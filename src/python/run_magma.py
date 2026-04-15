#!/usr/bin/env python3
"""MAGMA three-step wrapper: annotate, gene analysis, gene-set analysis.

Provides a unified CLI for the MAGMA v1.10 pipeline:
  Step 1 (annotate): Map SNPs to genes using gene.loc and SNP positions.
  Step 2 (gene):     Gene-level p-values from GWAS summary statistics.
  Step 3 (geneset):  Competitive gene-set enrichment testing.

All subprocess calls use list arguments (NOT shell=True) per T-05-05.
All input files are validated with os.path.exists before MAGMA invocation.

Usage:
    python run_magma.py --step annotate --magma-binary PATH --snp-loc BIM --gene-loc GENE_LOC --out OUT
    python run_magma.py --step gene --magma-binary PATH --bfile PLINK --pval SUMSTATS \
        --gene-annot ANNOT --sample-size N --out OUT
    python run_magma.py --step geneset --magma-binary PATH --gene-results RAW --set-annot SET --out OUT

References:
    de Leeuw et al. 2015 PLoS Comput Biol (MAGMA)
    MAGMA manual v1.10: ctg.cncr.nl/software/MAGMA/doc/manual_v1.10.pdf
"""
import argparse
import gzip
import io
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _open_sumstats(path: str):
    """Open a sumstats file, transparently handling .bgz/.gz compression.

    Harmonized sumstats are bgzipped (`{trait}.{ancestry}.tsv.bgz`), and
    BGZF is gzip-compatible. Returns a text-mode file handle.
    """
    if path.endswith(".bgz") or path.endswith(".gz"):
        return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8")
    return open(path, "r", encoding="utf-8")

