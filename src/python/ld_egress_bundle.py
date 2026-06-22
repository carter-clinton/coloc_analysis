#!/usr/bin/env python3
"""ld_egress_bundle.py — m3-02d per-chromosome LD egress bundling helper.

A reusable helper (feedback_extract_reusable_utilities) that groups the M3 LD
compute-cell outputs (.npz summary LD + AF) by chromosome into export bundles
and SPLITS a chromosome's bundle into ``chrN_a`` / ``chrN_b`` sub-bundles when
the summed bytes exceed the project working egress ceiling.

EGRESS CEILING (research Q5 / A2): ``EGRESS_CAP_GB = 50`` is a CONSERVATIVE
PROJECT WORKING CEILING, NOT a documented hard AoU API limit. AoU's real egress
mechanism is an ALERT THRESHOLD + MANUAL RELAXATION at egress-request time (the
real number is confirmed on the first export); 50 GB matches the
.planning/amendments/aou-egress-audit-log.md per-bundle convention ("split chr1
into 1a + 1b due to >50 GB"). The helper mirrors that within-chromosome split
affordance so the production export plan stays under the ceiling.

REQ-AOU-LD-EGRESS: ONLY summary variant×variant LD + allele frequency cross the
AoU egress boundary — nothing individual-level. This helper sizes/groups those
summary artifacts; it never touches genotypes.
REQ-PATH-PARAMETERIZATION: no hardcoded absolute HPC filesystem paths; the cell
inventory + the cap are inputs (the cap defaults to the project working ceiling).
"""
from __future__ import annotations

import math

# Conservative project working egress ceiling (research Q5/A2). NOT a hard AoU
# API cap — AoU uses an alert threshold + manual relaxation, confirmed on first
# export. Matches the aou-egress-audit-log per-bundle 50 GB convention.
EGRESS_CAP_GB = 50
_GB = 1_000_000_000  # decimal GB (matches np.savez_compressed staging sizes)
EGRESS_CAP_BYTES = EGRESS_CAP_GB * _GB


def _norm_chr(chrom) -> str:
    """Normalize a chromosome label to a bare token (strip a 'chr' prefix)."""
    s = str(chrom)
    return s[3:] if s.lower().startswith("chr") else s


def plan_egress_bundles(cell_sizes: list[dict],
                        cap_bytes: int = EGRESS_CAP_BYTES) -> list[dict]:
    """Group compute-cell outputs into per-chromosome egress bundles.

    ``cell_sizes``: an iterable of dicts, each ``{region_id, chr, bytes}`` (the
    summary LD .npz + AF byte size for one compute cell; ``chr`` is the bundle
    key). REQ-AOU-LD-EGRESS: these are summary artifacts only.

    Grouping: sum bytes per chromosome. If a chromosome's summed bytes exceed
    ``cap_bytes`` (default the 50 GB working ceiling), GREEDILY bin-pack its cells
    into ``chrN_a`` / ``chrN_b`` / ... sub-bundles so each sub-bundle's total is
    <= the cap (mirroring the audit-log "split chr1 into 1a + 1b" affordance). A
    chromosome under the cap stays a SINGLE ``chrN`` bundle.

    Returns a list of per-bundle dicts (sorted by chromosome, then sub-bundle):
        {bundle_id, chr, region_ids, total_bytes, n_cells}.
    """
    # Group cells by chromosome, preserving input order within a chromosome.
    by_chr: dict[str, list[dict]] = {}
    for cell in cell_sizes:
        chrom = _norm_chr(cell["chr"])
        by_chr.setdefault(chrom, []).append({
            "region_id": cell["region_id"],
            "bytes": int(cell["bytes"]),
        })

    bundles: list[dict] = []
    # Stable ordering: numeric chromosomes ascending, then non-numeric lexically.
    def _chr_key(c: str):
        return (0, int(c)) if c.isdigit() else (1, c)

    for chrom in sorted(by_chr, key=_chr_key):
        cells = by_chr[chrom]
        total = sum(c["bytes"] for c in cells)
        if total <= cap_bytes:
            bundles.append({
                "bundle_id": f"chr{chrom}",
                "chr": chrom,
                "region_ids": [c["region_id"] for c in cells],
                "total_bytes": total,
                "n_cells": len(cells),
            })
            continue
        # Over the cap: greedily bin-pack into chrN_a / chrN_b / ... sub-bundles.
        sub_bundles: list[dict] = []
        cur_ids: list[str] = []
        cur_bytes = 0
        for c in cells:
            # A single cell exceeding the cap still occupies its own sub-bundle
            # (the cap cannot be honored for an indivisible cell; flag via size).
            if cur_ids and cur_bytes + c["bytes"] > cap_bytes:
                sub_bundles.append({"region_ids": cur_ids, "total_bytes": cur_bytes})
                cur_ids, cur_bytes = [], 0
            cur_ids.append(c["region_id"])
            cur_bytes += c["bytes"]
        if cur_ids:
            sub_bundles.append({"region_ids": cur_ids, "total_bytes": cur_bytes})
        for i, sub in enumerate(sub_bundles):
            suffix = chr(ord("a") + i) if i < 26 else f"_{i}"
            bundles.append({
                "bundle_id": f"chr{chrom}_{suffix}",
                "chr": chrom,
                "region_ids": sub["region_ids"],
                "total_bytes": sub["total_bytes"],
                "n_cells": len(sub["region_ids"]),
            })
    return bundles


def bundle_gib(bundle: dict) -> float:
    """Bundle total in decimal GiB-ish GB (bytes / 1e9), for memo reporting."""
    return bundle["total_bytes"] / _GB


def n_bundles_over_cap(bundles: list[dict],
                       cap_bytes: int = EGRESS_CAP_BYTES) -> int:
    """Count bundles still exceeding the cap (only an indivisible single cell can)."""
    return sum(1 for b in bundles if b["total_bytes"] > cap_bytes)


def chromosomes_split(bundles: list[dict]) -> list[str]:
    """Chromosomes that were split into >1 sub-bundle (carry an ``_`` suffix)."""
    multi: dict[str, int] = {}
    for b in bundles:
        multi[b["chr"]] = multi.get(b["chr"], 0) + 1
    return [c for c, n in multi.items() if n > 1]
