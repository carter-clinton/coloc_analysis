"""Manifest-driven QTL colocalization dispatch (Phase 2).

Extends the Phase 1 coloc.smk pattern to GWAS-vs-QTL pairwise coloc.
The QTL coloc manifest cross-joins (locus x tissue x gene) per QTL source.
Each row maps to a single run_qtl_coloc.R invocation.

T-02-05 mitigation: wildcard_constraints qtl_coloc_id regex prevents path
traversal (same pattern as T-1-03).

Must be included AFTER qtl_download.smk and finemap.smk in the top-level
Snakefile so QTL_RAW_DIR, QTL_HARMONIZED_DIR, FINEMAP_DIR, and
finemap_output() are in scope.

Modified 2026-08-06 (260805-w7u, m3-04c blast-radius FINDING E) -- the gate row
``m3-04c-BLAST-RADIUS.md:141`` "Any GWAS x QTL colocalization".
``_qtl_coloc_ld_input`` is now routed through
``src/python/ld_panel.py::resolve_ld_path()`` using the SAME crosswalk object
``run_finemap`` uses. Before this, ``grep -cE
"CURATED_TO_M2|resolve_ld_path|ld_read_path" qtl_coloc.smk`` was **0**: this was
the one LD consumer that was never crosswalked, so an AFR GWAS fit produced on
the AoU panel would have been colocalized against the *1kG* LD matrix inside a
single ``coloc.susie`` posterior, with nothing in the output to say so.

ANCESTRY-GATED, on ONE lever: ``ld_read_path.{enabled,ancestries,coloc}`` via
``src/python/ld_read_path.py::ld_coloc_applies``. Off the allow-list -- which is
EUR, TRANS, EAS and HIS today -- the resolution expression is the pre-change one
character for character, so Track-A's 1,957 legacy coloc JSONs and today's 32/32
EUR successes cannot move.
"""

import os
import sys
from pathlib import Path

import pandas as pd

# 260805-w7u (FINDING E): the M3 LD-panel resolver + the allow-list gate, so the
# coloc LD path is decided by the SAME resolver run_finemap uses instead of a
# second constructed string. Same sys.path idiom as finemap.smk:42-79.
# ``workflow.basedir`` resolves to the project root under standard Snakemake
# invocation; walk up defensively if ``src/python`` is not directly under it.
try:
    _QTL_COLOC_BASE = Path(workflow.basedir)  # type: ignore[name-defined]
except NameError:
    _QTL_COLOC_BASE = Path(os.getcwd())

_QTL_SRC_PYTHON = str(_QTL_COLOC_BASE / "src" / "python")
if _QTL_SRC_PYTHON not in sys.path:
    sys.path.insert(0, _QTL_SRC_PYTHON)

from ld_panel import resolve_ld_path  # noqa: E402 -- intentional after sys.path mutation

# ⚠ THE CURATED->M2 CROSSWALK LOADER IS DELIBERATELY *NOT* IMPORTED HERE.
# Snakemake includes share one global namespace (Snakefile:113 includes
# finemap.smk, :138 includes this file) and qtl_coloc.smk already hard-depends on
# finemap.smk -- ``_qtl_coloc_gwas_fit_input`` calls ``finemap_output()`` eagerly
# as a .get() default. So ``CURATED_TO_M2`` (built once at finemap.smk:166) and
# ``REGION_SAFE_TO_ID`` (Snakefile:45-62) are already in scope and are REUSED.
# Loading the crosswalk a second time would create a second source of truth that
# can silently drift from the one run_finemap walks (T-w7u-07); the drift would
# be invisible precisely because both loads read the same file TODAY. The
# forward gate is the literal `grep -c` for that loader's name over this file,
# which must stay 0 -- so the name is deliberately not spelled out above.
from ld_read_path import (  # noqa: E402 -- same sys.path rationale
    ld_coloc_ancestries,
    ld_coloc_applies,
    ld_coloc_join,
    ld_matrix_region_id,
)

