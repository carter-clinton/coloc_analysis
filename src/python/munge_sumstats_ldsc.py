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
import os
import shutil
import subprocess
import sys
import tempfile
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


def _build_chrpos_to_rsid(bim_prefix: str, chromosomes=None) -> dict:
    """Build chr:pos → rsID lookup from 1000G plink bim files.

    Parameters
    ----------
    bim_prefix : str
        Path prefix for bim files (e.g. ".../1000G.EUR.QC").
        Files expected at {prefix}.{chr}.bim.
    chromosomes : list, optional
        Chromosomes to load (default: 1-22).

    Returns
    -------
    dict
        Mapping of "chr:pos" strings to rsID strings.
    """
    if chromosomes is None:
        chromosomes = [str(c) for c in range(1, 23)]
    lookup = {}
    for chrom in chromosomes:
        bim_path = f"{bim_prefix}.{chrom}.bim"
        try:
            with open(bim_path) as f:
                for line in f:
                    parts = line.split()
                    # bim format: CHR  rsID  CM  BP  A1  A2
                    key = f"{parts[0]}:{parts[3]}"
                    lookup[key] = parts[1]
        except FileNotFoundError:
            logger.warning("Bim file not found: %s, skipping chr%s", bim_path, chrom)
    logger.info("Built chr:pos → rsID lookup: %d entries from %s", len(lookup), bim_prefix)
    return lookup


def _snp_is_chrpos(snp_id: str) -> bool:
    """Check if a SNP ID is in chr:pos[:ref:alt] format.

    Accepts 2-token (``1:752566``) or 4-token (``1:729679:G:C``) variants;
    the 4-token form is GIGASTROKE 2022 + Aragam 2022 synthesis output
    from the M1 Wave 2b harmonizers (m1-02b).
    """
    if not snp_id or ":" not in snp_id:
        return False
    parts = snp_id.split(":")
    if len(parts) not in (2, 4):
        return False
    if not (parts[0].isdigit() and parts[1].isdigit()):
        return False
    return True


def _chrpos_key(snp_id: str) -> str:
    """Reduce a chr:pos[:ref:alt] SNP ID to its 2-token chr:pos key for lookup."""
    parts = snp_id.split(":")
    return f"{parts[0]}:{parts[1]}"


