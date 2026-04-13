#!/usr/bin/env python3
"""Build discoverability-matched background gene list for g:Profiler enrichment.

Implements the Reimand 2019 Nat Protoc recommendation (D-03a):
  1. For each of the 5 traits, read harmonized sumstats (EUR as largest-N ancestry)
  2. Filter to genome-wide significant SNPs (P < 5e-8)
  3. Extend each SNP position by +/- window_kb (default 500 kb)
  4. Merge overlapping intervals
  5. Intersect merged intervals with gene locations (NCBI37.3.gene.loc)
  6. Union across all traits
  7. Write unique gene symbol list (one gene per line)

This controls for "this gene was discoverable because it was near a GWAS hit
for anything" -- the conservative discoverability-matched background approach.

Usage:
    python build_gprofiler_bg.py \\
        --sumstats-dir data/processed/sumstats_harmonized \\
        --traits bmi,t2d,hypertension,asthma,stroke \\
        --gene-loc data/reference/magma/NCBI37.3.gene.loc \\
        --window-kb 500 \\
        --p-threshold 5e-8 \\
        --out results/pathway/gprofiler/background_genes.txt

References:
    Reimand et al. 2019 Nat Protoc (g:Profiler best practices)
"""
import argparse
import gzip
import io
import logging
import os
import sys
from pathlib import Path


