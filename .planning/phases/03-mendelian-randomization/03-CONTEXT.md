# Phase 3: Mendelian Randomization - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish causal direction between all 5 cardiometabolic trait pairs via bidirectional Mendelian randomization with robust weak-instrument mitigation for non-EUR ancestries. Instruments sourced from Phase 1 SuSiE credible sets. Includes 3 MVMR mediation tests for key triangular paths. Produces a bidirectional causal graph (main-text figure) and evidence matrix (supplementary).

</domain>

<decisions>
## Implementation Decisions

### D-01: Hypothesis scope & directionality
- **D-01a:** Test ALL 10 unique trait pairs (5-choose-2) in BOTH directions = 20 directed MR tests. Pre-register expected directions from literature but test both; non-significant reverse directions strengthen causal claims.
- **D-01b:** Include MVMR for 3 key triangular paths:
  1. BMI → Stroke adjusting for HTN (tests BP mediation)
  2. BMI → T2D adjusting for HTN (tests independence from BP pathway)
  3. HTN → T2D adjusting for BMI (tests independence from adiposity)
- **D-01c:** Config `mr.hypotheses` must be expanded from 3 to all 10 bidirectional pairs. MVMR triangles specified separately.

### D-02: Ancestry strategy (REQ-4)
- **D-02a:** **Ancestry-specific MR as primary analysis.** EUR is the strongest (largest instruments). AFR/EAS run with MR-RAPS where ancestry-matched GWAS exists.
- **D-02b:** **Trans-ancestry meta-MR (Lyon et al. 2023)** as additional sensitivity analysis — combines ancestry-stratified instruments with appropriate weights.
- **D-02c:** For trait pairs where one trait lacks non-EUR GWAS (bmi.AFR absent, hypertension AFR/EAS absent), run EUR-only MR. Document gaps explicitly in methods: "AFR/EAS MR not possible for pairs involving [trait] due to unavailable ancestry-matched GWAS."
- **D-02d:** This satisfies REQ-4: explicit ancestry-specific vs. trans-ancestry choice documented per pair; MR-RAPS mandatory for all non-EUR analyses.

### D-03: Instrument selection from SuSiE
- **D-03a:** **Lead SNP per credible set** (highest PIP variant from each SuSiE CS). For multi-signal regions (L>1), each CS contributes one independent instrument. Standard approach per Burgess 2023, Zuber 2023.
- **D-03b:** Complex regions (HLA_6p21, APOE_19q13, LPA/KIV-2, 9p21_CDKN2A, SLC2A9) **included in all analyses but flagged** in the diagnostic table. Let MR-PRESSO and MR-CAUSE detect if they are outliers. Do NOT exclude a priori.
- **D-03c:** **No minimum F-statistic threshold for instrument inclusion.** Report the full F-statistic distribution per ancestry per pair in supplementary. MR-RAPS is designed to handle weak instruments explicitly — no need for pre-filtering.
- **D-03d:** Instruments derived from FIQT-corrected discovery betas (Phase 9 winner's-curse adjustment), not raw discovery betas.

### D-04: Method triangulation & reporting
- **D-04a:** Run 5 MR methods per directed pair: IVW (random-effects), MR-Egger, weighted median, MR-PRESSO, MR-CAUSE. Plus MR-RAPS for all non-EUR analyses.
- **D-04b:** **Majority rule decision criterion:** call causal effect if >=3 of 5 methods reach nominal significance in the same direction. Pre-specifiable, reviewer-friendly.
- **D-04c:** **Steiger directionality filtering applied.** Instruments failing Steiger test are flagged (not dropped) to detect reverse causation. Standard in bidirectional MR (Steiger 2017).
- **D-04d:** **Bonferroni correction across 20 directed tests** (p < 0.0025). MVMR tests reported separately with their own correction (3 tests, p < 0.017).
- **D-04e:** Output as **both** directed graph (main-text Figure 5) and full evidence matrix (Supplementary Table). Graph: nodes = 5 traits, directed edges = significant causal effects, edge weight = IVW beta, edge style = confidence tier (strong: 3+ methods; moderate: 2; suggestive: 1). MVMR paths annotated.

### Claude's Discretion
- R package choices within TwoSampleMR/MR-CAUSE/MRPRESSO ecosystem
- Exact MVMR implementation (MVMR package vs. manual IVW extension)
- Diagnostic plot selection for supplementary (funnel, leave-one-out, forest)
- Steiger flagging visualization approach

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase inputs (instrument sources)
- `config/susie_policy.yaml` — SuSiE credible set policy, complex-region flags
- `src/legacy/region_analysis/scripts/run_susie_rss.R` — SuSiE output format (.fit.rds, .json)
- `config/pipeline.yaml` §mr — existing hypothesis config (must be expanded)

### Existing MR code (seeds)
- `src/legacy/region_analysis/scripts/create_mr_design.py` — manifest builder (reusable)
- `src/snakemake/rules/mr.smk` — stub rules (expand from here)

### Requirements
- `.planning/REQUIREMENTS.md` §REQ-4 — MR weak-instrument mitigation mandate

### Prior phase outputs consumed by MR
- Phase 1 `.fit.rds` files → SuSiE credible sets for instrument extraction
- Phase 2 tier assignments → gene-tissue context for interpreting MR results
- Phase 9 FIQT-corrected effect sizes → corrected betas for instrument construction

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `create_mr_design.py` (83 lines): Manifest builder parsing config hypotheses → TSV with exposure/outcome/ancestry/paths/status. Extend from 3 to 10+ bidirectional hypotheses + 3 MVMR.
- `mr.smk` (56 lines): Stub rules with correct conda env wiring (python_stats.yml, r_coloc.yml). Expand with actual MR execution rules.
- `sumstats_utils.py`: Effective-N computation, TRAIT_TYPE dict — reuse for MR sample size reporting.

### Established Patterns
- **Manifest-driven dispatch** (from Phase 2 QTL coloc, Phase 9 replication): build manifest TSV, then expand() rules over manifest rows. Apply same pattern for MR.
- **Per-ancestry processing** (from Phase 1 LD panels, Phase 9 replication): ancestry as wildcard, config-driven ancestry lists.
- **Sensitivity sweep** (from Phase 2 PP.H4 thresholds): report results across parameter grid, not single value.

### Integration Points
- `Snakefile` already includes `mr.smk` — rules will be discovered automatically
- `config/pipeline.yaml` §mr.hypotheses — expand with all 10 pairs + MVMR triangles
- `envs/r_coloc.yml` — needs TwoSampleMR, MRPRESSO, MR.CAUSE additions (check if present)

</code_context>

<specifics>
## Specific Ideas

- MVMR for 3 triangles is an elevation above basic bidirectional MR — it directly addresses the "pleiotropic loci" framing of the manuscript by testing mediation quantitatively
- Majority rule (3+/5) is pre-specifiable and maps cleanly to "strong/moderate/suggestive/null" evidence tiers in the causal graph
- The causal graph (Figure 5) should complement the colocalization Tier A/B matrix (Phase 2) — together they form the mechanistic narrative

</specifics>

<deferred>
## Deferred Ideas

- **Formal network MR / Bayesian mediation** — full path analysis with coefficients. Substantial scope, could be its own phase or post-submission extension.
- **Drug-target MR** — use gene-tissue coloc to proxy drug targets. Interesting for translational framing but adds Phase 2 dependency complexity.

</deferred>

---

*Phase: 03-mendelian-randomization*
*Context gathered: 2026-04-16*
