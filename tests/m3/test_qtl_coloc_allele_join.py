"""tests/m3/test_qtl_coloc_allele_join.py -- 260805-w7u Task 2 (FINDING E, key half).

THE COLOC JOIN IS KEYED IDENTICALLY, FAILS LOUDLY, AND HANDS coloc A REAL MATRIX.

WHY THIS MODULE EXISTS. Closing finding E's PATH (Task 1) without closing its KEY
substitutes one silent failure for another. Three facts, all MEASURED at
``7b1025d``, make that concrete:

  * F2 -- ``build_ld_rownames`` is NOT on the AoU path, so "fix it" is a no-op.
    ``ld_npz_to_rds.R:440`` writes ``R`` as a ``dsCMatrix`` **with** dimnames (the
    GRCh37 ``chr:pos:ref:alt`` ids), and ``run_qtl_coloc.R:232`` is
    ``rownames(ld_full) %||% colnames(ld_full) %||% build_ld_rownames(ld_obj)``
    -- ``%||%`` short-circuits on the first non-NULL, so ``ld_snp_names`` comes
    from ``rownames(ld_full)`` and ``build_ld_rownames`` never runs. The legacy
    1kG ``.rds`` is the opposite shape (``plink_ld_to_rds.R:88`` sets
    ``dimnames(R) <- NULL``), which is exactly why EUR coloc works today.
  * F3 -- an unusable panel does not reach a "silent identity"; it reaches FOUR
    stacked **exit-0** layers. Empty LD intersection -> ``too_few_snps`` at rc 0;
    a sparse ``dsCMatrix`` handed to ``coloc::runsusie`` -> the MEASURED error
    ``LD must be of class matrix`` swallowed by a ``tryCatch`` ->
    ``qtl_susie_failed`` at rc 0 (``coloc::check_dataset(req="LD")`` PASSES on
    the sparse matrix -- it does not catch this); ``use_identity`` fitting
    ``coloc.susie`` on ``diag(n)`` with only a ``cat()``; and Snakemake seeing
    rc 0 for all of them. In bulk that is indistinguishable from biology.
  * F4 -- the bridge that DOES exist is the region variant catalog
    ``{ld_reference}/variants/{region}.tsv`` (``CHR, POS, REF, ALT, SNP_ID``),
    already ``run_finemap.input.variants``. Both sumstats key conventions are
    live for AFR (``asthma.AFR -> rs151190501``, ``stroke.AFR -> 1:662622``), so
    a panel-only bridge cannot reach rsID-named fits; the catalog can reach both.

THE DUPLICATION'S PRICE, PAID HERE
----------------------------------
``src/snakemake/scripts/ld_allele_join.R`` is a DELIBERATE second implementation
of a join that already exists inside the FROZEN ``run_susie_rss.R``. A second
independent allele-key implementation is precisely how finding H came to exist in
two places. The difference is that agreement is **machine-checked on every suite
run**: ``test_differential_agreement_*`` drives BOTH on the same fixtures and
asserts identical ``keep``, ``ld``, ``orient`` and all six counters.

⚠ THE "SHIPPED" SIDE IS OBTAINED BY BODY-WALK EXTRACTION FROM THE REAL FROZEN
SOURCE, NEVER HAND-COPIED. ``match_indices_allele_aware`` is a closure nested
inside ``load_ld_matrix`` (``run_susie_rss.R:220``, inside ``:142-601``), so it
exists only during a live call; and ``load_ld_matrix()``'s return value does not
carry ``ld_idx`` at all (it is consumed internally at ``:489-493`` and
discarded). Sourcing the loader prefix alone gives::

    exists load_ld_matrix: TRUE
    exists match_indices_allele_aware (top level): FALSE

so :func:`extract_nested` walks ``body(load_ld_matrix)`` for the assignment
expression and ``eval()``s its RHS in a child environment into which the three
helpers it closes over (``.up``, ``.usable``, ``.allele_counts0``) have been
extracted FIRST. A hand-transcription here would produce a test that agrees
**with itself** -- a vacuous assertion wearing a green check, the class this arc
has caught six times. ``NC-2g`` proves the extractor tracks the source by turning
the agreement test RED against a deliberately ALTERED copy; the real
``run_susie_rss.R`` stays **code**-identical to ``bf04199`` throughout, and
**byte-unchanged on disk mid-control**.
(That pin was ``dc4bbd2`` until 2026-08-06; ``quick-260806-pd3`` spent
``AUTH-K1-UNFREEZE`` on finding K-1 and re-pinned. The unfreeze is SPENT.)

THRESHOLDS are READ from ``config/susie_policy.yaml`` (50 / 0.5 / 10), never
hardcoded permissive values -- ``tests/m3/test_ld_read_path.py``'s 8
gate-disabled tests are the cautionary precedent.

NO-SKIP RULE: ``_require_m3_r_toolchain()`` ERRORS rather than skipping when the
``m3-r-ld`` marker env is present.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from test_stitch_subregions_to_rds import (  # noqa: E402
    R_SUBPROCESS_TIMEOUT_S,
    _loader_functions_only,
    _require_m3_r_toolchain,
)
#: ⚠ THIS MODULE HOLDS THREE COMMENT-STRIPPERS WITH DELIBERATELY DIFFERENT
#: SEMANTICS, and they are REGISTERED here rather than merged. Do NOT rewire
#: them and do NOT add a fourth: each backs a different pre-existing assertion.
#:   * ``code_only`` (imported, below) DELETES triple-quoted strings -- right for
#:     a docstring, wrong for a Snakemake ``shell:`` body.
#:   * ``strip_py_comments`` (:this module) KEEPS them, because a ``shell:`` body
#:     IS a triple-quoted string.
#:   * ``r_code_only`` (:this module) is the R stripper, and it is deliberately
#:     KEPT: ``test_source_freeze.py`` consumes it as an INDEPENDENT cross-check
#:     against ``source_freeze``'s R mask. Two implementations, one answer.
#: ``tests/m3/source_freeze.py`` is the forward default for NEW code-identity
#: work (nine such strippers already existed repo-wide when it was written --
#: see DEC-2026-08-06-sr4-freeze-scope).
# ONE comment-stripper, shared with the Task 1 module. An absence claim about
# CODE must be evaluated against code -- the comments in both edited files
# legitimately quote the very tokens the tests assert are absent.
from test_qtl_coloc_ld_resolution import code_only  # noqa: E402
from source_freeze import (  # noqa: E402
    LANG_R,
    assert_code_frozen,
    assert_unchanged_on_disk,
    git_show,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUSIE_R_REL = "src/legacy/region_analysis/scripts/run_susie_rss.R"
SUSIE_R = PROJECT_ROOT / SUSIE_R_REL
NEW_JOIN_R = PROJECT_ROOT / "src" / "snakemake" / "scripts" / "ld_allele_join.R"
QTL_COLOC_R = PROJECT_ROOT / "src" / "snakemake" / "scripts" / "run_qtl_coloc.R"
QTL_COLOC_SMK = PROJECT_ROOT / "src" / "snakemake" / "rules" / "qtl_coloc.smk"
#: Read ONLY by AUTH-b77-01's narrowed params.region_id pin and its negative
#: control. This module never writes it.
FINEMAP_SMK = PROJECT_ROOT / "src" / "snakemake" / "rules" / "finemap.smk"

#: DIFFERENTIAL SUBSTRATE. The commit this plan started from -- the
#: un-crosswalked, allele-blind, sparse-matrix-passing coloc path. It MUST NEVER
#: be re-pinned: it is the permanent OFF-branch control, and bumping it in a
#: re-pin sweep would silently destroy it.
PRE_CHANGE_REF = "7b1025d"

#: CODE PIN. ``run_susie_rss.R``'s freeze, asserted by this module including
#: while NC-2g's altered-source control is running. IMPORTED, never re-declared:
#: ``R_CODE_REF`` in ``test_source_freeze_pins.py`` is the ONLY place the R pin
#: is spelled. ``quick-260806-sr4`` rescoped it from BYTES to CODE under
#: AUTH-SR4-RESCOPE -- a comment-only edit no longer moves it (the K-3
#: correction is the proof), a CODE edit still does. Re-set from ``dc4bbd2`` by
#: ``quick-260806-pd3`` after finding K-1; ``AUTH-K1-UNFREEZE`` is SPENT.
#: See DEC-2026-08-06-sr4-freeze-scope.
from test_source_freeze_pins import R_CODE_REF as FREEZE_CODE_REF  # noqa: E402

_POLICY = yaml.safe_load(
    (PROJECT_ROOT / "config" / "susie_policy.yaml").read_text()
)["susie"]
MIN_LD_OVERLAP = int(_POLICY["min_ld_overlap"])      # 50
MIN_LD_COVERAGE = float(_POLICY["min_ld_coverage"])  # 0.5
MIN_LD_MIN_USE = int(_POLICY["min_ld_min_use"])      # 10


@pytest.fixture(scope="session")
def r_toolchain() -> tuple[Path, dict]:
    return _require_m3_r_toolchain()


def strip_py_comments(text: str) -> str:
    """Remove Python ``#`` comments but PRESERVE string literals.

    ``code_only`` (shared with the Task 1 module) deletes triple-quoted strings
    outright, which is right for docstrings and wrong here: a Snakemake
    ``shell:`` body IS a triple-quoted string, so an assertion about the rendered
    command line has to survive the stripper. This variant keeps every string and
    removes only the comments -- which is exactly enough, because the token this
    test asserts is ABSENT appears only in a ``#`` comment explaining the trap.
    """
    out, i, n = [], 0, len(text)
    quote = None
    while i < n:
        ch = text[i]
        if quote:
            out.append(ch)
            if ch == "\\":
                if i + 1 < n:
                    out.append(text[i + 1])
                i += 2
                continue
            if text.startswith(quote, i):
                out.append(text[i + 1:i + len(quote)])
                i += len(quote)
                quote = None
                continue
            i += 1
            continue
        triple = text[i:i + 3]
        if triple in ('"""', "'''"):
            out.append(triple)
            quote = triple
            i += 3
            continue
        if ch in "\"'":
            out.append(ch)
            quote = ch
            i += 1
            continue
        if ch == "#":
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _git_show(spec: str) -> str:
    return subprocess.run(["git", "show", spec], cwd=PROJECT_ROOT,
                          capture_output=True, text=True, check=True).stdout


