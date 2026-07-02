---
phase: quick-260701-qcy
plan: 01-hardening
subsystem: infra
tags: [plink, ld, aou, afr, monomorphic, snplist, provenance, blast-radius, tdd, m3-02e]

# Dependency graph
requires:
  - phase: quick-260701-qcy
    provides: "_retained_window_bim + SQUARE --mac 1 --write-snplist drop-monomorphic (base commit c56c715)"
  - phase: quick-260630-rn4
    provides: "_window_bim_n_var_retry_on_zero transient short-read guard (27af416) — still the raw-window producer, untouched"
provides:
  - "LOUD duplicate-col-2-SNP-id uniqueness assertion in _retained_window_bim (converts a silent LD-row↔variant-id misalignment into a resume-safe ValueError)"
  - "Durable per-region monomorphic-drop provenance: new appended n_dropped_monomorphic panel column + a per-region stderr drop line"
affects: [m3-02e-T4-refire, m3-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Loud uniqueness assertion at an alignment seam that no downstream count/symmetry check can catch (silent-misalignment → loud-failure conversion)"
    - "Append-only panel-schema evolution (never reorder existing columns) + threading the new key through EVERY result dict for schema consistency"

key-files:
  created: []
  modified:
    - "src/python/run_native_ld_panel.py — _retained_window_bim dup-id ValueError (H1); _PANEL_COLUMNS append + process_region drop-count/stderr threading (H2)"
    - "tests/m3/test_run_native_ld_panel.py — H1/H2 failing-first tests; _MockPlink banded --r gz support; panel column-list assertion updated"

key-decisions:
  - "Gate the dup-id raise on snplist-referenced ids (not globally in the window): only a duplicate in the RETAINED/aligned set can misalign LD rows; a duplicate among dropped MAC=0 variants must not false-trip a region"
  - "n_var-mismatch ValueError kept BYTE-IDENTICAL; the uniqueness guard is a SEPARATE, additional raise upstream of it"
  - "n_dropped_monomorphic APPENDED to _PANEL_COLUMNS (never reorder); None on skip/init-error/banded rows; append_panel_row already uses row.get() so schema stays consistent"

patterns-established:
  - "Pattern: convert a silent-catastrophe alignment path into a loud, resume-safe failure when NO existing invariant (count parity, symmetry) can detect it"

requirements-completed: [m3-02e-T4-drop-monomorphic-hardening-D1D2-D4]

# Metrics
duration: ~35min
completed: 2026-07-02
---

# Phase quick-260701-qcy HARDENING: dup-id uniqueness assert + drop-count provenance Summary

**Two blast-radius follow-ups on the SAME square path as the drop-monomorphic fix (base `c56c715`): (H1) `_retained_window_bim` now RAISES a clear `ValueError` naming the region + offending id when a duplicate col-2 SNP id the snplist references would silently misalign LD rows against variant ids — a path no `n_var`-parity or symmetry check catches; (H2) the per-region monomorphic-drop count is now durable provenance via a new appended `n_dropped_monomorphic` panel column plus a loud per-region stderr line.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-07-02
- **Completed:** 2026-07-02
- **Tasks:** 2 (TDD RED, TDD GREEN) + full-suite verify
- **Files modified:** 2

## Accomplishments

### H1 — duplicate-SNP-id uniqueness assertion (blast-radius D1+D2, MEDIUM)
- `_retained_window_bim` keyed the raw window `.bim` by col-2 SNP id with first-occurrence-wins (`by_snp.setdefault`). A DUPLICATE col-2 id that the `--write-snplist` retained set references would silently pick one of two distinct rows and misalign every LD row against the variant ids — and **no existing guard catches it** (`n_var` counts still match, the matrix is still symmetric).
- Added a LOUD guard: while building `by_snp`, if a col-2 id that appears in the retained (snplist-referenced) set is seen more than once in the raw window `.bim`, raise `ValueError(f"ambiguous variant id {snp!r} appears >1x in the window .bim for {region_id} — cannot align LD rows to variant ids")`. Resume-safe: the loop records `status='error: ...'` and continues.
- `region_id` is now threaded into `_retained_window_bim` (keyword-only, default `""`) so the error names the region; the `process_region` SQUARE call site passes it.
- Happy-path behavior is unchanged for unique ids (production `hl.export_plink` varids `chr:pos:ref:alt` ARE unique), verified by a no-false-trip regression.
- Gated on the retained set (not globally in the window) so a duplicate among dropped MAC=0 variants cannot false-trip a region.

### H2 — drop-count observability (blast-radius D4, HIGH/provenance)
- (a) New panel column `n_dropped_monomorphic` **appended** to `_PANEL_COLUMNS` (existing columns keep their exact order/positions). Populated in the SQUARE ok path as `raw_window_n_var - window_n_var`; set to `None` in the skip-idempotent dict, the init/error dict, and the banded branch. `append_panel_row` already dedups via `row.get()`, so the schema stays consistent (no `KeyError`).
- (b) A LOUD per-region stderr line when `n_dropped > 0`: `region {region_id}: dropped {n} monomorphic (MAC=0) variants ({raw} in-window -> {retained} retained)`. plink's own `.log` is reclaimed with the region scratch, so this is the durable run-log evidence of the drop.

## Task Commits

Each task committed atomically (TDD RED then GREEN visible in history):

1. **Task 1: failing-first hardening tests (RED)** — `1a9d170` (test)
2. **Task 2: dup-id assert + drop-count provenance (GREEN)** — `ed9cfd4` (feat)

## Files Created/Modified

- `src/python/run_native_ld_panel.py`
  - `_retained_window_bim(..., *, region_id="")`: new duplicate-id uniqueness `ValueError`; happy path (unique ids) byte-equivalent.
  - `_PANEL_COLUMNS`: append `n_dropped_monomorphic`.
  - `process_region`: skip + init/error result dicts carry `n_dropped_monomorphic: None`; SQUARE ok path computes `raw - retained`, stores it, and emits the loud stderr line; banded branch sets it `None`; SQUARE call passes `region_id=` to `_retained_window_bim`.
- `tests/m3/test_run_native_ld_panel.py`
  - H1: `test_retained_window_bim_raises_on_duplicate_snp_id`, `test_retained_window_bim_unique_ids_do_not_false_trip`.
  - H2: `test_panel_columns_include_n_dropped_monomorphic`, `test_process_region_records_n_dropped_monomorphic`, `test_process_region_logs_drop_to_stderr`, `test_skip_and_error_result_dicts_carry_none_drop_count`, `test_banded_result_dict_carries_none_drop_count`.
  - `_MockPlink` extended to emit a header-only `.ld.gz` for the banded `--r gz` argv (so a banded `process_region` run reaches `status='ok'`); the panel-TSV column-list assertion updated for the appended column.

## Decisions Made

- **Dup-id raise gated on the snplist-referenced set, not globally.** Only a duplicate among the retained/aligned ids can misalign LD rows; a duplicate among dropped MAC=0 variants must not abort a region. This maximizes loudness on the actual failure mode without false-tripping.
- **`n_var`-mismatch `ValueError` kept byte-identical.** The uniqueness guard is a separate, additional raise upstream; the 27af416 transient retry guard, the banded LD logic, and `read_square_bin`/`load_bim` readers are untouched.
- **Append-only schema evolution.** The panel TSV is regenerated fresh for the fire (0/276 banked), so there is no backward-compat concern; still, the column is appended and threaded through every result dict for forward consistency.

## Deviations from Plan

None — the two hardening changes were executed exactly as specified. No auto-fixes (Rules 1-3) were required; scope stayed within the two allowed files.

## Authentication Gates

None.

## Known Stubs

None. The `.snplist` and window `.bim` remain real per-region plink artifacts; no placeholder/empty data paths were introduced. `n_dropped_monomorphic` is a computed provenance value, not a stub.

## Verification

- Module (`tests/m3/test_run_native_ld_panel.py`, smoke_dev py3.11): **45 passed** (RED showed the 8 new + 1 updated tests failing; GREEN all pass).
- Full `tests/m3` suite (R-heavy, m3-r-ld Rscript pin auto-discovered): <!-- SUITE_RESULT -->

---
*Phase: quick-260701-qcy (hardening follow-up)*
*Completed: 2026-07-02*