def convert_sumstats(
    input_path: str,
    output_path: str,
    trait: str = None,
    n_case: float = None,
    n_ctrl: float = None,
    n_override: float = None,
    bim_prefix: str = None,
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
    bim_prefix : str, optional
        Path prefix for 1000G bim files (e.g. ".../1000G.EUR.QC").
        Used to remap chr:pos SNP IDs to rsIDs when needed.

    Returns
    -------
    dict
        Stats: {n_input: int, n_output: int, n_filtered: int, n_remapped: int}.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    n_input = 0
    n_output = 0
    n_filtered = 0
    n_remapped = 0

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

        # Detect chr:pos SNP IDs by peeking at first non-empty SNP value.
        # If detected, build lookup from 1000G bim files to remap to rsIDs
        # (LDSC munge_sumstats.py --merge-alleles requires rsIDs).
        chrpos_lookup = None
        peek_pos = in_fh.tell()
        for peek_line in in_fh:
            peek_fields = peek_line.strip().split("\t")
            if len(peek_fields) > col_idx["SNP"]:
                peek_snp = peek_fields[col_idx["SNP"]]
                if peek_snp and peek_snp != "." and peek_snp != "NA":
                    if _snp_is_chrpos(peek_snp):
                        if bim_prefix:
                            logger.info(
                                "Detected chr:pos SNP IDs (e.g. '%s'). "
                                "Building rsID lookup from bim files.",
                                peek_snp,
                            )
                            chrpos_lookup = _build_chrpos_to_rsid(bim_prefix)
                        else:
                            logger.warning(
                                "Detected chr:pos SNP IDs but no bim_prefix "
                                "provided — SNPs will not merge with HapMap3."
                            )
                    break
        in_fh.seek(peek_pos)

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
                # Effect / other allele resolution. M1 D-16 harmonized files
                # ship EA/OA columns; pre-pivot Phase 09 files used REF/ALT
                # (where ALT is the effect allele). Prefer EA/OA when present
                # (m1-03 fix: previous default-A/G fallback silently zeroed
                # the LDSC output for D-16 inputs).
                if "EA" in col_idx and "OA" in col_idx:
                    a1 = fields[col_idx["EA"]]  # Effect allele -> A1
                    a2 = fields[col_idx["OA"]]  # Other allele -> A2
                elif "ALT" in col_idx and "REF" in col_idx:
                    a1 = fields[col_idx["ALT"]]  # Effect allele -> A1
                    a2 = fields[col_idx["REF"]]  # Other allele -> A2
                else:
                    # Last-resort dummy alleles (legacy Phase 5 behavior).
                    # A/G chosen (not A/T) because A/T is strand-ambiguous
                    # and LDSC filter_alleles() drops strand-ambiguous variants,
                    # which would silently zero out the output. A/G matches the
                    # run_hess.py dummy-allele convention.
                    a1 = "A"
                    a2 = "G"
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

                # Remap chr:pos[:ref:alt] → rsID if lookup is available
                if chrpos_lookup is not None:
                    lookup_key = _chrpos_key(snp) if _snp_is_chrpos(snp) else snp
                    rsid = chrpos_lookup.get(lookup_key)
                    if rsid is None:
                        n_filtered += 1
                        continue
                    snp = rsid
                    n_remapped += 1

                out_fh.write(
                    f"{snp}\t{a1}\t{a2}\t{row_n}\t{p}\t{beta}\t{se}\n"
                )
                n_output += 1

    return {
        "n_input": n_input, "n_output": n_output,
        "n_filtered": n_filtered, "n_remapped": n_remapped,
    }


def run_ldsc_munge_sumstats(
    pre_input: str,
    output_path: str,
    merge_alleles: str,
    chunksize: int = 500_000,
    n_override: float = None,
    n_case: float = None,
    n_ctrl: float = None,
    ldsc_python: str = None,
    munge_script: str = "tools/ldsc/munge_sumstats.py",
) -> None:
    """Drive LDSC's vendored ``tools/ldsc/munge_sumstats.py`` on a pre-staged
    LDSC-format TSV produced by ``convert_sumstats``.

    Output is the canonical LDSC-munged format (SNP A1 A2 N Z) with HM3
    SNP merging via ``--merge-alleles``.

    Parameters
    ----------
    pre_input : str
        Path to the LDSC pre-input TSV (SNP A1 A2 N P BETA SE) produced
        by ``convert_sumstats``.
    output_path : str
        Final ``.sumstats.gz`` target. munge_sumstats.py emits at
        ``<prefix>.sumstats.gz``; this function moves the result to
        ``output_path`` and cleans up the .log / .sumstats.gz at the
        prefix location.
    merge_alleles : str
        Path to ``data/external/ldscore/w_hm3.snplist``.
    chunksize : int
        --chunksize for munge_sumstats.py (D-12 spec: 500000).
    n_override, n_case, n_ctrl : float, optional
        Optional --N / --N-cas / --N-con overrides for munge_sumstats.py.
    ldsc_python : str, optional
        Python interpreter to use for munge_sumstats.py. Defaults to the
        current ``sys.executable`` if it has bitarray; falls back to
        ``LDSC_PYTHON`` env var. Must have bitarray + numpy + scipy + pandas
        (smoke_dev base lacks bitarray; use the auto-resolved
        snakemake-cached LDSC env when available).
    munge_script : str
        Path to ``tools/ldsc/munge_sumstats.py`` (vendored).
    """
    # Pick the LDSC-capable Python interpreter.
    if ldsc_python is None:
        ldsc_python = os.environ.get("LDSC_PYTHON", sys.executable)
    # Probe for bitarray availability.
    probe = subprocess.run(
        [ldsc_python, "-c", "import bitarray"],
        capture_output=True, text=True,
    )
    if probe.returncode != 0:
        # Fallback: check for the snakemake-cached LDSC env from m1-00.
        cached = (
            ".snakemake/conda/481e5f0b6ac97e63f5201cfab7469335_/bin/python"
        )
        if Path(cached).exists():
            ldsc_python = cached
        else:
            raise RuntimeError(
                f"LDSC munge requires a Python with bitarray; current "
                f"interpreter ({ldsc_python}) lacks it and the cached "
                f"snakemake env at {cached} is also absent. Set LDSC_PYTHON."
            )

    # munge_sumstats.py emits at <prefix>.sumstats.gz; collect prefix.
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if str(out_path).endswith(".sumstats.gz"):
        prefix = str(out_path)[: -len(".sumstats.gz")]
    elif str(out_path).endswith(".gz"):
        prefix = str(out_path)[: -len(".gz")].removesuffix(".sumstats")
    else:
        prefix = str(out_path)

    cmd = [
        ldsc_python, munge_script,
        "--sumstats", pre_input,
        "--out", prefix,
        "--merge-alleles", merge_alleles,
        "--chunksize", str(int(chunksize)),
        "--snp", "SNP",
        "--a1", "A1",
        "--a2", "A2",
        "--p", "P",
        "--signed-sumstats", "BETA,0",
        "--N-col", "N",
    ]
    if n_override is not None:
        cmd += ["--N", str(int(n_override))]
    if n_case is not None and n_ctrl is not None:
        cmd += ["--N-cas", str(int(n_case)), "--N-con", str(int(n_ctrl))]

    logger.info("Running LDSC munge_sumstats: %s", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    log_path = Path(prefix + ".log")
    log_path.write_text((res.stdout or "") + "\n--STDERR--\n" + (res.stderr or ""))

    if res.returncode != 0:
        raise RuntimeError(
            f"LDSC munge_sumstats.py failed (exit {res.returncode}). "
            f"See {log_path} for full output. STDERR tail:\n"
            f"{(res.stderr or '')[-2000:]}"
        )

    # Locate the produced .sumstats.gz; munge_sumstats.py emits at <prefix>.sumstats.gz.
    produced = Path(prefix + ".sumstats.gz")
    if not produced.exists():
        raise RuntimeError(
            f"munge_sumstats.py did not emit {produced}. Log at {log_path}."
        )

    # If output_path differs from prefix.sumstats.gz, move it.
    if str(produced) != str(out_path):
        shutil.move(str(produced), str(out_path))


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
        # Note: choices restriction removed in m1-03 to support D-16 trait
        # tokens (cad, ldl, hdl, tg, tc, egfr, hba1c, sbp). The
        # convert_sumstats helper validates trait against TRAIT_TYPE
        # internally; unrecognized traits route through the per-row-N path.
        help=("Trait name for effective-N calculation (binary traits). "
              "Recognized tokens: " + ",".join(sorted(TRAIT_TYPE.keys()))),
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
    parser.add_argument(
        "--bim-prefix",
        default=None,
        help="1000G bim prefix for chr:pos→rsID remapping (e.g. .../1000G.EUR.QC)",
    )
    parser.add_argument(
        "--merge-alleles",
        default=None,
        help=("Path to LDSC HM3 SNP list (e.g. data/external/ldscore/w_hm3.snplist). "
              "When supplied, the wrapper produces the LDSC pre-input TSV in a temp "
              "file then drives tools/ldsc/munge_sumstats.py to emit the final "
              "<output>.sumstats.gz. When omitted, only the pre-input format is "
              "written to --output (legacy Phase 5 behavior)."),
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=500_000,
        help="munge_sumstats.py --chunksize (D-12 spec: 500000).",
    )
    parser.add_argument(
        "--ldsc-python",
        default=None,
        help=("Python interpreter that has bitarray for tools/ldsc/munge_sumstats.py. "
              "Defaults to LDSC_PYTHON env or sys.executable; falls back to the "
              "snakemake-cached LDSC env at m1-00 baseline."),
    )
    args = parser.parse_args()

    if args.merge_alleles is None:
        # Legacy single-step path: wrapper writes the LDSC pre-input format.
        stats = convert_sumstats(
            input_path=args.input,
            output_path=args.output,
            trait=args.trait,
            n_case=args.n_case,
            n_ctrl=args.n_ctrl,
            n_override=args.n_override,
            bim_prefix=args.bim_prefix,
        )

        logger.info(
            "Converted %d/%d variants (%d filtered) to %s",
            stats["n_output"], stats["n_input"], stats["n_filtered"], args.output,
        )
        return

    # Two-step path: (1) wrapper -> LDSC pre-input TSV, (2) munge_sumstats.py -> .sumstats.gz.
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        suffix="_ldsc_pre.tsv.gz", delete=False, dir=str(Path(args.output).parent)
    ) as tmp:
        pre_input = tmp.name

    try:
        stats = convert_sumstats(
            input_path=args.input,
            output_path=pre_input,
            trait=args.trait,
            n_case=args.n_case,
            n_ctrl=args.n_ctrl,
            n_override=args.n_override,
            bim_prefix=args.bim_prefix,
        )
        logger.info(
            "Pre-converted %d/%d variants (%d filtered) to %s",
            stats["n_output"], stats["n_input"], stats["n_filtered"], pre_input,
        )

        run_ldsc_munge_sumstats(
            pre_input=pre_input,
            output_path=args.output,
            merge_alleles=args.merge_alleles,
            chunksize=args.chunksize,
            n_override=args.n_override,
            n_case=args.n_case,
            n_ctrl=args.n_ctrl,
            ldsc_python=args.ldsc_python,
        )
        logger.info("LDSC-munged output: %s", args.output)
    finally:
        try:
            os.unlink(pre_input)
        except OSError:
            pass


if __name__ == "__main__":
    main()
