"""ld_panel.py — M3 Wave 0 LD-panel path resolver.

Single function ``resolve_ld_path(region_id, ancestry, config)``: walk the
ordered fallback chain configured under ``config['ld_panel'][ancestry]`` and
return the first existing ``.rds`` path for the requested region × ancestry
cell. Honors a per-ancestry ``pin`` override and a global ``strict_aou_only``
flag.

Source: RESEARCH.md Q7 (verbatim function body); D-M3-05 (M2 supersede chain
explains why AFR_aou is the chain head while AFR_hgdp/AFR_1kg remain available
during the staged Wave-4 production rollout).

Consumed by ``src/snakemake/rules/finemap.smk`` (Wave 3 wires this in; M3 Wave
0 only lands the helper + pytest scaffold).
"""
from __future__ import annotations

from pathlib import Path

__all__ = ["is_aou_source", "resolve_ld_path"]

#: Token that marks a chain source as AoU-derived.
_AOU_SOURCE_TOKEN = "aou"


def is_aou_source(source: str) -> bool:
    """True when *source* names an AoU-derived panel, ANYWHERE in the name.

    DELIBERATELY NOT ``endswith("_aou")``. The TRANS chain head is
    ``TRANS_aou_eur`` -- ancestry-of-panel LAST -- so the suffix test returned
    False and ``strict_aou_only`` was PROVABLY BLIND to it (m3-04c blast
    radius, finding G). The removal note for ``build_ld_rds_aou_eur`` verified
    that the RULE NAME had no references; it never checked the ARTIFACT PATH,
    so the TRANS head outlived its producer.

    Split on ``_`` and test for the EXACT token, so this cannot widen
    accidentally onto a source that merely CONTAINS the letters (``EUR_aoudad``).

    Verdicts on the shipped chains (config/pipeline.yaml ``ld_panel`` block)::

        EUR_ukbb_pub  False | EUR_aou        True
        EUR_ukbb      False | AFR_aou        True
        EUR_1kg       False | TRANS_aou_eur  True   <- was False before finding G
        AFR_hgdp      False | AFR_1kg        False

    Pinned by ``tests/m3/test_ld_panel_aou_orphan_and_strict.py``, which
    asserts the True-set as an EQUALITY over the REAL shipped chains (a widened
    predicate fails) and carries the orphan registry.
    """
    return _AOU_SOURCE_TOKEN in str(source).split("_")


def resolve_ld_path(
    region_id: str,
    ancestry: str,
    config: dict,
    region_safe: str | None = None,
) -> Path:
    """Walk the ``config['ld_panel'][ancestry]`` fallback chain.

    Substitutes ``{region_id}`` and ``{region_safe}`` placeholders in each
    chain entry's path template **independently**. The legacy Track A naming
    convention uses ``region_safe`` slugs (e.g., ``FTO_16q12``) for the
    1kg/HGDP/UKBB tails of the chain; M2 uses sequential ``region_id``
    (e.g., ``m2_region_00067``) for the AoU panel head. The two are
    different naming conventions for the same physical region — the
    upstream caller must supply both so each chain entry resolves to the
    correct on-disk path.

    Precedence: ``pin`` > ``strict_aou_only`` > fallback walk. When ``pin``
    is set, only the pinned chain entry is considered; ``strict_aou_only``
    fires only when the (un-pinned) walk encounters a missing AoU-sourced
    entry (see :func:`is_aou_source` -- an exact ``aou`` TOKEN anywhere in the
    source name, NOT an ``_aou`` suffix; ``TRANS_aou_eur`` is AoU-sourced).

    ⚠ ``pin`` short-circuits AHEAD of ``strict_aou_only``: a pinned chain has
    the other entries filtered out before the walk, so pinning an ancestry to
    a non-AoU source RE-HIDES exactly what strict mode exists to expose.

    Returns the first existing path. Raises:

    * ``ValueError`` if a non-null ``pin[ancestry]`` is set but the pinned
      ``source`` is not in the chain.
    * ``FileNotFoundError`` if ``strict_aou_only`` is true and the AoU-source
      entry for this ancestry is missing.
    * ``FileNotFoundError`` with message "No LD panel found ..." if no entry
      in the chain resolves to an existing path (and strict mode is off).

    Args:
        region_id: M2 manifest ID (e.g., ``m2_region_00067``); substituted
            into ``{region_id}`` placeholders (AoU chain heads).
        ancestry: One of ``AFR``, ``EUR``, ``TRANS`` (per the Q7 chain).
        config: Loaded ``config/pipeline.yaml`` dict; must contain
            ``ld_panel`` block.
        region_safe: Filesystem-safe Track A slug (e.g., ``FTO_16q12``);
            substituted into ``{region_safe}`` placeholders (1kg/HGDP/UKBB
            tails). When ``None`` (back-compat default), falls back to
            ``region_id`` so callers that pre-date the m3-W3 split keep
            working — but this case is only correct when both placeholders
            should resolve to the same value (which is **not** the case
            for the AoU chain head; see CR-001 in the m3 review).

    Returns:
        Resolved ``Path`` (the first existing entry).

    See Also:
        ``config/pipeline.yaml`` ``ld_panel:`` block; D-M3-05 supersede
        rationale.
    """
    if region_safe is None:
        region_safe = region_id
    panel_cfg = config["ld_panel"]
    pin = panel_cfg.get("pin", {}).get(ancestry)
    chain = panel_cfg[ancestry]
    if pin is not None:
        chain = [c for c in chain if c["source"] == pin]
        if not chain:
            raise ValueError(f"pin {pin!r} not in {ancestry} chain")
    for entry in chain:
        path_str = entry["path"].format(region_id=region_id, region_safe=region_safe)
        path = Path(path_str)
        if path.exists():
            return path
        if panel_cfg.get("strict_aou_only", False) and is_aou_source(entry["source"]):
            raise FileNotFoundError(
                f"strict_aou_only: {ancestry} AoU panel missing for {region_id} "
                f"(expected at {path})"
            )
    raise FileNotFoundError(f"No LD panel found for {region_id} {ancestry}")
