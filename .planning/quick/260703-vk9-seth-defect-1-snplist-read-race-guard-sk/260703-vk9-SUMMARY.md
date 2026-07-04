# Quick Task 260703-vk9 — SUMMARY

**Seth Defect 1 — snplist-read race guard + skip-intersection-when-no-drop**

**Date:** 2026-07-04 · **Branch:** m3-W2-aou-deltas · **Mode:** quick (inline exec)

## What & why

The live region-1 loop failure — `.ld.bin implies 102421 but the window .bim has
0 rows` — was a **RACE, not a logic bug** (Seth, offline-verified). `_retained_window_bim`
read `{out_prefix}.snplist` with a bare `read_text()` and **no** retry-on-zero guard,
unlike its sibling raw-window `.bim` read (`_window_bim_n_var_retry_on_zero`, 27af416).
It raced plink's flush → read an un-flushed (empty) snplist → 0 retained ids → a false
`n_var` mismatch. Offline the same call returns `102421 == 102421` and the snplist ids
match the `.bim` col-2 ids byte-for-byte — the logic and join are sound.

## Changes (edit ONLY `src/python/run_native_ld_panel.py`)

- **A — `_needs_retained_subset(bin_n_var, raw_window_n_var) -> bool`** (new pure helper).
  Returns `bin_n_var != raw_window_n_var`. The snplist∩.bim intersection is needed ONLY
  when `--mac` actually dropped variants; in the observed AFR regime `--mac 1` drops 0.
- **B — `expect_nonzero` retry guard.** `_retained_window_bim` gains a kw-only
  `expect_nonzero: bool = False`. After the snplist read, if `not retained_ids and
  expect_nonzero`, retry up to `_WINDOW_BIM_RETRIES` (sleep `_WINDOW_BIM_RETRY_SLEEP_S`),
  loud WARN to stderr on recovery. Mirrors the raw-window guard. **A persistently-empty
  snplist still returns `[]` → the caller's byte-identical `n_var` mismatch still fires**
  (no semantics loosened).
- **C — conditional caller.** The square branch does the intersection only under
  `_needs_retained_subset(...)` (with `expect_nonzero=(bin_n_var > 0)`); otherwise it uses
  the already-race-guarded raw window `.bim` directly. The `ValueError`, `n_var`, and the
  `n_dropped` provenance block are UNCHANGED (`n_dropped` is correctly 0 in the skip path).

No new imports (`time`/`sys`/`_WINDOW_BIM_RETRIES=3`/`_WINDOW_BIM_RETRY_SLEEP_S=0.5`
already at module top).

## Tests — `tests/m3/test_defect1.py` (new, TDD RED→GREEN)

1. `_needs_retained_subset` → `False` on equal counts / `True` on a drop / `True` on a
   degenerate `0` mismatch.
2. An initially-empty snplist **recovers on retry** when `expect_nonzero=True` (returns the
   real count; `time.sleep` monkeypatched to no-op).
3. A **persistently-empty** snplist still returns `0` so the caller's mismatch fires.

RED verified (AttributeError / TypeError before the edit) → GREEN after.
**Full `tests/m3`: 336 passed / 30 skipped** (baseline 333/30 + 3 new; 0 failed, 9m07s).

## Boundaries honored

- Did **not** touch the o0m-landed `test_plink_ld_to_npz.py` / `test_nan_guard.py` /
  `test_gate.py` or `plink_ld_to_npz.py` (o0m corrected Seth's original Defect-3
  `.all(axis=1)`; that landed version is authoritative).
- **No loop re-fire.** The fix is NC-State-side, NOT on the running VM (`2d3d67`).
- Explicit-path staging only (GPFS shared tree).

## Carry-forwards (NOT in this commit)

1. **NaN→0 + PSD conditioning policy** — the true region-1 substrate fix (a downstream
   `.npz`/`.rds`/pre-SuSiE step with recorded `n_zeroed` provenance). Filed as backlog
   999.x. Zeroing a pairwise `r` asserts unmeasured independence; PSD projection perturbs
   the whole matrix — deserves its own design pass.
2. **Mechanism framing (record softened):** the NaN'd variants are index-adjacent and
   cluster into 5 tight bp windows of low-MAF variants — the signature of a
   **pairwise-undefined `r` among clustered rare variants** (0/0 on a specific pair's
   complete-sample intersection), **not** a "plink bug." The fix is identical either way.
