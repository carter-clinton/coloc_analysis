#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path("/share/clintonlab/ckclinto/admix_map")

coloc_df = pd.read_csv(PROJECT_DIR / "results/multitrait/coloc_summary_augmented.tsv", sep="\t")
regions_df = pd.read_csv(PROJECT_DIR / "config/regions_tiled.csv")

print("=== REGIONS FILE STRUCTURE ===")
print(f"Columns: {list(regions_df.columns)}")
print(f"Sample rows:\n{regions_df.head()}\n")

print("=== COLOC NO_OVERLAP PAIRS ===")
no_overlap = coloc_df[(coloc_df["ancestry"] == "AFR") & (coloc_df["qc_flag"].str.contains("NO_OVERLAP", na=False))]
print(f"Total: {len(no_overlap)}")
print(f"Sample base_regions: {no_overlap['base_region'].head(10).tolist()}\n")

print("=== REGION LOOKUP TEST ===")
for base_region in no_overlap["base_region"].head(10):
    search_term = base_region.split("__")[0]  # Remove __tile suffix if present

    # Try different matching strategies
    exact = regions_df[regions_df["region_id"] == base_region]
    contains = regions_df[regions_df["region_id"].str.contains(search_term, case=False, na=False)]
    startswith = regions_df[regions_df["region_id"].str.startswith(search_term, na=False)]

    print(f"{base_region}:")
    print(f"  search_term: '{search_term}'")
    print(f"  exact match: {len(exact)} rows")
    print(f"  contains: {len(contains)} rows")
    print(f"  startswith: {len(startswith)} rows")

    if len(contains) > 0:
        r = contains.iloc[0]
        chr_col = [c for c in regions_df.columns if c.lower() == 'chr'][0] if any(c.lower() == 'chr' for c in regions_df.columns) else None
        start_col = [c for c in regions_df.columns if c.lower() == 'start'][0] if any(c.lower() == 'start' for c in regions_df.columns) else None
        end_col = [c for c in regions_df.columns if c.lower() == 'end'][0] if any(c.lower() == 'end' for c in regions_df.columns) else None
        print(f"  coords: chr={r.get(chr_col, 'N/A')}, start={r.get(start_col, 'N/A')}, end={r.get(end_col, 'N/A')}")
    print()
