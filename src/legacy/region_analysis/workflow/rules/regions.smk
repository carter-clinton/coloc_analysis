import sys

PYTHON_BIN = sys.executable


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
        {PYTHON_BIN} scripts/make_regions_from_loci.py \
            --input {input.loci} \
            --output {output.bed}
        """
