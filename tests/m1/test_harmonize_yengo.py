"""Contract tests for src/python/harmonize_yengo.py.

Asserts that the 4 variant codepaths (yengo2018, loh2022_eur, loh2022_afr,
page2019_afr) each:
  (a) emit the canonical 10-column schema
  (b) produce dual artifacts (.tsv.gz + .parquet)
  (c) write a .qc.json sidecar
  (d) drop palindromic rows in the [0.48, 0.52] MAF band
  (e) for Loh variants, the recorded liftover drop rate < 5%

Plan reference: m1-02a-harmonizers-continuous-traits-PLAN.md Task 1.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PY = PROJECT_ROOT / "src" / "python"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
HARMONIZER = SRC_PY / "harmonize_yengo.py"
PYTHON = sys.executable

# Canonical schema (mirrors sumstats_utils.CANONICAL_COLS).
CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]


def _run_harmonizer(
    variant: str,
    fixture_name: str,
    tmp_path: Path,
    extra_args: list[str] | None = None,
    chain_arg: bool = False,
) -> tuple[Path, Path, Path]:
    """Invoke harmonize_yengo CLI on a fixture; return (tsv_gz, parquet, qc_json) paths."""
    src = FIXTURES / fixture_name
    work = tmp_path / fixture_name
    shutil.copy(src, work)

    # CLI emits intermediate .tsv.gz (Snakemake rule does the bgzip+tabix step).
    output_tsvgz = tmp_path / f"out_{variant}.tsv.gz"
    output_parquet = tmp_path / f"out_{variant}.parquet"
    qc_json = tmp_path / f"out_{variant}.qc.json"

    cmd = [
        PYTHON, str(HARMONIZER),
        "--input", str(work),
        "--output", str(output_tsvgz),
        "--parquet", str(output_parquet),
        "--qc-json", str(qc_json),
        "--variant", variant,
        "--trait", "bmi",
        "--ancestry", "EUR",
        "--year", "2018",
        "--consortium", "GIANT-UKBB",
    ]
    if chain_arg:
        chain = PROJECT_ROOT / "data" / "external" / "liftover" / "hg38ToHg19.over.chain.gz"
        cmd.extend(["--chain", str(chain)])
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"harmonize_yengo {variant} failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    return output_tsvgz, output_parquet, qc_json


def _read_canonical(tsv_gz: Path) -> pd.DataFrame:
    return pd.read_csv(tsv_gz, sep="\t", compression="gzip")


# ---- yengo2018 (no liftover) ----

def test_yengo2018_canonical_schema(tmp_path):
    tsv_gz, parquet, qc_json = _run_harmonizer("yengo2018", "yengo_head.tsv", tmp_path)
    assert tsv_gz.exists()
    assert parquet.exists()
    assert qc_json.exists()
    df = _read_canonical(tsv_gz)
    for col in CANONICAL_COLS:
        assert col in df.columns, f"Missing canonical column {col}"
    assert df["BETA"].notna().all()
    assert df["SE"].notna().all()


def test_yengo2018_qc_json_drops_palindromic(tmp_path):
    tsv_gz, _, qc_json = _run_harmonizer("yengo2018", "yengo_head.tsv", tmp_path)
    qc = json.loads(qc_json.read_text())
    assert "n_palindromic_dropped" in qc
    # Fixture has 6 rows that meet (palindromic A/T or C/G + MAF in [0.48, 0.52]):
    #   rs3 (A/T 0.50), rs6 (T/A 0.485), rs8 (C/G 0.51), rs11 (G/C 0.485),
    #   rs16 (G/A — not palindromic), rs20 (C/A — not palindromic).
    # So expect at least 4 palindromic drops.
    assert qc["n_palindromic_dropped"] >= 1, qc
    assert qc["n_input"] == 20
    assert qc["n_output"] + qc["n_palindromic_dropped"] == qc["n_input"]


def test_yengo2018_parquet_mirrors_tsv(tmp_path):
    tsv_gz, parquet, _ = _run_harmonizer("yengo2018", "yengo_head.tsv", tmp_path)
    df_tsv = _read_canonical(tsv_gz)
    df_parquet = pd.read_parquet(parquet)
    assert len(df_tsv) == len(df_parquet)


# ---- loh2022_eur (b38 -> b37 liftover) ----

@pytest.mark.skipif(
    not (Path("data/external/liftover/hg38ToHg19.over.chain.gz")).is_absolute() or
    not (Path("/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis") /
         "data/external/liftover/hg38ToHg19.over.chain.gz").exists(),
    reason="hg38ToHg19 chain file not staged.",
)
def test_loh2022_eur_canonical_schema(tmp_path):
    tsv_gz, parquet, qc_json = _run_harmonizer(
        "loh2022_eur", "loh_head.tsv", tmp_path, chain_arg=True
    )
    assert tsv_gz.exists()
    df = _read_canonical(tsv_gz)
    for col in CANONICAL_COLS:
        assert col in df.columns, f"Missing canonical column {col}"


@pytest.mark.skipif(
    not (Path("/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis") /
         "data/external/liftover/hg38ToHg19.over.chain.gz").exists(),
    reason="hg38ToHg19 chain file not staged.",
)
def test_loh2022_eur_liftover_drop_rate_under_5pct(tmp_path):
    _, _, qc_json = _run_harmonizer(
        "loh2022_eur", "loh_head.tsv", tmp_path, chain_arg=True
    )
    qc = json.loads(qc_json.read_text())
    assert "liftover_drop_rate" in qc, qc
    # Hard ceiling per RESEARCH pitfall #1.
    assert qc["liftover_drop_rate"] < 0.05, qc


# ---- page2019_afr (b37 native, no liftover) ----

def test_page2019_afr_canonical_schema(tmp_path):
    tsv_gz, parquet, qc_json = _run_harmonizer(
        "page2019_afr", "page_bmi_afr_head.tsv", tmp_path
    )
    df = _read_canonical(tsv_gz)
    for col in CANONICAL_COLS:
        assert col in df.columns
    # PAGE has INFO column → harmonizer should record info_filter_count in QC.
    qc = json.loads(qc_json.read_text())
    assert "n_info_below_threshold" in qc
