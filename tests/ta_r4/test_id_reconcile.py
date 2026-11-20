"""W3f 15.7b: ta_r4.id_reconcile.reconcile, the identity check both completeness gates use (F4, F6)."""
from __future__ import annotations

from ta_r4.id_reconcile import reconcile


def test_reconcile_exact_set_ok():
    r = reconcile(["a", "b", "c"], ["c", "a", "b"])
    assert r.ok
    assert (r.missing, r.extra, r.duplicated) == ([], [], [])


def test_reconcile_reports_missing():
    r = reconcile(range(1, 6), [1, 2, 4])
    assert not r.ok
    assert (r.missing, r.extra, r.duplicated) == ([3, 5], [], [])
    assert "missing=2" in r.summary()


def test_reconcile_reports_extra():
    r = reconcile(["a", "b"], ["a", "b", "z", "y"])
    assert not r.ok
    assert (r.missing, r.extra, r.duplicated) == ([], ["y", "z"], [])
    assert "extra=2" in r.summary()


def test_reconcile_reports_duplicates():
    r = reconcile(range(1, 4), [1, 1, 1, 2, 3, 3])
    assert not r.ok
    assert (r.missing, r.extra, r.duplicated) == ([], [], [1, 3])
    assert "duplicated=2" in r.summary()
    # the same count as the expected set is not enough: 3 copies of 1 for 1..3
    r = reconcile(range(1, 4), [1, 1, 1])
    assert (r.missing, r.duplicated) == ([2, 3], [1])
