"""Contract tests for src/python/harmonize_wuttke.py.

Asserts:
  (a) Wuttke 2019 TRANS/EUR space-delimited input -> canonical 10 cols
  (b) Morris 2019 AFR (same-format companion) -> canonical 10 cols
  (c) Dual-emit (.tsv.gz + .parquet) + .qc.json sidecar
  (d) Palindromic / MAF filter QC counts present

Plan reference: m1-02a-harmonizers-continuous-traits-PLAN.md Task 2.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PY = PROJECT_ROOT / "src" / "python"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
HARMONIZER = SRC_PY / "harmonize_wuttke.py"
PYTHON = sys.executable

CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]


def _run_wuttke(
    fixture: str,
    variant: str,
    ancestry: str,
    tmp_path: Path,
) -> tuple[Path, Path, Path]:
    src = FIXTURES / fixture
    work = tmp_path / fixture
    shutil.copy(src, work)
    output_tsvgz = tmp_path / f"out_{variant}_{ancestry}.tsv.gz"
    output_parquet = tmp_path / f"out_{variant}_{ancestry}.parquet"
    qc_json = tmp_path / f"out_{variant}_{ancestry}.qc.json"

    cmd = [
        PYTHON, str(HARMONIZER),
        "--input", str(work),
        "--output", str(output_tsvgz),
        "--parquet", str(output_parquet),
        "--qc-json", str(qc_json),
        "--variant", variant,
        "--ancestry", ancestry,
        "--year", "2019",
        "--consortium", "CKDGen",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"harmonize_wuttke {variant}/{ancestry} failed: stderr={result.stderr!r}"
    )
    return output_tsvgz, output_parquet, qc_json


def test_wuttke_eur_canonical_schema(tmp_path):
    tsv_gz, parquet, qc_json = _run_wuttke(
        "wuttke_head.tsv", "wuttke2019_eur", "EUR", tmp_path
    )
    df = pd.read_csv(tsv_gz, sep="\t", compression="gzip")
    for col in CANONICAL_COLS:
        assert col in df.columns
    assert df["BETA"].notna().all()
    assert parquet.exists()
    qc = json.loads(qc_json.read_text())
    assert qc["n_input"] == 20
    assert "n_palindromic_dropped" in qc
    assert qc["n_output"] >= 1


def test_wuttke_trans_canonical_schema(tmp_path):
    tsv_gz, _, qc_json = _run_wuttke(
        "wuttke_head.tsv", "wuttke2019_trans", "TRANS", tmp_path
    )
    df = pd.read_csv(tsv_gz, sep="\t", compression="gzip")
    for col in CANONICAL_COLS:
        assert col in df.columns


def test_morris_afr_canonical_schema(tmp_path):
    tsv_gz, _, qc_json = _run_wuttke(
        "morris_afr_head.tsv", "morris2019_afr", "AFR", tmp_path
    )
    df = pd.read_csv(tsv_gz, sep="\t", compression="gzip")
    for col in CANONICAL_COLS:
        assert col in df.columns
    qc = json.loads(qc_json.read_text())
    assert qc["ancestry"] == "AFR"
    assert qc["variant"] == "morris2019_afr"
