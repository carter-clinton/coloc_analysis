# Phase 4: Matched-N cross-ancestry concordance - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-15
**Phase:** 04-matched-n-cross-ancestry-concordance
**Areas discussed:** Bootstrap mechanism, Primary concordance metric, Matched-N scope, LDSC r_g granularity, Hou 2023 null, r_g test burden

---

## Gray Area Selection

User selected all 4 presented gray areas for deep-dive (Bootstrap mechanism, Primary concordance metric, Matched-N scope, LDSC r_g granularity). Hou 2023 null parameters surfaced as a follow-up after anchor decisions locked.

---

## Bootstrap mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| SE-inflation + full SuSiE refit per bootstrap (Recommended) | Analytic SE rescaling: SE_EUR_matched = SE_EUR × √(N_EUR / N_AFR). Then 100× parametric Z resampling feeds a fresh SuSiE fit per bootstrap. Hours-to-days LSF. Literature convention (Hou 2023, Mahajan 2022). | ✓ |
| Full variant re-resampling + SuSiE refit | Resample with replacement at the variant level, rebuild region LD subsets, refit SuSiE per bootstrap. Most rigorous for CS uncertainty but compute-prohibitive (~weeks on LSF). Methodologically awkward (rebuilding per-bootstrap LD). | |
| MVN Z-score resampling under fixed LD | Bootstrap from Z ~ MVN(μ=β̂/SE_matched, Σ=R). Refit SuSiE per bootstrap. Correctly propagates LD correlation into Z uncertainty. Middle-ground compute. | |

**User's choice:** SE-inflation + full SuSiE refit per bootstrap
**Notes:** MVN approach noted as Phase 11 supplementary sensitivity if NG reviewers push back.

---

## Primary concordance metric

| Option | Description | Selected |
|--------|-------------|----------|
| Locus-level Tier A retention (Recommended) | Primary: fraction of AFR-discovered Tier A loci where EUR-bootstrap median achieves Tier A. Secondary: credible-set Jaccard at matched loci. Direction-of-effect is downstream sanity check. Matches H7 phrasing. | ✓ |
| Credible-set Jaccard (variant-level IoU) | Variant-level overlap between AFR CS and EUR-bootstrap CS per matched locus. More granular; sensitive to LD-tagging. Risk: CSs often shift by a few variants under power reduction. | |
| Joint PP.H4 ≥ 0.8 + same-direction β (reuse Phase 9 D-04) | Phase 9 replication criterion applied cross-ancestry. Conflates coloc stability with effect-size stability — may double-count power loss. | |

**User's choice:** Locus-level Tier A retention (Recommended)
**Notes:** Jaccard retained as secondary metric in D-02b. Joint Phase-9 criterion explicitly rejected for primary per D-02e rationale (double-counting power loss).

---

## Matched-N scope

| Option | Description | Selected |
|--------|-------------|----------|
| AFR only (EUR→AFR per trait) (Recommended) | Scope matches original broken Table 2. 5 traits × 1 ancestry pair. Tight scope, fastest to ship. EAS generalization handled by Phase 9 BBJ gate (D-05c). | ✓ |
| AFR + EAS (where BBJ/EAS sumstats available) | EUR→AFR AND EUR→EAS per trait. Compute doubles. H7 testable twice. Risk: scope creep against "fix Table 2" mandate. | |
| AFR + EAS + Hispanic | All T1 non-EUR ancestries. Hispanic N typically too small for meaningful matching (noise-dominated). | |

**User's choice:** AFR only (EUR→AFR per trait)
**Notes:** EAS deferred to backlog per Phase 4 scope guardrail. bmi.AFR surfaced as an ingestion gap (Phase 0 D-20 open item); plan must resolve this before matched-N runs.

---

## LDSC r_g granularity

| Option | Description | Selected |
|--------|-------------|----------|
| Same-trait × ancestry-pair only (Recommended) | Global benchmark: T2D-EUR vs T2D-AFR etc. 5 tests. Minimal multiple testing. Directly benchmarks H7 null. | |
| Full trait-pair × ancestry-pair matrix | All pairwise trait × ancestry combinations. Up to 30 tests + Bonferroni. Richer context (e.g., "T2D↔BMI r_g is similar in EUR and AFR"). | ✓ |
| Tier-A-bearing trait pairs only | Restrict to trait pairs with ≥1 Tier A coloc from Phase 2. Lowest test burden; post-hoc subsetting may draw reviewer flags. | |

**User's choice:** Full trait-pair × ancestry-pair matrix
**Notes:** Carter overrode the recommended option to the more ambitious full matrix. Rationale per discussion: the expanded r_g matrix maps how pleiotropy itself varies across ancestries — directly serves the project's "pleiotropy-across-ancestries" original research framing (not just a benchmark). Same-trait subset is distinguished in D-04b as the "global benchmark for H7" within the larger matrix.

---

## Hou 2023 null parameters (follow-up)

| Option | Description | Selected |
|--------|-------------|----------|
| Empirical from T1 Tier A β̂/SE (Recommended) | Fit the Hou 2023 framework using this study's T1 first-production Tier A β̂/SE as the effect-size prior. Per-locus expected detection prob = P(χ²_NCP ≥ threshold). Robust — uses study's own distribution. | ✓ |
| Parametric from Hou 2023 published prior | Use effect-size distribution from Hou 2023 Table S1. Comparable to other matched-N papers but less tailored. Risk: Hou's prior biased toward common EUR variants. | |
| Both — empirical as primary, parametric as sensitivity | Report both. Empirical drives primary Table 2; parametric as supplement. | |

**User's choice:** Empirical from T1 Tier A β̂/SE
**Notes:** Parametric Hou prior deferred to Phase 11 supplementary as robustness-to-prior-choice.

---

## LDSC r_g test burden (follow-up)

| Option | Description | Selected |
|--------|-------------|----------|
| BH FDR at q<0.05 across all r_g tests (Recommended) | Benjamini-Hochberg joint FDR. Matches Phase 5 D-01a convention. | ✓ |
| Bonferroni across all r_g tests | Conservative. Likely misses genuine AFR-specific r_g patterns (Pan-UKBB AFR N-limited, SE-inflated). | |
| BH within ancestry-pair, reported separately | FDR applied independently per ancestry-pair matrix. Reviewers may view as post-hoc stratification. | |

**User's choice:** BH FDR at q<0.05 across all r_g tests
**Notes:** Bonferroni + per-ancestry-pair BH retained in D-04c as supplementary robustness-to-correction-choice.

---

## Claude's Discretion

- LSF array topology (per-trait vs per-bootstrap chunking)
- Bootstrap seed strategy
- Intermediate file retention policy
- Supplementary Figure aesthetics / color palette
- Significant-figure rounding on final Table 2
- LDSC r_g matrix parallelization

## Deferred Ideas

- MVN Z-score resampling — Phase 11 supplementary sensitivity
- Parametric Hou 2023 prior — Phase 11 supplementary robustness
- Per-ancestry-pair BH + Bonferroni for LDSC r_g — Phase 11 supplementary
- EAS and Hispanic matched-N — backlog candidate if T2/T3 feedback demands
- bmi.AFR sumstats ingestion — Phase 0 D-20 dependency, plan must resolve
- Joint PP.H4 + effect-size criterion — may reappear as supplementary cross-check in Phase 11
