"""E1-E8 estimators on synthetic inputs with hand-computed answers, and the FINAL/DRAFT label (W3d; D-26)."""
from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from .conftest import REPO_ROOT
from .fixtures.estimand_fixtures import doc, manifest, mrow

RULES = yaml.safe_load((REPO_ROOT / "config/ta_r4/decision_rules.yaml").read_text())
PAIRS3 = [("asthma", "bmi"), ("asthma", "t2d"), ("bmi", "t2d")]


def _rows(docs, man):
    from ta_r4.estimands import build_rows

    return build_rows(docs, man)


def _man3(region="R1"):
    return manifest([mrow(region, "EUR", p) for p in PAIRS3])


# ------------------------------------------------------------------ region_stat / build_rows

def test_region_stat_by_method():
    from ta_r4.estimands import region_stat

    d = doc("x", "A2_identity", "p12_primary", 0.9)
    d["pp_h4"] = 0.3
    assert region_stat(d) == (0.9, False)
    f = doc("x", "A2_identity", "p12_primary", 0.4, method="fallback_abf")
    f["pp_h4_max"] = 0.99
    assert region_stat(f) == (0.4, True)
    a = doc("x", "A1_matched", "p12_primary", 0.7)
    a["pp_h4_max"] = 0.2
    assert region_stat(a) == (0.7, False)
    with pytest.raises(ValueError):
        region_stat(dict(d, method="mystery"))


def test_build_rows_labels_and_manifest_join():
    m = _man3()
    rid = m.row_id[0]
    rows = _rows([doc(rid, "A1_matched", "p12_primary", 0.5), doc(rid, "A1_allvars", "p12_primary", 0.6),
                  doc(rid, "A3_1kg", "p12_primary", 0.7)], m)
    assert sorted(rows.label) == ["A1_allvars", "A1_matched", "A3_1kg"]
    assert set(rows.loc[rows.label == "A1_matched", "varset"]) == {"matched"}
    assert rows.region_safe.unique().tolist() == ["R1"]
    assert rows.row_class.unique().tolist() == ["primary"]
    with pytest.raises(ValueError):
        _rows([doc("not_in_manifest", "A3_1kg", "p12_primary", 0.1)], m)
    with pytest.raises(ValueError):
        _rows([doc(rid, "A3_1kg", "p12_primary", 0.1)] * 2, m)


# ------------------------------------------------------------------ E1

def test_e1_paired_delta_subsets():
    from ta_r4.estimands import e1_paired_delta

    m = _man3()
    r1, r2, r3 = m.row_id
    k = "p12_primary"
    docs = [doc(r1, "A2_identity", k, 0.9), doc(r1, "A3_1kg", k, 0.5), doc(r1, "A1_matched", k, 0.8),
            doc(r2, "A2_identity", k, 0.3, method="fallback_abf"), doc(r2, "A3_1kg", k, 0.2),
            doc(r2, "A1_matched", k, 0.3),
            doc(r3, "A2_identity", k, 0.6), doc(r3, "A3_1kg", k, 0.6, method="fallback_abf"),
            doc(r3, "A1_matched", k, 0.6),
            doc(r1, "A2_identity", "p12_sensitivity", 0.1), doc(r1, "A3_1kg", "p12_sensitivity", 0.9)]
    rows = _rows(docs, m)
    a2 = e1_paired_delta(rows, "A2_identity", "A3_1kg", k, "both methods coloc_susie")
    assert a2["all_rows"].set_index("row_id").delta.round(12).to_dict() == {r1: 0.4, r2: 0.1, r3: 0.0}
    assert set(a2["all_rows"].loc[a2["all_rows"].is_fallback, "row_id"]) == {r2, r3}
    assert a2["both_have_cs"].row_id.tolist() == [r1]
    a1 = e1_paired_delta(rows, "A1_matched", "A3_1kg", k, "A3 method coloc_susie")
    assert sorted(a1["both_have_cs"].row_id) == [r1, r2]
    assert a1["both_have_cs"].set_index("row_id").delta.round(12).to_dict() == {r1: 0.3, r2: 0.1}


# ------------------------------------------------------------------ bootstrap / sign test

def test_bootstrap_deterministic_and_constant():
    from ta_r4.estimands import cluster_bootstrap_ci

    rng = np.random.default_rng(1)
    v = rng.normal(size=60)
    cl = np.repeat(np.arange(10), 6)
    a = cluster_bootstrap_ci(v, cl, B=10000, seed=20261021)
    b = cluster_bootstrap_ci(v, cl, B=10000, seed=20261021)
    assert a == b
    assert a != cluster_bootstrap_ci(v, cl, B=10000, seed=1)
    assert cluster_bootstrap_ci(np.full(40, 0.1), np.repeat(np.arange(10), 4), B=10000, seed=5) == \
        pytest.approx((0.1, 0.1), abs=1e-15)


