#!/usr/bin/env python
import argparse
import csv
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


def load_regions(path: Path) -> Dict[str, Dict[str, str]]:
    with path.open("r", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        raise ValueError(f"No regions found in {path}")
    regions: Dict[str, Dict[str, str]] = {}
    for row in rows:
        region_id = row["region_id"]
        regions[region_id] = {
            "chr": str(row["chr"]).replace("chr", "").replace("CHR", ""),
            "start": int(float(row["start"])),
            "end": int(float(row["end"])),
        }
    return regions


def collect_variants(
    harmonized_paths: Iterable[str],
    chrom: str,
    start: int,
    end: int,
) -> pd.DataFrame:
    chrom_clean = str(chrom)
    records = OrderedDict()
    for path in harmonized_paths:
        path_obj = Path(path)
        if not path_obj.exists():
            continue
        header = pd.read_csv(path_obj, sep="\t", nrows=0, compression="gzip")
        available = header.columns.tolist()
        usecols = ["CHR", "POS"]
        ref_missing = "REF" not in available
        alt_missing = "ALT" not in available
        snp_missing = "SNP_ID" not in available
        if not ref_missing:
            usecols.append("REF")
        if not alt_missing:
            usecols.append("ALT")
        if not snp_missing:
            usecols.append("SNP_ID")
        chunks = pd.read_csv(
            path_obj,
            sep="\t",
            usecols=usecols,
            compression="gzip",
            chunksize=500_000,
        )
        for chunk in chunks:
            if chunk.empty:
                continue
            chunk["CHR"] = (
                chunk["CHR"]
                .astype(str)
                .str.replace("^chr", "", regex=True)
                .str.replace("^CHR", "", regex=True)
            )
            chunk["POS"] = pd.to_numeric(chunk["POS"], errors="coerce")
            mask = (chunk["CHR"] == chrom_clean) & (
                (chunk["POS"] >= start) & (chunk["POS"] <= end)
            )
            if not mask.any():
                continue
            subset_cols = ["CHR", "POS"]
            if not ref_missing:
                subset_cols.append("REF")
            if not alt_missing:
                subset_cols.append("ALT")
            if not snp_missing:
                subset_cols.append("SNP_ID")
            subset = chunk.loc[mask, subset_cols].dropna(subset=["POS"])
            if subset.empty:
                continue
            subset["POS"] = subset["POS"].astype(int)
            if ref_missing:
                subset["REF"] = "N"
            if alt_missing:
                subset["ALT"] = "N"
            if "SNP_ID" not in subset.columns:
                subset["SNP_ID"] = pd.NA
            for row in subset.itertuples(index=False):
                snp_id = getattr(row, "SNP_ID", None)
                snp_id_clean = None
                if snp_id is not None and pd.notna(snp_id):
                    snp_id_str = str(snp_id).strip()
                    if snp_id_str and snp_id_str.lower() != "na":
                        snp_id_clean = snp_id_str
                ref_val = getattr(row, "REF", "N")
                alt_val = getattr(row, "ALT", "N")
                ref_clean = str(ref_val).lower()
                alt_clean = str(alt_val).lower()
                has_real_alleles = ref_clean not in {"", "n", "nan"} and alt_clean not in {"", "n", "nan"}

                if snp_id_clean:
                    key = f"SNP::{snp_id_clean}"
                else:
                    key = f"POS::{row.CHR}::{row.POS}::{ref_clean}::{alt_clean}"
                    if key in records:
                        continue

                existing = records.get(key)
                if existing is None or (
                    snp_id_clean
                    and (existing["REF"].lower() in {"", "n"} or existing["ALT"].lower() in {"", "n"})
                    and has_real_alleles
                ):
                    records[key] = {
                        "CHR": row.CHR,
                        "POS": row.POS,
                        "REF": ref_val,
                        "ALT": alt_val,
                        "SNP_ID": snp_id_clean,
                    }
    if not records:
        return pd.DataFrame(columns=["CHR", "POS", "REF", "ALT", "SNP_ID"])
    df = pd.DataFrame(list(records.values()), columns=["CHR", "POS", "REF", "ALT", "SNP_ID"])
    if df.empty:
        return df

    df["SNP_ID"] = df["SNP_ID"].fillna("").astype(str)
    df["REF"] = df["REF"].fillna("").astype(str)
    df["ALT"] = df["ALT"].fillna("").astype(str)
    ref_missing = df["REF"].str.lower().isin({"", "n", "nan"})
    alt_missing = df["ALT"].str.lower().isin({"", "n", "nan"})
    df["has_real_alleles"] = ~(ref_missing | alt_missing)
    df["has_snp"] = df["SNP_ID"].str.len() > 0
    df = df.sort_values(
        by=["has_snp", "has_real_alleles"],
        ascending=[False, False],
        kind="mergesort",
    )
    df = df.drop_duplicates(subset=["CHR", "POS", "REF", "ALT", "SNP_ID"], keep="first")
    df["pos_key"] = df["CHR"].astype(str) + ":" + df["POS"].astype(str)
    pos_with_ids = set(df.loc[df["SNP_ID"] != "", "pos_key"])
    if pos_with_ids:
        keep_mask = ~(
            (df["SNP_ID"] == "")
            & df["pos_key"].isin(pos_with_ids)
        )
        df = df.loc[keep_mask].copy()
    df["primary_key"] = df.apply(
        lambda row: row["SNP_ID"] if row["SNP_ID"] else row["pos_key"],
        axis=1,
    )
    df = df.drop_duplicates(subset=["primary_key"], keep="first")
    df = df.drop(columns=["has_real_alleles", "has_snp", "primary_key", "pos_key"])
    df = df.sort_values(["CHR", "POS"]).reset_index(drop=True)
    return df


def main():
    parser = argparse.ArgumentParser(description="Collect variant positions for a region.")
    parser.add_argument("--region-id", required=True, help="Region identifier to subset.")
    parser.add_argument("--regions-csv", required=True, help="CSV with region definitions.")
    parser.add_argument("--harmonized", nargs="+", required=True, help="Harmonized GWAS files.")
    parser.add_argument("--output", required=True, help="Output TSV path.")
    args = parser.parse_args()

    regions = load_regions(Path(args.regions_csv))
    if args.region_id not in regions:
        available = ", ".join(sorted(regions.keys()))
        raise KeyError(f"Region {args.region_id} not found. Available: {available}")
    region = regions[args.region_id]

    df = collect_variants(
        harmonized_paths=args.harmonized,
        chrom=region["chr"],
        start=region["start"],
        end=region["end"],
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep="\t", index=False)


if __name__ == "__main__":
    main()
