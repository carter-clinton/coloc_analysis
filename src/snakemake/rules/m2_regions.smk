"""M2 Wave 4 — region union BED builder per D-M2-09.

Plan: m2-04-clumping-mtcojo-regions-PLAN.md.
Decisions:
  D-M2-09 — strict union of clumped + MTAG-novel + CPASSOC-novel leads,
            ±1 Mb windows, bedtools default merge
  Q6 + Pitfall 9 — bedtools merge with NO -d, NO -s flags

Inputs:
  - data/processed/clumping/{ancestry}/*.clumped.bed (Wave 4 Task 1)
  - data/processed/mtag/{stratum}/{stratum}_mtag_maxfdr_filtered.txt (Wave 2)
  - data/processed/cpassoc/{stratum}/cpassoc_results.tsv (Wave 3)

Output:
  - results/regions/union_region_list.bed
    schema: chr, start, end, region_id, score=., strand=., provenance_json
"""
from pathlib import Path
import os

try:
    _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
except NameError:
    _BASE = Path(os.getcwd())


_CLUMP_DIR = "data/processed/clumping"
_MTAG_DIR = "data/processed/mtag"
_CPASSOC_DIR = "data/processed/cpassoc"
_REGIONS_OUT = "results/regions/union_region_list.bed"

STRATA = ("EUR", "AFR", "TRANS")


rule m2_build_region_union:
    """Strict union BED of clumped + MTAG-novel + CPASSOC-novel leads (D-M2-09, Q6).

    bedtools default merge (no -d, no -s — Pitfall 9). ±1 Mb windows per lead.
    Output schema: chr, start, end, region_id, score=., strand=., provenance_json
    """
    input:
        clumped=lambda wc: [str(p) for p in Path(_CLUMP_DIR).rglob("*.clumped.bed")],
        mtag=expand(f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_maxfdr_filtered.txt", stratum=STRATA),
        cpassoc=expand(f"{_CPASSOC_DIR}/{{stratum}}/cpassoc_results.tsv", stratum=STRATA),
    output:
        bed=_REGIONS_OUT,
    conda:
        "../../../envs/m2-regions.yml"
    resources:
        mem_mb=8000,
        runtime=30,
    shell:
        r"""
        mkdir -p $(dirname {output.bed})
        python src/python/build_region_union.py \
            --clumped-beds {input.clumped} \
            --mtag-paths {input.mtag} \
            --cpassoc-paths {input.cpassoc} \
            --out {output.bed}
        wc -l {output.bed}
        """
