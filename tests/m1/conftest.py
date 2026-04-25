"""Shared M1 test fixtures.

Provides synthetic 10-column TSV fixtures (b37 + b38), an LDSC rg-log
fixture loader, and a chain-file path resolver. Test modules in tests/m1/
consume these fixtures.

Plan reference: m1-00-preflight-and-environment-PLAN.md Task 1.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

# Project root: tests/m1/conftest.py -> parents[2] = repo root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# Make src/python importable for `import sumstats_utils`.
import sys

_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Path to the static fixture directory (TSVs, LDSC log)."""
    return FIXTURES_DIR


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Repo root path."""
    return PROJECT_ROOT


@pytest.fixture
def synth_b37_frame() -> pd.DataFrame:
    """Load the static synthetic 10-col GRCh37 fixture (100 rows).

    Five A/T or C/G palindromic rows in EAF=[0.48, 0.52]; ninety-five
    non-palindromic rows. EAF range covers [0.005, 0.5].
    """
    fp = FIXTURES_DIR / "synth_10col_b37.tsv"
    return pd.read_csv(fp, sep="\t")


@pytest.fixture
def synth_b38_frame() -> pd.DataFrame:
    """Load the static synthetic 10-col GRCh38 fixture (20 rows).

    First 20 rows of the b37 fixture with positions shifted by +1Mb to
    simulate hg38 coordinates. Used by test_liftover.py round-trip.
    """
    fp = FIXTURES_DIR / "synth_10col_b38.tsv"
    return pd.read_csv(fp, sep="\t")


@pytest.fixture
def ldsc_rg_log_text() -> str:
    """Read the LDSC rg-log fixture as a single string.

    Used by test_ldsc_star_reducer.py to verify gcov_int parsing on a
    realistic 3-pair "Summary of Genetic Correlation Results" table.
    """
    fp = FIXTURES_DIR / "ldsc_rg_log_sample.log"
    with open(fp) as fh:
        return fh.read()


@pytest.fixture
def chain_file_path(project_root) -> Path:
    """Path to the staged hg38ToHg19 UCSC chain file (Wave 0 Task 2).

    Tests that need real liftover capability use this fixture; tests that
    only need to assert chain-file existence use the same path. If the
    chain file is absent at fixture-resolution time, the test should
    pytest.skip with a reason — Wave 0 Task 2 stages the file.
    """
    return project_root / "data" / "external" / "liftover" / "hg38ToHg19.over.chain.gz"


# Programmatic factories -------------------------------------------------

def _build_b37_rows(n: int = 100) -> pd.DataFrame:
    """Construct a synthetic canonical 10-col DataFrame with `n` rows.

    Used both for static fixture generation and for inline tests that
    want a programmatic frame. Keep deterministic — seed-driven.
    """
    import numpy as np

    rng = np.random.default_rng(42)
    # Force-include 5 palindromic rows in the MAF=[0.48,0.52] band.
    pal_alleles = [("A", "T"), ("T", "A"), ("C", "G"), ("G", "C"), ("A", "T")]
    pal_eaf = [0.485, 0.500, 0.515, 0.490, 0.505]

    non_pal_alleles_pool = [
        ("A", "G"), ("G", "A"), ("C", "T"), ("T", "C"),
        ("A", "C"), ("C", "A"), ("G", "T"), ("T", "G"),
    ]
    n_non_pal = n - 5

    chrs = rng.integers(1, 23, size=n)
    bps = rng.integers(10_000, 250_000_000, size=n)
    snps = [f"rs{i:08d}" for i in range(n)]

    eas = []
    oas = []
    for i in range(n):
        if i < 5:
            ea, oa = pal_alleles[i]
        else:
            ea, oa = non_pal_alleles_pool[(i - 5) % len(non_pal_alleles_pool)]
        eas.append(ea)
        oas.append(oa)

    betas = rng.normal(0.0, 0.05, size=n)
    ses = rng.uniform(0.01, 0.05, size=n)
    ps = rng.uniform(1e-10, 1.0, size=n)

    eafs = []
    for i in range(n):
        if i < 5:
            eafs.append(pal_eaf[i])
        else:
            # non-palindromic — broad EAF range [0.005, 0.5]
            eafs.append(float(rng.uniform(0.005, 0.5)))

    ns = rng.integers(50_000, 700_000, size=n).astype(int)

    return pd.DataFrame({
        "CHR": chrs,
        "BP": bps,
        "SNP": snps,
        "EA": eas,
        "OA": oas,
        "BETA": betas,
        "SE": ses,
        "P": ps,
        "EAF": eafs,
        "N": ns,
    })
