"""W3a known-answer comparison (D-12b): Route C vs Route L per fit, and each vs the frozen record.

The live test does not assert equality (§B.10): mismatches are findings. It asserts the table is the
on-disk union of fit ids, with complete columns.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from .conftest import MAN_DIR, REPO_ROOT

from ta_r4 import known_answer_compare as kac

TABLE = MAN_DIR / "known_answer_W3a.tsv"
RSCRIPT = "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript"


def _fit(status="ok", sizes=(3, 2), pip=None):
    return {"status": status, "n_cs": len(sizes), "cs_sizes": tuple(sizes),
            "pip": dict(pip if pip is not None else {"rs1": 0.9, "rs2": 0.05, "rs3": 1e-3})}


def test_identical_fits_equal():
    r = kac.compare(_fit(), _fit())
    assert r["status_eq"] and r["n_cs_eq"] and r["cs_sizes_eq"] and r["variant_ids_eq"]
    assert r["max_abs_dpip"] == 0.0 and r["equal"] is True


def test_pip_perturbation_1e9_not_equal():
    b = _fit()
    b["pip"]["rs2"] += 1e-9
    r = kac.compare(_fit(), b)
    assert r["equal"] is False and r["status_eq"] and r["cs_sizes_eq"]
    assert abs(r["max_abs_dpip"] - 1e-9) < 1e-15


def test_cs_sizes_difference():
    r = kac.compare(_fit(sizes=(3, 2)), _fit(sizes=(3, 4)))
    assert r["n_cs_eq"] and not r["cs_sizes_eq"] and r["equal"] is False


def test_missing_variant_reported_not_nan_filled():
    b = _fit()
    del b["pip"]["rs3"]
    r = kac.compare(_fit(), b)
    assert r["variant_ids_eq"] is False and r["max_abs_dpip"] is None and r["equal"] is False
    assert r["n_only_c"] == 1 and r["n_only_l"] == 0


def test_early_exit_both_without_pip_equal():
    a, b = _fit("too_many_variants", ()), _fit("too_many_variants", ())
    a["pip"] = b["pip"] = None
    r = kac.compare(a, b)
    assert r["equal"] is True and r["max_abs_dpip"] is None


def test_compare_to_k2d():
    row = {"status": "ok", "n_CS": "2", "cs_sizes": "3;2"}
    assert kac.compare_to_k2d(row, _fit()) == {"status_eq": True, "n_cs_eq": True, "cs_sizes_eq": True}
    assert kac.compare_to_k2d({"status": "ok", "n_CS": "0", "cs_sizes": ""}, _fit(sizes=())) == \
        {"status_eq": True, "n_cs_eq": True, "cs_sizes_eq": True}
    r = kac.compare_to_k2d(row, _fit("non_converged", (3,)))
    assert r == {"status_eq": False, "n_cs_eq": False, "cs_sizes_eq": False}


def test_aggregate_against_frozen():
    fits = [_fit("ok", (1,))] * 48 + [_fit("too_many_variants", ())] * 24 + \
           [_fit("non_converged", (2,))] * 3 + [_fit("non_converged", ())] * 15 + [_fit("no_variants", ())] * 6
    agg = kac.aggregate(fits)
    assert agg["n"] == 96 and agg["non_empty"] == 51
    assert agg["status_counts"] == {"ok": 48, "too_many_variants": 24, "non_converged": 18, "no_variants": 6}
    assert all(kac.compare_aggregate(agg).values())
    agg2 = kac.aggregate(fits[1:] + [_fit("ok", ())])
    flags = kac.compare_aggregate(agg2)
    assert flags["non_empty_eq"] is False and flags["status_counts_eq"] is True


@pytest.mark.r4_heavy
def test_live_table_is_the_on_disk_union(monkeypatch):
    monkeypatch.setattr(kac, "RSCRIPT", RSCRIPT)
    if not (REPO_ROOT / "data/r4/results/repro_routeC").exists():
        pytest.skip("data/r4/results/repro_routeC absent (W3a fire not run)")
    rows = kac.build_table()
    for pair, (arm_c, arm_l) in kac.ROUTE_PAIRS.items():
        ids = kac.fit_ids_on_disk(arm_c) | kac.fit_ids_on_disk(arm_l)
        got = [(r["trait"], r["ancestry"], r["region_safe"]) for r in rows if r["pair"] == pair]
        assert len(got) == len(set(got)) == len(ids) and set(got) == ids
    for r in rows:
        assert list(r) == kac.COLUMNS and all(v != "" for v in r.values()), r
    with open(TABLE, newline="") as fh:
        committed = list(csv.DictReader(fh, delimiter="\t"))
    assert committed == rows
