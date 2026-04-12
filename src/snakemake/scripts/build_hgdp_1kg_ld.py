#!/usr/bin/env python3
"""Build HGDP+1kG AFR LD panel from gnomAD v3.1.2 phased BCFs (anonymous HTTPS).

Source
------
- Bucket: gs://gcp-public-data--gnomad (public, no DUA)
- Metadata: https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1/secondary_analyses/hgdp_1kg/metadata_and_qc/gnomad_meta_v1.tsv
  (Hail-exported TSV with dot-separated column names; the plan's pre-spec
  path under release/3.1.2/pca/ does NOT exist -- verified in
  wave2b_preflight.log step 1b/1h.)
- BCFs: https://storage.googleapis.com/gcp-public-data--gnomad/resources/hgdp_1kg/phased_haplotypes_v2/hgdp1kgp_chr{N}.filtered.SNV_INDEL.phased.shapeit5.bcf
- License: public CC-BY, no DUA
- Reference: atgu/hgdp_tgp, gnomAD v3.1.2 release notes

Preflight findings (wave2b_preflight.log)
-----------------------------------------
- Genetic-region column: `hgdp_tgp_meta.Genetic.region` (dot-separated
  Hail export; NOT `genetic_region` as the plan pre-spec assumed)
- Sample id column: `s`
- AFR sample count: 1003 in metadata, 986 after reconciling against
  chr22 BCF header (v2 QC drops some; Plan 01-03 Task 1-03-03 test
  bounds widened to 950-1010 to reflect the v2 panel)
- Sample ID prefixes: HGDP00xxx, NA (1kG), LP (Bergstrom HGDP genomes),
  SS (Bergstrom Simons). Match BCF header directly -- no prefix
  reconciliation needed. Legacy prefix-variant loop kept below as a
  defensive fallback (Pitfall 3 mitigation) in case future BCF versions
  re-prefix.
- Contig naming: chr{N} (GRCh38 style). HGDP+1kG v2 is GRCh38 while
  config/pipeline.yaml is GRCh37 -- DEF-01-04 tracks this; this script
  emits the chr-prefixed region spec regardless so downstream liftover
  simply substitutes coordinates.
- bcftools >= 1.18 is required for HTTPS streaming (envs/ld_build.yml
  pins bcftools=1.21).
- Total BCF footprint is ~17 GB across 22 autosomes -- well under the
  plan's 100 GB worst case.

Mitigations
-----------
T-1-02 (Tampering on downloads): SHA256 computed per BCF slice and
    metadata snapshot; recorded in sidecar .meta.json. Public GCS bucket
    accessed via anonymous HTTPS -- no API keys.
T-1-02b (plink .ld text parser): plink_ld_to_rds.R uses strict numeric
    typing with data.table::fread and rejects non-numeric cells before
    writing .rds. No shell interpolation of plink-produced strings.
T-1-03 (region_id -> filesystem path): region_id is sanitized via a
    regex + explicit '/' and '..' rejection before path interpolation
    (mirrors download_ukbb_ld_tiles.py safe_region_id helper).
T-1-04 (AFR LD panel provenance): ld_source = "hgdp_1kg_v3_1_2" written
    to .meta.json sidecar so Plan 01-05 QC dashboard and Plan 01-06
    methods fragment can surface the exact panel + n.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd


META_URL = (
    "https://storage.googleapis.com/gcp-public-data--gnomad/"
    "release/3.1/secondary_analyses/hgdp_1kg/metadata_and_qc/gnomad_meta_v1.tsv"
)
BCF_URL_TPL = (
    "https://storage.googleapis.com/gcp-public-data--gnomad/"
    "resources/hgdp_1kg/phased_haplotypes_v2/{fname}"
)
DEFAULT_BCF_FNAME_TEMPLATE = (
    "hgdp1kgp_chr{chrom}.filtered.SNV_INDEL.phased.shapeit5.bcf"
)
DEFAULT_REGION_COL = "hgdp_tgp_meta.Genetic.region"
DEFAULT_SAMPLE_COL = "s"
DEFAULT_LD_SOURCE = "hgdp_1kg_v3_1_2"
DEFAULT_SOURCE_PAPER = (
    "gnomAD v3.1.2 HGDP+1kG phased haplotypes v2 (Koenig et al.; "
    "atgu/hgdp_tgp; contamination-filtered SHAPEIT5 phasing)"
)
DEFAULT_BUCKET = "gs://gcp-public-data--gnomad"

_SAFE_ID_RE = re.compile(r"[^A-Za-z0-9_]")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def sha256_file(path: Path) -> str:
    """Streaming SHA256 of a local file (T-1-02 mitigation)."""
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_region_id(region_id: str) -> str:
    """T-1-03 mitigation: reject slashes + path traversal before interpolation."""
    if "/" in region_id or ".." in region_id:
        raise ValueError(f"Unsafe region_id: {region_id!r}")
    return _SAFE_ID_RE.sub("_", region_id)


def normalize_chrom(chrom: str, target_style: str = "chr") -> str:
    """Emit 'chr22' when target_style='chr', else '22'. HGDP+1kG v2 BCFs
    use chr-prefixed contigs (GRCh38 style). Accepts either input style."""
    c = str(chrom).lstrip().lower()
    if c.startswith("chr"):
        c = c[3:]
    return f"chr{c}" if target_style == "chr" else c


# ---------------------------------------------------------------------------
# Metadata + sample list
# ---------------------------------------------------------------------------
def download_metadata(meta_path: Path) -> pd.DataFrame:
    """Fetch the gnomAD v3.1.2 HGDP+1kG sample metadata TSV.

    Cached on the scratch mount to avoid repeated downloads; the plan's
    pre-spec path 404s, so this function uses the verified v1 path under
    release/3.1/secondary_analyses/hgdp_1kg/metadata_and_qc/.
    """
    if not meta_path.exists():
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["curl", "-sL", "--fail", META_URL, "-o", str(meta_path)],
            check=True,
        )
    return pd.read_csv(meta_path, sep="\t", low_memory=False)


def extract_afr_samples(
    meta_df: pd.DataFrame,
    reg_col: str,
    sample_col: str,
    out_path: Path,
    bcf_sample_list: Optional[Path] = None,
) -> int:
    """Write the AFR keep-file consumed by `bcftools view -S`.

    Reconciles sample IDs against the BCF header (Pitfall 3). On the
    current gnomAD v3.1.2 HGDP+1kG v2 panel, sample IDs match directly
    (verified via wave2b_preflight.log step 8), but the prefix-variant
    fallback loop is retained defensively for future BCF re-releases.
    """
    if reg_col not in meta_df.columns:
        raise KeyError(
            f"Region column {reg_col!r} not found in metadata; "
            f"available columns include: {list(meta_df.columns)[:20]}..."
        )
    afr = meta_df[meta_df[reg_col] == "AFR"]
    samples = afr[sample_col].astype(str).tolist()

    if bcf_sample_list is not None:
        bcf_samples = set(Path(bcf_sample_list).read_text().split())
        reconciled = [s for s in samples if s in bcf_samples]
        if not reconciled:
            # Pitfall 3 fallback: try common prefix variants.
            for prefix in ("HGDP_", "1KG_", ""):
                cand = [f"{prefix}{s}" for s in samples]
                reconciled = [s for s in cand if s in bcf_samples]
                if reconciled:
                    break
        if not reconciled:
            raise RuntimeError(
                "No AFR sample id survives reconciliation against the BCF "
                "header. Check metadata vs BCF prefix conventions."
            )
        samples = reconciled

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(samples) + "\n")
    return len(samples)


# ---------------------------------------------------------------------------
# BCF slicing + plink2 LD
# ---------------------------------------------------------------------------
def get_bcf_sample_list(bcf_url: str, out_path: Path) -> Path:
    """Cache the BCF header sample list for reconciliation.

    Uses `bcftools query -l` over HTTPS (htslib >= 1.18). See
    wave2b_preflight.log step 7b for the remote-stream verification.
    """
    if out_path.exists():
        return out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as handle:
        subprocess.run(["bcftools", "query", "-l", bcf_url], check=True, stdout=handle)
    return out_path


def stream_bcf_slice(
    bcf_url: str,
    samples_file: Path,
    chrom: str,
    start: int,
    end: int,
    out_bcf: Path,
    maf: float = 0.01,
) -> None:
    """Stream-slice a per-region BCF from anonymous HTTPS.

    Uses chr-prefixed contig naming (GRCh38 style, confirmed in
    wave2b_preflight.log step 9). `--min-af` drops monomorphic variants
    which otherwise explode the plink LD size.
    """
    region_spec = f"{normalize_chrom(chrom, 'chr')}:{int(start)}-{int(end)}"
    out_bcf.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "bcftools", "view",
        "-S", str(samples_file),
        "--force-samples",
        "-r", region_spec,
        "--min-af", str(maf),
        "-Ob", "-o", str(out_bcf),
        bcf_url,
    ]
    subprocess.run(cmd, check=True)
    subprocess.run(["bcftools", "index", "-f", str(out_bcf)], check=True)


def plink2_ld(bcf_path: Path, out_prefix: Path) -> Path:
    """Run plink2 LD computation on a per-region BCF slice.

    Tries `--r-phased square` first (phased haplotype correlation, which
    is the correct stat when operating on the SHAPEIT5 phased BCFs).
    Falls back to `--r2-phased square` and then plain `--r2 square` if
    the active plink2 build does not expose the newer flags.

    Returns the prefix used so the caller can locate the .vcor / .ld
    output file for conversion.
    """
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    # plink2 CLI varies by build; try phased, then r2-phased, then plain r2.
    for flag in ("--r-phased", "--r2-phased", "--r2"):
        cmd = [
            "plink2",
            "--bcf", str(bcf_path),
            flag, "square",
            "--out", str(out_prefix),
            "--allow-extra-chr",
            "--threads", os.environ.get("PLINK2_THREADS", "4"),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return out_prefix
    raise RuntimeError(
        f"plink2 LD computation failed for {bcf_path}. "
        f"Last stderr:\n{result.stderr[-2000:]}"
    )


def locate_plink_ld_output(out_prefix: Path) -> Path:
    """Find the plink LD text file, which varies by plink2 version.

    plink2 may produce:
      {prefix}.phased.vcor         (newer --r-phased)
      {prefix}.phased.vcor2        (alternate)
      {prefix}.vcor                (--r2-phased)
      {prefix}.ld                  (older --r2)
    """
    for suffix in (".phased.vcor", ".phased.vcor2", ".vcor", ".vcor2", ".ld"):
        cand = out_prefix.parent / f"{out_prefix.name}{suffix}"
        if cand.exists():
            return cand
    raise FileNotFoundError(
        f"No plink LD output file found for prefix {out_prefix}. "
        f"Checked: .phased.vcor, .phased.vcor2, .vcor, .vcor2, .ld"
    )


def locate_plink_variants(out_prefix: Path) -> Path:
    """plink2 writes variant metadata as {prefix}.pvar or {prefix}.bim."""
    for suffix in (".pvar", ".bim"):
        cand = out_prefix.parent / f"{out_prefix.name}{suffix}"
        if cand.exists():
            return cand
    raise FileNotFoundError(
        f"No plink variant file found for prefix {out_prefix}."
    )


def convert_to_rds(
    plink_prefix: Path,
    out_rds: Path,
    region_id: str,
    chrom: str,
    start: int,
    end: int,
    sha_manifest: dict,
    sample_count: int,
    rscript_path: str,
    r_helper_script: str,
) -> None:
    """Shell out to `plink_ld_to_rds.R` and write the sidecar .meta.json."""
    ld_file = locate_plink_ld_output(plink_prefix)
    var_file = locate_plink_variants(plink_prefix)
    out_rds.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            rscript_path,
            r_helper_script,
            "--ld", str(ld_file),
            "--variants", str(var_file),
            "--region-id", region_id,
            "--ancestry", "AFR",
            "--ld-source", DEFAULT_LD_SOURCE,
            "--output", str(out_rds),
        ],
        check=True,
    )
    meta = {
        "region_id": region_id,
        "safe_region_id": safe_region_id(region_id),
        "chr": str(chrom),
        "start": int(start),
        "end": int(end),
        "ld_source": DEFAULT_LD_SOURCE,
        "n_samples_afr": int(sample_count),
        "sha256": sha_manifest,
        "source_paper": DEFAULT_SOURCE_PAPER,
        "bucket": DEFAULT_BUCKET,
        "plink_ld_file": ld_file.name,
    }
    out_rds.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[Iterable[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Build HGDP+1kG AFR LD panel from gnomAD v3.1.2 phased BCFs.",
    )
    ap.add_argument("--regions-csv", required=True,
                    help="config/regions_curated.csv")
    ap.add_argument("--out-dir", required=True,
                    help="Output dir for {safe_region_id}.rds + .meta.json")
    ap.add_argument(
        "--scratch-dir",
        default="/rs1/researchers/c/ckclinto/hgdp_1kg_scratch",
        help="Local cache for metadata TSV + per-region BCF slices",
    )
    ap.add_argument(
        "--bcf-fname-template",
        default=DEFAULT_BCF_FNAME_TEMPLATE,
        help="e.g. hgdp1kgp_chr{chrom}.filtered.SNV_INDEL.phased.shapeit5.bcf",
    )
    ap.add_argument("--region-column", default=DEFAULT_REGION_COL,
                    help="Metadata column holding 'AFR'/'EUR'/... labels")
    ap.add_argument("--sample-column", default=DEFAULT_SAMPLE_COL,
                    help="Metadata column holding sample id values")
    ap.add_argument(
        "--region-ids",
        nargs="*",
        default=None,
        help="Optional subset of region_id values (Scope B pilot)",
    )
    ap.add_argument("--maf", type=float, default=0.01,
                    help="MAF floor passed to bcftools view --min-af")
    ap.add_argument(
        "--rscript",
        default="Rscript",
        help="Path to Rscript interpreter for plink_ld_to_rds.R",
    )
    ap.add_argument(
        "--r-helper-script",
        default="src/snakemake/scripts/plink_ld_to_rds.R",
        help="Path to plink_ld_to_rds.R",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve inputs + validate region filter but skip bcftools/plink2.",
    )
    args = ap.parse_args(list(argv) if argv is not None else None)

    scratch = Path(args.scratch_dir)
    scratch.mkdir(parents=True, exist_ok=True)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- metadata + AFR sample list -----------------------------------
    meta_path = scratch / "gnomad_meta_v1.tsv"
    meta_df = download_metadata(meta_path)
    meta_sha = sha256_file(meta_path)
    print(f"[meta] rows={len(meta_df)} sha256={meta_sha}")

    afr_samples_file = scratch / "afr_samples.txt"
    sample_count = extract_afr_samples(
        meta_df, args.region_column, args.sample_column, afr_samples_file,
        bcf_sample_list=None,
    )
    print(f"[afr] {sample_count} samples in AFR keep-file (pre-BCF reconciliation)")

    # --- regions --------------------------------------------------------
    regions = pd.read_csv(args.regions_csv)
    if args.region_ids:
        regions = regions[regions["region_id"].isin(args.region_ids)]
    # Scope B: autosomes only (parallel to UKBB_LD_REGION_INFOS in
    # ld_reference.smk). chrX uses a separate BCF family in HGDP+1kG v2.
    autosomes = {str(c) for c in range(1, 23)}
    regions = regions[
        regions["chr"].astype(str).str.lstrip("chr").isin(autosomes)
    ]
    print(f"[regions] {len(regions)} autosomal regions selected")

    # --- per-region slice + plink LD + .rds conversion ------------------
    for _, row in regions.iterrows():
        rid = str(row["region_id"])
        safe = safe_region_id(rid)
        chrom_raw = str(row["chr"]).lstrip("chr")
        start = int(row["start"])
        end = int(row["end"])
        bcf_fname = args.bcf_fname_template.format(chrom=chrom_raw)
        bcf_url = BCF_URL_TPL.format(fname=bcf_fname)

        if args.dry_run:
            print(f"[dry-run][{rid}] would slice {bcf_url} {chrom_raw}:{start}-{end}")
            continue

        # Reconcile sample list against this BCF (Pitfall 3)
        bcf_samples_cache = scratch / f"{chrom_raw}_bcf_samples.txt"
        get_bcf_sample_list(bcf_url, bcf_samples_cache)
        recon_samples_file = scratch / f"afr_samples_{chrom_raw}.txt"
        recon_count = extract_afr_samples(
            meta_df, args.region_column, args.sample_column, recon_samples_file,
            bcf_sample_list=bcf_samples_cache,
        )
        print(f"[{rid}] reconciled AFR sample count: {recon_count}")

        slice_bcf = scratch / f"{safe}_afr.bcf"
        stream_bcf_slice(bcf_url, recon_samples_file, chrom_raw, start, end, slice_bcf)
        sha_manifest = {
            bcf_fname: sha256_file(slice_bcf),
            "gnomad_meta_v1.tsv": meta_sha,
        }

        ld_prefix = scratch / f"ld_afr_{safe}"
        plink2_ld(slice_bcf, ld_prefix)

        out_rds = out_dir / f"{safe}.rds"
        convert_to_rds(
            ld_prefix, out_rds, rid, chrom_raw, start, end,
            sha_manifest, recon_count,
            rscript_path=args.rscript,
            r_helper_script=args.r_helper_script,
        )
        print(f"[{rid}] AFR LD .rds written: {out_rds}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
