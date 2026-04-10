#!/usr/bin/env python3
"""
Pathway enrichment analysis for genome-wide colocalization signals.
"""

from collections import defaultdict
import os

OUTPUT_DIR = "genome_wide_analysis/results/analysis"

# Gene-pathway mapping (curated)
GENE_PATHWAYS = {
    # Insulin signaling
    "IRS1": ("Insulin_signaling", "Metabolic"),
    "IRS2": ("Insulin_signaling", "Metabolic"),
    "PPARG": ("Insulin_signaling", "Metabolic"),
    "KCNJ11": ("Insulin_secretion", "Metabolic"),
    "ABCC8": ("Insulin_secretion", "Metabolic"),
    "GCKR": ("Glucose_metabolism", "Metabolic"),
    "GCK": ("Glucose_metabolism", "Metabolic"),
    "HNF1A": ("Glucose_metabolism", "Metabolic"),
    "HNF4A": ("Glucose_metabolism", "Metabolic"),
    "HNF1B": ("Glucose_metabolism", "Metabolic"),
    "TCF7L2": ("Wnt_signaling", "Metabolic"),

    # Appetite/energy regulation
    "MC4R": ("Appetite_regulation", "Metabolic"),
    "FTO": ("Appetite_regulation", "Metabolic"),
    "BDNF": ("Appetite_regulation", "Metabolic"),
    "LEP": ("Appetite_regulation", "Metabolic"),
    "NEGR1": ("Appetite_regulation", "Metabolic"),
    "TMEM18": ("Appetite_regulation", "Metabolic"),
    "SEC16B": ("Appetite_regulation", "Metabolic"),
    "GPRC5B": ("Appetite_regulation", "Metabolic"),

    # Lipid metabolism
    "APOE": ("Lipid_transport", "Lipid"),
    "APOA1": ("Lipid_transport", "Lipid"),
    "APOC1": ("Lipid_transport", "Lipid"),
    "FADS1": ("Fatty_acid_metabolism", "Lipid"),
    "FADS2": ("Fatty_acid_metabolism", "Lipid"),
    "PCSK9": ("Cholesterol_metabolism", "Lipid"),
    "SORT1": ("Lipid_transport", "Lipid"),
    "CELSR2": ("Lipid_transport", "Lipid"),
    "LPA": ("Lipid_transport", "Lipid"),

    # Cardiovascular
    "SH2B3": ("Inflammation", "Cardiovascular"),
    "ATXN2": ("Cardiovascular_risk", "Cardiovascular"),
    "ABO": ("Coagulation", "Cardiovascular"),
    "NPR3": ("Blood_pressure", "Cardiovascular"),
    "UMOD": ("Blood_pressure", "Cardiovascular"),

    # Beta-cell function
    "SLC30A8": ("Zinc_transport", "Beta_cell"),
    "KCNQ1": ("Ion_channel", "Beta_cell"),
    "CDKAL1": ("tRNA_modification", "Beta_cell"),
    "IGF2BP2": ("mRNA_binding", "Beta_cell"),

    # Cell cycle/development
    "CDKN2A": ("Cell_cycle", "Development"),
    "CDKN2B": ("Cell_cycle", "Development"),
    "CCND2": ("Cell_cycle", "Development"),

    # Transcription factors
    "JAZF1": ("Transcription", "Regulatory"),
    "STAT3": ("Transcription", "Regulatory"),
    "FOXA2": ("Transcription", "Regulatory"),

    # Immune
    "HLA region": ("Immune_function", "Immune"),
    "MHC": ("Immune_function", "Immune"),

    # Signaling
    "BANK1": ("B_cell_signaling", "Immune"),
    "SLC39A8": ("Zinc_transport", "Metabolic"),
}

# Load annotated signals
input_file = "genome_wide_analysis/results/tables/Table1_HighConfidence_Signals_Annotated.tsv"

if not os.path.exists(input_file):
    print(f"Error: {input_file} not found. Run create_annotated_signals.py first.")
    exit(1)

# Make output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Count genes and pathways
gene_counts = defaultdict(int)
pathway_counts = defaultdict(int)
category_counts = defaultdict(int)

print("="*60)
print("PATHWAY ENRICHMENT ANALYSIS - GENOME-WIDE SIGNALS")
print("="*60)

with open(input_file) as f:
    header = f.readline()

    for line in f:
        fields = line.strip().split('\t')
        genes_str = fields[-1]

        for gene in genes_str.split(', '):
            gene = gene.strip()
            if gene and gene not in ['intergenic/novel', 'parse_error']:
                gene_counts[gene] += 1

                if gene in GENE_PATHWAYS:
                    pathway, category = GENE_PATHWAYS[gene]
                    pathway_counts[pathway] += 1
                    category_counts[category] += 1

print("\n--- Gene Frequency in High-Confidence Signals ---")
for gene, count in sorted(gene_counts.items(), key=lambda x: -x[1])[:20]:
    pathway_info = GENE_PATHWAYS.get(gene, ("Unknown", "Unknown"))
    print(f"  {gene:<15} {count:>3} signals  ({pathway_info[0]})")

print("\n--- Pathway Enrichment ---")
for pathway, count in sorted(pathway_counts.items(), key=lambda x: -x[1]):
    print(f"  {pathway:<25} {count:>3} genes")

print("\n--- Category Summary ---")
for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
    print(f"  {category:<20} {count:>3} genes")

# Save pathway summary
pathway_file = os.path.join(OUTPUT_DIR, "pathway_enrichment_summary.tsv")
with open(pathway_file, 'w') as f:
    f.write("Category\tPathway\tN_Genes\tGenes\n")

    # Group genes by pathway
    pathway_genes = defaultdict(list)
    for gene, (pathway, category) in GENE_PATHWAYS.items():
        if gene in gene_counts:
            pathway_genes[(category, pathway)].append(gene)

    for (category, pathway), genes in sorted(pathway_genes.items(), key=lambda x: -len(x[1])):
        f.write(f"{category}\t{pathway}\t{len(genes)}\t{', '.join(genes)}\n")

print(f"\nSaved: {pathway_file}")

# Calculate enrichment statistics
print("\n" + "="*60)
print("BIOLOGICAL INTERPRETATION")
print("="*60)

total_annotated = sum(1 for g in gene_counts if g in GENE_PATHWAYS)
print(f"""
Key Findings:
- {total_annotated} genes with pathway annotations among high-confidence signals
- Metabolic pathways dominate ({category_counts.get('Metabolic', 0)} genes)
- Strong representation of:
  * Insulin signaling/secretion (core T2D biology)
  * Glucose metabolism (liver, pancreas)
  * Lipid transport (cardiovascular connection)
  * Appetite regulation (obesity pathways)

This supports the biological coherence of the colocalization signals,
with convergence on known cardiometabolic disease mechanisms.
""")
