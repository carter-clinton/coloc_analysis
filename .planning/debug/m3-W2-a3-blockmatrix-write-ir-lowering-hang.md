---
status: resolved
trigger: "m3-W2-a3-blockmatrix-write-ir-lowering-hang — compute_region_ld Path A.3 ld_bm.write() on a fused lazy BlockMatrixIR hangs (BlockMatrixIR lowering not yet efficient/scalable -> interpreted BlockMatrixWrite -> driver-bound hang)"
created: 2026-06-12T00:00:00Z
updated: 2026-06-18T06:30:00Z
mode: symptoms_prefilled / find_and_fix
resolution: "FIX VALIDATED ON CLUSTER 2026-06-18 (quick 260618-3at). Ordering experiment ran on a 16-worker resize of cluster 20260617 (--skip-old --n-var 130000 --budget-sec 3600): ordering A COMPLETED 928.0s (valid A/repro_A.bm) = first cluster proof of the deployed fix; ordering B COMPLETED 863.5s (hang-free). --report-scratch-size shows banded(B)==dense(A) for ALL 23 A.3 regions (radius span+500kb, cap 50Mb, always >= span/2 -> band covers whole region) => B saves NO scratch => KEEP ordering A, B RETIRED. CR-01 reframed: ~1.8 TiB worst case (m2_region_00145) is ordering-INDEPENDENT; remaining GATE-3 question = xlarge dense-materialize compute cost vs region-splitting (NOT checkpoint ordering)."
---

## ★ 2026-06-18 RESOLUTION (quick `260618-3at`) — FIX CLUSTER-VALIDATED; KEEP A; B RETIRED

The cluster ordering experiment ran on a **16-worker resize of cluster `20260617`**
(`--skip-old --n-var 130000 --n-samples 2000 --radius-bp 1000000 --budget-sec 3600`,
`MASTER=yarn`, 64 concurrent tasks):

- **Ordering A COMPLETED — 928.0 s**, shape (130000,130000), valid `A/repro_A.bm`. The 21-second
  gap between the dense checkpoint write and the final write is the mechanism working as designed
  (final write reads concrete blocks → no driver collect). **First cluster validation of the
  deployed A.3 fix** — dev-10 had paused before ever confirming ordering A on a cluster.
- **Ordering B COMPLETED — 863.5 s**, valid `B/repro_B.bm`. B's `sparsify→checkpoint` (same IR
  shape as the OLD hung write) **did NOT reproduce the hang** — the IR-shape caveat is cleared.
- **OLD** skipped (`--skip-old`); the hang is already proven (dev-10 + the 8-vCPU 0.21 MiB/s grind
  on the prior 2-worker attempt, which confirmed OLD is driver-bound and intractable).
- The 2→16 resize succeeding **diagnosed the original 24-worker prod-cluster failure as
  quota/size-bound, not project-level** (perimeter/credit).

**DECISIVE FINDING (`--report-scratch-size`, full `config/ld_regions.tsv`):** `banded(B) ==
dense(A)` for **all 23 A.3 regions**, not just the worst. The manifest sets `radius = span+500kb`
(capped 50 Mb), which is always ≥ span/2, so the band covers ~the whole region for every A.3
region → **ordering B saves scratch NOWHERE.** The script's generic `SHIP B` line assumes
`banded ≪ dense`, which is false here.

