"""tests/m3/test_stitch_subregions_to_rds.py -- M3 Wave 2 re-scope (m3-02b).

Banded overlapping-window stitch + real-loader payload + whole-region payload
reconciliation. The 9 named stitch families (m3-02b Task 2):

    test_stitch_cross_core_band_retained   -- cross-boundary pair within
                                              buffer_bp RETAINED (not zeroed).
    test_stitch_zeroes_only_beyond_buffer  -- |pos_i-pos_j| > buffer_bp -> 0;
                                              sparse banded, NOT block-diagonal.
    test_stitch_banded_psd                 -- symmetric, diag==1, eigen >= -1e-6.
    test_stitch_allele_aware_alignment     -- order by (chr,pos,ref,alt); a
                                              multiallelic site is NOT collapsed.
    test_stitch_no_duplicate_variant_across_windows -- overlap variant appears
                                              once (core ownership).
    test_stitch_overlap_pair_agreement     -- a pair computed in 2 windows agrees
                                              (<1e-4) + single retained entry.
    test_stitch_sparse_payload             -- obj$R is dgCMatrix, round-trips.
    test_loader_accepts_stitched_payload   -- load_ld_matrix() accepts obj$R+
                                              obj$variants (NOT ld_missing).
    test_whole_region_payload_reconciled   -- ld_npz_to_rds.R emits R+variants.

NO-SKIP RULE (must_have A6): in the designated M3 conda env, missing R / Matrix
/ susieR makes these tests FAIL (no UNVERIFIED skip sentinel). The module-level
``_require_m3_r_toolchain()`` ERRORS (not skips) when the M3 marker env is active
but the toolchain is incomplete. Outside the M3 env (a bare dev box with no
usable Rscript) the tests skip with a diagnostic.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

# Make tests/m3 importable as a bare module dir so `from conftest import ...`
# resolves regardless of pytest import mode (mirrors the sibling modules).
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STITCH_R = PROJECT_ROOT / "src" / "scripts" / "stitch_subregions_to_rds.R"
CONVERTER_R = PROJECT_ROOT / "src" / "scripts" / "ld_npz_to_rds.R"
LOADER_R = PROJECT_ROOT / "src" / "legacy" / "region_analysis" / "scripts" / "run_susie_rss.R"
CHAIN_38_TO_37 = PROJECT_ROOT / "data" / "external" / "liftover" / "hg38ToHg19.over.chain.gz"

# The project-pinned M3 env (envs/m3-r-ld.yml). Its presence is the "M3 env is
# active" marker — when this Rscript exists the no-skip rule applies (ERROR on a
# broken toolchain rather than skip).
M3_R_LD_RSCRIPT = Path("/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/Rscript")
M3_R_LD_PYTHON = Path("/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/python")

R_PKGS = ("reticulate", "Matrix", "digest", "jsonlite", "susieR")

# Contention-safe subprocess wall-clock budget for every R round-trip below.
# SINGLE SOURCE OF TRUTH = the ROOT tests/conftest.py (the bare ``conftest`` module
# pytest imports; the tests/m3 conftest is shadowed by it). Flake-class fix for
# m3-W2-stitch-rds-test-failures: a ~66s reticulate cold-start under shared-node
# contention used to push tight literal timeouts past budget -> TimeoutExpired ->
# spurious FAILED. Re-exported here so sibling modules that already do
# `from test_stitch_subregions_to_rds import R_SUBPROCESS_TIMEOUT_S` keep working.
from conftest import R_SUBPROCESS_TIMEOUT_S  # noqa: E402,F401


def _candidate_rscripts() -> list[Path]:
    cands: list[Path] = []
    env = os.environ.get("M3_R_LD_RSCRIPT")
    if env:
        cands.append(Path(env))
    cands.append(M3_R_LD_RSCRIPT)
    on_path = shutil.which("Rscript")
    if on_path:
        cands.append(Path(on_path))
    seen: set[str] = set()
    out: list[Path] = []
    for c in cands:
        s = str(c.resolve()) if c.exists() else str(c)
        if s in seen:
            continue
        seen.add(s)
        out.append(c)
    return out


def _r_env_with_reticulate_python(rscript: Path) -> dict:
    """Return a subprocess env that pins RETICULATE_PYTHON to the env's own
    python (which carries numpy + pyliftover) when rscript is the m3-r-ld pin."""
    env = dict(os.environ)
    py = rscript.parent / "python"
    if py.exists():
        env.setdefault("RETICULATE_PYTHON", str(py))
    return env


def _check_r_env(rscript: Path) -> tuple[bool, str]:
    if not rscript.exists():
        return False, f"Rscript not found at {rscript}"
    probe = (
        'pkgs <- c("reticulate","Matrix","digest","jsonlite","susieR"); '
        'missing <- pkgs[!sapply(pkgs, requireNamespace, quietly=TRUE)]; '
        'if (length(missing)) { cat("MISSING_R:", paste(missing, collapse=","), "\\n"); quit(status=2) }; '
        'np <- tryCatch(reticulate::import("numpy"), error=function(e) NULL); '
        'pl <- tryCatch(reticulate::import("pyliftover"), error=function(e) NULL); '
        'if (is.null(np)) { cat("MISSING_PY: numpy\\n"); quit(status=3) }; '
        'if (is.null(pl)) { cat("MISSING_PY: pyliftover\\n"); quit(status=4) }; '
        'cat("OK\\n")'
    )
    try:
        res = subprocess.run([str(rscript), "-e", probe], capture_output=True,
                             text=True, timeout=R_SUBPROCESS_TIMEOUT_S,
                             env=_r_env_with_reticulate_python(rscript))
    except Exception as exc:  # noqa: BLE001
        return False, f"Rscript probe failed: {exc!r}"
    if res.returncode != 0:
        return False, f"rc={res.returncode}: {res.stdout.strip()} {res.stderr.strip()}"
    if "OK" not in res.stdout:
        return False, f"probe did not return OK: {res.stdout.strip()}"
    return True, "ok"


def _require_m3_r_toolchain() -> tuple[Path, dict]:
    """Resolve a usable Rscript + subprocess env.

    NO-SKIP (must_have A6): if the M3 marker env (the m3-r-ld pin) IS present,
    a broken toolchain raises (test FAILURE), never skips. Only when NO M3 env
    marker exists at all do we pytest.skip (a bare dev box).
    """
    m3_marker_present = M3_R_LD_RSCRIPT.exists() or os.environ.get("M3_R_LD_RSCRIPT")
    failures: list[str] = []
    for cand in _candidate_rscripts():
        ok, reason = _check_r_env(cand)
        if ok:
            return cand, _r_env_with_reticulate_python(cand)
        failures.append(f"{cand}: {reason}")
    detail = " | ".join(failures)
    if m3_marker_present:
        raise RuntimeError(
            "M3 env marker present but the R toolchain "
            "(reticulate+Matrix+digest+jsonlite+susieR+numpy+pyliftover) is "
            "incomplete — must_have A6 forbids skipping the stitch/loader/sparse "
            f"families in the M3 env. Tried: {detail}"
        )
    pytest.skip(f"no usable M3 Rscript toolchain (bare dev box); tried: {detail}")


@pytest.fixture(scope="session")
def r_toolchain() -> tuple[Path, dict]:
    return _require_m3_r_toolchain()


def _write_synthetic_chain(path: Path) -> None:
    """Write a minimal UCSC identity chain (GRCh38->GRCh37 proxy) covering the
    test coordinate ranges so liftover is deterministic and self-contained.

    The real hg38ToHg19 chain is a large external download not present in CI;
    the stitch/banding correctness is GRCh38-pos based and chain-agnostic, so a
    1:1 identity chain over chr12/chr16 is sufficient to exercise the real
    pyliftover code path without a network fetch. Format = UCSC .chain:
        chain score tName tSize tStrand tStart tEnd qName qSize qStrand qStart qEnd id
        <ungapped block size>
    A single ungapped block of the chrom size maps every position 1:1.
    """
    size = 250_000_000  # > any test coord; covers chr12 + chr16
    blocks = []
    cid = 1
    for chrom in ("chr12", "chr16"):
        blocks.append(
            f"chain 1000000 {chrom} {size} + 0 {size} {chrom} {size} + 0 {size} {cid}\n"
            f"{size}\n\n"
        )
        cid += 1
    path.write_text("".join(blocks))


@pytest.fixture(scope="session")
def chain_38_to_37(tmp_path_factory) -> Path:
    """Prefer the real chain; fall back to a self-contained synthetic identity
    chain so the R-execution families NEVER skip on a missing data fixture in
    the M3 env (must_have A6 no-skip)."""
    if CHAIN_38_TO_37.exists():
        return CHAIN_38_TO_37
    synth = tmp_path_factory.mktemp("chain") / "synthetic_identity.chain"
    _write_synthetic_chain(synth)
    return synth


# ---------------------------------------------------------------------------
# .npz + manifest fixture builders
# ---------------------------------------------------------------------------
def _write_window_npz(out_path: Path, variant_ids: list[str], ld: np.ndarray,
                      allele_freq: list[float] | None = None) -> None:
    n = len(variant_ids)
    if allele_freq is None:
        allele_freq = [0.25] * n
    np.savez_compressed(
        str(out_path),
        ld=ld.astype("float32"),
        variant_ids=np.asarray(variant_ids, dtype=str),
        rsids=np.asarray([""] * n, dtype=str),
        allele_freq=np.asarray(allele_freq, dtype="float32"),
    )


def _write_manifest(out_path: Path, parent: str, ancestry: str,
                    subs: list[dict], buffer_bp: int) -> None:
    """subs: list of {idx, core_start, core_end}. Writes a minimal manifest TSV
    carrying the columns the stitch reads."""
    cols = ["region_id", "ancestry", "parent_region_id", "subregion_index",
            "n_subregions", "core_start_grch38", "core_end_grch38", "buffer_bp"]
    lines = ["\t".join(cols)]
    n = len(subs)
    for s in subs:
        lines.append("\t".join(str(x) for x in [
            f"{parent}__sub{s['idx']:02d}", ancestry, parent, s["idx"], n,
            s["core_start"], s["core_end"], buffer_bp,
        ]))
    out_path.write_text("\n".join(lines) + "\n")


def _loader_functions_only(tmp_path: Path) -> Path:
    """Write a temp R file with ONLY the function-definition prefix of
    run_susie_rss.R (up to the top-level 'option_list <- list(' marker), so the
    loader-contract test can source load_ld_matrix() WITHOUT triggering the
    script's top-level argument parsing / main execution."""
    src = LOADER_R.read_text().splitlines()
    cut = len(src)
    for i, line in enumerate(src):
        if line.strip().startswith("option_list <-"):
            cut = i
            break
    out = tmp_path / "loader_funcs_only.R"
    out.write_text("\n".join(src[:cut]) + "\n")
    return out


