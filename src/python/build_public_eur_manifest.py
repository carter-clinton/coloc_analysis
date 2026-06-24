#!/usr/bin/env python3
"""build_public_eur_manifest.py -- m3-02e Move 2: map each M2 EUR region to the
overlapping PUBLIC UKBB 337k LD tile(s) and emit per-region extract jobs.

EUR LD for M3 is a PUBLIC reference at $0 compute (D-02e-02). The public panel
is closer to in-sample for a UK-Biobank-based EUR GWAS than AoU's 220k EUR would
be (MultiSuSiE / SuSiEx precedent: a matched public reference per ancestry).

PRIMARY  Weissbrod/PolyFun UKBB 337k (.npz scipy.sparse + .gz variants; 2,763 x
         3 Mb regions; s3://broad-alkesgroup-ukbb-ld/UKBB_LD/; CC-BY, no sign
         request; hg19/GRCh37). This reuses the existing download_ukbb_ld_tiles
         scaffold already in the tree.
ALTERNATE  Pan-UKBB 420k (s3://pan-ukb-us-east-1/ld_release/; Hail .bm,
           upper-triangular sparsified; hg19). Recorded as a documented
           alternate per D-02e-02 -- NOT the default.

COORDINATE RECONCILIATION (hg19<->hg38): the public panel is hg19/GRCh37; the
native AFR panel is GRCh38; the canonical analytic plane is GRCh37
(DEC-2026-04-24-01). config/ld_regions.tsv ALREADY carries both builds per row
(start_grch37/end_grch37 AND start_grch38/end_grch38, with liftover_status), so
the ROBUST path is to select public-panel tiles by the row's pre-lifted hg19
(grch37) window -- no re-liftover, and rsID-based variant matching downstream
where rsIDs exist. ``liftover_coordinate`` is the explicit fallback (pyliftover
over data/external/liftover/hg38ToHg19.over.chain.gz) for the rare case a
coordinate has no pre-lifted value; it never silently treats an hg19 coordinate
as hg38.

EGRESS: the public panel is external/public data; nothing AoU-individual-level is
touched here (REQ-PUBLIC-DATA-ONLY).

Usage:
    python src/python/build_public_eur_manifest.py \
        --manifest config/ld_regions.tsv \
        --out      data/interim/public_eur_ld/eur_pub_extract_jobs.tsv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

# Reuse the public-panel scaffold's overlap logic + S3 listing (do NOT
# re-implement the Tile / tiles_for_region overlap -- import it).
_SRC_SCRIPTS = Path(__file__).resolve().parents[1] / "snakemake" / "scripts"
if str(_SRC_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SRC_SCRIPTS))
from download_ukbb_ld_tiles import (  # noqa: E402
    Tile,
    safe_region_id,
    tiles_for_region,
)


# --------------------------------------------------------------------------- #
# Panel constants (D-02e-02)                                                   #
# --------------------------------------------------------------------------- #

EUR_PUBLIC_PRIMARY = {
    "source": "EUR_ukbb_pub",
    "panel": "Weissbrod_PolyFun_UKBB_337k",
    "bucket": "broad-alkesgroup-ukbb-ld",
    "prefix": "UKBB_LD/",
    "build": "hg19",          # GRCh37; reconciles to the GRCh37 analytic plane
    "n": 337491,
    "region_mb": 3,
    "license": "CC-BY",
    "source_paper": "Weissbrod et al. 2020 Nat Genet (UKBB-LD)",
    "fetch": "AWS S3 boto3 UNSIGNED (anonymous)",
}

EUR_PUBLIC_ALTERNATES = [
    {
        "panel": "Pan-UKBB_EUR_420k",
        "uri": "s3://pan-ukb-us-east-1/ld_release/",
        "n": 420531,
        "build": "hg19",
        "format": "hail_bm_upper_triangular",
        "note": "documented alternate per D-02e-02; not the default",
    }
]


# --------------------------------------------------------------------------- #
# Region reading + coordinate adapter                                         #
# --------------------------------------------------------------------------- #

def read_eur_regions(manifest_path: "str | Path") -> pd.DataFrame:
    """Read config/ld_regions.tsv and return the EUR rows."""
    df = pd.read_csv(manifest_path, sep="\t")
    eur = df[df["ancestry"].astype(str).str.upper() == "EUR"].reset_index(drop=True)
    return eur


def region_hg19_window(row) -> tuple[str, int, int]:
    """The public panel is hg19 -> select tiles by the row's GRCh37 window.

    Uses the manifest's pre-lifted start_grch37/end_grch37 (the robust path;
    liftover_status already verified). NOT the grch38 columns -- treating hg19
    panel coords as hg38 would misalign LD against the public-panel variants.
    """
    chrom = str(row["chr"]).strip().lstrip("chr")
    return chrom, int(row["start_grch37"]), int(row["end_grch37"])


def region_hg38_window(row) -> tuple[str, int, int]:
    """The GRCh38-native (AFR-plane) window for the same region."""
    chrom = str(row["chr"]).strip().lstrip("chr")
    return chrom, int(row["start_grch38"]), int(row["end_grch38"])


def _get_lifter(chain_path: "str | Path | None" = None):
    """Build a pyliftover hg38->hg19 lifter, or None if pyliftover is absent.

    Lazy import so the manifest builder works without pyliftover (the robust
    path uses the manifest's pre-lifted columns and needs no lifter at all).
    """
    try:
        from pyliftover import LiftOver  # noqa: WPS433 -- optional fallback dep
    except ImportError:
        return None
    if chain_path is None:
        return None
    return LiftOver(str(chain_path))


def liftover_coordinate(chrom: str, pos: int, *, direction: str,
                        chain_path: "str | Path | None" = None,
                        lifter=None) -> "tuple[str, int] | None":
    """Explicit hg38<->hg19 liftover FALLBACK (rsID matching is the robust path).

    ``direction`` must be exactly ``"hg38_to_hg19"`` or ``"hg19_to_hg38"``; any
    other value raises ValueError so an hg19 coordinate is NEVER silently treated
    as hg38 (and vice-versa). Returns ``(chrom, lifted_pos)`` or None when no
    chain/lifter is available (caller falls back to the pre-lifted manifest
    columns). The default chain is data/external/liftover/hg38ToHg19.over.chain.gz.
    """
    if direction not in ("hg38_to_hg19", "hg19_to_hg38"):
        raise ValueError(
            f"unknown liftover direction {direction!r}; must be 'hg38_to_hg19' "
            f"or 'hg19_to_hg38' (refusing to silently mix builds)."
        )
    lifter = lifter if lifter is not None else _get_lifter(chain_path)
    if lifter is None:
        return None
    contig = chrom if str(chrom).startswith("chr") else f"chr{chrom}"
    hits = lifter.convert_coordinate(contig, int(pos))
    if not hits:
        return None
    out_contig, out_pos = hits[0][0], hits[0][1]
    return out_contig.lstrip("chr"), int(out_pos)


# --------------------------------------------------------------------------- #
# Region -> tile mapping + job emission                                       #
# --------------------------------------------------------------------------- #

def map_region_to_tiles(*, chrom: str, start: int, end: int,
                        tiles: "list[Tile]") -> "list[Tile]":
    """Return the public-panel tile(s) overlapping a region's hg19 window.

    Reuses download_ukbb_ld_tiles.tiles_for_region (the overlap predicate); a
    region inside one 3 Mb tile maps to one tile, a region spanning two maps to
    both (cross-tile concat handled downstream by the extractor).
    """
    chrom = str(chrom).strip().lstrip("chr")
    on_chrom = [t for t in tiles if str(t.chrom) == chrom]
    return tiles_for_region(on_chrom, start, end)


def build_jobs(regions: pd.DataFrame, *, tiles_by_chrom: "dict[str, list[Tile]]",
               ) -> "list[dict]":
    """Emit one extract job per EUR region (no region orphaned).

    Each job: region_id, region_safe, chr, start (hg19), end (hg19), tile_keys,
    source=EUR_ukbb_pub, build=hg19. Selection uses the hg19 (GRCh37) window.
    """
    jobs: list[dict] = []
    for _, row in regions.iterrows():
        chrom, start, end = region_hg19_window(row)
        tiles = tiles_by_chrom.get(chrom, [])
        overlapping = map_region_to_tiles(chrom=chrom, start=start, end=end, tiles=tiles)
        jobs.append({
            "region_id": str(row["region_id"]),
            "region_safe": safe_region_id(str(row["region_id"])),
            "chr": chrom,
            "start": start,
            "end": end,
            "tile_keys": [t.npz_key for t in overlapping],
            "source": EUR_PUBLIC_PRIMARY["source"],
            "build": EUR_PUBLIC_PRIMARY["build"],
        })
    return jobs


def write_jobs_tsv(jobs: "list[dict]", out_path: "str | Path") -> str:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(jobs)
    if "tile_keys" in df.columns:
        df["tile_keys"] = df["tile_keys"].apply(lambda ks: ";".join(ks))
    df.to_csv(out_path, sep="\t", index=False)
    return str(out_path)


def _list_tiles_by_chrom(regions: pd.DataFrame) -> "dict[str, list[Tile]]":
    """Production tile listing: hit the public S3 bucket per EUR chromosome."""
    from download_ukbb_ld_tiles import list_tiles, make_s3_client  # lazy: S3 only in prod
    s3 = make_s3_client()
    out: dict[str, list[Tile]] = {}
    for chrom in regions["chr"].astype(str).str.lstrip("chr").unique():
        out[chrom] = list_tiles(s3, chrom)
    return out


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(
        description="Map M2 EUR regions to public UKBB 337k tiles; emit extract jobs"
    )
    ap.add_argument("--manifest", default="config/ld_regions.tsv",
                    help="Region manifest TSV (config/ld_regions.tsv)")
    ap.add_argument("--out", required=True, help="Output extract-jobs TSV")
    ap.add_argument("--no-s3", action="store_true",
                    help="Skip the S3 tile listing (jobs carry empty tile_keys)")
    args = ap.parse_args(argv)

    regions = read_eur_regions(args.manifest)
    if args.no_s3:
        tiles_by_chrom: dict[str, list[Tile]] = {}
    else:
        tiles_by_chrom = _list_tiles_by_chrom(regions)
    jobs = build_jobs(regions, tiles_by_chrom=tiles_by_chrom)
    out = write_jobs_tsv(jobs, args.out)
    print(f"[build_public_eur_manifest] {len(jobs)} EUR extract jobs -> {out} "
          f"(primary={EUR_PUBLIC_PRIMARY['panel']}, build={EUR_PUBLIC_PRIMARY['build']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
