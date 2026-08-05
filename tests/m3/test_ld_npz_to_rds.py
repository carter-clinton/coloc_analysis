"""tests/m3/test_ld_npz_to_rds.py -- M3 Wave 3 Task 1 converter pytest.

Covers the seven behaviors specified in the m3-03-W3 plan <behavior> block:

    1. test_npz_to_rds_round_trip   -- 50x50 symmetric LD .npz -> .rds; verify
                                       symmetric, dimnames present, dimensions match.
    2. test_chr_prefix_stripping    -- "chr16:..."  prefixed variant_ids land
                                       as "16:..." in .rds dimnames.
    3. test_grch38_to_grch37_liftover -- rs1558902 GRCh38 chr16:53809247 lifts
                                       to GRCh37 chr16:53803574 (dbSNP).
    4. test_rsid_preference_over_synthetic -- when rsid + chr:pos:ref:alt both
                                       populated, dimnames carry the rsid.
    5. test_failed_liftover_drops_variant -- variants whose IDs fail liftover
                                       are dropped; matrix dim reduces.
    6. test_provenance_json         -- .rds payload includes provenance with
                                       npz_path, chain_sha256, datetime,
                                       n_var_input, n_var_output.
    7. test_bm_to_npz_helper        -- src/python/bm_to_npz.py reads a synthetic
                                       Hail BlockMatrix and emits a valid .npz
                                       (graceful skip if Hail not installed).

Plus static-content sanity tests on the R script + Python helper (these run
without an R environment, ensuring CI flags surface even when m3-r-ld is
not built locally).

Environment discovery: the R-execution tests require an Rscript with
``reticulate``, ``Matrix``, ``digest``, ``jsonlite`` + Python ``numpy`` +
``pyliftover`` available. Order of preference:

    1. M3_R_LD_RSCRIPT environment variable (explicit override)
    2. /rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/Rscript (project pin)
    3. ``Rscript`` on PATH (must satisfy package check)

If no env satisfies the package check, the R-execution tests skip with a
diagnostic message naming exactly which packages are missing -- they do not
silently pass. Static structural tests still run.
"""
from __future__ import annotations

import json
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

# Shared contention-safe R-subprocess wall-clock budget (single source of truth in
# the ROOT tests/conftest.py — the bare ``conftest`` module pytest imports). Closes
# the m3-W2-stitch-rds-test-failures flake CLASS: this module's R/reticulate
# round-trips pay the same ~66s cold-start and previously used tight literal timeouts
# (60/60/180s) that flake under shared-node contention.
from conftest import R_SUBPROCESS_TIMEOUT_S  # noqa: E402


PROJECT_ROOT = Path(__file__).resolve().parents[2]
R_CONVERTER = PROJECT_ROOT / "src" / "scripts" / "ld_npz_to_rds.R"
BM_HELPER = PROJECT_ROOT / "src" / "python" / "bm_to_npz.py"
CHAIN_38_TO_37 = PROJECT_ROOT / "data" / "external" / "liftover" / "hg38ToHg19.over.chain.gz"


# ---------------------------------------------------------------------------
# R environment discovery (R-execution tests only)
# ---------------------------------------------------------------------------
def _candidate_rscripts() -> list[Path]:
    cands: list[Path] = []
    env = os.environ.get("M3_R_LD_RSCRIPT")
    if env:
        cands.append(Path(env))
    cands.append(Path("/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/Rscript"))
    on_path = shutil.which("Rscript")
    if on_path:
        cands.append(Path(on_path))
    # de-dup, preserve order
    seen: set[str] = set()
    out: list[Path] = []
    for c in cands:
        s = str(c.resolve()) if c.exists() else str(c)
        if s in seen:
            continue
        seen.add(s)
        out.append(c)
    return out


def _r_env(rscript: Path) -> dict:
    """Subprocess env for an Rscript run.

    Pin RETICULATE_PYTHON to the Rscript's sibling ``python`` so reticulate
    resolves the conda env that ships numpy + pyliftover, instead of an
    ephemeral uv-managed interpreter (which lacks pyliftover and forces the
    R-family tests to skip). Production invokes the converter from inside the
    m3-r-ld env where this binding already holds.
    """
    env = dict(os.environ)
    sibling_py = rscript.parent / "python"
    if sibling_py.exists():
        env.setdefault("RETICULATE_PYTHON", str(sibling_py))
    return env