**DECISION: KEEP ordering A** (deployed + now cluster-validated). **Ordering B RETIRED** — it is
byte-identical numerics with zero scratch benefit and nonzero change-risk; the
`DRAFT-orderingB-band-before-checkpoint.md` patch is parked (revisit only if a future manifest
adopts radius ≪ span). **CR-01 is ordering-INDEPENDENT:** region_00145 (~710k var) needs ~1.8 TiB
of transient GCS scratch under A *or* B. **The hang bug (this session's subject) is FIXED +
cluster-confirmed → session RESOLVED.** The remaining GATE-3 item is a SEPARATE scoping question
(xlarge dense-materialize compute cost vs region-splitting), tracked in WAVE-2-GATE-READINESS.md.

Everything below this block is the pre-experiment record (kept as history).

---

## Current Focus

hypothesis: LOCKED (do not re-investigate). `hl.ld_matrix(...)` returns a fused lazy
  BlockMatrixIR (row_correlation of standardized genotypes + radius banding). `.write()`
  on that fused IR triggers Hail's non-scalable BlockMatrixIR lowering -> falls back to the
  interpreted (driver-mediated) BlockMatrixWrite -> hangs on large banded matrices.
test: standalone cluster repro (a3_blockmatrix_lowering_repro.py) runs OLD / ordering A / ordering
  B on a synthetic MT at a HANG-INDUCING n_var and decides PASS on WALL-CLOCK COMPLETION within a
  per-ordering budget + valid .bm/_SUCCESS + r-parity vs OLD (adversarial review Finding B —
  re-gated 2026-06-12). The lowering warning is INFORMATIONAL ONLY (it fires on ALL BlockMatrix
  writes per CanLowerEfficiently; it is NOT the signal). OLD is the intractability control (expected
  to TIME OUT). The discriminator between A and B is completion-time + scratch footprint.
expecting: NEW path's checkpoint MATERIALIZES the matmul to concrete on-disk blocks BEFORE the
  sparsify+write, so the final (still-interpreted) write reads concrete blocks and is cheap — NOT
  "lowers natively" (the warning still fires). Ordering B (Pan-UKBB band-then-checkpoint) favored.
next_action: REMEDIATION COMPLETE (2026-06-12). Cluster experiment must decide ordering A
  (dense scratch) vs B (banded, Pan-UKBB-favored) on COMPLETION within budget at real region scales.

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

- timestamp: 2026-06-12T00:00:00Z
  checked: ADVERSARIAL CODE REVIEW — accepted findings (verified against Hail source) + remediation
  found: A second adversarial pass confirmed the fix's NUMERICS are byte-identical to hl.ld_matrix
    (sound — row_correlation + locus_windows + sparsify_row_intervals, blocks_only=False, same args)
    but found three real defects in the EXPLANATION + the REPRO + the ordering choice. ALL ACCEPTED:
    - FINDING A (HIGH): the lowering warning is CONSTANT, not eliminated. Hail
      `CanLowerEfficiently.scala` fails on EVERY `BlockMatrixWrite` unconditionally, and
      `.checkpoint()` IS a BlockMatrixWrite -> the warning fires on the OLD write, the checkpoint,
      AND the final write; all run interpreted (`LowerOrInterpretNonCompilable.scala` ->
      `Interpret.alreadyLowered`). The fix does NOT "lower to the native distributed writer." Its
      REAL mechanism: the checkpoint MATERIALIZES the matmul so the final interpreted write reads
      CONCRETE on-disk blocks (cheap) instead of driving an un-materialized matmul through the
      driver-side ContextRDD.collect (BlockMatrix.scala:978) that caused the OLD stall. Stated as
      "interpreted-but-cheap-because-inputs-are-concrete," with a version caveat (could not
      100%-confirm at 0.2.135 that no native-writer bypass exists for materialized sub-writes).
    - FINDING B (HIGH): the repro's PASS gate (`a_warning is False and a_ok`) was unsatisfiable —
      per Finding A the warning is ALWAYS present, so the repro always ESCALATED / returned 1 even
      when the fix works. RE-GATED on WALL-CLOCK COMPLETION at a hang-inducing scale: PASS = the
      ordering completes within a per-ordering wall-time budget AND produces a valid .bm AND matches
      OLD's r values. OLD is the intractability control (expected to TIME OUT); too-small --n-var =
      vacuous run (OLD completes, proves nothing) -> default --n-var raised + a vacuity warning. The
      warning grep is downgraded to informational logging with the CanLowerEfficiently explanation.
    - FINDING C (MEDIUM): ordering B (band-then-checkpoint) is the PROVEN Pan-UKBB production pattern
      (atgu/ukbb_pan_ancestry compute_ld_matrix.py: matmul -> _sparsify_row_intervals_expr ->
      sparsify_triangle -> checkpoint, at biobank scale). The "B might re-hang" fear was
      over-cautious / contradicted. B elevated to LEADING production-default candidate (avoids the
      CR-01 ~2 TB dense scratch; banded ~GB). Production default code stays A until the re-gated
      repro shows B completes within budget at the real 122k/710k scales (IR-shape caveat: OLD and B
      are the SAME BlockMatrixWrite(sparsify(matmul)) shape, so completion must be shown empirically).
    - FINDING D (LOW, NO CODE CHANGE): the fix's `locus_windows(..., _localize default True)` forces
      a ~5.7 MB driver collect of starts/stops for 710k vars — trivial (ld_matrix uses
      _localize=False). Minor non-issue; no action.
  implication: REMEDIATION APPLIED 2026-06-12: (1) repro RE-GATED on completion-within-budget +
    valid .bm + r-parity (Finding B) — new `_run_with_budget` helper, `--budget-sec`, default
    `--n-var=50000`, warning downgraded to informational; (2) mechanism prose corrected in
    aou_ld_panel.py (_a3_scratch_uri docstring, _write_a3_banded_correlation_bm docstring + step-2/5
    comments) + this doc's root_cause/fix — no more "lowers natively" (Finding A, cites
    CanLowerEfficiently.scala + LowerOrInterpretNonCompilable.scala, keeps version caveat); (3)
    ordering B elevated as leading candidate here + in WAVE-2-GATE-READINESS.md (Finding C), default
    code unchanged; (4) Finding D recorded as a LOW non-issue. The cluster experiment now decides
    A vs B on COMPLETION-TIME + SCRATCH, since the warning is no longer the signal.

