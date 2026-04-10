#!/usr/bin/env python3
"""
Summarize effect-scale QC with simple caution flags.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="results/qc/effect_scale_report_fixed.tsv",
        help="Effect-scale report TSV.",
    )
    parser.add_argument(
        "--output",
        default="results/qc/effect_scale_summary.tsv",
        help="Output summary TSV.",
    )
    parser.add_argument(
        "--median-thresh",
        type=float,
        default=1.0,
        help="Median log10 mismatch threshold for caution.",
    )
    parser.add_argument(
        "--tail-thresh",
        type=float,
        default=5.0,
        help="Tail mismatch percent threshold for caution.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = Path(args.input)
    if not path.exists():
        raise SystemExit(f"Missing effect-scale report: {path}")
    df = pd.read_csv(path, sep="\t")
    df["p_score_raw"] = pd.to_numeric(df.get("p_score_raw"), errors="coerce")
    df["P_mismatch_raw_pct"] = pd.to_numeric(df.get("P_mismatch_raw_pct"), errors="coerce")
    df["flag"] = "ok"
    mask = (df["p_score_raw"] > args.median_thresh) | (df["P_mismatch_raw_pct"] > args.tail_thresh)
    df.loc[mask, "flag"] = "caution"
    keep = [
        "trait",
        "ancestry",
        "p_score_raw",
        "P_mismatch_raw_pct",
        "flag",
    ]
    keep = [c for c in keep if c in df.columns]
    out = df[keep].copy()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
