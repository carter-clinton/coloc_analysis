#!/usr/bin/env python3
"""LDSC-SEG tissue-specific heritability enrichment wrapper.

Provides a CLI for running LDSC cell-type-specific analysis (--h2-cts)
using pre-built tissue annotation files from Finucane 2018:
  1. GTEx v8 53-tissue RNA-seq gene expression annotations
  2. Roadmap Epigenomics chromatin state annotations

Also includes:
  - .ldcts path fixing for downloaded files (T-05-13 / Pitfall 8)
  - Shared tissue identification across trait pairs (D-05b)
  - Results parsing for .cell_type_results.txt output

All subprocess calls use list arguments (NOT shell=True) per T-05-14.
All input files validated with os.path.exists before LDSC invocation.

References:
    Finucane et al. 2018 Nat Genet (LDSC-SEG)
    Bulik-Sullivan et al. 2015 Nat Genet (LDSC)

Usage:
    python run_ldsc_seg.py \\
        --ldsc-dir tools/ldsc \\
        --sumstats munged.sumstats.gz \\
        --ref-ld-chr baseline_v2.2/baselineLD. \\
        --w-ld-chr weights. \\
        --ldcts-file Multi_tissue_gene_expr.ldcts \\
        --out trait_tissue

    python run_ldsc_seg.py --fix-ldcts-paths \\
        --ldcts-file Multi_tissue_gene_expr.ldcts \\
        --ldcts-out Multi_tissue_gene_expr_fixed.ldcts \\
        --annot-dir data/reference/ldsc_seg/Multi_tissue_gene_expr
"""
import argparse
import csv
import logging
import os
import subprocess
import sys
from pathlib import Path

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
        Command as list of strings (no shell=True).
    step_name : str
        Descriptive name for logging.

    Returns
    -------
    subprocess.CompletedProcess
        Completed process result.

    Raises
    ------
    subprocess.CalledProcessError
        If the command exits with non-zero status.
    """
    logger.info("Running %s: %s", step_name, " ".join(str(c) for c in cmd))
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        logger.error(
            "%s failed (exit %d):\nstdout: %s\nstderr: %s",
            step_name,
            result.returncode,
            result.stdout[-2000:] if result.stdout else "",
            result.stderr[-2000:] if result.stderr else "",
        )
        raise subprocess.CalledProcessError(
            result.returncode, cmd, result.stdout, result.stderr
        )
    if result.stdout:
        logger.info("%s stdout (last 500 chars): %s", step_name, result.stdout[-500:])
    return result


def validate_ldcts_file(ldcts_path: str) -> list:
    """Validate .ldcts file format and return parsed entries.

    LDSC-SEG expects .ldcts files with format (per Pitfall 8):
        TISSUE_NAME<tab>LD_SCORE_PREFIX,ANNOT_PREFIX

    Some downloaded files may use different separators or path formats.

    Parameters
    ----------
    ldcts_path : str
        Path to .ldcts file.

    Returns
    -------
    list of tuple
        List of (tissue_name, ld_paths_string) tuples.

    Raises
    ------
    ValueError
        If the file format is invalid.
    """
    _validate_file(ldcts_path, ".ldcts file")

    entries = []
    with open(ldcts_path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                raise ValueError(
                    f"Invalid .ldcts format at line {line_num}: "
                    f"expected tab-separated tissue_name and LD paths, "
                    f"got {len(parts)} field(s): {line!r}"
                )
            tissue_name = parts[0]
            ld_paths = parts[1]
            entries.append((tissue_name, ld_paths))

    if not entries:
        raise ValueError(f"Empty .ldcts file: {ldcts_path}")

    logger.info("Validated .ldcts file: %d tissue entries from %s", len(entries), ldcts_path)
    return entries


def fix_ldcts_paths(
    ldcts_input: str,
    ldcts_output: str,
    annot_dir: str = None,
) -> int:
    """Rewrite .ldcts file paths to use local installation paths.

    Downloaded .ldcts files from Broad may have absolute paths from the
    original server. This rewrites them relative to the annotation directory.

    Parameters
    ----------
    ldcts_input : str
        Path to original .ldcts file.
    ldcts_output : str
        Path to write fixed .ldcts file.
    annot_dir : str, optional
        Directory containing tissue annotation files. If None, uses the
        parent directory of ldcts_input.

    Returns
    -------
    int
        Number of entries rewritten.

    T-05-13: validates and rewrites .ldcts paths.
    """
    _validate_file(ldcts_input, "input .ldcts file")

    if annot_dir is None:
        annot_dir = os.path.dirname(ldcts_input)

    os.makedirs(os.path.dirname(ldcts_output) or ".", exist_ok=True)

    n_fixed = 0
    with open(ldcts_input) as fin, open(ldcts_output, "w") as fout:
        for line in fin:
            line = line.strip()
            if not line or line.startswith("#"):
                fout.write(line + "\n")
                continue

            parts = line.split("\t")
            if len(parts) < 2:
                fout.write(line + "\n")
                continue

            tissue_name = parts[0]
            ld_paths = parts[1]

            # Rewrite paths: replace any absolute prefix with annot_dir
            fixed_paths = []
            for path_entry in ld_paths.split(","):
                path_entry = path_entry.strip()
                # Extract just the filename/relative part
                basename = os.path.basename(path_entry.rstrip("."))
                if basename:
                    fixed_path = os.path.join(annot_dir, basename) + "."
                else:
                    fixed_path = path_entry
                fixed_paths.append(fixed_path)

            fixed_line = f"{tissue_name}\t{','.join(fixed_paths)}"
            fout.write(fixed_line + "\n")
            n_fixed += 1

    logger.info("Fixed %d .ldcts entries: %s -> %s", n_fixed, ldcts_input, ldcts_output)
    return n_fixed


def run_tissue_enrichment(
    ldsc_dir: str,
    sumstats: str,
    ref_ld_chr: str,
    w_ld_chr: str,
    ldcts_file: str,
    out: str,
) -> dict:
    """Run LDSC-SEG tissue-specific heritability analysis.

    Uses --h2-cts flag (NOT --h2) for cell-type-specific analysis.

    Parameters
    ----------
    ldsc_dir : str
        Path to LDSC installation directory containing ldsc.py.
    sumstats : str
        Path to munged .sumstats.gz file.
    ref_ld_chr : str
        Baseline LD score prefix (e.g., "baselineLD_v2.2/baselineLD.").
    w_ld_chr : str
        Weight LD score prefix (e.g., "weights.").
    ldcts_file : str
        Path to .ldcts file mapping tissues to LD score paths.
    out : str
        Output prefix. Produces {out}.cell_type_results.txt.

    Returns
    -------
    dict
        Parsed results: list of per-tissue enrichment dicts.
    """
    ldsc_py = os.path.join(ldsc_dir, "ldsc.py")
    _validate_file(ldsc_py, "LDSC script")
    _validate_file(sumstats, "munged sumstats")
    _validate_file(ldcts_file, ".ldcts file")

    # Validate .ldcts format before calling LDSC
    validate_ldcts_file(ldcts_file)

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    # CRITICAL: Use --h2-cts (NOT --h2) for tissue-specific analysis
    cmd = [
        sys.executable, ldsc_py,
        "--h2-cts", sumstats,
        "--ref-ld-chr", ref_ld_chr,
        "--ref-ld-chr-cts", ldcts_file,
        "--w-ld-chr", w_ld_chr,
        "--out", out,
    ]

    _run_command(cmd, "LDSC-SEG tissue enrichment")

    # Parse results
    results_path = out + ".cell_type_results.txt"
    parsed = parse_seg_results(results_path)

    return {"results": parsed, "results_path": results_path}


def parse_seg_results(results_path: str) -> list:
    """Parse LDSC-SEG .cell_type_results.txt into list of per-tissue dicts.

    Extracts: Name, Coefficient, Coefficient_std_error,
    Coefficient_z-score, Coefficient_P_value (column name varies by version).

    Parameters
    ----------
    results_path : str
        Path to .cell_type_results.txt (tab-separated).

    Returns
    -------
    list of dict
        Per-tissue results.
    """
    if not os.path.exists(results_path):
        logger.warning("SEG results file not found: %s", results_path)
        return []

    parsed = []
    with open(results_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            parsed.append(dict(row))

    logger.info("Parsed %d tissue results from %s", len(parsed), results_path)
    return parsed


def write_seg_summary(results: list, output_path: str) -> None:
    """Write a clean TSV summary of LDSC-SEG results.

    Parameters
    ----------
    results : list of dict
        Parsed SEG results.
    output_path : str
        Output TSV path.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Map various column names to standardized output
    output_columns = [
        "tissue", "coefficient", "coefficient_se",
        "coefficient_z", "coefficient_p",
    ]

    with open(output_path, "w") as f:
        f.write("\t".join(output_columns) + "\n")
        for row in results:
            tissue = row.get("Name", row.get("tissue", ""))
            coeff = row.get("Coefficient", row.get("coefficient", ""))
            coeff_se = row.get("Coefficient_std_error", row.get("coefficient_se", ""))
            coeff_z = row.get("Coefficient_z-score", row.get("coefficient_z", ""))
            coeff_p = row.get("Coefficient_P_value", row.get("coefficient_p", ""))
            f.write(f"{tissue}\t{coeff}\t{coeff_se}\t{coeff_z}\t{coeff_p}\n")

    logger.info("Wrote SEG summary: %s (%d rows)", output_path, len(results))