## Resolution
<!-- OVERWRITE as understanding evolves -->

root_cause: |
  hl.ld_matrix(GT, locus, radius) builds a single fused lazy BlockMatrixIR:
  row_correlation(standardized genotypes) [G-center-normalize then G @ G.T] composed with the
  locus_windows radius banding (sparsify_row_intervals). Calling .write() on that IR is a
  BlockMatrixWrite.

  CORRECTED MECHANISM (adversarial review 2026-06-12, Finding A — verified against Hail source):
  The "BlockMatrixIR lowering not yet efficient/scalable" warning is NOT specific to this fused IR
  and is NOT eliminated by the fix. Hail 0.2.135's `CanLowerEfficiently.scala` fails on EVERY
  `BlockMatrixWrite` node UNCONDITIONALLY, so `LowerOrInterpretNonCompilable.scala` routes ALL
  BlockMatrix writes to `Interpret.alreadyLowered` (interpreted execution). The warning therefore
  fires on the OLD fused write, the fix's `.checkpoint()`, AND the fix's final write alike.

  The actual hang is NOT "the lowerer fails" — it is WHAT the interpreted writer has to do. When the
  write's input is an UN-MATERIALIZED matmul (the fused row_correlation @ G.T composed with the
  band), the interpreted writer drives the WHOLE matmul through a single driver-side
  ContextRDD.collect (BlockMatrix.scala:978 <- ContextRDD.scala:172) -> on a 122,678 x 122,678
  matrix (region m2_region_00006, span 17.7 Mb) it hangs 60+ min with no forward progress. This is
  structural to feeding an un-materialized matmul to the interpreted writer, not a data/OOM/kill
  bug, so it deterministically blocks all 36 large/xlarge A.3 regions. A.1/A.2 are unaffected
  because they call to_numpy() (a different, already-materializing collect path) on much smaller
  spans.