def _run_r(rscript: Path, env: dict, code: str, tmp_path: Path,
           name: str = "probe.R") -> subprocess.CompletedProcess:
    f = tmp_path / name
    f.write_text(code)
    return subprocess.run([str(rscript), str(f)], capture_output=True, text=True,
                          timeout=R_SUBPROCESS_TIMEOUT_S, env=env, cwd=PROJECT_ROOT)


# ==========================================================================
# STEP 0 -- the body-walk extractor. THE NAMED PRIVATE HELPER.
# ==========================================================================
#: The three nested helpers ``match_indices_allele_aware`` closes over. They must
#: be extracted into the CHILD environment FIRST or the returned callable fails
#: at call time. The list was verified COMPLETE by enumerating every nested
#: ``<- function`` in ``load_ld_matrix``'s span and tracing every call token in
#: the matcher body (the one apparent extra,
#: ``assert_declared_ld_authoritative``, occurs only inside a comment at
#: ``run_susie_rss.R:229``).
NESTED_HELPERS = (".up", ".usable", ".allele_counts0")

_EXTRACTOR_R = r'''
# --------------------------------------------------------------------------
# extract_nested() -- STEP 0.
#
# WHY `_loader_functions_only` ALONE IS INSUFFICIENT, recorded here so a future
# reader does not repeat the discovery. Its documented contract
# (tests/m3/test_stitch_subregions_to_rds.py:225-238) is "write a temp R file
# with ONLY the function-definition prefix of run_susie_rss.R (up to the
# top-level `option_list <- list(` marker) so the loader-contract test can source
# load_ld_matrix() WITHOUT triggering the script's top-level argument parsing".
# That contract does NOT extend to exposing nested closures:
# match_indices_allele_aware is defined at run_susie_rss.R:220, INSIDE
# load_ld_matrix (:142-:601; the option_list marker is at :659), so it exists
# only during a live call. Routing through a real load_ld_matrix() call does not
# rescue it either -- the returned object carries subset_idx (=keep),
# allele_orient (=orient) and allele_counts (=counts) but NEVER ld_idx, which is
# consumed internally at :489-493 to reorder variants/R and then discarded.
#
# So: walk body(load_ld_matrix) for the `<-` assignment whose LHS is the target
# name and eval() its RHS in a CHILD of the sourced environment. That yields a
# genuinely standalone callable copy of the REAL shipped function, WITHOUT
# invoking load_ld_matrix() and WITHOUT editing run_susie_rss.R (this reads the
# frozen source; it does not modify it).
# --------------------------------------------------------------------------
extract_nested <- function(fn, name) {
  found <- NULL
  walk <- function(e) {
    if (!is.null(found) || !is.call(e)) return(invisible(NULL))
    if (length(e) == 3L && as.character(e[[1]]) %in% c("<-", "=") &&
        is.name(e[[2]]) && identical(as.character(e[[2]]), name)) {
      found <<- e[[3]]; return(invisible(NULL))
    }
    for (i in seq_along(e)) if (!is.null(e[[i]])) try(walk(e[[i]]), silent = TRUE)
    invisible(NULL)
  }
  walk(body(fn))
  if (is.null(found)) stop("STOP-and-surface: could not extract ", name)
  found
}

build_shipped_matcher <- function(loader_funcs_path) {
  # Sourced into its OWN env whose parent is globalenv(). ld_allele_join.R is
  # sourced into a DIFFERENT env, so neither implementation can accidentally
  # resolve a helper belonging to the other -- a missing extraction ERRORS
  # instead of silently borrowing the new code and agreeing with itself.
  senv <- new.env(parent = globalenv())
  suppressWarnings(suppressMessages(sys.source(loader_funcs_path, envir = senv)))
  lm <- get("load_ld_matrix", envir = senv)
  child <- new.env(parent = senv)
  for (nm in c(__NESTED_HELPERS__)) {
    assign(nm, eval(extract_nested(lm, nm), envir = child), envir = child)
  }
  eval(extract_nested(lm, "match_indices_allele_aware"), envir = child)
}

build_new_matcher <- function(join_path) {
  nenv <- new.env(parent = globalenv())
  suppressWarnings(suppressMessages(sys.source(join_path, envir = nenv)))
  get("ld_allele_join_indices", envir = nenv)
}
'''


def extractor_r(nested_helpers=NESTED_HELPERS) -> str:
    quoted = ", ".join(f'"{h}"' for h in nested_helpers)
    return _EXTRACTOR_R.replace("__NESTED_HELPERS__", quoted)


def loader_prefix(tmp_path: Path, source_override: str | None = None) -> Path:
    """The ``run_susie_rss.R`` function-definition prefix.

    ``source_override`` writes an ALTERED copy into ``tmp_path`` -- used by NC-2g.
    The real file is never touched.
    """
    if source_override is None:
        return _loader_functions_only(tmp_path)
    alt = tmp_path / "altered_run_susie_rss.R"
    alt.write_text(source_override)
    lines = source_override.splitlines()
    cut = len(lines)
    for i, ln in enumerate(lines):
        if ln.strip().startswith("option_list <-"):
            cut = i
            break
    out = tmp_path / "altered_loader_funcs_only.R"
    out.write_text("\n".join(lines[:cut]) + "\n")
    return out


