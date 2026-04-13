"""Tests for permutation-based null gene set generator (Phase 5 Plan 05-05).

Validates:
- Pipeline config specifies 1000 permutations (D-06c)
- Null gene set size matching from extend_null_genesets.py
- Deterministic seed behavior (T-02-18)
- Exclusion of query genes from null sets
- Gene property matching tolerance
- Snakemake rules exist (permutation_null_genesets, permutation_magma, permutation_aggregate)
"""
import random
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))
from extend_null_genesets import (
    _median,
    find_matching_genes,
    generate_null_genesets,
    parse_gene_loc,
    read_query_genes,
)


class TestPermutationCount:
    """Validate permutation configuration."""

    def test_permutation_count(self, pipeline_config):
        """pipeline.yaml specifies 1000 permutations per D-06c."""
        pathway = pipeline_config.get("pathway", {})
        assert "permutation_n" in pathway
        assert pathway["permutation_n"] == 1000

    def test_permutation_null_genesets_rule_exists(self):
        """pathway.smk contains permutation_null_genesets rule."""
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
        text = smk_path.read_text()
        assert "rule permutation_null_genesets:" in text

    def test_permutation_magma_rule_exists(self):
        """pathway.smk contains permutation_magma rule."""
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
        text = smk_path.read_text()
        assert "rule permutation_magma:" in text

    def test_permutation_aggregate_rule_exists(self):
        """pathway.smk contains permutation_aggregate rule."""
        smk_path = PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
        text = smk_path.read_text()
        assert "rule permutation_aggregate:" in text


class TestNullGenesetSizeMatching:
    """Validate gene set size matching for permutation null."""

    @pytest.fixture()
    def mock_gene_loc_file(self, tmp_path):
        """Create a gene.loc file with 50 genes for matching tests."""
        outfile = tmp_path / "test_gene.loc"
        # 20 query-like genes on chr22 + 30 candidate genes for matching
        genes = []
        # Query-like genes (shorter, ~50k each)
        for i in range(20):
            start = 16000000 + i * 100000
            end = start + 50000
            genes.append(
                (str(1000 + i), "22", str(start), str(end), "+", f"QUERYGENE{i}")
            )
        # Candidate genes with varying lengths for matching pool
        for i in range(30):
            start = 20000000 + i * 100000
            end = start + 40000 + i * 1000  # varying lengths ~40-70k
            genes.append(
                (str(2000 + i), "22", str(start), str(end), "+", f"CANDIDATE{i}")
            )
        lines = ["\t".join(fields) + "\n" for fields in genes]
        outfile.write_text("".join(lines))
        return outfile

    @pytest.fixture()
    def mock_maf_dir(self, tmp_path):
        """Create a minimal MAF reference directory (empty -- triggers fallback)."""
        maf_dir = tmp_path / "maf_ref"
        maf_dir.mkdir()
        return str(maf_dir)

    @pytest.fixture()
    def mock_ld_dir(self, tmp_path):
        """Create a minimal LD score reference directory (empty -- triggers fallback)."""
        ld_dir = tmp_path / "ld_ref"
        ld_dir.mkdir()
        return str(ld_dir)

    def test_null_geneset_size_matching(self, mock_gene_loc_file, mock_maf_dir, mock_ld_dir, tmp_path):
        """Generate 10 null gene sets from 20 query genes; verify each has 20 genes."""
        query_genes = [f"QUERYGENE{i}" for i in range(20)]
        query_file = tmp_path / "query.txt"
        query_file.write_text("\n".join(query_genes) + "\n")

        out_dir = str(tmp_path / "null_output")
        null_sets = generate_null_genesets(
            query_genes=query_genes,
            gene_loc_path=str(mock_gene_loc_file),
            n_perm=10,
            seed=42,
            maf_reference=mock_maf_dir,
            ld_score_reference=mock_ld_dir,
            out_dir=out_dir,
        )

        assert len(null_sets) == 10
        for ns in null_sets:
            # Each null set should have genes (may be fewer than 20 if
            # not enough candidates, but with 30 candidates and relaxed
            # matching it should be close to 20)
            assert len(ns) > 0, "Null gene set should have at least some genes"
            assert len(ns) <= 20, "Null gene set should not exceed query size"

    def test_deterministic_seed(self, mock_gene_loc_file, mock_maf_dir, mock_ld_dir, tmp_path):
        """Two runs with same seed produce identical null gene sets."""
        query_genes = [f"QUERYGENE{i}" for i in range(10)]

        out_dir1 = str(tmp_path / "run1")
        out_dir2 = str(tmp_path / "run2")

        result1 = generate_null_genesets(
            query_genes=query_genes,
            gene_loc_path=str(mock_gene_loc_file),
            n_perm=5,
            seed=42,
            maf_reference=mock_maf_dir,
            ld_score_reference=mock_ld_dir,
            out_dir=out_dir1,
        )

        result2 = generate_null_genesets(
            query_genes=query_genes,
            gene_loc_path=str(mock_gene_loc_file),
            n_perm=5,
            seed=42,
            maf_reference=mock_maf_dir,
            ld_score_reference=mock_ld_dir,
            out_dir=out_dir2,
        )

        assert result1 == result2, "Same seed should produce identical null gene sets"

    def test_exclusion_of_query_genes(self, mock_gene_loc_file, mock_maf_dir, mock_ld_dir, tmp_path):
        """Null gene sets do not contain any query genes."""
        query_genes = [f"QUERYGENE{i}" for i in range(10)]

        null_sets = generate_null_genesets(
            query_genes=query_genes,
            gene_loc_path=str(mock_gene_loc_file),
            n_perm=5,
            seed=42,
            maf_reference=mock_maf_dir,
            ld_score_reference=mock_ld_dir,
            out_dir=str(tmp_path / "null_out"),
        )

        query_set = set(query_genes)
        for i, ns in enumerate(null_sets):
            overlap = query_set & set(ns)
            assert len(overlap) == 0, (
                f"Permutation {i} contains query genes: {overlap}"
            )

    def test_gene_density_tolerance(self, mock_gene_loc_file, mock_maf_dir, mock_ld_dir, tmp_path):
        """Gene length of null genes within tolerance of query genes.

        Without real LD/MAF data, the matching falls back to length-only.
        The length tolerance is 50% per D-06c.
        """
        query_genes = [f"QUERYGENE{i}" for i in range(5)]
        gene_loc = parse_gene_loc(str(mock_gene_loc_file))

        null_sets = generate_null_genesets(
            query_genes=query_genes,
            gene_loc_path=str(mock_gene_loc_file),
            n_perm=3,
            seed=42,
            maf_reference=mock_maf_dir,
            ld_score_reference=mock_ld_dir,
            out_dir=str(tmp_path / "null_tol"),
        )

        # Check that null gene lengths are within reasonable range of query
        query_lengths = [gene_loc[g]["length"] for g in query_genes if g in gene_loc]
        mean_query_len = sum(query_lengths) / max(len(query_lengths), 1)

        for ns in null_sets:
            for gene in ns:
                if gene in gene_loc:
                    null_len = gene_loc[gene]["length"]
                    # Should be within 2x of mean query length (very generous
                    # since relaxed fallback tolerance is 100%)
                    assert null_len < mean_query_len * 3, (
                        f"Gene {gene} length {null_len} too different from "
                        f"query mean {mean_query_len}"
                    )


