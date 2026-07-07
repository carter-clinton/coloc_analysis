"""Pre-registered AFR native-plink LD NaN conditioning (ROADMAP 999.1 §3).

``condition_ld_matrix`` applies the off-diagonal ``NaN -> 0`` policy pre-registered
in ``osf-amendment-afr-native-ld-nan-psd-2026-07-03.md`` (OSF file ``tcujq`` on
``az52u``, posted 2026-07-04) for the All of Us AFR native-plink per-region LD panel.

The RAW panel ``.npz`` is CORRECT to RAISE on any NaN
(``plink_ld_to_npz.read_square_bin`` — a ``0/0 -> NaN`` plink entry names its likely
source variant and demands an explicit policy). This module is the strictly
DOWNSTREAM, ADDITIVE repair stage that supplies that explicit policy; it does NOT
modify the raw contract (``read_square_bin`` / ``content_verify_npz`` /
``ld_npz_to_rds.R`` stay FROZEN).

Policy (amendment (a)(b)(d)):

  (a) Topology branch.
      - A FULLY-NaN variant row (off-diagonal NaN count >= n_var-1 — a
        zero-variance / monomorphic-within-analysis-set source, robust to plink
        keeping the diagonal at 1.0) is NOT zero-conditioned: RAISE and direct an
        upstream MAF / missingness QC drop on the actual analysis sample set.
      - Otherwise (isolated off-diagonal NaN pairs, the observed region-1 case) each
        undefined off-diagonal entry is set to ``0.0`` at BOTH ``(i, j)`` and
        ``(j, i)``. The diagonal (1.0 by construction) is untouched.
  (b) Zeroing ceiling. ``NaN -> 0`` is applied only when
      ``n_zeroed_pairs <= ceiling_frac * n_var`` (default ``ceiling_frac = 0.0005``,
      the pre-registered 0.05 percent). A region exceeding the ceiling is a substrate
      anomaly: RAISE (``BRANCH_AFR_COND_DEFERRED``) — re-diagnose + disclose as a
      deviation; never silently condition a large NaN fraction.
  (d) Provenance (egress-safe aggregates only). The returned record carries
      ``{nan_policy, n_zeroed_pairs, zeroed_pairs, n_var, ceiling_frac, ceiling_n}``
      — counts, unordered variant-pair INDICES, and policy labels; no genotypes and
      no full LD matrix.

DEFERRED BOUNDARY (§5, loop-gated): PSD regularization (``psd_regularize_eigclip``
lambda_floor=1e-6 primary; ``psd_regularize_ridge`` lambda in {0.001, 0.01, 0.1}
robustness companion — the shared ``src/R/regularization/psd_utils.R``) is applied to
the fine-mapping REGION SUBMATRIX at fit time, NOT to the full per-region panel
matrix here (a full-panel eigen-decomposition at n_var ~ 1e5 is infeasible and
analytically unnecessary). ``psd_method`` / ``psd_lambda`` are therefore NOT set by
this stage — they are populated in the fit-time provenance (§5).

Memory discipline (T-m3-06-04, reusing the m3-02e-T4 dense-verify OOM class): NaN
detection, fully-NaN-row classification, and pair location are block-wise (transient
bounded by ``block * n_var``, NO full ``n_var**2`` temporary); zeroing mutates in
place at the located coordinates (O(n_zeroed) writes, no 40 GiB copy).

smoke_dev py3.11, numpy only. No Hail, no perimeter access.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

import numpy as np

# Reuse the FROZEN block-wise NaN discipline from plink_ld_to_npz (read_square_bin /
# content_verify_npz are NOT modified — only the helper _has_any_nan_blocked is reused).
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))
import plink_ld_to_npz as pln  # noqa: E402

_SUPPORTED_POLICIES = ("off_diagonal_zero",)


# --------------------------------------------------------------------------- #
# Block-wise topology helpers (memory-bounded; mirror plink_ld_to_npz)         #
# --------------------------------------------------------------------------- #

def _fully_nan_rows_blocked(m: np.ndarray, block: int = 1024) -> List[int]:
    """Indices of rows whose off-diagonal entries are ALL NaN.

    A zero-variance / monomorphic source variant NaNs its whole row/column; plink may
    keep the diagonal at 1.0, so the robust predicate is ``nan_count_in_row >=
    n_var - 1`` (catches both the diagonal-1.0 and the diagonal-NaN fingerprints).
    Memory-lean: one ``block``-row bool slice at a time (no full n_var**2 temporary),
    mirroring ``plink_ld_to_npz.nan_variant_indices``."""
    n = m.shape[0]
    thresh = n - 1
    out: List[int] = []
    for i in range(0, n, block):
        counts = np.isnan(m[i:i + block, :]).sum(axis=1)
        for off in np.nonzero(counts >= thresh)[0]:
            out.append(i + int(off))
    return out


def _nan_offdiag_pairs_blocked(m: np.ndarray, block: int = 1024) -> List[Tuple[int, int]]:
    """Sorted list of unordered ``(i, j)`` (``i < j``) off-diagonal NaN pairs.

    Every off-diagonal NaN — in EITHER triangle — is recorded as the unordered pair
    ``(min, max)`` and de-duplicated, so a symmetric ``(i,j)+(j,i)`` plink NaN is
    counted ONCE and a lone lower-triangle NaN is still paired. Diagonal NaNs are
    skipped (the fully-NaN-row branch upstream owns the zero-variance case). Memory-
    lean: one ``block``-row bool slice at a time; ``seen`` holds only located pairs
    (O(n_zeroed), ceiling-bounded in practice) — no full n_var**2 temporary."""
    n = m.shape[0]
    seen = set()
    for i in range(0, n, block):
        blk = np.isnan(m[i:i + block, :])          # (b, n) bool, bounded transient
        rows, cols = np.nonzero(blk)
        for r_off, c in zip(rows.tolist(), cols.tolist()):
            r = i + r_off
            if r == c:
                continue                            # diagonal handled upstream
            a, b = (r, c) if r < c else (c, r)
            seen.add((a, b))
    return sorted(seen)


# --------------------------------------------------------------------------- #
# Public API                                                                  #
# --------------------------------------------------------------------------- #

def condition_ld_matrix(
    m: np.ndarray,
    *,
    nan_policy: str = "off_diagonal_zero",
    ceiling_frac: float = 0.0005,
    block: int = 1024,
) -> Tuple[np.ndarray, dict]:
    """Apply the pre-registered off-diagonal ``NaN -> 0`` conditioning to ``m``.

    Parameters
    ----------
    m : (n_var, n_var) float ndarray
        A raw region LD matrix (mutated IN PLACE for the zeroed coordinates).
    nan_policy : str
        Only ``"off_diagonal_zero"`` is pre-registered / supported.
    ceiling_frac : float
        Per-region zeroing ceiling as a fraction of ``n_var`` (default 0.0005).
    block : int
        Block-row size for the memory-bounded scans (semantic no-op; result is
        block-size-invariant).

    Returns
    -------
    (conditioned_matrix, provenance_record)
        ``provenance_record`` = ``{nan_policy, n_zeroed_pairs, zeroed_pairs, n_var,
        ceiling_frac, ceiling_n}``.

    Raises
    ------
    ValueError
        - unsupported ``nan_policy`` or non-square ``m``;
        - a fully-NaN variant row exists (directs an upstream MAF/missingness drop);
        - ``n_zeroed_pairs`` exceeds the ceiling (``BRANCH_AFR_COND_DEFERRED``).
    """
    if nan_policy not in _SUPPORTED_POLICIES:
        raise ValueError(
            f"unsupported nan_policy={nan_policy!r}; only {_SUPPORTED_POLICIES[0]!r} "
            f"is pre-registered (osf-amendment-afr-native-ld-nan-psd-2026-07-03.md)."
        )
    if m.ndim != 2 or m.shape[0] != m.shape[1]:
        raise ValueError(
            f"condition_ld_matrix expects a square (n_var, n_var) LD matrix; got shape {m.shape}."
        )

    n_var = int(m.shape[0])
    ceiling_n = ceiling_frac * n_var

    def _record(n_zeroed_pairs: int, zeroed_pairs: List[Tuple[int, int]]) -> dict:
        return {
            "nan_policy": nan_policy,
            "n_zeroed_pairs": n_zeroed_pairs,
            "zeroed_pairs": zeroed_pairs,
            "n_var": n_var,
            "ceiling_frac": ceiling_frac,
            "ceiling_n": ceiling_n,
        }

    # Fast clean short-circuit (block-wise; reuses the FROZEN plink helper).
    if not pln._has_any_nan_blocked(m, block=block):
        return m, _record(0, [])

    # (1) Topology branch: fully-NaN row(s) -> RAISE (drop upstream, NOT zero-condition).
    full_rows = _fully_nan_rows_blocked(m, block=block)
    if full_rows:
        preview = ", ".join(str(i) for i in full_rows[:10]) + ("..." if len(full_rows) > 10 else "")
        raise ValueError(
            f"condition_ld_matrix: variant row(s) [{preview}] are FULLY NaN "
            f"(off-diagonal NaN count >= n_var-1) — a zero-variance / monomorphic "
            f"source on the analysis sample set. DROP these variants by MAF / "
            f"missingness QC upstream (before the raw LD panel); do NOT zero-condition "
            f"a zero-variance source."
        )

    # (2) Locate all off-diagonal NaN i<j pairs (block-wise, bounded).
    pairs = _nan_offdiag_pairs_blocked(m, block=block)
    n_zeroed = len(pairs)

    # (3) No off-diagonal pairs (only e.g. diagonal noise; defensive) -> clean no-op.
    if n_zeroed == 0:
        return m, _record(0, [])

    # (4) Over-ceiling -> RAISE, NO mutation (substrate anomaly, defer + disclose).
    if n_zeroed > ceiling_n:
        raise ValueError(
            f"condition_ld_matrix: n_zeroed_pairs={n_zeroed} exceeds the pre-registered "
            f"ceiling ceiling_n={ceiling_n:g} (= {ceiling_frac:g} x n_var={n_var}) -> "
            f"BRANCH_AFR_COND_DEFERRED. A large NaN fraction indicates an LD-construction "
            f"problem, not a conditioning case: defer this region, re-diagnose, and "
            f"disclose as a deviation. The matrix was NOT mutated."
        )

    # (5) Zero the located pairs in place (O(n_zeroed) writes, no full-size copy).
    for (i, j) in pairs:
        m[i, j] = 0.0
        m[j, i] = 0.0

    return m, _record(n_zeroed, pairs)
