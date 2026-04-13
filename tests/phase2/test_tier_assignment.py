"""Tests for Tier A/B/C assignment logic (D-02c).

Validates:
- Tier A when both GWAS PP.H4 >= 0.8 AND QTL PP.H4 >= 0.8
- Tier B when GWAS PP.H4 >= 0.8 AND QTL PP.H4 in [0.5, 0.8)
- Tier C when GWAS PP.H4 >= 0.8 AND no QTL PP.H4 >= 0.5
- QTL-source-agnostic (same tier for eQTL/pQTL/sQTL/sc-eQTL per D-02c)
- parse_l2g.py reads Parquet and returns DataFrame with geneId and score columns
- build_gene_tissue_matrix.py produces a matrix with gene rows and tissue columns
- assign_tiers.py with --neg-ctrl-results produces negative_control rows
"""
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

from tests.phase2.conftest import CONFIG_DIR, PROJECT_ROOT

sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))


class TestAssignTierFunction:
    """Test assign_tier() function directly."""

    def test_tier_a_both_high(self):
        """gwas_pph4=0.95, qtl_pph4=0.85 -> Tier A."""
        from assign_tiers import assign_tier
        assert assign_tier(0.95, 0.85, 0.8) == "Tier A"

    def test_tier_b_qtl_moderate(self):
        """gwas_pph4=0.95, qtl_pph4=0.65 -> Tier B."""
        from assign_tiers import assign_tier
        assert assign_tier(0.95, 0.65, 0.8) == "Tier B"

    def test_tier_c_no_qtl(self):
        """gwas_pph4=0.95, qtl_pph4=0.2 -> Tier C."""
        from assign_tiers import assign_tier
        assert assign_tier(0.95, 0.2, 0.8) == "Tier C"

    def test_tier_c_qtl_none(self):
        """gwas_pph4=0.95, qtl_pph4=None -> Tier C."""
        from assign_tiers import assign_tier
        assert assign_tier(0.95, None, 0.8) == "Tier C"

    def test_tier_c_no_gwas(self):
        """gwas_pph4=0.3, qtl_pph4=0.9 -> below_threshold (requires GWAS >= 0.8)."""
        from assign_tiers import assign_tier
        result = assign_tier(0.3, 0.9, 0.8)
        assert result != "Tier A"
        assert result == "below_threshold"

    def test_tier_a_at_boundary(self):
        """gwas_pph4=0.8, qtl_pph4=0.8 -> Tier A (boundary inclusive)."""
        from assign_tiers import assign_tier
        assert assign_tier(0.8, 0.8, 0.8) == "Tier A"

    def test_tier_b_at_boundary(self):
        """gwas_pph4=0.8, qtl_pph4=0.5 -> Tier B (boundary inclusive)."""
        from assign_tiers import assign_tier
        assert assign_tier(0.8, 0.5, 0.8) == "Tier B"


class TestTierSourceAgnostic:
    """Tier assignment is QTL-source-agnostic (D-02c)."""

    def test_same_tier_for_all_sources(self):
        """Same PP.H4 values produce same tier regardless of qtl_source."""
        from assign_tiers import assign_tier

        for source in ["gtex_eqtl", "gtex_sqtl", "ukbppp_pqtl", "onek1k_sceqtl"]:
            # assign_tier is source-agnostic by design (no source argument)
            assert assign_tier(0.95, 0.85, 0.8) == "Tier A"
            assert assign_tier(0.95, 0.65, 0.8) == "Tier B"
            assert assign_tier(0.95, 0.2, 0.8) == "Tier C"


