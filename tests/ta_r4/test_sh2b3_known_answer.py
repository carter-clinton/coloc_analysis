"""W3b SH2B3 known answer (D-17): the R2-exact coloc per pair vs the frozen R2 JSONs, plus the separate
L10/iter-100 measurement. The live test does not assert a match (§B.10): mismatches are findings."""
from __future__ import annotations

import copy
import csv
import json

import pytest

from .conftest import MAN_DIR, REPO_ROOT

from ta_r4 import sh2b3_known_answer as ska

TABLE = MAN_DIR / "known_answer_sh2b3.tsv"
BMI_HTN = "SH2B3_12q24__EUR__bmi_vs_hypertension"


def _doc(pair_id, pp4=0.5, nsnps=100, hit1="rs1", hit2="rs2", n_cs_a=2, n_cs_b=3, status="success"):
    s = {"nsnps": nsnps, "hit1": hit1, "hit2": hit2, "PP.H0.abf": 0, "PP.H1.abf": 0, "PP.H2.abf": 0,
         "PP.H3.abf": None if pp4 is None else 1 - pp4, "PP.H4.abf": pp4}
    if status == "no_signal":
        s = {"nsnps": None, "PP.H0.abf": None, "PP.H1.abf": None, "PP.H2.abf": None, "PP.H3.abf": None,
             "PP.H4.abf": None}
    return {"pair_id": pair_id, "status": status, "summary": s, "n_cs_a": n_cs_a, "n_cs_b": n_cs_b}


def _frozen_docs():
    docs = {p: _doc(p) for p in ska.PAIRS}
    docs[BMI_HTN] = _doc(BMI_HTN, pp4=1, nsnps=168, hit1="rs3184504", hit2="rs3184504", n_cs_a=13, n_cs_b=5)
    docs["SH2B3_12q24__EUR__asthma_vs_bmi"] = _doc("SH2B3_12q24__EUR__asthma_vs_bmi", status="no_signal",
                                                   n_cs_a=0, n_cs_b=13)
    return docs


def _write(d, docs):
    d.mkdir(parents=True, exist_ok=True)
    for p, doc in docs.items():
        (d / f"{p}.json").write_text(json.dumps(doc))


def _dirs(tmp_path, r2=None, l10=None, frozen=None):
    fz = frozen or _frozen_docs()
    dirs = {"frozen": tmp_path / "frozen", "R2_exact": tmp_path / "r2", "L10_iter100": tmp_path / "l10"}
    _write(dirs["frozen"], fz)
    _write(dirs["R2_exact"], r2 if r2 is not None else copy.deepcopy(fz))
    _write(dirs["L10_iter100"], l10 if l10 is not None else {p: _doc(p, pp4=0.1) for p in ska.PAIRS})
    return dirs


def _rows(dirs):
    return ska.build_table(frozen_dir=dirs["frozen"],
                           repro_dirs={k: dirs[k] for k in ("R2_exact", "L10_iter100")})


def _row(rows, label, pair):
    (r,) = [r for r in rows if r["config_label"] == label and r["pair_id"] == pair]
    return r


def test_nine_canonical_pairs():
    assert len(ska.PAIRS) == 9 and BMI_HTN in ska.PAIRS
    assert "SH2B3_12q24__EUR__asthma_vs_t2d" not in ska.PAIRS


def test_eighteen_rows_labelled(tmp_path):
    rows = _rows(_dirs(tmp_path))
    assert len(rows) == 18
    assert sorted({r["config_label"] for r in rows}) == ["L10_iter100", "R2_exact"]
    assert all(sum(r["config_label"] == lab for r in rows) == 9 for lab in ("R2_exact", "L10_iter100"))
    assert list(rows[0]) == ska.COLUMNS


def test_identical_reproduction_matches(tmp_path):
    rows = _rows(_dirs(tmp_path))
    assert all(r["match_flag"] == "true" for r in rows if r["config_label"] == "R2_exact")


def test_l10_rows_never_matched_or_frozen(tmp_path):
    rows = _rows(_dirs(tmp_path))
    for r in rows:
        if r["config_label"] == "L10_iter100":
            assert r["pp_h4_frozen"] == "NA" and r["abs_diff"] == "NA" and r["match_flag"] == "NA"


