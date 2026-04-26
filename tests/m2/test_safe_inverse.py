"""_safe_inverse tests — pinv + conditional ridge fallback.

D-M2-Q2 — When cond(R) > 1e6, apply ridge regularization R + λI BEFORE pinv.
Plan reference: m2-00-preflight-and-environment-PLAN.md Task 6.
"""
from __future__ import annotations

import numpy as np
import pytest

try:
    from cpassoc import _safe_inverse  # noqa: F401
    _SAFE_INVERSE_AVAILABLE = True
except ImportError:
    _SAFE_INVERSE_AVAILABLE = False
    _safe_inverse = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(
    not _SAFE_INVERSE_AVAILABLE, reason="src/python/cpassoc.py not yet landed (Wave 0 Task 6)"
)


def test_well_conditioned_returns_pinv(synthetic_ldsc_matrix):
    """Well-conditioned R: pinv(R) @ R ≈ I within tolerance."""
    Rinv = _safe_inverse(synthetic_ldsc_matrix)
    np.testing.assert_allclose(
        Rinv @ synthetic_ldsc_matrix, np.eye(5), atol=1e-8
    )


def test_near_singular_triggers_ridge():
    """Near-singular R: ridge fallback prevents NaN/Inf in result."""
    # Construct a rank-1 + tiny noise matrix (nearly singular)
    v = np.array([1.0, 1.0, 1.0])
    R = np.outer(v, v) + 1e-15 * np.eye(3)
    Rinv = _safe_inverse(R, ridge_floor=1e-4)
    assert np.all(np.isfinite(Rinv))


def test_eigvalsh_psd_tolerance():
    """Result remains numerically PSD-symmetric within tolerance."""
    rng = np.random.default_rng(42)
    A = rng.uniform(0.0, 0.3, size=(5, 5))
    R = (A + A.T) / 2.0
    np.fill_diagonal(R, 1.0)
    Rinv = _safe_inverse(R)
    # Symmetrize before eigvalsh
    eigs = np.linalg.eigvalsh((Rinv + Rinv.T) / 2.0)
    assert np.all(eigs > -1e-10)
