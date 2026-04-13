#!/usr/bin/env python3
"""Create per-chromosome binary LDSC annotation files from pathway gene sets.

For each chromosome, reads the plink .bim file and gene location file,
then creates a .annot.gz file with columns: CHR, BP, SNP, CM, followed
by one binary column per pathway gene set (1 if SNP is within
--window-kb of any gene in that set, 0 otherwise).

Usage:
    python build_ldsc_annot.py \\
        --bim-prefix data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.EUR.QC \\
        --gene-loc data/reference/magma/NCBI37.3.gene.loc \\
        --gmt-files config/pathway_sets/custom_cardiometabolic.gmt \\
                    config/pathway_sets/negative_controls.gmt \\
        --window-kb 100 \\
        --out-prefix results/pathway/annot/custom

Produces 22 files: {out-prefix}.{chr}.annot.gz

T-05-05 mitigation: no shell calls; all I/O via standard Python.
T-05-04 mitigation: validates input columns before processing.
"""
import argparse
import gzip
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_gene_loc(gene_loc_path: str) -> list:
    """Load MAGMA gene.loc file.

    Returns list of dicts with keys: entrez, chr, start, end, strand, symbol.
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
            genes.append(
                {
                    "entrez": fields[0],
                    "chr": fields[1],
                    "start": int(fields[2]),
                    "end": int(fields[3]),
                    "strand": fields[4],
                    "symbol": fields[5],
                }
            )
    return genes


def parse_gmt(gmt_path: str) -> list:
    """Parse GMT file. Returns list of (set_name, set_of_gene_symbols)."""
    gene_sets = []
    with open(gmt_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            fields = line.split("\t")
            if len(fields) < 3:
                continue
            set_name = fields[0]
            genes = set(g.strip() for g in fields[2:] if g.strip())
            gene_sets.append((set_name, genes))
    return gene_sets


def build_gene_intervals(genes: list, gene_symbols: set, chrom: str, window_bp: int) -> list:
    """Build sorted list of (start, end) intervals for genes on a chromosome.

    Each interval is the gene body extended by window_bp on each side.

    Parameters
    ----------
    genes : list
        All genes from gene.loc file.
    gene_symbols : set
        Gene symbols in the current pathway set.
    chrom : str
        Chromosome (e.g., "1", "22").
    window_bp : int
        Window size in base pairs to extend around gene boundaries.

    Returns
    -------
    list of tuple
        Sorted list of (start, end) intervals.
    """
    intervals = []
    for g in genes:
        if g["symbol"] in gene_symbols and g["chr"] == chrom:
            start = max(0, g["start"] - window_bp)
            end = g["end"] + window_bp
            intervals.append((start, end))
    # Sort and merge overlapping intervals for efficiency
    if not intervals:
        return []
    intervals.sort()
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def point_in_intervals(pos: int, intervals: list) -> bool:
    """Check if a position falls within any interval using binary search.

    Parameters
    ----------
    pos : int
        Genomic position.
    intervals : list
        Sorted list of (start, end) merged intervals.

    Returns
    -------
    bool
        True if pos is within any interval.
    """
    lo, hi = 0, len(intervals) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if pos < intervals[mid][0]:
            hi = mid - 1
        elif pos > intervals[mid][1]:
            lo = mid + 1
        else:
            return True
    return False


def build_annot_for_chrom(
    chrom: str,
    bim_path: str,
    all_genes: list,
    pathway_sets: list,
    window_bp: int,
    out_path: str,
) -> dict:
    """Build binary annotation file for one chromosome.

    Parameters
    ----------
    chrom : str
        Chromosome number (e.g., "1").
    bim_path : str
        Path to plink .bim file for this chromosome.
    all_genes : list
        All genes from gene.loc file.
    pathway_sets : list
        List of (set_name, set_of_gene_symbols).
    window_bp : int
        Window in bp around gene boundaries.
    out_path : str
        Output .annot.gz path.

    Returns
    -------
    dict
        Stats: {n_snps: int, n_annotated: {set_name: int}}.
    """
    # Pre-build intervals for each pathway set on this chromosome
    set_intervals = []
    set_names = []
    for set_name, gene_symbols in pathway_sets:
        intervals = build_gene_intervals(all_genes, gene_symbols, chrom, window_bp)
        set_intervals.append(intervals)
        set_names.append(set_name)

    # Read .bim and write .annot.gz
    n_snps = 0
    n_annotated = {name: 0 for name in set_names}

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(bim_path) as bim_fh, gzip.open(out_path, "wt") as out_fh:
        # Write header
        header = ["CHR", "BP", "SNP", "CM"] + set_names
        out_fh.write("\t".join(header) + "\n")

        for line in bim_fh:
            fields = line.strip().split("\t")
            if len(fields) < 4:
                # Try whitespace split for space-delimited .bim
                fields = line.strip().split()
            if len(fields) < 4:
                continue

            snp_chr = fields[0]
            snp_id = fields[1]
            snp_cm = fields[2]
            snp_bp = int(fields[3])
            n_snps += 1

            annotations = []
            for i, intervals in enumerate(set_intervals):
                if intervals and point_in_intervals(snp_bp, intervals):
                    annotations.append("1")
                    n_annotated[set_names[i]] += 1
                else:
                    annotations.append("0")

            out_fh.write(
                f"{snp_chr}\t{snp_bp}\t{snp_id}\t{snp_cm}\t"
                + "\t".join(annotations)
                + "\n"
            )

    return {"n_snps": n_snps, "n_annotated": n_annotated}


def main():
    parser = argparse.ArgumentParser(
        description="Build per-chromosome LDSC binary annotation files from pathway gene sets"
    )
    parser.add_argument(
        "--bim-prefix",
        required=True,
        help="Plink .bim file prefix (e.g., 1000G.EUR.QC). "
        "Files expected at {prefix}.{chr}.bim",
    )
    parser.add_argument(
        "--gene-loc",
        required=True,
        help="Gene location file (NCBI37.3.gene.loc format)",
    )
    parser.add_argument(
        "--gmt-files",
        nargs="+",
        required=True,
        help="GMT files defining pathway gene sets",
    )
    parser.add_argument(
        "--window-kb",
        type=int,
        default=100,
        help="Window in kb around gene boundaries (default: 100)",
    )
    parser.add_argument(
        "--out-prefix",
        required=True,
        help="Output prefix. Produces {prefix}.{chr}.annot.gz for chr 1-22",
    )
    parser.add_argument(
        "--chromosomes",
        nargs="+",
        default=[str(c) for c in range(1, 23)],
        help="Chromosomes to process (default: 1-22)",
    )
    args = parser.parse_args()

    # Load genes
    all_genes = load_gene_loc(args.gene_loc)
    logger.info("Loaded %d genes from %s", len(all_genes), args.gene_loc)

    # Load pathway gene sets
    all_pathway_sets = []
    for gmt_path in args.gmt_files:
        sets = parse_gmt(gmt_path)
        logger.info("Loaded %d gene sets from %s", len(sets), gmt_path)
        all_pathway_sets.extend(sets)

    if not all_pathway_sets:
        logger.error("No gene sets found in input GMT files")
        sys.exit(1)

    window_bp = args.window_kb * 1000

    # Process each chromosome
    Path(args.out_prefix).parent.mkdir(parents=True, exist_ok=True)
    for chrom in args.chromosomes:
        bim_path = f"{args.bim_prefix}.{chrom}.bim"
        out_path = f"{args.out_prefix}.{chrom}.annot.gz"

        if not Path(bim_path).exists():
            logger.warning("BIM file not found: %s, skipping chr%s", bim_path, chrom)
            continue

        stats = build_annot_for_chrom(
            chrom=chrom,
            bim_path=bim_path,
            all_genes=all_genes,
            pathway_sets=all_pathway_sets,
            window_bp=window_bp,
            out_path=out_path,
        )
        annotated_summary = ", ".join(
            f"{name}={count}" for name, count in stats["n_annotated"].items() if count > 0
        )
        logger.info(
            "chr%s: %d SNPs, annotated: %s",
            chrom,
            stats["n_snps"],
            annotated_summary or "none",
        )

    logger.info("Done. Output prefix: %s", args.out_prefix)


if __name__ == "__main__":
    main()