# ==========================================================================
# The shared differential fixtures -- every disposition class
# ==========================================================================
_FIXTURES_R = r'''
FIXTURES <- list()

FIXTURES[["multiallelic"]] <- list(
  panel = data.frame(CHR = c("12","12","12"), POS = c(100L,100L,200L),
                     REF = c("A","A","C"), ALT = c("G","C","T"),
                     stringsAsFactors = FALSE),
  subset = data.frame(CHR = c("12","12"), POS = c(100L,200L),
                      REF = c("A","T"), ALT = c("C","C"),
                      stringsAsFactors = FALSE))

FIXTURES[["palindromic"]] <- list(
  panel = data.frame(CHR = rep("1",4), POS = c(10L,20L,30L,40L),
                     REF = c("A","T","C","G"), ALT = c("T","A","G","C"),
                     stringsAsFactors = FALSE),
  subset = data.frame(CHR = rep("1",4), POS = c(10L,20L,30L,40L),
                      REF = c("A","T","C","G"), ALT = c("T","A","G","C"),
                      stringsAsFactors = FALSE))

FIXTURES[["mismatch"]] <- list(
  panel = data.frame(CHR = rep("3",3), POS = c(1L,2L,3L),
                     REF = c("A","A","A"), ALT = c("G","G","G"),
                     stringsAsFactors = FALSE),
  subset = data.frame(CHR = rep("3",3), POS = c(1L,2L,3L),
                      REF = c("C","A","A"), ALT = c("T","G","G"),
                      stringsAsFactors = FALSE))

FIXTURES[["ambiguous"]] <- list(
  panel = data.frame(CHR = rep("5",3), POS = c(7L,7L,8L),
                     REF = c("A","A","A"), ALT = c("G","G","G"),
                     stringsAsFactors = FALSE),
  subset = data.frame(CHR = rep("5",2), POS = c(7L,8L),
                      REF = c("A","A"), ALT = c("G","G"),
                      stringsAsFactors = FALSE))

FIXTURES[["unusable"]] <- list(
  panel = data.frame(CHR = rep("9",4), POS = c(1L,2L,3L,4L),
                     REF = c("A","A","A","A"), ALT = c("G","G","G","G"),
                     stringsAsFactors = FALSE),
  subset = data.frame(CHR = rep("9",4), POS = c(1L,2L,3L,4L),
                      REF = c("", "N", NA, "A"), ALT = c("G","G","G","G"),
                      stringsAsFactors = FALSE))

FIXTURES[["absent_position"]] <- list(
  panel = data.frame(CHR = rep("2",2), POS = c(1L,2L),
                     REF = c("A","A"), ALT = c("G","G"),
                     stringsAsFactors = FALSE),
  subset = data.frame(CHR = rep("2",3), POS = c(1L,2L,999L),
                      REF = c("A","A","A"), ALT = c("G","G","G"),
                      stringsAsFactors = FALSE))

FIXTURES[["reject_panel_no_alleles"]] <- list(
  panel = data.frame(CHR = rep("4",2), POS = c(1L,2L), stringsAsFactors = FALSE),
  subset = data.frame(CHR = rep("4",2), POS = c(1L,2L),
                      REF = c("A","A"), ALT = c("G","G"),
                      stringsAsFactors = FALSE))

FIXTURES[["reject_subset_no_alleles"]] <- list(
  panel = data.frame(CHR = rep("4",2), POS = c(1L,2L),
                     REF = c("A","A"), ALT = c("G","G"),
                     stringsAsFactors = FALSE),
  subset = data.frame(CHR = rep("4",2), POS = c(1L,2L), stringsAsFactors = FALSE))

FIXTURES[["reject_panel_all_unusable"]] <- list(
  panel = data.frame(CHR = rep("4",2), POS = c(1L,2L),
                     REF = c("N","N"), ALT = c("N","N"),
                     stringsAsFactors = FALSE),
  subset = data.frame(CHR = rep("4",2), POS = c(1L,2L),
                      REF = c("A","A"), ALT = c("G","G"),
                      stringsAsFactors = FALSE))

FIXTURES[["na_coordinate"]] <- list(
  panel = data.frame(CHR = c("6","6",NA), POS = c(1L,NA,3L),
                     REF = c("A","A","A"), ALT = c("G","G","G"),
                     stringsAsFactors = FALSE),
  subset = data.frame(CHR = c("6","6",NA), POS = c(1L,NA,3L),
                      REF = c("A","A","A"), ALT = c("G","G","G"),
                      stringsAsFactors = FALSE))

# PRODUCTION-SCALE mixed fixture: 120 rows spanning exact / flipped /
# palindromic / mismatch / ambiguous / unusable / absent, all at once, so the
# agreement assertion is not confined to toy shapes.
FIXTURES[["mixed_production_scale"]] <- local({
  n <- 120L
  pos <- seq_len(n) * 10L
  ref <- rep("A", n); alt <- rep("G", n)
  ref[seq(3, n, by = 12)] <- "A";  alt[seq(3, n, by = 12)] <- "T"   # palindromic
  ref[seq(5, n, by = 12)] <- "C";  alt[seq(5, n, by = 12)] <- "G"   # palindromic
  pan <- data.frame(CHR = rep("12", n), POS = pos, REF = ref, ALT = alt,
                    stringsAsFactors = FALSE)
  # duplicate a 4-key -> ambiguous
  pan <- rbind(pan, pan[7, , drop = FALSE])
  sub_ref <- ref; sub_alt <- alt
  swap <- seq(2, n, by = 4)                       # transposed -> flipped
  tmp <- sub_ref[swap]; sub_ref[swap] <- sub_alt[swap]; sub_alt[swap] <- tmp
  sub_ref[seq(9, n, by = 24)] <- "C"              # mismatch
  sub_alt[seq(9, n, by = 24)] <- "T"
  sub_ref[seq(11, n, by = 40)] <- ""              # unusable
  sub <- data.frame(CHR = rep("12", n), POS = pos, REF = sub_ref, ALT = sub_alt,
                    stringsAsFactors = FALSE)
  sub <- rbind(sub, data.frame(CHR = "12", POS = 999999L, REF = "A", ALT = "G",
                               stringsAsFactors = FALSE))  # absent position
  list(panel = pan, subset = sub)
})

# I() forces a JSON ARRAY even at length 1. Without it `auto_unbox = TRUE`
# unboxes `keep = 3L` to the scalar `3`, and a comparison against `[3]` then
# fails for a reason that has nothing to do with the join.
as_record <- function(r) {
  list(keep = I(as.integer(r$keep)), ld = I(as.integer(r$ld)),
       orient = I(as.numeric(r$orient)),
       counts = list(
         exact = r$counts$exact, flipped = r$counts$flipped,
         dropped_ambiguous = r$counts$dropped_ambiguous,
         dropped_palindromic = r$counts$dropped_palindromic,
         dropped_mismatch = r$counts$dropped_mismatch,
         dropped_unusable = r$counts$dropped_unusable,
         reject = if (is.null(r$counts$reject)) NA_character_ else r$counts$reject))
}
'''


def differential_r(loader_funcs: Path, out_json: Path,
                   nested_helpers=NESTED_HELPERS) -> str:
    return f"""
suppressPackageStartupMessages(library(jsonlite))
{extractor_r(nested_helpers)}
{_FIXTURES_R}
SHIPPED <- build_shipped_matcher("{loader_funcs}")
NEWIMPL <- build_new_matcher("{NEW_JOIN_R}")
out <- list()
for (nm in names(FIXTURES)) {{
  f <- FIXTURES[[nm]]
  out[[nm]] <- list(shipped = as_record(SHIPPED(f$subset, f$panel)),
                    new     = as_record(NEWIMPL(f$subset, f$panel)))
}}
write_json(out, "{out_json}", auto_unbox = TRUE, pretty = TRUE,
           na = "string", digits = NA)
cat("DIFFERENTIAL_DONE\\n")
"""


@pytest.fixture(scope="module")
def differential(request, r_toolchain, tmp_path_factory):
    rscript, env = r_toolchain
    tmp = tmp_path_factory.mktemp("w7u_diff")
    lf = loader_prefix(tmp)
    out = tmp / "diff.json"
    res = _run_r(rscript, env, differential_r(lf, out), tmp, "diff.R")
    assert res.returncode == 0, f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    assert "DIFFERENTIAL_DONE" in res.stdout
    return json.loads(out.read_text())


# ==========================================================================
# T2.0 -- the extractor itself
# ==========================================================================
def test_the_shipped_matcher_is_not_reachable_without_the_body_walk(r_toolchain, tmp_path):
    """The measured fact that makes STEP 0 necessary rather than ornamental."""
    rscript, env = r_toolchain
    lf = loader_prefix(tmp_path)
    code = f"""
senv <- new.env(parent = globalenv())
suppressWarnings(suppressMessages(sys.source("{lf}", envir = senv)))
cat("load_ld_matrix:", exists("load_ld_matrix", envir = senv, inherits = FALSE), "\\n")
cat("match_indices_allele_aware:",
    exists("match_indices_allele_aware", envir = senv, inherits = FALSE), "\\n")
"""
    res = _run_r(rscript, env, code, tmp_path, "reach.R")
    assert res.returncode == 0, res.stderr
    assert "load_ld_matrix: TRUE" in res.stdout
    assert "match_indices_allele_aware: FALSE" in res.stdout


def test_extractor_returns_a_standalone_two_arg_callable(r_toolchain, tmp_path):
    """Shape + the canonical multiallelic behaviour, exactly as specified.

    ``keep = 1 2``, ``ld = 2 3``, ``orient = 1 -1``, ``exact = 1``,
    ``flipped = 1``, all four ``dropped_* = 0`` -- i.e. it binds to the SECOND
    panel row, not the first hit. Anything else means the extraction returned
    something other than the shipped matcher.
    """
    rscript, env = r_toolchain
    lf = loader_prefix(tmp_path)
    code = f"""
{extractor_r()}
{_FIXTURES_R}
m <- build_shipped_matcher("{lf}")
cat("class:", class(m), "\\n")
cat("nformals:", length(formals(m)), "\\n")
f <- FIXTURES[["multiallelic"]]
r <- m(f$subset, f$panel)
cat("keep:", paste(r$keep, collapse=" "), "\\n")
cat("ld:", paste(r$ld, collapse=" "), "\\n")
cat("orient:", paste(r$orient, collapse=" "), "\\n")
cat("exact:", r$counts$exact, "flipped:", r$counts$flipped, "\\n")
cat("dropped:", r$counts$dropped_ambiguous, r$counts$dropped_palindromic,
    r$counts$dropped_mismatch, r$counts$dropped_unusable, "\\n")
"""
    res = _run_r(rscript, env, code, tmp_path, "shape.R")
    assert res.returncode == 0, f"{res.stdout}\n{res.stderr}"
    assert "class: function" in res.stdout
    assert "nformals: 2" in res.stdout
    assert "keep: 1 2" in res.stdout
    assert "ld: 2 3" in res.stdout
    assert "orient: 1 -1" in res.stdout
    assert "exact: 1 flipped: 1" in res.stdout
    assert "dropped: 0 0 0 0" in res.stdout


def test_extractor_names_the_stop_and_surface_when_the_assignment_is_absent(
        r_toolchain, tmp_path):
    """A silent ``NULL`` here would let every agreement assertion pass vacuously."""
    rscript, env = r_toolchain
    lf = loader_prefix(tmp_path)
    code = f"""
{extractor_r()}
senv <- new.env(parent = globalenv())
suppressWarnings(suppressMessages(sys.source("{lf}", envir = senv)))
lm <- get("load_ld_matrix", envir = senv)
r <- tryCatch(extract_nested(lm, "no_such_function_name_at_all"),
              error = function(e) conditionMessage(e))
cat("MSG:", r, "\\n")
"""
    res = _run_r(rscript, env, code, tmp_path, "absent.R")
    assert res.returncode == 0, res.stderr
    assert "STOP-and-surface: could not extract no_such_function_name_at_all" in res.stdout


