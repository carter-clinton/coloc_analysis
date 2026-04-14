"""Phase 9 shared test fixtures — replication cohorts.

Provides:
  - replication_cohorts_config: parsed config/replication_cohorts.yaml
  - mock_finngen_sumstats: 100-row FinnGen R12 raw-schema tempfile
  - mock_bbj_sumstats:     100-row BBJ hum0197-v3 raw-schema tempfile
  - mock_mvp_sumstats:     100-row MVP dbGaP raw-schema tempfile
  - mock_gbmi_sumstats:    100-row GBMI raw-schema tempfile
  - canonical_schema:      list of canonical harmonized column names

All mock fixtures emit 100 SNPs at chr10:114750000-114750099 so they share
a locus with the TCF7L2 T2D signal used as a pipeline smoke-test anchor.
"""
from pathlib import Path

import pandas as pd
import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def replication_cohorts_config():
    """Parse config/replication_cohorts.yaml once per session."""
    with open(PROJECT_ROOT / "config" / "replication_cohorts.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture
def mock_finngen_sumstats(tmp_path):
    """100-row mock FinnGen R12 sumstats with canonical raw column names."""
    df = pd.DataFrame({
        "#chrom": [10] * 100,
        "pos": range(114750000, 114750100),
        "ref": ["A"] * 100,
        "alt": ["G"] * 100,
        "rsids": [f"rs{i}" for i in range(100)],
        "nearest_genes": ["TCF7L2"] * 100,
        "pval": [1e-8] * 100,
        "mlogp": [8.0] * 100,
        "beta": [0.1] * 100,
        "sebeta": [0.02] * 100,
        "af_alt": [0.3] * 100,
        "af_alt_cases": [0.32] * 100,
        "af_alt_controls": [0.29] * 100,
    })
    path = tmp_path / "finngen_R12_T2D.tsv.gz"
    df.to_csv(path, sep="\t", index=False, compression="gzip")
    return path


@pytest.fixture
def mock_bbj_sumstats(tmp_path):
    """100-row mock BBJ hum0197-v3 sumstats (REGENIE-style)."""
    df = pd.DataFrame({
        "SNPID": [f"10:{114750000+i}:A:G" for i in range(100)],
        "CHR": [10] * 100,
        "POS": range(114750000, 114750100),
        "Allele1": ["A"] * 100,
        "Allele2": ["G"] * 100,
        "AF": [0.3] * 100,
        "Beta": [0.08] * 100,
        "SE": [0.02] * 100,
        "p.value": [1e-6] * 100,
        "N": [180000] * 100,
    })
    path = tmp_path / "hum0197.v3.BBJ.T2D.v1.tsv"
    df.to_csv(path, sep="\t", index=False)
    return path


@pytest.fixture
def mock_mvp_sumstats(tmp_path):
    """100-row mock MVP dbGaP phs001672 sumstats.

    NOTE: MVP text files use the dbGaP GWAS-central schema (|beta|,
    "Coded Allele" direction) not raw REGENIE output. This fixture
    captures the REGENIE-style variant the plan draft assumed; Plan 09-02
    Task 3 will add a dbGaP-schema variant as its own fixture.
    """
    df = pd.DataFrame({
        "CHROM": [10] * 100,
        "POS": range(114750000, 114750100),
        "REF": ["A"] * 100,
        "ALT": ["G"] * 100,
        "ID": [f"rs{i}" for i in range(100)],
        "A1_FREQ": [0.3] * 100,
        "BETA": [0.1] * 100,
        "SE": [0.02] * 100,
        "LOG10P": [8.0] * 100,
        "N": [250000] * 100,
    })
    path = tmp_path / "pha004945.1.tsv.gz"
    df.to_csv(path, sep="\t", index=False, compression="gzip")
    return path


@pytest.fixture
def mock_gbmi_sumstats(tmp_path):
    """100-row mock GBMI sumstats with all_meta_* column prefix."""
    df = pd.DataFrame({
        "CHR": [10] * 100,
        "POS": range(114750000, 114750100),
        "REF": ["A"] * 100,
        "ALT": ["G"] * 100,
        "rsid": [f"rs{i}" for i in range(100)],
        "all_meta_sample_N": [1200000] * 100,
        "all_meta_AF": [0.3] * 100,
        "all_meta_beta": [0.09] * 100,
        "all_meta_sebeta": [0.015] * 100,
        "all_meta_pval": [1e-10] * 100,
    })
    path = tmp_path / "gbmi_t2d_eur.tsv.gz"
    df.to_csv(path, sep="\t", index=False, compression="gzip")
    return path


@pytest.fixture
def canonical_schema():
    """Canonical harmonized sumstats columns (ALL replication cohorts must conform)."""
    return ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]
