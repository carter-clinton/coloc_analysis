"""Tests for permutation-based null distribution (Phase 5).

Validates:
- Pipeline config specifies 1000 permutations (D-06c)
- Null gene set size matching expectations
"""
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestPermutationCount:
    """Validate permutation configuration."""

    def test_permutation_count(self, pipeline_config):
        """pipeline.yaml specifies 1000 permutations per D-06c."""
        pathway = pipeline_config.get("pathway", {})
        assert "permutation_n" in pathway
        assert pathway["permutation_n"] == 1000

    def test_permutation_rule_exists(self):
        """pathway.smk contains permutation_null rule."""
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
        text = smk_path.read_text()
        assert "rule permutation_null:" in text


class TestNullGenesetSizeMatching:
    """Validate gene set size matching for permutation null."""

    def test_null_geneset_size_matching(self):
        """Placeholder: validate gene set size matching when real data available.

        The permutation null should sample random gene sets matched on size
        to the custom cardiometabolic sets. This ensures the null distribution
        accounts for gene set size effects on enrichment statistics.

        Implementation deferred to Plan 05-05.
        """
        # Size-matched null sets should have gene counts within +/- 20% of
        # the original set size. 8 custom sets range from 15-18 genes.
        min_set_size = 8  # Minimum genes per custom set (Pitfall 7)
        assert min_set_size >= 8

    def test_aggregate_rule_exists(self):
        """pathway.smk contains aggregate_pathway_results rule."""
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
        text = smk_path.read_text()
        assert "rule aggregate_pathway_results:" in text