@pytest.mark.parametrize("omitted", NESTED_HELPERS)
def test_every_nested_helper_the_matcher_closes_over_is_extracted(
        r_toolchain, tmp_path, omitted):
    """Omitting one must ERROR at call time, not silently borrow another scope.

    This is what makes ``NESTED_HELPERS`` a VERIFIED list rather than a hopeful
    one: each name is dropped in turn and the resulting callable must fail.

    ⚠ It must fail on SOME fixture, not on a chosen one. First written against
    the multiallelic fixture alone, this test reported ``.allele_counts0`` as
    "not closed over" -- because that helper is reachable only through the
    ``empty()`` REJECTION path, which the multiallelic fixture never takes. A
    control that exercises one code path cannot certify a dependency on another;
    that is the same shape as the gate-disabled ``test_ld_read_path.py`` suite
    the blast radius indicts. So: every fixture, and at least one must break.
    """
    rscript, env = r_toolchain
    lf = loader_prefix(tmp_path)
    kept = tuple(h for h in NESTED_HELPERS if h != omitted)
    code = f"""
{extractor_r(kept)}
{_FIXTURES_R}
m <- build_shipped_matcher("{lf}")
for (nm in names(FIXTURES)) {{
  f <- FIXTURES[[nm]]
  r <- tryCatch({{ m(f$subset, f$panel); "OK" }},
                error = function(e) paste0("ERR:", conditionMessage(e)))
  cat(nm, "->", r, "\\n")
}}
"""
    res = _run_r(rscript, env, code, tmp_path, f"omit_{omitted.strip('.')}.R")
    assert res.returncode == 0, res.stderr
    assert "ERR:" in res.stdout, (
        f"omitting {omitted} broke NO fixture -- either it is not actually closed "
        f"over, or it resolved from another scope:\n{res.stdout}"
    )


# ==========================================================================
# T2.1 -- DIFFERENTIAL AGREEMENT
# ==========================================================================
ALL_FIXTURES = (
    "multiallelic", "palindromic", "mismatch", "ambiguous", "unusable",
    "absent_position", "reject_panel_no_alleles", "reject_subset_no_alleles",
    "reject_panel_all_unusable", "na_coordinate", "mixed_production_scale",
)


def test_differential_fixture_set_spans_every_disposition_class(differential):
    assert set(differential) == set(ALL_FIXTURES)
    assert len(ALL_FIXTURES) >= 5


@pytest.mark.parametrize("fixture", ALL_FIXTURES)
def test_differential_agreement_with_the_shipped_matcher(differential, fixture):
    """Identical ``keep``, ``ld``, ``orient`` and all six counters."""
    rec = differential[fixture]
    assert rec["new"]["keep"] == rec["shipped"]["keep"], f"{fixture}: keep"
    assert rec["new"]["ld"] == rec["shipped"]["ld"], f"{fixture}: ld"
    assert rec["new"]["orient"] == rec["shipped"]["orient"], f"{fixture}: orient"
    assert rec["new"]["counts"] == rec["shipped"]["counts"], f"{fixture}: counts"


def test_the_differential_fixtures_are_not_all_trivially_empty(differential):
    """NON-VACUITY: agreement on nothing is agreement on nothing."""
    nonempty = [k for k, v in differential.items() if v["shipped"]["keep"]]
    assert len(nonempty) >= 5, nonempty
    big = differential["mixed_production_scale"]["shipped"]
    assert len(big["keep"]) >= MIN_LD_OVERLAP
    c = big["counts"]
    for name in ("exact", "flipped", "dropped_palindromic", "dropped_mismatch",
                 "dropped_ambiguous", "dropped_unusable"):
        assert c[name] > 0, f"{name} never exercised at production scale: {c}"


# ==========================================================================
# T2.2 -- the disposition classes, asserted directly (not only differentially)
# ==========================================================================
def test_multiallelic_binds_the_matching_alt_not_the_first_hit(differential):
    r = differential["multiallelic"]["new"]
    assert r["keep"] == [1, 2]
    assert r["ld"] == [2, 3], "bound the FIRST panel row at the position, not the match"
    assert r["orient"] == [1, -1]
    assert r["counts"]["exact"] == 1 and r["counts"]["flipped"] == 1


def test_transposed_pair_is_kept_with_orient_minus_one(differential):
    r = differential["multiallelic"]["new"]
    assert -1 in r["orient"]
    assert r["counts"]["flipped"] == 1


def test_palindromic_rows_are_dropped_and_counted(differential):
    r = differential["palindromic"]["new"]
    assert r["keep"] == []
    assert r["counts"]["dropped_palindromic"] == 4
    assert r["counts"]["exact"] == 0 and r["counts"]["flipped"] == 0


def test_position_present_no_compatible_pair_is_dropped_mismatch(differential):
    r = differential["mismatch"]["new"]
    assert r["keep"] == [2, 3]
    assert r["counts"]["dropped_mismatch"] == 1


def test_duplicated_panel_4key_is_dropped_ambiguous(differential):
    r = differential["ambiguous"]["new"]
    assert r["keep"] == [2], "the duplicated 4-key must not bind to either row"
    assert r["counts"]["dropped_ambiguous"] == 1


def test_unusable_alleles_are_dropped_and_counted(differential):
    r = differential["unusable"]["new"]
    assert r["keep"] == [4]
    assert r["counts"]["dropped_unusable"] == 3


def test_absent_position_is_ordinary_non_overlap_and_not_counted(differential):
    r = differential["absent_position"]["new"]
    assert r["keep"] == [1, 2]
    c = r["counts"]
    assert all(c[k] == 0 for k in (
        "dropped_ambiguous", "dropped_palindromic", "dropped_mismatch",
        "dropped_unusable")), c


@pytest.mark.parametrize("fixture,reject", [
    ("reject_panel_no_alleles", "alleles_unavailable_panel"),
    ("reject_subset_no_alleles", "alleles_unavailable_sumstats"),
    ("reject_panel_all_unusable", "alleles_unavailable_panel"),
])
def test_structured_rejections_are_named_not_silent(differential, fixture, reject):
    r = differential[fixture]["new"]
    assert r["keep"] == []
    assert r["counts"]["reject"] == reject


def test_keep_ld_and_orient_stay_in_lockstep(differential):
    """The one way this join could itself introduce a sign error."""
    for name, rec in differential.items():
        r = rec["new"]
        assert len(r["keep"]) == len(r["ld"]) == len(r["orient"]), name
        assert r["keep"] == sorted(r["keep"]), f"{name}: keep is not ordered"


# ==========================================================================
# NC-2g -- THE EXTRACTOR ITSELF. PERMANENT, IN-SUITE.
#
# A plain "it is callable" check would pass on a hand-copied duplicate -- the
# exact failure STEP 0 exists to prevent. These prove the helper returns the
# SHIPPED function by pointing it at deliberately ALTERED source text and
# requiring the agreement to BREAK. The alteration is performed on an in-memory /
# temp copy; ``run_susie_rss.R`` is asserted 0-diff vs the freeze in the same
# test, so the control cannot be confused with a frozen-file edit.
# ==========================================================================
ALTERATIONS = {
    "palindromic_set_narrowed": (
        'paste0(sub_ref, sub_alt) %in% c("AT", "TA", "CG", "GC")',
        'paste0(sub_ref, sub_alt) %in% c("AT")',
    ),
    "orient_forced_to_one": (
        "orient_all <- ifelse(!is.na(m_exact), 1, -1)",
        "orient_all <- rep(1, length(m_exact))",
    ),
    "ambiguity_guard_removed": (
        "k4_pan[dup4] <- NA_character_",
        "k4_pan[dup4 & FALSE] <- NA_character_",
    ),
}


@pytest.mark.parametrize("alteration", sorted(ALTERATIONS))
def test_nc2g_extractor_tracks_the_shipped_source(r_toolchain, tmp_path, alteration):
    """RED against an ALTERED source, GREEN against the real one.

    If ``extract_nested`` were returning a stale copy, a hand-transcription, or
    anything other than the bytes on disk, altering those bytes would change
    nothing and this test would stay green. It is the only thing standing
    between the differential agreement test and the vacuous "agrees with itself"
    failure this arc has caught six times.
    """
    rscript, env = r_toolchain
    old, new = ALTERATIONS[alteration]
    real = SUSIE_R.read_text()
    # ⚠ THE CAPTURE GUARD. Without it the leak check below is a coverage
    # REDUCTION, not a strengthening: for a leak that occurred BEFORE this line,
    # `real` captures the already-leaked bytes and the comparison passes where
    # the old fixed-SHA byte diff went red. `HEAD` is symbolic, so no timebomb.
    assert real == git_show("HEAD", SUSIE_R_REL), (
        "run_susie_rss.R was already modified in the working tree BEFORE this "
        "control captured it -- the leak guard below would be comparing against "
        "leaked bytes"
    )
    assert real.count(old) == 1, (
        f"the NC-2g anchor {old!r} is not uniquely present in the frozen source; "
        f"the control would be altering nothing"
    )
    altered = real.replace(old, new)
    assert altered != real

    lf_alt = loader_prefix(tmp_path, source_override=altered)
    out = tmp_path / f"diff_{alteration}.json"
    res = _run_r(rscript, env, differential_r(lf_alt, out), tmp_path,
                 f"diff_{alteration}.R")
    assert res.returncode == 0, f"{res.stdout}\n{res.stderr}"
    rec = json.loads(out.read_text())

    disagreements = [
        name for name, r in rec.items()
        if (r["new"]["keep"] != r["shipped"]["keep"]
            or r["new"]["ld"] != r["shipped"]["ld"]
            or r["new"]["orient"] != r["shipped"]["orient"]
            or r["new"]["counts"] != r["shipped"]["counts"])
    ]
    assert disagreements, (
        f"altering the shipped source ({alteration}) changed NOTHING -- the "
        f"'shipped' side of the differential test is not tracking "
        f"{SUSIE_R_REL}"
    )

    # ⚠ MID-CONTROL, JOB B: the real frozen file must be untouched RIGHT NOW.
    # A SHA-FREE BYTE comparison against the bytes this control itself read, so
    # it still catches a leaked COMMENT -- which the code-only freeze gate
    # (JOB A) would deliberately let through. Byte-exact and timebomb-free.
    assert_unchanged_on_disk(SUSIE_R, real)


