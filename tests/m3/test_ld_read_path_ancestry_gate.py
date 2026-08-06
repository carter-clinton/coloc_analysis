"""tests/m3/test_ld_read_path_ancestry_gate.py -- 260805-23d Task 1 (T-B).

THE ACCEPTANCE TEST FOR BLOCKER-B (``m3-04c-BLAST-RADIUS.md``): *Track-A EUR
numerics move.*

m3-04c Task 1b removed a pin -- ``run_susie_rss.R`` used to rebuild its own
``{ld_dir}/{ancestry}/{region_id}.rds`` path no matter what ``resolve_ld_path``
chose, which SILENTLY held every EUR fit at the 1kG tail. Task 1b removed that
pin for EVERY ancestry, not just AFR. Measured on two deliberately different EUR
panels: ``r[1,2]`` 0.1 -> 0.9, credible sets 3 -> 10, nonzero PIPs 200 -> 78 --
while ``ld_status`` and ``ld_overlap_fraction``, the two fields anyone would
check to argue nothing moved, stayed BYTE-IDENTICAL. Track A is in submission.

EUR is safe today ONLY because ``data/processed/ld_reference/`` does not exist.
That is enforced by nothing, and building ``EUR_ukbb_pub`` is a ``$0``
prerequisite already on the roadmap. This module is the enforcement.

WHAT THIS MODULE PINS -- and, explicitly, what it does NOT
---------------------------------------------------------
Containment has TWO halves. This module owns the FIRST and pins the wiring of
the second:

  (a) THE RESOLVED STRING. Off the allow-list the curated->M2 crosswalk is not
      applied, so ``input.ld_matrix`` resolves character-for-character as it did
      at ``3f431ab``.                                        <- T1.2, T1.3 here.
  (b) THE OPENED BYTES. Off the allow-list ``run_susie_rss.R`` must IGNORE the
      declared ``--ld-file`` entirely, so the loader's candidate list is the
      legacy one. That is the ``authoritative`` formal inside ``load_ld_matrix``
      and it lands in Task 2 of this plan, with its own behavioural proof against
      two different EUR panels (test G there).
      ⚠ UNTIL TASK 2 LANDS, (b) IS NOT CLOSED: the loader still tries the
      declared file first for every ancestry. T1.4/T1.5 here pin the argv that
      makes Task 2's switch reachable (``--ld-authoritative false`` is already
      rendered for EUR/TRANS), but they do not and cannot prove (b).

Exact argv byte-identity with ``3f431ab`` is UNREACHABLE by design: the
pre-existing ``test_ld_read_path.py::T2.1`` requires ``--ld-file
{input.ld_matrix}`` to survive in the comment-stripped ``shell:`` block exactly
once file-wide, so the flag cannot be dropped for EUR. T1.4 therefore pins the
delta to EXACTLY the tokens the design is authorized to add, and nothing else
(four at 260805-23d; six since 260805-o7o added ``--ld-allele-aware`` under
AUTH-o7o-01). The authoritative count lives in ``EXPECTED_ADDED_TOKENS``.

NO R, NO SNAKEMAKE, NO NETWORK. Every test here is pure Python over the source
tree plus ``git show``; there is no toolchain that could make one of them SKIP.
"""
from __future__ import annotations

import difflib
import importlib
import re
import shlex
import subprocess
from pathlib import Path

import yaml

from ld_panel import resolve_ld_path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FINEMAP_SMK = PROJECT_ROOT / "src" / "snakemake" / "rules" / "finemap.smk"

#: The commit that is the FROZEN reference for EUR/TRANS behaviour: the tree as
#: it stood before m3-04c Task 1b threaded ``--ld-file`` into the shell.
BASELINE_REV = "3f431ab"

