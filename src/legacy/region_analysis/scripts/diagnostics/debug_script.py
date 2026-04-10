#!/usr/bin/env python3
import subprocess
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path("/share/clintonlab/ckclinto/admix_map")
HARMONIZED_DIR = PROJECT_DIR / "data_processed/sumstats_harmonized_fixed"

coloc_df = pd.read_csv(PROJECT_DIR / "results/multitrait/coloc_summary_augmented.tsv", sep="\t")
regions_df = pd.read_csv(PROJECT_DIR / "config/regions_tiled.csv")

no_overlap = coloc_df[(coloc_df["ancestry"] == "AFR") & (coloc_df["qc_flag"].str.contains("NO_OVERLAP", na=False))]

print("=== DEBUG: First 3 NO_OVERLAP pairs ===\n")
for idx, row in no_overlap.head(3).iterrows():
    print(f"Pair: {row['pair_id']}")
    print(f"  base_region: {row['base_region']}")

    search_term = row["base_region"].split("__")[0]
    region_match = regions_df[regions_df["region_id"].str.contains(search_term, case=False, na=False)]

    print(f"  search_term: '{search_term}'")
    print(f"  matches found: {len(region_match)}")

    if len(region_match) == 0:
        print("  ERROR: No match!\n")
        continue

    r = region_match.iloc[0]
    print(f"  matched region_id: {r['region_id']}")

    # Test both access methods
    chrom_get = str(r.get("chr", r.get("CHR")))
    start_get = int(r.get("start", r.get("START", 0)))
    end_get = int(r.get("end", r.get("END", 0)))

    chrom_bracket = str(r["chr"])
    start_bracket = int(r["start"])
    end_bracket = int(r["end"])

    print(f"  Using .get(): chr={chrom_get}, start={start_get}, end={end_get}")
    print(f"  Using []: chr={chrom_bracket}, start={start_bracket}, end={end_bracket}")

    # Test tabix
    file_a = HARMONIZED_DIR / f"{row['trait_a']}.AFR.tsv.bgz"
    query = f"{chrom_bracket}:{start_bracket}-{end_bracket}"
    cmd = f"tabix {file_a} {query} 2>/dev/null | wc -l"
    print(f"  Command: {cmd}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    count = int(result.stdout.strip() or 0)
    print(f"  Count: {count}\n")