def _check_r_env(rscript: Path) -> tuple[bool, str]:
    """Return (ok, reason). Probes for required R + Python packages."""
    if not rscript.exists():
        return False, f"Rscript not found at {rscript}"
    probe = (
        'pkgs <- c("reticulate","Matrix","digest","jsonlite"); '
        'missing <- pkgs[!sapply(pkgs, requireNamespace, quietly=TRUE)]; '
        'if (length(missing)) { '
        '  cat("MISSING_R:", paste(missing, collapse=","), "\\n"); quit(status=2) '
        '}; '
        'np <- tryCatch(reticulate::import("numpy"), error=function(e) NULL); '
        'pl <- tryCatch(reticulate::import("pyliftover"), error=function(e) NULL); '
        'if (is.null(np)) { cat("MISSING_PY: numpy\\n"); quit(status=3) }; '
        'if (is.null(pl)) { cat("MISSING_PY: pyliftover\\n"); quit(status=4) }; '
        'cat("OK\\n")'
    )
    try:
        res = subprocess.run(
            [str(rscript), "-e", probe],
            capture_output=True,
            text=True,
            timeout=R_SUBPROCESS_TIMEOUT_S,
            env=_r_env(rscript),
        )
    except Exception as exc:  # noqa: BLE001
        return False, f"Rscript probe failed: {exc!r}"
    if res.returncode != 0:
        return False, f"Rscript probe rc={res.returncode}: {res.stdout.strip()} {res.stderr.strip()}"
    if "OK" not in res.stdout:
        return False, f"Rscript probe did not return OK: {res.stdout.strip()}"
    return True, "ok"


@pytest.fixture(scope="session")
def rscript_or_skip() -> Path:
    """Resolve a usable Rscript; pytest.skip with diagnostic if none found."""
    failures: list[str] = []
    for cand in _candidate_rscripts():
        ok, reason = _check_r_env(cand)
        if ok:
            return cand
        failures.append(f"{cand}: {reason}")
    pytest.skip(
        "no Rscript with reticulate+Matrix+digest+jsonlite+numpy+pyliftover; "
        "tried: " + " | ".join(failures)
    )


@pytest.fixture(scope="session")
def chain_38_to_37() -> Path:
    if not CHAIN_38_TO_37.exists():
        pytest.skip(f"chain not present: {CHAIN_38_TO_37}")
    return CHAIN_38_TO_37


# ---------------------------------------------------------------------------
# Helpers: synthetic .npz fixtures + .rds reader
# ---------------------------------------------------------------------------
def _make_synthetic_npz(
    out_path: Path,
    n: int = 50,
    variant_ids: list[str] | None = None,
    rsids: list[str] | None = None,
    seed: int = 42,
) -> np.ndarray:
    """Build a synthetic n x n symmetric LD matrix and write to .npz.

    Returns the dense symmetric matrix used (for reference comparisons).
    Stored as lower-triangular to mirror the AOU-LD-PIPELINE.md §7.2
    export shape.
    """
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, n)).astype("float32")
    full = (A + A.T) / 2.0
    np.fill_diagonal(full, 1.0)
    lower = np.tril(full).astype("float32")
    if variant_ids is None:
        variant_ids = [f"16:{50_000_000 + i:d}:A:G" for i in range(n)]
    if rsids is None:
        rsids = [""] * n
    np.savez_compressed(
        str(out_path),
        ld=lower,
        variant_ids=np.asarray(variant_ids, dtype=str),
        rsids=np.asarray(rsids, dtype=str),
    )
    return full


def _read_rds(rscript: Path, rds_path: Path) -> dict:
    """Read .rds via Rscript, dump payload as JSON, parse in Python.

    Avoids the pyreadr dependency (not in smoke_dev). Encodes the matrix
    as nested list-of-lists; OK for 50 x 50 test matrices.

    260805-23d Task 5 -- THE ONE AUTHORIZED EDIT to this pre-existing module
    (blast-radius BLOCKER-D; Carter's decision, 2026-08-05). REPLACE, NOT RELAX:
    every assertion this helper feeds -- dimensions, symmetry, dimnames, the
    diagonal, the off-diagonal sample, snp_ids, provenance -- is PRESERVED and
    now reads obj$R, the field the real consumers have always used
    (run_susie_rss.R::load_ld_matrix reads obj$R + obj$variants;
    run_qtl_coloc.R:222 reads ld_obj$R). The stopifnot ADDS a pin so the removal
    of the dense back-compat `ld` field is TESTED rather than merely untested;
    tests/m3/test_ld_npz_to_rds_bounded.py::test_reader_rejects_a_pre_change_rds
    is the observation that this pin can fail. Net: strictly more than before.
    """
    # Matrix is attached first so touching the sparse obj$R cannot emit a lazy
    # load banner that races cat() for the JSON payload.
    reader = (
        'suppressPackageStartupMessages(library(Matrix)); '
        'args <- commandArgs(trailingOnly=TRUE); '
        'obj <- readRDS(args[[1]]); '
        'stopifnot(is.null(obj$ld)); '
        'M <- as.matrix(obj$R); '
        'out <- list( '
        '  ld_rows = nrow(M), '
        '  ld_cols = ncol(M), '
        '  ld_symmetric = isSymmetric(M), '
        '  dim_rownames = rownames(M), '
        '  dim_colnames = colnames(M), '
        '  snp_ids = obj$snp_ids, '
        '  ld_diag = diag(M), '
        '  ld_offdiag_sample = M[1, min(2L, ncol(M))], '
        '  provenance = obj$provenance '
        '); '
        'cat(jsonlite::toJSON(out, auto_unbox=TRUE, null="null", na="null"))'
    )
    res = subprocess.run(
        [str(rscript), "-e", reader, str(rds_path)],
        capture_output=True,
        text=True,
        timeout=R_SUBPROCESS_TIMEOUT_S,
        env=_r_env(rscript),
    )
    if res.returncode != 0:
        raise RuntimeError(f"rds reader failed rc={res.returncode}: {res.stderr}")
    payload = res.stdout
    # Find the JSON; some R installations emit a banner. We expect the
    # last printed token to be the JSON object; locate first "{".
    j_start = payload.find("{")
    if j_start < 0:
        raise RuntimeError(f"no JSON in rds reader output: {payload!r}")
    return json.loads(payload[j_start:])


