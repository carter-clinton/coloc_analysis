"""m2_stratum_keys deterministic enumeration tests (D-M2-06, D-M2-Q6).

Carter-locked: _MIN_PER_STRATUM = 3 (NOT 5 from research default).
STRATA = ('EUR', 'AFR', 'TRANS'); MULTI ancestry maps to TRANS.

Wave 0 Task 7 lands src/python/m2_stratum_keys.py.
"""
from __future__ import annotations

from pathlib import Path

import pytest

try:
    from m2_stratum_keys import (  # type: ignore[import-not-found]
        keys_for_stratum,
        enforce_stratum_floor,
        STRATA,
        _MIN_PER_STRATUM,
        _MAX_PER_STRATUM,
    )
    _MOD_AVAILABLE = True
except ImportError:
    _MOD_AVAILABLE = False
    keys_for_stratum = None  # type: ignore[assignment]
    enforce_stratum_floor = None  # type: ignore[assignment]
    STRATA = ()  # type: ignore[assignment]
    _MIN_PER_STRATUM = None  # type: ignore[assignment]
    _MAX_PER_STRATUM = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(
    not _MOD_AVAILABLE,
    reason="src/python/m2_stratum_keys.py not yet landed (Wave 0 Task 7)",
)


def test_min_per_stratum_locked_at_3():
    """D-M2-Q6 — Carter-locked floor at 3, NOT 5 (research default rejected)."""
    assert _MIN_PER_STRATUM == 3
    assert _MAX_PER_STRATUM == 9


def test_strata_locked():
    """STRATA tuple locked at (EUR, AFR, TRANS) per D-M2-06."""
    assert STRATA == ("EUR", "AFR", "TRANS")


def test_eur_returns_at_least_3_keys(trait_inventory_yaml):
    """EUR is the densest stratum; expected ≥3 active EUR cells in inventory."""
    if not trait_inventory_yaml.exists():
        pytest.skip("config/trait_inventory.yaml missing")
    keys = keys_for_stratum(trait_inventory_yaml, "EUR")
    assert len(keys) >= 3, f"EUR keys={keys}"


def test_invalid_stratum_raises():
    """Stratum not in STRATA raises ValueError."""
    with pytest.raises(ValueError):
        keys_for_stratum(Path("config/trait_inventory.yaml"), "FOO")


def test_floor_violation_raises():
    """enforce_stratum_floor raises AssertionError below _MIN_PER_STRATUM."""
    with pytest.raises(AssertionError):
        enforce_stratum_floor(["x", "y"], "AFR")


def test_floor_satisfied_passes():
    """Exactly 3 keys passes the floor."""
    enforce_stratum_floor(["x", "y", "z"], "AFR")
