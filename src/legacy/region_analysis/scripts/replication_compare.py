#!/usr/bin/env python3
import argparse
import math
import subprocess
from pathlib import Path

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="Compare baseline vs alternate datasets.")
    parser.add_argument(
        "--baseline-finemap",
        default="results/fine_mapping/finemap_summary_augmented.tsv",
    )
    parser.add_argument("--alt-finemap", required=True)
    parser.add_argument(
        "--baseline-coloc",
        default="results/multitrait/coloc_summary.tsv",
    )
    parser.add_argument("--alt-coloc", required=True)
    parser.add_argument(
        "--anchors",
        default="bmi:t2d:EUR,stroke:t2d:AFR",
        help="Comma-separated anchors trait_a:trait_b:ancestry.",
    )
    parser.add_argument(
        "--base-regions",
        default="",
        help="Optional comma-separated base regions to restrict.",
    )
    parser.add_argument(
        "--output-finemap",
        default="results/analysis/replication_finemap_compare.tsv",
    )
    parser.add_argument(
        "--output-coloc",
        default="results/analysis/replication_coloc_compare.tsv",
    )
    parser.add_argument(
        "--ld-dir",
        default="data_processed/ld_reference",
        help="LD directory containing ancestry/region_id.rds files.",
    )
    parser.add_argument(
        "--r2-script",
        default="scripts/compute_ld_r2.R",
        help="R script to compute LD r2 from an RDS file.",
    )
    return parser.parse_args()


def parse_anchors(anchor_str: str):
    anchors = []
    for item in anchor_str.split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid anchor '{item}'. Expected trait_a:trait_b:ancestry")
        anchors.append((parts[0], parts[1], parts[2]))
    return anchors


def parse_cs_median(cs_field: str):
    if not isinstance(cs_field, str) or not cs_field:
        return None
    sizes = []
    for chunk in cs_field.split(";"):
        if ":" not in chunk:
            continue
        _, size = chunk.split(":", 1)
        try:
            sizes.append(int(size))
        except ValueError:
            continue
    if not sizes:
        return None
    sizes.sort()
    mid = len(sizes) // 2
    if len(sizes) % 2 == 1:
        return sizes[mid]
    return int(round((sizes[mid - 1] + sizes[mid]) / 2))


def top_snp_id(chrom, pos):
    if pd.isna(chrom) or pd.isna(pos):
        return ""
    try:
        pos_int = int(float(pos))
    except ValueError:
        return ""
    chrom_str = str(chrom)
    chrom_str = chrom_str.replace("chr", "").replace("CHR", "")
    return f"{chrom_str}:{pos_int}"


