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


# ---------------------------------------------------------------------------
# LDSC r_g matrix (D-04a/b/d) — 35 total tests
# ---------------------------------------------------------------------------
import itertools

RG_TRAITS = config["traits"]  # 5 T1 traits
RG_TRAIT_PAIRS = list(itertools.combinations(RG_TRAITS, 2))  # 10 cross-trait pairs
RG_ANCESTRY_PAIRS = config["rg_ancestry_pairs"]  # [EUR_EUR, AFR_AFR, EUR_AFR]

# D-04a: 10 cross-trait pairs x 3 ancestry-pair strata = 30 tests
# D-04b: 5 same-trait EUR-AFR benchmarks (is_global_benchmark=TRUE)
# Total: 35 tests; BH-FDR q<0.05 across all 35 per D-04c
RG_COMBOS = [
    (t1, t2, ap) for (t1, t2) in RG_TRAIT_PAIRS for ap in RG_ANCESTRY_PAIRS
] + [
    (t, t, "EUR_AFR") for t in RG_TRAITS
]


def _parse_ancestry_pair(ap):
    """Split 'EUR_AFR' -> ('EUR', 'AFR')."""
    parts = ap.split("_")
    return parts[0], parts[1]


rule ldsc_rg:
    """D-04a: Single LDSC r_g test for (trait1, trait2, ancestry_pair).

    Reuses Phase 5 LDSC infrastructure (D-04d): munged sumstats + 1000G LD
    scores + ldsc_py3 env. For EUR-AFR cross-ancestry tests, ref-ld-chr and
    w-ld-chr both use EUR ldscores (LDSC default for cross-ancestry per
    Bulik-Sullivan 2015 FAQ). SE>0.3 flag applied downstream by apply_fdr.py
    (research A-2 minimum-deviation).
    """
    input:
        munged_t1=lambda w: f"results/ldsc/munged/{w.trait1}_{w.ancestry1}.sumstats.gz",
        munged_t2=lambda w: f"results/ldsc/munged/{w.trait2}_{w.ancestry2}.sumstats.gz",
        ldscores=lambda w: f"data/reference/ldsc/ldscores_{w.ancestry1}/",
    output:
        log="results/matched_n/rg/{trait1}_{trait2}_{ancestry1}_{ancestry2}.log",
    conda:
        "../envs/ldsc_py3.yml"
    resources:
        mem_mb=4000,
        runtime=30,
    shell:
        # NOTE: For EUR-AFR cross-ancestry r_g, ref-ld-chr and w-ld-chr
        # both use EUR ldscores per LDSC convention. This is a known
        # limitation; SE>0.3 flag applied downstream (research A-2).
        """
        python $(which ldsc.py) \
            --rg {input.munged_t1},{input.munged_t2} \
            --ref-ld-chr {input.ldscores} \
            --w-ld-chr {input.ldscores} \
            --out results/matched_n/rg/{wildcards.trait1}_{wildcards.trait2}_{wildcards.ancestry1}_{wildcards.ancestry2}
        """


def _expand_rg_log_paths():
    """Expand all 35 r_g log paths from RG_COMBOS."""
    paths = []
    for (t1, t2, ap) in RG_COMBOS:
        a1, a2 = _parse_ancestry_pair(ap)
        paths.append(f"results/matched_n/rg/{t1}_{t2}_{a1}_{a2}.log")
    return paths


rule collect_rg_logs:
    """Parse LDSC .log files into a single TSV for downstream FDR (D-04c).

    Parses all 35 r_g test logs (30 cross-trait + 5 same-trait EUR-AFR
    benchmarks) via munge_trait_pair_rg.py.
    """
    input:
        logs=_expand_rg_log_paths(),
    output:
        tsv="results/matched_n/rg_raw.tsv",
    shell:
        """
        python src/snakemake/scripts/munge_trait_pair_rg.py \
            --log-dir results/matched_n/rg \
            --out {output.tsv}
        """


# ---------------------------------------------------------------------------
# FDR correction (D-04c) + SE flag (research A-2)
# ---------------------------------------------------------------------------
rule apply_rg_fdr:
    """D-04c: BH-FDR q<0.05 across all 35 r_g tests jointly.

    Also flags SE>0.3 as unreliable_se per research A-2 minimum-deviation.
    Output is D-06d supplementary table (rg_matrix.tsv).
    """
    input:
        tsv="results/matched_n/rg_raw.tsv",
    output:
        tsv="results/matched_n/rg_matrix.tsv",
    shell:
        """
        python src/python/apply_fdr.py \
            --in {input.tsv} --out {output.tsv} \
            --fdr-q 0.05 --se-flag 0.3
        """
