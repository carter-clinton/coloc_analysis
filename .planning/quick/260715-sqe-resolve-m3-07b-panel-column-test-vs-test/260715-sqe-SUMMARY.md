---
phase: quick-260715-sqe
plan: 1
subsystem: testing
tags: [pytest, native-ld-panel, panel-tsv, occlusion-provenance, m3-07b, osf-prereg]

# Dependency graph
requires:
  - phase: m3-07b
    provides: "_PANEL_COLUMNS grown to 9 entries — n_dropped_occluded INSERTED at index 7 (span-filter drop-count provenance); _append_panel_row_local writes columns=_PANEL_COLUMNS"
  - phase: m3-07a
    provides: "test_panel_columns_include_n_dropped_occluded (the RED that pinned the column into the contract)"
provides:
  - "test_panel_tsv_append_resume_safe expected column list mirrors the live 9-entry _PANEL_COLUMNS (n_dropped_occluded idx 7, n_dropped_monomorphic LAST idx 8)"
  - "tests/m3/test_run_native_ld_panel.py driver suite fully GREEN: 52 passed / 0 failed (was 1 failed / 51 passed)"
  - "The m3-07b test-vs-test contradiction is CLOSED — resolved test-side on verified precedent evidence (see provenance note below), NOT by a Carter ruling"
affects: [m3-07c, native-ld-panel, panel-tsv-schema]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Edit-tool exact-match old_string as the idempotency gate (fails fast if already applied)"
    - "Test-only change; production code 0-line diff (git diff --stat -- src/ EMPTY)"
    - "Explicit `git add <path>` — never -A / . on this shared GPFS tree"

key-files:
  created: []
  modified:
    - "tests/m3/test_run_native_ld_panel.py — test_panel_tsv_append_resume_safe expected column list ONLY (+1 line)"

key-decisions:
  - "Fixed the TEST, not the column: dropping n_dropped_occluded from _PANEL_COLUMNS would discard the per-region occlusion provenance osf.io/az52u pre-registers (FORBIDDEN)."
  - "The contradiction was an OMISSION in the m3-07a RED, not a deliberate expectation — precedent 1a9d170 (quick-260701-qcy) added the PREVIOUS panel column AND updated this same assertion in one commit; the companion edit was simply skipped for n_dropped_occluded."
  - "n_dropped_occluded inserted at index 7 (BEFORE n_dropped_monomorphic), not appended — appending would re-fail with the index-7 diff merely flipped, and would break the [-1] pin at ~:1281."

patterns-established:
  - "Panel-TSV column additions must update BOTH the schema pin tests AND the :392 exact-column-list assertion in test_panel_tsv_append_resume_safe — :392 is the ONLY exact-order pin; all other panel tests use order-independent set()/issubset."

requirements-completed: [REQ-OSF-PREREG]

# Metrics
duration: 4min
completed: 2026-07-15
---

# Phase quick-260715-sqe: Resolve the m3-07b panel-column test-vs-test contradiction Summary

**`n_dropped_occluded` pinned at index 7 of the resume-safe panel-column assertion — the m3-07b occlusion provenance column survives intact and the native-LD driver suite is fully GREEN at 52/52.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-07-15
- **Completed:** 2026-07-15
- **Tasks:** 1
- **Files modified:** 1 (+1 line)

## Accomplishments

- **The contradiction is CLOSED, test-side.** `test_panel_tsv_append_resume_safe` (~:392) now mirrors the live 9-entry `drv._PANEL_COLUMNS` exactly: `n_dropped_occluded` at index 7, `n_dropped_monomorphic` LAST at index 8.
- **Driver suite 51 → 52 passed, 0 failed.** The last RED in `tests/m3/test_run_native_ld_panel.py` is gone.
- **The pre-registered occlusion provenance column survives.** `n_dropped_occluded` remains in production `_PANEL_COLUMNS` (line 116) — unreordered, undropped.
- **Both guard tests GREEN and byte-unchanged.** `test_panel_columns_include_n_dropped_occluded` (the m3-07a RED) and `test_panel_columns_include_n_dropped_monomorphic` (`[:7]` / `[-1]` pins) both explicitly named and confirmed *passed*, not skipped.
- **Production 0-line diff.** `git diff --stat -- src/` is EMPTY — the driver and all three frozen contracts (`plink_ld_to_npz.py`, `ld_npz_to_rds.R`, `condition_ld_matrix.py`) untouched.

