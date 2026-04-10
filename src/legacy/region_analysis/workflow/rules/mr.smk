import sys

PYTHON_BIN = sys.executable


rule build_mr_manifest:
    input:
        harmonized=HARMONIZED_ALL
    output:
        manifest="results/mr/mr_manifest.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/create_mr_design.py \
            --harmonized {input.harmonized} \
            --config config/config.yaml \
            --output {output.manifest}
        """


rule run_mr_placeholder:
    input:
        manifest="results/mr/mr_manifest.tsv"
    output:
        done="results/mr/placeholder.done"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
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
