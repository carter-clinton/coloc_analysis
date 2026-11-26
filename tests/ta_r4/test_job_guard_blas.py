"""W3f 15.8b (review R6; Carter Q-157J, Q-158R6S, Q-158R6G A): envs/r_coloc.yml pins libopenblas with an exact pin
file; the Snakemake job env built from it is the env the jobs ran in."""
from __future__ import annotations

import csv
import filecmp
import hashlib
import json
import re
import shutil
import subprocess
import types
from pathlib import Path

import pytest

from ta_r4.conda_job_env import R4_CONDA_PREFIX, job_env_dir

from .conftest import MAN_DIR, REPO_ROOT

CONDA = "/rs1/researchers/c/ckclinto/miniconda3/condabin/conda"
YML = REPO_ROOT / "envs/r_coloc.yml"
PIN_FILE = REPO_ROOT / "envs/r_coloc.linux-64.pin.txt"
LOCK_TSV = MAN_DIR / "env_lock_r_coloc_job.tsv"
_needs_rs1 = pytest.mark.skipif(not Path(R4_CONDA_PREFIX).is_dir(), reason="/rs1 job-env prefix absent")


def _explicit_lines(text):
    """The URL#md5 package lines after @EXPLICIT (the `# created-by` and other header lines are not compared)."""
    lines = text.splitlines()
    i = lines.index("@EXPLICIT")
    return [ln for ln in lines[i + 1:] if ln.strip() and not ln.startswith("#")]


def _yaml_pin():
    pins = re.findall(r"^\s*-\s*libopenblas=(\S+)\s*$", YML.read_text(), flags=re.M)
    assert len(pins) == 1, pins
    return pins[0]


def _lock_rows():
    with open(LOCK_TSV) as fh:
        return list(csv.DictReader((ln for ln in fh if not ln.startswith("#")), delimiter="\t"))


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
    pin = _yaml_pin()
    so = d / "lib" / f"libopenblasp-r{pin}.so"
    sha = [r for r in rows if r["kind"] == "libopenblas_sha256"]
    assert sha == [{"kind": "libopenblas_sha256", "name": so.name, "version": pin, "build": "", "channel": "",
                    "value": hashlib.sha256(so.read_bytes()).hexdigest()}]
    assert [r["value"] for r in rows if r["kind"] == "corename"] == ["SkylakeX"]
    assert {r["kind"] for r in rows} == {"package", "libopenblas_sha256", "corename"}
