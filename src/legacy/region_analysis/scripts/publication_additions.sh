#!/bin/bash
# Publication additions - bash version (no pandas dependency)

PROJECT_DIR="/share/clintonlab/ckclinto/admix_map"
COLOC_DIR="$PROJECT_DIR/results/multitrait/coloc"
ANALYSIS_DIR="$PROJECT_DIR/results/analysis"
mkdir -p "$ANALYSIS_DIR"

echo "=============================================================================="
echo "           PUBLICATION ADDITIONS - FINEMAPPING & STATISTICS"
echo "=============================================================================="

#==============================================================================
# 1. FINE-MAPPING INTEGRATION WITH COLOC
#==============================================================================
echo ""
echo "=============================================================================="
echo "1. FINE-MAPPING INTEGRATION WITH COLOC"
echo "=============================================================================="

# Check if fine-mapping results exist
FM_FILE="$PROJECT_DIR/results/fine_mapping/finemap_summary_augmented.tsv"
COLOC_FILE="$PROJECT_DIR/results/multitrait/coloc_summary.tsv"

if [ -f "$FM_FILE" ] && [ -f "$COLOC_FILE" ]; then
    echo ""
    echo "Integrating fine-mapping with colocalization results..."
    
    # Get high-confidence coloc signals
    awk -F'\t' 'NR==1 {for(i=1;i<=NF;i++) if($i=="PP.H4") h=i; if($i=="region") r=i; if($i=="ancestry") a=i; if($i=="trait_a") ta=i; if($i=="trait_b") tb=i}
                NR>1 && $h>=0.5 {print $r"\t"$a"\t"$ta"\t"$tb"\t"$h}' "$COLOC_FILE" | \
        head -20 | while IFS=$'\t' read region anc trait_a trait_b h4; do
        
        gene=$(echo "$region" | cut -d'_' -f1)
        echo "  Coloc signal: $region ($trait_a-$trait_b, H4=$h4)"
        
        # Look for fine-mapping at this locus
        grep -i "$gene" "$FM_FILE" 2>/dev/null | grep "$anc" | head -2
    done
else
    echo "Fine-mapping or coloc file not found. Skipping integration."
fi

#==============================================================================
# 2. EFFECT SIZE CONCORDANCE FROM JSON FILES
#==============================================================================
echo ""
echo "=============================================================================="
echo "2. EFFECT SIZE CONCORDANCE ANALYSIS"
echo "=============================================================================="

echo ""
echo "Analyzing effect size concordance from coloc JSON files..."
echo "(Sampling first 50 high-confidence signals)"

n_same_dir=0
n_total=0

