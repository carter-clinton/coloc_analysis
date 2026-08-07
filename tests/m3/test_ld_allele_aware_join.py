"""tests/m3/test_ld_allele_aware_join.py -- 260805-o7o Task 1 (FINDING H, loader half).

THE ALLELE-AWARE JOIN, AT PRODUCTION THRESHOLDS.

WHY THIS MODULE EXISTS. m3-04c blast-radius finding H: the sumstats<->panel join
inside ``load_ld_matrix`` is ALLELE-BLIND. Measured at ``0378ec8``:

  * the panel's ``SNP_ID`` is ``chr:pos:REF:ALT`` (``ld_npz_to_rds.R`` /
    ``parse_variants_frame``) while every harmonized AFR sumstats file carries
    either an rsid (``asthma.AFR`` -> ``rs151190501``) or ``chr:pos``
    (``stroke.AFR`` -> ``1:662622``). Neither form can ever equal
    ``chr:pos:ref:alt``, so the SNP_ID branch yields ZERO matches and
  * 100% of the join falls to ``matches <- match(key_subset, key_ld)`` on
    ``paste(CHR, POS, sep=":")`` -- FIRST HIT, REF/ALT IGNORED.

On a multiallelic site that binds a variant's z to a DIFFERENT ALT's LD row. On
a transposed site it binds z to a column signed on the opposite allele, and
SuSiE fits a mirrored LD structure with no error and no flag.

THRESHOLDS. This suite runs at the PRODUCTION thresholds read from
``config/susie_policy.yaml`` (50 / 0.5 / 10), NOT the permissive ``1 / 0.0 / 1``
that ``tests/m3/test_ld_read_path.py`` pins in all 8 of its tests -- that suite
DISABLES the production gate it claims to test and is therefore structurally
incapable of observing any of this.

NEGATIVE CONTROLS. ``[[feedback_green_assertion_needs_a_negative_control]]``:
a green you have never seen red is not evidence. Two controls here are PERMANENT
and IN-SUITE -- they re-run the identical fixture against the pre-change loader
recovered with ``git show 0378ec8:`` and assert the DEFECTIVE outcome:

  * ``test_negative_control_pre_change_loader_binds_the_first_alt``
  * ``test_negative_control_allele_aware_false_is_byte_identical_to_pre_change``

plus in-test controls on every classifier (a palindromic fixture next to a
non-palindromic one, a counter that is non-zero next to the same counter at
zero, a rejection next to the same shape that must NOT reject).

NO-SKIP RULE (inherited from must_have A6): ``_require_m3_r_toolchain()`` ERRORS
rather than skipping when the m3-r-ld marker env is present.
"""
from __future__ import annotations

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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUSIE_R_REL = "src/legacy/region_analysis/scripts/run_susie_rss.R"
SUSIE_R = PROJECT_ROOT / SUSIE_R_REL

#: The commit this plan started from -- the source carrying the allele-blind
#: join. The permanent negative-control substrate.
#: DIFFERENTIAL SUBSTRATE -- never re-pinned. See
#: DEC-2026-08-06-sr4-freeze-scope.
PRE_CHANGE_REF = "0378ec8"

# --------------------------------------------------------------------------
# PRODUCTION thresholds -- read, never hardcoded
# --------------------------------------------------------------------------
_POLICY = yaml.safe_load(
    (PROJECT_ROOT / "config" / "susie_policy.yaml").read_text()
)["susie"]
MIN_LD_OVERLAP = int(_POLICY["min_ld_overlap"])      # 50
MIN_LD_COVERAGE = float(_POLICY["min_ld_coverage"])  # 0.5
MIN_LD_MIN_USE = int(_POLICY["min_ld_min_use"])      # 10

N_SUBSET = 300
BASE_POS = 53809247
CHROM = "16"


@pytest.fixture(scope="session")
def r_toolchain() -> tuple[Path, dict]:
    return _require_m3_r_toolchain()


