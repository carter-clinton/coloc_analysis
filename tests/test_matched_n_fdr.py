"""Tests for BH-FDR correction across all r_g tests (D-04c).

Multiple-testing correction: Benjamini-Hochberg FDR at q < 0.05 across ALL
r_g tests in the matrix (not per-ancestry-pair, not trait-pair-stratified).
Matches Phase 5 D-01a pathway FDR convention.

References:
    - D-04c: BH-FDR q < 0.05 across all 35 r_g tests (30 cross + 5 bench)
    - D-04a: 10 trait pairs x 3 ancestry-pair strata = 30 cross-trait tests
    - D-04b: 5 same-trait EUR-AFR benchmarks
    - Research A-2: SE > 0.3 flagged as unreliable_se
    - config/matched_n.yaml: rg_fdr_q = 0.05
"""
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.python.apply_fdr import apply_bh_fdr


def _make_rg_raw_fixture(n_tests=35, seed=42):
    """Create a synthetic rg_raw.tsv with known p-values for testing."""
    rng = np.random.default_rng(seed)

    # Generate p-values: some small (significant), most moderate
    p_values = np.concatenate([
        rng.uniform(0.0001, 0.005, size=10),   # likely significant
        rng.uniform(0.01, 0.5, size=n_tests - 12),  # borderline
        np.array([np.nan, np.nan]),              # 2 NA p-values
    ])
    rng.shuffle(p_values[:n_tests - 2])  # shuffle non-NA

    se_values = np.concatenate([
        rng.uniform(0.05, 0.25, size=n_tests - 5),  # normal SE
        rng.uniform(0.35, 0.60, size=5),              # unreliable SE > 0.3
    ])
    rng.shuffle(se_values)

    rows = []
    traits = ["t2d", "stroke", "hypertension", "asthma", "bmi"]
    import itertools
    cross_pairs = list(itertools.combinations(traits, 2))
    ancestry_strata = ["EUR_EUR", "AFR_AFR", "EUR_AFR"]

    idx = 0
    # 30 cross-trait tests
    for t1, t2 in cross_pairs:
        for ap in ancestry_strata:
            a1, a2 = ap.split("_")
            rows.append({
                "trait1": t1, "trait2": t2,
                "ancestry1": a1, "ancestry2": a2,
                "is_global_benchmark": False,
                "rg": rng.uniform(-0.5, 0.9),
                "se": se_values[idx],
                "z": rng.uniform(-3, 3),
                "p": p_values[idx],
                "h2_obs_t1": rng.uniform(0.1, 0.5),
                "h2_obs_t2": rng.uniform(0.1, 0.5),
            })
            idx += 1

    # 5 same-trait EUR-AFR benchmarks
    for t in traits:
        rows.append({
            "trait1": t, "trait2": t,
            "ancestry1": "EUR", "ancestry2": "AFR",
            "is_global_benchmark": True,
            "rg": rng.uniform(0.5, 1.0),
            "se": se_values[idx],
            "z": rng.uniform(2, 5),
            "p": p_values[idx] if idx < len(p_values) else rng.uniform(0.001, 0.01),
            "h2_obs_t1": rng.uniform(0.1, 0.5),
            "h2_obs_t2": rng.uniform(0.1, 0.5),
        })
        idx += 1

    return pd.DataFrame(rows)


@pytest.mark.phase4
class TestBHFDR:
    """Test suite for D-04c BH-FDR correction."""

    def test_bh_fdr_across_all_tests(self):
        """Verify BH-FDR applied across ALL 35 r_g tests jointly (D-04c)."""
        df = _make_rg_raw_fixture()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f:
            df.to_csv(f.name, sep="\t", index=False)
            result = apply_bh_fdr(f.name, fdr_q=0.05, se_flag_threshold=0.3)

        # q_bh should exist for all valid-p rows
        valid = result["p"].notna()
        assert result.loc[valid, "q_bh"].notna().all()
        # fdr_significant should be boolean
        assert result["fdr_significant"].dtype == bool or result.loc[valid, "fdr_significant"].isin([True, False]).all()

    def test_bh_fdr_matches_independent_computation(self):
        """Verify our BH result matches a scipy-independent computation."""
        from statsmodels.stats.multitest import multipletests

        df = _make_rg_raw_fixture(n_tests=35, seed=123)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f:
            df.to_csv(f.name, sep="\t", index=False)
            result = apply_bh_fdr(f.name)

        valid = result["p"].notna()
        p_valid = df.loc[valid, "p"].values
        _, expected_q, _, _ = multipletests(p_valid, alpha=0.05, method="fdr_bh")

        np.testing.assert_allclose(
            result.loc[valid, "q_bh"].values, expected_q, rtol=1e-10
        )

    def test_na_p_preserved(self):
        """p=NaN rows preserved with q_bh=NA, fdr_significant=False."""
        df = _make_rg_raw_fixture()
        na_count = df["p"].isna().sum()
        assert na_count >= 2, "Fixture should have NA p-values"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f:
            df.to_csv(f.name, sep="\t", index=False)
            result = apply_bh_fdr(f.name)

        na_rows = result[result["p"].isna()]
        assert len(na_rows) == na_count
        assert na_rows["q_bh"].isna().all()
        assert (na_rows["fdr_significant"] == False).all()  # noqa: E712

    def test_unreliable_se_flag(self):
        """SE > 0.3 flagged as unreliable_se=True (research A-2)."""
        df = _make_rg_raw_fixture()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f:
            df.to_csv(f.name, sep="\t", index=False)
            result = apply_bh_fdr(f.name, se_flag_threshold=0.3)

        assert "unreliable_se" in result.columns
        # Rows with SE > 0.3 should be flagged
        expected = result["se"].abs() > 0.3
        pd.testing.assert_series_equal(
            result["unreliable_se"].astype(bool),
            expected.astype(bool),
            check_names=False,
        )
        assert result["unreliable_se"].any(), "Should have some unreliable SE rows"

    def test_output_tsv_written(self):
        """Verify output TSV is written when out_tsv is specified."""
        df = _make_rg_raw_fixture()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f_in:
            df.to_csv(f_in.name, sep="\t", index=False)
            with tempfile.NamedTemporaryFile(suffix=".tsv", delete=False) as f_out:
                apply_bh_fdr(f_in.name, out_tsv=f_out.name)
                result = pd.read_csv(f_out.name, sep="\t")

        assert "q_bh" in result.columns
        assert "fdr_significant" in result.columns
        assert "unreliable_se" in result.columns


@pytest.mark.phase4
def test_rg_matrix_schema():
    """D-06d: Verify rg_matrix.tsv has the exact required column set."""
    expected_columns = [
        "trait1", "trait2", "ancestry1", "ancestry2", "is_global_benchmark",
        "rg", "se", "z", "p", "h2_obs_t1", "h2_obs_t2",
        "q_bh", "fdr_significant", "unreliable_se",
    ]

    df = _make_rg_raw_fixture()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f:
        df.to_csv(f.name, sep="\t", index=False)
        result = apply_bh_fdr(f.name)

    assert list(result.columns) == expected_columns, (
        f"Column mismatch.\nExpected: {expected_columns}\nGot: {list(result.columns)}"
    )

    # Verify is_global_benchmark is present and has correct values
    assert "is_global_benchmark" in result.columns
    bench_rows = result[result["is_global_benchmark"] == True]  # noqa: E712
    assert len(bench_rows) == 5, f"Expected 5 global benchmarks, got {len(bench_rows)}"
