# Design: Nano-tier sample-axis collapse — call-rate degeneracy guard

**Date:** 2026-06-03
**Status:** Approved (Carter, 2026-06-03)
**Debug session:** `.planning/debug/m3-gateb-nano-sample-axis-collapse.md` (canonical)
**Confirming forensics:** `.planning/debug/m3-W2-gateB-nano-FAIL-diagnostics.md` (Carter, live byte-level)
**Branch:** `m3-W2-aou-deltas` @ HEAD 603482d

## Problem

Gate B nano-tier (`INTERVAL="chr22:16000000-18000000"`, a 2 Mb window) failed: the
`post_sample_qc` checkpoint returned **118,903 variant rows × 0 sample cols**.
`_assert_checkpoint_nonempty` halted Cell 3. The assertion's canned message labeled
this the "m3-W1 empty-MT catastrophe signature," which is **misleading** — and that
mislabel pushed the operational read toward an (incorrect) pivot to 1000G AFR.

## Root cause (triangulated — 3 independent lines agree)

The collapse is the **unguarded call-rate sample filter** at
`src/python/aou_ld_panel.py:1460-1461`:

```python
mt = hl.sample_qc(mt, name="sqc")
mt = mt.filter_cols(mt.sqc.call_rate >= MIN_CALL_RATE_SAMPLE)   # 0.98
```

`hl.sample_qc` computes each sample's `call_rate` over the variant rows **currently in
the MT**. At this point the MT is interval-filtered (~118,903 variants) and split-multi,
but **not yet variant-QC'd** (`hl.variant_qc` + the variant call-rate filter run in
Phase 3, downstream of this checkpoint, at `:1479-1485`). AoU's ACAF callset sets
FT-failed genotypes to no-call, so on a tiny window of un-QC'd, low-call-enriched
variants **every** sample's call_rate falls below 0.98 → `filter_cols` drops all samples
→ `118,903 × 0`.

Evidence:
- **Forensics (Carter):** post_split part-0 = 245,342 bytes (full sample table) →
  post_sample_qc part-0 = 35 bytes (schema, 0 data rows); Hail log: *"wrote matrix
  table with 118903 rows and 0 columns"* → cols honestly 0 in-memory before checkpoint
  (rules out I/O / `_SUCCESS`-over-missing-bytes corruption).
- **Code (debugger + review):** call-rate filter is unguarded; the het filter directly
  below (`:1465`) is guarded by `stdev > 0`. That asymmetry is the bug.
- **H3 eliminated:** post_split retained all cols *after* the ancestry filter +
  relatedness anti-join, so the env-derive / suffix-discovery aux refactor is exonerated.

## Verdict: scale-DEPENDENT artifact, NOT a catastrophe → NOT a pivot trigger

