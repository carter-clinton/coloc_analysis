#!/usr/bin/env python3
"""Materialize bgzipped TSV from harmonized parquet (DEF-M1-03-02 closure).

For the M2-01 LDSC matrix refire, 10 GLGC harmonized cells (HDL/TC/TG ×
{AFR,EUR,TRANS} = 9, plus ldl.HIS) have parquet files on disk
(data/processed/sumstats_harmonized_parquet/) but only 86-byte stub
TSV.bgz placeholders (data/processed/sumstats_harmonized/). The munge
wrapper consumes TSV.bgz, so we materialize TSV.bgz from parquet to
unblock the M2 refire.

The materialized files use plain gzip compression (which is
binary-compatible with the `gzip.open` call in `munge_sumstats_ldsc.py`'s
`open_maybe_gzip` helper). This is NOT a true bgzip output (no virtual
file offsets / .tbi-indexable blocks) but that does not matter for LDSC
munge consumption (LDSC reads sequentially from start to end).

Provenance: writes a sidecar .materialized_from_parquet marker recording
the source parquet path + shape + SHA-256 of input parquet.

Usage:
    python materialize_tsv_from_parquet.py KEY [KEY ...]

Where KEY is the trait-key prefix (e.g. hdl.EUR.GLGC.2021).
"""
from __future__ import annotations

import gzip
import hashlib
import sys
from pathlib import Path

import pyarrow.parquet as pq

PARQ_DIR = Path("data/processed/sumstats_harmonized_parquet")
HARM_DIR = Path("data/processed/sumstats_harmonized")


def materialize(key: str) -> tuple[int, int]:
    """Materialize one trait key. Returns (rows, output_size_bytes)."""
    parq_path = PARQ_DIR / f"{key}.GRCh37.parquet"
    out_path = HARM_DIR / f"{key}.GRCh37.tsv.bgz"

    if not parq_path.exists():
        raise FileNotFoundError(f"Parquet source missing: {parq_path}")

    # Compute parquet sha256 for provenance
    h = hashlib.sha256()
    with open(parq_path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    parq_sha = h.hexdigest()

    # Read parquet → pandas DataFrame
    df = pq.read_table(parq_path).to_pandas()
    n_rows = len(df)

    # Write gzipped TSV (LDSC's open_maybe_gzip uses gzip.open which is
    # bgzip-compatible because bgzip is a valid gzip stream)
    with gzip.open(out_path, "wt", compresslevel=6) as f:
        df.to_csv(f, sep="\t", index=False)

    out_sz = out_path.stat().st_size

    # Write provenance sidecar
    marker = HARM_DIR / f"{key}.GRCh37.materialized_from_parquet"
    marker.write_text(
        f"source_parquet: {parq_path}\n"
        f"source_sha256: {parq_sha}\n"
        f"rows: {n_rows}\n"
        f"output_size_bytes: {out_sz}\n"
        f"reason: DEF-M1-03-02 closure — parquet has real data; TSV.bgz was 86-byte stub\n"
    )

    return n_rows, out_sz


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: materialize_tsv_from_parquet.py KEY [KEY ...]", file=sys.stderr)
        sys.exit(1)

    keys = sys.argv[1:]
    print(f"Materializing {len(keys)} keys from parquet...", file=sys.stderr)
    for key in keys:
        n_rows, out_sz = materialize(key)
        print(f"  OK {key}: {n_rows:,} rows -> {out_sz/1024/1024:.1f} MB",
              file=sys.stderr)


if __name__ == "__main__":
    main()
