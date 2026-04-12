#!/usr/bin/env python3
# ============================================================
# Phase 1 NOTE (REQ-2, B-03 resolved): When fit-persistence is first enabled,
# {FINEMAP_DIR}/susie/ MUST be cleared before the first real execution.
# Snakemake tracks file mtimes not rule versions; stale JSON outputs from
# Phase 0 dry-runs bypass the new .fit.rds dependency and leave run_coloc_susie
# permanently broken. Execute before first Wave 1 real run:
#     rm -rf {FINEMAP_DIR}/susie/
# OR pass --forceall run_finemap to snakemake.
# Threat mitigation: T-1-05 (cache poisoning on fit-persistence switchover).
# ============================================================
"""
Augment the fine-mapping summary with LD metadata and derive a high-confidence subset.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


DEFAULT_TIER1_OUT = "results/fine_mapping/finemap_tier1_high_conf.tsv"
DEFAULT_TIER2_OUT = "results/fine_mapping/finemap_tier2_relaxed.tsv"
DEFAULT_TIER3_OUT = "results/fine_mapping/finemap_tier3_coloc.tsv"


def _parse_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def _parse_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _load_ld_meta(path: Path) -> Tuple[str, str]:
    """
    Return (ld_status_raw, ld_matrix_path_or_identity).
    """
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        return ("missing_json", "")
    except json.JSONDecodeError:
        return ("invalid_json", "")

    return (str(data.get("ld_status") or ""), str(data.get("ld_matrix") or ""))


def _categorize_ld(ld_status_raw: str, ld_matrix: str) -> str:
    status = (ld_status_raw or "").lower()
    matrix = (ld_matrix or "").lower()

    if not status and not matrix:
        return "unknown"
    if "missing" in status:
        return "ld_missing"
    if "fallback_identity" in status:
        return "identity"
    if matrix == "identity":
        return "identity"
    if "ld_loaded" in status or "used" in status or matrix.endswith(".rds"):
        return "used_ld"
    if status in {"invalid_json", "missing_json"}:
        return status

    return "unknown"


def _load_variant_counts(variant_dir: Path) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    if not variant_dir.exists():
        return counts
    for path in variant_dir.glob("*.tsv"):
        try:
            with path.open() as handle:
                next(handle, None)  # skip header
                count = sum(1 for _ in handle)
        except OSError:
            continue
        counts[path.stem] = count
    return counts


def _evaluate_tier(
    *,
    status: Optional[str],
    ld_flag: str,
    n_snps: Optional[int],
    n_cs: Optional[int],
    top_pip: Optional[float],
    min_snps: Optional[int],
    max_cs: Optional[int],
    min_top_pip: Optional[float],
    allow_identity: bool,
    allowed_ld: Optional[Iterable[str]] = None,
) -> Tuple[bool, List[str]]:
    """Apply tier-specific QC thresholds and return (pass?, issues)."""

    issues: List[str] = []

    status_val = (status or "").lower()
    ld_val = (ld_flag or "").lower()
    allowed_ld_set = {value.lower() for value in allowed_ld} if allowed_ld else None

    if status_val != "success":
        issues.append("status!=success")

    if ld_val == "ld_missing":
        issues.append("ld_missing")
    elif ld_val.startswith("missing_json") or ld_val.startswith("invalid_json"):
        issues.append(ld_val)
    elif allowed_ld_set is not None and ld_val not in allowed_ld_set:
        issues.append(f"ld_flag={ld_val or 'none'}")
    elif ld_val == "identity" and not allow_identity:
        issues.append("ld_identity")
    elif not ld_val:
        issues.append("ld_flag_missing")

    if n_snps is None:
        issues.append("n_snps_missing")
    elif min_snps is not None and n_snps < min_snps:
        issues.append(f"n_snps<{min_snps}")

    if n_cs is None:
        issues.append("n_cs_missing")
    elif max_cs is not None and n_cs > max_cs:
        issues.append(f"n_cs>{max_cs}")

    if top_pip is None:
        issues.append("top_pip_missing")
    elif min_top_pip is not None and top_pip < min_top_pip:
        issues.append(f"top_pip<{min_top_pip}")

    return (len(issues) == 0, issues)


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--summary",
        default="results/fine_mapping/finemap_summary.tsv",
        help="Path to the raw finemap summary TSV.",
    )
    p.add_argument(
        "--augment-out",
        default="results/fine_mapping/finemap_summary_augmented.tsv",
        help="Output path for the augmented summary.",
    )
    p.add_argument(
        "--tier1-out",
        default=DEFAULT_TIER1_OUT,
        help="Output path for the Tier 1 (strict) subset.",
    )
    # Backwards-compatible alias for legacy workflows that still pass
    # --filtered-out. Hidden from --help to avoid clutter.
    p.add_argument(
        "--filtered-out",
        dest="legacy_filtered_out",
        help=argparse.SUPPRESS,
    )
    p.add_argument(
        "--tier2-out",
        default=DEFAULT_TIER2_OUT,
        help="Output path for the Tier 2 (relaxed) subset.",
    )
    p.add_argument(
        "--tier3-out",
        default=DEFAULT_TIER3_OUT,
        help="Output path for the Tier 3 coloc-eligible subset.",
    )
    p.add_argument(
        "--variant-dir",
        default="data_processed/ld_reference/variants",
        help="Directory with region-level variant manifests.",
    )
    p.add_argument("--min-snps", type=int, default=50)
    p.add_argument("--max-cs", type=int, default=3)
    p.add_argument("--min-top-pip", type=float, default=0.5)
    p.add_argument(
        "--allow-identity",
        action="store_true",
        help="Allow identity LD matrices to pass the QC filter.",
    )
    p.add_argument("--tier2-min-snps", type=int, default=50)
    p.add_argument("--tier2-max-cs", type=int, default=5)
    p.add_argument("--tier2-min-top-pip", type=float, default=0.3)
    p.add_argument("--tier3-min-snps", type=int, default=30)
    return p


def main() -> None:
    args = _build_arg_parser().parse_args()

    summary_path = Path(args.summary)
    augment_path = Path(args.augment_out)
    tier1_path = Path(args.tier1_out or DEFAULT_TIER1_OUT)
    if getattr(args, "legacy_filtered_out", None):
        tier1_path = Path(args.legacy_filtered_out)
    tier2_path = Path(args.tier2_out or DEFAULT_TIER2_OUT)
    tier3_path = Path(args.tier3_out or DEFAULT_TIER3_OUT)
    variant_counts = _load_variant_counts(Path(args.variant_dir))

    if not summary_path.exists():
        raise SystemExit(f"Summary file not found: {summary_path}")

    augmented_rows: List[dict] = []
    tier1_rows: List[dict] = []
    tier2_rows: List[dict] = []
    tier3_rows: List[dict] = []

    tier1_cfg = {
        "min_snps": args.min_snps,
        "max_cs": args.max_cs,
        "min_top_pip": args.min_top_pip,
        "allow_identity": args.allow_identity,
        "allowed_ld": {"used_ld"},
    }
    tier2_cfg = {
        "min_snps": args.tier2_min_snps,
        "max_cs": args.tier2_max_cs,
        "min_top_pip": args.tier2_min_top_pip,
        "allow_identity": True,  # explicitly allow identity but mark via ld_flag
        "allowed_ld": {"used_ld", "identity"},
    }

    with summary_path.open() as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise SystemExit("Summary file is empty or missing headers.")

        base_fields = reader.fieldnames

        for row in reader:
            row = dict(row)
            n_snps = _parse_int(row.get("pip_nonzero")) or _parse_int(
                row.get("variants_in_cs")
            )
            n_cs = _parse_int(row.get("credible_sets"))
            top_pip = _parse_float(row.get("top_pip"))

            region_id = row.get("region_id", "")
            region_variant_total = variant_counts.get(region_id)

            json_path = Path(row.get("output_path", ""))
            ld_status_raw, ld_matrix_path = _load_ld_meta(json_path)
            ld_flag = _categorize_ld(ld_status_raw, ld_matrix_path)

            tier1_pass, tier1_issues = _evaluate_tier(
                status=row.get("status"),
                ld_flag=ld_flag,
                n_snps=n_snps,
                n_cs=n_cs,
                top_pip=top_pip,
                **tier1_cfg,
            )
            tier2_pass, tier2_issues = _evaluate_tier(
                status=row.get("status"),
                ld_flag=ld_flag,
                n_snps=n_snps,
                n_cs=n_cs,
                top_pip=top_pip,
                **tier2_cfg,
            )

            row["n_snps"] = n_snps if n_snps is not None else ""
            row["n_cs"] = n_cs if n_cs is not None else ""
            row["top_pip"] = (
                f"{top_pip:.4f}" if top_pip is not None else row.get("top_pip", "")
            )
            row["ld_status_raw"] = ld_status_raw
            row["ld_matrix_path"] = ld_matrix_path
            row["ld_flag"] = ld_flag
            row["region_variant_total"] = (
                region_variant_total if region_variant_total is not None else ""
            )
            row["high_confidence"] = "yes" if tier1_pass else "no"
            row["qc_notes"] = ";".join(tier1_issues)
            row["tier2_high_confidence"] = "yes" if tier2_pass else "no"
            row["tier2_qc_notes"] = ";".join(tier2_issues)

            augmented_rows.append(row)
            tier3_pass = row.get("status", "").lower() == "success"

            if tier1_pass:
                tier1_rows.append(dict(row))
            if tier2_pass:
                tier2_rows.append(dict(row))
            if tier3_pass:
                tier3_row = dict(row)
                tier3_row["tier3_coloc_flag"] = "yes"
                tier3_rows.append(tier3_row)

    extra_fields = [
        "n_snps",
        "n_cs",
        "ld_flag",
        "ld_status_raw",
        "ld_matrix_path",
        "region_variant_total",
        "high_confidence",
        "qc_notes",
        "tier2_high_confidence",
        "tier2_qc_notes",
    ]
    out_fields = base_fields + [f for f in extra_fields if f not in base_fields]

    augment_path.parent.mkdir(parents=True, exist_ok=True)
    tier1_path.parent.mkdir(parents=True, exist_ok=True)
    tier2_path.parent.mkdir(parents=True, exist_ok=True)
    tier3_path.parent.mkdir(parents=True, exist_ok=True)

    with augment_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=out_fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(augmented_rows)

    out_fields_tier3 = list(out_fields)
    if "tier3_coloc_flag" not in out_fields_tier3:
        out_fields_tier3.append("tier3_coloc_flag")

    with tier1_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=out_fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(tier1_rows)

    with tier2_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=out_fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(tier2_rows)

    with tier3_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=out_fields_tier3, delimiter="\t")
        writer.writeheader()
        writer.writerows(tier3_rows)


if __name__ == "__main__":
    main()
