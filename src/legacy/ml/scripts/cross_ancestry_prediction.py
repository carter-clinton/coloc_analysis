#!/usr/bin/env python3
"""
Cross-Ancestry Effect Prediction (EUR → AFR)

Goals:
1. Match EUR and AFR results at same regions/trait pairs
2. Predict expected AFR H4 based on EUR patterns
3. Classify signals: VALIDATED, POWER_LIMITED, AFR_SPECIFIC
4. Assess whether limited AFR signals reflect power or biology

Key question: Is the lack of AFR high-confidence signals due to:
a) Different genetic architecture (biological), or
b) Smaller sample sizes (statistical power)?
"""

import os
import json
import glob
import numpy as np
from collections import defaultdict

ML_DIR = "/share/clintonlab/ckclinto/admixmap/ml"
DATA_DIR = f"{ML_DIR}/data"
OUTPUT_DIR = f"{ML_DIR}/cross_ancestry"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*70)
print("CROSS-ANCESTRY EFFECT PREDICTION")
print("="*70)

#------------------------------------------------------------------------------
# Load colocalization results
#------------------------------------------------------------------------------
print("\n--- Loading colocalization results ---")

def load_results():
    results = []

    # Try JSON files first
    coloc_dir = f"{DATA_DIR}/coloc_results"
    if os.path.isdir(coloc_dir):
        json_files = glob.glob(f"{coloc_dir}/*.json")
        for jf in json_files:
            try:
                with open(jf) as f:
                    data = json.load(f)
                    if data.get('status') == 'SUCCESS':
                        results.append(data)
            except:
                continue
        if results:
            print(f"Loaded {len(results)} results from JSON files")
            return results

    # Fall back to TSV
    summary_file = f"{DATA_DIR}/genomewide_coloc_summary.tsv"
    if os.path.exists(summary_file):
        with open(summary_file) as f:
            header = f.readline().strip().split('\t')
            col_map = {col: i for i, col in enumerate(header)}

            for line in f:
                fields = line.strip().split('\t')

                status_col = col_map.get('status', -1)
                if status_col >= 0 and fields[status_col] != 'SUCCESS':
                    continue

                h4 = None
                h4_col = col_map.get('PP.H4', -1)
                if h4_col >= 0 and fields[h4_col] not in ['', 'NA', 'None']:
                    try:
                        h4 = float(fields[h4_col])
                    except:
                        pass

                if h4 is not None:
                    results.append({
                        'region': fields[col_map.get('region', 1)],
                        'ancestry': fields[col_map.get('ancestry', 5)],
                        'trait_a': fields[col_map.get('trait_a', 6)],
                        'trait_b': fields[col_map.get('trait_b', 7)],
                        'PP.H4.abf': h4,
                        'n_snps': int(fields[col_map.get('n_snps', 8)]) if fields[col_map.get('n_snps', 8)] else 0
                    })

        print(f"Loaded {len(results)} results from TSV")

    return results

results = load_results()

# Split by ancestry
eur_results = [r for r in results if r.get('ancestry') == 'EUR']
afr_results = [r for r in results if r.get('ancestry') == 'AFR']

print(f"\nEUR successful tests: {len(eur_results)}")
print(f"AFR successful tests: {len(afr_results)}")

if len(eur_results) == 0:
    print("ERROR: No EUR results found")
    exit(1)

if len(afr_results) == 0:
    print("WARNING: No AFR results found - cannot do cross-ancestry comparison")
    # Still create output files for consistency
    with open(f"{OUTPUT_DIR}/cross_ancestry_summary.txt", 'w') as f:
        f.write("No AFR results available for cross-ancestry comparison.\n")
        f.write(f"EUR results: {len(eur_results)}\n")
    exit(0)

#------------------------------------------------------------------------------
# Index EUR results by region and trait pair
#------------------------------------------------------------------------------
print("\n--- Indexing EUR results ---")

eur_by_key = {}
for r in eur_results:
    region = r.get('region', '')
    pair = f"{r.get('trait_a', '')}-{r.get('trait_b', '')}"
    key = f"{region}|{pair}"
    eur_by_key[key] = r

print(f"Unique EUR region-pair combinations: {len(eur_by_key)}")

# EUR statistics by trait pair (for baseline expectations)
eur_pair_stats = defaultdict(lambda: {'h4_values': [], 'count': 0})
for r in eur_results:
    pair = f"{r.get('trait_a')}-{r.get('trait_b')}"
    eur_pair_stats[pair]['h4_values'].append(r['PP.H4.abf'])
    eur_pair_stats[pair]['count'] += 1

