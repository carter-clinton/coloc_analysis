"""Fire-stage invariant verifier — mechanical gates for the AFR LD panel fire.

Purpose: convert the pre-fire checklist from HUMAN VIGILANCE into EXECUTABLE GATES that
exit non-zero. A check a human has to remember is a check that fails at region 180 at 3am.

DESIGN RULE 1 — FAIL CLOSED. Every check returns FAIL on missing input, unreadable input,
unparseable input, or an internal exception. A verifier that cannot measure must never pass.
This is the `_SUCCESS`-marker lesson in code: absence of evidence is FAIL, not PASS.

DESIGN RULE 2 — MEASURE THE DATA LAYER, NEVER A MARKER. Row counts come from reading rows.
Panel validity comes from re-reading the panel. A status string saying "ok" is corroboration,
never the measurement.

DESIGN RULE 3 — EVERY CHECK MUST BE PROVEN ABLE TO FAIL before it is trusted (see
test_fire_verifier.py negative controls). A green that has never been observed red is not a
result.

EGRESS: emits only counts, booleans, and policy labels. No genotypes, no LD values, no
per-sample data. Safe to run in-perimeter and report out.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
import os

HARD_STOP = "HARD_STOP"      # firing further would bank defective/unexplained output
FINDING   = "FINDING"        # scientifically meaningful; requires a human decision
WARN      = "WARN"           # note it, does not stop the fire
PASS      = "PASS"


@dataclass
class Check:
    name: str
    status: str
    detail: str
    severity: str = HARD_STOP        # severity IF failed
    measured: Dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == PASS


def _guard(name: str, severity: str, fn: Callable[[], Check]) -> Check:
    """Fail-closed wrapper: any exception becomes a FAIL, never a silent pass."""
    try:
        return fn()
    except Exception as e:                                  # noqa: BLE001
        return Check(name, "FAIL", f"check could not be evaluated ({type(e).__name__}: {e}) "
                                   f"-> FAIL CLOSED (unmeasurable != ok)", severity)


# --------------------------------------------------------------------------- #
# STAGE A — mechanism falsification. The scientific gate, not a smoke test.    #
# --------------------------------------------------------------------------- #

def check_nan_falsification(npz_path: str, reader, min_bytes: int = 256) -> Check:
    """The filtered region-1 panel must contain ZERO NaN.

    `reader` is the FROZEN plink_ld_to_npz.read_square_bin-equivalent: it RAISES on any NaN.
    We call it ourselves rather than trusting a status string — an independent re-read is the
    falsification. Raises nothing => occlusion accounted for 100% of region-1 NaN.
    Raises => occlusion is NOT the sole NaN mechanism => HARD STOP.
    """
    def run() -> Check:
        n = "stage_a_nan_falsification"
        if not os.path.exists(npz_path):
            return Check(n, "FAIL", f"banked panel absent: {npz_path} -> cannot falsify", HARD_STOP)
        size = os.path.getsize(npz_path)
        if size < min_bytes:
            return Check(n, "FAIL", f"panel is {size} B (< {min_bytes}) -> empty/truncated bank",
                         HARD_STOP, {"bytes": size})
        try:
            reader(npz_path)
        except Exception as e:                              # noqa: BLE001
            return Check(n, "FAIL",
                         f"panel STILL RAISES after occlusion filtering ({type(e).__name__}). "
                         f"Occlusion is NOT the sole NaN mechanism -> HARD STOP: do not fire "
                         f"the remaining regions; an unexplained defect class would be banked.",
                         HARD_STOP, {"bytes": size, "raised": type(e).__name__})
        return Check(n, PASS, "filtered panel re-read raises nothing: occlusion accounted for "
                              "100% of region-1 NaN (mechanism confirmed by construction)",
                     HARD_STOP, {"bytes": size})
    return _guard("stage_a_nan_falsification", HARD_STOP, run)


def check_manifest_rows(manifest_path: str, expected_records: int = 5,
                        expect_header: bool = True) -> Check:
    """Region-1 manifest ground truth: real row count + content, never an upload marker.

    Region 1 is the ONLY region with a known answer, so it is the one chance to validate the
    manifest writer against ground truth.
    """
    def run() -> Check:
        n = "stage_a_manifest_rows"
        if not os.path.exists(manifest_path):
            return Check(n, "FAIL", f"manifest absent: {manifest_path}", HARD_STOP)
        with open(manifest_path) as fh:
            lines = [l for l in fh.read().splitlines() if l.strip() != ""]
        want = expected_records + (1 if expect_header else 0)
        if len(lines) != want:
            return Check(n, "FAIL",
                         f"manifest has {len(lines)} non-empty lines, expected {want} "
                         f"(header + {expected_records} records)", HARD_STOP,
                         {"lines": len(lines), "expected": want})
        body = lines[1:] if expect_header else lines
        if any(len(r.split("\t")) < 2 for r in body):
            return Check(n, "FAIL", "manifest rows are not parseable as multi-field records "
                                    "-> writer emitted placeholder/marker content", HARD_STOP)
        return Check(n, PASS, f"manifest carries {len(body)} real records (+header), "
                              f"fields parseable", HARD_STOP,
                     {"records": len(body)})
    return _guard("stage_a_manifest_rows", HARD_STOP, run)


def check_occlusion_ceiling(n_occluded: int, n_var: int, frac: float = 0.0005) -> Check:
    """Pre-registered clause (d): defer when occluded count STRICTLY EXCEEDS frac * n_var."""
    def run() -> Check:
        n = "occlusion_anomaly_ceiling"
        ceiling = frac * n_var
        if n_occluded > ceiling:
            return Check(n, "FAIL",
                         f"n_occluded={n_occluded} > ceiling={ceiling:.1f} ({frac:g} x n_var="
                         f"{n_var}) -> region must DEFER (deferred_occlusion_anomaly), never "
                         f"auto-exclude; disclose as a deviation", HARD_STOP,
                         {"n_occluded": n_occluded, "ceiling": ceiling, "n_var": n_var})
        return Check(n, PASS, f"n_occluded={n_occluded} <= ceiling={ceiling:.1f} "
                              f"({ceiling/max(n_occluded,1):.0f}x headroom)", HARD_STOP,
                     {"n_occluded": n_occluded, "ceiling": ceiling, "n_var": n_var})
    return _guard("occlusion_anomaly_ceiling", HARD_STOP, run)


def check_region1_not_deferred(status: str) -> Check:
    """A deferral AT REGION 1 is itself the finding — region 1 is the known-answer region."""
    def run() -> Check:
        n = "region1_not_deferred"
        if status.strip().lower().startswith("deferred"):
            return Check(n, "FAIL",
                         f"region 1 returned status={status!r}. Region 1 is the known-answer "
                         f"region (5 occluded, 51 ceiling, 10x headroom) — a deferral here "
                         f"means the gate or the substrate disagrees with ground truth. "
                         f"This is a FINDING requiring diagnosis, not a retry.", FINDING,
                         {"status": status})
        return Check(n, PASS, f"region 1 status={status!r} (not deferred)", FINDING,
                     {"status": status})
    return _guard("region1_not_deferred", FINDING, run)


# --------------------------------------------------------------------------- #
# STAGE B — scaling + mechanism-consistency in aggregate                      #
# --------------------------------------------------------------------------- #

def check_peak_ram(peak_gib: Optional[float], vm_gib: float = 120.0,
                   headroom_frac: float = 0.15) -> Check:
    """Peak RSS must leave headroom on the VM; a missing measurement FAILS closed."""
    def run() -> Check:
        n = "stage_b_peak_ram"
        if peak_gib is None:
            return Check(n, "FAIL", "peak_ram_gib not reported -> unmeasurable, FAIL CLOSED "
                                    "(the producer must emit it per region)", HARD_STOP)
        limit = vm_gib * (1.0 - headroom_frac)
        if peak_gib > limit:
            return Check(n, "FAIL", f"peak {peak_gib:.1f} GiB > {limit:.1f} GiB "
                                    f"({headroom_frac:.0%} headroom on {vm_gib:.0f} GiB) -> "
                                    f"do not extrapolate to larger regions", HARD_STOP,
                         {"peak_gib": peak_gib, "limit_gib": limit})
        return Check(n, PASS, f"peak {peak_gib:.1f} GiB within {limit:.1f} GiB", HARD_STOP,
                     {"peak_gib": peak_gib, "limit_gib": limit})
    return _guard("stage_b_peak_ram", HARD_STOP, run)


def check_maf_depression(pairs: List[Dict[str, float]], min_frac: float = 0.5) -> Check:
    """Occluded variants should show DEPRESSED panel MAF vs sumstats MAF.

    Direction check only — the GWAS AFR cohort is not the AoU AFR cohort, so the exact ratio
    is confounded. Absence of systematic depression WEAKENS the mechanism attribution: that is
    a FINDING for a human, not a hard stop.
    """
    def run() -> Check:
        n = "stage_b_maf_depression"
        if not pairs:
            return Check(n, "FAIL", "no (panel_maf, sumstats_maf) pairs supplied -> "
                                    "unmeasurable, FAIL CLOSED", FINDING)
        usable = [p for p in pairs
                  if p.get("panel_maf") is not None and p.get("sumstats_maf") is not None]
        if not usable:
            return Check(n, "FAIL", "no usable pairs (all missing a side)", FINDING)
        depressed = sum(1 for p in usable if p["panel_maf"] < p["sumstats_maf"])
        frac = depressed / len(usable)
        if frac < min_frac:
            return Check(n, "FAIL",
                         f"only {depressed}/{len(usable)} ({frac:.0%}) of occluded variants show "
                         f"depressed panel MAF (threshold {min_frac:.0%}). The occlusion "
                         f"mechanism predicts systematic depression; its absence WEAKENS the "
                         f"attribution -> FINDING for human review (direction check only; "
                         f"cohort differences confound the magnitude).", FINDING,
                         {"depressed": depressed, "n": len(usable), "frac": frac})
        return Check(n, PASS, f"{depressed}/{len(usable)} ({frac:.0%}) depressed — direction "
                              f"consistent with occlusion", FINDING,
                     {"depressed": depressed, "n": len(usable), "frac": frac})
    return _guard("stage_b_maf_depression", FINDING, run)


# --------------------------------------------------------------------------- #
# COST GATE — denominator discipline                                          #
# --------------------------------------------------------------------------- #

def check_cost_denominator(n_regions_used: int, n_bankable: int, n_total: int = 276) -> Check:
    """Cost must be computed per BANKABLE region, never per region-of-276."""
    def run() -> Check:
        n = "cost_gate_denominator"
        if n_regions_used == n_total and n_bankable != n_total:
            return Check(n, "FAIL",
                         f"cost denominator is {n_total} (all regions) but only {n_bankable} are "
                         f"bankable -> understates per-region cost by "
                         f"{n_total/max(n_bankable,1):.2f}x. Use cost-per-BANKABLE-region.",
                         HARD_STOP, {"used": n_regions_used, "bankable": n_bankable})
        if n_regions_used != n_bankable:
            return Check(n, "FAIL", f"cost denominator {n_regions_used} != bankable {n_bankable}",
                         HARD_STOP, {"used": n_regions_used, "bankable": n_bankable})
        return Check(n, PASS, f"cost computed on {n_bankable} bankable regions", HARD_STOP,
                     {"bankable": n_bankable})
    return _guard("cost_gate_denominator", HARD_STOP, run)


# --------------------------------------------------------------------------- #
# DEFERRALS ARE EXPECTED STATES, NOT FAILURES                                 #
# --------------------------------------------------------------------------- #

_EXPECTED_DEFERRALS = ("deferred_infeasible_square", "deferred_occlusion_anomaly")


def classify_deferrals(status_rows: List[Dict[str, Any]]) -> Check:
    """Deferred rows are the GATES WORKING. Only UNRECOGNIZED statuses are failures.

    Guards against the mid-fire temptation to 'fix' a deferral, and against an unknown
    status string being silently treated as ok.
    """
    def run() -> Check:
        n = "deferral_classification"
        counts: Dict[str, int] = {}
        unknown: List[str] = []
        for r in status_rows:
            s = str(r.get("status", "")).strip()
            counts[s] = counts.get(s, 0) + 1
            if s.startswith("deferred") and s not in _EXPECTED_DEFERRALS:
                unknown.append(s)
            if s == "":
                unknown.append("<empty status>")
        if unknown:
            return Check(n, "FAIL", f"unrecognized status value(s) {sorted(set(unknown))} -> "
                                    f"an unknown status must never be treated as ok", HARD_STOP,
                         {"counts": counts})
        deferred = sum(v for k, v in counts.items() if k.startswith("deferred"))
        return Check(n, PASS, f"{deferred} deferred row(s), all recognized "
                              f"(gates working; do NOT 'fix' mid-fire)", WARN, {"counts": counts})
    return _guard("deferral_classification", HARD_STOP, run)


# --------------------------------------------------------------------------- #
# PUBLICATION GATE — the disclosure obligation cannot lapse silently          #
# --------------------------------------------------------------------------- #

def check_coverage_disclosure_resolved(disclosure_text: str,
                                       estimate_markers: tuple = ("ESTIMATE", "estimate",
                                                                  "~29", "10.5%")) -> Check:
    """R4-COVERAGE: the coverage-gap disclosure must carry MEASURED post-fire numbers.

    Fails while Seth's estimates are still in place. This is what stops the obligation from
    lapsing quietly between the fire and submission — it belongs in the test suite so it is
    RED until real numbers land.
    """
    def run() -> Check:
        n = "publication_coverage_disclosure"
        if not disclosure_text.strip():
            return Check(n, "FAIL", "no coverage disclosure text present -> obligation "
                                    "R4-COVERAGE unmet", HARD_STOP)
        found = [m for m in estimate_markers if m in disclosure_text]
        if found:
            return Check(n, "FAIL",
                         f"disclosure still carries estimate marker(s) {found} -> replace with "
                         f"MEASURED deferred_infeasible_square counts + affected span before "
                         f"publication", HARD_STOP, {"markers": found})
        return Check(n, PASS, "disclosure carries measured values (no estimate markers)",
                     HARD_STOP)
    return _guard("publication_coverage_disclosure", HARD_STOP, run)


# --------------------------------------------------------------------------- #
# Driver                                                                      #
# --------------------------------------------------------------------------- #

def summarize(checks: List[Check]) -> Dict[str, Any]:
    failed = [c for c in checks if not c.ok]
    hard = [c for c in failed if c.severity == HARD_STOP]
    finds = [c for c in failed if c.severity == FINDING]
    return {
        "all_pass": not failed,
        "exit_code": 0 if not failed else 1,
        "n_checks": len(checks),
        "hard_stops": [c.name for c in hard],
        "findings": [c.name for c in finds],
        "report": [{"name": c.name, "status": c.status, "severity": c.severity,
                    "detail": c.detail, "measured": c.measured} for c in checks],
    }
