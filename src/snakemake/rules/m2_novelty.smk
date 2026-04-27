"""M2 Wave 5 — Class 1 (joint-signal) novelty caller per OSF amendment §7.1.

Plan: m2-05-class1-novelty-and-closeout-PLAN.md.
REQ-NOVELTY-CLASS-1 + D-M2-05 (catalog v_lock_M2) + D-M2-07 (max_FDR threshold).

Pipeline:
  per-stratum mtag_maxfdr_filtered.txt (Wave 2)
    + per-stratum cpassoc_results.tsv (Wave 3)
    + GWAS Catalog v_lock_M2 (.zip frozen by SHA-256 in Wave 0 Task 5)
  -> src/python/call_class1_novelty.py
  -> results/novelty/joint_signal_novel.tsv (ROADMAP M2 success criterion 5)

Class 1 operational definition (OSF posting at osf.io/az52u/files/k8w7n,
amendment commit 61315de):
  Joint-signal novel = (MTAG p < 5e-8 OR CPASSOC p < 5e-8)
                       AND max(single-trait p) >= 5e-8
                       AND no contributing single-trait GWS hit within
                           +/-500 kb in GWAS Catalog v_lock_M2.

  High-confidence subset = MTAG ∩ CPASSOC.
"""
from pathlib import Path

# Per D-M2-Q6 _MIN_PER_STRATUM=3; all 3 strata cleared the floor in Waves 2-3
# (EUR=8, AFR=6, TRANS=7). Hard-coded here to keep the rule deterministic.
M2_NOVELTY_STRATA = ("EUR", "AFR", "TRANS")

# Catalog snapshot key per data/catalogs/catalog_lock_manifest.tsv
# (M2-locked SHA-256 = 652a974d3246748290baa83899d3c8db0027eed76663b767beaee319618961cd)
M2_CATALOG_VERSION = "v_lock_M2"


rule m2_call_class1_novelty:
    """Class 1 (joint-signal) novelty filter against GWAS Catalog v_lock_M2.

    Inputs (per stratum):
      - mtag_maxfdr_filtered.txt: SNP/A1/A2/Z/N/FRQ/mtag_beta/mtag_se/mtag_z/
                                  mtag_pval/max_FDR/trait_key
      - cpassoc_results.tsv:      chr/pos/rsid/A1/A2/n_traits/SHom_stat/SHom_p/
                                  SHet_stat/SHet_p/contributing_traits
      - residcov.trait_order.json: per-stratum K-trait order alignment (Pitfall 7)
      - gwas_catalog .zip: prior-art exclusion source (M2_CATALOG_VERSION)

    Output schema (per REQ-NOVELTY-CLASS-1 acceptance):
      chr  pos  rsid  stratum  mtag_p  cpassoc_shom_p  cpassoc_shet_p
        max_single_trait_p  nearest_gwas_catalog_entry  nearest_distance_bp
        confidence_tier
    """
    input:
        mtag=expand(
            "data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt",
            stratum=M2_NOVELTY_STRATA,
        ),
        cpassoc=expand(
            "data/processed/cpassoc/{stratum}/cpassoc_results.tsv",
            stratum=M2_NOVELTY_STRATA,
        ),
        sidecars=expand(
            "data/processed/mtag/{stratum}/residcov.trait_order.json",
            stratum=M2_NOVELTY_STRATA,
        ),
        catalog="data/catalogs/gwas-catalog-associations-full.zip",
    output:
        novel="results/novelty/joint_signal_novel.tsv",
    log:
        "logs/m2_05_call_class1_novelty.log",
    conda:
        "../../../envs/m2-novelty.yml"
    resources:
        mem_mb=16000,
        runtime=120,
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.novel}) $(dirname {log})
        python src/python/call_class1_novelty.py \
            --strata EUR AFR TRANS \
            --mtag-dir data/processed/mtag \
            --cpassoc-dir data/processed/cpassoc \
            --catalog-zip {input.catalog} \
            --out {output.novel} \
            2>&1 | tee {log}
        wc -l {output.novel}
        head -1 {output.novel}
        """


rule m2_novelty_closeout:
    """Aggregator: emits a tier-distribution summary alongside the main TSV.

    Re-reads results/novelty/joint_signal_novel.tsv after the class-1 caller
    fires; writes a one-line tier-distribution sidecar for the PHASE-CLOSEOUT
    report and the verifier D5 dimension.
    """
    input:
        novel="results/novelty/joint_signal_novel.tsv",
    output:
        summary="results/novelty/joint_signal_novel.summary.tsv",
    shell:
        r"""
        set -euo pipefail
        # Emit n_total / n_high / n_medium for the closeout summary
        python -c "
import pandas as pd
df = pd.read_csv('{input.novel}', sep='\t')
total = len(df)
n_high = int((df['confidence_tier']=='high').sum()) if total else 0
n_medium = int((df['confidence_tier']=='medium').sum()) if total else 0
with open('{output.summary}', 'w') as fh:
    fh.write('metric\tvalue\n')
    fh.write(f'n_total\t{{total}}\n')
    fh.write(f'n_high\t{{n_high}}\n')
    fh.write(f'n_medium\t{{n_medium}}\n')
"
        cat {output.summary}
        """
