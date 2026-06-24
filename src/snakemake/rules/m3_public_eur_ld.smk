"""m3-02e Move 2: PUBLIC EUR LD ($0 compute) -> EUR_ukbb_pub/{region_safe}.rds.

Builds the M3 EUR LD panel from the PUBLIC Weissbrod/PolyFun UKBB 337k reference
(s3://broad-alkesgroup-ukbb-ld/UKBB_LD/, CC-BY, hg19/GRCh37) instead of computing
EUR LD on AoU. $0 compute: public download + extract only. Pan-UKBB 420k is the
documented alternate (build_public_eur_manifest.EUR_PUBLIC_ALTERNATES).

Flow:
  build_public_eur_manifest.py  -> per-region extract jobs (M2 EUR region ->
      overlapping public 337k tile(s); hg19 window from the manifest's GRCh37
      columns; DEC-2026-04-24-01).
  download_ukbb_ld_tiles.py     -> fetch + extract per-region LD into
      data/processed/ld_reference/EUR_ukbb_pub/{region_safe}.rds + .meta.json.

ENV SPLIT (factual note):
  * The S3 FETCH is AWS boto3 UNSIGNED (anonymous) from s3://broad-alkesgroup-ukbb-ld/
    — NOT a GCS/AoU path — so it runs in envs/ld_build.yml (boto3), the SAME env
    the existing download_ukbb_ld_tiles rule uses (LD_BUILD_ENV).
  * Any .npz->.rds R step uses envs/m3-r-ld.yml (M3_R_LD_ENV), mirroring
    m3_convert_npz_rds.smk.

The resulting EUR_ukbb_pub .rds drops into the SAME loader contract the AFR
native-plink .npz->.rds uses; config/pipeline.yaml ld_panel.EUR chain head is
EUR_ukbb_pub (m3-02e Task 3). The .rds is built by the public-tile extractor
(download_ukbb_ld_tiles.py / ukbb_ld_tile_to_region_rds.py) which already emits
the R/variants/ld_source payload + .meta.json provenance.

DEF-01-01 workaround: conda directives use the absolute env paths (anchored on
workflow.basedir) so --use-conda resolves regardless of the including Snakefile.
"""
from __future__ import annotations

import os
from pathlib import Path

# Workflow-basedir-anchored paths (mirror m3_convert_npz_rds.smk).
try:
    _BASE_PUB_EUR = Path(workflow.basedir)  # type: ignore[name-defined]
except NameError:
    _BASE_PUB_EUR = Path(os.getcwd())


def _find_root_pub_eur(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(6):
        if (cur / "config" / "pipeline.yaml").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start


_PUB_EUR_ROOT = _find_root_pub_eur(_BASE_PUB_EUR)

# Conda envs (absolute; DEF-01-01). ld_build.yml carries boto3 for the UNSIGNED
# S3 fetch; m3-r-ld.yml carries the R/reticulate toolchain for the .rds step.
LD_BUILD_ENV_PUB = str(_PUB_EUR_ROOT / "envs" / "ld_build.yml")
M3_R_LD_ENV_PUB = str(_PUB_EUR_ROOT / "envs" / "m3-r-ld.yml")

try:
    _LD_REF_DIR_PUB = config["paths"]["ld_reference"]  # type: ignore[name-defined]
except (NameError, KeyError):
    _LD_REF_DIR_PUB = "data/processed/ld_reference"

EUR_UKBB_PUB_OUT_DIR = os.path.join(_LD_REF_DIR_PUB, "EUR_ukbb_pub")
EUR_PUB_MANIFEST = "config/ld_regions.tsv"
EUR_PUB_JOBS_TSV = "data/interim/public_eur_ld/eur_pub_extract_jobs.tsv"

# Public panel coordinates (Weissbrod 337k; hg19). Fetched via AWS S3 boto3
# UNSIGNED (anonymous) — broad-alkesgroup-ukbb-ld. Pan-UKBB 420k =
# s3://pan-ukb-us-east-1/ld_release/ is the documented alternate (D-02e-02).
EUR_PUB_BUCKET = "broad-alkesgroup-ukbb-ld"  # s3://, boto3 UNSIGNED


# ---------------------------------------------------------------------------
# Step 1: emit the per-region extract jobs (M2 EUR region -> 337k tile mapping)
# ---------------------------------------------------------------------------
rule build_public_eur_manifest:
    """Map each M2 EUR region to the overlapping public UKBB 337k tile(s)."""
    input:
        manifest=EUR_PUB_MANIFEST,
        script="src/python/build_public_eur_manifest.py",
    output:
        jobs=EUR_PUB_JOBS_TSV,
    conda:
        LD_BUILD_ENV_PUB
    shell:
        r"""
        set -euo pipefail
        python {input.script} \
            --manifest {input.manifest} \
            --out {output.jobs}
        """


# ---------------------------------------------------------------------------
# Step 2: fetch + extract the public 337k EUR LD per region ($0 compute).
# AWS S3 boto3 UNSIGNED (broad-alkesgroup-ukbb-ld) -> EUR_ukbb_pub/{safe}.rds.
# ---------------------------------------------------------------------------
rule build_public_eur_ld:
    """Download + extract the public UKBB 337k EUR LD into EUR_ukbb_pub/{region_safe}.rds.

    $0 compute: anonymous S3 download (boto3 UNSIGNED) + per-region extract via
    download_ukbb_ld_tiles.py (reuses the Tile/overlap/extract scaffold). The
    hg19 public-panel .rds drops into the loader contract used by run_finemap's
    resolver (EUR_ukbb_pub is the ld_panel.EUR chain head, m3-02e Task 3).
    """
    input:
        jobs=EUR_PUB_JOBS_TSV,
        script="src/snakemake/scripts/download_ukbb_ld_tiles.py",
        manifest=EUR_PUB_MANIFEST,
    output:
        marker=os.path.join(EUR_UKBB_PUB_OUT_DIR, ".m3_public_eur_ld.done"),
    params:
        out_dir=EUR_UKBB_PUB_OUT_DIR,
    conda:
        LD_BUILD_ENV_PUB  # boto3 UNSIGNED S3 fetch (NOT the GCS/AoU env)
    threads: 4
    resources:
        mem_mb=16000,
    shell:
        r"""
        set -euo pipefail
        mkdir -p {params.out_dir}
        # The public 337k panel ($0): fetch via AWS S3 boto3 UNSIGNED + extract
        # per-region LD .rds. Region coordinates are the manifest's hg19 (GRCh37)
        # window; the EUR_ukbb_pub .rds enters the same loader contract as AFR.
        python {input.script} \
            --regions-csv {input.manifest} \
            --out-dir {params.out_dir} \
            --ancestry EUR
        touch {output.marker}
        """