for json in "$COLOC_DIR"/*.json; do
    [ ! -f "$json" ] && continue
    
    # Extract H4
    h4=$(python3 -c "import json; print(json.load(open('$json')).get('summary', {}).get('PP.H4.abf', 0))" 2>/dev/null || echo "0")
    
    # Only analyze H4 > 0.5
    if python3 -c "exit(0 if float('$h4') > 0.5 else 1)" 2>/dev/null; then
        n_total=$((n_total + 1))
        
        # Check if betas have same sign (would need to parse lead SNP info)
        # For now, just count
        
        [ $n_total -ge 50 ] && break
    fi
done

echo "  Analyzed $n_total high-confidence signals"
echo "  (Detailed effect size analysis requires JSON parsing)"

#==============================================================================
# 3. KEY STATISTICS FOR MANUSCRIPT
#==============================================================================
echo ""
echo "=============================================================================="
echo "3. KEY STATISTICS FOR MANUSCRIPT"
echo "=============================================================================="

COLOC_SUMMARY="$PROJECT_DIR/results/multitrait/coloc_summary.tsv"
LOCUS_COMP="$ANALYSIS_DIR/locus_comparison.tsv"
PLEIO="$ANALYSIS_DIR/pleiotropic_loci.tsv"

if [ -f "$COLOC_SUMMARY" ]; then
    echo ""
    echo "=== MANUSCRIPT STATISTICS ==="
    
    total_pairs=$(awk 'NR>1' "$COLOC_SUMMARY" | wc -l)
    eur_pairs=$(awk -F'\t' 'NR>1 && $2=="EUR"' "$COLOC_SUMMARY" | wc -l)
    afr_pairs=$(awk -F'\t' 'NR>1 && $2=="AFR"' "$COLOC_SUMMARY" | wc -l)
    
    eur_h4_08=$(awk -F'\t' 'NR>1 && $2=="EUR" && $11>=0.8' "$COLOC_SUMMARY" | wc -l)
    eur_h4_05=$(awk -F'\t' 'NR>1 && $2=="EUR" && $11>=0.5' "$COLOC_SUMMARY" | wc -l)
    afr_h4_01=$(awk -F'\t' 'NR>1 && $2=="AFR" && $11>=0.1' "$COLOC_SUMMARY" | wc -l)
    
    unique_loci_h4_08=$(awk -F'\t' 'NR>1 && $11>=0.8 {print $1}' "$COLOC_SUMMARY" | sort -u | wc -l)
    
    echo "  total_pairs_analyzed: $total_pairs"
    echo "  eur_pairs: $eur_pairs"
    echo "  afr_pairs: $afr_pairs"
    echo "  eur_h4_08 (high-conf): $eur_h4_08"
    echo "  eur_h4_05 (strong): $eur_h4_05"
    echo "  afr_h4_01 (exploratory): $afr_h4_01"
    echo "  unique_loci_h4_08: $unique_loci_h4_08"
    echo "  traits_analyzed: 5"
    echo "  ancestries_analyzed: 2"
    
    if [ -f "$LOCUS_COMP" ]; then
        concordant_strong=$(awk -F'\t' '$6=="Strong"' "$LOCUS_COMP" | wc -l)
        concordant_moderate=$(awk -F'\t' '$6=="Moderate"' "$LOCUS_COMP" | wc -l)
        echo "  concordant_loci_strong: $concordant_strong"
        echo "  concordant_loci_moderate: $concordant_moderate"
    fi
    
    if [ -f "$PLEIO" ]; then
        pleiotropic_loci=$(awk 'NR>1' "$PLEIO" | wc -l)
        echo "  pleiotropic_loci: $pleiotropic_loci"
    fi
    
    # Save to file
    cat > "$ANALYSIS_DIR/manuscript_statistics.txt" << EOFSTATS
MANUSCRIPT STATISTICS
Generated: $(date)

Total pairs analyzed: $total_pairs
EUR pairs: $eur_pairs
AFR pairs: $afr_pairs

EUR high-confidence (H4≥0.8): $eur_h4_08
EUR strong (H4≥0.5): $eur_h4_05
AFR exploratory (H4≥0.1): $afr_h4_01

Unique loci (H4≥0.8): $unique_loci_h4_08
Concordant loci (strong): ${concordant_strong:-0}
Concordant loci (moderate): ${concordant_moderate:-0}
Pleiotropic loci (≥2 pairs): ${pleiotropic_loci:-0}

Traits analyzed: 5 (asthma, bmi, hypertension, stroke, t2d)
Ancestries: 2 (EUR, AFR)
EOFSTATS
    
    echo ""
    echo "Saved to: $ANALYSIS_DIR/manuscript_statistics.txt"
fi

#==============================================================================
# 4. CREATE TABLES FOR MANUSCRIPT
#==============================================================================
echo ""
echo "=============================================================================="
echo "4. GENERATING MANUSCRIPT TABLES"
echo "=============================================================================="

# Table 1: Top 20 signals
echo ""
echo "Creating Table 1: Top 20 Colocalization Signals..."

echo -e "Rank\tLocus\tAncestry\tTrait_A\tTrait_B\tPP.H4\tPP.H3\tn_SNPs" > "$ANALYSIS_DIR/Table1_Top20_Signals.tsv"
awk -F'\t' 'NR==1 {for(i=1;i<=NF;i++) {if($i=="region") r=i; if($i=="ancestry") a=i; if($i=="trait_a") ta=i; if($i=="trait_b") tb=i; if($i=="PP.H4") h4=i; if($i=="PP.H3") h3=i; if($i=="n_snps") n=i}}
            NR>1 {print $r"\t"$a"\t"$ta"\t"$tb"\t"$h4"\t"$h3"\t"$n}' "$COLOC_SUMMARY" | \
    sort -t$'\t' -k5 -rn | head -20 | awk -F'\t' '{print NR"\t"$0}' >> "$ANALYSIS_DIR/Table1_Top20_Signals.tsv"

echo "  Saved: $ANALYSIS_DIR/Table1_Top20_Signals.tsv"

# Table 2: Cross-ancestry concordance
if [ -f "$LOCUS_COMP" ]; then
    echo ""
    echo "Creating Table 2: Cross-Ancestry Concordance..."
    
    cp "$LOCUS_COMP" "$ANALYSIS_DIR/Table2_Cross_Ancestry_Concordance.tsv"
    echo "  Saved: $ANALYSIS_DIR/Table2_Cross_Ancestry_Concordance.tsv"
fi

# Table 3: Pleiotropic loci
if [ -f "$PLEIO" ]; then
    echo ""
    echo "Creating Table 3: Pleiotropic Loci..."
    
    cp "$PLEIO" "$ANALYSIS_DIR/Table3_Pleiotropic_Loci.tsv"
    echo "  Saved: $ANALYSIS_DIR/Table3_Pleiotropic_Loci.tsv"
fi

echo ""
echo "=============================================================================="
echo "                    PUBLICATION ADDITIONS COMPLETE"
echo "=============================================================================="
echo ""
echo "Output files:"
ls -lh "$ANALYSIS_DIR"/*.{tsv,txt} 2>/dev/null
echo ""
