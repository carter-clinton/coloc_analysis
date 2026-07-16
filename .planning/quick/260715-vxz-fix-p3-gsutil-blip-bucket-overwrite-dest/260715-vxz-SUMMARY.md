---
quick_id: 260715-vxz
type: execute
status: complete
requirements: [P3a, P3b]
commit: ff8cc47
branch: m3-W2-aou-deltas
baseline_head: 606f293
subsystem: m3-W2 native plink LD panel driver
tags: [data-loss, fail-closed, gsutil, provenance, aou, tdd]
tech-stack:
  patterns:
    - "fail-CLOSED tri-state classification at a trust boundary whose failure mode is destructive"
    - "REFUSE-never-auto-repair (u22 header-guard stance, :495-506)"
key-files:
  modified:
    - src/python/run_native_ld_panel.py
    - tests/m3/test_run_native_ld_panel.py
decisions:
  - "Added a SEPARATE fail-CLOSED classifier for the panel path rather than refactoring the shared _gsutil_object_size — its two callers have OPPOSITE failure-safety requirements."
  - "Detection tolerates singular+plural no-url(s)-matched, case-insensitively; corrected the mock to real gsutil's plural string rather than matching the mock's fiction."
  - "Tests assert bucket-object-byte-identical, not merely pytest.raises — a raises-only test passes even if the overwrite happens first."
metrics:
  tasks: 1
  tests_added: 4
  suite_before: "15 failed / 401 passed / 31 skipped"
  suite_after: "15 failed / 405 passed / 31 skipped"
  duration_min: ~35
  completed: 2026-07-15
---

# quick-260715-vxz: Fail closed on an indeterminate panel-TSV seed Summary

Closed **P3a/P3b**: a transient gsutil blip silently destroyed every banked row of the
gs:// panel TSV mid-fire. `append_panel_row` now fail-CLOSED-classifies the bucket state
and **refuses** rather than guessing "absent" and uploading a fresh 1-row file over
banked provenance.

## The defect, positively demonstrated (not merely asserted)

Before writing any test I ran a throwaway probe (scratchpad, not committed) against the
**live pre-fix code** through the `_run_gsutil` seam. It did not just show "nothing
raised" — it showed the loss:

| Scenario | raised | bucket rows before → after | bucket unchanged |
|---|---|---|---|
| **P3a** INDETERMINATE stat (503) vs a POPULATED panel TSV | `None` | **3 → 1** | **False** |
| **P3b** stat says PRESENT, seed `cp` FAILS | `None` | **3 → 1** | **False** |
| (c) control: definitively ABSENT | `None` | absent → 1 | n/a (correct) |

Three banked rows replaced by one, silently, in both cases. Same probe post-fix: both
raise, **3 → 3, bucket unchanged, zero `cp` to the panel URI**; the control still writes
its fresh row. The probe's bucket mock is *independently written* (not `_MockGsutil`), so
the control passing there is a second, independent confirmation that absent-detection
does not false-trip.

## Observed pre-fix result of each test — recorded honestly

Run against the **unmodified source** with the mock already extended (mock extension had
to land first; see landmine 4):

| Test | Observed pre-fix | Honest note |
|---|---|---|
| **(a)** `test_gs_panel_indeterminate_stat_refuses_without_overwriting` | **FAILED** — `Failed: DID NOT RAISE <class 'RuntimeError'>` | Genuine RED. The defect itself. |
| **(b)** `test_gs_panel_failed_seed_download_refuses_without_overwriting` | **FAILED** — `Failed: DID NOT RAISE <class 'RuntimeError'>` | Genuine RED. The defect itself. |
| **(c)** `test_gs_panel_definitively_absent_still_starts_fresh` | **PASSED pre-fix** | Expected. Pins today's *correct* absent path. **Not contrived into a RED.** |
| **(d)** `test_gs_panel_seeded_from_bucket_dedups_across_recycle` | **PASSED pre-fix** | Expected — **but only because the mock was extended first.** Against the unextended upload-only mock it would have failed via `Path("gs://…").stat()` → `FileNotFoundError` → swallowed → a P3b-shaped failure for a **mock-artifact** reason, not a real one. Exactly as the plan predicted. |

