#!/usr/bin/env python3
"""HESS/rho-HESS local genetic covariance wrapper (Phase 5, D-02a/D-02b/D-02c).

Provides three execution steps:
  1. local-rhog: Run rho-HESS for a single trait pair x ancestry x chromosome
  2. combine:    Combine per-chromosome results for a trait pair x ancestry
  3. compare:    Compare local covariance at pleiotropic loci vs genome-wide average

Because HESS is Python 2.7, this wrapper (Python 3) invokes HESS via
subprocess.run([python27_path, hess_script, ...]) where python27_path
points to the hess_py27 conda env's python binary.

T-05-18 mitigation: subprocess list args only (no shell=True).
T-05-17 mitigation: validate_hess_panel_build() checks SNP positions against GRCh37.
T-05-19 mitigation: Z = BETA/SE validated; N validated as positive integer;
                     NaN Z-scores rejected.

Usage:
    python run_hess.py --step local-rhog \\
        --hess-script tools/hess/hess.py \\
        --python27 /path/to/hess_env/bin/python \\
        --bfile data/reference/hess/ld_panel/EUR/chr22 \\
        --partition data/reference/hess/partition/chr22.bed \\
        --sumstats1 data/processed/sumstats_harmonized/bmi_EUR_hess.tsv \\
        --sumstats2 data/processed/sumstats_harmonized/t2d_EUR_hess.tsv \\
        --chrom 22 \\
        --out results/pathway/hess/bmi_t2d_EUR_chr22

    python run_hess.py --step combine \\
        --hess-script tools/hess/hess.py \\
        --python27 /path/to/hess_env/bin/python \\
        --prefix results/pathway/hess/bmi_t2d_EUR \\
        --out results/pathway/hess/bmi_t2d_EUR_combined

    python run_hess.py --step compare \\
        --combined-results results/pathway/hess/bmi_t2d_EUR_combined.txt \\
        --regions-curated config/regions_curated.csv \\
        --out results/pathway/hess/bmi_t2d_EUR_pleio_vs_bg.tsv
"""
import argparse
import csv
import gzip
import io
import logging
import math
import os
import subprocess
import sys
from pathlib import Path


def _open_sumstats(path: str):
    """Open a sumstats file, transparently handling .bgz/.gz compression.

    Harmonized sumstats are bgzipped (`{trait}.{ancestry}.tsv.bgz`). BGZF
    is gzip-compatible so gzip.open() handles both formats. Returns a
    text-mode file handle.
    """
    if path.endswith(".bgz") or path.endswith(".gz"):
        return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8")
    return open(path, "r", encoding="utf-8")

# Import shared effective-N logic
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sumstats_utils import TRAIT_TYPE, get_effective_n

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# GRCh37 reference positions for genome build validation (T-05-17).
# These are well-known SNPs with stable GRCh37 positions from dbSNP.
GRCH37_REFERENCE_SNPS = {
    "rs1": ("1", 779322),
    "rs12": ("1", 9513573),
    "rs334": ("11", 5248232),
    "rs7412": ("19", 45412079),
    "rs429358": ("19", 45411941),
}


def validate_hess_panel_build(bfile_prefix):
    """Validate that the HESS LD reference panel is on GRCh37 (T-05-17).

    Reads the .bim file, checks available reference SNPs against hardcoded
    GRCh37 positions. Raises ValueError if positions don't match.

    Parameters
    ----------
    bfile_prefix : str
        Prefix for plink bfile (e.g., data/reference/hess/ld_panel/EUR/chr1).
        Will read {bfile_prefix}.bim.

    Returns
    -------
    dict
        Mapping of matched SNP IDs to (expected_pos, actual_pos, match).

    Raises
    ------
    ValueError
        If any matched SNPs have positions inconsistent with GRCh37.
    FileNotFoundError
        If the .bim file does not exist.
    """
    bim_path = f"{bfile_prefix}.bim"
    if not os.path.exists(bim_path):
        raise FileNotFoundError(f"BIM file not found: {bim_path}")

    # Read .bim: CHR, SNP, CM, BP, A1, A2
    panel_snps = {}
    with open(bim_path) as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                chrom, snp_id, _cm, bp = parts[0], parts[1], parts[2], parts[3]
                panel_snps[snp_id] = (chrom, int(bp))

    # Check reference SNPs that exist in the panel
    results = {}
    matched = 0
    mismatched = 0

    for ref_snp, (ref_chr, ref_pos) in GRCH37_REFERENCE_SNPS.items():
        if ref_snp in panel_snps:
            actual_chr, actual_pos = panel_snps[ref_snp]
            is_match = str(actual_chr) == str(ref_chr) and actual_pos == ref_pos
            results[ref_snp] = {
                "expected_chr": ref_chr,
                "expected_pos": ref_pos,
                "actual_chr": actual_chr,
                "actual_pos": actual_pos,
                "match": is_match,
            }
            if is_match:
                matched += 1
            else:
                mismatched += 1

    if mismatched > 0:
        mismatch_details = [
            f"  {snp}: expected chr{info['expected_chr']}:{info['expected_pos']}, "
            f"got chr{info['actual_chr']}:{info['actual_pos']}"
            for snp, info in results.items()
            if not info["match"]
        ]
        raise ValueError(
            f"HESS LD panel genome build mismatch detected! "
            f"{mismatched} of {matched + mismatched} reference SNPs "
            f"have incorrect positions for GRCh37:\n"
            + "\n".join(mismatch_details)
            + "\n\nThe HESS LD panel must be on GRCh37 (hg19). "
            "Check if the panel was built on GRCh38 or another assembly."
        )

    if matched == 0:
        logger.warning(
            "No reference SNPs found in HESS panel BIM file %s. "
            "Build validation could not be performed. This may indicate "
            "an unusual panel or naming convention.",
            bim_path,
        )

    logger.info(
        "HESS panel build validation: %d/%d reference SNPs matched GRCh37",
        matched,
        matched + mismatched,
    )
    return results


