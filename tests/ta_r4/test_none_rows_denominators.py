"""W3f 15.7e (F8, F11; Carter Q-DEN A "Known states only"): an early-exit pair keeps the completed side's n_cs; the
pair no-CS rate counts known zeros and reports rows of unknown state; negative-control rates are split by method and
`none` rows are in no share denominator. Expected counts are hand-computed in each test."""
from __future__ import annotations

import importlib.util
import math
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from .conftest import REPO_ROOT
from .fixtures.build_toy_workflow import ANC, RSCRIPT, coloc, ok, pair_row, pair_session_root, run
from .fixtures.estimand_fixtures import doc, manifest, mrow

from ta_r4 import paths

PRE_157E_REF = "f20b667ba9f2775db7e9f336f4d6ea7ee9da8230"
PY = "/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11"
ARM = "A3_1kg"
K = "p12_primary"
THR = 0.8
SAME, NULL = pair_row("FIXP_SAME"), pair_row("FIXP_NULL")


def _git_show(path):
    return subprocess.run(["git", "show", f"{PRE_157E_REF}:{path}"], cwd=REPO_ROOT, capture_output=True, text=True,
                          check=True).stdout


def _old_estimands(tmp_path):
    p = tmp_path / "estimands_pre_157e.py"
    p.write_text(_git_show("src/python/ta_r4/estimands.py"))
    spec = importlib.util.spec_from_file_location("estimands_pre_157e", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ R: early-exit pair docs (F11)

@pytest.fixture(scope="module")
def fits(tmp_path_factory):
    return pair_session_root(tmp_path_factory)


def _exit_root(fits, tmp_path, row, statuses):
    root = tmp_path / f"ee_{row['region_id']}_{statuses[0]}_{statuses[1]}"
    shutil.copytree(fits, root, symlinks=True)
    for trait, st in zip((row["trait_a"], row["trait_b"]), statuses):
        if st:
            rds = root / paths.fit_rds(ARM, trait, ANC, row["region_id"])
            ok(run([RSCRIPT, "-e", f'saveRDS(list(status = "{st}", region = "{row["region_id"]}"), "{rds}")'], root))
    return root


def _n_sets(root, row, trait):
    rds = root / paths.fit_rds(ARM, trait, ANC, row["region_id"])
    p = ok(run([RSCRIPT, "-e", f'cat(length(readRDS("{rds}")$sets$cs))'], root))
    return int(p.stdout.strip().splitlines()[-1])


@pytest.mark.r4_heavy
def test_early_exit_pair_keeps_the_completed_sides_n_cs(fits, tmp_path):
    for row, statuses, kept in ((SAME, (None, "too_many_variants"), "a"),
                                (NULL, ("no_variants", None), "b")):  # B has no signal: the completed side is a 0
        p, full = coloc(fits, ARM, row, K, "susie")
        ok(p)
        want = _n_sets(fits, row, row[f"trait_{kept}"])
        assert full[f"n_cs_{kept}"] == want
        if row is NULL:
            assert want == 0
        p, d = coloc(_exit_root(fits, tmp_path, row, statuses), ARM, row, K, "susie")
        ok(p)
        gone = "b" if kept == "a" else "a"
        assert d["method"] == "none" and d["none_reason"].startswith("fit_early_exit:"), d
        assert d[f"n_cs_{kept}"] == want and d[f"n_cs_{gone}"] is None, d


@pytest.mark.r4_heavy
def test_early_exit_pair_records_which_side_exited(fits, tmp_path):
    for statuses in ((None, "too_many_variants"), ("no_variants", "too_many_variants")):
        p, d = coloc(_exit_root(fits, tmp_path, SAME, statuses), ARM, SAME, K, "susie")
        ok(p)
        assert (d["early_exit_a"], d["early_exit_b"]) == statuses, d
        for side, st in zip("ab", statuses):
            if st:
                assert d[f"n_cs_{side}"] is None
            else:
                assert isinstance(d[f"n_cs_{side}"], int)
    p, f = coloc(fits, ARM, SAME, K, "susie")
    ok(p)
    assert "early_exit_a" not in f and "early_exit_b" not in f  # fitted docs keep their exact key set


# ------------------------------------------------------------------ Python: pair no-CS by known state (F11)

def _pair_table(n_cs_list, label="A3_ukb", regions=None):
    from ta_r4.estimands import build_rows, e4_no_cs_rate, fit_frame

    pairs = [("asthma", "bmi"), ("asthma", "t2d"), ("bmi", "t2d"), ("bmi", "stroke"), ("t2d", "stroke")]
    regions = regions or ["R1"] * len(n_cs_list)
    m = manifest([mrow(reg, "EUR", pairs[i % 5]) for i, reg in enumerate(regions)])
    docs = []
    for rid, n_cs in zip(m.row_id, n_cs_list):
        method = "none" if None in n_cs else ("fallback_abf" if 0 in n_cs else None)
        d = doc(rid, label, K, 0.3, method=method, n_cs=n_cs)
        if method == "none":
            d.update({"pp_h4_max": None, "none_reason": "fit_early_exit:NA|too_many_variants"})
        docs.append(d)
    return e4_no_cs_rate(build_rows(docs, m), fit_frame([]))


def test_known_zero_beside_an_early_exit_is_no_cs():
    t = _pair_table([(0, None), (None, 0)])
    pr = t[t.level == "pair_row"].iloc[0]
    assert (int(pr.n_rows), int(pr.n_no_cs), int(pr.n_unknown)) == (2, 2, 0)
    assert pr.no_cs_rate == 1.0 and pr.no_cs_rate_known == 1.0


def test_unknown_without_a_known_zero_is_counted_as_unknown():
    t = _pair_table([(2, None), (None, None), (None, 1), (1, 1)])
    pr = t[t.level == "pair_row"].iloc[0]
    assert (int(pr.n_rows), int(pr.n_no_cs), int(pr.n_unknown)) == (4, 0, 3)
    assert pr.no_cs_rate == 0.0 and pr.no_cs_rate_known == 0.0


def test_no_cs_rate_known_excludes_unknown_rows():
    t = _pair_table([(0, None), (1, 1), (2, None), (None, None), (0, 3)], regions=["R1", "R1", "R1", "R2", "R2"])
    pr = t[t.level == "pair_row"].iloc[0]
    # no-CS: rows 1 and 5; unknown: rows 3 and 4; known state: 3 rows
    assert (int(pr.n_rows), int(pr.n_no_cs), int(pr.n_unknown)) == (5, 2, 2)
    assert pr.no_cs_rate == pytest.approx(2 / 5) and pr.no_cs_rate_known == pytest.approx(2 / 3)
    rg = t[t.level == "region"].set_index("region_safe")
    assert rg.loc["R1", ["n_rows", "n_no_cs", "n_unknown"]].astype(int).tolist() == [3, 1, 1]
    assert rg.loc["R1", "no_cs_rate_known"] == pytest.approx(1 / 2)
    assert rg.loc["R2", ["n_rows", "n_no_cs", "n_unknown"]].astype(int).tolist() == [2, 1, 1]
    assert rg.loc["R2", "no_cs_rate_known"] == 1.0
    allu = _pair_table([(None, None)])
    assert math.isnan(allu[allu.level == "pair_row"].iloc[0].no_cs_rate_known)  # no row of known state


def test_fit_level_rule_unchanged(tmp_path):
    from ta_r4.estimands import build_rows, e4_no_cs_rate, fit_frame

    def f(n_cs, status="ok"):
        cs = {f"CS{i + 1}": [{"CHR": "1", "POS": j} for j in range(2)] for i in range(n_cs)}
        return {"status": status, "credible_sets": cs, "d3b_ld_z_consistency_s": 0.1,
                "d3_ld_quality": {"n_outliers": 0, "max_logLR": 1.0}}

    fits = fit_frame([("A3_ukb", "asthma", "EUR", "R1", f(2)), ("A3_ukb", "bmi", "EUR", "R1", f(0)),
                      ("A3_ukb", "t2d", "EUR", "R1", {"status": "too_many_variants", "credible_sets": None}),
                      ("A3_1kg", "asthma", "EUR", "R1", {"status": "no_variants", "credible_sets": None}),
                      ("A3_1kg", "bmi", "EUR", "R1", f(1))])
    m = manifest([mrow("R1", "EUR", ("asthma", "bmi"))])
    rows = build_rows([doc(m.row_id[0], "A3_ukb", K, 0.3, n_cs=(2, 0), method="fallback_abf")], m)
    cols = ["level", "denominator", "ancestry", "label", "n_rows", "n_no_cs", "n_early_exit", "no_cs_rate"]
    new = e4_no_cs_rate(rows, fits)
    old = _old_estimands(tmp_path).e4_no_cs_rate(rows, fits)
    new, old = (x[x.level == "fit"][cols].reset_index(drop=True) for x in (new, old))
    pd.testing.assert_frame_equal(new, old)
    ft = new.set_index("label")
    assert ft.loc["A3_ukb", ["n_rows", "n_no_cs", "n_early_exit"]].astype(int).tolist() == [3, 2, 1]
    assert ft.loc["A3_1kg", ["n_rows", "n_no_cs", "n_early_exit"]].astype(int).tolist() == [2, 1, 1]


# ------------------------------------------------------------------ Python: NC rates by method (F8)

def _nc_rows(spec, label="A2_identity", nc_set="blood_group"):
    """spec: list of (method, h4); one NC row each, region NC_ABO."""
    from ta_r4.estimands import build_rows

    pairs = [("asthma", "bmi"), ("asthma", "t2d"), ("bmi", "t2d"), ("bmi", "stroke"), ("t2d", "stroke")]
    m = manifest([mrow("NC_ABO", "EUR", pairs[i], row_class="negative_control", nc_set=nc_set)
                  for i in range(len(spec))])
    docs = []
    for rid, (method, h4) in zip(m.row_id, spec):
        if label.startswith("A1_"):
            d = doc(rid, label, K, h4)
        else:
            d = doc(rid, label, K, 0.0 if h4 is None else h4, method=method,
                    n_cs=(0, 1) if method == "fallback_abf" else (1, 1))
        if method == "none":
            d.update({"pp_h4": None, "pp_h4_max": None, "n_cs_a": None, "n_cs_b": None,
                      "none_reason": "fit_early_exit:NA|too_many_variants"})
        docs.append(d)
    return build_rows(docs, m)


def _nc(rows):
    from ta_r4.estimands import negative_control_rates

    return negative_control_rates(rows, THR)


def test_nc_rates_split_by_method():
    rows = _nc_rows([("coloc_susie", 0.9), ("coloc_susie", 0.1), ("fallback_abf", 0.85), ("none", None)])
    t = _nc(rows).set_index("method")
    assert set(t.index) == {"coloc_susie", "fallback_abf", "none", "with_posterior"}
    assert t.loc["coloc_susie", ["n_rows", "n_h4"]].astype(int).tolist() == [2, 1]
    assert t.loc["coloc_susie", "share_h4"] == 0.5
    assert t.loc["fallback_abf", ["n_rows", "n_h4"]].astype(int).tolist() == [1, 1]
    assert t.loc["fallback_abf", "share_h4"] == 1.0
    assert set(t.threshold) == {THR} and set(t.label) == {"A2_identity"} and set(t.p12_key) == {K}


def test_nc_none_rows_are_counted_not_in_a_share_denominator():
    rows = _nc_rows([("coloc_susie", 0.9), ("none", None), ("none", None)])
    t = _nc(rows).set_index("method")
    assert t.loc["none", ["n_rows", "n_h4"]].astype(int).tolist() == [2, 0]
    assert math.isnan(t.loc["none", "share_h4"])
    wp = t.loc["with_posterior"]
    assert (int(wp.n_rows), int(wp.n_h4), wp.share_h4) == (1, 1, 1.0)  # 1 of 1, not 1 of 3
    only_none = _nc(_nc_rows([("none", None)])).set_index("method")
    assert int(only_none.loc["with_posterior", "n_rows"]) == 0 and math.isnan(only_none.loc["with_posterior",
                                                                                              "share_h4"])


def test_nc_with_posterior_row_labels_fallback():
    rows = _nc_rows([("coloc_susie", 0.9), ("fallback_abf", 0.85), ("fallback_abf", 0.2), ("none", None)])
    t = _nc(rows).set_index("method")
    wp = t.loc["with_posterior"]
    assert (int(wp.n_rows), int(wp.n_h4), int(wp.n_fallback_abf)) == (3, 2, 2)
    assert wp.share_h4 == pytest.approx(2 / 3)
    assert t.loc[["coloc_susie", "fallback_abf", "none"], "n_fallback_abf"].astype(int).tolist() == [0, 2, 0]


def test_nc_a1_methods_are_their_own_rows():
    rows = pd.concat([_nc_rows([("x", 0.9), ("x", 0.1)], label="A1_matched"),
                      _nc_rows([("x", 0.95)], label="A1_allvars"),
                      _nc_rows([("coloc_susie", 0.9)])], ignore_index=True)
    t = _nc(rows)
    got = {(r.label, r.method): (int(r.n_rows), int(r.n_h4)) for r in t.itertuples()}
    assert got == {("A1_matched", "A1_abf_matched"): (2, 1), ("A1_matched", "with_posterior"): (2, 1),
                   ("A1_allvars", "A1_abf_allvars"): (1, 1), ("A1_allvars", "with_posterior"): (1, 1),
                   ("A2_identity", "coloc_susie"): (1, 1), ("A2_identity", "with_posterior"): (1, 1)}


def test_nc_group_totals_reconcile():
    from ta_r4.estimands import build_rows

    from .fixtures.estimand_fixtures import universe

    m, docs = universe()
    nc_ids = list(m.row_id[m.row_class == "negative_control"])
    for i, d in enumerate(docs):  # give the NC rows every method
        if d["row_id"] in nc_ids and not d["mode"].startswith("A1_"):
            if i % 3 == 1:
                d.update(method="fallback_abf", n_cs_a=0, fallback_reason="n_cs_a==0")
            elif i % 3 == 2:
                d.update(method="none", pp_h4=None, pp_h4_max=None, n_cs_a=None, n_cs_b=None,
                         none_reason="coloc_susie_empty")
    rows = build_rows(docs, m)
    t = _nc(rows)
    nc = rows[rows.row_class == "negative_control"]
    key = ["nc_set", "label", "p12_key"]
    want = nc.groupby(key).size()
    per = t[t.method != "with_posterior"].groupby(key).n_rows.sum()
    pd.testing.assert_series_equal(per.sort_index(), want.sort_index(), check_names=False)
    wp = t[t.method == "with_posterior"].set_index(key).n_rows
    want_wp = nc[nc.method != "none"].groupby(key).size().reindex(want.index, fill_value=0)
    pd.testing.assert_series_equal(wp.sort_index(), want_wp.sort_index(), check_names=False)
    assert set(t.method) == {"coloc_susie", "fallback_abf", "none", "A1_abf_matched", "A1_abf_allvars",
                             "with_posterior"}
    assert len(t[t.method == "with_posterior"]) == len(want)


# ------------------------------------------------------------------ confirmatory outputs unchanged

def test_confirmatory_outputs_unchanged(tmp_path):
    from .test_run_aggregation import _run, build_tree

    repo = tmp_path / "repo"
    build_tree(repo)
    assert _run(repo, tmp_path / "new", draft=True) == 0
    old_src = tmp_path / "old_src"
    shutil.copytree(REPO_ROOT / "src/python/ta_r4", old_src / "ta_r4",
                    ignore=shutil.ignore_patterns("__pycache__"))
    for f in ("estimands.py", "run_aggregation.py"):
        (old_src / "ta_r4" / f).write_text(_git_show(f"src/python/ta_r4/{f}"))
    code = ("import sys; sys.path[:0] = [sys.argv[1], sys.argv[4]]; import ta_r4; "
            "assert ta_r4.__file__.startswith(sys.argv[1]), ta_r4.__file__; "
            "from ta_r4.run_aggregation import run_aggregation; "
            "sys.exit(run_aggregation(sys.argv[2], sys.argv[3], draft=True))")
    p = subprocess.run([PY, "-c", code, str(old_src), str(repo), str(tmp_path / "old"), str(REPO_ROOT / "src/python")],
                       capture_output=True, text=True, cwd=tmp_path)
    assert p.returncode == 0, p.stderr[-3000:]
    for t in ("branch_outcomes", "e1_paired_delta", "e2_agreement_sweep", "e3_reclassification"):
        new, old = ((tmp_path / d / f"{t}.tsv").read_bytes() for d in ("new", "old"))
        assert new == old, t
    assert (tmp_path / "new/negative_controls.tsv").read_bytes() != b""