def test_bootstrap_resamples_clusters_not_rows():
    """All variance lies between clusters (rows within a cluster are identical): the cluster CI must be
    much wider than a row bootstrap of the same 100 values, which pseudo-replicates 10 clusters as 100 rows."""
    from ta_r4.estimands import cluster_bootstrap_ci

    vals = np.repeat(np.linspace(-1, 1, 10), 10)
    cl = np.repeat(np.arange(10), 10)
    lo, hi = cluster_bootstrap_ci(vals, cl, B=4000, seed=3)
    rng = np.random.default_rng(3)
    row_stats = [np.median(rng.choice(vals, size=vals.size, replace=True)) for _ in range(4000)]
    rlo, rhi = np.percentile(row_stats, [2.5, 97.5])
    assert (hi - lo) > 1.5 * (rhi - rlo)


def test_bootstrap_undefined_below_two():
    from ta_r4.estimands import cluster_bootstrap_ci

    for v in ([], [0.3]):
        lo, hi = cluster_bootstrap_ci(np.array(v, float), np.array(["a"] * len(v)), B=100, seed=1)
        assert math.isnan(lo) and math.isnan(hi)


def test_sign_test_exact():
    from ta_r4.estimands import sign_test

    assert sign_test([0.1] * 8 + [0.0, 0.0]) == pytest.approx(0.0078125, abs=1e-15)
    assert sign_test([0.1] * 8 + [0.0, 0.0]) == sign_test([0.1] * 8)
    assert sign_test([-0.2] * 8) == sign_test([0.2] * 8)
    assert sign_test([0.0, 0.0]) == 1.0
    assert sign_test([0.1, -0.1]) == 1.0
    # 9 positive / 1 negative: 2 * (1 + 10) / 1024
    assert sign_test([1] * 9 + [-1]) == pytest.approx(22 / 1024, abs=1e-15)


# ------------------------------------------------------------------ E2

def test_mcnemar_exact():
    from ta_r4.estimands import mcnemar_exact

    assert mcnemar_exact(10, 0) == (pytest.approx(0.001953125, abs=1e-15), "X>A3")
    assert mcnemar_exact(0, 10)[1] == "A3>X"
    assert mcnemar_exact(5, 5) == (1.0, "none")
    assert mcnemar_exact(0, 0) == (1.0, "none")
    assert mcnemar_exact(7, 1)[0] == pytest.approx(2 * (1 + 8) / 256, abs=1e-15)


def test_cohen_kappa():
    from ta_r4.estimands import cohen_kappa

    assert cohen_kappa([[20, 5], [10, 15]]) == pytest.approx(0.4, abs=1e-12)
    assert cohen_kappa([[10, 0], [0, 10]]) == pytest.approx(1.0)
    assert math.isnan(cohen_kappa([[10, 0], [0, 0]]))
    assert math.isnan(cohen_kappa([[0, 0], [0, 0]]))


def test_e2_agreement_four_thresholds():
    from ta_r4.estimands import e2_agreement

    p = pd.DataFrame({"x_stat": [0.95, 0.85, 0.75, 0.6, 0.4], "ref_stat": [0.9, 0.6, 0.8, 0.3, 0.55]})
    t = e2_agreement(p, [0.5, 0.7, 0.8, 0.9]).set_index("threshold")
    assert t.loc[0.5, ["a", "b", "c", "d"]].tolist() == [3, 1, 1, 0]
    assert t.loc[0.7, ["a", "b", "c", "d"]].tolist() == [2, 1, 0, 2]
    assert t.loc[0.8, ["a", "b", "c", "d"]].tolist() == [1, 1, 1, 2]
    assert t.loc[0.9, ["a", "b", "c", "d"]].tolist() == [1, 0, 0, 4]
    assert t.loc[0.9, "kappa"] == pytest.approx(1.0)
    assert t.loc[0.9, "observed_agreement"] == 1.0
    assert t.loc[0.8, "mcnemar_p"] == 1.0
    assert t.loc[0.7, "mcnemar_direction"] == "X>A3"
    # a value exactly at the threshold is a call (>=)
    t2 = e2_agreement(pd.DataFrame({"x_stat": [0.8], "ref_stat": [0.79999]}), [0.8])
    assert t2[["a", "b", "c", "d"]].iloc[0].tolist() == [0, 1, 0, 0]


