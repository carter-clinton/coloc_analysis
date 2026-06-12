---
status: awaiting_human_verify
trigger: "m3-W2-a3-blockmatrix-write-ir-lowering-hang — compute_region_ld Path A.3 ld_bm.write() on a fused lazy BlockMatrixIR hangs (BlockMatrixIR lowering not yet efficient/scalable -> interpreted BlockMatrixWrite -> driver-bound hang)"
created: 2026-06-12T00:00:00Z
updated: 2026-06-12T00:30:00Z
mode: symptoms_prefilled / find_and_fix
---

## Current Focus

hypothesis: LOCKED (do not re-investigate). `hl.ld_matrix(...)` returns a fused lazy
  BlockMatrixIR (row_correlation of standardized genotypes + radius banding). `.write()`
  on that fused IR triggers Hail's non-scalable BlockMatrixIR lowering -> falls back to the
  interpreted (driver-mediated) BlockMatrixWrite -> hangs on large banded matrices.
test: standalone cluster repro (a3_blockmatrix_lowering_repro.py) runs OLD vs NEW path on a
  small synthetic MT and inspects the Hail driver log for the "BlockMatrixIR lowering not yet
  efficient/scalable" warning (VISIBLE on OLD, ABSENT on NEW) + asserts a valid .bm/_SUCCESS on NEW.
expecting: NEW path materializes the correlation BlockMatrix to disk (native distributed writer)
  BEFORE the sparsify+write, so the final write IR is small and lowers natively.
next_action: implement A.3-only fix in compute_region_ld; add pure-Python regression tests;
  write the cluster repro; commit + push.

## Symptoms
<!-- IMMUTABLE -->

expected: A.3 regions write a valid distributed BlockMatrix (.bm dir with _SUCCESS + populated
  blocks) in bounded time, lowering to Hail's native distributed writer.
actual: On region m2_region_00006 (AFR, span 17.7 Mb, n_var=122,678) the `ld_bm.write(bm_uri)`
  hung ~63+ min with zero forward progress; driver jstack `main` parked in Py4J gateway recv
  (1.4s CPU / 73 min wall); Spark stage `collect at ContextRDD.scala:172` 0/900 (reached 736/900
  only when force-killed); 0-byte then 99 GB orphan partial; no _SUCCESS.
errors: Driver hail log: "LowerOrInterpretNonCompilable: cannot efficiently lower query:
  BlockMatrixIR lowering not yet efficient/scalable" then "interpreting non-compilable result:
  BlockMatrixWrite". On kill: FatalError SparkException "Job 6 cancelled" at
  is.hail.linalg.BlockMatrix.write(BlockMatrix.scala:978) <- ContextRDD.collect(ContextRDD.scala:172).
reproduction: Run compute_region_ld on any region routed to Path A.3 (region_class large/xlarge
  OR span > PATH_A2_MAX_MB=10 Mb). A.3 branch: ld_bm = hl.ld_matrix(...) (~line 2214), then in the
  else/A.3 branch ld_bm.write(bm_uri, overwrite=True) (~line 2309).
started: First surfaced 2026-06-12 on the dev-10 GATE-2 fire (first live A.3 write). Path A.1/A.2
  (to_numpy) regions are unaffected.

## Eliminated
<!-- APPEND only -->

- hypothesis: knowledge-base match (no entry overlaps this error pattern)
  evidence: scanned .planning/debug/knowledge-base.md; the closest entries are empty-MT/_SUCCESS
    (different mechanism: driver-kill or executor truncation, NOT IR lowering) and the sample-axis
    collapse (QC, not BlockMatrix). This is a NOVEL bug class (Hail BlockMatrixIR lowering, not data validity).
  timestamp: 2026-06-12T00:00:00Z

## Evidence
<!-- APPEND only -->