def test_nc2g_deleting_the_assignment_raises_the_named_stop(r_toolchain, tmp_path):
    """...rather than silently returning NULL."""
    rscript, env = r_toolchain
    real = SUSIE_R.read_text()
    # ⚠ THE CAPTURE GUARD -- see the twin at the top of NC-2g above.
    assert real == git_show("HEAD", SUSIE_R_REL), (
        "run_susie_rss.R was already modified in the working tree BEFORE this "
        "control captured it -- the leak guard below would be comparing against "
        "leaked bytes"
    )
    anchor = "  match_indices_allele_aware <- function(subset_dt, variants_dt) {"
    assert real.count(anchor) == 1
    altered = real.replace(anchor, "  .w7u_nc2g_renamed <- function(subset_dt, variants_dt) {")
    lf_alt = loader_prefix(tmp_path, source_override=altered)
    code = f"""
{extractor_r()}
r <- tryCatch({{ build_shipped_matcher("{lf_alt}"); "NO_ERROR" }},
              error = function(e) conditionMessage(e))
cat("MSG:", r, "\\n")
"""
    res = _run_r(rscript, env, code, tmp_path, "nc2g_deleted.R")
    assert res.returncode == 0, res.stderr
    assert "STOP-and-surface: could not extract match_indices_allele_aware" in res.stdout
    # JOB B again: SHA-free, byte-exact, and still sensitive to a leaked comment.
    assert_unchanged_on_disk(SUSIE_R, real)


# ==========================================================================
# END-TO-END FIXTURES
#
# NO PANEL EXISTS ON THIS NODE (0/276 .npz banked; data/processed/ld_reference/
# is absent entirely), so every fixture below is synthesised into tmp_path.
#
# TWO PANEL SHAPES, both real:
#   aou    -- R is a dsCMatrix WITH dimnames = GRCh37 chr:pos:ref:alt
#             (ld_npz_to_rds.R:440). This is the shape that produces BOTH the
#             empty-intersection and the "LD must be of class matrix" defects.
#   legacy -- R is a BASE matrix with dimnames NULL plus a variants frame
#             carrying SNP_ID (plink_ld_to_rds.R:88 + build_ld_rownames). This is
#             the 1kG/EUR shape that works today, and it is the substrate for the
#             Track-A byte-identity proof.
# ==========================================================================
_FIXTURE_BUILDER_R = r'''
suppressPackageStartupMessages({
  library(Matrix); library(coloc); library(susieR)
  library(data.table); library(jsonlite)
})
set.seed(20260806)
OUT <- "__OUT__"
KIND <- "__KIND__"            # "rsid" | "chrpos"
SHAPE <- "__SHAPE__"          # "aou"  | "legacy"
BRIDGEABLE <- __BRIDGEABLE__  # TRUE | FALSE
USE_IDENTITY <- __USE_IDENTITY__
dir.create(OUT, recursive = TRUE, showWarnings = FALSE)

n <- 200L
chrom <- "12"
pos <- 110000000L + seq_len(n) * 500L

# ---- PANEL alleles: a non-palindromic A/G ladder with planted specials ----
pan_ref <- rep("A", n); pan_alt <- rep("G", n)
pal_i <- seq(25L, n, by = 25L)                 # planted palindromes (A/T)
pan_ref[pal_i] <- "A"; pan_alt[pal_i] <- "T"
pan <- data.frame(CHR = rep(chrom, n), POS = pos,
                  REF = pan_ref, ALT = pan_alt, stringsAsFactors = FALSE)
# a DUPLICATED 4-key -> `dropped_ambiguous` (panel row 201 mirrors row 40)
pan <- rbind(pan, pan[40L, , drop = FALSE])
n_pan <- nrow(pan)

# ---- CATALOG alleles: exact / transposed / mismatched / unusable ----
cat_ref <- pan_ref; cat_alt <- pan_alt
swap_i <- seq(2L, n, by = 4L)                   # -> flipped, orient -1
tmp <- cat_ref[swap_i]; cat_ref[swap_i] <- cat_alt[swap_i]; cat_alt[swap_i] <- tmp
mis_i <- seq(7L, n, by = 33L)                   # -> dropped_mismatch
cat_ref[mis_i] <- "C"; cat_alt[mis_i] <- "T"
unu_i <- seq(13L, n, by = 47L)                  # -> dropped_unusable
cat_ref[unu_i] <- ""

fit_names <- if (KIND == "rsid") {
  sprintf("rs%d", 900000L + seq_len(n))
} else {
  sprintf("%s:%d", chrom, pos)
}
cat_snp_id <- if (KIND == "rsid") fit_names else rep("", n)

cat_pos <- if (BRIDGEABLE) pos else (pos + 7L)  # 7 bp off -> nothing binds
catalog <- data.frame(CHR = rep(chrom, n), POS = cat_pos,
                      REF = cat_ref, ALT = cat_alt, SNP_ID = cat_snp_id,
                      stringsAsFactors = FALSE)
fwrite(catalog, file.path(OUT, "variants.tsv"), sep = "\t")

# ---- the LD matrix: a genuine AR(1) correlation (PSD, diag 1) ----
rho <- 0.85
d <- abs(outer(seq_len(n_pan), seq_len(n_pan), "-"))
Rd <- rho ^ d
diag(Rd) <- 1

panel_key <- paste(pan$CHR, pan$POS, pan$REF, pan$ALT, sep = ":")
if (SHAPE == "aou") {
  Rs <- as(as(as(Rd, "dMatrix"), "symmetricMatrix"), "CsparseMatrix")
  dimnames(Rs) <- list(panel_key, panel_key)
  ld_obj <- list(R = Rs, variants = pan, use_identity = FALSE, status = "ok")
} else {
  Rb <- Rd
  dimnames(Rb) <- NULL
  legacy_variants <- pan
  legacy_variants$SNP_ID <- c(fit_names, fit_names[40L])
  ld_obj <- list(R = Rb, variants = legacy_variants,
                 use_identity = FALSE, status = "ok")
}
if (USE_IDENTITY) ld_obj <- list(R = NULL, variants = pan,
                                 use_identity = TRUE, status = "too_many_variants")
saveRDS(ld_obj, file.path(OUT, "ld.rds"))

# ---- the GWAS fit, in FIT-NAME space ----
Rfit <- Rd[seq_len(n), seq_len(n)]
dimnames(Rfit) <- list(fit_names, fit_names)
z <- rep(0, n); z[100L] <- 6.5
z <- as.vector(Rfit %*% z) + rnorm(n, sd = 0.05)
se <- rep(0.02, n)
gwas_data <- list(beta = z * se, varbeta = se^2, snp = fit_names,
                  position = pos, type = "quant", N = 50000L, sdY = 1,
                  MAF = rep(0.25, n), LD = Rfit)
gwas_fit <- coloc::runsusie(gwas_data, suffix = 1)
saveRDS(gwas_fit, file.path(OUT, "gwas.fit.rds"))

# ---- the harmonized QTL TSV ----
zq <- rep(0, n); zq[100L] <- 5.5
zq <- as.vector(Rfit %*% zq) + rnorm(n, sd = 0.05)
seq_ <- rep(0.03, n)
qtl <- data.table(
  variant_id = sprintf("chr%s_%d_%s_%s", chrom, pos, pan_ref, pan_alt),
  rsid = if (KIND == "rsid") fit_names else rep("", n),
  beta = zq * seq_, se = seq_, maf = rep(0.25, n), position = pos)
fwrite(qtl, file.path(OUT, "qtl.tsv"), sep = "\t")

cat("FIXTURE_OK n_cs_gwas=", length(gwas_fit$sets$cs %||% list()), "\n", sep = "")
'''


def _build_fixture(rscript, env, out_dir: Path, kind="rsid", shape="aou",
                   bridgeable=True, use_identity=False) -> Path:
    code = (_FIXTURE_BUILDER_R
            .replace("__OUT__", str(out_dir))
            .replace("__KIND__", kind)
            .replace("__SHAPE__", shape)
            .replace("__BRIDGEABLE__", "TRUE" if bridgeable else "FALSE")
            .replace("__USE_IDENTITY__", "TRUE" if use_identity else "FALSE"))
    code = "`%||%` <- function(x, y) if (!is.null(x)) x else y\n" + code
    out_dir.mkdir(parents=True, exist_ok=True)
    f = out_dir / "build.R"
    f.write_text(code)
    res = subprocess.run([str(rscript), str(f)], capture_output=True, text=True,
                         timeout=R_SUBPROCESS_TIMEOUT_S, env=env, cwd=PROJECT_ROOT)
    assert res.returncode == 0, f"fixture build failed:\n{res.stdout}\n{res.stderr}"
    assert "FIXTURE_OK" in res.stdout, res.stdout
    return out_dir


