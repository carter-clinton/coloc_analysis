"""m3-02d Task 3 — redo_ld_cost_model.py unit tests.

The cost model extrapolates COMPLETING-cell blocks_per_min over REAL preflight
counts (EXCLUDING INTERRUPTED/NA rows), keeps three separate totals, computes
master-inclusive end-to-end cluster-hours, applies a contingency factor, projects
per-chrom egress bundles, and evaluates the EXACT projected*1.3<=budget_cap gate
with all four dispositions. Synthetic in-memory TSVs; no cluster, no AoU.
"""
import importlib
import sys
from pathlib import Path

import pandas as pd
import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

rlc = importlib.import_module("redo_ld_cost_model")

_PROBE_COLS = ["region_id", "ancestry", "region_class", "n_var", "block_count",
               "stage4_wall_min", "end_to_end_wall_min", "blocks_per_min",
               "peak_executor_mem_gib", "any_spill", "cluster_vcpu", "n_workers",
               "cluster_hours", "status"]


def _probe_row(region_id, anc, cls, n_var, block_count, s4, e2e, bpm, status,
               cluster_vcpu=384, n_workers=24, cluster_hours=10.0):
    return {
        "region_id": region_id, "ancestry": anc, "region_class": cls,
        "n_var": n_var, "block_count": block_count, "stage4_wall_min": s4,
        "end_to_end_wall_min": e2e, "blocks_per_min": bpm,
        "peak_executor_mem_gib": "30", "any_spill": "False",
        "cluster_vcpu": cluster_vcpu, "n_workers": n_workers,
        "cluster_hours": cluster_hours, "status": status,
    }


def _write_probe(tmp_path, rows):
    p = tmp_path / "probe.tsv"
    pd.DataFrame(rows, columns=_PROBE_COLS).to_csv(p, sep="\t", index=False)
    return p


def _write_preflight(tmp_path, rows):
    cols = ["region_id", "ancestry", "region_class", "window_span_mb", "n_var",
            "routed_path", "est_block_count", "est_output_gib", "over_threshold", "chr"]
    p = tmp_path / "preflight.tsv"
    pd.DataFrame(rows, columns=cols).to_csv(p, sep="\t", index=False)
    return p


def _pf_row(region_id, anc, cls, span, n_var, blocks, gib, chrom="12",
            routed="A.3", over=False):
    return {"region_id": region_id, "ancestry": anc, "region_class": cls,
            "window_span_mb": span, "n_var": n_var, "routed_path": routed,
            "est_block_count": blocks, "est_output_gib": gib,
            "over_threshold": over, "chr": chrom}


def _write_projection(tmp_path, parents_whole, parents_xlarge_with_subs):
    """parents_whole: list of region_id (whole). parents_xlarge_with_subs: dict
    {parent_id: n_sub}. Writes the projection split_status rows."""
    rows = []
    for rid in parents_whole:
        rows.append({"region_id": rid, "split_status": "whole", "n_subregions": 1,
                     "chr": "1"})
    for parent, n_sub in parents_xlarge_with_subs.items():
        rows.append({"region_id": parent, "split_status": "parent",
                     "n_subregions": n_sub, "chr": "12"})
        for k in range(n_sub):
            rows.append({"region_id": f"{parent}__sub{k:02d}",
                         "split_status": "subregion", "n_subregions": n_sub,
                         "chr": "12"})
    p = tmp_path / "projection.tsv"
    pd.DataFrame(rows).to_csv(p, sep="\t", index=False)
    return p


# --------------------------------------------------------------------------- #

def test_excludes_interrupted_rows(tmp_path):
    """A status=INTERRUPTED_write_bound / blocks_per_min=NA row is EXCLUDED from the
    rate basis (the exact prior-probe failure mode); a COMPLETED row contributes."""
    probe = _write_probe(tmp_path, [
        _probe_row("r_int", "EUR", "medium", 78730, 200, 16, 56, "NA",
                   "INTERRUPTED_write_bound"),
        _probe_row("r_afr", "AFR", "large", 80000, 109, 20, 40, 2.0, "COMPLETED"),
    ])
    pr = rlc.load_probe_rates(probe)
    assert ("AFR", "large") in pr["rates"]
    assert ("EUR", "medium") not in pr["rates"]  # interrupted -> excluded
    assert pr["rate_list"] == [2.0]
    # a COMPLETED row with NA rate is a data error (never treated as a rate).
    bad = _write_probe(tmp_path, [
        _probe_row("r_bad", "AFR", "large", 80000, 109, 20, 40, "NA", "COMPLETED"),
    ])
    with pytest.raises(ValueError):
        rlc.load_probe_rates(bad)
    # an all-interrupted probe yields no rate -> the model refuses to extrapolate.
    none_ok = _write_probe(tmp_path, [
        _probe_row("r_int", "EUR", "medium", 78730, 200, 16, 56, "NA",
                   "INTERRUPTED_write_bound"),
    ])
    with pytest.raises(ValueError):
        rlc.load_probe_rates(none_ok)


