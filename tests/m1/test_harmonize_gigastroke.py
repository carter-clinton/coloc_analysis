"""TDD RED — failing tests for src/python/harmonize_gigastroke.py.

GIGASTROKE Mishra 2022 all-stroke harmonizer. Loads D-02-integer-locked
GCST accessions from .planning/amendments/SUMSTATS-UPGRADE.tsv at module
load; defensive guard raises if any placeholder remains.

Plan reference: m1-02b-harmonizers-case-control-traits-PLAN.md Task 1.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))


@pytest.fixture
def gigastroke_fixture(fixtures_dir: Path) -> Path:
    return fixtures_dir / "gigastroke_head.tsv"


def test_harmonize_gigastroke_trans_schema(
    tmp_path: Path, gigastroke_fixture: Path
) -> None:
    """TRANS ancestry produces canonical 10-col schema."""
    import harmonize_gigastroke as hg

    out_tsv = tmp_path / "stroke.TRANS.GIGASTROKE.tsv.gz"
    qc = hg.harmonize_gigastroke(
        input_path=gigastroke_fixture,
        output_tsvgz=out_tsv,
        parquet_path=tmp_path / "stroke.TRANS.GIGASTROKE.parquet",
        qc_json_path=tmp_path / "stroke.TRANS.GIGASTROKE.qc.json",
        trait="stroke",
        ancestry="TRANS",
        consortium="GIGASTROKE",
        year=2022,
    )
    assert out_tsv.exists()
    df = pd.read_csv(out_tsv, sep="\t")
    expected = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]
    assert list(df.columns)[:10] == expected
    assert qc["n_palindromic_dropped"] >= 1


def test_harmonize_gigastroke_invalid_ancestry_raises(
    tmp_path: Path, gigastroke_fixture: Path
) -> None:
    """Unknown ancestry should raise."""
    import harmonize_gigastroke as hg

    with pytest.raises((SystemExit, ValueError)):
        hg.harmonize_gigastroke(
            input_path=gigastroke_fixture,
            output_tsvgz=tmp_path / "out.tsv.gz",
            parquet_path=tmp_path / "out.parquet",
            qc_json_path=tmp_path / "out.qc.json",
            trait="stroke",
            ancestry="XYZ",
            consortium="GIGASTROKE",
            year=2022,
        )


def test_harmonize_gigastroke_filenames_loaded_from_tsv() -> None:
    """Module-load defensive: GIGASTROKE_FILENAMES dict populated from
    SUMSTATS-UPGRADE.tsv with integer-locked GCST filenames (no
    `GCST90104540-series` placeholders)."""
    import harmonize_gigastroke as hg

    importlib.reload(hg)
    fmap = hg.GIGASTROKE_FILENAMES
    assert isinstance(fmap, dict)
    assert len(fmap) >= 1
    for _, fn in fmap.items():
        assert "GCST90104540-series" not in str(fn)


def test_harmonize_gigastroke_placeholder_guard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Module reload with a fixture TSV containing placeholder must raise."""
    fake_tsv = tmp_path / "SUMSTATS-UPGRADE.tsv"
    fake_tsv.write_text(
        "trait\tancestry\tsource_consortium\texpected_filename\n"
        "stroke\tTRANS\tGIGASTROKE\tGCST90104540-series_buildGRCh37.tsv.gz\n"
    )
    # Patch the module-level path constant before reload.
    import harmonize_gigastroke as hg

    monkeypatch.setattr(hg, "_TSV", fake_tsv)
    with pytest.raises(RuntimeError, match="placeholder"):
        hg._reload_filenames()
