#!/usr/bin/env python3
"""Aragam 2022 CARDIoGRAM-C4D-MVP CAD harmonizer + Klarin 2018 fallback (D-10).

Source columns (per RVTESTS meta header observed in
data/raw/sumstats_v2/Aragam2022/CAD/CAD_GWAS_*.tsv from Wave 1 ZIP unpack):
    MarkerName, CHR, BP, Allele1, Allele2, Freq1, FreqSE, MinFreq,
    MaxFreq, Effect, StdErr, P-value, Direction, HetISq, HetChiSq,
    HetDf, HetPVal, Cases, Effective_Cases, N [, Meta_analysis]

D-03 branch routing:
- Branch (a, AFR file present in ZIP): standard `harmonize_aragam` for
  TRANS + EUR + EAS + AFR.
- Branch (b, AFR absent): `harmonize_aragam` raises NotImplementedError
  for ancestry=AFR. Caller must use `harmonize_aragam_klarin2018()`
  with the Klarin 2018 MVP-AFR-CAD file (KP4CD / Zenodo / DUA).

Phase 1 fire (m1-01) determined branch (b): no AFR file in the ZIP
(see data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt).
The Klarin 2018 file remains DEFERRED with PENDING_D03_FALLBACK_RESOLUTION.

phenotype_lock: "CAD case-control (broad MI + CAD composite)"

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

VALID_ANCESTRIES = {"TRANS", "EUR", "EAS", "AFR"}

DEFAULT_ARAGAM_MANIFEST = Path(
    "data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt"
)

# Aragam RVTESTS meta column rename map.
ARAGAM_COLS = {
    "MarkerName": "SNP",
    "CHR": "CHR",
    "BP": "BP",
    "Allele1": "EA",
    "Allele2": "OA",
    "Freq1": "EAF",
    "Effect": "BETA",
    "StdErr": "SE",
    "P-value": "P",
    "N": "N",
}

# Klarin 2018 MVP format (best-effort guess; verify against actual file
# at fire time — Wave 1 has not located the file yet, so the column map
# below is the canonical "MVP" PLINK2-output convention. If the actual
# Klarin release ships a different schema, adjust KLARIN_COLS at fire time.)
KLARIN_COLS = {
    "ID": "SNP",
    "CHROM": "CHR",
    "POS": "BP",
    "ALT": "EA",
    "REF": "OA",
    "AF": "EAF",
    "BETA": "BETA",
    "SE": "SE",
    "P": "P",
}
# Klarin 2018 N is computed from N_case + N_ctrl if both columns present;
# else falls back to a single N column or uses a hardcoded N=8500 from
# the SUMSTATS-UPGRADE.tsv row 23 reference.


def _branch_for_afr(
    manifest: Path = DEFAULT_ARAGAM_MANIFEST,
) -> str:
    """Return 'a' if Aragam ZIP contains an AFR file, else 'b'.

    Reads the line-buffered ZIP listing produced in m1-00 Task 3
    (data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt). Returns
    'a' if any of the substrings "AFR", "African", "AA_", "_AA." are
    present; otherwise 'b' (Klarin 2018 fallback path required).

    Raises
    ------
    FileNotFoundError
        If the manifest is absent (Wave 0 ZIP audit not run).
    """
    if not Path(manifest).exists():
        raise FileNotFoundError(
            f"D-03 aragam_zip_manifest.txt missing at {manifest}; "
            f"Wave 0 ZIP enumeration not performed. Run "
            f"`unzip -l data/raw/sumstats_v2/Aragam2022/CAD/Aragam_2022_CARDIoGRAM_CAD_GWAS.zip "
            f"> {manifest}` before invoking this harmonizer."
        )
    text = Path(manifest).read_text()
    afr_tokens = ("AFR", "African", "AA_", "_AA.")
    return "a" if any(tok in text for tok in afr_tokens) else "b"


def _b2_guard(df: pd.DataFrame, col_map: dict, source: str) -> pd.DataFrame:
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


def _filter_emit(
    df: pd.DataFrame,
    qc: dict,
    output_tsvgz: Path,
    parquet_path: Path,
    qc_json_path: Path,
    *,
    maf_min: float = 0.005,
) -> dict:
    """Shared MAF/palindromic filter + sort + dual emit + qc.json."""
    df = df[CANONICAL_COLS].copy()
    df["CHR"] = df["CHR"].astype(str)

    maf = df["EAF"].where(df["EAF"] < 0.5, 1 - df["EAF"])
    keep_maf = maf >= maf_min
    qc["n_maf_below_threshold"] = int((~keep_maf).sum())
    df = df.loc[keep_maf].reset_index(drop=True)

    n_pre_pal = len(df)
    df = _su.filter_palindromic_ambiguous(df)
    qc["n_palindromic_dropped"] = n_pre_pal - len(df)

    # Tabix requires CHR/BP-sorted input. Aragam RVTESTS meta is naturally
    # sorted but enforce explicitly to be safe across all sources.
    df = df[CANONICAL_COLS].copy()
    df["_chr_sort"] = pd.to_numeric(df["CHR"], errors="coerce")
    df = df.dropna(subset=["_chr_sort"]).sort_values(
        ["_chr_sort", "BP"]
    ).drop(columns=["_chr_sort"]).reset_index(drop=True)

    _su.validate_canonical_frame(df[CANONICAL_COLS])
    _emit_dual_artifacts(df[CANONICAL_COLS], output_tsvgz, parquet_path)

    qc["n_output"] = int(len(df))
    qc["maf_min"] = maf_min
    qc_json_path.parent.mkdir(parents=True, exist_ok=True)
    qc_json_path.write_text(json.dumps(qc, indent=2, default=str) + "\n")
    return qc


def harmonize_aragam(
    input_path: Path,
    output_tsvgz: Path,
    parquet_path: Path,
    qc_json_path: Path,
    *,
    trait: str = "cad",
    ancestry: str = "TRANS",
    consortium: str = "CARDIoGRAM-C4D-MVP",
    year: int = 2022,
    maf_min: float = 0.005,
    manifest_path: Path = DEFAULT_ARAGAM_MANIFEST,
    skip_branch_check: bool = False,
) -> dict:
    """Harmonize an Aragam 2022 CARDIoGRAM-C4D-MVP CAD summary stat file.

    Parameters
    ----------
    skip_branch_check : bool
        If True, skip the D-03 manifest-based branch check (used by
        TRANS / EUR / EAS where AFR is not requested and the manifest
        may not be locally available, e.g., in unit tests).

    Raises
    ------
    NotImplementedError
        If ``ancestry == "AFR"`` and branch resolves to 'b' (no AFR
        file in ZIP). Caller must use :func:`harmonize_aragam_klarin2018`.
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
        "phenotype_lock": "CAD case-control (broad MI + CAD composite)",
    }

    if ancestry not in VALID_ANCESTRIES:
        raise ValueError(
            f"Aragam ancestry='{ancestry}' unknown. Expected one of "
            f"{sorted(VALID_ANCESTRIES)}."
        )

    if ancestry == "AFR" and not skip_branch_check:
        branch = _branch_for_afr(manifest_path)
        qc["d03_branch"] = branch
        if branch == "b":
            raise NotImplementedError(
                "D-03 branch b: Aragam AFR absent from ZIP manifest. "
                "Use harmonize_aragam_klarin2018() (Klarin 2018 MVP-AFR-CAD "
                "fallback per SUMSTATS-UPGRADE.tsv row 23) or emit a "
                ".deferred placeholder via Snakemake."
            )

    df_raw = pd.read_csv(input_path, sep="\t", compression="infer", low_memory=False)
    qc["n_input"] = int(len(df_raw))

    df = _b2_guard(df_raw, ARAGAM_COLS, "Aragam 2022 CARDIoGRAM")
    df = _coerce_canonical_dtypes(df)
    return _filter_emit(df, qc, output_tsvgz, parquet_path, qc_json_path,
                        maf_min=maf_min)


