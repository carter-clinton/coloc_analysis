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
import sys
from pathlib import Path

import pandas as pd

# Ancestries to emit per M2 region (D-M3-02). EUR/AFR only — TRANS LD is
# resolved via the EUR_aou panel per Q7 fallback chain (TRANS_aou_eur).
ANCESTRIES = ("AFR", "EUR")

# Per-region radius algorithm (RESEARCH Q2)
RADIUS_SAFETY_MARGIN_BP = 500_000
RADIUS_HARD_CAP_BP = 50_000_000

# region_class thresholds (RESEARCH Q2 + Q5 Path A.1/A.2/A.3)
CLASS_SMALL_MAX_MB = 5
CLASS_MEDIUM_MAX_MB = 25
CLASS_LARGE_MAX_MB = 50

# AOU §6 manifest schema, extended with structural columns from RESEARCH Q2
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
    "radius_bp",
    "region_class",
    "liftover_status",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bed", required=True, type=Path,
                   help="M2 union BED (GRCh37, 8 columns; results/regions/union_region_list.bed)")
    p.add_argument("--chain", required=True, type=Path,
                   help="UCSC GRCh37 to GRCh38 chain (data/external/liftover/hg19ToHg38.over.chain.gz)")
    p.add_argument("--out-manifest", required=True, type=Path,
                   help="Output 322-row TSV (config/ld_regions.tsv)")
    p.add_argument("--out-projection", required=True, type=Path,
                   help="Output 162-row per-region projection TSV (m3-region-class-projection.tsv)")
    p.add_argument("--out-mapping", required=False, type=Path, default=None,
                   help="Optional region_id <-> region_safe mapping TSV (RESEARCH O6)")
    p.add_argument("--ancestries", default=",".join(ANCESTRIES),
                   help="Comma-separated ancestry tokens to emit per region (default AFR,EUR)")
    return p.parse_args(argv)


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


def build_manifest(bed_df: pd.DataFrame, chain, ancestries: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Expand bed_df × ancestries into the AOU §6 manifest + per-region projection.

    Returns (manifest_df [322 rows], projection_df [162 rows: 1 header + 161 regions]).
    Projection has per-region span + class + Path-A class + estimated cluster-hours
    per RESEARCH Q5 OOM table.
    """
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
                "liftover_status": "failed",
            })
            continue

        radius_bp = compute_radius_bp(new_start, new_end)
        region_class = derive_region_class(new_start, new_end)
        # Path A class per RESEARCH Q5: small/medium -> A.1/A.2 (densify); large/xlarge -> A.3 (BlockMatrix to bucket)
        if region_class == "small":
            path_a = "A.1"
            est_hrs = 0.5  # 15-25 min mid
        elif region_class == "medium":
            path_a = "A.2"
            est_hrs = 1.5
        elif region_class == "large":
            path_a = "A.3"
            est_hrs = 8.0
        else:
            path_a = "A.3"
            est_hrs = 24.0

        span_bp = new_end - new_start
        projection_rows.append({
            "region_id": region_id,
            "chr": chr_int_str,
            "start_grch37": start_b37,
            "end_grch37": end_b37,
            "start_grch38": new_start,
            "end_grch38": new_end,
            "span_bp_grch38": span_bp,
            "span_mb_grch38": round(span_bp / 1_000_000, 3),
            "region_class": region_class,
            "radius_bp": radius_bp,
            "path_a_class": path_a,
            "est_cluster_hours_per_ancestry": est_hrs,
            "liftover_status": status,
        })

        # Emit one manifest row per ancestry (D-M3-02)
        for ancestry in ancestries:
            source_trait, lead_variant = derive_source_trait_and_lead(prov, ancestry)
            manifest_rows.append({
                "region_id": region_id,
                "chr": chr_int_str,
                "start_grch37": start_b37,
                "end_grch37": end_b37,
                "start_grch38": new_start,
                "end_grch38": new_end,
                "ancestry": ancestry,
                "source_trait": source_trait,
                "lead_variant": lead_variant,
                "radius_bp": radius_bp,
                "region_class": region_class,
                "liftover_status": status,
            })

    if audit_failures:
        print(f"AUDIT: {len(audit_failures)} liftover failures (dropped from manifest)",
              file=sys.stderr)

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
    bed_df = read_union_bed(args.bed)
    chain = load_chain(args.chain)
    ancestries = [a.strip() for a in args.ancestries.split(",") if a.strip()]
    manifest_df, projection_df = build_manifest(bed_df, chain, ancestries)
    write_tsv(manifest_df, args.out_manifest)
    write_tsv(projection_df, args.out_projection)
    if args.out_mapping is not None:
        write_mapping(manifest_df, projection_df, args.out_mapping)
    print(f"OK: wrote {len(manifest_df)} manifest rows -> {args.out_manifest}", file=sys.stderr)
    print(f"OK: wrote {len(projection_df)} projection rows -> {args.out_projection}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
