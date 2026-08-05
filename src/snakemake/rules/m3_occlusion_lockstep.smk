"""M3 exclude-in-LOCKSTEP rules: the occlusion catalog and its consume seam.

Plan: m3-04b-W4-occlusion-catalog-and-consume-seam (Tasks 1 + 2). Discharges the
consume-wiring deferral m3-07c disclosed in
``src/python/drop_occluded_from_sumstats.py:49-56``.

WHY THIS FILE EXISTS
--------------------
The pre-registered policy (osf.io/az52u, file ``trsx5``, POSTED
2026-07-10T13:32:22Z) is EXCLUDE-IN-LOCKSTEP: a variant whose LD is structurally
undefined because an overlapping deletion's REF span covers it leaves the LD panel
AND the harmonized sumstats. Until this file landed, the exclusion was enforced on
the panel ONLY (``occlusion_span_filter.py``, m3-07b) — and panel-only exclusion is
not a smaller version of the policy, it is a different and WRONG one. rs182965575
(GRCh37 ``1:5982778``) is present in 7 of 9 AFR sumstats, so a panel-only drop
ORPHANS it in 7 traits: the LD matrix has never heard of a variant those traits
still carry.

THREE RULES
-----------
``m3_assemble_occlusion_catalog``  Stage-A per-region manifests (+ chain + the 9
    public AFR sumstats) -> ONE genome-wide enriched catalog. This is the production
    caller the four m3-07b/07c functions never had.
``occlusion_filter_sumstats``      the AFR harmonized sumstats mirror, occlusion-filtered,
    re-bgzipped and tabix-indexed.
``occlusion_filter_variants``      the per-region variant list, occlusion-filtered with
    the SAME function and the SAME catalog.

BOTH consume seams are repointed, not one. ``ld_reference.smk::collect_region_variants``
pools every harmonized file ancestry-agnostically into
``{ld_reference}/variants/{region}.tsv``, so filtering only the sumstats would let
``run_finemap.input.variants`` re-introduce the occluded coordinate through the back
door.

RUNNABLE TODAY, LIVE LATER
--------------------------
There are ZERO per-region manifests on this tree (the AoU fire has banked none), and
the catalog rule is built to succeed in exactly that state:
``assemble_occlusion_catalog`` emits a SCHEMA-COMPLETE header-only catalog, so the
drop is an audited ``n_dropped == 0`` no-op today and becomes live the moment real
manifests land — with zero further wiring. That removes the
wire-it-later-and-forget failure mode this phase has already paid for twice.

⚠ The manifest / excludelist inputs are GLOB-DERIVED AT PARSE TIME. Newly egressed
manifests are picked up on the next Snakemake invocation; if the catalog already
exists it must be removed (or ``--forcerun m3_assemble_occlusion_catalog`` used) for
the new rows to be rolled up. They are declared as rule inputs so an mtime change on
an ALREADY-globbed manifest does trigger a rebuild.

CONDA ENVS. ``m3_assemble_occlusion_catalog`` needs pandas AND pyliftover ->
``envs/m3-r-ld.yml`` (M3_R_LD_ENV). The two filter rules need ``bgzip``/``tabix``,
which live ONLY in ``envs/python_stats.yml`` (htslib=1.21) -> PYTHON_STATS_ENV;
``bgzip`` is NOT on the login PATH.

m3-06 stays HELD: no rule here touches the LD-conditioning path, and the NaN-to-zero
fill it once proposed is DEAD — occluded variants are EXCLUDED with provenance,
never zeroed.
"""
from __future__ import annotations

