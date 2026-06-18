# DRAFT — Ordering B: band-before-checkpoint for `_write_a3_banded_correlation_bm`

> ## ⛔ NOT LANDED — RETIRED 2026-06-18 (quick `260618-3at`)
>
> **Decision: KEEP ordering A. Do NOT apply this draft.** The cluster ordering experiment ran
> (16-worker resize of cluster `20260617`, `--skip-old --n-var 130000 --budget-sec 3600`):
> **both A and B COMPLETED** (A 928.0 s, B 863.5 s; B is hang-free — the `sparsify→checkpoint`
> IR-shape did NOT reproduce the OLD driver-collect hang). So B's *technical* landing gate was met.
>
> **But the premise below ("What B buys") is FALSE for this manifest.** `--report-scratch-size`
> on the real `config/ld_regions.tsv` shows **`banded(B) == dense(A)` for ALL 23 A.3 regions**,
> not just the worst — because the manifest sets `radius = span+500kb` (capped 50 Mb), which is
> always ≥ span/2, so the band covers ~the whole region everywhere. **Ordering B saves scratch
> NOWHERE under this radius scheme.** It is byte-identical numerics with **zero** benefit and
> nonzero change-risk, so we keep the already-deployed, now-cluster-validated ordering A.
>
> **CR-01 is ordering-independent:** region_00145 (~710k var) needs ~1.8 TiB of (transient GCS)
> scratch under A *or* B. The real GATE-3 question is the xlarge dense-materialize **compute cost
> vs region-splitting**, not checkpoint ordering. See WAVE-2-GATE-READINESS.md + the debug session.
>
> **Revisit this draft ONLY if** a future manifest adopts `radius ≪ span` (e.g. a small fixed LD
> radius over a large region) — then B's banded scratch would genuinely beat A's dense, and the
> ready-to-apply patch below (verified non-vacuous) becomes worth landing.

**Original status (HISTORICAL — superseded by the banner above):** staged draft, gated on the cluster repro. **DO NOT APPLY** until BOTH:
1. The `scripts/a3_blockmatrix_lowering_repro.py` run shows **ordering B COMPLETES within `--budget-sec`** at production scale (≥122k var) — i.e. B's `checkpoint(sparsify(row_correlation))` does NOT hit the OLD fused-write driver-collect hang; AND
2. Carter gives an explicit go.

**Why gated:** ordering B's checkpoint writes `sparsify_row_intervals(hl.row_correlation(...))` — the SAME `BlockMatrixWrite(sparsify(matmul))` IR shape as the OLD `hl.ld_matrix(...).write()` that hung dev-10 region_00006. Pan-UKBB (`atgu/ukbb_pan_ancestry/compute_ld_matrix.py`) runs this pattern at biobank scale, so it is *expected* to complete — but that must be shown empirically before flipping the production default off ordering A. (Do-not list, HANDOFF.json.)

**What B buys:** the checkpoint materializes the radius-**banded** matrix (`blocks_only=False` prunes fully out-of-band blocks), so scratch is `O(n_var · band_width)` ≈ GB instead of ordering A's dense `O(n_var²)` ≈ **~2 TB** worst case (m2_region_00145). This is the **CR-01 resolution** and unblocks GATE-3.

**Numerics:** byte-identical to ordering A and to `hl.ld_matrix(...)`. Both orderings compose the exact same three ops (`row_correlation` → `locus_windows`/`sparsify_row_intervals(blocks_only=False)` → write); only the `checkpoint` position moves (after the band instead of before it). The repro's `_validate()` cross-checks A and B outputs against the OLD `to_numpy()` when OLD completes.

---

## Change 1 — replace the helper body (`src/python/aou_ld_panel.py`, lines ~2477–2568)

Keep the signature, `_a3_scratch_uri`, the n_var observability call, and the cleanup. Only the op order + the docstring/log framing change.

