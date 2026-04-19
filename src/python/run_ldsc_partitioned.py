#!/usr/bin/env python3
"""LDSC partitioned heritability wrapper: munge, compute-ld-scores, h2.

Provides a unified CLI for the LDSC partitioned heritability pipeline:
  Step: munge            -- Convert harmonized sumstats to LDSC format via
                            munge_sumstats_ldsc.py, then run LDSC munge_sumstats.py
  Step: compute-ld-scores -- Compute LD scores for custom annotations (ldsc --l2)
  Step: h2               -- Run partitioned heritability (ldsc --h2) with
                            baseline v2.2 + custom pathway annotations

All subprocess calls use list arguments (NOT shell=True) per T-05-05/T-05-14.
All input files validated with os.path.exists before LDSC invocation.

Critical design decisions:
  - Always includes --overlap-annot flag in h2 step (anti-pattern prevention)
  - Baseline v2.2 always first in --ref-ld-chr (D-04a)
  - Post-munge SNP count validation: warns if < 500,000 (Pitfall 2 / T-05-16)
  - Parses .results file to extract per-annotation enrichment metrics
  - In ``run_partitioned_h2``: strips ``NEGCTRL_HLA_IMMUNEL2`` from a private
    on-the-fly copy of the custom_pathway LD scores before invoking LDSC. The
    annotation is HLA-region-specific (chr6 26–34 Mb, the canonical MHC) and
    the standard LDSC weight file (``weights.hm3_noMHC``, Finucane 2015) excludes
    MHC by design. The inner-join in ``read_ld_and_sumstats`` zeros the column
    on the regression-eligible SNP set → singular X^T X → ``LinAlgError`` at
    ``np.linalg.solve(xtx, xty)``. Filtering is partitioned-h2-specific so the
    full custom_pathway files remain intact for LDSC-SEG and other consumers.
    See ``.planning/debug/t1-launch10-residual-failures.md`` §
    ``2026-04-18T20:55Z — Bug 5 RE-DIAGNOSIS`` for the SVD evidence.

References:
    Bulik-Sullivan et al. 2015 Nat Genet (LDSC)
    Finucane et al. 2015 Nat Genet (Partitioned heritability + MHC exclusion)
    Gazal et al. 2017 Nat Genet (Baseline v2.2)

Usage:
    python run_ldsc_partitioned.py --step munge \\
        --ldsc-dir tools/ldsc --sumstats input.tsv \\
        --hapmap3 w_hm3.snplist --sample-size 500000 --out munged

    python run_ldsc_partitioned.py --step compute-ld-scores \\
        --ldsc-dir tools/ldsc \\
        --annot-prefix annot/custom_pathway \\
        --bfile-prefix 1000G.EUR.QC \\
        --out-prefix ld_scores/custom_pathway \\
        --hapmap3 w_hm3.snplist

    python run_ldsc_partitioned.py --step h2 \\
        --ldsc-dir tools/ldsc \\
        --sumstats munged.sumstats.gz \\
        --ref-ld-chr baseline.,custom. \\
        --w-ld-chr weights. \\
        --frqfile-chr 1000G.EUR.QC. \\
        --out output_h2
"""
import argparse
import csv
import gzip
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Allow importing shared module from same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sumstats_utils import TRAIT_TYPE, compute_effective_n

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Minimum expected SNP count after munging (Pitfall 2 / T-05-16)
MIN_MUNGED_SNPS = 500000

# Annotations to drop from a private copy of custom_pathway LD scores before
# running ``ldsc.py --h2 --overlap-annot``. These columns have spatial
# coverage that conflicts with ``weights.hm3_noMHC`` (the standard LDSC
# weight file, Finucane 2015) — the inner-join in ``read_ld_and_sumstats``
# zeros them out on the regression-eligible SNP set, producing a singular
# X^T X. The annotations remain present in the canonical
# ``custom_pathway.{N}.l2.ldscore.gz`` files for other consumers
# (LDSC-SEG, etc.) — only the partitioned-h2 step uses the filtered copy.
# Stored without the trailing ``L2`` suffix; the L2 suffix is added when
# matching against header columns. See debug session
# ``.planning/debug/t1-launch10-residual-failures.md`` §
# ``2026-04-18T20:55Z — Bug 5 RE-DIAGNOSIS``.
PARTITIONED_H2_DROP_ANNOTATIONS = ("NEGCTRL_HLA_IMMUNE",)


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


def _count_sumstats_snps(sumstats_gz_path: str) -> int:
    """Count lines (excluding header) in a .sumstats.gz file.

    Parameters
    ----------
    sumstats_gz_path : str
        Path to the .sumstats.gz file.

    Returns
    -------
    int
        Number of SNP lines.
    """
    count = 0
    with gzip.open(sumstats_gz_path, "rt") as f:
        next(f, None)  # skip header
        for _ in f:
            count += 1
    return count


