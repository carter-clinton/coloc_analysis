"""Test the canonical 10-column harmonizer contract.

Asserts that ``sumstats_utils.validate_canonical_frame`` (M1 plan
contract) accepts a well-formed canonical frame and rejects frames
missing canonical columns. This contract gates every M1 harmonizer
output before munging / coloc / fine-mapping consumption.

Plan reference: m1-00-preflight-and-environment-PLAN.md Task 1.
"""
from __future__ import annotations

import pandas as pd
import pytest

import sumstats_utils  # noqa: F401  -- src/python on sys.path via conftest.py
from sumstats_utils import (
    CANONICAL_COLS,
    validate_canonical_frame,
    filter_palindromic_ambiguous,
)


def test_canonical_cols_signature():
    """The canonical 10-column schema is the locked contract."""
    assert CANONICAL_COLS == [
        "CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"
    ], "Canonical schema drift detected — every M1 harmonizer depends on this exact list."


def test_validate_canonical_frame_accepts_b37_fixture(synth_b37_frame):
    """The static b37 fixture conforms to the canonical schema."""
    # No exception expected.
    validate_canonical_frame(synth_b37_frame)


def test_validate_canonical_frame_rejects_missing_column(synth_b37_frame):
    """Dropping any canonical column triggers a ValueError (B-2 guard pattern)."""
    bad = synth_b37_frame.drop(columns=["BETA"])
    with pytest.raises(ValueError, match="missing column"):
        validate_canonical_frame(bad)


def test_validate_canonical_frame_rejects_non_numeric_beta(synth_b37_frame):
    """Replacing BETA with a string column triggers a ValueError."""
    bad = synth_b37_frame.copy()
    bad["BETA"] = bad["BETA"].astype(str)
    with pytest.raises(ValueError, match="non-numeric"):
        validate_canonical_frame(bad)


def test_filter_palindromic_drops_5_band_rows(synth_b37_frame):
    """The static fixture has exactly 5 palindromic rows in MAF=[0.48,0.52]."""
    n_in = len(synth_b37_frame)
    out = filter_palindromic_ambiguous(synth_b37_frame)
    n_dropped = n_in - len(out)
    # Per conftest._build_b37_rows: 5 palindromic rows seeded into MAF band.
    assert n_dropped == 5, (
        f"Expected 5 palindromic AT/CG rows in [0.48,0.52] dropped, got {n_dropped}"
    )


def test_validate_after_palindromic_filter(synth_b37_frame):
    """Canonical frame still validates after palindromic filter applies."""
    out = filter_palindromic_ambiguous(synth_b37_frame)
    # filter_palindromic_ambiguous adds palindromic_flag — validate_canonical_frame
    # only requires CANONICAL_COLS *present*, not exclusive.
    validate_canonical_frame(out)
