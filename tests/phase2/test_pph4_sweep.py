"""Tests for PP.H4 threshold sweep logic (REQ-3).

Validates:
- Sweep at exactly {0.5, 0.7, 0.8, 0.9}
- Tier count monotonicity
- Primary threshold is 0.8
- Output has ancestry column
- Output includes all tiers
"""
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

from tests.phase2.conftest import CONFIG_DIR, PROJECT_ROOT

# Import assign_tiers functions after they are created
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))


class TestSweepConfig:
    """Validate PP.H4 sweep configuration."""

    @pytest.fixture(autouse=True)
    def _load_config(self, pph4_config):
        self.config = pph4_config

    def test_sweep_values_match_config(self):
        """Sweep at exactly {0.5, 0.7, 0.8, 0.9}."""
        expected = [0.5, 0.7, 0.8, 0.9]
        assert self.config["sweep_values"] == expected

    def test_primary_threshold_is_0_8(self):
        """primary_threshold == 0.8."""
        assert self.config["primary_threshold"] == 0.8

    def test_tier_definitions_present(self):
        """tier_definitions has tier_a, tier_b, tier_c."""
        td = self.config["tier_definitions"]
        assert "tier_a" in td
        assert "tier_b" in td
        assert "tier_c" in td


class TestSweepLogic:
    """Test PP.H4 sweep logic using assign_tiers module functions."""

    @pytest.fixture
    def mock_results(self):
        """Create mock QTL coloc results with known PP.H4 values."""
        rows = []
        # 10 loci with varying PP.H4 values
        pph4_values = [0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.05]
        for i, pph4 in enumerate(pph4_values):
            rows.append({
                "region": f"region_{i}",
                "ancestry": "EUR",
                "qtl_source": "gtex_eqtl",
                "tissue": f"tissue_{i}",
                "gene_id": f"ENSG{i:011d}",
                "PP.H4.abf": pph4,
            })
        return pd.DataFrame(rows)

    def test_tier_count_monotonicity(self, mock_results, pph4_config):
        """Tier count at 0.5 >= at 0.7 >= at 0.8 >= at 0.9 (monotonicity)."""
        from assign_tiers import sweep_tiers

        sweep_df = sweep_tiers(mock_results, pph4_config["sweep_values"])

        # Group by threshold and count rows passing each
        for ancestry in sweep_df["ancestry"].unique():
            anc_df = sweep_df[sweep_df["ancestry"] == ancestry]
            prev_total = None
            for threshold in sorted(pph4_config["sweep_values"]):
                row = anc_df[anc_df["threshold"] == threshold]
                if len(row) > 0:
                    total = row.iloc[0].get("n_tier_a", 0) + row.iloc[0].get("n_tier_b", 0)
                    if prev_total is not None:
                        assert total <= prev_total, (
                            f"Monotonicity violated: threshold {threshold} "
                            f"has {total} > {prev_total}"
                        )
                    prev_total = total

    def test_sweep_output_has_ancestry_column(self, mock_results, pph4_config):
        """Sweep table has an ancestry column for per-ancestry reporting."""
        from assign_tiers import sweep_tiers

        sweep_df = sweep_tiers(mock_results, pph4_config["sweep_values"])
        assert "ancestry" in sweep_df.columns

    def test_sweep_produces_all_tiers(self, mock_results, pph4_config):
        """Output table has columns for Tier A, Tier B, and Tier C counts."""
        from assign_tiers import sweep_tiers

        sweep_df = sweep_tiers(mock_results, pph4_config["sweep_values"])
        assert "n_tier_a" in sweep_df.columns
        assert "n_tier_b" in sweep_df.columns
        assert "n_tier_c" in sweep_df.columns

    def test_sweep_produces_4_thresholds(self, mock_results, pph4_config):
        """Sweep output has rows for each of 4 thresholds."""
        from assign_tiers import sweep_tiers

        sweep_df = sweep_tiers(mock_results, pph4_config["sweep_values"])
        thresholds = sorted(sweep_df["threshold"].unique())
        assert thresholds == [0.5, 0.7, 0.8, 0.9]
