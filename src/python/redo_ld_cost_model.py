#!/usr/bin/env python3
"""redo_ld_cost_model.py — m3-02d LD production cost model + go/no-go gate.

This is the m3-02c Task 4 that was specced but NEVER built; this plan (m3-02d)
finalizes it. It turns the COMPLETING-cell re-probe rates (m3-W2-cost-probe.tsv)
+ the re-split REAL preflight counts (m3-W2-preflight-counts.tsv) + the post-split
projection into a defensible GREEN/RED go/no-go for the 322-cell production fire
(which stays OUT of scope here — it is Wave 4 / m3-04).

Binding-constraint re-scope (m3-02d): the cost is driven by the A.3 BlockMatrix
WRITE throughput + the per-cell EGRESS bundle size, extrapolated from the MEASURED
COMPLETING-cell blocks_per_min over the REAL preflight block counts — NOT span
guesses and NOT the INTERRUPTED/NA prior probe row (which is EXCLUDED).

Three separate totals (do not conflate):
  (a) n_logical_parent_panels == 322   (the M2 region x ancestry logical panels)
  (b) n_compute_cells > 322            (post-split: each xlarge parent -> N sub cells)
  (c) aggregate parent cost            (an xlarge parent == Sigma over its
                                        split_status=="subregion" rows)

The gate predicate is EXACT:  projected * 1.3 <= budget_cap_cluster_h  -> GREEN,
else YELLOW-narrow-radius / YELLOW-finer-split / RED.

REQ-PATH-PARAMETERIZATION: no hardcoded absolute HPC filesystem paths; every input
is a CLI argument.
"""
from __future__ import annotations

import argparse
import math
import statistics
from pathlib import Path

import pandas as pd

# Reuse the per-chromosome egress bundling helper (do NOT re-implement) — Task 2.
import ld_egress_bundle

# Fallback EUR/AFR write-rate factor when NO completing EUR cell exists in the probe
# (research A7 sample-ratio assumption: EUR ~220k / AFR ~73k ~= 3.01x slower). The
# +/-20% band is recorded as the source so the memo flags it as ASSUMED not measured.
EUR_FACTOR_FALLBACK = 3.01
EUR_FACTOR_FALLBACK_BAND = 0.20

# Contingency: factor = 1 + CONTINGENCY_K * CoV(probe blocks_per_min), floored.
CONTINGENCY_K = 0.5
CONTINGENCY_FLOOR = 1.15

# The EXACT GATE-1 headroom multiplier (projected * HEADROOM <= budget_cap).
GATE_HEADROOM = 1.3

# Pan-UKBB conservative LD band anchor (Mb). If the manifest still bands WIDER than
# this there is "narrow-radius" lever room (YELLOW-narrow-radius). Post-Q3 the locked
# buffers are already 3/5 Mb (< 10), so YELLOW-finer-split is the likelier lever.
PAN_UKBB_RADIUS_MB = 10

# Per-worker cluster credit rate ($/hr) — n2-standard-16 worker (research A8 band,
# flag for confirmation at the gate). Used only for the memo's credit-$ line.
WORKER_USD_PER_HOUR = 1.00

# Status values that DISQUALIFY a probe row from contributing a rate.
_NON_COMPLETING_STATUS_TOKENS = ("interrupt", "fail", "killed", "partial", "na")


def _is_completing(status: str) -> bool:
    """True iff the probe row's status is a COMPLETED run (a usable rate basis)."""
    s = str(status).strip().lower()
    if not s:
        return False
    if "completed" in s or s == "ok" or s == "complete":
        return any(tok not in s for tok in ("interrupt", "fail", "killed")) or True
    return False


def _na(v) -> bool:
    """True for NA / blank / non-numeric rate cells."""
    if v is None:
        return True
    s = str(v).strip().lower()
    return s in ("", "na", "nan", "none")


