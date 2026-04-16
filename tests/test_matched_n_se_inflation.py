"""Tests for matched-N SE-inflation formula (D-01a).

SE-inflation rescaling: SE_EUR_matched = SE_EUR * sqrt(N_EUR / N_AFR)
This is the analytic mechanism for cross-ancestry power matching.

References:
    - D-01a: EUR matched to AFR-N via analytic SE rescaling
    - Mahajan et al. 2022 DIAMANTE (Nat Genet 54:560) Methods
    - Zou et al. 2022 SuSiE-RSS (PLOS Genet PMC9337707)
"""
import pytest


@pytest.mark.phase4
@pytest.mark.xfail(reason="Wave 0 stub — implementation in later plan")
def test_se_inflation_formula():
    """Verify SE_EUR_matched = SE_EUR * sqrt(N_EUR / N_AFR).

    D-01a: N_AFR is trait-specific (per-trait N_eff from harmonized sumstats).
    The match is per-trait, not per-study.
    """
    raise NotImplementedError("SE-inflation implementation pending Plan 04-02")
