#!/usr/bin/env python3
"""
Generate H4-focused reporting tables and trait-pair summaries.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--coloc-augmented",
        default="results/multitrait/coloc_summary_augmented.tsv",
        help="Augmented coloc summary TSV.",
    )
    parser.add_argument(
        "--clean-h4",
        default="results/multitrait/coloc_clean_h4.tsv",
        help="Strict clean H4 set TSV.",
    )
    parser.add_argument(
        "--out-main",
        default="results/analysis/coloc_main_h4.tsv",
        help="Output main (strict) H4 table.",
    )
    parser.add_argument(
        "--out-candidate",
        default="results/analysis/coloc_candidate_h4.tsv",
        help="Output candidate H4 table (no LOW_LD/LOW_N exclusions).",
    )
    parser.add_argument(
        "--out-counts",
        default="results/analysis/coloc_h4_traitpair_counts.tsv",
        help="Output trait-pair counts summary.",
    )
    return parser.parse_args()


def add_trait_pair(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["trait_pair"] = out["trait_a"].astype(str) + "__" + out["trait_b"].astype(str)
    return out


def select_cols(df: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "base_region",
        "ancestry",
        "trait_a",
        "trait_b",
        "trait_pair",
        "PP.H3",
        "PP.H4",
        "n_common_snps",
        "overlap_tier",
        "overlap_frac_min",
        "ld_overlap_min",
        "ld_flag_mode_a",
        "ld_flag_mode_b",
        "N_median_a",
        "N_median_b",
        "qc_flag",
    ]
    cols = [c for c in keep if c in df.columns]
    return df[cols].copy()


def summarize_counts(df: pd.DataFrame, label: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=["set", "trait_pair", "ancestry", "n_pairs", "n_loci"]
        )
    counts = (
        df.groupby(["trait_pair", "ancestry"])["base_region"]
        .agg(n_pairs="count", n_loci=pd.Series.nunique)
        .reset_index()
    )
    counts.insert(0, "set", label)
    return counts


def main() -> None:
    args = parse_args()
    aug_path = Path(args.coloc_augmented)
    clean_path = Path(args.clean_h4)
    if not aug_path.exists():
        raise SystemExit(f"Missing coloc augmented summary: {aug_path}")
    if not clean_path.exists():
        raise SystemExit(f"Missing clean H4 set: {clean_path}")

    aug = pd.read_csv(aug_path, sep="\t")
    aug["PP.H4"] = pd.to_numeric(aug.get("PP.H4"), errors="coerce")

    qc = aug.get("qc_flag", "").fillna("")
    base_mask = (aug.get("coloc_status") == "ok") & ~qc.str.contains("NO_OVERLAP") & ~qc.str.contains("MISSING_PP")
    candidate = aug[base_mask & (aug["PP.H4"] >= 0.8)].copy()
    candidate = add_trait_pair(candidate)

    clean = pd.read_csv(clean_path, sep="\t")
    clean["PP.H4"] = pd.to_numeric(clean.get("PP.H4"), errors="coerce")
    clean = add_trait_pair(clean)

    main_df = select_cols(clean)
    cand_df = select_cols(candidate)

    Path(args.out_main).parent.mkdir(parents=True, exist_ok=True)
    main_df.to_csv(args.out_main, sep="\t", index=False)
    Path(args.out_candidate).parent.mkdir(parents=True, exist_ok=True)
    cand_df.to_csv(args.out_candidate, sep="\t", index=False)

    counts = pd.concat(
        [
            summarize_counts(clean, "clean_h4"),
            summarize_counts(candidate, "candidate_h4"),
        ],
        ignore_index=True,
    )
    Path(args.out_counts).parent.mkdir(parents=True, exist_ok=True)
    counts.to_csv(args.out_counts, sep="\t", index=False)


if __name__ == "__main__":
    main()
