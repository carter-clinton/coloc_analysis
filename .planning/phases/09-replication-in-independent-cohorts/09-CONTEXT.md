# Phase 9: Replication in Independent Cohorts - Context

**Gathered:** 2026-04-13
**Status:** Ready for research + planning

<domain>
## Phase Boundary

Validate T1 findings (Phase 1 coloc.susie credible sets + Phase 2 Tier A/B
gene-tissue-trait triples) in independent cohorts. Produces a master
replication table, per-signal replication status under a joint
effect-size + coloc criterion, winner's-curse-corrected effect sizes, and
a cross-ancestry generalization panel. This is the last T1 phase before
Checkpoint #1 (AJHG vs Nat Genet decision).

Scope does NOT include: new discovery in missing ancestries (EAS/HIS) —
that belongs to Phase 4 (T2-gated); MR-based shrinkage — Phase 3 (T2-gated);
AoU individual-level validation — Phase 8 (T2-gated); manuscript
assembly — Phase 11.

Consumes:
- Phase 1 `.fit.rds` fitted SuSiE objects (per trait × ancestry × region)
- Phase 2 `tier_assignments.tsv` (Tier A+B gene-trait triples)
- Phase 2 `coloc_summary.tsv` + PP.H4 sweep outputs
- `config/susie_policy.yaml` from Phase 1 (reused, not forked — per Phase 1 CONTEXT)

</domain>

<decisions>
## Implementation Decisions

### D-01: Cohort portfolio (belt-and-suspenders 4-cohort)

- **D-01a:** Four cohorts in scope: **GBMI + FinnGen R12 + MVP (dbGaP phs001672) + BBJ (hum0197-v3)**. All four are open-access or already registered (verified 2026-04-10, `.planning/data_access.md`). No DUA gate.
- **D-01b:** **AoU excluded from Phase 9.** Individual-level workbench + GCP compute is real infrastructure overhead for a solo-author project. Hispanic coverage available via GBMI AMR stratum. AoU pre-staged for Phase 8 (T2-gated PRS) if CP#1 greenlights T2.
- **D-01c:** GBMI plays the "cross-biobank meta" role (answers *"does it replicate across biobanks?"* in one artifact). FinnGen/MVP/BBJ play the per-ancestry native-replication role (answers *"does it replicate in a native non-meta cohort?"*). Both layers are required by D-03 (joint criterion).
- **D-01d:** deCODE pQTL (Ferkingstad 2021, ~4,907 aptamers, ~24 TB ephemeral downloads) remains deferred from Phase 2 CONTEXT D-01d. Not part of Phase 9 default scope; re-evaluate if reviewers request broader aptamer coverage post-submission.

### D-02: Replication unit — what gets tested

- **D-02a:** Full signal table, not top-N. Two classes of signal are tested:
  1. **Phase 1 credible-set lead SNPs** (per trait × ancestry × region from `.fit.rds` + `finemap_tier*.tsv`) — "does the fine-mapped variant replicate?"
  2. **Phase 2 Tier A+B gene-tissue-trait triples** (from `tier_assignments.tsv`, filter `tier ∈ {Tier A, Tier B}`) — "does the mechanistic claim replicate?"
- **D-02b:** Tier C signals NOT tested in primary replication. Reviewers won't push for replication of exploratory-tier signals; keeps table size defensible.

### D-03: Joint replication success criterion (strictest)

- **D-03a:** A signal counts as "replicated" in a given cohort if and only if BOTH of the following hold:
  1. **Effect-size criterion:** same-direction β in replication cohort, p < Bonferroni threshold computed per-cohort against the number of replicated-in-this-cohort signals
  2. **Coloc criterion:** re-run `coloc.susie(discovery_fit, replication_fit)` per region; require PP.H4 above threshold
- **D-03b:** **PP.H4 threshold sweep** `{0.5, 0.7, 0.8, 0.9}` — reuses Phase 2's sweep infrastructure (from D-01a/D-06 in Phase 2 CONTEXT). Produces a "which threshold holds" robustness table.
- **D-03c:** Rationale for joint requirement: effect-size replication alone can pass via a *different* causal variant (same signal, wrong mechanism). Coloc replication alone is posterior-probability-only and lacks frequentist effect-size evidence. Both together answer the statistical AND mechanistic replication questions — the Nat-Genet reviewer standard for a cross-ancestry coloc paper.

### D-04: Effect-size adjustment

