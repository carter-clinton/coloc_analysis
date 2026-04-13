"""Tests for OneK1K sc-eQTL harmonization and download (02-04 Task 1).

Covers:
- harmonize_onek1k.py: reads sceqtl_mock.tsv.gz and outputs common intermediate TSV
- download_onek1k.py: has fallback logic for eQTL Catalogue + onek1k.org
- config/qtl_sources.yaml: contains exactly 14 cell types
"""
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

# Ensure src/python is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))


@pytest.fixture(scope="module")
def sceqtl_mock_path():
    return PROJECT_ROOT / "tests" / "toy_3locus" / "data" / "qtl" / "sceqtl_mock.tsv.gz"


@pytest.fixture(scope="module")
def qtl_sources_config():
    with open(PROJECT_ROOT / "config" / "qtl_sources.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def harmonized_df(sceqtl_mock_path, qtl_sources_config):
    """Run harmonize_onek1k on the mock fixture for gene ENSG00000140718 in FTO region."""
    from harmonize_onek1k import harmonize_onek1k

    result = harmonize_onek1k(
        input_path=str(sceqtl_mock_path),
        cell_type="Mono_C",
        region={"chr": "16", "start": 53766088, "end": 54366088},
        gene_id="ENSG00000140718",
        source_format="eqtl_catalogue",
        config=qtl_sources_config,
    )
    return result


EXPECTED_COLUMNS = {
    "variant_id",
    "beta",
    "se",
    "maf",
    "position",
    "N",
    "sdY",
    "gene_id",
    "tissue",
    "pvalue",
    "rsid",
    "chromosome",
}


class TestOnek1kOutputColumns:
    """test_onek1k_output_columns: verify output has common intermediate columns."""

    def test_output_has_expected_columns(self, harmonized_df):
        assert set(harmonized_df.columns) == EXPECTED_COLUMNS

    def test_output_is_nonempty(self, harmonized_df):
        assert len(harmonized_df) > 0


class TestOnek1kSdY:
    """test_onek1k_sdy_is_one: sdY == 1.0 for all rows."""

    def test_sdy_is_one(self, harmonized_df):
        """sdY should be 1.0 for OneK1K (eQTL Catalogue inverse-normal transformed)."""
        assert (harmonized_df["sdY"] == 1.0).all()


class TestOnek1kCellTypeInTissueColumn:
    """test_onek1k_cell_type_in_tissue_column: tissue column == cell_type for all rows."""

    def test_tissue_equals_cell_type(self, harmonized_df):
        """tissue column should be the cell type name (Mono_C)."""
        assert (harmonized_df["tissue"] == "Mono_C").all()


class TestOnek1kRegionFilter:
    """test_onek1k_region_filter: output only contains variants within the region."""

    def test_region_filter_within_window(self, harmonized_df):
        """All output positions must be within the FTO GRCh38 region."""
        assert (harmonized_df["position"] >= 53766088).all()
        assert (harmonized_df["position"] <= 54366088).all()

    def test_region_filter_excludes_other_chroms(self, harmonized_df):
        """Only chromosome 16 variants should be present for FTO region."""
        assert (harmonized_df["chromosome"].astype(str) == "16").all()


class TestOnek1kNFromAn:
    """N should be an/2. Mock has an=1964, so N=982."""

    def test_n_is_982(self, harmonized_df):
        assert (harmonized_df["N"] == 982).all()


class TestOnek1k14CellTypesInConfig:
    """test_onek1k_14_cell_types_in_config: qtl_sources.yaml has exactly 14 cell types."""

    def test_14_cell_types(self, qtl_sources_config):
        cell_types = qtl_sources_config["sources"]["onek1k_sceqtl"]["cell_types"]
        assert len(cell_types) == 14

    def test_cell_types_are_strings(self, qtl_sources_config):
        cell_types = qtl_sources_config["sources"]["onek1k_sceqtl"]["cell_types"]
        assert all(isinstance(ct, str) for ct in cell_types)

    def test_mono_c_in_cell_types(self, qtl_sources_config):
        cell_types = qtl_sources_config["sources"]["onek1k_sceqtl"]["cell_types"]
        assert "Mono_C" in cell_types


class TestDownloadOnek1kHasFallback:
    """test_download_onek1k_has_fallback: download_onek1k.py has both source handlers."""

    def test_download_script_exists(self):
        script_path = PROJECT_ROOT / "src" / "python" / "download_onek1k.py"
        assert script_path.exists(), "download_onek1k.py should exist"

    def test_download_has_eqtl_catalogue_source(self):
        script_path = PROJECT_ROOT / "src" / "python" / "download_onek1k.py"
        content = script_path.read_text()
        assert "eqtl_catalogue" in content, "should handle eQTL Catalogue source"
        assert "QTS000038" in content, "should reference QTS000038 study ID"

    def test_download_has_onek1k_org_source(self):
        script_path = PROJECT_ROOT / "src" / "python" / "download_onek1k.py"
        content = script_path.read_text()
        assert "onek1k" in content.lower(), "should handle onek1k.org source"
        assert "onek1k.s3.ap-southeast-2" in content, "should reference S3 bucket"


class TestHarmonizeOnek1kReusesEqtlLogic:
    """harmonize_onek1k.py should reference harmonize_eqtl for eQTL Catalogue format reuse."""

    def test_script_references_harmonize_eqtl(self):
        script_path = PROJECT_ROOT / "src" / "python" / "harmonize_onek1k.py"
        content = script_path.read_text()
        assert "harmonize_eqtl" in content, "should import/reference harmonize_eqtl"

    def test_handles_both_source_formats(self):
        script_path = PROJECT_ROOT / "src" / "python" / "harmonize_onek1k.py"
        content = script_path.read_text()
        assert "eqtl_catalogue" in content, "should handle eqtl_catalogue format"
        assert "onek1k_org" in content, "should handle onek1k_org format"


class TestSnakemakeRulesExist:
    """qtl_download.smk should contain OneK1K download and harmonize rules."""

    def test_download_rule_exists(self):
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "qtl_download.smk"
        content = smk_path.read_text()
        assert "rule download_onek1k_cell_type:" in content

    def test_harmonize_rule_exists(self):
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "qtl_download.smk"
        content = smk_path.read_text()
        assert "rule harmonize_onek1k_region:" in content
