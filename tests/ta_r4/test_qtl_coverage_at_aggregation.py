"""W3f 15.7b (F6): QTL rows are reconciled against config/ta_r4/qtl_manifest.tsv by id at aggregation (FINAL exit 3,
DRAFT prints) and in the r4_qtl_aggregate job (--tierable-summary with an explicit --manifest)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from .conftest import REPO_ROOT
from .test_run_aggregation import PY, QTL_ARMS, QTL_SUMMARY_HEAD, _read, _run, final_repo

IDS = ("CUR0__x__eqtl__QTD1__G1", "CUR1__x__sqtl__QTD3__J1")
STALE = "CUR2__x__eqtl__QTD9__STALE"


def _summary(repo, arm):
    return Path(repo) / f"data/r4/results/{arm}/qtl_coloc_summary.tsv"


def _edit(p, fn):
    lines = p.read_text().splitlines()
    p.write_text("\n".join(fn(lines)) + "\n")


def _refused(repo, out, capsys):
    capsys.readouterr()
    assert _run(repo, out) == 3
    assert not out.exists() or not any(out.iterdir())
    return capsys.readouterr().err


def test_qtl_summary_matching_manifest_passes(tmp_path):
    repo = final_repo(tmp_path)
    out = tmp_path / "out"
    assert _run(repo, out) == 0
    q = _read(out, "qtl_rows")
    for arm in QTL_ARMS:
        assert sorted(q.qtl_coloc_id[q.qtl_arm == arm]) == sorted(IDS), arm


def _blank_method(lines):
    head = lines[0].split("\t")
    f = lines[1].split("\t")
    f[head.index("method")] = ""
    return [lines[0], "\t".join(f), *lines[2:]]


CASES = {
    "missing_row": (lambda ls: ls[:2], IDS[1], "missing"),
    "extra_row": (lambda ls: ls + [ls[1].replace(IDS[0], STALE)], STALE, "extra"),
    "duplicate_row": (lambda ls: ls[:2] + ls[1:], IDS[0], "duplicated"),
    "empty_method": (_blank_method, IDS[0], "empty method"),
}


@pytest.mark.parametrize("case", list(CASES))
def test_qtl_coverage_flags(tmp_path, capsys, case):
    fn, rid, kind = CASES[case]
    repo = final_repo(tmp_path)
    _edit(_summary(repo, "QTL_A2"), fn)
    err = _refused(repo, tmp_path / "out", capsys)
    print(err)
    hit = [ln for ln in err.splitlines() if "QTL_A2" in ln and kind in ln]
    assert hit and rid in hit[0], err


def test_final_refuses_on_a_qtl_coverage_gap(tmp_path, capsys):
    repo = final_repo(tmp_path)
    _edit(_summary(repo, "QTL_legacy"), lambda ls: ls[:2])
    out = tmp_path / "out"
    err = _refused(repo, out, capsys)
    assert "QTL_legacy" in err and IDS[1] in err and "FINAL refused" in err
    assert _run(repo, out, draft=True) == 0
    err = capsys.readouterr().err
    assert "QTL_legacy" in err and IDS[1] in err and "FINAL refused" not in err
    q = _read(out, "qtl_rows")
    assert list(q.qtl_coloc_id[q.qtl_arm == "QTL_legacy"]) == [IDS[0]]


def _tierable(src, out, manifest):
    return subprocess.run([PY, "-B", "-m", "ta_r4.run_qtl_group_r4", "--qtl-arm", "QTL_A3", "--tierable-summary",
                           str(src), "--out", str(out), "--manifest", str(manifest)], capture_output=True, text=True,
                          cwd=REPO_ROOT / "src/python")


def test_tierable_step_refuses_an_incomplete_summary(tmp_path):
    src = tmp_path / "summary.tsv"
    src.write_text(QTL_SUMMARY_HEAD
                   + f"{IDS[0]}\tgtex_eqtl\tLung\tG1\tCUR0\tEUR\t300\t500\t1\t1\t2\tsuccess\t0\t0.01\t0.04\t0.05\t0.9"
                     "\t1:1\t1:2\tcoloc_susie\t\t\t0\t0.01\t0.04\t0.05\t0.9\n")
    man = tmp_path / "qtl_manifest.tsv"
    out = tmp_path / "tierable.tsv"
    for ids, rid in (((IDS[0], IDS[1]), IDS[1]), ((IDS[1],), IDS[0])):  # a missing row, then an extra one
        pd.DataFrame({"qtl_row_id": ids}).to_csv(man, sep="\t", index=False)
        p = _tierable(src, out, man)
        assert p.returncode == 1, p.stdout + p.stderr
        assert rid in p.stderr and not out.exists() and not Path(f"{out}.tmp").exists()
    pd.DataFrame({"qtl_row_id": [IDS[0]]}).to_csv(man, sep="\t", index=False)
    p = _tierable(src, out, man)
    assert p.returncode == 0, p.stderr
    assert out.read_text() == src.read_text()


def test_a3_json_docs_reconciled(tmp_path, capsys):
    repo = final_repo(tmp_path)
    jdir = repo / "data/r4/results/QTL_A3/qtl"
    stale = jdir / f"{STALE}.json"
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_text('{"method": "coloc_susie"}')
    err = _refused(repo, tmp_path / "out", capsys)
    assert any("QTL_A3" in ln and "JSON" in ln and STALE in ln for ln in err.splitlines()), err
    stale.unlink()
    (jdir / f"{IDS[1]}.json").unlink()
    err = _refused(repo, tmp_path / "out", capsys)
    assert any("QTL_A3" in ln and "JSON" in ln and IDS[1] in ln for ln in err.splitlines()), err
