"""Negative controls for fire_verifier — every check PROVEN able to fail before trusted.

Each check gets BOTH a green case and a red case. A check that has only ever been observed
green is not evidence. Also asserts FAIL-CLOSED behaviour: missing/unreadable input FAILS.

Run: PYTHONPATH=. python3 test_fire_verifier.py
"""
import os, tempfile
import fire_verifier as fv


def _tmp(content: str, suffix=".tsv") -> str:
    fd, p = tempfile.mkstemp(suffix=suffix); os.close(fd)
    with open(p, "w") as fh: fh.write(content)
    return p


# ---------------- Stage A: NaN falsification ----------------

def test_nan_falsification_green():
    p = _tmp("x" * 1024, ".npz")
    c = fv.check_nan_falsification(p, reader=lambda _: None)
    assert c.ok, c.detail

def test_nan_falsification_RED_still_raises():
    p = _tmp("x" * 1024, ".npz")
    def raiser(_): raise ValueError("NaN at (10327,10328)")
    c = fv.check_nan_falsification(p, reader=raiser)
    assert not c.ok and c.severity == fv.HARD_STOP
    assert "NOT the sole NaN mechanism" in c.detail

def test_nan_falsification_RED_missing_panel_fails_closed():
    c = fv.check_nan_falsification("/nonexistent/panel.npz", reader=lambda _: None)
    assert not c.ok, "missing panel must FAIL, never pass"

def test_nan_falsification_RED_empty_panel():
    p = _tmp("", ".npz")
    c = fv.check_nan_falsification(p, reader=lambda _: None)
    assert not c.ok and "empty/truncated" in c.detail

def test_nan_falsification_RED_reader_explodes_fails_closed():
    # a reader that fails for a NON-NaN reason must still FAIL, not pass
    p = _tmp("x" * 1024, ".npz")
    def broken(_): raise OSError("disk gone")
    c = fv.check_nan_falsification(p, reader=broken)
    assert not c.ok


# ---------------- Stage A: manifest ground truth ----------------

_GOOD_MANIFEST = ("occluded_variant_id\tchrom\tpos_grch38\n"
                  "chr1:1980475:G:A\t1\t1980475\n"
                  "chr1:5733487:G:A\t1\t5733487\n"
                  "chr1:5922718:G:A\t1\t5922718\n"
                  "chr1:7492693:G:A\t1\t7492693\n"
                  "chr1:8375822:G:A\t1\t8375822\n")

def test_manifest_green():
    assert fv.check_manifest_rows(_tmp(_GOOD_MANIFEST)).ok

def test_manifest_RED_wrong_count():
    short = "\n".join(_GOOD_MANIFEST.splitlines()[:4]) + "\n"
    c = fv.check_manifest_rows(_tmp(short))
    assert not c.ok and "expected 6" in c.detail

def test_manifest_RED_missing_file_fails_closed():
    assert not fv.check_manifest_rows("/nonexistent/m.tsv").ok

def test_manifest_RED_marker_content_not_records():
    # the _SUCCESS-marker class: file exists, right line count, but not real records
    marker = "header\n_SUCCESS\n_SUCCESS\n_SUCCESS\n_SUCCESS\n_SUCCESS\n"
    c = fv.check_manifest_rows(_tmp(marker))
    assert not c.ok and "placeholder/marker" in c.detail


# ---------------- ceiling ----------------

def test_ceiling_green_region1():
    c = fv.check_occlusion_ceiling(n_occluded=5, n_var=102421)
    assert c.ok and abs(c.measured["ceiling"] - 51.2105) < 1e-3

def test_ceiling_RED_exceeded():
    c = fv.check_occlusion_ceiling(n_occluded=52, n_var=102421)
    assert not c.ok and "DEFER" in c.detail

def test_ceiling_boundary_equal_passes():
    # pre-registered wording is "exceeds" -> strict >; count == ceiling PASSES
    assert fv.check_occlusion_ceiling(n_occluded=60, n_var=120000).ok
    assert not fv.check_occlusion_ceiling(n_occluded=61, n_var=120000).ok


