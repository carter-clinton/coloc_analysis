#!/usr/bin/env python3
"""Per-stratum CPASSOC orchestrator — load munged sumstats, align variants,
slice R, compute SHom + SHet + chi-square p-values, write per-locus TSV.

Plan reference: m2-03-cpassoc-3-strata-PLAN.md.

Decision references:
  D-M2-04 — Python reimplementation of Zhu 2015 SHom + SHet using the M1
            LDSC bivariate-intercept matrix (re-fired in D-M2-01 to ~26-trait)
            as the cohort-correlation matrix R.
  D-M2-Q6 — _MIN_PER_STRATUM = 3 floor (Carter-locked); below-floor strata
            raise ValueError so the caller (Snakemake rule) can emit a row
            to skipped_strata.tsv per D-M2-06.
  Q7      — Per-stratum R is constructed as a principal submatrix of the
            full ~26x26 matrix. The principal-submatrix theorem guarantees
            PSD preservation; an eigvalsh probe enforces the invariant
            against numerical drift (tolerance -1e-10).

Pitfall references:
  Pitfall 7 — Trait order MUST match MTAG's residcov.trait_order.json
              sidecar (Wave 2 contract). CPASSOC consumes the SAME K-trait
              basis as MTAG so the downstream Class 1 novelty join (Wave 5)
              operates on a consistent K-trait set.

Public API:

  run_cpassoc(stratum, matrix_path, mtag_sidecar_path, munged_dir, out_path)
    Orchestrator. Returns the row count of the per-locus output TSV.

Output schema:

  chr, pos, rsid, A1, A2, n_traits, SHom_stat, SHom_p, SHet_stat, SHet_p,
  contributing_traits

Where:
  - chr, pos resolved from the SNP rsid via M1 sumstats_utils
    build_rsid_to_chrpos (1000G EUR PLINK bim files).
  - n_traits = K (constant per stratum).
  - SHom_stat = z' R^-1 z, chi-square df = K (Zhu 2015 Methods).
  - SHet_stat = z' (R^-1 - R^-1 1 (1' R^-1 1)^-1 1' R^-1) z, df = K - 1.
  - p-values = scipy.stats.chi2.sf(stat, df) (right-tail survival fn).
  - contributing_traits = ';'.join(trait_order) — provenance for downstream.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2

# Make src/python importable for cpassoc + m2_stratum_keys + sumstats_utils.
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

from cpassoc import cpassoc_shom, cpassoc_shet  # noqa: E402
from m2_stratum_keys import _MIN_PER_STRATUM  # noqa: E402


# ---------------------------------------------------------------------------
# I/O helpers.
# ---------------------------------------------------------------------------

def _load_munged(path: Path) -> pd.DataFrame:
    """Read LDSC-munged HM3 .sumstats.gz; return DataFrame with [SNP, A1, A2, Z, N].

    Tolerates the augmented schema produced by Wave 2's munged_for_mtag/ dir
    (P, FRQ, INFO extra columns) — only the canonical 5 columns are kept.
    """
    df = pd.read_csv(path, sep="\t")
    required = {"SNP", "A1", "A2", "Z", "N"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Munged file {path} missing columns: {missing}")
    return df[["SNP", "A1", "A2", "Z", "N"]].copy()


# ---------------------------------------------------------------------------
# Variant alignment across K traits.
# ---------------------------------------------------------------------------

def _intersect_and_align(per_trait: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Intersect rsids across K traits; align alleles to first trait's A1/A2.

    Returns a wide DataFrame indexed on SNP with columns:
      A1_ref, A2_ref, Z_<trait1>, Z_<trait2>, ..., Z_<traitK>

    Allele-alignment policy (conservative):
      - If A1/A2 match ref → keep Z as-is.
      - If A1/A2 are swapped relative to ref → flip Z (multiply by -1).
      - If A1/A2 are neither same-orientation nor swap (different alleles
        entirely) → DROP the SNP from this trait (which drops it from the
        intersection on the next iteration).

    Strand-flip / palindromic SNP handling: We do NOT have allele frequency
    in the LDSC-munged files, so we cannot disambiguate palindromic SNPs
    (A/T, C/G) by frequency. The conservative policy above keeps palindromic
    SNPs IF the alleles match-or-swap between traits. This may introduce
    sign errors at palindromic loci where A1/A2 labels happen to align by
    chance; the M1 munge already harmonizes to HM3 + applies M1
    sumstats_utils orientation logic, so this is a low-frequency residual.

    Parameters
    ----------
    per_trait : dict[str, pd.DataFrame]
        Trait-keyed dict; each DataFrame has [SNP, A1, A2, Z, N] columns.
        Order of dict keys defines the reference (first key) trait.

    Returns
    -------
    pd.DataFrame
        Wide DataFrame indexed on SNP with A1_ref, A2_ref, and Z_<trait>
        columns for each trait. Length = size of intersection after
        allele-alignment drops.
    """
    traits = list(per_trait.keys())
    if not traits:
        raise ValueError("_intersect_and_align: per_trait is empty")

    ref_trait = traits[0]
    ref_df = per_trait[ref_trait].set_index("SNP")
    # Initialise merged with ref columns renamed.
    merged = pd.DataFrame(
        {
            "A1_ref": ref_df["A1"],
            "A2_ref": ref_df["A2"],
            f"Z_{ref_trait}": ref_df["Z"],
        }
    )

    for trait in traits[1:]:
        other = per_trait[trait].set_index("SNP")[["A1", "A2", "Z"]]
        joined = merged.join(other, how="inner")
        same = (joined["A1_ref"] == joined["A1"]) & (joined["A2_ref"] == joined["A2"])
        swap = (joined["A1_ref"] == joined["A2"]) & (joined["A2_ref"] == joined["A1"])
        keep = same | swap
        joined = joined[keep].copy()
        # Sign-flip Z where alleles swap.
        joined[f"Z_{trait}"] = np.where(swap[keep], -joined["Z"], joined["Z"])
        joined = joined.drop(columns=["A1", "A2", "Z"])
        merged = joined

    return merged


