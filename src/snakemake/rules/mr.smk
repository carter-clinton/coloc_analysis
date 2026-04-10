"""Mendelian randomization rules.

Refactored from src/legacy/region_analysis/workflow/rules/mr.smk.
All paths parameterized via config["paths"] (D-09, D-10).
Conda directives point to envs/ relative to project root (D-25).
This is a stub/manifest-only rule in the current pipeline.
"""

import sys

PYTHON_BIN = sys.executable
RESULTS_ROOT = config["paths"]["results_root"]
MR_DIR = os.path.join(RESULTS_ROOT, "mr")


rule build_mr_manifest:
    input:
        harmonized=HARMONIZED_ALL,
    output:
        manifest=os.path.join(MR_DIR, "mr_manifest.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/create_mr_design.py \
            --harmonized {input.harmonized} \
            --config config/pipeline.yaml \
            --output {output.manifest}
        """


rule run_mr_placeholder:
    input:
        manifest=os.path.join(MR_DIR, "mr_manifest.tsv"),
    output:
        done=os.path.join(MR_DIR, "placeholder.done"),
    conda:
        "envs/r_coloc.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} - <<'PY'
import pandas as pd
from pathlib import Path
df = pd.read_csv("{input.manifest}", sep="\t")
ready = df[df["status"] == "ready"]
print("[mr] Total hypotheses: %s; ready: %s" % (len(df), len(ready)))
Path("{output.done}").write_text("mr placeholder complete\n")
PY
        """
