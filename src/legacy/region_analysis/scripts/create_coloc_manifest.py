#!/usr/bin/env python
import argparse
import itertools
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
    parser = argparse.ArgumentParser(description="Create coloc job manifest from multi-trait fine-mapping results.")
    parser.add_argument("--harmonized", nargs="+", required=True, help="Harmonized sumstats files.")
    parser.add_argument("--regions", required=True, help="Curated regions CSV (with parent_region column).")
    parser.add_argument("--tier1", required=False, default="", help="Tier 1 finemap table.")
    parser.add_argument("--tier2", required=False, default="", help="Tier 2 finemap table.")
    parser.add_argument("--tier3", required=False, default="results/fine_mapping/finemap_tier3_coloc.tsv", help="Tier 3 finemap table for coloc eligibility.")
    parser.add_argument("--output", required=True, help="Output TSV path.")
    return parser.parse_args()


def load_region_metadata(path: Path) -> tuple[pd.DataFrame, dict, dict]:
    df = pd.read_csv(path)
    if "parent_region" not in df.columns:
        df["parent_region"] = df["region_id"].str.split("__").str[0]
    df["parent_region"] = df["parent_region"].fillna(df["region_id"])
    df["chr"] = (
        df["chr"]
        .astype(str)
        .str.replace("^chr", "", regex=True)
        .str.replace("^CHR", "", regex=True)
    )
    df["start"] = pd.to_numeric(df["start"], errors="coerce")
    df["end"] = pd.to_numeric(df["end"], errors="coerce")
    region_to_base = df.set_index("region_id")["parent_region"].to_dict()
    base_coords = (
        df.groupby("parent_region")
        .agg({"chr": "first", "start": "min", "end": "max"})
        .rename_axis("base_region")
        .reset_index()
    )
    coord_map = base_coords.set_index("base_region").to_dict("index")
    return df, region_to_base, coord_map


def load_tier_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.warning(f"Tier table {path} missing; skipping.")
        return pd.DataFrame()
    df = pd.read_csv(path, sep="\t")
    missing = {"region_id", "trait", "ancestry"} - set(df.columns)
    if missing:
        logger.warning("Tier table %s missing columns %s; skipping.", path, ",".join(sorted(missing)))
        return pd.DataFrame()
    return df[["region_id", "trait", "ancestry"]].dropna()


def main():
    args = parse_args()
    _, region_to_base, base_coords = load_region_metadata(Path(args.regions))

    tier_frames = []
    for tier_path in filter(None, [args.tier3, args.tier1, args.tier2]):
        tier_frames.append(load_tier_table(Path(tier_path)))
    tier_frames = [df for df in tier_frames if not df.empty]
    if not tier_frames:
        logger.warning("No tier tables available; writing empty coloc manifest.")
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            columns=[
                "base_region",
                "ancestry",
                "trait_a",
                "trait_b",
                "path_a",
                "path_b",
                "chr",
                "start",
                "end",
                "pair_id",
            ]
        ).to_csv(args.output, sep="\t", index=False)
        return

    tiers = (
        pd.concat(tier_frames, ignore_index=True)
        .drop_duplicates(subset=["region_id", "trait", "ancestry"])
    )
    tiers["base_region"] = tiers["region_id"].map(region_to_base)
    tiers["base_region"] = tiers["base_region"].fillna(
        tiers["region_id"].str.split("__").str[0]
    )
    tiers = tiers.dropna(subset=["base_region", "trait", "ancestry"])

    trait_paths = {
        (rec["trait"], rec["ancestry"]): rec["path"]
        for rec in harmonized_records(args.harmonized)
    }

    manifest_rows = []
    for (base_region, ancestry), group in (
        tiers.groupby(["base_region", "ancestry"])
    ):
        unique_traits = sorted(group["trait"].unique())
        if len(unique_traits) < 2:
            continue
        coords = base_coords.get(base_region)
        if coords is None:
            logger.warning("Skipping base region %s (no coordinates).", base_region)
            continue
        for trait_a, trait_b in itertools.combinations(unique_traits, 2):
            path_a = trait_paths.get((trait_a, ancestry))
            path_b = trait_paths.get((trait_b, ancestry))
            if not path_a or not path_b:
                logger.warning(
                    "Skipping %s vs %s (%s, %s): missing harmonized file.",
                    trait_a,
                    trait_b,
                    base_region,
                    ancestry,
                )
                continue
            manifest_rows.append(
                {
                    "base_region": base_region,
                    "ancestry": ancestry,
                    "trait_a": trait_a,
                    "trait_b": trait_b,
                    "path_a": path_a,
                    "path_b": path_b,
                    "chr": coords["chr"],
                    "start": int(coords["start"]),
                    "end": int(coords["end"]),
                    "pair_id": f"{base_region}__{ancestry}__{trait_a}_vs_{trait_b}",
                }
            )

    manifest = pd.DataFrame(manifest_rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    logger.info(
        "Writing coloc manifest with %d trait pairs to %s",
        len(manifest),
        args.output,
    )
    manifest.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
