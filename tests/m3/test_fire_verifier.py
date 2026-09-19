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
no measured panel TSV exists in-repo. That skip IS the named enforcer of
the R4-COVERAGE disclosure obligation: the moment a measured panel TSV lands in the
repo the gate stops skipping and goes red until the disclosure carries measured
numbers plus a ``MEASURED:`` provenance line. The skip is guarded against masking
three ways (the check function's own green/red run unconditionally against
fixtures; the finder itself is shown valid on a tmp tree with and without the file;
the skip-count move is recorded in the SUMMARY).

THIS MODULE'S SKIP COUNT — ⚠ CORRECTED 2026-09-18 (quick-260918-qz5). This
paragraph used to claim the module "contributes exactly one skip to the tests/m3
baseline (31 -> 32)". BOTH halves are now wrong, and the retired wording is kept
here rather than deleted so the correction is legible: the baseline is 33 (not 31
— MEASURED at 940df48 and again at b6076b2: 1262 ids, 1229 passed, 33 skipped),
and this module now contributes TWO skips, because quick-260918-qz5 added a second
live gate on the same C7 template:

  * ``test_coverage_disclosure_live_gate_against_the_repo_file`` — the
    R4-COVERAGE disclosure obligation;
  * ``test_raised_nan_class_coverage_live_gate_against_the_repo_file`` — the
    R5-RAISED-NAN closeout obligation for the raised-NaN class.

Both skip on the SAME condition (``find_measured_panel_tsvs(PROJECT_ROOT)`` is
empty) and both fire the moment a measured panel TSV lands in-repo. So the
tests/m3 skip count moves **33 -> 34**: 33 at the end of that change would mean the
new enforcer did not collect (a silent coverage loss), and 35+ would mean something
else started skipping. Either is a stop.

⚠ AND THIS CLAIM NOW HAS A NAMED ENFORCER, which is the whole point of correcting
it:
``tests/m3/test_fire_runbook_pins.py::test_the_two_live_gate_skips_are_the_only_ones_while_no_panel_tsv_is_in_repo``
runs this module in a child process and reconciles its skips BY TEST ID, asserting
exactly these two names. An unenforced count claim is precisely the class of
belief-only assertion this correction exists to fix, and leaving the corrected
number equally unenforced would just reset the same trap.
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
#: A REAL two-condition deferral in the shape the producer emits it TODAY (the
#: constant head plus the three reported numbers and which condition fired). Copied
#: from the shipped f-string in ``run_native_ld_panel.process_region``, not from
#: memory; the ast status-vocabulary enforcer below pins the constant head.
REAL_OCCLUSION_ANOMALY = (
    "deferred_occlusion_anomaly: 812 occluded rows at 700 sites of 96708 "
    "(site_fraction 0.7238% > ceiling 0.5056%; inflation 1.16x <= ceiling 3.42x; "
    "fired=site_fraction)")
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
    """The Stage-A panel: region 1 computed ok with 231 occluded ROWS of 102,421.

    231 is MEASURED (2026-08-19/20 — 231 occluded rows at 196 sites of 96,708 sites;
    ``.planning/debug/260820-site-basis-sweep-results-as-received.md``), not derived.
    ``n_dropped_occluded`` is and stays a ROW count.
    """
    row = _panel_row("m2_region_00001", chrom=1, n_var=102421, wall_min=41.3,
                     peak_ram_gib=78.2, output_gib=39.1, status="ok",
                     n_dropped_occluded=231, n_dropped_monomorphic=0)
    return _write_panel(tmp_path, [row], **kw)


def _gate_json(tmp_path: Path, *, region_id="m2_region_00001", occ_rows=231,
               occ_sites=196, n_sites=96708, n_rows=102421,
               name=None, **overrides) -> Path:
    """A producer-shaped ``{region_id}.occlusion_gate.json`` in the region-1
    MEASURED shape (231 occluded rows at 196 of 96,708 sites -> 0.2027% / 1.18x).

    The ceilings are read off the SHIPPED producer, never typed here."""
    data = {
        "region_id": region_id,
        "n_rows": n_rows,
        "n_sites": n_sites,
        "occ_rows": occ_rows,
        "occ_sites": occ_sites,
        "site_fraction": (occ_sites / n_sites) if n_sites else 0.0,
        "inflation": (occ_rows / occ_sites) if occ_sites else None,
        "site_fraction_ceiling": rnlp._OCCLUSION_SITE_FRACTION_CEILING,
        "inflation_ceiling": rnlp._OCCLUSION_INFLATION_CEILING,
        "fired": [],
        "verdict": "ok",
    }
    data.update(overrides)
    path = tmp_path / (name or f"{region_id}.occlusion_gate.json")
    path.write_text(json.dumps(data, indent=2) + "\n")
    return path


def _excludelist(tmp_path: Path, n_ids: int = 231,
                 region_id="m2_region_00001") -> Path:
    """The region's ``.occluded.excludelist`` — one variant id per line, exactly as
    the producer writes it and exactly as plink ``--exclude`` consumed it. Its LINE
    COUNT is what Stage A derives ``expected_records`` from."""
    path = tmp_path / f"{region_id}.occluded.excludelist"
    path.write_text("".join(f"chr1:{1980475 + i}:G:A\n" for i in range(n_ids)))
    return path


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
    assert r["n_dropped_occluded"] == 231     # a ROW count, MEASURED 2026-08-19/20
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

def test_check_manifest_rows_has_no_default_expected_records():
    """A DEFAULT record count is a human-typed number wearing an API's clothes: it
    made ``expected_records=5`` the silent fallback for every caller that forgot to
    pass one, which is how the withdrawn "5 occluded" premise reached the fire
    runbook. Every caller must now state the count, and Stage A DERIVES it."""
    import inspect

    param = inspect.signature(fv.check_manifest_rows).parameters["expected_records"]
    assert param.default is inspect.Parameter.empty


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
# check_occlusion_gate (the POSTED two-condition clause (d), mk7ze)           #
# --------------------------------------------------------------------------- #

def test_occlusion_gate_green_region1_measured():
    """Region 1 as MEASURED 2026-08-19/20 — 231 occluded ROWS at 196 SITES of
    96,708 sites -> a 0.2027% site fraction and 1.18x inflation, under BOTH posted
    ceilings, so the gate must not fire there."""
    c = fv.check_occlusion_gate(occ_rows=231, occ_sites=196, n_sites=96708)
    assert c.ok, c.detail
    assert c.measured["fired"] == []
    assert c.measured["site_fraction"] == pytest.approx(196 / 96708)
    assert c.measured["inflation"] == pytest.approx(231 / 196)


