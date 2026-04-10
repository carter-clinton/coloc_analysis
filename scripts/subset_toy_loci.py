#!/usr/bin/env python3
"""
Subset GWAS summary statistics to toy 3-locus regions for CI smoke testing.

Usage:
    python scripts/subset_toy_loci.py \
        --config config/pipeline.yaml \
        --test-config tests/toy_3locus/config_test.yaml

Reads full harmonized sumstats from paths in --config, subsets to regions
defined in tests/toy_3locus/data/regions_toy.csv, writes subsets to the
raw_sumstats directory specified in --test-config.

This script is run ONCE after full data is downloaded (Phase 0 Track 0a or
Phase 1 data preparation) to populate tests/toy_3locus/data/.

Requires: tabix-indexed (.bgz + .tbi) harmonized sumstats in the production
harmonized_sumstats directory.
"""

import argparse
import csv
import os
import subprocess
import sys

import yaml


# Three well-characterized loci for CI regression testing (D-14)
TOY_LOCI = {
    "FTO_16q12_2":    {"chr": "16", "start": 53800000,  "end": 54400000},
    "TCF7L2_10q25_2": {"chr": "10", "start": 114550000, "end": 115150000},
    "SH2B3_12q24_12": {"chr": "12", "start": 111400000, "end": 112000000},
}


def subset_sumstats(input_bgz, output_path, regions):
    """Extract rows within genomic regions from a bgzipped, tabix-indexed sumstats file.

    Uses tabix for indexed region queries (O(log n) per region) rather than
    scanning the entire file.
    """
    # Get header from the bgzipped file
    header_cmd = ["bash", "-c", "zcat '{}' | head -1".format(input_bgz)]
    header_result = subprocess.run(header_cmd, capture_output=True, text=True, check=True)
    header = header_result.stdout

    # Query each toy locus region via tabix
    rows = []
    total_variants = 0
    for name, region in regions.items():
        query = "{}:{}-{}".format(region["chr"], region["start"], region["end"])
        cmd = ["tabix", input_bgz, query]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            block = result.stdout.strip()
            n_variants = len(block.split("\n"))
            total_variants += n_variants
            rows.append(block)
            print("    {} ({}): {} variants".format(name, query, n_variants))
        else:
            print("    {} ({}): 0 variants (tabix returned empty)".format(name, query))

    # Write subsetted output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(header)
        for block in rows:
            f.write(block + "\n")

    print("  Total: {} variants written to {}".format(total_variants, output_path))
    return total_variants


def main():
    parser = argparse.ArgumentParser(
        description="Subset harmonized sumstats for the toy 3-locus CI smoke test"
    )
    parser.add_argument(
        "--config",
        default="config/pipeline.yaml",
        help="Production pipeline config (default: config/pipeline.yaml)",
    )
    parser.add_argument(
        "--test-config",
        default="tests/toy_3locus/config_test.yaml",
        help="Test config (default: tests/toy_3locus/config_test.yaml)",
    )
    parser.add_argument(
        "--regions",
        default="tests/toy_3locus/data/regions_toy.csv",
        help="Toy regions CSV (default: tests/toy_3locus/data/regions_toy.csv)",
    )
    args = parser.parse_args()

    # Load configs
    with open(args.config) as f:
        cfg = yaml.safe_load(f)
    with open(args.test_config) as f:
        test_cfg = yaml.safe_load(f)

    harmonized_dir = cfg["paths"]["harmonized_sumstats"]
    test_raw_dir = test_cfg["paths"]["raw_sumstats"]

    # Optionally load regions from CSV (for logging)
    if os.path.exists(args.regions):
        with open(args.regions, newline="") as f:
            reader = csv.DictReader(f)
            region_names = [row["region_id"] for row in reader]
        print("Toy regions: {}".format(", ".join(region_names)))
    print("Source: {}".format(harmonized_dir))
    print("Destination: {}".format(test_raw_dir))
    print()

    # Subset each trait x ancestry pair from the test config
    skipped = []
    processed = []
    for trait in test_cfg["traits"]:
        ancestries = test_cfg.get("trait_ancestries", {}).get(
            trait, test_cfg["ancestries"]
        )
        for ancestry in ancestries:
            input_file = os.path.join(harmonized_dir, "{}.{}.tsv.bgz".format(trait, ancestry))
            output_file = os.path.join(test_raw_dir, "{}.{}.tsv".format(trait, ancestry))

            if not os.path.exists(input_file):
                print("SKIP: {} not found (data not yet downloaded)".format(input_file))
                skipped.append("{}.{}".format(trait, ancestry))
                continue

            # Check for tabix index
            tbi_file = input_file + ".tbi"
            if not os.path.exists(tbi_file):
                print(
                    "SKIP: {} has no tabix index (.tbi) -- "
                    "run harmonization pipeline first".format(input_file)
                )
                skipped.append("{}.{}".format(trait, ancestry))
                continue

            print("Subsetting {}.{}...".format(trait, ancestry))
            n = subset_sumstats(input_file, output_file, TOY_LOCI)
            processed.append("{}.{} ({} variants)".format(trait, ancestry, n))

    # Summary
    print()
    print("=" * 60)
    print("Subset complete.")
    if processed:
        print("  Processed: {}".format(len(processed)))
        for p in processed:
            print("    - {}".format(p))
    if skipped:
        print("  Skipped (data not available): {}".format(len(skipped)))
        for s in skipped:
            print("    - {}".format(s))
    if skipped:
        print()
        print(
            "NOTE: Skipped files will be available after running the "
            "data download pipeline (Phase 0 Track 0a)."
        )


if __name__ == "__main__":
    main()
