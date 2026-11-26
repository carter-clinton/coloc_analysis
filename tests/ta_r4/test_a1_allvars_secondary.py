"""A1 allvars secondary table (W3f 15.7d, F12): A1_allvars vs A3_1kg (EUR) and vs AFR661_A3 (AFR), descriptive."""
from __future__ import annotations

import importlib.util
import math
import subprocess
import types
from pathlib import Path

import pandas as pd
import pytest

from .conftest import REPO_ROOT
from .fixtures.estimand_fixtures import doc, manifest, mrow
from .test_run_aggregation import P12, PAIRS, _run, build_tree

PRE_157D_REF = "7b1e0fd2a9a1cfd42924d9bb461fa47666970a38"  # HEAD at 15.7d start
CONFIRMATORY = ("branch_outcomes", "e1_paired_delta", "e2_agreement_sweep", "e3_reclassification")
REF = {"EUR": "A3_1kg", "AFR": "AFR661_A3"}
AFR_ARMS = ("AFR661_A3", "AFR661_A2", "AFR504_A3")


def _w(p, d):
    import json

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d))


def tree(root):
    """build_tree plus 5 AFR primary rows with every AFR arm and A1 matched / allvars; A1 allvars and matched
    PP.H4 differ on every row of both ancestries."""
    root = Path(root)
    m = build_tree(root)
    afr = [mrow("AREG", "AFR", p) for p in PAIRS]
    man = pd.concat([m, manifest(afr)], ignore_index=True)
    man.to_csv(root / "config/ta_r4/pair_manifest.tsv", sep="\t", index=False)
    res = root / "data/r4/results"
    for j, r in enumerate(afr):
        rid = r["row_id"]
        for k in P12:
            b = 0.01 if k == "p12_sensitivity" else 0.0
            vals = {"AFR661_A3": 0.3 + 0.07 * j + b, "AFR661_A2": 0.6, "AFR504_A3": 0.5,
                    "A1_matched": 0.2 + 0.05 * j + b, "A1_allvars": 0.95 - 0.1 * j - b}
            for lab, h4 in vals.items():
                d = doc(rid, lab, k, h4, anc="AFR")
                if lab.startswith("A1_"):
                    _w(res / f"A1_AFR/coloc/{rid}.{lab.split('_', 1)[1]}.{k}.json", d)
                else:
                    _w(res / f"{lab}/coloc/{rid}.{k}.json", d)
    eur = m[m.ancestry == "EUR"].row_id.tolist()
    for j, rid in enumerate(eur):  # EUR allvars varies per row (build_tree writes a constant 0.5)
        for k in P12:
            _w(res / f"A1_EUR/coloc/{rid}.allvars.{k}.json",
               doc(rid, "A1_allvars", k, 0.9 - 0.02 * j - (0.01 if k == "p12_sensitivity" else 0)))
    return man


def _read(out, name):
    return pd.read_csv(Path(out) / f"{name}.tsv", sep="\t", comment="#", float_precision="round_trip")


@pytest.fixture(scope="module")
def agg(tmp_path_factory):
    root = tmp_path_factory.mktemp("a1av")
    man = tree(root / "repo")
    assert _run(root / "repo", root / "out", draft=True) == 0
    return man, root


def _ids(man, anc):
    from ta_r4 import estimands
    from ta_r4.run_aggregation import _ids

    return _ids(man, estimands.load_rules(REPO_ROOT), **({"ancestry": "AFR"} if anc == "AFR" else {}))


def test_allvars_table_has_both_ancestries_and_both_p12_keys(agg):
    _, root = agg
    t = _read(root / "out", "a1_allvars_secondary")
    assert list(t.columns) == ["ancestry", "variant_set", "contrast", "p12_key", "estimand", "subset", "metric", "value"]
    assert set(t.ancestry) == {"EUR", "AFR"}
    for anc, ref in REF.items():
        s = t[t.ancestry == anc]
        assert set(s.contrast) == {f"A1_allvars_vs_{ref}"}
        assert set(s.p12_key) == set(P12) and set(s.variant_set) == {"allvars"}
        assert set(s.estimand) == {"E1", "E2", "E3", "E4", "E5", "drops"}


def test_allvars_rows_are_the_primary_curated_and_afr_ids(agg):
    man, root = agg
    t = _read(root / "out", "a1_allvars_secondary")
    for anc in REF:
        ids = _ids(man, anc)
        assert len(ids) == {"EUR": 15, "AFR": 5}[anc]
        assert not any(i.startswith("NC_") for i in ids)
        s = t[(t.ancestry == anc) & (t.estimand == "drops")]
        assert set(s.loc[s.metric.isin(["x.n_expected", "ref.n_expected"]), "value"]) == {len(ids)}
        n = t[(t.ancestry == anc) & (t.estimand == "E1") & (t.subset == "all_rows") & (t.metric == "n")]
        assert sorted(n.value) == [len(ids)] * 2


