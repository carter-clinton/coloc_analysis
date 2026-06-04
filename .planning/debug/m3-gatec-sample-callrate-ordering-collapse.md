---
status: investigating
trigger: "m3-gatec-sample-callrate-ordering-collapse: post_sample_qc returned 1859922 rows x 0 cols at Gate C (whole chr22) — the sample-axis collapse the nano guard masked, reproduced at scale"
created: 2026-06-04T00:00:00Z
updated: 2026-06-04T00:00:00Z
supersedes: .planning/debug/resolved/m3-gateb-nano-sample-axis-collapse.md
related:
  - .planning/debug/m3-W1-empty-mt-catastrophe.md
  - .planning/debug/m3-W2-gateB-nano-FAIL-diagnostics.md
---

## Current Focus

hypothesis: |
  H1 (ORDERING — provisional, pending live probe). The per-sample call_rate sample
  filter (Phase 2, src/python/aou_ld_panel.py:1563, `filter_cols(sqc.call_rate >= 0.98)`)
  collapses the sample axis at ALL scales, not just nano. Cause: `hl.sample_qc` (:1552)
  computes call_rate over the RAW, pre-variant-QC variant set (interval-filtered + split,
  but BEFORE Phase 3 variant_qc at :1584). The AoU ACAF callset sets FT-failed genotypes
  to no-call, so over the un-variant-QC'd set — dominated by a rare/low-call tail — every
  sample's call_rate sits below 0.98. The 0.98 threshold is therefore UNSATISFIABLE on the
  pre-variant-QC matrix at any scale. The MIN_VARIANTS_FOR_SAMPLE_CALLRATE=500_000 guard
  (:233) only SKIPS the filter below 500K variants; it never made the metric valid above
  500K. At Gate C (1.86M chr22 variants > 500K) the SKIP does not fire, the filter applies,
  and removes all 74,576 samples.
test: |
  On-cluster read-only probe against the live, checkpointed AFR post_split MT
  (1,859,922 x 74,576), see "Probe" below. [A] confirms the threshold is unsatisfiable on
  the raw set (max call_rate < 0.98, 0/74576 pass). [A2] isolates call_rate vs the het
  filter. [B] validates the candidate fix (variant-QC-FIRST then sample_qc) recovers the
  sample axis (~74,576/74,576 pass 0.98). AWAITING NUMBERS.
expecting: |
  [A] RAW: max < 0.98, 0/74576 >= 0.98 (root cause confirmed).
  [A2] het ±3SD survivors ~74576/74576 (het not the collapser).
  [B] after variant-QC: mean/max >> 0.98, ~74576/74576 >= 0.98 (reorder fix validated on
  the real Gate C data, before any production code is written).
next_action: |
  Carter runs the Probe on the LIVE cluster (the post_split MT is perishable; recreating it
  costs a full re-fire ~$35-80 + 2h). Paste [A]/[A2]/[B]. Then: (1) finalize the fix =
  reorder Phase 2<->Phase 3 (variant_qc + variant filters BEFORE sample_qc + sample
  call_rate filter), (2) AMEND m3-RESEARCH.md §"Recommended driver ordering" (lines 124-140)
  — its documented order (sample_qc step 5 BEFORE variant_qc step 6) is the design-level
  root cause, (3) calibrate the e2e regression test's missingness profile to the probe
  numbers, (4) reframe/retire the 500K guard (it becomes non-load-bearing once call_rate is
  computed over QC-passing variants). Then RED -> fix -> GREEN NCSU-side, push, re-fire
  Gate C.

## Symptoms

expected: post_sample_qc checkpoint retains the sample axis (non-zero rows AND cols) → run
  proceeds through 3 cohort MTs + cohort_summary = Gate C PASS.
actual: post_sample_qc = 1,859,922 rows x 0 cols (AFR). Full sample axis dropped during
  Phase 2 sample-QC. Variants intact. `_assert_checkpoint_nonempty` (count_cols==0) raised
  RuntimeError at Cell 3 (In[6]); kernel halted before Cell 3.5 / AFR-selfid / EUR.
errors: RuntimeError from _assert_checkpoint_nonempty — "1859922 rows x 0 cols". (As at Gate
  B nano, the canned "empty-MT catastrophe" wording is misleading; this is sample-axis
  collapse, NOT the 0x0 platform finalize bug of m3-W1.)
reproduction: Hail 0.2.135, Spark 3.5.3, Gate C cluster (n2-standard-16 master + 24x
  n2-standard-16 workers / 384 vCPU), HEAD 07edafc, INTERVAL="chr22". Deterministic at
  post_sample_qc.
started: FIRST whole-chromosome fire to reach Phase 2 sample-QC with the call_rate filter
  ACTIVE (>500K variants). Gate B nano (<500K) SKIPPED the filter; that PASS was a scale
  artifact of the skip, not a validation.

## Scale contrast (the discriminating evidence)

