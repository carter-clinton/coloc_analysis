"""tests/m3/test_ld_read_path.py -- m3-04c Task 1b (Layer B).

THE ACCEPTANCE TEST FOR ``DEC-2026-08-05-m3-ld-read-path``.

BLOCKER-1 (m3-04b-BLAST-RADIUS.md): ``run_finemap`` DECLARES
``input.ld_matrix`` (via ``resolve_ld_path``) but its ``shell:`` block never
passes it. ``run_susie_rss.R`` REBUILT its own path as
``file.path(ld_dir, ancestry, region_id + ".rds")`` -- where ``ancestry`` is
``AFR`` and never ``AFR_aou`` -- so the AoU panel was UNREACHABLE and the fit
fell silently to an identity matrix. A declared ``input:`` absent from the
rule's ``shell:`` is a DAG DECLARATION ONLY.

The locked remedy threads the declared artifact into the R script behind a new
``--ld-file`` and puts it FIRST in the loader's candidate list, making
``resolve_ld_path`` the single source of truth. The ``--ld-dir`` reconstruction
survives strictly as the back-compat fallback.

THE DECISION'S OWN ACCEPTANCE BAR: prove ``resolved == what-the-script-opens``.
**A green DAG is NOT evidence.** Hence two halves:

    STATIC half  -- T2.1, T2.2, T2.7, T2.8: pin the wiring and the flags.
    BEHAVIOURAL  -- T2.3, T2.4, T2.5, T2.6: RUN the REAL R loader and observe
                    which file it actually opens.

NO-SKIP RULE (inherited from must_have A6 / test_stitch_subregions_to_rds.py):
``_require_m3_r_toolchain()`` ERRORS (never skips) when the m3-r-ld marker env
is present. ``/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/Rscript``
exists on the NCSU node, so T2.3-T2.6 genuinely RUN there -- a skip means the
harness was mis-wired, which the m3-04c acceptance criteria treat as a FAILURE.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

# Make sibling test modules importable (tests/m3 on sys.path) so we can reuse the
# stitch test's R-toolchain discovery + loader-prefix extractor.
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from test_stitch_subregions_to_rds import (  # noqa: E402
    R_SUBPROCESS_TIMEOUT_S,
    _loader_functions_only,
    _require_m3_r_toolchain,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FINEMAP_SMK = PROJECT_ROOT / "src" / "snakemake" / "rules" / "finemap.smk"
SUSIE_R = PROJECT_ROOT / "src" / "legacy" / "region_analysis" / "scripts" / "run_susie_rss.R"


# --------------------------------------------------------------------------
# Source-slicing helpers (STATIC half)
# --------------------------------------------------------------------------
def _rule_block(text: str, rule_name: str) -> str:
    """Return the source of one Snakemake rule, from ``rule <name>:`` up to the
    next column-0 ``rule ``/``checkpoint `` (or EOF)."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(rf"^rule\s+{re.escape(rule_name)}\s*:", line):
            start = i
            break
    assert start is not None, f"rule {rule_name} not found in {FINEMAP_SMK}"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^(rule|checkpoint)\s+\w+\s*:", lines[j]):
            end = j
            break
    return "\n".join(lines[start:end])


def _directive_block(rule_text: str, directive: str) -> str:
    """Return one directive's body inside a rule block (e.g. ``shell``,
    ``params``, ``input``): from the ``<directive>:`` line to the next
    same-or-lesser-indented directive line."""
    lines = rule_text.splitlines()
    start = None
    indent = None
    for i, line in enumerate(lines):
        if re.match(rf"^(\s*){re.escape(directive)}\s*:\s*$", line):
            start = i
            indent = len(line) - len(line.lstrip())
            break
    assert start is not None, f"directive {directive}: not found in rule block"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        line = lines[j]
        if not line.strip():
            continue
        cur = len(line) - len(line.lstrip())
        if cur <= indent and re.match(r"^\s*\w+\s*:", line):
            end = j
            break
    return "\n".join(lines[start:end])


def _shell_command_block(smk_text: str, rule_name: str = "run_finemap") -> str:
    """The rule's ``shell:`` body with ``#`` COMMENT LINES REMOVED.

    Deliberately stricter than the raw directive text: prose describing
    ``--ld-file`` must not be able to satisfy an assertion about the command
    that is actually executed. BLOCKER-1 was precisely a case where the
    documentation was right and the invocation was not.
    """
    block = _directive_block(_rule_block(smk_text, rule_name), "shell")
    return "\n".join(
        line for line in block.splitlines() if not line.lstrip().startswith("#")
    )


