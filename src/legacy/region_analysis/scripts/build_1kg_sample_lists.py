#!/usr/bin/env python
import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.utils_logging import get_logger

logger = get_logger()


def parse_args():
    parser = argparse.ArgumentParser(description="Generate ancestry-specific KEEP files for 1000G samples.")
    parser.add_argument("--panel", required=True, help="Path to integrated_call_samples panel file.")
    parser.add_argument("--config", default="config/config.yaml", help="YAML config with onekg.populations mapping.")
    parser.add_argument("--output-dir", default="data_raw/1kg", help="Directory to write <ANCESTRY>.samples files.")
    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.config, "r") as handle:
        cfg = yaml.safe_load(handle)

    pop_map = cfg.get("onekg", {}).get("populations")
    if not pop_map:
        raise ValueError("Config missing onekg.populations block")

    panel = pd.read_csv(args.panel, sep="\t")
    if not {"sample", "super_pop", "pop"}.issubset(panel.columns):
        raise ValueError("Panel file missing required columns: sample, super_pop, pop")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for ancestry, pops in pop_map.items():
        matched = panel[panel["pop"].isin(pops)]
        if matched.empty:
            logger.warning(f"No panel entries found for ancestry {ancestry} with pops {pops}")
        keep_path = output_dir / f"{ancestry}.samples"
        matched[["sample", "sample"]].to_csv(keep_path, sep="\t", index=False, header=False)
        logger.info(f"Wrote {matched.shape[0]} samples to {keep_path}")


if __name__ == "__main__":
    main()
