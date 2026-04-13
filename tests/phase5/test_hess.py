"""Tests for HESS/rho-HESS local genetic covariance wrapper (Plan 05-04).

Tests cover:
  - harmonized_to_hess format conversion (columns, Z-score, effective N)
  - compare_pleiotropic_vs_background z-score comparison
  - Trait pair generation (10 pairs from 5 traits)
  - Shared ancestry filtering for trait pairs
  - validate_hess_panel_build placeholder
  - No shell=True in run_hess.py (AST-based detection)
"""
import ast
import csv
import math
import os
import sys
from pathlib import Path

import pytest

# Project root for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from run_hess import (
    compare_pleiotropic_vs_background,
    harmonized_to_hess,
    validate_hess_panel_build,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_harmonized_sumstats(tmp_path):
    """Create a minimal harmonized sumstats TSV for HESS format conversion.

    100 rows on chr22, with known BETA/SE values for Z-score verification.
    """
    outfile = tmp_path / "mock_harmonized.tsv"
    header = "CHR\tPOS\tSNP\tREF\tALT\tBETA\tSE\tP\tEAF\tN\n"
    rows = []
    for i in range(100):
        pos = 16000000 + i * 1000
        snp = f"rs{200000 + i}"
        beta = 0.5 if i == 0 else 0.1 * ((-1) ** i)
        se = 0.1 if i == 0 else 0.05
        p = 1e-5 if i == 0 else 0.5
        rows.append(
            f"22\t{pos}\t{snp}\tA\tG\t{beta:.6f}\t{se:.6f}\t{p:.8f}\t0.3\t50000\n"
        )
    outfile.write_text(header + "".join(rows))
    return outfile


@pytest.fixture()
def mock_hess_combined(tmp_path):
    """Create a mock combined rho-HESS output with known partition covariances.

    5 pleiotropic partitions (high covariance) + 50 background partitions (low).
    """
    outfile = tmp_path / "mock_combined.txt"
    header = "chr\tstart\tend\tlocal_rhog\tse\n"
    rows = []

    # 5 pleiotropic partitions overlapping regions in regions_curated.csv
    # FTO locus: chr16:53800000-54400000
    pleio_covs = [0.3, 0.4, 0.35, 0.5, 0.45]
    for i, cov in enumerate(pleio_covs):
        start = 53800000 + i * 100000
        end = start + 100000
        rows.append(f"16\t{start}\t{end}\t{cov}\t0.05\n")

    # 50 background partitions (on chr1, not overlapping any curated region)
    import random
    rng = random.Random(42)
    for i in range(50):
        start = 1000000 + i * 200000
        end = start + 200000
        cov = rng.gauss(0.1, 0.03)
        rows.append(f"1\t{start}\t{end}\t{cov:.4f}\t0.04\n")

    outfile.write_text(header + "".join(rows))
    return outfile


@pytest.fixture()
def mock_regions_curated(tmp_path):
    """Create a minimal regions_curated.csv matching the project format."""
    outfile = tmp_path / "regions_curated.csv"
    content = (
        "region_id,chr,start,end,lead_snp,gene,trait_list,source\n"
        "FTO_16q12,16,53800000,54400000,rs9939609,FTO,\"bmi;t2d;htn\",GIANT\n"
        "MC4R_18q21,18,56000000,56600000,rs17782313,MC4R,\"bmi;t2d\",GIANT\n"
    )
    outfile.write_text(content)
    return outfile


@pytest.fixture()
def mock_bim_grch37(tmp_path):
    """Create a mock .bim file with GRCh37 reference SNPs for build validation."""
    outfile = tmp_path / "test_panel.bim"
    # Include reference SNPs at correct GRCh37 positions
    rows = [
        "1\trs1\t0\t779322\tA\tG\n",
        "1\trs12\t0\t9513573\tC\tT\n",
        "1\trs100\t0\t55000\tA\tC\n",
    ]
    outfile.write_text("".join(rows))
    return outfile


# ---------------------------------------------------------------------------
# Test: harmonized_to_hess output columns
# ---------------------------------------------------------------------------


def test_harmonized_to_hess_columns(mock_harmonized_sumstats, tmp_path):
    """Verify HESS output has exactly columns SNP, A1, A2, Z, N."""
    out_path = tmp_path / "hess_format.tsv"
    harmonized_to_hess(
        input_path=str(mock_harmonized_sumstats),
        output_path=str(out_path),
    )

    with open(out_path) as f:
        header = f.readline().strip().split("\t")

    assert header == ["SNP", "A1", "A2", "Z", "N"], (
        f"Expected ['SNP', 'A1', 'A2', 'Z', 'N'], got {header}"
    )


# ---------------------------------------------------------------------------
# Test: Z-score computation
# ---------------------------------------------------------------------------