def test_RED_occlusion_gate_site_fraction_exceeded():
    c = fv.check_occlusion_gate(occ_rows=700, occ_sites=600, n_sites=96708)
    assert not c.ok and "DEFER" in c.detail
    assert c.measured["fired"] == ["site_fraction"]


def test_RED_occlusion_gate_inflation_exceeded_with_site_fraction_under():
    """The COMPANION condition alone — the region the withdrawn single-condition
    ceiling could never have caught: 1 occluded site of 100,000 (a 0.001% site
    fraction, far under) carrying 8 occluded rows -> inflation 8.0, over."""
    c = fv.check_occlusion_gate(occ_rows=8, occ_sites=1, n_sites=100000)
    assert not c.ok
    assert c.measured["fired"] == ["inflation"]
    assert c.measured["site_fraction"] < c.measured["site_fraction_ceiling"]


def test_occlusion_gate_boundary_is_strictly_greater_on_both_conditions():
    """The posted rule says "exceeds" -> STRICT ``>`` on EACH condition; a value
    equal to its ceiling stays on the exclude-in-lockstep path."""
    tie = fv.check_occlusion_gate(occ_rows=1, occ_sites=1, n_sites=2000,
                                  site_ceiling=1 / 2000, inflation_ceiling=2.0)
    assert tie.ok and tie.measured["fired"] == []
    over = fv.check_occlusion_gate(occ_rows=1, occ_sites=2, n_sites=2000,
                                   site_ceiling=1 / 2000, inflation_ceiling=2.0)
    assert not over.ok and over.measured["fired"] == ["site_fraction"]

    tie2 = fv.check_occlusion_gate(occ_rows=8, occ_sites=1, n_sites=100000,
                                   inflation_ceiling=8.0)
    assert tie2.ok and tie2.measured["fired"] == []
    over2 = fv.check_occlusion_gate(occ_rows=9, occ_sites=1, n_sites=100000,
                                    inflation_ceiling=8.0)
    assert not over2.ok and over2.measured["fired"] == ["inflation"]


def test_occlusion_gate_zero_occlusion_reports_no_inflation():
    """0/0 is not a number: a region with no occluded site has NO inflation, and
    reporting 0.0 there would invent a measurement."""
    c = fv.check_occlusion_gate(occ_rows=0, occ_sites=0, n_sites=96708)
    assert c.ok and c.measured["inflation"] is None
    assert c.measured["fired"] == []


@pytest.mark.parametrize("missing", ["occ_rows", "occ_sites", "n_sites"])
def test_RED_occlusion_gate_missing_input_fails_closed(missing):
    args = {"occ_rows": 231, "occ_sites": 196, "n_sites": 96708}
    args[missing] = None
    c = fv.check_occlusion_gate(**args)
    assert not c.ok and "FAIL CLOSED" in c.detail


def test_occlusion_ceilings_are_the_shipped_module_globals(monkeypatch):
    """IDENTITY, not a literal: BOTH ceilings are READ from the shipped producer's
    module globals at EVALUATION time, exactly as the producer reads them."""
    assert (fv._default_site_fraction_ceiling()
            == rnlp._OCCLUSION_SITE_FRACTION_CEILING)
    assert fv._default_inflation_ceiling() == rnlp._OCCLUSION_INFLATION_CEILING
    monkeypatch.setattr(rnlp, "_OCCLUSION_SITE_FRACTION_CEILING", 0.5)
    monkeypatch.setattr(rnlp, "_OCCLUSION_INFLATION_CEILING", 100.0)
    assert fv._default_site_fraction_ceiling() == 0.5
    assert fv._default_inflation_ceiling() == 100.0
    # the gate must FOLLOW the globals, never a snapshot taken at import
    assert fv.check_occlusion_gate(occ_rows=5, occ_sites=5, n_sites=100).ok
    assert not fv.check_occlusion_gate(occ_rows=51, occ_sites=51, n_sites=100).ok


def test_producer_ceilings_come_from_the_one_pinned_constants_module():
    """The chain the whole batch rests on, asserted end to end: pinned module ->
    producer module globals -> the verifier's evaluation-time accessors."""
    import occlusion_gate_constants as ogc

    assert (rnlp._OCCLUSION_SITE_FRACTION_CEILING
            == ogc.OCCLUSION_SITE_FRACTION_CEILING)
    assert rnlp._OCCLUSION_INFLATION_CEILING == ogc.OCCLUSION_INFLATION_CEILING
    assert (fv._default_site_fraction_ceiling()
            == ogc.OCCLUSION_SITE_FRACTION_CEILING)
    assert fv._default_inflation_ceiling() == ogc.OCCLUSION_INFLATION_CEILING


def test_no_hardcoded_shipped_constants_in_the_module():
    """Hard rule 4: a hand-typed 0.0005 / 0.005056 / 0.5056 / 3.42 / 120000 / a
    re-declared 256 is a defect.

    ⚠ THE SCAN STRIPS ``#`` COMMENTS ONLY — a docstring or an f-string detail is
    CODE and IS scanned. That is deliberate: a ceiling typed into a user-facing
    detail string is exactly as unpinned as one typed into an expression. Render it
    from ``_default_site_fraction_ceiling()`` / ``_default_inflation_ceiling()``
    instead — identity, not a copy."""
    src = (PROJECT_ROOT / "src" / "python" / "fire_verifier.py").read_text()
    code = "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())
    for banned in ("0.0005", "0.005056", "0.5056", "3.42", "120000", "= 256"):
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
    s = fv.summarize([fv.check_occlusion_gate(231, 196, 96708),
                      fv.check_peak_ram(78.2)])
    assert s["all_pass"] is True and s["exit_code"] == 0 and s["n_checks"] == 2
    assert s["hard_stops"] == [] and s["findings"] == []


def test_summarize_buckets_hard_stops_and_findings_separately():
    checks = [fv.check_occlusion_gate(231, 196, 96708),
              fv.check_occlusion_gate(700, 600, 96708),
              fv.check_region1_status(REAL_INFEASIBLE)]
    s = fv.summarize(checks)
    assert s["exit_code"] == 1
    assert "occlusion_gate" in s["hard_stops"]
    assert "region1_status" in s["findings"]
    assert "region1_status" not in s["hard_stops"]


