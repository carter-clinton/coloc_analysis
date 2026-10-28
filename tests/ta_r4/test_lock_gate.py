"""Offline git-lock production gate (DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf)."""
from __future__ import annotations

import ast
import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ta_r4 import r4_lock_gate as g
from ta_r4.r4_lock_gate import LOCK_RECORD_REL, LOCKED_PATHS, SIGNOFF_REL, LockGateError, check_lock_gate
from ta_r4.signoff import record_signoff

from .conftest import REPO_ROOT
from .fixtures.make_fixture_repo import git, write_fixture_lock

SIGNOFF_FILE = f"{SIGNOFF_REL}/W4b-T3.yaml"


@pytest.fixture(autouse=True)
def _clear():
    g._clear_cache()
    yield
    g._clear_cache()


def _repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "src/python/ta_r4").mkdir(parents=True)
    (repo / "config/ta_r4").mkdir(parents=True)
    (repo / "README").write_text("fixture\n")
    (repo / "src/python/ta_r4/arms.py").write_text("ARMS = {}\n")
    for n in g.LOCKABLE:
        (repo / f"config/ta_r4/{n}.yaml").write_text("locked: false\n")
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "init")
    return repo


@pytest.fixture
def locked(tmp_path):
    repo = _repo(tmp_path)
    sha = write_fixture_lock(repo)
    return repo, sha


def _raises(repo, needle, stage="production"):
    with pytest.raises(LockGateError) as ei:
        check_lock_gate(repo, stage)
    assert needle in str(ei.value), str(ei.value)
    return str(ei.value)


def _commit_record(repo, text):
    (repo / LOCK_RECORD_REL).parent.mkdir(parents=True, exist_ok=True)
    (repo / LOCK_RECORD_REL).write_text(text)
    git(repo, "add", LOCK_RECORD_REL)
    git(repo, "commit", "-q", "-m", "record")


# --- stage handling ---------------------------------------------------------------------------

def test_positive_control(locked):
    repo, sha = locked
    assert check_lock_gate(repo, "production") is None
    assert g.read_lock_sha(repo) == sha


def test_repro_is_not_gated(tmp_path):
    assert check_lock_gate(_repo(tmp_path), "repro") is None


@pytest.mark.parametrize("stage", ["", "prod", "Production", None])
def test_unknown_stage_raises_valueerror(tmp_path, stage):
    with pytest.raises(ValueError):
        check_lock_gate(_repo(tmp_path), stage)


# --- lock record (a)-(d) ----------------------------------------------------------------------

def test_a_record_absent(tmp_path):
    _raises(_repo(tmp_path), "(a) lock record absent")


def test_b_record_untracked(tmp_path):
    repo = _repo(tmp_path)
    (repo / LOCK_RECORD_REL).parent.mkdir(parents=True)
    (repo / LOCK_RECORD_REL).write_text(json.dumps({"lock_sha": git(repo, "rev-parse", "HEAD")}))
    _raises(repo, "(b) lock record untracked")


def test_c_record_uncommitted_changes(locked):
    repo, _ = locked
    (repo / LOCK_RECORD_REL).write_text(json.dumps({"lock_sha": "0" * 40}))
    _raises(repo, "(c) lock record has uncommitted changes")


@pytest.mark.parametrize("text", ["not json", "[1, 2]", "{}", '{"lock_sha": "abcdef1"}', "UPPER"])
def test_d_bad_lock_sha(locked, text):
    repo, sha = locked
    if text == "UPPER":
        text = json.dumps({"lock_sha": sha.upper()})
    _commit_record(repo, text)
    msg = _raises(repo, "(d)")
    assert "lock_sha" in msg


# --- ancestry and locked configs (e)-(f) ------------------------------------------------------

def test_e_side_branch_not_ancestor(locked):
    repo, _ = locked
    git(repo, "checkout", "-q", "-b", "side", "HEAD~1")
    (repo / "README").write_text("side\n")
    git(repo, "commit", "-qam", "side")
    side = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-")
    _commit_record(repo, json.dumps({"lock_sha": side}))
    _raises(repo, "(e)")
    _raises(repo, "not an ancestor of HEAD")


