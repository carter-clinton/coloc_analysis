"""Plan 09-05 Task 2 — assemble master_table.tsv per RESEARCH §16.

Merges all Wave 3/4 per-cohort + IVW meta + FIQT outputs into the single
canonical replication matrix consumed by Phase 11 manuscript figures.

Schema (high level):
    - signal metadata:    signal_id, signal_class, discovery_trait,
                          discovery_ancestry, region, lead_snp
    - 4 effect-size cols: beta_discovery_raw, beta_discovery_FIQT,
                          beta_replication (per-cohort), beta_meta (meta block)
    - per-cohort × 5:     finngen_r12, gbmi_eur, gbmi_afr, mvp_eur, mvp_afr —
                          each contributes <cohort>_{beta_replication, se_replication,
                          p_replication, eaf_replication, power_posthoc,
                          replicated_bonferroni, replicated_pph4_{0.5,0.7,0.8,0.9},
                          replicated_joint_0.8, ...}
    - meta block:         beta_meta, se_meta, p_meta,
                          meta_replicated_bonferroni, meta_replicated_pph4_0.8,
                          meta_ancestry (I-2)
    - I-3 per-cohort flags: {cohort}_sample_overlap_flag for 6 cohorts
                          (includes bbj for full traceability)
    - low_maf_founder_flag: trait-level flag for Finnish founder panel

Revisions honored:
  - I-2: meta merge uses (signal_id, discovery_ancestry) not signal_id alone
         so signal_id collisions across ancestries do not mis-aggregate.
         Back-compat path: if discovery_ancestry absent from meta, fall back
         to signal_id-only and derive meta_ancestry from discovery_ancestry.
  - I-3: per-cohort sample_overlap_flag columns (not a single gbmi_eur-hardcoded
         column). KNOWN_OVERLAP_PAIRS supports (trait, cohort) and ("*", cohort)
         wildcard keys per RESEARCH §17 pitfall #3.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Union

import pandas as pd

# ---------------------------------------------------------------------------
# Constants (RESEARCH §17)
# ---------------------------------------------------------------------------

# All ancestry-matched replication cohorts + BBJ (for full traceability on
# sample-overlap flagging). BBJ contributes to the cross-ancestry panel,
# not the meta; its overlap flag here is advisory for QC review.
REPLICATION_COHORTS: list[str] = [
    "finngen_r12",
    "gbmi_eur",
    "gbmi_afr",
    "mvp_eur",
    "mvp_afr",
    "bbj",
]

# Subset actually used in per-cohort blocks + meta. BBJ is excluded upstream
# (is_generalization=TRUE in IVW meta rule) per D-05c, so no BBJ block.
PRIMARY_COHORTS: list[str] = [
    "finngen_r12",
    "gbmi_eur",
    "gbmi_afr",
    "mvp_eur",
    "mvp_afr",
]

# I-3 revision: per-cohort (trait, cohort) overlap registry. Trait="*" is a
# wildcard for structural overlap that applies to ALL traits in that cohort.
KNOWN_OVERLAP_PAIRS: dict[tuple[str, str], str] = {
    # Structural: GBMI meta includes FinnGen + UKBB cases by design
    ("*", "gbmi_eur"): (
        "GBMI-EUR includes FinnGen + UKBB cases by design (structural overlap)"
    ),
    ("*", "gbmi_afr"): (
        "GBMI-AFR structural overlap TBD — consult GBMI flagship S2 Table "
        "per cohort admixture"
    ),
    # Trait-specific
    ("hypertension", "gbmi_eur"): (
        "GBMI-EUR includes UKBB; overlaps Evangelou 2018 HTN discovery"
    ),
    ("bmi", "gbmi_eur"): (
        "GBMI lacks BMI; GIANT Yengo substitute overlaps UKBB -> GBMI-EUR "
        "if BMI used"
    ),
    ("stroke", "bbj"): (
        "MEGASTROKE any-stroke may overlap BBJ; BBJ uses ischemic-only (narrower)"
    ),
}

FINNISH_FOUNDER_FLAG_TRAITS: set[str] = {"t2d", "hypertension"}

PER_COHORT_EMPTY_SUFFIXES: list[str] = [
    "beta_replication",
    "se_replication",
    "p_replication",
    "eaf_replication",
    "N",
    "cohort_ancestry",
    "beta_discovery_FIQT",
    "se_FIQT",
    "pph4_replication",
    "replicated_pph4_0.5",
    "replicated_pph4_0.7",
    "replicated_pph4_0.8",
    "replicated_pph4_0.9",
    "bonf_threshold",
    "same_direction",
    "replicated_bonferroni",
    "power_posthoc",
    "replicated_joint_0.8",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def resolve_overlap_flag(trait: str, cohort: str) -> str | None:
    """Return overlap flag text for (trait, cohort), checking trait-specific
    before structural wildcard ('*', cohort)."""
    if trait is None:
        trait = ""
    for key in ((trait, cohort), ("*", cohort)):
        if key in KNOWN_OVERLAP_PAIRS:
            return KNOWN_OVERLAP_PAIRS[key]
    return None


# ---------------------------------------------------------------------------
# Core assembly
# ---------------------------------------------------------------------------
def assemble_master_table(
    manifest_tsv: Union[str, Path],
    fiqt_tsv: Union[str, Path],
    per_cohort_dir: Union[str, Path],
    coloc_dir: Union[str, Path],  # noqa: ARG001 — reserved for future PP.H4 JSON joins
    meta_tsv: Union[str, Path],
    output_tsv: Union[str, Path],
) -> pd.DataFrame:
    """Build the master replication table.

    See module docstring for output schema + revision rationale (I-2, I-3).
    """
    manifest_tsv = Path(manifest_tsv)
    fiqt_tsv = Path(fiqt_tsv)
    per_cohort_dir = Path(per_cohort_dir)
    meta_tsv = Path(meta_tsv)
    output_tsv = Path(output_tsv)

    manifest = pd.read_csv(manifest_tsv, sep="\t")
    fiqt = pd.read_csv(fiqt_tsv, sep="\t")

    # --- Signal metadata spine (one row per signal_id) --------------------
    meta_cols_keep = [
        c for c in (
            "signal_id",
            "signal_class",
            "discovery_trait",
            "discovery_ancestry",
            "region",
        ) if c in manifest.columns
    ]
    signals = (
        manifest[meta_cols_keep]
        .drop_duplicates("signal_id")
        .copy()
        .reset_index(drop=True)
    )

    # --- FIQT merge (rsid -> lead_snp rename, beta -> beta_discovery_raw) --
    fiqt_renamed = fiqt.rename(columns={
        "rsid": "lead_snp",
        "beta": "beta_discovery_raw",
        "se": "se_discovery_raw",
        "beta_FIQT": "beta_discovery_FIQT",
        "se_FIQT": "se_discovery_FIQT",
    })
    # Only carry columns we actually need (avoid polluting with `n` etc.)
    keep = [c for c in (
        "signal_id", "lead_snp",
        "beta_discovery_raw", "se_discovery_raw",
        "beta_discovery_FIQT", "se_discovery_FIQT",
    ) if c in fiqt_renamed.columns]
    signals = signals.merge(fiqt_renamed[keep], on="signal_id", how="left")

    # p_discovery_raw is not emitted by FIQT (winnerscurse takes z-stats);
    # fill with None placeholder so schema contract holds. Producers that
    # care about p-value can merge a separate discovery-pvalue column.
    signals["p_discovery_raw"] = None

    # --- Per-cohort blocks ------------------------------------------------
    for cohort in PRIMARY_COHORTS:
        pc_file = per_cohort_dir / f"{cohort}.tsv"
        if not pc_file.exists() or pc_file.stat().st_size == 0:
            for suffix in PER_COHORT_EMPTY_SUFFIXES:
                signals[f"{cohort}_{suffix}"] = None
            continue

        pc = pd.read_csv(pc_file, sep="\t")
        # Drop the raw `cohort` column so the renamer doesn't produce
        # duplicate cohort-prefixed cohort columns.
        if "cohort" in pc.columns:
            pc = pc.drop(columns=["cohort"])
        # Rename all columns except signal_id with the cohort prefix.
        pc_renamed = pc.rename(columns={
            c: f"{cohort}_{c}" for c in pc.columns if c != "signal_id"
        })
        signals = signals.merge(pc_renamed, on="signal_id", how="left")

    # --- Meta block (I-2 revision) ---------------------------------------
    if meta_tsv.exists() and meta_tsv.stat().st_size > 0:
        meta = pd.read_csv(meta_tsv, sep="\t")
        # Drop the raw `cohort` column from IVW meta to avoid collisions
        if "cohort" in meta.columns:
            meta = meta.drop(columns=["cohort"])
        if (
            "discovery_ancestry" in meta.columns
            and "discovery_ancestry" in signals.columns
        ):
            signals = signals.merge(
                meta, on=["signal_id", "discovery_ancestry"], how="left"
            )
        elif (
            "cohort_ancestry" in meta.columns
            and "discovery_ancestry" in signals.columns
        ):
            # IVW meta emits cohort_ancestry; align to discovery_ancestry.
            meta_aligned = meta.rename(
                columns={"cohort_ancestry": "discovery_ancestry"}
            )
            # Drop meta_ancestry from right side if already present so we
            # preserve IVW's explicit meta_ancestry column via merge.
            signals = signals.merge(
                meta_aligned, on=["signal_id", "discovery_ancestry"],
                how="left",
            )
        else:
            # Back-compat: meta table without ancestry — merge on signal_id alone.
            signals = signals.merge(meta, on="signal_id", how="left")

        # I-2: ensure meta_ancestry always present
        if "meta_ancestry" not in signals.columns:
            if "discovery_ancestry" in signals.columns:
                signals["meta_ancestry"] = signals["discovery_ancestry"]
            else:
                signals["meta_ancestry"] = None
    else:
        # Emit empty meta block so schema is stable
        for col in ("beta_meta", "se_meta", "p_meta",
                    "meta_replicated_bonferroni", "meta_replicated_pph4_0.8"):
            signals[col] = None
        signals["meta_ancestry"] = signals.get(
            "discovery_ancestry", pd.Series([None] * len(signals))
        )

    # --- I-3 per-cohort sample_overlap_flag columns ----------------------
    for cohort in REPLICATION_COHORTS:
        col = f"{cohort}_sample_overlap_flag"
        signals[col] = signals.apply(
            lambda r, c=cohort: resolve_overlap_flag(
                r.get("discovery_trait"), c
            ),
            axis=1,
        )

    # --- Trait-level flags -----------------------------------------------
    if "discovery_trait" in signals.columns:
        signals["low_maf_founder_flag"] = signals["discovery_trait"].isin(
            FINNISH_FOUNDER_FLAG_TRAITS
        )
    else:
        signals["low_maf_founder_flag"] = False

    signals["notes"] = None

    # --- Emit -------------------------------------------------------------
    output_tsv.parent.mkdir(parents=True, exist_ok=True)
    signals.to_csv(output_tsv, sep="\t", index=False)
    return signals


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--manifest", required=True)
    p.add_argument("--fiqt", required=True)
    p.add_argument("--per-cohort-dir", required=True)
    p.add_argument("--coloc-dir", required=True)
    p.add_argument("--meta", required=True)
    p.add_argument("--out", required=True)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    a = _parse_args(argv)
    assemble_master_table(
        manifest_tsv=a.manifest, fiqt_tsv=a.fiqt,
        per_cohort_dir=a.per_cohort_dir, coloc_dir=a.coloc_dir,
        meta_tsv=a.meta, output_tsv=a.out,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
