#!/usr/bin/env python3
"""Cluster ordering EXPERIMENT for the m3-W2 Path-A.3 BlockMatrixIR-lowering hang.

WHAT THIS DECIDES (the cluster experiment GATE-3 depends on)
============================================================
`compute_region_ld`'s Path A.3 used to call `hl.ld_matrix(...).write(bm_uri)` on a single
FUSED lazy BlockMatrixIR (row_correlation of standardized genotypes composed with the
radius banding). The dev-10 GATE-2 failure on m2_region_00006 (122,678 variants): the write
HUNG 60+ minutes in a single driver-side `ContextRDD.collect` (BlockMatrix.scala:978).

THE WARNING IS NOT THE SIGNAL (adversarial review, Finding A/B — READ THIS)
--------------------------------------------------------------------------
Earlier versions of this experiment gated PASS on the ABSENCE of the
"BlockMatrixIR lowering not yet efficient/scalable" warning. THAT GATE WAS WRONG. Per Hail
source `CanLowerEfficiently.scala`, that warning fires UNCONDITIONALLY on EVERY
`BlockMatrixWrite` node — and `.checkpoint()` IS a `BlockMatrixWrite`. So the warning appears
on the OLD fused write, on the fix's checkpoint, AND on the fix's final write. Every
BlockMatrix write falls back to `Interpret.alreadyLowered` (interpreted execution) via
`LowerOrInterpretNonCompilable.scala`. The fix does NOT make the write "lower natively." Its
REAL mechanism is: materializing the matmul (the checkpoint) before sparsify+write makes the
final INTERPRETED write read CONCRETE on-disk blocks (cheap) instead of driving an
un-materialized matmul through the driver-side `ContextRDD.collect` that caused the OLD
path's intractable stall. So the warning is INFORMATIONAL ONLY here, never a failure signal.

THE REAL DISCRIMINATOR = WALL-CLOCK COMPLETION + SCRATCH FOOTPRINT
-----------------------------------------------------------------
This experiment decides between orderings on whether each one COMPLETES WITHIN A WALL-TIME
BUDGET at a hang-inducing scale, plus the scratch footprint it writes — NOT on the warning.
OLD is the intractability CONTROL: at a large enough --n-var it is expected to TIME OUT
(stall in the driver collect), confirming the experiment is non-vacuous. A and B are PASS if
they complete within budget, produce a valid `.bm`, and match OLD's r values (parity).

  (OLD) hl.ld_matrix(...).write()
        -> the fused, un-materialized matmul. EXPECT it to STALL / TIME OUT at a hang-inducing
           --n-var (this is the control). Skip it with --skip-old once you trust the control.

  (A) current production default — checkpoint the UN-BANDED correlation, THEN band:
        corr = hl.row_correlation(GT)
        corr = corr.checkpoint(scratch)          # scratch = FULL DENSE n x n (CR-01!)
        starts, stops = locus_windows(locus, radius)
        banded = corr.sparsify_row_intervals(starts, stops, blocks_only=False)
        banded.write(bm_uri)
     Scratch footprint = O(n_var^2) DENSE (~2 TB on the largest production region). The write
     is interpreted (warning present) but cheap because it reads the concrete checkpoint.

  (B) Pan-UKBB production pattern (review CR-01 / Finding C) — band FIRST, then checkpoint:
        corr = hl.row_correlation(GT)
        starts, stops = locus_windows(locus, radius)
        banded = corr.sparsify_row_intervals(starts, stops, blocks_only=False)
        banded = banded.checkpoint(scratch)      # scratch = BANDED (~GB not ~TB)
        banded.write(bm_uri)
     This is the PROVEN biobank-scale pattern: atgu/ukbb_pan_ancestry compute_ld_matrix.py
     does exactly `(bm_Z @ bm_Z.T) -> _sparsify_row_intervals_expr -> sparsify_triangle ->
     checkpoint` (bands FIRST, checkpoints the BANDED matrix). The earlier "B might re-hang
     because .checkpoint() is a write of the same fused IR" framing was OVER-CAUTIOUS and is
     contradicted by Pan-UKBB running this at scale. IR-SHAPE CAVEAT: OLD's
     `ld_matrix().write()` and B's checkpoint are the SAME `BlockMatrixWrite(sparsify(matmul))`
     shape, so this experiment must EMPIRICALLY show B completes — Pan-UKBB suggests yes, but
     our 122k^2 / 710k^2 scale must be confirmed on the cluster. B avoids the CR-01 ~2 TB
     dense scratch (banded scratch is ~GB), so B is the LEADING production-default candidate.

DECISION RUBRIC (apply to the cluster output)
=============================================
The discriminator is COMPLETION-WITHIN-BUDGET + SCRATCH SIZE, NOT the warning (the warning
appears on ALL BlockMatrix writes — see Finding A above).
  * OLD is expected to TIME OUT at a hang-inducing --n-var (the control proving the
    experiment is non-vacuous). If OLD COMPLETES, --n-var is too small -> the experiment
    proves nothing; raise --n-var until OLD stalls.
  * Pick the ordering that COMPLETES within --budget-sec AND produces a valid `.bm` AND
    matches OLD's r values, with the SMALLEST scratch footprint.
  * If both A and B complete -> ship B (Pan-UKBB-proven, banded scratch ~GB vs A's ~TB dense).
  * If only A completes -> A required; the ~2 TB worst-case dense scratch (m2_region_00145
    ~710k var) MUST be sized against cluster scratch/bucket capacity before GATE 3.
  * If neither completes -> escalate: a different decomposition (e.g. per-block write) needed.
A green run at synthetic n does NOT clear GATE 3 by itself — run --report-scratch-size against
config/ld_regions.tsv to see the dense-vs-banded footprint at the REAL production n_var, AND
run the ordering experiment at a --n-var large enough that OLD actually stalls.

CAVEAT the extrapolation surfaces: for the LARGEST regions (span ~100 Mb) the radius
(span+500kb, capped at 50 Mb) bands ~98% of each row, so ordering B's banded scratch ~
ordering A's dense scratch (~2 TB) — B saves little HERE. B's value for those regions is then
just completion-within-budget (does the band-then-checkpoint composition complete?), not the
footprint. If both A and B complete, neither escapes the ~2 TB worst case for those regions
and CLUSTER SCRATCH CAPACITY is the binding GATE-3 constraint regardless of ordering. B's
footprint win is real for regions whose radius is narrow relative to span (mid-size A.3).

HOW CARTER RUNS IT (on the Dataproc / Hail Workbench cluster, NOT the NCSU HPC node)
====================================================================================
1. echo $WORKSPACE_BUCKET    # gs://rw-migration-aou-rw-476cdac2 (or any writable gs:// for scratch)
2. Ordering experiment. --n-var MUST be large enough that OLD stalls (else the experiment is
   vacuous — see Finding B). The dev-10 hang was 122,678 variants; default --n-var is set so
   OLD is intractable. A per-ordering --budget-sec wall-time bounds each write:
       python scripts/a3_blockmatrix_lowering_repro.py \
           --out-bucket $WORKSPACE_BUCKET/ld/_a3_lowering_repro \
           --n-var 50000 --n-samples 2000 --radius-bp 1000000 --budget-sec 1200
   Optionally pin the log:  --hail-log /tmp/hail-<...>.log   (auto-discovers newest /tmp/hail*.log)
   To skip the (intentionally-stalling) OLD control once trusted:  --skip-old
3. Production scratch-size extrapolation (NO Hail / NO cluster needed — runs anywhere):
       python scripts/a3_blockmatrix_lowering_repro.py --report-scratch-size \
           --regions-tsv config/ld_regions.tsv
   Prints, per A.3 region (largest first), the DENSE (ordering A) vs estimated BANDED
   (ordering B) scratch footprint so the GATE-3 sizing decision is grounded in real n_var.

EXPECTED OUTPUT (PASS) for the ordering experiment:
       [OLD] completed=False (TIMED OUT at budget — the intractability control)
       [A]   completed=True within budget   scratch=DENSE   .bm (n,n) + _SUCCESS + parity ~ 0
       [B]   completed=True within budget   scratch=BANDED   .bm (n,n) + _SUCCESS + parity ~ 0
       (lowering warning is PRESENT on all three — INFORMATIONAL ONLY, never a failure signal)
       RESULT: reports each ordering; apply the DECISION RUBRIC (completion + scratch) above.

CLEANUP: writes only under --out-bucket/{old,A,B,scratch_*}; delete that prefix after the run.
"""
from __future__ import annotations

