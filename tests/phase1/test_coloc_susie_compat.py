"""Phase 1 Wave 4 (01-04) -- compat test for run_coloc_susie.R output schema.

Verifies that the JSON emitted by src/snakemake/scripts/run_coloc_susie.R
remains parseable by the legacy downstream consumer
src/legacy/region_analysis/scripts/augment_coloc_summary.py without
modification (legacy-compat Pattern 6 Option A from 01-RESEARCH.md).

These tests run against a hand-written fixture that mirrors the expected
JSON schema. The real end-to-end smoke test (coloc.susie on toy .fit.rds
pairs) is deferred to Plan 01-06.
"""
import json
from pathlib import Path

import pytest

PHASE1_ROOT = Path(__file__).resolve().parent
FIXTURE = PHASE1_ROOT / "fixtures" / "expected_coloc_susie_output.json"
PROJECT_ROOT = PHASE1_ROOT.parents[1]
CONSUMER = PROJECT_ROOT / "src" / "legacy" / "region_analysis" / "scripts" / "augment_coloc_summary.py"


@pytest.fixture(scope="module")
def fixture_data():
    assert FIXTURE.exists(), f"Fixture not found: {FIXTURE}"
    return json.loads(FIXTURE.read_text())


def test_fixture_has_legacy_top_level_keys(fixture_data):
    """All top-level keys required by the legacy consumer must be present."""
    required_top = {
        "pair_id",
        "status",
        "trait_a",
        "trait_b",
        "ancestry",
        "region",
        "base_region",
        "summary",
        "susie_pairs",
    }
    missing = required_top - set(fixture_data.keys())
    assert not missing, f"Missing top-level keys required by legacy consumers: {missing}"


def test_summary_has_pp_h4_abf(fixture_data):
    """The best-pairwise 'summary' block must expose legacy PP.*.abf fields."""
    pp_keys = {"PP.H0.abf", "PP.H1.abf", "PP.H2.abf", "PP.H3.abf", "PP.H4.abf"}
    missing = pp_keys - set(fixture_data["summary"].keys())
    assert not missing, f"Missing PP.*.abf keys in summary: {missing}"


def test_summary_has_nsnps(fixture_data):
    """nsnps must exist on the summary for augment_coloc_summary.py row math."""
    assert "nsnps" in fixture_data["summary"], "summary missing 'nsnps'"
    assert fixture_data["summary"]["nsnps"] is None or isinstance(
        fixture_data["summary"]["nsnps"], int
    )


def test_susie_pairs_is_array(fixture_data):
    """New Phase 1 field: susie_pairs must be a list of dicts."""
    pairs = fixture_data["susie_pairs"]
    assert isinstance(pairs, list), "susie_pairs must be a JSON array"
    for i, row in enumerate(pairs):
        assert isinstance(row, dict), f"susie_pairs[{i}] is not a dict"


def test_susie_pairs_has_pp_keys(fixture_data):
    """Each pairwise row must expose the five posterior probability fields."""
    pp_keys = {"PP.H0.abf", "PP.H1.abf", "PP.H2.abf", "PP.H3.abf", "PP.H4.abf"}
    for i, row in enumerate(fixture_data["susie_pairs"]):
        missing = pp_keys - set(row.keys())
        assert not missing, f"susie_pairs[{i}] missing PP keys: {missing}"


def test_best_pairwise_is_max_h4(fixture_data):
    """Pattern 6 Option A: summary must equal the row with the highest PP.H4.abf."""
    pairs = fixture_data["susie_pairs"]
    if not pairs:
        pytest.skip("no pairwise rows in fixture (no_signal path)")
    best = max(pairs, key=lambda r: r["PP.H4.abf"])
    assert fixture_data["summary"]["PP.H4.abf"] == best["PP.H4.abf"], (
        "summary.PP.H4.abf does not match max over susie_pairs"
    )


def test_augment_consumer_readable_fields(fixture_data):
    """Mimic the field reads that augment_coloc_summary.py performs.

    augment_coloc_summary.py reads a TSV produced by summarize_coloc_results.py,
    which in turn aggregates JSON files. We verify the raw JSON exposes the
    fields that summarize_coloc_results.py / the legacy TSV extraction rely on.
    """
    if not CONSUMER.exists():
        pytest.skip(f"consumer script not present at {CONSUMER}")
    # Fields that the consumer pipeline transitively needs:
    _ = fixture_data["summary"]["PP.H4.abf"]
    _ = fixture_data["summary"]["nsnps"]
    _ = fixture_data["pair_id"]
    _ = fixture_data["ancestry"]
    _ = fixture_data["trait_a"]
    _ = fixture_data["trait_b"]


def test_r_script_parses_and_emits_compat_keys():
    """Static audit of the R script: confirm it writes the Pattern 6 keys."""
    script = PROJECT_ROOT / "src" / "snakemake" / "scripts" / "run_coloc_susie.R"
    assert script.exists(), f"run_coloc_susie.R not found at {script}"
    text = script.read_text()
    # These literal identifiers must appear in the script so the emitted JSON
    # carries the legacy-compat schema.
    for token in ("susie_pairs", "PP.H0.abf", "PP.H4.abf", "coloc::coloc.susie", "readRDS"):
        assert token in text, f"run_coloc_susie.R missing token: {token}"
