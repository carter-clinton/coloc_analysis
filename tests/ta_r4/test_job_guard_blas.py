"""W3f 15.8b (review R6; Carter Q-157J, Q-158R6S, Q-158R6G A): envs/r_coloc.yml pins libopenblas with an exact pin
file; with --blas-pinned (gated rules whose conda env is envs/r_coloc.yml) the job guard refuses any other BLAS, and
without it the guard reads no BLAS and records that the BLAS was not checked."""
from __future__ import annotations

import csv
import filecmp
import hashlib
import json
import os
import shutil
import subprocess
import types
from pathlib import Path

import pytest

from ta_r4 import commands, job_guard, r4_lock_gate
from ta_r4.conda_job_env import R4_CONDA_PREFIX, job_env_dir

from .conftest import MAN_DIR, REPO_ROOT
from .test_job_guard import ARM, CASCADELAKE, CLEAN_ENV, LABEL, blas_prefix, blas_stubs

CONDA = "/rs1/researchers/c/ckclinto/miniconda3/condabin/conda"
NAMED_ENV = Path("/rs1/researchers/c/ckclinto/conda_envs/r_coloc")
YML = REPO_ROOT / "envs/r_coloc.yml"
PIN_FILE = REPO_ROOT / "envs/r_coloc.linux-64.pin.txt"
LOCK_TSV = MAN_DIR / "env_lock_r_coloc_job.tsv"
_needs_rs1 = pytest.mark.skipif(not Path(R4_CONDA_PREFIX).is_dir(), reason="/rs1 job-env prefix absent")


@pytest.fixture
def gate_passes(monkeypatch):
    monkeypatch.setattr(r4_lock_gate, "check_lock_gate", lambda repo, stage: None)


def _digest():
    return job_guard.config_digest(job_guard.merged_config_from_files(REPO_ROOT, ARM))


def _run(tmp_path, prefix, pin, *, probe=None, r_probe=None, environ=None, blas_pinned=True):
    sp, sr = blas_stubs(prefix, pin)
    env = dict(CLEAN_ENV if environ is None else environ)
    if prefix is not None and "CONDA_PREFIX" not in env:
        env["CONDA_PREFIX"] = str(prefix)
    return job_guard.check(REPO_ROOT, ARM, _digest(), environ=env, cpuinfo=CASCADELAKE, record_dir=tmp_path / "rec",
                           label=LABEL, blas_pinned=blas_pinned, blas_probe=probe or sp, r_blas_probe=r_probe or sr)


def _explicit_lines(text):
    """The URL#md5 package lines after @EXPLICIT (the `# created-by` and other header lines are not compared)."""
    lines = text.splitlines()
    i = lines.index("@EXPLICIT")
    return [ln for ln in lines[i + 1:] if ln.strip() and not ln.startswith("#")]


# ---- unit: the pin and each --blas-pinned refusal ------------------------------------------------------------------

def test_pin_is_read_from_r_coloc_yml(tmp_path):
    repo = tmp_path / "repo"
    (repo / "envs").mkdir(parents=True)
    body = "name: r_coloc\ndependencies:\n  - r-base=4.4.2\n"
    (repo / "envs/r_coloc.yml").write_text(body + "  - libopenblas=9.9.9\n")
    assert job_guard.libopenblas_pin(repo) == "9.9.9"
    (repo / "envs/r_coloc.yml").write_text(body)
    with pytest.raises(job_guard.JobGuardError, match="libopenblas"):
        job_guard.libopenblas_pin(repo)
    (repo / "envs/r_coloc.yml").write_text(body + "  - libopenblas=9.9.9\n  - libopenblas=9.9.8\n")
    with pytest.raises(job_guard.JobGuardError, match="libopenblas"):
        job_guard.libopenblas_pin(repo)