def _drop_columns_from_ldscore(
    src_path: str,
    dst_path: str,
    drop_annotations: tuple,
) -> tuple:
    """Stream a ``.l2.ldscore.gz`` file dropping the named annotation columns.

    LDSC LD score files are tab-separated, gzipped, with a header row
    ``CHR<TAB>SNP<TAB>BP<TAB>{ANNOT1}L2<TAB>{ANNOT2}L2 ...``. Each
    annotation column ends in the ``L2`` suffix. This function rewrites
    the file dropping any column whose header (without ``L2``) is in
    ``drop_annotations``.

    Parameters
    ----------
    src_path : str
        Source ``.l2.ldscore.gz`` file path.
    dst_path : str
        Destination path (overwritten if exists).
    drop_annotations : tuple of str
        Annotation names WITHOUT the trailing ``L2`` suffix
        (e.g. ``("NEGCTRL_HLA_IMMUNE",)``).

    Returns
    -------
    tuple
        ``(dropped_indices, kept_header_cols)`` where ``dropped_indices`` is
        a list of 0-indexed column positions removed from the row and
        ``kept_header_cols`` is the surviving header column names.

    Raises
    ------
    ValueError
        If ``src_path`` lacks the expected ``CHR/SNP/BP`` prefix, or if any
        ``drop_annotations`` entry is not present in the header.
    """
    with gzip.open(src_path, "rt") as fin:
        header_line = fin.readline().rstrip("\n")
        cols = header_line.split("\t")
        if len(cols) < 4 or cols[:3] != ["CHR", "SNP", "BP"]:
            raise ValueError(
                f"{src_path}: expected header to start with CHR/SNP/BP, got {cols[:3]}"
            )

        drop_set = {f"{a}L2" for a in drop_annotations}
        # Identify which columns to drop, by 0-indexed position
        dropped_indices = [i for i, c in enumerate(cols) if c in drop_set]
        kept_indices = [i for i, _ in enumerate(cols) if i not in set(dropped_indices)]
        kept_header = [cols[i] for i in kept_indices]

        # Sanity: every requested annotation must be present
        present_drop_names = {cols[i] for i in dropped_indices}
        missing = drop_set - present_drop_names
        if missing:
            raise ValueError(
                f"{src_path}: requested drop annotations not in header: {sorted(missing)}"
            )

        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)
        with gzip.open(dst_path, "wt") as fout:
            fout.write("\t".join(kept_header) + "\n")
            for line in fin:
                line = line.rstrip("\n")
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) != len(cols):
                    raise ValueError(
                        f"{src_path}: row width {len(parts)} != header width "
                        f"{len(cols)} in line: {line[:120]!r}"
                    )
                fout.write("\t".join(parts[i] for i in kept_indices) + "\n")

    return dropped_indices, kept_header


def _drop_columns_from_annot(
    src_path: str,
    dst_path: str,
    drop_annotations: tuple,
) -> tuple:
    """Stream a ``.annot.gz`` file dropping the named annotation columns.

    LDSC .annot files are tab-separated, gzipped, with header
    ``CHR<TAB>BP<TAB>SNP<TAB>CM<TAB>{ANNOT1}<TAB>{ANNOT2} ...``.
    Annotation column names do NOT carry the trailing ``L2`` suffix
    (unlike the sibling ``.l2.ldscore.gz`` header). Match is by exact
    column name against ``drop_annotations``.

    Returns ``(dropped_indices, kept_header)`` where indices are 0-based
    into the annot header (CHR/BP/SNP/CM come first).
    """
    with gzip.open(src_path, "rt") as fin:
        header_line = fin.readline().rstrip("\n")
        cols = header_line.split("\t")
        if len(cols) < 5 or cols[:4] != ["CHR", "BP", "SNP", "CM"]:
            raise ValueError(
                f"{src_path}: expected header to start with CHR/BP/SNP/CM, got {cols[:4]}"
            )

        drop_set = set(drop_annotations)
        dropped_indices = [i for i, c in enumerate(cols) if c in drop_set]
        kept_indices = [i for i in range(len(cols)) if i not in set(dropped_indices)]
        kept_header = [cols[i] for i in kept_indices]

        present_drop_names = {cols[i] for i in dropped_indices}
        missing = drop_set - present_drop_names
        if missing:
            raise ValueError(
                f"{src_path}: requested drop annotations not in header: {sorted(missing)}"
            )

        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)
        with gzip.open(dst_path, "wt") as fout:
            fout.write("\t".join(kept_header) + "\n")
            for line in fin:
                line = line.rstrip("\n")
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) != len(cols):
                    raise ValueError(
                        f"{src_path}: row width {len(parts)} != header width "
                        f"{len(cols)} in line: {line[:120]!r}"
                    )
                fout.write("\t".join(parts[i] for i in kept_indices) + "\n")

    return dropped_indices, kept_header