def harmonized_to_hess(input_path, output_path, sample_size=None,
                       trait=None, n_case=None, n_ctrl=None,
                       bim_prefix=None):
    """Convert project harmonized sumstats to HESS-compatible format.

    HESS requires columns: SNP, CHR, BP, A1, A2, Z, N
    Z is computed as BETA/SE.

    Parameters
    ----------
    input_path : str
        Path to harmonized sumstats TSV (columns: CHR, POS, SNP, REF, ALT,
        BETA, SE, P, EAF, N).
    output_path : str
        Output path for HESS-format sumstats.
    sample_size : float, optional
        Override sample size for all rows.
    trait : str, optional
        Trait name for effective-N calculation.
    n_case : float, optional
        Number of cases (for binary traits).
    n_ctrl : float, optional
        Number of controls (for binary traits).

    Returns
    -------
    dict
        Stats: n_snps, n_dropped_nan_z, n_dropped_invalid_n.

    Raises
    ------
    ValueError
        If required columns are missing or all Z-scores are NaN.
    """
    # Core columns always required; REF/ALT optional (some sumstats lack alleles)
    # HESS needs CHR and BP (= POS) in addition to Z-score columns.
    core_required = {"SNP", "BETA", "SE", "N", "CHR", "POS"}

    # Read header to validate columns (handle .bgz/.gz transparently -- WR-08)
    with _open_sumstats(input_path) as f:
        header_line = f.readline().strip()
    input_cols = set(header_line.split("\t"))

    # Accept SNP_ID as alias for SNP (canonical harmonized column name)
    snp_col = "SNP"
    if "SNP" not in input_cols and "SNP_ID" in input_cols:
        snp_col = "SNP_ID"
        input_cols.add("SNP")  # satisfy the core_required check

    # Accept BP as alias for POS
    pos_col = "POS"
    if "POS" not in input_cols and "BP" in input_cols:
        pos_col = "BP"
        input_cols.add("POS")  # satisfy the core_required check

    missing = core_required - input_cols
    if missing:
        raise ValueError(
            f"Harmonized sumstats missing required columns: {missing}. "
            f"Available: {sorted(input_cols)}"
        )

    # Determine allele column availability; use dummy alleles when absent
    has_alleles = "REF" in input_cols and "ALT" in input_cols
    if not has_alleles:
        import logging
        logging.getLogger(__name__).warning(
            "REF/ALT columns missing from %s; using dummy alleles (A1=A, A2=G). "
            "HESS h2 estimates remain valid because they depend on Z and N, not alleles.",
            input_path,
        )

    stats = {"n_snps": 0, "n_dropped_nan_z": 0, "n_dropped_invalid_n": 0,
             "n_remapped": 0, "n_no_rsid": 0}
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Build chr:pos→rsID lookup if needed (detect from first SNP)
    chrpos_lookup = None
    if bim_prefix:
        with _open_sumstats(input_path) as peek_fh:
            peek_reader = csv.DictReader(peek_fh, delimiter="\t")
            for peek_row in peek_reader:
                peek_snp = peek_row.get(snp_col, "")
                if peek_snp and ":" in peek_snp:
                    parts = peek_snp.split(":")
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        from munge_sumstats_ldsc import _build_chrpos_to_rsid
                        logger.info("Detected chr:pos SNP IDs in HESS input. Building rsID lookup.")
                        chrpos_lookup = _build_chrpos_to_rsid(bim_prefix)
                break

    with _open_sumstats(input_path) as fin, open(output_path, "w") as fout:
        reader = csv.DictReader(fin, delimiter="\t")
        fout.write("SNP\tCHR\tBP\tA1\tA2\tZ\tN\n")

        for row in reader:
            snp = row[snp_col]
            chrom = row["CHR"]
            bp = row[pos_col]

            # Remap chr:pos → rsID if lookup available
            if chrpos_lookup is not None:
                rsid = chrpos_lookup.get(snp)
                if rsid is None:
                    stats["n_no_rsid"] += 1
                    continue
                snp = rsid
                stats["n_remapped"] += 1

            if has_alleles:
                a1 = row["ALT"].upper()   # Effect allele (HESS requires uppercase: KeyError on 'ag' etc.)
                a2 = row["REF"].upper()   # Other allele
            else:
                a1 = "A"  # Dummy allele; HESS uses Z and N, not alleles
                a2 = "G"

            # Compute Z = BETA / SE (T-05-19)
            try:
                beta = float(row["BETA"])
                se = float(row["SE"])
            except (ValueError, TypeError):
                stats["n_dropped_nan_z"] += 1
                continue

            if se == 0 or math.isnan(beta) or math.isnan(se):
                stats["n_dropped_nan_z"] += 1
                continue

            z = beta / se
            if math.isnan(z) or math.isinf(z):
                stats["n_dropped_nan_z"] += 1
                continue

            # Determine sample size
            if sample_size is not None:
                n = float(sample_size)
            elif trait is not None and TRAIT_TYPE.get(trait) == "binary":
                if n_case is not None and n_ctrl is not None:
                    n = get_effective_n(trait, 0, n_case=n_case, n_ctrl=n_ctrl)
                else:
                    # Fall back to row N with warning
                    try:
                        n = float(row["N"])
                    except (ValueError, TypeError):
                        stats["n_dropped_invalid_n"] += 1
                        continue
            else:
                try:
                    n = float(row["N"])
                except (ValueError, TypeError):
                    stats["n_dropped_invalid_n"] += 1
                    continue

            # Validate N is positive (T-05-19)
            if n <= 0 or math.isnan(n):
                stats["n_dropped_invalid_n"] += 1
                continue

            n_int = int(round(n))
            fout.write(f"{snp}\t{chrom}\t{bp}\t{a1}\t{a2}\t{z:.6f}\t{n_int}\n")
            stats["n_snps"] += 1

    if stats["n_snps"] == 0:
        raise ValueError(
            f"No valid SNPs after conversion from {input_path}. "
            f"Dropped {stats['n_dropped_nan_z']} for NaN Z-scores, "
            f"{stats['n_dropped_invalid_n']} for invalid N."
        )

    logger.info(
        "Converted %d SNPs to HESS format (dropped %d NaN Z, %d invalid N)",
        stats["n_snps"],
        stats["n_dropped_nan_z"],
        stats["n_dropped_invalid_n"],
    )
    return stats


