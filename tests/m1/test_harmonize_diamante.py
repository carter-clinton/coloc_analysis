"""TDD RED — failing tests for src/python/harmonize_diamante.py.

DIAMANTE Mahajan 2022 T2D harmonizer. Handles TRANS + EUR + EAS + SAS;
rejects AFR + HIS (TSV rows 8 + 11 dua_pending).

Plan reference: m1-02b-harmonizers-case-control-traits-PLAN.md Task 1.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))


@pytest.fixture
def diamante_fixture(fixtures_dir: Path) -> Path:
    return fixtures_dir / "diamante_head.tsv"


@pytest.mark.parametrize("ancestry", ["TRANS", "EUR", "EAS", "SAS"])
def test_harmonize_diamante_canonical_schema(
    tmp_path: Path, diamante_fixture: Path, ancestry: str
) -> None:
    """Each released ancestry produces canonical 10-col schema."""
    import harmonize_diamante as hd

    out_tsv = tmp_path / f"t2d.{ancestry}.DIAMANTE.tsv.gz"
    out_parquet = tmp_path / f"t2d.{ancestry}.DIAMANTE.parquet"
    out_qc = tmp_path / f"t2d.{ancestry}.DIAMANTE.qc.json"
    qc = hd.harmonize_diamante(
        input_path=diamante_fixture,
        output_tsvgz=out_tsv,
        parquet_path=out_parquet,
        qc_json_path=out_qc,
        trait="t2d",
        ancestry=ancestry,
        consortium="DIAMANTE",
        year=2022,
    )
    assert out_tsv.exists()
    assert out_parquet.exists()
    assert out_qc.exists()
    df = pd.read_csv(out_tsv, sep="\t")
    expected = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]
    assert list(df.columns)[:10] == expected
    assert qc["n_palindromic_dropped"] >= 1


@pytest.mark.parametrize("ancestry", ["AFR", "HIS"])
def test_harmonize_diamante_rejects_deferred_ancestry(
    tmp_path: Path, diamante_fixture: Path, ancestry: str
) -> None:
    """AFR + HIS strata must be rejected (TSV rows 8 + 11 dua_pending)."""
    import harmonize_diamante as hd

    out_tsv = tmp_path / f"t2d.{ancestry}.tsv.gz"
    out_parquet = tmp_path / f"t2d.{ancestry}.parquet"
    out_qc = tmp_path / f"t2d.{ancestry}.qc.json"
    with pytest.raises((SystemExit, ValueError)):
        hd.harmonize_diamante(
            input_path=diamante_fixture,
            output_tsvgz=out_tsv,
            parquet_path=out_parquet,
            qc_json_path=out_qc,
            trait="t2d",
            ancestry=ancestry,
            consortium="DIAMANTE",
            year=2022,
        )
    # No output file should have been produced.
    assert not out_tsv.exists()


def test_harmonize_diamante_n_effective_used(
    tmp_path: Path, diamante_fixture: Path
) -> None:
    """N column should prefer N_effective when present."""
    import harmonize_diamante as hd

    out_tsv = tmp_path / "t2d.TRANS.DIAMANTE.tsv.gz"
    qc = hd.harmonize_diamante(
        input_path=diamante_fixture,
        output_tsvgz=out_tsv,
        parquet_path=tmp_path / "t2d.TRANS.DIAMANTE.parquet",
        qc_json_path=tmp_path / "t2d.TRANS.DIAMANTE.qc.json",
        trait="t2d",
        ancestry="TRANS",
        consortium="DIAMANTE",
        year=2022,
    )
    df = pd.read_csv(out_tsv, sep="\t")
    # All N values should equal N_effective from fixture (100000).
    assert (df["N"] == 100000).all()
    assert qc.get("n_source") == "N_effective"