def load_probe_rates(probe_tsv) -> dict:
    """Read m3-W2-cost-probe.tsv -> COMPLETING-cell rate basis.

    EXCLUDES INTERRUPTED / NA-rate rows (the prior probe row is exactly this — it
    must NEVER be treated as a rate). Returns a dict:
        {
          "rates": {(ancestry, region_class): blocks_per_min, ...},
          "by_ancestry": {ancestry: blocks_per_min (mean over its completing cells)},
          "rate_list": [blocks_per_min, ...]  (for the contingency CoV),
          "overhead_factor": end_to_end_wall_min / stage4_wall_min (mean),
          "cluster_vcpu": int (from a completing row),
          "rows": [completing row dicts],
        }
    """
    df = pd.read_csv(probe_tsv, sep="\t", dtype=str)
    rates: dict = {}
    by_ancestry_acc: dict = {}
    rate_list: list[float] = []
    overheads: list[float] = []
    cluster_vcpu = None
    completing_rows: list[dict] = []
    for _, r in df.iterrows():
        if not _is_completing(r.get("status", "")):
            continue
        if _na(r.get("blocks_per_min")):
            # A COMPLETED row MUST carry a real rate; a NA rate is a data error.
            raise ValueError(
                f"probe row {r.get('region_id')} is COMPLETED but blocks_per_min is "
                f"NA — a completing cell must carry a real rate"
            )
        bpm = float(r["blocks_per_min"])
        anc = str(r["ancestry"])
        cls = str(r["region_class"])
        rates[(anc, cls)] = bpm
        by_ancestry_acc.setdefault(anc, []).append(bpm)
        rate_list.append(bpm)
        completing_rows.append(dict(r))
        if not _na(r.get("stage4_wall_min")) and not _na(r.get("end_to_end_wall_min")):
            s4 = float(r["stage4_wall_min"])
            e2e = float(r["end_to_end_wall_min"])
            if s4 > 0:
                overheads.append(e2e / s4)
        if cluster_vcpu is None and not _na(r.get("cluster_vcpu")):
            cluster_vcpu = int(float(r["cluster_vcpu"]))
    by_ancestry = {a: statistics.fmean(v) for a, v in by_ancestry_acc.items()}
    overhead_factor = statistics.fmean(overheads) if overheads else 1.0
    if not rate_list:
        raise ValueError(
            "no COMPLETING probe cells with a real blocks_per_min — the cost model "
            "cannot extrapolate from an INTERRUPTED/NA-only probe (the prior failure "
            "mode). Re-run the re-probe to completion first."
        )
    return {
        "rates": rates,
        "by_ancestry": by_ancestry,
        "rate_list": rate_list,
        "overhead_factor": overhead_factor,
        "cluster_vcpu": cluster_vcpu or 384,
        "rows": completing_rows,
    }


def load_preflight_counts(preflight_tsv) -> pd.DataFrame:
    """Read m3-W2-preflight-counts.tsv -> per-cell REAL n_var/block_count/output GiB.

    The cost model consumes THIS (real counts), not span guesses. Adds a
    ``parent_region_id`` column derived from the ``__sub`` naming so the
    three-totals parent aggregate can group sub-cells back to their xlarge parent.
    """
    df = pd.read_csv(preflight_tsv, sep="\t")
    df["n_var"] = df["n_var"].astype(int)
    df["est_block_count"] = df["est_block_count"].astype(float)
    df["est_output_gib"] = df["est_output_gib"].astype(float)
    df["parent_region_id"] = df["region_id"].astype(str).apply(
        lambda rid: rid.split("__sub")[0] if "__sub" in rid else rid
    )
    df["is_subregion"] = df["region_id"].astype(str).str.contains("__sub")
    return df


def eur_factor(probe) -> tuple[float, str]:
    """Measured EUR/AFR write-rate factor, else the A7 sample-ratio fallback.

    If both an AFR and EUR completing rate exist, factor = afr_rate / eur_rate
    (EUR slower => factor > 1, source="measured"). Else (3.01 +/- 20%,
    source="sample-ratio-assumed-A7").
    """
    by_anc = probe["by_ancestry"]
    if "AFR" in by_anc and "EUR" in by_anc and by_anc["EUR"] > 0:
        return by_anc["AFR"] / by_anc["EUR"], "measured"
    return EUR_FACTOR_FALLBACK, (
        f"sample-ratio-assumed-A7 (+/-{EUR_FACTOR_FALLBACK_BAND:.0%})"
    )


