"""Fine-mapping rules (SuSiE and related methods).

Refactored from src/legacy/region_analysis/workflow/rules/finemap.smk.
All paths parameterized via config (D-09, D-10).
Conda directives point to envs/ relative to project root (D-25).
Removed hardcoded rscript_bin -- conda env resolves Rscript.

Modified 2026-04-30 (m3-W3-T2): ``run_finemap.input.ld_matrix`` is now routed
through ``src/python/ld_panel.py::resolve_ld_path()`` per RESEARCH Q7
``Integration point``. The original hardcoded path
``{config['paths']['ld_reference']}/{ancestry}/{region}.rds`` is retained
below as a comment for audit. ``resolve_ld_path()`` walks the
``config['ld_panel'][ancestry]`` fallback chain (AFR_aou -> AFR_hgdp ->
AFR_1kg for AFR; EUR_aou -> EUR_ukbb -> EUR_1kg for EUR; per RESEARCH Q7)
and returns the first ``.rds`` path that exists. The legacy hardcoded
expression maps to the AFR_1kg / EUR_1kg tail of the chain via the
``{region_safe}`` template variable, so AFR/EUR regions whose AoU panels
have not yet landed continue to resolve to the existing 1000G panels --
zero behavior change for Track A finalization while M3 panels stage in.

Modified 2026-08-03 (m3-04b Task 2): ``run_finemap.input.sumstats`` AND
``run_finemap.input.variants`` are now routed through the EXCLUDE-IN-LOCKSTEP
seam (``src/python/occlusion_lockstep_cli.py``), discharging the consume-wiring
deferral ``src/python/drop_occluded_from_sumstats.py:49-56`` disclosed. Both
original expressions are retained below as ``# OLD:`` comments for audit,
matching the house style already used for ``ld_matrix``.

BOTH inputs move, not one. ``ld_reference.smk::collect_region_variants`` pools
every harmonized file ancestry-agnostically into
``{ld_reference}/variants/{region}.tsv``, so repointing only the sumstats would
let the occluded coordinate back in through ``input.variants`` and every
downstream fine-map would inherit the panel<->sumstats mismatch anyway.

The seam is ANCESTRY-GATED (``config.occlusion_lockstep.ancestries``, AFR only).
For every other ancestry -- and when the block is disabled or absent -- the
resolvers return the LEGACY strings character-for-character, so Track-A / EUR
numerics cannot move. ``params.region_id`` and ``input.ld_matrix`` are
deliberately UNTOUCHED here: the LD-path crosswalk is m3-04c's change, placed in
a later wave so the two ``finemap.smk`` edits never collide.
"""

import os
import sys
from pathlib import Path

# m3-W3-T2: import the M3 LD-panel resolver so run_finemap.input.ld_matrix
# can route LD path resolution through the unified ld_panel: chain in
# config/pipeline.yaml. ``workflow.basedir`` resolves to the project root
# under standard Snakemake invocation; we walk up if ``src/python`` is not
# directly under it (defensive for downstream Snakefile re-anchoring).
try:
    _FINEMAP_BASE = Path(workflow.basedir)  # type: ignore[name-defined]
except NameError:
    _FINEMAP_BASE = Path(os.getcwd())

_SRC_PYTHON = str(_FINEMAP_BASE / "src" / "python")
if _SRC_PYTHON not in sys.path:
    sys.path.insert(0, _SRC_PYTHON)

from ld_panel import resolve_ld_path  # noqa: E402 -- intentional after sys.path mutation

# m3-04b Task 2: the exclude-in-lockstep consume seam. Both resolvers return the
# LEGACY path string verbatim for any ancestry the seam does not cover, so this
# import cannot move a frozen number by itself.
from occlusion_lockstep_cli import (  # noqa: E402 -- same sys.path rationale
    lockstep_sumstats_path,
    lockstep_variants_path,
)

FINEMAP_DIR = config["finemap"]["output_dir"]
FINEMAP_METHODS = config["finemap"]["methods"]
PYTHON_BIN = sys.executable


def finemap_output(path_method, trait, ancestry, region):
    return os.path.join(FINEMAP_DIR, path_method, f"{trait}.{ancestry}.{region}.json")


rule build_finemap_manifest:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"],
    output:
        manifest=FINEMAP_MANIFEST,
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    params:
        methods=",".join(FINEMAP_METHODS),
    shell:
        r"""
        PYTHONPATH=src/legacy/region_analysis:${{PYTHONPATH:-}} \
        {PYTHON_BIN} src/legacy/region_analysis/scripts/create_finemap_tasks.py \
            --harmonized {input.harmonized} \
            --regions {input.regions} \
            --methods {params.methods} \
            --output {output.manifest}
        """