# Allow importing shared module from same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sumstats_utils import TRAIT_TYPE, compute_effective_n

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _validate_file(path: str, label: str) -> None:
    """Validate that an input file exists and is non-empty.

    Parameters
    ----------
    path : str
        File path to validate.
    label : str
        Descriptive label for error messages.

    Raises
    ------
    FileNotFoundError
        If the file does not exist or is empty.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"{label} not found: {path}")
    if os.path.isfile(path) and os.path.getsize(path) == 0:
        raise FileNotFoundError(f"{label} is empty: {path}")


def _run_command(cmd: list, step_name: str) -> subprocess.CompletedProcess:
    """Run a subprocess command with logging and error handling.

    Parameters
    ----------
    cmd : list
        Command as a list of strings (no shell=True).
    step_name : str
        Name of the MAGMA step for logging.

    Returns
    -------
    subprocess.CompletedProcess
        Completed process result.

    Raises
    ------
    subprocess.CalledProcessError
        If the command exits with non-zero status.
    """
    logger.info("Running MAGMA %s: %s", step_name, " ".join(cmd))
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        logger.error("MAGMA %s failed (exit %d)", step_name, result.returncode)
        logger.error("STDOUT:\n%s", result.stdout)
        logger.error("STDERR:\n%s", result.stderr)
        raise subprocess.CalledProcessError(
            result.returncode, cmd, result.stdout, result.stderr
        )
    logger.info("MAGMA %s completed successfully", step_name)
    if result.stdout:
        logger.debug("STDOUT:\n%s", result.stdout)
    return result


def effective_n(
    trait: str = None,
    sample_size: float = None,
    n_case: float = None,
    n_ctrl: float = None,
) -> float:
    """Compute effective sample size for MAGMA gene analysis.

    For quantitative traits, returns sample_size directly.
    For binary traits (T2D, hypertension, asthma, stroke), computes:
        N_eff = 4 / (1/n_case + 1/n_ctrl)

    Parameters
    ----------
    trait : str, optional
        Trait name for automatic type lookup in TRAIT_TYPE.
    sample_size : float, optional
        Total sample size (used for quantitative traits).
    n_case : float, optional
        Number of cases (required for binary traits).
    n_ctrl : float, optional
        Number of controls (required for binary traits).

    Returns
    -------
    float
        Effective sample size for MAGMA.

    Raises
    ------
    ValueError
        If required arguments are missing or invalid.
    """
    if trait and trait.lower() in TRAIT_TYPE:
        trait_type = TRAIT_TYPE[trait.lower()]
        if trait_type == "binary":
            if n_case is None or n_ctrl is None:
                raise ValueError(
                    f"Binary trait '{trait}' requires --n-case and --n-ctrl"
                )
            return compute_effective_n(n_case, n_ctrl)
        else:
            if sample_size is None:
                raise ValueError(
                    f"Quantitative trait '{trait}' requires --sample-size"
                )
            return float(sample_size)
    # No trait specified -- use explicit sample_size
    if sample_size is not None:
        return float(sample_size)
    if n_case is not None and n_ctrl is not None:
        return compute_effective_n(n_case, n_ctrl)
    raise ValueError("Must provide --sample-size or both --n-case and --n-ctrl")


def _create_pval_file(sumstats_path: str, tmpdir: str) -> str:
    """Extract SNP + P columns from harmonized sumstats for MAGMA.

    MAGMA --pval expects a whitespace-delimited file with at minimum
    SNP and P columns. We extract only these to avoid MAGMA choking
    on extra columns in harmonized sumstats.

    Parameters
    ----------
    sumstats_path : str
        Path to harmonized sumstats TSV.
    tmpdir : str
        Directory for the temporary pval file.

    Returns
    -------
    str
        Path to the temporary SNP+P file.

    Raises
    ------
    ValueError
        If SNP or P columns are not found in the input file.
    """
    pval_path = os.path.join(tmpdir, "magma_pval_input.txt")

    with _open_sumstats(sumstats_path) as fin:
        header_line = fin.readline().strip()
        columns = header_line.split("\t")

        # Find SNP and P column indices (case-insensitive).
        # Accept "SNP" (canonical harmonize_sumstats schema) or "SNP_ID"
        # (legacy harmonized files produced before the schema convergence).
        col_lower = [c.lower() for c in columns]
        snp_idx = None
        p_idx = None
        for i, c in enumerate(col_lower):
            if c in ("snp", "snp_id"):
                snp_idx = i
            elif c == "p":
                p_idx = i

        if snp_idx is None:
            raise ValueError(
                f"Column 'SNP' or 'SNP_ID' not found in {sumstats_path}. "
                f"Available columns: {columns}"
            )
        if p_idx is None:
            raise ValueError(
                f"Column 'P' not found in {sumstats_path}. "
                f"Available columns: {columns}"
            )

        n_written = 0
        with open(pval_path, "w") as fout:
            fout.write("SNP\tP\n")
            for line in fin:
                fields = line.strip().split("\t")
                if len(fields) > max(snp_idx, p_idx):
                    snp_val = fields[snp_idx]
                    p_val = fields[p_idx]
                    # Skip rows with missing values
                    if snp_val and p_val and p_val.lower() != "na":
                        fout.write(f"{snp_val}\t{p_val}\n")
                        n_written += 1

    logger.info(
        "Created MAGMA pval file with %d SNPs: %s", n_written, pval_path
    )
    return pval_path


def run_annotate(
    magma_binary: str,
    snp_loc: str,
    gene_loc: str,
    out: str,
) -> str:
    """MAGMA Step 1: Annotate SNPs to genes.

    Runs: magma --annotate --snp-loc {snp_loc} --gene-loc {gene_loc} --out {out}
    Produces: {out}.genes.annot

    Parameters
    ----------
    magma_binary : str
        Path to MAGMA binary.
    snp_loc : str
        Path to SNP location file (e.g., g1000_eur.bim).
    gene_loc : str
        Path to gene location file (e.g., NCBI37.3.gene.loc).
    out : str
        Output prefix.

    Returns
    -------
    str
        Path to the genes.annot output file.
    """
    _validate_file(magma_binary, "MAGMA binary")
    _validate_file(snp_loc, "SNP location file")
    _validate_file(gene_loc, "Gene location file")

    # Ensure output directory exists
    Path(out).parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        magma_binary,
        "--annotate",
        "--snp-loc", snp_loc,
        "--gene-loc", gene_loc,
        "--out", out,
    ]
    _run_command(cmd, "annotate")
    return f"{out}.genes.annot"


def run_gene_analysis(
    magma_binary: str,
    bfile: str,
    pval: str,
    gene_annot: str,
    out: str,
    sample_size: float = None,
    n_case: float = None,
    n_ctrl: float = None,
    trait: str = None,
) -> str:
    """MAGMA Step 2: Gene-level analysis from GWAS summary statistics.

    Runs: magma --bfile {bfile} --pval {pval_file} N={n} --gene-annot {gene_annot} --out {out}

    For binary traits (T2D, hypertension, asthma, stroke), computes effective N
    using the formula: N_eff = 4 / (1/n_case + 1/n_ctrl) per Pitfall 4.

    Parameters
    ----------
    magma_binary : str
        Path to MAGMA binary.
    bfile : str
        Plink bfile prefix (expects .bed/.bim/.fam).
    pval : str
        Path to harmonized sumstats file (will extract SNP+P columns).
    gene_annot : str
        Path to gene annotation file from Step 1.
    out : str
        Output prefix.
    sample_size : float, optional
        Total sample size (for quantitative traits).
    n_case : float, optional
        Number of cases (for binary traits).
    n_ctrl : float, optional
        Number of controls (for binary traits).
    trait : str, optional
        Trait name for automatic binary/quantitative detection.

    Returns
    -------
    str
        Path to the .genes.raw output file.
    """
    _validate_file(magma_binary, "MAGMA binary")
    _validate_file(f"{bfile}.bed", "Plink BED file")
    _validate_file(pval, "Summary statistics file")
    _validate_file(gene_annot, "Gene annotation file")

    # Compute effective N
    n_eff = effective_n(
        trait=trait,
        sample_size=sample_size,
        n_case=n_case,
        n_ctrl=n_ctrl,
    )
    logger.info("Using effective N = %.1f for MAGMA gene analysis", n_eff)

    # Ensure output directory exists
    Path(out).parent.mkdir(parents=True, exist_ok=True)

    # Create temp pval file with only SNP + P columns
    tmpdir = tempfile.mkdtemp(prefix="magma_pval_")
    try:
        pval_file = _create_pval_file(pval, tmpdir)

        cmd = [
            magma_binary,
            "--bfile", bfile,
            "--pval", pval_file, f"N={int(n_eff)}",
            "--gene-annot", gene_annot,
            "--out", out,
        ]
        _run_command(cmd, "gene analysis")
    finally:
        # T-05-11: Clean up temp pval file (contains only SNP + P, no individual data)
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

    return f"{out}.genes.raw"


def run_geneset_analysis(
    magma_binary: str,
    gene_results: str,
    set_annot: str,
    out: str,
) -> str:
    """MAGMA Step 3: Gene-set (competitive) enrichment analysis.

    Runs: magma --gene-results {gene_results} --set-annot {set_annot} --out {out}
    Produces: {out}.gsa.out with BETA, BETA_STD, SE, P per gene set.

    Parameters
    ----------
    magma_binary : str
        Path to MAGMA binary.
    gene_results : str
        Path to gene results from Step 2 (.genes.raw).
    set_annot : str
        Path to gene set annotation file (.set format).
    out : str
        Output prefix.

    Returns
    -------
    str
        Path to the .gsa.out output file.
    """
    _validate_file(magma_binary, "MAGMA binary")
    _validate_file(gene_results, "Gene results file")
    _validate_file(set_annot, "Gene set annotation file")

    # Ensure output directory exists
    Path(out).parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        magma_binary,
        "--gene-results", gene_results,
        "--set-annot", set_annot,
        "--out", out,
    ]
    _run_command(cmd, "gene-set analysis")
    return f"{out}.gsa.out"


def main():
    """CLI entry point for MAGMA three-step wrapper."""
    parser = argparse.ArgumentParser(
        description="MAGMA three-step pipeline wrapper (annotate, gene, geneset)"
    )
    parser.add_argument(
        "--step",
        required=True,
        choices=["annotate", "gene", "geneset"],
        help="Which MAGMA step to run",
    )
    parser.add_argument(
        "--magma-binary",
        required=True,
        help="Path to MAGMA v1.10 binary",
    )
    parser.add_argument(
        "--snp-loc",
        help="SNP location file, e.g. g1000_eur.bim (annotate step)",
    )
    parser.add_argument(
        "--gene-loc",
        help="Gene location file, e.g. NCBI37.3.gene.loc (annotate step)",
    )
    parser.add_argument(
        "--bfile",
        help="Plink bfile prefix (gene step)",
    )
    parser.add_argument(
        "--pval",
        help="Path to harmonized sumstats TSV (gene step)",
    )
    parser.add_argument(
        "--gene-annot",
        help="Gene annotation file from annotate step (gene step)",
    )
    parser.add_argument(
        "--sample-size",
        type=float,
        help="Total sample size for quantitative traits (gene step)",
    )
    parser.add_argument(
        "--n-case",
        type=float,
        help="Number of cases for binary traits (gene step)",
    )
    parser.add_argument(
        "--n-ctrl",
        type=float,
        help="Number of controls for binary traits (gene step)",
    )
    parser.add_argument(
        "--trait",
        help="Trait name for automatic binary/quantitative detection (gene step)",
    )
    parser.add_argument(
        "--gene-results",
        help="Gene results .genes.raw file (geneset step)",
    )
    parser.add_argument(
        "--set-annot",
        help="Gene set annotation .set file (geneset step)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output prefix",
    )

    args = parser.parse_args()

    if args.step == "annotate":
        if not args.snp_loc or not args.gene_loc:
            parser.error("--snp-loc and --gene-loc required for annotate step")
        run_annotate(args.magma_binary, args.snp_loc, args.gene_loc, args.out)

    elif args.step == "gene":
        if not args.bfile or not args.pval or not args.gene_annot:
            parser.error(
                "--bfile, --pval, and --gene-annot required for gene step"
            )
        run_gene_analysis(
            magma_binary=args.magma_binary,
            bfile=args.bfile,
            pval=args.pval,
            gene_annot=args.gene_annot,
            out=args.out,
            sample_size=args.sample_size,
            n_case=args.n_case,
            n_ctrl=args.n_ctrl,
            trait=args.trait,
        )

    elif args.step == "geneset":
        if not args.gene_results or not args.set_annot:
            parser.error(
                "--gene-results and --set-annot required for geneset step"
            )
        run_geneset_analysis(
            args.magma_binary, args.gene_results, args.set_annot, args.out
        )


if __name__ == "__main__":
    main()