def _drop_columns_from_m_file(
    src_path: str,
    dst_path: str,
    annotation_drop_indices: list,
) -> list:
    """Drop columns from an LDSC ``.l2.M`` or ``.l2.M_5_50`` sibling file.

    M files are single-line, tab-separated SNP counts — one entry per
    annotation column (NO ``CHR/SNP/BP`` prefix). The annotation column
    indices in the M file therefore correspond to LD-score header
    indices shifted by 3 (i.e. ldscore col index = M col index + 3).

    Parameters
    ----------
    src_path : str
        Source ``.l2.M`` or ``.l2.M_5_50`` file path.
    dst_path : str
        Destination path (overwritten if exists).
    annotation_drop_indices : list of int
        0-indexed annotation positions to drop. These are *annotation* indices
        (M-file positions), NOT LD-score header positions. Caller is
        responsible for the index shift.

    Returns
    -------
    list of str
        Surviving M-file values.
    """
    with open(src_path) as f:
        text = f.read().strip()
    if not text:
        raise ValueError(f"{src_path}: empty file")
    parts = text.split("\t")
    drop_set = set(annotation_drop_indices)
    kept = [v for i, v in enumerate(parts) if i not in drop_set]
    os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)
    with open(dst_path, "w") as f:
        f.write("\t".join(kept) + "\n")
    return kept


def _strip_annotation_for_partitioned_h2(
    src_prefix: str,
    dst_prefix: str,
    drop_annotations: tuple = PARTITIONED_H2_DROP_ANNOTATIONS,
    chromosomes: list = None,
    annot_src_prefix: str = None,
) -> dict:
    """Build a filtered private copy of a custom LD score set for partitioned-h2.

    For each chromosome, reads
    ``{src_prefix}{chrom}.l2.ldscore.gz`` plus the sibling ``.l2.M`` /
    ``.l2.M_5_50`` AND ``{annot_src_prefix}{chrom}.annot.gz``, drops the
    columns in ``drop_annotations``, and writes the filtered quadruplet
    under ``{dst_prefix}{chrom}.{l2.ldscore.gz,l2.M,l2.M_5_50,annot.gz}``.

    LDSC ``--overlap-annot`` reads ``.annot.gz`` files alongside LD
    scores via ``parse.annot``; filtering LD scores without also
    filtering annots leaves the annot matrix with the dropped column,
    causing the overlap correction to see different categories than the
    regression and ultimately an ``IOError`` once the annot prefix is
    probed in the tempdir.

    Parameters
    ----------
    src_prefix : str
        LD-score source prefix INCLUDING the trailing ``.`` separator
        (e.g. ``"results/.../ld_scores/custom_pathway."``).
    dst_prefix : str
        Destination prefix INCLUDING the trailing ``.``.
    drop_annotations : tuple of str, default PARTITIONED_H2_DROP_ANNOTATIONS
        Annotation names WITHOUT the ``L2`` suffix.
    chromosomes : list, optional
        Chromosomes to process (default: 1..22).
    annot_src_prefix : str, optional
        Annot source prefix (``{annot_src_prefix}{chrom}.annot.gz``).
        Defaults to ``src_prefix`` with ``/ld_scores/`` substituted by
        ``/annotations/`` — the project-convention sibling layout. Set
        explicitly when the convention does not hold.

    Returns
    -------
    dict
        ``{"chromosomes_processed": int, "kept_annotations": list,
        "dropped_annotations": list}``.

    Raises
    ------
    FileNotFoundError
        If any required source file is missing.
    ValueError
        If header validation fails, a requested drop annotation is
        absent, or the annot prefix cannot be derived from src_prefix.
    """
    if chromosomes is None:
        chromosomes = [str(c) for c in range(1, 23)]

    if annot_src_prefix is None:
        if "/ld_scores/" not in src_prefix:
            raise ValueError(
                f"Cannot derive annot_src_prefix from src_prefix={src_prefix!r} "
                f"(expected '/ld_scores/' segment). Pass annot_src_prefix explicitly."
            )
        annot_src_prefix = src_prefix.replace("/ld_scores/", "/annotations/", 1)

    n_processed = 0
    kept_annotations = None
    for chrom in chromosomes:
        src_ldscore = f"{src_prefix}{chrom}.l2.ldscore.gz"
        src_m = f"{src_prefix}{chrom}.l2.M"
        src_m_5_50 = f"{src_prefix}{chrom}.l2.M_5_50"
        src_annot = f"{annot_src_prefix}{chrom}.annot.gz"
        for label, p in (
            ("ldscore", src_ldscore),
            ("M", src_m),
            ("M_5_50", src_m_5_50),
            ("annot", src_annot),
        ):
            _validate_file(p, f"custom LD score {label} chr{chrom}")

        dst_ldscore = f"{dst_prefix}{chrom}.l2.ldscore.gz"
        dst_m = f"{dst_prefix}{chrom}.l2.M"
        dst_m_5_50 = f"{dst_prefix}{chrom}.l2.M_5_50"
        dst_annot = f"{dst_prefix}{chrom}.annot.gz"

        dropped_indices, kept_header = _drop_columns_from_ldscore(
            src_ldscore, dst_ldscore, drop_annotations
        )
        # M-file indices = ldscore indices shifted by -3 (CHR/SNP/BP not in M).
        m_drop_indices = sorted({i - 3 for i in dropped_indices})
        if any(i < 0 for i in m_drop_indices):
            raise ValueError(
                f"chr{chrom}: dropped index would map to negative M-file column "
                f"(ldscore drop indices = {dropped_indices})"
            )
        _drop_columns_from_m_file(src_m, dst_m, m_drop_indices)
        _drop_columns_from_m_file(src_m_5_50, dst_m_5_50, m_drop_indices)
        _drop_columns_from_annot(src_annot, dst_annot, drop_annotations)

        # First chromosome establishes the canonical kept-annotation list.
        # Subsequent chromosomes must match (defensive — header is identical
        # across chrs in the canonical pipeline, but verify).
        chrom_kept_annotations = [c for c in kept_header[3:]]
        if kept_annotations is None:
            kept_annotations = chrom_kept_annotations
        elif chrom_kept_annotations != kept_annotations:
            raise ValueError(
                f"chr{chrom} kept annotations differ from chr{chromosomes[0]}: "
                f"{chrom_kept_annotations} vs {kept_annotations}"
            )
        n_processed += 1

    logger.info(
        "Filtered partitioned-h2 LD scores: dropped %s, kept %d annotations across %d chromosomes (dst prefix: %s)",
        list(drop_annotations), len(kept_annotations or []), n_processed, dst_prefix,
    )
    return {
        "chromosomes_processed": n_processed,
        "kept_annotations": kept_annotations or [],
        "dropped_annotations": list(drop_annotations),
    }


