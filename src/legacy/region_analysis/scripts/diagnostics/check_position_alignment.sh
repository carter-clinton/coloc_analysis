#!/bin/bash
# Check if AFR files have aligned positions

PROJECT_DIR="${1:-/gpfs_common/share01/clintonlab/ckclinto/admix_map}"
HARMONIZED_DIR="$PROJECT_DIR/data_processed/sumstats_harmonized_fixed"

echo "=== POSITION DISTRIBUTION IN APOE REGION (chr19:45000000-46500000) ==="

for trait in asthma stroke t2d; do
  file="$HARMONIZED_DIR/${trait}.AFR.tsv.bgz"
  echo ""
  echo "--- ${trait}.AFR ---"

  # Get position statistics
  tabix "$file" 19:45000000-46500000 2>/dev/null | awk -F'\t' '
    BEGIN {min=999999999; max=0}
    {
      if ($2 < min) min = $2
      if ($2 > max) max = $2
      count++
    }
    END {
      print "  Variants: " count
      print "  Min POS: " min
      print "  Max POS: " max
      print "  Range: " (max - min)
    }
  '

  # Show first 5 positions
  echo "  First 5 positions:"
  tabix "$file" 19:45000000-46500000 2>/dev/null | head -5 | awk -F'\t' '{print "    " $1 ":" $2}'

  # Show last 5 positions
  echo "  Last 5 positions:"
  tabix "$file" 19:45000000-46500000 2>/dev/null | tail -5 | awk -F'\t' '{print "    " $1 ":" $2}'
done

echo ""
echo "=== CHECKING FOR POSITION OVERLAP ==="

# Extract positions from each file
tabix "$HARMONIZED_DIR/asthma.AFR.tsv.bgz" 19:45000000-46500000 2>/dev/null | cut -f2 | sort -n > /tmp/pos_asthma.txt
tabix "$HARMONIZED_DIR/stroke.AFR.tsv.bgz" 19:45000000-46500000 2>/dev/null | cut -f2 | sort -n > /tmp/pos_stroke.txt
tabix "$HARMONIZED_DIR/t2d.AFR.tsv.bgz" 19:45000000-46500000 2>/dev/null | cut -f2 | sort -n > /tmp/pos_t2d.txt

echo "Unique positions:"
echo "  asthma: $(wc -l < /tmp/pos_asthma.txt)"
echo "  stroke: $(wc -l < /tmp/pos_stroke.txt)"
echo "  t2d: $(wc -l < /tmp/pos_t2d.txt)"

echo ""
echo "Pairwise overlaps:"
echo "  asthma ∩ stroke: $(comm -12 /tmp/pos_asthma.txt /tmp/pos_stroke.txt | wc -l)"
echo "  asthma ∩ t2d: $(comm -12 /tmp/pos_asthma.txt /tmp/pos_t2d.txt | wc -l)"
echo "  stroke ∩ t2d: $(comm -12 /tmp/pos_stroke.txt /tmp/pos_t2d.txt | wc -l)"

echo ""
echo "=== GENOME BUILD CHECK ==="
# Check a known SNP position (rs429358 in APOE is at 44908684 in GRCh38, 45411941 in GRCh37)
echo "Looking for APOE rs429358 (GRCh37: 45411941, GRCh38: 44908684)..."
for trait in asthma stroke t2d; do
  file="$HARMONIZED_DIR/${trait}.AFR.tsv.bgz"
  echo "  ${trait}.AFR:"
  zcat "$file" | awk -F'\t' '$2==45411941 || $2==44908684 {print "    Found at POS=" $2}' | head -1 || echo "    Not found"
done

rm -f /tmp/pos_*.txt
