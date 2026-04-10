#!/usr/bin/env python3
import subprocess
import pandas as pd
from pathlib import Path
import os

# Add tabix to PATH
os.environ["PATH"] = "/rs1/researchers/c/ckclinto/conda_envs/nyabg-tools/bin:" + os.environ.get("PATH", "")

PROJECT_DIR = Path("/share/clintonlab/ckclinto/admix_map")
HARMONIZED_DIR = PROJECT_DIR / "data_processed/sumstats_harmonized_fixed"

coloc_df = pd.read_csv(PROJECT_DIR / "results/multitrait/coloc_summary_augmented.tsv", sep="\t")
regions_df = pd.read_csv(PROJECT_DIR / "config/regions_tiled.csv")

no_overlap = coloc_df[(coloc_df["ancestry"] == "AFR") & (coloc_df["qc_flag"].str.contains("NO_OVERLAP", na=False))]

print("=== DEBUG: First 3 NO_OVERLAP pairs with PATH fix ===\n")
for idx, row in no_overlap.head(3).iterrows():
    print(f"Pair: {row['pair_id']}")

    search_term = row["base_region"].split("__")[0]
    region_match = regions_df[regions_df["region_id"].str.contains(search_term, case=False, na=False)]

    if len(region_match) == 0:
        print("  ERROR: No match!\n")
        continue

    r = region_match.iloc[0]
    chrom, start, end = str(r["chr"]), int(r["start"]), int(r["end"])

    file_a = HARMONIZED_DIR / f"{row['trait_a']}.AFR.tsv.bgz"
    query = f"{chrom}:{start}-{end}"
    cmd = f"tabix {file_a} {query} 2>/dev/null | wc -l"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    count = int(result.stdout.strip() or 0)
    print(f"  Query: {query}")
    print(f"  Count: {count}\n")
