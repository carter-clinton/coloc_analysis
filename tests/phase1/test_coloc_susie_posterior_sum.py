"""Phase 1 Wave 4 (01-04) -- posterior sum property test for run_coloc_susie.R.

For every row in the susie_pairs array, sum(PP.H0..PP.H4) must equal
approximately 1.0. This is a mathematical property of coloc.susie output
(the five posteriors form a mutually-exclusive hypothesis partition) and
functions as a sanity check against silent bugs in the compat layer.

Also checks the best-pairwise 'summary' block (when status == "success").
Runs against the synthetic fixture; real end-to-end validation is deferred
to Plan 01-06.
"""
import json
from pathlib import Path

import pytest

PHASE1_ROOT = Path(__file__).resolve().parent
FIXTURE = PHASE1_ROOT / "fixtures" / "expected_coloc_susie_output.json"
PP_KEYS = ["PP.H0.abf", "PP.H1.abf", "PP.H2.abf", "PP.H3.abf", "PP.H4.abf"]
TOL = 1e-4


@pytest.fixture(scope="module")
def fixture_data():
    assert FIXTURE.exists(), f"Fixture not found: {FIXTURE}"
    return json.loads(FIXTURE.read_text())


def _row_sum(row):
    return sum(float(row[k]) for k in PP_KEYS)


def test_susie_pairs_sum_to_unity(fixture_data):
    pairs = fixture_data.get("susie_pairs", [])
    assert pairs, "fixture has empty susie_pairs (expected at least one row for this test)"
    for i, row in enumerate(pairs):
        s = _row_sum(row)
        assert abs(s - 1.0) < TOL, (
            f"susie_pairs[{i}] posterior sum {s:.6f} deviates from 1.0 by > {TOL} "
            f"(row: {row})"
        )


def test_best_pairwise_summary_sums_to_unity(fixture_data):
    if fixture_data.get("status") != "success":
        pytest.skip("status != success; summary is the no-signal sentinel")
    summary = fixture_data["summary"]
    if not all(k in summary for k in PP_KEYS):
        pytest.skip("summary missing PP.*.abf keys (no_signal path)")
    s = _row_sum(summary)
    assert abs(s - 1.0) < TOL, (
        f"best-pairwise summary posterior sum {s:.6f} deviates from 1.0 by > {TOL}"
    )


def test_posteriors_in_unit_interval(fixture_data):
    """Additional sanity: each posterior must lie in [0, 1]."""
    for i, row in enumerate(fixture_data.get("susie_pairs", [])):
        for k in PP_KEYS:
            v = float(row[k])
            assert 0.0 <= v <= 1.0, f"susie_pairs[{i}].{k} = {v} is out of [0,1]"
