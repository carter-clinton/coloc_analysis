"""ta-r4 W2a EUR LD substrate (D-03, D-10, D-12a): variant catalogs, legacy-identical and R4 1000G EUR panels,
A2 matched identity payloads, k2d reproduction payloads. Infrastructure: no gate input (D-05).

Commands mirror src/snakemake/rules/ld_reference.smk collect_region_variants and build_ld_rds_1kg_eur.
"""

ONEKG_EUR_PREFIX_R4 = "data/r4/ref/1000G_EUR_Phase3_plink/1000G.EUR.QC"
PYTHON_BIN = sys.executable

# The 8 Track A sumstats in the legacy HARMONIZED_ALL order (Snakefile TRAIT_ANCESTRY_PAIRS).
TRACK_A_SUMSTATS = [(t, a) for t in config["traits"] for a in config["trait_ancestries"].get(t, [])]
if len(TRACK_A_SUMSTATS) != 8:
    raise WorkflowError(f"expected the 8 Track A sumstats, got {TRACK_A_SUMSTATS}")
CATALOG_SUMSTATS = {
    "legacy": [f"data/processed/sumstats_harmonized/{t}.{a}.tsv.bgz" for t, a in TRACK_A_SUMSTATS],
    "r4": [r4paths.sumstats_path(t, a, "A3_1kg") for t, a in TRACK_A_SUMSTATS],
}
CATALOG_REGIONS_CSV = {"legacy": config["paths"]["regions_curated"], "r4": r4paths.regions_csv()}

CURATED_REGIONS = [s for _, s in REGION_INFOS if not REGION_METADATA[s]["source"].startswith("negative_control")]
_AUTOSOMAL = {str(c) for c in range(1, 23)}
# build_ld_rds_1kg_eur eligibility: autosomal, not HLA_6p21 (BMI_Xq24 is chrX).
R4_PANEL_REGIONS = [s for _, s in REGION_INFOS if REGION_METADATA[s]["chr"] in _AUTOSOMAL and s != "HLA_6p21"]
LEGACY_PANEL_REGIONS = [s for s in R4_PANEL_REGIONS if s in CURATED_REGIONS]
K2D_ANCESTRIES = ("EUR", "AFR")  # make_identity_ld_refs.R ANCESTRIES

R4_CATALOG_TARGETS = [r4paths.catalog_path("legacy", s) for s in CURATED_REGIONS] + [
    r4paths.catalog_path("r4", s) for _, s in REGION_INFOS
]
R4_PANEL_TARGETS_EUR = (
    [r4paths.panel_path("repro_routeC", s, "EUR") for s in LEGACY_PANEL_REGIONS]
    + [r4paths.panel_path("A3_1kg", s) for s in R4_PANEL_REGIONS]
    + [r4paths.panel_path("A2_identity", s) for s in R4_PANEL_REGIONS]
)
R4_K2D_TARGETS = [r4paths.panel_path("repro_k2d_routeC", s, a) for a in K2D_ANCESTRIES for s in CURATED_REGIONS]


def _wc(regions):
    return "|".join(sorted(regions))


def _tpl(arm, ancestry=None):
    return r4paths.panel_template(arm, ancestry).replace("{region_safe}", "{region}")


def _panel_mem(w):
    m = REGION_METADATA[w.region]
    return 32000 if m["end"] - m["start"] >= 2_000_000 else 8000


def _bfile(w):
    return f"{ONEKG_EUR_PREFIX_R4}.{REGION_METADATA[w.region]['chr']}"


rule r4_w2a_all:
    input:
        R4_CATALOG_TARGETS,
        R4_PANEL_TARGETS_EUR,
        R4_K2D_TARGETS,


