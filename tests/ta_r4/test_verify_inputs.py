"""Runtime sha256 verification of R4 inputs against the committed manifests (W3f 15.2, review N4)."""
from __future__ import annotations

import csv
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from ta_r4 import commands, paths
from ta_r4 import run_qtl_group_r4 as G
from ta_r4 import verify_inputs as V
from ta_r4.harmonize_qtl_r4 import harmonized_path

from .conftest import REPO_ROOT


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _manifest(path, rows, key="path"):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow([key, "sha256", "role"])
        for rel, sha in rows:
            w.writerow([rel, sha, "input"])
    return path


@pytest.fixture
def tree(tmp_path):
    """Two inputs at repo-relative paths, one listed per manifest (path / rel_path columns)."""
    a = tmp_path / "data/processed/sumstats_harmonized/tA.EUR.tsv.bgz"
    b = tmp_path / "data/r4/ld/variants_r4/R1.tsv"
    for p, text in ((a, "sumstats\n"), (b, "catalog\n")):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    m1 = _manifest(tmp_path / "m/sumstats.tsv", [(str(a.relative_to(tmp_path)), _sha(a))])
    m2 = _manifest(tmp_path / "m/catalogs.tsv", [(str(b.relative_to(tmp_path)), _sha(b))], key="rel_path")
    return tmp_path, [str(a.relative_to(tmp_path)), str(b.relative_to(tmp_path))], ["m/sumstats.tsv", "m/catalogs.tsv"]


def _cli(repo, manifests, files):
    argv = [sys.executable, "-m", "ta_r4.verify_inputs"]
    for m in manifests:
        argv += ["--manifest", m]
    for f in files:
        argv += ["--file", f]
    return subprocess.run(argv, cwd=repo, capture_output=True, text=True,
                          env={"PYTHONPATH": str(REPO_ROOT / "src/python"), "PATH": "/usr/bin:/bin"})


def test_correct_files_pass(tree):
    repo, files, mans = tree
    assert V.verify(files, mans, repo) is None
    p = _cli(repo, mans, files)
    assert p.returncode == 0, p.stderr


def test_one_byte_change_fails_naming_the_file(tree):
    repo, files, mans = tree
    want = _sha(repo / files[1])
    (repo / files[1]).write_text("catalOg\n")
    with pytest.raises(V.InputIntegrityError) as ei:
        V.verify(files, mans, repo)
    msg = str(ei.value)
    assert files[1] in msg and want in msg and _sha(repo / files[1]) in msg and files[0] not in msg
    p = _cli(repo, mans, files)
    assert p.returncode == 1 and files[1] in p.stderr and "InputIntegrityError" in p.stderr


def test_unlisted_file_fails(tree):
    repo, files, mans = tree
    extra = repo / "data/processed/sumstats_harmonized/tB.EUR.tsv.bgz"
    extra.write_text("unlisted\n")
    rel = str(extra.relative_to(repo))
    with pytest.raises(V.InputIntegrityError, match="not in manifest"):
        V.verify(files + [rel], mans, repo)
    p = _cli(repo, mans, files + [rel])
    assert p.returncode == 1 and rel in p.stderr and "not in manifest" in p.stderr


def test_file_listed_only_in_a_manifest_not_passed_fails(tree):
    repo, files, mans = tree
    p = _cli(repo, mans[:1], files)
    assert p.returncode == 1 and files[1] in p.stderr and "not in manifest" in p.stderr


def test_every_failing_file_is_reported(tree):
    repo, files, mans = tree
    for f in files:
        (repo / f).write_text("tampered\n")
    with pytest.raises(V.InputIntegrityError) as ei:
        V.verify(files, mans, repo)
    assert all(f in str(ei.value) for f in files)


def test_absent_file_fails(tree):
    repo, files, mans = tree
    (repo / files[0]).unlink()
    p = _cli(repo, mans, files)
    assert p.returncode == 1 and files[0] in p.stderr


