#!/usr/bin/env python3
"""GIGASTROKE Mishra 2022 all-stroke harmonizer (D-10).

Source columns (per EBI GWAS-Catalog harmonized format observed at
data/raw/sumstats_v2/GIGASTROKE2022/stroke/<ancestry>/GCST*.tsv.gz):
    chromosome, base_pair_location, effect_allele_frequency, beta,
    standard_error, p_value, odds_ratio, ci_lower, ci_upper,
    effect_allele, other_allele

Note: real GIGASTROKE files do NOT ship `variant_id` (rsID) or `n`
columns. The harmonizer synthesizes a SNP ID from
``chr:bp:OA:EA`` (canonical chr:bp:ref:alt convention) and pulls
the per-ancestry N total from `.planning/amendments/SUMSTATS-UPGRADE.tsv`
(rows 14-17). The plan-spec'd `variant_id` / `n` columns are still
honored opportunistically: if the input file ships them, they are
used instead of the synthesized values (e.g., for the test fixture).

phenotype_lock: "all-stroke (AS) case-control, combined ischemic + hemorrhagic"

Defensive D-02 integer-lock guard: at module load (and via the
testable :func:`_reload_filenames` entry point) every row of the
GIGASTROKE block in ``.planning/amendments/SUMSTATS-UPGRADE.tsv`` is
checked for the placeholder substring ``GCST90104540-series``.
Presence of the placeholder indicates Wave 0 D-02 lock was not
committed and the harmonizer must refuse to run.

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

# Module-level path to the locked inventory TSV. Tests may monkeypatch this
# before calling :func:`_reload_filenames` to exercise the placeholder guard.
_TSV = Path(".planning/amendments/SUMSTATS-UPGRADE.tsv")

VALID_ANCESTRIES = {"TRANS", "EUR", "AFR", "EAS", "SAS"}

# Per-ancestry total N (cases + controls) used when the raw file lacks an
# explicit n column. Values match SUMSTATS-UPGRADE.tsv rows 14-17.
GIGASTROKE_N_TOTAL = {
    "TRANS": 1614080,
    "EUR": 1296908,
    "AFR": 23991,
    "EAS": 400907,
}

# Raw -> canonical column rename map. `n` and `variant_id` are optional
# (the production GIGASTROKE files lack both); rename happens only if the
# column is present in the input.
GIGASTROKE_COLS_REQUIRED = {
    "chromosome": "CHR",
    "base_pair_location": "BP",
    "effect_allele": "EA",
    "other_allele": "OA",
    "effect_allele_frequency": "EAF",
    "beta": "BETA",
    "standard_error": "SE",
    "p_value": "P",
}
GIGASTROKE_COLS_OPTIONAL = {
    "variant_id": "SNP",
    "n": "N",
}


def _reload_filenames() -> dict:
    """Read SUMSTATS-UPGRADE.tsv and return ancestry -> filename map.

    Raises RuntimeError if any GIGASTROKE row still has the
    `GCST90104540-series` placeholder (Wave 0 D-02 lock not committed).
    """
    if not _TSV.exists():
        return {}

    df = pd.read_csv(_TSV, sep="\t")
    sub = df[df["source_consortium"] == "GIGASTROKE"].copy()
    for _, row in sub.iterrows():
        fn = str(row.get("expected_filename", ""))
        if "GCST90104540-series" in fn:
            raise RuntimeError(
                f"GIGASTROKE ancestry={row.get('ancestry', '?')}: filename "
                f"still has placeholder '{fn}'. Wave 0 D-02 lock not "
                f"committed. Fix .planning/amendments/SUMSTATS-UPGRADE.tsv "
                f"before running."
            )
    if len(sub):
        return dict(zip(sub["ancestry"], sub["expected_filename"]))
    return {}


# Module-level constant (lazily evaluated; tests may force re-evaluation
# via :func:`_reload_filenames`).
GIGASTROKE_FILENAMES = _reload_filenames()


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


def harmonize_gigastroke(
    input_path: Path,
    output_tsvgz: Path,
    parquet_path: Path,
    qc_json_path: Path,
    *,
    trait: str = "stroke",
    ancestry: str = "TRANS",
    consortium: str = "GIGASTROKE",
    year: int = 2022,
    maf_min: float = 0.005,
) -> dict:
    """Harmonize a GIGASTROKE Mishra 2022 all-stroke summary stat file."""
    qc: dict = {
        "trait": trait,
        "ancestry": ancestry,
        "consortium": consortium,
        "year": year,
        "input": str(input_path),
        "output": str(output_tsvgz),
        "parquet": str(parquet_path),
        "phenotype_lock": "all-stroke (AS) case-control, combined ischemic + hemorrhagic",
    }

    if ancestry not in VALID_ANCESTRIES:
        raise ValueError(
            f"GIGASTROKE ancestry='{ancestry}' unknown. Expected one of "
            f"{sorted(VALID_ANCESTRIES)}."
        )

    df_raw = pd.read_csv(input_path, sep="\t", compression="infer", low_memory=False)
    qc["n_input"] = int(len(df_raw))

    df = _b2_guard(df_raw, GIGASTROKE_COLS_REQUIRED, "GIGASTROKE Mishra 2022")

    # Optional SNP column. If absent, synthesize chr:bp:OA:EA.
    if "variant_id" in df_raw.columns:
        df["SNP"] = df_raw["variant_id"].astype(str)
        qc["snp_source"] = "variant_id"
    else:
        df["SNP"] = (
            df_raw["chromosome"].astype(str)
            + ":"
            + df_raw["base_pair_location"].astype(str)
            + ":"
            + df_raw["other_allele"].astype(str).str.upper()
            + ":"
            + df_raw["effect_allele"].astype(str).str.upper()
        )
        qc["snp_source"] = "synthesized_chr:bp:OA:EA"

    # Optional N column. If absent, fill from per-ancestry total.
    if "n" in df_raw.columns:
        df["N"] = pd.to_numeric(df_raw["n"], errors="coerce")
        qc["n_source"] = "per_row_n_column"
    else:
        df["N"] = GIGASTROKE_N_TOTAL[ancestry]
        qc["n_source"] = (
            f"per_ancestry_total_from_SUMSTATS-UPGRADE.tsv ({GIGASTROKE_N_TOTAL[ancestry]})"
        )

    df = _coerce_canonical_dtypes(df)
    df = df[CANONICAL_COLS].copy()
    df["CHR"] = df["CHR"].astype(str)

    # MAF >= maf_min.
    maf = df["EAF"].where(df["EAF"] < 0.5, 1 - df["EAF"])
    keep_maf = maf >= maf_min
    n_dropped_maf = int((~keep_maf).sum())
    df = df.loc[keep_maf].reset_index(drop=True)

    # Palindromic SNP filter at MAF=[0.48, 0.52] band.
    n_pre_pal = len(df)
    df = _su.filter_palindromic_ambiguous(df)
    n_palindromic_dropped = n_pre_pal - len(df)

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
    ap.add_argument("--trait", default="stroke")
    ap.add_argument("--ancestry", required=True, choices=sorted(VALID_ANCESTRIES))
    ap.add_argument("--consortium", default="GIGASTROKE")
    ap.add_argument("--year", type=int, default=2022)
    ap.add_argument("--maf-min", type=float, default=0.005)
    args = ap.parse_args()

    harmonize_gigastroke(
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