Pre-fix single file: `2 failed, 56 passed`. (a)/(b) are RED-first data-loss proofs;
(c)/(d) are regression guards that pin existing behavior — they were never expected to be
RED and were not made to look so.

The RED is **behavioral** (`pytest.raises(RuntimeError)`), not name-based. Asserting
`drv.PanelBucketStateUnknown` would have failed pre-fix with `AttributeError` — a RED for
a *naming* reason that never proves the clobber. `RuntimeError` fails pre-fix with
`DID NOT RAISE`, which *is* the defect.

## The fix

**Root cause:** `_gsutil_object_size` has exactly 2 callers (verified: `:209`, `:536`)
with **opposite** failure-safety requirements.

| Caller | False-"absent" costs | Correct default |
|---|---|---|
| `:209` `_existing_region_npz_gs` (resume guard) | COMPUTE (recompute a region) | assume absent — **correct, load-bearing for the 276-region skip** |
| `:536` panel mirror seed | **DATA LOSS** (upload-over) | **REFUSE** |

So a **new** fail-CLOSED helper was added for the panel path; the shared helper was **not**
refactored.

- `_gsutil_panel_object_size` — PRESENT(+size) / ABSENT(`None`) / INDETERMINATE(raise).
  ABSENT **only** on a positive `no url(s)? matched` signature (case-insensitive,
  singular+plural). Everything else — another `CalledProcessError` (503, 403, 404), any
  non-`CalledProcessError`, or an exit-0 stat with no parseable `Content-Length` — is
  INDETERMINATE. Docstring states *why* it is fail-CLOSED while `_gsutil_object_size` is
  fail-OPEN.
  - **isinstance guard:** `except subprocess.CalledProcessError` is matched *first* and is
    the only branch that touches `.stderr`; a `FileNotFoundError` (no `.stderr`) falls to
    the bare `except Exception` → INDETERMINATE. Pinned by sub-case (ii) of test (a).
