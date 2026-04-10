#!/usr/bin/env python
import argparse
import gzip
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd
import math

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.dataset_config import dataset_descriptor
from scripts.utils_logging import get_logger

logger = get_logger()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--trait", required=True)
    parser.add_argument("--ancestry", required=True)
    parser.add_argument("--build", required=True)
    parser.add_argument("--dataset-name", required=False, default=None)
    parser.add_argument(
        "--datasets-config",
        required=False,
        default="config/datasets.yaml",
    )
    return parser.parse_args()


def to_rename_pairs(column_map: Dict[str, Any], columns: List[str]) -> Dict[str, str]:
    rename_pairs: Dict[str, str] = {}
    lookup = {col.lower(): col for col in columns}
    for target, source in column_map.items():
        candidates = source if isinstance(source, (list, tuple)) else [source]
        for candidate in candidates:
            if not candidate:
                continue
            match = lookup.get(str(candidate).lower())
            if match:
                rename_pairs[match] = target
                break
    return rename_pairs


def find_column(columns: List[str], candidates: List[str]) -> Optional[str]:
    normalized = [c.lower() for c in candidates]
    for col in columns:
        if col.lower() in normalized:
            return col
    return None


def normalize_chrom(value: Any) -> str:
    return str(value).replace("chr", "").replace("CHR", "")


def load_rsid_positions(
    vcf_path: Path, target_ids: Set[str]
) -> Dict[str, Tuple[str, int, str, str]]:
    mapping: Dict[str, Tuple[str, int, str, str]] = {}
    if not vcf_path.exists():
        logger.warning("RSID mapping skipped; VCF %s missing", vcf_path)
        return mapping

    logger.info(
        "Building rsID mapping from %s for %d IDs",
        vcf_path,
        len(target_ids),
    )
    with gzip.open(vcf_path, "rt") as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) < 5:
                continue
            pos = int(fields[1])
            chrom = normalize_chrom(fields[0])
            ref = fields[3]
            alt = fields[4].split(",")[0]
            ids = [tok.strip() for tok in fields[2].split(";")]
            for rsid in ids:
                if rsid in target_ids and rsid not in mapping:
                    mapping[rsid] = (chrom, pos, ref, alt)
                    if len(mapping) == len(target_ids):
                        return mapping
    return mapping


