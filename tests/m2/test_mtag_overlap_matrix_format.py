"""MTAG residcov matrix format tests (REQ-MTAG-OVERLAP).

The MTAG --residcov_path flag accepts a bare numeric K×K matrix file
(.npy or whitespace-delimited .txt). These tests verify the .txt format
round-trips through numpy.loadtxt and that shape K×K matches len(trait_order).

Wave 0 dependency on Wave 2 — skipped until build_mtag_residcov_slice.py lands.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

try:
    from build_mtag_residcov_slice import slice_for_stratum  # type: ignore[import-not-found]
    _SLICE_AVAILABLE = True
except ImportError:
    _SLICE_AVAILABLE = False
    slice_for_stratum = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(
    not _SLICE_AVAILABLE,
    reason="src/python/build_mtag_residcov_slice.py not yet landed (Wave 2 Task 1)",
)


def test_loadtxt_round_trip(tmp_path: Path):
    """numpy.loadtxt(residcov.txt) returns a K×K matrix matching the slice."""
    matrix = np.array([[1.0, 0.2], [0.2, 1.0]])
    out_dir = tmp_path / "mtag" / "EUR"
    out_dir.mkdir(parents=True)
    slice_for_stratum(matrix, ["x", "y"], ["x", "y"], out_dir)
    loaded = np.loadtxt(out_dir / "residcov.txt")
    np.testing.assert_allclose(loaded, matrix, atol=1e-10)


def test_shape_matches_trait_order(tmp_path: Path):
    """K×K shape MUST equal len(trait_order.json['trait_order'])."""
    matrix = np.eye(4)
    out_dir = tmp_path / "mtag" / "AFR"
    out_dir.mkdir(parents=True)
    slice_for_stratum(matrix, ["a", "b", "c", "d"], ["a", "c"], out_dir)
    loaded = np.loadtxt(out_dir / "residcov.txt")
    payload = json.loads((out_dir / "residcov.trait_order.json").read_text())
    K = len(payload["trait_order"])
    assert loaded.shape == (K, K)
