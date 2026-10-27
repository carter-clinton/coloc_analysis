"""W2b T2 live gate (Pitfall 10): the real UKB 337k tile chr12_111000001_114000001 loads with diag == 1 exactly and a
symmetric R, and its r signs agree with the 1000G EUR R4 SH2B3 panel after orienting both to the same ALT.
Skips only while the tile has not been fetched; once it is on disk every check must run."""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

from ta_r4 import ukb337k_tiles as ukb

pytestmark = pytest.mark.r4_heavy

REPO = Path(__file__).resolve().parents[2]
TILE = "chr12_111000001_114000001"
EUR_PANEL = REPO / "data/r4/ld/EUR_1kg_r4/SH2B3_12q24.rds"
OUT = REPO / "data/r4/findings/ukb_tile_sign_agreement.tsv"
MIN_AGREEMENT = 0.90


def _tile_paths():
    npz, gz = ukb.tile_paths(TILE, REPO / ukb.DOWNLOAD_DIR)
    if not (npz.is_file() and gz.is_file()):
        pytest.skip(f"{TILE} not fetched yet")
    return npz, gz


def _halved(npz):
    """The legacy download_ukbb_ld_tiles.py transform, on the stored diagonal: (M + M.T) / 2."""
    d = sp.load_npz(npz).diagonal().astype(np.float64)
    return (d + d) / 2


def test_real_tile_diag_exactly_one():
    npz, gz = _tile_paths()
    M = sp.load_npz(npz)
    assert ukb.tile_convention(M) == "lower_half_diag"
    d = ukb.full_diagonal(M)
    assert d.shape[0] == M.shape[0] > 1000
    assert np.array_equal(d, np.ones_like(d))


def test_halving_transform_breaks_diag():
    npz, _ = _tile_paths()
    d = _halved(npz)
    assert not np.array_equal(d, np.ones_like(d))


def test_real_tile_symmetric_in_blocks():
    npz, gz = _tile_paths()
    R, v = ukb.load_tile(npz, gz)
    assert R.shape == (len(v), len(v))
    assert np.array_equal(np.diag(R), np.ones(len(v)))
    blk, worst = 2000, 0.0
    for s in range(0, R.shape[0], blk):
        worst = max(worst, float(np.max(np.abs(R[s:s + blk, :] - R[:, s:s + blk].T))))
    assert worst <= 1e-8, worst
    assert np.isfinite(R).all()


def test_sign_agreement_with_1000g_eur():
    npz, gz = _tile_paths()
    if not EUR_PANEL.is_file():
        pytest.fail(f"missing W2a panel {EUR_PANEL}")
    R_1kg, v_1kg = ukb.read_rds(EUR_PANEL)
    v_all = ukb.read_tile_variants(gz)
    keep = np.flatnonzero(v_all["POS"].isin(set(v_1kg["POS"])).to_numpy())
    R_u, v_u = ukb.load_tile(npz, gz, keep=keep)
    R_o, v_o, st = ukb.orient_to_reference(R_u, v_u, v_1kg)
    idx = v_1kg.reset_index(drop=True).reset_index().merge(v_o[["CHR", "POS", "REF", "ALT"]], on=["CHR", "POS", "REF", "ALT"])
    assert len(idx) == len(v_o)
    R_k = R_1kg[np.ix_(idx["index"].to_numpy(), idx["index"].to_numpy())]
    iu = np.triu_indices(len(v_o), 1)
    strong = np.abs(R_k[iu]) > 0.5
    n_pairs = int(strong.sum())
    agree = int((np.sign(R_o[iu][strong]) == np.sign(R_k[iu][strong])).sum())
    rate = agree / n_pairs
    # mixed pairs (one variant flipped, the other not) are the only pairs whose sign D.R.D changes
    u_alt = {(c, p, frozenset((a, b))): b for c, p, a, b in zip(v_u["CHR"], v_u["POS"], v_u["REF"], v_u["ALT"])}
    flip = np.array([u_alt[(c, p, frozenset((a, b)))] != b
                     for c, p, a, b in zip(v_o["CHR"], v_o["POS"], v_o["REF"], v_o["ALT"])])
    assert int(flip.sum()) == st["n_flipped"]
    mixed = strong & (flip[iu[0]] != flip[iu[1]])
    n_mixed = int(mixed.sum())
    agree_mixed = int((np.sign(R_o[iu][mixed]) == np.sign(R_k[iu][mixed])).sum())
    rate_mixed = agree_mixed / n_mixed
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["tile", "panel", "n_var_1kg", "n_var_shared", "n_flipped", "n_dropped_allele_mismatch",
                    "n_dropped_palindromic", "n_pairs_abs_r_gt_0.5", "n_agree", "rate", "n_pairs_mixed",
                    "n_agree_mixed", "rate_mixed"])
        w.writerow([TILE, "EUR_1kg_r4/SH2B3_12q24", len(v_1kg), len(v_o), st["n_flipped"],
                    st["n_var_dropped_allele_mismatch"], st["n_var_dropped_palindromic"], n_pairs, agree, f"{rate:.6f}",
                    n_mixed, agree_mixed, f"{rate_mixed:.6f}"])
    print(f"sign agreement {agree}/{n_pairs} = {rate:.6f} over {len(v_o)} shared variants (n_flipped {st['n_flipped']});"
          f" mixed-orientation pairs {agree_mixed}/{n_mixed} = {rate_mixed:.6f}")
    assert n_pairs >= 100 and n_mixed >= 20
    assert rate >= MIN_AGREEMENT, rate
    assert rate_mixed >= MIN_AGREEMENT, rate_mixed
