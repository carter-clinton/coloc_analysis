---
phase: quick-260701-qcy
verified: 2026-07-02T18:26:29Z
status: passed
score: 7/7 must-haves verified
overrides_applied: 0
deferred:
  - truth: "The emitted region-1 .ld.bin from the REAL 73k-AFR cohort is NaN-free and read_square_bin passes on it (empirical, not mock)"
    addressed_in: "m3-02e-T4 re-fire (post-land AoU operational gate)"
    evidence: "PLAN post_land_operational block explicitly scopes this OUT of the NCSU task ('NOT an NCSU task — for the AoU agent AFTER this fix pushes'); SUMMARY affects=[m3-02e-T4-refire, m3-04]; the region-1-only re-run passing read_square_bin is step 4 of the post-land gate"
---

# Phase quick-260701-qcy: Drop monomorphic (MAC=0-in-AFR) variants from the native-plink LD panel — Verification Report

**Phase Goal:** Drop monomorphic (MAC=0-in-AFR) variants from the native-plink LD panel so plink never emits NaN LD and read_square_bin's symmetry check passes. Decision LOCKED = drop MAC=0.
**Verified:** 2026-07-02T18:26:29Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | SQUARE plink command drops MAC=0 via `--mac 1` BEFORE `--r square`, emitting an (n_retained)^2 `.ld.bin` with NO NaN so read_square_bin's symmetry check passes | VERIFIED | `aou_ld_panel.py:2902` SQUARE branch appends `["--mac", "1", "--nonfounders", "--write-snplist", "--r", "square", "bin4"]`. plink1.9 order-of-ops (window → `--mac` → `--write-snplist` → `--r`) is the documented mechanism (RESEARCH HIGH). NaN-free-on-real-cohort empirical proof is the deferred AoU gate (see Deferred). |
| 2 | `--write-snplist` gives RETAINED variant IDs in `.ld.bin` row order; the converter aligns to that order (n_var == len(retained)) | VERIFIED | `--write-snplist` on `aou_ld_panel.py:2902`; `run_native_ld_panel.py:568` calls `_retained_window_bim(raw_window_bim, snplist_path)` which reads `{out_prefix}.snplist` and re-orders the raw window `.bim` to snplist order (`:374-388`); `:575` sets `n_var = window_n_var` (= retained count); `:585-588` passes retained `window_bim` + `n_var` to `plink_ld_to_npz`. |
| 3 | The `bin_n_var != window_n_var` cross-check compares RETAINED == RETAINED (uses the snplist), NOT the raw in-window `.bim` count | VERIFIED | `run_native_ld_panel.py:556` `bin_n_var = _n_var_from_ld_bin` (= sqrt(bytes/4) = n_retained); `:559-561` the raw guarded read is bound to `raw_window_n_var`/`raw_window_bim` (raw count now UNUSED in the check); `:568` `window_n_var` = retained count; `:569` compares `bin_n_var != window_n_var` → retained==retained. |
| 4 | A genuine bin/window disagreement still raises the BYTE-IDENTICAL `n_var mismatch` ValueError | VERIFIED | `git show c56c715` shows NO +/- lines touch the message string (`:570-574`); a snplist id absent from the raw `.bim` is skipped (`:384`) so a real disagreement still trips the check. |
| 5 | read_square_bin / load_bim / symmetry+diagonal+OOM-bounded checks UNCHANGED; banded branch + resume skip/continue UNCHANGED | VERIFIED | `git diff c90a629 HEAD -- src/python/plink_ld_to_npz.py` is EMPTY (byte-unchanged); `read_square_bin` symmetry raise still at `plink_ld_to_npz.py:189`; feat diff `c56c715` touches no banded-path / resume-skip / `_existing_region_npz` lines. |
| 6 | A NaN-bearing square `.ld.bin` still deterministically RAISES `square LD is not symmetric` | VERIFIED | Regression `test_read_square_bin_raises_on_monomorphic_nan` exists (587c3d4) and PASSES live; the reader itself is unmodified. |
| 7 | tests/m3 stays green (baseline 309 passed / 30 skipped; new tests add to passed) | VERIFIED | Scratchpad marker `full_suite_DONE.txt` = "314 passed, 30 skipped in 3795.05s" (= 309 + 5 new); the 5 new tests re-run live here = 5 passed in 17.21s. |

**Score:** 7/7 truths verified

### Deferred Items

Items not verifiable on NCSU and explicitly scoped by the plan as a downstream operational gate. Do NOT affect status.

