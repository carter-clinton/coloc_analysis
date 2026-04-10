#!/usr/bin/env python3
"""
Create manifest of all colocalization tests for genome-wide analysis.
"""

import os
import sys
from itertools import combinations

# Configuration
REGIONS_FILE = "config/genomewide_regions.tsv"
SUMSTATS_DIR = sys.argv[1] if len(sys.argv) > 1 else "data_processed/harmonized_fixed"
OUTPUT_FILE = "config/genomewide_coloc_manifest.tsv"

# Define trait pairs
EUR_TRAITS = ["bmi", "t2d", "hypertension", "stroke", "asthma"]
AFR_TRAITS = ["t2d", "stroke", "asthma"]

print("="*70)
print("CREATING COLOCALIZATION MANIFEST")
print("="*70)

# Load regions
regions = []
with open(REGIONS_FILE) as f:
    header = f.readline()
    for line in f:
        fields = line.strip().split('\t')
        regions.append({
            'region_id': fields[0],
            'chr': fields[1],
            'start': fields[2],
            'end': fields[3]
        })

print(f"Loaded {len(regions)} regions")

# Check available files
available_files = {}
for trait in EUR_TRAITS:
    f = os.path.join(SUMSTATS_DIR, f"{trait}.EUR.tsv.bgz")
    if os.path.exists(f):
        available_files[f"{trait}.EUR"] = f
        
for trait in AFR_TRAITS:
    f = os.path.join(SUMSTATS_DIR, f"{trait}.AFR.tsv.bgz")
    if os.path.exists(f):
        available_files[f"{trait}.AFR"] = f

print(f"Available sumstats files: {len(available_files)}")
for k in sorted(available_files.keys()):
    print(f"  {k}")

# Generate trait pairs
eur_pairs = list(combinations(EUR_TRAITS, 2))
afr_pairs = list(combinations(AFR_TRAITS, 2))

print(f"\nEUR trait pairs: {len(eur_pairs)}")
print(f"AFR trait pairs: {len(afr_pairs)}")

# Create manifest
manifest = []

# EUR pairs
for region in regions:
    for trait_a, trait_b in eur_pairs:
        key_a = f"{trait_a}.EUR"
        key_b = f"{trait_b}.EUR"
        
        if key_a in available_files and key_b in available_files:
            pair_id = f"{region['region_id']}__EUR__{trait_a}_vs_{trait_b}"
            manifest.append({
                'pair_id': pair_id,
                'region_id': region['region_id'],
                'chr': region['chr'],
                'start': region['start'],
                'end': region['end'],
                'ancestry': 'EUR',
                'trait_a': trait_a,
                'trait_b': trait_b,
                'path_a': available_files[key_a],
                'path_b': available_files[key_b]
            })

# AFR pairs
for region in regions:
    for trait_a, trait_b in afr_pairs:
        key_a = f"{trait_a}.AFR"
        key_b = f"{trait_b}.AFR"
        
        if key_a in available_files and key_b in available_files:
            pair_id = f"{region['region_id']}__AFR__{trait_a}_vs_{trait_b}"
            manifest.append({
                'pair_id': pair_id,
                'region_id': region['region_id'],
                'chr': region['chr'],
                'start': region['start'],
                'end': region['end'],
                'ancestry': 'AFR',
                'trait_a': trait_a,
                'trait_b': trait_b,
                'path_a': available_files[key_a],
                'path_b': available_files[key_b]
            })

print(f"\nTotal colocalization tests: {len(manifest)}")
print(f"  EUR: {len([m for m in manifest if m['ancestry'] == 'EUR'])}")
print(f"  AFR: {len([m for m in manifest if m['ancestry'] == 'AFR'])}")

# Save manifest
with open(OUTPUT_FILE, 'w') as f:
    header = ['pair_id', 'region_id', 'chr', 'start', 'end', 'ancestry', 'trait_a', 'trait_b', 'path_a', 'path_b']
    f.write('\t'.join(header) + '\n')
    
    for m in manifest:
        row = [str(m[h]) for h in header]
        f.write('\t'.join(row) + '\n')

print(f"\nSaved manifest to: {OUTPUT_FILE}")

# Save pair IDs for batch processing
pair_ids_file = "config/coloc_pair_ids.txt"
with open(pair_ids_file, 'w') as f:
    for m in manifest:
        f.write(m['pair_id'] + '\n')

print(f"Saved pair IDs to: {pair_ids_file}")
