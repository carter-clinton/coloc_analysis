---
phase: quick-260601-u1b
verified: 2026-06-01T00:00:00Z
status: passed
score: 8/8 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 7/8
  gaps_closed:
    - "AOU-1-chr22-smoke is parameterized by a single INTERVAL variable threaded into all three load_qc_cohort calls, the du-floor cells, and output suffixes — and ALL Track-4 cells are retained"
  gaps_remaining: []
  regressions: []
---

# Phase quick-260601-u1b: Harden chr22 smoke into tiered cheap-first validation — Verification Report

**Phase Goal:** Harden the chr22 smoke into a tiered cheap-first validation sequence (Tier 0 synthetic probe -> Tier 1 nano-interval -> Tier 2 chr22) + forensic-capture-on-fail, WITHOUT weakening any Track-4 guard. Repo artifacts only (code + tests + 2 notebooks + runbook); launches nothing, spends nothing.
**Verified:** 2026-06-01
**Status:** passed
**Re-verification:** Yes — after gap closure (commits c522032, 867d30a)

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A ~2 Mb nano-interval MT no longer false-positives the du byte-floor (the count_rows>0/count_cols>0 hard guard remains the real gate) | VERIFIED | `_interval_scaled_du_floor('chr22:16000000-18000000', base_floor_bytes=50_000_000)` returns `2_000_000` (2 MB, the MIN_DU_FLOOR_BYTES clamp). `_interval_scaled_du_floor('chr22', ...)` returns full `50_000_000`. Hard guard body at lines 706-753 is untouched. |
| 2 | An interval-agnostic du-floor helper exists in aou_ld_panel.py with passing tests, parameterized per tier | VERIFIED | `_interval_scaled_du_floor(interval_filter, *, base_floor_bytes)` defined at line 782. All 4 tests pass. Full suite: 109 passed / 27 skipped. |
| 3 | `_capture_catastrophe_forensics(uri, *, phase)` exists, is best-effort (never raises), and captures _SUCCESS-mtime-vs-part-mtimes + MT listing + hail.log copy + Spark-REST snapshot + a `_forensics/<phase>_capture.json` | VERIFIED | Function at line 924 with all captures (a)-(e) in try/except blocks. `_coerce_mtime` called at lines 1080-1081 for float-normalized distinguisher comparison. All-raising collaborators test passes; hypothesis-flag tests pass; json round-trip test passes. |
| 4 | The existing `_assert_checkpoint_nonempty` hard-fail/raise semantics are UNCHANGED (no guard weakened) | VERIFIED | Body lines 706-753: `count_rows()==0 or count_cols()==0` -> RuntimeError. md5 of function block: `16caccec0678a9e57f38569cb3e5b801` — byte-identical pre/post remediation. Diff from c89008c is purely additive; insertions begin after line 753. |
| 5 | A new Tier 0 mechanism-probe notebook exists that exercises the 2048-partition cores=1/5g write path with a synthetic range_matrix_table, ZERO source read, ZERO QC | VERIFIED | `AOU-0.5-mechanism-probe_template.ipynb` exists. Cores=1/5g lever byte-faithful, `range_matrix_table(50_000, 2_000).repartition(2048)`, `_assert_checkpoint_nonempty(phase='probe')`, few-MB du floor via `_interval_scaled_du_floor`, forensic-capture-on-fail, honest caveat + Gate-A markdown. |
| 6 | AOU-1-chr22-smoke is parameterized by a single INTERVAL variable threaded into all three load_qc_cohort calls, the du-floor cells, and output suffixes — ALL Track-4 cells retained | VERIFIED (CLOSED GAP) | `_MIN_BYTES` has 0 occurrences in the notebook (was the prior gap). All three du-floor cells (cell-5, cell-7, cell-9) assert `_size_bytes > _DU_FLOOR_BYTES`. `_DU_FLOOR_BYTES` is defined in Cell 1c via `_interval_scaled_du_floor(INTERVAL, ...)`. `interval_filter=INTERVAL` appears exactly 3 times. No hardcoded `50000000` / `50_000_000`. Only 2 bare `"chr22"` literals (INTERVAL default + Cell-0 backtick prose). All Track-4 cells retained. Commit c522032 (6-line substitution, minimal diff, JSON encoding preserved). |
| 7 | A tier-gated runbook documents Gate A/B/C with cluster specs, $ envelopes, decision rules, and the rigor caveat | VERIFIED | `TIERED-VALIDATION-RUNBOOK.md` confirmed. Gate A: 64 vCPU, NON-preemptible, ~$1-3. Gate B: same 64 vCPU, ~$1-3. Gate C: 384 vCPU, NON-preemptible, ~$35-80. 1000G AFR fallback at every FAIL branch. Rigor caveat and watchpoints present. |
| 8 | All ~94 prior tests still pass under smoke_dev pytest (no regression) | VERIFIED | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/ -q` (Python 3.11): **109 passed, 27 skipped in 1.46s**. Zero failures. Baseline was 65+11 at initial verification; +7 additional tests from IN-01/IN-02 remediation (867d30a), all green. |

**Score:** 8/8 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/python/aou_ld_panel.py` | interval-scaled du-floor helper + `_capture_catastrophe_forensics(uri, *, phase)` | VERIFIED | `_interval_scaled_du_floor` at line 782; `_coerce_mtime` at line 859; `_capture_catastrophe_forensics` at line 924. Purely additive diff from c89008c. |
| `tests/m3/test_aou_ld_panel_local.py` | RED-first tests for du-floor helper and forensics helper | VERIFIED | 8 original + 7 remediation tests, all pass. RED fail evidence in `red_fail_output.txt` (amended with IN-01 RED section). |
| `.planning/notebooks/AOU-0.5-mechanism-probe_template.ipynb` | Tier 0 synthetic-MT probe | VERIFIED | Valid nbformat. Cores=1/5g lever, repartition(2048), `_assert_checkpoint_nonempty(phase='probe')`, few-MB du soft-floor, forensic-capture-on-fail, honest caveat + Gate-A markdown. |
| `.planning/notebooks/AOU-1-chr22-smoke_template.ipynb` | INTERVAL-parameterized, all Track-4 cells retained | VERIFIED | Gap closed. `_MIN_BYTES` absent (0 occurrences). All 3 du-floor cells assert `_size_bytes > _DU_FLOOR_BYTES`. `_DU_FLOOR_BYTES` defined in Cell 1c. 3x `interval_filter=INTERVAL`. No hardcoded 50 MB. 2 bare `"chr22"` literals (acceptable). All Track-4 cells retained. |
| `.planning/quick/260601-u1b-harden-chr22-smoke-into-tiered-cheap-fir/TIERED-VALIDATION-RUNBOOK.md` | Gate A/B/C decision tree, cluster specs, $ envelopes, watchpoints, rigor framing | VERIFIED | All required content present and correct. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| AOU-0.5 probe cell | `_assert_checkpoint_nonempty` + `_capture_catastrophe_forensics` | imported helper calls on the synthetic-MT checkpoint | VERIFIED | Both imported and called; forensic-capture-on-fail in except block. |
| AOU-1 INTERVAL variable | `load_qc_cohort(interval_filter=INTERVAL)` + du-floor cell URIs + output suffixes | single notebook variable threaded through all three cohort fires + validation cells | VERIFIED | 3x `interval_filter=INTERVAL`; `_suffix` used in URIs; `_DU_FLOOR_BYTES` computed from INTERVAL; Cell 7 uses `[INTERVAL] * 3` and `_suffix`. |
| du-floor cells (Cells 3.5/4.5/5.5) | interval-agnostic count>0 hard guard + parameterized soft floor | du byte-floor demoted to soft-warn/parameterized; count>0 stays the HARD gate | VERIFIED | `_DU_FLOOR_BYTES` correctly referenced in all three assert statements and f-string messages. count>0 hard gate untouched. `_capture_catastrophe_forensics` on except, re-raise preserved. |
| TIERED-VALIDATION-RUNBOOK.md Gate A->B->C | AOU-0.5 probe -> AOU-1 (nano) -> AOU-1 (chr22) -> full-genome | decision gates escalate cheap->expensive; 1000G AFR is the documented FAIL safety net | VERIFIED | All three gates documented with cluster specs and decision rules. 1000G AFR safety net mentioned at every FAIL branch. |

