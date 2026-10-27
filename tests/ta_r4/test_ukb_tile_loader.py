"""W2b T2: UKB 337k tile loader (synthetic). Triangle/diagonal convention (Pitfall 10), region assembly over
overlapping tiles, and D.R.D re-orientation to a reference panel's REF/ALT (checker W2)."""
from __future__ import annotations

import gzip
import os

import numpy as np
import pandas as pd
import pytest
import scipy.sparse as sp

from ta_r4 import ukb337k_tiles as ukb

RSCRIPT = os.environ.get("RSCRIPT", "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript")


def _write_tile(tmp_path, name, M, pos, a1, a2, chrom="12"):
    npz, gz = tmp_path / f"{name}.npz", tmp_path / f"{name}.gz"
    sp.save_npz(npz, sp.coo_matrix(M), compressed=True)
    with gzip.open(gz, "wt") as fh:
        fh.write("rsid\tchromosome\tposition\tallele1\tallele2\n")
        for i, (p, x, y) in enumerate(zip(pos, a1, a2)):
            fh.write(f"rs{p}\t{chrom}\t{p}\t{x}\t{y}\n")
    return npz, gz


def _corr(n=4, seed=1):
    rng = np.random.default_rng(seed)
    G = rng.standard_normal((200, n)) @ rng.standard_normal((n, n))
    C = np.corrcoef(G, rowvar=False)
    C = (C + C.T) / 2
    np.fill_diagonal(C, 1.0)
    return C


FULL = _corr()
POS = [100, 200, 300, 400]
A1 = ["A", "C", "G", "T"]
A2 = ["G", "T", "A", "C"]


def test_lower_triangle_half_diag(tmp_path):
    M = np.tril(FULL, -1) + 0.5 * np.eye(4)
    R, v = ukb.load_tile(*_write_tile(tmp_path, "t", M, POS, A1, A2))
    assert np.array_equal(np.diag(R), np.ones(4))
    np.testing.assert_allclose(R, FULL, atol=1e-12)
    assert np.array_equal(R, R.T)


def test_upper_triangle_half_diag(tmp_path):
    M = np.triu(FULL, 1) + 0.5 * np.eye(4)
    R, _ = ukb.load_tile(*_write_tile(tmp_path, "t", M, POS, A1, A2))
    np.testing.assert_allclose(R, FULL, atol=1e-12)


def test_one_triangle_unit_diag(tmp_path):
    M = np.tril(FULL)
    R, _ = ukb.load_tile(*_write_tile(tmp_path, "t", M, POS, A1, A2))
    assert np.array_equal(np.diag(R), np.ones(4))
    np.testing.assert_allclose(R, FULL, atol=1e-12)


def test_symmetric_unchanged(tmp_path):
    R, _ = ukb.load_tile(*_write_tile(tmp_path, "t", FULL, POS, A1, A2))
    np.testing.assert_allclose(R, FULL, atol=1e-12)


@pytest.mark.parametrize("diag", [[0.5, 0.5, 1.0, 0.5], [0.9, 0.9, 0.9, 0.9], [0.0] * 4])
def test_other_diagonal_refused(tmp_path, diag):
    M = np.tril(FULL, -1) + np.diag(diag)
    with pytest.raises(ukb.TileConventionError):
        ukb.load_tile(*_write_tile(tmp_path, "t", M, POS, A1, A2))


def test_half_diag_both_triangles_refused(tmp_path):
    M = FULL - 0.5 * np.eye(4)  # both triangles, diag 0.5: M + M.T would double every r
    with pytest.raises(ukb.TileConventionError):
        ukb.load_tile(*_write_tile(tmp_path, "t", M, POS, A1, A2))


def test_variants_frame(tmp_path):
    M = np.tril(FULL, -1) + 0.5 * np.eye(4)
    _, v = ukb.load_tile(*_write_tile(tmp_path, "t", M, POS, A1, A2))
    assert list(v["ALT"]) == A1 and list(v["REF"]) == A2
    assert list(v["POS"]) == POS and list(v["CHR"]) == ["12"] * 4
    assert list(v["SNP_ID"]) == [f"rs{p}" for p in POS]