def _run_qtl_coloc(rscript, env, fixture: Path, out_json: Path, *,
                   script: Path | None = None, ancestry="AFR",
                   allele_join: str | None = None,
                   variant_list: Path | None = None,
                   extra: list[str] | None = None) -> subprocess.CompletedProcess:
    cmd = [str(rscript), str(script or QTL_COLOC_R),
           "--gwas-fit", str(fixture / "gwas.fit.rds"),
           "--qtl-sumstats", str(fixture / "qtl.tsv"),
           "--ld-matrix", str(fixture / "ld.rds"),
           "--qtl-source", "gtex_eqtl", "--tissue", "Whole_Blood",
           "--gene-id", "ENSG00000111252", "--region", "SH2B3_12q24",
           "--ancestry", ancestry, "--sdy", "1.0", "--sample-size", "670",
           "--policy", "config/susie_policy.yaml", "--output", str(out_json)]
    if allele_join is not None:
        cmd += ["--ld-allele-join", allele_join]
    if variant_list is not None:
        cmd += ["--variant-list", str(variant_list)]
    cmd += extra or []
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=R_SUBPROCESS_TIMEOUT_S, env=env, cwd=PROJECT_ROOT)


@pytest.fixture(scope="module")
def fx_aou_rsid(r_toolchain, tmp_path_factory):
    rscript, env = r_toolchain
    return _build_fixture(rscript, env, tmp_path_factory.mktemp("aou_rsid"),
                          kind="rsid", shape="aou")


@pytest.fixture(scope="module")
def fx_aou_chrpos(r_toolchain, tmp_path_factory):
    rscript, env = r_toolchain
    return _build_fixture(rscript, env, tmp_path_factory.mktemp("aou_chrpos"),
                          kind="chrpos", shape="aou")


@pytest.fixture(scope="module")
def fx_legacy_eur(r_toolchain, tmp_path_factory):
    rscript, env = r_toolchain
    return _build_fixture(rscript, env, tmp_path_factory.mktemp("legacy_eur"),
                          kind="rsid", shape="legacy")


# ==========================================================================
# T2.4 -- the bridge works, for BOTH live sumstats key conventions
# ==========================================================================
@pytest.mark.parametrize("fx_name,expect_space", [
    ("fx_aou_rsid", "catalog_snp_id"),
    ("fx_aou_chrpos", "catalog_chrpos"),
])
def test_the_catalog_bridges_both_fit_key_conventions(
        request, r_toolchain, tmp_path, fx_name, expect_space):
    """Both conventions are live for AFR (``asthma.AFR -> rs151190501``,
    ``stroke.AFR -> 1:662622``), so a panel-only bridge cannot reach rsID-named
    fits. The catalog reaches both -- and WHICH bridge won is recorded."""
    rscript, env = r_toolchain
    fx = request.getfixturevalue(fx_name)
    out = tmp_path / f"{fx_name}.json"
    res = _run_qtl_coloc(rscript, env, fx, out, allele_join="true",
                         variant_list=fx / "variants.tsv")
    assert res.returncode == 0, f"{res.stdout}\n{res.stderr}"
    d = json.loads(out.read_text())
    assert d["status"] == "success", d
    assert d["ld_key_space"] == expect_space
    assert d["n_snps_overlap"] >= MIN_LD_OVERLAP
    assert d["ld_panel_overlap"] >= MIN_LD_OVERLAP


def test_the_bridge_is_not_reachable_without_the_gate(r_toolchain, tmp_path, fx_aou_rsid):
    """THE DEFECT, REPRODUCED. Ungated, the AoU panel's key space never meets the
    fit's -- the intersection is EMPTY and the job exits 0 with ``too_few_snps``,
    which in bulk is indistinguishable from biology."""
    rscript, env = r_toolchain
    out = tmp_path / "ungated.json"
    res = _run_qtl_coloc(rscript, env, fx_aou_rsid, out)
    assert res.returncode == 0, res.stderr
    d = json.loads(out.read_text())
    assert d["status"] == "too_few_snps"
    assert "after LD intersection" in d["message"]
    assert d["n_snps_overlap"] == 0
    # ...and it says NOTHING about which panel it opened.
    assert "ld_matrix" not in d
    assert "ld_key_space" not in d


def test_every_disposition_class_reaches_the_json(r_toolchain, tmp_path, fx_aou_rsid):
    rscript, env = r_toolchain
    out = tmp_path / "counters.json"
    res = _run_qtl_coloc(rscript, env, fx_aou_rsid, out, allele_join="true",
                         variant_list=fx_aou_rsid / "variants.tsv")
    assert res.returncode == 0, res.stderr
    d = json.loads(out.read_text())
    assert d["ld_matrix"] == str(fx_aou_rsid / "ld.rds")
    assert d["ld_allele_join"] == "true"
    for k in ("ld_allele_exact", "ld_allele_flipped",
              "ld_allele_dropped_palindromic", "ld_allele_dropped_mismatch",
              "ld_allele_dropped_ambiguous", "ld_allele_dropped_unusable"):
        assert k in d, k
        assert isinstance(d[k], int), (k, d[k])
    # NON-VACUITY: a counter block of all zeros would prove nothing.
    assert d["ld_allele_exact"] > 0
    assert d["ld_allele_flipped"] > 0
    assert d["ld_allele_dropped_palindromic"] > 0
    assert d["ld_allele_dropped_mismatch"] > 0
    assert d["ld_allele_dropped_ambiguous"] > 0
    assert d["ld_allele_dropped_unusable"] > 0


# ==========================================================================
# T2.5 -- LOUD failure where verification is impossible
# ==========================================================================
def test_unbridgeable_catalog_exits_non_zero_with_a_named_reason(
        r_toolchain, tmp_path_factory, tmp_path):
    rscript, env = r_toolchain
    fx = _build_fixture(rscript, env, tmp_path_factory.mktemp("unbridgeable"),
                        kind="rsid", shape="aou", bridgeable=False)
    out = tmp_path / "unbridgeable.json"
    res = _run_qtl_coloc(rscript, env, fx, out, allele_join="true",
                         variant_list=fx / "variants.tsv")
    assert res.returncode != 0, f"exited 0:\n{res.stdout}"
    assert not out.exists(), "an output JSON was written on a fatal path"
    err = res.stderr
    assert "LD_JOIN_FATAL" in err
    assert "reason=panel_bridge_below_threshold" in err or \
           "reason=alleles_unavailable_panel" in err, err
    assert "region=SH2B3_12q24" in err
    assert "ancestry=AFR" in err
    assert f"threshold={MIN_LD_OVERLAP}" in err
    # every measured candidate key space, named
    for space in ("panel_rownames", "panel_chrpos", "panel_chrpos_ref_alt",
                  "catalog_snp_id", "catalog_chrpos"):
        assert space in err, f"{space} missing from the rejection: {err}"


@pytest.mark.parametrize("mode,reason", [
    ("absent", "reason=variant_catalog_absent"),
    ("missing", "reason=variant_catalog_missing"),
    ("unreadable", "reason=variant_catalog_unreadable"),
])
def test_catalog_problems_are_distinctly_named_non_zero_rejections(
        r_toolchain, tmp_path, fx_aou_rsid, mode, reason):
    rscript, env = r_toolchain
    out = tmp_path / f"cat_{mode}.json"
    if mode == "absent":
        vl = None
    elif mode == "missing":
        vl = tmp_path / "no_such_catalog.tsv"
    else:
        vl = tmp_path / "empty.tsv"
        vl.write_text("")
    res = _run_qtl_coloc(rscript, env, fx_aou_rsid, out, allele_join="true",
                         variant_list=vl)
    assert res.returncode != 0, res.stdout
    assert not out.exists()
    assert reason in res.stderr, res.stderr


def test_use_identity_under_the_gate_is_rejected_non_zero(
        r_toolchain, tmp_path_factory, tmp_path):
    """``BLAST-RADIUS:38``. Silently fitting ``coloc.susie`` on ``diag(n)``
    under an armed gate substitutes "no LD" for the LD the job was routed
    through the resolver to obtain."""
    rscript, env = r_toolchain
    fx = _build_fixture(rscript, env, tmp_path_factory.mktemp("identity"),
                        kind="rsid", shape="aou", use_identity=True)
    out = tmp_path / "identity.json"
    res = _run_qtl_coloc(rscript, env, fx, out, allele_join="true",
                         variant_list=fx / "variants.tsv")
    assert res.returncode != 0, res.stdout
    assert not out.exists()
    assert "reason=use_identity_under_gate" in res.stderr, res.stderr

    # ...and OFF the gate the SAME input still takes the legacy identity path
    # at rc 0. This is the inverted half: without it, "it fails loudly" could
    # just mean "it fails".
    out2 = tmp_path / "identity_ungated.json"
    res2 = _run_qtl_coloc(rscript, env, fx, out2)
    assert res2.returncode == 0, res2.stderr
    assert out2.exists()


def test_an_unrecognised_flag_value_is_a_hard_error(r_toolchain, tmp_path, fx_aou_rsid):
    rscript, env = r_toolchain
    out = tmp_path / "badflag.json"
    res = _run_qtl_coloc(rscript, env, fx_aou_rsid, out, allele_join="yes")
    assert res.returncode != 0
    assert "must be exactly 'true' or 'false'" in res.stderr
    assert not out.exists()


