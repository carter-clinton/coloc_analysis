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
    ``out_bucket=None`` keeps that reused guard on its local-dir branch, so no
    hail import is ever triggered. The durable ``gs://`` support uses ``gsutil``
    as a plain SUBPROCESS (NOT a hail import), so the module still imports with no
    hail installed.

  * **Durable ``gs://`` destination (AoU Dataproc bucket-first).** ``out_dir`` may
    be a ``gs://`` bucket prefix: regions compute into a LOCAL scratch dir, are
    content-verified, then the verified ``.npz`` (+ AF sidecar) is uploaded via
    ``gsutil cp`` — so banked regions survive a Dataproc cluster recycle (local disk
    dies with the cluster; [[feedback_aou_use_persistent_disk]]). The ``gs://``
    resume guard consults the BUCKET via ``gsutil stat`` (``_existing_region_npz_gs``,
    same MED-6 floor; a truncated/short object recomputes). The individual-level
    ``.bed/.bim/.fam`` are NEVER uploaded by the driver — only the aggregate
    ``.npz``/AF cross into the bucket (REQ-AOU-LD-EGRESS).

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

  * **Retired Hail A.3 path untouched.** This module imports ``aou_ld_panel``
    ONLY for ``_existing_region_npz`` + ``build_plink_ld_command``; it never calls
    the retired Hail BlockMatrix correlation/banding helpers (a regression test
    asserts none of those retired symbols appear anywhere in this source).

Horizontal fan-out note: N Spot VMs sharing one ``out_dir`` is SAFE because
``_existing_region_npz`` makes every process skip what the others already banked
— but this module builds NO orchestration; it is a single serial loop.

Usage (local out-dir):
    python src/python/run_native_ld_panel.py \
        --manifest config/ld_regions.tsv \
        --bfile-prefix <in_perimeter_bfile> \
        --out-dir <in_perimeter_out_dir> \
        --mode square --ancestry AFR \
        --panel-tsv <out_dir>/m3-W2-native-plink-panel.tsv