# 260805-w7u: the region variant catalog is the panel<->fit BRIDGE (see
# run_qtl_coloc.R). It is already run_finemap.input.variants, and it is resolved
# through the same lockstep-aware helper so the coloc job and the fine-map job
# read the SAME catalog file rather than two files that merely look alike.
from occlusion_lockstep_cli import lockstep_variants_path  # noqa: E402

PYTHON_BIN = sys.executable
QTL_COLOC_DIR = os.path.join(config["paths"]["results_root"], "qtl_coloc")

# T-02-05: Region-safe manifest ID constraint (same pattern as coloc.smk T-1-03).
# Only alphanumeric + underscore + dot + hyphen allowed.
wildcard_constraints:
    qtl_coloc_id=r"[A-Za-z0-9_.\-]+",


def _qtl_coloc_manifest_path():
    """Return the path to the QTL coloc manifest TSV."""
    return os.path.join(QTL_COLOC_DIR, "qtl_coloc_manifest.tsv")


def _qtl_coloc_manifest_row(qtl_coloc_id):
    """Resolve a single row from qtl_coloc_manifest.tsv by ID.

    Returns a dict, or None if the manifest does not exist or the ID is not
    found (Snakemake will retry once the manifest exists).
    """
    manifest_path = _qtl_coloc_manifest_path()
    if not os.path.exists(manifest_path):
        return None
    df = pd.read_csv(manifest_path, sep="\t", dtype=str)
    if "qtl_coloc_id" not in df.columns:
        return None
    row = df[df["qtl_coloc_id"] == qtl_coloc_id]
    if len(row) != 1:
        return None
    return row.iloc[0].to_dict()


def _qtl_coloc_per_id_jsons():
    """Enumerate per-id JSON output targets from the on-disk manifest.

    Called at Snakefile parse time (inside this .smk file) to expose
    QTL_COLOC_PER_ID_JSONS as a module-level global. Returns an empty list
    when the manifest does not yet exist — Snakemake will then only expand
    per-id targets after `build_qtl_coloc_manifest` has run once and the
    user re-invokes snakemake (manifest is a checkpoint-style prerequisite).

    Optional scope filter via `config["phase2_enabled_sources"]` (list of
    qtl_source values, defaults to None = all sources). When set, only
    manifest rows whose `qtl_source` is in the list contribute to the
    per-id JSON target set. T1 first-production uses this to target
    gtex_eqtl + gtex_sqtl only; pQTL (Synapse-auth prerequisite) and
    sc-eQTL (OneK1K QTD-map prerequisite) are T2-deferred per CP#1-final
    scope decision 2026-04-20.

    This mirrors the FINEMAP_OUTPUTS parse-time enumeration pattern in
    Snakefile (lines 80-88), but sources its row list from a materialized
    TSV rather than a config-driven cross product.
    """
    manifest_path = _qtl_coloc_manifest_path()
    if not os.path.exists(manifest_path):
        return []
    enabled_sources = config.get("phase2_enabled_sources")
    usecols = ["qtl_coloc_id", "qtl_source"] if enabled_sources else ["qtl_coloc_id"]
    try:
        df = pd.read_csv(manifest_path, sep="\t", dtype=str, usecols=usecols)
    except (ValueError, KeyError):
        return []
    if enabled_sources:
        df = df[df["qtl_source"].isin(enabled_sources)]
    return [
        os.path.join(QTL_COLOC_DIR, f"{qtl_coloc_id}.json")
        for qtl_coloc_id in df["qtl_coloc_id"].dropna().unique()
    ]


# Module-level parse-time enumeration. Exposed as a global so that both
# aggregate_qtl_coloc (below) and the Snakefile-level all_qtl_coloc target
# can reference the same list without divergence.
QTL_COLOC_PER_ID_JSONS = _qtl_coloc_per_id_jsons()

# L2G concordance is gated on OpenTargets L2G prediction data existing on disk
# (rule l2g_concordance input requires the directory). No auto-download rule
# currently exists; if the dir is absent, omit l2g_concordance.tsv from the
# default Phase 2 target list. Users can still request it explicitly once the
# data is landed.
_L2G_DIR = os.path.join(
    config["paths"]["data_root"], "raw", "opentargets", "l2g_prediction"
)
_L2G_OUTPUTS = (
    [os.path.join(QTL_COLOC_DIR, "l2g_concordance.tsv")]
    if os.path.isdir(_L2G_DIR)
    else []
)