def test_guard_refuses_a_libopenblas_version_other_than_the_pin(tmp_path, gate_passes):
    pin = job_guard.libopenblas_pin(REPO_ROOT)
    prefix = blas_prefix(tmp_path / "pa", pin, meta_versions=["0.3.32"])
    with pytest.raises(job_guard.JobGuardError, match="conda-meta libopenblas version 0.3.32 != pin"):
        _run(tmp_path, prefix, pin)
    prefix = blas_prefix(tmp_path / "pb", pin, meta_versions=[])
    with pytest.raises(job_guard.JobGuardError, match=r"conda-meta has 0 libopenblas records \[\]"):
        _run(tmp_path, prefix, pin)
    prefix = blas_prefix(tmp_path / "pc", pin, meta_versions=[pin, "0.3.32"])
    with pytest.raises(job_guard.JobGuardError, match="conda-meta has 2 libopenblas records"):
        _run(tmp_path, prefix, pin)


def test_guard_refuses_blas_symlinks_not_to_the_pinned_openblas(tmp_path, gate_passes):
    pin = job_guard.libopenblas_pin(REPO_ROOT)
    other = tmp_path / "other_blas.so"
    other.write_text("x\n")
    prefix = blas_prefix(tmp_path / "pa", pin, libblas_to=str(other))
    with pytest.raises(job_guard.JobGuardError, match="lib/libblas.so.3 resolves to"):
        _run(tmp_path, prefix, pin)
    prefix = blas_prefix(tmp_path / "pb", pin, liblapack_to=str(other))
    with pytest.raises(job_guard.JobGuardError, match="lib/liblapack.so.3 resolves to"):
        _run(tmp_path, prefix, pin)


def test_guard_refuses_without_conda_prefix(tmp_path, gate_passes):
    pin = job_guard.libopenblas_pin(REPO_ROOT)
    prefix = blas_prefix(tmp_path / "p", pin)
    sp, sr = blas_stubs(prefix, pin)
    with pytest.raises(job_guard.JobGuardError, match="CONDA_PREFIX is unset"):
        job_guard.check(REPO_ROOT, ARM, _digest(), environ=dict(CLEAN_ENV), cpuinfo=CASCADELAKE,
                        record_dir=tmp_path / "rec", label=LABEL, blas_pinned=True, blas_probe=sp, r_blas_probe=sr)


def test_guard_refuses_a_runtime_config_of_another_version(tmp_path, gate_passes):
    pin = job_guard.libopenblas_pin(REPO_ROOT)
    prefix = blas_prefix(tmp_path / "p", pin)
    probe = lambda library: (f"OpenBLAS {pin}0 DYNAMIC_ARCH NO_AFFINITY SkylakeX MAX_THREADS=128", "SkylakeX")
    with pytest.raises(job_guard.JobGuardError, match="OpenBLAS runtime version"):
        _run(tmp_path, prefix, pin, probe=probe)


def test_guard_refuses_a_missing_or_other_r_blas(tmp_path, gate_passes):
    pin = job_guard.libopenblas_pin(REPO_ROOT)
    prefix = blas_prefix(tmp_path / "p1", pin, rscript=False)
    with pytest.raises(job_guard.JobGuardError, match="bin/Rscript is missing"):
        _run(tmp_path, prefix, pin)
    prefix = blas_prefix(tmp_path / "p2", pin)
    with pytest.raises(job_guard.JobGuardError, match="R reports BLAS"):
        _run(tmp_path, prefix, pin, r_probe=lambda rscript: str(tmp_path / "another_libblas.so"))


def test_guard_record_has_the_blas_block(tmp_path, gate_passes):
    pin = job_guard.libopenblas_pin(REPO_ROOT)
    prefix = blas_prefix(tmp_path / "p", pin)
    rec = _run(tmp_path, prefix, pin)
    so = os.path.realpath(prefix / "lib" / f"libopenblasp-r{pin}.so")
    assert rec["checked"]["blas_pinned"] is True
    b = rec["blas"]
    assert b["status"] == "pinned" and b["version"] == pin and b["library"] == so
    assert b["config"].split()[:2] == ["OpenBLAS", pin] and b["corename"] == "SkylakeX"
    assert os.path.realpath(b["r_blas"]) == so
    assert json.loads((tmp_path / "rec" / f"local.{LABEL}.json").read_text()) == rec


