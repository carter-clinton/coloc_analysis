"""Tests for LDSC-SEG tissue-specific enrichment (Phase 5).

Validates:
- Pipeline config has LDSC-SEG paths configured
- .ldcts file format validation and path fixing (Pitfall 8 / T-05-13)
- .cell_type_results.txt parsing extracts correct columns
- Shared tissue identification across trait pairs (D-05b)
- --h2-cts flag usage (not --h2)
- No shell=True in subprocess calls (T-05-14)
"""
import ast
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))


class TestTissueAnnotationPaths:
    """Verify pipeline.yaml LDSC-SEG paths are configured."""

    def test_ldsc_seg_gene_expr_path(self, pipeline_config):
        """pipeline.yaml has ldsc_seg_gene_expr path configured."""
        pathway = pipeline_config.get("pathway", {})
        assert "ldsc_seg_gene_expr" in pathway
        assert "Multi_tissue_gene_expr" in pathway["ldsc_seg_gene_expr"]

    def test_ldsc_seg_chromatin_path(self, pipeline_config):
        """pipeline.yaml has ldsc_seg_chromatin path configured."""
        pathway = pipeline_config.get("pathway", {})
        assert "ldsc_seg_chromatin" in pathway
        assert "Multi_tissue_chromatin" in pathway["ldsc_seg_chromatin"]

    def test_ldsc_seg_rules_exist(self):
        """pathway.smk contains all LDSC-SEG rules."""
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
        text = smk_path.read_text()
        assert "rule ldsc_seg_gene_expr:" in text
        assert "rule ldsc_seg_chromatin:" in text
        assert "rule ldsc_seg_shared_tissues:" in text
        assert "rule fix_ldcts_paths:" in text


class TestLdctsFormat:
    """Test .ldcts file format validation and path fixing."""

    def test_ldcts_format_validation(self, tmp_path):
        """validate_ldcts_file accepts well-formed .ldcts files."""
        from run_ldsc_seg import validate_ldcts_file

        ldcts = tmp_path / "test.ldcts"
        ldcts.write_text(
            "Pancreas\tdata/reference/Pancreas.,data/reference/Pancreas_annot.\n"
            "Liver\tdata/reference/Liver.,data/reference/Liver_annot.\n"
        )

        entries = validate_ldcts_file(str(ldcts))
        assert len(entries) == 2
        assert entries[0][0] == "Pancreas"
        assert entries[1][0] == "Liver"

    def test_ldcts_format_rejects_bad(self, tmp_path):
        """validate_ldcts_file rejects files with missing tab separator."""
        from run_ldsc_seg import validate_ldcts_file

        ldcts = tmp_path / "bad.ldcts"
        ldcts.write_text("Pancreas no_tab_here\n")

        with pytest.raises(ValueError, match="Invalid .ldcts format"):
            validate_ldcts_file(str(ldcts))

    def test_ldcts_fix_paths(self, tmp_path):
        """Path rewriting produces valid .ldcts with correct local paths."""
        from run_ldsc_seg import fix_ldcts_paths

        # Create an input .ldcts with Broad-style absolute paths
        input_ldcts = tmp_path / "original.ldcts"
        input_ldcts.write_text(
            "Pancreas\t/broad/data/Pancreas.,/broad/annot/Pancreas.\n"
            "Liver\t/broad/data/Liver.,/broad/annot/Liver.\n"
        )

        output_ldcts = tmp_path / "fixed.ldcts"
        annot_dir = "/local/ldsc_seg"

        n_fixed = fix_ldcts_paths(
            ldcts_input=str(input_ldcts),
            ldcts_output=str(output_ldcts),
            annot_dir=annot_dir,
        )

        assert n_fixed == 2
        assert output_ldcts.exists()

        content = output_ldcts.read_text().strip().split("\n")
        assert len(content) == 2

        # Verify paths were rewritten to local directory
        for line in content:
            parts = line.split("\t")
            assert len(parts) == 2
            assert annot_dir in parts[1], f"Expected local path in: {parts[1]}"

    def test_ldcts_fix_preserves_tissue_names(self, tmp_path):
        """Path rewriting preserves original tissue names."""
        from run_ldsc_seg import fix_ldcts_paths

        input_ldcts = tmp_path / "input.ldcts"
        input_ldcts.write_text(
            "Brain_Cerebellum\t/old/path/Brain_Cerebellum.\n"
            "Heart_Left_Ventricle\t/old/path/Heart_Left_Ventricle.\n"
        )

        output_ldcts = tmp_path / "output.ldcts"
        fix_ldcts_paths(str(input_ldcts), str(output_ldcts), annot_dir="/new")

        content = output_ldcts.read_text().strip().split("\n")
        assert "Brain_Cerebellum" in content[0]
        assert "Heart_Left_Ventricle" in content[1]