# ==========================================================================
# T2.6 -- matrix class + memory bound
# ==========================================================================
def test_coloc_receives_a_base_matrix_even_from_a_dscmatrix_panel(
        r_toolchain, tmp_path, fx_aou_rsid):
    """The MEASURED defect: ``coloc::check_dataset(req="LD")`` PASSES on a
    sparse matrix, so the failure surfaces only inside ``runsusie`` -- wrapped in
    a ``tryCatch`` that turns it into ``qtl_susie_failed`` at rc 0."""
    rscript, env = r_toolchain
    probe = f'''
suppressPackageStartupMessages({{library(Matrix); library(coloc); library(susieR)}})
o <- readRDS("{fx_aou_rsid / "ld.rds"}")
cat("panel class:", paste(class(o$R), collapse="/"), "\\n")
n <- 60L
sub <- o$R[seq_len(n), seq_len(n), drop = FALSE]
cat("sparse subset is.matrix:", is.matrix(sub), "\\n")
d <- list(beta = rnorm(n) * 0.02, varbeta = rep(4e-4, n),
          snp = paste0("v", seq_len(n)), position = seq_len(n),
          type = "quant", N = 1000L, sdY = 1, MAF = rep(0.25, n), LD = sub)
dimnames(d$LD) <- list(d$snp, d$snp)
chk <- tryCatch({{ coloc::check_dataset(d, req = "LD"); "CHECK_PASSED" }},
                error = function(e) paste0("CHECK_ERR:", conditionMessage(e)))
cat("check_dataset:", chk, "\\n")
r <- tryCatch({{ coloc::runsusie(d, suffix = 2); "RUNSUSIE_OK" }},
              error = function(e) paste0("RUNSUSIE_ERR:", conditionMessage(e)))
cat("runsusie:", r, "\\n")
'''
    res = _run_r(rscript, env, probe, tmp_path, "sparse_probe.R")
    assert res.returncode == 0, res.stderr
    assert "dsCMatrix" in res.stdout or "dspMatrix" in res.stdout, res.stdout
    assert "sparse subset is.matrix: FALSE" in res.stdout
    assert "check_dataset: CHECK_PASSED" in res.stdout, (
        "check_dataset was expected to PASS on the sparse matrix -- if it now "
        "catches it, this test's premise (and F3) needs re-measuring: " + res.stdout
    )
    assert "runsusie: RUNSUSIE_ERR:" in res.stdout
    assert "LD must be of class matrix" in res.stdout

    # ...and the SCRIPT, under the gate, reaches success on the same panel.
    out = tmp_path / "class.json"
    r2 = _run_qtl_coloc(rscript, env, fx_aou_rsid, out, allele_join="true",
                        variant_list=fx_aou_rsid / "variants.tsv")
    assert r2.returncode == 0, f"{r2.stdout}\n{r2.stderr}"
    assert json.loads(out.read_text())["status"] == "success"


def test_the_full_panel_is_never_densified():
    """T-w7u-04. ``as.matrix()`` on a full ``n_var x n_var`` panel is ~45 GB at
    SH2B3's 75,497 variants. The coercion must be applied to the SUBSET."""
    code = r_code_only(QTL_COLOC_R.read_text())
    assert "as.matrix(ld_full)" not in code
    assert "as.matrix(ld_obj$R)" not in code
    assert "as.matrix(ld_full[idx, idx, drop = FALSE])" in code
    # The one legacy `as.matrix(ld_obj)` survives ONLY off the gate.
    assert "if (LD_ALLELE_JOIN) ld_obj else as.matrix(ld_obj)" in code


def test_subset_then_coerce_is_bounded_on_a_panel_much_larger_than_the_subset(
        r_toolchain, tmp_path):
    """Drives the real code shape on a panel whose DENSE form would be ~4 GB.

    A subset-then-coerce completes in bounded memory; ``as.matrix()`` on the full
    panel would not. The point is that the fixture's full form is far larger than
    the subset, so a coerce-first implementation could not pass this at all.
    """
    probe = r'''
suppressPackageStartupMessages(library(Matrix))
n <- 22000L                       # dense double form = 22000^2 * 8 = ~3.9 GB
i <- seq_len(n)
R <- sparseMatrix(i = i, j = i, x = 1, dims = c(n, n), symmetric = TRUE)
cat("dense_bytes_if_materialised:", format(as.numeric(n)^2 * 8, scientific = TRUE), "\n")
idx <- sample.int(n, 300L)
sub <- as.matrix(R[idx, idx, drop = FALSE])
cat("subset is.matrix:", is.matrix(sub), "dim:", paste(dim(sub), collapse="x"), "\n")
cat("BOUNDED_OK\n")
'''
    rscript, env = r_toolchain
    res = _run_r(rscript, env, probe, tmp_path, "bounded.R")
    assert res.returncode == 0, res.stderr
    assert "BOUNDED_OK" in res.stdout
    assert "subset is.matrix: TRUE" in res.stdout
    assert "dim: 300x300" in res.stdout


# ==========================================================================
# T2.7 -- TRACK-A / EUR CONTAINMENT
# ==========================================================================
def _old_script(tmp_path: Path) -> Path:
    p = tmp_path / "run_qtl_coloc_7b1025d.R"
    p.write_text(_git_show(f"{PRE_CHANGE_REF}:src/snakemake/scripts/run_qtl_coloc.R"))
    return p


@pytest.mark.parametrize("flags", [None, "false"])
def test_eur_json_is_byte_identical_to_7b1025d(
        r_toolchain, tmp_path, fx_legacy_eur, flags):
    """WHOLE FILE, not ``status`` and not ``n_snps_overlap``.

    m3-04c proved EUR numerics move while ``ld_status`` and
    ``ld_overlap_fraction`` stay byte-identical, so those fields are DISQUALIFIED
    as invariance evidence. Track A is in submission with 1,957 legacy coloc
    JSONs and today's coloc successes are 32/32 EUR.
    """
    rscript, env = r_toolchain
    new_out = tmp_path / f"eur_new_{flags}.json"
    old_out = tmp_path / f"eur_old_{flags}.json"
    r_new = _run_qtl_coloc(rscript, env, fx_legacy_eur, new_out,
                           ancestry="EUR", allele_join=flags)
    r_old = _run_qtl_coloc(rscript, env, fx_legacy_eur, old_out,
                           ancestry="EUR", script=_old_script(tmp_path))
    assert r_new.returncode == 0, f"{r_new.stdout}\n{r_new.stderr}"
    assert r_old.returncode == 0, f"{r_old.stdout}\n{r_old.stderr}"
    # NON-VACUITY: an error-status pair would compare equal for free.
    assert json.loads(old_out.read_text())["status"] == "success", \
        "the EUR fixture must reach a SUBSTANTIVE result for byte-identity to mean anything"
    assert new_out.read_bytes() == old_out.read_bytes()


def test_inverted_control_afr_with_the_gate_on_is_not_identical(
        r_toolchain, tmp_path, fx_aou_rsid):
    """A byte-identity proof that has never been seen to fail is not evidence."""
    rscript, env = r_toolchain
    new_out = tmp_path / "afr_new.json"
    old_out = tmp_path / "afr_old.json"
    r_new = _run_qtl_coloc(rscript, env, fx_aou_rsid, new_out, allele_join="true",
                           variant_list=fx_aou_rsid / "variants.tsv")
    r_old = _run_qtl_coloc(rscript, env, fx_aou_rsid, old_out,
                           script=_old_script(tmp_path))
    assert r_new.returncode == 0, r_new.stderr
    assert r_old.returncode == 0, r_old.stderr
    assert new_out.read_bytes() != old_out.read_bytes()
    assert json.loads(new_out.read_text())["status"] == "success"
    assert json.loads(old_out.read_text())["status"] == "too_few_snps"


def test_sample_null_loci_argv_still_takes_the_legacy_path(
        r_toolchain, tmp_path, fx_legacy_eur):
    """``sample_null_loci.py:369-384`` is a SECOND caller and passes NEITHER new
    flag. It is the live proof that the defaults point the right way."""
    src = (PROJECT_ROOT / "src" / "python" / "sample_null_loci.py").read_text()
    assert "--ld-allele-join" not in src
    assert "--variant-list" not in src
    rscript, env = r_toolchain
    out = tmp_path / "nullloci.json"
    res = _run_qtl_coloc(rscript, env, fx_legacy_eur, out, ancestry="EUR")
    assert res.returncode == 0, res.stderr
    d = json.loads(out.read_text())
    assert d["status"] == "success"
    assert "ld_allele_join" not in d, "an additive field leaked onto the legacy caller"


# ==========================================================================
# T2.8 -- the wiring
# ==========================================================================
def test_rule_run_qtl_coloc_threads_the_flag_and_the_catalog():
    text = QTL_COLOC_SMK.read_text()
    assert text.count("--ld-allele-join {params.ld_allele_join}") == 1
    assert "{params.variant_list_flag} {input.variants}" in text
    assert "variants=_qtl_coloc_variants_input" in text
    assert "lockstep_variants_path" in text


def test_the_variant_list_token_is_unconstructible_off_the_allow_list():
    """Not merely quoted -- ABSENT. ``--variant-list`` with an empty value would
    make optparse consume the next flag.

    Evaluated against COMMENT-STRIPPED source: the comment that documents the
    trap necessarily quotes the dangerous form, and a comment satisfying its own
    regex is one of the five vacuous assertions the m3-04c sweep indicts.
    """
    code = strip_py_comments(QTL_COLOC_SMK.read_text())
    assert "--variant-list {input.variants}" not in code
    assert "{params.variant_list_flag} {input.variants}" in code
    assert '"--variant-list" if _qtl_coloc_variants_path(wc) else ""' in code


