#!/usr/bin/env python3
"""Cluster repro + verify for the m3-W2 Path-A.3 BlockMatrixIR-lowering hang.

WHAT THIS PROVES
================
`compute_region_ld`'s Path A.3 used to call `hl.ld_matrix(...).write(bm_uri)` on a single
FUSED lazy BlockMatrixIR (row_correlation of standardized genotypes composed with the
radius banding). Hail 0.2.135 cannot lower that fused IR scalably, so it falls back to the
INTERPRETED, driver-mediated `BlockMatrixWrite` -> a single driver-side `ContextRDD.collect`
that HANGS for 60+ minutes on a large banded matrix (the dev-10 GATE-2 failure on
m2_region_00006: 122,678 variants, span 17.7 Mb).

The fix (src/python/aou_ld_panel.py::_write_a3_banded_correlation_bm) reproduces
hl.ld_matrix's OWN documented internals but inserts a checkpoint that breaks the fused IR:

    corr = hl.row_correlation(GT.n_alt_alleles())     # standardized Pearson r (== ld_matrix)
    corr = corr.checkpoint(scratch)                    # MATERIALIZE via native writer
    starts, stops = hl.linalg.utils.locus_windows(locus, radius=radius_bp)   # bp -> row band
    banded = corr.sparsify_row_intervals(starts, stops, blocks_only=False)   # exact same band
    banded.write(bm_uri)                               # small IR -> lowers natively

This script runs BOTH paths on a SMALL synthetic MT (cheap — seconds of cluster compute) and:
  (a) captures the Hail driver log around each write and reports whether the
      "BlockMatrixIR lowering not yet efficient/scalable" warning appears
      -> EXPECTED: PRESENT on OLD, ABSENT on NEW.
  (b) asserts the NEW path produced a valid .bm (readable, shape (n,n), _SUCCESS present).
  (c) (optional) asserts OLD vs NEW are numerically equal on a small region where OLD does
      NOT hang (small n keeps the interpreted writer tractable) — this proves the fix did
      not change the LD values, only the lowering path.

HOW CARTER RUNS IT (on the Dataproc / Hail Workbench cluster, NOT the NCSU HPC node)
====================================================================================
1. Ensure the env is the same one AOU-2 runs in (Hail importable, YARN-wired):
       echo $WORKSPACE_BUCKET          # must be gs://rw-migration-aou-rw-476cdac2 (or any writable gs:// for the scratch)
2. From the repo root on the cluster:
       python scripts/a3_blockmatrix_lowering_repro.py \
           --out-bucket $WORKSPACE_BUCKET/ld/_a3_lowering_repro \
           --n-var 400 --n-samples 300 --radius-bp 1000000

   Optionally point --hail-log at the active log so the grep is exact:
       python scripts/a3_blockmatrix_lowering_repro.py --hail-log /tmp/hail.log ...

3. WHERE TO LOOK FOR THE LOWERING WARNING:
   - Hail prints `LowerOrInterpretNonCompilable: ... BlockMatrixIR lowering not yet
     efficient/scalable` to the DRIVER hail log (default /tmp/hail-*.log; `hl.init` prints
     the exact path at startup, e.g. "Logging to: /tmp/hail-20260612-....log"). The script
     auto-discovers the newest /tmp/hail*.log if --hail-log is not given.
   - The script also routes Hail's Python logger to an in-memory buffer per phase and greps
     both the buffer and the on-disk log, so the result is robust to log-path quirks.

4. EXPECTED OUTPUT (PASS):
       [OLD] lowering warning present : True
       [NEW] lowering warning present : False
       [NEW] .bm readable, shape       : (400, 400)
       [NEW] _SUCCESS present          : True
       [PARITY] OLD vs NEW max|Δr|      : 0.0   (or < 1e-6)
       RESULT: PASS — fix removes the non-scalable lowering; NEW writes via native writer.

   If you set --skip-old (because OLD hangs at the n you chose), the parity check is skipped
   and only the NEW-path assertions + the absence of the warning on NEW are checked.

5. CLEANUP: the script writes only under --out-bucket/{old,new,scratch}; delete that prefix
   after the run. Keep it cheap: a few hundred variants × samples runs in seconds.

After this PASSES, re-run the standard dev-10 GATE-2 fire with the fixed code; m2_region_00006
(and the other large/xlarge A.3 cells) should now write a valid .bm in bounded time.
"""
from __future__ import annotations

import argparse
import glob
import io
import logging
import os
import sys
import time

LOWERING_SIGNATURE = "BlockMatrixIR lowering not yet efficient"


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


def _warning_seen(capture: _CaptureHandler, hail_log_path: str | None,
                  marker_time: float) -> bool:
    """True if the non-scalable-lowering warning appears in the captured buffer OR in the
    on-disk hail log written after marker_time."""
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