def parse_ci_interval(text: Any) -> Tuple[Optional[float], Optional[float]]:
    if pd.isna(text):
        return (None, None)
    tokens = re.findall(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", str(text))
    if len(tokens) >= 2:
        try:
            low = float(tokens[0])
            high = float(tokens[1])
            return (low, high)
        except ValueError:
            return (None, None)
    return (None, None)


def parse_african_counts(text: Any) -> Tuple[Optional[int], Optional[int]]:
    if pd.isna(text):
        return (None, None)
    expr = str(text)
    cases_match = re.search(
        r"([\d,]+)\s+African(?:\s+American)?\s+cases", expr, flags=re.IGNORECASE
    )
    ctrls_match = re.search(
        r"([\d,]+)\s+African(?:\s+American)?\s+controls", expr, flags=re.IGNORECASE
    )
    cases = int(cases_match.group(1).replace(",", "")) if cases_match else None
    ctrls = int(ctrls_match.group(1).replace(",", "")) if ctrls_match else None
    return (cases, ctrls)


def main():
    args = parse_args()
    meta = dataset_descriptor(
        trait=args.trait,
        ancestry=args.ancestry,
        config_path=args.datasets_config,
        dataset_name=args.dataset_name,
    )

    sep = meta.get("sep", "\t")
    compression = meta.get("compression")
    delim_ws = bool(meta.get("delim_whitespace", False))
    if compression in (None, "", "none", "None"):
        compression = None

    read_kwargs: Dict[str, Any] = {"compression": compression} if compression else {}
    if delim_ws:
        read_kwargs["sep"] = r"\s+"
        read_kwargs["engine"] = "python"
    else:
        read_kwargs["sep"] = sep

    sep_desc = "delim_whitespace=True" if delim_ws else f"sep='{sep}'"
    logger.info(
        f"Reading {args.input} with {sep_desc} compression='{compression}' "
        f"(dataset={meta['dataset']})"
    )
    df = pd.read_csv(args.input, **read_kwargs)

    rename_pairs = to_rename_pairs(meta.get("column_map", {}), df.columns.tolist())
    if rename_pairs:
        logger.info(f"Applying rename map: {rename_pairs}")
        df = df.rename(columns=rename_pairs)

    dataset_name = meta["dataset"]

    n_col_present = "N" in df.columns
    if n_col_present:
        df["N"] = pd.to_numeric(df["N"], errors="coerce")
    else:
        n_case_col = find_column(df.columns.tolist(), ["N_CASE", "NCASES", "CASE_N"])
        n_ctrl_col = find_column(df.columns.tolist(), ["N_CTRL", "NCONTROLS", "CONTROL_N"])
        if n_case_col and n_ctrl_col:
            logger.info("Deriving N from %s + %s", n_case_col, n_ctrl_col)
            df["N"] = (
                pd.to_numeric(df[n_case_col], errors="coerce")
                + pd.to_numeric(df[n_ctrl_col], errors="coerce")
            )
        elif meta.get("sample_size"):
            sample_size = float(meta["sample_size"])
            logger.info("Filling constant sample size N=%s", sample_size)
            df["N"] = sample_size

    if "N" in df.columns and df["N"].notna().any():
        df["N"] = pd.to_numeric(df["N"], errors="coerce")
    elif "N" in df.columns:
        # Drop empty column if creation failed
        df = df.drop(columns=["N"])

    if "P" not in df.columns and {"BETA", "SE"}.issubset(df.columns):
        logger.info("Deriving P from BETA/SE")
        beta_vals = pd.to_numeric(df["BETA"], errors="coerce")
        se_vals = pd.to_numeric(df["SE"], errors="coerce")
        with np.errstate(divide="ignore", invalid="ignore"):
            z = beta_vals / se_vals
        z = z.replace([np.inf, -np.inf], np.nan)
        z_abs = np.abs(z.to_numpy())
        if hasattr(np, "erfc"):
            p_vals = np.erfc(z_abs / np.sqrt(2.0))
        else:
            p_vals = np.vectorize(lambda v: math.erfc(v / math.sqrt(2.0)))(z_abs)
        df["P"] = p_vals

    # Handle MarkerName columns such as "10:100000625:SNP" when POS (and possibly CHR) missing.
    marker_source = None
    if "MarkerName" in df.columns and "POS" not in df.columns:
        marker_source = "MarkerName"
    elif (
        "POS" not in df.columns
        and "CHR" in df.columns
        and df["CHR"].astype(str).str.contains(":").any()
    ):
        marker_source = "CHR"

    if marker_source:
        logger.info(f"Deriving CHR/POS from {marker_source} column")
        marker_parts = df[marker_source].astype(str).str.split(":", n=2, expand=True)
        df["CHR"] = marker_parts[0].str.replace("^chr", "", regex=True)
        df["POS"] = pd.to_numeric(marker_parts[1], errors="coerce")

    # Special handling for certain datasets (e.g., AFR stroke catalog download).
    if dataset_name == "megastroke_metastroke" and args.ancestry.upper() == "AFR":
        logger.info("Applying AFR stroke transformations (OR handling, CI parsing, N derivation)")
        if "BETA" in df.columns:
            beta_series = pd.to_numeric(df["BETA"], errors="coerce")
            has_negative = (beta_series < 0).any()
            if has_negative:
                # Treat as already log-scale; do not transform.
                logger.info(
                    "AFR stroke BETA contains negative values; skipping OR->log transform"
                )
                df["BETA"] = beta_series
            else:
                logger.info("AFR stroke BETA appears positive-only; applying log transform")
                mask = beta_series > 0
                df["BETA"] = pd.NA
                df.loc[mask, "BETA"] = np.log(beta_series[mask])
        if "SE" not in df.columns or df["SE"].isna().all():
            ci_series = df.get("CI_TEXT")
            if ci_series is not None:
                bounds = ci_series.apply(parse_ci_interval)
                lowers = bounds.apply(lambda x: x[0] if x else None)
                uppers = bounds.apply(lambda x: x[1] if x else None)
                lowers = pd.to_numeric(lowers, errors="coerce")
                uppers = pd.to_numeric(uppers, errors="coerce")
                valid = (~lowers.isna()) & (~uppers.isna()) & (lowers > 0) & (uppers > 0)
                se_vals = pd.Series(np.nan, index=df.index)
                se_vals[valid] = (np.log(uppers[valid]) - np.log(lowers[valid])) / (2 * 1.96)
                df["SE"] = se_vals
        if "INITIAL_SAMPLE" in df.columns and len(df) > 0:
            parsed_counts = df["INITIAL_SAMPLE"].apply(parse_african_counts)
            case_vals = [entry[0] for entry in parsed_counts]
            ctrl_vals = [entry[1] for entry in parsed_counts]
            df["N_CASE"] = pd.Series(case_vals, index=df.index, dtype="float")
            df["N_CTRL"] = pd.Series(ctrl_vals, index=df.index, dtype="float")
            if "N" not in df.columns:
                df["N"] = df["N_CASE"].fillna(0) + df["N_CTRL"].fillna(0)
        if "RISK_ALLELE" in df.columns and "ALT" not in df.columns:
            alleles = (
                df["RISK_ALLELE"]
                .astype(str)
                .str.extract(r"[-/]([ACGT]+)$", expand=False)
                .str.upper()
            )
            df["ALT"] = alleles
        if "REF" not in df.columns:
            df["REF"] = pd.NA

    mandatory = ["CHR", "POS"]
    missing = [col for col in mandatory if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns {missing} after harmonization step for "
            f"trait={args.trait}, ancestry={args.ancestry}"
        )

    snp_candidates = meta.get("snp_id_columns") or [
        "SNP_ID",
        "SNP",
        "RSID",
        "RS_ID",
        "MarkerName",
        "MARKERNAME",
        "ID",
        "VariantID",
    ]
    snp_col = find_column(df.columns.tolist(), snp_candidates)
    if snp_col:
        logger.info("Adding SNP_ID column from %s", snp_col)
        snp_series = df[snp_col].astype(str).str.strip()
        snp_series = snp_series.replace(
            {"": pd.NA, "nan": pd.NA, "NaN": pd.NA, "NA": pd.NA}
        )
        df["SNP_ID"] = snp_series
    elif {"CHR", "POS"}.issubset(df.columns):
        logger.info(
            "Synthesizing SNP_ID as chr:pos because no explicit rsID column was found"
        )
        chr_series = (
            df["CHR"]
            .astype(str)
            .str.replace("^chr", "", regex=True)
            .str.replace("^CHR", "", regex=True)
        )
        pos_series = pd.to_numeric(df["POS"], errors="coerce")
        synthetic = pd.Series(pd.NA, index=df.index, dtype="object")
        valid = (~chr_series.isna()) & (~pos_series.isna())
        if valid.any():
            rounded_pos = pos_series.loc[valid].round().astype(int).astype(str)
            cleaned_chr = chr_series.loc[valid]
            synthetic.loc[valid] = cleaned_chr + ":" + rounded_pos
        df["SNP_ID"] = synthetic

    keep_cols = [
        col for col in
        ["CHR", "POS", "REF", "ALT", "BETA", "SE", "P", "EAF", "N", "SNP_ID"]
        if col in df.columns
    ]
    harmonized = df[keep_cols].copy()
    if "CHR" in harmonized.columns:
        harmonized["CHR"] = harmonized["CHR"].astype(str)
    if "POS" in harmonized.columns:
        harmonized["POS"] = pd.to_numeric(harmonized["POS"], errors="coerce")
        harmonized = harmonized.sort_values(by=["CHR", "POS"])
    harmonized["TRAIT"] = args.trait
    harmonized["ANCESTRY"] = args.ancestry
    harmonized["BUILD"] = args.build

    rsid_map_cfg = meta.get("rsid_map") or {}
    rsid_template = rsid_map_cfg.get("template")
    if rsid_template and "SNP_ID" in harmonized.columns:
        snp_preview = harmonized["SNP_ID"].dropna().astype(str)
        if not snp_preview.empty:
            colon_fraction = snp_preview.str.contains(":", regex=False).mean()
            if colon_fraction > 0.5:
                logger.info(
                    "Skipping rsID remap for %s because SNP_ID values look like chr:pos placeholders",
                    dataset_name,
                )
                rsid_template = None

        if rsid_template:
            chrom_whitelist = rsid_map_cfg.get("chromosomes")
            harmonized["CHR"] = harmonized["CHR"].astype(str).str.replace("^chr", "", regex=True).str.replace("^CHR", "", regex=True)
            harmonized["SNP_ID"] = harmonized["SNP_ID"].astype(str)
            unique_chroms = sorted(harmonized["CHR"].unique())
            if chrom_whitelist:
                chrom_whitelist = {normalize_chrom(ch) for ch in chrom_whitelist}
                target_chroms = [ch for ch in unique_chroms if ch in chrom_whitelist]
            else:
                target_chroms = unique_chroms

            total_updates = 0
            for chrom in target_chroms:
                mask = harmonized["CHR"] == chrom
                snp_ids = set(
                    harmonized.loc[mask & harmonized["SNP_ID"].notna(), "SNP_ID"].unique()
                )
                if not snp_ids:
                    continue
                vcf_path = Path(rsid_template.format(chrom=chrom))
                mapping = load_rsid_positions(vcf_path, snp_ids)
                if not mapping:
                    logger.warning("No rsID mapping found for chromosome %s", chrom)
                    continue
                mapped_series = harmonized.loc[mask, "SNP_ID"].map(mapping)
                update_mask = mapped_series.notna()
                if not update_mask.any():
                    continue
                update_idx = mapped_series.index[update_mask]
                tuple_series = mapped_series[update_mask]
                new_pos = tuple_series.map(lambda x: x[1]).astype(int).to_numpy()
                new_chr = tuple_series.map(lambda x: x[0]).astype(str).to_numpy()
                harmonized.loc[update_idx, "POS"] = new_pos
                harmonized.loc[update_idx, "CHR"] = new_chr
                if "REF" in harmonized.columns:
                    ref_values = tuple_series.map(lambda x: x[2]).astype(str)
                    existing_ref = harmonized.loc[update_idx, "REF"]
                    ref_mask = existing_ref.isna() | (existing_ref.astype(str).str.strip() == "")
                    ref_fill_idx = existing_ref.index[ref_mask]
                    harmonized.loc[ref_fill_idx, "REF"] = ref_values.loc[ref_fill_idx]
                if "ALT" in harmonized.columns:
                    alt_values = tuple_series.map(lambda x: x[3]).astype(str)
                    existing_alt = harmonized.loc[update_idx, "ALT"]
                    alt_mask = existing_alt.isna() | (existing_alt.astype(str).str.strip() == "")
                    alt_fill_idx = existing_alt.index[alt_mask]
                    harmonized.loc[alt_fill_idx, "ALT"] = alt_values.loc[alt_fill_idx]
                total_updates += len(update_idx)
            if total_updates:
                logger.info("Updated CHR/POS for %d variants using rsID mapping", total_updates)

    logger.info(f"Writing harmonized output to {args.output}")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    harmonized.to_csv(output_path, sep="\t", index=False)


if __name__ == "__main__":
    main()