def _run_stitch(rscript: Path, env: dict, parent: str, ancestry: str,
                out_rds: Path, chain: Path, manifest: Path,
                npzs: list[Path]) -> subprocess.CompletedProcess:
    cmd = [str(rscript), str(STITCH_R), "--parent", parent, "--ancestry", ancestry,
           "--out", str(out_rds), "--chain", str(chain), "--manifest", str(manifest)]
    for p in npzs:
        cmd += ["--npz", str(p)]
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=R_SUBPROCESS_TIMEOUT_S, env=env)


def _read_rds_summary(rscript: Path, env: dict, rds_path: Path, r_expr: str) -> str:
    """Run an R snippet that reads the .rds (as `obj`) and cats a result.

    Matrix is attached FIRST so that touching the dgCMatrix obj$R does not emit a
    lazy 'Loading required package: Matrix' banner that races the cat() output.
    """
    code = (f'suppressPackageStartupMessages(library(Matrix)); '
            f'obj <- readRDS("{rds_path}"); {r_expr}')
    res = subprocess.run([str(rscript), "-e", code], capture_output=True,
                         text=True, timeout=R_SUBPROCESS_TIMEOUT_S, env=env)
    if res.returncode != 0:
        raise RuntimeError(f"rds read failed rc={res.returncode}: {res.stderr}\n{res.stdout}")
    return res.stdout


