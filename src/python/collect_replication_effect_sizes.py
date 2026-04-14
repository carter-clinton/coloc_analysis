"""Plan 09-04 Task 2 Step 1b — per-cohort effect-size collector.

Produces the `results/replication/effect_size_raw/{cohort}.tsv` table that
compute_per_cohort_effect_size_test.py consumes. Each row corresponds to
one manifest signal_id routed to this cohort; effect sizes are pulled from
the Wave-2 harmonized sumstats at the lead SNP (credible-set) or, for Tier
A/B triples, at the region-lead lookup fallback.

I-5 revision intent: the raw effect-size table is not implicit — it has a
concrete producer so the DAG upstream of compute_per_cohort_effect_size_test
is complete.

Output schema (8 columns):
  signal_id, cohort, beta_replication, se_replication, p_replication,
  eaf_replication, N, cohort_ancestry

CLI:
  python collect_replication_effect_sizes.py \
    --manifest data/processed/replication/manifest.tsv \
    --cohort <cohort_name> \
    --out results/replication/effect_size_raw/<cohort>.tsv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]


def _empty_row(signal_id: str, cohort: str, cohort_ancestry: str = "") -> dict:
    return {
        "signal_id": signal_id,
        "cohort": cohort,
        "cohort_ancestry": cohort_ancestry,
        "beta_replication": None,
        "se_replication": None,
        "p_replication": None,
        "eaf_replication": None,
        "N": None,
    }


def _read_sumstats(path: Path) -> pd.DataFrame | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    try:
        compression = "gzip" if str(path).endswith(".gz") else None
        return pd.read_csv(path, sep="\t", compression=compression)
    except (pd.errors.EmptyDataError, OSError):
        return None


def _match_lead(ss: pd.DataFrame, row: pd.Series) -> pd.DataFrame:
    """Match a manifest row to the sumstats, preferring rsid then chr:bp."""
    lead = row.get("lead_snp") or row.get("SNP")
    if lead and "SNP" in ss.columns:
        m = ss[ss["SNP"] == lead]
        if not m.empty:
            return m

    # Fallback: parse region "chr:start-end" and take min-p SNP in range
    region = row.get("region")
    if region and "CHR" in ss.columns and "BP" in ss.columns and "P" in ss.columns:
        try:
            chr_str, rng = str(region).split(":", 1)
            start_str, end_str = rng.split("-", 1)
            chrom = chr_str.lstrip("chr")
            start = int(start_str)
            end = int(end_str)
            in_region = ss[
                (ss["CHR"].astype(str) == str(chrom))
                & (ss["BP"].astype(int) >= start)
                & (ss["BP"].astype(int) <= end)
            ]
            if not in_region.empty:
                return in_region.nsmallest(1, "P")
        except (ValueError, KeyError):
            pass

    return ss.iloc[0:0]


def extract_per_signal(manifest_df: pd.DataFrame, cohort: str) -> pd.DataFrame:
    """Collect one row per manifest signal routed to this cohort."""
    rows: list[dict] = []
    cohort_rows = manifest_df[manifest_df["cohort"] == cohort]
    for _, r in cohort_rows.iterrows():
        signal_id = r["signal_id"]
        cohort_anc = r.get("cohort_ancestry", "")
        path = Path(r["replication_sumstats_path"])
        ss = _read_sumstats(path)
        if ss is None:
            rows.append(_empty_row(signal_id, cohort, cohort_anc))
            continue
        match = _match_lead(ss, r)
        if match.empty:
            rows.append(_empty_row(signal_id, cohort, cohort_anc))
            continue
        m = match.iloc[0]
        rows.append({
            "signal_id": signal_id,
            "cohort": cohort,
            "cohort_ancestry": cohort_anc,
            "beta_replication": float(m["BETA"]) if pd.notna(m.get("BETA")) else None,
            "se_replication": float(m["SE"]) if pd.notna(m.get("SE")) else None,
            "p_replication": float(m["P"]) if pd.notna(m.get("P")) else None,
            "eaf_replication": float(m["EAF"]) if pd.notna(m.get("EAF")) else None,
            "N": int(m["N"]) if pd.notna(m.get("N")) else None,
        })
    return pd.DataFrame(rows)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--manifest", required=True,
                   help="data/processed/replication/manifest.tsv")
    p.add_argument("--cohort", required=True)
    p.add_argument("--out", required=True)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    a = _parse_args(argv)
    manifest_path = Path(a.manifest)
    out_path = Path(a.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not manifest_path.exists() or manifest_path.stat().st_size == 0:
        # Emit an empty table with the expected header so Snakemake sees the target
        empty = pd.DataFrame(columns=[
            "signal_id", "cohort", "cohort_ancestry",
            "beta_replication", "se_replication", "p_replication",
            "eaf_replication", "N",
        ])
        empty.to_csv(out_path, sep="\t", index=False)
        return 0

    manifest = pd.read_csv(manifest_path, sep="\t")
    df = extract_per_signal(manifest, a.cohort)
    df.to_csv(out_path, sep="\t", index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
