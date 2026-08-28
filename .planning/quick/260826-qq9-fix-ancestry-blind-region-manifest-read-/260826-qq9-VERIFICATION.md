---
phase: quick-260826-qq9
verified: 2026-08-28T22:56:00Z
status: passed
score: 16/16 must-haves verified (plus the T4 correction, independently re-verified)
overrides_applied: 0
---

# Quick Task 260826-qq9: Fix ancestry-blind region-manifest read — Verification Report

**Task goal:** Repair `src/python/pairwise_completeness_scan.py` so it reads
`config/ld_regions.tsv` on its real key `(region_id x ancestry)` instead of
`region_id` alone, add a `--ancestry` flag (default `AFR`) mirroring
`run_native_ld_panel._filter_ancestry`, add a duplicate-`region_id` guard at
both the iterator and the driver, reconcile the two `POOLED` denominators by
identity, do it TDD (red-before-green), and bank the contaminated
2026-08-26 sweep with a pre-registered prediction for the re-run.

**Base:** `352ac9e` → **HEAD `1333f3f`** (commits `d8f4d54`, `5078cdc`, `021f26f`, `1333f3f`)
**Verified:** 2026-08-28
**Status:** passed
**Re-verification:** No — initial verification

All checks below were re-derived independently against the live codebase and
a live full-suite run — not taken from the PLAN.md `<verify>` gates or the
SUMMARY.md's claims.

## Goal Achievement