QTL_COLOC_OUTPUTS = (
    [_qtl_coloc_manifest_path()]
    + QTL_COLOC_PER_ID_JSONS
    + [
        os.path.join(QTL_COLOC_DIR, "qtl_coloc_summary.tsv"),
        os.path.join(QTL_COLOC_DIR, "tier_assignments.tsv"),
        os.path.join(QTL_COLOC_DIR, "pph4_threshold_sweep.tsv"),
        os.path.join(QTL_COLOC_DIR, "gene_tissue_matrix.tsv"),
        os.path.join(QTL_COLOC_DIR, "gene_tissue_long.tsv"),
    ]
    + _L2G_OUTPUTS
)


def _qtl_manifest_row_by_wildcards(wildcards):
    """Resolve a manifest row via multiple lookup strategies.

    Tries in order:
      1. wildcards.qtl_coloc_id (used by run_qtl_coloc in this file).
      2. Compound key (tissue, gene_id, region) — used by
         harmonize_eqtl_region / harmonize_sqtl_region / harmonize_pqtl_region
         / harmonize_onek1k_region, whose wildcards don't carry qtl_coloc_id.
         When (tissue, gene_id, region) matches multiple sources (e.g.
         gtex_eqtl vs gtex_sqtl vs ukbppp_pqtl all with tissue=plasma),
         additional disambiguation is delegated to qtl_source if the
         wildcard carries it. In practice, path structure
         (eqtl/sqtl/pqtl/sceqtl root segment) is not available here — we
         take the first matching row.

    Returns a dict (manifest row) or None if no match.
    """
    # Path 1: direct qtl_coloc_id lookup.
    qtl_coloc_id = getattr(wildcards, "qtl_coloc_id", None)
    if qtl_coloc_id is not None:
        return _qtl_coloc_manifest_row(qtl_coloc_id)

    manifest_path = _qtl_coloc_manifest_path()
    if not os.path.exists(manifest_path):
        return None
    df = pd.read_csv(manifest_path, sep="\t", dtype=str)

    # Path 2: compound key via available wildcards. Apply each present
    # wildcard as an equality filter against its corresponding column.
    filter_map = {
        "tissue": "tissue",
        "gene_id": "gene_id",
        "region": "region",
        "dataset_id": "dataset_id",
        "cell_type": "tissue",   # harmonize_onek1k_region uses cell_type
        "protein": "gene_id",    # legacy wildcard name → manifest gene_id
    }
    sub = df
    for wc_name, col_name in filter_map.items():
        wc_val = getattr(wildcards, wc_name, None)
        if wc_val is None or col_name not in sub.columns:
            continue
        sub = sub[sub[col_name] == wc_val]
        if len(sub) == 0:
            return None
    if len(sub) == 0:
        return None
    return sub.iloc[0].to_dict()


def _qtl_manifest_field(wildcards, field):
    """Resolve a single field from the QTL coloc manifest for a given wildcard.

    Used by qtl_download.smk (harmonize_*_region) and by rules in this file.
    Supports both qtl_coloc_id-keyed lookup (run_qtl_coloc) and compound-key
    lookup (harmonize_* rules whose wildcards are path components).
    """
    row = _qtl_manifest_row_by_wildcards(wildcards)
    if row is None:
        return "MISSING_MANIFEST"
    return row.get(field, "MISSING_FIELD")


def _qtl_coloc_gwas_fit_input(wildcards):
    """Input function: resolve GWAS .fit.rds path from the manifest row."""
    row = _qtl_coloc_manifest_row(wildcards.qtl_coloc_id)
    if row is None:
        return os.path.join(
            QTL_COLOC_DIR,
            f"_MISSING_MANIFEST_{wildcards.qtl_coloc_id}.gwas.fit.rds",
        )
    return row.get(
        "gwas_fit_path",
        finemap_output("susie", row["gwas_trait"], row["ancestry"], row["region"]).replace(
            ".json", ".fit.rds"
        ),
    )


