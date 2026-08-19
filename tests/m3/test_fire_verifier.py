"""Contracts + negative controls for ``src/python/fire_verifier.py``.

``fire_verifier`` is the MECHANICAL GATE library for the AFR LD-panel fire: a
single command run on the AoU VM after ``git pull`` that evaluates the Stage-A /
Stage-B / Stage-C invariants and exits non-zero if any of them is red. It never
makes the go/no-go decision; it makes the EVIDENCE for that decision mechanical
and fail-closed.

WHAT RUNS WHERE. Everything in this module runs locally in ``smoke_dev`` (py3.11,
numpy + pandas). Nothing here touches the AoU perimeter, the bucket, the network,
or plink. Every ``.npz`` fixture is tiny (n <= 64): the memory discipline of the
real gate is enforced BY CONSTRUCTION (it calls the FROZEN blocked helpers in
``plink_ld_to_npz``), never by allocating a real ~42 GB region-1 matrix here.

WHY EVERY CHECK HAS A ``_RED_`` TEST. A green that has never been observed red is
not a result. Each ``_RED_``-named test is a negative control for one defect class
this project has actually hit: marker-not-data, unmeasured-treated-as-ok, wrong
denominator, unknown-status-as-ok, estimate-shipped-as-measurement, and a
misattributed NaN reported as an asymmetry. The verbatim red output of each is
banked in
``.planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-controls-transcript.txt``.

THE DRIFT ENFORCER. ``test_shipped_status_vocabulary_is_covered`` walks the SHIPPED
``run_native_ld_panel.py`` with ``ast`` and extracts the constant prefix of every
value ever assigned to ``result["status"]`` (or written as a ``"status":`` dict
entry). A status added to the producer tomorrow makes this module RED rather than
being silently classified as unknown mid-fire. It is proven non-vacuous two ways:
the extracted set must be NON-EMPTY, and ``test_RED_status_vocabulary_guard_...``
runs the SAME extractor over a fixture module carrying ``"banana"`` and asserts the
coverage assertion fails for it.

THE R4-COVERAGE OBLIGATION. ``test_coverage_disclosure_live_gate_...`` SKIPS while
no measured panel TSV exists in-repo, which is why this module contributes exactly
one skip to the tests/m3 baseline (31 -> 32). That skip IS the named enforcer of
the R4-COVERAGE disclosure obligation: the moment a measured panel TSV lands in the
repo the gate stops skipping and goes red until the disclosure carries measured
numbers plus a ``MEASURED:`` provenance line. The skip is guarded against masking
three ways (the check function's own green/red run unconditionally against
fixtures; the finder itself is shown valid on a tmp tree with and without the file;
the skip-count move is recorded in the SUMMARY).
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import aou_ld_panel as alp        # noqa: E402  (MED-6 byte floor)
import fire_verifier as fv        # noqa: E402  (the module under test)
import plink_ld_to_npz as pln     # noqa: E402  (FROZEN blocked helpers)
import run_native_ld_panel as rnlp  # noqa: E402  (the shipped producer)


# --------------------------------------------------------------------------- #
# Fixture builders                                                            #
# --------------------------------------------------------------------------- #

#: A REAL detail-bearing deferral, byte-shaped like the producer emits it
#: (``run_native_ld_panel.py:831``). The prototype this module supersedes would
#: have classified this as UNRECOGNIZED -> HARD_STOP on the gates working.
REAL_INFEASIBLE = "deferred_infeasible_square: n_var=102421 > ceiling=120000"
#: ``run_native_ld_panel.py:854``
REAL_OCCLUSION_ANOMALY = "deferred_occlusion_anomaly: 812 occluded of 102421 (ceiling 51)"
#: ``run_native_ld_panel.py:1028``
REAL_ERROR = "error: n_var mismatch for m2_region_00001: 102421 != 102420"


def _panel_row(region_id: str, chrom=1, n_var=None, wall_min=None, peak_ram_gib=None,
               output_gib=None, status="ok", n_dropped_occluded=None,
               n_dropped_monomorphic=None) -> str:
    """One panel-TSV data line in ``_PANEL_COLUMNS`` order (None -> empty field,
    exactly as ``pandas.to_csv`` renders it)."""
    values = {
        "region_id": region_id, "chr": chrom, "n_var": n_var, "wall_min": wall_min,
        "peak_ram_gib": peak_ram_gib, "output_gib": output_gib, "status": status,
        "n_dropped_occluded": n_dropped_occluded,
        "n_dropped_monomorphic": n_dropped_monomorphic,
    }
    return "\t".join("" if values[c] is None else str(values[c])
                     for c in rnlp._PANEL_COLUMNS)


def _write_panel(tmp_path: Path, rows, name="panel_fixture.tsv",
                 header=None) -> Path:
    hdr = "\t".join(rnlp._PANEL_COLUMNS) if header is None else header
    p = tmp_path / name
    p.write_text(hdr + "\n" + ("\n".join(rows) + "\n" if rows else ""))
    return p


def _region1_panel(tmp_path: Path, **kw) -> Path:
    """The Stage-A panel: region 1 computed ok, 5 occluded of 102,421."""
    row = _panel_row("m2_region_00001", chrom=1, n_var=102421, wall_min=41.3,
                     peak_ram_gib=78.2, output_gib=39.1, status="ok",
                     n_dropped_occluded=5, n_dropped_monomorphic=0)
    return _write_panel(tmp_path, [row], **kw)


def _symmetric_unit_diag(n: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    a = rng.standard_normal((n, n)).astype("float32")
    m = ((a + a.T) / 2.0).astype("float32")
    np.fill_diagonal(m, 1.0)
    return m


def _write_npz(path: Path, ld: np.ndarray) -> Path:
    """Write a region ``.npz`` the way the SHIPPED converter writes one
    (``plink_ld_to_npz.py:340`` ``np.savez_compressed``)."""
    n = ld.shape[0]
    np.savez_compressed(
        str(path),
        ld=ld.astype("float32", copy=False),
        variant_ids=np.array([f"chr1:{1000 + i}:A:T" for i in range(n)]),
        rsids=np.array([f"rs{i}" for i in range(n)]),
        allele_freq=np.full(n, 0.2, dtype="float32"),
        lower_triangular=np.array([False]),
    )
    return path


def _good_npz(tmp_path: Path, n: int = 64) -> Path:
    return _write_npz(tmp_path / "good.npz", _symmetric_unit_diag(n))


def _nan_diagonal_npz(tmp_path: Path, n: int = 64) -> Path:
    m = _symmetric_unit_diag(n)
    m[3, 3] = np.nan
    return _write_npz(tmp_path / "nan_diag.npz", m)


def _whole_row_nan_npz(tmp_path: Path, n: int = 64, row: int = 7) -> Path:
    """The fire-#3 fingerprint: a zero-variance variant NaNs its whole row AND
    column while the diagonal stays 1.0, so the shipped verifier reports it as an
    ASYMMETRY rather than as a NaN."""
    m = _symmetric_unit_diag(n)
    m[row, :] = np.nan
    m[:, row] = np.nan
    m[row, row] = np.float32(1.0)
    return _write_npz(tmp_path / "row_nan.npz", m)


_MANIFEST_HEADER = "\t".join(
    ["region_id", "chr", "variant_id", "pos_grch38", "ref", "alt"])


def _manifest(tmp_path: Path, n_records=5, region_id="m2_region_00001",
              name="occlusion_manifest.tsv") -> Path:
    lines = [_MANIFEST_HEADER]
    for i in range(n_records):
        lines.append("\t".join([region_id, "1", f"chr1:{1980475 + i}:G:A",
                                str(1980475 + i), "G", "A"]))
    p = tmp_path / name
    p.write_text("\n".join(lines) + "\n")
    return p


_GOOD_DISCLOSURE = """## R4-COVERAGE — the square-mode deferral set is an ancestry-specific COVERAGE GAP

