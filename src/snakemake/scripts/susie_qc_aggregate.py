#!/usr/bin/env python3
"""Aggregate run_finemap JSON outputs into a single TSV for the QC dashboard.

Reads all *.json under ``--input-dir`` (recursively), extracts D1/D2/D3
diagnostic fields + ld_source + L_saturated + min_abs_corr_sweep summary,
and writes a flat TSV keyed by (trait x ancestry x region_id).

Phase 1 REQ-2 acceptance #5 -- Per-locus fine-mapping QC report.
T-1-04 mitigation: surface ld_source field so
``ukbb_ld_tiled_block_diagonal`` is visible in the dashboard.

Task 1-05-04 extension: emits a standalone REQ-2 supplementary
sensitivity-sweep table ``sweep_complex_regions.tsv`` with two row-groups
(``known_complex``, ``data_flagged``). An ``--aggregated-only`` mode is
provided so the Snakemake rule can reuse the already-materialized
``qc_aggregated.tsv`` without re-scanning all JSON outputs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Schema / constants
# ---------------------------------------------------------------------------

AGGREGATE_COLUMNS = [
    "region_id",
    "trait",
    "ancestry",
    "status",
    "convergence_status",
    "L_used",
    "L_saturated",
    "ld_source",
    "n_variants",
    # D1 -- z-score sanity
    "ks_pvalue",
    "max_abs_z",
    "lambda_gc",
    # D2 -- convergence
    "converged",
    "niter",
    "elbo_final",
    # D3 -- LD quality (kriging-style outliers)
    "kriging_n_outliers",
    "kriging_max_logLR",
    "kriging_lambda",
    # D4 -- min_abs_corr sensitivity sweep
    "n_CS_macor_0.1",
    "n_CS_macor_0.5",
    "n_CS_macor_0.9",
    "total_PIP_macor_0.1",
    "total_PIP_macor_0.5",
    "total_PIP_macor_0.9",
    "max_PIP",
    "is_complex_region",
]

SWEEP_COLUMNS = [
    "row_group",
    "region_id",
    "trait",
    "ancestry",
    "n_CS_macor_0.1",
    "n_CS_macor_0.5",
    "n_CS_macor_0.9",
    "total_PIP_macor_0.1",
    "total_PIP_macor_0.5",
    "total_PIP_macor_0.9",
    "L_saturated",
    "max_PIP",
    "ld_source",
]

# Region IDs pre-specified as complex in config/susie_policy.yaml
# §complex_regions.pre_specified. Keep in sync with that file.
KNOWN_COMPLEX = {"HLA_6p21", "APOE_19q13", "9p21_CDKN2A", "SLC2A9_urate"}


# ---------------------------------------------------------------------------
# JSON -> row flattening
# ---------------------------------------------------------------------------


def _pick_ld_source(data: dict) -> str:
    """Accept either ``ld_source`` (preferred) or ``ld_matrix`` (legacy).

    run_susie_rss.R currently writes the loader source under the key
    ``ld_matrix`` (see line 490 of that script). Plan 01-05 and downstream
    tests query ``ld_source``. Accept both so the aggregator remains robust
    to either emission path.
    """
    val = data.get("ld_source")
    if val:
        return str(val)
    val = data.get("ld_matrix")
    if val:
        return str(val)
    return ""


def _sweep_rows(data: dict) -> dict:
    raw = data.get("min_abs_corr_sweep") or []
    indexed: dict = {}
    for entry in raw:
        try:
            key = float(entry["min_abs_corr"])
        except (KeyError, TypeError, ValueError):
            continue
        indexed[key] = entry
    return indexed


def _cs_pip_sum_total(entry: dict) -> float:
    """Return sum of cs_pip_sum for a sweep entry, or 0.0 if unavailable."""
    if not entry:
        return 0.0
    vals = entry.get("cs_pip_sum") or []
    try:
        return float(sum(float(v) for v in vals))
    except (TypeError, ValueError):
        return 0.0


def _max_pip(data: dict) -> float | None:
    """Return the max PIP across all credible sets, or None if unavailable."""
    cs_list = data.get("credible_sets")
    best: float | None = None
    if isinstance(cs_list, dict):
        cs_iter = cs_list.values()
    elif isinstance(cs_list, list):
        cs_iter = cs_list
    else:
        cs_iter = []
    for cs in cs_iter:
        if isinstance(cs, dict):
            pips = cs.get("pip") or []
        else:
            pips = []
        for p in pips:
            try:
                pf = float(p)
            except (TypeError, ValueError):
                continue
            if best is None or pf > best:
                best = pf
    # Fallback: top-level `pip` array (run_susie_rss.R emits fit$pip[fit$pip > 0])
    if best is None:
        top = data.get("pip")
        if isinstance(top, list):
            for p in top:
                try:
                    pf = float(p)
                except (TypeError, ValueError):
                    continue
                if best is None or pf > best:
                    best = pf
    return best


def flatten_one(json_path: Path) -> dict:
    data = json.loads(Path(json_path).read_text())
    d1 = data.get("d1_zscore_sanity", {}) or {}
    d2 = data.get("d2_convergence", {}) or {}
    d3 = data.get("d3_ld_quality", {}) or {}
    sweep = _sweep_rows(data)

    def sweep_n(level: float) -> int:
        entry = sweep.get(level) or {}
        try:
            return int(entry.get("n_CS", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def sweep_total_pip(level: float) -> float:
        return _cs_pip_sum_total(sweep.get(level) or {})

    region_id = data.get("region_id", "") or ""
    row = {
        "region_id": region_id,
        "trait": data.get("trait", ""),
        "ancestry": data.get("ancestry", ""),
        "status": data.get("status", ""),
        "convergence_status": data.get("convergence_status", ""),
        "L_used": data.get("L_used", None),
        "L_saturated": bool(data.get("L_saturated", False)),
        "ld_source": _pick_ld_source(data),
        "n_variants": data.get("n_variants", None),
        # D1
        "ks_pvalue": d1.get("ks_pvalue", None),
        "max_abs_z": d1.get("max_abs_z", None),
        "lambda_gc": d1.get("lambda_gc", None),
        # D2
        "converged": d2.get("converged", None),
        "niter": d2.get("niter", None),
        "elbo_final": d2.get("elbo_final", None),
        # D3
        "kriging_n_outliers": d3.get("n_outliers", None),
        "kriging_max_logLR": d3.get("max_logLR", None),
        "kriging_lambda": d3.get("lambda", None),
        # D4 -- counts at 3 min_abs_corr levels
        "n_CS_macor_0.1": sweep_n(0.1),
        "n_CS_macor_0.5": sweep_n(0.5),
        "n_CS_macor_0.9": sweep_n(0.9),
        "total_PIP_macor_0.1": sweep_total_pip(0.1),
        "total_PIP_macor_0.5": sweep_total_pip(0.5),
        "total_PIP_macor_0.9": sweep_total_pip(0.9),
        "max_PIP": _max_pip(data),
        "is_complex_region": region_id in KNOWN_COMPLEX,
    }
    return row


def aggregate_json_dir(input_dir: Path) -> pd.DataFrame:
    rows: list[dict] = []
    for jf in sorted(input_dir.rglob("*.json")):
        if jf.suffix != ".json":
            continue
        try:
            rows.append(flatten_one(jf))
        except Exception as e:  # noqa: BLE001 -- intentional fail-open on malformed
            print(f"[aggregate] WARN skipping {jf}: {e}")
    if not rows:
        return pd.DataFrame(columns=AGGREGATE_COLUMNS)
    df = pd.DataFrame(rows)
    # Ensure stable column ordering and schema completeness
    for col in AGGREGATE_COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df[AGGREGATE_COLUMNS]


# ---------------------------------------------------------------------------
# Sweep-complex-regions table (Task 1-05-04)
# ---------------------------------------------------------------------------


def _policy_trait_by_region(policy: dict) -> dict:
    """Map region_id -> set(trait ids).

    susie_policy.yaml §complex_regions.pre_specified does NOT currently pin
    per-region trait lists. If no trait_list is present, treat the region as
    applicable to all traits (i.e. return an empty set + a sentinel flag that
    the caller interprets as 'match any trait').
    """
    out: dict = {}
    for entry in (policy.get("complex_regions", {}) or {}).get("pre_specified", []) or []:
        rid = entry.get("region_id")
        if not rid:
            continue
        traits = entry.get("trait_list")
        if traits is None:
            # sentinel: None means "match any trait in the aggregated data"
            out[rid] = None
        else:
            out[rid] = set(traits)
    return out


def build_sweep_table(df: pd.DataFrame, policy: dict) -> pd.DataFrame:
    """Build the REQ-2 supplementary sensitivity table.

    Row groups:
      * ``known_complex`` -- rows whose region_id is in KNOWN_COMPLEX AND whose
        trait intersects the policy's pre_specified trait_list (if any).
      * ``data_flagged`` -- all remaining rows where L_saturated is True OR
        n_CS_macor_0.5 >= 3.
    """
    if df.empty:
        return pd.DataFrame(columns=SWEEP_COLUMNS)

    trait_by_region = _policy_trait_by_region(policy)

    def _is_known(row) -> bool:
        rid = row["region_id"]
        if rid not in KNOWN_COMPLEX:
            return False
        allowed = trait_by_region.get(rid, None)
        if allowed is None:
            # No explicit trait pin in policy -> match any trait
            return True
        return row["trait"] in allowed

    known_mask = df.apply(_is_known, axis=1)
    l_sat_mask = df["L_saturated"].fillna(False).astype(bool)
    # n_CS_macor_0.5 may be missing for older JSONs; coerce to 0
    n_cs_05 = pd.to_numeric(df["n_CS_macor_0.5"], errors="coerce").fillna(0)
    flagged_mask = (~known_mask) & (l_sat_mask | (n_cs_05 >= 3))

    known = df[known_mask].copy()
    known["row_group"] = "known_complex"
    flagged = df[flagged_mask].copy()
    flagged["row_group"] = "data_flagged"

    sweep_df = pd.concat([known, flagged], ignore_index=True)
    # Ensure all sweep columns exist before indexing
    for col in SWEEP_COLUMNS:
        if col not in sweep_df.columns:
            sweep_df[col] = None
    sweep_df = sweep_df[SWEEP_COLUMNS].sort_values(
        ["row_group", "region_id", "trait", "ancestry"],
        kind="stable",
    ).reset_index(drop=True)
    return sweep_df


def write_sweep_tsv(sweep_df: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header_prefix = ""
    known_empty = sweep_df.empty or "known_complex" not in set(sweep_df["row_group"])
    flagged_empty = sweep_df.empty or "data_flagged" not in set(sweep_df["row_group"])
    if sweep_df.empty:
        header_prefix = "## row_group_empty: both groups empty on current data\n"
    elif known_empty:
        header_prefix = "## row_group_empty: known_complex group empty on current data\n"
    elif flagged_empty:
        header_prefix = "## row_group_empty: data_flagged group empty on current data\n"
    with open(out_path, "w") as f:
        if header_prefix:
            f.write(header_prefix)
        sweep_df.to_csv(f, sep="\t", index=False)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _load_policy(path: str | None) -> dict:
    if not path:
        return {}
    import yaml  # local import -- yaml is in envs/qc_dashboard.yml but not base

    with open(path) as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--input-dir",
        help="Directory to scan recursively for run_finemap *.json outputs "
        "(e.g. results/finemap/susie). Mutually exclusive with --aggregated-only.",
    )
    ap.add_argument(
        "--output",
        help="Output path for qc_aggregated.tsv (required unless --aggregated-only).",
    )
    ap.add_argument(
        "--aggregated-only",
        action="store_true",
        help="Skip JSON scanning; read an existing qc_aggregated.tsv from --input "
        "and only write the sweep_complex_regions.tsv sensitivity table.",
    )
    ap.add_argument(
        "--input",
        help="When --aggregated-only is set, the path to the existing aggregated TSV.",
    )
    ap.add_argument(
        "--policy",
        help="Path to config/susie_policy.yaml (for sweep_complex_regions.tsv trait lists).",
    )
    ap.add_argument(
        "--sweep-out",
        help="Output path for sweep_complex_regions.tsv. When set, the sweep table "
        "is emitted in addition to (or instead of) qc_aggregated.tsv.",
    )
    args = ap.parse_args()

    if args.aggregated_only:
        if not args.input:
            ap.error("--aggregated-only requires --input pointing at qc_aggregated.tsv")
        df = pd.read_csv(args.input, sep="\t")
        # Normalize schema for downstream sweep-table logic
        for col in AGGREGATE_COLUMNS:
            if col not in df.columns:
                df[col] = None
        if args.output:
            # Rewrite normalized aggregated TSV if requested
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            df[AGGREGATE_COLUMNS].to_csv(args.output, sep="\t", index=False)
    else:
        if not args.input_dir or not args.output:
            ap.error("--input-dir and --output are required (or use --aggregated-only)")
        input_dir = Path(args.input_dir)
        df = aggregate_json_dir(input_dir)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.output, sep="\t", index=False)
        print(f"[aggregate] wrote {len(df)} rows to {args.output}")

    if args.sweep_out:
        policy = _load_policy(args.policy)
        sweep_df = build_sweep_table(df, policy)
        write_sweep_tsv(sweep_df, Path(args.sweep_out))
        print(
            f"[aggregate] wrote {len(sweep_df)} sweep rows to {args.sweep_out} "
            f"(groups: {sorted(set(sweep_df['row_group'])) if not sweep_df.empty else []})"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