#: The SIX tokens the design is allowed to add to ``run_finemap``'s Rscript
#: invocation, in this order, and nothing else.
#:
#: ⚠ THIS LIST IS A PROXY, NOT THE CONTRACT. The real contract -- stated in
#: ``test_rendered_argv_delta_vs_3f431ab_is_exactly_the_authorized_tokens``'s
#: docstring -- is that the delta stays confined to flags whose EUR/TRANS value is INERT BY
#: CONSTRUCTION. Being a closed literal, this list trips on any additional
#: token regardless of whether that token is inert, which is exactly what it
#: did when 260805-o7o added ``--ld-allele-aware``. WIDENED UNDER AUTH-o7o-01
#: (Carter, 2026-08-05), which required the widening be paid for by
#: ``test_params_ld_allele_aware_values`` below -- a DIRECT assertion of the
#: inertness property for EUR / TRANS / EAS / HIS and every degraded config
#: shape. The list got longer; the containment got STRICTER.
#:
#: Measured at HEAD against the shipped config/pipeline.yaml
#: ({enabled: true, ancestries: [AFR], allele_aware: true}):
#:     AFR    allele_aware=true    authoritative=true
#:     EUR    allele_aware=false   authoritative=false
#:     TRANS  allele_aware=false   authoritative=false
#:     EAS    allele_aware=false   authoritative=false
#:     HIS    allele_aware=false   authoritative=false
#:
#: DO NOT append a seventh/eighth token without landing the matching direct
#: inertness assertion. An entry here that nothing else pins is a widening for
#: free.
EXPECTED_ADDED_TOKENS = [
    "--ld-file",
    "{input.ld_matrix}",
    "--ld-authoritative",
    "{params.ld_authoritative}",
    "--ld-allele-aware",
    "{params.ld_allele_aware}",
]

#: Every ancestry that MUST stay off the declared-LD read path. EUR and TRANS
#: carry Track A (in submission); EAS and HIS have no AoU panel at all.
INERT_ANCESTRIES = ("EUR", "TRANS", "EAS", "HIS")

# The curated anchor used throughout. SH2B3_12q24 is Track A's anchor locus and
# the ONE curated region whose crosswalk target is a split subregion, so a
# crosswalk that leaks off the allow-list is maximally visible here.
ANCHOR = "SH2B3_12q24"
ANCHOR_M2 = "m2_region_00040__sub14"

# The real crosswalk maps the anchor (config/curated_to_m2_region_map.tsv:12).
CURATED_TO_M2 = {ANCHOR: ANCHOR_M2}
# Snakefile:45-62 builds this ONLY from config/regions_curated.csv, whose
# region_id column IS the curated slug -- so it is the identity here, exactly as
# in production.
REGION_SAFE_TO_ID = {ANCHOR: ANCHOR}


def _gate():
    """Import ``src/python/ld_read_path.py``.

    Imported lazily (not at module scope) so that a MISSING module fails as five
    NAMED assertions rather than as one pytest collection error -- the RED-phase
    requirement in 260805-23d Task 1. ``tests/m3/conftest.py`` already puts
    ``src/python`` on ``sys.path``.
    """
    try:
        return importlib.import_module("ld_read_path")
    except ImportError as exc:  # pragma: no cover - RED phase only
        raise AssertionError(
            "src/python/ld_read_path.py is missing or unimportable -- the "
            "ancestry allow-list that contains BLOCKER-B does not exist: "
            f"{exc}"
        ) from exc


def _cfg(ancestries=("AFR",), enabled=True) -> dict:
    return {"ld_read_path": {"enabled": enabled, "ancestries": list(ancestries)}}


def _panel_cfg(base: Path) -> dict:
    """The production ``ld_panel:`` block (config/pipeline.yaml:207-233) rooted
    at ``base``. Copied structurally, not imported, so a config edit that moves
    EUR off its 1kG tail shows up here as a FAILURE rather than silently."""
    return {
        "ld_panel": {
            "EUR": [
                {"source": "EUR_ukbb_pub", "path": str(base / "EUR_ukbb_pub" / "{region_safe}.rds")},
                {"source": "EUR_aou", "path": str(base / "EUR_aou" / "{region_id}.rds")},
                {"source": "EUR_ukbb", "path": str(base / "EUR_ukbb_ld" / "{region_safe}.rds")},
                {"source": "EUR_1kg", "path": str(base / "EUR" / "{region_safe}.rds")},
            ],
            "AFR": [
                {"source": "AFR_aou", "path": str(base / "AFR_aou" / "{region_id}.rds")},
                {"source": "AFR_hgdp", "path": str(base / "AFR_hgdp_1kg" / "{region_safe}.rds")},
                {"source": "AFR_1kg", "path": str(base / "AFR" / "{region_safe}.rds")},
            ],
            "TRANS": [
                {"source": "TRANS_aou_eur", "path": str(base / "EUR_aou" / "{region_id}.rds")},
                {"source": "EUR_1kg", "path": str(base / "EUR" / "{region_safe}.rds")},
            ],
            "strict_aou_only": False,
            "pin": {"EUR": None, "AFR": None, "TRANS": None},
        }
    }


