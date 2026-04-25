#!/usr/bin/env python3
"""MAGIC 2021 HbA1c harmonizer (6 ancestries: TRANS / EUR / AFR / EAS / SAS / HIS).

The MAGIC 1000G release includes explicit ``chromosome`` +
``base_pair_location`` columns alongside the rsid SNP key. The harmonizer
therefore prefers file-side CHR/BP and only falls back to the
``sumstats_utils.build_rsid_to_chrpos`` forward crosswalk when those
columns are absent (legacy releases or future schema drift).

Two MAGIC schema variants observed:

* **Per-ancestry single-trait** (EUR / AFR / EAS / SAS / HIS):
  ``variant chromosome base_pair_location effect_allele other_allele
   effect_allele_frequency beta standard_error p_value sample_size``
* **Trans-ancestry Bayes-factor meta** (TRANS):
  ``variant chromosome base_pair_location effect_allele other_allele
   log10BF sample_size het_p_value``

The TRANS variant has no BETA/SE/P columns; the harmonizer emits
canonical-shape rows with BETA/SE/P = NaN and records
``phenotype_lock = "log10BF only — no per-variant SE/P"`` in the QC
sidecar. Downstream LDSC / MTAG won't munge this file (no `Z` available);
its primary consumer is CPASSOC and HyPrColoc, both of which can read
log10BF directly.

Plan reference: m1-02a-harmonizers-continuous-traits-PLAN.md Task 2.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import sumstats_utils as _su  # noqa: E402

CANONICAL_COLS = _su.CANONICAL_COLS

# Per-ancestry single-trait column map.
MAGIC_PERANC_COLS = {
    "variant": "SNP",
    "chromosome": "CHR",
    "base_pair_location": "BP",
    "effect_allele": "EA",
    "other_allele": "OA",
    "effect_allele_frequency": "EAF",
    "beta": "BETA",
    "standard_error": "SE",
    "p_value": "P",
    "sample_size": "N",
}

# Trans-ancestry Bayes-factor variant — no BETA / SE / P columns.
MAGIC_TRANS_COLS = {
    "variant": "SNP",
    "chromosome": "CHR",
    "base_pair_location": "BP",
    "effect_allele": "EA",
    "other_allele": "OA",
    "sample_size": "N",
}


def _detect_magic_variant(df: pd.DataFrame) -> str:
    if {"beta", "standard_error", "p_value"}.issubset(df.columns):
        return "peranc"
    if "log10BF" in df.columns:
        return "trans_bayes_factor"
    raise ValueError(
        f"MAGIC harmonizer: cannot detect per-ancestry vs TRANS BF schema. "
        f"Found columns: {sorted(df.columns.tolist())}."
    )


def _b2_guard(df: pd.DataFrame, col_map: dict, source: str) -> pd.DataFrame:
    missing = [src for src in col_map if src not in df.columns]
    if missing:
        raise ValueError(
            f"{source} harmonizer: expected columns "
            f"{sorted(col_map.keys())} but file is missing {missing}. "
            f"Found columns: {sorted(df.columns.tolist())}."
        )
    return df[list(col_map.keys())].rename(columns=col_map)


def _emit_dual_artifacts(df: pd.DataFrame, output_tsvgz: Path,
                         parquet_path: Path) -> None:
    output_tsvgz.parent.mkdir(parents=True, exist_ok=True)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_tsvgz, sep="\t", index=False, compression="gzip")
    df.to_parquet(parquet_path, index=False, compression="snappy")


def _coerce_canonical_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in ("BP", "BETA", "SE", "P", "EAF", "N"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ("EA", "OA", "SNP", "CHR"):
        if c in df.columns:
            df[c] = df[c].astype(str)
    return df


def _fill_missing_chr_bp_via_crosswalk(
    df: pd.DataFrame,
    bim_prefix: str,
    chromosomes: list[int] | None,
    qc: dict,
) -> pd.DataFrame:
    """For rows lacking CHR/BP, fill via build_rsid_to_chrpos."""
    lookup = _su.build_rsid_to_chrpos(bim_prefix, chromosomes=chromosomes)
    qc["bim_prefix"] = bim_prefix
    qc["bim_lookup_size"] = len(lookup)

    pairs = df["SNP"].map(lookup)
    mapped = pairs.notna()
    qc["n_unmapped_rsid"] = int((~mapped).sum())

    df_out = df.loc[mapped].copy().reset_index(drop=True)
    chr_bp = pairs.dropna().reset_index(drop=True)
    df_out["CHR"] = [str(p[0]) for p in chr_bp]
    df_out["BP"] = [int(p[1]) for p in chr_bp]
    return df_out


def harmonize_magic(
    input_path: Path,
    output_tsvgz: Path,
    parquet_path: Path,
    qc_json_path: Path,
    ancestry: str,
    *,
    bim_prefix: str | None = None,
    bim_chromosomes: list[int] | None = None,
    maf_min: float = 0.005,
    consortium: str = "MAGIC",
    year: int = 2021,
) -> dict:
    if ancestry not in {"TRANS", "EUR", "AFR", "EAS", "SAS", "HIS"}:
        raise ValueError(
            f"MAGIC ancestry '{ancestry}' not in "
            f"{{TRANS,EUR,AFR,EAS,SAS,HIS}}"
        )

    qc: dict = {
        "ancestry": ancestry,
        "consortium": consortium,
        "year": year,
        "trait": "hba1c",
        "input": str(input_path),
        "output": str(output_tsvgz),
        "parquet": str(parquet_path),
    }

    df_raw = pd.read_csv(input_path, sep="\t", low_memory=False)
    qc["n_input"] = int(len(df_raw))
    magic_variant = _detect_magic_variant(df_raw)
    qc["magic_variant"] = magic_variant

    # Detect whether the raw file ships explicit CHR/BP, or whether we'll
    # need the rsid forward crosswalk. We split the column map into a
    # "required" subset (always present regardless of CHR/BP presence) and
    # an "optional" CHR/BP subset that may need crosswalk filling.
    has_raw_chr_bp = ("chromosome" in df_raw.columns and
                       "base_pair_location" in df_raw.columns)

    if magic_variant == "peranc":
        col_map_full = MAGIC_PERANC_COLS
        col_map = (
            col_map_full if has_raw_chr_bp
            else {k: v for k, v in col_map_full.items()
                  if k not in {"chromosome", "base_pair_location"}}
        )
        df = _b2_guard(df_raw, col_map, f"MAGIC peranc ({ancestry})")
        df = _coerce_canonical_dtypes(df)
    else:  # trans_bayes_factor
        col_map_full = MAGIC_TRANS_COLS
        col_map = (
            col_map_full if has_raw_chr_bp
            else {k: v for k, v in col_map_full.items()
                  if k not in {"chromosome", "base_pair_location"}}
        )
        df = _b2_guard(df_raw, col_map, f"MAGIC TRANS BF ({ancestry})")
        df["BETA"] = np.nan
        df["SE"] = np.nan
        df["P"] = np.nan
        df["EAF"] = np.nan
        # Carry log10BF + het_p_value through to qc sidecar (sumstats_utils
        # does not extend the canonical schema, so we drop them from the
        # canonical TSV but record their presence for downstream readers).
        qc["log10BF_carried"] = "log10BF" in df_raw.columns
        qc["het_p_value_carried"] = "het_p_value" in df_raw.columns
        qc["phenotype_lock"] = (
            "log10BF only — no per-variant SE/P; "
            "consume via CPASSOC / HyPrColoc; LDSC / MTAG cannot munge."
        )
        df = _coerce_canonical_dtypes(df)

    # Fill CHR/BP via crosswalk if missing (legacy releases).
    if not has_raw_chr_bp:
        if bim_prefix is None:
            raise ValueError(
                "MAGIC raw file lacks CHR/BP and --bim-prefix not supplied. "
                "Pass --bim-prefix data/reference/ldsc/1000G_EUR_Phase3_plink/"
                "1000G.EUR.QC for the EUR forward crosswalk."
            )
        df = _fill_missing_chr_bp_via_crosswalk(
            df, bim_prefix, bim_chromosomes, qc,
        )
    else:
        qc["n_unmapped_rsid"] = 0

    df = df[CANONICAL_COLS].copy()
    df["CHR"] = df["CHR"].astype(str)

    # MAF filter only meaningful for per-ancestry; TRANS BF has EAF=NaN so
    # everything passes the (NaN >= 0.005) test trivially.
    if magic_variant == "peranc":
        maf = df["EAF"].where(df["EAF"] < 0.5, 1 - df["EAF"])
        keep = maf >= maf_min
        qc["n_maf_below_threshold"] = int((~keep).sum())
        qc["maf_min"] = maf_min
        df = df.loc[keep].reset_index(drop=True)
    else:
        qc["n_maf_below_threshold"] = 0
        qc["maf_min"] = maf_min

    # Palindromic filter (peranc only — TRANS BF has no MAF info to band-filter).
    if magic_variant == "peranc":
        n_pre_pal = len(df)
        df = _su.filter_palindromic_ambiguous(df)
        qc["n_palindromic_dropped"] = n_pre_pal - len(df)
    else:
        qc["n_palindromic_dropped"] = 0

    # validate_canonical_frame allows BETA/SE/P NaN dtype-wise.
    _su.validate_canonical_frame(df[CANONICAL_COLS])
    _emit_dual_artifacts(df[CANONICAL_COLS], output_tsvgz, parquet_path)

    qc["n_output"] = int(len(df))
    qc_json_path.parent.mkdir(parents=True, exist_ok=True)
    qc_json_path.write_text(json.dumps(qc, indent=2, default=str) + "\n")
    return qc


def _parse_chrom_list(s: str | None) -> list[int] | None:
    if s is None or s == "":
        return None
    return [int(x) for x in s.split(",") if x.strip()]


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--parquet", required=True, type=Path)
    ap.add_argument("--qc-json", required=True, type=Path)
    ap.add_argument("--ancestry", required=True,
                    choices=["TRANS", "EUR", "AFR", "EAS", "SAS", "HIS"])
    ap.add_argument(
        "--bim-prefix",
        default=None,
        help="Prefix for PLINK .bim chromosome shards (default 1000G EUR LDSC). "
             "Only consulted if raw file lacks chromosome/base_pair_location.",
    )
    ap.add_argument(
        "--bim-chromosomes",
        default=None,
        help="Comma-sep list of chromosome ints to load (default 1..22).",
    )
    ap.add_argument("--maf-min", type=float, default=0.005)
    ap.add_argument("--consortium", default="MAGIC")
    ap.add_argument("--year", type=int, default=2021)
    args = ap.parse_args()

    harmonize_magic(
        input_path=args.input,
        output_tsvgz=args.output,
        parquet_path=args.parquet,
        qc_json_path=args.qc_json,
        ancestry=args.ancestry,
        bim_prefix=args.bim_prefix,
        bim_chromosomes=_parse_chrom_list(args.bim_chromosomes),
        maf_min=args.maf_min,
        consortium=args.consortium,
        year=args.year,
    )


if __name__ == "__main__":
    _main()
