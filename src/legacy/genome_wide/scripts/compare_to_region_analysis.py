#!/usr/bin/env python3
"""
Compare genome-wide results with original 50-region analysis.
"""

import os

REGION_DIR = "/share/clintonlab/ckclinto/admixmap/region_analysis"
GW_DIR = "/share/clintonlab/ckclinto/admixmap/genome_wide"

print("="*70)
print("COMPARISON: 50-REGION vs GENOME-WIDE ANALYSIS")
print("="*70)

# Load 50-region results
region_file = os.path.join(REGION_DIR, "results/multitrait/coloc_summary_comprehensive.tsv")

region_results = []
if os.path.exists(region_file):
    with open(region_file) as f:
        header = f.readline().strip().split('\t')
        col_map = {col: i for i, col in enumerate(header)}
        
        for line in f:
            fields = line.strip().split('\t')
            try:
                h4_col = col_map.get('PP.H4', -1)
                anc_col = col_map.get('ancestry', -1)
                
                h4 = float(fields[h4_col]) if h4_col >= 0 and fields[h4_col] not in ['', 'NA'] else 0
                anc = fields[anc_col] if anc_col >= 0 else ''
                region_results.append({'h4': h4, 'ancestry': anc, 'fields': fields})
            except:
                pass
    print(f"Loaded 50-region results: {len(region_results)}")
else:
    print(f"50-region file not found: {region_file}")
    # Try alternate location
    alt_files = [
        os.path.join(REGION_DIR, "results/coloc_summary.tsv"),
        os.path.join(REGION_DIR, "results/analysis/coloc_summary.tsv"),
    ]
    for alt in alt_files:
        if os.path.exists(alt):
            print(f"  Found alternative: {alt}")
            break

# Load genome-wide results
gw_file = os.path.join(GW_DIR, "results/analysis/genomewide_coloc_summary.tsv")

gw_results = []
if os.path.exists(gw_file):
    with open(gw_file) as f:
        header = f.readline().strip().split('\t')
        col_map = {col: i for i, col in enumerate(header)}
        
        for line in f:
            fields = line.strip().split('\t')
            try:
                status_col = col_map.get('status', -1)
                h4_col = col_map.get('PP.H4', -1)
                anc_col = col_map.get('ancestry', -1)
                
                status = fields[status_col] if status_col >= 0 else ''
                if status != 'SUCCESS':
                    continue
                    
                h4 = float(fields[h4_col]) if h4_col >= 0 and fields[h4_col] not in ['', 'NA'] else 0
                anc = fields[anc_col] if anc_col >= 0 else ''
                gw_results.append({'h4': h4, 'ancestry': anc, 'fields': fields})
            except:
                pass
    print(f"Loaded genome-wide results: {len(gw_results)}")
else:
    print(f"Genome-wide file not found: {gw_file}")

# Comparison
print("\n" + "-"*70)
print(f"{'METRIC':<40} {'50-REGION':>12} {'GENOME-WIDE':>12} {'CHANGE':>12}")
print("-"*70)

def count_by_threshold(results, threshold, ancestry=None):
    if ancestry:
        return sum(1 for r in results if r['h4'] >= threshold and r['ancestry'] == ancestry)
    return sum(1 for r in results if r['h4'] >= threshold)

# Overall stats
n_region = len(region_results)
n_gw = len(gw_results)
print(f"{'Total successful tests':<40} {n_region:>12} {n_gw:>12} {n_gw/max(n_region,1):.1f}x")

# By threshold
for thresh, label in [(0.8, "H4 >= 0.8 (high confidence)"), 
                       (0.5, "H4 >= 0.5 (moderate)"),
                       (0.2, "H4 >= 0.2 (suggestive)")]:
    n_r = count_by_threshold(region_results, thresh)
    n_g = count_by_threshold(gw_results, thresh)
    change = f"{n_g/max(n_r,1):.1f}x" if n_r > 0 else f"+{n_g}"
    print(f"{label:<40} {n_r:>12} {n_g:>12} {change:>12}")

print("-"*70)

# By ancestry
print(f"\n{'EUR ANCESTRY':<40}")
for thresh in [0.8, 0.5]:
    n_r = count_by_threshold(region_results, thresh, 'EUR')
    n_g = count_by_threshold(gw_results, thresh, 'EUR')
    change = f"{n_g/max(n_r,1):.1f}x" if n_r > 0 else f"+{n_g}"
    print(f"  H4 >= {thresh:<36} {n_r:>12} {n_g:>12} {change:>12}")

print(f"\n{'AFR ANCESTRY':<40}")
for thresh in [0.1, 0.05]:
    n_r = count_by_threshold(region_results, thresh, 'AFR')
    n_g = count_by_threshold(gw_results, thresh, 'AFR')
    change = f"{n_g/max(n_r,1):.1f}x" if n_r > 0 else f"+{n_g}"
    print(f"  H4 >= {thresh:<36} {n_r:>12} {n_g:>12} {change:>12}")

print("\n" + "="*70)
print("KEY FINDINGS")
print("="*70)

gw_h4_08 = count_by_threshold(gw_results, 0.8)
region_h4_08 = count_by_threshold(region_results, 0.8)
novel = gw_h4_08 - region_h4_08

print(f"""
- Genome-wide analysis tested {n_gw/max(n_region,1):.0f}x more region-trait pairs
- Discovered {gw_h4_08} high-confidence signals (vs {region_h4_08} in 50-region)
- {novel} potentially novel signals identified by expanding genome-wide
- Comprehensive coverage removes selection bias from known loci
""")

# Save comparison
comparison_file = os.path.join(GW_DIR, "results/analysis/comparison_50region_vs_genomewide.txt")
with open(comparison_file, 'w') as f:
    f.write("COMPARISON: 50-REGION vs GENOME-WIDE COLOCALIZATION\n")
    f.write("="*60 + "\n\n")
    f.write(f"50-Region Analysis:\n")
    f.write(f"  Total tests: {n_region}\n")
    f.write(f"  H4 >= 0.8: {count_by_threshold(region_results, 0.8)}\n")
    f.write(f"  H4 >= 0.5: {count_by_threshold(region_results, 0.5)}\n\n")
    f.write(f"Genome-Wide Analysis:\n")
    f.write(f"  Total tests: {n_gw}\n")
    f.write(f"  H4 >= 0.8: {count_by_threshold(gw_results, 0.8)}\n")
    f.write(f"  H4 >= 0.5: {count_by_threshold(gw_results, 0.5)}\n\n")
    f.write(f"Improvement: {n_gw/max(n_region,1):.1f}x more tests, {gw_h4_08/max(region_h4_08,1):.1f}x more high-confidence signals\n")

print(f"Saved comparison: {comparison_file}")
