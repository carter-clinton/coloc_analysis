#!/usr/bin/env python3
"""
Annotate replication finemap comparisons with LD r2 between lead SNPs.
"""
from __future__ import annotations

import argparse
import math
import subprocess
from pathlib import Path

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replication",
        default="results/analysis/replication_finemap_compare.tsv",
    )
    parser.add_argument(
        "--finemap-summary",
        default="results/fine_mapping/finemap_summary_augmented.tsv",
    )
    parser.add_argument(
        "--ld-dir",
        default="data_processed/ld_reference",
    )
    parser.add_argument(
        "--r2-script",
        default="scripts/compute_ld_r2.R",
    )
    parser.add_argument(
        "--output",
        default="results/analysis/replication_finemap_compare_ld.tsv",
    )
    return parser.parse_args()


def compute_ld_r2(rscript: str, rds_path: str, snp_a: str, snp_b: str) -> float:
    if not isinstance(rds_path, str) or not rds_path:
        return math.nan
    if not isinstance(snp_a, str) or not snp_a:
        return math.nan
    if not isinstance(snp_b, str) or not snp_b:
        return math.nan
    try:
        output = subprocess.check_output(
            ["Rscript", rscript, "--rds", rds_path, "--snp-a", snp_a, "--snp-b", snp_b],
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return math.nan
    try:
        return float(output)
    except ValueError:
        return math.nan


def select_best_tile(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["top_pip_num"] = pd.to_numeric(df["top_pip"], errors="coerce")
    df["n_snps_num"] = pd.to_numeric(df["n_snps"], errors="coerce").fillna(-1)
    df = df.sort_values(
        ["base_region", "trait", "ancestry", "top_pip_num", "n_snps_num", "region_id"],
        ascending=[True, True, True, False, False, True],
    )
    return df.drop_duplicates(["base_region", "trait", "ancestry"], keep="first")


def main():
    args = parse_args()
    rep = pd.read_csv(args.replication, sep="\t")
    fm = pd.read_csv(args.finemap_summary, sep="\t")
    fm["base_region"] = fm["region_id"].astype(str).str.split("__").str[0]
    fm_best = select_best_tile(fm)

    mapping = fm_best.set_index(["base_region", "trait", "ancestry"])["region_id"].to_dict()
    r2_cache = {}

    ld_r2 = []
    ld_signal = []
    ld_rds_path = []
    for _, row in rep.iterrows():
        base_region = row.get("base_region")
        trait = row.get("trait")
        ancestry = row.get("ancestry")
        region_id = mapping.get((base_region, trait, ancestry), "")
        rds = Path(args.ld_dir) / str(ancestry) / f"{region_id}.rds"
        if not rds.exists():
            rds_path = ""
        else:
            rds_path = str(rds)
        key = (rds_path, row.get("top_snp_id_base"), row.get("top_snp_id_alt"))
        if key in r2_cache:
            r2 = r2_cache[key]
        else:
            r2 = compute_ld_r2(args.r2_script, rds_path, row.get("top_snp_id_base"), row.get("top_snp_id_alt"))
            r2_cache[key] = r2
        if math.isnan(r2):
            signal = "missing"
        elif r2 >= 0.8:
            signal = "same_ld_signal"
        elif r2 < 0.2:
            signal = "different_ld_signal"
        else:
            signal = "intermediate"
        ld_r2.append(r2)
        ld_signal.append(signal)
        ld_rds_path.append(rds_path)

    rep["ld_r2"] = ld_r2
    rep["ld_signal"] = ld_signal
    rep["ld_rds_path"] = ld_rds_path

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rep.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    main()
