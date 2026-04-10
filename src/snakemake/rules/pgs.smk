"""Polygenic score rules.

Refactored from src/legacy/region_analysis/workflow/rules/pgs.smk.
All paths parameterized via config["paths"] (D-09, D-10).
Conda directives point to envs/ relative to project root (D-25).
This is a stub/manifest-only rule in the current pipeline.
"""

import sys

PYTHON_BIN = sys.executable
RESULTS_ROOT = config["paths"]["results_root"]
PGS_DIR = os.path.join(RESULTS_ROOT, "pgs")


rule build_pgs_manifest:
    input:
        harmonized=HARMONIZED_ALL,
    output:
        manifest=os.path.join(PGS_DIR, "pgs_manifest.tsv"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} src/legacy/region_analysis/scripts/create_pgs_manifest.py \
            --harmonized {input.harmonized} \
            --config config/pipeline.yaml \
            --output {output.manifest}
        """


rule run_pgs_placeholder:
    input:
        manifest=os.path.join(PGS_DIR, "pgs_manifest.tsv"),
    output:
        done=os.path.join(PGS_DIR, "placeholder.done"),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        {PYTHON_BIN} - <<'PY'
import pandas as pd
from pathlib import Path
df = pd.read_csv("{input.manifest}", sep="\t")
counts = df.groupby(["method", "target_ancestry"]).size().to_dict()
print("[pgs] Jobs queued: %s :: breakdown %s" % (len(df), counts))
Path("{output.done}").write_text("pgs placeholder complete\n")
PY
        """
