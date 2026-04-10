#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-la_multitrait_project}"

echo "Creating project at: ${PROJECT_ROOT}"
mkdir -p "${PROJECT_ROOT}"

# ----------------------------------------------------------------------
# Directory structure
# ----------------------------------------------------------------------
mkdir -p "${PROJECT_ROOT}"/{config,envs,data_raw/1kg,data_raw/sumstats,data_raw/misc,data_processed/sumstats_harmonized,data_processed/ld_reference,data_processed/regions,scripts,workflow/rules,logs,results/regions,results/multitrait,results/pgs,results/mr}

# ----------------------------------------------------------------------
# Conda envs
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/envs/snakemake_env.yml"
name: la_multitrait
channels:
  - conda-forge
  - bioconda
  - defaults
dependencies:
  - python=3.11
  - snakemake==8.*
  - pandas
  - numpy
  - scipy
  - pyarrow
  - cytoolz
  - pyyaml
  - click
  - requests
  - pip
  - plink
  - bcftools
  - pip:
      - loguru
EOF

cat << 'EOF' > "${PROJECT_ROOT}/envs/r_stats_env.yml"
name: la_multitrait_r
channels:
  - conda-forge
  - bioconda
  - defaults
dependencies:
  - r-base
  - r-data.table
  - r-tidyverse
  - r-optparse
  - r-susieR
  - r-coloc
EOF

cat << 'EOF' > "${PROJECT_ROOT}/envs/plink_env.yml"
name: la_multitrait_plink
channels:
  - bioconda
  - conda-forge
  - defaults
dependencies:
  - plink
  - bcftools
EOF

# ----------------------------------------------------------------------
# Config files
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/config/config.yaml"
traits:
  - bmi
  - t2d
  - hypertension
  - asthma
  - stroke

ancestries:
  - EUR
  - AFR

# build for coordinates
genome_build: GRCh37   # or GRCh38; we'll harmonize everything consistently

# where files live (relative to project_root)
paths:
  raw_sumstats: "data_raw/sumstats"
  harmonized_sumstats: "data_processed/sumstats_harmonized"
  regions_curated: "config/regions_curated.csv"
  regions_bed: "data_processed/regions/regions.bed"
  ld_1kg_root: "data_raw/1kg"
  ld_reference: "data_processed/ld_reference"

# 1000 Genomes setup for LD
onekg:
  version: phase3
  populations:
    AFR: ["YRI", "LWK", "GWD", "MSL", "ESN"]
    EUR: ["CEU", "TSI", "GBR", "FIN", "IBS"]
  chromosomes:
    - "1"
    - "2"
    - "3"
    - "4"
    - "5"
    - "6"
    - "7"
    - "8"
    - "9"
    - "10"
    - "11"
    - "12"
    - "13"
    - "14"
    - "15"
    - "16"
    - "17"
    - "18"
    - "19"
    - "20"
    - "21"
    - "22"
  ftp_base: "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502"
  vcf_template: "ALL.chr{chrom}.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz"
  panel_url: "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/integrated_call_samples_v3.20130502.ALL.panel"

# plink / bcftools params
plink:
  maf: 0.01
  geno: 0.01

resources:
  default_threads: 4
  default_mem_mb: 8000
#
# Preferred dataset source per trait
dataset_priority:
  bmi: yengo2018_bmi
  t2d: diamante2022_t2d
  hypertension: evangelou2018_bp
  asthma: gbmi_asthma
  stroke: megastroke_metastroke

multitrait:
  methods:
    - mashr
    - susie
  window_kb: 500
  region_padding_kb: 50

pgs:
  methods:
    - prs_csx
    - ldpred2
  target_ancestries:
    - EUR
    - AFR
  ld_reference_dir: "data_processed/ld_reference"

mr:
  hypotheses:
    - exposure: bmi
      outcome: t2d
      note: "BMI -> T2D causal hypothesis"
    - exposure: bmi
      outcome: hypertension
      note: "BMI -> hypertension"
    - exposure: hypertension
      outcome: stroke
      note: "BP -> stroke mediation"

trait_ancestries:
  bmi:
    - EUR
  t2d:
    - EUR
    - TRANS
  hypertension:
    - EUR
  asthma:
    - EUR
    - AFR
  stroke:
    - EUR
EOF

