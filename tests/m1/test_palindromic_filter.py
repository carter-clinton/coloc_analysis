"""Test ``filter_palindromic_ambiguous`` exact-count semantics.

Plan-spec test: 10 synthetic rows with 4 A/T palindromic in MAF=[0.48,0.52],
4 non-palindromic, 2 G/C outside band. Asserts the filter drops exactly 4
(the in-band A/T set; the out-of-band G/C set is retained with the
``palindromic_flag`` column set True).

Plan reference: m1-00-preflight-and-environment-PLAN.md Task 1.
"""
from __future__ import annotations

import pandas as pd
import pytest

import sumstats_utils  # noqa: F401 — src/python on sys.path
from sumstats_utils import filter_palindromic_ambiguous, CANONICAL_COLS


def _make_10_row_test_frame() -> pd.DataFrame:
    """Build the 10-row synthetic frame from the plan spec.

    - 4 A/T palindromic rows with EAF in [0.48, 0.52] (DROPPED)
    - 4 non-palindromic rows (KEPT, palindromic_flag=False)
    - 2 G/C palindromic rows with EAF outside [0.48, 0.52] (KEPT, palindromic_flag=True)
    """
    rows = [
        # 4 A/T palindromic in MAF band — DROPPED
        {"CHR": 1, "BP": 1000, "SNP": "rs1", "EA": "A", "OA": "T",
         "BETA": 0.01, "SE": 0.001, "P": 0.5, "EAF": 0.485, "N": 100000},
        {"CHR": 1, "BP": 2000, "SNP": "rs2", "EA": "T", "OA": "A",
         "BETA": 0.02, "SE": 0.002, "P": 0.4, "EAF": 0.500, "N": 100000},
        {"CHR": 1, "BP": 3000, "SNP": "rs3", "EA": "A", "OA": "T",
         "BETA": -0.01, "SE": 0.001, "P": 0.6, "EAF": 0.510, "N": 100000},
        {"CHR": 1, "BP": 4000, "SNP": "rs4", "EA": "T", "OA": "A",
         "BETA": 0.005, "SE": 0.001, "P": 0.7, "EAF": 0.495, "N": 100000},
        # 4 non-palindromic — KEPT
        {"CHR": 2, "BP": 1000, "SNP": "rs5", "EA": "A", "OA": "G",
         "BETA": 0.03, "SE": 0.002, "P": 0.1, "EAF": 0.30, "N": 100000},
        {"CHR": 2, "BP": 2000, "SNP": "rs6", "EA": "C", "OA": "T",
         "BETA": 0.04, "SE": 0.002, "P": 0.2, "EAF": 0.20, "N": 100000},
        {"CHR": 2, "BP": 3000, "SNP": "rs7", "EA": "G", "OA": "T",
         "BETA": -0.05, "SE": 0.003, "P": 0.05, "EAF": 0.10, "N": 100000},
        {"CHR": 2, "BP": 4000, "SNP": "rs8", "EA": "T", "OA": "G",
         "BETA": 0.06, "SE": 0.003, "P": 0.01, "EAF": 0.40, "N": 100000},
        # 2 G/C palindromic OUT of band — KEPT (with palindromic_flag=True)
        {"CHR": 3, "BP": 1000, "SNP": "rs9", "EA": "G", "OA": "C",
         "BETA": 0.10, "SE": 0.005, "P": 0.001, "EAF": 0.10, "N": 100000},
        {"CHR": 3, "BP": 2000, "SNP": "rs10", "EA": "C", "OA": "G",
         "BETA": -0.10, "SE": 0.005, "P": 0.001, "EAF": 0.90, "N": 100000},
    ]
    return pd.DataFrame(rows)[CANONICAL_COLS]


def test_filter_drops_exactly_four_inband_palindromic():
    """Exact-count semantics: 4 in-band A/T rows dropped, 6 retained."""
    df = _make_10_row_test_frame()
    assert len(df) == 10, "fixture frame must have 10 rows"

    out = filter_palindromic_ambiguous(df)
    assert len(out) == 6, (
        f"Expected 6 retained rows (4 non-pal + 2 out-of-band G/C), got {len(out)}"
    )

    # 2 of the kept rows must have palindromic_flag=True (the G/C ones)
    n_flagged = int(out["palindromic_flag"].sum())
    assert n_flagged == 2, (
        f"Expected 2 retained-palindromic-flag rows (out-of-band G/C), got {n_flagged}"
    )


def test_filter_preserves_non_palindromic_rows():
    """The 4 non-palindromic rows must be untouched and flag-False."""
    df = _make_10_row_test_frame()
    out = filter_palindromic_ambiguous(df)
    non_pal = out[out["palindromic_flag"] == False]
    assert len(non_pal) == 4, (
        f"Expected 4 non-palindromic rows retained, got {len(non_pal)}"
    )
    assert set(non_pal["SNP"]) == {"rs5", "rs6", "rs7", "rs8"}


def test_filter_band_edge_cases():
    """Rows exactly at MAF=0.48 and MAF=0.52 are inside the inclusive band."""
    rows = [
        # palindromic at exact band edges — DROPPED
        {"CHR": 1, "BP": 100, "SNP": "edgeA", "EA": "A", "OA": "T",
         "BETA": 0.0, "SE": 0.001, "P": 0.5, "EAF": 0.48, "N": 100000},
        {"CHR": 1, "BP": 200, "SNP": "edgeB", "EA": "C", "OA": "G",
         "BETA": 0.0, "SE": 0.001, "P": 0.5, "EAF": 0.52, "N": 100000},
        # palindromic just outside band — KEPT
        {"CHR": 1, "BP": 300, "SNP": "outA", "EA": "A", "OA": "T",
         "BETA": 0.0, "SE": 0.001, "P": 0.5, "EAF": 0.479, "N": 100000},
        {"CHR": 1, "BP": 400, "SNP": "outB", "EA": "C", "OA": "G",
         "BETA": 0.0, "SE": 0.001, "P": 0.5, "EAF": 0.521, "N": 100000},
    ]
    df = pd.DataFrame(rows)[CANONICAL_COLS]
    out = filter_palindromic_ambiguous(df)
    assert len(out) == 2, f"Expected 2 retained at-band-edge rows, got {len(out)}"
    assert set(out["SNP"]) == {"outA", "outB"}
