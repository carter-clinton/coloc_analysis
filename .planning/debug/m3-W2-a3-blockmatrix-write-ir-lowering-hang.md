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
  - One extra on-disk materialization (the scratch correlation BM) is the cost. For a banded region
    that is bounded (radius-banded, not the full O(n^2) dense), and it is written by the SCALABLE
    native writer — which is the entire point. The 50-Mb-banded xlarge invariant (HIGH-3) is preserved
    because locus_windows uses the SAME radius_bp the old code passed to hl.ld_matrix.

verification: |
  PURE-PYTHON (run here, NCSU HPC — Hail not importable): regression tests for
    (a) _route_region_path unchanged (existing test_route_region_path_oom_veto still green),
    (b) new _a3_scratch_uri helper (path-isolated, deterministic, idempotent),
    (c) static-AST check that the A.3 branch now calls row_correlation + locus_windows +
        sparsify_row_intervals + checkpoint, and that A.1/A.2 still reference ld_matrix/to_numpy,
    (d) static-AST check that _assert_blockmatrix_written + sidecar emission still present after the write.
  CLUSTER (Carter runs; Hail-required, NOT runnable here): a3_blockmatrix_lowering_repro.py builds a
    small synthetic MT, runs OLD `hl.ld_matrix(...).write()` and NEW path, greps the Hail driver log
    for the lowering warning (must be PRESENT on OLD, ABSENT on NEW), and asserts a valid .bm/_SUCCESS
    on NEW with the expected (n,n) shape. THIS is the lowering PROOF — the pure-Python tests cannot
    exercise Hail.
  PURE-PYTHON STATUS: PASS. `tests/m3/ -q` => 151 passed, 35 skipped (Hail-gated skips expected).
    3 new pure-Python guards green: test_a3_scratch_uri_is_path_isolated_and_idempotent,
    test_a3_branch_uses_materialize_then_band_not_fused_write,
    test_a3_helper_does_not_call_fused_ld_matrix_write. The existing OOM-veto routing test
    (test_route_region_path_oom_veto) still green (A.1/A.2 routing unchanged).
  CLUSTER STATUS: PENDING (Carter). scripts/a3_blockmatrix_lowering_repro.py is the lowering PROOF.
files_changed:
  - src/python/aou_ld_panel.py (A.3-only: _a3_scratch_uri + _write_a3_banded_correlation_bm helpers; A.3 branch now calls the helper instead of ld_bm.write(); A.1/A.2 + MED-4 guard + CR-003 sidecars untouched)
  - tests/m3/test_aou_ld_panel_local.py (3 new pure-Python A.3 guards)
  - scripts/a3_blockmatrix_lowering_repro.py (NEW; cluster lowering proof)
  - .planning/phases/m3-aou-afr-ld-panel-build/WAVE-2-GATE-READINESS.md (A.3-fix note + re-fire flag)

## .continue-here / SUMMARY
<!-- What still needs the cluster before dev-10 GATE-2 resumes -->

WHAT LANDED (NCSU-side, this session):
- A.3-only code fix in src/python/aou_ld_panel.py. The fused `hl.ld_matrix(...).write()` is replaced
  in BOTH A.3 sub-branches (local-test + bucket) by `_write_a3_banded_correlation_bm(mt_r, radius_bp, uri)`,
  which does row_correlation -> checkpoint(scratch) -> locus_windows(radius_bp) -> sparsify_row_intervals
  (blocks_only=False) -> write(stage_locally=True). Numerically identical to the old path; A.1/A.2,
  the MED-4 `_assert_blockmatrix_written` guard, and the CR-003 sidecar emission/upload are unchanged.
- 3 pure-Python regression tests (above) — all green; full m3 suite 151 passed / 35 skipped.

WHAT STILL REQUIRES THE CLUSTER (BLOCKS dev-10 GATE-2 resume — Carter, Hail-required):
1. LOWERING PROOF: run scripts/a3_blockmatrix_lowering_repro.py on the Dataproc/Hail cluster.
   EXPECT: lowering-warning PRESENT on OLD, ABSENT on NEW; NEW .bm readable shape (n,n) + _SUCCESS;
   OLD vs NEW max|Δr| ~ 0 (parity). Run instructions are in the script docstring.
2. SMALL-REGION RE-TEST: after the repro passes, re-fire dev-10 GATE-2 with the fixed code. The
   previously-hanging A.3 cell (m2_region_00006, span 17.7 Mb) must write a valid .bm in bounded time.
   Verify at the data layer (gsutil du of the .bm/parts + _assert_blockmatrix_written shape) — _SUCCESS
   is NOT proof (the project invariant).

ONLY AFTER both cluster steps PASS is this session resolvable (move to resolved/ + KB entry + DEBUG COMPLETE).
