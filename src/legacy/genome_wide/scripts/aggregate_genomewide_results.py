#!/usr/bin/env python3
"""
Comprehensive aggregation of genome-wide colocalization results.
"""

import json
import os
import glob
from collections import defaultdict

RESULTS_DIR = "results/coloc"
OUTPUT_DIR = "results/analysis"
TABLES_DIR = "results/tables"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)

print("="*70)
print("GENOME-WIDE COLOCALIZATION RESULTS AGGREGATION")
print("="*70)

#------------------------------------------------------------------------------
# Load all results
#------------------------------------------------------------------------------
print("\n--- Loading Results ---")

json_files = glob.glob(os.path.join(RESULTS_DIR, "*.json"))
print(f"Found {len(json_files)} result files")

results = []
errors = []

for jf in json_files:
    try:
        with open(jf) as f:
            data = json.load(f)
            results.append(data)
    except Exception as e:
        errors.append((jf, str(e)))

print(f"Successfully loaded: {len(results)}")
print(f"Load errors: {len(errors)}")

#------------------------------------------------------------------------------
# Status summary
#------------------------------------------------------------------------------
print("\n--- Status Distribution ---")

status_counts = defaultdict(int)
for r in results:
    status_counts[r.get('status', 'UNKNOWN')] += 1

for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
    pct = count * 100 / len(results)
    print(f"  {status}: {count} ({pct:.1f}%)")

#------------------------------------------------------------------------------
# Filter successful results
#------------------------------------------------------------------------------
successful = [r for r in results if r.get('status') == 'SUCCESS']
print(f"\nSuccessful colocalization tests: {len(successful)}")

#------------------------------------------------------------------------------
# H4 distribution analysis
#------------------------------------------------------------------------------
print("\n--- H4 Distribution ---")

h4_values = []
for r in successful:
    h4 = r.get('PP.H4.abf')
    if h4 is not None:
        try:
            h4_values.append(float(h4))
        except:
            pass

print(f"Total with H4 values: {len(h4_values)}")

thresholds = [(0.9, "Tier 0"), (0.8, "Tier 1"), (0.5, "Tier 2"), (0.2, "Tier 3"), (0.1, "Tier 4")]
for thresh, tier in thresholds:
    n = sum(1 for h4 in h4_values if h4 >= thresh)
    print(f"  H4 >= {thresh} ({tier}): {n} signals")

#------------------------------------------------------------------------------
# Save full summary TSV
#------------------------------------------------------------------------------
print("\n--- Saving Full Summary ---")

summary_file = os.path.join(OUTPUT_DIR, "genomewide_coloc_summary.tsv")
with open(summary_file, 'w') as f:
    header = ['pair_id', 'region', 'chr', 'start', 'end', 'ancestry', 
              'trait_a', 'trait_b', 'n_snps', 
              'PP.H0', 'PP.H1', 'PP.H2', 'PP.H3', 'PP.H4',
              'lead_snp', 'lead_snp_pp_h4', 'status']
    f.write('\t'.join(header) + '\n')
    
    for r in results:
        # Parse region to get chr, start, end
        region = r.get('region', '')
        parts = region.replace('chr', '').replace(':', '-').split('-')
        chr_val = parts[0] if len(parts) > 0 else ''
        start_val = parts[1] if len(parts) > 1 else ''
        end_val = parts[2] if len(parts) > 2 else ''
        
        row = [
            str(r.get('pair_id', '')),
            region,
            chr_val,
            start_val,
            end_val,
            str(r.get('ancestry', '')),
            str(r.get('trait_a', '')),
            str(r.get('trait_b', '')),
            str(r.get('n_snps', '')),
            str(r.get('PP.H0.abf', '')),
            str(r.get('PP.H1.abf', '')),
            str(r.get('PP.H2.abf', '')),
            str(r.get('PP.H3.abf', '')),
            str(r.get('PP.H4.abf', '')),
            str(r.get('lead_snp', '')),
            str(r.get('lead_snp_pp_h4', '')),
            str(r.get('status', ''))
        ]
        f.write('\t'.join(row) + '\n')