def n_workers_plus_master(cluster_vcpu: int, vcpu_per_worker: int = 16) -> int:
    """workers (cluster_vcpu / vcpu_per_worker) + 1 MASTER. All cluster_hours use this."""
    workers = int(round(cluster_vcpu / vcpu_per_worker))
    return workers + 1  # the +1 is the MASTER (master-inclusive accounting)


def project_cell_hours(preflight_df: pd.DataFrame, probe: dict,
                       eur_fac: float) -> pd.DataFrame:
    """Per compute cell: master-inclusive end-to-end cluster-hours from REAL counts.

    cluster_h = (block_count / matched_blocks_per_min / 60)   # node-hours of write
                * overhead_factor                              # end-to-end (not Stage-4)
                * (n_workers + 1)                              # MASTER-inclusive
    EUR cells are scaled by eur_fac (EUR write is eur_fac x slower than the AFR rate).
    The matched rate is the AFR completing rate (the reference); EUR derives via the
    factor so a single AFR completing cell suffices when paired with the measured
    or assumed EUR factor.
    """
    by_anc = probe["by_ancestry"]
    afr_rate = by_anc.get("AFR") or next(iter(by_anc.values()))
    overhead = probe["overhead_factor"]
    npm = n_workers_plus_master(probe["cluster_vcpu"])

    rows = []
    for _, r in preflight_df.iterrows():
        anc = str(r["ancestry"])
        block_count = float(r["est_block_count"])
        # AFR rate is the reference; EUR is eur_fac x slower (=> eur_fac x the hours).
        anc_scale = eur_fac if anc == "EUR" else 1.0
        write_node_h = block_count / afr_rate / 60.0 if afr_rate > 0 else 0.0
        cell_h = write_node_h * anc_scale * overhead * npm
        rows.append({
            "region_id": r["region_id"],
            "ancestry": anc,
            "region_class": r["region_class"],
            "parent_region_id": r["parent_region_id"],
            "is_subregion": bool(r["is_subregion"]),
            "n_var": int(r["n_var"]),
            "est_block_count": block_count,
            "est_output_gib": float(r["est_output_gib"]),
            "cluster_hours": cell_h,
        })
    return pd.DataFrame(rows)


def three_totals(projected_df: pd.DataFrame, projection_df: pd.DataFrame) -> dict:
    """The THREE separate totals. xlarge parents priced ONLY as Sigma over subs.

    (a) n_logical_parent_panels: the logical M2 region x ancestry panels. Counted
        from the projection's whole+parent rows x the 2 ancestries (== 322).
    (b) n_compute_cells: the expanded per-ancestry compute cells (> 322 post-split).
    (c) parent_aggregate: groupby(parent_region_id).cluster_hours.sum() — an xlarge
        parent's cost == the sum over its split_status=="subregion" rows.
    """
    # (a) logical parents: whole + parent projection rows, x the ancestries present.
    logical_units = projection_df[
        projection_df["split_status"].isin(["whole", "parent"])
    ]["region_id"].nunique()
    ancestries = sorted(projected_df["ancestry"].unique())
    n_logical_parents = logical_units * len(ancestries)

    # (b) compute cells = the per-ancestry compute rows.
    n_compute_cells = len(projected_df)

    # (c) parent aggregate (xlarge = Sigma over its subregion rows).
    parent_aggregate = (
        projected_df.groupby("parent_region_id")["cluster_hours"].sum().to_dict()
    )

    total_compute_h = float(projected_df["cluster_hours"].sum())
    total_parent_h = float(sum(parent_aggregate.values()))
    return {
        "n_logical_parents": n_logical_parents,
        "n_compute_cells": n_compute_cells,
        "parent_aggregate": parent_aggregate,
        "total_compute_h": total_compute_h,
        "total_parent_h": total_parent_h,
    }