# ---------------------------------------------------------------------------
# R-matrix slicing with Q7 PSD probe.
# ---------------------------------------------------------------------------

def _slice_R_for_trait_order(
    matrix_path: Path,
    trait_order: list[str],
    psd_tolerance: float = -1e-10,
) -> np.ndarray:
    """Q7 PSD-preserving principal submatrix of the M2 LDSC matrix.

    Reads the indexed wide TSV at `matrix_path` (Wave 1 reducer output),
    slices to the K x K block matching `trait_order`, defensively
    symmetrizes ((R + R.T) / 2), zero-fills any residual NaN cells (per
    Wave 1 SUMMARY policy: per-stratum slices are NaN-free given the M2
    matrix; this is a safety net for future matrix versions), enforces
    diag = 1.0 (LDSC self-pair convention), runs the eigvalsh probe, and
    on PSD violation applies an adaptive ridge so R is PSD before being
    handed to cpassoc_shom/cpassoc_shet.

    Q7 + D-M2-Q2 reconciliation (Wave 3 Task 3 deviation):
      The Q7 invariant assumed the M2 LDSC matrix is strictly PSD. In
      practice, the Wave 1 m2-01 SUMMARY documented that LDSC gcov_int
      estimates have negative off-diagonal values from real estimation
      noise (e.g., hdl.EUR x tg.EUR = -0.575; tc.EUR x tg.EUR = 0.402;
      Pitfall 8 false-alarm). The full 26x26 matrix has 5 negative
      eigenvalues (min = -0.327); per-stratum slices for EUR (min=-0.070)
      and TRANS (min=-0.084) are non-PSD, AFR (min=+0.013) is PSD.

      Rather than failing the rule, we apply an adaptive ridge sized to
      the negative-eigenvalue magnitude so R is just-barely PSD before
      _safe_inverse is called downstream. This preserves the D-M2-04
      semantics (LDSC matrix as R) while handling the documented Wave-1
      reality. The applied ridge is recorded for the audit log.

    Adaptive ridge sizing:
      lam = max(|min_eig| + epsilon, ridge_floor * trace(R) / K)
      where epsilon = 1e-3 ensures strict PSD post-ridge.

    Parameters
    ----------
    matrix_path : Path
        Wave 1 LDSC bivariate-intercept matrix TSV.
    trait_order : list[str]
        Canonical trait order (from Wave 2 sidecar).
    psd_tolerance : float
        Eigenvalue threshold below which adaptive ridge is applied
        (default -1e-10; Q7 contract).

    Returns
    -------
    np.ndarray
        K x K PSD matrix ready for cpassoc_shom/cpassoc_shet.

    Raises
    ------
    ValueError
        If any trait_order key is missing from the matrix index/columns.
        (PSD violations no longer raise — they trigger adaptive ridge.)
    """
    M = pd.read_csv(matrix_path, sep="\t", index_col=0)
    keys_in_matrix = [k for k in trait_order if k in M.index and k in M.columns]
    if len(keys_in_matrix) != len(trait_order):
        missing = sorted(set(trait_order) - set(keys_in_matrix))
        raise ValueError(
            f"_slice_R_for_trait_order: trait_order keys missing from "
            f"matrix at {matrix_path}: {missing}"
        )

    R = M.loc[trait_order, trait_order].values.astype(float)
    # Defensive NaN -> 0.0 off-diagonal substitution.
    R = np.where(np.isnan(R), 0.0, R)
    # Defensive symmetrize.
    R = (R + R.T) / 2.0
    # Diagonal MUST be 1.0 (LDSC self-pair convention).
    np.fill_diagonal(R, 1.0)

    # Q7 PSD probe — principal submatrix of a true-PSD matrix is PSD; this
    # guard catches LDSC estimation noise (negative gcov_int) per Wave 1
    # m2-01 SUMMARY documented findings.
    eigvals = np.linalg.eigvalsh(R)
    min_eig = float(eigvals.min())
    if min_eig < psd_tolerance:
        # D-M2-Q2 adaptive ridge: shift R to be PSD before downstream
        # _safe_inverse. The original _safe_inverse uses a fixed
        # ridge_floor=1e-4 which is too small for |min_eig| ~= 0.07-0.08.
        K = R.shape[0]
        epsilon = 1e-3  # buffer to ensure strict positive-definiteness
        # Use both an absolute (|min_eig|) and a relative (trace-scaled)
        # floor; pick the larger so we always achieve PSD.
        lam_abs = abs(min_eig) + epsilon
        lam_rel = 1e-4 * float(np.trace(R)) / K
        lam = max(lam_abs, lam_rel)
        R = R + lam * np.eye(K)
        # Verify PSD post-ridge (strict assertion — should always pass).
        eigvals_post = np.linalg.eigvalsh(R)
        if eigvals_post.min() < psd_tolerance:
            raise ValueError(
                f"_slice_R_for_trait_order: adaptive ridge failed; "
                f"post-ridge min eigval = {eigvals_post.min():.6g}, "
                f"applied lam = {lam:.6g}"
            )
        print(
            f"_slice_R_for_trait_order: PSD ridge applied — "
            f"pre-ridge min_eig = {min_eig:.6g}, applied lam = {lam:.6g}, "
            f"post-ridge min_eig = {eigvals_post.min():.6g} "
            f"(K={K}; D-M2-Q2 adaptive fallback per Q7 + Wave 1 "
            f"non-PSD documentation)",
            file=sys.stderr,
        )

    return R