def _open_sumstats(path: str):
    """Open a sumstats file, transparently handling .bgz/.gz compression.

    Harmonized sumstats are bgzipped (`{trait}.{ancestry}.tsv.bgz`), but the
    file is readable by gzip since BGZF is a gzip-compatible format. Returns a
    text-mode file handle.
    """
    if path.endswith(".bgz") or path.endswith(".gz"):
        return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8")
    return open(path, "r", encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _load_gene_locations(gene_loc_path: str) -> list:
    """Load gene locations from NCBI37.3.gene.loc format.

    Parameters
    ----------
    gene_loc_path : str
        Path to gene location file (columns: ENTREZ CHR START END STRAND SYMBOL).

    Returns
    -------
    list of dict
        Each dict has keys: chrom, start, end, symbol.
    """
    genes = []
    with open(gene_loc_path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) < 6:
                continue
            chrom = fields[1]
            try:
                start = int(fields[2])
                end = int(fields[3])
            except ValueError:
                continue
            symbol = fields[5]
            genes.append({
                "chrom": chrom,
                "start": start,
                "end": end,
                "symbol": symbol,
            })
    logger.info("Loaded %d gene locations from %s", len(genes), gene_loc_path)
    return genes


def _read_gws_snps(sumstats_path: str, p_threshold: float = 5e-8) -> list:
    """Read genome-wide significant SNPs from harmonized sumstats.

    Parameters
    ----------
    sumstats_path : str
        Path to harmonized sumstats TSV with columns CHR, POS, P.
    p_threshold : float
        P-value significance threshold (default 5e-8).

    Returns
    -------
    list of tuple
        Each tuple is (chrom, position) for significant SNPs.
    """
    gws_snps = []
    with _open_sumstats(sumstats_path) as fh:
        header_line = fh.readline().strip()
        columns = header_line.split("\t")
        col_lower = [c.lower() for c in columns]

        chr_idx = None
        pos_idx = None
        p_idx = None
        for i, c in enumerate(col_lower):
            if c == "chr":
                chr_idx = i
            elif c == "pos":
                pos_idx = i
            elif c == "p":
                p_idx = i

        if chr_idx is None or pos_idx is None or p_idx is None:
            logger.warning(
                "Missing CHR/POS/P columns in %s (found: %s), skipping",
                sumstats_path,
                columns,
            )
            return gws_snps

        for line in fh:
            fields = line.strip().split("\t")
            if len(fields) <= max(chr_idx, pos_idx, p_idx):
                continue
            try:
                p_val = float(fields[p_idx])
                if p_val < p_threshold:
                    chrom = fields[chr_idx].replace("chr", "")
                    pos = int(fields[pos_idx])
                    gws_snps.append((chrom, pos))
            except (ValueError, IndexError):
                continue

    logger.info(
        "Found %d GWS SNPs (P < %g) in %s",
        len(gws_snps),
        p_threshold,
        sumstats_path,
    )
    return gws_snps


def _merge_intervals(intervals: list) -> list:
    """Merge overlapping genomic intervals.

    Parameters
    ----------
    intervals : list of tuple
        Each tuple is (chrom, start, end).

    Returns
    -------
    list of tuple
        Merged intervals as (chrom, start, end).
    """
    if not intervals:
        return []

    # Sort by chrom then start
    sorted_intervals = sorted(intervals, key=lambda x: (x[0], x[1]))

    merged = [sorted_intervals[0]]
    for chrom, start, end in sorted_intervals[1:]:
        prev_chrom, prev_start, prev_end = merged[-1]
        if chrom == prev_chrom and start <= prev_end:
            # Overlapping -- extend
            merged[-1] = (chrom, prev_start, max(end, prev_end))
        else:
            merged.append((chrom, start, end))

    return merged


def _intersect_genes(merged_intervals: list, genes: list) -> set:
    """Find genes that overlap with merged genomic intervals.

    Parameters
    ----------
    merged_intervals : list of tuple
        Merged intervals as (chrom, start, end).
    genes : list of dict
        Gene locations with keys: chrom, start, end, symbol.

    Returns
    -------
    set
        Gene symbols that overlap with at least one interval.
    """
    # Build interval lookup by chromosome for efficiency
    intervals_by_chrom = {}
    for chrom, start, end in merged_intervals:
        intervals_by_chrom.setdefault(chrom, []).append((start, end))

    matched_genes = set()
    for gene in genes:
        gene_chrom = gene["chrom"]
        if gene_chrom not in intervals_by_chrom:
            continue
        gene_start = gene["start"]
        gene_end = gene["end"]
        for iv_start, iv_end in intervals_by_chrom[gene_chrom]:
            # Check overlap: gene overlaps interval if gene_start <= iv_end and gene_end >= iv_start
            if gene_start <= iv_end and gene_end >= iv_start:
                matched_genes.add(gene["symbol"])
                break  # No need to check more intervals for this gene

    return matched_genes


def build_union_background(
    sumstats_paths: list,
    gene_loc_path: str,
    window_kb: int = 500,
    p_threshold: float = 5e-8,
) -> set:
    """Build 5-trait union background gene list per D-03a.

    For each trait's summary statistics:
      1. Find genome-wide significant SNPs (P < p_threshold)
      2. Extend each SNP position by +/- window_kb
      3. Merge overlapping intervals
      4. Intersect with gene locations

    Union the gene lists across all traits.

    Parameters
    ----------
    sumstats_paths : list of str
        Paths to harmonized sumstats files for each trait.
    gene_loc_path : str
        Path to gene location file (NCBI37.3.gene.loc format).
    window_kb : int
        Window in kilobases to extend around each GWS SNP (default 500).
    p_threshold : float
        Genome-wide significance threshold (default 5e-8).

    Returns
    -------
    set
        Union of all background gene symbols across traits.
    """
    genes = _load_gene_locations(gene_loc_path)
    window_bp = window_kb * 1000

    all_background_genes = set()

    for path in sumstats_paths:
        if not os.path.exists(path):
            logger.warning("Sumstats file not found, skipping: %s", path)
            continue

        gws_snps = _read_gws_snps(path, p_threshold)
        if not gws_snps:
            logger.warning("No GWS SNPs in %s, skipping", path)
            continue

        # Extend SNP positions by window
        intervals = []
        for chrom, pos in gws_snps:
            start = max(0, pos - window_bp)
            end = pos + window_bp
            intervals.append((chrom, start, end))

        # Merge overlapping intervals
        merged = _merge_intervals(intervals)
        logger.info(
            "%d GWS SNPs -> %d merged intervals for %s",
            len(gws_snps),
            len(merged),
            path,
        )

        # Intersect with gene locations
        trait_genes = _intersect_genes(merged, genes)
        logger.info("%d genes in background from %s", len(trait_genes), path)
        all_background_genes.update(trait_genes)

    logger.info(
        "Total union background: %d unique genes from %d trait files",
        len(all_background_genes),
        len(sumstats_paths),
    )
    return all_background_genes


def main():
    """CLI entry point for background gene list builder."""
    parser = argparse.ArgumentParser(
        description="Build discoverability-matched background gene list for g:Profiler"
    )
    parser.add_argument(
        "--sumstats-dir",
        required=True,
        help="Directory containing harmonized sumstats TSV files",
    )
    parser.add_argument(
        "--traits",
        required=True,
        help="Comma-separated trait names (e.g., bmi,t2d,hypertension,asthma,stroke)",
    )
    parser.add_argument(
        "--ancestry",
        default="EUR",
        help="Ancestry to use for sumstats (default: EUR, the largest-N ancestry)",
    )
    parser.add_argument(
        "--gene-loc",
        required=True,
        help="Gene location file (NCBI37.3.gene.loc format)",
    )
    parser.add_argument(
        "--window-kb",
        type=int,
        default=500,
        help="Window in kb around each GWS SNP (default: 500 per D-03a)",
    )
    parser.add_argument(
        "--p-threshold",
        type=float,
        default=5e-8,
        help="Genome-wide significance P-value threshold (default: 5e-8)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output file path (one gene symbol per line)",
    )
    args = parser.parse_args()

    # Build sumstats file paths
    traits = [t.strip() for t in args.traits.split(",")]
    # Harmonized sumstats live at `{dir}/{trait}.{ancestry}.tsv.bgz` (dot
    # separator, bgzipped) per src/snakemake/rules/sumstats.smk. The previous
    # underscore pattern did not match on-disk files and silently returned
    # zero background genes (WR-01).
    sumstats_paths = [
        os.path.join(args.sumstats_dir, f"{trait}.{args.ancestry}.tsv.bgz")
        for trait in traits
    ]

    # Build background
    background_genes = build_union_background(
        sumstats_paths=sumstats_paths,
        gene_loc_path=args.gene_loc,
        window_kb=args.window_kb,
        p_threshold=args.p_threshold,
    )

    if not background_genes:
        logger.error("No background genes found -- check input files")
        sys.exit(1)

    # Write output
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as fout:
        for gene in sorted(background_genes):
            fout.write(f"{gene}\n")

    logger.info("Wrote %d background genes to %s", len(background_genes), args.out)


if __name__ == "__main__":
    main()
