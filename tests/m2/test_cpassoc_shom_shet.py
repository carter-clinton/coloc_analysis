"""CPASSOC SHom + SHet tests (Zhu 2015 *AJHG* 96:21-36).

D-M2-04 — Python reimplementation with LDSC intercept matrix as R.
Plan reference: m2-00-preflight-and-environment-PLAN.md Task 6.
"""
from __future__ import annotations

import numpy as np
import pytest

try:
    from cpassoc import cpassoc_shom, cpassoc_shet  # noqa: F401
    _CPASSOC_AVAILABLE = True
except ImportError:
    _CPASSOC_AVAILABLE = False
    cpassoc_shom = None  # type: ignore[assignment]
    cpassoc_shet = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(
    not _CPASSOC_AVAILABLE, reason="src/python/cpassoc.py not yet landed (Wave 0 Task 6)"
)


def test_shom_identity_R_equals_sum_z_squared():
    """Identity case: SHom(z, I) = Σ z_i² (chi-square df=K)."""
    z = np.array([[1.0, 2.0, 3.0]])
    R = np.eye(3)
    # SHom = z' I z = 1 + 4 + 9 = 14
    assert cpassoc_shom(z, R)[0] == pytest.approx(14.0, abs=1e-10)


def test_shet_identity_R_equals_centered_sum():
    """Identity case: SHet(z, I) = Σ z_i² − (Σ z_i)² / K (chi-square df=K-1)."""
    z = np.array([[1.0, 2.0, 3.0]])
    R = np.eye(3)
    # SHet = 14 - 36/3 = 14 - 12 = 2.0
    assert cpassoc_shet(z, R)[0] == pytest.approx(2.0, abs=1e-10)


def test_5_trait_synthetic(synthetic_z_matrix, synthetic_ldsc_matrix):
    """5-trait synthetic case: returns shape (n_snps,), all non-negative."""
    out_shom = cpassoc_shom(synthetic_z_matrix, synthetic_ldsc_matrix)
    out_shet = cpassoc_shet(synthetic_z_matrix, synthetic_ldsc_matrix)
    assert out_shom.shape == (100,)
    assert out_shet.shape == (100,)
    assert (out_shom >= 0).all()
    assert (out_shet >= 0).all()


def test_dimension_mismatch_raises():
    """K mismatch between z (last axis) and R must raise ValueError."""
    with pytest.raises(ValueError):
        cpassoc_shom(np.array([[1.0, 2.0]]), np.eye(3))
