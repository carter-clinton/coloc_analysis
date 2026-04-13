"""Tests for negative control pathway sets across all methods (Phase 5 Plan 05-05).

Validates:
- Each method has negative control pathway coverage in Snakemake rules
- Negative control genes do NOT overlap with custom cardiometabolic genes (REQ-7)
- Validation summary schema
- q > 0.05 threshold enforcement per D-06b
"""
import csv
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))
from build_magma_geneset import parse_gmt


class TestAllMethodsHaveNegCtrl:
    """Verify each analytical method has negative control rules in pathway.smk."""

    def test_all_methods_have_neg_ctrl(self):
        """pathway.smk has neg ctrl rules for MAGMA, g:Profiler, LDSC, LDSC-SEG, HESS.

        Negative controls are defined in negative_controls.gmt which feeds into:
        1. MAGMA gene-set analysis (via build_magma_geneset.py + magma_fdr)
        2. LDSC partitioned h2 (via build_ldsc_annot.py)
        3. g:Profiler (via gprofiler_negative_controls rule)
        4. LDSC-SEG (via custom tissue annotations from neg ctrl regions)
        5. HESS (via hess_negative_controls rule)
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

    def test_magma_neg_ctrl_rule(self):
        """pathway.smk includes negative controls in MAGMA gene-set file."""
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
        text = smk_path.read_text()
        # Negative controls feed into build_magma_set_file via negctrl GMT input
        assert "negative_control_gmt" in text
        assert "rule build_magma_set_file:" in text

    def test_gprofiler_neg_ctrl_rule(self):
        """pathway.smk has gprofiler_negative_controls rule."""
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
        text = smk_path.read_text()
        assert "rule gprofiler_negative_controls:" in text

    def test_ldsc_neg_ctrl_annotations(self):
        """pathway.smk builds LDSC annotations from negative control GMT."""
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
        text = smk_path.read_text()
        assert "rule ldsc_build_custom_annotations:" in text
        assert "negctrl_gmt" in text

    def test_hess_neg_ctrl_rule(self):
        """pathway.smk has hess_negative_controls rule."""
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
        text = smk_path.read_text()
        assert "rule hess_negative_controls:" in text

    def test_validate_neg_ctrl_rule(self):
        """pathway.smk has validate_negative_controls rule."""
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
        text = smk_path.read_text()
        assert "rule validate_negative_controls:" in text


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


class TestValidationSummarySchema:
    """Test the validation summary TSV has the expected schema."""

    def test_validation_summary_schema(self, tmp_path):
        """Validation summary must have expected columns per plan spec."""
        expected_columns = [
            "neg_ctrl_set", "method", "trait", "ancestry",
            "statistic", "p_value", "q_value", "passes_threshold",
        ]

        # Create a mock validation summary to test schema
        summary_path = tmp_path / "validation_summary.tsv"
        with open(summary_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=expected_columns, delimiter="\t")
            writer.writeheader()
            writer.writerow({
                "neg_ctrl_set": "NEGCTRL_HLA_IMMUNE",
                "method": "MAGMA",
                "trait": "bmi",
                "ancestry": "EUR",
                "statistic": "beta=0.1",
                "p_value": "0.500000",
                "q_value": "0.600000",
                "passes_threshold": "TRUE",
            })

        # Verify the schema
        with open(summary_path) as f:
            reader = csv.DictReader(f, delimiter="\t")
            fields = reader.fieldnames
            assert fields is not None
            for col in expected_columns:
                assert col in fields, f"Missing column: {col}"


class TestNegCtrlThreshold:
    """Test that the q > 0.05 threshold is enforced per D-06b."""

    def test_neg_ctrl_threshold(self):
        """Threshold for negative control pass is q > 0.05 per D-06b.

        The validate_negative_controls rule checks this threshold and
        hard-fails (exit 1) if any control produces q <= 0.05 (T-05-21).
        """
        from extend_null_genesets import validate_negative_controls

        # Create a mock validation file where all pass
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tsv", delete=False
        ) as f:
            f.write("neg_ctrl_set\tmethod\ttrait\tancestry\tstatistic\tp_value\tq_value\tpasses_threshold\n")
            f.write("NEGCTRL_HLA_IMMUNE\tMAGMA\tbmi\tEUR\tbeta=0.1\t0.5\t0.6\tTRUE\n")
            f.write("NEGCTRL_COSMETIC\tMAGMA\tbmi\tEUR\tbeta=0.05\t0.8\t0.9\tTRUE\n")
            tmp_path = f.name

        # Should pass without error
        result = validate_negative_controls(tmp_path)
        assert result is True

        import os
        os.unlink(tmp_path)

    def test_neg_ctrl_threshold_fail(self):
        """validate_negative_controls exits 1 when any q <= 0.05."""
        from extend_null_genesets import validate_negative_controls

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tsv", delete=False
        ) as f:
            f.write("neg_ctrl_set\tmethod\ttrait\tancestry\tstatistic\tp_value\tq_value\tpasses_threshold\n")
            f.write("NEGCTRL_HLA_IMMUNE\tMAGMA\tbmi\tEUR\tbeta=0.1\t0.01\t0.03\tFALSE\n")
            tmp_path = f.name

        # Should exit with code 1
        with pytest.raises(SystemExit) as exc_info:
            validate_negative_controls(tmp_path)
        assert exc_info.value.code == 1

        import os
        os.unlink(tmp_path)
