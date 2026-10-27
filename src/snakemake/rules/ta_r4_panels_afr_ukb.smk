"""ta-r4 W2b: AFR 1000G panels (D-20; 661 primary, 504 sensitivity), AFR661 matched identity payloads,
legacy AFR reproduction panels (build_ld_rds semantics), and the UKB 337k EUR sensitivity panels (D-03, D-04, E6).
Infrastructure: no gate input (D-05). Included after ta_r4_panels.smk (sorted), which defines the shared helpers.
"""

ONEKG_VCF_R4 = "data/r4/inputs/1kg_vcf"  # symlink to the /rs1 1000G Phase 3 VCFs (GRCh37)
AFR_SAMPLES = {"AFR661_1kg_r4": "data/r4/ref/samples/AFR661.samples", "AFR504_1kg_r4": "data/r4/ref/samples/AFR504.samples"}

# AFR-admissible regions (pair_manifest AFR admissible rows): the 10 curated autosomal regions.
AFR_PANEL_REGIONS = sorted(
    {r["region_safe"] for r in PAIR_ROWS if r["ancestry"] == "AFR" and r["admissible"] == "true"}
)
# Legacy AFR reproduction: every region of the frozen 36 AFR fits (3 traits x 12 curated regions).
LEGACY_AFR_REGIONS = CURATED_REGIONS

R4_AFR_TARGETS = (
    [r4paths.panel_path(a, s) for a in ("AFR661_A3", "AFR504_A3", "AFR661_A2") for s in AFR_PANEL_REGIONS]
    + [r4paths.panel_path("repro_routeC", s, "AFR") for s in LEGACY_AFR_REGIONS]
)


def _vcf(w):
    return f"{ONEKG_VCF_R4}/chr{REGION_METADATA[w.region]['chr']}.vcf.gz"


rule r4_w2b_afr_all:
    input:
        R4_AFR_TARGETS,


