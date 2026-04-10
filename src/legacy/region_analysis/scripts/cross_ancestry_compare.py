#!/usr/bin/env python3
import argparse
import csv
import itertools
import math
import subprocess
from pathlib import Path

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="Cross-ancestry finemap and coloc comparisons.")
    parser.add_argument(
        "--finemap-summary",
        default="results/fine_mapping/finemap_summary_augmented.tsv",
    )
    parser.add_argument(
        "--coloc-summary",
        default="results/multitrait/coloc_summary.tsv",
    )
    parser.add_argument(
        "--output-finemap",
        default="results/analysis/cross_ancestry_finemap_compare.tsv",
    )
    parser.add_argument(
        "--output-coloc",
        default="results/analysis/cross_ancestry_coloc_compare.tsv",
    )
    parser.add_argument(
        "--ancestries",
        nargs="*",
        default=None,
        help="Limit comparisons to these ancestries (e.g., EUR AFR).",
    )
    return parser.parse_args()


def parse_cs_median(cs_field: str):
    if not isinstance(cs_field, str) or not cs_field:
        return None
    parts = []
    for item in cs_field.split(";"):
        if ":" not in item:
            continue
        _, size = item.split(":", 1)
        try:
            parts.append(int(size))
        except ValueError:
            continue
    if not parts:
        return None
    parts.sort()
    mid = len(parts) // 2
    if len(parts) % 2 == 1:
        return parts[mid]
    return int(round((parts[mid - 1] + parts[mid]) / 2))


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


def is_rsid(value: str) -> bool:
    return isinstance(value, str) and value.startswith("rs")


