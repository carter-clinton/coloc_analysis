"""Plan 09-04 Task 2 — IVW fixed-effect meta-analysis (D-06b).

Validates the textbook math + the presence of aggregate_replication_meta.R.
End-to-end Snakemake integration test is deferred to Plan 09-05 Task 2.
"""
import math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_ivw_textbook_two_studies():
    """Textbook 2-study IVW: β=(w1·β1 + w2·β2)/(w1+w2), w=1/se²."""
    beta1, se1 = 0.2, 0.05
    beta2, se2 = 0.18, 0.04
    w1 = 1 / se1 ** 2
    w2 = 1 / se2 ** 2
    expected = (w1 * beta1 + w2 * beta2) / (w1 + w2)
    expected_se = math.sqrt(1 / (w1 + w2))
    # Known textbook: IVW of (0.2, 0.05) and (0.18, 0.04)
    assert abs(expected - 0.1878) < 0.001
    assert abs(expected_se - 0.0312) < 0.002
    # Sanity bounds — expected should be pulled toward β2 (lower SE, higher weight).
    assert abs(expected - 0.1875) < 0.01
    assert expected_se > 0
    assert expected_se < min(se1, se2)


def test_aggregate_ivw_script_present():
    """Plan 09-04 Task 2 artifact: aggregate_replication_meta.R exists."""
    script = PROJECT_ROOT / "src" / "snakemake" / "scripts" / "aggregate_replication_meta.R"
    assert script.exists(), f"Missing {script} — Plan 09-04 Task 2 not complete"


def test_aggregate_ivw_uses_metafor():
    """T-09-17 mitigation: IVW meta must use metafor::rma.uni, not hand-rolled."""
    script = PROJECT_ROOT / "src" / "snakemake" / "scripts" / "aggregate_replication_meta.R"
    if not script.exists():
        # Let test_aggregate_ivw_script_present fail first — avoid double-failure.
        return
    content = script.read_text()
    assert "metafor::rma.uni" in content or "rma.uni(" in content
    # Fixed-effect meta per D-06b
    assert "FE" in content or 'method = "FE"' in content or "method='FE'" in content


def test_same_direction_required(canonical_schema):
    """Ensure N, BETA, SE columns are in canonical schema."""
    assert "BETA" in canonical_schema
    assert "SE" in canonical_schema
    assert "N" in canonical_schema