import glob as _glob
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Workflow-basedir-anchored paths (DEF-01-01 absolute-conda-env convention,
# mirroring m3_convert_npz_rds.smk:29-53).
# ---------------------------------------------------------------------------
try:
    _OCCL_BASE = Path(workflow.basedir)  # type: ignore[name-defined]
except NameError:
    _OCCL_BASE = Path(os.getcwd())


def _occl_find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(6):
        if (cur / "config" / "pipeline.yaml").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start


_OCCL_PROJECT_ROOT = _occl_find_project_root(_OCCL_BASE)

# Conda envs (absolute paths; DEF-01-01 workaround). Same value m3_convert_npz_rds.smk
# assigns, restated here so this file is readable and greppable on its own.
M3_R_LD_ENV = str(_OCCL_PROJECT_ROOT / "envs" / "m3-r-ld.yml")
#: The ONLY env that carries bgzip + tabix (htslib=1.21). sumstats.smk:157 uses it
#: for exactly the same bgzip/tabix pair, so the filtered mirror keeps full parity
#: with the source it shadows.
PYTHON_STATS_ENV = str(_OCCL_PROJECT_ROOT / "envs" / "python_stats.yml")

# ---------------------------------------------------------------------------
# Config-parameterized paths (config/pipeline.yaml :: occlusion_lockstep)
# ---------------------------------------------------------------------------
try:
    _OCCL_CFG = dict(config.get("occlusion_lockstep", {}))  # type: ignore[name-defined]
except NameError:
    _OCCL_CFG = {}

try:
    _OCCL_HARMONIZED_DIR = config["paths"]["harmonized_sumstats"]  # type: ignore[name-defined]
except (NameError, KeyError):
    _OCCL_HARMONIZED_DIR = "data/processed/sumstats_harmonized"

try:
    _OCCL_LD_REF_DIR = config["paths"]["ld_reference"]  # type: ignore[name-defined]
except (NameError, KeyError):
    _OCCL_LD_REF_DIR = "data/processed/ld_reference"

OCCLUSION_CATALOG = _OCCL_CFG.get(
    "catalog", "data/processed/occlusion/occlusion_catalog_m3.tsv"
)
OCCLUSION_SUMSTATS_DIR = _OCCL_CFG.get(
    "sumstats_dir", "data/processed/sumstats_harmonized_occl"
)
OCCLUSION_VARIANTS_DIR = os.path.join(
    _OCCL_LD_REF_DIR, _OCCL_CFG.get("variants_dir_name", "variants_occl")
)
#: The UNFILTERED variant lists collect_region_variants writes
#: (ld_reference.smk:91). Recomputed here rather than imported: ld_reference.smk is
#: included LATER (and only when enable_ld_pipeline is true), so its globals do not
#: exist at this file's parse time.
OCCLUSION_VARIANTS_SRC_DIR = os.path.join(_OCCL_LD_REF_DIR, "variants")

OCCLUSION_MANIFEST_DIR = _OCCL_CFG.get(
    "manifest_dir", "data/interim/aou_ld_exports/AFR_aou"
)
OCCLUSION_EXCLUDELIST_DIR = _OCCL_CFG.get(
    "excludelist_dir", "data/interim/aou_ld_exports/AFR_aou"
)
OCCLUSION_ALLOW_DEGRADED = bool(_OCCL_CFG.get("allow_degraded", False))

#: The M2 region manifest, for the BLOCKER-4 region-coverage check. Config key mirrors
#: m3_ingest_aou_ld.smk:79-80. ⚠ 552 DATA ROWS = 276 unique region_id x 2 ancestries —
#: the assembler derives the expected set with nunique(region_id) filtered to the
#: ancestry, NEVER len(df)/wc -l (which give 552/553 and would fail 100% of the time).
try:
    OCCLUSION_REGIONS_TSV = config.get(  # type: ignore[name-defined]
        "ld_regions_manifest", "config/ld_regions.tsv"
    )
except NameError:
    OCCLUSION_REGIONS_TSV = "config/ld_regions.tsv"

#: Liftover chain (DEC-2026-04-24-01: AoU emits GRCh38, the analytic plane is GRCh37).
OCCLUSION_CHAIN_38_TO_37 = "data/external/liftover/hg38ToHg19.over.chain.gz"

OCCLUSION_ASSEMBLER = "src/python/assemble_occlusion_catalog.py"
OCCLUSION_CLI = "src/python/occlusion_lockstep_cli.py"
OCCLUSION_SRC_PYTHON = "src/python"


def _occl_sorted_glob(*patterns: str) -> list:
    """Sorted, de-duplicated glob over one or more patterns (recursive)."""
    hits: list = []
    for pattern in patterns:
        hits.extend(_glob.glob(pattern, recursive=True))
    return sorted(set(hits))


#: The M3 present-rate scan scope: the 9 REAL public AFR harmonized sumstats,
#: EXCLUDING asthma.AFR.grch38_backup.tsv.bgz (a build-38 backup, not an analytic
#: input — scanning it would put GRCh38 coordinates into a GRCh37 k/n).
OCCLUSION_AFR_SUMSTATS = [
    p for p in _occl_sorted_glob(os.path.join(_OCCL_HARMONIZED_DIR, "*.AFR*.tsv.bgz"))
    if not p.endswith(".grch38_backup.tsv.bgz")
]

#: Per-region Stage-A manifests (``occlusion_manifest.tsv``) egressed from the
#: perimeter. EMPTY on today's tree — see the module docstring.
OCCLUSION_MANIFESTS = _occl_sorted_glob(
    os.path.join(OCCLUSION_MANIFEST_DIR, "**", "*occlusion_manifest*.tsv"),
    os.path.join(OCCLUSION_MANIFEST_DIR, "*occlusion_manifest*.tsv"),
)

#: ``{region_id}.occluded.excludelist`` objects (run_native_ld_panel.py:937). The
#: DEGRADED fallback source; used only when no Stage-A manifest reached NC State,
#: and only with an explicit allow_degraded.
OCCLUSION_EXCLUDELISTS = _occl_sorted_glob(
    os.path.join(OCCLUSION_EXCLUDELIST_DIR, "**", "*.occluded.excludelist"),
    os.path.join(OCCLUSION_EXCLUDELIST_DIR, "*.occluded.excludelist"),
)


def _occl_arg(flag: str, values) -> str:
    """``--flag a b c``, or "" when there is nothing to pass."""
    values = list(values)
    if not values:
        return ""
    return f"{flag} " + " ".join(str(v) for v in values)


# ---------------------------------------------------------------------------
# Rule: m3_assemble_occlusion_catalog  (m3-04b Task 1)
# ---------------------------------------------------------------------------
rule m3_assemble_occlusion_catalog:
    """Assemble the genome-wide enriched reference-occlusion catalog.

    Calls, in order, the four m3-07b/07c functions that shipped with ZERO callers:
    ``aggregate_manifests`` -> ``add_grch37_positions`` -> ``scan_present_rate`` ->
    ``enrich_occlusion_manifest``, then re-asserts the full catalog schema so the
    artifact is usable EVEN WHEN EMPTY.

    Input:
        chain      = data/external/liftover/hg38ToHg19.over.chain.gz
        sumstats   = the 9 public AFR harmonized sumstats (present-rate scan scope)
        manifests / excludelists = glob-derived, EMPTY on today's tree
        regions_tsv = config/ld_regions.tsv — the BLOCKER-4 region-coverage check.
            Passed as --regions-tsv so the check is LIVE in production, not merely
            available. With it the assembler REFUSES to stamp
            provenance_source=stage_a_manifest on a rollup that does not cover every
            region carrying an excludelist (those regions' occluded variants would
            otherwise never be dropped from the sumstats = ORPHANED VARIANTS), and it
            reports n_regions_expected / n_regions_missing. ⚠ The expected set is
            nunique(region_id) filtered to the ancestry = 276, NEVER the file's 552
            data rows.
    Output:
        catalog   = config occlusion_lockstep.catalog
                    (+ a sibling {catalog}.README.md written by the assembler)

    Conda env: envs/m3-r-ld.yml (python 3.11 + pandas + pyliftover).
    """
    input:
        chain=OCCLUSION_CHAIN_38_TO_37,
        sumstats=OCCLUSION_AFR_SUMSTATS,
        manifests=OCCLUSION_MANIFESTS,
        excludelists=OCCLUSION_EXCLUDELISTS,
        regions_tsv=OCCLUSION_REGIONS_TSV,
        script=OCCLUSION_ASSEMBLER,
    output:
        catalog=OCCLUSION_CATALOG,
    log:
        "logs/m3_occlusion/assemble_occlusion_catalog.log",
    params:
        src_python=OCCLUSION_SRC_PYTHON,
        manifest_args=_occl_arg("--manifest", OCCLUSION_MANIFESTS),
        excludelist_args=_occl_arg("--excludelist", OCCLUSION_EXCLUDELISTS),
        sumstats_args=_occl_arg("--sumstats", OCCLUSION_AFR_SUMSTATS),
        degraded_flag="--allow-degraded" if OCCLUSION_ALLOW_DEGRADED else "",
    conda:
        M3_R_LD_ENV
    threads: 1
    resources:
        mem_mb=8000,
        runtime=120,
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.catalog}) $(dirname {log})
        PYTHONPATH={params.src_python}:${{PYTHONPATH:-}} \
        python {input.script} \
            --chain {input.chain} \
            --out {output.catalog} \
            --regions-tsv {input.regions_tsv} \
            {params.sumstats_args} \
            {params.manifest_args} \
            {params.excludelist_args} \
            {params.degraded_flag} \
            > {log} 2>&1
        """


# ---------------------------------------------------------------------------
# Rule: occlusion_filter_sumstats  (m3-04b Task 2)
# ---------------------------------------------------------------------------
rule occlusion_filter_sumstats:
    """The occlusion-filtered AFR harmonized sumstats mirror, bgzipped + tabixed.

    Input:  {harmonized_sumstats}/{stem}.tsv.bgz  +  the occlusion catalog
    Output: {occlusion_lockstep.sumstats_dir}/{stem}.tsv.bgz  (+ .tbi)

    The output directory MUST differ from the input directory
    (``sumstats_harmonized_occl`` vs ``sumstats_harmonized``): a same-directory
    wildcard would make this rule its own input and produce a DAG cycle.

    The ``{stem}`` constraint ends in ``.AFR`` so this rule can NEVER match a EUR
    stem. That is belt-and-braces on top of the ancestry gate in
    ``lockstep_sumstats_path``: Track-A / EUR numerics are frozen, and two
    independent barriers is the right number for a filter that deletes rows from
    scientific data.

    TWO LOGS. ``{stem}.counts.json`` is the durable audit ({n_in, n_dropped,
    n_out}, with n_in - n_dropped == n_out); ``{stem}.drops.log`` captures the
    module's per-drop STDERR, which is the IN-RUN WITNESS the pre-registration
    relies on (the catalog is the durable record, the log is the witness).

    ``tabix -f -S 1 -s 1 -b 2 -e 2`` reproduces ``sumstats.smk:157`` exactly, so
    the mirror keeps full parity with the source it shadows.

    Conda env: envs/python_stats.yml -- the ONLY env carrying bgzip + tabix.
    """
    input:
        sumstats=os.path.join(_OCCL_HARMONIZED_DIR, "{stem}.tsv.bgz"),
        catalog=OCCLUSION_CATALOG,
        script=OCCLUSION_CLI,
    output:
        bgz=os.path.join(OCCLUSION_SUMSTATS_DIR, "{stem}.tsv.bgz"),
        tbi=os.path.join(OCCLUSION_SUMSTATS_DIR, "{stem}.tsv.bgz.tbi"),
    log:
        counts=os.path.join("logs", "m3_occlusion", "{stem}.counts.json"),
        drops=os.path.join("logs", "m3_occlusion", "{stem}.drops.log"),
    wildcard_constraints:
        stem=r"[A-Za-z0-9_.\-]+\.AFR",
    params:
        src_python=OCCLUSION_SRC_PYTHON,
    conda:
        PYTHON_STATS_ENV
    threads: 1
    resources:
        mem_mb=8000,
        runtime=120,
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.bgz}) $(dirname {log.counts})
        PYTHONPATH={params.src_python}:${{PYTHONPATH:-}} \
        python {input.script} filter-sumstats \
            --in {input.sumstats} \
            --catalog {input.catalog} \
            --out {output.bgz} \
            --counts-json {log.counts} \
            2> {log.drops}
        tabix -f -S 1 -s 1 -b 2 -e 2 {output.bgz}
        """


