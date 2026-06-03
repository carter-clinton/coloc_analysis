---
status: resolved
trigger: "m3-gateb-nano-sample-axis-collapse: post_sample_qc returned 118903 rows x 0 cols at Gate B nano (chr22:16000000-18000000)"
created: 2026-06-03T00:00:00Z
updated: 2026-06-03T15:30:00Z
resolved: 2026-06-03T15:30:00Z
---

## Current Focus

hypothesis: CONFIRMED H2 - the call_rate sample filter (Step 7) collapses the sample axis at nano scale because per-sample call_rate is computed over the small, unfiltered (pre-variant-QC) 2 Mb variant set; AoU ACAF FT-no-calls depress it below 0.98 for all samples. Het filter (Step 8) is already guarded by stdev>0; call_rate had no analogous nano guard.
test: RESOLVED. Fix LIVE-VERIFIED on AoU at Gate B nano re-fire #3 (HEAD 9f0c837). The SKIP guard fired with the exact expected log line; the sample axis survived sample-QC end-to-end on all 3 cohorts. See RESOLUTION section below.
expecting: (met) Gate B nano re-fire -> post_sample_qc writes non-zero cols (filter skipped + logged), 3 cohort MTs populate, assertions silent = PASS.
next_action: NONE. Session resolved 2026-06-03 after human-verify CONFIRMED FIXED. Commits e5bf0e7 (RED) + fad2847 (fix) + 9f0c837 (live-verified HEAD) on m3-W2-aou-deltas. KB entry appended; session archived to resolved/.

## Symptoms