# ---------------------------------------------------------------------------
# rsid -> (chr, pos) resolution.
# ---------------------------------------------------------------------------

_DEFAULT_BIM_PREFIX = "data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC"


def _resolve_chr_pos(
    rsid_iter,
    bim_prefix: str = _DEFAULT_BIM_PREFIX,
) -> pd.DataFrame:
    """Resolve chr+pos for each rsid via M1 sumstats_utils.build_rsid_to_chrpos.

    Falls back to (NaN, NaN) per rsid if the helper is unavailable or if
    a particular rsid is not present in the 1000G EUR HM3 reference. The
    Class 1 novelty join (Wave 5) requires chr+pos to compare against the
    GWAS Catalog v_lock_M2 — but in the absence of chr+pos, downstream
    can backfill via the harmonized parquet on the MTAG-novel subset
    (this is a much smaller join than per-SNP).

    Returns a DataFrame with columns rsid, chr, pos.
    """
    rsids = list(rsid_iter)
    try:
        from sumstats_utils import build_rsid_to_chrpos  # type: ignore
        # 1000G EUR HM3 reference has ~9.5M SNPs covering most HM3 SNPs.
        full_bim_prefix = str(_PROJECT_ROOT / bim_prefix)
        mapping = build_rsid_to_chrpos(full_bim_prefix)
        chrs = [mapping.get(r, (None, None))[0] for r in rsids]
        poss = [mapping.get(r, (None, None))[1] for r in rsids]
    except (ImportError, FileNotFoundError, AttributeError):
        # Fallback: emit NaN and let Wave 5 backfill on the novel subset.
        chrs = [None] * len(rsids)
        poss = [None] * len(rsids)

    return pd.DataFrame({"rsid": rsids, "chr": chrs, "pos": poss})