def run_munge(
    ldsc_dir: str,
    sumstats: str,
    hapmap3: str,
    out: str,
    sample_size: float = None,
    n_case: float = None,
    n_ctrl: float = None,
    trait: str = None,
    bim_prefix: str = None,
) -> dict:
    """Step: munge -- Convert sumstats to LDSC format and run munge_sumstats.py.

    First pre-formats using munge_sumstats_ldsc.py, then runs the official
    LDSC munge_sumstats.py for final munging with HapMap3 merge.

    Parameters
    ----------
    ldsc_dir : str
        Path to LDSC installation directory containing ldsc.py.
    sumstats : str
        Path to harmonized GWAS sumstats TSV (may be gzipped).
    hapmap3 : str
        Path to w_hm3.snplist for allele merging.
    out : str
        Output prefix. Produces {out}.sumstats.gz.
    sample_size : float, optional
        Total sample size. Used for quantitative traits.
    n_case : float, optional
        Number of cases for binary traits.
    n_ctrl : float, optional
        Number of controls for binary traits.
    trait : str, optional
        Trait name for effective-N computation.

    Returns
    -------
    dict
        Stats: {n_snps: int, pre_format_stats: dict}.
    """
    ldsc_py = os.path.join(ldsc_dir, "ldsc.py")
    munge_script = os.path.join(ldsc_dir, "munge_sumstats.py")

    _validate_file(sumstats, "input sumstats")
    _validate_file(hapmap3, "HapMap3 SNP list")

    # Use ldsc.py if munge_sumstats.py doesn't exist as standalone
    if not os.path.exists(munge_script):
        munge_script = ldsc_py

    # Determine effective N
    if trait and trait in TRAIT_TYPE and TRAIT_TYPE[trait] == "binary":
        if n_case is None or n_ctrl is None:
            raise ValueError(
                f"Binary trait '{trait}' requires --n-case and --n-ctrl"
            )
        eff_n = compute_effective_n(n_case, n_ctrl)
        logger.info(
            "Binary trait '%s': effective N = %.1f (cases=%d, controls=%d)",
            trait, eff_n, int(n_case), int(n_ctrl),
        )
    elif sample_size is not None:
        eff_n = float(sample_size)
    else:
        eff_n = None

    # Pre-format using project's munge_sumstats_ldsc.py
    pre_format_dir = os.path.dirname(out) or "."
    os.makedirs(pre_format_dir, exist_ok=True)
    pre_formatted = out + "_preformatted.tsv.gz"

    from munge_sumstats_ldsc import convert_sumstats

    pre_stats = convert_sumstats(
        input_path=sumstats,
        output_path=pre_formatted,
        trait=trait,
        n_case=n_case,
        n_ctrl=n_ctrl,
        n_override=eff_n,
        bim_prefix=bim_prefix,
    )
    logger.info(
        "Pre-formatted %d/%d variants (filtered %d)",
        pre_stats["n_output"], pre_stats["n_input"], pre_stats["n_filtered"],
    )

    # Run official LDSC munge_sumstats.py
    cmd = [
        sys.executable, munge_script,
        "--sumstats", pre_formatted,
        "--merge-alleles", hapmap3,
        "--out", out,
    ]
    if eff_n is not None:
        cmd.extend(["--N", str(int(eff_n))])

    _run_command(cmd, "LDSC munge")

    # T-05-16: Post-munge validation -- check SNP count
    munged_path = out + ".sumstats.gz"
    result = {"pre_format_stats": pre_stats, "n_snps": 0}

    if os.path.exists(munged_path):
        n_snps = _count_sumstats_snps(munged_path)
        result["n_snps"] = n_snps
        if n_snps < MIN_MUNGED_SNPS:
            logger.warning(
                "Munged sumstats has only %d SNPs (expected > %d). "
                "Possible column mismatch or allele filtering. "
                "Check LDSC munge log for details.",
                n_snps, MIN_MUNGED_SNPS,
            )
        else:
            logger.info("Munged sumstats: %d SNPs (OK)", n_snps)
    else:
        logger.error("Munged output not found: %s", munged_path)

    # Clean up pre-formatted intermediate
    if os.path.exists(pre_formatted):
        os.remove(pre_formatted)

    return result


