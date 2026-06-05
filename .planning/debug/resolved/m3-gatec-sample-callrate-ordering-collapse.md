---
status: awaiting_human_verify
trigger: "m3-gatec-sample-callrate-ordering-collapse: post_sample_qc returned 1859922 rows x 0 cols at Gate C (whole chr22) — the sample-axis collapse the nano guard masked, reproduced at scale"
created: 2026-06-04T00:00:00Z
updated: 2026-06-04T12:00:00Z
fix_commit: 80d0a00
supersedes: .planning/debug/resolved/m3-gateb-nano-sample-axis-collapse.md
related:
  - .planning/debug/m3-W1-empty-mt-catastrophe.md
  - .planning/debug/m3-W2-gateB-nano-FAIL-diagnostics.md
---

## Current Focus

hypothesis: |
  H1 (ORDERING — CONFIRMED on live data 2026-06-04, see "Probe results" below).
  [A] RAW call_rate max=0.8490 → 0/74576 pass 0.98 (unsatisfiable pre-variant-QC).
  [A2] het ±3SD keeps 74142/74576 (het exonerated). [B] variant-QC-first (1.86M →
  283,854 vars) → call_rate mean=0.9975, 74558/74576 (99.98%) pass 0.98 (reorder
  recovers the full sample axis). Fix validated before any production code.

  H1 (ORDERING — original statement). The per-sample call_rate sample
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

## Probe results (LIVE, 2026-06-04, against mt_afr_post_split_chr22.mt 1859922×74576)

Forensic readout was also saved cluster-side to
`.planning/debug/m3-gatec-sample-axis-collapse-probe.txt` (CLUSTER LOCAL DISK —
lost at teardown; numbers transcribed here NCSU-side so they survive):

```
[A]  RAW call_rate (pre-variant-QC):  mean=0.8075  min=0.7520  max=0.8490  | >=0.98 : 0/74576
[A2] het ±3.0SD survivors:            74142/74576
[B]  after variant-QC (283854 vars):  mean=0.9975  min=0.9568  max=0.9996  | >=0.98 : 74558/74576
```

- [A] CONFIRMS the threshold is unsatisfiable on the raw set: max call_rate 0.8490 < 0.98 →
  the 0.98 filter at :1563 keeps 0/74576. Independent of scale (this is whole-chr22).
- [A2] EXONERATES the het ±3SD filter (74142/74576 retained) → call_rate is the sole collapser.
- [B] VALIDATES the reorder fix on real Gate C data: variant-QC-first (1.86M → 283,854 clean
  variants) lifts sample call_rate to mean 0.9975; 74558/74576 (99.98%) clear 0.98. The 18
  dropped samples are legitimate low-call-rate exclusions — the intended behavior of the
  filter when computed over QC-passing variants.

root_cause: |
  CONFIRMED (live Probe 2026-06-04, [A]/[A2]/[B] above). QC ORDERING BUG.

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

status: awaiting_human_verify — fix landed + GREEN NCSU-side; pending live Gate C re-fire.

**Fix (commit 80d0a00).** Reordered load_qc_cohort so variant_qc + variant filters
(Phase 2) run BEFORE sample_qc + call_rate + het (Phase 3). Per-sample call_rate is now
measured over the post-variant-QC clean variant set. Per DEC-2026-06-04 (Carter) the
MIN_VARIANTS_FOR_SAMPLE_CALLRATE=500K nano guard keys on the RAW (pre-variant-QC) variant
count — captured before variant_qc, persisted to the renamed post_variant_qc sidecar,
restored on RESUME_FROM_POST_VARIANT_QC — so the validated threshold and the nano-smoke
clean-PASS tier are preserved (whole-chr+ raw ≥500K → APPLY over clean variants; nano raw
<500K → SKIP).

Checkpoint topology renamed for honesty: intermediate-2 post_sample_qc → post_variant_qc
(URI phase, ckpt var, RESUME_FROM_POST_VARIANT_QC state, sidecar phase, assert phases).
m3-RESEARCH.md "Recommended ordering" (steps 5/6 swapped + dated correction) + module
docstrings amended.

**Tests (GREEN NCSU-side, 125 passed / 31 skipped, no Hail).** The staged
test_sample_callrate_filter_runs_after_variant_qc (static, was xfail-strict) now PASSES as
a normal guard; topology-rename tests updated; no assertions weakened. The e2e
structured-missingness reproduction stays skipped (needs a fixture enhancement — probe
target numbers recorded in its skip reason).