```python
def _write_a3_banded_correlation_bm(mt_r: "hl.MatrixTable", radius_bp: int,
                                    bm_uri: str, *, stage_locally: bool = True,
                                    n_var: "int | None" = None) -> None:
    """Write a Path-A.3 radius-banded Pearson-r BlockMatrix WITHOUT the fused-IR hang.

    Numerically identical to ``hl.ld_matrix(mt_r.GT.n_alt_alleles(), mt_r.locus,
    radius=radius_bp).write(bm_uri)`` — it reproduces ld_matrix's OWN documented internals
    (``row_correlation`` of standardized genotypes, then ``sparsify_row_intervals`` banded
    by ``locus_windows``) but inserts a ``checkpoint`` between the BANDING and the final
    write (ORDERING B: band-then-checkpoint).

    ORDERING (m3-W2 A.3 cluster repro decision, CR-01 resolution): the band
    (``sparsify_row_intervals``) is applied to the LAZY correlation BEFORE the checkpoint, so
    the checkpoint MATERIALIZES the radius-BANDED matrix (``O(n_var * band_width)`` ~ GB) and
    NOT the full dense ``O(n_var^2)`` correlation (~2 TB worst case). This is the Pan-UKBB
    production pattern (atgu/ukbb_pan_ancestry compute_ld_matrix.py: matmul ->
    sparsify_row_intervals -> sparsify_triangle -> checkpoint) and resolves CR-01 (the dense
    ~2 TB scratch that blocked GATE-3 under the prior ordering A). The ordering was chosen
    EMPIRICALLY by scripts/a3_blockmatrix_lowering_repro.py (decision = COMPLETES within
    --budget-sec with the smaller scratch; the lowering warning is NOT the signal — it fires
    on every BlockMatrix write). test_a3_band_before_checkpoint_ordering locks it in.

    MECHANISM (adversarial review, Finding A — NOT "lowers natively"):
      Every ``BlockMatrixWrite`` is INTERPRETED in Hail 0.2.135 — ``CanLowerEfficiently.scala``
      reports all BlockMatrix writes as not-efficiently-lowerable, so the
      "BlockMatrixIR lowering not yet efficient/scalable" warning fires on the OLD fused
      write, on the ``checkpoint`` below (a BlockMatrixWrite), AND on the final write. The
      checkpoint does NOT make anything "lower to the native distributed writer." What it
      DOES: it MATERIALIZES the (now banded) matmul to concrete on-disk blocks once, so the
      final (still-interpreted) write reads CONCRETE blocks instead of driving an
      un-materialized matmul through the driver-side ``ContextRDD.collect``
      (BlockMatrix.scala:978) that caused the OLD path's intractable 60+ min stall.
      IR-SHAPE CAVEAT (why this ordering is repro-gated): the checkpoint below writes
      ``sparsify_row_intervals(row_correlation(...))`` — the SAME BlockMatrixWrite(sparsify(
      matmul)) shape as the OLD ld_matrix().write(). It is safe to materialize here ONLY
      because the cluster repro showed it completes within budget at >=122k-var scale (the
      band prunes out-of-band blocks so the driver collect is bounded by the banded, not the
      dense, block count). If a future Hail version regresses this, the repro re-run is the
      gate.

    Why this is exactly ld_matrix and NOT a hand-rolled covariance:
      - ``hl.row_correlation(entry_expr)`` IS ld_matrix's standardization step: it
        mean-imputes missing genotypes WITHIN variant, centers + unit-normalizes each row,
        then computes the Gram matrix => Pearson **r** (not raw covariance). We call it
        directly, so there is zero standardization-drift risk.
      - ``hl.linalg.utils.locus_windows(locus_expr, radius)`` maps the BASE-PAIR radius to
        the SAME row-index windows ld_matrix uses (the loci are sorted, so a bp window is a
        contiguous row-index interval). ``sparsify_row_intervals(..., blocks_only=False)``
        keeps the EXACT in-band r values (blocks_only=True would zero whole off-band blocks
        but admit extra in-block entries — wrong for an LD reference panel consumed by
        SuSiE-RSS; we want byte-equivalent banding to the old path).

    See .planning/debug/m3-W2-a3-blockmatrix-write-ir-lowering-hang.md for the full
    root-cause + tradeoff record. ``stage_locally=True`` reduces the distributed-write
    network bottleneck (per the Hail BlockMatrix docs).
    """
    import hail as hl

    scratch_uri = _a3_scratch_uri(bm_uri)
    # WR-02 (m3-W2 A.3 review): surface the scratch cost. Under ORDERING B the checkpoint
    # holds the radius-BANDED matrix, so the actual scratch is <= the dense upper bound below
    # (O(n_var * band_width), ~GB for typical A.3 regions). _dense_footprint_bytes is logged as
    # the UN-BANDED UPPER BOUND for continuity with --report-scratch-size; for the largest
    # regions (radius span+500kb capped at 50 Mb over a ~100 Mb span) the band covers nearly the
    # whole row so banded ~ dense and the cluster scratch-capacity check still governs GATE-3.
    if n_var is None:
        try:
            n_var = mt_r.count_rows()
        except Exception:  # noqa: BLE001 -- count is best-effort for the log only
            n_var = None
    if n_var is not None:
        dense_bytes = _dense_footprint_bytes(n_var)
        dense_gib = dense_bytes / 1024 ** 3
        print(f"[compute_region_ld] A.3 scratch (ordering B, banded checkpoint): n_var={n_var:,}"
              f" -> checkpointing the RADIUS-BANDED correlation (actual <= the un-banded upper "
              f"bound {dense_gib:,.1f} GiB float32 = {dense_bytes:,} bytes) to {scratch_uri}. "
              f"The band is applied BEFORE this checkpoint (CR-01 resolution), so the scratch is "
              f"banded (O(n_var * band_width)), not dense.")
        if dense_bytes > A3_DENSE_SCRATCH_WARN_BYTES:
            print(f"[compute_region_ld] NOTE A.3 un-banded upper bound {dense_gib:,.1f} GiB "
                  f"exceeds the {A3_DENSE_SCRATCH_WARN_BYTES / 1024 ** 3:,.0f} GiB soft "
                  f"threshold (m3-W2 WR-02). Under ordering B the materialized scratch is the "
                  f"BANDED subset (typically ~GB); for the very largest regions the band still "
                  f"covers most of the span, so confirm the banded footprint fits cluster scratch "
                  f"capacity before GATE-3 (run scripts/a3_blockmatrix_lowering_repro.py "
                  f"--report-scratch-size). See WAVE-2-GATE-READINESS.md / debug session.")
    # 1. Standardized Pearson-r correlation matrix (ld_matrix's own first step) — LAZY.
    corr_bm = hl.row_correlation(mt_r.GT.n_alt_alleles())
    # 2. bp radius -> row-index band (identical mapping to ld_matrix).
    starts, stops = hl.linalg.utils.locus_windows(mt_r.locus, radius=radius_bp)
    # 3. ORDERING B: apply the EXACT same band as ld_matrix to the LAZY correlation FIRST
    #    (blocks_only=False = exact in-band r values; prunes fully out-of-band blocks).
    banded = corr_bm.sparsify_row_intervals(
        starts=starts, stops=stops, blocks_only=False,
    )
    # 4. MATERIALIZE the BANDED matrix to scratch (CR-01: banded ~GB, not dense ~2 TB). This
    #    checkpoint is ITSELF an interpreted BlockMatrixWrite (warning fires) sharing the OLD
    #    fused-write IR shape, but it is bounded by the BANDED block count and was shown to
    #    complete within budget by the cluster repro. The final write below then reads CONCRETE
    #    blocks instead of driving an un-materialized matmul through the driver ContextRDD.collect.
    banded = banded.checkpoint(scratch_uri, overwrite=True)
    # 5. Final write is STILL interpreted (warning fires) but CHEAP: its input is the concrete
    #    checkpointed banded matrix, not the un-materialized matmul. No driver-bound full collect.
    banded.write(bm_uri, overwrite=True, stage_locally=stage_locally)
    # 6. Best-effort scratch cleanup (survival is harmless: overwrite=True on any re-fire).
    try:
        hl.current_backend().fs.rmtree(scratch_uri)
    except Exception as e:  # noqa: BLE001 -- cleanup is best-effort, never fatal
        print(f"[compute_region_ld] A.3 scratch cleanup skipped for {scratch_uri}: {e}")
```