### Observable Truths (from PLAN.md `must_haves.truths`, 16 total)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Manifest read on real key (region_id × ancestry), never region_id alone | ✓ VERIFIED | Live call: `_read_regions_tsv('config/ld_regions.tsv', None)` → **276**; `ancestry='EUR'` → **276**. `awk -F'\t' 'NR>1{print $7}' config/ld_regions.tsv \| sort \| uniq -c` → `276 AFR`, `276 EUR` (553 lines total). AFR/EUR bounds genuinely differ for 123 regions (e.g. `m2_region_00040__sub00`: AFR `(37463740,45398515)` vs EUR `(37463740,47398515)`). |
| 2 | Ancestry predicate is a mirrored, enforced contract (not invented) | ✓ VERIFIED | `_matches_ancestry` present; cross-module `ast`+`exec` enforcer test `test_ancestry_predicate_agrees_with_the_production_filter_contract` exists and passes; `run_native_ld_panel.py` is read-only (0-line diff). All 9 ancestry-tagged tests pass standalone. |
| 3 | Default is load-bearing (`AFR`), PENDING PASTE needs no edit | ✓ VERIFIED | `DEFAULT_ANCESTRY == 'AFR'`; parser `--ancestry` default `== 'AFR'`; `grep -c -- '--ancestry' .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` = **0**; that file is 0-line diff vs `352ac9e`. |
| 4 | Region present only in unrequested ancestry raises, never silently drops | ✓ VERIFIED | Tests `test_region_only_in_the_unrequested_ancestry_raises_naming_the_id` and `test_cli_region_only_in_the_unrequested_ancestry_exits_2_and_writes_no_tsv` present and pass (full-suite 0 failed). |
| 5 | Duplicate `region_id` is defense-in-depth: raises at iterator AND driver; third layer honestly labelled | ✓ VERIFIED | Reproduced live: CONTROL 6 rows `[0..5]`; CASE A (identical bounds) raises `ValueError` naming `'R'`; CASE B (differing bounds) raises, naming `'R'`. Driver's `if region_id in summaries: raise` (src:1507) confirmed unreachable-as-shipped but independently test-demonstrated — see truth #13 below. |
| 6 | Duplicate guard pinned on both real shapes (identical + strictly-inside bounds), CONTROL kept green | ✓ VERIFIED | Same live reproduction as #5. `iter_bim_windows` calls `_assert_unique_region_ids` at line 739 before `specs` is built. |
| 7 | Per-region stdout table prints exactly one line per region_id | ✓ VERIFIED | `test_cli_stdout_table_prints_exactly_one_line_per_region_id` present and passes; unique `windows` guaranteed upstream by `_assert_unique_region_ids`. |
| 8 | Two `POOLED` denominators are ONE basis, reconciled by a raising identity check, before `write_tsv` | ✓ VERIFIED | Code inspection: `pooled_candidate_rows = sum(s["n_candidate_rows"] for s in summaries.values())`; `if pooled_candidate_rows != len(all_results): raise ValueError(...)` at src:1531-1539, BEFORE `write_tsv(all_results, args.out)` at src:1541. All three `POOLED` stdout lines carry `basis: per-region summaries` (2 unwrapped + 1 line-wrapped = 3 by tolerant count — see Known Issue below). |
| 9 | 2-ancestry manifest end-to-end regression emits exactly N rows, never 2N/4N/8N | ✓ VERIFIED | `test_two_ancestry_manifest_emits_no_inflated_counts_end_to_end` present and passes. |
| 10 | Contaminated sweep banked verbatim from the AS-RECEIVED artifact, with CONTAMINATED/ZERO-ON-A-CONTAMINATED-BASIS/SURVIVING labelling | ✓ VERIFIED | `260826-qq9-AS-RECEIVED-step3-and-forensics.md` re-measured: **8397 B**, md5 `22cbdd99b8d8714bfe2f22a2b499e58a` — byte-unchanged. All 19 required needles present in the debug record (Python re-check, tolerant of thousands-separators): `PRE-REGISTERED PREDICTION`, `CONTAMINATED`, region IDs, coordinate strings, `2865513`, `1412356`, `1453157`, `393887`, both two-row pair_keys, `pcs_00057_crosscheck.tsv`, `uniq -c`, and the offset-histogram pattern. |
| 11 | Two denominators reconciled: `2,865,513 = 1,412,356 + 1,453,157`; `wc -l` = pooled + 1; ratio 1.972 explained | ✓ VERIFIED | Present in debug record section (b1), with the explicit AFR⊆EUR-for-9-subNN-regions explanation for why the ratio is 1.972 not 2.000. |
| 12 | Identity table re-derived from BLOCK 2 by script: 15 rows, multiplicity uniformly 8, `{-14:1,-9:1,-6:1,-3:1,-1:1,0:10}`, 13 pairs, 10/3; `13+2=15` reconciled by naming both two-row pair_keys; 5-vs-3 undercount stated | ✓ VERIFIED | Present verbatim in debug record section (c); histogram independently re-summed (below) sums to 15. |
| 13 | Re-run's expectation PRE-REGISTERED before the re-run, mismatch = finding not adjustment | ✓ VERIFIED | Section (e) present: 15 rows / 13 pairs / 10-3 / `{-14:1,-9:1,-6:1,-3:1,-1:1,0:10}` — independently summed: **15**. States explicitly the re-run has NOT happened. |
| 14 | No criterion/threshold/policy moved — frozen surfaces + OSF paste block byte-unchanged | ✓ VERIFIED | `git diff --stat 352ac9e HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py src/python/aou_ld_panel.py .planning/amendments/` = **empty**. OSF paste block re-extracted with the safe two-step file form: **22945 B**, md5 `13a49f543cabcc27ce9f1e589783c060` — exact match. |
| 15 | Suite re-baselined honestly, component-exact, 0 failed, skips stay 33 | ✓ VERIFIED | **Live full-suite re-run: `1122 passed, 33 skipped, 0 failed` in 970.73s.** Independent collect-only cross-checks: non-scanner files = **1054** (unchanged); scanner file alone = **101** (80 baseline + 20 T1-T3 + 1 T4). `1054 + 101 = 1155 = 1122 + 33`. |
| 16 | Shared GPFS tree not trampled; pre-existing untracked entries left as found; `sparse_parent_benchmark.tsv` restored not staged | ✓ VERIFIED | `git status --porcelain` before and after the full-suite run shows the identical untracked-entry set as the session-start snapshot, plus the expected `.planning/STATE.md` modification (see Note below). `sparse_parent_benchmark.tsv` was dirtied by the live suite run and restored with `git checkout --`, confirmed clean afterward, never staged. |

**Score:** 16/16 truths verified.

### T4 correction (post-plan, independently re-verified per this task's explicit checklist)

