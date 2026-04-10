#!/usr/bin/env python3
"""
Build a summary of top PIP variants per base_region/trait/ancestry for plotting.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--finemap-summary",
        default="results/fine_mapping/finemap_summary_augmented.tsv",
        help="Fine-mapping summary with top PIP fields.",
    )
    parser.add_argument(
        "--output",
        default="results/fine_mapping/a_list_pip_summary.tsv",
        help="Output TSV path.",
    )
    return parser.parse_args()


def build_top_snp(row: pd.Series) -> str:
    chrom = row.get("top_chr")
    pos = row.get("top_pos")
    if pd.isna(chrom) or pd.isna(pos):
        return ""
    try:
        pos_int = int(float(pos))
    except ValueError:
        return ""
    chrom_str = str(chrom).replace("chr", "").replace("CHR", "")
    return f"{chrom_str}:{pos_int}"


def main() -> None:
    args = parse_args()
    finemap_path = Path(args.finemap_summary)
    if not finemap_path.exists():
        raise SystemExit(f"Missing finemap summary: {finemap_path}")

    df = pd.read_csv(finemap_path, sep="\t")
    df["base_region"] = df["region_id"].astype(str).str.split("__").str[0]
    df["top_pip_num"] = pd.to_numeric(df.get("top_pip"), errors="coerce")
    df["n_snps_num"] = pd.to_numeric(df.get("n_snps"), errors="coerce")

    df = df[df.get("status") == "success"].copy()
    df = df[df["top_pip_num"].notna()].copy()
    df = df.sort_values(
        ["base_region", "trait", "ancestry", "top_pip_num", "n_snps_num", "region_id"],
        ascending=[True, True, True, False, False, True],
    )
    df = df.drop_duplicates(["base_region", "trait", "ancestry"], keep="first")

    df["top_snp"] = df.apply(build_top_snp, axis=1)

    keep_cols = [
        "base_region",
        "region_id",
        "trait",
        "ancestry",
        "top_snp",
        "top_chr",
        "top_pos",
        "top_pip",
        "top_beta",
        "top_se",
        "n_snps",
        "n_cs",
        "ld_flag",
    ]
    out = df[[col for col in keep_cols if col in df.columns]].copy()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, sep="\t", index=False)


if __name__ == "__main__":
    main()
