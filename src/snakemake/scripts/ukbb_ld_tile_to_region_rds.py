#!/usr/bin/env python3
"""Convert an already-downloaded UKBB-LD NPZ tile (+ companion variant TSV)
into a per-region `.rds` + sidecar `.meta.json`, without touching S3.

This is the retry / offline-iteration counterpart to
`download_ukbb_ld_tiles.py`. Use it when:
  - You have already cached a tile locally and want to re-extract a region
    without re-hitting the bucket,
  - You are debugging the intersection logic for a new curated region,
  - You want to extract from a tile that spans only one tile (no cross-tile
    block-diagonal concat needed).

Usage
-----
    python ukbb_ld_tile_to_region_rds.py \
        --tile-npz /path/to/chr22_16000001_19000001.npz \
        --tile-var /path/to/chr22_16000001_19000001.gz \
        --region-id APOL1_22q12 \
        --chrom 22 --start 36200000 --end 36600000 \
        --out-dir data/processed/ld_reference/EUR_ukbb_ld

Outputs (mirrors download_ukbb_ld_tiles.py):
    {out-dir}/{safe_region_id}.rds
    {out-dir}/{safe_region_id}.meta.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Reuse the shared helpers from the downloader (same directory).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from download_ukbb_ld_tiles import (  # noqa: E402
    HAVE_PYREADR,
    _position_column,
    load_ld_matrix,
    load_variant_tsv,
    safe_region_id,
    sha256_file,
)

try:
    import pyreadr  # noqa: F401
except ImportError:  # pragma: no cover - env-dependent
    pass


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Extract a per-region LD .rds from a single already-downloaded "
            "UKBB-LD tile (single-tile case only). For multi-tile regions use "
            "download_ukbb_ld_tiles.py."
        ),
    )
    ap.add_argument("--tile-npz", required=True, type=Path)
    ap.add_argument("--tile-var", required=True, type=Path)
    ap.add_argument("--region-id", required=True)
    ap.add_argument("--chrom", required=True)
    ap.add_argument("--start", required=True, type=int)
    ap.add_argument("--end", required=True, type=int)
    ap.add_argument("--out-dir", required=True, type=Path)
    args = ap.parse_args(argv)

    if not args.tile_npz.exists():
        raise SystemExit(f"tile NPZ not found: {args.tile_npz}")
    if not args.tile_var.exists():
        raise SystemExit(f"tile variant TSV not found: {args.tile_var}")

    safe_id = safe_region_id(args.region_id)

    R_full = load_ld_matrix(args.tile_npz)
    variants = load_variant_tsv(args.tile_var)
    pos_col = _position_column(variants)

    n_tile = len(variants)
    if R_full.shape != (n_tile, n_tile):
        raise SystemExit(
            f"LD shape {R_full.shape} does not match variant count {n_tile}"
        )

    mask = (variants[pos_col] >= args.start) & (variants[pos_col] <= args.end)
    idx = mask.values
    if idx.sum() == 0:
        raise SystemExit(
            f"No variants in chr{args.chrom}:{args.start}-{args.end} "
            f"within tile {args.tile_npz.name}"
        )

    R_region = R_full[np.ix_(idx, idx)]
    variants_region = variants.loc[mask].reset_index(drop=True)

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_rds = out_dir / f"{safe_id}.rds"
    out_meta = out_rds.with_suffix(".meta.json")

    if HAVE_PYREADR:
        pyreadr.write_rds(
            str(out_rds),
            {
                "R": pd.DataFrame(R_region),
                "variants": variants_region,
                "ld_source": pd.DataFrame({"ld_source": ["ukbb_ld_tiled"]}),
            },
        )
    else:
        np.savez(
            str(out_rds.with_suffix(".npz")),
            R=R_region,
            variants=variants_region.to_records(index=False),
        )
        out_rds.write_bytes(b"PYREADR_MISSING\n")

    meta = {
        "region_id": args.region_id,
        "safe_region_id": safe_id,
        "chr": args.chrom,
        "start": args.start,
        "end": args.end,
        "n_variants": int(len(variants_region)),
        "ld_source": "ukbb_ld_tiled",
        "tile_keys": [args.tile_npz.name],
        "sha256": {
            args.tile_npz.name: sha256_file(args.tile_npz),
            args.tile_var.name: sha256_file(args.tile_var),
        },
        "source_paper": "Weissbrod et al. 2020 Nat Genet (UKBB-LD)",
    }
    out_meta.write_text(json.dumps(meta, indent=2))
    print(
        f"[{args.region_id}] wrote {out_rds} (n_variants={meta['n_variants']}, "
        f"ld_source=ukbb_ld_tiled)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
