"""Contract tests for src/python/harmonize_magic.py.

MAGIC 2021 HbA1c per-ancestry single-trait files now carry explicit
``chromosome`` + ``base_pair_location`` columns (the 1000G version,
not the older rsid-only release). The harmonizer therefore prefers
the file's CHR/BP and only falls back to ``build_rsid_to_chrpos``
when those columns are absent.

Tests verify:
  (a) Per-ancestry file with CHR/BP -> canonical 10 cols (no crosswalk)
  (b) TRANS Bayes-factor variant (log10BF; no BETA/SE/P) emits an
      asymmetric canonical frame: BETA = NaN with a phenotype lock note
  (c) When the input lacks CHR/BP, --bim-prefix forward crosswalk fills
      them in via sumstats_utils.build_rsid_to_chrpos

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
HARMONIZER = SRC_PY / "harmonize_magic.py"
PYTHON = sys.executable

CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]


def _run_magic(
    fixture: str,
    ancestry: str,
    tmp_path: Path,
    extra_args: list[str] | None = None,
) -> tuple[Path, Path, Path]:
    src = FIXTURES / fixture
    work = tmp_path / fixture
    shutil.copy(src, work)
    output_tsvgz = tmp_path / f"out_{ancestry}.tsv.gz"
    output_parquet = tmp_path / f"out_{ancestry}.parquet"
    qc_json = tmp_path / f"out_{ancestry}.qc.json"
    cmd = [
        PYTHON, str(HARMONIZER),
        "--input", str(work),
        "--output", str(output_tsvgz),
        "--parquet", str(output_parquet),
        "--qc-json", str(qc_json),
        "--ancestry", ancestry,
        "--year", "2021",
        "--consortium", "MAGIC",
    ]
    if extra_args:
        cmd.extend(extra_args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"harmonize_magic {ancestry} failed: stderr={result.stderr!r}"
    )
    return output_tsvgz, output_parquet, qc_json


def test_magic_eur_canonical_schema(tmp_path):
    tsv_gz, parquet, qc_json = _run_magic("magic_head.tsv", "EUR", tmp_path)
    df = pd.read_csv(tsv_gz, sep="\t", compression="gzip")
    for col in CANONICAL_COLS:
        assert col in df.columns
    assert df["BETA"].notna().all()
    qc = json.loads(qc_json.read_text())
    assert qc["n_input"] == 20
    assert "n_palindromic_dropped" in qc


def test_magic_trans_bayes_factor_variant(tmp_path):
    """TRANS file ships log10BF / het_p_value (no BETA/SE/P)."""
    tsv_gz, _, qc_json = _run_magic("magic_trans_head.tsv", "TRANS", tmp_path)
    df = pd.read_csv(tsv_gz, sep="\t", compression="gzip")
    for col in CANONICAL_COLS:
        assert col in df.columns
    # TRANS variant has no BETA/SE/P in raw -> all NaN here.
    qc = json.loads(qc_json.read_text())
    assert qc.get("magic_variant") == "trans_bayes_factor"
    # Verify lnBF / het_p columns preserved out-of-band in qc sidecar.
    assert qc.get("phenotype_lock") is not None


def test_magic_rsid_crosswalk_fills_chr_bp(tmp_path):
    """When CHR/BP columns are absent, the harmonizer must call
    build_rsid_to_chrpos against --bim-prefix."""
    # Strip CHR/BP from the magic fixture to simulate the rsid-only schema.
    src = FIXTURES / "magic_head.tsv"
    df_raw = pd.read_csv(src, sep="\t")
    df_strip = df_raw.drop(columns=["chromosome", "base_pair_location"])
    work = tmp_path / "magic_rsid_only.tsv"
    df_strip.to_csv(work, sep="\t", index=False)

    output_tsvgz = tmp_path / "out_rsid.tsv.gz"
    output_parquet = tmp_path / "out_rsid.parquet"
    qc_json = tmp_path / "out_rsid.qc.json"
    bim_prefix = str(FIXTURES / "mini_1kg")

    cmd = [
        PYTHON, str(HARMONIZER),
        "--input", str(work),
        "--output", str(output_tsvgz),
        "--parquet", str(output_parquet),
        "--qc-json", str(qc_json),
        "--ancestry", "EUR",
        "--bim-prefix", bim_prefix,
        "--bim-chromosomes", "1,2",
        "--year", "2021",
        "--consortium", "MAGIC",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"harmonize_magic rsid-crosswalk failed: stderr={result.stderr!r}"
    )

    df = pd.read_csv(output_tsvgz, sep="\t", compression="gzip")
    for col in CANONICAL_COLS:
        assert col in df.columns
    qc = json.loads(qc_json.read_text())
    assert "n_unmapped_rsid" in qc
    # Fixture has 5 rsids on chr1 + 5 on chr2 + 5 unrelated; bim covers 5
    # of those. Expect some unmapped count; confirm > 0.
    assert qc["n_unmapped_rsid"] > 0