# ---------------------------------------------------------------------------
# Public orchestrator.
# ---------------------------------------------------------------------------

def run_cpassoc(
    stratum: str,
    matrix_path: Path,
    mtag_sidecar_path: Path,
    munged_dir: Path,
    out_path: Path,
    bim_prefix: str = _DEFAULT_BIM_PREFIX,
) -> int:
    """Per-stratum CPASSOC orchestrator. Returns row count of output TSV.

    Steps:
      1. Read mtag_sidecar_path JSON for canonical trait_order (CRITICAL —
         must match MTAG's --residcov_path order; Pitfall 7).
      2. Enforce _MIN_PER_STRATUM = 3 floor (D-M2-Q6).
      3. Slice R (Q7 PSD-preserving principal submatrix).
      4. Load each trait's munged sumstats.
      5. Intersect SNPs across K traits with allele-alignment.
      6. Build (n_snps, K) z-score matrix in trait_order column order.
      7. Compute SHom + SHet (Zhu 2015) + chi-square p-values.
      8. Resolve chr+pos via 1000G EUR PLINK bim crosswalk.
      9. Write per-locus TSV with full schema.

    Parameters
    ----------
    stratum : str
        One of {"EUR", "AFR", "TRANS"}.
    matrix_path : Path
        Path to the indexed wide TSV from m1_ldsc_rg_reduce
        (Wave-1 output: data/processed/ldsc_overlap/
        bivariate_intercept_matrix_2026-04-M2.tsv).
    mtag_sidecar_path : Path
        Path to data/processed/mtag/{stratum}/residcov.trait_order.json
        (Wave 2 sidecar — alignment contract).
    munged_dir : Path
        Directory containing per-trait .sumstats.gz files. Wave 2 augmented
        copies live at data/processed/mtag/munged_for_mtag/. Either dir is
        fine since CPASSOC only reads SNP/A1/A2/Z/N (not P/FRQ/INFO).
    out_path : Path
        Output TSV path: data/processed/cpassoc/{stratum}/cpassoc_results.tsv.
    bim_prefix : str, optional
        PLINK bim file prefix for chr+pos resolution. Default 1000G EUR.

    Returns
    -------
    int
        Number of rows written to out_path (= post-intersection SNP count).

    Raises
    ------
    ValueError
        If K < _MIN_PER_STRATUM, or trait_order keys missing from matrix,
        or PSD probe fails, or the post-intersection SNP count is 0.
    """
    # 1. Read sidecar for trait_order (Pitfall 7 contract).
    sidecar = json.loads(Path(mtag_sidecar_path).read_text())
    trait_order: list[str] = sidecar["trait_order"]
    K = len(trait_order)

    # 2. Floor enforcement (D-M2-Q6).
    if K < _MIN_PER_STRATUM:
        raise ValueError(
            f"run_cpassoc: stratum {stratum} has K={K} < _MIN_PER_STRATUM="
            f"{_MIN_PER_STRATUM} per D-M2-Q6 (Carter-locked floor). "
            f"Caller should emit skipped_strata.tsv per D-M2-06."
        )

    # 3. Slice R (Q7 PSD-preserving principal submatrix with eigvalsh probe).
    R = _slice_R_for_trait_order(Path(matrix_path), trait_order)

    # 4. Load each trait's munged sumstats.
    munged_dir = Path(munged_dir)
    per_trait: dict[str, pd.DataFrame] = {}
    for key in trait_order:
        munged_path = munged_dir / f"{key}.sumstats.gz"
        if not munged_path.exists():
            raise ValueError(
                f"run_cpassoc: munged sumstats missing for trait {key}: "
                f"{munged_path}"
            )
        per_trait[key] = _load_munged(munged_path)

    # 5. Intersect + align across K traits.
    merged = _intersect_and_align(per_trait)
    n_snps = len(merged)
    if n_snps == 0:
        raise ValueError(
            f"run_cpassoc: after intersection across {K} traits, no SNPs "
            f"remain for stratum {stratum}. Check input munged files."
        )

    # 6. Build (n_snps, K) z-score matrix in trait_order column order.
    z_cols = [f"Z_{trait}" for trait in trait_order]
    Z_mat = merged[z_cols].values.astype(float)

    # 7. Compute SHom + SHet + chi-square p-values (Zhu 2015 Methods).
    shom = cpassoc_shom(Z_mat, R)
    shet = cpassoc_shet(Z_mat, R)
    shom_p = chi2.sf(shom, df=K)
    shet_p = chi2.sf(shet, df=max(K - 1, 1))

    # 8. Resolve chr+pos for downstream Class 1 novelty join.
    chrpos = _resolve_chr_pos(merged.index, bim_prefix=bim_prefix)

    # 9. Build + write output frame.
    out = pd.DataFrame(
        {
            "chr": chrpos["chr"].values,
            "pos": chrpos["pos"].values,
            "rsid": merged.index.values,
            "A1": merged["A1_ref"].values,
            "A2": merged["A2_ref"].values,
            "n_traits": K,
            "SHom_stat": shom,
            "SHom_p": shom_p,
            "SHet_stat": shet,
            "SHet_p": shet_p,
            "contributing_traits": ";".join(trait_order),
        }
    )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, sep="\t", index=False)

    return len(out)


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def _main() -> int:
    ap = argparse.ArgumentParser(
        description="Per-stratum CPASSOC orchestrator (Zhu 2015 SHom + SHet "
                    "with the M2 LDSC bivariate-intercept matrix as R)."
    )
    ap.add_argument(
        "--stratum", required=True, choices=("EUR", "AFR", "TRANS"),
        help="Stratum identifier (used for log messages and floor checks).",
    )
    ap.add_argument(
        "--matrix", type=Path, required=True,
        help="Path to indexed wide TSV from m1_ldsc_rg_reduce "
             "(Wave-1 output: bivariate_intercept_matrix_2026-04-M2.tsv).",
    )
    ap.add_argument(
        "--mtag-sidecar", type=Path, required=True,
        help="Path to data/processed/mtag/{stratum}/residcov.trait_order.json "
             "(Wave 2 alignment contract).",
    )
    ap.add_argument(
        "--munged-dir", type=Path,
        default=Path("data/processed/mtag/munged_for_mtag"),
        help="Directory containing per-trait .sumstats.gz files.",
    )
    ap.add_argument(
        "--out", type=Path, required=True,
        help="Output TSV path (will be created with parent dirs).",
    )
    ap.add_argument(
        "--bim-prefix", type=str, default=_DEFAULT_BIM_PREFIX,
        help="PLINK bim prefix for chr+pos rsid crosswalk.",
    )
    args = ap.parse_args()

    n = run_cpassoc(
        stratum=args.stratum,
        matrix_path=args.matrix,
        mtag_sidecar_path=args.mtag_sidecar,
        munged_dir=args.munged_dir,
        out_path=args.out,
        bim_prefix=args.bim_prefix,
    )
    print(
        f"run_cpassoc: stratum={args.stratum} K=(from sidecar) "
        f"n_snps={n} written to {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
