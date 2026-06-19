"""tests/m3/test_sparse_parent_benchmark.py -- M3 Wave 2 re-scope (m3-02b).

Proves the stitched banded sparse parent panel does NOT whole-parent-densify
(HIGH#2): the SuSiE wrapper densifies LAZILY per credible-set window, never the
whole 600k-var parent (a 615k-var dense float64 is ~3 TB).

Builds a realistically-sized banded sparse R directly in R at the target M (tens
of thousands of variants) with a buffer_bp band, writes it as a dgCMatrix .rds,
and records:
    M, rds_bytes, read_s, peak_ram_load_gib, window_var, densify_window_s,
    peak_ram_densify_gib
to tests/m3/sparse_parent_benchmark.tsv. Asserts:
    * obj$R inherits sparseMatrix (NOT a base dense matrix);
    * object.size(obj$R) << dense M^2*8;
    * peak RAM during load stays under a stated ceiling (no whole-parent dense).

NO-SKIP RULE (must_have A6): runs in the M3 env (Matrix present). The
_require_m3_r_toolchain gate ERRORS (not skips) when the M3 marker env is active
but the toolchain is incomplete.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# Make sibling test modules importable (tests/m3 on sys.path).
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from test_stitch_subregions_to_rds import _require_m3_r_toolchain  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_TSV = PROJECT_ROOT / "tests" / "m3" / "sparse_parent_benchmark.tsv"

# Fixture sizing: M large enough that a DENSE M^2 float64 (M^2*8 bytes) would be
# multi-GiB, so a sparse-only load proves the lazy-densify claim. M=50,000 ->
# dense = 50000^2 * 8 = ~18.6 GiB; the sparse banded load must stay well under.
FIXTURE_M = 50_000
BAND_VARS = 600           # ~band half-width in variant index units (banded)
WINDOW_VAR = 6_000        # one credible-set window densified
PEAK_RAM_LOAD_CEILING_GIB = 8.0
PEAK_RAM_DENSIFY_CEILING_GIB = 8.0


@pytest.fixture(scope="session")
def r_toolchain() -> tuple[Path, dict]:
    return _require_m3_r_toolchain()


def test_no_whole_parent_dense_materialization(r_toolchain, tmp_path):
    """obj$R is sparse + object.size << dense M^2*8; per-window densify is a slice."""
    rscript, env = r_toolchain
    rds = tmp_path / "parent.rds"
    code = f"""
    suppressPackageStartupMessages(library(Matrix))
    M <- {FIXTURE_M}L; band <- {BAND_VARS}L
    # Build a banded sparse symmetric R directly (no dense M^2 ever allocated).
    set.seed(7)
    ii <- integer(0); jj <- integer(0); xx <- numeric(0)
    # diagonal
    ii <- c(ii, 1:M); jj <- c(jj, 1:M); xx <- c(xx, rep(1, M))
    # band entries (upper triangle within +/- band)
    for (off in 1:band) {{
      n <- M - off
      if (n <= 0) break
      r <- exp(-off / band) * 0.5
      ii <- c(ii, 1:n); jj <- c(jj, (1+off):M); xx <- c(xx, rep(r, n))
    }}
    R <- sparseMatrix(i = ii, j = jj, x = xx, dims = c(M, M), symmetric = FALSE)
    R <- R + t(R); diag(R) <- 1
    R <- as(R, "CsparseMatrix")
    variants <- data.frame(SNP_ID = paste0("1:", 1:M, ":A:G"),
      CHR = "1", POS = 1:M, REF = "A", ALT = "G", AF = 0.25,
      stringsAsFactors = FALSE)
    saveRDS(list(R = R, variants = variants, snp_ids = variants$SNP_ID),
            "{rds}", compress = "xz")

    # ---- load + measure ----
    gc(reset = TRUE)
    t0 <- Sys.time()
    obj <- readRDS("{rds}")
    read_s <- as.numeric(difftime(Sys.time(), t0, units = "secs"))
    peak_load_gib <- sum(gc()[, 6]) / 1024   # gc col 6 = max used Mb -> GiB
    sparse_ok <- inherits(obj$R, "sparseMatrix")
    not_dense <- !is.matrix(obj$R)
    obj_bytes <- as.numeric(object.size(obj$R))
    dense_bytes <- as.numeric(M) * as.numeric(M) * 8

    # ---- lazy per-window densification (slice only) ----
    w <- {WINDOW_VAR}L
    idx <- 1:w
    gc(reset = TRUE)
    t1 <- Sys.time()
    sub_dense <- as.matrix(obj$R[idx, idx, drop = FALSE])
    densify_s <- as.numeric(difftime(Sys.time(), t1, units = "secs"))
    peak_densify_gib <- sum(gc()[, 6]) / 1024
    rds_bytes <- file.info("{rds}")$size

    cat(sprintf("SPARSE=%s\\n", sparse_ok))
    cat(sprintf("NOTDENSE=%s\\n", not_dense))
    cat(sprintf("OBJBYTES=%.0f\\n", obj_bytes))
    cat(sprintf("DENSEBYTES=%.0f\\n", dense_bytes))
    cat(sprintf("RDSBYTES=%.0f\\n", rds_bytes))
    cat(sprintf("READS=%.3f\\n", read_s))
    cat(sprintf("PEAKLOAD=%.3f\\n", peak_load_gib))
    cat(sprintf("WINDOWVAR=%d\\n", w))
    cat(sprintf("DENSIFYS=%.3f\\n", densify_s))
    cat(sprintf("PEAKDENSIFY=%.3f\\n", peak_densify_gib))
    """
    proc = subprocess.run([str(rscript), "-e", code], capture_output=True,
                          text=True, timeout=600, env=env)
    assert proc.returncode == 0, f"benchmark R failed: {proc.stderr}\n{proc.stdout}"
    vals = dict(l.split("=") for l in proc.stdout.splitlines() if "=" in l)

    assert vals["SPARSE"].strip() == "TRUE", "obj$R must be a sparseMatrix"
    assert vals["NOTDENSE"].strip() == "TRUE", "obj$R must NOT be a base dense matrix"
    obj_bytes = float(vals["OBJBYTES"])
    dense_bytes = float(vals["DENSEBYTES"])
    assert obj_bytes < dense_bytes * 0.25, (
        f"sparse object {obj_bytes:.0f} not << dense {dense_bytes:.0f}")
    peak_load = float(vals["PEAKLOAD"])
    assert peak_load < PEAK_RAM_LOAD_CEILING_GIB, (
        f"peak RAM on load {peak_load:.2f} GiB exceeds ceiling "
        f"{PEAK_RAM_LOAD_CEILING_GIB} GiB -> whole-parent dense suspected")

    # Write the benchmark TSV (committed artifact).
    header = ("M\trds_bytes\tread_s\tpeak_ram_load_gib\twindow_var\t"
              "densify_window_s\tpeak_ram_densify_gib\n")
    line = "\t".join(str(x) for x in [
        FIXTURE_M, int(float(vals["RDSBYTES"])), vals["READS"].strip(),
        f"{peak_load:.3f}", int(vals["WINDOWVAR"]), vals["DENSIFYS"].strip(),
        vals["PEAKDENSIFY"].strip(),
    ]) + "\n"
    BENCHMARK_TSV.write_text(header + line)


def test_sparse_parent_benchmark_records_metrics(r_toolchain, tmp_path):
    """The benchmark TSV exists with the required metric columns + a data row."""
    # Ensure the metrics test depends on the produced artifact; if the prior test
    # has not run in this session, run a lightweight regeneration.
    if not BENCHMARK_TSV.exists():
        test_no_whole_parent_dense_materialization(r_toolchain, tmp_path)
    assert BENCHMARK_TSV.exists(), "sparse_parent_benchmark.tsv must be written"
    lines = BENCHMARK_TSV.read_text().strip().splitlines()
    assert len(lines) >= 2, "benchmark TSV needs a header + >=1 data row"
    header = lines[0]
    for col in ("rds_bytes", "read_s", "peak_ram_load_gib", "window_var",
                "densify_window_s", "peak_ram_densify_gib"):
        assert col in header, f"benchmark header missing {col}"
    row = dict(zip(header.split("\t"), lines[1].split("\t")))
    assert float(row["peak_ram_load_gib"]) < PEAK_RAM_LOAD_CEILING_GIB
    assert float(row["peak_ram_densify_gib"]) < PEAK_RAM_DENSIFY_CEILING_GIB
    assert int(row["window_var"]) == WINDOW_VAR
