"""FINDING J — the per-region receipt could not tell an early exit from a regression.

`m3-04c-BLAST-RADIUS.md` finding **J**: ``finemap.smk``'s per-region receipt
reads ``ld_matrix`` / ``ld_file_declared`` off the region JSON, but
``run_susie_rss.R``'s ``no_variants`` and ``too_many_variants`` early exits emit
**neither key**. ``d.get()`` on an absent key returns ``None``, so the receipt
printed ``ld_matrix None ld_file_declared None`` -- character for character what
a genuine declare-vs-read regression prints. ``HLA_6p21`` and ``PYHIN1_1q23``
are NAMED ``too_many_variants`` regions, so the ambiguity was firing on real
inputs today.

**The fix is entirely on the non-frozen half of the pair.**
``src/legacy/region_analysis/scripts/run_susie_rss.R`` is RE-FROZEN at
``dc4bbd2`` and is NOT touched by this module or by the change it tests; the
freeze is re-asserted MID-TEST.

WHAT IS LOAD-BEARING HERE
-------------------------
The early-exit token (``NA_EARLY_EXIT`` / ``early_exit:<status>``) and the
regression token (``ABSENT`` / ``ALARM_LD_FIELDS_MISSING``) must be **UNEQUAL**.
An implementation that renders both as ``MISSING`` fails here. That inequality
IS finding J.

NC-J1 and NC-J2 are **permanent and in-suite**, not one-off reverts: the
``6b427bc`` receipt is extracted by the SAME extractor and driven over the SAME
fixtures, so "the old receipt genuinely could not distinguish them" is
reproduced on every run rather than argued.

DISCIPLINE
----------
The receipt is EXTRACTED from the live ``finemap.smk`` (comment-stripped
``shell:`` body), never hand-copied -- the ``260805-w7u`` body-walk rule. A
hand-copy would keep passing while the shipped line rotted.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FINEMAP_SMK = PROJECT_ROOT / "src" / "snakemake" / "rules" / "finemap.smk"
RUN_SUSIE_R = (
    PROJECT_ROOT / "src" / "legacy" / "region_analysis" / "scripts" / "run_susie_rss.R"
)

#: The commit this task started from -- the permanent differential substrate.
PRE_CHANGE_REF = "6b427bc"

#: ``run_susie_rss.R``'s re-freeze pin (260805-o7o; the unfreeze is SPENT).
FROZEN_R_REV = "dc4bbd2"

#: The tokens finding J's closure introduces. They must never be equal.
EARLY_EXIT_TOKEN = "NA_EARLY_EXIT"
REGRESSION_TOKEN = "ABSENT"
ALARM_VERDICT = "ALARM_LD_FIELDS_MISSING"
PRESENT_VERDICT = "ld_fields_present"

#: Every LD field the frozen early-exit writers do NOT emit.
LD_FIELDS_ABSENT_FROM_EARLY_EXITS = (
    "ld_matrix",
    "ld_file_declared",
    "ld_authoritative",
    "ld_allele_exact",
)


# ==========================================================================
# Extraction -- from the LIVE source, never a hand-copy
# ==========================================================================
def _rule_block(text: str, rule_name: str) -> str:
    """COPIED from tests/m3/test_ld_read_path.py (not imported: that module is
    pre-existing and must stay unedited)."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(rf"^rule\s+{re.escape(rule_name)}\s*:", line):
            start = i
            break
    assert start is not None, f"rule {rule_name} not found"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^(rule|checkpoint)\s+\w+\s*:", lines[j]):
            end = j
            break
    return "\n".join(lines[start:end])


def _directive_block(rule_text: str, directive: str) -> str:
    """COPIED from tests/m3/test_ld_read_path.py."""
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
    """The ``shell:`` body with ``#`` COMMENT LINES REMOVED.

    Prose about the receipt -- and this change added a lot of it -- must never
    satisfy an assertion about the command that is actually executed.
    """
    block = _directive_block(_rule_block(smk_text, rule_name), "shell")
    return "\n".join(
        line for line in block.splitlines() if not line.lstrip().startswith("#")
    )