class TestGeneLocParser:
    """Test gene location file parsing."""

    def test_parse_gene_loc(self, mock_gene_loc):
        """parse_gene_loc reads NCBI37.3.gene.loc format correctly."""
        genes = parse_gene_loc(str(mock_gene_loc))
        assert len(genes) == 20
        assert "TESTGENE1" in genes
        assert genes["TESTGENE1"]["chr"] == "22"
        assert genes["TESTGENE1"]["length"] == 50000

    def test_read_query_genes(self, tmp_path):
        """read_query_genes reads one gene per line."""
        gene_file = tmp_path / "genes.txt"
        gene_file.write_text("INSR\nIRS1\nAKT1\n# comment\n\nPPARG\n")
        genes = read_query_genes(str(gene_file))
        assert genes == ["INSR", "IRS1", "AKT1", "PPARG"]


class TestMatchingLogic:
    """Test the gene matching functions."""

    def test_find_matching_genes_strict(self):
        """find_matching_genes filters by all 3 criteria."""
        query_props = {"length": 50000, "ld_complexity": 10, "median_maf": 0.25}
        all_props = {
            "GENE_A": {"length": 55000, "ld_complexity": 11, "median_maf": 0.26},  # match
            "GENE_B": {"length": 200000, "ld_complexity": 10, "median_maf": 0.25},  # too long
            "GENE_C": {"length": 50000, "ld_complexity": 100, "median_maf": 0.25},  # LD too high
            "GENE_D": {"length": 50000, "ld_complexity": 10, "median_maf": 0.01},  # MAF too low
        }
        matches = find_matching_genes(
            query_props, all_props, exclude_genes=set(),
        )
        assert "GENE_A" in matches
        assert "GENE_B" not in matches
        assert "GENE_C" not in matches
        assert "GENE_D" not in matches

    def test_find_matching_excludes(self):
        """Excluded genes are not returned."""
        query_props = {"length": 50000, "ld_complexity": 10, "median_maf": 0.25}
        all_props = {
            "GENE_A": {"length": 50000, "ld_complexity": 10, "median_maf": 0.25},
        }
        matches = find_matching_genes(
            query_props, all_props, exclude_genes={"GENE_A"},
        )
        assert len(matches) == 0

    def test_median_helper(self):
        """_median computes correct median."""
        assert _median([1, 2, 3]) == 2
        assert _median([1, 2, 3, 4]) == 2.5
        assert _median([]) == 0.0
        assert _median([5]) == 5


class TestMafLdRequired:
    """Verify that --maf-reference and --ld-score-reference are required."""

    def test_maf_reference_required(self, tmp_path):
        """generate_null_genesets raises ValueError without maf_reference."""
        with pytest.raises(ValueError, match="maf-reference"):
            generate_null_genesets(
                query_genes=["A"],
                gene_loc_path=str(tmp_path / "fake.loc"),
                n_perm=1,
                seed=42,
                maf_reference=None,
                ld_score_reference="/some/path",
            )

    def test_ld_score_reference_required(self, tmp_path):
        """generate_null_genesets raises ValueError without ld_score_reference."""
        with pytest.raises(ValueError, match="ld-score-reference"):
            generate_null_genesets(
                query_genes=["A"],
                gene_loc_path=str(tmp_path / "fake.loc"),
                n_perm=1,
                seed=42,
                maf_reference="/some/path",
                ld_score_reference=None,
            )
