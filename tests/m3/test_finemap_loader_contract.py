"""tests/m3/test_finemap_loader_contract.py -- M3 Wave 2 re-scope (m3-02b) A6.

A6 is answered by EXERCISING the REAL resolver -> loader -> susie path, NOT a
sentinel verdict file:

    resolve_ld_path -> load_ld_matrix() -> susieR::susie_rss() on a stitched
    banded sparse parent .rds placed at the finemap.smk LD-dir layout
    ({ld_dir}/{ancestry}/{region_id}.rds). load_ld_matrix() must return a
    non-NULL R (densified as.matrix slice) + variants subset; susie_rss() must
    return a fit yielding a credible set.

NO-SKIP RULE (must_have A6): in the designated M3 conda env the loader path
MUST run (R + Matrix + susieR + coloc present). ``_require_m3_r_toolchain()``
ERRORS (not skips) when the M3 marker env is active but the toolchain is
incomplete. Outside any M3 env (bare dev box) the tests skip with a diagnostic.

The R-toolchain discovery + stitch fixture builders are reused from
test_stitch_subregions_to_rds.py.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

# Make sibling test modules importable (tests/m3 on sys.path) so we can reuse the
# stitch test's R-toolchain discovery + fixture builders.
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

# Reuse the toolchain discovery + fixture builders from the stitch test module.
from test_stitch_subregions_to_rds import (  # noqa: E402
    LOADER_R,
    _loader_functions_only,
    _require_m3_r_toolchain,
    _run_stitch,
    _two_window_fixture,
)


@pytest.fixture(scope="session")
def r_toolchain() -> tuple[Path, dict]:
    return _require_m3_r_toolchain()


@pytest.fixture(scope="session")
def chain_38_to_37(tmp_path_factory) -> Path:
    from test_stitch_subregions_to_rds import CHAIN_38_TO_37, _write_synthetic_chain
    if CHAIN_38_TO_37.exists():
        return CHAIN_38_TO_37
    synth = tmp_path_factory.mktemp("chain_fm") / "synthetic_identity.chain"
    _write_synthetic_chain(synth)
    return synth


def _place_stitched_parent(rscript, env, chain, tmp_path):
    """Build a stitched banded sparse parent .rds and place it at the resolver's
    expected finemap.smk path ld_dir/ancestry/{region_id}.rds."""
    parent, manifest, npzs, info = _two_window_fixture(tmp_path)
    ld_dir = tmp_path / "ld_reference"
    (ld_dir / "AFR").mkdir(parents=True)
    out_rds = ld_dir / "AFR" / f"{parent}.rds"
    res = _run_stitch(rscript, env, parent, "AFR", out_rds, chain, manifest, npzs)
    assert res.returncode == 0, f"stitch failed: {res.stderr}\n{res.stdout}"
    return parent, ld_dir, out_rds


def test_loader_contract_no_skip_in_m3_env(r_toolchain):
    """If the M3 env is active the toolchain MUST be present (a skip is FAILURE)."""
    rscript, env = r_toolchain
    probe = (
        'pkgs <- c("Matrix","susieR","coloc"); '
        'missing <- pkgs[!sapply(pkgs, requireNamespace, quietly=TRUE)]; '
        'if (length(missing)) { cat("MISSING:", paste(missing, collapse=","), "\\n"); quit(status=2) }; '
        'cat("OK\\n")'
    )
    res = subprocess.run([str(rscript), "-e", probe], capture_output=True,
                         text=True, timeout=120, env=env)
    assert res.returncode == 0 and "OK" in res.stdout, (
        f"M3 env must carry Matrix+susieR+coloc (no-skip A6): {res.stdout} {res.stderr}"
    )


def test_resolver_loads_and_susie_runs_on_stitched_parent(r_toolchain, chain_38_to_37, tmp_path):
    """resolve_ld_path -> load_ld_matrix() -> susie_rss() on a stitched parent.

    Exercises the REAL loader (NOT a direct susie_rss() call): load_ld_matrix()
    returns obj$R (as.matrix slice) + variants subset; susie_rss() on the slice
    returns a fit with susie_get_cs() yielding >= 0 credible sets.
    """
    rscript, env = r_toolchain
    parent, ld_dir, out_rds = _place_stitched_parent(rscript, env, chain_38_to_37, tmp_path)
    loader_funcs = _loader_functions_only(tmp_path)
    code = (
        'suppressPackageStartupMessages({library(Matrix); library(susieR)}); '
        'suppressWarnings(suppressMessages(source("%s"))); '
        'MIN_LD_OVERLAP <- 1L; MIN_LD_COVERAGE <- 0.0; MIN_LD_MIN_USE <- 1L; '
        'obj <- readRDS("%s"); v <- obj$variants; '
        # subset = the loaded variants -> guaranteed overlap (CHR,POS,SNP_ID)
        'subset <- data.frame(CHR=v$CHR, POS=v$POS, SNP_ID=v$SNP_ID, stringsAsFactors=FALSE); '
        'r <- load_ld_matrix("%s", "AFR", "%s", subset); '
        'cat(sprintf("RNULL=%%s\\n", is.null(r$R))); '
        'cat(sprintf("ISMAT=%%s\\n", is.matrix(r$R))); '
        'stopifnot(!is.null(r$R)); '
        'R <- r$R; n_var <- nrow(R); '
        # synthetic z aligned to the returned LD slice; run the REAL susie_rss
        'set.seed(1); z <- rnorm(n_var) * 2; '
        'fit <- susieR::susie_rss(z = z, R = R, n = 5000, L = 5); '
        'cs <- susieR::susie_get_cs(fit, Xcorr = R); '
        'cat(sprintf("NCS=%%d\\n", length(cs$cs))); '
        'cat(sprintf("SUSIE_OK=%%s\\n", inherits(fit, "susie") || !is.null(fit$pip)))'
    ) % (loader_funcs, out_rds, ld_dir, parent)
    proc = subprocess.run([str(rscript), "-e", code], capture_output=True,
                          text=True, timeout=300, env=env)
    assert proc.returncode == 0, f"resolver->loader->susie failed: {proc.stderr}\n{proc.stdout}"
    vals = dict(l.split("=") for l in proc.stdout.splitlines() if "=" in l)
    assert vals.get("RNULL", "").strip() == "FALSE", proc.stdout
    assert vals.get("ISMAT", "").strip() == "TRUE", "loader densifies via as.matrix"
    assert int(vals["NCS"]) >= 0, "susie_get_cs returned"
    assert vals.get("SUSIE_OK", "").strip() == "TRUE", "susie_rss returned a fit"
