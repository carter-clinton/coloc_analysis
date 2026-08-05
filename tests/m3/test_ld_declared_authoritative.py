"""tests/m3/test_ld_declared_authoritative.py -- 260805-23d Task 2 (T-A 1/2 + T-T).

THE PRODUCTION-THRESHOLD ACCEPTANCE SUITE for the m3-04c blast radius.

WHY THIS MODULE EXISTS AT ALL. ``tests/m3/test_ld_read_path.py`` pins
``MIN_LD_OVERLAP <- 1L; MIN_LD_COVERAGE <- 0.0; MIN_LD_MIN_USE <- 1L`` in all 8
of its tests -- the quality gate is DISABLED in every one of them, so that suite
is *structurally incapable* of observing production behaviour. Both blockers
below live entirely inside the gate, which is why 548 green tests saw neither.

    BLOCKER-A -- ``--ld-file`` was a PREFERENCE, not a mandate. The candidate
      loop only ``return``s a candidate that clears the gate (``:216``); on
      failure it fell through to the ``--ld-dir`` reconstruction, found the
      legacy 1kG panel and returned THAT with a success status. Reproduced at
      50 / 0.5 / 10:  declared ``AFR_aou/m2_region_00067.rds``
      -> opened ``AFR/FTO_16q12.rds`` -> ``ld_loaded;overlap_ok;200;1.000``.
      Plus ``best_partial <- list(...)`` (``:237``) overwrote UNCONDITIONALLY,
      so a declared panel at 40/100 lost to a dir candidate at 20/100.

    BLOCKER-B -- m3-04c Task 1b removed a pin that had been silently holding
      every EUR fit at ``{ld_dir}/EUR/{region}.rds``. Un-pinned, an EUR fit
      moves the moment ``EUR_ukbb_pub/`` exists: r[1,2] 0.1 -> 0.9 with
      ``ld_status`` BYTE-IDENTICAL. Track A is in submission.

THE STANDING RULE (m3-04c process note: "a green assertion is evidence only if
you have seen it fail"). Every load-bearing assertion here has a NEGATIVE
CONTROL, and three of them are PERMANENT and in-suite: they re-run the very same
fixture against the PRE-CHANGE loader recovered with ``git show 5ec33bd:`` and
assert the DEFECTIVE outcome. If anyone ever neuters a fixture (identical
panels, permissive thresholds), those controls go red.

NO-SKIP RULE (inherited from must_have A6): ``_require_m3_r_toolchain()`` ERRORS
rather than skipping when the m3-r-ld marker env is present. A skip here means a
mis-wired harness and is treated as a FAILURE.
"""
from __future__ import annotations

import gzip
import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

# Make sibling test modules importable (tests/m3 on sys.path) so we can reuse the
# stitch test's R-toolchain discovery + loader-prefix extractor. This is the
# established seam (test_ld_read_path.py already imports it the same way), not a
# new coupling.
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from test_stitch_subregions_to_rds import (  # noqa: E402
    R_SUBPROCESS_TIMEOUT_S,
    _loader_functions_only,
    _require_m3_r_toolchain,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUSIE_R_REL = "src/legacy/region_analysis/scripts/run_susie_rss.R"
SUSIE_R = PROJECT_ROOT / SUSIE_R_REL

# The commit this remediation started from -- the source that carries BOTH
# defects. Used as the permanent negative control below.
PRE_CHANGE_REF = "5ec33bd"


# --------------------------------------------------------------------------
# THE PRODUCTION THRESHOLDS -- read, never hardcoded
# --------------------------------------------------------------------------
_POLICY = yaml.safe_load(
    (PROJECT_ROOT / "config" / "susie_policy.yaml").read_text()
)["susie"]
MIN_LD_OVERLAP = int(_POLICY["min_ld_overlap"])      # 50
MIN_LD_COVERAGE = float(_POLICY["min_ld_coverage"])  # 0.5
MIN_LD_MIN_USE = int(_POLICY["min_ld_min_use"])      # 10

# The fixed subset every panel is matched against. 300 is chosen so an overlap of
# 200 (the value the blast-radius reproduction used) is both reachable AND clears
# MIN_LD_COVERAGE = 0.5, while 40 / 20 / 12 / 3 all sit strictly below the gate.
N_SUBSET = 300

# 260805-23d Task 3: the FULL-SCRIPT tests build their sumstats in Python while the
# panels are built by the R preamble, so the coordinate system has to be single
# sourced or the two halves silently stop overlapping (an overlap-0 fixture would
# make every end-to-end assertion vacuous). Interpolated into the preamble below.
BASE_POS = 53809247
CHROM = "16"
E2E_REGION = "FTO_16q12"


def _offset_for_overlap(overlap: int) -> int:
    """``id_offset`` that makes a full-width panel overlap the subset by exactly
    ``overlap`` variants. Panel ids are rs{off+1}..rs{off+N_SUBSET}; the subset is
    rs1..rs{N_SUBSET}; so the intersection has N_SUBSET - off elements."""
    assert 0 <= overlap <= N_SUBSET
    return N_SUBSET - overlap


# --------------------------------------------------------------------------
# R harness (BEHAVIOURAL -- this module runs the REAL loader, always)
# --------------------------------------------------------------------------
@pytest.fixture(scope="session")
def r_toolchain() -> tuple[Path, dict]:
    return _require_m3_r_toolchain()


_R_PREAMBLE_TEMPLATE = r'''
suppressPackageStartupMessages(library(Matrix))
suppressWarnings(suppressMessages(source("__LOADER_FUNCS__")))
MIN_LD_OVERLAP  <- __MIN_LD_OVERLAP__L
MIN_LD_COVERAGE <- __MIN_LD_COVERAGE__
MIN_LD_MIN_USE  <- __MIN_LD_MIN_USE__L

N_SUBSET <- __N_SUBSET__L
BASE_POS <- __BASE_POS__L
CHROM    <- "__CHROM__"

vid <- function(i) paste0("rs", i)

# A panel of `n_ld` variants whose ids are rs{id_offset+1}..rs{id_offset+n_ld},
# so the realized overlap against mk_subset() is exactly N_SUBSET - id_offset.
# `r12` is the off-diagonal used to prove WHICH panel's numbers reached the fit.
make_panel <- function(path, n_ld = N_SUBSET, id_offset = 0L, r12 = 0.4) {
  ids <- seq_len(n_ld) + id_offset
  R <- diag(n_ld)
  if (n_ld >= 2) { R[1, 2] <- r12; R[2, 1] <- r12 }
  variants <- data.frame(SNP_ID = vid(ids), CHR = rep(CHROM, n_ld),
                         POS = BASE_POS + ids, stringsAsFactors = FALSE)
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  saveRDS(list(R = R, variants = variants, status = "ld_loaded"), path)
  invisible(path)
}

# Exactly what src/snakemake/scripts/make_identity_ld_refs.R:64 writes.
make_identity_panel <- function(path) {
  ids <- seq_len(N_SUBSET)
  variants <- data.frame(SNP_ID = vid(ids), CHR = rep(CHROM, N_SUBSET),
                         POS = BASE_POS + ids, stringsAsFactors = FALSE)
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  saveRDS(list(R = NULL, use_identity = TRUE, status = "identity",
               variants = variants), path)
  invisible(path)
}

mk_subset <- function() {
  ids <- seq_len(N_SUBSET)
  data.frame(SNP_ID = vid(ids), CHR = rep(CHROM, N_SUBSET),
             POS = BASE_POS + ids, stringsAsFactors = FALSE)
}

emit <- function(res, tag) {
  cat(sprintf("%s_SOURCE=%s\n", tag,
              if (is.null(res$source)) "<NULL>" else res$source))
  cat(sprintf("%s_RNULL=%s\n", tag, is.null(res$R)))
  cat(sprintf("%s_STATUS=%s\n", tag,
              if (is.null(res$status)) "<NULL>" else res$status))
  cat(sprintf("%s_NROW=%s\n", tag,
              if (is.null(res$R)) "<NULL>" else nrow(res$R)))
  cat(sprintf("%s_OVERLAP=%s\n", tag,
              if (is.null(res$overlap)) "<NULL>" else as.character(res$overlap)))
  cat(sprintf("%s_COVERAGE=%s\n", tag,
              if (is.null(res$coverage)) "<NULL>" else sprintf("%.6f", res$coverage)))
  cat(sprintf("%s_REJECTED=%s\n", tag, isTRUE(res$declared_rejected)))
  cat(sprintf("%s_REASON=%s\n", tag,
              if (is.null(res$reject_reason)) "<NULL>" else res$reject_reason))
  cat(sprintf("%s_DECLARED=%s\n", tag,
              if (is.null(res$declared)) "<NULL>" else res$declared))
  cat(sprintf("%s_R12=%s\n", tag,
              if (is.null(res$R) || nrow(res$R) < 2) "<NULL>"
              else sprintf("%.6f", res$R[1, 2])))
}
'''


def _render_preamble(loader_funcs: Path) -> str:
    return (
        _R_PREAMBLE_TEMPLATE
        .replace("__LOADER_FUNCS__", str(loader_funcs))
        .replace("__MIN_LD_OVERLAP__", str(MIN_LD_OVERLAP))
        .replace("__MIN_LD_COVERAGE__", repr(MIN_LD_COVERAGE))
        .replace("__MIN_LD_MIN_USE__", str(MIN_LD_MIN_USE))
        .replace("__N_SUBSET__", str(N_SUBSET))
        .replace("__BASE_POS__", str(BASE_POS))
        .replace("__CHROM__", CHROM)
    )


def _loader_prefix_from_text(src_text: str, out_path: Path) -> Path:
    """The function-definition PREFIX of an arbitrary run_susie_rss.R text.

    Same cut rule as ``_loader_functions_only`` (up to ``option_list <-``), but
    driven by supplied source so a historical revision can be sourced too."""
    lines = src_text.splitlines()
    cut = len(lines)
    for i, line in enumerate(lines):
        if line.strip().startswith("option_list <-"):
            cut = i
            break
    assert cut < len(lines), "no top-level 'option_list <-' marker in the source"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines[:cut]) + "\n")
    return out_path


