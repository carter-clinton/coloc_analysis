---
phase: quick-260630-rn4
plan: 01
subsystem: m3-native-plink-ld-loop
tags: [m3-02e-T4, ld-panel, transient-short-read, retry-guard, tdd, reusable-utility]
requires:
  - src/python/run_native_ld_panel.py::_window_bim_n_var
  - src/python/run_native_ld_panel.py::process_region (square branch)
provides:
  - _window_bim_n_var_retry_on_zero (bounded-retry transient short-read guard)
  - _WINDOW_BIM_RETRIES / _WINDOW_BIM_RETRY_SLEEP_S module constants
affects:
  - src/python/run_native_ld_panel.py (SQUARE verify path only)
tech-stack:
  added: []
  patterns:
    - "bounded-retry self-heal on a transient read, byte-identical raise on a genuine persistent failure"
    - "reusable utility + failing-first regression for a recurrent bug class ([[feedback_extract_reusable_utilities]])"
key-files:
  created: []
  modified:
    - src/python/run_native_ld_panel.py
    - tests/m3/test_run_native_ld_panel.py
decisions:
  - "SQUARE-only wiring: bin_n_var computed FIRST drives expect_nonzero=(bin_n_var>0); banded path keeps the bare _window_bim_n_var call unchanged"
  - "Persistent 0 returns the last (0, window_bim) UNCHANGED so the caller's existing check raises the byte-identical ValueError — zero semantic change to a genuine mismatch"
metrics:
  duration_min: 59
  tasks: 2
  files: 2
  completed: 2026-07-01
requirements: [m3-02e-T4-transient-shortread-guard]
---

# Phase quick-260630-rn4 Plan 01: Transient Short-Read Retry Guard Summary

In-run bounded-retry guard around the cohort-`.bim` window count in the
native-plink LD loop's SQUARE verify path: a one-off transient short read
(`n_var==0` against a NON-empty `.ld.bin`) now self-heals in-run with a loud
auditable WARN instead of silently dropping a region across an ~11-day serial
fire, while a genuine persistent mismatch still raises the byte-identical
`ValueError`.

## What Was Built

### `_window_bim_n_var_retry_on_zero` (reusable wrapper)

```
_window_bim_n_var_retry_on_zero(bim_path, chrom, from_bp, to_bp, *,
    expect_nonzero, retries=_WINDOW_BIM_RETRIES, sleep_s=_WINDOW_BIM_RETRY_SLEEP_S)
    -> tuple[int, Path]
```

Contract:
- Calls `_window_bim_n_var` once.
- If `n_var == 0 and expect_nonzero`: retries up to `retries` (=3) more times with
  `time.sleep(sleep_s)` (=0.5s) between attempts — the cohort-`.bim`
  `read_text()` transient self-heals on a re-read.
- On the first attempt that returns `n_var > 0` after seeing a 0: emits a LOUD
  auditable stderr WARN (region `chr:[from,to]` + recovered `n_var`, `flush=True`)
  and returns `(n_var, window_bim)`.
- If it never recovers: returns the LAST `(0, window_bim)` UNCHANGED so the
  caller's existing `bin_n_var != window_n_var` check raises the byte-identical
  mismatch (region records `status="error: ..."`, loop continues, region unbanked).
- If `expect_nonzero` is False (a legitimately empty window): does NOT loop —
  returns the single first result.

Module constants `_WINDOW_BIM_RETRIES = 3` and `_WINDOW_BIM_RETRY_SLEEP_S = 0.5`
were added by the `_DEFAULT_PANEL_NAME` block with an m3-02e-T4 comment. Reuses the
already-imported `time` / `sys`; **no new imports**.

### SQUARE-only wiring in `process_region`

The SQUARE branch was restructured so `bin_n_var = _n_var_from_ld_bin(ld_path)` is
computed FIRST, then:

```
window_n_var, window_bim = _window_bim_n_var_retry_on_zero(
    bim_path, chrom, from_bp, to_bp, expect_nonzero=(bin_n_var > 0),
)
```

The banded (`else`) branch keeps calling the bare `_window_bim_n_var` unchanged.
The `n_var mismatch ...` `ValueError` f-string is **byte-identical** to the
pre-change source (`git diff` shows no `+`/`-` on that string).

## Byte-Identical Mismatch Guarantee

A persistent `n_var==0` against a non-empty `.ld.bin` still raises verbatim:

```
n_var mismatch for {region_id}: .ld.bin implies {bin_n_var} but the window .bim
has 0 rows — the .ld.bin and the [{from_bp},{to_bp}] window must agree.
```

`status="error: ..."`, region unbanked, loop continues — asserted verbatim by T2.

## The 4 New Tests (section 13, TDD)

| Test | Asserts |
| --- | --- |
| `test_retry_wrapper_self_heals_on_transient_zero_and_warns` (T1) | first call 0 -> retry 102421; wrapped fn called exactly twice; LOUD WARN on stderr carrying `102421` + `from_bp` |
| `test_retry_wrapper_persistent_zero_preserves_byte_identical_mismatch` (T2) | persistent 0 vs non-empty `.ld.bin` -> `status` starts `error:` + contains the EXACT mismatch substring; `.npz` not banked |
| `test_retry_wrapper_nonzero_first_call_no_retry_no_warn` (T3) | legit nonzero-first-call -> exactly one read, no WARN |
| `test_retry_wrapper_expect_nonzero_false_does_not_spin` (T4) | `expect_nonzero=False` + 0 -> returns 0, exactly one call, no retry spin |

`monkeypatch.setattr(drv.time, "sleep", lambda *_a, **_k: None)` keeps every
sleeping test fast. RED proven: T1/T3/T4 `AttributeError` on the missing wrapper
pre-implementation.

## Deviations from Plan

None — plan executed exactly as written.

## Threat / Egress Notes

None. No new network endpoints, auth paths, file-access patterns, or schema
changes. The guard only re-reads the SAME cohort `.bim` already read by the
unchanged `_window_bim_n_var`; the individual-level `.bed/.bim/.fam` egress
boundary is untouched.

## Known Stubs

None.

## Verification

- `grep -n _window_bim_n_var_retry_on_zero src/python/run_native_ld_panel.py` ->
  wrapper def (line 301) AND SQUARE call site (line 514).
- Banded branch still calls the bare `_window_bim_n_var` (line 525).
- Mismatch `ValueError` string byte-identical (`git diff` clean on that f-string).
- No new top-level imports (`git diff` shows none; reused `time` / `sys`).
- Targeted: `5 passed, 29 deselected` (4 new + 1 pre-existing banded).
- **Full tests/m3: `309 passed, 30 skipped in 3112.10s (0:51:52)`** — exceeds the
  baseline requirement (>=302 passed / 30 skipped; the 4 new tests add to passed).

## Commits

- `bba9cf8` test(quick-260630-rn4): add failing-first regression (RED)
- `27af416` fix(quick-260630-rn4): transient short-read retry guard on the SQUARE window-.bim count (GREEN)

## Self-Check: PASSED

- FOUND: src/python/run_native_ld_panel.py
- FOUND: tests/m3/test_run_native_ld_panel.py
- FOUND commit: bba9cf8
- FOUND commit: 27af416