def harmonize_aragam_klarin2018(
    input_path: Path,
    output_tsvgz: Path,
    parquet_path: Path,
    qc_json_path: Path,
    *,
    trait: str = "cad",
    ancestry: str = "AFR",
    consortium: str = "MVP-CHARGE-Klarin",
    year: int = 2018,
    maf_min: float = 0.005,
) -> dict:
    """Harmonize the Klarin 2018 MVP-AFR-CAD fallback file (D-03 branch b).

    Klarin et al. 2018 published an AFR-stratified MVP CAD analysis.
    SUMSTATS-UPGRADE.tsv row 23 records N=8500 for this file. The
    actual file location is PENDING_D03_FALLBACK_RESOLUTION as of
    Wave 1 fire — when located, this function harmonizes it to the
    canonical 10-col schema with N = N_case + N_ctrl from the file.
    """
    qc: dict = {
        "trait": trait,
        "ancestry": ancestry,
        "consortium": consortium,
        "year": year,
        "input": str(input_path),
        "output": str(output_tsvgz),
        "parquet": str(parquet_path),
        "phenotype_lock": (
            "CAD case-control AFR subset (Klarin 2018 MVP-AFR-CAD fallback)"
        ),
    }

    df_raw = pd.read_csv(input_path, sep="\t", compression="infer", low_memory=False)
    qc["n_input"] = int(len(df_raw))

    df = _b2_guard(df_raw, KLARIN_COLS, "Klarin 2018 MVP-AFR-CAD")
    if {"N_case", "N_ctrl"}.issubset(df_raw.columns):
        nc = pd.to_numeric(df_raw["N_case"], errors="coerce")
        nk = pd.to_numeric(df_raw["N_ctrl"], errors="coerce")
        df["N"] = nc.fillna(0) + nk.fillna(0)
        qc["n_source"] = "N_case + N_ctrl"
    elif "N" in df_raw.columns:
        df["N"] = pd.to_numeric(df_raw["N"], errors="coerce")
        qc["n_source"] = "N column"
    else:
        df["N"] = 8500  # SUMSTATS-UPGRADE.tsv row 23 reference total.
        qc["n_source"] = "fallback_8500_from_SUMSTATS-UPGRADE.tsv"

    df = _coerce_canonical_dtypes(df)
    return _filter_emit(df, qc, output_tsvgz, parquet_path, qc_json_path,
                        maf_min=maf_min)


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--parquet", required=True, type=Path)
    ap.add_argument("--qc-json", required=True, type=Path)
    ap.add_argument("--trait", default="cad")
    ap.add_argument("--ancestry", required=True, choices=sorted(VALID_ANCESTRIES))
    ap.add_argument("--consortium", default="CARDIoGRAM-C4D-MVP")
    ap.add_argument("--year", type=int, default=2022)
    ap.add_argument("--maf-min", type=float, default=0.005)
    ap.add_argument("--klarin-fallback", action="store_true",
                    help="Use Klarin 2018 MVP-AFR-CAD fallback codepath")
    ap.add_argument("--manifest-path", type=Path, default=DEFAULT_ARAGAM_MANIFEST)
    args = ap.parse_args()

    if args.klarin_fallback:
        harmonize_aragam_klarin2018(
            input_path=args.input,
            output_tsvgz=args.output,
            parquet_path=args.parquet,
            qc_json_path=args.qc_json,
            trait=args.trait,
            ancestry=args.ancestry,
            consortium="MVP-CHARGE-Klarin",
            year=2018,
            maf_min=args.maf_min,
        )
    else:
        harmonize_aragam(
            input_path=args.input,
            output_tsvgz=args.output,
            parquet_path=args.parquet,
            qc_json_path=args.qc_json,
            trait=args.trait,
            ancestry=args.ancestry,
            consortium=args.consortium,
            year=args.year,
            maf_min=args.maf_min,
            manifest_path=args.manifest_path,
        )


if __name__ == "__main__":
    _main()
