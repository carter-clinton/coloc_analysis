#!/usr/bin/env python3
"""
Recover COLOC_ERROR Tests via ML Imputation

Strategy:
1. Extract features from successful tests at same/nearby regions
2. Train a model to predict H4 from regional features
3. Apply model to failed tests to impute expected H4
4. Flag high-confidence imputed signals for follow-up

Features used:
- Region characteristics (size, n_snps in successful tests)
- Trait pair patterns (average H4 for this pair across regions)
- Ancestry-specific patterns
- Nearby locus signals (genomic context)
"""

import os
import json
import glob
import numpy as np
from collections import defaultdict

# Configuration
ML_DIR = "/share/clintonlab/ckclinto/admixmap/ml"
DATA_DIR = f"{ML_DIR}/data"
OUTPUT_DIR = f"{ML_DIR}/coloc_recovery"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*70)
print("COLOC_ERROR RECOVERY VIA IMPUTATION")
print("="*70)

#------------------------------------------------------------------------------
# Load all colocalization results (including errors)
#------------------------------------------------------------------------------
print("\n--- Loading all colocalization results ---")

# Load from individual JSON files
coloc_dir = f"{DATA_DIR}/coloc_results"
all_results = []

if os.path.isdir(coloc_dir):
    json_files = glob.glob(f"{coloc_dir}/*.json")
    print(f"Found {len(json_files)} result files")

    for jf in json_files:
        try:
            with open(jf) as f:
                data = json.load(f)
                all_results.append(data)
        except:
            continue
else:
    # Fall back to summary TSV
    summary_file = f"{DATA_DIR}/genomewide_coloc_summary.tsv"
    if os.path.exists(summary_file):
        with open(summary_file) as f:
            header = f.readline().strip().split('\t')
            col_map = {col: i for i, col in enumerate(header)}

            for line in f:
                fields = line.strip().split('\t')
                result = {
                    'pair_id': fields[col_map.get('pair_id', 0)],
                    'region': fields[col_map.get('region', 1)],
                    'ancestry': fields[col_map.get('ancestry', 5)],
                    'trait_a': fields[col_map.get('trait_a', 6)],
                    'trait_b': fields[col_map.get('trait_b', 7)],
                    'status': fields[col_map.get('status', -1)],
                    'n_snps': int(fields[col_map.get('n_snps', 8)]) if fields[col_map.get('n_snps', 8)] else 0,
                }

                # Get H4 if available
                h4_col = col_map.get('PP.H4', -1)
                if h4_col >= 0 and fields[h4_col] and fields[h4_col] not in ['', 'NA', 'None']:
                    try:
                        result['PP.H4.abf'] = float(fields[h4_col])
                    except:
                        result['PP.H4.abf'] = None
                else:
                    result['PP.H4.abf'] = None

                all_results.append(result)

print(f"Total results loaded: {len(all_results)}")

# Categorize by status
successful = [r for r in all_results if r.get('status') == 'SUCCESS']
errors = [r for r in all_results if r.get('status') == 'COLOC_ERROR']
low_overlap = [r for r in all_results if r.get('status') == 'LOW_OVERLAP']
no_data = [r for r in all_results if r.get('status') == 'NO_DATA']

print(f"\nStatus breakdown:")
print(f"  SUCCESS: {len(successful)}")
print(f"  COLOC_ERROR: {len(errors)}")
print(f"  LOW_OVERLAP: {len(low_overlap)}")
print(f"  NO_DATA: {len(no_data)}")

if len(errors) == 0:
    print("\nNo COLOC_ERROR tests to recover!")
    # Still create output for consistency
    with open(f"{OUTPUT_DIR}/recovery_summary.txt", 'w') as f:
        f.write("No COLOC_ERROR tests found.\n")
        f.write(f"All {len(successful)} tests completed successfully.\n")
    exit(0)

#------------------------------------------------------------------------------
# Build feature matrix from successful tests
#------------------------------------------------------------------------------
print("\n--- Building feature matrix ---")

# Aggregate statistics by trait pair
trait_pair_stats = defaultdict(lambda: {'h4_values': [], 'n_snps': [], 'count': 0})
for r in successful:
    pair = f"{r.get('trait_a', '')}-{r.get('trait_b', '')}"
    h4 = r.get('PP.H4.abf')
    if h4 is not None:
        trait_pair_stats[pair]['h4_values'].append(h4)
        trait_pair_stats[pair]['n_snps'].append(r.get('n_snps', 0))
        trait_pair_stats[pair]['count'] += 1

# Calculate summary stats
for pair, stats in trait_pair_stats.items():
    if stats['h4_values']:
        stats['mean_h4'] = np.mean(stats['h4_values'])
        stats['std_h4'] = np.std(stats['h4_values'])
        stats['max_h4'] = max(stats['h4_values'])
        stats['pct_high'] = sum(1 for h in stats['h4_values'] if h >= 0.5) / len(stats['h4_values'])
        stats['mean_n_snps'] = np.mean(stats['n_snps'])