def _touch(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"")
    return p


# ==========================================================================
# T1.1 -- the gate itself
# ==========================================================================
def test_gate_applies_to_afr_only():
    """T1.1. ``ld_read_path_applies`` is TRUE for AFR and FALSE for everything
    else, and every uncertain config shape answers "change nothing".

    Same discipline as ``occlusion_lockstep_cli._lockstep_applies``: this
    resolver decides which LD bytes a fine-map reads, so absent / disabled /
    unlisted must all mean LEGACY.
    """
    g = _gate()
    cfg = _cfg()
    assert g.ld_read_path_applies("AFR", cfg) is True
    assert g.ld_read_path_applies("EUR", cfg) is False, (
        "EUR must be OFF the allow-list -- this is the BLOCKER-B containment"
    )
    assert g.ld_read_path_applies("TRANS", cfg) is False

    # every "uncertain" config shape is a change-nothing answer
    assert g.ld_read_path_applies("AFR", {}) is False, "absent block must mean legacy"
    assert g.ld_read_path_applies("AFR", _cfg(enabled=False)) is False, (
        "enabled: false is the kill switch and must disarm AFR too"
    )
    assert g.ld_read_path_applies("AFR", _cfg(ancestries=())) is False, (
        "ancestries: [] is the kill switch and must disarm AFR too"
    )
    assert g.ld_read_path_applies("AFR", {"ld_read_path": "not-a-dict"}) is False
    assert g.ld_read_path_applies("AFR", None) is False

    # NEGATIVE CONTROL -- the function READS the list; it does not hardcode
    # "EUR -> False". Without this, a `return ancestry == "AFR"` stub would pass
    # every assertion above and the kill switch would be a lie.
    assert g.ld_read_path_applies("EUR", _cfg(ancestries=("AFR", "EUR"))) is True, (
        "the gate must read config ld_read_path.ancestries, not hardcode a verdict"
    )


# ==========================================================================
# T1.2 -- the crosswalk is not applied off the allow-list
# ==========================================================================
def test_crosswalk_is_not_applied_off_the_allow_list():
    """T1.2. ``ld_matrix_region_id`` returns 3f431ab's expression verbatim for
    every ancestry outside the allow-list.

    3f431ab's expression was ``REGION_SAFE_TO_ID[wildcards.region]``. m3-04c
    Task 1a replaced it with ``CURATED_TO_M2.get(region, REGION_SAFE_TO_ID[region])``
    for ALL ancestries (blast radius finding F). The crosswalk was built AFR-only
    (``build_curated_m2_crosswalk.py:145``), and ``ld_panel.EUR[1]`` /
    ``ld_panel.TRANS[0]`` both template on ``{region_id}`` -- so an ungated
    crosswalk reaches straight into EUR's and TRANS's chains.
    """
    g = _gate()
    cfg = _cfg()

    assert g.ld_matrix_region_id(ANCHOR, "EUR", cfg, CURATED_TO_M2, REGION_SAFE_TO_ID) == ANCHOR
    assert g.ld_matrix_region_id(ANCHOR, "TRANS", cfg, CURATED_TO_M2, REGION_SAFE_TO_ID) == ANCHOR

    # NEGATIVE CONTROL -- the crosswalk IS applied on the allow-list, so the
    # assertions above are observing a gate and not a no-op function.
    assert g.ld_matrix_region_id(ANCHOR, "AFR", cfg, CURATED_TO_M2, REGION_SAFE_TO_ID) == ANCHOR_M2, (
        "AFR must still be crosswalked or the AoU panel stays unreachable"
    )

    # an unmapped region falls through to the legacy value on BOTH sides
    unmapped_safe_to_id = {"BMI_Xq24": "BMI_Xq24"}
    for anc in ("AFR", "EUR", "TRANS"):
        assert g.ld_matrix_region_id(
            "BMI_Xq24", anc, cfg, CURATED_TO_M2, unmapped_safe_to_id
        ) == "BMI_Xq24"