def test_the_per_pair_receipt_reads_every_counter():
    """A write-only counter is not observability -- the project rule
    ``finemap.smk`` already states."""
    text = QTL_COLOC_SMK.read_text()
    assert "log:" in text and "ld_receipt" in text
    for field in ("ld_matrix", "ld_key_space", "ld_panel_overlap", "ld_allele_join",
                  "ld_allele_exact", "ld_allele_flipped",
                  "ld_allele_dropped_palindromic", "ld_allele_dropped_mismatch",
                  "ld_allele_dropped_ambiguous", "ld_allele_dropped_unusable"):
        assert f"'{field}'" in text, field


def test_run_qtl_coloc_sources_the_shared_join():
    code = r_code_only(QTL_COLOC_R.read_text())
    assert "ld_allele_join.R" in code
    assert "source(LD_ALLELE_JOIN_R)" in code
    assert "ld_allele_join_indices(" in code


def test_the_overlap_floor_agrees_with_the_shipped_policy():
    """No new fatal threshold was invented; the existing one just became loud."""
    code = r_code_only(QTL_COLOC_R.read_text())
    assert f"MIN_COLOC_LD_OVERLAP <- {MIN_LD_OVERLAP}L" in code, (
        f"the script's floor has drifted from config/susie_policy.yaml "
        f"min_ld_overlap={MIN_LD_OVERLAP}"
    )


def test_params_region_id_is_not_declared_here():
    """``run_finemap.params.region_id`` is out of scope and must not be shadowed.

    NARROWED 2026-08-06 under **AUTH-b77-01** (quick-260806-b77). The second
    assertion used to be ``diff.stdout.strip() == ""`` — a WHOLE-FILE pin of
    ``src/snakemake/rules/finemap.smk`` against the FIXED SHA ``7b1025d``. That
    is a **false invariant by construction**: it cannot distinguish a
    ``params.region_id`` regression from a legitimate edit, so it was guaranteed
    to fail on the NEXT change to that file whatever the change was
    (``[[feedback_coverage_assertion_can_be_false_invariant]]``). It fired on
    quick-260806-b77's blast-radius **FINDING J** fix — the per-region receipt —
    which has nowhere else to live, because the other half of that pair is
    ``run_susie_rss.R``, RE-FROZEN at ``dc4bbd2`` with its unfreeze SPENT.
    (``dc4bbd2`` is the pin that was IN FORCE AT THAT TIME and is left as-is
    deliberately: this paragraph is a HISTORICAL record of why AUTH-b77-01 was
    needed, and re-pinning it would falsify history. The live pin is now
    ``bf04199`` — see ``FREEZE_CODE_REF`` — re-set by ``quick-260806-pd3`` on
    2026-08-06 after finding K-1, and RESCOPED from a byte freeze to a CODE
    freeze by ``quick-260806-sr4`` on the same day under ``AUTH-SR4-RESCOPE``.)

    The pin is REPLACED BY ITS OWN SUBJECT, not relaxed: no hunk of a
    ``finemap.smk`` diff may mention ``region_id`` at all. That is **STRICTLY
    STRONGER on the thing this test names** — it says WHICH change is forbidden,
    and it still fails on a ``params.region_id`` edit that arrives inside a
    commit which also legitimately changes something else, a case the whole-file
    pin could not tell apart. Measured at the time of the edit:
    ``git diff 7b1025d HEAD -- src/snakemake/rules/finemap.smk`` is 128 lines
    and contains ``region_id`` **0** times.

    ⚠ THIS IS THE SECONDARY GUARD. The PRIMARY guard rail is
    ``tests/m3/test_occlusion_lockstep_wiring.py::test_params_region_id_is_untouched``,
    which asserts the directive still reads
    ``region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],``
    character-for-character. It is UNTOUCHED by AUTH-b77-01 and green.

    The FIRST assertion below (``qtl_coloc.smk`` declares no ``region_id=lambda``
    of its own) is this test's original subject and is unchanged, verbatim.
    """
    text = QTL_COLOC_SMK.read_text()
    assert "region_id=lambda" not in text
    diff = subprocess.run(
        ["git", "diff", PRE_CHANGE_REF, "HEAD", "--",
         "src/snakemake/rules/finemap.smk"],
        cwd=PROJECT_ROOT, capture_output=True, text=True,
    )
    _assert_finemap_diff_leaves_region_id_alone(diff.stdout)


def _assert_finemap_diff_leaves_region_id_alone(diff_text: str) -> None:
    """AUTH-b77-01's narrowed assertion, factored out so a NEGATIVE CONTROL can
    drive it with a diff in which ``params.region_id`` IS touched.

    A green assertion is evidence only if you have seen it fail, and the
    whole-file pin this replaces was never once exercised against the defect it
    claimed to guard. See
    ``test_nc_auth_b77_01_the_narrowed_pin_still_catches_a_region_id_edit``.
    """
    assert "region_id" not in diff_text, (
        "a finemap.smk change touched region_id. run_finemap.params.region_id "
        f"has been out of scope for every task since {PRE_CHANGE_REF}: it feeds "
        "run_susie_rss.R --region, which looks the id up in "
        "config/regions_curated.csv, and its sibling resolve_ld_path(region_id=...) "
        "argument sits ~30 lines away and is spelled almost identically. "
        f"Offending diff:\n{diff_text}"
    )


def test_nc_auth_b77_01_the_narrowed_pin_still_catches_a_region_id_edit(tmp_path):
    """NC-AUTH-b77-01 — PERMANENT AND IN-SUITE. The price of AUTH-b77-01.

    Prove the NARROWED assertion still catches what it claims by driving it with
    a real ``git diff`` in which ``params.region_id`` IS edited. The edit is made
    on a TEMP COPY inside a throwaway repo; ``src/snakemake/rules/finemap.smk``
    in the working tree is asserted 0-diff MID-CONTROL, the same discipline
    ``260805-w7u``'s NC-2g used against the frozen R source.
    """
    real = FINEMAP_SMK.read_text()
    anchor = "region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],"
    assert real.count(anchor) == 1, (
        "the params.region_id directive is not where this control expects it; "
        "the control could be perturbing nothing"
    )

    repo = tmp_path / "repo"
    (repo / "src" / "snakemake" / "rules").mkdir(parents=True)
    target = repo / "src" / "snakemake" / "rules" / "finemap.smk"
    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "nc@example.invalid"],
        ["git", "config", "user.name", "nc"],
    ):
        subprocess.run(cmd, cwd=repo, check=True, capture_output=True)
    target.write_text(real)
    subprocess.run(["git", "add", "-f", str(target.relative_to(repo))],
                   cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True,
                   capture_output=True)

    # THE PERTURBATION: shadow params.region_id, exactly the defect this guards.
    target.write_text(real.replace(anchor, "region_id=lambda wildcards: wildcards.region,"))
    perturbed = subprocess.run(
        ["git", "diff", "HEAD", "--", "src/snakemake/rules/finemap.smk"],
        cwd=repo, capture_output=True, text=True,
    ).stdout
    assert "region_id" in perturbed, "the control produced no region_id hunk"

    with pytest.raises(AssertionError, match="touched region_id"):
        _assert_finemap_diff_leaves_region_id_alone(perturbed)

    # ...and the REAL diff still passes, so the control is not merely noisy.
    real_diff = subprocess.run(
        ["git", "diff", PRE_CHANGE_REF, "HEAD", "--",
         "src/snakemake/rules/finemap.smk"],
        cwd=PROJECT_ROOT, capture_output=True, text=True,
    ).stdout
    _assert_finemap_diff_leaves_region_id_alone(real_diff)
    assert real_diff.strip(), (
        "the real diff is EMPTY, so the assertion above proved nothing -- this "
        "control is only meaningful while finemap.smk has legitimately changed"
    )

    # MID-CONTROL: the working tree was never written.
    assert FINEMAP_SMK.read_text() == real


# ==========================================================================
# T2.3 -- freeze + scope, asserted continuously
# ==========================================================================
def test_run_susie_rss_code_is_frozen():
    """JOB A -- THE FREEZE GATE. Rescoped from bytes to CODE by quick-260806-sr4
    under AUTH-SR4-RESCOPE; the pin itself did not move."""
    assert_code_frozen(SUSIE_R_REL, FREEZE_CODE_REF, LANG_R)


def r_code_only(text: str) -> str:
    """``text`` with R ``#`` comments removed (string literals preserved).

    An absence claim about CODE must be evaluated against code -- the header of
    ``ld_allele_join.R`` legitimately names ``load_ld_matrix`` when it explains
    the frozen-file reason this is not an extraction.
    """
    out = []
    for line in text.splitlines():
        res, in_str, quote, i = [], False, "", 0
        while i < len(line):
            ch = line[i]
            if in_str:
                res.append(ch)
                if ch == "\\":
                    i += 2
                    if i - 1 < len(line):
                        res.append(line[i - 1])
                    continue
                if ch == quote:
                    in_str = False
            elif ch in "\"'":
                in_str, quote = True, ch
                res.append(ch)
            elif ch == "#":
                break
            else:
                res.append(ch)
            i += 1
        out.append("".join(res))
    return "\n".join(out)


def test_the_new_join_is_not_a_copy_of_the_frozen_file():
    """Sanity: ``ld_allele_join.R`` is a standalone source, not the loader."""
    code = r_code_only(NEW_JOIN_R.read_text())
    assert "ld_allele_join_indices <- function(subset_dt, variants_dt)" in code
    assert "load_ld_matrix" not in code
    assert "option_list" not in code
    # non-vacuity for the stripper
    assert "ld_allele_join_indices" in code
    assert "load_ld_matrix" in NEW_JOIN_R.read_text()  # it IS named, in the header