Usage (durable gs:// out-dir, AoU Dataproc):
    python src/python/run_native_ld_panel.py \
        --manifest config/ld_regions.tsv \
        --bfile-prefix <in_perimeter_bfile> \
        --out-dir gs://<bucket>/ld/AFR_aou \
        --scratch-dir /tmp/native_ld_scratch \
        --mode square --ancestry AFR \
        --panel-tsv gs://<bucket>/ld/AFR_aou/m3-W2-native-plink-panel.tsv
"""
from __future__ import annotations

import argparse
import json
import math
import os
import resource
import subprocess
import sys
import tempfile
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
import occlusion_manifest as ocm  # Stage-A (coordinate-only) occlusion provenance
from occlusion_span_filter import detect_occluded_variants  # m3-07b span filter

_PANEL_COLUMNS = [
    "region_id", "chr", "n_var", "wall_min", "peak_ram_gib", "output_gib", "status",
    # m3-07b: durable per-region record of how many REFERENCE-OCCLUDED variants the
    # span filter excluded before --r (the pre-registered exclude-in-lockstep
    # policy, osf.io/az52u). Distinct from the monomorphic drop below: a conflated
    # single count could not distinguish "plink dropped a MAC=0 site" from "we
    # excluded a structurally-undefined-LD record", which is exactly the provenance
    # the OSF amendment-update commits to publishing.
    #
    # INSERTED here (not appended after n_dropped_monomorphic) — the leading 7
    # columns keep their exact positions, AND n_dropped_monomorphic keeps its
    # position as the LAST column, which the pre-existing
    # test_panel_columns_include_n_dropped_monomorphic pins (`_PANEL_COLUMNS[-1]`).
    # See the m3-07b SUMMARY: the plan's prose said "append after
    # n_dropped_monomorphic", which would have broken that passing test.
    "n_dropped_occluded",
    # 260701-qcy hardening H2 (blast-radius D4): durable per-region record of how
    # many monomorphic (MAC=0-in-AFR) variants --mac 1 dropped before --r square.
    # APPENDED (never reorder the leading columns); None on skip/banded/error rows.
    "n_dropped_monomorphic",
]
_DEFAULT_PANEL_NAME = "m3-W2-native-plink-panel.tsv"

# m3-02e-T4 transient short-read guard (260630-rn4): a one-off short read of the
# cohort .bim by _window_bim_n_var's read_text() at the instant plink finishes
# writing the 42 GB .ld.bin can return 0 in-window rows against a NON-empty
# .ld.bin, dropping a region across an ~11-day serial fire. The SQUARE verify path
# retries the window count a bounded number of times so the transient self-heals
# in-run; a genuine persistent 0 still raises the byte-identical n_var mismatch.
_WINDOW_BIM_RETRIES = 3
_WINDOW_BIM_RETRY_SLEEP_S = 0.5


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
# Durable gs:// destination (Dataproc bucket-first; local disk dies w/ cluster) #
#                                                                             #
# On an AoU Dataproc cluster the local disk is ephemeral (it dies with the    #
# cluster — [[feedback_aou_use_persistent_disk]]), so banked .npz must land in #
# a gs:// bucket to survive a recycle and to make resume work across recycles. #
# gsutil is a SUBPROCESS (NOT a hail import): the module stays hail-free.      #
# These are the SOLE gsutil call sites; tests monkeypatch _run_gsutil.        #
# --------------------------------------------------------------------------- #

def _is_gs_uri(path: "str | Path") -> bool:
    """True iff ``path`` is a ``gs://`` URI (a str starting with gs://)."""
    return isinstance(path, str) and path.startswith("gs://")


def _gs_join(prefix: str, name: str) -> str:
    """Join a gs:// prefix and an object name with a single slash."""
    return f"{prefix.rstrip('/')}/{name}"


def _run_gsutil(args: list[str]) -> "subprocess.CompletedProcess":
    """Run ``gsutil <args>`` and return the CompletedProcess (check=True).

    SOLE gsutil seam — tests monkeypatch exactly this function. gsutil is a plain
    subprocess (NOT a hail import), so the module stays importable without hail.
    """
    return subprocess.run(["gsutil", *args], check=True,
                          capture_output=True, text=True)


def _gsutil_object_size(gs_uri: str) -> "int | None":
    """Return the Content-Length of ``gs_uri`` via ``gsutil stat``, or None if the
    object is absent / any gsutil error occurs (safer to recompute than to assume a
    checkpoint that may not exist)."""
    try:
        proc = _run_gsutil(["stat", gs_uri])
    except Exception:
        return None
    for line in (proc.stdout or "").splitlines():
        if "Content-Length:" in line:
            try:
                return int(line.split("Content-Length:")[1].strip())
            except (ValueError, IndexError):
                return None
    return None


def _existing_region_npz_gs(region_id: str, gs_out_dir: str) -> "str | None":
    """Hail-free gs:// resume guard: return ``{gs_out_dir}/{region_id}.npz`` iff it
    exists in the bucket AND its size >= ``_MIN_REGION_NPZ_BYTES`` (the MED-6
    truncation floor), else None. Does NOT use _existing_region_npz's hail hadoop
    branch — consults the bucket purely via ``gsutil stat`` (subprocess)."""
    uri = _gs_join(gs_out_dir, f"{region_id}.npz")
    size = _gsutil_object_size(uri)
    if size is not None and size >= alp._MIN_REGION_NPZ_BYTES:
        return uri
    if size is not None and size < alp._MIN_REGION_NPZ_BYTES:
        print(f"WARN: existing {uri} is {size} B (< {alp._MIN_REGION_NPZ_BYTES} B "
              f"floor) — treating as truncated; will recompute (m3-W2 MED-6).",
              file=sys.stderr, flush=True)
    return None


def _gsutil_upload(local_path: "str | Path", gs_uri: str) -> None:
    """Upload a single local file to ``gs_uri`` via ``gsutil cp``."""
    _run_gsutil(["cp", str(local_path), gs_uri])


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
        if not pln._is_symmetric_blocked(ld, atol=1e-4):
            return (False, "not symmetric (atol 1e-4)")
    elif mode == "banded":
        lt = bool(z["lower_triangular"][0]) if "lower_triangular" in z.files else False
        if lt is not True:
            return (False, "banded npz lower_triangular flag is not True")
        if not pln._strict_upper_is_zero_blocked(ld):
            return (False, "banded npz has non-zero strict upper triangle")
    else:
        return (False, f"unknown mode {mode!r}")

    return (True, f"ok (n={n})")


# --------------------------------------------------------------------------- #
# Window-subset .bim + n_var cross-check                                      #
# --------------------------------------------------------------------------- #

def _chrom_match_key(chrom) -> str:
    """Normalize a contig label for cohort-.bim ↔ manifest matching.

    plink1.9 normalizes a leading ``chr``/``CHR`` prefix, so ``--chr 1`` matches a
    ``chr1``-prefixed GRCh38 ``.bim`` and emits the in-window ``.ld.bin``. The
    ``config/ld_regions.tsv`` ``chr`` column is bare numeric (``1``) while the AoU
    GRCh38 cohort ``.bim`` is ``chr``-prefixed (``chr1``), so the verify MUST strip
    the prefix on both sides or it counts 0 in-window rows and fails ``n_var``
    cross-check on every region ([[feedback_npz_triangle_flag_contract]] class of
    silent contig-format drift; see also ld_npz_to_rds.R's downstream ``^chr`` strip).
    """
    s = str(chrom).strip()
    low = s.lower()
    return s[3:] if low.startswith("chr") else s


def _window_bim_n_var(bim_path: "str | Path", chrom, from_bp: int, to_bp: int) -> tuple[int, Path]:
    """Build the WINDOW-SUBSET .bim (in cohort row order) for [from_bp, to_bp] on
    ``chrom`` and return (n_var, window_bim_path).

    plink ``--r`` over ``--from-bp/--to-bp`` emits LD for exactly the in-window
    variants, in cohort ``.bim`` order. plink_ld_to_npz.load_bim must therefore
    read a ``.bim`` containing ONLY the in-window rows (in that order) so its row
    order == the ``.ld.bin`` row order. The subset ``.bim`` is written next to the
    cohort ``.bim`` as ``{cohort}.{region-window}.bim``-style temp; callers pass
    that path to plink_ld_to_npz. The chrom compare is ``chr``-prefix agnostic
    (``_chrom_match_key``, mirroring plink1.9); kept-line content stays VERBATIM so
    the written window ``.bim`` preserves the cohort's native contig labels.
    """
    bim_path = Path(bim_path)
    chrom_key = _chrom_match_key(chrom)
    kept_lines: list[str] = []
    for line in bim_path.read_text().splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        if _chrom_match_key(parts[0]) == chrom_key and from_bp <= int(parts[3]) <= to_bp:
            kept_lines.append(line.rstrip("\n"))
    n_var = len(kept_lines)
    window_bim = bim_path.with_name(f"{bim_path.stem}.{chrom_key}_{from_bp}_{to_bp}.window.bim")
    window_bim.write_text("\n".join(kept_lines) + ("\n" if kept_lines else ""))
    return n_var, window_bim


def _window_bim_n_var_retry_on_zero(
    bim_path: "str | Path", chrom, from_bp: int, to_bp: int, *,
    expect_nonzero: bool,
    retries: int = _WINDOW_BIM_RETRIES,
    sleep_s: float = _WINDOW_BIM_RETRY_SLEEP_S,
) -> tuple[int, Path]:
    """Transient-short-read guard around ``_window_bim_n_var`` (m3-02e-T4 260630-rn4).

    ``_window_bim_n_var`` reads the cohort ``.bim`` via ``read_text()``. At the
    instant plink finishes writing the 42 GB ``.ld.bin``, that read can return a
    one-off ZERO in-window count against a NON-empty ``.ld.bin`` — a transient that
    would otherwise fail the SQUARE ``n_var`` cross-check and silently drop the
    region across an ~11-day serial fire. When the caller KNOWS the window is
    non-empty (``expect_nonzero`` — i.e. the square ``.ld.bin`` already implies
    ``bin_n_var > 0``), retry the window count up to ``retries`` more times so the
    transient self-heals in-run, emitting a LOUD auditable stderr WARN on recovery.

    A GENUINE persistent ``0`` never recovers: the LAST ``(0, window_bim)`` is
    returned UNCHANGED so the caller's existing ``bin_n_var != window_n_var`` check
    raises the byte-identical ``ValueError`` (the region records ``status='error:
    ...'`` and the loop continues). When ``expect_nonzero`` is False (a legitimately
    empty window), the loop is NOT spun — the single first result is returned.
    Fixed with a REUSABLE wrapper + failing-first regression per
    [[feedback_extract_reusable_utilities]] (recurrent window-verify drift class).
    """
    n_var, window_bim = _window_bim_n_var(bim_path, chrom, from_bp, to_bp)
    if not (n_var == 0 and expect_nonzero):
        return n_var, window_bim

    for _ in range(retries):
        time.sleep(sleep_s)
        n_var, window_bim = _window_bim_n_var(bim_path, chrom, from_bp, to_bp)
        if n_var > 0:
            print(
                f"WARN: transient zero-row window .bim for "
                f"chr{_chrom_match_key(chrom)}:[{from_bp},{to_bp}] recovered on retry "
                f"(n_var={n_var}); a transient short read of the cohort .bim "
                f"self-healed in-run (m3-02e-T4 260630-rn4).",
                file=sys.stderr, flush=True,
            )
            return n_var, window_bim

    # never recovered -> return the last (0, window_bim) so the caller raises the
    # byte-identical n_var mismatch (persistent genuine-empty vs a non-empty .ld.bin).
    return n_var, window_bim


def _needs_retained_subset(bin_n_var: int, raw_window_n_var: int) -> bool:
    """Defect 1 (quick 260703-vk9): the snplist∩raw-window-.bim intersection is
    needed ONLY when ``--mac`` actually dropped variants — i.e. the ``.ld.bin`` count
    differs from the raw in-window count. In the observed AFR regime ``--mac 1``
    drops 0 (``bin_n_var == raw_window_n_var``), so the intersection is a no-op that
    only adds a snplist-read race; skip it and use the (already race-guarded) raw
    window ``.bim`` directly. A non-equal count (a real drop, OR a genuine mismatch)
    -> do the intersection so ``n_var`` aligns to the retained ``.ld.bin`` row order
    (a genuine mismatch still trips the caller's byte-identical ``n_var`` check
    downstream)."""
    return bin_n_var != raw_window_n_var


def _retained_window_bim(raw_window_bim: "str | Path",
                         snplist_path: "str | Path",
                         *, region_id: str = "",
                         expect_nonzero: bool = False) -> tuple[int, Path]:
    """Subset a RAW in-window ``.bim`` to the plink ``--write-snplist`` RETAINED set,
    in snplist order, and return ``(n_retained, retained_window_bim_path)``
    (quick 260701-qcy — drop monomorphic MAC=0 variants).

    plink1.9 applies ``--mac 1`` (drop MAC=0) AFTER the ``--chr/--from-bp/--to-bp``
    window but BEFORE ``--r square``, so the emitted ``.ld.bin`` is
    ``(n_retained)^2`` with NO monomorphic (zero-variance -> ``0/0 -> NaN`` LD)
    rows, and ``--write-snplist`` writes the retained variant ids in filtered
    ``.bim`` order == the ``.ld.bin`` row order. The raw window ``.bim`` (from
    ``_window_bim_n_var``, produced THROUGH the 27af416 transient-short-read guard)
    still lists ALL in-window variants, so its count would DISAGREE with the
    ``.ld.bin`` on every region. This helper intersects the raw window ``.bim`` with
    the snplist and RE-ORDERS to snplist order (the authoritative ``.ld.bin`` row
    order — not a bp re-sort), so ``plink_ld_to_npz.load_bim``'s row order matches
    the ``.ld.bin`` columns and ``n_var == n_retained`` (the per-region ``n_var``
    now legitimately EXCLUDES monomorphic MAC=0 variants). ``read_square_bin`` /
    ``load_bim`` are UNCHANGED (they CAUGHT the NaN — they are correct).

    A snplist id absent from the raw window ``.bim`` is skipped, so a genuine
    bin/window disagreement still trips the caller's byte-identical ``n_var``
    mismatch ``ValueError``.

    HARDENING (260701-qcy blast-radius D1+D2): the raw-window keying was
    first-occurrence-wins (``setdefault``). A DUPLICATE col-2 id that the snplist
    references would then SILENTLY pick one of two distinct rows and misalign the
    LD rows against the variant ids — and NO existing guard catches it (``n_var``
    counts still match, the matrix is still symmetric). Instead of silently
    misaligning, RAISE a clear ``ValueError`` naming the region + the offending id.
    Production ``hl.export_plink`` varids (``chr:pos:ref:alt``) ARE unique, so this
    never trips on the real cohort; it only converts the one silent-catastrophe
    path into a loud, resume-safe failure (the loop records ``status='error: ...'``
    and continues).
    """
    raw_window_bim = Path(raw_window_bim)
    snplist_path = Path(snplist_path)
    # Defect 1 (quick 260703-vk9): the snplist read must be guarded against the SAME
    # transient short read that _window_bim_n_var_retry_on_zero guards for the raw
    # window .bim. The live region-1 failure was this exact race: a bare read_text()
    # hit an un-flushed (empty) {out_prefix}.snplist -> 0 retained ids -> a false
    # n_var mismatch. When the caller KNOWS a real drop occurred (expect_nonzero),
    # retry the read until it is non-empty; a genuinely-empty snplist still returns
    # [] after the bounded retries so the caller's mismatch check still fires.
    retained_ids = [ln.strip() for ln in snplist_path.read_text().splitlines()
                    if ln.strip()]
    if not retained_ids and expect_nonzero:
        for _ in range(_WINDOW_BIM_RETRIES):
            time.sleep(_WINDOW_BIM_RETRY_SLEEP_S)
            retained_ids = [ln.strip() for ln in snplist_path.read_text().splitlines()
                            if ln.strip()]
            if retained_ids:
                print(
                    f"WARN: transient empty snplist for {region_id} recovered on retry "
                    f"({len(retained_ids)} retained); a short read of {snplist_path.name} "
                    f"self-healed in-run (Defect 1, quick 260703-vk9).",
                    file=sys.stderr, flush=True,
                )
                break
    retained_set = set(retained_ids)
    by_snp: dict[str, str] = {}
    seen: set[str] = set()
    for line in raw_window_bim.read_text().splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        snp = parts[1]  # SNP id (col 2)
        # LOUD uniqueness guard: a duplicate col-2 id the snplist references cannot
        # be aligned to a single LD row -> fail instead of first-occurrence-wins.
        if snp in seen and snp in retained_set:
            raise ValueError(
                f"ambiguous variant id {snp!r} appears >1x in the window .bim for "
                f"{region_id} — cannot align LD rows to variant ids"
            )
        seen.add(snp)
        by_snp.setdefault(snp, line.rstrip("\n"))  # SNP id (col 2) -> verbatim line
    kept_lines = [by_snp[snp] for snp in retained_ids if snp in by_snp]
    retained_n_var = len(kept_lines)
    retained_bim = raw_window_bim.with_name(f"{raw_window_bim.stem}.retained.bim")
    retained_bim.write_text("\n".join(kept_lines) + ("\n" if kept_lines else ""))
    return retained_n_var, retained_bim


def _n_var_from_ld_bin(ld_bin_path: "str | Path") -> int:
    """square .ld.bin holds n_var**2 little-endian float32 -> n_var = sqrt(bytes/4)."""
    nbytes = Path(ld_bin_path).stat().st_size
    return int(round(math.sqrt(nbytes / 4.0)))


# --------------------------------------------------------------------------- #
# Resume-safe panel TSV append                                                #
# --------------------------------------------------------------------------- #

def _append_panel_row_local(tsv_path: Path, row: dict) -> None:
    """Resume-safe append to a LOCAL panel TSV (the core dedup-by-region_id logic)."""
    out_row = {c: row.get(c) for c in _PANEL_COLUMNS}
    if not tsv_path.exists():
        tsv_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([out_row], columns=_PANEL_COLUMNS).to_csv(
            tsv_path, sep="\t", index=False
        )
        return
    existing = pd.read_csv(tsv_path, sep="\t", dtype={"region_id": str})
    # Reconcile the header BEFORE the dedup read below — ordering is load-bearing: a
    # shifted stale file can make `existing["region_id"]` KeyError first, masking the
    # real diagnosis. Appending under a mismatched header writes N fields beneath M
    # names, which either aborts the next region's dedup read on an UNCAUGHT
    # ParserError (append_panel_row is called at :808, outside the per-region
    # try/except) or — against a header-only file — silently shifts every column via
    # pandas' implicit-index inference. Either way the ~11-day billed fire is lost or
    # its provenance falsified, so fail at region 1 at zero cost. REFUSE, never
    # auto-repair: a guard that silently repairs HIDES the bug.
    if list(existing.columns) != _PANEL_COLUMNS:
        raise ValueError(
            f"panel TSV {tsv_path} has a STALE header and cannot be appended to.\n"
            f"  found:    {list(existing.columns)}\n"
            f"  expected: {_PANEL_COLUMNS}\n"
            "Appending under a mismatched header produces a ragged TSV that aborts the "
            "loop on the next region's dedup read, or silently shifts every column. "
            "Rotate or delete the stale panel TSV and re-run; it is rebuilt from the "
            "banked per-region .npz files."
        )
    if str(out_row["region_id"]) in set(existing["region_id"].astype(str)):
        return  # already banked -> no duplicate row
    with tsv_path.open("a") as fh:
        pd.DataFrame([out_row], columns=_PANEL_COLUMNS).to_csv(
            fh, sep="\t", index=False, header=False
        )


def append_panel_row(tsv_path: "str | Path", row: dict,
                     *, scratch_dir: "str | Path | None" = None) -> None:
    """Append one row to the panel TSV, resume-safe (dedup by ``region_id``).

    Local ``tsv_path`` -> write/append in place. A ``gs://`` ``tsv_path`` -> maintain
    the local mirror under ``scratch_dir`` (downloading the current bucket copy on
    first touch so dedup survives a recycle), append, then upload the updated TSV.
    Columns are fixed (``_PANEL_COLUMNS``).
    """
    if not _is_gs_uri(tsv_path):
        _append_panel_row_local(Path(tsv_path), row)
        return

    # gs:// panel TSV: mirror locally in scratch, append, re-upload.
    gs_uri = str(tsv_path)
    scratch_dir = Path(scratch_dir or Path(tempfile.gettempdir()))
    scratch_dir.mkdir(parents=True, exist_ok=True)
    local_mirror = scratch_dir / gs_uri.rsplit("/", 1)[-1]
    if not local_mirror.exists():
        # Seed the local mirror from the bucket copy if one exists (resume-safe
        # dedup across a cluster recycle); absent/erroring -> start fresh.
        existing_size = _gsutil_object_size(gs_uri)
        if existing_size is not None and existing_size > 0:
            try:
                _run_gsutil(["cp", gs_uri, str(local_mirror)])
            except Exception:
                pass
    _append_panel_row_local(local_mirror, row)
    _gsutil_upload(local_mirror, gs_uri)


# --------------------------------------------------------------------------- #
# Per-region processing                                                        #
# --------------------------------------------------------------------------- #

def _reclaim_region_scratch(compute_dir: "str | Path", region_id: str,
                            *, keep_npz: bool) -> None:
    """Delete a region's local scratch artifacts once its output is durable.

    The bulky plink intermediates (``{region_id}.ld.bin``/``.ld.gz`` ~ n_var^2
    float32, plus ``.afreq``/``.log``/``.nosex``) accumulate ~30+ GiB/region; over a
    long serial panel (e.g. 276 AFR windows) that overflows any finite scratch disk.
    Called ONLY after the deliverable is safe: ``gs://`` -> the verified ``.npz`` is
    already uploaded to the bucket (``keep_npz=False``, drop everything); LOCAL ->
    the ``.npz`` IS the deliverable + the resume guard reads it (``keep_npz=True``,
    drop only the intermediates). The cohort bfile lives OUTSIDE ``compute_dir`` (a
    distinct ``--bfile-prefix`` dir), so the ``{region_id}.*`` glob never touches it.

    m3-07b: ``{region_id}.occluded.excludelist`` is DURABLE PROVENANCE, not a bulky
    intermediate — it is the exact drop set plink ``--exclude`` was given, and the
    pre-registered policy (osf.io/az52u) commits to every drop being auditable. It
    is tiny (one variant id per line) and is KEPT wherever the ``.npz`` is kept.
    In ``gs://`` mode the local scratch is fully reclaimed as before (the bucket
    holds the deliverable); the excludelist is uploaded alongside the verified
    ``.npz`` before this runs, so the provenance still lands durably.
    """
    compute_dir = Path(compute_dir)
    _keep_names = {f"{region_id}.npz", f"{region_id}.occluded.excludelist"}
    for p in compute_dir.glob(f"{region_id}.*"):
        if keep_npz and p.name in _keep_names:
            continue
        try:
            p.unlink()
        except OSError:  # best-effort reclaim; never fail the loop on cleanup
            pass


def process_region(row: dict, *, bfile_prefix: str, out_dir: "str | Path",
                   mode: str = "square", panel_tsv: "str | Path | None" = None,
                   scratch_dir: "str | Path | None" = None) -> dict:
    """Process ONE manifest region: skip-if-banked, else plink -> .npz -> verify
    -> (durable) land in the destination.

    ``out_dir`` may be a LOCAL path OR a ``gs://`` bucket prefix:

      * LOCAL ``out_dir`` -> compute directly into it; resume guard reuses the
        hail-free ``_existing_region_npz`` local-dir branch (MED-6 floor). Behavior
        is byte-identical to the pre-gs:// driver.
      * ``gs://`` ``out_dir`` (AoU Dataproc bucket-first; local disk dies with the
        cluster) -> compute into a LOCAL ``scratch_dir``, content-verify, THEN
        upload the verified ``.npz`` (and its ``.afreq`` sidecar if present) to the
        bucket via ``gsutil cp``. The resume guard consults the BUCKET via
        ``gsutil stat`` (``_existing_region_npz_gs``, MED-6 floor) — hail-free. The
        individual-level ``.bed/.bim/.fam`` are NEVER uploaded by the driver (only
        the aggregate ``.npz``/AF cross into the bucket; REQ-AOU-LD-EGRESS).

    Every plink command is built through ``build_plink_ld_command``
    (--keep-allele-order). Any exception or verify failure on this region records a
    status and lets the loop continue (one bad region never aborts the loop).
    """
    region_id = str(row["region_id"])
    chrom = row["chr"]
    from_bp = int(row["window_start_grch38"])
    to_bp = int(row["window_end_grch38"])
    gs_mode = _is_gs_uri(out_dir)

    if gs_mode:
        gs_out_dir = str(out_dir)
        compute_dir = Path(scratch_dir or Path(tempfile.gettempdir()) / "native_ld_scratch")
        panel_tsv = panel_tsv or _gs_join(gs_out_dir, _DEFAULT_PANEL_NAME)
    else:
        gs_out_dir = None
        compute_dir = Path(out_dir)
        panel_tsv = panel_tsv or (Path(out_dir) / _DEFAULT_PANEL_NAME)
    compute_dir.mkdir(parents=True, exist_ok=True)

    # (a) SKIP guard. gs:// -> consult the BUCKET via gsutil stat (hail-free);
    #     local -> reuse _existing_region_npz local-dir branch. Both enforce the
    #     _MIN_REGION_NPZ_BYTES MED-6 floor (a truncated object/file recomputes).
    if gs_mode:
        existing = _existing_region_npz_gs(region_id, gs_out_dir)
    else:
        existing = alp._existing_region_npz(region_id, None, compute_dir)
    if existing is not None:
        result = {
            "region_id": region_id, "chr": chrom, "n_var": None,
            "wall_min": None, "peak_ram_gib": None, "output_gib": None,
            "status": "skipped_idempotent", "out": existing,
            "n_dropped_occluded": None,     # skip: no filter run this pass
            "n_dropped_monomorphic": None,  # skip: no drop computed this run
        }
        append_panel_row(panel_tsv, result, scratch_dir=compute_dir)  # dedups
        return result

    out_prefix = str(compute_dir / region_id)
    result = {
        "region_id": region_id, "chr": chrom, "n_var": None,
        "wall_min": None, "peak_ram_gib": None, "output_gib": None,
        "status": "error", "out": None,
        "n_dropped_occluded": None,     # set in the SQUARE ok path; None otherwise
        "n_dropped_monomorphic": None,  # set in the SQUARE ok path; None otherwise
    }
    try:
        # window-subset .bim (load_bim row order == .ld.bin row order)
        bim_path = f"{bfile_prefix}.bim"

        # (b) REFERENCE-OCCLUSION span filter — m3-07b, BEFORE plink runs.
        #
        # Read the RAW window .bim FIRST and detect the variants an overlapping
        # deletion's REF span occludes, so they can be handed to plink --exclude and
        # never reach --r. This ORDERING is the whole fix: an occluded record that
        # survives into --r makes plink emit a NaN row/col (diagonal still 1.0 — the
        # m3-02e-T4 fire-#3 fingerprint), which the FROZEN read_square_bin correctly
        # refuses. The reader is right; the input was wrong. We remove the cause
        # upstream rather than conditioning the symptom downstream — NaN->0 is DEAD,
        # and the retired m3-06 conditioning module stays FROZEN/HELD and is never
        # imported here (a source-scan guard in the test suite enforces that, which
        # is why this comment names no retired symbol).
        #
        # This pre-plink read uses the PLAIN _window_bim_n_var, NOT the retry-on-zero
        # wrapper: the transient-short-read race that wrapper guards is a read racing
        # plink's own 42 GB .ld.bin write (m3-02e-T4 260630-rn4). Here plink has not
        # started, so there is no concurrent writer and nothing to race (RESEARCH §1
        # step 2). The POST-plink read below keeps the guard, untouched.
        exclude_path = None
        occluded_ids: list[str] = []
        occlusion_edges: list = []
        if mode == "square":
            pre_window_n_var, pre_window_bim = _window_bim_n_var(
                bim_path, chrom, from_bp, to_bp,
            )
            raw_rows = [
                ln.split()[:6]
                for ln in Path(pre_window_bim).read_text().splitlines()
                if ln.strip()
            ]
            occluded_ids, occlusion_edges = detect_occluded_variants(raw_rows)
            if occluded_ids:
                # Durable provenance, not a scratch temp: the excludelist is the
                # exact argv input plink saw, kept next to the region's outputs so a
                # reviewer can reproduce the drop set (survives _reclaim_region_scratch).
                excl = Path(f"{out_prefix}.occluded.excludelist")
                excl.parent.mkdir(parents=True, exist_ok=True)
                excl.write_text("".join(f"{vid}\n" for vid in occluded_ids))
                exclude_path = str(excl)
                print(
                    f"region {region_id}: EXCLUDING {len(occluded_ids)} "
                    f"reference-occluded variant(s) before --r "
                    f"({pre_window_n_var} in-window; overlapping-deletion REF span "
                    f"-> structurally undefined LD; excluded in lockstep with "
                    f"provenance, never zeroed — osf.io/az52u)",
                    file=sys.stderr, flush=True,
                )
                # Stage-A (coordinate/id-only) provenance manifest. Guarded: a
                # manifest write must never abort a region (one bad region never
                # aborts the loop) — the excludelist above is the redundant record.
                try:
                    ocm.append_occlusion_rows(
                        compute_dir, region_id, raw_rows, edges=occlusion_edges,
                    )
                except Exception as manifest_exc:  # noqa: BLE001 — provenance is best-effort
                    print(
                        f"WARN {region_id}: occlusion manifest append failed "
                        f"({manifest_exc}); the .occluded.excludelist still records "
                        f"the drop set",
                        file=sys.stderr, flush=True,
                    )

        cmd = alp.build_plink_ld_command(
            bfile_prefix=bfile_prefix, chrom=chrom, from_bp=from_bp, to_bp=to_bp,
            out_prefix=out_prefix, mode=mode, exclude=exclude_path,
        )
        wall_min, peak_ram_gib = _run_plink(cmd)
        result["wall_min"] = round(wall_min, 4)
        result["peak_ram_gib"] = round(peak_ram_gib, 4)

        if mode == "square":
            # SQUARE: compute bin_n_var FIRST so a NON-empty .ld.bin drives
            # expect_nonzero; the transient-short-read guard (m3-02e-T4 260630-rn4)
            # then self-heals a one-off zero-row window read in-run. A genuine
            # persistent 0 falls through to the byte-identical mismatch below.
            ld_path = Path(f"{out_prefix}.ld.bin")
            bin_n_var = _n_var_from_ld_bin(ld_path)
            # The RAW in-window .bim read STAYS behind the 27af416 transient guard
            # (retry-on-zero semantics INTACT — it is the producer of raw_window_bim).
            raw_window_n_var, raw_window_bim = _window_bim_n_var_retry_on_zero(
                bim_path, chrom, from_bp, to_bp, expect_nonzero=(bin_n_var > 0),
            )
            # --mac 1 drops MAC=0 monomorphic (zero-variance -> NaN LD) variants
            # BEFORE --r. When it dropped SOMETHING (bin_n_var != raw_window_n_var),
            # the .ld.bin (and --write-snplist) list only the RETAINED set, so we must
            # intersect the raw window .bim with the snplist (in snplist == .ld.bin
            # order) to align n_var + load_bim. But when it dropped NOTHING
            # (bin_n_var == raw_window_n_var — the observed AFR regime), that
            # intersection is a NO-OP that only re-reads the snplist and reintroduces
            # the Defect 1 race; SKIP it and use the (already race-guarded) raw window
            # .bim directly (quick 260703-vk9).
            if _needs_retained_subset(bin_n_var, raw_window_n_var):
                snplist_path = f"{out_prefix}.snplist"
                window_n_var, window_bim = _retained_window_bim(
                    raw_window_bim, snplist_path, region_id=region_id,
                    expect_nonzero=(bin_n_var > 0),
                )
            else:
                window_n_var, window_bim = raw_window_n_var, raw_window_bim
            if bin_n_var != window_n_var:
                raise ValueError(
                    f"n_var mismatch for {region_id}: .ld.bin implies {bin_n_var} "
                    f"but the window .bim has {window_n_var} rows — the .ld.bin and "
                    f"the [{from_bp},{to_bp}] window must agree."
                )
            n_var = window_n_var
            # HARDENING (260701-qcy H2, blast-radius D4): record + LOUDLY log how many
            # monomorphic (MAC=0) variants --mac 1 dropped. plink's own .log is
            # reclaimed with the region scratch, so this is the durable provenance.
            #
            # m3-07b SPLIT: the two drop reasons are DISTINCT and must not be
            # conflated. raw_window_n_var still counts ALL in-window variants
            # (including the ones we excluded), so the naive
            # `raw_window_n_var - window_n_var` would charge every occlusion drop to
            # the monomorphic column. Subtract the occluded set FIRST: the
            # monomorphic count is measured against the POST-exclude window, which is
            # the population plink's --mac 1 actually saw.
            n_dropped_occluded = len(occluded_ids)
            result["n_dropped_occluded"] = n_dropped_occluded
            n_dropped = (raw_window_n_var - n_dropped_occluded) - window_n_var
            result["n_dropped_monomorphic"] = n_dropped
            if n_dropped > 0:
                print(
                    f"region {region_id}: dropped {n_dropped} monomorphic (MAC=0) "
                    f"variants ({raw_window_n_var} in-window -> {window_n_var} "
                    f"retained)",
                    file=sys.stderr, flush=True,
                )
        else:
            window_n_var, window_bim = _window_bim_n_var(bim_path, chrom, from_bp, to_bp)
            ld_path = Path(f"{out_prefix}.ld.gz")
            n_var = window_n_var
            result["n_dropped_occluded"] = None     # banded: no span filter (square is the fire path)
            result["n_dropped_monomorphic"] = None  # banded does not drop MAC=0
        result["n_var"] = n_var

        af_sidecar = Path(f"{out_prefix}.afreq")
        af_arg = af_sidecar if af_sidecar.is_file() else None
        out_npz = compute_dir / f"{region_id}.npz"
        pln.plink_ld_to_npz(
            mode=mode, ld_path=ld_path, bim_path=window_bim,
            af_sidecar_path=af_arg, out_npz=out_npz, region_id=region_id, n_var=n_var,
        )

        ok, reason = content_verify_npz(out_npz, mode=mode)
        result["output_gib"] = round(out_npz.stat().st_size / 1024.0 ** 3, 6)
        result["status"] = "ok" if ok else "verify_failed"
        if not ok:
            print(f"VERIFY-FAILED {region_id}: {reason}", file=sys.stderr, flush=True)

        if gs_mode:
            if ok:
                # Upload ONLY the verified aggregate .npz (+ AF sidecar). The
                # individual-level .bed/.bim/.fam never leave the compute node.
                npz_uri = _gs_join(gs_out_dir, f"{region_id}.npz")
                _gsutil_upload(out_npz, npz_uri)
                result["out"] = npz_uri
                if af_arg is not None and Path(af_arg).is_file():
                    _gsutil_upload(af_arg, _gs_join(gs_out_dir, f"{region_id}.afreq"))
                # m3-07b: the occlusion drop set is durable provenance the OSF
                # amendment-update commits to publishing — upload it before the
                # local scratch is reclaimed. Coordinate/id-only (egress-clean:
                # variant ids + geometry, no genotypes, no per-person counts).
                if exclude_path is not None and Path(exclude_path).is_file():
                    _gsutil_upload(
                        exclude_path,
                        _gs_join(gs_out_dir, f"{region_id}.occluded.excludelist"),
                    )
            else:
                result["out"] = str(out_npz)  # left in scratch for inspection
        else:
            result["out"] = str(out_npz)
    except Exception as e:  # one bad region never aborts the whole loop
        result["status"] = f"error: {e}"
        print(f"ERROR {region_id}: {e}", file=sys.stderr, flush=True)

    append_panel_row(panel_tsv, result, scratch_dir=compute_dir)
    # Reclaim per-region scratch so a long serial panel can't fill the disk. ONLY on
    # success: a verify_failed/error region's artifacts are left for inspection (rare,
    # surfaced via the panel `status` column). gs:// -> the bucket holds the verified
    # .npz, drop everything; LOCAL -> keep the .npz (deliverable + resume guard).
    if result["status"] == "ok":
        _reclaim_region_scratch(compute_dir, region_id, keep_npz=not gs_mode)
    return result


# --------------------------------------------------------------------------- #
# Static index-sharding (8-VM Spot fan-out partitioning)                      #
# --------------------------------------------------------------------------- #

def _validate_shard(num_shards: int, shard_index: int) -> None:
    """Loudly reject an out-of-range shard spec.

    ``num_shards`` must be >= 1; ``shard_index`` must satisfy
    ``0 <= shard_index < num_shards``. Without this, a typo'd shard would either
    silently process nothing or re-run another VM's partition.
    """
    if not isinstance(num_shards, int) or num_shards < 1:
        raise ValueError(f"num_shards must be a positive int, got {num_shards!r}")
    if not isinstance(shard_index, int) or not (0 <= shard_index < num_shards):
        raise ValueError(
            f"shard_index must satisfy 0 <= shard_index < num_shards "
            f"({num_shards}); got shard_index={shard_index!r}"
        )


def _filter_ancestry(regions: list[dict], ancestry: str) -> list[dict]:
    """Filter manifest rows to ``ancestry`` (uppercase match) PRESERVING order."""
    return [r for r in regions
            if str(r.get("ancestry", "")).upper() == ancestry.upper()]


def _shard_rows(regions: list[dict], num_shards: int, shard_index: int) -> list[dict]:
    """Static index-shard: keep rows at positions ``idx`` where
    ``idx % num_shards == shard_index``, in the EXISTING (un-re-sorted) order.

    All shards must see the IDENTICAL ancestry-filtered order so the partition is
    consistent across VMs — callers must NOT re-sort before this. With
    ``num_shards==1`` every row is kept (single-VM behavior unchanged).
    """
    return [row for idx, row in enumerate(regions)
            if idx % num_shards == shard_index]


def select_shard_region_ids(manifest_path: "str | Path", *, num_shards: int = 1,
                            shard_index: int = 0, ancestry: str = "AFR") -> list[str]:
    """Pure partition preview: the ``region_id``s this shard would PROCESS (no
    plink, no I/O beyond reading the manifest). Used to prove the 8-shard
    partition is disjoint + exhaustive without running the loop."""
    _validate_shard(num_shards, shard_index)
    regions = _filter_ancestry(alp._read_manifest(Path(manifest_path)), ancestry)
    return [str(r["region_id"]) for r in _shard_rows(regions, num_shards, shard_index)]


# --------------------------------------------------------------------------- #
# Loop driver                                                                  #
# --------------------------------------------------------------------------- #

class RegionGateError(RuntimeError):
    """Raised when ``fail_fast`` is set and a region completes with a non-``ok``
    status — HALTS the serial native-plink LD loop so a broken region (e.g. region
    1) cannot silently precede a ~276-region / multi-day fire. ``process_region``
    already appended the failed region's panel row before this raises, so the loop
    stays resume-safe (fix the region, re-fire, the errored region recomputes)."""

    def __init__(self, region_id, status):
        self.region_id = region_id
        self.status = status
        super().__init__(
            f"region gate FAILED at {region_id}: status={status!r} — halting the "
            f"native-plink LD loop (fail_fast). Fix the region before re-firing; a "
            f"gate that only logs cannot protect a 276-region run."
        )


def run_native_ld_panel(manifest_path: "str | Path", bfile_prefix: str,
                        out_dir: "str | Path", *, mode: str = "square",
                        panel_tsv: "str | Path | None" = None,
                        ancestry: str = "AFR",
                        num_shards: int = 1, shard_index: int = 0,
                        scratch_dir: "str | Path | None" = None,
                        fail_fast: bool = False) -> list[dict]:
    """Drive the native-plink LD loop over the ``ancestry`` rows of the manifest.

    Reads the manifest (``aou_ld_panel._read_manifest``), filters to
    ``str(row['ancestry']).upper() == ancestry.upper()`` (mirrors the fire brief
    ``awk '$7=="AFR"'``), then STATIC-INDEX-SHARDS the filtered rows: this VM
    processes a region at filtered position ``idx`` ONLY when
    ``idx % num_shards == shard_index``. With ``num_shards==1`` (default) every
    region is processed (single-VM behavior unchanged). Returns the list of
    per-region result dicts. When ``fail_fast`` is set, the loop STOPS and raises
    ``RegionGateError`` on the first region whose ``status != 'ok'`` (its panel row
    is already written — resume-safe); default ``False`` keeps the resume-safe
    continue so one bad region never aborts the whole loop.

    ``out_dir`` may be a LOCAL path OR a ``gs://`` bucket prefix (durable,
    resume-safe via ``gsutil`` for the AoU Dataproc bucket-first layout — local disk
    dies with the cluster). For ``gs://``, regions compute into ``scratch_dir`` (a
    local temp dir) and the verified ``.npz``/AF are uploaded; the resume guard
    consults the bucket via ``gsutil stat``. ``panel_tsv`` defaults to
    ``out_dir/m3-W2-native-plink-panel.tsv`` (gs:// when out_dir is gs://).

    8-VM Spot fan-out: launch 8 VMs with ``--num-shards 8`` and
    ``--shard-index 0..7`` against the SAME ``out_dir`` but DISTINCT ``--panel-tsv``
    paths (e.g. ``...shard0.tsv``..``...shard7.tsv``). Sharding partitions WHICH
    regions each VM computes; it does NOT shard the output path — the ``.npz``
    outputs AND the resume guard stay pointed at the one shared ``out_dir``, so the
    resume guard is GLOBAL across all VMs and the egress bundler later sees all 276.
    The per-shard panel TSVs avoid concurrent-append corruption and are merged at
    handback.
    """
    _validate_shard(num_shards, shard_index)
    # Do NOT Path()-wrap a gs:// URI (Path would collapse gs:// -> gs:/).
    out_dir_arg: "str | Path" = str(out_dir) if _is_gs_uri(out_dir) else Path(out_dir)
    regions = _filter_ancestry(alp._read_manifest(Path(manifest_path)), ancestry)
    regions = _shard_rows(regions, num_shards, shard_index)

    results: list[dict] = []
    for row in regions:
        res = process_region(
            row, bfile_prefix=bfile_prefix, out_dir=out_dir_arg,
            mode=mode, panel_tsv=panel_tsv, scratch_dir=scratch_dir,
        )
        results.append(res)
        if fail_fast and str(res.get("status")) != "ok":
            raise RegionGateError(str(res.get("region_id")), str(res.get("status")))
    return results


def main(argv: "list[str] | None" = None) -> int:
    p = argparse.ArgumentParser(
        description="Resumable native-plink LD loop driver for the m3-02e AFR panel (STEP 4)."
    )
    p.add_argument("--manifest", default="config/ld_regions.tsv", type=Path,
                   help="Region manifest TSV (default config/ld_regions.tsv)")
    p.add_argument("--bfile-prefix", dest="bfile_prefix", required=True,
                   help="In-perimeter plink bfile prefix (.bed/.bim/.fam)")
    p.add_argument("--out-dir", dest="out_dir", required=True,
                   help="Destination for per-region .npz: a LOCAL dir OR a gs:// "
                        "bucket prefix (durable/resume-safe on AoU Dataproc, where "
                        "local disk dies with the cluster). gs:// uploads only the "
                        "aggregate .npz/AF — never the individual-level .bed/.bim/.fam.")
    p.add_argument("--scratch-dir", dest="scratch_dir", default=None,
                   help="Local scratch dir used to compute per-region outputs before "
                        "upload when --out-dir is gs:// (default: a system temp dir).")
    p.add_argument("--mode", choices=["square", "banded"], default="square",
                   help="LD output mode (D-02e-01 default: square)")
    p.add_argument("--panel-tsv", dest="panel_tsv", default=None,
                   help="Panel TSV (local OR gs://; default "
                        "<out-dir>/m3-W2-native-plink-panel.tsv)")
    p.add_argument("--ancestry", default="AFR",
                   help="Manifest ancestry filter (default AFR)")
    p.add_argument("--num-shards", dest="num_shards", type=int, default=1,
                   help="Total number of parallel VMs/shards (default 1 = single VM). "
                        "Static index-shard: this VM processes filtered rows where "
                        "idx %% num_shards == shard_index, against the SHARED out-dir.")
    p.add_argument("--shard-index", dest="shard_index", type=int, default=0,
                   help="0-based index of THIS shard (0 <= shard_index < num_shards). "
                        "For the 8-VM fan-out: 0..7, each with its own --panel-tsv.")
    p.add_argument("--fail-fast", dest="fail_fast", action="store_true",
                   help="Halt the loop (raise RegionGateError) on the FIRST region "
                        "whose status != 'ok'. Use to GATE region 1 before committing "
                        "to a full 276-region fire. Default off = resume-safe continue.")
    args = p.parse_args(argv)

    results = run_native_ld_panel(
        args.manifest, args.bfile_prefix, args.out_dir,
        mode=args.mode, panel_tsv=args.panel_tsv, ancestry=args.ancestry,
        num_shards=args.num_shards, shard_index=args.shard_index,
        scratch_dir=args.scratch_dir, fail_fast=args.fail_fast,
    )
    for res in results:
        print(json.dumps(res), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
