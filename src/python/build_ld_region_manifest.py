#!/usr/bin/env python3
"""build_ld_region_manifest.py — M3 Wave 0 region manifest reformatter.

Reads the M2 deliverable ``results/regions/union_region_list.bed`` (161 GRCh37
regions, 8 columns: chr/start/end/region_id/score/strand/provenance_json/lead_token)
and emits a 322-row (region × ancestry) GRCh38-native manifest in the
AOU-LD-PIPELINE.md §6 schema, extended with per-region ``radius_bp``,
``region_class``, and ``liftover_status`` columns.

Algorithmic anchors (RESEARCH.md):

* Q1 — Liftover at the reformatter (one-shot via ``pyliftover``); emit BOTH
  GRCh37 (provenance) AND GRCh38 (AoU-side input) coordinate columns.
* Q2 — Per-region ``radius_bp = min((end_grch38 - start_grch38) + 500_000,
  50_000_000)``; ``region_class`` ∈ {small ≤ 5 Mb, medium ≤ 25 Mb, large ≤
  50 Mb, xlarge > 50 Mb}.

D-M3-02 — every M2 region is duplicated for AFR + EUR (322 rows total).

This module is consumed by the Wave 0 Snakemake pipeline (out of scope for
this task); the dev-subset selector at ``src/python/select_ld_regions_dev.py``
filters the manifest output, and the AoU driver at ``src/python/aou_ld_panel.py``
consumes it inside the AoU Workbench.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import pandas as pd

# Ancestries to emit per M2 region (D-M3-02). EUR/AFR only — TRANS LD is
# resolved via the EUR_aou panel per Q7 fallback chain (TRANS_aou_eur).
ANCESTRIES = ("AFR", "EUR")

# Per-region radius algorithm (RESEARCH Q2)
RADIUS_SAFETY_MARGIN_BP = 500_000
RADIUS_HARD_CAP_BP = 50_000_000

# WR-01 guard (2026-06-19): the buffer default = the parent region radius (up to
# 50 Mb). For an xlarge parent a 50 Mb buffer makes each compute window
# core + 2*buffer ~= the WHOLE parent span -> the per-window dense scratch
# regresses to the ~65 GiB master-crash / "intractable" wall the split exists to
# fix (project_state: dev-10 KILLED). We do NOT unilaterally pick a scientific
# band width (m3-02c's cost probe owns that measurement); instead we make the
# SILENT parent-spanning-window failure mode IMPOSSIBLE. If the radius-based
# DEFAULT (no explicit --subregion-buffer-mb) yields a window whose span reaches
# this fraction of the parent span, the build RAISES and tells the user to pass
# an explicit --subregion-buffer-mb (the Pan-UKBB AFR/EUR anchor bands at 10 Mb).
# An explicit override is always honored (so m3-02c can widen + measure).
SUBREGION_WINDOW_PARENT_SPAN_GUARD_FRAC = 0.90

# region_class thresholds (RESEARCH Q2 + Q5 Path A.1/A.2/A.3)
CLASS_SMALL_MAX_MB = 5
CLASS_MEDIUM_MAX_MB = 25
CLASS_LARGE_MAX_MB = 50

# m3-W2 re-scope (Q-RS3, REVISED to overlapping windows per m3-REVIEWS HIGH#1):
# xlarge regions are split at manifest-build time into N overlapping-window
# COMPUTE rows so each compute window's dense scratch is bounded (no 65 GiB
# master crash). Each sub-region owns a NON-OVERLAPPING half-open CORE interval
# [core_start_k, core_end_k); the COMPUTE WINDOW = core extended by buffer_bp on
# EACH side. The cores tile the parent exactly; the compute windows overlap by
# buffer_bp so cross-core variant pairs within the band are computed by both.
DEFAULT_MAX_SUBREGION_SPAN_MB = 10.0
DEFAULT_SPLIT_CLASSES = "xlarge"
# Default banding buffer = the region radius (min(core_span + 500kb, 50Mb)) when
# --subregion-buffer-mb is not given. The buffer is the band/buffer knob and the
# single cost-vs-correctness lever; the m3-02c cost probe measures its real cost
# and the radius-narrow-to-10Mb Pan-UKBB lever is the YELLOW disposition.

# AOU §6 manifest schema, extended with structural columns from RESEARCH Q2 +
# the m3-W2 split provenance columns (Q-RS3 overlapping-window split).
MANIFEST_COLUMNS = [
    "region_id",
    "chr",
    "start_grch37",
    "end_grch37",
    "start_grch38",
    "end_grch38",
    "ancestry",
    "source_trait",
    "lead_variant",
    "parent_region_id",
    "subregion_index",
    "n_subregions",
    "core_start_grch38",
    "core_end_grch38",
    "window_start_grch38",
    "window_end_grch38",
    "buffer_bp",
    "radius_bp",
    "region_class",
    "liftover_status",
]


def _parse_buffer_by_ancestry(spec: "str | None") -> "dict[str, float] | None":
    """Parse a ``ANC:MB,ANC:MB`` per-ancestry buffer spec into ``{anc: mb_float}``.

    Returns None for an empty/None spec (the global single-knob path stays in
    effect). The locked M3 spec is ``"AFR:3,EUR:5"``. The values are CLI inputs,
    NOT hardcoded constants — this just parses them.
    """
    if spec is None:
        return None
    spec = spec.strip()
    if not spec:
        return None
    out: dict[str, float] = {}
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise ValueError(
                f"--subregion-buffer-mb-by-ancestry entry {part!r} is not ANC:MB"
            )
        anc, mb = part.split(":", 1)
        anc = anc.strip()
        try:
            out[anc] = float(mb.strip())
        except ValueError as e:
            raise ValueError(
                f"--subregion-buffer-mb-by-ancestry buffer for {anc!r} is not a "
                f"number: {mb!r}"
            ) from e
    return out or None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bed", required=False, default=None, type=Path,
                   help="M2 union BED (GRCh37, 8 columns; results/regions/union_region_list.bed). "
                        "Required UNLESS --split-existing-manifest is given (XOR).")
    p.add_argument("--chain", required=False, default=None, type=Path,
                   help="UCSC GRCh37 to GRCh38 chain (data/external/liftover/hg19ToHg38.over.chain.gz). "
                        "Required UNLESS --split-existing-manifest is given (XOR).")
    p.add_argument("--split-existing-manifest", dest="split_existing_manifest",
                   required=False, default=None, type=Path,
                   help="Path B regen: split an EXISTING committed manifest TSV in place "
                        "(no --bed/--chain; the forward chain + M2 union BED are gone). "
                        "Mutually exclusive with --bed/--chain.")
    p.add_argument("--out-manifest", required=True, type=Path,
                   help="Output 322-row TSV (config/ld_regions.tsv)")
    p.add_argument("--out-projection", required=True, type=Path,
                   help="Output 162-row per-region projection TSV (m3-region-class-projection.tsv)")
    p.add_argument("--out-mapping", required=False, type=Path, default=None,
                   help="Optional region_id <-> region_safe mapping TSV (RESEARCH O6)")
    p.add_argument("--ancestries", default=",".join(ANCESTRIES),
                   help="Comma-separated ancestry tokens to emit per region (default AFR,EUR)")
    p.add_argument("--max-subregion-span-mb", type=float,
                   default=DEFAULT_MAX_SUBREGION_SPAN_MB,
                   help="CORE window bp width in Mb for splitting xlarge regions; "
                        "Q-RS3 density anchor 10 Mb ~= 69k AFR var < 75k. The cores "
                        "tile the parent exactly (half-open); each compute WINDOW = "
                        "core +/- --subregion-buffer-mb.")
    p.add_argument("--split-classes", default=DEFAULT_SPLIT_CLASSES,
                   help="Comma-separated region_class values to split into overlapping "
                        "sub-region compute rows (default 'xlarge'; only xlarge splits).")
    p.add_argument("--subregion-buffer-mb", type=float, default=None,
                   help="Banding buffer in Mb added to EACH side of a core to form the "
                        "compute window; the band/buffer width and the single "
                        "cost-vs-correctness knob (buffer_bp). Default = the region radius "
                        "min(core_span+500kb, 50Mb). The Pan-UKBB anchor bands at 10 Mb; "
                        "the m3-02c cost probe measures this buffer's real cost and the "
                        "narrow-to-10Mb lever is the YELLOW disposition. DO NOT silently "
                        "keep 50 Mb. This is the GLOBAL (single, all-ancestry) knob; for "
                        "an ancestry-specific buffer use --subregion-buffer-mb-by-ancestry.")
    p.add_argument("--subregion-buffer-mb-by-ancestry",
                   dest="subregion_buffer_mb_by_ancestry", type=str, default=None,
                   help="PER-ANCESTRY banding buffer as a comma-separated ANC:MB mapping "
                        "(e.g. 'AFR:3,EUR:5'). When given, it OVERRIDES --subregion-buffer-mb "
                        "for the named ancestries; an unnamed ancestry falls back to "
                        "--subregion-buffer-mb (or the region radius if neither is given). "
                        "Each ancestry's compute window = core +/- ITS buffer, so an AFR "
                        "__sub row and the matching EUR __sub row carry DIFFERENT "
                        "window_start/window_end/buffer_bp while the half-open CORES (which "
                        "are buffer-independent) stay identical across ancestries. "
                        "The LOCKED M3 value (Carter 2026-06-22, per-ancestry LD-decay scale) "
                        "is 'AFR:3,EUR:5' with --max-subregion-span-mb 5. These 3/5 numbers "
                        "are CLI parameters threaded through the build, NOT hardcoded library "
                        "constants.")
    args = p.parse_args(argv)
    # Parse the per-ancestry buffer mapping into {ancestry: buffer_mb_float}.
    args.subregion_buffer_mb_by_ancestry = _parse_buffer_by_ancestry(
        args.subregion_buffer_mb_by_ancestry
    )
    # XOR: split-existing mode vs. bed/chain mode. Enforce mutual exclusion +
    # the required-inputs-present check via argparse-native p.error().
    if args.split_existing_manifest is not None:
        if args.bed is not None or args.chain is not None:
            p.error("--split-existing-manifest is mutually exclusive with --bed/--chain")
    else:
        if not (args.bed is not None and args.chain is not None):
            p.error("either --split-existing-manifest OR both --bed and --chain are required")
    return args


def parse_provenance(prov_str: str) -> dict:
    """Parse the M2 BED column 7 provenance JSON.

    The M2 builder emits the JSON wrapped in literal double quotes which BED
    column-quoting doubles into ``""``. Strip quotes + collapse doubled quotes
    before json.loads.
    """
    s = prov_str.strip()
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    s = s.replace('""', '"')
    return json.loads(s)


def derive_source_trait_and_lead(prov: dict, ancestry: str) -> tuple[str, str]:
    """Return (source_trait, lead_variant) for a region × ancestry cell.

    M2 provenance does NOT carry per-trait lead variants in the BED (D-M2-09);
    the lead variant is resolved at AoU-side cohort definition time. We emit
    ``source_trait`` derived from the first ancestry-matching MTAG entry (most
    informative); ``lead_variant`` is left as ``NA`` to be filled by Wave 1.
    """
    mtag = prov.get("mtag", []) or []
    # Match per-stratum: e.g. 'bmi.AFR.PAGE.2019.AFR' for AFR, 'bmi.EUR.*' for EUR.
    for entry in mtag:
        # entry format: trait.stratum.cohort.year.ancestry  (e.g. bmi.AFR.PAGE.2019.AFR)
        parts = entry.split(".")
        if len(parts) >= 2 and parts[1] == ancestry:
            return entry, "NA"
    # Fall back to first MTAG entry (TRANS-stratum traits are routed through EUR panel)
    if mtag:
        return mtag[0], "NA"
    # Then clump
    clump = prov.get("clump", []) or []
    for entry in clump:
        if entry.endswith(f".{ancestry}"):
            return entry, "NA"
    if clump:
        return clump[0], "NA"
    # Then cpassoc
    cp = prov.get("cpassoc", []) or []
    if cp:
        return cp[0], "NA"
    return "NA", "NA"


def _find_mappable(chain, chrom: str, pos: int, direction: int,
                   max_step_bp: int = 1_000_000, step_size_bp: int = 1_000) -> tuple[int | None, list]:
    """Walk inward (direction=+1) or outward (-1) from pos in step_size_bp
    increments until convert_coordinate returns at least one hit on ``chrom``.

    Returns (probe_pos, hits) on success or (None, []) after max_step_bp.

    Rationale: M2 union regions are wide (median 9 Mb) and often span centromeres
    or other unmappable gaps where the exact endpoint has no liftover hit. The
    correct behavior for region-bound liftover is to walk the endpoint inward
    until a mappable site is found — this preserves the spatial envelope of the
    region rather than dropping the entire region.
    """
    walked = 0
    probe = pos
    while walked <= max_step_bp:
        hits = chain.convert_coordinate(chrom, probe)
        same = [h for h in (hits or []) if h[0] == chrom]
        if same:
            return probe, same
        probe += direction * step_size_bp
        if probe < 0:
            break
        walked += step_size_bp
    return None, []


def liftover_region(chain, contig: str, start: int, end: int) -> tuple[int | None, int | None, str]:
    """Liftover BED-style half-open interval (start, end) GRCh37 -> GRCh38.

    Returns (new_start, new_end, status). Status ∈ {primary, multi-segment, failed}.

    Algorithm:
    1. Try direct liftover of both endpoints.
    2. If either endpoint has no hit on the same chromosome, walk INWARD in
       1 kb steps up to 1 Mb to find a nearby mappable site (status =>
       "multi-segment" to flag the offset). This handles M2's wide regions
       whose endpoints land in centromeres / unmappable gaps in GRCh38.
    3. If still unmappable after walking, the region's status is "failed".
    """
    chrom = contig if contig.startswith("chr") else f"chr{contig}"
    # BED start is 0-based; end is exclusive. Liftover (end - 1) to stay within
    # the original interval, then add +1 to the resulting position.
    start_probe = start
    end_probe = max(end - 1, start)

    direct_start = chain.convert_coordinate(chrom, start_probe) or []
    direct_end = chain.convert_coordinate(chrom, end_probe) or []
    start_same = [h for h in direct_start if h[0] == chrom]
    end_same = [h for h in direct_end if h[0] == chrom]

    walked_start = walked_end = False
    if not start_same:
        _, start_same = _find_mappable(chain, chrom, start_probe, direction=+1)
        walked_start = bool(start_same)
    if not end_same:
        _, end_same = _find_mappable(chain, chrom, end_probe, direction=-1)
        walked_end = bool(end_same)

    if not start_same or not end_same:
        return None, None, "failed"

    new_starts = [h[1] for h in start_same]
    new_ends = [h[1] + 1 for h in end_same]
    new_start = min(new_starts)
    new_end = max(new_ends)

    # Handle the inversion / rearrangement case where the chain maps the
    # endpoints to coordinates whose order is reversed. Walk inward from
    # the rearranged endpoint (max 5 Mb) to find a position that preserves
    # start < end while staying within the original spatial envelope.
    if new_end <= new_start:
        # First, try walking the END further inward (toward start_probe)
        for step in (50_000, 250_000, 1_000_000, 2_500_000, 5_000_000):
            probe = max(end_probe - step, start_probe + 1)
            hits = chain.convert_coordinate(chrom, probe) or []
            same = [h for h in hits if h[0] == chrom and (h[1] + 1) > new_start]
            if same:
                new_ends = [h[1] + 1 for h in same]
                new_end = max(new_ends)
                walked_end = True
                break
        if new_end <= new_start:
            # Try walking the START further inward (toward end_probe)
            for step in (50_000, 250_000, 1_000_000, 2_500_000, 5_000_000):
                probe = min(start_probe + step, end_probe - 1)
                hits = chain.convert_coordinate(chrom, probe) or []
                same = [h for h in hits if h[0] == chrom and h[1] < new_end]
                if same:
                    new_starts = [h[1] for h in same]
                    new_start = min(new_starts)
                    walked_start = True
                    break
        if new_end <= new_start:
            return None, None, "failed"

    multi = (
        walked_start or walked_end
        or len(start_same) > 1 or len(end_same) > 1
    )
    status = "multi-segment" if multi else "primary"
    return new_start, new_end, status


def compute_radius_bp(start_b38: int, end_b38: int) -> int:
    """Per-region radius (RESEARCH Q2). Capped at 50 Mb."""
    span = end_b38 - start_b38
    raw = span + RADIUS_SAFETY_MARGIN_BP
    return min(raw, RADIUS_HARD_CAP_BP)


def derive_region_class(start_b38: int, end_b38: int) -> str:
    """region_class per RESEARCH Q2 / Q5 thresholds."""
    span_mb = (end_b38 - start_b38) / 1_000_000
    if span_mb <= CLASS_SMALL_MAX_MB:
        return "small"
    if span_mb <= CLASS_MEDIUM_MAX_MB:
        return "medium"
    if span_mb <= CLASS_LARGE_MAX_MB:
        return "large"
    return "xlarge"


def split_region_overlapping(
    start_b38: int,
    end_b38: int,
    core_span_bp: int,
    buffer_bp: int,
) -> list[dict]:
    """Split [start_b38, end_b38) into N overlapping-window sub-regions (Q-RS3).

    HALF-OPEN CORE semantics (load-bearing): each sub-region owns a
    NON-OVERLAPPING core ownership interval ``[core_start_k, core_end_k)``.
    A variant exactly at ``core_end_k`` belongs to the NEXT core, never this
    one. The cores tile ``[start_b38, end_b38)`` exactly — no gap, no overlap;
    ``core_0.start == start_b38`` and ``core_{N-1}.end == end_b38`` (the last
    core absorbs the integer remainder).

    The COMPUTE WINDOW for core_k is the core extended by ``buffer_bp`` on EACH
    side, clamped to the parent:
        window_k = [max(start_b38, core_start_k - buffer_bp),
                    min(end_b38,   core_end_k   + buffer_bp))
    Adjacent windows OVERLAP by ~buffer_bp so every cross-core variant pair
    within ``buffer_bp`` is computed by BOTH neighbouring windows (the stitch
    reconciles the duplicate pair). The compute row's start/end = the WINDOW so
    ``compute_region_ld`` computes the cross-core band.

    Returns a list of N dicts, each:
        {subregion_index, n_subregions, core_start, core_end,
         window_start, window_end}
    """
    if end_b38 <= start_b38:
        raise ValueError(f"empty region for split: [{start_b38}, {end_b38})")
    if core_span_bp <= 0:
        raise ValueError(f"core_span_bp must be positive, got {core_span_bp}")

    total = end_b38 - start_b38
    n = max(1, math.ceil(total / core_span_bp))
    # Equal integer-width cores tiling [start, end); the last core absorbs the
    # remainder so core_{N-1}.end == end_b38 exactly.
    base = total // n
    subs: list[dict] = []
    cursor = start_b38
    for k in range(n):
        core_start = cursor
        if k == n - 1:
            core_end = end_b38
        else:
            core_end = core_start + base
        cursor = core_end
        window_start = max(start_b38, core_start - buffer_bp)
        window_end = min(end_b38, core_end + buffer_bp)
        subs.append({
            "subregion_index": k,
            "n_subregions": n,
            "core_start": core_start,
            "core_end": core_end,
            "window_start": window_start,
            "window_end": window_end,
        })
    return subs


def derive_region_safe(region_id: str, contig: str, start_b38: int, end_b38: int) -> str:
    """Best-effort region_safe (filesystem-safe slug) for the optional mapping table.

    M2 IDs are already filesystem-safe (m2_region_NNNNN). Track A used curated
    slugs (FTO_16q12). The mapping table is hand-curated for the 11 Track A
    overlaps (built separately in select_ld_regions_dev.py + companion task);
    here we just emit a synthetic region_safe = ``r{NNNNN}_{chr}_{start_mb}_{end_mb}``
    pattern matching AOU §6 example.
    """
    n = region_id.replace("m2_region_", "")
    return f"r{n}_{contig}_{start_b38}_{end_b38}"


def load_chain(chain_path: Path):
    """Load UCSC chain via pyliftover."""
    from pyliftover import LiftOver

    if not chain_path.exists():
        raise FileNotFoundError(f"chain file missing: {chain_path}")
    return LiftOver(str(chain_path))


def read_union_bed(bed_path: Path) -> pd.DataFrame:
    """Read M2 union BED. 8 columns, no header, tab-separated.

    Columns: chr, start, end, region_id, score, strand, provenance_json, lead_token (optional).
    Some rows have only 7 columns (no lead_token); pad to 8 for uniformity.
    """
    rows = []
    with bed_path.open() as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                raise ValueError(f"BED row has < 7 columns: {line[:200]}")
            if len(parts) == 7:
                parts.append("")
            rows.append(parts[:8])
    df = pd.DataFrame(rows, columns=["chr", "start", "end", "region_id", "score",
                                     "strand", "provenance_json", "lead_token"])
    df["start"] = df["start"].astype(int)
    df["end"] = df["end"].astype(int)
    return df


def _path_a_for_class(region_class: str) -> tuple[str, float]:
    """RESEARCH Q5: small->A.1, medium->A.2, large/xlarge->A.3 + est cluster-hours."""
    if region_class == "small":
        return "A.1", 0.5  # 15-25 min mid
    if region_class == "medium":
        return "A.2", 1.5
    if region_class == "large":
        return "A.3", 8.0
    return "A.3", 24.0


def _assemble_region_rows(
    *,
    region_id: str,
    chr_int_str: str,
    start_b37: int,
    end_b37: int,
    start_b38: int,
    end_b38: int,
    region_class: str,
    radius_bp: int,
    status: str,
    ancestries: list[str],
    trait_lead_fn,
    split_set: set,
    core_span_bp: int,
    buffer_override_bp: "int | None",
    buffer_override_bp_by_ancestry: "dict[str, int] | None" = None,
) -> tuple[list[dict], list[dict]]:
    """Assemble (manifest_rows, projection_rows) for ONE successfully-resolved
    GRCh38 region — the SHARED single-source-of-geometry helper called by BOTH
    ``build_manifest`` (post-liftover) and ``split_existing_manifest`` (reading
    the GRCh38 coords straight from an existing manifest row).

    ``trait_lead_fn(ancestry) -> (source_trait, lead_variant)`` resolves per-cell
    provenance. The caller supplies GRCh38 coords/class/radius/grch37/status; this
    helper owns the SPLIT-vs-WHOLE decision, the overlapping-window geometry, the
    WR-01 SUBREGION_BUFFER_GUARD, and the whole-region convention columns. The
    failed-liftover projection branch stays in ``build_manifest`` (liftover-specific,
    never shared).
    """
    path_a, est_hrs = _path_a_for_class(region_class)
    span_bp = end_b38 - start_b38
    manifest_rows: list[dict] = []
    projection_rows: list[dict] = []

    if region_class in split_set:
        # SPLIT branch: overlapping-window sub-regions. The banding buffer is
        # resolved PER ANCESTRY (m3-02d): an explicit per-ancestry override wins,
        # else the global scalar override, else the parent region radius (the band
        # knob). Each ancestry's compute WINDOW = core +/- ITS buffer, so an AFR
        # __sub row and the matching EUR __sub row may carry DIFFERENT
        # window_start/window_end/buffer_bp. The half-open CORES are
        # buffer-INDEPENDENT (split_region_overlapping tiles on core_span_bp only),
        # so they are byte-identical across ancestries — only the windows differ.
        by_anc = buffer_override_bp_by_ancestry or {}

        def _buffer_for(ancestry: str) -> int:
            if ancestry in by_anc:
                return int(by_anc[ancestry])
            if buffer_override_bp is not None:
                return int(buffer_override_bp)
            return int(radius_bp)

        # The CORE tiling is buffer-independent (window-only depends on buffer), so
        # compute it ONCE (n_sub + the per-sub cores are shared across ancestries).
        ref_subs = split_region_overlapping(
            start_b38, end_b38, core_span_bp, _buffer_for(ancestries[0])
        )
        n_sub = len(ref_subs)

        # WR-01 guard: refuse to SILENTLY emit a parent-spanning compute window
        # from the radius-based DEFAULT buffer (the 65 GiB master-crash condition).
        # Only fires when NEITHER an explicit per-ancestry NOR a global buffer was
        # given for an ancestry AND that ancestry's widest window reaches ~the whole
        # parent span. An explicit buffer (per-ancestry or global) is always honored
        # (the locked 3/5 Mb buffers bypass it). Checked per ancestry.
        for ancestry in ancestries:
            explicit = (ancestry in by_anc) or (buffer_override_bp is not None)
            if explicit or n_sub <= 1:
                continue
            anc_subs = split_region_overlapping(
                start_b38, end_b38, core_span_bp, _buffer_for(ancestry)
            )
            widest_window = max(s["window_end"] - s["window_start"] for s in anc_subs)
            if widest_window >= SUBREGION_WINDOW_PARENT_SPAN_GUARD_FRAC * span_bp:
                raise ValueError(
                    f"SUBREGION_BUFFER_GUARD: region {region_id} "
                    f"({region_class}, {span_bp/1e6:.1f} Mb) split into {n_sub} "
                    f"sub-regions, but the DEFAULT buffer for ancestry {ancestry} "
                    f"({_buffer_for(ancestry)/1e6:.1f} Mb = the parent radius) makes "
                    f"the widest compute window {widest_window/1e6:.1f} Mb "
                    f">= {SUBREGION_WINDOW_PARENT_SPAN_GUARD_FRAC:.0%} of the "
                    f"parent span -- a parent-spanning window whose dense "
                    f"scratch regresses to the ~65 GiB intractable wall the "
                    f"split exists to avoid. Pass an explicit "
                    f"--subregion-buffer-mb (or --subregion-buffer-mb-by-ancestry; "
                    f"the locked M3 buffers are AFR:3,EUR:5 Mb; m3-02c's cost probe "
                    f"measures the correct width). Refusing to silently keep the "
                    f"50 Mb default."
                )

        # Parent projection row (NOT a compute row). radius_bp = the parent radius.
        projection_rows.append({
            "region_id": region_id,
            "chr": chr_int_str,
            "start_grch37": start_b37,
            "end_grch37": end_b37,
            "start_grch38": start_b38,
            "end_grch38": end_b38,
            "span_bp_grch38": span_bp,
            "span_mb_grch38": round(span_bp / 1_000_000, 3),
            "region_class": region_class,
            "radius_bp": radius_bp,
            "path_a_class": path_a,
            "est_cluster_hours_per_ancestry": est_hrs,
            "split_status": "parent",
            "n_subregions": n_sub,
            "liftover_status": status,
        })

        # Per (subregion_index, ancestry): compute THAT ancestry's window geometry
        # and emit a compute row carrying that ancestry's window + buffer_bp. The
        # PROJECTION carries ONE sub row per subregion_index (the logical split
        # structure the cost model's three-totals counts over); its geometry uses
        # the WIDEST ancestry window (a conservative envelope) so the projection's
        # span/est stays an upper bound. The per-ANCESTRY geometry the cost model
        # consumes per-cell lives in the MANIFEST compute rows (each carries its own
        # ancestry's window_start/window_end/buffer_bp).
        anc_subs_by_anc = {
            ancestry: split_region_overlapping(
                start_b38, end_b38, core_span_bp, _buffer_for(ancestry)
            )
            for ancestry in ancestries
        }
        widest_anc = max(ancestries, key=_buffer_for)
        for k in range(n_sub):
            sub_id = f"{region_id}__sub{k:02d}"
            core = ref_subs[k]
            # Projection sub row: widest-ancestry window (conservative envelope).
            wide = anc_subs_by_anc[widest_anc][k]
            wstart, wend = wide["window_start"], wide["window_end"]
            wclass = derive_region_class(wstart, wend)
            wpath_a, west = _path_a_for_class(wclass)
            projection_rows.append({
                "region_id": sub_id,
                "chr": chr_int_str,
                "start_grch37": start_b37,
                "end_grch37": end_b37,
                "start_grch38": wstart,
                "end_grch38": wend,
                "span_bp_grch38": wend - wstart,
                "span_mb_grch38": round((wend - wstart) / 1_000_000, 3),
                "region_class": wclass,
                "radius_bp": _buffer_for(widest_anc),
                "path_a_class": wpath_a,
                "est_cluster_hours_per_ancestry": west,
                "split_status": "subregion",
                "n_subregions": n_sub,
                "liftover_status": status,
            })
            for ancestry in ancestries:
                buf_anc = _buffer_for(ancestry)
                sub = anc_subs_by_anc[ancestry][k]
                win_start = sub["window_start"]
                win_end = sub["window_end"]
                win_class = derive_region_class(win_start, win_end)
                source_trait, lead_variant = trait_lead_fn(ancestry)
                manifest_rows.append({
                    "region_id": sub_id,
                    "chr": chr_int_str,
                    "start_grch37": start_b37,
                    "end_grch37": end_b37,
                    "start_grch38": win_start,
                    "end_grch38": win_end,
                    "ancestry": ancestry,
                    "source_trait": source_trait,
                    "lead_variant": lead_variant,
                    "parent_region_id": region_id,
                    "subregion_index": k,
                    "n_subregions": n_sub,
                    "core_start_grch38": core["core_start"],
                    "core_end_grch38": core["core_end"],
                    "window_start_grch38": win_start,
                    "window_end_grch38": win_end,
                    "buffer_bp": buf_anc,
                    "radius_bp": buf_anc,
                    "region_class": win_class,
                    "liftover_status": status,
                })
        return manifest_rows, projection_rows

    # WHOLE branch: one compute row per ancestry + whole-region convention.
    projection_rows.append({
        "region_id": region_id,
        "chr": chr_int_str,
        "start_grch37": start_b37,
        "end_grch37": end_b37,
        "start_grch38": start_b38,
        "end_grch38": end_b38,
        "span_bp_grch38": span_bp,
        "span_mb_grch38": round(span_bp / 1_000_000, 3),
        "region_class": region_class,
        "radius_bp": radius_bp,
        "path_a_class": path_a,
        "est_cluster_hours_per_ancestry": est_hrs,
        "split_status": "whole",
        "n_subregions": 1,
        "liftover_status": status,
    })
    for ancestry in ancestries:
        source_trait, lead_variant = trait_lead_fn(ancestry)
        manifest_rows.append({
            "region_id": region_id,
            "chr": chr_int_str,
            "start_grch37": start_b37,
            "end_grch37": end_b37,
            "start_grch38": start_b38,
            "end_grch38": end_b38,
            "ancestry": ancestry,
            "source_trait": source_trait,
            "lead_variant": lead_variant,
            "parent_region_id": "",
            "subregion_index": -1,
            "n_subregions": 1,
            "core_start_grch38": start_b38,
            "core_end_grch38": end_b38,
            "window_start_grch38": start_b38,
            "window_end_grch38": end_b38,
            "buffer_bp": radius_bp,
            "radius_bp": radius_bp,
            "region_class": region_class,
            "liftover_status": status,
        })
    return manifest_rows, projection_rows


def build_manifest(
    bed_df: pd.DataFrame,
    chain,
    ancestries: list[str],
    max_subregion_span_mb: float = DEFAULT_MAX_SUBREGION_SPAN_MB,
    split_classes: "str | list[str]" = DEFAULT_SPLIT_CLASSES,
    subregion_buffer_mb: "float | None" = None,
    subregion_buffer_mb_by_ancestry: "dict[str, float] | None" = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Expand bed_df × ancestries into the AOU §6 manifest + per-region projection.

    Returns (manifest_df, projection_df). For a region whose ``region_class`` is
    in ``split_classes`` (default ``{"xlarge"}``), the parent is NOT emitted as a
    compute manifest row; instead it is split into N overlapping-window __sub
    compute rows (Q-RS3, REVISED to overlapping windows per m3-REVIEWS HIGH#1):

    * each sub-region owns a half-open CORE interval ``[core_start_k, core_end_k)``;
      the cores tile the parent exactly (no gap/overlap).
    * each compute row's ``start_grch38``/``end_grch38`` = the COMPUTE WINDOW =
      ``[core_start - buffer_bp, core_end + buffer_bp]`` clamped to the parent, so
      ``compute_region_ld`` computes the cross-core pairs within ``buffer_bp``.
    * ``buffer_bp`` is an explicit column AND a CLI param (``--subregion-buffer-mb``);
      default = the region radius ``min(core_span+500kb, 50Mb)``. NOT silently 50 Mb.
    * the parent is emitted into the projection with ``split_status="parent"``;
      each sub-region with ``split_status="subregion"``; whole regions with
      ``split_status="whole"``.

    A non-split region emits exactly ONE manifest row per ancestry with NO
    ``__sub`` suffix and whole-region provenance (parent_region_id="",
    subregion_index=-1, n_subregions=1, core==window==region, buffer_bp=radius).
    """
    if isinstance(split_classes, str):
        split_set = {c.strip() for c in split_classes.split(",") if c.strip()}
    else:
        split_set = set(split_classes)
    core_span_bp = int(round(max_subregion_span_mb * 1_000_000))
    buffer_override_bp = (
        int(round(subregion_buffer_mb * 1_000_000)) if subregion_buffer_mb is not None else None
    )
    buffer_override_bp_by_ancestry = (
        {a: int(round(mb * 1_000_000)) for a, mb in subregion_buffer_mb_by_ancestry.items()}
        if subregion_buffer_mb_by_ancestry else None
    )

    manifest_rows: list[dict] = []
    projection_rows: list[dict] = []
    audit_failures: list[str] = []

    for _, row in bed_df.iterrows():
        contig = row["chr"]
        # Strip 'chr' prefix for the chr column per AOU §6 (column type int 1-22)
        chr_int_str = contig.replace("chr", "")
        start_b37 = int(row["start"])
        end_b37 = int(row["end"])
        region_id = row["region_id"]
        try:
            prov = parse_provenance(row["provenance_json"])
        except Exception as e:
            print(f"WARN: failed to parse provenance for {region_id}: {e}", file=sys.stderr)
            prov = {}

        new_start, new_end, status = liftover_region(chain, contig, start_b37, end_b37)
        if status == "failed":
            audit_failures.append(f"FAILED LIFTOVER: {region_id} {contig}:{start_b37}-{end_b37}")
            print(f"AUDIT: {audit_failures[-1]}", file=sys.stderr)
            # Still emit projection row so the projection captures all 161 regions
            projection_rows.append({
                "region_id": region_id,
                "chr": chr_int_str,
                "start_grch37": start_b37,
                "end_grch37": end_b37,
                "start_grch38": -1,
                "end_grch38": -1,
                "span_bp_grch38": 0,
                "span_mb_grch38": 0.0,
                "region_class": "FAILED",
                "radius_bp": 0,
                "path_a_class": "FAILED",
                "est_cluster_hours_per_ancestry": 0.0,
                "split_status": "failed",
                "n_subregions": 0,
                "liftover_status": "failed",
            })
            continue

        radius_bp = compute_radius_bp(new_start, new_end)
        region_class = derive_region_class(new_start, new_end)

        m_rows, p_rows = _assemble_region_rows(
            region_id=region_id,
            chr_int_str=chr_int_str,
            start_b37=start_b37,
            end_b37=end_b37,
            start_b38=new_start,
            end_b38=new_end,
            region_class=region_class,
            radius_bp=radius_bp,
            status=status,
            ancestries=ancestries,
            trait_lead_fn=lambda a, _prov=prov: derive_source_trait_and_lead(_prov, a),
            split_set=split_set,
            core_span_bp=core_span_bp,
            buffer_override_bp=buffer_override_bp,
            buffer_override_bp_by_ancestry=buffer_override_bp_by_ancestry,
        )
        manifest_rows.extend(m_rows)
        projection_rows.extend(p_rows)

    if audit_failures:
        print(f"AUDIT: {len(audit_failures)} liftover failures (dropped from manifest)",
              file=sys.stderr)

    manifest_df = pd.DataFrame(manifest_rows, columns=MANIFEST_COLUMNS)
    projection_df = pd.DataFrame(projection_rows)
    return manifest_df, projection_df


