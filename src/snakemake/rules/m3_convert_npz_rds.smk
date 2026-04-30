"""M3 Wave 3 .npz -> .rds conversion rules.

Plan: m3-03-W3-ncsu-ingest-and-resolver, Task 2.

Mirrors ``src/snakemake/rules/ld_reference.smk`` ``build_ld_rds_1kg_eur`` rule
convention. Two parallel rules -- ``build_ld_rds_aou_afr`` and
``build_ld_rds_aou_eur`` -- both back the same R script
(``src/scripts/ld_npz_to_rds.R``). The R script handles chr-prefix
stripping + GRCh38 -> GRCh37 variant ID liftover via the UCSC chain at
``data/external/liftover/hg38ToHg19.over.chain.gz`` (DEC-2026-04-24-01).

Output convention:
    data/processed/ld_reference/AFR_aou/{region_id}.rds
    data/processed/ld_reference/EUR_aou/{region_id}.rds

These paths match the head of the ``config['ld_panel'][AFR]`` / ``[EUR]``
fallback chains in ``config/pipeline.yaml`` (RESEARCH Q7); ``finemap.smk``'s
``run_finemap.input.ld_matrix`` walks the chain via
``src/python/ld_panel.py::resolve_ld_path()``.

Conda env: envs/m3-r-ld.yml (r-base + reticulate + Matrix + jsonlite +
digest + numpy + pyliftover; built once per Wave 3).
"""
from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Workflow-basedir-anchored paths (mirrors m1_download.smk + ld_reference.smk
# absolute-path conda-env workaround per DEF-01-01).
# ---------------------------------------------------------------------------
try:
    _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
except NameError:
    _BASE = Path(os.getcwd())


def _find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(6):
        if (cur / "config" / "pipeline.yaml").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start


_M3_PROJECT_ROOT = _find_project_root(_BASE)

# Conda env (absolute path; DEF-01-01 workaround)
M3_R_LD_ENV = str(_M3_PROJECT_ROOT / "envs" / "m3-r-ld.yml")

# Path-parameterized roots
try:
    LD_INTERIM = config["paths"].get(  # type: ignore[name-defined]
        "ld_interim", "data/interim/aou_ld_exports"
    )
except (NameError, KeyError):
    LD_INTERIM = "data/interim/aou_ld_exports"

try:
    LD_REF_DIR = config["paths"]["ld_reference"]  # type: ignore[name-defined]
except (NameError, KeyError):
    LD_REF_DIR = "data/processed/ld_reference"

# Liftover chain (DEC-2026-04-24-01: AoU emits GRCh38; project canonical
# analytic plane is GRCh37; the ld_npz_to_rds.R script applies the chain).
LIFTOVER_CHAIN_38_TO_37 = "data/external/liftover/hg38ToHg19.over.chain.gz"

# Converter script (relative to project root; Snakemake invokes from project
# cwd so the relative path resolves correctly).
LD_NPZ_TO_RDS_SCRIPT = "src/scripts/ld_npz_to_rds.R"


# ---------------------------------------------------------------------------
# Rule: build_ld_rds_aou_afr
# ---------------------------------------------------------------------------
rule build_ld_rds_aou_afr:
    """Convert AoU AFR LD .npz -> .rds with GRCh38 -> GRCh37 variant ID liftover.

    Input:
        npz   = data/interim/aou_ld_exports/AFR_aou/{region_id}.npz
        chain = data/external/liftover/hg38ToHg19.over.chain.gz
    Output:
        rds   = data/processed/ld_reference/AFR_aou/{region_id}.rds

    Conda env: envs/m3-r-ld.yml.

    Wildcard constraints:
        region_id matches the M2 manifest convention "m2_region_NNNNN".
    """
    input:
        npz=os.path.join(LD_INTERIM, "AFR_aou", "{region_id}.npz"),
        chain=LIFTOVER_CHAIN_38_TO_37,
        rscript=LD_NPZ_TO_RDS_SCRIPT,
    output:
        rds=os.path.join(LD_REF_DIR, "AFR_aou", "{region_id}.rds"),
    log:
        "logs/ld_reference/aou_afr/{region_id}.log",
    wildcard_constraints:
        region_id=r"m2_region_\d{5}",
    conda:
        M3_R_LD_ENV
    threads: 1
    resources:
        mem_mb=8000,
        runtime=120,
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.rds}) $(dirname {log})
        Rscript {input.rscript} {input.npz} {output.rds} {input.chain} \
            > {log} 2>&1
        """


# ---------------------------------------------------------------------------
# Rule: build_ld_rds_aou_eur
# ---------------------------------------------------------------------------
rule build_ld_rds_aou_eur:
    """Convert AoU EUR LD .npz -> .rds with GRCh38 -> GRCh37 variant ID liftover.

    Input:
        npz   = data/interim/aou_ld_exports/EUR_aou/{region_id}.npz
        chain = data/external/liftover/hg38ToHg19.over.chain.gz
    Output:
        rds   = data/processed/ld_reference/EUR_aou/{region_id}.rds

    Conda env: envs/m3-r-ld.yml.

    Wildcard constraints:
        region_id matches the M2 manifest convention "m2_region_NNNNN".
    """
    input:
        npz=os.path.join(LD_INTERIM, "EUR_aou", "{region_id}.npz"),
        chain=LIFTOVER_CHAIN_38_TO_37,
        rscript=LD_NPZ_TO_RDS_SCRIPT,
    output:
        rds=os.path.join(LD_REF_DIR, "EUR_aou", "{region_id}.rds"),
    log:
        "logs/ld_reference/aou_eur/{region_id}.log",
    wildcard_constraints:
        region_id=r"m2_region_\d{5}",
    conda:
        M3_R_LD_ENV
    threads: 1
    resources:
        mem_mb=8000,
        runtime=120,
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.rds}) $(dirname {log})
        Rscript {input.rscript} {input.npz} {output.rds} {input.chain} \
            > {log} 2>&1
        """