print(f"Saved: {summary_file}")

#------------------------------------------------------------------------------
# Table 1: High-confidence signals (H4 >= 0.8)
#------------------------------------------------------------------------------
print("\n--- Table 1: High-Confidence Signals ---")

high_conf = [r for r in successful if r.get('PP.H4.abf', 0) >= 0.8]
high_conf_sorted = sorted(high_conf, key=lambda x: x.get('PP.H4.abf', 0), reverse=True)

table1_file = os.path.join(TABLES_DIR, "Table1_HighConfidence_Signals.tsv")
with open(table1_file, 'w') as f:
    header = ['Rank', 'Region', 'Ancestry', 'Trait_A', 'Trait_B', 
              'PP.H4', 'PP.H3', 'n_SNPs', 'Lead_SNP']
    f.write('\t'.join(header) + '\n')
    
    for i, r in enumerate(high_conf_sorted, 1):
        row = [
            str(i),
            r.get('region', ''),
            r.get('ancestry', ''),
            r.get('trait_a', ''),
            r.get('trait_b', ''),
            f"{r.get('PP.H4.abf', 0):.4f}",
            f"{r.get('PP.H3.abf', 0):.4f}",
            str(r.get('n_snps', '')),
            str(r.get('lead_snp', ''))
        ]
        f.write('\t'.join(row) + '\n')

print(f"High-confidence signals (H4 >= 0.8): {len(high_conf)}")
print(f"Saved: {table1_file}")

# Show top 15
print("\nTop 15 signals:")
print(f"{'Rank':<5} {'Region':<25} {'Traits':<20} {'H4':>8} {'Ancestry':<8}")
print("-" * 70)
for i, r in enumerate(high_conf_sorted[:15], 1):
    traits = f"{r.get('trait_a', '')}-{r.get('trait_b', '')}"
    print(f"{i:<5} {r.get('region', ''):<25} {traits:<20} {r.get('PP.H4.abf', 0):>8.4f} {r.get('ancestry', ''):<8}")

#------------------------------------------------------------------------------
# Table 2: Trait Pair Summary
#------------------------------------------------------------------------------
print("\n--- Table 2: Trait Pair Summary ---")

trait_pair_stats = defaultdict(lambda: {
    'total': 0, 'success': 0, 
    'h4_08': 0, 'h4_05': 0, 'h4_02': 0,
    'max_h4': 0
})

for r in results:
    pair = f"{r.get('trait_a', '')}-{r.get('trait_b', '')}"
    ancestry = r.get('ancestry', '')
    key = f"{pair}_{ancestry}"
    
    trait_pair_stats[key]['total'] += 1
    
    if r.get('status') == 'SUCCESS':
        trait_pair_stats[key]['success'] += 1
        h4 = r.get('PP.H4.abf', 0)
        if h4 >= 0.8:
            trait_pair_stats[key]['h4_08'] += 1
        if h4 >= 0.5:
            trait_pair_stats[key]['h4_05'] += 1
        if h4 >= 0.2:
            trait_pair_stats[key]['h4_02'] += 1
        if h4 > trait_pair_stats[key]['max_h4']:
            trait_pair_stats[key]['max_h4'] = h4

table2_file = os.path.join(TABLES_DIR, "Table2_TraitPair_Summary.tsv")
with open(table2_file, 'w') as f:
    header = ['Trait_Pair', 'Ancestry', 'Total_Tests', 'Successful', 
              'H4>=0.8', 'H4>=0.5', 'H4>=0.2', 'Max_H4']
    f.write('\t'.join(header) + '\n')
    
    for key in sorted(trait_pair_stats.keys()):
        parts = key.rsplit('_', 1)
        pair = parts[0]
        ancestry = parts[1] if len(parts) > 1 else ''
        stats = trait_pair_stats[key]
        
        row = [
            pair, ancestry,
            str(stats['total']),
            str(stats['success']),
            str(stats['h4_08']),
            str(stats['h4_05']),
            str(stats['h4_02']),
            f"{stats['max_h4']:.4f}"
        ]
        f.write('\t'.join(row) + '\n')