# ------------------------------------------------------------------ E3 / E4

def test_e3_reclassification_argmax():
    from ta_r4.estimands import e1_paired_delta, e3_reclassification

    m = _man3()
    r1, r2, r3 = m.row_id
    k = "p12_primary"
    docs = [doc(r1, "A2_identity", k, 0.9), doc(r1, "A3_1kg", k, 0.3, h3=0.6),
            doc(r2, "A2_identity", k, 0.9), doc(r2, "A3_1kg", k, 0.95),
            doc(r3, "A2_identity", k, 0.2, h3=0.7), doc(r3, "A3_1kg", k, 0.1, h3=0.85)]
    p = e1_paired_delta(_rows(docs, m), "A2_identity", "A3_1kg", k, "both methods coloc_susie")["all_rows"]
    t = e3_reclassification(p)
    got = {(r.class_x, r.class_ref): r.n for r in t.itertuples()}
    assert got == {("H4", "H3"): 1, ("H4", "H4"): 1, ("H3", "H3"): 1}


def test_e4_no_cs_rate():
    from ta_r4.estimands import e4_no_cs_rate, fit_frame

    m = _man3()
    r1, r2, r3 = m.row_id
    k = "p12_primary"
    docs = [doc(r1, "A2_identity", k, 0.4, method="fallback_abf", n_cs=(0, 2)),
            doc(r2, "A2_identity", k, 0.5, n_cs=(1, 1)),
            doc(r3, "A2_identity", k, 0.4, method="fallback_abf", n_cs=(3, 0)),
            doc(r1, "A3_1kg", k, 0.5, n_cs=(1, 1)), doc(r1, "A1_matched", k, 0.5)]
    t = e4_no_cs_rate(_rows(docs, m), fit_frame([]))
    t = t[t.level == "pair_row"].set_index("label")
    assert t.loc["A2_identity", ["n_rows", "n_no_cs"]].tolist() == [3, 2]
    assert t.loc["A2_identity", "no_cs_rate"] == pytest.approx(2 / 3)
    assert t.loc["A3_1kg", "no_cs_rate"] == 0.0
    assert "A1_matched" not in t.index


def _fitdoc(n_cs, lam=0.1, outl=0, exact=None, flipped=None, status="ok"):
    cs = {f"CS{i + 1}": [{"CHR": "1", "POS": j} for j in range(i + 2)] for i in range(n_cs)}
    return {"status": status, "credible_sets": cs if n_cs else [], "d3b_ld_z_consistency_s": lam,
            "d3_ld_quality": {"n_outliers": outl, "max_logLR": 1.5, "lambda": None}, "ld_allele_exact": exact,
            "ld_allele_flipped": flipped, "L_saturated": False,
            "min_abs_corr_sweep": [{"min_abs_corr": 0.5, "n_CS": n_cs, "cs_sizes": list(range(2, n_cs + 2))}]}


def test_e4_finemap_structure_and_e5():
    from ta_r4.estimands import e4_finemap_structure, e5_diagnostics, fit_frame

    f = fit_frame([("A3_1kg", "bmi", "EUR", "R1", _fitdoc(2, lam=0.7, outl=3)),
                   ("A2_identity", "bmi", "EUR", "R1", _fitdoc(0)),
                   ("A3_1kg", "t2d", "EUR", "R1", {"status": "too_many_variants", "credible_sets": None})])
    s = e4_finemap_structure(f).set_index(["arm", "trait"])
    assert s.loc[("A3_1kg", "bmi"), "n_cs"] == 2
    assert s.loc[("A3_1kg", "bmi"), "cs_sizes"] == "2;3"
    assert s.loc[("A2_identity", "bmi"), "n_cs"] == 0
    assert pd.isna(s.loc[("A3_1kg", "t2d"), "n_cs"])
    d = e5_diagnostics(f).set_index(["arm", "trait"])
    assert d.loc[("A3_1kg", "bmi"), "lambda_hat"] == 0.7
    assert d.loc[("A3_1kg", "bmi"), "kriging_n_outliers"] == 3


# ------------------------------------------------------------------ E7

