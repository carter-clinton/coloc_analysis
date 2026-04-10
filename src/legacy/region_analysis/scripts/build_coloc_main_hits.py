#!/usr/bin/env python3
"""
Build main coloc results table for manuscript.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--coloc-augmented",
        default="results/multitrait/coloc_summary_augmented.tsv",
    )
    parser.add_argument(
        "--output",
        default="results/multitrait/coloc_main_hits.tsv",
    )
    parser.add_argument(
        "--exclude-low-ld",
        action="store_true",
        help="Exclude pairs flagged LOW_LD in qc_flag.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    path = Path(args.coloc_augmented)
    if not path.exists():
        raise SystemExit(f"Missing coloc augmented summary: {path}")
    df = pd.read_csv(path, sep="\t")
    df["PP.H3"] = pd.to_numeric(df.get("PP.H3"), errors="coerce")
    df["PP.H4"] = pd.to_numeric(df.get("PP.H4"), errors="coerce")

    df = df[df.get("coloc_status") == "ok"].copy()
    qc = df.get("qc_flag", "").fillna("")
    df = df[~qc.str.contains("NO_OVERLAP") & ~qc.str.contains("MISSING_PP")].copy()
    if args.exclude_low_ld:
        df = df[~qc.str.contains("LOW_LD")].copy()

    df = df[(df["PP.H4"] >= 0.8) | (df["PP.H3"] >= 0.8)].copy()

    df["ld_flag_mode"] = df.apply(
        lambda r: "used_ld"
        if r.get("ld_flag_mode_a") == "used_ld" and r.get("ld_flag_mode_b") == "used_ld"
        else "mixed",
        axis=1,
    )
    df["N_median_min"] = df[["N_median_a", "N_median_b"]].min(axis=1)

    keep_cols = [
        "base_region",
        "ancestry",
        "trait_a",
        "trait_b",
        "PP.H3",
        "PP.H4",
        "coloc_status",
        "qc_flag",
        "n_common_snps",
        "overlap_tier",
        "overlap_frac_min",
        "ld_flag_mode",
        "ld_flag_mode_a",
        "ld_flag_mode_b",
        "ld_overlap_min",
        "N_median_min",
    ]
    keep_cols = [c for c in keep_cols if c in df.columns]
    out = df[keep_cols].copy()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
