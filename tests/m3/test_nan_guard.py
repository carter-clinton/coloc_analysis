"""Regression tests for the NaN guard in plink_ld_to_npz.read_square_bin
(quick 260703-o0m, Seth Defect 3).

A plink ``--r`` ``0/0 -> NaN`` LD entry (zero-variance variant: monomorphic in the
``--nonfounders`` set, all-missing, or all-heterozygous) must be DIAGNOSED by the
reader — a NaN-specific error that NAMES the likely source variant row(s) — not
mis-reported as an asymmetry. The culprit finder must be robust to the REAL
fire-#3 fingerprint (whole-row NaN with the diagonal still 1.0, where a naive
``np.isnan(row).all(axis=1)`` returns []) AND to a sparse NaN cluster, and must
stay memory-lean (block-wise, no full ``n_var**2`` temporary — the OOM class that
bit m3-02e-T4).

Runs in smoke_dev py3.11 (numpy only). No Hail.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import plink_ld_to_npz as pln  # noqa: E402

NAN32 = np.float32("nan")


def _clean_symmetric(n: int, seed: int = 1) -> np.ndarray:
    """Exactly-symmetric float32 matrix, unit diagonal, no NaN."""
    rng = np.random.default_rng(seed)
    a = rng.standard_normal((n, n)).astype("float32")
    m = ((a + a.T) / np.float32(2.0)).astype("float32")
    np.fill_diagonal(m, 1.0)
    return m


def _write(m: np.ndarray, path: Path) -> Path:
    m.astype("<f4").tofile(path)
    return path


# --------------------------------------------------------------------------- #
# _has_any_nan_blocked                                                         #
# --------------------------------------------------------------------------- #

def test_has_any_nan_blocked_false_on_clean():
    assert pln._has_any_nan_blocked(_clean_symmetric(48)) is False


def test_has_any_nan_blocked_true_on_sparse():
    m = _clean_symmetric(48)
    m[5, 30] = NAN32
    m[30, 5] = NAN32
    assert pln._has_any_nan_blocked(m) is True


# --------------------------------------------------------------------------- #
# nan_variant_indices — robust to the REAL fingerprint (diagonal stays 1.0)    #
# --------------------------------------------------------------------------- #

def test_nan_variant_indices_ranks_whole_row_source_first_diag_1():
    """Fire-#3 fingerprint: a monomorphic variant NaNs its whole row/col but plink
    keeps the diagonal at 1.0, so row k is NOT fully NaN. ``.all(axis=1)`` would
    return []; the ranked-by-count finder must put k FIRST (n-1 NaNs vs 1 for an
    innocent paired row)."""
    n = 40
    m = _clean_symmetric(n)
    k = 7
    m[k, :] = NAN32
    m[:, k] = NAN32
    np.fill_diagonal(m, 1.0)
    idx = pln.nan_variant_indices(m)
    assert idx, "must not be empty on the diagonal-1.0 whole-row fingerprint"
    assert idx[0] == k


def test_nan_variant_indices_reports_sparse_cluster():
    n = 40
    m = _clean_symmetric(n)
    a, b = 5, 30
    m[a, b] = NAN32
    m[b, a] = NAN32
    assert {a, b} <= set(pln.nan_variant_indices(m))


def test_nan_variant_indices_block_size_invariant():
    """A small block forces multiple passes; the result must not depend on block."""
    n = 40
    m = _clean_symmetric(n)
    k = 11
    m[k, :] = NAN32
    m[:, k] = NAN32
    np.fill_diagonal(m, 1.0)
    assert pln.nan_variant_indices(m, block=4)[0] == k
    assert pln.nan_variant_indices(m, block=4)[0] == pln.nan_variant_indices(m, block=4096)[0]


# --------------------------------------------------------------------------- #
# read_square_bin end-to-end                                                   #
# --------------------------------------------------------------------------- #

def test_read_square_bin_clean_returns_matrix(tmp_path):
    n = 32
    m = _clean_symmetric(n)
    out = pln.read_square_bin(_write(m, tmp_path / "clean.ld.bin"), n)
    assert out.shape == (n, n)
    assert not np.isnan(out).any()


def test_read_square_bin_nan_names_source(tmp_path):
    n = 40
    m = _clean_symmetric(n)
    k = 7
    m[k, :] = NAN32
    m[:, k] = NAN32
    np.fill_diagonal(m, 1.0)
    with pytest.raises(ValueError) as ei:
        pln.read_square_bin(_write(m, tmp_path / "nan.ld.bin"), n)
    msg = str(ei.value)
    assert "NaN" in msg
    assert "not symmetric" not in msg
    assert str(k) in msg


def test_read_square_bin_asymmetric_no_nan_still_not_symmetric(tmp_path):
    """The NaN pre-check must NOT swallow a genuine (NaN-free) asymmetry — a
    symmetric-but-not-NaN matrix broken at one off-diagonal pair still raises the
    original 'not symmetric' error."""
    n = 32
    m = _clean_symmetric(n)
    m[3, 9] = np.float32(0.9)
    m[9, 3] = np.float32(-0.9)   # break symmetry, no NaN, diagonal stays 1.0
    with pytest.raises(ValueError, match="not symmetric"):
        pln.read_square_bin(_write(m, tmp_path / "asym.ld.bin"), n)
