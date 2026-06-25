"""run_native_ld_panel.py -- m3-02e STEP 4: the RESUMABLE native-plink LD loop
driver for the 276-region AFR LD panel (quick 260625-r6m).

The full square loop is ~263 VM-h (~11 days serial wall) on a single Spot VM that
WILL be preempted, so resumability + content-validated skip is mandatory. This
driver is the turnkey replacement for the hand-described STEP-4 bash loop in
``m3-02e-AFR-NATIVE-FIRE-BRIEF.md``.

Design contracts (all enforced by tests/m3/test_run_native_ld_panel.py):

  * **Hail-free at module scope.** This runs on a plink-only Spot VM (or NCSU
    after egress); it must import with no hail installed. It REUSES
    ``aou_ld_panel`` (which is itself hail-free at module scope — the hail import
    is lazy, inside ``_existing_region_npz``'s ``gs://`` branch only). Passing
    ``out_bucket=None`` keeps the resume guard on its local-dir branch, so no
    hail import is ever triggered.

  * **Idempotent resume via the MED-6 byte-floor, NOT a bare ``[ -f ]``.** The
    per-region skip reuses ``aou_ld_panel._existing_region_npz`` (``out_bucket=None``,
    ``out_local_dir=out_dir``), which enforces ``_MIN_REGION_NPZ_BYTES`` (256 B):
    a truncated ``.npz`` from a mid-write preemption is rejected and recomputed,
    not silently banked ([[feedback_aou_success_marker_not_evidence_of_data]]).
    A second back-to-back run over the same out dir therefore does ZERO plink work.

  * **``--keep-allele-order`` on every call, via the helper.** The driver issues
    plink ONLY through ``aou_ld_panel.build_plink_ld_command`` (the flag is
    hardcoded there); it never hand-rolls the plink argv (T-M3-02e-SIGN). Dropping
    the flag flips LD signs vs the GWAS z and makes susieR fail.

  * **Per-region content verification (D-M3-10).** ``content_verify_npz`` loads
    each ``.npz`` and asserts float32 / square shape / unit diagonal / symmetry
    (square) or the one-triangle invariant (banded). A region that fails is marked
    ``verify_failed`` and the loop CONTINUES (no whole-loop abort); markers /
    file existence are never trusted.

  * **Retired Hail A.3 path untouched.** This module does NOT reference
    ``compute_region_ld`` / ``_write_a3_banded_correlation_bm`` / ``row_correlation``
    / ``ld_matrix``; it imports ``aou_ld_panel`` ONLY for ``_existing_region_npz``
    + ``build_plink_ld_command``.

Horizontal fan-out note: N Spot VMs sharing one ``out_dir`` is SAFE because
``_existing_region_npz`` makes every process skip what the others already banked
— but this module builds NO orchestration; it is a single serial loop.

Usage:
    python src/python/run_native_ld_panel.py \
        --manifest config/ld_regions.tsv \
        --bfile-prefix <in_perimeter_bfile> \
        --out-dir <in_perimeter_out_dir> \
        --mode square --ancestry AFR \
        --panel-tsv <out_dir>/m3-W2-native-plink-panel.tsv
"""
from __future__ import annotations

import argparse
import json
import math
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# Bootstrap src/python on sys.path (mirror the test bootstrap) so the sibling
# native-plink modules import whether invoked as a script or imported as a module.
_SRC_PYTHON = Path(__file__).resolve().parent
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import aou_ld_panel as alp  # hail-free at module scope; reused for the guard + cmd builder
import plink_ld_to_npz as pln  # hail-free .ld.bin/.ld.gz -> egress-clean .npz

_PANEL_COLUMNS = [
    "region_id", "chr", "n_var", "wall_min", "peak_ram_gib", "output_gib", "status",
]
_DEFAULT_PANEL_NAME = "m3-W2-native-plink-panel.tsv"


# --------------------------------------------------------------------------- #
# SOLE subprocess seam (tests monkeypatch exactly this one function)          #
# --------------------------------------------------------------------------- #