- `append_panel_row` seed block — cp failure against a PRESENT object **raises**
  (`except: pass` removed); a cp that "succeeds" but lands no mirror **raises** (same loss,
  other door). `size == 0` and ABSENT still start fresh (today's lossless behavior).
- Errors are actionable, chain the cause (`raise … from exc`), and **distinguish P3a
  ("INDETERMINATE") from P3b ("failed to DOWNLOAD")** — both assertions are pinned by tests.
- `re` was **not** imported; used the substring form rather than adding an import.
- **No auto-repair, no retry.** Refuse and escalate (u22's REFUSE stance).

Used a stdlib-only implementation; no Context7 lookup was warranted (`subprocess`/`pathlib`
only, no third-party API surface).

## `_MockGsutil` blast radius — all 6 pre-existing call sites byte-identical

Following the m3-07b `_MockPlink` precedent. Every extension is **opt-in via a
keyword-only kwarg defaulting to `None`**, so no existing construction changes behavior.

| Call site | Construction | Why unaffected |
|---|---|---|
| `:705` | `_MockGsutil()` | all new kwargs default `None` → empty sets/dicts; no new branch reachable |
| `:735` | `_MockGsutil()` | same |
| `:775` | `_MockGsutil(prestaged={uri: int})` | `objects: dict[uri, int]` kept **exactly as-is**; `prestaged` semantics unchanged |
| `:799` | `_MockGsutil(prestaged={uri: int})` | same |
| `:814` | `_MockGsutil(stat_error_uris={uri})` | `stat_error_uris` semantics **byte-identical** (still raises the *absent* signature); new INDETERMINATE capability is a **separate** kwarg |
| `:838` | `_MockGsutil()` | all new kwargs default `None` |

Three extensions:
1. **`stat_indeterminate_uris` / `stat_raise_uris`** — the mock **conflated error with
   absent** (`stat_error_uris` raised the *absent* signature), so it could not express the
   exact state the fix must distinguish. `stat_error_uris` untouched.
2. **`cp_fail_srcs`** — models P3b.
3. **download direction + `contents`/`prestaged_contents`** — `cp` was **upload-only**
   (`Path(src).stat()` on a `gs://` src → `FileNotFoundError`), so **the mirror-seed
   download path had never been exercised by any test. That is how P3 survived.**
   `objects` remains `{uri: int}` (upload now records `len(read_bytes())` — identical size
   for a regular file); `contents` is a **parallel** dict added for the byte-identical
   proofs.

**Corrected the mock's stderr** from the singular `"No URL matched"` to real gsutil's
plural `"No URLs matched: gs://..."`. **This is safe for `:814` because
`_gsutil_object_size` catches ALL exceptions and returns `None` regardless of stderr** —
its result is stderr-independent. A mock that misreports its tool's output is the *same
bug class as P3 itself*; had detection been written against the mock's fiction, production
would never classify absent and **every first region would raise, so the ~11-day fire
could never start** (T-vxz-04).

**Empirical confirmation:** all **54** pre-existing tests in the file passed *pre-fix* with
the extended mock (`2 failed, 56 passed` = only (a)/(b) red). `:814` is textually
unmodified and green; every diff deletion is confined to `_MockGsutil` internals.

## Verification

| Gate | Result |
|---|---|
| Single file | **58 passed** |
| **Full `tests/m3` (backgrounded, 390s)** | **`15 failed / 405 passed / 31 skipped`** — exactly 401 + 4 |
| The 15 failures | **9** `drop_occluded_from_sumstats` + **6** `occlusion_present_rate_scan` — same `ModuleNotFoundError`s |
| Non-`ModuleNotFoundError` failures | **none** (no regression) |
| m3-07c modules | both **ABSENT** — RED preserved, never below 15 |
| Frozen contracts (3 files) | **0-line diff** |
| `:186-217` (`_gsutil_object_size`/`_existing_region_npz_gs`) | **no hunk** — lowest hunk is old line **223** |
| `_PANEL_COLUMNS` / u22 header guard | no diff line touches either; guard intact |
| Tests `:392`/`:1281`/`:1590` | green |
| AoU perimeter | **zero contact** — everything through monkeypatched `_run_gsutil` |
| Staging | explicit paths only; 3 pre-existing dirty files untouched |

## Deviations from Plan

None — plan executed exactly as written. No Rule 1–4 deviation fired; no CLAUDE.md conflict.

Two judgment calls inside the plan's stated latitude:
- Used the **substring** form over importing `re` (plan: "your call") — avoids touching the
  import block.
- Test (a) carries a **second sub-case** (`FileNotFoundError` → INDETERMINATE) inside the
  same test function rather than a 5th test, keeping the count at exactly 4 (405 = 401+4)
  while pinning the checker's isinstance-guard note. Without the guard the classifier would
  `AttributeError` on `.stderr`.

## Known Stubs

None.

## Threat Flags

None. No new network endpoint, auth path, file access pattern, or schema change was
introduced; T-vxz-01/02 are mitigated as planned, T-vxz-04 pinned by test (c).

## Self-Check: PASSED

- `src/python/run_native_ld_panel.py` — FOUND (modified, committed)
- `tests/m3/test_run_native_ld_panel.py` — FOUND (modified, committed)
- `.planning/quick/260715-vxz-fix-p3-gsutil-blip-bucket-overwrite-dest/260715-vxz-SUMMARY.md` — FOUND
- Commit `ff8cc47` — FOUND in `git log`
- Working tree clean for both modified files; no docs committed; not pushed (orchestrator's job)
</content>