**Logged:** 2026-08-14. **Status: DISCHARGED with measured post-fire numbers.**

MEASURED: derived from the panel TSV's deferred_infeasible_square rows
(m3-W2-native-plink-panel.tsv, 2026-09-XX rollup).

| Quantity | Measured |
|---|---|
| regions deferring at the cap | 31 / 276 |
| banked regions | 245 |
| largest deferred span | 51.3 Mb |

31 regions exceeding the n_var ceiling were not converted in square mode;
affected span 412.7 Mb. This is disclosed as a methods/limitations item
alongside the occlusion disclosure.
"""

_CURRENT_DISCLOSURE = """## R4-COVERAGE — the square-mode deferral set is an ancestry-specific COVERAGE GAP

**Logged:** 2026-08-14 (`quick-260814-guk`, from Seth's 2026-08-14 R4).
**Status: REGISTERED as a DISCLOSURE OBLIGATION — not blocking the fire.**

| Quantity | Estimate |
|---|---|
| regions deferring at the 120k cap | **29 / 276 = 10.5%** |
| bankable target | **~247 regions** |
| largest deferred span | **48.5 Mb** |

⚠ **These are Seth's estimates, not measurements.** The ACTUAL numbers emerge at
fire time from the panel TSV's `deferred_infeasible_square` rows and MUST replace
them before anything is published.
"""

#: Innocent prose that contains the WORD "estimated" but none of the measured
#: sentinels. Seth's bare `estimate` marker would false-positive on this.
_FALSE_POSITIVE_DISCLOSURE = """## R4-COVERAGE — coverage gap, discharged

MEASURED: derived from the panel TSV deferred_infeasible_square rows.

The affected span was estimated from Stage B and then MEASURED at rollup time.
An earlier estimated figure was superseded by the measurement below.

| Quantity | Measured |
|---|---|
| regions deferring at the cap | 33 / 276 |
| banked regions | 243 |
| largest deferred span | 52.9 Mb |
"""


def _disclosure_file(tmp_path: Path, text: str, name="deferred-items.md") -> Path:
    p = tmp_path / name
    # Embed the block in a larger document so the heading extractor is exercised
    # the way it is against the real multi-section deferred-items.md.
    p.write_text("# Deferred items\n\n## R1-SOMETHING\n\nunrelated\n\n"
                 + text + "\n## R5-AFTER\n\ntrailing section\n")
    return p


# --------------------------------------------------------------------------- #
# parse_panel_tsv (A-05) — the SINGLE TSV parser                              #
# --------------------------------------------------------------------------- #

def test_parse_panel_tsv_green_nine_columns(tmp_path):
    p = _region1_panel(tmp_path)
    rows = fv.parse_panel_tsv(p)
    assert len(rows) == 1
    r = rows[0]
    assert r["region_id"] == "m2_region_00001"
    assert r["n_var"] == 102421
    assert r["peak_ram_gib"] == pytest.approx(78.2)
    assert r["n_dropped_occluded"] == 5
    assert r["status"] == "ok"


def test_parse_panel_tsv_green_empty_fields_become_none(tmp_path):
    p = _write_panel(tmp_path, [_panel_row("m2_region_00002", status="skipped_idempotent")])
    r = fv.parse_panel_tsv(p)[0]
    assert r["n_var"] is None and r["peak_ram_gib"] is None
    assert r["n_dropped_occluded"] is None
    assert r["status"] == "skipped_idempotent"


def test_parse_panel_tsv_green_detail_bearing_status_survives_tab_split(tmp_path):
    """A real deferral status carries spaces, ``=`` and ``>`` INSIDE the field."""
    p = _write_panel(tmp_path, [_panel_row("m2_region_00042", status=REAL_INFEASIBLE)])
    r = fv.parse_panel_tsv(p)[0]
    assert r["status"] == REAL_INFEASIBLE


def test_RED_parse_panel_tsv_renamed_header_column_refuses(tmp_path):
    bad = "\t".join(["region_id", "chrom"] + list(rnlp._PANEL_COLUMNS[2:]))
    p = _write_panel(tmp_path, [_panel_row("m2_region_00001")], header=bad)
    with pytest.raises(ValueError) as e:
        fv.parse_panel_tsv(p)
    assert "header" in str(e.value).lower()


def test_RED_parse_panel_tsv_missing_file(tmp_path):
    with pytest.raises(Exception):
        fv.parse_panel_tsv(tmp_path / "nope.tsv")


def test_RED_parse_panel_tsv_ragged_row(tmp_path):
    p = _write_panel(tmp_path, [_panel_row("m2_region_00001"), "m2_region_00002\t1\t5"])
    with pytest.raises(ValueError) as e:
        fv.parse_panel_tsv(p)
    assert "ragged" in str(e.value).lower() or "field" in str(e.value).lower()


# --------------------------------------------------------------------------- #
# A-03 — the shipped-vocabulary AST drift enforcer                            #
# --------------------------------------------------------------------------- #

def _extract_status_prefixes(source: str) -> set:
    """Constant prefix of every value assigned to ``result["status"]`` or written
    as a ``"status":`` dict entry. Handles ``Constant``, ``JoinedStr`` (leading
    ``Constant`` part) and ``IfExp`` (both branches)."""
    def prefixes(node) -> set:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return {node.value}
        if isinstance(node, ast.JoinedStr):
            head = node.values[0] if node.values else None
            if isinstance(head, ast.Constant) and isinstance(head.value, str):
                return {head.value}
            return set()
        if isinstance(node, ast.IfExp):
            return prefixes(node.body) | prefixes(node.orelse)
        return set()

    found: set = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if (isinstance(tgt, ast.Subscript)
                        and isinstance(tgt.slice, ast.Constant)
                        and tgt.slice.value == "status"):
                    found |= prefixes(node.value)
        elif isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value == "status":
                    found |= prefixes(v)
    return found


def test_status_vocabulary_extractor_is_not_vacuous():
    src = (PROJECT_ROOT / "src" / "python" / "run_native_ld_panel.py").read_text()
    found = _extract_status_prefixes(src)
    assert found, ("the AST extractor found ZERO status emission sites in the "
                   "shipped producer -> the drift guard below would be VACUOUS")
    assert len(found) >= 5, f"only {len(found)} status prefixes extracted: {sorted(found)}"


def test_shipped_status_vocabulary_is_covered_by_the_allow_list():
    src = (PROJECT_ROOT / "src" / "python" / "run_native_ld_panel.py").read_text()
    found = _extract_status_prefixes(src)
    uncovered = sorted(p for p in found
                       if fv._status_class(p) == fv.STATUS_UNKNOWN)
    assert not uncovered, (
        f"the shipped producer can emit status prefix(es) {uncovered} that "
        f"fire_verifier's allow-list does not recognize; a mid-fire row carrying "
        f"one would HARD_STOP as 'unknown'. Extend _OK_STATUSES / "
        f"_DEFERRAL_PREFIXES / _FAILURE_STATUSES and re-adjudicate the severity.")


def test_RED_status_vocabulary_guard_catches_a_new_shipped_status(tmp_path):
    """The SAME extractor + the SAME coverage assertion over a fixture producer
    carrying an unrecognized status must FAIL (the guard is not vacuous)."""
    fixture = tmp_path / "fake_producer.py"
    fixture.write_text(
        "def process_region(result):\n"
        "    result['status'] = 'skipped_idempotent'\n"
        "    result[\"status\"] = \"banana\"\n"
        "    return result\n"
    )
    found = _extract_status_prefixes(fixture.read_text())
    assert "banana" in found
    uncovered = sorted(p for p in found if fv._status_class(p) == fv.STATUS_UNKNOWN)
    assert uncovered == ["banana"], (
        "the coverage assertion did NOT flag an unrecognized shipped status -> "
        "the drift guard is vacuous")


def test_status_vocabulary_covers_the_measured_seven_sites():
    """The M2 table, pinned: every measured emission prefix classifies."""
    for prefix, want in [
        ("skipped_idempotent", fv.STATUS_OK),
        ("ok", fv.STATUS_OK),
        ("error", fv.STATUS_FAILURE),
        ("error: ", fv.STATUS_FAILURE),
        ("verify_failed", fv.STATUS_FAILURE),
        ("deferred_infeasible_square: n_var=", fv.STATUS_DEFERRAL),
        ("deferred_occlusion_anomaly: ", fv.STATUS_DEFERRAL),
    ]:
        assert fv._status_class(prefix) == want, prefix


# --------------------------------------------------------------------------- #
# classify_statuses (A-02) — PREFIX matching, not exact membership            #
# --------------------------------------------------------------------------- #

def test_classify_statuses_green_real_detail_bearing_deferrals():
    """THE regression pin: a REAL deferral carries a detail suffix. Exact
    membership (the prototype) would flag every one as unrecognized."""
    rows = ([{"status": "ok"}] * 5
            + [{"status": REAL_INFEASIBLE}] * 29
            + [{"status": REAL_OCCLUSION_ANOMALY}] * 2)
    c = fv.classify_statuses(rows)
    assert c.ok, c.detail
    assert c.measured["n_deferred"] == 31
    assert c.measured["n_ok"] == 5


def test_classify_statuses_green_skipped_idempotent_is_a_real_shipped_status():
    c = fv.classify_statuses([{"status": "skipped_idempotent"}] * 3)
    assert c.ok, c.detail
    assert c.measured["n_ok"] == 3


def test_RED_classify_statuses_unknown_token():
    c = fv.classify_statuses([{"status": "banana"}])
    assert not c.ok and c.severity == fv.HARD_STOP
    assert "banana" in c.detail


def test_RED_classify_statuses_empty_status():
    c = fv.classify_statuses([{"status": ""}])
    assert not c.ok and c.severity == fv.HARD_STOP


def test_RED_classify_statuses_unknown_deferral_reason():
    c = fv.classify_statuses([{"status": "deferred_mystery_reason"}])
    assert not c.ok and c.severity == fv.HARD_STOP
    assert "deferred_mystery_reason" in c.detail


def test_RED_classify_statuses_verify_failed_is_a_finding():
    c = fv.classify_statuses([{"status": "ok"}, {"status": "verify_failed"}])
    assert not c.ok
    assert c.severity == fv.FINDING, (
        "a region that banked NOTHING is not the gates working, but Stage C runs "
        "without --fail-fast so the correct response is report-to-Carter, not an "
        "auto-abort")


def test_RED_classify_statuses_real_error_row_is_a_finding():
    c = fv.classify_statuses([{"status": "ok"}, {"status": REAL_ERROR}])
    assert not c.ok and c.severity == fv.FINDING
    assert "1" in c.detail


def test_classify_statuses_unknown_outranks_finding():
    c = fv.classify_statuses([{"status": "verify_failed"}, {"status": "banana"}])
    assert not c.ok and c.severity == fv.HARD_STOP


# --------------------------------------------------------------------------- #
# check_nan_falsification (A-01)                                              #
# --------------------------------------------------------------------------- #

def test_nan_falsification_green_valid_npz(tmp_path):
    c = fv.check_nan_falsification(_good_npz(tmp_path))
    assert c.ok, c.detail


def test_shipped_verifier_rejects_both_nan_fixtures(tmp_path):
    """The implication pin. ``check_nan_falsification`` PASSES on the shipped
    ``content_verify_npz`` returning ok=True and claims that entails NaN-free.
    That claim is MEASURED here, not argued: both NaN fixtures must be ok=False."""
    ok_diag, reason_diag = rnlp.content_verify_npz(_nan_diagonal_npz(tmp_path))
    assert ok_diag is False, reason_diag
    ok_row, reason_row = rnlp.content_verify_npz(_whole_row_nan_npz(tmp_path))
    assert ok_row is False, reason_row
    # and the misreport the frozen reader's own comment warns about:
    assert "symmetric" in reason_row


def test_RED_nan_falsification_nan_on_the_diagonal(tmp_path):
    c = fv.check_nan_falsification(_nan_diagonal_npz(tmp_path))
    assert not c.ok and c.severity == fv.HARD_STOP
    assert "NaN" in c.detail
    assert "occlusion is NOT the sole NaN mechanism" in c.detail


def test_RED_nan_falsification_whole_row_nan_with_unit_diagonal(tmp_path):
    """The fire-#3 fingerprint: the shipped verifier calls it an asymmetry; the
    gate must name it a NaN and rank the SOURCE row."""
    c = fv.check_nan_falsification(_whole_row_nan_npz(tmp_path, row=7))
    assert not c.ok and c.severity == fv.HARD_STOP
    assert "NaN" in c.detail
    assert "occlusion is NOT the sole NaN mechanism" in c.detail
    assert c.measured["nan_source_rows"][0] == 7
    assert "7" in c.detail


def test_RED_nan_falsification_missing_file_fails_closed(tmp_path):
    c = fv.check_nan_falsification(tmp_path / "absent.npz")
    assert not c.ok and c.severity == fv.HARD_STOP
    assert "NaN" not in c.detail


def test_RED_nan_falsification_below_min_bytes_fails_closed(tmp_path):
    p = tmp_path / "tiny.npz"
    p.write_bytes(b"x" * (alp._MIN_REGION_NPZ_BYTES - 1))
    c = fv.check_nan_falsification(p)
    assert not c.ok and c.severity == fv.HARD_STOP
    assert str(alp._MIN_REGION_NPZ_BYTES) in c.detail
    assert "NaN" not in c.detail


def test_RED_nan_falsification_corrupt_bytes_does_not_claim_nan(tmp_path):
    p = tmp_path / "corrupt.npz"
    p.write_bytes(b"x" * 4096)
    c = fv.check_nan_falsification(p)
    assert not c.ok
    assert "NaN" not in c.detail, (
        "a non-NaN failure must NEVER be reported as a NaN finding — that is the "
        "misattribution the frozen reader's own comment warns against")


def test_RED_nan_falsification_verifier_raising_oserror_fails_closed(tmp_path):
    def broken(_path, **_kw):
        raise OSError("disk gone")
    c = fv.check_nan_falsification(_good_npz(tmp_path), verifier=broken)
    assert not c.ok
    assert "NaN" not in c.detail


def test_nan_falsification_uses_the_shipped_verifier_by_default(tmp_path):
    """Identity: the default verifier IS ``run_native_ld_panel.content_verify_npz``
    (never a re-implementation)."""
    assert fv._default_npz_verifier() is rnlp.content_verify_npz
    assert fv._default_nan_scanner() is pln._has_any_nan_blocked
    assert fv._default_nan_ranker() is pln.nan_variant_indices


def test_nan_falsification_min_bytes_default_is_the_shipped_floor():
    assert fv._default_min_npz_bytes() is alp._MIN_REGION_NPZ_BYTES


# --------------------------------------------------------------------------- #
# check_manifest_rows (A-10)                                                  #
# --------------------------------------------------------------------------- #

def test_manifest_rows_green(tmp_path):
    c = fv.check_manifest_rows(_manifest(tmp_path), expected_records=5,
                               region_id="m2_region_00001")
    assert c.ok, c.detail
    assert c.measured["records"] == 5


def test_RED_manifest_rows_wrong_line_count(tmp_path):
    c = fv.check_manifest_rows(_manifest(tmp_path, n_records=3), expected_records=5,
                               region_id="m2_region_00001")
    assert not c.ok and "expected 6" in c.detail


def test_RED_manifest_rows_success_placeholders_at_the_right_count(tmp_path):
    """The $2,140 defect class: right line count, wrong content."""
    p = tmp_path / "marker_manifest.tsv"
    p.write_text("header\n" + "_SUCCESS\n" * 5)
    c = fv.check_manifest_rows(p, expected_records=5, region_id="m2_region_00001")
    assert not c.ok and "placeholder" in c.detail


def test_RED_manifest_rows_missing_file(tmp_path):
    c = fv.check_manifest_rows(tmp_path / "nope.tsv", expected_records=5,
                               region_id="m2_region_00001")
    assert not c.ok and c.severity == fv.HARD_STOP


def test_RED_manifest_rows_wrong_region_id(tmp_path):
    p = _manifest(tmp_path, region_id="m2_region_00099")
    c = fv.check_manifest_rows(p, expected_records=5, region_id="m2_region_00001")
    assert not c.ok
    assert "m2_region_00099" in c.detail and "m2_region_00001" in c.detail


# --------------------------------------------------------------------------- #
# check_occlusion_ceiling (M5 / clause (d))                                   #
# --------------------------------------------------------------------------- #

def test_occlusion_ceiling_green_region1():
    c = fv.check_occlusion_ceiling(n_occluded=5, n_var=102421)
    assert c.ok, c.detail
    assert c.measured["ceiling"] == pytest.approx(51.2105, abs=1e-3)


def test_RED_occlusion_ceiling_exceeded():
    c = fv.check_occlusion_ceiling(n_occluded=52, n_var=102421)
    assert not c.ok and "DEFER" in c.detail


def test_occlusion_ceiling_boundary_is_strictly_greater():
    """Clause (d) says 'exceeds' -> count == ceiling stays on the lockstep path."""
    assert fv.check_occlusion_ceiling(n_occluded=60, n_var=120000).ok
    assert not fv.check_occlusion_ceiling(n_occluded=61, n_var=120000).ok


def test_RED_occlusion_ceiling_missing_count_fails_closed():
    c = fv.check_occlusion_ceiling(n_occluded=None, n_var=102421)
    assert not c.ok


def test_occlusion_fraction_is_the_shipped_module_global(monkeypatch):
    """IDENTITY, not a literal: the default fraction is READ from the shipped
    module global at evaluation time, exactly as the producer reads it."""
    assert fv._default_occlusion_fraction() == rnlp._OCCLUSION_ANOMALY_FRACTION
    monkeypatch.setattr(rnlp, "_OCCLUSION_ANOMALY_FRACTION", 0.5)
    assert fv._default_occlusion_fraction() == 0.5
    # 5 of 100 is under a 0.5 ceiling of 50 -> the gate must follow the global
    assert fv.check_occlusion_ceiling(n_occluded=5, n_var=100).ok
    assert not fv.check_occlusion_ceiling(n_occluded=51, n_var=100).ok


def test_no_hardcoded_shipped_constants_in_the_module():
    """Hard rule 4: a literal 0.0005 / 120000 / re-declared 256 is a defect."""
    src = (PROJECT_ROOT / "src" / "python" / "fire_verifier.py").read_text()
    code = "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())
    for banned in ("0.0005", "120000", "= 256"):
        assert banned not in code, (
            f"fire_verifier.py hardcodes {banned!r}; import the shipped constant "
            f"instead (a hand-transcribed constant is a silent divergence)")


# --------------------------------------------------------------------------- #
# check_region1_status (A-04)                                                 #
# --------------------------------------------------------------------------- #

def test_region1_status_green():
    assert fv.check_region1_status("ok").ok


def test_RED_region1_status_real_deferral_is_a_finding():
    c = fv.check_region1_status(REAL_INFEASIBLE)
    assert not c.ok and c.severity == fv.FINDING
    assert "not a retry" in c.detail


def test_RED_region1_status_verify_failed_is_the_widening_pin():
    """Region 1 runs under ``--fail-fast``, where ``RegionGateError`` fires on ANY
    status != 'ok' (run_native_ld_panel.py:1161) — not just a deferral."""
    c = fv.check_region1_status("verify_failed")
    assert not c.ok and c.severity == fv.FINDING


def test_RED_region1_status_empty():
    assert not fv.check_region1_status("").ok


# --------------------------------------------------------------------------- #
# check_peak_ram (A-09)                                                       #
# --------------------------------------------------------------------------- #

def test_peak_ram_green():
    assert fv.check_peak_ram(78.2).ok


def test_RED_peak_ram_over_limit():
    c = fv.check_peak_ram(110.0)
    assert not c.ok and c.severity == fv.HARD_STOP


def test_RED_peak_ram_unreported_fails_closed():
    c = fv.check_peak_ram(None)
    assert not c.ok and "FAIL CLOSED" in c.detail


def test_vm_total_gib_is_the_repo_documented_value():
    assert fv._VM_TOTAL_GIB == 120.0


# --------------------------------------------------------------------------- #
# check_maf_depression (A-12)                                                 #
# --------------------------------------------------------------------------- #

def test_maf_depression_green():
    pairs = ([{"panel_maf": 0.0078, "sumstats_maf": 0.014}] * 4
             + [{"panel_maf": 0.02, "sumstats_maf": 0.019}])
    assert fv.check_maf_depression(pairs).ok


def test_RED_maf_depression_no_systematic_depression():
    pairs = ([{"panel_maf": 0.02, "sumstats_maf": 0.014}] * 4
             + [{"panel_maf": 0.007, "sumstats_maf": 0.014}])
    c = fv.check_maf_depression(pairs)
    assert not c.ok and c.severity == fv.FINDING and "WEAKENS" in c.detail


def test_RED_maf_depression_empty_pairs_fails_closed():
    c = fv.check_maf_depression([])
    assert not c.ok and c.severity == fv.FINDING


# --------------------------------------------------------------------------- #
# check_cost_denominator (A-08)                                               #
# --------------------------------------------------------------------------- #

def test_cost_denominator_green():
    assert fv.check_cost_denominator(n_regions_used=247, n_bankable=247, n_total=276).ok


def test_RED_cost_denominator_uses_all_276():
    c = fv.check_cost_denominator(n_regions_used=276, n_bankable=247, n_total=276)
    assert not c.ok and "understates" in c.detail


def test_RED_cost_denominator_used_not_equal_bankable():
    c = fv.check_cost_denominator(n_regions_used=250, n_bankable=247, n_total=276)
    assert not c.ok


def test_cost_denominator_n_total_has_no_default():
    """276 is correct today (M9) — a default is how a count goes silently stale."""
    with pytest.raises(TypeError):
        fv.check_cost_denominator(247, 247)


# --------------------------------------------------------------------------- #
# check_coverage_disclosure_resolved (A-06) — UNCONDITIONAL fixture cases     #
# --------------------------------------------------------------------------- #

def test_RED_coverage_disclosure_current_text_still_carries_estimates(tmp_path):
    p = _disclosure_file(tmp_path, _CURRENT_DISCLOSURE)
    c = fv.check_coverage_disclosure_resolved(p)
    assert not c.ok and c.severity == fv.HARD_STOP
    assert "29 / 276 = 10.5%" in c.detail, (
        "the detail must NAME the sentinel it found, so the obligation is actionable")


def test_coverage_disclosure_green_with_measured_numbers_and_provenance(tmp_path):
    p = _disclosure_file(tmp_path, _GOOD_DISCLOSURE)
    c = fv.check_coverage_disclosure_resolved(p)
    assert c.ok, c.detail


def test_RED_coverage_disclosure_empty_file(tmp_path):
    p = tmp_path / "empty.md"
    p.write_text("")
    c = fv.check_coverage_disclosure_resolved(p)
    assert not c.ok


def test_RED_coverage_disclosure_missing_file(tmp_path):
    c = fv.check_coverage_disclosure_resolved(tmp_path / "nope.md")
    assert not c.ok and c.severity == fv.HARD_STOP


def test_RED_coverage_disclosure_renamed_heading_is_vacuity_not_green(tmp_path):
    """T-sml-07: a renamed heading empties the extracted block; an empty block
    satisfies every content assertion TRIVIALLY. Vacuity is a FAIL."""
    p = _disclosure_file(tmp_path, _GOOD_DISCLOSURE.replace("## R4-COVERAGE",
                                                            "## R4-COVERAGE-RENAMED"))
    c = fv.check_coverage_disclosure_resolved(p)
    assert not c.ok
    assert "R4-COVERAGE" in c.detail


def test_RED_coverage_disclosure_sentinels_removed_but_no_provenance(tmp_path):
    """Deleting the warning must not discharge the obligation."""
    text = _GOOD_DISCLOSURE.replace(
        "MEASURED: derived from the panel TSV's deferred_infeasible_square rows\n"
        "(m3-W2-native-plink-panel.tsv, 2026-09-XX rollup).\n", "")
    p = _disclosure_file(tmp_path, text)
    c = fv.check_coverage_disclosure_resolved(p)
    assert not c.ok and "MEASURED:" in c.detail


def test_coverage_disclosure_false_positive_guard_on_the_word_estimated(tmp_path):
    """Seth's bare ``estimate`` marker would false-positive on innocent prose."""
    p = _disclosure_file(tmp_path, _FALSE_POSITIVE_DISCLOSURE)
    c = fv.check_coverage_disclosure_resolved(p)
    assert c.ok, c.detail


def test_coverage_disclosure_infeasible_ceiling_is_the_shipped_constant():
    assert fv._infeasible_ceiling() is rnlp._DEFAULT_MAX_N_VAR


# --------------------------------------------------------------------------- #
# A-07 — the live gate + its three anti-masking guards                        #
# --------------------------------------------------------------------------- #

def test_panel_artifact_name_is_imported_from_the_producer():
    assert fv._panel_artifact_name() is rnlp._DEFAULT_PANEL_NAME


def test_measured_panel_finder_is_shown_valid(tmp_path):
    """Guard (b): the SKIP CONDITION itself is proven able to distinguish.
    A skip-guard hides the bug unless the skipped check is shown valid."""
    empty_tree = tmp_path / "empty"
    (empty_tree / "sub").mkdir(parents=True)
    (empty_tree / "sub" / "unrelated.tsv").write_text("x\n")
    assert fv.find_measured_panel_tsvs(empty_tree) == []

    populated = tmp_path / "populated"
    (populated / "results").mkdir(parents=True)
    target = populated / "results" / rnlp._DEFAULT_PANEL_NAME
    target.write_text("\t".join(rnlp._PANEL_COLUMNS) + "\n")
    found = fv.find_measured_panel_tsvs(populated)
    assert [Path(p).name for p in found] == [rnlp._DEFAULT_PANEL_NAME]
    assert Path(found[0]).resolve() == target.resolve()


def test_coverage_disclosure_live_gate_against_the_repo_file():
    """Guard (c): this SKIP is the named enforcer of the R4-COVERAGE disclosure
    obligation. It stops skipping the moment a measured panel TSV lands in-repo,
    and then stays RED until the disclosure carries measured numbers."""
    panels = fv.find_measured_panel_tsvs(PROJECT_ROOT)
    if not panels:
        pytest.skip(
            f"no measured panel TSV ({rnlp._DEFAULT_PANEL_NAME}) in-repo yet — the "
            f"R4-COVERAGE disclosure cannot carry measured numbers before the fire. "
            f"This skip IS the enforcer: it fires the moment the artifact lands.")
    disclosure = (PROJECT_ROOT / ".planning" / "phases" / "m3-aou-afr-ld-panel-build"
                  / "deferred-items.md")
    c = fv.check_coverage_disclosure_resolved(disclosure)
    assert c.ok, (
        f"a measured panel TSV exists ({[str(p) for p in panels]}) but the "
        f"R4-COVERAGE disclosure has not been updated: {c.detail}")


# --------------------------------------------------------------------------- #
# summarize / CLI                                                             #
# --------------------------------------------------------------------------- #

def test_summarize_all_pass_exit_zero():
    s = fv.summarize([fv.check_occlusion_ceiling(5, 102421), fv.check_peak_ram(78.2)])
    assert s["all_pass"] is True and s["exit_code"] == 0 and s["n_checks"] == 2
    assert s["hard_stops"] == [] and s["findings"] == []


def test_summarize_buckets_hard_stops_and_findings_separately():
    checks = [fv.check_occlusion_ceiling(5, 102421),
              fv.check_occlusion_ceiling(52, 102421),
              fv.check_region1_status(REAL_INFEASIBLE)]
    s = fv.summarize(checks)
    assert s["exit_code"] == 1
    assert "occlusion_anomaly_ceiling" in s["hard_stops"]
    assert "region1_status" in s["findings"]
    assert "region1_status" not in s["hard_stops"]


def test_check_status_is_pass_or_fail_only():
    for c in [fv.check_peak_ram(78.2), fv.check_peak_ram(None),
              fv.check_occlusion_ceiling(5, 102421)]:
        assert c.status in (fv.PASS, fv.FAIL)


def test_cli_stage_c_green_exit_zero(tmp_path, capsys):
    p = _write_panel(tmp_path, [_panel_row("m2_region_00001", status="ok"),
                                _panel_row("m2_region_00042", status=REAL_INFEASIBLE)])
    rc = fv.main(["stage-c", "--panel-tsv", str(p)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "status_classification" in out


def test_RED_cli_stage_c_unknown_status_exit_one(tmp_path):
    p = _write_panel(tmp_path, [_panel_row("m2_region_00001", status="banana")])
    assert fv.main(["stage-c", "--panel-tsv", str(p)]) == 1


def test_cli_report_json_round_trips(tmp_path):
    p = _write_panel(tmp_path, [_panel_row("m2_region_00001", status="ok")])
    report = tmp_path / "gate.json"
    fv.main(["stage-c", "--panel-tsv", str(p), "--report", str(report)])
    data = json.loads(report.read_text())
    assert data["n_checks"] >= 1
    assert "status_classification" in [c["name"] for c in data["report"]]
    assert data["exit_code"] == 0


def test_cli_stage_a_green(tmp_path):
    panel = _region1_panel(tmp_path)
    manifest = _manifest(tmp_path)
    npz = _good_npz(tmp_path)
    rc = fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
                  "--manifest", str(manifest), "--npz", str(npz)])
    assert rc == 0


def test_RED_cli_stage_a_requires_npz(tmp_path):
    panel = _region1_panel(tmp_path)
    manifest = _manifest(tmp_path)
    with pytest.raises(SystemExit) as e:
        fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
                 "--manifest", str(manifest)])
    assert e.value.code == 2, "a falsification that did not run is not a falsification"


