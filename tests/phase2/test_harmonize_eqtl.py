"""Tests for harmonize_eqtl.py eQTL Catalogue harmonization (02-02 Task 1)."""
import gzip
import json
import os
import re
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

# Ensure src/python is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))


@pytest.fixture(scope="module")
def eqtl_mock_path():
    return PROJECT_ROOT / "tests" / "toy_3locus" / "data" / "qtl" / "eqtl_mock.tsv.gz"


@pytest.fixture(scope="module")
def qtl_sources_config():
    with open(PROJECT_ROOT / "config" / "qtl_sources.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def harmonized_df(eqtl_mock_path, qtl_sources_config, tmp_path_factory):
    """Run harmonize_eqtl on the mock fixture for gene ENSG00000140718 in FTO region."""
    from harmonize_eqtl import harmonize_eqtl

    result = harmonize_eqtl(
        input_path=str(eqtl_mock_path),
        region={"chr": "16", "start": 53766088, "end": 54366088},
        gene_id="ENSG00000140718",
        tissue_name="Adipose_Subcutaneous",
        tissue_n=581,
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


class TestHarmonizeEqtlOutputColumns:
    def test_output_has_expected_columns(self, harmonized_df):
        assert set(harmonized_df.columns) == EXPECTED_COLUMNS

    def test_output_is_nonempty(self, harmonized_df):
        assert len(harmonized_df) > 0


class TestHarmonizeEqtlSdY:
    def test_sdy_is_one(self, harmonized_df):
        """All sdY values should be 1.0 for GTEx (inverse-normal transformed)."""
        assert (harmonized_df["sdY"] == 1.0).all()


class TestHarmonizeEqtlN:
    def test_n_is_half_an(self, harmonized_df):
        """N should equal an/2. Mock has an=838, so N=419."""
        assert (harmonized_df["N"] == 419).all()


class TestHarmonizeEqtlRegionFilter:
    def test_region_filter_within_window(self, harmonized_df):
        """All output positions must be within the FTO GRCh38 region."""
        assert (harmonized_df["position"] >= 53766088).all()
        assert (harmonized_df["position"] <= 54366088).all()

    def test_region_filter_excludes_other_chroms(self, harmonized_df):
        """Only chromosome 16 variants should be present for FTO region."""
        assert (harmonized_df["chromosome"].astype(str) == "16").all()


class TestHarmonizeEqtlMafFilter:
    def test_no_extreme_maf(self, harmonized_df):
        """No rows with maf < 0.005 or maf > 0.995."""
        assert (harmonized_df["maf"] >= 0.005).all()
        assert (harmonized_df["maf"] <= 0.995).all()


class TestHarmonizeEqtlGeneFilter:
    def test_gene_filter(self, harmonized_df):
        """Output should only contain the requested gene."""
        assert (harmonized_df["gene_id"] == "ENSG00000140718").all()


class TestHarmonizeEqtlTissue:
    def test_tissue_column(self, harmonized_df):
        """Tissue column should be set to the provided tissue name."""
        assert (harmonized_df["tissue"] == "Adipose_Subcutaneous").all()
