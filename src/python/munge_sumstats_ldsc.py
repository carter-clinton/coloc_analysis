#!/usr/bin/env python3
"""Convert project harmonized GWAS sumstats to LDSC-compatible format.

Reads the harmonized TSV format (columns: CHR, POS, SNP, REF, ALT, BETA,
SE, P, EAF, N) and outputs LDSC munge_sumstats.py input format (columns:
SNP, A1, A2, N, P, BETA, SE).

For binary traits, computes effective N via sumstats_utils.compute_effective_n
to avoid double-counting imbalanced case/control ratios.

Usage:
    python munge_sumstats_ldsc.py \\
        --input data/processed/sumstats_harmonized/bmi.EUR.tsv.bgz \\
        --output results/pathway/ldsc_munged/bmi.EUR.sumstats.gz \\
        --trait bmi

    python munge_sumstats_ldsc.py \\
        --input data/processed/sumstats_harmonized/t2d.EUR.tsv.bgz \\
        --output results/pathway/ldsc_munged/t2d.EUR.sumstats.gz \\
        --trait t2d \\
        --n-case 74124 --n-ctrl 824006

T-05-04 mitigation: validates required input columns before conversion;
rejects files missing SNP, P, BETA, or SE with explicit error message.
"""
import argparse
import gzip
import logging
import sys
from pathlib import Path

# Import shared effective-N logic (NOT reimplemented locally per D-01b)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sumstats_utils import TRAIT_TYPE, get_effective_n

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Required columns in harmonized input (REF/ALT optional — some sumstats
# like Yengo 2018 bmi.EUR lack alleles; LDSC merge-alleles reconciles via SNP ID)
REQUIRED_INPUT_COLS = {"SNP", "BETA", "SE", "P", "N"}

# LDSC output column order
LDSC_COLS = ["SNP", "A1", "A2", "N", "P", "BETA", "SE"]


def open_maybe_gzip(path: str, mode: str = "rt"):
    """Open a file, auto-detecting gzip by extension."""
    if path.endswith(".gz") or path.endswith(".bgz"):
        return gzip.open(path, mode)
    return open(path, mode)


def convert_sumstats(
    input_path: str,
    output_path: str,
    trait: str = None,
    n_case: float = None,
    n_ctrl: float = None,
    n_override: float = None,
) -> dict:
    """Convert harmonized sumstats to LDSC format.

    Parameters
    ----------
    input_path : str
        Path to harmonized sumstats TSV (may be gzipped/bgzipped).
    output_path : str
        Output path (.gz for gzip, plain otherwise).
    trait : str, optional
        Trait name for effective-N calculation. If None, uses N column directly.
    n_case : float, optional
        Number of cases (required for binary traits).
    n_ctrl : float, optional
        Number of controls (required for binary traits).
    n_override : float, optional
        If set, use this N for all rows (overrides per-row N and effective-N).

    Returns
    -------
    dict
        Stats: {n_input: int, n_output: int, n_filtered: int}.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    n_input = 0
    n_output = 0
    n_filtered = 0

    with open_maybe_gzip(input_path) as in_fh:
        header_line = in_fh.readline().strip()
        in_cols = header_line.split("\t")
        col_idx = {col: i for i, col in enumerate(in_cols)}

        # Accept SNP_ID as alias for SNP (canonical harmonized column name)
        if "SNP" not in in_cols and "SNP_ID" in in_cols:
            col_idx["SNP"] = col_idx["SNP_ID"]

        # T-05-04: validate required columns (check col_idx keys, not in_cols,
        # so aliases are recognized without inflating the column count)
        missing = REQUIRED_INPUT_COLS - set(col_idx.keys())
        if missing:
            logger.error(
                "Input file missing required columns: %s. Found: %s",
                ", ".join(sorted(missing)),
                ", ".join(in_cols),
            )
            sys.exit(1)

        # Determine effective N
        use_effective_n = (
            trait is not None
            and trait in TRAIT_TYPE
            and TRAIT_TYPE[trait] == "binary"
            and n_case is not None
            and n_ctrl is not None
        )
        if use_effective_n:
            eff_n = get_effective_n(trait, 0, n_case, n_ctrl)
            logger.info(
                "Binary trait '%s': effective N = %.1f (n_case=%d, n_ctrl=%d)",
                trait,
                eff_n,
                int(n_case),
                int(n_ctrl),
            )

        open_out = gzip.open if output_path.endswith(".gz") else open
        with open_out(output_path, "wt") as out_fh:
            out_fh.write("\t".join(LDSC_COLS) + "\n")

            for line in in_fh:
                n_input += 1
                fields = line.strip().split("\t")
                if len(fields) < len(in_cols):
                    n_filtered += 1
                    continue

                snp = fields[col_idx["SNP"]]
                # REF/ALT optional — use dummy alleles when absent (LDSC
                # merge-alleles reconciles via SNP ID from w_hm3.snplist)
                if "ALT" in col_idx and "REF" in col_idx:
                    a1 = fields[col_idx["ALT"]]  # Effect allele -> A1
                    a2 = fields[col_idx["REF"]]  # Other allele -> A2
                else:
                    a1 = "A"
                    a2 = "T"
                beta = fields[col_idx["BETA"]]
                se = fields[col_idx["SE"]]
                p = fields[col_idx["P"]]

                # Determine N for this row
                if n_override is not None:
                    row_n = str(int(n_override))
                elif use_effective_n:
                    row_n = str(int(round(eff_n)))
                else:
                    row_n = fields[col_idx["N"]]

                # Filter: skip missing/invalid values
                try:
                    p_val = float(p)
                    if p_val <= 0 or p_val > 1:
                        n_filtered += 1
                        continue
                except (ValueError, TypeError):
                    n_filtered += 1
                    continue

                # Skip missing SNP IDs
                if not snp or snp == "." or snp == "NA":
                    n_filtered += 1
                    continue

                out_fh.write(
                    f"{snp}\t{a1}\t{a2}\t{row_n}\t{p}\t{beta}\t{se}\n"
                )
                n_output += 1

    return {"n_input": n_input, "n_output": n_output, "n_filtered": n_filtered}


def main():
    parser = argparse.ArgumentParser(
        description="Convert harmonized GWAS sumstats to LDSC munge_sumstats input"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input harmonized sumstats TSV (may be .gz or .bgz)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output LDSC format file (.gz for gzip)",
    )
    parser.add_argument(
        "--trait",
        default=None,
        choices=list(TRAIT_TYPE.keys()),
        help="Trait name for effective-N calculation (binary traits)",
    )
    parser.add_argument(
        "--n-case",
        type=float,
        default=None,
        help="Number of cases (required for binary traits)",
    )
    parser.add_argument(
        "--n-ctrl",
        type=float,
        default=None,
        help="Number of controls (required for binary traits)",
    )
    parser.add_argument(
        "--n-override",
        type=float,
        default=None,
        help="Override N for all rows (ignores per-row N and effective-N)",
    )
    args = parser.parse_args()

    stats = convert_sumstats(
        input_path=args.input,
        output_path=args.output,
        trait=args.trait,
        n_case=args.n_case,
        n_ctrl=args.n_ctrl,
        n_override=args.n_override,
    )

    logger.info(
        "Converted %d/%d variants (%d filtered) to %s",
        stats["n_output"],
        stats["n_input"],
        stats["n_filtered"],
        args.output,
    )


if __name__ == "__main__":
    main()
