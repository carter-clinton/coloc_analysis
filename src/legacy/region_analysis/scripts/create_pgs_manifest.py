#!/usr/bin/env python
import argparse
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.manifest_utils import harmonized_records
from scripts.utils_logging import get_logger

logger = get_logger()


def parse_args():
    parser = argparse.ArgumentParser(description="Plan cross-ancestry PGS runs.")
    parser.add_argument("--harmonized", nargs="+", required=True)
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def load_pgs_config(path: str) -> Dict[str, List[str]]:
    with open(path, "r") as handle:
        cfg = yaml.safe_load(handle)
    pgs_cfg = cfg.get("pgs", {})
    return {
        "methods": pgs_cfg.get("methods", []),
        "target_ancestries": pgs_cfg.get("target_ancestries", []),
        "ld_reference_dir": pgs_cfg.get("ld_reference_dir", ""),
    }


def main():
    args = parse_args()
    pgs_cfg = load_pgs_config(args.config)
    records = harmonized_records(args.harmonized)

    rows = []
    for entry in records:
        for method in pgs_cfg["methods"]:
            for target in pgs_cfg["target_ancestries"]:
                rows.append(
                    {
                        "trait": entry["trait"],
                        "discovery_ancestry": entry["ancestry"],
                        "target_ancestry": target,
                        "method": method,
                        "sumstats_path": entry["path"],
                        "ld_reference_dir": pgs_cfg["ld_reference_dir"],
                    }
                )

    manifest = pd.DataFrame(rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Writing PGS manifest ({len(manifest)} rows) to {args.output}")
    manifest.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