def test_e7_frozen_vs_fixed_and_flipped_shares():
    from ta_r4.estimands import e7_frozen_vs_fixed, fit_frame

    w3a = pd.DataFrame({"pair": ["real_ld", "real_ld", "k2d"], "trait": ["bmi", "t2d", "bmi"],
                        "ancestry": ["EUR"] * 3, "region_safe": ["R1", "R1", "R1"],
                        "status_L": ["ok", "non_converged", "ok"], "n_cs_L": ["2", "0", "9"]})
    m = _man3()
    rid = m.row_id[0]
    sh = pd.DataFrame({"config_label": ["R2_exact", "L10_iter100"], "pair_id": [rid, rid],
                       "status": ["ok", "ok"], "pp_h4_reproduced": ["0.91", "0.1"]})
    fits = fit_frame([("A3_1kg", "bmi", "EUR", "R1", _fitdoc(1, exact=90, flipped=10)),
                      ("A3_1kg", "t2d", "EUR", "R1", _fitdoc(3, exact=60, flipped=40)),
                      ("A3_1kg", "bmi", "EUR", "R2", _fitdoc(1, exact=0, flipped=0)),
                      ("A2_identity", "bmi", "EUR", "R1", _fitdoc(5, exact=1, flipped=99))])
    rows = _rows([doc(rid, "A3_1kg", "p12_primary", 0.42), doc(rid, "A3_1kg", "p12_sensitivity", 0.9)], m)
    qtl = [{"id": "q1", "qtl_orient_exact": 3, "qtl_orient_flipped": 1},
           {"id": "q2", "qtl_orient_exact": None, "qtl_orient_flipped": None}]
    t = e7_frozen_vs_fixed(w3a, sh, fits, rows, qtl, a3_arm={"EUR": "A3_1kg"}, p12_key="p12_primary")
    fy = t[t.section == "fit_yield"].set_index("id")
    assert set(fy.index) == {"bmi.EUR.R1", "t2d.EUR.R1"}
    assert fy.loc["bmi.EUR.R1", ["frozen_value", "fixed_value"]].tolist() == ["ok;n_cs=2", "ok;n_cs=1"]
    assert fy.loc["t2d.EUR.R1", "fixed_value"] == "ok;n_cs=3"
    sp = t[t.section == "sh2b3_pair"].set_index("id")
    assert sp.index.tolist() == [rid]
    assert float(sp.loc[rid, "frozen_value"]) == 0.91 and float(sp.loc[rid, "fixed_value"]) == 0.42
    fr = t[t.section == "flipped_share_region"].set_index("id")
    assert fr.loc["R1", "flipped_share"] == pytest.approx(50 / 200)
    assert math.isnan(fr.loc["R2", "flipped_share"])
    fq = t[t.section == "flipped_share_qtl"].set_index("id")
    assert fq.loc["q1", "flipped_share"] == pytest.approx(0.25)
    assert math.isnan(fq.loc["q2", "flipped_share"])


# ------------------------------------------------------------------ E8 / Wilson

def test_wilson_ci():
    from ta_r4.estimands import wilson_ci

    lo, hi = wilson_ci(0, 200)
    assert lo == 0.0
    assert hi == pytest.approx(0.0188, abs=1e-4)
    z = 1.959963984540054
    assert hi == pytest.approx(z * z / (200 + z * z), rel=1e-12)
    lo, hi = wilson_ci(200, 200)
    assert hi == pytest.approx(1.0) and lo == pytest.approx(1 - z * z / (200 + z * z), rel=1e-12)
    assert all(math.isnan(x) for x in wilson_ci(0, 0))


def test_e8_simulation_rates():
    from ta_r4.estimands import e8_simulation_rates

    recs = []
    for rep in range(200):
        recs.append({"region": "R1", "scenario": "H3_r2_0.6", "gen_panel": "gen_1kg", "rep": rep + 1, "arm": "A2",
                     "method": "coloc_susie", "pp_h4": 0.1, "pp_h4_max": 0.9 if rep < 50 else 0.5})
        recs.append({"region": "R1", "scenario": "H3_r2_0.6", "gen_panel": "gen_1kg", "rep": rep + 1, "arm": "A3",
                     "method": "coloc_susie", "pp_h4": 0.1, "pp_h4_max": 0.1})
        recs.append({"region": "R1", "scenario": "H4", "gen_panel": "gen_ukb", "rep": rep + 1, "arm": "A1",
                     "method": "A1_abf_matched", "pp_h4": 0.95 if rep % 2 else 0.2, "pp_h4_max": 0.95 if rep % 2 else 0.2})
    t = e8_simulation_rates(pd.DataFrame(recs), threshold=0.8).set_index(["arm", "scenario", "gen_panel"])
    assert t.loc[("A2", "H3_r2_0.6", "gen_1kg"), ["n", "k"]].tolist() == [200, 50]
    assert t.loc[("A2", "H3_r2_0.6", "gen_1kg"), "rate"] == 0.25
    assert t.loc[("A2", "H3_r2_0.6", "gen_1kg"), "quantity"] == "false_H4"
    assert t.loc[("A3", "H3_r2_0.6", "gen_1kg"), "ci_hi"] == pytest.approx(0.0188, abs=1e-4)
    assert t.loc[("A3", "H3_r2_0.6", "gen_1kg"), "r2_bin"] == "0.6"
    assert t.loc[("A1", "H4", "gen_ukb"), "quantity"] == "true_H4"
    assert t.loc[("A1", "H4", "gen_ukb"), "rate"] == 0.5


