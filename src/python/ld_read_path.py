"""ld_read_path.py — the ANCESTRY ALLOW-LIST for the DECLARED-LD read path.

m3-04c blast radius, **BLOCKER-B**. m3-04c Task 1b removed a pin that had been
SILENTLY holding every EUR fit at ``{ld_dir}/EUR/{region}.rds`` (the 1kG tail):
``run_susie_rss.R`` always rebuilt its own path regardless of what
``resolve_ld_path`` chose. Task 1b un-pinned it **for every ancestry, not just
AFR**. Measured on two deliberately different EUR panels: ``r[1,2]`` 0.1 -> 0.9,
credible sets 3 -> 10, nonzero PIPs 200 -> 78 — while ``ld_status`` and
``ld_overlap_fraction``, the two fields anyone would check to argue nothing
moved, stayed **BYTE-IDENTICAL**. Track A is in submission.

EUR is safe today only because ``data/processed/ld_reference/`` does not exist.
That is enforced by nothing, and building ``EUR_ukbb_pub`` is a ``$0``
prerequisite already on the roadmap. This module is the enforcement.

WHAT IT GATES
-------------
For every ancestry NOT on the allow-list:

* :func:`ld_matrix_region_id` returns ``region_safe_to_id[region]`` — 3f431ab's
  expression, character for character — so the curated->M2 crosswalk is not
  applied and ``run_finemap.input.ld_matrix`` resolves exactly as it did before
  m3-04c. (The crosswalk was built AFR-only,
  ``build_curated_m2_crosswalk.py:145``, while ``ld_panel.EUR[1]`` and the
  ``ld_panel.TRANS`` chain HEAD both template on ``{region_id}`` — so an ungated
  crosswalk reaches straight into EUR's and TRANS's chains.)
* :func:`ld_file_authoritative` renders ``"false"``, and ``run_susie_rss.R``
  then IGNORES the declared ``--ld-file`` entirely, so the loader's candidate
  list is character-for-character the legacy one.

THE FAIL-SAFE DIRECTION IS "CHANGE NOTHING"
-------------------------------------------
Every uncertain answer here — block absent, block malformed, ``enabled: false``,
ancestry unlisted — resolves to LEGACY. This resolver decides which LD **bytes**
a fine-map reads, so "config absent -> assume enabled" would silently repoint a
published fit at a panel nothing in that config declares. Fail-safe is
CALLER-relative and for this caller it means change nothing
(``[[feedback_failsafe_default_is_caller_relative]]``). Same shape, same
rationale, as ``occlusion_lockstep_cli._lockstep_applies``.

THE ALLOW-LIST IS ALSO THE KILL SWITCH
--------------------------------------
There is deliberately no per-run override flag for the authoritative-declared-
panel semantics: a per-run override re-creates the silent path this module
exists to close. ``ld_read_path.enabled: false`` or ``ld_read_path.ancestries:
[]`` in ``config/pipeline.yaml`` restores today's behaviour for every ancestry
in one line.

Pure stdlib, no Snakemake, no I/O — so every branch is unit-testable without
instantiating a workflow (``tests/m3/test_ld_read_path_ancestry_gate.py``).
"""
from __future__ import annotations

__all__ = [
    "ld_read_path_applies",
    "ld_matrix_region_id",
    "ld_file_authoritative",
    "ld_allele_aware",
]

#: Ancestries the declared-LD read path applies to when the block lists none.
#: AFR only: the AoU native-plink panel is the AFR chain head, and it is the one
#: artifact the curated->M2 crosswalk was built for. The EUR chain head is the
#: public UKBB 337k reference, which has no M2 counterpart at all.
_DEFAULT_ANCESTRIES = ["AFR"]


def _ld_read_path_block(config) -> dict:
    """The ``ld_read_path`` config block, or ``{}`` when absent/malformed."""
    try:
        block = config.get("ld_read_path", {})
    except AttributeError:
        return {}
    return dict(block) if isinstance(block, dict) else {}


def ld_read_path_applies(ancestry, config) -> bool:
    """True when the declared-LD read path applies to ``ancestry``.

    False — i.e. LEGACY, change nothing — when the block is absent or empty,
    when ``enabled`` is false, or when ``ancestry`` is not listed.
    """
    block = _ld_read_path_block(config)
    if not block:
        return False
    if not block.get("enabled", True):
        return False
    ancestries = block.get("ancestries", _DEFAULT_ANCESTRIES)
    try:
        listed = {str(a) for a in ancestries}
    except TypeError:
        return False
    return str(ancestry) in listed


def ld_matrix_region_id(region, ancestry, config, curated_to_m2, region_safe_to_id) -> str:
    """The ``region_id`` handed to ``ld_panel.resolve_ld_path``.

    OFF the allow-list this returns ``region_safe_to_id[region]`` — 3f431ab's
    expression, character for character, so the resolved ``input.ld_matrix``
    string cannot move. ON it, the curated->M2 crosswalk applies so the AoU
    panel is reachable at all.

    A region with no crosswalk entry (``status=unmapped`` rows are dropped by
    ``load_curated_to_m2``; ``BMI_Xq24`` is chrX and M2 is autosomes-only per
    D-M2-09) falls through to the legacy value on BOTH sides of the gate.
    """
    legacy = region_safe_to_id[region]
    if not ld_read_path_applies(ancestry, config):
        return legacy
    return curated_to_m2.get(region, legacy)


def ld_file_authoritative(ancestry, config) -> str:
    """The literal value rendered into ``--ld-authoritative``: ``"true"`` or
    ``"false"``.

    A STRING, not a bool: it is interpolated straight into ``run_finemap``'s
    shell and parsed by ``run_susie_rss.R``, which ``stop()``s on any value it
    does not recognise rather than silently defaulting.
    """
    return "true" if ld_read_path_applies(ancestry, config) else "false"


def ld_allele_aware(ancestry, config) -> str:
    """The literal value rendered into ``--ld-allele-aware``: ``"true"`` or
    ``"false"``.

    260805-o7o (m3-04c blast radius, **FINDING H**). ``"true"`` ONLY when the
    ``ld_read_path`` block is enabled, ``ancestry`` is on the SAME allow-list
    that already contains AFR (and not EUR / TRANS), AND ``allele_aware`` is
    explicitly truthy. Two independently-flippable levers, deliberately: the
    allow-list contains the change to an ancestry, and ``allele_aware`` turns
    finding H's fix off on its own without disturbing 260805-23d's
    authoritative-declared-panel mandate.

    Every uncertain answer -- block absent, block malformed, ``enabled: false``,
    ancestry unlisted, ``allele_aware`` sub-key ABSENT, ``allele_aware: false``
    -- is ``"false"``. The caller-relative fail-safe is CHANGE NOTHING
    (``[[feedback_failsafe_default_is_caller_relative]]``): this flag decides
    which LD ROW a z-score is bound to and whether that z is NEGATED, so
    "unspecified -> assume the new join" would silently move published numbers.
    The shipped ``config/pipeline.yaml`` carries the key explicitly and
    ``tests/m3/test_ld_allele_aware_wiring.py`` pins that it does.

    A STRING for the same reason as :func:`ld_file_authoritative`: it is
    interpolated into ``run_finemap``'s shell and parsed by ``run_susie_rss.R``,
    which ``stop()``s on any value it does not recognise.
    """
    if not ld_read_path_applies(ancestry, config):
        return "false"
    return "true" if _ld_read_path_block(config).get("allele_aware") is True else "false"
