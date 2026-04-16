#!/usr/bin/env python3
"""Per-bootstrap Z resampling + SuSiE refit invocation for matched-N analysis.

Implements D-01b: for each bootstrap b, draw Z_b ~ N(beta_hat/SE_matched, 1)
per variant independently, write pseudo-sumstats, and refit SuSiE via the
Phase 1 run_susie_rss.R script (reused verbatim).

Usage:
    python bootstrap_driver.py \\
        --trait t2d --trait-id 0 --region chr10_114p \\
        --bootstrap-idx 1 \\
        --eur-sumstats data/processed/region_analysis/sumstats_harmonized_fixed/t2d_EUR.bgz \\
        --afr-n 55525 \\
        --ld-matrix-rds results/ld_reference/ukbb_eur/chr10_114p.rds \\
        --output-fit-rds /rs1/researchers/c/ckclinto/matched_n_fits/t2d/chr10_114p/bootstrap_1/eur_matched.fit.rds
"""
import argparse
import gzip
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# Project convention: sys.path.insert for flat-name imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "python"))
from se_inflation import compute_seed, draw_z_bootstrap, inflate_se, reconstruct_pseudo_sumstats


def parse_args(argv=None):
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(
        description="Per-bootstrap Z resampling + SuSiE refit for matched-N analysis"
    )
    p.add_argument("--trait", required=True, help="Trait name (e.g., t2d)")
    p.add_argument("--trait-id", type=int, required=True,
                   help="Zero-indexed trait identifier (0..4)")
    p.add_argument("--region", required=True, help="Region ID (e.g., chr10_114p)")
    p.add_argument("--bootstrap-idx", type=int, required=True,
                   help="Bootstrap index (1..bootstrap_n)")
    p.add_argument("--eur-sumstats", required=True,
                   help="Path to EUR sumstats (tsv.gz/bgz)")
    p.add_argument("--afr-n", type=float, required=True,
                   help="AFR effective sample size (target matched-N)")
    p.add_argument("--ld-matrix-rds", required=True,
                   help="Path to LD matrix .rds for the region")
    p.add_argument("--output-fit-rds", required=True,
                   help="Output path for the bootstrap .fit.rds")
    p.add_argument("--seed-base", type=int, default=1000,
                   help="Seed base multiplier (default: 1000 per config)")
    p.add_argument("--susie-policy", default="config/susie_policy.yaml",
                   help="Path to SuSiE policy YAML (reused verbatim from Phase 1)")
    p.add_argument("--susie-script",
                   default="src/legacy/region_analysis/scripts/run_susie_rss.R",
                   help="Path to Phase 1 run_susie_rss.R (reused verbatim)")
    return p.parse_args(argv)


