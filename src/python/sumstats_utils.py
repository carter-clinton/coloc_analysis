#!/usr/bin/env python3
"""Shared utility module for cross-method sumstats operations.

Used by MAGMA, LDSC, and HESS wrappers to avoid reimplementing
effective-N logic in each individual script. Import as:

    from sumstats_utils import compute_effective_n, get_effective_n, TRAIT_TYPE
"""


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