# ==========================================================================
# T1.3 -- the RESOLVED STRING is byte-identical to 3f431ab, for EUR and TRANS
# ==========================================================================
def _resolved_new(g, region, ancestry, cfg, panel_cfg) -> str:
    """What ``run_finemap.input.ld_matrix`` resolves to AFTER this task."""
    merged = {**panel_cfg, **cfg}
    return str(
        resolve_ld_path(
            region_id=g.ld_matrix_region_id(region, ancestry, merged, CURATED_TO_M2, REGION_SAFE_TO_ID),
            ancestry=ancestry,
            config=merged,
            region_safe=region,
        )
    )


def _resolved_3f431ab(region, ancestry, panel_cfg) -> str:
    """What ``run_finemap.input.ld_matrix`` resolved to AT 3f431ab -- the
    expression copied character-for-character from that revision."""
    return str(
        resolve_ld_path(
            region_id=REGION_SAFE_TO_ID[region],
            ancestry=ancestry,
            config=panel_cfg,
            region_safe=region,
        )
    )


def test_declared_path_is_byte_identical_to_3f431ab_for_eur_and_trans(tmp_path):
    """T1.3. The resolved ``input.ld_matrix`` STRING for EUR and TRANS is
    byte-identical to 3f431ab's.

    TWO TREES, deliberately. The first is the "chain head present" tree the plan
    names. The second is CROSSWALK-SENSITIVE: it is built so that applying the
    crosswalk genuinely changes the answer, which is what makes the equality
    assertion capable of failing. Without tree B the assertion is satisfied by
    ``ld_panel.EUR[0]`` templating on ``{region_safe}`` and observes nothing --
    exactly the "structurally incapable of failing" class the blast radius found
    five times.
    """
    g = _gate()
    cfg = _cfg()

    # ---- TREE A: EUR chain head present (both templates land on the same id)
    base_a = tmp_path / "a" / "ld_reference"
    panel_a = _panel_cfg(base_a)
    _touch(base_a / "EUR_ukbb_pub" / f"{ANCHOR}.rds")
    _touch(base_a / "EUR" / f"{ANCHOR}.rds")
    for anc in ("EUR", "TRANS"):
        assert _resolved_new(g, ANCHOR, anc, cfg, panel_a) == _resolved_3f431ab(ANCHOR, anc, panel_a)

    # ---- TREE B: crosswalk-sensitive. EUR_ukbb_pub is ABSENT for this region
    # and EUR_aou/{m2_id}.rds EXISTS, so the crosswalk -- if it leaked -- would
    # move EUR off its 1kG tail and TRANS off its EUR_1kg fallback.
    base_b = tmp_path / "b" / "ld_reference"
    panel_b = _panel_cfg(base_b)
    aou_eur = _touch(base_b / "EUR_aou" / f"{ANCHOR_M2}.rds")
    kg = _touch(base_b / "EUR" / f"{ANCHOR}.rds")

    for anc in ("EUR", "TRANS"):
        legacy = _resolved_3f431ab(ANCHOR, anc, panel_b)
        assert legacy == str(kg), (
            f"[{anc}] fixture broken: 3f431ab must resolve to the 1kG tail here, got {legacy!r}"
        )
        assert _resolved_new(g, ANCHOR, anc, cfg, panel_b) == legacy, (
            f"[{anc}] input.ld_matrix moved off 3f431ab's string -- BLOCKER-B is open"
        )

        # NEGATIVE CONTROL -- with this ancestry ON the allow-list the very same
        # comparison FAILS, so the equality above is a measurement, not a tautology.
        leaked = _resolved_new(g, ANCHOR, anc, _cfg(ancestries=("AFR", anc)), panel_b)
        assert leaked == str(aou_eur), (
            f"[{anc}] negative control is vacuous: the crosswalk did not change the "
            f"resolved path even when the ancestry was allow-listed (got {leaked!r})"
        )
        assert leaked != legacy