def test_e_nonexistent_sha(locked):
    repo, _ = locked
    _commit_record(repo, json.dumps({"lock_sha": "1" * 40}))
    _raises(repo, "not an ancestor of HEAD")


def test_f_config_not_locked(tmp_path):
    repo = _repo(tmp_path)
    write_fixture_lock(repo, locked=False)
    _raises(repo, "not locked: true")


@pytest.mark.parametrize("name", g.LOCKABLE)
def test_f_one_config_not_locked(tmp_path, name):
    repo = _repo(tmp_path)
    write_fixture_lock(repo)
    p = repo / f"config/ta_r4/{name}.yaml"
    p.write_text("locked: false\n")
    git(repo, "commit", "-qam", "unlock one")
    lock = git(repo, "rev-parse", "HEAD")
    _commit_record(repo, json.dumps({"lock_sha": lock}))
    _raises(repo, f"config/ta_r4/{name}.yaml is not locked: true")


# --- drift (g)-(h) ----------------------------------------------------------------------------

def test_g_committed_drift(locked):
    repo, _ = locked
    (repo / "src/python/ta_r4/arms.py").write_text("ARMS = {'x': 1}\n")
    git(repo, "commit", "-qam", "edit after lock")
    msg = _raises(repo, "(g)")
    assert "drifted" in msg and "src/python/ta_r4/arms.py" in msg


def test_h_working_copy_drift(locked):
    repo, _ = locked
    (repo / "src/python/ta_r4/arms.py").write_text("ARMS = {'x': 1}\n")
    msg = _raises(repo, "(h)")
    assert "drifted" in msg and "working copy" in msg and "arms.py" in msg


def test_h_untracked_drift(locked):
    repo, _ = locked
    (repo / "src/python/ta_r4/new_mod.py").write_text("X = 1\n")
    msg = _raises(repo, "(h)")
    assert "drifted" in msg and "untracked" in msg and "new_mod.py" in msg


def test_edit_outside_locked_paths_is_not_drift(locked):
    repo, _ = locked
    (repo / "README").write_text("edited\n")
    (repo / "notes.txt").write_text("untracked\n")
    assert check_lock_gate(repo, "production") is None
    git(repo, "add", "notes.txt")
    git(repo, "commit", "-qam", "outside")
    g._clear_cache()
    assert check_lock_gate(repo, "production") is None


# --- Carter's W4b-T3 confirmation (i) ---------------------------------------------------------

def test_i_signoff_absent(locked):
    repo, _ = locked
    git(repo, "rm", "-q", SIGNOFF_FILE)
    git(repo, "commit", "-q", "-m", "drop sign-off")
    _raises(repo, "(i) W4b-T3")


def test_i_signoff_untracked(locked):
    repo, _ = locked
    git(repo, "rm", "-q", "--cached", SIGNOFF_FILE)
    git(repo, "commit", "-q", "-m", "untrack sign-off")
    assert (repo / SIGNOFF_FILE).is_file()
    _raises(repo, "(i) W4b-T3 sign-off untracked")


def test_i_signoff_lock_sha_mismatch(locked):
    repo, _ = locked
    git(repo, "rm", "-q", SIGNOFF_FILE)
    import datetime as dt
    raw = f"carter-approved {dt.date.today().isoformat()}\nlock_sha: {'b' * 40}\n"
    record_signoff("W4b-T3", raw, min_date="2026-10-01", signoff_dir=repo / SIGNOFF_REL)
    git(repo, "add", SIGNOFF_FILE)
    git(repo, "commit", "-q", "-m", "other sha")
    _raises(repo, "(i) W4b-T3 lock_sha")


def test_i_signoff_tampered(locked):
    repo, _ = locked
    p = repo / SIGNOFF_FILE
    p.write_text(p.read_text().replace("lock_sha:", "lock_sha:  "))
    git(repo, "commit", "-qam", "tamper")
    _raises(repo, "(i) W4b-T3")


# --- memoization, offline, no bypass ----------------------------------------------------------

