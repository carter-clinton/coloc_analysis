"""Phase 5 pytest fixtures -- pathway analysis config, mock data, GMT paths."""
import gzip
import random
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
PATHWAY_SETS_DIR = CONFIG_DIR / "pathway_sets"


@pytest.fixture(scope="session")
def project_root():
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def config_dir():
    return CONFIG_DIR


@pytest.fixture(scope="session")
def custom_gmt_path():
    """Return path to config/pathway_sets/custom_cardiometabolic.gmt."""
    return PATHWAY_SETS_DIR / "custom_cardiometabolic.gmt"


@pytest.fixture(scope="session")
def negctrl_gmt_path():
    """Return path to config/pathway_sets/negative_controls.gmt."""
    return PATHWAY_SETS_DIR / "negative_controls.gmt"


@pytest.fixture(scope="session")
def pipeline_config():
    """Return parsed config/pipeline.yaml with pathway section."""
    path = CONFIG_DIR / "pipeline.yaml"
    with open(path) as f:
        cfg = yaml.safe_load(f)
    assert "pathway" in cfg, "pipeline.yaml missing pathway section"
    return cfg


@pytest.fixture()
def mock_sumstats_path(tmp_path):
    """Create a minimal harmonized sumstats TSV for testing.

    100 rows on chr22, random P values, seed=42.
    Columns: CHR, POS, SNP, REF, ALT, BETA, SE, P, EAF, N
    """
    rng = random.Random(42)
    outfile = tmp_path / "mock_sumstats.tsv"
    header = "CHR\tPOS\tSNP\tREF\tALT\tBETA\tSE\tP\tEAF\tN\n"
    rows = []
    for i in range(100):
        pos = 16000000 + i * 1000
        snp = f"rs{100000 + i}"
        beta = rng.gauss(0, 0.1)
        se = abs(rng.gauss(0.05, 0.01))
        p = rng.uniform(0.0001, 1.0)
        eaf = rng.uniform(0.05, 0.95)
        rows.append(
            f"22\t{pos}\t{snp}\tA\tG\t{beta:.6f}\t{se:.6f}\t{p:.8f}\t{eaf:.4f}\t50000\n"
        )
    outfile.write_text(header + "".join(rows))
    return outfile


@pytest.fixture()
def mock_gene_loc(tmp_path):
    """Create a minimal NCBI37.3.gene.loc-format file.

    20 genes on chr22, format: ENTREZ CHR START END STRAND SYMBOL
    """
    outfile = tmp_path / "mock_gene.loc"
    genes = [
        ("1000", "22", "16050000", "16100000", "+", "TESTGENE1"),
        ("1001", "22", "16150000", "16200000", "+", "TESTGENE2"),
        ("1002", "22", "16250000", "16300000", "-", "TESTGENE3"),
        ("1003", "22", "16350000", "16400000", "+", "TESTGENE4"),
        ("1004", "22", "16450000", "16500000", "-", "TESTGENE5"),
        ("1005", "22", "16550000", "16600000", "+", "TESTGENE6"),
        ("1006", "22", "16650000", "16700000", "+", "TESTGENE7"),
        ("1007", "22", "16750000", "16800000", "-", "TESTGENE8"),
        ("1008", "22", "16850000", "16900000", "+", "TESTGENE9"),
        ("1009", "22", "16950000", "17000000", "+", "TESTGENE10"),
        ("3630", "22", "17050000", "17100000", "+", "INSR"),
        ("3667", "22", "17150000", "17200000", "+", "IRS1"),
        ("8660", "22", "17250000", "17300000", "-", "IRS2"),
        ("5290", "22", "17350000", "17400000", "+", "PIK3CA"),
        ("207", "22", "17450000", "17500000", "+", "AKT1"),
        ("208", "22", "17550000", "17600000", "-", "AKT2"),
        ("5468", "22", "17650000", "17700000", "+", "PPARG"),
        ("4035", "22", "17750000", "17800000", "+", "MC4R"),
        ("79068", "22", "17850000", "17900000", "+", "FTO"),
        ("627", "22", "17950000", "18000000", "+", "BDNF"),
    ]
    lines = ["\t".join(fields) + "\n" for fields in genes]
    outfile.write_text("".join(lines))
    return outfile


@pytest.fixture()
def mock_bim(tmp_path):
    """Create a minimal plink .bim file for chr22.

    100 SNPs matching mock_sumstats positions.
    .bim format: CHR SNP CM BP A1 A2
    """
    outfile = tmp_path / "mock.22.bim"
    rows = []
    for i in range(100):
        pos = 16000000 + i * 1000
        snp = f"rs{100000 + i}"
        rows.append(f"22\t{snp}\t0\t{pos}\tA\tG\n")
    outfile.write_text("".join(rows))
    return outfile


@pytest.fixture()
def mock_magma_gene_results(tmp_path):
    """Create a minimal MAGMA .genes.raw file.

    20 genes with ZSTAT, P, NSNPS columns.
    """
    outfile = tmp_path / "mock.genes.raw"
    header = "GENE\tNSNPS\tNPARAM\tN\tZSTAT\tP\n"
    rng = random.Random(42)
    rows = []
    for i in range(20):
        entrez = 1000 + i
        nsnps = rng.randint(5, 50)
        zstat = rng.gauss(0, 2)
        p = rng.uniform(0.001, 1.0)
        rows.append(f"{entrez}\t{nsnps}\t1\t50000\t{zstat:.4f}\t{p:.6f}\n")
    outfile.write_text(header + "".join(rows))
    return outfile


@pytest.fixture()
def mock_ldsc_results(tmp_path):
    """Create a minimal LDSC .results file.

    Baseline + custom annotation enrichment columns.
    """
    outfile = tmp_path / "mock.results"
    header = (
        "Category\tProp._SNPs\tProp._h2\tProp._h2_std_error\t"
        "Enrichment\tEnrichment_std_error\tEnrichment_p\t"
        "Coefficient\tCoefficient_z-score\n"
    )
    rows = [
        "L2_0\t0.05\t0.10\t0.02\t2.00\t0.50\t0.001\t1.5e-08\t3.2\n",
        "CUSTOM_INSULIN_SIGNALINGL2_0\t0.02\t0.05\t0.01\t2.50\t0.60\t0.005\t2.0e-08\t2.8\n",
    ]
    outfile.write_text(header + "".join(rows))
    return outfile
