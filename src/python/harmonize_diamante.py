#!/usr/bin/env python3
"""DIAMANTE Mahajan 2022 T2D trans + per-ancestry harmonizer (D-10).

Source columns (per DIAMANTE portal data dictionary):
    chromosome, position, rsID, effect_allele, other_allele,
    effect_allele_frequency, beta, standard_error, pvalue,
    N_effective, N_case, N_control

Handles TRANS + EUR + EAS + SAS. AFR + HIS strata are dua_pending per
SUMSTATS-UPGRADE.tsv rows 8 + 11 (DIAGRAM gate on manuscript acceptance);
Snakemake emits .deferred placeholder for those — this module refuses
those ancestries with SystemExit.

phenotype_lock: "doctor-diagnosed T2D case-control"

Output: dual-emit per D-09 — `.tsv.gz` (intermediate; Snakemake bgzips
to `.tsv.bgz` + tabix-indexes downstream) AND `.parquet` mirror AND a
`.qc.json` sidecar with palindromic / MAF / N-source drop counts.

Plan reference: m1-02b-harmonizers-case-control-traits-PLAN.md Task 1.
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

# DIAMANTE strata that are released vs DUA-pending (TSV rows 8 + 11).
RELEASED_ANCESTRIES = {"TRANS", "EUR", "EAS", "SAS"}
DEFERRED_ANCESTRIES = {"AFR", "HIS"}

# Raw -> canonical column rename map.
# `effect_allele_frequency` already corresponds to canonical EAF for EA.
DIAMANTE_COLS = {
    "chromosome": "CHR",
    "position": "BP",
    "rsID": "SNP",
    "effect_allele": "EA",
    "other_allele": "OA",
    "effect_allele_frequency": "EAF",
    "beta": "BETA",
    "standard_error": "SE",
    "pvalue": "P",
}


def _b2_guard(df: pd.DataFrame, col_map: dict, source: str) -> pd.DataFrame:
    """B-2 guard (Phase 09 pattern): fail loudly on missing columns."""
    missing = [src for src in col_map if src not in df.columns]
    if missing:
        raise ValueError(
            f"{source} harmonizer: expected columns "
            f"{sorted(col_map.keys())} but file is missing {missing}. "
            f"Found columns: {sorted(df.columns.tolist())}."
        )
    return df[list(col_map.keys())].rename(columns=col_map)


def _coerce_canonical_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in ("BP", "BETA", "SE", "P", "EAF", "N"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ("EA", "OA", "SNP"):
        df[c] = df[c].astype(str)
    df["EA"] = df["EA"].str.upper()
    df["OA"] = df["OA"].str.upper()
    return df


def _emit_dual_artifacts(
    df: pd.DataFrame,
    output_tsvgz: Path,
    parquet_path: Path,
) -> None:
    output_tsvgz.parent.mkdir(parents=True, exist_ok=True)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_tsvgz, sep="\t", index=False, compression="gzip")
    df.to_parquet(parquet_path, index=False, compression="snappy")


def harmonize_diamante(
    input_path: Path,
    output_tsvgz: Path,
    parquet_path: Path,
    qc_json_path: Path,
    *,
    trait: str = "t2d",
    ancestry: str = "TRANS",
    consortium: str = "DIAMANTE",
    year: int = 2022,
    maf_min: float = 0.005,
) -> dict:
    """Harmonize a DIAMANTE Mahajan 2022 T2D summary stat file.

    Parameters
    ----------
    input_path : Path
        Raw DIAMANTE per-ancestry sumstat (`DIAMANTE-<ancestry>.sumstat.txt.gz`).
    output_tsvgz, parquet_path, qc_json_path : Path
        D-09 dual-emit + sidecar paths.
    ancestry : str
        One of ``TRANS, EUR, EAS, SAS``. ``AFR`` and ``HIS`` are
        DUA-pending and refused (TSV rows 8 + 11).

    Returns
    -------
    dict
        QC summary written to ``qc_json_path`` and returned.

    Raises
    ------
    SystemExit
        If ``ancestry`` is in :data:`DEFERRED_ANCESTRIES` (AFR, HIS).
    ValueError
        If ``ancestry`` is unknown OR raw file lacks expected columns.
    """
    qc: dict = {
        "trait": trait,
        "ancestry": ancestry,
        "consortium": consortium,
        "year": year,
        "input": str(input_path),
        "output": str(output_tsvgz),
        "parquet": str(parquet_path),
        "phenotype_lock": "doctor-diagnosed T2D case-control",
    }

    if ancestry in DEFERRED_ANCESTRIES:
        raise SystemExit(
            f"DIAMANTE ancestry='{ancestry}' is DUA-pending per "
            f"SUMSTATS-UPGRADE.tsv rows 8 (AFR) + 11 (HIS); DIAGRAM "
            f"gate on manuscript acceptance. Use the .deferred Snakemake "
            f"rule for this ancestry — this module refuses to harmonize."
        )
    if ancestry not in RELEASED_ANCESTRIES:
        raise ValueError(
            f"DIAMANTE ancestry='{ancestry}' unknown. Expected one of "
            f"{sorted(RELEASED_ANCESTRIES | DEFERRED_ANCESTRIES)}."
        )

    df_raw = pd.read_csv(input_path, sep="\t", compression="infer", low_memory=False)
    qc["n_input"] = int(len(df_raw))

    # B-2 guard on the BETA / SE / P / allele subset (always present).
    df = _b2_guard(df_raw, DIAMANTE_COLS, "DIAMANTE Mahajan 2022")

    # N column: prefer N_effective, fallback to N_case + N_control.
    if "N_effective" in df_raw.columns:
        df["N"] = pd.to_numeric(df_raw["N_effective"], errors="coerce")
        qc["n_source"] = "N_effective"
    elif {"N_case", "N_control"}.issubset(df_raw.columns):
        # Effective N for case-control = 4 / (1/N_case + 1/N_ctrl).
        nc = pd.to_numeric(df_raw["N_case"], errors="coerce")
        nk = pd.to_numeric(df_raw["N_control"], errors="coerce")
        df["N"] = 4.0 / (1.0 / nc + 1.0 / nk)
        qc["n_source"] = "computed_from_N_case_N_control"
    else:
        raise ValueError(
            "DIAMANTE harmonizer: neither N_effective nor "
            "(N_case + N_control) found in input columns: "
            f"{sorted(df_raw.columns.tolist())}."
        )

    df = _coerce_canonical_dtypes(df)
    df = df[CANONICAL_COLS].copy()
    df["CHR"] = df["CHR"].astype(str)

    # MAF >= 0.005 (D-12 QC item).
    maf = df["EAF"].where(df["EAF"] < 0.5, 1 - df["EAF"])
    keep_maf = maf >= maf_min
    n_dropped_maf = int((~keep_maf).sum())
    df = df.loc[keep_maf].reset_index(drop=True)

    # Palindromic SNP filter at MAF=[0.48, 0.52] band (RESEARCH pitfall #2).
    n_pre_pal = len(df)
    df = _su.filter_palindromic_ambiguous(df)
    n_palindromic_dropped = n_pre_pal - len(df)

    # Tabix requires CHR/BP-sorted input; sort canonical-CHR (1..22, X, Y)
    # numerically when possible and BP ascending. Drop rows with non-numeric
    # CHR for tabix safety.
    df = df[CANONICAL_COLS].copy()
    df["_chr_sort"] = pd.to_numeric(df["CHR"], errors="coerce")
    df = df.dropna(subset=["_chr_sort"]).sort_values(
        ["_chr_sort", "BP"]
    ).drop(columns=["_chr_sort"]).reset_index(drop=True)

    _su.validate_canonical_frame(df[CANONICAL_COLS])
    _emit_dual_artifacts(df[CANONICAL_COLS], output_tsvgz, parquet_path)

    qc["n_palindromic_dropped"] = n_palindromic_dropped
    qc["n_maf_below_threshold"] = n_dropped_maf
    qc["maf_min"] = maf_min
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
    ap.add_argument("--trait", default="t2d")
    ap.add_argument(
        "--ancestry",
        required=True,
        choices=sorted(RELEASED_ANCESTRIES | DEFERRED_ANCESTRIES),
    )
    ap.add_argument("--consortium", default="DIAMANTE")
    ap.add_argument("--year", type=int, default=2022)
    ap.add_argument("--maf-min", type=float, default=0.005)
    args = ap.parse_args()

    harmonize_diamante(
        input_path=args.input,
        output_tsvgz=args.output,
        parquet_path=args.parquet,
        qc_json_path=args.qc_json,
        trait=args.trait,
        ancestry=args.ancestry,
        consortium=args.consortium,
        year=args.year,
        maf_min=args.maf_min,
    )


if __name__ == "__main__":
    _main()
