"""mtCOJO extreme-overlap filter tests (D-M2-08, D-M2-Q5).

Per D-M2-08: Apply mtCOJO to every MTAG-novel locus where the bivariate-
intercept-matrix gcov_int with any contributing trait exceeds 0.1 (Turley
2018 §"sample overlap" threshold).

Wave 4 lands src/python/mtcojo_extreme_overlap_filter.py.
"""
from __future__ import annotations

import pytest

try:
    from mtcojo_extreme_overlap_filter import has_extreme_overlap  # type: ignore[import-not-found]
    _FILTER_AVAILABLE = True
except ImportError:
    _FILTER_AVAILABLE = False
    has_extreme_overlap = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(
    not _FILTER_AVAILABLE,
    reason="src/python/mtcojo_extreme_overlap_filter.py not yet landed (Wave 4)",
)


def test_above_threshold_returns_true():
    """gcov_int = 0.15 with any contributing trait → True (above 0.1)."""
    import numpy as np

    R = np.array([[1.0, 0.15], [0.15, 1.0]])
    assert has_extreme_overlap("bmi", ["bmi", "t2d"], R, threshold=0.1) is True


def test_threshold_boundary_exclusive():
    """Boundary case: gcov_int = exactly 0.10 must NOT trigger (strict >)."""
    import numpy as np

    R = np.array([[1.0, 0.10], [0.10, 1.0]])
    assert has_extreme_overlap("bmi", ["bmi", "t2d"], R, threshold=0.1) is False
