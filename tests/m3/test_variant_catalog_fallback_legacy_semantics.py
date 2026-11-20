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
   "no number moves". Since the N1 re-indent, ``too_many_variants_payload`` is
   compared after stripping leading whitespace, and the symbol-scoped diff
   allows the one N1 emit line
   (DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation).

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

import difflib
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
N1_CAP_ANCHOR = "if (cap_after_ld && nrow(subset) > SUSIE_MAX_VARIANTS)"

#: The legacy key's emit into the JSON output (it writes the key, never sets it).
LEGACY_KEY_EMIT = "variant_catalog_fallback = variant_catalog_fallback"

#: Regions compared after stripping leading whitespace (the N1 re-indent).
INDENT_INSENSITIVE_REGIONS = frozenset({"too_many_variants_payload"})


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


def _lstrip_lines(text: str) -> list[str]:
    return [ln.lstrip(" \t") for ln in text.splitlines()]


def _assert_region_unmoved(region: str, new: str, old: str) -> None:
    if region in INDENT_INSENSITIVE_REGIONS:
        new_lines, old_lines = new.splitlines(), old.splitlines()
        assert len(new_lines) == len(old_lines), (
            f"MUST-NOT-MOVE region {region!r} has {len(new_lines)} lines, "
            f"{PRE_K1_REF} has {len(old_lines)}"
        )
        for i, (a, b) in enumerate(zip(_lstrip_lines(new), _lstrip_lines(old))):
            assert a == b, (
                f"MUST-NOT-MOVE region {region!r} differs from {PRE_K1_REF} at "
                f"line {i} beyond leading whitespace:\n"
                f"{PRE_K1_REF}: {old_lines[i]!r}\nHEAD: {new_lines[i]!r}"
            )
        return
    assert new == old, (
        f"MUST-NOT-MOVE region {region!r} is no longer byte-identical to "
        f"{PRE_K1_REF}. AUTH-K1-UNFREEZE authorized ONE deleted line inside the "
        f"Path-2 block and a comment reword above it -- nothing else.\n"
        f"--- {PRE_K1_REF} ---\n{old}\n--- HEAD ---\n{new}"
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

    ``too_many_variants_payload`` alone ignores leading whitespace (the N1
    re-indent; DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation).
    """
    new = _named_region(SUSIE_R.read_text(), region)
    old = _named_region(_pre_k1_source(), region)

    # non-vacuity: an empty extraction on both sides would compare equal
    assert new.strip(), f"the {region!r} extraction is EMPTY at HEAD"
    assert old.strip(), f"the {region!r} extraction is EMPTY at {PRE_K1_REF}"

    _assert_region_unmoved(region, new, old)


# ==========================================================================
# (f) THE WHOLE-FILE CLAIM, in a form that is not a timebomb
# ==========================================================================
def _symbol_scoped_changes(diff_text: str, cancel_reindent: bool = True):
    """(removed, added, n_reindented) over code lines naming a fallback symbol.
    With ``cancel_reindent``, a removed and an added line in the SAME hunk that
    differ only in leading whitespace cancel as a re-indentation."""
    hunks: list[tuple[list[str], list[str]]] = [([], [])]
    for line in diff_text.splitlines():
        if line.startswith("@@"):
            hunks.append(([], []))
            continue
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
        hunks[-1][1 if line[0] == "+" else 0].append(body)

    removed, added, n_reindented = [], [], 0
    for rem, add in hunks:
        used = [False] * len(add)
        for r in rem:
            j = None
            if cancel_reindent:
                j = next((k for k, a in enumerate(add) if not used[k] and a != r
                          and a.lstrip(" \t") == r.lstrip(" \t")), None)
            if j is None:
                removed.append(r.strip())
            else:
                used[j] = True
                n_reindented += 1
        added.extend(a.strip() for k, a in enumerate(add) if not used[k])
    return removed, added, n_reindented


def _assert_symbol_diff_is_k1_only(diff_text: str, new_src: str,
                                   old_src: str) -> None:
    removed, added, _ = _symbol_scoped_changes(diff_text)
    assert removed == [LEGACY_KEY_ASSIGNMENT], (
        "the symbol-scoped diff removed something other than exactly the one "
        f"authorized line:\n{removed}"
    )
    assert added == [LEGACY_KEY_EMIT], (
        "the symbol-scoped diff ADDED a code line other than the one N1 emit "
        "line (K-1; DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-"
        "unfreeze, DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-"
        f"indentation):\n{added}"
    )
    n1 = _code_lines(_early_exit_payload(new_src, N1_CAP_ANCHOR))
    assert n1.count(LEGACY_KEY_EMIT) == 1, (
        "the symbol-scoped diff's one allowed emit line is not in the N1 "
        f"flag-true payload (K-1):\n{n1}"
    )
    n_new = _code_lines(new_src).count(LEGACY_KEY_EMIT)
    n_old = _code_lines(old_src).count(LEGACY_KEY_EMIT)
    assert n_new == n_old + 1, (
        f"the symbol-scoped diff allows exactly one more {LEGACY_KEY_EMIT!r} "
        f"line than {PRE_K1_REF} (K-1); found {n_new} vs {n_old}"
    )


def _difflib_diff(old_src: str, new_src: str) -> str:
    return "".join(difflib.unified_diff(
        old_src.splitlines(True), new_src.splitlines(True), "a", "b"))


def test_the_symbol_scoped_diff_is_exactly_one_removed_line():
    """One removed CODE line naming the two fallback symbols; the only added one
    is the N1 emit line.

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

    Same-hunk re-indentations cancel, and the one N1 emit line is allowed
    (DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation).
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

    _assert_symbol_diff_is_k1_only(diff, SUSIE_R.read_text(), _pre_k1_source())


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


# ==========================================================================
# (h) 15.5c: indentation-insensitive pins and their in-memory controls
#     (DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation)
# ==========================================================================
_DIFF_MSG = "symbol-scoped diff"


def _git_diff_vs_pre_k1() -> str:
    return subprocess.run(
        ["git", "diff", PRE_K1_REF, "--", SUSIE_R_REL],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True,
    ).stdout


def _splice_region(src: str, name: str, perturb) -> tuple[str, str]:
    """Perturb region ``name`` inside an in-memory copy of ``src``; return the
    perturbed source and the region re-extracted from it."""
    region = _named_region(src, name)
    assert src.count(region) == 1, f"region {name!r} is not unique in the source"
    new_region = perturb(region)
    assert new_region != region, f"the perturbation of {name!r} changed nothing"
    perturbed = src.replace(region, new_region)
    assert perturbed != src
    return perturbed, _named_region(perturbed, name)


def _reindent_after_first(text: str, pad: str) -> str:
    lines = text.split("\n")
    return "\n".join([lines[0]] + [pad + ln for ln in lines[1:]])


def _replace_once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, f"marker {old!r} is not unique"
    return text.replace(old, new)


def test_the_too_many_extractor_picks_the_default_path_payload():
    src = SUSIE_R.read_text()
    assert src.count(TOO_MANY_ANCHOR) == 1
    assert src.count(N1_CAP_ANCHOR) == 1
    default = _named_region(src, "too_many_variants_payload")
    n1 = _early_exit_payload(src, N1_CAP_ANCHOR)
    assert "after LD restriction" not in default and "cap_stage" not in default
    assert "after LD restriction" in n1 and "cap_stage" in n1
    assert n1 != default


def test_the_real_payload_differs_from_pre_k1_only_in_indentation():
    head = _named_region(SUSIE_R.read_text(), "too_many_variants_payload")
    old = _named_region(_pre_k1_source(), "too_many_variants_payload")
    assert head != old, "the raw payloads are equal: the normalization is not exercised"
    _assert_region_unmoved("too_many_variants_payload", head, old)


def _swap_chrom_start(region: str) -> str:
    lines = region.split("\n")
    i = [k for k, ln in enumerate(lines) if ln.strip() == "chrom = reg$chr,"]
    j = [k for k, ln in enumerate(lines) if ln.strip() == "start = reg$start,"]
    assert len(i) == 1 and len(j) == 1
    lines[i[0]], lines[j[0]] = lines[j[0]], lines[i[0]]
    return "\n".join(lines)


def _drop_notes(region: str) -> str:
    lines = region.split("\n")
    keep = [ln for ln in lines if not ln.strip().startswith("notes = ")]
    assert len(keep) == len(lines) - 1
    return "\n".join(keep)


def _trailing_space(region: str) -> str:
    return _replace_once(region, "ancestry = opt$ancestry,\n",
                         "ancestry = opt$ancestry, \n")


NC_I1_PERTURBATIONS = {
    "value": lambda r: _replace_once(r, '"too_many_variants"', '"too_many_variantz"'),
    "dropped": _drop_notes,
    "reordered": _swap_chrom_start,
    "interior_ws": lambda r: _replace_once(r, "trait = opt$trait", "trait  = opt$trait"),
    "trailing_ws": _trailing_space,
}


@pytest.mark.parametrize("kind", list(NC_I1_PERTURBATIONS))
def test_nc_i1_a_payload_content_change_is_red(kind):
    src = SUSIE_R.read_text()
    old = _named_region(_pre_k1_source(), "too_many_variants_payload")
    _, new = _splice_region(src, "too_many_variants_payload",
                            NC_I1_PERTURBATIONS[kind])
    with pytest.raises(AssertionError) as excinfo:
        _assert_region_unmoved("too_many_variants_payload", new, old)
    assert "too_many_variants_payload" in str(excinfo.value)
    assert SUSIE_R.read_text() == src, "NC-I1 leaked onto the working tree"


def _mixed_indent(region: str) -> str:
    lines = region.split("\n")
    out = [lines[0]]
    for k, ln in enumerate(lines[1:], start=1):
        out.append("\t" + ln.lstrip(" \t") if k % 2 == 1 else "  " + ln)
    return "\n".join(out)


NC_I2_PERTURBATIONS = {
    "mixed": _mixed_indent,
    "plus4": lambda r: _reindent_after_first(r, "    "),
}


@pytest.mark.parametrize("kind", list(NC_I2_PERTURBATIONS))
def test_nc_i2_payload_indentation_alone_is_green(kind):
    src = SUSIE_R.read_text()
    head = _named_region(src, "too_many_variants_payload")
    old = _named_region(_pre_k1_source(), "too_many_variants_payload")
    _, new = _splice_region(src, "too_many_variants_payload",
                            NC_I2_PERTURBATIONS[kind])
    assert new != old and new != head
    _assert_region_unmoved("too_many_variants_payload", new, old)
    assert SUSIE_R.read_text() == src, "NC-I2 leaked onto the working tree"


@pytest.mark.parametrize(
    "region",
    [r for r in MUST_NOT_MOVE_REGIONS if r not in INDENT_INSENSITIVE_REGIONS],
)
def test_nc_i3_the_other_four_regions_stay_byte_exact(region):
    src = SUSIE_R.read_text()
    old = _named_region(_pre_k1_source(), region)
    _assert_region_unmoved(region, _named_region(src, region), old)
    _, new = _splice_region(src, region, lambda r: _reindent_after_first(r, "  "))
    with pytest.raises(AssertionError) as excinfo:
        _assert_region_unmoved(region, new, old)
    assert repr(region) in str(excinfo.value)
    assert SUSIE_R.read_text() == src, "NC-I3 leaked onto the working tree"


def test_the_difflib_diff_agrees_with_git_on_the_real_source():
    src = SUSIE_R.read_text()
    old = _pre_k1_source()
    git_diff = _git_diff_vs_pre_k1()
    dl_diff = _difflib_diff(old, src)
    assert git_diff.strip() and dl_diff.strip()
    _assert_symbol_diff_is_k1_only(git_diff, src, old)
    _assert_symbol_diff_is_k1_only(dl_diff, src, old)
    assert _symbol_scoped_changes(git_diff)[2] >= 1
    assert _symbol_scoped_changes(dl_diff)[2] >= 1


def test_nc_i4_diff_with_the_path2_assignment_back_is_red():
    src = SUSIE_R.read_text()
    old = _pre_k1_source()
    marker = "    ld_overlap_zero_fallback <- TRUE\n"
    spliced = _replace_once(src, marker, f"    {LEGACY_KEY_ASSIGNMENT}\n{marker}")
    with pytest.raises(AssertionError) as excinfo:
        _assert_symbol_diff_is_k1_only(_difflib_diff(old, spliced), spliced, old)
    assert _DIFF_MSG in str(excinfo.value)
    assert SUSIE_R.read_text() == src, "NC-I4 leaked onto the working tree"


def _reindent_emit(region: str) -> str:
    return _replace_once(region, f"    {LEGACY_KEY_EMIT}\n",
                         f"      {LEGACY_KEY_EMIT}\n")


def test_nc_i5_diff_reindentation_alone_is_green():
    src = SUSIE_R.read_text()
    old = _pre_k1_source()
    n_real = _symbol_scoped_changes(_difflib_diff(old, src))[2]
    perturbed, _ = _splice_region(src, "no_variants_payload", _reindent_emit)
    diff = _difflib_diff(old, perturbed)
    _assert_symbol_diff_is_k1_only(diff, perturbed, old)
    assert _symbol_scoped_changes(diff)[2] == n_real + 1
    assert SUSIE_R.read_text() == src, "NC-I5 leaked onto the working tree"


def test_nc_i6_the_reindent_cancellation_is_load_bearing():
    src = SUSIE_R.read_text()
    removed, _, n = _symbol_scoped_changes(_git_diff_vs_pre_k1(),
                                           cancel_reindent=False)
    assert n == 0
    assert LEGACY_KEY_EMIT in removed
    assert removed != [LEGACY_KEY_ASSIGNMENT]
    assert SUSIE_R.read_text() == src


def test_nc_i7_diff_extra_emit_outside_the_n1_payload_is_red():
    src = SUSIE_R.read_text()
    old = _pre_k1_source()
    perturbed, _ = _splice_region(
        src, "no_variants_payload",
        lambda r: _replace_once(r, f"    {LEGACY_KEY_EMIT}\n",
                                f"    {LEGACY_KEY_EMIT}\n    {LEGACY_KEY_EMIT}\n"))
    with pytest.raises(AssertionError) as excinfo:
        _assert_symbol_diff_is_k1_only(_difflib_diff(old, perturbed), perturbed, old)
    assert _DIFF_MSG in str(excinfo.value)
    assert SUSIE_R.read_text() == src, "NC-I7 leaked onto the working tree"


@pytest.mark.parametrize("kind", ["interior", "cross_hunk"])
def test_nc_i8_not_a_reindentation_is_not_cancelled(kind):
    src = SUSIE_R.read_text()
    if kind == "interior":
        old = _pre_k1_source()
        perturbed, _ = _splice_region(
            src, "too_many_variants_payload",
            lambda r: _replace_once(r, LEGACY_KEY_EMIT,
                                    "variant_catalog_fallback = used_variant_catalog"))
        with pytest.raises(AssertionError) as excinfo:
            _assert_symbol_diff_is_k1_only(_difflib_diff(old, perturbed),
                                           perturbed, old)
        assert _DIFF_MSG in str(excinfo.value)
    else:
        synthetic = (
            "--- a\n+++ b\n"
            "@@ -1,3 +1,2 @@\n ctx\n"
            f"-    {LEGACY_KEY_EMIT}\n ctx\n"
            "@@ -10,2 +9,3 @@\n ctx\n"
            f"+      {LEGACY_KEY_EMIT}\n ctx\n"
        )
        removed, added, n = _symbol_scoped_changes(synthetic)
        assert n == 0
        assert removed == [LEGACY_KEY_EMIT] and added == [LEGACY_KEY_EMIT]
    assert SUSIE_R.read_text() == src, "NC-I8 leaked onto the working tree"
