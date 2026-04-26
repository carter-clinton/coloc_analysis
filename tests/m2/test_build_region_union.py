"""Region union BED tests (D-M2-09).

Strict union of clumped + MTAG-novel + CPASSOC-novel leads, ±1 Mb windows,
bedtools default merge. Provenance JSON column preserved.

Wave 4 lands src/python/build_region_union.py.
"""
from __future__ import annotations

import pytest

try:
    from build_region_union import build_union  # type: ignore[import-not-found]
    _UNION_AVAILABLE = True
except ImportError:
    _UNION_AVAILABLE = False
    build_union = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(
    not _UNION_AVAILABLE,
    reason="src/python/build_region_union.py not yet landed (Wave 4)",
)


def test_strict_merge_default():
    """Overlapping ±1 Mb windows from two leads are merged into one interval."""
    import pandas as pd

    leads = pd.DataFrame(
        {
            "chrom": ["1", "1"],
            "pos": [1_000_000, 1_500_000],
            "source": ["clump", "mtag"],
        }
    )
    out = build_union(leads, window_bp=1_000_000)
    # Should collapse to 1 interval since windows overlap (0..2M and 0.5M..2.5M)
    assert len(out) == 1


def test_window_bp_is_one_megabase():
    """Default window is ±1 Mb per D-M2-09."""
    import pandas as pd

    leads = pd.DataFrame({"chrom": ["1"], "pos": [5_000_000], "source": ["clump"]})
    out = build_union(leads, window_bp=1_000_000)
    assert int(out.iloc[0]["start"]) == 4_000_000
    assert int(out.iloc[0]["end"]) == 6_000_000


def test_provenance_json_preserved():
    """Output rows must carry a provenance column listing contributing methods."""
    import pandas as pd

    leads = pd.DataFrame(
        {"chrom": ["1", "1"], "pos": [1_000_000, 1_100_000], "source": ["clump", "cpassoc"]}
    )
    out = build_union(leads, window_bp=1_000_000)
    prov = out.iloc[0]["provenance"]
    # provenance is a JSON-encoded list or dict referencing source methods
    assert "clump" in str(prov)
    assert "cpassoc" in str(prov)


def test_empty_input_empty_output():
    """No leads → empty BED."""
    import pandas as pd

    leads = pd.DataFrame(columns=["chrom", "pos", "source"])
    out = build_union(leads, window_bp=1_000_000)
    assert len(out) == 0