| Check | Status | Evidence |
|---|---|---|
| Stale string "NO committed test can" absent from `src/` and `tests/` | ✓ VERIFIED | `grep -rn "NO committed test can" src/ tests/` → no matches. |
| Correction landed in module comment | ✓ VERIFIED | src:1483 `# LAYER 3 — UNREACHABLE IN THE SHIPPED CONFIGURATION, BUT TESTED.` through src:1503. |
| Correction landed in sibling CLI test's docstring | ✓ VERIFIED | `test_cli_duplicate_region_id_manifest_exits_2_and_writes_no_tsv` docstring (tests:3049-3067) explicitly names the new test and states the earlier claim was wrong in general. |
| Correction landed in debug record's enforcer table | ✓ VERIFIED | Debug record line 361: cell now names `test_driver_summaries_guard_independently_refuses_last_wins_with_both_upstream_layers_disabled`, not "none". |
| **Negative control reproduced live by this verifier**: delete `if region_id in summaries: raise`, confirm the new test goes RED | ✓ VERIFIED | Deleted the 5-line branch at src:1507-1511, ran `pytest -k test_driver_summaries_guard_independently_refuses_last_wins_with_both_upstream_layers_disabled` → **1 failed**, with the assertion failing on `"evaluated twice" in str(excinfo.value)` because the POOLED-denominator identity check caught it instead (`sum...= 4 but the emitted TSV carries 8...`) — exactly the mechanism the SUMMARY describes. |
| **Restored with `git checkout --`, verified guard AND new comment block both present** | ✓ VERIFIED | `git diff -- src/python/pairwise_completeness_scan.py` → 0 lines after restore. `grep -n "if region_id in summaries"` → line 1507 present. `grep -n "LAYER 3 — UNREACHABLE IN THE SHIPPED CONFIGURATION"` → line 1483 present. Re-ran the specific test after restore: **1 passed**. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `src/python/pairwise_completeness_scan.py` | ≥1400 lines, contains `_REGIONS_TSV_ANCESTRY_COL` | ✓ VERIFIED | 1582 lines; 4 occurrences of the constant/comment. |
| `tests/m3/test_pairwise_completeness_scan.py` | ≥2700 lines, contains `_matches_ancestry` | ✓ VERIFIED | 3370 lines; 96 top-level `def test_` functions (101 collected items incl. parametrization); 7 occurrences of `_matches_ancestry`. |
| `.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md` | ≥120 lines, contains `PRE-REGISTERED PREDICTION` | ✓ VERIFIED | 580 lines; section (e) present with exact histogram. |
| `.planning/HANDOFF.json` | contains `suite_baselines` | ✓ VERIFIED | Present; `suite_baselines["tests/m3"]` correctly REPLACES (not appends) the prior 1101/33/0 entry with 1121/33/0 (T1-T3 baseline) — see Anti-Patterns note below re: T4's +1 not reflected. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `_read_regions_tsv` | manifest column 7 (0-based 6) | `_REGIONS_TSV_ANCESTRY_COL=6` + `_matches_ancestry`, default `AFR` | ✓ WIRED | `grep -n "_REGIONS_TSV_ANCESTRY_COL\s*=\s*6"` → src:1215. |
| `_matches_ancestry` | `run_native_ld_panel._filter_ancestry` (read-only) | ast-extracted source, exec'd in a test | ✓ WIRED | Enforcer test present and passing; production file 0-line diff. |
| `iter_bim_windows` | `_assert_unique_region_ids` | call before `specs` built | ✓ WIRED | src:739, before `specs = [...]` at src:742. |
| `main()` driver loop | `summaries` dict | refuse-to-overwrite raise | ✓ WIRED | src:1507 `if region_id in summaries:`. |
| POOLED stdout block | `summaries.values()` sum | must-be-identity assertion vs `len(all_results)` | ✓ WIRED | src:1531-1539, raises before `write_tsv` at src:1541. |
| debug record | `260826-qq9-AS-RECEIVED-step3-and-forensics.md` | verbatim BLOCK 1/BLOCK 2 splice | ✓ WIRED | 1 occurrence of the filename reference; content matches byte-verified source. |
| debug record | `260825-PENDING-PASTE-pairwise-completeness-sweep.md` STEP 3 | names the exact banked command | ✓ WIRED | 1 occurrence; PENDING PASTE itself confirmed 0-line diff. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Real-data ancestry filter returns 276/276, never 552 | `_read_regions_tsv('config/ld_regions.tsv', None[, ancestry='EUR'])` | AFR 276, EUR 276 | ✓ PASS |
| Duplicate-id guard: CONTROL/CASE A/CASE B | live `iter_bim_windows` calls on synthetic 6-row `.bim` | CONTROL 6 rows `[0..5]`; CASE A raises; CASE B raises | ✓ PASS |
| Full test suite | `pytest tests/m3 -q` | 1122 passed, 33 skipped, 0 failed, 970.73s | ✓ PASS |
| Scanner file alone | `pytest tests/m3/test_pairwise_completeness_scan.py -q` | 101 passed | ✓ PASS |
| T4 negative control | delete driver guard branch, run the specific test | 1 failed (as expected — POOLED identity catches it instead) | ✓ PASS |
| T4 restore integrity | `git checkout --`, re-run same test | 1 passed, 0-line diff | ✓ PASS |
| Frozen-surface diff | `git diff --stat 352ac9e HEAD -- <5 frozen paths>` | empty | ✓ PASS |
| OSF paste block | safe two-step file extraction + `wc -c` + `md5sum` | 22945 B / `13a49f543cabcc27ce9f1e589783c060` | ✓ PASS |

