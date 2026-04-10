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
    parser = argparse.ArgumentParser(description="Generate MR hypothesis manifest.")
    parser.add_argument("--harmonized", nargs="+", required=True)
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def load_mr_hypotheses(config_path: str) -> List[Dict[str, str]]:
    with open(config_path, "r") as handle:
        cfg = yaml.safe_load(handle)
    return cfg.get("mr", {}).get("hypotheses", [])


def main():
    args = parse_args()
    hypotheses = load_mr_hypotheses(args.config)
    harmonized = harmonized_records(args.harmonized)

    index = {}
    for entry in harmonized:
        index.setdefault(entry["trait"], {})[entry["ancestry"]] = entry["path"]

    rows = []
    for hypo in hypotheses:
        exposure = hypo["exposure"]
        outcome = hypo["outcome"]
        note = hypo.get("note", "")
        available_ancestries = set(index.get(exposure, {}).keys()) & set(index.get(outcome, {}).keys())
        if not available_ancestries:
            rows.append(
                {
                    "exposure": exposure,
                    "outcome": outcome,
                    "ancestry": "",
                    "exposure_path": "",
                    "outcome_path": "",
                    "note": note,
                    "status": "missing_harmonized_sumstats",
                }
            )
            continue
        for anc in sorted(available_ancestries):
            rows.append(
                {
                    "exposure": exposure,
                    "outcome": outcome,
                    "ancestry": anc,
                    "exposure_path": index[exposure][anc],
                    "outcome_path": index[outcome][anc],
                    "note": note,
                    "status": "ready",
                }
            )

    manifest = pd.DataFrame(rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Writing MR design manifest ({len(manifest)} rows) to {args.output}")
    manifest.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