# --------------------------------------------------------------------------
# R harness. Every panel/subset here carries REF/ALT -- that is the whole point.
# --------------------------------------------------------------------------
_R_PREAMBLE_TEMPLATE = r'''
suppressPackageStartupMessages(library(Matrix))
suppressWarnings(suppressMessages(source("__LOADER_FUNCS__")))
MIN_LD_OVERLAP  <- __MIN_LD_OVERLAP__L
MIN_LD_COVERAGE <- __MIN_LD_COVERAGE__
MIN_LD_MIN_USE  <- __MIN_LD_MIN_USE__L

N_SUBSET <- __N_SUBSET__L
BASE_POS <- __BASE_POS__L
CHROM    <- "__CHROM__"

# A clean biallelic non-palindromic ladder: REF=A ALT=G at every position, so a
# swap (G/A) and a mismatch (C/T) are both unambiguous, and nothing is
# accidentally palindromic.
mk_subset <- function(n = N_SUBSET, ref = "A", alt = "G") {
  i <- seq_len(n)
  data.frame(SNP_ID = paste0("rs", i), CHR = rep(CHROM, n), POS = BASE_POS + i,
             REF = rep(ref, n), ALT = rep(alt, n), stringsAsFactors = FALSE)
}

# A panel over the SAME coordinates. `id_offset` shifts the panel window so the
# realized positional overlap is N_SUBSET - id_offset. `r12` identifies WHICH
# panel's numbers reached the caller.
mk_panel_frame <- function(n = N_SUBSET, id_offset = 0L, ref = "A", alt = "G") {
  i <- seq_len(n) + id_offset
  data.frame(SNP_ID = paste(CHROM, BASE_POS + i, ref, alt, sep = ":"),
             CHR = rep(CHROM, n), POS = BASE_POS + i,
             REF = rep(ref, n), ALT = rep(alt, n), stringsAsFactors = FALSE)
}

save_panel <- function(path, variants, r12 = 0.4) {
  n <- if (is.null(variants)) 2L else nrow(variants)
  R <- diag(n)
  if (n >= 2) { R[1, 2] <- r12; R[2, 1] <- r12 }
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  saveRDS(list(R = R, variants = variants, status = "ld_loaded"), path)
  invisible(path)
}

emit <- function(res, tag) {
  cat(sprintf("%s_SOURCE=%s\n", tag, if (is.null(res$source)) "<NULL>" else res$source))
  cat(sprintf("%s_RNULL=%s\n", tag, is.null(res$R)))
  cat(sprintf("%s_STATUS=%s\n", tag, if (is.null(res$status)) "<NULL>" else res$status))
  cat(sprintf("%s_NROW=%s\n", tag, if (is.null(res$R)) "<NULL>" else nrow(res$R)))
  cat(sprintf("%s_OVERLAP=%s\n", tag,
              if (is.null(res$overlap)) "<NULL>" else as.character(res$overlap)))
  cat(sprintf("%s_REJECTED=%s\n", tag, isTRUE(res$declared_rejected)))
  cat(sprintf("%s_REASON=%s\n", tag,
              if (is.null(res$reject_reason)) "<NULL>" else res$reject_reason))
  cat(sprintf("%s_SUBSETIDX=%s\n", tag,
              if (is.null(res$subset_idx)) "<NULL>"
              else paste(res$subset_idx, collapse = ",")))
  cat(sprintf("%s_ORIENT=%s\n", tag,
              if (is.null(res$allele_orient)) "<NULL>"
              else paste(res$allele_orient, collapse = ",")))
  cat(sprintf("%s_ORIENT_LEN=%s\n", tag,
              if (is.null(res$allele_orient)) "<NULL>"
              else as.character(length(res$allele_orient))))
  cat(sprintf("%s_SUBSETIDX_LEN=%s\n", tag,
              if (is.null(res$subset_idx)) "<NULL>"
              else as.character(length(res$subset_idx))))
  cnt <- res$allele_counts
  for (k in c("exact", "flipped", "dropped_ambiguous", "dropped_palindromic",
              "dropped_mismatch", "dropped_unusable")) {
    cat(sprintf("%s_CNT_%s=%s\n", tag, k,
                if (is.null(cnt) || is.null(cnt[[k]])) "<NULL>"
                else as.character(cnt[[k]])))
  }
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
    """The function-definition PREFIX of an arbitrary run_susie_rss.R text --
    same cut rule as ``_loader_functions_only``, but driven by supplied source so
    a historical revision can be sourced too."""
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
    proc = subprocess.run(
        ["git", "show", f"{PRE_CHANGE_REF}:{SUSIE_R_REL}"],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, (
        f"git show {PRE_CHANGE_REF}:{SUSIE_R_REL} failed: {proc.stderr}"
    )
    assert "load_ld_matrix <- function" in proc.stdout
    assert "match_indices_allele_aware" not in proc.stdout, (
        "the negative-control substrate already carries the fix -- it is not a "
        "pre-change source"
    )
    return _loader_prefix_from_text(
        proc.stdout, tmp_path / "pre_change" / "loader_funcs_only.R"
    )


def _run_r(rscript: Path, env: dict, tmp_path: Path, body: str,
           name: str = "probe.R", loader_funcs: Path | None = None) -> dict:
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


def _run_r_allow_fail(rscript: Path, env: dict, tmp_path: Path, body: str,
                      name: str = "probe.R",
                      loader_funcs: Path | None = None
                      ) -> subprocess.CompletedProcess:
    if loader_funcs is None:
        loader_funcs = _loader_functions_only(tmp_path)
    script = tmp_path / name
    script.write_text(_render_preamble(loader_funcs) + "\n" + body)
    return subprocess.run(
        [str(rscript), str(script)], capture_output=True, text=True,
        timeout=R_SUBPROCESS_TIMEOUT_S, env=env,
    )


# ==========================================================================
# T-T -- the suite cannot silently go permissive
# ==========================================================================
def test_thresholds_under_test_are_the_production_thresholds():
    """Guard against this suite degrading the way ``test_ld_read_path.py`` did
    (it pins ``MIN_LD_OVERLAP <- 1L; MIN_LD_COVERAGE <- 0.0; MIN_LD_MIN_USE <- 1L``
    in all 8 tests, disabling the production gate it claims to test).

    Two halves: the constants must be the production ones AND the RENDERED R
    preamble must actually carry them -- a value read from YAML but never
    interpolated would be theatre.
    """
    assert (MIN_LD_OVERLAP, MIN_LD_COVERAGE, MIN_LD_MIN_USE) == (50, 0.5, 10), (
        "config/susie_policy.yaml no longer holds the thresholds this suite was "
        f"written against: got {(MIN_LD_OVERLAP, MIN_LD_COVERAGE, MIN_LD_MIN_USE)}"
    )
    rendered = _render_preamble(Path("/dev/null"))
    assert "MIN_LD_OVERLAP  <- 50L" in rendered
    assert "MIN_LD_COVERAGE <- 0.5" in rendered
    assert "MIN_LD_MIN_USE  <- 10L" in rendered
    assert "MIN_LD_OVERLAP  <- 1L" not in rendered
    assert "MIN_LD_COVERAGE <- 0.0" not in rendered


# ==========================================================================
# A -- allele_aware = FALSE is BYTE-IDENTICAL to the pre-change loader
# ==========================================================================
def test_negative_control_allele_aware_false_is_byte_identical_to_pre_change(
    r_toolchain, tmp_path
):
    """A (PERMANENT NEGATIVE CONTROL + the containment proof in one).

    The default -- and every legacy caller -- must reproduce ``0378ec8``'s
    matcher EXACTLY. Proven with ``identical()`` on the WHOLE returned list, not
    on selected fields: m3-04c proved ``ld_status`` and ``ld_overlap_fraction``
    stay byte-identical while the numerics move, so a field-wise comparison is
    exactly the evidence that has already failed once here.

    Both loaders are sourced into the SAME R process under different names, run
    against the SAME .rds, and the two result objects compared. The additive
    ``allele_orient`` / ``allele_counts`` fields are NULL under
    ``allele_aware = FALSE``, and assigning NULL into an R list is a no-op, so
    ``identical()`` is the right instrument and not an over-claim.

    This test is ALSO the negative control for every allele-aware assertion
    below: if the new matcher ever leaked into the default path, this goes red.
    """
    rscript, env = r_toolchain
    pre = _pre_change_loader_prefix(tmp_path)
    cur = _loader_functions_only(tmp_path)
    panel = tmp_path / "ld_reference" / "AFR" / "FTO_16q12.rds"
    body = (
        f'save_panel("{panel}", mk_panel_frame(id_offset = 0L), r12 = 0.42)\n'
        'sub <- mk_subset()\n'
        # current source -> new_load ; pre-change source -> old_load
        f'source("{cur}")\nnew_load <- load_ld_matrix\n'
        f'source("{pre}")\nold_load <- load_ld_matrix\n'
        f'a <- new_load("{tmp_path / "ld_reference"}", "AFR", "FTO_16q12", sub,'
        ' authoritative = FALSE)\n'
        f'b <- old_load("{tmp_path / "ld_reference"}", "AFR", "FTO_16q12", sub,'
        ' authoritative = FALSE)\n'
        'cat(sprintf("IDENTICAL=%s\\n", identical(a, b)))\n'
        'cat(sprintf("A_OVERLAP=%s\\n", a$overlap))\n'
        'cat(sprintf("A_ORIENT_NULL=%s\\n", is.null(a$allele_orient)))\n'
        'cat(sprintf("A_COUNTS_NULL=%s\\n", is.null(a$allele_counts)))\n'
        # ...and the SAME comparison with the flag ON must be FALSE, or
        # `identical()` here would be satisfied by a no-op implementation.
        f'c2 <- new_load("{tmp_path / "ld_reference"}", "AFR", "FTO_16q12", sub,'
        ' authoritative = FALSE, allele_aware = TRUE)\n'
        'cat(sprintf("IDENTICAL_AWARE=%s\\n", identical(c2, b)))\n'
        'cat(sprintf("C_ORIENT_NULL=%s\\n", is.null(c2$allele_orient)))\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tA.R", loader_funcs=cur)
    assert vals["IDENTICAL"] == "TRUE", (
        "allele_aware = FALSE is NOT byte-identical to the pre-change loader -- "
        "the default path moved, and every EUR/TRANS containment claim in this "
        "plan is void"
    )
    assert vals["A_OVERLAP"] == str(N_SUBSET)
    assert vals["A_ORIENT_NULL"] == "TRUE"
    assert vals["A_COUNTS_NULL"] == "TRUE"
    # NEGATIVE CONTROL: the comparison can detect a difference at all.
    assert vals["IDENTICAL_AWARE"] == "FALSE", (
        "identical() returned TRUE even with allele_aware = TRUE -- the "
        "comparison is incapable of observing the change and test A is vacuous"
    )
    assert vals["C_ORIENT_NULL"] == "FALSE"


# ==========================================================================
# B -- MULTIALLELIC disambiguation, with the defect asserted permanently
# ==========================================================================
#: ⚠ DEVIATION FROM THE PLAN'S LITERAL FIXTURE, RECORDED HERE RATHER THAN
#: ABSORBED. The plan's <behavior> block for Task 1 states BOTH of these:
#:
#:   "Multiallelic disambiguation: a panel carrying 1:100:A:G and 1:100:A:T at
#:    the SAME position, and a sumstats row REF=A ALT=T -> binds to the A:T row."
#:   "Palindromic drop: sumstats REF=A ALT=T vs panel 1:100:A:T -> DROPPED."
#:
#: A/T IS PALINDROMIC, so those two sentences are mutually unsatisfiable as
#: written. The palindromic-drop rule is the load-bearing scientific decision
#: (restated three times in the plan and carried by threat register T-o7o-03),
#: so it is honoured EXACTLY and the multiallelic fixture uses a NON-palindromic
#: alternate (A/C) instead. That proves the property the plan's must_haves
#: actually name -- "a sumstats variant binds to the panel LD row whose REF/ALT
#: it actually matches, never to an arbitrary ALT at the same position" --
#: without weakening anything. The plan's LITERAL A/T example is ALSO asserted,
#: as a DROP, in ``test_plan_literal_multiallelic_at_row_is_dropped_palindromic``
#: below, so both sentences are covered and neither is quietly discarded.
_MULTIALLELIC_PANEL = (
    # TWO panel rows at the SAME position: A/G first, A/C second. The sumstats
    # row is A/C, so an allele-blind matcher takes row 1 (A/G) and an
    # allele-aware one takes row 2. The discriminator is WHICH panel row the
    # variant bound to, read straight off the shrunk variants frame.
    'pan <- rbind(\n'
    '  data.frame(SNP_ID = "x1", CHR = CHROM, POS = BASE_POS + 1L, REF = "A",\n'
    '             ALT = "G", stringsAsFactors = FALSE),\n'
    '  data.frame(SNP_ID = "x2", CHR = CHROM, POS = BASE_POS + 1L, REF = "A",\n'
    '             ALT = "C", stringsAsFactors = FALSE),\n'
    '  mk_panel_frame(n = 60L, id_offset = 1L)\n'
    ')\n'
    'sub <- rbind(\n'
    '  data.frame(SNP_ID = "rs1", CHR = CHROM, POS = BASE_POS + 1L, REF = "A",\n'
    '             ALT = "C", stringsAsFactors = FALSE),\n'
    '  mk_subset(n = 60L)[2:60, ]\n'
    ')\n'
)


def test_multiallelic_site_binds_to_the_matching_alt(r_toolchain, tmp_path):
    """B. A panel carrying ``1:100:A:G`` AND ``1:100:A:C`` at the SAME position,
    with a sumstats row ``REF=A ALT=C``, must bind to the ``A:C`` row.

    THIS IS FINDING H'S CORE. The legacy ``match(paste(CHR,POS,sep=":"), ...)``
    returns the FIRST hit, so the variant's z is fitted against the LD row of a
    DIFFERENT alternate allele -- a wrong row, silently, with no status change.

    The discriminator is WHICH PANEL ROW the variant bound to (``x2``), not a
    path or a status string.

    (See ``_MULTIALLELIC_PANEL`` for why the alternate is C and not the plan's
    literal T.)

    NEGATIVE CONTROL (PERMANENT, in-suite):
    ``test_negative_control_pre_change_loader_binds_the_first_alt``.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    panel = ld_dir / "AFR_aou" / "m2_region_00040__sub14.rds"
    body = (
        _MULTIALLELIC_PANEL
        + f'save_panel("{panel}", pan, r12 = 0.90)\n'
        + f'res <- load_ld_matrix("{ld_dir}", "AFR", "m2_region_00040__sub14",'
          f' sub, authoritative = TRUE, allele_aware = TRUE, ld_file = "{panel}")\n'
        + 'emit(res, "AW")\n'
        # the panel row the FIRST subset row bound to, read from the shrunk
        # variants frame the loader returns
        + 'cat(sprintf("AW_BOUND_SNPID=%s\\n", res$variants$SNP_ID[1]))\n'
        + 'cat(sprintf("AW_BOUND_ALT=%s\\n", res$variants$ALT[1]))\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tB.R")
    assert vals["AW_BOUND_ALT"] == "C", (
        f"the allele-aware matcher bound the A/C sumstats row to a panel row "
        f"with ALT={vals['AW_BOUND_ALT']!r} (SNP_ID={vals['AW_BOUND_SNPID']!r}) "
        "-- i.e. it is still taking the first hit at the position"
    )
    assert vals["AW_BOUND_SNPID"] == "x2", vals["AW_BOUND_SNPID"]
    assert vals["AW_CNT_flipped"] == "0", vals["AW_CNT_flipped"]
    assert vals["AW_CNT_dropped_ambiguous"] == "0", vals["AW_CNT_dropped_ambiguous"]


def test_plan_literal_multiallelic_at_row_is_dropped_palindromic(
    r_toolchain, tmp_path
):
    """B'. The plan's LITERAL multiallelic example (``REF=A ALT=T`` against a
    panel carrying ``A:G`` and ``A:T`` at one position) resolves to a
    PALINDROMIC DROP, not a bind -- because the plan's own palindromic rule
    takes precedence and A/T is a palindrome.

    Asserted explicitly so the contradiction inside the plan's ``<behavior>``
    block is recorded in the suite rather than silently resolved by whoever
    wrote the fixture. The scientifically important half -- the variant is NOT
    bound to the ``A:G`` row -- holds either way, which is why the deviation is
    safe.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    panel = ld_dir / "AFR_aou" / "plan_literal.rds"
    body = (
        'pan <- rbind(\n'
        '  data.frame(SNP_ID = "x1", CHR = CHROM, POS = BASE_POS + 1L, REF = "A",\n'
        '             ALT = "G", stringsAsFactors = FALSE),\n'
        '  data.frame(SNP_ID = "x2", CHR = CHROM, POS = BASE_POS + 1L, REF = "A",\n'
        '             ALT = "T", stringsAsFactors = FALSE),\n'
        '  mk_panel_frame(n = 60L, id_offset = 1L)\n'
        ')\n'
        'sub <- rbind(\n'
        '  data.frame(SNP_ID = "rs1", CHR = CHROM, POS = BASE_POS + 1L, REF = "A",\n'
        '             ALT = "T", stringsAsFactors = FALSE),\n'
        '  mk_subset(n = 60L)[2:60, ]\n'
        ')\n'
        f'save_panel("{panel}", pan, r12 = 0.90)\n'
        f'res <- load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{panel}")\n'
        'emit(res, "LIT")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tBp.R")
    assert vals["LIT_CNT_dropped_palindromic"] == "1", (
        f"expected the A/T row to be dropped as palindromic, got "
        f"{vals['LIT_CNT_dropped_palindromic']}"
    )
    kept = {int(i) for i in vals["LIT_SUBSETIDX"].split(",")}
    assert 1 not in kept, (
        "the palindromic A/T sumstats row survived into keep -- it would be "
        "bound to a panel row whose strand cannot be verified"
    )
    assert vals["LIT_OVERLAP"] == "59", vals["LIT_OVERLAP"]


def test_negative_control_pre_change_loader_binds_the_first_alt(
    r_toolchain, tmp_path
):
    """B-control (PERMANENT). The IDENTICAL fixture against ``0378ec8``'s loader
    binds to the FIRST panel row (``A:G``, ``SNP_ID = "x1"``) -- finding H,
    reproduced and asserted, permanently in-suite.

    If anyone ever neuters the fixture so the two panel rows stop colliding at a
    position, THIS goes red rather than test B silently passing for the wrong
    reason.
    """
    rscript, env = r_toolchain
    pre = _pre_change_loader_prefix(tmp_path)
    ld_dir = tmp_path / "ld_reference"
    panel = ld_dir / "AFR_aou" / "m2_region_00040__sub14.rds"
    body = (
        _MULTIALLELIC_PANEL
        + f'save_panel("{panel}", pan, r12 = 0.90)\n'
        + f'res <- load_ld_matrix("{ld_dir}", "AFR", "m2_region_00040__sub14",'
          f' sub, authoritative = TRUE, ld_file = "{panel}")\n'
        + 'cat(sprintf("PRE_BOUND_SNPID=%s\\n", res$variants$SNP_ID[1]))\n'
        + 'cat(sprintf("PRE_BOUND_ALT=%s\\n", res$variants$ALT[1]))\n'
        + 'cat(sprintf("PRE_OVERLAP=%s\\n", res$overlap))\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tB_pre.R", loader_funcs=pre)
    assert vals["PRE_BOUND_ALT"] == "G", (
        "the pre-change loader was expected to bind the A/C sumstats row to the "
        f"FIRST panel row (ALT=G); it bound ALT={vals['PRE_BOUND_ALT']!r} -- the "
        "control no longer reproduces the defect it guards"
    )
    assert vals["PRE_BOUND_SNPID"] == "x1", vals["PRE_BOUND_SNPID"]


# ==========================================================================
# C -- SWAP: matched, orient = -1, counted as flipped
# ==========================================================================
def test_transposed_alleles_are_matched_and_oriented_minus_one(
    r_toolchain, tmp_path
):
    """C. Sumstats ``REF=A ALT=G`` against a panel row ``pos:G:A`` is LEGITIMATE
    DATA whose only defect is bookkeeping: both sides code on ALT, so negating z
    restores it at zero cost and SuSiE's PIP is invariant to the coding of any
    single variant. It must be KEPT with ``orient = -1``, never dropped.

    Fixture: the first 60 subset rows are A/G, the panel is G/A at exactly those
    positions -> every row flips.

    NEGATIVE CONTROL (in-test): the SAME shape with a panel that is A/G gives
    ``flipped == 0`` and ``exact == 60``, so "everything flips" cannot pass.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    swapped = ld_dir / "AFR_aou" / "swapped.rds"
    aligned = ld_dir / "AFR_aou" / "aligned.rds"
    body = (
        'sub <- mk_subset(n = 60L, ref = "A", alt = "G")\n'
        f'save_panel("{swapped}", mk_panel_frame(n = 60L, ref = "G", alt = "A"),'
        ' r12 = 0.90)\n'
        f'save_panel("{aligned}", mk_panel_frame(n = 60L, ref = "A", alt = "G"),'
        ' r12 = 0.90)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{swapped}"), "SWAP")\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{aligned}"), "SAME")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tC.R")

    assert vals["SWAP_OVERLAP"] == "60", vals["SWAP_OVERLAP"]
    assert vals["SWAP_CNT_flipped"] == "60", vals["SWAP_CNT_flipped"]
    assert vals["SWAP_CNT_exact"] == "0", vals["SWAP_CNT_exact"]
    assert set(vals["SWAP_ORIENT"].split(",")) == {"-1"}, vals["SWAP_ORIENT"]
    assert vals["SWAP_CNT_dropped_mismatch"] == "0", vals["SWAP_CNT_dropped_mismatch"]
    assert vals["SWAP_SOURCE"] == str(swapped)

    # NEGATIVE CONTROL -- an aligned panel must NOT flip anything
    assert vals["SAME_CNT_flipped"] == "0", (
        "an ALIGNED panel reported flips -- the orientation classifier is "
        "flipping indiscriminately and test C is vacuous"
    )
    assert vals["SAME_CNT_exact"] == "60", vals["SAME_CNT_exact"]
    assert set(vals["SAME_ORIENT"].split(",")) == {"1"}, vals["SAME_ORIENT"]


# ==========================================================================
# D -- the DROP classes, each with a zero-counter control in the same module
# ==========================================================================
def test_palindromic_variants_are_dropped_and_counted(r_toolchain, tmp_path):
    """D1. Sumstats ``REF=A ALT=T`` against panel ``pos:A:T`` is an EXACT match
    -- and it is exactly the class that can be silently sign-wrong, because
    ``ld_npz_to_rds.R``'s liftover (``:348-361``) carries ref/alt through the
    GRCh38->GRCh37 lift VERBATIM without complementing them. A strand-inverted
    chain block therefore produces a palindromic exact match whose LD is signed
    on the opposite strand, and NOTHING in the allele codes reveals it. Every
    other inversion class self-reports as a mismatch.

    So palindromes are DROPPED, counted, and absent from ``keep``/``ld``.

    NEGATIVE CONTROL (in-test): the identical shape with ``REF=A ALT=G`` gives
    ``dropped_palindromic == 0`` -- the classifier is not dropping everything.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    pal = ld_dir / "AFR_aou" / "pal.rds"
    nonpal = ld_dir / "AFR_aou" / "nonpal.rds"
    body = (
        'sub_pal <- mk_subset(n = 60L, ref = "A", alt = "T")\n'
        'sub_ok  <- mk_subset(n = 60L, ref = "A", alt = "G")\n'
        f'save_panel("{pal}", mk_panel_frame(n = 60L, ref = "A", alt = "T"), r12 = 0.9)\n'
        f'save_panel("{nonpal}", mk_panel_frame(n = 60L, ref = "A", alt = "G"), r12 = 0.9)\n'
        # A wholly palindromic subset keeps NOTHING, so in declared mode the
        # panel is REJECTED for overlap -- the drop is a legitimate overlap
        # loss routed through the EXISTING gate, not a new fatal threshold.
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub_pal, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{pal}"), "PALD")\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub_ok, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{nonpal}"), "OKAY")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tD1.R")

    assert vals["PALD_REJECTED"] == "TRUE", vals["PALD_REJECTED"]
    assert vals["PALD_REASON"] == "overlap_below_min_use", vals["PALD_REASON"]
    assert vals["OKAY_OVERLAP"] == "60", vals["OKAY_OVERLAP"]
    assert vals["OKAY_CNT_dropped_palindromic"] == "0", (
        "a NON-palindromic fixture reported palindromic drops -- the classifier "
        "matches everything and D1 is vacuous"
    )
    assert vals["OKAY_CNT_exact"] == "60"


def test_palindromic_drop_counter_is_visible_on_a_returned_result(
    r_toolchain, tmp_path
):
    """D1b. D1 proves the palindromic rows are gone; this proves they are
    COUNTED on a result the caller actually receives.

    Fixture: 60 clean A/G rows (which clear the gate) plus 20 palindromic A/T
    rows at further positions that the panel also carries. The returned result
    must have ``overlap == 60`` and ``dropped_palindromic == 20``, and the
    palindromic subset indices must be ABSENT from ``subset_idx``.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    panel = ld_dir / "AFR_aou" / "mixed.rds"
    body = (
        'sub <- rbind(mk_subset(n = 60L, ref = "A", alt = "G"),\n'
        '             data.frame(SNP_ID = paste0("rsP", 1:20),\n'
        '                        CHR = rep(CHROM, 20), POS = BASE_POS + 500L + 1:20,\n'
        '                        REF = rep("A", 20), ALT = rep("T", 20),\n'
        '                        stringsAsFactors = FALSE))\n'
        'pan <- rbind(mk_panel_frame(n = 60L, ref = "A", alt = "G"),\n'
        '             data.frame(SNP_ID = paste0("p", 1:20),\n'
        '                        CHR = rep(CHROM, 20), POS = BASE_POS + 500L + 1:20,\n'
        '                        REF = rep("A", 20), ALT = rep("T", 20),\n'
        '                        stringsAsFactors = FALSE))\n'
        f'save_panel("{panel}", pan, r12 = 0.9)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{panel}"), "MIX")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tD1b.R")
    assert vals["MIX_OVERLAP"] == "60", vals["MIX_OVERLAP"]
    assert vals["MIX_CNT_dropped_palindromic"] == "20", (
        f"expected 20 palindromic drops, got {vals['MIX_CNT_dropped_palindromic']}"
    )
    assert vals["MIX_CNT_exact"] == "60"
    kept = {int(i) for i in vals["MIX_SUBSETIDX"].split(",")}
    assert kept == set(range(1, 61)), sorted(kept)[:5]
    assert not (kept & set(range(61, 81))), "a palindromic row survived into keep"
    assert vals["MIX_ORIENT_LEN"] == vals["MIX_SUBSETIDX_LEN"] == "60"


def test_allele_mismatch_at_a_present_position_is_dropped_and_counted(
    r_toolchain, tmp_path
):
    """D2. Position present in the panel, alleles ``C/T`` vs panel ``A/G``:
    neither the exact nor the swapped 4-key hits, so the variant is DROPPED and
    counted as ``dropped_mismatch`` -- NOT bound to the position's row.

    This is also the class a strand-inverted, NON-palindromic liftover lands in:
    it self-reports.

    NEGATIVE CONTROL (in-test): the same fixture with matching alleles gives
    ``dropped_mismatch == 0`` and ``exact == 60``.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    panel = ld_dir / "AFR_aou" / "ag.rds"
    body = (
        'sub_bad <- mk_subset(n = 60L, ref = "C", alt = "T")\n'
        'sub_ok  <- mk_subset(n = 60L, ref = "A", alt = "G")\n'
        f'save_panel("{panel}", mk_panel_frame(n = 60L, ref = "A", alt = "G"), r12 = 0.9)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub_bad, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{panel}"), "BAD")\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub_ok, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{panel}"), "GOOD")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tD2.R")
    # every row mismatched -> zero overlap -> the declared panel is REJECTED
    assert vals["BAD_REJECTED"] == "TRUE", vals["BAD_REJECTED"]
    assert vals["BAD_REASON"] == "overlap_below_min_use", vals["BAD_REASON"]
    assert vals["GOOD_OVERLAP"] == "60", vals["GOOD_OVERLAP"]
    assert vals["GOOD_CNT_dropped_mismatch"] == "0", (
        "a fully-matching fixture reported mismatch drops -- the classifier is "
        "not discriminating and D2 is vacuous"
    )


def test_mismatch_counter_is_visible_on_a_returned_result(r_toolchain, tmp_path):
    """D2b. The mismatch counter on a result the caller actually receives:
    60 clean A/G rows plus 15 C/T rows at positions the panel carries as A/G."""
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    panel = ld_dir / "AFR_aou" / "mm.rds"
    body = (
        'sub <- rbind(mk_subset(n = 60L, ref = "A", alt = "G"),\n'
        '             data.frame(SNP_ID = paste0("rsM", 1:15),\n'
        '                        CHR = rep(CHROM, 15), POS = BASE_POS + 800L + 1:15,\n'
        '                        REF = rep("C", 15), ALT = rep("T", 15),\n'
        '                        stringsAsFactors = FALSE))\n'
        'pan <- rbind(mk_panel_frame(n = 60L, ref = "A", alt = "G"),\n'
        '             data.frame(SNP_ID = paste0("pM", 1:15),\n'
        '                        CHR = rep(CHROM, 15), POS = BASE_POS + 800L + 1:15,\n'
        '                        REF = rep("A", 15), ALT = rep("G", 15),\n'
        '                        stringsAsFactors = FALSE))\n'
        f'save_panel("{panel}", pan, r12 = 0.9)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{panel}"), "MM")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tD2b.R")
    assert vals["MM_OVERLAP"] == "60", vals["MM_OVERLAP"]
    assert vals["MM_CNT_dropped_mismatch"] == "15", vals["MM_CNT_dropped_mismatch"]
    assert vals["MM_CNT_dropped_palindromic"] == "0", vals["MM_CNT_dropped_palindromic"]
    assert vals["MM_CNT_exact"] == "60"


def test_ambiguous_duplicate_four_key_is_dropped_and_counted(r_toolchain, tmp_path):
    """D3. A panel carrying the SAME 4-key twice cannot be bound to a single LD
    row, so the key is removed from the match TABLE entirely and the variant is
    dropped as ``dropped_ambiguous`` -- neither duplicate is used.

    Same "a fallback that is never constructed cannot be silently taken"
    discipline 260805-23d applied to ``dir_candidates``.

    NEGATIVE CONTROL (in-test): the same panel WITHOUT the duplicate gives
    ``dropped_ambiguous == 0`` and one more kept row.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    dup = ld_dir / "AFR_aou" / "dup.rds"
    uniq = ld_dir / "AFR_aou" / "uniq.rds"
    body = (
        'sub <- mk_subset(n = 60L, ref = "A", alt = "G")\n'
        'pan_u <- mk_panel_frame(n = 60L, ref = "A", alt = "G")\n'
        # duplicate the FIRST panel row verbatim -> its 4-key appears twice
        'pan_d <- rbind(pan_u, pan_u[1, ])\n'
        f'save_panel("{dup}", pan_d, r12 = 0.9)\n'
        f'save_panel("{uniq}", pan_u, r12 = 0.9)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{dup}"), "DUP")\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{uniq}"), "UNQ")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tD3.R")
    assert int(vals["DUP_CNT_dropped_ambiguous"]) >= 1, (
        f"a duplicated 4-key was not counted as ambiguous: "
        f"{vals['DUP_CNT_dropped_ambiguous']}"
    )
    assert vals["DUP_OVERLAP"] == "59", vals["DUP_OVERLAP"]
    kept = {int(i) for i in vals["DUP_SUBSETIDX"].split(",")}
    assert 1 not in kept, "the ambiguous variant was bound to one of the duplicates"
    # NEGATIVE CONTROL
    assert vals["UNQ_CNT_dropped_ambiguous"] == "0", (
        "a panel with NO duplicate 4-key reported ambiguity -- D3 is vacuous"
    )
    assert vals["UNQ_OVERLAP"] == "60", vals["UNQ_OVERLAP"]


@pytest.mark.parametrize("bad", ['"N"', '""', 'NA_character_'])
def test_unusable_alleles_are_dropped_and_counted(r_toolchain, tmp_path, bad):
    """D4. ``REF`` (or ``ALT``) that is ``"N"`` / ``""`` / ``NA`` on EITHER side
    cannot be oriented, so the variant is DROPPED and counted as
    ``dropped_unusable`` -- never matched on position alone.

    ``collect_region_variants.py:86-88`` really does fill ``"N"`` when a trait
    lacks alleles, so this is a live shape, not a hypothetical.

    NEGATIVE CONTROL: the sibling ``exact == 60`` rows in the SAME fixture are
    kept, so "drop everything" cannot pass.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    panel = ld_dir / "AFR_aou" / "unusable.rds"
    body = (
        'sub <- rbind(mk_subset(n = 60L, ref = "A", alt = "G"),\n'
        '             data.frame(SNP_ID = paste0("rsU", 1:12),\n'
        '                        CHR = rep(CHROM, 12), POS = BASE_POS + 900L + 1:12,\n'
        f'                        REF = rep({bad}, 12), ALT = rep("G", 12),\n'
        '                        stringsAsFactors = FALSE))\n'
        'pan <- rbind(mk_panel_frame(n = 60L, ref = "A", alt = "G"),\n'
        '             data.frame(SNP_ID = paste0("pU", 1:12),\n'
        '                        CHR = rep(CHROM, 12), POS = BASE_POS + 900L + 1:12,\n'
        '                        REF = rep("A", 12), ALT = rep("G", 12),\n'
        '                        stringsAsFactors = FALSE))\n'
        f'save_panel("{panel}", pan, r12 = 0.9)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{panel}"), "UNU")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name=f"tD4_{abs(hash(bad))}.R")
    assert vals["UNU_CNT_dropped_unusable"] == "12", (
        f"REF={bad} was not counted as unusable: {vals['UNU_CNT_dropped_unusable']}"
    )
    assert vals["UNU_OVERLAP"] == "60", vals["UNU_OVERLAP"]
    assert vals["UNU_CNT_exact"] == "60", vals["UNU_CNT_exact"]


def test_absent_position_is_ordinary_non_overlap_and_increments_no_counter(
    r_toolchain, tmp_path
):
    """D5. A sumstats variant whose ``chr:pos`` is not in the panel AT ALL is
    ordinary non-overlap -- not a defect, and it must NOT inflate any drop
    counter. Otherwise the counters would read as allele failures on every
    partially-overlapping region and be useless as an operator signal.

    NEGATIVE CONTROL: the counters are non-zero in the palindromic / mismatch /
    ambiguous / unusable tests in THIS module, so "all counters are always 0"
    cannot satisfy this test.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    panel = ld_dir / "AFR_aou" / "partial.rds"
    body = (
        # 80 sumstats rows, panel covers only the first 60 positions
        'sub <- mk_subset(n = 80L, ref = "A", alt = "G")\n'
        f'save_panel("{panel}", mk_panel_frame(n = 60L, ref = "A", alt = "G"), r12 = 0.9)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{panel}"), "PART")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tD5.R")
    assert vals["PART_OVERLAP"] == "60", vals["PART_OVERLAP"]
    assert vals["PART_CNT_exact"] == "60"
    for k in ("dropped_ambiguous", "dropped_palindromic", "dropped_mismatch",
              "dropped_unusable"):
        assert vals[f"PART_CNT_{k}"] == "0", (
            f"{k} incremented for a position the panel simply does not carry: "
            f"{vals[f'PART_CNT_{k}']}"
        )


# ==========================================================================
# E -- the two VERIFICATION-IMPOSSIBLE rejections
# ==========================================================================
def test_panel_without_alleles_is_a_structured_rejection(r_toolchain, tmp_path):
    """E1. ``allele_aware = TRUE``, ``authoritative = TRUE``, a panel whose
    ``variants`` frame has NO REF/ALT columns: verification is IMPOSSIBLE, so
    the loader returns a STRUCTURED rejection rather than degrading to a
    position-only match. Degrading here is PRECISELY finding H.

    NEGATIVE CONTROL (in-test): the identical panel WITH REF/ALT is accepted.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    noalleles = ld_dir / "AFR_aou" / "noalleles.rds"
    withalleles = ld_dir / "AFR_aou" / "withalleles.rds"
    body = (
        'sub <- mk_subset(n = 60L)\n'
        'pan <- mk_panel_frame(n = 60L)\n'
        f'save_panel("{noalleles}", pan[, c("SNP_ID", "CHR", "POS")], r12 = 0.9)\n'
        f'save_panel("{withalleles}", pan, r12 = 0.9)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{noalleles}"), "NOP")\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{withalleles}"), "YESP")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tE1.R")
    assert vals["NOP_REJECTED"] == "TRUE", vals["NOP_REJECTED"]
    assert vals["NOP_REASON"] == "alleles_unavailable_panel", vals["NOP_REASON"]
    assert vals["NOP_STATUS"] == "ld_declared_rejected;alleles_unavailable_panel", (
        vals["NOP_STATUS"]
    )
    assert vals["NOP_RNULL"] == "TRUE"
    # NEGATIVE CONTROL
    assert vals["YESP_REJECTED"] == "FALSE", (
        "a panel WITH REF/ALT was also rejected -- the guard fires "
        "unconditionally and E1 is vacuous"
    )
    assert vals["YESP_OVERLAP"] == "60"


def test_sumstats_without_alleles_is_a_structured_rejection(r_toolchain, tmp_path):
    """E2. The mirror case: the sumstats subset carries no usable REF/ALT.

    NEGATIVE CONTROL (in-test): the identical subset WITH alleles is accepted;
    and an all-``"N"`` REF/ALT subset (the ``collect_region_variants.py:86-88``
    shape) rejects too, so "column present" is not mistaken for "usable".
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    panel = ld_dir / "AFR_aou" / "p.rds"
    body = (
        'sub_ok <- mk_subset(n = 60L)\n'
        'sub_nocol <- sub_ok[, c("SNP_ID", "CHR", "POS")]\n'
        'sub_alln  <- mk_subset(n = 60L, ref = "N", alt = "N")\n'
        f'save_panel("{panel}", mk_panel_frame(n = 60L), r12 = 0.9)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub_nocol, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{panel}"), "NOCOL")\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub_alln, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{panel}"), "ALLN")\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub_ok, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{panel}"), "OKS")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tE2.R")
    assert vals["NOCOL_REJECTED"] == "TRUE"
    assert vals["NOCOL_REASON"] == "alleles_unavailable_sumstats", vals["NOCOL_REASON"]
    assert vals["ALLN_REJECTED"] == "TRUE"
    assert vals["ALLN_REASON"] == "alleles_unavailable_sumstats", vals["ALLN_REASON"]
    # NEGATIVE CONTROL
    assert vals["OKS_REJECTED"] == "FALSE", (
        "a subset WITH usable alleles was also rejected -- E2 is vacuous"
    )
    assert vals["OKS_OVERLAP"] == "60"


def test_new_reject_reasons_abort_through_the_existing_assert(r_toolchain, tmp_path):
    """E3. Both new reason codes flow into the PRE-EXISTING
    ``assert_declared_ld_authoritative()`` and abort the region.

    This is the ``test_ld_declared_authoritative.py:278-286`` convention being
    honoured: the reason codes are kept as data precisely so a fifth (here:
    a fifth and a sixth) cannot be added to the loader without someone deciding
    whether it stops. It does -- the assert stops on ``declared_rejected``
    regardless of reason and therefore needed NO edit.

    NEGATIVE CONTROL (in-test): the identical rejection with
    ``authoritative = FALSE`` runs past the assert at rc 0 -- so both new reasons
    are provably INERT off the allow-list, which is the EUR/TRANS containment.
    """
    rscript, env = r_toolchain
    reached = "REACHED_PAST_THE_ASSERT"
    for reason in ("alleles_unavailable_panel", "alleles_unavailable_sumstats"):
        body = (
            f'res <- list(R = NULL, source = "/p/d.rds",\n'
            f'            status = "ld_declared_rejected;{reason}",\n'
            f'            declared_rejected = TRUE, reject_reason = "{reason}",\n'
            f'            declared = "/p/d.rds", overlap = 0, coverage = 0)\n'
            f'assert_declared_ld_authoritative(res, TRUE, "m2_region_00040__sub14",'
            f' "AFR", MIN_LD_OVERLAP, MIN_LD_COVERAGE, MIN_LD_MIN_USE)\n'
            f'cat("{reached}\\n")\n'
        )
        proc = _run_r_allow_fail(rscript, env, tmp_path, body, name=f"tE3_{reason}.R")
        assert proc.returncode != 0, (
            f"reason={reason} did NOT abort the region (rc=0); a written JSON at "
            f"rc 0 is a job Snakemake marks DONE\n{proc.stdout}"
        )
        assert reached not in proc.stdout
        assert "LD_DECLARED_REJECTED:" in proc.stderr, proc.stderr
        assert f"reason={reason}" in proc.stderr, proc.stderr

        # NEGATIVE CONTROL -- inert off the allow-list
        body_off = body.replace(
            'assert_declared_ld_authoritative(res, TRUE,',
            'assert_declared_ld_authoritative(res, FALSE,')
        proc_off = _run_r_allow_fail(rscript, env, tmp_path, body_off,
                                     name=f"tE3_off_{reason}.R")
        assert proc_off.returncode == 0, (
            f"reason={reason} aborted a region OFF the allow-list -- EUR/TRANS "
            f"containment is broken\n{proc_off.stderr}"
        )
        assert reached in proc_off.stdout


def test_new_rejections_are_inert_under_authoritative_false(r_toolchain, tmp_path):
    """E4. At the LOADER level (not just the assert): a caller with
    ``allele_aware = TRUE`` but ``authoritative = FALSE`` can never produce a
    ``declared_rejected`` result. The candidate is skipped and the legacy
    ``ld_missing`` shape is returned -- no abort is reachable.

    NEGATIVE CONTROL (in-test): the same fixture with ``authoritative = TRUE``
    DOES set ``declared_rejected``.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    noalleles = ld_dir / "AFR_aou" / "na.rds"
    body = (
        'sub <- mk_subset(n = 60L)\n'
        'pan <- mk_panel_frame(n = 60L)\n'
        f'save_panel("{noalleles}", pan[, c("SNP_ID", "CHR", "POS")], r12 = 0.9)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = FALSE,'
        f' allele_aware = TRUE, ld_file = "{noalleles}"), "OFF")\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{noalleles}"), "ON")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tE4.R")
    assert vals["OFF_REJECTED"] == "FALSE", vals["OFF_REJECTED"]
    assert vals["OFF_REASON"] == "<NULL>", vals["OFF_REASON"]
    # the unverifiable candidate is SKIPPED, so the loader falls out of the loop
    # into the legacy `ld_missing` shape -- no rejection, no abort
    assert vals["OFF_STATUS"] == "ld_missing", vals["OFF_STATUS"]
    assert vals["OFF_RNULL"] == "TRUE", vals["OFF_RNULL"]
    # NEGATIVE CONTROL
    assert vals["ON_REJECTED"] == "TRUE", (
        "the same fixture did not reject under authoritative = TRUE -- E4 is "
        "vacuous"
    )


# ==========================================================================
# F -- orientation alignment: the one way this fix could ITSELF mis-sign
# ==========================================================================
def test_allele_orient_is_aligned_to_subset_idx_on_every_return(
    r_toolchain, tmp_path
):
    """F. ``allele_orient`` must be the SAME LENGTH and the SAME ORDER as
    ``subset_idx`` on every return that carries one. Letting them fall out of
    step is the single way this fix could produce a sign error of its own.

    Three returns are covered:
      F1 the GATE-PASS return (overlap >= 50 and coverage >= 0.5),
      F2 the ``best_partial`` return (overlap in [10, 50)),
      F3 the ``nrow(R) != length(keep_idx)`` branch -- which under
         ``allele_aware`` is only reachable with a variants-less (bare matrix)
         panel, and THAT is a structured rejection, so the branch cannot return
         a ``subset_idx`` without an orient at all. Asserted as such.

    The order claim is checked by INTERLEAVING flipped and exact rows: an
    implementation that reordered ``keep_idx`` without reordering ``orient``
    would emit the orient vector of the unsorted construction.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    gate = ld_dir / "AFR_aou" / "gate.rds"
    part = ld_dir / "AFR_aou" / "part.rds"
    bare = ld_dir / "AFR_aou" / "bare.rds"
    body = (
        # 60 rows, ODD indices swapped in the panel -> orient alternates -1/+1
        'n <- 60L\n'
        'sub <- mk_subset(n = n, ref = "A", alt = "G")\n'
        'pan <- mk_panel_frame(n = n, ref = "A", alt = "G")\n'
        'odd <- which(seq_len(n) %% 2L == 1L)\n'
        'pan$REF[odd] <- "G"; pan$ALT[odd] <- "A"\n'
        f'save_panel("{gate}", pan, r12 = 0.9)\n'
        # partial: only 20 of the 60 positions are in the panel -> overlap 20,
        # coverage 20/60 = 0.33 < 0.5 -> best_partial
        'pan_p <- pan[1:20, ]\n'
        f'save_panel("{part}", pan_p, r12 = 0.9)\n'
        f'save_panel("{bare}", NULL, r12 = 0.9)\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{gate}"), "GATE")\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{part}"), "PART")\n'
        f'emit(load_ld_matrix("{ld_dir}", "AFR", "r", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{bare}"), "BARE")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tF.R")

    # F1 -- gate pass
    assert vals["GATE_STATUS"].startswith("ld_loaded;overlap_ok"), vals["GATE_STATUS"]
    assert vals["GATE_ORIENT_LEN"] == vals["GATE_SUBSETIDX_LEN"] == "60"
    orient = vals["GATE_ORIENT"].split(",")
    idx = [int(i) for i in vals["GATE_SUBSETIDX"].split(",")]
    assert idx == sorted(idx), "subset_idx is not ascending"
    # position k of orient must describe subset row idx[k]
    for k, row in enumerate(idx):
        expected = "-1" if row % 2 == 1 else "1"
        assert orient[k] == expected, (
            f"orient[{k}] = {orient[k]} for subset row {row}; the orientation "
            "vector is OUT OF STEP with subset_idx -- this fix would itself "
            "produce a sign error"
        )
    assert vals["GATE_CNT_flipped"] == "30" and vals["GATE_CNT_exact"] == "30"

    # F2 -- best_partial
    assert vals["PART_STATUS"].startswith("ld_loaded;partial_overlap"), vals["PART_STATUS"]
    assert vals["PART_ORIENT_LEN"] == vals["PART_SUBSETIDX_LEN"] == "20"

    # F3 -- the variants-less panel cannot return a subset_idx at all
    assert vals["BARE_REJECTED"] == "TRUE", vals["BARE_REJECTED"]
    assert vals["BARE_REASON"] == "alleles_unavailable_panel", vals["BARE_REASON"]
    assert vals["BARE_SUBSETIDX"] == "<NULL>", (
        "a variants-less panel returned a subset_idx under allele_aware -- the "
        "nrow(R) != length(keep_idx) branch is reachable without an orient "
        "vector and the length guard in run_susie_rss.R can be bypassed"
    )
