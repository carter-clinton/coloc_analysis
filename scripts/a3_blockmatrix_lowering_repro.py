#!/usr/bin/env python3
"""Cluster ordering EXPERIMENT for the m3-W2 Path-A.3 BlockMatrixIR-lowering hang.

WHAT THIS DECIDES (the cluster experiment GATE-3 depends on)
============================================================
`compute_region_ld`'s Path A.3 used to call `hl.ld_matrix(...).write(bm_uri)` on a single
FUSED lazy BlockMatrixIR (row_correlation of standardized genotypes composed with the
radius banding). Hail 0.2.135 cannot lower that fused IR scalably, so it falls back to the
INTERPRETED, driver-mediated `BlockMatrixWrite` -> a single driver-side `ContextRDD.collect`
that HANGS for 60+ minutes (the dev-10 GATE-2 failure on m2_region_00006: 122,678 variants).

The fix inserts a `checkpoint` that materializes a BlockMatrix to disk via the native
distributed writer, breaking the fused IR. BUT there are TWO places the checkpoint can sit,
and they have RADICALLY different scratch footprints AND an empirically-unknown lowering
behavior. This script runs BOTH orderings (plus the OLD fused path) so the CLUSTER decides
which to ship — it MUST NOT be decided on paper:

  (OLD) hl.ld_matrix(...).write()
        -> the fused IR. EXPECT the "BlockMatrixIR lowering not yet efficient" warning
           PRESENT (this is the hang shape). Reference for r-parity.

  (A) current production default — checkpoint the UN-BANDED correlation, THEN band:
        corr = hl.row_correlation(GT)
        corr = corr.checkpoint(scratch)          # scratch = FULL DENSE n x n (CR-01!)
        starts, stops = locus_windows(locus, radius)
        banded = corr.sparsify_row_intervals(starts, stops, blocks_only=False)
        banded.write(bm_uri)
     Scratch footprint = O(n_var^2) DENSE (~2 TB on the largest production region).
     Lowering: row_correlation ALONE is checkpointed (no band fused into the write of the
     scratch) — HYPOTHESIS: this lowers (warning ABSENT). This is what the repro must confirm.

  (B) proposed (review CR-01 fix) — band FIRST, then checkpoint the BANDED matrix:
        corr = hl.row_correlation(GT)
        starts, stops = locus_windows(locus, radius)
        banded = corr.sparsify_row_intervals(starts, stops, blocks_only=False)
        banded = banded.checkpoint(scratch)      # scratch = BANDED (much smaller for xlarge)
        banded.write(bm_uri)
     Scratch footprint = banded (radius-capped) — dramatically smaller for xlarge regions.
     Lowering: the checkpoint now materializes the row_correlation -> sparsify_row_intervals
     COMPOSITION. That is the SAME fused (correlation+band) IR shape that originally hung as
     `ld_matrix().write()`. .checkpoint() IS a write, so ordering B MIGHT RE-INTRODUCE THE
     HANG. WHICH ORDERING ACTUALLY LOWERS IS UNKNOWN WITHOUT THIS CLUSTER RUN.

DECISION RUBRIC (apply to the cluster output)
=============================================
Pick the ordering whose lowering warning is ABSENT with the SMALLEST scratch footprint:
  * If BOTH A and B are warning-free  -> prefer B (banded scratch; ~GB not ~TB).
  * If only A is warning-free         -> A is REQUIRED; the ~2 TB worst-case dense scratch
                                         (m2_region_00145 ~710k var) MUST be sized against
                                         the cluster scratch/bucket capacity before GATE 3.
  * If neither A nor B is warning-free -> escalate: the checkpoint is not breaking the fusion;
                                         a different decomposition (e.g. per-block write) is needed.
A green run at synthetic n does NOT clear GATE 3 by itself — run --report-scratch-size against
config/ld_regions.tsv to see the dense-vs-banded footprint at the REAL production n_var.

CAVEAT the extrapolation surfaces: for the LARGEST regions (span ~100 Mb) the radius
(span+500kb, capped at 50 Mb) bands ~98% of each row, so ordering B's banded scratch ~
ordering A's dense scratch (~2 TB) — B saves little HERE. B's value for those regions is the
LOWERING behavior (does the band-then-checkpoint composition lower?), not the footprint. If
both A and B lower, neither escapes the ~2 TB worst case and CLUSTER SCRATCH CAPACITY is the
binding GATE-3 constraint regardless of ordering. B's footprint win is real only for regions
whose radius is narrow relative to span (mid-size A.3 regions).

HOW CARTER RUNS IT (on the Dataproc / Hail Workbench cluster, NOT the NCSU HPC node)
====================================================================================
1. echo $WORKSPACE_BUCKET    # gs://rw-migration-aou-rw-476cdac2 (or any writable gs:// for scratch)
2. Ordering experiment (small synthetic MT — seconds of cluster compute):
       python scripts/a3_blockmatrix_lowering_repro.py \
           --out-bucket $WORKSPACE_BUCKET/ld/_a3_lowering_repro \
           --n-var 400 --n-samples 300 --radius-bp 1000000
   Optionally pin the log:  --hail-log /tmp/hail-<...>.log   (auto-discovers newest /tmp/hail*.log)
   To skip the (possibly hanging) OLD path:  --skip-old
3. Production scratch-size extrapolation (NO Hail / NO cluster needed — runs anywhere):
       python scripts/a3_blockmatrix_lowering_repro.py --report-scratch-size \
           --regions-tsv config/ld_regions.tsv
   Prints, per A.3 region (largest first), the DENSE (ordering A) vs estimated BANDED
   (ordering B) scratch footprint so the GATE-3 sizing decision is grounded in real n_var.

EXPECTED OUTPUT (PASS) for the ordering experiment:
       [OLD] lowering warning present : True
       [A]   lowering warning present : False     scratch=DENSE
       [B]   lowering warning present : <DECIDES — the whole point>   scratch=BANDED
       [A]   .bm shape (n,n) + _SUCCESS + parity vs OLD max|Δr| ~ 0
       [B]   .bm shape (n,n) + _SUCCESS + parity vs OLD max|Δr| ~ 0
       RESULT: reports each ordering; apply the DECISION RUBRIC above to pick the GATE-3 default.

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
    """True if the non-scalable-lowering warning appears in the captured buffer OR the on-disk log."""
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
        print("  DECISION RUBRIC: ship the warning-free ordering with the smallest scratch.")
        print("  If both A and B are warning-free on the cluster -> ship B (banded).")
        print("  If only A is warning-free -> A required; the dense worst-case above MUST fit")
        print("  cluster scratch capacity before GATE-3 (322-cell) production.")
        if worst["banded"] >= 0.9 * worst["dense"]:
            print("\n  NOTE: for the LARGEST regions banded ~ dense — the radius (span+500kb,")
            print("  capped at 50 Mb) covers nearly the whole row over a ~100 Mb span, so")
            print("  ordering B saves little scratch HERE. B's value is then the LOWERING")
            print("  behavior, not the footprint: if A re-hangs and B lowers, B still wins;")
            print("  if both lower, neither escapes the ~2 TB worst case and the cluster's")
            print("  scratch capacity is the binding GATE-3 constraint regardless of ordering.")
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
    """Ordering B: band FIRST, checkpoint the BANDED matrix, then write. MIGHT re-hang."""
    corr = hl.row_correlation(mt.GT.n_alt_alleles())
    starts, stops = hl.linalg.utils.locus_windows(mt.locus, radius=radius_bp)
    banded = corr.sparsify_row_intervals(starts=starts, stops=stops, blocks_only=False)
    banded = banded.checkpoint(scratch_uri, overwrite=True)
    banded.write(bm_uri, overwrite=True, stage_locally=True)


def _phase(hl, label, fn, mt, radius_bp, bm_uri, scratch_uri, capture, hail_log):
    print(f"\n[{label}] running...")
    capture.buf = io.StringIO()
    t0 = time.time()
    fn(hl, mt, radius_bp, bm_uri, scratch_uri)
    wall = time.time() - t0
    warning = _warning_seen(capture, hail_log)
    scratch_bytes = _scratch_dir_size_bytes(hl, scratch_uri)
    print(f"[{label}] write wall: {wall:.1f}s  lowering-warning={warning}  "
          f"scratch={_fmt_bytes(scratch_bytes) if scratch_bytes is not None else 'n/a'}")
    return warning, scratch_bytes


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

    old_uri = f"{args.out_bucket}/old/repro_old.bm"
    a_uri = f"{args.out_bucket}/A/repro_A.bm"
    a_scratch = f"{args.out_bucket}/scratch_A/corr.bm"
    b_uri = f"{args.out_bucket}/B/repro_B.bm"
    b_scratch = f"{args.out_bucket}/scratch_B/corr.bm"

    old_warning = None
    old_np = None
    if not args.skip_old:
        print("\n[OLD] hl.ld_matrix(...).write()  (fused IR -> expect lowering warning + slow)")
        capture.buf = io.StringIO()
        t0 = time.time()
        ld_bm = hl.ld_matrix(mt.GT.n_alt_alleles(), mt.locus, radius=args.radius_bp)
        ld_bm.write(old_uri, overwrite=True)
        print(f"[OLD] write wall: {time.time() - t0:.1f}s")
        old_warning = _warning_seen(capture, hail_log)
        old_np = hl.linalg.BlockMatrix.read(old_uri).to_numpy()

    a_warning, a_scratch_bytes = _phase(hl, "A (dense-then-band, current default)",
                                        _run_ordering_A, mt, args.radius_bp, a_uri, a_scratch,
                                        capture, hail_log)
    b_warning, b_scratch_bytes = _phase(hl, "B (band-then-checkpoint, proposed; MIGHT re-hang)",
                                        _run_ordering_B, mt, args.radius_bp, b_uri, b_scratch,
                                        capture, hail_log)

    def _validate(label, uri):
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
              f"parity max|Δr|={'n/a' if parity is None else f'{parity:.3e}'}")
        ok = shape == (n, n) and present and (parity is None or parity < 1e-5)
        return ok

    print("\n========== RESULT ==========")
    if not args.skip_old:
        print(f"[OLD] lowering warning present : {old_warning}  (expect True — the hang shape)")
    print(f"[A]   lowering warning present : {a_warning}  scratch={_fmt_bytes(a_scratch_bytes) if a_scratch_bytes is not None else 'n/a'} (DENSE)")
    print(f"[B]   lowering warning present : {b_warning}  scratch={_fmt_bytes(b_scratch_bytes) if b_scratch_bytes is not None else 'n/a'} (BANDED)")
    a_ok = _validate("A", a_uri)
    b_ok = _validate("B", b_uri)

    print("\n---------- DECISION ----------")
    a_clear = (a_warning is False) and a_ok
    b_clear = (b_warning is False) and b_ok
    if a_clear and b_clear:
        print("BOTH A and B are warning-free + valid -> per rubric, SHIP B (banded scratch).")
        print("  Re-order _write_a3_banded_correlation_bm to band-before-checkpoint, then re-run")
        print("  --report-scratch-size to confirm the banded worst-case fits cluster capacity.")
    elif a_clear and not b_clear:
        print("ONLY A is warning-free -> A is REQUIRED (B re-fuses/re-hangs).")
        print("  GATE-3 BLOCKED until the ~2 TB dense worst-case (see --report-scratch-size)")
        print("  is sized against cluster scratch capacity. Keep ordering A.")
    elif b_clear and not a_clear:
        print("ONLY B is warning-free -> unexpected (A checkpoints only row_correlation).")
        print("  Investigate before shipping; B is the candidate but verify scratch capacity.")
    else:
        print("NEITHER A nor B is warning-free -> ESCALATE. The checkpoint is not breaking the")
        print("  fusion; a different decomposition (per-block write) is needed before GATE-3.")

    if not args.skip_old and old_warning is not True:
        print("\nNOTE: OLD did NOT show the warning at this synthetic n — increase --n-var or")
        print("  inspect the log path; the OLD warning is the positive control for the grep.")
    return 0 if (a_clear or b_clear) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-bucket",
                    help="gs:// (or local dir) prefix for old/A/B/scratch_* .bm outputs "
                         "(required for the ordering experiment; not needed for --report-scratch-size)")
    ap.add_argument("--n-var", type=int, default=400)
    ap.add_argument("--n-samples", type=int, default=300)
    ap.add_argument("--radius-bp", type=int, default=1_000_000)
    ap.add_argument("--hail-log", default=None,
                    help="path to the active Hail driver log (auto-discovers newest /tmp/hail*.log)")
    ap.add_argument("--skip-old", action="store_true",
                    help="skip the OLD fused-write path (use if it hangs at your chosen n)")
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