# ---------------------------------------------------------------------------
# Rule: occlusion_filter_variants  (m3-04b Task 2)
# ---------------------------------------------------------------------------
rule occlusion_filter_variants:
    """The occlusion-filtered per-region variant list. Plain TSV in, plain TSV out.

    Input:  {ld_reference}/variants/{region}.tsv  +  the occlusion catalog
    Output: {ld_reference}/{variants_dir_name}/{region}.tsv

    THE SECOND LEAK. ``ld_reference.smk::collect_region_variants`` pools ALL
    harmonized files ancestry-agnostically (OrderedDict dedup over every trait and
    ancestry), so the occluded coordinate survives in the variant list even after
    the AFR sumstats mirror has dropped it. Filtering only the sumstats is not a
    lockstep.

    The variant list is NOT re-filtered per ancestry and is NOT itself
    ancestry-scoped -- ``lockstep_variants_path`` is what decides, per fine-map
    job, whether a given ancestry reads the filtered or the unfiltered list. That
    is deliberate: filtering ``collect_region_variants``'s own INPUTS would drag
    the EUR sumstats through the AFR occlusion filter and move Track-A numerics.

    Same function, same catalog, same (CHR,POS) key as the sumstats drop. No
    second implementation, no second chance to disagree with the panel.
    """
    input:
        variants=os.path.join(OCCLUSION_VARIANTS_SRC_DIR, "{region}.tsv"),
        catalog=OCCLUSION_CATALOG,
        script=OCCLUSION_CLI,
    output:
        variants=os.path.join(OCCLUSION_VARIANTS_DIR, "{region}.tsv"),
    log:
        counts=os.path.join("logs", "m3_occlusion", "variants", "{region}.counts.json"),
        drops=os.path.join("logs", "m3_occlusion", "variants", "{region}.drops.log"),
    wildcard_constraints:
        region=r"[A-Za-z0-9_.\-]+",
    params:
        src_python=OCCLUSION_SRC_PYTHON,
    conda:
        PYTHON_STATS_ENV
    threads: 1
    resources:
        mem_mb=4000,
        runtime=60,
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.variants}) $(dirname {log.counts})
        PYTHONPATH={params.src_python}:${{PYTHONPATH:-}} \
        python {input.script} filter-variants \
            --in {input.variants} \
            --catalog {input.catalog} \
            --out {output.variants} \
            --counts-json {log.counts} \
            2> {log.drops}
        """