# ⚠ DISCLOSED ANALYSIS CHANGE (260805-w7u, FINDING E) -- READ BEFORE THE FIRST
#   FIRE. Recorded here rather than absorbed silently, in the register of
#   finemap.smk:103-158.
#
#   THE CHANGE. On the allow-list this input function stops constructing
#   {ld_reference}/{ancestry}/{region}.rds and asks resolve_ld_path() instead.
#   The FIRST curated AFR region for which an AFR_aou/<m2_id>.rds actually
#   exists therefore switches its COLOC LD source from AFR_1kg (1000G AFR,
#   n=661) to the AoU AFR panel, and that pair's colocalization numerics WILL
#   move: PP.H4, credible-set membership, and which variants enter at all.
#   Until such an .rds exists nothing on this path moves -- but the day it lands
#   it moves without a flag unless this note is carried into the record. Any AFR
#   coloc figure or table regenerated after that point is NOT comparable to one
#   produced before it. It is INTENDED (the n=661 reference IS the
#   miscalibration M3 exists to correct) and it is still DISCLOSABLE.
#
#   ONE CROSSWALK OBJECT. CURATED_TO_M2 (finemap.smk:166) and REGION_SAFE_TO_ID
#   (Snakefile:45-62) are REUSED from the shared include namespace, never
#   re-loaded here. run_finemap and run_qtl_coloc must not be able to disagree
#   about which artifact a region maps to; two loads of the same TSV agree today
#   and are free to diverge tomorrow (T-w7u-07).
#
#   THE RAISE IS INTENDED. With the gate ON and no panel anywhere,
#   resolve_ld_path raises FileNotFoundError at DAG-BUILD time -- the same
#   property finemap.smk already has. Falling back to the legacy path here would
#   add a FIFTH silent layer to the four exit-0 layers already traced on this
#   path (empty LD intersection -> "too_few_snps" at rc 0; a sparse dsCMatrix
#   rejected by runsusie inside a tryCatch -> "qtl_susie_failed" at rc 0;
#   use_identity fitting coloc.susie on diag(n) with only a cat(); and Snakemake
#   seeing rc 0 for all of them). Loud beats a fifth layer.
#
#   OFF THE ALLOW-LIST THE RETURN EXPRESSION BELOW IS 7b1025d's, CHARACTER FOR
#   CHARACTER. That is the Track-A containment -- 1,957 legacy coloc JSONs, and
#   today's coloc successes are 32/32 EUR. Do not "tidy" it; it is pinned
#   differentially against the real 7b1025d function in
#   tests/m3/test_qtl_coloc_ld_resolution.py.
def _qtl_coloc_ld_input(wildcards):
    """Input function: resolve LD matrix path from the manifest row.

    ON the allow-list (ld_read_path.{enabled,ancestries,coloc}) the answer comes
    from resolve_ld_path() through ld_matrix_region_id() -- the same call
    run_finemap.input.ld_matrix makes -- so the LD reaching coloc::runsusie is
    the SAME artifact the GWAS fit was produced on. OFF it, the manifest column
    (or the legacy constructed path) is returned exactly as before.
    """
    row = _qtl_coloc_manifest_row(wildcards.qtl_coloc_id)
    if row is None:
        return os.path.join(
            QTL_COLOC_DIR,
            f"_MISSING_MANIFEST_{wildcards.qtl_coloc_id}.ld.rds",
        )
    ancestry = row["ancestry"]
    if ld_coloc_applies(ancestry, config):
        return str(
            resolve_ld_path(
                region_id=ld_matrix_region_id(
                    row["region"],
                    ancestry,
                    config,
                    CURATED_TO_M2,
                    REGION_SAFE_TO_ID,
                ),
                ancestry=ancestry,
                config=config,
                region_safe=row["region"],
            )
        )
    return row.get(
        "ld_matrix_path",
        os.path.join(
            config["paths"]["ld_reference"],
            row["ancestry"],
            f"{row['region']}.rds",
        ),
    )


