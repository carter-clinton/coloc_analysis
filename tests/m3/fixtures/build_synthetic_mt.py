#!/usr/bin/env python3
"""Build a synthetic AoU-shaped MatrixTable for local M3 driver tests.

Per RESEARCH.md Q6 — minimum viable schema (~100 samples × ~1500 variants
× 2 chromosomes chr16 + chr6) that exercises every Hail call path used by
``src/python/aou_ld_panel.py``: split_multi_hts, sample_qc, variant_qc,
filter_intervals, ld_matrix.

Synthesis strategy:
* ``hl.balding_nichols_model`` with 3 populations (AFR / EUR / OTH proxy)
* 1000 variants on chr16 (50e6 - 52e6, ~2 Mb FTO neighborhood)
* 500 variants on chr6 (28e6 - 34e6, HLA classical width)
* Annotate samples with ``ancestry_pred`` (60 'afr' / 30 'eur' / 10 'oth')
* Annotate ``filters = empty_set(tstr)``, ``rsid = missing(tstr)`` so the
  driver code path that filters AoU-flagged variants still has a column.

Idempotent: if the target MT already exists, no-op.

Usage:
    python tests/m3/fixtures/build_synthetic_mt.py --out tests/m3/fixtures/synthetic_mt/synthetic_aou.mt
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path,
                        help="Target MatrixTable directory path")
    parser.add_argument("--n-samples", type=int, default=100)
    parser.add_argument("--n-variants-chr16", type=int, default=1000)
    parser.add_argument("--n-variants-chr6", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force", action="store_true",
                        help="Rebuild even if target exists")
    args = parser.parse_args(argv)

    if args.out.exists() and not args.force:
        print(f"OK: {args.out} exists; not rebuilding (use --force to override)")
        return 0
    if args.out.exists():
        shutil.rmtree(args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    import hail as hl
    hl.init(default_reference="GRCh38", log="/tmp/synthetic_mt_build.log",
            quiet=True)

    n_total = args.n_variants_chr16 + args.n_variants_chr6
    # Balding-Nichols generator emits a MT with:
    #   row_key = (locus, alleles), col_key = sample_idx, entry GT = call
    # Default loci are chr1:1, chr1:2, ... so we must remap loci to chr16/chr6.
    mt = hl.balding_nichols_model(
        n_populations=3,
        n_samples=args.n_samples,
        n_variants=n_total,
        fst=[0.05, 0.05, 0.05],
    )
    mt = mt.add_row_index("variant_idx_synth")
    # Map first n_variants_chr16 to chr16 between 50e6 and 52e6;
    # remaining to chr6 between 28e6 and 34e6 (HLA-classical width).
    n16 = args.n_variants_chr16
    chr16_min, chr16_max = 50_000_000, 52_000_000
    chr6_min, chr6_max = 28_000_000, 34_000_000

    mt = mt.annotate_rows(
        new_locus=hl.if_else(
            mt.variant_idx_synth < n16,
            hl.locus(
                "chr16",
                hl.int32(chr16_min + (mt.variant_idx_synth * (chr16_max - chr16_min)) // n16),
                reference_genome="GRCh38",
            ),
            hl.locus(
                "chr6",
                hl.int32(chr6_min + ((mt.variant_idx_synth - n16) * (chr6_max - chr6_min))
                         // max(args.n_variants_chr6, 1)),
                reference_genome="GRCh38",
            ),
        )
    )
    mt = mt.key_rows_by()
    mt = mt.select_rows(
        locus=mt.new_locus,
        alleles=mt.alleles,
    ).key_rows_by("locus", "alleles")

    # Annotate row metadata fields the driver expects (filters, rsid).
    mt = mt.annotate_rows(
        filters=hl.empty_set(hl.tstr),
        rsid=hl.missing(hl.tstr),
    )

    # Annotate ancestry_pred on cols. 60% afr / 30% eur / 10% oth deterministically.
    n = args.n_samples
    n_afr = int(round(n * 0.60))
    n_eur = int(round(n * 0.30))
    # remainder -> oth
    mt = mt.add_col_index("col_idx_synth")
    mt = mt.annotate_cols(
        ancestry_pred=hl.if_else(
            mt.col_idx_synth < n_afr,
            "afr",
            hl.if_else(
                mt.col_idx_synth < (n_afr + n_eur),
                "eur",
                "oth",
            ),
        ),
    )

    # Persist
    mt.write(str(args.out), overwrite=True)
    print(f"OK: synthetic MT written to {args.out}")
    print(f"     n_samples = {n}; n_variants = {n_total} "
          f"(chr16: {args.n_variants_chr16}, chr6: {args.n_variants_chr6})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
