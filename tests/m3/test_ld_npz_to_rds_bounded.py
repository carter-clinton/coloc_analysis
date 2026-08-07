"""tests/m3/test_ld_npz_to_rds_bounded.py -- 260805-23d Task 5, blast-radius BLOCKER-D.

WHAT THIS PINS. ``src/scripts/ld_npz_to_rds.R`` used to materialise a full dense
n x n float64 in R (``z$f[["ld"]]`` under ``convert = TRUE``, then three more
whole-matrix temporaries for the symmetry recovery) AND to PERSIST that dense
matrix into the ``.rds`` as a back-compat ``ld`` field -- all under a declared
``mem_mb=8000``. For the SMALLEST crosswalk target (SH2B3 ``m2_region_00040__sub14``,
n_var 75,497) the dense float64 alone is 45.6 GB; the ``ld`` field made it an
OUTPUT cost as well, so no amount of block-wise processing could have fixed it.

Carter's decision (2026-08-05) unfreezes ``src/scripts/ld_npz_to_rds.R`` FOR THIS
TASK ONLY: drop the dense ``ld`` field, bound the read block-wise. The other two
frozen contracts (``src/python/plink_ld_to_npz.py``,
``src/python/condition_ld_matrix.py``) stay frozen -- this module reads
``plink_ld_to_npz.py`` for the block-loop SHAPE only and never edits it.

THE FOUR PINS

1. ``test_old_and_new_rds_are_field_identical_except_ld``
   The byte-equivalence proof AND the negative control for the removal. Runs the
   PRE-CHANGE converter (recovered with ``git show 5ec33bd:...``) and the NEW one
   over the SAME synthetic ``.npz``, then compares in ONE Rscript with
   ``identical()`` -- not ``all.equal()`` -- on ``R`` / ``variants`` / ``snp_ids``
   and on ``provenance`` minus ``datetime``. Both triangle conventions are covered
   (``lower_triangular`` TRUE and absent), because the flag is this file's
   recurring defect class (CR-01 doubling, BR-01 halving --
   ``[[feedback_npz_triangle_flag_contract]]``), and the tiling is re-run at a
   deliberately awkward block size so the multi-tile path is exercised at n=64
   rather than only the single-tile degenerate case. FOUR negative controls, each
   a perturbation of one surviving field, are evaluated in the same run.

2. ``test_read_is_memory_bounded``
   ``/usr/bin/time -v`` maxRSS, old converter vs new, on the PRODUCTION-SHAPED
   input (see the docstring there for why banded, and what the dense worst case
   costs). Its own control: it fails if the new converter is not actually leaner,
   plus an absolute-margin guard so a both-tiny measurement cannot pass vacuously,
   plus a shape-independent bound against the irreducible dense-float32 read.

3. ``test_no_whole_matrix_expression_survives``
   The whole-matrix expressions are gone from the CODE (comment-stripped, so the
   assertion cannot be satisfied by renaming a variable in prose), with the
   5ec33bd source as the observed-failing control.

4. ``test_reader_rejects_a_pre_change_rds``
   The ``stopifnot(is.null(obj$ld))`` added to ``test_ld_npz_to_rds.py::_read_rds``
   is a LIVE assertion: a pre-change ``.rds`` fed to it raises. Without this the
   removal would be pinned by a test that can never fail.

SCOPE HONESTY -- NOT A FULL CLOSE OF BLOCKER-D. The ``.npz``'s own ``ld`` key is a
DENSE float32 array written by the FROZEN producer
(``plink_ld_to_npz.py`` ``np.zeros((n_var, n_var), dtype="float32")``), so even a
perfectly bounded reader must hold ONE dense float32 copy: 22.8 GB at n=75,497
(SH2B3 ``__sub14``), 67.3 GB at MC4R, ~553 GB at the FTO/HLA ~372k targets. This
work makes SH2B3's subregion feasible on a big-memory node and makes the large
targets FAIL FAST at a stated ceiling instead of OOM-killing after hours. It does
NOT make them convertible; that needs a genuinely sparse ``.npz``, which is a
PRODUCER-side change on a frozen file and is out of scope.

No perimeter access, no billed action: synthetic ``.npz`` only, NC State, $0.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

# Make tests/m3 importable as a bare module dir (mirrors the sibling modules).
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from conftest import R_SUBPROCESS_TIMEOUT_S  # noqa: E402

# The edited reader is imported, NOT re-implemented: pin 4 must exercise the very
# helper the pre-existing behaviour suite runs through.
from test_ld_npz_to_rds import (  # noqa: E402
    R_CONVERTER,
    _candidate_rscripts,
    _check_r_env,
    _r_env,
    _read_rds,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHAIN_38_TO_37 = (
    PROJECT_ROOT / "data" / "external" / "liftover" / "hg38ToHg19.over.chain.gz"
)
CONVERTER_REL = "src/scripts/ld_npz_to_rds.R"

# The pre-change tree. ld_npz_to_rds.R is byte-identical at 5ec33bd and at the
# 260805-23d Task 4 tip: Tasks 1-4 touched finemap.smk, run_susie_rss.R,
# ld_read_path.py, pipeline.yaml and m3_convert_npz_rds.smk -- never this script.
#: DIFFERENTIAL SUBSTRATE -- never re-pinned. See
#: DEC-2026-08-06-sr4-freeze-scope.
PRE_CHANGE_REF = "5ec33bd"

GNU_TIME = Path("/usr/bin/time")

# n=6000 => n**2 float32 = 144 MB in the reader, n**2 float64 = 288 MB per R copy.
MEM_TEST_N = 6000
MEM_TEST_BAND = 250


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def rscript_or_skip() -> Path:
    """Resolve an Rscript with reticulate+Matrix+digest+jsonlite+numpy+pyliftover."""
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


def _git_show(ref: str, rel_path: str) -> str:
    res = subprocess.run(
        ["git", "show", f"{ref}:{rel_path}"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert res.returncode == 0, (
        f"git show {ref}:{rel_path} failed rc={res.returncode}: {res.stderr}"
    )
    return res.stdout


def _pre_change_converter(tmp_path: Path) -> Path:
    """The 5ec33bd converter, recovered to a tmp file so it can be RUN."""
    out = tmp_path / "ld_npz_to_rds_PRE_CHANGE.R"
    out.write_text(_git_show(PRE_CHANGE_REF, CONVERTER_REL), encoding="utf-8")
    return out


def _strip_r_comments(src: str) -> str:
    """Drop ``#`` comments so a code-level assertion cannot be satisfied by prose.

    Simplification, valid for THIS file: ``ld_npz_to_rds.R`` carries no ``#``
    inside any string literal (verified: the only regexes are ``^chr``,
    ``^rs[0-9]+$`` and the strftime format), so cutting each line at its first
    ``#`` removes exactly the comments.
    """
    return "\n".join(line.split("#", 1)[0] for line in src.splitlines())


def _make_npz(
    out_path: Path,
    n: int,
    lower_flag: bool | None,
    seed: int = 42,
    unliftable_idx: tuple[int, ...] = (),
    with_af: bool = True,
) -> None:
    """Synthetic LD ``.npz`` in the shape the frozen producer writes.

    ``lower_flag=True``  -> store ``np.tril`` + ``lower_triangular=[True]``
                            (the production banded/A.3 shape).
    ``lower_flag=None``  -> store the FULL symmetric matrix and OMIT the flag
                            (the Path A.1 square shape; the reader must then only
                            project out float asymmetry, never mirror).
    ``unliftable_idx`` variants get a malformed 3-field id so ``liftover_one``
    returns NA and the converter exercises its drop-and-remap path.
    """
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, n)).astype("float32")
    full = ((A + A.T) / 2.0).astype("float32")
    np.fill_diagonal(full, 1.0)

    vids = [f"chr16:{53_800_000 + i * 100}:A:G" for i in range(n)]
    for i in unliftable_idx:
        vids[i] = f"chr16:{53_800_000 + i * 100}:A"  # 3 fields -> NA -> dropped

    payload: dict = {
        "variant_ids": np.asarray(vids, dtype=str),
        "rsids": np.asarray([""] * n, dtype=str),
    }
    if with_af:
        payload["allele_freq"] = np.linspace(0.01, 0.49, n).astype("float64")
    if lower_flag:
        payload["ld"] = np.tril(full).astype("float32")
        payload["lower_triangular"] = np.array([True])
    else:
        payload["ld"] = full
    np.savez_compressed(str(out_path), **payload)


def _run_converter(
    rscript: Path,
    converter: Path,
    npz: Path,
    rds: Path,
    chain: Path,
    extra_env: dict | None = None,
) -> subprocess.CompletedProcess:
    env = _r_env(rscript)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [str(rscript), str(converter), str(npz), str(rds), str(chain)],
        capture_output=True,
        text=True,
        timeout=R_SUBPROCESS_TIMEOUT_S,
        env=env,
    )


def _run_r_json(rscript: Path, code: str, args: list[str]) -> dict:
    res = subprocess.run(
        [str(rscript), "-e", code, *args],
        capture_output=True,
        text=True,
        timeout=R_SUBPROCESS_TIMEOUT_S,
        env=_r_env(rscript),
    )
    assert res.returncode == 0, f"R comparator failed rc={res.returncode}: {res.stderr}"
    j = res.stdout.find("{")
    assert j >= 0, f"no JSON in comparator output: {res.stdout!r}"
    return json.loads(res.stdout[j:])


# The comparator. ONE R process reads every .rds, runs identical() on each
# surviving field, and evaluates the four negative controls in the same session.
_COMPARE_R = (
    'suppressPackageStartupMessages(library(Matrix)); '
    'args <- commandArgs(trailingOnly=TRUE); '
    'a <- readRDS(args[[1]]); b <- readRDS(args[[2]]); '
    'cblk <- readRDS(args[[3]]); '
    'afull <- readRDS(args[[4]]); bfull <- readRDS(args[[5]]); '
    'strip <- function(p) { p$datetime <- NULL; p }; '
    'cmp <- function(x, y) list(R=identical(x$R, y$R), '
    '  variants=identical(x$variants, y$variants), '
    '  snp_ids=identical(x$snp_ids, y$snp_ids), '
    '  provenance=identical(strip(x$provenance), strip(y$provenance))); '
    'pR <- b; pR$R@x[1] <- pR$R@x[1] + 1; '
    'pV <- b; pV$variants$AF[1] <- pV$variants$AF[1] + 1; '
    'pS <- b; pS$snp_ids[1] <- "PERTURBED"; '
    'pP <- b; pP$provenance$n_var_output <- -1L; '
    'out <- list( '
    '  lower = cmp(a, b), '
    '  lower_small_block = cmp(a, cblk), '
    '  full = cmp(afull, bfull), '
    '  old_has_ld = !is.null(a$ld), '
    '  new_has_ld = !is.null(b$ld), '
    '  new_has_ld_full = !is.null(bfull$ld), '
    '  names_old = names(a), '
    '  names_new = names(b), '
    '  r_class_old = class(a$R)[1], '
    '  r_class_new = class(b$R)[1], '
    '  n_var_output = a$provenance$n_var_output, '
    '  n_var_dropped = a$provenance$n_var_dropped_liftover, '
    '  nnz_old = length(a$R@x), '
    '  nnz_new = length(b$R@x), '
    '  ctl_R = cmp(a, pR)$R, '
    '  ctl_variants = cmp(a, pV)$variants, '
    '  ctl_snp_ids = cmp(a, pS)$snp_ids, '
    '  ctl_provenance = cmp(a, pP)$provenance '
    '); '
    'cat(jsonlite::toJSON(out, auto_unbox=TRUE, null="null", na="null"))'
)


# ===========================================================================
# 1. Field equivalence + the removal's negative control
# ===========================================================================
def test_old_and_new_rds_are_field_identical_except_ld(
    rscript_or_skip, chain_38_to_37, tmp_path
):
    """Every SURVIVING field is byte-equivalent; only ``ld`` disappears.

    ``identical()``, not ``all.equal()``: the new block-bounded reader must
    reproduce the old whole-matrix arithmetic BIT for BIT, including the
    dsCMatrix internals (``i`` / ``p`` / ``x`` / ``uplo`` / Dimnames), not merely
    to within a tolerance. That is what makes it safe to re-point every
    pre-existing assertion in test_ld_npz_to_rds.py from ``obj$ld`` to ``obj$R``.

    Coverage inside this one test:
      * ``lower_triangular=True``  (production banded / A.3 shape)
      * flag ABSENT + full matrix  (Path A.1 square shape)
      * the same lower-tri input re-converted at ``M3_LD_CONVERT_BLOCK=7`` so the
        n=64 case runs 10 x 10 tiles -- diagonal blocks, strictly-upper blocks and
        a 1-wide remainder block -- instead of the single-tile degenerate path
      * three unliftable variants (incl. the LAST row) so the drop + index remap
        runs on a non-trivial keep set
    """
    old_conv = _pre_change_converter(tmp_path)

    npz_low = tmp_path / "low.npz"
    npz_full = tmp_path / "full.npz"
    _make_npz(npz_low, n=64, lower_flag=True, unliftable_idx=(10, 33, 63))
    _make_npz(npz_full, n=64, lower_flag=None, unliftable_idx=(10, 33, 63))

    a = tmp_path / "old_low.rds"
    b = tmp_path / "new_low.rds"
    c = tmp_path / "new_low_block7.rds"
    afull = tmp_path / "old_full.rds"
    bfull = tmp_path / "new_full.rds"

    runs = [
        ("old lower", old_conv, npz_low, a, None),
        ("new lower", R_CONVERTER, npz_low, b, None),
        ("new lower block=7", R_CONVERTER, npz_low, c, {"M3_LD_CONVERT_BLOCK": "7"}),
        ("old full", old_conv, npz_full, afull, None),
        ("new full", R_CONVERTER, npz_full, bfull, None),
    ]
    for label, conv, npz, rds, extra in runs:
        res = _run_converter(
            rscript_or_skip, Path(conv), npz, rds, chain_38_to_37, extra_env=extra
        )
        assert res.returncode == 0, (
            f"{label} converter failed rc={res.returncode}:\n{res.stderr}\n{res.stdout}"
        )

    got = _run_r_json(
        rscript_or_skip, _COMPARE_R, [str(a), str(b), str(c), str(afull), str(bfull)]
    )

    # The fixture must be non-degenerate: variants really were dropped, and the
    # matrix really has off-diagonal content.
    assert got["n_var_dropped"] == 3, f"expected 3 liftover drops, got {got}"
    assert got["n_var_output"] == 61, f"expected 61 surviving variants, got {got}"
    assert got["nnz_old"] > 61, f"degenerate fixture (diagonal only): {got}"

    for key in ("lower", "lower_small_block", "full"):
        block = got[key]
        for field in ("R", "variants", "snp_ids", "provenance"):
            assert block[field] is True, (
                f"[{key}] obj${field} is NOT identical between the pre-change "
                f"converter and the block-bounded one: {got}"
            )

    # The removal, pinned in BOTH directions.
    assert got["old_has_ld"] is True, (
        "the 5ec33bd converter must still carry the dense ld field -- if it does "
        "not, this test's control is vacuous"
    )
    assert got["new_has_ld"] is False, "the new payload must NOT carry obj$ld"
    assert got["new_has_ld_full"] is False, "the new payload must NOT carry obj$ld"
    assert set(got["names_new"]) == {"R", "variants", "snp_ids", "provenance"}, got
    assert set(got["names_old"]) - set(got["names_new"]) == {"ld"}, got
    assert got["r_class_old"] == got["r_class_new"], (
        f"obj$R changed class: {got['r_class_old']} -> {got['r_class_new']}"
    )
    assert got["nnz_old"] == got["nnz_new"], got

    # NEGATIVE CONTROLS -- each perturbs exactly one surviving field and must
    # flip its own identical() to FALSE. Without these, four TRUEs above would be
    # evidence of nothing.
    for ctl in ("ctl_R", "ctl_variants", "ctl_snp_ids", "ctl_provenance"):
        assert got[ctl] is False, (
            f"{ctl}: perturbing that field did NOT break identical() -- the "
            f"equivalence assertion is structurally incapable of failing: {got}"
        )


# ===========================================================================
# 2. The read is memory-bounded
# ===========================================================================
def _max_rss_kb(rscript: Path, converter: Path, npz: Path, rds: Path, chain: Path) -> int:
    proc = subprocess.run(
        [
            str(GNU_TIME), "-v",
            str(rscript), str(converter), str(npz), str(rds), str(chain),
        ],
        capture_output=True,
        text=True,
        timeout=R_SUBPROCESS_TIMEOUT_S,
        env=_r_env(rscript),
    )
    assert proc.returncode == 0, (
        f"converter under /usr/bin/time failed rc={proc.returncode}:\n"
        f"{proc.stderr[-4000:]}\n{proc.stdout[-2000:]}"
    )
    m = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", proc.stderr)
    assert m, f"no maxRSS in /usr/bin/time -v output:\n{proc.stderr[-4000:]}"
    return int(m.group(1))


def test_read_is_memory_bounded(rscript_or_skip, chain_38_to_37, tmp_path):
    """maxRSS(new) <= 0.6 * maxRSS(old) on a PRODUCTION-SHAPED n=6000 panel.

    WHY BANDED, NOT DENSE-RANDOM. Every ``.npz`` this converter will ever read is
    written banded + lower-triangular by the frozen producer
    (``plink_ld_to_npz.py`` ``mode='banded'`` -> ``lower_triangular=True``;
    ``aou_ld_panel.py`` ``_write_a3_banded_correlation_bm``), and the ``.rds``
    payload has been a SPARSE ``Matrix`` since m3-02b precisely because of that.
    A dense-random fixture would measure a matrix this pipeline never produces.

    STATED PLAINLY RATHER THAN HIDDEN: the gain is shape-dependent, and the shape
    chosen here is the flattering one because it is the production one. Measured
    on this node, 260805-23d Task 5:

        banded n=6000 (production shape)  old 2290 MB -> new  805 MB  (0.351x)
        DENSE  n=3000 (never produced)    old  926 MB -> new  750 MB  (0.809x)

    On a pathologically dense panel the win collapses, because the irreducible
    dense float32 read and the SPARSE OUTPUT (which stores 12 bytes per retained
    entry against the old dense 8) then dominate. The 0.6 bound is therefore a
    claim about the panels this pipeline actually converts, not a universal one.

    Three independent guards, so a vacuous pass is not available:
      * ratio           -- new must be <= 0.6 x old (the plan's bound);
      * absolute margin -- old must exceed new by > 200 MB, so a both-tiny
                           measurement cannot satisfy the ratio by accident;
      * structural      -- new must sit under 10 x the ONE dense float32 copy the
                           reader cannot avoid (n**2 * 4 bytes). Shape-independent,
                           and NOT vacuous: the pre-change converter is asserted to
                           BREACH the very same bound in the same run (it measures
                           ~16.7x, holding four whole-matrix float64 temporaries on
                           top of that float32), so the guard is one this change
                           had to earn.
    """
    assert GNU_TIME.exists(), (
        f"{GNU_TIME} is required to measure maxRSS and is absent. This test does "
        "NOT skip: a new skip would breach the suite's skip budget and would hide "
        "the only measurement that shows the converter got leaner."
    )

    old_conv = _pre_change_converter(tmp_path)

    # Banded lower-triangular, exactly the production emit shape.
    rng = np.random.default_rng(11)
    n, band = MEM_TEST_N, MEM_TEST_BAND
    low = np.zeros((n, n), dtype="float32")
    for i in range(n):
        j0 = max(0, i - band)
        low[i, j0:i + 1] = (rng.standard_normal(i - j0 + 1) * 0.1).astype("float32")
    np.fill_diagonal(low, 1.0)
    npz = tmp_path / "banded6000.npz"
    np.savez_compressed(
        str(npz),
        ld=low,
        variant_ids=np.asarray(
            [f"chr16:{53_800_000 + i * 20}:A:G" for i in range(n)], dtype=str
        ),
        rsids=np.asarray([""] * n, dtype=str),
        lower_triangular=np.array([True]),
        allele_freq=np.linspace(0.01, 0.49, n).astype("float64"),
    )
    del low

    old_kb = _max_rss_kb(
        rscript_or_skip, old_conv, npz, tmp_path / "mem_old.rds", chain_38_to_37
    )
    new_kb = _max_rss_kb(
        rscript_or_skip, Path(R_CONVERTER), npz, tmp_path / "mem_new.rds", chain_38_to_37
    )
    dense_f32_kb = (n * n * 4) // 1024

    msg = (
        f"maxRSS old={old_kb} kB ({old_kb / 1024:.0f} MB), "
        f"new={new_kb} kB ({new_kb / 1024:.0f} MB), "
        f"ratio={new_kb / old_kb:.3f}, "
        f"one dense float32 copy at n={n} = {dense_f32_kb} kB "
        f"({dense_f32_kb / 1024:.0f} MB)"
    )
    assert new_kb <= 0.6 * old_kb, "converter is not memory-bounded: " + msg
    assert old_kb > new_kb + 200_000, "both measurements are tiny; " + msg
    # The structural guard, and its own control: the pre-change converter must
    # BREACH the bound the new one has to satisfy. Without this the 10x ceiling
    # could be a number nothing could ever fail.
    assert old_kb > 10 * dense_f32_kb, (
        "structural guard is vacuous -- even the pre-change converter satisfies "
        "it, so it discriminates nothing: " + msg
    )
    assert new_kb <= 10 * dense_f32_kb, (
        "the bounded reader is still holding whole-matrix copies on top of the "
        "one dense float32 the frozen .npz forces it to read: " + msg
    )


# ===========================================================================
# 3. No whole-matrix expression survives in the CODE
# ===========================================================================
_BANNED_WHOLE_MATRIX_EXPRESSIONS = (
    "tri + t(tri) - diag(diag(tri))",
    "(tri + t(tri)) / 2",
    'as(tri, "CsparseMatrix")',
)


def test_no_whole_matrix_expression_survives():
    """The n**2 expressions are gone from the code, and were present at 5ec33bd.

    Comment-stripped on purpose. A raw-text grep would be satisfiable by renaming
    a variable inside an explanatory comment, which is the "assertion structurally
    incapable of failing" class this whole remediation exists to close.
    """
    new_code = _strip_r_comments(Path(R_CONVERTER).read_text(encoding="utf-8"))
    old_src = _git_show(PRE_CHANGE_REF, CONVERTER_REL)
    old_code = _strip_r_comments(old_src)

    for expr in _BANNED_WHOLE_MATRIX_EXPRESSIONS:
        # NEGATIVE CONTROL: the pre-change code really does carry it, so the
        # assertion below has something to fail on.
        assert expr in old_code, (
            f"control is vacuous: {expr!r} is absent from the {PRE_CHANGE_REF} "
            f"source, so its absence from the new source proves nothing"
        )
        assert expr not in new_code, (
            f"{expr!r} still materialises a whole n x n matrix in "
            f"{CONVERTER_REL}"
        )

    # The persisted dense field, checked against the RAW text (unambiguous, and
    # it must not survive in a comment either).
    assert "ld         = tri" in old_src, "control is vacuous for the ld field"
    assert "ld         = tri" not in Path(R_CONVERTER).read_text(encoding="utf-8"), (
        "the dense back-compat `ld` field is still in the saved payload"
    )


# ===========================================================================
# 4. The reader's new stopifnot is live
# ===========================================================================
def test_reader_rejects_a_pre_change_rds(rscript_or_skip, chain_38_to_37, tmp_path):
    """A pre-change ``.rds`` fed to the EDITED ``_read_rds`` must raise.

    ``test_ld_npz_to_rds.py::_read_rds`` gained ``stopifnot(is.null(obj$ld))`` so
    the removal is pinned rather than merely untested. This is the observation
    that the pin can fail: build the payload the OLD converter writes, hand it to
    the very helper every pre-existing behaviour test runs through, and require a
    RuntimeError. A pin nobody has seen fail is decoration.
    """
    old_conv = _pre_change_converter(tmp_path)
    npz = tmp_path / "pre_change.npz"
    _make_npz(npz, n=16, lower_flag=True)
    old_rds = tmp_path / "pre_change.rds"
    res = _run_converter(rscript_or_skip, old_conv, npz, old_rds, chain_38_to_37)
    assert res.returncode == 0, f"pre-change converter failed: {res.stderr}"

    with pytest.raises(RuntimeError):
        _read_rds(rscript_or_skip, old_rds)

    # And the SAME helper must accept the new payload -- otherwise the pin above
    # would pass simply because _read_rds is broken for every input.
    new_rds = tmp_path / "post_change.rds"
    res = _run_converter(rscript_or_skip, Path(R_CONVERTER), npz, new_rds, chain_38_to_37)
    assert res.returncode == 0, f"new converter failed: {res.stderr}"
    payload = _read_rds(rscript_or_skip, new_rds)
    assert payload["ld_rows"] == payload["ld_cols"] > 0, payload
    assert payload["ld_symmetric"] is True, payload