def _qtl_coloc_variants_path(wildcards):
    """The region variant catalog that BRIDGES the panel to the GWAS fit.

    260805-w7u (FINDING E). ``{ld_reference}/variants/{region}.tsv`` --
    ``CHR, POS, REF, ALT, SNP_ID``, GRCh37, already ``run_finemap.input.variants``
    -- resolved through the SAME lockstep-aware helper ``finemap.smk`` uses, so
    the coloc job and the fine-map job read the same file rather than two files
    that merely look alike.

    Returns ``None`` off the allow-list. That is what makes EUR's DAG gain NO
    new edge: ``input.variants`` is then ``[]`` and the shell emits no
    ``--variant-list`` token at all.
    """
    row = _qtl_coloc_manifest_row(wildcards.qtl_coloc_id)
    if row is None or not ld_coloc_applies(row["ancestry"], config):
        return None
    return lockstep_variants_path(
        row["region"], row["ancestry"], config, config["paths"]["ld_reference"]
    )


def _qtl_coloc_variants_input(wildcards):
    path = _qtl_coloc_variants_path(wildcards)
    return [path] if path else []


def _qtl_coloc_harmonized_input(wildcards):
    """Input function: resolve harmonized QTL TSV path from the manifest row."""
    row = _qtl_coloc_manifest_row(wildcards.qtl_coloc_id)
    if row is None:
        return os.path.join(
            QTL_COLOC_DIR,
            f"_MISSING_MANIFEST_{wildcards.qtl_coloc_id}.harmonized.tsv.gz",
        )
    return row.get(
        "harmonized_qtl_path",
        os.path.join(
            QTL_HARMONIZED_DIR,
            row["qtl_source"].replace("gtex_", "").replace("ukbppp_", "").replace("onek1k_", ""),
            row.get("dataset_id", "unknown"),
            row["gene_id"],
            f"{row['region']}.harmonized.tsv.gz",
        ),
    )


rule build_qtl_coloc_manifest:
    """Build the QTL coloc manifest by cross-joining regions x QTL sources x tissues x genes.

    IMPORTANT: The manifest builder iterates ALL sources defined in
    qtl_sources.yaml (gtex_eqtl, gtex_sqtl, ukbppp_pqtl, onek1k_sceqtl),
    not just eQTL. Plans 02-03 and 02-04 add harmonization scripts for
    new source types, but the manifest already includes rows for all sources
    because it reads from config. sQTL/pQTL/OneK1K rows will appear once
    their harmonized files exist on disk.

    Columns: qtl_coloc_id, qtl_source, tissue, gene_id, region, ancestry,
    gwas_trait, dataset_id, chr, start_grch38, end_grch38, tissue_n, sdy,
    gwas_fit_path, ld_matrix_path, harmonized_qtl_path.
    """
    input:
        regions="config/regions_curated_grch38.csv",
        qtl_config="config/qtl_sources.yaml",
        tissue_n_lookup=os.path.join(QTL_HARMONIZED_DIR, "gtex_tissue_n_lookup.json"),
    output:
        manifest=_qtl_coloc_manifest_path(),
    params:
        script=os.path.join("src", "python", "build_qtl_coloc_manifest.py"),
        results_root=config["paths"]["results_root"],
        ld_reference=config["paths"]["ld_reference"],
        harmonized_dir=QTL_HARMONIZED_DIR,
        # 260805-w7u (FINDING E): the SAME allow-list _qtl_coloc_ld_input gates
        # on, read from the SAME config block, filtered by the SAME predicate.
        # An ancestry whose LD path the resolver decides must not also have a
        # competing path written into the manifest column -- the sentinel makes
        # that impossible to take silently. Empty string (today's default off
        # the allow-list) reproduces 7b1025d's manifest byte for byte.
        # ⚠ THE SHELL TOKEN BELOW IS QUOTED, AND THAT IS NOT COSMETIC. Off the
        # allow-list this value is the EMPTY STRING; unquoted it would collapse
        # and argparse would consume the NEXT flag as its value ("--output"),
        # failing the manifest build in exactly the default configuration.
        resolver_ancestries=",".join(ld_coloc_ancestries(config)),
    conda:
        str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
    shell:
        r"""
        mkdir -p $(dirname {output.manifest})
        python {params.script} \
            --regions {input.regions} \
            --qtl-sources {input.qtl_config} \
            --tissue-n-lookup {input.tissue_n_lookup} \
            --results-root {params.results_root} \
            --ld-reference {params.ld_reference} \
            --harmonized-dir {params.harmonized_dir} \
            --resolver-ancestries "{params.resolver_ancestries}" \
            --output {output.manifest}
        """