def test_check_status_is_pass_or_fail_only():
    for c in [fv.check_peak_ram(78.2), fv.check_peak_ram(None),
              fv.check_occlusion_gate(231, 196, 96708)]:
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
    """The whole Stage-A chain green on the MEASURED region-1 shape: a 231-record
    manifest, a 231-id excludelist, and a sidecar reporting occ_rows=231."""
    panel = _region1_panel(tmp_path)
    manifest = _manifest(tmp_path, n_records=231)
    npz = _good_npz(tmp_path)
    gate = _gate_json(tmp_path)
    excl = _excludelist(tmp_path)
    rc = fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
                  "--manifest", str(manifest), "--npz", str(npz),
                  "--gate-json", str(gate), "--excludelist", str(excl)])
    assert rc == 0


def test_cli_stage_a_derives_expected_records_from_the_excludelist(tmp_path, capsys):
    """expected_records is DERIVED from the excludelist LINE COUNT and cross-checked
    against the sidecar's occ_rows — never typed. Shown non-vacuous by using a
    count (7) that appears nowhere as a default."""
    panel = _region1_panel(tmp_path)
    manifest = _manifest(tmp_path, n_records=7)
    npz = _good_npz(tmp_path)
    gate = _gate_json(tmp_path, occ_rows=7, occ_sites=7)
    excl = _excludelist(tmp_path, n_ids=7)
    rc = fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
                  "--manifest", str(manifest), "--npz", str(npz),
                  "--gate-json", str(gate), "--excludelist", str(excl)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "expected_records_derivation" in out
    assert "DERIVED" in out and "occ_rows=7" in out


def test_RED_cli_stage_a_excludelist_sidecar_mismatch_fails_closed(tmp_path, capsys):
    """THE CROSS-CHECK CONTROL, and the entire point of the derivation: the sidecar
    says 230 while the excludelist carries 231. Two records of the SAME drop set
    disagree -> STOP and re-measure. Picking either one would be the defect.

    The ONLY difference from ``test_cli_stage_a_green`` (which is 231/231 and exits
    0) is the sidecar's occ_rows, so the red is attributable to the cross-check and
    to nothing else — asserted on the detail text, not merely on the exit code."""
    panel = _region1_panel(tmp_path)
    manifest = _manifest(tmp_path, n_records=231)
    npz = _good_npz(tmp_path)
    gate = _gate_json(tmp_path, occ_rows=230)
    excl = _excludelist(tmp_path, n_ids=231)
    rc = fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
                  "--manifest", str(manifest), "--npz", str(npz),
                  "--gate-json", str(gate), "--excludelist", str(excl)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "CROSS-CHECK FAILED" in out
    assert "231 variant id(s)" in out and "occ_rows=230" in out
    assert "expected_records_derivation" in out


def test_RED_cli_stage_a_requires_excludelist(tmp_path):
    """No excludelist -> nothing to DERIVE from -> argparse refuses. There is no
    silent fallback to a human's number any more."""
    panel = _region1_panel(tmp_path)
    with pytest.raises(SystemExit) as e:
        fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
                 "--manifest", str(_manifest(tmp_path)), "--npz", str(_good_npz(tmp_path)),
                 "--gate-json", str(_gate_json(tmp_path))])
    assert e.value.code == 2


def test_RED_cli_stage_a_absent_excludelist_fails_closed(tmp_path):
    """A named-but-missing excludelist is unmeasurable -> FAIL CLOSED."""
    panel = _region1_panel(tmp_path)
    rc = fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
                  "--manifest", str(_manifest(tmp_path, n_records=231)),
                  "--npz", str(_good_npz(tmp_path)),
                  "--gate-json", str(_gate_json(tmp_path)),
                  "--excludelist", str(tmp_path / "nope.occluded.excludelist")])
    assert rc == 1


def test_cli_stage_a_expected_records_override_is_logged_as_an_override(tmp_path, capsys):
    """--expected-records is an OVERRIDE, not the source of truth, and it says so in
    the check detail alongside the value it displaced."""
    panel = _region1_panel(tmp_path)
    manifest = _manifest(tmp_path, n_records=3)
    npz = _good_npz(tmp_path)
    gate = _gate_json(tmp_path, occ_rows=231)
    excl = _excludelist(tmp_path, n_ids=231)
    rc = fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
                  "--manifest", str(manifest), "--npz", str(npz),
                  "--gate-json", str(gate), "--excludelist", str(excl),
                  "--expected-records", "3"])
    out = capsys.readouterr().out
    # the derivation itself still SUCCEEDED (231 from the excludelist, cross-checked
    # against the sidecar) and the override is recorded next to the value it
    # displaced, so the report can never be read as "231 was measured to be 3".
    assert "OVERRIDDEN" in out and "derived value was 231" in out
    # the manifest check used the OVERRIDE (3 records + header parsed clean)
    assert "manifest carries 3 real record(s)" in out
    assert rc == 0


def test_RED_cli_stage_a_requires_gate_json(tmp_path):
    """The sidecar is the shipped gate's OWN measurement; without it the verifier
    could only re-assert a number a human typed. REQUIRED, no skip."""
    panel = _region1_panel(tmp_path)
    manifest = _manifest(tmp_path)
    npz = _good_npz(tmp_path)
    with pytest.raises(SystemExit) as e:
        fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
                 "--manifest", str(manifest), "--npz", str(npz),
                 "--excludelist", str(_excludelist(tmp_path))])
    assert e.value.code == 2


def test_RED_cli_stage_a_absent_gate_json_fails_closed(tmp_path):
    """A sidecar that is not there is not evidence -> FAIL CLOSED, not a pass."""
    panel = _region1_panel(tmp_path)
    manifest = _manifest(tmp_path)
    npz = _good_npz(tmp_path)
    rc = fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
                 "--manifest", str(manifest), "--npz", str(npz),
                 "--gate-json", str(tmp_path / "nope.occlusion_gate.json"),
                 "--excludelist", str(_excludelist(tmp_path))])
    assert rc == 1


def test_RED_cli_stage_a_requires_npz(tmp_path):
    panel = _region1_panel(tmp_path)
    manifest = _manifest(tmp_path)
    with pytest.raises(SystemExit) as e:
        fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
                 "--manifest", str(manifest),
                 "--gate-json", str(_gate_json(tmp_path)),
                 "--excludelist", str(_excludelist(tmp_path))])
    assert e.value.code == 2, "a falsification that did not run is not a falsification"


