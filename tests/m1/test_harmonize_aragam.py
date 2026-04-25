"""TDD RED — failing tests for src/python/harmonize_aragam.py.

Aragam CARDIoGRAM-C4D-MVP CAD harmonizer + Klarin 2018 fallback.

D-03 branch routing:
- Branch (a, AFR in ZIP): _branch_for_afr() returns 'a' from manifest
- Branch (b, AFR absent): _branch_for_afr() returns 'b'; AFR raises
  NotImplementedError directing caller to harmonize_aragam_klarin2018().

Plan reference: m1-02b-harmonizers-case-control-traits-PLAN.md Task 1.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))


@pytest.fixture
def aragam_fixture(fixtures_dir: Path) -> Path:
    return fixtures_dir / "aragam_head.tsv"


@pytest.fixture
def klarin_fixture(fixtures_dir: Path) -> Path:
    return fixtures_dir / "klarin2018_mvp_afr_head.tsv"


def test_branch_for_afr_present(tmp_path: Path) -> None:
    """When manifest has 'AFR' or 'AA_' substring, branch (a)."""
    import harmonize_aragam as ha

    manifest = tmp_path / "aragam_zip_manifest.txt"
    manifest.write_text(
        "Length      Date    Time    Name\n"
        "100  01-01-2022   CAD_GWAS_AFR_meta.tsv\n"
    )
    assert ha._branch_for_afr(manifest) == "a"


def test_branch_for_afr_absent_routes_to_klarin(tmp_path: Path) -> None:
    """When manifest lacks AFR tokens, branch (b)."""
    import harmonize_aragam as ha

    manifest = tmp_path / "aragam_zip_manifest.txt"
    manifest.write_text(
        "Length      Date    Time    Name\n"
        "100  01-01-2022   CAD_GWAS_BBJ_meta.tsv\n"
        "100  01-01-2022   CAD_GWAS_SEX_STRATIFIED.txt.gz\n"
        "100  01-01-2022   CAD_GWAS_primary_discovery_meta.tsv\n"
    )
    assert ha._branch_for_afr(manifest) == "b"


def test_branch_for_afr_missing_manifest_raises(tmp_path: Path) -> None:
    """Missing manifest must raise FileNotFoundError."""
    import harmonize_aragam as ha

    with pytest.raises(FileNotFoundError, match="aragam_zip_manifest"):
        ha._branch_for_afr(tmp_path / "missing.txt")


def test_harmonize_aragam_trans_schema(
    tmp_path: Path, aragam_fixture: Path
) -> None:
    """TRANS produces canonical 10-col schema."""
    import harmonize_aragam as ha

    out_tsv = tmp_path / "cad.TRANS.Aragam.tsv.gz"
    qc = ha.harmonize_aragam(
        input_path=aragam_fixture,
        output_tsvgz=out_tsv,
        parquet_path=tmp_path / "cad.TRANS.Aragam.parquet",
        qc_json_path=tmp_path / "cad.TRANS.Aragam.qc.json",
        trait="cad",
        ancestry="TRANS",
        consortium="CARDIoGRAM-C4D-MVP",
        year=2022,
        skip_branch_check=True,
    )
    assert out_tsv.exists()
    df = pd.read_csv(out_tsv, sep="\t")
    expected = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]
    assert list(df.columns)[:10] == expected
    # Aragam alleles arrive lowercase; should be uppercased.
    assert df["EA"].str.isupper().all()
    assert qc["n_palindromic_dropped"] >= 1


def test_harmonize_aragam_afr_branch_b_raises(
    tmp_path: Path, aragam_fixture: Path
) -> None:
    """When branch (b), AFR ancestry routes to NotImplementedError."""
    import harmonize_aragam as ha

    manifest = tmp_path / "aragam_zip_manifest.txt"
    manifest.write_text(
        "Length      Date    Time    Name\n"
        "100  01-01-2022   CAD_GWAS_BBJ_meta.tsv\n"
        "100  01-01-2022   CAD_GWAS_SEX_STRATIFIED.txt.gz\n"
        "100  01-01-2022   CAD_GWAS_primary_discovery_meta.tsv\n"
    )
    with pytest.raises(NotImplementedError, match="branch b"):
        ha.harmonize_aragam(
            input_path=aragam_fixture,
            output_tsvgz=tmp_path / "out.tsv.gz",
            parquet_path=tmp_path / "out.parquet",
            qc_json_path=tmp_path / "out.qc.json",
            trait="cad",
            ancestry="AFR",
            consortium="CARDIoGRAM-C4D-MVP",
            year=2022,
            manifest_path=manifest,
        )


def test_harmonize_aragam_klarin2018_schema(
    tmp_path: Path, klarin_fixture: Path
) -> None:
    """Klarin 2018 MVP-AFR-CAD fallback emits canonical 10-col schema."""
    import harmonize_aragam as ha

    out_tsv = tmp_path / "cad.AFR.Klarin2018.tsv.gz"
    qc = ha.harmonize_aragam_klarin2018(
        input_path=klarin_fixture,
        output_tsvgz=out_tsv,
        parquet_path=tmp_path / "cad.AFR.Klarin2018.parquet",
        qc_json_path=tmp_path / "cad.AFR.Klarin2018.qc.json",
        trait="cad",
        ancestry="AFR",
        consortium="MVP-CHARGE-Klarin",
        year=2018,
    )
    assert out_tsv.exists()
    df = pd.read_csv(out_tsv, sep="\t")
    expected = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]
    assert list(df.columns)[:10] == expected
    # N should be N_case + N_ctrl = 2000 + 6500 = 8500
    assert (df["N"] == 8500).all()
    assert qc["n_palindromic_dropped"] >= 1
