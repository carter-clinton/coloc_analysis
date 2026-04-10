#!/usr/bin/env python3
"""
Identify all genome-wide significant loci across traits for colocalization analysis.

Strategy:
1. Extract all variants with P < 5e-8 from each trait
2. Group into 1Mb windows
3. Merge overlapping windows across traits
4. Output final region list
"""

import gzip
import os
import sys
from collections import defaultdict

# Configuration
SUMSTATS_DIR = sys.argv[1] if len(sys.argv) > 1 else "data_processed/harmonized_fixed"
OUTPUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "config"
P_THRESHOLD = 5e-8
WINDOW_SIZE = 1000000  # 1Mb
MERGE_DISTANCE = 500000  # Merge windows within 500kb

# Traits and ancestries
EUR_TRAITS = ["bmi", "t2d", "hypertension", "stroke", "asthma"]
AFR_TRAITS = ["t2d", "stroke", "asthma"]

print("="*70)
print("GENOME-WIDE REGION IDENTIFICATION")
print("="*70)
print(f"P-value threshold: {P_THRESHOLD}")
print(f"Window size: {WINDOW_SIZE/1e6}Mb")
print(f"Merge distance: {MERGE_DISTANCE/1e3}kb")
print()

def parse_sumstats(filepath, p_threshold):
    """Extract significant variants from summary statistics."""
    significant = []
    
    if not os.path.exists(filepath):
        print(f"  File not found: {filepath}")
        return significant
    
    with gzip.open(filepath, 'rt') as f:
        header = f.readline().strip().split('\t')
        
        # Find column indices
        col_idx = {col: i for i, col in enumerate(header)}
        chr_col = col_idx.get('CHR', col_idx.get('chr', -1))
        pos_col = col_idx.get('POS', col_idx.get('pos', -1))
        p_col = col_idx.get('P', col_idx.get('p', col_idx.get('pvalue', -1)))
        
        if chr_col < 0 or pos_col < 0 or p_col < 0:
            print(f"  Missing columns in {filepath}")
            print(f"  Header: {header}")
            return significant
        
        for line in f:
            fields = line.strip().split('\t')
            try:
                chrom = fields[chr_col].replace('chr', '')
                if not chrom.isdigit():
                    continue
                chrom = int(chrom)
                pos = int(fields[pos_col])
                p = float(fields[p_col])
                
                if p < p_threshold:
                    significant.append((chrom, pos, p))
            except (ValueError, IndexError):
                continue
    
    return significant

def create_windows(variants, window_size):
    """Group variants into windows."""
    windows = defaultdict(list)
    
    for chrom, pos, p in variants:
        window_start = (pos // window_size) * window_size
        window_end = window_start + window_size
        window_id = f"chr{chrom}_{window_start}_{window_end}"
        windows[window_id].append((chrom, pos, p))
    
    return windows

def merge_nearby_windows(windows, merge_distance):
    """Merge windows that are close together."""
    # Group by chromosome
    by_chrom = defaultdict(list)
    for window_id, variants in windows.items():
        chrom = int(window_id.split('_')[0].replace('chr', ''))
        start = int(window_id.split('_')[1])
        end = int(window_id.split('_')[2])
        min_p = min(v[2] for v in variants)
        by_chrom[chrom].append((start, end, min_p, variants))
    
    # Merge within each chromosome
    merged = {}
    for chrom, regions in by_chrom.items():
        regions.sort(key=lambda x: x[0])
        
        merged_regions = []
        current = list(regions[0])
        
        for start, end, min_p, variants in regions[1:]:
            if start - current[1] <= merge_distance:
                # Merge
                current[1] = max(current[1], end)
                current[2] = min(current[2], min_p)
                current[3] = current[3] + variants
            else:
                merged_regions.append(current)
                current = [start, end, min_p, variants]
        
        merged_regions.append(current)
        
        for start, end, min_p, variants in merged_regions:
            # Extend by 250kb on each side for colocalization
            final_start = max(0, start - 250000)
            final_end = end + 250000
            window_id = f"chr{chrom}_{final_start}_{final_end}"
            merged[window_id] = {
                'chrom': chrom,
                'start': final_start,
                'end': final_end,
                'min_p': min_p,
                'n_variants': len(variants)
            }
    
    return merged

# Collect significant variants from all traits
all_variants = []
trait_counts = {}

print("Scanning summary statistics files:")
print()

# EUR traits
for trait in EUR_TRAITS:
    filepath = os.path.join(SUMSTATS_DIR, f"{trait}.EUR.tsv.bgz")
    print(f"  {trait}.EUR: ", end="", flush=True)
    variants = parse_sumstats(filepath, P_THRESHOLD)
    print(f"{len(variants)} significant variants")
    trait_counts[f"{trait}.EUR"] = len(variants)
    all_variants.extend(variants)

print()

# AFR traits
for trait in AFR_TRAITS:
    filepath = os.path.join(SUMSTATS_DIR, f"{trait}.AFR.tsv.bgz")
    print(f"  {trait}.AFR: ", end="", flush=True)
    variants = parse_sumstats(filepath, P_THRESHOLD)
    print(f"{len(variants)} significant variants")
    trait_counts[f"{trait}.AFR"] = len(variants)

print()
print(f"Total significant variants: {len(all_variants)}")

# Create windows
print()
print("Creating windows...")
windows = create_windows(all_variants, WINDOW_SIZE)
print(f"  Initial windows: {len(windows)}")

# Merge nearby windows
merged = merge_nearby_windows(windows, MERGE_DISTANCE)
print(f"  After merging: {len(merged)}")

# Save regions
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_file = os.path.join(OUTPUT_DIR, "genomewide_regions.tsv")

with open(output_file, 'w') as f:
    f.write("region_id\tchr\tstart\tend\tsize_kb\tmin_p\tn_gwsig_variants\n")
    
    for region_id in sorted(merged.keys(), key=lambda x: (merged[x]['chrom'], merged[x]['start'])):
        r = merged[region_id]
        size_kb = (r['end'] - r['start']) / 1000
        f.write(f"{region_id}\t{r['chrom']}\t{r['start']}\t{r['end']}\t{size_kb:.1f}\t{r['min_p']:.2e}\t{r['n_variants']}\n")

print()
print(f"Saved regions to: {output_file}")

# Summary statistics
print()
print("="*70)
print("SUMMARY")
print("="*70)
print(f"Total genome-wide significant regions: {len(merged)}")
print()
print("Regions by chromosome:")
chrom_counts = defaultdict(int)
for region_id, r in merged.items():
    chrom_counts[r['chrom']] += 1
for chrom in sorted(chrom_counts.keys()):
    print(f"  Chr{chrom}: {chrom_counts[chrom]}")

print()
print("Region size distribution:")
sizes = [(r['end'] - r['start'])/1000 for r in merged.values()]
print(f"  Min: {min(sizes):.0f} kb")
print(f"  Max: {max(sizes):.0f} kb")
print(f"  Mean: {sum(sizes)/len(sizes):.0f} kb")

# Save trait hit counts
counts_file = os.path.join(OUTPUT_DIR, "gwas_hit_counts.tsv")
with open(counts_file, 'w') as f:
    f.write("trait_ancestry\tn_significant_variants\n")
    for trait, count in sorted(trait_counts.items()):
        f.write(f"{trait}\t{count}\n")

print()
print(f"Saved hit counts to: {counts_file}")
