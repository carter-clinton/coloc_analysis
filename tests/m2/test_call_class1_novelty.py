"""Class 1 novelty filter tests (REQ-NOVELTY-CLASS-1, D-M2-05).

Per Amendment §7.1: Class 1 = high-confidence joint-signal novelty
(MTAG ∩ CPASSOC, ±500 kb GWAS Catalog window enforcement).

Wave 5 lands src/python/call_class1_novelty.py.
"""
from __future__ import annotations

import pytest

try:
    from call_class1_novelty import call_novelty  # type: ignore[import-not-found]
    _NOVELTY_AVAILABLE = True
except ImportError:
    _NOVELTY_AVAILABLE = False
    call_novelty = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(
    not _NOVELTY_AVAILABLE,
    reason="src/python/call_class1_novelty.py not yet landed (Wave 5)",
)


def test_mtag_or_cpassoc_pmin_5e8_admitted():
    """Loci with MTAG p<5e-8 OR CPASSOC p<5e-8 are admitted to novelty triage."""
    import pandas as pd

    leads = pd.DataFrame(
        {
            "chrom": ["1"],
            "pos": [1_000_000],
            "mtag_p": [1e-9],
            "cpassoc_p": [0.5],
            "max_single_trait_p": [0.1],
        }
    )
    catalog = pd.DataFrame(columns=["chrom", "pos"])  # empty catalog
    out = call_novelty(leads, catalog, window_bp=500_000)
    assert len(out) == 1


def test_max_single_trait_p_above_threshold_required():
    """If max single-trait p < 5e-8, NOT joint-signal novel (single trait already calls)."""
    import pandas as pd

    leads = pd.DataFrame(
        {
            "chrom": ["1"],
            "pos": [1_000_000],
            "mtag_p": [1e-9],
            "cpassoc_p": [1e-9],
            "max_single_trait_p": [1e-10],  # already single-trait significant
        }
    )
    catalog = pd.DataFrame(columns=["chrom", "pos"])
    out = call_novelty(leads, catalog, window_bp=500_000)
    assert len(out) == 0


def test_catalog_window_500kb_enforced():
    """Lead within ±500 kb of a GWAS Catalog hit is NOT novel."""
    import pandas as pd

    leads = pd.DataFrame(
        {
            "chrom": ["1"],
            "pos": [1_000_000],
            "mtag_p": [1e-9],
            "cpassoc_p": [1e-9],
            "max_single_trait_p": [0.1],
        }
    )
    catalog = pd.DataFrame({"chrom": ["1"], "pos": [1_000_500]})  # 500 bp away
    out = call_novelty(leads, catalog, window_bp=500_000)
    assert len(out) == 0


def test_mtag_intersect_cpassoc_high_confidence():
    """Joint MTAG ∩ CPASSOC novelty is tagged confidence=high."""
    import pandas as pd

    leads = pd.DataFrame(
        {
            "chrom": ["1"],
            "pos": [1_000_000],
            "mtag_p": [1e-9],
            "cpassoc_p": [1e-9],
            "max_single_trait_p": [0.1],
        }
    )
    catalog = pd.DataFrame(columns=["chrom", "pos"])
    out = call_novelty(leads, catalog, window_bp=500_000)
    assert len(out) == 1
    assert out.iloc[0].get("confidence", "") == "high"
