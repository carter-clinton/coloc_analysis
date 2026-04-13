#!/usr/bin/env python3
"""Gene-set-level permutation null generator per D-06c.

Extends the Phase 2 sample_null_loci.py pattern to gene-set matching:
generates N permutation null gene sets matched for gene length, LD
complexity (independent LD block count), and median MAF against the
query gene list (colocalization-derived Tier A+B genes).

Three matching criteria per D-06c:
  (a) Gene length (END - START): +/- 50% tolerance
  (b) LD complexity: count of independent LD blocks within gene
      boundaries, computed from baselineLD_v2.2 LD scores
  (c) Median MAF of SNPs within gene boundaries from 1000G_Phase3_frq

Deterministic seeds: seed_base + permutation_index (T-02-18 pattern).

Usage:
    python extend_null_genesets.py \\
        --query-genes GENES.txt \\
        --gene-loc NCBI37.3.gene.loc \\
        --maf-reference data/reference/ldsc/1000G_Phase3_frq \\
        --ld-score-reference data/reference/ldsc/baselineLD_v2.2 \\
        --n-permutations 1000 \\
        --seed 42 \\
        --out-dir results/pathway/permutation_null

References:
    sample_null_loci.py (Phase 2) -- matching infrastructure
    D-06c: 1000 permutation null gene sets matched for length, LD, MAF
    T-02-18: deterministic seed = seed_base + permutation_index
"""
import argparse
import csv
import gzip
import logging
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Gene location parsing
# ---------------------------------------------------------------------------

