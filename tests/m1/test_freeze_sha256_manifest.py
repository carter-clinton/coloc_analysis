"""Tests for src/python/freeze_sha256_manifest.py — deterministic SHA-256 manifest writer.

Plan: m1-01-portal-fetches-and-aragam-route Task 1.
Behavior contract:
- Walks a root dir, sorts by relative_path lexicographically, writes TSV.
- With --no-mtime, two runs over the same tree produce byte-identical TSV
  (this is the OSF-paste reproducibility requirement per D-13).
- Skips *.partial, *.deferred, .download_complete* per --skip-glob default.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "src" / "python" / "freeze_sha256_manifest.py"


def _make_fixture(tmp_path: Path) -> Path:
    """Create a 3-file tree with mixed depths and one ignorable .deferred."""
    root = tmp_path / "raw_tree"
    (root / "GLGC2021" / "LDL" / "EUR").mkdir(parents=True, exist_ok=True)
    (root / "DIAMANTE2022" / "T2D" / "EUR").mkdir(parents=True, exist_ok=True)
    (root / "Aragam2022").mkdir(parents=True, exist_ok=True)

    (root / "GLGC2021" / "LDL" / "EUR" / "ldl_eur.tsv.gz").write_bytes(b"FAKE_LDL_EUR_BYTES_001\n")
    (root / "DIAMANTE2022" / "T2D" / "EUR" / "t2d_eur.tsv.gz").write_bytes(b"FAKE_T2D_EUR_BYTES_002\n")
    (root / "Aragam2022" / "cad_trans.tsv").write_bytes(b"FAKE_CAD_TRANS_BYTES_003\n")
    # Ignorable artifacts (must be skipped)
    (root / "Aragam2022" / "in_progress.partial").write_bytes(b"halfway")
    (root / "DIAMANTE2022" / "T2D" / "EUR" / ".deferred").write_bytes(b"")
    return root


def _run_freeze(root: Path, out: Path, with_mtime: bool = False) -> subprocess.CompletedProcess:
    py = sys.executable
    cmd = [py, str(SCRIPT), "--root", str(root), "--out", str(out)]
    if not with_mtime:
        cmd.append("--no-mtime")
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def test_freeze_sha256_manifest_three_real_rows(tmp_path: Path):
    root = _make_fixture(tmp_path)
    out = tmp_path / "sha256_manifest.tsv"
    _run_freeze(root, out, with_mtime=False)
    rows = out.read_text().splitlines()
    # 1 header + 3 real files (the .partial and .deferred must be skipped)
    assert len(rows) == 4, f"expected 1 header + 3 data rows, got {len(rows)}: {rows}"
    assert rows[0].split("\t") == ["relative_path", "sha256", "bytes"]


def test_freeze_sha256_manifest_byte_identical_on_rerun(tmp_path: Path):
    root = _make_fixture(tmp_path)
    out_a = tmp_path / "sha256_a.tsv"
    out_b = tmp_path / "sha256_b.tsv"
    _run_freeze(root, out_a, with_mtime=False)
    _run_freeze(root, out_b, with_mtime=False)
    assert out_a.read_bytes() == out_b.read_bytes(), \
        "two runs with --no-mtime must produce byte-identical output (OSF-paste reproducibility)"


def test_freeze_sha256_manifest_lexicographic_order(tmp_path: Path):
    root = _make_fixture(tmp_path)
    out = tmp_path / "sha256_manifest.tsv"
    _run_freeze(root, out, with_mtime=False)
    rows = out.read_text().splitlines()
    paths = [r.split("\t")[0] for r in rows[1:]]
    assert paths == sorted(paths), f"rows must be sorted by relative_path; got {paths}"
    # Verify the expected order:
    assert paths == [
        "Aragam2022/cad_trans.tsv",
        "DIAMANTE2022/T2D/EUR/t2d_eur.tsv.gz",
        "GLGC2021/LDL/EUR/ldl_eur.tsv.gz",
    ]


def test_freeze_sha256_manifest_skips_partial_and_deferred(tmp_path: Path):
    root = _make_fixture(tmp_path)
    out = tmp_path / "sha256_manifest.tsv"
    _run_freeze(root, out, with_mtime=False)
    body = out.read_text()
    assert ".partial" not in body
    assert ".deferred" not in body
