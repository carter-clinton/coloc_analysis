"""The confirmatory contrast: selection, subsets and category rules come from decision_rules.yaml (W3d)."""
from __future__ import annotations

import copy
import json
import math

import pandas as pd
import pytest
import yaml

from .conftest import REPO_ROOT
from .fixtures.estimand_fixtures import doc, manifest, mrow, universe

RULES_PATH = REPO_ROOT / "config/ta_r4/decision_rules.yaml"
KEYS = {"n_rows", "n_both", "median_delta", "mean_delta", "ci_lo", "ci_hi", "sign_p", "mcnemar_b", "mcnemar_c",
        "mcnemar_p", "kappa", "observed_agreement", "categories", "n_regions", "signflip_T", "signflip_k",
        "signflip_p", "signflip_method", "signflip_direction"}


@pytest.fixture(scope="module")
def rules():
    from ta_r4.estimands import load_rules

    return load_rules(RULES_PATH)


@pytest.fixture(scope="module")
def uni():
    return universe()


def _rows(docs, man):
    from ta_r4.estimands import build_rows

    return build_rows(docs, man)


def _cs(rows, x, rules):
    from ta_r4.estimands import contrast_stats

    return contrast_stats(rows, x, "A3_1kg", rules)


def _canon(d):
    return json.dumps(d, sort_keys=True, default=str)


# ------------------------------------------------------------------ selection on the real manifest

def test_real_manifest_confirmatory_rows(rules):
    from ta_r4.estimands import confirmatory_rows, load_manifest

    sel = confirmatory_rows(load_manifest(REPO_ROOT), rules)
    assert len(sel) == 100
    assert sel.region_safe.nunique() == 10
    assert set(sel.row_class) == {"primary"} and set(sel.ancestry) == {"EUR"} and set(sel.admissible) == {"true"}
    assert not any(r.startswith("NC_") for r in sel.region_safe)


def test_selection_is_read_from_the_yaml(tmp_path, rules):
    from ta_r4.estimands import confirmatory_rows, load_manifest, load_rules

    y = yaml.safe_load(RULES_PATH.read_text())
    y["confirmatory"]["rows"]["ancestry"] = "AFR"
    p = tmp_path / "decision_rules.yaml"
    p.write_text(yaml.safe_dump(y))
    afr = confirmatory_rows(load_manifest(REPO_ROOT), load_rules(p))
    assert len(afr) == 30 and set(afr.ancestry) == {"AFR"}
    man, docs = universe()
    rows = _rows(docs, man)
    assert _cs(rows, "A2_identity", rules)["n_rows"] == 50
    assert _cs(rows, "A2_identity", load_rules(p))["n_rows"] == 0


# ------------------------------------------------------------------ output shape and subsets

def test_returned_keys_and_counts(uni, rules):
    man, docs = uni
    s = _cs(_rows(docs, man), "A2_identity", rules)
    assert set(s) >= KEYS
    assert set(s["categories"]) == {"n_both_ok", "ci", "mcnemar", "kappa_ok"}
    assert s["n_rows"] == 50 and s["n_both"] == 50 and s["n_regions"] == 10
    assert s["median_delta"] > 0 and s["ci_lo"] > 0
    assert s["categories"]["ci"] == "pos" and s["categories"]["n_both_ok"] is True


def test_clusters_are_the_confirmatory_regions(uni, rules, monkeypatch):
    from ta_r4 import estimands

    seen = {}
    real = estimands.cluster_bootstrap_ci

    def spy(values, clusters, **kw):
        seen["clusters"] = set(clusters)
        seen["B"], seen["seed"] = kw.get("B"), kw.get("seed")
        return real(values, clusters, **kw)

    monkeypatch.setattr(estimands, "cluster_bootstrap_ci", spy)
    man, docs = uni
    _cs(_rows(docs, man), "A2_identity", rules)
    assert seen["clusters"] == {f"REG{i:02d}" for i in range(10)}
    assert (seen["B"], seen["seed"]) == (10000, 20261021)