---

### Data-Flow Trace (Level 4)

Not applicable — this phase produces repo-only artifacts (no runnable APIs, no live data pipeline). Notebooks are templates; no data flows until Carter fires them on AoU.

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `_MIN_BYTES` absent from AOU-1 notebook | json parse + grep | 0 occurrences | PASS |
| `assert _size_bytes > _DU_FLOOR_BYTES` in all 3 du-floor cells | json parse | 3 cells confirmed | PASS |
| `interval_filter=INTERVAL` count == 3 | json parse | 3 | PASS |
| No hardcoded `50000000` / `50_000_000` | json parse | 0 occurrences | PASS |
| `_coerce_mtime` defined and called in `_capture_catastrophe_forensics` | grep aou_ld_panel.py | defined line 859; called lines 1080-1081 | PASS |
| `_assert_checkpoint_nonempty` body unchanged (count_rows==0 or count_cols==0 -> RuntimeError) | read lines 706-753 | Body byte-identical | PASS |
| Full test suite under smoke_dev pytest (`tests/m3/`) | pytest -q | **109 passed, 27 skipped** | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| QUICK-260601-U1B | 260601-u1b-PLAN.md | Tiered cheap-first chr22 validation hardening | SATISFIED | All 8 must-haves verified. Code, tests, AOU-0.5 notebook, parameterized AOU-1, and runbook all correct and complete. Prior `_MIN_BYTES` NameError closed by c522032; IN-01 mtime-coerce + IN-02/IN-03 closed by 867d30a. |