def test_RED_cli_stage_a_unknown_region_fails_closed(tmp_path):
    panel = _region1_panel(tmp_path)
    manifest = _manifest(tmp_path)
    npz = _good_npz(tmp_path)
    rc = fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_99999",
                  "--manifest", str(manifest), "--npz", str(npz),
                  "--gate-json", str(_gate_json(tmp_path)),
                  "--excludelist", str(_excludelist(tmp_path))])
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
                       n_dropped_occluded=231, n_dropped_monomorphic=0)]
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
    manifest = _manifest(tmp_path, n_records=231)
    npz = _whole_row_nan_npz(tmp_path)
    report = tmp_path / "stage_a.json"
    fv.main(["stage-a", "--panel-tsv", str(panel), "--region-id", "m2_region_00001",
             "--manifest", str(manifest), "--npz", str(npz),
             "--gate-json", str(_gate_json(tmp_path)),
             "--excludelist", str(_excludelist(tmp_path)), "--report", str(report)])
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


# --------------------------------------------------------------------------- #
# P3 (quick-260918-qz5) — `raised_nan:` IS ITS OWN CLASS                      #
# --------------------------------------------------------------------------- #
# Carter's 2026-09-18 decision: the raise stands, the region banks NOTHING, the
# loop continues (the pre-registered T1 contract executing), with a stop reserved
# for an UNCLASSIFIED raise. The verifier must therefore be able to say "a raise
# happened, here is which region, and it banked nothing" WITHOUT either
#   (a) calling it a deferral — which would route it to the PASS-as-"the gates
#       working" branch the adjudication disqualified, or
#   (b) lumping it with `error:`/`verify_failed` — which would misattribute the
#       pre-registered contract executing as an operational failure.

#: A REAL raise in the shape P2 emits it (the frozen reader's head + the ranked
#: NaN source rows). Copied from a MEASURED producer run, not from memory.
REAL_RAISED_NAN = (
    "raised_nan: square LD carries NaN for /scratch/m2_region_00057.ld.bin: "
    "likely source variant row(s) ranked by NaN count [index: 3, 0, 1, 2, 4...] "
    "— plink --r writes 0/0 -> NaN for a zero-variance variant")


def test_status_class_raised_nan_is_its_own_class():
    """T2.6 — not ok, not a deferral, not a failure, not unknown."""
    cls = fv._status_class(REAL_RAISED_NAN)
    assert cls == fv.STATUS_RAISED_NAN
    for other in (fv.STATUS_OK, fv.STATUS_DEFERRAL, fv.STATUS_FAILURE,
                  fv.STATUS_UNKNOWN):
        assert cls != other, other
    # the bare prefix classifies too (the ast enforcer extracts `raised_nan: `)
    assert fv._status_class("raised_nan: ") == fv.STATUS_RAISED_NAN


def test_classify_statuses_counts_raises_SEPARATELY_from_failures():
    """T2.7 — n_raised_nan and n_failed are reported separately, their region
    lists are DISJOINT, and a raise is counted in neither n_ok nor n_deferred."""
    rows = [
        {"region_id": "r1", "status": "ok"},
        {"region_id": "r2", "status": "ok"},
        {"region_id": "r57", "status": REAL_RAISED_NAN},
        {"region_id": "r9", "status": REAL_ERROR},
    ]
    c = fv.classify_statuses(rows)
    m = c.measured
    assert m["n_raised_nan"] == 1, m
    assert m["n_failed"] == 1, m
    assert m["n_ok"] == 2 and m["n_deferred"] == 0, m
    assert m["raised_nan_regions"] == ["r57"], m
    assert m["failed_regions"] == ["r9"], m
    assert not set(m["raised_nan_regions"]) & set(m["failed_regions"])
    # THE SUM IDENTITY (B2): the five classes must account for every row
    assert (m["n_ok"] + m["n_deferred"] + m["n_raised_nan"] + m["n_failed"]
            + m["n_unknown"]) == m["n_rows"] == 4, m


def test_classify_statuses_a_raise_alone_does_not_populate_the_failure_list():
    """T2.7b — a panel of [ok, raised_nan] must not report a FAILURE state: the
    region banked nothing, but that is the contract executing, not an operational
    failure."""
    rows = [{"region_id": "r1", "status": "ok"},
            {"region_id": "r57", "status": REAL_RAISED_NAN}]
    c = fv.classify_statuses(rows)
    assert c.measured["failed_regions"] == [], c.measured
    assert c.measured["n_raised_nan"] == 1


def test_classify_statuses_PASS_detail_drops_the_gates_working_clause_on_a_raise():
    """T2.7c — ⚠ B2, the framing defect this change exists to stop. Left alone, a
    panel of [ok, raised_nan] printed "1 ok-class + 0 deferred row(s) of 2, ALL
    recognized (THE GATES WORKING; do NOT 'fix' a deferral mid-fire ...)" — the
    raise INVISIBLE in the counts and framed as the gates working, at every
    check-in for ~9 days. That is the exact framing the adjudication disqualified.

    CONTROL (below): on a ZERO-raise panel the original "the gates working"
    sentence must survive VERBATIM, so the fix cannot silently delete the shipped
    deferral guidance."""
    raise_rows = [{"region_id": "r1", "status": "ok"},
                  {"region_id": "r57", "status": REAL_RAISED_NAN}]
    c = fv.classify_statuses(raise_rows)
    assert c.ok, c.detail          # a raise alone is not this check's FAIL
    # the DISQUALIFIED FRAMING, pinned by its exact shipped shape rather than by
    # the loose substring "the gates working" — a negative literal assertion that
    # a nearby innocent phrase can satisfy or break is the trap recorded in
    # [[reference_enforcement_traps_literals_and_linenumbers]]
    assert "ALL recognized (the gates" not in c.detail, c.detail
    assert "do NOT 'fix' a deferral mid-fire" not in c.detail, c.detail
    assert "raised-NaN" in c.detail or "raised_nan" in c.detail, c.detail
    assert "raised_nan_contract_fired" in c.detail, c.detail
    assert "NOT a deferral" in c.detail, c.detail
    # the five counts are NAMED in the detail and reconcile to n_rows
    assert "= 2 row(s)" in c.detail, c.detail

    # --- CONTROL: zero raises -> the shipped sentence is untouched ---
    clean = [{"region_id": "r1", "status": "ok"},
             {"region_id": "r2", "status": REAL_INFEASIBLE}]
    c2 = fv.classify_statuses(clean)
    assert c2.ok, c2.detail
    assert "the gates working" in c2.detail, c2.detail
    assert "do NOT 'fix' a deferral mid-fire" in c2.detail, c2.detail
    assert "raised" not in c2.detail.lower(), c2.detail