def run_compute_ld_scores(
    ldsc_dir: str,
    annot_prefix: str,
    bfile_prefix: str,
    out_prefix: str,
    hapmap3: str = None,
    chromosomes: list = None,
) -> dict:
    """Step: compute-ld-scores -- Compute LD scores for custom annotations.

    Runs per chromosome: ldsc.py --l2 --bfile ... --annot ... --out ...

    Parameters
    ----------
    ldsc_dir : str
        Path to LDSC installation directory.
    annot_prefix : str
        Annotation file prefix. Files expected at {prefix}.{chr}.annot.gz.
    bfile_prefix : str
        Plink bfile prefix. Files at {prefix}.{chr}.{bed,bim,fam}.
    out_prefix : str
        Output prefix. Produces {prefix}.{chr}.l2.ldscore.gz.
    hapmap3 : str, optional
        Path to HapMap3 SNP list for --print-snps.
    chromosomes : list, optional
        Chromosomes to process (default: 1-22).

    Returns
    -------
    dict
        Stats: {chromosomes_processed: int}.
    """
    ldsc_py = os.path.join(ldsc_dir, "ldsc.py")
    _validate_file(ldsc_py, "LDSC script")

    if chromosomes is None:
        chromosomes = [str(c) for c in range(1, 23)]

    os.makedirs(os.path.dirname(out_prefix) or ".", exist_ok=True)

    # LDSC --print-snps expects a single-column file of SNP IDs (no header).
    # w_hm3.snplist is a 3-column TSV (SNP, A1, A2) which LDSC reads with
    # pd.read_csv(header=None) using comma separator — every row becomes one
    # long string that never matches annotation rsIDs.  Extract column 1 to a
    # temp file so the merge succeeds.
    print_snps_path = None
    if hapmap3 and os.path.exists(hapmap3):
        snp_only = os.path.join(
            os.path.dirname(out_prefix) or ".", ".print_snps_ids.txt"
        )
        with open(hapmap3) as fin, open(snp_only, "w") as fout:
            for line in fin:
                snp_id = line.split()[0]
                if snp_id != "SNP":          # skip header
                    fout.write(snp_id + "\n")
        print_snps_path = snp_only
        logger.info("Extracted %s SNP IDs from %s -> %s",
                     sum(1 for _ in open(snp_only)), hapmap3, snp_only)

    n_processed = 0
    for chrom in chromosomes:
        annot_file = f"{annot_prefix}.{chrom}.annot.gz"
        bfile = f"{bfile_prefix}.{chrom}"

        # Validate annot file exists
        if not os.path.exists(annot_file):
            logger.warning("Annotation file not found: %s, skipping chr%s", annot_file, chrom)
            continue

        cmd = [
            sys.executable, ldsc_py,
            "--l2",
            "--bfile", bfile,
            "--ld-wind-cm", "1",
            "--annot", annot_file,
            "--out", f"{out_prefix}.{chrom}",
        ]

        if print_snps_path:
            cmd.extend(["--print-snps", print_snps_path])

        _run_command(cmd, f"LDSC compute LD scores chr{chrom}")
        n_processed += 1

    return {"chromosomes_processed": n_processed}


