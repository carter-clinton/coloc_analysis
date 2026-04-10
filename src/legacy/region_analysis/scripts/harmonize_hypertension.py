#!/usr/bin/env python3
"""
Harmonize hypertension (Evangelou 2018) summary statistics.
Parses CHR:POS from MarkerName column.
"""

import gzip
import sys
from pathlib import Path

INPUT = Path("data_raw/sumstats/hypertension.EUR.raw.gz")
OUTPUT = Path("data_processed/harmonized_fixed/hypertension.EUR.tsv.bgz")

print(f"Input: {INPUT}")
print(f"Output: {OUTPUT}")

# Column mapping from raw file
# MarkerName Allele1 Allele2 Freq1 Effect StdErr P TotalSampleSize N_effective
# Allele1 = effect allele (ALT), Allele2 = other allele (REF)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with gzip.open(INPUT, 'rt') as fin, gzip.open(OUTPUT, 'wt') as fout:
    # Write header
    fout.write("CHR\tPOS\tREF\tALT\tBETA\tSE\tP\tEAF\tN\n")
    
    header = fin.readline().strip().split()
    print(f"Input columns: {header}")
    
    # Find column indices
    marker_idx = header.index("MarkerName")
    a1_idx = header.index("Allele1")  # Effect allele = ALT
    a2_idx = header.index("Allele2")  # Other allele = REF
    freq_idx = header.index("Freq1")   # EAF of Allele1
    beta_idx = header.index("Effect")
    se_idx = header.index("StdErr")
    p_idx = header.index("P")
    n_idx = header.index("TotalSampleSize")
    
    kept = 0
    skipped = 0
    
    for line in fin:
        fields = line.strip().split()
        
        # Parse MarkerName (format: CHR:POS:TYPE or CHR:POS)
        marker = fields[marker_idx]
        parts = marker.split(":")
        
        if len(parts) < 2:
            skipped += 1
            continue
        
        chrom = parts[0]
        pos = parts[1]
        
        # Skip non-numeric chromosomes (X, Y, MT) for now
        try:
            int(chrom)
            int(pos)
        except ValueError:
            skipped += 1
            continue
        
        # Get alleles (uppercase)
        alt = fields[a1_idx].upper()  # Effect allele
        ref = fields[a2_idx].upper()  # Other allele
        
        # Skip if alleles are not single nucleotides
        if len(alt) != 1 or len(ref) != 1:
            skipped += 1
            continue
        
        if alt not in "ACGT" or ref not in "ACGT":
            skipped += 1
            continue
        
        # Get stats
        beta = fields[beta_idx]
        se = fields[se_idx]
        p = fields[p_idx]
        eaf = fields[freq_idx]
        n = fields[n_idx]
        
        # Write output
        fout.write(f"{chrom}\t{pos}\t{ref}\t{alt}\t{beta}\t{se}\t{p}\t{eaf}\t{n}\n")
        kept += 1
        
        if kept % 1000000 == 0:
            print(f"  Processed {kept:,} variants...")

print(f"\nDone: {kept:,} kept, {skipped:,} skipped")