def test_absent_manifest_fails(tree):
    repo, files, mans = tree
    p = _cli(repo, ["m/none.tsv"], files)
    assert p.returncode == 1 and "m/none.tsv" in p.stderr


def test_no_files_is_an_error(tree):
    repo, _, mans = tree
    with pytest.raises(V.InputIntegrityError):
        V.verify([], mans, repo)


def test_conflicting_records_fail(tree):
    repo, files, mans = tree
    _manifest(repo / "m/other.tsv", [(files[0], "0" * 64)])
    with pytest.raises(V.InputIntegrityError, match="conflicting"):
        V.verify(files, mans + ["m/other.tsv"], repo)


# ---- command builders --------------------------------------------------------------------------------------------

def test_verify_command_production_fit():
    cmd = commands.verify_command("A3_1kg", "bmi", "EUR", "SH2B3_12q24")
    assert cmd[:4] == commands._PY and cmd[4] == "ta_r4.verify_inputs"
    assert [cmd[i + 1] for i, x in enumerate(cmd) if x == "--manifest"] == [V.SUMSTATS, V.CATALOGS]
    assert [cmd[i + 1] for i, x in enumerate(cmd) if x == "--file"] == [
        paths.sumstats_path("bmi", "EUR", "A3_1kg"), paths.catalog_path("r4", "SH2B3_12q24")]


def test_coloc_verify_command_checks_both_sumstats():
    row = {"row_id": "SH2B3_12q24__EUR__bmi_vs_stroke", "ancestry": "EUR", "region_id": "SH2B3_12q24",
           "region_safe": "SH2B3_12q24", "trait_a": "bmi", "trait_b": "stroke"}
    for arm, mode in (("A3_1kg", "susie"), ("A3_1kg", "A1_matched"), ("A3_1kg", "A1_allvars"), ("A2_identity", "susie")):
        cmd = commands.coloc_verify_command(arm, row, mode)
        assert cmd[:5] == commands._PY + ["ta_r4.verify_inputs"]
        assert [cmd[i + 1] for i, x in enumerate(cmd) if x == "--file"] == [
            paths.sumstats_path("bmi", "EUR", arm), paths.sumstats_path("stroke", "EUR", arm)]
    with pytest.raises(ValueError):
        commands.coloc_verify_command("A3_1kg", row, "qtl_abf")


@pytest.mark.parametrize("arm", ["repro_routeC", "repro_routeL", "repro_k2d_routeC", "repro_sh2b3_r2"])
def test_repro_arms_are_not_verified(arm):
    """Repro catalogs for the 19 NC regions are not in catalogs_sha256.tsv (measured 2026-11-09); repro is not gated."""
    assert commands.verify_command(arm, "asthma", "EUR", "SH2B3_12q24") == ["true"]


def test_production_commands_run_and_fail_on_tamper(tmp_path):
    """The rendered argv, run from a tree with the R4 relative layout: exit 0, then exit 1 after a one-byte change."""
    cmd = commands.verify_command("A3_1kg", "asthma", "EUR", "R1")
    files = [cmd[i + 1] for i, x in enumerate(cmd) if x == "--file"]
    for f in files:
        (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / f).write_text(f"{f}\n")
    _manifest(tmp_path / V.SUMSTATS, [(files[0], _sha(tmp_path / files[0]))])
    _manifest(tmp_path / V.CATALOGS, [(files[1], _sha(tmp_path / files[1]))], key="rel_path")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/python").symlink_to(REPO_ROOT / "src/python")
    assert subprocess.run(cmd, cwd=tmp_path, capture_output=True).returncode == 0
    (tmp_path / files[0]).write_text("x\n")
    p = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True)
    assert p.returncode == 1 and files[0] in p.stderr


# ---- run_qtl_group_r4 verifies before any row --------------------------------------------------------------------

REGION, QTD, FEATS, TRAITS = "R1", "QTD999999", ("ENSG00000000101", "ENSG00000000102"), ("tA", "tB")