def test_real_count_extrapolation_not_span(tmp_path):
    """Per-cell cluster-h uses the PREFLIGHT block_count, not span. Two cells with
    the SAME span but different preflight block_count get different hours."""
    probe = _write_probe(tmp_path, [
        _probe_row("r_afr", "AFR", "large", 80000, 100, 20, 40, 2.0, "COMPLETED"),
    ])
    pr = rlc.load_probe_rates(probe)
    pf = rlc.load_preflight_counts(_write_preflight(tmp_path, [
        _pf_row("a__sub00", "AFR", "large", 11.0, 80000, 100.0, 7.0),
        _pf_row("a__sub01", "AFR", "large", 11.0, 80000, 400.0, 7.0),  # 4x blocks, same span
    ]))
    proj = rlc.project_cell_hours(pf, pr, eur_fac=3.0)
    h0 = proj[proj["region_id"] == "a__sub00"]["cluster_hours"].iloc[0]
    h1 = proj[proj["region_id"] == "a__sub01"]["cluster_hours"].iloc[0]
    assert h1 == pytest.approx(4.0 * h0)  # driven by block_count, not span


def test_master_inclusive_end_to_end_hours(tmp_path):
    """cluster_hours per cell = block_count/rate/60 * overhead * (n_workers + 1) — the
    +1 is the MASTER, and the overhead uses end_to_end (not stage4-only)."""
    probe = _write_probe(tmp_path, [
        _probe_row("r_afr", "AFR", "large", 80000, 100, 20, 40, 2.0, "COMPLETED",
                   cluster_vcpu=384),
    ])
    pr = rlc.load_probe_rates(probe)
    assert rlc.n_workers_plus_master(384) == 25  # 24 workers + 1 master
    assert pr["overhead_factor"] == pytest.approx(40 / 20)  # e2e/stage4 = 2.0
    pf = rlc.load_preflight_counts(_write_preflight(tmp_path, [
        _pf_row("a__sub00", "AFR", "large", 11.0, 80000, 120.0, 7.0),
    ]))
    proj = rlc.project_cell_hours(pf, pr, eur_fac=3.0)
    expected = (120.0 / 2.0 / 60.0) * 2.0 * 25  # write_node_h * overhead * (workers+1)
    assert proj["cluster_hours"].iloc[0] == pytest.approx(expected)
    # explicitly NOT n_workers alone (24) and NOT stage4-only overhead (1.0):
    not_master = (120.0 / 2.0 / 60.0) * 2.0 * 24
    assert proj["cluster_hours"].iloc[0] != pytest.approx(not_master)


def test_eur_factor_measured_then_fallback(tmp_path):
    """With completing AFR + EUR cells -> measured factor afr/eur; without an EUR
    completing cell -> 3.01 +/-20% fallback recorded as the source."""
    measured = rlc.load_probe_rates(_write_probe(tmp_path, [
        _probe_row("r_afr", "AFR", "large", 80000, 100, 20, 40, 2.0, "COMPLETED"),
        _probe_row("r_eur", "EUR", "large", 60000, 75, 30, 60, 1.0, "COMPLETED"),
    ]))
    fac, src = rlc.eur_factor(measured)
    assert fac == pytest.approx(2.0)  # afr 2.0 / eur 1.0
    assert src == "measured"
    afr_only = rlc.load_probe_rates(_write_probe(tmp_path, [
        _probe_row("r_afr", "AFR", "large", 80000, 100, 20, 40, 2.0, "COMPLETED"),
    ]))
    fac2, src2 = rlc.eur_factor(afr_only)
    assert fac2 == pytest.approx(rlc.EUR_FACTOR_FALLBACK)
    assert "assumed" in src2.lower()


def test_three_separate_totals(tmp_path):
    """(a) 322 logical parents, (b) > 322 compute cells, (c) parent aggregate ==
    Sigma over its subregion rows grouped by parent_region_id."""
    probe = rlc.load_probe_rates(_write_probe(tmp_path, [
        _probe_row("r_afr", "AFR", "large", 80000, 100, 20, 40, 2.0, "COMPLETED"),
    ]))
    # 160 whole logical regions + 1 xlarge parent with 3 subs = 161 logical units.
    # x 2 ancestries = 322 logical panels. compute cells = 160*2 + 3*2 = 326 > 322.
    whole = [f"m2_region_{i:05d}" for i in range(160)]
    proj_tsv = _write_projection(tmp_path, whole, {"m2_region_99999": 3})
    pf_rows = []
    for rid in whole:
        for anc in ("AFR", "EUR"):
            pf_rows.append(_pf_row(rid, anc, "small", 3.0, 5000, 5.0, 0.2, chrom="1"))
    for k in range(3):
        for anc in ("AFR", "EUR"):
            pf_rows.append(_pf_row(f"m2_region_99999__sub{k:02d}", anc, "large",
                                   11.0, 80000, 100.0, 7.0, chrom="12"))
    pf = rlc.load_preflight_counts(_write_preflight(tmp_path, pf_rows))
    projected = rlc.project_cell_hours(pf, probe, eur_fac=3.0)
    projection_df = pd.read_csv(proj_tsv, sep="\t")
    totals = rlc.three_totals(projected, projection_df)
    assert totals["n_logical_parents"] == 322
    assert totals["n_compute_cells"] == 326
    assert totals["n_compute_cells"] > 322
    # parent aggregate: the xlarge parent == sum over its 6 sub rows (3 sub x 2 anc).
    sub_rows = projected[projected["parent_region_id"] == "m2_region_99999"]
    assert totals["parent_aggregate"]["m2_region_99999"] == pytest.approx(
        sub_rows["cluster_hours"].sum())
    assert len(sub_rows) == 6


