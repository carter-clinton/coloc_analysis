"""M3 Wave 3 NCSU-side AoU LD-export ingest rule.

Plan: m3-03-W3-ncsu-ingest-and-resolver, Task 2.

Carter exports per-chromosome LD bundles from the AoU Workspace bucket
(gs://${WORKSPACE_BUCKET}/ld/{ANCESTRY}_aou/) to NCSU GPFS at
``data/interim/aou_ld_exports/{ANCESTRY}_aou/``. The bundles arrive as
loose ``.npz`` files (Path A.1 / A.2) plus optional sharded BlockMatrix
directories under ``bm/`` (Path A.3 large/xlarge regions per D-M3-09).

This rule files a per-chromosome ``.aou_export_complete.{ancestry}.{chr}``
flag once Carter has confirmed the bundle is on disk and inventory matches
the M2 region manifest. Downstream rules in m3_convert_npz_rds.smk can then
fire to convert each region's ``.npz`` to its canonical ``.rds``.

Pattern reuse: mirrors ``src/snakemake/rules/m1_download.smk`` lines 46-62
flag-driven download rule convention. Differs only in the inventory check
on top of the touch -- LD bundles must contain every M2 region for the
chromosome × ancestry cell.

Conda env: envs/m3-aou-dev.yml -- the rule's `run` block uses pandas (in
the env) for manifest reading; no Hail required for the inventory check.

T-M3-EGR-W3 disposition (info disclosure): ACCEPT. The rule operates only
on already-egressed bundles; no AoU access required at inventory time.
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

# Conda env (absolute path so --use-conda resolves regardless of including Snakefile)
M3_AOU_DEV_ENV = str(_M3_PROJECT_ROOT / "envs" / "m3-aou-dev.yml")

# Path-parameterized export landing + .rds destination roots.
# config["paths"].get("ld_interim", default) keeps the rule running when
# pipeline.yaml does not yet list an explicit ld_interim key (M3 Wave 0
# left this key implicit; resolver default is "data/interim/aou_ld_exports").
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

# M2 region manifest path (322 rows, region × ancestry per D-M3-02).
LD_REGIONS_MANIFEST = str(
    _M3_PROJECT_ROOT
    / Path(
        # Allow override via config; default to the Wave 0 emitted path.
        (config.get("ld_regions_manifest", "config/ld_regions.tsv")  # type: ignore[name-defined]
         if "config" in dir() else "config/ld_regions.tsv")
    )
)


# ---------------------------------------------------------------------------
# Rule: m3_ingest_aou_export_arrives
#
# Flag-driven inventory rule. Carter `gsutil cp -r` the chromosome's bundle
# from the AoU workspace bucket to data/interim/aou_ld_exports/{ANCESTRY}_aou/
# then touches an "arrived" marker (or runs `snakemake m3_ingest_aou_export_arrives`
# manually). The rule verifies that every M2 region for the chromosome ×
# ancestry cell has a corresponding .npz file on disk before stamping the
# completion flag.
# ---------------------------------------------------------------------------
rule m3_ingest_aou_export_arrives:
    """Verify per-chromosome × ancestry .npz bundle is complete and stamp flag.

    Output:
        flag = data/interim/aou_ld_exports/.aou_export_complete.{ancestry}.{chr}

    The flag is the gate consumed by downstream conversion rules (Wave 4
    production fire). Until the flag exists, snakemake will not attempt
    to convert that chromosome × ancestry cell.

    Wildcard constraints:
        ancestry in {AFR, EUR}
        chr      in {1..22, X}
    """
    output:
        flag=os.path.join(
            LD_INTERIM,
            ".aou_export_complete.{ancestry}.{chr}",
        ),
    params:
        npz_dir=lambda wildcards: os.path.join(
            LD_INTERIM, f"{wildcards.ancestry}_aou"
        ),
        manifest=LD_REGIONS_MANIFEST,
    wildcard_constraints:
        ancestry=r"AFR|EUR",
        chr=r"[0-9]+|X",
    # NOTE: Snakemake disallows `conda:` with `run:` directives. The
    # inventory check uses pandas which must be available in the parent
    # Snakemake env (smoke_dev: Snakemake 7.32.4 + Python 3.11 already
    # carries pandas). M3_AOU_DEV_ENV is referenced by Wave 4 production
    # rules (which use shell:) elsewhere, not by this inventory check.
    resources:
        mem_mb=2000,
        runtime=60,
    run:
        import pandas as pd  # noqa: WPS433 -- in parent Snakemake env

        npz_dir = Path(params.npz_dir)
        if not npz_dir.is_dir():
            raise FileNotFoundError(
                f"AoU export landing dir missing for {wildcards.ancestry} "
                f"chr {wildcards.chr}: {npz_dir}"
            )

        manifest_path = Path(params.manifest)
        if not manifest_path.is_file():
            raise FileNotFoundError(
                f"ld_regions manifest missing: {manifest_path}; "
                f"run M3 Wave 0 build_ld_region_manifest.py first"
            )

        manifest = pd.read_csv(manifest_path, sep="\t")
        chr_int = (
            int(wildcards.chr)
            if wildcards.chr.isdigit()
            else wildcards.chr
        )
        sub = manifest[
            (manifest["chr"] == chr_int)
            & (manifest["ancestry"] == wildcards.ancestry)
        ]
        expected_regions = set(sub["region_id"].tolist())
        if not expected_regions:
            raise ValueError(
                f"manifest has no rows for {wildcards.ancestry} chr "
                f"{wildcards.chr}; expected at least one region"
            )

        present = {p.stem for p in npz_dir.glob("*.npz")}
        missing = sorted(expected_regions - present)
        if missing:
            raise FileNotFoundError(
                f"chr {wildcards.chr} {wildcards.ancestry} bundle missing "
                f"{len(missing)} region(s): {missing[:5]}"
                + ("..." if len(missing) > 5 else "")
            )

        # Stamp the completion flag.
        flag_path = Path(output.flag)
        flag_path.parent.mkdir(parents=True, exist_ok=True)
        flag_path.touch()


# ---------------------------------------------------------------------------
# Convenience aggregate target: every chromosome × ancestry cell covered.
# Wave 4 production fire consumes this; not in ALL_TARGETS by default since
# it requires manual gsutil cp first.
# ---------------------------------------------------------------------------
rule m3_ingest_aou_export_arrives_all:
    """Aggregate marker: every per-chromosome × ancestry export flag present."""
    input:
        # 22 autosomes × 2 ancestries (AFR + EUR). chr X is excluded for now;
        # M2 union BED restricts to autosomes per D-M2-09.
        flags=expand(
            os.path.join(
                LD_INTERIM, ".aou_export_complete.{ancestry}.{chr}"
            ),
            ancestry=["AFR", "EUR"],
            chr=[str(i) for i in range(1, 23)],
        ),
    output:
        sentinel=os.path.join(LD_INTERIM, ".aou_export_arrives_all.complete"),
    shell:
        r"""touch {output.sentinel}"""


# ---------------------------------------------------------------------------
# Helper function: lookup a region's chromosome from the M2 manifest. Used by
# m3_aou_npz_arrives below to express the per-region .npz dependency on the
# per-chromosome export-arrives flag (which is the actual gsutil cp gate).
# Memoized so repeated calls during DAG construction don't re-read the TSV.
# ---------------------------------------------------------------------------
_REGION_TO_CHR_AND_ANCESTRIES: dict[str, set[str]] = {}
_REGION_TO_CHR: dict[str, str] = {}


def _load_region_to_chr_index() -> None:
    """Memoized read of LD_REGIONS_MANIFEST -> region_id -> chr index.

    Idempotent; cheap to call repeatedly during DAG construction.
    """
    if _REGION_TO_CHR:
        return
    try:
        manifest_path = Path(LD_REGIONS_MANIFEST)
        if not manifest_path.is_file():
            return
        with manifest_path.open("r", encoding="utf-8") as fh:
            header = fh.readline().rstrip("\r\n").split("\t")
            try:
                ix_region = header.index("region_id")
                ix_chr = header.index("chr")
            except ValueError:
                return
            for line in fh:
                cols = line.rstrip("\r\n").split("\t")
                if len(cols) <= max(ix_region, ix_chr):
                    continue
                region = cols[ix_region]
                chrom = cols[ix_chr]
                if region and chrom:
                    _REGION_TO_CHR.setdefault(region, chrom)
    except Exception:  # noqa: BLE001 -- DAG-construction-time helper must not crash parsing
        return


def _region_chr(region_id: str) -> str | None:
    """Return chromosome string for a region_id, or None if not in manifest."""
    _load_region_to_chr_index()
    return _REGION_TO_CHR.get(region_id)


# ---------------------------------------------------------------------------
# Rule: m3_aou_npz_arrives
#
# Per-region .npz "arrives" rule. The .npz itself is produced manually by
# Carter (gsutil cp -r from AoU workspace bucket); this rule wires the .npz
# dependency to the per-chromosome export-arrives flag so the DAG can plan
# all 322 cells against the flag set rather than 322 individual files.
#
# At dry-run time, the chain
#   .rds -> .npz -> .aou_export_complete.{ancestry}.{chr} -> (manual)
# resolves cleanly. At apply time, the rule fails fast if the flag exists
# but the actual .npz is missing -- which is the expected error: Carter's
# gsutil cp didn't land the file.
# ---------------------------------------------------------------------------
rule m3_aou_npz_arrives:
    """Per-region .npz arrival sentinel; depends on per-chr export flag.

    Snakemake will not run this rule unless invoked manually with
    ``--touch`` or with the .npz already present on disk; its purpose is to
    let the DAG plan from .rds back to the chromosome flag without a
    MissingInputException. Carter's manual ``gsutil cp -r`` is the actual
    file-producer.
    """
    input:
        flag=lambda wildcards: os.path.join(
            LD_INTERIM,
            ".aou_export_complete.{ancestry}.{chr}",
        ).format(
            ancestry=wildcards.ancestry,
            chr=_region_chr(wildcards.region_id) or "UNKNOWN",
        ),
    output:
        npz=os.path.join(LD_INTERIM, "{ancestry}_aou", "{region_id}.npz"),
    wildcard_constraints:
        ancestry=r"AFR|EUR",
        region_id=r"m2_region_\d{5}",
    resources:
        mem_mb=500,
        runtime=15,
    shell:
        r"""
        set -euo pipefail
        if [ ! -f {output.npz} ]; then
            echo "ERROR: expected {output.npz} on disk but it is missing." >&2
            echo "Carter must gsutil cp -r the AoU export bundle for chr"  >&2
            echo "        $(basename {input.flag} | cut -d. -f3-) to       " >&2
            echo "        $(dirname  {output.npz})                          " >&2
            exit 1
        fi
        # Touch to update mtime so downstream rules re-fire if needed.
        touch {output.npz}
        """