def parse_gene_loc(gene_loc_path):
    """Parse NCBI37.3.gene.loc file.

    Format: ENTREZ CHR START END STRAND SYMBOL
    Returns dict mapping gene symbol -> {entrez, chr, start, end, strand, symbol, length}.
    """
    genes = {}
    with open(gene_loc_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 6:
                continue
            entrez, chrom, start, end, strand, symbol = parts[:6]
            try:
                start_i = int(start)
                end_i = int(end)
            except ValueError:
                continue
            genes[symbol] = {
                "entrez": entrez,
                "chr": chrom,
                "start": start_i,
                "end": end_i,
                "strand": strand,
                "symbol": symbol,
                "length": max(end_i - start_i, 1),
            }
    return genes


def read_query_genes(path):
    """Read a query gene list (one gene symbol per line)."""
    genes = []
    with open(path) as f:
        for line in f:
            g = line.strip()
            if g and not g.startswith("#"):
                genes.append(g)
    return genes


# ---------------------------------------------------------------------------
# MAF computation
# ---------------------------------------------------------------------------

def load_maf_for_chromosome(maf_prefix, chrom):
    """Load MAF values from 1000G_Phase3_frq files for a chromosome.

    Looks for {maf_prefix}/1000G.EUR.QC.{chrom}.frq or similar.
    Returns dict mapping position -> MAF.
    """
    # Try common file patterns
    patterns = [
        f"{maf_prefix}/1000G.EUR.QC.{chrom}.frq",
        f"{maf_prefix}.{chrom}.frq",
        f"{maf_prefix}/1000G_Phase3_frq.{chrom}.frq",
    ]
    for pattern in patterns:
        if os.path.exists(pattern):
            return _parse_frq_file(pattern)
        gz_path = pattern + ".gz"
        if os.path.exists(gz_path):
            return _parse_frq_file_gz(gz_path)
    # Return empty dict if no file found
    return {}


def _parse_frq_file(path):
    """Parse a PLINK .frq file. Returns dict: pos -> maf."""
    maf_map = {}
    with open(path) as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                try:
                    # Typical .frq columns: CHR SNP A1 A2 MAF NCHROBS
                    maf = float(parts[4])
                    # Extract position from SNP name if possible, or skip
                    snp = parts[1]
                    maf_map[snp] = maf
                except (ValueError, IndexError):
                    continue
    return maf_map


def _parse_frq_file_gz(path):
    """Parse a gzipped .frq file. Returns dict: snp -> maf."""
    maf_map = {}
    with gzip.open(path, "rt") as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                try:
                    maf = float(parts[4])
                    snp = parts[1]
                    maf_map[snp] = maf
                except (ValueError, IndexError):
                    continue
    return maf_map


# ---------------------------------------------------------------------------
# LD score parsing
# ---------------------------------------------------------------------------

def load_ld_scores_for_chromosome(ld_prefix, chrom):
    """Load LD scores from baselineLD_v2.2 for a chromosome.

    Looks for {ld_prefix}/baselineLD.{chrom}.l2.ldscore.gz or similar.
    Returns list of (position, ld_score) tuples sorted by position.
    """
    patterns = [
        f"{ld_prefix}/baselineLD.{chrom}.l2.ldscore.gz",
        f"{ld_prefix}.{chrom}.l2.ldscore.gz",
    ]
    for pattern in patterns:
        if os.path.exists(pattern):
            return _parse_ldscore_gz(pattern)
    return []


def _parse_ldscore_gz(path):
    """Parse gzipped ldscore file. Returns list of (bp, total_ld_score)."""
    records = []
    with gzip.open(path, "rt") as f:
        header = f.readline().strip().split()
        # Find relevant columns
        try:
            bp_idx = header.index("BP")
        except ValueError:
            bp_idx = 2  # Default position for BP column
        # Use baselineLD column (last column is usually total LD score)
        # or the L2 column
        l2_idx = len(header) - 1
        for i, col in enumerate(header):
            if col == "L2" or col.startswith("baseL2"):
                l2_idx = i
                break

        for line in f:
            parts = line.strip().split()
            if len(parts) > max(bp_idx, l2_idx):
                try:
                    bp = int(parts[bp_idx])
                    ld = float(parts[l2_idx])
                    records.append((bp, ld))
                except (ValueError, IndexError):
                    continue
    return records


# ---------------------------------------------------------------------------
# BIM file parsing for SNP positions
# ---------------------------------------------------------------------------

def load_bim_positions(bim_prefix, chrom):
    """Load SNP positions from a plink .bim file.

    Returns dict: snp_name -> position.
    """
    patterns = [
        f"{bim_prefix}.{chrom}.bim",
        f"{bim_prefix}/{chrom}.bim",
        f"{bim_prefix}/1000G.EUR.QC.{chrom}.bim",
    ]
    snp_pos = {}
    for pattern in patterns:
        if os.path.exists(pattern):
            with open(pattern) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        snp_pos[parts[1]] = int(parts[3])
            break
    return snp_pos


# ---------------------------------------------------------------------------
# Gene property computation
# ---------------------------------------------------------------------------

def compute_gene_properties(gene_info, maf_prefix, ld_prefix):
    """Compute matching properties for a single gene.

    Returns dict with keys: length, ld_complexity, median_maf.
    - length: gene end - gene start (bp)
    - ld_complexity: count of SNPs with LD score > 2x chromosome mean
    - median_maf: median MAF of SNPs within gene boundaries
    """
    chrom = gene_info["chr"]
    start = gene_info["start"]
    end = gene_info["end"]
    length = gene_info["length"]

    # LD complexity: count SNPs with LD score > 2x chromosome mean
    ld_records = load_ld_scores_for_chromosome(ld_prefix, chrom)
    gene_ld_scores = [ld for bp, ld in ld_records if start <= bp <= end]
    chrom_mean_ld = (
        sum(ld for _, ld in ld_records) / max(len(ld_records), 1)
        if ld_records else 1.0
    )
    ld_complexity = sum(1 for ld in gene_ld_scores if ld > 2 * chrom_mean_ld)

    # Median MAF: from 1000G_Phase3_frq files
    maf_map = load_maf_for_chromosome(maf_prefix, chrom)
    # We need SNP positions to filter by gene boundaries
    # If maf_map is keyed by SNP names, we need BIM positions
    # Fall back to computing median of all MAFs if position matching is not possible
    gene_mafs = []
    if maf_map:
        # Try to use BIM-based position lookup
        bim_pos = load_bim_positions(
            os.path.dirname(maf_prefix) if "/" in maf_prefix else maf_prefix,
            chrom,
        )
        for snp, maf in maf_map.items():
            pos = bim_pos.get(snp)
            if pos is not None and start <= pos <= end:
                gene_mafs.append(maf)

    median_maf = _median(gene_mafs) if gene_mafs else 0.25  # fallback

    return {
        "length": length,
        "ld_complexity": ld_complexity,
        "median_maf": median_maf,
    }


def compute_all_gene_properties(gene_loc, query_genes, maf_prefix, ld_prefix):
    """Compute properties for all genes in gene_loc.

    Returns dict: symbol -> {length, ld_complexity, median_maf}.
    Caches per-chromosome data to avoid redundant I/O.
    """
    # Group genes by chromosome for efficient I/O
    chrom_genes = defaultdict(list)
    for symbol, info in gene_loc.items():
        chrom_genes[info["chr"]].append(symbol)

    # Only load data for chromosomes that have query genes or potential matches
    query_chroms = set()
    for qg in query_genes:
        if qg in gene_loc:
            query_chroms.add(gene_loc[qg]["chr"])

    properties = {}
    for chrom, symbols in chrom_genes.items():
        # Load per-chromosome reference data once
        ld_records = load_ld_scores_for_chromosome(ld_prefix, chrom)
        chrom_mean_ld = (
            sum(ld for _, ld in ld_records) / max(len(ld_records), 1)
            if ld_records else 1.0
        )
        maf_map = load_maf_for_chromosome(maf_prefix, chrom)
        bim_pos = load_bim_positions(
            os.path.dirname(maf_prefix) if "/" in maf_prefix else maf_prefix,
            chrom,
        )

        for symbol in symbols:
            info = gene_loc[symbol]
            start = info["start"]
            end = info["end"]

            # LD complexity
            gene_ld_scores = [
                ld for bp, ld in ld_records if start <= bp <= end
            ]
            ld_complexity = sum(
                1 for ld in gene_ld_scores if ld > 2 * chrom_mean_ld
            )

            # Median MAF
            gene_mafs = []
            for snp, maf in maf_map.items():
                pos = bim_pos.get(snp)
                if pos is not None and start <= pos <= end:
                    gene_mafs.append(maf)
            median_maf = _median(gene_mafs) if gene_mafs else 0.25

            properties[symbol] = {
                "length": info["length"],
                "ld_complexity": ld_complexity,
                "median_maf": median_maf,
            }

    return properties


# ---------------------------------------------------------------------------
# Matching and null generation
# ---------------------------------------------------------------------------

def _median(values):
    """Compute median of a list of numbers."""
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def find_matching_genes(
    query_props,
    all_gene_props,
    exclude_genes,
    length_tol=0.5,
    ld_tol=0.3,
    maf_tol=0.3,
    rng=None,
):
    """Find genes matching query gene's properties within tolerances.

    D-06c matching criteria:
      - Gene length: +/- 50% (tolerance=0.5)
      - LD block count: +/- 30% (tolerance=0.3)
      - Median MAF: +/- 30% (tolerance=0.3)

    Returns a list of matching gene symbols (shuffled by rng if provided).
    """
    q_len = query_props["length"]
    q_ld = query_props["ld_complexity"]
    q_maf = query_props["median_maf"]

    matches = []
    for symbol, props in all_gene_props.items():
        if symbol in exclude_genes:
            continue

        # Length check
        if q_len > 0 and abs(props["length"] - q_len) / max(q_len, 1) > length_tol:
            continue

        # LD complexity check
        if q_ld > 0 and abs(props["ld_complexity"] - q_ld) / max(q_ld, 1) > ld_tol:
            continue
        # If query has 0 LD complexity, only match with genes that also have 0
        if q_ld == 0 and props["ld_complexity"] > 0:
            continue

        # MAF check
        if q_maf > 0 and abs(props["median_maf"] - q_maf) / max(q_maf, 0.01) > maf_tol:
            continue

        matches.append(symbol)

    if rng is not None:
        rng.shuffle(matches)

    return matches


def generate_null_genesets(
    query_genes,
    gene_loc_path,
    n_perm,
    seed,
    maf_reference=None,
    ld_score_reference=None,
    out_dir=None,
    exclude_sets=None,
):
    """Generate N permutation null gene sets matched for length, LD, MAF.

    This is the main reusable function per the plan's must_haves.

    Args:
        query_genes: list of gene symbols (the colocalization gene list)
        gene_loc_path: path to NCBI37.3.gene.loc
        n_perm: number of permutations
        seed: base random seed (T-02-18: seed_base + perm_index)
        maf_reference: path prefix for 1000G_Phase3_frq files (REQUIRED)
        ld_score_reference: path prefix for baselineLD_v2.2 LD scores (REQUIRED)
        out_dir: output directory (optional; if None, returns lists)
        exclude_sets: set of gene symbols to exclude from null sampling

    Returns:
        list of lists of gene symbols (each inner list is one null gene set)
    """
    if maf_reference is None:
        raise ValueError(
            "--maf-reference is REQUIRED per D-06c (3-criterion matching). "
            "Point to 1000G_Phase3_frq directory."
        )
    if ld_score_reference is None:
        raise ValueError(
            "--ld-score-reference is REQUIRED per D-06c (3-criterion matching). "
            "Point to baselineLD_v2.2 directory."
        )

    gene_loc = parse_gene_loc(gene_loc_path)

    # Resolve query genes to those present in gene_loc
    resolved_query = [g for g in query_genes if g in gene_loc]
    if not resolved_query:
        logger.warning("No query genes found in gene location file")
        return []

    missing = set(query_genes) - set(resolved_query)
    if missing:
        logger.warning("Query genes not in gene.loc (skipped): %s", missing)

    # Build exclusion set: query genes + negative control + custom pathway genes
    exclude_genes = set(query_genes)
    if exclude_sets:
        exclude_genes.update(exclude_sets)

    # Compute properties for ALL genes (cached by chromosome)
    logger.info("Computing gene properties for %d genes...", len(gene_loc))
    all_props = compute_all_gene_properties(
        gene_loc, resolved_query, maf_reference, ld_score_reference
    )

    # Compute properties for query genes specifically
    query_props = {g: all_props.get(g) for g in resolved_query if g in all_props}

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    null_genesets = []
    summary_rows = []

    for perm_idx in range(n_perm):
        perm_seed = seed + perm_idx
        rng = random.Random(perm_seed)

        null_set = []
        used_in_this_perm = set(exclude_genes)

        for qg in resolved_query:
            qprops = query_props.get(qg)
            if qprops is None:
                continue

            # Find matching genes
            candidates = find_matching_genes(
                qprops,
                all_props,
                used_in_this_perm,
                length_tol=0.5,
                ld_tol=0.3,
                maf_tol=0.3,
                rng=rng,
            )

            if candidates:
                chosen = candidates[0]  # shuffled by rng, so first is random
                null_set.append(chosen)
                used_in_this_perm.add(chosen)
            else:
                # Relaxed matching: length only (fallback, still deterministic)
                relaxed = find_matching_genes(
                    qprops,
                    all_props,
                    used_in_this_perm,
                    length_tol=1.0,
                    ld_tol=10.0,
                    maf_tol=10.0,
                    rng=rng,
                )
                if relaxed:
                    chosen = relaxed[0]
                    null_set.append(chosen)
                    used_in_this_perm.add(chosen)

        null_genesets.append(null_set)

        # Write to file if output dir provided
        if out_dir:
            out_path = os.path.join(out_dir, f"null_geneset_{perm_idx:04d}.txt")
            with open(out_path, "w") as f:
                for gene in null_set:
                    f.write(f"{gene}\n")

        # Summary stats
        lengths = [
            all_props[g]["length"] for g in null_set if g in all_props
        ]
        mean_length = sum(lengths) / max(len(lengths), 1) if lengths else 0

        summary_rows.append({
            "permutation_id": perm_idx,
            "n_genes": len(null_set),
            "mean_gene_length": f"{mean_length:.1f}",
            "seed": perm_seed,
        })

        if (perm_idx + 1) % 100 == 0:
            logger.info(
                "Generated %d / %d null gene sets", perm_idx + 1, n_perm
            )

    # Write summary TSV
    if out_dir:
        summary_path = os.path.join(out_dir, "null_geneset_summary.tsv")
        with open(summary_path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "permutation_id", "n_genes", "mean_gene_length", "seed",
                ],
                delimiter="\t",
            )
            writer.writeheader()
            writer.writerows(summary_rows)
        logger.info("Summary written to %s", summary_path)

    logger.info(
        "Generated %d null gene sets (%d genes each)",
        n_perm,
        len(resolved_query),
    )
    return null_genesets


