"""Variant ID mapping utility for GRCh37 -> GRCh38 coordinate conversion.

Converts rsID + GRCh37 position to eQTL Catalogue variant_id format
(chr{chrom}_{pos_grch38}_{ref}_{alt}) used by GTEx v8, OneK1K, and other
GRCh38-based QTL sources.

Requires: pyliftover (conda install -c bioconda pyliftover)
"""

from typing import Optional


def rsid_to_grch38_variant_id(
    rsid: str,
    grch37_chr: str,
    grch37_pos: int,
    ref: str,
    alt: str,
    lo,  # LiftOver instance
) -> Optional[str]:
    """Convert a GRCh37 variant to eQTL Catalogue GRCh38 variant_id format.

    Parameters
    ----------
    rsid : str
        rsID of the variant (for logging only; not used in conversion).
    grch37_chr : str
        Chromosome in GRCh37 (e.g., "16" or "chr16").
    grch37_pos : int
        1-based position in GRCh37.
    ref : str
        Reference allele.
    alt : str
        Alternative allele.
    lo : pyliftover.LiftOver
        Initialized LiftOver instance with hg19ToHg38 chain.

    Returns
    -------
    str or None
        Variant ID in format "chr{chrom}_{pos}_{ref}_{alt}" (GRCh38), or
        None if liftover fails.
    """
    # Normalize chromosome to 'chrN' format
    chrom = str(grch37_chr)
    if not chrom.startswith("chr"):
        chrom = f"chr{chrom}"

    # pyliftover uses 0-based coordinates
    result = lo.convert_coordinate(chrom, grch37_pos - 1)

    if not result:
        return None

    # Take the first (highest confidence) hit
    lifted_chrom, lifted_pos_0based, lifted_strand, _ = result[0]

    # Convert back to 1-based
    lifted_pos = lifted_pos_0based + 1

    # Strip 'chr' prefix for the numeric part
    chrom_num = lifted_chrom.replace("chr", "")

    # eQTL Catalogue format: chr{chrom}_{pos}_{ref}_{alt}
    variant_id = f"chr{chrom_num}_{lifted_pos}_{ref}_{alt}"

    return variant_id


def build_variant_map(
    snp_names: list,
    grch37_positions: dict,
    lo,  # LiftOver instance
) -> dict:
    """Batch conversion of SNP names from Phase 1 .fit.rds to GRCh38 variant IDs.

    Parameters
    ----------
    snp_names : list of str
        List of SNP identifiers (rsIDs or chr:pos format).
    grch37_positions : dict
        Mapping of snp_name -> dict with keys:
        - 'chr': chromosome (str)
        - 'pos': 1-based GRCh37 position (int)
        - 'ref': reference allele (str)
        - 'alt': alternative allele (str)
    lo : pyliftover.LiftOver
        Initialized LiftOver instance with hg19ToHg38 chain.

    Returns
    -------
    dict
        Mapping of snp_name -> GRCh38 variant_id (str or None if lift failed).
    """
    variant_map = {}
    n_success = 0
    n_fail = 0

    for snp in snp_names:
        info = grch37_positions.get(snp)
        if info is None:
            variant_map[snp] = None
            n_fail += 1
            continue

        variant_id = rsid_to_grch38_variant_id(
            rsid=snp,
            grch37_chr=info["chr"],
            grch37_pos=info["pos"],
            ref=info["ref"],
            alt=info["alt"],
            lo=lo,
        )
        variant_map[snp] = variant_id
        if variant_id is not None:
            n_success += 1
        else:
            n_fail += 1

    print(
        f"[variant_id_map] Mapped {n_success}/{len(snp_names)} variants "
        f"({n_fail} failed)"
    )

    return variant_map
