"""Region-level sign-flip direction test and the n_regions_min floor (W3f N7;
DEC-2026-11-04-ta-r4-n7-region-signflip-and-floor)."""
from __future__ import annotations

import copy
import itertools
import math

import pytest
import yaml

from .conftest import REPO_ROOT
from .fixtures.estimand_fixtures import doc, manifest, mrow

RULES_PATH = REPO_ROOT / "config/ta_r4/decision_rules.yaml"
PAIRS = [("asthma", "bmi"), ("asthma", "t2d"), ("bmi", "t2d"), ("bmi", "stroke"), ("t2d", "stroke")]


@pytest.fixture
def rules():
    return yaml.safe_load(RULES_PATH.read_text())


def _sf(d, exact_max_k=20, B=10000, seed=20261021):
    from ta_r4.estimands import region_signflip

    return region_signflip({f"R{i:02d}": v for i, v in enumerate(d)}, exact_max_k=exact_max_k, B=B, seed=seed)


def _brute(d):
    """Independent enumeration over every sign assignment of the non-zero d_r."""
    nz = [v for v in d if v != 0]
    T = abs(sum(d))
    hits = sum(1 for s in itertools.product((1, -1), repeat=len(nz)) if abs(sum(a * b for a, b in zip(s, nz))) >= T)
    return hits / 2 ** len(nz)


# ------------------------------------------------------------------ region_signflip

@pytest.mark.parametrize("d, k, T, p", [
    ([1] * 7, 7, 7, 0.015625),
    ([1] * 6, 6, 6, 0.03125),
    ([1, 1, 1], 3, 3, 0.25),
    ([3, 1, 1], 3, 5, 0.25),
    ([2, -1], 2, 1, 1.0),
    ([0, 0, 0], 0, 0, 1.0),
])
def test_exact_p_hand_computed(d, k, T, p):
    s = _sf(d)
    assert (s["k"], s["T"], s["p"], s["method"]) == (k, T, p, "exact")


def test_direction_is_the_sign_of_T():
    assert _sf([1] * 7)["direction"] == "X>A3"
    s = _sf([-1] * 7)
    assert (s["direction"], s["T"], s["p"]) == ("A3>X", -7, 0.015625)
    assert _sf([0, 0])["direction"] == "none"
    assert _sf([2, -2])["direction"] == "none"


@pytest.mark.parametrize("d", [[3, -1, 2, 0, 1, 1, -2], [1, 1, 1, 1, -1, 2, 5, 0, 0, 1], [4, -4, 1], [1, 2, 3, 4, 5]])
def test_exact_equals_independent_enumeration(d):
    assert _sf(d)["p"] == _brute(d)


def test_exact_at_k_20_is_two_over_two_to_the_20():
    s = _sf([1] * 20)
    assert (s["k"], s["method"], s["p"]) == (20, "exact", 2 / 2 ** 20)


def test_monte_carlo_above_exact_max_k():
    d = [3, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, -1]
    exact = _brute(d)
    s = _sf(d, exact_max_k=5, B=10000, seed=20261021)
    assert s["method"] == "monte_carlo" and s["k"] == 12
    se = math.sqrt(exact * (1 - exact) / 10000)
    assert abs(s["p"] - exact) <= 4 * se, (s["p"], exact, se)
    assert s == _sf(d, exact_max_k=5, B=10000, seed=20261021)           # deterministic for a fixed seed
    n = s["p"] * 10001 - 1
    assert abs(n - round(n)) < 1e-6                                       # p = (1 + count) / (B + 1)
    assert _sf(d, exact_max_k=12)["method"] == "exact"                   # k == exact_max_k is exact


# ------------------------------------------------------------------ categorize

def _stats(**kw):
    s = {"n_both": 20, "n_regions": 10, "ci_lo": -0.1, "ci_hi": 0.1, "mcnemar_p": 0.5, "mcnemar_b": 3,
         "mcnemar_c": 3, "signflip_p": 0.5, "signflip_T": 0, "kappa": 0.7, "observed_agreement": 0.9}
    s.update(kw)
    return s