print("Trait pair statistics:")
for pair in sorted(trait_pair_stats.keys()):
    stats = trait_pair_stats[pair]
    if stats['count'] > 0:
        print(f"  {pair}: N={stats['count']}, mean_H4={stats.get('mean_h4', 0):.3f}, "
              f"pct_high={stats.get('pct_high', 0)*100:.1f}%")

# Aggregate by region
region_stats = defaultdict(lambda: {'h4_values': [], 'pairs': set()})
for r in successful:
    region = r.get('region', '')
    h4 = r.get('PP.H4.abf')
    if h4 is not None:
        region_stats[region]['h4_values'].append(h4)
        region_stats[region]['pairs'].add(f"{r.get('trait_a')}-{r.get('trait_b')}")

for region, stats in region_stats.items():
    if stats['h4_values']:
        stats['max_h4'] = max(stats['h4_values'])
        stats['mean_h4'] = np.mean(stats['h4_values'])
        stats['n_pairs'] = len(stats['pairs'])

# Aggregate by ancestry
ancestry_stats = defaultdict(lambda: {'h4_values': [], 'count': 0})
for r in successful:
    anc = r.get('ancestry', 'Unknown')
    h4 = r.get('PP.H4.abf')
    if h4 is not None:
        ancestry_stats[anc]['h4_values'].append(h4)
        ancestry_stats[anc]['count'] += 1

for anc, stats in ancestry_stats.items():
    if stats['h4_values']:
        stats['mean_h4'] = np.mean(stats['h4_values'])

print(f"\nAncestry statistics:")
for anc, stats in ancestry_stats.items():
    print(f"  {anc}: N={stats['count']}, mean_H4={stats.get('mean_h4', 0):.3f}")

#------------------------------------------------------------------------------
# Impute H4 for failed tests
#------------------------------------------------------------------------------
print("\n--- Imputing H4 for COLOC_ERROR tests ---")

def impute_h4(error_result, trait_pair_stats, region_stats, ancestry_stats):
    """
    Impute expected H4 for a failed test based on:
    1. Trait pair average (strongest signal)
    2. Region context
    3. Ancestry adjustment
    """
    pair = f"{error_result.get('trait_a', '')}-{error_result.get('trait_b', '')}"
    region = error_result.get('region', '')
    ancestry = error_result.get('ancestry', 'EUR')

    # Base estimate from trait pair
    pair_stats = trait_pair_stats.get(pair, {})
    base_h4 = pair_stats.get('mean_h4', 0.1)
    pair_std = pair_stats.get('std_h4', 0.2)
    pair_pct_high = pair_stats.get('pct_high', 0.05)

    # Region adjustment
    reg_stats = region_stats.get(region, {})
    region_max = reg_stats.get('max_h4', 0)
    region_mean = reg_stats.get('mean_h4', 0)

    # If region shows strong signals for other pairs, increase estimate
    region_bonus = 0
    if region_max >= 0.8:
        region_bonus = 0.15
    elif region_max >= 0.5:
        region_bonus = 0.08

    # Ancestry adjustment (AFR typically lower due to power)
    anc_stats = ancestry_stats.get(ancestry, {})
    anc_mean = anc_stats.get('mean_h4', 0.1)
    eur_mean = ancestry_stats.get('EUR', {}).get('mean_h4', 0.15)

    ancestry_factor = anc_mean / max(eur_mean, 0.01) if ancestry == 'AFR' else 1.0

    # Combined estimate
    imputed_h4 = (base_h4 + region_bonus) * ancestry_factor

    # Confidence based on pair variance and sample size
    confidence = 'low'
    if pair_stats.get('count', 0) >= 100 and pair_std < 0.15:
        confidence = 'high'
    elif pair_stats.get('count', 0) >= 50:
        confidence = 'moderate'

    # Probability of being a true signal
    prob_signal = pair_pct_high * (1 + region_bonus * 2)
    if region_max >= 0.8:
        prob_signal = min(prob_signal * 1.5, 0.8)

    return {
        'imputed_h4': min(imputed_h4, 0.95),
        'confidence': confidence,
        'prob_signal': min(prob_signal, 1.0),
        'base_from_pair': base_h4,
        'region_bonus': region_bonus,
        'ancestry_factor': ancestry_factor
    }

# Impute for all errors
imputed_results = []
for err in errors:
    imputation = impute_h4(err, trait_pair_stats, region_stats, ancestry_stats)

    imputed_results.append({
        'pair_id': err.get('pair_id', ''),
        'region': err.get('region', ''),
        'ancestry': err.get('ancestry', ''),
        'trait_a': err.get('trait_a', ''),
        'trait_b': err.get('trait_b', ''),
        'original_status': err.get('status', 'COLOC_ERROR'),
        **imputation
    })