---

## Change 2 — add an ordering-lock regression test (`tests/m3/test_aou_ld_panel_local.py`)

Locks band-BEFORE-checkpoint so a future edit can't silently revert to ordering A (dense scratch / CR-01 regression). Pure-Python AST, runs on the NCSU node.

```python
def test_a3_band_before_checkpoint_ordering():
    """ORDERING LOCK (m3-W2 A.3 cluster repro, CR-01 resolution): the helper must apply the
    radius band (sparsify_row_intervals) BEFORE the checkpoint, so the materialized scratch is
    the banded matrix (~GB) and NOT the dense O(n_var^2) correlation (~2 TB). A regression to
    band-AFTER-checkpoint (ordering A) re-opens CR-01 / GATE-3. Pure-Python (no Hail)."""
    import ast, inspect
    from aou_ld_panel import _write_a3_banded_correlation_bm
    src = inspect.getsource(_write_a3_banded_correlation_bm)
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_write_a3_banded_correlation_bm")
    # First .sparsify_row_intervals(...) call must lexically precede the .checkpoint(...) that
    # writes scratch_uri. Use call-attribute line numbers of the executable body.
    sparsify_lines = [n.lineno for n in ast.walk(fn)
                      if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                      and n.func.attr == "sparsify_row_intervals"]
    checkpoint_lines = [n.lineno for n in ast.walk(fn)
                        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                        and n.func.attr == "checkpoint"]
    assert sparsify_lines, "helper must band via sparsify_row_intervals"
    assert checkpoint_lines, "helper must checkpoint the banded BM"
    assert min(sparsify_lines) < min(checkpoint_lines), (
        "ORDERING B regression: sparsify_row_intervals (band) must come BEFORE checkpoint "
        "(materialize) — band-after-checkpoint is ordering A and re-opens CR-01 / GATE-3."
    )
```

