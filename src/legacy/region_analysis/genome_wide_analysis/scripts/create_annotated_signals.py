#!/usr/bin/env python3
"""
Create annotated high-confidence signals table from colocalization results.
Extracts gene names from locus identifiers and filters for high PP.H4 signals.
"""

import os

# Input/output paths
INPUT_FILE = "results/multitrait/coloc_clean_h4.tsv"
OUTPUT_DIR = "genome_wide_analysis/results/tables"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Table1_HighConfidence_Signals_Annotated.tsv")

# PP.H4 threshold for high-confidence signals
H4_THRESHOLD = 0.8

# Gene mapping from locus names (known genes in locus identifiers)
LOCUS_TO_GENE = {
    "APOE": "APOE",
    "APOA": "APOA1",
    "FADS1": "FADS1",
    "FADS2": "FADS2",
    "FTO": "FTO",
    "GCKR": "GCKR",
    "IRS1": "IRS1",
    "IRS2": "IRS2",
    "KCNJ11": "KCNJ11",
    "MC4R": "MC4R",
    "TCF7L2": "TCF7L2",
    "PPARG": "PPARG",
    "SH2B3": "SH2B3",
    "CDKN2": "CDKN2A, CDKN2B",
    "HNF1A": "HNF1A",
    "HNF4A": "HNF4A",
    "HNF1B": "HNF1B",
    "SLC30A8": "SLC30A8",
    "KCNQ1": "KCNQ1",
    "CDKAL1": "CDKAL1",
    "IGF2BP2": "IGF2BP2",
    "JAZF1": "JAZF1",
    "GCK": "GCK",
    "ABCC8": "ABCC8",
    "PCSK9": "PCSK9",
    "SORT1": "SORT1",
    "CELSR2": "CELSR2",
    "ATXN2": "ATXN2",
    "BDNF": "BDNF",
    "LEP": "LEP",
    "LPA": "LPA",
    "NEGR1": "NEGR1",
    "SEC16B": "SEC16B",
    "TMEM18": "TMEM18",
    "GPRC5B": "GPRC5B",
    "NPR3": "NPR3",
    "UMOD": "UMOD",
    "BMI": "intergenic/novel",
    "HLA": "HLA region",
    "MHC": "MHC",
    "BANK1": "BANK1",
    "SLC39A8": "SLC39A8",
    "ABO": "ABO",
    "STAT3": "STAT3",
    "FOXA2": "FOXA2",
    "CCND2": "CCND2",
}


def extract_gene_from_locus(locus_id):
    """Extract gene name from locus identifier."""
    # Locus format is typically: GENE_CHRp/q or GENE_region
    locus_upper = locus_id.upper()

    # Check each known gene pattern
    for pattern, gene in LOCUS_TO_GENE.items():
        if pattern.upper() in locus_upper:
            return gene

    # If no match, try to extract gene name from start of locus ID
    parts = locus_id.split('_')
    if parts:
        # Check if first part looks like a gene name
        first_part = parts[0]
        if first_part.isalpha() or (first_part[:-1].isalpha() and first_part[-1].isdigit()):
            return first_part

    return "intergenic/novel"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found")
        return

    high_conf_signals = []

    with open(INPUT_FILE) as f:
        header = f.readline().strip().split('\t')

        # Find column indices
        h4_idx = header.index('PP.H4')
        locus_idx = header.index('base_region')
        ancestry_idx = header.index('ancestry')
        trait_a_idx = header.index('trait_a')
        trait_b_idx = header.index('trait_b')
        chr_idx = header.index('chr_a')
        start_idx = header.index('start_a')
        end_idx = header.index('end_a')

        for line in f:
            fields = line.strip().split('\t')

            try:
                h4 = float(fields[h4_idx])
            except (ValueError, IndexError):
                continue

            if h4 >= H4_THRESHOLD:
                locus = fields[locus_idx]
                ancestry = fields[ancestry_idx]
                trait_a = fields[trait_a_idx]
                trait_b = fields[trait_b_idx]
                chrom = fields[chr_idx]
                start = fields[start_idx]
                end = fields[end_idx]
                gene = extract_gene_from_locus(locus)

                high_conf_signals.append({
                    'locus': locus,
                    'chr': chrom,
                    'start': start,
                    'end': end,
                    'ancestry': ancestry,
                    'trait_a': trait_a,
                    'trait_b': trait_b,
                    'PP_H4': h4,
                    'genes': gene
                })

    # Sort by PP.H4 descending
    high_conf_signals.sort(key=lambda x: -x['PP_H4'])

    # Write output
    with open(OUTPUT_FILE, 'w') as f:
        f.write("Locus\tChr\tStart\tEnd\tAncestry\tTrait_A\tTrait_B\tPP_H4\tGenes\n")

        for sig in high_conf_signals:
            f.write(f"{sig['locus']}\t{sig['chr']}\t{sig['start']}\t{sig['end']}\t")
            f.write(f"{sig['ancestry']}\t{sig['trait_a']}\t{sig['trait_b']}\t")
            f.write(f"{sig['PP_H4']:.4f}\t{sig['genes']}\n")

    print(f"Created {OUTPUT_FILE}")
    print(f"Total high-confidence signals (PP.H4 >= {H4_THRESHOLD}): {len(high_conf_signals)}")

    # Print gene summary
    from collections import Counter
    gene_counts = Counter()
    for sig in high_conf_signals:
        for g in sig['genes'].split(', '):
            gene_counts[g.strip()] += 1

    print("\nTop genes in high-confidence signals:")
    for gene, count in gene_counts.most_common(15):
        print(f"  {gene}: {count}")


if __name__ == "__main__":
    main()
