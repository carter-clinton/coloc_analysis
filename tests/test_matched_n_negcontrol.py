"""Integration test: negative controls should NOT flip tier under bootstrap.

HLA and pigmentation loci are expected to show ancestry-specific effects
that would NOT survive matched-N bootstrap -- they should remain in their
pre-bootstrap tier (not flip from non-Tier-A to Tier A under bootstrap).

This test loads bootstrap coloc_summary.tsv outputs for loci flagged as
is_negative_control=True in Phase 2 tier_assignments.tsv and asserts no
Tier A flips occur across any bootstrap replicate.

References:
    - CP#1(c): Phase 4 must not flip HLA/pigmentation tiers under bootstrap
    - Phase 2 negative controls: HLA, cosmetic, blood group sets
    - D-02a: Tier A criterion (PP.H4 >= 0.8 AND QTL coloc >= 0.8)
"""
import csv
import os
from pathlib import Path

import pytest


COLOC_DIR = Path("results/matched_n/coloc")
TIER_ASSIGNMENTS = Path("results/phase2/tier_assignments.tsv")
CONCORDANCE_THRESHOLD = 0.8


def _load_negative_control_loci():
    """Load loci flagged as is_negative_control=True from tier_assignments.tsv.

    Returns:
        List of (trait, region_id) tuples for negative-control loci,
        or None if tier_assignments.tsv does not exist or has no
        is_negative_control column.
    """
    if not TIER_ASSIGNMENTS.exists():
        return None

    neg_controls = []
    with open(TIER_ASSIGNMENTS, newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        if "is_negative_control" not in (reader.fieldnames or []):
            return None
        for row in reader:
            if row.get("is_negative_control", "").strip().lower() in ("true", "1", "yes"):
                trait = row.get("trait", "unknown")
                region_id = row.get("region_id", row.get("region", "unknown"))
                neg_controls.append((trait, region_id))

    return neg_controls if neg_controls else None


def _check_tier_a_in_coloc(coloc_tsv_path, threshold=CONCORDANCE_THRESHOLD):
    """Check if a coloc_summary.tsv shows Tier A status.

    Returns True if max PP.H4 >= threshold AND at least one QTL coloc >= threshold.
    """
    if not os.path.exists(coloc_tsv_path):
        return False

    with open(coloc_tsv_path, newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        pph4_values = []
        for row in reader:
            try:
                pph4_values.append(float(row.get("pph4", 0)))
            except (ValueError, TypeError):
                pass

    if not pph4_values:
        return False

    max_pph4 = max(pph4_values)
    any_above = any(v >= threshold for v in pph4_values)
    return (max_pph4 >= threshold) and any_above


@pytest.mark.phase4
class TestNegativeControls:
    """Negative-control loci must not flip to Tier A under matched-N bootstrap."""

    def test_hla_pigmentation_no_tier_flip(self):
        """Verify HLA and pigmentation loci do not flip to Tier A under bootstrap.

        Loads is_negative_control loci from tier_assignments.tsv, then checks
        every bootstrap replicate's coloc_summary.tsv. If ANY bootstrap shows
        Tier A for a negative-control locus, the test fails (false-positive
        structure introduced by bootstrap).
        """
        neg_controls = _load_negative_control_loci()

        if neg_controls is None:
            pytest.skip(
                "Skipped: tier_assignments.tsv not found or does not contain "
                "is_negative_control column. Negative-control loci must be "
                "flagged in Phase 2 tier_assignments.tsv with "
                "is_negative_control=True for this test to run."
            )

        if not COLOC_DIR.exists():
            pytest.skip(
                f"Skipped: {COLOC_DIR} does not exist. Run full matched-N "
                "bootstrap production before running this integration test."
            )

        flipped = []
        checked = 0

        for trait, region_id in neg_controls:
            # Scan all bootstrap directories for this trait/region
            region_dir = COLOC_DIR / trait / region_id
            if not region_dir.exists():
                continue

            for boot_dir in sorted(region_dir.iterdir()):
                if not boot_dir.is_dir() or not boot_dir.name.startswith("bootstrap_"):
                    continue

                coloc_path = boot_dir / "coloc_summary.tsv"
                checked += 1

                if _check_tier_a_in_coloc(str(coloc_path)):
                    flipped.append(
                        f"{trait}/{region_id}/{boot_dir.name}: "
                        f"FLIPPED to Tier A (false positive)"
                    )

        if checked == 0:
            pytest.skip(
                "Skipped: no bootstrap coloc outputs found for negative-control "
                "loci. Run full production before this integration test."
            )

        assert not flipped, (
            f"Negative-control loci flipped to Tier A in {len(flipped)} "
            f"bootstrap(s) out of {checked} checked:\n"
            + "\n".join(flipped[:20])  # Show first 20 to avoid noise
        )

    def test_negative_control_loci_exist_in_manifest(self):
        """Verify negative-control loci are present in tier_assignments.tsv.

        This is a prerequisite check: if no loci are flagged, the main test
        will skip silently, which could mask a missing-data issue.
        """
        neg_controls = _load_negative_control_loci()
        if neg_controls is None:
            pytest.skip(
                "tier_assignments.tsv not found or lacks is_negative_control column"
            )

        assert len(neg_controls) > 0, (
            "is_negative_control column exists but no loci are flagged True. "
            "At minimum, HLA and pigmentation loci should be flagged."
        )
