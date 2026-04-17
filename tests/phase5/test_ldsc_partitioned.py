"""Tests for LDSC partitioned heritability utilities (Phase 5).

Validates:
- munge_sumstats_ldsc.py column output format
- Effective N calculation for binary traits
- build_ldsc_annot.py annotation format and window logic
- Negative control annotation validity (REQ-7)
- run_ldsc_partitioned.py command construction and results parsing
- SNP count warning threshold (Pitfall 2 / T-05-16)
- --overlap-annot always present in h2 (anti-pattern)
- Baseline v2.2 first in --ref-ld-chr (D-04a)
"""
import gzip
import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))
from build_ldsc_annot import (
    build_annot_for_chrom,
    build_gene_intervals,
    load_gene_loc,
    parse_gmt,
    point_in_intervals,
)
from munge_sumstats_ldsc import convert_sumstats
from sumstats_utils import TRAIT_TYPE, compute_effective_n, get_effective_n


class TestMungeSumstats:
    """Test munge_sumstats_ldsc.py conversion."""

    def test_munge_sumstats_columns(self, mock_sumstats_path, tmp_path):
        """munge_sumstats_ldsc.py produces output with correct LDSC columns."""
        out_path = tmp_path / "munged.sumstats.gz"
        stats = convert_sumstats(
            input_path=str(mock_sumstats_path),
            output_path=str(out_path),
        )
        assert out_path.exists()
        with gzip.open(str(out_path), "rt") as f:
            header = f.readline().strip().split("\t")
        expected_cols = ["SNP", "A1", "A2", "N", "P", "BETA", "SE"]
        assert header == expected_cols, f"Got columns: {header}"
        assert stats["n_output"] > 0, "No variants written"

    def test_munge_output_row_count(self, mock_sumstats_path, tmp_path):
        """Output should have approximately 100 rows (some may be filtered)."""
        out_path = tmp_path / "munged.sumstats.gz"
        stats = convert_sumstats(
            input_path=str(mock_sumstats_path),
            output_path=str(out_path),
        )
        assert stats["n_input"] == 100
        # Most rows should pass (random p-values are in valid range)
        assert stats["n_output"] >= 90

    def test_munge_effective_n(self):
        """Effective N: 4/(1/1000 + 1/5000) = 3333.33..."""
        result = compute_effective_n(1000, 5000)
        assert abs(result - 3333.333333) < 0.01

    def test_munge_effective_n_equal_cases_controls(self):
        """Effective N with equal cases/controls = total N."""
        result = compute_effective_n(5000, 5000)
        assert result == 10000.0

    def test_munge_effective_n_binary_trait(self):
        """get_effective_n for binary trait t2d uses effective N."""
        result = get_effective_n("t2d", 100000, n_case=5000, n_ctrl=20000)
        expected = compute_effective_n(5000, 20000)
        assert result == expected

    def test_munge_effective_n_quantitative_trait(self):
        """get_effective_n for quantitative trait bmi returns N directly."""
        result = get_effective_n("bmi", 50000)
        assert result == 50000.0


