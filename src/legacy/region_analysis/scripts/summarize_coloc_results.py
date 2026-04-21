#!/usr/bin/env python3
"""
Summarize coloc JSON outputs into a TSV with PP.H3/PP.H4 per trait pair.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd

# Package-relative import shim: when invoked directly from the Snakemake rule
# the script's parent (region_analysis/) is not on sys.path, so
# `from scripts.utils_logging import get_logger` raises ModuleNotFoundError.
# Prepend the region_analysis/ dir so the `scripts` package resolves.
_LEGACY_REGION_DIR = Path(__file__).resolve().parent.parent
if str(_LEGACY_REGION_DIR) not in sys.path:
    sys.path.insert(0, str(_LEGACY_REGION_DIR))

from scripts.utils_logging import get_logger  # noqa: E402

logger = get_logger()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        required=True,
        help="Coloc manifest TSV produced by create_coloc_manifest.py",
    )
    parser.add_argument(
        "--coloc-dir",
        default="results/multitrait/coloc",
        help="Directory containing coloc JSON outputs.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output TSV path for the coloc summary.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Dict:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        logger.warning("Coloc JSON missing: %s", path)
    except json.JSONDecodeError as err:
        logger.warning("Invalid JSON in %s: %s", path, err)
    return {}


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    coloc_dir = Path(args.coloc_dir)

    if not manifest_path.exists():
        logger.warning("Manifest %s missing; writing empty summary.", manifest_path)
        pd.DataFrame(
            columns=[
                "pair_id",
                "base_region",
                "region",
                "ancestry",
                "trait_a",
                "trait_b",
                "PP.H3",
                "PP.H3.abf",
                "PP.H4",
                "PP.H4.abf",
                "nsnps",
                "n_common_snps",
            ]
        ).to_csv(args.output, sep="\t", index=False)
        return

    manifest = pd.read_csv(manifest_path, sep="\t")
    records: List[Dict] = []

    for _, row in manifest.iterrows():
        pair_id = row.get("pair_id")
        if not isinstance(pair_id, str):
            continue
        json_path = coloc_dir / f"{pair_id}.json"
        data = load_json(json_path)
        if not data:
            continue

        summary = data.get("summary", {}) or {}
        # Emit BOTH legacy (base_region / PP.H3 / PP.H4) and assign_tiers-
        # compatible (region / PP.H3.abf / PP.H4.abf) column names. Downstream
        # augment_coloc_summary.py reads the legacy set; assign_tiers.py reads
        # the .abf-suffixed set. Single-file aliasing avoids forking the TSV.
        base_region_val = row.get("base_region")
        pp_h3 = summary.get("PP.H3.abf") or summary.get("PP.H3")
        pp_h4 = summary.get("PP.H4.abf") or summary.get("PP.H4")
        records.append(
            {
                "pair_id": pair_id,
                "base_region": base_region_val,
                "region": base_region_val,
                "ancestry": row.get("ancestry"),
                "trait_a": row.get("trait_a"),
                "trait_b": row.get("trait_b"),
                "PP.H3": pp_h3,
                "PP.H3.abf": pp_h3,
                "PP.H4": pp_h4,
                "PP.H4.abf": pp_h4,
                "nsnps": summary.get("nsnps"),
                "n_common_snps": data.get("n_common_snps"),
                "n_merge_chrpos": data.get("n_merge_chrpos"),
                "n_a_region": (data.get("diagnostics") or {}).get("n_a_region"),
                "n_b_region": (data.get("diagnostics") or {}).get("n_b_region"),
            }
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(output_path, sep="\t", index=False)
    logger.info("Wrote coloc summary with %d rows to %s", len(records), output_path)


if __name__ == "__main__":
    main()