cat << 'EOF' > "${PROJECT_ROOT}/config/datasets.yaml"
datasets:
  gbmi_asthma:
    description: "GBMI asthma summary statistics (May 2021 release)."
    base_url: "https://gbmi-sumstats.s3.amazonaws.com"
    defaults:
      compression: "gzip"
      sep: "\t"
      column_map:
        CHR: ["CHR", "chr"]
        POS: ["POS", "pos"]
        REF: ["REF", "NEA", "non_effect_allele"]
        ALT: ["ALT", "EA", "effect_allele"]
        BETA: ["BETA", "beta"]
        SE: ["SE", "se"]
        P: ["P", "pval", "p_value"]
        EAF: ["EAF", "af", "effect_allele_frequency"]
    traits:
      asthma:
        ancestries:
          EUR:
            path: "Asthma_Bothsex_eur_inv_var_meta_GBMI_052021_nbbkgt1.txt.gz"
            md5: ""
          AFR:
            path: "Asthma_Bothsex_afr_inv_var_meta_GBMI_052021_nbbkgt1.txt.gz"
            md5: ""

  yengo2018_bmi:
    description: "Yengo et al. 2018 BMI meta-analysis."
    base_url: "https://cnsgenomics.com/data/yengo_et_al_2018_hmg"
    defaults:
      compression: "gzip"
      sep: "\t"
      column_map:
        CHR: ["CHR", "chr"]
        POS: ["BP", "POS", "bp"]
        REF: ["A2", "NEA"]
        ALT: ["A1", "EA"]
        BETA: ["b", "BETA"]
        SE: ["se", "SE"]
        P: ["p", "P"]
        EAF: ["Freq1", "EAF", "freq1"]
        N: ["N", "n_total"]
    traits:
      bmi:
        ancestries:
          EUR:
            path: "Meta-analysis_Locke_et_al%2BUKBiobank_2018_UPDATED.txt.gz"
            md5: ""

  diamante2022_t2d:
    description: "DIAMANTE 2022 T2D summary statistics."
    base_url: "https://diagram-consortium.org/downloads"
    defaults:
      compression: "gzip"
      sep: "\t"
      column_map:
        CHR: ["chr", "CHR"]
        POS: ["pos", "POS"]
        REF: ["nea", "REF", "non_effect_allele"]
        ALT: ["ea", "ALT", "effect_allele"]
        BETA: ["beta", "BETA"]
        SE: ["se", "SE"]
        P: ["pval", "P", "p_value"]
        EAF: ["eaf", "EAF"]
    traits:
      t2d:
        ancestries:
          EUR:
            path: "DIAMANTE-EUR.sumstat.txt.gz"
            md5: ""
          TRANS:
            path: "DIAMANTE-TA.sumstat.txt.gz"
            md5: ""

  evangelou2018_bp:
    description: "Evangelou et al. 2018 UKB+ICBP blood pressure meta-analysis."
    base_url: "https://grasp.nhlbi.nih.gov/downloads/ResultsAug2019/2018/Evangelou"
    defaults:
      compression: "gzip"
      sep: "\t"
      column_map:
        CHR: ["CHR", "chr"]
        POS: ["BP", "POS"]
        REF: ["REF_ALLELE", "NEA", "non_effect_allele"]
        ALT: ["EFFECT_ALLELE", "EA", "effect_allele"]
        BETA: ["BETA", "beta"]
        SE: ["SE", "se"]
        P: ["PVAL", "pvalue", "p"]
        EAF: ["EAF", "effect_allele_frequency"]
    traits:
      hypertension:
        note: "Systolic blood pressure meta-analysis proxy for hypertension risk."
        ancestries:
          EUR:
            path: "UKB-ICBPmeta750k_SBPsummaryResults.txt.gz"
            md5: ""

  megastroke_metastroke:
    description: "METASTROKE / MEGASTROKE ischemic stroke results (Traylor 2012)."
    base_url: "https://personal.broadinstitute.org/ryank"
    defaults:
      compression: "infer"
      sep: "\t"
      column_map:
        CHR: ["chr", "CHR"]
        POS: ["pos", "POS", "bp"]
        REF: ["ref", "a2", "NEA"]
        ALT: ["alt", "a1", "EA"]
        BETA: ["beta", "BETA"]
        SE: ["se", "SE"]
        P: ["p", "P"]
    traits:
      stroke:
        ancestries:
          EUR:
            path: "3490334.Traylor.2012.zip"
            md5: ""
            zip_member: ""
EOF

cat << 'EOF' > "${PROJECT_ROOT}/config/regions_curated.csv"
region_id,chr,start,end,lead_snp,gene,trait_list,source
FTO_16q12,16,53800000,54400000,rs9939609,FTO,"bmi;t2d;htn",GIANT
MC4R_18q21,18,56000000,56600000,rs17782313,MC4R,"bmi;t2d",GIANT
SH2B3_12q24,12,111400000,112000000,rs3184504,SH2B3,"htn;stroke;cad",BP_meta
APOL1_22q12,22,36200000,36600000,G1/G2,APOL1,"htn;ckd;stroke?",APOL1_literature
PYHIN1_1q23,1,158000000,162000000,rsX,PYHIN1,"asthma",CAAPA
CXADR_F2RL1_6p21,6,10300000,11800000,NA,"CXADR/F2RL1","htn;obesity",AA_admixture
BMI_5q13.3,5,72000000,76000000,NA,NA,"bmi",AA_admixture
BMI_Xq24,X,118000000,122000000,NA,NA,"bmi",AA_admixture
EOF

cat << 'EOF' > "${PROJECT_ROOT}/config/cluster_lsf.yaml"
# LSF cluster configuration for Snakemake on NCSU cluster.
# Tune queue, time, and mem_mb to your environment.

__default__:
  queue: "short"      # TODO: replace with your actual queue
  time: "04:00"       # walltime HH:MM
  mem_mb: 8000
  threads: 4

download_sumstats:
  time: "02:00"
  mem_mb: 4000
  threads: 1

harmonize_sumstats:
  time: "04:00"
  mem_mb: 8000
  threads: 2

make_regions_from_loci:
  time: "01:00"
  mem_mb: 2000
  threads: 1

prepare_ld_plink:
  time: "24:00"
  mem_mb: 32000
  threads: 4
EOF

# ----------------------------------------------------------------------
# Main Snakefile (in workflow/)
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/workflow/Snakefile"
import os
import yaml

# Path is relative to the working directory (project root)
configfile: "config/config.yaml"

TRAITS = config["traits"]
ANCESTRIES = config["ancestries"]
TRAIT_ANCESTRIES = config.get("trait_ancestries")
TRAIT_ANCESTRY_PAIRS = []
if TRAIT_ANCESTRIES:
    for trait in TRAITS:
        ancestries = TRAIT_ANCESTRIES.get(trait, ANCESTRIES)
        for anc in ancestries:
            TRAIT_ANCESTRY_PAIRS.append((trait, anc))
else:
    for trait in TRAITS:
        for anc in ANCESTRIES:
            TRAIT_ANCESTRY_PAIRS.append((trait, anc))

HARMONIZED_ALL = [
    os.path.join(
        config["paths"]["harmonized_sumstats"],
        f"{trait}.{ancestry}.tsv.bgz"
    )
    for trait, ancestry in TRAIT_ANCESTRY_PAIRS
]

# include modular rule files; paths are relative to this Snakefile (workflow/)
include: "rules/sumstats.smk"
include: "rules/regions.smk"
include: "rules/ld_reference.smk"
include: "rules/multitrait.smk"
include: "rules/pgs.smk"
include: "rules/mr.smk"
include: "rules/qc.smk"

