"""Tests for run_qtl_coloc.R, qtl_coloc.smk, and Snakefile wiring (02-02 Task 2)."""
import os
import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestRunQtlColocR:
    """Verify run_qtl_coloc.R exists and has required interface."""

    @pytest.fixture(scope="class")
    def script_path(self):
        return PROJECT_ROOT / "src" / "snakemake" / "scripts" / "run_qtl_coloc.R"

    @pytest.fixture(scope="class")
    def script_content(self, script_path):
        assert script_path.exists(), f"run_qtl_coloc.R not found at {script_path}"
        return script_path.read_text()

    def test_run_qtl_coloc_r_exists(self, script_path):
        assert script_path.exists()

    def test_contains_coloc_susie_call(self, script_content):
        """Must call coloc::coloc.susie(gwas_fit, qtl_fit)."""
        assert "coloc::coloc.susie(gwas_fit, qtl_fit)" in script_content

    def test_contains_runsusie_call(self, script_content):
        """Must call coloc::runsusie(qtl_data on the QTL side."""
        assert "coloc::runsusie(qtl_data" in script_content

    def test_has_gwas_fit_arg(self, script_content):
        assert "--gwas-fit" in script_content

    def test_has_qtl_sumstats_arg(self, script_content):
        assert "--qtl-sumstats" in script_content

    def test_has_ld_matrix_arg(self, script_content):
        assert "--ld-matrix" in script_content

    def test_has_sdy_arg(self, script_content):
        assert "--sdy" in script_content

    def test_has_sample_size_arg(self, script_content):
        assert "--sample-size" in script_content

    def test_has_json_output(self, script_content):
        """Must write JSON output via jsonlite."""
        assert "jsonlite" in script_content
        assert "write_json" in script_content

    def test_has_check_dataset(self, script_content):
        """T-02-07 mitigation: validates QTL dataset before SuSiE fitting."""
        assert "check_dataset" in script_content

    def test_has_min_snp_guard(self, script_content):
        """Must skip coloc if too few overlapping SNPs."""
        assert "too_few_snps" in script_content

    def test_has_edge_case_handling(self, script_content):
        """Must handle QTL SuSiE convergence failure."""
        assert "qtl_susie_failed" in script_content

    def test_has_no_qtl_cs_handling(self, script_content):
        """Must handle case where QTL side has no credible sets."""
        assert "no_qtl_cs" in script_content


class TestQtlColocSmk:
    """Verify qtl_coloc.smk has required rules and functions."""

    @pytest.fixture(scope="class")
    def smk_path(self):
        return PROJECT_ROOT / "src" / "snakemake" / "rules" / "qtl_coloc.smk"

    @pytest.fixture(scope="class")
    def smk_content(self, smk_path):
        assert smk_path.exists(), f"qtl_coloc.smk not found at {smk_path}"
        return smk_path.read_text()

    def test_qtl_coloc_smk_exists(self, smk_path):
        assert smk_path.exists()

    def test_has_run_qtl_coloc_rule(self, smk_content):
        assert "rule run_qtl_coloc:" in smk_content

    def test_has_build_manifest_rule(self, smk_content):
        assert "rule build_qtl_coloc_manifest:" in smk_content

    def test_has_manifest_row_function(self, smk_content):
        assert "_qtl_coloc_manifest_row" in smk_content

    def test_has_manifest_field_function(self, smk_content):
        assert "_qtl_manifest_field" in smk_content

    def test_has_wildcard_constraints(self, smk_content):
        assert "wildcard_constraints:" in smk_content
        assert "qtl_coloc_id" in smk_content

    def test_manifest_id_regex(self, smk_content):
        """T-02-05: wildcard_constraints must use safe regex."""
        # Find the regex pattern for qtl_coloc_id
        match = re.search(r'qtl_coloc_id\s*=\s*r"([^"]+)"', smk_content)
        assert match is not None, "qtl_coloc_id regex not found"
        pattern = match.group(1)
        # Must be restrictive (alphanumeric + safe chars)
        assert re.match(r"^\[A-Za-z0-9", pattern), f"Pattern not restrictive enough: {pattern}"

    def test_has_aggregate_rule(self, smk_content):
        assert "rule aggregate_qtl_coloc:" in smk_content


class TestSnakefileIncludes:
    """Verify Snakefile includes the new QTL rule files."""

    @pytest.fixture(scope="class")
    def snakefile_content(self):
        snakefile = PROJECT_ROOT / "Snakefile"
        assert snakefile.exists()
        return snakefile.read_text()

    def test_includes_qtl_coloc_smk(self, snakefile_content):
        assert 'include: "src/snakemake/rules/qtl_coloc.smk"' in snakefile_content

    def test_includes_qtl_download_smk(self, snakefile_content):
        assert 'include: "src/snakemake/rules/qtl_download.smk"' in snakefile_content

    def test_qtl_download_before_qtl_coloc(self, snakefile_content):
        """qtl_download.smk must be included before qtl_coloc.smk."""
        idx_download = snakefile_content.index("qtl_download.smk")
        idx_coloc = snakefile_content.index("qtl_coloc.smk")
        assert idx_download < idx_coloc, "qtl_download.smk must be included before qtl_coloc.smk"
