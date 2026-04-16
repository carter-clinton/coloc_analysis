"""Tests for Tier A retention concordance metric (D-02a).

Primary metric: Fraction of AFR-discovered Tier A loci for which the
EUR-matched bootstrap median achieves Tier A (PP.H4 >= 0.8 AND at least
one QTL coloc >= 0.8). Computed per trait with 95% CI from bootstrap
distribution.

References:
    - D-02a: Primary concordance metric definition
    - D-02d: H7 pre-registered threshold (20pp absolute reduction)
    - D-02e: Phase 9 joint criterion explicitly NOT reused
"""
import csv
import os
import shutil
import subprocess
import sys

import pytest

FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__),
    "fixtures", "matched_n", "synthetic_bootstraps",
)
SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir,
    "src", "snakemake", "scripts", "compute_tier_a_retention.R",
)
# Normalize path
SCRIPT_PATH = os.path.normpath(SCRIPT_PATH)

# Find Rscript: conda env first, then PATH
_RSCRIPT_CANDIDATES = [
    "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript",
]


def _find_rscript():
    """Find a working Rscript binary."""
    for candidate in _RSCRIPT_CANDIDATES:
        if os.path.isfile(candidate):
            return candidate
    found = shutil.which("Rscript")
    if found:
        return found
    pytest.skip("Rscript not found on PATH or in known conda envs")


RSCRIPT = _find_rscript()


def _run_retention_script(out_dir, n_bootstraps=5):
    """Run compute_tier_a_retention.R on synthetic fixtures and return output paths."""
    out_retention = os.path.join(out_dir, "tier_a_retention.tsv")
    out_sign = os.path.join(out_dir, "sign_agreement.tsv")

    cmd = [
        RSCRIPT, SCRIPT_PATH,
        "--tier-assignments", os.path.join(FIXTURES_DIR, "tier_assignments.tsv"),
        "--coloc-dir", os.path.join(FIXTURES_DIR, "coloc"),
        "--unmatched-coloc-dir", os.path.join(FIXTURES_DIR, "full_eur_coloc"),
        "--out", out_retention,
        "--out-sign", out_sign,
        "--concordance-threshold", "0.8",
        "--n-bootstraps", str(n_bootstraps),
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        pytest.fail(
            f"compute_tier_a_retention.R failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

    return out_retention, out_sign


def _read_tsv(path):
    """Read a TSV file and return list of dicts."""
    with open(path, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


@pytest.mark.phase4
class TestTierARetention:
    """D-02a: Tier A retention from synthetic bootstrap fixtures."""

    def test_bootstrap_mean_retention(self, tmp_path):
        """Verify bootstrap mean Tier A retention = 0.6 on synthetic fixture.

        Fixture design: 5 AFR Tier A loci x 5 bootstraps, each bootstrap
        retains exactly 3/5 loci -> retention = 0.6 for every bootstrap.
        """
        out_ret, _ = _run_retention_script(str(tmp_path), n_bootstraps=5)
        rows = _read_tsv(out_ret)

        assert len(rows) == 1, f"Expected 1 trait row, got {len(rows)}"
        row = rows[0]

        assert row["trait"] == "test_trait"
        assert int(row["n_afr_tier_a"]) == 5
        assert int(row["n_bootstraps"]) == 5

        mean_ret = float(row["mean_retention"])
        assert abs(mean_ret - 0.6) < 0.001, (
            f"Expected mean_retention=0.6, got {mean_ret}"
        )

    def test_ci_contains_true_retention(self, tmp_path):
        """95% CI must contain the true retention value of 0.6.

        Since all 5 bootstraps have identical retention=0.6, CI should be
        [0.6, 0.6] (or very close due to quantile interpolation).
        """
        out_ret, _ = _run_retention_script(str(tmp_path), n_bootstraps=5)
        rows = _read_tsv(out_ret)
        row = rows[0]

        ci_lo = float(row["ci95_lo"])
        ci_hi = float(row["ci95_hi"])

        assert ci_lo <= 0.6 + 0.001, f"CI lower bound {ci_lo} > 0.6"
        assert ci_hi >= 0.6 - 0.001, f"CI upper bound {ci_hi} < 0.6"

    def test_unmatched_concordance_present(self, tmp_path):
        """D-02d: unmatched_concordance column present and correct.

        Fixture: 4/5 loci are Tier A at full EUR N -> unmatched = 0.8.
        """
        out_ret, _ = _run_retention_script(str(tmp_path), n_bootstraps=5)
        rows = _read_tsv(out_ret)
        row = rows[0]

        assert "unmatched_concordance" in row, "Missing unmatched_concordance column"
        unmatched = float(row["unmatched_concordance"])
        assert abs(unmatched - 0.8) < 0.001, (
            f"Expected unmatched_concordance=0.8, got {unmatched}"
        )

    def test_output_columns(self, tmp_path):
        """Verify output TSV has all required columns per D-06a."""
        out_ret, _ = _run_retention_script(str(tmp_path), n_bootstraps=5)
        rows = _read_tsv(out_ret)

        required_cols = [
            "trait", "n_afr_tier_a", "mean_retention",
            "ci95_lo", "ci95_hi", "n_bootstraps", "unmatched_concordance",
        ]
        for col in required_cols:
            assert col in rows[0], f"Missing required column: {col}"

    def test_sign_agreement_output(self, tmp_path):
        """D-02c: sign agreement TSV is produced with correct schema."""
        _, out_sign = _run_retention_script(str(tmp_path), n_bootstraps=5)
        rows = _read_tsv(out_sign)

        assert len(rows) == 1
        row = rows[0]

        required_cols = ["trait", "n_loci_checked", "n_sign_agree", "frac_sign_agree"]
        for col in required_cols:
            assert col in row, f"Missing column: {col}"

        # All fixtures have sign_agree=1
        frac = float(row["frac_sign_agree"])
        assert frac == 1.0, f"Expected 100% sign agreement, got {frac}"


@pytest.mark.phase4
class TestD02eGuard:
    """Regression guard: D-02e Phase 9 joint criterion must NOT be reused."""

    def test_d02e_comment_in_script(self):
        """The script header must contain the D-02e exclusion comment."""
        with open(SCRIPT_PATH) as f:
            content = f.read()

        assert "D-02e EXPLICITLY NOT REUSED" in content, (
            "Missing D-02e guard comment in compute_tier_a_retention.R header"
        )

    def test_d02a_comment_in_script(self):
        """The script header must reference D-02a as PRIMARY METRIC."""
        with open(SCRIPT_PATH) as f:
            content = f.read()

        assert "D-02a PRIMARY METRIC" in content, (
            "Missing D-02a PRIMARY METRIC comment in script header"
        )
