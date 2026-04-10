#!/usr/bin/env python
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.manifest_utils import parse_trait_ancestry
from scripts.utils_logging import get_logger

logger = get_logger()


def summarize_file(path: Path, max_rows: int | None = None) -> dict:
    read_kwargs = dict(sep="\t", compression="gzip")
    if max_rows:
        read_kwargs["nrows"] = max_rows
    df = pd.read_csv(path, **read_kwargs)
    for col in ["POS", "BETA", "SE", "P", "EAF", "N"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    trait, ancestry = parse_trait_ancestry(path.name)
    summary = {
        "trait": trait,
        "ancestry": ancestry,
        "path": str(path),
        "rows": int(df.shape[0]),
        "nchr": int(df["CHR"].nunique()) if "CHR" in df else 0,
        "missing_beta": int(df["BETA"].isna().sum()) if "BETA" in df else df.shape[0],
        "missing_se": int(df["SE"].isna().sum()) if "SE" in df else df.shape[0],
        "missing_p": int(df["P"].isna().sum()) if "P" in df else df.shape[0],
        "eaf_min": float(df["EAF"].min()) if "EAF" in df else None,
        "eaf_max": float(df["EAF"].max()) if "EAF" in df else None,
        "beta_mean": float(df["BETA"].mean()) if "BETA" in df else None,
        "beta_sd": float(df["BETA"].std()) if "BETA" in df else None,
        "se_median": float(df["SE"].median()) if "SE" in df else None,
        "p_min": float(df["P"].min()) if "P" in df else None,
    }
    return summary


def main():
    parser = argparse.ArgumentParser(description="Summarize harmonized summary statistics.")
    parser.add_argument("--harmonized", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-rows", type=int, default=None, help="Limit rows read per file (for speed).")
    parser.add_argument("--json-log", default=None, help="Optional JSON file for structured summaries.")
    args = parser.parse_args()

    summaries = []
    for path_str in args.harmonized:
        path = Path(path_str)
        if not path.exists():
            logger.warning(f"Missing harmonized file: {path}")
            continue
        logger.info(f"Summarizing {path}")
        summaries.append(summarize_file(path, args.max_rows))

    df = pd.DataFrame(summaries)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, sep="\t", index=False)
    logger.info(f"Wrote harmonized QC table to {args.output}")

    if args.json_log:
        with open(args.json_log, "w") as handle:
            json.dump(summaries, handle, indent=2)


if __name__ == "__main__":
    main()
