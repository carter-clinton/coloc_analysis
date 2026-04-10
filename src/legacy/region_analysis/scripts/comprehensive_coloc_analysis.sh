#!/bin/bash
# Comprehensive Cross-Ancestry Colocalization & Pleiotropy Analysis
# Uses bash/awk for portability

SUMMARY="results/multitrait/coloc_summary.tsv"
OUTDIR="results/analysis"
mkdir -p "$OUTDIR"

echo "=============================================================================================="
echo "           COMPREHENSIVE CROSS-ANCESTRY COLOCALIZATION & PLEIOTROPY ANALYSIS"
echo "=============================================================================================="

#==============================================================================
# 1. TIERED SIGNAL COUNTS BY ANCESTRY
#==============================================================================
echo ""
echo "=============================================================================================="
echo "1. TIERED SIGNAL COUNTS BY ANCESTRY"
echo "=============================================================================================="
echo ""

awk -F'\t' '
NR==1 {
  for(i=1;i<=NF;i++) {
    if($i=="ancestry") a=i
    if($i=="PP.H4") h=i
  }
  next
}
{
  anc = $a
  h4 = $h
  
  if(h4 >= 0.8) tier[anc]["t1"]++
  else if(h4 >= 0.5) tier[anc]["t2"]++
  else if(h4 >= 0.2) tier[anc]["t3"]++
  else if(h4 >= 0.1) tier[anc]["t4"]++
  else if(h4 >= 0.05) tier[anc]["t5"]++
  else tier[anc]["below"]++
  
  total[anc]++
}
END {
  printf "%-35s %10s %10s %10s\n", "Tier", "EUR", "AFR", "Total"
  print "------------------------------------------------------------------------"
  printf "%-35s %10d %10d %10d\n", "Tier 1: High Confidence (≥0.8)", tier["EUR"]["t1"]+0, tier["AFR"]["t1"]+0, tier["EUR"]["t1"]+tier["AFR"]["t1"]
  printf "%-35s %10d %10d %10d\n", "Tier 2: Moderate (0.5-0.8)", tier["EUR"]["t2"]+0, tier["AFR"]["t2"]+0, tier["EUR"]["t2"]+tier["AFR"]["t2"]
  printf "%-35s %10d %10d %10d\n", "Tier 3: Suggestive (0.2-0.5)", tier["EUR"]["t3"]+0, tier["AFR"]["t3"]+0, tier["EUR"]["t3"]+tier["AFR"]["t3"]
  printf "%-35s %10d %10d %10d\n", "Tier 4: Exploratory (0.1-0.2)", tier["EUR"]["t4"]+0, tier["AFR"]["t4"]+0, tier["EUR"]["t4"]+tier["AFR"]["t4"]
  printf "%-35s %10d %10d %10d\n", "Tier 5: Weak (0.05-0.1)", tier["EUR"]["t5"]+0, tier["AFR"]["t5"]+0, tier["EUR"]["t5"]+tier["AFR"]["t5"]
  printf "%-35s %10d %10d %10d\n", "Below threshold (<0.05)", tier["EUR"]["below"]+0, tier["AFR"]["below"]+0, tier["EUR"]["below"]+tier["AFR"]["below"]
  print "------------------------------------------------------------------------"
  printf "%-35s %10d %10d %10d\n", "TOTAL", total["EUR"]+0, total["AFR"]+0, total["EUR"]+total["AFR"]
}' "$SUMMARY"

#==============================================================================
# 2. CROSS-ANCESTRY CONCORDANCE
#==============================================================================
echo ""
echo "=============================================================================================="
echo "2. CROSS-ANCESTRY CONCORDANCE BY LOCUS"
echo "=============================================================================================="
echo ""

# Create locus comparison file
awk -F'\t' '
NR==1 {
  for(i=1;i<=NF;i++) {
    if($i=="region") r=i
    if($i=="ancestry") a=i
    if($i=="trait_a") ta=i
    if($i=="trait_b") tb=i
    if($i=="PP.H4") h=i
  }
  next
}
{
  region = $r
  anc = $a
  h4 = $h
  traits = $ta "-" $tb
  
  if(anc == "EUR") {
    if(h4 > eur_h4[region]) {
      eur_h4[region] = h4
      eur_traits[region] = traits
    }
  } else {
    if(h4 > afr_h4[region]) {
      afr_h4[region] = h4
      afr_traits[region] = traits
    }
  }
  loci[region] = 1
}
END {
  print "region\teur_h4\teur_traits\tafr_h4\tafr_traits\tconcordance"
  
  for(locus in loci) {
    eh4 = eur_h4[locus]+0
    ah4 = afr_h4[locus]+0
    et = (eur_traits[locus] ? eur_traits[locus] : "—")
    at = (afr_traits[locus] ? afr_traits[locus] : "—")
    
    # Determine concordance
    if(eh4 > 0 && ah4 > 0) {
      if(eh4 >= 0.5 && ah4 >= 0.1) conc = "Strong"
      else if(eh4 >= 0.5 && ah4 >= 0.05) conc = "Moderate"
      else if(eh4 >= 0.2 && ah4 >= 0.05) conc = "Weak"
      else conc = "Discordant"
    } else if(eh4 > 0) {
      conc = "EUR-only"
    } else if(ah4 > 0) {
      conc = "AFR-only"
    } else {
      conc = "No-data"
    }
    
    print locus "\t" eh4 "\t" et "\t" ah4 "\t" at "\t" conc
  }
}' "$SUMMARY" > "$OUTDIR/locus_comparison.tsv"