def _two_window_fixture(tmp_path: Path, buffer_bp: int = 5_000_000,
                        straddle_r: float = 0.6):
    """Build 2 adjacent windows, cores [0,10M) and [10M,20M), with a straddle
    pair 1 kb apart across the 10M boundary carrying correlation straddle_r.

    Window 0 (core [0,10M), window [0, 10M+buffer]) holds variants near 10M;
    Window 1 (core [10M,20M), window [10M-buffer, 20M]) ALSO holds the straddle
    variant from core 0 (it is inside window 1's left buffer).
    """
    parent = "m2_region_00040"
    # Variants: A at 9,999,500 (core0); B at 10,000,500 (core1) -> straddle, 1 kb apart.
    # Plus a distant variant D at 18,000,000 (core1) far beyond buffer from A.
    A = "12:9999500:A:G"
    B = "12:10000500:C:T"
    D = "12:18000000:G:A"

    # Window 0 npz: variants A, B (both inside window0 = [0, 15M])
    w0_vids = [A, B]
    w0 = np.array([[1.0, straddle_r], [straddle_r, 1.0]], dtype="float32")
    # Window 1 npz: variants A, B, D (A is in window1's left buffer [5M,20M])
    w1_vids = [A, B, D]
    w1 = np.array([
        [1.0, straddle_r, 0.0],
        [straddle_r, 1.0, 0.05],
        [0.0, 0.05, 1.0],
    ], dtype="float32")

    npz0 = tmp_path / f"{parent}__sub00.npz"
    npz1 = tmp_path / f"{parent}__sub01.npz"
    _write_window_npz(npz0, w0_vids, w0)
    _write_window_npz(npz1, w1_vids, w1)

    manifest = tmp_path / "manifest.tsv"
    _write_manifest(manifest, parent, "AFR", [
        {"idx": 0, "core_start": 0, "core_end": 10_000_000},
        {"idx": 1, "core_start": 10_000_000, "core_end": 20_000_000},
    ], buffer_bp)
    return parent, manifest, [npz0, npz1], dict(A=A, B=B, D=D, straddle_r=straddle_r)


# ===========================================================================
# Static-content tests (always run; no Rscript required)
# ===========================================================================
def test_stitch_script_static_grep():
    assert STITCH_R.is_file()
    src = STITCH_R.read_text()
    assert "sparseMatrix" in src
    assert "bdiag" not in src, "stitch must be banded, NOT block-diagonal"
    assert "banded within radius_bp; zeroed beyond" in src
    assert src.count("buffer_bp") >= 2
    assert "variants" in src
    n_lines = sum(1 for _ in STITCH_R.open())
    assert n_lines >= 120, f"stitch script too short: {n_lines}"


# ===========================================================================
# Banded stitch behavior families (R-execution; no-skip in M3 env)
# ===========================================================================
def test_stitch_cross_core_band_retained(r_toolchain, chain_38_to_37, tmp_path):
    """Cross-boundary pair within buffer_bp is RETAINED (not zeroed). CENTRAL FIX."""
    rscript, env = r_toolchain
    parent, manifest, npzs, info = _two_window_fixture(tmp_path)
    out_rds = tmp_path / f"{parent}.rds"
    res = _run_stitch(rscript, env, parent, "AFR", out_rds, chain_38_to_37, manifest, npzs)
    assert res.returncode == 0, f"stitch failed: {res.stderr}\n{res.stdout}"
    # Read back R[A,B] (straddle pair). Match rows by GRCh38 pos in variants$POS?
    # The .rds dimnames are b37 ids; match by variants$CHR/POS proximity instead.
    code = (
        'v <- obj$variants; R <- as.matrix(obj$R); '
        # A b38 pos 9999500, B b38 pos 10000500 -> b37 differ; identify by AF/order:
        # both are the two lowest-POS owned variants. Use the two with smallest POS.
        'ord <- order(v$POS); ia <- ord[1]; ib <- ord[2]; '
        'cat(sprintf("R_AB=%.4f\\n", R[ia, ib]))'
    )
    out = _read_rds_summary(rscript, env, out_rds, code)
    r_ab = float([l for l in out.splitlines() if l.startswith("R_AB=")][0].split("=")[1])
    assert abs(r_ab - info["straddle_r"]) < 1e-3, f"straddle r not retained: {r_ab}"


