#!/bin/bash
set -euo pipefail

export PATH="/rs1/researchers/c/ckclinto/conda_envs/nyabg-tools/bin:$PATH"
PROJECT_DIR="/share/clintonlab/ckclinto/admix_map"

echo "=== Testing actual tiled region coordinates ==="
echo ""

# APOE from regions_tiled.csv
echo "APOE_19q13 (from regions_tiled.csv: 19:44900000-45300000)"
for trait in asthma stroke t2d; do
  count=$(tabix "$PROJECT_DIR/data_processed/sumstats_harmonized_fixed/${trait}.AFR.tsv.bgz" 19:44900000-45300000 2>/dev/null | wc -l)
  echo "  ${trait}.AFR: $count variants"
done
echo ""

# ACE_AGT from regions_tiled.csv
echo "ACE_AGT_1q42 (from regions_tiled.csv: 1:229500000-230000000)"
for trait in asthma stroke t2d; do
  count=$(tabix "$PROJECT_DIR/data_processed/sumstats_harmonized_fixed/${trait}.AFR.tsv.bgz" 1:229500000-230000000 2>/dev/null | wc -l)
  echo "  ${trait}.AFR: $count variants"
done
echo ""

# ANGPTL3 from regions_tiled.csv
echo "ANGPTL3_1p31.1 (from regions_tiled.csv: 1:62820000-63320000)"
for trait in asthma stroke t2d; do
  count=$(tabix "$PROJECT_DIR/data_processed/sumstats_harmonized_fixed/${trait}.AFR.tsv.bgz" 1:62820000-63320000 2>/dev/null | wc -l)
  echo "  ${trait}.AFR: $count variants"
done
