"""Minimal git repo copied from the WORKING TREE for gate dry-runs. Never copies the sentinel or data/."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SENTINEL_NAME = "OSF-R4-POSTED.json"
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
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", SENTINEL_NAME)
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
    assert not list(repo.rglob(SENTINEL_NAME))
    (repo / ".gitignore").write_text("/data/\n/.snakemake/\n")
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fixture from working tree")
    return repo
