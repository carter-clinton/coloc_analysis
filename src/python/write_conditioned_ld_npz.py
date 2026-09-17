"""Bank a NaN-conditioned LD matrix as a separate provenance-stamped ``.npz``
(m3-06-W6-T3, ROADMAP 999.1 §4).

==== WITHDRAWN POLICY NOTICE (tcujq -> trsx5) -- READ BEFORE ANYTHING BELOW ====

The conditioning this module banks -- the isolated-pair off-diagonal ``NaN -> 0``
zeroing and the per-region zeroing ceiling, run by ``condition_ld_matrix`` -- WAS
pre-registered: OSF file tcujq on az52u, posted 2026-07-04T04:14:46Z. It was then
WITHDRAWN by the amendment-update OSF file trsx5 on az52u, posted
2026-07-10T13:32:22Z. The posted trsx5 body, under "What is withdrawn:", reads:

    The off-diagonal NaN→0 conditioning of isolated pairwise-undefined entries
    (prior amendment tcujq item (a) isolated-off-diagonal-pair branch and item
    (b) the per-region zeroing ceiling), together with its
    BRANCH_AFR_COND_CLEAN / BRANCH_AFR_COND_APPLIED / BRANCH_AFR_COND_DEFERRED
    outcome branches, is withdrawn.

The replacement pre-registered by trsx5 is overlapping-deletion occlusion
exclude-in-lockstep (LD panel AND harmonized summary statistics) with a mandatory
provenance manifest; NaN→0 is prohibited.

STATUS: this module (m3-06, HELD) is retained as a historical record and is NOT
called by the pipeline. Its code, its error strings and its on-disk provenance
keys (``nan_policy``, ``n_zeroed``, ``zeroed_pairs``, ``ceiling_frac``) are
deliberately left unchanged -- read them, and the "pre-registered" wording below,
in light of this withdrawal. The text below this notice is the original 2026-07
wording, kept as written. Recorded:
DEC-2026-09-16-condition-ld-matrix-freeze-code-only (quick-260916-oyq).

==== END WITHDRAWN POLICY NOTICE ====

``write_conditioned_npz`` runs ``condition_ld_matrix`` (the pre-registered
off-diagonal ``NaN -> 0`` policy) then ``np.savez_compressed`` the conditioned matrix
to a SEPARATE ``{region}.conditioned.npz`` — NEVER the raw ``{region}.npz``. The
conditioned artifact carries:

  base keys  : ld, variant_ids, rsids, allele_freq, lower_triangular
               (the exact set ``src/scripts/ld_npz_to_rds.R`` already ingests);
  provenance : n_zeroed, zeroed_pairs, nan_policy, psd_method, psd_lambda,
               ceiling_frac.

Provenance-name unification (fold-in): the on-disk key ``n_zeroed`` IS the in-memory
conditioning record's ``n_zeroed_pairs`` — the same quantity under one name across
the ``.npz`` and the record. ``zeroed_pairs`` is the ``(n_zeroed, 2)`` int array of
the unordered ``i < j`` NaN pairs. ``ceiling_frac`` records the pre-registered 0.0005
ceiling for reproducibility (a fixed pre-registration constant, NOT a
fine-mapping-tunable).

DEFERRED BOUNDARY (§5, loop-gated): ``psd_method`` / ``psd_lambda`` are PLACEHOLDER
sentinels here (``"PENDING_FIT_TIME"`` / ``NaN``). PSD regularization
(``psd_regularize_eigclip`` lambda_floor=1e-6 primary; ``psd_regularize_ridge``
lambda in {0.001, 0.01, 0.1} companion — the shared
``src/R/regularization/psd_utils.R``) is applied to the fine-mapping REGION SUBMATRIX
at fit time (§5), which fills the FIT-time provenance. The raw-panel ``.npz`` +
``plink_ld_to_npz.read_square_bin`` + ``content_verify_npz`` + ``ld_npz_to_rds.R``
stay FROZEN; the conditioned ``.rds`` materialization is also §5. This module is
Python-only (``.npz``) for a clean, NCSU-confirmable verify — no R round-trip, no
perimeter access.

Raw-clobber guard (T-m3-06-05): the output path MUST end in ``.conditioned.npz`` and
MUST NOT be the raw ``{region_id}.npz`` path, so the FROZEN raw contract cannot be
overwritten.

smoke_dev py3.11, numpy only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))
import condition_ld_matrix as clm  # noqa: E402

_CONDITIONED_SUFFIX = ".conditioned.npz"
_PSD_METHOD_PENDING = "PENDING_FIT_TIME"   # filled at fit time (§5, deferred/loop-gated)


def write_conditioned_npz(
    *,
    m: np.ndarray,
    variant_ids,
    rsids,
    allele_freq,
    lower_triangular: bool,
    out_npz: str,
    region_id: str,
    nan_policy: str = "off_diagonal_zero",
    ceiling_frac: float = 0.0005,
) -> str:
    """Condition ``m`` then bank it as ``out_npz`` (a ``*.conditioned.npz``).

    Returns the written path. Propagates the ``ValueError`` from
    ``condition_ld_matrix`` (fully-NaN row / over-ceiling) WITHOUT writing a file.
    """
    out_path = Path(out_npz)
    # Raw-clobber guard (before conditioning / any write): refuse anything that is
    # not a *.conditioned.npz, and refuse the raw {region_id}.npz path explicitly.
    if not out_path.name.endswith(_CONDITIONED_SUFFIX):
        raise ValueError(
            f"write_conditioned_npz: out_npz must end in {_CONDITIONED_SUFFIX!r} to keep "
            f"the FROZEN raw {{region}}.npz contract un-clobberable; got {out_path.name!r}."
        )
    if out_path.name == f"{region_id}.npz":
        raise ValueError(
            f"write_conditioned_npz: out_npz equals the raw region path "
            f"{region_id}.npz — refusing to overwrite the frozen raw artifact."
        )

    # Apply the pre-registered conditioning (RAISES propagate here -> no file written).
    # (Policy WITHDRAWN by trsx5, OSF 2026-07-10; see the module docstring notice.)
    conditioned, record = clm.condition_ld_matrix(
        m, nan_policy=nan_policy, ceiling_frac=ceiling_frac,
    )

    # zeroed_pairs -> (n_zeroed, 2) int array (empty -> (0, 2)).
    pairs_arr = np.array(record["zeroed_pairs"], dtype=np.int64).reshape(-1, 2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        str(out_path),
        # --- base keys (ld_npz_to_rds.R ingest set) ---
        ld=conditioned,
        variant_ids=np.asarray(variant_ids),
        rsids=np.asarray(rsids),
        allele_freq=np.asarray(allele_freq),
        lower_triangular=np.array([bool(lower_triangular)]),  # triangle-flag contract, preserved
        # --- provenance keys ---
        n_zeroed=np.int64(record["n_zeroed_pairs"]),          # == record n_zeroed_pairs (unified name)
        zeroed_pairs=pairs_arr,
        nan_policy=np.asarray(record["nan_policy"]),
        ceiling_frac=np.float64(record["ceiling_frac"]),
        # --- fit-time PLACEHOLDERS (§5, deferred) ---
        psd_method=np.asarray(_PSD_METHOD_PENDING),
        psd_lambda=np.float32("nan"),
    )
    return str(out_path)
