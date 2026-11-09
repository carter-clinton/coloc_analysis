"""The confirmatory estimator refuses an incomplete row set; FINAL aggregation requires full coloc coverage (W3f N6)."""
from __future__ import annotations

import itertools
from pathlib import Path

import pytest
import yaml

from .conftest import REPO_ROOT
from .fixtures.estimand_fixtures import doc, manifest, mrow
from .test_run_aggregation import TABLES, _run, build_tree, final_repo

RULES = yaml.safe_load((REPO_ROOT / "config/ta_r4/decision_rules.yaml").read_text())
PAIRS10 = list(itertools.combinations(("asthma", "bmi", "hypertension", "stroke", "t2d"), 2))


def _man100():
    return manifest([mrow(f"REG{i:02d}", "EUR", p) for i in range(10) for p in PAIRS10])


def _docs(row_ids, x=0.9, ref=0.7):
    out = []
    for rid in row_ids:
        out += [doc(rid, "A2_identity", "p12_primary", x), doc(rid, "A3_1kg", "p12_primary", ref)]
    return out


def _stats(docs, man, x="A2_identity"):
    from ta_r4.estimands import build_rows, contrast_stats

    return contrast_stats(build_rows(docs, man), x, "A3_1kg", RULES, man)


# ------------------------------------------------------------------ estimator-level completeness

def test_counterexample_a_ten_rows_of_one_region_refused():
    """Codex N6: 10 rows of one region (n_both 10, CI [0.2, 0.2], McNemar p 0.001953125) out of 100 expected."""
    from ta_r4.estimands import ConfirmatoryIncomplete

    man = _man100()
    ten = man.row_id[man.region_safe == "REG00"].tolist()
    assert len(man) == 100 and len(ten) == 10
    with pytest.raises(ConfirmatoryIncomplete, match=r"A2_identity_vs_A3_1kg.*A2_identity: 90 of 100 missing"):
        _stats(_docs(ten), man)


def test_cherry_picked_rows_over_ten_regions_refused():
    """One X-favouring row per region passes the region floor; only completeness stops it."""
    from ta_r4.estimands import ConfirmatoryIncomplete

    man = _man100()
    picked = man.drop_duplicates("region_safe").row_id.tolist()
    assert len(picked) == 10
    with pytest.raises(ConfirmatoryIncomplete):
        _stats(_docs(picked), man)


def test_counterexample_b_ten_row_manifest_is_non_informative():
    from ta_r4.branch_classifier import classify

    man = _man100()
    man = man[man.region_safe == "REG00"].reset_index(drop=True)
    s = _stats(_docs(man.row_id), man)
    assert (s["n_both"], s["n_regions"], s["mcnemar_p"]) == (10, 1, 0.001953125)
    assert s["ci_lo"] == pytest.approx(0.2) and s["ci_hi"] == pytest.approx(0.2)
    assert classify(s, RULES) == ("NON_INFORMATIVE", "rule1_n_both")


def test_missing_ref_side_named():
    from ta_r4.estimands import ConfirmatoryIncomplete

    man = _man100()
    docs = [d for d in _docs(man.row_id) if not (d["arm"] == "A3_1kg" and d["row_id"] == "REG03__EUR__bmi_vs_t2d")]
    with pytest.raises(ConfirmatoryIncomplete, match=r"A3_1kg: 1 of 100 missing \['REG03__EUR__bmi_vs_t2d'\]"):
        _stats(docs, man)


def test_wrong_p12_key_does_not_count():
    from ta_r4.estimands import ConfirmatoryIncomplete

    man = _man100()
    docs = _docs(man.row_id)
    docs[0]["p12_key"] = "p12_sensitivity"
    with pytest.raises(ConfirmatoryIncomplete):
        _stats(docs, man)


def test_a1_needs_the_matched_varset():
    from ta_r4.estimands import ConfirmatoryIncomplete

    man = _man100()
    docs = [doc(r, "A3_1kg", "p12_primary", 0.5) for r in man.row_id]
    docs += [doc(r, "A1_allvars", "p12_primary", 0.5) for r in man.row_id]
    docs += [doc(r, "A1_matched", "p12_primary", 0.5) for r in man.row_id[1:]]
    with pytest.raises(ConfirmatoryIncomplete, match="A1_matched: 1 of 100 missing"):
        _stats(docs, man, x="A1_matched")
    docs.append(doc(man.row_id[0], "A1_matched", "p12_primary", 0.5))
    assert _stats(docs, man, x="A1_matched")["n_rows"] == 100


def test_method_none_counts_as_present():
    man = _man100()
    docs = _docs(man.row_id)
    docs[0]["method"] = "none"
    s = _stats(docs, man)
    assert s["n_rows"] == 99 and s["n_both"] == 99


# ------------------------------------------------------------------ coverage-gated FINAL aggregation

def _coloc(repo, arm, name):
    return Path(repo) / f"data/r4/results/{arm}/coloc/{name}"


@pytest.mark.parametrize("change", ["missing", "extra"])
def test_final_refuses_incomplete_coverage(tmp_path, capsys, change):
    repo = final_repo(tmp_path)
    rid = "CUR1__EUR__bmi_vs_stroke"
    if change == "missing":
        _coloc(repo, "A3_ukb", f"{rid}.p12_sensitivity.json").unlink()
    else:
        _coloc(repo, "A3_1kg", f"{rid}.p12_bogus.json").write_text("{}")
    out = tmp_path / "out"
    assert _run(repo, out) == 3
    assert not out.exists() or not list(out.glob("*.tsv"))
    err = capsys.readouterr().err
    want = (f"EUR missing=1 extra=0" if change == "missing" else f"EUR missing=0 extra=1")
    assert want in err and "AFR missing=0 extra=0" in err
    assert rid in err


def test_final_complete_coverage_writes_final(tmp_path):
    repo = final_repo(tmp_path)
    out = tmp_path / "out"
    assert _run(repo, out) == 0
    assert all((out / f"{t}.tsv").read_text().startswith("# status=FINAL\n") for t in TABLES)


def test_draft_reports_coverage_in_every_table(tmp_path, capsys):
    repo = tmp_path / "repo"
    build_tree(repo)
    _coloc(repo, "A3_ukb_isect", "NC_ABO__EUR__asthma_vs_bmi.p12_primary.json").unlink()
    out = tmp_path / "out"
    assert _run(repo, out, draft=True) == 0
    line = "# coverage=EUR missing=1 extra=0; AFR missing=0 extra=0"
    for t in TABLES:
        head = (out / f"{t}.tsv").read_text().splitlines()[:2]
        assert head == ["# status=DRAFT", line], t
    assert "EUR missing=1 extra=0" in capsys.readouterr().err
