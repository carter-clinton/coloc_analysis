"""Phase 1 -- min_abs_corr sweep structure + soft monotonicity test.
REQ-2 acceptance #3 (sweep >=3 values) + REQ-2 implicit monotonicity (Pitfall 5 soft policy).
"""
import json
from pathlib import Path
import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures"
FLAG_FILE = Path(__file__).parent / "monotonicity_flags.json"
SAMPLE_JSON = FIXTURE_DIR / "sample_susie_output.json"


@pytest.fixture
def sample_output():
    if not SAMPLE_JSON.exists():
        pytest.skip(f"Fixture {SAMPLE_JSON} not yet created (produced by Task 1-01-08 dry-run/smoke)")
    return json.loads(SAMPLE_JSON.read_text())


def test_three_sweep_values(sample_output):
    sweep = sample_output.get("min_abs_corr_sweep")
    assert sweep is not None, "min_abs_corr_sweep missing from JSON"
    assert len(sweep) == 3, f"Expected 3 sweep rows, got {len(sweep)}"
    macors = sorted(float(r["min_abs_corr"]) for r in sweep)
    assert macors == [0.1, 0.5, 0.9], f"Expected [0.1,0.5,0.9], got {macors}"


def test_monotonic_or_flag(sample_output):
    sweep = sample_output.get("min_abs_corr_sweep") or []
    by_macor = {float(r["min_abs_corr"]): int(r["n_CS"]) for r in sweep}
    n01 = by_macor.get(0.1, 0)
    n05 = by_macor.get(0.5, 0)
    n09 = by_macor.get(0.9, 0)
    if not (n01 >= n05 >= n09):
        flags = json.loads(FLAG_FILE.read_text()) if FLAG_FILE.exists() else []
        flags.append({
            "file": str(SAMPLE_JSON),
            "n_CS_by_macor": {"0.1": n01, "0.5": n05, "0.9": n09},
            "note": "Pitfall 5 -- non-monotonic sweep flagged for QC dashboard review",
        })
        FLAG_FILE.write_text(json.dumps(flags, indent=2))
        pytest.xfail("Non-monotonic -- flagged in monotonicity_flags.json (soft per Pitfall 5)")
    assert n01 >= n05 >= n09