fix: |
  A.3-ONLY restructure (A.1/A.2 untouched, still use the existing `ld_bm = hl.ld_matrix(...)`).
  Replace the fused `hl.ld_matrix(...).write()` in the A.3 branch with hl.ld_matrix's OWN internal
  steps, inserting a checkpoint that breaks the fused IR:

    1. corr_bm = hl.row_correlation(mt_r.GT.n_alt_alleles())     # standardized Pearson-r Gram matrix
    2. corr_bm = corr_bm.checkpoint(scratch_uri)                  # MATERIALIZE the matmul to concrete
                                                                  #   on-disk blocks (this checkpoint is
                                                                  #   ITSELF an interpreted BlockMatrixWrite
                                                                  #   — warning fires here too — but it
                                                                  #   writes the dense matrix ONCE)
    3. starts, stops = hl.linalg.utils.locus_windows(mt_r.locus, radius=radius_bp)  # bp radius -> row-index band
    4. banded = corr_bm.sparsify_row_intervals(starts, stops, blocks_only=False)    # EXACT same band as ld_matrix
    5. banded.write(bm_uri, overwrite=True)                       # STILL interpreted (warning fires) but
                                                                  #   CHEAP: reads concrete blocks, not an
                                                                  #   un-materialized matmul -> no driver collect

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
  - ORDERING B (band-then-checkpoint) IS THE LEADING PRODUCTION-DEFAULT CANDIDATE (adversarial
    review 2026-06-12, Finding C). The earlier "B might re-introduce the hang because .checkpoint()
    is a write of the same fused IR" framing was OVER-CAUTIOUS and is CONTRADICTED by Pan-UKBB:
    atgu/ukbb_pan_ancestry `compute_ld_matrix.py` does exactly `(bm_Z @ bm_Z.T) ->
    _sparsify_row_intervals_expr -> sparsify_triangle -> checkpoint` — it bands FIRST and
    checkpoints the BANDED matrix, AT BIOBANK SCALE. So band-then-checkpoint is a PROVEN
    production pattern, and it avoids the CR-01 ~2 TB dense scratch (banded scratch is ~GB).
    IR-SHAPE CAVEAT (why we still do not flip the default in code yet): OLD's
    `hl.ld_matrix(...).write()` and ordering B's checkpoint are the SAME
    `BlockMatrixWrite(sparsify(matmul))` shape. Pan-UKBB suggests B completes, but our
    122,678^2 / ~710k^2 scales must be EMPIRICALLY confirmed on the cluster. Therefore: B is
    FAVORED and documented as the leading candidate, but the production default code stays A
    until the RE-GATED repro shows B COMPLETES within budget at the real scales. The repro now
    decides on completion-time + scratch footprint, NOT on the (always-present) lowering warning
    — see the re-gated experiment + CR-01 below.

verification: |
  PURE-PYTHON (run here, NCSU HPC — Hail not importable): regression tests for
    (a) _route_region_path unchanged (existing test_route_region_path_oom_veto still green),
    (b) new _a3_scratch_uri helper (path-isolated, deterministic, idempotent),
    (c) static-AST check that the A.3 branch now calls row_correlation + locus_windows +
        sparsify_row_intervals + checkpoint, and that A.1/A.2 still reference ld_matrix/to_numpy,
    (d) static-AST check that _assert_blockmatrix_written + sidecar emission still present after the write.
  CLUSTER (Carter runs; Hail-required, NOT runnable here): a3_blockmatrix_lowering_repro.py is a
    3-WAY ORDERING EXPERIMENT, RE-GATED on WALL-CLOCK COMPLETION (adversarial review Finding B). It
    builds a synthetic MT at a HANG-INDUCING n_var and runs OLD `hl.ld_matrix(...).write()`, ordering
    A (checkpoint dense correlation -> band -> write; current default), and ordering B (band ->
    checkpoint banded -> write; the Pan-UKBB pattern, leading candidate). For EACH it reports whether
    it COMPLETED within a per-ordering wall-time budget (`--budget-sec`), the scratch footprint (dense
    vs banded), .bm validity ((n,n)+_SUCCESS), and r-parity vs OLD. The lowering-warning grep is kept
    as INFORMATIONAL logging ONLY (it WILL appear on all BlockMatrix writes — CanLowerEfficiently —
    and is NOT a failure signal). A no-Hail `--report-scratch-size` mode extrapolates the
    dense-vs-banded scratch at REAL production n_var from config/ld_regions.tsv so a green small-n run
    cannot falsely clear GATE 3.
    DECISION RUBRIC (completion + scratch, NOT warning): OLD is the intractability CONTROL — at a
    large enough --n-var it must TIME OUT (if OLD COMPLETES, --n-var is too small and the run is
    VACUOUS — raise it). Pick the ordering that COMPLETES within budget + valid .bm + r-parity, with
    the smallest scratch. If both A and B complete -> ship B (Pan-UKBB-proven, banded ~GB vs A's ~TB
    dense). If only A completes -> A required and the ~2 TB worst case must fit cluster scratch
    capacity. THIS experiment is the completion PROOF + the GATE-3 ordering decision — the pure-Python
    tests cannot exercise Hail.
  PURE-PYTHON STATUS: PASS. `tests/m3/ -q` => 153 passed, 35 skipped (Hail-gated skips expected).
    5 pure-Python guards green: test_a3_scratch_uri_is_path_isolated_and_idempotent,
    test_a3_branch_uses_materialize_then_band_not_fused_write,
    test_a3_helper_does_not_call_fused_ld_matrix_write, test_dense_footprint_bytes_matches_n2_times_4,
    test_dense_footprint_helper_used_by_a3_write_for_observability. The existing OOM-veto routing test
    (test_route_region_path_oom_veto) still green (A.1/A.2 routing unchanged).
  CLUSTER STATUS: PENDING (Carter). scripts/a3_blockmatrix_lowering_repro.py is the lowering PROOF
    + the GATE-3 ordering decision (3-way experiment).