rule all:
    input:
        HARMONIZED_ALL,
        # curated regions BED
        config["paths"]["regions_bed"],
        # LD reference 'index marker' files per ancestry
        expand(
            os.path.join(
                config["paths"]["ld_reference"],
                "{ancestry}.ldindex"
            ),
            ancestry=ANCESTRIES,
        ),
        "results/multitrait/harmonized_manifest.tsv",
        "results/pgs/pgs_manifest.tsv",
        "results/mr/mr_manifest.tsv",
        "results/qc/harmonized_summary.tsv",
        "results/multitrait/placeholder.done",
        "results/pgs/placeholder.done",
        "results/mr/placeholder.done"
EOF

# ----------------------------------------------------------------------
# Rules: summary stats download + harmonization
# ----------------------------------------------------------------------
cat << 'SUMSTATS' > "${PROJECT_ROOT}/workflow/rules/sumstats.smk"
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.dataset_config import dataset_descriptor

DATASETS_CONFIG_PATH = os.path.join("config", "datasets.yaml")

def raw_sumstats_path(wildcards):
    return os.path.join(
        config["paths"]["raw_sumstats"],
        f"{wildcards.trait}.{wildcards.ancestry}.raw.gz"
    )

def harmonized_sumstats_path(wildcards):
    return os.path.join(
        config["paths"]["harmonized_sumstats"],
        f"{wildcards.trait}.{wildcards.ancestry}.tsv.bgz"
    )

def dataset_meta(wildcards):
    return dataset_descriptor(
        trait=wildcards.trait,
        ancestry=wildcards.ancestry,
        config_path=DATASETS_CONFIG_PATH,
        dataset_priority=config.get("dataset_priority", {}),
    )

rule download_sumstats:
    output:
        raw=raw_sumstats_path
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    run:
        import hashlib
        import requests

        os.makedirs(config["paths"]["raw_sumstats"], exist_ok=True)
        meta = dataset_meta(wildcards)
        tmp_path = Path(str(output.raw) + ".tmp")
        with requests.get(meta["url"], stream=True) as resp:
            resp.raise_for_status()
            with open(tmp_path, "wb") as handle:
                for chunk in resp.iter_content(chunk_size=1 << 19):
                    if chunk:
                        handle.write(chunk)

        expected_md5 = (meta.get("md5") or "").strip()
        if expected_md5:
            hasher = hashlib.md5()
            with open(tmp_path, "rb") as handle:
                for chunk in iter(lambda: handle.read(8192), b""):
                    if not chunk:
                        break
                    hasher.update(chunk)
            digest = hasher.hexdigest()
            if digest.lower() != expected_md5.lower():
                raise ValueError(
                    f"MD5 mismatch for {meta['url']}: expected {expected_md5}, observed {digest}"
                )

        tmp_path.replace(output.raw)

rule harmonize_sumstats:
    input:
        raw=raw_sumstats_path
    output:
        harmonized=harmonized_sumstats_path
    conda:
        "../../envs/snakemake_env.yml"
    threads: 2
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    params:
        dataset_name=lambda wildcards: dataset_meta(wildcards)["dataset"],
        datasets_config=DATASETS_CONFIG_PATH,
    shell:
        r"""
        mkdir -p {config["paths"]["harmonized_sumstats"]}
        python scripts/harmonize_sumstats.py \
            --input {input.raw} \
            --output {output.harmonized} \
            --trait {wildcards.trait} \
            --ancestry {wildcards.ancestry} \
            --build {config["genome_build"]} \
            --dataset-name {params.dataset_name} \
            --datasets-config {params.datasets_config}
        tabix -f -s 1 -b 2 -e 2 {output.harmonized}
        """
SUMSTATS

# ----------------------------------------------------------------------
# Rules: region definitions from curated loci (incl. APOL1)
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/workflow/rules/regions.smk"
rule make_regions_from_loci:
    input:
        loci=config["paths"]["regions_curated"]
    output:
        bed=config["paths"]["regions_bed"]
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        mkdir -p "$(dirname {output.bed})"
        python scripts/make_regions_from_loci.py \
            --input {input.loci} \
            --output {output.bed}
        """
EOF

# ----------------------------------------------------------------------
# Rules: 1000 Genomes LD reference (AFR/EUR)
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/workflow/rules/ld_reference.smk"
import os

CHROMOSOMES = config["onekg"].get(
    "chromosomes",
    [str(chrom) for chrom in range(1, 23)],
)
CHROM_STRING = " ".join(CHROMOSOMES)


def vcf_path(chrom):
    return os.path.join(
        config["paths"]["ld_1kg_root"],
        "vcf",
        f"chr{chrom}.vcf.gz",
    )


def vcf_tbi_path(chrom):
    return vcf_path(chrom) + ".tbi"


def sample_list_path(ancestry):
    return os.path.join(
        config["paths"]["ld_1kg_root"],
        f"{ancestry}.samples",
    )


def ld_index_path(ancestry):
    return os.path.join(
        config["paths"]["ld_reference"],
        f"{ancestry}.ldindex",
    )


rule download_1kg_panel:
    output:
        panel=os.path.join(
            config["paths"]["ld_1kg_root"],
            "integrated_call_samples.panel",
        )
    params:
        url=config["onekg"].get("panel_url")
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        set -euo pipefail
        mkdir -p {config["paths"]["ld_1kg_root"]}
        curl -L "{params.url}" -o {output.panel}
        """


rule download_1kg_vcf:
    output:
        vcf=lambda wildcards: vcf_path(wildcards.chrom),
        tbi=lambda wildcards: vcf_tbi_path(wildcards.chrom)
    params:
        url=lambda wildcards: "{base}/{fname}".format(
            base=config["onekg"].get("ftp_base", "").rstrip("/"),
            fname=config["onekg"]
            .get(
                "vcf_template",
                "ALL.chr{chrom}.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
            )
            .format(chrom=wildcards.chrom),
        )
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.vcf})
        curl -L "{params.url}" -o {output.vcf}
        curl -L "{params.url}.tbi" -o {output.tbi}
        """


rule build_1kg_sample_lists:
    input:
        panel=os.path.join(
            config["paths"]["ld_1kg_root"],
            "integrated_call_samples.panel",
        )
    output:
        expand(
            sample_list_path(ancestry),
            ancestry=config["ancestries"],
        )
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        python scripts/build_1kg_sample_lists.py \
            --panel {input.panel} \
            --config config/config.yaml \
            --output-dir {config["paths"]["ld_1kg_root"]}
        """


