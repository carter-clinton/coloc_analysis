#!/usr/bin/env python3
"""
Extract HyPrColoc results for a specific base_region/ancestry.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary",
        default="results/multitrait/hyprcoloc_summary.tsv",
        help="HyPrColoc summary TSV.",
    )
    parser.add_argument("--base-region", required=True)
    parser.add_argument("--ancestry", required=True)
    parser.add_argument(
        "--output",
        default="results/analysis/hyprcoloc_focus.tsv",
        help="Output TSV path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary_path = Path(args.summary)
    if not summary_path.exists():
        raise SystemExit(f"Missing summary: {summary_path}")
    df = pd.read_csv(summary_path, sep="\t")
    out = df[
        (df["base_region"] == args.base_region)
        & (df["ancestry"] == args.ancestry)
    ].copy()
    if out.empty:
        raise SystemExit(
            f"No HyPrColoc row for {args.base_region} {args.ancestry}"
        )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