def _pre_change_loader_prefix(tmp_path: Path) -> Path:
    """The PRE-CHANGE (``5ec33bd``) loader prefix -- the source carrying both
    defects. This is the negative-control substrate."""
    proc = subprocess.run(
        ["git", "show", f"{PRE_CHANGE_REF}:{SUSIE_R_REL}"],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, (
        f"git show {PRE_CHANGE_REF}:{SUSIE_R_REL} failed: {proc.stderr}"
    )
    assert "load_ld_matrix <- function" in proc.stdout
    return _loader_prefix_from_text(
        proc.stdout, tmp_path / "pre_change" / "loader_funcs_only.R"
    )


def _run_r(rscript: Path, env: dict, tmp_path: Path, body: str,
           name: str = "probe.R", loader_funcs: Path | None = None) -> dict:
    """Source a loader prefix, run ``body``, return the emitted KEY=VALUE map.

    Raises on a non-zero R exit, so an ``unused argument (authoritative = ...)``
    surfaces as a FAILURE rather than as a silently empty result. (Task 3 adds
    the stop()-based tests; those get their own rc-tolerant runner, and this one
    is deliberately NOT weakened.)"""
    if loader_funcs is None:
        loader_funcs = _loader_functions_only(tmp_path)
    script = tmp_path / name
    script.write_text(_render_preamble(loader_funcs) + "\n" + body)
    proc = subprocess.run(
        [str(rscript), str(script)], capture_output=True, text=True,
        timeout=R_SUBPROCESS_TIMEOUT_S, env=env,
    )
    assert proc.returncode == 0, (
        f"R loader probe failed (rc={proc.returncode}).\n"
        f"--- stderr ---\n{proc.stderr}\n--- stdout ---\n{proc.stdout}"
    )
    out = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip()
    return out


# --------------------------------------------------------------------------
# 260805-23d Task 3 harness -- the hard stop() and its wiring
# --------------------------------------------------------------------------
def _run_r_allow_fail(rscript: Path, env: dict, tmp_path: Path, body: str,
                      name: str = "probe.R",
                      loader_funcs: Path | None = None
                      ) -> subprocess.CompletedProcess:
    """Like ``_run_r`` but TOLERATES a non-zero exit; returns the process.

    Task 3's whole subject is a hard ``stop()``, so its runner must be able to
    OBSERVE ``rc != 0``. ``_run_r`` is deliberately NOT weakened to accommodate
    it: a Task-2 loader probe that dies is still a failure there.
    """
    if loader_funcs is None:
        loader_funcs = _loader_functions_only(tmp_path)
    script = tmp_path / name
    script.write_text(_render_preamble(loader_funcs) + "\n" + body)
    return subprocess.run(
        [str(rscript), str(script)], capture_output=True, text=True,
        timeout=R_SUBPROCESS_TIMEOUT_S, env=env,
    )


REACHED = "REACHED_PAST_THE_ASSERT"

# The four reason codes the loader can emit, with a realized (overlap, coverage)
# for each. Kept as data so a fifth reason cannot be added to the R source
# without someone deciding whether it stops.
REJECT_CASES = (
    ("unreadable", 0, 0),
    ("no_matrix", 0, 0),
    ("use_identity", 0, 0),
    ("overlap_below_min_use", 3, 0.01),
)


def _rejection_body(reason: str, overlap, coverage, declared: str,
                    authoritative: str = "TRUE") -> str:
    """An R body that hands a SYNTHETIC rejection (exactly the shape
    ``load_ld_matrix`` returns) to the assert, then tries to run past it."""
    return (
        f'res <- list(R = NULL, source = "{declared}",\n'
        f'            status = "ld_declared_rejected;{reason}",\n'
        f'            declared_rejected = TRUE, reject_reason = "{reason}",\n'
        f'            declared = "{declared}", overlap = {overlap}, coverage = {coverage})\n'
        f'assert_declared_ld_authoritative(res, {authoritative}, "m2_region_00067", "AFR",\n'
        f'                                 MIN_LD_OVERLAP, MIN_LD_COVERAGE, MIN_LD_MIN_USE)\n'
        f'cat("{REACHED}\\n")\n'
    )


# --------------------------------------------------------------------------
# FULL-SCRIPT harness -- run_susie_rss.R end to end, real inputs
# --------------------------------------------------------------------------
def _make_full_script_inputs(tmp_path: Path) -> dict:
    """The MINIMUM real inputs run_susie_rss.R needs to reach the LD load.

    A `gzip`-compressed sumstats .tsv.bgz (the script reads it with
    ``gunzip -c``, so plain gzip is what it actually requires), a 4-column
    regions CSV, and the REAL ``config/susie_policy.yaml``. No --variant-list,
    so the catalog branches stay out of the picture.

    The variant ids/coords mirror the R preamble's ``mk_subset()`` exactly --
    both are driven by BASE_POS / CHROM / N_SUBSET -- so panel-vs-sumstats
    overlap is controlled purely by a panel's ``id_offset``.
    """
    root = tmp_path / "e2e"
    root.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20260805)
    rows = ["\t".join(("SNP_ID", "CHR", "POS", "BETA", "SE", "N"))]
    for i in range(1, N_SUBSET + 1):
        rows.append("\t".join((
            f"rs{i}", CHROM, str(BASE_POS + i),
            f"{rng.gauss(0.0, 0.02):.6f}", "0.020000", "100000",
        )))
    sumstats = root / "sumstats.tsv.bgz"
    with gzip.open(sumstats, "wt") as fh:
        fh.write("\n".join(rows) + "\n")
    regions_csv = root / "regions.csv"
    regions_csv.write_text(
        "region_id,chr,start,end\n"
        f"{E2E_REGION},{CHROM},{BASE_POS},{BASE_POS + 100000}\n"
    )
    return {"root": root, "sumstats": sumstats, "regions_csv": regions_csv}


def _build_panels(rscript: Path, env: dict, tmp_path: Path,
                  specs: list[tuple[Path, int, float]], name: str) -> None:
    """Write real .rds panels via the preamble's own ``make_panel``.

    ``specs`` is (path, realized overlap against the subset, r[1,2])."""
    body = "".join(
        f'make_panel("{p}", id_offset = {_offset_for_overlap(ov)}L, r12 = {r12})\n'
        for p, ov, r12 in specs
    )
    _run_r(rscript, env, tmp_path, body + 'cat("PANELS=ok\\n")\n', name=name)


def _run_full_script(rscript: Path, env: dict, inputs: dict, out_json: Path, *,
                     ancestry: str, authoritative: str, ld_dir: Path,
                     ld_file: Path | str | None,
                     ) -> subprocess.CompletedProcess:
    """Invoke the REAL run_susie_rss.R. rc-tolerant on purpose."""
    cmd = [
        str(rscript), str(SUSIE_R),
        "--sumstats", str(inputs["sumstats"]),
        "--trait", "TEST_TRAIT",
        "--ancestry", ancestry,
        "--method", "susie_rss",
        "--region", E2E_REGION,
        "--regions-csv", str(inputs["regions_csv"]),
        "--ld-dir", str(ld_dir),
        "--ld-authoritative", authoritative,
        "--policy", str(PROJECT_ROOT / "config" / "susie_policy.yaml"),
        "--output", str(out_json),
    ]
    if ld_file is not None:
        cmd += ["--ld-file", str(ld_file)]
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=R_SUBPROCESS_TIMEOUT_S, env=env,
                          cwd=str(PROJECT_ROOT))


