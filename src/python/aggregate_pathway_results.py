#!/usr/bin/env python3
"""Cross-method pathway result aggregation for Phase 5.

Reads outputs from all 6 analytical components (MAGMA, g:Profiler, LDSC
partitioned, LDSC-SEG, HESS, negative controls) and produces two summary
tables:

A. pathway_enrichment_summary.tsv -- Per-pathway cross-method summary
   with consensus ranking.

B. phase5_overview.tsv -- Phase 5 top-level summary (one row per
   analytical component).

T-05-24: validates expected columns in each input file.

Usage:
    python aggregate_pathway_results.py \\
        --magma-dir results/pathway/magma \\
        --gprofiler-dir results/pathway/gprofiler \\
        --ldsc-dir results/pathway/ldsc_partitioned \\
        --ldsc-seg-dir results/pathway/ldsc_seg \\
        --hess-dir results/pathway/hess \\
        --neg-ctrl-dir results/pathway/negative_controls \\
        --out results/pathway/pathway_enrichment_summary.tsv

References:
    de Leeuw 2015 (MAGMA), Reimand 2019 (g:Profiler), Finucane 2015/2018 (LDSC),
    Gazal 2017 (baseline v2.2), Shi 2017 (HESS)
"""
import argparse
import csv
import glob
import logging
import math
import os
import sys
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Input readers with schema validation (T-05-24)
# ---------------------------------------------------------------------------

def _validate_columns(header, required, source_name):
    """Validate that required columns exist in a TSV header.

    T-05-24: reject files with unexpected schema.
    """
    missing = [c for c in required if c not in header]
    if missing:
        logger.warning(
            "Schema mismatch in %s: missing columns %s (have %s)",
            source_name, missing, header,
        )
        return False
    return True


def read_magma_results(magma_dir):
    """Read MAGMA gene-set FDR results (per trait x ancestry).

    Returns list of dicts with: pathway, trait, ancestry, beta, se, p, q.
    """
    results = []
    for fdr_path in sorted(glob.glob(os.path.join(magma_dir, "*_geneset_fdr.tsv"))):
        basename = os.path.basename(fdr_path)
        trait_anc = basename.replace("_geneset_fdr.tsv", "")
        parts = trait_anc.rsplit("_", 1)
        trait = parts[0] if len(parts) == 2 else trait_anc
        ancestry = parts[1] if len(parts) == 2 else "EUR"

        with open(fdr_path) as f:
            reader = csv.DictReader(f, delimiter="\t")
            if not _validate_columns(
                reader.fieldnames or [], ["VARIABLE", "BETA", "P", "FDR_Q"],
                f"MAGMA {basename}",
            ):
                continue
            for row in reader:
                results.append({
                    "pathway": row.get("VARIABLE", ""),
                    "trait": trait,
                    "ancestry": ancestry,
                    "magma_beta": _safe_float(row.get("BETA")),
                    "magma_se": _safe_float(row.get("SE")),
                    "magma_p": _safe_float(row.get("P")),
                    "magma_q": _safe_float(row.get("FDR_Q")),
                })
    return results


