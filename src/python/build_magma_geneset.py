#!/usr/bin/env python3
"""Convert GMT files to MAGMA .set format.

MAGMA .set format:
    SET_NAME NGENES ENTREZ_ID1 ENTREZ_ID2 ...

Gene symbol to Entrez ID mapping uses the NCBI37.3.gene.loc file distributed
with MAGMA, which has columns: ENTREZ CHR START END STRAND SYMBOL.

Usage:
    python build_magma_geneset.py \\
        --gmt-files custom_cardiometabolic.gmt negative_controls.gmt \\
        --gene-loc data/reference/magma/NCBI37.3.gene.loc \\
        --out output.set

T-05-05 mitigation: no shell=True calls; all file I/O via standard Python.
"""
import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_gene_loc(gene_loc_path: str) -> dict:
    """Load MAGMA gene.loc file and return symbol -> entrez_id mapping.

    The gene.loc file is whitespace-delimited with columns:
    ENTREZ_ID  CHR  START  END  STRAND  SYMBOL

    Parameters
    ----------
    gene_loc_path : str
        Path to NCBI37.3.gene.loc or equivalent.

    Returns
    -------
    dict
        Mapping from gene symbol (str) to Entrez ID (str).
    """
    symbol_to_entrez = {}
    with open(gene_loc_path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) < 6:
                continue
            entrez_id = fields[0]
            symbol = fields[5]
            # If duplicate symbols, keep the first occurrence
            if symbol not in symbol_to_entrez:
                symbol_to_entrez[symbol] = entrez_id
    logger.info("Loaded %d gene symbols from %s", len(symbol_to_entrez), gene_loc_path)
    return symbol_to_entrez


def load_symbol_to_entrez(mapping_path: str) -> dict:
    """Load a custom symbol-to-Entrez mapping file (TSV: SYMBOL\\tENTREZ_ID).

    Parameters
    ----------
    mapping_path : str
        Path to TSV file with columns SYMBOL and ENTREZ_ID.

    Returns
    -------
    dict
        Mapping from gene symbol to Entrez ID.
    """
    mapping = {}
    with open(mapping_path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("SYMBOL"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                mapping[parts[0]] = parts[1]
    return mapping


def parse_gmt(gmt_path: str) -> list:
    """Parse a GMT file into a list of (set_name, description, gene_list) tuples.

    GMT format: SET_NAME<tab>DESCRIPTION<tab>GENE1<tab>GENE2<tab>...

    Parameters
    ----------
    gmt_path : str
        Path to GMT file.

    Returns
    -------
    list of tuple
        Each tuple is (set_name, description, list_of_gene_symbols).
    """
    gene_sets = []
    with open(gmt_path) as fh:
        for line_num, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            fields = line.split("\t")
            if len(fields) < 3:
                logger.warning(
                    "GMT line %d in %s has fewer than 3 fields, skipping",
                    line_num,
                    gmt_path,
                )
                continue
            set_name = fields[0]
            description = fields[1]
            genes = [g.strip() for g in fields[2:] if g.strip()]
            gene_sets.append((set_name, description, genes))
    return gene_sets


def convert_to_magma_set(
    gene_sets: list, symbol_to_entrez: dict, output_path: str
) -> dict:
    """Convert gene sets to MAGMA .set format.

    Parameters
    ----------
    gene_sets : list
        List of (set_name, description, gene_symbols) from parse_gmt.
    symbol_to_entrez : dict
        Gene symbol -> Entrez ID mapping.
    output_path : str
        Path to write the .set file.

    Returns
    -------
    dict
        Summary: {set_name: {n_input: int, n_mapped: int, unmapped: list}}.
    """
    summary = {}
    with open(output_path, "w") as fh:
        for set_name, _desc, genes in gene_sets:
            entrez_ids = []
            unmapped = []
            for gene in genes:
                eid = symbol_to_entrez.get(gene)
                if eid:
                    entrez_ids.append(eid)
                else:
                    unmapped.append(gene)

            if not entrez_ids:
                logger.warning(
                    "Set '%s': all %d genes unmapped, skipping",
                    set_name,
                    len(genes),
                )
                summary[set_name] = {
                    "n_input": len(genes),
                    "n_mapped": 0,
                    "unmapped": unmapped,
                }
                continue

            if unmapped:
                logger.info(
                    "Set '%s': %d/%d genes unmapped: %s",
                    set_name,
                    len(unmapped),
                    len(genes),
                    ", ".join(unmapped),
                )

            # MAGMA .set format: SET_NAME NGENES ENTREZ1 ENTREZ2 ...
            fh.write(f"{set_name}\t{len(entrez_ids)}\t")
            fh.write("\t".join(entrez_ids))
            fh.write("\n")

            summary[set_name] = {
                "n_input": len(genes),
                "n_mapped": len(entrez_ids),
                "unmapped": unmapped,
            }

    logger.info("Wrote %d gene sets to %s", len(gene_sets), output_path)
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Convert GMT files to MAGMA .set format"
    )
    parser.add_argument(
        "--gmt-files",
        nargs="+",
        required=True,
        help="One or more GMT files to convert",
    )
    parser.add_argument(
        "--gene-loc",
        required=True,
        help="MAGMA gene.loc file (NCBI37.3.gene.loc) for symbol->Entrez mapping",
    )
    parser.add_argument(
        "--symbol-to-entrez",
        default=None,
        help="Optional custom symbol-to-Entrez TSV mapping file (overrides gene.loc)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output .set file path",
    )
    args = parser.parse_args()

    # Load gene symbol -> Entrez ID mapping
    symbol_to_entrez = load_gene_loc(args.gene_loc)

    # Optionally overlay custom mapping
    if args.symbol_to_entrez:
        custom = load_symbol_to_entrez(args.symbol_to_entrez)
        logger.info("Custom mapping overrides %d symbols", len(custom))
        symbol_to_entrez.update(custom)

    # Parse all GMT files
    all_gene_sets = []
    for gmt_path in args.gmt_files:
        sets = parse_gmt(gmt_path)
        logger.info("Loaded %d gene sets from %s", len(sets), gmt_path)
        all_gene_sets.extend(sets)

    if not all_gene_sets:
        logger.error("No gene sets found in input GMT files")
        sys.exit(1)

    # Convert and write
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    summary = convert_to_magma_set(all_gene_sets, symbol_to_entrez, args.out)

    # Report summary
    total_mapped = sum(s["n_mapped"] for s in summary.values())
    total_input = sum(s["n_input"] for s in summary.values())
    logger.info(
        "Total: %d/%d genes mapped across %d sets",
        total_mapped,
        total_input,
        len(summary),
    )


if __name__ == "__main__":
    main()
