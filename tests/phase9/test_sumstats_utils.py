"""Unit tests for Phase 9 sumstats_utils.py extensions (Plan 09-02 Task 1).

Covers:
  - is_palindromic (A/T, C/G strand palindromes)
  - filter_palindromic_ambiguous (MAF band exclusion per RESEARCH pitfall #2)
  - liftover_to_grch37 (5% drop-rate threshold enforcement per pitfall #1)
"""
from pathlib import Path
import sys

import pandas as pd
import pytest

# Project convention: add src/python to sys.path and import by module name.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from sumstats_utils import (  # noqa: E402
    filter_palindromic_ambiguous,
    is_palindromic,
    liftover_to_grch37,
)


def test_is_palindromic():
    assert is_palindromic("A", "T")
    assert is_palindromic("T", "A")
    assert is_palindromic("C", "G")
    assert is_palindromic("G", "C")
    assert not is_palindromic("A", "G")
    assert not is_palindromic("C", "T")


def test_is_palindromic_case_insensitive():
    assert is_palindromic("a", "t")
    assert is_palindromic("c", "g")


def test_filter_palindromic_ambiguous_drops_band():
    # 5 distinct templates × 20 reps = 100 rows
    #   idx 0: A/T EAF=0.50 -> palindromic + ambig -> DROP
    #   idx 1: A/G EAF=0.30 -> non-palindromic -> keep
    #   idx 2: C/G EAF=0.49 -> palindromic + ambig -> DROP
    #   idx 3: G/A EAF=0.20 -> non-palindromic -> keep
    #   idx 4: A/T EAF=0.51 -> palindromic + ambig -> DROP
    df = pd.DataFrame({
        "EA": ["A", "A", "C", "G", "A"] * 20,
        "OA": ["T", "G", "G", "A", "T"] * 20,
        "EAF": [0.50, 0.30, 0.49, 0.20, 0.51] * 20,
    })
    out = filter_palindromic_ambiguous(df)
    # 3 of every 5 rows dropped -> 40 keepers
    assert len(out) == 40, f"Expected 40 rows, got {len(out)}"
    assert "palindromic_flag" in out.columns


def test_filter_palindromic_keeps_nonambiguous_palindromes():
    # A/T with MAF=0.10 is palindromic but NOT in ambiguity band -> keep + flag
    df = pd.DataFrame({
        "EA": ["A"] * 10,
        "OA": ["T"] * 10,
        "EAF": [0.10] * 10,
    })
    out = filter_palindromic_ambiguous(df)
    assert len(out) == 10
    assert out["palindromic_flag"].all()


def test_liftover_at_threshold_ok(monkeypatch):
    """Exactly 5% drop rate must pass (<=, not strict <)."""
    import sumstats_utils as SU
    df = pd.DataFrame({
        "CHR": ["1"] * 100,
        "BP": list(range(1000, 1100)),
        "EA": ["A"] * 100,
        "OA": ["G"] * 100,
    })

    def fake_lift(cf, chrom, pos):
        # Fail first 5 (pos 1000..1004), succeed for >=1005 -> 5/100 drop
        return ("1", pos + 100) if pos >= 1005 else None

    monkeypatch.setattr(SU, "liftover_coordinates", fake_lift)
    out, qc = liftover_to_grch37(df, "/dev/null")
    assert qc["drop_rate"] == 0.05
    assert qc["n_lifted"] == 95
    assert qc["n_dropped"] == 5
    assert len(out) == 95


def test_liftover_above_threshold_raises(monkeypatch):
    import sumstats_utils as SU
    df = pd.DataFrame({
        "CHR": ["1"] * 100,
        "BP": list(range(1000, 1100)),
        "EA": ["A"] * 100,
        "OA": ["G"] * 100,
    })

    def fake_lift(cf, chrom, pos):
        # Fail 6/100 -> 6% drop
        return ("1", pos + 100) if pos >= 1006 else None

    monkeypatch.setattr(SU, "liftover_coordinates", fake_lift)
    with pytest.raises(RuntimeError, match="pitfall #1"):
        liftover_to_grch37(df, "/dev/null")


def test_liftover_updates_chr_bp(monkeypatch):
    import sumstats_utils as SU
    df = pd.DataFrame({
        "CHR": ["10"] * 100,
        "BP": list(range(100, 200)),
        "EA": ["A"] * 100,
        "OA": ["G"] * 100,
    })

    def fake_lift(cf, chrom, pos):
        # Map chr10 -> 10 (no prefix), pos -> pos + 1_000_000
        return ("10", pos + 1_000_000)

    monkeypatch.setattr(SU, "liftover_coordinates", fake_lift)
    out, qc = liftover_to_grch37(df, "/dev/null")
    assert qc["drop_rate"] == 0.0
    assert (out["BP"].astype(int).min() == 1_000_100)
    assert (out["BP"].astype(int).max() == 1_000_199)
