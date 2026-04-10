#!/usr/bin/env python3
"""
Build clean coloc subsets from results/multitrait/coloc_summary_augmented.tsv.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="results/multitrait/coloc_summary_augmented.tsv",
        help="Augmented coloc summary TSV.",
    )
    parser.add_argument(
        "--out-clean",
        default="results/multitrait/coloc_clean.tsv",
        help="Output clean subset TSV.",
    )
    parser.add_argument(
        "--out-clean-h4",
        default="results/multitrait/coloc_clean_h4.tsv",
        help="Output clean subset with PP.H4 >= 0.8.",
    )
    parser.add_argument(
        "--allow-low-ld",
        action="store_true",
        help="Keep LOW_LD entries in clean set.",
    )
    parser.add_argument(
        "--allow-low-n",
        action="store_true",
        help="Keep LOW_N entries in clean set.",
    )
    return parser.parse_args()


def has_flag(series: pd.Series, flag: str) -> pd.Series:
    return series.fillna("").str.contains(flag, regex=False)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Missing coloc summary: {input_path}")

    df = pd.read_csv(input_path, sep="\t")
    qc = df.get("qc_flag", pd.Series([""] * len(df)))

    mask = ~has_flag(qc, "NO_OVERLAP") & ~has_flag(qc, "MISSING_PP")
    if not args.allow_low_ld:
        mask &= ~has_flag(qc, "LOW_LD")
    if not args.allow_low_n:
        mask &= ~has_flag(qc, "LOW_N")

    if "coloc_status" in df.columns:
        mask &= df["coloc_status"].fillna("") == "ok"

    clean = df[mask].copy()
    clean_path = Path(args.out_clean)
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(clean_path, sep="\t", index=False)

    clean_h4 = clean.copy()
    clean_h4["PP.H4"] = pd.to_numeric(clean_h4.get("PP.H4"), errors="coerce")
    clean_h4 = clean_h4[clean_h4["PP.H4"] >= 0.8].copy()
    clean_h4_path = Path(args.out_clean_h4)
    clean_h4_path.parent.mkdir(parents=True, exist_ok=True)
    clean_h4.to_csv(clean_h4_path, sep="\t", index=False)


if __name__ == "__main__":
    main()