def compute_ld_r2(rscript: str, rds_path: str, snp_a: str, snp_b: str) -> float:
    if not rds_path or not snp_a or not snp_b:
        return math.nan
    try:
        output = subprocess.check_output(
            ["Rscript", rscript, "--rds", rds_path, "--snp-a", snp_a, "--snp-b", snp_b],
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return math.nan
    try:
        return float(output)
    except ValueError:
        return math.nan


def resolve_ld_rds(ld_dir: str, ancestry: str, region_a: str, region_b: str) -> str:
    if not ancestry:
        return ""
    base = Path(ld_dir) / ancestry
    for region in (region_a, region_b):
        if not region:
            continue
        candidate = base / f"{region}.rds"
        if candidate.exists():
            return str(candidate)
    return ""


def select_best_tile(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["top_pip_num"] = pd.to_numeric(df["top_pip"], errors="coerce")
    df["n_snps_num"] = pd.to_numeric(df["n_snps"], errors="coerce").fillna(-1)
    df = df.sort_values(
        ["base_region", "trait", "ancestry", "top_pip_num", "n_snps_num", "region_id"],
        ascending=[True, True, True, False, False, True],
    )
    return df.drop_duplicates(["base_region", "trait", "ancestry"], keep="first")


def build_finemap_compare(baseline: pd.DataFrame, alt: pd.DataFrame, anchors, base_regions, ld_dir, r2_script):
    baseline = baseline.copy()
    alt = alt.copy()
    baseline["base_region"] = baseline["region_id"].astype(str).str.split("__").str[0]
    alt["base_region"] = alt["region_id"].astype(str).str.split("__").str[0]

    if base_regions:
        baseline = baseline[baseline["base_region"].isin(base_regions)].copy()
        alt = alt[alt["base_region"].isin(base_regions)].copy()

    baseline = select_best_tile(baseline)
    alt = select_best_tile(alt)
    baseline["top_snp_id"] = baseline.apply(lambda r: top_snp_id(r["top_chr"], r["top_pos"]), axis=1)
    alt["top_snp_id"] = alt.apply(lambda r: top_snp_id(r["top_chr"], r["top_pos"]), axis=1)
    baseline["cs_size_median"] = baseline["credible_set_sizes"].apply(parse_cs_median)
    alt["cs_size_median"] = alt["credible_set_sizes"].apply(parse_cs_median)

    rows = []
    for trait_a, trait_b, ancestry in anchors:
        for trait in (trait_a, trait_b):
            base_sub = baseline[(baseline["trait"] == trait) & (baseline["ancestry"] == ancestry)]
            alt_sub = alt[(alt["trait"] == trait) & (alt["ancestry"] == ancestry)]
            if base_sub.empty or alt_sub.empty:
                continue
            merged = base_sub.merge(
                alt_sub,
                on=["base_region", "trait", "ancestry"],
                suffixes=("_base", "_alt"),
            )
            for _, row in merged.iterrows():
                pos_a = pd.to_numeric(row["top_pos_base"], errors="coerce")
                pos_b = pd.to_numeric(row["top_pos_alt"], errors="coerce")
                distance = ""
                if not (math.isnan(pos_a) or math.isnan(pos_b)):
                    distance = int(abs(pos_a - pos_b))
                same_top = bool(row["top_snp_id_base"] and row["top_snp_id_base"] == row["top_snp_id_alt"])
                same_tile = row["region_id_base"] == row["region_id_alt"]
                notes = []
                if row.get("status_base") != "success":
                    notes.append(f"status_base={row.get('status_base')}")
                if row.get("status_alt") != "success":
                    notes.append(f"status_alt={row.get('status_alt')}")
                if same_tile:
                    notes.append("same_tile")
                ld_rds = resolve_ld_rds(ld_dir, ancestry, row["region_id_base"], row["region_id_alt"])
                ld_r2 = compute_ld_r2(r2_script, ld_rds, row["top_snp_id_base"], row["top_snp_id_alt"])
                if math.isnan(ld_r2):
                    ld_signal = "missing"
                elif ld_r2 >= 0.8:
                    ld_signal = "same_ld_signal"
                elif ld_r2 < 0.2:
                    ld_signal = "different_ld_signal"
                else:
                    ld_signal = "intermediate"

                rows.append(
                    {
                        "base_region": row["base_region"],
                        "trait": trait,
                        "ancestry": ancestry,
                        "top_snp_id_base": row["top_snp_id_base"],
                        "top_pos_base": row["top_pos_base"],
                        "top_pip_base": row["top_pip_base"],
                        "top_snp_id_alt": row["top_snp_id_alt"],
                        "top_pos_alt": row["top_pos_alt"],
                        "top_pip_alt": row["top_pip_alt"],
                        "same_top_snp": same_top,
                        "distance_bp": distance,
                        "cs_count_base": row.get("n_cs_base"),
                        "cs_count_alt": row.get("n_cs_alt"),
                        "cs_size_median_base": row.get("cs_size_median_base"),
                        "cs_size_median_alt": row.get("cs_size_median_alt"),
                        "ld_flag_base": row.get("ld_flag_base"),
                        "ld_flag_alt": row.get("ld_flag_alt"),
                        "ld_r2": ld_r2,
                        "ld_signal": ld_signal,
                        "ld_rds_path": ld_rds,
                        "notes": ";".join(notes),
                    }
                )

    return pd.DataFrame(rows)


def coloc_class(pp_h3, pp_h4):
    try:
        h3 = float(pp_h3)
    except (TypeError, ValueError):
        h3 = float("nan")
    try:
        h4 = float(pp_h4)
    except (TypeError, ValueError):
        h4 = float("nan")
    if not math.isnan(h4) and h4 >= 0.8:
        return "H4_shared"
    if not math.isnan(h3) and h3 >= 0.8 and (math.isnan(h4) or h4 < 0.5):
        return "H3_distinct"
    if math.isnan(h3) and math.isnan(h4):
        return "missing"
    return "ambiguous"


def build_coloc_compare(base: pd.DataFrame, alt: pd.DataFrame, anchors, base_regions):
    for df in (base, alt):
        df["trait_pair"] = df.apply(
            lambda r: "_vs_".join(sorted([str(r["trait_a"]), str(r["trait_b"])])), axis=1
        )
        df["coloc_class"] = df.apply(lambda r: coloc_class(r["PP.H3"], r["PP.H4"]), axis=1)

    if base_regions:
        base = base[base["base_region"].isin(base_regions)].copy()
        alt = alt[alt["base_region"].isin(base_regions)].copy()

    rows = []
    for trait_a, trait_b, ancestry in anchors:
        pair = "_vs_".join(sorted([trait_a, trait_b]))
        base_sub = base[(base["ancestry"] == ancestry) & (base["trait_pair"] == pair)]
        alt_sub = alt[(alt["ancestry"] == ancestry) & (alt["trait_pair"] == pair)]
        if base_sub.empty or alt_sub.empty:
            continue
        merged = base_sub.merge(
            alt_sub,
            on=["base_region", "ancestry", "trait_pair"],
            suffixes=("_base", "_alt"),
        )
        for _, row in merged.iterrows():
            rows.append(
                {
                    "base_region": row["base_region"],
                    "trait_pair": pair,
                    "ancestry": ancestry,
                    "base_class": row["coloc_class_base"],
                    "alt_class": row["coloc_class_alt"],
                    "base_PP.H4": row.get("PP.H4_base"),
                    "alt_PP.H4": row.get("PP.H4_alt"),
                    "stable_H4": row["coloc_class_base"] == "H4_shared"
                    and row["coloc_class_alt"] == "H4_shared",
                    "class_changed": row["coloc_class_base"] != row["coloc_class_alt"],
                }
            )

    return pd.DataFrame(rows)


def main():
    args = parse_args()
    anchors = parse_anchors(args.anchors)
    base_regions = [r.strip() for r in args.base_regions.split(",") if r.strip()]

    base_fm = pd.read_csv(args.baseline_finemap, sep="\t")
    alt_fm = pd.read_csv(args.alt_finemap, sep="\t")
    finemap_out = build_finemap_compare(
        base_fm,
        alt_fm,
        anchors,
        base_regions,
        args.ld_dir,
        args.r2_script,
    )
    Path(args.output_finemap).parent.mkdir(parents=True, exist_ok=True)
    finemap_out.to_csv(args.output_finemap, sep="\t", index=False)

    base_coloc = pd.read_csv(args.baseline_coloc, sep="\t")
    alt_coloc = pd.read_csv(args.alt_coloc, sep="\t")
    coloc_out = build_coloc_compare(base_coloc, alt_coloc, anchors, base_regions)
    Path(args.output_coloc).parent.mkdir(parents=True, exist_ok=True)
    coloc_out.to_csv(args.output_coloc, sep="\t", index=False)


if __name__ == "__main__":
    main()