rule prepare_ld_plink:
    input:
        vcfs=[vcf_path(chrom) for chrom in CHROMOSOMES],
        tbi=[vcf_tbi_path(chrom) for chrom in CHROMOSOMES],
        samples=[sample_list_path(ancestry) for ancestry in config["ancestries"]]
    output:
        [ld_index_path(ancestry) for ancestry in config["ancestries"]]
    conda:
        "../../envs/plink_env.yml"
    threads: config["resources"]["default_threads"]
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        set -euo pipefail
        mkdir -p {config["paths"]["ld_reference"]}

        for ANC in {" ".join(config["ancestries"])}; do
          SAMPLE_FILE={config["paths"]["ld_1kg_root"]}/$ANC.samples
          OUT_DIR={config["paths"]["ld_reference"]}/$ANC
          mkdir -p "$OUT_DIR"
          INDEX_FILE={config["paths"]["ld_reference"]}/$ANC.ldindex
          : > "$INDEX_FILE"

          for CHR in {CHROM_STRING}; do
            PREFIX=$OUT_DIR/chr${{CHR}}
            plink \
              --vcf {config["paths"]["ld_1kg_root"]}/vcf/chr${{CHR}}.vcf.gz \
              --keep "$SAMPLE_FILE" \
              --maf {config["plink"]["maf"]} \
              --geno {config["plink"]["geno"]} \
              --make-bed \
              --out "$PREFIX"

            echo "${{PREFIX}}.bed" >> "$INDEX_FILE"
          done
        done
        """
EOF

# ----------------------------------------------------------------------
# Rules: multitrait planning
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/workflow/rules/multitrait.smk"
rule build_multitrait_manifest:
    input:
        harmonized=HARMONIZED_ALL,
        regions=config["paths"]["regions_curated"]
    output:
        manifest="results/multitrait/harmonized_manifest.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        python scripts/create_multitrait_manifest.py \
            --harmonized {input.harmonized} \
            --regions {input.regions} \
            --output {output.manifest}
        """
        

rule run_multitrait_placeholder:
    input:
        manifest="results/multitrait/harmonized_manifest.tsv"
    output:
        done="results/multitrait/placeholder.done"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        python - <<'PY'
import pandas as pd
from pathlib import Path
df = pd.read_csv("{input.manifest}", sep="\t")
print(f"[multitrait] Planned regions: {df['region_count'].iloc[0] if not df.empty else 0}; comparisons: {len(df)}")
Path("{output.done}").write_text("multitrait placeholder complete\n")
PY
        """
EOF

# ----------------------------------------------------------------------
# Rules: cross-ancestry PGS planning
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/workflow/rules/pgs.smk"
rule build_pgs_manifest:
    input:
        harmonized=HARMONIZED_ALL
    output:
        manifest="results/pgs/pgs_manifest.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        python scripts/create_pgs_manifest.py \
            --harmonized {input.harmonized} \
            --config config/config.yaml \
            --output {output.manifest}
        """


rule run_pgs_placeholder:
    input:
        manifest="results/pgs/pgs_manifest.tsv"
    output:
        done="results/pgs/placeholder.done"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        python - <<'PY'
import pandas as pd
from pathlib import Path
df = pd.read_csv("{input.manifest}", sep="\t")
counts = df.groupby(["method", "target_ancestry"]).size().to_dict()
print(f"[pgs] Jobs queued: {len(df)} :: breakdown {counts}")
Path("{output.done}").write_text("pgs placeholder complete\n")
PY
        """
EOF

# ----------------------------------------------------------------------
# Rules: Mendelian randomization planning
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/workflow/rules/mr.smk"
rule build_mr_manifest:
    input:
        harmonized=HARMONIZED_ALL
    output:
        manifest="results/mr/mr_manifest.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        python scripts/create_mr_design.py \
            --harmonized {input.harmonized} \
            --config config/config.yaml \
            --output {output.manifest}
        """


rule run_mr_placeholder:
    input:
        manifest="results/mr/mr_manifest.tsv"
    output:
        done="results/mr/placeholder.done"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        python - <<'PY'
import pandas as pd
from pathlib import Path
df = pd.read_csv("{input.manifest}", sep="\t")
ready = df[df["status"] == "ready"]
print(f"[mr] Total hypotheses: {len(df)}; ready: {len(ready)}")
Path("{output.done}").write_text("mr placeholder complete\n")
PY
        """
EOF

# ----------------------------------------------------------------------
# Rules: harmonized QC
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/workflow/rules/qc.smk"
rule summarize_harmonized_sumstats:
    input:
        harmonized=HARMONIZED_ALL
    output:
        report="results/qc/harmonized_summary.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        python scripts/qc_harmonized_sumstats.py \
            --harmonized {input.harmonized} \
            --output {output.report}
        """
EOF

# ----------------------------------------------------------------------
# Scripts: harmonize_sumstats.py
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/scripts/harmonize_sumstats.py"
#!/usr/bin/env python
import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.dataset_config import dataset_descriptor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--trait", required=True)
    parser.add_argument("--ancestry", required=True)
    parser.add_argument("--build", required=True)
    parser.add_argument("--dataset-name", required=False, default=None)
    parser.add_argument(
        "--datasets-config",
        required=False,
        default="config/datasets.yaml",
    )
    return parser.parse_args()


def to_rename_pairs(column_map: Dict[str, Any], columns: List[str]) -> Dict[str, str]:
    rename_pairs: Dict[str, str] = {}
    lookup = {col.lower(): col for col in columns}
    for target, source in column_map.items():
        candidates = source if isinstance(source, (list, tuple)) else [source]
        for candidate in candidates:
            if not candidate:
                continue
            match = lookup.get(str(candidate).lower())
            if match:
                rename_pairs[match] = target
                break
    return rename_pairs