print(f"Saved: {table2_file}")

#------------------------------------------------------------------------------
# Table 3: Pleiotropic Loci (signals in 2+ trait pairs)
#------------------------------------------------------------------------------
print("\n--- Table 3: Pleiotropic Loci ---")

region_signals = defaultdict(list)
for r in successful:
    if r.get('PP.H4.abf', 0) >= 0.5:
        region_signals[r.get('region', '')].append({
            'trait_pair': f"{r.get('trait_a', '')}-{r.get('trait_b', '')}",
            'h4': r.get('PP.H4.abf', 0),
            'ancestry': r.get('ancestry', '')
        })

pleiotropic = {k: v for k, v in region_signals.items() if len(v) >= 2}

table3_file = os.path.join(TABLES_DIR, "Table3_Pleiotropic_Loci.tsv")
with open(table3_file, 'w') as f:
    header = ['Region', 'N_Trait_Pairs', 'Trait_Pairs', 'Max_H4', 'Ancestries']
    f.write('\t'.join(header) + '\n')
    
    for region in sorted(pleiotropic.keys(), key=lambda x: len(pleiotropic[x]), reverse=True):
        signals = pleiotropic[region]
        pairs = ', '.join(sorted(set(s['trait_pair'] for s in signals)))
        ancestries = ', '.join(sorted(set(s['ancestry'] for s in signals)))
        max_h4 = max(s['h4'] for s in signals)
        
        row = [region, str(len(signals)), pairs, f"{max_h4:.4f}", ancestries]
        f.write('\t'.join(row) + '\n')

print(f"Pleiotropic loci (>= 2 trait pairs with H4 >= 0.5): {len(pleiotropic)}")
print(f"Saved: {table3_file}")

# Show top pleiotropic loci
if pleiotropic:
    print("\nTop 10 pleiotropic loci:")
    for region in sorted(pleiotropic.keys(), key=lambda x: len(pleiotropic[x]), reverse=True)[:10]:
        signals = pleiotropic[region]
        print(f"  {region}: {len(signals)} trait pairs")

#------------------------------------------------------------------------------
# Table 4: Cross-Ancestry Comparison
#------------------------------------------------------------------------------
print("\n--- Table 4: Cross-Ancestry Comparison ---")

# Find regions with signals in both ancestries
eur_signals = defaultdict(dict)
afr_signals = defaultdict(dict)

for r in successful:
    region = r.get('region', '')
    pair = f"{r.get('trait_a', '')}-{r.get('trait_b', '')}"
    h4 = r.get('PP.H4.abf', 0)
    
    if r.get('ancestry') == 'EUR':
        if pair not in eur_signals[region] or h4 > eur_signals[region][pair]:
            eur_signals[region][pair] = h4
    elif r.get('ancestry') == 'AFR':
        if pair not in afr_signals[region] or h4 > afr_signals[region][pair]:
            afr_signals[region][pair] = h4

# Find concordant loci
concordant = []
for region in set(eur_signals.keys()) & set(afr_signals.keys()):
    for pair in set(eur_signals[region].keys()) & set(afr_signals[region].keys()):
        eur_h4 = eur_signals[region][pair]
        afr_h4 = afr_signals[region][pair]
        
        if eur_h4 >= 0.5 and afr_h4 >= 0.05:
            concordant.append({
                'region': region,
                'trait_pair': pair,
                'eur_h4': eur_h4,
                'afr_h4': afr_h4,
                'concordance': 'Strong' if afr_h4 >= 0.1 else 'Moderate'
            })