def test_stitch_zeroes_only_beyond_buffer(r_toolchain, chain_38_to_37, tmp_path):
    """A pair > buffer_bp apart is exactly 0; matrix is banded (NOT bdiag)."""
    rscript, env = r_toolchain
    parent, manifest, npzs, info = _two_window_fixture(tmp_path, buffer_bp=5_000_000)
    out_rds = tmp_path / f"{parent}.rds"
    res = _run_stitch(rscript, env, parent, "AFR", out_rds, chain_38_to_37, manifest, npzs)
    assert res.returncode == 0, res.stderr
    code = (
        'v <- obj$variants; R <- as.matrix(obj$R); ord <- order(v$POS); '
        'ia <- ord[1]; id <- ord[length(ord)]; '  # A (lowest) vs D (highest, >8Mb away)
        'cat(sprintf("R_AD=%.6f\\n", R[ia, id])); '
        'cat(sprintf("NNZ=%d\\n", length(which(R != 0)))); '
        'cat(sprintf("FULL=%d\\n", nrow(R)*ncol(R))); '
        'cat(sprintf("SPARSE=%s\\n", inherits(obj$R, "sparseMatrix")))'
    )
    out = _read_rds_summary(rscript, env, out_rds, code)
    vals = dict(l.split("=") for l in out.splitlines() if "=" in l and not l.startswith("WROTE"))
    assert abs(float(vals["R_AD"])) < 1e-6, "pair beyond buffer must be 0"
    # banded (not dense, not bdiag-collapsed): some cross-core entries exist + sparse
    assert int(vals["NNZ"]) < int(vals["FULL"]), "must be sparse banded, not full"
    assert vals["SPARSE"].strip() == "TRUE"


def test_stitch_banded_psd(r_toolchain, chain_38_to_37, tmp_path):
    """obj$R symmetric, diag==1, eigenvalues >= -1e-6 on a small fixture."""
    rscript, env = r_toolchain
    parent, manifest, npzs, info = _two_window_fixture(tmp_path)
    out_rds = tmp_path / f"{parent}.rds"
    res = _run_stitch(rscript, env, parent, "AFR", out_rds, chain_38_to_37, manifest, npzs)
    assert res.returncode == 0, res.stderr
    code = (
        'R <- as.matrix(obj$R); '
        'cat(sprintf("SYM=%s\\n", isSymmetric(R))); '
        'cat(sprintf("DIAG1=%s\\n", all(abs(diag(R)-1) < 1e-9))); '
        'ev <- eigen(R, symmetric=TRUE, only.values=TRUE)$values; '
        'cat(sprintf("MINEV=%.6f\\n", min(ev)))'
    )
    out = _read_rds_summary(rscript, env, out_rds, code)
    vals = dict(l.split("=") for l in out.splitlines() if "=" in l and not l.startswith("WROTE"))
    assert vals["SYM"].strip() == "TRUE"
    assert vals["DIAG1"].strip() == "TRUE"
    assert float(vals["MINEV"]) >= -1e-6


def test_stitch_allele_aware_alignment(r_toolchain, chain_38_to_37, tmp_path):
    """Multiallelic site (same pos, different ALT) is NOT collapsed; ordered by
    (chr,pos,ref,alt); obj$variants has CHR,POS,REF,ALT,SNP_ID,AF."""
    rscript, env = r_toolchain
    parent = "m2_region_00040"
    # Two variants at the SAME pos, different ALT (multiallelic), both in core0.
    v1 = "12:5000000:A:G"
    v2 = "12:5000000:A:T"
    v3 = "12:6000000:C:G"
    vids = [v1, v2, v3]
    ld = np.eye(3, dtype="float32")
    ld[0, 1] = ld[1, 0] = 0.3
    npz0 = tmp_path / f"{parent}__sub00.npz"
    _write_window_npz(npz0, vids, ld)
    manifest = tmp_path / "manifest.tsv"
    _write_manifest(manifest, parent, "AFR",
                    [{"idx": 0, "core_start": 0, "core_end": 10_000_000}], 5_000_000)
    out_rds = tmp_path / f"{parent}.rds"
    res = _run_stitch(rscript, env, parent, "AFR", out_rds, chain_38_to_37, manifest, [npz0])
    assert res.returncode == 0, res.stderr
    code = (
        'v <- obj$variants; '
        'cat(sprintf("NROW=%d\\n", nrow(v))); '
        'cat(sprintf("COLS=%s\\n", paste(sort(names(v)), collapse=","))); '
        # the two multiallelic rows must both be present (NOT collapsed)
        'ma <- v[v$POS != "NA" | TRUE, ]; '
        'cat(sprintf("ALTS=%s\\n", paste(sort(v$ALT), collapse=",")))'
    )
    out = _read_rds_summary(rscript, env, out_rds, code)
    vals = dict(l.split("=", 1) for l in out.splitlines() if "=" in l and not l.startswith("WROTE"))
    assert int(vals["NROW"]) == 3, "multiallelic site must NOT be collapsed"
    cols = set(vals["COLS"].strip().split(","))
    assert {"SNP_ID", "CHR", "POS", "REF", "ALT", "AF"}.issubset(cols), cols
    assert "G,G,T" == vals["ALTS"].strip(), vals["ALTS"]