def test_contingency_factor_from_variance(tmp_path):
    """A contingency factor from the probe blocks_per_min CoV is applied; the
    contingency-adjusted total >= raw, and the factor is floored at 1.15."""
    probe = rlc.load_probe_rates(_write_probe(tmp_path, [
        _probe_row("r_a", "AFR", "large", 80000, 100, 20, 40, 2.0, "COMPLETED"),
        _probe_row("r_b", "AFR", "large", 80000, 100, 20, 40, 4.0, "COMPLETED"),
    ]))
    total_with, factor = rlc.apply_contingency(1000.0, probe["rate_list"])
    assert factor >= rlc.CONTINGENCY_FLOOR
    assert total_with >= 1000.0
    assert total_with == pytest.approx(1000.0 * factor)
    # a single-sample probe -> CoV undefined -> floor applies.
    _, floor_factor = rlc.apply_contingency(1000.0, [2.0])
    assert floor_factor == pytest.approx(rlc.CONTINGENCY_FLOOR)


def test_egress_bundle_projection(tmp_path):
    """The model projects per-chrom egress bundles via ld_egress_bundle and flags
    them vs EGRESS_CAP_GB=50."""
    pf = rlc.load_preflight_counts(_write_preflight(tmp_path, [
        _pf_row("a__sub00", "AFR", "large", 11.0, 80000, 100.0, 30.0, chrom="1"),
        _pf_row("a__sub01", "AFR", "large", 11.0, 80000, 100.0, 30.0, chrom="1"),
        _pf_row("b", "AFR", "small", 3.0, 5000, 5.0, 5.0, chrom="2"),
    ]))
    eg = rlc.project_egress_bundles(pf)
    assert eg["egress_cap_gb"] == 50
    assert eg["total_output_gib"] == pytest.approx(65.0)
    # chr1 (60 GiB) > 50 -> split into _a/_b
    assert "1" in eg["chromosomes_split"]
    assert "2" not in eg["chromosomes_split"]


def test_gate_predicate_green(tmp_path):
    """PROJECTED * 1.3 <= BUDGET_CAP -> GREEN (the exact predicate)."""
    gate = rlc.evaluate_gate(700.0, 1000.0)  # 700*1.3 = 910 <= 1000
    assert gate["headroom_ok"] is True
    assert gate["disposition"] == "GREEN"
    assert gate["projected_x_headroom"] == pytest.approx(910.0)
    assert gate["headroom_multiplier"] == 1.3


def test_gate_predicate_red_and_levers(tmp_path):
    """PROJECTED * 1.3 > BUDGET_CAP -> a non-GREEN disposition; the lever depends on
    band room (narrow-radius) / a dominant class (finer-split) / none (RED)."""
    # 900*1.3 = 1170 > 1000 -> not GREEN.
    base = rlc.evaluate_gate(900.0, 1000.0)
    assert base["headroom_ok"] is False
    assert base["disposition"] in {"YELLOW-narrow-radius", "YELLOW-finer-split", "RED"}
    # band room (buffer 15 Mb > Pan-UKBB 10) -> narrow-radius lever.
    narrow = rlc.evaluate_gate(900.0, 1000.0, lever_room_radius_mb=15.0)
    assert narrow["disposition"] == "YELLOW-narrow-radius"
    # buffer already narrow (3 Mb < 10) but a class dominates -> finer-split lever.
    finer = rlc.evaluate_gate(900.0, 1000.0, lever_room_radius_mb=3.0,
                              dominant_class="AFR/large")
    assert finer["disposition"] == "YELLOW-finer-split"
    # no lever room at all -> RED.
    red = rlc.evaluate_gate(900.0, 1000.0, lever_room_radius_mb=3.0,
                            dominant_class=None)
    assert red["disposition"] == "RED"


def test_no_hardcoded_paths():
    """REQ-PATH-PARAMETERIZATION: the model source carries no absolute HPC paths."""
    src = (SRC / "redo_ld_cost_model.py").read_text()
    for forbidden in ("/share/clintonlab", "/rs1/researchers", "/gpfs_common"):
        assert forbidden not in src