def test_unflagged_guard_records_not_checked_and_reads_no_blas(tmp_path, gate_passes, monkeypatch):
    other = tmp_path / "other_blas.so"
    other.write_text("x\n")
    prefix = blas_prefix(tmp_path / "p", "0.3.34", meta_versions=["0.3.32"], libblas_to=str(other), rscript=False)

    def boom(*a, **k):
        raise AssertionError("BLAS read without --blas-pinned")

    for name in ("blas_facts", "blas_violations", "libopenblas_pin"):
        monkeypatch.setattr(job_guard, name, boom)
    rec = job_guard.check(REPO_ROOT, ARM, _digest(), environ={**CLEAN_ENV, "CONDA_PREFIX": str(prefix)},
                          cpuinfo=CASCADELAKE, record_dir=tmp_path / "rec", label=LABEL, blas_pinned=False,
                          blas_probe=boom, r_blas_probe=boom)
    assert rec["checked"]["blas_pinned"] == "not_checked"
    assert rec["blas"] == {"status": "not_checked", "reason": job_guard.BLAS_NOT_CHECKED_REASON}
    assert job_guard.BLAS_NOT_CHECKED_REASON and "Q-158R6G" in job_guard.BLAS_NOT_CHECKED_REASON
    assert json.loads((tmp_path / "rec" / f"local.{LABEL}.json").read_text()) == rec


def test_cli_blas_pinned_flag_reaches_check(monkeypatch):
    seen = []

    def capture(*a, **k):
        seen.append(k)
        return {"config_sha256": "0" * 64, "cpu": {"model_name": "x"},
                "blas": {"status": "pinned" if k["blas_pinned"] else "not_checked"}}

    monkeypatch.setattr(job_guard, "check", capture)
    argv = ["check", "--stage", "production", "--arm", ARM, "--config-sha256", "0" * 64, "--record-dir", "/tmp/x",
            "--label", LABEL]
    assert job_guard.main(argv + ["--blas-pinned"]) == 0
    assert job_guard.main(argv) == 0
    assert [k["blas_pinned"] for k in seen] == [True, False]


# ---- r4_heavy: the real job env, the named env, the pin file and the lock manifest ---------------------------------

@pytest.mark.r4_heavy
@_needs_rs1
def test_job_env_locator_equals_snakemake_env_address(tmp_path):
    from snakemake.deployment.conda import Env

    wf = types.SimpleNamespace(conda_frontend="conda", singularity_args="",
                               persistence=types.SimpleNamespace(conda_env_path=R4_CONDA_PREFIX),
                               sourcecache=types.SimpleNamespace(open=lambda f, mode="rb": open(f.get_path_or_uri(), mode)))
    d = job_env_dir(YML, R4_CONDA_PREFIX)
    assert str(d) == Env(wf, env_file=str(YML), env_dir=R4_CONDA_PREFIX).address
    assert d.is_dir() and (d / "bin/Rscript").is_file()
    (tmp_path / "envs").mkdir()
    shutil.copy2(YML, tmp_path / "envs/r_coloc.yml")
    assert job_env_dir(tmp_path / "envs/r_coloc.yml", R4_CONDA_PREFIX) == d
    (tmp_path / "envs/r_coloc.post-deploy.sh").write_text("#!/bin/sh\n")
    with pytest.raises(RuntimeError, match="post-deploy"):
        job_env_dir(tmp_path / "envs/r_coloc.yml", R4_CONDA_PREFIX)


def _lock_rows():
    with open(LOCK_TSV) as fh:
        return list(csv.DictReader((ln for ln in fh if not ln.startswith("#")), delimiter="\t"))