def test_both_have_cs_subset_rules(uni, rules):
    man, docs = uni
    docs = copy.deepcopy(docs)
    conf = set(man.row_id[(man.row_class == "primary") & (man.ancestry == "EUR") & (man.admissible == "true")])
    ids = sorted(conf)
    for d in docs:
        if d["p12_key"] != "p12_primary" or d["row_id"] not in conf:
            continue
        if d["row_id"] in ids[:3] and d["arm"] == "A2_identity":
            d["method"] = "fallback_abf"
        if d["row_id"] in ids[3:5] and d["arm"] == "A3_1kg":
            d["method"] = "fallback_abf"
    rows = _rows(docs, man)
    a2 = _cs(rows, "A2_identity", rules)
    a1 = _cs(rows, "A1_matched", rules)
    assert (a2["n_rows"], a2["n_both"]) == (50, 45)
    assert (a1["n_rows"], a1["n_both"]) == (50, 48)


def test_mcnemar_b_c_orientation(rules):
    man = manifest([mrow(f"R{i}", "EUR", ("asthma", "bmi")) for i in range(12)])
    docs = []
    for i, rid in enumerate(man.row_id):
        x, ref = (0.9, 0.1) if i < 7 else ((0.1, 0.9) if i < 8 else (0.1, 0.1))
        docs += [doc(rid, "A2_identity", "p12_primary", x), doc(rid, "A3_1kg", "p12_primary", ref)]
    s = _cs(_rows(docs, man), "A2_identity", rules)
    assert (s["mcnemar_b"], s["mcnemar_c"]) == (7, 1)
    assert s["mcnemar_p"] == pytest.approx(2 * 9 / 256)
    assert s["categories"]["mcnemar"] == "ns"


# ------------------------------------------------------------------ negative / positive controls on selection

def _perturb(docs, man, pred):
    out = copy.deepcopy(docs)
    mi = man.set_index("row_id")
    n = 0
    for d in out:
        if pred(d, mi.loc[d["row_id"]]):
            d["pp_h4"] = d["pp_h4_max"] = 0.999 if d["pp_h4_max"] < 0.5 else 0.001
            n += 1
    assert n > 0
    return out


@pytest.mark.parametrize("what, pred", [
    ("negative_control", lambda d, m: m.row_class == "negative_control"),
    ("AFR", lambda d, m: m.ancestry == "AFR"),
    ("p12_sensitivity", lambda d, m: d["p12_key"] == "p12_sensitivity"),
    ("A1_allvars", lambda d, m: d["mode"] == "A1_allvars"),
    ("repro_arm", lambda d, m: d["arm"].startswith("repro_")),
    ("A3_ukb_and_isect", lambda d, m: d["arm"] in ("A3_ukb", "A3_ukb_isect", "A3_1kg_isect")),
])
def test_non_confirmatory_rows_never_move_the_stats(uni, rules, what, pred):
    man, docs = uni
    rules = dict(rules, bootstrap_B=1000)  # selection property; B only sets run time
    for x in ("A2_identity", "A1_matched"):
        base = _cs(_rows(docs, man), x, rules)
        pert = _cs(_rows(_perturb(docs, man, pred), man), x, rules)
        assert _canon(base) == _canon(pert), (what, x)