def _brace_block(text: str, anchor: str) -> str:
    """Return ``anchor`` plus its balanced ``{...}`` body (R source)."""
    idx = text.find(anchor)
    assert idx != -1, f"anchor not found: {anchor!r}"
    open_idx = text.index("{", idx)
    depth = 0
    for k in range(open_idx, len(text)):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return text[idx:k + 1]
    raise AssertionError(f"unbalanced braces after {anchor!r}")


def _paren_block(text: str, anchor: str) -> str:
    """Return ``anchor`` plus its balanced ``(...)`` body (R source)."""
    idx = text.find(anchor)
    assert idx != -1, f"anchor not found: {anchor!r}"
    open_idx = text.index("(", idx)
    depth = 0
    for k in range(open_idx, len(text)):
        if text[k] == "(":
            depth += 1
        elif text[k] == ")":
            depth -= 1
            if depth == 0:
                return text[idx:k + 1]
    raise AssertionError(f"unbalanced parens after {anchor!r}")


def _success_result_block(susie_src: str) -> str:
    """The SUCCESS ``result <- list(...)`` -- the one carrying
    ``status = "success"``. The no_variants / too_many_variants early-exit
    blocks share the same anchor text, so select by content."""
    blocks = []
    pos = 0
    while True:
        idx = susie_src.find("result <- list(", pos)
        if idx == -1:
            break
        blk = _paren_block(susie_src[idx:], "result <- list(")
        blocks.append(blk)
        pos = idx + len(blk)
    hits = [b for b in blocks if 'status = "success"' in b]
    assert len(hits) == 1, (
        f"expected exactly one success result list, found {len(hits)} "
        f"among {len(blocks)} result<-list() blocks"
    )
    return hits[0]


# --------------------------------------------------------------------------
# R subprocess harness (BEHAVIOURAL half)
# --------------------------------------------------------------------------
@pytest.fixture(scope="session")
def r_toolchain() -> tuple[Path, dict]:
    return _require_m3_r_toolchain()


# Loaded via `source()` of the function-definition PREFIX only (cut at
# "option_list <-"), so no top-level argparse/main fires. MIN_LD_* are set from
# config/susie_policy.yaml in production, which is past the cut -- so they are
# pinned permissively here: this module tests WHICH FILE IS OPENED, not the
# acceptance thresholds (those are test_finemap_loader_contract.py's job).
_R_PREAMBLE = r'''
suppressPackageStartupMessages(library(Matrix))
suppressWarnings(suppressMessages(source("__LOADER_FUNCS__")))
MIN_LD_OVERLAP <- 1L
MIN_LD_COVERAGE <- 0.0
MIN_LD_MIN_USE <- 1L

N_VAR <- 5L
IDS <- paste0("rs", seq_len(N_VAR))
POSNS <- 53809247L + seq_len(N_VAR)

make_panel <- function(path) {
  R <- diag(N_VAR)
  R[1, 2] <- 0.4
  R[2, 1] <- 0.4
  variants <- data.frame(SNP_ID = IDS, CHR = rep("16", N_VAR), POS = POSNS,
                         stringsAsFactors = FALSE)
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  saveRDS(list(R = R, variants = variants, status = "ld_loaded"), path)
  invisible(path)
}

mk_subset <- function() {
  data.frame(SNP_ID = IDS, CHR = rep("16", N_VAR), POS = POSNS,
             stringsAsFactors = FALSE)
}

emit <- function(res, tag) {
  cat(sprintf("%s_SOURCE=%s\n", tag,
              if (is.null(res$source)) "<NULL>" else res$source))
  cat(sprintf("%s_RNULL=%s\n", tag, is.null(res$R)))
  cat(sprintf("%s_STATUS=%s\n", tag,
              if (is.null(res$status)) "<NULL>" else res$status))
  cat(sprintf("%s_NROW=%s\n", tag,
              if (is.null(res$R)) "<NULL>" else nrow(res$R)))
}
'''


def _run_r(rscript: Path, env: dict, tmp_path: Path, body: str,
           name: str = "probe.R") -> dict:
    """Source the REAL loader prefix, run ``body``, return the emitted KEY=VALUE
    map. Raises on a non-zero R exit so an "unused argument (ld_file = ...)"
    error surfaces as a FAILURE, not as a silently empty result."""
    loader_funcs = _loader_functions_only(tmp_path)
    script = tmp_path / name
    script.write_text(
        _R_PREAMBLE.replace("__LOADER_FUNCS__", str(loader_funcs)) + "\n" + body
    )
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