**Existing tests that stay GREEN unchanged** (verified against their assertions — all check op *presence*, not order):
- `test_a3_branch_uses_materialize_then_band_not_fused_write` — `row_correlation` / `sparsify_row_intervals` / `checkpoint` all still present.
- `test_a3_helper_does_not_call_fused_ld_matrix_write` — helper still avoids `ld_matrix`; same three ops present.
- `test_a3_scratch_uri_is_path_isolated_and_idempotent` — scratch URI unchanged.
- `test_dense_footprint_bytes_matches_n2_times_4` — `_dense_footprint_bytes` math unchanged (kept as upper bound).
- `test_dense_footprint_helper_used_by_a3_write_for_observability` — helper still CALLS `_dense_footprint_bytes` in the WR-02 log.

> Optional follow-up (not required to land B): the WR-02 log now labels dense as an *upper bound*. If we later want the log to report the true banded estimate, port the repro's `_banded_footprint_bytes(n_var, span_bp, radius_bp)` into `aou_ld_panel.py` and pass span — but that needs span threaded into the helper, so defer unless reviewers ask.

---

## Change 3 — doc/comment touchpoints to flip from "ordering A / CR-01 open" to "ordering B / CR-01 resolved"

Land these in the SAME commit so the record is consistent:
- `src/python/aou_ld_panel.py` ~line 2217 call-site comment: `(row_correlation -> checkpoint -> band -> write)` → `(row_correlation -> band -> checkpoint -> write)`.
- `src/python/aou_ld_panel.py` `_a3_scratch_uri` docstring (~2459–2464): the "materializes the (un-banded) correlation ... FIRST, then ... applies the radius band" sentence describes ordering A — update to band-then-checkpoint.
- `src/python/aou_ld_panel.py` `_dense_footprint_bytes` docstring (~2433): "footprint of ordering A's checkpointed scratch" → note ordering B checkpoints the banded subset; this stays the dense upper bound.
- `.planning/WAVE-2-GATE-READINESS.md`: CR-01 → RESOLVED (cite repro completion times + scratch sizes).
- `.planning/debug/m3-W2-a3-blockmatrix-write-ir-lowering-hang.md` (+ `-REVIEW.md`): record the experiment outcome + ordering-B decision; move the session toward resolved.
- `tests/m3/test_aou_ld_panel_local.py` comment block ~2546 (`row_correlation -> checkpoint -> sparsify_row_intervals band -> write`) → reorder to match B.

## Apply procedure (on Carter's go, after B wins)
1. `/gsd-quick` (or extend the open debug session) — atomic commit, explicit paths only (no `git add -A` on GPFS).
2. Apply Change 1 + 2 + 3.
3. `tests/m3` must stay green (155 passed + the new ordering-lock test = 156) — run on NCSU node.
4. Then re-fire dev-10 region_00006: verify the `.bm` at the DATA LAYER (`_assert_blockmatrix_written` + `gsutil du` of `.bm/parts`), never `_SUCCESS`.
5. Re-run `--report-scratch-size` to record the production banded footprint for the GATE-3 sizing memo.

## If B LOSES (only A completes, or B hits the same hang)
Do NOT apply this draft. Keep ordering A. CR-01 stays open and GATE-3 is blocked on fitting the ~2 TB dense worst case to cluster scratch capacity (or a per-block streaming write) — a separate design task. The repro's `_validate()` + `--report-scratch-size` output is the evidence for that branch.