**Why the prior session's guard wasn't enough (lesson).** resolved/m3-gateb-nano-sample-
axis-collapse.md found the mechanism but mis-scoped it as a nano artifact and chose a guard
over a reorder, on the untested assumption that genome-wide call_rate "stabilizes above
0.98." Gate C falsified that (max 0.8490 at 1.86M variants). The guard masked the bug ≤500K
and shipped it to a $35-80 fire. Generalization for the KB: a degeneracy guard that SKIPS a
check on a "degenerate" tier is masking, not fixing, unless the check is independently shown
to be valid on the non-skipped tier — verify the assumption, don't assume the dilution.

**LIVE CONFIRMATION (2026-06-04 re-fire, branch HEAD 0e3ef2a / fix 80d0a00).** On the exact
AFR cohort that collapsed to ×0 before, the fix WORKS:
```
20:53:31  post_split        1,859,922 × 74,576   (sample axis intact)
20:55:43  post_variant_qc     283,854 × 74,576   (NEW reordered checkpoint; was post_sample_qc=×0)
20:57:56  mt_afr_qc (final)   283,854 × 74,059   (_SUCCESS) — call_rate APPLIED (raw 1.86M>500K,
                                                  guard did NOT skip), ~517 legit low-call trim,
                                                  NOT a collapse; _assert_checkpoint_nonempty silent
```
Variant count 283,854 matches Probe [B] exactly. The ordering bug is RESOLVED on the failing
cohort. Forensic readout (cluster-local, transcribed NCSU-side): `.planning/debug/m3-gatec-refire-result.txt`.

**Run halted after AFR (separate, NOT this bug).** Cohorts 2 (AFR pca_selfid) + 3 (EUR) did
not run this pass. Post-stall driver diagnosis (jstack ×2 5s apart, PID 81718): `main`
RUNNABLE but parked on the py4j gateway socket read (PythonGatewayServer.main), CPU
byte-identical across both samples (zero advance), NO collect/RangePartitioner/BlockMatrix
frames; Spark UI :4040/:4041/:4042 empty (no live SparkContext / no active stage); kernel
(PID 81655) State=S in do_epoll_wait. => the run HALTED BETWEEN CELLS (nothing computing),
NOT a driver wedge and NOT a selfid-cohort query-shape issue.

CONFIRMED CAUSE (hypothesis b — uncaught exception). On-disk execution map: Cell 3 [6]=ok,
**Cell 3.5 [7]=AssertionError**, Cell 4+ [None]=UNRUN. The AFR du-floor guard (Cell 3.5) raised
and Run All halted, parking the kernel idle in epoll exactly as the signature predicted — the
selfid cohort never dispatched. The AssertionError is a FALSE POSITIVE from the guard's own
path construction: `_ckpt_uri = _qc_checkpoint_uri(...) + _suffix` appends `_chr22` AFTER the
`.mt` extension → a phantom `mt_afr_qc.mt_chr22/entries/rows/parts/` that never exists →
`gsutil du -s` returns 0 → `0 > 50_000_000` False → halt. The real MT is healthy at the
un-suffixed `mt_afr_qc.mt/` (283854×74059, _SUCCESS, ~22.4 GB at entries/rows/parts/). The
author's own comment admitted `_qc_checkpoint_uri` "does NOT honor interval_filter" yet
suffixed anyway. Smoke-template-only bug (`AOU-1-chr22-smoke_template.ipynb`); the production
`AOU-1_template.ipynb` is already correct ([[feedback_aou_websocket_drop_zombie_pattern]] was
NOT the cause — the run-loop halt was the raised guard, not a frontend drop).

FIX (this commit): dropped `+ _suffix` from all 6 affected sites — the 3 du-floor guard
cells (7/9/11) AND the 3 cohort_summary `checkpoint_path` provenance entries (cell 13, which
would have recorded phantom paths after the guards passed). Legit `_suffix` uses (cohort
labels, the `cohort_summary_m3_chr22.tsv` filename) left intact. A notebook guard path-
construction defect — NOT the ordering bug, NOT a selfid pipeline issue. Separate latent
observation (tracked, not blocking): the FINAL checkpoint is not interval-isolated (nano/chr22
share `mt_{ancestry}_qc.mt`) — a load_qc_cohort design question, not this guard's concern.

**Remaining to fully close (human-verify):** a clean uninterrupted re-fire completing all 3
cohort MTs (non-zero n_samples AND n_variants) + du-floor real GB entries/rows/parts/ +
cohort_summary 3 non-zero rows. On PASS → mark resolved + archive to resolved/ + KB entry;
close the sibling entries-path + driver-collect sessions; greenlight Wave 2 full-genome rebuild.