def _qtl_tree(root):
    """A one-group QTL tree (cwd-relative R4 layout) whose inputs are listed in the default manifests."""
    from .fixtures.qtl_group_fixture import MCOLS
    rows = [[f"{REGION}__EUR__{t}__eqtl__Whole_Blood__{f}", REGION, "EUR", t, "eqtl", "Whole_Blood", QTD, f, f,
             "12", 1, 2, 3] for t in TRAITS for f in FEATS]
    with open(root / "qtl_manifest.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(MCOLS)
        w.writerows(rows)
    files = [harmonized_path("eqtl", QTD, f, REGION) for f in FEATS] + \
            [paths.sumstats_path(t, "EUR", "A3_1kg") for t in TRAITS] + [paths.catalog_path("r4", REGION)]
    for f in files:
        (root / f).parent.mkdir(parents=True, exist_ok=True)
        (root / f).write_text(f"{f}\n")
    _manifest(root / V.QTL_HARMONIZED, [(f, _sha(root / f)) for f in files[:2]], key="rel_path")
    _manifest(root / V.SUMSTATS, [(f, _sha(root / f)) for f in files[2:4]])
    _manifest(root / V.CATALOGS, [(files[4], _sha(root / files[4]))], key="rel_path")
    for rel in (commands.COLOC_PRIORS, G.QTL_SOURCES):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel, root / rel)
    (root / paths.regions_csv()).write_text(f"region_id,ancestry,chr,start,end\n{REGION},EUR,12,1,2\n")
    return files


class _Ran(Exception):
    pass


def _stub_run(*a, **k):
    raise _Ran(a[0])


def test_qtl_group_runs_rows_when_inputs_verify(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _qtl_tree(tmp_path)
    with pytest.raises(_Ran):
        G.run_group("QTL_A3", REGION, "eqtl", QTD, manifest="qtl_manifest.tsv", run=_stub_run)


@pytest.mark.parametrize("victim", [0, 2, 4], ids=["harmonized", "sumstats", "catalog"])
def test_qtl_group_tampered_input_fails_before_any_row(tmp_path, monkeypatch, victim):
    monkeypatch.chdir(tmp_path)
    files = _qtl_tree(tmp_path)
    (tmp_path / files[victim]).write_text("tampered\n")
    with pytest.raises(V.InputIntegrityError) as ei:
        G.run_group("QTL_A3", REGION, "eqtl", QTD, manifest="qtl_manifest.tsv", run=_stub_run)
    assert files[victim] in str(ei.value)
    assert not list(tmp_path.rglob("*.json"))


def test_qtl_group_cli_exit_1_without_done(tmp_path):
    files = _qtl_tree(tmp_path)
    (tmp_path / files[0]).write_text("tampered\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/python").symlink_to(REPO_ROOT / "src/python")
    p = subprocess.run([sys.executable, "-m", "ta_r4.run_qtl_group_r4", "--qtl-arm", "QTL_A3", "--region", REGION,
                        "--source", "eqtl", "--qtd", QTD, "--manifest", "qtl_manifest.tsv", "--done", "g.done"],
                       cwd=tmp_path, capture_output=True, text=True, env={"PYTHONPATH": "src/python", "PATH": "/usr/bin:/bin"})
    assert p.returncode == 1 and "InputIntegrityError" in p.stderr and files[0] in p.stderr, p.stderr[-2000:]
    assert not (tmp_path / "g.done").exists()


# ---- heavy: a real production input against its committed record ------------------------------------------------

@pytest.mark.r4_heavy
def test_real_asthma_eur_sumstats_verifies():
    rel = paths.sumstats_path("asthma", "EUR", "A3_1kg")
    assert V.verify([rel], [V.SUMSTATS], REPO_ROOT) is None
    with open(REPO_ROOT / V.SUMSTATS, newline="") as fh:
        rec = {r["path"]: r["sha256"] for r in csv.DictReader(fh, delimiter="\t")}
    assert rec[rel] == V.sha256_file(REPO_ROOT / rel)
