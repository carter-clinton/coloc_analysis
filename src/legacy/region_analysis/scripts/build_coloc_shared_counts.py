#!/usr/bin/env python3
"""
Summarize shared causal loci counts by trait pair and ancestry (PP.H4 >= 0.8).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--coloc-summary",
        default="results/multitrait/coloc_summary.tsv",
        help="Coloc summary TSV.",
    )
    parser.add_argument(
        "--output",
        default="results/multitrait/coloc_shared_counts.tsv",
        help="Output TSV path.",
    )
    parser.add_argument(
        "--h4-threshold",
        type=float,
        default=0.8,
        help="PP.H4 threshold for shared-causal loci.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    coloc_path = Path(args.coloc_summary)
    if not coloc_path.exists():
        raise SystemExit(f"Missing coloc summary: {coloc_path}")

    df = pd.read_csv(coloc_path, sep="\t")
    df["PP.H4"] = pd.to_numeric(df.get("PP.H4"), errors="coerce")
    df = df[df["PP.H4"] >= args.h4_threshold].copy()
    df["trait_pair"] = df["trait_a"].astype(str) + "__" + df["trait_b"].astype(str)

    counts = (
        df.groupby(["trait_pair", "ancestry"])["base_region"]
        .nunique()
        .reset_index(name="n_loci")
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    counts.to_csv(output_path, sep="\t", index=False)


if __name__ == "__main__":
    main()