def read_header(path: str):
    cmd = f"zcat -f {path} | head -n 1"
    try:
        output = subprocess.check_output(["bash", "-c", cmd], text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    if not output:
        return None
    return output.split("\t")


def build_header_index(path: str, cache):
    if path in cache:
        return cache[path]
    header = read_header(path)
    if header is None:
        cache[path] = {}
        return cache[path]
    cache[path] = {name: idx for idx, name in enumerate(header)}
    return cache[path]


def lookup_rsid(path: str, chrom: str, pos: float, header_cache, result_cache):
    if not path or not chrom or pos is None or math.isnan(pos):
        return ""
    try:
        pos_int = int(float(pos))
    except ValueError:
        return ""
    cache_key = (path, str(chrom), pos_int)
    if cache_key in result_cache:
        return result_cache[cache_key]

    header_idx = build_header_index(path, header_cache)
    snp_idx = header_idx.get("SNP_ID")
    chr_idx = header_idx.get("CHR")
    pos_idx = header_idx.get("POS")
    if snp_idx is None or chr_idx is None or pos_idx is None:
        result_cache[cache_key] = ""
        return ""

    cmd = ["tabix", path, f"{chrom}:{pos_int}-{pos_int}"]
    try:
        output = subprocess.check_output(cmd, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        result_cache[cache_key] = ""
        return ""
    rsid = ""
    for row in csv.reader(output.splitlines(), delimiter="\t"):
        if not row:
            continue
        if row[0].startswith("#"):
            continue
        if chr_idx >= len(row) or pos_idx >= len(row):
            continue
        if row[chr_idx].replace("chr", "").replace("CHR", "") != str(chrom):
            continue
        if row[pos_idx] != str(pos_int):
            continue
        if snp_idx < len(row):
            candidate = row[snp_idx]
            if is_rsid(candidate):
                rsid = candidate
            break
    result_cache[cache_key] = rsid
    return rsid


def select_best_tile(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["top_pip_num"] = pd.to_numeric(df["top_pip"], errors="coerce")
    df["n_snps_num"] = pd.to_numeric(df["n_snps"], errors="coerce").fillna(-1)
    df = df.sort_values(
        ["base_region", "trait", "ancestry", "top_pip_num", "n_snps_num", "region_id"],
        ascending=[True, True, True, False, False, True],
    )
    return df.drop_duplicates(["base_region", "trait", "ancestry"], keep="first")


def build_finemap_compare(finemap_path: str, out_path: str, ancestries=None):
    df = pd.read_csv(finemap_path, sep="\t")
    df["base_region"] = df["region_id"].astype(str).str.split("__").str[0]
    if ancestries:
        df = df[df["ancestry"].isin(ancestries)].copy()

    best = select_best_tile(df)
    best["top_snp_id"] = best.apply(lambda r: top_snp_id(r["top_chr"], r["top_pos"]), axis=1)
    header_cache = {}
    result_cache = {}
    best["top_rsid"] = best.apply(
        lambda r: lookup_rsid(
            r.get("sumstats"),
            str(r.get("top_chr")).replace("chr", "").replace("CHR", ""),
            r.get("top_pos"),
            header_cache,
            result_cache,
        ),
        axis=1,
    )
    best["cs_count"] = pd.to_numeric(best.get("n_cs"), errors="coerce")
    best["cs_size_median"] = best["credible_set_sizes"].apply(parse_cs_median)

    rows = []
    for (base_region, trait), group in best.groupby(["base_region", "trait"]):
        group = group.dropna(subset=["ancestry"])
        anc_list = sorted(group["ancestry"].unique())
        for anc_a, anc_b in itertools.combinations(anc_list, 2):
            row_a = group[group["ancestry"] == anc_a].iloc[0]
            row_b = group[group["ancestry"] == anc_b].iloc[0]

            pos_a = pd.to_numeric(row_a["top_pos"], errors="coerce")
            pos_b = pd.to_numeric(row_b["top_pos"], errors="coerce")
            distance = ""
            if not (math.isnan(pos_a) or math.isnan(pos_b)):
                distance = int(abs(pos_a - pos_b))

            same_top = bool(row_a["top_snp_id"] and row_a["top_snp_id"] == row_b["top_snp_id"])
            same_rsid = bool(row_a["top_rsid"] and row_a["top_rsid"] == row_b["top_rsid"])

            notes = [f"tile_a={row_a['region_id']}", f"tile_b={row_b['region_id']}"]
            if row_a.get("status") != "success":
                notes.append(f"status_a={row_a.get('status')}")
            if row_b.get("status") != "success":
                notes.append(f"status_b={row_b.get('status')}")
            if pd.isna(row_a.get("top_pip")):
                notes.append("top_pip_missing_a")
            if pd.isna(row_b.get("top_pip")):
                notes.append("top_pip_missing_b")
            if pd.to_numeric(row_a.get("n_snps"), errors="coerce") == 0:
                notes.append("n_snps_zero_a")
            if pd.to_numeric(row_b.get("n_snps"), errors="coerce") == 0:
                notes.append("n_snps_zero_b")
            if isinstance(row_a.get("ld_flag"), str) and "identity" in row_a.get("ld_flag"):
                notes.append("ld_identity_a")
            if isinstance(row_b.get("ld_flag"), str) and "identity" in row_b.get("ld_flag"):
                notes.append("ld_identity_b")

            rows.append(
                {
                    "base_region": base_region,
                    "trait": trait,
                    "ancestry_a": anc_a,
                    "ancestry_b": anc_b,
                    "top_snp_id_a": row_a["top_snp_id"],
                    "top_rsid_a": row_a.get("top_rsid"),
                    "top_pos_a": row_a.get("top_pos"),
                    "top_pip_a": row_a.get("top_pip"),
                    "top_snp_id_b": row_b["top_snp_id"],
                    "top_rsid_b": row_b.get("top_rsid"),
                    "top_pos_b": row_b.get("top_pos"),
                    "top_pip_b": row_b.get("top_pip"),
                    "same_top_snp": same_top,
                    "same_top_rsid": same_rsid,
                    "distance_bp": distance,
                    "cs_count_a": row_a.get("cs_count"),
                    "cs_count_b": row_b.get("cs_count"),
                    "cs_size_median_a": row_a.get("cs_size_median"),
                    "cs_size_median_b": row_b.get("cs_size_median"),
                    "ld_flag_a": row_a.get("ld_flag"),
                    "ld_flag_b": row_b.get("ld_flag"),
                    "notes": ";".join(notes),
                }
            )

    out = pd.DataFrame(rows)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, sep="\t", index=False)


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


def interpretation_bucket(eur_class, afr_class):
    if eur_class == "H4_shared" and afr_class == "H4_shared":
        return "shared_both"
    if eur_class == "H4_shared" and afr_class != "H4_shared":
        return "EUR_shared_AFR_ambiguous"
    if afr_class == "H4_shared" and eur_class != "H4_shared":
        return "AFR_shared_only"
    if eur_class == "H3_distinct" and afr_class == "H3_distinct":
        return "distinct_both"
    if "missing" in (eur_class, afr_class):
        return "missing_one"
    return "other"


def build_coloc_compare(coloc_path: str, out_path: str, ancestries=None):
    df = pd.read_csv(coloc_path, sep="\t")
    if ancestries:
        df = df[df["ancestry"].isin(ancestries)].copy()
    df["trait_pair"] = df["trait_a"].astype(str) + "_vs_" + df["trait_b"].astype(str)
    df["coloc_class"] = df.apply(lambda r: coloc_class(r["PP.H3"], r["PP.H4"]), axis=1)

    rows = []
    for (base_region, trait_pair), group in df.groupby(["base_region", "trait_pair"]):
        eur = group[group["ancestry"] == "EUR"]
        afr = group[group["ancestry"] == "AFR"]
        eur_row = eur.iloc[0] if not eur.empty else None
        afr_row = afr.iloc[0] if not afr.empty else None

        eur_class = coloc_class(eur_row["PP.H3"], eur_row["PP.H4"]) if eur_row is not None else "missing"
        afr_class = coloc_class(afr_row["PP.H3"], afr_row["PP.H4"]) if afr_row is not None else "missing"

        rows.append(
            {
                "base_region": base_region,
                "trait_pair": trait_pair,
                "EUR_class": eur_class,
                "AFR_class": afr_class,
                "EUR_PP.H4": eur_row["PP.H4"] if eur_row is not None else "",
                "AFR_PP.H4": afr_row["PP.H4"] if afr_row is not None else "",
                "interpretation": interpretation_bucket(eur_class, afr_class),
            }
        )

    out = pd.DataFrame(rows)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, sep="\t", index=False)


def main():
    args = parse_args()
    build_finemap_compare(args.finemap_summary, args.output_finemap, args.ancestries)
    build_coloc_compare(args.coloc_summary, args.output_coloc, args.ancestries)


if __name__ == "__main__":
    main()
