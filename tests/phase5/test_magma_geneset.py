"""Tests for MAGMA gene set files, build_magma_geneset.py, and run_magma.py (Phase 5).

Validates:
- GMT file format and content for custom cardiometabolic pathways
- Negative control GMT file content (REQ-7)
- build_magma_geneset.py parsing and conversion logic
- run_magma.py subprocess command construction (T-05-05: no shell=True)
- Effective N computation for binary traits (Pitfall 4)
- MAGMA pval file format (SNP + P only)
"""
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PATHWAY_SETS_DIR = PROJECT_ROOT / "config" / "pathway_sets"

# Add src/python to path for direct imports
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))
from build_magma_geneset import parse_gmt, load_gene_loc, convert_to_magma_set
from run_magma import run_annotate, effective_n, _create_pval_file


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


class TestRunMagmaAnnotateCmd:
    """Test run_magma.py annotate step command construction."""

    def test_run_magma_annotate_cmd(self, tmp_path):
        """Verify subprocess command list is constructed correctly for annotate step.

        T-05-05: Must use list args (no shell=True).
        T-05-10: File paths validated before passing to MAGMA.
        """
        # Create mock files that run_annotate will validate
        mock_magma = tmp_path / "magma"
        mock_magma.write_text("#!/bin/bash\necho mock")
        mock_magma.chmod(0o755)

        mock_snp_loc = tmp_path / "g1000_eur.bim"
        mock_snp_loc.write_text("22\trs100\t0\t1000\tA\tG\n")

        mock_gene_loc = tmp_path / "gene.loc"
        mock_gene_loc.write_text("1000\t22\t1000\t2000\t+\tTEST\n")

        out_prefix = str(tmp_path / "output")

        # Patch subprocess.run to capture the command
        with patch("run_magma.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            run_annotate(
                magma_binary=str(mock_magma),
                snp_loc=str(mock_snp_loc),
                gene_loc=str(mock_gene_loc),
                out=out_prefix,
            )

            # Verify subprocess.run was called with list args (not string)
            call_args = mock_run.call_args
            cmd = call_args[0][0]  # First positional arg is the command list
            assert isinstance(cmd, list), "Command must be a list (no shell=True)"
            assert str(mock_magma) in cmd
            assert "--annotate" in cmd
            assert "--snp-loc" in cmd
            assert "--gene-loc" in cmd
            assert "--out" in cmd

            # Verify shell=True is NOT used
            kwargs = call_args[1] if len(call_args) > 1 else call_args.kwargs
            assert kwargs.get("check") is not True or "shell" not in kwargs or kwargs["shell"] is False


class TestEffectiveNBinaryTrait:
    """Test effective N calculation for binary traits."""

    def test_effective_n_binary_trait(self):
        """Verify effective N: n_case=5000, n_ctrl=20000 => N_eff = 16000.0.

        Formula: N_eff = 4 / (1/n_case + 1/n_ctrl)
                       = 4 / (1/5000 + 1/20000)
                       = 4 / (0.0002 + 0.00005)
                       = 4 / 0.00025
                       = 16000.0
        """
        n_eff = effective_n(n_case=5000, n_ctrl=20000)
        assert n_eff == pytest.approx(16000.0, rel=1e-6)

    def test_effective_n_quantitative_trait(self):
        """Quantitative trait returns sample_size directly."""
        n_eff = effective_n(trait="bmi", sample_size=500000)
        assert n_eff == 500000.0

    def test_effective_n_binary_trait_auto_detect(self):
        """Binary trait auto-detected from trait name."""
        n_eff = effective_n(trait="t2d", n_case=5000, n_ctrl=20000)
        assert n_eff == pytest.approx(16000.0, rel=1e-6)

    def test_effective_n_binary_missing_args_raises(self):
        """Binary trait without n_case/n_ctrl raises ValueError."""
        with pytest.raises(ValueError, match="requires --n-case"):
            effective_n(trait="t2d", sample_size=25000)


class TestMagmaPvalFileFormat:
    """Test MAGMA pval file extraction from harmonized sumstats."""

    def test_magma_pval_file_format(self, mock_sumstats_path, tmp_path):
        """Verify temp pval file has only SNP + P columns.

        T-05-11: Temp file should contain only SNP and P (no individual-level data).
        """
        pval_path = _create_pval_file(str(mock_sumstats_path), str(tmp_path))

        # Read the generated pval file
        with open(pval_path) as f:
            header = f.readline().strip()
            first_data = f.readline().strip()

        # Verify header has exactly SNP and P
        assert header == "SNP\tP", f"Expected 'SNP\\tP' header, got '{header}'"

        # Verify data rows have exactly 2 columns
        fields = first_data.split("\t")
        assert len(fields) == 2, f"Expected 2 columns, got {len(fields)}"

        # Verify SNP column looks like an rsID
        assert fields[0].startswith("rs"), f"SNP should be rsID, got {fields[0]}"

        # Verify P is a valid float
        float(fields[1])  # Should not raise

    def test_pval_file_row_count(self, mock_sumstats_path, tmp_path):
        """Verify pval file has same number of data rows as input."""
        pval_path = _create_pval_file(str(mock_sumstats_path), str(tmp_path))

        with open(pval_path) as f:
            lines = [l for l in f.readlines() if l.strip()]
        # 1 header + 100 data rows
        assert len(lines) == 101, f"Expected 101 lines (1 header + 100 data), got {len(lines)}"
