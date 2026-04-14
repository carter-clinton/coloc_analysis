#!/usr/bin/env python3
"""BBJ hum0197-v3 zip -> canonical harmonized sumstats (Plan 09-02 Task 5).

BBJ is always GRCh38 on NBDC -> liftover to GRCh37 is required.
Raw zip payload is a REGENIE-style TSV; palindromic-ambiguity filter
applied after liftover (RESEARCH pitfalls #1 + #2).

Zip extractor (extract_bbj_zip) skips README* entries and picks the first
.tsv / .txt entry; BBJ zips are ≤ 2 GB per RESEARCH §9 so no zip-bomb
concern, but the 'known filename pattern' mitigation for T-09-10 lives
here.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Optional

import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import sumstats_utils as _su  # noqa: E402

CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]


def extract_bbj_zip(zip_path: Path, out_dir: Path) -> Path:
    """Extract the sumstats TSV from a BBJ hum0197-v3 zip.

    Returns the path of the extracted payload file (first entry whose
    filename ends in .tsv or .txt and does NOT contain 'readme').

    Raises
    ------
    ValueError
        When no .tsv/.txt payload can be found in the zip.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        candidates = [
            n
            for n in zf.namelist()
            if n.lower().endswith((".tsv", ".txt"))
            and "readme" not in n.lower()
        ]
        if not candidates:
            raise ValueError(
                f"{zip_path}: no .tsv/.txt file found in zip (entries: "
                f"{zf.namelist()})"
            )
        zf.extractall(out_dir)
        return out_dir / candidates[0]


def harmonize_bbj_sumstats(
    input_file: Path,
    output_gz: Path,
    chain_file: Path,
    trait: str,
    trait_code: str,
    qc_out: Optional[Path] = None,
) -> dict:
    """Harmonize an extracted BBJ sumstats TSV to canonical schema.

    Parameters
    ----------
    input_file : Path
        Extracted BBJ TSV (from :func:`extract_bbj_zip`).
    output_gz : Path
        Output path for harmonized (GRCh37) gzipped TSV.
    chain_file : Path
        ``hg38ToHg19.over.chain.gz``.
    trait : str
        Phase-9 trait label (e.g., ``t2d``).
    trait_code : str
        BBJ trait code (e.g., ``T2D``, ``IS``, ``SBP``).
    qc_out : Path, optional
        JSON QC report destination.
    """
    # BBJ sometimes uses whitespace-delimited files; sep=None triggers the
    # Python csv sniffer, which handles tab/space transparently. The python
    # engine does not accept the low_memory flag, hence the explicit omit.
    df = pd.read_csv(input_file, sep=None, engine="python")
    df = df.rename(
        columns={
            "CHR": "CHR",
            "POS": "BP",
            "SNPID": "SNP",
            "Allele1": "OA",
            "Allele2": "EA",
            "AF": "EAF",
            "Beta": "BETA",
            "SE": "SE",
            "p.value": "P",
            "N": "N",
        }
    )
    df = df[CANONICAL_COLS]

    # Liftover GRCh38 -> GRCh37 (required for BBJ)
    df_lifted, liftover_qc = _su.liftover_to_grch37(df, str(chain_file))

    # Palindromic-ambiguity filter
    n_before_pal = len(df_lifted)
    df_out = _su.filter_palindromic_ambiguous(df_lifted)
    n_after_pal = len(df_out)

    qc: dict = {
        "cohort": "bbj_hum0197_v3",
        "trait": trait,
        "trait_code": trait_code,
        **liftover_qc,
        "n_after_palindromic": int(n_after_pal),
        "n_palindromic_dropped": int(n_before_pal - n_after_pal),
        "n_output": int(n_after_pal),
    }

    Path(output_gz).parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_gz, sep="\t", index=False, compression="gzip")

    if qc_out is not None:
        Path(qc_out).parent.mkdir(parents=True, exist_ok=True)
        Path(qc_out).write_text(json.dumps(qc, indent=2))

    return qc


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--chain-file", required=True)
    ap.add_argument("--trait", required=True)
    ap.add_argument("--trait-code", required=True)
    ap.add_argument("--qc-out", default=None)
    args = ap.parse_args()

    harmonize_bbj_sumstats(
        Path(args.input),
        Path(args.output),
        Path(args.chain_file),
        args.trait,
        args.trait_code,
        qc_out=Path(args.qc_out) if args.qc_out else None,
    )


if __name__ == "__main__":
    _main()
