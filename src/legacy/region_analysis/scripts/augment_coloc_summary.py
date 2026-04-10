#!/usr/bin/env python3
import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="Augment coloc summary with QC fields.")
    parser.add_argument("--coloc-summary", required=True)
    parser.add_argument("--region-trait-qc", required=True)
    parser.add_argument("--effect-scale-actions", required=False)
    parser.add_argument("--output", required=True)
    parser.add_argument("--low-n-threshold", type=float, default=10000)
    return parser.parse_args()


def safe_div(numer, denom):
    if denom is None or denom == 0 or math.isnan(denom):
        return math.nan
    return float(numer) / float(denom)


def main():
    args = parse_args()
    cs = pd.read_csv(args.coloc_summary, sep="\t")
    qc = pd.read_csv(args.region_trait_qc, sep="\t")

    actions = None
    if args.effect_scale_actions and Path(args.effect_scale_actions).exists():
        actions = pd.read_csv(args.effect_scale_actions, sep="\t")
        actions = actions.rename(columns={"trait": "trait_action", "ancestry": "ancestry_action"})

    qc_a = qc.rename(columns={"base_region": "base_region_a", "trait": "trait_a", "ancestry": "ancestry"})
    qc_b = qc.rename(columns={"base_region": "base_region_b", "trait": "trait_b", "ancestry": "ancestry"})
    qc_a = qc_a.rename(columns={col: f"{col}_a" for col in qc_a.columns if col not in {"base_region_a", "trait_a", "ancestry"}})
    qc_b = qc_b.rename(columns={col: f"{col}_b" for col in qc_b.columns if col not in {"base_region_b", "trait_b", "ancestry"}})

    cs = cs.merge(
        qc_a,
        left_on=["base_region", "trait_a", "ancestry"],
        right_on=["base_region_a", "trait_a", "ancestry"],
        how="left",
    ).merge(
        qc_b,
        left_on=["base_region", "trait_b", "ancestry"],
        right_on=["base_region_b", "trait_b", "ancestry"],
        how="left",
    )

    cs["overlap_frac_a"] = cs.apply(
        lambda r: safe_div(r.get("n_common_snps", 0), r.get("nsnps_coloc_input_a", math.nan)), axis=1
    )
    cs["overlap_frac_b"] = cs.apply(
        lambda r: safe_div(r.get("n_common_snps", 0), r.get("nsnps_coloc_input_b", math.nan)), axis=1
    )
    cs["overlap_frac_min"] = cs[["overlap_frac_a", "overlap_frac_b"]].min(axis=1)
    cs["ld_overlap_min"] = cs[["ld_overlap_fraction_a", "ld_overlap_fraction_b"]].min(axis=1)
    cs["overlap_tier"] = np.where(
        cs["n_common_snps"] >= 200,
        "primary",
        np.where(cs["n_common_snps"] >= 100, "secondary", "low"),
    )

    if actions is not None:
        action_a = actions.rename(columns={
            "trait_action": "trait_a",
            "ancestry_action": "ancestry",
            "action": "effect_action_a",
        })
        action_b = actions.rename(columns={
            "trait_action": "trait_b",
            "ancestry_action": "ancestry",
            "action": "effect_action_b",
        })
        cs = cs.merge(action_a[["trait_a", "ancestry", "effect_action_a"]],
                      on=["trait_a", "ancestry"], how="left")
        cs = cs.merge(action_b[["trait_b", "ancestry", "effect_action_b"]],
                      on=["trait_b", "ancestry"], how="left")

    flags = []
    coloc_status = []
    for _, row in cs.iterrows():
        row_flags = []
        missing_pp = pd.isna(row.get("PP.H3")) or pd.isna(row.get("PP.H4"))
        n_common = row.get("n_common_snps", 0)
        n_merge = row.get("n_merge_chrpos", 0)
        if n_common == 0 or missing_pp:
            if n_merge and not pd.isna(n_merge) and n_merge > 0:
                row_flags.append("ALLELE_MISMATCH_AFTER_NORM")
                coloc_status.append("allele_mismatch")
            else:
                row_flags.append("NO_OVERLAP")
                coloc_status.append("no_overlap")
        else:
            coloc_status.append("ok")
        if missing_pp:
            row_flags.append("MISSING_PP")
        if n_common < 100:
            row_flags.append("LOW_OVERLAP")
        elif n_common < 200:
            row_flags.append("LOW_OVERLAP_SECONDARY")
        ld_overlap_min = row.get("ld_overlap_min")
        if (not pd.isna(ld_overlap_min) and ld_overlap_min < 0.2) or row.get("ld_flag_mode_a") == "identity" or row.get("ld_flag_mode_b") == "identity":
            row_flags.append("LOW_LD")
        med_a = row.get("N_median_a")
        med_b = row.get("N_median_b")
        if (not pd.isna(med_a) and med_a < args.low_n_threshold) or (not pd.isna(med_b) and med_b < args.low_n_threshold):
            row_flags.append("LOW_N")
        if (row.get("effect_action_a") and row.get("effect_action_a") != "keep") or (
            row.get("effect_action_b") and row.get("effect_action_b") != "keep"
        ):
            row_flags.append("UNSTABLE_EFFECT_SCALE")
        flags.append(";".join(dict.fromkeys(row_flags)))

    cs["coloc_status"] = coloc_status
    cs["qc_flag"] = flags

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    cs.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
