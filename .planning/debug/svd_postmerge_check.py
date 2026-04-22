#!/usr/bin/env python3
"""Replicate the EXACT matrix LDSC inverts for asthma_EUR — including the
HapMap3 sumstats merge + chi^2 filter + check_variance pruning.

This is the matrix that produced cond = 1.16e20 in production
(asthma_EUR_pathway_h2.log line 100).

The key insight from svd_genome_check.py is that the genome-wide ref_ld
matrix is full-rank (cond ~ 5e3) BEFORE merging with sumstats. The
condition-number explosion must happen at one of:
  (a) post-variance-pruning narrow custom subset zeroing out
  (b) the SNP subset after merge_with_sumstats
  (c) the chi^2-filtered subset (chisq_max ~ 562 from the log)
"""
import gzip
import os
import sys

import numpy as np
import pandas as pd

ROOT = "/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis"
BASE_TPL = f"{ROOT}/data/reference/ldsc/baselineLD.{{c}}.l2.ldscore.gz"
CUST_TPL = f"{ROOT}/results/pathway/ldsc_partitioned/ld_scores/custom_pathway.{{c}}.l2.ldscore.gz"
W_TPL = f"{ROOT}/data/reference/ldsc/1000G_Phase3_weights_hm3_no_MHC/weights.hm3_noMHC.{{c}}.l2.ldscore.gz"
SUMSTATS = f"{ROOT}/results/pathway/ldsc_partitioned/munged/asthma_EUR.sumstats.gz"


def merge_ldscore_sets(base_dfs, cust_dfs):
    """Replicate ps.ldscore_fromlist behavior: merge two sets on SNP, side by side."""
    base_all = pd.concat(base_dfs, ignore_index=True)
    cust_all = pd.concat(cust_dfs, ignore_index=True)
    merged = base_all.merge(cust_all, on=["CHR", "SNP", "BP"], how="inner")
    return merged