expected: post_sample_qc checkpoint returns MT with non-zero rows AND non-zero cols (samples retained), run proceeds to 3 cohort MTs = Gate B PASS.
actual: post_sample_qc returned 118903 rows x 0 cols. All sample columns dropped during sample-QC. Variants intact. Run halted at Cell 3.
errors: RuntimeError from _assert_checkpoint_nonempty - "118903 rows x 0 cols ... empty-MT catastrophe signature" (NOTE: canned message is misleading; this is sample-axis collapse only, NOT 0x0 platform finalize bug).
reproduction: Hail 0.2.135, Spark 3.5.3, n2-standard-16 master + 4x workers, executor.cores=1, HEAD 603482d, INTERVAL="chr22:16000000-18000000". Restart Kernel & Run All -> deterministic fail at post_sample_qc.
started: FIRST run to ever reach post_sample_qc. Sample-QC on nano interval never exercised before (re-fire #1 died at colon-path bug before sample-QC).

## Eliminated

## Evidence

- timestamp: 2026-06-03T00:10:00Z
  checked: load_qc_cohort Phase 2 sample-axis ops (src/python/aou_ld_panel.py:1457-1476)
  found: EXACTLY TWO sample-axis filters in Phase 2 (the post_sample_qc phase). Step 7 (L1460-1461) hl.sample_qc + filter_cols(sqc.call_rate >= MIN_CALL_RATE_SAMPLE=0.98). Step 8 (L1463-1469) het r_het_hom_var +/-3SD, GUARDED by `if het_stats.stdev is not None and het_stats.stdev > 0`. No ancestry/relatedness join in Phase 2 (those are in Phase 1, before post_split, which already PASSED with 118903 rows present + samples present at checkpoint 1).
  implication: The het filter CANNOT collapse cols on a degenerate nano window (guard skips it when stdev<=0). That leaves the call_rate filter (Step 7) as the ONLY unguarded sample-axis op in Phase 2. It is the collapse point.

- timestamp: 2026-06-03T00:12:00Z
  checked: Whether call_rate filter is scale-invariant or interval-dependent
  found: hl.sample_qc computes per-sample metrics over the variant rows CURRENTLY in the MT. At this point in the pipeline the MT has been interval-filtered to chr22:16-18Mb (L1389-1393) AND split_multi (L1425) but NOT yet variant-QC'd (variant_qc is Phase 3, L1479, AFTER the post_sample_qc checkpoint). So sqc.call_rate = (non-missing GT calls across the ~118,903 nano-window variants) / 118,903. This is INTERVAL-DEPENDENT: the denominator and the specific variants are entirely the nano window's contents.
  implication: call_rate is fundamentally scale-dependent. On a 2 Mb ACAF window dominated by rare/low-quality variants (pre-variant-QC), every sample's missingness rate over that small, unfiltered variant set can plausibly exceed 2% -> call_rate < 0.98 -> ALL samples dropped. This is a NANO ARTIFACT, not a genome-wide-real failure: genome-wide, call_rate averages over millions of mostly-well-called variants and stabilizes well above 0.98.

- timestamp: 2026-06-03T00:14:00Z
  checked: Pipeline ordering - is variant_qc applied before sample_qc?
  found: NO. Canonical order (docstring L7-19 + code): filter_intervals -> ancestry -> anti_join relateds -> split_multi -> [checkpoint post_split] -> sample_qc + call_rate filter + het filter -> [checkpoint post_sample_qc] -> variant_qc + variant filters (Phase 3). sample_qc runs on the RAW post-split variant set, including all low-call-rate / monomorphic / AoU-flagged variants that variant_qc would later strip.
  implication: On a full chromosome or genome the noise from low-quality variants is diluted. On a 2 Mb window, if that window happens to be enriched for low-call-rate variants (or if ACAF includes many variants where a chunk of samples are no-call), the per-sample call_rate is computed over a small, unfiltered, potentially pathological variant set -> systematic depression below 0.98. Reordering (variant_qc before sample_qc) is NOT canonical per RESEARCH.md, so the fix is a degeneracy guard, not a reorder.

- timestamp: 2026-06-03T00:16:00Z
  checked: H3 (aux-join regression) viability against the observed failure point
  found: post_split checkpoint (Phase 1, AFTER ancestry filter_cols + relatedness anti_join) WROTE SUCCESSFULLY and PASSED _assert_checkpoint_nonempty (nonzero rows AND cols) - operator reports post_split wrote fine and the failure is at post_sample_qc. Ancestry/relatedness aux tables are GENOME-WIDE per-sample calls (interval-INVARIANT). If the aux join had dropped all samples, post_split would have been 118903 x 0 and failed FIRST, at Phase 1. It did not.
  implication: H3 ELIMINATED. The sample axis was non-empty at the post_split checkpoint (end of Phase 1); collapse happened strictly inside Phase 2 (sample_qc), downstream of all aux joins.

- timestamp: 2026-06-03T00:18:00Z
  checked: Test coverage for sample-axis retention at nano scale (tests/m3/test_aou_ld_panel_local.py + fixtures/build_synthetic_mt.py)
  found: (1) The only end-to-end col-retention test (test_aou_driver_loads_synthetic_mt, L925-941) calls load_qc_cohort WITHOUT interval_filter -> runs over the FULL fixture (chr16 50-52Mb + chr6 28-34Mb, all variants), never a 2 Mb nano slice. (2) The synthetic MT is built with hl.balding_nichols_model (build_synthetic_mt.py:56-61) which emits FULLY-CALLED genotypes (no missingness injected) -> sqc.call_rate == 1.0 for every sample -> the >= 0.98 filter is a guaranteed no-op in tests. (3) No test injects GT missingness or exercises load_qc_cohort with a span-bounded interval_filter through the sample-QC phase.
  implication: COVERAGE GAP. The call_rate sample filter's degenerate-nano behavior is structurally untestable with the current fixture (no missingness) and untested at nano scale (no interval_filter through Phase 2). This is exactly why the bug reached the first live nano fire undetected. The het filter got its `stdev>0` guard from prior reasoning; the analogous call_rate degeneracy was never guarded because it never surfaced in a no-missingness fixture.

- timestamp: 2026-06-03T00:24:00Z
  checked: AoU ACAF MT genotype model (web - AoU "How the All of Us Genomic data are organized")
  found: AoU ACAF threshold callset applies per-GENOTYPE FT (genotype filter): "A process was created to filter out genotypes when they fail genotype filtering (FT)." Failed genotypes become NO-CALL (missing GT). The multiallelic-split MT is the input. So sqc.call_rate = n_called/(n_called+n_not_called) is genuinely < 1.0 and varies with WHICH variants are in scope.
  implication: CONFIRMS the H2 mechanism mechanistically. On the full genome, per-sample call_rate averages over millions of variants and stabilizes well above 0.98. On a 2 Mb nano window of ~118,903 PRE-variant-QC variants (FT-failed/low-quality variants NOT yet stripped), the per-sample call_rate is computed over a small, unfiltered, potentially low-quality variant set. If that window is enriched for low-call variants, EVERY sample's call_rate drops below 0.98 -> filter_cols nukes all samples -> 118903 rows x 0 cols. This is a NANO-SCALE ARTIFACT of computing sample call_rate over an unfiltered small interval, NOT a genome-wide-real catastrophe.

root_cause: |
  SAMPLE-AXIS COLLAPSE AT THE call_rate FILTER (Step 7), a NANO-TIER ARTIFACT (H2 CONFIRMED).

  Exact operation: src/python/aou_ld_panel.py:1460-1461
      mt = hl.sample_qc(mt, name="sqc")
      mt = mt.filter_cols(mt.sqc.call_rate >= MIN_CALL_RATE_SAMPLE)   # 0.98

  Mechanism: hl.sample_qc computes per-sample call_rate over the variant rows
  CURRENTLY in the MT. At this point the MT is interval-filtered to
  chr22:16-18Mb (~118,903 variants) and split_multi, but NOT yet variant-QC'd
  (variant_qc is Phase 3, downstream of the post_sample_qc checkpoint). The AoU
  ACAF callset sets FT-failed genotypes to no-call, so call_rate is genuinely
  <1.0 and is computed over a SMALL, UNFILTERED variant set on a nano window.
  On a 2 Mb window enriched for low-call (pre-variant-QC) variants, every
  sample's call_rate falls below 0.98 and filter_cols drops ALL samples ->
  118,903 rows x 0 cols. _assert_checkpoint_nonempty then halts at
  post_sample_qc with the (misleading) canned empty-MT message.

  Hypothesis verdict:
    - H1 (real genome-wide sample-QC bug): REFUTED. The threshold 0.98 is fixed,
      but the METRIC it gates (call_rate) is interval-dependent and only collapses
      because the window is tiny and pre-variant-QC. At whole-chr22 / genome-wide
      scale, call_rate averages over orders of magnitude more variants and
      stabilizes far above 0.98 -> samples are retained. Scale-DEPENDENT.
    - H2 (nano-tier degenerate filter): CONFIRMED. Direct analogue of the het
      filter's documented degeneracy, which is ALREADY guarded by
      `if het_stats.stdev is not None and het_stats.stdev > 0` (L1465). The
      call_rate filter has NO analogous nano-degeneracy guard -- the asymmetry
      the directive predicted. FALSE NEGATIVE of the cheap tier.
    - H3 (aux-join regression): ELIMINATED. The post_split checkpoint (end of
      Phase 1, AFTER ancestry filter_cols + relatedness anti_join) wrote with
      NON-ZERO cols and passed its own _assert_checkpoint_nonempty. Aux ancestry/
      relatedness tables are genome-wide per-sample and interval-INVARIANT; had
      they dropped all samples, post_split would have been Nx0 and failed FIRST.
      It did not. Collapse is strictly inside Phase 2 (sample_qc), downstream of
      all aux joins. The env-derive/suffix-discover aux refactor is NOT implicated.

  STRATEGIC BOTTOM LINE: This is NOT scale-invariant and is NOT a real catastrophe.
  It does NOT justify abandoning AoU AFR WGS for 1000G. It is a cheap-tier false
  negative + a missing degeneracy guard. AoU AFR WGS remains the committed
  genome-wide substrate.

  COVERAGE GAP that let it through: the only end-to-end col-retention test
  (tests/m3/test_aou_ld_panel_local.py:925-941) runs load_qc_cohort with NO
  interval_filter over the full synthetic fixture, and the fixture is built with
  hl.balding_nichols_model (fully-called genotypes, zero missingness), so
  sqc.call_rate == 1.0 for every sample and the >=0.98 filter is a guaranteed
  no-op. The nano + missingness path was never exercised.

fix: |
  APPLIED 2026-06-03 (commits e5bf0e7 RED + fad2847 GREEN, branch
  m3-W2-aou-deltas). Implements the approved design at
  docs/superpowers/specs/2026-06-03-nano-sample-axis-callrate-guard-design.md
  exactly (5 parts). Genome-scale path held byte-identical; only the degenerate
  small-span case changes. Het guard, aux resolution, and the colon/driver-
  collect fixes are untouched.

  1. Degeneracy guard (src/python/aou_ld_panel.py:~1457-1485, Phase 2):
       mt = hl.sample_qc(mt, name="sqc")
       _n_var = mt.count_rows()
       if _n_var < MIN_VARIANTS_FOR_SAMPLE_CALLRATE:
           cr = mt.aggregate_cols(hl.agg.stats(mt.sqc.call_rate))
           print("[load_qc_cohort] SKIP call_rate sample filter — only ...")
           sample_callrate_filtered = False
       else:
           mt = mt.filter_cols(mt.sqc.call_rate >= MIN_CALL_RATE_SAMPLE)
           sample_callrate_filtered = True
     Mirrors the het filter's `stdev > 0` degeneracy guard directly below it.

  2. New constant MIN_VARIANTS_FOR_SAMPLE_CALLRATE = 500_000 near the other QC
     constants (aou_ld_panel.py:~221), with the derivation comment (nano density
     ~59.5K/Mb; whole-chr22 ~2.4M; 500K never trips at whole-chromosome-or-larger
     scale, always trips at nano).

  3. Truthful provenance — PROVENANCE-THREADING APPROACH CHOSEN: a HYBRID of the
     spec's options, the only one that respects the existing resume-validation
     contract:
       - The CONSTANT MIN_VARIANTS_FOR_SAMPLE_CALLRATE goes into
         _collect_provenance().params (spec option b for the constant). It is a
         genuine QC parameter, so _validate_sidecar SHOULD invalidate
         intermediates if it changes — symmetric with the other 7 thresholds.
       - The RUNTIME OUTCOME sample_callrate_filtered (the per-fire boolean) is
         threaded into the post_sample_qc sidecar at write time via a new
         _write_sidecar(..., sample_callrate_filtered: bool | None = None) kwarg,
         and ADDED to _SIDECAR_COMPARE_EXCLUDE_FIELDS.
       WHY NOT spec option (a) (mutate the provenance dict before the
       post_sample_qc write): _collect_provenance's output is reused UNMUTATED
       across BOTH sidecars (post_split + post_sample_qc) AND is the object
       compared field-by-field by _validate_sidecar (aou_ld_panel.py:584) on
       resume. Baking a runtime outcome into it would (i) leak into the
       post_split sidecar (where the guard has not run yet), and (ii) be compared
       on resume — spuriously invalidating a valid post_sample_qc intermediate,
       since the outcome is a RESULT, not an INPUT. Threading it through
       _write_sidecar (None for post_split => no field written; bool for
       post_sample_qc) + excluding it from comparison keeps the reuse-without-
       mutation contract intact and still records the truth honestly per
       [[feedback_aou_success_marker_not_evidence_of_data]].

  4. Assertion-message fix (_assert_checkpoint_nonempty, aou_ld_panel.py:~834):
     branches on the axis — rows>0/cols==0 => "sample (column) axis collapsed
     during {phase} — every sample dropped by a QC predicate; ... This is NOT the
     m3-W1 finalize catastrophe (which is 0x0)."; cols>0/rows==0 => analogous
     variant-axis message; true 0x0 => the existing finalize-catastrophe message
     preserved verbatim with all cross-reference pointers.

  5. Regression test (close the coverage gap, TDD RED-first):
     - tests/m3/fixtures/build_synthetic_mt.py: new --missingness knob (default
       0.0 => backward-compatible fully-called fixture) injecting deterministic
       per-genotype no-calls so call_rate < 1.0 is achievable.
     - tests/m3/conftest.py: synthetic_mt_path_missing fixture (~5% missingness).
     - tests/m3/test_aou_ld_panel_local.py: pure-Python RED-first tests for the
       assertion-message branches, the constant + its provenance.params entry,
       and the sample_callrate_filtered sidecar threading; plus two hail-gated
       integration tests (guard skip-on-nano cols-retained / provenance False;
       above-floor filter-still-drops-bad-sample / provenance True).

  EVIDENCE:
    RED (smoke_dev pytest, no hail): 5 pure-Python tests FAILED pre-fix
      (ImportError: MIN_VARIANTS_FOR_SAMPLE_CALLRATE; TypeError:
      _write_sidecar() unexpected kwarg; missing sample-axis/variant-axis
      message); test_assert_checkpoint_zero_by_zero PASSED (0x0 message
      preserved); 2 hail-gated tests SKIPPED locally.
    GREEN (smoke_dev pytest): full tests/m3 = 122 passed / 29 skipped (baseline
      116 / 27; +6 passed [5 newly-green pure-Python + the 0x0-preserved test
      counted in the suite delta], +2 skipped = the 2 hail-gated integration
      tests). Colon-fix + driver-collect + Track-4 _assert_checkpoint_nonempty
      regression tests all still green (31 passed / 1 skipped in the targeted
      sweep). Diff scope on src confined to the 5 intended regions
      (git diff --stat: 109 insertions / 10 deletions, 1 file); het guard,
      driver-collect read-back, naive_coalesce, _post_split_read_partitions
      untouched.

  NOTE: NCSU has no hail env, so the two hail-gated integration tests SKIP
  locally (consistent with the 27->29 skip baseline). They lock the
  guard-skip-cols-retained and above-floor-filter-applies behavior and will run
  on a hail env / the AoU cluster at Gate B re-fire.

  --- ORIGINAL DIAGNOSE-ONLY RECOMMENDATION (superseded by the applied fix above) ---

  PRIMARY (recommended): Add a nano-degeneracy guard to the call_rate sample
  filter symmetric with the het filter's stdev>0 guard. The cleanest correct
  fix is to compute sample call_rate over a VARIANT-QC'd variant set rather than
  the raw pre-QC nano window -- i.e. gate the call_rate filter on a minimum
  effective variant count and/or apply a basic variant call-rate prefilter to
  the variants used for sample_qc so a tiny low-quality window cannot
  systematically depress every sample. Options, in order of rigor:
    1. (Most defensible) Move/duplicate a lightweight variant call-rate prefilter
       (vqc.call_rate >= MIN_CALL_RATE_VARIANT) BEFORE sample_qc on intervals
       below a span/variant-count threshold, so sample call_rate is measured over
       reasonable-quality variants. Preserves canonical sample-before-variant QC
       at genome scale while preventing the nano pathology. Document the
       asymmetry explicitly.
    2. (Minimal, matches het precedent) Guard: only apply the call_rate
       filter_cols when n_variants in scope exceeds a documented floor (e.g.
       skip on span-bounded nano intervals where the metric is unreliable, the
       same posture as the het stdev>0 skip). On the nano tier the filter is a
       diagnostic, not a real QC step.
    3. Add an assertion that captures WHY all samples dropped (log call_rate
       distribution: mean/min/max/quantiles via aggregate_cols) before the
       filter, so any future collapse is self-explaining rather than hitting
       the misleading "empty-MT catastrophe" canned message.
  Also: fix the misleading _assert_checkpoint_nonempty message for the rows>0,
  cols==0 case -- distinguish "sample axis collapsed (QC dropped all cols)" from
  the true 0x0 platform-finalize catastrophe.

  REGRESSION TEST (close the coverage gap): extend the synthetic fixture to
  inject per-genotype missingness (set a fraction of GT to hl.missing so
  call_rate < 1.0) AND add a load_qc_cohort test that passes a span-bounded
  interval_filter through Phase 2, asserting cols are retained under the fix.

verification: |
  Code-only confirmation is STRONG (mechanism traced end-to-end; H1/H3 refuted by
  the post_split-passed evidence + interval-invariance of aux tables; H2 confirmed
  by AoU ACAF FT-no-call documentation). If a cents-level live probe is desired
  before committing a fix, it is OPTIONAL, not required:
    Read the persisted post_split intermediate from the bucket and print the
    call_rate distribution + surviving cols after each Phase-2 step (NO re-fire,
    NO recompute of Phase 1):

      import hail as hl
      mt = hl.read_matrix_table(
        "gs://rw-migration-aou-rw-476cdac2/ld/intermediate/"
        "mt_afr_post_split_chr22_16000000_18000000.mt")
      mt = hl.sample_qc(mt, name="sqc")
      s = mt.aggregate_cols(hl.agg.stats(mt.sqc.call_rate))
      print("call_rate mean/min/max:", s.mean, s.min, s.max)
      print("cols >= 0.98:",
            mt.filter_cols(mt.sqc.call_rate >= 0.98).count_cols())

    EXPECTED if H2 holds: s.max < 0.98 (every sample below threshold) ->
    "cols >= 0.98: 0". This reads one already-written nano checkpoint (cents),
    confirms the collapse is at the call_rate step, and confirms it is a small-
    window artifact (call_rate.mean depressed because variants are unfiltered).

  FIX VERIFICATION (2026-06-03, code-side, NCSU):
    - RED demonstrated: 5 pure-Python tests failed pre-fix (the guard, constant,
      provenance threading, and assertion-message branches were absent),
      reproducing the contract of the 118903x0 collapse; the 0x0-preserved test
      passed throughout (existing finalize message untouched).
    - GREEN: full tests/m3 = 122 passed / 29 skipped (baseline 116 / 27).
    - Genome-scale path unchanged: above-floor branch still applies the 0.98
      filter (locked by the hail-gated above-floor test, which drops a
      genuinely-bad sample and records provenance flag True); src diff confined
      to 5 intended regions; het guard / driver-collect / colon fixes byte-
      identical.
    HUMAN-VERIFY REMAINING: confirm end-to-end at the Gate B nano re-fire that
    post_sample_qc writes with non-zero cols (filter skipped + SKIP line logged),
    all 3 cohort MTs populate, and the assertions stay silent = PASS. The two
    hail-gated integration tests cannot run NCSU-side (no hail env), so the live
    re-fire is the column-retention end-to-end proof.

files_changed:
  - src/python/aou_ld_panel.py: MIN_VARIANTS_FOR_SAMPLE_CALLRATE constant; Phase-2 call_rate degeneracy guard (skip below floor, log, set sample_callrate_filtered); constant added to _collect_provenance.params; _write_sidecar gains sample_callrate_filtered kwarg threaded into the post_sample_qc sidecar; sample_callrate_filtered added to _SIDECAR_COMPARE_EXCLUDE_FIELDS; _assert_checkpoint_nonempty message branched (sample-axis / variant-axis / true 0x0).
  - tests/m3/fixtures/build_synthetic_mt.py: --missingness knob (default 0.0, backward-compatible).
  - tests/m3/conftest.py: synthetic_mt_path_missing fixture (~5% missingness).
  - tests/m3/test_aou_ld_panel_local.py: 5 pure-Python RED-first tests + 2 hail-gated integration tests.

confirming_forensics: |
  Carter's live byte-level forensics (referenced in the design spec as
  .planning/debug/m3-W2-gateB-nano-FAIL-diagnostics.md) were NOT committed to
  this branch (file absent at fix time). The confirming forensics are recorded
  in the design spec
  (docs/superpowers/specs/2026-06-03-nano-sample-axis-callrate-guard-design.md,
  "Evidence" section) and summarized here: post_split part-0 = 245,342 bytes
  (full sample table) -> post_sample_qc part-0 = 35 bytes (schema, 0 data rows);
  Hail log "wrote matrix table with 118903 rows and 0 columns" -> cols honestly
  0 in-memory before the checkpoint (rules out I/O / _SUCCESS-over-missing-bytes
  corruption). Three independent lines agree (debugger code analysis + Carter
  byte-level forensics + AoU ACAF FT-no-call documentation).