def _e1_direct(man, root, anc, k, subset):
    from ta_r4 import estimands

    rules = estimands.load_rules(REPO_ROOT)
    rows = estimands.load_rows(root / "repo", man)
    ref = REF[anc]
    sub = estimands.e1_paired_delta(rows, "A1_allvars", ref, k, f"{ref} method coloc_susie", _ids(man, anc))[subset]
    return estimands.e1_summary(sub, rules)


def _same(a, b):
    return (math.isnan(a) and math.isnan(b)) or a == b


def test_allvars_e1_equals_a_direct_paired_computation(agg):
    man, root = agg
    t = _read(root / "out", "a1_allvars_secondary")
    n = 0
    for anc in REF:
        for k in P12:
            for subset in ("both_have_cs", "all_rows"):
                want = _e1_direct(man, root, anc, k, subset)
                s = t[(t.ancestry == anc) & (t.p12_key == k) & (t.estimand == "E1") & (t.subset == subset)]
                got = dict(zip(s.metric, s.value))
                for m, v in want.items():
                    assert _same(float(got[m]), float(v)), (anc, k, subset, m, got[m], v)
                    n += 1
    assert n == 2 * 2 * 2 * 9


def test_allvars_table_tracks_allvars_not_matched(agg):
    from ta_r4 import estimands

    man, root = agg
    rows = estimands.load_rows(root / "repo", man)
    t = _read(root / "out", "a1_allvars_secondary")
    for anc, ref in REF.items():
        for k in P12:
            ids = _ids(man, anc)
            rule = f"{ref} method coloc_susie"
            av = estimands.e1_summary(estimands.e1_paired_delta(rows, "A1_allvars", ref, k, rule, ids)["all_rows"],
                                      estimands.load_rules(REPO_ROOT))["median_delta"]
            mt = estimands.e1_summary(estimands.e1_paired_delta(rows, "A1_matched", ref, k, rule, ids)["all_rows"],
                                      estimands.load_rules(REPO_ROOT))["median_delta"]
            assert av != mt
            s = t[(t.ancestry == anc) & (t.p12_key == k) & (t.estimand == "E1") & (t.subset == "all_rows")
                  & (t.metric == "median_delta")]
            assert s.value.tolist() == [av], (anc, k, s.value.tolist(), av, mt)


def test_row_drops_has_the_a1_allvars_family(agg):
    man, root = agg
    rd = _read(root / "out", "row_drops")
    f = rd[rd.family == "a1_allvars"]
    assert set(f.contrast) == {"A1_allvars_vs_A3_1kg", "A1_allvars_vs_AFR661_A3"}
    assert set(f.variant_set) == {"allvars"} and set(f.p12_key) == set(P12) and set(f.side) == {"x", "ref"}
    assert len(f) == 2 * 2 * 2
    for anc, ref in REF.items():
        s = f[f.contrast == f"A1_allvars_vs_{ref}"]
        assert set(s.n_expected) == {len(_ids(man, anc))} and set(s.n_output) == {len(_ids(man, anc))}
        assert s.loc[s.side == "x", "label"].tolist() == ["A1_allvars"] * 2
        assert set(s.loc[s.side == "x", "n_a1"]) == {len(_ids(man, anc))}


def test_confirmatory_tables_unchanged(agg, tmp_path):
    """The four confirmatory tables are byte-equal to those run_aggregation.py at PRE_157D_REF writes."""
    _, root = agg
    src = subprocess.run(["git", "show", f"{PRE_157D_REF}:src/python/ta_r4/run_aggregation.py"], cwd=REPO_ROOT,
                         capture_output=True, text=True, check=True).stdout
    old_py = tmp_path / "run_aggregation_pre_157d.py"
    old_py.write_text(src)
    spec = importlib.util.spec_from_file_location("ta_r4_run_aggregation_pre_157d", old_py)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    assert "a1_allvars_secondary" not in old.TABLES
    # 15.8d made fit_cs_filtered a required E7 argument; the pre-157d script does not pass it (Carter Q-158DFX)
    filtered = pd.read_csv(REPO_ROOT / ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/"
                           "fit_cs_json_vs_rds.tsv", sep="\t", dtype=str, keep_default_na=False)
    est = types.ModuleType("estimands_pre_157d_proxy")
    est.__dict__.update(vars(old.estimands))
    e7 = old.estimands.e7_frozen_vs_fixed
    est.e7_frozen_vs_fixed = lambda *a, **k: e7(*a, fit_cs_filtered=filtered, **k)
    old.estimands = est
    assert old.run_aggregation(root / "repo", tmp_path / "old", draft=True) == 0
    for name in CONFIRMATORY:
        a = (tmp_path / "old" / f"{name}.tsv").read_bytes()
        b = (root / "out" / f"{name}.tsv").read_bytes()
        assert len(a.splitlines()) > 3, name
        assert a == b, name
