"""Tests for MAGMA gene set files and build_magma_geneset.py (Phase 5).

Validates:
- GMT file format and content for custom cardiometabolic pathways
- Negative control GMT file content (REQ-7)
- build_magma_geneset.py parsing and conversion logic
"""
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PATHWAY_SETS_DIR = PROJECT_ROOT / "config" / "pathway_sets"

# Add src/python to path for direct imports
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))
from build_magma_geneset import parse_gmt, load_gene_loc, convert_to_magma_set


class TestCustomGMT:
    """Validate custom_cardiometabolic.gmt content."""

    def test_custom_gmt_has_8_sets(self, custom_gmt_path):
        """custom_cardiometabolic.gmt has exactly 8 lines (8 pathway sets)."""
        lines = [l for l in custom_gmt_path.read_text().strip().split("\n") if l.strip()]
        assert len(lines) == 8, f"Expected 8 sets, got {len(lines)}"

    def test_custom_gmt_gene_counts(self, custom_gmt_path):
        """Each pathway has >= 8 genes (no empty sets, per Pitfall 7)."""
        gene_sets = parse_gmt(str(custom_gmt_path))
        for set_name, _desc, genes in gene_sets:
            assert len(genes) >= 8, (
                f"Set '{set_name}' has only {len(genes)} genes (minimum 8)"
            )

    def test_insulin_signaling_genes(self, custom_gmt_path):
        """CUSTOM_INSULIN_SIGNALING contains key insulin pathway genes."""
        gene_sets = parse_gmt(str(custom_gmt_path))
        insulin_set = next(
            (gs for gs in gene_sets if gs[0] == "CUSTOM_INSULIN_SIGNALING"), None
        )
        assert insulin_set is not None, "CUSTOM_INSULIN_SIGNALING not found"
        expected_genes = {"INSR", "IRS1", "IRS2", "PIK3CA", "AKT1", "AKT2"}
        actual_genes = set(insulin_set[2])
        assert expected_genes.issubset(actual_genes), (
            f"Missing genes: {expected_genes - actual_genes}"
        )

    def test_appetite_regulation_genes(self, custom_gmt_path):
        """CUSTOM_APPETITE_REGULATION contains key appetite genes."""
        gene_sets = parse_gmt(str(custom_gmt_path))
        appetite_set = next(
            (gs for gs in gene_sets if gs[0] == "CUSTOM_APPETITE_REGULATION"), None
        )
        assert appetite_set is not None
        expected_genes = {"MC4R", "FTO", "BDNF", "LEP"}
        actual_genes = set(appetite_set[2])
        assert expected_genes.issubset(actual_genes)

    def test_gmt_format_valid(self, custom_gmt_path):
        """Each GMT line has >= 3 tab-separated fields (name, description, genes)."""
        for i, line in enumerate(custom_gmt_path.read_text().strip().split("\n"), 1):
            if not line.strip():
                continue
            fields = line.split("\t")
            assert len(fields) >= 3, (
                f"Line {i} has {len(fields)} fields, need >= 3"
            )


class TestNegCtrlGMT:
    """Validate negative_controls.gmt content (REQ-7)."""

    def test_neg_ctrl_sets_included(self, negctrl_gmt_path):
        """negative_controls.gmt has exactly 3 lines with HLA-A, OCA2, ABO."""
        lines = [l for l in negctrl_gmt_path.read_text().strip().split("\n") if l.strip()]
        assert len(lines) == 3, f"Expected 3 neg ctrl sets, got {len(lines)}"
        full_text = negctrl_gmt_path.read_text()
        assert "HLA-A" in full_text
        assert "OCA2" in full_text
        assert "ABO" in full_text

    def test_neg_ctrl_set_names(self, negctrl_gmt_path):
        """Negative control set names follow NEGCTRL_ prefix convention."""
        gene_sets = parse_gmt(str(negctrl_gmt_path))
        for set_name, _desc, _genes in gene_sets:
            assert set_name.startswith("NEGCTRL_"), (
                f"Negative control set '{set_name}' missing NEGCTRL_ prefix"
            )


class TestBuildMagmaGeneset:
    """Test build_magma_geneset.py parsing and conversion."""

    def test_build_magma_geneset_runs(self, mock_gene_loc, custom_gmt_path, tmp_path):
        """build_magma_geneset.py can parse GMT and gene.loc to produce .set output."""
        out_path = tmp_path / "test_output.set"
        gene_sets = parse_gmt(str(custom_gmt_path))
        symbol_to_entrez = load_gene_loc(str(mock_gene_loc))
        summary = convert_to_magma_set(gene_sets, symbol_to_entrez, str(out_path))

        assert out_path.exists(), ".set file not created"
        assert len(summary) == 8, f"Expected 8 sets in summary, got {len(summary)}"

        # At least some genes should be mapped (mock has INSR, IRS1, etc.)
        total_mapped = sum(s["n_mapped"] for s in summary.values())
        assert total_mapped > 0, "No genes mapped from mock gene.loc"

    def test_gmt_parse_returns_correct_structure(self, custom_gmt_path):
        """parse_gmt returns list of (name, description, genes) tuples."""
        gene_sets = parse_gmt(str(custom_gmt_path))
        assert len(gene_sets) == 8
        for name, desc, genes in gene_sets:
            assert isinstance(name, str)
            assert isinstance(desc, str)
            assert isinstance(genes, list)
            assert all(isinstance(g, str) for g in genes)
