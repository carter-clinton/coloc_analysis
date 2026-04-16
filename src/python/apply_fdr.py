#!/usr/bin/env python3
"""
D-04c: BH-FDR q<0.05 across ALL r_g tests jointly (not per-ancestry-pair, not
per-trait-pair-stratified). Matches Phase 5 D-01a pathway FDR convention.

RESEARCH A-2 option (a) minimum-deviation: flag SE>0.3 as 'unreliable_se' column
per LDSC wiki guidance without removing the row.

Input: rg_raw.tsv (from collect_rg_logs / munge_trait_pair_rg.py)
Output: rg_matrix.tsv (D-06d supplementary table) with added columns:
    q_bh, fdr_significant, unreliable_se
"""
import argparse
import sys

import pandas as pd
from statsmodels.stats.multitest import multipletests


def apply_bh_fdr(
    rg_raw_tsv: str,
    fdr_q: float = 0.05,
    se_flag_threshold: float = 0.3,
    out_tsv: str = None,
) -> pd.DataFrame:
    """Apply Benjamini-Hochberg FDR correction across all r_g tests.

    Parameters
    ----------
    rg_raw_tsv : str
        Path to input TSV with columns including 'p' and 'se'.
    fdr_q : float
        FDR q-value threshold (default 0.05 per D-04c).
    se_flag_threshold : float
        SE threshold above which to flag as unreliable (default 0.3 per A-2).
    out_tsv : str, optional
        If provided, write corrected results to this path.

    Returns
    -------
    pd.DataFrame
        Input dataframe augmented with q_bh, fdr_significant, unreliable_se.
    """
    df = pd.read_csv(rg_raw_tsv, sep="\t")

    # Drop tests where LDSC could not compute rg (p=NA)
    valid = df["p"].notna()

    if valid.sum() > 0:
        rej, q, _, _ = multipletests(
            df.loc[valid, "p"].values, alpha=fdr_q, method="fdr_bh"
        )
        df.loc[valid, "q_bh"] = q
        df.loc[valid, "fdr_significant"] = rej
    else:
        df["q_bh"] = pd.NA
        df["fdr_significant"] = False

    # Invalid rows get NA/False
    df.loc[~valid, "q_bh"] = pd.NA
    df.loc[~valid, "fdr_significant"] = False

    # RESEARCH A-2 option (a): flag SE > threshold as unreliable
    df["unreliable_se"] = df["se"].abs() > se_flag_threshold

    if out_tsv:
        df.to_csv(out_tsv, sep="\t", index=False)

    return df


def main():
    parser = argparse.ArgumentParser(
        description="D-04c: Apply BH-FDR correction to LDSC r_g matrix."
    )
    parser.add_argument("--in", dest="input_tsv", required=True, help="Input rg_raw.tsv")
    parser.add_argument("--out", required=True, help="Output rg_matrix.tsv")
    parser.add_argument("--fdr-q", type=float, default=0.05, help="FDR q threshold")
    parser.add_argument("--se-flag", type=float, default=0.3, help="SE unreliability threshold")
    args = parser.parse_args()

    df = apply_bh_fdr(args.input_tsv, args.fdr_q, args.se_flag, args.out)
    n_sig = df["fdr_significant"].sum() if "fdr_significant" in df.columns else 0
    n_unreliable = df["unreliable_se"].sum() if "unreliable_se" in df.columns else 0
    print(f"FDR correction complete: {n_sig} significant at q<{args.fdr_q}, "
          f"{n_unreliable} flagged unreliable SE>{args.se_flag}")


if __name__ == "__main__":
    main()
