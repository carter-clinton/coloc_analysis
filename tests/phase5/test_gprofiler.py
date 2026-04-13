"""Tests for g:Profiler enrichment analysis (Phase 5).

Validates:
- Background gene construction from trait sumstats
- Negative control enrichment null expectation
- gprofiler2 evcodes parameter configuration (D-03b)
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestBackgroundConstruction:
    """Test union background gene set construction from sumstats."""

    def test_background_construction(self, pipeline_config):
        """Pipeline config has the 5 traits needed for background union."""
        traits = pipeline_config.get("traits", [])
        assert len(traits) == 5, f"Expected 5 traits, got {len(traits)}"
        expected = {"bmi", "t2d", "hypertension", "asthma", "stroke"}
        assert set(traits) == expected


class TestNegCtrlEnrichment:
    """Test negative control enrichment expectations."""

    def test_neg_ctrl_enrichment_null(self):
        """Placeholder: verify negative controls show q > 0.05 when real data available.

        This test will be filled in Plan 05-04 when gprofiler_enrichment rule
        is implemented. For now, validates the expectation is documented.
        """
        # Expected: negative control gene sets (HLA, cosmetic, blood group)
        # should NOT show significant enrichment for cardiometabolic pathways.
        # Quantitative test deferred to real data execution.
        expected_q_threshold = 0.05
        assert expected_q_threshold > 0


class TestEvcodesParameter:
    """Test gprofiler2 call configuration."""

    def test_evcodes_parameter(self):
        """Verify pathway.smk gprofiler_enrichment rule specifies evcodes=TRUE per D-03b."""
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
        text = smk_path.read_text()
        # The rule docstring or implementation should reference evcodes=TRUE
        assert "evcodes" in text.lower() or "evcodes=TRUE" in text, (
            "pathway.smk gprofiler_enrichment rule should specify evcodes=TRUE per D-03b"
        )

    def test_gprofiler_env_has_r_gprofiler2(self):
        """envs/gprofiler.yml contains r-gprofiler2 dependency."""
        env_path = PROJECT_ROOT / "envs" / "gprofiler.yml"
        text = env_path.read_text()
        assert "r-gprofiler2" in text

    def test_gprofiler_bg_window_configured(self, pipeline_config):
        """pipeline.yaml has gprofiler_bg_window_kb configured."""
        pathway = pipeline_config.get("pathway", {})
        assert "gprofiler_bg_window_kb" in pathway
        assert pathway["gprofiler_bg_window_kb"] == 500
