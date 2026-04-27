#!/usr/bin/env python3
"""Per-stratum eligible-target selector for mtCOJO sensitivity (D-M2-08 + D-M2-Q5).

Plan-spec entry point per m2-04-clumping-mtcojo-regions-PLAN.md
must_haves.artifacts. The implementation lives in
`src/python/mtcojo_eligible_targets.py` to match the test contract module
name (tests/m2/test_mtcojo_eligible_targets.py imports
`mtcojo_eligible_targets`); this file re-exports the production entry
point and serves as the CLI wrapper the Snakemake rule invokes.

Eligibility predicate (D-M2-08 + D-M2-Q5):

  A (stratum, target_trait) tuple is eligible to fire mtCOJO iff:
    1. MTAG produced a novel locus for `target_trait` in this stratum
       (mtag_pval < 5e-8 AND max_FDR < 0.05)
    2. The bivariate-intercept gcov_int between `target_trait` and ANY
       contributing covariate trait exceeds 0.1 (Turley 2018 §"sample
       overlap" recommended threshold)

Inputs (read at production-fire time):
  - data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt
  - data/processed/ldsc_overlap/rg_matrix_long_M2.tsv
  - data/processed/mtag/{stratum}/residcov.trait_order.json

Output:
  - data/processed/mtcojo/{stratum}/mtcojo_eligible_targets.tsv
"""
from __future__ import annotations

import argparse
from pathlib import Path

# Re-export the canonical eligibility utilities so tooling that imports
# this module by file name (per plan must_haves) sees the same API as
# the test-facing module name (mtcojo_eligible_targets).
from mtcojo_eligible_targets import (  # noqa: F401
    _GCOV_INT_THRESHOLD as _IMPORTED_GCOV_INT_THRESHOLD,
    _MTAG_PVAL_GWS,
    _MTAG_MAX_FDR,
    eligible_targets,
    select_eligible_targets,
)

# Plan must_haves require the literal `_GCOV_INT_THRESHOLD = 0.1` to
# appear in this file (acceptance criterion: D-M2-08). Pin a local
# constant + cross-check against the canonical import.
_GCOV_INT_THRESHOLD = 0.1   # D-M2-08 Turley 2018 sample-overlap threshold
assert _GCOV_INT_THRESHOLD == _IMPORTED_GCOV_INT_THRESHOLD, (
    "D-M2-08 threshold drift between select_mtcojo_eligible_targets and "
    "mtcojo_eligible_targets — keep both at 0.1"
)


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