def _balanced_block_end(text: str, start_idx: int, opener: str = "{",
                        closer: str = "}") -> int:
    """Index just past the balanced ``opener``/``closer`` block that begins at
    or after ``start_idx``."""
    open_idx = text.index(opener, start_idx)
    depth = 0
    for k in range(open_idx, len(text)):
        if text[k] == opener:
            depth += 1
        elif text[k] == closer:
            depth -= 1
            if depth == 0:
                return k + 1
    raise AssertionError("unbalanced block")


def _assert_wiring(src: str) -> None:
    """Every SOURCE-LEVEL wiring claim of Task 3, as one reusable predicate.

    Factored out so the PERMANENT negative control can run the IDENTICAL
    assertions against ``git show 5ec33bd:`` and be seen to fail. An assertion
    that has only ever been run against the source it was written for is not
    evidence (m3-04c process note)."""
    marker = re.search(r"^option_list <-", src, re.M)
    assert marker is not None, "no top-level 'option_list <-' marker"

    # 1. DEFINED exactly once, and ABOVE the option_list marker -- otherwise
    #    _loader_functions_only() slices it away and every behavioural test in
    #    this family silently degrades to source-grep theatre.
    defs = [m.start() for m in re.finditer(
        r"^assert_declared_ld_authoritative <- function", src, re.M)]
    assert len(defs) == 1, f"expected 1 definition, found {len(defs)}"
    assert defs[0] < marker.start(), (
        "assert_declared_ld_authoritative() is defined BELOW the "
        "'option_list <-' marker, so _loader_functions_only() cuts it away and "
        "it cannot be invoked by any test in this suite"
    )

    # 2. Called exactly once, on ld_result.
    calls = [m.start() for m in re.finditer(
        r"assert_declared_ld_authoritative\(ld_result", src)]
    assert len(calls) == 1, (
        f"expected exactly 1 call site on ld_result, found {len(calls)}"
    )

    # 3. Sited AFTER the retry loop closes and BEFORE the subset shrink, so no
    #    fit can be built on a rejected panel and no retry can outrun the gate.
    repeat_idx = src.index("repeat {")
    repeat_end = _balanced_block_end(src, repeat_idx)
    shrink_idx = src.index("if (!is.null(ld_result$subset_idx))")
    assert repeat_end < calls[0] < shrink_idx, (
        "the assert must sit between the end of the retry loop and the subset "
        f"shrink (loop ends {repeat_end}, call {calls[0]}, shrink {shrink_idx})"
    )

    # 4. `authoritative` is THREADED into the load call -- on ONE line, with
    #    ld_file still last, so the pre-existing T2.2 regex keeps matching.
    assert re.search(
        r"load_ld_matrix\([^\n]*authoritative\s*=\s*ld_authoritative[^\n]*"
        r"ld_file\s*=\s*opt\$`ld-file`", src), (
        "the sole load_ld_matrix call site must pass "
        "authoritative = ld_authoritative BEFORE ld_file = opt$`ld-file`, on "
        "one line -- without it --ld-authoritative is parsed and then ignored, "
        "every ancestry runs on the TRUE default, and BLOCKER-B is open"
    )


# ==========================================================================
# H -- the assert STOPS, loudly and greppably, on every rejection reason
# ==========================================================================
@pytest.mark.parametrize("reason,overlap,coverage", REJECT_CASES)
def test_assert_stops_on_every_rejection_reason(
    r_toolchain, tmp_path, reason, overlap, coverage
):
    """H. A structured rejection from ``load_ld_matrix`` must ABORT the region.

    WHY A HARD stop() AND NOT A STATUS FIELD (settled in the plan's
    <failure_semantics_decision>): a written JSON at rc 0 makes Snakemake mark
    the job DONE, ``snakemake all`` completes green, and the gate degrades into
    a post-hoc scan someone has to remember to run. That is the exact failure
    class of this entire sweep -- the ``resolved == opened`` receipt ALREADY
    existed in every region's JSON and nobody read it. A stop() makes the DAG
    itself the gate; with ``--keep-going`` the blast radius is one region.

    NEGATIVE CONTROL: ``test_assert_is_silent_on_an_accepted_result`` runs the
    same function on an ACCEPTED result and requires rc 0 with nothing printed
    -- so "it stops" is observably violable rather than "it always stops".
    """
    rscript, env = r_toolchain
    declared = str(tmp_path / "ld_reference" / "AFR_aou" / "m2_region_00067.rds")
    proc = _run_r_allow_fail(
        rscript, env, tmp_path,
        _rejection_body(reason, overlap, coverage, declared),
        name=f"tH_{reason}.R",
    )
    assert proc.returncode != 0, (
        f"reason={reason} did NOT abort the region (rc=0). A written JSON at "
        f"rc 0 is a job Snakemake marks DONE.\nstdout:\n{proc.stdout}"
    )
    assert REACHED not in proc.stdout, (
        f"execution continued past the assert for reason={reason}"
    )
    err = proc.stderr
    assert "LD_DECLARED_REJECTED:" in err, (
        f"the machine-greppable prefix is missing.\nstderr:\n{err}"
    )
    for key in (f"reason={reason}", f"declared={declared}",
                "region=m2_region_00067", "ancestry=AFR",
                f"overlap={overlap}", "coverage=",
                f"min_ld_overlap={MIN_LD_OVERLAP}",
                f"min_ld_coverage={MIN_LD_COVERAGE}",
                f"min_ld_min_use={MIN_LD_MIN_USE}",
                "remedy="):
        assert key in err, f"missing {key!r} from the abort message:\n{err}"


def test_assert_is_silent_on_an_accepted_result(r_toolchain, tmp_path):
    """H-control. The same function on an ACCEPTED result exits 0 and says
    nothing. Without this, "the assert stops" would be satisfied by a function
    that stops unconditionally."""
    rscript, env = r_toolchain
    body = (
        'res <- list(R = diag(3), source = "/p/declared.rds",\n'
        '            status = "ld_loaded;overlap_ok;300;1.000",\n'
        '            overlap = 300, coverage = 1)\n'
        'assert_declared_ld_authoritative(res, TRUE, "m2_region_00067", "AFR",\n'
        '                                 MIN_LD_OVERLAP, MIN_LD_COVERAGE, MIN_LD_MIN_USE)\n'
        f'cat("{REACHED}\\n")\n'
    )
    proc = _run_r_allow_fail(rscript, env, tmp_path, body, name="tH_ok.R")
    assert proc.returncode == 0, proc.stderr
    assert REACHED in proc.stdout
    assert "LD_DECLARED_REJECTED" not in proc.stderr, proc.stderr


