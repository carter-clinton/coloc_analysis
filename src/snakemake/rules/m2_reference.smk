"""M2 Wave 0 reference-data builder: 1000G AFR Phase 3 PLINK bfiles.

Pitfall 3 (m2-RESEARCH.md): data/reference/ldsc/1000G_AFR_Phase3_plink/ has
NO .bed/.bim/.fam on disk; only the LDSC-public .frq files at
1000G_Phase3_frq_AFR/ are present. Build the bfile triple per chromosome
from data/raw/1kg/vcf/chr{chr}.vcf.gz keeping data/raw/1kg/AFR.samples
(504 sample IDs).

Output: data/reference/ldsc/1000G_AFR_Phase3_plink/1000G.AFR.QC.{chr}.{bed,bim,fam}
Filters: --maf 0.005 --geno 0.05 --hwe 1e-6 (per RESEARCH Pitfall 3 spec).

Plan reference: m2-00-preflight-and-environment-PLAN.md Task 4 (BLOCKING).
Decision references:
  D-M2-02 — provisional 1000G AFR (N=661) for M2; M3 supersede with AoU
  D-M2-09 — clumped lead variants per (trait × ancestry) feed union BED
  D-M2-Q2 — EUR ld-scores cross-ancestry for M2 LDSC; AFR PLINK only for clumping

Conda env: envs/m2-clumping.yml (plink=1.9 — Pitfall 5).
"""
from pathlib import Path
import os

try:
    _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
except NameError:
    _BASE = Path(os.getcwd())

_AFR_PLINK_DIR = "data/reference/ldsc/1000G_AFR_Phase3_plink"


rule m2_build_1000g_afr_plink_chr:
    """Per-chr 1000G AFR PLINK bfile build from VCF + AFR.samples.

    Reads chromosome-level 1000G VCF, keeps the 504 AFR samples per
    AFR.samples (1000G integrated_call_samples.panel AFR continental
    super-population: ACB, ASW, ESN, GWD, LWK, MSL, YRI), applies
    MAF/HWE/geno QC filters, and writes the .bed/.bim/.fam triple.
    """
    input:
        vcf="data/raw/1kg/vcf/chr{chr}.vcf.gz",
        keep="data/raw/1kg/AFR.samples",
    output:
        bed=f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}.bed",
        bim=f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}.bim",
        fam=f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}.fam",
    params:
        out_prefix=f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}",
    conda:
        "../../../envs/m2-clumping.yml"
    resources:
        mem_mb=4000,
        runtime=120,
    threads: 2
    shell:
        r"""
        mkdir -p $(dirname {params.out_prefix})
        plink \
            --vcf {input.vcf} \
            --keep {input.keep} \
            --maf 0.005 \
            --geno 0.05 \
            --hwe 1e-6 \
            --make-bed \
            --memory 3500 \
            --out {params.out_prefix}
        test -s {output.bed}
        test -s {output.bim}
        test -s {output.fam}
        """


rule m2_build_1000g_afr_plink_all:
    """Aggregator — all 22 autosomes built; touches sentinel marker."""
    input:
        expand(f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}.bed", chr=range(1, 23)),
        expand(f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}.bim", chr=range(1, 23)),
        expand(f"{_AFR_PLINK_DIR}/1000G.AFR.QC.{{chr}}.fam", chr=range(1, 23)),
    output:
        sentinel=f"{_AFR_PLINK_DIR}/.build_complete",
    shell:
        "touch {output.sentinel}"