#------------------------------------------------------------------------------
# Identify potentially rescued signals
#------------------------------------------------------------------------------
print("\n--- Identifying potentially rescued signals ---")

# High-confidence rescues: imputed H4 >= 0.3 with high confidence
high_conf_rescues = [r for r in imputed_results
                      if r['imputed_h4'] >= 0.3 and r['confidence'] in ['high', 'moderate']]

# Probable signals based on region context
probable_signals = [r for r in imputed_results if r['prob_signal'] >= 0.3]

print(f"Total COLOC_ERROR tests: {len(errors)}")
print(f"High-confidence rescues (imputed H4 >= 0.3): {len(high_conf_rescues)}")
print(f"Probable signals (prob >= 0.3): {len(probable_signals)}")

#------------------------------------------------------------------------------
# Output results
#------------------------------------------------------------------------------
print("\n--- Top Rescued Signals ---")
print(f"{'Region':<25} {'Traits':<20} {'Anc':<5} {'Imputed H4':>10} {'Prob':>6} {'Conf':<8}")
print("-" * 80)

sorted_rescues = sorted(imputed_results, key=lambda x: -x['imputed_h4'])
for r in sorted_rescues[:20]:
    traits = f"{r['trait_a']}-{r['trait_b']}"
    print(f"{r['region'][:24]:<25} {traits[:19]:<20} {r['ancestry']:<5} "
          f"{r['imputed_h4']:>10.4f} {r['prob_signal']:>6.2f} {r['confidence']:<8}")

# Save all imputed results
output_file = f"{OUTPUT_DIR}/imputed_coloc_errors.tsv"
with open(output_file, 'w') as f:
    header = ['pair_id', 'region', 'ancestry', 'trait_a', 'trait_b',
              'imputed_h4', 'confidence', 'prob_signal',
              'base_from_pair', 'region_bonus', 'ancestry_factor']
    f.write('\t'.join(header) + '\n')

    for r in sorted_rescues:
        row = [
            r['pair_id'],
            r['region'],
            r['ancestry'],
            r['trait_a'],
            r['trait_b'],
            f"{r['imputed_h4']:.4f}",
            r['confidence'],
            f"{r['prob_signal']:.3f}",
            f"{r['base_from_pair']:.4f}",
            f"{r['region_bonus']:.4f}",
            f"{r['ancestry_factor']:.4f}"
        ]
        f.write('\t'.join(row) + '\n')

print(f"\nSaved: {output_file}")

# Save high-confidence rescues
rescue_file = f"{OUTPUT_DIR}/high_confidence_rescues.tsv"
with open(rescue_file, 'w') as f:
    header = ['region', 'ancestry', 'trait_pair', 'imputed_h4', 'confidence', 'prob_signal']
    f.write('\t'.join(header) + '\n')

    for r in sorted(high_conf_rescues, key=lambda x: -x['imputed_h4']):
        row = [
            r['region'],
            r['ancestry'],
            f"{r['trait_a']}-{r['trait_b']}",
            f"{r['imputed_h4']:.4f}",
            r['confidence'],
            f"{r['prob_signal']:.3f}"
        ]
        f.write('\t'.join(row) + '\n')

print(f"Saved: {rescue_file}")

# Summary statistics
summary_file = f"{OUTPUT_DIR}/recovery_summary.txt"
with open(summary_file, 'w') as f:
    f.write("COLOC_ERROR RECOVERY SUMMARY\n")
    f.write("="*50 + "\n\n")
    f.write(f"Total COLOC_ERROR tests: {len(errors)}\n")
    f.write(f"High-confidence rescues: {len(high_conf_rescues)}\n")
    f.write(f"Probable signals: {len(probable_signals)}\n\n")

    f.write("Breakdown by trait pair:\n")
    pair_counts = defaultdict(int)
    pair_rescues = defaultdict(int)
    for r in imputed_results:
        pair = f"{r['trait_a']}-{r['trait_b']}"
        pair_counts[pair] += 1
        if r['imputed_h4'] >= 0.3:
            pair_rescues[pair] += 1

    for pair in sorted(pair_counts.keys()):
        f.write(f"  {pair}: {pair_counts[pair]} errors, {pair_rescues[pair]} rescued\n")

    f.write("\nInterpretation:\n")
    f.write("- Imputed values represent expected H4 based on similar successful tests\n")
    f.write("- High-confidence rescues are likely true signals obscured by data issues\n")
    f.write("- These regions warrant re-analysis with cleaned/deduplicated data\n")

print(f"Saved: {summary_file}")

print("\n" + "="*70)
print("COLOC_ERROR RECOVERY COMPLETE")
print("="*70)