@pytest.mark.parametrize("kw, key, want", [
    ({"n_regions": 7}, "n_both_ok", True),
    ({"n_regions": 6}, "n_both_ok", False),
    ({"n_regions": 6, "n_both": 100}, "n_both_ok", False),
    ({"n_regions": 10, "n_both": 9}, "n_both_ok", False),
    ({"signflip_p": 0.0249, "signflip_T": 3}, "mcnemar", "sig_X_gt_A3"),
    ({"signflip_p": 0.0249, "signflip_T": -3}, "mcnemar", "sig_A3_gt_X"),
    ({"signflip_p": 0.025, "signflip_T": 3}, "mcnemar", "ns"),
    ({"signflip_p": 0.0249, "signflip_T": 0}, "mcnemar", "ns"),
    ({"signflip_p": 0.25, "signflip_T": 10, "mcnemar_p": 0.001953125, "mcnemar_b": 10, "mcnemar_c": 0},
     "mcnemar", "ns"),
    ({"signflip_p": 0.01, "signflip_T": 5, "mcnemar_p": 0.5, "mcnemar_b": 0, "mcnemar_c": 9},
     "mcnemar", "sig_X_gt_A3"),
])
def test_categorize_uses_regions(rules, kw, key, want):
    from ta_r4.estimands import categorize

    assert categorize(_stats(**kw), rules)[key] == want


def test_n_regions_min_read_from_rules(rules):
    from ta_r4.estimands import categorize

    r = copy.deepcopy(rules)
    assert r["confirmatory"]["n_regions_min"] == 7
    r["confirmatory"]["n_regions_min"] = 3
    assert categorize(_stats(n_regions=3), r)["n_both_ok"] is True
    assert categorize(_stats(n_regions=3), rules)["n_both_ok"] is False


def test_missing_n_regions_min_raises(rules):
    from ta_r4.estimands import categorize

    r = copy.deepcopy(rules)
    del r["confirmatory"]["n_regions_min"]
    with pytest.raises((KeyError, ValueError)):
        categorize(_stats(), r)


# ------------------------------------------------------------------ through contrast_stats

def _contrast(spec, rules):
    """spec: one list per region of (x, ref) region statistics per row (A2_identity vs A3_1kg)."""
    from ta_r4.estimands import build_rows, contrast_stats

    rows, docs = [], []
    for i, region in enumerate(spec):
        for j, (x, ref) in enumerate(region):
            r = mrow(f"REG{i:02d}", "EUR", PAIRS[j])
            rows.append(r)
            docs += [doc(r["row_id"], "A2_identity", "p12_primary", x), doc(r["row_id"], "A3_1kg", "p12_primary", ref)]
    man = manifest(rows)
    return contrast_stats(build_rows(docs, man), "A2_identity", "A3_1kg", rules, man)


B, C, N = (0.9, 0.1), (0.1, 0.9), (0.1, 0.1)   # X-only call, ref-only call, no call


def test_seven_regions_with_k_six_is_ns(rules):
    s = _contrast([[B, N]] * 6 + [[N, N]], rules)
    assert (s["n_both"], s["n_regions"], s["signflip_k"], s["signflip_T"]) == (14, 7, 6, 6)
    assert s["signflip_p"] == 0.03125 and s["signflip_method"] == "exact"
    assert s["categories"]["n_both_ok"] is True
    assert s["categories"]["mcnemar"] == "ns"


def test_rows_significant_regions_not(rules):
    s = _contrast([[B] * 4, [B] * 3, [B] * 3], rules)
    assert (s["mcnemar_b"], s["mcnemar_c"], s["mcnemar_p"]) == (10, 0, 0.001953125)   # descriptive
    assert (s["n_both"], s["n_regions"], s["signflip_k"], s["signflip_T"], s["signflip_p"]) == (10, 3, 3, 10, 0.25)
    assert s["categories"]["mcnemar"] == "ns"
    assert s["categories"]["n_both_ok"] is False


@pytest.mark.parametrize("cell, cat, direction", [(B, "sig_X_gt_A3", "X>A3"), (C, "sig_A3_gt_X", "A3>X")])
def test_eight_concordant_regions_are_significant(rules, cell, cat, direction):
    s = _contrast([[cell, N]] * 8, rules)
    assert (s["n_regions"], s["signflip_k"], s["signflip_p"]) == (8, 8, 2 / 256)
    assert s["signflip_direction"] == direction
    assert s["categories"]["mcnemar"] == cat and s["categories"]["n_both_ok"] is True


def test_missing_exact_max_k_raises(rules):
    r = copy.deepcopy(rules)
    del r["confirmatory"]["region_signflip"]["exact_max_k"]
    with pytest.raises((KeyError, ValueError)):
        _contrast([[B, N]] * 8, r)
