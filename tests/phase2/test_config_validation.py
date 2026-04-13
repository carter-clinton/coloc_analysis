"""Tests for Phase 2 config file validation.

Validates that pph4_thresholds.yaml, negative_controls.yaml, and
qtl_sources.yaml load correctly and contain the required schema.
All YAML loading uses yaml.safe_load() per T-02-02 mitigation.
"""
import pytest
import yaml
from pathlib import Path


class TestPph4Thresholds:
    """Validate config/pph4_thresholds.yaml."""

    def test_loads_without_error(self, pph4_config):
        assert pph4_config is not None

    def test_primary_threshold(self, pph4_config):
        assert pph4_config["primary_threshold"] == 0.8

    def test_sweep_values(self, pph4_config):
        assert pph4_config["sweep_values"] == [0.5, 0.7, 0.8, 0.9]

    def test_tier_definitions_present(self, pph4_config):
        tiers = pph4_config.get("tier_definitions", {})
        assert "tier_a" in tiers
        assert "tier_b" in tiers
        assert "tier_c" in tiers

    def test_tier_a_thresholds(self, pph4_config):
        tier_a = pph4_config["tier_definitions"]["tier_a"]
        assert tier_a["min_pph4_gwas"] == 0.8
        assert tier_a["min_pph4_qtl"] == 0.8


class TestNegativeControls:
    """Validate config/negative_controls.yaml."""

    def test_loads_without_error(self, neg_ctrl_config):
        assert neg_ctrl_config is not None

    def test_exactly_3_curated_sets(self, neg_ctrl_config):
        curated = neg_ctrl_config.get("curated_sets", {})
        assert len(curated) == 3, f"Expected 3 curated sets, got {len(curated)}"

    def test_required_set_names(self, neg_ctrl_config):
        curated = neg_ctrl_config["curated_sets"]
        required = {"hla_immune", "cosmetic", "blood_group"}
        assert set(curated.keys()) == required

    def test_each_set_has_genes(self, neg_ctrl_config):
        for name, spec in neg_ctrl_config["curated_sets"].items():
            assert "genes" in spec, f"Set '{name}' missing 'genes' key"
            assert isinstance(spec["genes"], list), (
                f"Set '{name}' genes should be a list"
            )
            assert len(spec["genes"]) > 0, f"Set '{name}' has empty genes list"

    def test_matched_null_spec(self, neg_ctrl_config):
        null_spec = neg_ctrl_config.get("matched_null_spec")
        assert null_spec is not None, "Missing matched_null_spec"
        assert "n_draws" in null_spec
        assert 100 <= null_spec["n_draws"] <= 1000, (
            f"n_draws={null_spec['n_draws']} outside [100, 1000]"
        )

    def test_safe_load_used(self, config_dir):
        """Verify YAML is loadable via safe_load (T-02-02 mitigation)."""
        path = config_dir / "negative_controls.yaml"
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data is not None


class TestQtlSources:
    """Validate config/qtl_sources.yaml."""

    def test_loads_without_error(self, qtl_sources_config):
        assert qtl_sources_config is not None

    def test_has_4_sources(self, qtl_sources_config):
        sources = qtl_sources_config.get("sources", {})
        assert len(sources) == 4, f"Expected 4 QTL sources, got {len(sources)}"

    def test_required_source_names(self, qtl_sources_config):
        sources = qtl_sources_config["sources"]
        required = {"gtex_eqtl", "gtex_sqtl", "ukbppp_pqtl", "onek1k_sceqtl"}
        assert set(sources.keys()) == required

    def test_all_genome_build_grch38(self, qtl_sources_config):
        for name, spec in qtl_sources_config["sources"].items():
            assert spec.get("genome_build") == "GRCh38", (
                f"Source '{name}' genome_build should be GRCh38, "
                f"got {spec.get('genome_build')}"
            )

    def test_each_source_has_columns(self, qtl_sources_config):
        for name, spec in qtl_sources_config["sources"].items():
            assert "columns" in spec, f"Source '{name}' missing 'columns' key"
            cols = spec["columns"]
            assert "beta" in cols or "BETA" in cols, (
                f"Source '{name}' missing beta column mapping"
            )

    def test_safe_load_all_configs(self, config_dir):
        """Verify all 3 new YAML config files load via safe_load."""
        for name in ["pph4_thresholds.yaml", "negative_controls.yaml", "qtl_sources.yaml"]:
            path = config_dir / name
            assert path.exists(), f"Config file {name} does not exist"
            with open(path) as f:
                data = yaml.safe_load(f)
            assert data is not None, f"Config file {name} loaded as None"