## RESOLUTION (live-verified, 2026-06-03)

status: RESOLVED — fix LIVE-VERIFIED on AoU. Human-verify checkpoint response: CONFIRMED FIXED.

fix_commits:
  - e5bf0e7  test(m3-nano-sqc): RED regression for sample-axis call-rate collapse
  - fad2847  fix(m3-nano-sqc): guard call_rate sample filter against nano degeneracy
  - 9f0c837  the live-verified HEAD (Gate B re-fire #3 ran on this commit)

implemented_design: docs/superpowers/specs/2026-06-03-nano-sample-axis-callrate-guard-design.md
  (the approved 5-part design; implemented exactly — degeneracy guard mirroring the het
  stdev>0 precedent, MIN_VARIANTS_FOR_SAMPLE_CALLRATE=500_000 constant, truthful
  provenance threading, branched assertion message, faithful regression test).

confirming_forensics: .planning/debug/m3-W2-gateB-nano-FAIL-diagnostics.md
  (Carter's live byte-level forensics of re-fire #2: post_split part-0 = 245,342 bytes
  full sample table -> post_sample_qc part-0 = 35 bytes schema-only; Hail log "wrote
  matrix table with 118903 rows and 0 columns" — three independent lines agreeing the
  collapse was honest in-memory sample-axis loss at the call_rate filter, NOT I/O
  corruption and NOT the m3-W1 0x0 finalize catastrophe).

live_verification:
  run: Gate B nano re-fire #3, HEAD 9f0c837, Hail Genomics cluster (n2-standard-16 master
       + 4x n2-standard-16 workers), INTERVAL=chr22:16000000-18000000, YARN-confirmed
       executor.cores=1 / 5g.

  guard_fired: The EUR cohort log printed the EXACT expected SKIP line:
    "[load_qc_cohort] SKIP call_rate sample filter — only 118903 variants (< 500000);
     call_rate degenerate on this span (mean=0.7942 max=0.8503)"
    (mean=0.7942, max=0.8503 — every sample below the 0.98 threshold, mechanically
     confirming H2: at nano scale the metric is degenerate and would have nuked all
     samples had the filter applied.)

  sample_axis_retained_end_to_end (the 3-cohort col-retention table — the one thing
  unprovable NCSU-side; hand-transcribed from live Hail write-logs + bucket verification
  on 2026-06-03, because the cohort_summary TSV did NOT auto-write — see entries-path
  follow-up note below):

    | Cohort                  | MT                          | Final dims              | _SUCCESS | Notes                                                                      |
    |-------------------------|-----------------------------|-------------------------|----------|----------------------------------------------------------------------------|
    | AFR primary             | mt_afr_qc.mt                | 18,648 var x 74,065 smp | PRESENT  | post_split 118903x74576 -> post_sample_qc 118903x74065 (dropped ~511 = sane QC) |
    | AFR PCA-selfid          | mt_afr_pca_selfid_qc.mt     | populated               | PRESENT  | populated, _SUCCESS present                                                 |
    | EUR                     | mt_eur_qc.mt                | 10,199 var x 221,572 smp| PRESENT  | post_split 118903x222502 -> post_sample_qc 118903x221572 -> final; ~3.25 GB on disk |

    (Prior failure was 118903 x 0 on EVERY cohort. The sample axis now survives sample-QC
     on all three; the ~511-sample and ~930-sample drops are normal downstream QC, not
     collapse.)

  assertion_silent: _assert_checkpoint_nonempty (the count-based, path-INDEPENDENT gate)
    stayed SILENT on all three cohorts — the genuine end-to-end PASS signal. This is the
    real gate (count_rows/count_cols based), independent of the entries-path bug noted
    below.