def _run_converter(rscript: Path, npz: Path, rds: Path, chain: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(rscript), str(R_CONVERTER), str(npz), str(rds), str(chain)],
        capture_output=True,
        text=True,
        timeout=R_SUBPROCESS_TIMEOUT_S,
        env=_r_env(rscript),
    )


# ===========================================================================
# Static-content tests (always run; no Rscript required)
# ===========================================================================
def test_r_converter_exists_and_min_length():
    assert R_CONVERTER.is_file(), f"missing: {R_CONVERTER}"
    n_lines = sum(1 for _ in R_CONVERTER.open())
    assert n_lines >= 60, f"R converter too short: {n_lines} < 60"


def test_r_converter_static_grep_acceptance():
    """Acceptance criteria from plan <acceptance_criteria>."""
    src = R_CONVERTER.read_text()
    # Liftover present
    assert "pyliftover" in src or "LiftOver" in src
    # Chain SHA recorded
    assert "chain_sha256" in src or "chain_path" in src
    # exactly one saveRDS call
    assert src.count("saveRDS") == 1, f"expected 1 saveRDS, got {src.count('saveRDS')}"
    # provenance referenced at least twice
    assert src.count("provenance") >= 2


def test_bm_helper_exists_and_imports_block_matrix():
    assert BM_HELPER.is_file(), f"missing: {BM_HELPER}"
    src = BM_HELPER.read_text()
    assert "BlockMatrix.read" in src or "hl.linalg.BlockMatrix" in src
    assert src.count("savez_compressed") == 1
    n_lines = sum(1 for _ in BM_HELPER.open())
    assert n_lines >= 40, f"bm_to_npz.py too short: {n_lines} < 40"


# ===========================================================================
# Behavior tests (require working Rscript; skip gracefully if env missing)
# ===========================================================================
def test_npz_to_rds_round_trip(rscript_or_skip, chain_38_to_37, tmp_path):
    """50x50 symmetric .npz -> .rds; symmetric + dimnames + dim match."""
    npz = tmp_path / "synth.npz"
    rds = tmp_path / "synth.rds"
    full = _make_synthetic_npz(npz, n=50)
    res = _run_converter(rscript_or_skip, npz, rds, chain_38_to_37)
    assert res.returncode == 0, f"converter failed: {res.stderr}\n{res.stdout}"
    assert rds.exists()
    payload = _read_rds(rscript_or_skip, rds)
    # All variants are at chr16:50_000_000+i — these may or may not lift over;
    # the round-trip test asserts only on the surviving subset's structure.
    n_out = payload["ld_rows"]
    assert n_out == payload["ld_cols"]
    assert n_out > 0, "all variants dropped by liftover -- pick coords that lift"
    assert payload["ld_symmetric"] is True
    assert len(payload["dim_rownames"]) == n_out
    assert len(payload["dim_colnames"]) == n_out
    assert payload["dim_rownames"] == payload["dim_colnames"]


def test_chr_prefix_stripping(rscript_or_skip, chain_38_to_37, tmp_path):
    """Variant IDs with 'chr16:...' prefix get stripped to '16:...' in dimnames."""
    npz = tmp_path / "chr_prefix.npz"
    rds = tmp_path / "chr_prefix.rds"
    # Use coordinates known to liftover (FTO ~53.8 Mb) so we don't drop them.
    vids = [
        "chr16:53809247:T:A",  # rs1558902 GRCh38
        "chr16:53800000:C:G",
        "chr16:53810000:G:T",
    ]
    n = len(vids)
    rng = np.random.default_rng(0)
    A = rng.standard_normal((n, n)).astype("float32")
    full = (A + A.T) / 2.0
    np.fill_diagonal(full, 1.0)
    lower = np.tril(full).astype("float32")
    np.savez_compressed(
        str(npz),
        ld=lower,
        variant_ids=np.asarray(vids, dtype=str),
        rsids=np.asarray([""] * n, dtype=str),
    )
    res = _run_converter(rscript_or_skip, npz, rds, chain_38_to_37)
    assert res.returncode == 0, f"converter failed: {res.stderr}"
    payload = _read_rds(rscript_or_skip, rds)
    # No surviving dim_rownames should start with "chr"
    for name in payload["dim_rownames"]:
        assert not name.startswith("chr"), f"dimname still has chr-prefix: {name}"