| # | Item | Addressed In | Evidence |
| --- | --- | --- | --- |
| 1 | Region-1 re-run on the REAL 73k-AFR cohort emits a NaN-free, symmetric `.ld.bin` (read_square_bin passes; n_var slightly < 102,421) | m3-02e-T4 re-fire (post-land AoU gate) | PLAN `post_land_operational` block: "NOT an NCSU task — for the AoU agent AFTER this fix pushes"; step 4 = region-1-only re-run must pass read_square_bin before the full 276-region fire. SUMMARY `affects: [m3-02e-T4-refire, m3-04]`. |

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `src/python/aou_ld_panel.py` | build_plink_ld_command SQUARE emits `--mac 1 --nonfounders --write-snplist` | VERIFIED | `:2902`; banded `else` branch (`:2903-2909`) has no `--mac`; `--keep-allele-order`/`--r square bin4` retained. |
| `src/python/run_native_ld_panel.py` | `_retained_window_bim` helper; SQUARE process_region threads the retained snplist so n_var==len(retained) | VERIFIED | `_retained_window_bim` at `:348-388`; threaded at `:568`; guard `_window_bim_n_var_retry_on_zero` preserved as raw-window producer at `:559-561`. |
| `tests/m3/test_run_native_ld_panel.py` | `_MockPlink` honors `--write-snplist`; drop/order/flags/guard tests | VERIFIED | `_MockPlink` gains `mono_snps` + `.snplist` emission (587c3d4); 4 new tests present, all pass. |
| `tests/m3/test_plink_ld_to_npz.py` | NaN-`.ld.bin` regression asserting read_square_bin RAISES `not symmetric` | VERIFIED | `test_read_square_bin_raises_on_monomorphic_nan` present + passes. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| build_plink_ld_command (square) | plink argv | append `--mac 1 --nonfounders --write-snplist` | WIRED | `aou_ld_panel.py:2902` |
| process_region (square) | `_retained_window_bim` | intersect raw window `.bim` with `{out_prefix}.snplist` in snplist order | WIRED | `run_native_ld_panel.py:567-568` |
| `_retained_window_bim` | plink_ld_to_npz (unchanged) | pass retained-order `.bim` + `n_var=len(retained)` | WIRED | `run_native_ld_panel.py:585-588` (`bim_path=window_bim, n_var=n_var`) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| 5 new tests pass in current tree | `pytest` on the 5 named tests (smoke_dev env) | `5 passed in 17.21s` | PASS |
| Full suite green above baseline | scratchpad `full_suite_DONE.txt` | `314 passed, 30 skipped` | PASS |
| Flags test asserts banded lacks `--mac`/`--write-snplist`/`--nonfounders` | inspect test body | `assert "--mac" not in bd` etc. present | PASS |
| plink_ld_to_npz.py byte-unchanged | `git diff c90a629 HEAD -- src/python/plink_ld_to_npz.py` | empty | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| m3-02e-T4-drop-monomorphic-mac0 | 260701-qcy-PLAN | Drop MAC=0 monomorphic-in-AFR variants from the native-plink LD panel (per-region `--mac 1 --write-snplist`, thread the retained snplist) | SATISFIED | Truths 1-7 all VERIFIED; code + tests landed + green on NCSU. |

### Anti-Patterns Found

None. No TODO/FIXME/placeholder introduced. `_retained_window_bim` writes a real retained `.bim` from the actual plink `.snplist` (no hardcoded empty data). Guard preservation is real (the retry-on-zero call remains the raw-window producer), locked by an integration-level test distinct from the existing unit-level guard tests.

### Human Verification Required

None for this NCSU task. The only empirical/external item (region-1 `.ld.bin` NaN-free on the real AoU cohort) is a DEFERRED downstream operational gate owned by the AoU agent in the m3-02e-T4 re-fire (see Deferred Items) — the plan explicitly scopes it out of this task.

### Gaps Summary

No gaps. All 7 must-have truths are verified against the actual codebase:
- SQUARE branch emits `--mac 1 --nonfounders --write-snplist`; banded branch is untouched (no `--mac`).
- The 27af416 transient short-read guard is preserved as the raw-window producer; `_retained_window_bim` consumes its output and threads the plink `.snplist` so the cross-check compares retained==retained and `load_bim` aligns to the retained columns.
- The `n_var mismatch` ValueError message is byte-identical (git-confirmed).
- `plink_ld_to_npz.py` (read_square_bin / load_bim / content_verify_npz), the banded path, and the resume skip/continue semantics are unchanged.
- The NaN-`.ld.bin` regression locks the diagnosis; the full tests/m3 suite is 314 passed / 30 skipped (309 baseline + 5 new), and the 5 new tests were independently re-run here (5 passed).

The empirical region-1 re-run against the real 73k-AFR cohort remains the documented post-land AoU operational gate (deferred, not a gap). The NCSU code-fix deliverable is complete and verified; it is inert until pushed (origin tip must == local HEAD before any AoU pull, per [[feedback_push_ncsu_before_aou_clone_fire]]).

---

_Verified: 2026-07-02T18:26:29Z_
_Verifier: Claude (gsd-verifier)_