def load_eur_sumstats(path: str) -> pd.DataFrame:
    """Load EUR sumstats for a region from tsv.gz/bgz file.

    Expected columns: variant_id (or SNP), chrom (or CHR), pos (or BP),
    beta (or BETA), se (or SE), N (optional).
    """
    # Handle both .bgz and .tsv.gz
    open_fn = gzip.open if path.endswith((".gz", ".bgz")) else open
    df = pd.read_csv(path, sep="\t", compression="gzip" if path.endswith((".gz", ".bgz")) else None)

    # Normalize column names to lowercase
    col_map = {}
    for col in df.columns:
        cl = col.lower()
        if cl in ("snp", "variant_id", "rsid"):
            col_map[col] = "variant_id"
        elif cl in ("chr", "chrom", "chromosome"):
            col_map[col] = "chrom"
        elif cl in ("bp", "pos", "position"):
            col_map[col] = "pos"
        elif cl in ("beta", "effect"):
            col_map[col] = "beta"
        elif cl in ("se", "stderr"):
            col_map[col] = "se"
        elif cl == "n":
            col_map[col] = "N"
    df = df.rename(columns=col_map)

    required = {"variant_id", "beta", "se"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in EUR sumstats: {missing}")

    return df


def get_eur_n(sumstats_df: pd.DataFrame, trait: str) -> float:
    """Extract EUR effective N from sumstats or trait_sample_sizes config.

    Falls back to median N column if present, otherwise reads from
    config/trait_sample_sizes.yaml.
    """
    if "N" in sumstats_df.columns:
        n_val = sumstats_df["N"].median()
        if np.isfinite(n_val) and n_val > 0:
            return float(n_val)

    # Fallback: config-driven
    sizes_path = Path("config/trait_sample_sizes.yaml")
    if sizes_path.exists():
        with open(sizes_path) as fh:
            sizes = yaml.safe_load(fh)
        if trait in sizes and "EUR" in sizes[trait]:
            return float(sizes[trait]["EUR"])

    raise ValueError(
        f"Cannot determine EUR N for {trait}: no N column in sumstats "
        f"and no config/trait_sample_sizes.yaml entry"
    )


def run_bootstrap(args):
    """Execute one bootstrap iteration: Z resample + SuSiE refit."""
    # 1. Load EUR sumstats
    df = load_eur_sumstats(args.eur_sumstats)

    # 2. Get EUR effective N
    n_eur = get_eur_n(df, args.trait)
    n_afr = args.afr_n

    # 3. SE inflation per D-01a
    se_eur = df["se"].values.astype(np.float64)
    beta_hat = df["beta"].values.astype(np.float64)
    se_matched = inflate_se(se_eur, n_eur, n_afr)

    # 4. Compute deterministic seed per D-01b
    seed = compute_seed(args.trait_id, args.bootstrap_idx, args.seed_base)

    # 5. Draw bootstrap Z-scores
    z_b = draw_z_bootstrap(beta_hat, se_matched, seed)

    # 6. Reconstruct pseudo-sumstats
    beta_b, se_b = reconstruct_pseudo_sumstats(z_b, se_matched)

    # 7. Write pseudo-sumstats to temp file
    output_dir = Path(args.output_fit_rds).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_pseudo.tsv", dir=tempfile.gettempdir(),
        delete=False, prefix=f"bootstrap_{args.bootstrap_idx}_"
    ) as tmp:
        tmp_path = tmp.name
        # Write header
        tmp.write("variant_id\tchrom\tpos\tbeta\tse\tN\n")
        for i in range(len(df)):
            vid = df["variant_id"].iloc[i]
            chrom = df["chrom"].iloc[i] if "chrom" in df.columns else "NA"
            pos = df["pos"].iloc[i] if "pos" in df.columns else "NA"
            tmp.write(f"{vid}\t{chrom}\t{pos}\t{beta_b[i]:.8g}\t{se_b[i]:.8g}\t{n_afr}\n")

    # 8. Invoke Phase 1 run_susie_rss.R (verbatim reuse)
    cmd = [
        "Rscript", args.susie_script,
        "--sumstats", tmp_path,
        "--ld-rds", args.ld_matrix_rds,
        "--policy", args.susie_policy,
        "--output", args.output_fit_rds,
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
        print(f"OK bootstrap {args.bootstrap_idx}")
        if result.stdout:
            print(result.stdout, end="")
    except subprocess.CalledProcessError as e:
        # SuSiE failure: write minimal failure .rds matching Phase 1
        # retry-ladder policy. Use R to create a compatible failure object.
        print(
            f"WARN bootstrap {args.bootstrap_idx} SuSiE failed: {e.stderr}",
            file=sys.stderr,
        )
        _write_failure_rds(args.output_fit_rds, args.bootstrap_idx, str(e.stderr))
    finally:
        # 9. Cull tmp pseudo-sumstats after fit (retention policy per CONTEXT)
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _write_failure_rds(output_path: str, bootstrap_idx: int, error_msg: str):
    """Write a minimal failure .rds so downstream rules can detect and skip.

    Uses R via subprocess to create an RDS-compatible failure object,
    matching the Phase 1 / Phase 9 failure-path convention.
    """
    r_code = f"""
    failure <- list(
        status = "susie_failure",
        bootstrap_idx = {bootstrap_idx}L,
        error = "{error_msg[:200]}",
        converged = FALSE,
        sets = list(cs = list())
    )
    class(failure) <- c("susie_failure", "list")
    dir.create(dirname("{output_path}"), recursive = TRUE, showWarnings = FALSE)
    saveRDS(failure, "{output_path}")
    cat("Wrote failure RDS:", "{output_path}", "\\n")
    """
    try:
        subprocess.run(
            ["Rscript", "-e", r_code],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError:
        # Last resort: write an empty file so Snakemake doesn't re-trigger
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).touch()


def main():
    args = parse_args()
    run_bootstrap(args)


if __name__ == "__main__":
    main()
