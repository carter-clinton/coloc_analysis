"""Region extraction rules.

Refactored from src/legacy/region_analysis/workflow/rules/regions.smk.
All paths parameterized via config["paths"] (D-09, D-10).
Conda directives point to envs/ relative to project root (D-25).
"""

import sys

PYTHON_BIN = sys.executable


rule make_regions_from_loci:
    input:
        loci=config["paths"]["regions_curated"],
    output:
        bed=config["paths"]["regions_bed"],
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        mkdir -p "$(dirname {output.bed})"
        {PYTHON_BIN} src/legacy/region_analysis/scripts/make_regions_from_loci.py \
            --input {input.loci} \
            --output {output.bed}
        """
