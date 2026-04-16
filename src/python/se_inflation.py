"""
Matched-N SE inflation per D-01a:
    SE_EUR_matched = SE_EUR * sqrt(N_EUR / N_AFR_trait)
Independent-Z resampling per D-01b:
    Z_b ~ N(beta_hat / SE_matched, 1) per variant, independently within a region.
LD matrix R is held fixed (used only in downstream SuSiE refit, not here).

Per RESEARCH B-1 CONFIRMED: analytic consequence of Z/beta/SE scaling under fixed
per-variant effect size. Downstream SuSiE refit uses full R.
"""
import numpy as np


def inflate_se(se_eur: np.ndarray, n_eur: float, n_afr: float) -> np.ndarray:
    """Inflate EUR standard errors to simulate matched-N (AFR sample size).

    SE_EUR_matched = SE_EUR * sqrt(n_eur / n_afr)

    Parameters
    ----------
    se_eur : np.ndarray
        Per-variant standard errors from EUR GWAS at full sample size.
    n_eur : float
        EUR effective sample size (full).
    n_afr : float
        AFR effective sample size (target matched-N).

    Returns
    -------
    np.ndarray
        Inflated SE at matched-N scale.

    Raises
    ------
    ValueError
        If n_eur or n_afr is non-positive, or n_afr > n_eur.
    """
    if n_afr <= 0 or n_eur <= 0:
        raise ValueError(f"N_EUR={n_eur}, N_AFR={n_afr}; both must be positive")
    if n_afr > n_eur:
        raise ValueError(f"Matched-N requires N_AFR ({n_afr}) <= N_EUR ({n_eur})")
    factor = np.sqrt(n_eur / n_afr)
    return se_eur * factor


def draw_z_bootstrap(
    beta_hat: np.ndarray,
    se_matched: np.ndarray,
    seed: int,
    rng_backend: str = "default_rng",
) -> np.ndarray:
    """Draw independent bootstrap Z-scores under matched-N SE.

    Z_b ~ N(beta_hat / SE_matched, 1) per variant, independently.

    Parameters
    ----------
    beta_hat : np.ndarray
        EUR effect estimates (original scale).
    se_matched : np.ndarray
        Inflated SE from inflate_se().
    seed : int
        Deterministic seed for reproducibility.
    rng_backend : str
        RNG backend (only 'default_rng' supported).

    Returns
    -------
    np.ndarray
        Bootstrap Z-scores (same shape as beta_hat).
    """
    rng = np.random.default_rng(seed)
    mean = beta_hat / se_matched
    z = rng.normal(loc=mean, scale=1.0, size=beta_hat.shape)
    return z


def reconstruct_pseudo_sumstats(
    z_bootstrap: np.ndarray, se_matched: np.ndarray
) -> tuple:
    """Reconstruct pseudo-sumstats from bootstrap Z-scores.

    beta_b = Z_b * SE_matched
    se_b = SE_matched  (held at matched scale per D-01b)

    Parameters
    ----------
    z_bootstrap : np.ndarray
        Bootstrap Z-scores from draw_z_bootstrap().
    se_matched : np.ndarray
        Inflated SE from inflate_se().

    Returns
    -------
    (beta_b, se_b) : tuple of np.ndarray
        Pseudo effect estimates and SE at matched-N scale.
    """
    beta_b = z_bootstrap * se_matched
    se_b = se_matched  # SE held at matched scale per D-01b
    return beta_b, se_b


def compute_seed(trait_id: int, bootstrap_idx: int, seed_base: int = 1000) -> int:
    """Compute deterministic seed for a given trait and bootstrap index.

    seed = seed_base * trait_id + bootstrap_idx

    Parameters
    ----------
    trait_id : int
        Zero-indexed trait identifier (0..4 for 5 T1 traits).
    bootstrap_idx : int
        Bootstrap index (1..bootstrap_n).
    seed_base : int
        Base multiplier (default 1000 per config/matched_n.yaml).

    Returns
    -------
    int
        Deterministic seed value.
    """
    return seed_base * trait_id + bootstrap_idx
