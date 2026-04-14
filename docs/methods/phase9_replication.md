# Phase 9 Replication Methods

> Draft methods fragment for manuscript (consumed verbatim by Phase 11).
> All design decisions are anchored to the project decision log
> (`.planning/DECISIONS.md`) and to `09-RESEARCH.md` under
> `.planning/phases/09-replication-in-independent-cohorts/`.

## Cohort portfolio (D-01)

We assessed replication of Phase 1 credible-set lead SNPs and Phase 2
Tier A+B gene-tissue-trait triples across four independent cohorts:

- **GBMI** (Zhou et al. 2022, *Cell Genomics*) — cross-biobank meta-analysis
  with per-ancestry EUR and AFR strata.
- **FinnGen R12** (Kurki et al. 2023, *Nature*) — Finnish founder-population
  EUR biobank release.
- **MVP phs001672** (Million Veteran Program, dbGaP open-access) — EUR, AFR,
  HIS, EAS, TRANS strata; per-trait availability inventoried in
  `mvp_phs001672_inventory.md`. Not all discovery traits are released in
  MVP (stroke, asthma, BMI flagged NOT_RELEASED as of 2026-04).
- **Biobank Japan, hum0197-v3** (Sakaue et al. 2021, *Nat Genet*) — EAS panel
  used as a cross-ancestry **generalization** reference (D-05c); see below.

All four cohorts are open-access per the project's `data_access.md`;
no cohort required a protected data-use agreement at submission time.

## Signal taxonomy (D-02)

Two signal classes entered replication:

1. **Credible-set lead SNPs** from Phase 1 fine-mapping, indexed by
   `(trait × ancestry × region)`.
2. **Tier A+B gene-tissue-trait triples** from Phase 2 colocalization
   (primary threshold PP.H4 ≥ 0.8 + tissue-matched QTL evidence).

Tier C exploratory signals were excluded (D-02b). BBJ routing additionally
filters to Tier A+B only (D-05c).

## Joint replication criterion (D-03)

A signal was declared **replicated** in a given cohort if and only if BOTH
conditions held:

