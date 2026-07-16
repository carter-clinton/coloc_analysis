---
quick_id: 260715-vxz
verified: 2026-07-16T03:53:17Z
status: passed
score: 6/6 must-haves verified
commit: ff8cc47
baseline: 606f293
overrides_applied: 0
---

# Quick 260715-vxz Verification Report — Fix P3 gsutil-blip bucket overwrite

**Goal:** close P3 — `append_panel_row`'s gs:// mirror-seed silently overwrote the
bucket panel TSV with a fresh 1-row file after a transient gsutil error, destroying
banked provenance mid-fire.
**Invariant:** never `gsutil cp` the mirror OVER the bucket object unless positively
established the mirror contains everything the bucket object contains (downloaded
OK, or definitively absent). INDETERMINATE → RAISE.

**Verified:** 2026-07-16T03:53:17Z
**Status:** passed
**Method:** Exercised through the monkeypatched `_run_gsutil` seam with an
independently-written mock (NOT the repo's `_MockGsutil`), plus a second pass
running the repo's own committed tests against the actual pre-fix module content
(git show 606f293) to confirm the SUMMARY's RED/GREEN claims are honest.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | INDETERMINATE gsutil stat (not the absent signature) RAISES instead of silently starting a fresh 1-row mirror | ✓ VERIFIED | Independent probe `case_a_indeterminate_503` + `case_a2_indeterminate_filenotfound` both raised `RuntimeError`/`PanelBucketStateUnknown`; repo test `test_gs_panel_indeterminate_stat_refuses_without_overwriting` green post-fix, `DID NOT RAISE` pre-fix (confirmed by re-running the actual test function against the pre-fix module) |
| 2 | Stat PRESENT + failed seed download RAISES instead of overwriting | ✓ VERIFIED | Independent probe `case_b_present_but_cp_fails` raised; repo test `test_gs_panel_failed_seed_download_refuses_without_overwriting` green post-fix, `DID NOT RAISE` pre-fix (confirmed against actual pre-fix module) |
| 3 | Both refusal cases leave the bucket object byte-identical, no `cp` to the panel URI issued | ✓ VERIFIED | Probe asserts `bucket.store[gs_uri] == pre_bytes` and no `cp` call with `dst==gs_uri` in both (a) and (b); repo tests assert `mock_gs.contents[_GS_PANEL_URI] == banked` and `_cp_to(mock_gs, _GS_PANEL_URI) == []` |
| 4 | DEFINITIVELY-ABSENT object (real gsutil's plural `No URLs matched:`) still starts fresh + uploads, no false trip | ✓ VERIFIED | Independent probe `case_c_definitively_absent` (plural) + `case_c2_singular_no_url_matched` (singular) both proceed without raising; repo test `test_gs_panel_definitively_absent_still_starts_fresh` green both pre-fix and post-fix (correctly unchanged) |
| 5 | Happy path (present + successful seed) seeds/appends/uploads, dedup preserved across simulated recycle | ✓ VERIFIED | Independent probe `case_d_happy_path_recycle_dedup`: 2 lines (header+1) after re-seeding across a fresh scratch dir for the same region_id; repo test `test_gs_panel_seeded_from_bucket_dedups_across_recycle` green post-fix, PASSED pre-fix too (expected — pins pre-existing intent, only reachable once the mock's download path was added) |
| 6 | `_existing_region_npz_gs` resume behavior UNCHANGED — stat error still means recompute | ✓ VERIFIED | `git diff 606f293 ff8cc47 -- src/python/run_native_ld_panel.py` shows lowest hunk at old line 224 (nothing touches :186-217); the resume-guard test (`stat_error_uris={f"{gs_out}/afr_err.npz"}`, asserting `len(mock_plink2.calls)==1`) is byte-identical text pre/post (diff-verified) and passes |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/python/run_native_ld_panel.py` | Tri-state fail-CLOSED classifier + refusing seed block in `append_panel_row` | ✓ VERIFIED | New `_gsutil_panel_object_size` (:251-315) + `PanelBucketStateUnknown(RuntimeError)` (:246-248) + rewritten seed block in `append_panel_row` (:627-663); `except: pass` swallow removed; no retry/sleep — raises immediately |
| `tests/m3/test_run_native_ld_panel.py` | 4 tests (2 RED-first + 2 regression) + `_MockGsutil` extended | ✓ VERIFIED | `test_gs_panel_indeterminate_stat_refuses_without_overwriting`, `test_gs_panel_failed_seed_download_refuses_without_overwriting`, `test_gs_panel_definitively_absent_still_starts_fresh`, `test_gs_panel_seeded_from_bucket_dedups_across_recycle` all present and green; `_MockGsutil` extended with `stat_indeterminate_uris`/`stat_raise_uris`/`cp_fail_srcs`/download-direction+`contents` — all opt-in kwargs defaulting `None` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `append_panel_row` | new tri-state classifier (not `_gsutil_object_size`) | panel-seed branch :637 | ✓ WIRED | `existing_size = _gsutil_panel_object_size(gs_uri)` at :637, comment explicitly notes "raises if INDETERMINATE"; `_gsutil_object_size` (fail-OPEN) untouched and used only at :209 |
| `tests/m3/test_run_native_ld_panel.py` | `drv._run_gsutil` | monkeypatch (sole gsutil seam) | ✓ WIRED | All 4 new tests + all 6 pre-existing call sites use `monkeypatch.setattr(drv, "_run_gsutil", ...)`; zero real gsutil/network contact confirmed (grep for direct `subprocess.run(["gsutil"` outside the seam: none) |
| `_existing_region_npz_gs` | `_gsutil_object_size` (untouched) | resume guard :209 | ✓ WIRED, UNCHANGED | `git diff` confirms no hunk touches :186-217; fail-OPEN "assume absent on any error" behavior preserved, load-bearing for the 276-region skip |

### Independent Verification (beyond repo tests)

Wrote a from-scratch mock (`IndependentBucket`, not `_MockGsutil`) and exercised
`append_panel_row` through the monkeypatched seam directly, against both the
**post-fix** module at HEAD (ff8cc47) and the **pre-fix** module loaded via
`importlib` from `git show 606f293:src/python/run_native_ld_panel.py`:

| Scenario | Pre-fix (606f293) | Post-fix (ff8cc47) |
|----------|--------------------|---------------------|
| P3a: INDETERMINATE 503 vs 3 banked rows | No raise; rows 3→1; bucket changed | Raises `PanelBucketStateUnknown`(`RuntimeError`); rows stay 3; bucket byte-identical |
| P3a-ii: `FileNotFoundError` (gsutil missing) | (not separately probed pre-fix; same code path as 503) | Raises; bucket unchanged |
| P3b: stat PRESENT, seed cp fails | No raise; rows 3→1; bucket changed | Raises; rows stay 3; bucket byte-identical |
| Control: definitively absent | No raise; fresh 1-row upload (correct) | No raise; fresh 1-row upload (correct) — both plural and singular `No URL(s) matched` spellings tolerated |
| Happy path + simulated recycle dedup | (not exercised pre-fix in this probe) | 1 row survives fresh-scratch recycle for the same `region_id` (2 lines: header+1) |

Additionally, ran the **repo's own committed test functions** (not a re-implementation)
against the actual pre-fix module content via `importlib` module-cache substitution
(`sys.modules["run_native_ld_panel"]` pointed at the 606f293 content before executing
the test file), to independently confirm the SUMMARY's honesty claim:

```
[test_gs_panel_indeterminate_stat_refuses_without_overwriting]        FAILED (pre-fix): Failed: DID NOT RAISE <class 'RuntimeError'>
[test_gs_panel_failed_seed_download_refuses_without_overwriting]      FAILED (pre-fix): Failed: DID NOT RAISE <class 'RuntimeError'>
[test_gs_panel_definitively_absent_still_starts_fresh]                PASSED (pre-fix)
[test_gs_panel_seeded_from_bucket_dedups_across_recycle]              PASSED (pre-fix)
```

This is an **exact match** to the SUMMARY's claimed pre-fix results — the SUMMARY's
RED record is honest, not contrived.

### Containment Checks (all held)

| Check | Result |
|-------|--------|
| `git diff --stat 606f293 ff8cc47` on frozen contracts (`plink_ld_to_npz.py`, `ld_npz_to_rds.R`, `condition_ld_matrix.py`) | Empty — 0-line diff, confirmed |
| `_gsutil_object_size` / `_existing_region_npz_gs` (:186-217) | No hunk touches this region; lowest hunk starts at old line 224 |
| Resume-guard test (`stat_error_uris`, `len(mock_plink2.calls)==1`) | Byte-identical text pre/post (diff-verified), green |
| `_MockGsutil`'s 6 pre-existing call sites | All construct with either no kwargs or `prestaged={uri:int}`; every new kwarg defaults `None`; behaviorally unchanged (confirmed by code read + the `stat_error_uris` semantics being preserved verbatim at :717) |
| m3-07c modules | Both `occlusion_present_rate_scan.py` and `drop_occluded_from_sumstats.py` confirmed **absent** from `src/python/` |
| Full-suite failure count | Exactly 15 (never dropped below) — 07c not built |
| `_PANEL_COLUMNS` | No diff line touches it (`git diff` grep confirms) |
| u22 header guard (`fe375e7`, "STALE header") | No diff line touches it |
| Tests `:392`/`:1281`/`:1590` (baseline line numbers; content-matched, not line-matched, since the file grew) | All present and green — `test_panel_columns_include_n_dropped_occluded`, `_PANEL_COLUMNS[:7]` assertions, panel-column-list assertion in `test_gs_panel_tsv_uploaded`'s neighbor |
| No auto-repair / no retry-forever | Confirmed — no `sleep`/`retry`/`while True` anywhere in the new classifier or seed block; `except: pass` swallow removed; raises immediately (single attempt) |
| Staging discipline | Only `src/python/run_native_ld_panel.py` + `tests/m3/test_run_native_ld_panel.py` in commit `ff8cc47`; pre-existing dirty files (`.claude/settings.json`, `260625-r6m-SUMMARY.md`, `tests/m3/sparse_parent_benchmark.tsv`) untouched by this commit |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Single-file suite | `pytest tests/m3/test_run_native_ld_panel.py -q` | `58 passed in 1.75s` | ✓ PASS |
| Full suite | `pytest tests/m3 -q` (backgrounded, 384.81s) | `15 failed, 405 passed, 31 skipped` — 9 in `test_occlusion_lockstep_drop.py` + 6 in `test_occlusion_present_rate_scan.py`, all `ModuleNotFoundError` | ✓ PASS — matches expected baseline+4, no regression |
| `size==0` empty-object edge case (not one of the plan's 4 required tests, but part of the tri-state classifier's caller contract) | Ad-hoc probe: empty bucket object, mock raises if a `cp` download is attempted | No raise, no download attempted, fresh mirror starts (lossless, unchanged behavior) | ✓ PASS |

### Requirements Coverage

Quick task (no `.planning/REQUIREMENTS.md` phase mapping applies). Requirements
`P3a`/`P3b` are defined entirely within this task's PLAN frontmatter and are fully
covered by the must-haves table above.

### Anti-Patterns Found

None. Scanned `src/python/run_native_ld_panel.py` (new region :224-315, :609-664) and
`tests/m3/test_run_native_ld_panel.py` (new tests) for TODO/FIXME/placeholder,
empty-handler, and swallowed-exception patterns — none found. The one pre-existing
`except Exception: pass` this fix was meant to eliminate is confirmed removed.

### Human Verification Required

None. This is backend/library-level fail-closed logic fully exercisable through the
monkeypatched subprocess seam; no visual, real-time, or external-service behavior
requires human judgment. All four plan-mandated scenarios (a)-(d) plus two edge
cases (singular absent-signature spelling, `FileNotFoundError` non-`CalledProcessError`
path, `size==0` empty-object path) were independently exercised and match expectations.

### Gaps Summary

No gaps. All 6 must-have truths verified with two independent lines of evidence each
(a from-scratch mock probe against both pre-fix and post-fix module content, plus
re-running the repo's own test functions against the actual pre-fix module to confirm
the SUMMARY's RED/GREEN claims were not contrived). Containment holds: frozen
contracts 0-line diff, `_gsutil_object_size`/`_existing_region_npz_gs` untouched,
`_PANEL_COLUMNS` and the u22 header guard undisturbed, m3-07c not started, full suite
at exactly 15 failed / 405 passed / 31 skipped (baseline 401 + 4 new tests, same two
`ModuleNotFoundError`s split 9+6). One atomic commit (`ff8cc47`) touching only the two
intended files.

---

*Verified: 2026-07-16T03:53:17Z*
*Verifier: Claude (gsd-verifier)*
