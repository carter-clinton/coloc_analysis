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

# 260805-23d Task 1 (m3-04c blast radius, BLOCKER-B): the ANCESTRY ALLOW-LIST for
# the declared-LD read path. Pure stdlib, no I/O -- importing it cannot change a
# resolved path by itself. OFF the allow-list both helpers reproduce 3f431ab's
# behaviour character-for-character, which is what keeps Track-A / EUR numerics
# from moving. Same sys.path rationale as above.
from ld_read_path import (  # noqa: E402
    ld_allele_aware,
    ld_file_authoritative,
    ld_matrix_region_id,
)

# m3-04c Task 1a: the curated -> M2 region crosswalk (Layer A of AoU panel
# reachability). ``load_curated_to_m2`` is a pure TSV read -- it does NOT import
# pyliftover (the lift happens once, inside the builder), so this module-scope
# import cannot make ``snakemake --list`` depend on a liftover toolchain.
from build_curated_m2_crosswalk import (  # noqa: E402 -- same rationale
    crosswalk_missing_region_safes,
    load_curated_to_m2,
)

FINEMAP_DIR = config["finemap"]["output_dir"]
FINEMAP_METHODS = config["finemap"]["methods"]
PYTHON_BIN = sys.executable

# m3-04c Task 1a: load the curated -> M2 crosswalk ONCE at module scope.
# ``REGION_SAFE_TO_ID`` (Snakefile:45-62) is built ONLY from
# config/regions_curated.csv, whose ``region_id`` column IS the curated slug, so
# it is essentially the IDENTITY for curated regions and can never yield an M2
# id. The AFR_aou chain head in config/pipeline.yaml templates on
# ``{region_id}``, so without this map the resolver asks for
# ``AFR_aou/FTO_16q12.rds`` -- a filename the producer never writes.
# Rows with status=unmapped are skipped by the loader, so ``.get(...)`` falls
# through to today's legacy value character-for-character. A MISSING artifact
# yields {} rather than an error: the DAG must still build on a fresh clone,
# before the crosswalk has been generated.
#
# ⚠ DISCLOSED ANALYSIS CHANGE (m3-04c Task 1c) -- READ BEFORE THE FIRST FIRE.
#
# This crosswalk is what makes the AoU AFR panel REACHABLE at all. Reachability
# is not a plumbing detail: it moves published numbers. Recorded here rather
# than absorbed silently.
#
#   ⚠ THE CROSSWALK IS ANCESTRY-GATED (260805-23d Task 1, BLOCKER-B). It is
#   applied ONLY for the ancestries listed in `config/pipeline.yaml
#   ld_read_path.ancestries` (AFR today), via
#   src/python/ld_read_path.py::ld_matrix_region_id. m3-04c Task 1a applied it
#   for EVERY ancestry, which reached straight into EUR and TRANS: the crosswalk
#   is AFR-only by construction (build_curated_m2_crosswalk.py:145), yet
#   ld_panel.EUR[1] (EUR_aou) and the ld_panel.TRANS chain HEAD both template on
#   {region_id}. Off the allow-list ld_matrix_region_id returns 3f431ab's
#   expression character-for-character, so the resolved input.ld_matrix string
#   for EUR / TRANS cannot move. This is NOT merely a params.region_id vs
#   input.ld_matrix collision concern -- it is a frozen-numerics containment for
#   a manuscript in submission.
#
#   THE CHANGE. The FIRST curated AFR region for which an AFR_aou/<m2_id>.rds
#   actually exists switches its LD source from AFR_1kg
#   (data/processed/ld_reference/AFR/<region_safe>.rds -- 1000G AFR, n=661) to
#   the AoU AFR panel, and that region's fine-mapping numerics WILL change:
#   PIPs, credible-set membership, credible-set size, and the estimate_s
#   z-vs-LD consistency scalar. Until such an .rds exists, every AFR region
#   still falls through to the same tail it uses today, so this crosswalk moves
#   nothing on its own.
#
#   IT IS INTENDED, AND IT IS STILL DISCLOSABLE. The n=661 1000G AFR reference
#   IS the miscalibration M3 exists to correct, so the switch is the whole point
#   of this phase -- not a regression. But it means any AFR figure/table
#   regenerated after the first AFR_aou artifact lands is NOT comparable to the
#   same figure/table produced before it. State the switch in the
#   manuscript/OSF record; do not let a reader discover it by diffing versions.
#
#   THE HOLD SWITCH IS `config/pipeline.yaml ld_panel.pin.AFR`. Set it to a
#   source name (e.g. "AFR_1kg") to pin the AFR chain to that entry ONLY, which
#   holds a fit at a known panel while the change is being disclosed or while a
#   before/after comparison is produced. It is null by default -- the default is
#   the chain, and the chain now reaches AFR_aou. (`strict_aou_only: true` is
#   the opposite lever: fail loudly instead of falling back.)
#
# ⚠ SH2B3 CORE-STRADDLE CAVEAT (T-m3-04c-13). SH2B3_12q24 -- the ANCHOR locus --
#   is the only curated region mapping to a SPLIT parent, and it maps to
#   m2_region_00040__sub14. That subregion's CORE owns 523,169 bp of the
#   600,000 bp locus (87.2%); the remaining 12.8% sits inside __sub15's core and
#   is covered by __sub14's panel only through its BUFFER -- the region where a
#   stitched parent's core-ownership de-dup would have assigned those variants
#   to __sub15 instead. Both windows fully CONTAIN the locus, so containment
#   cannot decide; maximum core overlap selects __sub14 and the independent
#   window-edge-distance criterion agrees. NEITHER core fully contains SH2B3.
#   The bp arithmetic is NOT the acceptance test: run_susie_rss.R gates on
#   REALIZED variant overlap/coverage. The region-1 gate (m3-04c Task 3 STEP A)
#   is where that realized overlap/coverage is measured for SH2B3 explicitly,
#   off the newly-logged declared-LD value. Do not assume 87.2% of the bp
#   carries over to the variant axis.
#
_CURATED_TO_M2_TSV = Path(
    config.get("paths", {}).get(
        "curated_to_m2_map",
        str(_FINEMAP_BASE / "config" / "curated_to_m2_region_map.tsv"),
    )
)
CURATED_TO_M2 = load_curated_to_m2(_CURATED_TO_M2_TSV)
if not CURATED_TO_M2:
    print(
        "[finemap.smk] WARN: curated->M2 crosswalk not loaded from "
        f"{_CURATED_TO_M2_TSV}; every curated region falls back to the legacy "
        "region-safe id (today's behaviour, and the AoU AFR panel stays "
        "unreachable). Regenerate with "
        "`python src/python/build_curated_m2_crosswalk.py`.",
        file=sys.stderr,
    )