def test_raised_nan_contract_fired_is_a_FINDING_naming_the_regions():
    """T2.8 — a panel of ONLY ok + raised_nan rows does NOT pass as "the gates
    working": a separate check reports the raise as a FINDING with its own count
    and region list. THREE distinct checks exist precisely so no disposition can
    hide another (one Check can only report its first failing condition)."""
    rows = [{"region_id": "r1", "status": "ok"},
            {"region_id": "m2_region_00057", "status": REAL_RAISED_NAN}]
    c = fv.check_raised_nan_findings(rows)
    assert not c.ok, c.detail
    assert c.name == "raised_nan_contract_fired"
    assert c.severity == fv.FINDING
    assert "m2_region_00057" in c.detail, c.detail
    assert c.measured["n_raised_nan"] == 1, c.measured
    # the wording carries the posture, so a check-in reader cannot misread it
    for phrase in ("banked", "loop continues", "UNCLASSIFIED"):
        assert phrase.lower() in c.detail.lower(), (phrase, c.detail)
    # CONTROL: a raise-free panel PASSES this check
    c2 = fv.check_raised_nan_findings([{"region_id": "r1", "status": "ok"}])
    assert c2.ok, c2.detail


def test_check_region1_status_findings_on_a_raise():
    """T2.9 — RECORDED NON-CHANGE: region 1 runs under --fail-fast, which raises
    on ANY non-'ok' status, so check_region1_status needed no logic change."""
    c = fv.check_region1_status(REAL_RAISED_NAN)
    assert not c.ok, c.detail
    assert "raised_nan" in c.detail


def test_cost_denominator_a_raise_is_unbankable_but_not_an_operational_failure():
    """T2.10 — D6, the decision the brief asked for. A `raised_nan:` row is NOT
    bankable (it banked no .npz, and cost-per-BANKABLE-region is the gate's whole
    purpose) and NOT an operational failure (calling the pre-registered contract
    executing a "failure" misattributes it). The message must let a human separate
    the two reasons, because COST-1 is ALREADY invalidated by one deferral
    (00071 at n_var 169,803) and conflating the causes would hide that."""
    c = fv.check_cost_denominator(n_regions_used=3, n_bankable=2, n_total=276,
                                  n_raised_nan=1, n_deferred=0, n_failed=0)
    assert c.measured["raised_nan"] == 1, c.measured
    assert c.measured["bankable"] == 2, c.measured   # ok-class ONLY
    # The PROPERTY, not a bare word: the detail must attribute this unbankable row
    # to the NaN contract AND state the operational-failure count separately, so a
    # human can tell which one moved.
    assert "1 raised-NaN" in c.detail, c.detail
    assert "0 operational failure(s)" in c.detail, c.detail
    assert "NOT an operational failure" in c.detail, c.detail

    # CONTROL: the same shape with the raise replaced by an operational failure
    # attributes it to the FAILURE count, not the raise count. Without this the
    # assertions above could not tell a two-reason message from a one-reason one.
    c2 = fv.check_cost_denominator(n_regions_used=3, n_bankable=2, n_total=276,
                                   n_raised_nan=0, n_deferred=0, n_failed=1)
    assert c2.measured["failed"] == 1 and c2.measured["raised_nan"] == 0, c2.measured
    assert "0 raised-NaN" in c2.detail, c2.detail
    assert "1 operational failure(s)" in c2.detail, c2.detail
    assert c.detail != c2.detail, "the two reasons must be distinguishable"


def test_cost_denominator_three_positional_signature_is_unchanged():
    """T2.10b — every pre-existing 3-positional call site and test must be
    BYTE-UNCHANGED: the new parameters are keyword-only with 0 defaults."""
    assert fv.check_cost_denominator(247, 247, 276).ok
    c = fv.check_cost_denominator(276, 247, 276)
    assert not c.ok
    assert c.measured["raised_nan"] == 0 and c.measured["deferred"] == 0
    assert c.measured["failed"] == 0


def test_status_vocabulary_covers_the_measured_eight_sites():
    """T2.11 — the M6 table EXTENDED to the eighth emission site."""
    for prefix, want in [
        ("skipped_idempotent", fv.STATUS_OK),
        ("ok", fv.STATUS_OK),
        ("error", fv.STATUS_FAILURE),
        ("error: ", fv.STATUS_FAILURE),
        ("verify_failed", fv.STATUS_FAILURE),
        ("deferred_infeasible_square: n_var=", fv.STATUS_DEFERRAL),
        ("deferred_occlusion_anomaly: ", fv.STATUS_DEFERRAL),
        ("raised_nan: ", fv.STATUS_RAISED_NAN),
    ]:
        assert fv._status_class(prefix) == want, prefix


# --------------------------------------------------------------------------- #
# P4 (quick-260918-qz5) — STATEFUL stage-C check-in semantics (--prev-report)  #
# --------------------------------------------------------------------------- #
# Under the adopted posture ONE raise would otherwise make EVERY remaining Stage C
# check-in exit 1 for the remaining ~9 days. A gate that is always red is a gate no
# one reads — so the gate becomes stateful: exit 1 means something NEW failed SINCE
# THE LAST CHECK-IN. The acknowledged set is FILE-based and explicit, never hidden
# state, and every degenerate input FAILS CLOSED.

import hashlib      # noqa: E402  (P4: the aliasing guard is pinned on the FILE)
import subprocess   # noqa: E402  (the skip-count enforcer shells out)


def _md5(p: Path) -> str:
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def _stage_c(panel, report=None, prev=None):
    """Run stage-c through the real CLI, returning (rc, stdout)."""
    import io
    import contextlib
    argv = ["stage-c", "--panel-tsv", str(panel)]
    if report is not None:
        argv += ["--report", str(report)]
    if prev is not None:
        argv += ["--prev-report", str(prev)]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fv.main(argv)
    return rc, buf.getvalue()


