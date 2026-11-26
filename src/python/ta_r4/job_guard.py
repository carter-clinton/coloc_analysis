"""First command of every production job (W3f 15.7a, review F1). Runs the lock gate, then refuses to run unless the
job's run configuration, CPU type and OpenBLAS env are the committed ones, and writes a JSON record of what it checked.

  python -m ta_r4.job_guard check --stage production --arm ARM --config-sha256 HEX --record-dir DIR --label LABEL [--blas-pinned]

With --blas-pinned (gated rules whose conda env is envs/r_coloc.yml; 15.8b, Carter Q-158R6G A) it also refuses a job
whose CONDA_PREFIX does not load the libopenblas version pinned in envs/r_coloc.yml; without it the BLAS is not read
and the record says so.

The digest is the one commands.gate_command rendered from the job's merged Snakemake config; the guard recomputes it
from the three committed configuration files, so a --config / --configfile / profile override fails here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
from pathlib import Path

from ta_r4 import r4_lock_gate
from ta_r4.r4_lock_gate import LockGateError

ALLOWED_OPENBLAS_ENV = ("OPENBLAS_VERBOSE", "OPENBLAS_NUM_THREADS")
CASCADELAKE = {"family": 6, "model": 85, "required": ("avx512_vnni",), "absent": ("avx512_bf16",)}
R_COLOC_YML = "envs/r_coloc.yml"
BLAS_NOT_CHECKED_REASON = ("no --blas-pinned: the rule's conda env is not envs/r_coloc.yml, so the job runs no R and "
                           "its BLAS is not pinned (Q-158R6G A)")
_PIN_LINE = re.compile(r"^\s*-\s*libopenblas\b(.*)$")
_PIN_EXACT = re.compile(r"^=([0-9][0-9A-Za-z.]*)\s*(#.*)?$")
_PROBE = ("import ctypes,sys\n"
          "l=ctypes.CDLL(sys.argv[1]); l.openblas_get_config.restype=ctypes.c_char_p; "
          "l.openblas_get_corename.restype=ctypes.c_char_p\n"
          "print(l.openblas_get_config().decode()); print(l.openblas_get_corename().decode())\n")


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


def libopenblas_pin(repo):
    """The version of the single `- libopenblas=<version>` dependency line of envs/r_coloc.yml."""
    lines = [m.group(1) for ln in (Path(repo) / R_COLOC_YML).read_text().splitlines() if (m := _PIN_LINE.match(ln))]
    exact = [m.group(1) for rest in lines if (m := _PIN_EXACT.match(rest.rstrip()))]
    if len(lines) != 1 or len(exact) != 1:
        raise JobGuardError(f"{R_COLOC_YML} must have exactly one `- libopenblas=<version>` line, found {len(lines)} "
                            f"libopenblas line(s)")
    return exact[0]


def default_blas_probe(library):
    """(openblas_get_config, openblas_get_corename) of `library`, called in a fresh `sys.executable -I` process (the
    guard's own interpreter; the r_coloc env has no python3), so the guard never loads that OpenBLAS itself."""
    out = subprocess.run([sys.executable, "-I", "-c", _PROBE, library], capture_output=True, text=True, check=True)
    config, corename = out.stdout.splitlines()[:2]
    return config, corename


def default_r_blas_probe(rscript):
    """The BLAS library R reports, in its own process (extSoftVersion()[["BLAS"]])."""
    return subprocess.run([rscript, "--vanilla", "-e", 'cat(extSoftVersion()[["BLAS"]])'], capture_output=True,
                          text=True, check=True).stdout.strip()


def blas_facts(prefix, probe=None, r_probe=None):
    """What the conda env at `prefix` loads: conda-meta libopenblas versions, the realpaths of lib/libblas.so.3 and
    lib/liblapack.so.3, the runtime config and corename of the libblas library and the BLAS R reports."""
    facts = {"prefix": prefix}
    if not prefix:
        return facts
    root = Path(prefix)
    versions = []
    for f in sorted((root / "conda-meta").glob("libopenblas-*.json")):
        try:
            m = json.loads(f.read_text())
        except (OSError, ValueError) as e:
            versions.append(f"unreadable {f.name}: {e}")
            continue
        if m.get("name") == "libopenblas":
            versions.append(str(m.get("version")))
    facts["conda_meta_versions"] = versions
    for so in ("libblas.so.3", "liblapack.so.3"):
        p = root / "lib" / so
        facts[so] = os.path.realpath(p) if p.exists() else None
    facts["config"] = facts["corename"] = facts["probe_error"] = None
    if facts["libblas.so.3"]:
        try:
            facts["config"], facts["corename"] = (probe or default_blas_probe)(facts["libblas.so.3"])
        except (OSError, ValueError, subprocess.CalledProcessError) as e:
            facts["probe_error"] = repr(e)
    rscript = root / "bin" / "Rscript"
    facts["rscript"] = str(rscript) if rscript.is_file() else None
    facts["r_blas"] = facts["r_blas_error"] = None
    if facts["rscript"]:
        try:
            facts["r_blas"] = (r_probe or default_r_blas_probe)(facts["rscript"])
        except (OSError, subprocess.CalledProcessError) as e:
            facts["r_blas_error"] = repr(e)
    return facts


def blas_violations(facts, pin):
    """Every way `facts` differs from the pinned OpenBLAS (one distinct message per check); [] = pinned."""
    prefix = facts.get("prefix")
    if not prefix:
        return ["CONDA_PREFIX is unset: the job's conda env, and so its BLAS, is unknown"]
    out = []
    want = os.path.realpath(Path(prefix) / "lib" / f"libopenblasp-r{pin}.so")
    versions = facts["conda_meta_versions"]
    if len(versions) != 1:
        out.append(f"conda-meta has {len(versions)} libopenblas records {versions}, not one at pin {pin}")
    elif versions[0] != pin:
        out.append(f"conda-meta libopenblas version {versions[0]} != pin {pin}")
    if not os.path.isfile(want):
        out.append(f"the pinned library {want} does not exist")
    for so in ("libblas.so.3", "liblapack.so.3"):
        if facts[so] != want:
            out.append(f"lib/{so} resolves to {facts[so]}, not the pinned {want}")
    config = facts["config"]
    tokens = config.split() if config else []
    if len(tokens) < 2 or tokens[0] != "OpenBLAS" or tokens[1] != pin:
        out.append(f"OpenBLAS runtime version of {facts['libblas.so.3']}: config {config!r} is not version {pin}"
                   + (f" ({facts['probe_error']})" if facts["probe_error"] else ""))
    if not facts["rscript"]:
        out.append(f"{prefix}/bin/Rscript is missing: the BLAS R loads cannot be checked")
    elif not facts["r_blas"] or os.path.realpath(facts["r_blas"]) != want:
        out.append(f"R reports BLAS {facts['r_blas']!r}, not the pinned {want}"
                   + (f" ({facts['r_blas_error']})" if facts["r_blas_error"] else ""))
    return out


def _ld_flags(arm, cfg):
    from ld_read_path import ld_allele_aware, ld_file_authoritative
    from ta_r4.arms import arm_ancestries

    return {a: {"ld_authoritative": ld_file_authoritative(a, cfg), "ld_allele_aware": ld_allele_aware(a, cfg)}
            for a in arm_ancestries(arm)}


def check(repo, arm, digest, *, environ, cpuinfo, record_dir, label, blas_pinned, blas_probe=None, r_blas_probe=None):
    """Lock gate first (raises LockGateError), then digest, CPU, kernel env and, if blas_pinned, the OpenBLAS of
    $CONDA_PREFIX against the envs/r_coloc.yml pin (raise JobGuardError); on success writes
    <record_dir>/<SLURM_JOB_ID or local>.<label>.json and returns the record. blas_pinned=False reads no BLAS."""
    r4_lock_gate.check_lock_gate(Path(repo), "production")
    if not label or "/" in label or label.startswith("."):
        raise JobGuardError(f"label {label!r}: must be a non-empty file-name component")
    if blas_pinned is not True and blas_pinned is not False:
        raise JobGuardError(f"blas_pinned {blas_pinned!r}: must be True or False")
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
    if blas_pinned:
        pin = libopenblas_pin(repo)
        facts = blas_facts(environ.get("CONDA_PREFIX"), blas_probe, r_blas_probe)
        bad = blas_violations(facts, pin)
        if bad:
            raise JobGuardError(f"BLAS is not the libopenblas {pin} pinned in {R_COLOC_YML}: " + "; ".join(bad))
        blas = {"status": "pinned", "version": pin, "library": facts["libblas.so.3"], "config": facts["config"],
                "corename": facts["corename"], "r_blas": facts["r_blas"]}
    else:
        blas = {"status": "not_checked", "reason": BLAS_NOT_CHECKED_REASON}
    cpu = _cpu_summary(cpus[0])
    job = environ.get("SLURM_JOB_ID") or "local"
    rec = {
        "label": label, "arm": arm, "host": socket.gethostname(), "slurm_job_id": environ.get("SLURM_JOB_ID"),
        "cpu": {"family": cpu["family"], "model": cpu["model"], "model_name": cpu["model_name"], "n_processors": len(cpus),
                "avx512_vnni": "avx512_vnni" in cpu["flags"], "avx512_bf16": "avx512_bf16" in cpu["flags"]},
        "checked": {"lock_gate": True, "config_digest": True, "cpu_cascadelake": True, "kernel_env": True,
                    "blas_pinned": True if blas_pinned else "not_checked"},
        "blas": blas,
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
    c.add_argument("--blas-pinned", action="store_true")
    args = ap.parse_args(argv)
    repo = Path(__file__).resolve().parents[3]  # as r4_lock_gate.main
    rd = Path(args.record_dir)
    try:
        with open("/proc/cpuinfo") as fh:
            cpuinfo = fh.read()
        rec = check(repo, args.arm, args.config_sha256, environ=dict(os.environ), cpuinfo=cpuinfo,
                    record_dir=rd if rd.is_absolute() else repo / rd, label=args.label, blas_pinned=args.blas_pinned)
    except LockGateError as e:
        print(f"LockGateError: {e}", file=sys.stderr)
        return 1
    except JobGuardError as e:
        print(f"JobGuardError: {e}", file=sys.stderr)
        return 1
    print(f"job guard OK (lock gate, config {rec['config_sha256'][:12]}, {rec['cpu']['model_name']}, "
          f"blas {rec['blas']['status']}, label {args.label})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
