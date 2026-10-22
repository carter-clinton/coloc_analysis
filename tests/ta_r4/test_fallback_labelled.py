"""D-02 enforcer: a trait with 0 credible sets gives method fallback_abf (labelled, with a reason), whose PPs equal
A1_matched exactly (Pitfall 8). Never a coloc_susie row with n_cs 0. The live gate reads only
ta_r4.paths.result_dirs("coloc") (B4: repro outputs are never read)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import REPO_ROOT
from .fixtures.build_toy_workflow import coloc, ok, pair_row, pair_session_root

from ta_r4 import paths
from ta_r4.arms import ARMS

ARM = "A3_1kg"
METHODS = {"coloc_susie", "fallback_abf", "A1_abf_matched", "A1_abf_allvars"}
PP = ("pp_h0", "pp_h1", "pp_h2", "pp_h3", "pp_h4")
NO_DIRS = "no R4 coloc result dir exists yet (W5b enables)"


def coloc_result_docs(root):
    """(docs, problems) over *.json in each EXISTING dir of result_dirs("coloc"). None if no dir exists."""
    dirs = [Path(root) / d for d in paths.result_dirs("coloc")]
    present = [d for d in dirs if d.is_dir()]
    if not present:
        return None, []
    docs, problems = [], []
    for d in present:
        files = sorted(d.glob("*.json"))
        if not files:
            problems.append(f"{d}: 0 coloc JSONs")
        for f in files:
            docs.append((f, json.loads(f.read_text())))
    return docs, problems


def fallback_violations(docs):
    out = []
    for f, d in docs:
        m = d.get("method")
        if m not in METHODS:
            out.append(f"{f}: method {m!r}")
        if m == "coloc_susie" and (d.get("n_cs_a") == 0 or d.get("n_cs_b") == 0):
            out.append(f"{f}: coloc_susie with n_cs_a={d.get('n_cs_a')} n_cs_b={d.get('n_cs_b')}")
        if m == "fallback_abf" and not d.get("fallback_reason"):
            out.append(f"{f}: fallback_abf without fallback_reason")
        if m != "fallback_abf" and d.get("fallback_reason") is not None:
            out.append(f"{f}: fallback_reason on {m}")
    return out


@pytest.fixture(scope="module")
def fits(tmp_path_factory):
    return pair_session_root(tmp_path_factory)


@pytest.mark.r4_heavy
@pytest.mark.parametrize("key", ["p12_primary", "p12_sensitivity"])
def test_fallback_when_trait_b_has_no_cs(fits, key):
    row = pair_row("FIXP_NULL")
    p, d = coloc(fits, ARM, row, key, "susie")
    ok(p)
    p, a1 = coloc(fits, ARM, row, key, "A1_matched")
    ok(p)
    assert d["method"] == "fallback_abf" and d["fallback_reason"] == "n_cs_b==0"
    assert d["n_cs_a"] >= 1 and d["n_cs_b"] == 0 and d["summary"] == a1["summary"]
    print(f"{key}: fallback pp_h4 {d['pp_h4']!r} A1_matched pp_h4 {a1['pp_h4']!r}")
    assert [d[k] for k in PP] == [a1[k] for k in PP]  # identity, not tolerance (Pitfall 8)
    assert (d["n_snps"], d["variant_set_sha256"]) == (a1["n_snps"], a1["variant_set_sha256"])
    assert fallback_violations([("fallback", d), ("a1", a1)]) == []


@pytest.mark.r4_heavy
def test_both_traits_with_cs_is_coloc_susie(fits):
    p, d = coloc(fits, ARM, pair_row("FIXP_SAME"), "p12_primary", "susie")
    ok(p)
    assert d["method"] == "coloc_susie" and d["fallback_reason"] is None and d["n_cs_b"] >= 1


# --- the live gate and its controls -------------------------------------------------------------------------

def test_gate_dirs_are_result_dirs_coloc():
    dirs = paths.result_dirs("coloc")
    repro = [a for a, r in ARMS.items() if r["stage"] == "repro"]
    assert dirs == [f"data/r4/results/{a}/coloc" for a in sorted(a for a in ARMS if a not in repro)] + \
        ["data/r4/results/A1_EUR/coloc", "data/r4/results/A1_AFR/coloc"]
    assert not any(f"/{a}/" in d for d in dirs for a in repro)


def _put(root, rel, doc):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc))


GOOD = {"method": "coloc_susie", "n_cs_a": 2, "n_cs_b": 1, "fallback_reason": None}
BAD = {"method": "coloc_susie", "n_cs_a": 2, "n_cs_b": 0, "fallback_reason": None}


def test_gate_does_not_read_repro_tree(tmp_path):
    _put(tmp_path, "data/r4/results/repro_sh2b3_r2/coloc/r.p12_primary.json", BAD)
    assert coloc_result_docs(tmp_path) == (None, [])
    _put(tmp_path, "data/r4/results/A3_1kg/coloc/r.p12_primary.json", GOOD)
    docs, problems = coloc_result_docs(tmp_path)
    assert [f.parent.parent.name for f, _ in docs] == ["A3_1kg"] and problems == []
    assert fallback_violations(docs) == []


@pytest.mark.parametrize("doc,needle", [
    (BAD, "coloc_susie with n_cs_a=2 n_cs_b=0"),
    ({"method": "fallback_abf", "n_cs_a": 2, "n_cs_b": 0, "fallback_reason": None}, "without fallback_reason"),
    ({"method": "coloc.abf"}, "method 'coloc.abf'"),
    ({**GOOD, "fallback_reason": "n_cs_b==0"}, "fallback_reason on coloc_susie"),
])
def test_gate_flags_mislabelled_rows(tmp_path, doc, needle):
    _put(tmp_path, "data/r4/results/A2_identity/coloc/r.p12_primary.json", doc)
    docs, _ = coloc_result_docs(tmp_path)
    v = fallback_violations(docs)
    assert len(v) == 1 and needle in v[0], v


def test_gate_flags_empty_result_dir(tmp_path):
    (tmp_path / "data/r4/results/A1_EUR/coloc").mkdir(parents=True)
    docs, problems = coloc_result_docs(tmp_path)
    assert docs == [] and problems == [f"{tmp_path}/data/r4/results/A1_EUR/coloc: 0 coloc JSONs"]


@pytest.mark.r4_heavy
def test_live_fallback_labelled():
    docs, problems = coloc_result_docs(REPO_ROOT)
    if docs is None:
        pytest.skip(NO_DIRS)
    assert problems == []
    assert fallback_violations(docs) == []
