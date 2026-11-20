"""First command of every production job (W3f 15.7a, review F1). Runs the lock gate, then refuses to run unless the
job's run configuration, CPU type and OpenBLAS env are the committed ones, and writes a JSON record of what it checked.

  python -m ta_r4.job_guard check --stage production --arm ARM --config-sha256 HEX --record-dir DIR --label LABEL

The digest is the one commands.gate_command rendered from the job's merged Snakemake config; the guard recomputes it
from the three committed configuration files, so a --config / --configfile / profile override fails here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import sys
from pathlib import Path

from ta_r4 import r4_lock_gate
from ta_r4.r4_lock_gate import LockGateError

ALLOWED_OPENBLAS_ENV = ("OPENBLAS_VERBOSE", "OPENBLAS_NUM_THREADS")
CASCADELAKE = {"family": 6, "model": 85, "required": ("avx512_vnni",), "absent": ("avx512_bf16",)}


class JobGuardError(Exception):
    pass


def CONFIG_FILES(arm):
    """The committed configuration files of an arm, in Snakemake merge order (bin/r4_fire.sh --configfile)."""
    return ["config/pipeline.yaml", "config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml"]


def merged_config_from_files(repo, arm):
    """The merged config Snakemake builds from CONFIG_FILES(arm) (snakemake.utils.update_config, in order)."""
    from snakemake.io import load_configfile
    from snakemake.utils import update_config

    cfg = {}
    for rel in CONFIG_FILES(arm):
        update_config(cfg, load_configfile(str(Path(repo) / rel)) or {})
    return cfg


def config_digest(cfg):
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _cpus(cpuinfo):
    out = []
    for blk in cpuinfo.strip().split("\n\n"):
        kv = {}
        for line in blk.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                kv[k.strip()] = v.strip()
        if "processor" in kv:
            out.append(kv)
    return out


def _cpu_summary(cpu):
    return {"family": int(cpu.get("cpu family", -1)), "model": int(cpu.get("model", -1)),
            "model_name": cpu.get("model name", ""), "flags": sorted(set(cpu.get("flags", "").split()))}


def cpu_is_cascadelake(cpuinfo):
    """Every processor is Cascade Lake: family 6, model 85, avx512_vnni present, avx512_bf16 absent (Skylake-SP is
    model 85 without avx512_vnni; Cooper Lake is model 85 with avx512_bf16)."""
    cpus = _cpus(cpuinfo)
    if not cpus:
        return False
    for c in map(_cpu_summary, cpus):
        if (c["family"], c["model"]) != (CASCADELAKE["family"], CASCADELAKE["model"]):
            return False
        if not all(f in c["flags"] for f in CASCADELAKE["required"]) or any(f in c["flags"] for f in CASCADELAKE["absent"]):
            return False
    return True


def kernel_env_violations(environ):
    """OPENBLAS_* variables other than OPENBLAS_VERBOSE / OPENBLAS_NUM_THREADS (e.g. OPENBLAS_CORETYPE), sorted."""
    return sorted(k for k in environ if k.startswith("OPENBLAS_") and k not in ALLOWED_OPENBLAS_ENV)


def _ld_flags(arm, cfg):
    from ld_read_path import ld_allele_aware, ld_file_authoritative
    from ta_r4.arms import arm_ancestries

    return {a: {"ld_authoritative": ld_file_authoritative(a, cfg), "ld_allele_aware": ld_allele_aware(a, cfg)}
            for a in arm_ancestries(arm)}


def check(repo, arm, digest, *, environ, cpuinfo, record_dir, label):
    """Lock gate first (raises LockGateError), then digest, CPU and kernel env (raise JobGuardError); on success writes
    <record_dir>/<SLURM_JOB_ID or local>.<label>.json and returns the record."""
    r4_lock_gate.check_lock_gate(Path(repo), "production")
    if not label or "/" in label or label.startswith("."):
        raise JobGuardError(f"label {label!r}: must be a non-empty file-name component")
    cfg = merged_config_from_files(repo, arm)
    want = config_digest(cfg)
    if digest != want:
        raise JobGuardError(f"run configuration digest {digest} != {want}, the digest of the committed files "
                            f"{CONFIG_FILES(arm)}: the job was built under an overridden configuration")
    cpus = _cpus(cpuinfo)
    if not cpu_is_cascadelake(cpuinfo):
        seen = sorted({(c["family"], c["model"], c["model_name"]) for c in map(_cpu_summary, cpus)})
        raise JobGuardError(f"CPU is not Cascade Lake (family 6, model 85, avx512_vnni, no avx512_bf16): {seen}")
    bad = kernel_env_violations(environ)
    if bad:
        raise JobGuardError(f"OpenBLAS variables other than {list(ALLOWED_OPENBLAS_ENV)} are set: {bad}")
    cpu = _cpu_summary(cpus[0])
    job = environ.get("SLURM_JOB_ID") or "local"
    rec = {
        "label": label, "arm": arm, "host": socket.gethostname(), "slurm_job_id": environ.get("SLURM_JOB_ID"),
        "cpu": {"family": cpu["family"], "model": cpu["model"], "model_name": cpu["model_name"], "n_processors": len(cpus),
                "avx512_vnni": "avx512_vnni" in cpu["flags"], "avx512_bf16": "avx512_bf16" in cpu["flags"]},
        "checked": {"lock_gate": True, "config_digest": True, "cpu_cascadelake": True, "kernel_env": True},
        "openblas_env": {k: environ[k] for k in sorted(environ) if k.startswith("OPENBLAS_")},
        "config_files": CONFIG_FILES(arm), "config_sha256": want,
        "credible_set": cfg.get("finemap", {}).get("credible_set"),
        "ld_flags": _ld_flags(arm, cfg),
    }
    out = Path(record_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{job}.{label}.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m ta_r4.job_guard", description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    c = sub.add_parser("check")
    c.add_argument("--stage", required=True, choices=["production"])
    c.add_argument("--arm", required=True)
    c.add_argument("--config-sha256", required=True)
    c.add_argument("--record-dir", required=True)
    c.add_argument("--label", required=True)
    args = ap.parse_args(argv)
    repo = Path(__file__).resolve().parents[3]  # as r4_lock_gate.main
    rd = Path(args.record_dir)
    try:
        with open("/proc/cpuinfo") as fh:
            cpuinfo = fh.read()
        rec = check(repo, args.arm, args.config_sha256, environ=dict(os.environ), cpuinfo=cpuinfo,
                    record_dir=rd if rd.is_absolute() else repo / rd, label=args.label)
    except LockGateError as e:
        print(f"LockGateError: {e}", file=sys.stderr)
        return 1
    except JobGuardError as e:
        print(f"JobGuardError: {e}", file=sys.stderr)
        return 1
    print(f"job guard OK (lock gate, config {rec['config_sha256'][:12]}, {rec['cpu']['model_name']}, label {args.label})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
