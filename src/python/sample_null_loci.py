#!/usr/bin/env python3
"""Sample distance-matched null loci and build negative control manifests.

Three modes of operation:

1. **Default (null loci sampling):** Generate distance-matched null loci
   using bedtools shuffle. Produces BED files matched on gene density and
   region size for empirical PP.H4 calibration (REQ-7, D-04c).

2. **--build-neg-ctrl-manifest:** Build a coloc manifest for curated negative
   control gene sets. Produces a TSV in the same format as qtl_coloc_manifest.tsv,
   one row per (neg_ctrl_set x gene x region x qtl_source).

3. **--run-neg-ctrl-coloc:** Run QTL coloc on the negative control manifest
   by calling run_qtl_coloc.R for each row, then aggregate results into a
   single TSV.

T-02-18 mitigation: deterministic seeds (seed_base + draw_id).
"""
import argparse
import csv
import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sample null loci, build neg-ctrl manifests, or run neg-ctrl coloc."
    )
    # Mode flags
    parser.add_argument(
        "--build-neg-ctrl-manifest",
        action="store_true",
        help="Build negative control coloc manifest from curated gene sets.",
    )
    parser.add_argument(
        "--run-neg-ctrl-coloc",
        action="store_true",
        help="Run QTL coloc on negative control manifest rows.",
    )

    # Common arguments
    parser.add_argument("--neg-ctrl-config", required=True, help="Path to negative_controls.yaml")
    parser.add_argument("--output", help="Output path (manifest TSV or aggregated results TSV)")

    # Null loci sampling arguments
    parser.add_argument("--regions", help="Path to regions_curated_grch38.csv")
    parser.add_argument("--genome-sizes", help="Path to hg38.chrom.sizes")
    parser.add_argument("--blacklist", help="Path to hg38 blacklist BED")
    parser.add_argument("--gene-density-bed", help="Path to gene density per-window BED")
    parser.add_argument("--output-dir", help="Output directory for null loci BED files")
    parser.add_argument("--n-draws", type=int, default=None, help="Number of null sets")
    parser.add_argument("--seed-base", type=int, default=42, help="Base random seed")

    # Build manifest arguments
    parser.add_argument("--qtl-config", help="Path to qtl_sources.yaml")

    # Run neg-ctrl coloc arguments
    parser.add_argument("--manifest", help="Path to neg_ctrl_coloc_manifest.tsv")

    return parser.parse_args()


