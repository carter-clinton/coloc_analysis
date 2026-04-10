#!/usr/bin/env python3
import subprocess
import pandas as pd
from pathlib import Path
import sys
import os

# Add tabix to PATH
os.environ["PATH"] = "/rs1/researchers/c/ckclinto/conda_envs/nyabg-tools/bin:" + os.environ.get("PATH", "")

PROJECT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/share/clintonlab/ckclinto/admix_map")
HARMONIZED_DIR = PROJECT_DIR / "data_processed/sumstats_harmonized_fixed"
OUTPUT_FILE = PROJECT_DIR / "results/diagnostics/no_overlap_diagnosis.tsv"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

coloc_df = pd.read_csv(PROJECT_DIR / "results/multitrait/coloc_summary_augmented.tsv", sep="\t")
regions_df = pd.read_csv(PROJECT_DIR / "config/regions_tiled.csv")

no_overlap = coloc_df[(coloc_df["ancestry"] == "AFR") & (coloc_df["qc_flag"].str.contains("NO_OVERLAP", na=False))]
print(f"Analyzing {len(no_overlap)} AFR NO_OVERLAP pairs...")

def get_counts(file, chrom, start, end):
    # Only check numeric chromosome (no chr prefix based on Step 1 results)
    try:
        tabix_num = int(subprocess.run(f"tabix {file} {chrom}:{start}-{end} 2>/dev/null | wc -l", shell=True, capture_output=True, text=True, timeout=30).stdout.strip() or 0)
    except:
        tabix_num = 0
    # Skip expensive awk verification - trust tabix results
    return tabix_num

results = []
for idx, row in no_overlap.iterrows():
    region_match = regions_df[regions_df["region_id"].str.contains(row["base_region"].split("__")[0], case=False, na=False)]
    if len(region_match) == 0: continue
    r = region_match.iloc[0]
    chrom, start, end = str(r.get("chr", r.get("CHR"))), int(r.get("start", r.get("START", 0))), int(r.get("end", r.get("END", 0)))

    file_a, file_b = HARMONIZED_DIR / f"{row['trait_a']}.AFR.tsv.bgz", HARMONIZED_DIR / f"{row['trait_b']}.AFR.tsv.bgz"
    if not file_a.exists() or not file_b.exists(): continue

    count_a = get_counts(file_a, chrom, start, end)
    count_b = get_counts(file_b, chrom, start, end)

    if count_a == 0 and count_b == 0: diag = "both_zero"
    elif count_a == 0 or count_b == 0: diag = "one_zero"
    else: diag = "both_nonzero"

    results.append({"pair_id": row["pair_id"], "region": f"{chrom}:{start}-{end}", "count_a": count_a, "count_b": count_b, "diagnosis": diag})
    if len(results) % 10 == 0:
        print(f"  {len(results)}/{len(no_overlap)}")
        # Save intermediate results
        pd.DataFrame(results).to_csv(OUTPUT_FILE, sep="\t", index=False)

pd.DataFrame(results).to_csv(OUTPUT_FILE, sep="\t", index=False)
print(f"\nSaved: {OUTPUT_FILE}")
print(pd.DataFrame(results)["diagnosis"].value_counts())