def apply_contingency(total_h: float, rate_list: list[float]) -> tuple[float, float]:
    """Contingency factor from the probe blocks_per_min variance (CoV).

    factor = max(CONTINGENCY_FLOOR, 1 + CONTINGENCY_K * CoV); CoV = stdev/mean.
    Returns (total_with_contingency, contingency_factor). With < 2 rate samples the
    CoV is undefined -> the floor applies.
    """
    if len(rate_list) >= 2:
        mean = statistics.fmean(rate_list)
        cov = (statistics.stdev(rate_list) / mean) if mean > 0 else 0.0
    else:
        cov = 0.0
    factor = max(CONTINGENCY_FLOOR, 1.0 + CONTINGENCY_K * cov)
    return total_h * factor, factor


def project_egress_bundles(preflight_df: pd.DataFrame) -> dict:
    """Per-chromosome egress bundle projection (reuses ld_egress_bundle).

    Sums est_output_gib per chromosome over the compute cells, plans the per-chrom
    bundles (splitting any > EGRESS_CAP_GB into chrN_a/chrN_b), and flags the totals
    against the 50 GB working ceiling.
    """
    cells = [
        {
            "region_id": str(r["region_id"]),
            "chr": str(r["chr"]) if "chr" in preflight_df.columns else "NA",
            "bytes": int(round(float(r["est_output_gib"]) * 1e9)),
        }
        for _, r in preflight_df.iterrows()
    ]
    bundles = ld_egress_bundle.plan_egress_bundles(cells)
    total_gib = float(preflight_df["est_output_gib"].sum())
    return {
        "total_output_gib": total_gib,
        "n_bundles": len(bundles),
        "bundles": bundles,
        "n_over_cap": ld_egress_bundle.n_bundles_over_cap(bundles),
        "chromosomes_split": ld_egress_bundle.chromosomes_split(bundles),
        "egress_cap_gb": ld_egress_bundle.EGRESS_CAP_GB,
    }


def evaluate_gate(projected: float, budget_cap_cluster_h: float, *,
                  lever_room_radius_mb: "float | None" = None,
                  dominant_class: "str | None" = None) -> dict:
    """Evaluate the EXACT go/no-go gate: projected * 1.3 <= budget_cap.

    Disposition:
      GREEN              if projected * 1.3 <= budget_cap (headroom_ok)
      YELLOW-narrow-radius  if there is band to cut (current buffer > Pan-UKBB 10 Mb)
      YELLOW-finer-split    if a class dominates and the buffer is already narrow
                            (the likelier post-Q3 lever)
      RED                if no lever room
    """
    # The EXACT predicate:  projected * 1.3 <= budget_cap
    headroom_ok = projected * GATE_HEADROOM <= budget_cap_cluster_h
    if headroom_ok:
        disposition = "GREEN"
    elif lever_room_radius_mb is not None and lever_room_radius_mb > PAN_UKBB_RADIUS_MB:
        disposition = "YELLOW-narrow-radius"
    elif dominant_class is not None:
        # Buffer already narrow (post-Q3 3/5 Mb < 10 Mb) -> finer split is the lever.
        disposition = "YELLOW-finer-split"
    else:
        disposition = "RED"
    return {
        "projected": projected,
        "budget_cap": budget_cap_cluster_h,
        "headroom_multiplier": GATE_HEADROOM,
        "projected_x_headroom": projected * GATE_HEADROOM,
        "headroom_ok": headroom_ok,
        "disposition": disposition,
    }


def _dominant_class(projected_df: pd.DataFrame) -> "str | None":
    """The (ancestry, region_class) tuple contributing the most cluster-hours."""
    if projected_df.empty:
        return None
    grp = projected_df.groupby(["ancestry", "region_class"])["cluster_hours"].sum()
    if grp.empty:
        return None
    anc, cls = grp.idxmax()
    return f"{anc}/{cls}"


