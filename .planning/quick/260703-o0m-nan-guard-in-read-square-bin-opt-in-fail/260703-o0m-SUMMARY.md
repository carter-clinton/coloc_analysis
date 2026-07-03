# Quick Task 260703-o0m — SUMMARY

**Date:** 2026-07-03
**Branch:** m3-W2-aou-deltas
**Origin:** Seth (Claude Science agent) — Defects 3 & 4, relayed by Carter; verified against source at 2d23d67 before implementation.
**Status:** Complete — both defects landed TDD (RED→GREEN), tests green.

## What & why

Two NC-State-side defensive fixes to the native-plink LD path. **Code only — the
AoU loop, VM, and kernel were untouched; the fixes are NOT on the running VM
(2d23d67) and must NOT trigger a re-fire.** Source files are byte-identical
between HEAD and the VM's running commit (the intervening commits are docs-only).

### Defect 3 — NaN-specific error in `read_square_bin` (`src/python/plink_ld_to_npz.py`)
At 2d23d67 the reader ran reshape → diagonal → `_is_symmetric_blocked` with **no
NaN check**, so a plink `0/0 -> NaN` entry (zero-variance variant) raised the
**misleading** `square LD is not symmetric` (`NaN != NaN` trips the symmetry
equality). Added `_has_any_nan_blocked` + `nan_variant_indices` (block-wise, no
full `n_var²` temporary) and a NaN pre-check that runs **before** the diagonal/
symmetry checks and raises a NaN-specific `ValueError` naming the likely source
variant row(s). The diagonal/symmetry/OOM-bounded checks are unchanged and still
run after — a NaN-free asymmetric matrix still raises `not symmetric`.

**Correction vs. the relayed spec:** Seth's proposed `nan_variant_indices` used
`np.isnan(row).all(axis=1)`, which returns `[]` on the **real fire-#3 fingerprint**
(whole-row NaN with the diagonal still `1.0`, and the sparse "12 NaN across 11
rows" pattern) — the culprit-naming would silently fail exactly when needed. The
landed version ranks rows by NaN count (worst-first, capped), which names the
source on both the whole-row and sparse fingerprints. The regression test keeps
the realistic diagonal=1.0 fingerprint (not Seth's `m[k,k]=nan`).

**do_not exception:** `HANDOFF.json`/`STATE.md` said keep `read_square_bin`
frozen. This add is a diagnostic strengthening (raises earlier + clearer, never
loosens a check). Carter approved the exception (AskUserQuestion, 2026-07-03); the
do_not note is amended to record it.

### Defect 4 — opt-in fail-fast region gate (`src/python/run_native_ld_panel.py`)
`process_region` swallows every error into `status='error: ...'` and the loop
continues, so a broken region 1 could not halt a ~276-region fire. Added
`RegionGateError` (carries `region_id` + `status`) and a keyword-only
`fail_fast=False`; after each `results.append`, the loop raises `RegionGateError`
when `fail_fast and status != 'ok'`. Added a `--fail-fast` CLI flag threaded
through `main()`. **Default off is byte-behaviour-identical** (resume-safe
continue); the failed region's panel row is already written before the raise.

## Commits (TDD RED→GREEN, explicit paths only)

| Commit | Type | Content |
|---|---|---|
| `28c70ff` | test (RED) | Defect 3 NaN-guard contract — `test_plink_ld_to_npz.py` (flipped), `test_nan_guard.py` (new) |
| `b57d31e` | feat (GREEN) | Defect 3 impl — `plink_ld_to_npz.py` |
| `ebceb43` | test (RED) | Defect 4 gate contract — `test_gate.py` (new) |
| `12b86d6` | feat (GREEN) | Defect 4 impl — `run_native_ld_panel.py` |

## Verification

- Runner: `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python` (py3.11, pytest 9).
- Defect 3 surface (`test_plink_ld_to_npz.py` + `test_nan_guard.py`): **27 passed**.
- Both changed modules' full surface (`test_run_native_ld_panel.py` +
  `test_plink_ld_to_npz.py` + `test_nan_guard.py` + `test_gate.py`): **76 passed**.
- Full `tests/m3/` sweep: see STATE.md row (final gate before docs commit).
- `--fail-fast` present in CLI `--help`; both source files byte-compile.

## Guardrails honored

Explicit git paths (no `git add -A` on GPFS); no worktree isolation; AoU loop/VM/
kernel untouched; no re-fire. Files changed: `src/python/plink_ld_to_npz.py`,
`src/python/run_native_ld_panel.py`, `tests/m3/test_plink_ld_to_npz.py`,
`tests/m3/test_nan_guard.py`, `tests/m3/test_gate.py`.

## Follow-ups (out of scope here)

- Seth's Defects 1 (snplist∩bim=0) and 2 (true NaN source) remain pending
  in-perimeter diagnostics — do NOT re-fire until those are cleared.
- `content_verify_npz` has a parallel verify path; a matching NaN diagnostic there
  is a candidate future hardening (not in this task's scope).
