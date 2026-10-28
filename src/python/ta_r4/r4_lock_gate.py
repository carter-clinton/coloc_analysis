"""R4 production gate: the W4b lock commit is an ancestor of HEAD, no locked path drifted, Carter confirmed lock_sha.

Fails closed. Offline: no network, reads no environment variables, no bypass.
"""
from __future__ import annotations

import argparse
import functools
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

from ta_r4.signoff import SignoffError, verify_signoff

PHASE_REL = ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission"
LOCK_RECORD_REL = f"{PHASE_REL}/R4-LOCK.json"
SIGNOFF_REL = f"{PHASE_REL}/signoffs"
SIGNOFF_ID = "W4b-T3"
LOCKABLE = ("coloc_priors", "decision_rules", "simulation")
LOCKED_PATHS = (
    "src/snakemake/scripts/ta_r4",
    "src/python/ta_r4",
    "src/snakemake/rules/ta_r4_*.smk",
    "config/ta_r4",
    "Snakefile.ta_r4",
    "bin/r4_fire.sh",
    "src/legacy/region_analysis/scripts/run_susie_rss.R",
    "src/snakemake/scripts/plink_ld_to_rds.R",
    "src/snakemake/scripts/run_qtl_coloc.R",
    "src/snakemake/scripts/ld_allele_join.R",
    "src/python/assign_tiers.py",
    "src/python/aggregate_qtl_coloc.py",
    "src/python/harmonize_eqtl.py",
    "src/python/harmonize_sqtl.py",
    "src/python/ld_read_path.py",
    "src/python/ld_panel.py",
    "envs",
    f"{PHASE_REL}/manifests/panels_*.tsv",
)
STAGES = ("repro", "production")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class LockGateError(RuntimeError):
    pass


def _git(repo, *args):
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def _git_ok(repo, what, *args) -> str:
    rc, out, err = _git(repo, *args)
    if rc != 0:
        raise LockGateError(f"{what}: git {' '.join(args[:2])} failed: {err.strip()}")
    return out


def _tracked_clean(repo, rel, tag, what):
    if not (Path(repo) / rel).is_file():
        raise LockGateError(f"({tag[0]}) {what} absent: {rel}")
    if _git(repo, "ls-files", "--error-unmatch", "--", rel)[0] != 0:
        raise LockGateError(f"({tag[1]}) {what} untracked: {rel}")
    rc, out, err = _git(repo, "status", "--porcelain", "--", rel)
    if rc != 0 or out.strip():
        raise LockGateError(f"({tag[2]}) {what} has uncommitted changes: {rel}")


def read_lock_sha(repo) -> str:
    """Checks (a)-(d); returns the record's lock_sha."""
    _tracked_clean(repo, LOCK_RECORD_REL, "abc", "lock record")
    try:
        doc = json.loads((Path(repo) / LOCK_RECORD_REL).read_text())
    except ValueError as e:
        raise LockGateError(f"(d) lock record is not JSON, no lock_sha: {e}") from None
    if not isinstance(doc, dict):
        raise LockGateError("(d) lock record is not a JSON object, no lock_sha")
    sha = doc.get("lock_sha")
    if not isinstance(sha, str) or not SHA_RE.match(sha):
        raise LockGateError(f"(d) lock_sha {sha!r} is not a 40-char lowercase hex sha")
    return sha


def _read_head(repo) -> str:
    return _git_ok(repo, "cannot read HEAD", "rev-parse", "HEAD").strip()


def _check(repo):
    sha = read_lock_sha(repo)
    if _git(repo, "merge-base", "--is-ancestor", sha, "HEAD")[0] != 0:
        raise LockGateError(f"(e) lock_sha {sha} is not an ancestor of HEAD")
    for n in LOCKABLE:
        rc, out, _ = _git(repo, "show", f"{sha}:config/ta_r4/{n}.yaml")
        try:
            doc = yaml.safe_load(out) if rc == 0 else None
        except yaml.YAMLError:
            doc = None
        if not isinstance(doc, dict) or doc.get("locked") is not True:
            raise LockGateError(f"(f) config/ta_r4/{n}.yaml is not locked: true at lock_sha {sha}")
    out = _git_ok(repo, "(g)", "diff", "--name-only", sha, "HEAD", "--", *LOCKED_PATHS)
    if out.strip():
        raise LockGateError(f"(g) locked paths drifted since lock_sha {sha} (committed): {out.split()}")
    out = _git_ok(repo, "(h)", "diff", "--name-only", sha, "--", *LOCKED_PATHS)
    if out.strip():
        raise LockGateError(f"(h) locked paths drifted since lock_sha {sha} (working copy): {out.split()}")
    out = _git_ok(repo, "(h)", "ls-files", "--others", "--exclude-standard", "--", *LOCKED_PATHS)
    if out.strip():
        raise LockGateError(f"(h) locked paths drifted since lock_sha {sha} (untracked): {out.split()}")
    _tracked_clean(repo, f"{SIGNOFF_REL}/{SIGNOFF_ID}.yaml", "iii", f"{SIGNOFF_ID} sign-off")
    try:
        fields = verify_signoff(SIGNOFF_ID, signoff_dir=Path(repo) / SIGNOFF_REL)
    except SignoffError as e:
        raise LockGateError(f"(i) {SIGNOFF_ID}: {e}") from None
    if fields.get("lock_sha") != sha:
        raise LockGateError(f"(i) {SIGNOFF_ID} lock_sha {fields.get('lock_sha')!r} != lock record {sha}")


@functools.lru_cache(maxsize=None)
def _head_cached(real: str) -> str:
    return _read_head(real)


@functools.lru_cache(maxsize=None)
def _check_cached(real: str, head: str) -> bool:
    _check(real)
    return True


def _clear_cache():
    _head_cached.cache_clear()
    _check_cached.cache_clear()


def check_lock_gate(repo_root, stage) -> None:
    """'repro' passes; 'production' raises LockGateError unless checks (a)-(i) pass."""
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {STAGES}, got {stage!r}")
    if stage == "repro":
        return None
    real = os.path.realpath(repo_root)
    _check_cached(real, _head_cached(real))
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m ta_r4.r4_lock_gate", description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("check").add_argument("--stage", required=True, choices=STAGES)
    sub.add_parser("paths")
    args = ap.parse_args(argv)
    if args.command == "paths":
        print("\n".join(LOCKED_PATHS))
        return 0
    repo = Path(__file__).resolve().parents[3]
    try:
        check_lock_gate(repo, args.stage)
    except LockGateError as e:
        print(f"LockGateError: {e}", file=sys.stderr)
        return 1
    print(f"lock gate OK (offline, stage={args.stage})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