def run_partitioned_h2(
    ldsc_dir: str,
    sumstats: str,
    ref_ld_chr: str,
    w_ld_chr: str,
    frqfile_chr: str,
    out: str,
    drop_annotations: tuple = PARTITIONED_H2_DROP_ANNOTATIONS,
) -> dict:
    """Step: h2 -- Run LDSC partitioned heritability.

    CRITICAL: Always includes --overlap-annot flag (anti-pattern prevention).
    Baseline v2.2 must be first entry in --ref-ld-chr (D-04a).

    Per Bug 5 RE-DIAGNOSIS (debug session
    ``.planning/debug/t1-launch10-residual-failures.md`` §
    ``2026-04-18T20:55Z``), LDSC's
    ``ValueError: LD Score matrix condition number is {1e20}`` for this
    annotation set is NOT intrinsic baselineLD collinearity. It is a
    structural mismatch between the ``NEGCTRL_HLA_IMMUNE`` annotation
    (non-zero only on chr6 26–34 Mb, the canonical MHC) and the standard
    LDSC weight file ``weights.hm3_noMHC`` (Finucane 2015, MHC excluded
    by design). The inner-join in ``read_ld_and_sumstats`` zeros the
    ``NEGCTRL_HLA_IMMUNEL2`` column on the regression-eligible SNP set →
    rank-1 deficiency → ``LinAlgError`` at
    ``np.linalg.solve(xtx, xty)`` (jackknife.py:376). ``--invert-anyway``
    bypasses the safety gate but cannot solve a structurally singular
    system.

    Resolution (Carter, Option 1): when the custom_pathway prefix is the
    last entry in ``ref_ld_chr``, this function builds an ephemeral
    filtered copy of the custom LD score files in a per-job temp dir
    with ``NEGCTRL_HLA_IMMUNEL2`` removed, points ``--ref-ld-chr`` at
    the filtered prefix, and cleans up after LDSC completes. The
    canonical ``custom_pathway.{N}.l2.ldscore.gz`` files are unchanged
    so other consumers (LDSC-SEG) continue to see all 11 annotations.

    Quantitative confirmation: post-drop cond(X_filt) on the asthma_EUR
    post-merge subset = 4.97e3 (down from 1.16e20), full rank — well
    below the 1e5 LDSC threshold; ``--invert-anyway`` is no longer needed
    and is intentionally omitted.

    Parameters
    ----------
    ldsc_dir : str
        Path to LDSC installation directory.
    sumstats : str
        Path to munged .sumstats.gz file.
    ref_ld_chr : str
        Comma-separated LD score prefixes. Baseline v2.2 MUST be first.
        Example: "baseline.,custom_pathway."
    w_ld_chr : str
        Weight LD score prefix (e.g., "weights.").
    frqfile_chr : str
        Frequency file prefix (e.g., "1000G.EUR.QC.").
    out : str
        Output prefix. Produces {out}.results.
    drop_annotations : tuple of str, default PARTITIONED_H2_DROP_ANNOTATIONS
        Annotation names (no ``L2`` suffix) to strip from the custom
        LD score prefix (last entry of ``ref_ld_chr``) for this
        invocation only. Pass ``()`` to disable filtering.

    Returns
    -------
    dict
        Parsed results: list of per-annotation enrichment dicts.
    """
    ldsc_py = os.path.join(ldsc_dir, "ldsc.py")
    _validate_file(ldsc_py, "LDSC script")
    _validate_file(sumstats, "munged sumstats")

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    # Build a private filtered copy of the custom LD scores (last entry of
    # ref_ld_chr per D-04a baseline-first convention). The filtered triplet
    # lives under a per-job temp dir and is removed after LDSC returns
    # (success or failure). Skipped if drop_annotations is empty or only
    # one prefix is supplied (no custom side to filter).
    ref_ld_prefixes = ref_ld_chr.split(",")
    effective_ref_ld_chr = ref_ld_chr
    tmp_dir = None
    if drop_annotations and len(ref_ld_prefixes) >= 2:
        custom_prefix_src = ref_ld_prefixes[-1]
        # Sanity: the supplied prefix must end with the conventional separator
        # so per-chrom files resolve as ``{prefix}{chrom}.l2.ldscore.gz``.
        if not custom_prefix_src.endswith("."):
            logger.warning(
                "Custom LD score prefix %r does not end with '.'; "
                "_strip_annotation_for_partitioned_h2 will still concatenate {prefix}{chrom}.",
                custom_prefix_src,
            )
        tmp_dir = tempfile.mkdtemp(prefix="ldsc_partition_h2_filt_")
        # Preserve the basename so log lines and any downstream filename parsing
        # see a recognizable prefix (e.g. ``custom_pathway_phh2.``).
        src_basename = os.path.basename(custom_prefix_src.rstrip("."))
        filtered_prefix_basename = f"{src_basename}_phh2."
        dst_prefix = os.path.join(tmp_dir, filtered_prefix_basename)
        _strip_annotation_for_partitioned_h2(
            src_prefix=custom_prefix_src,
            dst_prefix=dst_prefix,
            drop_annotations=drop_annotations,
        )
        effective_ref_ld_chr = ",".join(ref_ld_prefixes[:-1] + [dst_prefix])
        logger.info(
            "Partitioned h2: rewrote --ref-ld-chr custom prefix %s → %s "
            "(dropped: %s)",
            custom_prefix_src, dst_prefix, list(drop_annotations),
        )

    # CRITICAL: --overlap-annot is always included (anti-pattern prevention).
    # NOTE: --invert-anyway is intentionally OMITTED. The previous
    # condition-number explosion was caused by NEGCTRL_HLA_IMMUNE × no-MHC
    # weights, not intrinsic baseline collinearity — see docstring above.
    # With the filtered custom prefix, post-merge cond(X) ~ 5e3, well below
    # the 1e5 hard threshold.
    cmd = [
        sys.executable, ldsc_py,
        "--h2", sumstats,
        "--ref-ld-chr", effective_ref_ld_chr,
        "--w-ld-chr", w_ld_chr,
        "--overlap-annot",
        "--frqfile-chr", frqfile_chr,
        "--out", out,
    ]

    try:
        _run_command(cmd, "LDSC partitioned h2")
    finally:
        # Best-effort cleanup of the filtered LD score temp dir, even if LDSC
        # raised. Leave the dir behind only if removal itself fails (in which
        # case OS tmpfile cleanup will eventually reap it).
        if tmp_dir and os.path.isdir(tmp_dir):
            try:
                shutil.rmtree(tmp_dir)
            except OSError as cleanup_err:
                logger.warning(
                    "Failed to remove ephemeral filtered LD score dir %s: %s",
                    tmp_dir, cleanup_err,
                )

    # Parse results file
    results_path = out + ".results"
    parsed = parse_ldsc_results(results_path)

    return {"results": parsed, "results_path": results_path}


