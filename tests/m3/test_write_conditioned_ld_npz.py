"""Tests for src/python/write_conditioned_ld_npz.py (m3-06-W6-T3, ROADMAP 999.1 §4).

``write_conditioned_npz`` banks the NaN-conditioned LD matrix as a SEPARATE
provenance-stamped ``{region}.conditioned.npz`` (never the raw ``{region}.npz``):

  - base keys : ld, variant_ids, rsids, allele_freq, lower_triangular
                (the exact set ld_npz_to_rds.R already ingests);
  - provenance: n_zeroed, zeroed_pairs, nan_policy, psd_method, psd_lambda,
                ceiling_frac. The ``.npz`` key ``n_zeroed`` == the in-memory
                record's ``n_zeroed_pairs`` (unified provenance name). psd_method /
                psd_lambda are PLACEHOLDER sentinels ("PENDING_FIT_TIME" / NaN) —
                populated at FIT TIME (§5, deferred/loop-gated).

Out-path guard (T-m3-06-05): the writer REFUSES any path that is not
``*.conditioned.npz`` (and refuses the raw ``{region}.npz`` path) so the FROZEN raw
contract can never be clobbered.

Runs in smoke_dev py3.11 (numpy only). No Hail, no perimeter access, no R round-trip.
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

import write_conditioned_ld_npz as wcn  # noqa: E402

NAN32 = np.float32("nan")
REGION = "region_00001"

BASE_KEYS = ("ld", "variant_ids", "rsids", "allele_freq", "lower_triangular")
PROV_KEYS = ("n_zeroed", "zeroed_pairs", "nan_policy", "psd_method", "psd_lambda", "ceiling_frac")


def _clean_symmetric(n: int, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    a = rng.standard_normal((n, n)).astype("float32")
    m = ((a + a.T) / np.float32(2.0)).astype("float32")
    np.fill_diagonal(m, 1.0)
    return m


def _sidecars(n: int) -> dict:
    return dict(
        variant_ids=np.array([f"1:{1000 + i}:A:G" for i in range(n)]),
        rsids=np.array([f"rs{100 + i}" for i in range(n)]),
        allele_freq=np.linspace(0.01, 0.5, n).astype("float32"),
    )


def _set_pair_nan(m, i, j):
    m[i, j] = NAN32
    m[j, i] = NAN32


# --------------------------------------------------------------------------- #
# Round-trip: base + provenance keys; conditioned ld                          #
# --------------------------------------------------------------------------- #

def test_roundtrip_keys_and_conditioned_ld(tmp_path):
    n = 40
    m = _clean_symmetric(n)
    _set_pair_nan(m, 5, 30)
    _set_pair_nan(m, 10, 11)
    out = tmp_path / f"{REGION}.conditioned.npz"
    ret = wcn.write_conditioned_npz(
        m=m, **_sidecars(n), lower_triangular=False,
        out_npz=str(out), region_id=REGION, ceiling_frac=0.5,
    )
    assert Path(ret) == out and out.exists()
    z = np.load(out, allow_pickle=False)
    for k in BASE_KEYS + PROV_KEYS:
        assert k in z.files, f"missing key {k}"
    ld = z["ld"]
    assert ld[5, 30] == 0.0 and ld[30, 5] == 0.0
    assert ld[10, 11] == 0.0 and ld[11, 10] == 0.0
    assert np.allclose(np.diag(ld), 1.0)
    assert not np.isnan(ld).any()
    assert np.array_equal(ld, ld.T)


def test_provenance_values(tmp_path):
    n = 40
    m = _clean_symmetric(n)
    _set_pair_nan(m, 5, 30)
    _set_pair_nan(m, 10, 11)
    out = tmp_path / f"{REGION}.conditioned.npz"
    wcn.write_conditioned_npz(
        m=m, **_sidecars(n), lower_triangular=False,
        out_npz=str(out), region_id=REGION, ceiling_frac=0.5,
    )
    z = np.load(out, allow_pickle=False)
    assert int(z["n_zeroed"]) == 2                         # == record n_zeroed_pairs
    pairs = z["zeroed_pairs"]
    assert pairs.shape == (2, 2)
    assert sorted(map(tuple, pairs.tolist())) == [(5, 30), (10, 11)]
    assert str(z["nan_policy"]) == "off_diagonal_zero"
    assert str(z["psd_method"]) == "PENDING_FIT_TIME"      # fit-time placeholder (§5)
    assert np.isnan(float(z["psd_lambda"]))                # fit-time placeholder (§5)
    assert float(z["ceiling_frac"]) == pytest.approx(0.5)


def test_lower_triangular_flag_preserved_square(tmp_path):
    n = 24
    m = _clean_symmetric(n)
    _set_pair_nan(m, 3, 9)
    out = tmp_path / f"{REGION}.conditioned.npz"
    wcn.write_conditioned_npz(
        m=m, **_sidecars(n), lower_triangular=False,
        out_npz=str(out), region_id=REGION, ceiling_frac=0.5,
    )
    z = np.load(out, allow_pickle=False)
    flag = z["lower_triangular"]
    val = bool(flag[0]) if getattr(flag, "shape", ()) == (1,) else bool(flag)
    assert val is False                                    # square source -> False, preserved


def test_lower_triangular_true_preserved(tmp_path):
    n = 24
    m = _clean_symmetric(n)
    out = tmp_path / f"{REGION}.conditioned.npz"
    wcn.write_conditioned_npz(
        m=m, **_sidecars(n), lower_triangular=True,
        out_npz=str(out), region_id=REGION, ceiling_frac=0.5,
    )
    z = np.load(out, allow_pickle=False)
    flag = z["lower_triangular"]
    val = bool(flag[0]) if getattr(flag, "shape", ()) == (1,) else bool(flag)
    assert val is True


# --------------------------------------------------------------------------- #
# CLEAN input -> conditioned artifact with n_zeroed==0 (BRANCH_AFR_COND_CLEAN) #
# --------------------------------------------------------------------------- #

def test_clean_input_writes_zero_provenance(tmp_path):
    n = 32
    m = _clean_symmetric(n)
    out = tmp_path / f"{REGION}.conditioned.npz"
    wcn.write_conditioned_npz(
        m=m, **_sidecars(n), lower_triangular=False,
        out_npz=str(out), region_id=REGION,
    )
    z = np.load(out, allow_pickle=False)
    assert int(z["n_zeroed"]) == 0
    assert z["zeroed_pairs"].shape == (0, 2)
    assert not np.isnan(z["ld"]).any()


# --------------------------------------------------------------------------- #
# Out-path guard: cannot clobber the raw {region}.npz contract                 #
# --------------------------------------------------------------------------- #

def test_out_path_must_be_conditioned_suffix(tmp_path):
    n = 16
    m = _clean_symmetric(n)
    bad = tmp_path / f"{REGION}.npz"                       # raw suffix -> refuse
    with pytest.raises(ValueError, match="conditioned"):
        wcn.write_conditioned_npz(
            m=m, **_sidecars(n), lower_triangular=False,
            out_npz=str(bad), region_id=REGION,
        )
    assert not bad.exists()


def test_out_path_rejects_raw_region_path(tmp_path):
    n = 16
    m = _clean_symmetric(n)
    other = tmp_path / "something_else.npz"
    with pytest.raises(ValueError):
        wcn.write_conditioned_npz(
            m=m, **_sidecars(n), lower_triangular=False,
            out_npz=str(other), region_id=REGION,
        )


def test_preexisting_raw_npz_unchanged_after_conditioned_write(tmp_path):
    import hashlib
    n = 32
    # a pre-existing raw {region}.npz on disk
    raw = tmp_path / f"{REGION}.npz"
    np.savez_compressed(raw, ld=_clean_symmetric(n), lower_triangular=np.array([False]))
    raw_sha_before = hashlib.sha256(raw.read_bytes()).hexdigest()
    # a conditioned write to the sibling path
    m = _clean_symmetric(n)
    _set_pair_nan(m, 4, 20)
    out = tmp_path / f"{REGION}.conditioned.npz"
    wcn.write_conditioned_npz(
        m=m, **_sidecars(n), lower_triangular=False,
        out_npz=str(out), region_id=REGION, ceiling_frac=0.5,
    )
    assert out.exists()
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == raw_sha_before  # raw byte-unchanged


# --------------------------------------------------------------------------- #
# RAISE propagates from condition_ld_matrix -> no artifact written            #
# --------------------------------------------------------------------------- #

def test_fully_nan_row_raise_propagates_no_file(tmp_path):
    n = 40
    m = _clean_symmetric(n)
    k = 7
    m[k, :] = NAN32
    m[:, k] = NAN32
    np.fill_diagonal(m, 1.0)
    out = tmp_path / f"{REGION}.conditioned.npz"
    with pytest.raises(ValueError):
        wcn.write_conditioned_npz(
            m=m, **_sidecars(n), lower_triangular=False,
            out_npz=str(out), region_id=REGION, ceiling_frac=0.5,
        )
    assert not out.exists()


def test_over_ceiling_raise_propagates_no_file(tmp_path):
    n = 40
    m = _clean_symmetric(n)
    for (i, j) in [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)]:
        _set_pair_nan(m, i, j)
    out = tmp_path / f"{REGION}.conditioned.npz"
    with pytest.raises(ValueError, match="BRANCH_AFR_COND_DEFERRED"):
        wcn.write_conditioned_npz(
            m=m, **_sidecars(n), lower_triangular=False,
            out_npz=str(out), region_id=REGION, ceiling_frac=0.05,
        )
    assert not out.exists()
