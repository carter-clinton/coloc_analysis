"""Minimal git repo copied from the WORKING TREE for gate dry-runs. Never copies the lock record or data/."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
LOCK_RECORD_NAME = "R4-LOCK.json"
COPY_FILES = ("Snakefile.ta_r4", "config/pipeline.yaml")
COPY_DIRS = ("config/ta_r4", "src/python", "envs")
GIT_ID = ["-c", "user.name=R4 Fixture", "-c", "user.email=r4-fixture@example.invalid", "-c", "commit.gpgsign=false"]


def git(repo, *args):
    r = subprocess.run(["git", *GIT_ID, *args], cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args}: {r.stderr}")
    return r.stdout.strip()


def make_fixture_repo(tmp_path) -> Path:
    repo = Path(tmp_path) / "fixture_repo"
    repo.mkdir()
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", LOCK_RECORD_NAME)
    for f in COPY_FILES:
        (repo / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / f, repo / f)
    for d in COPY_DIRS:
        shutil.copytree(REPO_ROOT / d, repo / d, ignore=ignore, symlinks=True)
    rules = repo / "src/snakemake/rules"
    rules.mkdir(parents=True)
    for smk in sorted((REPO_ROOT / "src/snakemake/rules").glob("ta_r4_*.smk")):
        shutil.copy2(smk, rules / smk.name)
    assert not (repo / "data").exists()
    assert not list(repo.rglob(LOCK_RECORD_NAME))
    (repo / ".gitignore").write_text("/data/\n/.snakemake/\n__pycache__/\n")
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fixture from working tree")
    return repo


def write_fixture_lock(repo, *, locked=True) -> str:
    """Fixture only (tmp_path): a lock commit of the three configs, then R4-LOCK.json + a W4b-T3 sign-off."""
    import datetime as dt
    import json
    import re

    from ta_r4.r4_lock_gate import LOCK_RECORD_REL, LOCKABLE, SIGNOFF_REL
    from ta_r4.signoff import record_signoff

    repo = Path(repo)
    line = f"locked: {'true' if locked else 'false'}"
    cfgs = []
    for n in LOCKABLE:
        rel = f"config/ta_r4/{n}.yaml"
        p = repo / rel
        text = p.read_text() if p.exists() else ""
        text, k = re.subn(r"(?m)^locked:.*$", line, text)
        if not k:
            text += ("" if text.endswith("\n") or not text else "\n") + line + "\n"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        cfgs.append(rel)
    git(repo, "add", *cfgs)
    git(repo, "commit", "-q", "--allow-empty", "-m", "fixture lock commit")
    sha = git(repo, "rev-parse", "HEAD")
    (repo / LOCK_RECORD_REL).parent.mkdir(parents=True, exist_ok=True)
    (repo / LOCK_RECORD_REL).write_text(json.dumps({"lock_sha": sha}, indent=1) + "\n")
    raw = f"carter-approved {dt.date.today().isoformat()}\nlock_sha: {sha}\n"
    (repo / SIGNOFF_REL / "W4b-T3.yaml").unlink(missing_ok=True)
    record_signoff("W4b-T3", raw, min_date="2026-10-01", signoff_dir=repo / SIGNOFF_REL)
    git(repo, "add", LOCK_RECORD_REL, f"{SIGNOFF_REL}/W4b-T3.yaml")
    git(repo, "commit", "-q", "-m", "fixture lock record + W4b-T3")
    return sha
