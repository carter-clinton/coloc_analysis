"""Multi-signal SuSiE colocalization rule (REQ-2 success criterion #4).

Replaces the legacy run_coloc_pair rule in multitrait.smk (single-variant
ABF backend). Depends on .fit.rds outputs from finemap.smk:run_finemap
(Phase 1 Wave 1). Uses the legacy-compat JSON schema so downstream
augment_coloc_summary.py, build_coloc_h4_reports.py, and
build_coloc_top_hits_table.py continue working.

Must be included AFTER finemap.smk and multitrait.smk in the top-level
Snakefile so finemap_output() and MULTITRAIT_DIR are in scope.
"""

import os
import sys

import pandas as pd

PYTHON_BIN = sys.executable
COLOC_SUSIE_DIR = os.path.join(MULTITRAIT_DIR, "coloc_susie")


# Region-safe pair_id constraint: alphanumeric + underscore + dot + hyphen.
# Manifest pair_ids are produced deterministically by create_coloc_manifest.py
# from trusted upstream inputs (T-1-03 mitigation from threat register).
wildcard_constraints:
    pair_id=r"[A-Za-z0-9_.\-]+",


def _coloc_manifest_row(pair_id):
    """Resolve (trait_a, trait_b, ancestry, region) from the coloc_manifest TSV.

    The manifest is produced upstream by multitrait.smk:build_coloc_manifest.
    Row schema includes: pair_id, trait_a, trait_b, ancestry, region.
    Returns a dict, or None if the manifest does not exist or the pair_id
    is not found (Snakemake will retry once the manifest exists).
    """
    manifest_path = os.path.join(MULTITRAIT_DIR, "coloc_manifest.tsv")
    if not os.path.exists(manifest_path):
        return None
    df = pd.read_csv(manifest_path, sep="\t", dtype=str)
    if "pair_id" not in df.columns:
        return None
    row = df[df["pair_id"] == pair_id]
    if len(row) != 1:
        return None
    return row.iloc[0].to_dict()


def _fit_rds_for(trait, ancestry, region_safe):
    """Return the .fit.rds path produced by run_finemap for (trait, ancestry, region).

    Uses the method name 'susie' (the only method that persists a .fit.rds).
    Convention: the fit path is derived from the JSON output path by
    replacing '.json' with '.fit.rds' -- matches finemap.smk:run_finemap output.
    """
    return finemap_output("susie", trait, ancestry, region_safe).replace(
        ".json", ".fit.rds"
    )


def _coloc_susie_fit_input(which, wildcards):
    """Input function: resolve fit_a/fit_b paths via the coloc_manifest.

    If the manifest is not yet available the DAG check would fail -- but the
    run_coloc_susie rule depends on the manifest as an explicit input, so
    Snakemake will materialize it first. When the manifest is missing during
    dry-run of a target not reachable from build_coloc_manifest, we return
    a sentinel path that will clearly error rather than silently succeed.
    """
    row = _coloc_manifest_row(wildcards.pair_id)
    if row is None:
        # Dry-run placeholder: Snakemake will re-evaluate once the manifest
        # exists. Return a descriptive path that will error loudly if used.
        return os.path.join(
            MULTITRAIT_DIR,
            "coloc_susie",
            f"_MISSING_MANIFEST_{wildcards.pair_id}_{which}.fit.rds",
        )
    trait_key = "trait_a" if which == "a" else "trait_b"
    return _fit_rds_for(row[trait_key], row["ancestry"], row["region"])


rule run_coloc_susie:
    input:
        manifest=os.path.join(MULTITRAIT_DIR, "coloc_manifest.tsv"),
        policy="config/susie_policy.yaml",
        fit_a=lambda wc: _coloc_susie_fit_input("a", wc),
        fit_b=lambda wc: _coloc_susie_fit_input("b", wc),
        script="src/snakemake/scripts/run_coloc_susie.R",
    output:
        json=os.path.join(COLOC_SUSIE_DIR, "{pair_id}.json"),
    conda:
        "envs/r_coloc.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        mkdir -p $(dirname {output.json})
        Rscript {input.script} \
            --fit-a {input.fit_a} \
            --fit-b {input.fit_b} \
            --policy {input.policy} \
            --pair-id {wildcards.pair_id} \
            --manifest {input.manifest} \
            --output {output.json}
        """