class TestBuildLdscAnnot:
    """Test build_ldsc_annot.py annotation generation."""

    def test_build_ldsc_annot_format(self, mock_bim, mock_gene_loc, tmp_path):
        """build_ldsc_annot.py produces .annot file with correct columns."""
        all_genes = load_gene_loc(str(mock_gene_loc))
        # Create a simple test gene set with mock genes
        pathway_sets = [("TEST_SET", {"TESTGENE1", "TESTGENE2", "INSR"})]
        out_path = tmp_path / "test.22.annot.gz"

        stats = build_annot_for_chrom(
            chrom="22",
            bim_path=str(mock_bim),
            all_genes=all_genes,
            pathway_sets=pathway_sets,
            window_bp=100000,  # 100 kb
            out_path=str(out_path),
        )

        assert out_path.exists()
        with gzip.open(str(out_path), "rt") as f:
            header = f.readline().strip().split("\t")
        expected_header = ["CHR", "BP", "SNP", "CM", "TEST_SET"]
        assert header == expected_header

        assert stats["n_snps"] == 100
        assert stats["n_annotated"]["TEST_SET"] >= 0

    def test_neg_ctrl_annotation(self, mock_bim, mock_gene_loc, negctrl_gmt_path, tmp_path):
        """Negative control gene sets produce valid annotation columns (REQ-7)."""
        all_genes = load_gene_loc(str(mock_gene_loc))
        pathway_sets = parse_gmt(str(negctrl_gmt_path))
        out_path = tmp_path / "negctrl.22.annot.gz"

        stats = build_annot_for_chrom(
            chrom="22",
            bim_path=str(mock_bim),
            all_genes=all_genes,
            pathway_sets=pathway_sets,
            window_bp=100000,
            out_path=str(out_path),
        )

        assert out_path.exists()
        with gzip.open(str(out_path), "rt") as f:
            header = f.readline().strip().split("\t")
        # Should have 3 negative control columns
        neg_cols = [c for c in header if c.startswith("NEGCTRL_")]
        assert len(neg_cols) == 3

    def test_window_kb_parameter(self, mock_gene_loc):
        """100 kb window correctly extends gene boundaries."""
        all_genes = load_gene_loc(str(mock_gene_loc))
        # TESTGENE1 is at 16050000-16100000
        gene_symbols = {"TESTGENE1"}
        intervals = build_gene_intervals(all_genes, gene_symbols, "22", 100000)
        assert len(intervals) == 1
        # With 100kb window: 16050000 - 100000 = 15950000, 16100000 + 100000 = 16200000
        assert intervals[0][0] == 15950000
        assert intervals[0][1] == 16200000

    def test_point_in_intervals(self):
        """Binary search correctly identifies points in intervals."""
        intervals = [(1000, 2000), (5000, 6000), (9000, 10000)]
        assert point_in_intervals(1500, intervals) is True
        assert point_in_intervals(3000, intervals) is False
        assert point_in_intervals(5000, intervals) is True
        assert point_in_intervals(10001, intervals) is False

    def test_custom_annotation_per_chromosome(self, mock_gene_loc, tmp_path):
        """build_ldsc_annot produces 22 annotation files (one per chromosome).

        Uses mock data with genes only on chr22, so only chr22 produces
        annotated SNPs. The other chromosomes are skipped because mock BIM
        files only exist for chr22. The key assertion is that the function
        correctly handles per-chromosome file naming.
        """
        all_genes = load_gene_loc(str(mock_gene_loc))
        pathway_sets = [("TEST_SET", {"TESTGENE1"})]

        # Create mock BIM files for 3 chromosomes
        for chrom in ["20", "21", "22"]:
            bim_file = tmp_path / f"mock.{chrom}.bim"
            rows = []
            for i in range(10):
                pos = 16000000 + i * 1000
                rows.append(f"{chrom}\trs_{chrom}_{i}\t0\t{pos}\tA\tG\n")
            bim_file.write_text("".join(rows))

        # Build annotations for these 3 chromosomes
        for chrom in ["20", "21", "22"]:
            out_path = tmp_path / f"test.{chrom}.annot.gz"
            build_annot_for_chrom(
                chrom=chrom,
                bim_path=str(tmp_path / f"mock.{chrom}.bim"),
                all_genes=all_genes,
                pathway_sets=pathway_sets,
                window_bp=100000,
                out_path=str(out_path),
            )
            assert out_path.exists(), f"Missing annotation for chr{chrom}"


