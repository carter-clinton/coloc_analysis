"""Regression tests for the opt-in fail-fast region gate in
run_native_ld_panel.run_native_ld_panel (quick 260703-o0m, Seth Defect 4).

process_region swallows every error into ``status='error: ...'`` and the loop
CONTINUES, so a broken region 1 cannot halt a ~276-region / multi-day fire. The
opt-in ``fail_fast`` gate raises ``RegionGateError`` on the FIRST non-'ok' region
and stops; the default (``fail_fast=False``) preserves the resume-safe continue.

Runs in smoke_dev py3.11. No plink / no Hail: process_region and the
manifest/ancestry/shard helpers are monkeypatched so the loop control-flow is
tested in isolation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import run_native_ld_panel as rn  # noqa: E402

ROWS = [{"region_id": "r1", "ancestry": "AFR"},
        {"region_id": "r2", "ancestry": "AFR"},
        {"region_id": "r3", "ancestry": "AFR"}]


def _stub_region_source(monkeypatch, rows):
    """Bypass manifest read + ancestry filter + shard so the loop iterates `rows`."""
    monkeypatch.setattr(rn.alp, "_read_manifest", lambda _p: rows)
    monkeypatch.setattr(rn, "_filter_ancestry", lambda regions, ancestry: regions)
    monkeypatch.setattr(rn, "_shard_rows", lambda regions, ns, si: regions)


def _fake_process(status_map):
    """A fake process_region returning a canned status per region_id, recording the
    call order in the returned `calls` list."""
    calls = []

    def fake(row, **_kw):
        rid = row["region_id"]
        calls.append(rid)
        return {"region_id": rid, "status": status_map[rid], "out": None}

    return fake, calls


def test_fail_fast_halts_on_first_non_ok(monkeypatch, tmp_path):
    _stub_region_source(monkeypatch, ROWS)
    fake, calls = _fake_process({"r1": "ok", "r2": "error: boom", "r3": "ok"})
    monkeypatch.setattr(rn, "process_region", fake)
    with pytest.raises(rn.RegionGateError) as ei:
        rn.run_native_ld_panel("manifest.tsv", "bfile", tmp_path, fail_fast=True)
    assert ei.value.region_id == "r2"
    assert "error: boom" in ei.value.status
    assert calls == ["r1", "r2"]            # r3 never processed — the loop halted


def test_default_continues_past_error(monkeypatch, tmp_path):
    _stub_region_source(monkeypatch, ROWS)
    fake, calls = _fake_process({"r1": "ok", "r2": "error: boom", "r3": "ok"})
    monkeypatch.setattr(rn, "process_region", fake)
    results = rn.run_native_ld_panel("manifest.tsv", "bfile", tmp_path)  # default
    assert calls == ["r1", "r2", "r3"]      # resume-safe continue unchanged
    assert [r["status"] for r in results] == ["ok", "error: boom", "ok"]


def test_fail_fast_all_ok_completes(monkeypatch, tmp_path):
    _stub_region_source(monkeypatch, ROWS)
    fake, calls = _fake_process({"r1": "ok", "r2": "ok", "r3": "ok"})
    monkeypatch.setattr(rn, "process_region", fake)
    results = rn.run_native_ld_panel("manifest.tsv", "bfile", tmp_path, fail_fast=True)
    assert calls == ["r1", "r2", "r3"]
    assert all(r["status"] == "ok" for r in results)


def test_region_gate_error_carries_context():
    err = rn.RegionGateError("m2_region_00001", "error: not symmetric")
    assert err.region_id == "m2_region_00001"
    assert err.status == "error: not symmetric"
    assert "m2_region_00001" in str(err)