import argparse
import csv
import glob
import io
import logging
import os
import sys
import time

LOWERING_SIGNATURE = "BlockMatrixIR lowering not yet efficient"
PATH_A2_MAX_MB = 10.0  # mirrors aou_ld_panel._route_region_path OOM veto (A.3 routing)
RADIUS_HARD_CAP_BP = 50_000_000  # mirrors build_ld_region_manifest.RADIUS_HARD_CAP_BP (50 Mb)


def _newest_hail_log() -> str | None:
    candidates = sorted(glob.glob("/tmp/hail*.log"), key=os.path.getmtime, reverse=True)
    return candidates[0] if candidates else None


class _CaptureHandler(logging.Handler):
    """Capture Hail's Python-side log records into an in-memory buffer."""

    def __init__(self) -> None:
        super().__init__(level=logging.NOTSET)
        self.buf = io.StringIO()

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D401
        try:
            self.buf.write(self.format(record) + "\n")
        except Exception:  # noqa: BLE001
            pass


def _warning_seen(capture: _CaptureHandler, hail_log_path: str | None) -> bool:
    """True if the non-scalable-lowering warning appears in the captured buffer OR the on-disk log.

    INFORMATIONAL ONLY (adversarial review, Finding A). This warning is NOT a failure signal.
    Per Hail `CanLowerEfficiently.scala`, `BlockMatrixWrite` nodes are ALWAYS reported as
    not-efficiently-lowerable, so this string is expected on EVERY BlockMatrix write — the OLD
    fused write, the fix's `.checkpoint()` (itself a BlockMatrixWrite), AND the fix's final
    write. Its presence does NOT mean the path hangs and its absence is NOT the PASS criterion
    (see `run_experiment`, which gates on wall-clock completion). This helper exists only so the
    experiment can print whether the warning fired, for the record.
    """
    if LOWERING_SIGNATURE in capture.buf.getvalue():
        return True
    if hail_log_path and os.path.isfile(hail_log_path):
        try:
            with open(hail_log_path, "r", errors="replace") as fh:
                if LOWERING_SIGNATURE in fh.read():
                    return True
        except OSError:
            pass
    return False


