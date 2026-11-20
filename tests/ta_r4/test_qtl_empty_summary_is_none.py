"""W3f 15.7b (F7): a run_qtl_coloc.R success whose coloc.susie summary is empty or has no finite PP.H4.abf is written
with method none and the GWAS pair none reason (coloc_susie_empty / coloc_susie_no_finite_h4), is not tierable, and
its reason reaches the aggregate's none_status. run_qtl_coloc.R and aggregate_qtl_coloc.py are not changed."""
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

import pytest

from .conftest import REPO_ROOT
from .test_qtl_group_runner import _row

from ta_r4 import run_qtl_group_r4 as G

PY = "/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11"
AGG = REPO_ROOT / "src/python/aggregate_qtl_coloc.py"
FINITE = {"PP.H0.abf": 0.01, "PP.H1.abf": 0.02, "PP.H2.abf": 0.03, "PP.H3.abf": 0.04, "PP.H4.abf": 0.9,
          "hit1": "1:1", "hit2": "1:2"}
SUMMARIES = {"empty_list": ([], "coloc_susie_empty"), "empty_dict": ({}, "coloc_susie_empty"),
             "null_h4": ({**FINITE, "PP.H4.abf": None}, "coloc_susie_no_finite_h4"),
             "nan_h4": ({**FINITE, "PP.H4.abf": float("nan")}, "coloc_susie_no_finite_h4")}


def _fake(summary):
    """subprocess.run stand-in: run_qtl_coloc.R status success with both sides' credible sets and `summary`."""
    def run(argv, **kw):
        out = argv[argv.index("--output") + 1]
        Path(out).write_text(json.dumps({"status": "success", "n_cs_gwas": 2, "n_cs_qtl": 1, "n_snps_overlap": 300,
                                         "qtl_source": "gtex_eqtl", "summary": summary}))
        return subprocess.CompletedProcess(argv, 0, "", "")
    return run


def _doc(tmp_path, summary, trait="tA"):
    odir, tdir = tmp_path / "qtl", tmp_path / "tmp"
    odir.mkdir(exist_ok=True)
    tdir.mkdir(exist_ok=True)
    row = _row(trait=trait)
    m = G.run_row("QTL_A3", row, "FIX.1", odir, tdir, {"p12_key": G.P12_KEY}, 1.0, run=_fake(summary))
    return m, json.loads((odir / f"{row['qtl_row_id']}.json").read_text()), odir


@pytest.mark.parametrize("case", list(SUMMARIES))
def test_success_with_empty_summary_is_method_none(tmp_path, case):
    summary, reason = SUMMARIES[case]
    m, d, _ = _doc(tmp_path, summary)
    assert m == "none"
    assert (d["method"], d["status"], d["qtl_r_status"], d["fallback_reason"]) == ("none", reason, "success", None)
    assert d["pp_h4"] is None or d["pp_h4"] != d["pp_h4"]  # no posterior


def test_success_with_finite_summary_stays_coloc_susie(tmp_path):
    m, d, _ = _doc(tmp_path, FINITE)
    assert m == "coloc_susie"
    assert (d["method"], d["status"], d["fallback_reason"]) == ("coloc_susie", "success", None)
    assert d["pp_h4"] == 0.9 and "qtl_r_status" not in d


def _aggregate(odir, out):
    p = subprocess.run([PY, "-B", str(AGG), "--json-dir", str(odir), "--manifest", str(out) + ".absent", "--output",
                        str(out), "--with-method-columns"], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    with open(out) as fh:
        return {r["qtl_coloc_id"]: r for r in csv.DictReader(fh, delimiter="\t")}


def test_none_row_is_not_tierable(tmp_path):
    _, _, odir = _doc(tmp_path, [])
    _doc(tmp_path, FINITE, trait="tB")
    rows = _aggregate(odir, tmp_path / "summary.tsv")
    assert sorted(r["method"] for r in rows.values()) == ["coloc_susie", "none"]
    kept, total = G.tierable_summary(tmp_path / "summary.tsv", tmp_path / "tierable.tsv")
    assert (kept, total) == (1, 2)
    with open(tmp_path / "tierable.tsv") as fh:
        assert [r["method"] for r in csv.DictReader(fh, delimiter="\t")] == ["coloc_susie"]


def test_aggregate_exports_the_none_reason(tmp_path):
    from ta_r4.estimands import NONE_REASONS

    want = {}
    for trait, case in (("tA", "empty_list"), ("tB", "null_h4")):
        summary, reason = SUMMARIES[case]
        _, d, odir = _doc(tmp_path, summary, trait=trait)
        want[d["qtl_row_id"]] = reason
        assert reason in NONE_REASONS
    rows = _aggregate(odir, tmp_path / "summary.tsv")
    assert {k: (r["method"], r["none_status"]) for k, r in rows.items()} == {k: ("none", v) for k, v in want.items()}