def identify_shared_tissues(
    seg_results: dict,
    trait_pairs: list,
    p_threshold: float = 0.05,
) -> list:
    """Identify tissues with shared enrichment between trait pairs (D-05b).

    For each trait pair, finds tissues significant in BOTH traits
    (P < threshold after Bonferroni correction across tissues).

    Parameters
    ----------
    seg_results : dict
        Mapping of trait name -> list of tissue result dicts.
        Each dict has 'Name' (tissue) and a P-value column.
    trait_pairs : list of tuple
        List of (trait1, trait2) pairs to compare.
    p_threshold : float
        Significance threshold after Bonferroni correction (default: 0.05).

    Returns
    -------
    list of dict
        Shared tissue entries with keys: trait1, trait2, shared_tissue,
        p_trait1, p_trait2.
    """
    shared = []

    for trait1, trait2 in trait_pairs:
        results1 = seg_results.get(trait1, [])
        results2 = seg_results.get(trait2, [])

        if not results1 or not results2:
            logger.info(
                "Skipping trait pair %s-%s: missing data (results1=%d, results2=%d)",
                trait1, trait2, len(results1), len(results2),
            )
            continue

        # Build tissue -> p-value maps
        def get_p_value(row):
            """Extract P-value from various possible column names."""
            for key in ["Coefficient_P_value", "coefficient_p", "P_value", "p_value", "P"]:
                if key in row:
                    try:
                        return float(row[key])
                    except (ValueError, TypeError):
                        continue
            return 1.0

        tissues1 = {}
        for row in results1:
            tissue = row.get("Name", row.get("tissue", ""))
            if tissue:
                tissues1[tissue] = get_p_value(row)

        tissues2 = {}
        for row in results2:
            tissue = row.get("Name", row.get("tissue", ""))
            if tissue:
                tissues2[tissue] = get_p_value(row)

        # Bonferroni correction: adjust threshold by number of tissues tested
        n_tissues = max(len(tissues1), len(tissues2), 1)
        bonf_threshold = p_threshold / n_tissues

        # Find tissues significant in both
        common_tissues = set(tissues1.keys()) & set(tissues2.keys())
        for tissue in sorted(common_tissues):
            p1 = tissues1[tissue]
            p2 = tissues2[tissue]
            if p1 < bonf_threshold and p2 < bonf_threshold:
                shared.append({
                    "trait1": trait1,
                    "trait2": trait2,
                    "shared_tissue": tissue,
                    "p_trait1": p1,
                    "p_trait2": p2,
                })

        logger.info(
            "Trait pair %s-%s: %d shared tissues (Bonf threshold=%.2e, %d common tested)",
            trait1, trait2, len([s for s in shared if s["trait1"] == trait1 and s["trait2"] == trait2]),
            bonf_threshold, len(common_tissues),
        )

    return shared


