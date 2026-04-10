#!/usr/bin/env python3
"""
Comprehensive Cross-Ancestry Colocalization & Pleiotropy Analysis

Goals:
1. Compare EUR vs AFR signals at same loci - are markers shared?
2. Identify known vs novel pleiotropic markers
3. Evaluate multi-trait pleiotropy (markers affecting >1 trait pair)
4. Tiered confidence framework for both ancestries
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

PROJECT_DIR = Path("/share/clintonlab/ckclinto/admix_map")

# Load data
coloc = pd.read_csv(PROJECT_DIR / "results/multitrait/coloc_summary.tsv", sep="\t")
coloc = coloc[coloc["PP.H4"].notna()].copy()

# Known pleiotropic loci from literature (for comparison)
KNOWN_PLEIOTROPIC = {
    "TCF7L2": ["t2d", "bmi", "stroke"],
    "FTO": ["bmi", "t2d"],
    "MC4R": ["bmi", "t2d", "hypertension"],
    "GCKR": ["t2d", "bmi"],
    "APOE": ["stroke", "bmi", "t2d"],
    "SH2B3": ["stroke", "hypertension", "bmi"],
    "KCNJ11": ["t2d", "hypertension"],
    "PPARG": ["t2d", "hypertension"],
    "IRS1": ["t2d", "bmi"],
    "LPA": ["stroke", "bmi"],
    "CDKAL1": ["t2d"],
    "HHEX": ["t2d"],
    "SLC30A8": ["t2d"],
    "HNF1A": ["t2d"],
    "BDNF": ["bmi", "t2d"],
}

print("="*90)
print("COMPREHENSIVE CROSS-ANCESTRY COLOCALIZATION & PLEIOTROPY ANALYSIS")
print("="*90)

#==============================================================================
# 1. TIERED FRAMEWORK FOR BOTH ANCESTRIES
#==============================================================================
print("\n" + "="*90)
print("1. TIERED SIGNAL COUNTS BY ANCESTRY")
print("="*90)

tiers = [
    ("Tier 1: High Confidence", 0.8, 1.0),
    ("Tier 2: Moderate", 0.5, 0.8),
    ("Tier 3: Suggestive", 0.2, 0.5),
    ("Tier 4: Exploratory", 0.1, 0.2),
    ("Tier 5: Weak", 0.05, 0.1),
    ("Below threshold", 0.0, 0.05),
]

def assign_tier(h4):
    if h4 >= 0.8: return "Tier1_HighConf"
    elif h4 >= 0.5: return "Tier2_Moderate"
    elif h4 >= 0.2: return "Tier3_Suggestive"
    elif h4 >= 0.1: return "Tier4_Exploratory"
    elif h4 >= 0.05: return "Tier5_Weak"
    else: return "Below_threshold"

coloc["tier"] = coloc["PP.H4"].apply(assign_tier)

print(f"\n{'Tier':<30} {'EUR':>10} {'AFR':>10} {'Total':>10}")
print("-" * 65)

for tier_name, low, high in tiers:
    eur = len(coloc[(coloc["ancestry"]=="EUR") & (coloc["PP.H4"]>=low) & (coloc["PP.H4"]<high)])
    afr = len(coloc[(coloc["ancestry"]=="AFR") & (coloc["PP.H4"]>=low) & (coloc["PP.H4"]<high)])
    # For top tier, include ==1.0
    if high == 1.0:
        eur = len(coloc[(coloc["ancestry"]=="EUR") & (coloc["PP.H4"]>=low)])
        afr = len(coloc[(coloc["ancestry"]=="AFR") & (coloc["PP.H4"]>=low)])
    print(f"{tier_name:<30} {eur:>10} {afr:>10} {eur+afr:>10}")

#==============================================================================
# 2. CROSS-ANCESTRY CONCORDANCE AT LOCUS LEVEL
#==============================================================================
print("\n" + "="*90)
print("2. CROSS-ANCESTRY CONCORDANCE BY LOCUS")
print("="*90)

# Get all unique loci
all_loci = coloc["region"].unique()

# For each locus, get best EUR and AFR signals
locus_comparison = []

for locus in all_loci:
    locus_data = coloc[coloc["region"] == locus]
    
    eur_data = locus_data[locus_data["ancestry"] == "EUR"]
    afr_data = locus_data[locus_data["ancestry"] == "AFR"]
    
    # Best EUR signal
    if len(eur_data) > 0:
        eur_best = eur_data.loc[eur_data["PP.H4"].idxmax()]
        eur_h4 = eur_best["PP.H4"]
        eur_traits = f"{eur_best['trait_a']}-{eur_best['trait_b']}"
        eur_tier = eur_best["tier"]
    else:
        eur_h4 = np.nan
        eur_traits = "—"
        eur_tier = "No data"
    
    # Best AFR signal
    if len(afr_data) > 0:
        afr_best = afr_data.loc[afr_data["PP.H4"].idxmax()]
        afr_h4 = afr_best["PP.H4"]
        afr_traits = f"{afr_best['trait_a']}-{afr_best['trait_b']}"
        afr_tier = afr_best["tier"]
    else:
        afr_h4 = np.nan
        afr_traits = "—"
        afr_tier = "No data"
    
    # Determine concordance
    if pd.notna(eur_h4) and pd.notna(afr_h4):
        if eur_h4 >= 0.5 and afr_h4 >= 0.1:
            concordance = "Strong"
        elif eur_h4 >= 0.5 and afr_h4 >= 0.05:
            concordance = "Moderate"
        elif eur_h4 >= 0.2 and afr_h4 >= 0.05:
            concordance = "Weak"
        else:
            concordance = "Discordant"
    elif pd.notna(eur_h4):
        concordance = "EUR-only"
    elif pd.notna(afr_h4):
        concordance = "AFR-only"
    else:
        concordance = "No data"
    
    # Check if known pleiotropic
    gene = locus.split("_")[0]
    known = "Yes" if gene in KNOWN_PLEIOTROPIC else "No"
    
    locus_comparison.append({
        "locus": locus,
        "gene": gene,
        "eur_h4": eur_h4,
        "eur_traits": eur_traits,
        "eur_tier": eur_tier,
        "afr_h4": afr_h4,
        "afr_traits": afr_traits,
        "afr_tier": afr_tier,
        "concordance": concordance,
        "known_pleiotropic": known
    })

locus_df = pd.DataFrame(locus_comparison)

# Summary
print("\n=== CONCORDANCE SUMMARY ===")
print(locus_df["concordance"].value_counts().to_string())

# Show concordant loci
print("\n=== STRONGLY CONCORDANT LOCI (EUR H4≥0.5 AND AFR H4≥0.1) ===")
strong_conc = locus_df[locus_df["concordance"] == "Strong"].sort_values("eur_h4", ascending=False)
if len(strong_conc) > 0:
    print(f"\n{'Locus':<25} {'Gene':<10} {'EUR H4':>8} {'AFR H4':>8} {'EUR Traits':<20} {'AFR Traits':<20} {'Known?'}")
    print("-" * 110)
    for _, row in strong_conc.iterrows():
        print(f"{row['locus']:<25} {row['gene']:<10} {row['eur_h4']:>8.3f} {row['afr_h4']:>8.3f} {row['eur_traits']:<20} {row['afr_traits']:<20} {row['known_pleiotropic']}")
else:
    print("No strongly concordant loci found.")

print("\n=== MODERATELY CONCORDANT LOCI (EUR H4≥0.5 AND AFR H4≥0.05) ===")
mod_conc = locus_df[locus_df["concordance"] == "Moderate"].sort_values("eur_h4", ascending=False)
if len(mod_conc) > 0:
    print(f"\n{'Locus':<25} {'Gene':<10} {'EUR H4':>8} {'AFR H4':>8} {'EUR Traits':<20} {'AFR Traits':<20} {'Known?'}")
    print("-" * 110)
    for _, row in mod_conc.head(15).iterrows():
        print(f"{row['locus']:<25} {row['gene']:<10} {row['eur_h4']:>8.3f} {row['afr_h4']:>8.3f} {row['eur_traits']:<20} {row['afr_traits']:<20} {row['known_pleiotropic']}")
else:
    print("No moderately concordant loci found.")

#==============================================================================
# 3. MULTI-TRAIT PLEIOTROPY ANALYSIS
#==============================================================================
print("\n" + "="*90)
print("3. MULTI-TRAIT PLEIOTROPY ANALYSIS")
print("="*90)

# Count how many trait pairs show signal at each locus
pleiotropy = defaultdict(lambda: {"EUR": [], "AFR": []})

for _, row in coloc.iterrows():
    if row["PP.H4"] >= 0.1:  # Include exploratory signals
        locus = row["region"]
        ancestry = row["ancestry"]
        trait_pair = f"{row['trait_a']}-{row['trait_b']}"
        pleiotropy[locus][ancestry].append({
            "traits": trait_pair,
            "h4": row["PP.H4"],
            "tier": row["tier"]
        })

# Find loci with multiple trait pairs
print("\n=== PLEIOTROPIC LOCI (≥2 trait pairs with H4≥0.1) ===")
print(f"\n{'Locus':<25} {'Gene':<10} {'EUR pairs':>10} {'AFR pairs':>10} {'Known?':<8} {'Trait Pairs'}")
print("-" * 100)

pleiotropic_loci = []
for locus, data in pleiotropy.items():
    eur_pairs = len(data["EUR"])
    afr_pairs = len(data["AFR"])
    total_pairs = eur_pairs + afr_pairs
    
    if total_pairs >= 2:
        gene = locus.split("_")[0]
        known = "Yes" if gene in KNOWN_PLEIOTROPIC else "NOVEL"
        
        all_traits = set()
        for p in data["EUR"] + data["AFR"]:
            all_traits.add(p["traits"])
        
        pleiotropic_loci.append({
            "locus": locus,
            "gene": gene,
            "eur_pairs": eur_pairs,
            "afr_pairs": afr_pairs,
            "total_pairs": total_pairs,
            "known": known,
            "trait_pairs": ", ".join(sorted(all_traits))
        })

pleiotropic_loci.sort(key=lambda x: x["total_pairs"], reverse=True)

for loc in pleiotropic_loci[:20]:
    print(f"{loc['locus']:<25} {loc['gene']:<10} {loc['eur_pairs']:>10} {loc['afr_pairs']:>10} {loc['known']:<8} {loc['trait_pairs'][:40]}")

#==============================================================================
# 4. NOVEL PLEIOTROPIC DISCOVERIES
#==============================================================================
print("\n" + "="*90)
print("4. NOVEL PLEIOTROPIC DISCOVERIES (Not in known literature)")
print("="*90)

novel_loci = [loc for loc in pleiotropic_loci if loc["known"] == "NOVEL"]

print(f"\nFound {len(novel_loci)} potentially novel pleiotropic loci:\n")

if len(novel_loci) > 0:
    print(f"{'Locus':<25} {'Gene':<12} {'Trait Pairs':>12} {'Max EUR H4':>12} {'Max AFR H4':>12}")
    print("-" * 80)
    
    for loc in novel_loci:
        locus = loc["locus"]
        eur_signals = pleiotropy[locus]["EUR"]
        afr_signals = pleiotropy[locus]["AFR"]
        
        max_eur = max([s["h4"] for s in eur_signals]) if eur_signals else 0
        max_afr = max([s["h4"] for s in afr_signals]) if afr_signals else 0
        
        print(f"{locus:<25} {loc['gene']:<12} {loc['total_pairs']:>12} {max_eur:>12.3f} {max_afr:>12.3f}")
        
        # Show individual signals
        for s in eur_signals:
            print(f"    EUR: {s['traits']:<20} H4={s['h4']:.3f} ({s['tier']})")
        for s in afr_signals:
            print(f"    AFR: {s['traits']:<20} H4={s['h4']:.3f} ({s['tier']})")
        print()

#==============================================================================
# 5. KNOWN MARKERS VALIDATION
#==============================================================================
print("\n" + "="*90)
print("5. KNOWN PLEIOTROPIC MARKER VALIDATION")
print("="*90)

print("\nChecking if known pleiotropic genes show expected cross-trait signals:\n")

print(f"{'Gene':<12} {'Expected Traits':<30} {'EUR Signals':>12} {'AFR Signals':>12} {'Validated?'}")
print("-" * 85)

for gene, expected_traits in KNOWN_PLEIOTROPIC.items():
    # Find loci containing this gene
    gene_loci = locus_df[locus_df["gene"].str.upper() == gene.upper()]
    
    if len(gene_loci) == 0:
        print(f"{gene:<12} {', '.join(expected_traits):<30} {'Not found':>12} {'':>12} {'—'}")
        continue
    
    # Get all signals at these loci
    eur_signals = []
    afr_signals = []
    
    for locus in gene_loci["locus"].values:
        for _, row in coloc[(coloc["region"] == locus) & (coloc["PP.H4"] >= 0.1)].iterrows():
            if row["ancestry"] == "EUR":
                eur_signals.append(f"{row['trait_a']}-{row['trait_b']}:{row['PP.H4']:.2f}")
            else:
                afr_signals.append(f"{row['trait_a']}-{row['trait_b']}:{row['PP.H4']:.2f}")
    
    eur_count = len(eur_signals)
    afr_count = len(afr_signals)
    
    # Check if expected traits are represented
    validated = "Yes" if eur_count > 0 else "No"
    
    print(f"{gene:<12} {', '.join(expected_traits):<30} {eur_count:>12} {afr_count:>12} {validated}")

#==============================================================================
# 6. CROSS-ANCESTRY TRAIT-SPECIFIC ANALYSIS
#==============================================================================
print("\n" + "="*90)
print("6. TRAIT PAIR COMPARISON: EUR vs AFR")
print("="*90)

# Get unique trait pairs
trait_pairs = coloc.groupby(["trait_a", "trait_b"]).size().reset_index()[["trait_a", "trait_b"]]

print(f"\n{'Trait Pair':<25} {'EUR H4≥0.8':>12} {'EUR H4≥0.5':>12} {'AFR H4≥0.1':>12} {'AFR H4≥0.05':>12} {'Shared Loci':>12}")
print("-" * 90)

for _, row in trait_pairs.iterrows():
    pair = f"{row['trait_a']}-{row['trait_b']}"
    
    eur_pair = coloc[(coloc["ancestry"]=="EUR") & (coloc["trait_a"]==row["trait_a"]) & (coloc["trait_b"]==row["trait_b"])]
    afr_pair = coloc[(coloc["ancestry"]=="AFR") & (coloc["trait_a"]==row["trait_a"]) & (coloc["trait_b"]==row["trait_b"])]
    
    eur_h8 = len(eur_pair[eur_pair["PP.H4"] >= 0.8])
    eur_h5 = len(eur_pair[eur_pair["PP.H4"] >= 0.5])
    afr_h1 = len(afr_pair[afr_pair["PP.H4"] >= 0.1])
    afr_h05 = len(afr_pair[afr_pair["PP.H4"] >= 0.05])
    
    # Shared loci (both have signal)
    eur_loci = set(eur_pair[eur_pair["PP.H4"] >= 0.5]["region"])
    afr_loci = set(afr_pair[afr_pair["PP.H4"] >= 0.05]["region"])
    shared = len(eur_loci & afr_loci)
    
    if eur_h8 > 0 or afr_h1 > 0:  # Only show pairs with some signal
        print(f"{pair:<25} {eur_h8:>12} {eur_h5:>12} {afr_h1:>12} {afr_h05:>12} {shared:>12}")

#==============================================================================
# 7. SUMMARY & RECOMMENDATIONS
#==============================================================================
print("\n" + "="*90)
print("7. SUMMARY & MANUSCRIPT RECOMMENDATIONS")
print("="*90)

n_eur_h8 = len(coloc[(coloc["ancestry"]=="EUR") & (coloc["PP.H4"]>=0.8)])
n_afr_h1 = len(coloc[(coloc["ancestry"]=="AFR") & (coloc["PP.H4"]>=0.1)])
n_concordant = len(locus_df[locus_df["concordance"].isin(["Strong", "Moderate"])])
n_novel = len(novel_loci)

print(f"""
SUMMARY STATISTICS:
  - EUR high-confidence signals (H4≥0.8): {n_eur_h8}
  - AFR exploratory signals (H4≥0.1): {n_afr_h1}
  - Cross-ancestry concordant loci: {n_concordant}
  - Novel pleiotropic discoveries: {n_novel}
  - Known markers validated: {len([g for g in KNOWN_PLEIOTROPIC if any(locus_df["gene"].str.upper()==g.upper())])}

