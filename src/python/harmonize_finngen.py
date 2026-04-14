#!/usr/bin/env python3
"""FinnGen R12 TSV.gz -> canonical harmonized sumstats (Plan 09-02 Task 2).

Reads a FinnGen R12 per-endpoint summary-stats file (gzipped TSV, GRCh38),
renames to the canonical 10-column schema, lifts over to GRCh37, and
applies the palindromic-SNP ambiguity filter (RESEARCH pitfalls #1 + #2).

Output columns (canonical):
    CHR BP SNP EA OA BETA SE P EAF N [N_CASES N_CTRLS] palindromic_flag

FinnGen R12 raw schema (per config/replication_cohorts.yaml):
    #chrom pos ref alt rsids nearest_genes pval mlogp beta sebeta
    af_alt af_alt_cases af_alt_controls
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

# Allow running as a module (python -m src.python.harmonize_finngen) or as
# a standalone script. Imports follow the repo-wide convention used by the
# Phase 2 harmonizers — `sys.path.insert` + flat module name.
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import sumstats_utils as _su  # noqa: E402

CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]


def harmonize_finngen_sumstats(
    input_gz: Path,
    output_gz: Path,
    chain_file: Path,
    trait: str,
    case_n: int,
    ctrl_n: int | None = None,
    qc_out: Path | None = None,
) -> dict:
    """Harmonize a FinnGen R12 per-endpoint file to canonical schema.

    Parameters
    ----------
    input_gz : Path
        FinnGen R12 ``finngen_R12_{endpoint}.tsv.gz`` file (GRCh38).
    output_gz : Path
        Output path for the harmonized (GRCh37) gzipped TSV.
    chain_file : Path
        UCSC ``hg38ToHg19.over.chain.gz`` chain file.
    trait : str
        Phase-9 trait label (e.g. ``t2d``).
    case_n : int
        Number of cases reported by FinnGen for this endpoint.
    ctrl_n : int, optional
        Number of controls. When omitted it defaults to ``case_n`` (rough
        approximation; the FinnGen R12 manifest should always supply both).
    qc_out : Path, optional
        Path for a JSON QC report. Not written when ``None``.

    Returns
    -------
    dict
        QC statistics: ``n_input``, ``n_lifted``, ``n_dropped``,
        ``drop_rate`` (all from the liftover step), plus
        ``n_after_palindromic``, ``n_palindromic_dropped``, ``trait``,
        ``cohort="finngen_r12"``.
    """
    df = pd.read_csv(input_gz, sep="\t", compression="gzip", low_memory=False)
    df = df.rename(
        columns={
            "#chrom": "CHR",
            "pos": "BP",
            "rsids": "SNP",
            "ref": "OA",
            "alt": "EA",
            "beta": "BETA",
            "sebeta": "SE",
            "pval": "P",
            "af_alt": "EAF",
        }
    )

    # Attach N. FinnGen endpoint files don't carry per-variant N, so we use
    # the reported case_n (+ ctrl_n when supplied). Downstream meta-analysis
    # can override via trait metadata if needed.
    if ctrl_n is None:
        n_total = int(case_n)
    else:
        n_total = int(case_n) + int(ctrl_n)
    df["N"] = n_total
    df["N_CASES"] = int(case_n)
    if ctrl_n is not None:
        df["N_CTRLS"] = int(ctrl_n)

    extra_cols = [c for c in ("N_CASES", "N_CTRLS") if c in df.columns]
    df = df[CANONICAL_COLS + extra_cols]

    # Liftover GRCh38 -> GRCh37 (RESEARCH pitfall #1).
    df_lifted, liftover_qc = _su.liftover_to_grch37(df, str(chain_file))

    # Palindromic-ambiguous exclusion (RESEARCH pitfall #2).
    n_before_pal = len(df_lifted)
    df_out = _su.filter_palindromic_ambiguous(df_lifted)
    n_after_pal = len(df_out)

    qc: dict = {
        "cohort": "finngen_r12",
        "trait": trait,
        **liftover_qc,
        "n_after_palindromic": int(n_after_pal),
        "n_palindromic_dropped": int(n_before_pal - n_after_pal),
    }

    Path(output_gz).parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_gz, sep="\t", index=False, compression="gzip")

    if qc_out is not None:
        Path(qc_out).parent.mkdir(parents=True, exist_ok=True)
        Path(qc_out).write_text(json.dumps(qc, indent=2))

    return qc


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="FinnGen R12 tsv.gz")
    ap.add_argument("--output", required=True, help="Harmonized tsv.gz (GRCh37)")
    ap.add_argument("--chain-file", required=True, help="hg38ToHg19.over.chain.gz")
    ap.add_argument("--trait", required=True)
    ap.add_argument("--case-n", type=int, required=True)
    ap.add_argument("--ctrl-n", type=int, default=None)
    ap.add_argument("--qc-out", default=None)
    args = ap.parse_args()

    harmonize_finngen_sumstats(
        Path(args.input),
        Path(args.output),
        Path(args.chain_file),
        trait=args.trait,
        case_n=args.case_n,
        ctrl_n=args.ctrl_n,
        qc_out=Path(args.qc_out) if args.qc_out else None,
    )


if __name__ == "__main__":
    _main()