# ==========================================================================
# T1.4 -- the rendered argv delta vs 3f431ab is EXACTLY the authorized tokens
# ==========================================================================
def _rule_block(text: str, rule_name: str) -> str:
    """COPIED from tests/m3/test_ld_read_path.py (not imported: that module is
    pre-existing and must stay unedited, and a shared helper would couple two
    suites that pin different things)."""
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
    """COPIED from tests/m3/test_ld_read_path.py: the ``shell:`` body with ``#``
    COMMENT LINES REMOVED, so prose about a flag cannot satisfy an assertion
    about the command that is actually executed."""
    block = _directive_block(_rule_block(smk_text, rule_name), "shell")
    return "\n".join(
        line for line in block.splitlines() if not line.lstrip().startswith("#")
    )


def _rscript_argv(smk_text: str) -> list[str]:
    """The ``run_susie_rss.R`` invocation only, as a shlex token list.

    Line-continuations are joined; everything before the ``Rscript`` line and
    from the ``{PYTHON_BIN} -c`` receipt line onward is cut, so the comparison
    sees the fine-mapping argv and nothing else."""
    lines = _shell_command_block(smk_text).splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip().startswith("Rscript "))
    end = next(
        (i for i in range(start + 1, len(lines)) if "{PYTHON_BIN}" in lines[i]),
        len(lines),
    )
    joined = " ".join(ln.strip().rstrip("\\").strip() for ln in lines[start:end])
    return shlex.split(joined)


def _argv_delta(old: list[str], new: list[str]) -> tuple[list[str], list[str]]:
    """(added, removed) between two token lists, ORDER-SENSITIVE: a reordering
    shows up as a delete plus an insert, never as "no change"."""
    added: list[str] = []
    removed: list[str] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
        a=old, b=new, autojunk=False
    ).get_opcodes():
        if tag in ("insert", "replace"):
            added.extend(new[j1:j2])
        if tag in ("delete", "replace"):
            removed.extend(old[i1:i2])
    return added, removed


def _baseline_finemap_smk() -> str:
    return subprocess.run(
        ["git", "show", f"{BASELINE_REV}:src/snakemake/rules/finemap.smk"],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True,
    ).stdout


def test_rendered_argv_delta_vs_3f431ab_is_exactly_the_authorized_tokens():
    """T1.4. ``run_finemap``'s Rscript argv gained EXACTLY the tokens the design
    is authorized to add versus 3f431ab, and lost or reordered nothing.

    ⚠ THIS IS NOT A BEHAVIOURAL CONTAINMENT PROOF. It pins that the argv delta
    is confined to flags whose EUR/TRANS value is inert BY CONSTRUCTION once
    ``load_ld_matrix`` honours ``--ld-authoritative``. Byte-identical argv is
    unreachable here because the pre-existing T2.1 forbids removing
    ``--ld-file`` from the shell; this is the strictly-bounded alternative.

    ⚠ RENAMED under AUTH-o7o-01 (260805-o7o). This was
    ``test_rendered_argv_delta_vs_3f431ab_is_exactly_four_tokens`` when the list
    held four tokens -- the name it is cited under in 260805-23d's PLAN and
    SUMMARY. It went stale the moment ``--ld-allele-aware`` was authorized, so
    the count came out of the name entirely rather than being bumped to six and
    left to go stale again on the next authorization. The count now lives in
    ``EXPECTED_ADDED_TOKENS`` alone, where it is checked rather than described.
    """
    old = _rscript_argv(_baseline_finemap_smk())
    new = _rscript_argv(FINEMAP_SMK.read_text())

    added, removed = _argv_delta(old, new)
    assert removed == [], (
        f"run_finemap's Rscript invocation LOST tokens versus {BASELINE_REV}: {removed!r}"
    )
    assert added == EXPECTED_ADDED_TOKENS, (
        f"the argv delta versus {BASELINE_REV} must be exactly "
        f"{EXPECTED_ADDED_TOKENS!r}, got {added!r}"
    )
    # ...and the declared-LD flag stays BEFORE --ld-authoritative so T2.1's
    # `--ld-file\s+(\S+)` capture cannot be confused.
    assert new.index("--ld-file") < new.index("--ld-authoritative")

    # NEGATIVE CONTROL -- the same comparison of the baseline against ITSELF is
    # empty. Without it, a bug in _rscript_argv that returned [] for both sides
    # would pass `removed == []` and be caught by nothing.
    self_added, self_removed = _argv_delta(old, old)
    assert (self_added, self_removed) == ([], []), (
        "the argv differ is not self-consistent"
    )
    assert len(old) > 20, f"the baseline argv slice is suspiciously short: {old!r}"


