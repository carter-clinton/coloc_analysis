---
phase: 260625-r6m
plan: 01
subsystem: m3-aou-afr-ld-panel
tags: [m3-02e, native-plink, ld-panel, resumable, idempotent, content-verify, egress]
requires:
  - aou_ld_panel._existing_region_npz (MED-6 byte-floor resume guard)
  - aou_ld_panel.build_plink_ld_command (--keep-allele-order hardcoded)
  - aou_ld_panel._read_manifest
  - plink_ld_to_npz.plink_ld_to_npz (.ld.bin/.ld.gz -> egress-clean .npz)
provides:
  - src/python/run_native_ld_panel.py (resumable native-plink LD loop driver, STEP 4)
  - run_native_ld_panel / process_region / content_verify_npz / append_panel_row / main
affects:
  - m3-02e-AFR-NATIVE-FIRE-BRIEF.md STEP 4 (re-pointed to the driver) + STEP 5 (inline verify is primary)
tech-stack:
  added: []
  patterns:
    - "Single subprocess seam (_run_plink) so tests monkeypatch exactly one function."
    - "Reuse the existing MED-6 resume guard (out_bucket=None keeps it hail-free) rather than a bare [ -f ] check."
    - "Per-region content verification (D-M3-10) returns (ok, reason); failures continue the loop, never abort."
    - "Resume-safe TSV append: header once, dedup by region_id."
key-files:
  created:
    - src/python/run_native_ld_panel.py
    - tests/m3/test_run_native_ld_panel.py
  modified:
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-02e-AFR-NATIVE-FIRE-BRIEF.md
decisions:
  - "A corrupt square .ld.bin is rejected at conversion (plink_ld_to_npz's own square checks) -> status='error: ...', a non-ok failure that still continues the loop; the inline content_verify_npz gate is the second, redundant D-M3-10 guard for any .npz that passes conversion. The one-bad-region test accepts either non-ok status."
  - "content_verify_npz returns (ok, reason) instead of raising, so the loop records the per-region status and continues (DoS mitigation T-260625-r6m-05)."
metrics:
  duration: ~70 min (incl. ~48 min full-suite gate)
  completed: 2026-06-25
  tasks: 3
  files: 3
requirements: [REQ-AOU-LD-EGRESS, D-M3-10, MED-6, T-M3-02e-SIGN, D-02e-01]
---

# Phase 260625-r6m Plan 01: Resumable native-plink LD loop driver Summary

Built `src/python/run_native_ld_panel.py` — the turnkey, idempotent, content-verified
loop driver that turns m3-02e STEP 4 (previously hand-described bash) into a single
re-runnable script, the only thing that was blocking the billable STEP-4 AFR LD fire.

## What was built

- **`src/python/run_native_ld_panel.py`** (368 lines, hail-free at module scope).
  Exports `run_native_ld_panel`, `process_region`, `content_verify_npz`,
  `append_panel_row`, `main`. Per region it: skips-if-banked via the REUSED
  `aou_ld_panel._existing_region_npz` (MED-6 `_MIN_REGION_NPZ_BYTES` floor, called
  with `out_bucket=None` to stay on the hail-free local-dir branch); else issues
  plink ONLY through `aou_ld_panel.build_plink_ld_command` (so `--keep-allele-order`
  is always present and the argv is never hand-rolled); builds a window-subset `.bim`
  (so `load_bim` row order == the `.ld.bin` row order) and cross-checks the n_var
  derived from the `.ld.bin` size against the window `.bim` row count; converts via
  `plink_ld_to_npz.plink_ld_to_npz`; content-verifies inline (`content_verify_npz`,
  D-M3-10); and appends a resume-safe row to `m3-W2-native-plink-panel.tsv`. A bad
  region records a non-ok status and the loop CONTINUES.

- **`tests/m3/test_run_native_ld_panel.py`** (396 lines, 11 tests). plink mocked at
  the single `_run_plink` seam (writes a synthetic square `.ld.bin`, records argv).
  Coverage: no-module-scope-hail-import, resume-skip = zero plink work on a second
  run, MED-6 floor rejects a truncated `.npz` (not a bare `[ -f ]`), content-verify
  rejects non-symmetric / wrong-diagonal npz, one bad region does not abort the loop,
  panel TSV append resume-safe (one header, no dup rows, correct columns),
  `--keep-allele-order` on every issued argv + obtained via the helper (AST: not
  hand-rolled), AFR-only filtering, retired-Hail-path absence, no hardcoded abs paths.

