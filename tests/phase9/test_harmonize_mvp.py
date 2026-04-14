"""Unit tests for harmonize_mvp.py (Plan 09-02 Task 4).

Covers both the REGENIE-style schema (fixture in conftest.py) and the
dbGaP GWAS-central schema (|β| + Coded Allele) that the real phs001672
files use — the Wave-1 corrections to the plan draft mandated both
variants be supported (see 09-01 Rule 1 deviation #2).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from harmonize_mvp import (  # noqa: E402
    harmonize_mvp_sumstats,
    log10p_to_pval,
    reconstruct_signed_beta,
)


def test_log10p_conversion():
    log10p = pd.Series([0.0, 3.0, 8.0, 350.0])
    p = log10p_to_pval(log10p)
    assert abs(p.iloc[0] - 1.0) < 1e-9
    assert abs(p.iloc[1] - 1e-3) < 1e-9
    assert abs(p.iloc[2] - 1e-8) < 1e-12
    # Phase 2 convention: clip LOG10P at 300 to avoid numeric underflow.
    assert abs(p.iloc[3] - 1e-300) < 1e-305


def test_log10p_clipped_below_zero():
    """Negative LOG10P values (edge-case data errors) clip to 0 -> P=1."""
    log10p = pd.Series([-5.0, 0.5])
    p = log10p_to_pval(log10p)
    assert abs(p.iloc[0] - 1.0) < 1e-9
    assert abs(p.iloc[1] - 10 ** (-0.5)) < 1e-9


def test_mvp_canonical_regenie_schema(mock_mvp_sumstats, tmp_path, canonical_schema):
    """REGENIE-style (CHROM/POS/REF/ALT/BETA/LOG10P) - fixture default."""
    out = tmp_path / "mvp_t2d_eur.tsv.gz"
    qc = harmonize_mvp_sumstats(
        mock_mvp_sumstats,
        out,
        "pha004945.1",
        "t2d",
        "eur",
        genome_build="GRCh37",
    )
    df = pd.read_csv(out, sep="\t", compression="gzip")
    for col in canonical_schema:
        assert col in df.columns, f"missing canonical column: {col}"
    # LOG10P=8 -> P=1e-8 for the fixture
    assert abs(df["P"].iloc[0] - 1e-8) < 1e-12
    assert qc["pha_id"] == "pha004945.1"
    assert qc["ancestry"] == "eur"


def test_reconstruct_signed_beta_same_allele():
    """When coded allele == EA (ALT), sign is preserved (|β| -> +|β|)."""
    df = pd.DataFrame({
        "EA": ["A", "G", "C"],
        "OA": ["G", "A", "T"],
        "beta_abs": [0.5, 0.2, 0.1],
        "coded_allele": ["A", "G", "C"],
    })
    signed = reconstruct_signed_beta(df, beta_abs_col="beta_abs", coded_col="coded_allele")
    assert list(signed) == [0.5, 0.2, 0.1]


def test_reconstruct_signed_beta_opposite_allele():
    """When coded allele == OA (REF), sign flips (|β| -> -|β|)."""
    df = pd.DataFrame({
        "EA": ["A", "G", "C"],
        "OA": ["G", "A", "T"],
        "beta_abs": [0.5, 0.2, 0.1],
        "coded_allele": ["G", "A", "T"],  # == OA everywhere
    })
    signed = reconstruct_signed_beta(df, beta_abs_col="beta_abs", coded_col="coded_allele")
    assert list(signed) == [-0.5, -0.2, -0.1]


def test_mvp_dbgap_schema(tmp_path, canonical_schema):
    """dbGaP GWAS-central schema (|β| + Coded Allele) — real phs001672 layout."""
    # Simulate a dbGaP file: columns "Chr ID", "Chr Position", "Allele1",
    # "Allele2", "SNP ID", "β" (absolute value), "SE", "P-value",
    # "Coded Allele", "Sample size". All coded == ALT -> positive betas.
    df_raw = pd.DataFrame({
        "Chr ID": [10] * 100,
        "Chr Position": range(114750000, 114750100),
        "Allele1": ["A"] * 100,  # OA
        "Allele2": ["G"] * 100,  # EA
        "SNP ID": [f"rs{i}" for i in range(100)],
        "β": [0.15] * 100,
        "SE": [0.02] * 100,
        "P-value": [1e-8] * 100,
        "Coded Allele": ["G"] * 100,  # == Allele2 -> positive
        "Sample size": [250000] * 100,
    })
    src = tmp_path / "pha004945_dbgap.txt.gz"
    df_raw.to_csv(src, sep="\t", index=False, compression="gzip")

    out = tmp_path / "mvp_t2d_eur_dbgap.tsv.gz"
    qc = harmonize_mvp_sumstats(
        src,
        out,
        "pha004945.1",
        "t2d",
        "eur",
        genome_build="GRCh37",  # dbGaP phs001672 is actually GRCh38, but we test
                                 # the schema decoder separately from liftover
    )
    df = pd.read_csv(out, sep="\t", compression="gzip")
    for col in canonical_schema:
        assert col in df.columns, f"missing {col}"
    # Signed BETA reconstructed as +0.15 (coded == EA)
    assert (df["BETA"] == 0.15).all()
    assert (df["P"] == 1e-8).all()