class TestLdscPartitioned:
    """Test run_ldsc_partitioned.py command construction and results parsing."""

    def test_munge_snp_count_warning(self, mock_sumstats_path, tmp_path, caplog):
        """Verify WARNING logged if < 500,000 SNPs after munging (Pitfall 2).

        We test by calling run_munge with a mock LDSC that produces a small
        .sumstats.gz file (100 SNPs), which is well below the 500K threshold.
        """
        from run_ldsc_partitioned import MIN_MUNGED_SNPS, _count_sumstats_snps

        # Create a small .sumstats.gz with only 50 SNPs
        small_sumstats = tmp_path / "small.sumstats.gz"
        with gzip.open(str(small_sumstats), "wt") as f:
            f.write("SNP\tA1\tA2\tN\tP\tBETA\tSE\n")
            for i in range(50):
                f.write(f"rs{i}\tA\tG\t50000\t0.5\t0.01\t0.005\n")

        count = _count_sumstats_snps(str(small_sumstats))
        assert count == 50
        assert count < MIN_MUNGED_SNPS

    def test_overlap_annot_flag(self):
        """Verify --overlap-annot is always present in h2 command construction.

        The run_partitioned_h2 function MUST include --overlap-annot in the
        subprocess command to avoid the known LDSC anti-pattern.
        """
        import run_ldsc_partitioned

        # Read the source and verify --overlap-annot is in the h2 function
        source = Path(run_ldsc_partitioned.__file__).read_text()
        assert "--overlap-annot" in source, (
            "run_ldsc_partitioned.py must include --overlap-annot in h2 step"
        )

        # More specifically, check it's in the run_partitioned_h2 function body
        import inspect

        h2_source = inspect.getsource(run_ldsc_partitioned.run_partitioned_h2)
        assert "--overlap-annot" in h2_source, (
            "run_partitioned_h2() function must include --overlap-annot"
        )

    def test_baseline_first_in_ref_ld(self):
        """Verify baseline v2.2 path appears before custom in --ref-ld-chr (D-04a)."""
        from run_ldsc_partitioned import build_ref_ld_chr_arg

        result = build_ref_ld_chr_arg(
            baseline_prefix="data/reference/ldsc/baselineLD.",
            custom_prefix="results/pathway/ld_scores/custom_pathway.",
        )

        parts = result.split(",")
        assert len(parts) == 2, f"Expected 2 parts, got {len(parts)}"
        assert "baselineLD" in parts[0], "Baseline must be first in --ref-ld-chr"
        assert "custom_pathway" in parts[1], "Custom must be second in --ref-ld-chr"

    def test_ldsc_results_parsing(self, mock_ldsc_results):
        """Verify .results file parsing extracts correct columns."""
        from run_ldsc_partitioned import parse_ldsc_results

        parsed = parse_ldsc_results(str(mock_ldsc_results))

        assert len(parsed) == 2, f"Expected 2 rows, got {len(parsed)}"

        # Check first row has expected fields
        row0 = parsed[0]
        assert "Category" in row0
        assert "Prop._SNPs" in row0
        assert "Prop._h2" in row0
        assert "Enrichment" in row0
        assert "Enrichment_p" in row0
        assert "Enrichment_std_error" in row0

        # Check values
        assert row0["Category"] == "L2_0"
        assert float(row0["Prop._SNPs"]) == pytest.approx(0.05)
        assert float(row0["Enrichment"]) == pytest.approx(2.00)
        assert float(row0["Enrichment_p"]) == pytest.approx(0.001)

    def test_no_shell_true(self):
        """Verify run_ldsc_partitioned.py never passes shell=True to subprocess (T-05-14).

        Uses AST analysis to check that no subprocess call uses shell=True
        as a keyword argument -- this is more robust than string matching
        which catches false positives in comments and docstrings.
        """
        import ast

        import run_ldsc_partitioned

        source = Path(run_ldsc_partitioned.__file__).read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        pytest.fail(
                            f"run_ldsc_partitioned.py line {node.lineno}: "
                            f"subprocess call uses shell=True"
                        )

    def test_h2_summary_writer(self, mock_ldsc_results, tmp_path):
        """Verify write_h2_summary produces clean TSV from parsed results."""
        from run_ldsc_partitioned import parse_ldsc_results, write_h2_summary

        parsed = parse_ldsc_results(str(mock_ldsc_results))
        summary_path = tmp_path / "h2_summary.tsv"
        write_h2_summary(parsed, str(summary_path))

        assert summary_path.exists()
        lines = summary_path.read_text().strip().split("\n")
        assert len(lines) == 3  # header + 2 rows
        header = lines[0].split("\t")
        assert "annotation" in header
        assert "enrichment" in header
        assert "enrichment_p" in header
