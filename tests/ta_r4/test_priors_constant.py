"""Priors enforcer (D-01, Pitfall 5): p1, p2, p12 come only from config/ta_r4/coloc_priors.yaml and are recorded
in every output; for one row_id and p12_key every arm used the same p12. Live gate over result_dirs("coloc")."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pytest
import yaml

from .conftest import REPO_ROOT
from .fixtures.build_toy_workflow import coloc, ok, pair_row, pair_session_root
from .test_fallback_labelled import NO_DIRS, _put, coloc_result_docs

from ta_r4 import commands, paths

ARM = "A3_1kg"
PRI = yaml.safe_load(open(REPO_ROOT / commands.COLOC_PRIORS))


def prior_violations(docs, pri=PRI):
    out = []
    for f, d in docs:
        key = d.get("p12_key")
        if key not in commands.P12_KEYS:
            out.append(f"{f}: p12_key {key!r}")
            continue
        want = {"p1": pri["p1"], "p2": pri["p2"], "p12": pri[key], "overlap_min": pri["overlap_min"],
                "trim_by_posterior": pri["trim_by_posterior"]}
        for k, v in want.items():
            if d.get(k) != v:
                out.append(f"{f}: {k} {d.get(k)!r} != yaml {v!r}")
    return out


def cross_arm_p12_violations(docs):
    seen = defaultdict(set)
    for _, d in docs:
        seen[(d.get("row_id"), d.get("p12_key"))].add(d.get("p12"))
    return [f"{row} {key}: p12 values {sorted(v, key=repr)}" for (row, key), v in sorted(seen.items(), key=repr)
            if len(v) > 1]


@pytest.fixture(scope="module")
def fits(tmp_path_factory):
    return pair_session_root(tmp_path_factory)


@pytest.mark.r4_heavy
def test_every_mode_records_yaml_priors(fits):
    docs = []
    for region, mode in (("FIXP_SAME", "susie"), ("FIXP_NULL", "susie"), ("FIXP_SAME", "A1_matched"),
                         ("FIXP_MIX", "A1_allvars")):
        for key in commands.P12_KEYS:
            p, d = coloc(fits, ARM, pair_row(region), key, mode)
            ok(p)
            assert d["p12_key"] == key and d["p12"] == PRI[key]
            docs.append((f"{region}.{mode}.{key}", d))
    assert {d["method"] for _, d in docs} == {"coloc_susie", "fallback_abf", "A1_abf_matched", "A1_abf_allvars"}
    assert prior_violations(docs) == []


@pytest.mark.r4_heavy
def test_explicit_prior_moves_the_answer(fits, tmp_path):
    """The yaml value reaches coloc: a yaml with another p12_primary changes PP.H4 for susie and A1."""
    alt = dict(PRI, p12_primary=1e-5)
    (tmp_path / "pri.yaml").write_text(yaml.safe_dump(alt))
    for region, mode in (("FIXP_SAME", "susie"), ("FIXP_SAME", "A1_matched")):
        _, base = coloc(fits, ARM, pair_row(region), "p12_primary", mode)
        p, d = coloc(fits, ARM, pair_row(region), "p12_primary", mode, ["--priors", tmp_path / "pri.yaml"])
        ok(p)
        assert d["p12"] == 1e-5 and d["pp_h4_max"] != base["pp_h4_max"]
        assert prior_violations([("alt", d)], alt) == [] and prior_violations([("alt", d)]) != []


# --- the live gate and its controls -------------------------------------------------------------------------

def _doc(row="R", key="p12_primary", **over):
    d = {"row_id": row, "p12_key": key, "p1": PRI["p1"], "p2": PRI["p2"], "p12": PRI[key],
         "overlap_min": PRI["overlap_min"], "trim_by_posterior": PRI["trim_by_posterior"]}
    d.update(over)
    return d


def test_gate_dirs_exclude_repro():
    from ta_r4.arms import ARMS
    dirs = set(paths.result_dirs("coloc"))
    assert {"data/r4/results/A1_EUR/coloc", "data/r4/results/A1_AFR/coloc"} <= dirs
    assert all(f"data/r4/results/{a}/coloc" not in dirs for a, r in ARMS.items() if r["stage"] == "repro")


def test_gate_ignores_repro_default_priors(tmp_path):
    """A W3b-style reproduction output (package-default priors, R2-era schema) is never read (B4)."""
    _put(tmp_path, "data/r4/results/repro_sh2b3_r2/coloc/R.p12_primary.json",
         {"pair_id": "R", "summary": {"PP.H4.abf": 0.9}, "p12": 1e-5})
    assert coloc_result_docs(tmp_path) == (None, [])
    _put(tmp_path, "data/r4/results/A3_1kg/coloc/R.p12_primary.json", _doc())
    docs, problems = coloc_result_docs(tmp_path)
    assert len(docs) == 1 and problems == [] and prior_violations(docs) == []


@pytest.mark.parametrize("over,needle", [
    ({"p12": 1e-5}, "p12 1e-05 != yaml 5e-06"),
    ({"p1": None}, "p1 None != yaml 0.0001"),
    ({"p12_key": "p12"}, "p12_key 'p12'"),
    ({"trim_by_posterior": False}, "trim_by_posterior False != yaml True"),
])
def test_gate_flags_wrong_priors(over, needle):
    v = prior_violations([("f", _doc(**over))])
    assert len(v) == 1 and needle in v[0], v


def test_gate_flags_cross_arm_p12(tmp_path):
    _put(tmp_path, "data/r4/results/A3_1kg/coloc/R.p12_primary.json", _doc())
    _put(tmp_path, "data/r4/results/A2_identity/coloc/R.p12_primary.json", _doc(p12=1e-5))
    _put(tmp_path, "data/r4/results/A1_EUR/coloc/R.matched.p12_primary.json", _doc())
    docs, _ = coloc_result_docs(tmp_path)
    assert cross_arm_p12_violations(docs) == ["R p12_primary: p12 values [1e-05, 5e-06]"]
    assert cross_arm_p12_violations([d for d in docs if "A2_identity" not in str(d[0])]) == []


@pytest.mark.r4_heavy
def test_live_priors_constant():
    docs, problems = coloc_result_docs(REPO_ROOT)
    if docs is None:
        pytest.skip(NO_DIRS)
    assert problems == []
    assert prior_violations([(f, d) for f, d in docs]) == []
    assert cross_arm_p12_violations(docs) == []