## Task Commits

1. **Task 1: Insert n_dropped_occluded at index 7 of the resume-safe test's expected column list** — `957d5a1` (test)

**Plan metadata:** handled by the orchestrator (docs commit not made by the executor, per task constraints).

## Files Created/Modified

- `tests/m3/test_run_native_ld_panel.py` — `test_panel_tsv_append_resume_safe`: inserted `"n_dropped_occluded",  # m3-07b: occlusion span-filter drop-count provenance` into the `assert list(df.columns) == [...]` literal at index 7. The test's actual subject — resume safety (one row per region; header written exactly once) — is untouched.

## Decisions Made

**⚠ PROVENANCE CORRECTION (orchestrator, post-executor).** The executor's draft recorded this decision as "pre-settled by Carter." That is **not accurate** and has been corrected — it matters, because the 2026-07-15 HANDOFF explicitly logged this as *"a CARTER CALL, deliberately NOT taken,"* and a future session must not believe a human ruled on it when one did not.

**What actually happened:** Carter's `/gsd-resume-work` args named "decide the column conflict" as the next step. The decision was then made **by the orchestrating agent this session**, on evidence verified before any edit — not by a Carter ruling, and not by the executor (which received it already settled and was correctly instructed not to re-litigate it).

**The evidence the call rests on** (each independently checked against the live repo this session, not taken from the handoff narrative):

