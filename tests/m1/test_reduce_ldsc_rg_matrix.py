"""Test the LDSC star-topology rg-log reducer (m1-03 Wave 3).

Coverage targets per m1-03-PLAN Task 1 step (C):
- parse_rg_log on focal_0 fixture (2 pairs)
- build_intercept_matrix on 3-trait fixture set (3x3 symmetric, diag=1.0)
- validate_self_consistency on clean and broken matrices
- validate_expected_intercept_heuristics flags within-GLGC EUR deviations

The reducer is `src/python/reduce_ldsc_rg_matrix.py` (Wave 3 module);
this test imports it via the conftest sys.path injection.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from reduce_ldsc_rg_matrix import (  # type: ignore[import-not-found]
    parse_rg_log,
    build_intercept_matrix,
    build_long_format,
    validate_self_consistency,
    validate_expected_intercept_heuristics,
    key_from_path,
)


# Three-trait synthetic key set used across the tests; mirrors the
# focal_0 / focal_1 fixture log filenames.
TRAIT_KEYS_3 = sorted([
    "bmi.EUR.GIANT-UKBB.2018",
    "t2d.EUR.DIAMANTE.2022",
    "sbp.EUR.Evangelou-ICBP-UKBB.2018",
])


def test_parse_rg_log_focal_0_returns_two_pairs(fixtures_dir: Path) -> None:
    """focal_0 fixture has 2 pairs (focal=bmi, others={t2d, sbp})."""
    df = parse_rg_log(fixtures_dir / "ldsc_rg_log_focal_0.log")
    assert len(df) == 2, f"expected 2 pairs from focal_0 fixture, got {len(df)}"
    required = {"p1", "p2", "rg", "rg_se", "gcov_int", "gcov_int_se"}
    missing = required - set(df.columns)
    assert not missing, f"reducer output missing columns {missing}"
    # gcov_int values from the fixture are 0.1234 and 0.0412
    expected_gcov = sorted([0.1234, 0.0412])
    actual_gcov = sorted(df["gcov_int"].tolist())
    for got, want in zip(actual_gcov, expected_gcov):
        assert abs(got - want) < 1e-6, f"got {got}, want {want}"


def test_parse_rg_log_focal_1_returns_one_pair(fixtures_dir: Path) -> None:
    """focal_1 fixture has 1 pair (focal=t2d, other=sbp)."""
    df = parse_rg_log(fixtures_dir / "ldsc_rg_log_focal_1.log")
    assert len(df) == 1, f"expected 1 pair from focal_1 fixture, got {len(df)}"
    assert abs(df["gcov_int"].iloc[0] - 0.0871) < 1e-6


def test_key_from_path_strips_sumstats_suffix() -> None:
    """key_from_path returns the D-16 trait key (drops .sumstats.gz)."""
    p = "data/processed/ldsc_overlap/munged/bmi.EUR.GIANT-UKBB.2018.sumstats.gz"
    assert key_from_path(p) == "bmi.EUR.GIANT-UKBB.2018"


def test_build_intercept_matrix_3x3_symmetric_diag_one(
    fixtures_dir: Path, tmp_path: Path,
) -> None:
    """Symmetric 3x3 matrix with diag=1.0 from the 2 fixture logs."""
    # Stage the 2 fixture logs into a tmp dir so build_intercept_matrix's
    # log_dir.glob("focal_*.log") sees them.
    log_dir = tmp_path / "rg_logs"
    log_dir.mkdir()
    (log_dir / "focal_0.log").write_text(
        (fixtures_dir / "ldsc_rg_log_focal_0.log").read_text()
    )
    (log_dir / "focal_1.log").write_text(
        (fixtures_dir / "ldsc_rg_log_focal_1.log").read_text()
    )

    mat = build_intercept_matrix(log_dir, TRAIT_KEYS_3)
    assert mat.shape == (3, 3)
    # Diagonal is 1.0
    for k in TRAIT_KEYS_3:
        assert abs(mat.at[k, k] - 1.0) < 1e-9
    # Symmetry within numerical tolerance
    diff = (mat.values - mat.values.T)
    assert np.nanmax(np.abs(diff)) < 1e-9
    # Off-diagonals match the fixture gcov_int values
    assert abs(mat.at["bmi.EUR.GIANT-UKBB.2018", "t2d.EUR.DIAMANTE.2022"] - 0.1234) < 1e-6
    assert abs(mat.at["bmi.EUR.GIANT-UKBB.2018", "sbp.EUR.Evangelou-ICBP-UKBB.2018"] - 0.0412) < 1e-6
    assert abs(mat.at["t2d.EUR.DIAMANTE.2022", "sbp.EUR.Evangelou-ICBP-UKBB.2018"] - 0.0871) < 1e-6


def test_build_long_format_emits_per_pair_rows(
    fixtures_dir: Path, tmp_path: Path,
) -> None:
    """Long-form TSV has one row per pair with rg, rg_se, gcov_int."""
    log_dir = tmp_path / "rg_logs"
    log_dir.mkdir()
    (log_dir / "focal_0.log").write_text(
        (fixtures_dir / "ldsc_rg_log_focal_0.log").read_text()
    )
    (log_dir / "focal_1.log").write_text(
        (fixtures_dir / "ldsc_rg_log_focal_1.log").read_text()
    )
    long = build_long_format(log_dir, TRAIT_KEYS_3)
    # 2 pairs from focal_0 + 1 pair from focal_1 = 3 rows.
    assert len(long) == 3
    assert set(["trait_a", "trait_b", "rg", "rg_se", "gcov_int", "gcov_int_se"]).issubset(long.columns)


def test_validate_self_consistency_clean_returns_no_warnings() -> None:
    """A symmetric matrix with diag=1.0 produces zero warnings."""
    mat = pd.DataFrame(
        [[1.0, 0.1, 0.2], [0.1, 1.0, 0.3], [0.2, 0.3, 1.0]],
        index=TRAIT_KEYS_3, columns=TRAIT_KEYS_3,
    )
    warnings = validate_self_consistency(mat)
    assert warnings == [], f"clean matrix should yield no warnings, got: {warnings}"


def test_validate_self_consistency_broken_detects_asymmetry() -> None:
    """Asymmetric matrix triggers a symmetry-violation warning."""
    mat = pd.DataFrame(
        [[1.0, 0.1, 0.2], [0.5, 1.0, 0.3], [0.2, 0.3, 1.0]],  # 0.5 != 0.1
        index=TRAIT_KEYS_3, columns=TRAIT_KEYS_3,
    )
    warnings = validate_self_consistency(mat, tol=1e-6)
    assert any("Symmetry violation" in w for w in warnings), warnings


def test_validate_self_consistency_broken_diagonal() -> None:
    """Diagonal not ~1.0 triggers a diagonal warning."""
    mat = pd.DataFrame(
        [[0.5, 0.1, 0.2], [0.1, 1.0, 0.3], [0.2, 0.3, 1.0]],  # diag[0]=0.5
        index=TRAIT_KEYS_3, columns=TRAIT_KEYS_3,
    )
    warnings = validate_self_consistency(mat)
    assert any("Diagonal" in w for w in warnings), warnings


def test_heuristic_within_glgc_lipids_eur_flags_deviations() -> None:
    """Within-GLGC EUR lipid pair with intercept far from 1.0 is flagged."""
    keys = sorted([
        "ldl.EUR.GLGC.2021",
        "hdl.EUR.GLGC.2021",
        "tg.EUR.GLGC.2021",
    ])
    mat = pd.DataFrame(
        [[1.0, 0.2, 0.2], [0.2, 1.0, 0.2], [0.2, 0.2, 1.0]],  # 0.2 deviates
        index=keys, columns=keys,
    )
    warnings = validate_expected_intercept_heuristics(mat)
    assert len(warnings) >= 1, (
        "Expected at least one within-GLGC EUR lipid deviation warning, got: "
        f"{warnings}"
    )


def test_heuristic_within_glgc_lipids_eur_clean_passes() -> None:
    """Within-GLGC EUR lipid pair with intercept ~1.0 is NOT flagged."""
    keys = sorted([
        "ldl.EUR.GLGC.2021",
        "hdl.EUR.GLGC.2021",
        "tg.EUR.GLGC.2021",
    ])
    mat = pd.DataFrame(
        [[1.0, 0.95, 1.05], [0.95, 1.0, 1.02], [1.05, 1.02, 1.0]],
        index=keys, columns=keys,
    )
    warnings = validate_expected_intercept_heuristics(mat)
    assert warnings == [], f"clean within-GLGC matrix should pass, got: {warnings}"


def test_parse_rg_log_handles_missing_gcov_column(tmp_path: Path) -> None:
    """Logs without a Summary table yield empty DataFrame (no crash)."""
    fp = tmp_path / "broken.log"
    fp.write_text(
        "Beginning analysis at Sat Apr 25 06:00:00 2026\n"
        "(no Summary of Genetic Correlation Results table)\n"
        "Analysis finished\n"
    )
    df = parse_rg_log(fp)
    assert df.empty
