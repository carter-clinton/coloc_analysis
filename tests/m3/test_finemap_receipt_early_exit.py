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
``src/legacy/region_analysis/scripts/run_susie_rss.R`` is **CODE-FROZEN** at
``bf04199`` and is NOT touched by this module or by the change it tests; the
freeze is re-asserted MID-TEST. (The pin was ``dc4bbd2`` until 2026-08-06, when
``quick-260806-pd3`` spent ``AUTH-K1-UNFREEZE`` on finding **K-1** -- one line
deleted from the Path-2 branch -- and re-pinned at ``bf04199``. That unfreeze is
SPENT; there is no open window on this file.)

``quick-260806-sr4`` RESCOPED that freeze from **bytes** to **CODE** under
``AUTH-SR4-RESCOPE``: comments, blank lines and trailing whitespace are now
deliberately FREE, and the gate below runs through
``source_freeze.assert_code_frozen`` instead of ``git diff --exit-code``. The
same session spent ``AUTH-SR4-K3`` on a COMMENT-ONLY correction (the K-3 census
figures at ``:1018-1019``) which did **NOT move the pin** -- that is the
acceptance demonstration for the rescope, and it is asserted permanently by
``test_source_freeze_pins.py::test_the_k3_comment_fix_did_not_move_the_code_pin``.
The pin itself is declared in exactly ONE place, ``R_CODE_REF``, and imported
here. Why a guard exists at all, and what it deliberately does NOT cover, is
``DEC-2026-08-06-sr4-freeze-scope``.

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

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from source_freeze import LANG_R, assert_code_frozen  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FINEMAP_SMK = PROJECT_ROOT / "src" / "snakemake" / "rules" / "finemap.smk"
SUSIE_R_REL = "src/legacy/region_analysis/scripts/run_susie_rss.R"
RUN_SUSIE_R = (
    PROJECT_ROOT / "src" / "legacy" / "region_analysis" / "scripts" / "run_susie_rss.R"
)

#: DIFFERENTIAL SUBSTRATE. The commit this task started from. It MUST NEVER be
#: re-pinned: NC-J1/NC-J2 extract the ``6b427bc`` receipt with the SAME extractor
#: and reproduce the ambiguity finding J closes. Bumping it in a re-pin sweep
#: would silently kill both controls.
PRE_CHANGE_REF = "6b427bc"

#: CODE PIN. ``run_susie_rss.R``'s freeze, IMPORTED rather than re-declared:
#: ``R_CODE_REF`` in ``test_source_freeze_pins.py`` is the ONLY place the R pin
#: is spelled, so a re-pinner who obeys "update exactly one constant per frozen
#: subject" cannot leave this gate red. ``quick-260806-sr4`` rescoped it from
#: BYTES to CODE under AUTH-SR4-RESCOPE: a comment-only edit no longer moves it
#: (the K-3 correction is the proof), a CODE edit still does.
#: See DEC-2026-08-06-sr4-freeze-scope.
from test_source_freeze_pins import R_CODE_REF as FROZEN_R_CODE_REV  # noqa: E402

#: ``finemap.smk`` BEFORE the K-1 decoder fix. A DIFFERENTIAL SUBSTRATE, not a
#: freeze pin: it MUST stay ``63453db`` forever. Never re-pin it. NC-K5 drives
#: the receipt program extracted from THIS revision over the post-K-1
#: ``(false, true)`` fixture and reproduces the incoherence the fix closes;
#: bumping it in a re-pin sweep would silently kill that control.
PRE_K1_SMK_REF = "63453db"

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
    """JOB A -- THE FREEZE GATE, rescoped from bytes to CODE by quick-260806-sr4.

    The ACTUAL side is the WORKING TREE, deliberately: this is called MID-TEST
    (``:341``/``:357``) to catch an uncommitted write, so a ``git show HEAD:``
    read here would go blind with nothing turning red.
    """
    assert_code_frozen(SUSIE_R_REL, FROZEN_R_CODE_REV, LANG_R)


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
# K's decoder ring -- K-1 CLOSED by quick-260806-pd3, and the decoder had to
# gain a FIFTH outcome to stay truthful after the closure
# ==========================================================================
#: DOCUMENTATION ONLY. The load-bearing set is RECOVERED from the live
#: ``finemap.smk`` by ``_recovered_cause_tokens()``; this literal survives only
#: so a reader can see the five without running the extractor, and is asserted
#: EQUAL to the recovered set. A hand-copy used as the subject would be a test
#: that agrees with itself -- the class this module's own docstring forbids.
CAUSE_TOKENS = (
    "key_absent",
    "none",
    "path2_ld_overlap_zero_RETRY",
    "path2_ld_overlap_zero_NO_NUMERIC_CAUSE",
    "path1_variant_catalog_empty_subset",
)


