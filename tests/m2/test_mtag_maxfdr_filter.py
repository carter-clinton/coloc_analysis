"""MTAG max_FDR post-hoc filter tests (D-M2-Q1).

Per Turley 2018 Methods §"maxFDR" + D-M2-Q1: drop MTAG-meta rows where
max_FDR ≥ 0.05. Wave 2 lands src/python/mtag_maxfdr_filter.py.
"""
from __future__ import annotations

import pytest

try:
    from mtag_maxfdr_filter import filter_by_max_fdr  # type: ignore[import-not-found]
    _FILTER_AVAILABLE = True
except ImportError:
    _FILTER_AVAILABLE = False
    filter_by_max_fdr = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(
    not _FILTER_AVAILABLE,
    reason="src/python/mtag_maxfdr_filter.py not yet landed (Wave 2)",
)


def test_drops_rows_at_or_above_threshold():
    """Rows with max_FDR >= 0.05 must be dropped."""
    import pandas as pd  # local import — only needed when filter exists

    df = pd.DataFrame({"snp": ["a", "b", "c"], "max_FDR": [0.01, 0.05, 0.10]})
    out = filter_by_max_fdr(df, threshold=0.05)
    assert (out["max_FDR"] < 0.05).all()
    assert len(out) == 1
    assert out.iloc[0]["snp"] == "a"


def test_retains_rows_below_threshold():
    """Rows with max_FDR < 0.05 are retained."""
    import pandas as pd

    df = pd.DataFrame({"snp": ["a", "b"], "max_FDR": [0.001, 0.049]})
    out = filter_by_max_fdr(df, threshold=0.05)
    assert len(out) == 2
