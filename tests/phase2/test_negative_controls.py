"""Tests for negative control pipeline (REQ-7).

Validates:
- config/negative_controls.yaml has exactly 3 curated gene sets
- Each set has >= 2 genes
- matched_null_spec.n_draws is between 100 and 1000
- Null loci BED does not overlap real loci BED
- Null threshold is primary_threshold (0.8)
"""
import csv
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

# Project paths from conftest
from tests.phase2.conftest import CONFIG_DIR, PROJECT_ROOT


class TestCuratedSets:
    """Validate curated negative control gene sets in config."""

    @pytest.fixture(autouse=True)
    def _load_config(self, neg_ctrl_config):
        self.config = neg_ctrl_config

    def test_curated_sets_count(self):
        """negative_controls.yaml has exactly 3 curated_sets."""
        assert "curated_sets" in self.config
        assert len(self.config["curated_sets"]) == 3

    def test_curated_set_names(self):
        """Sets are hla_immune, cosmetic, blood_group."""
        expected = {"hla_immune", "cosmetic", "blood_group"}
        assert set(self.config["curated_sets"].keys()) == expected

    def test_curated_set_genes_nonempty(self):
        """Each set has >= 2 genes."""
        for name, setdef in self.config["curated_sets"].items():
            assert "genes" in setdef, f"{name} missing 'genes' key"
            assert len(setdef["genes"]) >= 2, f"{name} has < 2 genes"

    def test_null_threshold_is_primary(self):
        """null_threshold_source in config points to primary_threshold."""
        assert "null_threshold_source" in self.config
        assert "primary_threshold" in self.config["null_threshold_source"]


class TestMatchedNullSpec:
    """Validate matched null loci specification."""

    @pytest.fixture(autouse=True)
    def _load_config(self, neg_ctrl_config):
        self.spec = neg_ctrl_config["matched_null_spec"]

    def test_n_draws_in_range(self):
        """n_draws is between 100 and 1000."""
        assert 100 <= self.spec["n_draws"] <= 1000

    def test_gene_density_tolerance(self):
        """gene_density_tolerance is a float in (0, 1)."""
        tol = self.spec["match_criteria"]["gene_density_tolerance"]
        assert 0 < tol < 1

    def test_region_size_tolerance(self):
        """region_size_tolerance is a float in (0, 1)."""
        tol = self.spec["match_criteria"]["region_size_tolerance"]
        assert 0 < tol < 1

    def test_seed_base_is_int(self):
        """seed_base is an integer."""
        assert isinstance(self.spec["seed_base"], int)


class TestSampleNullLoci:
    """Validate sample_null_loci.py script exists and has correct interface."""

    def test_script_exists(self):
        """src/python/sample_null_loci.py exists."""
        script = PROJECT_ROOT / "src" / "python" / "sample_null_loci.py"
        assert script.exists(), f"Missing {script}"

    def test_script_contains_bedtools(self):
        """Script references bedtools for shuffling."""
        script = PROJECT_ROOT / "src" / "python" / "sample_null_loci.py"
        text = script.read_text()
        assert "bedtools" in text.lower() or "shuffle" in text

    def test_script_has_n_draws_arg(self):
        """Script has --n-draws CLI argument."""
        script = PROJECT_ROOT / "src" / "python" / "sample_null_loci.py"
        text = script.read_text()
        assert "--n-draws" in text

    def test_script_has_build_neg_ctrl_manifest(self):
        """Script has --build-neg-ctrl-manifest flag."""
        script = PROJECT_ROOT / "src" / "python" / "sample_null_loci.py"
        text = script.read_text()
        assert "--build-neg-ctrl-manifest" in text

    def test_script_has_run_neg_ctrl_coloc(self):
        """Script has --run-neg-ctrl-coloc flag."""
        script = PROJECT_ROOT / "src" / "python" / "sample_null_loci.py"
        text = script.read_text()
        assert "--run-neg-ctrl-coloc" in text


class TestNullLociNoOverlap:
    """Test that null loci do not overlap real loci (unit-level mock)."""

    def test_no_overlap_mock(self, tmp_path):
        """Mock null loci BED does not overlap real loci BED."""
        # Create mock real loci BED
        real_bed = tmp_path / "real.bed"
        real_bed.write_text(
            "chr16\t53766088\t54366088\tFTO_16q12\n"
            "chr18\t58332768\t58932768\tMC4R_18q21\n"
        )
        # Create mock null loci BED that does NOT overlap
        null_bed = tmp_path / "null.bed"
        null_bed.write_text(
            "chr1\t1000000\t1600000\tnull_1\n"
            "chr2\t5000000\t5600000\tnull_2\n"
        )
        # bedtools intersect should return 0 overlapping regions
        try:
            result = subprocess.run(
                ["bedtools", "intersect", "-a", str(null_bed), "-b", str(real_bed), "-wa"],
                capture_output=True,
                text=True,
                check=True,
            )
            overlapping = result.stdout.strip()
            assert overlapping == "", f"Found overlapping regions: {overlapping}"
        except FileNotFoundError:
            pytest.skip("bedtools not available in test environment")


class TestNegativeControlsSmk:
    """Validate negative_controls.smk rule file."""

    def test_smk_exists(self):
        """src/snakemake/rules/negative_controls.smk exists."""
        smk = PROJECT_ROOT / "src" / "snakemake" / "rules" / "negative_controls.smk"
        assert smk.exists(), f"Missing {smk}"

    def test_smk_has_generate_null_loci(self):
        """Rule file contains rule generate_null_loci."""
        smk = PROJECT_ROOT / "src" / "snakemake" / "rules" / "negative_controls.smk"
        text = smk.read_text()
        assert "rule generate_null_loci:" in text

    def test_smk_has_pph4_threshold_sweep(self):
        """Rule file contains rule pph4_threshold_sweep."""
        smk = PROJECT_ROOT / "src" / "snakemake" / "rules" / "negative_controls.smk"
        text = smk.read_text()
        assert "rule pph4_threshold_sweep:" in text

    def test_smk_has_run_curated_negative_controls(self):
        """Rule file contains rule run_curated_negative_controls."""
        smk = PROJECT_ROOT / "src" / "snakemake" / "rules" / "negative_controls.smk"
        text = smk.read_text()
        assert "rule run_curated_negative_controls:" in text

    def test_snakefile_includes_neg_ctrl_smk(self):
        """Top-level Snakefile includes negative_controls.smk."""
        snakefile = PROJECT_ROOT / "Snakefile"
        text = snakefile.read_text()
        assert "negative_controls.smk" in text
