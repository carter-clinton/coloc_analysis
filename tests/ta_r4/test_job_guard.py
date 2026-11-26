"""W3f 15.7a (review F1): every production job checks the resolved config digest, the CPU type and the OpenBLAS env and
records them; bin/r4_fire.sh and Snakefile.ta_r4 refuse run-configuration overrides on a production arm."""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ta_r4 import commands, job_guard, r4_lock_gate
from ta_r4.r4_lock_gate import LockGateError

from .conftest import REPO_ROOT, merged_config
from .test_in_job_gate import _fire, _fire_repo, build_gate_repo, dry_run
from .test_lock_gate import SMK

ARM = "A3_1kg"
LABEL = "r4_run_finemap.ancestry=EUR_region=SH2B3_12q24_trait=asthma"
_BASE_FLAGS = "fpu vme sse sse2 ssse3 sse4_1 sse4_2 avx avx2 fma avx512f avx512dq avx512cd avx512bw avx512vl"


def _cpuinfo(model, extra=(), family=6, n=2):
    flags = " ".join([_BASE_FLAGS, *extra])
    return "".join(f"processor\t: {i}\nvendor_id\t: GenuineIntel\ncpu family\t: {family}\nmodel\t\t: {model}\n"
                   f"model name\t: Intel(R) Xeon(R) CPU model {model}\nflags\t\t: {flags}\n\n" for i in range(n))


CASCADELAKE = _cpuinfo(85, ("avx512_vnni",))
CPU_REJECTED = {
    "skylake_sp": _cpuinfo(85),
    "cooper_lake": _cpuinfo(85, ("avx512_vnni", "avx512_bf16")),
    "broadwell": _cpuinfo(79).replace(" avx512f avx512dq avx512cd avx512bw avx512vl", ""),
    "haswell": _cpuinfo(63).replace(" avx512f avx512dq avx512cd avx512bw avx512vl", ""),
}
CLEAN_ENV = {"PATH": "/usr/bin", "OPENBLAS_VERBOSE": "2"}


# ---- CPU type and kernel env --------------------------------------------------------------------------------------

def test_cpu_cascadelake_accepted():
    assert job_guard.cpu_is_cascadelake(CASCADELAKE) is True


@pytest.mark.parametrize("kind", list(CPU_REJECTED))
def test_cpu_rejected(kind):
    assert job_guard.cpu_is_cascadelake(CPU_REJECTED[kind]) is False


def test_openblas_coretype_rejected():
    assert job_guard.kernel_env_violations({"PATH": "/usr/bin", "OPENBLAS_CORETYPE": "Haswell"}) == ["OPENBLAS_CORETYPE"]


def test_openblas_verbose_and_num_threads_allowed():
    assert job_guard.ALLOWED_OPENBLAS_ENV == ("OPENBLAS_VERBOSE", "OPENBLAS_NUM_THREADS")
    assert job_guard.kernel_env_violations({"PATH": "/usr/bin", "OPENBLAS_VERBOSE": "2", "OPENBLAS_NUM_THREADS": "1"}) == []


# ---- config digest -------------------------------------------------------------------------------------------------

def test_merged_config_matches_snakemake_update_config():
    assert job_guard.CONFIG_FILES(ARM) == ["config/pipeline.yaml", "config/ta_r4/overlay_base.yaml",
                                           f"config/ta_r4/overlay_{ARM}.yaml"]
    got = job_guard.merged_config_from_files(REPO_ROOT, ARM)
    assert got == merged_config("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{ARM}.yaml")
    assert got["ta_r4"]["arm"] == ARM and got["finemap"]["credible_set"] == 0.95


def test_credible_set_override_changes_the_digest():
    cfg = job_guard.merged_config_from_files(REPO_ROOT, ARM)
    probe = copy.deepcopy(cfg)
    probe["finemap"]["credible_set"] = 0.5
    fit = commands.fit_command(ARM, "asthma", "EUR", "SH2B3_12q24", probe)
    assert fit[fit.index("--credible-set") + 1] == "0.5"  # the reviewer's probe still renders
    d0, d1 = job_guard.config_digest(cfg), job_guard.config_digest(probe)
    assert len(d0) == 64 and d0 != d1
    assert d0 == job_guard.config_digest(job_guard.merged_config_from_files(REPO_ROOT, ARM))


@pytest.fixture
def gate_passes(monkeypatch):
    calls = []
    monkeypatch.setattr(r4_lock_gate, "check_lock_gate", lambda repo, stage: calls.append((str(repo), stage)))
    return calls


