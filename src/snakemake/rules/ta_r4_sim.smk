"""ta-r4 E8 simulation calibration (D-23, D-26): simulate_coloc_r4.R per (region, scenario, generation panel).

Production only (lock gate first); defined only in the A3_1kg invocation. 10 regions x 5 scenarios x 2 panels = 100
jobs. The rule never passes --reps-override (smoke only).
"""

import re
import shlex

import yaml

from ta_r4 import commands as r4cmd

R4_SIM_CONFIG = "config/ta_r4/simulation.yaml"
R4_SIM_SCRIPT = "src/snakemake/scripts/ta_r4/simulate_coloc_r4.R"
with open(Path(workflow.basedir) / R4_SIM_CONFIG) as _fh:
    R4_SIM = yaml.safe_load(_fh)


def _r4_sim_inputs(w):
    gate = gate_input(w)  # lock gate first: production refuses before any path is resolved
    return {
        "gate": gate,
        "fit_panel": f"data/r4/ld/{R4_SIM['fit_panel']}/{w.region}.rds",
        "gen_panel": f"data/r4/ld/{R4_SIM['gen_panels'][w.gen]}/{w.region}.rds",
        "config": R4_SIM_CONFIG,
        "priors": r4cmd.COLOC_PRIORS,
        "policy": ARMS["A3_1kg"]["policy"],
        "script": R4_SIM_SCRIPT,
        "coloc_script": r4cmd.COLOC_SCRIPT,
    }


def _r4_sim_cmd(w, input):
    return shlex.join(["Rscript", R4_SIM_SCRIPT, "--fit-panel", input.fit_panel, "--gen-panel", input.gen_panel,
                       "--gen", w.gen, "--scenario", w.scenario, "--region", w.region, "--config", input.config,
                       "--priors", input.priors, "--policy", input.policy,
                       "--credible-set", str(config.get("finemap", {}).get("credible_set", 0.95)),
                       "--out", f"data/r4/results/sim/{w.region}.{w.scenario}.{w.gen}.tsv"])


R4_SIM_TARGETS = [f"data/r4/results/sim/{g}.{s}.{n}.tsv" for g in R4_SIM["regions"] for s in R4_SIM["scenarios"]
                  for n in R4_SIM["gen_panels"]] if ARM == "A3_1kg" else []

if ARM == "A3_1kg":

    rule r4_sim:
        input:
            unpack(_r4_sim_inputs),
        output:
            "data/r4/results/sim/{region}.{scenario}.{gen}.tsv",
        log:
            "data/r4/logs/sim/{region}.{scenario}.{gen}.log",
        wildcard_constraints:
            region="|".join(R4_SIM["regions"]),
            scenario="|".join(re.escape(s) for s in R4_SIM["scenarios"]),
            gen="|".join(R4_SIM["gen_panels"]),
        conda:
            str(Path(workflow.basedir) / "envs" / "r_coloc.yml")
        threads: 1
        resources:
            mem_mb=8000,
        params:
            cmd=_r4_sim_cmd,
        shell:
            "{params.cmd} > {log} 2>&1"

    rule r4_sim_all:
        input:
            R4_SIM_TARGETS,
