"""m3-02c STEP A — preflight count-pass helper tests.

Covers the count-only preflight mechanism added for the cost probe (Task 3):
the pure cost-sizing estimates (_preflight_estimates) and the TSV driver
(write_preflight_counts), with the Hail count stubbed so no cluster is needed.
"""
import csv
import importlib
import math
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

ld = importlib.import_module("aou_ld_panel")


# --------------------------------------------------------------------------- #
# _preflight_estimates — pure math + routing
# --------------------------------------------------------------------------- #
def test_routing_by_span():
    # small span -> A.1, medium -> A.2, large span -> A.3 (span veto)
    assert ld._preflight_estimates(1000, 3.0, "small", 3_000_000)["routed_path"] == "A.1"
    assert ld._preflight_estimates(1000, 8.0, "medium", 8_000_000)["routed_path"] == "A.2"
    assert ld._preflight_estimates(1000, 20.0, "medium", 10_000_000)["routed_path"] == "A.3"
    assert ld._preflight_estimates(1000, 44.0, "large", 10_000_000)["routed_path"] == "A.3"


def test_est_block_count_formula():
    # ceil(n_var/4096)**2 / 2  (PLAN Task 3 STEP A definition)
    n_var = 122_678
    exp = (math.ceil(n_var / 4096) ** 2) / 2.0
    got = ld._preflight_estimates(n_var, 17.7, "medium", 18_197_067)["est_block_count"]
    assert got == exp


def test_over_threshold_boundary():
    # n_var > 75_000 is the trigger; exactly 75_000 is NOT over
    assert ld._preflight_estimates(75_000, 10.0, "medium", 10_000_000)["over_threshold"] is False
    assert ld._preflight_estimates(75_001, 10.0, "medium", 10_000_000)["over_threshold"] is True


def test_est_output_gib_full_triangle_when_radius_ge_span():
    # radius_bp >= span_bp -> band_frac == 1.0 -> full upper-triangle nnz
    n_var = 50_000
    span_mb = 17.7
    radius_bp = 18_197_067  # >= span
    full = 0.5 * (n_var ** 2) * 4.0 / 1e9
    got = ld._preflight_estimates(n_var, span_mb, "medium", radius_bp)["est_output_gib"]
    assert got == pytest.approx(full)


def test_est_output_gib_banded_fraction_when_radius_lt_span():
    # radius_bp < span_bp -> est scales by band_frac = radius/span
    n_var = 50_000
    span_mb = 20.0
    radius_bp = 10_000_000  # half the span
    band_frac = radius_bp / (span_mb * 1e6)
    exp = 0.5 * (n_var ** 2) * band_frac * 4.0 / 1e9
    got = ld._preflight_estimates(n_var, span_mb, "medium", radius_bp)["est_output_gib"]
    assert got == pytest.approx(exp)
    assert band_frac < 1.0  # sanity: this is genuinely a banded case


def test_zero_var_is_safe():
    est = ld._preflight_estimates(0, 10.0, "medium", 10_000_000)
    assert est["est_block_count"] == 0
    assert est["est_output_gib"] == 0
    assert est["over_threshold"] is False


# --------------------------------------------------------------------------- #
# write_preflight_counts — TSV driver (Hail count stubbed)
# --------------------------------------------------------------------------- #
def _row(region_id, ancestry, region_class, start, end, radius_bp, chrom="6"):
    return {
        "region_id": region_id, "ancestry": ancestry, "region_class": region_class,
        "chr": chrom, "start_grch38": start, "end_grch38": end, "radius_bp": radius_bp,
    }


def test_write_preflight_counts_columns_and_rows(tmp_path, monkeypatch):
    rows = [
        _row("m2_region_00006", "AFR", "medium", 104_045_894, 121_742_961, 18_197_067, chrom="1"),
        _row("m2_region_00143", "AFR", "large", 14_557_405, 58_453_775, 44_396_370),
        _row("m2_region_00143", "EUR", "large", 14_557_405, 58_453_775, 44_396_370),
    ]
    # stub the Hail count: return n_var keyed by region+ancestry
    counts = {("m2_region_00006", "AFR"): 122_678,
              ("m2_region_00143", "AFR"): 410_000,
              ("m2_region_00143", "EUR"): 380_000}
    monkeypatch.setattr(ld, "count_region_n_var",
                        lambda row, mt: counts[(row["region_id"], row["ancestry"])])
    out = tmp_path / "m3-W2-preflight-counts.tsv"
    res = ld.write_preflight_counts(rows, {"AFR": object(), "EUR": object()}, out)

    assert len(res) == 3
    with open(out) as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        assert reader.fieldnames == ld.PREFLIGHT_COUNT_COLUMNS
        recs = list(reader)
    assert len(recs) == 3
    # the 44 Mb MHC region (region_00143) must flag over_threshold
    mhc = [r for r in recs if r["region_id"] == "m2_region_00143" and r["ancestry"] == "AFR"][0]
    assert mhc["over_threshold"] == "True"
    assert int(mhc["n_var"]) == 410_000
    assert mhc["routed_path"] == "A.3"


def test_write_preflight_counts_missing_ancestry_raises(tmp_path, monkeypatch):
    rows = [_row("m2_region_00006", "AMR", "medium", 1, 1_000_000, 1_000_000)]
    monkeypatch.setattr(ld, "count_region_n_var", lambda row, mt: 100)
    out = tmp_path / "x.tsv"
    with pytest.raises(KeyError):
        ld.write_preflight_counts(rows, {"AFR": object(), "EUR": object()}, out)


def test_write_preflight_counts_window_span_from_grch38(tmp_path, monkeypatch):
    # window_span_mb must derive from (end_grch38 - start_grch38)
    rows = [_row("r", "AFR", "medium", 37_463_740, 57_333_291, 10_000_000, chrom="12")]
    monkeypatch.setattr(ld, "count_region_n_var", lambda row, mt: 60_000)
    out = tmp_path / "x.tsv"
    res = ld.write_preflight_counts(rows, {"AFR": object()}, out)
    assert res[0]["window_span_mb"] == pytest.approx((57_333_291 - 37_463_740) / 1e6, abs=1e-3)