- **D-04a:** **FIQT empirical Bayes winner's curse correction** (Bigdeli et al. 2016 Bioinformatics) — applied to discovery β̂ to produce shrinkage-corrected discovery effect.
- **D-04b:** Master replication table includes **4 effect-size columns per signal × cohort:**
  1. `beta_discovery_raw` — unadjusted (inflated by winner's curse)
  2. `beta_discovery_FIQT` — FIQT-corrected (the honest discovery effect)
  3. `beta_replication` — unbiased estimator from replication cohort
  4. `beta_meta` — IVW meta-analysis β (discovery + replication) where both reach significance
- **D-04c:** **COJO (GCTA conditional+joint analysis)** as SUPPLEMENTARY sensitivity, one supplementary table. Runs per complex locus to check whether independent secondary signals drive failed replications. Orthogonal to winner's curse; pre-empts reviewer comments about LD-dependent secondary signals.
- **D-04d:** BRcalibration considered and rejected — marginally better statistically but harder to defend methodologically as a solo author. FIQT is the defensible default.
- **D-04e:** MR-based shrinkage explicitly out of scope (Phase 3 is T2-gated).

### D-05: Ancestry-matching design — asymmetric (match where possible, generalize where not)

- **D-05a:** Discovery ancestries on disk from Phases 1/2: **EUR (all 5 traits), AFR (3 traits: t2d/stroke/asthma)**. EAS/HIS/AMR were NOT ingested in Phase 0 D-20 despite being planned; harmonized files do not exist. t2d.TRANS exists as a trans-ancestry meta.
- **D-05b:** **Primary panel — ancestry-matched replication:**
  - EUR discovery → FinnGen + GBMI-EUR + MVP-EUR
  - AFR discovery → MVP-AFR + GBMI-AFR
  - Output table: per-signal × per-cohort replication status + 4-column effect sizes
- **D-05c:** **Secondary panel — cross-ancestry generalization (BBJ only):**
  - For **Tier A+B signals ONLY** (not credible-set SNPs): test each EUR-discovered signal in BBJ-EAS as *evidence of generalization* (NOT claimed as replication)
  - Explicitly framed in methods as generalization, not replication — this is the cross-ancestry finding, not a weakness
  - If a signal fails EAS generalization, this is informative (reports ancestry-specific effect), not a negative result
- **D-05d:** GBMI EAS/AMR strata available but unmatched (no EAS/HIS discovery). Parked — potential supplementary analysis only if reviewers ask.
- **D-05e:** Ingesting missing-ancestry discovery (E2 option) was considered and rejected. That would balloon Phase 9 scope into "redo Phase 1/2 for missing ancestries" which is properly Phase 4 (T2-gated matched-N cross-ancestry) scope.

### D-06: Meta-analysis aggregation — both layers reported

- **D-06a:** **Per-cohort columns** in master table (one replication Y/N per signal per cohort). Most transparent for reviewers.
- **D-06b:** **META column** computed as IVW meta-analysis across replication cohorts matching discovery ancestry (see D-05b). Single "replicated in meta" summary column.
- **D-06c:** Both layers are always reported (no single-layer-only option). This is my discretion — reviewers want both.

### D-07: Replication table outputs (locked for planner)

- `results/replication/master_table.tsv` — signal × cohort × {replicated_bonferroni, replicated_pph4_0.5, replicated_pph4_0.7, replicated_pph4_0.8, replicated_pph4_0.9, beta_discovery_raw, beta_discovery_FIQT, beta_replication, beta_meta, se_replication, p_replication, pph4_replication}
- `results/replication/cross_ancestry_generalization_tier_ab.tsv` — BBJ-EAS generalization panel for Tier A+B signals only
- `results/replication/cojo_sensitivity.tsv` — COJO conditional+joint sensitivity (supplementary)
- `results/replication/replication_holdout_supplementary.tsv` — hold-out table for supplementary material (criterion #3 in ROADMAP)

### D-08: LD panels for replication coloc

- **D-08a:** EUR replication coloc uses **UKBB-LD** panel (reused from Phase 1).
- **D-08b:** AFR replication coloc uses **HGDP+1kG v3.1.2 AFR** panel (reused from Phase 1).
- **D-08c:** **EAS generalization coloc requires new LD panel** — 1000G Phase 3 EAS is cached from Phase 0 but Phase 1 did not extend to EAS (Scope B pilot stopped at AFR). Either: (i) extend `build_hgdp_1kg_ld` to produce EAS panels for the Tier A+B region set, or (ii) use 1000G Phase 3 EAS directly (~504 samples, smaller than BBJ would ideally match but defensible for generalization panel). Researcher to evaluate.
- **D-08d:** S-LDXR multi-ancestry LD scores (flagged in Phase 5 CONTEXT as possible Phase 9 add) — deferred. Not needed for the replication criterion as specified.

### Claude's Discretion (not surfaced to user)

- Exact phenotype-mapping per cohort (FinnGen endpoint codes, MVP ICD10+lab definitions, BBJ PheWeb-JP trait IDs, GBMI harmonized trait names) — researcher surveys and planner specifies
- FIQT implementation: use `winnerscurse` R package (Bigdeli-adjacent), `BEAM` (Ferreira & Purcell), or hand-coded from the Bigdeli 2016 formula — planner picks based on research
- COJO runner invocation details — reuses GCTA binary pattern from existing codebase if present
- Snakemake rule structure for replication pipeline (naming, resource allocation, conda envs) — planner decides
- Format of supplementary hold-out table (column order, rounding, etc.) — planner decides
- Handling of traits where MVP N is too small for Bonferroni power (e.g., MVP asthma) — documented caveat, standard practice
- Choice of liftover strategy per cohort (GBMI GRCh38, FinnGen R12 GRCh38, BBJ GRCh38, MVP mixed) — reuses Phase 0 liftover utility; cohort-specific logic is planner's call

</decisions>

<specifics>
## User Specifics

- Portfolio is **belt-and-suspenders** (#3 shape): GBMI cross-biobank meta + per-ancestry native. Not minimal-viable #1 (GBMI + FinnGen), not maximum #4 (all 5 including AoU).
- For BBJ generalization panel: **Tier A+B ONLY** (not Tier A/B/C, not credible-set SNPs). Keeps supplementary table size defensible.
- Replication criterion is **strictest option** (joint effect-size + coloc). User explicitly endorsed "both jointly required" over tiered criterion.
- Effect-size reporting: **4 columns + COJO sensitivity supplementary**. User endorsed full transparency over minimal presentation.
- Ancestry asymmetry is **accepted** — we match where we can, generalize where we can't, and explicitly frame generalization as the cross-ancestry finding rather than papering over it.

</specifics>

<deferred>
## Deferred Ideas

- **AoU individual-level validation** — Phase 8 (T2-gated PRS) territory. AoU access already credentialed; pre-staged for Phase 8 if CP#1 greenlights T2.
- **EAS/HIS/AMR discovery ingestion** — Phase 4 (T2-gated matched-N cross-ancestry) scope. Doing it here would redefine Phase 9 as "redo Phase 1/2 for missing ancestries."
- **deCODE pQTL broader aptamer coverage** — deferred from Phase 2 D-01d. Re-evaluate only if reviewers explicitly request.
- **S-LDXR multi-ancestry partitioned heritability** — flagged in Phase 5 CONTEXT. Not needed for D-03 replication criterion. Could be added as supplementary.
- **MR-based replication shrinkage** — Phase 3 (T2) territory. FIQT stands alone for T1.
- **BRcalibration effect-size correction** — considered, rejected for D-04 in favor of FIQT.
- **Tier C signal replication** — not in primary scope. Possible supplementary if reviewers push for exploratory-tier coverage.
- **GBMI EAS/AMR strata cross-ancestry analysis** — parked. Supplementary only if reviewers ask.
- **hyprcoloc multi-trait replication** — Phase 2 CONTEXT D-01f deferred hyprcoloc. Not revisited here.
- **Per-endpoint sensitivity within FinnGen** (e.g., T2D-without-metformin vs T2D-all) — out of scope; standard harmonization only.

</deferred>

<canonical_refs>
## Canonical References

Key papers:
- **Bigdeli, Lee, Webb et al. 2016** *Bioinformatics* 32:2598 — FIQT empirical Bayes winner's curse correction (D-04a)
- **Yang, Ferreira, Morris et al. 2012** *Nat Genet* 44:369 — GCTA-COJO conditional+joint analysis (D-04c)
- **Wallace 2020** *PLoS Genet* 16:e1008720 — coloc.susie method (reused from Phase 1, applied to replication per D-03a)
- **Zhou, Karjalainen, Graham et al. 2022** *Cell Genomics* 2:100192 — GBMI methods + public data release (D-01a)
- **Kurki, Karjalainen, Palta et al. 2023** *Nature* 613:508 — FinnGen R10 flagship (R12 update in 2024)
- **Ishigaki, Akiyama et al. 2020** *Nat Genet* 52:669 — BBJ T2D (phenotype definition reference for BBJ)
- **Sakaue, Kanai, Tanigawa et al. 2021** *Nat Genet* 53:1415 — BBJ multi-trait flagship (BMI, HTN, BP, asthma)

Phase-internal references:
- `.planning/phases/01-coloc-susie-fine-mapping-spine/01-CONTEXT.md` — susie_policy.yaml, LD panel architecture, `.fit.rds` schema (Phase 9 reuses verbatim)
- `.planning/phases/02-3-way-qtl-colocalization/02-CONTEXT.md` — Tier A/B definitions, PP.H4 sweep {0.5, 0.7, 0.8, 0.9}, tier_assignments.tsv schema
- `.planning/phases/05-pathway-partitioned-heritability/05-CONTEXT.md` — S-LDXR deferral (D-08d)
- `.planning/data_access.md` — cohort access status (FinnGen R12 registration, MVP dbGaP, BBJ hum0197-v3, GBMI open, AoU credentialed but deferred)
- `.planning/DECISIONS.md` — "All of Us: workbench-in / summary-out strategy" (AoU deferral rationale); T1 tier gating
- `.planning/REQUIREMENTS.md` — REQ-11 (T1/T2/T3 tier gating); no REQ directly assigned to Phase 9 but Phase 9 supports overall validity gates for CP#1

External resources:
- FinnGen R12 GCS bucket: `gs://finngen-public-data-r12/summary_stats/` (verified 2026-04-10)
- MVP dbGaP: `phs001672` (v3.p1 current; T2D sub-accessions `pha004943`-`pha004947`)
- BBJ NBDC: `https://humandbs.dbcls.jp/files/hum0197/hum0197.v3.BBJ.{TRAIT}.v1.zip`
- GBMI: `https://www.globalbiobankmeta.org/resources`

</canonical_refs>