def test_keep_subset(tmp_path):
    M = np.tril(FULL, -1) + 0.5 * np.eye(4)
    R, v = ukb.load_tile(*_write_tile(tmp_path, "t", M, POS, A1, A2), keep=[0, 2, 3])
    np.testing.assert_allclose(R, FULL[np.ix_([0, 2, 3], [0, 2, 3])], atol=1e-12)
    assert list(v["POS"]) == [100, 300, 400]


def test_tile_names_for():
    assert ukb.tile_names_for("12", 111_400_000, 112_000_000) == [
        "chr12_109000001_112000001", "chr12_110000001_113000001", "chr12_111000001_114000001"]
    assert ukb.tile_names_for("1", 1, 500_000) == ["chr1_1_3000001"]


def test_covering_tiles_single_when_region_fits():
    names = ukb.covering_tiles("12", 111_400_000, 112_000_000)
    assert len(names) == 1
    s, e = (int(x) for x in names[0].split("_")[1:])
    assert s <= 111_400_000 and e >= 112_000_000


def test_covering_tiles_wide_region_drops_dominated():
    names = ukb.covering_tiles("1", 158_000_000, 162_000_000)
    clipped = [(max(int(n.split("_")[1]), 158_000_000), min(int(n.split("_")[2]), 162_000_000)) for n in names]
    for i, a in enumerate(clipped):
        for j, b in enumerate(clipped):
            if i != j:
                assert not (b[0] <= a[0] and a[1] <= b[1]), (a, b)
    # every pair <= 2 Mb apart inside the region shares a kept tile
    for p in range(158_000_000, 160_000_001, 250_000):
        q = p + 2_000_000
        assert any(s <= p and q <= e for s, e in clipped), (p, q)


# --- assemble_region over overlapping synthetic tiles ---------------------------------------------------------------
BIG = _corr(6, seed=7)
BPOS = [10, 20, 30, 40, 50, 60]
BA1 = list("ACGTAC")
BA2 = list("GTACGT")


def _tile(tmp_path, name, idx, R=BIG):
    sub = R[np.ix_(idx, idx)]
    M = np.tril(sub, -1) + 0.5 * np.eye(len(idx))
    return _write_tile(tmp_path, name, M, [BPOS[i] for i in idx], [BA1[i] for i in idx], [BA2[i] for i in idx])