def _run_plink(cmd: list[str]) -> tuple[float, float]:
    """Run the plink argv via subprocess; return (wall_min, peak_ram_gib).

    Peak child RAM is the RUSAGE_CHILDREN.ru_maxrss DELTA across the call (Linux
    ru_maxrss is KiB -> /1024/1024 = GiB). This is headless-safe on a Spot VM (no
    /usr/bin/time dependency). This is the ONLY subprocess call site, so tests
    monkeypatch a single seam.
    """
    rss_before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    t0 = time.time()
    subprocess.run(cmd, check=True)
    wall_min = (time.time() - t0) / 60.0
    rss_after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    peak_kib = max(rss_after - rss_before, rss_after)
    peak_ram_gib = peak_kib / 1024.0 / 1024.0
    return (wall_min, peak_ram_gib)


# --------------------------------------------------------------------------- #
# Content verification (D-M3-10; markers are NOT evidence)                    #
# --------------------------------------------------------------------------- #

def content_verify_npz(npz_path: "str | Path", *, mode: str = "square") -> tuple[bool, str]:
    """Contents-validate a region ``.npz`` -> (ok, reason).

    square: dtype float32, square shape, |diag - 1.0| < 1e-3 over the FULL
    diagonal, and ``np.allclose(ld, ld.T, atol=1e-4)``.
    banded: ``lower_triangular`` is True and ``np.triu(ld, k=1)`` all-zero.

    NEVER trusts file existence/size alone — this is the per-region D-M3-10 gate.
    Returns (False, reason) on any failure rather than raising, so the loop can
    record the status and continue.
    """
    try:
        z = np.load(str(npz_path), allow_pickle=True)
    except Exception as e:  # unreadable/truncated file
        return (False, f"unreadable npz: {e}")

    if "ld" not in z.files:
        return (False, "missing 'ld' key")
    ld = z["ld"]
    if ld.dtype != np.float32:
        return (False, f"dtype {ld.dtype} != float32")
    if ld.ndim != 2 or ld.shape[0] != ld.shape[1]:
        return (False, f"not square: shape {ld.shape}")
    n = ld.shape[0]

    if mode == "square":
        diag = np.diag(ld)
        if not np.allclose(diag, 1.0, atol=1e-3):
            return (False, "diagonal != 1.0 (atol 1e-3)")
        if not np.allclose(ld, ld.T, atol=1e-4):
            return (False, "not symmetric (atol 1e-4)")
    elif mode == "banded":
        lt = bool(z["lower_triangular"][0]) if "lower_triangular" in z.files else False
        if lt is not True:
            return (False, "banded npz lower_triangular flag is not True")
        if not np.allclose(np.triu(ld, k=1), 0.0):
            return (False, "banded npz has non-zero strict upper triangle")
    else:
        return (False, f"unknown mode {mode!r}")

    return (True, f"ok (n={n})")


# --------------------------------------------------------------------------- #
# Window-subset .bim + n_var cross-check                                      #
# --------------------------------------------------------------------------- #

def _window_bim_n_var(bim_path: "str | Path", chrom, from_bp: int, to_bp: int) -> tuple[int, Path]:
    """Build the WINDOW-SUBSET .bim (in cohort row order) for [from_bp, to_bp] on
    ``chrom`` and return (n_var, window_bim_path).

    plink ``--r`` over ``--from-bp/--to-bp`` emits LD for exactly the in-window
    variants, in cohort ``.bim`` order. plink_ld_to_npz.load_bim must therefore
    read a ``.bim`` containing ONLY the in-window rows (in that order) so its row
    order == the ``.ld.bin`` row order. The subset ``.bim`` is written next to the
    cohort ``.bim`` as ``{cohort}.{region-window}.bim``-style temp; callers pass
    that path to plink_ld_to_npz.
    """
    bim_path = Path(bim_path)
    chrom_s = str(chrom)
    kept_lines: list[str] = []
    for line in bim_path.read_text().splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        if str(parts[0]) == chrom_s and from_bp <= int(parts[3]) <= to_bp:
            kept_lines.append(line.rstrip("\n"))
    n_var = len(kept_lines)
    window_bim = bim_path.with_name(f"{bim_path.stem}.{chrom_s}_{from_bp}_{to_bp}.window.bim")
    window_bim.write_text("\n".join(kept_lines) + ("\n" if kept_lines else ""))
    return n_var, window_bim


