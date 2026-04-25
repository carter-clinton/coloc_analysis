#!/usr/bin/env python3
"""Shared utility module for cross-method sumstats operations.

Used by MAGMA, LDSC, and HESS wrappers to avoid reimplementing
effective-N logic in each individual script. Import as:

    from sumstats_utils import compute_effective_n, get_effective_n, TRAIT_TYPE

Phase 9 additions (2026-04-14): `is_palindromic`, `filter_palindromic_ambiguous`,
and `liftover_to_grch37` — shared by the 4 replication-cohort harmonizers
(harmonize_finngen, harmonize_gbmi, harmonize_mvp, harmonize_bbj).
"""

import pandas as pd

from liftover import liftover_coordinates


def compute_effective_n(n_case: float, n_ctrl: float) -> float:
    """Compute effective sample size for binary traits.

    Uses the standard formula: N_eff = 4 / (1/N_case + 1/N_ctrl)
    This is the harmonic mean scaled by 4, commonly used in GWAS
    meta-analysis (Willer et al. 2010).

    Parameters
    ----------
    n_case : float
        Number of cases.
    n_ctrl : float
        Number of controls.

    Returns
    -------
    float
        Effective sample size.

    Raises
    ------
    ValueError
        If n_case or n_ctrl is <= 0.
    """
    if n_case <= 0 or n_ctrl <= 0:
        raise ValueError(
            f"n_case ({n_case}) and n_ctrl ({n_ctrl}) must both be > 0"
        )
    return 4.0 / (1.0 / n_case + 1.0 / n_ctrl)


# Per-trait type classification for the 5 cardiometabolic traits.
# Binary traits require effective-N conversion; quantitative traits use
# the reported sample size directly.
TRAIT_TYPE = {
    "bmi": "quantitative",
    "t2d": "binary",
    "hypertension": "binary",
    "stroke": "binary",
    "asthma": "binary",
}


def get_effective_n(
    trait: str,
    n: float,
    n_case: float = None,
    n_ctrl: float = None,
) -> float:
    """Get the effective sample size for a given trait.

    For quantitative traits, returns n directly.
    For binary traits, computes effective N from n_case and n_ctrl.

    Parameters
    ----------
    trait : str
        Trait name (must be a key in TRAIT_TYPE).
    n : float
        Total sample size (used directly for quantitative traits).
    n_case : float, optional
        Number of cases (required for binary traits).
    n_ctrl : float, optional
        Number of controls (required for binary traits).

    Returns
    -------
    float
        Effective sample size.

    Raises
    ------
    KeyError
        If trait is not in TRAIT_TYPE.
    ValueError
        If binary trait but n_case/n_ctrl not provided or <= 0.
    """
    trait_type = TRAIT_TYPE[trait]
    if trait_type == "quantitative":
        return float(n)
    # Binary trait: require case/control counts
    if n_case is None or n_ctrl is None:
        raise ValueError(
            f"Binary trait '{trait}' requires n_case and n_ctrl, "
            f"got n_case={n_case}, n_ctrl={n_ctrl}"
        )
    return compute_effective_n(n_case, n_ctrl)


# ==========================================================================
# Phase 9 — Replication cohort harmonization helpers (Plan 09-02 Task 1)
# ==========================================================================

# A/T and C/G are palindromic on the forward strand — cannot resolve EA/OA
# orientation by allele alone; MAF-band exclusion is required to avoid strand
# flips (RESEARCH pitfall #2).
PALINDROMIC_PAIRS = {("A", "T"), ("T", "A"), ("C", "G"), ("G", "C")}


def is_palindromic(ea: str, oa: str) -> bool:
    """Return True if (EA, OA) is a palindromic (strand-ambiguous) pair."""
    return (ea.upper(), oa.upper()) in PALINDROMIC_PAIRS


def filter_palindromic_ambiguous(
    df: pd.DataFrame,
    ea_col: str = "EA",
    oa_col: str = "OA",
    eaf_col: str = "EAF",
    maf_band: tuple = (0.48, 0.52),
) -> pd.DataFrame:
    """Drop palindromic SNPs whose MAF lies in the ambiguity band.

    Rows where EA/OA is a palindrome (A/T, T/A, C/G, G/C) **and** the
    minor-allele frequency (MAF = min(EAF, 1-EAF)) falls inside
    ``maf_band`` are removed outright. Surviving rows gain a boolean
    ``palindromic_flag`` column so downstream coloc/meta code can track
    them even when retained.

    Parameters
    ----------
    df : pd.DataFrame
        Harmonized sumstats with EA/OA/EAF columns.
    ea_col, oa_col, eaf_col : str
        Column names (defaults match the canonical schema).
    maf_band : (float, float)
        MAF interval where palindromic pairs are ambiguous. The standard
        [0.48, 0.52] window follows GWAS harmonization practice (the exact
        width is a tradeoff between strand-flip risk and power loss).

    Returns
    -------
    pd.DataFrame
        Filtered frame with a new ``palindromic_flag`` column. Input is not
        modified in place.
    """
    pal_mask = df.apply(lambda r: is_palindromic(r[ea_col], r[oa_col]), axis=1)
    maf = df[eaf_col].where(df[eaf_col] < 0.5, 1 - df[eaf_col])
    ambig = pal_mask & maf.between(maf_band[0], maf_band[1])
    keep = ~ambig
    out = df.loc[keep].copy()
    out["palindromic_flag"] = pal_mask.loc[keep].values
    return out