def test_assemble_overlapping_tiles(tmp_path):
    tiles = [_tile(tmp_path, "a", [0, 1, 2, 3]), _tile(tmp_path, "b", [2, 3, 4, 5])]
    R, v, st = ukb.assemble_region(tiles, "12", 1, 100)
    assert list(v["POS"]) == BPOS
    covered = np.zeros((6, 6), bool)
    covered[np.ix_([0, 1, 2, 3], [0, 1, 2, 3])] = True
    covered[np.ix_([2, 3, 4, 5], [2, 3, 4, 5])] = True
    np.testing.assert_allclose(R[covered], BIG[covered], atol=1e-12)
    assert np.all(R[~covered] == 0)
    assert st["n_pairs_zero_filled"] == int((~covered).sum() // 2) == 4
    assert st["n_tiles"] == 2 and st["n_var"] == 6
    assert np.array_equal(np.diag(R), np.ones(6))


def test_assemble_disagreement_raises(tmp_path):
    other = BIG.copy()
    other[2, 3] = other[3, 2] = BIG[2, 3] + 1e-3
    tiles = [_tile(tmp_path, "a", [0, 1, 2, 3]), _tile(tmp_path, "b", [2, 3, 4, 5], R=other)]
    with pytest.raises(ukb.TileDisagreementError):
        ukb.assemble_region(tiles, "12", 1, 100)


def test_assemble_keep_positions_and_bounds(tmp_path):
    tiles = [_tile(tmp_path, "a", [0, 1, 2, 3]), _tile(tmp_path, "b", [2, 3, 4, 5])]
    R, v, st = ukb.assemble_region(tiles, "12", 15, 55, keep_positions={20, 40, 50, 60})
    assert list(v["POS"]) == [20, 40, 50]
    np.testing.assert_allclose(R, BIG[np.ix_([1, 3, 4], [1, 3, 4])] * np.array(
        [[1, 1, 0], [1, 1, 1], [0, 1, 1]]), atol=1e-12)
    assert st["n_pairs_zero_filled"] == 1


# --- orient_to_reference: the D.R.D known answer ---------------------------------------------------------------------
def _fixture():
    rng = np.random.default_rng(20261026)
    hap = rng.random((400, 3))
    x1 = (hap[:, 0] < 0.4).astype(float) + (rng.random(400) < 0.4)
    x2 = np.clip(x1 + (rng.random(400) < 0.3) - (rng.random(400) < 0.2), 0, 2)
    x3 = np.clip(x2 + (rng.random(400) < 0.25) - (rng.random(400) < 0.25), 0, 2)
    G = np.column_stack([x1, x2, x3])
    R_ref = np.corrcoef(G, rowvar=False)
    G_swap = G.copy()
    G_swap[:, 1] = 2 - G_swap[:, 1]
    R_swap = np.corrcoef(G_swap, rowvar=False)
    ref = pd.DataFrame({"SNP_ID": ["rs1", "rs2", "rs3"], "CHR": ["12"] * 3, "POS": [100, 200, 300],
                        "REF": ["A", "C", "G"], "ALT": ["G", "T", "A"]})
    swapped = ref.copy()
    swapped.loc[1, ["REF", "ALT"]] = ["T", "C"]
    swapped["SNP_ID"] = ["u1", "u2", "u3"]
    return R_ref, R_swap, ref, swapped


def test_fixture_signs():
    R_ref, R_swap, _, _ = _fixture()
    assert abs(R_ref[0, 1]) > 0.1 and abs(R_ref[1, 2]) > 0.1
    np.testing.assert_allclose(R_swap[0, 1], -R_ref[0, 1], atol=1e-12)
    np.testing.assert_allclose(R_swap[1, 2], -R_ref[1, 2], atol=1e-12)
    np.testing.assert_allclose(R_swap[0, 2], R_ref[0, 2], atol=1e-12)


def test_orient_known_answer():
    R_ref, R_swap, ref, swapped = _fixture()
    R, v, st = ukb.orient_to_reference(R_swap, swapped, ref)
    np.testing.assert_allclose(R, R_ref, atol=1e-12, rtol=0)
    assert np.sign(R[0, 1]) == np.sign(R_ref[0, 1])
    assert list(v["REF"]) == list(ref["REF"]) and list(v["ALT"]) == list(ref["ALT"])
    assert list(v["POS"]) == list(ref["POS"]) and list(v["SNP_ID"]) == list(ref["SNP_ID"])
    assert st["n_flipped"] == 1
    assert st["n_var_dropped_allele_mismatch"] == 0 and st["n_var_dropped_palindromic"] == 0


def test_orient_follows_reference_order():
    R_ref, R_swap, ref, swapped = _fixture()
    perm = [2, 0, 1]
    R, v, _ = ukb.orient_to_reference(R_swap[np.ix_(perm, perm)], swapped.iloc[perm].reset_index(drop=True), ref)
    np.testing.assert_allclose(R, R_ref, atol=1e-12, rtol=0)
    assert list(v["POS"]) == [100, 200, 300]


def test_orient_drops_allele_mismatch_and_palindromes():
    R_ref, R_swap, ref, swapped = _fixture()
    swapped = swapped.copy()
    swapped.loc[0, ["REF", "ALT"]] = ["A", "C"]  # {A,C} vs reference {A,G}
    ref2 = ref.copy()
    ref2.loc[2, ["REF", "ALT"]] = ["C", "G"]
    swapped.loc[2, ["REF", "ALT"]] = ["G", "C"]  # palindromic: orientation cannot be read from the alleles
    R, v, st = ukb.orient_to_reference(R_swap, swapped, ref2)
    assert st["n_var_dropped_allele_mismatch"] == 1
    assert st["n_var_dropped_palindromic"] == 1
    assert list(v["POS"]) == [200] and R.shape == (1, 1) and R[0, 0] == 1.0


def test_orient_counts_variants_absent_from_reference():
    R_ref, R_swap, ref, swapped = _fixture()
    R, v, st = ukb.orient_to_reference(R_swap, swapped, ref.iloc[[0, 1]].reset_index(drop=True))
    assert st["n_var_not_in_reference"] == 1 and len(v) == 2
    np.testing.assert_allclose(R, R_ref[:2, :2], atol=1e-12, rtol=0)


# --- .rds round trip --------------------------------------------------------------------------------------------------
def test_write_read_rds_roundtrip(tmp_path):
    rscript = RSCRIPT
    R = BIG
    v = pd.DataFrame({"SNP_ID": [f"rs{p}" for p in BPOS], "CHR": ["12"] * 6, "POS": BPOS, "REF": BA2, "ALT": BA1})
    out = tmp_path / "x.rds"
    ukb.write_rds(R, v, out, ld_source="unit", region_id="X", rscript=rscript)
    R2, v2 = ukb.read_rds(out, rscript=rscript)
    assert np.array_equal(R2, R)
    assert list(v2["POS"]) == BPOS and list(v2["ALT"]) == BA1 and list(v2["CHR"]) == ["12"] * 6


def test_fetch_tile_records_head_size(tmp_path, monkeypatch):
    calls = []

    def fake_head(url):
        return (1234 if url.endswith(".npz") else 56), ('"abc-3"' if url.endswith(".npz") else '"0123456789abcdef0123456789abcdef"')

    def fake_fetch(url, dest_dir, md5=None, sha256=None, size=None, magic=("gzip",), **kw):
        calls.append((url, size, md5, magic))
        p = tmp_path / "dl" / url.rsplit("/", 1)[1]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"x")
        return {"path": str(p), "size": size, "md5": md5 or "m", "sha256": "s", "magic": list(magic)}

    monkeypatch.setattr(ukb, "_head", fake_head)
    monkeypatch.setattr(ukb, "fetch_verified", fake_fetch)
    man = tmp_path / "m.tsv"
    ukb.fetch_tile("chr12_111000001_114000001", dest_root=tmp_path / "dl", manifest=man, downloads_root=tmp_path)
    rows = pd.read_csv(man, sep="\t", dtype=str)
    assert list(rows["file"]) == ["chr12_111000001_114000001.gz", "chr12_111000001_114000001.npz"]
    assert list(rows["size_bytes"]) == ["56", "1234"]
    gz_call = next(c for c in calls if c[0].endswith(".gz"))
    npz_call = next(c for c in calls if c[0].endswith(".npz"))
    assert gz_call[2] == "0123456789abcdef0123456789abcdef"  # single-part ETag is the md5
    assert npz_call[2] is None and npz_call[3] == ("zip",)  # multipart ETag is not an md5


