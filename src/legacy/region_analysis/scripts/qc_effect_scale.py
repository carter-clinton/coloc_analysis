#!/usr/bin/env python3
import argparse
import csv
import math
import os
import random
import subprocess
import shutil
import sys
from pathlib import Path

import numpy as np


def norm_ppf(p: float) -> float:
    # Acklam's inverse normal approximation.
    if p <= 0.0:
        return -math.inf
    if p >= 1.0:
        return math.inf
    a = [
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    ]
    b = [
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    ]
    c = [
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    ]
    d = [
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e00,
        3.754408661907416e00,
    ]
    plow = 0.02425
    phigh = 1 - plow
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
        )
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
        )
    q = p - 0.5
    r = q * q
    return (
        (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
        / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    )


def norm_isf(p: float) -> float:
    return norm_ppf(1 - p)


def parse_args():
    parser = argparse.ArgumentParser(description="QC effect size scale across harmonized GWAS files.")
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--out_report", required=True)
    parser.add_argument("--out_actions", required=True)
    parser.add_argument("--sample", type=int, default=200000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--apply", action="store_true", help="Write corrected files.")
    parser.add_argument("--fixed-dir", default="data_processed/sumstats_harmonized_fixed")
    return parser.parse_args()


def parse_trait_ancestry(path: str):
    name = Path(path).name
    tokens = name.split(".")
    if len(tokens) < 2:
        return "", ""
    return tokens[0], tokens[1]


def safe_float(value):
    try:
        if value is None:
            return None
        if isinstance(value, str) and value.strip() in {"", "NA", "NaN", "nan"}:
            return None
        return float(value)
    except ValueError:
        return None


def sample_rows(path: str, sample_size: int, seed: int):
    rng = random.Random(seed)
    sample = []
    with subprocess.Popen(["gunzip", "-c", path], stdout=subprocess.PIPE, text=True) as proc:
        reader = csv.reader(proc.stdout, delimiter="\t")
        header = next(reader, None)
        if header is None:
            return header, sample
        for idx, row in enumerate(reader, start=1):
            if not row:
                continue
            if len(sample) < sample_size:
                sample.append(row)
            else:
                j = rng.randint(1, idx)
                if j <= sample_size:
                    sample[j - 1] = row
    return header, sample


def compute_p_score(betas, ses, ps):
    mask = np.isfinite(betas) & np.isfinite(ses) & (ses > 0) & np.isfinite(ps)
    if mask.sum() < 10:
        return math.nan
    betas = betas[mask]
    ses = ses[mask]
    ps = np.clip(ps[mask], 1e-300, 1.0)
    z = np.abs(betas / ses)
    pred = np.array([math.erfc(val / math.sqrt(2)) for val in z], dtype=float)
    pred = np.clip(pred, 1e-300, 1.0)
    diff = np.abs(np.log10(ps) - np.log10(pred))
    return float(np.nanmedian(diff))


def compute_p_mismatch(betas, ses, ps, tol_log10=1.0):
    mask = np.isfinite(betas) & np.isfinite(ses) & (ses > 0) & np.isfinite(ps)
    if mask.sum() < 10:
        return math.nan
    betas = betas[mask]
    ses = ses[mask]
    ps = np.clip(ps[mask], 1e-300, 1.0)
    z = np.abs(betas / ses)
    pred = np.array([math.erfc(val / math.sqrt(2)) for val in z], dtype=float)
    pred = np.clip(pred, 1e-300, 1.0)
    diff = np.abs(np.log10(ps) - np.log10(pred))
    return float(np.mean(diff > tol_log10) * 100.0)


def assess_scale(header, rows):
    col_map = {name: idx for idx, name in enumerate(header)}
    beta_idx = col_map.get("BETA")
    se_idx = col_map.get("SE")
    p_idx = col_map.get("P")
    if beta_idx is None or p_idx is None:
        return None
    betas = []
    ses = []
    ps = []
    for row in rows:
        if beta_idx >= len(row) or p_idx >= len(row):
            continue
        beta = safe_float(row[beta_idx])
        pval = safe_float(row[p_idx])
        if beta is None or pval is None:
            continue
        betas.append(beta)
        ps.append(pval)
        se_val = None
        if se_idx is not None and se_idx < len(row):
            se_val = safe_float(row[se_idx])
        ses.append(se_val)

    betas = np.array(betas, dtype=float)
    ps = np.array(ps, dtype=float)
    ses = np.array([np.nan if v is None else v for v in ses], dtype=float)

    if betas.size == 0:
        return None

    beta_neg_frac = float(np.mean(betas < 0))
    q10, q50, q90 = np.quantile(betas, [0.1, 0.5, 0.9])
    se_valid_frac = float(np.mean(np.isfinite(ses) & (ses > 0)))
    p_score_raw = compute_p_score(betas, ses, ps)
    log_betas = np.where(betas > 0, np.log(betas), np.nan)
    p_score_log = compute_p_score(log_betas, ses, ps)
    p_mismatch_raw = compute_p_mismatch(betas, ses, ps)
    p_mismatch_log = compute_p_mismatch(log_betas, ses, ps)

    convert = False
    if (not math.isnan(p_score_log)) and (not math.isnan(p_score_raw)) and beta_neg_frac < 0.02 and q10 > 0 and p_score_log + 0.1 < p_score_raw:
        convert = True
    elif (not math.isnan(p_score_log)) and (not math.isnan(p_score_raw)) and beta_neg_frac < 0.05 and q50 > 0.5 and p_score_log + 0.2 < p_score_raw:
        convert = True

    derive_se = se_valid_frac < 0.5

    if convert and derive_se:
        action = "convert_or_to_logor+derive_se"
    elif convert:
        action = "convert_or_to_logor"
    elif derive_se:
        action = "derive_se"
    else:
        action = "keep"

    return {
        "beta_neg_frac": beta_neg_frac,
        "beta_q10": q10,
        "beta_q50": q50,
        "beta_q90": q90,
        "p_score_raw": p_score_raw,
        "p_score_log": p_score_log,
        "P_mismatch_raw_pct": p_mismatch_raw,
        "P_mismatch_log_pct": p_mismatch_log,
        "se_valid_frac": se_valid_frac,
        "action": action,
        "convert_or": convert,
        "derive_se": derive_se,
        "n_sample": betas.size,
    }


def apply_fix(path, action, out_dir):
    trait, ancestry = parse_trait_ancestry(path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{trait}.{ancestry}.tsv.bgz"
    tmp_plain = out_path.with_suffix(".tsv")

    with subprocess.Popen(["gunzip", "-c", path], stdout=subprocess.PIPE, text=True) as proc:
        reader = csv.reader(proc.stdout, delimiter="\t")
        header = next(reader, None)
        if header is None:
            return None
        col_map = {name: idx for idx, name in enumerate(header)}
        beta_idx = col_map.get("BETA")
        se_idx = col_map.get("SE")
        p_idx = col_map.get("P")
        if beta_idx is None or p_idx is None:
            raise RuntimeError(f"Missing BETA/P in {path}")

        if se_idx is None and action["derive_se"]:
            header.append("SE")
            se_idx = len(header) - 1

        with open(tmp_plain, "w", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t")
            writer.writerow(header)
            for row in reader:
                if not row:
                    continue
                if len(row) < len(header):
                    row += [""] * (len(header) - len(row))
                beta = safe_float(row[beta_idx])
                pval = safe_float(row[p_idx])
                se_val = safe_float(row[se_idx]) if se_idx is not None and se_idx < len(row) else None

                if action["convert_or"] and beta is not None:
                    if beta > 0:
                        beta = math.log(beta)
                    else:
                        beta = None

                if action["derive_se"]:
                    if se_val is None or not math.isfinite(se_val) or se_val <= 0:
                        if beta is not None and pval is not None and pval > 0:
                            z_abs = norm_isf(pval / 2)
                            if z_abs > 0:
                                sign = 1.0 if beta >= 0 else -1.0
                                se_val = beta / (sign * z_abs)
                if beta is not None:
                    row[beta_idx] = f"{beta:.6g}"
                if se_idx is not None and se_val is not None:
                    row[se_idx] = f"{se_val:.6g}"
                writer.writerow(row)

    subprocess.run(["bgzip", "-f", str(tmp_plain)], check=True)
    tmp_bgz = tmp_plain.with_suffix(".tsv.gz")
    tmp_bgz.rename(out_path)
    if shutil.which("tabix"):
        subprocess.run(["tabix", "-f", "-S", "1", "-s", "1", "-b", "2", "-e", "2", str(out_path)], check=False)
    return out_path


def main():
    args = parse_args()
    random.seed(args.seed)
    report_rows = []
    action_rows = []
    for path in args.inputs:
        header, rows = sample_rows(path, args.sample, args.seed)
        if header is None:
            continue
        stats = assess_scale(header, rows)
        if stats is None:
            continue
        trait, ancestry = parse_trait_ancestry(path)
        report_rows.append({
            "path": path,
            "trait": trait,
            "ancestry": ancestry,
            "n_sample": stats["n_sample"],
            "beta_neg_frac": stats["beta_neg_frac"],
            "beta_q10": stats["beta_q10"],
            "beta_q50": stats["beta_q50"],
            "beta_q90": stats["beta_q90"],
            "p_score_raw": stats["p_score_raw"],
            "p_score_log": stats["p_score_log"],
            "P_mismatch_raw_pct": stats["P_mismatch_raw_pct"],
            "P_mismatch_log_pct": stats["P_mismatch_log_pct"],
            "se_valid_frac": stats["se_valid_frac"],
        })
        action_rows.append({
            "path": path,
            "trait": trait,
            "ancestry": ancestry,
            "action": stats["action"],
            "convert_or": stats["convert_or"],
            "derive_se": stats["derive_se"],
        })

    if not report_rows:
        raise SystemExit("No report rows generated; check inputs.")
    Path(args.out_report).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_report, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(report_rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(report_rows)

    Path(args.out_actions).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_actions, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(action_rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(action_rows)

    if args.apply:
        for row in action_rows:
            trait, ancestry = row["trait"], row["ancestry"]
            action = {
                "convert_or": row["convert_or"] in {"True", True},
                "derive_se": row["derive_se"] in {"True", True},
            }
            apply_fix(row["path"], action, args.fixed_dir)


if __name__ == "__main__":
    main()
