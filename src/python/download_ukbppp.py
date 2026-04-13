#!/usr/bin/env python3
"""Download UKB-PPP per-protein summary statistics from Synapse.

Provides CLI for downloading UKB-PPP pQTL REGENIE summary statistics from
the Synapse project syn51364943 (Sun et al. 2023). Falls back to S3 unsigned
access if Synapse download fails.

Security: Auth token is read from SYNAPSE_AUTH_TOKEN env var or --auth-token
CLI argument. NEVER committed to source control (T-02-08).
"""

import argparse
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def download_from_synapse(
    protein: str,
    chromosome: str,
    output_dir: str,
    synapse_project: str = "syn51364943",
    auth_token: str = None,
) -> str:
    """Download UKB-PPP per-protein chromosome file from Synapse.

    Parameters
    ----------
    protein : str
        Protein name (e.g., "IL6").
    chromosome : str
        Chromosome to download (e.g., "6").
    output_dir : str
        Local output directory.
    synapse_project : str
        Synapse project ID (default: syn51364943).
    auth_token : str, optional
        Synapse auth token. If None, reads from SYNAPSE_AUTH_TOKEN env var.

    Returns
    -------
    str
        Path to the downloaded file.

    Raises
    ------
    RuntimeError
        If download fails from both Synapse and S3 fallback.
    """
    import synapseclient

    # Resolve auth token (T-02-08: never hardcode)
    token = auth_token or os.environ.get("SYNAPSE_AUTH_TOKEN")
    if not token:
        raise RuntimeError(
            "No Synapse auth token provided. Set SYNAPSE_AUTH_TOKEN environment "
            "variable or pass --auth-token. See "
            "https://help.synapse.org/docs/Managing-Your-Account.2055405596.html "
            "for how to create a personal access token."
        )

    # Prepare output path
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    expected_filename = f"discovery_chr{chromosome}_{protein}.gz"
    output_path = output_dir / expected_filename

    # T-02-10: Check disk space before download (basic check)
    try:
        stat = os.statvfs(str(output_dir))
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
        if free_gb < 1.0:
            logger.warning(
                "Low disk space: %.1f GB free in %s", free_gb, output_dir
            )
    except OSError:
        pass

    try:
        syn = synapseclient.Synapse()
        syn.login(authToken=token)

        # Navigate to per-protein data within the Synapse folder
        # The UKB-PPP data is organized by protein in syn51365301
        logger.info(
            "Downloading %s chr%s from Synapse project %s",
            protein,
            chromosome,
            synapse_project,
        )

        # Query for the specific file
        results = syn.getChildren(
            "syn51365301", includeTypes=["file"]
        )

        target_file = None
        for item in results:
            if expected_filename in item.get("name", ""):
                target_file = item
                break

        if target_file:
            downloaded = syn.get(target_file["id"], downloadLocation=str(output_dir))
            logger.info("Downloaded: %s", downloaded.path)
            return str(downloaded.path)
        else:
            logger.warning(
                "File %s not found in Synapse folder; trying S3 fallback",
                expected_filename,
            )
            raise FileNotFoundError(f"Not found in Synapse: {expected_filename}")

    except (
        synapseclient.core.exceptions.SynapseError,
        FileNotFoundError,
        ConnectionError,
        TimeoutError,
        OSError,
    ) as e:
        logger.warning("Synapse download failed: %s. Trying S3 fallback.", e)
        return _download_from_s3(protein, chromosome, output_dir)


def _download_from_s3(
    protein: str,
    chromosome: str,
    output_dir: Path,
) -> str:
    """Fallback: download from S3 unsigned access.

    Uses the public S3 bucket s3://ukbiobank.opendata.sagebase.org/
    with unsigned (anonymous) access.
    """
    try:
        import boto3
        from botocore import UNSIGNED
        from botocore.config import Config

        s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))

        bucket = "ukbiobank.opendata.sagebase.org"
        key = f"UKB-PPP/{protein}/discovery_chr{chromosome}_{protein}.gz"
        output_path = output_dir / f"discovery_chr{chromosome}_{protein}.gz"

        logger.info("Downloading from S3: s3://%s/%s", bucket, key)
        s3.download_file(bucket, key, str(output_path))

        # Verify download
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError(f"Downloaded file is empty: {output_path}")

        logger.info("S3 download complete: %s (%d bytes)", output_path, output_path.stat().st_size)
        return str(output_path)

    except ImportError:
        raise RuntimeError(
            "boto3 not installed. Install with: pip install boto3"
        )
    except Exception as e:
        raise RuntimeError(
            f"Both Synapse and S3 downloads failed for {protein} chr{chromosome}: {e}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Download UKB-PPP per-protein summary statistics from Synapse"
    )
    parser.add_argument(
        "--protein", required=True, help="Protein name (e.g., IL6)"
    )
    parser.add_argument(
        "--chromosome", required=True, help="Chromosome to download (e.g., 6)"
    )
    parser.add_argument(
        "--synapse-project",
        default="syn51364943",
        help="Synapse project ID (default: syn51364943)",
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw/ukbppp/",
        help="Local output directory",
    )
    parser.add_argument(
        "--auth-token",
        default=None,
        help="Synapse auth token (or set SYNAPSE_AUTH_TOKEN env var)",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    output_path = download_from_synapse(
        protein=args.protein,
        chromosome=args.chromosome,
        output_dir=args.output_dir,
        synapse_project=args.synapse_project,
        auth_token=args.auth_token,
    )

    print(f"[download_ukbppp] Downloaded to: {output_path}")


if __name__ == "__main__":
    main()