(i) Same-direction β̂ with p < Bonferroni threshold
    `α = 0.05 / N_signals_tested_in_cohort` (per-cohort denominator, not
    family-wise; RESEARCH pitfall #4).

(ii) `coloc.susie(discovery_fit, replication_fit)` PP.H4 above threshold.
     We sweep the threshold over {0.5, 0.7, 0.8, 0.9}; the primary criterion
     uses 0.8 (D-03b). The master replication table reports all four sweep
     levels as separate boolean columns per (signal × cohort).

Both conditions are required — a strong effect-size re-discovery at the lead
SNP without coloc agreement is treated as insufficient evidence of shared
causal architecture (D-03a).

## Effect-size correction (D-04)

Discovery β̂ were corrected for winner's curse via **FIQT**
(FDR-inverse-quantile-transform; Bigdeli et al. 2016, *Bioinformatics*)
using the `winnerscurse` R package (Forde et al. 2023, *Bioinformatics*),
pinned to commit SHA `2ed00bb` for reproducibility.

The master replication table reports four effect-size columns per
(signal × cohort):

1. `beta_discovery_raw` — raw discovery β̂
2. `beta_discovery_FIQT` — FIQT-corrected discovery β̂
3. `{cohort}_beta_replication` — replication-cohort β̂
4. `beta_meta` — inverse-variance-weighted meta across ancestry-matched
   replication cohorts (`metafor::rma.uni(method = "FE")`, D-06b)

The post-hoc power computation (`power_posthoc` per cohort) uses
`beta_discovery_FIQT` as the effect-size anchor, not the raw discovery β,
so power is not inflated by the curse (RESEARCH pitfall #5).

## Ancestry-matched panels (D-05, D-05c)

Replication routing is strictly ancestry-matched:

| Discovery ancestry | Replication cohorts                           |
|--------------------|-----------------------------------------------|
| EUR                | FinnGen R12, GBMI-EUR, MVP-EUR                |
| AFR                | GBMI-AFR, MVP-AFR                             |
| EAS (discovery)    | BBJ only (primary); no cross-ancestry meta    |

For **Tier A+B signals only** (D-05c), BBJ-EAS is additionally used as a
**cross-ancestry generalization** panel. Signals that fail in BBJ-EAS are
reported as ancestry-specific, not as failed replications — the IVW
fixed-effect meta-analysis (D-06b, T-09-17) explicitly excludes
`is_generalization=TRUE` rows so EUR/AFR primary meta is never mixed with
cross-ancestry evidence.

Credible-set lead SNPs are **not** routed to BBJ generalization because
within-ancestry LD structure drives credible-set membership, making the
SNP-level cross-ancestry transferability question ill-posed; we restrict
generalization to gene-tissue-trait triples where the functional unit is
ancestry-agnostic.

## COJO sensitivity caveat (D-04c, RESEARCH gotcha #1)

As an orthogonal sensitivity we ran **GCTA-COJO** conditional + joint
analysis (`--cojo-slct`, `--cojo-p 5e-8`, `--cojo-wind 10000`) at complex
loci using 1000 Genomes Phase 3 LD references:

- **1000G EUR (N=503)** for EUR discoveries
- **1000G AFR (N=661)** for AFR discoveries

Both panels are below GCTA's recommended N ≥ 4000 threshold (Yang et al.
2012, *Am J Hum Genet*). We therefore flag COJO output as **tier-2
supplementary evidence** and do **not** treat COJO-failed loci as primary
non-replications. The caveat is enforced at three layers:

1. **Shell:** `run_cojo.sh` emits a `WARN` to stderr whenever the PLINK
   `.fam` row count is below 4000 (T-09-22 mitigation).
2. **Tests:** `tests/phase9/test_cojo_sensitivity.py` asserts the `4000`
   literal + `WARN` token + `set -euo pipefail` hardening are present.
3. **Methods (this document):** readers are alerted that
   `cojo_sensitivity.tsv` is a supplementary sensitivity, not a primary
   gate.

The primary joint criterion uses `coloc.susie` re-estimation on the
replication cohort (D-03), not COJO.

## Stroke endpoint heterogeneity (RESEARCH gotcha #3)

The four cohorts publish heterogeneous stroke endpoint definitions:

| Cohort      | Primary endpoint     | Sensitivity endpoint |
|-------------|----------------------|----------------------|
| FinnGen R12 | `I9_STR_EXH` (exhaustive any-stroke union) | `I9_STR` |
| BBJ         | `IS` (ischemic-only) | —                    |
| MVP         | NOT_RELEASED as main-effect GWAS in phs001672 | — |
| MEGASTROKE (Phase 1 discovery) | any-stroke | — |

We adopted **ischemic-only** as the primary cross-cohort stroke endpoint
(consistent at BBJ `IS` + FinnGen `I9_STR`) and report `I9_STR_EXH` /
any-stroke as a **sensitivity** in the supplementary holdout table so
discovery-definition breadth is explicit.

## Replication outputs

- `results/replication/master_table.tsv` — full replication matrix
  (one row per signal × cohort unrolled to per-cohort columns; 4
  effect-size columns; meta block; per-cohort sample_overlap_flag columns
  per RESEARCH §17 pitfall #3).
- `results/replication/cross_ancestry_generalization_tier_ab.tsv` —
  BBJ-EAS generalization panel (Tier A+B only; `is_generalization=TRUE`
  for every row).
- `results/replication/cojo_sensitivity.tsv` — GCTA-COJO joint analysis
  output per complex locus × cohort (tier-2 supplementary only; see
  caveat above).
- `results/replication/replication_holdout_supplementary.tsv` —
  leave-one-cohort-out IVW meta per signal (jack-knife sensitivity
  against cohort-driven outlier support).

## Citations

- Zhou et al. 2022. *Cell Genomics* 2:100192. GBMI flagship.
- Kurki et al. 2023. *Nature* 613:508-518. FinnGen R11 / R12 data freeze.
- Sakaue et al. 2021. *Nat Genet* 53:1415-1424. BBJ cross-population meta.
- Bigdeli et al. 2016. *Bioinformatics* 32:2598-2603. FIQT method.
- Yang et al. 2012. *Am J Hum Genet* 88:76-82. GCTA-COJO method + LD
  reference recommendations.
- Wallace 2020. *PLoS Genet* 16:e1008720. `coloc.susie` method.
- MVP phs001672 analysis files (dbGaP, accessed 2026-04).
