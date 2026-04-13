#!/usr/bin/env python3
"""Estimate sdY from summary statistics for non-unit-variance QTL data.

Implements the formula from coloc::est_sdY (Wallace, github.com/chr1swallace/coloc):
    sdY = sqrt(median(2 * maf * (1 - maf) * (N * varbeta + beta^2)))

Used for UKB-PPP pQTL where Olink NPX values may not be unit-variance
(Open Question 1 from RESEARCH.md). The estimated sdY is passed to
run_qtl_coloc.R via --sdy.
"""

import argparse
import logging

import numpy as np

logger = logging.getLogger(__name__)


def estimate_sdy(beta: np.ndarray, se: np.ndarray, maf: np.ndarray, n: int) -> float:
    """Estimate sdY from summary statistics.

    Implements the coloc::est_sdY formula:
        sdY = sqrt(median(2 * maf * (1 - maf) * (N * se^2 + beta^2)))

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

    Raises
    ------
    ValueError
        If inputs are empty or have incompatible shapes.
    """
    beta = np.asarray(beta, dtype=float)
    se = np.asarray(se, dtype=float)
    maf = np.asarray(maf, dtype=float)

    if len(beta) == 0:
        raise ValueError("Cannot estimate sdY from empty arrays")

    if not (len(beta) == len(se) == len(maf)):
        raise ValueError(
            f"Input arrays must have equal length: "
            f"beta={len(beta)}, se={len(se)}, maf={len(maf)}"
        )

    varbeta = se ** 2
    # coloc::est_sdY formula
    per_snp = 2 * maf * (1 - maf) * (n * varbeta + beta ** 2)

    # Filter to valid (positive, finite) values
    valid = np.isfinite(per_snp) & (per_snp > 0)
    if valid.sum() == 0:
        logger.warning("No valid per-SNP sdY estimates; returning 1.0 as fallback")
        return 1.0

    sdy = float(np.sqrt(np.median(per_snp[valid])))

    if sdy <= 0 or not np.isfinite(sdy):
        logger.warning("sdY estimate non-positive or non-finite (%s); returning 1.0", sdy)
        return 1.0

    return sdy


def main():
    parser = argparse.ArgumentParser(
        description="Estimate sdY from summary statistics"
    )
    parser.add_argument("--beta", required=True, help="Comma-separated beta values")
    parser.add_argument("--se", required=True, help="Comma-separated SE values")
    parser.add_argument("--maf", required=True, help="Comma-separated MAF values")
    parser.add_argument("--n", required=True, type=int, help="Sample size")

    args = parser.parse_args()

    beta = np.array([float(x) for x in args.beta.split(",")])
    se = np.array([float(x) for x in args.se.split(",")])
    maf = np.array([float(x) for x in args.maf.split(",")])

    sdy = estimate_sdy(beta=beta, se=se, maf=maf, n=args.n)
    print(f"Estimated sdY = {sdy:.6f}")


if __name__ == "__main__":
    main()
