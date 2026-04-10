#!/usr/bin/env python3
"""
Annotate colocalization signals with gene names based on genomic coordinates.
Uses a curated list of known cardiometabolic genes at GWAS loci.
"""

import os

# Curated gene annotations for major cardiometabolic GWAS loci
# Format: (chr, start_mb, end_mb): [genes]
GENE_ANNOTATIONS = {
    # Chromosome 1
    (1, 55, 58): ["PCSK9", "BSND"],
    (1, 76, 81): ["ST6GALNAC3", "PIGC"],
    (1, 109, 112): ["CELSR2", "PSRC1", "SORT1"],
    (1, 219, 222): ["LYPLAL1"],
    
    # Chromosome 2
    (2, 27, 28): ["GCKR"],
    (2, 43, 46): ["THADA"],
    (2, 60, 63): ["BCL11A"],
    (2, 165, 168): ["COBLL1", "GRB14"],
    (2, 226, 228): ["IRS1"],
    
    # Chromosome 3
    (3, 12, 14): ["PPARG"],
    (3, 64, 67): ["ADAMTS9"],
    (3, 185, 188): ["IGF2BP2"],
    
    # Chromosome 4
    (4, 88, 90): ["MEPE", "SPP1"],  # Bone metabolism
    (4, 100, 107): ["BANK1", "SLC39A8", "MANBA"],  # Major pleiotropic hub
    (4, 129, 131): ["PABPC4L"],
    
    # Chromosome 5
    (5, 53, 56): ["ARL15"],
    (5, 76, 79): ["ZBED3", "PDE8B"],
    (5, 172, 176): ["CPEB4"],
    
    # Chromosome 6
    (6, 16, 36): ["HLA region", "MHC"],  # Major histocompatibility complex
    (6, 20, 22): ["CDKAL1"],
    (6, 126, 129): ["CENPW"],
    (6, 39, 41): ["KCNK5"],
    
    # Chromosome 7
    (7, 14, 16): ["DGKB"],
    (7, 28, 30): ["JAZF1"],
    (7, 44, 46): ["GCK"],
    (7, 127, 130): ["PAX4", "LEP"],
    
    # Chromosome 8
    (8, 9, 11): ["MSRA"],
    (8, 41, 43): ["ANK1"],
    (8, 118, 120): ["SLC30A8"],
    
    # Chromosome 9
    (9, 4, 6): ["GLIS3"],
    (9, 21, 23): ["CDKN2A", "CDKN2B"],
    (9, 136, 139): ["ABO"],
    
    # Chromosome 10
    (10, 12, 14): ["CDC123", "CAMK1D"],
    (10, 63, 66): ["ARID5B"],
    (10, 69, 72): ["HHEX", "IDE"],
    (10, 94, 96): ["KCNMA1"],
    (10, 113, 117): ["TCF7L2"],  # Major T2D gene
    
    # Chromosome 11
    (11, 2, 4): ["KCNQ1"],
    (11, 17, 19): ["KCNJ11", "ABCC8"],
    (11, 42, 44): ["LRRC4C"],
    (11, 47, 49): ["NR1H3", "MADD"],
    (11, 61, 63): ["FADS1", "FADS2"],
    (11, 72, 74): ["ARAP1"],
    (11, 116, 118): ["APOA1", "APOC3", "APOA4"],
    
    # Chromosome 12
    (12, 4, 6): ["CCND2"],
    (12, 26, 28): ["ITPR2"],
    (12, 66, 68): ["HMGA2"],
    (12, 71, 73): ["TSPAN8", "LGR5"],
    (12, 111, 113): ["SH2B3", "ATXN2"],
    (12, 121, 124): ["HNF1A"],
    
    # Chromosome 13
    (13, 80, 82): ["SPRY2"],
    
    # Chromosome 14
    (14, 101, 103): ["MARK3"],
    
    # Chromosome 15
    (15, 62, 64): ["C2CD4A", "C2CD4B"],
    (15, 77, 79): ["HMG20A"],
    (15, 89, 91): ["FURIN", "FES"],
    
    # Chromosome 16
    (16, 4, 6): ["RBFOX1"],
    (16, 53, 55): ["FTO"],  # Major obesity gene
    (16, 75, 77): ["BCAR1", "CFDP1"],
    
    # Chromosome 17
    (17, 7, 9): ["SLC16A11", "SLC16A13"],
    (17, 36, 38): ["HNF1B"],
    (17, 40, 42): ["STAT3"],
    
    # Chromosome 18
    (18, 7, 9): ["PTPN2"],
    (18, 42, 44): ["SETBP1"],
    (18, 56, 58): ["MC4R"],  # Appetite regulation
    (18, 59, 61): ["PMAIP1", "MC4R region"],  # Pleiotropic hub
    (18, 62, 64): ["BCL2"],
    
    # Chromosome 19
    (19, 7, 9): ["JUND", "PGPEP1"],
    (19, 33, 35): ["PEPD"],
    (19, 45, 47): ["APOE", "APOC1", "APOC2"],  # Lipid metabolism
    (19, 52, 54): ["GIPR"],
    
    # Chromosome 20
    (20, 22, 24): ["FOXA2"],
    (20, 42, 44): ["HNF4A"],
    (20, 62, 64): ["ZGPAT"],
    
    # Chromosome 22
    (22, 28, 30): ["MTMR3"],
}