- timestamp: 2026-06-12T00:00:00Z
  checked: hl.ld_matrix internals (hail.is BlockMatrix + genetics docs; Pan-UKBB compute_ld_matrix.py)
  found: hl.ld_matrix(entry_expr, locus_expr, radius) is documented as:
    "sparsifies the result of row_correlation() using linalg.utils.locus_windows() and
    BlockMatrix.sparsify_row_intervals()". I.e. ld_matrix = row_correlation(GT) -> sparsify_row_intervals
    (banded by locus_windows). row_correlation mean-imputes missing genotypes WITHIN variant,
    centers + normalizes each row to unit variance, then computes the Gram matrix => Pearson r.
    The whole thing is one fused lazy BlockMatrixIR; .write() lowers it as a single query.
  implication: We do NOT need to hand-roll standardization. We can reproduce ld_matrix EXACTLY by
    calling its own building blocks (row_correlation + locus_windows + sparsify_row_intervals) and
    insert a CHECKPOINT between the correlation and the sparsify+write. The checkpoint materializes
    the dense-banded correlation BM to disk via the native distributed writer, breaking the fused IR;
    the final write then reads a concrete BM + applies sparsify (small IR) and lowers natively.
    This is the canonical Pan-UKBB production pattern (they checkpoint_tmp the BM before writing).

- timestamp: 2026-06-12T00:00:00Z
  checked: hl.row_correlation availability + checkpoint semantics
  found: hl.row_correlation(entry_expr) exists in Hail 0.2 (hail.methods.statgen) and returns a
    BlockMatrix. BlockMatrix.checkpoint(path) "interrupts lazy evaluation and materializes the matrix
    to disk" and returns a BlockMatrix backed by that on-disk read (native writer, not IR interpreter).
    hl.linalg.utils.locus_windows(locus_expr, radius) returns (starts, stops) row-index arrays:
    [starts[i], stops[i]) is the maximal range of j with same contig and |pos_i - pos_j| <= radius.
    BlockMatrix.sparsify_row_intervals(starts, stops, blocks_only=False) keeps exactly those entries
    (blocks_only=False preserves the exact r values within band; blocks_only=True would zero whole
    off-band blocks but can include extra in-block entries — we want EXACT band parity with ld_matrix,
    so blocks_only=False).
  implication: NEW A.3 path = row_correlation(GT) -> checkpoint(tmp) -> sparsify_row_intervals(
    locus_windows(radius)) -> write. Numerically IDENTICAL to hl.ld_matrix (same standardization,
    same banding), but the write IR is broken so it lowers to the native distributed writer.

- timestamp: 2026-06-11T18:00:00Z
  checked: code review (m3-W2-a3-blockmatrix-write-ir-lowering-hang-REVIEW.md) — CR-01 + WR-01..04 + IN-01..03
  found: REMEDIATION APPLIED (this session). (1) CR-01 confirmed real: ordering A checkpoints the
    UN-banded full-dense correlation -> O(n_var^2) scratch (~60 GB region_00006, ~2 TB
    m2_region_00145). The doc's "radius-banded not dense" claim was wrong and is corrected above.
    (2) The review's suggested band-before-checkpoint (ordering B) was NOT adopted as the default
    because `.checkpoint()` is a write and band-before-checkpoint re-materializes the SAME fused
    correlation+band IR that hung — it might re-hang. (3) scripts/a3_blockmatrix_lowering_repro.py
    restructured into a 3-WAY ordering experiment (OLD / A / B) that, per ordering, reports the
    lowering-warning presence + scratch footprint + .bm validity + r-parity vs OLD, plus a no-Hail
    `--report-scratch-size` mode that extrapolates dense-vs-banded scratch from config/ld_regions.tsv
    (worst case m2_region_00145 ~1.8 TiB). (4) WR-02 observability + soft-guard log added to
    _write_a3_banded_correlation_bm (logs n_var + dense footprint before the checkpoint; loud WARN
    past 300 GiB). (5) IN-01: routing now happens before `ld_bm = hl.ld_matrix(...)`, which is
    constructed ONLY for A.1/A.2 (A.3 no longer holds the unused fused IR). (6) New pure-Python
    helper `_dense_footprint_bytes(n_var)` + unit tests. Full m3 suite 153 passed / 35 skipped.
  implication: GATE-3 (322-cell production) is BLOCKED on CR-01. The cluster ordering experiment
    must decide the production ordering BEFORE GATE-3 fires (see Resolution.gate3_blocker).

## Resolution
<!-- OVERWRITE as understanding evolves -->

