"""Tests for matched-N SE-inflation formula (D-01a) and bootstrap Z resampling (D-01b).

SE-inflation rescaling: SE_EUR_matched = SE_EUR * sqrt(N_EUR / N_AFR)
This is the analytic mechanism for cross-ancestry power matching.

References:
    - D-01a: EUR matched to AFR-N via analytic SE rescaling
    - D-01b: Per-bootstrap Z_b ~ N(beta_hat/SE_matched, 1) independent draws
    - Mahajan et al. 2022 DIAMANTE (Nat Genet 54:560) Methods
    - Zou et al. 2022 SuSiE-RSS (PLOS Genet PMC9337707)
"""
import sys
from pathlib import Path

import numpy as np
import pytest

# Project convention: sys.path.insert for flat-name imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "python"))

from se_inflation import (
    compute_seed,
    draw_z_bootstrap,
    inflate_se,
    reconstruct_pseudo_sumstats,
)


@pytest.mark.phase4
class TestInflateSE:
    """D-01a: SE_EUR_matched = SE_EUR * sqrt(N_EUR / N_AFR)."""

    def test_inflate_se_identity_when_n_equal(self):
        """When N_EUR == N_AFR, factor = 1.0 -> SE unchanged."""
        se = np.array([0.01, 0.02, 0.05])
        result = inflate_se(se, n_eur=100_000, n_afr=100_000)
        np.testing.assert_allclose(result, se, rtol=1e-10)

    def test_inflate_se_scales_correctly(self):
        """N_EUR=700k, N_AFR=55525 -> factor = sqrt(700000/55525) ~ 3.55."""
        se = np.array([0.01, 0.02, 0.05])
        n_eur = 700_000
        n_afr = 55_525
        expected_factor = np.sqrt(n_eur / n_afr)
        result = inflate_se(se, n_eur=n_eur, n_afr=n_afr)
        np.testing.assert_allclose(result, se * expected_factor, rtol=1e-10)
        assert np.isclose(expected_factor, np.sqrt(700000 / 55525))

    def test_inflate_se_raises_on_zero_n_afr(self):
        """N_AFR=0 -> ValueError."""
        se = np.array([0.01])
        with pytest.raises(ValueError, match="both must be positive"):
            inflate_se(se, n_eur=100_000, n_afr=0)

    def test_inflate_se_raises_on_negative_n(self):
        """Negative N -> ValueError."""
        se = np.array([0.01])
        with pytest.raises(ValueError, match="both must be positive"):
            inflate_se(se, n_eur=-100, n_afr=50_000)

    def test_inflate_se_raises_when_afr_exceeds_eur(self):
        """N_AFR > N_EUR -> ValueError (matched-N only inflates, never shrinks)."""
        se = np.array([0.01])
        with pytest.raises(ValueError, match="Matched-N requires"):
            inflate_se(se, n_eur=50_000, n_afr=100_000)


@pytest.mark.phase4
class TestDrawZBootstrap:
    """D-01b: Z_b ~ N(beta_hat / SE_matched, 1) per variant."""

    def test_draw_z_determinism(self):
        """Same seed -> identical Z draws."""
        beta = np.array([0.1, -0.05, 0.3])
        se = np.array([0.02, 0.03, 0.01])
        z1 = draw_z_bootstrap(beta, se, seed=42)
        z2 = draw_z_bootstrap(beta, se, seed=42)
        np.testing.assert_array_equal(z1, z2)

    def test_draw_z_different_seeds(self):
        """Different seeds -> different Z draws."""
        beta = np.array([0.1, -0.05, 0.3])
        se = np.array([0.02, 0.03, 0.01])
        z1 = draw_z_bootstrap(beta, se, seed=42)
        z2 = draw_z_bootstrap(beta, se, seed=43)
        assert not np.array_equal(z1, z2)


@pytest.mark.phase4
class TestReconstructPseudoSumstats:
    """D-01b: beta_b = Z_b * SE_matched, se_b = SE_matched."""

    def test_reconstruct_pseudo_sumstats(self):
        """Pseudo-sumstats reconstruction is correct."""
        z = np.array([5.0, -2.0, 10.0])
        se = np.array([0.02, 0.03, 0.01])
        beta_b, se_b = reconstruct_pseudo_sumstats(z, se)
        np.testing.assert_allclose(beta_b, z * se, rtol=1e-10)
        np.testing.assert_array_equal(se_b, se)


@pytest.mark.phase4
class TestComputeSeed:
    """Seed determinism: seed = seed_base * trait_id + bootstrap_idx."""

    def test_compute_seed_formula(self):
        """compute_seed(3, 7, 1000) == 3007."""
        assert compute_seed(trait_id=3, bootstrap_idx=7, seed_base=1000) == 3007

    def test_compute_seed_zero_trait(self):
        """compute_seed(0, 1) == 1."""
        assert compute_seed(trait_id=0, bootstrap_idx=1) == 1

    def test_compute_seed_custom_base(self):
        """compute_seed(2, 50, seed_base=500) == 1050."""
        assert compute_seed(trait_id=2, bootstrap_idx=50, seed_base=500) == 1050
