---
status: resolved
trigger: "m3-W2-a2-dense-narrow-driver-oom-routing — _route_region_path routes by span only; dense-narrow A.2 cell OOMs driver in to_numpy()"
created: 2026-06-23T00:00:00Z
updated: 2026-06-23T00:00:00Z
---

## Current Focus

hypothesis: CONFIRMED — `_route_region_path(region_class, span_mb)` gates A.1/A.2 demotion on SPAN only; the true driver-OOM determinant for A.1/A.2 is the `to_numpy()` dense collect = n_var^2 * 8 bytes (Hail BlockMatrix is float64; the `.astype("float32")` happens AFTER the collect). A dense-narrow cell (span <= 10 Mb, high n_var) routes A.2 and OOMs the 11 GiB driver heap.
test: exercise the pure function directly; analyze preflight TSV; RED-first regression test then minimal fix.
expecting: 69 A.2 cells flip to A.3 after the density veto.
next_action: write RED test, run it failing, apply fix, run GREEN + full m3 suite, re-derive routing.

## Symptoms

expected: A cell whose A.2 to_numpy() dense collect would exceed the driver heap should route to Path A.3 (banded BlockMatrix.write), not OOM the driver.
actual: region_00040__sub00 AFR (span 7.93 Mb <= 10 Mb cap, n_var 64,176) routed A.2 and INTERRUPTED with a driver-collect OOM in to_numpy().
errors: status=INTERRUPTED_a2_driver_collect in m3-W2-cost-probe.tsv; dense array > driver heap.
reproduction: pure-function decidable from preflight TSV; `_route_region_path(region_class, span_mb)` returns "A.2" for dense-narrow cells.
started: surfaced 2026-06-23 in m3-02d Task-4 re-probe (push 210e66c); span-only veto added earlier never considered density.

## Eliminated

(none — root cause confirmed directly)

## Evidence

- timestamp: 2026-06-23
  checked: src/python/aou_ld_panel.py:325-353 `_route_region_path` + lines 2461-2470 A.1/A.2 densify.
  found: A.1/A.2 do `ld_bm.to_numpy().astype("float32")` — to_numpy() materializes the FULL float64 array on the driver BEFORE the float32 cast. Veto at 350-352 gates on span_mb only.
  implication: density (n_var) is never consulted; the veto predicate is wrong axis.

- timestamp: 2026-06-23
  checked: Hail docs — BlockMatrix.to_numpy() dtype.
  found: BlockMatrix is float64; to_numpy() returns float64 ndarray (tofile→fromfile). Peak driver bytes = n_var^2 * 8.
  implication: OOM determinant = n_var^2 * 8 bytes. region_00040 = 64176^2*8 = 32.9 GB >> 11 GiB heap.

- timestamp: 2026-06-23
  checked: direct call `_route_region_path("medium", 7.93)` -> "A.2" (the OOM cell).
  found: confirmed bug; control cells (small low-density -> A.1, sparse medium -> A.2, wide-span -> A.3 via existing veto) all correct.
  implication: bug isolated to the missing density predicate.

- timestamp: 2026-06-23
  checked: full preflight TSV (552 cells; 106 routed A.2).
  found: 69 of 106 A.2 cells have float64 to_numpy collect > 11 GiB heap (max 60.2 GB region_00062 AFR). Systemic, not one-off.
  implication: fix must demote all 69 to A.3.

## Resolution

root_cause: `_route_region_path` demotes A.1/A.2 to A.3 only when span_mb > PATH_A2_MAX_MB. The driver-OOM determinant for A.1/A.2 is the to_numpy() dense float64 collect = n_var^2 * 8 bytes (Hail BlockMatrix is float64; the `.astype("float32")` runs AFTER the collect peak), which is independent of span. A dense-narrow cell (small span, high variant density) passes the span gate but its dense collect exceeds the driver heap. Confirmed directly: `_route_region_path("medium", 7.93)` -> "A.2" with a 32.9 GB collect; 69/106 A.2 cells exceed even the full 11 GiB heap.
fix: Added a SECOND OOM veto (density axis) to `_route_region_path`, threaded an optional `n_var` parameter through it and both call sites (live compute_region_ld @ ~line 2392, preflight _preflight_estimates @ ~line 431). New named module constants DRIVER_HEAP_GIB=11, DRIVER_COLLECT_SAFE_FRACTION=0.40, _DENSE_COLLECT_BYTES_PER_ELEM=8, helper _max_safe_to_numpy_n_var() (=24,301 var). Any A.1/A.2 cell whose n_var^2*8 collect exceeds 40% of the heap is demoted to A.3. n_var omitted -> prior span-only behavior preserved (backward compat). Conservative 0.40 fraction leaves headroom for Spark/Py4J + Python + the transient float32 copy during .astype. Demotion is safe (banded A.3 write proven viable).
verification: RED-first test test_route_region_path_density_veto fails on missing constant, GREEN after fix. Full m3 suite: 244 passed, 30 skipped, 0 failed/0 errors (isolated clean run b8rxau9f0; an earlier run showed 2 ERRORS that were a transient R-env probe TimeoutExpired from two parallel pytest runs contending — the 17 R-toolchain tests pass in isolation). Re-derived routing over the 552-cell preflight TSV: 100 of 106 A.2 cells flip A.2->A.3 (only 6 genuinely-safe n_var<=24,301 A.2 cells remain); all 6 named dense-narrow cells confirmed A.3; invariant "0 A.1/A.2 cells exceed full 11 GiB collect" holds.
files_changed: [src/python/aou_ld_panel.py, tests/m3/test_aou_ld_panel_local.py]