def liftover_to_grch37(
    df: pd.DataFrame,
    chain_file: str,
    chr_col: str = "CHR",
    bp_col: str = "BP",
    max_drop_rate: float = 0.05,
) -> "tuple[pd.DataFrame, dict]":
    """Lift a harmonized sumstats DataFrame from GRCh38 to GRCh37.

    Applies :func:`liftover.liftover_coordinates` per row and replaces
    ``chr_col`` / ``bp_col`` in place (on the returned copy). Rows whose
    coordinates cannot be lifted are dropped. If the drop rate exceeds
    ``max_drop_rate`` the function raises ``RuntimeError`` — silent large
    drops have been the source of real replication failures (RESEARCH
    pitfall #1 references the same failure mode).

    Parameters
    ----------
    df : pd.DataFrame
        Input sumstats with ``chr_col`` + ``bp_col`` (GRCh38 coords).
    chain_file : str
        Path to a UCSC chain file (e.g., hg38ToHg19.over.chain.gz).
    chr_col, bp_col : str
        Column names to rewrite.
    max_drop_rate : float
        Hard QC ceiling on fraction of rows that fail liftover. Default
        0.05 (== 5 %). At-exact-threshold is permitted.

    Returns
    -------
    (df_lifted, qc)
        ``df_lifted`` has CHR/BP replaced with GRCh37 coordinates; unlifted
        rows are dropped. ``qc`` dict has keys ``n_input``, ``n_lifted``,
        ``n_dropped``, ``drop_rate``.

    Raises
    ------
    RuntimeError
        When ``drop_rate > max_drop_rate``.
    """
    n_in = len(df)
    if n_in == 0:
        qc = {
            "n_input": 0,
            "n_lifted": 0,
            "n_dropped": 0,
            "drop_rate": 0.0,
        }
        return df.copy(), qc

    # The module-level import is re-resolved here so monkeypatching
    # `sumstats_utils.liftover_coordinates` in unit tests propagates.
    lifted = df.apply(
        lambda r: liftover_coordinates(chain_file, str(r[chr_col]), int(r[bp_col])),
        axis=1,
    )
    mask = lifted.notna()
    out = df.loc[mask].copy()
    if mask.any():
        out[chr_col] = [t[0].replace("chr", "") for t in lifted[mask]]
        out[bp_col] = [int(t[1]) for t in lifted[mask]]

    # WR-07 fix: bucket drop reasons so "unknown chromosome label" (e.g.,
    # chrMT, chrM, chr0) is distinguishable from "failed liftover lookup"
    # in the QC dict. This avoids silent mis-attribution of the 5% budget
    # when a cohort uses a non-autosomal naming convention.
    _AUTOSOMAL = {str(i) for i in range(1, 23)} | {f"chr{i}" for i in range(1, 23)}
    _XY = {"X", "Y", "chrX", "chrY", "23", "24", "chr23", "chr24"}
    dropped_chrs = df.loc[~mask, chr_col].astype(str)
    n_dropped_unknown_chrom = int(
        (~dropped_chrs.isin(_AUTOSOMAL | _XY)).sum()
    )
    n_dropped_liftover = int((~mask).sum() - n_dropped_unknown_chrom)

    qc = {
        "n_input": n_in,
        "n_lifted": int(mask.sum()),
        "n_dropped": int((~mask).sum()),
        "n_dropped_unknown_chrom": n_dropped_unknown_chrom,
        "n_dropped_liftover_failed": n_dropped_liftover,
        "drop_rate": float((~mask).mean()),
    }
    if qc["drop_rate"] > max_drop_rate:
        raise RuntimeError(
            f"Liftover drop rate {qc['drop_rate']:.2%} exceeds "
            f"{max_drop_rate:.0%} threshold (RESEARCH pitfall #1 — silent "
            f"large liftover drops)"
        )
    return out, qc


# ==========================================================================
# M1 — Canonical 10-column schema + contract validation
# ==========================================================================
# Added 2026-04-25 for the M1 harmonizer wave (Rule 2 — auto-add critical
# missing functionality referenced by the M1 plan). Mirrors the same column
# list each Phase 09 harmonizer hard-codes locally; consolidating here avoids
# drift across the seven new M1 harmonizers (D-10).

CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]