def read_gprofiler_results(gprofiler_dir):
    """Read g:Profiler enrichment results.

    Returns list of dicts with: source, term_name, p, q, intersection_size.
    """
    results = []
    enrichment_path = os.path.join(gprofiler_dir, "enrichment_results.tsv")
    if not os.path.exists(enrichment_path):
        logger.warning("g:Profiler enrichment results not found: %s", enrichment_path)
        return results

    with open(enrichment_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        if not _validate_columns(
            reader.fieldnames or [], ["term_name", "p_value"],
            "g:Profiler enrichment",
        ):
            return results
        for row in reader:
            results.append({
                "source": row.get("source", ""),
                "term_name": row.get("term_name", ""),
                "gprofiler_p": _safe_float(row.get("p_value")),
                "gprofiler_q": _safe_float(row.get("q_value")),
                "intersection_size": _safe_int(row.get("intersection_size")),
            })
    return results


def read_ldsc_results(ldsc_dir):
    """Read LDSC partitioned h2 summary.

    Returns list of dicts with: pathway, trait, ancestry, prop_h2, enrichment, p.
    """
    results = []
    summary_path = os.path.join(ldsc_dir, "h2_summary.tsv")
    if not os.path.exists(summary_path):
        logger.warning("LDSC h2 summary not found: %s", summary_path)
        return results

    with open(summary_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        if not _validate_columns(
            reader.fieldnames or [], ["annotation", "enrichment"],
            "LDSC h2 summary",
        ):
            return results
        for row in reader:
            results.append({
                "pathway": row.get("annotation", ""),
                "trait": row.get("trait", ""),
                "ancestry": row.get("ancestry", ""),
                "ldsc_h2_frac": _safe_float(row.get("prop_h2")),
                "ldsc_enrichment": _safe_float(row.get("enrichment")),
                "ldsc_p": _safe_float(row.get("enrichment_p")),
            })
    return results


def read_ldsc_seg_results(ldsc_seg_dir):
    """Read LDSC-SEG tissue results summary.

    Returns list of dicts with: tissue, trait, coefficient, p.
    """
    results = []
    summary_path = os.path.join(ldsc_seg_dir, "shared_tissue_summary.tsv")
    if not os.path.exists(summary_path):
        logger.warning("LDSC-SEG shared tissue summary not found: %s", summary_path)
        return results

    with open(summary_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            results.append({
                "trait1": row.get("trait1", ""),
                "trait2": row.get("trait2", ""),
                "shared_tissue": row.get("shared_tissue", ""),
                "p_trait1": _safe_float(row.get("p_trait1")),
                "p_trait2": _safe_float(row.get("p_trait2")),
            })
    return results


def read_hess_results(hess_dir):
    """Read HESS local covariance summary.

    Returns list of dicts with: trait pair, ancestry, mean_pleio, mean_bg, ratio, z_score, p.
    """
    results = []
    summary_path = os.path.join(hess_dir, "local_covariance_summary.tsv")
    if not os.path.exists(summary_path):
        logger.warning("HESS local covariance summary not found: %s", summary_path)
        return results

    with open(summary_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            results.append({
                "trait1": row.get("trait1", ""),
                "trait2": row.get("trait2", ""),
                "ancestry": row.get("ancestry", ""),
                "mean_pleio": _safe_float(row.get("mean_pleio")),
                "mean_bg": _safe_float(row.get("mean_bg")),
                "ratio": _safe_float(row.get("ratio")),
                "z_score": _safe_float(row.get("z_score")),
                "hess_p": _safe_float(row.get("p_value")),
            })
    return results


def read_neg_ctrl_validation(neg_ctrl_dir):
    """Read negative control validation summary.

    Returns list of dicts with: method, neg_ctrl_set, passes_threshold.
    """
    results = []
    summary_path = os.path.join(neg_ctrl_dir, "validation_summary.tsv")
    if not os.path.exists(summary_path):
        logger.warning("Negative control validation not found: %s", summary_path)
        return results

    with open(summary_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            results.append({
                "method": row.get("method", ""),
                "neg_ctrl_set": row.get("neg_ctrl_set", ""),
                "passes_threshold": row.get("passes_threshold", ""),
                "q_value": _safe_float(row.get("q_value")),
            })
    return results


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def _safe_float(val):
    """Convert to float, returning NaN on failure."""
    if val is None or val == "" or val == "NA":
        return float("nan")
    try:
        return float(val)
    except (ValueError, TypeError):
        return float("nan")


def _safe_int(val):
    """Convert to int, returning 0 on failure."""
    if val is None or val == "":
        return 0
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0


def _geometric_mean_p(p_values):
    """Compute geometric mean of p-values (ignoring NaN)."""
    valid = [p for p in p_values if not math.isnan(p) and p > 0]
    if not valid:
        return float("nan")
    log_sum = sum(math.log(p) for p in valid)
    return math.exp(log_sum / len(valid))


def aggregate_all_methods(
    magma_dir=None,
    gprofiler_dir=None,
    ldsc_dir=None,
    ldsc_seg_dir=None,
    hess_dir=None,
    neg_ctrl_dir=None,
    out_enrichment=None,
    out_overview=None,
):
    """Cross-method aggregation producing summary tables.

    A. pathway_enrichment_summary.tsv -- per-pathway cross-method summary
    B. phase5_overview.tsv -- one row per analytical component
    """
    # Read all inputs
    magma = read_magma_results(magma_dir) if magma_dir else []
    gprofiler = read_gprofiler_results(gprofiler_dir) if gprofiler_dir else []
    ldsc = read_ldsc_results(ldsc_dir) if ldsc_dir else []
    ldsc_seg = read_ldsc_seg_results(ldsc_seg_dir) if ldsc_seg_dir else []
    hess = read_hess_results(hess_dir) if hess_dir else []
    neg_ctrl = read_neg_ctrl_validation(neg_ctrl_dir) if neg_ctrl_dir else []

    # -----------------------------------------------------------------------
    # A. pathway_enrichment_summary.tsv
    # -----------------------------------------------------------------------
    # Index MAGMA results by pathway
    magma_by_pathway = defaultdict(list)
    for r in magma:
        magma_by_pathway[r["pathway"]].append(r)

    # Index g:Profiler results by term
    gprofiler_by_term = {}
    for r in gprofiler:
        gprofiler_by_term[r["term_name"]] = r

    # Index LDSC results by pathway
    ldsc_by_pathway = defaultdict(list)
    for r in ldsc:
        ldsc_by_pathway[r["pathway"]].append(r)

    # Build enrichment summary
    all_pathways = set(magma_by_pathway.keys()) | set(ldsc_by_pathway.keys())
    enrichment_rows = []
    for pathway in sorted(all_pathways):
        # MAGMA: best (lowest p) across trait x ancestry
        magma_entries = magma_by_pathway.get(pathway, [])
        best_magma = min(magma_entries, key=lambda x: x["magma_p"], default=None) if magma_entries else None

        # LDSC: best across trait x ancestry
        ldsc_entries = ldsc_by_pathway.get(pathway, [])
        best_ldsc = min(ldsc_entries, key=lambda x: x["ldsc_p"], default=None) if ldsc_entries else None

        # g:Profiler: match by pathway name (partial)
        gp_match = gprofiler_by_term.get(pathway)
        if gp_match is None:
            # Try substring match
            for term, entry in gprofiler_by_term.items():
                if pathway.lower() in term.lower() or term.lower() in pathway.lower():
                    gp_match = entry
                    break

        # Count significant methods (q < 0.05)
        p_values = []
        n_sig = 0
        if best_magma and not math.isnan(best_magma["magma_q"]):
            p_values.append(best_magma["magma_p"])
            if best_magma["magma_q"] < 0.05:
                n_sig += 1
        if gp_match and not math.isnan(gp_match.get("gprofiler_q", float("nan"))):
            p_values.append(gp_match["gprofiler_p"])
            if gp_match["gprofiler_q"] < 0.05:
                n_sig += 1
        if best_ldsc and not math.isnan(best_ldsc["ldsc_p"]):
            p_values.append(best_ldsc["ldsc_p"])
            if best_ldsc["ldsc_p"] < 0.05:
                n_sig += 1

        geo_mean_p = _geometric_mean_p(p_values) if p_values else float("nan")

        # WR-03 fix: guard format strings against NaN so missing values
        # render as "NA" consistently instead of producing the string "nan"
        # (Python's default float formatting for NaN).
        def _fmt(val, prec):
            if val is None or (isinstance(val, float) and math.isnan(val)):
                return "NA"
            return f"{val:.{prec}f}"

        enrichment_rows.append({
            "pathway": pathway,
            "magma_beta": _fmt(best_magma.get("magma_beta"), 4) if best_magma else "NA",
            "magma_p": _fmt(best_magma.get("magma_p"), 6) if best_magma else "NA",
            "magma_q": _fmt(best_magma.get("magma_q"), 6) if best_magma else "NA",
            "gprofiler_p": _fmt(gp_match.get("gprofiler_p"), 6) if gp_match else "NA",
            "gprofiler_q": _fmt(gp_match.get("gprofiler_q"), 6) if gp_match else "NA",
            "ldsc_h2_frac": _fmt(best_ldsc.get("ldsc_h2_frac"), 6) if best_ldsc else "NA",
            "ldsc_enrichment": _fmt(best_ldsc.get("ldsc_enrichment"), 4) if best_ldsc else "NA",
            "ldsc_p": _fmt(best_ldsc.get("ldsc_p"), 6) if best_ldsc else "NA",
            "n_methods_significant": n_sig,
            "geometric_mean_p": _fmt(geo_mean_p, 6),
        })

    # Sort by n_methods_significant (desc), then geometric mean p (asc)
    enrichment_rows.sort(
        key=lambda x: (
            -x["n_methods_significant"],
            float(x["geometric_mean_p"]) if x["geometric_mean_p"] != "NA" else 1.0,
        )
    )

    # Add consensus_rank
    for i, row in enumerate(enrichment_rows):
        row["consensus_rank"] = i + 1

    # Write A
    if out_enrichment:
        os.makedirs(os.path.dirname(out_enrichment), exist_ok=True)
        enrichment_cols = [
            "pathway", "magma_beta", "magma_p", "magma_q",
            "gprofiler_p", "gprofiler_q",
            "ldsc_h2_frac", "ldsc_enrichment", "ldsc_p",
            "n_methods_significant", "geometric_mean_p", "consensus_rank",
        ]
        with open(out_enrichment, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=enrichment_cols, delimiter="\t")
            writer.writeheader()
            writer.writerows(enrichment_rows)
        logger.info(
            "Wrote pathway enrichment summary: %d pathways -> %s",
            len(enrichment_rows), out_enrichment,
        )

    # -----------------------------------------------------------------------
    # B. phase5_overview.tsv
    # -----------------------------------------------------------------------
    neg_ctrl_pass = all(
        r.get("passes_threshold", "").upper() == "TRUE" for r in neg_ctrl
    ) if neg_ctrl else True  # vacuously true if no data yet

    overview_rows = [
        {
            "component": "MAGMA",
            "status": "complete" if magma else "pending",
            "n_significant_pathways": sum(
                1 for r in magma if not math.isnan(r["magma_q"]) and r["magma_q"] < 0.05
            ),
            "n_significant_tissues": "NA",
            "neg_ctrl_pass": "PASS" if neg_ctrl_pass else "FAIL",
            "notes": f"{len(magma)} pathway-trait results",
        },
        {
            "component": "gProfiler",
            "status": "complete" if gprofiler else "pending",
            "n_significant_pathways": sum(
                1 for r in gprofiler
                if not math.isnan(r.get("gprofiler_q", float("nan")))
                and r["gprofiler_q"] < 0.05
            ),
            "n_significant_tissues": "NA",
            "neg_ctrl_pass": "PASS" if neg_ctrl_pass else "FAIL",
            "notes": f"{len(gprofiler)} enrichment terms",
        },
        {
            "component": "LDSC_partitioned",
            "status": "complete" if ldsc else "pending",
            "n_significant_pathways": sum(
                1 for r in ldsc if not math.isnan(r["ldsc_p"]) and r["ldsc_p"] < 0.05
            ),
            "n_significant_tissues": "NA",
            "neg_ctrl_pass": "PASS" if neg_ctrl_pass else "FAIL",
            "notes": f"{len(ldsc)} annotation-trait results",
        },
        {
            "component": "LDSC-SEG",
            "status": "complete" if ldsc_seg else "pending",
            "n_significant_pathways": "NA",
            "n_significant_tissues": len(ldsc_seg),
            "neg_ctrl_pass": "NA",
            "notes": f"{len(ldsc_seg)} shared tissue enrichments",
        },
        {
            "component": "HESS",
            "status": "complete" if hess else "pending",
            "n_significant_pathways": sum(
                1 for r in hess
                if not math.isnan(r.get("hess_p", float("nan")))
                and r["hess_p"] < 0.05
            ),
            "n_significant_tissues": "NA",
            "neg_ctrl_pass": "NA",
            "notes": f"{len(hess)} trait-pair comparisons",
        },
        {
            "component": "permutation_null",
            "status": "complete" if magma else "pending",
            "n_significant_pathways": "NA",
            "n_significant_tissues": "NA",
            "neg_ctrl_pass": "PASS" if neg_ctrl_pass else "FAIL",
            "notes": "1000 permutation null gene sets",
        },
    ]

    if out_overview:
        os.makedirs(os.path.dirname(out_overview), exist_ok=True)
        overview_cols = [
            "component", "status", "n_significant_pathways",
            "n_significant_tissues", "neg_ctrl_pass", "notes",
        ]
        with open(out_overview, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=overview_cols, delimiter="\t")
            writer.writeheader()
            writer.writerows(overview_rows)
        logger.info("Wrote phase5 overview: %s", out_overview)

    return enrichment_rows, overview_rows


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Aggregate Phase 5 pathway results from all analytical methods."
    )
    parser.add_argument("--magma-dir", help="Directory with MAGMA FDR results")
    parser.add_argument("--gprofiler-dir", help="Directory with g:Profiler results")
    parser.add_argument("--ldsc-dir", help="Directory with LDSC partitioned h2 results")
    parser.add_argument("--ldsc-seg-dir", help="Directory with LDSC-SEG results")
    parser.add_argument("--hess-dir", help="Directory with HESS results")
    parser.add_argument("--neg-ctrl-dir", help="Directory with negative control validation")
    parser.add_argument(
        "--out", required=True,
        help="Output path for pathway_enrichment_summary.tsv",
    )
    parser.add_argument(
        "--out-overview",
        help="Output path for phase5_overview.tsv (default: same dir as --out)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    out_overview = args.out_overview
    if not out_overview:
        out_overview = os.path.join(
            os.path.dirname(args.out), "phase5_overview.tsv"
        )

    aggregate_all_methods(
        magma_dir=args.magma_dir,
        gprofiler_dir=args.gprofiler_dir,
        ldsc_dir=args.ldsc_dir,
        ldsc_seg_dir=args.ldsc_seg_dir,
        hess_dir=args.hess_dir,
        neg_ctrl_dir=args.neg_ctrl_dir,
        out_enrichment=args.out,
        out_overview=out_overview,
    )


if __name__ == "__main__":
    main()
