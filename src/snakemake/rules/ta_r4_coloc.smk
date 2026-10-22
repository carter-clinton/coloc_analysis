"""ta-r4 trait-pair coloc (D-01, D-02, D-21): run_coloc_pair_r4.R for admissible pair_manifest rows.

r4_coloc_pair: coloc.susie on the arm's fits, or the labelled fallback_abf when a fit has 0 credible sets.
r4_coloc_A1: A1 matched / all-variants, defined only in the A3 invocations (A3_1kg, AFR661_A3).
The argv is ta_r4.commands.coloc_command, which the tests run as-is. Both rules take the OSF gate first.
"""

import shlex

from ta_r4 import commands as r4cmd
from ta_r4.arms import arm_ancestries

R4_COLOC_ROWS = {r["row_id"]: r for r in PAIR_ROWS if r["admissible"] == "true"}
_R4_COLOC_ENV = str(Path(workflow.basedir) / "envs" / "r_coloc.yml")


def _r4_coloc_row(w, ancestries):
    r = R4_COLOC_ROWS.get(w.row_id)
    if r is None or r["ancestry"] not in ancestries:
        raise WorkflowError(f"{w.row_id}: not an admissible {'/'.join(ancestries)} row of config/ta_r4/pair_manifest.tsv")
    return r


def _r4_coloc_inputs(w, mode):
    gate = gate_input(w)  # OSF gate first: production refuses before any path is resolved
    ancs = arm_ancestries(ARM) if mode == "susie" else (r4cmd.A1_FIT_ARMS[ARM],)
    r = _r4_coloc_row(w, ancs)
    anc, reg = r["ancestry"], r["region_safe"]
    d = {
        "gate": gate,
        "sumstats_a": r4paths.sumstats_path(r["trait_a"], anc, ARM),
        "sumstats_b": r4paths.sumstats_path(r["trait_b"], anc, ARM),
        "priors": r4cmd.COLOC_PRIORS,
        "traits": r4cmd.TRAIT_MANIFEST,
        "regions": r4paths.regions_csv(),
        "script": r4cmd.COLOC_SCRIPT,
    }
    if mode != "A1_allvars":
        d["fit_a"] = r4paths.fit_rds(ARM, r["trait_a"], anc, reg)
        d["fit_b"] = r4paths.fit_rds(ARM, r["trait_b"], anc, reg)
    return d


def R4_COLOC_TARGETS(arm):
    """Every coloc output of one arm's invocation (A1 rows included for the A3 arms)."""
    rows = [r for r in R4_COLOC_ROWS.values() if r["ancestry"] in arm_ancestries(arm)]
    modes = ["susie"] + (["A1_matched", "A1_allvars"] if arm in r4cmd.A1_FIT_ARMS else [])
    return [r4cmd.coloc_output(arm, r, k, m) for r in rows for k in r4cmd.P12_KEYS for m in modes]


rule r4_coloc_pair:
    input:
        unpack(lambda w: _r4_coloc_inputs(w, "susie")),
    output:
        r4paths.coloc_json(ARM, "{row_id}", "{p12key}"),
    log:
        f"data/r4/logs/{ARM}/coloc/{{row_id}}.{{p12key}}.log",
    wildcard_constraints:
        row_id="[A-Za-z0-9_]+",
        p12key="|".join(r4cmd.P12_KEYS),
    conda:
        _R4_COLOC_ENV
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    params:
        cmd=lambda w: shlex.join(r4cmd.coloc_command(ARM, _r4_coloc_row(w, arm_ancestries(ARM)), w.p12key, "susie")),
    shell:
        "{params.cmd} > {log} 2>&1"


if ARM in r4cmd.A1_FIT_ARMS:

    rule r4_coloc_A1:
        input:
            unpack(lambda w: _r4_coloc_inputs(w, f"A1_{w.varset}")),
        output:
            r4paths.coloc_json(f"A1_{r4cmd.A1_FIT_ARMS[ARM]}", "{row_id}", "{p12key}", "{varset}"),
        log:
            f"data/r4/logs/A1_{r4cmd.A1_FIT_ARMS[ARM]}/coloc/{{row_id}}.{{varset}}.{{p12key}}.log",
        wildcard_constraints:
            row_id="[A-Za-z0-9_]+",
            p12key="|".join(r4cmd.P12_KEYS),
            varset="matched|allvars",
        conda:
            _R4_COLOC_ENV
        threads: 1
        resources:
            mem_mb=config["resources"]["default_mem_mb"],
        params:
            cmd=lambda w: shlex.join(r4cmd.coloc_command(
                ARM, _r4_coloc_row(w, (r4cmd.A1_FIT_ARMS[ARM],)), w.p12key, f"A1_{w.varset}")),
        shell:
            "{params.cmd} > {log} 2>&1"
