"""Phase 1 Plan 01-05 -- QC dashboard aggregator + rendered HTML validation.

Test suite for susie_qc_aggregate.py and the rendered qc_dashboard.html.

- test_aggregator_*: unit tests that run the aggregator on fixture JSONs and
  validate TSV schema, D1/D2/D3/D4/ld_source/L_saturated/is_complex_region columns.
- test_sweep_*: validate the sweep_complex_regions.tsv supplementary table.
- test_dashboard_*: integration tests that check the rendered HTML contains
  required column headers and the HLA T-1-04 flag. These tests skip when the
  dashboard has not yet been rendered (deferred to Plan 01-06 real run).

REQ-2 acceptance #5: Per-locus fine-mapping QC report generated.
T-1-04 mitigation: HLA block-diagonal flag surfaced in dashboard.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures"

# Expected aggregator TSV columns (must match susie_qc_aggregate.AGGREGATE_COLUMNS)
REQUIRED_COLUMNS = {
    "region_id",
    "trait",
    "ancestry",
    "status",
    "convergence_status",
    "L_used",
    "L_saturated",
    "ld_source",
    "n_variants",
    "ks_pvalue",
    "max_abs_z",
    "lambda_gc",
    "converged",
    "niter",
    "elbo_final",
    "kriging_n_outliers",
    "kriging_max_logLR",
    "kriging_lambda",
    "n_CS_macor_0.1",
    "n_CS_macor_0.5",
    "n_CS_macor_0.9",
    "total_PIP_macor_0.1",
    "total_PIP_macor_0.5",
    "total_PIP_macor_0.9",
    "max_PIP",
    "is_complex_region",
}

SWEEP_REQUIRED_COLUMNS = {
    "row_group",
    "region_id",
    "trait",
    "ancestry",
    "n_CS_macor_0.1",
    "n_CS_macor_0.5",
    "n_CS_macor_0.9",
    "total_PIP_macor_0.1",
    "total_PIP_macor_0.5",
    "total_PIP_macor_0.9",
    "L_saturated",
    "max_PIP",
    "ld_source",
}

# Dashboard path (only present after a real pipeline run)
FINEMAP_DIR = Path(os.environ.get("FINEMAP_DIR", "results/finemap"))
DASHBOARD = FINEMAP_DIR / "qc_dashboard.html"

# Aggregator script path
AGGREGATOR = Path("src/snakemake/scripts/susie_qc_aggregate.py")
POLICY = Path("config/susie_policy.yaml")

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_FIXTURE = FIXTURE_DIR / "sample_susie_output.json"

# Synthetic HLA fixture with block-diagonal LD flag
HLA_FIXTURE_DATA = {
    "region_id": "HLA_6p21",
    "trait": "t2d",
    "ancestry": "EUR",
    "status": "success",
    "converged": True,
    "niter": 200,
    "elbo_final": -456.78,
    "convergence_status": "converged_max_iter",
    "L_used": 10,
    "L_saturated": True,
    "ld_matrix": "ukbb_ld_tiled_block_diagonal",
    "n_variants": 5000,
    "min_abs_corr_sweep": [
        {"min_abs_corr": 0.1, "n_CS": 5, "cs_sizes": [20, 15, 12, 8, 3],
         "cs_pip_sum": [0.98, 0.95, 0.90, 0.80, 0.40]},
        {"min_abs_corr": 0.5, "n_CS": 3, "cs_sizes": [20, 15, 12],
         "cs_pip_sum": [0.98, 0.95, 0.90]},
        {"min_abs_corr": 0.9, "n_CS": 1, "cs_sizes": [20],
         "cs_pip_sum": [0.98]},
    ],
    "d1_zscore_sanity": {"ks_pvalue": 0.05, "max_abs_z": 12.3, "lambda_gc": 1.15},
    "d2_convergence": {
        "converged": True,
        "niter": 200,
        "elbo_final": -456.78,
        "convergence_status": "converged_max_iter",
    },
    "d3_ld_quality": {"n_outliers": 15, "max_logLR": 8.2, "lambda": 1.12},
}


@pytest.fixture(scope="module")
def fixture_json_dir(tmp_path_factory):
    """Create a temp dir with two fixture JSONs for aggregator testing."""
    d = tmp_path_factory.mktemp("finemap_json")
    susie_dir = d / "susie"
    susie_dir.mkdir()

    # Copy sample fixture
    sample_data = json.loads(SAMPLE_FIXTURE.read_text())
    (susie_dir / "synthetic_test.json").write_text(json.dumps(sample_data, indent=2))

    # Write HLA fixture
    (susie_dir / "hla_test.json").write_text(json.dumps(HLA_FIXTURE_DATA, indent=2))

    return d


@pytest.fixture(scope="module")
def aggregated_tsv(fixture_json_dir, tmp_path_factory):
    """Run the aggregator on fixture JSONs and return path to output TSV."""
    out_dir = tmp_path_factory.mktemp("aggregated")
    out_tsv = out_dir / "qc_aggregated.tsv"
    result = subprocess.run(
        [
            sys.executable,
            str(AGGREGATOR),
            "--input-dir",
            str(fixture_json_dir / "susie"),
            "--output",
            str(out_tsv),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Aggregator failed:\n{result.stderr}"
    assert out_tsv.exists(), "Aggregator did not produce output TSV"
    return out_tsv


@pytest.fixture(scope="module")
def sweep_tsv(aggregated_tsv, tmp_path_factory):
    """Run the aggregator in --aggregated-only mode to produce sweep table."""
    out_dir = tmp_path_factory.mktemp("sweep")
    sweep_path = out_dir / "sweep_complex_regions.tsv"
    result = subprocess.run(
        [
            sys.executable,
            str(AGGREGATOR),
            "--aggregated-only",
            "--input",
            str(aggregated_tsv),
            "--policy",
            str(POLICY),
            "--sweep-out",
            str(sweep_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Sweep generation failed:\n{result.stderr}"
    assert sweep_path.exists(), "Aggregator did not produce sweep TSV"
    return sweep_path


# ---------------------------------------------------------------------------
# Aggregator unit tests
# ---------------------------------------------------------------------------


class TestAggregatorSchema:
    """Verify aggregated TSV schema and content."""

    def test_aggregator_produces_tsv(self, aggregated_tsv):
        assert aggregated_tsv.exists()
        assert aggregated_tsv.stat().st_size > 0

    def test_aggregator_has_required_columns(self, aggregated_tsv):
        with open(aggregated_tsv) as f:
            reader = csv.DictReader(f, delimiter="\t")
            columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        assert not missing, f"Aggregated TSV missing columns: {missing}"

    def test_aggregator_has_rows(self, aggregated_tsv):
        with open(aggregated_tsv) as f:
            reader = csv.DictReader(f, delimiter="\t")
            rows = list(reader)
        assert len(rows) == 2, f"Expected 2 fixture rows, got {len(rows)}"

    def test_aggregator_d1_populated(self, aggregated_tsv):
        """D1 z-score sanity check fields are non-empty."""
        with open(aggregated_tsv) as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                assert row["ks_pvalue"], f"ks_pvalue empty for {row['region_id']}"
                assert row["max_abs_z"], f"max_abs_z empty for {row['region_id']}"
                assert row["lambda_gc"], f"lambda_gc empty for {row['region_id']}"

    def test_aggregator_d2_populated(self, aggregated_tsv):
        """D2 convergence fields are non-empty."""
        with open(aggregated_tsv) as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                assert row["niter"], f"niter empty for {row['region_id']}"
                assert row["elbo_final"], f"elbo_final empty for {row['region_id']}"
                assert row["convergence_status"], (
                    f"convergence_status empty for {row['region_id']}"
                )

    def test_aggregator_d3_populated(self, aggregated_tsv):
        """D3 LD quality fields are non-empty."""
        with open(aggregated_tsv) as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                assert row["kriging_n_outliers"], (
                    f"kriging_n_outliers empty for {row['region_id']}"
                )

    def test_aggregator_d4_sweep_monotonic(self, aggregated_tsv):
        """D4 n_CS counts should be monotonically non-increasing as min_abs_corr rises."""
        with open(aggregated_tsv) as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                n01 = int(row["n_CS_macor_0.1"])
                n05 = int(row["n_CS_macor_0.5"])
                n09 = int(row["n_CS_macor_0.9"])
                assert n01 >= n05 >= n09, (
                    f"Non-monotonic CS counts for {row['region_id']}: "
                    f"{n01} >= {n05} >= {n09}"
                )

    def test_aggregator_ld_source_surfaced(self, aggregated_tsv):
        """T-1-04: ld_source field must be populated for HLA fixture."""
        with open(aggregated_tsv) as f:
            reader = csv.DictReader(f, delimiter="\t")
            rows = list(reader)
        hla_rows = [r for r in rows if r["region_id"] == "HLA_6p21"]
        assert hla_rows, "HLA_6p21 fixture row not found in aggregated TSV"
        assert hla_rows[0]["ld_source"] == "ukbb_ld_tiled_block_diagonal", (
            f"Expected HLA ld_source flag, got: {hla_rows[0]['ld_source']!r}"
        )

    def test_aggregator_complex_region_flagged(self, aggregated_tsv):
        """is_complex_region must be True for HLA_6p21."""
        with open(aggregated_tsv) as f:
            reader = csv.DictReader(f, delimiter="\t")
            rows = list(reader)
        hla_rows = [r for r in rows if r["region_id"] == "HLA_6p21"]
        assert hla_rows, "HLA_6p21 fixture row not found"
        assert hla_rows[0]["is_complex_region"] == "True", (
            f"Expected is_complex_region=True for HLA, got: "
            f"{hla_rows[0]['is_complex_region']!r}"
        )

    def test_aggregator_l_saturated(self, aggregated_tsv):
        """L_saturated must be True for HLA fixture."""
        with open(aggregated_tsv) as f:
            reader = csv.DictReader(f, delimiter="\t")
            rows = list(reader)
        hla_rows = [r for r in rows if r["region_id"] == "HLA_6p21"]
        assert hla_rows
        assert hla_rows[0]["L_saturated"] == "True"


# ---------------------------------------------------------------------------
# Sweep table tests (Task 1-05-04)
# ---------------------------------------------------------------------------


class TestSweepTable:
    """Verify sweep_complex_regions.tsv schema and content."""

    def test_sweep_exists(self, sweep_tsv):
        assert sweep_tsv.exists()

    def test_sweep_has_required_columns(self, sweep_tsv):
        lines = [
            l for l in sweep_tsv.read_text().splitlines() if not l.startswith("##")
        ]
        if not lines:
            pytest.skip("Sweep table empty (no data rows)")
        reader = csv.DictReader(lines, delimiter="\t")
        columns = set(reader.fieldnames or [])
        missing = SWEEP_REQUIRED_COLUMNS - columns
        assert not missing, f"Sweep TSV missing columns: {missing}"

    def test_sweep_hla_in_known_complex(self, sweep_tsv):
        """HLA_6p21 should appear in known_complex group."""
        lines = [
            l for l in sweep_tsv.read_text().splitlines() if not l.startswith("##")
        ]
        reader = csv.DictReader(lines, delimiter="\t")
        rows = list(reader)
        hla_known = [
            r
            for r in rows
            if r["region_id"] == "HLA_6p21" and r["row_group"] == "known_complex"
        ]
        assert hla_known, "HLA_6p21 not found in known_complex group of sweep table"

    def test_sweep_row_groups_valid(self, sweep_tsv):
        """All row_group values must be known_complex or data_flagged."""
        lines = [
            l for l in sweep_tsv.read_text().splitlines() if not l.startswith("##")
        ]
        reader = csv.DictReader(lines, delimiter="\t")
        for row in reader:
            assert row["row_group"] in ("known_complex", "data_flagged"), (
                f"Unexpected row_group: {row['row_group']!r}"
            )


# ---------------------------------------------------------------------------
# Dashboard HTML integration tests (skip until real render in 01-06)
# ---------------------------------------------------------------------------


class TestDashboardHTML:
    """Tests against the rendered qc_dashboard.html (post-pipeline only)."""

    REQUIRED_HTML_COLUMNS = [
        "region_id",
        "trait",
        "ancestry",
        "convergence_status",
        "ld_source",
        "ks_pvalue",
        "max_abs_z",
        "lambda_gc",
        "niter",
        "elbo_final",
        "kriging_n_outliers",
        "n_CS_macor_0.1",
        "n_CS_macor_0.5",
        "n_CS_macor_0.9",
    ]

    def test_dashboard_exists(self):
        if not DASHBOARD.exists():
            pytest.skip(
                f"{DASHBOARD} not yet rendered (deferred to Plan 01-06 real run)"
            )
        assert DASHBOARD.stat().st_size > 1000

    def test_dashboard_has_columns(self):
        if not DASHBOARD.exists():
            pytest.skip(f"{DASHBOARD} not yet rendered")
        html = DASHBOARD.read_text(errors="ignore")
        missing = [c for c in self.REQUIRED_HTML_COLUMNS if c not in html]
        assert not missing, f"Dashboard HTML missing columns: {missing}"

    def test_dashboard_surfaces_hla_flag(self):
        """T-1-04 mitigation check: HLA block-diagonal flag must be present."""
        if not DASHBOARD.exists():
            pytest.skip(f"{DASHBOARD} not yet rendered")
        html = DASHBOARD.read_text(errors="ignore")
        assert "ukbb_ld_tiled_block_diagonal" in html, (
            "HLA block-diagonal flag not surfaced in dashboard (T-1-04 regression)"
        )
