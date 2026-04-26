"""MTAG residcov slice tests (D-M2-10 critical correction, REQ-MTAG-OVERLAP).

D-M2-10 corrects the colloquial '--overlap' to MTAG's actual --residcov_path
flag. The implementation MUST emit:
  - bare numeric K×K matrix (no header, no row index) at residcov.txt
  - sidecar trait_order.json recording trait-order alignment with --sumstats

These tests exercise the slice helper. Wave 2 Task 1 lands
src/python/build_mtag_residcov_slice.py.

Pitfall 7 (RESEARCH): silent mis-alignment if --sumstats order diverges from
--residcov_path row/col order.
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


def test_slice_preserves_trait_order(tmp_path: Path):
    """Output K×K matrix rows/cols must match --sumstats order exactly."""
    # Matrix 4 traits; slice 3 in custom order
    matrix = np.array(
        [
            [1.0, 0.1, 0.2, 0.3],
            [0.1, 1.0, 0.4, 0.5],
            [0.2, 0.4, 1.0, 0.6],
            [0.3, 0.5, 0.6, 1.0],
        ]
    )
    full_keys = ["bmi.EUR", "t2d.EUR", "sbp.EUR", "ldl.EUR"]
    stratum_keys = ["sbp.EUR", "bmi.EUR", "ldl.EUR"]  # custom order
    out_dir = tmp_path / "mtag" / "EUR"
    out_dir.mkdir(parents=True)
    slice_for_stratum(matrix, full_keys, stratum_keys, out_dir)
    sliced = np.loadtxt(out_dir / "residcov.txt")
    # Diagonal still 1.0
    assert sliced[0, 0] == pytest.approx(1.0)
    # Row 0 = sbp; col 1 = bmi → should be matrix[2,0] = 0.2
    assert sliced[0, 1] == pytest.approx(0.2)


def test_sidecar_json_written(tmp_path: Path):
    """sidecar trait_order.json must record the order used in residcov.txt."""
    matrix = np.eye(3)
    full_keys = ["a", "b", "c"]
    stratum_keys = ["c", "a"]
    out_dir = tmp_path / "mtag" / "AFR"
    out_dir.mkdir(parents=True)
    slice_for_stratum(matrix, full_keys, stratum_keys, out_dir)
    sidecar = out_dir / "residcov.trait_order.json"
    assert sidecar.exists()
    payload = json.loads(sidecar.read_text())
    assert payload["trait_order"] == ["c", "a"]


def test_output_is_bare_numeric(tmp_path: Path):
    """residcov.txt must be bare numeric (no header, no row index) per Pitfall 1."""
    matrix = np.eye(2)
    out_dir = tmp_path / "mtag" / "TRANS"
    out_dir.mkdir(parents=True)
    slice_for_stratum(matrix, ["x", "y"], ["x", "y"], out_dir)
    text = (out_dir / "residcov.txt").read_text()
    # No header line should contain non-numeric tokens like trait keys
    for line in text.strip().splitlines():
        for tok in line.split():
            float(tok)  # raises if non-numeric
