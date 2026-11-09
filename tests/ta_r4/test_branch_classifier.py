"""Outcome-branch classifier: total over the 36 category combinations, explicit precedence (W3d; D-26, checker W5)."""
from __future__ import annotations

import copy
import itertools
from collections import Counter

import pytest
import yaml

from .conftest import REPO_ROOT

RULES_PATH = REPO_ROOT / "config/ta_r4/decision_rules.yaml"
PARTIAL_KEYS = ("ci_pos_mcnemar_ns", "ci_pos_mcnemar_opposite", "ci_neg_mcnemar_ns", "ci_neg_mcnemar_opposite")
CI = ("pos", "neg", "incl0")
MCN = ("sig_X_gt_A3", "sig_A3_gt_X", "ns")


@pytest.fixture
def rules():
    return yaml.safe_load(RULES_PATH.read_text())


def _cat(n_both_ok, ci, mcnemar, kappa_ok):
    return {"n_both_ok": n_both_ok, "ci": ci, "mcnemar": mcnemar, "kappa_ok": kappa_ok}


def test_rules_carry_precedence_and_four_partial_keys(rules):
    assert rules["precedence"] == ["n_both", "ci_includes_0", "ci_mcnemar_agree", "partial_rule"]
    assert set(rules["partial_rule"]) == set(PARTIAL_KEYS)
    assert rules["locked"] is False


def test_truth_table_is_total_and_unique(rules):
    from ta_r4.branch_classifier import enumerate_truth_table

    tt = enumerate_truth_table(rules)
    assert len(tt) == 36
    keys = [(r["n_both_ok"], r["ci"], r["mcnemar"], r["kappa_ok"]) for r in tt]
    assert len(set(keys)) == 36
    assert set(keys) == set(itertools.product((True, False), CI, MCN, (True, False)))
    for r in tt:
        assert r["branch"] and r["via"]


def test_per_branch_counts(rules):
    from ta_r4.branch_classifier import enumerate_truth_table

    tt = enumerate_truth_table(rules)
    via = Counter(r["via"].split(":")[0] for r in tt)
    assert via == {"rule1_n_both": 18, "rule2_ci_includes_0": 6, "rule3_agree": 4, "partial_rule": 8}
    non_partial = Counter(r["branch"] for r in tt if not r["via"].startswith("partial_rule"))
    assert non_partial == {"NON_INFORMATIVE": 18, "NO_SYSTEMATIC_DIFFERENCE": 3, "HETEROGENEOUS": 3,
                           "INFLATION_SUPPORTED": 2, "DEFLATION": 2}
    assert sum(non_partial.values()) + via["partial_rule"] == 36


def test_heterogeneous_total_is_11_under_the_proposed_partial_rules(rules):
    """T13: 3 HETEROGENEOUS by rule 2 + 8 partial-rule rows, all HETEROGENEOUS in the committed yaml."""
    from ta_r4.branch_classifier import enumerate_truth_table

    assert set(rules["partial_rule"].values()) == {"HETEROGENEOUS"}
    total = Counter(r["branch"] for r in enumerate_truth_table(rules))
    print("truth table branch totals:", dict(sorted(total.items())))
    assert total == {"NON_INFORMATIVE": 18, "NO_SYSTEMATIC_DIFFERENCE": 3, "HETEROGENEOUS": 11,
                     "INFLATION_SUPPORTED": 2, "DEFLATION": 2}


def test_partial_rule_rows_are_exactly_the_uncovered_combinations(rules):
    from ta_r4.branch_classifier import enumerate_truth_table

    tt = enumerate_truth_table(rules)
    got = {(r["ci"], r["mcnemar"], r["kappa_ok"]) for r in tt if r["via"].startswith("partial_rule")}
    pairs = {("pos", "ns"), ("pos", "sig_A3_gt_X"), ("neg", "ns"), ("neg", "sig_X_gt_A3")}
    assert got == {(c, m, k) for (c, m) in pairs for k in (True, False)}
    assert all(r["n_both_ok"] for r in tt if r["via"].startswith("partial_rule"))
    keys = {r["via"].split(":", 1)[1] for r in tt if r["via"].startswith("partial_rule")}
    assert keys == set(PARTIAL_KEYS)


@pytest.mark.parametrize("cat, branch, via", [
    (_cat(False, "pos", "sig_X_gt_A3", True), "NON_INFORMATIVE", "rule1_n_both"),
    (_cat(False, "incl0", "ns", True), "NON_INFORMATIVE", "rule1_n_both"),
    (_cat(True, "incl0", "sig_X_gt_A3", True), "NO_SYSTEMATIC_DIFFERENCE", "rule2_ci_includes_0"),
    (_cat(True, "incl0", "sig_A3_gt_X", False), "HETEROGENEOUS", "rule2_ci_includes_0"),
    (_cat(True, "pos", "sig_X_gt_A3", False), "INFLATION_SUPPORTED", "rule3_agree"),
    (_cat(True, "neg", "sig_A3_gt_X", True), "DEFLATION", "rule3_agree"),
    (_cat(True, "pos", "ns", True), "HETEROGENEOUS", "partial_rule:ci_pos_mcnemar_ns"),
    (_cat(True, "neg", "sig_X_gt_A3", False), "HETEROGENEOUS", "partial_rule:ci_neg_mcnemar_opposite"),
])
def test_precedence_examples(rules, cat, branch, via):
    from ta_r4.branch_classifier import classify

    assert classify(cat, rules) == (branch, via)
    assert classify({"categories": cat, "n_both": 3}, rules) == (branch, via)


def test_partial_rule_value_is_read_from_rules(rules):
    from ta_r4.branch_classifier import classify

    r = copy.deepcopy(rules)
    r["partial_rule"]["ci_pos_mcnemar_ns"] = "INFLATION_SUPPORTED"
    assert classify(_cat(True, "pos", "ns", True), r) == ("INFLATION_SUPPORTED", "partial_rule:ci_pos_mcnemar_ns")


@pytest.mark.parametrize("key", PARTIAL_KEYS)
def test_missing_partial_key_breaks_coverage(rules, key):
    from ta_r4.branch_classifier import enumerate_truth_table

    r = copy.deepcopy(rules)
    del r["partial_rule"][key]
    with pytest.raises((KeyError, ValueError)):
        enumerate_truth_table(r)


def test_swapped_precedence_moves_counts(rules):
    from ta_r4.branch_classifier import enumerate_truth_table

    r = copy.deepcopy(rules)
    r["precedence"] = ["ci_includes_0", "n_both", "ci_mcnemar_agree", "partial_rule"]
    tt = enumerate_truth_table(r)
    assert Counter(x["branch"] for x in tt)["NON_INFORMATIVE"] == 12


@pytest.mark.parametrize("bad", [
    {"precedence": ["n_both", "ci_includes_0", "ci_mcnemar_agree"]},
    {"precedence": ["n_both", "ci_includes_0", "partial_rule", "ci_mcnemar_agree"]},
    {"partial_rule": {k: "MAYBE" for k in PARTIAL_KEYS}},
])
def test_malformed_rules_refused(rules, bad):
    from ta_r4.branch_classifier import classify

    r = dict(copy.deepcopy(rules), **bad)
    with pytest.raises(ValueError):
        classify(_cat(True, "pos", "ns", True), r)


@pytest.mark.parametrize("cat", [_cat(True, "zero", "ns", True), _cat(1, "pos", "ns", True),
                                 _cat(True, "pos", "X>A3", True)])
def test_unknown_category_values_refused(rules, cat):
    from ta_r4.branch_classifier import classify

    with pytest.raises(ValueError):
        classify(cat, rules)