# ------------------------------------------------------------------ FINAL / DRAFT label

def _w4a_raw(repo):
    import datetime as dt

    from ta_r4.signoff import canonical_sha256

    dr = yaml.safe_load((repo / "config/ta_r4/decision_rules.yaml").read_text())
    pri = yaml.safe_load((repo / "config/ta_r4/coloc_priors.yaml").read_text())
    lines = [f"carter-approved {dt.date.today().isoformat()}", f"p12_primary: {pri['p12_primary']}",
             f"kappa_cut: {dr['kappa_cut']}", f"n_both_min: {dr['n_both_min']}"]
    lines += [f"partial_rule.{k}: {v}" for k, v in dr["partial_rule"].items()]
    lines += [f"confirmatory_sha256: {canonical_sha256(dr['confirmatory'])}", "draft: approved"]
    return "\n".join(lines) + "\n"


@pytest.fixture
def fixture_repo(tmp_path):
    from .fixtures.make_fixture_repo import make_fixture_repo

    return make_fixture_repo(tmp_path)


def _sign_w4a(repo, raw):
    from ta_r4.r4_lock_gate import SIGNOFF_REL
    from ta_r4.signoff import record_signoff

    record_signoff("W4a-T3", raw, min_date="2026-10-01", signoff_dir=repo / SIGNOFF_REL)


def test_status_draft_when_unlocked(fixture_repo):
    from ta_r4.estimands import output_status, with_status

    assert output_status(fixture_repo) == "DRAFT"
    assert with_status({"x": 1}, "DRAFT")["status"] == "DRAFT"
    df = with_status(pd.DataFrame({"a": [1]}), "DRAFT")
    assert df.attrs["status"] == "DRAFT"


def test_status_draft_when_locked_without_w4a(fixture_repo):
    from ta_r4.estimands import output_status
    from .fixtures.make_fixture_repo import write_fixture_lock

    write_fixture_lock(fixture_repo)
    assert output_status(fixture_repo) == "DRAFT"


def test_status_final_with_locks_signoff_and_gate(fixture_repo):
    from ta_r4.estimands import output_status
    from .fixtures.make_fixture_repo import write_fixture_lock

    write_fixture_lock(fixture_repo)
    _sign_w4a(fixture_repo, _w4a_raw(fixture_repo))
    assert output_status(fixture_repo) == "FINAL"


def test_status_draft_when_w4a_disagrees_with_config(fixture_repo):
    from ta_r4.estimands import output_status
    from .fixtures.make_fixture_repo import write_fixture_lock

    write_fixture_lock(fixture_repo)
    _sign_w4a(fixture_repo, re.sub(r"(?m)^kappa_cut: .*$", "kappa_cut: 0.7", _w4a_raw(fixture_repo)))
    assert output_status(fixture_repo) == "DRAFT"


def test_status_draft_when_gate_fails(fixture_repo):
    from ta_r4.estimands import output_status
    from ta_r4.r4_lock_gate import LOCK_RECORD_REL
    from .fixtures.make_fixture_repo import write_fixture_lock

    write_fixture_lock(fixture_repo)
    _sign_w4a(fixture_repo, _w4a_raw(fixture_repo))
    assert output_status(fixture_repo) == "FINAL"
    p = Path(fixture_repo) / "src/python/ta_r4/estimands.py"
    p.write_text(p.read_text() + "\n# drift\n")
    assert output_status(fixture_repo) == "DRAFT"
    (Path(fixture_repo) / LOCK_RECORD_REL).unlink()
    assert output_status(fixture_repo) == "DRAFT"


def test_status_draft_for_the_real_repo():
    from ta_r4.estimands import output_status

    assert output_status(REPO_ROOT) == "DRAFT"
