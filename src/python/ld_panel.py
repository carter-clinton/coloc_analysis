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

__all__ = ["resolve_ld_path"]


def resolve_ld_path(region_id: str, ancestry: str, config: dict) -> Path:
    """Walk the ``config['ld_panel'][ancestry]`` fallback chain.

    Substitutes ``{region_id}`` and ``{region_safe}`` placeholders in each
    chain entry's path template. The legacy Track A naming convention used
    ``region_safe`` slugs (e.g., ``FTO_16q12``) while M2 uses sequential
    ``region_id`` (e.g., ``m2_region_00067``); both are substituted to the
    same value here, with the upstream caller responsible for translating
    between the two via ``config/region_id_mapping.tsv`` (RESEARCH O6).

    Returns the first existing path. Raises:

    * ``ValueError`` if a non-null ``pin[ancestry]`` is set but the pinned
      ``source`` is not in the chain.
    * ``FileNotFoundError`` if ``strict_aou_only`` is true and the AoU-source
      entry for this ancestry is missing.
    * ``FileNotFoundError`` with message "No LD panel found ..." if no entry
      in the chain resolves to an existing path (and strict mode is off).

    Args:
        region_id: M2 manifest ID (e.g., ``m2_region_00067``).
        ancestry: One of ``AFR``, ``EUR``, ``TRANS`` (per the Q7 chain).
        config: Loaded ``config/pipeline.yaml`` dict; must contain
            ``ld_panel`` block.

    Returns:
        Resolved ``Path`` (the first existing entry).

    See Also:
        ``config/pipeline.yaml`` ``ld_panel:`` block; D-M3-05 supersede
        rationale.
    """
    panel_cfg = config["ld_panel"]
    pin = panel_cfg.get("pin", {}).get(ancestry)
    chain = panel_cfg[ancestry]
    if pin is not None:
        chain = [c for c in chain if c["source"] == pin]
        if not chain:
            raise ValueError(f"pin {pin!r} not in {ancestry} chain")
    for entry in chain:
        path_str = entry["path"].format(region_id=region_id, region_safe=region_id)
        path = Path(path_str)
        if path.exists():
            return path
        if panel_cfg.get("strict_aou_only", False) and entry["source"].endswith("_aou"):
            raise FileNotFoundError(
                f"strict_aou_only: {ancestry} AoU panel missing for {region_id} "
                f"(expected at {path})"
            )
    raise FileNotFoundError(f"No LD panel found for {region_id} {ancestry}")