# ==========================================================================
# T1.5 -- the value handed to --ld-authoritative
# ==========================================================================
def test_params_ld_authoritative_values():
    """T1.5. ``--ld-authoritative`` is ``"true"`` for AFR and ``"false"`` for
    everything else, including every degraded config shape.

    The literal strings matter: this value is rendered straight into the shell
    and parsed by ``run_susie_rss.R``, which stop()s on anything it does not
    recognise."""
    g = _gate()
    cfg = _cfg()
    assert g.ld_file_authoritative("AFR", cfg) == "true"
    assert g.ld_file_authoritative("EUR", cfg) == "false"
    assert g.ld_file_authoritative("TRANS", cfg) == "false"
    assert g.ld_file_authoritative("AFR", {}) == "false", (
        "an absent block must render 'false' -- legacy behaviour everywhere"
    )
    assert g.ld_file_authoritative("AFR", _cfg(enabled=False)) == "false"

    # NEGATIVE CONTROL -- the value tracks the allow-list rather than being a
    # constant; a `return "false"` stub would satisfy 4 of the 5 asserts above.
    assert g.ld_file_authoritative("EUR", _cfg(ancestries=("AFR", "EUR"))) == "true"

    # the rendered shell reads this param and nothing else
    shell = _shell_command_block(FINEMAP_SMK.read_text())
    assert re.search(r"--ld-authoritative\s+\{params\.ld_authoritative\}", shell), (
        "run_finemap's shell: must pass --ld-authoritative {params.ld_authoritative}"
    )
    params = _directive_block(_rule_block(FINEMAP_SMK.read_text(), "run_finemap"), "params")
    assert "ld_file_authoritative(" in params, (
        "params.ld_authoritative must come from ld_read_path.ld_file_authoritative, "
        f"not be hardcoded; params block was:\n{params}"
    )


# ==========================================================================
# T1.6 -- the value handed to --ld-allele-aware (260805-o7o, AUTH-o7o-01)
# ==========================================================================
def _cfg_aware(ancestries=("AFR",), enabled=True, allele_aware=True) -> dict:
    """``_cfg`` plus the ``allele_aware`` sub-key. Separate helper so ``_cfg``
    stays byte-identical for the pre-existing tests that call it."""
    block = {"enabled": enabled, "ancestries": list(ancestries)}
    if allele_aware is not None:
        block["allele_aware"] = allele_aware
    return {"ld_read_path": block}


