"""Contract tests for src/python/m1_raw_glob.py.

The shared helper resolves the single expected raw-file path for any
(source_tag, ancestry) pair, used by every harmonize Snakemake rule's
``params: lambda``. W8 fix: returns DEFERRED_SENTINEL when an upstream
``.deferred`` marker is present in the resolved target_dir.

Plan reference: m1-02a-harmonizers-continuous-traits-PLAN.md Task 2 step (A0).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PY = PROJECT_ROOT / "src" / "python"
sys.path.insert(0, str(SRC_PY))


@pytest.fixture
def fake_repo(tmp_path, monkeypatch):
    """Build a minimal repo skeleton with a portal manifest + raw tree."""
    # config/download_manifest_m1_portal.tsv
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    manifest = cfg_dir / "download_manifest_m1_portal.tsv"
    manifest.write_text(
        "source_tag\turl\ttarget_dir\tfilename\trequires_cookie_env\t"
        "sha256_expected\ttrait\tancestry\tconsortium\tyear\n"
        "GIANT2018_BMI_EUR\thttps://example/x.gz\t"
        + str(tmp_path / "data/raw/sumstats_v2/GIANT2018/BMI/EUR")
        + "\tx.gz\tNONE\tUNKNOWN\tbmi\tEUR\tGIANT-UKBB\t2018\n"
        "Loh2022_BMI_EUR\tPENDING_D01_ACCESSION\t"
        + str(tmp_path / "data/raw/sumstats_v2/Loh2022/BMI/EUR")
        + "\tLoh2022_BMI_EUR.tsv.gz\tNONE\tUNKNOWN\tbmi\tEUR\t"
          "GIANT-23andMe\t2022\n"
    )

    # Materialize the raw target dirs.
    (tmp_path / "data/raw/sumstats_v2/GIANT2018/BMI/EUR").mkdir(
        parents=True, exist_ok=True
    )
    (tmp_path / "data/raw/sumstats_v2/Loh2022/BMI/EUR").mkdir(
        parents=True, exist_ok=True
    )

    # Need an empty SUMSTATS-UPGRADE.tsv so the helper's UPGRADE_TSV.exists()
    # check has a defined-but-empty fallback table.
    upgrade_dir = tmp_path / ".planning" / "amendments"
    upgrade_dir.mkdir(parents=True)
    (upgrade_dir / "SUMSTATS-UPGRADE.tsv").write_text(
        "source_consortium\tcitation_first_author_year\ttrait\tancestry\t"
        "expected_filename\n"
    )

    # Run helper from this fake repo root so its relative-path constants resolve.
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_resolve_raw_for_finds_landed_file(fake_repo):
    """Single matching raw file under target_dir -> returns its path."""
    target = fake_repo / "data/raw/sumstats_v2/GIANT2018/BMI/EUR/x.gz"
    target.write_bytes(b"\x1f\x8b\x08\x00")  # gzip magic header

    # Force re-import to pick up monkeypatched cwd.
    if "m1_raw_glob" in sys.modules:
        del sys.modules["m1_raw_glob"]
    from m1_raw_glob import resolve_raw_for

    out = resolve_raw_for("GIANT2018_BMI_EUR", "EUR")
    assert os.path.basename(out) == "x.gz"
    assert "GIANT2018/BMI/EUR" in out


def test_resolve_raw_for_no_matches_raises(fake_repo):
    """Zero raw files + no .deferred marker -> AssertionError."""
    if "m1_raw_glob" in sys.modules:
        del sys.modules["m1_raw_glob"]
    from m1_raw_glob import resolve_raw_for

    # GIANT target dir is empty -> expect zero matches (AssertionError).
    with pytest.raises(AssertionError, match="expected exactly 1"):
        resolve_raw_for("GIANT2018_BMI_EUR", "EUR")


def test_resolve_raw_for_deferred_marker_returns_sentinel(fake_repo):
    """W8 fix: .deferred marker in target_dir -> DEFERRED_SENTINEL."""
    if "m1_raw_glob" in sys.modules:
        del sys.modules["m1_raw_glob"]
    from m1_raw_glob import resolve_raw_for, DEFERRED_SENTINEL

    # Loh2022 target dir is empty + has a .deferred marker (matches the
    # m1-01 N1 path: PENDING_D01_ACCESSION -> .deferred placeholder).
    deferred = (
        fake_repo / "data/raw/sumstats_v2/Loh2022/BMI/EUR/.deferred"
    )
    deferred.touch()

    out = resolve_raw_for("Loh2022_BMI_EUR", "EUR")
    assert out == DEFERRED_SENTINEL
    assert DEFERRED_SENTINEL == "__DEFERRED__"


def test_resolve_raw_for_two_matches_raises(fake_repo):
    """Two matching raw files (rare; e.g. a download partial+complete coexists)
    -> AssertionError, never silently chooses one."""
    target_dir = fake_repo / "data/raw/sumstats_v2/GIANT2018/BMI/EUR"
    (target_dir / "x.gz").write_bytes(b"\x1f\x8b")
    (target_dir / "x.gz.bak").write_bytes(b"\x1f\x8b")  # second hit

    # Mutate the manifest to use a glob filename to provoke a 2-match resolution.
    manifest = fake_repo / "config" / "download_manifest_m1_portal.tsv"
    text = manifest.read_text()
    text = text.replace("\tx.gz\t", "\tx.gz*\t")
    manifest.write_text(text)

    if "m1_raw_glob" in sys.modules:
        del sys.modules["m1_raw_glob"]
    from m1_raw_glob import resolve_raw_for

    with pytest.raises(AssertionError, match="expected exactly 1"):
        resolve_raw_for("GIANT2018_BMI_EUR", "EUR")
