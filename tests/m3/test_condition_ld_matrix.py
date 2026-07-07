"""Tests for src/python/condition_ld_matrix.py (m3-06-W6-T2, ROADMAP 999.1 §3).

condition_ld_matrix applies the pre-registered AFR native-panel NaN conditioning
policy (osf-amendment-afr-native-ld-nan-psd-2026-07-03.md):

  (a) Topology branch:
      - a FULLY-NaN variant row (zero-variance / monomorphic source) RAISES and
        directs an upstream MAF/missingness QC drop (NOT zero-conditioning);
      - otherwise isolated off-diagonal NaN pairs are set to 0.0 at BOTH (i,j) and
        (j,i); the diagonal (1.0) is untouched.
  (b) Zeroing ceiling: n_zeroed_pairs > ceiling_frac * n_var RAISES
      (BRANCH_AFR_COND_DEFERRED — substrate anomaly, re-diagnose + disclose).
  (d) Provenance: {nan_policy, n_zeroed_pairs, zeroed_pairs, n_var, ceiling_frac,
      ceiling_n}. PSD (method/lambda) runs at FIT TIME on the region submatrix
      (§5, deferred) — NOT here.

Memory discipline (T-m3-06-04): NaN detection, fully-NaN-row classification, and
pair location are block-wise (transient bounded by block x n_var, no full n_var**2
temporary), reusing the plink_ld_to_npz.py OOM discipline; a block-size-invariance
test locks it.

Runs in smoke_dev py3.11 (numpy only). No Hail, no perimeter access. Mirrors the
fixture/style of tests/m3/test_nan_guard.py.
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

import condition_ld_matrix as clm  # noqa: E402

NAN32 = np.float32("nan")


def _clean_symmetric(n: int, seed: int = 1) -> np.ndarray:
    """Exactly-symmetric float32 matrix, unit diagonal, no NaN (mirrors test_nan_guard)."""
    rng = np.random.default_rng(seed)
    a = rng.standard_normal((n, n)).astype("float32")
    m = ((a + a.T) / np.float32(2.0)).astype("float32")
    np.fill_diagonal(m, 1.0)
    return m


def _set_pair_nan(m: np.ndarray, i: int, j: int) -> None:
    """Set a symmetric off-diagonal NaN pair (both triangles), plink-style."""
    m[i, j] = NAN32
    m[j, i] = NAN32


def _region1_topology(n: int = 40) -> np.ndarray:
    """Region-1 characterized topology: 12 NaN cells = 6 symmetric off-diagonal pairs
    across 11 index-adjacent variant rows, 0 fully-NaN rows (index 10 shared by two
    pairs -> 11 distinct rows, not 12)."""
    m = _clean_symmetric(n)
    for (i, j) in [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (10, 11)]:
        _set_pair_nan(m, i, j)
    return m


# --------------------------------------------------------------------------- #
# CLEAN: no-op passthrough                                                     #
# --------------------------------------------------------------------------- #

def test_clean_matrix_is_noop_passthrough():
    n = 32
    m = _clean_symmetric(n)
    ref = m.copy()
    out, rec = clm.condition_ld_matrix(m)
    assert rec["n_zeroed_pairs"] == 0
    assert rec["zeroed_pairs"] == []
    assert rec["n_var"] == n
    assert rec["nan_policy"] == "off_diagonal_zero"
    assert np.array_equal(out, ref)          # unchanged
    assert not np.isnan(out).any()


def test_clean_record_carries_ceiling_provenance():
    m = _clean_symmetric(20)
    _, rec = clm.condition_ld_matrix(m, ceiling_frac=0.0005)
    assert rec["ceiling_frac"] == 0.0005
    assert rec["ceiling_n"] == pytest.approx(0.0005 * 20)


# --------------------------------------------------------------------------- #
# ISOLATED off-diagonal NaN pairs                                             #
# --------------------------------------------------------------------------- #

def test_isolated_pairs_zeroed_and_recorded():
    n = 40
    m = _clean_symmetric(n)
    _set_pair_nan(m, 5, 30)
    _set_pair_nan(m, 10, 11)
    out, rec = clm.condition_ld_matrix(m, ceiling_frac=0.5)   # high ceiling: isolate topology
    assert rec["n_zeroed_pairs"] == 2
    assert rec["zeroed_pairs"] == [(5, 30), (10, 11)]         # sorted i<j
    # zeroed at BOTH triangles
    assert out[5, 30] == 0.0 and out[30, 5] == 0.0
    assert out[10, 11] == 0.0 and out[11, 10] == 0.0
    # diagonal untouched
    assert np.allclose(np.diag(out), 1.0)
    # no remaining NaN, symmetric
    assert not np.isnan(out).any()
    assert np.array_equal(out, out.T)


def test_region1_topology_six_pairs():
    n = 40
    m = _region1_topology(n)
    out, rec = clm.condition_ld_matrix(m, ceiling_frac=0.5)   # 6 <= 0.5*40=20, isolate topology
    assert rec["n_zeroed_pairs"] == 6
    assert rec["zeroed_pairs"] == [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (10, 11)]
    assert not np.isnan(out).any()
    assert np.array_equal(out, out.T)
    assert np.allclose(np.diag(out), 1.0)


def test_offdiag_nan_in_lower_triangle_only_still_paired():
    """Robustness: even if a NaN appears in only ONE triangle, the pair is captured
    as unordered i<j and zeroed at BOTH coordinates."""
    n = 24
    m = _clean_symmetric(n)
    m[15, 4] = NAN32          # lower triangle only (i>j)
    out, rec = clm.condition_ld_matrix(m, ceiling_frac=0.5)
    assert rec["zeroed_pairs"] == [(4, 15)]
    assert out[4, 15] == 0.0 and out[15, 4] == 0.0
    assert not np.isnan(out).any()


# --------------------------------------------------------------------------- #
# FULLY-NaN row -> RAISE (drop upstream, do NOT zero-condition)                #
# --------------------------------------------------------------------------- #

def test_fully_nan_row_raises_and_directs_qc_drop():
    n = 40
    m = _clean_symmetric(n)
    k = 7
    m[k, :] = NAN32
    m[:, k] = NAN32
    np.fill_diagonal(m, 1.0)   # plink keeps diagonal 1.0 (fire-#3 fingerprint)
    with pytest.raises(ValueError) as ei:
        clm.condition_ld_matrix(m, ceiling_frac=0.5)
    msg = str(ei.value)
    assert str(k) in msg
    assert ("MAF" in msg) or ("missingness" in msg)
    assert "drop" in msg.lower()


def test_fully_nan_row_takes_priority_over_ceiling():
    """A fully-NaN row RAISES the drop-directive even when isolated pairs also
    exist — the topology branch is evaluated first."""
    n = 40
    m = _region1_topology(n)
    k = 20
    m[k, :] = NAN32
    m[:, k] = NAN32
    np.fill_diagonal(m, 1.0)
    with pytest.raises(ValueError) as ei:
        clm.condition_ld_matrix(m, ceiling_frac=0.5)
    assert ("MAF" in str(ei.value)) or ("missingness" in str(ei.value))


# --------------------------------------------------------------------------- #
# OVER-CEILING -> RAISE (BRANCH_AFR_COND_DEFERRED, no mutation)                #
# --------------------------------------------------------------------------- #

def test_over_ceiling_raises_branch_deferred_no_mutation():
    n = 40
    m = _clean_symmetric(n)
    pairs = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)]  # 6 pairs
    for (i, j) in pairs:
        _set_pair_nan(m, i, j)
    ref = m.copy()
    # ceiling_frac=0.05 -> ceiling_n = 2.0; 6 > 2 -> RAISE
    with pytest.raises(ValueError) as ei:
        clm.condition_ld_matrix(m, ceiling_frac=0.05)
    assert "BRANCH_AFR_COND_DEFERRED" in str(ei.value)
    # no mutation on the raise path (NaN pairs left intact, nothing zeroed)
    assert np.array_equal(m[np.isnan(m) == False], ref[np.isnan(ref) == False])
    assert np.isnan(m[1, 2])


def test_default_ceiling_frac_boundary_at_n4000():
    """Exercise the REAL pre-registered default ceiling_frac=0.0005 at a tractable
    n_var=4000 -> ceiling_n=2.0: 1 pair passes, 5 pairs raise. Covers the amendment
    default without a region-1-scale dense matrix."""
    n = 4000
    # 1 pair passes (1 <= 2.0)
    m1 = _clean_symmetric(n)
    _set_pair_nan(m1, 100, 101)
    _, rec = clm.condition_ld_matrix(m1)   # default ceiling_frac=0.0005
    assert rec["ceiling_n"] == pytest.approx(2.0)
    assert rec["n_zeroed_pairs"] == 1
    # 5 pairs raise (5 > 2.0)
    m5 = _clean_symmetric(n)
    for (i, j) in [(10, 11), (20, 21), (30, 31), (40, 41), (50, 51)]:
        _set_pair_nan(m5, i, j)
    with pytest.raises(ValueError, match="BRANCH_AFR_COND_DEFERRED"):
        clm.condition_ld_matrix(m5)


# --------------------------------------------------------------------------- #
# MEMORY-BOUNDED: block-size invariance                                       #
# --------------------------------------------------------------------------- #

def test_block_size_invariance():
    """Result (matrix + record) must be independent of the block parameter — the
    block-wise scan is a memory bound, not a semantic knob (mirrors test_nan_guard)."""
    n = 40
    m_small = _region1_topology(n)
    m_large = _region1_topology(n)
    out_s, rec_s = clm.condition_ld_matrix(m_small, ceiling_frac=0.5, block=4)
    out_l, rec_l = clm.condition_ld_matrix(m_large, ceiling_frac=0.5, block=4096)
    assert rec_s["n_zeroed_pairs"] == rec_l["n_zeroed_pairs"] == 6
    assert rec_s["zeroed_pairs"] == rec_l["zeroed_pairs"]
    assert np.array_equal(out_s, out_l)


def test_fully_nan_rows_helper_block_invariant():
    n = 40
    m = _clean_symmetric(n)
    k = 13
    m[k, :] = NAN32
    m[:, k] = NAN32
    np.fill_diagonal(m, 1.0)
    assert clm._fully_nan_rows_blocked(m, block=4) == clm._fully_nan_rows_blocked(m, block=4096) == [k]


def test_nan_offdiag_pairs_helper_block_invariant():
    n = 40
    m = _region1_topology(n)
    p_small = clm._nan_offdiag_pairs_blocked(m, block=4)
    p_large = clm._nan_offdiag_pairs_blocked(m, block=4096)
    assert p_small == p_large == [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (10, 11)]


# --------------------------------------------------------------------------- #
# Policy guard (Rule 2 correctness safeguard)                                 #
# --------------------------------------------------------------------------- #

def test_unsupported_nan_policy_raises():
    m = _clean_symmetric(16)
    with pytest.raises(ValueError, match="off_diagonal_zero"):
        clm.condition_ld_matrix(m, nan_policy="drop_variant")


def test_non_square_input_raises():
    with pytest.raises(ValueError):
        clm.condition_ld_matrix(np.zeros((4, 5), dtype="float32"))