@pytest.mark.r4_heavy
@_needs_rs1
def test_real_job_env_passes_and_named_env_is_refused():
    pin = job_guard.libopenblas_pin(REPO_ROOT)
    d = job_env_dir(YML, R4_CONDA_PREFIX)
    facts = job_guard.blas_facts(str(d), None, None)
    assert job_guard.blas_violations(facts, pin) == [], facts
    corename = [r["value"] for r in _lock_rows() if r["kind"] == "corename"]
    assert corename == [facts["corename"]], (corename, facts)
    named = job_guard.blas_violations(job_guard.blas_facts(str(NAMED_ENV), None, None), pin)
    assert any(v.startswith(f"conda-meta libopenblas version 0.3.32 != pin {pin}") for v in named), named


@pytest.mark.r4_heavy
@_needs_rs1
def test_pin_file_equals_the_job_env_explicit_list():
    d = job_env_dir(YML, R4_CONDA_PREFIX)
    assert filecmp.cmp(str(d) + ".pin.txt", PIN_FILE, shallow=False)
    out = subprocess.run([CONDA, "list", "--explicit", "--md5", "-p", str(d)], capture_output=True, text=True,
                         check=True).stdout
    assert _explicit_lines(out) == _explicit_lines(PIN_FILE.read_text())


@pytest.mark.r4_heavy
@_needs_rs1
def test_env_lock_manifest_matches_the_job_env():
    d = job_env_dir(YML, R4_CONDA_PREFIX)
    rows = _lock_rows()
    want = []
    for f in sorted((d / "conda-meta").glob("*.json")):
        m = json.loads(f.read_text())
        want.append({"kind": "package", "name": m["name"], "version": m["version"], "build": m["build"],
                     "channel": m["channel"], "value": m["md5"]})
    assert [r for r in rows if r["kind"] == "package"] == want
    pin = job_guard.libopenblas_pin(REPO_ROOT)
    so = d / "lib" / f"libopenblasp-r{pin}.so"
    sha = [r for r in rows if r["kind"] == "libopenblas_sha256"]
    assert sha == [{"kind": "libopenblas_sha256", "name": so.name, "version": pin, "build": "", "channel": "",
                    "value": hashlib.sha256(so.read_bytes()).hexdigest()}]
    assert [r["value"] for r in rows if r["kind"] == "corename"] == ["SkylakeX"]
    assert {r["kind"] for r in rows} == {"package", "libopenblas_sha256", "corename"}


# ---- gate_command / is_r_coloc_env: the flag follows the rule's conda directive (Task 4) ----------------------------

def test_gate_command_flags_only_the_r_coloc_env(tmp_path):
    yml = str(REPO_ROOT / "envs/r_coloc.yml")
    assert commands.is_r_coloc_env(yml, REPO_ROOT) is True
    link = tmp_path / "link_r_coloc.yml"
    link.symlink_to(yml)
    assert commands.is_r_coloc_env(str(link), REPO_ROOT) is True
    assert commands.is_r_coloc_env(Path(yml), str(REPO_ROOT)) is True
    assert commands.is_r_coloc_env(None, REPO_ROOT) is False
    assert commands.is_r_coloc_env(str(REPO_ROOT / "envs/python_stats.yml"), REPO_ROOT) is False
    for bad in ("envs/r_coloc.yml", lambda w: yml, 1):
        with pytest.raises(ValueError):
            commands.is_r_coloc_env(bad, REPO_ROOT)
    cfg = job_guard.merged_config_from_files(REPO_ROOT, ARM)
    off = commands.gate_command("production", ARM, cfg, label=LABEL, blas_pinned=False)
    assert "--blas-pinned" not in off and off[-2:] == ["--label", LABEL]
    assert commands.gate_command("production", ARM, cfg, label=LABEL, blas_pinned=True) == off + ["--blas-pinned"]
    for kw in ({"blas_pinned": None}, {}, {"blas_pinned": 1}):
        with pytest.raises(ValueError, match="blas_pinned"):
            commands.gate_command("production", ARM, cfg, label=LABEL, **kw)
    assert commands.gate_command("repro") == ["true"]