@pytest.mark.parametrize("delta,flag", [(5e-7, "true"), (2e-6, "false")])
def test_tolerance_1e6(tmp_path, delta, flag):
    r2 = _frozen_docs()
    r2["SH2B3_12q24__EUR__stroke_vs_t2d"]["summary"]["PP.H4.abf"] += delta
    r = _row(_rows(_dirs(tmp_path, r2=r2)), "R2_exact", "SH2B3_12q24__EUR__stroke_vs_t2d")
    assert r["match_flag"] == flag
    assert abs(float(r["abs_diff"]) - delta) < 1e-12


def test_fingerprint_mismatch_fails_match_even_with_equal_pp(tmp_path):
    r2 = _frozen_docs()
    r2["SH2B3_12q24__EUR__stroke_vs_t2d"]["summary"]["nsnps"] = 99
    r = _row(_rows(_dirs(tmp_path, r2=r2)), "R2_exact", "SH2B3_12q24__EUR__stroke_vs_t2d")
    assert r["abs_diff"] == "0.000e+00" and r["fingerprint_eq"] == "false" and r["match_flag"] == "false"


def test_status_and_na_pp(tmp_path):
    # both no_signal with NA PP.H4: equal; reproduced numeric vs frozen NA: not equal, abs_diff NA
    r2 = _frozen_docs()
    rows = _rows(_dirs(tmp_path, r2=r2))
    r = _row(rows, "R2_exact", "SH2B3_12q24__EUR__asthma_vs_bmi")
    assert r["pp_h4_frozen"] == "NA" and r["pp_h4_reproduced"] == "NA" and r["match_flag"] == "true"
    r2["SH2B3_12q24__EUR__asthma_vs_bmi"] = _doc("SH2B3_12q24__EUR__asthma_vs_bmi", n_cs_a=0, n_cs_b=13)
    r = _row(_rows(_dirs(tmp_path / "b", r2=r2)), "R2_exact", "SH2B3_12q24__EUR__asthma_vs_bmi")
    assert r["abs_diff"] == "NA" and r["match_flag"] == "false"


def test_bmi_htn_fingerprint_field_by_field():
    good = _frozen_docs()[BMI_HTN]
    fp = ska.fingerprint_check(good)
    assert set(fp) == {"n_cs_a", "n_cs_b", "nsnps", "hit1", "hit2"}
    assert all(v["eq"] for v in fp.values())
    assert (fp["n_cs_a"]["expected"], fp["n_cs_b"]["expected"], fp["nsnps"]["expected"]) == (13, 5, 168)
    bad = copy.deepcopy(good)
    bad["n_cs_a"] = 12
    bad["summary"]["hit2"] = "rs7"
    fp = ska.fingerprint_check(bad)
    assert [k for k, v in fp.items() if not v["eq"]] == ["n_cs_a", "hit2"]


def test_bmi_htn_fingerprint_is_absolute_not_relative(tmp_path):
    # a frozen JSON that drifted from the recorded fingerprint does not make a matching reproduction pass
    fz = _frozen_docs()
    fz[BMI_HTN]["n_cs_a"] = 12
    r = _row(_rows(_dirs(tmp_path, frozen=fz)), "R2_exact", BMI_HTN)
    assert r["fingerprint_eq"] == "false" and r["match_flag"] == "false"


def test_missing_reproduction_raises(tmp_path):
    dirs = _dirs(tmp_path)
    (dirs["R2_exact"] / f"{BMI_HTN}.json").unlink()
    with pytest.raises(FileNotFoundError):
        _rows(dirs)


def test_l15_fit_check():
    fits = {"bmi": {"credible_sets": {f"CS{i}": [1] for i in range(1, 14)}, "ld_overlap": 170},
            "hypertension": {"credible_sets": {f"CS{i}": [1] for i in range(1, 6)}, "ld_overlap": 589},
            "stroke": {"credible_sets": {"CS1": [1], "CS2": [2]}, "ld_overlap": 621}}
    rows = {r["trait"]: r for r in ska.l15_fit_check(fits)}
    assert rows["bmi"]["n_cs_eq"] and rows["bmi"]["ld_overlap_eq"]
    assert (rows["stroke"]["n_cs"], rows["stroke"]["n_cs_expected"], rows["stroke"]["n_cs_eq"]) == (2, 3, False)
    assert rows["stroke"]["ld_overlap_eq"] is False