root_cause: |
  hl.ld_matrix(GT, locus, radius) builds a single fused lazy BlockMatrixIR:
  row_correlation(standardized genotypes) [G-center-normalize then G @ G.T] composed with the
  locus_windows radius banding (sparsify_row_intervals). Calling .write() on that fused IR forces
  Hail to lower the *entire* composed BlockMatrixIR in one query. Hail 0.2.135's BlockMatrixIR
  lowerer cannot lower this composition scalably -> it emits
  "BlockMatrixIR lowering not yet efficient/scalable" and falls back to the INTERPRETED
  (driver-mediated) BlockMatrixWrite path (`interpreting non-compilable result: BlockMatrixWrite`).
  The interpreted writer drives the matrix through a single driver-side ContextRDD.collect
  (BlockMatrix.scala:978 <- ContextRDD.scala:172), which serializes the whole banded matrix through
  the driver -> on a 122,678 x 122,678 banded matrix (region m2_region_00006, span 17.7 Mb) it hangs
  for 60+ min with no forward progress. This is structural to the FUSED IR, not a data/OOM/kill bug,
  so it deterministically blocks all 36 large/xlarge A.3 regions. A.1/A.2 are unaffected because they
  call to_numpy() (a different, already-materializing collect path) on much smaller spans.

fix: |
  A.3-ONLY restructure (A.1/A.2 untouched, still use the existing `ld_bm = hl.ld_matrix(...)`).
  Replace the fused `hl.ld_matrix(...).write()` in the A.3 branch with hl.ld_matrix's OWN internal
  steps, inserting a checkpoint that breaks the fused IR:

    1. corr_bm = hl.row_correlation(mt_r.GT.n_alt_alleles())     # standardized Pearson-r Gram matrix
    2. corr_bm = corr_bm.checkpoint(scratch_uri)                  # MATERIALIZE -> native distributed writer
                                                                  #   (breaks the fused IR; the write that
                                                                  #    follows reads a concrete BM)
    3. starts, stops = hl.linalg.utils.locus_windows(mt_r.locus, radius=radius_bp)  # bp radius -> row-index band
    4. banded = corr_bm.sparsify_row_intervals(starts, stops, blocks_only=False)    # EXACT same band as ld_matrix
    5. banded.write(bm_uri, overwrite=True)                       # small IR (read-checkpoint + sparsify) -> lowers

  Then the existing _assert_blockmatrix_written guard + the CR-003 variant_ids/rsids sidecar
  emission/upload run UNCHANGED. A new pure helper `_a3_scratch_uri(bm_uri)` derives the scratch
  checkpoint path (bm_uri + ".corr_scratch.bm") so it is path-isolated and overwritable; the scratch
  is best-effort cleaned after the final write (its survival is harmless — overwrite=True on re-fire).

  STANDARDIZATION/BANDING TRADEOFF (chosen + why):
  - We do NOT hand-roll standardization. row_correlation IS ld_matrix's own standardization
    (mean-impute within variant + center + unit-normalize each row, then Gram). Calling it directly
    guarantees the output is the SAME Pearson r as the old path — zero numerical drift risk. This is
    strictly preferable to writing our own from_entry_expr center/scale (which could silently emit raw
    covariance instead of r — the exact trap called out in the hypothesis).
  - Banding: the radius is in BASE PAIRS. ld_matrix maps bp radius -> row-index windows via
    locus_windows (the loci are sorted, so a bp window is a contiguous row-index interval). We reuse
    locus_windows directly, so the NEW band is BYTE-equivalent to ld_matrix's band. We use
    blocks_only=False to keep exact in-band r values (blocks_only=True trades exactness for fewer
    blocks — wrong for an LD reference panel consumed by SuSiE-RSS).
  - One extra on-disk materialization (the scratch correlation BM) is the cost. CORRECTION
    (2026-06-11, review CR-01): the EARLIER claim here — "radius-banded, not the full O(n^2)
    dense" — was FACTUALLY WRONG for the code as written. The current ordering (call it
    ordering A) checkpoints `hl.row_correlation(...)` BEFORE `sparsify_row_intervals`, so the
    scratch BM is the FULL DENSE n×n float32 correlation matrix (O(n_var^2)), NOT the banded
    one. The band is applied only AFTER the checkpoint, to the already-materialized dense
    scratch. Quantified: region_00006 (n_var=122,678) -> ~60 GB dense scratch; the largest
    production region m2_region_00145 (102.5 Mb, ~710k var) -> ~2 TB dense scratch.
    The 50-Mb-banded xlarge invariant (HIGH-3) is preserved for the FINAL .bm (locus_windows
    uses the SAME radius_bp), but it does NOT bound the scratch.
  - WHY WE DID NOT BLINDLY SWITCH TO band-before-checkpoint (ordering B): `.checkpoint()` IS a
    write, so checkpointing `row_correlation -> sparsify_row_intervals` materializes the SAME
    fused (correlation+band) IR shape that originally hung as `hl.ld_matrix(...).write()`.
    Ordering B MIGHT RE-INTRODUCE THE HANG. Ordering A checkpoints `row_correlation` ALONE
    (likely lowers) precisely to avoid that fusion. WHICH ORDERING ACTUALLY LOWERS IS
    EMPIRICALLY UNKNOWN WITHOUT THE CLUSTER. Therefore the production default ordering is NOT
    changed here; the cluster repro (now a 3-way ordering experiment) decides — see CR-01 below.