def test_grch38_to_grch37_liftover(rscript_or_skip, chain_38_to_37, tmp_path):
    """chr16:53809247 (GRCh38) lifts to GRCh37 16:53843159 via the UCSC chain.

    The pipeline's coordinate truth is the UCSC hg38ToHg19 chain (pyliftover),
    NOT a dbSNP rsID lookup. Verified directly: LiftOver(hg38ToHg19).convert
    ("chr16", 53809247) -> ("chr16", 53843159). (An earlier dbSNP-derived
    expectation of 53803574 never ran because reticulate bound to a pyliftover-
    less interpreter; the _r_env RETICULATE_PYTHON pin un-skipped it.)
    """
    npz = tmp_path / "lift.npz"
    rds = tmp_path / "lift.rds"
    # Single-variant .npz to keep the test focused on the coordinate.
    vids = ["chr16:53809247:T:A"]   # rs1558902 GRCh38
    rsids = [""]                    # force the synthetic-ID path
    n = len(vids)
    lower = np.array([[1.0]], dtype="float32")
    np.savez_compressed(
        str(npz),
        ld=lower,
        variant_ids=np.asarray(vids, dtype=str),
        rsids=np.asarray(rsids, dtype=str),
    )
    res = _run_converter(rscript_or_skip, npz, rds, chain_38_to_37)
    assert res.returncode == 0, f"converter failed: {res.stderr}"
    payload = _read_rds(rscript_or_skip, rds)
    # Expect b37 ID "16:53843159:T:A" (UCSC hg38ToHg19 chain). Allow ±1 bp.
    rownames = payload["dim_rownames"]
    if isinstance(rownames, str):
        rownames = [rownames]
    assert len(rownames) == 1, f"expected 1 surviving variant, got {rownames}"
    name = rownames[0]
    parts = name.split(":")
    assert parts[0] == "16", f"chrom changed: {parts}"
    pos37 = int(parts[1])
    # chr16:53809247 (GRCh38) -> GRCh37 chr16:53843159 via UCSC hg38ToHg19 chain
    assert abs(pos37 - 53843159) <= 5, f"liftover off: got {pos37}, expected ~53843159"


def test_rsid_preference_over_synthetic(rscript_or_skip, chain_38_to_37, tmp_path):
    """When both rsid and synthetic ID are populated, dimnames carry rsid."""
    npz = tmp_path / "rsid_pref.npz"
    rds = tmp_path / "rsid_pref.rds"
    vids = ["chr16:53809247:T:A", "chr16:53810000:G:C"]
    rsids = ["rs1558902", "rs99999999"]
    lower = np.tril(np.eye(2, dtype="float32"))
    np.savez_compressed(
        str(npz),
        ld=lower,
        variant_ids=np.asarray(vids, dtype=str),
        rsids=np.asarray(rsids, dtype=str),
    )
    res = _run_converter(rscript_or_skip, npz, rds, chain_38_to_37)
    assert res.returncode == 0, f"converter failed: {res.stderr}"
    payload = _read_rds(rscript_or_skip, rds)
    rownames = payload["dim_rownames"]
    if isinstance(rownames, str):
        rownames = [rownames]
    assert "rs1558902" in rownames
    assert "rs99999999" in rownames


def test_failed_liftover_drops_variant(rscript_or_skip, chain_38_to_37, tmp_path):
    """Variants whose IDs fail liftover are dropped; matrix dim reduces."""
    npz = tmp_path / "drop.npz"
    rds = tmp_path / "drop.rds"
    vids = [
        "chr16:53809247:T:A",          # liftable
        "chr99:1234567:A:T",           # invalid chromosome -> NA -> drop
        "chr16:53810000:G:C",           # liftable
        "not_a_variant_id",            # malformed -> NA -> drop
    ]
    n = len(vids)
    rng = np.random.default_rng(1)
    A = rng.standard_normal((n, n)).astype("float32")
    full = (A + A.T) / 2.0
    np.fill_diagonal(full, 1.0)
    lower = np.tril(full).astype("float32")
    np.savez_compressed(
        str(npz),
        ld=lower,
        variant_ids=np.asarray(vids, dtype=str),
        rsids=np.asarray([""] * n, dtype=str),
    )
    res = _run_converter(rscript_or_skip, npz, rds, chain_38_to_37)
    assert res.returncode == 0, f"converter failed: {res.stderr}"
    payload = _read_rds(rscript_or_skip, rds)
    # 2 of 4 should survive
    assert payload["ld_rows"] == 2
    assert payload["ld_cols"] == 2
    # And n_var_dropped_liftover should equal 2
    prov = payload["provenance"]
    assert int(prov["n_var_input"]) == 4
    assert int(prov["n_var_output"]) == 2
    assert int(prov["n_var_dropped_liftover"]) == 2


def test_provenance_json(rscript_or_skip, chain_38_to_37, tmp_path):
    """RDS payload includes provenance with required fields."""
    npz = tmp_path / "prov.npz"
    rds = tmp_path / "prov.rds"
    vids = ["chr16:53809247:T:A", "chr16:53810000:G:C"]
    lower = np.tril(np.eye(2, dtype="float32"))
    np.savez_compressed(
        str(npz),
        ld=lower,
        variant_ids=np.asarray(vids, dtype=str),
        rsids=np.asarray([""] * 2, dtype=str),
    )
    res = _run_converter(rscript_or_skip, npz, rds, chain_38_to_37)
    assert res.returncode == 0
    payload = _read_rds(rscript_or_skip, rds)
    prov = payload["provenance"]
    for key in (
        "npz_path",
        "chain_path",
        "chain_sha256",
        "datetime",
        "n_var_input",
        "n_var_output",
        "n_var_dropped_liftover",
        "genome_build",
    ):
        assert key in prov, f"provenance missing {key}: {prov.keys()}"
    assert prov["genome_build"] == "GRCh37"
    # SHA-256 is 64 hex chars
    assert len(str(prov["chain_sha256"])) == 64


