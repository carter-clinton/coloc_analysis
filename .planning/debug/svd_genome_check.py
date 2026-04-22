#!/usr/bin/env python3
"""Genome-wide check: confirm chr22 zero-variance pattern holds globally.

For each chromosome 1..22:
  - Load custom_pathway LD scores
  - For each custom annotation column, report:
        n_nonzero (out of n_snps), max value, std, M_5_50 from .l2.M_5_50 file
  - Confirm whether the rank-deficiency we found on chr22 is structural
    (the annotation has zero SNPs across the whole genome) or just chr-local.

Also concatenate ALL 22 chromosomes and re-run the SVD on the genome-wide
joint matrix.
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = "/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis"
BASE_TPL = f"{ROOT}/data/reference/ldsc/baselineLD.{{c}}.l2.ldscore.gz"
CUST_TPL = f"{ROOT}/results/pathway/ldsc_partitioned/ld_scores/custom_pathway.{{c}}.l2.ldscore.gz"
M_TPL = f"{ROOT}/results/pathway/ldsc_partitioned/ld_scores/custom_pathway.{{c}}.l2.M_5_50"
M_BASE_TPL = f"{ROOT}/data/reference/ldsc/baselineLD.{{c}}.l2.M_5_50"


def per_chr_summary():
    print("=== Per-chromosome non-zero SNP count for each custom annotation ===\n")
    print("Reads .l2.M_5_50 (SNP count per annotation that LDSC actually uses)\n")

    # Load M_5_50 from custom_pathway for all chrs
    cust_M = {}
    for c in range(1, 23):
        path = M_TPL.format(c=c)
        if not os.path.exists(path):
            print(f"chr{c}: MISSING {path}")
            continue
        with open(path) as f:
            line = f.read().strip()
        cust_M[c] = [int(x) for x in line.split()]

    # Get column names from chr1
    df = pd.read_csv(CUST_TPL.format(c=1), sep="\t", nrows=1)
    cust_cols = [c for c in df.columns if c not in ("CHR", "SNP", "BP")]

    n_cust = len(cust_cols)
    # Build a cust × chr matrix of M_5_50 counts
    M_arr = np.zeros((n_cust, 22), dtype=int)
    for c in range(1, 23):
        M_arr[:, c - 1] = cust_M[c]

    print(f"{'annotation':<45} {'M_5_50 sum':>12} {'min':>6} {'max':>6} {'#chrs nonzero':>14}")
    for i, name in enumerate(cust_cols):
        row = M_arr[i]
        print(f"{name:<45} {row.sum():>12d} {row.min():>6d} {row.max():>6d} "
              f"{int((row > 0).sum()):>14d}")

    print("\n=== Genome-wide rank check: stack all chromosomes ===\n")
    base_dfs = []
    cust_dfs = []
    for c in range(1, 23):
        bdf = pd.read_csv(BASE_TPL.format(c=c), sep="\t")
        cdf = pd.read_csv(CUST_TPL.format(c=c), sep="\t")
        base_dfs.append(bdf)
        cust_dfs.append(cdf)
    base_all = pd.concat(base_dfs, ignore_index=True)
    cust_all = pd.concat(cust_dfs, ignore_index=True)
    print(f"baselineLD genome-wide: {base_all.shape}")
    print(f"custom_pathway genome-wide: {cust_all.shape}")

    merged = base_all.merge(cust_all, on=["CHR", "SNP", "BP"], how="inner")
    print(f"Inner-merged genome-wide: {merged.shape}\n")

    base_cols = [c for c in base_all.columns if c not in ("CHR", "SNP", "BP")]
    annot_cols = base_cols + cust_cols
    p = len(annot_cols)
    n = merged.shape[0]
    X = merged[annot_cols].to_numpy(dtype=np.float64)
    print(f"Genome-wide X shape: ({n}, {p})\n")

    # Quick SVD
    s = np.linalg.svd(X, compute_uv=False)
    s_max, s_min = s[0], s[-1]
    cond = s_max / s_min if s_min > 0 else np.inf
    rank = int(np.sum(s > s_max * 1e-10))
    print(f"σ_max = {s_max:.6e}  σ_min = {s_min:.6e}  cond = {cond:.6e}")
    print(f"rank @ σ_rel > 1e-10 = {rank} / {p}\n")

    print("Smallest 15 singular values (genome-wide):")
    for i, sv in enumerate(s[-15:]):
        idx = p - 15 + i
        print(f"  σ[{idx:3d}] = {sv:.6e}   relative: {sv / s_max:.6e}")

    # Per-column std on the genome-wide matrix
    print("\n=== Per-custom-annotation std on genome-wide X ===")
    cust_idx_start = len(base_cols)
    for i, name in enumerate(cust_cols):
        col = X[:, cust_idx_start + i]
        nz = int((col != 0).sum())
        print(f"  {name:<45}  std = {col.std():.6e}  nonzero SNPs = {nz}/{n}  "
              f"min={col.min():.3e} max={col.max():.3e}")


if __name__ == "__main__":
    per_chr_summary()
