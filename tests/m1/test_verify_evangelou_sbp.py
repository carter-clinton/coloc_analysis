"""TDD RED — failing tests for src/python/verify_evangelou_sbp.py.

Plan reference: m1-02b-harmonizers-case-control-traits-PLAN.md Task 2.
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
def evangelou_b37_fixture(fixtures_dir: Path) -> Path:
    return fixtures_dir / "evangelou_b37_head.tsv"


def test_verify_evangelou_sbp_b37_pass(
    tmp_path: Path, evangelou_b37_fixture: Path
) -> None:
    """Valid b37 fixture passes verify; D-16 outputs created."""
    import verify_evangelou_sbp as ves

    target_tsv = tmp_path / "sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.tsv.bgz"
    target_parquet = tmp_path / "sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.parquet"
    target_qc = tmp_path / "sbp.EUR.Evangelou-ICBP-UKBB.2018.qc.json"

    qc = ves.verify_and_rename(
        source=evangelou_b37_fixture,
        target_tsv_bgz=target_tsv,
        target_parquet=target_parquet,
        target_qc=target_qc,
    )
    assert target_tsv.exists()
    assert target_parquet.exists()
    assert target_qc.exists()
    assert qc["build_verified"] == "GRCh37"
    qc_json = json.loads(target_qc.read_text())
    assert qc_json["build_verified"] == "GRCh37"
    assert qc_json["d16_name"] == target_tsv.name
    assert qc_json["phenotype_lock"] == "SBP continuous (mmHg), medication-adjusted"


def test_verify_evangelou_sbp_b38_position_fails(tmp_path: Path) -> None:
    """A row at chr1:260_000_000 (> b37 chr1 max) triggers AssertionError."""
    bad_fixture = tmp_path / "evangelou_b38_invalid.tsv"
    bad_fixture.write_text(
        "CHR\tPOS\tREF\tALT\tBETA\tSE\tP\tEAF\tN\tSNP_ID\tTRAIT\tANCESTRY\tBUILD\n"
        "1\t260000000\tg\ta\t0.0605\t0.0254\t0.01714\t0.8365\t682570\t"
        "1:260000000\thypertension\tEUR\tGRCh37\n"
    )
    import verify_evangelou_sbp as ves

    target_tsv = tmp_path / "sbp.EUR.Evangelou.tsv.bgz"
    target_parquet = tmp_path / "sbp.EUR.Evangelou.parquet"
    target_qc = tmp_path / "sbp.EUR.Evangelou.qc.json"

    with pytest.raises(AssertionError, match="b37 max"):
        ves.verify_and_rename(
            source=bad_fixture,
            target_tsv_bgz=target_tsv,
            target_parquet=target_parquet,
            target_qc=target_qc,
        )
    # Failed verify must not produce output files.
    assert not target_tsv.exists()
    assert not target_parquet.exists()


def test_verify_evangelou_sbp_eaf_out_of_range_fails(tmp_path: Path) -> None:
    """EAF > 1 fails verify."""
    bad_fixture = tmp_path / "evangelou_bad_eaf.tsv"
    bad_fixture.write_text(
        "CHR\tPOS\tREF\tALT\tBETA\tSE\tP\tEAF\tN\tSNP_ID\tTRAIT\tANCESTRY\tBUILD\n"
        "1\t100000\tg\ta\t0.0605\t0.0254\t0.01714\t1.5\t682570\t"
        "1:100000\thypertension\tEUR\tGRCh37\n"
    )
    import verify_evangelou_sbp as ves

    with pytest.raises(AssertionError, match="EAF"):
        ves.verify_and_rename(
            source=bad_fixture,
            target_tsv_bgz=tmp_path / "out.tsv.bgz",
            target_parquet=tmp_path / "out.parquet",
            target_qc=tmp_path / "out.qc.json",
        )