rule r4_catalog:
    input:
        harmonized=lambda w: CATALOG_SUMSTATS[w.route],
        regions=lambda w: CATALOG_REGIONS_CSV[w.route],
    output:
        "data/r4/ld/variants_{route}/{region}.tsv",
    wildcard_constraints:
        route="legacy|r4",
        region=_wc(s for _, s in REGION_INFOS),
    params:
        region_id=lambda w: REGION_SAFE_TO_ID[w.region],
    conda:
        str(Path(workflow.basedir) / "envs" / "python_stats.yml")
    threads: 1
    resources:
        mem_mb=8000,
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/collect_region_variants.py \
            --region-id {params.region_id} \
            --regions-csv {input.regions} \
            --harmonized {input.harmonized} \
            --output {output}
        """


rule r4_panel_eur_legacy:
    input:
        bed=lambda w: _bfile(w) + ".bed",
        bim=lambda w: _bfile(w) + ".bim",
        fam=lambda w: _bfile(w) + ".fam",
        rscript="src/snakemake/scripts/plink_ld_to_rds.R",
    output:
        rds=_tpl("repro_routeC", "EUR"),
    wildcard_constraints:
        region=_wc(LEGACY_PANEL_REGIONS),
    params:
        bfile=_bfile,
        chrom=lambda w: REGION_METADATA[w.region]["chr"],
        start=lambda w: REGION_METADATA[w.region]["start"],
        end=lambda w: REGION_METADATA[w.region]["end"],
        region_id=lambda w: REGION_SAFE_TO_ID[w.region],
        work_prefix=lambda w: f"data/r4/ld/work/legacy_repro_EUR/{w.region}",
    conda:
        str(Path(workflow.basedir) / "envs" / "plink.yml")
    threads: 1
    resources:
        mem_mb=_panel_mem,
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.rds}) $(dirname {params.work_prefix})
        plink \
            --bfile {params.bfile} \
            --chr {params.chrom} \
            --from-bp {params.start} \
            --to-bp {params.end} \
            --r square \
            --write-snplist \
            --make-just-bim \
            --out {params.work_prefix} \
            --threads {threads}
        Rscript {input.rscript} \
            --ld {params.work_prefix}.ld \
            --variants {params.work_prefix}.bim \
            --region-id {params.region_id} \
            --ancestry EUR \
            --ld-source onekg_phase3_eur_hm3 \
            --output {output.rds}
        (md5sum {params.work_prefix}.ld; stat -c '%s' {params.work_prefix}.ld) > {params.work_prefix}.ld.md5
        rm -f {params.work_prefix}.ld
        """


rule r4_panel_eur_1kg:
    input:
        bed=lambda w: _bfile(w) + ".bed",
        bim=lambda w: _bfile(w) + ".bim",
        fam=lambda w: _bfile(w) + ".fam",
        rscript="src/snakemake/scripts/plink_ld_to_rds.R",
    output:
        rds=_tpl("A3_1kg"),
    wildcard_constraints:
        region=_wc(R4_PANEL_REGIONS),
    params:
        bfile=_bfile,
        chrom=lambda w: REGION_METADATA[w.region]["chr"],
        start=lambda w: REGION_METADATA[w.region]["start"],
        end=lambda w: REGION_METADATA[w.region]["end"],
        region_id=lambda w: REGION_SAFE_TO_ID[w.region],
        work_prefix=lambda w: f"data/r4/ld/work/EUR_1kg_r4/{w.region}",
    conda:
        str(Path(workflow.basedir) / "envs" / "plink.yml")
    threads: 1
    resources:
        mem_mb=_panel_mem,
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.rds}) $(dirname {params.work_prefix})
        plink \
            --bfile {params.bfile} \
            --chr {params.chrom} \
            --from-bp {params.start} \
            --to-bp {params.end} \
            --keep-allele-order \
            --r square \
            --write-snplist \
            --make-just-bim \
            --out {params.work_prefix} \
            --threads {threads}
        Rscript {input.rscript} \
            --ld {params.work_prefix}.ld \
            --variants {params.work_prefix}.bim \
            --region-id {params.region_id} \
            --ancestry EUR \
            --ld-source onekg_phase3_eur_hm3_keep_allele_order \
            --emit-ref-alt true \
            --output {output.rds}
        (md5sum {params.work_prefix}.ld; stat -c '%s' {params.work_prefix}.ld) > {params.work_prefix}.ld.md5
        rm -f {params.work_prefix}.ld
        """


rule r4_identity_payload:
    input:
        panel=_tpl("A3_1kg"),
        script="src/snakemake/scripts/ta_r4/make_matched_identity_payload.R",
    output:
        _tpl("A2_identity"),
    wildcard_constraints:
        region=_wc(R4_PANEL_REGIONS),
    conda:
        str(Path(workflow.basedir) / "envs" / "r_coloc.yml")
    threads: 1
    resources:
        mem_mb=_panel_mem,
    shell:
        "Rscript {input.script} --in {input.panel} --out {output}"


rule r4_k2d_payload:
    input:
        variants=lambda w: r4paths.catalog_path("legacy", w.region),
        script="src/snakemake/scripts/ta_r4/make_k2d_payload.R",
    output:
        "data/r4/ld/k2d_identity/{ancestry}/{region}.rds",
    wildcard_constraints:
        ancestry="EUR|AFR",
        region=_wc(CURATED_REGIONS),
    conda:
        str(Path(workflow.basedir) / "envs" / "r_coloc.yml")
    threads: 1
    resources:
        mem_mb=8000,
    shell:
        "Rscript {input.script} --variants {input.variants} --out {output}"