def _receipt_program(smk_text: str) -> str:
    """The python source inside the single ``{PYTHON_BIN} -c "..."`` receipt.

    NON-VACUITY GUARD: exactly ONE such line must exist and the extracted
    program must be non-empty and contain ``json.load``. A failed extraction
    that returns ``""`` would make every assertion in this module test nothing.
    """
    shell = _shell_command_block(smk_text)
    lines = [ln for ln in shell.splitlines() if "{PYTHON_BIN} -c" in ln]
    assert len(lines) == 1, (
        f"expected exactly one '{{PYTHON_BIN}} -c' receipt line in the "
        f"comment-stripped shell body, found {len(lines)}"
    )
    line = lines[0]
    start = line.index('-c "') + len('-c "')
    end = line.rindex('"')
    prog = line[start:end]
    assert prog.strip(), "the extracted receipt program is EMPTY"
    assert "json.load" in prog, (
        "the extracted receipt program does not call json.load -- the "
        f"extraction is wrong, not the receipt:\n{prog[:200]}"
    )
    return prog


def _git_show(spec: str) -> str:
    return subprocess.run(
        ["git", "show", spec],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _run_receipt(program: str, payload_path: Path, region: str, ancestry: str) -> str:
    """Execute the extracted receipt exactly as the rule does."""
    res = subprocess.run(
        [sys.executable, "-c", program, str(payload_path), region, ancestry],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, (
        f"receipt exited {res.returncode}\nstdout: {res.stdout}\nstderr: {res.stderr}"
    )
    return res.stdout.strip()


# ==========================================================================
# Fixtures -- built from the EXACT key list the FROZEN early-exit writers emit
# ==========================================================================
#: The ``result <- list(...)`` payload of run_susie_rss.R's early exits, keys in
#: source order. Pinned against the frozen file by
#: ``test_the_frozen_early_exits_still_emit_no_ld_field``.
def _early_exit_payload(status: str, notes: str) -> dict:
    return {
        "trait": "bmi",
        "ancestry": "AFR",
        "method": "susie",
        "region_id": "m2_region_00143",
        "chrom": "6",
        "start": 25000000,
        "end": 35000000,
        "sumstats": "data/processed/harmonized/bmi.AFR.tsv.gz",
        "ld_dir": "data/processed/ld_reference",
        "status": status,
        "notes": notes,
        "variant_catalog_path": "data/processed/variant_catalog/HLA_6p21.AFR.tsv",
        "variant_catalog_attempted": True,
        "variant_catalog_used": True,
        "variant_catalog_fallback": False,
    }


def _no_variants_payload() -> dict:
    return _early_exit_payload("no_variants", "No variants within region bounds")


def _too_many_variants_payload() -> dict:
    return _early_exit_payload(
        "too_many_variants", "n_variants=363412 exceeds SUSIE_MAX_VARIANTS=50000"
    )


def _regressed_payload() -> dict:
    """A REAL fit status whose LD fields have gone missing -- the regression.

    Deliberately IDENTICAL to the ``no_variants`` payload in every key the
    ``6b427bc`` receipt actually reads, and different only in ``status`` and
    ``notes`` (which that receipt never printed). That is what makes NC-J1 a
    measurement of finding J rather than a story about it.
    """
    p = _early_exit_payload("success", "fit completed")
    return p


def _full_success_payload() -> dict:
    """Every field the receipt reads, present -- no token may fire."""
    return {
        "trait": "bmi",
        "ancestry": "AFR",
        "method": "susie",
        "region_id": "m2_region_00040__sub14",
        "status": "success",
        "d3b_ld_z_consistency_s": 0.0123,
        "ld_source_mismatch_flag": False,
        "ld_matrix": "data/processed/ld_reference/AFR_aou/m2_region_00040__sub14.rds",
        "ld_file_declared": (
            "data/processed/ld_reference/AFR_aou/m2_region_00040__sub14.rds"
        ),
        "ld_authoritative": True,
        "variant_catalog_path": "data/processed/variant_catalog/SH2B3_12q24.AFR.tsv",
        "variant_catalog_attempted": True,
        "variant_catalog_used": True,
        "variant_catalog_fallback": False,
        "ld_overlap_zero_fallback": False,
        "ld_allele_aware": True,
        "ld_allele_exact": 136,
        "ld_allele_flipped": 46,
        "ld_allele_dropped_palindromic": 8,
        "ld_allele_dropped_mismatch": 5,
        "ld_allele_dropped_ambiguous": 1,
        "ld_allele_dropped_unusable": 4,
        "ld_allele_catalog_join": "allele_key",
    }


def _write(tmp_path: Path, name: str, payload: dict) -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(payload, indent=2))
    return p


# ==========================================================================
# The premise -- pinned against the FROZEN source
# ==========================================================================
def _brace_block(text: str, anchor: str) -> str:
    """``anchor`` plus its balanced ``{...}`` body (R source).

    COPIED from tests/m3/test_ld_read_path.py rather than imported.
    """
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
                return text[idx: k + 1]
    raise AssertionError(f"unbalanced braces after {anchor!r}")


def _paren_block(text: str, anchor: str) -> str:
    """``anchor`` plus its balanced ``(...)`` body (R source). COPIED likewise."""
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
                return text[idx: k + 1]
    raise AssertionError(f"unbalanced parens after {anchor!r}")


EARLY_EXIT_ANCHORS = (
    "if (nrow(subset) == 0)",
    "if (nrow(subset) > SUSIE_MAX_VARIANTS)",
)


@pytest.mark.parametrize("anchor", EARLY_EXIT_ANCHORS)
def test_the_frozen_early_exits_still_emit_no_ld_field(anchor):
    """THE RECEIPT'S PREMISE, pinned against the FROZEN source.

    If a future unfreeze teaches the early exits to emit ``ld_matrix``, this
    test tells you the receipt's premise moved -- rather than the receipt
    quietly starting to report ``NA_EARLY_EXIT`` beside a real path.
    """
    src = RUN_SUSIE_R.read_text()
    assert src.count(anchor) == 1, (
        f"anchor {anchor!r} occurs {src.count(anchor)} times in the frozen "
        "source; the brace-walk could be matching the wrong block (or nothing)"
    )
    block = _brace_block(src, anchor)
    assert "result <- list(" in block, f"no result list inside {anchor!r}"
    payload = _paren_block(block, "result <- list(")
    assert "status =" in payload
    for field in LD_FIELDS_ABSENT_FROM_EARLY_EXITS:
        assert field not in payload, (
            f"{anchor!r} now emits {field!r} -- finding J's premise has moved "
            "and the receipt's NA_EARLY_EXIT token would be misleading"
        )
    # the frozen file is READ here, never written
    _assert_r_freeze_clean()


def _assert_r_freeze_clean() -> None:
    res = subprocess.run(
        ["git", "diff", "--exit-code", FROZEN_R_REV, "--",
         "src/legacy/region_analysis/scripts/run_susie_rss.R"],
        cwd=PROJECT_ROOT, capture_output=True, text=True,
    )
    assert res.returncode == 0, (
        f"run_susie_rss.R has drifted off its re-freeze pin {FROZEN_R_REV}:\n"
        f"{res.stdout[:2000]}"
    )


def test_run_susie_rss_r_is_still_frozen_at_its_pin():
    _assert_r_freeze_clean()


# ==========================================================================
# THE LOAD-BEARING ASSERTION -- the two tokens are UNEQUAL
# ==========================================================================
def test_the_early_exit_token_and_the_alarm_token_are_not_equal():
    assert EARLY_EXIT_TOKEN != REGRESSION_TOKEN
    prog = _receipt_program(FINEMAP_SMK.read_text())
    assert EARLY_EXIT_TOKEN in prog
    assert REGRESSION_TOKEN in prog
    assert ALARM_VERDICT in prog
    assert PRESENT_VERDICT in prog


@pytest.mark.parametrize(
    "name,payload,status",
    [
        ("no_variants", _no_variants_payload(), "no_variants"),
        ("too_many_variants", _too_many_variants_payload(), "too_many_variants"),
    ],
)
def test_an_early_exit_renders_the_early_exit_token_and_verdict(
    tmp_path, name, payload, status
):
    prog = _receipt_program(FINEMAP_SMK.read_text())
    out = _run_receipt(prog, _write(tmp_path, f"{name}.json", payload), "HLA_6p21", "AFR")

    assert f"ld_receipt_verdict early_exit:{status}" in out, out
    assert f"ld_matrix {EARLY_EXIT_TOKEN}" in out, out
    assert f"ld_file_declared {EARLY_EXIT_TOKEN}" in out, out
    assert f"ld_authoritative {EARLY_EXIT_TOKEN}" in out, out
    # A BARE None can never render for an absent key again.
    assert "ld_matrix None" not in out, out
    assert "ld_file_declared None" not in out, out
    # ...and the REGRESSION token must not appear on an early exit.
    assert REGRESSION_TOKEN not in out, out
    assert ALARM_VERDICT not in out, out


def test_a_regressed_json_renders_the_alarm_token_and_verdict(tmp_path):
    prog = _receipt_program(FINEMAP_SMK.read_text())
    out = _run_receipt(
        prog, _write(tmp_path, "regressed.json", _regressed_payload()), "SH2B3_12q24", "AFR"
    )

    assert f"ld_receipt_verdict {ALARM_VERDICT}" in out, out
    assert f"ld_matrix {REGRESSION_TOKEN}" in out, out
    assert f"ld_file_declared {REGRESSION_TOKEN}" in out, out
    assert EARLY_EXIT_TOKEN not in out, out
    assert "early_exit:" not in out, out


def test_a_full_success_json_fires_no_token_at_all(tmp_path):
    """NO FALSE ALARM. The real path is printed verbatim and the verdict is
    ``ld_fields_present``; neither substitution token appears anywhere."""
    payload = _full_success_payload()
    prog = _receipt_program(FINEMAP_SMK.read_text())
    out = _run_receipt(
        prog, _write(tmp_path, "success.json", payload), "SH2B3_12q24", "AFR"
    )

    assert f"ld_receipt_verdict {PRESENT_VERDICT}" in out, out
    assert f"ld_matrix {payload['ld_matrix']}" in out, out
    assert EARLY_EXIT_TOKEN not in out, out
    assert REGRESSION_TOKEN not in out, out
    assert ALARM_VERDICT not in out, out
    for key in ("ld_allele_exact", "ld_allele_flipped", "ld_allele_catalog_join"):
        assert f"{key} {payload[key]}" in out, (key, out)


def test_the_three_cases_are_mutually_distinguishable(tmp_path):
    """The whole of finding J, stated as an inequality over whole outputs."""
    prog = _receipt_program(FINEMAP_SMK.read_text())
    outs = {
        name: _run_receipt(prog, _write(tmp_path, f"{name}.json", payload), "HLA_6p21", "AFR")
        for name, payload in (
            ("no_variants", _no_variants_payload()),
            ("too_many_variants", _too_many_variants_payload()),
            ("regressed", _regressed_payload()),
        )
    }
    assert len(set(outs.values())) == 3, (
        "the new receipt renders two or more of "
        "(no_variants, too_many_variants, regressed) IDENTICALLY:\n"
        + "\n".join(f"{k}: {v}" for k, v in outs.items())
    )


# ==========================================================================
# NC-J1 / NC-J2 -- PERMANENT AND IN-SUITE
# ==========================================================================
def test_nc_j1_the_pre_change_receipt_cannot_distinguish_them(tmp_path):
    """NC-J1 -- finding J REPRODUCED, permanently, rather than argued.

    The ``6b427bc`` receipt, extracted by the SAME extractor and driven over the
    SAME three fixtures, produces ONE output for all three: an early exit and a
    real declare-vs-read regression are literally indistinguishable.
    """
    old_prog = _receipt_program(_git_show(f"{PRE_CHANGE_REF}:src/snakemake/rules/finemap.smk"))
    new_prog = _receipt_program(FINEMAP_SMK.read_text())

    fixtures = {
        "no_variants": _no_variants_payload(),
        "too_many_variants": _too_many_variants_payload(),
        "regressed": _regressed_payload(),
    }
    paths = {n: _write(tmp_path, f"{n}.json", p) for n, p in fixtures.items()}

    old_outs = {n: _run_receipt(old_prog, p, "HLA_6p21", "AFR") for n, p in paths.items()}
    new_outs = {n: _run_receipt(new_prog, p, "HLA_6p21", "AFR") for n, p in paths.items()}

    for name, out in old_outs.items():
        assert "ld_matrix None" in out, (name, out)
        assert "ld_file_declared None" in out, (name, out)

    assert len(set(old_outs.values())) == 1, (
        "the pre-change receipt was expected to be BLIND to the difference; it "
        "produced more than one output -- the fixtures differ in a field it "
        f"reads, so NC-J1 is not measuring finding J:\n{old_outs}"
    )
    assert len(set(new_outs.values())) == 3, (
        f"the new receipt does not distinguish all three:\n{new_outs}"
    )


def test_nc_j2_the_receipt_program_actually_changed():
    """NC-J2. A no-op edit must not be able to pass NC-J1 by accident."""
    old_prog = _receipt_program(_git_show(f"{PRE_CHANGE_REF}:src/snakemake/rules/finemap.smk"))
    new_prog = _receipt_program(FINEMAP_SMK.read_text())
    assert new_prog != old_prog, (
        "the extracted receipt program is byte-identical to "
        f"{PRE_CHANGE_REF}'s -- the extractor is reading the wrong thing, or "
        "nothing was actually changed"
    )


# ==========================================================================
# K's decoder ring -- the $0, non-frozen PARTIAL mitigation (K stays DEFERRED)
# ==========================================================================
@pytest.mark.parametrize(
    "vcf,ozf,expected",
    [
        (None, None, "key_absent"),                              # all 1,957 legacy JSONs pre-date it
        (False, False, "none"),
        (True, True, "path2_ld_overlap_zero_NO_NUMERIC_CAUSE"),  # THE PHANTOM FLIP
        (True, False, "path1_variant_catalog_empty_subset"),     # the key's ORIGINAL meaning
    ],
)
def test_the_variant_catalog_fallback_cause_token_explains_the_phantom(
    tmp_path, vcf, ozf, expected
):
    """K is DEFERRED, not closed. This does NOT restore the key's additive
    contract -- only the frozen emission site can -- but it makes the phantom
    SELF-EXPLAINING at the place a reader diffing JSONs is actually looking.
    """
    payload = _full_success_payload()
    if vcf is None:
        payload.pop("variant_catalog_fallback")
        payload.pop("ld_overlap_zero_fallback")
    else:
        payload["variant_catalog_fallback"] = vcf
        payload["ld_overlap_zero_fallback"] = ozf

    prog = _receipt_program(FINEMAP_SMK.read_text())
    out = _run_receipt(
        prog, _write(tmp_path, "cause.json", payload), "SH2B3_12q24", "AFR"
    )
    assert f"variant_catalog_fallback_cause {expected}" in out, out


# ==========================================================================
# Pre-existing constraints on the shell -- asserted HERE too, so a future edit
# to this receipt line trips in the module that owns it
# ==========================================================================
def test_the_receipt_still_reads_every_field_the_pre_existing_suites_pin():
    stripped = _shell_command_block(FINEMAP_SMK.read_text())
    assert stripped.count("--ld-allele-aware {params.ld_allele_aware}") == 1
    for key in (
        "ld_allele_exact", "ld_allele_flipped", "ld_allele_dropped_palindromic",
        "ld_allele_dropped_mismatch", "ld_allele_dropped_ambiguous",
        "ld_allele_dropped_unusable", "ld_allele_catalog_join",
        "d3b_ld_z_consistency_s", "ld_source_mismatch_flag", "ld_matrix",
        "ld_file_declared", "ld_authoritative", "variant_catalog_fallback",
        "ld_overlap_zero_fallback", "ld_allele_aware",
    ):
        assert f"d.get('{key}')" in stripped, key


def test_no_new_python_bin_line_was_introduced_before_the_receipt():
    """``test_ld_read_path_ancestry_gate.py::_rscript_argv`` cuts the argv at
    the FIRST ``{PYTHON_BIN}`` line after ``Rscript``. A second one anywhere
    between them would silently truncate the argv-delta comparison."""
    shell = _shell_command_block(FINEMAP_SMK.read_text())
    assert shell.count("{PYTHON_BIN}") == 1, (
        f"{shell.count('{PYTHON_BIN}')} '{{PYTHON_BIN}}' occurrences in the "
        "comment-stripped shell body; expected exactly 1"
    )
    lines = shell.splitlines()
    rscript = next(i for i, ln in enumerate(lines) if ln.strip().startswith("Rscript "))
    receipt = next(i for i, ln in enumerate(lines) if "{PYTHON_BIN}" in ln)
    assert receipt > rscript
    assert "--output {output.json}" in "\n".join(lines[rscript:receipt]), (
        "the Rscript argv no longer reaches --output before the receipt line"
    )