---

### Anti-Patterns Found

None. The prior blocker (`_MIN_BYTES` undefined in AOU-1 du-floor cells) is closed. No new anti-patterns detected in the remediation commits.

---

### Human Verification Required

None. All must-haves are mechanically verifiable from the repo artifacts.

---

## Gaps Summary

No gaps. The single gap from the initial verification is closed.

**Prior gap:** AOU-1 du-floor cells (3.5/4.5/5.5, notebook cell indices 5/7/9) asserted `_size_bytes > _MIN_BYTES` where `_MIN_BYTES` was never assigned — `NameError` at runtime, disabling the soft-floor check on every tier fire.

**Closure (commit c522032):** All 6 occurrences (`assert` + f-string message x 3 cells) replaced `_MIN_BYTES` -> `_DU_FLOOR_BYTES` via raw byte-level substitution. Minimal 6-line diff; JSON encoding preserved; nbformat re-validated. Python parse confirms 0 `_MIN_BYTES` occurrences and 3 du-floor cells with `assert _size_bytes > _DU_FLOOR_BYTES`.

**Additional remediation (commit 867d30a):**
- IN-01: `_coerce_mtime(value) -> float | None` added at line 859 and called in the distinguisher at lines 1080-1081. Hail string/mixed-type mtimes now coerce to a common float scale before comparison — the distinguisher no longer degrades to `'indeterminate'` on `TypeError` from str-vs-int pairs, and lexicographic inversion on same-format strings is eliminated.
- IN-02: Two additional never-raise production-path tests (bucket=None + partial-JSON-on-raise-collaborators).
- IN-03: Dead local `success_uri` variable removed.

Final test count: **109 passed / 27 skipped** (was 65+11 at initial verification). Zero regressions.

---

_Verified: 2026-06-01T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
_Re-verification after gap closure: commits c522032, 867d30a_