def _n_var_from_ld_bin(ld_bin_path: "str | Path") -> int:
    """square .ld.bin holds n_var**2 little-endian float32 -> n_var = sqrt(bytes/4)."""
    nbytes = Path(ld_bin_path).stat().st_size
    return int(round(math.sqrt(nbytes / 4.0)))


# --------------------------------------------------------------------------- #
# Resume-safe panel TSV append                                                #
# --------------------------------------------------------------------------- #

def append_panel_row(tsv_path: "str | Path", row: dict) -> None:
    """Append one row to the panel TSV, resume-safe.

    If the TSV does not exist -> write header + row. If it exists and the row's
    ``region_id`` is already present -> do nothing (no duplicate). Otherwise append
    the row WITHOUT re-writing the header. Columns are fixed (``_PANEL_COLUMNS``).
    """
    tsv_path = Path(tsv_path)
    out_row = {c: row.get(c) for c in _PANEL_COLUMNS}

    if not tsv_path.exists():
        tsv_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([out_row], columns=_PANEL_COLUMNS).to_csv(
            tsv_path, sep="\t", index=False
        )
        return

    existing = pd.read_csv(tsv_path, sep="\t", dtype={"region_id": str})
    if str(out_row["region_id"]) in set(existing["region_id"].astype(str)):
        return  # already banked -> no duplicate row
    with tsv_path.open("a") as fh:
        pd.DataFrame([out_row], columns=_PANEL_COLUMNS).to_csv(
            fh, sep="\t", index=False, header=False
        )


# --------------------------------------------------------------------------- #
# Per-region processing                                                        #
# --------------------------------------------------------------------------- #