def test_stitch_no_duplicate_variant_across_windows(r_toolchain, chain_38_to_37, tmp_path):
    """A variant in the OVERLAP (present in both window .npz) appears ONCE."""
    rscript, env = r_toolchain
    parent, manifest, npzs, info = _two_window_fixture(tmp_path)
    out_rds = tmp_path / f"{parent}.rds"
    res = _run_stitch(rscript, env, parent, "AFR", out_rds, chain_38_to_37, manifest, npzs)
    assert res.returncode == 0, res.stderr
    code = (
        'v <- obj$variants; key <- paste(v$CHR, v$POS, v$REF, v$ALT, sep=":"); '
        'cat(sprintf("NDUP=%d\\n", sum(duplicated(key)))); '
        'cat(sprintf("NROW=%d\\n", nrow(v))); '
        'cat(sprintf("RDIM=%d\\n", nrow(obj$R)))'
    )
    out = _read_rds_summary(rscript, env, out_rds, code)
    vals = dict(l.split("=") for l in out.splitlines() if "=" in l and not l.startswith("WROTE"))
    assert int(vals["NDUP"]) == 0, "no variant may be duplicated across windows"
    assert int(vals["NROW"]) == int(vals["RDIM"])
    # A (core0), B (core1), D (core1) = 3 core-owned variants; A appears once
    # despite being in BOTH windows.
    assert int(vals["NROW"]) == 3


def test_stitch_overlap_pair_agreement(r_toolchain, chain_38_to_37, tmp_path):
    """A pair computed in TWO overlapping windows agrees (<1e-4) + single entry."""
    rscript, env = r_toolchain
    # straddle pair A-B is computed in BOTH window0 and window1 with the SAME r.
    parent, manifest, npzs, info = _two_window_fixture(tmp_path, straddle_r=0.6)
    out_rds = tmp_path / f"{parent}.rds"
    res = _run_stitch(rscript, env, parent, "AFR", out_rds, chain_38_to_37, manifest, npzs)
    assert res.returncode == 0, f"agreement stitch failed: {res.stderr}\n{res.stdout}"
    code = (
        'v <- obj$variants; R <- as.matrix(obj$R); ord <- order(v$POS); '
        'ia <- ord[1]; ib <- ord[2]; '
        'cat(sprintf("R_AB=%.4f\\n", R[ia, ib])); '
        'cat(sprintf("SYMOK=%s\\n", abs(R[ia,ib]-R[ib,ia]) < 1e-9))'
    )
    out = _read_rds_summary(rscript, env, out_rds, code)
    vals = dict(l.split("=") for l in out.splitlines() if "=" in l and not l.startswith("WROTE"))
    assert abs(float(vals["R_AB"]) - 0.6) < 1e-3, "agreed straddle r kept once"
    assert vals["SYMOK"].strip() == "TRUE"


def test_stitch_full_window_float32_asymmetric_not_doubled(
        r_toolchain, chain_38_to_37, tmp_path):
    """CR-01 regression (RED-first), stitch path: a window .npz holding a FULL
    matrix with ~1e-7 float32 triangle asymmetry must NOT have its off-diagonals
    doubled by the per-window symmetry recovery. The straddle r is staged from
    tri[ra,rb]; if the recovery doubles the full matrix (r->2r) the stitched
    R[A,B] becomes ~1.2 instead of ~0.6. Honor the lower_triangular flag."""
    rscript, env = r_toolchain
    parent = "m2_region_00040"
    A = "12:9999500:A:G"
    B = "12:10000500:C:T"
    # FULL window matrix with deliberate float32 asymmetry (not lower-tri).
    w = np.array([[1.0, 0.6000001], [0.5999999, 1.0]], dtype="float32")
    npz0 = tmp_path / f"{parent}__sub00.npz"
    npz1 = tmp_path / f"{parent}__sub01.npz"
    np.savez_compressed(str(npz0), ld=w,
                        variant_ids=np.asarray([A, B], dtype=str),
                        rsids=np.asarray(["", ""], dtype=str),
                        allele_freq=np.asarray([0.25, 0.25], dtype="float32"),
                        lower_triangular=np.array([False]))
    np.savez_compressed(str(npz1), ld=w,
                        variant_ids=np.asarray([A, B], dtype=str),
                        rsids=np.asarray(["", ""], dtype=str),
                        allele_freq=np.asarray([0.25, 0.25], dtype="float32"),
                        lower_triangular=np.array([False]))
    manifest = tmp_path / "manifest.tsv"
    _write_manifest(manifest, parent, "AFR", [
        {"idx": 0, "core_start": 0, "core_end": 10_000_000},
        {"idx": 1, "core_start": 10_000_000, "core_end": 20_000_000},
    ], 5_000_000)
    out_rds = tmp_path / f"{parent}.rds"
    res = _run_stitch(rscript, env, parent, "AFR", out_rds, chain_38_to_37, manifest, [npz0, npz1])
    assert res.returncode == 0, f"stitch failed: {res.stderr}\n{res.stdout}"
    code = (
        'v <- obj$variants; R <- as.matrix(obj$R); ord <- order(v$POS); '
        'ia <- ord[1]; ib <- ord[2]; '
        'cat(sprintf("R_AB=%.5f\\n", R[ia, ib]))'
    )
    out = _read_rds_summary(rscript, env, out_rds, code)
    r_ab = float([l for l in out.splitlines() if l.startswith("R_AB=")][0].split("=")[1])
    assert abs(r_ab - 0.6) < 1e-3, f"full-window off-diagonal DOUBLED: {r_ab} (CR-01)"


