"""M2 Wave 4 — mtCOJO sensitivity per (stratum, target_trait) per D-M2-08 + Q5.

Plan: m2-04-clumping-mtcojo-regions-PLAN.md.
Decisions:
  D-M2-08 — mtCOJO on every MTAG-novel locus where any contributing-trait
            gcov_int > 0.1 (Turley 2018 §"sample overlap")
  D-M2-Q3 — TRANS uses 1000G EUR LD primary + 1000G AFR sensitivity check
  D-M2-Q5 — only MTAG-novel target traits with extreme overlap fire mtCOJO
  CR-checker WR-4 — `mtcojo_eligible_targets` is a SNAKEMAKE CHECKPOINT
            (commit 296f25d) so the eligible-targets list expands the DAG
            mid-execution. Snakemake re-evaluates {trait} wildcards AFTER
            the checkpoint emits eligible_targets.tsv.
            See https://snakemake.readthedocs.io/en/stable/snakefiles/rules.html#data-dependent-conditional-execution

Inputs (consumed at production-fire time):
  - data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt  (Wave 2)
  - data/processed/ldsc_overlap/rg_matrix_long_M2.tsv                 (Wave 1)
  - data/processed/mtag/{stratum}/residcov.trait_order.json           (Wave 2 sidecar)
  - data/processed/sumstats_harmonized/{trait_key}.GRCh37.tsv.bgz     (M1)

Outputs:
  - data/processed/mtcojo/{stratum}/mtcojo_eligible_targets.tsv       (checkpoint)
  - data/processed/mtcojo/{stratum}/{trait}.mtcojo.cojo               (per eligible target)
  - data/processed/mtcojo/{stratum}/mtcojo_sensitivity.tsv            (aggregator)
"""
from pathlib import Path
import os
import sys

try:
    _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
except NameError:
    _BASE = Path(os.getcwd())


_MTAG_DIR = "data/processed/mtag"
_MTCOJO_DIR = "data/processed/mtcojo"
_LONG_MATRIX = "data/processed/ldsc_overlap/rg_matrix_long_M2.tsv"
_HARMONIZED_DIR = "data/processed/sumstats_harmonized"
_LDSCORE_EUR = "data/external/ldscore/eur_w_ld_chr"

STRATA = ("EUR", "AFR", "TRANS")


def _mtcojo_ld_ref(stratum: str) -> str:
    """LD reference bfile prefix per stratum (D-M2-Q3).

    TRANS uses 1000G EUR primary; AFR sensitivity is added as a separate
    re-run per Q3 + Q4. EUR/AFR strata use matched 1000G panels.
    """
    if stratum == "EUR":
        return "data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC"
    if stratum == "AFR":
        return "data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC"
    if stratum == "TRANS":
        # D-M2-Q3 + RESEARCH Q4 — TRANS primary is 1000G EUR Phase 3 plink
        return "data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC"
    raise ValueError(stratum)


