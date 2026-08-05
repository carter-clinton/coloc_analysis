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

OPERATOR SEQUENCE (260805-23d Task 4, blast-radius BLOCKER-C). ``build_ld_rds_aou_afr``
is per-region and nothing reached it from ``rule all``, so a successful fire could
bank 276 ``.npz`` and ``snakemake all`` would still report success off the 1000G
tail. The aggregate marker ``m3_convert_aou_afr_rds_all`` (below) names all 276
``.rds`` in one command. Run, in order::

    snakemake m3_ingest_aou_export_arrives_all   # the manual-egress arrival flags
    snakemake m3_convert_aou_afr_rds_all         # .npz -> .rds, all 276 AFR panels
    snakemake all                                # fine-mapping, resolver now hits AFR_aou

DISCLOSED RESIDUAL: step 2 is NOT optional and NOT automatic. See the banner above
the aggregate rule.
"""
from __future__ import annotations

import csv
import os
import sys
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
# Convenience aggregate target: every AFR AoU panel converted .npz -> .rds.
#
# WHY THIS EXISTS (m3-04c blast radius, BLOCKER-C). resolve_ld_path returns the
# first EXISTING path in the ld_panel chain (src/python/ld_panel.py:87), so a
# not-yet-built chain head is SKIPPED rather than pulled in as a to-be-built
# input, and Snakefile's ALL_TARGETS (:185-209) names no AFR_aou/*.rds. Without
# this target, `snakemake all` after a successful ~11-day fire finds no
# AFR_aou/*.rds, walks the chain down to the 1000G n=661 tail, and reports
# SUCCESS. The per-region rule above IS reachable by explicitly naming a path
# (verified: a clean 3-job DAG for
# data/processed/ld_reference/AFR_aou/m2_region_00040__sub14.rds) -- so the
# missing piece was WIRING, not logic, and this is the one command that names
# all of it.
#
# NOT IN ALL_TARGETS, deliberately, for exactly the reason
# m3_ingest_aou_export_arrives_all is not (m3_ingest_aou_ld.smk:225-246): the
# .npz arrive by a MANUAL egress that runs over weeks, so wiring them into
# `rule all` would make every unrelated run demand an un-egressed AoU panel.
# The operator invokes this explicitly:
#
#     snakemake m3_convert_aou_afr_rds_all
#
# AFTER the per-chromosome arrival flags are filed, and BEFORE `snakemake all`.
#
# DISCLOSED RESIDUAL -- do not overclaim this rule. It makes the conversion
# INVOCABLE AS ONE OPERATOR COMMAND. It does NOT make `snakemake all`
# self-sufficient: resolve_ld_path's first-EXISTING semantics are unchanged, so
# `snakemake all` alone still cannot pull an unbuilt AoU panel into the DAG.
# Making run_finemap depend on the sentinel would force the AoU fire for EVERY
# ancestry, which is worse; changing the resolver is out of scope here.
#
# COVERAGE IS DERIVED, NOT HARDCODED. The input list is read from
# config/ld_regions.tsv and filtered to ancestry == "AFR" -- 276 ids today, 153
# whole regions + 123 m3-02b __sub splits, including m2_region_00040__sub14
# (the Track A anchor SH2B3_12q24's panel). A glob over the .npz directory would
# silently under-cover whenever the egress is incomplete, which is the same
# class of silence as the defect this rule closes. The 276 count is pinned in
# tests/m3/test_convert_aggregate_target.py against the manifest, and any region
# that loses its AFR row is named LOUDLY on stderr below rather than quietly
# shrinking the target set.
# ---------------------------------------------------------------------------
M3_LD_REGIONS_MANIFEST = str(_M3_PROJECT_ROOT / "config" / "ld_regions.tsv")


def _afr_aou_region_ids(manifest_path: str = M3_LD_REGIONS_MANIFEST) -> list[str]:
    """Sorted unique AFR region_ids from the M2 manifest (276 today).

    A missing manifest returns [] rather than raising: the DAG must still build
    on a fresh clone, matching the CURATED_TO_M2 loader's discipline in
    finemap.smk. But an empty or SHRUNKEN target set is never silent -- it is
    the BLOCKER-C failure mode one level down -- so both cases WARN to stderr
    exactly as finemap.smk does for an unloaded crosswalk.
    """
    if not os.path.isfile(manifest_path):
        print(
            "[m3_convert_npz_rds.smk] WARN: LD region manifest not found at "
            f"{manifest_path}; the aggregate target m3_convert_aou_afr_rds_all "
            "covers NOTHING and would exit success having converted zero "
            "panels. Restore config/ld_regions.tsv before the AoU consume.",
            file=sys.stderr,
        )
        return []

    afr: set[str] = set()
    every: set[str] = set()
    with open(manifest_path, "r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            region_id = (row.get("region_id") or "").strip()
            if not region_id:
                continue
            every.add(region_id)
            if (row.get("ancestry") or "").strip() == "AFR":
                afr.add(region_id)

    if not afr:
        print(
            "[m3_convert_npz_rds.smk] WARN: no ancestry == 'AFR' rows in "
            f"{manifest_path} ({len(every)} region ids present); the aggregate "
            "target m3_convert_aou_afr_rds_all covers NOTHING. Verify the "
            "manifest's ancestry column before the AoU consume.",
            file=sys.stderr,
        )
        return []

    # A region present in the manifest but carrying no AFR row SHRINKS the
    # target set. Name it; do not let the aggregate quietly cover less.
    no_afr_row = sorted(every - afr)
    if no_afr_row:
        print(
            "[m3_convert_npz_rds.smk] WARN: "
            f"{len(no_afr_row)} of {len(every)} region ids in {manifest_path} "
            "have no ancestry == 'AFR' row and are therefore NOT covered by "
            f"m3_convert_aou_afr_rds_all: {no_afr_row[:5]}"
            + ("..." if len(no_afr_row) > 5 else ""),
            file=sys.stderr,
        )

    return sorted(afr)


M3_AFR_AOU_RDS = [
    os.path.join(LD_REF_DIR, "AFR_aou", f"{rid}.rds") for rid in _afr_aou_region_ids()
]


rule m3_convert_aou_afr_rds_all:
    """Aggregate marker: every AFR AoU .npz converted to its canonical .rds.

    Not in ALL_TARGETS by design -- see the banner above. Invoke explicitly
    after the egress arrival flags and before `snakemake all`.
    """
    input:
        rds=M3_AFR_AOU_RDS,
    output:
        sentinel=os.path.join(LD_REF_DIR, "AFR_aou", ".convert_all.complete"),
    shell:
        r"""touch {output.sentinel}"""


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