# ---------------------------------------------------------------------------
# m3-02e Move 3: estimate_s z-vs-LD consistency guard (Zou 2022).
# run_susie_rss.R now serializes a per-region estimate_s_rss scalar
# (d3b_ld_z_consistency_s) + an ld_source_mismatch_flag. The two NEW LD sources
# this wave introduces -- the native-plink AFR LD (built with --keep-allele-order)
# and the public-EUR panel (hg19->hg38 liftover) -- are the ones most exposed to
# an allele-flip / encoding mismatch between the LD source and the GWAS z-scores,
# the exact failure estimate_s catches. The run_finemap rule captures that
# per-region s-estimate to a log artifact so a z-vs-LD mismatch is flagged before
# it silently corrupts fine-mapping.
#
# m3-02e (B-1) LD-BUILD BOUNDARY: the M3 LD-build is COMPLETE within m3-02e --
# AFR LD = the ~276 native-plink per-ancestry windows (Task 4 in-perimeter fire)
# + EUR LD = the public UKBB 337k panel (Task 2, $0). The Hail BlockMatrix LD
# path is RETIRED. m3-04-W4-production-and-egress-PLAN.md is the STALE 322-cell
# HAIL LD production fire (322 = pre-m3-02d 161 union regions x 2 ancestries;
# 276 = the post-m3-02d per-ancestry AFR window count).
#
# THE REPLAN LANDED (2026-08-03). m3-04-W4 is superseded by m3-04b (this file's
# consume seam + the genome-wide occlusion catalog) and m3-04c (panel
# reachability: the curated<->M2 crosswalk, the stale ingest/convert rules, the
# egress grouping, the Check-2 redefinition and the in-perimeter fire). Nothing
# rebuilds LD via Hail; m3-02e's AFR-native .npz + the public EUR .rds are
# consumed as-is. The DEFERRED consume seam named in
# ``src/python/drop_occluded_from_sumstats.py:49-56`` is WIRED HERE, on
# ``input.sumstats`` and ``input.variants`` together. The downstream coloc/SuSiE
# fine-mapping fire is a separate M4 concern, unaffected.
# ---------------------------------------------------------------------------
rule run_finemap:
    input:
        # m3-04b Task 2: route BOTH consume inputs through the ancestry-gated
        # exclude-in-lockstep seam (osf.io/az52u, file trsx5). For any ancestry
        # outside config.occlusion_lockstep.ancestries -- and when the block is
        # disabled or absent -- these resolvers return the ORIGINAL strings
        # character-for-character, so Track-A / EUR numerics cannot move.
        # OLD: sumstats=lambda wildcards: os.path.join(
        #          HARMONIZED_DIR,
        #          f"{wildcards.trait}.{wildcards.ancestry}.tsv.bgz",
        #      ),
        # OLD: variants=lambda wildcards: os.path.join(
        #          config["paths"]["ld_reference"],
        #          "variants",
        #          f"{wildcards.region}.tsv",
        #      ),
        sumstats=lambda wildcards: lockstep_sumstats_path(
            wildcards.trait, wildcards.ancestry, config, HARMONIZED_DIR
        ),
        variants=lambda wildcards: lockstep_variants_path(
            wildcards.region,
            wildcards.ancestry,
            config,
            config["paths"]["ld_reference"],
        ),
        # m3-W3-T2: route LD path through ld_panel: resolver (RESEARCH Q7).
        # Original (pre-M3) expression for audit -- this hardcoded the
        # legacy {ancestry}/{region_safe}.rds path; the resolver subsumes
        # it as the tail of the AFR/EUR chains in config/pipeline.yaml.
        # OLD: ld_matrix=lambda w: os.path.join(
        #          config["paths"]["ld_reference"],
        #          w.ancestry,
        #          f"{w.region}.rds",
        #      ),
        # m3-W3-T2 + CR-001 fix (2026-05-01): wildcards.region is the
        # filesystem-safe slug (e.g., FTO_16q12), but the AoU chain head in
        # config/pipeline.yaml uses {region_id} (e.g., m2_region_00067).
        # Translate via REGION_SAFE_TO_ID and pass BOTH placeholders so the
        # resolver substitutes them independently. Without this, the AoU
        # panel path (which uses {region_id}) silently falls through to the
        # 1kg/HGDP/UKBB fallback (which use {region_safe}).
        ld_matrix=lambda wildcards: str(
            resolve_ld_path(
                region_id=REGION_SAFE_TO_ID[wildcards.region],
                ancestry=wildcards.ancestry,
                config=config,
                region_safe=wildcards.region,
            )
        ),
        manifest=FINEMAP_MANIFEST,
        # ta-sh2b3 W0 Pitfall 2 mitigation (RESEARCH.md L351 + Wave 0 Task 4):
        # Read policy from config so per-L overlays (config/pipeline_lsweep_L{15,20,30}_overlay.yaml)
        # propagate into the rule's static input declaration. Default
        # preserves existing behavior (config/susie_policy.yaml = L=10 baseline).
        # Without this, --configfile config/pipeline_lsweep_L20_overlay.yaml
        # would set config["finemap"]["policy"] but the rule input would
        # still be the hardcoded path, leading to L_used=10 in JSON output.
        policy=config.get("finemap", {}).get("policy", "config/susie_policy.yaml"),
        script_dep="src/legacy/region_analysis/scripts/run_susie_rss.R",
    output:
        json=finemap_output("{method}", "{trait}", "{ancestry}", "{region}"),
        fit=finemap_output("{method}", "{trait}", "{ancestry}", "{region}").replace(".json", ".fit.rds"),
    log:
        # m3-02e Move 3: per-region estimate_s (z-vs-LD consistency) capture.
        ld_z_consistency=finemap_output(
            "{method}", "{trait}", "{ancestry}", "{region}"
        ).replace(".json", ".estimate_s.log"),
    conda:
        "envs/r_coloc.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    params:
        regions_csv=config["paths"]["regions_curated"],
        ld_dir=config["finemap"]["ld_reference_dir"],
        region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],
        credible_set=config["finemap"].get("credible_set", 0.95),
        # susie_credible_set_yield RECOVERY_PLAN Stage 2 (2026-04-21): raise
        # the sumstats-side variant cap from the run_susie_rss.R hard default
        # (6000) to a value that admits all 11 curated EUR autosomal regions
        # at 1000G HM3 density (max = PYHIN1_1q23 at 15,236 HM3 variants).
        # Bumping to 16000 keeps the pre-skip path closed for regions where
        # we now have real LD, and leaves the path open for HLA_6p21 (69k
        # variants, LD from UKBB-LD tiled panel on a separate branch).
        susie_max_variants=config.get("finemap", {}).get(
            "susie_max_variants", 16000
        ),
    shell:
        r"""
        export SUSIE_MAX_VARIANTS={params.susie_max_variants}
        Rscript src/legacy/region_analysis/scripts/run_susie_rss.R \
          --sumstats {input.sumstats} \
          --trait {wildcards.trait} \
          --ancestry {wildcards.ancestry} \
          --method {wildcards.method} \
          --region {params.region_id} \
          --regions-csv {params.regions_csv} \
          --ld-dir {params.ld_dir} \
          --variant-list {input.variants} \
          --credible-set {params.credible_set} \
          --policy {input.policy} \
          --output {output.json}
        # m3-02e Move 3: surface the per-region estimate_s z-vs-LD consistency
        # scalar (Zou 2022) to a log artifact. No f-string braces here -- only
        # Snakemake's intended {{}} placeholders -- so the rule shell stays valid.
        {PYTHON_BIN} -c "import json,sys; d=json.load(open(sys.argv[1])); print('region', sys.argv[2], 'ancestry', sys.argv[3], 'ld_z_consistency_s', d.get('d3b_ld_z_consistency_s'), 'ld_source_mismatch_flag', d.get('ld_source_mismatch_flag'))" {output.json} {wildcards.region} {wildcards.ancestry} > {log.ld_z_consistency} || true
        """


rule summarize_finemap_results:
    input:
        FINEMAP_OUTPUTS,
    output:
        summary=FINEMAP_SUMMARY,
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    script:
        "../../legacy/region_analysis/scripts/summarize_finemap_results.py"


rule filter_finemap_summary:
    input:
        summary=FINEMAP_SUMMARY,
    output:
        augmented=os.path.join(FINEMAP_DIR, "finemap_summary_augmented.tsv"),
        tier1=os.path.join(FINEMAP_DIR, "finemap_tier1_high_conf.tsv"),
        tier2=os.path.join(FINEMAP_DIR, "finemap_tier2_relaxed.tsv"),
        tier3=os.path.join(FINEMAP_DIR, "finemap_tier3_coloc.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/filter_finemap_summary.py \
            --summary {input.summary} \
            --augment-out {output.augmented} \
            --tier1-out {output.tier1} \
            --tier2-out {output.tier2} \
            --tier3-out {output.tier3}
        """