def get_genes_for_region(region_str):
    """Map a region string to gene names."""
    try:
        # Parse region: "chr4:100250000-107250000" or "4:100250000-107250000"
        parts = region_str.replace('chr', '').split(':')
        chrom = int(parts[0])
        coords = parts[1].split('-')
        start_bp = int(coords[0])
        end_bp = int(coords[1])
        
        start_mb = start_bp / 1e6
        end_mb = end_bp / 1e6
        
        # Find matching genes
        genes = []
        for (c, s, e), gene_list in GENE_ANNOTATIONS.items():
            if c == chrom:
                # Check for overlap
                if not (end_mb < s or start_mb > e):
                    genes.extend(gene_list)
        
        return list(set(genes)) if genes else ["intergenic/novel"]
    except:
        return ["parse_error"]

# Load high-confidence signals
input_file = "results/tables/Table1_HighConfidence_Signals.tsv"
output_file = "results/tables/Table1_HighConfidence_Signals_Annotated.tsv"

print("Annotating high-confidence signals with gene names...")

with open(input_file) as f_in, open(output_file, 'w') as f_out:
    header = f_in.readline().strip()
    f_out.write(header + "\tGenes\n")
    
    for line in f_in:
        fields = line.strip().split('\t')
        region = fields[1]  # Region column
        genes = get_genes_for_region(region)
        gene_str = ", ".join(genes)
        f_out.write(line.strip() + "\t" + gene_str + "\n")

print(f"Saved annotated table: {output_file}")

# Also annotate pleiotropic loci
pleio_input = "results/tables/Table3_Pleiotropic_Loci.tsv"
pleio_output = "results/tables/Table3_Pleiotropic_Loci_Annotated.tsv"

print("\nAnnotating pleiotropic loci...")

with open(pleio_input) as f_in, open(pleio_output, 'w') as f_out:
    header = f_in.readline().strip()
    f_out.write(header + "\tGenes\n")
    
    for line in f_in:
        fields = line.strip().split('\t')
        region = fields[0]  # Region column
        genes = get_genes_for_region(region)
        gene_str = ", ".join(genes)
        f_out.write(line.strip() + "\t" + gene_str + "\n")

print(f"Saved annotated table: {pleio_output}")

# Create summary of top genes
print("\n" + "="*60)
print("TOP SIGNALS WITH GENE ANNOTATIONS")
print("="*60)

with open(output_file) as f:
    header = f.readline()
    print(f"\n{'Rank':<5} {'Region':<25} {'Traits':<20} {'H4':>8}  Genes")
    print("-" * 85)
    
    for i, line in enumerate(f):
        if i >= 20:
            break
        fields = line.strip().split('\t')
        rank = fields[0]
        region = fields[1][:24]
        traits = f"{fields[3]}-{fields[4]}"
        h4 = fields[5]
        genes = fields[-1][:30]
        print(f"{rank:<5} {region:<25} {traits:<20} {h4:>8}  {genes}")

print("\nAnnotation complete!")