def process_region(row: dict, *, bfile_prefix: str, out_dir: Path,
                   mode: str = "square", panel_tsv: "str | Path | None" = None) -> dict:
    """Process ONE manifest region: skip-if-banked, else plink -> .npz -> verify.

    Resume guard (REUSED ``_existing_region_npz``, MED-6 floor) short-circuits a
    content-valid existing ``.npz`` with ZERO plink work. Every plink command is
    built through ``build_plink_ld_command`` (--keep-allele-order). Any exception
    or verify failure on this region records a status and lets the loop continue.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    region_id = str(row["region_id"])
    chrom = row["chr"]
    from_bp = int(row["window_start_grch38"])
    to_bp = int(row["window_end_grch38"])
    panel_tsv = panel_tsv or (out_dir / _DEFAULT_PANEL_NAME)

    # (a) SKIP guard -- out_bucket=None keeps the guard hail-free (local-dir branch,
    #     which enforces the _MIN_REGION_NPZ_BYTES floor).
    existing = alp._existing_region_npz(region_id, None, out_dir)
    if existing is not None:
        result = {
            "region_id": region_id, "chr": chrom, "n_var": None,
            "wall_min": None, "peak_ram_gib": None, "output_gib": None,
            "status": "skipped_idempotent", "out": existing,
        }
        append_panel_row(panel_tsv, result)  # dedups internally
        return result

    out_prefix = str(out_dir / region_id)
    result = {
        "region_id": region_id, "chr": chrom, "n_var": None,
        "wall_min": None, "peak_ram_gib": None, "output_gib": None,
        "status": "error", "out": None,
    }
    try:
        cmd = alp.build_plink_ld_command(
            bfile_prefix=bfile_prefix, chrom=chrom, from_bp=from_bp, to_bp=to_bp,
            out_prefix=out_prefix, mode=mode,
        )
        wall_min, peak_ram_gib = _run_plink(cmd)
        result["wall_min"] = round(wall_min, 4)
        result["peak_ram_gib"] = round(peak_ram_gib, 4)

        # window-subset .bim (load_bim row order == .ld.bin row order)
        bim_path = f"{bfile_prefix}.bim"
        window_n_var, window_bim = _window_bim_n_var(bim_path, chrom, from_bp, to_bp)

        if mode == "square":
            ld_path = Path(f"{out_prefix}.ld.bin")
            bin_n_var = _n_var_from_ld_bin(ld_path)
            if bin_n_var != window_n_var:
                raise ValueError(
                    f"n_var mismatch for {region_id}: .ld.bin implies {bin_n_var} "
                    f"but the window .bim has {window_n_var} rows — the .ld.bin and "
                    f"the [{from_bp},{to_bp}] window must agree."
                )
            n_var = window_n_var
        else:
            ld_path = Path(f"{out_prefix}.ld.gz")
            n_var = window_n_var
        result["n_var"] = n_var

        af_sidecar = Path(f"{out_prefix}.afreq")
        af_arg = af_sidecar if af_sidecar.is_file() else None
        out_npz = out_dir / f"{region_id}.npz"
        pln.plink_ld_to_npz(
            mode=mode, ld_path=ld_path, bim_path=window_bim,
            af_sidecar_path=af_arg, out_npz=out_npz, region_id=region_id, n_var=n_var,
        )

        ok, reason = content_verify_npz(out_npz, mode=mode)
        result["output_gib"] = round(out_npz.stat().st_size / 1024.0 ** 3, 6)
        result["out"] = str(out_npz)
        result["status"] = "ok" if ok else "verify_failed"
        if not ok:
            print(f"VERIFY-FAILED {region_id}: {reason}", file=sys.stderr, flush=True)
    except Exception as e:  # one bad region never aborts the whole 276 loop
        result["status"] = f"error: {e}"
        print(f"ERROR {region_id}: {e}", file=sys.stderr, flush=True)

    append_panel_row(panel_tsv, result)
    return result


# --------------------------------------------------------------------------- #
# Loop driver                                                                  #
# --------------------------------------------------------------------------- #

def run_native_ld_panel(manifest_path: "str | Path", bfile_prefix: str,
                        out_dir: "str | Path", *, mode: str = "square",
                        panel_tsv: "str | Path | None" = None,
                        ancestry: str = "AFR") -> list[dict]:
    """Drive the native-plink LD loop over the ``ancestry`` rows of the manifest.

    Reads the manifest (``aou_ld_panel._read_manifest``), filters to
    ``str(row['ancestry']).upper() == ancestry.upper()`` (mirrors the fire brief
    ``awk '$7=="AFR"'``), and calls :func:`process_region` per row. Returns the
    list of per-region result dicts. ``panel_tsv`` defaults to
    ``out_dir/m3-W2-native-plink-panel.tsv``.
    """
    out_dir = Path(out_dir)
    panel_tsv = panel_tsv or (out_dir / _DEFAULT_PANEL_NAME)
    regions = alp._read_manifest(Path(manifest_path))
    regions = [r for r in regions if str(r.get("ancestry", "")).upper() == ancestry.upper()]

    results: list[dict] = []
    for row in regions:
        res = process_region(
            row, bfile_prefix=bfile_prefix, out_dir=out_dir,
            mode=mode, panel_tsv=panel_tsv,
        )
        results.append(res)
    return results


def main(argv: "list[str] | None" = None) -> int:
    p = argparse.ArgumentParser(
        description="Resumable native-plink LD loop driver for the m3-02e AFR panel (STEP 4)."
    )
    p.add_argument("--manifest", default="config/ld_regions.tsv", type=Path,
                   help="Region manifest TSV (default config/ld_regions.tsv)")
    p.add_argument("--bfile-prefix", dest="bfile_prefix", required=True,
                   help="In-perimeter plink bfile prefix (.bed/.bim/.fam)")
    p.add_argument("--out-dir", dest="out_dir", required=True, type=Path,
                   help="Output dir for per-region .ld.bin/.ld.gz + .npz")
    p.add_argument("--mode", choices=["square", "banded"], default="square",
                   help="LD output mode (D-02e-01 default: square)")
    p.add_argument("--panel-tsv", dest="panel_tsv", default=None, type=Path,
                   help="Panel TSV (default <out-dir>/m3-W2-native-plink-panel.tsv)")
    p.add_argument("--ancestry", default="AFR",
                   help="Manifest ancestry filter (default AFR)")
    args = p.parse_args(argv)

    results = run_native_ld_panel(
        args.manifest, args.bfile_prefix, args.out_dir,
        mode=args.mode, panel_tsv=args.panel_tsv, ancestry=args.ancestry,
    )
    for res in results:
        print(json.dumps(res), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
