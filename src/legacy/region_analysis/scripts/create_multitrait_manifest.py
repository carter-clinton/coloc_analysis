#!/usr/bin/env python
import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.manifest_utils import harmonized_records
from scripts.utils_logging import get_logger

logger = get_logger()


def parse_args():
    parser = argparse.ArgumentParser(description="Summarize harmonized files for multi-trait modeling.")
    parser.add_argument("--harmonized", nargs="+", required=True, help="Harmonized sumstats (trait.ancestry.tsv.bgz).")
    parser.add_argument("--regions", required=True, help="Curated regions CSV.")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    records = harmonized_records(args.harmonized)
    regions_df = pd.read_csv(args.regions)
    region_count = regions_df.shape[0]

    manifest = pd.DataFrame(records)
    manifest["regions_file"] = args.regions
    manifest["region_count"] = region_count
    manifest["size_bytes"] = manifest["path"].apply(lambda p: Path(p).stat().st_size if Path(p).exists() else 0)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Writing multitrait manifest with {len(manifest)} entries to {args.output}")
    manifest.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
