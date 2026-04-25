#!/usr/bin/env python3
"""Reduce N-1 LDSC star-topology rg log files into:

  (1) NxN symmetric bivariate-intercept wide TSV (D-11 primary; MTAG --overlap consumer)
  (2) Long-form fat TSV with rg/rg_se/gcov_int/gcov_int_se/h2_a/h2_b (M2 CPASSOC consumer)

Plan reference: m1-03-munge-and-ldsc-intercept-matrix-PLAN.md Task 1 step (A).

RESEARCH Pitfall #1: ``ldsc.py an "rg cross" flag`` does NOT exist in the vendored
abdenlab/ldsc-python3 fork. The CANONICAL approach for full N×N coverage is
N-1 star-topology ``--rg`` calls where focal_i pairs with traits i+1..N-1
in a single comma-separated list. This module's parser is built for that
shape: it parses the ``Summary of Genetic Correlation Results`` table at
the bottom of each focal log and extracts ``gcov_int`` for matrix
assembly.

LDSC ``--rg`` log Summary table column order:
  p1, p2, rg, se, z, p, h2_obs, h2_obs_se, h2_int, h2_int_se, gcov_int, gcov_int_se

Validation heuristics (Pitfall #8 false-alarm protection):
  - within-GLGC EUR lipid pairs (LDL/HDL/TG/TC × EUR) expect intercept ~ 1.0.
  - UKB-UKB EUR pairs expect intercept > 0.5.
  - Non-overlap pairs expect intercept ~ 0.0 ± 0.05.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# D-16 trait-key regex: <trait>.<ancestry>.<consortium>.<year>.sumstats.gz
TRAIT_KEY_RE = re.compile(
    r"(?P<trait>[a-z0-9]+)\.(?P<ancestry>[A-Z]+)\."
    r"(?P<consortium>[\w-]+)\.(?P<year>\d{4})\.sumstats\.gz"
)

TABLE_HEADER_MARKER = "Summary of Genetic Correlation Results"
# Column order per LDSC --rg output:
#   p1 p2 rg se z p h2_obs h2_obs_se h2_int h2_int_se gcov_int gcov_int_se
_COLS_EXPECTED = 12

# Validation tolerances and expected ranges.
_DIAG_TOL = 0.1                         # diagonal must be within 1.0 +/- this band
_LIPID_LOWER, _LIPID_UPPER = 0.7, 1.3   # within-GLGC EUR lipid intercept band


# ---------------------------------------------------------------------------
# Parser primitives.
# ---------------------------------------------------------------------------

def _safe_float(token: str) -> float:
    """Convert an LDSC token to float; map 'NA' / '.' to NaN."""
    if token in ("NA", "N/A", "n/a", "."):
        return np.nan
    try:
        return float(token)
    except (ValueError, TypeError):
        return np.nan


def parse_rg_log(log_path: Path) -> pd.DataFrame:
    """Extract per-pair rg + h2 + gcov_int rows from one LDSC --rg log file.

    Returns a DataFrame with columns:
      [p1, p2, rg, rg_se, z, p, h2_obs, h2_obs_se, h2_int, h2_int_se,
       gcov_int, gcov_int_se]

    Empty DataFrame on logs without a Summary table.
    """
    text = log_path.read_text()
    rows: list[dict] = []
    in_table = False
    for line in text.splitlines():
        if TABLE_HEADER_MARKER in line:
            in_table = True
            continue
        if not in_table:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        # Skip the column header line and any analysis/end markers.
        if stripped.startswith(("p1", "Analysis", "Total")):
            continue
        parts = stripped.split()
        if len(parts) < _COLS_EXPECTED:
            continue
        try:
            rows.append({
                "p1": parts[0],
                "p2": parts[1],
                "rg": _safe_float(parts[2]),
                "rg_se": _safe_float(parts[3]),
                "z": _safe_float(parts[4]),
                "p": _safe_float(parts[5]),
                "h2_obs": _safe_float(parts[6]),
                "h2_obs_se": _safe_float(parts[7]),
                "h2_int": _safe_float(parts[8]),
                "h2_int_se": _safe_float(parts[9]),
                "gcov_int": _safe_float(parts[10]),
                "gcov_int_se": _safe_float(parts[11]),
            })
        except (ValueError, IndexError):
            continue
    return pd.DataFrame(rows)


def key_from_path(path_str: str) -> str:
    """Extract the D-16 trait-key (without ``.sumstats.gz``) from a path string."""
    name = Path(path_str).name
    if not name.endswith(".sumstats.gz"):
        raise ValueError(
            f"Path '{name}' does not end with '.sumstats.gz' "
            f"(D-16 munged-file convention)"
        )
    return name[: -len(".sumstats.gz")]


# ---------------------------------------------------------------------------
# Matrix assembly.
# ---------------------------------------------------------------------------

def build_intercept_matrix(log_dir: Path, trait_keys: list[str]) -> pd.DataFrame:
    """Assemble the symmetric NxN bivariate-intercept matrix.

    Diagonal defaults to 1.0 (self-pair intercept = h2 intercept reported
    separately by LDSC; D-11 convention sets the diagonal to 1.0 for
    MTAG --overlap consumption). Off-diagonals come from ``gcov_int`` of
    each pair across all focal_*.log files in ``log_dir``.

    Pairs whose endpoints don't match the trait_keys list are silently
    skipped (handles partial logs / mismatched key sets).
    """
    mat = pd.DataFrame(np.nan, index=trait_keys, columns=trait_keys, dtype=float)
    for k in trait_keys:
        mat.at[k, k] = 1.0  # diagonal convention

    for log_path in sorted(log_dir.glob("focal_*.log")):
        df = parse_rg_log(log_path)
        for _, row in df.iterrows():
            try:
                k1 = key_from_path(row["p1"])
                k2 = key_from_path(row["p2"])
            except ValueError:
                continue
            if k1 not in trait_keys or k2 not in trait_keys:
                continue
            mat.at[k1, k2] = row["gcov_int"]
            mat.at[k2, k1] = row["gcov_int"]  # symmetric assignment
    return mat


def build_long_format(log_dir: Path, trait_keys: list[str]) -> pd.DataFrame:
    """Build the long-form fat TSV (per-pair rg + gcov_int + h2_a + h2_b).

    Per-pair fields surfaced for M2 CPASSOC wrapper consumption (RESEARCH
    open-question #5). h2_a is the focal-pair h2_obs as printed in the
    log; h2_b is left NaN here (LDSC's per-pair Summary table emits only
    one h2_obs column — the focal — and the partner h2 is in the Summary
    body above the table; capturing it would require multi-section
    parsing not yet implemented).
    """
    rows: list[dict] = []
    for log_path in sorted(log_dir.glob("focal_*.log")):
        df = parse_rg_log(log_path)
        for _, r in df.iterrows():
            try:
                k1 = key_from_path(r["p1"])
                k2 = key_from_path(r["p2"])
            except ValueError:
                continue
            if k1 not in trait_keys or k2 not in trait_keys:
                continue
            rows.append({
                "trait_a": k1,
                "trait_b": k2,
                "rg": r["rg"],
                "rg_se": r["rg_se"],
                "gcov_int": r["gcov_int"],
                "gcov_int_se": r["gcov_int_se"],
                "h2_a": r["h2_obs"],
                "h2_b": np.nan,
                "p_rg": r["p"],
                "z_rg": r["z"],
                "h2_int_a": r["h2_int"],
                "h2_int_se_a": r["h2_int_se"],
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Validation.
# ---------------------------------------------------------------------------

def validate_self_consistency(mat: pd.DataFrame, tol: float = 1e-6) -> list[str]:
    """Return a list of self-consistency warnings; empty list on a clean matrix.

    Checks:
      - Symmetry: max|mat - mat.T| <= tol (NaN-safe).
      - Diagonal ~ 1.0 within DIAG_TOL band (or NaN).
    """
    warnings: list[str] = []

    if mat.size > 0:
        diff = mat.values - mat.values.T
        max_off_diag = np.nanmax(np.abs(diff))
        if not np.isnan(max_off_diag) and max_off_diag > tol:
            warnings.append(
                f"Symmetry violation: max|mat - mat.T| = {max_off_diag:.6g} (tol={tol})"
            )

    diag = np.diag(mat.values)
    bad_diag = [
        (i, float(d))
        for i, d in enumerate(diag)
        if not (np.isnan(d) or abs(d - 1.0) < _DIAG_TOL)
    ]
    if bad_diag:
        warnings.append(
            f"Diagonal values not ~1.0 ({_DIAG_TOL} tol): {bad_diag[:5]}"
        )

    return warnings


def validate_expected_intercept_heuristics(mat: pd.DataFrame) -> list[str]:
    """Pitfall #8 false-alarm protection.

    Within-GLGC EUR lipid pairs (LDL/HDL/TG/TC × EUR) cohort-overlap completely
    (same study) so the bivariate intercept is expected ~ 1.0. Deviations
    > +/- 0.3 are flagged for QC review.
    """
    warnings: list[str] = []

    eur_cols = [c for c in mat.columns if ".EUR." in c]
    lipid_traits = ("ldl", "hdl", "tg", "tc")
    glgc_eur = [
        c for c in eur_cols
        if c.startswith(tuple(f"{t}." for t in lipid_traits))
        and ".GLGC." in c
    ]
    for i, c1 in enumerate(glgc_eur):
        for c2 in glgc_eur[i + 1:]:
            v = mat.at[c1, c2]
            if not np.isnan(v) and not (_LIPID_LOWER < v < _LIPID_UPPER):
                warnings.append(
                    f"Within-GLGC EUR lipid pair ({c1}, {c2}) intercept={v:.3f}; "
                    f"expected ~1.0 (band [{_LIPID_LOWER}, {_LIPID_UPPER}])"
                )

    return warnings


# ---------------------------------------------------------------------------
# CLI driver.
# ---------------------------------------------------------------------------

def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--log-dir", type=Path, required=True,
                    help="Directory containing focal_*.log files.")
    ap.add_argument("--trait-keys-file", type=Path, required=True,
                    help="One D-16 trait key per line.")
    ap.add_argument("--output-matrix", type=Path, required=True,
                    help="NxN wide TSV (D-11 primary deliverable).")
    ap.add_argument("--output-long", type=Path, required=True,
                    help="Long-form fat TSV (per-pair rg/gcov_int/h2).")
    ap.add_argument("--output-validation", type=Path,
                    default=Path("data/processed/ldsc_overlap/rg_validation_warnings.json"),
                    help="JSON dump of validation warnings.")
    args = ap.parse_args()

    trait_keys = sorted([
        line.strip()
        for line in args.trait_keys_file.read_text().splitlines()
        if line.strip()
    ])

    mat = build_intercept_matrix(args.log_dir, trait_keys)
    long = build_long_format(args.log_dir, trait_keys)
    warn_sym = validate_self_consistency(mat)
    warn_heur = validate_expected_intercept_heuristics(mat)

    args.output_matrix.parent.mkdir(parents=True, exist_ok=True)
    mat.to_csv(args.output_matrix, sep="\t")
    long.to_csv(args.output_long, sep="\t", index=False)

    args.output_validation.parent.mkdir(parents=True, exist_ok=True)
    args.output_validation.write_text(json.dumps({
        "symmetry_warnings": warn_sym,
        "heuristic_warnings": warn_heur,
        "n_traits": len(trait_keys),
        "n_pairs_filled": int((mat.notna().sum().sum() - len(trait_keys)) / 2),
    }, indent=2))

    print(f"Wrote matrix shape {mat.shape} to {args.output_matrix}", file=sys.stderr)
    print(f"Wrote long-form ({len(long)} pairs) to {args.output_long}", file=sys.stderr)
    if warn_sym or warn_heur:
        print(
            f"VALIDATION WARNINGS: {len(warn_sym)} symmetry + {len(warn_heur)} "
            f"heuristic — see {args.output_validation}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    _main()