# ==========================================================================
# I -- IT MUST NOT FALSE-TRIP. In this repo that is the bigger risk.
# ==========================================================================
def test_assert_does_not_false_trip_on_legitimate_results(r_toolchain, tmp_path):
    """I. A too-eager gate is historically the WORSE failure here (cf. the P3
    gsutil precedent, where a too-narrow absent-detection would have stopped
    every legitimate first region). Enumerate the legitimate shapes and require
    silence on all of them, in ONE process -- if any one stopped, none of the
    later ones would print.

    Covers: not authoritative at all (EUR / TRANS can NEVER be aborted by this
    path); an accepted gate pass; an accepted partial_overlap; the legacy
    ``ld_dir_missing`` / ``ld_missing`` / ``ld_overlap_insufficient`` guards
    that a caller supplying NO --ld-file gets; a bare legacy 3-field result;
    and an explicit ``declared_rejected = FALSE``.

    NEGATIVE CONTROL: ``test_assert_does_fire_on_the_one_case_that_should``
    feeds the SAME runner the one shape that must abort.
    """
    rscript, env = r_toolchain
    cases = [
        # (tag, result expr, authoritative)
        ("NOT_AUTH_REJECTION",
         'list(R = NULL, source = "/p/d.rds", status = "ld_declared_rejected;unreadable",'
         ' declared_rejected = TRUE, reject_reason = "unreadable", declared = "/p/d.rds",'
         ' overlap = 0, coverage = 0)', "FALSE"),
        # a DIFFERENT reason code, same regime: no reason can abort off the
        # allow-list, so EUR / TRANS are unreachable by this path entirely
        ("NOT_AUTH_REJECTION_USE_IDENTITY",
         'list(R = NULL, source = "/p/d.rds", status = "ld_declared_rejected;use_identity",'
         ' declared_rejected = TRUE, reject_reason = "use_identity", declared = "/p/d.rds",'
         ' overlap = 0, coverage = 0)', "FALSE"),
        ("GATE_PASS",
         'list(R = diag(3), source = "/p/d.rds", status = "ld_loaded;overlap_ok;300;1.000",'
         ' overlap = 300, coverage = 1)', "TRUE"),
        ("PARTIAL_OVERLAP",
         'list(R = diag(3), source = "/p/d.rds", status = "ld_loaded;partial_overlap;12;0.040",'
         ' overlap = 12, coverage = 0.04)', "TRUE"),
        # what a caller that supplied NO --ld-file gets back
        ("LEGACY_LD_DIR_MISSING",
         'list(R = NULL, source = NULL, status = "ld_dir_missing")', "TRUE"),
        ("LEGACY_LD_MISSING",
         'list(R = NULL, source = NULL, status = "ld_missing", overlap = 0, coverage = 0)',
         "TRUE"),
        ("LEGACY_OVERLAP_INSUFFICIENT",
         'list(R = NULL, source = NULL, status = "ld_overlap_insufficient",'
         ' overlap = 4, coverage = 0.013)', "TRUE"),
        ("LEGACY_BARE_THREE_FIELD",
         'list(R = diag(2), source = "/p/legacy.rds", status = "ld_loaded")', "TRUE"),
        ("EXPLICIT_FALSE_FLAG",
         'list(R = diag(2), source = "/p/d.rds", status = "ld_loaded",'
         ' declared_rejected = FALSE, reject_reason = NULL)', "TRUE"),
    ]
    body = "".join(
        f'assert_declared_ld_authoritative({expr}, {auth}, "m2_region_00067", "AFR",\n'
        f'                                 MIN_LD_OVERLAP, MIN_LD_COVERAGE, MIN_LD_MIN_USE)\n'
        f'cat("OK_{tag}\\n")\n'
        for tag, expr, auth in cases
    )
    proc = _run_r_allow_fail(rscript, env, tmp_path, body, name="tI.R")
    assert proc.returncode == 0, (
        "the assert FALSE-TRIPPED on a legitimate result -- a too-eager gate "
        f"stops legitimate regions.\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    for tag, _, _ in cases:
        assert f"OK_{tag}" in proc.stdout, (
            f"the assert fired on {tag}, which is a legitimate result\n"
            f"stderr:\n{proc.stderr}"
        )
    assert "LD_DECLARED_REJECTED" not in proc.stderr, proc.stderr


def test_assert_does_fire_on_the_one_case_that_should(r_toolchain, tmp_path):
    """I-control. Same runner, same message shape, the ONE shape that must
    abort: ``declared_rejected = TRUE`` AND authoritative. Without this, test I
    would be satisfied by a function whose body is ``invisible(TRUE)``."""
    rscript, env = r_toolchain
    body = (
        'assert_declared_ld_authoritative('
        'list(R = NULL, source = "/p/d.rds", status = "ld_declared_rejected;no_matrix",'
        ' declared_rejected = TRUE, reject_reason = "no_matrix", declared = "/p/d.rds",'
        ' overlap = 0, coverage = 0), TRUE, "m2_region_00067", "AFR",\n'
        '                                 MIN_LD_OVERLAP, MIN_LD_COVERAGE, MIN_LD_MIN_USE)\n'
        'cat("OK_SHOULD_NOT_PRINT\\n")\n'
    )
    proc = _run_r_allow_fail(rscript, env, tmp_path, body, name="tI_ctl.R")
    assert proc.returncode != 0, proc.stdout
    assert "OK_SHOULD_NOT_PRINT" not in proc.stdout
    assert "LD_DECLARED_REJECTED:" in proc.stderr


# ==========================================================================
# J -- the wiring, pinned at source, with a git-show negative control
# ==========================================================================
def test_main_script_calls_the_assert_after_the_retry_loop(tmp_path):
    """J. The assert exists once, is defined ABOVE ``option_list <-``, is called
    exactly once, sits between the retry loop and the subset shrink, and
    ``authoritative = ld_authoritative`` is threaded into the load call.

    The placement half is not cosmetic: ``_loader_functions_only()`` slices
    run_susie_rss.R at the FIRST line starting ``option_list <-``. A definition
    below that marker is unreachable from every behavioural test in this file,
    and tests H and I would silently become grep-only.

    NEGATIVE CONTROL (PERMANENT): the IDENTICAL predicate against the
    pre-change ``5ec33bd`` source recovered by ``git show``. It must FAIL there.
    """
    _assert_wiring(SUSIE_R.read_text())

    # ...and the placement claim asserted through the REAL slicer, not by
    # reasoning about it.
    sliced = _loader_functions_only(tmp_path).read_text()
    assert "assert_declared_ld_authoritative <- function" in sliced, (
        "the function did not survive _loader_functions_only()'s cut at "
        "'option_list <-' -- move the definition ABOVE that marker"
    )

    # NEGATIVE CONTROL
    proc = subprocess.run(
        ["git", "show", f"{PRE_CHANGE_REF}:{SUSIE_R_REL}"],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    with pytest.raises(AssertionError):
        _assert_wiring(proc.stdout)


# ==========================================================================
# K -- END TO END: a rejected declared panel aborts the region
# ==========================================================================
def test_end_to_end_declared_rejection_aborts_the_region(r_toolchain, tmp_path):
    """K. The real script, real inputs, corrupt declared panel, AFR,
    ``--ld-authoritative true``: rc != 0, the greppable prefix on stderr, and
    NO output JSON -- so Snakemake fails the job instead of marking it DONE.

    A valid ``{ld_dir}/AFR/`` panel that clears the gate outright is present the
    whole time: the point is that it is DELIBERATELY not taken.

    NEGATIVE CONTROL (in-test): the byte-identical invocation with
    ``--ld-authoritative false`` -> rc 0, a JSON IS written, and it was written
    on the dir panel. That is today's behaviour and it is the proof the
    assertion above can fail.
    """
    rscript, env = r_toolchain
    inputs = _make_full_script_inputs(tmp_path)
    ld_dir = inputs["root"] / "ld_reference"
    declared = ld_dir / "AFR_aou" / "m2_region_00040__sub14.rds"
    dirpanel = ld_dir / "AFR" / f"{E2E_REGION}.rds"
    _build_panels(rscript, env, tmp_path, [(dirpanel, 300, 0.10)], "tK_panels.R")
    declared.parent.mkdir(parents=True, exist_ok=True)
    declared.write_bytes(os.urandom(64))

    out_auth = inputs["root"] / "auth.json"
    proc = _run_full_script(rscript, env, inputs, out_auth, ancestry="AFR",
                            authoritative="true", ld_dir=ld_dir,
                            ld_file=declared)
    assert proc.returncode != 0, (
        "a corrupt DECLARED panel produced a completed region at rc 0 -- "
        "Snakemake would mark this job DONE\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    assert "LD_DECLARED_REJECTED:" in proc.stderr, proc.stderr
    assert "reason=unreadable" in proc.stderr, proc.stderr
    assert f"declared={declared}" in proc.stderr, proc.stderr
    assert not out_auth.exists(), (
        "an output JSON was written for a rejected declared panel"
    )
    assert not Path(str(out_auth).replace(".json", ".fit.rds")).exists()

    # NEGATIVE CONTROL -- identical invocation, authoritative FALSE
    out_noauth = inputs["root"] / "noauth.json"
    proc2 = _run_full_script(rscript, env, inputs, out_noauth, ancestry="AFR",
                             authoritative="false", ld_dir=ld_dir,
                             ld_file=declared)
    assert proc2.returncode == 0, proc2.stderr
    assert out_noauth.exists(), "no JSON written off the allow-list"
    payload = json.loads(out_noauth.read_text())
    assert payload["ld_matrix"] == str(dirpanel), payload["ld_matrix"]
    assert payload["ld_overlap"] == 300


# ==========================================================================
# L -- END TO END: the BLOCKER-B proof, through the REAL script
# ==========================================================================
def test_end_to_end_eur_ignores_the_declared_panel_and_afr_opens_it(
    r_toolchain, tmp_path
):
    """L. THE manuscript-protecting proof, at the level that actually ships.

    Test G proves the property of ``load_ld_matrix``. That is NOT the same
    claim: at 51a60ca the loader honoured ``authoritative`` correctly while the
    SOLE CALL SITE still read
    ``load_ld_matrix(..., ld_file = opt$`ld-file`)`` -- so the formal defaulted
    to TRUE, every ancestry ran authoritative, and the real script opened
    ``EUR_ukbb_pub`` under ``--ld-authoritative false`` (measured: ld_overlap
    300, i.e. the declared panel). ``[[feedback_declared_input_is_not_the_read_path]]``
    in its exact dual: a parsed flag that nothing consumes.

    Fixture: panels distinguished by BOTH r[1,2] AND realized overlap, so the
    discriminator is a NUMBER the fit was computed from (``ld_overlap``), not
    only a path string a receipt could mislabel.
        declared EUR_ukbb_pub -> overlap 300  (3f431ab could not reach this)
        dir      EUR/         -> overlap 200  (3f431ab's read path)

    NEGATIVE CONTROL (in-test): the same EUR invocation with
    ``--ld-authoritative true`` opens the declared panel at overlap 300 -- the
    precise movement the blast radius measured. The EUR assertion is therefore
    observably violable.
    """
    rscript, env = r_toolchain
    inputs = _make_full_script_inputs(tmp_path)
    ld_dir = inputs["root"] / "ld_reference"
    eur_declared = ld_dir / "EUR_ukbb_pub" / f"{E2E_REGION}.rds"
    eur_dir = ld_dir / "EUR" / f"{E2E_REGION}.rds"
    afr_declared = ld_dir / "AFR_aou" / "m2_region_00040__sub14.rds"
    afr_dir = ld_dir / "AFR" / f"{E2E_REGION}.rds"
    _build_panels(rscript, env, tmp_path, [
        (eur_declared, 300, 0.90), (eur_dir, 200, 0.10),
        (afr_declared, 300, 0.90), (afr_dir, 200, 0.10),
    ], "tL_panels.R")

    def _run(tag, ancestry, authoritative, declared):
        out = inputs["root"] / f"{tag}.json"
        proc = _run_full_script(rscript, env, inputs, out, ancestry=ancestry,
                                authoritative=authoritative, ld_dir=ld_dir,
                                ld_file=declared)
        assert proc.returncode == 0, f"[{tag}] rc={proc.returncode}\n{proc.stderr}"
        assert out.exists(), f"[{tag}] no JSON"
        return json.loads(out.read_text())

    # --- EUR / TRANS containment: the declared panel is INVISIBLE -----------
    eur = _run("eur_false", "EUR", "false", eur_declared)
    assert eur["ld_matrix"] == str(eur_dir), (
        f"EUR opened {eur['ld_matrix']!r} instead of the 3f431ab read path "
        f"{str(eur_dir)!r}: --ld-authoritative false is parsed but not "
        "consumed, and Track-A EUR numerics can move (BLOCKER-B)"
    )
    assert eur["ld_overlap"] == 200, (
        f"EUR fit was computed on {eur['ld_overlap']} variants; the 3f431ab "
        "read path yields 200"
    )
    assert eur["ld_status"] == "ld_loaded;overlap_ok;200;0.667", eur["ld_status"]
    # the receipt still records the DECLARED path, and honestly disagrees
    assert eur["ld_file_declared"] == str(eur_declared)
    assert eur["ld_matrix"] != eur["ld_file_declared"]

    # --- NEGATIVE CONTROL: the movement BLOCKER-B measured ------------------
    eur_moved = _run("eur_true", "EUR", "true", eur_declared)
    assert eur_moved["ld_matrix"] == str(eur_declared)
    assert eur_moved["ld_overlap"] == 300, (
        "the fixture no longer reproduces the EUR movement, so the containment "
        "assertion above is vacuous"
    )

    # --- AFR: the declared AoU panel IS the one that is opened --------------
    afr = _run("afr_true", "AFR", "true", afr_declared)
    assert afr["ld_matrix"] == str(afr_declared), (
        f"AFR opened {afr['ld_matrix']!r}, not the DECLARED AoU panel -- the "
        "11-day fire would buy a panel the fit never reads"
    )
    assert afr["ld_matrix"] == afr["ld_file_declared"], (
        "resolved != opened for AFR"
    )
    assert afr["ld_overlap"] == 300
    assert afr["ld_matrix"] != str(afr_dir)

    # ...and the same AFR fixture off the allow-list falls back, proving the
    # AFR result above is produced by the flag and not by path luck.
    afr_off = _run("afr_false", "AFR", "false", afr_declared)
    assert afr_off["ld_matrix"] == str(afr_dir)
    assert afr_off["ld_overlap"] == 200


# ==========================================================================
# M -- END TO END: an ABSENT declared panel must NOT abort the region
# ==========================================================================
def test_end_to_end_absent_declared_panel_does_not_abort_the_region(
    r_toolchain, tmp_path
):
    """M. The false-trip guard at the level that ships.

    Two legitimate shapes that MUST still complete under
    ``--ld-authoritative true``:
      M1 -- no ``--ld-file`` at all (a legacy / ad-hoc caller).
      M2 -- ``--ld-file`` naming a panel that DOES NOT EXIST YET. This is the
            P3 gsutil precedent restated: the AoU .rds arrive over weeks, and a
            gate that cannot tell "not built yet" from "built and rejected"
            would stop every AFR region before the fire ever ran. The loud path
            arms only when the declared file EXISTS (Task 2, pre-existing T2.6
            GHOST); an absent one leaves a stderr trace and falls back.

    NEGATIVE CONTROL (in-test): make the SAME declared path exist and be
    corrupt -> rc != 0. Absence and rejection are therefore distinguished by
    the code, not by the fixture.
    """
    rscript, env = r_toolchain
    inputs = _make_full_script_inputs(tmp_path)
    ld_dir = inputs["root"] / "ld_reference"
    dirpanel = ld_dir / "AFR" / f"{E2E_REGION}.rds"
    not_built = ld_dir / "AFR_aou" / "m2_region_00040__sub14.rds"
    _build_panels(rscript, env, tmp_path, [(dirpanel, 300, 0.10)], "tM_panels.R")
    assert not not_built.exists()

    # M1 -- no declared file at all
    out1 = inputs["root"] / "m1.json"
    p1 = _run_full_script(rscript, env, inputs, out1, ancestry="AFR",
                          authoritative="true", ld_dir=ld_dir, ld_file=None)
    assert p1.returncode == 0, (
        "the gate false-tripped on a caller that supplied NO --ld-file\n"
        f"{p1.stderr}"
    )
    assert out1.exists()
    assert json.loads(out1.read_text())["ld_matrix"] == str(dirpanel)

    # M2 -- declared panel not built yet
    out2 = inputs["root"] / "m2.json"
    p2 = _run_full_script(rscript, env, inputs, out2, ancestry="AFR",
                          authoritative="true", ld_dir=ld_dir,
                          ld_file=not_built)
    assert p2.returncode == 0, (
        "the gate false-tripped on a NOT-YET-BUILT declared panel -- that "
        f"would stop every AFR region before the fire\n{p2.stderr}"
    )
    assert out2.exists()
    assert json.loads(out2.read_text())["ld_matrix"] == str(dirpanel)
    assert "LD_DECLARED_ABSENT:" in p2.stderr, (
        "an absent declared panel must still leave a stderr trace"
    )

    # NEGATIVE CONTROL -- same path, now present and corrupt
    not_built.parent.mkdir(parents=True, exist_ok=True)
    not_built.write_bytes(os.urandom(64))
    out3 = inputs["root"] / "m3.json"
    p3 = _run_full_script(rscript, env, inputs, out3, ancestry="AFR",
                          authoritative="true", ld_dir=ld_dir,
                          ld_file=not_built)
    assert p3.returncode != 0, (
        "absence and rejection are indistinguishable -- the M1/M2 assertions "
        "above are vacuous"
    )
    assert "LD_DECLARED_REJECTED:" in p3.stderr
    assert not out3.exists()


# ==========================================================================
# T-T -- the suite cannot silently go permissive
# ==========================================================================
def test_thresholds_under_test_are_the_production_thresholds():
    """Guard against this suite going permissive the way test_ld_read_path.py's
    8 tests did (they all pin 1 / 0.0 / 1, disabling the gate that BOTH blockers
    live inside).

    Two halves: the values must be the production ones, AND the rendered R
    preamble must actually carry them -- a constant read from YAML but never
    interpolated would be theatre.
    """
    assert (MIN_LD_OVERLAP, MIN_LD_COVERAGE, MIN_LD_MIN_USE) == (50, 0.5, 10), (
        "config/susie_policy.yaml no longer holds the thresholds this suite was "
        f"written against: got {(MIN_LD_OVERLAP, MIN_LD_COVERAGE, MIN_LD_MIN_USE)}. "
        "Re-derive the fixtures rather than relaxing the assertion."
    )
    rendered = _render_preamble(Path("/dev/null"))
    assert "MIN_LD_OVERLAP  <- 50L" in rendered
    assert "MIN_LD_COVERAGE <- 0.5" in rendered
    assert "MIN_LD_MIN_USE  <- 10L" in rendered
    # the permissive shape test_ld_read_path.py uses must not appear here
    assert "MIN_LD_OVERLAP  <- 1L" not in rendered
    assert "MIN_LD_COVERAGE <- 0.0" not in rendered


# ==========================================================================
# A -- DEFECT 1: the declared panel is not abandoned for a dir candidate
# ==========================================================================
def test_declared_panel_is_not_abandoned_for_a_dir_candidate(r_toolchain, tmp_path):
    """A. At PRODUCTION thresholds, a sub-gate declared panel must still be the
    one that is opened -- not silently swapped for the 1kG reconstruction.

    Fixture: declared AoU panel at overlap 20 (>= MIN_LD_MIN_USE 10, <
    MIN_LD_OVERLAP 50) and a ``{ld_dir}/AFR/`` panel at overlap 300 that clears
    the gate outright. Pre-change, the loop ``next``ed past the declared panel
    and returned the dir panel with ``ld_loaded;overlap_ok`` -- the DAG declared
    one panel and the fit read another, exactly BLOCKER-1's defect class.

    NEGATIVE CONTROL (in-test): the identical fixture with authoritative = FALSE
    returns the DIR panel -- so the assertion above is observably violable.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    declared = ld_dir / "AFR_aou" / "m2_region_00067.rds"
    dirpanel = ld_dir / "AFR" / "FTO_16q12.rds"
    body = (
        f'declared <- "{declared}"\n'
        f'dirpanel <- "{dirpanel}"\n'
        f'make_panel(declared, id_offset = {_offset_for_overlap(20)}L, r12 = 0.90)\n'
        f'make_panel(dirpanel, id_offset = {_offset_for_overlap(300)}L, r12 = 0.10)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "FTO_16q12", mk_subset(),'
        f' authoritative = TRUE, ld_file = declared), "AUTH")\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "FTO_16q12", mk_subset(),'
        f' authoritative = FALSE, ld_file = declared), "NOAUTH")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tA.R")

    assert vals["AUTH_SOURCE"] == str(declared), (
        f"the loader opened {vals['AUTH_SOURCE']!r}, not the DECLARED "
        f"{str(declared)!r}: the declared panel is still a preference, not a "
        "mandate (BLOCKER-A)"
    )
    assert vals["AUTH_STATUS"].startswith("ld_loaded;partial_overlap"), vals["AUTH_STATUS"]
    assert vals["AUTH_OVERLAP"] == "20", vals["AUTH_OVERLAP"]
    assert vals["AUTH_R12"] == "0.900000", (
        "the returned matrix is not the declared panel's numbers"
    )
    assert vals["AUTH_SOURCE"] != str(dirpanel)

    # NEGATIVE CONTROL: the property violated -> the assertion above would fail.
    assert vals["NOAUTH_SOURCE"] == str(dirpanel), vals["NOAUTH_SOURCE"]
    assert vals["NOAUTH_R12"] == "0.100000"
    assert vals["NOAUTH_STATUS"].startswith("ld_loaded;overlap_ok")


def test_negative_control_pre_change_loader_substitutes_the_dir_panel(
    r_toolchain, tmp_path
):
    """A-control (PERMANENT). The same fixture against ``5ec33bd``'s loader.

    Reproduces BLOCKER-A verbatim: declared AoU panel, opened 1kG panel, status
    reports SUCCESS. Keeps test A honest -- if the fixture were ever neutered so
    the dir panel could not win, THIS goes red."""
    rscript, env = r_toolchain
    pre = _pre_change_loader_prefix(tmp_path)
    ld_dir = tmp_path / "ld_reference"
    declared = ld_dir / "AFR_aou" / "m2_region_00067.rds"
    dirpanel = ld_dir / "AFR" / "FTO_16q12.rds"
    body = (
        f'declared <- "{declared}"\n'
        f'make_panel(declared, id_offset = {_offset_for_overlap(20)}L, r12 = 0.90)\n'
        f'make_panel("{dirpanel}", id_offset = {_offset_for_overlap(300)}L, r12 = 0.10)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "FTO_16q12", mk_subset(),'
        f' ld_file = declared), "PRE")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tA_pre.R", loader_funcs=pre)
    assert vals["PRE_SOURCE"] == str(dirpanel), (
        "the pre-change loader was expected to silently substitute the 1kG dir "
        f"panel; it opened {vals['PRE_SOURCE']!r} instead -- the control no "
        "longer reproduces the defect it is guarding"
    )
    assert vals["PRE_STATUS"].startswith("ld_loaded;overlap_ok"), vals["PRE_STATUS"]
    assert vals["PRE_R12"] == "0.100000"


# ==========================================================================
# B -- DEFECT 2: best_partial keeps the BEST overlap, not the last
# ==========================================================================
def test_best_partial_keeps_the_best_overlap_not_the_last(r_toolchain, tmp_path):
    """B. ``best_partial <- list(...)`` overwrote unconditionally, so the LAST
    sub-gate candidate won regardless of quality.

    Legacy path (no declared file) with region_id ``BMI_5q13.3`` -- a real
    curated region whose ``safe_region_id()`` is ``BMI_5q13_3``, so the loader
    genuinely builds TWO distinct dir candidates. Candidate 1 at overlap 40,
    candidate 2 at overlap 20, both sub-gate and both >= MIN_LD_MIN_USE.

    NEGATIVE CONTROL (in-test): swap them. The answer must STILL be 40, proving
    selection is by overlap and not by position. (Position-based selection
    passes the swapped arrangement and fails the first -- so the pair is the
    discriminator, not either arrangement alone.)
    """
    rscript, env = r_toolchain
    tree_a = tmp_path / "arrangement_a" / "ld_reference"
    tree_b = tmp_path / "arrangement_b" / "ld_reference"
    off40, off20 = _offset_for_overlap(40), _offset_for_overlap(20)
    body = (
        # arrangement A: id-form candidate 40, safe-form candidate 20
        f'a_first  <- "{tree_a}/EUR/BMI_5q13.3.rds"\n'
        f'a_second <- "{tree_a}/EUR/BMI_5q13_3.rds"\n'
        f'make_panel(a_first,  id_offset = {off40}L, r12 = 0.44)\n'
        f'make_panel(a_second, id_offset = {off20}L, r12 = 0.22)\n'
        f'emit(load_ld_matrix("{tree_a}", "EUR", "BMI_5q13.3", mk_subset(),'
        f' ld_file = NULL), "A")\n'
        # arrangement B: swapped
        f'b_first  <- "{tree_b}/EUR/BMI_5q13.3.rds"\n'
        f'b_second <- "{tree_b}/EUR/BMI_5q13_3.rds"\n'
        f'make_panel(b_first,  id_offset = {off20}L, r12 = 0.22)\n'
        f'make_panel(b_second, id_offset = {off40}L, r12 = 0.44)\n'
        f'emit(load_ld_matrix("{tree_b}", "EUR", "BMI_5q13.3", mk_subset(),'
        f' ld_file = NULL), "B")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tB.R")

    assert vals["A_OVERLAP"] == "40", (
        f"a candidate at overlap 40 lost to one at overlap 20 (got "
        f"{vals['A_OVERLAP']}): best_partial is still last-wins"
    )
    assert vals["A_SOURCE"] == f"{tree_a}/EUR/BMI_5q13.3.rds"
    assert vals["A_R12"] == "0.440000"

    # NEGATIVE CONTROL: order reversed, answer unchanged => selection is by
    # overlap, not by position.
    assert vals["B_OVERLAP"] == "40", vals["B_OVERLAP"]
    assert vals["B_SOURCE"] == f"{tree_b}/EUR/BMI_5q13_3.rds"
    assert vals["B_R12"] == "0.440000"


def test_negative_control_pre_change_best_partial_takes_the_last(
    r_toolchain, tmp_path
):
    """B-control (PERMANENT). Arrangement A against ``5ec33bd``'s loader returns
    the WORSE (overlap 20) panel. This is the defect, pinned."""
    rscript, env = r_toolchain
    pre = _pre_change_loader_prefix(tmp_path)
    tree = tmp_path / "pre_arrangement" / "ld_reference"
    body = (
        f'make_panel("{tree}/EUR/BMI_5q13.3.rds", '
        f'id_offset = {_offset_for_overlap(40)}L, r12 = 0.44)\n'
        f'make_panel("{tree}/EUR/BMI_5q13_3.rds", '
        f'id_offset = {_offset_for_overlap(20)}L, r12 = 0.22)\n'
        f'emit(load_ld_matrix("{tree}", "EUR", "BMI_5q13.3", mk_subset(),'
        f' ld_file = NULL), "PRE")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tB_pre.R", loader_funcs=pre)
    assert vals["PRE_OVERLAP"] == "20", (
        "the pre-change loader was expected to take the LAST sub-gate candidate "
        f"(overlap 20); got {vals['PRE_OVERLAP']} -- the control no longer "
        "reproduces the defect it is guarding"
    )
    assert vals["PRE_SOURCE"] == f"{tree}/EUR/BMI_5q13_3.rds"


# ==========================================================================
# C -- a use_identity declared panel is not silently honoured
# ==========================================================================
def test_declared_use_identity_is_not_silently_honoured(r_toolchain, tmp_path):
    """C. ``:182`` ``return``ed BEFORE the gate whenever ``use_identity`` was
    set, and ``:529`` then wrote ``ld_matrix = ld_result$source``. The JSON
    receipt therefore read ``ld_matrix == ld_file_declared`` -- a FORGED green
    match -- while SuSiE ran on ``diag(n)``. A ``use_identity`` payload is a real
    artifact: ``make_identity_ld_refs.R:64`` writes exactly this shape.

    Under authoritative = TRUE the loader must return a structured REJECTION.
    (The hard ``stop()`` on that rejection is Task 3; this task pins the SHAPE.)

    NEGATIVE CONTROLS (in-test), both at the same code point:
      C1 -- the identity payload sited at the DIR path with authoritative =
            FALSE returns the byte-identical legacy early return
            (R NULL, source == candidate, status == "identity") at rc 0.
      C2 -- the identity payload sited ONLY at the declared path with
            authoritative = FALSE is INVISIBLE: nothing is opened.
    """
    rscript, env = r_toolchain
    auth_dir = tmp_path / "auth" / "ld_reference"
    c1_dir = tmp_path / "c1" / "ld_reference"
    c2_dir = tmp_path / "c2" / "ld_reference"
    auth_declared = auth_dir / "AFR_aou" / "m2_region_00067.rds"
    auth_dirpanel = auth_dir / "AFR" / "FTO_16q12.rds"
    c1_dirpanel = c1_dir / "AFR" / "FTO_16q12.rds"
    c2_declared = c2_dir / "AFR_aou" / "m2_region_00067.rds"
    body = (
        f'make_identity_panel("{auth_declared}")\n'
        f'make_panel("{auth_dirpanel}", id_offset = {_offset_for_overlap(300)}L, r12 = 0.10)\n'
        f'emit(load_ld_matrix("{auth_dir}", "AFR", "FTO_16q12", mk_subset(),'
        f' authoritative = TRUE, ld_file = "{auth_declared}"), "AUTH")\n'
        # C1: legacy early return preserved off the allow-list
        f'make_identity_panel("{c1_dirpanel}")\n'
        f'emit(load_ld_matrix("{c1_dir}", "AFR", "FTO_16q12", mk_subset(),'
        f' authoritative = FALSE, ld_file = NULL), "C1")\n'
        # C2: the declared file is invisible off the allow-list
        f'make_identity_panel("{c2_declared}")\n'
        f'dir.create("{c2_dir}/AFR", recursive = TRUE, showWarnings = FALSE)\n'
        f'emit(load_ld_matrix("{c2_dir}", "AFR", "FTO_16q12", mk_subset(),'
        f' authoritative = FALSE, ld_file = "{c2_declared}"), "C2")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tC.R")

    assert vals["AUTH_REJECTED"] == "TRUE", (
        "a use_identity declared panel was accepted silently; the receipt would "
        f"read ld_matrix == ld_file_declared while SuSiE ran on diag(n). "
        f"status={vals['AUTH_STATUS']!r}"
    )
    assert vals["AUTH_REASON"] == "use_identity", vals["AUTH_REASON"]
    assert vals["AUTH_RNULL"] == "TRUE"
    assert vals["AUTH_SOURCE"] == str(auth_declared)
    assert vals["AUTH_DECLARED"] == str(auth_declared)
    # and the dir panel was NOT silently substituted
    assert vals["AUTH_SOURCE"] != str(auth_dirpanel)

    # NEGATIVE CONTROL C1 -- legacy shape byte-identical
    assert vals["C1_REJECTED"] == "FALSE"
    assert vals["C1_RNULL"] == "TRUE"
    assert vals["C1_SOURCE"] == str(c1_dirpanel)
    assert vals["C1_STATUS"] == "identity", vals["C1_STATUS"]

    # NEGATIVE CONTROL C2 -- declared file invisible when not authoritative
    assert vals["C2_SOURCE"] == "<NULL>", vals["C2_SOURCE"]
    assert vals["C2_STATUS"] == "ld_missing", vals["C2_STATUS"]


# ==========================================================================
# D -- a corrupt declared panel is not silence
# ==========================================================================
def test_corrupt_declared_panel_is_not_silence(r_toolchain, tmp_path):
    """D. ``:171`` wrapped ``readRDS`` in ``tryCatch`` -> ``NULL`` -> a bare
    ``next``. No message, no warning, no JSON field, no non-zero exit: a
    truncated ``.rds`` from an interrupted conversion burned full compute and
    emitted a plausible result computed on the 1kG panel.

    NEGATIVE CONTROL (in-test): authoritative = FALSE -> the dir panel IS opened
    at rc 0 with a success status. That is today's behaviour and it is the proof
    the assertion can fail.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    declared = ld_dir / "AFR_aou" / "m2_region_00067.rds"
    dirpanel = ld_dir / "AFR" / "FTO_16q12.rds"
    declared.parent.mkdir(parents=True, exist_ok=True)
    declared.write_bytes(os.urandom(64))
    assert declared.stat().st_size == 64

    body = (
        f'make_panel("{dirpanel}", id_offset = {_offset_for_overlap(300)}L, r12 = 0.10)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "FTO_16q12", mk_subset(),'
        f' authoritative = TRUE, ld_file = "{declared}"), "AUTH")\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "FTO_16q12", mk_subset(),'
        f' authoritative = FALSE, ld_file = "{declared}"), "NOAUTH")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tD.R")

    assert vals["AUTH_REJECTED"] == "TRUE", (
        f"an unreadable declared panel was silent; status={vals['AUTH_STATUS']!r}"
    )
    assert vals["AUTH_REASON"] == "unreadable", vals["AUTH_REASON"]
    assert vals["AUTH_SOURCE"] == str(declared)
    assert vals["AUTH_RNULL"] == "TRUE"
    assert vals["AUTH_SOURCE"] != str(dirpanel), (
        "the dir panel was opened after the declared panel failed to read"
    )

    # NEGATIVE CONTROL
    assert vals["NOAUTH_SOURCE"] == str(dirpanel)
    assert vals["NOAUTH_RNULL"] == "FALSE"
    assert vals["NOAUTH_STATUS"].startswith("ld_loaded;overlap_ok")


# ==========================================================================
# E -- below MIN_LD_MIN_USE is a rejection, not an identity fallback
# ==========================================================================
def test_declared_below_min_use_is_a_rejection_not_an_identity_fallback(
    r_toolchain, tmp_path
):
    """E. A declared panel that cannot clear ``MIN_LD_MIN_USE`` (10) previously
    fell out of the loop into ``ld_overlap_insufficient`` and then to an identity
    fit reported as ``status="success"``. Under authoritative = TRUE it is a
    structured rejection carrying the realized overlap.

    NEGATIVE CONTROL (in-test): overlap 12 (just above min_use) is NOT a
    rejection -- it returns the DECLARED panel under partial_overlap. The
    tightening is exactly at the threshold, not everywhere.
    """
    rscript, env = r_toolchain
    lo_dir = tmp_path / "below" / "ld_reference"
    hi_dir = tmp_path / "above" / "ld_reference"
    lo = lo_dir / "AFR_aou" / "m2_region_00067.rds"
    hi = hi_dir / "AFR_aou" / "m2_region_00067.rds"
    body = (
        f'make_panel("{lo}", id_offset = {_offset_for_overlap(3)}L, r12 = 0.33)\n'
        f'dir.create("{lo_dir}/AFR", recursive = TRUE, showWarnings = FALSE)\n'
        f'emit(load_ld_matrix("{lo_dir}", "AFR", "FTO_16q12", mk_subset(),'
        f' authoritative = TRUE, ld_file = "{lo}"), "LO")\n'
        f'make_panel("{hi}", id_offset = {_offset_for_overlap(12)}L, r12 = 0.55)\n'
        f'dir.create("{hi_dir}/AFR", recursive = TRUE, showWarnings = FALSE)\n'
        f'emit(load_ld_matrix("{hi_dir}", "AFR", "FTO_16q12", mk_subset(),'
        f' authoritative = TRUE, ld_file = "{hi}"), "HI")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tE.R")

    assert vals["LO_REJECTED"] == "TRUE", (
        f"overlap 3 < MIN_LD_MIN_USE {MIN_LD_MIN_USE} must be a rejection; "
        f"status={vals['LO_STATUS']!r}"
    )
    assert vals["LO_REASON"] == "overlap_below_min_use", vals["LO_REASON"]
    assert vals["LO_OVERLAP"] == "3", vals["LO_OVERLAP"]
    assert vals["LO_DECLARED"] == str(lo)
    assert vals["LO_RNULL"] == "TRUE"

    # NEGATIVE CONTROL: just above min_use -> unchanged partial_overlap
    assert vals["HI_REJECTED"] == "FALSE", vals["HI_STATUS"]
    assert vals["HI_STATUS"].startswith("ld_loaded;partial_overlap"), vals["HI_STATUS"]
    assert vals["HI_OVERLAP"] == "12"
    assert vals["HI_SOURCE"] == str(hi)
    assert vals["HI_R12"] == "0.550000"


# ==========================================================================
# F -- the pre-existing GHOST contract does not move
# ==========================================================================
def test_declared_absent_still_returns_the_legacy_guard(r_toolchain, tmp_path):
    """F. The loud path arms only when the declared file EXISTS. A supplied but
    ABSENT ``--ld-file`` with an absent ``--ld-dir`` keeps the byte-identical
    legacy ``"ld_dir_missing"`` at rc 0 -- the pre-existing T2.6 GHOST contract,
    which this remediation must not move.

    Asserted under BOTH the explicit authoritative = TRUE and the default, so
    neither the new formal nor its default can drift the contract.
    """
    rscript, env = r_toolchain
    missing_dir = tmp_path / "no_such_ld_dir"
    unreadable = tmp_path / "no_such_panel.rds"
    body = (
        f'emit(load_ld_matrix("{missing_dir}", "AFR", "FTO_16q12", mk_subset(),'
        f' authoritative = TRUE, ld_file = "{unreadable}"), "GHOST")\n'
        f'emit(load_ld_matrix("{missing_dir}", "AFR", "FTO_16q12", mk_subset(),'
        f' ld_file = "{unreadable}"), "GHOSTDEF")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tF.R")
    for tag in ("GHOST", "GHOSTDEF"):
        assert vals[f"{tag}_RNULL"] == "TRUE", f"[{tag}] expected R = NULL"
        assert vals[f"{tag}_SOURCE"] == "<NULL>", f"[{tag}] expected source = NULL"
        assert vals[f"{tag}_STATUS"] == "ld_dir_missing", (
            f"[{tag}] the legacy status string moved: {vals[f'{tag}_STATUS']!r}"
        )
        assert vals[f"{tag}_REJECTED"] == "FALSE", (
            f"[{tag}] an absent declared file must not arm the loud path"
        )


# ==========================================================================
# G -- THE MANUSCRIPT-PROTECTING PROOF (BLOCKER-B, behavioural refutation)
# ==========================================================================
def test_authoritative_false_is_byte_identical_to_3f431ab(r_toolchain, tmp_path):
    """G. Under ``--ld-authoritative false`` the loader IGNORES the declared
    argument ENTIRELY, so the two extra argv tokens are inert BY CONSTRUCTION
    and an EUR fit cannot move.

    Fixture: two DELIBERATELY DIFFERENT EUR panels, both clearing the production
    gate outright, distinguished ONLY by r[1,2] -- 0.9 on the declared
    ``EUR_ukbb_pub`` head, 0.1 on the ``{ld_dir}/EUR/`` 1kG tail. This is the
    blast radius's own fixture and its own measurement.

    Exact argv byte-identity vs 3f431ab is UNREACHABLE (the pre-existing T2.1
    requires the declared-LD argument to remain in run_finemap's shell for EVERY
    ancestry, and editing T2.1 is forbidden). What is delivered instead is
    strictly stronger and is proven here: the OPENED BYTES are byte-identical.

    NEGATIVE CONTROL (in-test): authoritative = TRUE opens the declared panel and
    returns 0.9 -- precisely the movement BLOCKER-B measured. The assertion is
    therefore observably violable.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    declared = ld_dir / "EUR_ukbb_pub" / "FTO_16q12.rds"
    dirpanel = ld_dir / "EUR" / "FTO_16q12.rds"
    body = (
        f'declared <- "{declared}"\n'
        f'make_panel(declared, id_offset = 0L, r12 = 0.90)\n'
        f'make_panel("{dirpanel}", id_offset = 0L, r12 = 0.10)\n'
        f'emit(load_ld_matrix("{ld_dir}", "EUR", "FTO_16q12", mk_subset(),'
        f' authoritative = FALSE, ld_file = declared), "EUR")\n'
        f'emit(load_ld_matrix("{ld_dir}", "EUR", "FTO_16q12", mk_subset(),'
        f' authoritative = TRUE, ld_file = declared), "MOVED")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tG.R")

    assert vals["EUR_SOURCE"] == str(dirpanel), (
        f"EUR opened {vals['EUR_SOURCE']!r} instead of the 1kG tail "
        f"{str(dirpanel)!r}: the declared panel is NOT being ignored off the "
        "allow-list, and Track-A numerics can move (BLOCKER-B)"
    )
    assert vals["EUR_R12"] == "0.100000", (
        f"EUR LD MATRIX CHANGED: r[1,2] = {vals['EUR_R12']} (expected 0.100000)"
    )
    assert vals["EUR_STATUS"] == f"ld_loaded;overlap_ok;{N_SUBSET};1.000"

    # NEGATIVE CONTROL: this is the movement the blast radius measured.
    assert vals["MOVED_SOURCE"] == str(declared)
    assert vals["MOVED_R12"] == "0.900000"
    # ...and the tell: ld_status is BYTE-IDENTICAL across the move.
    assert vals["MOVED_STATUS"] == vals["EUR_STATUS"], (
        "the fixture no longer reproduces the byte-identical-status tell that "
        "made BLOCKER-B invisible"
    )


def test_negative_control_pre_change_loader_moves_eur(r_toolchain, tmp_path):
    """G-control (PERMANENT). The identical two-panel EUR fixture against
    ``5ec33bd``'s loader, called exactly as run_finemap called it.

    Reproduces BLOCKER-B's measurement: opened ``EUR_ukbb_pub``, r[1,2] = 0.9,
    with ``ld_status`` byte-identical to the 1kG read. If anyone ever makes the
    two panels the same, or drops the ld_file thread, this control goes red and
    test G's proof stops being vacuous."""
    rscript, env = r_toolchain
    pre = _pre_change_loader_prefix(tmp_path)
    ld_dir = tmp_path / "ld_reference"
    declared = ld_dir / "EUR_ukbb_pub" / "FTO_16q12.rds"
    dirpanel = ld_dir / "EUR" / "FTO_16q12.rds"
    body = (
        f'declared <- "{declared}"\n'
        f'make_panel(declared, id_offset = 0L, r12 = 0.90)\n'
        f'make_panel("{dirpanel}", id_offset = 0L, r12 = 0.10)\n'
        f'emit(load_ld_matrix("{ld_dir}", "EUR", "FTO_16q12", mk_subset(),'
        f' ld_file = declared), "AFTER")\n'
        f'emit(load_ld_matrix("{ld_dir}", "EUR", "FTO_16q12", mk_subset(),'
        f' ld_file = NULL), "BEFORE")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tG_pre.R", loader_funcs=pre)
    assert vals["AFTER_SOURCE"] == str(declared), vals["AFTER_SOURCE"]
    assert vals["AFTER_R12"] == "0.900000"
    assert vals["BEFORE_SOURCE"] == str(dirpanel)
    assert vals["BEFORE_R12"] == "0.100000"
    assert vals["AFTER_STATUS"] == vals["BEFORE_STATUS"], (
        "the byte-identical ld_status tell no longer reproduces"
    )