| tier | variants | <500K guard | call_rate filter | post_sample_qc cols |
|------|----------|-------------|------------------|---------------------|
| Gate B (nano, chr22:16-18Mb) | 118,903 | trips → SKIP | NOT applied | 74,065 ✓ survived |
| Gate C (whole chr22) | 1,859,922 | does not trip | APPLIED | 0 ✗ collapsed |

The nano tier passed *because* it had too few variants to run the collapsing code path. Gate
B's PASS did not exonerate the threshold — it skipped it. ([[feedback_cheap_tier_fail_not_pivot]])

## Eliminated

- FILTER-SENSE INVERSION — REFUTED by inspection. :1563 keeps `call_rate >= 0.98` (high-call
  samples). Sense is correct; the threshold is unsatisfiable, which is a different failure.
- OOM / memory — REFUTED. RegionPool logs clean, no OutOfMemory; the collapse is in the data
  (count_cols==0 after a logical filter), not a resource fault.
- 1000G PIVOT — NOT APPLICABLE. AoU-side sample-QC logic bug, reproducible only on AoU data;
  1000G cannot diagnose it. Stays smoke-fail safety net only. ([[feedback_no_1000g_ld_pivot]])

## Evidence

- timestamp: 2026-06-04T00:02:00Z
  checked: Phase 2/Phase 3 ordering in src/python/aou_ld_panel.py:1538-1590
  found: sample_qc + sample call_rate filter (Phase 2, :1552/:1563) run BEFORE variant_qc +
    variant filters (Phase 3, :1584-1590). Per-sample call_rate is therefore measured over
    the raw post-split variant set including the rare/low-call/FT-failed tail variant_qc is
    meant to strip. The code comment at :1543 states this outright ("pre-variant-QC").
  implication: The 0.98 sample threshold is evaluated against a depressed call_rate. Root
    cause is ORDERING, manifesting as an unsatisfiable threshold — independent of scale.

- timestamp: 2026-06-04T00:04:00Z
  checked: The prior (prematurely-resolved) session
    .planning/debug/resolved/m3-gateb-nano-sample-axis-collapse.md
  found: Its OWN evidence (entries 00:14, 00:18, 00:24) correctly identified the EXACT
    mechanism (sample_qc over pre-variant-QC variants; ACAF FT no-calls depress call_rate).
    BUT it drew two conclusions Gate C now FALSIFIES:
      (1) "genome-wide, call_rate averages over millions of mostly-well-called variants and
          stabilizes well above 0.98" → an UNTESTED ASSUMPTION. Gate C tested it at 1.86M
          variants: call_rate did NOT stabilize; the axis collapsed to 0.
      (2) "Reordering (variant_qc before sample_qc) is NOT canonical per RESEARCH.md, so the
          fix is a degeneracy guard, not a reorder." → the guard masked the bug ≤500K and
          let it through at scale.
  implication: The right root cause was found and then mis-scoped as a "nano artifact." The
    guard treated the symptom. The disease (ordering) survived. Session correctly REOPENED.

- timestamp: 2026-06-04T00:06:00Z
  checked: m3-RESEARCH.md §"Recommended aou_ld_panel.py ordering" (lines 124-140)
  found: The documented canonical order is step 5 `sample_qc; filter call_rate >= 0.98`
    THEN step 6 `variant_qc; filter MAF/HWE/call_rate`. This ordering was verified for Hail
    API correctness, NOT for the statistical validity of computing sample call_rate over the
    un-variant-QC'd ACAF set.
  implication: The bug is design-level, not just a code slip. The fix MUST amend RESEARCH.md
    (and the docstring at :7-19) with the Gate C evidence and the corrected order. Standard
    biobank practice (gnomAD/UKB) computes sample call_rate over a common, well-called
    variant subset — i.e. AFTER variant QC, not before. ([[feedback_rigor_over_speed]])

- timestamp: 2026-06-04T00:08:00Z
  checked: Why this reached a $35-80 live fire undetected (test coverage)
  found: The only e2e col-retention test runs the full fixture with ZERO missingness
    (balding_nichols → call_rate==1.0), making the 0.98 filter a guaranteed no-op. The
    fixture builder GAINED a `--missingness` knob during the nano session but no test yet
    uses it to drive a sample-QC-ordering reproduction. No static test pins sample-QC AFTER
    variant-QC.
  implication: COVERAGE GAP. Fix needs (a) a static ordering guard (Hail-free, deterministic)
    and (b) an e2e reproduction with STRUCTURED missingness (no-call concentrated on the
    rare/low-call variants variant-QC removes) so sample-QC-first collapses the axis and
    variant-QC-first retains it. ([[feedback_extract_reusable_utilities]])

