#!/usr/bin/env python3
"""CPASSOC SHom + SHet test statistics (Zhu 2015 *AJHG* 96:21-36).

M2 plan reference: m2-03-cpassoc-3-strata-PLAN.md (consumer); landed at Wave 0
by m2-00-preflight-and-environment-PLAN.md Task 6.

Decision references:
  D-M2-04 — Python reimplementation with the LDSC bivariate-intercept matrix
            from M1 (re-fired in D-M2-01 to ~26-trait) as the cohort-correlation
            matrix R. Mathematically equivalent to Zhu's null-SNP empirical R
            (Bulik-Sullivan derivation), already estimated and frozen.
  D-M2-Q2 — numpy.linalg.pinv with conditional ridge fallback when cond > 1e6.

Formulas (per Zhu 2015 Methods):

  SHom = z' R^-1 z
       (chi-square df = K; tests homogeneous pleiotropic effect)

  SHet = z' (R^-1 - R^-1 1 (1' R^-1 1)^-1 1' R^-1) z
       (chi-square df = K - 1; tests heterogeneous pleiotropic effect)

where R is the cohort-correlation matrix and z is the per-SNP K-vector of
trait z-scores. The K traits feeding into a single CPASSOC run are the
stratum-matched traits per D-M2-06.

Per D-M2-Q5 + D-M2-08 the downstream consumers (mtCOJO eligibility, Class 1
novelty) read the SHom/SHet outputs alongside MTAG `--residcov_path` results.
Class 1 high-confidence novelty = MTAG ∩ CPASSOC per Amendment §7.1.
"""
from __future__ import annotations

import numpy as np

_COND_THRESHOLD = 1e6
_RIDGE_FLOOR_DEFAULT = 1e-4
_PINV_RCOND = 1e-15


def _safe_inverse(R: np.ndarray, ridge_floor: float = _RIDGE_FLOOR_DEFAULT) -> np.ndarray:
    """Pseudoinverse with conditional ridge fallback for near-singular R.

    Per D-M2-Q2: if cond(R) > _COND_THRESHOLD (1e6), apply ridge
    regularization R + λI where λ = ridge_floor * trace(R) / K BEFORE
    the pseudoinverse. Otherwise return numpy.linalg.pinv(R) directly.

    Defensive symmetry guard: R = (R + R.T) / 2 before inversion to
    suppress numerical drift in upstream LDSC matrix derivation.

    Parameters
    ----------
    R : np.ndarray, shape (K, K)
        Cohort-correlation matrix (LDSC bivariate-intercept).
    ridge_floor : float
        λ multiplier applied to trace(R)/K when ridge fallback fires.
        Default 1e-4.

    Returns
    -------
    np.ndarray, shape (K, K)
        Pseudoinverse (with optional ridge regularization for ill-conditioned R).
    """
    R = (R + R.T) / 2.0  # defensive symmetry guard
    cond = float(np.linalg.cond(R))
    if cond > _COND_THRESHOLD:
        K = R.shape[0]
        lam = ridge_floor * float(np.trace(R)) / K
        R = R + lam * np.eye(K)
    return np.linalg.pinv(R, rcond=_PINV_RCOND)


def cpassoc_shom(z: np.ndarray, R: np.ndarray) -> np.ndarray:
    """SHom test statistic per SNP. Returns chi-square df=K values.

    Parameters
    ----------
    z : np.ndarray, shape (n_snps, K)
        Per-SNP K-trait z-score matrix.
    R : np.ndarray, shape (K, K)
        Cohort-correlation matrix (LDSC bivariate-intercept).

    Returns
    -------
    np.ndarray, shape (n_snps,)
        SHom chi-square statistic per SNP (df = K).

    Raises
    ------
    ValueError
        If z is not 2D, or R is not square, or z.shape[1] != R.shape[0].
    """
    if z.ndim != 2:
        raise ValueError(f"z must be 2D (n_snps, K), got shape {z.shape}")
    if R.shape[0] != R.shape[1]:
        raise ValueError(f"R must be square, got shape {R.shape}")
    if z.shape[1] != R.shape[0]:
        raise ValueError(f"K mismatch: z has K={z.shape[1]}, R is {R.shape}")
    Rinv = _safe_inverse(R)
    return np.einsum("ij,jk,ik->i", z, Rinv, z)


def cpassoc_shet(z: np.ndarray, R: np.ndarray) -> np.ndarray:
    """SHet test statistic per SNP. Returns chi-square df=K-1 values.

    Tests heterogeneous pleiotropic effect by projecting out the homogeneous
    component (1'R^-1 z direction) before quadratic-form computation.

    Parameters
    ----------
    z : np.ndarray, shape (n_snps, K)
        Per-SNP K-trait z-score matrix.
    R : np.ndarray, shape (K, K)
        Cohort-correlation matrix.

    Returns
    -------
    np.ndarray, shape (n_snps,)
        SHet chi-square statistic per SNP (df = K - 1).

    Raises
    ------
    ValueError
        If z is not 2D, or R is not square, or z.shape[1] != R.shape[0].
    """
    if z.ndim != 2:
        raise ValueError(f"z must be 2D (n_snps, K), got shape {z.shape}")
    if R.shape[0] != R.shape[1]:
        raise ValueError(f"R must be square, got shape {R.shape}")
    if z.shape[1] != R.shape[0]:
        raise ValueError(f"K mismatch: z has K={z.shape[1]}, R is {R.shape}")
    Rinv = _safe_inverse(R)
    K = R.shape[0]
    one = np.ones(K)
    denom = float(one @ Rinv @ one)
    proj = Rinv - np.outer(Rinv @ one, one @ Rinv) / denom
    return np.einsum("ij,jk,ik->i", z, proj, z)