# ==========================================================================
# T2.1 / T2.2 -- STATIC: the wiring
# ==========================================================================
def test_run_finemap_shell_passes_the_declared_ld_matrix():
    """T2.1. The ``shell:`` block passes the DECLARED artifact, verbatim.

    This is the one assertion that would have caught BLOCKER-1 at m3-W3-T2:
    ``input.ld_matrix`` existed and resolved correctly, but nothing passed it to
    the consumer, so the resolver's answer was inert. The VALUE token must be
    exactly ``{input.ld_matrix}`` -- not ``{params.ld_dir}``, not a rebuilt
    string. Anything else re-opens the declare-vs-read split.
    """
    shell_block = _shell_command_block(FINEMAP_SMK.read_text())
    assert re.search(r"--ld-file\s+\{input\.ld_matrix\}", shell_block), (
        "run_finemap's shell: must pass the DECLARED LD artifact as "
        "--ld-file {input.ld_matrix}; a declared input absent from shell: is a "
        f"DAG declaration ONLY (BLOCKER-1). shell block was:\n{shell_block}"
    )
    m = re.search(r"--ld-file\s+(\S+)", shell_block)
    assert m is not None
    value_token = m.group(1)
    assert value_token == "{input.ld_matrix}", (
        f"--ld-file must receive the resolver's artifact, got {value_token!r}"
    )
    assert "{params.ld_dir}" != value_token
    # exactly once, repo-wide, so there is one read path and not two
    assert FINEMAP_SMK.read_text().count("--ld-file {input.ld_matrix}") == 1


def test_ld_file_option_is_declared():
    """T2.2. ``run_susie_rss.R`` declares ``--ld-file`` and ``load_ld_matrix``
    accepts an ``ld_file`` argument."""
    src = SUSIE_R.read_text()
    option_list = _paren_block(src, "option_list <- list(")
    assert 'make_option("--ld-file"' in option_list, (
        "run_susie_rss.R's option_list must declare --ld-file"
    )
    sig = re.search(r"load_ld_matrix\s*<-\s*function\s*\(([^)]*)\)", src)
    assert sig is not None, "load_ld_matrix definition not found"
    params = [p.split("=")[0].strip() for p in sig.group(1).split(",")]
    assert "ld_file" in params, f"load_ld_matrix signature lacks ld_file: {sig.group(1)!r}"
    # ld_file LAST with a default => positional callers are unaffected
    assert params[-1] == "ld_file", (
        f"ld_file must be the LAST formal so existing positional callers are "
        f"unaffected; got {params!r}"
    )
    assert re.search(r"ld_file\s*=\s*NULL", sig.group(1)), (
        "ld_file must default to NULL (back-compat with --ld-dir-only callers)"
    )
    # the SOLE call site threads the parsed option through
    assert re.search(r"load_ld_matrix\([^\n]*ld_file\s*=\s*opt\$`ld-file`", src), (
        "the sole call site must pass ld_file = opt$`ld-file`"
    )


