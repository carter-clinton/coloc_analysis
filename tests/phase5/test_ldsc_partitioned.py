"""Tests for LDSC partitioned heritability utilities (Phase 5).

Validates:
- munge_sumstats_ldsc.py column output format
- Effective N calculation for binary traits
- build_ldsc_annot.py annotation format and window logic
- Negative control annotation validity (REQ-7)
"""
import gzip
import sys
from pathlib import Path

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
