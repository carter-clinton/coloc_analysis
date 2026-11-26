"""Print {rule: conda_env} from Snakemake 7.32.4's own parse of <repo>/Snakefile.ta_r4 (test 15's truth source).

Usage (cwd = repo): python3.11 rule_conda_envs.py <repo> <arm>. An in-process Workflow + include: no DAG, no params
lambda evaluated, no rule_gate / is_r_coloc_env call."""
import json
import os
import sys
from pathlib import Path


def main(repo, arm):
    repo = Path(repo).resolve()
    sys.path.insert(0, str(repo / "src/python"))
    from snakemake.workflow import Workflow
    from ta_r4 import job_guard

    snakefile = str(repo / "Snakefile.ta_r4")
    wf = Workflow(snakefile=snakefile,
                  overwrite_configfiles=[os.path.abspath(repo / p) for p in job_guard.CONFIG_FILES(arm)],
                  overwrite_config=job_guard.merged_config_from_files(repo, arm), config_args=None)
    wf.include(snakefile, overwrite_default_target=True)
    out = {}
    for rule in wf.rules:
        env = rule.conda_env
        out[rule.name] = env if isinstance(env, str) or env is None else "<non-str:" + type(env).__name__ + ">"
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main(*sys.argv[1:3])
