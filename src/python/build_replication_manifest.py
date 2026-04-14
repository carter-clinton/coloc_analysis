#!/usr/bin/env python3
"""Build the Phase 9 replication manifest — signal × cohort × ancestry crossmap.

Consumes:
  - Phase 1 credible-set summary TSV (columns: trait, ancestry, region, lead_snp)
  - Phase 2 tier_assignments.tsv (columns: signal_id, gwas_trait, gwas_ancestry,
    region, gene_id, tissue, qtl_source, gwas_pph4, qtl_pph4, tier)
  - config/replication_cohorts.yaml (panels + cohort trait availability)

Emits:
  - data/processed/replication/manifest.tsv

Each manifest row describes one (signal × cohort) replication target. Row
schema (Plan 09-03):

    signal_id                — unique {trait}_{ancestry}_{region}_{class}
    signal_class             — credible_set_SNP | tier_A_triple | tier_B_triple
    discovery_trait
    discovery_ancestry       — EUR or AFR
    region                   — chr:start-end GRCh37
    lead_snp (credible_set_SNP rows only)
    gene_id / tissue / qtl_source (triple rows only)
    cohort                   — finngen_r12 | gbmi_eur | gbmi_afr | mvp_eur |
                               mvp_afr | bbj
    cohort_ancestry          — EUR / AFR / EAS
    is_generalization        — True for BBJ cross-ancestry rows (Tier A+B only)
    discovery_fit_path       — results/fine_mapping/*.fit.rds
    replication_sumstats_path — data/processed/replication/harmonized_grch37/...
    ld_panel                 — ukbb_ld | hgdp_1kg_afr | thousand_g_eas

Policy enforcement:
  - D-02b  Tier C signals EXCLUDED from manifest (only Tier A+B kept)
  - D-05   Ancestry-matched routing via config['panels']['primary_{anc}']
  - D-05c  BBJ appears ONLY for Tier A+B triples (signal_scope: tier_ab_only)
  - D-08   LD panel routed per cohort_ancestry via config['ld_panels']
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

PHASE1_FIT_GLOB = "results/fine_mapping/{trait}_{ancestry}_{region}.fit.rds"
HARMONIZED_BASE = "data/processed/replication/harmonized_grch37"


def _resolve_cohort_cfg_name(cohort_name: str) -> str:
    """Map a manifest cohort name to the key used in config['cohorts']."""
    if cohort_name == "finngen_r12":
        return "finngen_r12"
    if cohort_name == "bbj":
        return "bbj_hum0197_v3"
    if cohort_name.startswith("mvp"):
        return "mvp_phs001672"
    if cohort_name.startswith("gbmi"):
        return "gbmi"
    raise ValueError(f"Unknown cohort name: {cohort_name}")


def _cohort_trait_available(cohort_cfg: dict, trait: str, ancestry_key: str | None = None) -> bool:
    """Return True iff trait is available in this cohort.

    For MVP (which carries per-ancestry strata under each trait), `ancestry_key`
    is the stratum key (e.g., 'eur', 'afr', 'eas'). The trait-level status flag
    (e.g., stroke.status == NOT_RELEASED_AS_OF_2026-04) still takes precedence.

    For other cohorts, `ancestry_key` is unused.
    """
    traits = cohort_cfg.get("traits", {})
    t = traits.get(trait)
    if t is None:
        return False
    if isinstance(t, dict):
        status = t.get("status")
        if status in ("EXCLUDED", "NOT_RELEASED_AS_OF_2026-04", "PHASE2_FOLLOWUP"):
            return False
        # MVP stratum-level check: if ancestry_key provided and trait has
        # per-ancestry subdicts, the specific stratum must exist.
        if ancestry_key is not None and ancestry_key in t:
            return True
        if ancestry_key is not None:
            # Stratum missing for this ancestry -> unavailable.
            # BUT: if the trait has no nested ancestry strata (flat config like
            # finngen/bbj with {endpoint: X, case_n: Y}), ancestry_key lookup
            # doesn't apply. Detect by checking if any value is a dict.
            has_strata = any(isinstance(v, dict) for v in t.values())
            if has_strata:
                return False
        return True
    return False


def _resolve_rep_path(
    cohort_name: str, trait: str, ancestry_key: str, cfg: dict
) -> str:
    """Resolve expected path to the Wave-2 harmonized sumstats for this
    (cohort, trait, ancestry) triple.

    Matches the canonical Wave-2 output layout at
    `data/processed/replication/harmonized_grch37/{cohort}/{file}.tsv.gz`.
    """
    if cohort_name == "finngen_r12":
        trait_meta = cfg["cohorts"]["finngen_r12"]["traits"].get(trait)
        if not isinstance(trait_meta, dict):
            return f"{HARMONIZED_BASE}/finngen_r12/MISSING_{trait}.tsv.gz"
        endpoint = trait_meta.get("endpoint", "UNKNOWN")
        return f"{HARMONIZED_BASE}/finngen_r12/{trait}_{endpoint}.tsv.gz"
    if cohort_name.startswith("gbmi_"):
        anc = cohort_name.split("_", 1)[1]  # 'eur' / 'afr' / 'eas' / ...
        return f"{HARMONIZED_BASE}/gbmi/{trait}_{anc}.tsv.gz"
    if cohort_name.startswith("mvp_"):
        anc = cohort_name.split("_", 1)[1]
        trait_meta = cfg["cohorts"]["mvp_phs001672"]["traits"].get(trait, {})
        stratum = trait_meta.get(anc, {}) if isinstance(trait_meta, dict) else {}
        pha = stratum.get("pha", f"MISSING_{trait}_{anc}")
        return f"{HARMONIZED_BASE}/mvp/{pha}.tsv.gz"
    if cohort_name == "bbj":
        trait_meta = cfg["cohorts"]["bbj_hum0197_v3"]["traits"].get(trait, {})
        code = trait_meta.get("trait_code", f"MISSING_{trait}") if isinstance(trait_meta, dict) else f"MISSING_{trait}"
        return f"{HARMONIZED_BASE}/bbj/{trait}_{code}.tsv.gz"
    raise ValueError(f"Unknown cohort: {cohort_name}")


def _ld_panel_for(cohort_name: str, cohort_ancestry: str, cfg: dict) -> str:
    """Route per-cohort LD panel per D-08.

    Routing is by cohort_ancestry (the ancestry of the LD in the replication
    cohort), NOT the discovery ancestry. For BBJ (EAS) this is always EAS.
    """
    panels = cfg["ld_panels"]
    if cohort_ancestry == "EUR":
        return panels["EUR"]
    if cohort_ancestry == "AFR":
        return panels["AFR"]
    if cohort_ancestry == "EAS":
        return panels["EAS"]
    raise ValueError(f"Unknown cohort ancestry: {cohort_ancestry}")


def _cohort_ancestry(cohort_name: str) -> str:
    """Return the canonical ancestry code for the replication cohort."""
    if cohort_name == "finngen_r12":
        return "EUR"
    if cohort_name == "bbj":
        return "EAS"
    if cohort_name.endswith("_eur"):
        return "EUR"
    if cohort_name.endswith("_afr"):
        return "AFR"
    if cohort_name.endswith("_eas"):
        return "EAS"
    raise ValueError(f"Cannot infer ancestry for cohort: {cohort_name}")


def _ancestry_key_for_cohort(cohort_name: str) -> str | None:
    """Return the stratum key used to index the MVP/GBMI per-ancestry dict.

    Returns None for flat-config cohorts (finngen, bbj).
    """
    if "_" not in cohort_name:
        return None  # finngen_r12 / bbj treated as flat
    if cohort_name in ("finngen_r12",):
        return None
    # mvp_eur / gbmi_afr / ... -> last segment
    return cohort_name.split("_", 1)[1]


def build_manifest(
    credset_tsv: Path,
    tier_assignments_tsv: Path,
    config_yaml: Path,
    out_tsv: Path,
) -> pd.DataFrame:
    """Build the Phase 9 replication manifest as a DataFrame and write it.

    Missing / empty discovery inputs are allowed: returned DataFrame will be
    empty. This is the expected state before Phase 1/2 have produced their
    own outputs.
    """
    with open(config_yaml) as f:
        cfg = yaml.safe_load(f)
    panels = cfg.get("panels", {})

    # Read discovery inputs, tolerating missing files and empty frames.
    credset = pd.DataFrame()
    if credset_tsv.exists() and credset_tsv.stat().st_size > 0:
        try:
            credset = pd.read_csv(credset_tsv, sep="\t")
        except pd.errors.EmptyDataError:
            credset = pd.DataFrame()
    tiers = pd.DataFrame()
    if tier_assignments_tsv.exists() and tier_assignments_tsv.stat().st_size > 0:
        try:
            tiers = pd.read_csv(tier_assignments_tsv, sep="\t")
        except pd.errors.EmptyDataError:
            tiers = pd.DataFrame()

    # D-02b: Tier C excluded
    if not tiers.empty and "tier" in tiers.columns:
        tier_ab = tiers[tiers["tier"].isin(["Tier A", "Tier B"])].copy()
    else:
        tier_ab = pd.DataFrame()

    rows: list[dict] = []

    # ----------------------------------------------------------------
    # Layer 1: Phase 1 credible-set SNPs (primary panel only; no BBJ)
    # ----------------------------------------------------------------
    for _, r in credset.iterrows():
        disc_anc = str(r["ancestry"]).upper()
        panel_key = f"primary_{disc_anc.lower()}"
        if panel_key not in panels:
            continue
        target_cohorts = list(panels[panel_key].get("cohorts", []))
        for cohort_name in target_cohorts:
            cohort_cfg_name = _resolve_cohort_cfg_name(cohort_name)
            cohort_cfg = cfg["cohorts"][cohort_cfg_name]
            anc_key = _ancestry_key_for_cohort(cohort_name)
            if not _cohort_trait_available(cohort_cfg, r["trait"], anc_key):
                continue
            cohort_anc = _cohort_ancestry(cohort_name)
            rows.append(
                {
                    "signal_id": f"{r['trait']}_{disc_anc}_{r['region']}_{r['lead_snp']}",
                    "signal_class": "credible_set_SNP",
                    "discovery_trait": r["trait"],
                    "discovery_ancestry": disc_anc,
                    "region": r["region"],
                    "lead_snp": r["lead_snp"],
                    "gene_id": "",
                    "tissue": "",
                    "qtl_source": "",
                    "cohort": cohort_name,
                    "cohort_ancestry": cohort_anc,
                    "is_generalization": False,
                    "discovery_fit_path": PHASE1_FIT_GLOB.format(
                        trait=r["trait"], ancestry=disc_anc, region=r["region"]
                    ),
                    "replication_sumstats_path": _resolve_rep_path(
                        cohort_name, r["trait"], anc_key or "", cfg
                    ),
                    "ld_panel": _ld_panel_for(cohort_name, cohort_anc, cfg),
                }
            )

    # ----------------------------------------------------------------
    # Layer 2: Phase 2 Tier A+B triples (primary panel + BBJ generalization)
    # ----------------------------------------------------------------
    for _, r in tier_ab.iterrows():
        disc_anc = str(r["gwas_ancestry"]).upper()
        panel_key = f"primary_{disc_anc.lower()}"
        target_cohorts = list(panels.get(panel_key, {}).get("cohorts", []))
        # D-05c: Add BBJ for EUR Tier A+B triples only (generalization layer).
        # The config documents this via panels.generalization_eas with
        # signal_scope: tier_ab_only and discovery_ancestry: EUR.
        gen_panel = panels.get("generalization_eas", {})
        gen_scope = gen_panel.get("signal_scope", "")
        if (
            disc_anc == gen_panel.get("discovery_ancestry", "EUR").upper()
            and gen_scope == "tier_ab_only"
        ):
            for c in gen_panel.get("cohorts", []):
                if c not in target_cohorts:
                    target_cohorts.append(c)

        for cohort_name in target_cohorts:
            cohort_cfg_name = _resolve_cohort_cfg_name(cohort_name)
            cohort_cfg = cfg["cohorts"][cohort_cfg_name]
            anc_key = _ancestry_key_for_cohort(cohort_name)
            if not _cohort_trait_available(cohort_cfg, r["gwas_trait"], anc_key):
                continue
            cohort_anc = _cohort_ancestry(cohort_name)
            is_gen = cohort_name == "bbj"
            tier_letter = str(r["tier"]).strip()[-1]  # 'A' or 'B'
            rows.append(
                {
                    "signal_id": (
                        f"{r['gwas_trait']}_{disc_anc}_{r['region']}_"
                        f"tier{tier_letter}_{r['gene_id']}"
                    ),
                    "signal_class": f"tier_{tier_letter}_triple",
                    "discovery_trait": r["gwas_trait"],
                    "discovery_ancestry": disc_anc,
                    "region": r["region"],
                    "lead_snp": "",
                    "gene_id": r["gene_id"],
                    "tissue": r.get("tissue", ""),
                    "qtl_source": r.get("qtl_source", ""),
                    "cohort": cohort_name,
                    "cohort_ancestry": cohort_anc,
                    "is_generalization": is_gen,
                    "discovery_fit_path": PHASE1_FIT_GLOB.format(
                        trait=r["gwas_trait"], ancestry=disc_anc, region=r["region"]
                    ),
                    "replication_sumstats_path": _resolve_rep_path(
                        cohort_name, r["gwas_trait"], anc_key or "", cfg
                    ),
                    "ld_panel": _ld_panel_for(cohort_name, cohort_anc, cfg),
                }
            )

    df = pd.DataFrame(rows)
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_tsv, sep="\t", index=False)
    return df


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--credset", required=True, help="Phase 1 credible_set_summary.tsv")
    p.add_argument("--tiers", required=True, help="Phase 2 tier_assignments.tsv")
    p.add_argument("--config", required=True, help="config/replication_cohorts.yaml")
    p.add_argument("--out", required=True, help="Output manifest TSV path")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    a = _parse_args(argv)
    df = build_manifest(
        Path(a.credset), Path(a.tiers), Path(a.config), Path(a.out)
    )
    if df.empty:
        print("manifest rows: 0 (no credible-set SNPs or Tier A+B triples on disk yet)")
    else:
        counts = df["signal_class"].value_counts().to_dict()
        print(f"manifest rows: {len(df)}; classes: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