def test_RED_cli_stage_a_unknown_region_fails_closed(tmp_path):
    panel = _region1_panel(tmp_path)
    manifest = _manifest(tmp_path)
    npz = _good_npz(tmp_path)
    rc = fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_99999",
                  "--manifest", str(manifest), "--npz", str(npz)])
    assert rc == 1


def test_cli_stage_b_green(tmp_path):
    rows = [_panel_row(f"m2_region_{i:05d}", n_var=90000 + i, wall_min=30.0,
                       peak_ram_gib=70.0 + i, output_gib=30.0, status="ok",
                       n_dropped_occluded=2, n_dropped_monomorphic=0)
            for i in range(1, 6)]
    p = _write_panel(tmp_path, rows)
    assert fv.main(["stage-b", "--panel-tsv", str(p), "--n-total", "276",
                    "--vm-gib", "120"]) == 0


def test_RED_cli_stage_b_peak_ram_over_limit(tmp_path):
    rows = [_panel_row("m2_region_00001", n_var=102421, wall_min=41.3,
                       peak_ram_gib=110.0, output_gib=39.1, status="ok",
                       n_dropped_occluded=5, n_dropped_monomorphic=0)]
    p = _write_panel(tmp_path, rows)
    assert fv.main(["stage-b", "--panel-tsv", str(p), "--n-total", "276"]) == 1