### Requirements Coverage

The 10 requirement IDs in this plan's frontmatter (`PCS-FIX-ANCESTRY-BLIND-MANIFEST-READ`, `PCS-CLI-ANCESTRY-FLAG-DEFAULT-AFR`, `PCS-ANCESTRY-CONTRACT-MIRRORS-PRODUCTION`, `PCS-DUPLICATE-REGION-ID-RAISES-ITER`, `PCS-DUPLICATE-REGION-ID-RAISES-DRIVER`, `PCS-POOLED-DENOMINATOR-RECONCILED`, `PCS-DEBUG-RECORD-CONTAMINATION-AND-SURVIVORS`, `PCS-PREREG-PREDICTION-BEFORE-RERUN`, `PCS-FROZEN-SURFACES-UNCHANGED`, `PCS-SUITE-REBASELINE`) are quick-task-local IDs, not present in `.planning/REQUIREMENTS.md` (confirmed by grep — expected for a quick task, which does not draw from the milestone requirements ledger). All 10 map 1:1 onto the truths table above and are SATISFIED. No orphaned milestone requirements apply to this quick task.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `src/python/pairwise_completeness_scan.py` | T1-T4 diff | none (TODO/FIXME/placeholder/debug-print scan clean) | — | — |
| `.planning/HANDOFF.json` | `suite_baselines["tests/m3"]` | States `1121 passed / ... 1154 collected` (the T1-T3 baseline); does not reflect T4's +1 (actual current-state truth is `1122 passed / 1155 collected`, confirmed by live run) | ℹ️ Info | Non-blocking. T4 was a correction added after the original PLAN.md's three tasks and after T3's HANDOFF.json update; T4 itself did not re-touch HANDOFF.json. The SUMMARY.md correctly states 1122 as the final number, so the discrepancy is confined to one JSON field and does not misrepresent the code's correctness — but a future resuming agent reading only HANDOFF.json would see a number 1 test short of the live baseline. Recommend a trivial follow-up correcting `suite_baselines["tests/m3"]` to 1122/33/0/1155 the next time this file is touched. |

**Known, already-flagged, non-blocking gate defect (confirmed, not re-reported as new):** T2's `<verify>` gate `grep -c 'basis: per-region summaries' >= 3` returns **2** against the correct, committed code — confirmed live. The third occurrence is line-wrapped across two source lines (`"basis: per-region "` + `f"summaries): ..."`). A line-wrap-tolerant `grep -c 'basis: per-region'` returns **3**, confirming all three POOLED lines do carry a basis in-line. This is a defect in the plan's automated gate regex, not in the shipped code — consistent with the SUMMARY's own disposition.

**Confirmed no live second writer:** `ps aux` shows two Claude Code processes attached to this GPFS working tree — one matching this session's own resume ID, one without `--resume` (likely this session's original pre-resume invocation, not a concurrent writer). `git status --porcelain` for the specific files this quick modified (`pairwise_completeness_scan.py`, `test_pairwise_completeness_scan.py`, the debug record, `HANDOFF.json`) shows zero pending changes — only `.planning/STATE.md` is modified, which matches T3's explicitly documented deviation ("STATE.md is written and current on disk but is left for the orchestrator's atomic commit"). The tree is coherent.

### Human Verification Required

None. This task is a backend instrument repair (parsing logic, guard clauses, denominator arithmetic, and a documentation record) with no UI, no visual output, and no external service integration — every must-have is programmatically verifiable, and every one was independently re-derived above (not merely re-read from the SUMMARY).

### Gaps Summary

No gaps. All 16 must-have truths, all 4 required artifacts, all 7 key links, and the T4 correction (independently re-verified via a live negative control this verifier ran itself) hold against the actual codebase and a live 1122/33/0 full-suite run. The single minor finding (HANDOFF.json's suite baseline undercounting by 1 test after T4) is informational and non-blocking — it does not affect code correctness, test coverage, or the debug record's integrity, and is called out above for a trivial future correction.

---

_Verified: 2026-08-28T22:56:00Z_
_Verifier: Claude (gsd-verifier)_