verification: |
  PURE-PYTHON (run here, NCSU HPC — Hail not importable): regression tests for
    (a) _route_region_path unchanged (existing test_route_region_path_oom_veto still green),
    (b) new _a3_scratch_uri helper (path-isolated, deterministic, idempotent),
    (c) static-AST check that the A.3 branch now calls row_correlation + locus_windows +
        sparsify_row_intervals + checkpoint, and that A.1/A.2 still reference ld_matrix/to_numpy,
    (d) static-AST check that _assert_blockmatrix_written + sidecar emission still present after the write.
  CLUSTER (Carter runs; Hail-required, NOT runnable here): a3_blockmatrix_lowering_repro.py is now a
    3-WAY ORDERING EXPERIMENT. It builds a small synthetic MT and runs OLD `hl.ld_matrix(...).write()`,
    ordering A (checkpoint dense correlation -> band -> write; current default), and ordering B
    (band -> checkpoint banded -> write; the review's proposal that MIGHT re-hang). For EACH it reports
    the lowering-warning presence (PRESENT on OLD = positive control; the A/B results DECIDE), the
    scratch footprint (dense vs banded), .bm validity ((n,n)+_SUCCESS), and r-parity vs OLD. A no-Hail
    `--report-scratch-size` mode extrapolates the dense-vs-banded scratch at REAL production n_var from
    config/ld_regions.tsv so a green small-n run cannot falsely clear GATE 3.
    DECISION RUBRIC: ship the warning-free ordering with the smallest scratch; if both A and B are
    warning-free, prefer B (banded); if only A is warning-free, A is required and the ~2 TB worst-case
    must be sized against cluster scratch capacity. THIS experiment is the lowering PROOF + the
    GATE-3 ordering decision — the pure-Python tests cannot exercise Hail.
  PURE-PYTHON STATUS: PASS. `tests/m3/ -q` => 153 passed, 35 skipped (Hail-gated skips expected).
    5 pure-Python guards green: test_a3_scratch_uri_is_path_isolated_and_idempotent,
    test_a3_branch_uses_materialize_then_band_not_fused_write,
    test_a3_helper_does_not_call_fused_ld_matrix_write, test_dense_footprint_bytes_matches_n2_times_4,
    test_dense_footprint_helper_used_by_a3_write_for_observability. The existing OOM-veto routing test
    (test_route_region_path_oom_veto) still green (A.1/A.2 routing unchanged).
  CLUSTER STATUS: PENDING (Carter). scripts/a3_blockmatrix_lowering_repro.py is the lowering PROOF
    + the GATE-3 ordering decision (3-way experiment).
gate3_blocker: |
  CR-01 (review 2026-06-11): GATE-3 (322-cell production) is BLOCKED until the cluster ordering
  experiment (scripts/a3_blockmatrix_lowering_repro.py) picks a warning-free ordering whose
  worst-case scratch fits cluster scratch capacity. The current default (ordering A) checkpoints
  the FULL DENSE n×n correlation (~2 TB worst case, m2_region_00145 ~710k var). Ordering B
  (band-before-checkpoint) shrinks scratch ONLY for mid-size A.3 regions — for the ~100 Mb
  xlarge regions the 50-Mb-capped radius bands ~98% of the row, so banded ≈ dense, and B might
  re-hang anyway. dev-10 GATE-2 (one dev region, region_00006 ~60 GB scratch, ordering A) is
  TOLERABLE and may proceed on current code; the production 322-cell fire is NOT until CR-01 is
  resolved by the cluster experiment. See WAVE-2-GATE-READINESS.md.
files_changed:
  - src/python/aou_ld_panel.py (A.3-only: route-before-ld_bm so the fused ld_bm is built ONLY for A.1/A.2 [IN-01]; _dense_footprint_bytes helper [WR-02]; _write_a3_banded_correlation_bm logs n_var + dense footprint + loud WARN past 300 GiB before the checkpoint [WR-02]; A.1/A.2 + MED-4 guard + CR-003 sidecars behaviorally untouched; default ordering A UNCHANGED — the cluster decides A vs B)
  - tests/m3/test_aou_ld_panel_local.py (3 prior A.3 guards + 2 new: _dense_footprint_bytes unit test + static-AST that the A.3 helper logs the footprint)
  - scripts/a3_blockmatrix_lowering_repro.py (RESTRUCTURED into a 3-way OLD/A/B ordering experiment + no-Hail --report-scratch-size extrapolation + decision rubric)
  - .planning/phases/m3-aou-afr-ld-panel-build/WAVE-2-GATE-READINESS.md (dev-10 GATE-2 may proceed on ordering A; GATE-3 BLOCKED on CR-01)

## .continue-here / SUMMARY
<!-- What still needs the cluster before dev-10 GATE-2 resumes -->

WHAT LANDED (NCSU-side, original fix):
- A.3-only code fix in src/python/aou_ld_panel.py. The fused `hl.ld_matrix(...).write()` is replaced
  in BOTH A.3 sub-branches (local-test + bucket) by `_write_a3_banded_correlation_bm(...)`, which does
  row_correlation -> checkpoint(scratch) -> locus_windows(radius_bp) -> sparsify_row_intervals
  (blocks_only=False) -> write(stage_locally=True). Numerically identical to the old path.

WHAT LANDED (REMEDIATION, 2026-06-11 review pass):
- CR-01 corrected in this doc: ordering A checkpoints the FULL DENSE n×n correlation (~2 TB worst case),
  NOT a banded matrix. The default ordering is INTENTIONALLY UNCHANGED (band-before-checkpoint = ordering
  B might re-hang because .checkpoint() is a write of the same fused IR; the cluster must decide).
- repro RESTRUCTURED into a 3-way OLD/A/B ordering experiment + a no-Hail --report-scratch-size mode
  (worst case m2_region_00145 ~1.8 TiB) + a decision rubric. WR-02 observability log + soft guard added.
  IN-01: ld_bm built only for A.1/A.2. New _dense_footprint_bytes helper + 2 unit tests.
- Full m3 suite 153 passed / 35 skipped.

WHAT STILL REQUIRES THE CLUSTER:
1. dev-10 GATE-2 (TOLERABLE on current ordering A; ~60 GB scratch for region_00006): run the repro
   ordering experiment, then re-fire the previously-hanging A.3 cell (m2_region_00006). Verify at the
   data layer (gsutil du of the .bm/parts + _assert_blockmatrix_written shape) — _SUCCESS is NOT proof.
2. GATE-3 (322-cell production) is BLOCKED on CR-01: the cluster ordering experiment must pick a
   warning-free ordering whose worst-case scratch (~2 TB) fits cluster scratch capacity. Apply the
   decision rubric in the repro docstring; if it selects ordering B, re-order
   _write_a3_banded_correlation_bm (band-before-checkpoint) and re-run --report-scratch-size before
   the production fire.

ONLY AFTER the cluster ordering experiment + the GATE-3 sizing decision is this session resolvable.