def test_RED_cli_stage_b_no_computed_rows_is_vacuity(tmp_path):
    """Nothing to measure must FAIL, not pass vacuously."""
    p = _write_panel(tmp_path, [_panel_row("m2_region_00001",
                                           status="skipped_idempotent")])
    assert fv.main(["stage-b", "--panel-tsv", str(p), "--n-total", "276"]) == 1


def test_RED_cli_disclosure_against_the_live_repo_file():
    """The disclosure subcommand, run against the REAL file, is red today."""
    disclosure = (PROJECT_ROOT / ".planning" / "phases" / "m3-aou-afr-ld-panel-build"
                  / "deferred-items.md")
    assert fv.main(["disclosure", "--file", str(disclosure)]) == 1


def test_report_json_carries_no_float_arrays(tmp_path):
    """T-sml-01: the report leaves the perimeter as text. Counts, booleans, byte
    sizes, row indices and policy labels only — never LD values."""
    panel = _region1_panel(tmp_path)
    manifest = _manifest(tmp_path)
    npz = _whole_row_nan_npz(tmp_path)
    report = tmp_path / "stage_a.json"
    fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
             "--manifest", str(manifest), "--npz", str(npz), "--report", str(report)])
    data = json.loads(report.read_text())

    def walk(node, path="report"):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for v in node:
                assert not isinstance(v, float), (
                    f"{path} carries a float array element {v!r} — the gate must "
                    f"emit counts/indices/labels, never LD values")
                walk(v, f"{path}[]")

    for entry in data["report"]:
        walk(entry["measured"], f"report[{entry['name']}].measured")
