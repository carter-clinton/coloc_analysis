"""Tests for H7 pre-registered verdict logic (D-02d).

H7 decision rule: compare mean matched-N concordance (D-02a) to mean
unmatched concordance (EUR at full N). A >= 20 percentage-point absolute
reduction = "power artifact"; < 20 = "concordance is real, not a power
artifact."

Pre-registered threshold: OSF DOI 10.17605/OSF.IO/PVB5J, H7 line 102.

References:
    - D-02d: 20pp absolute reduction threshold
    - config/matched_n.yaml: h7_reduction_threshold_pp = 20
"""
import pytest


@pytest.mark.phase4
@pytest.mark.xfail(reason="Wave 0 stub — implementation in later plan")
def test_20pp_verdict():
    """Verify H7 verdict: >= 20pp drop = power artifact, < 20pp = concordance holds.

    D-02d: Pre-registered at 20 percentage-point absolute reduction.
    Must use config h7_reduction_threshold_pp, not hardcoded 20.
    """
    raise NotImplementedError("H7 verdict implementation pending Plan 04-03")
