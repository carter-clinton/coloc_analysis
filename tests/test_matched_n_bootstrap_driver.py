"""Tests for bootstrap_driver.py — per-bootstrap pseudo-sumstats + SuSiE refit.

Verifies:
- CLI argument parsing (--help exits 0)
- EUR sumstats loading with column normalization
- SE inflation integration with se_inflation.py
- Subprocess call to run_susie_rss.R (mocked)
- Seed determinism through the full driver path

References:
    - D-01b: Per-bootstrap Z_b ~ N(beta_hat/SE_matched, 1)
    - Phase 1 run_susie_rss.R reused verbatim
"""
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

# Project convention: sys.path.insert for flat-name imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "snakemake" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "python"))


@pytest.mark.phase4
class TestBootstrapDriverCLI:
    """Verify CLI argument parsing."""

    def test_help_exits_zero(self):
        """--help should exit 0 (argparse SystemExit)."""
        from bootstrap_driver import parse_args
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--help"])
        assert exc_info.value.code == 0

    def test_parse_required_args(self):
        """All required args parse correctly."""
        from bootstrap_driver import parse_args
        args = parse_args([
            "--trait", "t2d",
            "--trait-id", "0",
            "--region", "chr10_114p",
            "--bootstrap-idx", "1",
            "--eur-sumstats", "data/test.bgz",
            "--afr-n", "55525",
            "--ld-matrix-rds", "results/test.rds",
            "--output-fit-rds", "/tmp/test.fit.rds",
        ])
        assert args.trait == "t2d"
        assert args.trait_id == 0
        assert args.bootstrap_idx == 1
        assert args.afr_n == 55525.0


@pytest.mark.phase4
class TestLoadEurSumstats:
    """Verify EUR sumstats loading with column normalization."""

    def test_load_normalized_columns(self, tmp_path):
        """Columns like SNP/BETA/SE are normalized to variant_id/beta/se."""
        from bootstrap_driver import load_eur_sumstats
        tsv = tmp_path / "test.tsv"
        tsv.write_text("SNP\tCHR\tBP\tBETA\tSE\tN\n"
                        "rs1\t10\t100\t0.1\t0.02\t700000\n"
                        "rs2\t10\t200\t-0.05\t0.03\t700000\n")
        df = load_eur_sumstats(str(tsv))
        assert "variant_id" in df.columns
        assert "beta" in df.columns
        assert "se" in df.columns

    def test_raises_on_missing_columns(self, tmp_path):
        """Missing required columns -> ValueError."""
        from bootstrap_driver import load_eur_sumstats
        tsv = tmp_path / "bad.tsv"
        tsv.write_text("foo\tbar\n1\t2\n")
        with pytest.raises(ValueError, match="Missing required columns"):
            load_eur_sumstats(str(tsv))


@pytest.mark.phase4
class TestBootstrapDriverIntegration:
    """Integration test with mocked Rscript subprocess."""

    @patch("bootstrap_driver.subprocess.run")
    def test_rscript_call_contains_susie_rss(self, mock_run, tmp_path):
        """Verify Rscript invocation includes run_susie_rss.R and susie_policy.yaml."""
        from bootstrap_driver import parse_args, run_bootstrap

        # Create a minimal EUR sumstats file
        sumstats = tmp_path / "eur.tsv"
        data = pd.DataFrame({
            "SNP": [f"rs{i}" for i in range(10)],
            "CHR": [10] * 10,
            "BP": list(range(100, 110)),
            "BETA": np.random.default_rng(42).normal(0, 0.1, 10),
            "SE": np.full(10, 0.02),
            "N": [700000] * 10,
        })
        data.to_csv(sumstats, sep="\t", index=False)

        output_rds = tmp_path / "output" / "test.fit.rds"

        mock_run.return_value = MagicMock(
            returncode=0, stdout="OK\n", stderr=""
        )

        args = parse_args([
            "--trait", "t2d",
            "--trait-id", "0",
            "--region", "chr10_114p",
            "--bootstrap-idx", "1",
            "--eur-sumstats", str(sumstats),
            "--afr-n", "55525",
            "--ld-matrix-rds", str(tmp_path / "ld.rds"),
            "--output-fit-rds", str(output_rds),
        ])

        run_bootstrap(args)

        # Verify Rscript was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]

        # Check the command includes run_susie_rss.R
        assert any("run_susie_rss.R" in str(a) for a in call_args), \
            f"run_susie_rss.R not found in command: {call_args}"

        # Check susie_policy.yaml is passed
        assert any("susie_policy.yaml" in str(a) for a in call_args), \
            f"susie_policy.yaml not found in command: {call_args}"

    @patch("bootstrap_driver.subprocess.run")
    def test_seed_determinism_through_driver(self, mock_run, tmp_path):
        """Same inputs + same bootstrap_idx -> same pseudo-sumstats."""
        from bootstrap_driver import parse_args, load_eur_sumstats, inflate_se, compute_seed, draw_z_bootstrap

        sumstats = tmp_path / "eur.tsv"
        rng = np.random.default_rng(42)
        data = pd.DataFrame({
            "SNP": [f"rs{i}" for i in range(5)],
            "CHR": [10] * 5,
            "BP": list(range(100, 105)),
            "BETA": rng.normal(0, 0.1, 5),
            "SE": np.full(5, 0.02),
            "N": [700000] * 5,
        })
        data.to_csv(sumstats, sep="\t", index=False)

        df = load_eur_sumstats(str(sumstats))
        se_matched = inflate_se(df["se"].values, 700000, 55525)
        seed = compute_seed(0, 1, 1000)

        z1 = draw_z_bootstrap(df["beta"].values, se_matched, seed)
        z2 = draw_z_bootstrap(df["beta"].values, se_matched, seed)
        np.testing.assert_array_equal(z1, z2)
