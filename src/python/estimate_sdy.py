#!/usr/bin/env python3
"""Estimate sdY from summary statistics for non-unit-variance QTL data.

Implements the formula from coloc::est_sdY (Wallace, github.com/chr1swallace/coloc):
    sdY = sqrt(median(2 * maf * (1 - maf) * (N * varbeta + beta^2)))

Used for UKB-PPP pQTL where Olink NPX values may not be unit-variance.
"""

import numpy as np


def estimate_sdy(beta: np.ndarray, se: np.ndarray, maf: np.ndarray, n: int) -> float:
    """Estimate sdY from summary statistics.

    Parameters
    ----------
    beta : np.ndarray
        Effect sizes.
    se : np.ndarray
        Standard errors.
    maf : np.ndarray
        Minor allele frequencies.
    n : int
        Sample size.

    Returns
    -------
    float
        Estimated standard deviation of the phenotype (sdY).
    """
    raise NotImplementedError("RED phase stub")