def _cause_expression(smk_text: str) -> str:
    """The ``cause=(...)`` sub-expression, sliced out of the LIVE receipt."""
    prog = _receipt_program(smk_text)
    start = prog.index("cause=(")
    end = prog.index(";", start)
    expr = prog[start:end]
    assert expr.strip(), "the cause= slice is EMPTY -- the extraction is wrong"
    return expr


def _recovered_cause_tokens(smk_text: str) -> set:
    """Every quoted token inside the live ``cause=(...)`` expression.

    ⚠ THE CHARACTER CLASS MUST ADMIT ``A-Z``. Two of the five tokens carry
    uppercase runs (``..._NO_NUMERIC_CAUSE``, ``..._RETRY``); a lowercase-only
    class silently recovers THREE, and the cheapest local repair -- relaxing the
    exactly-5 guard -- would drop precisely the two tokens the no-prefix
    property exists for, re-introducing the vacuity NC-K6 prevents.
    """
    recovered = set(re.findall(r"'([A-Za-z0-9_]+)'", _cause_expression(smk_text)))
    assert len(recovered) == 5, (
        f"expected exactly 5 cause tokens in the live receipt, recovered "
        f"{len(recovered)}: {sorted(recovered)}"
    )
    return recovered


def _assert_cause_is(out: str, expected: str) -> None:
    """Delimiter-aware match. ⚠ A plain ``in`` test cannot separate
    ``path2_ld_overlap_zero_RETRY`` from
    ``path2_ld_overlap_zero_NO_NUMERIC_CAUSE`` when the expected value is the
    shared prefix ``path2_ld_overlap_zero``. NC-K6 pins that this matters.
    """
    assert re.search(
        rf"variant_catalog_fallback_cause {re.escape(expected)}(\s|$)", out
    ), f"expected cause {expected!r} with a delimiter; got:\n{out}"


