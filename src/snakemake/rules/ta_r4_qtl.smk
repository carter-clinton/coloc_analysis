"""ta-r4 QTL layer (W3e; D-05, D-06, D-07, D-22, D-02).

r4_qtl_harmonize: pre-gate data processing (D-05), one job per (source, qtd, region) group of
config/ta_r4/qtl_manifest.tsv; the shipped harmonizers run once per molecular_trait_id (ta_r4.harmonize_qtl_r4).
"""

from ta_r4 import harmonize_qtl_r4 as r4harm

_R4_QTL_ROWS = r4harm.manifest_rows(str(Path(workflow.basedir) / r4harm.MANIFEST))
_R4_QTL_GROUPS = r4harm.groups(_R4_QTL_ROWS)
R4_QTL_HARMONIZE_TARGETS = [r4harm.done_path(*g) for g in _R4_QTL_GROUPS]


rule r4_qtl_harmonize:
    input:
        tsv=lambda w: r4harm.download_path(w.qtd),
        tbi=lambda w: r4harm.download_path(w.qtd) + ".tbi",
        manifest=r4harm.MANIFEST,
        qtl_sources=r4harm.QTL_SOURCES,
    output:
        r4harm.done_path("{source}", "{qtd}", "{region}"),
    log:
        "data/r4/logs/qtl_harmonize/{source}.{qtd}.{region}.log",
    wildcard_constraints:
        source="eqtl|sqtl",
        qtd="QTD[0-9]+",
        region="[A-Za-z0-9_]+",
    conda:
        str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
    threads: 1
    resources:
        mem_mb=8000,
    shell:
        "env PYTHONPATH=src/python python -m ta_r4.harmonize_qtl_r4 --source {wildcards.source} --qtd {wildcards.qtd}"
        " --region {wildcards.region} --manifest {input.manifest} --done {output} > {log} 2>&1"


rule r4_qtl_harmonize_all:
    input:
        R4_QTL_HARMONIZE_TARGETS,