def test_stateful_checkin_sequence_end_to_end(tmp_path):
    """T3.1 — the four-step sequence the operator actually performs.

    (ii) is the whole point, and note what it does NOT mean: the raise is still
    REPORTED and still COUNTED. "Acknowledged" must never mean "hidden" — that
    would trade an always-red gate for a lying one."""
    p1 = _write_panel(tmp_path, [_panel_row("r1", n_var=100),
                                 _panel_row("r57", n_var=8000,
                                            status=REAL_RAISED_NAN)],
                      name="p1.tsv")
    A = tmp_path / "A.json"
    B = tmp_path / "B.json"
    C = tmp_path / "C.json"

    # (i) first check-in, no prev report -> RED
    rc, out = _stage_c(p1, report=A)
    assert rc == 1, out
    assert "r57" in out, out

    # (ii) the SAME panel, acknowledged against A -> GREEN, still reported+counted
    rc, out = _stage_c(p1, report=B, prev=A)
    assert rc == 0, out
    assert "r57" in out, "an acknowledged raise must still be REPORTED"
    rep = json.loads(B.read_text())
    entry = [e for e in rep["report"] if e["name"] == "status_classification"][0]
    assert entry["measured"]["n_raised_nan"] == 1, entry["measured"]
    assert entry["measured"]["raised_nan_regions"] == ["r57"], entry["measured"]

    # (iii) a SECOND raising region -> RED, naming ONLY the new one
    p2 = _write_panel(tmp_path, [_panel_row("r1", n_var=100),
                                 _panel_row("r57", n_var=8000,
                                            status=REAL_RAISED_NAN),
                                 _panel_row("r99", n_var=9000,
                                            status=REAL_RAISED_NAN)],
                      name="p2.tsv")
    rc, out = _stage_c(p2, report=C, prev=B)
    assert rc == 1, out
    newc = [e for e in json.loads(C.read_text())["report"]
            if e["name"] == "new_failures_since_last_checkin"][0]
    assert newc["measured"]["new_regions"] == ["r99"], newc["measured"]
    assert "r99" in newc["detail"], newc["detail"]

    # (iv) a NEW error: region against (iii)'s report -> RED, naming only it
    p3 = _write_panel(tmp_path, [_panel_row("r1", n_var=100),
                                 _panel_row("r57", n_var=8000,
                                            status=REAL_RAISED_NAN),
                                 _panel_row("r99", n_var=9000,
                                            status=REAL_RAISED_NAN),
                                 _panel_row("r5", status=REAL_ERROR)],
                      name="p3.tsv")
    rc, out = _stage_c(p3, report=tmp_path / "D.json", prev=C)
    assert rc == 1, out
    newc = [e for e in json.loads((tmp_path / "D.json").read_text())["report"]
            if e["name"] == "new_failures_since_last_checkin"][0]
    assert newc["measured"]["new_regions"] == ["r5"], newc["measured"]


def test_a_disappeared_row_is_a_HARD_STOP_with_the_rotation_remedy(tmp_path):
    """T3.2 + T3.5c — the panel TSV is append-only and deduped, so an
    acknowledged region that VANISHED means truncation or replacement. That can
    never be a silent pass.

    W3 — and the message must carry its REMEDY, because the innocent route in is
    ordinary: the shipped stale-header error tells the operator to rotate the
    panel TSV, after which EVERY acknowledged region has "disappeared"."""
    p1 = _write_panel(tmp_path, [_panel_row("r1"), _panel_row(
        "r57", n_var=8000, status=REAL_RAISED_NAN)], name="p1.tsv")
    A = tmp_path / "A.json"
    _stage_c(p1, report=A)
    rotated = _write_panel(tmp_path, [_panel_row("r1")], name="rotated.tsv")
    rc, out = _stage_c(rotated, report=tmp_path / "B.json", prev=A)
    assert rc == 1, out
    e = [x for x in json.loads((tmp_path / "B.json").read_text())["report"]
         if x["name"] == "new_failures_since_last_checkin"][0]
    assert e["severity"] == fv.HARD_STOP, e
    assert "r57" in e["detail"], e["detail"]
    assert "append-only" in e["detail"], e["detail"]
    assert "without `--prev-report`" in e["detail"] or \
           "without --prev-report" in e["detail"], e["detail"]
    assert "re-mint" in e["detail"], e["detail"]


def test_an_unknown_status_is_NEVER_acknowledgeable(tmp_path):
    """T3.3 — D8. An unknown status is a VOCABULARY DEFECT, not a region outcome:
    acknowledging it is precisely how a new failure mode would enter unnoticed,
    which is the reason that branch exists at all."""
    p = _write_panel(tmp_path, [_panel_row("r1"),
                                _panel_row("rX", status="banana")], name="p.tsv")
    A = tmp_path / "A.json"
    rc, _ = _stage_c(p, report=A)
    assert rc == 1
    # A now lists rX among the unknown regions; re-check against it anyway
    assert "rX" in json.loads(A.read_text())["report"][0]["measured"][
        "unknown_regions"]
    rc2, out2 = _stage_c(p, report=tmp_path / "B.json", prev=A)
    assert rc2 == 1, out2
    e = [x for x in json.loads((tmp_path / "B.json").read_text())["report"]
         if x["name"] == "status_classification"][0]
    assert e["severity"] == fv.HARD_STOP, e
    assert "UNRECOGNIZED" in e["detail"], e["detail"]


def test_no_prev_report_exit_codes_match_the_MEASURED_base_table(tmp_path):
    """T3.4 — WITHOUT --prev-report the exit code is IDENTICAL to the MEASURED
    BASE table, with EXACTLY ONE deliberate, recorded exception.

    The `BASE exit` column below was MEASURED in a --shared clone checked out at
    BASE b6076b2 (banked in $SCRATCH/stage_c_base_exit_codes.txt), not guessed —
    the first draft of this plan GUESSED it and was wrong for the header-only row,
    which is the row that turned out to matter."""
    table = [
        # (label, rows, BASE exit measured, required POST exit)
        ("[ok]", [_panel_row("r1")], 0, 0),
        ("[ok + real deferral]",
         [_panel_row("r1"), _panel_row("r2", status=REAL_INFEASIBLE)], 0, 0),
        ("[verify_failed]", [_panel_row("r1", status="verify_failed")], 1, 1),
        ("[error: boom]", [_panel_row("r1", status="error: boom")], 1, 1),
        ("[banana]", [_panel_row("r1", status="banana")], 1, 1),
        ("[<empty status>]", [_panel_row("r1", status="")], 1, 1),
        # ⚠ THE ONE DELIBERATE CHANGE (D7e / W2): a header-only panel PASSED
        # vacuously at BASE, printing "ALL recognized (the gates working)" over
        # ZERO rows, while _stage_b already refused the same input.
        ("[header-only, 0 rows]", [], 0, 1),
    ]
    for i, (label, rows, base_exit, want) in enumerate(table):
        p = _write_panel(tmp_path, rows, name=f"t34_{i}.tsv")
        rc, out = _stage_c(p)
        assert rc == want, f"{label}: expected {want}, got {rc}\n{out}"
        if label == "[header-only, 0 rows]":
            # the ONE deliberate change: BASE 0 -> POST 1. It early-returns with
            # ONLY the zero-row check, which is correct — with no rows there is
            # nothing for the raise checks to classify.
            assert base_exit == 0 and want == 1, label
            assert "stage_c_zero_data_rows" in out, out
            continue
        assert rc == base_exit, f"{label}: BASE said {base_exit}, POST gave {rc}"
        # the two new raise checks are PRESENT but SILENT on a raise-free panel:
        # they are NAMED in the rollup (so the operator sees they ran) and they
        # report ZERO raises. (The plan asked for "no raised_nan string in the
        # output", which is unsatisfiable: the checks' own NAMES contain it, and
        # naming a check that ran is the opposite of a defect.)
        assert "raised_nan_contract_fired" in out, out
        assert "raised_nan_class_coverage" in out, out
        assert "0 raised-NaN row(s)" in out, out
        assert "no raised_nan: rows" in out, out


