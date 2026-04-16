"""Tests for Tier A retention concordance metric (D-02a).

Primary metric: Fraction of AFR-discovered Tier A loci for which the
EUR-matched bootstrap median achieves Tier A (PP.H4 >= 0.8 AND at least
one QTL coloc >= 0.8). Computed per trait with 95% CI from bootstrap
distribution.

References:
    - D-02a: Primary concordance metric definition
    - D-02d: H7 pre-registered threshold (20pp absolute reduction)
"""
import pytest


@pytest.mark.phase4
@pytest.mark.xfail(reason="Wave 0 stub — implementation in later plan")
def test_bootstrap_median_tier_a():
    """Verify bootstrap median Tier A retention computation.

    D-02a: For each trait, compute fraction of AFR Tier A loci where
    EUR-matched bootstrap median PP.H4 >= concordance_threshold AND
    at least one QTL coloc >= concordance_threshold. Report with 95% CI.
    """
    raise NotImplementedError("Tier A retention implementation pending Plan 04-03")