def _run_with_budget(fn, budget_sec: float):
    """Run `fn()` in a worker thread, returning (completed, wall_seconds).

    The discriminator between orderings (Finding B): an ordering PASSES only if it COMPLETES
    within `budget_sec`. OLD is expected to TIME OUT (completed=False) at a hang-inducing
    --n-var — that is the intractability control proving the experiment is non-vacuous.

    Pure-Python (threading + time); no Hail. The worker thread is daemonic so a stalled Hail
    driver collect does not block process exit — the timed-out call keeps running server-side
    but we stop WAITING on it and report it as not-completed-within-budget. This is the
    "driver-collect-stall check": a write that has not returned within the budget is treated
    as the hang, exactly as the dev-10 60-min stall would be.
    """
    import threading

    result: dict = {"done": False, "error": None}

    def _target() -> None:
        try:
            fn()
            result["done"] = True
        except BaseException as exc:  # noqa: BLE001 -- surface any Hail/Spark error as not-done
            result["error"] = exc

    t = threading.Thread(target=_target, daemon=True)
    t0 = time.time()
    t.start()
    t.join(timeout=budget_sec)
    wall = time.time() - t0
    completed = result["done"] and not t.is_alive()
    return completed, wall, result["error"]


# --------------------------------------------------------------------------------------
# Scratch-size extrapolation (pure-Python; no Hail; runs on the NCSU node or the cluster)
# --------------------------------------------------------------------------------------