checkpoint m2_mtcojo_eligible_targets:
    """Per-stratum eligibility list (D-M2-Q5).

    SNAKEMAKE CHECKPOINT (per CR-checker WR-4, commit 296f25d): downstream
    {trait} wildcards are re-evaluated AFTER this rule completes, by
    parsing the on-disk eligibility TSV. Joins MTAG-novel hit lists from
    Wave 2 with the LDSC bivariate-intercept matrix from Wave 1, filters
    to (target_trait) tuples passing the gcov_int > 0.1 (D-M2-08) threshold.
    """
    input:
        mtag_filtered=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_maxfdr_filtered.txt",
        long_matrix=_LONG_MATRIX,
        sidecar=f"{_MTAG_DIR}/{{stratum}}/residcov.trait_order.json",
    output:
        tsv=f"{_MTCOJO_DIR}/{{stratum}}/mtcojo_eligible_targets.tsv",
    conda:
        "../../../envs/m2-mtcojo.yml"
    resources:
        mem_mb=2000,
        runtime=10,
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.tsv})
        python src/python/select_mtcojo_eligible_targets.py \
            --stratum {wildcards.stratum} \
            --mtag-filtered {input.mtag_filtered} \
            --long-matrix {input.long_matrix} \
            --sidecar {input.sidecar} \
            --out {output.tsv}
        """


rule m2_mtcojo_run:
    """Per (stratum, target_trait) mtCOJO conditional analysis (D-M2-08).

    GCTA mtCOJO consumes a 2-column file listing (trait_label, cojo_path)
    with the target trait first then covariate traits. The COJO format per
    trait is: SNP A1 A2 freq b se p N (whitespace-delimited). We materialize
    these from harmonized .tsv.bgz on the fly via build_cojo_inputs.py.

    LD reference: {EUR,AFR}.QC.{1..22} (mbfile list). LD-scores: eur_w_ld_chr/
    cross-ancestry approximation per D-M2-Q2 (M2 LDSC convention; M3
    supersede when AoU AFR LD lands).
    """
    input:
        eligible=f"{_MTCOJO_DIR}/{{stratum}}/mtcojo_eligible_targets.tsv",
        sidecar=f"{_MTAG_DIR}/{{stratum}}/residcov.trait_order.json",
    output:
        cojo=f"{_MTCOJO_DIR}/{{stratum}}/{{trait}}.mtcojo.cojo",
        log=f"{_MTCOJO_DIR}/{{stratum}}/{{trait}}.mtcojo.log",
    params:
        ld_ref=lambda wc: _mtcojo_ld_ref(wc.stratum),
        out_prefix=f"{_MTCOJO_DIR}/{{stratum}}/{{trait}}.mtcojo",
        ldsc_dir=_LDSCORE_EUR,
    conda:
        "../../../envs/m2-mtcojo.yml"
    resources:
        mem_mb=8000,
        runtime=120,
    threads: 4
    shell:
        r"""
        set -euo pipefail
        python src/python/build_cojo_inputs.py \
            --target {wildcards.trait} \
            --stratum {wildcards.stratum} \
            --sidecar {input.sidecar} \
            --harmonized-dir {_HARMONIZED_DIR} \
            --out-dir $(dirname {params.out_prefix})/cojo_inputs

        # Build mbfile list of per-chr 1000G {EUR|AFR} bfiles
        MBFILE=$(mktemp --suffix=.mbfile)
        trap "rm -f $MBFILE" EXIT
        for c in $(seq 1 22); do
            BF="{params.ld_ref}.${{c}}"
            if [ -f "${{BF}}.bed" ]; then
                echo "${{BF}}" >> $MBFILE
            fi
        done

        gcta \
            --mtcojo-file $(dirname {params.out_prefix})/cojo_inputs/{wildcards.trait}.mtcojo.list \
            --mbfile $MBFILE \
            --w-ld-chr {params.ldsc_dir}/ \
            --ref-ld-chr {params.ldsc_dir}/ \
            --out {params.out_prefix} \
            2>&1 | tee {output.log}
        test -s {output.cojo}
        """


def _mtcojo_targets_for_stratum(wildcards):
    """Dynamic input function driven by the m2_mtcojo_eligible_targets checkpoint.

    Snakemake re-evaluates this function AFTER the checkpoint completes,
    parsing eligible_targets.tsv to expand {trait} wildcards into the
    per-target cojo file paths the sensitivity-table aggregator depends on.
    """
    import pandas as pd
    elig_path = checkpoints.m2_mtcojo_eligible_targets.get(stratum=wildcards.stratum).output.tsv
    df = pd.read_csv(elig_path, sep="\t")
    return [
        f"{_MTCOJO_DIR}/{wildcards.stratum}/{t}.mtcojo.cojo"
        for t in df["target_trait"].tolist()
    ]


rule m2_mtcojo_sensitivity_table:
    """Aggregate per-stratum mtcojo outputs into mtcojo_sensitivity.tsv.

    DYNAMIC INPUT driven by the checkpoint (CR-checker WR-4). Snakemake
    re-resolves {trait} wildcards after the checkpoint emits eligible_targets.tsv.

    Output schema (D-M2-Q3 includes trans_ld_panel_concordance for TRANS):
      locus_id, trait, mtag_p_original, mtcojo_p, max_overlapping_intercept,
      sensitivity_flag, [trans_ld_panel_concordance for TRANS]
    """
    input:
        eligible=f"{_MTCOJO_DIR}/{{stratum}}/mtcojo_eligible_targets.tsv",
        cojo_files=_mtcojo_targets_for_stratum,
    output:
        sensitivity=f"{_MTCOJO_DIR}/{{stratum}}/mtcojo_sensitivity.tsv",
    conda:
        "../../../envs/m2-mtcojo.yml"
    resources:
        mem_mb=4000,
        runtime=15,
    shell:
        r"""
        python src/python/build_mtcojo_sensitivity_table.py \
            --stratum {wildcards.stratum} \
            --eligible {input.eligible} \
            --mtcojo-dir $(dirname {output.sensitivity}) \
            --mtag-filtered {_MTAG_DIR}/{wildcards.stratum}/{wildcards.stratum}_mtag_maxfdr_filtered.txt \
            --out {output.sensitivity}
        """


rule m2_mtcojo_all_strata:
    """Aggregator over all 3 strata."""
    input:
        expand(f"{_MTCOJO_DIR}/{{stratum}}/mtcojo_sensitivity.tsv", stratum=STRATA),
    output:
        sentinel=f"{_MTCOJO_DIR}/.m2_mtcojo_complete",
    shell:
        "touch {output.sentinel}"