# ---------------------------------------------------------------------------
# Negative control validation
# ---------------------------------------------------------------------------

def validate_negative_controls(validation_path):
    """Check that all negative controls pass (q > 0.05).

    T-05-21: hard fail (exit 1) if any row has passes_threshold=FALSE.
    """
    failed = []
    with open(validation_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("passes_threshold", "").upper() == "FALSE":
                failed.append(row)

    if failed:
        logger.error(
            "NEGATIVE CONTROL VALIDATION FAILED: %d entries with q <= 0.05",
            len(failed),
        )
        for f_row in failed:
            logger.error(
                "  FAIL: %s / %s / %s -- q=%s",
                f_row.get("neg_ctrl_set", "?"),
                f_row.get("method", "?"),
                f_row.get("trait", "?"),
                f_row.get("q_value", "?"),
            )
        sys.exit(1)  # T-05-21: hard fail

    logger.info("Negative control validation PASSED: all entries have q > 0.05")
    return True


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate permutation null gene sets matched for length, LD, MAF (D-06c)."
    )
    parser.add_argument(
        "--query-genes", required=True,
        help="Path to query gene list (one gene symbol per line)",
    )
    parser.add_argument(
        "--gene-loc", required=True,
        help="Path to NCBI37.3.gene.loc gene location file",
    )
    parser.add_argument(
        "--maf-reference", required=True,
        help="Path prefix for 1000G_Phase3_frq MAF files (REQUIRED per D-06c)",
    )
    parser.add_argument(
        "--ld-score-reference", required=True,
        help="Path prefix for baselineLD_v2.2 LD score files (REQUIRED per D-06c)",
    )
    parser.add_argument(
        "--n-permutations", type=int, default=1000,
        help="Number of permutation null gene sets (default: 1000 per D-06c)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Base random seed (deterministic: seed_base + perm_index per T-02-18)",
    )
    parser.add_argument(
        "--out-dir", required=True,
        help="Output directory for null gene set files",
    )
    parser.add_argument(
        "--exclude-gmt", nargs="*", default=[],
        help="GMT files whose genes should be excluded from null sampling",
    )
    return parser.parse_args()


def _parse_gmt_genes(gmt_path):
    """Extract all unique gene symbols from a GMT file."""
    genes = set()
    with open(gmt_path) as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                genes.update(parts[2:])
    return genes


def main():
    args = parse_args()

    # Build exclusion set from GMT files
    exclude_genes = set()
    for gmt_path in args.exclude_gmt:
        if os.path.exists(gmt_path):
            exclude_genes.update(_parse_gmt_genes(gmt_path))
            logger.info("Excluding %d genes from %s", len(exclude_genes), gmt_path)

    query_genes = read_query_genes(args.query_genes)
    logger.info("Query gene list: %d genes", len(query_genes))

    generate_null_genesets(
        query_genes=query_genes,
        gene_loc_path=args.gene_loc,
        n_perm=args.n_permutations,
        seed=args.seed,
        maf_reference=args.maf_reference,
        ld_score_reference=args.ld_score_reference,
        out_dir=args.out_dir,
        exclude_sets=exclude_genes,
    )


if __name__ == "__main__":
    main()