def split_existing_manifest(
    in_manifest_df: pd.DataFrame,
    *,
    subregion_buffer_mb: "float | None" = None,
    subregion_buffer_mb_by_ancestry: "dict[str, float] | None" = None,
    max_subregion_span_mb: float = DEFAULT_MAX_SUBREGION_SPAN_MB,
    split_classes: "str | list[str]" = DEFAULT_SPLIT_CLASSES,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Path B regen: split an EXISTING (committed) manifest in place.

    The canonical ``--bed``/``--chain`` regen inputs are GONE (the forward
    ``hg19ToHg38`` chain was deleted; the M2 union BED is nowhere on the tree),
    so we split the already-lifted-over GRCh38 manifest directly. This does NOT
    liftover and does NOT recompute radius/region_class — those are carried
    straight from the existing rows (recomputation is impossible without the chain
    AND unnecessary, since the split geometry is GRCh38-only). ``region_class``
    drives the split decision exactly as ``build_manifest``.

    The existing manifest may be the OLD 12-column schema (region_id, chr,
    start_grch37, end_grch37, start_grch38, end_grch38, ancestry, source_trait,
    lead_variant, radius_bp, region_class, liftover_status) — it carries NONE of
    the 8 split-provenance columns. This function OUTPUTS the full 20-column
    ``MANIFEST_COLUMNS`` schema, ADDING the split columns (xlarge -> __sub rows;
    non-xlarge -> whole-region convention) by reusing the SAME
    ``_assemble_region_rows`` helper ``build_manifest`` calls. The __sub geometry
    is therefore byte-identical to ``build_manifest`` for the same coords.

    Returns ``(manifest_df, projection_df)`` — same shape as ``build_manifest``.
    """
    if isinstance(split_classes, str):
        split_set = {c.strip() for c in split_classes.split(",") if c.strip()}
    else:
        split_set = set(split_classes)
    core_span_bp = int(round(max_subregion_span_mb * 1_000_000))
    buffer_override_bp = (
        int(round(subregion_buffer_mb * 1_000_000)) if subregion_buffer_mb is not None else None
    )
    buffer_override_bp_by_ancestry = (
        {a: int(round(mb * 1_000_000)) for a, mb in subregion_buffer_mb_by_ancestry.items()}
        if subregion_buffer_mb_by_ancestry else None
    )

    manifest_rows: list[dict] = []
    projection_rows: list[dict] = []

    # Group by region_id preserving first-seen order; each group = per-ancestry
    # rows for one region.
    for region_id, group in in_manifest_df.groupby("region_id", sort=False):
        first = group.iloc[0]
        # chr column may carry a bare int or a 'chr'-prefixed string; normalize.
        chr_int_str = str(first["chr"]).replace("chr", "")
        start_b37 = int(first["start_grch37"])
        end_b37 = int(first["end_grch37"])
        start_b38 = int(first["start_grch38"])
        end_b38 = int(first["end_grch38"])
        region_class = str(first["region_class"])
        radius_bp = int(first["radius_bp"])
        status = str(first["liftover_status"])

        # Per-ancestry (source_trait, lead_variant) lookup from the group's rows.
        lookup: dict[str, tuple[str, str]] = {}
        for _, r in group.iterrows():
            lookup[str(r["ancestry"])] = (
                str(r["source_trait"]), str(r["lead_variant"])
            )
        # Preserve input ancestry order (AFR then EUR as committed).
        ancestries = list(dict.fromkeys(str(a) for a in group["ancestry"]))

        m_rows, p_rows = _assemble_region_rows(
            region_id=str(region_id),
            chr_int_str=chr_int_str,
            start_b37=start_b37,
            end_b37=end_b37,
            start_b38=start_b38,
            end_b38=end_b38,
            region_class=region_class,
            radius_bp=radius_bp,
            status=status,
            ancestries=ancestries,
            trait_lead_fn=lambda a, _lk=lookup: _lk[a],
            split_set=split_set,
            core_span_bp=core_span_bp,
            buffer_override_bp=buffer_override_bp,
            buffer_override_bp_by_ancestry=buffer_override_bp_by_ancestry,
        )
        manifest_rows.extend(m_rows)
        projection_rows.extend(p_rows)

    manifest_df = pd.DataFrame(manifest_rows, columns=MANIFEST_COLUMNS)
    projection_df = pd.DataFrame(projection_rows)
    return manifest_df, projection_df


def write_tsv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep="\t", index=False)


def write_mapping(manifest_df: pd.DataFrame, projection_df: pd.DataFrame, path: Path) -> None:
    """Optional region_id <-> region_safe mapping (RESEARCH O6).

    We emit one row per UNIQUE region_id (deduplicated across ancestries) so
    the resolver helper has both naming conventions available.
    """
    rows = []
    seen = set()
    for _, r in manifest_df.iterrows():
        rid = r["region_id"]
        if rid in seen:
            continue
        seen.add(rid)
        region_safe = derive_region_safe(rid, r["chr"], r["start_grch38"], r["end_grch38"])
        rows.append({
            "region_safe": region_safe,
            "region_id": rid,
            "source": "m2_union",
            "notes": "synthetic slug; M2 region union",
        })
    df = pd.DataFrame(rows, columns=["region_safe", "region_id", "source", "notes"])
    write_tsv(df, path)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.split_existing_manifest is not None:
        # Path B regen: split an EXISTING manifest in place (no --bed/--chain).
        in_df = pd.read_csv(args.split_existing_manifest, sep="\t")
        manifest_df, projection_df = split_existing_manifest(
            in_df,
            subregion_buffer_mb=args.subregion_buffer_mb,
            subregion_buffer_mb_by_ancestry=args.subregion_buffer_mb_by_ancestry,
            max_subregion_span_mb=args.max_subregion_span_mb,
            split_classes=args.split_classes,
        )
    else:
        bed_df = read_union_bed(args.bed)
        chain = load_chain(args.chain)
        ancestries = [a.strip() for a in args.ancestries.split(",") if a.strip()]
        manifest_df, projection_df = build_manifest(
            bed_df, chain, ancestries,
            max_subregion_span_mb=args.max_subregion_span_mb,
            split_classes=args.split_classes,
            subregion_buffer_mb=args.subregion_buffer_mb,
            subregion_buffer_mb_by_ancestry=args.subregion_buffer_mb_by_ancestry,
        )
    write_tsv(manifest_df, args.out_manifest)
    write_tsv(projection_df, args.out_projection)
    if args.out_mapping is not None:
        write_mapping(manifest_df, projection_df, args.out_mapping)
    print(f"OK: wrote {len(manifest_df)} manifest rows -> {args.out_manifest}", file=sys.stderr)
    print(f"OK: wrote {len(projection_df)} projection rows -> {args.out_projection}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
