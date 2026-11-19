"""15.5b: UKB native panels hold at most one variant per CHR:POS (DEC-2026-11-18-ta-r4-ukb-native-multiallelic-a1).
At a multi-variant position the single SNV is kept, else the position is dropped; lone variants (indels too) stay."""
from __future__ import annotations

import ast
import gzip
import os
import shlex
import types
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import scipy.sparse as sp

from ta_r4 import paths as r4paths
from ta_r4 import ukb337k_tiles as ukb

REPO = Path(__file__).resolve().parents[2]
RULES = REPO / "src/snakemake/rules/ta_r4_panels_afr_ukb.smk"
RSCRIPT = os.environ.get("RSCRIPT", "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript")
NEW_KEYS = {"n_sites_multiallelic", "n_sites_kept_snv", "n_sites_dropped_all", "n_var_dropped_multiallelic"}


def _ma():
    from ta_r4 import ukb_native_multiallelic as ma
    return ma


def _corr(n, seed=3):
    rng = np.random.default_rng(seed)
    C = np.corrcoef(rng.standard_normal((300, n)) @ rng.standard_normal((n, n)), rowvar=False)
    C = (C + C.T) / 2
    np.fill_diagonal(C, 1.0)
    return C


def _v(rows, chrom="12"):
    return pd.DataFrame([{"SNP_ID": s, "CHR": chrom, "POS": p, "REF": r, "ALT": a} for s, p, r, a in rows])


def _run(rows):
    v = _v(rows)
    R = _corr(len(v))
    return (R, v, *_ma().resolve_multiallelic_positions(R.copy(), v.copy()))


def _check_submatrix(R, v, Rk, vk, keep):
    keep = np.asarray(keep)
    assert np.array_equal(Rk, R[np.ix_(keep, keep)])
    pd.testing.assert_frame_equal(vk, v.iloc[keep].reset_index(drop=True))


def _actions(audit):
    return dict(zip(audit["SNP_ID"], audit["action"]))


def test_a_snv_plus_indel_keeps_the_snv():
    R, v, Rk, vk, audit, st = _run([("s1", 100, "A", "G"), ("snv", 200, "G", "T"), ("ind", 200, "G", "GT"),
                                     ("s3", 300, "C", "T")])
    _check_submatrix(R, v, Rk, vk, [0, 1, 3])
    assert _actions(audit) == {"snv": "kept_snv", "ind": "dropped"}
    assert set(audit["class"]) == {"one_snv"} and set(audit["n_at_pos"]) == {2} and set(audit["n_snv"]) == {1}
    assert st == {"n_sites_multiallelic": 1, "n_sites_kept_snv": 1, "n_sites_dropped_all": 0,
                  "n_var_dropped_multiallelic": 1}


def test_a2_star_allele_is_not_an_snv():
    assert _ma().is_snv("A", "G") and not _ma().is_snv("A", "*") and not _ma().is_snv("N", "A")
    R, v, Rk, vk, audit, st = _run([("ag", 500, "A", "G"), ("star", 500, "A", "*")])
    _check_submatrix(R, v, Rk, vk, [0])
    assert _actions(audit) == {"ag": "kept_snv", "star": "dropped"}
    assert set(audit["class"]) == {"one_snv"} and set(audit["n_snv"]) == {1}


def test_b_indel_plus_indel_drops_both():
    R, v, Rk, vk, audit, st = _run([("x", 100, "C", "T"), ("rsA", 200, "A", "AAAAC"), ("rsA", 200, "AAAAC", "A")])
    _check_submatrix(R, v, Rk, vk, [0])
    assert list(audit["action"]) == ["dropped", "dropped"] and set(audit["class"]) == {"no_snv"}
    assert st == {"n_sites_multiallelic": 1, "n_sites_kept_snv": 0, "n_sites_dropped_all": 1,
                  "n_var_dropped_multiallelic": 2}


def test_c_snv_plus_snv_drops_both():
    R, v, Rk, vk, audit, st = _run([("ac", 200, "A", "C"), ("ag", 200, "A", "G"), ("y", 300, "G", "A")])
    _check_submatrix(R, v, Rk, vk, [2])
    assert _actions(audit) == {"ac": "dropped", "ag": "dropped"} and set(audit["class"]) == {"multi_snv"}
    assert set(audit["n_snv"]) == {2}
    assert st["n_sites_dropped_all"] == 1 and st["n_var_dropped_multiallelic"] == 2


def test_d_lone_indel_and_lone_snv_are_kept():
    R, v, Rk, vk, audit, st = _run([("ind", 100, "C", "CA"), ("snv", 200, "G", "A"), ("del", 300, "TTA", "T")])
    _check_submatrix(R, v, Rk, vk, [0, 1, 2])
    assert len(audit) == 0


