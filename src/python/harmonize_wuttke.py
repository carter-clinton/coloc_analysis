#!/usr/bin/env python3
"""CKDGen Wuttke 2019 + Morris 2019 AFR companion eGFR harmonizer.

Three variant codepaths (all GRCh37 native; no liftover):

* ``wuttke2019_trans`` — CKDGen Wuttke 2019 trans-ancestry overall meta
  (`20171016_MW_eGFR_overall_ALL_nstud61.dbgap.txt.gz`).
* ``wuttke2019_eur`` — CKDGen Wuttke 2019 EUR-only meta
  (`20171017_MW_eGFR_overall_EA_nstud42.dbgap.txt.gz`).
* ``morris2019_afr`` — Morris 2019 eGFR-AFR companion paper.

All three observed files share the same space-delimited Wuttke header
``Chr Pos_b37 RSID Allele1 Allele2 Freq1 Effect StdErr P-value n_total_sum``
(verified against the production files staged from CKDGen Freiburg).

Plan reference: m1-02a-harmonizers-continuous-traits-PLAN.md Task 2.
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

# Wuttke / Morris common column rename map.
WUTTKE_COLS = {
    "Chr": "CHR",
    "Pos_b37": "BP",
    "RSID": "SNP",
    "Allele1": "EA",
    "Allele2": "OA",
    "Freq1": "EAF",
    "Effect": "BETA",
    "StdErr": "SE",
    "P-value": "P",
    "n_total_sum": "N",
}

# Alternate Morris 2019 header (defensive — file naming hints at a possible
# different schema; we try Wuttke schema first and fall through).
MORRIS_AFR_ALT_COLS = {
    "Chromosome": "CHR",
    "Position": "BP",
    "SNP_ID": "SNP",
    "Effect_Allele": "EA",
    "Other_Allele": "OA",
    "EAF": "EAF",
    "BETA": "BETA",
    "SE": "SE",
    "P": "P",
    "N": "N",
}


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
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ("EA", "OA", "SNP", "CHR"):
        df[c] = df[c].astype(str)
    # Wuttke alleles are lowercase (a/t/c/g); upper-case for canonical comparability.
    df["EA"] = df["EA"].str.upper()
    df["OA"] = df["OA"].str.upper()
    return df


def _read_raw(input_path: Path) -> pd.DataFrame:
    """Wuttke files are whitespace-delimited; auto-detect tab fallback for
    Morris alt-format if the Wuttke schema isn't found.

    pandas ``sep=r"\\s+"`` with the python engine handles both single-space
    delimiters (Wuttke production files) and multi-space alignment-style
    delimiters defensively.
    """
    # Try whitespace first (Wuttke convention) — single-space and tab both.
    # NOTE: pandas python engine does not accept low_memory; rely on default.
    df = pd.read_csv(input_path, sep=r"\s+", engine="python")
    if "Chr" in df.columns or "Chromosome" in df.columns:
        return df
    # Fall back to tab-delimited (Morris alt-format possibility).
    return pd.read_csv(input_path, sep="\t", low_memory=False)


def harmonize_wuttke(
    input_path: Path,
    output_tsvgz: Path,
    parquet_path: Path,
    qc_json_path: Path,
    variant: str,
    *,
    maf_min: float = 0.005,
    ancestry: str = "EUR",
    consortium: str = "CKDGen",
    year: int = 2019,
) -> dict:
    if variant not in {"wuttke2019_trans", "wuttke2019_eur", "morris2019_afr"}:
        raise ValueError(
            f"Unknown variant '{variant}'. Expected one of "
            f"wuttke2019_trans, wuttke2019_eur, morris2019_afr."
        )

    qc: dict = {
        "variant": variant,
        "ancestry": ancestry,
        "consortium": consortium,
        "year": year,
        "trait": "egfr",
        "input": str(input_path),
        "output": str(output_tsvgz),
        "parquet": str(parquet_path),
    }

    df_raw = _read_raw(input_path)
    qc["n_input"] = int(len(df_raw))

    # Probe Wuttke schema first; fall back to Morris alt if Wuttke fails.
    if "Chr" in df_raw.columns and "RSID" in df_raw.columns:
        df = _b2_guard(df_raw, WUTTKE_COLS, f"Wuttke/Morris ({variant})")
    elif "Chromosome" in df_raw.columns and "SNP_ID" in df_raw.columns:
        df = _b2_guard(df_raw, MORRIS_AFR_ALT_COLS, "Morris 2019 alt schema")
    else:
        raise ValueError(
            f"{variant} harmonizer: cannot detect Wuttke or Morris-alt header. "
            f"Found columns: {sorted(df_raw.columns.tolist())}."
        )

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
    ap.add_argument("--variant", required=True,
                    choices=["wuttke2019_trans", "wuttke2019_eur", "morris2019_afr"])
    ap.add_argument("--ancestry", required=True,
                    choices=["TRANS", "EUR", "AFR"])
    ap.add_argument("--maf-min", type=float, default=0.005)
    ap.add_argument("--consortium", default="CKDGen")
    ap.add_argument("--year", type=int, default=2019)
    args = ap.parse_args()
    harmonize_wuttke(
        input_path=args.input,
        output_tsvgz=args.output,
        parquet_path=args.parquet,
        qc_json_path=args.qc_json,
        variant=args.variant,
        maf_min=args.maf_min,
        ancestry=args.ancestry,
        consortium=args.consortium,
        year=args.year,
    )


if __name__ == "__main__":
    _main()