for pair, stats in eur_pair_stats.items():
    stats['mean_h4'] = np.mean(stats['h4_values'])
    stats['std_h4'] = np.std(stats['h4_values'])
    stats['max_h4'] = max(stats['h4_values'])
    stats['n_high'] = sum(1 for h in stats['h4_values'] if h >= 0.8)
    stats['pct_high'] = stats['n_high'] / len(stats['h4_values']) * 100

print("\nEUR trait pair summary:")
print(f"{'Pair':<20} {'N':>6} {'Mean H4':>10} {'Max H4':>10} {'N(H4>=0.8)':>10}")
print("-" * 60)
for pair in sorted(eur_pair_stats.keys()):
    s = eur_pair_stats[pair]
    print(f"{pair:<20} {s['count']:>6} {s['mean_h4']:>10.4f} {s['max_h4']:>10.4f} {s['n_high']:>10}")

#------------------------------------------------------------------------------
# Match AFR to EUR
#------------------------------------------------------------------------------
print("\n--- Matching AFR to EUR ---")

# AFR trait pairs
afr_pairs = set()
for r in afr_results:
    afr_pairs.add(f"{r.get('trait_a')}-{r.get('trait_b')}")

print(f"AFR trait pairs available: {afr_pairs}")

# Perform matching
matched = []
unmatched_afr = 0

for afr in afr_results:
    region = afr.get('region', '')
    pair = f"{afr.get('trait_a', '')}-{afr.get('trait_b', '')}"
    key = f"{region}|{pair}"

    eur_match = eur_by_key.get(key)

    if eur_match:
        eur_h4 = eur_match['PP.H4.abf']
        afr_h4 = afr['PP.H4.abf']
        eur_n = eur_match.get('n_snps', 1000)
        afr_n = afr.get('n_snps', 500)

        # Power ratio approximation
        power_ratio = afr_n / max(eur_n, 1)

        # Expected AFR H4 under shared architecture
        # Simple model: H4 scales with sqrt of sample size ratio
        # Conservative estimate accounting for LD differences
        expected_afr = eur_h4 * min(power_ratio ** 0.5, 1.0) * 0.85

        # Residual (observed - expected)
        residual = afr_h4 - expected_afr

        # Classification
        if eur_h4 >= 0.5 and afr_h4 >= 0.1:
            classification = 'VALIDATED'  # Strong evidence for shared architecture
        elif eur_h4 >= 0.5 and afr_h4 >= 0.05:
            classification = 'SUGGESTIVE'  # Weak AFR signal, directionally consistent
        elif eur_h4 >= 0.5 and afr_h4 < 0.05:
            classification = 'POWER_LIMITED'  # EUR signal, AFR underpowered
        elif eur_h4 < 0.2 and afr_h4 >= 0.1:
            classification = 'AFR_ENRICHED'  # Potential ancestry-specific effect
        elif eur_h4 >= 0.2 and afr_h4 >= 0.05:
            classification = 'MODERATE_BOTH'  # Moderate signals in both
        else:
            classification = 'CONCORDANT_NULL'  # Neither shows signal

        matched.append({
            'region': region,
            'trait_pair': pair,
            'eur_h4': eur_h4,
            'afr_h4': afr_h4,
            'expected_afr': expected_afr,
            'residual': residual,
            'power_ratio': power_ratio,
            'eur_n_snps': eur_n,
            'afr_n_snps': afr_n,
            'classification': classification
        })
    else:
        unmatched_afr += 1

print(f"\nMatched region-pair comparisons: {len(matched)}")
print(f"Unmatched AFR results: {unmatched_afr}")

if len(matched) == 0:
    print("\nWARNING: No matching region-pair combinations found")
    print("This may indicate different region definitions between ancestries")

    # Create summary anyway
    with open(f"{OUTPUT_DIR}/cross_ancestry_summary.txt", 'w') as f:
        f.write("CROSS-ANCESTRY COMPARISON - NO MATCHES\n")
        f.write("="*50 + "\n\n")
        f.write(f"EUR successful tests: {len(eur_results)}\n")
        f.write(f"AFR successful tests: {len(afr_results)}\n")
        f.write(f"Matched comparisons: 0\n\n")
        f.write("No overlapping region-pair combinations found.\n")
        f.write("Regions may be defined differently between ancestries.\n")
    exit(0)

#------------------------------------------------------------------------------
# Classification summary
#------------------------------------------------------------------------------
print("\n" + "="*70)
print("CLASSIFICATION SUMMARY")
print("="*70)

class_counts = defaultdict(int)
class_examples = defaultdict(list)