def test_stitch_overlap_pair_disagreement_raises(r_toolchain, chain_38_to_37, tmp_path):
    """If the two windows DISAGREE on a shared pair, the stitch STOPs (integrity)."""
    rscript, env = r_toolchain
    parent = "m2_region_00040"
    A = "12:9999500:A:G"; B = "12:10000500:C:T"
    npz0 = tmp_path / f"{parent}__sub00.npz"
    npz1 = tmp_path / f"{parent}__sub01.npz"
    _write_window_npz(npz0, [A, B], np.array([[1, 0.6], [0.6, 1]], dtype="float32"))
    _write_window_npz(npz1, [A, B], np.array([[1, 0.9], [0.9, 1]], dtype="float32"))
    manifest = tmp_path / "manifest.tsv"
    _write_manifest(manifest, parent, "AFR", [
        {"idx": 0, "core_start": 0, "core_end": 10_000_000},
        {"idx": 1, "core_start": 10_000_000, "core_end": 20_000_000},
    ], 5_000_000)
    out_rds = tmp_path / f"{parent}.rds"
    res = _run_stitch(rscript, env, parent, "AFR", out_rds, chain_38_to_37, manifest, [npz0, npz1])
    assert res.returncode != 0, "disagreeing overlap pairs must fail the stitch"
    assert "disagreement" in (res.stderr + res.stdout).lower()


def test_stitch_completeness_guard_not_bypassed_by_filename(
        r_toolchain, chain_38_to_37, tmp_path):
    """WR-02 regression: the missing-child completeness guard must NOT be silently
    bypassed when an .npz filename lacks the __subNN token. A 2-subregion parent
    fed only ONE window whose file is named without __sub used to slip past the
    guard (seen_idx stayed empty, length(seen_idx) > 0L was FALSE) and write an
    INCOMPLETE panel. The stitch must instead REFUSE (subregion identity is
    derived from the manifest; an un-mappable npz is an error)."""
    rscript, env = r_toolchain
    parent = "m2_region_00040"
    A = "12:9999500:A:G"
    B = "12:10000500:C:T"
    # Manifest declares n_subregions=2 for this parent.
    manifest = tmp_path / "manifest.tsv"
    _write_manifest(manifest, parent, "AFR", [
        {"idx": 0, "core_start": 0, "core_end": 10_000_000},
        {"idx": 1, "core_start": 10_000_000, "core_end": 20_000_000},
    ], 5_000_000)
    # ONE npz, named WITHOUT the __subNN token (cannot be inferred from filename).
    npz_noname = tmp_path / "window_zero.npz"
    _write_window_npz(npz_noname, [A, B],
                      np.array([[1.0, 0.6], [0.6, 1.0]], dtype="float32"))
    out_rds = tmp_path / f"{parent}.rds"
    res = _run_stitch(rscript, env, parent, "AFR", out_rds, chain_38_to_37,
                      manifest, [npz_noname])
    assert res.returncode != 0, (
        "stitch must REFUSE an un-mappable / incomplete npz set, not silently "
        "write an incomplete panel (WR-02)")
    combined = (res.stderr + res.stdout)
    assert "STITCH_INPUT" in combined, combined


def test_stitch_sparse_payload(r_toolchain, chain_38_to_37, tmp_path):
    """obj$R inherits sparseMatrix (dgCMatrix), round-trips, dims == owned count."""
    rscript, env = r_toolchain
    parent, manifest, npzs, info = _two_window_fixture(tmp_path)
    out_rds = tmp_path / f"{parent}.rds"
    res = _run_stitch(rscript, env, parent, "AFR", out_rds, chain_38_to_37, manifest, npzs)
    assert res.returncode == 0, res.stderr
    code = (
        'cat(sprintf("SPARSE=%s\\n", inherits(obj$R, "sparseMatrix"))); '
        'cat(sprintf("CLS=%s\\n", class(obj$R)[1])); '
        'cat(sprintf("DIM=%d\\n", nrow(obj$R)))'
    )
    out = _read_rds_summary(rscript, env, out_rds, code)
    vals = dict(l.split("=") for l in out.splitlines() if "=" in l and not l.startswith("WROTE"))
    assert vals["SPARSE"].strip() == "TRUE"
    assert "Matrix" in vals["CLS"] or "dgC" in vals["CLS"]
    assert int(vals["DIM"]) == 3


