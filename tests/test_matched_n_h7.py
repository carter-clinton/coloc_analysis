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

from src.python.assemble_table2 import compute_h7_verdict


@pytest.mark.phase4
class TestH7Verdict:
    """D-02d: H7 verdict with 20pp absolute reduction threshold."""

    def test_h7_power_artifact(self):
        """unmatched=60%, matched=35% -> reduction=25pp >= 20pp -> power_artifact."""
        assert compute_h7_verdict(35.0, 60.0, threshold_pp=20.0) == "power_artifact"

    def test_h7_concordance_holds(self):
        """unmatched=60%, matched=45% -> reduction=15pp < 20pp -> concordance_holds."""
        assert compute_h7_verdict(45.0, 60.0, threshold_pp=20.0) == "concordance_holds"

    def test_h7_exact_boundary(self):
        """reduction=20.0pp exactly -> power_artifact (>= semantics)."""
        assert compute_h7_verdict(40.0, 60.0, threshold_pp=20.0) == "power_artifact"

    def test_h7_no_reduction(self):
        """matched >= unmatched -> no reduction -> concordance_holds."""
        assert compute_h7_verdict(65.0, 60.0, threshold_pp=20.0) == "concordance_holds"

    def test_h7_negative_reduction(self):
        """matched > unmatched (negative reduction) -> concordance_holds."""
        assert compute_h7_verdict(80.0, 60.0, threshold_pp=20.0) == "concordance_holds"

    def test_h7_zero_reduction(self):
        """Both equal -> reduction=0pp -> concordance_holds."""
        assert compute_h7_verdict(60.0, 60.0, threshold_pp=20.0) == "concordance_holds"

    def test_h7_custom_threshold(self):
        """Threshold from config (not hardcoded 20): 10pp threshold."""
        # 15pp reduction >= 10pp threshold -> power_artifact
        assert compute_h7_verdict(45.0, 60.0, threshold_pp=10.0) == "power_artifact"
        # 5pp reduction < 10pp threshold -> concordance_holds
        assert compute_h7_verdict(55.0, 60.0, threshold_pp=10.0) == "concordance_holds"
