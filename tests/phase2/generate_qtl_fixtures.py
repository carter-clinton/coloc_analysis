#!/usr/bin/env python3
"""Generate synthetic QTL fixture files for Phase 2 integration tests.

Produces 4 gzipped TSV files in tests/toy_3locus/data/qtl/ covering the
3 toy locus regions (FTO_16q12, MC4R_18q21, SH2B3_12q24) with:
- 50 synthetic variants per region per gene (150+ rows per file)
- Variant IDs in eQTL Catalogue format: chr{chrom}_{pos}_{ref}_{alt}
- Realistic column schemas matching each QTL source type
- One "signal" variant per region with |beta| > 0.3

Output files:
  eqtl_mock.tsv.gz   - GTEx eQTL format
  sqtl_mock.tsv.gz    - GTEx sQTL format
  pqtl_mock.tsv.gz    - UKB-PPP REGENIE format
  sceqtl_mock.tsv.gz  - OneK1K sc-eQTL format
"""

import gzip
import math
import os
import random
from pathlib import Path

# Use fixed seed for reproducibility
random.seed(42)

# Toy locus regions (GRCh38-like coordinates for fixture purposes)
REGIONS = [
    {"region_id": "FTO_16q12", "chr": 16, "start": 53766088, "end": 54366088,
     "gene_id": "ENSG00000140718", "gene_name": "FTO"},
    {"region_id": "MC4R_18q21", "chr": 18, "start": 58332768, "end": 58932768,
     "gene_id": "ENSG00000166603", "gene_name": "MC4R"},
    {"region_id": "SH2B3_12q24", "chr": 12, "start": 110962196, "end": 111562196,
     "gene_id": "ENSG00000111252", "gene_name": "SH2B3"},
]

BASES = ["A", "C", "G", "T"]
N_VARIANTS_PER_REGION = 50


def _random_alleles():
    ref = random.choice(BASES)
    alt = random.choice([b for b in BASES if b != ref])
    return ref, alt


def _random_beta(signal=False):
    if signal:
        return random.choice([-1, 1]) * random.uniform(0.3, 0.6)
    return random.gauss(0, 0.05)


def _random_se():
    return random.uniform(0.01, 0.1)


def _random_maf():
    return round(random.uniform(0.05, 0.45), 4)


def _pvalue_from_beta_se(beta, se):
    """Approximate two-sided p-value from beta/se using z^2."""
    z = abs(beta / se) if se > 0 else 0
    # Rough approximation of 2-sided p from z
    # Use survival function approximation: p ~ 2 * exp(-0.5*z^2) / (z * sqrt(2*pi))
    if z < 0.1:
        return 1.0
    p = 2.0 * math.exp(-0.5 * z * z) / (z * math.sqrt(2 * math.pi))
    return max(p, 1e-300)


def generate_eqtl_mock(out_dir: Path):
    """Generate eqtl_mock.tsv.gz in eQTL Catalogue format."""
    header = [
        "molecular_trait_id", "variant", "chromosome", "position", "ref", "alt",
        "beta", "se", "pvalue", "maf", "an", "ac", "gene_id", "median_tpm", "rsid"
    ]
    rows = []
    for region in REGIONS:
        chrom = region["chr"]
        start = region["start"]
        gene_id = region["gene_id"]
        for i in range(N_VARIANTS_PER_REGION):
            pos = start + i * 1000 + random.randint(0, 999)
            ref, alt = _random_alleles()
            is_signal = (i == 25)  # One signal variant per region
            beta = _random_beta(signal=is_signal)
            se = _random_se()
            pval = _pvalue_from_beta_se(beta, se)
            maf = _random_maf()
            an = 838  # GTEx v8 typical
            ac = int(an * maf)
            variant_id = f"chr{chrom}_{pos}_{ref}_{alt}"
            rsid = f"rs{random.randint(1000000, 99999999)}"
            rows.append([
                gene_id, variant_id, str(chrom), str(pos), ref, alt,
                f"{beta:.6f}", f"{se:.6f}", f"{pval:.6e}", f"{maf:.4f}",
                str(an), str(ac), gene_id, f"{random.uniform(0.5, 50):.2f}", rsid
            ])

    path = out_dir / "eqtl_mock.tsv.gz"
    with gzip.open(path, "wt") as f:
        f.write("\t".join(header) + "\n")
        for row in rows:
            f.write("\t".join(row) + "\n")
    print(f"  eqtl_mock.tsv.gz: {len(rows)} data rows")