def test_e_no_multi_variant_position_is_identity():
    R, v, Rk, vk, audit, st = _run([("a", 100, "C", "T"), ("b", 200, "G", "A")])
    assert np.array_equal(Rk, R)
    pd.testing.assert_frame_equal(vk, v)
    assert st == {k: 0 for k in NEW_KEYS} and len(audit) == 0
    assert {"n_at_pos", "n_snv", "class", "action"} <= set(audit.columns)


def test_keyed_by_chr_and_pos_and_order_kept():
    """Same POS on two chromosomes is not a multi-variant position; interleaved rows keep their order."""
    v = pd.concat([_v([("a", 100, "C", "T"), ("i", 200, "G", "GA")]),
                   _v([("b", 100, "C", "CA")], chrom="13"), _v([("s", 200, "G", "C")])], ignore_index=True)
    R = _corr(4)
    Rk, vk, audit, st = _ma().resolve_multiallelic_positions(R, v)
    _check_submatrix(R, v, Rk, vk, [0, 2, 3])
    assert _actions(audit) == {"i": "dropped", "s": "kept_snv"}


# --- T-f: the real PYHIN1_1q23 site -----------------------------------------------------------------------------------
@pytest.mark.r4_heavy
def test_f_real_pyhin1_160680184_keeps_rs184461353():
    tiles = ukb.region_tiles("1", 158000000, 162000000)
    if not tiles or not all(Path(p).is_file() for t in tiles for p in t):
        pytest.skip("UKB tiles for PYHIN1_1q23 are not on disk")
    v = pd.concat([ukb.read_tile_variants(gz) for _, gz in tiles], ignore_index=True)
    v = v[(v["CHR"] == "1") & (v["POS"] == 160680184)].drop_duplicates(["CHR", "POS", "REF", "ALT"])
    ids = set(v["SNP_ID"])
    assert "rs184461353" in ids, f"UKB tiles lack rs184461353 at 1:160680184 (have {sorted(ids)})"
    assert "rs143145026" in ids, f"UKB tiles lack rs143145026 at 1:160680184 (have {sorted(ids)})"
    cat = pd.read_csv(r4paths.catalog_path("r4", "PYHIN1_1q23"), sep="\t", dtype={"CHR": str, "REF": str, "ALT": str})
    allowed = set(ukb._allele_keys(cat[cat["POS"] == 160680184]))
    v = v[[k in allowed for k in ukb._allele_keys(v)]].reset_index(drop=True)
    assert set(v["SNP_ID"]) == {"rs184461353", "rs143145026"}, "catalog filter did not keep both rows"
    Rk, vk, audit, st = _ma().resolve_multiallelic_positions(np.eye(len(v)), v)
    assert list(vk["SNP_ID"]) == ["rs184461353"] and {vk.at[0, "REF"], vk.at[0, "ALT"]} == {"A", "G"}
    assert _actions(audit) == {"rs184461353": "kept_snv", "rs143145026": "dropped"}
    assert np.array_equal(Rk, np.eye(1))


# --- T-g: build_native_multiallelic resolves after the catalog filter -------------------------------------------------
TILE_ROWS = [("rs10", 10, "G", "A"), ("rs20s", 20, "T", "C"), ("rs20i", 20, "CA", "C"),
             ("rs30s", 30, "A", "G"), ("rs30i", 30, "GA", "G"), ("rs40", 40, "TTA", "T")]
TILE_C = _corr(len(TILE_ROWS), seed=7)


def _write_tile(tmp_path, name, idx):
    """TILE_ROWS[idx] (rsid, pos, allele1=ALT, allele2=REF); one lower triangle with diag 0.5 (the UKB convention)."""
    C = TILE_C[np.ix_(idx, idx)]
    M = np.tril(C, -1) + 0.5 * np.eye(len(idx))
    npz, gz = tmp_path / f"{name}.npz", tmp_path / f"{name}.gz"
    sp.save_npz(npz, sp.coo_matrix(M), compressed=True)
    with gzip.open(gz, "wt") as fh:
        fh.write("rsid\tchromosome\tposition\tallele1\tallele2\n")
        for i in idx:
            rs, p, a1, a2 = TILE_ROWS[i]
            fh.write(f"{rs}\t12\t{p}\t{a1}\t{a2}\n")
    return npz, gz


def _fixture(tmp_path):
    """Tile a = 10, 20 SNV, 20 indel, 30 SNV; tile b = 30 SNV, 30 indel, 40. At 30 the tiles hold an SNV and an
    indel but the catalog only the indel -> a lone (kept) indel in the panel. The dropped 20 indel shares no tile
    with 30i / 40, so the drop removes 2 zero-filled pairs."""
    tiles = [_write_tile(tmp_path, "a", [0, 1, 2, 3]), _write_tile(tmp_path, "b", [3, 4, 5])]
    cat = pd.DataFrame({"CHR": ["12"] * 5, "POS": [10, 20, 20, 30, 40], "REF": ["A", "C", "C", "G", "T"],
                        "ALT": ["G", "T", "CA", "GA", "TTA"], "SNP_ID": ["c10", "c20s", "c20i", "c30i", "c40"]})
    cat.to_csv(tmp_path / "cat.tsv", sep="\t", index=False)
    return tiles, tmp_path / "cat.tsv"


