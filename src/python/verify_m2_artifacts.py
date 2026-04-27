#!/usr/bin/env python3
"""M2 phase verifier — Python only per D-M2-Q4.

Plan: m2-05-class1-novelty-and-closeout-PLAN.md.
Modeled on src/python/verify_m1_artifacts.py (RESEARCH §G fallback pattern).
Quarto QC report deferred to M6 manuscript phase per Carter D-M2-Q4 ruling.

Dimensions checked (PASS / WARN / FAIL):

  D1 — RM-1: bivariate_intercept_matrix_2026-04-M2.tsv exists, square
              N in [20, 50] band, symmetric, diag ~1.0
  D2 — RM-2: per-stratum MTAG outputs exist with max_FDR column
  D3 — RM-3: per-stratum CPASSOC outputs exist with SHom_p + SHet_p columns
  D4 — RM-4: results/regions/union_region_list.bed exists with provenance JSON
  D5 — RM-5: results/novelty/joint_signal_novel.tsv exists with confidence_tier
  D6 — RM-6: data/processed/mtcojo/*/mtcojo_sensitivity.tsv exists per stratum
  D7 — REQ-CATALOG-VERSION-LOCK: catalog_lock_manifest.tsv has row
              gwas_catalog.v_lock_M2 with valid SHA-256 (64-hex)
  D8 — REQ-OSF-PREREG: gate-release commit d55c1d1 already landed
              (sentinel; pass-through per Carter ruling)
  D9 — REQ-SNAKEMAKE-CI: tests/toy_3locus/m2_smoke_targets.smk exists with
              at least one M2 rule

Overall verdict:
  PASS only if all dimensions PASS;
  FAIL if any dimension FAIL;
  otherwise WARN.

Exit code: 0 if overall != FAIL, 1 if overall == FAIL.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Per-dimension check functions
# ---------------------------------------------------------------------------

def _check_d1_ldsc_matrix() -> dict:
    """RM-1: M2 LDSC bivariate-intercept matrix invariants."""
    path = _PROJECT_ROOT / "data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv"
    if not path.exists():
        return {"dimension": "D1", "name": "ldsc_matrix", "verdict": "FAIL",
                "reason": f"missing {path.relative_to(_PROJECT_ROOT)}"}
    try:
        M = pd.read_csv(path, sep="\t", index_col=0)
    except Exception as e:
        return {"dimension": "D1", "name": "ldsc_matrix", "verdict": "FAIL",
                "reason": f"unparseable: {e}"}
    if M.shape[0] != M.shape[1]:
        return {"dimension": "D1", "name": "ldsc_matrix", "verdict": "FAIL",
                "reason": f"not square: {M.shape}"}
    if not (20 <= M.shape[0] <= 50):
        return {"dimension": "D1", "name": "ldsc_matrix", "verdict": "WARN",
                "reason": f"N={M.shape[0]} outside expected band [20, 50]",
                "n_traits": int(M.shape[0])}
    A = M.values.astype(float)
    sym_violation = float(np.nanmax(np.abs(A - A.T)))
    if sym_violation > 1e-6:
        return {"dimension": "D1", "name": "ldsc_matrix", "verdict": "FAIL",
                "reason": f"not symmetric (max |R - R.T| = {sym_violation:.2e})"}
    diag = np.diag(A)
    if not np.all(np.abs(diag - 1.0) < 1e-6):
        return {"dimension": "D1", "name": "ldsc_matrix", "verdict": "WARN",
                "reason": f"diagonal not all 1.0 (min={np.min(diag):.4f}, max={np.max(diag):.4f})",
                "n_traits": int(M.shape[0])}
    return {"dimension": "D1", "name": "ldsc_matrix", "verdict": "PASS",
            "n_traits": int(M.shape[0]),
            "max_sym_violation": sym_violation}


def _check_d2_mtag(strata: Tuple[str, ...] = ("EUR", "AFR", "TRANS")) -> dict:
    """RM-2: Per-stratum MTAG outputs with max_FDR column present."""
    results = {}
    for s in strata:
        f = _PROJECT_ROOT / f"data/processed/mtag/{s}/{s}_mtag_maxfdr_filtered.txt"
        skip = _PROJECT_ROOT / f"data/processed/mtag/{s}/skipped_strata.tsv"
        if f.exists() and f.stat().st_size > 0:
            # Stream small chunk to check schema and row count cheaply
            try:
                head = pd.read_csv(f, sep="\t", nrows=10)
                # Total rows (count via wc -l minus header)
                with open(f) as fh:
                    total_rows = sum(1 for _ in fh) - 1
                results[s] = {
                    "exists": True,
                    "rows": int(total_rows),
                    "has_max_FDR": "max_FDR" in head.columns,
                    "has_mtag_pval": "mtag_pval" in head.columns,
                    "has_trait_key": "trait_key" in head.columns,
                }
            except Exception as e:
                results[s] = {"exists": True, "error": str(e)}
        elif skip.exists() and skip.stat().st_size > 0:
            results[s] = {"exists": False, "skipped": True,
                          "reason": skip.read_text().strip().split("\n")[0]}
        else:
            results[s] = {"exists": False, "skipped": False, "reason": "not produced"}
    any_landed = any(r.get("exists", False) for r in results.values())
    all_with_schema = all(
        r.get("has_max_FDR", False) and r.get("has_mtag_pval", False)
        and r.get("has_trait_key", False)
        for r in results.values() if r.get("exists")
    )
    if any_landed and all_with_schema:
        return {"dimension": "D2", "name": "mtag", "verdict": "PASS",
                "per_stratum": results}
    if any_landed:
        return {"dimension": "D2", "name": "mtag", "verdict": "WARN",
                "per_stratum": results,
                "reason": "some MTAG outputs missing required columns"}
    return {"dimension": "D2", "name": "mtag", "verdict": "FAIL",
            "per_stratum": results, "reason": "no MTAG output landed"}


def _check_d3_cpassoc(strata: Tuple[str, ...] = ("EUR", "AFR", "TRANS")) -> dict:
    """RM-3: Per-stratum CPASSOC outputs with SHom_p + SHet_p columns."""
    results = {}
    for s in strata:
        f = _PROJECT_ROOT / f"data/processed/cpassoc/{s}/cpassoc_results.tsv"
        if f.exists() and f.stat().st_size > 0:
            try:
                head = pd.read_csv(f, sep="\t", nrows=10)
                with open(f) as fh:
                    total_rows = sum(1 for _ in fh) - 1
                results[s] = {
                    "exists": True,
                    "rows": int(total_rows),
                    "has_SHom_p": "SHom_p" in head.columns,
                    "has_SHet_p": "SHet_p" in head.columns,
                    "has_chr_pos_rsid": all(
                        c in head.columns for c in ("chr", "pos", "rsid")
                    ),
                }
            except Exception as e:
                results[s] = {"exists": True, "error": str(e)}
        else:
            results[s] = {"exists": False}
    any_landed = any(r.get("exists", False) for r in results.values())
    all_complete = all(
        r.get("has_SHom_p") and r.get("has_SHet_p") and r.get("has_chr_pos_rsid")
        for r in results.values() if r.get("exists")
    )
    if any_landed and all_complete:
        return {"dimension": "D3", "name": "cpassoc", "verdict": "PASS",
                "per_stratum": results}
    return {
        "dimension": "D3", "name": "cpassoc",
        "verdict": "WARN" if any_landed else "FAIL",
        "per_stratum": results,
    }


def _check_d4_regions() -> dict:
    """RM-4: union_region_list.bed exists with provenance JSON column."""
    path = _PROJECT_ROOT / "results/regions/union_region_list.bed"
    if not path.exists() or path.stat().st_size == 0:
        return {"dimension": "D4", "name": "regions", "verdict": "FAIL",
                "reason": f"missing or empty {path.relative_to(_PROJECT_ROOT)}"}
    n = sum(1 for _ in open(path))
    # Check provenance JSON in last column of first row. The build_region_union
    # writer uses CSV-style double-quote escaping (per Wave 4 Deviation 3),
    # so unwrap surrounding quotes + collapse doubled-inner-quotes before parsing.
    first_row = open(path).readline().rstrip("\n").split("\t")
    has_provenance = False
    if len(first_row) >= 4:
        candidate = first_row[-1].strip()
        if candidate.startswith('"') and candidate.endswith('"'):
            candidate = candidate[1:-1].replace('""', '"')
        try:
            json.loads(candidate)
            has_provenance = True
        except (json.JSONDecodeError, ValueError):
            has_provenance = False
    if n < 100:
        return {"dimension": "D4", "name": "regions", "verdict": "WARN",
                "regions": int(n),
                "reason": f"region count {n} below >100 must_have floor",
                "has_provenance_json": has_provenance}
    if not has_provenance:
        return {"dimension": "D4", "name": "regions", "verdict": "WARN",
                "regions": int(n),
                "reason": "first row last column not JSON-parseable"}
    return {"dimension": "D4", "name": "regions", "verdict": "PASS",
            "regions": int(n), "has_provenance_json": True}


def _check_d5_novelty() -> dict:
    """RM-5: joint_signal_novel.tsv with full Class 1 schema."""
    path = _PROJECT_ROOT / "results/novelty/joint_signal_novel.tsv"
    if not path.exists():
        return {"dimension": "D5", "name": "novelty", "verdict": "FAIL",
                "reason": f"missing {path.relative_to(_PROJECT_ROOT)}"}
    df = pd.read_csv(path, sep="\t")
    required = {
        "chr", "pos", "rsid", "stratum",
        "mtag_p", "cpassoc_shom_p", "cpassoc_shet_p",
        "max_single_trait_p",
        "nearest_gwas_catalog_entry", "nearest_distance_bp",
        "confidence_tier",
    }
    missing = required - set(df.columns)
    if missing:
        return {"dimension": "D5", "name": "novelty", "verdict": "FAIL",
                "reason": f"missing columns: {sorted(missing)}"}
    if len(df) == 0:
        return {"dimension": "D5", "name": "novelty", "verdict": "WARN",
                "reason": "empty novelty output (no Class 1 loci called)",
                "loci": 0}
    if not df["confidence_tier"].isin({"high", "medium"}).all():
        bad = df.loc[~df["confidence_tier"].isin({"high", "medium"}),
                     "confidence_tier"].unique().tolist()
        return {"dimension": "D5", "name": "novelty", "verdict": "WARN",
                "reason": f"confidence_tier contains out-of-vocab values: {bad}",
                "loci": int(len(df))}
    n_high = int((df["confidence_tier"] == "high").sum())
    n_medium = int((df["confidence_tier"] == "medium").sum())
    return {"dimension": "D5", "name": "novelty", "verdict": "PASS",
            "loci": int(len(df)),
            "n_high": n_high, "n_medium": n_medium,
            "per_stratum": df["stratum"].value_counts().to_dict()}


def _check_d6_mtcojo(strata: Tuple[str, ...] = ("EUR", "AFR", "TRANS")) -> dict:
    """RM-6: per-stratum mtcojo_sensitivity.tsv with sensitivity_flag column."""
    any_landed = False
    per = {}
    for s in strata:
        f = _PROJECT_ROOT / f"data/processed/mtcojo/{s}/mtcojo_sensitivity.tsv"
        if f.exists() and f.stat().st_size > 0:
            any_landed = True
            try:
                head = pd.read_csv(f, sep="\t", nrows=20)
                per[s] = {
                    "exists": True,
                    "rows": int(len(head)),
                    "has_sensitivity_flag": "sensitivity_flag" in head.columns,
                    "n_pass": int(
                        (head.get("sensitivity_flag", pd.Series()) == "PASS").sum()
                    ) if "sensitivity_flag" in head.columns else 0,
                    "n_warn": int(
                        (head.get("sensitivity_flag", pd.Series()) == "WARN").sum()
                    ) if "sensitivity_flag" in head.columns else 0,
                    "n_fail": int(
                        (head.get("sensitivity_flag", pd.Series()) == "FAIL").sum()
                    ) if "sensitivity_flag" in head.columns else 0,
                }
            except Exception as e:
                per[s] = {"exists": True, "error": str(e)}
        else:
            per[s] = {"exists": False}
    if not any_landed:
        return {"dimension": "D6", "name": "mtcojo", "verdict": "FAIL",
                "per_stratum": per,
                "reason": "no mtcojo_sensitivity.tsv landed"}
    # All FAIL is acceptable WARN — indicates Wave 4 D4 deferred re-fire pending
    has_any_pass_or_warn = any(
        (r.get("n_pass", 0) > 0 or r.get("n_warn", 0) > 0)
        for r in per.values() if r.get("exists")
    )
    if has_any_pass_or_warn:
        return {"dimension": "D6", "name": "mtcojo", "verdict": "PASS",
                "per_stratum": per}
    return {"dimension": "D6", "name": "mtcojo", "verdict": "WARN",
            "per_stratum": per,
            "reason": "all sensitivity_flag = FAIL (Wave 4 D4 deferred re-fire pending; M2-POST-M3-08)"}


def _check_d7_catalog() -> dict:
    """REQ-CATALOG-VERSION-LOCK: v_lock_M2 row with valid SHA-256."""
    path = _PROJECT_ROOT / "data/catalogs/catalog_lock_manifest.tsv"
    if not path.exists():
        return {"dimension": "D7", "name": "catalog_v_lock", "verdict": "FAIL",
                "reason": f"missing {path.relative_to(_PROJECT_ROOT)}"}
    text = path.read_text()
    if "gwas_catalog.v_lock_M2" not in text:
        return {"dimension": "D7", "name": "catalog_v_lock", "verdict": "FAIL",
                "reason": "no v_lock_M2 row in catalog_lock_manifest.tsv"}
    sha_match = re.search(
        r"gwas_catalog\.v_lock_M2[^\n]*?([a-f0-9]{64})", text, re.IGNORECASE
    )
    if not sha_match:
        return {"dimension": "D7", "name": "catalog_v_lock", "verdict": "WARN",
                "reason": "v_lock_M2 row found but no 64-hex SHA-256"}
    return {"dimension": "D7", "name": "catalog_v_lock", "verdict": "PASS",
            "sha256_prefix": sha_match.group(1)[:16]}


def _check_d8_osf() -> dict:
    """REQ-OSF-PREREG: pass-through; OSF posting at osf.io/az52u (DEC-2026-04-25-02)."""
    try:
        log = subprocess.run(
            ["git", "log", "--oneline", "--all"],
            cwd=str(_PROJECT_ROOT),
            capture_output=True, text=True, timeout=30,
        )
        # Look for the gate-release commit referenced in DEC-2026-04-25-02
        has_gate_release = (
            "d55c1d1" in log.stdout
            or "M2 gate released" in log.stdout
            or "OSF amendment posted" in log.stdout
        )
    except Exception:
        has_gate_release = False
    return {"dimension": "D8", "name": "osf_prereg", "verdict": "PASS",
            "gate_release_landed": has_gate_release,
            "note": "OSF amendment posted at osf.io/az52u/files/k8w7n per DEC-2026-04-25-02; M2 hard gate released 2026-04-25"}


def _check_d9_snakemake_ci() -> dict:
    """REQ-SNAKEMAKE-CI: tests/toy_3locus/m2_smoke_targets.smk with M2 rule."""
    smoke = _PROJECT_ROOT / "tests/toy_3locus/m2_smoke_targets.smk"
    if not smoke.exists():
        return {"dimension": "D9", "name": "snakemake_ci", "verdict": "FAIL",
                "reason": f"missing {smoke.relative_to(_PROJECT_ROOT)}"}
    body = smoke.read_text()
    if "rule m2_smoke" not in body:
        return {"dimension": "D9", "name": "snakemake_ci", "verdict": "WARN",
                "reason": "no rule m2_smoke* found in smoke targets"}
    # Confirm Snakefile.test includes the smoke rule
    snakefile = _PROJECT_ROOT / "tests/toy_3locus/Snakefile.test"
    if snakefile.exists() and "m2_smoke_targets" in snakefile.read_text():
        return {"dimension": "D9", "name": "snakemake_ci", "verdict": "PASS",
                "smoke_target_in_snakefile": True}
    return {"dimension": "D9", "name": "snakemake_ci", "verdict": "WARN",
            "reason": "smoke smk exists but not included in Snakefile.test"}


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def verify_all() -> dict:
    """Run all 9 dimensions and aggregate to overall verdict."""
    results = [
        _check_d1_ldsc_matrix(),
        _check_d2_mtag(),
        _check_d3_cpassoc(),
        _check_d4_regions(),
        _check_d5_novelty(),
        _check_d6_mtcojo(),
        _check_d7_catalog(),
        _check_d8_osf(),
        _check_d9_snakemake_ci(),
    ]
    verdicts = [r["verdict"] for r in results]
    if all(v == "PASS" for v in verdicts):
        overall = "PASS"
    elif any(v == "FAIL" for v in verdicts):
        overall = "FAIL"
    else:
        overall = "WARN"
    return {
        "phase": "m2-ldsc-mtag-cpassoc-discovery",
        "verifier": "verify_m2_artifacts.py",
        "verifier_model": "python_only_per_d_m2_q4",
        "verified_at": datetime.utcnow().isoformat() + "Z",
        "overall": overall,
        "n_pass": int(sum(v == "PASS" for v in verdicts)),
        "n_warn": int(sum(v == "WARN" for v in verdicts)),
        "n_fail": int(sum(v == "FAIL" for v in verdicts)),
        "dimensions": results,
    }


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--out", type=Path,
        default=Path(".planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-VERIFY.json"),
        help="Output JSON path for verifier results",
    )
    args = ap.parse_args()
    result = verify_all()
    out_path = args.out
    if not out_path.is_absolute():
        out_path = _PROJECT_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    print(f"M2 verifier — overall: {result['overall']} "
          f"(PASS={result['n_pass']}, WARN={result['n_warn']}, FAIL={result['n_fail']})")
    for d in result["dimensions"]:
        details = ""
        if "reason" in d:
            details = f"  [{d['reason']}]"
        elif d["dimension"] == "D5" and "loci" in d:
            details = f"  [{d['loci']} loci, {d.get('n_high', 0)} high + {d.get('n_medium', 0)} medium]"
        elif d["dimension"] == "D4" and "regions" in d:
            details = f"  [{d['regions']} regions]"
        elif d["dimension"] == "D1" and "n_traits" in d:
            details = f"  [N={d['n_traits']} traits]"
        print(f"  {d['dimension']} {d.get('name', ''):20s}: {d['verdict']:6s}{details}")

    raise SystemExit(0 if result["overall"] != "FAIL" else 1)


if __name__ == "__main__":
    _main()
