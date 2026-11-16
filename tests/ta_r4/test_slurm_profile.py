"""bin/r4_fire.sh Slurm profile: every submitted job carries the cluster's required sbatch flags and a sized -t.

A real snakemake run of the committed profile against a toy Snakefile, with fake sbatch/sacct on PATH recording the
argv; the same checker must fail on profiles with -t or set-resources removed (negative controls).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
PROFILE = REPO / "config/ta_r4/cluster_slurm"
STATUS = PROFILE / "status.sh"
JOBSCRIPT = PROFILE / "jobscript.sh"
SMK = str(Path(sys.executable).parent / "snakemake")
REQUIRED = (("-p", "compute"), ("-A", "clintonlab_cpu"), ("-q", "normal"))
#: Carter 2026-11-16: OpenBLAS picks its kernel by CPU; pinned fits reproduce only on the AVX-512 kernel
CONSTRAINT = "--constraint=cascadelake"
BLAS_ENV = "blas_env=unset,2"  # OPENBLAS_CORETYPE never set; OPENBLAS_VERBOSE=2 logs the selected core
#: rule -> (runtime minutes, mem_mb) the profile must submit with
EXPECTED = {"toy_default": (60, 8000), "r4_run_finemap": (180, 48000), "r4_panel_ukb_native": (120, 48000)}

TOY = """
rule all:
    input: "out/toy_default.txt", "out/r4_run_finemap.txt", "out/r4_panel_ukb_native.txt"

rule toy_default:
    output: "out/toy_default.txt"
    shell: "echo blas_env=${{OPENBLAS_CORETYPE:-unset}},${{OPENBLAS_VERBOSE:-unset}} >&2; echo ok > {output}"

rule r4_run_finemap:
    output: "out/r4_run_finemap.txt"
    resources: mem_mb=8000
    shell: "echo blas_env=${{OPENBLAS_CORETYPE:-unset}},${{OPENBLAS_VERBOSE:-unset}} >&2; echo ok > {output}"

rule r4_panel_ukb_native:
    output: "out/r4_panel_ukb_native.txt"
    resources: mem_mb=48000
    shell: "echo blas_env=${{OPENBLAS_CORETYPE:-unset}},${{OPENBLAS_VERBOSE:-unset}} >&2; echo ok > {output}"