def test_r1_crosscheck_counts():
    targets = [{"pair_id": "R__EUR__a_vs_b", "base_region": "R", "ancestry": "EUR", "trait_a": "a", "trait_b": "b"},
               {"pair_id": "R__EUR__b_vs_c", "base_region": "R", "ancestry": "EUR", "trait_a": "b", "trait_b": "c"}]
    n_cs = {("a", "EUR", "R"): 0, ("b", "EUR", "R"): 4, ("c", "EUR", "R"): 2}
    rows = ska.r1_crosscheck(targets, n_cs)
    assert [r["any_side_zero"] for r in rows] == [True, False]
    with pytest.raises(KeyError):
        ska.r1_crosscheck(targets, {("a", "EUR", "R"): 1})


@pytest.mark.r4_heavy
def test_live_table_from_disk():
    if not (REPO_ROOT / ska.REPRO_DIRS["R2_exact"]).is_dir():
        pytest.skip(f"{ska.REPRO_DIRS['R2_exact']} absent (W3b fire not run)")
    rows = ska.build_table(root=REPO_ROOT)
    assert len(rows) == 18
    with open(TABLE, newline="") as fh:
        committed = list(csv.DictReader(fh, delimiter="\t"))
    assert committed == rows


def test_fit_cs_table_and_r1_table():
    w3a = [{"pair": "real_ld", "trait": "a", "ancestry": "EUR", "region_safe": "R", "status_L": "ok", "n_cs_L": "1"},
           {"pair": "real_ld", "trait": "b", "ancestry": "EUR", "region_safe": "R", "status_L": "ok", "n_cs_L": "4"},
           {"pair": "real_ld", "trait": "c", "ancestry": "EUR", "region_safe": "R", "status_L": "too_many_variants",
            "n_cs_L": "0"},
           {"pair": "k2d", "trait": "a", "ancestry": "EUR", "region_safe": "R", "status_L": "ok", "n_cs_L": "9"}]
    rds = {("a", "EUR", "R"): 0, ("b", "EUR", "R"): 4, ("c", "EUR", "R"): None}
    fc = ska.fit_cs_table(w3a, rds)
    assert [r["eq"] for r in fc] == ["false", "true", "NA"]
    targets = [{"pair_id": "R__EUR__a_vs_b", "base_region": "R", "ancestry": "EUR", "trait_a": "a", "trait_b": "b"}]
    (r,) = ska.r1_table(targets, {("a", "EUR", "R"): 1, ("b", "EUR", "R"): 4}, rds)
    assert (r["any_zero_json"], r["any_zero_rds"]) == ("false", "true")


@pytest.mark.r4_heavy
def test_live_r1_and_fit_cs_tables(monkeypatch):
    monkeypatch.setattr(ska, "RSCRIPT", "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript")
    monkeypatch.chdir(REPO_ROOT)
    w3a = list(csv.DictReader(open(MAN_DIR / "known_answer_W3a.tsv", newline=""), delimiter="\t"))
    keys = [(r["trait"], r["ancestry"], r["region_safe"]) for r in w3a if r["pair"] == "real_ld"]
    fresh = ska.fit_cs_table(w3a, ska.rds_cs_counts("repro_routeL", keys))
    rows = {p: list(csv.DictReader(open(MAN_DIR / p, newline=""), delimiter="\t"))
            for p in ("r1_structural_crosscheck.tsv", "fit_cs_json_vs_rds.tsv")}
    r1, fc = rows["r1_structural_crosscheck.tsv"], rows["fit_cs_json_vs_rds.tsv"]
    targets = list(csv.DictReader(open(REPO_ROOT / ska.R1_TARGETS, newline=""), delimiter="\t"))
    assert [r["pair_id"] for r in r1] == [t["pair_id"] for t in targets] and len(r1) == 28
    assert len(fc) == 96 and fc == fresh
    by = {(r["trait"], r["ancestry"], r["region_safe"]): r for r in fc}
    for t, r in zip(targets, r1):
        for side in ("a", "b"):
            f = by[(t[f"trait_{side}"], t["ancestry"], t["base_region"])]
            assert (r[f"n_cs_json_{side}"], r[f"n_cs_rds_{side}"]) == (f["n_cs_json"], f["n_cs_rds_sets"])