rule r4_panel_afr_1kg:
    input:
        vcf=_vcf,
        tbi=lambda w: _vcf(w) + ".tbi",
        samples=lambda w: AFR_SAMPLES[w.panel],
        catalog=lambda w: r4paths.catalog_path("r4", w.region),
        rscript="src/snakemake/scripts/plink_ld_to_rds.R",
    output:
        rds="data/r4/ld/{panel}/{region}.rds",
    wildcard_constraints:
        panel="AFR661_1kg_r4|AFR504_1kg_r4",
        region=_wc(AFR_PANEL_REGIONS),
    params:
        chrom=lambda w: REGION_METADATA[w.region]["chr"],
        start=lambda w: REGION_METADATA[w.region]["start"],
        end=lambda w: REGION_METADATA[w.region]["end"],
        region_id=lambda w: REGION_SAFE_TO_ID[w.region],
        work_prefix=lambda w: f"data/r4/ld/work/{w.panel}/{w.region}",
    conda:
        str(Path(workflow.basedir) / "envs" / "plink.yml")
    threads: 1
    resources:
        mem_mb=32000,
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.rds}) $(dirname {params.work_prefix})
        awk -F'\t' 'NR > 1 {{ print $1 "\t" $2 "\t" $2 "\t" $1 ":" $2 }}' {input.catalog} | sort -u > {params.work_prefix}.range.txt
        plink \
            --vcf {input.vcf} \
            --keep {input.samples} \
            --chr {params.chrom} \
            --from-bp {params.start} \
            --to-bp {params.end} \
            --snps-only just-acgt \
            --biallelic-only strict \
            --maf 0.01 \
            --set-missing-var-ids '@:#:$1:$2' \
            --extract range {params.work_prefix}.range.txt \
            --keep-allele-order \
            --r square \
            --make-just-bim \
            --make-just-fam \
            --write-snplist \
            --out {params.work_prefix} \
            --threads {threads}
        Rscript {input.rscript} \
            --ld {params.work_prefix}.ld \
            --variants {params.work_prefix}.bim \
            --region-id {params.region_id} \
            --ancestry AFR \
            --ld-source onekg_phase3_{wildcards.panel} \
            --emit-ref-alt true \
            --output {output.rds}
        (md5sum {params.work_prefix}.ld; stat -c '%s' {params.work_prefix}.ld) > {params.work_prefix}.ld.md5
        rm -f {params.work_prefix}.ld
        """


rule r4_identity_payload_afr:
    input:
        panel=r4paths.panel_template("AFR661_A3").replace("{region_safe}", "{region}"),
        script="src/snakemake/scripts/ta_r4/make_matched_identity_payload.R",
    output:
        r4paths.panel_template("AFR661_A2").replace("{region_safe}", "{region}"),
    wildcard_constraints:
        region=_wc(AFR_PANEL_REGIONS),
    conda:
        str(Path(workflow.basedir) / "envs" / "r_coloc.yml")
    threads: 1
    resources:
        mem_mb=32000,
    shell:
        "Rscript {input.script} --in {input.panel} --out {output}"


rule r4_panel_afr_legacy:
    # ld_reference.smk build_ld_rds, verbatim semantics: VCF route, AFR.samples (504), the legacy pooled catalog,
    # LD_MAX_VARIANTS unset (default 6000 -> use_identity placeholder above it).
    input:
        vcf=_vcf,
        tbi=lambda w: _vcf(w) + ".tbi",
        samples=AFR_SAMPLES["AFR504_1kg_r4"],
        variants=lambda w: r4paths.catalog_path("legacy", w.region),
    output:
        _tpl("repro_routeC", "AFR"),
    wildcard_constraints:
        region=_wc(LEGACY_AFR_REGIONS),
    params:
        chrom=lambda w: REGION_METADATA[w.region]["chr"],
        start=lambda w: REGION_METADATA[w.region]["start"],
        end=lambda w: REGION_METADATA[w.region]["end"],
        region_id=lambda w: REGION_SAFE_TO_ID[w.region],
    conda:
        str(Path(workflow.basedir) / "envs" / "r_coloc.yml")
    threads: 1
    resources:
        mem_mb=8000,
    shell:
        r"""
        set -euo pipefail
        unset LD_MAX_VARIANTS
        {PYTHON_BIN} src/legacy/region_analysis/scripts/build_ld_rds.py \
            --vcf {input.vcf} \
            --samples {input.samples} \
            --chrom {params.chrom} \
            --start {params.start} \
            --end {params.end} \
            --region-id {params.region_id} \
            --ancestry AFR \
            --output {output} \
            --rscript Rscript \
            --variant-list {input.variants}
        """


# --- UKB 337k EUR sensitivity panels (D-03, D-04, E6): native, isect (oriented to EUR_1kg_r4), matched 1000G isect ---
from ta_r4 import ukb337k_tiles as r4ukb

UKB_ISECT_REGIONS = R4_PANEL_REGIONS  # 10 admissible + 19 NC
UKB_NATIVE_REGIONS = R4_PANEL_REGIONS + ["HLA_6p21"]  # HLA: exploratory fits only (D-24)
UKB_STATS = "data/r4/ld/work/ukb337k/{kind}/{region}.stats.tsv"

R4_UKB_TARGETS = (
    [r4paths.panel_path("A3_ukb", s) for s in UKB_NATIVE_REGIONS]
    + [r4paths.panel_path(a, s) for a in ("A3_ukb_isect", "A3_1kg_isect") for s in UKB_ISECT_REGIONS]
)


def _ukb_tiles(w):
    m = REGION_METADATA[w.region]
    return [str(p) for t in r4ukb.region_tiles(m["chr"], m["start"], m["end"]) for p in t]


rule r4_w2b_ukb_all:
    input:
        R4_UKB_TARGETS,


rule r4_panel_ukb_native:
    input:
        tiles=_ukb_tiles,
        catalog=lambda w: r4paths.catalog_path("r4", w.region),
        code="src/python/ta_r4/ukb337k_tiles.py",
    output:
        rds=_tpl("A3_ukb"),
        stats=UKB_STATS.replace("{kind}", "native"),
    wildcard_constraints:
        region=_wc(UKB_NATIVE_REGIONS),
    params:
        chrom=lambda w: REGION_METADATA[w.region]["chr"],
        start=lambda w: REGION_METADATA[w.region]["start"],
        end=lambda w: REGION_METADATA[w.region]["end"],
        region_id=lambda w: REGION_SAFE_TO_ID[w.region],
    conda:
        str(Path(workflow.basedir) / "envs" / "r_coloc.yml")
    threads: 1
    resources:
        mem_mb=48000,
    shell:
        r"""
        PYTHONPATH=src/python {PYTHON_BIN} -m ta_r4.ukb337k_tiles build-native \
            --region-id {params.region_id} --region-safe {wildcards.region} \
            --chr {params.chrom} --start {params.start} --end {params.end} \
            --catalog {input.catalog} --out {output.rds} --stats {output.stats}
        """


rule r4_panel_ukb_isect:
    input:
        tiles=_ukb_tiles,
        ref=_tpl("A3_1kg"),
        code="src/python/ta_r4/ukb337k_tiles.py",
    output:
        ukb=_tpl("A3_ukb_isect"),
        onekg=_tpl("A3_1kg_isect"),
        stats=UKB_STATS.replace("{kind}", "isect"),
    wildcard_constraints:
        region=_wc(UKB_ISECT_REGIONS),
    params:
        chrom=lambda w: REGION_METADATA[w.region]["chr"],
        start=lambda w: REGION_METADATA[w.region]["start"],
        end=lambda w: REGION_METADATA[w.region]["end"],
        region_id=lambda w: REGION_SAFE_TO_ID[w.region],
    conda:
        str(Path(workflow.basedir) / "envs" / "r_coloc.yml")
    threads: 1
    resources:
        mem_mb=32000,
    shell:
        r"""
        PYTHONPATH=src/python {PYTHON_BIN} -m ta_r4.ukb337k_tiles build-isect \
            --region-id {params.region_id} --region-safe {wildcards.region} \
            --chr {params.chrom} --start {params.start} --end {params.end} \
            --ref-panel {input.ref} --out-ukb {output.ukb} --out-1kg {output.onekg} --stats {output.stats}
        """