`call_rate` is a per-sample mean over the in-window variant set, so it is interval-
dependent by construction:
- **2 Mb (~119K un-QC'd variants):** all samples < 0.98 → FAIL.
- **Whole chr22 (~2.4M) / genome-wide:** averages over ~20–25× more sites, stabilizes
  well above 0.98 → samples retained → PASS.

The 0.98 threshold exists in code as the *intended genome-wide* filter (WGS sample call
rates routinely >0.99), so the pipeline expects samples to clear it at scale. The cheap
fire caught a **real harness defect (missing degeneracy guard)** — not a broken AoU
build. Pivoting to 1000G over this would abandon the 138×-power committed AoU AFR
substrate for a ~15-line guard, violating `[[feedback_no_1000g_ld_pivot]]` and
`[[feedback_rigor_over_speed]]`. **Decision: fix the guard + revalidate, do not pivot.**

The "cheap-tier FAIL → pivot" rule has an unstated precondition — the cheap tier must be
a faithful scale-model. It is faithful for checkpoint finalize / partitions / URI logic /
driver-collect / genome-wide aux joins; it is **not** faithful for any QC metric computed
over the variants-in-window (sample call_rate). Threshold validation for such metrics
belongs to the whole-chromosome+ tier (Gate C).

## Design (approved)

Genome-scale path held **byte-identical**; only the degenerate small-span case changes.

1. **Degeneracy guard** on the call-rate sample filter (`:1460-1461`), mirroring the het
   `stdev > 0` precedent — skip the filter when the variant count is below a floor where
   `call_rate` is statistically meaningful; log loudly with the call_rate distribution;
   keep all samples. (See pseudocode below.)

2. **New module constant** `MIN_VARIANTS_FOR_SAMPLE_CALLRATE = 500_000`. Derivation: nano
   density ≈ 59.5K variants/Mb; whole-chr22 ≈ 2.4M; 500K is ~4× the nano count and ~5×
   below the smallest real tier (chr22-full), so it **never trips at whole-chromosome-or-
   larger scale** (genome science untouched) and always trips at nano. Documented in the
   constant's comment.

3. **Truthful provenance** — add `sample_callrate_filtered: bool` (and the floor) to
   `_collect_provenance` output so the sidecar honestly records whether the cohort was
   call-rate-QC'd (`[[feedback_aou_success_marker_not_evidence_of_data]]`).

4. **Fix the misleading assertion message** (`:836-844`) — distinguish
   `rows>0, cols==0` ("**sample axis collapsed during QC** — check QC predicates /
   degeneracy guards; NOT a finalize bug") from true `0×0` ("finalize catastrophe").

5. **Faithful regression test** — inject per-genotype missingness into the synthetic
   fixture (`tests/m3/fixtures/build_synthetic_mt.py:56-61`, currently zero-missingness so
   call_rate≡1.0 made the filter a guaranteed no-op) and add a `load_qc_cohort` Phase-2
   test asserting:
   - (RED→GREEN) span-bounded + low-call, below floor → guard skips, **cols retained**,
     skip logged, provenance flag `False`;
   - above-floor variant count → filter **still applies and drops genuinely-bad samples**,
     provenance flag `True` (proves genome-scale path unchanged).

### Guard pseudocode

```python
mt = hl.sample_qc(mt, name="sqc")
_n_var = mt.count_rows()
if _n_var < MIN_VARIANTS_FOR_SAMPLE_CALLRATE:
    cr = mt.aggregate_cols(hl.agg.stats(mt.sqc.call_rate))
    print(f"[load_qc_cohort] SKIP call_rate sample filter — only {_n_var} "
          f"variants (< {MIN_VARIANTS_FOR_SAMPLE_CALLRATE}); call_rate degenerate "
          f"on this span (mean={cr.mean:.4f} max={cr.max:.4f}). Sample-QC thresholds "
          f"validated at whole-chromosome+ tier.")
    sample_callrate_filtered = False
else:
    mt = mt.filter_cols(mt.sqc.call_rate >= MIN_CALL_RATE_SAMPLE)
    sample_callrate_filtered = True
```

## Non-goals (YAGNI)

- No change to the canonical sample-before-variant QC ordering.
- No new validation tier; no threshold relaxation.
- No change to the het guard, aux resolution, or the colon/driver-collect fixes (all
  confirmed working this run).

## Revalidation sequence (after fix lands)

1. NCSU: `tests/m3` green (RED→GREEN on the new test).
2. Push to `origin/m3-W2-aou-deltas`.
3. Re-fire **Gate B nano** (~$1–3): expect post_sample_qc to write with non-zero cols
   (filter skipped + logged), all 3 cohort MTs populated, assertions silent = **PASS**.
4. Proceed to **Gate C** (chr22-full), where the real sample-QC thresholds get validated
   on a meaningful (~2.4M) variant count.

## References

- `.planning/debug/m3-gateb-nano-sample-axis-collapse.md`
- `.planning/debug/m3-W2-gateB-nano-FAIL-diagnostics.md`
- `.planning/debug/m3-W1-empty-mt-catastrophe.md` (the *true* 0×0 catastrophe — distinct)
- `[[feedback_no_1000g_ld_pivot]]`, `[[feedback_rigor_over_speed]]`,
  `[[feedback_aou_success_marker_not_evidence_of_data]]`,
  `[[feedback_extract_reusable_utilities]]`
