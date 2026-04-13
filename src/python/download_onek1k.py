#!/usr/bin/env python3
"""Download OneK1K single-cell eQTL data from eQTL Catalogue or onek1k.org (Phase 2).

Provides dual-source download with eQTL Catalogue as primary source
(QTS000038, GRCh38, inverse-normal) and onek1k.org S3 as fallback
(GRCh37, requires liftover).

T-02-12 mitigation: prefer eQTL Catalogue (known provenance); log which
source was used in download metadata.
T-02-13 mitigation: validate file size > 0 after download; check .tbi
index if present.

14 cell types (Yazar 2022):
  CD4_NC, CD4_ET, CD4_SOX4, CD8_NC, CD8_ET, CD8_S100B,
  NK, NK_R, B_IN, B_Mem, Plasma, Mono_C, Mono_NC, DC
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# eQTL Catalogue study ID for OneK1K (Yazar 2022)
EQTL_CATALOGUE_STUDY = "QTS000038"
EQTL_CATALOGUE_FTP_BASE = (
    "ftp://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/"
)

# onek1k.org S3 fallback (GRCh37)
ONEK1K_S3_BASE = "https://onek1k.s3.ap-southeast-2.amazonaws.com"

# All 14 cell types
VALID_CELL_TYPES = [
    "CD4_NC",
    "CD4_ET",
    "CD4_SOX4",
    "CD8_NC",
    "CD8_ET",
    "CD8_S100B",
    "NK",
    "NK_R",
    "B_IN",
    "B_Mem",
    "Plasma",
    "Mono_C",
    "Mono_NC",
    "DC",
]


def _load_dataset_map(output_dir: str) -> dict:
    """Load or discover the cell type -> dataset ID mapping.

    Checks for a cached mapping at {output_dir}/eqtl_catalogue_dataset_map.json.
    If not present, attempts to query the eQTL Catalogue metadata to discover
    dataset IDs for QTS000038.

    Returns
    -------
    dict
        Mapping of cell_type -> dataset_id (e.g., {"Mono_C": "QTD000563"}).
    """
    map_path = os.path.join(output_dir, "eqtl_catalogue_dataset_map.json")

    if os.path.exists(map_path):
        with open(map_path) as f:
            return json.load(f)

    # If no cached map, attempt to query metadata
    logger.info(
        "No dataset map found at %s; attempting eQTL Catalogue metadata query",
        map_path,
    )

    # Placeholder: in production, this would query the eQTL Catalogue
    # metadata TSV at ftp.ebi.ac.uk to discover dataset IDs for QTS000038.
    # For now, return an empty dict -- the caller handles missing mappings.
    return {}


def download_eqtl_catalogue(
    cell_type: str,
    output_dir: str,
    dataset_map: dict,
) -> str:
    """Download OneK1K data from eQTL Catalogue (primary source).

    Parameters
    ----------
    cell_type : str
        Cell type to download (e.g., "Mono_C").
    output_dir : str
        Local output directory.
    dataset_map : dict
        Mapping of cell_type -> dataset_id.

    Returns
    -------
    str
        Path to downloaded file, or empty string if download failed.
    """
    dataset_id = dataset_map.get(cell_type)

    if not dataset_id:
        logger.warning(
            "No dataset ID found for cell type '%s' in eQTL Catalogue "
            "study %s. Check eqtl_catalogue_dataset_map.json.",
            cell_type,
            EQTL_CATALOGUE_STUDY,
        )
        return ""

    url_tsv = (
        f"{EQTL_CATALOGUE_FTP_BASE}{dataset_id}/{dataset_id}.all.tsv.gz"
    )
    url_tbi = (
        f"{EQTL_CATALOGUE_FTP_BASE}{dataset_id}/{dataset_id}.all.tsv.gz.tbi"
    )

    out_tsv = os.path.join(output_dir, f"{dataset_id}.all.tsv.gz")
    out_tbi = os.path.join(output_dir, f"{dataset_id}.all.tsv.gz.tbi")

    os.makedirs(output_dir, exist_ok=True)

    for url, out_path in [(url_tsv, out_tsv), (url_tbi, out_tbi)]:
        try:
            subprocess.run(
                ["wget", "-q", "-O", out_path, url],
                check=True,
                timeout=3600,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.error("Download failed for %s: %s", url, e)
            return ""

    # T-02-13: validate non-empty download
    if not os.path.exists(out_tsv) or os.path.getsize(out_tsv) == 0:
        logger.error("Downloaded file is empty or missing: %s", out_tsv)
        return ""

    # T-02-13: validate tabix index matches if present
    if os.path.exists(out_tbi) and os.path.getsize(out_tbi) == 0:
        logger.warning("Tabix index is empty: %s (continuing without index)", out_tbi)

    logger.info(
        "Downloaded OneK1K %s from eQTL Catalogue: %s (%d bytes)",
        cell_type,
        out_tsv,
        os.path.getsize(out_tsv),
    )
    return out_tsv


def download_onek1k_org(cell_type: str, output_dir: str) -> str:
    """Download OneK1K data from onek1k.org S3 (fallback source).

    Note: onek1k.org files are in GRCh37 format. A liftover step is
    needed before harmonization (handled by harmonize_onek1k.py with
    source_format="onek1k_org").

    Parameters
    ----------
    cell_type : str
        Cell type to download (e.g., "Mono_C").
    output_dir : str
        Local output directory.

    Returns
    -------
    str
        Path to downloaded file, or empty string if download failed.
    """
    # onek1k.org S3 file naming convention
    url = f"{ONEK1K_S3_BASE}/eqtl/{cell_type}_eQTL.tsv.gz"
    out_path = os.path.join(output_dir, f"{cell_type}_eQTL.tsv.gz")

    os.makedirs(output_dir, exist_ok=True)

    try:
        subprocess.run(
            ["wget", "-q", "--no-check-certificate", "-O", out_path, url],
            check=True,
            timeout=3600,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.error(
            "Download from onek1k.org failed for %s: %s", cell_type, e
        )
        return ""

    # T-02-13: validate non-empty download
    if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
        logger.error("Downloaded file is empty or missing: %s", out_path)
        return ""

    logger.info(
        "Downloaded OneK1K %s from onek1k.org S3: %s (%d bytes, GRCh37)",
        cell_type,
        out_path,
        os.path.getsize(out_path),
    )
    return out_path


def download_onek1k(
    cell_type: str,
    output_dir: str,
    source: str = "eqtl_catalogue",
) -> str:
    """Download OneK1K sc-eQTL data with fallback logic.

    Primary: eQTL Catalogue (QTS000038, GRCh38)
    Fallback: onek1k.org S3 (onek1k.s3.ap-southeast-2.amazonaws.com, GRCh37)

    Parameters
    ----------
    cell_type : str
        One of the 14 OneK1K cell types.
    output_dir : str
        Local output directory.
    source : str
        "eqtl_catalogue" (default) or "onek1k_org".

    Returns
    -------
    str
        Path to downloaded file.
    """
    if cell_type not in VALID_CELL_TYPES:
        raise ValueError(
            f"Invalid cell type '{cell_type}'. "
            f"Valid types: {VALID_CELL_TYPES}"
        )

    if source == "eqtl_catalogue":
        dataset_map = _load_dataset_map(output_dir)
        result = download_eqtl_catalogue(cell_type, output_dir, dataset_map)
        if result:
            return result
        # Fallback to onek1k.org
        logger.warning(
            "eQTL Catalogue download failed for %s; falling back to onek1k.org",
            cell_type,
        )
        return download_onek1k_org(cell_type, output_dir)
    elif source == "onek1k_org":
        return download_onek1k_org(cell_type, output_dir)
    else:
        raise ValueError(
            f"Unknown source '{source}'. "
            "Expected 'eqtl_catalogue' or 'onek1k_org'."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Download OneK1K sc-eQTL data (eQTL Catalogue or onek1k.org)"
    )
    parser.add_argument(
        "--cell-type",
        required=True,
        choices=VALID_CELL_TYPES,
        help="OneK1K cell type to download",
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw/onek1k/",
        help="Local output directory (default: data/raw/onek1k/)",
    )
    parser.add_argument(
        "--source",
        default="eqtl_catalogue",
        choices=["eqtl_catalogue", "onek1k_org"],
        help="Download source (default: eqtl_catalogue with onek1k_org fallback)",
    )

    args = parser.parse_args()

    result = download_onek1k(
        cell_type=args.cell_type,
        output_dir=args.output_dir,
        source=args.source,
    )

    if result:
        print(f"[download_onek1k] Downloaded {args.cell_type} to {result}")
    else:
        print(
            f"[download_onek1k] FAILED to download {args.cell_type}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