def test_a_header_only_panel_does_not_pass_vacuously(tmp_path):
    """T3.4b — W2. Closed in _stage_c (MANDATED: classify_statuses is called by
    stage-a, stage-b AND stage-c, so putting it there would silently change two
    OTHER fire-path gates' report shape).

    The message must LIST the five routes in and assert none of them, because
    four of the five are innocent — including day one, before the first region
    appends its row."""
    p = _write_panel(tmp_path, [], name="empty.tsv")
    rc, out = _stage_c(p, report=tmp_path / "R.json")
    assert rc == 1, out
    e = [x for x in json.loads((tmp_path / "R.json").read_text())["report"]
         if x["name"] == "stage_c_zero_data_rows"][0]
    assert e["severity"] == fv.HARD_STOP, e
    # the _stage_b wording precedent, so the two gates agree (anchor C3)
    assert "a check with no input must FAIL" in e["detail"], e["detail"]
    assert "not pass vacuously" in e["detail"], e["detail"]
    # the five routes in
    for route in ("first row", "rotated", "not atomic", "truncated", "overwrite"):
        assert route in e["detail"], (route, e["detail"])

    # CONTROL: ONE data row and the condition does not fire (a legitimately early
    # panel is not an error)
    p1 = _write_panel(tmp_path, [_panel_row("r1")], name="one.tsv")
    rc1, out1 = _stage_c(p1, report=tmp_path / "R1.json")
    assert rc1 == 0, out1
    names = [x["name"] for x in json.loads((tmp_path / "R1.json").read_text())["report"]]
    assert "stage_c_zero_data_rows" not in names, names


def test_prev_report_fail_closed_cases_carry_their_remedy(tmp_path):
    """T3.5 — each FAILS CLOSED at HARD_STOP *with its remedy asserted*. The
    remedy text is only REACHABLE because the loaders RETURN a Check rather than
    raising (W12): a raise would be swallowed by main()'s generic handler into
    "stage_c_driver: the gate could not run (...)" and the specific remedy would
    never print."""
    p = _write_panel(tmp_path, [_panel_row("r1")], name="p.tsv")

    # (a) --prev-report naming a file that does not exist
    rc, out = _stage_c(p, report=tmp_path / "R1.json",
                       prev=tmp_path / "nope.json")
    assert rc == 1, out
    e = [x for x in json.loads((tmp_path / "R1.json").read_text())["report"]
         if x["name"] == "prev_report_loadable"][0]
    assert e["severity"] == fv.HARD_STOP, e
    assert "without --prev-report" in e["detail"], e["detail"]
    assert "mint" in e["detail"], e["detail"]

    # (b) a PRE-CHANGE report shape: valid JSON with acknowledgeable_schema
    #     DELETED. Built by deleting the key from a REAL report, so the fixture
    #     cannot drift from the real shape.
    real = tmp_path / "real.json"
    _stage_c(p, report=real)
    d = json.loads(real.read_text())
    assert d.pop("acknowledgeable_schema", None) is not None, \
        "summarize() must emit the named key, or this fixture is vacuous"
    old = tmp_path / "old.json"
    old.write_text(json.dumps(d))
    rc, out = _stage_c(p, report=tmp_path / "R2.json", prev=old)
    assert rc == 1, out
    e = [x for x in json.loads((tmp_path / "R2.json").read_text())["report"]
         if x["name"] == "prev_report_loadable"][0]
    assert e["severity"] == fv.HARD_STOP, e
    assert "acknowledgeable_schema" in e["detail"], e["detail"]
    assert "without --prev-report" in e["detail"], e["detail"]


def test_an_ALIASED_invocation_leaves_the_prev_report_BYTE_UNCHANGED(tmp_path):
    """T3.5b — ⚠ B3, pinned on the PROPERTY (the FILE), not on the message.

    A HARD_STOP *check* is not enough here: main() writes the report
    UNCONDITIONALLY AFTER the checks run (MEASURED at BASE), so a check that
    merely REPORTS the aliasing would watch the overwrite happen and the
    acknowledged set would be DESTROYED by the very invocation that read it. The
    guard must run BEFORE the checks and return early WITHOUT writing."""
    p = _write_panel(tmp_path, [_panel_row("r1"), _panel_row(
        "r57", n_var=8000, status=REAL_RAISED_NAN)], name="p.tsv")
    R = tmp_path / "R.json"
    _stage_c(p, report=R)
    before = _md5(R)

    rc, out = _stage_c(p, report=R, prev=R)
    assert rc == 1, out
    assert "prev_report_aliasing" in out, out
    assert _md5(R) == before, "the aliased invocation OVERWROTE the prev report"

    # CONTROL 1 — the assertion is not vacuous in the "nothing is ever written"
    # direction: a NON-aliased run DOES write its own report and leaves R alone.
    R2 = tmp_path / "R2.json"
    rc2, _ = _stage_c(p, report=R2, prev=R)
    assert R2.is_file(), "a non-aliased run must still write its report"
    assert _md5(R) == before
    # CONTROL 2 — resolve() semantics: a DIFFERENT SPELLING of the same path is
    # still caught, so a symlink or a `..` cannot slip past the guard.
    sub = tmp_path / "sub"
    sub.mkdir()
    spelled = sub / ".." / "R.json"
    rc3, out3 = _stage_c(p, report=R, prev=spelled)
    assert rc3 == 1 and "prev_report_aliasing" in out3, out3
    assert _md5(R) == before


