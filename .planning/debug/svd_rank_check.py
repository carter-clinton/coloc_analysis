#!/usr/bin/env python3
"""Rank-deficiency analysis for the LDSC partitioned_h2 joint annotation matrix.

Replicates the matrix that LDSC sees just before
``check_ld_condition_number`` (sumstats.py:312-338) for one chromosome:
    X = [baseline LD scores (97 cols) | custom_pathway LD scores (11 cols)]
merged on SNP, then runs SVD + computes pairwise correlation between
custom_pathway columns and baselineLD columns.

The intent is to determine whether ``--invert-anyway`` failure
(LinAlgError: Singular matrix at jackknife.py:376) is caused by:
  (A) borderline numerical conditioning (cond high but rank == p), or
  (B) true rank deficiency (rank < p, so X^T X is singular regardless of
      forced inversion).

Outputs:
  1. Singular value spectrum + machine-epsilon-relative rank
  2. Top-correlated annotation pairs (custom × baseline) with |r| > 0.95
  3. Conditional number computed two ways (np.linalg.cond on X, on X^T X)
"""
import gzip
import sys

import numpy as np
import pandas as pd

CHROM = 22
BASELINE = (
    "/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/"
    f"data/reference/ldsc/baselineLD.{CHROM}.l2.ldscore.gz"
)
CUSTOM = (
    "/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/"
    f"results/pathway/ldsc_partitioned/ld_scores/custom_pathway.{CHROM}.l2.ldscore.gz"
)


def load_ldscores(path):
    df = pd.read_csv(path, sep="\t")
    return df