@pytest.mark.parametrize(
    "vcf,ozf,expected",
    [
        # MEASURED 2026-08-06: 687 of the 2,596 region JSONs under
        # results/legacy/region_analysis carry NO variant_catalog_fallback key.
        # (The old comment here claimed "all 1,957 legacy JSONs pre-date it",
        # which was FALSE -- the ones that carry it render `none`, below.)
        (None, None, "key_absent"),
        # 1,900 of the 1,909 legacy JSONs that DO carry the key render this.
        # (1,909 carry it + 687 key-absent = the 2,596 region JSONs. A wider
        # census reporting 1,944 also swept .planning/debug fits and
        # results_lsweep_*.bak siblings -- 35 non-region files.)
        (False, False, "none"),
        # NEW, and the reason K-1 forced a decoder change: after K-1 a real
        # Path-2 revert emits variant_catalog_fallback false + overlap_zero
        # true. The pre-K-1 decoder rendered that as `none` -- FALSE, because
        # Path 2 DID fire. NC-K5 reproduces that lie permanently.
        (False, True, "path2_ld_overlap_zero_RETRY"),
        # FORENSIC MARKER ONLY. Unreachable from any tree at or after bf04199;
        # its presence dates an artifact to the m3-04c window. 0 on this node.
        (True, True, "path2_ld_overlap_zero_NO_NUMERIC_CAUSE"),
        # the key's restored, and now ONLY, meaning. 9 real AFR JSONs measured.
        (True, False, "path1_variant_catalog_empty_subset"),
    ],
)
def test_the_variant_catalog_fallback_cause_token_explains_the_phantom(
    tmp_path, vcf, ozf, expected
):
    """K-1 is CLOSED (quick-260806-pd3). The decoder still renders the PAIR, and
    it had to gain a fifth outcome to keep telling the truth: the post-K-1
    Path-2 signature is (false, true), which the four-outcome decoder called
    ``none``.
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
    _assert_cause_is(out, expected)


def test_the_cause_tokens_are_distinct_and_none_is_a_prefix_of_another():
    """The tokens are RECOVERED from the live ``finemap.smk``, never trusted
    from the literal above -- so renaming one in the ``.smk`` turns this RED."""
    recovered = _recovered_cause_tokens(FINEMAP_SMK.read_text())
    assert set(CAUSE_TOKENS) == recovered, (
        "the documentation literal CAUSE_TOKENS no longer matches the tokens "
        f"actually shipped in finemap.smk.\nliteral:   {sorted(CAUSE_TOKENS)}\n"
        f"recovered: {sorted(recovered)}"
    )
    assert len(CAUSE_TOKENS) == len(set(CAUSE_TOKENS)), "duplicate cause token"
    for a in recovered:
        for b in recovered:
            if a == b:
                continue
            assert not a.startswith(b), (
                f"cause token {a!r} starts with {b!r}; a substring match on "
                f"{b!r} would also match {a!r} -- the prefix-collision trap"
            )


def test_nc_k5_the_pre_k1_decoder_called_a_real_path2_revert_none(tmp_path):
    """NC-K5 -- PERMANENT, DIFFERENTIAL. The decoder fix is LOAD-BEARING.

    The ``PRE_K1_SMK_REF`` receipt, extracted by the SAME extractor and driven
    over the SAME post-K-1 ``(false, true)`` fixture, renders ``none`` -- i.e. it
    reports that neither revert fired, on a payload where Path 2 DID fire. The
    live receipt renders ``path2_ld_overlap_zero_RETRY``. Reproducing the
    incoherence beats arguing it, needs no revert, and is ``.pyc``-safe.
    """
    payload = _full_success_payload()
    payload["variant_catalog_fallback"] = False
    payload["ld_overlap_zero_fallback"] = True
    path = _write(tmp_path, "post_k1_path2.json", payload)

    old_prog = _receipt_program(
        _git_show(f"{PRE_K1_SMK_REF}:src/snakemake/rules/finemap.smk")
    )
    new_prog = _receipt_program(FINEMAP_SMK.read_text())
    assert old_prog != new_prog, (
        f"the receipt is byte-identical to {PRE_K1_SMK_REF}'s -- the extractor "
        "is reading the wrong thing, or the decoder was never fixed"
    )

    old_out = _run_receipt(old_prog, path, "SH2B3_12q24", "AFR")
    new_out = _run_receipt(new_prog, path, "SH2B3_12q24", "AFR")

    _assert_cause_is(old_out, "none")
    _assert_cause_is(new_out, "path2_ld_overlap_zero_RETRY")


def test_nc_k6_a_naive_substring_match_cannot_separate_the_two_path2_tokens(
    tmp_path,
):
    """NC-K6 -- PERMANENT. The prefix trap is closed as a PROPERTY, not a claim.

    ``"variant_catalog_fallback_cause path2_ld_overlap_zero" in out`` matches
    BOTH path2 outputs; the delimiter-aware matcher separates them. If a future
    edit renamed a token so one became a prefix of the other, the sibling
    no-prefix test goes RED and this one documents why it matters.
    """
    prog = _receipt_program(FINEMAP_SMK.read_text())
    outs = {}
    for name, (vcf, ozf) in {
        "true_true": (True, True),
        "false_true": (False, True),
    }.items():
        payload = _full_success_payload()
        payload["variant_catalog_fallback"] = vcf
        payload["ld_overlap_zero_fallback"] = ozf
        outs[name] = _run_receipt(
            prog, _write(tmp_path, f"{name}.json", payload), "SH2B3_12q24", "AFR"
        )

    naive = "variant_catalog_fallback_cause path2_ld_overlap_zero"
    assert naive in outs["true_true"], outs["true_true"]
    assert naive in outs["false_true"], outs["false_true"]

    # ...and the delimiter-aware matcher does NOT conflate them
    _assert_cause_is(outs["true_true"], "path2_ld_overlap_zero_NO_NUMERIC_CAUSE")
    _assert_cause_is(outs["false_true"], "path2_ld_overlap_zero_RETRY")
    with pytest.raises(AssertionError):
        _assert_cause_is(outs["false_true"], "path2_ld_overlap_zero_NO_NUMERIC_CAUSE")
    with pytest.raises(AssertionError):
        _assert_cause_is(outs["true_true"], "path2_ld_overlap_zero_RETRY")


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