else:
    # quick-260806-b77 (m3-04c blast radius, FINDING L): the WARN above fires
    # ONLY on a FULLY EMPTY dict. The crosswalk is a HAND-RUN, DAG-ABSENT
    # artifact -- no rule produces config/curated_to_m2_region_map.tsv -- so a
    # 13th curated region added to config/regions_curated.csv WITHOUT rerunning
    # the builder was silently legacy-routed: the AoU AFR panel simply stayed
    # unreachable for it, with no message anywhere. PARTIAL coverage needs its
    # own, NAMED warning.
    #
    # The curated set is derived from config["paths"]["regions_curated"], NOT
    # from REGION_SAFE_TO_ID: that name is built in Snakefile:45-62 and is
    # currently referenced only from inside DEFERRED lambdas, so its
    # availability at finemap.smk PARSE time is not proven. The config path has
    # no include-order dependency.
    #
    # Deliberately a WARN and not a raise: a raise at DAG-parse time would
    # change `--list` behaviour for every caller and risks tripping pre-existing
    # DAG-building tests. The actual gate is
    # tests/m3/test_curated_m2_crosswalk_drift.py, which compares the COMMITTED
    # artifact against a fresh rebuild -- the first test in this repo to read the
    # committed file at all.
    _CURATED_MISSING = crosswalk_missing_region_safes(
        config.get("paths", {}).get("regions_curated", "config/regions_curated.csv"),
        _CURATED_TO_M2_TSV,
    )
    if _CURATED_MISSING:
        print(
            f"[finemap.smk] WARN: the curated->M2 crosswalk at "
            f"{_CURATED_TO_M2_TSV} has NO ROW AT ALL for "
            f"{len(_CURATED_MISSING)} curated region(s): "
            f"{', '.join(_CURATED_MISSING)}. Those regions are SILENTLY "
            "legacy-routed -- the AoU AFR panel stays unreachable for them and "
            "nothing else will say so. The crosswalk is hand-run and DAG-absent, "
            "so it does not rebuild itself. Regenerate with "
            "`python src/python/build_curated_m2_crosswalk.py`.",
            file=sys.stderr,
        )


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
        # m3-W3-T2 + CR-001 (2026-05-01), CORRECTED by m3-04c Task 1a
        # (2026-08-05). wildcards.region is the filesystem-safe curated slug
        # (e.g., FTO_16q12); the AoU chain head in config/pipeline.yaml uses
        # {region_id} (e.g., m2_region_00067). BOTH placeholders are still
        # passed so the resolver substitutes them independently -- without
        # region_safe= the 1kg/HGDP/UKBB tails regress to the same-value
        # substitution bug CR-001 fixed.
        #
        # WHAT CR-001 GOT WRONG: it claimed the safe-slug -> M2-id translation
        # was performed here. It never was. Snakefile:45-62 builds that map
        # ONLY from config/regions_curated.csv, whose region_id column IS the
        # slug, so the map is the identity for curated regions and cannot
        # emit m2_region_00067. The AoU panel path was therefore UNREACHABLE:
        # the resolver asked for AFR_aou/FTO_16q12.rds, which the producer
        # never writes, and fell silently through to the 1kg tail.
        # config/curated_to_m2_region_map.tsv performs the real translation;
        # a curated region with no M2 counterpart (BMI_Xq24 is chrX, and M2 is
        # autosomes-only per D-M2-09) falls back to the legacy value, so its
        # resolved path string is byte-identical to today's.
        #
        # HOW THE CROSSWALK SELECTS -- and why it does NOT read the manifest's
        # start_grch37/end_grch37: for a SPLIT parent those columns hold the
        # PARENT's ~89 Mb bounding box copied verbatim into every subregion row
        # (build_ld_region_manifest.py:585-587,650-653), so all 18 subregions of
        # m2_region_00040 tie exactly and a lexicographic tie-break returns
        # __sub00 -- ZERO bp of overlap with SH2B3, ~66 Mb away. Selection is
        # instead done on the *_grch38 window/core columns LIFTED back to GRCh37
        # (hg38ToHg19, the only chain the repo ships), ranked on CORE overlap.
        #
        # ⚠ DISCLOSED (m3-04c, T-m3-04c-13): SH2B3_12q24 straddles a core
        # boundary. __sub14's core owns 523,169 bp of the 600,000 bp locus
        # (87.2%); the remaining 12.8% lives in __sub15's core, so __sub14's
        # panel covers those variants only through its BUFFER. run_susie_rss.R
        # gates on REALIZED variant overlap/coverage, not bp, so the region-1
        # gate must check that explicitly rather than assume the arithmetic
        # carries over.
        #
        # ⚠ ANCESTRY GATE (260805-23d Task 1, BLOCKER-B). ld_matrix_region_id
        # applies CURATED_TO_M2 only for config ld_read_path.ancestries (AFR).
        # For EUR / TRANS it returns REGION_SAFE_TO_ID[region] -- 3f431ab's
        # expression, character for character -- so this whole call reproduces
        # the pre-m3-04c resolution and Track-A numerics cannot move.
        ld_matrix=lambda wildcards: str(
            resolve_ld_path(
                region_id=ld_matrix_region_id(
                    wildcards.region,
                    wildcards.ancestry,
                    config,
                    CURATED_TO_M2,
                    REGION_SAFE_TO_ID,
                ),
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
        # 260805-23d Task 1 (BLOCKER-B): "true" only for the ancestries in config
        # ld_read_path.ancestries. "false" makes run_susie_rss.R IGNORE the
        # declared LD argument entirely, so its candidate list is the legacy one
        # and the two extra argv tokens are inert BY CONSTRUCTION. The literal
        # value is a string because it is parsed by the R script, which stop()s
        # on anything it does not recognise rather than silently defaulting.
        ld_authoritative=lambda wildcards: ld_file_authoritative(
            wildcards.ancestry, config
        ),
        # 260805-o7o (m3-04c blast-radius FINDING H): "true" only for the
        # ancestries in config ld_read_path.ancestries AND only when
        # ld_read_path.allele_aware is explicitly true. "false" makes
        # run_susie_rss.R run the legacy CHR:POS match() character-for-character,
        # so EUR / TRANS cannot move. A string for the same reason as
        # ld_authoritative: the R script stop()s on anything it does not
        # recognise rather than silently defaulting.
        ld_allele_aware=lambda wildcards: ld_allele_aware(
            wildcards.ancestry, config
        ),
    shell:
        r"""
        export SUSIE_MAX_VARIANTS={params.susie_max_variants}
        # m3-04c Task 1b (DEC-2026-08-05-m3-ld-read-path): --ld-file passes the
        # DECLARED input.ld_matrix -- i.e. resolve_ld_path's answer -- straight
        # into the R script, which tries it FIRST. Its ABSENCE was BLOCKER-1:
        # the input was declared to the DAG but never handed to the consumer, so
        # run_susie_rss.R rebuilt ld_dir/ancestry/region_id.rds, could never
        # reach AFR_aou/, and fell silently to an identity matrix. --ld-dir
        # stays as the back-compat fallback. DO NOT remove --ld-file without
        # re-opening the declare-vs-read split.
        #
        # 260805-23d Task 1 (BLOCKER-B): --ld-authoritative carries the ancestry
        # allow-list verdict into the R script. "false" (every ancestry outside
        # config ld_read_path.ancestries) makes the loader IGNORE the declared-LD
        # argument entirely, so its candidate list is the legacy one and these two
        # extra tokens are inert BY CONSTRUCTION -- the containment that keeps a
        # Track-A EUR fit from moving when EUR_ukbb_pub/ lands. The flag is NOT
        # named --ld-file-authoritative on purpose: neither --ld-file nor --ld-dir
        # may be a prefix of it, or R optparse long-option matching goes ambiguous.
        Rscript src/legacy/region_analysis/scripts/run_susie_rss.R \
          --sumstats {input.sumstats} \
          --trait {wildcards.trait} \
          --ancestry {wildcards.ancestry} \
          --method {wildcards.method} \
          --region {params.region_id} \
          --regions-csv {params.regions_csv} \
          --ld-dir {params.ld_dir} \
          --ld-file {input.ld_matrix} \
          --ld-authoritative {params.ld_authoritative} \
          --ld-allele-aware {params.ld_allele_aware} \
          --variant-list {input.variants} \
          --credible-set {params.credible_set} \
          --policy {input.policy} \
          --output {output.json}
        # m3-02e Move 3: surface the per-region estimate_s z-vs-LD consistency
        # scalar (Zou 2022) to a log artifact. No f-string braces here -- only
        # Snakemake's intended {{}} placeholders -- so the rule shell stays valid.
        #
        # m3-04c Task 1b: this one-liner is also the per-region RECEIPT for
        # `resolved == what-the-script-opens` -- ld_matrix is the path opened,
        # ld_file_declared is the path resolved and declared; a mismatch (or an
        # 'identity' ld_matrix) means the read path regressed. It ALSO reads the
        # two Path-1/Path-2 revert flags (HIGH-2). SINCE K-1 (quick-260806-pd3)
        # THE PAIR IS NO LONGER OVERLOADED: variant_catalog_fallback is set by
        # PATH 1 ONLY (the AFR variant-catalog empty-subset revert -- the
        # pre-existing key's one meaning), and ld_overlap_zero_fallback is the
        # PATH-2 (ld_overlap==0) discriminator. Reading both still separates the
        # two reverts. Write-only flags are not observability, which is why they
        # are consumed here.
        #
        # 260805-23d Task 3: ld_authoritative is read too, because it is what
        # makes the receipt INTERPRETABLE. Off the allow-list ld_matrix is
        # EXPECTED to differ from the declared path -- that difference is the
        # EUR/TRANS containment working, not a regression -- so a reader that
        # cannot see the regime would raise a false alarm on every EUR row.
        #
        # 260805-o7o (FINDING H): the eight allele-join fields are read HERE for
        # the same reason -- a write-only counter is not observability, which is
        # the project rule this file already states above. ld_allele_aware makes
        # the counters interpretable (null = not measured, i.e. EUR/TRANS;
        # 0 = measured and clean), and ld_allele_catalog_join records which
        # variant-catalog regime produced the subset.
        #
        # ============================================================
        # quick-260806-b77 (m3-04c blast radius, FINDING J): AN ABSENT KEY AND A
        # REGRESSED KEY USED TO RENDER IDENTICALLY.
        # ============================================================
        # run_susie_rss.R's two EARLY EXITS -- `no_variants` and
        # `too_many_variants` -- build their result list from a SHORT key set
        # that carries status / notes / ld_dir / the variant_catalog_* quartet
        # and NO ld_matrix, ld_file_declared, ld_authoritative or ld_allele_*
        # key at all. d.get() on an absent key returns None, so this receipt
        # printed `ld_matrix None ld_file_declared None` -- character for
        # character what a genuine declare-vs-read regression prints. HLA_6p21
        # and PYHIN1_1q23 are NAMED too_many_variants regions, so that ambiguity
        # was firing on REAL INPUTS TODAY, and it is the exact defect class
        # BLOCKER-1 was.
        #
        # THE FIX IS ENTIRELY ON THIS SIDE OF THE PAIR. run_susie_rss.R was NOT
        # touched by finding J's fix -- that claim is historical and stands. (It
        # was RE-FROZEN at dc4bbd2 then; the live pin is now bf04199, re-set by
        # quick-260806-pd3 for finding K-1, whose unfreeze is SPENT.) Every LD
        # field is now wrapped
        # as (d.get(KEY) if KEY in d else na), where `na` is
        #   NA_EARLY_EXIT  when status is no_variants / too_many_variants
        #   ABSENT         otherwise -- i.e. a REAL regression
        # and ld_receipt_verdict renders early_exit:<status> /
        # ld_fields_present / ALARM_LD_FIELDS_MISSING. The early-exit token and
        # the alarm token are DIFFERENT STRINGS; that inequality is the whole of
        # finding J and is asserted by
        # tests/m3/test_finemap_receipt_early_exit.py, which EXTRACTS this line
        # from the live source and runs it on fixtures.
        #
        # The literal d.get(KEY) spelling survives inside every wrapper on
        # purpose -- tests/m3/test_ld_allele_aware_wiring.py and
        # tests/m3/test_ld_read_path.py assert on it, and both are pre-existing.
        #
        # ============================================================
        # THE DECODER RING FOR variant_catalog_fallback (FINDING K -- CLOSED by
        # quick-260806-pd3; see K-1 in
        # .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md)
        # ============================================================
        # variant_catalog_fallback is a PRE-EXISTING key. m3-04c briefly MUTATED
        # it -- the Path-2 (ld_overlap==0) retry set it too, with NO NUMERIC
        # CAUSE -- so a before/after JSON diff showed a causeless false -> true
        # flip. K-1 CLOSED that by deleting the Path-2 assignment, restoring the
        # key's single legacy meaning: the PATH-1 AFR variant-catalog
        # empty-subset revert.
        #
        # variant_catalog_fallback_cause is the RUNTIME TOKEN that renders the
        # PAIR, so a reader diffing JSONs meets the explanation where they are
        # actually looking. FIVE outcomes, and the token set is EXTRACTED from
        # this very line by tests/m3/test_finemap_receipt_early_exit.py -- never
        # hand-copied, so a rename here turns that test RED:
        #
        #   key absent            -> key_absent
        #        a JSON older than the key itself. Real: 687 of the 2,596 region
        #        JSONs under results/legacy/region_analysis (measured 2026-08-06).
        #   false + false/absent  -> none
        #        neither revert fired. This is what 1,900 of the 1,909 legacy
        #        JSONs carrying the key render. (1,909 + 687 key-absent = 2,596.)
        #   false + true          -> path2_ld_overlap_zero_RETRY
        #        THE POST-K-1 CANONICAL PATH-2 SIGNATURE. Before K-1 this pair
        #        rendered `none`, which was FALSE: Path 2 DID fire.
        #   true  + true          -> path2_ld_overlap_zero_NO_NUMERIC_CAUSE
        #        UNREACHABLE from any tree at or after bf04199. Retained as a
        #        FORENSIC MARKER: it dates an artifact to the m3-04c window.
        #        0 such artifacts exist on this node (0 JSONs carry
        #        ld_overlap_zero_fallback at all).
        #   true  + false         -> path1_variant_catalog_empty_subset
        #        the key's restored, and now ONLY, meaning. Real: the 9 AFR
        #        JSONs measured 2026-08-06 (RAD50_peak__tile1 and 8
        #        PYHIN1_1q23 tiles), none carrying ld_overlap_zero_fallback.
        #
        # ⚠ PREFIX-COLLISION TRAP. `path2_ld_overlap_zero` is a prefix of BOTH
        # path2_* tokens, so a substring match cannot separate them. The tokens
        # are deliberately named so neither is a prefix of the other, AND the
        # test matches on a trailing delimiter. Both properties are asserted
        # permanently (NC-K6).
        {PYTHON_BIN} -c "import json,sys; d=json.load(open(sys.argv[1])); st=d.get('status'); EARLY=('no_variants','too_many_variants'); na=('NA_EARLY_EXIT' if st in EARLY else 'ABSENT'); vd=('early_exit:'+str(st) if st in EARLY else ('ld_fields_present' if 'ld_matrix' in d else 'ALARM_LD_FIELDS_MISSING')); vcp=('variant_catalog_fallback' in d); vcv=d.get('variant_catalog_fallback'); ozv=d.get('ld_overlap_zero_fallback'); cause=('key_absent' if not vcp else ('path1_variant_catalog_empty_subset' if (vcv and not ozv) else ('path2_ld_overlap_zero_NO_NUMERIC_CAUSE' if (vcv and ozv) else ('path2_ld_overlap_zero_RETRY' if ozv else 'none')))); print('region', sys.argv[2], 'ancestry', sys.argv[3], 'status', st, 'ld_receipt_verdict', vd, 'ld_z_consistency_s', (d.get('d3b_ld_z_consistency_s') if 'd3b_ld_z_consistency_s' in d else na), 'ld_source_mismatch_flag', (d.get('ld_source_mismatch_flag') if 'ld_source_mismatch_flag' in d else na), 'ld_matrix', (d.get('ld_matrix') if 'ld_matrix' in d else na), 'ld_file_declared', (d.get('ld_file_declared') if 'ld_file_declared' in d else na), 'ld_authoritative', (d.get('ld_authoritative') if 'ld_authoritative' in d else na), 'variant_catalog_fallback', (d.get('variant_catalog_fallback') if 'variant_catalog_fallback' in d else na), 'ld_overlap_zero_fallback', (d.get('ld_overlap_zero_fallback') if 'ld_overlap_zero_fallback' in d else na), 'variant_catalog_fallback_cause', cause, 'ld_allele_aware', (d.get('ld_allele_aware') if 'ld_allele_aware' in d else na), 'ld_allele_exact', (d.get('ld_allele_exact') if 'ld_allele_exact' in d else na), 'ld_allele_flipped', (d.get('ld_allele_flipped') if 'ld_allele_flipped' in d else na), 'ld_allele_dropped_palindromic', (d.get('ld_allele_dropped_palindromic') if 'ld_allele_dropped_palindromic' in d else na), 'ld_allele_dropped_mismatch', (d.get('ld_allele_dropped_mismatch') if 'ld_allele_dropped_mismatch' in d else na), 'ld_allele_dropped_ambiguous', (d.get('ld_allele_dropped_ambiguous') if 'ld_allele_dropped_ambiguous' in d else na), 'ld_allele_dropped_unusable', (d.get('ld_allele_dropped_unusable') if 'ld_allele_dropped_unusable' in d else na), 'ld_allele_catalog_join', (d.get('ld_allele_catalog_join') if 'ld_allele_catalog_join' in d else na))" {output.json} {wildcards.region} {wildcards.ancestry} > {log.ld_z_consistency} || true
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
