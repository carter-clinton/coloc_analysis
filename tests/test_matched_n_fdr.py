"""Tests for BH-FDR correction across all 30 LDSC r_g tests (D-04c).

Multiple-testing correction: Benjamini-Hochberg FDR at q < 0.05 across ALL
r_g tests in the matrix (not per-ancestry-pair, not trait-pair-stratified).
Matches Phase 5 D-01a pathway FDR convention.

References:
    - D-04c: BH-FDR q < 0.05 across all 30 r_g tests
    - D-04a: 10 trait pairs x 3 ancestry-pair strata = 30 tests
    - config/matched_n.yaml: rg_fdr_q = 0.05
"""
import pytest


@pytest.mark.phase4
@pytest.mark.xfail(reason="Wave 0 stub — implementation in later plan")
def test_bh_fdr_across_30_tests():
    """Verify BH-FDR applied across ALL 30 r_g tests (10 pairs x 3 strata).

    D-04c: Single BH correction across entire matrix, not per-stratum.
    Uses config rg_fdr_q threshold. Bonferroni + per-stratum BH reported
    as supplementary robustness checks.
    """
    raise NotImplementedError("BH-FDR implementation pending Plan 04-04")
