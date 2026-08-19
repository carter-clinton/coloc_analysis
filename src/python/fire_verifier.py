"""Fire-stage mechanical gates for the AFR native-plink LD panel fire.

ONE command, run on the AoU Cloud Analysis VM after ``git pull``, that evaluates
the Stage-A / Stage-B / Stage-C invariants and exits non-zero if any of them is
red::

    python3 src/python/fire_verifier.py stage-a --panel-tsv ... --region-id ... \\
        --manifest ... --npz ... --report /home/jupyter/fire_gate_stageA.json
    python3 src/python/fire_verifier.py stage-b --panel-tsv ... --n-total 276
    python3 src/python/fire_verifier.py stage-c --panel-tsv ...
    python3 src/python/fire_verifier.py disclosure --file ...

WHY. The pre-fire checklist was a list a human had to remember. That works at
region 1 with full attention and fails at region 180 at 3am. Everything on it
except the go/no-go decision itself can be made mechanical. Adopted from Seth's
2026-08-18 reference prototype; every check re-adjudicated BY MEASUREMENT against
the shipped producer/converter, with each disagreement resolved in the SHIPPED
code's favour (see ``260818-sml-COURIER-TO-SETH-adjudication.md``, D-01..D-13).

THREE DESIGN RULES (Seth's, kept verbatim because they are sound)
-----------------------------------------------------------------
1. FAIL CLOSED. Missing file, unreadable input, unparseable content, or an
   internal exception => FAIL. A verifier that cannot measure must never pass.
   This is the ``_SUCCESS``-marker lesson expressed in code: absence of evidence
   is FAIL, not PASS.
2. MEASURE THE DATA LAYER, NEVER A MARKER. Row counts come from reading rows;
   panel validity comes from re-reading the panel through the SHIPPED verifier. A
   status string saying "ok" is corroboration, never the measurement.
3. EVERY CHECK PROVEN ABLE TO FAIL before it is trusted. Each check here has at
   least one negative control in ``tests/m3/test_fire_verifier.py`` that was
   DRIVEN RED against this module, with the verbatim output banked in
   ``.planning/quick/260818-sml-.../260818-sml-controls-transcript.txt``.

IT NEVER MAKES THE DECISION. The go/no-go is Carter's; an agent never fires the
loop. These gates make the EVIDENCE for that decision mechanical and fail-closed.
A red is a STOP; it is not a licence to retry or repair.

NO HAND-TRANSCRIBED SHIPPED CONSTANTS. ``_PANEL_COLUMNS``, the clause-(d) anomaly
fraction, the ``--max-n-var`` feasibility ceiling, the default panel-TSV name and
the MED-6 ``.npz`` byte floor are all IMPORTED from the shipped modules and read
at evaluation time. A re-declared copy is a silent divergence with no enforcer.
The only literals in this module are ``_VM_TOTAL_GIB`` (below) and the peak-RAM
headroom fraction.

MEMORY DISCIPLINE. Region 1 is ~102k x 102k float32 = ~42 GB. There is no
``np.isnan(m)`` / ``np.allclose(m, m.T)`` / ``np.triu(m)`` over a full dense
matrix anywhere here: the NaN falsification calls the shipped verifier (which uses
the FROZEN blocked helpers) and, only on an already-failing path, re-loads ONCE to
diagnose with the FROZEN blocked scanner. At most one full array is live at a time.

SEVERITY IS TWO-TIER.
  HARD_STOP — firing further would bank defective or unexplained output.
  FINDING    — scientifically meaningful; needs a human decision, not an auto-abort.
⚠ A-04 NOTE, deliberately recorded here: ``check_region1_status`` fails at FINDING,
not HARD_STOP. That is Seth's judgment call and the runbook's own language ("a
deferral there would itself be the finding"). Flipping it is a ONE-CONSTANT change
(``_REGION1_SEVERITY``) reserved for Carter — and ``exit_code`` is non-zero either
way, so nothing operational rides on the tier.

EGRESS. This module emits counts, booleans, file sizes, row indices and policy
labels. No genotypes, no LD values, no per-sample data. ``nan_variant_indices``
returns ROW INDICES, never LD values. Safe to run in-perimeter and paste out.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Bootstrap src/python on sys.path (mirror run_native_ld_panel.py:90-94) so the
# sibling shipped modules import whether this is invoked as a script or imported.
_SRC_PYTHON = Path(__file__).resolve().parent
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import aou_ld_panel as alp          # noqa: E402  MED-6 .npz byte floor
import plink_ld_to_npz as pln       # noqa: E402  FROZEN blocked NaN helpers
import run_native_ld_panel as rnlp  # noqa: E402  the shipped fire-path producer


# --------------------------------------------------------------------------- #
# Status / severity vocabulary                                                #
# --------------------------------------------------------------------------- #

PASS = "PASS"
FAIL = "FAIL"

HARD_STOP = "HARD_STOP"   # firing further would bank defective/unexplained output
FINDING = "FINDING"       # scientifically meaningful; requires a human decision

#: A-04: the region-1 tier. ONE constant, reserved for Carter (see module docstring).
_REGION1_SEVERITY = FINDING

#: The compute VM's total RAM. Repo-documented, not a guess:
#: ``.planning/debug/m3-producer-unbounded-dense-read.md:17`` — "n1-standard-32,
#: 120 GB". The runbook passes ``--vm-gib`` explicitly so the number is visible at
#: the call site too.
_VM_TOTAL_GIB = 120.0

#: Default RAM headroom demanded of a per-region peak RSS.
_DEFAULT_HEADROOM_FRAC = 0.15


# --------------------------------------------------------------------------- #
# Shipped-constant accessors — read at EVALUATION TIME, never copied           #
# --------------------------------------------------------------------------- #

def _default_occlusion_fraction() -> float:
    """The pre-registered trsx5 clause-(d) anomaly fraction.

    Read as a MODULE GLOBAL off the shipped producer at evaluation time, exactly
    as ``run_native_ld_panel.process_region`` reads it (it is deliberately NOT
    CLI-tunable there: "a knob would invite silent deviation from the public
    commitment"). Never bound as a default argument, never re-declared.
    """
    return rnlp._OCCLUSION_ANOMALY_FRACTION


def _infeasible_ceiling() -> int:
    """The ``--max-n-var`` square-mode feasibility ceiling (shipped default).

    Pinned by ``test_max_n_var_default_pins_consumer_ceiling`` to
    ``config/pipeline.yaml``'s ``m3_convert_max_n_var``.
    """
    return rnlp._DEFAULT_MAX_N_VAR


def _default_min_npz_bytes() -> int:
    """The MED-6 resume-guard byte floor (``aou_ld_panel._MIN_REGION_NPZ_BYTES``)."""
    return alp._MIN_REGION_NPZ_BYTES


def _default_npz_verifier() -> Callable:
    """The SHIPPED pre-upload contents gate, ``content_verify_npz``.

    It re-reads the BANKED ``.npz`` (not the pre-``.npz`` ``.ld.bin``, which is
    deleted after a successful region in gs:// mode) and returns ``(ok, reason)``
    rather than raising. See D-01 in the courier note.
    """
    return rnlp.content_verify_npz


def _default_nan_scanner() -> Callable:
    """FROZEN memory-bounded 'does this matrix contain any NaN' scan."""
    return pln._has_any_nan_blocked


def _default_nan_ranker() -> Callable:
    """FROZEN worst-first NaN source-row ranker (handles the whole-row-NaN-with-
    unit-diagonal fire-#3 fingerprint, where a naive any-NaN scan flags every row).
    """
    return pln.nan_variant_indices


def _panel_artifact_name() -> str:
    """The producer's default panel-TSV filename (``_DEFAULT_PANEL_NAME``)."""
    return rnlp._DEFAULT_PANEL_NAME


# --------------------------------------------------------------------------- #
# Check + fail-closed guard                                                   #
# --------------------------------------------------------------------------- #

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
    """Fail-closed wrapper: any exception becomes a FAIL, never a silent pass.

    The message deliberately makes NO claim about the cause — in particular it
    never attributes an unmeasurable check to a NaN.
    """
    try:
        return fn()
    except Exception as e:  # noqa: BLE001 — that is the point: nothing escapes
        return Check(name, FAIL,
                     f"check could not be evaluated ({type(e).__name__}: {e}) "
                     f"-> FAIL CLOSED (unmeasurable != ok)", severity)


# --------------------------------------------------------------------------- #
# A-05 — parse_panel_tsv is the SINGLE panel-TSV parser                       #
# --------------------------------------------------------------------------- #

def _num_or_none(raw: str, cast) -> Optional[Any]:
    s = (raw or "").strip()
    if s == "":
        return None
    return cast(float(s)) if cast is int else cast(s)


_INT_COLUMNS = ("n_var", "n_dropped_occluded", "n_dropped_monomorphic")
_FLOAT_COLUMNS = ("wall_min", "peak_ram_gib", "output_gib")


def parse_panel_tsv(path: "str | Path") -> List[Dict[str, Any]]:
    """Read the per-region panel TSV -> ``list[dict]``.

    THE single parser: no check anywhere in this module does ad-hoc column
    indexing (a positional ``$5`` in one place and ``$7`` in another is how a
    schema change falsifies provenance silently).

    Contract, mirroring the shipped ``_append_panel_row_local``:
      * the header must be EXACTLY the imported ``_PANEL_COLUMNS`` — REFUSE, never
        repair (a guard that silently repairs HIDES the bug);
      * a ragged row RAISES rather than being coerced;
      * numeric columns are coerced to number-or-None (an empty field is how
        ``pandas.to_csv`` renders ``None``);
      * ``status`` is kept as a RAW string — the real statuses carry detail
        suffixes with spaces, ``=`` and ``>`` inside the field.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"panel TSV not found: {p}")
    with p.open(newline="") as fh:
        rows = list(csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE))
    if not rows:
        raise ValueError(f"panel TSV {p} is EMPTY (not even a header) -> refuse")

    header = rows[0]
    expected = list(rnlp._PANEL_COLUMNS)
    if header != expected:
        raise ValueError(
            f"panel TSV {p} has an UNEXPECTED header and cannot be parsed.\n"
            f"  found:    {header}\n"
            f"  expected: {expected}\n"
            "REFUSE, never repair: parsing under a mismatched header either "
            "aborts or silently shifts every column."
        )

    out: List[Dict[str, Any]] = []
    for lineno, row in enumerate(rows[1:], start=2):
        if not row or all(c.strip() == "" for c in row):
            continue
        if len(row) != len(header):
            raise ValueError(
                f"panel TSV {p} line {lineno} is RAGGED: {len(row)} field(s), "
                f"expected {len(header)} -> refuse (a ragged row is how a stale "
                f"header falsifies every downstream count)"
            )
        rec: Dict[str, Any] = dict(zip(header, row))
        for col in _INT_COLUMNS:
            rec[col] = _num_or_none(rec[col], int)
        for col in _FLOAT_COLUMNS:
            rec[col] = _num_or_none(rec[col], float)
        rec["status"] = rec["status"]  # raw, on purpose
        out.append(rec)
    return out


# --------------------------------------------------------------------------- #
# A-02 — the status allow-list, PREFIX-matched                                #
# --------------------------------------------------------------------------- #

STATUS_OK = "ok_class"
STATUS_DEFERRAL = "deferral_class"
STATUS_FAILURE = "failure_class"
STATUS_UNKNOWN = "unknown"

#: Measured from the shipped producer's SEVEN status emission sites (M2). The
#: real deferral statuses carry a DETAIL SUFFIX, so recognition MUST be prefix-
#: based: an exact-membership test would flag every real deferral as unrecognized
#: and HARD_STOP the fire on the gates working (D-02).
_OK_STATUSES = ("ok", "skipped_idempotent")
_DEFERRAL_PREFIXES = ("deferred_infeasible_square", "deferred_occlusion_anomaly")
_FAILURE_STATUSES = ("verify_failed", "error")
_FAILURE_PREFIXES = ("error:",)


def _status_class(status: Any) -> str:
    """Classify one panel-TSV status string. Unrecognized / empty -> UNKNOWN.

    The enforcer that keeps this allow-list honest is
    ``tests/m3/test_fire_verifier.py::test_shipped_status_vocabulary_is_covered_by_the_allow_list``:
    it walks the SHIPPED producer with ``ast`` and asserts every constant status
    prefix it can emit classifies here. A status added tomorrow makes that RED.
    """
    s = ("" if status is None else str(status)).strip()
    if s == "":
        return STATUS_UNKNOWN
    if s in _OK_STATUSES:
        return STATUS_OK
    for prefix in _DEFERRAL_PREFIXES:
        if s.startswith(prefix):
            return STATUS_DEFERRAL
    if s in _FAILURE_STATUSES:
        return STATUS_FAILURE
    for prefix in _FAILURE_PREFIXES:
        if s.startswith(prefix):
            return STATUS_FAILURE
    return STATUS_UNKNOWN


def classify_statuses(status_rows: List[Dict[str, Any]]) -> Check:
    """Classify every panel row's status.

    Dispositions (A-02):
      * ok-class (``ok`` / ``skipped_idempotent``)          -> PASS
      * deferral-class (prefix-matched)                     -> PASS. Deferred rows
        are THE GATES WORKING; never "fix" one mid-fire.
      * failure-class (``verify_failed`` / ``error``/``error:``) -> FAIL at FINDING.
        A region that banked NOTHING is not the gates working — but Stage C runs
        without ``--fail-fast``, so the loop legitimately continues and the correct
        response is report-to-Carter, not an auto-abort.
      * anything else, and any EMPTY status                 -> FAIL at HARD_STOP.
        An unknown status silently treated as ok is how a new failure mode enters
        unnoticed.
    """
    def run() -> Check:
        n = "status_classification"
        counts: Dict[str, int] = {}
        by_class: Dict[str, int] = {STATUS_OK: 0, STATUS_DEFERRAL: 0,
                                    STATUS_FAILURE: 0, STATUS_UNKNOWN: 0}
        unknown: List[str] = []
        failures: List[str] = []
        for r in status_rows:
            raw = r.get("status", "")
            key = ("<empty status>" if str(raw).strip() == "" else str(raw).strip())
            counts[key] = counts.get(key, 0) + 1
            cls = _status_class(raw)
            by_class[cls] += 1
            if cls == STATUS_UNKNOWN:
                unknown.append(key)
            elif cls == STATUS_FAILURE:
                failures.append(key)

        measured = {
            "counts": counts,
            "n_rows": len(status_rows),
            "n_ok": by_class[STATUS_OK],
            "n_deferred": by_class[STATUS_DEFERRAL],
            "n_failed": by_class[STATUS_FAILURE],
            "n_unknown": by_class[STATUS_UNKNOWN],
        }

        if unknown:
            return Check(
                n, FAIL,
                f"UNRECOGNIZED status value(s) {sorted(set(unknown))} in "
                f"{len(status_rows)} row(s) -> an unknown status must NEVER be "
                f"treated as ok. Either the producer gained a status the gate does "
                f"not know, or the panel TSV is corrupt. HARD STOP.",
                HARD_STOP, measured)

        if failures:
            return Check(
                n, FAIL,
                f"{len(failures)} row(s) in a FAILURE state {sorted(set(failures))} "
                f"of {len(status_rows)} -> those regions banked NOTHING. Stage C "
                f"runs without --fail-fast so the loop continues by design; report "
                f"these to Carter with their per-region statuses. Do NOT re-fire "
                f"blindly.",
                FINDING, measured)

        return Check(
            n, PASS,
            f"{by_class[STATUS_OK]} ok-class + {by_class[STATUS_DEFERRAL]} "
            f"deferred row(s) of {len(status_rows)}, ALL recognized (the gates "
            f"working; do NOT 'fix' a deferral mid-fire — a region above the "
            f"n_var ceiling of {_infeasible_ceiling()} defers by design)",
            HARD_STOP, measured)

    return _guard("status_classification", HARD_STOP, run)


# --------------------------------------------------------------------------- #
# STAGE A — mechanism falsification (the scientific gate, not a smoke test)   #
# --------------------------------------------------------------------------- #

_NAN_VERDICT = "occlusion is NOT the sole NaN mechanism"


def check_nan_falsification(npz_path: "str | Path", *,
                            verifier: Optional[Callable] = None,
                            nan_scanner: Optional[Callable] = None,
                            ranker: Optional[Callable] = None,
                            min_bytes: Optional[int] = None,
                            mode: str = "square") -> Check:
    """The BANKED region-1 panel must contain zero NaN — verified, not asserted.

    Order (A-01), shipped path first and diagnosis second:

    1. missing file -> FAIL closed; below the MED-6 byte floor -> FAIL closed.
    2. call the SHIPPED ``content_verify_npz`` (never a re-implementation). It
       re-reads the BANKED ``.npz``, which is the artifact that survives the fire
       (the pre-``.npz`` ``.ld.bin`` the frozen ``read_square_bin`` consumes is
       deleted after a successful region in gs:// mode). ``ok=True`` -> PASS: the
       shipped pre-upload verification re-read this object, and ok therefore
       entails NaN-free. That implication is PINNED by fixture tests
       (``test_shipped_verifier_rejects_both_nan_fixtures``), not argued.
    3. ``ok=False`` -> load the array ONCE MORE and run the FROZEN blocked scanner.
       NaN present -> HARD_STOP naming NaN and the ranked SOURCE rows. NaN absent
       -> HARD_STOP carrying the shipped ``reason`` verbatim and explicitly NOT
       claiming NaN. This matters: the shipped verifier detects NaN only
       INDIRECTLY and reports it as ``"not symmetric"`` — exactly the
       misattribution the frozen reader's own comment warns against.
    4. any exception -> FAIL closed, with no NaN attribution.

    Memory-bounded: at most one full array is live, and the second load happens
    ONLY on the already-failing path.
    """
    verifier = _default_npz_verifier() if verifier is None else verifier
    nan_scanner = _default_nan_scanner() if nan_scanner is None else nan_scanner
    ranker = _default_nan_ranker() if ranker is None else ranker
    floor = _default_min_npz_bytes() if min_bytes is None else min_bytes

    def run() -> Check:
        n = "stage_a_nan_falsification"
        p = str(npz_path)
        if not os.path.exists(p):
            return Check(n, FAIL,
                         f"banked panel absent: {p} -> cannot falsify (a "
                         f"falsification that did not run is not a falsification)",
                         HARD_STOP)
        size = os.path.getsize(p)
        if size < floor:
            return Check(n, FAIL,
                         f"panel is {size} B, below the shipped MED-6 floor of "
                         f"{floor} B -> empty/truncated bank, cannot falsify",
                         HARD_STOP, {"bytes": size})

        ok, reason = verifier(p, mode=mode)
        if ok:
            return Check(n, PASS,
                         f"the SHIPPED content verification re-read the banked "
                         f".npz ({size} B) and returned ok -> the region carries no "
                         f"NaN; occlusion accounted for 100% of the region-1 NaN "
                         f"(shipped reason: {reason})",
                         HARD_STOP, {"bytes": size})

        # --- FAILING PATH ONLY: one extra load, to DIAGNOSE ------------------
        try:
            import numpy as np  # local: keep the happy path free of the import
            with np.load(p, allow_pickle=True) as z:
                ld = z["ld"]
                has_nan = bool(nan_scanner(ld))
                src_rows = [int(i) for i in ranker(ld)] if has_nan else []
        except Exception as e:  # noqa: BLE001
            return Check(n, FAIL,
                         f"the SHIPPED content verification FAILED. Reason "
                         f"(verbatim): {reason!r}. The follow-up diagnosis could "
                         f"not run ({type(e).__name__}: {e}), so NO cause is "
                         f"attributed here -- diagnose the reported reason.",
                         HARD_STOP, {"bytes": size, "shipped_reason": reason})

        if has_nan:
            preview = ", ".join(str(i) for i in src_rows[:10])
            return Check(n, FAIL,
                         f"the banked panel STILL CARRIES NaN after occlusion "
                         f"filtering: likely source variant row(s) ranked "
                         f"worst-first [{preview}]. {_NAN_VERDICT} -> HARD STOP. Do "
                         f"not fire the remaining regions; an unexplained defect "
                         f"class would be banked. (The shipped verifier reported "
                         f"this as {reason!r} — it detects NaN only indirectly.)",
                         HARD_STOP,
                         {"bytes": size, "shipped_reason": reason,
                          "nan_source_rows": src_rows})

        return Check(n, FAIL,
                     f"the SHIPPED content verification FAILED. Reason (verbatim): "
                     f"{reason!r}. The frozen blocked scan found ZERO null entries, "
                     f"so this is NOT attributed to a residual occlusion mechanism "
                     f"-> HARD STOP and diagnose the reported reason.",
                     HARD_STOP, {"bytes": size, "shipped_reason": reason})

    return _guard("stage_a_nan_falsification", HARD_STOP, run)


def check_manifest_rows(manifest_path: "str | Path", expected_records: int = 5,
                        *, region_id: Optional[str] = None,
                        expect_header: bool = True) -> Check:
    """Region-1 occlusion-manifest ground truth: real rows, never an upload marker.

    Region 1 is the ONLY region with a known answer (5 occluded), so it is the one
    chance to validate the manifest writer against ground truth.

    A-10: the row COUNT is not sufficient. The shipped writer emits a ``region_id``
    column (``occlusion_manifest.STAGE_A_COLUMNS[0]``), and the runbook's own
    expectation is "region_id m2_region_00001 on every record row" — so this
    asserts the value, not merely the arithmetic. Right count / wrong content is
    the exact defect class that cost this project $2,140 once.
    """
    def run() -> Check:
        n = "stage_a_manifest_rows"
        p = Path(manifest_path)
        if not p.is_file():
            return Check(n, FAIL, f"manifest absent: {p} -> FAIL CLOSED", HARD_STOP)
        lines = [ln for ln in p.read_text().splitlines() if ln.strip() != ""]
        want = expected_records + (1 if expect_header else 0)
        if len(lines) != want:
            return Check(n, FAIL,
                         f"manifest has {len(lines)} non-empty line(s), expected "
                         f"{want} (header + {expected_records} records)",
                         HARD_STOP, {"lines": len(lines), "expected": want})

        header = lines[0].split("\t") if expect_header else []
        body = lines[1:] if expect_header else lines
        if any(len(r.split("\t")) < 2 for r in body):
            return Check(n, FAIL,
                         "manifest rows are not parseable as multi-field records "
                         "-> the writer emitted placeholder/marker content at the "
                         "right line count (the _SUCCESS-marker defect class)",
                         HARD_STOP, {"records": len(body)})

        if region_id is not None:
            if "region_id" not in header:
                return Check(n, FAIL,
                             f"manifest header {header} carries no region_id column "
                             f"-> cannot validate ownership of the records",
                             HARD_STOP, {"records": len(body)})
            idx = header.index("region_id")
            observed = sorted({r.split("\t")[idx] for r in body})
            if observed != [region_id]:
                return Check(n, FAIL,
                             f"manifest record rows carry region_id(s) {observed}, "
                             f"expected every row to be {region_id!r} -> the "
                             f"manifest does not belong to the region under test",
                             HARD_STOP,
                             {"records": len(body), "region_ids": observed})

        return Check(n, PASS,
                     f"manifest carries {len(body)} real record(s) + header, fields "
                     f"parseable"
                     + (f", every record row region_id={region_id!r}"
                        if region_id is not None else ""),
                     HARD_STOP, {"records": len(body)})

    return _guard("stage_a_manifest_rows", HARD_STOP, run)


def check_occlusion_ceiling(n_occluded: Optional[int], n_var: Optional[int],
                            frac: Optional[float] = None) -> Check:
    """Pre-registered trsx5 clause (d): defer when the occluded count STRICTLY
    EXCEEDS ``frac * n_var``.

    Reproduces the shipped comparison exactly — FLOAT ceiling, STRICT ``>`` (clause
    (d) says "exceeds", so count == ceiling stays on the exclude-in-lockstep path)
    — and reads the fraction from the shipped module global at evaluation time.
    """
    def run() -> Check:
        n = "occlusion_anomaly_ceiling"
        f = _default_occlusion_fraction() if frac is None else frac
        ceiling = f * n_var
        measured = {"n_occluded": n_occluded, "ceiling": ceiling, "n_var": n_var,
                    "frac": f}
        if n_occluded > ceiling:
            return Check(n, FAIL,
                         f"n_occluded={n_occluded} > ceiling={ceiling:.1f} "
                         f"({f:g} x n_var={n_var}) -> the region must DEFER "
                         f"(deferred_occlusion_anomaly), never auto-exclude; "
                         f"disclose as a deviation",
                         HARD_STOP, measured)
        headroom = ceiling / max(n_occluded, 1)
        return Check(n, PASS,
                     f"n_occluded={n_occluded} <= ceiling={ceiling:.1f} "
                     f"({headroom:.0f}x headroom)",
                     HARD_STOP, measured)

    return _guard("occlusion_anomaly_ceiling", HARD_STOP, run)


def check_region1_status(status: Any) -> Check:
    """Region 1 is the known-answer region; anything other than exactly ``ok`` is
    the finding.

    A-04 WIDENING: region 1 runs under ``--fail-fast``, where ``RegionGateError``
    fires on ANY ``status != 'ok'`` (``run_native_ld_panel.py:1161``) — not only on
    a ``deferred`` prefix. So ``verify_failed`` and ``error: ...`` are in scope too.
    Severity is ``_REGION1_SEVERITY`` (see the module docstring).
    """
    def run() -> Check:
        n = "region1_status"
        s = ("" if status is None else str(status)).strip()
        if s == "ok":
            return Check(n, PASS, "region 1 status='ok'", _REGION1_SEVERITY,
                         {"status": s})
        return Check(n, FAIL,
                     f"region 1 returned status={s!r}. Region 1 is the known-answer "
                     f"region (5 occluded, ~51 ceiling, 10x headroom) and runs under "
                     f"--fail-fast, which raises on ANY non-'ok' status — so this "
                     f"means the gate or the substrate disagrees with ground truth. "
                     f"This is a FINDING requiring diagnosis, not a retry.",
                     _REGION1_SEVERITY, {"status": s})

    return _guard("region1_status", _REGION1_SEVERITY, run)


# --------------------------------------------------------------------------- #
# STAGE B — scaling + mechanism consistency in aggregate                      #
# --------------------------------------------------------------------------- #

def check_peak_ram(peak_gib: Optional[float], vm_gib: float = _VM_TOTAL_GIB,
                   headroom_frac: float = _DEFAULT_HEADROOM_FRAC) -> Check:
    """Peak RSS must leave headroom on the VM; a MISSING measurement FAILS CLOSED."""
    def run() -> Check:
        n = "stage_b_peak_ram"
        if peak_gib is None:
            return Check(n, FAIL,
                         "peak_ram_gib not reported -> unmeasurable, FAIL CLOSED "
                         "(the producer must emit it per computed region)",
                         HARD_STOP)
        limit = vm_gib * (1.0 - headroom_frac)
        measured = {"peak_gib": peak_gib, "limit_gib": limit, "vm_gib": vm_gib}
        if peak_gib > limit:
            return Check(n, FAIL,
                         f"peak {peak_gib:.1f} GiB > {limit:.1f} GiB "
                         f"({headroom_frac:.0%} headroom on {vm_gib:.0f} GiB) -> do "
                         f"NOT extrapolate to larger regions",
                         HARD_STOP, measured)
        return Check(n, PASS, f"peak {peak_gib:.1f} GiB within {limit:.1f} GiB",
                     HARD_STOP, measured)

    return _guard("stage_b_peak_ram", HARD_STOP, run)


def check_maf_depression(pairs: List[Dict[str, float]],
                         min_frac: float = 0.5) -> Check:
    """Occluded variants should show DEPRESSED panel MAF vs sumstats MAF.

    DIRECTION check only — the GWAS AFR cohort is not the AoU AFR cohort, so the
    exact ratio is confounded. Absence of systematic depression WEAKENS the
    mechanism attribution: a FINDING for a human, not a hard stop.

    ⚠ A-12: IMPLEMENTED BUT NOT WIRED into any subcommand. The
    ``(panel_maf, sumstats_maf)`` pairs come from the occlusion manifests joined to
    the harmonized sumstats — Stage-B-report-side plumbing that does not exist yet,
    and building it is Carter's planning-side work, not the browser agent's.
    """
    def run() -> Check:
        n = "stage_b_maf_depression"
        if not pairs:
            return Check(n, FAIL,
                         "no (panel_maf, sumstats_maf) pairs supplied -> "
                         "unmeasurable, FAIL CLOSED", FINDING)
        usable = [p for p in pairs
                  if p.get("panel_maf") is not None
                  and p.get("sumstats_maf") is not None]
        if not usable:
            return Check(n, FAIL, "no usable pairs (all missing a side) -> FAIL "
                                  "CLOSED", FINDING)
        depressed = sum(1 for p in usable if p["panel_maf"] < p["sumstats_maf"])
        frac = depressed / len(usable)
        measured = {"depressed": depressed, "n": len(usable), "frac": frac}
        if frac < min_frac:
            return Check(n, FAIL,
                         f"only {depressed}/{len(usable)} ({frac:.0%}) of occluded "
                         f"variants show depressed panel MAF (threshold "
                         f"{min_frac:.0%}). The occlusion mechanism predicts "
                         f"systematic depression; its absence WEAKENS the "
                         f"attribution -> FINDING for human review (direction check "
                         f"only; cohort differences confound the magnitude).",
                         FINDING, measured)
        return Check(n, PASS,
                     f"{depressed}/{len(usable)} ({frac:.0%}) depressed — direction "
                     f"consistent with occlusion", FINDING, measured)

    return _guard("stage_b_maf_depression", FINDING, run)


# --------------------------------------------------------------------------- #
# COST GATE — denominator discipline                                          #
# --------------------------------------------------------------------------- #

def check_cost_denominator(n_regions_used: int, n_bankable: int,
                           n_total: int) -> Check:
    """Cost must be computed per BANKABLE region, never per region-of-``n_total``.

    A-08: ``n_total`` is REQUIRED, with no default. It is 276 today (measured:
    ``awk -F'\\t' 'NR>1 && $7=="AFR"' config/ld_regions.tsv | wc -l``) — and a
    default is exactly how a count goes silently stale.
    """
    def run() -> Check:
        n = "cost_gate_denominator"
        measured = {"used": n_regions_used, "bankable": n_bankable,
                    "total": n_total}
        if n_regions_used == n_total and n_bankable != n_total:
            return Check(n, FAIL,
                         f"cost denominator is {n_total} (all regions) but only "
                         f"{n_bankable} are bankable -> understates per-region cost "
                         f"by {n_total / max(n_bankable, 1):.2f}x. Use "
                         f"cost-per-BANKABLE-region.",
                         HARD_STOP, measured)
        if n_regions_used != n_bankable:
            return Check(n, FAIL,
                         f"cost denominator {n_regions_used} != bankable "
                         f"{n_bankable} -> the extrapolation covers regions that "
                         f"banked nothing",
                         HARD_STOP, measured)
        return Check(n, PASS,
                     f"cost computed on {n_bankable} bankable region(s) of "
                     f"{n_total} total", HARD_STOP, measured)

    return _guard("cost_gate_denominator", HARD_STOP, run)


# --------------------------------------------------------------------------- #
# PUBLICATION GATE — the R4-COVERAGE obligation cannot lapse silently         #
# --------------------------------------------------------------------------- #

#: The R4-COVERAGE block heading. The negative lookahead is load-bearing: a
#: RENAMED heading must yield an EMPTY block (-> a vacuity FAIL below), not a
#: fuzzy match that lets the rename through.
_R4_HEADING = re.compile(r"^## R4-COVERAGE(?![-\w])", re.M)
_SECTION_HEADING = re.compile(r"^## ", re.M)

#: MEASURED sentinels from the live disclosure text, NOT the bare word "estimate".
#: Two of the prototype's four markers are DEAD against the real file (the literal
#: uppercase ESTIMATE does not occur, and the text reads "29 / 276", never "~29"),
#: and a bare "estimate" would false-positive on innocent prose such as
#: "estimated from Stage B". See D-09.
_R4_ESTIMATE_SENTINELS = (
    "29 / 276 = 10.5%",
    "Seth's estimates, not measurements",
    "~247 regions",
    "48.5 Mb",
    "~10.5%",
)

#: Minimum non-empty lines for the extracted block to be non-vacuous. An empty or
#: gutted block satisfies every content assertion TRIVIALLY — the 260817-vbu V0
#: lesson, restated here because this file is parsed by heading.
_R4_MIN_BLOCK_LINES = 8


def _extract_r4_block(text: str) -> str:
    m = _R4_HEADING.search(text)
    if m is None:
        return ""
    start = m.start()
    nxt = _SECTION_HEADING.search(text, m.end())
    return text[start:nxt.start()] if nxt else text[start:]


def check_coverage_disclosure_resolved(path: "str | Path") -> Check:
    """R4-COVERAGE: the coverage-gap disclosure must carry MEASURED post-fire
    numbers plus a ``MEASURED:`` provenance line naming the panel-TSV source.

    A-06: takes a FILE, not a string, so the obligation is checked where it
    actually lives (``deferred-items.md``). Fails while the pre-fire estimates are
    still in place; fails just as hard if someone discharges it by DELETING the
    warning and shipping nothing (that is what the provenance line is for); and
    fails on a renamed heading, because an empty block is vacuous, not green.

    This is RED today by design. Its live gate in ``tests/m3/test_fire_verifier.py``
    skips until a measured panel TSV lands in-repo — that skip IS the named
    enforcer of the obligation.
    """
    def run() -> Check:
        n = "publication_coverage_disclosure"
        p = Path(path)
        if not p.is_file():
            return Check(n, FAIL,
                         f"disclosure file absent: {p} -> obligation R4-COVERAGE "
                         f"unmeasurable, FAIL CLOSED", HARD_STOP)
        block = _extract_r4_block(p.read_text())
        n_lines = len([ln for ln in block.splitlines() if ln.strip() != ""])
        if n_lines < _R4_MIN_BLOCK_LINES:
            return Check(n, FAIL,
                         f"the '## R4-COVERAGE' block in {p} extracted to "
                         f"{n_lines} non-empty line(s) (need >= "
                         f"{_R4_MIN_BLOCK_LINES}) -> the heading was renamed or the "
                         f"block was gutted; every content assertion below it would "
                         f"be VACUOUS",
                         HARD_STOP, {"block_lines": n_lines})

        found = [s for s in _R4_ESTIMATE_SENTINELS if s in block]
        if found:
            return Check(n, FAIL,
                         f"the R4-COVERAGE disclosure still carries pre-fire "
                         f"estimate sentinel(s): {'; '.join(found)} -> replace with "
                         f"MEASURED deferred_infeasible_square counts + the affected "
                         f"span from the panel TSV (the n_var ceiling is "
                         f"{_infeasible_ceiling()}) before anything is published",
                         HARD_STOP, {"block_lines": n_lines, "sentinels": found})

        if not re.search(r"^\s*MEASURED:", block, re.M):
            return Check(n, FAIL,
                         "the R4-COVERAGE block carries no 'MEASURED:' provenance "
                         "line -> the obligation cannot be discharged by deleting "
                         "the warning and shipping nothing; name the source the "
                         "numbers were measured from",
                         HARD_STOP, {"block_lines": n_lines})

        artifact = _panel_artifact_name()
        if ("panel tsv" not in block.lower()) and (artifact not in block):
            return Check(n, FAIL,
                         f"the R4-COVERAGE block names no panel-TSV source (neither "
                         f"the phrase 'panel TSV' nor {artifact!r}) -> the measured "
                         f"numbers have no provenance",
                         HARD_STOP, {"block_lines": n_lines})

        return Check(n, PASS,
                     f"the R4-COVERAGE disclosure carries measured values with a "
                     f"MEASURED: provenance line ({n_lines} non-empty lines, no "
                     f"pre-fire estimate sentinels)",
                     HARD_STOP, {"block_lines": n_lines})

    return _guard("publication_coverage_disclosure", HARD_STOP, run)


def find_measured_panel_tsvs(root: "str | Path") -> List[Path]:
    """Every in-repo file named like the producer's panel TSV, sorted.

    Used as the SKIP CONDITION of the live R4-COVERAGE gate: while the fire has not
    run, no measured panel TSV exists in-repo and the disclosure cannot possibly
    carry measured numbers. The condition is DERIVED (from
    ``run_native_ld_panel._DEFAULT_PANEL_NAME``), not invented, and the finder
    itself is shown valid by its own test on a tmp tree with and without the file.

    Symlinked directories are NOT followed: this asks "is the artifact IN the
    repo", and a results symlink into another filesystem is not the repo.
    """
    name = _panel_artifact_name()
    hits: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(str(root), followlinks=False):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__", ".snakemake",
                                    "node_modules", ".pytest_cache")]
        if name in filenames:
            hits.append(Path(dirpath) / name)
    return sorted(hits)


# --------------------------------------------------------------------------- #
# Driver                                                                      #
# --------------------------------------------------------------------------- #

def summarize(checks: List[Check]) -> Dict[str, Any]:
    """Roll a list of checks up into the gate's verdict.

    ``exit_code`` is 0 only if EVERY check passed. HARD_STOP and FINDING are
    bucketed separately, but both are non-zero: the tier informs the human
    response, it never softens the gate.
    """
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


def _print_summary(subcommand: str, s: Dict[str, Any]) -> None:
    print(f"=== fire_verifier {subcommand} ===")
    for entry in s["report"]:
        print(f"{entry['status']}  {entry['severity']}  {entry['name']}: "
              f"{entry['detail']}")
    print()
    print(f"hard_stops: {s['hard_stops']}")
    print(f"findings:   {s['findings']}")
    print(f"exit_code:  {s['exit_code']}")
    if s["exit_code"] != 0:
        print("A RED IS A STOP. Paste this block to Carter and wait — never chain "
              "past a red, and never retry or 'repair' on your own.")


def _lookup_region(rows: List[Dict[str, Any]], region_id: str
                   ) -> Optional[Dict[str, Any]]:
    for r in rows:
        if str(r.get("region_id")) == region_id:
            return r
    return None


def _stage_a(args) -> List[Check]:
    checks = [check_nan_falsification(args.npz),
              check_manifest_rows(args.manifest,
                                  expected_records=args.expected_records,
                                  region_id=args.region_id)]
    try:
        rows = parse_panel_tsv(args.panel_tsv)
    except Exception as e:  # noqa: BLE001 — fail closed, do not guess
        detail = (f"panel TSV unreadable ({type(e).__name__}: {e}) -> FAIL CLOSED")
        checks.append(Check("occlusion_anomaly_ceiling", FAIL, detail, HARD_STOP))
        checks.append(Check("region1_status", FAIL, detail, _REGION1_SEVERITY))
        checks.append(Check("status_classification", FAIL, detail, HARD_STOP))
        return checks

    row = _lookup_region(rows, args.region_id)
    if row is None:
        detail = (f"region {args.region_id!r} has NO row in {args.panel_tsv} -> the "
                  f"gate cannot measure n_var / n_dropped_occluded, FAIL CLOSED "
                  f"(never take these from a number a human typed)")
        checks.append(Check("occlusion_anomaly_ceiling", FAIL, detail, HARD_STOP))
        checks.append(Check("region1_status", FAIL, detail, _REGION1_SEVERITY))
    else:
        checks.append(check_occlusion_ceiling(row["n_dropped_occluded"],
                                              row["n_var"]))
        checks.append(check_region1_status(row["status"]))
    checks.append(classify_statuses(rows))
    return checks


def _stage_b(args) -> List[Check]:
    rows = parse_panel_tsv(args.panel_tsv)
    computed = [r for r in rows if str(r.get("status", "")).strip() == "ok"]
    checks: List[Check] = []
    if not computed:
        checks.append(Check(
            "stage_b_peak_ram", FAIL,
            f"no computed rows (status == 'ok') in {args.panel_tsv} -> there is "
            f"NOTHING to measure a peak against; a check with no input must FAIL, "
            f"not pass vacuously", HARD_STOP, {"n_rows": len(rows)}))
    else:
        for r in computed:
            c = check_peak_ram(r["peak_ram_gib"], vm_gib=args.vm_gib)
            c.name = f"{c.name}[{r['region_id']}]"
            checks.append(c)
    checks.append(classify_statuses(rows))
    n_bankable = sum(1 for r in rows if _status_class(r.get("status")) == STATUS_OK)
    checks.append(check_cost_denominator(n_regions_used=len(rows),
                                         n_bankable=n_bankable,
                                         n_total=args.n_total))
    return checks


def _stage_c(args) -> List[Check]:
    rows = parse_panel_tsv(args.panel_tsv)
    return [classify_statuses(rows)]


def _disclosure(args) -> List[Check]:
    return [check_coverage_disclosure_resolved(args.file)]


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fire_verifier.py",
        description="Mechanical fire-stage gates for the AFR LD panel build. "
                    "Exit 0 = every invariant for that stage is green. Exit 1 = at "
                    "least one is red -> STOP and report; the gate never decides.")
    sub = p.add_subparsers(dest="subcommand", required=True)

    a = sub.add_parser("stage-a", help="region-1 gate: mechanism falsification")
    a.add_argument("--panel-tsv", required=True)
    a.add_argument("--region-id", required=True)
    a.add_argument("--manifest", required=True)
    a.add_argument("--npz", required=True,
                   help="the BANKED region .npz, copied locally. REQUIRED: there is "
                        "no skip on the fire path — a falsification that did not "
                        "run is not a falsification.")
    a.add_argument("--expected-records", type=int, default=5)
    a.set_defaults(_run=_stage_a)

    b = sub.add_parser("stage-b", help="de-risk batch: scaling + cost denominator")
    b.add_argument("--panel-tsv", required=True)
    b.add_argument("--n-total", type=int, required=True,
                   help="total regions in the manifest (276 today). REQUIRED: a "
                        "default is how a count goes silently stale.")
    b.add_argument("--vm-gib", type=float, default=_VM_TOTAL_GIB)
    b.set_defaults(_run=_stage_b)

    c = sub.add_parser("stage-c", help="full-fire check-in rollup")
    c.add_argument("--panel-tsv", required=True)
    c.set_defaults(_run=_stage_c)

    d = sub.add_parser("disclosure", help="R4-COVERAGE publication obligation")
    d.add_argument("--file", required=True)
    d.set_defaults(_run=_disclosure)

    for q in (a, b, c, d):
        q.add_argument("--report", default=None,
                       help="write the summarize() dict to this path as JSON")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    """Run one stage's gates. Returns the exit code (0 green / 1 red).

    Project convention (``plink_ld_to_npz.main`` / ``run_native_ld_panel.main``):
    ``main(argv) -> int`` with ``sys.exit(main())`` at the entry point, so the
    shell still sees the exit status while the tests can assert on the value.
    """
    args = _build_parser().parse_args(argv)
    try:
        checks = args._run(args)
    except Exception as e:  # noqa: BLE001 — the driver fails closed too
        checks = [Check(f"{args.subcommand}_driver", FAIL,
                        f"the gate could not run ({type(e).__name__}: {e}) -> FAIL "
                        f"CLOSED", HARD_STOP)]
    s = summarize(checks)
    _print_summary(args.subcommand, s)
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        with open(args.report, "w") as fh:
            json.dump(s, fh, indent=2)
        print(f"report written: {args.report}")
    return int(s["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
