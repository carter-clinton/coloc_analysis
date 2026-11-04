"""ta-r4 QTL layer (W3e; D-05, D-06, D-07, D-22, D-02).

r4_qtl_harmonize: pre-gate data processing (D-05), one job per (source, qtd, region) group of
config/ta_r4/qtl_manifest.tsv; the shipped harmonizers run once per molecular_trait_id (ta_r4.harmonize_qtl_r4).
r4_qtl_group / r4_qtl_aggregate / r4_qtl_tiers: defined only in the invocation of a QTL arm's fit arm (QTL_A3 in
A3_1kg, QTL_A2 in A2_identity: production, gated; QTL_legacy in repro_routeL: repro). The group runner is
ta_r4.run_qtl_group_r4.
"""

import sys

from ta_r4 import commands as r4cmd
from ta_r4 import harmonize_qtl_r4 as r4harm
from ta_r4 import run_qtl_group_r4 as r4qtl
from ta_r4.arms import arm_stage

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


R4_QTL_ARM = r4qtl.qtl_arm_for(ARM)
_R4_QTL_IDX = r4harm.group_index(_R4_QTL_ROWS)


def _r4_qtl_gate(w):
    """Lock gate on the QTL arm's fit-arm stage; raises before any path is resolved."""
    stage = arm_stage(r4qtl.fit_arm(w.qtl_arm))
    check_lock_gate(Path(workflow.basedir), stage)
    return [LOCK_RECORD_REL] if stage == "production" else []


def _r4_qtl_group_inputs(w):
    gate = _r4_qtl_gate(w)
    rows = _R4_QTL_IDX.get((w.source, w.qtd, w.region))
    if not rows:
        raise WorkflowError(f"no config/ta_r4/qtl_manifest.tsv rows for {w.region} {w.source} {w.qtd}")
    fa = r4qtl.fit_arm(w.qtl_arm)
    traits = sorted({r["trait"] for r in rows})
    d = {
        "gate": gate,
        "harmonized": r4harm.done_path(w.source, w.qtd, w.region),
        "fits": [r4paths.fit_rds(fa, t, r4qtl.ANCESTRY, w.region) for t in traits],
        "sumstats": [r4paths.sumstats_path(t, r4qtl.ANCESTRY, fa) for t in traits],
        "panel": r4paths.panel_path(fa, w.region, r4qtl.ANCESTRY),
        "manifest": r4harm.MANIFEST,
        "priors": r4cmd.COLOC_PRIORS,
        "traits": r4cmd.TRAIT_MANIFEST,
        "qtl_sources": r4harm.QTL_SOURCES,
        "script": r4qtl.QTL_SCRIPT,
        "abf_script": r4cmd.COLOC_SCRIPT,
    }
    if r4qtl.QTL_ARMS[w.qtl_arm]["ld_allele_join"] == "true":
        d["catalog"] = r4qtl.catalog(w.qtl_arm, w.region)
    return d


def R4_QTL_TARGETS(qtl_arm):
    """Every group .done, the aggregate and the tier tables of one QTL arm."""
    return [r4qtl.done_path(qtl_arm, reg, src, qtd) for src, qtd, reg in _R4_QTL_GROUPS] + [
        f"data/r4/results/{qtl_arm}/qtl_coloc_summary.tsv", f"data/r4/results/{qtl_arm}/qtl_tiers.tsv"]


if R4_QTL_ARM is not None:

    rule r4_qtl_group:
        input:
            unpack(_r4_qtl_group_inputs),
        output:
            r4qtl.done_path("{qtl_arm}", "{region}", "{source}", "{qtd}"),
        log:
            "data/r4/logs/{qtl_arm}/qtl/{region}.{source}.{qtd}.log",
        wildcard_constraints:
            qtl_arm=R4_QTL_ARM,
            region="[A-Za-z0-9_]+",
            source="eqtl|sqtl",
            qtd="QTD[0-9]+",
        conda:
            str(Path(workflow.basedir) / "envs" / "r_coloc.yml")
        threads: 1
        resources:
            mem_mb=config["resources"]["default_mem_mb"],
        params:
            py=sys.executable,
        shell:
            "env PYTHONPATH=src/python {params.py} -m ta_r4.run_qtl_group_r4 --qtl-arm {wildcards.qtl_arm}"
            " --region {wildcards.region} --source {wildcards.source} --qtd {wildcards.qtd}"
            " --manifest {input.manifest} --done {output} > {log} 2>&1"

    rule r4_qtl_aggregate:
        input:
            gate=_r4_qtl_gate,
            groups=lambda w: [r4qtl.done_path(w.qtl_arm, reg, src, qtd) for src, qtd, reg in _R4_QTL_GROUPS],
            manifest=r4harm.MANIFEST,
        output:
            "data/r4/results/{qtl_arm}/qtl_coloc_summary.tsv",
        log:
            "data/r4/logs/{qtl_arm}/qtl_aggregate.log",
        wildcard_constraints:
            qtl_arm=R4_QTL_ARM,
        params:
            py=sys.executable,
        shell:
            "{params.py} src/python/aggregate_qtl_coloc.py --json-dir data/r4/results/{wildcards.qtl_arm}/qtl"
            " --manifest {input.manifest} --output {output} > {log} 2>&1"

    rule r4_qtl_tiers:
        input:
            gate=_r4_qtl_gate,
            summary="data/r4/results/{qtl_arm}/qtl_coloc_summary.tsv",
            coloc=lambda w: r4qtl.coloc_inputs(w.qtl_arm),
            pph4="config/pph4_thresholds.yaml",
        output:
            gwas="data/r4/results/{qtl_arm}/gwas_coloc_for_tiers.tsv",
            tiers="data/r4/results/{qtl_arm}/qtl_tiers.tsv",
            sweep="data/r4/results/{qtl_arm}/qtl_tiers_sweep.tsv",
        log:
            "data/r4/logs/{qtl_arm}/qtl_tiers.log",
        wildcard_constraints:
            qtl_arm=R4_QTL_ARM,
        params:
            py=sys.executable,
        shell:
            "(env PYTHONPATH=src/python {params.py} -m ta_r4.run_qtl_group_r4 --qtl-arm {wildcards.qtl_arm}"
            " --gwas-coloc-table {output.gwas} && {params.py} src/python/assign_tiers.py --input {input.summary}"
            " --gwas-coloc {output.gwas} --pph4-config {input.pph4} --output {output.tiers} --sweep"
            " --sweep-output {output.sweep}) > {log} 2>&1"

    rule r4_qtl_all:
        input:
            R4_QTL_TARGETS(R4_QTL_ARM),
