"""R4 outcome-branch classifier (D-26; checker W5). Steps run in the order of rules['precedence']; first match wins.

  n_both            n_both_ok False                               -> NON_INFORMATIVE                 (rule1_n_both)
  ci_includes_0     ci incl0 -> NO_SYSTEMATIC_DIFFERENCE if kappa_ok else HETEROGENEOUS        (rule2_ci_includes_0)
  ci_mcnemar_agree  ci pos + sig_X_gt_A3 -> INFLATION_SUPPORTED; ci neg + sig_A3_gt_X -> DEFLATION (rule3_agree)
  partial_rule      ci pos/neg with McNemar ns or opposite -> rules['partial_rule'][key]  (partial_rule:<key>)
"""
from __future__ import annotations

import itertools

from ta_r4.signoff import BRANCHES

CI = ("pos", "neg", "incl0")
MCNEMAR = ("sig_X_gt_A3", "sig_A3_gt_X", "ns")
PARTIAL_KEYS = ("ci_pos_mcnemar_ns", "ci_pos_mcnemar_opposite", "ci_neg_mcnemar_ns", "ci_neg_mcnemar_opposite")
AGREE = {"pos": "sig_X_gt_A3", "neg": "sig_A3_gt_X"}


def _n_both(c, rules):
    return None if c["n_both_ok"] else ("NON_INFORMATIVE", "rule1_n_both")


def _ci_includes_0(c, rules):
    if c["ci"] != "incl0":
        return None
    return ("NO_SYSTEMATIC_DIFFERENCE" if c["kappa_ok"] else "HETEROGENEOUS", "rule2_ci_includes_0")


def _ci_mcnemar_agree(c, rules):
    if c["ci"] in AGREE and c["mcnemar"] == AGREE[c["ci"]]:
        return ("INFLATION_SUPPORTED" if c["ci"] == "pos" else "DEFLATION", "rule3_agree")
    return None


def _partial_rule(c, rules):
    if c["ci"] not in AGREE or c["mcnemar"] == AGREE[c["ci"]]:
        return None
    key = f"ci_{c['ci']}_mcnemar_{'ns' if c['mcnemar'] == 'ns' else 'opposite'}"
    return (rules["partial_rule"][key], f"partial_rule:{key}")


STEPS = {"n_both": _n_both, "ci_includes_0": _ci_includes_0, "ci_mcnemar_agree": _ci_mcnemar_agree,
         "partial_rule": _partial_rule}


def _check_rules(rules):
    order = list(rules["precedence"])
    if sorted(order) != sorted(STEPS) or order[-1] != "partial_rule":
        raise ValueError(f"precedence {order} must order all of {sorted(STEPS)} with partial_rule last")
    pr = rules["partial_rule"]
    for k, v in pr.items():
        if k not in PARTIAL_KEYS or v not in BRANCHES:
            raise ValueError(f"partial_rule {k}: {v!r} (keys {PARTIAL_KEYS}, branches {BRANCHES})")
    return order


def classify(contrast_stats, rules):
    """(branch, via) for a contrast_stats dict (its 'categories') or a bare categories dict."""
    c = contrast_stats.get("categories", contrast_stats)
    if not (isinstance(c.get("n_both_ok"), bool) and isinstance(c.get("kappa_ok"), bool)
            and c.get("ci") in CI and c.get("mcnemar") in MCNEMAR):
        raise ValueError(f"categories out of domain: {c}")
    for name in _check_rules(rules):
        hit = STEPS[name](c, rules)
        if hit is not None:
            return hit
    raise ValueError(f"no rule matched {c}")


def enumerate_truth_table(rules):
    """All 2 x 3 x 3 x 2 = 36 category combinations with their (branch, via)."""
    out = []
    for nb, ci, mc, ko in itertools.product((True, False), CI, MCNEMAR, (True, False)):
        c = {"n_both_ok": nb, "ci": ci, "mcnemar": mc, "kappa_ok": ko}
        branch, via = classify(c, rules)
        out.append({**c, "branch": branch, "via": via})
    return out
