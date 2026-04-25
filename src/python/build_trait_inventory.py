#!/usr/bin/env python3
"""Emit config/trait_inventory.yaml from SUMSTATS-UPGRADE.tsv + SHA manifests +
qc.json sidecars + LDSC h2/intercept parsed from rg_logs.

Per CONTEXT D-16 + REQ-TRAIT-INVENTORY. Schema follows
m1-RESEARCH.md Example 4 verbatim:

    {trait, ancestry, consortium, year, source_url, doi, build, phenotype_lock,
     harmonized_path, parquet_path, munged_path,
     n_total, n_cases, n_controls,
     sha256_raw, sha256_harmonized,
     ldsc_intercept, ldsc_h2,
     qc_report_path, qc_status,
     cohort_overlap_cohorts, mtag_overlap_correction_required,
     dua_required, license}

The output file is the M1 → M2 schema contract: every M2 plan
(MTAG, CPASSOC, HyPrColoc, coloc, SuSiE-RSS) reads this YAML to resolve
input paths, sample sizes, and overlap-correction metadata.

Plan reference: m1-04-qc-reports-inventory-manifest-PLAN.md Task 1 step (C).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from m1_trait_keys import TOKEN_MAP  # noqa: E402

# Reuse the already-tested parse_rg_log helper from Wave 3 reducer.
try:
    from reduce_ldsc_rg_matrix import parse_rg_log  # noqa: E402
except Exception:  # pragma: no cover — defensive
    parse_rg_log = None

ANCESTRY_MAP = {
    "EUR": "EUR", "AFR": "AFR", "EAS": "EAS", "SAS": "SAS",
    "HIS": "HIS", "TRANS": "TRANS", "MULTI": "MULTI",
}

# Wave 2b harmonizers emit short author-name consortium tokens (e.g. "Aragam")
# while .planning/amendments/SUMSTATS-UPGRADE.tsv uses formal consortium
# strings (e.g. "CARDIoGRAM-C4D-MVP" for the TRANS pooled meta and "BBJ" for
# the EAS subset). The harmonizer-emitted token is what shows up in
# trait_keys.txt + on-disk filenames, so the inventory must use the same
# alias to match dim-j ⊆ invariant.
#
# Source: .planning/phases/m1-sumstats-upgrade-and-harmonization/m1-02b-...
#         -SUMMARY.md "Aragam D-03 branch verdict" + Wave-3 trait_keys.txt.
CONSORTIUM_ALIAS: dict[tuple[str, str, str], str] = {
    # (trait_token, ancestry, source_consortium_in_tsv) -> harmonizer-emitted
    ("cad", "TRANS", "CARDIoGRAM-C4D-MVP"): "Aragam",
    ("cad", "EAS",   "BBJ"):                "Aragam",
    ("cad", "EUR",   "CARDIoGRAM-C4D-UKB"): "Aragam",
}

# Top-level YAML version + build target are constants for M1.
INVENTORY_VERSION = "2026-04-M1"
INVENTORY_BUILD_TARGET = "GRCh37"


def _year_from_citation(s: str) -> int:
    """Robust 4-digit year extraction (matches m1_trait_keys._year_from_citation)."""
    m = re.search(r"(\d{4})", str(s))
    if not m:
        raise ValueError(f"No 4-digit year in citation: {s!r}")
    return int(m.group(1))


def _build_key(row: pd.Series) -> str | None:
    """Build the D-16 key ``<trait>.<ancestry>.<consortium>.<year>`` for a row.

    Returns ``None`` if the trait label is not in TOKEN_MAP (DEFERRED rows
    such as MAGIC TRANS hyphenated tokens are silently skipped).
    """
    trait_label = str(row["trait"])
    if trait_label not in TOKEN_MAP:
        return None
    token = TOKEN_MAP[trait_label]
    anc = str(row["ancestry"])
    if anc not in ANCESTRY_MAP:
        return None
    anc_norm = ANCESTRY_MAP[anc]
    consortium_raw = str(row["source_consortium"])
    consortium = CONSORTIUM_ALIAS.get((token, anc_norm, consortium_raw),
                                      consortium_raw)
    year = _year_from_citation(row["citation_first_author_year"])
    return f"{token}.{anc_norm}.{consortium}.{year}"


def _read_qc_status(qc_json: Path) -> str:
    """Return the qc_status string from a sidecar, or 'MISSING' / 'ERROR'."""
    if not qc_json.exists():
        return "MISSING"
    try:
        d = json.loads(qc_json.read_text())
        return d.get("qc_status", "UNKNOWN")
    except Exception:  # pragma: no cover — defensive
        return "ERROR"


def _split_cohorts(s) -> list[str]:
    if pd.isna(s):
        return []
    return [x.strip() for x in str(s).split(",") if x.strip()]


def _safe_int(x):
    if pd.isna(x):
        return None
    try:
        return int(x)
    except Exception:
        return None


def _resolve_sha(manifest: pd.DataFrame, needle: str) -> str | None:
    """Find a SHA-256 row whose relative_path contains ``needle`` substring.

    Returns the first match's sha256 (a 64-hex string) or None.
    """
    if not needle or not isinstance(needle, str):
        return None
    hits = manifest[manifest["relative_path"].str.contains(re.escape(needle),
                                                            regex=True, na=False)]
    if len(hits) == 0:
        return None
    return str(hits.iloc[0]["sha256"])


def _fill_ldsc_from_rg_logs(inv: dict, rg_log_dir: Path) -> dict:
    """Populate ldsc_intercept (h2_int) + ldsc_h2 (h2_obs) from focal_*.log.

    For each pair record the focal trait gets h2_obs + h2_int + the off-diagonal
    gcov_int (which the Wave 3 plan uses as the diagonal-of-the-symmetric-matrix
    proxy when the focal log has only itself in the Heritability sub-section).
    """
    if parse_rg_log is None or not rg_log_dir.exists():
        return inv
    for log_path in sorted(rg_log_dir.glob("focal_*.log")):
        df = parse_rg_log(log_path)
        if df.empty:
            continue
        for _, r in df.iterrows():
            for col in ("p1", "p2"):
                key = Path(str(r[col])).name.replace(".sumstats.gz", "")
                if key in inv["traits"]:
                    if inv["traits"][key].get("ldsc_intercept") is None:
                        # gcov_int is the cross-trait intercept; for the focal
                        # itself, h2_int is the per-trait LDSC intercept.
                        h2_int = r.get("h2_int")
                        if h2_int is not None and pd.notna(h2_int):
                            inv["traits"][key]["ldsc_intercept"] = float(h2_int)
                    if inv["traits"][key].get("ldsc_h2") is None:
                        h2_obs = r.get("h2_obs")
                        if h2_obs is not None and pd.notna(h2_obs):
                            inv["traits"][key]["ldsc_h2"] = float(h2_obs)
    return inv


def build_inventory(
    tsv_path: Path,
    raw_manifest: Path,
    harm_manifest: Path,
    qc_log_dir: Path,
    rg_log_dir: Path,
) -> dict:
    """Build the inventory dict from sources.

    Returns a dict with keys ``{version, build_target, traits}`` where ``traits``
    is a dict keyed by D-16 key (``<trait>.<ancestry>.<consortium>.<year>``).
    """
    tsv = pd.read_csv(tsv_path, sep="\t", dtype=str)
    raw_sha = pd.read_csv(raw_manifest, sep="\t") if raw_manifest.exists() else \
        pd.DataFrame(columns=["relative_path", "sha256", "bytes"])
    harm_sha = pd.read_csv(harm_manifest, sep="\t") if harm_manifest.exists() else \
        pd.DataFrame(columns=["relative_path", "sha256", "bytes"])

    inv: dict = {
        "version": INVENTORY_VERSION,
        "build_target": INVENTORY_BUILD_TARGET,
        "traits": {},
    }

    for _, row in tsv.iterrows():
        try:
            key = _build_key(row)
        except (KeyError, ValueError):
            continue
        if key is None:
            continue
        token = TOKEN_MAP[str(row["trait"])]
        anc = ANCESTRY_MAP[str(row["ancestry"])]
        # The key already has the alias-resolved consortium baked in; pull it
        # out so the entry's `consortium` field stays consistent with the key.
        consortium_resolved = key.split(".")[2]
        # File path conventions per D-16.
        harm_path = f"data/processed/sumstats_harmonized/{key}.GRCh37.tsv.bgz"
        parq_path = f"data/processed/sumstats_harmonized_parquet/{key}.GRCh37.parquet"
        mun_path  = f"data/processed/ldsc_overlap/munged/{key}.sumstats.gz"
        qc_html   = f"data/processed/sumstats_harmonized/qc_log/{key}.qc.html"
        qc_json   = qc_log_dir / f"{key}.qc.json"

        sha_raw = _resolve_sha(raw_sha, str(row.get("expected_filename") or ""))
        sha_harm = _resolve_sha(harm_sha, f"{key}.GRCh37.tsv.bgz")

        dua_required = str(row.get("dua_required") or "").strip().lower() == "yes"
        license_label = "academic_dua" if dua_required else "public_academic"

        entry = {
            "trait": token,
            "ancestry": anc,
            "consortium": consortium_resolved,
            "year": _year_from_citation(row["citation_first_author_year"]),
            "source_url": str(row.get("download_url") or ""),
            "doi": str(row.get("doi") or ""),
            "build": 37,
            "phenotype_lock": str(row.get("phenotype_definition") or ""),
            "harmonized_path": harm_path,
            "parquet_path": parq_path,
            "munged_path": mun_path,
            "n_total": _safe_int(row.get("n_total")),
            "n_cases": _safe_int(row.get("n_cases")),
            "n_controls": _safe_int(row.get("n_controls")),
            "sha256_raw": sha_raw,
            "sha256_harmonized": sha_harm,
            "ldsc_intercept": None,
            "ldsc_h2": None,
            "qc_report_path": qc_html,
            "qc_status": _read_qc_status(qc_json),
            "cohort_overlap_cohorts": _split_cohorts(row.get("sample_source_cohort")),
            "mtag_overlap_correction_required": str(
                row.get("mtag_overlap_correction_required") or ""
            ).strip().lower() == "yes",
            "dua_required": dua_required,
            "license": license_label,
            "status": str(row.get("status") or ""),
        }
        inv["traits"][key] = entry

    _fill_ldsc_from_rg_logs(inv, rg_log_dir)
    return inv


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tsv", type=Path,
                    default=Path(".planning/amendments/SUMSTATS-UPGRADE.tsv"))
    ap.add_argument("--raw-manifest", type=Path,
                    default=Path("data/raw/sumstats_v2/sha256_manifest.tsv"))
    ap.add_argument("--harm-manifest", type=Path,
                    default=Path("data/processed/sumstats_harmonized/sha256_manifest.tsv"))
    ap.add_argument("--qc-log-dir", type=Path,
                    default=Path("data/processed/sumstats_harmonized/qc_log"))
    ap.add_argument("--rg-log-dir", type=Path,
                    default=Path("data/processed/ldsc_overlap/rg_logs"))
    ap.add_argument("--output", type=Path,
                    default=Path("config/trait_inventory.yaml"))
    args = ap.parse_args()
    inv = build_inventory(
        args.tsv, args.raw_manifest, args.harm_manifest,
        args.qc_log_dir, args.rg_log_dir,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(inv, sort_keys=False))
    print(f"Wrote {len(inv['traits'])} trait cells to {args.output}",
          file=sys.stderr)


if __name__ == "__main__":
    _main()