def blas_prefix(root, pin, *, meta_versions=None, libblas_to=None, liblapack_to=None, rscript=True):
    """A fake conda prefix that passes every --blas-pinned check for `pin` unless one argument changes it: conda-meta
    libopenblas records (`meta_versions`), libblas.so.3's / liblapack.so.3's target (`libblas_to` / `liblapack_to`),
    bin/Rscript (`rscript`)."""
    root = Path(root)
    (root / "conda-meta").mkdir(parents=True)
    for i, v in enumerate([pin] if meta_versions is None else meta_versions):
        (root / "conda-meta" / f"libopenblas-{v}-pthreads_h{i}_0.json").write_text(
            json.dumps({"name": "libopenblas", "version": v, "build": f"pthreads_h{i}_0"}))
    lib = root / "lib"
    lib.mkdir()
    so = lib / f"libopenblasp-r{pin}.so"
    so.write_text("dummy\n")
    (lib / "libblas.so.3").symlink_to(so.name if libblas_to is None else libblas_to)
    (lib / "liblapack.so.3").symlink_to(so.name if liblapack_to is None else liblapack_to)
    if rscript:
        (root / "bin").mkdir()
        (root / "bin" / "Rscript").write_text("#!/bin/sh\n")
    return root


def blas_stubs(prefix, pin):
    """(blas_probe, r_blas_probe) stubs returning the pinned runtime config and the prefix's pinned library."""
    so = str(Path(prefix) / "lib" / f"libopenblasp-r{pin}.so")
    return (lambda library: (f"OpenBLAS {pin} DYNAMIC_ARCH NO_AFFINITY SkylakeX MAX_THREADS=128", "SkylakeX"),
            lambda rscript: so)


def _check(tmp_path, digest, *, environ=None, cpuinfo=CASCADELAKE, label=LABEL, blas_pinned=True):
    env = dict(CLEAN_ENV if environ is None else environ)
    kw = {}
    if blas_pinned is True:
        pin = job_guard.libopenblas_pin(REPO_ROOT)
        prefix = tmp_path / "blas_prefix"
        if not prefix.exists():
            blas_prefix(prefix, pin)
        env.setdefault("CONDA_PREFIX", str(prefix))
        kw["blas_probe"], kw["r_blas_probe"] = blas_stubs(prefix, pin)
    return job_guard.check(REPO_ROOT, ARM, digest, environ=env, cpuinfo=cpuinfo, record_dir=tmp_path / "rec",
                           label=label, blas_pinned=blas_pinned, **kw)


def test_guard_refuses_a_digest_mismatch(tmp_path, gate_passes):
    probe = job_guard.merged_config_from_files(REPO_ROOT, ARM)
    probe["finemap"]["credible_set"] = 0.5
    with pytest.raises(job_guard.JobGuardError, match="digest"):
        _check(tmp_path, job_guard.config_digest(probe))
    assert gate_passes == [(str(REPO_ROOT), "production")]
    assert not (tmp_path / "rec").exists() or not list((tmp_path / "rec").iterdir())
    for bad_cpu, bad_env in ((CPU_REJECTED["skylake_sp"], None), (CASCADELAKE, {"OPENBLAS_CORETYPE": "Haswell"})):
        with pytest.raises(job_guard.JobGuardError):
            _check(tmp_path, job_guard.config_digest(job_guard.merged_config_from_files(REPO_ROOT, ARM)),
                   cpuinfo=bad_cpu, environ=bad_env)


def test_guard_writes_the_record(tmp_path, gate_passes):
    cfg = job_guard.merged_config_from_files(REPO_ROOT, ARM)
    d = job_guard.config_digest(cfg)
    rec = _check(tmp_path, d, environ={"SLURM_JOB_ID": "4242", "OPENBLAS_VERBOSE": "2", "OPENBLAS_NUM_THREADS": "1"})
    path = tmp_path / "rec" / f"4242.{LABEL}.json"
    assert path.is_file() and json.loads(path.read_text()) == rec
    assert rec["config_sha256"] == d and rec["credible_set"] == 0.95 and rec["arm"] == ARM and rec["label"] == LABEL
    assert rec["openblas_env"] == {"OPENBLAS_NUM_THREADS": "1", "OPENBLAS_VERBOSE": "2"}
    assert rec["cpu"]["family"] == 6 and rec["cpu"]["model"] == 85 and "Xeon" in rec["cpu"]["model_name"]
    assert rec["checked"] == {"lock_gate": True, "config_digest": True, "cpu_cascadelake": True, "kernel_env": True,
                              "blas_pinned": True}
    assert rec["host"] and rec["slurm_job_id"] == "4242"
    assert rec["ld_flags"] == {"EUR": {"ld_authoritative": "true", "ld_allele_aware": "true"}}
    _check(tmp_path, d, label="r4_sim.gen=gen_1kg_region=SH2B3_12q24_scenario=H0")
    assert (tmp_path / "rec" / "local.r4_sim.gen=gen_1kg_region=SH2B3_12q24_scenario=H0.json").is_file()


def test_guard_runs_the_lock_gate_first(tmp_path, monkeypatch):
    calls = []

    def refuse(repo, stage):
        calls.append(stage)
        raise LockGateError("(g) locked paths drifted: fixture")

    monkeypatch.setattr(r4_lock_gate, "check_lock_gate", refuse)
    with pytest.raises(LockGateError, match="locked paths drifted"):  # a bad digest, CPU and env too: the gate wins
        _check(tmp_path, "f" * 64, cpuinfo=CPU_REJECTED["haswell"], environ={"OPENBLAS_CORETYPE": "Haswell"})
    assert calls == ["production"] and not (tmp_path / "rec").exists()