# ===========================================================================
# BR-01 regression (blast-radius of the CR-01 fix): the CR-01 fix made the
# .npz `lower_triangular` flag AUTHORITATIVE in ld_npz_to_rds.R -- the reader
# reconstructs the upper triangle (tri + t(tri) - diag(diag(tri))) ONLY when
# the flag is TRUE, else it just symmetrizes (tri + t(tri))/2. A lower-tri
# .npz that OMITS the flag therefore gets HALVED: (L + t(L))/2 averages the
# populated r against a structural 0 -> r/2 (0.6 -> 0.30).
#
# bm_to_npz.py (Path A.3, xlarge regions, the m3-02b xlarge-split deliverable
# path) writes np.tril(...) lower-triangular and historically did NOT write
# the flag -> every A.3 off-diagonal r silently halved. These tests pin the
# fix: bm_to_npz.py MUST write lower_triangular=True, and a lower-tri .npz
# built the bm_to_npz.py way must round-trip the TRUE r, not r/2.
# ===========================================================================
def test_bm_to_npz_static_writes_lower_triangular_flag():
    """BR-01 contract: bm_to_npz.py's savez_compressed includes lower_triangular.

    Static check -- runs without Hail or R. RED against the flag-less
    bm_to_npz.py; GREEN once the flag is written.
    """
    src = BM_HELPER.read_text()
    assert "lower_triangular" in src, (
        "BR-01: bm_to_npz.py emits np.tril(...) lower-triangular .npz but does "
        "NOT write the lower_triangular flag; after the CR-01 fix the reader "
        "defaults absent->FALSE and HALVES every off-diagonal r. The "
        "savez_compressed call must pass lower_triangular=np.array([True])."
    )


def test_bm_style_lower_tri_npz_recovers_true_r(rscript_or_skip, chain_38_to_37, tmp_path):
    """BR-01 round-trip: a lower-tri .npz written the bm_to_npz.py way (np.tril
    + lower_triangular flag) must recover the TRUE off-diagonal r, NOT r/2.

    RED expectation against a flag-LESS .npz: recovered r == 0.30 (halved).
    GREEN with the flag present: recovered r == 0.60.
    """
    npz = tmp_path / "bm_style.npz"
    rds = tmp_path / "bm_style.rds"
    # Two variants chosen to liftover cleanly (FTO ~53.8 Mb) so neither is
    # dropped; a known off-diagonal r so we can assert exact recovery.
    true_r = np.float32(0.6)
    full = np.array([[1.0, true_r], [true_r, 1.0]], dtype="float32")
    lower = np.tril(full).astype("float32")  # exactly what bm_to_npz.py stores
    vids = ["chr16:53809247:T:A", "chr16:53810000:G:C"]
    np.savez_compressed(
        str(npz),
        ld=lower,
        variant_ids=np.asarray(vids, dtype=str),
        rsids=np.asarray([""] * 2, dtype=str),
        # Mirror the bm_to_npz.py fix: write the flag so the reader
        # reconstructs instead of halving.
        lower_triangular=np.array([True]),
    )
    res = _run_converter(rscript_or_skip, npz, rds, chain_38_to_37)
    assert res.returncode == 0, f"converter failed: {res.stderr}\n{res.stdout}"
    payload = _read_rds(rscript_or_skip, rds)
    assert payload["ld_rows"] == 2, "both variants should survive liftover"
    # Diagonal preserved at 1.0.
    diag = payload["ld_diag"]
    if not isinstance(diag, list):
        diag = [diag]
    for d in diag:
        assert abs(float(d) - 1.0) < 1e-5, f"diagonal not 1.0: {diag}"
    # Symmetric.
    assert payload["ld_symmetric"] is True
    # THE BR-01 ASSERTION: off-diagonal must be the TRUE r (0.60), proving the
    # lower triangle was reconstructed, NOT halved to 0.30 and NOT doubled.
    off = float(payload["ld_offdiag_sample"])
    assert abs(off - 0.60) < 1e-4, (
        f"BR-01: recovered off-diagonal r={off:.4f}; expected 0.60. "
        f"r/2 (0.30) => lower-tri .npz was symmetrized without reconstruction "
        f"(flag absent/ignored); 2r (1.20) => double-counted."
    )


