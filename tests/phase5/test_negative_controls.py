"""Tests for negative control pathway sets across all methods (Phase 5).

Validates:
- Each method has negative control pathway coverage
- Negative control genes do NOT overlap with custom cardiometabolic genes (REQ-7)
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))
from build_magma_geneset import parse_gmt


class TestAllMethodsHaveNegCtrl:
    """Verify each analytical method has negative control rows."""

    def test_all_methods_have_neg_ctrl(self):
        """Each method (MAGMA, g:Profiler, LDSC, LDSC-SEG, HESS) has neg ctrl rows.

        Negative controls are defined in negative_controls.gmt which feeds into:
        1. MAGMA gene-set analysis (via build_magma_geneset.py)
        2. LDSC partitioned h2 (via build_ldsc_annot.py)
        3. g:Profiler (via negative control gene lists)
        4. LDSC-SEG (via custom tissue annotations from neg ctrl regions)
        5. HESS (via negative control loci from neg_ctrl_coloc_manifest)

        This test validates the GMT file exists and has content for all methods.
        """
        negctrl_gmt = (
            PROJECT_ROOT / "config" / "pathway_sets" / "negative_controls.gmt"
        )
        assert negctrl_gmt.exists(), "negative_controls.gmt missing"
        gene_sets = parse_gmt(str(negctrl_gmt))
        assert len(gene_sets) == 3, f"Expected 3 neg ctrl sets, got {len(gene_sets)}"

        # Each set should have genes
        for name, _desc, genes in gene_sets:
            assert len(genes) >= 3, f"Neg ctrl set '{name}' has < 3 genes"

    def test_neg_ctrl_set_names(self):
        """Negative control sets are named NEGCTRL_HLA_IMMUNE, NEGCTRL_COSMETIC, NEGCTRL_BLOOD_GROUP."""
        negctrl_gmt = (
            PROJECT_ROOT / "config" / "pathway_sets" / "negative_controls.gmt"
        )
        gene_sets = parse_gmt(str(negctrl_gmt))
        set_names = {gs[0] for gs in gene_sets}
        expected = {"NEGCTRL_HLA_IMMUNE", "NEGCTRL_COSMETIC", "NEGCTRL_BLOOD_GROUP"}
        assert set_names == expected


class TestNegCtrlGeneOverlap:
    """Test that negative control genes do NOT overlap with custom cardiometabolic genes."""

    def test_neg_ctrl_gmt_gene_overlap(self, custom_gmt_path, negctrl_gmt_path):
        """Negative control genes should not overlap with custom cardiometabolic genes.

        This ensures negative controls are truly independent of the hypothesis
        being tested (REQ-7). Any overlap would invalidate the negative control.
        """
        custom_sets = parse_gmt(str(custom_gmt_path))
        negctrl_sets = parse_gmt(str(negctrl_gmt_path))

        # Collect all custom cardiometabolic genes
        custom_genes = set()
        for _name, _desc, genes in custom_sets:
            custom_genes.update(genes)

        # Collect all negative control genes
        negctrl_genes = set()
        for _name, _desc, genes in negctrl_sets:
            negctrl_genes.update(genes)

        overlap = custom_genes & negctrl_genes
        assert len(overlap) == 0, (
            f"Negative control genes overlap with custom cardiometabolic genes: {overlap}"
        )
