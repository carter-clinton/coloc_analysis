#!/usr/bin/env python3
"""mtCOJO eligible-target selector (D-M2-08 + D-M2-Q5).

A (stratum, target_trait) tuple is eligible to fire mtCOJO iff:

  1. MTAG produced a novel locus for `target_trait` in this stratum
     (mtag_pval < 5e-8 AND max_FDR < 0.05 in
     `data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt`).

  2. The bivariate-intercept gcov_int between `target_trait` and ANY
     contributing covariate trait exceeds 0.1 (D-M2-08 threshold; Turley
     2018 §"sample overlap").

This module exports two public entry points:

  - eligible_targets(mtag_novel: pd.DataFrame, R, trait_keys, threshold=0.1)
      Test-facing API consumed by tests/m2/test_mtcojo_eligible_targets.py.
      Inputs:
        mtag_novel : DataFrame with columns ['target_trait', 'stratum', ...]
                     listing the target traits with at least one MTAG-novel hit.
        R          : K×K bivariate-intercept matrix slice for the stratum.
        trait_keys : ordered trait keys aligned to R rows/cols.
        threshold  : D-M2-08 default 0.1.
      Output: DataFrame with columns
        ['target_trait', 'max_overlapping_intercept', 'max_with_trait', 'n_mtag_novel_loci']
      restricted to MTAG-novel targets that ALSO pass the extreme-overlap test.

  - select_eligible_targets(mtag_filtered_path, long_matrix_path,
                            sidecar_path) -> pd.DataFrame
      Production-fire entry point used by the Snakemake rule. Reads the
      Wave 2 maxfdr_filtered.txt + Wave 1 long-form rg_matrix +
      residcov.trait_order.json sidecar, builds the same eligibility
      DataFrame.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from mtcojo_extreme_overlap_filter import (
    _DEFAULT_THRESHOLD,
    has_extreme_overlap,
    max_overlapping_intercept,
)

_GCOV_INT_THRESHOLD = 0.1   # D-M2-08 Turley 2018 recommended (matches mtcojo_extreme_overlap_filter._DEFAULT_THRESHOLD)
assert _GCOV_INT_THRESHOLD == _DEFAULT_THRESHOLD, (
    "D-M2-08 threshold drift between mtcojo_eligible_targets and "
    "mtcojo_extreme_overlap_filter — keep both at 0.1"
)
_MTAG_PVAL_GWS = 5e-8
_MTAG_MAX_FDR = 0.05


def eligible_targets(
    mtag_novel: pd.DataFrame,
    R: np.ndarray,
    trait_keys: Sequence[str],
    threshold: float = _GCOV_INT_THRESHOLD,
) -> pd.DataFrame:
    """Return DataFrame of (target_trait, max_overlapping_intercept, max_with_trait, n_mtag_novel_loci).

    Test contract (tests/m2/test_mtcojo_eligible_targets.py):
      - Targets WITH MTAG-novel hits AND any |gcov_int| > threshold → emitted
      - MTAG-null targets → NOT emitted regardless of overlap

    Parameters
    ----------
    mtag_novel : pd.DataFrame
        Rows describe MTAG-novel target traits. Must include 'target_trait'
        column. Counts of novel loci per target are summed across rows
        with the same target_trait (or stored as 1 if absent).
    R : np.ndarray
        K×K bivariate-intercept matrix slice for the stratum.
    trait_keys : Sequence[str]
        Ordered trait keys aligned to R.
    threshold : float
        D-M2-08 threshold (default 0.1).
    """
    if "target_trait" not in mtag_novel.columns:
        raise ValueError("mtag_novel must contain 'target_trait' column")

    # Per-target novel-locus counts.
    if mtag_novel.empty:
        return pd.DataFrame(
            columns=["target_trait", "max_overlapping_intercept", "max_with_trait", "n_mtag_novel_loci"]
        )

    counts = mtag_novel.groupby("target_trait").size().to_dict()

    rows = []
    for target, n_novel in counts.items():
        if target not in trait_keys:
            # MTAG-novel target absent from R (e.g., stratum mismatch);
            # cannot evaluate overlap → skip.
            continue
        if not has_extreme_overlap(target, trait_keys, R, threshold=threshold):
            continue
        max_int, with_trait = max_overlapping_intercept(target, trait_keys, R)
        rows.append({
            "target_trait": target,
            "max_overlapping_intercept": max_int,
            "max_with_trait": with_trait,
            "n_mtag_novel_loci": int(n_novel),
        })
    return pd.DataFrame(
        rows,
        columns=["target_trait", "max_overlapping_intercept", "max_with_trait", "n_mtag_novel_loci"],
    )


def _build_R_from_long_matrix(
    long_path: Path,
    trait_order: Sequence[str],
) -> np.ndarray:
    """Re-assemble K×K gcov_int matrix from Wave 1 long-form TSV.

    Long schema (Wave 1 m2-01 SUMMARY): trait_a, trait_b, rg, rg_se,
    gcov_int, gcov_int_se, h2_a, h2_b, p_rg, z_rg, h2_int_a, h2_int_se_a.
    """
    long = pd.read_csv(long_path, sep="\t")
    if "gcov_int" not in long.columns:
        raise ValueError(f"long matrix at {long_path} missing 'gcov_int' column")
    K = len(trait_order)
    idx = {t: i for i, t in enumerate(trait_order)}
    R = np.zeros((K, K))
    np.fill_diagonal(R, 1.0)
    for _, row in long.iterrows():
        a, b = row["trait_a"], row["trait_b"]
        if a not in idx or b not in idx:
            continue
        v = row["gcov_int"]
        if pd.isna(v):
            continue
        i, j = idx[a], idx[b]
        if i == j:
            continue
        R[i, j] = R[j, i] = float(v)
    return R


def select_eligible_targets(
    mtag_filtered_path: Path,
    long_matrix_path: Path,
    sidecar_path: Path,
    pval_threshold: float = _MTAG_PVAL_GWS,
    fdr_threshold: float = _MTAG_MAX_FDR,
    overlap_threshold: float = _GCOV_INT_THRESHOLD,
) -> pd.DataFrame:
    """Production-fire entry: derive eligibility list from on-disk artifacts.

    The MTAG filtered output (Wave 2) has columns:
      SNP, A1, A2, Z, N, FRQ, mtag_beta, mtag_se, mtag_z, mtag_pval, max_FDR, trait_key

    The Wave 2 audit log notes max_FDR is a placeholder=0.0 pending an
    LSF --fdr re-fire; rows with mtag_pval < 5e-8 are considered novel
    pending re-fire (Wave 4 superset behavior — caveat surfaced in the
    M2 closeout).
    """
    sidecar = json.loads(sidecar_path.read_text())
    trait_order = sidecar["trait_order"]

    mtag = pd.read_csv(mtag_filtered_path, sep="\t")
    if "mtag_pval" not in mtag.columns or "trait_key" not in mtag.columns:
        raise ValueError(
            f"MTAG filtered at {mtag_filtered_path} missing mtag_pval/trait_key cols"
        )

    novel = mtag[mtag["mtag_pval"] < pval_threshold]
    if "max_FDR" in novel.columns:
        # Apply FDR filter only when max_FDR is non-placeholder
        # (Wave 2 placeholder is 0.0 retain-all; future LSF re-fire will
        # populate real per-trait scalars).
        novel = novel[novel["max_FDR"] < fdr_threshold]

    # Build the (target_trait) lookup; we only need the trait_key and a
    # row-count per target.
    novel_per_trait = (
        novel.groupby("trait_key").size().reset_index(name="n_mtag_novel_loci")
    )
    novel_per_trait = novel_per_trait.rename(columns={"trait_key": "target_trait"})

    R = _build_R_from_long_matrix(long_matrix_path, trait_order)

    return eligible_targets(novel_per_trait, R, trait_order, threshold=overlap_threshold)


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stratum", required=True)
    ap.add_argument("--mtag-filtered", type=Path, required=True)
    ap.add_argument("--long-matrix", type=Path, required=True)
    ap.add_argument("--sidecar", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pval-threshold", type=float, default=_MTAG_PVAL_GWS)
    ap.add_argument("--fdr-threshold", type=float, default=_MTAG_MAX_FDR)
    ap.add_argument("--overlap-threshold", type=float, default=_GCOV_INT_THRESHOLD)
    args = ap.parse_args()

    df = select_eligible_targets(
        args.mtag_filtered,
        args.long_matrix,
        args.sidecar,
        pval_threshold=args.pval_threshold,
        fdr_threshold=args.fdr_threshold,
        overlap_threshold=args.overlap_threshold,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, sep="\t", index=False)
    print(
        f"{args.stratum}: {len(df)} eligible target traits "
        f"(gcov_int > {args.overlap_threshold})"
    )


if __name__ == "__main__":
    _main()
