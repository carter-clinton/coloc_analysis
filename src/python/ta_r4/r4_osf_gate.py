"""R4 OSF gate (D-05, D-27, B5).

verify_online: submit host, once per production fire; one OSF API call; writes a per-HEAD receipt.
check_osf_gate: offline, memoized per process; every DAG evaluation and LSF job.
Fails closed. Reads no environment variables and has no bypass.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import socket
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SENTINEL_REL = ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/OSF-R4-POSTED.json"
RECEIPT_DIR_REL = "data/r4/gate"
OSF_NODE = "az52u"
OSF_API = "https://api.osf.io/v2/files/{guid}/"
REQUIRED_KEYS = ("osf_url", "osf_file_guid", "posted_utc", "amendment_path", "amendment_sha256", "head_sha")
STAGES = ("repro", "production")


class OsfGateError(RuntimeError):
    pass


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True)


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _now(now):
    return now if now is not None else datetime.now(timezone.utc)


def _parse_utc(s):
    if not isinstance(s, str) or not s:
        raise ValueError(s)
    t = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError(f"{s} has no timezone")
    return t


def _read_head(repo) -> str:
    r = _git(repo, "rev-parse", "HEAD")
    if r.returncode != 0:
        raise OsfGateError(f"cannot read HEAD in {repo}: {r.stderr.decode().strip()}")
    return r.stdout.decode().strip()


def _local_checks(repo, now) -> dict:
    """(a)-(g). Returns the parsed sentinel."""
    repo = Path(repo)
    sp = repo / SENTINEL_REL
    if not sp.is_file():
        raise OsfGateError(f"(a) sentinel absent: {SENTINEL_REL}")
    if _git(repo, "ls-files", "--error-unmatch", "--", SENTINEL_REL).returncode != 0:
        raise OsfGateError(f"(b) sentinel untracked: {SENTINEL_REL}")
    st = _git(repo, "status", "--porcelain", "--", SENTINEL_REL)
    if st.returncode != 0 or st.stdout.strip():
        raise OsfGateError(f"(c) sentinel has uncommitted changes: {SENTINEL_REL}")
    try:
        doc = json.loads(sp.read_text())
    except ValueError as e:
        raise OsfGateError(f"(d) sentinel is not JSON: {e}") from None
    if not isinstance(doc, dict):
        raise OsfGateError("(d) sentinel is not a JSON object")
    for k in REQUIRED_KEYS:
        if k not in doc or doc[k] in (None, ""):
            raise OsfGateError(f"(d) sentinel missing key {k}")
    am = str(doc["amendment_path"])
    if _git(repo, "ls-files", "--error-unmatch", "--", am).returncode != 0:
        raise OsfGateError(f"(e) amendment untracked: {am}")
    blob = _git(repo, "show", f"HEAD:{am}")
    work = (repo / am).read_bytes() if (repo / am).is_file() else None
    if blob.returncode != 0 or _sha256(blob.stdout) != doc["amendment_sha256"] \
            or work is None or _sha256(work) != doc["amendment_sha256"]:
        raise OsfGateError(f"(e) amendment sha256 != sentinel amendment_sha256 ({am}, committed and working copy)")
    try:
        posted = _parse_utc(doc["posted_utc"])
    except (ValueError, TypeError):
        raise OsfGateError(f"(f) posted_utc unparseable: {doc['posted_utc']!r}") from None
    if posted > _now(now):
        raise OsfGateError(f"(f) posted_utc {doc['posted_utc']} is in the future")
    if _git(repo, "merge-base", "--is-ancestor", str(doc["head_sha"]), "HEAD").returncode != 0:
        raise OsfGateError(f"(g) sentinel head_sha {doc['head_sha']} is not an ancestor of HEAD")
    return doc


def _receipt_paths(repo, head):
    d = Path(repo) / RECEIPT_DIR_REL
    return d / f"osf_receipt_{head}.json", d / f"osf_api_response_{head}.json"


def _receipt_checks(repo, doc, head):
    """(k)-(o) plus the raw-response hash."""
    rp, ap = _receipt_paths(repo, head)
    if not rp.is_file():
        raise OsfGateError(f"(k) no receipt for HEAD {head} under {RECEIPT_DIR_REL}; run bin/r4_fire.sh")
    try:
        rc = json.loads(rp.read_text())
    except ValueError as e:
        raise OsfGateError(f"(k) receipt is not JSON: {e}") from None
    s_sha = _sha256((Path(repo) / SENTINEL_REL).read_bytes())
    if rc.get("sentinel_sha256") != s_sha:
        raise OsfGateError("(l) receipt sentinel_sha256 != sha256(sentinel)")
    for f in ("amendment_sha256", "osf_reported_sha256"):
        if rc.get(f) != doc["amendment_sha256"]:
            raise OsfGateError(f"(m) receipt {f} != sentinel amendment_sha256")
    if rc.get("osf_target_node") != OSF_NODE:
        raise OsfGateError(f"(n) receipt osf_target_node {rc.get('osf_target_node')!r} != {OSF_NODE!r}")
    if rc.get("head_sha") != head:
        raise OsfGateError(f"(o) receipt head_sha {rc.get('head_sha')!r} != HEAD {head}")
    if not ap.is_file() or _sha256(ap.read_bytes()) != rc.get("api_response_sha256"):
        raise OsfGateError("receipt api_response_sha256 != sha256(saved API response)")


def parse_osf_file(raw: bytes) -> dict:
    data = json.loads(raw)["data"]
    attrs = data.get("attributes") or {}
    hashes = (attrs.get("extra") or {}).get("hashes") or {}
    target = (data.get("relationships") or {}).get("target") or {}
    node = (target.get("data") or {}).get("id")
    if not node:
        href = ((target.get("links") or {}).get("related") or {}).get("href") or ""
        node = href.rstrip("/").rsplit("/", 1)[-1] or None
    return {"sha256": hashes.get("sha256"), "md5": hashes.get("md5"),
            "date_created": attrs.get("date_created"), "target_node": node, "raw": raw}


def fetch_osf_file(guid: str) -> dict:
    with urllib.request.urlopen(OSF_API.format(guid=guid), timeout=30) as r:
        return parse_osf_file(r.read())


def verify_online(repo_root, *, fetch=fetch_osf_file, now=None) -> dict:
    """Submit host only: local checks, one OSF API call, then write the per-HEAD receipt."""
    repo = Path(repo_root)
    doc = _local_checks(repo, now)
    head = _read_head(repo)
    try:
        api = fetch(str(doc["osf_file_guid"]))
    except Exception as e:  # noqa: BLE001 - any failure fails closed
        raise OsfGateError(f"(i) OSF API fetch failed (fail closed): {type(e).__name__}: {e}") from None
    if api.get("sha256") != doc["amendment_sha256"]:
        raise OsfGateError(f"(h) OSF-reported sha256 {api.get('sha256')!r} != amendment_sha256")
    if api.get("target_node") != OSF_NODE:
        raise OsfGateError(f"(j) OSF target node {api.get('target_node')!r} != {OSF_NODE!r}")
    raw = api["raw"] if isinstance(api.get("raw"), bytes) else json.dumps(api.get("raw")).encode()
    receipt = {
        "sentinel_sha256": _sha256((repo / SENTINEL_REL).read_bytes()),
        "amendment_sha256": doc["amendment_sha256"],
        "osf_reported_sha256": api["sha256"],
        "osf_target_node": api["target_node"],
        "osf_file_guid": doc["osf_file_guid"],
        "osf_date_created": api.get("date_created"),
        "head_sha": head,
        "checked_utc": _now(now).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": socket.gethostname(),
        "api_response_sha256": _sha256(raw),
    }
    rp, ap = _receipt_paths(repo, head)
    rp.parent.mkdir(parents=True, exist_ok=True)
    ap.write_bytes(raw)
    tmp = rp.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
    os.replace(tmp, rp)
    return receipt


@functools.lru_cache(maxsize=None)
def _head_cached(real: str) -> str:
    return _read_head(real)


@functools.lru_cache(maxsize=None)
def _offline_cached(real: str, head: str, now) -> bool:
    doc = _local_checks(real, now)
    _receipt_checks(real, doc, head)
    return True


def _clear_cache():
    _head_cached.cache_clear()
    _offline_cached.cache_clear()


def check_osf_gate(repo_root, stage, *, now=None) -> None:
    """Offline gate. 'repro' passes; 'production' raises OsfGateError unless sentinel + receipt are valid."""
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {STAGES}, got {stage!r}")
    if stage == "repro":
        return None
    real = os.path.realpath(repo_root)
    head = _head_cached(real)
    # `now` is None in production use, so the memo key is (realpath, HEAD).
    _offline_cached(real, head, now)
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m ta_r4.r4_osf_gate", description=__doc__)
    ap.add_argument("command", choices=("verify-online", "check"))
    ap.add_argument("--stage", required=True, choices=STAGES)
    args = ap.parse_args(argv)
    repo = Path(__file__).resolve().parents[3]
    try:
        if args.command == "check":
            check_osf_gate(repo, args.stage)
            print(f"OSF gate OK (offline, stage={args.stage})")
        else:
            if args.stage != "production":
                print("verify-online is for --stage production only", file=sys.stderr)
                return 2
            rc = verify_online(repo)
            print(f"OSF gate verified online; receipt for HEAD {rc['head_sha']}")
    except OsfGateError as e:
        print(f"OsfGateError: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