def test_params_ld_allele_aware_values():
    """T1.6. ``--ld-allele-aware`` is ``"true"`` for AFR and ``"false"`` for
    EVERY other ancestry, including every degraded config shape.

    ⚠ THIS TEST IS THE PRICE OF WIDENING ``EXPECTED_ADDED_TOKENS``, and it is
    why AUTH-o7o-01 authorized that widening. ``EXPECTED_ADDED_TOKENS`` is a
    PROXY for the real contract -- "the argv delta is confined to flags whose
    EUR/TRANS value is inert BY CONSTRUCTION"
    (``test_rendered_argv_delta_vs_3f431ab_is_exactly_the_authorized_tokens``,
    T1.4). As a
    closed literal it trips on ANY additional token whether or not that token is
    inert, so lengthening it alone would trade a real guarantee for a stale
    count. This asserts the inertness DIRECTLY, for a wider ancestry set than
    T1.5 covers, so the containment ends up STRICTER than before the widening.

    Why these four ancestries: EUR and TRANS carry Track A, which is in
    submission; EAS and HIS have no AoU panel at all, so a leak there would
    point a fit at a panel nothing declares.

    NEGATIVE CONTROL (in-test): put EUR on the allow-list and the SAME assertion
    must render ``"true"``. Without it a ``return "false"`` stub would satisfy
    every inertness assert above -- the unfalsifiable-proxy failure this arc has
    now hit three times.
    """
    g = _gate()
    cfg = _cfg_aware()

    # THE ARMED CASE
    assert g.ld_allele_aware("AFR", cfg) == "true"

    # THE INERT CASES -- the property T1.4's docstring actually names
    for anc in INERT_ANCESTRIES:
        assert g.ld_allele_aware(anc, cfg) == "false", (
            f"--ld-allele-aware renders {g.ld_allele_aware(anc, cfg)!r} for "
            f"{anc}; it must be 'false' so the allele-aware join is inert BY "
            f"CONSTRUCTION off the allow-list. EUR/TRANS carry Track A, which "
            f"is in submission."
        )

    # ...and against the REAL shipped config, not only a synthetic one, so the
    # shipped file cannot drift EUR onto the read path unnoticed.
    shipped = yaml.safe_load((PROJECT_ROOT / "config" / "pipeline.yaml").read_text())
    assert g.ld_allele_aware("AFR", shipped) == "true"
    for anc in INERT_ANCESTRIES:
        assert g.ld_allele_aware(anc, shipped) == "false", (
            f"the SHIPPED config/pipeline.yaml arms the allele-aware join for "
            f"{anc}"
        )

    # every degraded config shape T1.5 enumerates, plus the two new ones
    assert g.ld_allele_aware("AFR", {}) == "false", (
        "an absent block must render 'false' -- legacy behaviour everywhere"
    )
    assert g.ld_allele_aware("AFR", {"ld_read_path": "not-a-dict"}) == "false", (
        "a malformed block must render 'false'"
    )
    assert g.ld_allele_aware("AFR", _cfg_aware(enabled=False)) == "false"
    assert g.ld_allele_aware("AFR", _cfg_aware(ancestries=())) == "false"
    assert g.ld_allele_aware("AFR", _cfg_aware(allele_aware=None)) == "false", (
        "an ABSENT allele_aware sub-key must render 'false' -- the fail-safe is "
        "CHANGE NOTHING, and this flag decides which LD row each z binds to"
    )
    assert g.ld_allele_aware("AFR", _cfg_aware(allele_aware=False)) == "false"

    # the two levers are INDEPENDENT: disarming the join must not disarm
    # 260805-23d's authoritative-declared-panel mandate
    assert g.ld_file_authoritative("AFR", _cfg_aware(allele_aware=False)) == "true"

    # NEGATIVE CONTROL -- the value tracks the allow-list rather than being a
    # constant. Without this, a `return "false"` stub passes everything above.
    assert g.ld_allele_aware("EUR", _cfg_aware(ancestries=("AFR", "EUR"))) == "true", (
        "putting EUR on the allow-list did NOT arm the flag -- every inertness "
        "assertion above is vacuous"
    )

    # the rendered shell reads this param, and it is not hardcoded
    shell = _shell_command_block(FINEMAP_SMK.read_text())
    assert re.search(r"--ld-allele-aware\s+\{params\.ld_allele_aware\}", shell), (
        "run_finemap's shell: must pass --ld-allele-aware {params.ld_allele_aware}"
    )
    params = _directive_block(_rule_block(FINEMAP_SMK.read_text(), "run_finemap"), "params")
    assert "ld_allele_aware(" in params, (
        "params.ld_allele_aware must come from ld_read_path.ld_allele_aware, "
        f"not be hardcoded; params block was:\n{params}"
    )