def test_covering_tiles_only_from_available():
    all_names = ukb.tile_names_for("6", 25_000_000, 35_000_000)
    gone = {"chr6_28000001_31000001", "chr6_29000001_32000001", "chr6_30000001_33000001"}
    names = ukb.covering_tiles("6", 25_000_000, 35_000_000, available=set(all_names) - gone)
    assert not gone & set(names)
    assert "chr6_27000001_30000001" in names and "chr6_31000001_34000001" in names


# --- W2b T3: allele-checked assembly, native and isect panel builders -------------------------------------------------
def _keys(pos, a, b):
    return {(int(p), frozenset((x, y))) for p, x, y in zip(pos, a, b)}


def test_assemble_allowed_drops_allele_mismatch(tmp_path):
    tiles = [_tile(tmp_path, "a", [0, 1, 2, 3]), _tile(tmp_path, "b", [2, 3, 4, 5])]
    allowed = _keys(BPOS, BA1, BA2) - {(30, frozenset(("G", "A")))} | {(30, frozenset(("G", "C")))}
    R, v, st = ukb.assemble_region(tiles, "12", 1, 100, allowed=allowed)
    keep = [0, 1, 3, 4, 5]
    assert list(v["POS"]) == [BPOS[i] for i in keep]
    assert st["n_var_dropped_allele_mismatch"] == 1
    covered = np.zeros((6, 6), bool)
    covered[np.ix_([0, 1, 2, 3], [0, 1, 2, 3])] = True
    covered[np.ix_([2, 3, 4, 5], [2, 3, 4, 5])] = True
    c = covered[np.ix_(keep, keep)]
    np.testing.assert_allclose(R[c], BIG[np.ix_(keep, keep)][c], atol=1e-12)
    assert st["n_pairs_zero_filled"] == int((~c).sum() // 2) == 4


def _write_catalog(path, pos, ref, alt):
    pd.DataFrame({"CHR": ["12"] * len(pos), "POS": pos, "REF": ref, "ALT": alt,
                  "SNP_ID": [f"c{p}" for p in pos]}).to_csv(path, sep="\t", index=False)
    return path


def test_build_native(tmp_path):
    tiles = [_tile(tmp_path, "a", [0, 1, 2, 3]), _tile(tmp_path, "b", [2, 3, 4, 5])]
    # catalog: 10 (alleles transposed: still the same unordered pair), 20, 40 with a different allele pair, 60; 70 absent
    cat = _write_catalog(tmp_path / "cat.tsv", [10, 20, 40, 60, 70], ["A", "T", "A", "C", "A"], ["G", "C", "G", "T", "G"])
    R, v, st = ukb.build_native(tiles, "12", 1, 100, cat)
    assert list(v["POS"]) == [10, 20, 60]
    assert list(v["ALT"]) == [BA1[0], BA1[1], BA1[5]] and list(v["REF"]) == [BA2[0], BA2[1], BA2[5]]
    assert st["n_var_dropped_allele_mismatch"] == 1 and st["n_var"] == 3 and st["n_tiles"] == 2
    np.testing.assert_allclose(R[:2, :2], BIG[np.ix_([0, 1], [0, 1])], atol=1e-12)
    assert R[0, 2] == 0 and st["n_pairs_zero_filled"] == 2


def _ref_panel():
    """A 1000G-like reference over BPOS[1:] whose labels are REF/ALT-transposed at 20 and 50 relative to the tiles
    (so R_ref = D.BIG.D there) and an allele mismatch at 40."""
    idx = [1, 2, 3, 4, 5]
    s = np.array([-1.0, 1.0, 1.0, -1.0, 1.0])
    R_ref = BIG[np.ix_(idx, idx)] * np.outer(s, s)
    ref_alt = [BA2[1], BA1[2], "C", BA2[4], BA1[5]]
    ref_ref = [BA1[1], BA2[2], "A", BA1[4], BA2[5]]
    v = pd.DataFrame({"SNP_ID": [f"rs{BPOS[i]}" for i in idx], "CHR": ["12"] * 5, "POS": [BPOS[i] for i in idx],
                      "A1": ref_alt, "A2": ref_ref, "REF": ref_ref, "ALT": ref_alt})
    return R_ref, v


def test_build_isect_known_answer(tmp_path):
    tiles = [_tile(tmp_path, "a", [0, 1, 2, 3]), _tile(tmp_path, "b", [2, 3, 4, 5])]
    R_ref, v_ref = _ref_panel()
    R_u, R_k, v, st = ukb.build_isect(tiles, "12", 1, 100, R_ref, v_ref)
    keep = [0, 1, 3, 4]  # reference rows kept: 20, 30, 50, 60 (40 dropped: allele mismatch)
    assert list(v["POS"]) == [20, 30, 50, 60]
    pd.testing.assert_frame_equal(v, v_ref.iloc[keep].reset_index(drop=True))
    np.testing.assert_allclose(R_k, R_ref[np.ix_(keep, keep)], atol=0, rtol=0)
    covered = np.array([[1, 1, 0, 0], [1, 1, 1, 1], [0, 1, 1, 1], [0, 1, 1, 1]], bool)  # 20 and 50/60 share no tile
    np.testing.assert_allclose(R_u[covered], R_k[covered], atol=1e-12)
    assert np.all(R_u[~covered] == 0)
    assert st["n_flipped"] == 2 and st["n_var_dropped_allele_mismatch"] == 1 and st["n_var"] == 4
    assert st["n_pairs_zero_filled"] == 2
    assert st["n_agree"] + st["n_disagree"] == st["n_pairs_abs_r_gt_0.5"]


def test_build_isect_rds_frames_identical(tmp_path):
    rscript = RSCRIPT
    tiles = [_tile(tmp_path, "a", [0, 1, 2, 3]), _tile(tmp_path, "b", [2, 3, 4, 5])]
    R_ref, v_ref = _ref_panel()
    ref_rds = ukb.write_rds(R_ref, v_ref, tmp_path / "ref.rds", ld_source="ref", rscript=rscript)
    st = ukb.write_isect_panels(tiles, "12", 1, 100, ref_rds, tmp_path / "u.rds", tmp_path / "k.rds",
                                region_id="X", rscript=rscript)
    Ru, vu = ukb.read_rds(tmp_path / "u.rds", rscript=rscript)
    Rk, vk = ukb.read_rds(tmp_path / "k.rds", rscript=rscript)
    pd.testing.assert_frame_equal(vu, vk)
    assert list(vu.columns) == list(v_ref.columns) and st["n_var"] == 4
    assert np.array_equal(np.diag(Ru), np.ones(4)) and np.array_equal(Ru, Ru.T)


def test_build_isect_sign_agreement_skips_zero_filled(tmp_path):
    C = BIG.copy()
    C[1, 5] = C[5, 1] = 0.9  # strong, but 20 and 60 share no tile
    tiles = [_tile(tmp_path, "a", [0, 1, 2, 3], R=C), _tile(tmp_path, "b", [2, 3, 4, 5], R=C)]
    v_ref = pd.DataFrame({"SNP_ID": [f"rs{p}" for p in BPOS], "CHR": ["12"] * 6, "POS": BPOS, "REF": BA2, "ALT": BA1})
    _, _, _, st = ukb.build_isect(tiles, "12", 1, 100, C, v_ref)
    covered = np.zeros((6, 6), bool)
    covered[np.ix_([0, 1, 2, 3], [0, 1, 2, 3])] = True
    covered[np.ix_([2, 3, 4, 5], [2, 3, 4, 5])] = True
    iu = np.triu_indices(6, 1)
    expected = int((covered[iu] & (np.abs(C[iu]) > 0.5)).sum())
    assert st["n_pairs_abs_r_gt_0.5"] == expected == st["n_agree"]
    assert st["n_flipped"] == 0 and st["n_pairs_mixed"] == 0


def test_add_stats_columns(tmp_path):
    man = tmp_path / "m.tsv"
    man.write_text("ancestry\tregion_safe\tn_var\nEUR\tA\t3\nEUR\tB\t4\n")
    sd = tmp_path / "st"
    sd.mkdir()
    (sd / "A.stats.tsv").write_text("region_safe\tn_tiles\tn_flipped\nA\t1\t0\n")
    (sd / "B.stats.tsv").write_text("region_safe\tn_tiles\tn_flipped\nB\t3\t2\n")
    out = ukb.add_stats_columns(man, sd, ["n_tiles", "n_flipped"])
    assert list(out.columns) == ["ancestry", "region_safe", "n_var", "n_tiles", "n_flipped"]
    assert pd.read_csv(man, sep="\t", dtype=str)["n_flipped"].tolist() == ["0", "2"]
    (sd / "B.stats.tsv").unlink()
    man.write_text("ancestry\tregion_safe\tn_var\nEUR\tA\t3\nEUR\tB\t4\n")
    with pytest.raises(ValueError, match="without build stats"):
        ukb.add_stats_columns(man, sd, ["n_tiles"])
