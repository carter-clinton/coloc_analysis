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


# ---------------------------------------------------------------------------
# Helper: read AFR effective N for a trait from config or sample sizes file
# ---------------------------------------------------------------------------
def read_trait_afr_n(trait):
    """Read AFR effective sample size for a trait.

    First checks config/trait_sample_sizes.yaml, then falls back to
    a hardcoded table from Phase 0 / Phase 4 CONTEXT D-03c.
    """
    import yaml as _yaml
    from pathlib import Path as _P
    sizes_path = _P("config/trait_sample_sizes.yaml")
    if sizes_path.exists():
        with open(sizes_path) as fh:
            sizes = _yaml.safe_load(fh)
        if trait in sizes and "AFR" in sizes[trait]:
            return float(sizes[trait]["AFR"])
    # Fallback: known values from Phase 0 / Phase 4 data access audit
    _KNOWN_AFR_N = {
        "t2d": 55525,       # DIAMANTE AFR
        "stroke": 24000,    # MVP / GIGASTROKE AFR
        "hypertension": 28000, # Pan-UKBB / MVP AFR
        "asthma": 15000,    # Pan-UKBB / EAGLE AFR
        "bmi": 55500,       # MVP phs002453 AFR (primary)
    }
    if trait in _KNOWN_AFR_N:
        return float(_KNOWN_AFR_N[trait])
    raise ValueError(f"Cannot determine AFR N for trait: {trait}")


# ---------------------------------------------------------------------------
# Per-bootstrap SuSiE refit (D-01b)
# ---------------------------------------------------------------------------
rule run_matched_bootstrap:
    """D-01b: Per-bootstrap Z resampling + SuSiE refit via Phase 1 script."""
    input:
        eur_sumstats=lambda w: f"data/processed/region_analysis/sumstats_harmonized_fixed/{w.trait}_EUR.bgz",
        ld_rds="results/ld_reference/ukbb_eur/{region}.rds",
        manifest=str(MATCHED_N_OUT / "manifest.tsv"),
        susie_policy="config/susie_policy.yaml",
    output:
        fit_rds=str(FITS_ROOT / "{trait}/{region}/bootstrap_{b}/eur_matched.fit.rds"),
    params:
        trait_id=lambda w: MATCHED_N_TRAITS.index(w.trait),
        bootstrap_idx=lambda w: int(w.b),
        afr_n=lambda w: read_trait_afr_n(w.trait),
    resources:
        mem_mb=8000,
        runtime=60,
    shell:
        """
        python src/snakemake/scripts/bootstrap_driver.py \
            --trait {wildcards.trait} --trait-id {params.trait_id} \
            --region {wildcards.region} \
            --bootstrap-idx {params.bootstrap_idx} \
            --eur-sumstats {input.eur_sumstats} \
            --afr-n {params.afr_n} \
            --ld-matrix-rds {input.ld_rds} \
            --output-fit-rds {output.fit_rds}
        """


# ---------------------------------------------------------------------------
# Per-bootstrap coloc.susie (D-01c)
# ---------------------------------------------------------------------------
rule run_matched_coloc:
    """D-01c: coloc.susie per bootstrap; AFR discovery .fit.rds held fixed."""
    input:
        afr_fit="results/fine_mapping/susie/{trait}.AFR.{region}.fit.rds",
        eur_matched_fit=str(FITS_ROOT / "{trait}/{region}/bootstrap_{b}/eur_matched.fit.rds"),
    output:
        coloc_rds=str(MATCHED_N_OUT / "coloc/{trait}/{region}/bootstrap_{b}/coloc.rds"),
        coloc_tsv=str(MATCHED_N_OUT / "coloc/{trait}/{region}/bootstrap_{b}/coloc_summary.tsv"),
    resources:
        mem_mb=4000,
        runtime=30,
    shell:
        """
        Rscript src/snakemake/scripts/run_matched_coloc.R \
            --afr-fit {input.afr_fit} \
            --eur-matched-fit {input.eur_matched_fit} \
            --output-rds {output.coloc_rds} \
            --output-tsv {output.coloc_tsv}
        """
