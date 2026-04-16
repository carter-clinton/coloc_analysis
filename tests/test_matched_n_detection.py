"""Tests for per-locus NCP-based detection probability (D-05a).

Per-locus expected detection probability under the null: computed using
this study's T1 first-production Tier A beta/SE distribution as the
effect-size prior. For each AFR Tier A locus with observed beta_AFR,
compute NCP = (beta/SE)^2 at N_EUR_matched, then the analytic
P(chi^2 >= threshold | NCP) detection probability.

This is an original-research construction per RESEARCH B-2 resolution —
not attributable to a single prior paper.

References:
    - D-05a: Empirical beta/SE from T1 Tier A
    - D-05b: Trait-level expected concordance = arithmetic mean of per-locus probs
    - RESEARCH B-2: Original construction (not Hou 2023 radmix)
"""
import pytest


@pytest.mark.phase4
@pytest.mark.xfail(reason="Wave 0 stub — implementation in later plan")
def test_ncp_from_empirical_beta_se():
    """Verify NCP = (beta/SE)^2 and detection probability = P(chi^2 >= T | NCP).

    D-05a: Per-locus detection probability computed from empirical beta/SE.
    Original-research construction per RESEARCH B-2 resolution.
    """
    raise NotImplementedError("NCP detection probability implementation pending Plan 04-04")