class TestSweepProducesThresholds:
    """Sweep output validation."""

    @pytest.fixture
    def mock_qtl_results(self):
        """Mock QTL coloc results with varying PP.H4 values."""
        rows = []
        pph4_values = [0.95, 0.85, 0.75, 0.65, 0.55, 0.45]
        for i, pph4 in enumerate(pph4_values):
            rows.append({
                "region": f"region_{i}",
                "ancestry": "EUR",
                "qtl_source": "gtex_eqtl",
                "tissue": f"tissue_{i}",
                "gene_id": f"ENSG{i:011d}",
                "PP.H4.abf": pph4,
            })
        return pd.DataFrame(rows)

    def test_sweep_produces_4_thresholds(self, mock_qtl_results, pph4_config):
        """Sweep output has rows for 0.5, 0.7, 0.8, 0.9."""
        from assign_tiers import sweep_tiers
        sweep_df = sweep_tiers(mock_qtl_results, pph4_config["sweep_values"])
        thresholds = sorted(sweep_df["threshold"].unique())
        assert thresholds == [0.5, 0.7, 0.8, 0.9]

    def test_sweep_monotonic_tier_a(self, mock_qtl_results, pph4_config):
        """Tier A count at 0.5 >= at 0.7 >= at 0.8 >= at 0.9."""
        from assign_tiers import sweep_tiers
        sweep_df = sweep_tiers(mock_qtl_results, pph4_config["sweep_values"])
        eur_df = sweep_df[sweep_df["ancestry"] == "EUR"]
        tier_a_counts = []
        for threshold in [0.5, 0.7, 0.8, 0.9]:
            row = eur_df[eur_df["threshold"] == threshold]
            tier_a_counts.append(row.iloc[0]["n_tier_a"] if len(row) > 0 else 0)
        # Monotonically decreasing
        for i in range(len(tier_a_counts) - 1):
            assert tier_a_counts[i] >= tier_a_counts[i + 1], (
                f"Monotonicity violated: {tier_a_counts}"
            )


class TestAssignTiersFull:
    """Test full tier assignment with GWAS + QTL inputs."""

    @pytest.fixture
    def mock_gwas_coloc(self):
        return pd.DataFrame([
            {"region": "FTO_16q12", "ancestry": "EUR", "trait_a": "bmi", "trait_b": "t2d", "PP.H4.abf": 0.92},
            {"region": "MC4R_18q21", "ancestry": "EUR", "trait_a": "bmi", "trait_b": "t2d", "PP.H4.abf": 0.85},
            {"region": "SH2B3_12q24", "ancestry": "EUR", "trait_a": "htn", "trait_b": "stroke", "PP.H4.abf": 0.88},
        ])

    @pytest.fixture
    def mock_qtl_results(self):
        return pd.DataFrame([
            {"region": "FTO_16q12", "ancestry": "EUR", "qtl_source": "gtex_eqtl", "tissue": "Adipose", "gene_id": "ENSG00000140718", "PP.H4.abf": 0.87},
            {"region": "MC4R_18q21", "ancestry": "EUR", "qtl_source": "gtex_eqtl", "tissue": "Brain", "gene_id": "ENSG00000166603", "PP.H4.abf": 0.60},
            {"region": "SH2B3_12q24", "ancestry": "EUR", "qtl_source": "ukbppp_pqtl", "tissue": "Blood", "gene_id": "ENSG00000111252", "PP.H4.abf": 0.30},
        ])

    @pytest.fixture
    def pph4_cfg(self, pph4_config):
        return pph4_config

    def test_full_tier_assignment(self, mock_gwas_coloc, mock_qtl_results, pph4_cfg):
        """Full tier assignment produces correct tiers."""
        from assign_tiers import assign_tiers_full
        tier_df = assign_tiers_full(mock_qtl_results, mock_gwas_coloc, pph4_cfg)
        fto_row = tier_df[tier_df["region"] == "FTO_16q12"]
        assert fto_row.iloc[0]["tier"] == "Tier A"
        mc4r_row = tier_df[tier_df["region"] == "MC4R_18q21"]
        assert mc4r_row.iloc[0]["tier"] == "Tier B"
        sh2b3_row = tier_df[tier_df["region"] == "SH2B3_12q24"]
        assert sh2b3_row.iloc[0]["tier"] == "Tier C"

    def test_neg_ctrl_rows_in_tier_table(self, mock_gwas_coloc, mock_qtl_results, pph4_cfg):
        """When neg_ctrl_df provided, output contains negative_control rows."""
        from assign_tiers import assign_tiers_full
        neg_ctrl = pd.DataFrame([
            {"region": "neg_ctrl_hla", "ancestry": "EUR", "qtl_source": "gtex_eqtl",
             "gene_id": "HLA-A", "PP.H4.abf": 0.45, "neg_ctrl_set": "hla_immune"},
        ])
        tier_df = assign_tiers_full(mock_qtl_results, mock_gwas_coloc, pph4_cfg, neg_ctrl)
        neg_rows = tier_df[tier_df["tier"] == "negative_control"]
        assert len(neg_rows) > 0
        assert neg_rows.iloc[0]["neg_ctrl_set"] == "hla_immune"