# ---- gate_command -----------------------------------------------------------------------------------------------------

def test_gate_command_production_is_the_guard():
    cfg = job_guard.merged_config_from_files(REPO_ROOT, ARM)
    assert commands.gate_command("production", ARM, cfg, label=LABEL, blas_pinned=False) == commands._PY + [
        "ta_r4.job_guard", "check", "--stage", "production", "--arm", ARM,
        "--config-sha256", job_guard.config_digest(cfg), "--record-dir", "data/r4/logs/job_guard", "--label", LABEL]


def test_gate_command_repro_unchanged():
    assert commands.gate_command("repro") == ["true"]


# ---- bin/r4_fire.sh production allowlist ---------------------------------------------------------------------------

REFUSED_FLAGS = {"--config": ["--config", "finemap={credible_set:0.5}"], "-C": ["-C", "x=1"],
                 "--configfile": ["--configfile", "config/ta_r4/overlay_base.yaml"],
                 "--profile": ["--profile", "config/ta_r4/cluster_slurm"], "--cluster": ["--cluster", "sbatch"],
                 "--jobscript": ["--jobscript", "config/ta_r4/cluster_slurm/jobscript.sh"]}


@pytest.mark.parametrize("flag", list(REFUSED_FLAGS))
def test_fire_refuses_production_flag(tmp_path, flag):
    repo, stub = _fire_repo(tmp_path)
    p, called = _fire(repo, stub, "-n", *REFUSED_FLAGS[flag])
    assert p.returncode == 2 and "REFUSED" in p.stderr and flag in p.stderr and not called, (p.returncode, p.stderr)
    assert "every production job re-runs the lock gate" not in p.stdout  # refused before the lock gate


@pytest.mark.parametrize("var", ["R4_FIRE_PY", "R4_FIRE_SMK"])
def test_fire_refuses_env_override(tmp_path, var):
    repo, stub = _fire_repo(tmp_path)
    p, called = _fire(repo, stub, env={var: str(stub / ("py" if var == "R4_FIRE_PY" else "smk"))})
    assert p.returncode == 2 and "REFUSED" in p.stderr and var in p.stderr and not called, (p.returncode, p.stderr)


ALLOWED_FLAGS = {"-n": ["-n"], "-p": ["-p"], "--list": ["--list"], "--unlock": ["--unlock"], "-j_4": ["-j", "4"]}


@pytest.mark.parametrize("flag", list(ALLOWED_FLAGS))
def test_fire_allows_production_flag(tmp_path, flag):
    repo, stub = _fire_repo(tmp_path)
    p, called = _fire(repo, stub, *ALLOWED_FLAGS[flag], "data/r4/results/x.json")
    assert p.returncode == 0 and called, p.stderr
    argv = (stub / "smk_called").read_text().split()
    assert argv[-1 - len(ALLOWED_FLAGS[flag]):] == [*ALLOWED_FLAGS[flag], "data/r4/results/x.json"]


# ---- Snakefile.ta_r4 construction refusal (production arm) ---------------------------------------------------------

REFUSAL = "REFUSED: production run configuration differs from the committed configuration files"
CFG = ["config/pipeline.yaml", "config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{ARM}.yaml"]


@pytest.fixture(scope="module")
def gate_repo(tmp_path_factory):
    repo, _, targets = build_gate_repo(tmp_path_factory.mktemp("guard"))
    other = tmp_path_factory.mktemp("other")
    shutil.copy2(repo / CFG[2], other / Path(CFG[2]).name)
    (other / "extra.yaml").write_text("x: 1\n")
    return repo, targets, other


def _smk(repo, targets, cfg, *extra):
    p = subprocess.run([SMK, *targets, "-s", "Snakefile.ta_r4", "-d", ".", "-n", "--configfile", *cfg, *extra],
                       cwd=repo, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


@pytest.mark.r4_heavy
def test_clean_locked_production_dry_run_passes_construction(gate_repo):
    repo, targets, _ = gate_repo
    rc, out = dry_run(repo, targets)
    assert rc == 0 and REFUSAL not in out and "Job stats" in out, out[-3000:]


@pytest.mark.r4_heavy
@pytest.mark.parametrize("case", ["config_arg", "extra_configfile", "overlay_at_another_path", "reordered_configfiles"])
def test_construction_refuses(gate_repo, case):
    repo, targets, other = gate_repo
    cfg, extra = list(CFG), []
    if case == "config_arg":
        extra = ["--config", "x=1"]
    elif case == "extra_configfile":
        cfg.append(str(other / "extra.yaml"))
    elif case == "overlay_at_another_path":
        cfg[2] = str(other / Path(CFG[2]).name)
        assert (other / Path(CFG[2]).name).read_bytes() == (repo / CFG[2]).read_bytes()
    else:
        cfg = [CFG[0], CFG[2], CFG[1]]
    rc, out = _smk(repo, targets, cfg, *extra)
    assert rc != 0 and REFUSAL in out, out[-3000:]
    before = out[:out.index(REFUSAL)]
    assert "LockGateError" not in before and "lock gate" not in before.lower(), before[-2000:]