- **Precedent `1a9d170`** (itself quick-260701-qcy): added the PREVIOUS panel column RED-first **AND** updated this *same* `:392` assertion in the *same* commit — its message reads *"updated the panel-TSV column-list assertion for the appended column."* The companion edit was simply never made for `n_dropped_occluded` ⟹ **omission, not a deliberate expectation.**
- **Test subject:** `test_panel_tsv_append_resume_safe` proves resume safety (one row per region; header written exactly once). The column list is supporting setup, not the assertion under test. Column schema has dedicated tests at ~:1274 / ~:1585.
- **Blast radius:** `:392` was the ONLY exact-column-list pin for the panel TSV; every other panel test uses order-independent `set()`/`issubset`; no R/Snakemake/downstream consumer reads the panel TSV at all.
- **The `do_not` was honored:** the fix updates the pre-existing assertion (the handoff's own proposed remedy) and does **not** weaken the 07a RED — verified PASSED, not skipped.

**If Carter disagrees with this call, `957d5a1` is a 1-line test-only revert.** Nothing downstream was built on it.

Recorded rationale, for the record:

- **Precedent:** `1a9d170` (quick-260701-qcy) added the previous panel column RED-first AND updated this same assertion in the same commit.
- **Test subject:** `test_panel_tsv_append_resume_safe` proves resume safety; the column list is supporting setup. Column schema has dedicated tests at ~:1274 and ~:1585.
- **Blast radius:** :392 was the only exact-column-list pin for the panel TSV; no R/Snakemake/downstream consumer reads it.

## Deviations from Plan

None — plan executed exactly as written. One inserted line, one file, one commit. No deviation rules fired; no auto-fixes were needed.

## Issues Encountered

**One observation, no action taken (worth recording so it is not re-diagnosed later):**

The plan's Step 1.4 expected `git diff --name-only` to name `tests/m3/test_run_native_ld_panel.py` "and nothing else" (anticipating only `sparse_parent_benchmark.tsv` as a possible extra). The working tree actually carried **three** pre-existing dirty files from before this task, all already ' M' in the session-start git status:

- `.claude/settings.json`
- `.planning/quick/260625-r6m-build-resumable-native-plink-ld-loop-dri/260625-r6m-SUMMARY.md`
- `tests/m3/sparse_parent_benchmark.tsv`

None are attributable to this task, and none were staged — explicit-path staging (`git add tests/m3/test_run_native_ld_panel.py`) excluded them structurally. `git diff --cached --name-only` was verified to name exactly one file before committing. The plan's "nothing else" wording assumed a clean tree; the load-bearing gate (`git diff --stat -- src/` EMPTY) passed.

**No GPFS object-store loss this run** — the commit landed first try, despite the known recurring pattern (3 hits in ~3 weeks).

## Verification

Plan's automated gate: **PASSED**.

- `pytest tests/m3/test_run_native_ld_panel.py -q` → **52 passed** in 1.42s, 0 failed
- `pytest ...::test_panel_columns_include_n_dropped_occluded ...::test_panel_columns_include_n_dropped_monomorphic -q` → **2 passed**
- `git diff --stat -- src/` → **EMPTY**
- `git diff a76ebe5 HEAD -- tests/m3/test_run_native_ld_panel.py` → **1 file changed, 1 insertion(+)** — a pure single insertion, which structurally confirms both guard tests are byte-unchanged
- `grep -n "n_dropped_occluded" src/python/run_native_ld_panel.py` → line 116 in `_PANEL_COLUMNS` (intact, in position)

**Full `tests/m3` suite — RUN BY THE ORCHESTRATOR (the executor skipped it as plan-optional; the orchestrator ran it anyway as the regression gate):**

```
15 failed, 395 passed, 31 skipped in 411.34s (0:06:51)
```

**Against the m3-07b baseline of `16 failed / 394 passed / 31 skipped`: exactly ONE test flipped RED→GREEN (this fix), and nothing regressed.**

Every one of the 15 remaining failures is an expected m3-07c `ModuleNotFoundError`, confirmed by counting the actual exception rather than trusting the file names:

| Missing module (m3-07c, unbuilt) | Failures | Suite |
|---|---|---|
| `drop_occluded_from_sumstats` (07c T4) | 9 | `test_occlusion_lockstep_drop.py` |
| `occlusion_present_rate_scan` (07c T3) | 6 | `test_occlusion_present_rate_scan.py` |
| **Total** | **15** | = the full failure count, so **zero unexplained failures** |

These go green when 07c lands and are out of scope here.

Note: running the full suite re-dirties `tests/m3/sparse_parent_benchmark.tsv` (a known benign write into the tracked tree). It was NOT staged — explicit-path staging excludes it.

## Self-Check: PASSED

- `tests/m3/test_run_native_ld_panel.py` — FOUND (modified, +1 line)
- Commit `957d5a1` — FOUND in `git log`
- `n_dropped_occluded` in `src/python/run_native_ld_panel.py::_PANEL_COLUMNS` — FOUND (line 116)

## Known Stubs

None. This task added no code paths, no placeholders, and no unwired data.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **`tests/m3/test_run_native_ld_panel.py` is fully GREEN (52/52).** The single open test-vs-test contradiction reported at m3-07b close is resolved; it no longer blocks anything.
- **m3-07c remains NOT started** — it needs Carter's explicit go. Its modules are unbuilt (the 15 expected `ModuleNotFoundError` failures in the wider `tests/m3` suite).
- **AoU perimeter untouched; the native LD loop was NOT re-fired** (loop STOPPED, .npz 0/276). `condition_ld_matrix.py` remains FROZEN/HELD (m3-06). $0 spend.
- **Not pushed** — the orchestrator handles the docs commit and the push. Per `reference_ncsu_github_push_auth`, verify `origin` tip == local HEAD afterward; NCSU can run many commits ahead of origin.

---
*Phase: quick-260715-sqe*
*Completed: 2026-07-15*
