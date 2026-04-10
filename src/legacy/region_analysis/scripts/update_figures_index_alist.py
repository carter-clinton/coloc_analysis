#!/usr/bin/env python3
"""
Add A-list tags and trait-pair info to results/plots/figures_index.tsv.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


A_LIST = {
    "FTO_16q12",
    "BMI_5q13.3",
    "TCF7L2_10q25",
    "SH2B3_12q24",
    "RAD50_IL13_5q31.1",
    "HHEX_10q23",
}

ALIAS_MAP = {
    "FTO": "FTO_16q12",
    "FTO_16q12": "FTO_16q12",
    "BMI5q13": "BMI_5q13.3",
    "BMI_5q13.3": "BMI_5q13.3",
    "SH2B3": "SH2B3_12q24",
    "SH2B3_12q24": "SH2B3_12q24",
    "TCF7L2": "TCF7L2_10q25",
    "TCF7L2_10q25": "TCF7L2_10q25",
    "RAD50": "RAD50_IL13_5q31.1",
    "RAD50_IL13_5q31.1": "RAD50_IL13_5q31.1",
    "HHEX": "HHEX_10q23",
    "HHEX_10q23": "HHEX_10q23",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="results/plots/figures_index.tsv",
        help="Figures index TSV.",
    )
    parser.add_argument(
        "--output",
        default="results/plots/figures_index.tsv",
        help="Output TSV (overwrites input by default).",
    )
    return parser.parse_args()


def infer_locus(row: pd.Series) -> str:
    region = str(row.get("region", "")).strip()
    if region and region in ALIAS_MAP:
        return ALIAS_MAP[region]
    file_name = str(row.get("file", ""))
    for alias, locus in ALIAS_MAP.items():
        if alias and alias in file_name:
            return locus
    return ""


def infer_trait_pair(traits: str) -> str:
    if not traits:
        return ""
    parts = [p.strip() for p in str(traits).split(",") if p.strip()]
    if len(parts) == 2:
        return f"{parts[0]}_vs_{parts[1]}"
    return ""


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Missing figures index: {input_path}")

    df = pd.read_csv(input_path, sep="\t")
    df["alist_locus"] = df.apply(infer_locus, axis=1)
    df["is_alist"] = df["alist_locus"].isin(A_LIST).astype(int)
    df["trait_pair"] = df.get("traits", "").apply(infer_trait_pair)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep="\t", index=False)


if __name__ == "__main__":
    main()