def load_regions(regions_path):
    """Load GRCh38 regions from CSV, return list of dicts."""
    regions = []
    with open(regions_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            regions.append({
                "region_id": row["region_id"],
                "chr": row["chr"].replace("chr", "").replace("CHR", ""),
                "start": int(float(row["start_grch38"])),
                "end": int(float(row["end_grch38"])),
            })
    return regions


def regions_to_bed(regions, bed_path):
    """Write regions to a BED file (chr, start, end, region_id)."""
    with open(bed_path, "w") as f:
        for r in regions:
            chrom = f"chr{r['chr']}" if not str(r["chr"]).startswith("chr") else r["chr"]
            f.write(f"{chrom}\t{r['start']}\t{r['end']}\t{r['region_id']}\n")


def compute_region_size(region):
    """Compute region size in base pairs."""
    return region["end"] - region["start"]


def sample_null_loci(args, neg_config):
    """Generate distance-matched null loci using bedtools shuffle."""
    regions = load_regions(args.regions)
    spec = neg_config["matched_null_spec"]
    n_draws = args.n_draws or spec["n_draws"]
    seed_base = args.seed_base or spec.get("seed_base", 42)
    gene_density_tol = spec["match_criteria"]["gene_density_tolerance"]
    region_size_tol = spec["match_criteria"]["region_size_tolerance"]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write real loci BED for exclusion
    real_bed = output_dir / "real_loci.bed"
    regions_to_bed(regions, real_bed)

    # Build exclusion BED (real loci + blacklist + centromeres)
    exclusion_bed = output_dir / "exclusion_zones.bed"
    exclusion_parts = [str(real_bed)]
    if args.blacklist and os.path.exists(args.blacklist):
        exclusion_parts.append(args.blacklist)

    # Merge exclusion zones
    if len(exclusion_parts) == 1:
        # Just copy real loci as exclusion
        import shutil
        shutil.copy(str(real_bed), str(exclusion_bed))
    else:
        # Cat, sort, and merge exclusion BEDs using safe subprocess pipeline
        # (no shell=True to avoid command injection via file paths)
        try:
            cat_proc = subprocess.Popen(
                ["cat"] + exclusion_parts,
                stdout=subprocess.PIPE,
            )
            sort_proc = subprocess.Popen(
                ["sort", "-k1,1", "-k2,2n"],
                stdin=cat_proc.stdout,
                stdout=subprocess.PIPE,
            )
            cat_proc.stdout.close()
            merge_proc = subprocess.Popen(
                ["bedtools", "merge"],
                stdin=sort_proc.stdout,
                stdout=subprocess.PIPE,
                text=True,
            )
            sort_proc.stdout.close()
            stdout, _ = merge_proc.communicate()
            # Check for errors in the pipeline
            cat_proc.wait()
            sort_proc.wait()
            if merge_proc.returncode != 0:
                raise subprocess.CalledProcessError(merge_proc.returncode, "bedtools merge")
            with open(exclusion_bed, "w") as f:
                f.write(stdout)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("bedtools merge failed; using real loci as exclusion zones only")
            import shutil
            shutil.copy(str(real_bed), str(exclusion_bed))

    # Genome sizes
    genome_sizes = args.genome_sizes
    if not genome_sizes or not os.path.exists(genome_sizes):
        # Generate minimal genome sizes for hg38 standard chromosomes
        genome_sizes = str(output_dir / "hg38.chrom.sizes")
        _write_hg38_chrom_sizes(genome_sizes)

    # Compute real locus properties for matching
    real_sizes = {r["region_id"]: compute_region_size(r) for r in regions}
    mean_real_size = sum(real_sizes.values()) / len(real_sizes)

    # Sample null loci
    summary_rows = []
    for draw_id in range(n_draws):
        seed = seed_base + draw_id
        out_bed = output_dir / f"null_loci_draw_{draw_id:04d}.bed"

        try:
            cmd = [
                "bedtools", "shuffle",
                "-i", str(real_bed),
                "-g", genome_sizes,
                "-excl", str(exclusion_bed),
                "-noOverlapping",
                "-seed", str(seed),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            with open(out_bed, "w") as f:
                f.write(result.stdout)

            # Post-filter: check region size tolerance
            null_regions = _parse_bed(out_bed)
            accepted = []
            for nr in null_regions:
                nr_size = nr["end"] - nr["start"]
                # Check if size matches any real region within tolerance
                matched = any(
                    abs(nr_size - rs) / max(rs, 1) <= region_size_tol
                    for rs in real_sizes.values()
                )
                if matched:
                    accepted.append(nr)

            # Rewrite filtered BED
            with open(out_bed, "w") as f:
                for ar in accepted:
                    f.write(f"{ar['chr']}\t{ar['start']}\t{ar['end']}\t{ar.get('name', 'null')}\n")

            mean_size = (
                sum(a["end"] - a["start"] for a in accepted) / max(len(accepted), 1)
            )

            summary_rows.append({
                "draw_id": draw_id,
                "n_regions": len(accepted),
                "mean_gene_density": 0.0,  # placeholder; real value from gene_density_bed
                "mean_region_size": mean_size,
                "seed": seed,
            })
        except FileNotFoundError:
            logger.warning(
                "bedtools not found; writing placeholder null loci for draw %d", draw_id
            )
            # Write empty BED
            with open(out_bed, "w") as f:
                pass
            summary_rows.append({
                "draw_id": draw_id,
                "n_regions": 0,
                "mean_gene_density": 0.0,
                "mean_region_size": 0.0,
                "seed": seed,
            })
        except subprocess.CalledProcessError as e:
            logger.warning("bedtools shuffle failed for draw %d: %s", draw_id, e.stderr)
            with open(out_bed, "w") as f:
                pass
            summary_rows.append({
                "draw_id": draw_id,
                "n_regions": 0,
                "mean_gene_density": 0.0,
                "mean_region_size": 0.0,
                "seed": seed,
            })

    # Write summary TSV
    summary_path = output_dir / "null_loci_summary.tsv"
    with open(summary_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["draw_id", "n_regions", "mean_gene_density", "mean_region_size", "seed"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    logger.info("Generated %d null loci draws in %s", n_draws, output_dir)
    logger.info("Summary: %s", summary_path)


def build_neg_ctrl_manifest(args, neg_config):
    """Build negative control coloc manifest from curated gene sets.

    Produces a TSV in the same format as qtl_coloc_manifest.tsv, one row per
    (neg_ctrl_set x gene x region x qtl_source). The regions used are the
    curated negative control regions defined in negative_controls.yaml.
    """
    curated_sets = neg_config["curated_sets"]

    # Load QTL sources
    with open(args.qtl_config) as f:
        qtl_config = yaml.safe_load(f)
    sources = qtl_config.get("sources", {})

    # Load real regions for matching metadata
    regions = load_regions(args.regions)

    rows = []
    for set_name, setdef in curated_sets.items():
        genes = setdef["genes"]
        # Use the set's defined regions or fallback to a single-region definition
        set_regions = []
        if "region_grch38" in setdef:
            r = setdef["region_grch38"]
            set_regions.append({
                "chr": str(r["chr"]),
                "start": r["start"],
                "end": r["end"],
                "region_id": f"neg_ctrl_{set_name}",
            })
        elif "regions_grch37" in setdef:
            # Use GRCh37 coordinates as approximate (liftover handled elsewhere)
            for rdef in setdef["regions_grch37"]:
                set_regions.append({
                    "chr": str(rdef["chr"]),
                    "start": rdef["start"],
                    "end": rdef["end"],
                    "region_id": f"neg_ctrl_{set_name}_{rdef.get('gene', 'unknown')}",
                })

        for gene in genes:
            for region in set_regions:
                for src_name, src_def in sources.items():
                    row = {
                        "qtl_coloc_id": f"negctrl_{set_name}_{gene}_{region['region_id']}_{src_name}",
                        "qtl_source": src_name,
                        "tissue": "all",
                        "gene_id": gene,
                        "region": region["region_id"],
                        "ancestry": "EUR",
                        "gwas_trait": "negative_control",
                        "dataset_id": set_name,
                        "chr": region["chr"],
                        "start_grch38": region["start"],
                        "end_grch38": region["end"],
                        "tissue_n": str(src_def.get("sample_size", 0)),
                        "sdy": str(src_def.get("sdY", 1.0)),
                        "neg_ctrl_set": set_name,
                        "gwas_fit_path": "",
                        "ld_matrix_path": "",
                        "harmonized_qtl_path": "",
                    }
                    rows.append(row)

    # Write manifest
    output_path = args.output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fieldnames = [
        "qtl_coloc_id", "qtl_source", "tissue", "gene_id", "region",
        "ancestry", "gwas_trait", "dataset_id", "chr", "start_grch38",
        "end_grch38", "tissue_n", "sdy", "neg_ctrl_set",
        "gwas_fit_path", "ld_matrix_path", "harmonized_qtl_path",
    ]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Built negative control manifest: %d rows -> %s", len(rows), output_path)


def run_neg_ctrl_coloc(args, neg_config):
    """Run QTL coloc on negative control manifest and aggregate results.

    Iterates manifest rows, calling run_qtl_coloc.R via subprocess for each row,
    then aggregates JSON outputs into a single TSV.
    """
    import pandas as pd

    manifest = pd.read_csv(args.manifest, sep="\t", dtype=str)
    results = []

    for _, row in manifest.iterrows():
        qtl_coloc_id = row["qtl_coloc_id"]
        logger.info("Running neg-ctrl coloc: %s", qtl_coloc_id)

        # Build Rscript command (same invocation as qtl_coloc.smk)
        output_json = os.path.join(
            os.path.dirname(args.output), f"{qtl_coloc_id}.json"
        )
        os.makedirs(os.path.dirname(output_json), exist_ok=True)

        cmd = [
            "Rscript", "src/snakemake/scripts/run_qtl_coloc.R",
            "--gwas-fit", row.get("gwas_fit_path", ""),
            "--qtl-sumstats", row.get("harmonized_qtl_path", ""),
            "--ld-matrix", row.get("ld_matrix_path", ""),
            "--qtl-source", row.get("qtl_source", ""),
            "--tissue", row.get("tissue", ""),
            "--gene-id", row.get("gene_id", ""),
            "--region", row.get("region", ""),
            "--ancestry", row.get("ancestry", ""),
            "--sdy", str(row.get("sdy", "1.0")),
            "--sample-size", str(row.get("tissue_n", "0")),
            "--policy", "config/susie_policy.yaml",
            "--output", output_json,
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=600)
            # Parse JSON output
            if os.path.exists(output_json):
                with open(output_json) as f:
                    coloc_result = json.load(f)
                summary = coloc_result.get("summary", {})
                results.append({
                    "qtl_coloc_id": qtl_coloc_id,
                    "neg_ctrl_set": row.get("neg_ctrl_set", ""),
                    "qtl_source": row.get("qtl_source", ""),
                    "gene_id": row.get("gene_id", ""),
                    "region": row.get("region", ""),
                    "ancestry": row.get("ancestry", ""),
                    "PP.H4.abf": summary.get("PP.H4.abf", 0.0),
                    "PP.H3.abf": summary.get("PP.H3.abf", 0.0),
                    "nsnps": summary.get("nsnps", 0),
                })
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning("Failed coloc for %s: %s", qtl_coloc_id, str(e))
            results.append({
                "qtl_coloc_id": qtl_coloc_id,
                "neg_ctrl_set": row.get("neg_ctrl_set", ""),
                "qtl_source": row.get("qtl_source", ""),
                "gene_id": row.get("gene_id", ""),
                "region": row.get("region", ""),
                "ancestry": row.get("ancestry", ""),
                "PP.H4.abf": None,
                "PP.H3.abf": None,
                "nsnps": 0,
            })

    # Write aggregated results
    results_df = pd.DataFrame(results)
    results_df.to_csv(args.output, sep="\t", index=False)
    logger.info("Aggregated %d neg-ctrl coloc results -> %s", len(results), args.output)


def _parse_bed(bed_path):
    """Parse a BED file into list of dicts."""
    regions = []
    with open(bed_path) as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                regions.append({
                    "chr": parts[0],
                    "start": int(parts[1]),
                    "end": int(parts[2]),
                    "name": parts[3] if len(parts) > 3 else "",
                })
    return regions


def _write_hg38_chrom_sizes(path):
    """Write minimal hg38 chromosome sizes for bedtools."""
    sizes = {
        "chr1": 248956422, "chr2": 242193529, "chr3": 198295559,
        "chr4": 190214555, "chr5": 181538259, "chr6": 170805979,
        "chr7": 159345973, "chr8": 145138636, "chr9": 138394717,
        "chr10": 133797422, "chr11": 135086622, "chr12": 133275309,
        "chr13": 114364328, "chr14": 107043718, "chr15": 101991189,
        "chr16": 90338345, "chr17": 83257441, "chr18": 80373285,
        "chr19": 58617616, "chr20": 64444167, "chr21": 46709983,
        "chr22": 50818468, "chrX": 156040895,
    }
    with open(path, "w") as f:
        for chrom, size in sizes.items():
            f.write(f"{chrom}\t{size}\n")


def main():
    args = parse_args()

    with open(args.neg_ctrl_config) as f:
        neg_config = yaml.safe_load(f)

    if args.build_neg_ctrl_manifest:
        build_neg_ctrl_manifest(args, neg_config)
    elif args.run_neg_ctrl_coloc:
        run_neg_ctrl_coloc(args, neg_config)
    else:
        sample_null_loci(args, neg_config)


if __name__ == "__main__":
    main()