# ===========================================================================
# AF SIDECAR (AF-SIDECAR-01): bm_to_npz.py must carry the A.3 allele_freq
# sidecar into the .npz `allele_freq` key (row-aligned to variant_ids), with
# the missing-vs-zero distinction (WR-03: blank -> NaN, never a fake 0.0),
# a loud all-NaN + WARNING when the sidecar is omitted, and a loud ValueError
# when the sidecar is row-misaligned. These converter-level tests do NOT depend
# on a real Hail install or on R: they inject a stub `hail` module so the real
# bm_to_npz() AF code path (loader + length-guard + savez_compressed) runs even
# where Hail is absent (e.g. the smoke_dev / Track A NCSU devboxes). The A.3
# end-to-end test is R-env-gated via rscript_or_skip.
# ===========================================================================
def _install_stub_hail(monkeypatch, dense: np.ndarray) -> None:
    """Inject a minimal stub `hail` module so bm_to_npz() runs without Hail.

    bm_to_npz() does `import hail as hl` then
    `hl.linalg.BlockMatrix.read(str(bm_dir))` -> `.shape` / `.to_numpy()`.
    We stub exactly that surface so the AF loader / length-guard / savez path
    is exercised on the real bm_to_npz.py code (no real JVM, no real .bm dir).
    """
    import sys
    import types

    dense = np.asarray(dense, dtype="float64")

    class _StubBM:
        def __init__(self, arr):
            self._arr = arr
            self.shape = (arr.shape[0], arr.shape[1])

        def to_numpy(self):
            return self._arr

    class _StubBMClass:
        @staticmethod
        def read(_path):
            return _StubBM(dense)

    hail_mod = types.ModuleType("hail")
    linalg_mod = types.ModuleType("hail.linalg")
    linalg_mod.BlockMatrix = _StubBMClass
    hail_mod.linalg = linalg_mod
    hail_mod.is_initialized = lambda: True
    hail_mod.init = lambda *a, **k: None
    monkeypatch.setitem(sys.modules, "hail", hail_mod)
    monkeypatch.setitem(sys.modules, "hail.linalg", linalg_mod)


