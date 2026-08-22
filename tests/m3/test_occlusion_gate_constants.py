"""THE ENFORCER for the two POSTED occlusion-gate ceilings.

``src/python/occlusion_gate_constants.py`` is the ONE place in this repository
that holds the two numbers the public pre-registration commits us to executing
(OSF file ``mk7ze`` on record ``az52u``, posted 2026-08-22T02:58:55Z). This module
is the named enforcer that keeps them tied to that public record.

WHY A RENDERED-STRING IDENTITY AND NOT A FLOAT TOLERANCE. The amendment writes the
ceilings as PRINTED STRINGS — ``0.5056%`` and ``3.42x`` — and those printed strings
are what the world was told. A float tolerance would let a value drift inside the
tolerance while the printed record stayed put; the interesting failure (a
transcription slip in the 4th decimal) is exactly the one a tolerance hides. So
the test parses the amendment's OWN SLOT_LEDGER lines and asserts that RENDERING
the shipped constant reproduces the parsed string BYTE FOR BYTE. That is a
must-be-identity transform, not a must-match number
(``feedback_aggregate_agreement_hides_component_errors``).

NON-VACUITY. Both ledger lines must be found exactly once, so deleting a ledger
line makes this RED rather than silently vacuous. And both halves carry an
in-test NEGATIVE CONTROL: a perturbed constant must render to a DIFFERENT string,
and a one-byte flip inside a scratch copy of the paste block must move its md5.
A green that has never been seen red is not a result
(``feedback_green_assertion_needs_a_negative_control``).

WHAT ELSE LIVES HERE. The banned-literal scans over the two consumers
(``run_native_ld_panel.py`` and ``fire_verifier.py``): the ceilings must be
IMPORTED / read at evaluation time, never hand-typed a second time. Those scans
strip ``#`` comments the way ``test_fire_verifier`` already does — note that a
docstring or an f-string is CODE, not a comment, and IS scanned.

NOTHING HERE TOUCHES THE PERIMETER, the network, or the amendment on disk. The
one-byte-flip control operates on a copy under pytest's ``tmp_path`` only.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

from occlusion_gate_constants import (          # noqa: E402  (module under test)
    OCCLUSION_INFLATION_CEILING,
    OCCLUSION_SITE_FRACTION_CEILING,
)

# --------------------------------------------------------------------------- #
# The public record                                                           #
# --------------------------------------------------------------------------- #

_AMENDMENT = (PROJECT_ROOT / ".planning" / "amendments"
              / "osf-amendment-occlusion-gate-recalibration-2026-08-20.md")

_PASTE_OPEN = "--- PASTE INTO OSF FROM HERE ---"
_PASTE_CLOSE = "--- PASTE ENDS HERE ---"

#: Marker-EXCLUSIVE paste block, as posted. SIZE FIRST, THEN HASH — the 260817-vbu
#: house order (a size mismatch localises the damage; a hash mismatch only says
#: "something moved").
_PASTE_BLOCK_BYTES = 22945
_PASTE_BLOCK_MD5 = "13a49f543cabcc27ce9f1e589783c060"

#: The amendment's OWN instantiation-ledger line shapes (two leading spaces in the
#: fenced SLOT_LEDGER block). ``[ \t]*$`` rather than ``\s*$``: ``\s`` matches a
#: newline under ``re.M`` and would let the match run past the line end.
_SLOT_PCT_RE = re.compile(
    r"^[ \t]*CEILING_3X_MEDIAN_PCT[ \t]*=[ \t]*([0-9.]+%)[ \t]*$", re.M)
_SLOT_INFLATION_RE = re.compile(
    r"^[ \t]*INFLATION_CEILING_3X_X[ \t]*=[ \t]*([0-9.]+x)[ \t]*$", re.M)


def _render_site_fraction_pct(fraction: float) -> str:
    """Render a bare FRACTION the way the amendment prints it: a PERCENTAGE to 4
    decimals with a trailing ``%``. The units trap in one function."""
    return f"{fraction * 100:.4f}%"


def _render_inflation_x(ratio: float) -> str:
    """Render an inflation ratio the way the amendment prints it: 2 decimals + ``x``."""
    return f"{ratio:.2f}x"


def _extract_paste_block(text: str) -> bytes:
    """The marker-EXCLUSIVE paste block, byte-identical to the shell guard

        awk '/--- PASTE INTO OSF FROM HERE ---/{f=1;next}
             /--- PASTE ENDS HERE ---/{f=0}f' "$A"

    i.e. the lines STRICTLY between the two markers, rejoined with ``\\n`` and
    given a trailing ``\\n`` (awk's own record terminator).
    """
    lines = text.splitlines()
    assert lines.count(_PASTE_OPEN) == 1, "paste-block OPEN marker is not unique"
    assert lines.count(_PASTE_CLOSE) == 1, "paste-block CLOSE marker is not unique"
    i = lines.index(_PASTE_OPEN)
    j = lines.index(_PASTE_CLOSE)
    assert i < j, "paste-block markers are out of order"
    return ("\n".join(lines[i + 1:j]) + "\n").encode()


# --------------------------------------------------------------------------- #
# A — rendered-string identity against the posted SLOT_LEDGER                 #
# --------------------------------------------------------------------------- #

def test_ceilings_render_identically_to_the_posted_slot_ledger():
    """The two shipped constants RENDER to the two strings the amendment printed.

    Identity, not tolerance; parsed from the amendment, not re-typed here. A
    change to either constant without a new posted amendment fails right here.
    """
    text = _AMENDMENT.read_text()

    pct_hits = _SLOT_PCT_RE.findall(text)
    infl_hits = _SLOT_INFLATION_RE.findall(text)
    # NON-VACUITY: a deleted ledger line must break this test, not silence it.
    assert len(pct_hits) == 1, (
        f"expected EXACTLY one CEILING_3X_MEDIAN_PCT ledger line in {_AMENDMENT}, "
        f"found {pct_hits!r} — the enforcer would be vacuous")
    assert len(infl_hits) == 1, (
        f"expected EXACTLY one INFLATION_CEILING_3X_X ledger line in {_AMENDMENT}, "
        f"found {infl_hits!r} — the enforcer would be vacuous")

    assert _render_site_fraction_pct(OCCLUSION_SITE_FRACTION_CEILING) == pct_hits[0], (
        "the shipped site-fraction ceiling does not render to the POSTED string "
        f"{pct_hits[0]!r}. The executed rule must be the pre-registered rule; a "
        "change here requires a NEW posted OSF amendment FIRST.")
    assert _render_inflation_x(OCCLUSION_INFLATION_CEILING) == infl_hits[0], (
        "the shipped inflation ceiling does not render to the POSTED string "
        f"{infl_hits[0]!r}. The executed rule must be the pre-registered rule; a "
        "change here requires a NEW posted OSF amendment FIRST.")


def test_site_fraction_ceiling_is_a_bare_fraction_not_a_percentage():
    """The units trap, pinned: the code holds 0.005056 (a FRACTION); the amendment
    prints 0.5056% (a PERCENTAGE). A consumer comparing a fraction against the
    percentage number would be 100x too permissive."""
    assert 0.0 < OCCLUSION_SITE_FRACTION_CEILING < 0.01
    assert OCCLUSION_INFLATION_CEILING > 1.0


# --------------------------------------------------------------------------- #
# B — the public-record pin (size first, then hash)                           #
# --------------------------------------------------------------------------- #

def test_amendment_paste_block_is_the_posted_bytes():
    """The marker-exclusive paste block is byte-frozen at what was posted.

    This is the repudiation guard: the constants above are only meaningful while
    the record they are pinned to is the record that was published.
    """
    block = _extract_paste_block(_AMENDMENT.read_text())
    assert len(block) == _PASTE_BLOCK_BYTES, (
        f"paste block is {len(block)} B, posted was {_PASTE_BLOCK_BYTES} B")
    assert hashlib.md5(block).hexdigest() == _PASTE_BLOCK_MD5, (
        "paste-block md5 moved off the posted anchor "
        f"{_PASTE_BLOCK_MD5} — the public record and the repo copy have diverged")


# --------------------------------------------------------------------------- #
# NEGATIVE CONTROLS — the enforcer is evidence only because it can fail       #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "renderer, perturbed, perturbed_rendering, posted",
    [
        (_render_site_fraction_pct, 0.005057, "0.5057%", "0.5056%"),
        (_render_site_fraction_pct, 0.005055, "0.5055%", "0.5056%"),
        (_render_inflation_x, 3.43, "3.43x", "3.42x"),
        (_render_inflation_x, 3.41, "3.41x", "3.42x"),
    ],
)
def test_NEGATIVE_CONTROL_rendered_identity_discriminates(
        renderer, perturbed, perturbed_rendering, posted):
    """CONTROL 1: the SAME rendering helper the green test uses must produce a
    DIFFERENT string for a perturbed constant. If it did not, the identity
    transform would be decoration."""
    assert renderer(perturbed) == perturbed_rendering
    assert renderer(perturbed) != posted


def test_NEGATIVE_CONTROL_one_byte_flip_moves_the_paste_block_md5(tmp_path):
    """CONTROL 2: a ONE-BYTE flip strictly INSIDE the paste block, performed on a
    scratch copy (never in-tree), moves the extracted md5 off the anchor while
    leaving the byte length unchanged — so the pin is measuring content, not size.
    """
    text = _AMENDMENT.read_text()
    lines = text.splitlines()
    i = lines.index(_PASTE_OPEN)
    j = lines.index(_PASTE_CLOSE)

    victim = next((k for k in range(i + 1, j) if "occlusion" in lines[k]), None)
    assert victim is not None, "no flippable line found inside the paste block"
    mutated = list(lines)
    # same-length substitution == a one-BYTE flip, not an edit
    mutated[victim] = lines[victim].replace("occlusion", "occlusiom", 1)
    assert mutated[victim] != lines[victim]
    assert len(mutated[victim]) == len(lines[victim])

    scratch = tmp_path / "amendment_copy.md"
    scratch.write_text("\n".join(mutated) + ("\n" if text.endswith("\n") else ""))

    flipped = _extract_paste_block(scratch.read_text())
    assert len(flipped) == _PASTE_BLOCK_BYTES, "the control changed the SIZE too"
    assert hashlib.md5(flipped).hexdigest() != _PASTE_BLOCK_MD5, (
        "a one-byte flip inside the paste block did NOT move the md5 -> the pin "
        "cannot detect tampering and is decoration")