- **`m3-02e-AFR-NATIVE-FIRE-BRIEF.md`** STEP 4 re-pointed to a single
  `python src/python/run_native_ld_panel.py` invocation (idempotent across Spot
  preemption); STEP 5 note marks the driver's inline verify as the primary D-M3-10
  gate (the standalone numpy check is now the spot re-check). STEP 0-3 and 6-7 are
  untouched (the production-VM re-measure gate stays a blocking pre-loop step).

## Threat register dispositions (all `mitigate` items satisfied)

- **T-260625-r6m-01** (truncated `.npz` from preemption): REUSED `_existing_region_npz`
  MED-6 floor; `test_skip_uses_existing_region_npz_not_bare_exists` proves a <256-byte
  file recomputes.
- **T-260625-r6m-02** (marker says done, contents wrong): `content_verify_npz`
  float32/square/diag/symmetry per region; status recorded in the panel TSV.
- **T-260625-r6m-03** (LD sign flip vs GWAS z): plink ONLY via `build_plink_ld_command`;
  `test_keep_allele_order_on_every_issued_command` + the AST not-hand-rolled guard.
- **T-260625-r6m-05** (one bad region aborts the loop): `process_region` try/except +
  `content_verify_npz` non-raising; `test_one_bad_region_does_not_abort_loop` proves
  a corrupt region 1 does not block a clean region 2.

## Verification

- `pytest tests/m3/test_run_native_ld_panel.py` -> **11 passed**.
- `pytest tests/m3` (full-suite gate, smoke_dev py3.11, R `m3-r-ld` env active) ->
  **282 passed, 30 skipped, 0 failed** in 2875.73s (~48 min). No regression; the
  R stitch tests all ran and passed (the 3 PRE-EXISTING stitch failures previously
  tracked in STATE.md were the flaky reticulate cold-start class, already resolved at
  80fbb9a — they did NOT recur).
- `grep run_native_ld_panel.py m3-02e-AFR-NATIVE-FIRE-BRIEF.md` -> STEP 4 re-pointed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Test expectation] one-bad-region status widened to accept `error:`**
- **Found during:** Task 1 (`test_one_bad_region_does_not_abort_loop`).
- **Issue:** A corrupt square `.ld.bin` is rejected inside `plink_ld_to_npz`'s own
  square-matrix checks (same diag/symmetry invariants as `content_verify_npz`) BEFORE
  reaching the inline verify gate, so the status is `error: ...` rather than
  `verify_failed`. Both outcomes satisfy the must-have (region marked failed, loop
  continues, corrupt region not banked).
- **Fix:** Broadened the assertion to accept `verify_failed` OR an `error`-prefixed
  status, and added `assert not (out_dir/'regBAD.npz').is_file()` to prove the corrupt
  region was not banked. No production-code change.
- **Commit:** 35361e5

**2. [Rule 1 - Boundary guard] reworded the retired-path docstring**
- **Found during:** Task 2 (`test_driver_does_not_touch_retired_hail_path`).
- **Issue:** The driver's "does NOT touch the retired Hail path" docstring listed the
  retired symbol names verbatim, which tripped the substring-absence guard (the guard
  scans the whole source, mirroring the sibling test in test_plink_ld_to_npz.py).
- **Fix:** Reworded the docstring to describe the boundary without naming the retired
  symbols; the guarantee is unchanged and the test now passes.
- **Commit:** 1a1a361

## Self-Check: PASSED

- FOUND: src/python/run_native_ld_panel.py
- FOUND: tests/m3/test_run_native_ld_panel.py
- FOUND: .planning/phases/m3-aou-afr-ld-panel-build/m3-02e-AFR-NATIVE-FIRE-BRIEF.md (STEP 4 re-pointed)
- FOUND commit 35361e5 (Task 1)
- FOUND commit 1a1a361 (Task 2)