def main():
    args = parse_args()
    meta = dataset_descriptor(
        trait=args.trait,
        ancestry=args.ancestry,
        config_path=args.datasets_config,
        dataset_name=args.dataset_name,
    )

    sep = meta.get("sep", "\t")
    compression = meta.get("compression")
    if compression in (None, "", "none", "None"):
        compression = None
    elif compression == "infer":
        compression = "infer"

    logger.info(
        f"Reading {args.input} with sep='{sep}' compression='{compression}' "
        f"(dataset={meta['dataset']})"
    )
    df = pd.read_csv(args.input, sep=sep, compression=compression)

    rename_pairs = to_rename_pairs(meta.get("column_map", {}), df.columns.tolist())
    if rename_pairs:
        logger.info(f"Applying rename map: {rename_pairs}")
        df = df.rename(columns=rename_pairs)

    mandatory = ["CHR", "POS"]
    missing = [col for col in mandatory if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns {missing} after harmonization step for "
            f"trait={args.trait}, ancestry={args.ancestry}"
        )

    keep_cols = [
        col for col in
        ["CHR", "POS", "REF", "ALT", "BETA", "SE", "P", "EAF", "N"]
        if col in df.columns
    ]
    harmonized = df[keep_cols].copy()
    harmonized["TRAIT"] = args.trait
    harmonized["ANCESTRY"] = args.ancestry
    harmonized["BUILD"] = args.build

    logger.info(f"Writing harmonized output to {args.output}")
    harmonized.to_csv(args.output, sep="\t", index=False, compression="gzip")


if __name__ == "__main__":
    main()
EOF
chmod +x "${PROJECT_ROOT}/scripts/harmonize_sumstats.py"

# ----------------------------------------------------------------------
# Scripts: make_regions_from_loci.py
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/scripts/make_regions_from_loci.py"
#!/usr/bin/env python
import argparse
import pandas as pd

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--pad_kb", type=int, default=250, help="Padding if start/end are missing")
    args = p.parse_args()

    loci = pd.read_csv(args.input)

    def infer_coords(row):
        if pd.notnull(row.get("start")) and pd.notnull(row.get("end")):
            return int(row["start"]), int(row["end"])
        # fallback: ±pad_kb around lead SNP position, if you add it later
        raise ValueError("start/end missing and no fallback logic implemented yet for row: {}".format(row.get("region_id", "")))

    starts, ends = zip(*[infer_coords(r) for _, r in loci.iterrows()])
    loci["start"] = starts
    loci["end"] = ends

    # BED is 0-based, half-open
    bed = loci[["chr", "start", "end", "region_id"]].copy()
    bed["chr"] = bed["chr"].astype(str).str.replace("^chr", "", regex=True)

    bed.to_csv(args.output, sep="\t", header=False, index=False)

if __name__ == "__main__":
    main()
EOF
chmod +x "${PROJECT_ROOT}/scripts/make_regions_from_loci.py"

# ----------------------------------------------------------------------
# Scripts: compute_ld_plink.sh (helper, not wired yet)
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/scripts/compute_ld_plink.sh"
#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 4 ]]; then
  echo "Usage: $0 <1kg_vcf.gz> <sample_list> <out_prefix> <maf> [geno]" >&2
  exit 1
fi

VCF="$1"
SAMPLES="$2"
OUT="$3"
MAF="$4"
GENO="${5:-0.01}"

plink \
  --vcf "${VCF}" \
  --keep "${SAMPLES}" \
  --maf "${MAF}" \
  --geno "${GENO}" \
  --make-bed \
  --out "${OUT}"
EOF
chmod +x "${PROJECT_ROOT}/scripts/compute_ld_plink.sh"

# ----------------------------------------------------------------------
# Scripts: python package scaffolding
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/scripts/__init__.py"
"""Utility package for Snakemake helper modules."""
EOF

cat << 'EOF' > "${PROJECT_ROOT}/scripts/dataset_config.py"
"""
Helpers for loading dataset configuration metadata used across Snakemake rules.
"""
from __future__ import annotations

import functools
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@functools.lru_cache(maxsize=None)
def _load_config(path: str) -> Dict[str, Any]:
    config_path = Path(path).expanduser().resolve()
    with config_path.open("r") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or "datasets" not in data:
        raise ValueError(f"Config at {config_path} missing 'datasets' key")
    data["_resolved_path"] = str(config_path)
    return data