def test_memoized_zero_subprocess_calls_on_second_check(locked, monkeypatch):
    repo, _ = locked
    check_lock_gate(repo, "production")
    n = {"calls": 0}
    real = g.subprocess.run

    def counting(*a, **k):
        n["calls"] += 1
        return real(*a, **k)
    monkeypatch.setattr(g.subprocess, "run", counting)
    check_lock_gate(repo, "production")
    check_lock_gate(str(repo), "production")
    assert n["calls"] == 0


def test_failure_is_not_memoized(tmp_path):
    repo = _repo(tmp_path)
    _raises(repo, "lock record absent")
    write_fixture_lock(repo)
    g._head_cached.cache_clear()
    assert check_lock_gate(repo, "production") is None


def test_no_network_call(locked, monkeypatch):
    import socket
    import urllib.request
    repo, _ = locked

    def boom(*a, **k):
        raise AssertionError("network call from the lock gate")
    monkeypatch.setattr(socket.socket, "connect", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(urllib.request, "urlopen", boom)
    assert check_lock_gate(repo, "production") is None
    (repo / "src/python/ta_r4/arms.py").write_text("ARMS = {'x': 1}\n")
    g._clear_cache()
    _raises(repo, "drifted")


def _tree():
    return ast.parse(Path(g.__file__).read_text())


def test_no_network_imports():
    mods = set()
    for n in ast.walk(_tree()):
        if isinstance(n, ast.Import):
            mods |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module.split(".")[0])
    assert mods, "AST scan found no imports"
    assert not mods & {"urllib", "socket", "http", "requests", "urllib3", "httpx"}


def test_no_environ_or_getenv_in_module():
    tree = _tree()
    hits = [n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr in ("environ", "getenv")]
    names = [n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id in ("environ", "getenv")]
    imports = [a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names
               if a.name in ("environ", "getenv")]
    assert hits == names == imports == []


BYPASS_ENV = {"R4_GATE_BYPASS": "1", "R4_STAGE": "repro", "OSF_GATE_SKIP": "1", "OSF_TOKEN": "x",
              "GATE_OPEN": "1"}


def test_env_vars_do_not_bypass_refusal(tmp_path, monkeypatch):
    for k, v in BYPASS_ENV.items():
        monkeypatch.setenv(k, v)
    _raises(_repo(tmp_path), "lock record absent")


def test_env_vars_do_not_change_pass(locked, monkeypatch):
    repo, _ = locked
    for k, v in BYPASS_ENV.items():
        monkeypatch.setenv(k, v)
    assert check_lock_gate(repo, "production") is None
    (repo / "src/python/ta_r4/arms.py").write_text("ARMS = {'x': 1}\n")
    g._clear_cache()
    _raises(repo, "drifted")


def test_signature_has_no_bypass_parameter():
    assert list(inspect.signature(check_lock_gate).parameters) == ["repo_root", "stage"]


def test_constants():
    assert LOCK_RECORD_REL == ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/R4-LOCK.json"
    assert g.LOCKABLE == ("coloc_priors", "decision_rules", "simulation")
    assert "src/python/ta_r4" in LOCKED_PATHS and "Snakefile.ta_r4" in LOCKED_PATHS


# --- CLI and the real repo --------------------------------------------------------------------

def _cli(*args):
    return subprocess.run([sys.executable, "-m", "ta_r4.r4_lock_gate", *args], cwd=REPO_ROOT / "src/python",
                          capture_output=True, text=True)


def test_cli_paths():
    r = _cli("paths")
    assert r.returncode == 0
    assert tuple(r.stdout.splitlines()) == LOCKED_PATHS


def test_cli_repro_passes():
    assert _cli("check", "--stage", "repro").returncode == 0


def test_real_repo_state():
    """Conditional: absent/untracked record -> CLI exit 1; tracked -> read_lock_sha succeeds."""
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", LOCK_RECORD_REL], cwd=REPO_ROOT,
                             capture_output=True).returncode == 0
    if not tracked:
        r = _cli("check", "--stage", "production")
        assert r.returncode == 1
        want = "lock record absent" if not (REPO_ROOT / LOCK_RECORD_REL).exists() else "lock record untracked"
        assert want in r.stderr and "LockGateError" in r.stderr, r.stderr
    else:
        g.read_lock_sha(REPO_ROOT)
