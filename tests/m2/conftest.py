"""Shared M2 test fixtures.

Mirrors tests/m1/conftest.py. Provides project_root, synthetic_ldsc_matrix,
synthetic_z_matrix, trait_inventory_yaml fixtures consumed by tests/m2/test_*.py.

Plan reference: m2-00-preflight-and-environment-PLAN.md Task 1.
Decision references:
  D-M2-04 — CPASSOC Python reimplementation with LDSC intercept matrix as R
  D-M2-Q6 — _MIN_PER_STRATUM=3 (Carter-locked)
  REQ-MTAG-OVERLAP — MTAG --residcov_path consumes K×K bare matrix slice
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

# Project root: tests/m2/conftest.py -> parents[2] = repo root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# Make src/python importable for `import cpassoc` etc. (mirrors tests/m1/conftest.py).
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Repo root path."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Path to the static fixture directory."""
    return FIXTURES_DIR


@pytest.fixture
def synthetic_ldsc_matrix() -> np.ndarray:
    """5×5 PSD synthetic R matrix; diag=1.0, off-diag in [0.0, 0.3], seed=42.

    Mimics the M1 LDSC bivariate-intercept matrix structure (PSD, symmetric,
    diag=1.0). Used by CPASSOC SHom/SHet tests.
    """
    rng = np.random.default_rng(42)
    A = rng.uniform(0.0, 0.3, size=(5, 5))
    R = (A + A.T) / 2.0
    np.fill_diagonal(R, 1.0)
    return R


@pytest.fixture
def synthetic_z_matrix() -> np.ndarray:
    """(100, 5) z-score grid, seed=42.

    Used by CPASSOC + MTAG slice tests.
    """
    rng = np.random.default_rng(42)
    return rng.standard_normal(size=(100, 5))


@pytest.fixture
def trait_inventory_yaml(project_root: Path) -> Path:
    """Path to the locked trait_inventory.yaml.

    Used by m2_stratum_keys tests. If absent, the test should pytest.skip.
    """
    return project_root / "config" / "trait_inventory.yaml"
