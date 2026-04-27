#!/usr/bin/env python3
"""mtCOJO extreme-overlap predicate (D-M2-08).

Per D-M2-08 (Turley 2018 §"sample overlap"): apply mtCOJO to every
MTAG-novel target trait where any contributing-trait gcov_int with the
target exceeds 0.1 (strict > threshold).

This module exports the boolean predicate consumed by:

  - tests/m2/test_mtcojo_extreme_overlap_filter.py (test contract)
  - src/python/mtcojo_eligible_targets.py (target-list builder)

Public API:

  has_extreme_overlap(target, trait_keys, R, threshold=0.1) -> bool
    Returns True iff any off-diagonal entry of R involving `target` has
    absolute value strictly greater than `threshold`.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np


_DEFAULT_THRESHOLD = 0.1   # D-M2-08 Turley 2018 recommended


def has_extreme_overlap(
    target: str,
    trait_keys: Sequence[str],
    R: np.ndarray,
    threshold: float = _DEFAULT_THRESHOLD,
) -> bool:
    """Return True if any off-diagonal R entry involving `target` exceeds threshold.

    Parameters
    ----------
    target : str
        Trait key whose row/column we probe.
    trait_keys : Sequence[str]
        Ordered trait keys aligned to the rows/cols of R.
    R : np.ndarray
        Symmetric K×K matrix; bivariate-intercept (gcov_int) values
        from the LDSC matrix slice for the relevant stratum.
    threshold : float
        Strict-greater threshold (D-M2-08 default = 0.1).

    Returns
    -------
    bool
        True iff max(|R[target, j]| for j != target) > threshold.

    Notes
    -----
    The test contract (test_threshold_boundary_exclusive) requires
    boundary-exclusive behavior: gcov_int = exactly 0.10 is NOT extreme.
    Hence the strict `>` comparison rather than `>=`.
    """
    if target not in trait_keys:
        return False
    R = np.asarray(R)
    if R.shape != (len(trait_keys), len(trait_keys)):
        raise ValueError(
            f"R shape {R.shape} mismatches len(trait_keys)={len(trait_keys)}"
        )
    i = trait_keys.index(target)
    others = [j for j in range(len(trait_keys)) if j != i]
    if not others:
        return False
    row = np.abs(R[i, others])
    return bool(np.any(row > threshold))


def max_overlapping_intercept(
    target: str,
    trait_keys: Sequence[str],
    R: np.ndarray,
) -> tuple[float, str]:
    """Return (max abs gcov_int with target, trait that achieves the max).

    Companion utility for mtcojo_eligible_targets — the eligibility
    selector needs both the boolean and the witness trait.
    """
    if target not in trait_keys:
        return 0.0, ""
    R = np.asarray(R)
    i = trait_keys.index(target)
    others = [j for j in range(len(trait_keys)) if j != i]
    if not others:
        return 0.0, ""
    row = np.abs(R[i, others])
    j = int(np.argmax(row))
    return float(row[j]), trait_keys[others[j]]