def test_z_score_computation(mock_harmonized_sumstats, tmp_path):
    """Verify Z = BETA/SE. First row: BETA=0.5, SE=0.1 => Z=5.0."""
    out_path = tmp_path / "hess_format.tsv"
    harmonized_to_hess(
        input_path=str(mock_harmonized_sumstats),
        output_path=str(out_path),
    )

    with open(out_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        first_row = next(reader)

    z_val = float(first_row["Z"])
    assert abs(z_val - 5.0) < 0.001, (
        f"Expected Z=5.0 (BETA=0.5/SE=0.1), got Z={z_val}"
    )


# ---------------------------------------------------------------------------
# Test: effective N for binary traits
# ---------------------------------------------------------------------------


def test_effective_n_binary(tmp_path):
    """Verify binary trait N computation: N_eff = 4/(1/n_case + 1/n_ctrl)."""
    # Create sumstats for a binary trait
    sumstats_path = tmp_path / "binary_sumstats.tsv"
    header = "CHR\tPOS\tSNP\tREF\tALT\tBETA\tSE\tP\tEAF\tN\n"
    rows = "22\t16000000\trs999\tA\tG\t0.2\t0.04\t1e-6\t0.3\t100000\n"
    sumstats_path.write_text(header + rows)

    out_path = tmp_path / "hess_binary.tsv"

    # t2d is binary: n_case=74124, n_ctrl=824006
    n_case = 74124
    n_ctrl = 824006
    expected_neff = 4.0 / (1.0 / n_case + 1.0 / n_ctrl)

    harmonized_to_hess(
        input_path=str(sumstats_path),
        output_path=str(out_path),
        trait="t2d",
        n_case=n_case,
        n_ctrl=n_ctrl,
    )

    with open(out_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        row = next(reader)

    actual_n = int(row["N"])
    # Allow rounding: int(round(expected_neff))
    assert actual_n == int(round(expected_neff)), (
        f"Expected N_eff={int(round(expected_neff))}, got N={actual_n}"
    )


# ---------------------------------------------------------------------------
# Test: compare_pleiotropic_vs_background
# ---------------------------------------------------------------------------


def test_compare_pleiotropic_vs_background(
    mock_hess_combined, mock_regions_curated
):
    """With mock data: 5 pleiotropic partitions (high cov) vs 50 background (low).

    Z-score should be positive and significant.
    """
    result = compare_pleiotropic_vs_background(
        combined_path=str(mock_hess_combined),
        regions_path=str(mock_regions_curated),
    )

    assert result["n_pleio_partitions"] == 5, (
        f"Expected 5 pleiotropic partitions, got {result['n_pleio_partitions']}"
    )
    assert result["n_bg_partitions"] == 50, (
        f"Expected 50 background partitions, got {result['n_bg_partitions']}"
    )

    # Pleiotropic mean should be higher than background
    assert result["mean_pleio"] > result["mean_bg"], (
        f"Expected mean_pleio > mean_bg, got {result['mean_pleio']} vs {result['mean_bg']}"
    )

    # Z-score should be positive (pleio > bg)
    assert result["z_score"] > 0, (
        f"Expected positive z_score, got {result['z_score']}"
    )

    # With these mock values, z-score should be significant (p < 0.05)
    assert result["p_value"] < 0.05, (
        f"Expected p_value < 0.05, got {result['p_value']}"
    )

    # Ratio should be > 1
    assert result["ratio"] > 1.0, (
        f"Expected ratio > 1.0, got {result['ratio']}"
    )

    # All expected keys present
    for key in ["mean_pleio", "mean_bg", "ratio", "z_score", "p_value",
                "n_pleio_partitions", "n_bg_partitions"]:
        assert key in result, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# Test: trait pair generation (10 pairs from 5 traits)
# ---------------------------------------------------------------------------


def test_trait_pair_generation():
    """Verify 10 unique trait pairs from 5 traits (C(5,2) = 10)."""
    traits = ["bmi", "t2d", "hypertension", "asthma", "stroke"]

    pairs = []
    for i, t1 in enumerate(traits):
        for t2 in traits[i + 1:]:
            pairs.append((t1, t2))

    assert len(pairs) == 10, f"Expected 10 pairs, got {len(pairs)}"

    # Verify specific expected pairs exist
    expected = [
        ("bmi", "t2d"),
        ("bmi", "hypertension"),
        ("bmi", "asthma"),
        ("bmi", "stroke"),
        ("t2d", "hypertension"),
        ("t2d", "asthma"),
        ("t2d", "stroke"),
        ("hypertension", "asthma"),
        ("hypertension", "stroke"),
        ("asthma", "stroke"),
    ]
    assert pairs == expected, f"Pair list mismatch: {pairs}"

    # No duplicates
    assert len(set(pairs)) == 10, "Duplicate pairs found"


# ---------------------------------------------------------------------------
# Test: shared ancestry filter
# ---------------------------------------------------------------------------


def test_shared_ancestry_filter():
    """Verify only shared ancestries between trait pairs are used.

    bmi [EUR, AFR, EAS] x hypertension [EUR, AFR, HIS] = [EUR, AFR]
    bmi [EUR, AFR, EAS] x asthma [EUR, AFR] = [EUR, AFR]
    t2d [EUR, TRANS, AFR, EAS] x stroke [EUR, AFR, EAS] = [EUR, AFR, EAS]
    """
    trait_ancestries = {
        "bmi": ["EUR", "AFR", "EAS"],
        "t2d": ["EUR", "TRANS", "AFR", "EAS"],
        "hypertension": ["EUR", "AFR", "HIS"],
        "asthma": ["EUR", "AFR"],
        "stroke": ["EUR", "AFR", "EAS"],
    }

    # bmi x hypertension
    shared = sorted(
        set(trait_ancestries["bmi"]) & set(trait_ancestries["hypertension"])
    )
    assert shared == ["AFR", "EUR"], f"bmi x hypertension: expected ['AFR', 'EUR'], got {shared}"

    # bmi x asthma
    shared = sorted(
        set(trait_ancestries["bmi"]) & set(trait_ancestries["asthma"])
    )
    assert shared == ["AFR", "EUR"], f"bmi x asthma: expected ['AFR', 'EUR'], got {shared}"

    # t2d x stroke
    shared = sorted(
        set(trait_ancestries["t2d"]) & set(trait_ancestries["stroke"])
    )
    assert shared == ["AFR", "EAS", "EUR"], f"t2d x stroke: expected ['AFR', 'EAS', 'EUR'], got {shared}"

    # Generate all pairs with shared ancestries (should get more than 10 unique combos)
    traits = ["bmi", "t2d", "hypertension", "asthma", "stroke"]
    all_pairs = []
    for i, t1 in enumerate(traits):
        for t2 in traits[i + 1:]:
            shared_anc = sorted(
                set(trait_ancestries.get(t1, []))
                & set(trait_ancestries.get(t2, []))
            )
            for anc in shared_anc:
                all_pairs.append((t1, t2, anc))

    # Verify no empty ancestry intersections
    for t1, t2, anc in all_pairs:
        assert anc in trait_ancestries[t1], f"{anc} not in {t1} ancestries"
        assert anc in trait_ancestries[t2], f"{anc} not in {t2} ancestries"


# ---------------------------------------------------------------------------
# Test: validate_hess_panel_build (with mock BIM)
# ---------------------------------------------------------------------------


def test_validate_panel_build(mock_bim_grch37, tmp_path):
    """Validate genome build check with mock BIM containing GRCh37 positions.

    The mock BIM has rs1 at chr1:779322 and rs12 at chr1:9513573, both
    correct GRCh37 positions. Should pass validation.
    """
    bfile_prefix = str(tmp_path / "test_panel")

    result = validate_hess_panel_build(bfile_prefix)

    # Should have matched at least the reference SNPs present in mock
    matched_snps = [snp for snp, info in result.items() if info["match"]]
    assert len(matched_snps) >= 2, (
        f"Expected >= 2 matched reference SNPs, got {len(matched_snps)}: {matched_snps}"
    )


def test_validate_panel_build_wrong_positions(tmp_path):
    """Validate that wrong positions raise ValueError."""
    bim_path = tmp_path / "wrong_panel.bim"
    # rs1 at wrong position (GRCh38 instead of GRCh37)
    bim_path.write_text("1\trs1\t0\t999999\tA\tG\n")

    with pytest.raises(ValueError, match="genome build mismatch"):
        validate_hess_panel_build(str(tmp_path / "wrong_panel"))


# ---------------------------------------------------------------------------
# Test: no shell=True in run_hess.py (AST-based detection)
# ---------------------------------------------------------------------------


def test_no_shell_true_in_run_hess():
    """Verify run_hess.py never uses shell=True in subprocess calls (T-05-18).

    Uses AST parsing to avoid false positives from comments/docstrings.
    """
    run_hess_path = PROJECT_ROOT / "src" / "python" / "run_hess.py"
    assert run_hess_path.exists(), f"run_hess.py not found at {run_hess_path}"

    with open(run_hess_path) as f:
        tree = ast.parse(f.read())

    shell_true_lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword):
            if node.arg == "shell" and isinstance(node.value, ast.Constant):
                if node.value.value is True:
                    shell_true_lines.append(node.lineno)

    assert len(shell_true_lines) == 0, (
        f"shell=True found at line(s) {shell_true_lines} in run_hess.py. "
        "All subprocess calls must use list args (T-05-18)."
    )