root_cause: |
  PROVISIONAL (pending live Probe [A]/[B]). QC ORDERING BUG.

  load_qc_cohort runs sample-QC (per-sample call_rate filter, >= 0.98) in Phase 2 BEFORE
  variant-QC in Phase 3 (src/python/aou_ld_panel.py:1552/1563 precede :1584). hl.sample_qc
  computes call_rate over whatever variant rows are currently in the MT — here the raw,
  post-split, PRE-variant-QC ACAF set. AoU ACAF sets FT-failed genotypes to no-call, so over
  that un-QC'd set (rich in rare/low-call variants) every sample's call_rate falls below
  0.98. The 0.98 sample threshold is thus UNSATISFIABLE on the pre-variant-QC matrix at every
  scale. MIN_VARIANTS_FOR_SAMPLE_CALLRATE=500_000 only SKIPS the filter below 500K variants
  (masking the bug at the nano tier); it does not make the metric valid above 500K. At Gate C
  (1.86M > 500K) the filter applies and zeroes the 74,576-sample axis.

  The documented "canonical ordering" in m3-RESEARCH.md (lines 124-140, sample_qc step 5
  before variant_qc step 6) is the design-level origin of the bug.

## Probe (read-only, run on the LIVE Gate C cluster against the checkpointed post_split MT)

```python
import os, hail as hl, aou_ld_panel as A

WB = os.environ["WORKSPACE_BUCKET"]
ps_uri = A._intermediate_checkpoint_uri(WB, "afr", "post_split", False, "chr22")
print("post_split:", ps_uri)

ps = hl.read_matrix_table(ps_uri).cache()
n_cols = ps.count_cols()
ps = hl.sample_qc(ps, name="sqc")

# [A] Root cause: is the 0.98 sample threshold satisfiable on the RAW pre-variant-QC set?
cr = ps.aggregate_cols(hl.agg.stats(ps.sqc.call_rate))
n_raw = ps.aggregate_cols(hl.agg.count_where(ps.sqc.call_rate >= A.MIN_CALL_RATE_SAMPLE))
print(f"[A] RAW call_rate mean={cr.mean:.4f} min={cr.min:.4f} max={cr.max:.4f} | "
      f">= {A.MIN_CALL_RATE_SAMPLE}: {n_raw}/{n_cols}")

# [A2] Discriminator: is it the het ±3SD filter, not call_rate?
het = ps.aggregate_cols(hl.agg.stats(ps.sqc.r_het_hom_var))
if het.stdev and het.stdev > 0:
    lo, hi = het.mean - A.HET_HOM_SD_BAND*het.stdev, het.mean + A.HET_HOM_SD_BAND*het.stdev
    n_het = ps.aggregate_cols(hl.agg.count_where((ps.sqc.r_het_hom_var>=lo)&(ps.sqc.r_het_hom_var<=hi)))
    print(f"[A2] het ±{A.HET_HOM_SD_BAND}SD survivors: {n_het}/{n_cols}")

# [B] Fix validation: does variant-QC-FIRST make 0.98 satisfiable? (the proposed reorder)
v = hl.variant_qc(ps, name="vqc")
v = v.filter_rows((v.vqc.AF[1] >= A.MIN_MAF_INTERNAL) & (v.vqc.AF[1] <= A.MAX_MAF) &
                  (v.vqc.call_rate >= A.MIN_CALL_RATE_VARIANT) & (v.vqc.p_value_hwe >= A.MIN_HWE_PVALUE))
if "filters" in v.row:
    v = v.filter_rows(hl.len(v.filters) == 0)
n_var = v.count_rows()
v = hl.sample_qc(v, name="sqc2")
cr2 = v.aggregate_cols(hl.agg.stats(v.sqc2.call_rate))
n_fix = v.aggregate_cols(hl.agg.count_where(v.sqc2.call_rate >= A.MIN_CALL_RATE_SAMPLE))
print(f"[B] after variant-QC ({n_var} variants): call_rate mean={cr2.mean:.4f} "
      f"min={cr2.min:.4f} max={cr2.max:.4f} | >= {A.MIN_CALL_RATE_SAMPLE}: {n_fix}/{n_cols}")
```

## Candidate fix (DO NOT apply until Probe [B] confirms — Iron Law: root cause first)

1. Reorder load_qc_cohort: variant_qc + variant filters (MAF/HWE/call_rate, drop FT-flagged)
   BEFORE sample_qc + sample call_rate filter + het filter. Keep split_multi_hts first
   (existing test_canonical_ordering_split_before_variant_qc stays green: split < variant_qc).
   Re-checkpoint boundary names accordingly (post_variant_qc / post_sample_qc).
2. Amend m3-RESEARCH.md lines 124-140 + the module docstring (:7-19) with the corrected order
   and the Gate C falsification of the "genome-wide dilution" assumption.
3. Reframe MIN_VARIANTS_FOR_SAMPLE_CALLRATE: non-load-bearing once call_rate is over
   QC-passing variants; keep only as defense-in-depth (or remove with rationale).
4. Regression tests (see staged skeletons): static ordering guard (RED now) + e2e structured-
   missingness reproduction (calibrate fraction from Probe numbers).

## RESOLUTION

(pending — fill after Probe [A]/[B] + fix + GREEN + live Gate C re-fire PASS)