echo "=== CONCORDANCE SUMMARY ==="
awk -F'\t' 'NR>1 {count[$6]++} END {for(c in count) print c ": " count[c]}' "$OUTDIR/locus_comparison.tsv" | sort -k2 -rn

echo ""
echo "=== STRONGLY CONCORDANT LOCI (EUR H4≥0.5 AND AFR H4≥0.1) ==="
printf "\n%-30s %10s %10s %-25s %-25s\n" "Locus" "EUR_H4" "AFR_H4" "EUR_Traits" "AFR_Traits"
echo "--------------------------------------------------------------------------------------------"
awk -F'\t' '$6=="Strong" {printf "%-30s %10.3f %10.3f %-25s %-25s\n", $1, $2, $4, $3, $5}' "$OUTDIR/locus_comparison.tsv" | sort -k2 -rn | head -20

echo ""
echo "=== MODERATELY CONCORDANT LOCI (EUR H4≥0.5 AND AFR H4≥0.05) ==="
printf "\n%-30s %10s %10s %-25s %-25s\n" "Locus" "EUR_H4" "AFR_H4" "EUR_Traits" "AFR_Traits"
echo "--------------------------------------------------------------------------------------------"
awk -F'\t' '$6=="Moderate" {printf "%-30s %10.3f %10.3f %-25s %-25s\n", $1, $2, $4, $3, $5}' "$OUTDIR/locus_comparison.tsv" | sort -k2 -rn | head -15

#==============================================================================
# 3. MULTI-TRAIT PLEIOTROPY
#==============================================================================
echo ""
echo "=============================================================================================="
echo "3. MULTI-TRAIT PLEIOTROPY ANALYSIS"
echo "=============================================================================================="
echo ""

# Count trait pairs per locus
awk -F'\t' '
NR==1 {
  for(i=1;i<=NF;i++) {
    if($i=="region") r=i
    if($i=="ancestry") a=i
    if($i=="trait_a") ta=i
    if($i=="trait_b") tb=i
    if($i=="PP.H4") h=i
  }
  next
}
$h >= 0.1 {
  region = $r
  anc = $a
  pair = $ta "-" $tb
  
  if(anc == "EUR") {
    eur_count[region]++
    eur_pairs[region] = (eur_pairs[region] ? eur_pairs[region] "," pair : pair)
  } else {
    afr_count[region]++
    afr_pairs[region] = (afr_pairs[region] ? afr_pairs[region] "," pair : pair)
  }
}
END {
  print "region\teur_pairs\tafr_pairs\ttotal_pairs\ttrait_list"
  
  for(region in eur_count) {
    ec = eur_count[region]+0
    ac = afr_count[region]+0
    total = ec + ac
    
    if(total >= 2) {
      # Combine trait lists
      all_pairs = ""
      if(eur_pairs[region]) all_pairs = eur_pairs[region]
      if(afr_pairs[region]) all_pairs = (all_pairs ? all_pairs "," afr_pairs[region] : afr_pairs[region])
      
      print region "\t" ec "\t" ac "\t" total "\t" all_pairs
    }
  }
  
  for(region in afr_count) {
    if(!(region in eur_count)) {
      ac = afr_count[region]
      if(ac >= 2) {
        print region "\t0\t" ac "\t" ac "\t" afr_pairs[region]
      }
    }
  }
}' "$SUMMARY" | sort -t$'\t' -k4 -rn > "$OUTDIR/pleiotropic_loci.tsv"

echo "=== PLEIOTROPIC LOCI (≥2 trait pairs with H4≥0.1) ==="
printf "\n%-30s %12s %12s %12s %s\n" "Locus" "EUR_pairs" "AFR_pairs" "Total_pairs" "Trait_Pairs"
echo "--------------------------------------------------------------------------------------------"
awk -F'\t' 'NR>1 {
  gene = $1
  gsub(/_.*/, "", gene)
  printf "%-30s %12d %12d %12d %s\n", $1, $2, $3, $4, substr($5, 1, 50)
}' "$OUTDIR/pleiotropic_loci.tsv" | head -25

