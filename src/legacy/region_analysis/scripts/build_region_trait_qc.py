#!/usr/bin/env python3
import argparse
import csv
import math
import subprocess
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="Build region × trait QC metrics.")
    parser.add_argument("--finemap-summary", required=True)
    parser.add_argument("--regions", required=True)
    parser.add_argument("--harmonized-dir", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def parse_overlap_fraction(raw: str) -> Optional[float]:
    if not isinstance(raw, str):
        return None
    tokens = [t.strip() for t in raw.split(";") if t.strip()]
    frac = None
    for tok in tokens[::-1]:
        try:
            val = float(tok)
        except ValueError:
            continue
        if 0 <= val <= 1:
            frac = val
            break
    return frac


def ld_flag_mode(flags: Iterable[str]) -> str:
    rank = {"ld_missing": 0, "unknown": 1, "identity": 2, "used_ld": 3}
    best = "ld_missing"
    best_rank = -1
    for flag in flags:
        f = str(flag) if flag is not None else "unknown"
        r = rank.get(f, 1)
        if r > best_rank:
            best_rank = r
            best = f
    return best


def safe_float(val: str) -> Optional[float]:
    try:
        if val is None:
            return None
        if isinstance(val, str) and val.strip() in {"", "NA", "NaN", "nan"}:
            return None
        return float(val)
    except ValueError:
        return None


def tabix_region(path: str, chrom: str, start: int, end: int) -> Tuple[int, int, List[float]]:
    cmd = ["tabix", "-h", path, f"{chrom}:{start}-{end}"]
    try:
        output = subprocess.check_output(cmd, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 0, 0, []

    reader = csv.reader(output.splitlines(), delimiter="\t")
    header = None
    n_values: List[float] = []
    n_rows = 0
    n_valid = 0
    idx_n = None
    idx_beta = None
    idx_se = None
    idx_p = None
    for row in reader:
        if not row:
            continue
        if row[0].startswith("#"):
            continue
        if header is None:
            header = row
            header_map = {name: idx for idx, name in enumerate(header)}
            for name in ("N", "N_EFF", "N_eff", "NEFF"):
                if name in header_map:
                    idx_n = header_map[name]
                    break
            idx_beta = header_map.get("BETA")
            idx_se = header_map.get("SE")
            idx_p = header_map.get("P")
            continue
        n_rows += 1
        if idx_n is not None and idx_n < len(row):
            val = safe_float(row[idx_n])
            if val is not None:
                n_values.append(val)
        beta_val = safe_float(row[idx_beta]) if idx_beta is not None and idx_beta < len(row) else None
        se_val = safe_float(row[idx_se]) if idx_se is not None and idx_se < len(row) else None
        p_val = safe_float(row[idx_p]) if idx_p is not None and idx_p < len(row) else None
        if beta_val is None or se_val is None:
            continue
        if se_val <= 0:
            continue
        if idx_p is not None and p_val is None:
            continue
        n_valid += 1
    return n_rows, n_valid, n_values


def main():
    args = parse_args()
    summary = pd.read_csv(args.finemap_summary, sep="\t")
    summary["base_region"] = summary["region_id"].astype(str).str.split("__").str[0]
    summary["ld_overlap_fraction"] = summary["ld_status_raw"].apply(parse_overlap_fraction)

    regions = pd.read_csv(args.regions)
    regions["base_region"] = regions["parent_region"]
    bounds = regions.groupby("base_region").agg(
        chrom=("chr", "first"),
        start=("start", "min"),
        end=("end", "max"),
    )

    grouped = summary.groupby(["base_region", "trait", "ancestry"], dropna=False)
    rows = []
    for (base_region, trait, ancestry), sub in grouped:
        if base_region not in bounds.index:
            continue
        chrom = str(bounds.loc[base_region, "chrom"]).replace("chr", "")
        start = int(bounds.loc[base_region, "start"])
        end = int(bounds.loc[base_region, "end"])
        region_variant_total = pd.to_numeric(sub["region_variant_total"], errors="coerce").max()
        n_snps_susie = pd.to_numeric(sub["n_snps"], errors="coerce").max()
        ld_overlap = pd.to_numeric(sub["ld_overlap_fraction"], errors="coerce").max()
        flags = sub["ld_flag"].fillna("unknown").astype(str).tolist()
        flag_mode = ld_flag_mode(flags)
        any_identity = any(flag == "identity" for flag in flags)

        sumstats_path = Path(args.harmonized_dir) / f"{trait}.{ancestry}.tsv.bgz"
        nsnps_window = 0
        nsnps_valid = 0
        n_vals: List[float] = []
        if sumstats_path.exists():
            nsnps_window, nsnps_valid, n_vals = tabix_region(str(sumstats_path), chrom, start, end)
        n_min = float(np.nanmin(n_vals)) if n_vals else math.nan
        n_median = float(np.nanmedian(n_vals)) if n_vals else math.nan
        n_max = float(np.nanmax(n_vals)) if n_vals else math.nan

        rows.append(
            {
                "base_region": base_region,
                "trait": trait,
                "ancestry": ancestry,
                "chr": chrom,
                "start": start,
                "end": end,
                "sumstats_path": str(sumstats_path),
                "n_variants_window": region_variant_total,
                "n_snps_susie": n_snps_susie,
                "ld_overlap_fraction": ld_overlap,
                "ld_flag_mode": flag_mode,
                "ld_flag_any_identity": any_identity,
                "nsnps_window": nsnps_window,
                "nsnps_coloc_input": nsnps_valid,
                "N_min": n_min,
                "N_median": n_median,
                "N_max": n_max,
            }
        )

    out = pd.DataFrame(rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