def generate_sqtl_mock(out_dir: Path):
    """Generate sqtl_mock.tsv.gz in eQTL Catalogue sQTL format."""
    header = [
        "molecular_trait_id", "variant", "chromosome", "position", "ref", "alt",
        "beta", "se", "pvalue", "maf", "an", "ac", "gene_id", "median_tpm", "rsid"
    ]
    rows = []
    for region in REGIONS:
        chrom = region["chr"]
        start = region["start"]
        gene_id = region["gene_id"]
        # sQTL molecular_trait_id uses splice junction format
        splice_id = f"chr{chrom}:{start + 500}:{start + 1500}:clu_{random.randint(10000, 99999)}"
        for i in range(N_VARIANTS_PER_REGION):
            pos = start + i * 1000 + random.randint(0, 999)
            ref, alt = _random_alleles()
            is_signal = (i == 25)
            beta = _random_beta(signal=is_signal)
            se = _random_se()
            pval = _pvalue_from_beta_se(beta, se)
            maf = _random_maf()
            an = 838
            ac = int(an * maf)
            variant_id = f"chr{chrom}_{pos}_{ref}_{alt}"
            rsid = f"rs{random.randint(1000000, 99999999)}"
            rows.append([
                splice_id, variant_id, str(chrom), str(pos), ref, alt,
                f"{beta:.6f}", f"{se:.6f}", f"{pval:.6e}", f"{maf:.4f}",
                str(an), str(ac), gene_id, f"{random.uniform(0.5, 50):.2f}", rsid
            ])

    path = out_dir / "sqtl_mock.tsv.gz"
    with gzip.open(path, "wt") as f:
        f.write("\t".join(header) + "\n")
        for row in rows:
            f.write("\t".join(row) + "\n")
    print(f"  sqtl_mock.tsv.gz: {len(rows)} data rows")


def generate_pqtl_mock(out_dir: Path):
    """Generate pqtl_mock.tsv.gz in UKB-PPP REGENIE format."""
    header = [
        "CHROM", "GENPOS", "ID", "ALLELE0", "ALLELE1", "A1FREQ",
        "INFO", "N", "BETA", "SE", "LOG10P"
    ]
    rows = []
    for region in REGIONS:
        chrom = region["chr"]
        start = region["start"]
        for i in range(N_VARIANTS_PER_REGION):
            pos = start + i * 1000 + random.randint(0, 999)
            ref, alt = _random_alleles()
            is_signal = (i == 25)
            beta = _random_beta(signal=is_signal)
            se = _random_se()
            pval = _pvalue_from_beta_se(beta, se)
            log10p = -math.log10(max(pval, 1e-300))
            maf = _random_maf()
            snp_id = f"{chrom}:{pos}:{ref}:{alt}"
            info = round(random.uniform(0.8, 1.0), 3)
            n = 54219
            rows.append([
                str(chrom), str(pos), snp_id, ref, alt,
                f"{maf:.4f}", f"{info:.3f}", str(n),
                f"{beta:.6f}", f"{se:.6f}", f"{log10p:.4f}"
            ])

    path = out_dir / "pqtl_mock.tsv.gz"
    with gzip.open(path, "wt") as f:
        f.write("\t".join(header) + "\n")
        for row in rows:
            f.write("\t".join(row) + "\n")
    print(f"  pqtl_mock.tsv.gz: {len(rows)} data rows")


def generate_sceqtl_mock(out_dir: Path):
    """Generate sceqtl_mock.tsv.gz in OneK1K sc-eQTL format (eQTL Catalogue + cell_type)."""
    header = [
        "molecular_trait_id", "variant", "chromosome", "position", "ref", "alt",
        "beta", "se", "pvalue", "maf", "an", "ac", "gene_id", "median_tpm",
        "rsid", "cell_type"
    ]
    rows = []
    for region in REGIONS:
        chrom = region["chr"]
        start = region["start"]
        gene_id = region["gene_id"]
        for i in range(N_VARIANTS_PER_REGION):
            pos = start + i * 1000 + random.randint(0, 999)
            ref, alt = _random_alleles()
            is_signal = (i == 25)
            beta = _random_beta(signal=is_signal)
            se = _random_se()
            pval = _pvalue_from_beta_se(beta, se)
            maf = _random_maf()
            an = 1964  # ~982 samples * 2
            ac = int(an * maf)
            variant_id = f"chr{chrom}_{pos}_{ref}_{alt}"
            rsid = f"rs{random.randint(1000000, 99999999)}"
            rows.append([
                gene_id, variant_id, str(chrom), str(pos), ref, alt,
                f"{beta:.6f}", f"{se:.6f}", f"{pval:.6e}", f"{maf:.4f}",
                str(an), str(ac), gene_id, f"{random.uniform(0.5, 50):.2f}",
                rsid, "Mono_C"
            ])

    path = out_dir / "sceqtl_mock.tsv.gz"
    with gzip.open(path, "wt") as f:
        f.write("\t".join(header) + "\n")
        for row in rows:
            f.write("\t".join(row) + "\n")
    print(f"  sceqtl_mock.tsv.gz: {len(rows)} data rows")


def main():
    out_dir = Path(__file__).resolve().parent.parent / "toy_3locus" / "data" / "qtl"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating QTL fixtures in {out_dir}")
    generate_eqtl_mock(out_dir)
    generate_sqtl_mock(out_dir)
    generate_pqtl_mock(out_dir)
    generate_sceqtl_mock(out_dir)
    print("Done.")


if __name__ == "__main__":
    main()