gate3_blocker: |
  CR-01 (review 2026-06-11; re-gated 2026-06-12): GATE-3 (322-cell production) is BLOCKED until the
  cluster ordering experiment (scripts/a3_blockmatrix_lowering_repro.py) picks an ordering that
  COMPLETES within the wall-time budget at a hang-inducing scale AND whose worst-case scratch fits
  cluster scratch capacity. (The discriminator is COMPLETION-TIME + SCRATCH, NOT the lowering
  warning — Finding B; the warning fires on all BlockMatrix writes.) The current default (ordering
  A) checkpoints the FULL DENSE n×n correlation (~2 TB worst case, m2_region_00145 ~710k var).
  Ordering B (band-before-checkpoint) is the Pan-UKBB-proven pattern and is FAVORED: it shrinks
  scratch to ~GB for mid-size A.3 regions. For the ~100 Mb xlarge regions the 50-Mb-capped radius
  bands ~98% of the row so banded ≈ dense (B saves little scratch THERE — its value is completion),
  but Pan-UKBB running band-then-checkpoint at biobank scale contradicts the earlier "B might
  re-hang" fear. dev-10 GATE-2 (one dev region, region_00006 ~60 GB scratch, ordering A) is
  TOLERABLE and may proceed on current code; the production 322-cell fire is NOT until CR-01 is
  resolved by the cluster experiment. See WAVE-2-GATE-READINESS.md.
files_changed:
  - src/python/aou_ld_panel.py (A.3-only: route-before-ld_bm so the fused ld_bm is built ONLY for A.1/A.2 [IN-01]; _dense_footprint_bytes helper [WR-02]; _write_a3_banded_correlation_bm logs n_var + dense footprint + loud WARN past 300 GiB before the checkpoint [WR-02]; A.1/A.2 + MED-4 guard + CR-003 sidecars behaviorally untouched; default ordering A UNCHANGED — the cluster decides A vs B)
  - tests/m3/test_aou_ld_panel_local.py (3 prior A.3 guards + 2 new: _dense_footprint_bytes unit test + static-AST that the A.3 helper logs the footprint)
  - scripts/a3_blockmatrix_lowering_repro.py (RESTRUCTURED into a 3-way OLD/A/B ordering experiment + no-Hail --report-scratch-size extrapolation + decision rubric; 2026-06-12 RE-GATED on wall-clock completion (Finding B): _run_with_budget helper + --budget-sec + default --n-var=50000 + warning downgraded to informational; B reframed as Pan-UKBB-proven candidate (Finding C); mechanism prose corrected (Finding A))
  - .planning/phases/m3-aou-afr-ld-panel-build/WAVE-2-GATE-READINESS.md (dev-10 GATE-2 may proceed on ordering A; GATE-3 BLOCKED on CR-01; 2026-06-12 ordering B elevated as Pan-UKBB-favored candidate, discriminator = completion-time not warning)
  - tests/m3/test_aou_ld_panel_local.py (2026-06-12: + _run_with_budget unit test for the re-gated completion discriminator)

