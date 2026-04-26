"""mtCOJO eligible-target selection tests (D-M2-Q5).

Per D-M2-Q5: Run mtCOJO ONLY for target traits where MTAG produced a novel
locus AND the bivariate-intercept-matrix gcov_int with any contributing
trait exceeds 0.1 (D-M2-08 threshold). MTAG-null targets get NO mtCOJO.

Wave 4 lands src/python/mtcojo_eligible_targets.py.
"""
from __future__ import annotations

import pytest

try:
    from mtcojo_eligible_targets import eligible_targets  # type: ignore[import-not-found]
    _ELIG_AVAILABLE = True
except ImportError:
    _ELIG_AVAILABLE = False
    eligible_targets = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(
    not _ELIG_AVAILABLE,
    reason="src/python/mtcojo_eligible_targets.py not yet landed (Wave 4)",
)


def test_only_mtag_novel_with_extreme_overlap_emitted():
    """target with MTAG-novel hit AND any gcov_int > 0.1 → emitted."""
    import numpy as np
    import pandas as pd

    mtag_novel = pd.DataFrame({"target_trait": ["bmi", "t2d"], "stratum": ["EUR", "EUR"]})
    # 2x2 intercept matrix; bmi-t2d gcov_int = 0.15 (extreme); t2d-sbp = 0.05 (mild)
    rkeys = ["bmi", "t2d", "sbp"]
    R = np.array([[1.0, 0.15, 0.02], [0.15, 1.0, 0.05], [0.02, 0.05, 1.0]])
    out = eligible_targets(mtag_novel, R, rkeys, threshold=0.1)
    assert "bmi" in set(out["target_trait"])  # has overlap > 0.1 with t2d
    assert "t2d" in set(out["target_trait"])  # has overlap > 0.1 with bmi


def test_mtag_null_targets_skipped():
    """Targets without MTAG-novel hits are NOT emitted regardless of overlap."""
    import numpy as np
    import pandas as pd

    mtag_novel = pd.DataFrame({"target_trait": ["bmi"], "stratum": ["EUR"]})
    rkeys = ["bmi", "sbp"]
    R = np.array([[1.0, 0.5], [0.5, 1.0]])  # high overlap but sbp is MTAG-null
    out = eligible_targets(mtag_novel, R, rkeys, threshold=0.1)
    assert "sbp" not in set(out["target_trait"])
