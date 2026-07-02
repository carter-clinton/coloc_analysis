---
phase: quick-260701-qcy
plan: 01
subsystem: infra
tags: [plink, ld, aou, afr, monomorphic, mac, snplist, tdd, m3-02e]

# Dependency graph
requires:
  - phase: quick-260630-rn4
    provides: "_window_bim_n_var_retry_on_zero transient short-read guard (27af416) — preserved, still the raw-window producer"
  - phase: m3-02e-T4
    provides: "native-plink LD loop driver (run_native_ld_panel.py) + build_plink_ld_command + plink_ld_to_npz readers"
provides:
  - "SQUARE plink LD command drops MAC=0 (monomorphic-in-AFR) variants via --mac 1 --nonfounders --write-snplist so plink never emits NaN LD and read_square_bin's symmetry check passes"
  - "_retained_window_bim helper threading the plink .snplist so per-region n_var == retained polymorphic count and the .npz variant list aligns to the retained set"
affects: [m3-02e-T4-refire, m3-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-region --mac 1 + --write-snplist (drop monomorphic BEFORE --r), snplist threaded through the converter for .ld.bin/.bim/n_var/.npz alignment"
    - "Reusable helper + failing-first regression for a recurrent alignment/verify bug class ([[feedback_extract_reusable_utilities]])"

key-files:
  created: []
  modified:
    - "src/python/aou_ld_panel.py — build_plink_ld_command SQUARE branch emits --mac 1 --nonfounders --write-snplist"
    - "src/python/run_native_ld_panel.py — new _retained_window_bim; process_region SQUARE path threads the retained snplist"
    - "tests/m3/test_run_native_ld_panel.py — _MockPlink honors --write-snplist; drop/order/flags/guard-preservation tests"
    - "tests/m3/test_plink_ld_to_npz.py — NaN-.ld.bin regression locking read_square_bin RAISE"

key-decisions:
  - "Per-region --mac 1 + --write-snplist (not a one-time bfile pre-filter): no new ~354 GB artifact on the disk-tight loop VM; cohort-wide MAC makes the two equivalent"
  - "Include --nonfounders as cheap insurance so --mac counts all samples regardless of .fam parent columns"
  - "read_square_bin / load_bim / symmetry+diagonal+OOM-bounded checks LEFT UNCHANGED — they CAUGHT the NaN; they are correct"

patterns-established:
  - "Pattern: plink filter order-of-operations (window -> --mac -> --write-snplist -> --r) leveraged to drop zero-variance variants before LD export"

requirements-completed: [m3-02e-T4-drop-monomorphic-mac0]

# Metrics
duration: ~90min
completed: 2026-07-02
---

# Phase quick-260701-qcy: Drop monomorphic (MAC=0-in-AFR) variants from the native-plink LD panel Summary

**SQUARE plink LD now drops MAC=0 monomorphic-in-AFR variants via `--mac 1 --nonfounders --write-snplist` (no `0/0 -> NaN` LD), and the driver threads the retained `.snplist` so `n_var`, the window `.bim`, and the `.npz` variant list align to the retained polymorphic set — read_square_bin's symmetry check passes.**

## Performance

- **Duration:** ~90 min
- **Started:** 2026-07-02
- **Completed:** 2026-07-02
- **Tasks:** 3 (TDD RED, TDD GREEN, verify+commit)
- **Files modified:** 4

## Accomplishments
- Root-caused fix landed for the m3-02e-T4 fire #3 region-1 symmetry-check failure: ~11 monomorphic (MAC=0-in-AFR) variants made plink `--r` emit NaN LD (`0/0`), and `NaN != NaN` broke `read_square_bin`'s symmetry check. Systemic across the 276 windows.
- `build_plink_ld_command` SQUARE branch emits `--mac 1 --nonfounders --write-snplist`; the banded branch is untouched.
- New reusable `_retained_window_bim(raw_window_bim, snplist_path)` intersects the raw in-window `.bim` with the plink `.snplist` in snplist (== `.ld.bin`) order; `process_region` SQUARE path threads it so `n_var == len(retained)` and `load_bim` aligns to the retained columns.
- The 27af416 transient short-read retry guard is PRESERVED: `_window_bim_n_var_retry_on_zero` remains the producer of the raw window `.bim`; only the cross-check operand moved to the retained count. The `n_var mismatch` ValueError message is byte-identical (git diff shows no +/- on the string).
- NaN-`.ld.bin` regression locks the diagnosis: `read_square_bin` RAISES `square LD is not symmetric` on a monomorphic-NaN matrix; the reader itself is NOT modified.

## Task Commits

Each task was committed atomically (TDD RED then GREEN visible in history):

1. **Task 1: failing-first drop-monomorphic tests** - `587c3d4` (test)
2. **Task 2: emit flags + thread retained snplist** - `c56c715` (feat)
3. **Task 3: full-suite verify + STATE/HANDOFF refresh** - metadata commit (docs)

## Files Created/Modified
- `src/python/aou_ld_panel.py` - `build_plink_ld_command` SQUARE branch appends `--mac 1 --nonfounders --write-snplist`; docstring notes the monomorphic-drop + retained-set semantics.
- `src/python/run_native_ld_panel.py` - new `_retained_window_bim`; SQUARE `process_region` threads the retained snplist (guard-preserving); comments note `n_var` now excludes MAC=0 variants.
- `tests/m3/test_run_native_ld_panel.py` - `_MockPlink` honors `--write-snplist` (drops `mono_snps`, emits `.snplist`, sizes `.ld.bin` to retained^2); tests (a) flags, (b) drop/align, (c) snplist-order reorder, (e) guard-preservation integration.
- `tests/m3/test_plink_ld_to_npz.py` - NaN-`.ld.bin` regression asserting `read_square_bin` RAISES `not symmetric`.

## Decisions Made
- **Per-region `--mac 1 --write-snplist`, not a one-time bfile pre-filter.** The loop VM's 1 TB PD is ~588 GB used; a second ~354 GB filtered bfile is infeasible + a re-stage risk. Cohort-wide MAC makes per-region and global filtering equivalent for correctness, so per-region wins on disk/blast-radius (RESEARCH Q6; CLAUDE.md rigor-over-speed).
- **`--nonfounders` included** as cheap insurance so `--mac` counts all samples even if a `.fam` ever had nonzero parent columns (RESEARCH Pitfall 3; zero downside for an all-founder `hl.export_plink` cohort).
- **`read_square_bin` / `load_bim` / OOM-bounded checks left unchanged** — they caught the NaN and are correct; the fix is upstream (drop the monomorphic rows before LD).

## Deviations from Plan

None - plan executed exactly as written. No auto-fixes (Rules 1-3) were required; the two checker warnings were already folded into the plan and were honored:
- **Checker warning 1 (guard preservation):** `_window_bim_n_var_retry_on_zero` remains the raw-window producer; `_retained_window_bim` consumes its output; only the cross-check operand changed. An integration-level guard-preservation test (`test_square_path_still_routes_through_transient_guard`) locks this distinct from the existing unit-level guard tests.
- **Checker warning 2 (STATE keep-current):** STATE.md + HANDOFF.json were refreshed in Task 3 (see below).

## Issues Encountered
None during planned work. Note: the `tests/m3` full suite is R-subprocess-heavy (reticulate/susieR/coloc via the `m3-r-ld` Rscript pin) and takes ~45-60 min wall; a concurrently-launched baseline run was killed to free CPU for the post-fix run.

## Authentication Gates
None.

## Known Stubs
None. The `.snplist` is a real per-region plink artifact; no placeholder/empty data paths were introduced.

## STATE/HANDOFF Refresh

Per plan Task 3 and `[[feedback_state_md_keep_current]]`, `.planning/STATE.md` and `.planning/HANDOFF.json` were updated in this executor to record: drop-monomorphic fix LANDED + green; re-fire PENDING = push origin -> AoU `git pull` >= new HEAD on the SAME n1-standard-32 (NO respec) -> REGION-1-ONLY re-run passes `read_square_bin` -> full 276. These are included for the orchestrator's final metadata commit (explicit paths).

## Next Phase Readiness
- Fix is landed + green on NCSU. **Not yet pushed** — the fix is inert on AoU until `origin` tip == local HEAD ([[feedback_push_ncsu_before_aou_clone_fire]]).
- Post-land operational gate (AoU agent, NOT NCSU): push origin -> `git pull` on the loop VM (n1-standard-32, NO respec) -> re-gate (`grep write-snplist`) -> **run REGION 1 ONLY** and confirm `read_square_bin` passes (no NaN, symmetric; `n_var` slightly < 102,421) -> only then launch the full 276-region loop.

---
*Phase: quick-260701-qcy*
*Completed: 2026-07-02*