def _dense_footprint_bytes(n_var: int) -> int:
    """Bytes a full DENSE n_var x n_var float32 matrix occupies (ordering A's scratch).

    Mirrors aou_ld_panel._dense_footprint_bytes so the repro extrapolation and the
    production observability log agree. Kept local so this script needs no Hail import.
    """
    n = int(n_var)
    if n < 0:
        raise ValueError(f"n_var must be non-negative, got {n_var!r}")
    return n * n * 4


def _estimate_n_var(span_bp: int, density_per_mb: float) -> int:
    """Estimate n_var from a region span using an AFR variant density (var/Mb)."""
    return int(round((span_bp / 1_000_000.0) * density_per_mb))


def _banded_footprint_bytes(n_var: int, span_bp: int, radius_bp: int) -> int:
    """Estimate ordering-B BANDED scratch bytes.

    A radius-banded n x n matrix keeps, per row, ~ (2*radius / span) * n_var columns (the
    band half-width is the radius in bp mapped to a row-index window). Footprint ~
    n_var * band_width * 4 bytes, capped at the dense footprint when the band covers the
    whole region (2*radius >= span). This is an ORDER-OF-MAGNITUDE estimate for the GATE-3
    sizing decision, not an exact block count.
    """
    span_bp = max(1, int(span_bp))
    frac = min(1.0, (2.0 * radius_bp) / span_bp)
    band_cols = max(1, int(round(n_var * frac)))
    banded = n_var * band_cols * 4
    return min(banded, _dense_footprint_bytes(n_var))


def _fmt_bytes(b: float) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if b < 1024 or unit == "TiB":
            return f"{b:,.1f} {unit}"
        b /= 1024
    return f"{b:,.1f} TiB"


