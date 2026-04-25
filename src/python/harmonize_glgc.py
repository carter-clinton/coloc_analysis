#!/usr/bin/env python3
"""GLGC 2021 lipid harmonizer (LDL / HDL / TG / TC × 6 ancestries).

Two raw header families are observed in `data/raw/sumstats_v2/GLGC2021/`:

* **Per-ancestry single-variant meta** (LDL/HDL/TG/TC × {EUR, AFR, EAS, SAS, HIS}):
  ``rsID  CHROM  POS_b37  REF  ALT  N  N_studies  POOLED_ALT_AF  EFFECT_SIZE
   SE  pvalue_neg_log10  pvalue  pvalue_neg_log10_GC  pvalue_GC``
* **TRANS Bayes-factor meta** (LDL/HDL/TG/TC × TRANS):
  ``rsID  CHROM  POS_b37  REF  ALT  N  N_studies  POOLED_ALT_AF  pvalue_neg_log10
   pvalue  lnBF  pvalue_neg_log10_GC  pvalue_GC  METAL_Effect  METAL_StdErr
   METAL_Pvalue``

Both fan into the canonical 10-column schema. The TRANS variant uses
``METAL_Effect`` / ``METAL_StdErr`` / ``METAL_Pvalue`` for BETA / SE / P;
per-ancestry uses ``EFFECT_SIZE`` / ``SE`` / ``pvalue`` directly.

D-04: keep the inventory as-is (LDL × 6 + HDL/TG/TC × 3 each = 15 rows).

logTG note (TSV row 34): the ``logTG_INV_*`` files ship pre-transformed
log-TG values; the harmonizer marks ``phenotype_lock = "log(TG) inverse-
normal transformed"`` in the QC sidecar but does NOT re-transform.

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

# Per-ancestry single-variant column map.
GLGC_PERANC_COLS = {
    "CHROM": "CHR",
    "POS_b37": "BP",
    "rsID": "SNP",
    "REF": "OA",       # GLGC convention: REF = non-effect, ALT = effect.
    "ALT": "EA",
    "POOLED_ALT_AF": "EAF",
    "EFFECT_SIZE": "BETA",
    "SE": "SE",
    "pvalue": "P",
    "N": "N",
}

# TRANS Bayes-factor meta column map (METAL_*).
GLGC_TRANS_COLS = {
    "CHROM": "CHR",
    "POS_b37": "BP",
    "rsID": "SNP",
    "REF": "OA",
    "ALT": "EA",
    "POOLED_ALT_AF": "EAF",
    "METAL_Effect": "BETA",
    "METAL_StdErr": "SE",
    "METAL_Pvalue": "P",
    "N": "N",
}


def _detect_glgc_variant(df: pd.DataFrame) -> str:
    """Return either "peranc" or "trans" based on which BETA-column triplet
    is present in ``df``."""
    if {"EFFECT_SIZE", "SE", "pvalue"}.issubset(df.columns):
        return "peranc"
    if {"METAL_Effect", "METAL_StdErr", "METAL_Pvalue"}.issubset(df.columns):
        return "trans"
    raise ValueError(
        f"GLGC harmonizer: cannot detect TRANS-vs-per-ancestry header. "
        f"Need either {{EFFECT_SIZE, SE, pvalue}} or "
        f"{{METAL_Effect, METAL_StdErr, METAL_Pvalue}}. "
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


def _emit_dual_artifacts(
    df: pd.DataFrame,
    output_tsvgz: Path,
    parquet_path: Path,
) -> None:
    output_tsvgz.parent.mkdir(parents=True, exist_ok=True)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_tsvgz, sep="\t", index=False, compression="gzip")
    df.to_parquet(parquet_path, index=False, compression="snappy")


def _coerce_canonical_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in ("BP", "BETA", "SE", "P", "EAF", "N"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ("EA", "OA", "SNP", "CHR"):
        df[c] = df[c].astype(str)
    return df


def harmonize_glgc(
    input_path: Path,
    output_tsvgz: Path,
    parquet_path: Path,
    qc_json_path: Path,
    subtype: str,
    ancestry: str,
    *,
    maf_min: float = 0.005,
    trait_token: "str | None" = None,
    consortium: str = "GLGC",
    year: int = 2021,
) -> dict:
    """Harmonize a GLGC 2021 lipids file.

    Parameters
    ----------
    subtype : str
        One of {LDL, HDL, TG, TC}. Drives the trait token in the qc sidecar.
    ancestry : str
        One of {TRANS, EUR, AFR, EAS, SAS, HIS}.
    """
    if subtype not in {"LDL", "HDL", "TG", "TC"}:
        raise ValueError(f"GLGC subtype '{subtype}' not in {{LDL,HDL,TG,TC}}")
    if ancestry not in {"TRANS", "EUR", "AFR", "EAS", "SAS", "HIS"}:
        raise ValueError(
            f"GLGC ancestry '{ancestry}' not in "
            f"{{TRANS,EUR,AFR,EAS,SAS,HIS}}"
        )

    trait_lc = (trait_token or subtype).lower()
    qc: dict = {
        "subtype": subtype,
        "ancestry": ancestry,
        "consortium": consortium,
        "year": year,
        "trait": trait_lc,
        "input": str(input_path),
        "output": str(output_tsvgz),
        "parquet": str(parquet_path),
    }

    df_raw = pd.read_csv(input_path, sep="\t", low_memory=False)
    qc["n_input"] = int(len(df_raw))

    glgc_variant = _detect_glgc_variant(df_raw)
    qc["glgc_variant"] = glgc_variant
    col_map = (
        GLGC_PERANC_COLS if glgc_variant == "peranc" else GLGC_TRANS_COLS
    )
    df = _b2_guard(df_raw, col_map, f"GLGC {glgc_variant}")
    df = _coerce_canonical_dtypes(df)
    df = df[CANONICAL_COLS].copy()

    # MAF filter.
    maf = df["EAF"].where(df["EAF"] < 0.5, 1 - df["EAF"])
    keep = maf >= maf_min
    qc["n_maf_below_threshold"] = int((~keep).sum())
    qc["maf_min"] = maf_min
    df = df.loc[keep].reset_index(drop=True)

    # Palindromic filter.
    n_pre_pal = len(df)
    df = _su.filter_palindromic_ambiguous(df)
    qc["n_palindromic_dropped"] = n_pre_pal - len(df)

    _su.validate_canonical_frame(df[CANONICAL_COLS])

    _emit_dual_artifacts(df[CANONICAL_COLS], output_tsvgz, parquet_path)

    # logTG phenotype lock detection: filename hint OR --logtg flag.
    fname_lc = str(input_path).lower()
    is_logtg = subtype == "TG" and ("logtg" in fname_lc)
    if is_logtg:
        qc["phenotype_lock"] = "log(TG) inverse-normal transformed"
    else:
        qc["phenotype_lock"] = None

    qc["n_output"] = int(len(df))
    qc_json_path.parent.mkdir(parents=True, exist_ok=True)
    qc_json_path.write_text(json.dumps(qc, indent=2, default=str) + "\n")
    return qc


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--parquet", required=True, type=Path)
    ap.add_argument("--qc-json", required=True, type=Path)
    ap.add_argument("--subtype", required=True,
                    choices=["LDL", "HDL", "TG", "TC"])
    ap.add_argument("--ancestry", required=True,
                    choices=["TRANS", "EUR", "AFR", "EAS", "SAS", "HIS"])
    ap.add_argument("--maf-min", type=float, default=0.005)
    ap.add_argument("--consortium", default="GLGC")
    ap.add_argument("--year", type=int, default=2021)
    args = ap.parse_args()

    harmonize_glgc(
        input_path=args.input,
        output_tsvgz=args.output,
        parquet_path=args.parquet,
        qc_json_path=args.qc_json,
        subtype=args.subtype,
        ancestry=args.ancestry,
        maf_min=args.maf_min,
        consortium=args.consortium,
        year=args.year,
    )


if __name__ == "__main__":
    _main()