# ---------------- region-1 deferral is a finding ----------------

def test_region1_status_green():
    assert fv.check_region1_not_deferred("ok").ok

def test_region1_RED_deferred_is_finding():
    c = fv.check_region1_not_deferred("deferred_infeasible_square")
    assert not c.ok and c.severity == fv.FINDING and "not a retry" in c.detail


# ---------------- Stage B ----------------

def test_peak_ram_green():
    assert fv.check_peak_ram(78.2).ok

def test_peak_ram_RED_over_limit():
    assert not fv.check_peak_ram(110.0).ok

def test_peak_ram_RED_unreported_fails_closed():
    c = fv.check_peak_ram(None)
    assert not c.ok and "FAIL CLOSED" in c.detail

def test_maf_depression_green():
    pairs = [{"panel_maf": 0.0078, "sumstats_maf": 0.014}] * 4 + \
            [{"panel_maf": 0.02, "sumstats_maf": 0.019}]
    assert fv.check_maf_depression(pairs).ok

def test_maf_depression_RED_no_systematic_depression():
    pairs = [{"panel_maf": 0.02, "sumstats_maf": 0.014}] * 4 + \
            [{"panel_maf": 0.007, "sumstats_maf": 0.014}]
    c = fv.check_maf_depression(pairs)
    assert not c.ok and c.severity == fv.FINDING and "WEAKENS" in c.detail

def test_maf_depression_RED_empty_fails_closed():
    assert not fv.check_maf_depression([]).ok


# ---------------- cost denominator ----------------

def test_cost_green():
    assert fv.check_cost_denominator(n_regions_used=247, n_bankable=247).ok

def test_cost_RED_uses_276():
    c = fv.check_cost_denominator(n_regions_used=276, n_bankable=247)
    assert not c.ok and "understates" in c.detail


# ---------------- deferral classification ----------------

def test_deferrals_green_recognized():
    rows = [{"status": "ok"}] * 5 + [{"status": "deferred_infeasible_square"}] * 29
    c = fv.classify_deferrals(rows)
    assert c.ok and c.measured["counts"]["deferred_infeasible_square"] == 29

def test_deferrals_RED_unknown_status():
    c = fv.classify_deferrals([{"status": "deferred_mystery_reason"}])
    assert not c.ok and "unrecognized" in c.detail

def test_deferrals_RED_empty_status():
    c = fv.classify_deferrals([{"status": ""}])
    assert not c.ok


# ---------------- publication disclosure gate ----------------

def test_disclosure_RED_while_estimates_remain():
    txt = "Approximately ~29 regions (10.5%) were not converted (ESTIMATE, pending fire)."
    c = fv.check_coverage_disclosure_resolved(txt)
    assert not c.ok and "estimate marker" in c.detail

def test_disclosure_green_with_measured_numbers():
    txt = ("31 regions exceeding n_var 120000 were not converted in square mode; "
           "affected span 412.7 Mb (measured from panel TSV deferred rows).")
    assert fv.check_coverage_disclosure_resolved(txt).ok

def test_disclosure_RED_empty_fails_closed():
    assert not fv.check_coverage_disclosure_resolved("").ok


# ---------------- summarize / exit code ----------------

def test_summarize_exit_codes():
    good = [fv.check_occlusion_ceiling(5, 102421)]
    bad = good + [fv.check_occlusion_ceiling(52, 102421)]
    assert fv.summarize(good)["exit_code"] == 0
    s = fv.summarize(bad)
    assert s["exit_code"] == 1 and "occlusion_anomaly_ceiling" in s["hard_stops"]


if __name__ == "__main__":
    import sys
    fns = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    reds = [k for k, _ in fns if "_RED_" in k or "_RED" in k]
    fails = 0
    for k, fn in fns:
        try:
            fn(); print(f"PASS  {k}")
        except AssertionError as e:
            fails += 1; print(f"FAIL  {k}: {e}")
    print(f"\n{len(fns)-fails}/{len(fns)} passed  ({len(reds)} of them are NEGATIVE CONTROLS "
          f"proving a check can fail)")
    sys.exit(1 if fails else 0)