def report_scratch_size(regions_tsv: str, density_per_mb: float) -> int:
    """Print dense (ordering A) vs banded (ordering B) scratch footprint for A.3 regions.

    A region is routed to A.3 when region_class is large/xlarge OR span > PATH_A2_MAX_MB.
    n_var is estimated from span x density (no Hail). Largest-first so the worst case (the
    GATE-3 blocker, ~2 TB on m2_region_00145) is at the top.
    """
    rows = []
    with open(regions_tsv, newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for r in reader:
            try:
                start = int(r["start_grch38"])
                end = int(r["end_grch38"])
                radius_bp = int(r["radius_bp"])
            except (KeyError, ValueError):
                continue
            span_bp = max(0, end - start)
            span_mb = span_bp / 1_000_000.0
            region_class = (r.get("region_class") or "").strip().lower()
            is_a3 = region_class in ("large", "xlarge") or span_mb > PATH_A2_MAX_MB
            if not is_a3:
                continue
            # Production caps the radius at 50 Mb (build_ld_region_manifest.RADIUS_HARD_CAP_BP)
            # at hl.ld_matrix call time; the manifest radius_bp is uncapped (span+500kb). Apply
            # the cap here so ordering B's banded estimate reflects what production actually bands.
            eff_radius_bp = min(radius_bp, RADIUS_HARD_CAP_BP)
            n_var = _estimate_n_var(span_bp, density_per_mb)
            dense = _dense_footprint_bytes(n_var)
            banded = _banded_footprint_bytes(n_var, span_bp, eff_radius_bp)
            rows.append({
                "region_id": r.get("region_id", "?"),
                "ancestry": r.get("ancestry", "?"),
                "span_mb": span_mb,
                "n_var": n_var,
                "dense": dense,
                "banded": banded,
            })

    rows.sort(key=lambda x: x["dense"], reverse=True)
    print(f"\n==== A.3 scratch footprint extrapolation (density={density_per_mb:,.0f} var/Mb) ====")
    print(f"  routed to A.3 = region_class in (large,xlarge) OR span > {PATH_A2_MAX_MB} Mb")
    print(f"  n_var ESTIMATED from span x density; dense=ordering A (CR-01), banded=ordering B est.\n")
    print(f"  {'region_id':<18} {'anc':<4} {'span_Mb':>8} {'n_var(est)':>11} "
          f"{'dense(A)':>12} {'banded(B est)':>14}")
    for x in rows[:25]:
        print(f"  {x['region_id']:<18} {x['ancestry']:<4} {x['span_mb']:>8.1f} "
              f"{x['n_var']:>11,} {_fmt_bytes(x['dense']):>12} {_fmt_bytes(x['banded']):>14}")
    if rows:
        worst = rows[0]
        print(f"\n  WORST CASE (GATE-3 blocker): {worst['region_id']} ({worst['ancestry']}) "
              f"span {worst['span_mb']:.1f} Mb ~ {worst['n_var']:,} var -> "
              f"ordering A dense scratch ~ {_fmt_bytes(worst['dense'])} "
              f"vs ordering B banded ~ {_fmt_bytes(worst['banded'])}.")
        print("  DECISION RUBRIC: ship the ordering that COMPLETES within budget with the")
        print("  smallest scratch (the warning fires on ALL writes — it is NOT the signal).")
        print("  Pan-UKBB runs band-then-checkpoint (B) at biobank scale, so B is favored.")
        print("  If both A and B complete on the cluster -> ship B (banded ~GB vs A's ~TB dense).")
        print("  If only A completes -> A required; the dense worst-case above MUST fit cluster")
        print("  scratch capacity before GATE-3 (322-cell) production.")
        if worst["banded"] >= 0.9 * worst["dense"]:
            print("\n  NOTE: for the LARGEST regions banded ~ dense — the radius (span+500kb,")
            print("  capped at 50 Mb) covers nearly the whole row over a ~100 Mb span, so")
            print("  ordering B saves little scratch HERE. B's value is then just")
            print("  completion-within-budget, not the footprint: if A's dense materialization")
            print("  is the bottleneck and B completes, B still wins; if both complete, neither")
            print("  escapes the ~2 TB worst case and the cluster's scratch capacity is the")
            print("  binding GATE-3 constraint regardless of ordering.")
    else:
        print("  (no A.3 regions found in the manifest)")
    return 0


# --------------------------------------------------------------------------------------
# Hail ordering experiment (cluster only)
# --------------------------------------------------------------------------------------

def _build_synth_mt(hl, n_var: int, n_samples: int, radius_bp: int):
    """Tiny synthetic, locus-sorted MT on chr1 with a GT field, contiguous so the bp radius
    spans the whole region (banding == dense on this small case, matching ld_matrix)."""
    import random

    step = max(1, radius_bp // max(1, n_var) // 2)
    rows = []
    pos = 100_000
    random.seed(13)
    for _ in range(n_var):
        rows.append({"locus": hl.Locus("chr1", pos, reference_genome="GRCh38"),
                     "alleles": ["A", "C"]})
        pos += step
    mt = hl.utils.range_matrix_table(n_rows=n_var, n_cols=n_samples)
    loci = hl.literal([r["locus"] for r in rows])
    mt = mt.annotate_rows(locus=loci[mt.row_idx], alleles=["A", "C"])
    mt = mt.key_rows_by("locus", "alleles")
    mt = mt.annotate_entries(
        GT=hl.unphased_diploid_gt_index_call((mt.row_idx + mt.col_idx) % 3)
    )
    return mt


def _scratch_dir_size_bytes(hl, scratch_uri: str) -> int | None:
    """Best-effort total byte size of a scratch .bm directory (for the dense-vs-banded probe)."""
    try:
        total = 0
        for stat in hl.current_backend().fs.ls(scratch_uri):
            sz = getattr(stat, "size", None) or getattr(stat, "size_bytes", None)
            if sz:
                total += int(sz)
        return total
    except Exception:  # noqa: BLE001
        return None


def _run_ordering_A(hl, mt, radius_bp, bm_uri, scratch_uri):
    """Ordering A: checkpoint UN-banded correlation (dense scratch), then band, then write."""
    corr = hl.row_correlation(mt.GT.n_alt_alleles())
    corr = corr.checkpoint(scratch_uri, overwrite=True)
    starts, stops = hl.linalg.utils.locus_windows(mt.locus, radius=radius_bp)
    banded = corr.sparsify_row_intervals(starts=starts, stops=stops, blocks_only=False)
    banded.write(bm_uri, overwrite=True, stage_locally=True)


def _run_ordering_B(hl, mt, radius_bp, bm_uri, scratch_uri):
    """Ordering B: band FIRST, checkpoint the BANDED matrix, then write.

    This is the Pan-UKBB production pattern (atgu/ukbb_pan_ancestry compute_ld_matrix.py:
    matmul -> sparsify_row_intervals -> sparsify_triangle -> checkpoint), proven at biobank
    scale. Leading production-default candidate (Finding C); banded scratch ~GB vs A's ~TB.
    IR-shape caveat: this checkpoint is the SAME BlockMatrixWrite(sparsify(matmul)) shape as
    OLD's ld_matrix().write(), so the cluster must EMPIRICALLY confirm it completes within
    budget at our 122k/710k scale (Pan-UKBB suggests yes)."""
    corr = hl.row_correlation(mt.GT.n_alt_alleles())
    starts, stops = hl.linalg.utils.locus_windows(mt.locus, radius=radius_bp)
    banded = corr.sparsify_row_intervals(starts=starts, stops=stops, blocks_only=False)
    banded = banded.checkpoint(scratch_uri, overwrite=True)
    banded.write(bm_uri, overwrite=True, stage_locally=True)


def _phase(hl, label, fn, mt, radius_bp, bm_uri, scratch_uri, capture, hail_log, budget_sec):
    print(f"\n[{label}] running (budget {budget_sec:.0f}s)...")
    capture.buf = io.StringIO()
    completed, wall, error = _run_with_budget(
        lambda: fn(hl, mt, radius_bp, bm_uri, scratch_uri), budget_sec)
    warning = _warning_seen(capture, hail_log)
    scratch_bytes = _scratch_dir_size_bytes(hl, scratch_uri) if completed else None
    status = "COMPLETED" if completed else ("TIMED OUT" if error is None else f"ERROR: {error!r}")
    print(f"[{label}] {status} in {wall:.1f}s  (lowering-warning={warning} — INFORMATIONAL, "
          f"appears on ALL BlockMatrix writes per CanLowerEfficiently)  "
          f"scratch={_fmt_bytes(scratch_bytes) if scratch_bytes is not None else 'n/a'}")
    return completed, wall, scratch_bytes


def run_experiment(args) -> int:
    import hail as hl
    import numpy as np

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(repo_root, "src", "python"))

    hl.init()
    hail_log = args.hail_log or _newest_hail_log()
    print(f"[repro] Hail log: {hail_log}")

    capture = _CaptureHandler()
    logging.getLogger("hail").addHandler(capture)
    logging.getLogger().addHandler(capture)

    mt = _build_synth_mt(hl, args.n_var, args.n_samples, args.radius_bp)
    n = mt.count_rows()
    print(f"[repro] synthetic MT: {n} variants x {args.n_samples} samples; radius={args.radius_bp} bp")
    print(f"[repro] dense footprint at this n = {_fmt_bytes(_dense_footprint_bytes(n))} "
          f"(production worst case ~2 TB — run --report-scratch-size)")
    if n < 50_000:
        print(f"[repro] WARNING: n_var={n} may be too small for OLD to stall (Finding B vacuity "
              f"hole). The dev-10 hang was 122,678 variants; if OLD COMPLETES below, RAISE --n-var.")

    old_uri = f"{args.out_bucket}/old/repro_old.bm"
    a_uri = f"{args.out_bucket}/A/repro_A.bm"
    a_scratch = f"{args.out_bucket}/scratch_A/corr.bm"
    b_uri = f"{args.out_bucket}/B/repro_B.bm"
    b_scratch = f"{args.out_bucket}/scratch_B/corr.bm"

    print("\nNOTE (Finding A): the 'BlockMatrixIR lowering not yet efficient/scalable' warning")
    print("  fires on EVERY BlockMatrix write (CanLowerEfficiently.scala) — OLD, the checkpoint,")
    print("  AND the final write. It is INFORMATIONAL ONLY. PASS is decided on WALL-CLOCK")
    print(f"  COMPLETION within the {args.budget_sec:.0f}s budget, NOT on warning absence.\n")

    old_completed = None
    old_np = None
    if not args.skip_old:
        print("\n[OLD] hl.ld_matrix(...).write()  (fused un-materialized matmul -> the hang shape;")
        print(f"      EXPECT it to TIME OUT at this --n-var={args.n_var}. This is the control.)")
        capture.buf = io.StringIO()

        def _old_write():
            ld_bm = hl.ld_matrix(mt.GT.n_alt_alleles(), mt.locus, radius=args.radius_bp)
            ld_bm.write(old_uri, overwrite=True)

        old_completed, old_wall, old_err = _run_with_budget(_old_write, args.budget_sec)
        old_status = ("COMPLETED" if old_completed
                      else ("TIMED OUT" if old_err is None else f"ERROR: {old_err!r}"))
        print(f"[OLD] {old_status} in {old_wall:.1f}s "
              f"(lowering-warning={_warning_seen(capture, hail_log)} — informational)")
        if old_completed:
            old_np = hl.linalg.BlockMatrix.read(old_uri).to_numpy()

    a_completed, a_wall, a_scratch_bytes = _phase(
        hl, "A (dense-then-band, current default)", _run_ordering_A,
        mt, args.radius_bp, a_uri, a_scratch, capture, hail_log, args.budget_sec)
    b_completed, b_wall, b_scratch_bytes = _phase(
        hl, "B (band-then-checkpoint; Pan-UKBB production pattern)", _run_ordering_B,
        mt, args.radius_bp, b_uri, b_scratch, capture, hail_log, args.budget_sec)

    def _validate(label, uri, completed):
        if not completed:
            print(f"[{label}] not validated — did not complete within budget")
            return False
        bm = hl.linalg.BlockMatrix.read(uri)
        shape = tuple(bm.shape)
        success = uri.rstrip("/") + "/_SUCCESS"
        try:
            present = hl.current_backend().fs.exists(success)
        except Exception:  # noqa: BLE001
            present = os.path.isfile(success)
        parity = None
        if old_np is not None:
            parity = float(np.max(np.abs(old_np - bm.to_numpy())))
        print(f"[{label}] shape={shape} _SUCCESS={present} "
              f"parity max|Δr|={'n/a (OLD timed out — no reference)' if parity is None else f'{parity:.3e}'}")
        ok = shape == (n, n) and present and (parity is None or parity < 1e-5)
        return ok

    print("\n========== RESULT (discriminator = completion-within-budget + scratch) ==========")
    if not args.skip_old:
        print(f"[OLD] completed={old_completed}  (expect False — TIMED OUT — the intractability control)")
    print(f"[A]   completed={a_completed} in {a_wall:.1f}s  "
          f"scratch={_fmt_bytes(a_scratch_bytes) if a_scratch_bytes is not None else 'n/a'} (DENSE)")
    print(f"[B]   completed={b_completed} in {b_wall:.1f}s  "
          f"scratch={_fmt_bytes(b_scratch_bytes) if b_scratch_bytes is not None else 'n/a'} (BANDED)")
    a_ok = _validate("A", a_uri, a_completed)
    b_ok = _validate("B", b_uri, b_completed)

    # PASS = completes within budget AND valid .bm AND r-parity (Finding B). NOT warning-absence.
    a_clear = a_completed and a_ok
    b_clear = b_completed and b_ok

    print("\n---------- DECISION ----------")
    if not args.skip_old and old_completed:
        print("WARNING: the OLD fused write COMPLETED at this --n-var, so the experiment is")
        print(f"  VACUOUS (Finding B's vacuity hole): too-small n lets OLD finish and proves")
        print(f"  nothing about the hang. RAISE --n-var (current {args.n_var}) until OLD times out,")
        print("  then re-run. Do NOT trust A/B PASS until OLD is the failing control.\n")

    if a_clear and b_clear:
        print("BOTH A and B COMPLETE + valid -> per rubric, SHIP B (Pan-UKBB-proven, banded")
        print("  scratch ~GB vs A's ~TB dense). Re-order _write_a3_banded_correlation_bm to")
        print("  band-before-checkpoint, then re-run --report-scratch-size to confirm the banded")
        print("  worst-case fits cluster capacity.")
    elif a_clear and not b_clear:
        print("ONLY A completes -> A is REQUIRED (B did not complete within budget at this scale).")
        print("  GATE-3 BLOCKED until the ~2 TB dense worst-case (see --report-scratch-size)")
        print("  is sized against cluster scratch capacity. Keep ordering A.")
    elif b_clear and not a_clear:
        print("ONLY B completes -> ship B (the Pan-UKBB pattern); A's dense materialization is")
        print("  the bottleneck at this scale. Verify banded scratch capacity, then re-order.")
    else:
        print("NEITHER A nor B completes within budget -> ESCALATE. Neither checkpoint placement")
        print("  makes the interpreted write tractable at this scale; a different decomposition")
        print("  (e.g. per-block write) is needed before GATE-3. Confirm --budget-sec is realistic.")

    return 0 if (a_clear or b_clear) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-bucket",
                    help="gs:// (or local dir) prefix for old/A/B/scratch_* .bm outputs "
                         "(required for the ordering experiment; not needed for --report-scratch-size)")
    # Finding B: --n-var must be large enough that the OLD fused write is intractable within
    # the budget, else the experiment is VACUOUS (OLD completes -> proves nothing about the
    # hang). The dev-10 hang was 122,678 variants; default to a scale where OLD stalls. Lower
    # it only for a quick smoke (and then OLD completing is EXPECTED and the run is vacuous).
    ap.add_argument("--n-var", type=int, default=50_000,
                    help="synthetic variant count. MUST be large enough that OLD times out "
                         "(default 50000; dev-10 hang was 122,678). Too small => vacuous run.")
    ap.add_argument("--n-samples", type=int, default=2_000)
    ap.add_argument("--radius-bp", type=int, default=1_000_000)
    ap.add_argument("--budget-sec", type=float, default=1_200.0,
                    help="per-ordering wall-time budget (s). An ordering PASSES only if it "
                         "COMPLETES within this budget; OLD is expected to TIME OUT (the "
                         "intractability control). Default 1200s (20 min).")
    ap.add_argument("--hail-log", default=None,
                    help="path to the active Hail driver log (auto-discovers newest /tmp/hail*.log)")
    ap.add_argument("--skip-old", action="store_true",
                    help="skip the OLD fused-write control (it is expected to stall — skip once "
                         "you trust it as the intractability control to save wall time)")
    ap.add_argument("--report-scratch-size", action="store_true",
                    help="NO-HAIL mode: print dense(A) vs banded(B) scratch footprint per A.3 "
                         "region from --regions-tsv so a small-n run cannot falsely clear GATE 3")
    ap.add_argument("--regions-tsv", default="config/ld_regions.tsv",
                    help="region manifest for --report-scratch-size")
    ap.add_argument("--density-per-mb", type=float, default=6930.0,
                    help="AFR variant density (var/Mb) for n_var estimation "
                         "(default 6930 ~ region_00006: 122,678 var / 17.7 Mb)")
    args = ap.parse_args()

    if args.report_scratch_size:
        return report_scratch_size(args.regions_tsv, args.density_per_mb)

    if not args.out_bucket:
        ap.error("--out-bucket is required for the ordering experiment "
                 "(or pass --report-scratch-size for the no-Hail footprint report)")
    return run_experiment(args)


if __name__ == "__main__":
    raise SystemExit(main())