def main():
    print(f"=== Rank-deficiency analysis for chr{CHROM} ===\n")

    base = load_ldscores(BASELINE)
    cust = load_ldscores(CUSTOM)
    print(f"baseline LD scores: {base.shape} ({base.shape[1] - 3} annotations)")
    print(f"custom_pathway LD scores: {cust.shape} ({cust.shape[1] - 3} annotations)")

    # Match LDSC behavior: inner-join on SNP
    merged = base.merge(cust, on=["CHR", "SNP", "BP"], how="inner")
    print(f"\nAfter inner merge on (CHR,SNP,BP): {merged.shape}\n")

    base_cols = [c for c in base.columns if c not in ("CHR", "SNP", "BP")]
    cust_cols = [c for c in cust.columns if c not in ("CHR", "SNP", "BP")]
    annot_cols = base_cols + cust_cols
    p = len(annot_cols)
    n = merged.shape[0]
    X = merged[annot_cols].to_numpy(dtype=np.float64)
    print(f"X shape (n SNPs × p annotations): ({n}, {p})")
    print(f"  baseline annotations: {len(base_cols)}")
    print(f"  custom_pathway annotations: {len(cust_cols)}\n")

    # === 1. SVD of X directly ===
    print("=== Singular value decomposition of X ===")
    # full_matrices=False gives p singular values
    s = np.linalg.svd(X, compute_uv=False)
    s_max = s[0]
    s_min = s[-1]
    cond_X = s_max / s_min if s_min > 0 else np.inf
    print(f"  σ_max = {s_max:.6e}")
    print(f"  σ_min = {s_min:.6e}")
    print(f"  cond(X) = σ_max/σ_min = {cond_X:.6e}\n")

    # Numerical rank: count singular values above tolerance
    eps = np.finfo(np.float64).eps
    tol_default = max(X.shape) * s_max * eps  # numpy default
    rank_default = int(np.sum(s > tol_default))
    print("Numerical rank (numpy default tolerance "
          f"{tol_default:.3e}): {rank_default} / {p}")

    for tol_rel in [1e-6, 1e-8, 1e-10, 1e-12]:
        rank = int(np.sum(s > s_max * tol_rel))
        print(f"  rank @ σ > σ_max * {tol_rel:.0e}: {rank} / {p}")

    print("\n  Smallest 15 singular values (descending tail):")
    for i, sv in enumerate(s[-15:]):
        idx = p - 15 + i
        print(f"    σ[{idx:3d}] = {sv:.6e}   (relative to σ_max: {sv / s_max:.6e})")

    # === 2. cond(X^T X) — what LDSC actually inverts ===
    print("\n=== X^T X (the matrix LDSC tries to invert at jackknife.py:376) ===")
    XtX = X.T @ X
    cond_XtX = np.linalg.cond(XtX)
    rank_XtX = np.linalg.matrix_rank(XtX)
    print(f"  cond(X^T X) = {cond_XtX:.6e}")
    print(f"  rank(X^T X) (numpy default tol) = {rank_XtX} / {p}")

    # cond(X^T X) ≈ cond(X)^2 when X is full rank — sanity check
    print(f"  cond(X)^2 (for cross-check) = {cond_X ** 2:.6e}")

    # eigvalsh on the symmetric XtX
    w = np.linalg.eigvalsh(XtX)
    w = np.sort(w)
    print("\n  Smallest 10 eigenvalues of X^T X (ascending — negative = numerical floor):")
    for i in range(10):
        print(f"    λ[{i}] = {w[i]:.6e}")

    # === 3. Identify the rank-deficient direction(s) ===
    # Get the full SVD this time so we can inspect Vt (right singular vectors)
    # Only on a sub-sample if X is large; chr22 should be ~14k SNPs so OK
    print("\n=== Right singular vectors of the smallest singular values ===")
    print("(large absolute weights here flag the columns participating in "
          "the rank-deficient direction)\n")
    U, s_full, Vt = np.linalg.svd(X, full_matrices=False)
    # Look at smallest 3 singular vectors
    for k in range(3):
        idx = p - 1 - k
        print(f"--- σ[{idx}] = {s_full[idx]:.6e} ---")
        v = Vt[idx]  # right singular vector
        # Top-5 contributing columns by |weight|
        top = np.argsort(-np.abs(v))[:8]
        for j in top:
            kind = "BASE" if j < len(base_cols) else "CUST"
            col = annot_cols[j]
            print(f"   {kind}  v[{j:3d}] = {v[j]:+.5f}   {col}")
        print()

    # === 4. Pairwise Pearson r — custom × baseline ===
    print("=== Top |r| between custom_pathway columns and baselineLD columns ===")
    # Standardize each column
    Xs = (X - X.mean(axis=0)) / X.std(axis=0, ddof=0)
    Rmat = (Xs.T @ Xs) / n
    # Index ranges
    n_b = len(base_cols)
    n_c = len(cust_cols)
    # Block: rows = custom, cols = baseline
    R_cb = Rmat[n_b:, :n_b]
    print(f"R_cb shape: {R_cb.shape}\n")

    # Find all (custom, baseline) pairs with |r| > 0.95
    pairs = []
    for i in range(n_c):
        for j in range(n_b):
            r = R_cb[i, j]
            if abs(r) > 0.95:
                pairs.append((abs(r), r, cust_cols[i], base_cols[j]))
    pairs.sort(reverse=True)
    print(f"Found {len(pairs)} (custom, baseline) pairs with |r| > 0.95")
    print("Top 25 (by |r|):")
    for _, r, c, b in pairs[:25]:
        print(f"  r = {r:+.5f}   {c}   <->   {b}")

    # Also: max |r| per custom column
    print("\n=== Max |r| per custom_pathway column (against any baseline) ===")
    for i, c in enumerate(cust_cols):
        j = int(np.argmax(np.abs(R_cb[i])))
        print(f"  {c:50s}  max |r| = {abs(R_cb[i, j]):.4f}  vs  {base_cols[j]}")

    # === 5. Pairwise Pearson r — custom × custom (intra-block) ===
    print("\n=== Pairwise |r| between custom_pathway columns ===")
    R_cc = Rmat[n_b:, n_b:]
    pairs = []
    for i in range(n_c):
        for j in range(i + 1, n_c):
            r = R_cc[i, j]
            if abs(r) > 0.95:
                pairs.append((abs(r), r, cust_cols[i], cust_cols[j]))
    pairs.sort(reverse=True)
    print(f"Found {len(pairs)} custom × custom pairs with |r| > 0.95")
    for _, r, c1, c2 in pairs[:15]:
        print(f"  r = {r:+.5f}   {c1}   <->   {c2}")

    # === 6. Drop-one rank test: which custom annotation, when removed, restores rank? ===
    print("\n=== Drop-one rank test for custom_pathway columns ===")
    base_X = X[:, :n_b]
    rank_base = np.linalg.matrix_rank(base_X)
    print(f"  rank(baselineLD alone) = {rank_base} / {n_b}")
    rank_full = np.linalg.matrix_rank(X)
    print(f"  rank(baselineLD + custom_pathway) = {rank_full} / {p}")
    print(f"  expected if no rank drops: {p}; deficit = {p - rank_full}\n")

    print("  Per-custom-column drop test:")
    for i, c in enumerate(cust_cols):
        # X minus this custom column
        keep_cols = list(range(n_b)) + [n_b + j for j in range(n_c) if j != i]
        X_drop = X[:, keep_cols]
        r = np.linalg.matrix_rank(X_drop)
        marker = "<--- DROP RESTORES RANK" if r > rank_full - 1 else ""
        print(f"    drop {c:50s}  -> rank = {r} / {len(keep_cols)} {marker}")


if __name__ == "__main__":
    main()