def _max_buffer_mb(preflight_df: pd.DataFrame, manifest_df: "pd.DataFrame | None") -> float:
    """Largest banding buffer (Mb) among compute cells — the narrow-radius lever room."""
    if manifest_df is not None and "buffer_bp" in manifest_df.columns:
        subs = manifest_df[manifest_df["region_id"].astype(str).str.contains("__sub")]
        if not subs.empty:
            return float(subs["buffer_bp"].astype(float).max()) / 1e6
    return 0.0


def build_budget_memo(*, totals: dict, contingency_factor: float,
                      projected_raw: float, projected: float,
                      gate: dict, egress: dict, eur_fac: float, eur_source: str,
                      probe: dict, budget_cap: float, manifest_df=None) -> str:
    """Render m3-W2-budget-redo.md (the go/no-go memo)."""
    credit_usd = projected * WORKER_USD_PER_HOUR
    lines = []
    lines.append("# m3-W2 Budget Redo — LD production go/no-go\n")
    lines.append(
        "Re-scoped around the MEASURED binding constraints (A.3 write throughput + "
        "per-cell egress GiB), extrapolated from the COMPLETING-cell re-probe rates "
        "over the REAL re-split preflight counts. The prior INTERRUPTED/NA probe row "
        "is EXCLUDED from the rate basis.\n"
    )
    lines.append("## Three totals (do not conflate)\n")
    lines.append(f"- **(a) n_logical_parent_panels** = {totals['n_logical_parents']} "
                 f"(the M2 region x ancestry logical panels)")
    lines.append(f"- **(b) n_compute_cells** = {totals['n_compute_cells']} "
                 f"(> 322 post-split: each xlarge parent expands into N sub-cells)")
    lines.append(f"- **(c) aggregate parent** = Sigma over each parent's "
                 f"split_status==subregion rows; total_parent_h = "
                 f"{totals['total_parent_h']:.1f} cluster-h\n")
    lines.append("## Extrapolation basis\n")
    lines.append(f"- COMPLETING probe rates (blocks_per_min): {probe['by_ancestry']}")
    lines.append(f"- measured EUR/AFR write factor = {eur_fac:.3f} (source: {eur_source})")
    lines.append(f"- end-to-end overhead_factor (e2e/stage4) = {probe['overhead_factor']:.3f}")
    lines.append(f"- master-inclusive workers+1 = "
                 f"{n_workers_plus_master(probe['cluster_vcpu'])} "
                 f"(cluster_vcpu {probe['cluster_vcpu']})\n")
    lines.append("## Projection + contingency\n")
    lines.append(f"- PROJECTED (raw, master-inclusive) = {projected_raw:.1f} cluster-h")
    lines.append(f"- contingency factor (from probe blocks_per_min CoV) = "
                 f"{contingency_factor:.3f}")
    lines.append(f"- **PROJECTED (with contingency)** = {projected:.1f} cluster-h "
                 f"(~${credit_usd:,.0f} at ${WORKER_USD_PER_HOUR:.2f}/worker-h, "
                 f"A8 rate — flag for confirmation)\n")
    lines.append("## Per-chromosome egress projection\n")
    lines.append(f"- total summary-LD+AF output = {egress['total_output_gib']:.1f} GiB "
                 f"across {egress['n_bundles']} per-chrom bundles "
                 f"(EGRESS_CAP_GB={egress['egress_cap_gb']}, a CONSERVATIVE project "
                 f"working ceiling per Q5/A2 — confirm the real number on first export)")
    if egress["chromosomes_split"]:
        lines.append(f"- chromosomes split into _a/_b (> {egress['egress_cap_gb']} GB): "
                     f"{sorted(egress['chromosomes_split'])}")
    lines.append(f"- bundles still over cap (indivisible single cells): "
                 f"{egress['n_over_cap']}\n")
    lines.append("## Gate evaluation\n")
    lines.append(f"- BUDGET_CAP_CLUSTER_H = {budget_cap:.1f}")
    lines.append(f"- predicate: PROJECTED * {gate['headroom_multiplier']} "
                 f"({gate['projected_x_headroom']:.1f}) <= BUDGET_CAP "
                 f"({budget_cap:.1f}) -> headroom_ok = {gate['headroom_ok']}")
    lines.append(f"- **DISPOSITION: {gate['disposition']}**\n")
    if gate["disposition"] == "GREEN":
        lines.append("GREEN: the 322-cell production fire is within the 1.3x headroom "
                     "of the approved cap. m3-04 (Wave 4) is UNBLOCKED.\n")
    else:
        lines.append("NOT GREEN: the next lever is the disposition above "
                     "(YELLOW-narrow-radius = cut the buffer band; YELLOW-finer-split "
                     "= lower --max-subregion-span-mb, the likelier post-Q3 lever since "
                     "the buffer is already narrow; RED = no lever room). A re-probe is "
                     "needed before m3-04.\n")
    lines.append("## Scope\n")
    lines.append("The full 322-cell production fire is EXPLICITLY OUT OF SCOPE here and "
                 "stays in Wave 4 (m3-04). This plan ends at the go/no-go decision.\n")
    return "\n".join(lines)


