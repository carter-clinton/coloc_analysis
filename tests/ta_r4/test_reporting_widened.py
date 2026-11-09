"""W3f 15.4 Task 1: outcome-state drops (N8), status-agnostic cross-purity and leveled no-CS rates (N9), E6 = E1-E5
with drops (N10). Expected counts are hand-computed in each test."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from .conftest import REPO_ROOT
from .fixtures.estimand_fixtures import doc, manifest, mrow

RULES = yaml.safe_load((REPO_ROOT / "config/ta_r4/decision_rules.yaml").read_text())
PAIRS4 = [("asthma", "bmi"), ("asthma", "t2d"), ("bmi", "t2d"), ("bmi", "stroke")]
K = "p12_primary"
RULE = "both methods coloc_susie"


def _none(row_id, label, reason):
    d = doc(row_id, label, K, 0.0, method="none", n_cs=(None, None))
    d.update({"pp_h4_max": None, "none_reason": reason})
    return d


def _fixture():
    """R1, 4 rows. X = A3_ukb, ref = A3_1kg.
    r1: X coloc_susie, ref coloc_susie                -> paired, finite, both_have_cs
    r2: X fallback_abf (n_cs 0,2), ref coloc_susie    -> paired, finite, not both_have_cs
    r3: X none fit_early_exit, ref coloc_susie        -> paired, not finite
    r4: X none coloc_susie_empty, ref no output       -> unpaired"""
    m = manifest([mrow("R1", "EUR", p) for p in PAIRS4])
    r1, r2, r3, r4 = m.row_id
    docs = [doc(r1, "A3_ukb", K, 0.9), doc(r1, "A3_1kg", K, 0.85, h3=0.1),
            doc(r2, "A3_ukb", K, 0.4, method="fallback_abf", n_cs=(0, 2)), doc(r2, "A3_1kg", K, 0.2),
            _none(r3, "A3_ukb", "fit_early_exit:too_many_variants|ok"), doc(r3, "A3_1kg", K, 0.3),
            _none(r4, "A3_ukb", "coloc_susie_empty")]
    from ta_r4.estimands import build_rows

    return m, build_rows(docs, m)


# ------------------------------------------------------------------ N8 row_drops

def test_row_drop_table_hand_counts():
    from ta_r4.estimands import row_drop_table

    m, rows = _fixture()
    t = row_drop_table(rows, m, [("A3_ukb", "A3_1kg", "native", RULE)], [K]).set_index("side")
    assert len(t) == 2
    x, r = t.loc["x"], t.loc["ref"]
    assert x.label == "A3_ukb" and r.label == "A3_1kg"
    assert x.contrast == r.contrast == "A3_ukb_vs_A3_1kg" and x.p12_key == K
    want_x = {"n_expected": 4, "n_output": 4, "n_coloc_susie": 1, "n_a1": 0, "n_fallback": 1, "n_method_none": 2,
              "n_none_fit_early_exit": 1, "n_none_coloc_susie_empty": 1, "n_none_coloc_susie_no_finite_h4": 0,
              "n_paired": 3, "n_paired_finite": 2, "n_both_have_cs": 1, "n_dropped_not_both_have_cs": 1}
    want_r = {"n_expected": 4, "n_output": 3, "n_coloc_susie": 3, "n_a1": 0, "n_fallback": 0, "n_method_none": 0,
              "n_none_fit_early_exit": 0, "n_none_coloc_susie_empty": 0, "n_none_coloc_susie_no_finite_h4": 0,
              "n_paired": 3, "n_paired_finite": 2, "n_both_have_cs": 1, "n_dropped_not_both_have_cs": 1}
    for col, v in want_x.items():
        assert int(x[col]) == v, col
    for col, v in want_r.items():
        assert int(r[col]) == v, col


def test_row_drop_table_a1_side_and_both_keys():
    from ta_r4.estimands import build_rows, row_drop_table

    m = manifest([mrow("R1", "EUR", p) for p in PAIRS4[:2]])
    r1, r2 = m.row_id
    docs = [doc(r1, "A1_matched", k, 0.5) for k in ("p12_primary", "p12_sensitivity")]
    docs += [doc(r1, "A3_1kg", k, 0.4) for k in ("p12_primary", "p12_sensitivity")]
    docs += [doc(r2, "A3_1kg", "p12_primary", 0.4)]
    rows = build_rows(docs, m)
    t = row_drop_table(rows, m, [("A1_matched", "A3_1kg", "matched", "A3_1kg method coloc_susie")],
                       ["p12_primary", "p12_sensitivity"]).set_index(["p12_key", "side"])
    assert len(t) == 4
    assert t.loc[("p12_primary", "x"), ["n_output", "n_a1", "n_paired", "n_both_have_cs"]].astype(int).tolist() == [1, 1, 1, 1]
    assert t.loc[("p12_primary", "ref"), ["n_output", "n_coloc_susie"]].astype(int).tolist() == [2, 2]
    assert int(t.loc[("p12_sensitivity", "ref"), "n_output"]) == 1


def test_row_drop_table_rejects_unknown_method():
    from ta_r4.estimands import row_drop_table

    m, rows = _fixture()
    rows.loc[rows.method == "fallback_abf", "method"] = "mystery"
    with pytest.raises(ValueError, match="mystery"):
        row_drop_table(rows, m, [("A3_ukb", "A3_1kg", "native", RULE)], [K])


# ------------------------------------------------------------------ N9 no-CS rate levels

def _fits():
    from ta_r4.estimands import fit_frame

    def f(n_cs, status="ok", lam=0.1, outl=0):
        cs = {f"CS{i + 1}": [{"CHR": "1", "POS": j} for j in range(2)] for i in range(n_cs)}
        return {"status": status, "credible_sets": cs, "d3b_ld_z_consistency_s": lam,
                "d3_ld_quality": {"n_outliers": outl, "max_logLR": 1.0}}

    return fit_frame([("A3_ukb", "asthma", "EUR", "R1", f(2, lam=0.3, outl=1)),
                      ("A3_ukb", "bmi", "EUR", "R1", f(0, lam=0.5, outl=3)),
                      ("A3_ukb", "t2d", "EUR", "R1", {"status": "too_many_variants", "credible_sets": None}),
                      ("A3_1kg", "asthma", "EUR", "R1", f(1, status="non_converged", lam=0.2)),
                      ("A3_1kg", "bmi", "EUR", "R1", f(1, lam=0.4, outl=2)),
                      ("A3_1kg", "bmi", "EUR", "R2", f(0))])


def test_e4_no_cs_rate_levels_and_denominators():
    from ta_r4.estimands import e4_no_cs_rate

    _, rows = _fixture()
    t = e4_no_cs_rate(rows, _fits())
    assert set(t.level) == {"pair_row", "region", "fit"}
    den = dict(zip(t.level, t.denominator))
    assert den == {"pair_row": "pair rows of the arm", "region": "pair rows of the arm in the region",
                   "fit": "fits of the arm"}
    pr = t[t.level == "pair_row"].set_index("label")
    assert pr.loc["A3_ukb", ["n_rows", "n_no_cs"]].astype(int).tolist() == [4, 1]  # r2 n_cs_a == 0
    assert pr.loc["A3_ukb", "no_cs_rate"] == pytest.approx(0.25)
    rg = t[t.level == "region"].set_index(["label", "region_safe"])
    assert rg.loc[("A3_ukb", "R1"), ["n_rows", "n_no_cs"]].astype(int).tolist() == [4, 1]
    ft = t[t.level == "fit"].set_index("label")
    # A3_ukb: 3 fits, bmi has 0 sets, t2d exited early (no sets): 2 of 3; A3_1kg: 3 fits, R2 bmi 0 sets: 1 of 3
    assert ft.loc["A3_ukb", ["n_rows", "n_no_cs", "n_early_exit"]].astype(int).tolist() == [3, 2, 1]
    assert ft.loc["A3_1kg", ["n_rows", "n_no_cs", "n_early_exit"]].astype(int).tolist() == [3, 1, 0]
    assert ft.loc["A3_1kg", "no_cs_rate"] == pytest.approx(1 / 3)


# ------------------------------------------------------------------ N9 cross-purity

def test_cross_purity_pairs():
    from ta_r4.run_aggregation import CROSS_PURITY

    assert [(f, p) for f, p, _ in CROSS_PURITY] == [
        ("A2_identity", "A3_1kg"), ("A3_ukb", "A3_1kg"), ("A3_1kg", "A3_ukb"), ("A3_ukb_isect", "A3_1kg_isect"),
        ("A3_1kg_isect", "A3_ukb_isect"), ("AFR661_A2", "AFR661_A3"), ("AFR504_A3", "AFR661_A3"),
        ("AFR661_A3", "AFR504_A3")]
    absent = {(f, p) for f, p, a in CROSS_PURITY if a}
    assert absent == {("A3_ukb", "A3_1kg"), ("A3_1kg", "A3_ukb"), ("AFR504_A3", "AFR661_A3"),
                      ("AFR661_A3", "AFR504_A3")}


def test_cross_purity_is_status_agnostic(tmp_path):
    from ta_r4 import paths
    from ta_r4.run_aggregation import _cross_purity

    fits = _fits()
    calls = []

    def runner(repo, rds, panel, allow_absent):
        calls.append((Path(rds).name, Path(panel).name, allow_absent))
        if Path(rds).name.startswith("bmi."):  # a fit whose RDS has no credible set
            return pd.DataFrame(columns=["cs", "size", "min_abs_corr", "mean_abs_corr", "purity_fit",
                                         "n_cs_variants", "n_present", "note"])
        return pd.DataFrame([{"cs": "L1", "size": 3, "min_abs_corr": float("nan"), "mean_abs_corr": float("nan"),
                              "purity_fit": 0.9, "n_cs_variants": 3, "n_present": 1, "note": "fewer_than_2_present"}])

    for f in fits.itertuples():
        if f.status not in ("too_many_variants", "no_variants"):
            p = tmp_path / paths.fit_rds(f.arm, f.trait, f.ancestry, f.region_safe)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x")
    for arm, reg in (("A3_1kg", "R1"), ("A3_1kg", "R2"), ("A3_ukb", "R1")):
        p = tmp_path / paths.panel_path(arm, reg)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x")
    t = _cross_purity(tmp_path, fits, runner)
    k = t.set_index(["fit_arm", "panel_arm", "trait", "region_safe"])
    # non_converged A3_1kg asthma fit is scored against A3_ukb
    nc = k.loc[("A3_1kg", "A3_ukb", "asthma", "R1")]
    assert nc.cs == "L1" and nc.note == "fewer_than_2_present"
    assert int(nc.n_cs_variants) == 3 and int(nc.n_present) == 1 and pd.isna(nc.min_abs_corr)
    assert k.loc[("A3_ukb", "A3_1kg", "t2d", "R1"), "note"] == "early_exit"
    assert k.loc[("A3_ukb", "A3_1kg", "bmi", "R1"), "note"] == "no_cs"
    assert k.loc[("A3_1kg", "A3_ukb", "bmi", "R2"), "note"] == "panel_missing"
    assert all(a for _, _, a in calls)  # native pairs allow absent members
    assert len(t) == 6  # 3 A3_ukb fits + 3 A3_1kg fits; no other arm has fits


# ------------------------------------------------------------------ N10 E6 long format

def test_e6_panel_contrast_is_e1_to_e5_with_drops():
    from ta_r4.estimands import e6_panel_contrast

    m, rows = _fixture()
    t = e6_panel_contrast(rows, _fits(), RULES, set(m.row_id), [("A3_ukb", "A3_1kg", "native", RULE)], [K])
    assert list(t.columns) == ["variant_set", "contrast", "p12_key", "estimand", "subset", "metric", "value"]
    assert set(t.estimand) == {"E1", "E2", "E3", "E4", "E5", "drops"}
    for e in ("E1", "E2", "E3"):
        assert set(t[t.estimand == e].subset) == {"both_have_cs", "all_rows"}, e
    v = t.set_index(["estimand", "subset", "metric"]).value
    assert v[("E1", "both_have_cs", "n")] == 1 and v[("E1", "all_rows", "n")] == 2
    assert v[("E1", "all_rows", "n_fallback")] == 1
    assert v[("E1", "both_have_cs", "median_delta")] == pytest.approx(0.05)
    for thr in RULES["sweep"]:
        assert ("E2", "all_rows", f"kappa@{thr}") in v.index
    # r1 0.9 vs 0.85 (both call H4), r2 0.4 vs 0.2 (neither)
    assert [v[("E2", "all_rows", f"{c}@0.8")] for c in ("n", "a", "b", "c", "d")] == [2, 1, 0, 0, 1]
    assert v[("E2", "both_have_cs", "n@0.8")] == 1
    assert v[("E3", "all_rows", "H4->H4")] == 1 and v[("E3", "all_rows", "H3->H3")] == 1
    assert v[("E4", "-", "x.pair_row.n_no_cs")] == 1 and v[("E4", "-", "x.pair_row.n_rows")] == 4
    assert v[("E4", "-", "x.fit.n_no_cs")] == 2 and v[("E4", "-", "ref.fit.n_rows")] == 2  # R1 fits only
    assert v[("E5", "-", "x.median_lambda_hat")] == pytest.approx(0.4)  # A3_ukb ok fits 0.3, 0.5 (t2d NaN)
    assert v[("E5", "-", "ref.median_kriging_n_outliers")] == pytest.approx(1.0)  # 0, 2
    assert v[("drops", "-", "x.n_method_none")] == 2 and v[("drops", "-", "ref.n_output")] == 3
    assert v[("drops", "-", "x.n_dropped_not_both_have_cs")] == 1