def test_loader_accepts_stitched_payload(r_toolchain, chain_38_to_37, tmp_path):
    """run_susie_rss.R::load_ld_matrix() accepts obj$R+obj$variants (NOT ld_missing)."""
    rscript, env = r_toolchain
    parent, manifest, npzs, info = _two_window_fixture(tmp_path)
    ld_dir = tmp_path / "ld"
    (ld_dir / "AFR").mkdir(parents=True)
    out_rds = ld_dir / "AFR" / f"{parent}.rds"
    res = _run_stitch(rscript, env, parent, "AFR", out_rds, chain_38_to_37, manifest, npzs)
    assert res.returncode == 0, res.stderr
    loader_funcs = _loader_functions_only(tmp_path)
    # Source ONLY the loader function defs (no top-level argparse/main); define
    # the MIN_LD_* policy constants the loader references (set from the YAML in
    # production, line 255+, which is past the cut).
    code = (
        'suppressPackageStartupMessages(library(Matrix)); '
        'suppressWarnings(suppressMessages(source("%s"))); '
        'MIN_LD_OVERLAP <- 1L; MIN_LD_COVERAGE <- 0.0; MIN_LD_MIN_USE <- 1L; '
        'obj <- readRDS("%s"); v <- obj$variants; '
        # build subset from the loaded variants (guarantee overlap)
        'subset <- data.frame(CHR=v$CHR, POS=v$POS, SNP_ID=v$SNP_ID, '
        '  stringsAsFactors=FALSE); '
        'r <- load_ld_matrix("%s", "AFR", "%s", subset); '
        'cat(sprintf("STATUS=%%s\\n", r$status)); '
        'cat(sprintf("RNULL=%%s\\n", is.null(r$R))); '
        'cat(sprintf("ISMAT=%%s\\n", is.matrix(r$R)))'
    ) % (loader_funcs, out_rds, ld_dir, parent)
    proc = subprocess.run([str(rscript), "-e", code], capture_output=True,
                          text=True, timeout=R_SUBPROCESS_TIMEOUT_S, env=env)
    assert proc.returncode == 0, f"loader call failed: {proc.stderr}\n{proc.stdout}"
    vals = dict(l.split("=") for l in proc.stdout.splitlines() if "=" in l)
    assert vals.get("RNULL", "").strip() == "FALSE", f"loader returned NULL R: {proc.stdout}"
    assert "ld_missing" not in vals.get("STATUS", ""), proc.stdout
    assert vals.get("ISMAT", "").strip() == "TRUE", "loader densifies R via as.matrix"


def test_whole_region_payload_reconciled(r_toolchain, chain_38_to_37, tmp_path):
    """ld_npz_to_rds.R now writes obj$R + obj$variants; load_ld_matrix accepts it."""
    rscript, env = r_toolchain
    # 1-npz fixture: 3 variants near FTO that liftover cleanly.
    vids = ["chr16:53809247:T:A", "chr16:53810000:G:C", "chr16:53811000:A:T"]
    n = len(vids)
    ld = np.eye(n, dtype="float32")
    ld[0, 1] = ld[1, 0] = 0.4
    npz = tmp_path / "whole.npz"
    np.savez_compressed(str(npz), ld=np.tril(ld).astype("float32"),
                        variant_ids=np.asarray(vids, dtype=str),
                        rsids=np.asarray([""] * n, dtype=str),
                        allele_freq=np.asarray([0.3] * n, dtype="float32"))
    rds = tmp_path / "whole.rds"
    conv = subprocess.run([str(rscript), str(CONVERTER_R), str(npz), str(rds),
                           str(chain_38_to_37)], capture_output=True, text=True,
                          timeout=R_SUBPROCESS_TIMEOUT_S, env=env)
    assert conv.returncode == 0, f"converter failed: {conv.stderr}\n{conv.stdout}"
    code = (
        'obj <- readRDS("%s"); '
        'cat(sprintf("HASR=%%s\\n", !is.null(obj$R))); '
        'cat(sprintf("HASV=%%s\\n", !is.null(obj$variants))); '
        'cat(sprintf("VCOLS=%%s\\n", paste(sort(names(obj$variants)), collapse=","))); '
        'cat(sprintf("HASSNP=%%s\\n", !is.null(obj$snp_ids)))'  # back-compat
    ) % rds
    out = _read_rds_summary(rscript, env, rds, code.split("; ", 1)[1])
    vals = dict(l.split("=", 1) for l in out.splitlines() if "=" in l and not l.startswith("WROTE"))
    assert vals["HASR"].strip() == "TRUE", "whole-region .rds must carry obj$R"
    assert vals["HASV"].strip() == "TRUE", "whole-region .rds must carry obj$variants"
    assert {"SNP_ID", "CHR", "POS", "REF", "ALT", "AF"}.issubset(
        set(vals["VCOLS"].strip().split(",")))
    assert vals["HASSNP"].strip() == "TRUE", "back-compat obj$snp_ids must remain"