# --------------------------------------------------------------------------- #
# P5 (quick-260918-qz5) — the CLOSEOUT COVERAGE accounting, on the C7 template #
# --------------------------------------------------------------------------- #

def test_check_raised_nan_coverage_accounts_for_the_class_as_UNCLASSIFIED(tmp_path):
    """T3.6 — it checks PRESENCE, COUNT and the UNCLASSIFIED DEFAULT, and NOTHING
    ELSE. It must not be readable as evidence that any raise has been classified:
    there is NO classification mechanism in the pipeline today (LOW-1, the
    per-region pre-check, is DEFERRED by Carter until COST-1 measures a per-region
    wall time), and the check's own detail has to say so in words."""
    rows = [{"region_id": "r1", "status": "ok", "n_var": 100},
            {"region_id": "m2_region_00057", "status": REAL_RAISED_NAN,
             "n_var": 8000}]
    c = fv.check_raised_nan_coverage(rows)
    assert c.name == "raised_nan_class_coverage"
    assert c.ok, c.detail
    assert c.measured["n_raised_nan"] == 1, c.measured
    assert c.measured["rows"] == [
        {"region_id": "m2_region_00057", "n_var": 8000,
         "classification": "UNCLASSIFIED"}], c.measured
    assert "UNCLASSIFIED" in c.detail
    assert "no classification mechanism" in c.detail.lower(), c.detail
    assert "COST-1" in c.detail, c.detail

    # PASS with an EXPLICIT zero statement on a raise-free panel
    c0 = fv.check_raised_nan_coverage([{"region_id": "r1", "status": "ok"}])
    assert c0.ok and "0 raised-NaN row(s)" in c0.detail, c0.detail

    # FAIL CLOSED: a raise whose n_var is missing cannot enter the closeout
    # distribution — which is the very gap X1 exists to close
    cn = fv.check_raised_nan_coverage(
        [{"region_id": "r57", "status": REAL_RAISED_NAN, "n_var": None}])
    assert not cn.ok and cn.severity == fv.HARD_STOP, cn
    assert "n_var" in cn.detail, cn.detail
    # FAIL CLOSED: a raise with no region_id cannot be accounted for at all
    ci = fv.check_raised_nan_coverage(
        [{"region_id": "", "status": REAL_RAISED_NAN, "n_var": 10}])
    assert not ci.ok and ci.severity == fv.HARD_STOP, ci
    assert "region_id" in ci.detail, ci.detail


def _raised_nan_registered(panel_rows, deferred_items_text) -> bool:
    """THE PREDICATE the live gate below applies: every raised_nan: region in the
    measured panel must be BOTH counted by check_raised_nan_coverage AND named in
    the `## R5-RAISED-NAN` block of deferred-items.md. Extracted so it can be
    exercised on a synthetic tree while the live path is dormant."""
    c = fv.check_raised_nan_coverage(panel_rows)
    block = fv._extract_named_block(deferred_items_text, "R5-RAISED-NAN")
    regions = [r["region_id"] for r in c.measured["rows"]]
    return bool(c.ok) and all(r in block for r in regions)


def test_raised_nan_class_coverage_live_gate_against_the_repo_file():
    """THE NAMED ENFORCER (P5 / D9), on the R4-COVERAGE C7 template.

    THIS SKIP *IS* THE ENFORCER. It fires the moment a measured panel TSV lands
    in-repo, and then stays red until every raised_nan: region in it is registered
    in the `## R5-RAISED-NAN` block of deferred-items.md (the block
    quick-260918-qz0 registered). The skip is guarded against masking three ways,
    exactly as the C7 precedent above: the check function's own green AND red run
    unconditionally against fixtures (T3.6); the PREDICATE is shown able to fail
    AND able to pass on a synthetic tree (the sibling test below); and the
    skip-count move 33 -> 34 is recorded in the SUMMARY and enforced by
    tests/m3/test_fire_runbook_pins.py."""
    panels = fv.find_measured_panel_tsvs(PROJECT_ROOT)
    if not panels:
        pytest.skip(
            f"no measured panel TSV ({rnlp._DEFAULT_PANEL_NAME}) in-repo yet — no "
            f"raised_nan: region can have been measured before the fire. This skip "
            f"IS the enforcer: it fires the moment the artifact lands.")
    disclosure = (PROJECT_ROOT / ".planning" / "phases" / "m3-aou-afr-ld-panel-build"
                  / "deferred-items.md")
    for panel in panels:
        rows = fv.parse_panel_tsv(panel)
        assert _raised_nan_registered(rows, disclosure.read_text()), (
            f"a measured panel TSV exists ({panel}) carrying raised_nan: region(s) "
            f"that are not accounted for in the ## R5-RAISED-NAN block of "
            f"{disclosure}: {fv.check_raised_nan_coverage(rows).detail}")


def test_the_raised_nan_coverage_predicate_is_proven_both_ways_on_a_synthetic_tree(
        tmp_path):
    """T3.7 — the live gate above is DORMANT today, so its LOGIC is proven here,
    in BOTH directions. A skip whose predicate has never been seen to fail is a
    coverage loss dressed as an enforcer."""
    rows = [{"region_id": "r1", "status": "ok", "n_var": 100},
            {"region_id": "m2_region_00057", "status": REAL_RAISED_NAN,
             "n_var": 8000}]
    omits = ("## R4-COVERAGE\nsomething else\n\n"
             "## R5-RAISED-NAN — the obligation\nno region is named here\n")
    assert not _raised_nan_registered(rows, omits), \
        "the predicate PASSED on a deferred-items.md that omits the region"
    lists = ("## R4-COVERAGE\nsomething else\n\n"
             "## R5-RAISED-NAN — the obligation\n"
             "m2_region_00057 (n_var 8000) is registered here\n")
    assert _raised_nan_registered(rows, lists), \
        "the predicate FAILED even though the region IS registered"
    # and the block extractor is not vacuous: a RENAMED heading yields an empty
    # block, so a rename cannot silently satisfy the membership test
    assert fv._extract_named_block(lists, "R5-RAISED-NAN-RENAMED") == ""
    assert not _raised_nan_registered(
        rows, lists.replace("R5-RAISED-NAN", "R5-RENAMED"))
