"""OSF gate (D-05, D-27, B5): one online verification per fire, offline memoized in-job check."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

from .conftest import REPO_ROOT

from ta_r4 import r4_osf_gate as g
from ta_r4.r4_osf_gate import OsfGateError, check_osf_gate, verify_online

NOW = datetime(2026, 12, 1, tzinfo=timezone.utc)
AMEND_REL = ".planning/amendments/R4_PUBLIC_fixture.md"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git(repo, *args):
    r = subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "-c", "commit.gpgsign=false", *args], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def head(repo):
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture(autouse=True)
def _clear():
    g._clear_cache()
    yield
    g._clear_cache()


def _repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".planning/amendments").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "README").write_text("fixture\n")
    (repo / AMEND_REL).write_text("# R4 amendment (fixture)\n")
    git(repo, "add", "README", AMEND_REL)
    git(repo, "commit", "-q", "-m", "init")
    return repo


def _sentinel_doc(repo, **over):
    doc = {
        "osf_url": "https://osf.io/az52u/files/fixture",
        "osf_file_guid": "fxgid",
        "posted_utc": "2026-11-01T12:00:00Z",
        "amendment_path": AMEND_REL,
        "amendment_sha256": sha((repo / AMEND_REL).read_bytes()),
        "head_sha": head(repo),
    }
    doc.update(over)
    return doc


def _write_sentinel(repo, doc=None, commit=True, **over):
    doc = doc if doc is not None else _sentinel_doc(repo, **over)
    p = repo / g.SENTINEL_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=1) + "\n")
    if commit:
        git(repo, "add", g.SENTINEL_REL)
        git(repo, "commit", "-q", "-m", "sentinel")
    return doc


def _fake_fetch(repo, node="az52u", sha256=None, calls=None):
    def fetch(guid):
        if calls is not None:
            calls.append(guid)
        s = sha256 or sha((repo / AMEND_REL).read_bytes())
        raw = json.dumps({"data": {"id": guid, "attributes": {"extra": {"hashes": {"sha256": s}}}}}).encode()
        return {"sha256": s, "md5": "0" * 32, "date_created": "2026-11-01T12:00:00Z",
                "target_node": node, "raw": raw}
    return fetch


@pytest.fixture
def posted(tmp_path):
    """Committed amendment + sentinel; receipt written by verify_online with a fake fetch."""
    repo = _repo(tmp_path)
    _write_sentinel(repo)
    receipt = verify_online(repo, fetch=_fake_fetch(repo), now=NOW)
    g._clear_cache()
    return repo, receipt


def _receipt_path(repo):
    return repo / g.RECEIPT_DIR_REL / f"osf_receipt_{head(repo)}.json"


def _edit_receipt(repo, **over):
    p = _receipt_path(repo)
    doc = json.loads(p.read_text())
    doc.update(over)
    p.write_text(json.dumps(doc))


def _raises(repo, needle, stage="production"):
    with pytest.raises(OsfGateError) as ei:
        check_osf_gate(repo, stage, now=NOW)
    assert needle in str(ei.value), str(ei.value)
    return str(ei.value)


# --- stage handling -----------------------------------------------------------------------------

def test_repro_is_not_gated(tmp_path):
    repo = _repo(tmp_path)
    assert check_osf_gate(repo, "repro", now=NOW) is None


@pytest.mark.parametrize("stage", ["", "prod", "Production", "none", None])
def test_unknown_stage_raises_valueerror(tmp_path, stage):
    with pytest.raises(ValueError):
        check_osf_gate(_repo(tmp_path), stage, now=NOW)


# --- local checks (a)-(g) -----------------------------------------------------------------------

def test_a_sentinel_absent(tmp_path):
    _raises(_repo(tmp_path), "sentinel absent")


def test_b_sentinel_untracked(tmp_path):
    repo = _repo(tmp_path)
    _write_sentinel(repo, commit=False)
    _raises(repo, "sentinel untracked")


def test_c_sentinel_uncommitted_changes(tmp_path):
    repo = _repo(tmp_path)
    doc = _write_sentinel(repo)
    doc["osf_url"] = "https://osf.io/az52u/files/other"
    _write_sentinel(repo, doc=doc, commit=False)
    _raises(repo, "uncommitted changes")


@pytest.mark.parametrize("key", ["osf_url", "osf_file_guid", "posted_utc", "amendment_path",
                                 "amendment_sha256", "head_sha"])
def test_d_missing_key(tmp_path, key):
    repo = _repo(tmp_path)
    doc = _sentinel_doc(repo)
    del doc[key]
    _write_sentinel(repo, doc=doc)
    _raises(repo, f"missing key {key}")


def test_e_amendment_untracked(tmp_path):
    repo = _repo(tmp_path)
    (repo / ".planning/amendments/untracked.md").write_text("x\n")
    _write_sentinel(repo, amendment_path=".planning/amendments/untracked.md",
                    amendment_sha256=sha(b"x\n"))
    _raises(repo, "amendment untracked")


def test_e_amendment_sha_mismatch(tmp_path):
    repo = _repo(tmp_path)
    _write_sentinel(repo, amendment_sha256="f" * 64)
    _raises(repo, "amendment sha256")


def test_e_amendment_working_copy_edited(tmp_path):
    repo = _repo(tmp_path)
    _write_sentinel(repo)
    (repo / AMEND_REL).write_text("# edited after posting\n")
    _raises(repo, "amendment sha256")


@pytest.mark.parametrize("posted", ["2027-01-01T00:00:00Z", "not-a-date", "2026-13-01T00:00:00Z", ""])
def test_f_posted_utc_future_or_unparseable(tmp_path, posted):
    repo = _repo(tmp_path)
    _write_sentinel(repo, posted_utc=posted)
    _raises(repo, "posted_utc")


def test_g_head_sha_not_ancestor(tmp_path):
    repo = _repo(tmp_path)
    _write_sentinel(repo, head_sha="1" * 40)
    _raises(repo, "not an ancestor")


# --- receipt checks (k)-(o) ---------------------------------------------------------------------

def test_positive_control(posted):
    repo, receipt = posted
    assert check_osf_gate(repo, "production", now=NOW) is None
    assert receipt["head_sha"] == head(repo)
    assert set(receipt) >= {"sentinel_sha256", "amendment_sha256", "osf_reported_sha256", "osf_target_node",
                            "head_sha", "checked_utc", "host", "api_response_sha256"}
    raw = (repo / g.RECEIPT_DIR_REL / f"osf_api_response_{head(repo)}.json").read_bytes()
    assert receipt["api_response_sha256"] == sha(raw)


def test_k_no_receipt_for_head(posted):
    repo, _ = posted
    (repo / "README").write_text("moved\n")
    git(repo, "commit", "-qam", "move HEAD")
    _raises(repo, "no receipt")


def test_k_no_receipt_at_all(tmp_path):
    repo = _repo(tmp_path)
    _write_sentinel(repo)
    _raises(repo, "no receipt")


def test_l_receipt_sentinel_sha(posted):
    repo, _ = posted
    _edit_receipt(repo, sentinel_sha256="a" * 64)
    _raises(repo, "sentinel_sha256")


@pytest.mark.parametrize("field", ["amendment_sha256", "osf_reported_sha256"])
def test_m_receipt_amendment_sha(posted, field):
    repo, _ = posted
    _edit_receipt(repo, **{field: "b" * 64})
    _raises(repo, field)


def test_n_receipt_target_node(posted):
    repo, _ = posted
    _edit_receipt(repo, osf_target_node="zzzzz")
    _raises(repo, "osf_target_node")


def test_o_receipt_head_sha(posted):
    repo, _ = posted
    _edit_receipt(repo, head_sha="c" * 40)
    _raises(repo, "receipt head_sha")


def test_receipt_api_response_tampered(posted):
    repo, _ = posted
    (repo / g.RECEIPT_DIR_REL / f"osf_api_response_{head(repo)}.json").write_bytes(b"{}")
    _raises(repo, "api_response")


# --- verify_online (h)-(j) ----------------------------------------------------------------------

def test_verify_online_runs_local_checks_before_fetch(tmp_path):
    repo, calls = _repo(tmp_path), []
    with pytest.raises(OsfGateError, match="sentinel absent"):
        verify_online(repo, fetch=_fake_fetch(repo, calls=calls), now=NOW)
    assert calls == []


def test_verify_online_fetches_once(tmp_path):
    repo, calls = _repo(tmp_path), []
    _write_sentinel(repo)
    verify_online(repo, fetch=_fake_fetch(repo, calls=calls), now=NOW)
    assert calls == ["fxgid"]


def test_h_api_sha_mismatch(tmp_path):
    repo = _repo(tmp_path)
    _write_sentinel(repo)
    with pytest.raises(OsfGateError, match="OSF-reported sha256"):
        verify_online(repo, fetch=_fake_fetch(repo, sha256="d" * 64), now=NOW)
    assert not (repo / g.RECEIPT_DIR_REL).exists() or not list((repo / g.RECEIPT_DIR_REL).iterdir())


def test_i_fetch_raises_fails_closed(tmp_path):
    repo = _repo(tmp_path)
    _write_sentinel(repo)

    def down(guid):
        raise OSError("network unreachable")
    with pytest.raises(OsfGateError, match="fail closed"):
        verify_online(repo, fetch=down, now=NOW)


def test_j_api_target_node(tmp_path):
    repo = _repo(tmp_path)
    _write_sentinel(repo)
    with pytest.raises(OsfGateError, match="target node"):
        verify_online(repo, fetch=_fake_fetch(repo, node="qqqqq"), now=NOW)


def test_parse_osf_file_response():
    raw = json.dumps({"data": {"id": "k8w7n", "attributes": {
        "date_created": "2026-04-25T15:00:00.000000Z",
        "extra": {"hashes": {"sha256": "e" * 64, "md5": "f" * 32}}},
        "relationships": {"target": {"data": {"id": "az52u", "type": "nodes"},
                                     "links": {"related": {"href": "https://api.osf.io/v2/nodes/az52u/"}}}}}}).encode()
    d = g.parse_osf_file(raw)
    assert d == {"sha256": "e" * 64, "md5": "f" * 32, "date_created": "2026-04-25T15:00:00.000000Z",
                 "target_node": "az52u", "raw": raw}


def test_parse_osf_file_target_from_href_only():
    raw = json.dumps({"data": {"attributes": {"extra": {"hashes": {"sha256": "e" * 64}}},
                               "relationships": {"target": {"links": {"related": {
                                   "href": "https://api.osf.io/v2/nodes/az52u/"}}}}}}).encode()
    assert g.parse_osf_file(raw)["target_node"] == "az52u"


# --- memoization, offline, no bypass -------------------------------------------------------------

def test_memoized_zero_subprocess_calls_on_second_check(posted, monkeypatch):
    repo, _ = posted
    check_osf_gate(repo, "production", now=NOW)
    n = {"calls": 0}
    real = g.subprocess.run

    def counting(*a, **k):
        n["calls"] += 1
        return real(*a, **k)
    monkeypatch.setattr(g.subprocess, "run", counting)
    check_osf_gate(repo, "production", now=NOW)
    check_osf_gate(str(repo), "production", now=NOW)
    assert n["calls"] == 0


def test_failure_is_not_memoized(tmp_path):
    repo = _repo(tmp_path)
    _raises(repo, "sentinel absent")
    _raises(repo, "sentinel absent")


def test_offline_path_makes_no_network_call(posted, monkeypatch):
    import socket
    import urllib.request
    repo, _ = posted

    def boom(*a, **k):
        raise AssertionError("network call from the offline gate")
    monkeypatch.setattr(urllib.request, "urlopen", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(g, "fetch_osf_file", boom)
    assert check_osf_gate(repo, "production", now=NOW) is None


def test_no_environ_or_getenv_in_module():
    tree = ast.parse(Path(g.__file__).read_text())
    hits = [n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr in ("environ", "getenv")]
    names = [n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id in ("environ", "getenv")]
    imports = [a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names
               if a.name in ("environ", "getenv")]
    assert hits == names == imports == []


BYPASS_ENV = {"R4_GATE_BYPASS": "1", "R4_STAGE": "repro", "OSF_GATE_SKIP": "1"}


def test_env_vars_do_not_bypass_refusal(tmp_path, monkeypatch):
    repo = _repo(tmp_path)
    for k, v in BYPASS_ENV.items():
        monkeypatch.setenv(k, v)
    _raises(repo, "sentinel absent")


def test_env_vars_do_not_change_pass(posted, monkeypatch):
    repo, _ = posted
    for k, v in BYPASS_ENV.items():
        monkeypatch.setenv(k, v)
    assert check_osf_gate(repo, "production", now=NOW) is None
    _edit_receipt(repo, head_sha="c" * 40)
    g._clear_cache()
    _raises(repo, "receipt head_sha")


def test_signature_has_no_bypass_parameter():
    sig = inspect.signature(check_osf_gate)
    assert list(sig.parameters) == ["repo_root", "stage", "now"]
    assert sig.parameters["now"].kind is inspect.Parameter.KEYWORD_ONLY
    vsig = inspect.signature(verify_online)
    assert list(vsig.parameters) == ["repo_root", "fetch", "now"]
    assert all(vsig.parameters[p].kind is inspect.Parameter.KEYWORD_ONLY for p in ("fetch", "now"))


def test_constants():
    assert g.SENTINEL_REL == ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/OSF-R4-POSTED.json"
    assert g.RECEIPT_DIR_REL == "data/r4/gate"
    assert g.OSF_NODE == "az52u"