class TestSegResultsParsing:
    """Test .cell_type_results.txt parsing."""

    def test_seg_results_parsing(self, tmp_path):
        """Verify .cell_type_results.txt parsing extracts correct columns."""
        from run_ldsc_seg import parse_seg_results

        results_file = tmp_path / "test.cell_type_results.txt"
        results_file.write_text(
            "Name\tCoefficient\tCoefficient_std_error\tCoefficient_z-score\tCoefficient_P_value\n"
            "Pancreas\t1.5e-08\t5.0e-09\t3.0\t0.001\n"
            "Liver\t8.0e-09\t4.0e-09\t2.0\t0.05\n"
            "Brain\t-1.0e-09\t3.0e-09\t-0.33\t0.74\n"
        )

        parsed = parse_seg_results(str(results_file))
        assert len(parsed) == 3

        # Check first row
        row0 = parsed[0]
        assert row0["Name"] == "Pancreas"
        assert "Coefficient" in row0
        assert "Coefficient_P_value" in row0
        assert float(row0["Coefficient_P_value"]) == pytest.approx(0.001)

    def test_seg_results_empty_file(self, tmp_path):
        """parse_seg_results returns empty list for missing file."""
        from run_ldsc_seg import parse_seg_results

        result = parse_seg_results(str(tmp_path / "nonexistent.txt"))
        assert result == []

    def test_seg_summary_writer(self, tmp_path):
        """write_seg_summary produces clean TSV from parsed results."""
        from run_ldsc_seg import write_seg_summary

        results = [
            {"Name": "Pancreas", "Coefficient": "1.5e-08",
             "Coefficient_std_error": "5e-09", "Coefficient_z-score": "3.0",
             "Coefficient_P_value": "0.001"},
            {"Name": "Liver", "Coefficient": "8e-09",
             "Coefficient_std_error": "4e-09", "Coefficient_z-score": "2.0",
             "Coefficient_P_value": "0.05"},
        ]

        summary_path = tmp_path / "seg_summary.tsv"
        write_seg_summary(results, str(summary_path))

        assert summary_path.exists()
        lines = summary_path.read_text().strip().split("\n")
        assert len(lines) == 3  # header + 2 rows
        header = lines[0].split("\t")
        assert "tissue" in header
        assert "coefficient_p" in header


class TestSharedTissues:
    """Test shared tissue identification across trait pairs (D-05b)."""

    def test_shared_tissue_identification(self):
        """With mock data: pancreas P < Bonf threshold for both bmi and t2d."""
        from run_ldsc_seg import identify_shared_tissues

        # Mock SEG results: 3 tissues, pancreas significant in both
        seg_results = {
            "bmi": [
                {"Name": "Pancreas", "Coefficient_P_value": "0.0001"},
                {"Name": "Liver", "Coefficient_P_value": "0.5"},
                {"Name": "Brain", "Coefficient_P_value": "0.8"},
            ],
            "t2d": [
                {"Name": "Pancreas", "Coefficient_P_value": "0.0005"},
                {"Name": "Liver", "Coefficient_P_value": "0.3"},
                {"Name": "Brain", "Coefficient_P_value": "0.6"},
            ],
        }

        trait_pairs = [("bmi", "t2d")]

        shared = identify_shared_tissues(seg_results, trait_pairs)

        # With 3 tissues, Bonferroni threshold = 0.05/3 = 0.0167
        # Pancreas: p1=0.0001, p2=0.0005 -> both < 0.0167 -> shared
        assert len(shared) == 1
        assert shared[0]["shared_tissue"] == "Pancreas"
        assert shared[0]["trait1"] == "bmi"
        assert shared[0]["trait2"] == "t2d"
        assert float(shared[0]["p_trait1"]) < 0.05
        assert float(shared[0]["p_trait2"]) < 0.05

    def test_shared_tissue_no_overlap(self):
        """No shared tissues when no tissue passes Bonferroni in both traits."""
        from run_ldsc_seg import identify_shared_tissues

        seg_results = {
            "bmi": [
                {"Name": "Pancreas", "Coefficient_P_value": "0.001"},
                {"Name": "Liver", "Coefficient_P_value": "0.5"},
            ],
            "hypertension": [
                {"Name": "Pancreas", "Coefficient_P_value": "0.5"},
                {"Name": "Liver", "Coefficient_P_value": "0.001"},
            ],
        }

        shared = identify_shared_tissues(seg_results, [("bmi", "hypertension")])
        assert len(shared) == 0

    def test_shared_tissue_missing_trait(self):
        """Gracefully handles missing trait data."""
        from run_ldsc_seg import identify_shared_tissues

        seg_results = {
            "bmi": [{"Name": "Pancreas", "Coefficient_P_value": "0.001"}],
        }

        shared = identify_shared_tissues(seg_results, [("bmi", "t2d")])
        assert len(shared) == 0


class TestH2CtsFlag:
    """Test that run_ldsc_seg.py uses --h2-cts (not --h2)."""

    def test_h2_cts_flag(self):
        """Verify run_ldsc_seg.py uses --h2-cts in the command construction."""
        import run_ldsc_seg

        import inspect

        source = inspect.getsource(run_ldsc_seg.run_tissue_enrichment)
        assert "--h2-cts" in source, (
            "run_tissue_enrichment must use --h2-cts, not --h2"
        )

    def test_no_plain_h2_flag(self):
        """Verify run_tissue_enrichment does NOT use plain --h2 flag."""
        import run_ldsc_seg

        import inspect

        source = inspect.getsource(run_ldsc_seg.run_tissue_enrichment)
        # Should have --h2-cts but NOT a standalone "--h2" (without -cts)
        lines = source.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            # Check for standalone --h2 that is NOT --h2-cts
            if '"--h2"' in stripped and '"--h2-cts"' not in stripped:
                pytest.fail(
                    f"run_tissue_enrichment uses '--h2' instead of '--h2-cts': {stripped}"
                )

    def test_no_shell_true(self):
        """Verify run_ldsc_seg.py never passes shell=True to subprocess (T-05-14)."""
        import run_ldsc_seg

        source = Path(run_ldsc_seg.__file__).read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        pytest.fail(
                            f"run_ldsc_seg.py line {node.lineno}: "
                            f"subprocess call uses shell=True"
                        )