disposition (Carter's standing framing): this is "no cheap failure mode reproduced —
  escalating to the real test," NOT "validated." The m3-W1 empty-MT catastrophe is RULED
  OUT at the nano tier; the column-retention guard is proven on live AoU data. The actual
  sample-QC threshold validation belongs to Gate C (chr22-full, ~2.4M variants). Cluster
  torn down -> $0.

separate_followup (NOT part of this session — a distinct future /gsd-debug):
  entries-path bug. The du-floor diagnostic cells, the catastrophe guard
  _validate_checkpoint_populated, the auto-resume kill-mtime check, and the tests all
  probe entries/entries/parts/, which does NOT exist on a real Hail 0.2.135 MatrixTable —
  real entry data lives at entries/rows/parts/ (Carter verified: EUR mt 3.25 GB total,
  3.24 GB at entries/rows/parts/, entries/entries/parts/ absent). The bug is FAIL-SAFE
  (wrong path => false-positive / force-recompute; never passes an empty MT as populated),
  so THIS session's PASS is VALID (the real gate is the path-independent count-based
  _assert_checkpoint_nonempty). But the entries-path bug blocked the cohort_summary TSV
  auto-write (Cell 5.5 false-positive) and must be fixed before Gate C. Tracked in
  STATE.md as a Gate-C blocker; do NOT conflate with this resolved session.