# ==========================================================================
# T2.3-T2.6 -- BEHAVIOURAL: what the REAL loader actually opens
# ==========================================================================
def test_loader_opens_the_declared_file_not_the_reconstructed_path(r_toolchain, tmp_path):
    """T2.3. THE ACCEPTANCE TEST: ``resolved == what-the-script-opens``.

    The declared artifact lives at ``ld_reference/AFR_aou/m2_region_00067.rds``
    -- a path the ``{ld_dir}/{ancestry}/{region_id}.rds`` reconstruction can
    NEVER reach, because ``ancestry`` is ``AFR`` and the curated region id is
    ``FTO_16q12``. ``ld_reference/AFR/`` EXISTS but is EMPTY, so the ld_dir
    guard passes and the reconstruction genuinely looks and finds nothing.
    A green DAG proves none of this; opening the file does.
    """
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    (ld_dir / "AFR").mkdir(parents=True)  # EXISTS, EMPTY: reconstruction has somewhere to look
    declared = ld_dir / "AFR_aou" / "m2_region_00067.rds"
    body = (
        f'declared <- "{declared}"\n'
        'make_panel(declared)\n'
        f'res <- load_ld_matrix("{ld_dir}", "AFR", "FTO_16q12", mk_subset(), ld_file = declared)\n'
        'emit(res, "D")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="t23.R")
    assert vals["D_SOURCE"] == str(declared), (
        f"the loader opened {vals['D_SOURCE']!r}, not the DECLARED "
        f"{str(declared)!r} -- resolved != opened"
    )
    assert vals["D_RNULL"] == "FALSE", "declared panel loaded but R is NULL"
    assert vals["D_NROW"] == "5"


def test_absent_ld_file_still_reconstructs_from_ld_dir(r_toolchain, tmp_path):
    """T2.4. The ``--ld-dir`` reconstruction survives as the fallback.

    No caller that omits ``--ld-file`` may break (1kg/HGDP/UKBB tails, the
    stitch/loader-contract tests, and any ad-hoc invocation)."""
    rscript, env = r_toolchain
    ld_dir = tmp_path / "ld_reference"
    recon = ld_dir / "AFR" / "FTO_16q12.rds"
    body = (
        f'recon <- "{recon}"\n'
        'make_panel(recon)\n'
        f'res <- load_ld_matrix("{ld_dir}", "AFR", "FTO_16q12", mk_subset(), ld_file = NULL)\n'
        'emit(res, "F")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="t24.R")
    assert vals["F_SOURCE"] == str(recon), (
        f"ld_dir reconstruction regressed: opened {vals['F_SOURCE']!r}"
    )
    assert vals["F_RNULL"] == "FALSE"


def test_ld_file_works_when_ld_dir_is_absent(r_toolchain, tmp_path):
    """T2.5. THE TRAP at the loader's first guard.

    The pre-change guard was
    ``if (is.null(ld_dir) || ld_dir == "" || !file.exists(ld_dir)) return(...)``
    -- so a NAIVE ``--ld-file`` addition still bails HERE whenever ld_dir is
    absent, i.e. the fix does nothing in exactly the case it exists for. All
    three absent-ld_dir shapes (NULL, "", nonexistent) must still load the
    declared file."""
    rscript, env = r_toolchain
    declared = tmp_path / "panels" / "AFR_aou" / "m2_region_00067.rds"
    missing_dir = tmp_path / "no_such_ld_dir"
    body = (
        f'declared <- "{declared}"\n'
        'make_panel(declared)\n'
        'emit(load_ld_matrix(NULL, "AFR", "FTO_16q12", mk_subset(), ld_file = declared), "NULLDIR")\n'
        f'emit(load_ld_matrix("{missing_dir}", "AFR", "FTO_16q12", mk_subset(), ld_file = declared), "MISSDIR")\n'
        'emit(load_ld_matrix("", "AFR", "FTO_16q12", mk_subset(), ld_file = declared), "EMPTYDIR")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="t25.R")
    for tag in ("NULLDIR", "MISSDIR", "EMPTYDIR"):
        assert vals[f"{tag}_RNULL"] == "FALSE", (
            f"[{tag}] a valid --ld-file was supplied but the loader returned NULL R "
            f"(status={vals[f'{tag}_STATUS']!r}) -- the ld_dir guard still bails"
        )
        assert vals[f"{tag}_STATUS"] != "ld_dir_missing", (
            f"[{tag}] the ld_dir guard fired despite a readable --ld-file"
        )
        assert vals[f"{tag}_SOURCE"] == str(declared), (
            f"[{tag}] opened {vals[f'{tag}_SOURCE']!r}, not the declared file"
        )


def test_both_absent_returns_the_byte_identical_legacy_status(r_toolchain, tmp_path):
    """T2.6. The legacy contract is PRESERVED, not merely bypassed.

    With neither a usable ld_dir nor an ld_file, the loader must still return
    ``R = NULL`` and the character-for-character ``"ld_dir_missing"`` status
    that downstream provenance/reporting already keys on."""
    rscript, env = r_toolchain
    missing_dir = tmp_path / "no_such_ld_dir"
    unreadable = tmp_path / "no_such_panel.rds"
    body = (
        f'emit(load_ld_matrix("{missing_dir}", "AFR", "FTO_16q12", mk_subset(), ld_file = NULL), "BOTH")\n'
        f'emit(load_ld_matrix(NULL, "AFR", "FTO_16q12", mk_subset(), ld_file = NULL), "NN")\n'
        f'emit(load_ld_matrix("{missing_dir}", "AFR", "FTO_16q12", mk_subset(), ld_file = "{unreadable}"), "GHOST")\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="t26.R")
    for tag in ("BOTH", "NN", "GHOST"):
        assert vals[f"{tag}_RNULL"] == "TRUE", f"[{tag}] expected R = NULL"
        assert vals[f"{tag}_SOURCE"] == "<NULL>", f"[{tag}] expected source = NULL"
        assert vals[f"{tag}_STATUS"] == "ld_dir_missing", (
            f"[{tag}] the legacy status string moved: {vals[f'{tag}_STATUS']!r} "
            "!= 'ld_dir_missing'"
        )


# ==========================================================================
# T2.7 / T2.8 -- STATIC: HIGH-2 observability + the per-region receipt
# ==========================================================================
def test_path2_ld_overlap_zero_fallback_is_observable_and_read():
    """T2.7 (HIGH-2). The ``ld_overlap == 0`` revert stops being invisible.

    Path 1 (the AFR empty-filtered-subset revert) sets BOTH
    ``used_variant_catalog <- FALSE`` and ``variant_catalog_fallback <- TRUE``.
    Path 2 (the ``ld_overlap == 0`` retry) set only the former -- no
    distinguishing signal at all, and no consumer read either flag. Threading a
    NEW LD source with different varid provenance RAISES the probability of
    ``ld_overlap == 0``, so the blind spot had to close before the fire.

    HONEST LIMITATION: exercising Path 2 end-to-end requires the WHOLE script
    (sumstats + regions csv + policy + variant list + a real region), so this
    family is pinned at SOURCE level. That is the same documented rationale the
    project already uses for Snakemake-directive assertions
    (test_finemap_loader_contract.py::test_estimate_s_guard_present). The
    science behaviour is deliberately NOT asserted here because it deliberately
    does not change: Path 2 still reverts to subset_base and still retries once.
    """
    src = SUSIE_R.read_text()

    # initialized alongside the Path-1 flag
    assert "variant_catalog_fallback <- FALSE" in src
    assert "ld_overlap_zero_fallback <- FALSE" in src, (
        "ld_overlap_zero_fallback must be initialized FALSE alongside "
        "variant_catalog_fallback"
    )
    init_gap = src.index("ld_overlap_zero_fallback <- FALSE") - src.index(
        "variant_catalog_fallback <- FALSE")
    assert 0 < init_gap < 120, (
        "the two fallback flags must be initialized together (parity), "
        f"but they are {init_gap} chars apart"
    )

    # the Path-2 branch sets BOTH
    branch = _brace_block(src, "if (ld_overlap == 0 && used_variant_catalog && attempt == 1)")
    assert "variant_catalog_fallback <- TRUE" in branch, (
        "Path 2 must set variant_catalog_fallback (parity with Path 1); today "
        f"the branch is:\n{branch}"
    )
    assert "ld_overlap_zero_fallback <- TRUE" in branch, (
        "Path 2 must set ld_overlap_zero_fallback so it is DISTINGUISHABLE "
        f"from the Path-1 revert; today the branch is:\n{branch}"
    )
    # science behaviour unchanged: still one retry against subset_base
    assert "subset <- copy(subset_base)" in branch
    assert "attempt <- attempt + 1" in branch

    # both surface in the success JSON
    success = _success_result_block(src)
    assert "variant_catalog_fallback = variant_catalog_fallback" in success
    assert "ld_overlap_zero_fallback = ld_overlap_zero_fallback" in success, (
        "ld_overlap_zero_fallback must reach the output JSON"
    )

    # ...and something actually READS them (write-only flags are not observability)
    smk_shell = _shell_command_block(FINEMAP_SMK.read_text())
    assert "ld_overlap_zero_fallback" in smk_shell, (
        "the per-region estimate_s log must READ ld_overlap_zero_fallback; a "
        "flag nothing consumes is not observability"
    )
    assert "variant_catalog_fallback" in smk_shell


def test_declared_and_opened_paths_are_both_recorded_in_the_output_json():
    """T2.8. Every region's JSON carries the DECLARED path beside the OPENED one.

    ``ld_matrix = ld_source`` already records what was opened. Adding
    ``ld_file_declared = opt$`ld-file``` makes ``resolved == opened`` a
    per-region checkable fact AFTER the fire, not just a pre-fire assertion
    (plan verification item 11). Additive JSON keys are safe:
    summarize_finemap_results.py reads with .get() against a fixed FIELDNAMES
    list."""
    src = SUSIE_R.read_text()
    success = _success_result_block(src)
    assert "ld_matrix = ld_source" in success, "the OPENED path must stay recorded"
    assert re.search(r"ld_file_declared\s*=\s*opt\$`ld-file`", success), (
        "the success result must record ld_file_declared (the DECLARED path) "
        "beside ld_matrix (the OPENED path)"
    )
    # the log one-liner surfaces the pair per region
    smk_shell = _shell_command_block(FINEMAP_SMK.read_text())
    assert "ld_file_declared" in smk_shell and "'ld_matrix'" in smk_shell, (
        "the estimate_s log must print BOTH ld_matrix and ld_file_declared so "
        "each region's log is a resolved==opened receipt"
    )