def parse_ldsc_results(results_path: str) -> list:
    """Parse LDSC .results file into a list of per-annotation dicts.

    Extracts: Category, Prop._SNPs, Prop._h2, Prop._h2_std_error,
    Enrichment, Enrichment_std_error, Enrichment_p, Coefficient,
    Coefficient_z-score.

    Parameters
    ----------
    results_path : str
        Path to LDSC .results file (tab-separated).

    Returns
    -------
    list of dict
        Per-annotation results.
    """
    if not os.path.exists(results_path):
        logger.warning("Results file not found: %s", results_path)
        return []

    parsed = []
    with open(results_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            parsed.append(dict(row))

    logger.info("Parsed %d annotation results from %s", len(parsed), results_path)
    return parsed


def write_h2_summary(results: list, output_path: str) -> None:
    """Write a clean TSV summary of LDSC partitioned h2 results.

    Columns: annotation, prop_snps, prop_h2, prop_h2_se, enrichment,
    enrichment_se, enrichment_p, coefficient, coefficient_z.

    Parameters
    ----------
    results : list of dict
        Parsed LDSC results from parse_ldsc_results.
    output_path : str
        Output TSV path.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    columns = [
        ("Category", "annotation"),
        ("Prop._SNPs", "prop_snps"),
        ("Prop._h2", "prop_h2"),
        ("Prop._h2_std_error", "prop_h2_se"),
        ("Enrichment", "enrichment"),
        ("Enrichment_std_error", "enrichment_se"),
        ("Enrichment_p", "enrichment_p"),
        ("Coefficient", "coefficient"),
        ("Coefficient_z-score", "coefficient_z"),
    ]

    with open(output_path, "w") as f:
        # Write header
        f.write("\t".join(out_name for _, out_name in columns) + "\n")
        for row in results:
            values = [str(row.get(ldsc_name, "")) for ldsc_name, _ in columns]
            f.write("\t".join(values) + "\n")

    logger.info("Wrote h2 summary: %s (%d rows)", output_path, len(results))


def build_ref_ld_chr_arg(baseline_prefix: str, custom_prefix: str) -> str:
    """Build the --ref-ld-chr argument ensuring baseline comes first (D-04a).

    Parameters
    ----------
    baseline_prefix : str
        Baseline v2.2 LD score prefix (e.g., "data/reference/ldsc/baselineLD_v2.2/baselineLD.").
    custom_prefix : str
        Custom annotation LD score prefix (e.g., "results/pathway/ld_scores/custom_pathway.").

    Returns
    -------
    str
        Comma-separated ref-ld-chr argument with baseline first.
    """
    return f"{baseline_prefix},{custom_prefix}"


def main():
    parser = argparse.ArgumentParser(
        description="LDSC partitioned heritability wrapper"
    )
    parser.add_argument(
        "--step",
        required=True,
        choices=["munge", "compute-ld-scores", "h2"],
        help="Pipeline step to run",
    )
    parser.add_argument("--ldsc-dir", required=True, help="Path to LDSC installation")
    parser.add_argument("--sumstats", help="Input sumstats path")
    parser.add_argument("--hapmap3", help="HapMap3 SNP list path")
    parser.add_argument("--sample-size", type=float, help="Total sample size")
    parser.add_argument("--n-case", type=float, help="Number of cases (binary traits)")
    parser.add_argument("--n-ctrl", type=float, help="Number of controls (binary traits)")
    parser.add_argument("--trait", help="Trait name for effective-N")
    parser.add_argument("--annot-prefix", help="Annotation file prefix (compute-ld-scores)")
    parser.add_argument("--bfile-prefix", help="Plink bfile prefix (compute-ld-scores)")
    parser.add_argument("--ref-ld-chr", help="Comma-separated ref LD score prefixes (h2)")
    parser.add_argument("--w-ld-chr", help="Weight LD score prefix (h2)")
    parser.add_argument("--frqfile-chr", help="Frequency file prefix (h2)")
    parser.add_argument("--out", help="Output prefix")
    parser.add_argument("--out-prefix", help="Output prefix (compute-ld-scores)")
    parser.add_argument(
        "--bim-prefix",
        help="1000G bim prefix for chr:pos→rsID remapping in munge (e.g. .../1000G.EUR.QC)",
    )
    parser.add_argument(
        "--chromosomes",
        nargs="+",
        default=[str(c) for c in range(1, 23)],
        help="Chromosomes to process (default: 1-22)",
    )
    args = parser.parse_args()

    if args.step == "munge":
        if not args.sumstats or not args.hapmap3 or not args.out:
            parser.error("--step munge requires --sumstats, --hapmap3, --out")
        run_munge(
            ldsc_dir=args.ldsc_dir,
            sumstats=args.sumstats,
            hapmap3=args.hapmap3,
            out=args.out,
            sample_size=args.sample_size,
            n_case=args.n_case,
            n_ctrl=args.n_ctrl,
            trait=args.trait,
            bim_prefix=args.bim_prefix,
        )

    elif args.step == "compute-ld-scores":
        out_prefix = args.out_prefix or args.out
        if not args.annot_prefix or not args.bfile_prefix or not out_prefix:
            parser.error(
                "--step compute-ld-scores requires --annot-prefix, --bfile-prefix, --out-prefix"
            )
        run_compute_ld_scores(
            ldsc_dir=args.ldsc_dir,
            annot_prefix=args.annot_prefix,
            bfile_prefix=args.bfile_prefix,
            out_prefix=out_prefix,
            hapmap3=args.hapmap3,
            chromosomes=args.chromosomes,
        )

    elif args.step == "h2":
        if not args.sumstats or not args.ref_ld_chr or not args.w_ld_chr or not args.out:
            parser.error(
                "--step h2 requires --sumstats, --ref-ld-chr, --w-ld-chr, --out"
            )
        if not args.frqfile_chr:
            parser.error("--step h2 requires --frqfile-chr")
        result = run_partitioned_h2(
            ldsc_dir=args.ldsc_dir,
            sumstats=args.sumstats,
            ref_ld_chr=args.ref_ld_chr,
            w_ld_chr=args.w_ld_chr,
            frqfile_chr=args.frqfile_chr,
            out=args.out,
        )

        # Write summary TSV alongside results
        if result.get("results"):
            summary_path = args.out + "_summary.tsv"
            write_h2_summary(result["results"], summary_path)


if __name__ == "__main__":
    main()