## .continue-here / SUMMARY
<!-- What still needs the cluster before dev-10 GATE-2 resumes -->

WHAT LANDED (NCSU-side, original fix):
- A.3-only code fix in src/python/aou_ld_panel.py. The fused `hl.ld_matrix(...).write()` is replaced
  in BOTH A.3 sub-branches (local-test + bucket) by `_write_a3_banded_correlation_bm(...)`, which does
  row_correlation -> checkpoint(scratch) -> locus_windows(radius_bp) -> sparsify_row_intervals
  (blocks_only=False) -> write(stage_locally=True). Numerically identical to the old path.

WHAT LANDED (REMEDIATION, 2026-06-11 review pass):
- CR-01 corrected in this doc: ordering A checkpoints the FULL DENSE n×n correlation (~2 TB worst case),
  NOT a banded matrix.
- repro RESTRUCTURED into a 3-way OLD/A/B ordering experiment + a no-Hail --report-scratch-size mode
  (worst case m2_region_00145 ~1.8 TiB) + a decision rubric. WR-02 observability log + soft guard added.
  IN-01: ld_bm built only for A.1/A.2. New _dense_footprint_bytes helper + 2 unit tests.

WHAT LANDED (REMEDIATION, 2026-06-12 ADVERSARIAL review pass — Findings A/B/C/D accepted):
- FINDING A: mechanism prose corrected throughout (aou_ld_panel.py + this doc) — the lowering warning
  fires on ALL BlockMatrix writes (CanLowerEfficiently.scala); the fix is "interpreted-but-cheap-because-
  inputs-are-concrete," NOT "lowers natively." Version caveat kept.
- FINDING B: repro RE-GATED on WALL-CLOCK COMPLETION (the old `a_warning is False` gate was
  unsatisfiable). New _run_with_budget helper + --budget-sec + default --n-var=50000 (hang-inducing) +
  vacuity warning if OLD completes; warning grep downgraded to informational. +2 unit tests.
- FINDING C: ordering B (band-then-checkpoint) elevated to LEADING production-default candidate — it is
  the PROVEN Pan-UKBB pattern (atgu/ukbb_pan_ancestry compute_ld_matrix.py at biobank scale); the "B might
  re-hang" framing was over-cautious. Default code STAYS A pending the re-gated repro (IR-shape caveat:
  OLD and B share the BlockMatrixWrite(sparsify(matmul)) shape, so B's completion must be shown at scale).
- FINDING D (LOW, no code change): locus_windows _localize=True forces a ~5.7 MB driver collect for 710k
  vars — trivial; noted as a non-issue.
- Full m3 suite 155 passed / 35 skipped (153 + the 2 new completion-discriminator tests).

WHAT STILL REQUIRES THE CLUSTER:
1. dev-10 GATE-2 (TOLERABLE on current ordering A; ~60 GB scratch for region_00006): run the repro
   ordering experiment at a hang-inducing --n-var, then re-fire the previously-hanging A.3 cell
   (m2_region_00006). Verify at the data layer (gsutil du of the .bm/parts + _assert_blockmatrix_written
   shape) — _SUCCESS is NOT proof.
2. GATE-3 (322-cell production) is BLOCKED on CR-01: the cluster ordering experiment must pick the
   ordering that COMPLETES within the wall-time budget (NOT the always-present lowering warning) and
   whose worst-case scratch (~2 TB) fits cluster scratch capacity. Apply the re-gated decision rubric in
   the repro docstring; ordering B (Pan-UKBB-favored) is the expected pick — if selected, re-order
   _write_a3_banded_correlation_bm (band-before-checkpoint) and re-run --report-scratch-size before the
   production fire.

ONLY AFTER the cluster ordering experiment + the GATE-3 sizing decision is this session resolvable.
