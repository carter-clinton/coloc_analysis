"""Tests for per-locus NCP-based detection probability (D-05a/b/c/d).

Per-locus expected detection probability under the null: computed using
this study's T1 first-production Tier A beta/SE distribution as the
effect-size prior.

This is an ORIGINAL-RESEARCH CONSTRUCTION per RESEARCH B-2 resolution --
not attributable to a single prior paper.

References:
    - D-05a: Empirical beta/SE from T1 Tier A -> NCP -> detection prob
    - D-05b: Trait-level expected concordance = arithmetic mean of per-locus probs
    - D-05c: Hou et al. 2023 Table S1 parametric prior NOT used for primary
    - D-05d: Arithmetic mean aggregation across loci per trait
    - RESEARCH B-2: Original construction (not Hou 2023 radmix)
"""
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.python.compute_detection_probability import (
    GW_SIG_CHI2_THRESHOLD,
    per_locus_detection_prob,
    trait_expected_concordance,
)


@pytest.mark.phase4
class TestDetectionProbability:
    """Test suite for D-05 detection probability."""

    def test_ncp_from_empirical_beta_se(self):
        """Verify NCP = (beta/SE)^2 and detection probability = P(chi^2 >= T | NCP).

        D-05a: beta_hat=0.3, SE=0.05 -> NCP=36 -> ncx2.sf(~29.72, df=1, nc=36)
        Expected: ~0.78 (within 0.01 tolerance).
        """
        beta = np.array([0.3])
        se = np.array([0.05])
        ncp = (0.3 / 0.05) ** 2  # 36
        assert abs(ncp - 36.0) < 1e-10

        prob = per_locus_detection_prob(beta, se)
        expected = stats.ncx2.sf(GW_SIG_CHI2_THRESHOLD, df=1, nc=36)

        assert abs(prob[0] - expected) < 1e-10
        # NCP=36 at GW-sig threshold (~29.72) gives ~0.71 detection probability
        assert abs(prob[0] - 0.708) < 0.01, f"Expected ~0.708, got {prob[0]}"

    def test_trait_expected_concordance_arithmetic_mean(self):
        """Synthetic fixture: 3 loci per trait x 2 traits, known per-locus probs.

        D-05b/d: Trait-level = arithmetic mean of per-locus detection probs.
        """
        # Create synthetic data with known beta/SE
        data = {
            "trait": ["t2d"] * 3 + ["stroke"] * 3,
            "locus_id": ["loc1", "loc2", "loc3", "loc4", "loc5", "loc6"],
            "beta_afr": [0.3, 0.2, 0.4, 0.1, 0.5, 0.15],
            "se_afr": [0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
        }
        df = pd.DataFrame(data)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f_in:
            df.to_csv(f_in.name, sep="\t", index=False)
            with tempfile.NamedTemporaryFile(suffix=".tsv", delete=False) as f_out:
                result = trait_expected_concordance(f_in.name, f_out.name)

        assert len(result) == 2
        assert set(result["trait"]) == {"t2d", "stroke"}

        # Verify arithmetic mean for t2d
        t2d_betas = np.array([0.3, 0.2, 0.4])
        t2d_se = np.array([0.05, 0.05, 0.05])
        t2d_probs = per_locus_detection_prob(t2d_betas, t2d_se)
        t2d_expected = np.mean(t2d_probs)

        t2d_row = result[result["trait"] == "t2d"].iloc[0]
        assert t2d_row["n_tier_a_loci"] == 3
        np.testing.assert_allclose(
            t2d_row["expected_concordance_hou_null"], t2d_expected, rtol=1e-10
        )

    def test_empty_trait_raises_or_nan(self):
        """Trait with 0 Tier A loci -> either excluded or NaN concordance."""
        # Create data with only one trait
        data = {
            "trait": ["t2d", "t2d"],
            "locus_id": ["loc1", "loc2"],
            "beta_afr": [0.3, 0.2],
            "se_afr": [0.05, 0.05],
        }
        df = pd.DataFrame(data)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f_in:
            df.to_csv(f_in.name, sep="\t", index=False)
            with tempfile.NamedTemporaryFile(suffix=".tsv", delete=False) as f_out:
                result = trait_expected_concordance(f_in.name, f_out.name)

        # stroke should not appear (no rows -> excluded by groupby)
        assert "stroke" not in result["trait"].values

    def test_original_research_header(self):
        """Regression test: '# ORIGINAL-RESEARCH CONSTRUCTION' present in file."""
        script_path = Path(__file__).resolve().parent.parent / "src" / "python" / "compute_detection_probability.py"
        content = script_path.read_text()
        assert "# ORIGINAL-RESEARCH CONSTRUCTION" in content, (
            "Missing ORIGINAL-RESEARCH CONSTRUCTION header (D-05, RESEARCH B-2)"
        )

    def test_parametric_hou_not_used(self):
        """Regression test: 'Hou et al. 2023 Table S1 is NOT used' present."""
        script_path = Path(__file__).resolve().parent.parent / "src" / "python" / "compute_detection_probability.py"
        content = script_path.read_text()
        assert "Hou et al. 2023 Table S1 is NOT used" in content, (
            "Missing D-05c parametric-prior-exclusion statement"
        )

    def test_gwsig_threshold(self):
        """Verify genome-wide significance chi-square threshold is ~29.72."""
        expected = stats.chi2.ppf(1 - 5e-8, df=1)
        assert abs(GW_SIG_CHI2_THRESHOLD - expected) < 1e-6
        assert abs(GW_SIG_CHI2_THRESHOLD - 29.72) < 0.01

    def test_output_schema(self):
        """Output TSV must have columns: trait, n_tier_a_loci, expected_concordance_hou_null."""
        data = {
            "trait": ["t2d", "t2d", "stroke"],
            "locus_id": ["a", "b", "c"],
            "beta_afr": [0.3, 0.2, 0.4],
            "se_afr": [0.05, 0.05, 0.05],
        }
        df = pd.DataFrame(data)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f_in:
            df.to_csv(f_in.name, sep="\t", index=False)
            with tempfile.NamedTemporaryFile(suffix=".tsv", delete=False) as f_out:
                result = trait_expected_concordance(f_in.name, f_out.name)

        assert list(result.columns) == ["trait", "n_tier_a_loci", "expected_concordance_hou_null"]
