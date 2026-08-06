"""FINDING K-1 -- ``variant_catalog_fallback`` is a PRE-EXISTING key and must
keep its ONE legacy meaning.

`m3-04c-BLAST-RADIUS.md` row **K** / `deferred-items.md` **K-1**:
``variant_catalog_fallback`` predates m3-04c. Every legacy region JSON on this
node records it, and it means exactly one thing: *the Path-1 AFR
variant-catalog empty-subset revert fired* (``run_susie_rss.R:904-917``).

m3-04c's Path-2 "parity" change made the ``ld_overlap == 0`` retry ALSO set that
key, with no numeric cause. A pre-existing key that silently acquires a second
meaning forces every future automated before/after JSON comparison to
special-case it, and produces a ``false -> true`` flip a reader WILL chase.
`quick-260806-b77` mitigated that with a runtime decoder ring; it did not close
it. `quick-260806-pd3` closes it by deleting the single Path-2 assignment under
**AUTH-K1-UNFREEZE** (now SPENT) and **AUTH-K1-TEST**.

WHAT IS LOAD-BEARING HERE
-------------------------
Two claims, both mechanical rather than argued:

1. **The key is assigned at exactly ONE site**, and that site is Path 1.
2. **NOTHING ELSE MOVED.** The unfreeze was scoped to one deleted line plus a
   comment reword, so the Path-2 block's *code-only* lines must equal
   ``PRE_K1_REF``'s minus exactly that line, and the five MUST-NOT-MOVE regions
   must be byte-identical to ``PRE_K1_REF``. That is the mechanical form of
   "no number moves".

WHY THERE IS NO WHOLE-FILE PIN
------------------------------
``git diff <FIXED-SHA> HEAD -- file == ""`` is green once and red forever after
(``[[feedback_fixed_sha_whole_file_pin_is_a_timebomb]]``). Every containment
assertion below is **SYMBOL-scoped** -- a named brace block, a named
``result <- list(...)`` payload, or diff lines mentioning a named symbol -- so a
future AUTHORIZED unfreeze produces a message naming WHICH region moved instead
of an undifferentiated wall of diff.

NEGATIVE CONTROLS ARE PERMANENT, NOT ONE-OFF
--------------------------------------------
NC-K1 walks ``PRE_K1_REF``'s revision and asserts the extractor DOES see the
line there; NC-K2 splices the line back into an **in-memory** copy and asserts
the predicate goes RED, then asserts the working tree was never written.
Neither reverts a file on disk, so neither can be defeated by the ``.pyc``
bytecode cache (``[[feedback_negative_control_defeated_by_bytecode_cache]]``).

NO-SKIP BY CONSTRUCTION: this module is pure source text + ``git``. It runs no
R, no Snakemake and no toolchain fixture, so it cannot degrade into a skip and
present that as evidence.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# Make sibling test modules importable (tests/m3 on sys.path) -- the established
# pattern in this directory. The walkers are IMPORTED, not re-implemented, so
# the extractor under test is the SAME one the authorized assertion in
# tests/m3/test_ld_read_path.py uses.
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from test_ld_read_path import (  # noqa: E402
    _brace_block,
    _paren_block,
    _shell_command_block,
    _success_result_block,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUSIE_R_REL = "src/legacy/region_analysis/scripts/run_susie_rss.R"
SUSIE_R = PROJECT_ROOT / SUSIE_R_REL
FINEMAP_SMK = PROJECT_ROOT / "src" / "snakemake" / "rules" / "finemap.smk"

#: The revision that carried the m3-04c Path-2 overload. A DIFFERENTIAL
#: SUBSTRATE, not a freeze pin: it MUST stay dc4bbd2 forever, even after the
#: re-pin of run_susie_rss.R's freeze at pd3's commit 1. Bumping it would
#: silently destroy NC-K1 and the containment proofs, which is precisely the
#: mistake hard rule 4 of the pd3 plan exists to prevent.
PRE_K1_REF = "dc4bbd2"

#: The legacy key's ONE assignment. Exactly one occurrence, inside Path 1.
LEGACY_KEY_ASSIGNMENT = "variant_catalog_fallback <- TRUE"

PATH1_ANCHOR = 'ancestry_upper == "AFR" &&'
PATH2_ANCHOR = "if (ld_overlap == 0 && used_variant_catalog && attempt == 1)"
NO_VARIANTS_ANCHOR = "if (nrow(subset) == 0)"
TOO_MANY_ANCHOR = "if (nrow(subset) > SUSIE_MAX_VARIANTS)"


# ==========================================================================
# Helpers -- source text and git only
# ==========================================================================
def _git_show(spec: str) -> str:
    return subprocess.run(
        ["git", "show", spec],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _pre_k1_source() -> str:
    return _git_show(f"{PRE_K1_REF}:{SUSIE_R_REL}")


def _code_lines(block: str) -> list[str]:
    """The block's CODE-only lines, stripped: blanks and ``#`` comments dropped.

    The K-1 edit deletes one code line AND rewords a comment. Comparing raw
    lines would therefore conflate the authorized comment reword with a code
    change, which is the whole thing these assertions exist to separate.
    """
    out = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        out.append(stripped)
    return out


def _init_pair_region(src: str) -> str:
    """The two-line initializer region: ``variant_catalog_fallback <- FALSE``
    and the ``ld_overlap_zero_fallback <- FALSE`` line immediately after it."""
    lines = src.splitlines()
    hits = [i for i, ln in enumerate(lines)
            if ln.strip() == "variant_catalog_fallback <- FALSE"]
    assert len(hits) == 1, (
        f"expected exactly one variant_catalog_fallback <- FALSE initializer, "
        f"found {len(hits)}"
    )
    i = hits[0]
    region = "\n".join(lines[i:i + 2])
    assert "ld_overlap_zero_fallback <- FALSE" in region, (
        "the two fallback flags are no longer initialized on adjacent lines; "
        f"the region extracted was:\n{region}"
    )
    return region


def _early_exit_payload(src: str, anchor: str) -> str:
    block = _brace_block(src, anchor)
    assert "result <- list(" in block, f"no result list inside {anchor!r}"
    return _paren_block(block, "result <- list(")


#: THE K-1 PREDICATE, factored out so NC-K2 can drive it with a source in which
#: the deleted line HAS been spliced back -- proving it can fail.
def _assert_path2_does_not_set_the_legacy_key(text: str) -> None:
    branch = _brace_block(text, PATH2_ANCHOR)
    assert LEGACY_KEY_ASSIGNMENT not in branch, (
        "Path 2 must NOT set the legacy variant_catalog_fallback key (K-1): it "
        "is a pre-existing key whose meaning is the Path-1 AFR empty-subset "
        f"revert. Today the branch is:\n{branch}"
    )


# ==========================================================================
# (a) THE CLAIM: one assignment site, and it is Path 1
# ==========================================================================
def test_the_legacy_key_is_assigned_at_exactly_one_site():
    """``variant_catalog_fallback <- TRUE`` occurs ONCE, inside Path 1 only.

    NON-VACUITY: both anchors are asserted unique, both extracted blocks are
    asserted non-empty, and each is asserted to contain a SECOND expected
    marker -- so a brace-walk that silently landed on the wrong block, or on
    nothing, cannot make this test pass by absence.
    """
    src = SUSIE_R.read_text()

    assert src.count(LEGACY_KEY_ASSIGNMENT) == 1, (
        f"{LEGACY_KEY_ASSIGNMENT!r} occurs {src.count(LEGACY_KEY_ASSIGNMENT)} "
        "times; K-1 requires exactly 1 (the Path-1 AFR empty-subset revert)"
    )
    assert src.count(PATH1_ANCHOR) == 1, "the Path-1 anchor is not unique"
    assert src.count(PATH2_ANCHOR) == 1, "the Path-2 anchor is not unique"

    path1 = _brace_block(src, PATH1_ANCHOR)
    path2 = _brace_block(src, PATH2_ANCHOR)

    # non-vacuity: neither walk returned an empty or wrong block
    assert "subset <- copy(subset_base)" in path1, (
        "the Path-1 block does not contain its own revert -- the brace-walk "
        f"landed somewhere else:\n{path1}"
    )
    assert "subset <- copy(subset_base)" in path2, (
        "the Path-2 block does not contain its own revert -- the brace-walk "
        f"landed somewhere else:\n{path2}"
    )

    assert LEGACY_KEY_ASSIGNMENT in path1, (
        "Path 1 must STILL set variant_catalog_fallback -- that is the key's "
        f"restored and only meaning:\n{path1}"
    )
    _assert_path2_does_not_set_the_legacy_key(src)


# ==========================================================================
# (b) NC-K1 -- PERMANENT, DIFFERENTIAL. Proves the walker can see the line.
# ==========================================================================
def test_nc_k1_the_same_walk_finds_the_line_at_the_pre_k1_revision():
    """NC-K1. The identical extraction over ``PRE_K1_REF`` MUST find the line.

    Without this, "``variant_catalog_fallback <- TRUE`` is not in the Path-2
    block" is indistinguishable from "the extractor is reading the wrong block".
    PERMANENT and in-suite: it reads a past revision with ``git show`` and never
    writes the working tree, so it needs no revert and cannot be defeated by the
    ``.pyc`` bytecode cache.
    """
    old = _pre_k1_source()

    assert old.count(LEGACY_KEY_ASSIGNMENT) == 2, (
        f"at {PRE_K1_REF} the legacy key was assigned TWICE (Path 1 and the "
        f"m3-04c Path-2 overload); found {old.count(LEGACY_KEY_ASSIGNMENT)}. "
        "Either the extractor is reading the wrong revision, or the historical "
        "substrate is not what K-1 says it is"
    )
    old_path2 = _brace_block(old, PATH2_ANCHOR)
    assert LEGACY_KEY_ASSIGNMENT in old_path2, (
        f"the Path-2 block at {PRE_K1_REF} does NOT contain "
        f"{LEGACY_KEY_ASSIGNMENT!r}: the extractor is reading the wrong block, "
        "or nothing changed"
    )


# ==========================================================================
# (c) NC-K2 -- PERMANENT, IN-MEMORY. Proves the predicate CAN fail.
# ==========================================================================
def test_nc_k2_splicing_the_line_back_in_memory_turns_the_predicate_red():
    """NC-K2. Re-insert the deleted line into an IN-MEMORY copy of TODAY's
    source; the K-1 predicate must raise.

    ``.pyc``-SAFE BY DESIGN: no file is written and no module is re-imported, so
    ``importlib``'s ``(mtime_seconds, size)`` bytecode validation cannot serve a
    stale body of the predicate
    (``[[feedback_negative_control_defeated_by_bytecode_cache]]``). The final
    assertion proves the control left the working tree untouched.
    """
    src = SUSIE_R.read_text()

    # green on the real thing
    _assert_path2_does_not_set_the_legacy_key(src)

    marker = "    ld_overlap_zero_fallback <- TRUE\n"
    assert src.count(marker) == 1, (
        f"the splice marker {marker!r} is not uniquely present; the control "
        "would be perturbing the wrong place (or nothing)"
    )
    spliced = src.replace(marker, f"    {LEGACY_KEY_ASSIGNMENT}\n{marker}")
    assert spliced != src, "the in-memory splice changed nothing"

    with pytest.raises(AssertionError) as excinfo:
        _assert_path2_does_not_set_the_legacy_key(spliced)
    assert "K-1" in str(excinfo.value)

    # ⚠ the control is IN-MEMORY ONLY: the frozen file was never written
    assert SUSIE_R.read_text() == src, (
        "NC-K2 leaked onto the working tree -- the on-disk frozen file changed"
    )


# ==========================================================================
# (d) THE TIGHTEST PIN: the Path-2 block lost one code line and gained none
# ==========================================================================
def test_the_path2_block_lost_exactly_one_code_line_and_gained_none():
    """AUTH-K1-UNFREEZE's scope, mechanically: ONE code line deleted, none added,
    none reordered. This is the mechanical form of "no number moves" -- the
    Path-2 revert still reverts to ``subset_base``, still retries once, and
    still records itself.

    ⚠ MAINTENANCE CONTRACT. This is the tightest pin in the module. If a FUTURE
    AUTHORIZED unfreeze legitimately changes this block, **UPDATE THE EXPECTED
    DELTA -- do not delete the test.** Deleting it would remove the only
    mechanical proof that a scoped unfreeze stayed scoped.
    """
    new_lines = _code_lines(_brace_block(SUSIE_R.read_text(), PATH2_ANCHOR))
    old_lines = _code_lines(_brace_block(_pre_k1_source(), PATH2_ANCHOR))

    # non-vacuity: the block is real, not an empty walk
    assert len(new_lines) >= 5, (
        f"the Path-2 block has only {len(new_lines)} code lines; the brace-walk "
        f"is not returning the real block:\n{new_lines}"
    )
    for survivor in (
        "subset <- copy(subset_base)",
        "used_variant_catalog <- FALSE",
        "ld_overlap_zero_fallback <- TRUE",
        "attempt <- attempt + 1",
    ):
        assert survivor in new_lines, (
            f"{survivor!r} left the Path-2 block -- that is OUTSIDE "
            "AUTH-K1-UNFREEZE's scope (science behaviour must be unchanged)"
        )

    assert set(old_lines) - set(new_lines) == {LEGACY_KEY_ASSIGNMENT}, (
        "the Path-2 block lost something other than the one authorized line:\n"
        f"removed = {sorted(set(old_lines) - set(new_lines))}"
    )
    assert set(new_lines) - set(old_lines) == set(), (
        "the Path-2 block GAINED a code line; AUTH-K1-UNFREEZE authorized a "
        f"deletion only:\nadded = {sorted(set(new_lines) - set(old_lines))}"
    )
    # ORDERED, so a reordering that preserves the set still fails
    assert [ln for ln in old_lines if ln != LEGACY_KEY_ASSIGNMENT] == new_lines, (
        "the Path-2 block's code lines were REORDERED, not merely trimmed:\n"
        f"expected: {[ln for ln in old_lines if ln != LEGACY_KEY_ASSIGNMENT]}\n"
        f"actual:   {new_lines}"
    )


# ==========================================================================
# (e) THE FIVE MUST-NOT-MOVE REGIONS, byte-identical, each NAMED
# ==========================================================================
def _named_region(src: str, name: str) -> str:
    if name == "init_pair":
        return _init_pair_region(src)
    if name == "path1_block":
        return _brace_block(src, PATH1_ANCHOR)
    if name == "no_variants_payload":
        return _early_exit_payload(src, NO_VARIANTS_ANCHOR)
    if name == "too_many_variants_payload":
        return _early_exit_payload(src, TOO_MANY_ANCHOR)
    if name == "success_payload":
        return _success_result_block(src)
    raise AssertionError(f"unknown region {name!r}")


MUST_NOT_MOVE_REGIONS = (
    "init_pair",
    "path1_block",
    "no_variants_payload",
    "too_many_variants_payload",
    "success_payload",
)


@pytest.mark.parametrize("region", MUST_NOT_MOVE_REGIONS)
def test_the_five_must_not_move_sites_are_byte_identical(region):
    """AUTH-K1-UNFREEZE named five regions that MUST NOT MOVE: the init pair
    (``:787-788``), the Path-1 mutation (``:904-917``), the two early-exit emits
    (``:936`` / ``:968``) and the success emit (``:1208``). Each is extracted by
    its OWN anchor from HEAD and from ``PRE_K1_REF`` and compared for BYTE
    equality -- so the failure message names WHICH region moved.

    ⚠ MAINTENANCE CONTRACT. If a future AUTHORIZED unfreeze legitimately moves
    one of these, **UPDATE THE NAMED REGION -- do not delete the test.**
    """
    new = _named_region(SUSIE_R.read_text(), region)
    old = _named_region(_pre_k1_source(), region)

    # non-vacuity: an empty extraction on both sides would compare equal
    assert new.strip(), f"the {region!r} extraction is EMPTY at HEAD"
    assert old.strip(), f"the {region!r} extraction is EMPTY at {PRE_K1_REF}"

    assert new == old, (
        f"MUST-NOT-MOVE region {region!r} is no longer byte-identical to "
        f"{PRE_K1_REF}. AUTH-K1-UNFREEZE authorized ONE deleted line inside the "
        f"Path-2 block and a comment reword above it -- nothing else.\n"
        f"--- {PRE_K1_REF} ---\n{old}\n--- HEAD ---\n{new}"
    )


# ==========================================================================
# (f) THE WHOLE-FILE CLAIM, in a form that is not a timebomb
# ==========================================================================
def test_the_symbol_scoped_diff_is_exactly_one_removed_line():
    """One removed CODE line naming the two fallback symbols, zero added.

    Restricted to lines mentioning ``variant_catalog_fallback`` or
    ``ld_overlap_zero_fallback``, so -- unlike a whole-file pin against a fixed
    SHA -- it survives a future unrelated authorized unfreeze and still fails on
    a re-introduction of the overload.

    ⚠ THE MARKER IS STRIPPED BEFORE THE COMMENT TEST. ``line.lstrip()`` on a raw
    diff line is ``"-    # ..."``, which does NOT start with ``#``; and K-1's
    reworded comment is guaranteed to mention the symbol. A naive filter would
    leak comment lines into the count and fail for the wrong reason.

    ⚠ THE DIFF IS ``PRE_K1_REF`` vs THE **WORKING TREE**, not vs ``HEAD``. Every
    other assertion in this module reads ``SUSIE_R.read_text()``, i.e. the file
    as shipped on disk; a ``PRE_K1_REF..HEAD`` form would assert about a
    different substrate than its siblings AND could not be green until the
    commit carrying the deletion existed -- an ordering trap the module's own
    non-vacuity guard caught. Once committed the two forms agree, because the
    freeze gate independently requires the working tree to be clean.
    """
    diff = subprocess.run(
        ["git", "diff", PRE_K1_REF, "--", SUSIE_R_REL],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True,
    ).stdout

    # NON-VACUITY: if the unrestricted diff were empty the filter proves nothing
    assert diff.strip(), (
        f"git diff {PRE_K1_REF} HEAD -- {SUSIE_R_REL} is EMPTY; K-1's deletion "
        "is not in the tree, so this assertion would be measuring nothing"
    )

    removed, added = [], []
    for line in diff.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if not (line.startswith("+") or line.startswith("-")):
            continue
        body = line[1:]                       # ⚠ STRIP THE MARKER FIRST
        if body.lstrip().startswith("#"):     # then, and only then, drop comments
            continue
        if ("variant_catalog_fallback" not in body
                and "ld_overlap_zero_fallback" not in body):
            continue
        (added if line[0] == "+" else removed).append(body.strip())

    assert removed == [LEGACY_KEY_ASSIGNMENT], (
        "the symbol-scoped diff removed something other than exactly the one "
        f"authorized line:\n{removed}"
    )
    assert added == [], (
        "the symbol-scoped diff ADDED a code line mentioning a fallback symbol; "
        f"AUTH-K1-UNFREEZE authorized a deletion only:\n{added}"
    )


# ==========================================================================
# (g) NOTHING BECAME INVISIBLE -- asserted, not argued
# ==========================================================================
def test_ld_overlap_zero_fallback_is_still_the_path2_discriminator():
    """K-1 removes the legacy key's Path-2 overload; it removes NO observability.

    ``ld_overlap_zero_fallback`` is still initialized ``FALSE``, still set
    ``TRUE`` by the Path-2 revert, still emitted in the success JSON, and still
    READ by the per-region receipt in ``finemap.smk``. A write-only flag is not
    observability, so the last leg is the load-bearing one.
    """
    src = SUSIE_R.read_text()

    assert src.count("ld_overlap_zero_fallback <- FALSE") == 1
    assert src.count("ld_overlap_zero_fallback <- TRUE") == 1

    branch = _brace_block(src, PATH2_ANCHOR)
    assert "ld_overlap_zero_fallback <- TRUE" in branch, (
        "the Path-2 revert no longer records itself AT ALL -- K-1 was supposed "
        f"to remove the legacy overload, not the discriminator:\n{branch}"
    )

    success = _success_result_block(src)
    assert "ld_overlap_zero_fallback = ld_overlap_zero_fallback" in success, (
        "ld_overlap_zero_fallback no longer reaches the output JSON"
    )
    assert "variant_catalog_fallback = variant_catalog_fallback" in success, (
        "variant_catalog_fallback no longer reaches the output JSON; K-1 "
        "narrows the key's MEANING, it does not stop emitting it"
    )

    smk_shell = _shell_command_block(FINEMAP_SMK.read_text())
    assert "ld_overlap_zero_fallback" in smk_shell, (
        "the per-region receipt must READ ld_overlap_zero_fallback; a flag "
        "nothing consumes is not observability"
    )
