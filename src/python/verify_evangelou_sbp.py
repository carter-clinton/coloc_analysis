#!/usr/bin/env python3
"""D-10 + D-16 verify + rename of pre-pivot Evangelou 2018 SBP-EUR T1-spine file.

Asserts ``hypertension.EUR.tsv.bgz`` is (a) GRCh37 (every BP <= chrom max
+ tolerance), (b) 10-col canonical schema (after renaming source columns
``POS->BP, ALT->EA, REF->OA, SNP_ID->SNP``), (c) EAF/P in valid ranges.
On pass: copies bgzipped TSV + .tbi to D-16 name, builds .parquet,
writes .qc.json sidecar. On fail: raises ``AssertionError`` listing
specific defects and does NOT write any target file.

Source schema (observed at
``data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz``):
    CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD

Canonical 10-col schema (D-16):
    CHR BP SNP EA OA BETA SE P EAF N

Trait token D-16: ``sbp`` (per CONTEXT phenotype lock).
Target name: ``sbp.EUR.Evangelou-ICBP-UKBB.2018.GRCh37.tsv.bgz``.

phenotype_lock: "SBP continuous (mmHg), medication-adjusted"

Plan reference: m1-02b-harmonizers-case-control-traits-PLAN.md Task 2.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import sumstats_utils as _su  # noqa: E402

# b37 (hg19 primary assembly) per-chromosome max BP. Any value greater
# than CHR_MAX_B37[c] + tolerance implies the file is b38, not b37.
CHR_MAX_B37 = {
    1: 249250621, 2: 243199373, 3: 198022430, 4: 191154276,
    5: 180915260, 6: 171115067, 7: 159138663, 8: 146364022,
    9: 141213431, 10: 135534747, 11: 135006516, 12: 133851895,
    13: 115169878, 14: 107349540, 15: 102531392, 16: 90354753,
    17: 81195210, 18: 78077248, 19: 59128983, 20: 63025520,
    21: 48129895, 22: 51304566,
}
TOL_BP = 1000  # forgive ~1kb rounding at chromosome end.

# Source-column -> canonical-column rename map (Evangelou pre-pivot).
EVANGELOU_COL_MAP = {
    "CHR": "CHR",
    "POS": "BP",
    "SNP_ID": "SNP",
    "ALT": "EA",     # ALT is the effect allele in the pre-pivot file.
    "REF": "OA",
    "BETA": "BETA",
    "SE": "SE",
    "P": "P",
    "EAF": "EAF",
    "N": "N",
}


def _chrom_int(c) -> "int | None":
    s = str(c).replace("chr", "").upper()
    try:
        return int(s)
    except ValueError:
        return None


def verify_and_rename(
    source: Path,
    target_tsv_bgz: Path,
    target_parquet: Path,
    target_qc: Path,
) -> dict:
    """Verify source is b37 + canonical-conformant, then write D-16 outputs.

    Steps:
    1. Read ``source`` (bgzipped TSV via pandas ``compression='infer'``).
    2. Rename Evangelou pre-pivot columns to canonical 10-col schema.
    3. Validate canonical schema via :func:`sumstats_utils.validate_canonical_frame`.
    4. Spot-check every BP <= CHR_MAX_B37[chr] + TOL_BP (b37 invariant).
    5. Spot-check EAF in [0, 1] and P in [0, 1].
    6. On pass: copy source bgzip to ``target_tsv_bgz`` + .tbi sibling,
       write parquet, write qc.json. On fail: raise AssertionError;
       no target written.

    Returns
    -------
    dict
        QC dict (also written to ``target_qc`` as JSON).
    """
    # bgzip files have `.bgz` extension that pandas doesn't recognize via
    # `compression="infer"`; explicitly select gzip for .bgz / .gz / .bgzip
    # suffixes (bgzip is gzip-compatible at the stream level).
    src_name = str(source).lower()
    if src_name.endswith((".bgz", ".gz", ".bgzip", ".tsv.bgz", ".tsv.gz")):
        comp = "gzip"
    else:
        comp = "infer"
    df_raw = pd.read_csv(source, sep="\t", compression=comp, low_memory=False)

    # B-2 guard on the rename map.
    missing = [c for c in EVANGELOU_COL_MAP if c not in df_raw.columns]
    if missing:
        raise AssertionError(
            f"Evangelou verify FAILED: source missing columns {missing}. "
            f"Found: {sorted(df_raw.columns.tolist())}. "
            f"Expected EVANGELOU_COL_MAP keys: "
            f"{sorted(EVANGELOU_COL_MAP.keys())}."
        )
    df = df_raw[list(EVANGELOU_COL_MAP.keys())].rename(columns=EVANGELOU_COL_MAP)

    # Coerce dtypes for the validate_canonical_frame contract.
    for c in ("BP", "BETA", "SE", "P", "EAF", "N"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ("EA", "OA", "SNP"):
        df[c] = df[c].astype(str)
    df["EA"] = df["EA"].str.upper()
    df["OA"] = df["OA"].str.upper()
    df["CHR"] = df["CHR"].astype(str)

    _su.validate_canonical_frame(df)

    # b37 chromosome-length invariants.
    df["_chr_i"] = df["CHR"].map(_chrom_int)
    over_rows = []
    for chrom, max_bp in CHR_MAX_B37.items():
        sub = df[df["_chr_i"] == chrom]
        over = sub[sub["BP"] > max_bp + TOL_BP]
        if len(over) > 0:
            over_rows.append((chrom, int(len(over))))
    if over_rows:
        raise AssertionError(
            f"Evangelou build verify FAILED: BP > b37 max on {over_rows}. "
            f"File may be b38 — aborting rename."
        )

    if not df["EAF"].between(0, 1).all():
        bad_eaf = df[~df["EAF"].between(0, 1)].head(3)
        raise AssertionError(
            f"Evangelou verify FAILED: EAF out of [0, 1] on rows like:\n{bad_eaf}"
        )
    if not df["P"].between(0, 1).all():
        bad_p = df[~df["P"].between(0, 1)].head(3)
        raise AssertionError(
            f"Evangelou verify FAILED: P out of [0, 1] on rows like:\n{bad_p}"
        )

    df = df.drop(columns=["_chr_i"])

    target_tsv_bgz.parent.mkdir(parents=True, exist_ok=True)
    target_parquet.parent.mkdir(parents=True, exist_ok=True)
    target_qc.parent.mkdir(parents=True, exist_ok=True)

    # Copy source bgzipped TSV byte-for-byte (provenance preserved).
    shutil.copy2(source, target_tsv_bgz)
    tbi_src = source.parent / (source.name + ".tbi")
    tbi_dst = target_tsv_bgz.parent / (target_tsv_bgz.name + ".tbi")
    if tbi_src.exists():
        shutil.copy2(tbi_src, tbi_dst)

    # Write canonical 10-col parquet (drops the extra TRAIT/ANCESTRY/BUILD
    # tail columns from the pre-pivot file but preserves rows).
    df.to_parquet(target_parquet, index=False, compression="snappy")

    qc = {
        "source": str(source),
        "n_rows": int(len(df)),
        "build_verified": "GRCh37",
        "phenotype_lock": "SBP continuous (mmHg), medication-adjusted",
        "d16_name": target_tsv_bgz.name,
        "schema_valid": True,
        "tolerance_bp": TOL_BP,
    }
    target_qc.write_text(json.dumps(qc, indent=2) + "\n")
    return qc


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--source", type=Path,
        default=Path(
            "data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz"
        ),
    )
    ap.add_argument("--target-tsv-bgz", type=Path, required=True)
    ap.add_argument("--target-parquet", type=Path, required=True)
    ap.add_argument("--target-qc", type=Path, required=True)
    args = ap.parse_args()
    qc = verify_and_rename(
        source=args.source,
        target_tsv_bgz=args.target_tsv_bgz,
        target_parquet=args.target_parquet,
        target_qc=args.target_qc,
    )
    print(json.dumps(qc, indent=2))


if __name__ == "__main__":
    _main()
