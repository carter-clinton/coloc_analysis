"""Tests for GRCh37 -> GRCh38 liftover of curated regions.

Validates that config/regions_curated_grch38.csv exists and contains
valid lifted coordinates for all 12 regions in regions_curated.csv.
"""
import csv
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestLiftoverOutput:
    """Validate the GRCh38-lifted regions CSV."""

    def test_grch38_csv_exists(self, regions_grch38_path):
        assert regions_grch38_path.exists(), (
            f"Expected GRCh38 regions file at {regions_grch38_path}"
        )

    def test_grch38_has_12_regions(self, regions_grch38):
        assert len(regions_grch38) == 12, (
            f"Expected 12 data rows, got {len(regions_grch38)}"
        )

    def test_required_columns_present(self, regions_grch38):
        required = {
            "region_id", "chr", "start_grch37", "end_grch37",
            "start_grch38", "end_grch38", "lead_snp", "gene",
            "trait_list", "source", "lift_status",
        }
        actual = set(regions_grch38[0].keys())
        missing = required - actual
        assert not missing, f"Missing columns: {missing}"

    def test_all_regions_lift_status_ok(self, regions_grch38):
        for row in regions_grch38:
            assert row["lift_status"] == "OK", (
                f"Region {row['region_id']} has lift_status={row['lift_status']}"
            )

    def test_start_lt_end_grch38(self, regions_grch38):
        for row in regions_grch38:
            start = int(row["start_grch38"])
            end = int(row["end_grch38"])
            assert start < end, (
                f"Region {row['region_id']}: start_grch38 ({start}) >= end_grch38 ({end})"
            )

    def test_fto_grch38_coordinates(self, regions_grch38):
        """FTO_16q12 GRCh38 coordinates should be within 200 kb of 53700000."""
        fto = [r for r in regions_grch38 if r["region_id"] == "FTO_16q12"]
        assert len(fto) == 1, f"Expected 1 FTO_16q12 row, got {len(fto)}"
        start = int(fto[0]["start_grch38"])
        assert abs(start - 53700000) < 200000, (
            f"FTO_16q12 start_grch38={start} too far from expected ~53700000"
        )

    def test_region_ids_match_source(self, regions_grch38):
        """All region_ids in GRCh38 file must match those in regions_curated.csv."""
        source_path = PROJECT_ROOT / "config" / "regions_curated.csv"
        with open(source_path, newline="") as f:
            source_ids = {r["region_id"] for r in csv.DictReader(f)}
        lifted_ids = {r["region_id"] for r in regions_grch38}
        assert source_ids == lifted_ids, (
            f"ID mismatch: in source not lifted={source_ids - lifted_ids}, "
            f"in lifted not source={lifted_ids - source_ids}"
        )

    def test_region_size_sanity(self, regions_grch38):
        """Lifted region size should not differ from GRCh37 size by more than 100 kb."""
        source_path = PROJECT_ROOT / "config" / "regions_curated.csv"
        with open(source_path, newline="") as f:
            source_sizes = {
                r["region_id"]: int(r["end"]) - int(r["start"])
                for r in csv.DictReader(f)
            }
        for row in regions_grch38:
            size_38 = int(row["end_grch38"]) - int(row["start_grch38"])
            size_37 = source_sizes.get(row["region_id"], size_38)
            diff = abs(size_38 - size_37)
            assert diff < 100000, (
                f"Region {row['region_id']}: size diff {diff} bp between builds exceeds 100 kb"
            )
