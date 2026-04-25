#!/usr/bin/env python3
"""BMI continuous-trait harmonizer: Yengo 2018 + Loh 2022 + PAGE 2019.

Three families of input file format share a single canonical-10-col emitter:

* ``yengo2018``  — GIANT 2018 / UKBB meta (Locke + UKBB, GRCh37 native).
  Columns: ``CHR POS SNP Tested_Allele Other_Allele Freq_Tested_Allele_in_HRS
  BETA SE P N``.
* ``loh2022_eur`` / ``loh2022_afr`` — Loh 2022 GIANT + 23andMe meta
  (GRCh38; requires liftover to GRCh37 per DEC-2026-04-24-01).
  Columns (GWAS-Catalog harmonized format):
  ``variant_id chromosome base_pair_location effect_allele other_allele
  effect_allele_frequency beta standard_error p_value n``.
* ``page2019_afr`` — PAGE Wojcik 2019 BMI-AFR (GRCh37 native; ships an
  INFO column ``INFO-score`` filtered at ``--info-min`` (default 0.8)).
  Columns: ``Chr Position_hg19 SNP Other-allele Effect-allele
  Effect-allele-frequency Sample-size Beta SE P-val INFO-score rsid``.

Output: dual-emit per D-09 — the CLI writes a ``.tsv.gz`` (Snakemake bgzips
it to ``.tsv.bgz`` + tabix-indexes downstream) AND a ``.parquet`` mirror
AND a ``.qc.json`` sidecar with palindromic / liftover / INFO drop counts.

Plan reference: m1-02a-harmonizers-continuous-traits-PLAN.md Task 1.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import sumstats_utils as _su  # noqa: E402

CANONICAL_COLS = _su.CANONICAL_COLS

# Per-source column rename maps. Keys are raw-file column names; values are
# canonical-schema names. `_normalize_header` collapses common whitespace
# variants before lookup so a column literally named "P-val" in PAGE survives
# even if pandas read it as ``P-val``.

YENGO_COLS = {
    "CHR": "CHR",
    "POS": "BP",
    "SNP": "SNP",
    "Tested_Allele": "EA",
    "Other_Allele": "OA",
    "Freq_Tested_Allele_in_HRS": "EAF",
    "BETA": "BETA",
    "SE": "SE",
    "P": "P",
    "N": "N",
}

# Loh 2022 ships GWAS-Catalog harmonized format; tolerate both lowercase
# variant_id and the historical "rsid"/"SNP" alternates if Carter's portal
# fetch normalizes naming.
LOH_COLS = {
    "variant_id": "SNP",
    "chromosome": "CHR",
    "base_pair_location": "BP",
    "effect_allele": "EA",
    "other_allele": "OA",
    "effect_allele_frequency": "EAF",
    "beta": "BETA",
    "standard_error": "SE",
    "p_value": "P",
    "n": "N",
}

# PAGE 2019 (Wojcik) — published format with hyphen-separated tokens.
PAGE_COLS = {
    "Chr": "CHR",
    "Position_hg19": "BP",
    "rsid": "SNP",          # "rsid" present alongside "SNP" (chr:pos:ref:alt id);
                            # we prefer the rsXXXX field for downstream LDSC/MTAG.
    "Other-allele": "OA",
    "Effect-allele": "EA",
    "Effect-allele-frequency": "EAF",
    "Sample-size": "N",
    "Beta": "BETA",
    "SE": "SE",
    "P-val": "P",
}


def _b2_guard(df: pd.DataFrame, col_map: dict, source: str) -> pd.DataFrame:
    """B-2 guard (Phase 09 pattern): fail loudly if any expected column is
    missing rather than silently dropping rows downstream."""
    missing = [src for src in col_map if src not in df.columns]
    if missing:
        raise ValueError(
            f"{source} harmonizer: expected columns "
            f"{sorted(col_map.keys())} but file is missing {missing}. "
            f"Found columns: {sorted(df.columns.tolist())}."
        )
    return df[list(col_map.keys())].rename(columns=col_map)


def _emit_dual_artifacts(
    df: pd.DataFrame,
    output_tsvgz: Path,
    parquet_path: Path,
) -> None:
    """Write ``df`` to both ``.tsv.gz`` (intermediate; Snakemake bgzips
    + tabix-indexes) and ``.parquet`` (snappy)."""
    output_tsvgz.parent.mkdir(parents=True, exist_ok=True)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_tsvgz, sep="\t", index=False, compression="gzip")
    df.to_parquet(parquet_path, index=False, compression="snappy")


def _coerce_canonical_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce numeric columns to numeric and string columns to str.

    Centralized because each variant codepath converges on the same
    canonical schema; without this, allele columns may surface as
    object-with-mixed-types which breaks `validate_canonical_frame`.
    """
    df = df.copy()
    for c in ("BP", "BETA", "SE", "P", "EAF", "N"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ("EA", "OA", "SNP"):
        df[c] = df[c].astype(str)
    return df


def harmonize_yengo(
    input_path: Path,
    output_tsvgz: Path,
    parquet_path: Path,
    qc_json_path: Path,
    variant: str,
    *,
    chain_file: "str | None" = None,
    info_min: float = 0.8,
    maf_min: float = 0.005,
    trait: str = "bmi",
    ancestry: str = "EUR",
    consortium: str = "GIANT-UKBB",
    year: int = 2018,
) -> dict:
    """Run the BMI-family harmonizer for the given ``variant`` codepath.

    Returns a dict with QC counts (also written to ``qc_json_path``).
    """
    qc: dict = {
        "variant": variant,
        "trait": trait,
        "ancestry": ancestry,
        "consortium": consortium,
        "year": year,
        "input": str(input_path),
        "output": str(output_tsvgz),
        "parquet": str(parquet_path),
    }

    # --- read raw ---
    sep = "\t"
    df_raw = pd.read_csv(input_path, sep=sep, low_memory=False)
    qc["n_input"] = int(len(df_raw))

    # --- variant codepath: rename + (optional) liftover ---
    n_dropped_info = 0
    n_dropped_maf = 0
    liftover_qc: dict = {}

    if variant == "yengo2018":
        df = _b2_guard(df_raw, YENGO_COLS, "Yengo 2018 GIANT+UKBB")
        df = _coerce_canonical_dtypes(df)

    elif variant in {"loh2022_eur", "loh2022_afr"}:
        df = _b2_guard(df_raw, LOH_COLS, f"Loh 2022 ({variant})")
        df = _coerce_canonical_dtypes(df)
        if chain_file is None:
            raise ValueError(
                f"variant={variant} requires --chain (b38->b37 liftover per "
                f"DEC-2026-04-24-01). Pass the staged hg38ToHg19 chain file."
            )
        df, liftover_qc = _su.liftover_to_grch37(df, chain_file=chain_file)
        # Re-coerce CHR to str post-liftover (liftover_to_grch37 may emit str).
        df["CHR"] = df["CHR"].astype(str)

    elif variant == "page2019_afr":
        # PAGE has both `SNP` (chr:pos:ref:alt) and `rsid`. We map `rsid`->SNP
        # for canonical schema; drop the chr:pos:ref:alt column (kept as side
        # info in the raw archive).
        if "SNP" in df_raw.columns and "rsid" in df_raw.columns:
            # Drop the chr:pos:ref:alt SNP column to avoid double-key collision
            # in the rename below; the canonical SNP is the rsXXXX form.
            df_raw = df_raw.drop(columns=["SNP"])
        df = _b2_guard(df_raw, PAGE_COLS, "PAGE 2019 Wojcik")

        # PAGE-specific INFO filter (RESEARCH §QC checklist item 6).
        if "INFO-score" in df_raw.columns:
            info = pd.to_numeric(df_raw["INFO-score"], errors="coerce")
            keep_info = info.fillna(0) >= info_min
            n_dropped_info = int((~keep_info).sum())
            df = df.loc[keep_info.values].reset_index(drop=True)

        df = _coerce_canonical_dtypes(df)

    else:
        raise ValueError(
            f"Unknown variant '{variant}'. Expected one of "
            f"yengo2018, loh2022_eur, loh2022_afr, page2019_afr."
        )

    # --- canonical column ordering (after rename, before filters) ---
    df = df[CANONICAL_COLS].copy()
    df["CHR"] = df["CHR"].astype(str)

    # MAF >= 0.005 filter (D-12 QC item).
    maf = df["EAF"].where(df["EAF"] < 0.5, 1 - df["EAF"])
    keep_maf = maf >= maf_min
    n_dropped_maf = int((~keep_maf).sum())
    df = df.loc[keep_maf].reset_index(drop=True)

    # --- palindromic SNP filter at MAF=[0.48, 0.52] band ---
    n_pre_pal = len(df)
    df = _su.filter_palindromic_ambiguous(df)
    n_palindromic_dropped = n_pre_pal - len(df)

    # --- contract validation ---
    _su.validate_canonical_frame(df[CANONICAL_COLS])

    # --- emit dual artifacts ---
    _emit_dual_artifacts(df[CANONICAL_COLS], output_tsvgz, parquet_path)

    # --- QC sidecar ---
    qc["n_palindromic_dropped"] = n_palindromic_dropped
    qc["n_maf_below_threshold"] = n_dropped_maf
    qc["maf_min"] = maf_min
    qc["n_info_below_threshold"] = n_dropped_info
    qc["info_min"] = info_min if variant == "page2019_afr" else None
    qc["n_output"] = int(len(df))
    if liftover_qc:
        qc["n_liftover_input"] = liftover_qc.get("n_input")
        qc["n_liftover_lifted"] = liftover_qc.get("n_lifted")
        qc["n_liftover_dropped"] = liftover_qc.get("n_dropped")
        qc["liftover_drop_rate"] = liftover_qc.get("drop_rate")
    qc_json_path.parent.mkdir(parents=True, exist_ok=True)
    qc_json_path.write_text(json.dumps(qc, indent=2, default=str) + "\n")

    return qc


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path,
                    help="Intermediate .tsv.gz path; Snakemake bgzips to .tsv.bgz")
    ap.add_argument("--parquet", required=True, type=Path)
    ap.add_argument("--qc-json", required=True, type=Path)
    ap.add_argument(
        "--variant",
        required=True,
        choices=["yengo2018", "loh2022_eur", "loh2022_afr", "page2019_afr"],
    )
    ap.add_argument("--chain", default=None,
                    help="Path to hg38ToHg19 chain (required for loh2022_*)")
    ap.add_argument("--info-min", type=float, default=0.8)
    ap.add_argument("--maf-min", type=float, default=0.005)
    ap.add_argument("--trait", default="bmi")
    ap.add_argument("--ancestry", default="EUR")
    ap.add_argument("--consortium", default="GIANT-UKBB")
    ap.add_argument("--year", type=int, default=2018)
    args = ap.parse_args()

    harmonize_yengo(
        input_path=args.input,
        output_tsvgz=args.output,
        parquet_path=args.parquet,
        qc_json_path=args.qc_json,
        variant=args.variant,
        chain_file=args.chain,
        info_min=args.info_min,
        maf_min=args.maf_min,
        trait=args.trait,
        ancestry=args.ancestry,
        consortium=args.consortium,
        year=args.year,
    )


if __name__ == "__main__":
    _main()
