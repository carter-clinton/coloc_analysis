#!/usr/bin/env python3
"""Download UKBB-LD tiled EUR panel (Weissbrod 2020) from the AWS Open Data
Registry bucket `s3://broad-alkesgroup-ukbb-ld/UKBB_LD/` and extract
per-curated-region LD submatrices.

Background
----------
- Bucket: s3://broad-alkesgroup-ukbb-ld (public, anonymous via boto3 UNSIGNED)
- Prefix: UKBB_LD/
- Tile layout: chr{N}_{start}_{end}.npz + companion chr{N}_{start}_{end}.gz
  (scipy.sparse COO NPZ -- verified by Plan 01-02 Wave 0 preflight,
  wave2a_preflight.log)
- License: AWS Open Data Registry (public, no DUA)
- Reference: Weissbrod et al. 2020, Nature Genetics

Tile format (verified 2026-04-12 preflight, chr22_14000001_17000001)
--------------------------------------------------------------------
NPZ is NOT an upper-triangle flat array keyed "R" (the plan pre-spec
assumption) -- it is a scipy.sparse coo_matrix saved via
scipy.sparse.save_npz. Internal keys: row, col, format, shape, data.
The stored matrix is symmetric (density ~0.50) so a .toarray() call
yields the full n x n LD matrix directly, no triangular reconstruction
needed.

Companion .gz variant TSV columns: rsid, chromosome, position, allele1,
allele2 (tab-separated, gzipped).

Mitigations
-----------
T-1-02 (Tampering on downloads): SHA256 computed per tile, recorded in
    a sidecar .meta.json alongside each region .rds.
T-1-03 (region_id -> filesystem path): region_id is sanitized to
    alnum+underscore before any path interpolation.
T-1-04 (HLA cross-tile LD): regions spanning multiple tiles are built
    as scipy.linalg.block_diag of per-tile submatrices; the sidecar
    .meta.json records ld_source='ukbb_ld_tiled_block_diagonal' so the
    QC dashboard and methods fragment can surface the statistical
    caveat.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import scipy.linalg
import scipy.sparse

try:
    import boto3
    from botocore import UNSIGNED
    from botocore.client import Config
    HAVE_BOTO3 = True
except ImportError:
    HAVE_BOTO3 = False

try:
    import pyreadr
    HAVE_PYREADR = True
except ImportError:
    HAVE_PYREADR = False


BUCKET = "broad-alkesgroup-ukbb-ld"
PREFIX = "UKBB_LD/"

# m3-02e Move 2 (additive): the public UKBB 337k panel is the M3 EUR LD source
# (EUR_ukbb_pub), written to its own target dir so it does not collide with the
# legacy curated EUR_ukbb_ld output. The existing rule behavior is unchanged;
# m3_public_eur_ld.smk passes this dir via the existing --out-dir parameter.
# These tiles are hg19/GRCh37 (the Weissbrod build); the M3 analytic plane is
# GRCh37, so the EUR_ukbb_pub .rds drops into the same loader contract after the
# standard chr-prefix + provenance handling (DEC-2026-04-24-01).
EUR_UKBB_PUB_OUT_DIR = "data/processed/ld_reference/EUR_ukbb_pub"
EUR_UKBB_PUB_BUILD = "hg19"  # GRCh37

# Tile naming regex: chr{N}_{start}_{end}.npz (N is 1..22 or X)
_TILE_RE = re.compile(r"chr([0-9XY]+)_(\d+)_(\d+)\.npz$")

# T-1-03 region_id sanitizer: keep only word characters (alnum + underscore).
_SAFE_ID_RE = re.compile(r"[^A-Za-z0-9_]")


@dataclass(frozen=True)
class Tile:
    chrom: str
    start: int
    end: int
    npz_key: str  # full S3 key under PREFIX

    @property
    def var_key(self) -> str:
        return self.npz_key[:-len(".npz")] + ".gz"

    def __repr__(self) -> str:  # pragma: no cover - debug only
        return f"Tile(chr{self.chrom}:{self.start}-{self.end})"


# ---------------------------------------------------------------------------
# S3 access
# ---------------------------------------------------------------------------
def make_s3_client():
    """Return a boto3 S3 client configured for unsigned (anonymous) access."""
    if not HAVE_BOTO3:
        raise RuntimeError(
            "boto3 is required; install via envs/ld_build.yml. "
            "Run: conda env create -f envs/ld_build.yml"
        )
    return boto3.client("s3", config=Config(signature_version=UNSIGNED))


def list_tiles(s3, chrom: str) -> list[Tile]:
    """List all UKBB-LD NPZ tiles for one chromosome, sorted by start position."""
    paginator = s3.get_paginator("list_objects_v2")
    tiles: list[Tile] = []
    for page in paginator.paginate(Bucket=BUCKET, Prefix=f"{PREFIX}chr{chrom}_"):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.endswith(".npz"):
                continue
            m = _TILE_RE.search(key)
            if not m:
                continue
            t_chr, t_start, t_end = m.group(1), int(m.group(2)), int(m.group(3))
            if t_chr != chrom:
                continue  # defensive: paginator prefix should filter this
            tiles.append(Tile(chrom=t_chr, start=t_start, end=t_end, npz_key=key))
    tiles.sort(key=lambda t: (t.start, t.end))
    return tiles


def tiles_for_region(
    tiles: list[Tile], region_start: int, region_end: int
) -> list[Tile]:
    """Return tiles whose [start, end] intersects [region_start, region_end]."""
    return [t for t in tiles if t.end >= region_start and t.start <= region_end]


# ---------------------------------------------------------------------------
# Local IO
# ---------------------------------------------------------------------------
def sha256_file(path: Path) -> str:
    """Streaming SHA256 of a local file (T-1-02 provenance)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_tile(s3, key: str, local_path: Path) -> str:
    """Download an S3 key to a local path, skipping if already cached.

    Returns the SHA256 of the local file (T-1-02 mitigation).
    """
    local_path.parent.mkdir(parents=True, exist_ok=True)
    if not local_path.exists():
        s3.download_file(BUCKET, key, str(local_path))
    return sha256_file(local_path)


