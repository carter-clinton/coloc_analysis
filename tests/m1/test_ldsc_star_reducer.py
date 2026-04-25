"""Test the LDSC star-topology rg log reducer (gcov_int extraction).

Wave 3 implements ``src/python/reduce_ldsc_rg_matrix.py`` with a
``parse_rg_log`` function that consumes an LDSC ``--rg`` log file and
returns a DataFrame with columns ``[p1, p2, gcov_int, gcov_int_se]``
(plus rg, se, z, p, h2_obs, h2_obs_se, h2_int, h2_int_se).

This Wave 0 test:
- Asserts the LDSC rg log fixture is on disk and parseable.
- If reduce_ldsc_rg_matrix.parse_rg_log exists (Wave 3 landed), runs it
  on the fixture and asserts 3 rows + correct gcov_int values.
- Otherwise, pytest.skip with explicit reason — Wave 3 has not yet
  authored the module.

Plan reference: m1-00-preflight-and-environment-PLAN.md Task 1.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def test_ldsc_rg_log_fixture_present(fixtures_dir):
    """The 3-pair LDSC rg-log fixture exists and contains the summary table."""
    fp = fixtures_dir / "ldsc_rg_log_sample.log"
    assert fp.exists(), f"LDSC rg log fixture missing: {fp}"
    text = fp.read_text()
    assert "Summary of Genetic Correlation Results" in text, (
        "LDSC rg-log fixture missing the summary-table header"
    )
    # Three pairs (p1==focal, p2 in {t2d, hypertension, asthma}).
    assert text.count("bmi_EUR.sumstats.gz") >= 4, (
        "Expected focal trait to appear in fixture log >= 4 times"
    )
    assert "gcov_int" in text, "Fixture log must contain gcov_int column"


def test_parse_rg_log_three_pair_extraction(fixtures_dir):
    """If reduce_ldsc_rg_matrix.parse_rg_log exists (Wave 3), verify it.

    Skips with explicit reason when Wave 3 has not yet authored the module.
    """
    spec = importlib.util.find_spec("reduce_ldsc_rg_matrix")
    if spec is None:
        # Try src/python via project_root
        project_root = Path(__file__).resolve().parents[2]
        candidate = project_root / "src" / "python" / "reduce_ldsc_rg_matrix.py"
        if not candidate.exists():
            pytest.skip(
                "Wave 3 module src/python/reduce_ldsc_rg_matrix.py not yet "
                "created; this Wave 0 test asserts collection only and will "
                "pass once Wave 3 lands the parser."
            )

    # Try import; if attribute missing, still skip with explicit reason.
    try:
        from reduce_ldsc_rg_matrix import parse_rg_log  # type: ignore[import-not-found]
    except (ImportError, AttributeError):
        pytest.skip(
            "reduce_ldsc_rg_matrix.parse_rg_log not yet implemented; "
            "Wave 3 plan (m1-03) will land it."
        )

    fp = fixtures_dir / "ldsc_rg_log_sample.log"
    df = parse_rg_log(fp)

    # 3 pairs in the fixture: bmi vs {t2d, hypertension, asthma}
    assert len(df) == 3, f"Expected 3 pairs from fixture, got {len(df)}"

    required_cols = {"p1", "p2", "gcov_int"}
    missing = required_cols - set(df.columns)
    assert not missing, f"Reducer output missing columns: {missing}"

    # Verify gcov_int values match the fixture (0.1234, 0.0412, 0.9812)
    expected_gcov = sorted([0.1234, 0.0412, 0.9812])
    actual_gcov = sorted(df["gcov_int"].tolist())
    for got, want in zip(actual_gcov, expected_gcov):
        assert abs(got - want) < 1e-6, (
            f"gcov_int mismatch: got {got}, want {want}; full set {actual_gcov}"
        )
