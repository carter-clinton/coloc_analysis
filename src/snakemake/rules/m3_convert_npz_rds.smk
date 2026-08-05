"""M3 AoU AFR .npz -> .rds conversion rule.

Plan: m3-03-W3-ncsu-ingest-and-resolver Task 2; DE-STALED by m3-04c Task 2.

AFR-ONLY. Mirrors ``src/snakemake/rules/ld_reference.smk``
``build_ld_rds_1kg_eur`` rule convention. ``build_ld_rds_aou_afr`` backs the R
script ``src/scripts/ld_npz_to_rds.R``, which handles chr-prefix stripping +
GRCh38 -> GRCh37 variant ID liftover via the UCSC chain at
``data/external/liftover/hg38ToHg19.over.chain.gz`` (DEC-2026-04-24-01).

Output convention:
    data/processed/ld_reference/AFR_aou/{region_id}.rds

That path is the head of the ``config['ld_panel'][AFR]`` fallback chain in
``config/pipeline.yaml`` (RESEARCH Q7); ``finemap.smk``'s
``run_finemap.input.ld_matrix`` walks the chain via
``src/python/ld_panel.py::resolve_ld_path()``, and m3-04c Task 1b threads that
resolved path into ``run_susie_rss.R`` as ``--ld-file`` so the artifact is
actually OPENED and not merely declared.

The EUR head is ``EUR_ukbb_pub``, NOT ``EUR_aou`` -- see the retirement note
below the AFR rule.

``region_id`` spans the 276 unique ids in ``config/ld_regions.tsv``, 123 of
which are m3-02b subregion splits (``m2_region_00040__sub14`` is the panel
Task 1a's crosswalk selects for the Track A anchor ``SH2B3_12q24``).

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
        region_id matches the M2 manifest convention, INCLUDING the m3-02b
        subregion splits: "m2_region_NNNNN" or "m2_region_NNNNN__subKK".
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
        # m3-04c Task 2: admit the m3-02b subregion splits. The old
        # r"m2_region_\d{5}" silently excluded 123 of the 276 manifest ids --
        # including m2_region_00040__sub14, the Track A anchor's panel.
        region_id=r"m2_region_\d{5}(__sub\d{2})?",
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
# RETIRED RULE: `build_ld_rds_aou_eur` (removed by m3-04c Task 2, 2026-08-05)
#
# It converted data/interim/aou_ld_exports/EUR_aou/{region_id}.npz ->
# data/processed/ld_reference/EUR_aou/{region_id}.rds.
#
# WHY IT IS GONE. m3-02e Move 2 (the Wave-2 cost re-architecture) made the
# PUBLIC UKBB 337k panel the ld_panel.EUR chain head in config/pipeline.yaml:
# `EUR_ukbb_pub`, built on NC State for $0 by
#     src/snakemake/rules/m3_public_eur_ld.smk   <- the LIVE EUR producer
# (Carter's call: a 337k public panel is better matched to the external EUR
# GWAS than an AoU 220k panel, and it costs nothing). No EUR LD is computed
# inside the AoU perimeter, so data/interim/aou_ld_exports/EUR_aou/ is never
# populated and this rule could only ever fail on a missing input -- while
# still advertising, in the DAG, a panel that does not exist.
#
# VERIFIED BEFORE REMOVAL: `build_ld_rds_aou_eur` had no code or test
# references anywhere outside .planning/ documentation.
#
# The AoU ingest side is AFR-only for the same reason -- see the ancestry
# wildcard constraints in src/snakemake/rules/m3_ingest_aou_ld.smk.
# ---------------------------------------------------------------------------
