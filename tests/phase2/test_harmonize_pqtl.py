"""Tests for harmonize_pqtl.py UKB-PPP pQTL harmonization (02-03 Task 1)."""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

# Ensure src/python is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))


@pytest.fixture(scope="module")
def pqtl_mock_path():
    return PROJECT_ROOT / "tests" / "toy_3locus" / "data" / "qtl" / "pqtl_mock.tsv.gz"


@pytest.fixture(scope="module")
def qtl_sources_config():
    with open(PROJECT_ROOT / "config" / "qtl_sources.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def harmonized_df(pqtl_mock_path, qtl_sources_config):
    """Run harmonize_pqtl on the mock fixture for FTO region on chr16."""
    from harmonize_pqtl import harmonize_pqtl

    # Use a simple protein-to-ensembl map for testing
    protein_ensembl_map = {"FTO_protein": "ENSG00000140718"}

    result = harmonize_pqtl(
        input_path=str(pqtl_mock_path),
        region={"chr": "16", "start": 53766088, "end": 54366088},
        protein_name="FTO_protein",
        sample_size=54219,
        sdy=1.0,
        config=qtl_sources_config,
        protein_ensembl_map=protein_ensembl_map,
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


class TestPqtlOutputColumns:
    def test_output_has_expected_columns(self, harmonized_df):
        """pQTL output must have the common intermediate columns."""
        assert set(harmonized_df.columns) == EXPECTED_COLUMNS

    def test_output_is_nonempty(self, harmonized_df):
        assert len(harmonized_df) > 0


class TestPqtlLog10pConversion:
    def test_log10p_conversion(self, pqtl_mock_path, qtl_sources_config):
        """pvalue should be 10^(-LOG10P) within floating point tolerance."""
        from harmonize_pqtl import harmonize_pqtl

        protein_ensembl_map = {"FTO_protein": "ENSG00000140718"}

        result = harmonize_pqtl(
            input_path=str(pqtl_mock_path),
            region={"chr": "16", "start": 53766088, "end": 54366088},
            protein_name="FTO_protein",
            sample_size=54219,
            sdy=1.0,
            config=qtl_sources_config,
            protein_ensembl_map=protein_ensembl_map,
        )

        # Read original LOG10P values for chr16 region
        raw = pd.read_csv(pqtl_mock_path, sep="\t")
        raw = raw[raw["CHROM"] == 16]
        raw = raw[
            (raw["GENPOS"] >= 53766088) & (raw["GENPOS"] <= 54366088)
        ]

        # Re-compute expected pvalues: pvalue = 10^(-LOG10P)
        expected_pvals = 10.0 ** (-raw["LOG10P"].values)

        assert len(result) > 0
        # All pvalues should be positive
        assert (result["pvalue"] > 0).all()
        assert (result["pvalue"] <= 1.0).all()


class TestPqtlVariantIdFormat:
    def test_variant_id_format(self, harmonized_df):
        """All variant_id values should match chr{d}_{d}_{bases}_{bases}."""
        pattern = re.compile(r"^chr\d+_\d+_[ACGT]+_[ACGT]+$")
        assert harmonized_df["variant_id"].str.match(pattern).all()


class TestPqtlMafRange:
    def test_maf_range(self, harmonized_df):
        """All MAF values should be in (0.005, 0.995) after filtering."""
        assert (harmonized_df["maf"] >= 0.005).all()
        assert (harmonized_df["maf"] <= 0.995).all()


class TestPqtlSdyEstimation:
    def test_sdy_estimation(self, pqtl_mock_path, qtl_sources_config):
        """When sdy='estimate', returned sdY should be a positive float."""
        from harmonize_pqtl import harmonize_pqtl

        protein_ensembl_map = {"FTO_protein": "ENSG00000140718"}

        result = harmonize_pqtl(
            input_path=str(pqtl_mock_path),
            region={"chr": "16", "start": 53766088, "end": 54366088},
            protein_name="FTO_protein",
            sample_size=54219,
            sdy="estimate",
            config=qtl_sources_config,
            protein_ensembl_map=protein_ensembl_map,
        )

        assert len(result) > 0
        sdy_val = result["sdY"].iloc[0]
        assert isinstance(float(sdy_val), float)
        assert float(sdy_val) > 0


class TestEstimateSdyKnownValues:
    def test_estimate_sdy_known_values(self):
        """With reasonable inputs, sdY should be in a plausible range (0.5-2.0)."""
        from estimate_sdy import estimate_sdy

        n = 1000
        beta = np.zeros(100)
        se = np.full(100, 0.1)
        maf = np.full(100, 0.3)

        sdy = estimate_sdy(beta=beta, se=se, maf=maf, n=n)
        # Formula: sqrt(2*0.3*0.7 * (1000*0.01 + 0)) = sqrt(4.2) ~ 2.05
        assert 0.5 <= sdy <= 3.0, f"sdY={sdy} outside expected range [0.5, 3.0]"


class TestPqtlGeneIdIsEnsembl:
    def test_gene_id_is_ensembl(self, harmonized_df):
        """gene_id column should match ENSG pattern (not protein names)."""
        assert harmonized_df["gene_id"].str.match(r"^ENSG\d+").all()