def run_cost_model(*, probe_tsv, preflight_tsv, projection_tsv,
                   budget_cap_cluster_h: float, manifest_tsv=None) -> dict:
    """End-to-end: load -> project -> totals -> contingency -> egress -> gate."""
    probe = load_probe_rates(probe_tsv)
    preflight_df = load_preflight_counts(preflight_tsv)
    projection_df = pd.read_csv(projection_tsv, sep="\t")
    manifest_df = pd.read_csv(manifest_tsv, sep="\t") if manifest_tsv else None

    eur_fac, eur_source = eur_factor(probe)
    projected_df = project_cell_hours(preflight_df, probe, eur_fac)
    totals = three_totals(projected_df, projection_df)
    projected_raw = totals["total_compute_h"]
    projected, contingency_factor = apply_contingency(projected_raw, probe["rate_list"])
    egress = project_egress_bundles(preflight_df)
    gate = evaluate_gate(
        projected, budget_cap_cluster_h,
        lever_room_radius_mb=_max_buffer_mb(preflight_df, manifest_df),
        dominant_class=_dominant_class(projected_df),
    )
    return {
        "probe": probe, "preflight_df": preflight_df, "projection_df": projection_df,
        "manifest_df": manifest_df, "eur_factor": eur_fac, "eur_source": eur_source,
        "projected_df": projected_df, "totals": totals,
        "projected_raw": projected_raw, "projected": projected,
        "contingency_factor": contingency_factor, "egress": egress, "gate": gate,
        "budget_cap": budget_cap_cluster_h,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--probe-tsv", required=True, type=Path)
    p.add_argument("--preflight-tsv", required=True, type=Path)
    p.add_argument("--projection", required=True, type=Path)
    p.add_argument("--manifest", required=False, type=Path, default=None,
                   help="config/ld_regions.tsv (for the narrow-radius lever buffer_bp)")
    p.add_argument("--budget-cap-cluster-h", required=True, type=float)
    p.add_argument("--out-budget-md", required=True, type=Path)
    args = p.parse_args(argv)

    res = run_cost_model(
        probe_tsv=args.probe_tsv, preflight_tsv=args.preflight_tsv,
        projection_tsv=args.projection, budget_cap_cluster_h=args.budget_cap_cluster_h,
        manifest_tsv=args.manifest,
    )
    memo = build_budget_memo(
        totals=res["totals"], contingency_factor=res["contingency_factor"],
        projected_raw=res["projected_raw"], projected=res["projected"],
        gate=res["gate"], egress=res["egress"], eur_fac=res["eur_factor"],
        eur_source=res["eur_source"], probe=res["probe"],
        budget_cap=res["budget_cap"], manifest_df=res["manifest_df"],
    )
    args.out_budget_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_budget_md.write_text(memo)
    print(f"OK: PROJECTED={res['projected']:.1f} cluster-h, "
          f"disposition={res['gate']['disposition']} -> {args.out_budget_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