rule run_qtl_coloc:
    """Run GWAS-vs-QTL coloc.susie for a single manifest row.

    This is the main dispatch rule. Each qtl_coloc_id corresponds to a
    unique (region x tissue x gene x qtl_source x ancestry) combination.
    """
    input:
        manifest=_qtl_coloc_manifest_path(),
        gwas_fit=_qtl_coloc_gwas_fit_input,
        qtl_sumstats=_qtl_coloc_harmonized_input,
        ld_matrix=_qtl_coloc_ld_input,
        # 260805-w7u (FINDING E): [] off the allow-list, so EUR's DAG gains no
        # new edge and Track A's 1,957 legacy coloc JSONs stay reproducible.
        variants=_qtl_coloc_variants_input,
        policy="config/susie_policy.yaml",
        script="src/snakemake/scripts/run_qtl_coloc.R",
        join_script="src/snakemake/scripts/ld_allele_join.R",
    output:
        json=os.path.join(QTL_COLOC_DIR, "{qtl_coloc_id}.json"),
    log:
        # 260805-w7u: the per-pair LD receipt, in the exact register of
        # finemap.smk:441. A write-only counter is not observability.
        ld_receipt=os.path.join(QTL_COLOC_DIR, "{qtl_coloc_id}.ld_join.log"),
    params:
        qtl_source=lambda wc: _qtl_manifest_field(wc, "qtl_source"),
        tissue=lambda wc: _qtl_manifest_field(wc, "tissue"),
        gene_id=lambda wc: _qtl_manifest_field(wc, "gene_id"),
        region=lambda wc: _qtl_manifest_field(wc, "region"),
        ancestry=lambda wc: _qtl_manifest_field(wc, "ancestry"),
        sdy=lambda wc: _qtl_manifest_field(wc, "sdy"),
        sample_size=lambda wc: _qtl_manifest_field(wc, "tissue_n"),
        # 260805-w7u (FINDING E). ONE gate, rendered as a string because
        # run_qtl_coloc.R stop()s on any value it does not recognise rather than
        # silently defaulting.
        ld_allele_join=lambda wc: ld_coloc_join(
            _qtl_manifest_field(wc, "ancestry"), config
        ),
        # ⚠ THE FLAG IS A PARAM, NOT A LITERAL IN THE SHELL. Off the allow-list
        # input.variants is [] and `--variant-list {input.variants}` would render
        # a bare flag whose value becomes the NEXT token -- the same argparse/
        # optparse trap the manifest builder's empty allow-list hit. Emitting the
        # flag itself only when the input list is non-empty makes the token
        # unconstructible in the ungated case, which is stronger than quoting it.
        variant_list_flag=lambda wc: (
            "--variant-list" if _qtl_coloc_variants_path(wc) else ""
        ),
    conda:
        str(Path(workflow.basedir) / "envs" / "r_coloc.yml")
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        mkdir -p $(dirname {output.json})
        Rscript {input.script} \
            --gwas-fit {input.gwas_fit} \
            --qtl-sumstats {input.qtl_sumstats} \
            --ld-matrix {input.ld_matrix} \
            --qtl-source {params.qtl_source} \
            --tissue {params.tissue} \
            --gene-id {params.gene_id} \
            --region {params.region} \
            --ancestry {params.ancestry} \
            --sdy {params.sdy} \
            --sample-size {params.sample_size} \
            --policy {input.policy} \
            --ld-allele-join {params.ld_allele_join} \
            {params.variant_list_flag} {input.variants} \
            --output {output.json}
        # 260805-w7u: the per-pair LD RECEIPT, in the exact register of
        # finemap.smk:441. ld_matrix is the panel actually OPENED; ld_key_space
        # records which bridge won; ld_panel_overlap is the realized overlap; and
        # the six counters make every disposition class -- including the
        # orientation counter that measures deferred E-2's magnitude -- visible
        # per pair. `|| true` so a receipt failure can never mask the job's own
        # exit status, which under the gate is the thing that must be trusted.
        {PYTHON_BIN} -c "import json,sys; d=json.load(open(sys.argv[1])); print('qtl_coloc_id', sys.argv[2], 'region', sys.argv[3], 'ancestry', sys.argv[4], 'status', d.get('status'), 'ld_matrix', d.get('ld_matrix'), 'ld_allele_join', d.get('ld_allele_join'), 'ld_key_space', d.get('ld_key_space'), 'ld_panel_overlap', d.get('ld_panel_overlap'), 'ld_allele_exact', d.get('ld_allele_exact'), 'ld_allele_flipped', d.get('ld_allele_flipped'), 'ld_allele_dropped_palindromic', d.get('ld_allele_dropped_palindromic'), 'ld_allele_dropped_mismatch', d.get('ld_allele_dropped_mismatch'), 'ld_allele_dropped_ambiguous', d.get('ld_allele_dropped_ambiguous'), 'ld_allele_dropped_unusable', d.get('ld_allele_dropped_unusable'))" {output.json} {wildcards.qtl_coloc_id} {params.region} {params.ancestry} > {log.ld_receipt} || true
        """


rule aggregate_qtl_coloc:
    """Aggregate all per-pair QTL coloc JSON outputs into a summary TSV.

    Reads all JSON files in QTL_COLOC_DIR matching *.json, extracts the
    summary row (best PP.H4.abf pairwise comparison), and writes a flat TSV
    for downstream filtering and tiering.

    Note: per-id JSONs are NOT declared as inputs of this rule. Doing so
    would transitively propagate into rule all_pathway (via
    extract_tier_ab_genes → assign_tiers → aggregate_qtl_coloc), which
    would force all_pathway to require all 1243 QTL coloc jobs before it
    can run — breaking the Launch10-15 pathway drain pattern.

    Instead, rule all_qtl_coloc (in the top-level Snakefile) explicitly
    lists QTL_COLOC_PER_ID_JSONS so that invoking all_qtl_coloc correctly
    expands to all 1243 per-id coloc jobs. Invoking qtl_coloc_summary.tsv
    directly will NOT backward-chain to per-id jobs — this is intentional
    for Phase 5 compatibility. Phase 2 first-production fires via
    all_qtl_coloc.
    """
    input:
        manifest=_qtl_coloc_manifest_path(),
    output:
        summary=os.path.join(QTL_COLOC_DIR, "qtl_coloc_summary.tsv"),
    params:
        script=os.path.join("src", "python", "aggregate_qtl_coloc.py"),
        json_dir=QTL_COLOC_DIR,
    conda:
        str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
    shell:
        r"""
        python {params.script} \
            --json-dir {params.json_dir} \
            --manifest {input.manifest} \
            --output {output.summary}
        """


# ---------------------------------------------------------------------------
# Phase 2 Plan 05: Tier assignment, L2G concordance, gene-tissue matrix
# ---------------------------------------------------------------------------

# NEG_CTRL_DIR defined in negative_controls.smk (included before this file).
# Redefined here for self-contained reference; Snakemake tolerates re-assignment.
NEG_CTRL_DIR = os.path.join(config["paths"]["results_root"], "negative_controls")

QTL_PROC_ENV_COLOC = str(
    str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
)


rule assign_tiers:
    """Assign Tier A/B/C confidence levels (D-02c, QTL-source-agnostic).

    Combines GWAS-GWAS coloc results (trait-trait PP.H4) with QTL coloc
    results to produce mechanistic tier assignments. Also produces the
    PP.H4 threshold sweep table (REQ-3).

    Per REQ-7 negative-control strategy (2026-04-20 scope reconciliation):
    primary HLA-immune coverage comes from HLA-trait rows already embedded
    in the main qtl_coloc_summary.tsv (HLA_6p21 is a curated region; 113
    rows × asthma trait). Cosmetic + blood-group negative controls require
    Phase 1 fits for regions outside the curated 12 and are therefore
    delivered through Phase 5's MAGMA / LDSC-SEG / HESS / g:Profiler
    negative-control pipeline (all 3 curated sets). The dedicated Phase 2
    `run_curated_negative_controls` rule is wired-but-partial (manifest
    rows lack gwas_fit paths); its output, when present, contributes
    Tier-A-surveillance rows with tier="negative_control" but is treated
    as an optional input here: assign_tiers.py tolerates missing
    neg_ctrl_results per its CLI contract
    (`if args.neg_ctrl_results and os.path.exists(...)`).

    Implementation: `neg_ctrl_results` is declared as a `params:` path
    (not `input:`) so the rule can fire before `run_curated_negative_controls`
    produces (or gracefully skips producing) its TSV. The script applies
    its own existence check.
    """
    input:
        qtl_results=os.path.join(QTL_COLOC_DIR, "qtl_coloc_summary.tsv"),
        gwas_coloc=os.path.join(
            config["paths"]["results_root"], "multitrait",
            "coloc_summary.tsv",
        ),
        pph4_config="config/pph4_thresholds.yaml",
    output:
        tiers=os.path.join(QTL_COLOC_DIR, "tier_assignments.tsv"),
        sweep=os.path.join(QTL_COLOC_DIR, "pph4_threshold_sweep.tsv"),
    params:
        script=os.path.join("src", "python", "assign_tiers.py"),
        neg_ctrl_results=os.path.join(NEG_CTRL_DIR, "curated_neg_ctrl_results.tsv"),
    conda:
        QTL_PROC_ENV_COLOC
    shell:
        r"""
        # neg-ctrl results are optional; assign_tiers.py tolerates missing file
        if [ -f {params.neg_ctrl_results} ]; then
          neg_ctrl_arg="--neg-ctrl-results {params.neg_ctrl_results}"
        else
          neg_ctrl_arg=""
        fi
        python {params.script} \
          --input {input.qtl_results} \
          --gwas-coloc {input.gwas_coloc} \
          --pph4-config {input.pph4_config} \
          $neg_ctrl_arg \
          --output {output.tiers} \
          --sweep --sweep-output {output.sweep}
        """


rule l2g_concordance:
    """Compute Open Targets L2G concordance for Tier A loci (D-05a/D-05b).

    L2G is independent corroboration, NOT a filter gate. Disagreements are
    flagged as findings (potential distal enhancer-driven assignments).
    """
    input:
        tiers=os.path.join(QTL_COLOC_DIR, "tier_assignments.tsv"),
        l2g_dir=os.path.join(
            config["paths"]["data_root"], "raw", "opentargets", "l2g_prediction",
        ),
    output:
        concordance=os.path.join(QTL_COLOC_DIR, "l2g_concordance.tsv"),
    params:
        script=os.path.join("src", "python", "parse_l2g.py"),
    conda:
        QTL_PROC_ENV_COLOC
    shell:
        r"""
        python {params.script} \
          --l2g-dir {input.l2g_dir} \
          --tier-table {input.tiers} \
          --output {output.concordance}
        """


rule build_gene_tissue_matrix:
    """Build gene x tissue x cell-type matrix from all QTL coloc results.

    Produces both wide-format (heatmap-ready) and long-format (analysis-ready)
    tables. Columns combine tissue/cell_type with QTL source for unambiguous
    identification.
    """
    input:
        qtl_results=os.path.join(QTL_COLOC_DIR, "qtl_coloc_summary.tsv"),
    output:
        matrix=os.path.join(QTL_COLOC_DIR, "gene_tissue_matrix.tsv"),
        long_table=os.path.join(QTL_COLOC_DIR, "gene_tissue_long.tsv"),
    params:
        script=os.path.join("src", "python", "build_gene_tissue_matrix.py"),
    conda:
        QTL_PROC_ENV_COLOC
    shell:
        r"""
        python {params.script} \
          --input {input.qtl_results} \
          --output-matrix {output.matrix} \
          --output-long {output.long_table}
        """
