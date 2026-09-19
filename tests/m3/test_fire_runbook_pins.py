"""NAMED ENFORCERS for claims the 260812-ox1 fire runbooks make about themselves.

Created by quick-260918-qz5. Every test here exists because a claim was being
made with NO enforcer, and
``[[feedback_a_claimed_invariant_needs_a_named_enforcer]]`` is explicit that an
invariant with no named enforcer is a BELIEF. This project has already shipped a
"all pinned files 0-line diff vs <SHA>" assertion that nothing anywhere enforced,
and 5 of the 8 files had drifted.

THREE claims are pinned here:

1. ``test_stage_c_fire_command_and_step_9d_are_byte_pinned`` — quick-260918-qz5
   edits ``260812-ox1-AGENT-PROMPT.md`` ~20 lines away from the Stage C fire
   command, and the plan asserts both that command and the STEP 9d block stay
   BYTE-UNCHANGED. Before this, the only "enforcer" of that was a human reading a
   ``git diff``.

2. ``test_the_agent_surface_and_the_paste_surface_carry_the_same_raise_posture`` —
   ``AGENT-PROMPT.md`` is what the AGENT reads and ``BROWSER-PASTE.md`` is what
   Carter PASTES. quick-260918-qz0 landed the Stage-C raise posture in the AGENT
   surface only, so the paste surface carried no posture at all.

3. ``test_the_two_live_gate_skips_are_the_only_ones_while_no_panel_tsv_is_in_repo``
   — ``tests/m3/test_fire_verifier.py``'s module docstring asserts a SKIP COUNT.
   An unenforced count claim is precisely the class of belief-only assertion that
   docstring correction is itself fixing, so it gets an enforcer in the same
   change.

⚠ ONE TEST HERE SHELLS OUT to a child pytest (claim 3). It is exempt from the
"one pytest at a time" rule only in the sense that it IS that one pytest's child.
Never run it concurrently with a full-suite run.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

RUNBOOK_DIR = (PROJECT_ROOT / ".planning" / "quick"
               / "260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r")

# --------------------------------------------------------------------------- #
# 1. the BYTE-PINNED blocks                                                   #
# --------------------------------------------------------------------------- #
# Located by UNIQUE QUOTED ANCHOR, never by line number: quick-260918-qz5's own
# edits move every line below them, and an enforcer that cites an offset breaks
# the moment the file it guards is edited
# (`[[reference_enforcement_traps_literals_and_linenumbers]]`).
#
# ⛔ NOT the bare string "STEP 9d": that occurs SEVEN times in the file
# (measured). Ambiguous locators relocate to the wrong place half the time, so
# the bare form is used ONLY as a containment assertion INSIDE an
# already-located block.
_FIRE_ANCHOR = "timeout 312h nohup python3"          # measured raw=1 norm=1
_STEP9D_ANCHOR = "STEP 9d — FIRE-SHELL PRECONDITIONS"  # measured raw=1 norm=1

#: MEASURED by the executor of quick-260918-qz5 from the INSTALLED
#: 260812-ox1-AGENT-PROMPT.md (md5 48295e108d4ff3b0dab3bf366b70c085, 709 lines).
#: Both blocks were verified BYTE-IDENTICAL at 940df48 and at b6076b2 — i.e.
#: quick-260918-qz0's +38-line insertion did not touch either one — so the pin is
#: valid against both the plan's originally-cited BASE and the post-qz0 base this
#: task actually ran on. The fire command is form B (`timeout 312h nohup python3`),
#: which was MEASURED, not guessed: form A (`nohup timeout 312h python3`) lets
#: timeout FORWARD the SIGHUP and the child DIED on GNU coreutils 8.32
#: (quick-260916-vqr, 2026-09-16).
_FIRE_COMMAND_MD5 = "16a8417991547c3e423fc356cec41f89"   # 2 lines, 330 B
_STEP_9D_MD5 = "7dd6c73ec14b640dcaf41526f1221fca"        # 149 lines, 7,972 B


def _agent_prompt_text() -> str:
    return (RUNBOOK_DIR / "260812-ox1-AGENT-PROMPT.md").read_text()


def _extract_fire_command(text: str) -> str:
    """The form-B fire command block: the anchored line plus the indented lines
    that follow it (the command and its `echo "fire PID: $!"`)."""
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if _FIRE_ANCHOR in l]
    assert len(hits) == 1, f"the fire-command anchor matched {len(hits)} times"
    i = hits[0]
    out = [lines[i]]
    j = i + 1
    while j < len(lines) and lines[j].startswith("  ") and lines[j].strip():
        out.append(lines[j])
        j += 1
    return "\n".join(out) + "\n"


def _extract_step_9d(text: str) -> str:
    """The STEP 9d block: from its own heading to the next top-level STEP heading."""
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if _STEP9D_ANCHOR in l]
    assert len(hits) == 1, f"the STEP 9d anchor matched {len(hits)} times"
    i = hits[0]
    j = i + 1
    while j < len(lines) and not lines[j].startswith("STEP "):
        j += 1
    return "\n".join(lines[i:j]) + "\n"


def test_stage_c_fire_command_and_step_9d_are_byte_pinned():
    """The Stage C fire command and the STEP 9d block are BYTE-UNCHANGED.

    ⚠ HOW TO MOVE THIS PIN, because a content pin with no documented exit route
    becomes an uninterpretable red for whoever comes next
    (`[[feedback_fixed_sha_whole_file_pin_is_a_timebomb]]`):

    This pins the Stage C fire command and the STEP 9d block as measured at
    b6076b2 (and verified identical at 940df48), because quick-260918-qz5 edits
    this same file ~20 lines away from the command and the form-B command was
    MEASURED, not guessed (GNU coreutils 8.32, quick-260916-vqr). A LEGITIMATE
    future change to either block updates THESE TWO CONSTANTS and nothing else,
    in the same commit as a recorded decision naming what changed and why. NEVER
    re-derive them to silence a red you have not explained.
    """
    t = _agent_prompt_text()
    fire = _extract_fire_command(t)
    step9d = _extract_step_9d(t)

    # NON-VACUITY, both blocks: a pin over an empty or wrong extraction is worse
    # than no pin, because it is green.
    assert fire.strip(), "the fire-command extraction is EMPTY"
    assert step9d.strip(), "the STEP 9d extraction is EMPTY"
    assert _FIRE_ANCHOR in fire
    assert 'echo "fire PID: $!"' in fire
    assert "STEP 9d" in step9d
    # form A must never reappear: nohup OUTSIDE timeout lets the SIGHUP through
    assert "nohup timeout 312h python3" not in fire, (
        "the RETIRED form A reappeared in the fire command; it was MEASURED to "
        "let timeout forward the SIGHUP and kill the child")

    assert hashlib.md5(fire.encode()).hexdigest() == _FIRE_COMMAND_MD5, (
        f"the Stage C fire command CHANGED:\n{fire}")
    assert hashlib.md5(step9d.encode()).hexdigest() == _STEP_9D_MD5, (
        "the STEP 9d block CHANGED (first line: "
        f"{step9d.split(chr(10))[0]!r}, {step9d.count(chr(10))} lines)")


def test_the_byte_pin_is_PROVEN_ABLE_TO_FAIL_on_a_mutated_copy():
    """The pin above is green; this is the observation that it CAN go red.

    Mutated IN MEMORY — never by editing the shared working tree, which is how a
    control becomes a real defect."""
    t = _agent_prompt_text()
    real_fire = _extract_fire_command(t)
    # Mutate INSIDE the block but NOT the anchor itself: a wrong --ancestry would
    # fire the whole ~11-day panel against the wrong cohort, and it is exactly the
    # kind of one-token edit a human diff review slides past.
    # (⚠ mutating the anchor string instead makes the EXTRACTOR fail rather than
    # the PIN, which is a control that passes for the wrong reason — measured.)
    mutated = t.replace("--ancestry AFR >", "--ancestry EUR >")
    assert mutated != t, "the mutation did not apply -> this control is vacuous"
    mut_fire = _extract_fire_command(mutated)
    assert _FIRE_ANCHOR in mut_fire, "the extractor must still locate the block"
    assert hashlib.md5(mut_fire.encode()).hexdigest() != _FIRE_COMMAND_MD5, \
        "the fire-command pin did NOT notice a changed timeout -> it is vacuous"
    assert hashlib.md5(real_fire.encode()).hexdigest() == _FIRE_COMMAND_MD5

    real_9d = _extract_step_9d(t)
    mutated9 = t.replace("computes nothing.", "computes nothing. (edited)")
    mut_9d = _extract_step_9d(mutated9)
    assert mut_9d != real_9d
    assert hashlib.md5(mut_9d.encode()).hexdigest() != _STEP_9D_MD5, \
        "the STEP 9d pin did NOT notice an edited block -> it is vacuous"


# --------------------------------------------------------------------------- #
# 2. THE TWO OPERATOR SURFACES MUST AGREE                                     #
# --------------------------------------------------------------------------- #

#: The five posture probes, one per operative rule plus the resume mechanism.
#: MEASURED against the INSTALLED (post-qz0) AGENT-PROMPT.md at n >= 1 each
#: before this test was written — the probe list describes qz0's LANDED WORDING,
#: which this task does not own. If qz0's wording ever moves, the probe is
#: re-worded to match qz0's text; qz0's block is never edited to satisfy this.
_POSTURE_PROBES = ("m2_region_00057", "UNCLASSIFIED", "inputs or the criterion",
                   "closeout denominator", "recomputes on resume")

#: The CORRECTED resume mechanism. Verified against the SHIPPED code: the resume
#: skip consults the `.npz` and NOTHING ELSE, so every region that banked nothing
#: recomputes.
_CORRECTED_RESUME = "already in the bucket"

#: ⚠ THE BANNED (NARROWED) RESUME SENTENCE, matched BY ITS PROPERTY.
#:
#: The reviewer's form — "Resume skips a region only if its `.npz` exists, so an
#: `error:` region is recomputed on every re-fire" — names ONLY `error:` and
#: thereby implies a `verify_failed` or `deferred_*` region would be SKIPPED.
#: That is MEASURED FALSE against the shipped code, so it must appear in NEITHER
#: surface.
#:
#: ⚠ THE SENTENCE BOUNDARY IS THE WHOLE DIFFICULTY, and getting it wrong makes
#: this guard VACUOUS. A naive `[^.]{0,400}\.` terminates on the period INSIDE
#: `.npz`, so the matched span is always "Resume skips a region only if its `."
#: — which can never contain `error:`, and the guard silently passes on the very
#: sentence it bans. (Measured: that exact form was tried and could not go red on
#: the banned text.) A real sentence end is a period followed by WHITESPACE or
#: end-of-string, which `.npz` is not, so that is what is matched here.
_RESUME_SENTENCE = re.compile(
    r"[Rr]esume skips a region only if.{0,600}?\.(?=\s|$)", re.S)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def _carries_narrowed_resume(text: str):
    """Every narrowed resume sentence in ``text`` (normalised). Empty == clean."""
    hits = []
    for m in _RESUME_SENTENCE.finditer(_norm(text)):
        s = m.group(0)
        if "error:" in s and "verify_failed" not in s and "deferred_" not in s:
            hits.append(s)
    return hits


def test_the_agent_surface_and_the_paste_surface_carry_the_same_raise_posture():
    """AGENT-PROMPT.md is what the agent reads; BROWSER-PASTE.md is what Carter
    pastes. A posture that lives in only one of them is a posture half the
    operators never see.

    ⚠ THIS IS A TEXT CHECK, and therefore the WEAKEST gate in quick-260918-qz5:
    it pins the PRESENCE OF THE OPERATIVE LANGUAGE, not a behaviour. That is
    genuinely what is at stake for a human-read runbook, and nothing stronger
    exists for prose — but it is not, and must not be reported as, a behavioural
    pin.
    """
    agent = _norm((RUNBOOK_DIR / "260812-ox1-AGENT-PROMPT.md").read_text())
    paste = _norm((RUNBOOK_DIR / "260812-ox1-BROWSER-PASTE.md").read_text())
    surfaces = (("AGENT-PROMPT", agent), ("BROWSER-PASTE", paste))

    for probe in _POSTURE_PROBES:
        for name, txt in surfaces:
            assert probe.lower() in txt.lower(), \
                f"{name} is missing the posture probe {probe!r}"

    for name, txt in surfaces:
        assert _CORRECTED_RESUME in txt.lower(), \
            f"{name} is missing the corrected resume mechanism"

    for name, txt in surfaces:
        assert not _carries_narrowed_resume(txt), \
            f"{name} carries the NARROWED resume sentence: " \
            f"{_carries_narrowed_resume(txt)!r}"


def test_the_two_surface_gate_is_PROVEN_ABLE_TO_FAIL_in_both_directions():
    """The green above is evidence only because this has been seen to fail.

    Both directions, in memory: a surface with the posture STRIPPED must go red
    on the probes, and a surface carrying the banned C5 sentence VERBATIM must go
    red on the ban."""
    # (a) the probe direction
    agent = _norm((RUNBOOK_DIR / "260812-ox1-AGENT-PROMPT.md").read_text())
    stripped = agent
    for probe in _POSTURE_PROBES:
        stripped = re.sub(re.escape(probe), "xxxx", stripped, flags=re.I)
    missing = [p for p in _POSTURE_PROBES if p.lower() not in stripped.lower()]
    assert missing == list(_POSTURE_PROBES), \
        "the probe assertion cannot detect a stripped surface -> it is vacuous"

    # (b) the BAN direction, against the reviewer's C5 sentence VERBATIM
    c5 = ("Resume skips a region only if its `.npz` exists, so an `error:` region "
          "is recomputed on every re-fire.")
    assert _carries_narrowed_resume(c5), (
        "the narrowed-resume ban cannot detect the banned sentence -> it is "
        "VACUOUS. This is exactly the failure mode a `[^.]{0,400}` sentence "
        "bound produces: it stops at the period inside `.npz`.")
    # and the CORRECTED sentence must NOT trip the ban (no false positive)
    corrected = ("Resume skips a region only if its `.npz` is ALREADY IN THE "
                 "BUCKET, so every region that banked nothing — `error:`, "
                 "`verify_failed` and BOTH `deferred_*` classes — recomputes on "
                 "resume.")
    assert not _carries_narrowed_resume(corrected), \
        "the ban FALSE-POSITIVES on the corrected sentence"


# --------------------------------------------------------------------------- #
# 3. THE SKIP COUNT the test_fire_verifier.py docstring claims                 #
# --------------------------------------------------------------------------- #

def test_the_two_live_gate_skips_are_the_only_ones_while_no_panel_tsv_is_in_repo(
        tmp_path):
    """Names the claim the test_fire_verifier.py module docstring makes, so it
    cannot go stale. Without this, "two skips / 33 -> 34" would drift silently —
    which is precisely the failure mode the corrected docstring is fixing.

    ⚠ RECONCILED BY TEST ID, from the child run's JUnit XML — NOT by grepping its
    summary line. MEASURED: `pytest -q -rs` prints each skip as
    `SKIPPED [1] <file>:<line>: <reason>`, with the test NAME nowhere in the
    output, so an assertion that the names appear in stdout can never pass. A
    by-id parse also survives any future change to pytest's summary formatting,
    and pins WHICH two tests skip rather than merely how many.
    """
    import fire_verifier as fv
    if fv.find_measured_panel_tsvs(PROJECT_ROOT):
        pytest.skip("a measured panel TSV landed: both live gates now RUN; "
                    "this claim is spent")
    xml = tmp_path / "child.xml"
    subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider",
                    "-q", f"--junitxml={xml}",
                    str(PROJECT_ROOT / "tests/m3/test_fire_verifier.py")],
                   capture_output=True, text=True, cwd=PROJECT_ROOT)
    import xml.etree.ElementTree as ET
    tree = ET.parse(xml)
    skipped, failed = [], []
    for tc in tree.iter("testcase"):
        kinds = {ch.tag for ch in tc}
        if "skipped" in kinds:
            skipped.append(tc.get("name"))
        if kinds & {"failure", "error"}:
            failed.append(tc.get("name"))
    assert not failed, f"the child run had failures: {failed}"
    assert sorted(skipped) == sorted([
        "test_coverage_disclosure_live_gate_against_the_repo_file",
        "test_raised_nan_class_coverage_live_gate_against_the_repo_file",
    ]), (f"this module must contribute EXACTLY the two named live-gate skips "
         f"while no measured panel TSV is in-repo; it contributed {skipped}")