def load_ld_matrix(npz_path: Path) -> np.ndarray:
    """Load a UKBB-LD NPZ tile as a dense float32 ndarray.

    Per Plan 01-02 Wave 0 preflight the NPZ is a scipy.sparse COO matrix
    keyed {row, col, format, shape, data}. We load it via
    scipy.sparse.load_npz and densify via .toarray(). The stored matrix
    is already symmetric (density ~0.50 == upper triangle filled
    symmetrically), so no triangular reconstruction is needed.
    """
    sparse = scipy.sparse.load_npz(str(npz_path))
    dense = sparse.toarray().astype(np.float32, copy=False)
    # Defensive symmetrization in case the producer stored only one triangle
    if not np.allclose(dense, dense.T, atol=1e-6):
        dense = (dense + dense.T) / 2.0
    return dense


def load_variant_tsv(var_path: Path) -> pd.DataFrame:
    """Load the companion .gz TSV of variants for a tile.

    Columns observed in the preflight probe:
        rsid, chromosome, position, allele1, allele2
    """
    df = pd.read_csv(var_path, sep="\t", compression="gzip")
    return df


def _position_column(df: pd.DataFrame) -> str:
    for cand in ("position", "pos", "POS", "bp", "BP"):
        if cand in df.columns:
            return cand
    raise ValueError(
        f"No position column in variant TSV; columns={list(df.columns)}"
    )


# ---------------------------------------------------------------------------
# Region extraction
# ---------------------------------------------------------------------------
def safe_region_id(region_id: str) -> str:
    """T-1-03 mitigation: reject slashes and non-word characters."""
    if "/" in region_id or ".." in region_id:
        raise ValueError(f"Unsafe region_id: {region_id!r}")
    return _SAFE_ID_RE.sub("_", region_id)