"""

FAKE_SBATCH = """#!/usr/bin/env bash
script="${@: -1}"
printf '%s\\x1f' "$@" >> "$FAKE_LOG"; printf '\\n' >> "$FAKE_LOG"
bash "$script" > /dev/null 2>> "$FAKE_ERR"
echo $((RANDOM + 1000))
"""
FAKE_SACCT = '#!/usr/bin/env bash\necho "${FAKE_SACCT_STATE:-COMPLETED}"\n'


def _bin(d: Path, name: str, body: str):
    p = d / name
    p.write_text(body)
    p.chmod(0o755)


def _run_profile(tmp_path: Path, profile: dict) -> tuple[list[list[str]], str]:
    work = tmp_path / "w"
    (work / "config/ta_r4/cluster_slurm").mkdir(parents=True)
    shutil.copy2(STATUS, work / "config/ta_r4/cluster_slurm/status.sh")
    if JOBSCRIPT.is_file():
        shutil.copy2(JOBSCRIPT, work / "config/ta_r4/cluster_slurm/jobscript.sh")
    prof = tmp_path / "profile"
    prof.mkdir()
    (prof / "config.yaml").write_text(yaml.safe_dump(profile))
    (work / "Snakefile").write_text(TOY)
    fb = tmp_path / "fakebin"
    fb.mkdir()
    _bin(fb, "sbatch", FAKE_SBATCH)
    _bin(fb, "sacct", FAKE_SACCT)
    log = tmp_path / "sbatch.log"
    log.touch()
    err = tmp_path / "jobs.err"
    err.touch()
    env = dict(os.environ, PATH=f"{fb}:{os.environ['PATH']}", FAKE_LOG=str(log), FAKE_ERR=str(err))
    env.pop("OPENBLAS_CORETYPE", None)
    env.pop("OPENBLAS_VERBOSE", None)
    p = subprocess.run([SMK, "--profile", str(prof), "--nolock", "all"],
                       cwd=work, env=env, capture_output=True, text=True, timeout=600)
    assert p.returncode == 0, p.stdout[-3000:] + p.stderr[-3000:]
    return [ln.split("\x1f")[:-1] for ln in log.read_text().splitlines() if ln], err.read_text()


def _flag(argv, f):
    return [argv[i + 1] for i, a in enumerate(argv[:-1]) if a == f]


def sbatch_violations(calls: list[list[str]], err: str) -> list[str]:
    bad = []
    for tag in ("r4_placement host=", BLAS_ENV):
        if err.count(tag) != len(calls):
            bad.append(f"job stderr has {err.count(tag)} x {tag!r}, expected one per job ({len(calls)})")
    rules = {}
    for argv in calls:
        name = (_flag(argv, "-J") or ["?"])[0].removeprefix("r4.")
        rules[name] = argv
        for f, v in REQUIRED:
            if _flag(argv, f) != [v]:
                bad.append(f"{name}: {f} {_flag(argv, f)} != [{v!r}]")
        t = _flag(argv, "-t")
        if len(t) != 1 or not t[0].isdigit():
            bad.append(f"{name}: -t {t} is not one integer (minutes)")
        elif name in EXPECTED and int(t[0]) != EXPECTED[name][0]:
            bad.append(f"{name}: -t {t[0]} != {EXPECTED[name][0]}")
        m = [a for a in argv if a.startswith("--mem=")]
        if name in EXPECTED and m != [f"--mem={EXPECTED[name][1]}"]:
            bad.append(f"{name}: {m} != --mem={EXPECTED[name][1]}")
        if [a for a in argv if a.startswith("--constraint")] != [CONSTRAINT]:
            bad.append(f"{name}: constraint {[a for a in argv if a.startswith('--constraint')]} != [{CONSTRAINT!r}]")
        if "--parsable" not in argv or "--export=ALL" not in argv:
            bad.append(f"{name}: --parsable/--export=ALL missing")
    if sorted(rules) != sorted(EXPECTED):
        bad.append(f"submitted rules {sorted(rules)} != {sorted(EXPECTED)}")
    return bad


def _committed():
    return yaml.safe_load((PROFILE / "config.yaml").read_text())


@pytest.mark.r4_heavy
@pytest.mark.skipif(not Path(SMK).is_file(), reason="snakemake not beside sys.executable")
def test_committed_profile_submits_every_job_with_required_flags(tmp_path):
    assert sbatch_violations(*_run_profile(tmp_path, _committed())) == []


@pytest.mark.r4_heavy
@pytest.mark.skipif(not Path(SMK).is_file(), reason="snakemake not beside sys.executable")
@pytest.mark.parametrize("mutation", ["no_t", "no_set_resources", "no_account", "no_constraint", "no_jobscript"])
def test_checker_fails_on_broken_profiles(tmp_path, mutation):
    prof = _committed()
    if mutation == "no_t":
        prof["cluster"] = prof["cluster"].replace(" -t {resources.runtime}", "")
    elif mutation == "no_set_resources":
        del prof["set-resources"]
    elif mutation == "no_account":
        prof["cluster"] = prof["cluster"].replace(" -A clintonlab_cpu", "")
    elif mutation == "no_constraint":
        prof["cluster"] = prof["cluster"].replace(f" {CONSTRAINT}", "")
    else:
        del prof["jobscript"]
    assert sbatch_violations(*_run_profile(tmp_path, prof)) != []


@pytest.mark.parametrize("state,want", [("COMPLETED", "success"), ("RUNNING", "running"), ("PENDING", "running"),
                                        ("TIMEOUT", "failed"), ("OUT_OF_MEMORY", "failed"), ("FAILED", "failed"),
                                        ("CANCELLED", "failed"), ("NODE_FAIL", "failed")])
def test_status_script_maps_slurm_states(tmp_path, state, want):
    _bin(tmp_path, "sacct", FAKE_SACCT)
    env = dict(os.environ, PATH=f"{tmp_path}:{os.environ['PATH']}", FAKE_SACCT_STATE=state)
    p = subprocess.run(["bash", str(STATUS), "12345;cluster"], env=env, capture_output=True, text=True)
    assert (p.returncode, p.stdout.strip()) == (0, want)


def test_fire_script_uses_the_slurm_profile(tmp_path):
    """Behavioural: bin/r4_fire.sh hands snakemake --profile config/ta_r4/cluster_slurm (fake snakemake prints argv)."""
    fake = tmp_path / "smk"
    _bin(tmp_path, "smk", '#!/usr/bin/env bash\nprintf "%s\\n" "$@"\n')
    env = dict(os.environ, R4_FIRE_SMK=str(fake))
    p = subprocess.run(["bash", str(REPO / "bin/r4_fire.sh"), "repro", "repro_routeC", "-n"], env=env,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    argv = p.stdout.splitlines()
    assert _flag(argv, "--profile") == ["config/ta_r4/cluster_slurm"]