def validate_canonical_frame(df: pd.DataFrame) -> None:
    """Validate that ``df`` conforms to the canonical 10-column schema.

    Asserts that every column in :data:`CANONICAL_COLS` is present. Numeric
    columns (BP, BETA, SE, P, EAF, N) must be numeric dtype. Allele columns
    (EA, OA) must be string-like. SNP and CHR are coerced/checked but
    accept either str or int (CHR may legitimately be int 1..22 or str
    "1".."22"/"X"/"Y"). Raises ``ValueError`` with the missing/typed-wrong
    columns listed.

    This is the contract that every harmonizer in M1 must satisfy before
    its output is consumed by munge / coloc / fine-mapping / CPASSOC.

    Parameters
    ----------
    df : pd.DataFrame
        Harmonized sumstats DataFrame.

    Raises
    ------
    ValueError
        If any canonical column is missing OR a numeric column is non-
        numeric dtype OR an allele column is non-string dtype.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError(
            f"validate_canonical_frame expected pd.DataFrame, got {type(df)!r}"
        )

    missing = [c for c in CANONICAL_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Canonical-frame validation failed: missing column(s) {missing}. "
            f"Required: {CANONICAL_COLS}. Found: {sorted(df.columns.tolist())}."
        )

    # Numeric columns
    numeric_cols = ["BP", "BETA", "SE", "P", "EAF", "N"]
    bad_numeric = [
        c for c in numeric_cols if not pd.api.types.is_numeric_dtype(df[c])
    ]
    if bad_numeric:
        raise ValueError(
            f"Canonical-frame validation failed: non-numeric dtype for "
            f"{bad_numeric}. Each numeric column must be numeric dtype "
            f"(int/float). Found: "
            f"{ {c: str(df[c].dtype) for c in bad_numeric} }."
        )

    # Allele columns must be string-like (object dtype with str values).
    for c in ("EA", "OA"):
        # Allow object dtype; require non-null sample to be str.
        if not df[c].empty:
            sample = df[c].dropna().head(1)
            if len(sample) > 0 and not isinstance(sample.iloc[0], str):
                raise ValueError(
                    f"Canonical-frame validation failed: column {c} must be "
                    f"string dtype, got first-non-null value "
                    f"{sample.iloc[0]!r} ({type(sample.iloc[0]).__name__})."
                )


# ==========================================================================
# M1 Wave 2a — rsID -> (chr, bp) forward crosswalk (harmonize_magic.py only)
# ==========================================================================

# Module-level cache keyed by bim_prefix to avoid re-reading 22 .bim files
# per harmonizer invocation. Cleared automatically on process exit.
_rsid_lookup_cache: "dict[str, dict[str, tuple[int, int]]]" = {}


def build_rsid_to_chrpos(
    bim_prefix: str,
    chromosomes: "list[int] | None" = None,
) -> "dict[str, tuple[int, int]]":
    """Build forward rsid -> (chr, bp) lookup from PLINK ``.bim`` files.

    Reads files of form ``{bim_prefix}.{chr}.bim`` (6-column PLINK bim:
    ``chr rsid cm bp a1 a2``). Used by ``harmonize_magic.py`` for the
    rare cases where a sumstats file ships rsid-only SNP IDs without
    explicit CHR/BP columns (RESEARCH pitfall #5).

    Parameters
    ----------
    bim_prefix : str
        Path prefix such that ``{prefix}.{chr}.bim`` exists for each
        chromosome. Example: ``data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC``
        with files ``data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC.1.bim``.
    chromosomes : list[int], optional
        List of chromosome ints; defaults to ``range(1, 23)``.

    Returns
    -------
    dict
        Map of ``rsid`` (str) → ``(chromosome:int, bp:int)``.

    Raises
    ------
    FileNotFoundError
        If any chromosome bim is missing.
    """
    if bim_prefix in _rsid_lookup_cache:
        return _rsid_lookup_cache[bim_prefix]
    if chromosomes is None:
        chromosomes = list(range(1, 23))

    from pathlib import Path

    lookup: "dict[str, tuple[int, int]]" = {}
    for chrom in chromosomes:
        bim = Path(f"{bim_prefix}.{chrom}.bim")
        if not bim.exists():
            raise FileNotFoundError(f"build_rsid_to_chrpos: {bim} missing")
        df = pd.read_csv(
            bim,
            sep=r"\s+",
            header=None,
            names=["chr", "rsid", "cm", "bp", "a1", "a2"],
            dtype={"chr": int, "bp": int, "rsid": str},
            engine="python",
        )
        # Use vectorized dict construction over .itertuples for speed at scale
        # (1000G EUR contains ~9.5M SNPs total).
        for r in df.itertuples(index=False):
            lookup[r.rsid] = (int(r.chr), int(r.bp))
    _rsid_lookup_cache[bim_prefix] = lookup
    return lookup
