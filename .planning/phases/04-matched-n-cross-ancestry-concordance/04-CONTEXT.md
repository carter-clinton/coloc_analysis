# Phase 4: Matched-N cross-ancestry concordance — Context

**Gathered:** 2026-04-15
**Status:** Ready for research + planning
**Tier:** T2 (gated on CP#1 — conditional-go verdict 2026-04-15)

<domain>
## Phase Boundary

Replace the broken Table 2 from the original manuscript (which compared
incomparable trait-pairs across ancestries of vastly different sample
size) with a power-corrected cross-ancestry concordance analysis that
tests the pre-registered H7 hypothesis: under matched-N bootstrap, is
observed EUR-AFR concordance substantially lower than the unmatched
comparison (≥20% absolute reduction = "power artifact"), or does it
hold up (<20% = "concordance is real, not a power artifact")?

Consumes:
- Phase 1 `.fit.rds` fitted SuSiE objects (per trait × ancestry × region)
- Phase 1 `config/susie_policy.yaml` (reused verbatim, not forked)
- Phase 2 `tier_assignments.tsv` (Tier A+B gene-trait triples for the
  loci being matched-N bootstrapped)
- Phase 2 `coloc_summary.tsv` + PP.H4 sweep outputs
- All 5 T1 traits’ harmonized sumstats for EUR and AFR (BMI AFR tracked
  as ingestion gap — see Deferred)
- LDSC baseline infrastructure from Phase 5 (munged sumstats + LD scores
  for 1000G Phase 3 panels per ancestry)

Scope does NOT include:
- EAS / Hispanic matched-N (AFR-only per D-03 below; EAS generalization
  remains handled by Phase 9 D-05c BBJ gate)
- Individual-level data (Pan-UKBB, UK Biobank, All of Us) — matched-N
  is implemented at the summary-statistics level per D-01
- MR-based shrinkage — Phase 3 (T2-gated)
- New Table 2 *text* / manuscript integration — Phase 11

</domain>

<decisions>
## Implementation Decisions

### D-01: Bootstrap mechanism — SE-inflation + full SuSiE refit per bootstrap

- **D-01a:** EUR is "matched to AFR-N" via analytic SE rescaling:
  `SE_EUR_matched = SE_EUR × √(N_EUR / N_AFR_trait)`. N_AFR is
  trait-specific (per-trait N_eff from harmonized sumstats, not a fixed
  constant), so the match is per-trait, not per-study.
- **D-01b:** Per bootstrap b ∈ {1…100}: draw Z_b ~ N(β̂/SE_matched, 1) per
  variant independently within each region, reconstruct pseudo-sumstats
  (β̂_b = Z_b × SE_matched, keeping the Phase 1 region LD matrix R
  fixed), and refit SuSiE via `run_susie_rss` with the Phase 1
  `susie_policy.yaml`. Outputs 100 `.fit.rds` files per
  (trait × ancestry=EUR_matched × region).
- **D-01c:** Coloc.susie re-estimation runs per bootstrap using the
  bootstrap `.fit.rds` paired with the *same* AFR-discovery `.fit.rds`.
  This isolates power-induced variation on the EUR side while holding
  the AFR comparator fixed (the "discovery is AFR, can EUR-matched
  replicate?" framing).
- **D-01d:** Literature convention (Hou 2023, Mahajan 2022
  DIAMANTE-AFR power-matching). Compute envelope: 100 bootstraps × 5
  traits × ~200 regions × ~3 QTL sources ≈ 300k SuSiE fits + 300k
  coloc.susie calls. LSF array with per-trait-per-bootstrap chunking;
  expected wall-clock ~3–5 days on the standard LSF partition.
- **D-01e:** MVN Z-score resampling under LD (alternative considered)
  is documented as a sensitivity analysis deferred to Phase 11
  supplementary if NG reviewers request it. Not primary — adds compute
  without changing the H7 verdict at the pre-registered threshold.

### D-02: Primary concordance metric — locus-level Tier A retention

- **D-02a:** **Primary metric:** Fraction of AFR-discovered Tier A loci
  (from Phase 2 `tier_assignments.tsv`) for which the EUR-matched
  bootstrap median achieves Tier A (PP.H4 ≥ 0.8 AND at least one QTL
  coloc ≥ 0.8). Computed per trait; reported with 95% CI from the
  bootstrap distribution.
- **D-02b:** **Secondary metric:** Credible-set Jaccard index at
  matched loci. For each locus where both AFR and EUR-matched bootstrap
  achieve PP.H4 ≥ 0.5 (relaxed threshold to avoid conditioning on the
  primary criterion), compute |CS_AFR ∩ CS_EUR_b| / |CS_AFR ∪ CS_EUR_b|
  per bootstrap. Report mean + 95% CI.
- **D-02c:** **Tertiary sanity check:** lead-variant direction-of-effect
  sign agreement. Should be ~100% — any violation flags a pipeline bug,
  not a scientific finding.
- **D-02d:** Pre-registered H7 decision is evaluated against D-02a only:
  compare mean matched-N concordance (D-02a) to mean *unmatched*
  concordance (EUR at full N, computed once from Phase 2 outputs). A
  ≥20 percentage-point absolute reduction = "power artifact" framing;
  <20 = "concordance is real, not a power artifact."
- **D-02e:** The Phase 9 joint PP.H4 + effect-size criterion (D-04) is
  NOT reused here — it conflates coloc stability with effect-size
  stability, which would double-count power loss and inflate the
  observed concordance reduction.

### D-03: Matched-N scope — AFR only, all 5 T1 traits where AFR sumstats exist

- **D-03a:** Per-trait EUR→AFR matched-N bootstrap only. 5 traits × 1
  ancestry pair. EAS generalization is already handled by Phase 9 D-05c
  BBJ gate; duplicating here would be scope creep against the original
  Table 2 replacement mandate.
- **D-03b:** Hispanic scope explicitly excluded — Pan-UKBB Hispanic N
  is too small for meaningful EUR→HIS matching (would match EUR down
  to N~5k, noise-dominated).
- **D-03c:** Trait-by-trait AFR sumstats availability is the binding
  constraint. Confirmed available in Phase 0/1/2/9 data pipeline:
  - t2d.AFR (DIAMANTE AFR)
  - stroke.AFR (MVP or GIGASTROKE AFR stratum)
  - hypertension.AFR (Pan-UKBB or MVP)
  - asthma.AFR (Pan-UKBB or EAGLE AFR)
  - **bmi.AFR** — ingestion gap per STATE.md DEF-RO7-02 /
    Phase 0 D-20 open item. Plan must surface this as a dependency
    resolution before matched-N runs. Candidate source: Pan-UKBB AFR
    BMI continuous trait.

### D-04: LDSC cross-ancestry r_g scope — full trait-pair × ancestry-pair matrix

- **D-04a:** Run LDSC r_g across the full trait-pair × ancestry-pair
  matrix (C(5,2) = 10 trait pairs × {EUR-EUR, AFR-AFR, EUR-AFR} = up to
  30 tests). This goes beyond the global benchmark (same-trait
  cross-ancestry) to map how pleiotropy itself varies across
  ancestries — directly serves the project's
  "pleiotropy-across-ancestries" original research framing.
- **D-04b:** Same-trait × ancestry-pair r_g (5 tests: T2D-EUR vs
  T2D-AFR, etc.) is a distinguished subset reported as the "global
  benchmark for H7" — this is what matched-N concordance should
  approach under the null of equal causal architecture across
  ancestries.
- **D-04c:** Multiple-testing correction: Benjamini-Hochberg FDR at
  q<0.05 across ALL r_g tests in the matrix (not per-ancestry-pair,
  not trait-pair-stratified). Matches Phase 5 D-01a pathway FDR
  convention. Bonferroni + per-ancestry-pair BH are reported in
  supplementary as robustness-to-correction-choice.
- **D-04d:** Reuses Phase 5 LDSC infrastructure (munged sumstats per
  trait per ancestry, 1000G Phase 3 LD scores per ancestry, env
  `ldsc_py3`). No new data downloads required if Phase 5 first-
  production has landed munged sumstats for AFR.

### D-05: Hou et al. 2023 null — empirical β̂/SE from T1 Tier A

- **D-05a:** Expected detection probability under the null is computed
  per locus using this study's T1 first-production Tier A β̂/SE
  distribution as the effect-size prior. For each AFR Tier A locus
  with observed β̂_AFR, compute the expected chi-square
  non-centrality parameter (NCP) at N_EUR_matched, then the analytic
  P(χ² ≥ threshold | NCP) detection probability.
- **D-05b:** Per-locus expected detection probabilities aggregate to a
  trait-level "expected concordance under matched-N null" — directly
  comparable to the observed D-02a concordance. If observed >> expected,
  that's evidence for *more* concordance than power alone predicts
  (i.e., shared causal architecture).
- **D-05c:** Parametric prior from Hou et al. 2023 Table S1 is NOT used
  for the primary analysis. Empirical from study data is more tailored
  to the loci under study; Hou's prior is biased toward common-variant
  EUR architecture and may poorly describe AFR-Tier-A effect sizes.
- **D-05d:** Pooled vs per-locus: detection probability is per-locus,
  then aggregated (arithmetic mean across loci per trait) to match the
  D-02a metric. Alternative pooling (median, stratified-by-MAF) is
  deferred to Phase 11 supplementary if needed.

### D-06: Table 2 output structure

- **D-06a:** One row per trait. Columns (minimum required):
  1. Trait
  2. N_AFR_eff
  3. N_EUR_eff (full)
  4. N_EUR_matched (= N_AFR_eff after matching)
  5. Unmatched concordance % (from Phase 2, one number per trait)
  6. Matched-N concordance mean % (D-02a)
  7. Matched-N concordance 95% CI
  8. Expected concordance % under Hou 2023 null (D-05b)
  9. LDSC same-trait cross-ancestry r_g (D-04b) ± SE
  10. H7 verdict per trait ("power artifact" if col6 < col5 − 20pp;
      else "concordance holds")
- **D-06b:** Secondary Table 2b: credible-set Jaccard per trait with
  95% CI (D-02b).
- **D-06c:** Supplementary Figure: bootstrap concordance distributions
  as violin plots, one panel per trait, overlaid with observed
  unmatched concordance and Hou expected null.
- **D-06d:** Supplementary Table S-Ph4-1: full trait-pair × ancestry-pair
  r_g matrix with FDR-adjusted q-values and BH flags (D-04a).

### Claude's Discretion

- Exact LSF array topology (per-trait vs per-bootstrap chunking) — plan
  via compute-budget estimate during planning.
- Bootstrap seed strategy (fixed seed = `1000 * trait_id + bootstrap_idx`
  is sufficient; Carter preference TBD at review).
- Intermediate file retention: 100 × `.fit.rds` per (trait, region) is
  ~50–200 MB per locus; retain primary bootstrap outputs on
  `/rs1/researchers/c/ckclinto/`, cull intermediate Z-matrices after
  fits converge.
- Exact violin plot aesthetics, color palette, axis labels (reuse
  Phase 5 dashboard styling).
- Numeric rounding / significant figures on the final Table 2.
- Parallelization of LDSC r_g matrix (trivially embarrassing, 30
  independent LSF jobs).

</decisions>

<specifics>
## Specific References

- Hou et al. 2023 (PMC10403901 / Nat Genet) — matched-N bootstrap
  framework. Detection-probability framework in their Methods §3 is the
  primary analytic reference.
- Mahajan et al. 2022 (DIAMANTE, Nature Genetics) — SE-inflation
  approach for cross-ancestry power matching at T2D loci. Methods §6.
- Bulik-Sullivan et al. 2015 (LDSC original) + Martin et al. 2017
  (cross-ancestry r_g) — LDSC r_g per-ancestry-pair conventions.
- Project framing: pleiotropy-across-ancestries is an *original
  research claim*, not a revision artifact (user memory
  "feedback_original_research_framing"). D-04a scope reflects this.
- Pre-registered H7 hypothesis: `.planning/osf_prereg_draft.md` §H7
  line 102 (≥20pp absolute reduction threshold).
- Original broken Table 2: the current manuscript's Table 2 compared
  EUR trait pairs against AFR trait pairs without power matching. The
  new Table 2 is a per-trait concordance panel, not a trait-pair
  matrix — this is a structural replacement, not a cosmetic fix.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 4 scope + success criteria
- `.planning/ROADMAP.md` §Phase 4 (line 180) — 4 success criteria,
  T2 gating, dependency on CP#1.
- `.planning/checkpoints/T1_review.md` — CP#1 interim verdict granting
  conditional-go to T2 + §"What T2 planning should start on now"
  identifying Phase 4 as the first T2 target.
- `.planning/osf_prereg_draft.md` §H7 (line 102), §"Matched-N concordance"
  (line 320), §Hypothesis table (line 149) — pre-registered H7
  threshold and scope.

### Methodology + pre-registration
- `.planning/PROJECT.md` — Core value statement + constraints
  (100% public data, solo author, GPFS, no worktree isolation).
- `.planning/REQUIREMENTS.md` §REQ-11 — Tiered + gated scope rule.
- `.planning/DECISIONS.md` — Project-level decision log (current +
  historical).

### Upstream phase contracts (consumed inputs)
- `.planning/phases/01-coloc-susie-fine-mapping-spine/01-CONTEXT.md`
  §G1/G2 — `.fit.rds` output schema + `config/susie_policy.yaml`
  structure. Phase 4 consumes both unchanged.
- `.planning/phases/02-3-way-qtl-colocalization/02-CONTEXT.md`
  §D-01/D-02 — Tier assignment logic + PP.H4 sweep outputs. Phase 4
  uses `tier_assignments.tsv` as the AFR-Tier-A input list.
- `.planning/phases/02-3-way-qtl-colocalization/02-05-SUMMARY.md` —
  Final schema for tier outputs.
- `.planning/phases/05-pathway-partitioned-heritability/05-CONTEXT.md`
  §D-04 — LDSC baseline model + munged sumstats infrastructure that
  Phase 4 reuses for r_g.
- `.planning/phases/09-replication-in-independent-cohorts/09-CONTEXT.md`
  §D-04, §D-05c — Phase 9's joint replication criterion (not reused
  for primary per D-02e) + EAS/BBJ generalization gate (reason Phase
  4 scope is AFR-only per D-03a).
- `.planning/phases/09-replication-in-independent-cohorts/09-SMOKE.md` —
  TCF7L2/T2D positive-control β estimates (AFR=0.226, EAS=0.318,
  EUR=0.272) provide sanity-check anchors for the matched-N EUR
  bootstrap distribution around the AFR β.

### Legacy seed assets
- `src/legacy/region_analysis/scripts/cross_ancestry_compare.py`
  (319 lines) — Pairwise finemap/coloc comparison for the original
  broken Table 2. **Reuse as scaffold only** — its unmatched-N
  comparison logic is exactly what matched-N replaces. Harvest the
  per-region result-parsing and output-formatting helpers; discard
  the concordance computation.

### External literature (methodology)
- Hou et al. 2023 Nat Genet — Detection-probability framework (D-05).
- Mahajan et al. 2022 DIAMANTE Nat Genet — SE-inflation matched-N
  convention (D-01).
- Bulik-Sullivan et al. 2015 Nat Genet (LDSC) — r_g method.
- Martin et al. 2017 AJHG — Cross-ancestry r_g conventions.

### Downstream integration
- Phase 11 (manuscript) will consume the new Table 2 and
  Supplementary Figure S-Ph4-1 from this phase.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/legacy/region_analysis/scripts/cross_ancestry_compare.py` —
  Pairwise comparison skeleton. Harvest result parsing, TSV writers;
  discard its concordance logic.
- `src/snakemake/scripts/run_susie_rss.R` (Phase 1) — Called verbatim
  per bootstrap for the matched-N refit. No modifications.
- `src/snakemake/scripts/run_coloc_susie.R` (Phase 1) — Called
  verbatim per bootstrap for coloc re-estimation. No modifications.
- `src/snakemake/rules/pathway.smk` LDSC rules (Phase 5) — `ldsc_rg`
  rule is a trivial extension/new rule; munge + baseline already built.
- `src/python/sumstats_utils.py` (Phase 5) — Effective-N helpers for
  computing N_EUR_eff / N_AFR_eff per trait.

### Established Patterns
- **Snakemake rule module per domain:** Create
  `src/snakemake/rules/matched_n.smk` following the pattern of
  `replication.smk` (Phase 9) — self-contained, reads
  `config/pipeline.yaml`, outputs to `results/matched_n/`.
- **Config-driven scope:** Per Phase 9 D-03b (`signal_scope` config
  key), new config `config/matched_n.yaml` with keys `ancestry_pairs`,
  `bootstrap_n` (default 100), `seed_base`, `concordance_threshold`
  (default 0.8 = Tier A), `h7_reduction_threshold_pp` (default 20).
- **Panel-driven manifest:** Per Phase 9 D-03a, `build_matched_n_manifest`
  rule reads config + Phase 2 `tier_assignments.tsv` to emit a
  trait × AFR-Tier-A-locus × bootstrap_idx manifest.
- **.fit.rds reuse:** Per Phase 1 G1, the bootstrap additively creates
  new `.fit.rds` files at `results/matched_n/fits/` without touching
  the Phase 1 discovery `.fit.rds` files.
- **Parallelization:** Per Phase 1 / Phase 9 LSF conventions, use
  Snakemake rule parallelism (one job per bootstrap × trait × region)
  via `cluster_lsf.yaml` profile.

### Integration Points
- **Input:** Phase 1 `.fit.rds` (AFR discovery side, fixed) + Phase 2
  `tier_assignments.tsv` (Tier A locus list) + Phase 5 munged sumstats
  + LD scores (for r_g).
- **Output:** `results/matched_n/table2.tsv` (D-06a) +
  `results/matched_n/table2_jaccard.tsv` (D-06b) +
  `results/matched_n/rg_matrix.tsv` (D-04d) + bootstrap raw outputs
  under `results/matched_n/bootstraps/{trait}/{region}/{b}/`.
- **Downstream:** Phase 11 manuscript Table 2 + Supplementary
  Figure S-Ph4-1 + Supplementary Table S-Ph4-1.

</code_context>

<deferred>
## Deferred Ideas

- **MVN Z-score resampling under LD** — alternative bootstrap
  mechanism. Deferred to Phase 11 supplementary as
  "robustness-to-bootstrap-method" sensitivity analysis if NG
  reviewers push back on SE-inflation primary.
- **Parametric Hou 2023 prior** — as sensitivity analysis in Phase 11
  supplementary.
- **Per-ancestry-pair BH + Bonferroni for LDSC r_g** — as
  robustness-to-correction-choice in Phase 11 supplementary.
- **EAS and Hispanic matched-N** — EAS handled by Phase 9 D-05c
  generalization gate; Hispanic N too small to match. Backlog candidate
  only if T2/T3 feedback demands it.
- **bmi.AFR sumstats ingestion** — Phase 0 D-20 open item; Phase 4
  plan must surface this as a dependency (candidate source Pan-UKBB
  AFR BMI). If unresolvable, Phase 4 reports matched-N for 4 traits
  (t2d, stroke, hypertension, asthma) with bmi flagged as
  "AFR-unavailable, global LDSC r_g reported as proxy."
- **Joint PP.H4 + effect-size concordance criterion (Phase 9 D-04
  reuse)** — explicitly rejected as primary per D-02e; may reappear
  as a supplementary cross-check alongside D-02a if space permits
  in Phase 11.

</deferred>

---

*Phase: 04-matched-n-cross-ancestry-concordance*
*Context gathered: 2026-04-15*