def _build_synth_mt(hl, n_var: int, n_samples: int, radius_bp: int):
    """Tiny synthetic, locus-sorted MT on chr1 with a GT field, contiguous so the bp radius
    spans the whole region (banding == dense on this small case, matching ld_matrix)."""
    import random

    # spread variants every (radius_bp // (n_var)) bp so the window covers all of them
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
    # deterministic pseudo-genotypes in {0,1,2}; a little structure so r != identity
    mt = mt.annotate_entries(
        GT=hl.unphased_diploid_gt_index_call(
            (mt.row_idx + mt.col_idx) % 3
        )
    )
    return mt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-bucket", required=True,
                    help="gs:// (or local dir) prefix for old/new/scratch .bm outputs")
    ap.add_argument("--n-var", type=int, default=400)
    ap.add_argument("--n-samples", type=int, default=300)
    ap.add_argument("--radius-bp", type=int, default=1_000_000)
    ap.add_argument("--hail-log", default=None,
                    help="path to the active Hail driver log (auto-discovers newest /tmp/hail*.log)")
    ap.add_argument("--skip-old", action="store_true",
                    help="skip the OLD fused-write path (use if it hangs at your chosen n)")
    args = ap.parse_args()

    import hail as hl
    import numpy as np

    # make src/python importable so we use the SAME helper the pipeline uses
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(repo_root, "src", "python"))
    from aou_ld_panel import _write_a3_banded_correlation_bm, _a3_scratch_uri  # noqa: E402

    hl.init()
    hail_log = args.hail_log or _newest_hail_log()
    print(f"[repro] Hail log: {hail_log}")

    capture = _CaptureHandler()
    logging.getLogger("hail").addHandler(capture)
    logging.getLogger().addHandler(capture)

    mt = _build_synth_mt(hl, args.n_var, args.n_samples, args.radius_bp)
    n = mt.count_rows()
    print(f"[repro] synthetic MT: {n} variants x {args.n_samples} samples; radius={args.radius_bp} bp")

    old_uri = f"{args.out_bucket}/old/repro_old.bm"
    new_uri = f"{args.out_bucket}/new/repro_new.bm"

    old_warning = None
    old_np = None
    if not args.skip_old:
        print("\n[OLD] hl.ld_matrix(...).write()  (fused IR -> expect lowering warning + slow)")
        capture.buf = io.StringIO()
        t0 = time.time()
        ld_bm = hl.ld_matrix(mt.GT.n_alt_alleles(), mt.locus, radius=args.radius_bp)
        ld_bm.write(old_uri, overwrite=True)
        print(f"[OLD] write wall: {time.time() - t0:.1f}s")
        old_warning = _warning_seen(capture, hail_log, t0)
        old_np = hl.linalg.BlockMatrix.read(old_uri).to_numpy()

    print("\n[NEW] _write_a3_banded_correlation_bm(...)  (materialize -> band -> write; expect NO warning)")
    capture.buf = io.StringIO()
    t1 = time.time()
    _write_a3_banded_correlation_bm(mt, args.radius_bp, new_uri)
    print(f"[NEW] write wall: {time.time() - t1:.1f}s")
    new_warning = _warning_seen(capture, hail_log, t1)

    # NEW-path validity
    new_bm = hl.linalg.BlockMatrix.read(new_uri)
    new_shape = new_bm.shape
    success_path = new_uri.rstrip("/") + "/_SUCCESS"
    try:
        success_present = hl.current_backend().fs.exists(success_path)
    except Exception:  # noqa: BLE001
        success_present = os.path.isfile(success_path)

    print("\n========== RESULT ==========")
    if not args.skip_old:
        print(f"[OLD] lowering warning present : {old_warning}")
    print(f"[NEW] lowering warning present : {new_warning}")
    print(f"[NEW] .bm readable, shape       : {new_shape}")
    print(f"[NEW] _SUCCESS present          : {success_present}")

    parity_ok = True
    if old_np is not None:
        new_np = new_bm.to_numpy()
        max_delta = float(np.max(np.abs(old_np - new_np)))
        parity_ok = max_delta < 1e-5
        print(f"[PARITY] OLD vs NEW max|Δr|      : {max_delta:.3e}")

    ok = (
        (args.skip_old or old_warning is True)   # OLD must show the warning (when run)
        and new_warning is False                  # NEW must NOT
        and tuple(new_shape) == (n, n)
        and success_present
        and parity_ok
    )
    print("RESULT:", "PASS — fix removes non-scalable lowering; NEW writes via native writer."
          if ok else "FAIL — inspect the per-phase output above.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