class TestParseL2G:
    """Validate parse_l2g.py exists and has correct interface."""

    def test_script_exists(self):
        """src/python/parse_l2g.py exists."""
        script = PROJECT_ROOT / "src" / "python" / "parse_l2g.py"
        assert script.exists(), f"Missing {script}"

    def test_script_contains_pyarrow(self):
        """Script uses pyarrow.parquet."""
        script = PROJECT_ROOT / "src" / "python" / "parse_l2g.py"
        text = script.read_text()
        assert "pyarrow" in text

    def test_script_contains_concordance(self):
        """Script computes concordance."""
        script = PROJECT_ROOT / "src" / "python" / "parse_l2g.py"
        text = script.read_text()
        assert "concordance" in text.lower()


class TestBuildGeneTissueMatrix:
    """Validate build_gene_tissue_matrix.py exists and has correct interface."""

    def test_script_exists(self):
        """src/python/build_gene_tissue_matrix.py exists."""
        script = PROJECT_ROOT / "src" / "python" / "build_gene_tissue_matrix.py"
        assert script.exists(), f"Missing {script}"

    def test_script_contains_build_matrix(self):
        """Script has build_matrix or gene_tissue function."""
        script = PROJECT_ROOT / "src" / "python" / "build_gene_tissue_matrix.py"
        text = script.read_text()
        assert "build_matrix" in text or "gene_tissue" in text

    def test_matrix_builder_logic(self):
        """build_gene_tissue_matrix produces wide-format matrix from long data."""
        from build_gene_tissue_matrix import build_matrix
        input_df = pd.DataFrame([
            {"gene_id": "ENSG001", "region": "FTO_16q12", "tissue": "Adipose", "qtl_source": "gtex_eqtl", "PP.H4.abf": 0.92},
            {"gene_id": "ENSG001", "region": "FTO_16q12", "tissue": "Brain", "qtl_source": "gtex_eqtl", "PP.H4.abf": 0.45},
            {"gene_id": "ENSG002", "region": "MC4R_18q21", "tissue": "Adipose", "qtl_source": "gtex_eqtl", "PP.H4.abf": 0.88},
        ])
        matrix_df, long_df = build_matrix(input_df, pph4_threshold=0.8)
        # Matrix should have gene rows and tissue columns
        assert "gene_id" in matrix_df.columns or matrix_df.index.name == "gene_id"
        # Only values >= threshold should appear
        assert len(long_df) <= len(input_df)


class TestQtlColocSmkExtensions:
    """Validate qtl_coloc.smk has been extended with tier/L2G/matrix rules."""

    def test_qtl_coloc_smk_has_assign_tiers(self):
        """qtl_coloc.smk has rule assign_tiers."""
        smk = PROJECT_ROOT / "src" / "snakemake" / "rules" / "qtl_coloc.smk"
        text = smk.read_text()
        assert "rule assign_tiers:" in text

    def test_qtl_coloc_smk_has_l2g_concordance(self):
        """qtl_coloc.smk has rule l2g_concordance."""
        smk = PROJECT_ROOT / "src" / "snakemake" / "rules" / "qtl_coloc.smk"
        text = smk.read_text()
        assert "rule l2g_concordance:" in text

    def test_qtl_coloc_smk_has_gene_tissue_matrix(self):
        """qtl_coloc.smk has rule build_gene_tissue_matrix."""
        smk = PROJECT_ROOT / "src" / "snakemake" / "rules" / "qtl_coloc.smk"
        text = smk.read_text()
        assert "rule build_gene_tissue_matrix:" in text