def _validate_path(path, description):
    """Validate that a file path exists and is not empty (T-05-18)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"{description} not found: {path}")
    return os.path.abspath(path)


def run_local_rhog(hess_script, python27, bfile, partition,
                   sumstats1, sumstats2, chrom, out):
    """Run rho-HESS local genetic covariance for one chromosome.

    Invokes HESS via Python 2.7 subprocess (T-05-18: list args, no shell=True).

    Parameters
    ----------
    hess_script : str
        Path to hess.py script.
    python27 : str
        Path to Python 2.7 interpreter in hess_py27 conda env.
    bfile : str
        Prefix for plink bfile (HESS LD panel for this chromosome).
    partition : str
        Path to partition BED file for this chromosome.
    sumstats1 : str
        Path to HESS-formatted sumstats for trait 1.
    sumstats2 : str
        Path to HESS-formatted sumstats for trait 2.
    chrom : str or int
        Chromosome number.
    out : str
        Output prefix for rho-HESS results.

    Returns
    -------
    subprocess.CompletedProcess
        Result of the subprocess call.

    Raises
    ------
    subprocess.CalledProcessError
        If HESS returns non-zero exit code.
    FileNotFoundError
        If any input file is missing.
    """
    # Validate all input paths (T-05-18)
    python27 = _validate_path(python27, "Python 2.7 interpreter")
    hess_script = _validate_path(hess_script, "HESS script")
    partition = _validate_path(partition, "Partition BED file")
    sumstats1 = _validate_path(sumstats1, "Sumstats file 1")
    sumstats2 = _validate_path(sumstats2, "Sumstats file 2")

    # Validate bfile components exist
    for ext in [".bed", ".bim", ".fam"]:
        bfile_component = f"{bfile}{ext}"
        if not os.path.exists(bfile_component):
            raise FileNotFoundError(
                f"HESS LD panel component not found: {bfile_component}"
            )

    # Create output directory
    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # If partition file is genome-wide (ldetect format), filter to this
    # chromosome and write a temp per-chromosome BED for HESS.
    chrom_str = str(chrom)
    chrom_tag = f"chr{chrom_str}"
    with open(partition) as pfh:
        header = pfh.readline()
        lines = [l for l in pfh if l.strip().split()[0].replace("chr", "") == chrom_str]
    if lines:
        import tempfile
        _part_tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=f"_chr{chrom_str}.bed", delete=False, dir=out_dir
        )
        _part_tmp.write(header)
        _part_tmp.writelines(lines)
        _part_tmp.close()
        partition = _part_tmp.name
        logger.info("Filtered partition to chr%s: %d blocks -> %s", chrom_str, len(lines), partition)

    # Build command (T-05-18: list args only, no shell=True)
    # HESS argparse: --local-rhog takes nargs=2 (two sumstats file paths),
    # --chrom is a separate flag.  Previous version incorrectly passed chrom
    # as the first positional arg to --local-rhog and used non-existent
    # --sumstats1/--sumstats2 flags.
    cmd = [
        python27,
        hess_script,
        "--local-rhog",
        sumstats1,
        sumstats2,
        "--chrom",
        str(chrom),
        "--bfile",
        bfile,
        "--partition",
        partition,
        "--out",
        out,
    ]

    return _run_hess_subprocess(cmd, "HESS local-rhog", out_for_log=out)


def _filter_empty_loci(prefix, filt_prefix, chromosomes=range(1, 23)):
    """Drop rank-deficient (empty) loci from HESS step1 outputs.

    ``local_hsqg_step2`` computes a matrix A whose rows are per-locus
    projections and rejects the estimation when ``rank(A) < number_of_loci``
    (tools/hess/src/estimation.py ``local_hsqg_step2_helper``). A locus with
    zero SNPs contributes a zero row (both ``.eig.gz`` and ``.prjsq.gz``
    write an empty line for these loci — see estimation.py:81-82), which
    guarantees rank deficiency. In practice, several trait-partition
    combinations produce 1-4 such loci genome-wide when the harmonized
    sumstats have no SNPs overlapping a HESS partition block.

    This helper reads ``{prefix}_chr{N}.{info,eig,prjsq}.gz`` for each
    chromosome, drops rows where ``nsnp == 0 OR rank == 0``, and writes
    filtered copies as ``{filt_prefix}_chr{N}.{info,eig,prjsq}.gz``. The
    three files are line-indexed, so the same row indices are dropped from
    each. The filtered prefix is then passed to hess.py as ``--prefix``.

    Parameters
    ----------
    prefix : str
        Original step1 prefix. Reads ``{prefix}_chr{N}.*.gz``.
    filt_prefix : str
        Prefix for filtered copies. Writes ``{filt_prefix}_chr{N}.*.gz``.
    chromosomes : iterable of int, default range(1, 23)
        Chromosomes to process (autosomes).

    Returns
    -------
    dict
        Per-chromosome counts: ``{chrom: {"total": int, "kept": int, "dropped": int}}``.

    Raises
    ------
    FileNotFoundError
        If any of the three step1 files is missing for a chromosome.
    ValueError
        If an info row and the corresponding eig/prjsq line counts disagree.
    """
    stats = {}
    out_dir = os.path.dirname(filt_prefix)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    for chrom in chromosomes:
        info_src = f"{prefix}_chr{chrom}.info.gz"
        eig_src = f"{prefix}_chr{chrom}.eig.gz"
        prjsq_src = f"{prefix}_chr{chrom}.prjsq.gz"

        for src, label in [(info_src, "info"), (eig_src, "eig"), (prjsq_src, "prjsq")]:
            if not os.path.exists(src):
                raise FileNotFoundError(
                    f"HESS step1 {label} file missing for chr{chrom}: {src}"
                )

        info_dst = f"{filt_prefix}_chr{chrom}.info.gz"
        eig_dst = f"{filt_prefix}_chr{chrom}.eig.gz"
        prjsq_dst = f"{filt_prefix}_chr{chrom}.prjsq.gz"

        # Read info rows, decide which row indices to keep
        with gzip.open(info_src, "rt") as fh:
            info_lines = fh.readlines()

        keep_mask = []
        for line in info_lines:
            parts = line.strip().split()
            if len(parts) < 5:
                # Malformed row — drop conservatively so hess.py doesn't NaN later
                keep_mask.append(False)
                continue
            try:
                nsnp = int(parts[2])
                rank = int(parts[3])
            except (ValueError, IndexError):
                keep_mask.append(False)
                continue
            keep_mask.append(not (nsnp == 0 or rank == 0))

        # Read eig/prjsq (one whitespace-delimited line per locus, possibly empty)
        with gzip.open(eig_src, "rt") as fh:
            eig_lines = fh.readlines()
        with gzip.open(prjsq_src, "rt") as fh:
            prjsq_lines = fh.readlines()

        # HESS writes the same number of lines to all three files (one per locus).
        # Any disagreement indicates corrupted step1 output.
        if not (len(info_lines) == len(eig_lines) == len(prjsq_lines)):
            raise ValueError(
                f"HESS step1 file lengths disagree for chr{chrom}: "
                f"info={len(info_lines)} eig={len(eig_lines)} "
                f"prjsq={len(prjsq_lines)} (prefix={prefix})"
            )

        total = len(info_lines)
        kept = sum(1 for k in keep_mask if k)
        dropped = total - kept
        stats[chrom] = {"total": total, "kept": kept, "dropped": dropped}

        with gzip.open(info_dst, "wt") as fh_info, \
             gzip.open(eig_dst, "wt") as fh_eig, \
             gzip.open(prjsq_dst, "wt") as fh_prjsq:
            for keep, i_line, e_line, p_line in zip(
                keep_mask, info_lines, eig_lines, prjsq_lines
            ):
                if keep:
                    fh_info.write(i_line)
                    fh_eig.write(e_line)
                    fh_prjsq.write(p_line)

        if dropped:
            logger.info(
                "chr%s: filtered %d empty loci (nsnp==0 or rank==0); kept %d/%d",
                chrom, dropped, kept, total,
            )

    total_dropped = sum(s["dropped"] for s in stats.values())
    total_kept = sum(s["kept"] for s in stats.values())
    logger.info(
        "Filter summary for prefix %s: kept %d loci, dropped %d empty loci",
        prefix, total_kept, total_dropped,
    )
    return stats


def _filter_empty_loci_rhog(prefix, filt_prefix, chromosomes=range(1, 23)):
    """Drop empty loci from rho-HESS step1 outputs (combine step input).

    rho-HESS ``local_rhog_step2`` (tools/hess/src/estimation.py:458-508)
    reads four per-chromosome files: ``{prefix}_trait1_chr{N}.info.gz``,
    ``{prefix}_trait2_chr{N}.info.gz``, ``{prefix}_chr{N}.eig.gz``, and
    ``{prefix}_chr{N}.prjprod.gz``. It then constructs the matrix
    ``A = np.diag(info1['N'] * info2['N'])`` and rejects when
    ``np.linalg.matrix_rank(A) < nloci``.

    An empty locus (``nsnp == 0`` in either trait's info row) writes a row
    with ``N == 0``, putting a zero on the diagonal of A and guaranteeing
    rank deficiency. The Launch12 hess_combine failures all surface here:
    ``[ERROR] Rank of A less than the number of loci.`` (estimation.py:506).

    Counterpart to :func:`_filter_empty_loci` (which filters single-trait
    ``local_hsqg_step2`` inputs read as ``{prefix}_chr{N}.{info,eig,prjsq}.gz``).
    The rho-HESS file naming differs: trait-specific info files but
    pair-shared eig/prjprod, so this function reads four per-chromosome
    files and drops a row index ``k`` if EITHER ``info1[k].nsnp == 0`` OR
    ``info2[k].nsnp == 0`` (HESS partitions are shared across the pair, so
    in practice the empty-locus indices align between the two traits, but
    we OR the masks defensively).

    Parameters
    ----------
    prefix : str
        Original step1 prefix (the trait pair x ancestry prefix). Reads
        ``{prefix}_trait{1,2}_chr{N}.info.gz`` and
        ``{prefix}_chr{N}.{eig,prjprod}.gz``.
    filt_prefix : str
        Prefix for filtered copies. Writes the same four file naming patterns.
    chromosomes : iterable of int, default range(1, 23)
        Chromosomes to process (autosomes).

    Returns
    -------
    dict
        Per-chromosome counts: ``{chrom: {"total": int, "kept": int, "dropped": int}}``.

    Raises
    ------
    FileNotFoundError
        If any of the four step1 files is missing for a chromosome.
    ValueError
        If line counts disagree across the four files for a chromosome.
    """
    stats = {}
    out_dir = os.path.dirname(filt_prefix)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    for chrom in chromosomes:
        info1_src = f"{prefix}_trait1_chr{chrom}.info.gz"
        info2_src = f"{prefix}_trait2_chr{chrom}.info.gz"
        eig_src = f"{prefix}_chr{chrom}.eig.gz"
        prjprod_src = f"{prefix}_chr{chrom}.prjprod.gz"

        for src, label in [
            (info1_src, "info (trait1)"),
            (info2_src, "info (trait2)"),
            (eig_src, "eig"),
            (prjprod_src, "prjprod"),
        ]:
            if not os.path.exists(src):
                raise FileNotFoundError(
                    f"rho-HESS step1 {label} file missing for chr{chrom}: {src}"
                )

        info1_dst = f"{filt_prefix}_trait1_chr{chrom}.info.gz"
        info2_dst = f"{filt_prefix}_trait2_chr{chrom}.info.gz"
        eig_dst = f"{filt_prefix}_chr{chrom}.eig.gz"
        prjprod_dst = f"{filt_prefix}_chr{chrom}.prjprod.gz"

        with gzip.open(info1_src, "rt") as fh:
            info1_lines = fh.readlines()
        with gzip.open(info2_src, "rt") as fh:
            info2_lines = fh.readlines()
        with gzip.open(eig_src, "rt") as fh:
            eig_lines = fh.readlines()
        with gzip.open(prjprod_src, "rt") as fh:
            prjprod_lines = fh.readlines()

        if not (
            len(info1_lines)
            == len(info2_lines)
            == len(eig_lines)
            == len(prjprod_lines)
        ):
            raise ValueError(
                f"rho-HESS step1 file lengths disagree for chr{chrom}: "
                f"info1={len(info1_lines)} info2={len(info2_lines)} "
                f"eig={len(eig_lines)} prjprod={len(prjprod_lines)} "
                f"(prefix={prefix})"
            )

        keep_mask = []
        for i1_line, i2_line in zip(info1_lines, info2_lines):
            keep = True
            for line in (i1_line, i2_line):
                parts = line.strip().split()
                if len(parts) < 5:
                    keep = False
                    break
                try:
                    nsnp = int(parts[2])
                    rank = int(parts[3])
                except (ValueError, IndexError):
                    keep = False
                    break
                if nsnp == 0 or rank == 0:
                    keep = False
                    break
            keep_mask.append(keep)

        total = len(info1_lines)
        kept = sum(1 for k in keep_mask if k)
        dropped = total - kept
        stats[chrom] = {"total": total, "kept": kept, "dropped": dropped}

        with gzip.open(info1_dst, "wt") as fh_i1, \
             gzip.open(info2_dst, "wt") as fh_i2, \
             gzip.open(eig_dst, "wt") as fh_e, \
             gzip.open(prjprod_dst, "wt") as fh_p:
            for keep, i1l, i2l, el, pl in zip(
                keep_mask, info1_lines, info2_lines, eig_lines, prjprod_lines
            ):
                if keep:
                    fh_i1.write(i1l)
                    fh_i2.write(i2l)
                    fh_e.write(el)
                    fh_p.write(pl)

        if dropped:
            logger.info(
                "chr%s (rho-HESS): filtered %d empty loci; kept %d/%d",
                chrom, dropped, kept, total,
            )

    total_dropped = sum(s["dropped"] for s in stats.values())
    total_kept = sum(s["kept"] for s in stats.values())
    logger.info(
        "rho-HESS filter summary for prefix %s: kept %d loci, dropped %d empty loci",
        prefix, total_kept, total_dropped,
    )
    return stats


def _run_hess_subprocess(cmd, description, out_for_log=None):
    """Invoke HESS (Py2.7) and surface diagnostics on failure.

    Wraps ``subprocess.run(..., check=True)`` so that when hess.py exits
    non-zero, the caller gets the child's ``stderr``, ``stdout``, AND the
    hess.py-generated ``{out}.log`` all forwarded to the logger at ERROR
    level before ``CalledProcessError`` propagates. The Launch11 diagnosis
    in .planning/debug/t1-launch10-residual-failures.md §2026-04-17T21:14Z
    showed that the real error (``Rank of A less than the number of loci``)
    was hidden in the hess.py-authored log file because ``check=True``
    swallows the child output.

    Parameters
    ----------
    cmd : list of str
        Full argv for ``subprocess.run`` (no shell).
    description : str
        Human-friendly description used in log lines.
    out_for_log : str, optional
        HESS ``--out`` value. If provided, ``{out_for_log}.log`` is read
        and forwarded on failure.

    Returns
    -------
    subprocess.CompletedProcess
    """
    logger.info("Running %s: %s", description, " ".join(cmd))
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        logger.error("%s failed (exit %s).", description, exc.returncode)
        if exc.stdout:
            logger.error("%s stdout:\n%s", description, exc.stdout)
        if exc.stderr:
            logger.error("%s stderr:\n%s", description, exc.stderr)
        if out_for_log:
            log_file = f"{out_for_log}.log"
            if os.path.exists(log_file):
                try:
                    with open(log_file) as fh:
                        log_contents = fh.read()
                    logger.error(
                        "%s hess.py log file (%s):\n%s",
                        description, log_file, log_contents,
                    )
                except OSError as read_exc:
                    logger.error(
                        "Could not read hess.py log file %s: %s",
                        log_file, read_exc,
                    )
            else:
                logger.error(
                    "%s did not emit a hess.py log file at %s",
                    description, log_file,
                )
        raise

    if result.stdout:
        logger.info("%s stdout:\n%s", description, result.stdout)
    if result.stderr:
        logger.warning("%s stderr:\n%s", description, result.stderr)
    return result


def run_hsqg_step2(hess_script, python27, prefix, out):
    """Run HESS local SNP-heritability step 2 for a single trait.

    HESS dispatcher (tools/hess/hess.py:73-76) selects ``local_hsqg_step2`` when
    ``--prefix`` and ``--out`` are provided and all three rho-HESS flags
    (``--pheno-cor``, ``--num-shared``, ``--local-hsqg-est``) are absent. Reads
    ``{prefix}_chr{N}.{info,eig,prjsq}.gz`` for chromosomes 1-22 and writes
    ``{out}.txt`` (columns: chr, start, end, num_snp, k, local_h2g, var, se,
    z, p).

    This step is required because rho-HESS step 2 needs per-trait local
    heritability estimates as ``--local-hsqg-est`` inputs (tools/hess/hess.py:84-87).
    rho-HESS step 1 already writes per-trait files as
    ``{pair_prefix}_trait{1,2}_chr{N}.{info,eig,prjsq}.gz``, so we invoke this
    with ``prefix={pair_prefix}_trait1`` and ``prefix={pair_prefix}_trait2`` to
    produce the two ``{out}.txt`` files that rho-HESS step 2 consumes via
    ``--local-hsqg-est file1 file2`` (nargs=2 at tools/hess/hess.py:176-177).

    Pre-filter: ``local_hsqg_step2`` rejects rank-deficient projection
    matrices (``Rank of A less than the number of loci``). Empty loci
    (``nsnp == 0`` in the info row) always produce a zero-row and therefore
    always rank-deficiency. This function pre-filters the three step1 files
    (info, eig, prjsq) to drop empty loci before invoking hess.py. Filtered
    copies are written as ``{prefix}_filt_chr{N}.*.gz`` and HESS is invoked
    with ``--prefix {prefix}_filt``. See Launch11 regression (debug file
    §2026-04-17T21:14Z).

    Parameters
    ----------
    hess_script : str
        Path to hess.py script.
    python27 : str
        Path to Python 2.7 interpreter in hess_py27 conda env.
    prefix : str
        Prefix for per-chromosome step1 outputs. Must resolve
        ``{prefix}_chr{N}.{info,eig,prjsq}.gz`` for N in 1..22.
    out : str
        Output prefix. Writes ``{out}.txt``.

    Returns
    -------
    subprocess.CompletedProcess

    Raises
    ------
    FileNotFoundError
        If python27 or hess_script is missing.
    subprocess.CalledProcessError
        If HESS exits non-zero.
    """
    python27 = _validate_path(python27, "Python 2.7 interpreter")
    hess_script = _validate_path(hess_script, "HESS script")

    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # Pre-filter empty loci (nsnp==0 or rank==0). Write filtered copies
    # alongside the originals so Snakemake's existing .done sentinel still
    # covers the originating step1 work. HESS reads filtered files only.
    filt_prefix = f"{prefix}_filt"
    _filter_empty_loci(prefix, filt_prefix)

    # Dispatch to local_hsqg_step2: prefix + out, no rho-HESS flags
    cmd = [
        python27,
        hess_script,
        "--prefix",
        filt_prefix,
        "--out",
        out,
    ]

    return _run_hess_subprocess(cmd, "HESS local_hsqg_step2", out_for_log=out)


def run_combine(hess_script, python27, prefix, out,
                local_hsqg_est1=None, local_hsqg_est2=None,
                pheno_cor=0.0, num_shared=0):
    """Combine per-chromosome rho-HESS results (local_rhog_step2).

    HESS dispatcher (tools/hess/hess.py:83-87) selects ``local_rhog_step2``
    only when ``--pheno-cor``, ``--num-shared``, AND ``--local-hsqg-est`` are
    ALL provided. Previous implementation passed only ``--prefix``/``--out``,
    which routed to ``local_hsqg_step2`` (single-trait heritability), which
    then failed with "Missing step 1 results" because rho-HESS step 1 writes
    trait-specific files as ``{prefix}_trait{1,2}_chr{N}.info.gz``, not
    ``{prefix}_chr{N}.info.gz``.

    Parameters
    ----------
    hess_script : str
        Path to hess.py script.
    python27 : str
        Path to Python 2.7 interpreter.
    prefix : str
        Prefix for per-chromosome rho-HESS step 1 results
        (e.g., ``results/pathway/hess/bmi_t2d_EUR``). HESS step 2 reads
        ``{prefix}_trait{1,2}_chr{N}.*.gz`` and ``{prefix}_chr{N}.{eig,prjprod}.gz``.
    out : str
        Output prefix for combined results. HESS writes ``{out}.txt``.
    local_hsqg_est1 : str, optional
        Path to trait1 local heritability estimates (``{out}.txt`` from
        ``run_hsqg_step2`` with prefix=``{prefix}_trait1``). Required for
        rho-HESS dispatch; without it HESS routes to single-trait step 2.
    local_hsqg_est2 : str, optional
        Path to trait2 local heritability estimates. Required for rho-HESS dispatch.
    pheno_cor : float, default 0.0
        Phenotype correlation between traits. 0.0 is valid when there is no
        sample overlap (``num_shared == 0``), which holds for independent
        cohorts (public sumstats from non-overlapping studies).
    num_shared : int, default 0
        Number of shared samples between the two GWAS cohorts. Setting this
        to 0 tells HESS to skip sample-overlap bias correction (see
        tools/hess/src/estimation.py:482-484 and 518: ``rhoe = 0.0 when
        num_shared == 0``).

    Returns
    -------
    subprocess.CompletedProcess
    """
    python27 = _validate_path(python27, "Python 2.7 interpreter")
    hess_script = _validate_path(hess_script, "HESS script")

    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    if local_hsqg_est1 is not None and local_hsqg_est2 is not None:
        # Rho-HESS step 2 dispatch: --local-hsqg-est takes nargs=2 (one file per trait).
        # Pre-filter empty loci from the four step1 files (info1, info2, eig, prjprod):
        # local_rhog_step2 builds A = diag(N1*N2), so an empty locus (nsnp==0 → N==0)
        # puts a zero on the diagonal and rejects with rank-deficiency. See
        # tools/hess/src/estimation.py:497-508 and the .planning/debug session
        # §2026-04-18T13:00Z (Bug 4).
        filt_prefix = f"{prefix}_filt"
        _filter_empty_loci_rhog(prefix, filt_prefix)
        local_hsqg_est1 = _validate_path(local_hsqg_est1, "Local hsqg estimates (trait 1)")
        local_hsqg_est2 = _validate_path(local_hsqg_est2, "Local hsqg estimates (trait 2)")
        cmd = [
            python27,
            hess_script,
            "--prefix",
            filt_prefix,
            "--out",
            out,
            "--pheno-cor", str(pheno_cor),
            "--num-shared", str(num_shared),
            "--local-hsqg-est", local_hsqg_est1, local_hsqg_est2,
        ]
        description = "HESS local_rhog_step2"
    else:
        # Legacy / single-trait heritability path: retain backwards compat.
        # No pre-filter needed because the legacy code path historically passes the
        # original prefix; if a caller starts hitting rank deficiency on this branch,
        # add a _filter_empty_loci(prefix, ...) call here.
        cmd = [
            python27,
            hess_script,
            "--prefix",
            prefix,
            "--out",
            out,
        ]
        description = "HESS local_hsqg_step2 (legacy path)"

    return _run_hess_subprocess(cmd, description, out_for_log=out)


def compare_pleiotropic_vs_background(combined_path, regions_path):
    """Compare local covariance at pleiotropic loci vs genome-wide average (D-02c).

    Algorithm:
    1. Read combined rho-HESS output (per-partition local covariance + SE)
    2. Read regions_curated.csv for pleiotropic loci coordinates
    3. Map partitions to pleiotropic loci by interval overlap
    4. Split into pleiotropic vs background partitions
    5. Compute mean local covariance for each group
    6. Compute z-score: z = (mean_pleio - mean_bg) / sqrt(se_pleio^2/n_pleio + se_bg^2/n_bg)
    7. Compute two-sided p-value

    Parameters
    ----------
    combined_path : str
        Path to combined rho-HESS output file. Expected columns:
        chr, start, end, local_rhog (or rho_g), se (or local_rhog_se).
    regions_path : str
        Path to config/regions_curated.csv with columns: region_id, chr, start, end.

    Returns
    -------
    dict
        Keys: mean_pleio, mean_bg, ratio, z_score, p_value,
        n_pleio_partitions, n_bg_partitions.

    Raises
    ------
    FileNotFoundError
        If input files don't exist.
    ValueError
        If no pleiotropic or background partitions found.
    """
    if not os.path.exists(combined_path):
        raise FileNotFoundError(
            f"Combined rho-HESS results not found: {combined_path}"
        )
    if not os.path.exists(regions_path):
        raise FileNotFoundError(
            f"Regions curated file not found: {regions_path}"
        )

    # Read pleiotropic loci from regions_curated.csv
    pleiotropic_loci = []
    with open(regions_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                chrom = str(row["chr"]).replace("chr", "")
                start = int(row["start"])
                end = int(row["end"])
                pleiotropic_loci.append((chrom, start, end))
            except (ValueError, KeyError) as e:
                logger.warning("Skipping malformed region row: %s (%s)", row, e)

    if not pleiotropic_loci:
        raise ValueError("No valid pleiotropic loci found in regions file")

    # Read combined rho-HESS output
    # HESS output format varies; handle common column names
    partitions = []
    with open(combined_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        cols = reader.fieldnames

        # Detect column names for local covariance and SE
        rhog_col = None
        se_col = None
        chr_col = None
        start_col = None
        end_col = None

        for c in cols:
            cl = c.lower()
            if cl in ("local_rhog", "rho_g", "rhog", "local_cov", "cov"):
                rhog_col = c
            elif cl in ("se", "local_rhog_se", "rhog_se", "cov_se"):
                se_col = c
            elif cl in ("chr", "chrom", "chromosome"):
                chr_col = c
            elif cl in ("start", "bp_start", "begin"):
                start_col = c
            elif cl in ("end", "bp_end", "stop"):
                end_col = c

        if not all([rhog_col, se_col, chr_col, start_col, end_col]):
            raise ValueError(
                f"Could not identify required columns in combined HESS output. "
                f"Available columns: {cols}. "
                f"Need columns for: chr, start, end, local_rhog/cov, se. "
                f"Detected: chr={chr_col}, start={start_col}, end={end_col}, "
                f"rhog={rhog_col}, se={se_col}"
            )

        for row in reader:
            try:
                chrom = str(row[chr_col]).replace("chr", "")
                start = int(row[start_col])
                end = int(row[end_col])
                rhog = float(row[rhog_col])
                se = float(row[se_col])

                if math.isnan(rhog) or math.isnan(se):
                    continue

                partitions.append({
                    "chr": chrom,
                    "start": start,
                    "end": end,
                    "rhog": rhog,
                    "se": se,
                })
            except (ValueError, KeyError) as e:
                logger.warning("Skipping malformed partition row: %s", e)

    if not partitions:
        raise ValueError("No valid partitions found in combined HESS output")

    # Classify partitions as pleiotropic or background
    pleio_partitions = []
    bg_partitions = []

    for part in partitions:
        is_pleio = False
        for locus_chr, locus_start, locus_end in pleiotropic_loci:
            # Check overlap: partition [start, end] intersects locus [start, end]
            if (str(part["chr"]) == str(locus_chr)
                    and part["start"] < locus_end
                    and part["end"] > locus_start):
                is_pleio = True
                break

        if is_pleio:
            pleio_partitions.append(part)
        else:
            bg_partitions.append(part)

    n_pleio = len(pleio_partitions)
    n_bg = len(bg_partitions)

    if n_pleio == 0:
        raise ValueError(
            "No partitions overlap pleiotropic loci. Check that the "
            "combined HESS output and regions_curated.csv use the same "
            "genome build (expected GRCh37)."
        )
    if n_bg == 0:
        raise ValueError("No background partitions found (all are pleiotropic)")

    # Compute mean local covariance for each group
    mean_pleio = sum(p["rhog"] for p in pleio_partitions) / n_pleio
    mean_bg = sum(p["rhog"] for p in bg_partitions) / n_bg

    # Compute pooled SE for each group
    # SE of the mean = sqrt(sum(se_i^2) / n^2)
    se_pleio = math.sqrt(sum(p["se"] ** 2 for p in pleio_partitions)) / n_pleio
    se_bg = math.sqrt(sum(p["se"] ** 2 for p in bg_partitions)) / n_bg

    # Z-score for difference: z = (mean_pleio - mean_bg) / sqrt(se_pleio^2 + se_bg^2)
    se_diff = math.sqrt(se_pleio ** 2 + se_bg ** 2)
    if se_diff == 0:
        z_score = float("inf") if mean_pleio > mean_bg else float("-inf")
        p_value = 0.0
    else:
        z_score = (mean_pleio - mean_bg) / se_diff
        # Two-sided p-value from standard normal
        p_value = 2.0 * _norm_sf(abs(z_score))

    # Compute ratio (handle zero mean_bg)
    if mean_bg != 0:
        ratio = mean_pleio / mean_bg
    else:
        ratio = float("inf") if mean_pleio > 0 else float("nan")

    result = {
        "mean_pleio": mean_pleio,
        "mean_bg": mean_bg,
        "ratio": ratio,
        "z_score": z_score,
        "p_value": p_value,
        "n_pleio_partitions": n_pleio,
        "n_bg_partitions": n_bg,
    }

    logger.info(
        "Pleiotropic vs background comparison: "
        "mean_pleio=%.4f (n=%d), mean_bg=%.4f (n=%d), "
        "ratio=%.2f, z=%.2f, p=%.2e",
        mean_pleio, n_pleio, mean_bg, n_bg, ratio, z_score, p_value,
    )

    return result


def _norm_sf(z):
    """Survival function (1 - CDF) of the standard normal distribution.

    Uses the complementary error function for numerical stability.
    Avoids scipy dependency for this single function.
    """
    return 0.5 * math.erfc(z / math.sqrt(2))


def write_comparison_results(result, output_path):
    """Write pleiotropic vs background comparison results to TSV.

    Parameters
    ----------
    result : dict
        Output from compare_pleiotropic_vs_background().
    output_path : str
        Output TSV path.
    """
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, "w") as f:
        columns = [
            "mean_pleio", "mean_bg", "ratio", "z_score", "p_value",
            "n_pleio_partitions", "n_bg_partitions",
        ]
        f.write("\t".join(columns) + "\n")
        values = [str(result[col]) for col in columns]
        f.write("\t".join(values) + "\n")

    logger.info("Wrote comparison results to %s", output_path)


def main():
    """CLI entry point for HESS/rho-HESS wrapper."""
    parser = argparse.ArgumentParser(
        description="HESS/rho-HESS local genetic covariance wrapper"
    )
    parser.add_argument(
        "--step",
        required=True,
        choices=["local-rhog", "hsqg-step2", "combine", "compare"],
        help="Execution step: local-rhog, hsqg-step2, combine, or compare",
    )

    # local-rhog args
    parser.add_argument("--hess-script", help="Path to hess.py script")
    parser.add_argument(
        "--python27",
        help="Path to Python 2.7 interpreter in hess_py27 conda env",
    )
    parser.add_argument("--bfile", help="Plink bfile prefix for HESS LD panel")
    parser.add_argument("--partition", help="Partition BED file path")
    parser.add_argument("--sumstats1", help="HESS-format sumstats for trait 1")
    parser.add_argument("--sumstats2", help="HESS-format sumstats for trait 2")
    parser.add_argument("--chrom", help="Chromosome number")
    parser.add_argument("--out", help="Output prefix/path")

    # combine args
    parser.add_argument("--prefix", help="Prefix for per-chromosome results")
    parser.add_argument(
        "--local-hsqg-est1",
        help=(
            "Path to trait 1 local heritability estimates "
            "({out}.txt from --step hsqg-step2). When supplied with "
            "--local-hsqg-est2, the combine step dispatches rho-HESS step 2."
        ),
    )
    parser.add_argument(
        "--local-hsqg-est2",
        help="Path to trait 2 local heritability estimates (see --local-hsqg-est1).",
    )
    parser.add_argument(
        "--pheno-cor",
        type=float,
        default=0.0,
        help="Phenotype correlation between the two traits (default 0.0).",
    )
    parser.add_argument(
        "--num-shared",
        type=int,
        default=0,
        help="Number of shared samples between the two GWAS cohorts (default 0 = no overlap).",
    )

    # compare args
    parser.add_argument("--combined-results", help="Combined rho-HESS output")
    parser.add_argument("--regions-curated", help="Path to regions_curated.csv")

    args = parser.parse_args()

    if args.step == "local-rhog":
        # Validate required args
        for required in ["hess_script", "python27", "bfile", "partition",
                         "sumstats1", "sumstats2", "chrom", "out"]:
            if getattr(args, required) is None:
                parser.error(f"--{required.replace('_', '-')} required for --step local-rhog")

        run_local_rhog(
            hess_script=args.hess_script,
            python27=args.python27,
            bfile=args.bfile,
            partition=args.partition,
            sumstats1=args.sumstats1,
            sumstats2=args.sumstats2,
            chrom=args.chrom,
            out=args.out,
        )

    elif args.step == "hsqg-step2":
        for required in ["hess_script", "python27", "prefix", "out"]:
            if getattr(args, required) is None:
                parser.error(
                    f"--{required.replace('_', '-')} required for --step hsqg-step2"
                )

        run_hsqg_step2(
            hess_script=args.hess_script,
            python27=args.python27,
            prefix=args.prefix,
            out=args.out,
        )

    elif args.step == "combine":
        for required in ["hess_script", "python27", "prefix", "out"]:
            if getattr(args, required) is None:
                parser.error(f"--{required.replace('_', '-')} required for --step combine")

        run_combine(
            hess_script=args.hess_script,
            python27=args.python27,
            prefix=args.prefix,
            out=args.out,
            local_hsqg_est1=args.local_hsqg_est1,
            local_hsqg_est2=args.local_hsqg_est2,
            pheno_cor=args.pheno_cor,
            num_shared=args.num_shared,
        )

    elif args.step == "compare":
        for required in ["combined_results", "regions_curated", "out"]:
            if getattr(args, required) is None:
                parser.error(f"--{required.replace('_', '-')} required for --step compare")

        result = compare_pleiotropic_vs_background(
            combined_path=args.combined_results,
            regions_path=args.regions_curated,
        )
        write_comparison_results(result, args.out)


if __name__ == "__main__":
    main()
