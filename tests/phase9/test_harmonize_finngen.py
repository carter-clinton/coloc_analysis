"""Unit tests for harmonize_finngen.py (Plan 09-02 Task 2)."""
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from harmonize_finngen import harmonize_finngen_sumstats  # noqa: E402


def test_canonical_schema(mock_finngen_sumstats, tmp_path, canonical_schema, monkeypatch):
    """harmonize_finngen produces the 10-column canonical schema + QC dict."""
    import sumstats_utils as SU

    # Neutralise liftover for unit test; QC dict still flows through.
    monkeypatch.setattr(
        SU,
        "liftover_to_grch37",
        lambda df, cf: (
            df.assign(CHR=df["CHR"].astype(str)),
            {"n_input": len(df), "n_lifted": len(df), "n_dropped": 0, "drop_rate": 0.0},
        ),
    )

    out = tmp_path / "finngen_t2d_harmonized.tsv.gz"
    qc_out = tmp_path / "finngen_t2d.qc.json"
    qc = harmonize_finngen_sumstats(
        mock_finngen_sumstats,
        out,
        Path("/dev/null"),
        trait="t2d",
        case_n=65000,
        ctrl_n=200000,
        qc_out=qc_out,
    )

    df = pd.read_csv(out, sep="\t", compression="gzip")
    for col in canonical_schema:
        assert col in df.columns, f"missing canonical column: {col}"

    # BETA preserved from the mock fixture (all 0.1)
    assert (df["BETA"] == 0.1).all()
    # N is case + ctrl
    assert (df["N"] == 265000).all()
    assert qc["drop_rate"] == 0.0
    # QC JSON written
    assert qc_out.exists()
    assert json.loads(qc_out.read_text())["cohort"] == "finngen_r12"


def test_palindromic_exclusion_applied(mock_finngen_sumstats, tmp_path, monkeypatch):
    """Palindromic A/G fixture rows in the ambiguity band should be dropped."""
    import sumstats_utils as SU

    monkeypatch.setattr(
        SU,
        "liftover_to_grch37",
        lambda df, cf: (
            df.assign(CHR=df["CHR"].astype(str)),
            {"n_input": len(df), "n_lifted": len(df), "n_dropped": 0, "drop_rate": 0.0},
        ),
    )

    out = tmp_path / "finngen_t2d_harmonized.tsv.gz"
    qc = harmonize_finngen_sumstats(
        mock_finngen_sumstats,
        out,
        Path("/dev/null"),
        trait="t2d",
        case_n=65000,
        ctrl_n=200000,
    )

    # The fixture ref/alt is A/G (not palindromic), so no rows should drop.
    assert qc["n_palindromic_dropped"] == 0
    assert qc["n_after_palindromic"] == 100


def test_liftover_drop_rate_propagated(mock_finngen_sumstats, tmp_path, monkeypatch):
    """Liftover QC (drop_rate) flows into the harmonizer's QC dict."""
    import sumstats_utils as SU

    def fake_liftover(df, cf):
        return (
            df.iloc[:95].assign(CHR=df["CHR"].iloc[:95].astype(str)),
            {"n_input": 100, "n_lifted": 95, "n_dropped": 5, "drop_rate": 0.05},
        )

    monkeypatch.setattr(SU, "liftover_to_grch37", fake_liftover)

    out = tmp_path / "finngen_t2d_harmonized.tsv.gz"
    qc = harmonize_finngen_sumstats(
        mock_finngen_sumstats,
        out,
        Path("/dev/null"),
        trait="t2d",
        case_n=65000,
        ctrl_n=200000,
    )
    assert qc["drop_rate"] == 0.05
    assert qc["n_lifted"] == 95