def main():
    print("=== Replicating asthma_EUR LDSC partitioned_h2 condition check ===\n")

    # 1. Load genome-wide ref_ld
    base_dfs = [pd.read_csv(BASE_TPL.format(c=c), sep="\t") for c in range(1, 23)]
    cust_dfs = [pd.read_csv(CUST_TPL.format(c=c), sep="\t") for c in range(1, 23)]
    ref_ld = merge_ldscore_sets(base_dfs, cust_dfs)
    print(f"genome-wide ref_ld merge: {ref_ld.shape}")
    ld_cols = [c for c in ref_ld.columns if c not in ("CHR", "SNP", "BP")]
    print(f"  columns (n annotations): {len(ld_cols)}")

    # 2. Apply check_variance: drop zero-variance LD score columns
    var_zero = ref_ld[ld_cols].var() == 0
    n_dropped = var_zero.sum()
    print(f"\ncheck_variance: {n_dropped} columns dropped for zero variance:")
    for c in var_zero.index[var_zero]:
        print(f"  - {c}")
    keep_cols = [c for c in ld_cols if not var_zero[c]]
    ref_ld_kept = ref_ld[["SNP"] + keep_cols]
    print(f"  surviving ref_ld shape: {ref_ld_kept.shape}")

    # 3. Load weights and sumstats
    weights = pd.concat(
        [pd.read_csv(W_TPL.format(c=c), sep="\t") for c in range(1, 23)],
        ignore_index=True,
    )
    print(f"\nweights LD scores: {weights.shape}")

    sumstats = pd.read_csv(SUMSTATS, sep="\t")
    print(f"munged sumstats: {sumstats.shape}")
    print(f"  columns: {list(sumstats.columns)}")

    # 4. Replicate read_ld_and_sumstats merges
    # smart_merge(ld_scores, sumstats) → first ref vs sumstats, then result vs weights
    merged = ref_ld_kept.merge(sumstats, on="SNP", how="inner")
    print(f"\nAfter ref_ld merge with sumstats: {merged.shape[0]} SNPs")
    merged = merged.merge(weights[["SNP", "L2"]] if "L2" in weights.columns else weights, on="SNP", how="inner")
    # Could be that the weight col isn't named L2 — check
    print(f"After merge with weights: {merged.shape[0]} SNPs")

    # 5. The matrix passed to check_ld_condition_number is `sumstats[ref_ld_cnames]`
    X_post = merged[keep_cols].to_numpy(dtype=np.float64)
    print(f"\nMatrix to check_ld_condition_number: {X_post.shape}")
    print(f"(Production log says: 'After merging with regression SNP LD, 967534 SNPs remain'.)")

    cond_post = np.linalg.cond(X_post)
    print(f"\ncond(X_post) BEFORE chi^2 filter = {cond_post:.6e}")

    s = np.linalg.svd(X_post, compute_uv=False)
    print(f"  σ_max = {s[0]:.6e}, σ_min = {s[-1]:.6e}")
    print(f"  rank @ σ_rel > 1e-10: {int(np.sum(s > s[0] * 1e-10))} / {X_post.shape[1]}")

    print("\nSmallest 10 singular values:")
    for i in range(10):
        idx = X_post.shape[1] - 10 + i
        print(f"  σ[{idx:3d}] = {s[idx]:.6e}  rel: {s[idx] / s[0]:.6e}")

    # 6. Apply chi^2 filter (chisq_max = 562.534 from the production log)
    # chisq = Z^2; cap at chisq_max
    chisq_max = 562.534
    chisq = merged["Z"].values ** 2
    mask = chisq < chisq_max
    print(f"\nApplying chi^2 < {chisq_max} filter: keep {mask.sum()} / {len(mask)} SNPs")
    X_filt = X_post[mask]
    print(f"X_filt shape: {X_filt.shape}")

    cond_filt = np.linalg.cond(X_filt)
    print(f"\ncond(X_filt) AFTER chi^2 filter = {cond_filt:.6e}")
    s = np.linalg.svd(X_filt, compute_uv=False)
    print(f"  σ_max = {s[0]:.6e}, σ_min = {s[-1]:.6e}")
    print(f"  rank @ σ_rel > 1e-10: {int(np.sum(s > s[0] * 1e-10))} / {X_filt.shape[1]}")

    print("\nSmallest 10 singular values (post-chi^2-filter):")
    for i in range(10):
        idx = X_filt.shape[1] - 10 + i
        print(f"  σ[{idx:3d}] = {s[idx]:.6e}  rel: {s[idx] / s[0]:.6e}")

    # Production log says cond = 116151824161276379136 ≈ 1.16e20.
    # cond from np.linalg.cond is computed on X (not X^T X), so let's also
    # see what int(np.linalg.cond(X_filt)) returns.
    print(f"\nProduction log cond value: 1.16e20")
    print(f"Our cond(X_filt) (before chi^2 mask, identical match expected): "
          f"int = {int(cond_post)}")

    # Per-column variance on the filtered matrix to identify zero-vars on this subset
    print("\nPer-column std on chi^2-filtered subset, sorted ascending:")
    stds = X_filt.std(axis=0)
    sort_idx = np.argsort(stds)
    for j in sort_idx[:20]:
        kind = "BASE" if j < 97 else "CUST"
        print(f"  std={stds[j]:.6e}  {kind}  col={keep_cols[j] if j < len(keep_cols) else '?'}")

    # Zero-variance columns post-filter?
    n_zero = int((stds == 0).sum())
    print(f"\nPost-filter zero-variance columns: {n_zero}")
    if n_zero > 0:
        for j in np.where(stds == 0)[0]:
            print(f"  zero col: {keep_cols[j]}")

    # === Identify the rank-deficient direction in the filtered matrix ===
    print("\n=== Right singular vectors of smallest singular values (filtered X) ===")
    U, s_full, Vt = np.linalg.svd(X_filt, full_matrices=False)
    for k in range(3):
        idx = X_filt.shape[1] - 1 - k
        print(f"\n--- σ[{idx}] = {s_full[idx]:.6e} ---")
        v = Vt[idx]
        top = np.argsort(-np.abs(v))[:10]
        for j in top:
            kind = "BASE" if j < 97 else "CUST"
            print(f"   {kind}  v[{j:3d}] = {v[j]:+.5f}   {keep_cols[j]}")


if __name__ == "__main__":
    main()