def main():
    parser = argparse.ArgumentParser(
        description="LDSC-SEG tissue-specific heritability enrichment wrapper"
    )

    # Main analysis mode
    parser.add_argument("--ldsc-dir", help="Path to LDSC installation")
    parser.add_argument("--sumstats", help="Munged .sumstats.gz path")
    parser.add_argument("--ref-ld-chr", help="Baseline LD score prefix")
    parser.add_argument("--w-ld-chr", help="Weight LD score prefix")
    parser.add_argument("--ldcts-file", help=".ldcts file path")
    parser.add_argument("--out", help="Output prefix")

    # Path fixing mode
    parser.add_argument(
        "--fix-ldcts-paths", action="store_true",
        help="Fix .ldcts file paths instead of running analysis",
    )
    parser.add_argument("--ldcts-out", help="Output path for fixed .ldcts file")
    parser.add_argument("--annot-dir", help="Directory with tissue annotation files")

    args = parser.parse_args()

    if args.fix_ldcts_paths:
        if not args.ldcts_file or not args.ldcts_out:
            parser.error("--fix-ldcts-paths requires --ldcts-file and --ldcts-out")
        fix_ldcts_paths(
            ldcts_input=args.ldcts_file,
            ldcts_output=args.ldcts_out,
            annot_dir=args.annot_dir,
        )
    else:
        if not all([args.ldsc_dir, args.sumstats, args.ref_ld_chr, args.w_ld_chr, args.ldcts_file, args.out]):
            parser.error(
                "Analysis mode requires --ldsc-dir, --sumstats, --ref-ld-chr, "
                "--w-ld-chr, --ldcts-file, --out"
            )
        result = run_tissue_enrichment(
            ldsc_dir=args.ldsc_dir,
            sumstats=args.sumstats,
            ref_ld_chr=args.ref_ld_chr,
            w_ld_chr=args.w_ld_chr,
            ldcts_file=args.ldcts_file,
            out=args.out,
        )

        # Write summary TSV alongside results
        if result.get("results"):
            summary_path = args.out + "_summary.tsv"
            write_seg_summary(result["results"], summary_path)


if __name__ == "__main__":
    main()
