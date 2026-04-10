#!/usr/bin/env python
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union

import csv
import gzip
import numpy as np


LD_MAX_VARIANTS = int(os.environ.get("LD_MAX_VARIANTS", "6000"))


def load_samples(path: Path) -> List[str]:
    samples: List[str] = []
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) == 1:
                samples.append(parts[0])
            else:
                samples.append(parts[1])
    if not samples:
        raise ValueError(f"Sample file {path} is empty")
    return samples


def parse_gt(gt_str: str) -> float:
    if gt_str is None or gt_str == "" or "." in gt_str:
        return np.nan
    gt_str = gt_str.replace("|", "/")
    alleles = gt_str.split("/")
    if len(alleles) != 2:
        return np.nan
    if not all(a in ("0", "1") for a in alleles):
        return np.nan
    return float(int(alleles[0]) + int(alleles[1]))


def normalize_chrom(chrom: str) -> str:
    return chrom.replace("CHR", "").replace("chr", "")


def resolve_tabix() -> Optional[str]:
    candidate = os.environ.get("TABIX_BIN") or shutil.which("tabix")
    return candidate


TABIX_BIN = resolve_tabix()


def list_vcf_contigs(vcf_path: Path) -> List[str]:
    if TABIX_BIN:
        cmd = [TABIX_BIN, "-l", str(vcf_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to list contigs for {vcf_path} using tabix. "
                f"stderr: {result.stderr.strip()}"
            )
        contigs = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return contigs
    contigs: List[str] = []
    with gzip.open(vcf_path, "rt") as handle:
        for line in handle:
            if line.startswith("##contig"):
                # Format: ##contig=<ID=1,length=...>
                key = line.strip()
                if "ID=" in key:
                    idx = key.split("ID=", 1)[1]
                    contig = idx.split(",", 1)[0].replace(">", "").strip()
                    contigs.append(contig)
            elif line.startswith("#CHROM"):
                break
    return contigs


def resolve_contig(vcf_path: Path, chrom: str) -> str:
    contigs = list_vcf_contigs(vcf_path)
    chrom_clean = normalize_chrom(chrom)
    candidates = [chrom, chrom_clean, f"chr{chrom_clean}"]
    for cand in candidates:
        if cand in contigs:
            return cand
    raise ValueError(f"Chromosome {chrom} not present in {vcf_path}")


def stream_region(vcf_path: Path, contig: str, start: int, end: int) -> Iterable[str]:
    if TABIX_BIN:
        region = f"{contig}:{start}-{end}"
        cmd = [TABIX_BIN, "-h", str(vcf_path), region]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            yield line.rstrip("\n")
        stderr = proc.stderr.read() if proc.stderr else ""
        ret = proc.wait()
        if ret != 0:
            raise RuntimeError(
                f"tabix failed for region {region} in {vcf_path} (code {ret}). "
                f"stderr: {stderr.strip()}"
            )
        return

    with gzip.open(vcf_path, "rt") as handle:
        header_emitted = False
        for line in handle:
            if line.startswith("#"):
                if not header_emitted or line.startswith("##"):
                    yield line.rstrip("\n")
                if line.startswith("#CHROM"):
                    header_emitted = True
                continue
            fields = line.split("\t")
            if not fields:
                continue
            line_contig = fields[0].replace("chr", "").replace("CHR", "")
            if line_contig != contig.replace("chr", "").replace("CHR", ""):
                continue
            pos = int(fields[1])
            if start <= pos <= end:
                yield line.rstrip("\n")


def build_genotype_matrix(
    vcf_path: Path,
    chrom: str,
    start: int,
    end: int,
    samples: List[str],
    variant_positions: Optional[Set[int]] = None,
    variant_ids: Optional[Set[str]] = None,
    allow_id_fallback: bool = True,
) -> tuple[np.ndarray, List[Dict[str, Any]]]:
    chrom_clean = normalize_chrom(chrom)
    contig = resolve_contig(vcf_path, chrom)

    positions: List[int] = []
    refs: List[str] = []
    alts: List[str] = []
    ids: List[str] = []
    genotypes: List[List[float]] = []

    sample_indices: List[int] | None = None
    header_samples: List[str] = []

    remaining_positions = set(int(pos) for pos in variant_positions) if variant_positions else None
    remaining_ids = set(v_id for v_id in (variant_ids or set()) if v_id)

    for line in stream_region(vcf_path, contig, start, end):
        if line.startswith("##"):
            continue
        if line.startswith("#CHROM"):
            header = line.split("\t")
            header_samples = header[9:]
            sample_map = {name: idx for idx, name in enumerate(header_samples)}
            missing = [sample for sample in samples if sample not in sample_map]
            if missing:
                preview = ", ".join(missing[:5])
                raise ValueError(f"Samples not found in VCF header: {preview}")
            sample_indices = [sample_map[sample] for sample in samples]
            continue

        if sample_indices is None:
            raise RuntimeError("VCF header missing sample columns for region fetch")

        fields = line.split("\t")
        pos = int(fields[1])
        alt = fields[4]
        if "," in alt:
            continue

        variant_id = fields[2].strip()
        if variant_id == ".":
            variant_id = ""

        if variant_positions is not None or variant_ids is not None:
            match = False
            if remaining_positions is not None and pos in remaining_positions:
                match = True
                remaining_positions.discard(pos)
            if not match and remaining_ids is not None and variant_id and variant_id in remaining_ids:
                match = True
                remaining_ids.discard(variant_id)
            if not match:
                continue
        else:
            match = True

        variant_genotypes: List[float] = []
        has_non_missing = False
        format_fields = fields[8].split(":")
        if "GT" not in format_fields:
            continue
        gt_index = format_fields.index("GT")
        for idx in sample_indices:
            sample_field = fields[9 + idx]
            values = sample_field.split(":")
            if gt_index >= len(values):
                dosage = np.nan
            else:
                dosage = parse_gt(values[gt_index])
            if np.isnan(dosage):
                variant_genotypes.append(np.nan)
            else:
                has_non_missing = True
                variant_genotypes.append(dosage)
        if not has_non_missing:
            continue

        positions.append(pos)
        refs.append(fields[3])
        alts.append(alt)
        ids.append(variant_id)
        genotypes.append(variant_genotypes)
        if remaining_positions is not None and not remaining_positions:
            if remaining_ids is None or not remaining_ids:
                break
        if remaining_ids is not None and not remaining_ids:
            if remaining_positions is None or not remaining_positions:
                break

    variants: List[VariantRecord] = [
        {
            "CHR": chrom_clean,
            "POS": pos,
            "REF": ref,
            "ALT": alt,
            "SNP_ID": ids[idx] or "",
        }
        for idx, (pos, ref, alt) in enumerate(zip(positions, refs, alts))
    ]
    if not genotypes:
        R_matrix = np.zeros((0, 0))
    else:
        geno = np.array(genotypes, dtype=float)
        variant_means = np.nanmean(geno, axis=1, keepdims=True)
        inds = np.where(np.isnan(geno))
        geno[inds] = variant_means[inds[0], 0]
        geno_centered = geno - geno.mean(axis=1, keepdims=True)
        denom = np.std(geno_centered, axis=1, ddof=1, keepdims=True)
        denom[denom == 0] = 1.0
        geno_scaled = geno_centered / denom
        n_samples = geno.shape[1]
        if n_samples < 2:
            R_matrix = np.eye(geno.shape[0])
        else:
            R_matrix = np.matmul(geno_scaled, geno_scaled.T) / (n_samples - 1)

    if allow_id_fallback and variant_ids and len(variants) == 0:
        print(
            f"[build_ld_rds] No overlapping variants found for {chrom}:{start}-{end}; "
            "retrying chromosome-wide search using SNP IDs."
        )
        return build_genotype_matrix(
            vcf_path=vcf_path,
            chrom=chrom,
            start=1,
            end=1_000_000_000,
            samples=samples,
            variant_positions=None,
            variant_ids=variant_ids,
            allow_id_fallback=False,
        )

    return R_matrix, variants


VariantRecord = Dict[str, Any]
VariantLike = Union[VariantRecord, Tuple[str, int, str, str]]


def write_variants_tsv(path: Path, variants: Sequence[VariantLike]):
    with path.open("w", newline="") as handle:
        fieldnames = ["CHR", "POS", "REF", "ALT", "SNP_ID"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for row in variants:
            if isinstance(row, dict):
                writer.writerow(
                    {
                        "CHR": row.get("CHR"),
                        "POS": row.get("POS"),
                        "REF": row.get("REF"),
                        "ALT": row.get("ALT"),
                        "SNP_ID": row.get("SNP_ID") or "",
                    }
                )
            else:
                chr_v, pos_v, ref_v, alt_v = row
                writer.writerow(
                    {
                        "CHR": chr_v,
                        "POS": pos_v,
                        "REF": ref_v,
                        "ALT": alt_v,
                        "SNP_ID": "",
                    }
                )


def write_rds(R: np.ndarray, variants: Sequence[VariantLike], output: Path, rscript_bin: str):
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        matrix_path = Path(tmpdir) / "matrix.tsv"
        variants_path = Path(tmpdir) / "variants.tsv"
        if R.size == 0:
            matrix_path.write_text("")
        else:
            np.savetxt(matrix_path, R, fmt="%.6f", delimiter="\t")
        write_variants_tsv(variants_path, variants)
        r_code = f"""
variants <- read.table("{variants_path}", header=TRUE, sep="\\t", stringsAsFactors=FALSE)
if (file.exists("{matrix_path}") && file.info("{matrix_path}")$size > 0) {{
  matrix_data <- as.matrix(read.table("{matrix_path}", header=FALSE, sep="\\t"))
}} else {{
  matrix_data <- matrix(nrow=0, ncol=0)
}}
saveRDS(list(R=matrix_data, variants=variants), "{output}")
"""
        subprocess.run([rscript_bin, "-e", r_code], check=True)


def write_placeholder_rds(
    variants: Sequence[VariantLike],
    output: Path,
    rscript_bin: str,
    status: str = "ld_placeholder",
):
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        variants_path = Path(tmpdir) / "variants.tsv"
        write_variants_tsv(variants_path, variants)
        r_code = f"""
variants <- read.table("{variants_path}", header=TRUE, sep="\\t", stringsAsFactors=FALSE)
obj <- list(R=NULL, variants=variants, use_identity=TRUE, status="{status}")
saveRDS(obj, "{output}")
"""
        subprocess.run([rscript_bin, "-e", r_code], check=True)


def load_variant_list(path: Path) -> List[VariantRecord]:
    variants: List[VariantRecord] = []
    with path.open() as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            return variants
        for row in reader:
            chrom = str(row.get("CHR", "")).replace("chr", "").replace("CHR", "")
            pos = row.get("POS")
            if pos is None or pos == "":
                continue
            try:
                pos_int = int(float(pos))
            except ValueError:
                continue
            ref = row.get("REF") or "N"
            alt = row.get("ALT") or "N"
            snp_id = row.get("SNP_ID") or row.get("snp_id") or ""
            variants.append(
                {
                    "CHR": chrom,
                    "POS": pos_int,
                    "REF": ref,
                    "ALT": alt,
                    "SNP_ID": snp_id.strip() if isinstance(snp_id, str) else "",
                }
            )
    # Deduplicate while preserving order
    seen: Set[Tuple[str, int, str, str, str]] = set()
    unique: List[VariantRecord] = []
    for item in variants:
        key = (
            item["CHR"],
            item["POS"],
            item["REF"],
            item["ALT"],
            item.get("SNP_ID") or "",
        )
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def main():
    parser = argparse.ArgumentParser(description="Build LD matrix RDS from VCF region.")
    parser.add_argument("--vcf", required=True, help="Path to chromosome VCF (bgzipped).")
    parser.add_argument("--samples", required=True, help="Sample list (FID IID).")
    parser.add_argument("--chrom", required=True, help="Chromosome (e.g., 16).")
    parser.add_argument("--start", type=int, required=True, help="Start coordinate (1-based).")
    parser.add_argument("--end", type=int, required=True, help="End coordinate (1-based).")
    parser.add_argument("--region-id", required=True, help="Region identifier.")
    parser.add_argument("--ancestry", required=True, help="Ancestry label.")
    parser.add_argument("--output", required=True, help="Output RDS path.")
    parser.add_argument("--rscript", required=True, help="Path to Rscript executable.")
    parser.add_argument("--variant-list", help="Optional TSV with columns CHR,POS,REF,ALT to subset variants.")
    args = parser.parse_args()

    samples = load_samples(Path(args.samples))
    if not samples:
        raise ValueError("Sample list is empty")

    vcf_path = Path(args.vcf)
    if not vcf_path.exists():
        raise FileNotFoundError(f"VCF not found: {vcf_path}")

    variant_filter_pos: Optional[Set[int]] = None
    variant_filter_ids: Optional[Set[str]] = None
    variant_records: Optional[List[Dict[str, Any]]] = None
    if args.variant_list:
        variant_path = Path(args.variant_list)
        if not variant_path.exists():
            raise FileNotFoundError(f"Variant list not found: {variant_path}")
        variant_records = load_variant_list(variant_path)
        if not variant_records:
            write_placeholder_rds(
                [],
                Path(args.output),
                args.rscript,
                status="no_variants",
            )
            return
        variant_filter_pos = {item["POS"] for item in variant_records}
        variant_filter_ids = {
            item.get("SNP_ID").strip()
            for item in variant_records
            if isinstance(item.get("SNP_ID"), str) and item.get("SNP_ID").strip()
        } or None
        unique_count = len(variant_filter_pos)
        if unique_count > LD_MAX_VARIANTS:
            print(
                f"[build_ld_rds] Region {args.region_id} has {unique_count} variants; "
                f"exceeds LD_MAX_VARIANTS={LD_MAX_VARIANTS}. Writing identity placeholder."
            )
            write_placeholder_rds(
                variant_records,
                Path(args.output),
                args.rscript,
                status="variants_exceed_threshold",
            )
            return

    R, variants = build_genotype_matrix(
        vcf_path=vcf_path,
        chrom=args.chrom,
        start=args.start,
        end=args.end,
        samples=samples,
        variant_positions=variant_filter_pos,
        variant_ids=variant_filter_ids,
    )
    if variant_records is not None and len(variants) == 0:
        print(
            f"[build_ld_rds] No variants from list found in VCF for region {args.region_id}; using placeholder."
        )
        write_placeholder_rds(
            variant_records if variant_records is not None else [],
            Path(args.output),
            args.rscript,
            status="variants_missing_in_vcf",
        )
        return
    write_rds(R, variants, Path(args.output), args.rscript)


if __name__ == "__main__":
    main()
