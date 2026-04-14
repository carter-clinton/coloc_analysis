#!/usr/bin/env python3
"""MVP dbGaP phs001672 sumstats -> canonical harmonized (Plan 09-02 Task 4).

Wave-1 corrections (see .planning/phases/09-replication-in-independent-cohorts/
09-01-SUMMARY.md deviations) established that phs001672 uses:

  1. **GRCh38** (not GRCh37); liftover is required.
  2. The **dbGaP GWAS-central** column schema (|β| absolute value +
     "Coded Allele" orientation), not raw REGENIE.

This harmonizer supports BOTH schemas, dispatching on detected column set:

  - REGENIE-style (CHROM, POS, REF, ALT, BETA, LOG10P, N, ID, A1_FREQ) —
    used by the Wave-1 pytest fixture and some MVP pre-release files.
  - dbGaP GWAS-central (Chr ID, Chr Position, Allele1, Allele2, |β|/β, SE,
    P-value, Coded Allele, Sample size, SNP ID) — the real phs001672
    release; signed beta reconstructed from Coded Allele orientation.

LOG10P -> P conversion follows the Phase 2 convention of clipping LOG10P
to [0, 300] before exponentiation (avoids numeric underflow at 1e-300).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import sumstats_utils as _su  # noqa: E402

CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]


def log10p_to_pval(log10p: pd.Series, clip: tuple = (0.0, 300.0)) -> pd.Series:
    """Convert LOG10P to P with clip to [0, 300] (Phase 2 convention).

    Clipping below 0 handles edge-case negative LOG10P data errors.
    Clipping above 300 prevents numeric underflow at P < 1e-300.
    """
    clipped = log10p.clip(lower=clip[0], upper=clip[1])
    return pd.Series(np.power(10.0, -clipped.values), index=clipped.index)


def reconstruct_signed_beta(
    df: pd.DataFrame,
    beta_abs_col: str = "beta_abs",
    coded_col: str = "coded_allele",
    ea_col: str = "EA",
    oa_col: str = "OA",
) -> pd.Series:
    """Rebuild signed BETA from |β| + coded allele orientation.

    dbGaP GWAS-central reports |β| (always non-negative) plus a "Coded
    Allele" column whose value is either the effect allele (EA) or the
    other allele (OA). When coded == EA the sign is +; when coded == OA
    the sign is -. The returned Series has the same index as ``df``.
    """
    coded_upper = df[coded_col].astype(str).str.upper()
    ea_upper = df[ea_col].astype(str).str.upper()
    oa_upper = df[oa_col].astype(str).str.upper()
    # Sign = +1 when coded == EA, -1 when coded == OA, else NaN (unclassified)
    sign = pd.Series(np.nan, index=df.index)
    sign[coded_upper == ea_upper] = 1.0
    sign[coded_upper == oa_upper] = -1.0
    signed = sign * df[beta_abs_col].astype(float)
    return signed


def _detect_schema(df: pd.DataFrame) -> str:
    """Return 'regenie' or 'dbgap' based on observed columns."""
    if "CHROM" in df.columns and ("BETA" in df.columns or "LOG10P" in df.columns):
        return "regenie"
    if "Chr ID" in df.columns and ("β" in df.columns or "|β|" in df.columns):
        return "dbgap"
    raise ValueError(
        "MVP harmonizer: could not detect schema (REGENIE or dbGaP). "
        f"Observed columns: {sorted(df.columns.tolist())}"
    )


def _harmonize_regenie(df: pd.DataFrame) -> pd.DataFrame:
    """REGENIE-style -> canonical. Assumes CHROM/POS/REF/ALT/BETA/LOG10P|PVAL."""
    out = df.rename(
        columns={
            "CHROM": "CHR",
            "POS": "BP",
            "ID": "SNP",
            "REF": "OA",
            "ALT": "EA",
            "A1_FREQ": "EAF",
            "BETA": "BETA",
            "SE": "SE",
            "N": "N",
        }
    )
    if "LOG10P" in out.columns:
        out["P"] = log10p_to_pval(out["LOG10P"])
    elif "PVAL" in out.columns:
        out["P"] = out["PVAL"]
    elif "P" in out.columns:
        pass  # already named
    else:
        raise ValueError("REGENIE MVP file: no LOG10P, PVAL, or P column")
    # Fill SNP if absent
    if "SNP" not in out.columns:
        out["SNP"] = out["CHR"].astype(str) + ":" + out["BP"].astype(str)
    return out[CANONICAL_COLS]


def _harmonize_dbgap(df: pd.DataFrame) -> pd.DataFrame:
    """dbGaP GWAS-central -> canonical. Reconstructs signed BETA."""
    # Normalise the beta column name (can be 'β' or '|β|' depending on
    # copy method; both mean the same thing per dbGaP docs).
    beta_col = "β" if "β" in df.columns else "|β|"

    out = pd.DataFrame()
    out["CHR"] = df["Chr ID"].astype(str)
    out["BP"] = df["Chr Position"].astype(int)
    out["SNP"] = df.get("SNP ID", pd.Series([""] * len(df))).astype(str)
    out["OA"] = df["Allele1"].astype(str)
    out["EA"] = df["Allele2"].astype(str)
    out["SE"] = df["SE"].astype(float)
    out["P"] = df["P-value"].astype(float)
    out["N"] = df["Sample size"].astype(int)
    # EAF not in dbGaP GWAS-central; fill NaN, downstream can re-merge
    # allele frequencies from a reference if needed.
    out["EAF"] = np.nan

    # Signed beta — needs EA/OA already present in `out`.
    tmp = out.copy()
    tmp["beta_abs"] = df[beta_col].astype(float).values
    tmp["coded_allele"] = df["Coded Allele"].astype(str).values
    out["BETA"] = reconstruct_signed_beta(tmp).values

    return out[CANONICAL_COLS]


def harmonize_mvp_sumstats(
    input_gz: Path,
    output_gz: Path,
    pha_id: str,
    trait: str,
    ancestry: str,
    genome_build: str = "GRCh37",
    chain_file: Optional[Path] = None,
    qc_out: Optional[Path] = None,
) -> dict:
    """Harmonize an MVP phs001672 analysis file to canonical schema.

    Parameters
    ----------
    input_gz : Path
        MVP dbGaP text file (``phs001672.pha#####.txt.gz`` or a REGENIE
        variant).
    output_gz : Path
        Output path for the harmonized (canonical-schema) gzipped TSV.
    pha_id : str
        dbGaP analysis ID (e.g., ``pha004945.1``).
    trait : str
        Phase-9 trait label.
    ancestry : str
        Ancestry stratum (``eur``, ``afr``, ``eas``, ``his``, ``trans``).
    genome_build : {"GRCh37", "GRCh38"}
        Source build. GRCh38 triggers liftover to GRCh37 (pitfall #1).
    chain_file : Path, optional
        Chain file for liftover; required iff genome_build == GRCh38.
    qc_out : Path, optional
        JSON QC path.

    Returns
    -------
    dict
        QC summary including detected schema and liftover QC (when applied).
    """
    df_raw = pd.read_csv(input_gz, sep="\t", compression="gzip", low_memory=False)
    schema = _detect_schema(df_raw)

    if schema == "regenie":
        df = _harmonize_regenie(df_raw)
    else:  # dbgap
        df = _harmonize_dbgap(df_raw)

    qc: dict = {
        "cohort": "mvp_phs001672",
        "pha_id": pha_id,
        "trait": trait,
        "ancestry": ancestry,
        "schema": schema,
        "n_input": int(len(df)),
    }

    if genome_build == "GRCh38":
        if chain_file is None:
            raise ValueError("MVP GRCh38 file requires chain_file for liftover")
        df, liftover_qc = _su.liftover_to_grch37(df, str(chain_file))
        qc.update(liftover_qc)

    # Palindromic exclusion. dbGaP files with NaN EAF can't meet the MAF
    # band test (NaN is always outside any interval) -> all palindromes
    # retained but flagged. That's the correct behavior: we defer strand
    # resolution until a reference EAF is merged in Plan 09-03.
    n_before_pal = len(df)
    df = _su.filter_palindromic_ambiguous(df)
    qc["n_after_palindromic"] = int(len(df))
    qc["n_palindromic_dropped"] = int(n_before_pal - len(df))
    qc["n_output"] = int(len(df))

    Path(output_gz).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_gz, sep="\t", index=False, compression="gzip")

    if qc_out is not None:
        Path(qc_out).parent.mkdir(parents=True, exist_ok=True)
        Path(qc_out).write_text(json.dumps(qc, indent=2))

    return qc


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--pha-id", required=True)
    ap.add_argument("--trait", required=True)
    ap.add_argument("--ancestry", required=True)
    ap.add_argument("--genome-build", default="GRCh38",
                    help="GRCh37 or GRCh38 (default: GRCh38 — real phs001672 build)")
    ap.add_argument("--chain-file", default=None)
    ap.add_argument("--qc-out", default=None)
    args = ap.parse_args()

    harmonize_mvp_sumstats(
        Path(args.input),
        Path(args.output),
        args.pha_id,
        args.trait,
        args.ancestry,
        genome_build=args.genome_build,
        chain_file=Path(args.chain_file) if args.chain_file else None,
        qc_out=Path(args.qc_out) if args.qc_out else None,
    )


if __name__ == "__main__":
    _main()