#==============================================================================
# 4. TRAIT PAIR ANALYSIS
#==============================================================================
echo ""
echo "=============================================================================================="
echo "6. TRAIT PAIR COMPARISON: EUR vs AFR"
echo "=============================================================================================="
echo ""

printf "\n%-25s %12s %12s %12s %12s %12s\n" "Trait_Pair" "EUR_H4≥0.8" "EUR_H4≥0.5" "AFR_H4≥0.1" "AFR_H4≥0.05" "Shared_Loci"
echo "--------------------------------------------------------------------------------------------"

awk -F'\t' '
NR==1 {
  for(i=1;i<=NF;i++) {
    if($i=="region") r=i
    if($i=="ancestry") a=i
    if($i=="trait_a") ta=i
    if($i=="trait_b") tb=i
    if($i=="PP.H4") h=i
  }
  next
}
{
  pair = $ta "-" $tb
  anc = $a
  h4 = $h
  region = $r
  
  if(anc == "EUR") {
    if(h4 >= 0.8) eur_h8[pair]++
    if(h4 >= 0.5) {
      eur_h5[pair]++
      eur_loci[pair,region] = 1
    }
  } else {
    if(h4 >= 0.1) afr_h1[pair]++
    if(h4 >= 0.05) {
      afr_h05[pair]++
      afr_loci[pair,region] = 1
    }
  }
  
  pairs[pair] = 1
}
END {
  for(pair in pairs) {
    eh8 = eur_h8[pair]+0
    eh5 = eur_h5[pair]+0
    ah1 = afr_h1[pair]+0
    ah05 = afr_h05[pair]+0
    
    # Count shared loci
    shared = 0
    for(key in eur_loci) {
      split(key, arr, SUBSEP)
      if(arr[1] == pair && (pair,arr[2]) in afr_loci) shared++
    }
    
    if(eh8 > 0 || ah1 > 0) {
      printf "%-25s %12d %12d %12d %12d %12d\n", pair, eh8, eh5, ah1, ah05, shared
    }
  }
}' "$SUMMARY" | sort -k2 -rn

#==============================================================================
# 5. SUMMARY STATISTICS
#==============================================================================
echo ""
echo "=============================================================================================="
echo "7. SUMMARY STATISTICS"
echo "=============================================================================================="
echo ""

n_eur_h8=$(awk -F'\t' 'NR>1 && $2=="EUR" && $11>=0.8' "$SUMMARY" | wc -l)
n_eur_h5=$(awk -F'\t' 'NR>1 && $2=="EUR" && $11>=0.5' "$SUMMARY" | wc -l)
n_afr_h1=$(awk -F'\t' 'NR>1 && $2=="AFR" && $11>=0.1' "$SUMMARY" | wc -l)
n_afr_h05=$(awk -F'\t' 'NR>1 && $2=="AFR" && $11>=0.05' "$SUMMARY" | wc -l)
n_concordant=$(awk -F'\t' 'NR>1 && ($6=="Strong" || $6=="Moderate")' "$OUTDIR/locus_comparison.tsv" | wc -l)
n_pleiotropic=$(awk -F'\t' 'NR>1' "$OUTDIR/pleiotropic_loci.tsv" | wc -l)

echo "SUMMARY STATISTICS:"
echo "  - EUR high-confidence signals (H4≥0.8): $n_eur_h8"
echo "  - EUR strong signals (H4≥0.5): $n_eur_h5"
echo "  - AFR exploratory signals (H4≥0.1): $n_afr_h1"
echo "  - AFR weak signals (H4≥0.05): $n_afr_h05"
echo "  - Cross-ancestry concordant loci: $n_concordant"
echo "  - Pleiotropic loci (≥2 trait pairs): $n_pleiotropic"
echo ""
echo "MANUSCRIPT REPORTING RECOMMENDATION:"
echo ""
echo "  TIER 1 (Main Results):"
echo "    - EUR H4≥0.8 signals with cross-ancestry support (AFR H4≥0.05)"
echo "    - Report as 'robust shared signals'"
echo ""
echo "  TIER 2 (Supporting Evidence):"
echo "    - EUR H4≥0.5 signals"
echo "    - AFR signals at validated EUR loci"
echo "    - Report as 'moderate evidence for pleiotropy'"
echo ""
echo "  TIER 3 (Exploratory/Discussion):"
echo "    - Novel pleiotropic loci"
echo "    - EUR-only strong signals without AFR replication"
echo "    - Report as 'suggestive evidence requiring replication'"
echo ""
echo "OUTPUT FILES:"
echo "  - $OUTDIR/locus_comparison.tsv"
echo "  - $OUTDIR/pleiotropic_loci.tsv"
echo ""
echo "=============================================================================================="