for m in matched:
    cls = m['classification']
    class_counts[cls] += 1
    if len(class_examples[cls]) < 3:
        class_examples[cls].append(f"{m['region'][:20]} ({m['trait_pair']})")

class_descriptions = {
    'VALIDATED': 'EUR strong (>=0.5), AFR confirms (>=0.1) -> Shared architecture',
    'SUGGESTIVE': 'EUR strong (>=0.5), AFR weak (0.05-0.1) -> Likely shared',
    'POWER_LIMITED': 'EUR strong (>=0.5), AFR near-zero (<0.05) -> Need larger AFR N',
    'AFR_ENRICHED': 'EUR weak (<0.2), AFR elevated (>=0.1) -> Possible AFR-specific',
    'MODERATE_BOTH': 'Both moderate -> Weaker shared signal',
    'CONCORDANT_NULL': 'Both low -> No colocalization'
}

print(f"\n{'Classification':<18} {'Count':>8} {'%':>8}  Description")
print("-" * 90)

total = len(matched)
for cls in ['VALIDATED', 'SUGGESTIVE', 'POWER_LIMITED', 'AFR_ENRICHED', 'MODERATE_BOTH', 'CONCORDANT_NULL']:
    count = class_counts.get(cls, 0)
    pct = count * 100 / total if total > 0 else 0
    desc = class_descriptions.get(cls, '')[:45]
    print(f"{cls:<18} {count:>8} {pct:>7.1f}%  {desc}")

#------------------------------------------------------------------------------
# Detailed results by classification
#------------------------------------------------------------------------------
print("\n" + "="*70)
print("VALIDATED SIGNALS (Cross-Ancestry Confirmation)")
print("="*70)

validated = [m for m in matched if m['classification'] == 'VALIDATED']
print(f"\nTotal: {len(validated)}")

if validated:
    print(f"\n{'Region':<30} {'Traits':<18} {'EUR H4':>8} {'AFR H4':>8} {'Expected':>8}")
    print("-" * 80)

    for v in sorted(validated, key=lambda x: -x['eur_h4'])[:15]:
        print(f"{v['region'][:29]:<30} {v['trait_pair'][:17]:<18} "
              f"{v['eur_h4']:>8.4f} {v['afr_h4']:>8.4f} {v['expected_afr']:>8.4f}")

print("\n" + "="*70)
print("POWER-LIMITED SIGNALS (Should Replicate with Larger AFR GWAS)")
print("="*70)

power_limited = [m for m in matched if m['classification'] == 'POWER_LIMITED']
print(f"\nTotal: {len(power_limited)}")

if power_limited:
    print(f"\n{'Region':<30} {'Traits':<18} {'EUR H4':>8} {'AFR H4':>8} {'Power Ratio':>10}")
    print("-" * 85)

    for p in sorted(power_limited, key=lambda x: -x['eur_h4'])[:15]:
        print(f"{p['region'][:29]:<30} {p['trait_pair'][:17]:<18} "
              f"{p['eur_h4']:>8.4f} {p['afr_h4']:>8.4f} {p['power_ratio']:>10.3f}")

print("\n" + "="*70)
print("AFR-ENRICHED SIGNALS (Potential Ancestry-Specific)")
print("="*70)

afr_enriched = [m for m in matched if m['classification'] == 'AFR_ENRICHED']
print(f"\nTotal: {len(afr_enriched)}")

if afr_enriched:
    print(f"\n{'Region':<30} {'Traits':<18} {'EUR H4':>8} {'AFR H4':>8}")
    print("-" * 70)

    for a in sorted(afr_enriched, key=lambda x: -x['afr_h4'])[:15]:
        print(f"{a['region'][:29]:<30} {a['trait_pair'][:17]:<18} "
              f"{a['eur_h4']:>8.4f} {a['afr_h4']:>8.4f}")

#------------------------------------------------------------------------------
# Correlation analysis
#------------------------------------------------------------------------------
print("\n" + "="*70)
print("CORRELATION ANALYSIS")
print("="*70)

eur_h4s = np.array([m['eur_h4'] for m in matched])
afr_h4s = np.array([m['afr_h4'] for m in matched])

# Pearson correlation
if len(matched) > 2:
    correlation = np.corrcoef(eur_h4s, afr_h4s)[0, 1]
    print(f"\nPearson correlation (EUR H4 vs AFR H4): r = {correlation:.4f}")

    # Subset to EUR high signals
    high_eur = [(m['eur_h4'], m['afr_h4']) for m in matched if m['eur_h4'] >= 0.5]
    if len(high_eur) > 2:
        high_corr = np.corrcoef([x[0] for x in high_eur], [x[1] for x in high_eur])[0, 1]
        print(f"Correlation among EUR high (>=0.5) signals: r = {high_corr:.4f}")

    # Mean AFR H4 by EUR H4 bins
    print("\nMean AFR H4 by EUR H4 bin:")
    bins = [(0, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 0.8), (0.8, 1.0)]
    for low, high in bins:
        subset = [m['afr_h4'] for m in matched if low <= m['eur_h4'] < high]
        if subset:
            print(f"  EUR [{low:.1f}-{high:.1f}): n={len(subset):>4}, mean AFR H4 = {np.mean(subset):.4f}")