def _import_bm_to_npz():
    """Import the bm_to_npz module from src/python by file path."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("bm_to_npz_under_test", BM_HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_af_sidecar(path: Path, values: list) -> None:
    """Write a one-float-per-line AF sidecar (blank line for a missing AF)."""
    lines = []
    for v in values:
        if v is None or (isinstance(v, str) and v == ""):
            lines.append("")
        else:
            lines.append(repr(float(v)))
    path.write_text("\n".join(lines) + "\n")


def test_bm_to_npz_writes_allele_freq_when_provided(tmp_path, monkeypatch):
    """--allele-freq sidecar -> row-aligned numeric allele_freq key; blank -> NaN.

    RED against the current bm_to_npz.py (no allele_freq key, no allele_freq_tsv
    param). Exercises the real bm_to_npz() AF loader via a stubbed Hail.
    """
    bm = _import_bm_to_npz()
    n = 3
    dense = np.eye(n, dtype="float64")
    dense[1, 0] = dense[0, 1] = 0.5
    _install_stub_hail(monkeypatch, dense)

    vid_tsv = tmp_path / "variant_ids.tsv"
    rsid_tsv = tmp_path / "rsids.tsv"
    af_tsv = tmp_path / "region.allele_freq.tsv"
    vids = [f"16:{53_800_000 + i:d}:A:G" for i in range(n)]
    vid_tsv.write_text("\n".join(vids) + "\n")
    # Non-empty rsids: _load_sidecar (np.loadtxt) collapses an all-blank file to
    # a length-0 array (pre-existing quirk, unrelated to AF); use placeholders so
    # the rsids length-guard sees n_rows and the AF path is what's under test.
    rsid_tsv.write_text("\n".join(f"rs{i}" for i in range(n)) + "\n")
    # WR-03: middle entry genuinely missing (blank) -> must round-trip to NaN.
    _write_af_sidecar(af_tsv, [0.12, "", 0.34])

    out_npz = tmp_path / "out.npz"
    fake_bm = tmp_path / "fake.bm"
    fake_bm.mkdir()  # bm_to_npz() guards is_dir(); stub read ignores contents
    bm.bm_to_npz(
        bm_dir=fake_bm,
        variant_ids_tsv=vid_tsv,
        rsids_tsv=rsid_tsv,
        out_npz=out_npz,
        allele_freq_tsv=af_tsv,
    )
    z = np.load(str(out_npz))
    assert "allele_freq" in z.files, "allele_freq key missing from .npz"
    af = np.asarray(z["allele_freq"], dtype=float)
    assert af.shape == (n,), f"allele_freq length {af.shape} != n_rows {n}"
    assert abs(af[0] - 0.12) < 1e-6
    assert abs(af[2] - 0.34) < 1e-6
    # WR-03: blank entry is NaN, NOT a fake 0.0.
    assert np.isnan(af[1]), f"blank AF must be NaN, got {af[1]!r}"
    assert af[1] != 0.0
    # Existing keys unchanged (no BR-01 regression).
    assert bool(np.asarray(z["lower_triangular"]).ravel()[0]) is True
    assert list(z["variant_ids"]) == vids
    upper = np.triu(z["ld"], k=1)
    assert np.allclose(upper, 0.0), "ld must remain lower-triangular only"


def test_bm_to_npz_omitted_allele_freq_is_all_nan_and_warns(tmp_path, monkeypatch, capsys):
    """No --allele-freq -> all-NaN allele_freq key (len n_rows) + loud WARNING.

    RED against the current bm_to_npz.py (no allele_freq key at all).
    """
    bm = _import_bm_to_npz()
    n = 3
    dense = np.eye(n, dtype="float64")
    _install_stub_hail(monkeypatch, dense)

    vid_tsv = tmp_path / "variant_ids.tsv"
    rsid_tsv = tmp_path / "rsids.tsv"
    vids = [f"16:{53_800_000 + i:d}:A:G" for i in range(n)]
    vid_tsv.write_text("\n".join(vids) + "\n")
    # Non-empty rsids: _load_sidecar (np.loadtxt) collapses an all-blank file to
    # a length-0 array (pre-existing quirk, unrelated to AF); use placeholders so
    # the rsids length-guard sees n_rows and the AF path is what's under test.
    rsid_tsv.write_text("\n".join(f"rs{i}" for i in range(n)) + "\n")

    out_npz = tmp_path / "out.npz"
    fake_bm = tmp_path / "fake.bm"
    fake_bm.mkdir()  # bm_to_npz() guards is_dir(); stub read ignores contents
    bm.bm_to_npz(
        bm_dir=fake_bm,
        variant_ids_tsv=vid_tsv,
        rsids_tsv=rsid_tsv,
        out_npz=out_npz,
        allele_freq_tsv=None,
    )
    captured = capsys.readouterr()
    z = np.load(str(out_npz))
    assert "allele_freq" in z.files, "allele_freq key must ALWAYS be present"
    af = np.asarray(z["allele_freq"], dtype=float)
    assert af.shape == (n,)
    assert np.all(np.isnan(af)), f"omitted AF must be all-NaN, got {af!r}"
    # Absence must be VISIBLE, not silent.
    assert "WARNING" in captured.out, f"no loud WARNING printed: {captured.out!r}"
    assert "no --allele-freq" in captured.out, (
        f"WARNING must name the missing --allele-freq: {captured.out!r}"
    )


def test_bm_to_npz_misaligned_allele_freq_raises(tmp_path, monkeypatch):
    """AF sidecar length != n_rows -> loud ValueError naming the lengths + path.

    RED against the current bm_to_npz.py (no allele_freq handling at all).
    """
    bm = _import_bm_to_npz()
    n = 3
    dense = np.eye(n, dtype="float64")
    _install_stub_hail(monkeypatch, dense)

    vid_tsv = tmp_path / "variant_ids.tsv"
    rsid_tsv = tmp_path / "rsids.tsv"
    af_tsv = tmp_path / "region.allele_freq.tsv"
    vids = [f"16:{53_800_000 + i:d}:A:G" for i in range(n)]
    vid_tsv.write_text("\n".join(vids) + "\n")
    # Non-empty rsids: _load_sidecar (np.loadtxt) collapses an all-blank file to
    # a length-0 array (pre-existing quirk, unrelated to AF); use placeholders so
    # the rsids length-guard sees n_rows and the AF path is what's under test.
    rsid_tsv.write_text("\n".join(f"rs{i}" for i in range(n)) + "\n")
    # Only 2 AF values for a 3-row BlockMatrix -> misaligned.
    _write_af_sidecar(af_tsv, [0.12, 0.34])

    out_npz = tmp_path / "out.npz"
    fake_bm = tmp_path / "fake.bm"
    fake_bm.mkdir()  # bm_to_npz() guards is_dir(); stub read ignores contents
    with pytest.raises(ValueError) as excinfo:
        bm.bm_to_npz(
            bm_dir=fake_bm,
            variant_ids_tsv=vid_tsv,
            rsids_tsv=rsid_tsv,
            out_npz=out_npz,
            allele_freq_tsv=af_tsv,
        )
    msg = str(excinfo.value)
    assert "allele_freq" in msg, f"ValueError must name allele_freq: {msg!r}"
    assert "2" in msg and "3" in msg, f"ValueError must name lengths: {msg!r}"
    assert "out.npz" in msg, f"ValueError must name the out path: {msg!r}"


def test_a3_style_npz_carries_af_into_variants(rscript_or_skip, chain_38_to_37, tmp_path):
    """End-to-end: an A.3-shaped .npz with allele_freq lands in obj$variants$AF.

    Proves the bm_to_npz OUTPUT CONTRACT (np.tril ld + variant_ids + rsids +
    lower_triangular=[True] + allele_freq) carries AF into obj$variants$AF via
    ld_npz_to_rds.R. R-env-gated (skips with diagnostic if m3-r-ld absent).
    Coords chosen to lift cleanly (FTO ~53.8 Mb) so neither variant drops.
    """
    npz = tmp_path / "a3_style.npz"
    rds = tmp_path / "a3_style.rds"
    vids = ["chr16:53809247:T:A", "chr16:53810000:G:C"]
    af = [0.12, 0.34]
    true_r = np.float32(0.6)
    full = np.array([[1.0, true_r], [true_r, 1.0]], dtype="float32")
    lower = np.tril(full).astype("float32")
    np.savez_compressed(
        str(npz),
        ld=lower,
        variant_ids=np.asarray(vids, dtype=str),
        rsids=np.asarray([""] * 2, dtype=str),
        lower_triangular=np.array([True]),
        allele_freq=np.asarray(af, dtype=float),
    )
    res = _run_converter(rscript_or_skip, npz, rds, chain_38_to_37)
    assert res.returncode == 0, f"converter failed: {res.stderr}\n{res.stdout}"
    payload = _read_rds_with_af(rscript_or_skip, rds)
    assert payload["ld_rows"] == 2, "both variants should survive liftover"
    variants_af = payload["variants_af"]
    if not isinstance(variants_af, list):
        variants_af = [variants_af]
    assert len(variants_af) == 2, f"expected 2 AF values, got {variants_af!r}"
    assert abs(float(variants_af[0]) - 0.12) < 1e-6, f"AF[0] off: {variants_af}"
    assert abs(float(variants_af[1]) - 0.34) < 1e-6, f"AF[1] off: {variants_af}"


def _read_rds_with_af(rscript: Path, rds_path: Path) -> dict:
    """Read .rds via Rscript dumping obj$variants$AF (na='null') as JSON.

    Mirror of _read_rds but also dumps the variants$AF column so the A.3
    end-to-end test can assert AF landed in obj$variants$AF.

    260805-23d Task 5 -- the second half of the ONE authorized edit to this
    module (blast-radius BLOCKER-D). Same discipline as _read_rds above: the
    dimension assertions are PRESERVED and re-pointed at obj$R, the AF assertions
    are untouched, and the stopifnot pins the dense `ld` field's removal.
    """
    reader = (
        'suppressPackageStartupMessages(library(Matrix)); '
        'args <- commandArgs(trailingOnly=TRUE); '
        'obj <- readRDS(args[[1]]); '
        'stopifnot(is.null(obj$ld)); '
        'out <- list( '
        '  ld_rows = nrow(obj$R), '
        '  ld_cols = ncol(obj$R), '
        '  variants_af = obj$variants$AF '
        '); '
        'cat(jsonlite::toJSON(out, auto_unbox=TRUE, null="null", na="null"))'
    )
    res = subprocess.run(
        [str(rscript), "-e", reader, str(rds_path)],
        capture_output=True,
        text=True,
        timeout=R_SUBPROCESS_TIMEOUT_S,
        env=_r_env(rscript),
    )
    if res.returncode != 0:
        raise RuntimeError(f"rds AF reader failed rc={res.returncode}: {res.stderr}")
    payload = res.stdout
    j_start = payload.find("{")
    if j_start < 0:
        raise RuntimeError(f"no JSON in rds AF reader output: {payload!r}")
    return json.loads(payload[j_start:])


def test_bm_to_npz_helper(tmp_path):
    """src/python/bm_to_npz.py reads a synthetic Hail BlockMatrix; emits .npz.

    Skipped if Hail is not installed (the m3-aou-dev env has not been built
    on every dev box yet).
    """
    hl = pytest.importorskip("hail")
    # Build a synthetic 8x8 symmetric LD matrix as a Hail BlockMatrix.
    n = 8
    rng = np.random.default_rng(7)
    A = rng.standard_normal((n, n)).astype("float64")
    full = (A + A.T) / 2.0
    np.fill_diagonal(full, 1.0)

    # Hail must be initialized for BlockMatrix.from_numpy(). Use a quiet
    # session; let Hail manage its own JVM.
    try:
        if not hl.is_initialized():  # type: ignore[attr-defined]
            hl.init(quiet=True)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Hail init failed: {exc!r}")

    bm_dir = tmp_path / "synthetic.bm"
    bm = hl.linalg.BlockMatrix.from_numpy(full)
    bm.write(str(bm_dir), overwrite=True, force_row_major=True)

    vids = [f"16:{50_000_000 + i:d}:A:G" for i in range(n)]
    rsids = [""] * n
    vid_tsv = tmp_path / "variant_ids.tsv"
    rsid_tsv = tmp_path / "rsids.tsv"
    vid_tsv.write_text("\n".join(vids) + "\n")
    rsid_tsv.write_text("\n".join(rsids) + "\n")

    out_npz = tmp_path / "out.npz"
    # Invoke the helper as a subprocess so PATH-resolution mirrors production.
    res = subprocess.run(
        [
            "python",
            str(BM_HELPER),
            "--bm-dir", str(bm_dir),
            "--variant-ids", str(vid_tsv),
            "--rsids", str(rsid_tsv),
            "--out-npz", str(out_npz),
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert res.returncode == 0, f"bm_to_npz.py failed: {res.stderr}\n{res.stdout}"
    assert out_npz.exists()
    z = np.load(str(out_npz))
    assert z["ld"].shape == (n, n)
    # Lower-triangular: upper triangle (above diag) must be zero.
    upper = np.triu(z["ld"], k=1)
    assert np.allclose(upper, 0.0), "bm_to_npz.py must emit lower-triangular only"
    assert list(z["variant_ids"]) == vids
    # BR-01: the lower_triangular flag must be present + True so the reader
    # reconstructs (not halves) the off-diagonals.
    assert "lower_triangular" in z.files, (
        "BR-01: bm_to_npz.py .npz missing lower_triangular flag"
    )
    assert bool(np.asarray(z["lower_triangular"]).ravel()[0]) is True