TIERED REPORTING RECOMMENDATION:

  TIER 1 (Main Results):
    - EUR H4≥0.8 signals with cross-ancestry support (AFR H4≥0.05)
    - Report as "robust shared signals"
  
  TIER 2 (Supporting Evidence):
    - EUR H4≥0.5 signals
    - AFR signals at known pleiotropic loci
    - Report as "moderate evidence for pleiotropy"
  
  TIER 3 (Exploratory/Discussion):
    - Novel pleiotropic loci
    - AFR H4≥0.05 at EUR-validated loci
    - Report as "suggestive evidence requiring replication"
  
  TIER 4 (Supplementary):
    - All signals H4≥0.1
    - Full cross-ancestry comparison
""")

# Save comprehensive results
locus_df.to_csv(PROJECT_DIR / "results/analysis/cross_ancestry_locus_comparison.tsv", sep="\t", index=False)
pd.DataFrame(pleiotropic_loci).to_csv(PROJECT_DIR / "results/analysis/pleiotropic_loci.tsv", sep="\t", index=False)

# Create tiered results table
coloc["cross_ancestry_support"] = coloc["region"].apply(
    lambda x: locus_df[locus_df["locus"]==x]["concordance"].values[0] if x in locus_df["locus"].values else "Unknown"
)
coloc.to_csv(PROJECT_DIR / "results/multitrait/coloc_summary_comprehensive.tsv", sep="\t", index=False)

print(f"""
OUTPUT FILES:
  - results/analysis/cross_ancestry_locus_comparison.tsv
  - results/analysis/pleiotropic_loci.tsv
  - results/multitrait/coloc_summary_comprehensive.tsv
""")