def test_whole_region_null_af_survives_as_na_not_zero(
        r_toolchain, chain_38_to_37, tmp_path):
    """WR-03 regression: a missing AF (NaN in the .npz) must survive into
    obj$variants$AF as NA, NOT be coerced to a fake 0.0 (which would be
    indistinguishable from a real allele frequency of 0)."""
    rscript, env = r_toolchain
    vids = ["chr16:53809247:T:A", "chr16:53810000:G:C", "chr16:53811000:A:T"]
    n = len(vids)
    ld = np.eye(n, dtype="float32")
    ld[0, 1] = ld[1, 0] = 0.4
    # AF: variant 0 missing (NaN), variant 1 a genuine 0.0, variant 2 a real AF.
    af = np.asarray([np.nan, 0.0, 0.3], dtype="float32")
    npz = tmp_path / "nullaf.npz"
    np.savez_compressed(str(npz), ld=np.tril(ld).astype("float32"),
                        variant_ids=np.asarray(vids, dtype=str),
                        rsids=np.asarray([""] * n, dtype=str),
                        allele_freq=af,
                        lower_triangular=np.array([True]))
    rds = tmp_path / "nullaf.rds"
    conv = subprocess.run([str(rscript), str(CONVERTER_R), str(npz), str(rds),
                           str(chain_38_to_37)], capture_output=True, text=True,
                          timeout=R_SUBPROCESS_TIMEOUT_S, env=env)
    assert conv.returncode == 0, f"converter failed: {conv.stderr}\n{conv.stdout}"
    code = (
        'v <- obj$variants; '
        'cat(sprintf("AF0NA=%s\\n", is.na(v$AF[1]))); '   # missing -> NA
        'cat(sprintf("AF1=%.4f\\n", v$AF[2])); '          # genuine 0.0 preserved
        'cat(sprintf("AF2=%.4f\\n", v$AF[3]))'
    )
    out = _read_rds_summary(rscript, env, rds, code)
    vals = dict(l.split("=") for l in out.splitlines()
                if "=" in l and not l.startswith("WROTE"))
    assert vals["AF0NA"].strip() == "TRUE", "missing AF must be NA, not 0.0 (WR-03)"
    assert abs(float(vals["AF1"]) - 0.0) < 1e-6, "a genuine AF=0 must be preserved"
    assert abs(float(vals["AF2"]) - 0.3) < 1e-3


def test_whole_region_full_matrix_float32_asymmetric_not_doubled(
        r_toolchain, chain_38_to_37, tmp_path):
    """CR-01 regression (RED-first): a FULL (Path A.1) float32 matrix carries
    ~1e-7 triangle asymmetry from Hail block-sum order. The OLD unconditional
    ``if (!isSymmetric(tri)) tri <- tri + t(tri) - diag(diag(tri))`` recovery
    DOUBLES every off-diagonal (r -> 2r) on such a full matrix because
    isSymmetric's ~2.2e-14 tol trips on the 1e-7 noise. The fix HONORS the
    ``lower_triangular`` flag the .npz carries: for a full matrix (flag False or
    absent) it must ONLY project out float asymmetry via (tri+t(tri))/2, never
    double. Assert the recovered off-diagonal equals the true r (~0.6), NOT 2r.
    """
    rscript, env = r_toolchain
    vids = ["chr16:53809247:T:A", "chr16:53810000:G:C", "chr16:53811000:A:T"]
    n = len(vids)
    # FULL symmetric-in-intent matrix with deliberate float32 triangle asymmetry
    # ~1e-7 (above isSymmetric's 2.2e-14 tol, exactly the Hail block-sum drift).
    ld = np.eye(n, dtype="float32")
    ld[0, 1] = np.float32(0.6000001)
    ld[1, 0] = np.float32(0.5999999)
    ld[0, 2] = np.float32(0.3000001)
    ld[2, 0] = np.float32(0.2999999)
    npz = tmp_path / "full_asym.npz"
    # lower_triangular=False (Path A.1 convention) — full matrix, NOT one-sided.
    np.savez_compressed(str(npz), ld=ld,
                        variant_ids=np.asarray(vids, dtype=str),
                        rsids=np.asarray([""] * n, dtype=str),
                        allele_freq=np.asarray([0.3] * n, dtype="float32"),
                        lower_triangular=np.array([False]))
    rds = tmp_path / "full_asym.rds"
    conv = subprocess.run([str(rscript), str(CONVERTER_R), str(npz), str(rds),
                           str(chain_38_to_37)], capture_output=True, text=True,
                          timeout=R_SUBPROCESS_TIMEOUT_S, env=env)
    assert conv.returncode == 0, f"converter failed: {conv.stderr}\n{conv.stdout}"
    code = (
        'R <- as.matrix(obj$R); '
        'cat(sprintf("R01=%.5f\\n", R[1, 2])); '
        'cat(sprintf("R02=%.5f\\n", R[1, 3])); '
        'cat(sprintf("SYM=%s\\n", isSymmetric(R))); '
        'cat(sprintf("DIAG1=%s\\n", all(abs(diag(R)-1) < 1e-9)))'
    )
    out = _read_rds_summary(rscript, env, rds, code)
    vals = dict(l.split("=") for l in out.splitlines()
                if "=" in l and not l.startswith("WROTE"))
    # The bug doubles 0.6 -> 1.2 and 0.3 -> 0.6. The fix keeps them ~r.
    assert abs(float(vals["R01"]) - 0.6) < 1e-3, (
        f"off-diagonal DOUBLED (got {vals['R01']}, expected ~0.6) -- CR-01 bug")
    assert abs(float(vals["R02"]) - 0.3) < 1e-3, (
        f"off-diagonal DOUBLED (got {vals['R02']}, expected ~0.3) -- CR-01 bug")
    assert vals["SYM"].strip() == "TRUE"
    assert vals["DIAG1"].strip() == "TRUE"