def test_one_confirmatory_row_moves_the_median(uni, rules):
    from ta_r4.estimands import e1_paired_delta

    man, docs = uni
    rows = _rows(docs, man)
    base = _cs(rows, "A2_identity", rules)
    sub = e1_paired_delta(rows, "A2_identity", "A3_1kg", "p12_primary", "both methods coloc_susie")["both_have_cs"]
    sub = sub[sub.row_id.isin(set(man.row_id[man.row_class == "primary"]))].sort_values("delta")
    target = sub.row_id.iloc[len(sub) // 2 - 1]
    pert = copy.deepcopy(docs)
    for d in pert:
        if d["row_id"] == target and d["arm"] == "A2_identity" and d["p12_key"] == "p12_primary":
            d["pp_h4"] = d["pp_h4_max"] = 0.0
    s = _cs(_rows(pert, man), "A2_identity", rules)
    assert s["median_delta"] != base["median_delta"]


# ------------------------------------------------------------------ category rules (each edge case)

def _stats(**kw):
    s = {"n_both": 20, "n_regions": 10, "ci_lo": -0.1, "ci_hi": 0.1, "mcnemar_p": 0.5, "mcnemar_b": 3,
         "mcnemar_c": 3, "signflip_p": 0.5, "signflip_T": 0, "kappa": 0.7, "observed_agreement": 0.9}
    s.update(kw)
    return s


@pytest.mark.parametrize("kw, key, want", [
    ({"n_both": 10}, "n_both_ok", True),
    ({"n_both": 9}, "n_both_ok", False),
    ({"ci_lo": 0.0, "ci_hi": 0.2}, "ci", "incl0"),
    ({"ci_lo": 1e-12, "ci_hi": 0.2}, "ci", "pos"),
    ({"ci_lo": -0.2, "ci_hi": -1e-12}, "ci", "neg"),
    ({"ci_lo": -0.2, "ci_hi": 0.0}, "ci", "incl0"),
    ({"ci_lo": float("nan"), "ci_hi": float("nan")}, "ci", "incl0"),
    ({"signflip_p": 0.025, "signflip_T": 9}, "mcnemar", "ns"),
    ({"signflip_p": 0.0249, "signflip_T": 9}, "mcnemar", "sig_X_gt_A3"),
    ({"signflip_p": 0.0249, "signflip_T": -9}, "mcnemar", "sig_A3_gt_X"),
    ({"signflip_p": 0.0249, "signflip_T": 0}, "mcnemar", "ns"),
    ({"mcnemar_p": 0.0001, "mcnemar_b": 9, "mcnemar_c": 0}, "mcnemar", "ns"),
    ({"kappa": 0.6}, "kappa_ok", True),
    ({"kappa": 0.5999}, "kappa_ok", False),
    ({"kappa": float("nan"), "observed_agreement": 1.0}, "kappa_ok", True),
    ({"kappa": float("nan"), "observed_agreement": float("nan")}, "kappa_ok", False),
])
def test_category_edges(rules, kw, key, want):
    from ta_r4.estimands import categorize

    assert categorize(_stats(**kw), rules)[key] == want


def test_category_cutoffs_read_from_rules(rules):
    from ta_r4.estimands import categorize

    r = copy.deepcopy(rules)
    r["n_both_min"], r["kappa_cut"], r["alpha"] = 5, 0.8, 0.6
    c = categorize(_stats(n_both=6, kappa=0.7, signflip_p=0.5, signflip_T=9), r)
    assert (c["n_both_ok"], c["kappa_ok"], c["mcnemar"]) == (True, False, "sig_X_gt_A3")


@pytest.mark.parametrize("n_both", [0, 1])
def test_ci_undefined_for_n_both_below_two(rules, n_both):
    man = manifest([mrow(f"R{i}", "EUR", ("asthma", "bmi")) for i in range(3)])
    docs = []
    for i, rid in enumerate(man.row_id):
        m = "coloc_susie" if i < n_both else "fallback_abf"
        docs += [doc(rid, "A2_identity", "p12_primary", 0.9), doc(rid, "A3_1kg", "p12_primary", 0.2, method=m)]
    s = _cs(_rows(docs, man), "A2_identity", rules)
    assert s["n_both"] == n_both and s["n_rows"] == 3
    assert math.isnan(s["ci_lo"]) and math.isnan(s["ci_hi"])
    assert s["categories"]["ci"] == "incl0"
    assert s["categories"]["n_both_ok"] is False


def test_kappa_undefined_reported_na(rules):
    man = manifest([mrow(f"R{i}", "EUR", ("asthma", "bmi")) for i in range(4)])
    docs = []
    for rid in man.row_id:
        docs += [doc(rid, "A2_identity", "p12_primary", 0.1), doc(rid, "A3_1kg", "p12_primary", 0.2)]
    s = _cs(_rows(docs, man), "A2_identity", rules)
    assert math.isnan(s["kappa"]) and s["observed_agreement"] == 1.0
    assert s["categories"]["kappa_ok"] is True


def test_non_confirmatory_contrast_refused(uni, rules):
    from ta_r4.estimands import contrast_stats

    man, docs = uni
    rows = _rows(docs, man)
    with pytest.raises(ValueError):
        contrast_stats(rows, "A3_ukb", "A3_1kg", rules)
    with pytest.raises(ValueError):
        contrast_stats(rows, "A2_identity", "A3_ukb", rules)
