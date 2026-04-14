"""Plan 09-04 Task 2 — per-cohort Bonferroni effect-size test.

Behavior covered (D-03a + RESEARCH pitfalls #4, #5):
- compute_bonferroni: denominator = N_signals_tested_in_THIS_cohort
- check_same_direction: β_disc vs β_rep sign match (with NaN handling)
- posthoc_power: two-sided power at Bonferroni α given β_FIQT and rep SE
- compute_joint_criterion: Bonferroni AND coloc PP.H4 >= primary threshold
"""
import math
import sys
from pathlib import Path

import pandas as pd
import pytest

# Project-root resolver (pytest is normally invoked from project root but
# this keeps tests portable to pre-__init__ subdirectories).
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))


def test_bonferroni_denominator():
    """RESEARCH pitfall #4: α / N_in_cohort, not α / N_global (T-09-15)."""
    from compute_per_cohort_effect_size_test import compute_bonferroni

    assert compute_bonferroni(20) == pytest.approx(0.0025)
    assert compute_bonferroni(1) == pytest.approx(0.05)
    assert compute_bonferroni(100) == pytest.approx(0.0005)


def test_bonferroni_rejects_zero():
    from compute_per_cohort_effect_size_test import compute_bonferroni

    with pytest.raises(ValueError):
        compute_bonferroni(0)


def test_same_direction_positive():
    from compute_per_cohort_effect_size_test import check_same_direction

    assert check_same_direction(0.2, 0.15)
    assert check_same_direction(-0.2, -0.15)


def test_same_direction_opposite():
    from compute_per_cohort_effect_size_test import check_same_direction

    assert not check_same_direction(0.2, -0.15)
    assert not check_same_direction(-0.2, 0.15)


def test_same_direction_nan():
    from compute_per_cohort_effect_size_test import check_same_direction

    assert not check_same_direction(float("nan"), 0.1)
    assert not check_same_direction(0.1, float("nan"))


def test_posthoc_power_range():
    """Large effect + small SE should give high power; small effect -> low power."""
    from compute_per_cohort_effect_size_test import posthoc_power

    p = posthoc_power(beta_fiqt=0.3, se_rep=0.05, alpha=0.0025)
    assert 0 < p <= 1
    assert p > 0.8  # large effect, small SE → high power

    p_low = posthoc_power(beta_fiqt=0.01, se_rep=0.05, alpha=0.0025)
    assert 0 <= p_low < 0.5


def test_posthoc_power_nan_guards():
    from compute_per_cohort_effect_size_test import posthoc_power

    # NaN beta → NaN power
    assert math.isnan(posthoc_power(float("nan"), 0.05, 0.0025))
    # Zero or negative SE → NaN power
    assert math.isnan(posthoc_power(0.2, 0.0, 0.0025))
    assert math.isnan(posthoc_power(0.2, -0.01, 0.0025))


def test_joint_criterion_true():
    from compute_per_cohort_effect_size_test import compute_joint_criterion

    row = pd.Series({"replicated_bonferroni": True, "replicated_pph4_0.8": True})
    assert compute_joint_criterion(row, 0.8)


def test_joint_criterion_false_coloc():
    from compute_per_cohort_effect_size_test import compute_joint_criterion

    row = pd.Series({"replicated_bonferroni": True, "replicated_pph4_0.8": False})
    assert not compute_joint_criterion(row, 0.8)


def test_joint_criterion_false_bonferroni():
    from compute_per_cohort_effect_size_test import compute_joint_criterion

    row = pd.Series({"replicated_bonferroni": False, "replicated_pph4_0.8": True})
    assert not compute_joint_criterion(row, 0.8)


def test_joint_criterion_missing_keys_default_false():
    from compute_per_cohort_effect_size_test import compute_joint_criterion

    # Missing keys → False (defensive default for unjoined rows)
    assert not compute_joint_criterion(pd.Series({}), 0.8)


def test_process_cohort_end_to_end(tmp_path):
    """Smoke: merge 3 signals × 1 cohort through process_cohort and verify
    the derived columns (bonf_threshold, same_direction, power_posthoc,
    replicated_bonferroni, replicated_joint_0.8) exist and take plausible values."""
    from compute_per_cohort_effect_size_test import process_cohort

    effect_df = pd.DataFrame({
        "signal_id": ["s1", "s2", "s3"],
        "cohort": ["mvp_eur"] * 3,
        "beta_replication": [0.20, 0.18, -0.05],
        "se_replication":   [0.03, 0.04, 0.04],
        "p_replication":    [1e-10, 1e-5, 0.2],
    })
    fiqt_df = pd.DataFrame({
        "signal_id": ["s1", "s2", "s3"],
        "beta_discovery_FIQT": [0.22, 0.15, 0.10],  # note: s3 discovery +, rep -
    })
    coloc_df = pd.DataFrame({
        "signal_id": ["s1", "s2", "s3"],
        "cohort":    ["mvp_eur"] * 3,
        "replicated_pph4_0.5": [True, True, False],
        "replicated_pph4_0.7": [True, True, False],
        "replicated_pph4_0.8": [True, False, False],
        "replicated_pph4_0.9": [False, False, False],
    })

    out = process_cohort(effect_df, fiqt_df, coloc_df, cohort="mvp_eur")

    # α = 0.05 / 3 ≈ 0.01666...
    assert out["bonf_threshold"].unique()[0] == pytest.approx(0.05 / 3)

    # s1: strong effect, same direction → bonferroni True
    row_s1 = out[out["signal_id"] == "s1"].iloc[0]
    assert row_s1["same_direction"]
    assert row_s1["replicated_bonferroni"]
    assert row_s1["replicated_joint_0.8"]  # joint = bonf + pph4>=0.8

    # s3: opposite direction → same_direction False → bonferroni False
    row_s3 = out[out["signal_id"] == "s3"].iloc[0]
    assert not row_s3["same_direction"]
    assert not row_s3["replicated_bonferroni"]
    assert not row_s3["replicated_joint_0.8"]

    # s2: same dir + p=1e-5 < 0.0166 → bonferroni True, but pph4<0.8 → joint False
    row_s2 = out[out["signal_id"] == "s2"].iloc[0]
    assert row_s2["replicated_bonferroni"]
    assert not row_s2["replicated_joint_0.8"]

    # Post-hoc power column exists and values are in [0,1] or NaN
    assert "power_posthoc" in out.columns
    valid_power = out["power_posthoc"].dropna()
    assert ((valid_power >= 0) & (valid_power <= 1)).all()
