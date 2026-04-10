#!/bin/bash
cd /share/clintonlab/ckclinto/admix_map

echo "=== AFR COLOC RESULTS SUMMARY ==="
echo ""

# Regenerate summaries first
bash scripts/regenerate_coloc_summaries.sh 2>/dev/null

# Count results
total_afr=$(awk -F'\t' '$3=="AFR"' results/multitrait/coloc_summary_augmented.tsv | wc -l)
valid_h4=$(awk -F'\t' '$3=="AFR" && $7!=""' results/multitrait/coloc_summary_augmented.tsv | wc -l)
h4_gt_05=$(awk -F'\t' '$3=="AFR" && $7>0.5' results/multitrait/coloc_summary_augmented.tsv | wc -l)
h4_gt_08=$(awk -F'\t' '$3=="AFR" && $7>0.8' results/multitrait/coloc_summary_augmented.tsv | wc -l)

echo "Total AFR pairs: $total_afr"
echo "With valid PP.H4: $valid_h4"
echo "PP.H4 > 0.5: $h4_gt_05"
echo "PP.H4 > 0.8: $h4_gt_08"

echo ""
echo "=== TOP AFR H4 SIGNALS ==="
awk -F'\t' 'NR==1{print "Region\tTraitA\tTraitB\tPP.H4\tn_snps"} 
            $3=="AFR" && $7>0.3 {print $2"\t"$4"\t"$5"\t"$7"\t"$8}' \
  results/multitrait/coloc_summary_augmented.tsv | sort -t$'\t' -k4 -rn | head -20 | column -t

echo ""
echo "=== COMPARISON: EUR vs AFR H4 COUNTS ==="
echo "EUR PP.H4 > 0.8: $(awk -F'\t' '$3=="EUR" && $7>0.8' results/multitrait/coloc_summary_augmented.tsv | wc -l)"
echo "AFR PP.H4 > 0.8: $h4_gt_08"

echo ""
echo "=== QC FLAG DISTRIBUTION (AFR) ==="
awk -F'\t' '$3=="AFR" {print $NF}' results/multitrait/coloc_summary_augmented.tsv | sort | uniq -c | sort -rn | head -10