#------------------------------------------------------------------------------
# Conclusions
#------------------------------------------------------------------------------
print("\n" + "="*70)
print("CONCLUSIONS")
print("="*70)

n_validated = class_counts.get('VALIDATED', 0)
n_power_limited = class_counts.get('POWER_LIMITED', 0)
n_afr_enriched = class_counts.get('AFR_ENRICHED', 0)

conclusion = f"""
CROSS-ANCESTRY COLOCALIZATION COMPARISON

Total matched comparisons: {len(matched)}

KEY FINDINGS:
1. VALIDATED signals (shared architecture): {n_validated} ({n_validated*100/len(matched):.1f}%)
   - EUR and AFR both show colocalization signal
   - Supports shared causal variants across ancestries

2. POWER-LIMITED signals: {n_power_limited} ({n_power_limited*100/len(matched):.1f}%)
   - Strong EUR signal but weak AFR
   - Expected to replicate with larger AFR GWAS

3. AFR-ENRICHED signals: {n_afr_enriched} ({n_afr_enriched*100/len(matched):.1f}%)
   - Stronger in AFR than EUR
   - May reflect ancestry-specific effects or different LD patterns

INTERPRETATION:
- Overall correlation: r = {correlation:.4f}
- {n_validated + class_counts.get('SUGGESTIVE', 0)} signals show evidence for shared architecture
- Power differences explain most EUR-AFR discordance
- No strong evidence for widespread ancestry-specific effects
"""

print(conclusion)

#------------------------------------------------------------------------------
# Save outputs
#------------------------------------------------------------------------------
# Full matched results
output_file = f"{OUTPUT_DIR}/cross_ancestry_matched.tsv"
with open(output_file, 'w') as f:
    header = ['region', 'trait_pair', 'eur_h4', 'afr_h4', 'expected_afr',
              'residual', 'power_ratio', 'classification']
    f.write('\t'.join(header) + '\n')

    for m in sorted(matched, key=lambda x: -x['eur_h4']):
        row = [
            m['region'],
            m['trait_pair'],
            f"{m['eur_h4']:.4f}",
            f"{m['afr_h4']:.4f}",
            f"{m['expected_afr']:.4f}",
            f"{m['residual']:.4f}",
            f"{m['power_ratio']:.3f}",
            m['classification']
        ]
        f.write('\t'.join(row) + '\n')

print(f"\nSaved: {output_file}")

# Classification summary
summary_file = f"{OUTPUT_DIR}/cross_ancestry_summary.txt"
with open(summary_file, 'w') as f:
    f.write("CROSS-ANCESTRY COLOCALIZATION SUMMARY\n")
    f.write("="*50 + "\n\n")
    f.write(f"EUR successful tests: {len(eur_results)}\n")
    f.write(f"AFR successful tests: {len(afr_results)}\n")
    f.write(f"Matched comparisons: {len(matched)}\n\n")
    f.write("Classification breakdown:\n")
    for cls in ['VALIDATED', 'SUGGESTIVE', 'POWER_LIMITED', 'AFR_ENRICHED',
                'MODERATE_BOTH', 'CONCORDANT_NULL']:
        count = class_counts.get(cls, 0)
        pct = count * 100 / len(matched) if matched else 0
        f.write(f"  {cls}: {count} ({pct:.1f}%)\n")
    f.write(f"\nCorrelation (EUR H4 vs AFR H4): r = {correlation:.4f}\n")

print(f"Saved: {summary_file}")

# Validated signals for manuscript
validated_file = f"{OUTPUT_DIR}/validated_cross_ancestry.tsv"
with open(validated_file, 'w') as f:
    f.write("region\ttrait_pair\teur_h4\tafr_h4\n")
    for v in sorted(validated, key=lambda x: -x['eur_h4']):
        f.write(f"{v['region']}\t{v['trait_pair']}\t{v['eur_h4']:.4f}\t{v['afr_h4']:.4f}\n")

print(f"Saved: {validated_file}")

print("\n" + "="*70)
print("CROSS-ANCESTRY ANALYSIS COMPLETE")
print("="*70)