def test_g_build_native_multiallelic_resolves_after_the_catalog_filter(tmp_path):
    tiles, cat = _fixture(tmp_path)
    R, v, st, audit = _ma().build_native_multiallelic(tiles, "12", 1, 100, cat)
    R0, v0, st0 = ukb.build_native(tiles, "12", 1, 100, cat)
    Rr, vr, ar, _ = _ma().resolve_multiallelic_positions(R0, v0)
    pd.testing.assert_frame_equal(audit, ar)
    assert np.array_equal(R, Rr)
    pd.testing.assert_frame_equal(v, vr)
    assert list(v["SNP_ID"]) == ["rs10", "rs20s", "rs30i", "rs40"]
    assert set(st) == set(st0) | NEW_KEYS
    same = set(st0) - {"n_var", "n_pairs_zero_filled"}
    assert {k: st[k] for k in same} == {k: st0[k] for k in same}
    assert st["n_var"] == len(v) == 4 and st0["n_var"] == 5
    assert st["n_sites_multiallelic"] == 1 and st["n_var_dropped_multiallelic"] == 1 and st["n_sites_kept_snv"] == 1
    # n_pairs_zero_filled describes the final panel: the tile-measured mask restricted to the kept rows
    _, va, _, filled = ukb.assemble_region(tiles, "12", 1, 100, allowed=set(ukb._allele_keys(pd.read_csv(cat, sep="\t"))),
                                           return_filled=True)
    keep = np.flatnonzero(va["SNP_ID"].isin(v["SNP_ID"]).to_numpy())
    f = filled[np.ix_(keep, keep)]
    assert st0["n_pairs_zero_filled"] == 6 and st["n_pairs_zero_filled"] == int((~f).sum() // 2) == 4


def test_i_cli_writes_panel_stats_and_audit(tmp_path, monkeypatch):
    if not Path(RSCRIPT).is_file():
        pytest.skip("no Rscript")
    monkeypatch.setenv("RSCRIPT", RSCRIPT)
    tiles, cat = _fixture(tmp_path)
    monkeypatch.setattr(ukb, "region_tiles", lambda c, s, e: tiles)
    out, stats = tmp_path / "p" / "X.rds", tmp_path / "s" / "X.stats.tsv"
    assert _ma().main(["build-native", "--region-id", "X", "--region-safe", "X", "--chr", "12", "--start", "1",
                       "--end", "100", "--catalog", str(cat), "--out", str(out), "--stats", str(stats)]) == 0
    R, v = ukb.read_rds(out, rscript=RSCRIPT)
    Re, ve, _, _ = _ma().build_native_multiallelic(tiles, "12", 1, 100, cat)
    assert np.array_equal(R, Re) and list(v["SNP_ID"]) == list(ve["SNP_ID"])
    srow = pd.read_csv(stats, sep="\t")
    assert NEW_KEYS <= set(srow.columns) and int(srow.at[0, "n_var"]) == 4
    audit = pd.read_csv(tmp_path / "s" / "X.multiallelic_resolved.tsv", sep="\t")
    assert dict(zip(audit["SNP_ID"], audit["action"])) == {"rs20s": "kept_snv", "rs20i": "dropped"}


# --- T-h: rule wiring (parsed rule objects) ---------------------------------------------------------------------------
def _rule_decorators():
    import snakemake.parser as sp_
    from snakemake.sourcecache import LocalSourceFile
    wf = types.SimpleNamespace(sourcecache=types.SimpleNamespace(open=lambda f: open(f.get_path_or_uri())))
    code, _, _ = sp_.parse(LocalSourceFile(str(RULES)), wf)
    out = {}
    for node in ast.walk(ast.parse(code)):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("__rule_"):
            d = {}
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                    d[dec.func.attr] = dec
            out[node.name[len("__rule_"):]] = d
    return out


def _shell_module(dec):
    toks = shlex.split(dec["shellcmd"].args[0].value.replace("\\\n", " "))
    i = toks.index("-m")
    return toks[i + 1], toks[i + 2]


def _inputs(dec):
    return {k.arg: k.value.value for k in dec["input"].keywords if isinstance(k.value, ast.Constant)}


def test_h_native_rule_uses_the_new_builder_and_isect_rule_is_unchanged():
    rules = _rule_decorators()
    nat, isect = rules["r4_panel_ukb_native"], rules["r4_panel_ukb_isect"]
    assert _shell_module(nat) == ("ta_r4.ukb_native_multiallelic", "build-native")
    assert "src/python/ta_r4/ukb_native_multiallelic.py" in _inputs(nat).values()
    assert {k.arg for k in nat["output"].keywords} == {"rds", "stats", "resolved"}
    assert _shell_module(isect) == ("ta_r4.ukb337k_tiles", "build-isect")
    assert "src/python/ta_r4/ukb_native_multiallelic.py" not in _inputs(isect).values()
