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
    "ld_coloc_applies",
    "ld_coloc_join",
    "ld_coloc_ancestries",
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


def ld_coloc_applies(ancestry, config) -> bool:
    """The SINGLE gate for the GWAS x QTL colocalization LD read path.

    260805-w7u (m3-04c blast-radius, **FINDING E**, gate row
    ``m3-04c-BLAST-RADIUS.md:141`` "Any GWAS x QTL colocalization").
    ``qtl_coloc.smk`` is the one LD consumer that was never crosswalked
    (``grep -cE "CURATED_TO_M2|resolve_ld_path|ld_read_path" qtl_coloc.smk`` was
    **0** at ``7b1025d``), so an AFR GWAS fit produced on the AoU panel would be
    colocalized against the *1kG* LD matrix inside one ``coloc.susie``.

    (a) IT IS DELIBERATELY **ONE** LEVER FOR **BOTH** HALVES of the remedy -- the
    resolver route (``_qtl_coloc_ld_input``) and the allele-aware panel<->fit
    join (``run_qtl_coloc.R --ld-allele-join``). Two independently flippable
    levers would permit the state *resolution ON / join OFF*: the coloc job would
    open the AoU panel and then fail to key against it, i.e. it would trade
    silently-WRONG LD for silently-NO LD. That is the same defect wearing a
    different mask, and closing E is not allowed to substitute it. Whoever wants
    to disarm one half must disarm both.

    (b) THE FAIL-SAFE DIRECTION IS **CHANGE NOTHING**. Block absent, block
    malformed, ``enabled: false``, ancestry unlisted, ``coloc`` sub-key absent,
    ``coloc: false``, ``coloc: "true"`` (a YAML string), ``coloc: 1`` -- every
    uncertain answer is ``False`` and the entire coloc path stays byte-identical
    to ``7b1025d`` for EVERY ancestry including AFR (finding E simply stays
    open). ``is True`` rather than truthiness, mirroring :func:`ld_allele_aware`:
    this flag decides which LD **bytes** a published posterior is computed from,
    and Track A is in submission with 1,957 legacy coloc JSONs on disk
    (``[[feedback_failsafe_default_is_caller_relative]]``).

    (c) IT RETURNS A ``bool``, unlike :func:`ld_allele_aware` and
    :func:`ld_file_authoritative`, because BOTH of its consumers are Python --
    ``qtl_coloc.smk``'s input function and the manifest builder's allow-list.
    The R script receives a separately-rendered ``"true"`` / ``"false"`` string
    from :func:`ld_coloc_join`.

    ``ld_read_path.enabled: false``, ``ancestries: []`` and ``coloc: false`` are
    each a one-line kill switch.
    """
    if not ld_read_path_applies(ancestry, config):
        return False
    return _ld_read_path_block(config).get("coloc") is True


def ld_coloc_join(ancestry, config) -> str:
    """The literal value rendered into ``--ld-allele-join``: ``"true"`` / ``"false"``.

    A STRING for the same reason as :func:`ld_file_authoritative`: it is
    interpolated straight into ``run_qtl_coloc``'s shell and parsed by
    ``run_qtl_coloc.R``, which ``stop()``s on any value it does not recognise
    rather than silently defaulting. Derived from :func:`ld_coloc_applies` so
    there is exactly ONE predicate, not two that can drift.
    """
    return "true" if ld_coloc_applies(ancestry, config) else "false"


def ld_coloc_ancestries(config) -> list:
    """Every ancestry whose coloc LD path the resolver decides, in config order.

    260805-w7u. The ``--resolver-ancestries`` allow-list handed to
    ``build_qtl_coloc_manifest.py``, so the manifest column and
    ``_qtl_coloc_ld_input`` can never disagree about which ancestries are gated.

    ⚠ WHY THIS LIVES HERE AND NOT IN ``qtl_coloc.smk``. The plan's STEP 6 spelled
    this as ``",".join(a for a in config.get("ld_read_path", {}).get(
    "ancestries", []) if ld_coloc_applies(a, config))`` inline in the rule --
    which would have made ``qtl_coloc.smk`` read the ``ld_read_path`` block
    directly, contradicting that same plan's requirement that the ``.smk`` hold
    no second reading of the block (T-w7u-07: a second reader of a config shape
    is a second thing to keep in step, and it agrees TODAY precisely because
    nobody has changed the shape yet). Keeping the enumeration in the module
    that already owns the block satisfies both: the ``.smk`` names no sub-key at
    all, and the DECISION is still exactly one predicate.

    The enumeration is filtered THROUGH :func:`ld_coloc_applies`, so it is not an
    independent answer: with ``enabled: false`` or ``coloc`` absent/false this
    returns ``[]`` even though ``ancestries`` is non-empty.
    """
    block = _ld_read_path_block(config)
    try:
        listed = list(block.get("ancestries", _DEFAULT_ANCESTRIES))
    except TypeError:
        return []
    return [str(a) for a in listed if ld_coloc_applies(str(a), config)]