table4_file = os.path.join(TABLES_DIR, "Table4_CrossAncestry_Concordance.tsv")
with open(table4_file, 'w') as f:
    header = ['Region', 'Trait_Pair', 'EUR_H4', 'AFR_H4', 'Concordance']
    f.write('\t'.join(header) + '\n')
    
    for c in sorted(concordant, key=lambda x: x['eur_h4'], reverse=True):
        row = [c['region'], c['trait_pair'], f"{c['eur_h4']:.4f}", 
               f"{c['afr_h4']:.4f}", c['concordance']]
        f.write('\t'.join(row) + '\n')

print(f"Cross-ancestry concordant loci: {len(concordant)}")
print(f"  Strong (EUR>=0.5, AFR>=0.1): {sum(1 for c in concordant if c['concordance']=='Strong')}")
print(f"  Moderate (EUR>=0.5, AFR>=0.05): {sum(1 for c in concordant if c['concordance']=='Moderate')}")
print(f"Saved: {table4_file}")

#------------------------------------------------------------------------------
# Manuscript Statistics
#------------------------------------------------------------------------------
print("\n" + "="*70)
print("MANUSCRIPT STATISTICS")
print("="*70)

unique_regions = len(set(r.get('region', '') for r in successful))
eur_success = sum(1 for r in successful if r.get('ancestry') == 'EUR')
afr_success = sum(1 for r in successful if r.get('ancestry') == 'AFR')

stats_text = f"""
GENOME-WIDE COLOCALIZATION ANALYSIS - MANUSCRIPT STATISTICS
============================================================

ANALYSIS SCOPE
--------------
Total colocalization tests attempted: {len(results)}
Successful tests: {len(successful)} ({len(successful)*100/len(results):.1f}%)
  - EUR: {eur_success}
  - AFR: {afr_success}
Unique genomic regions tested: {unique_regions}
Traits analyzed: 5 (BMI, T2D, Hypertension, Stroke, Asthma)
Ancestries: 2 (EUR, AFR)

COLOCALIZATION SIGNALS
----------------------
High-confidence (H4 >= 0.8): {sum(1 for h in h4_values if h >= 0.8)}
Moderate (H4 >= 0.5): {sum(1 for h in h4_values if h >= 0.5)}
Suggestive (H4 >= 0.2): {sum(1 for h in h4_values if h >= 0.2)}
Exploratory (H4 >= 0.1): {sum(1 for h in h4_values if h >= 0.1)}

EUR High-confidence (H4 >= 0.8): {sum(1 for r in successful if r.get('ancestry')=='EUR' and r.get('PP.H4.abf',0)>=0.8)}
AFR Signals (H4 >= 0.1): {sum(1 for r in successful if r.get('ancestry')=='AFR' and r.get('PP.H4.abf',0)>=0.1)}

PLEIOTROPY
----------
Pleiotropic loci (>=2 trait pairs, H4>=0.5): {len(pleiotropic)}

CROSS-ANCESTRY
--------------
Concordant loci (EUR>=0.5, AFR>=0.05): {len(concordant)}
  - Strong concordance: {sum(1 for c in concordant if c['concordance']=='Strong')}
  - Moderate concordance: {sum(1 for c in concordant if c['concordance']=='Moderate')}

TOP SIGNAL
----------
{high_conf_sorted[0].get('region', 'N/A')} ({high_conf_sorted[0].get('trait_a', '')}-{high_conf_sorted[0].get('trait_b', '')}): H4 = {high_conf_sorted[0].get('PP.H4.abf', 0):.4f}
"""

print(stats_text)

stats_file = os.path.join(OUTPUT_DIR, "manuscript_statistics.txt")
with open(stats_file, 'w') as f:
    f.write(stats_text)
print(f"\nSaved: {stats_file}")

print("\n" + "="*70)
print("AGGREGATION COMPLETE")
print("="*70)
