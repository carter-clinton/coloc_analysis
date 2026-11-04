"""Coloc coverage: observed output paths == expected (admissible row x production arm x p12 key, + A1) (W3d; B2)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from .conftest import REPO_ROOT
from .fixtures.estimand_fixtures import manifest, mrow

PY = "/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11"
P12 = ("p12_primary", "p12_sensitivity")


def _real_manifest():
    from ta_r4.estimands import load_manifest

    return load_manifest(REPO_ROOT)


def test_expected_totals_from_the_committed_manifest_and_arms():
    from ta_r4.arms import production_arms
    from ta_r4.coloc_coverage import expected_ids

    m = _real_manifest()
    n_eur = int(((m.ancestry == "EUR") & (m.admissible == "true")).sum())
    n_afr = int(((m.ancestry == "AFR") & (m.admissible == "true")).sum())
    assert (n_eur, n_afr) == (290, 30)
    assert (len(production_arms("EUR")), len(production_arms("AFR"))) == (5, 3)
    eur, afr = expected_ids(m, "EUR"), expected_ids(m, "AFR")
    assert len(eur) == 290 * 2 * 7 == 4060
    assert len(afr) == 30 * 2 * 5 == 300
    assert not eur & afr
    assert all("/A1_EUR/" in p or p.split("/")[3] in production_arms("EUR") for p in eur)
    assert not any("repro" in p for p in eur | afr)


def test_expected_paths_use_the_coloc_path_helpers():
    from ta_r4 import paths
    from ta_r4.coloc_coverage import expected_ids

    m = _real_manifest()
    rid = m.row_id[(m.ancestry == "AFR") & (m.admissible == "true")].iloc[0]
    afr = expected_ids(m, "AFR")
    assert paths.coloc_json("AFR661_A2", rid, "p12_sensitivity") in afr
    assert paths.coloc_json("A1_AFR", rid, "p12_primary", "allvars") in afr
    inad = m.row_id[m.admissible != "true"].iloc[0]
    assert not any(f"/{inad}." in p for p in expected_ids(m, "EUR") | afr)


def _fixture(tmp_path):
    from ta_r4.coloc_coverage import expected_ids

    m = manifest([mrow("R1", "EUR", p) for p in (("asthma", "bmi"), ("asthma", "t2d"), ("bmi", "t2d"))]
                 + [mrow("R2", "EUR", ("asthma", "bmi"), admissible="false")])
    exp = expected_ids(m, "EUR", arms=("A3_1kg", "A2_identity"), a1_varsets=())
    for p in exp:
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("{}")
    return m, exp


def test_fixture_complete(tmp_path):
    from ta_r4.coloc_coverage import check

    _, exp = _fixture(tmp_path)
    assert len(exp) == 12
    assert check(exp, tmp_path) == (set(), set())


def test_fixture_missing_extra_and_repro_ignored(tmp_path):
    from ta_r4.coloc_coverage import check

    _, exp = _fixture(tmp_path)
    gone = sorted(exp)[3]
    (tmp_path / gone).unlink()
    stray = "data/r4/results/A3_1kg/coloc/R9__EUR__x_vs_y.p12_primary.json"
    (tmp_path / stray).write_text("{}")
    repro = tmp_path / "data/r4/results/repro_sh2b3_r2/coloc/R1__EUR__asthma_vs_bmi.p12_primary.json"
    repro.parent.mkdir(parents=True)
    repro.write_text("{}")
    (tmp_path / "data/r4/results/A2_identity/coloc/R1__EUR__asthma_vs_bmi.p12_primary.json.tmp").write_text("")
    missing, extra = check(exp, tmp_path)
    assert missing == {gone}
    assert extra == {stray}


def _cli(repo, anc, manifest_path):
    return subprocess.run([PY, "-B", "-m", "ta_r4.coloc_coverage", "--ancestry", anc, "--repo", str(repo),
                           "--manifest", str(manifest_path)], capture_output=True, text=True,
                          cwd=REPO_ROOT / "src/python")


def test_cli_real_repo_reports_expected_and_exits_1():
    p = _cli(REPO_ROOT, "EUR", REPO_ROOT / "config/ta_r4/pair_manifest.tsv")
    assert p.returncode == 1
    assert p.stdout.strip() == "missing=4060 extra=0 expected=4060"
    p = _cli(REPO_ROOT, "AFR", REPO_ROOT / "config/ta_r4/pair_manifest.tsv")
    assert p.stdout.strip() == "missing=300 extra=0 expected=300"


def test_cli_complete_tree_exits_0_and_one_missing_exits_1(tmp_path):
    from ta_r4.coloc_coverage import expected_ids

    m = manifest([mrow("R1", "AFR", p) for p in (("asthma", "bmi"), ("bmi", "t2d"))])
    mp = tmp_path / "pair_manifest.tsv"
    m.to_csv(mp, sep="\t", index=False)
    exp = expected_ids(m, "AFR")
    assert len(exp) == 2 * 2 * 5
    for p in exp:
        (tmp_path / p).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / p).write_text("{}")
    ok = _cli(tmp_path, "AFR", mp)
    assert (ok.returncode, ok.stdout.strip()) == (0, "missing=0 extra=0 expected=20")
    (tmp_path / sorted(exp)[0]).unlink()
    bad = _cli(tmp_path, "AFR", mp)
    assert (bad.returncode, bad.stdout.strip()) == (1, "missing=1 extra=0 expected=20")
    assert Path(sorted(exp)[0]).name in bad.stderr
