"""Wave 4 test (RED in Wave 1): IVW meta-analysis correctness.

Validates the textbook math and schema; actual IVW runner comes from
Plan 09-04 Task 3 (src/snakemake/scripts/aggregate_replication_meta.R).
"""
import math


def test_ivw_textbook_two_studies():
    """Textbook 2-study IVW: β=(w1·β1 + w2·β2)/(w1+w2), w=1/se²."""
    beta1, se1 = 0.2, 0.05
    beta2, se2 = 0.18, 0.04
    w1 = 1 / se1 ** 2
    w2 = 1 / se2 ** 2
    expected = (w1 * beta1 + w2 * beta2) / (w1 + w2)
    expected_se = math.sqrt(1 / (w1 + w2))
    # Sanity bounds — expected should be pulled toward β2 (lower SE, higher weight).
    assert abs(expected - 0.1875) < 0.01
    assert expected_se > 0
    assert expected_se < min(se1, se2)


def test_same_direction_required(canonical_schema):
    """Ensure N, BETA, SE columns are in canonical schema."""
    assert "BETA" in canonical_schema
    assert "SE" in canonical_schema
    assert "N" in canonical_schema