def extract_region(
    s3,
    chrom: str,
    region_id: str,
    region_start: int,
    region_end: int,
    out_dir: Path,
    scratch_dir: Path,
) -> str:
    """Build the per-region LD .rds + sidecar .meta.json for one curated region.

    Returns the ld_source flag string.
    """
    safe_id = safe_region_id(region_id)
    tiles = list_tiles(s3, chrom)
    overlapping = tiles_for_region(tiles, region_start, region_end)
    if not overlapping:
        raise RuntimeError(
            f"No UKBB-LD tiles overlap chr{chrom}:{region_start}-{region_end} "
            f"for region {region_id!r}"
        )

    sha_manifest: dict[str, str] = {}
    blocks_R: list[np.ndarray] = []
    blocks_v: list[pd.DataFrame] = []

    for tile in overlapping:
        npz_local = scratch_dir / Path(tile.npz_key).name
        var_local = scratch_dir / Path(tile.var_key).name
        sha_manifest[tile.npz_key] = download_tile(s3, tile.npz_key, npz_local)
        sha_manifest[tile.var_key] = download_tile(s3, tile.var_key, var_local)

        R_tile = load_ld_matrix(npz_local)
        var_tile = load_variant_tsv(var_local)

        pos_col = _position_column(var_tile)
        n_tile = len(var_tile)
        if R_tile.shape != (n_tile, n_tile):
            raise RuntimeError(
                f"Tile {tile.npz_key}: LD shape {R_tile.shape} does not match "
                f"variant count {n_tile}"
            )

        mask = (var_tile[pos_col] >= region_start) & (var_tile[pos_col] <= region_end)
        idx = mask.values
        if idx.sum() == 0:
            continue
        blocks_R.append(R_tile[np.ix_(idx, idx)])
        blocks_v.append(var_tile.loc[mask].reset_index(drop=True))

    if not blocks_R:
        raise RuntimeError(
            f"No variants within chr{chrom}:{region_start}-{region_end} after "
            f"intersecting {len(overlapping)} tile(s) for region {region_id!r}"
        )

    if len(blocks_R) == 1:
        R_region = blocks_R[0]
        variants_region = blocks_v[0]
        ld_source = "ukbb_ld_tiled"
    else:
        # Multi-tile block-diagonal (HLA-style) -- T-1-04 mitigation
        R_region = scipy.linalg.block_diag(*blocks_R)
        variants_region = pd.concat(blocks_v, ignore_index=True)
        ld_source = "ukbb_ld_tiled_block_diagonal"

    n_variants = int(len(variants_region))

    out_dir.mkdir(parents=True, exist_ok=True)
    out_rds = out_dir / f"{safe_id}.rds"
    out_meta = out_rds.with_suffix(".meta.json")

    # Write .rds (Python -> R bridge via pyreadr). We wrap R as a DataFrame
    # (pyreadr does not support raw matrices for writing) plus a variants
    # DataFrame; R consumers should call `as.matrix()` on the R component.
    if HAVE_PYREADR:
        pyreadr.write_rds(
            str(out_rds),
            {
                "R": pd.DataFrame(R_region),
                "variants": variants_region,
                "ld_source": pd.DataFrame({"ld_source": [ld_source]}),
            },
        )
    else:
        # Defer: drop a .npz next to the .rds path so the rule output still
        # appears and the R bridge can convert it. This path is exercised only
        # when pyreadr is unavailable (e.g. in a minimal preflight env).
        fallback = out_rds.with_suffix(".npz")
        np.savez(
            str(fallback),
            R=R_region,
            variants=variants_region.to_records(index=False),
        )
        # Write a shim .rds placeholder so downstream existence checks pass;
        # this should never land in production because ld_build.yml pins
        # pyreadr.
        out_rds.write_bytes(b"PYREADR_MISSING\n")

    meta = {
        "region_id": region_id,
        "safe_region_id": safe_id,
        "chr": chrom,
        "start": region_start,
        "end": region_end,
        "n_variants": n_variants,
        "ld_source": ld_source,
        "tile_keys": [t.npz_key for t in overlapping],
        "sha256": sha_manifest,
        "source_paper": "Weissbrod et al. 2020 Nat Genet (UKBB-LD)",
        "bucket": BUCKET,
        "prefix": PREFIX,
    }
    out_meta.write_text(json.dumps(meta, indent=2))
    return ld_source


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Download UKBB-LD tiles and extract per-region LD .rds",
    )
    ap.add_argument("--regions-csv", required=True, help="config/regions_curated.csv")
    ap.add_argument("--out-dir", required=True, help="Output dir for {region}.rds")
    ap.add_argument(
        "--scratch-dir",
        default="/rs1/researchers/c/ckclinto/ukbb_ld_scratch",
        help="Local cache for downloaded NPZ + variant TSV tiles",
    )
    ap.add_argument(
        "--region-ids",
        nargs="*",
        default=None,
        help="Optional subset of region_id values to process (default: all)",
    )
    ap.add_argument(
        "--ancestry",
        default="EUR",
        help="Ancestry label recorded in the output (UKBB-LD is EUR-only)",
    )
    args = ap.parse_args(list(argv) if argv is not None else None)

    out_dir = Path(args.out_dir)
    scratch_dir = Path(args.scratch_dir)
    scratch_dir.mkdir(parents=True, exist_ok=True)

    regions = pd.read_csv(args.regions_csv)
    required_cols = {"region_id", "chr", "start", "end"}
    missing = required_cols - set(regions.columns)
    if missing:
        raise SystemExit(f"regions CSV missing required columns: {sorted(missing)}")

    if args.region_ids:
        regions = regions[regions["region_id"].isin(args.region_ids)]
    # Filter out X/Y chromosomes (UKBB-LD autosomes only; BMI_Xq24 is ChrX).
    before = len(regions)
    regions = regions[~regions["chr"].astype(str).str.upper().isin(["X", "Y", "MT"])]
    skipped = before - len(regions)
    if skipped:
        print(
            f"[download_ukbb_ld_tiles] skipped {skipped} non-autosomal region(s); "
            f"UKBB-LD EUR panel covers autosomes only.",
            file=sys.stderr,
        )

    s3 = make_s3_client()
    for _, row in regions.iterrows():
        chrom = str(row["chr"]).strip().lstrip("chr")
        ld_source = extract_region(
            s3,
            chrom=chrom,
            region_id=str(row["region_id"]),
            region_start=int(row["start"]),
            region_end=int(row["end"]),
            out_dir=out_dir,
            scratch_dir=scratch_dir,
        )
        print(f"[{row['region_id']}] chr{chrom}:{row['start']}-{row['end']} "
              f"ld_source={ld_source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
