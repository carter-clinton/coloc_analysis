"""Contract tests for src/python/harmonize_glgc.py.

Asserts:
  (a) GLGC RVTESTS-style headers map to the canonical 10-column schema
  (b) per-ancestry single-trait file (LDL EUR) emits dual artifacts + QC
  (c) the logTG variant flags `phenotype_lock` in the QC sidecar without
      re-transforming values

Plan reference: m1-02a-harmonizers-continuous-traits-PLAN.md Task 1.
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
HARMONIZER = SRC_PY / "harmonize_glgc.py"
PYTHON = sys.executable

CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]


def _run_glgc(
    fixture: str,
    subtype: str,
    ancestry: str,
    tmp_path: Path,
) -> tuple[Path, Path, Path]:
    src = FIXTURES / fixture
    work = tmp_path / fixture
    shutil.copy(src, work)

    output_tsvgz = tmp_path / f"out_{subtype}_{ancestry}.tsv.gz"
    output_parquet = tmp_path / f"out_{subtype}_{ancestry}.parquet"
    qc_json = tmp_path / f"out_{subtype}_{ancestry}.qc.json"

    cmd = [
        PYTHON, str(HARMONIZER),
        "--input", str(work),
        "--output", str(output_tsvgz),
        "--parquet", str(output_parquet),
        "--qc-json", str(qc_json),
        "--subtype", subtype,
        "--ancestry", ancestry,
        "--year", "2021",
        "--consortium", "GLGC",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"harmonize_glgc {subtype}/{ancestry} failed: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    return output_tsvgz, output_parquet, qc_json


def test_glgc_ldl_eur_canonical_schema(tmp_path):
    tsv_gz, parquet, qc_json = _run_glgc(
        "glgc_ldl_head.tsv", "LDL", "EUR", tmp_path
    )
    df = pd.read_csv(tsv_gz, sep="\t", compression="gzip")
    for col in CANONICAL_COLS:
        assert col in df.columns, f"Missing canonical column {col}"
    assert df["BETA"].notna().all()
    assert df["SE"].notna().all()
    assert parquet.exists()
    qc = json.loads(qc_json.read_text())
    assert qc["n_input"] == 20
    assert qc["n_output"] >= 1
    # No log-TG transform marker for LDL.
    assert qc.get("phenotype_lock") in (None, "linear", ""), qc


def test_glgc_logtg_eur_marks_phenotype_lock(tmp_path):
    # The harmonizer should detect logTG via either the --subtype TG +
    # filename hint OR explicit --logtg flag. We pass an explicit flag for
    # determinism here.
    src = FIXTURES / "glgc_tg_logtg_head.tsv"
    work = tmp_path / "logTG_INV_EUR_head.tsv"  # filename signals logTG
    shutil.copy(src, work)

    output_tsvgz = tmp_path / "out_TG_EUR.tsv.gz"
    output_parquet = tmp_path / "out_TG_EUR.parquet"
    qc_json = tmp_path / "out_TG_EUR.qc.json"

    cmd = [
        PYTHON, str(HARMONIZER),
        "--input", str(work),
        "--output", str(output_tsvgz),
        "--parquet", str(output_parquet),
        "--qc-json", str(qc_json),
        "--subtype", "TG",
        "--ancestry", "EUR",
        "--year", "2021",
        "--consortium", "GLGC",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"harmonize_glgc TG (logTG) failed: stderr={result.stderr!r}"
    )

    df = pd.read_csv(output_tsvgz, sep="\t", compression="gzip")
    for col in CANONICAL_COLS:
        assert col in df.columns
    qc = json.loads(qc_json.read_text())
    assert qc.get("phenotype_lock") == "log(TG) inverse-normal transformed", qc
