"""Phase 4 — Matched-N cross-ancestry concordance (production rules).

Implements the pre-registered H7 hypothesis test: under matched-N bootstrap,
does observed EUR-AFR concordance drop >= 20pp (power artifact) or hold
(concordance is real)?

Structure:
    rule all_matched_n          — aggregate target (table2 + jaccard + rg + violin)
    rule build_matched_n_manifest — Phase 2 tier_assignments -> bootstrap manifest

Config loaded from config/matched_n.yaml (string literal per Phase 9 learning).
Schema validated by schemas/matched_n.schema.yaml.

Consumes:
    - Phase 1 .fit.rds (AFR discovery, fixed per D-01c)
    - Phase 2 tier_assignments.tsv (Tier A locus list)
    - Phase 5 munged sumstats + LD scores (for LDSC r_g)

Outputs to results/matched_n/:
    - table2.tsv (D-06a: 5 rows x 10 cols)
    - table2_jaccard.tsv (D-06b: credible-set Jaccard)
    - rg_matrix.tsv (D-04d: full trait-pair x ancestry-pair r_g)
    - supp_violin.pdf (D-06c: bootstrap concordance distributions)
"""
from pathlib import Path

# Load Phase 4 matched-N config additively (string literal, project-root-relative).
configfile: "config/matched_n.yaml"

# ---------------------------------------------------------------------------
# Constants from config
# ---------------------------------------------------------------------------
MATCHED_N_OUT = Path(config["output_root"])
FITS_ROOT = Path(config["bootstrap_fits_root"])
MATCHED_N_TRAITS = config["traits"]
BOOTSTRAP_N = config["bootstrap_n"]

# ---------------------------------------------------------------------------
# Aggregate target: final Phase 4 deliverables
# ---------------------------------------------------------------------------
rule all_matched_n:
    input:
        table2=str(MATCHED_N_OUT / "table2.tsv"),
        table2_jaccard=str(MATCHED_N_OUT / "table2_jaccard.tsv"),
        rg_matrix=str(MATCHED_N_OUT / "rg_matrix.tsv"),
        supp_violin=str(MATCHED_N_OUT / "supp_violin.pdf"),

# ---------------------------------------------------------------------------
# Manifest generation: Phase 2 tier_assignments -> bootstrap manifest
# ---------------------------------------------------------------------------
rule build_matched_n_manifest:
    """Build the matched-N bootstrap manifest from Phase 2 Tier A assignments.

    Cross-joins Tier A AFR loci x config traits x bootstrap indices (1..100).
    Handles bmi.AFR specially: if harmonized sumstats missing, emits rows with
    bmi_afr_status=unavailable flag (downstream rules skip bmi bootstrap and
    emit 'AFR-unavailable' sentinel in table2 per CONTEXT deferred-fallback-d).
    """
    input:
        tier_assignments="results/phase2/tier_assignments.tsv",
        config_file="config/matched_n.yaml",
    output:
        manifest=str(MATCHED_N_OUT / "manifest.tsv"),
    run:
        import csv
        import yaml
        from pathlib import Path as P

        # Load config
        with open(input.config_file) as fh:
            mn_cfg = yaml.safe_load(fh)

        traits = mn_cfg["traits"]
        n_boot = mn_cfg["bootstrap_n"]

        # Check bmi.AFR availability
        bmi_afr_path = P("data/processed/region_analysis/sumstats_harmonized_fixed/bmi_AFR.bgz")
        bmi_afr_available = bmi_afr_path.exists()

        # Read tier assignments and filter to AFR Tier A
        tier_a_regions = []
        with open(input.tier_assignments, newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            for row in reader:
                if row.get("tier", "").strip().upper() == "A":
                    tier_a_regions.append(row)

        # Write manifest: trait x region x bootstrap_idx
        outdir = P(output.manifest).parent
        outdir.mkdir(parents=True, exist_ok=True)

        with open(output.manifest, "w", newline="") as out:
            writer = csv.writer(out, delimiter="\t")
            writer.writerow([
                "trait", "ancestry_pair", "region_id",
                "afr_fit_rds", "bootstrap_idx", "bmi_afr_status",
            ])
            for trait in traits:
                # Determine bmi.AFR status
                if trait == "bmi" and not bmi_afr_available:
                    status = "unavailable"
                else:
                    status = "available"

                for region in tier_a_regions:
                    region_id = region.get("region_id", region.get("region", "unknown"))
                    afr_fit = f"results/fine_mapping/susie/{trait}.AFR.{region_id}.fit.rds"

                    for b in range(1, n_boot + 1):
                        writer.writerow([
                            trait,
                            "EUR_AFR",
                            region_id,
                            afr_fit,
                            b,
                            status,
                        ])

        print(f"Manifest written: {sum(1 for _ in open(output.manifest)) - 1} rows")
