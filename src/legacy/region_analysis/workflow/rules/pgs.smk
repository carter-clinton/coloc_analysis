import sys

PYTHON_BIN = sys.executable


rule build_pgs_manifest:
    input:
        harmonized=HARMONIZED_ALL
    output:
        manifest="results/pgs/pgs_manifest.tsv"
    conda:
        "../../envs/snakemake_env.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"]
    shell:
        r"""
        {PYTHON_BIN} scripts/create_pgs_manifest.py \
            --harmonized {input.harmonized} \
            --config config/config.yaml \
            --output {output.manifest}
        """


rule run_pgs_placeholder:
    input:
        manifest="results/pgs/pgs_manifest.tsv"
    output:
        done="results/pgs/placeholder.done"
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
counts = df.groupby(["method", "target_ancestry"]).size().to_dict()
print("[pgs] Jobs queued: %s :: breakdown %s" % (len(df), counts))
Path("{output.done}").write_text("pgs placeholder complete\n")
PY
        """