def dataset_descriptor(
    trait: str,
    ancestry: str,
    config_path: str = "config/datasets.yaml",
    dataset_name: Optional[str] = None,
    dataset_priority: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    cfg = _load_config(config_path)
    datasets = cfg["datasets"]
    dataset_name = (
        dataset_name
        or (dataset_priority or {}).get(trait)
        or next(iter(datasets.keys()))
    )
    try:
        dataset = datasets[dataset_name]
    except KeyError as err:
        raise KeyError(f"Dataset '{dataset_name}' not defined in {config_path}") from err

    trait_cfg = dataset.get("traits", {}).get(trait)
    if trait_cfg is None:
        available = ", ".join(dataset.get("traits", {}).keys())
        raise KeyError(
            f"Trait '{trait}' missing for dataset '{dataset_name}'. "
            f"Available: {available}"
        )

    ancestry_cfg = (trait_cfg.get("ancestries") or {}).get(ancestry)
    if ancestry_cfg is None:
        available = ", ".join((trait_cfg.get("ancestries") or {}).keys())
        raise KeyError(
            f"Trait '{trait}' missing ancestry '{ancestry}' for dataset '{dataset_name}'. "
            f"Available: {available}"
        )

    defaults = dataset.get("defaults", {})
    column_map: Dict[str, Any] = {}
    for scope in (defaults, trait_cfg, ancestry_cfg):
        column_map.update(scope.get("column_map", {}))

    compression = ancestry_cfg.get(
        "compression",
        trait_cfg.get("compression", defaults.get("compression", "infer")),
    )
    sep = ancestry_cfg.get(
        "sep",
        trait_cfg.get("sep", defaults.get("sep", "\t")),
    )

    path = ancestry_cfg.get("path") or trait_cfg.get("path")
    if not path:
        raise ValueError(
            f"No download path specified for trait '{trait}', ancestry '{ancestry}' "
            f"in dataset '{dataset_name}'."
        )

    base_url = dataset.get("base_url", "").rstrip("/")
    if path.startswith("http://") or path.startswith("https://"):
        url = path
    elif base_url:
        url = f"{base_url}/{path.lstrip('/')}"
    else:
        url = path

    descriptor = {
        "dataset": dataset_name,
        "trait": trait,
        "ancestry": ancestry,
        "url": url,
        "path": path,
        "md5": ancestry_cfg.get("md5") or trait_cfg.get("md5"),
        "description": dataset.get("description", ""),
        "column_map": column_map,
        "compression": compression,
        "sep": sep,
        "config_path": cfg["_resolved_path"],
        "zip_member": ancestry_cfg.get("zip_member")
        or trait_cfg.get("zip_member")
        or defaults.get("zip_member"),
    }
    return descriptor


__all__ = ["dataset_descriptor"]
EOF

cat << 'EOF' > "${PROJECT_ROOT}/scripts/manifest_utils.py"
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def parse_trait_ancestry(path: str) -> Tuple[str, str]:
    name = Path(path).name
    tokens = name.split(".")
    if len(tokens) < 2:
        raise ValueError(
            f"Cannot infer trait/ancestry from filename '{name}'. "
            "Expected <trait>.<ancestry>.<ext>"
        )
    trait, ancestry = tokens[0], tokens[1]
    return trait, ancestry


def harmonized_records(paths: Iterable[str]) -> List[Dict[str, str]]:
    records: List[Dict[str, str]] = []
    for path in paths:
        trait, ancestry = parse_trait_ancestry(path)
        records.append(
            {
                "trait": trait,
                "ancestry": ancestry,
                "path": str(path),
            }
        )
    return records


__all__ = ["parse_trait_ancestry", "harmonized_records"]
EOF

# ----------------------------------------------------------------------
# Scripts: planning helpers
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/scripts/create_multitrait_manifest.py"
#!/usr/bin/env python
import argparse
import sys
from pathlib import Path

import pandas as pd
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.manifest_utils import harmonized_records


def parse_args():
    parser = argparse.ArgumentParser(description="Summarize harmonized files for multi-trait modeling.")
    parser.add_argument("--harmonized", nargs="+", required=True, help="Harmonized sumstats (trait.ancestry.tsv.bgz).")
    parser.add_argument("--regions", required=True, help="Curated regions CSV.")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    records = harmonized_records(args.harmonized)
    regions_df = pd.read_csv(args.regions)
    region_count = regions_df.shape[0]

    manifest = pd.DataFrame(records)
    manifest["regions_file"] = args.regions
    manifest["region_count"] = region_count
    manifest["size_bytes"] = manifest["path"].apply(lambda p: Path(p).stat().st_size if Path(p).exists() else 0)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Writing multitrait manifest with {len(manifest)} entries to {args.output}")
    manifest.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
EOF
chmod +x "${PROJECT_ROOT}/scripts/create_multitrait_manifest.py"

cat << 'EOF' > "${PROJECT_ROOT}/scripts/create_pgs_manifest.py"
#!/usr/bin/env python
import argparse
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yaml
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.manifest_utils import harmonized_records


def parse_args():
    parser = argparse.ArgumentParser(description="Plan cross-ancestry PGS runs.")
    parser.add_argument("--harmonized", nargs="+", required=True)
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def load_pgs_config(path: str) -> Dict[str, List[str]]:
    with open(path, "r") as handle:
        cfg = yaml.safe_load(handle)
    pgs_cfg = cfg.get("pgs", {})
    return {
        "methods": pgs_cfg.get("methods", []),
        "target_ancestries": pgs_cfg.get("target_ancestries", []),
        "ld_reference_dir": pgs_cfg.get("ld_reference_dir", ""),
    }


def main():
    args = parse_args()
    pgs_cfg = load_pgs_config(args.config)
    records = harmonized_records(args.harmonized)

    rows = []
    for entry in records:
        for method in pgs_cfg["methods"]:
            for target in pgs_cfg["target_ancestries"]:
                rows.append(
                    {
                        "trait": entry["trait"],
                        "discovery_ancestry": entry["ancestry"],
                        "target_ancestry": target,
                        "method": method,
                        "sumstats_path": entry["path"],
                        "ld_reference_dir": pgs_cfg["ld_reference_dir"],
                    }
                )

    manifest = pd.DataFrame(rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Writing PGS manifest ({len(manifest)} rows) to {args.output}")
    manifest.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
EOF
chmod +x "${PROJECT_ROOT}/scripts/create_pgs_manifest.py"

cat << 'EOF' > "${PROJECT_ROOT}/scripts/create_mr_design.py"
#!/usr/bin/env python
import argparse
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yaml
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.manifest_utils import harmonized_records


def parse_args():
    parser = argparse.ArgumentParser(description="Generate MR hypothesis manifest.")
    parser.add_argument("--harmonized", nargs="+", required=True)
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def load_mr_hypotheses(config_path: str) -> List[Dict[str, str]]:
    with open(config_path, "r") as handle:
        cfg = yaml.safe_load(handle)
    return cfg.get("mr", {}).get("hypotheses", [])


def main():
    args = parse_args()
    hypotheses = load_mr_hypotheses(args.config)
    harmonized = harmonized_records(args.harmonized)

    index = {}
    for entry in harmonized:
        index.setdefault(entry["trait"], {})[entry["ancestry"]] = entry["path"]

    rows = []
    for hypo in hypotheses:
        exposure = hypo["exposure"]
        outcome = hypo["outcome"]
        note = hypo.get("note", "")
        available_ancestries = set(index.get(exposure, {}).keys()) & set(index.get(outcome, {}).keys())
        if not available_ancestries:
            rows.append(
                {
                    "exposure": exposure,
                    "outcome": outcome,
                    "ancestry": "",
                    "exposure_path": "",
                    "outcome_path": "",
                    "note": note,
                    "status": "missing_harmonized_sumstats",
                }
            )
            continue
        for anc in sorted(available_ancestries):
            rows.append(
                {
                    "exposure": exposure,
                    "outcome": outcome,
                    "ancestry": anc,
                    "exposure_path": index[exposure][anc],
                    "outcome_path": index[outcome][anc],
                    "note": note,
                    "status": "ready",
                }
            )

    manifest = pd.DataFrame(rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Writing MR design manifest ({len(manifest)} rows) to {args.output}")
    manifest.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
EOF
chmod +x "${PROJECT_ROOT}/scripts/create_mr_design.py"

cat << 'EOF' > "${PROJECT_ROOT}/scripts/build_1kg_sample_lists.py"
#!/usr/bin/env python
import argparse
from pathlib import Path

import pandas as pd
import yaml
from loguru import logger


def parse_args():
    parser = argparse.ArgumentParser(description="Generate ancestry-specific KEEP files for 1000G samples.")
    parser.add_argument("--panel", required=True, help="Path to integrated_call_samples panel file.")
    parser.add_argument("--config", default="config/config.yaml", help="YAML config with onekg.populations mapping.")
    parser.add_argument("--output-dir", default="data_raw/1kg", help="Directory to write <ANCESTRY>.samples files.")
    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.config, "r") as handle:
        cfg = yaml.safe_load(handle)

    pop_map = cfg.get("onekg", {}).get("populations")
    if not pop_map:
        raise ValueError("Config missing onekg.populations block")

    panel = pd.read_csv(args.panel, sep="\t")
    if not {"sample", "super_pop", "pop"}.issubset(panel.columns):
        raise ValueError("Panel file missing required columns: sample, super_pop, pop")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for ancestry, pops in pop_map.items():
        matched = panel[panel["pop"].isin(pops)]
        if matched.empty:
            logger.warning(f"No panel entries found for ancestry {ancestry} with pops {pops}")
        keep_path = output_dir / f"{ancestry}.samples"
        matched[["sample", "sample"]].to_csv(keep_path, sep="\t", index=False, header=False)
        logger.info(f"Wrote {matched.shape[0]} samples to {keep_path}")


if __name__ == "__main__":
    main()
EOF
chmod +x "${PROJECT_ROOT}/scripts/build_1kg_sample_lists.py"

cat << 'EOF' > "${PROJECT_ROOT}/scripts/qc_harmonized_sumstats.py"
#!/usr/bin/env python
import argparse
import json
from pathlib import Path

import pandas as pd
from loguru import logger

from scripts.manifest_utils import parse_trait_ancestry


def summarize_file(path: Path, max_rows: int | None = None) -> dict:
    read_kwargs = dict(sep="\t")
    if max_rows:
        read_kwargs["nrows"] = max_rows
    df = pd.read_csv(path, **read_kwargs)
    trait, ancestry = parse_trait_ancestry(path.name)
    summary = {
        "trait": trait,
        "ancestry": ancestry,
        "path": str(path),
        "rows": int(df.shape[0]),
        "nchr": int(df["CHR"].nunique()) if "CHR" in df else 0,
        "missing_beta": int(df["BETA"].isna().sum()) if "BETA" in df else df.shape[0],
        "missing_se": int(df["SE"].isna().sum()) if "SE" in df else df.shape[0],
        "missing_p": int(df["P"].isna().sum()) if "P" in df else df.shape[0],
        "eaf_min": float(df["EAF"].min()) if "EAF" in df else None,
        "eaf_max": float(df["EAF"].max()) if "EAF" in df else None,
        "beta_mean": float(df["BETA"].mean()) if "BETA" in df else None,
        "beta_sd": float(df["BETA"].std()) if "BETA" in df else None,
        "se_median": float(df["SE"].median()) if "SE" in df else None,
        "p_min": float(df["P"].min()) if "P" in df else None,
    }
    return summary


def main():
    parser = argparse.ArgumentParser(description="Summarize harmonized summary statistics.")
    parser.add_argument("--harmonized", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-rows", type=int, default=None, help="Limit rows read per file (for speed).")
    parser.add_argument("--json-log", default=None, help="Optional JSON file for structured summaries.")
    args = parser.parse_args()

    summaries = []
    for path_str in args.harmonized:
        path = Path(path_str)
        if not path.exists():
            logger.warning(f"Missing harmonized file: {path}")
            continue
        logger.info(f"Summarizing {path}")
        summaries.append(summarize_file(path, args.max_rows))

    df = pd.DataFrame(summaries)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, sep="\t", index=False)
    logger.info(f"Wrote harmonized QC table to {args.output}")

    if args.json_log:
        with open(args.json_log, "w") as handle:
            json.dump(summaries, handle, indent=2)


if __name__ == "__main__":
    main()
EOF
chmod +x "${PROJECT_ROOT}/scripts/qc_harmonized_sumstats.py"

cat << 'EOF' > "${PROJECT_ROOT}/scripts/stage_mock_sumstats.py"
#!/usr/bin/env python
import argparse
import gzip
import random
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import yaml
from loguru import logger


def load_config(config_path: str) -> Dict:
    with open(config_path, "r") as handle:
        return yaml.safe_load(handle)


def trait_ancestry_pairs(cfg: Dict) -> List[Tuple[str, str]]:
    traits = cfg["traits"]
    ancestries = cfg["ancestries"]
    overrides = cfg.get("trait_ancestries") or {}
    pairs = []
    for trait in traits:
        trait_ancs = overrides.get(trait, ancestries)
        for anc in trait_ancs:
            pairs.append((trait, anc))
    return pairs


def random_variant(chrom: int, pos_start: int) -> Dict[str, object]:
    pos = pos_start + random.randint(0, 1_000_000)
    ref = random.choice(["A", "C", "G", "T"])
    alt = random.choice([b for b in ["A", "C", "G", "T"] if b != ref])
    beta = random.uniform(-0.5, 0.5)
    se = abs(random.gauss(0.05, 0.02))
    z = beta / se if se else 0
    eaf = min(max(random.uniform(0.01, 0.99), 0.01), 0.99)
    return {
        "CHR": chrom,
        "POS": pos,
        "REF": ref,
        "ALT": alt,
        "BETA": beta,
        "SE": se,
        "P": min(max(2 * (1 - abs(z) / 8), 1e-12), 1.0),
        "EAF": eaf,
    }


def make_records(variants_per_chrom: int) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    for chrom in (1, 2):
        for idx in range(variants_per_chrom):
            records.append(random_variant(chrom, idx * 100_000))
    return records


def write_table(path: Path, records: Iterable[Dict[str, object]]):
    header = ["CHR", "POS", "REF", "ALT", "BETA", "SE", "P", "EAF"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as handle:
        handle.write("\t".join(header) + "\n")
        for row in records:
            handle.write(
                "\t".join(str(row[col]) for col in header)
                + "\n"
            )


def main():
    parser = argparse.ArgumentParser(description="Create tiny GWAS summary statistics for testing.")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--output-dir", default="data_raw/sumstats")
    parser.add_argument("--variants-per-chr", type=int, default=5)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    random.seed(args.seed)
    cfg = load_config(args.config)
    pairs = trait_ancestry_pairs(cfg)
    logger.info(f"Creating mock sumstats for {len(pairs)} trait/ancestry combinations")

    created = []
    for trait, ancestry in pairs:
        records = make_records(args.variants_per_chrom)
        out_path = Path(args.output_dir) / f"{trait}.{ancestry}.raw.gz"
        write_table(out_path, records)
        created.append(out_path)

    for path in created:
        logger.info(f"Wrote mock file: {path}")
    logger.info("Done.")


if __name__ == "__main__":
    main()
EOF
chmod +x "${PROJECT_ROOT}/scripts/stage_mock_sumstats.py"

# ----------------------------------------------------------------------
# Scripts: utils_logging.py
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/scripts/utils_logging.py"
from loguru import logger
import sys

def setup_logging(level: str = "INFO"):
    """
    Simple helper to configure loguru once per script.
    """
    logger.remove()
    logger.add(sys.stderr, level=level)
    return logger
EOF

# ----------------------------------------------------------------------
# README
# ----------------------------------------------------------------------
cat << 'EOF' > "${PROJECT_ROOT}/README.md"
# Summary-statistics-based multi-trait workflow (Snakemake + LSF)

This repo is a project skeleton for:

- Summary-statistics-based multi-trait analyses as the main “real-data” engine.
- Re-usable slots for:
  - Local-ancestry-based region definitions (from AA admixture hits),
  - PGS/PRS-CSx,
  - MR and multi-trait colocalization.

## Layout

See `config/config.yaml` for traits, ancestries, and paths.

Key dirs:

- `config/` : global config, datasets, curated regions (incl. APOL1), LSF cluster config.
- `envs/`   : conda envs (Snakemake core, R stats, plink/bcftools).
- `data_raw/` and `data_processed/` : raw / processed GWAS & LD data.
- `scripts/` : Python + shell helpers.
- `workflow/` : main `Snakefile` and modular `rules/`.

## Quickstart

Create env:

```bash
mamba env create -f envs/snakemake_env.yml
conda activate la_multitrait
snakemake --cores 4 --use-conda
```

Replace the env name / working directory reference above with whatever you actually use on your system.

### Configure data sources

1. `config/datasets.yaml` already lists the current sources mentioned in the project brief (GBMI asthma, Yengo 2018 BMI, DIAMANTE 2022 T2D, Evangelou 2018 BP, and MEGASTROKE stroke). Update the `md5`, `path`, or `zip_member` fields if you mirror the files elsewhere or if the upstream archives change layout. The `column_map` entries describe how raw column names map to the harmonized schema—tweak them if any dataset deviates.
2. `config/config.yaml` controls the trait list, per-trait dataset priority, and the `trait_ancestries` matrix (e.g., BMI currently has EUR only, while asthma has EUR+AFR). Adjust those lists if you add additional ancestries or traits.
3. To add additional loci/regions, extend `config/regions_curated.csv` and re-run `snakemake make_regions_from_loci`.

Need a smoke-test without downloading the large public files? Run:

```bash
python scripts/stage_mock_sumstats.py --config config/config.yaml --output-dir data_raw/sumstats
```

This creates tiny gzipped GWAS files for every trait/ancestry pair so the Snakemake DAG can be exercised end-to-end.

### Workflow modules

- **Summary stats** (`workflow/rules/sumstats.smk`): downloads raw files via `requests`, transparently extracts `.zip` archives, and feeds them into `scripts/harmonize_sumstats.py`, which uses `config/datasets.yaml` metadata to standardize column names. Once harmonized, `workflow/rules/qc.smk` summarizes each file (N variants, missingness, allele-frequency range) at `results/qc/harmonized_summary.tsv`.
- **Region prep** (`workflow/rules/regions.smk`): converts curated loci into BED files.
- **Multitrait planning** (`workflow/rules/multitrait.smk`): `scripts/create_multitrait_manifest.py` records which harmonized file pairs feed each region-based analysis.
- **LD + PGS scaffolding** (`workflow/rules/ld_reference.smk` / `workflow/rules/pgs.smk`): `download_1kg_vcf` pulls per-chromosome 1000G Phase 3 vcfs + tbi files, `build_1kg_sample_lists.py` generates ancestry-specific KEEP files from the panel, `prepare_ld_plink` builds filtered PLINK references, and `scripts/create_pgs_manifest.py` enumerates PRS-CSx/LDpred2 jobs across ancestries. A placeholder rule (`run_pgs_placeholder`) reports how many jobs would run.
- **MR design** (`workflow/rules/mr.smk`): `scripts/create_mr_design.py` cross-references harmonized files with the hypotheses listed under the `mr:` block in `config/config.yaml`, and `run_mr_placeholder` prints the ready vs missing hypotheses count.
- **Multitrait execution placeholder** (`run_multitrait_placeholder`) consumes the manifest and echoes the number of planned region-trait analyses—swap this out with SuSiE/FINEMAP/coloc runners once the LD matrices are ready.

After editing the configs above, `snakemake --cores <N> --use-conda` will pull raw summary stats, harmonize them, and emit planning manifests under `results/`.
EOF

chmod +x setup_project.sh
