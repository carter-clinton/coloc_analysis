"""Sumstats download and harmonization rules.

Refactored from src/legacy/region_analysis/workflow/rules/sumstats.smk.
All paths parameterized via config["paths"] (D-09, D-10).
Conda directives point to envs/ relative to project root (D-25).
"""

import os
import sys
from pathlib import Path

# Import dataset_descriptor from legacy scripts (available on sys.path)
# We set up the path so the legacy helper can be found
_LEGACY_SCRIPTS = os.path.join("src", "legacy", "region_analysis")
if _LEGACY_SCRIPTS not in sys.path:
    sys.path.insert(0, _LEGACY_SCRIPTS)

from scripts.dataset_config import dataset_descriptor

DATASETS_CONFIG_PATH = os.path.join("config", "datasets.yaml")
PYTHON_BIN = sys.executable
RAW_SUMSTATS_TEMPLATE = os.path.join(
    config["paths"]["raw_sumstats"],
    "{trait}.{ancestry}.raw.gz",
)
HARMONIZED_SUMSTATS_TEMPLATE = os.path.join(
    config["paths"]["harmonized_sumstats"],
    "{trait}.{ancestry}.tsv.bgz",
)


def dataset_meta(wildcards):
    """Look up dataset metadata for a trait/ancestry pair."""
    return dataset_descriptor(
        trait=wildcards.trait,
        ancestry=wildcards.ancestry,
        config_path=DATASETS_CONFIG_PATH,
        dataset_priority=config.get("dataset_priority", {}),
    )


rule download_sumstats:
    output:
        raw=RAW_SUMSTATS_TEMPLATE,
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    run:
        import hashlib
        import gzip
        import requests
        import shutil
        import zipfile
        from pathlib import Path

        os.makedirs(config["paths"]["raw_sumstats"], exist_ok=True)
        meta = dataset_meta(wildcards)
        cache_root = Path(config["paths"].get("cache_downloads", "cache/downloads"))
        candidate_paths = []
        if meta.get("local_path"):
            candidate_paths.append(Path(meta["local_path"]))
        candidate_paths.append(cache_root / meta["dataset"] / Path(meta["path"]).name)

        local_source = None
        for cand in candidate_paths:
            cand = cand.expanduser()
            if cand.is_file():
                local_source = cand
                break

        tmp_path = Path(str(output.raw) + ".tmp")
        if local_source:
            print(f"[download_sumstats] Using staged file {local_source} for {meta['dataset']}")
            shutil.copyfile(local_source, tmp_path)
        else:
            try:
                with requests.get(meta["url"], stream=True) as resp:
                    resp.raise_for_status()
                    with open(tmp_path, "wb") as handle:
                        for chunk in resp.iter_content(chunk_size=1 << 19):
                            if chunk:
                                handle.write(chunk)
            except requests.RequestException as err:
                hint = candidate_paths[0]
                raise RuntimeError(
                    f"Failed to download {meta['url']} for trait {wildcards.trait} "
                    f"(ancestry {wildcards.ancestry}). "
                    f"Please place the file at {hint} and rerun."
                ) from err

        expected_md5 = (meta.get("md5") or "").strip()
        if expected_md5:
            hasher = hashlib.md5()
            with open(tmp_path, "rb") as handle:
                for chunk in iter(lambda: handle.read(8192), b""):
                    if not chunk:
                        break
                    hasher.update(chunk)
            digest = hasher.hexdigest()
            if digest.lower() != expected_md5.lower():
                raise ValueError(
                    f"MD5 mismatch for {meta['url']}: expected {expected_md5}, observed {digest}"
                )

        is_zip = meta["path"].lower().endswith(".zip")
        if is_zip:
            with zipfile.ZipFile(tmp_path, "r") as archive:
                members = [m for m in archive.namelist() if not m.endswith("/")]
                member_name = meta.get("zip_member") or (members[0] if members else None)
                if not member_name:
                    raise ValueError(f"No file entries found inside zip archive {meta['path']}")
                if member_name not in archive.namelist():
                    raise ValueError(
                        f"Requested member '{member_name}' not found in archive {meta['path']}"
                    )
                with archive.open(member_name) as src, gzip.open(output.raw, "wb") as dest:
                    shutil.copyfileobj(src, dest)
            tmp_path.unlink()
        else:
            tmp_path.replace(output.raw)


rule harmonize_sumstats:
    input:
        raw=RAW_SUMSTATS_TEMPLATE,
        datasets_config=DATASETS_CONFIG_PATH,
    output:
        harmonized=HARMONIZED_SUMSTATS_TEMPLATE,
    conda:
        "envs/python_stats.yml"
    threads: 2
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    params:
        dataset_name=lambda wildcards: dataset_meta(wildcards)["dataset"],
        harmonized_dir=config["paths"]["harmonized_sumstats"],
        genome_build=config["genome_build"],
    shell:
        r"""
        mkdir -p {params.harmonized_dir}
        TMP_OUT={output.harmonized}.tmp
        {PYTHON_BIN} src/legacy/region_analysis/scripts/harmonize_sumstats.py \
            --input {input.raw} \
            --output $TMP_OUT \
            --trait {wildcards.trait} \
            --ancestry {wildcards.ancestry} \
            --build {params.genome_build} \
            --dataset-name {params.dataset_name} \
            --datasets-config {input.datasets_config}
        tail -n +2 $TMP_OUT | sort -k1,1 -k2,2n > $TMP_OUT.sorted
        head -n 1 $TMP_OUT > $TMP_OUT.header
        cat $TMP_OUT.header $TMP_OUT.sorted > $TMP_OUT
        rm $TMP_OUT.sorted $TMP_OUT.header
        bgzip -f $TMP_OUT
        mv $TMP_OUT.gz {output.harmonized}
        tabix -f -S 1 -s 1 -b 2 -e 2 {output.harmonized}
        """


rule validate_sumstats:
    """Check that harmonized sumstats contain required columns.

    Stub validation rule -- confirms the harmonized output has the expected
    column schema before downstream rules consume it.
    """
    input:
        harmonized=HARMONIZED_SUMSTATS_TEMPLATE,
    output:
        report=os.path.join(
            config["paths"]["results_root"],
            "qc",
            "sumstats_validation",
            "{trait}.{ancestry}.validation.tsv",
        ),
    conda:
        "envs/python_stats.yml"
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    shell:
        r"""
        mkdir -p $(dirname {output.report})
        {PYTHON_BIN} -c "
import gzip, sys
required = ['CHR', 'POS', 'REF', 'ALT', 'BETA', 'SE', 'P']
with gzip.open('{input.harmonized}', 'rt') as f:
    header = f.readline().strip().split('\t')
missing = [c for c in required if c not in header]
with open('{output.report}', 'w') as out:
    out.write('trait\tancestry\tstatus\tmissing_columns\n')
    status = 'PASS' if not missing else 'FAIL'
    out.write('{wildcards.trait}\t{wildcards.ancestry}\t' + status + '\t' + ','.join(missing) + '\n')
if missing:
    print(f'WARNING: Missing columns: {{missing}}', file=sys.stderr)
    sys.exit(1)
"
        """
