---
checkpoint: 1
tier_reviewed: T1
tier_gated: T2
status: interim — conditional go
verdict: PROCEED to T2 research + planning in parallel with T1 first-production
final_verdict_pending_on: first-production LSF launch of snakemake all_pathway + all_replication
created: 2026-04-15
authors: Carter K. Clinton (solo) + Claude
requirement: REQ-11
---

# Checkpoint #1 Review — End of T1 Spine (Interim)

> **Read first:** this is a **code-complete interim review**, not a data-complete verdict. T1 planning and implementation are finished (25/25 plans executed, security audits closed, test suites green, pre-flight smoke PASS). What has **not** yet happened is a first-production LSF launch that executes Phase 0 → 1 → 2 → 5 → 9 end-to-end against the full trait × ancestry × cohort grid. The final CP#1 verdict is reserved for after that run, but the conditions for conditional proceed-to-T2 are satisfied today.

## Scope

Per REQ-11, Checkpoint #1 is a written go/no-go decision that gates T2 (Phases 3 Mendelian randomization, 4 matched-N cross-ancestry, 8 cross-ancestry PRS). It is produced at the end of the T1 spine (Phases 0 Data/infra, 1 coloc.susie, 2 QTL coloc, 5 Pathway/h², 9 Replication).

This file serves that requirement in **interim form**: it documents what is provably true as of 2026-04-15, what remains to be verified on real data, and a recommendation keyed to those conditions.

## T1 spine status as of 2026-04-15

### Code completeness (25/25 plans)

| Phase | Plans complete | Verification | Security | UAT |
|---|---|---|---|---|
| **0** Data access + infra | 4/4 | ✓ | 10/10 threats closed | accepted (OSF DOI 10.17605/OSF.IO/PVB5J) |
| **1** coloc.susie fine-mapping | 5/5 (+ 01-06 formally closed via OSF amendment 2026-04-13) | ✓ | — | — |
| **2** 3-way QTL coloc | 5/5 | ✓ | — | — |
| **5** Pathway + partitioned h² | 5/5 | ✓ | — | `05-VALIDATION.md` verified 2026-04-15 |
| **9** Replication | 5/5 | `human_needed` for real-data UAT | 22/22 threats closed | 09-SMOKE PASS (see below); 2/3 HUMAN-UAT pending |

All 25 plans have SUMMARY.md artifacts. Test suites green (100 passed Phase 5; Phase 9 partial_pass). Security-auditor closed all 32 cross-phase threats.

### What is proven on real data

**Phase 9 pre-flight smoke (Strategy A, 2026-04-14)** — TCF7L2/T2D × 4 cohorts:

| Cohort | Ancestry | β (TCF7L2 rs7903146) | SE | P | N_eff |
|--------|----------|-----|------|-----|-------|
| FinnGen R12 | EUR | 0.256 | 0.007 | 1e-282 | 219K |
| MVP phs001672 | EUR | 0.280 | 0.005 | 2e-305 | 515K |
| MVP phs001672 | AFR | 0.226 | 0.014 | 6e-60 | 55K |
| BBJ hum0197-v3 | EAS | 0.318 | 0.022 | 2e-47 | 135K |

- EUR meta (FinnGen + MVP EUR): β = 0.272, SE = 0.004, p < 1e-308
- 3/3 replication rows pass Bonferroni + same-direction (Bonferroni-passing rate 100%, D-04 criterion 1)
- Cross-ancestry generalization to EAS: supported — BBJ β = 0.318 with same T-allele direction
- Effect-size + meta + master-table assembly code paths all validated
- coloc.susie re-estimation not exercisable without Phase 1 end-to-end LD panels (deferred, expected)

**Phase 5 MAGMA branch scout (bmi.EUR, 2026-04-14)** — real UKB BMI sumstats (Yengo 2018, N = 694649):

- `results/pathway/magma/bmi_EUR_geneset_fdr.tsv` — 9617 gene sets, 194 FDR_Q < 0.05
- Top hit **CUSTOM_APPETITE_REGULATION** q = 7.25e-11 — biologically coherent for BMI
- MAGMA annotate → gene-analysis → gene-set → FDR chain proven end-to-end
- g:Profiler / LDSC partitioned / LDSC-SEG / HESS branches of Phase 5 still require their own real-data scouts

### What is **not** yet proven on real data

The CP#1 success criteria in ROADMAP.md (§"Checkpoint #1: End of T1 spine") specify four artifacts. Three of them cannot be produced until a first-production Phase 0 → 1 → 2 → 5 → 9 LSF run completes:

| CP#1 criterion | Current state |
|---|---|
| Tier A signals that survived PP.H4 sweep + replication | **pending** — requires Phase 1 (discovery `.fit.rds` per trait×ancestry) + Phase 2 (`tier_assignments.tsv`) + Phase 9 coloc.susie re-estimation. All code in place; only single positive-control (TCF7L2) exercised so far. |
| Ancestry-level power retention under matched-N preview | **pending** — matched-N bootstrap is a Phase 4 (T2) deliverable. Preview requires either a Phase 4 sprint or a minimal proxy computation against first-production Phase 1 results. |
| Go/no-go decision with explicit evidence | **this document** (interim) → reissued as CP#1-final after first-production run |
| Submission target: AJHG vs Nature Genet pivot | **deferred** — contingent on Tier A signal count + cross-ancestry concordance magnitude (both require first-production data) |

## Decision

**Interim verdict: CONDITIONAL GO — proceed to T2 research + planning in parallel with T1 first-production execution.**

### Why conditional-go (not defer)

1. **T1 code + tests are provably complete.** 25/25 plans verified, 32/32 security threats closed, 100/100 Phase 5 tests green, Phase 9 pre-flight PASS. No known code blockers remain.
2. **Single positive control validates the pipeline.** TCF7L2 replicates cleanly across 4 cohorts with 3 ancestries. If the wiring were broken, this would have surfaced.
3. **Manuscript target is already Nature Genetics.** The project framing (see `PROJECT.md` core value + user memory "original research framing") commits to a mechanistically resolved cross-ancestry story. T2 phases (MR + matched-N + PRS) are the **mechanistic + causal + translational** layers that make the Nat Genet pitch defensible. Deferring T2 research until first-production completes would waste the parallelism this project was designed to exploit.
4. **Research and planning for T2 do not consume T1 compute.** Beginning T2 research (Phase 3/4/8 literature + method surveys) and phase planning in parallel does not block or interfere with T1 first-production runs.

### What the conditional constraints are

The "go" becomes **final** only when all three conditions below are met. Any condition failing requires revisiting this decision.

1. **First-production Phase 0 → 1 → 2 runs complete successfully.** Evidence: `results/fine_mapping/susie/*.fit.rds` populated for all trait×ancestry combinations; `tier_assignments.tsv` materialized with Tier A/B/C counts per ancestry.
2. **Phase 5 branches beyond MAGMA pass their real-data scouts.** g:Profiler, LDSC partitioned, LDSC-SEG, HESS each produce valid output on at least one trait×ancestry. The ten scout-surfaced integration concerns (now documented in `05-VALIDATION.md` Manual-Only) are the risk surface to watch.
3. **Phase 9 full DAG executes.** All four D-07 artifacts (`master_table.tsv`, `cross_ancestry_generalization_tier_ab.tsv`, `cojo_sensitivity.tsv`, `replication_holdout_supplementary.tsv`) materialize with populated per-cohort replication columns. HLA negative control check passes (≥70% HLA signals fail joint criterion in ≥3 of 4 cohort groups, per `09-HUMAN-UAT.md` test #2).

If any condition fails or surfaces a scientific-validity issue (not a fixable engineering bug), CP#1-final is revised to **NO-GO** and T2 work is halted.

### What T2 planning should start on now

Ordered by dependency:

1. **Phase 4 first (matched-N cross-ancestry).** Provides the ancestry-power-retention number that the final CP#1 verdict needs, and is the smallest-scope T2 phase. Spend planning effort here so first-production Phase 1 can be re-analyzed the moment it completes.
2. **Phase 3 second (Mendelian randomization).** `create_mr_design.py` + `mr.smk` seeds exist in `src/legacy/region_analysis/`. Planning should decide the trait-pair matrix, weak-instrument strategy per ancestry, and MR-PRESSO / MR-CAUSE configuration.
3. **Phase 8 third (cross-ancestry PRS).** Highest compute cost and most complex artifact; defer planning until Phase 4 is partially executed so the matched-N preview informs the PRS ancestry-transfer expectations.

## Submission target guidance

**Interim framing: Nature Genetics-primary with AJHG fallback.** The pipeline is architected for NG — the three analytical spines (coloc.susie + QTL coloc, bidirectional MR, matched-N cross-ancestry + selection scans) are the mechanistic, causal, and equity layers that collectively define a NG-competitive paper.

Decision rule at CP#1-final:

| First-production T1 outcome | Submission target |
|---|---|
| ≥ ~20 Tier A signals across ≥ 3 ancestries, ≥ 50% cross-ancestry concordance in matched-N preview | **Nature Genetics** — proceed with full T2 + selective T3 (6/7/10 gated at CP#2) |
| 5-20 Tier A signals across ≥ 2 ancestries, cross-ancestry concordance story intact but smaller | **Nature Genetics** attempt first; AJHG as fallback after 1 rejection |
| < 5 Tier A signals OR HLA negative control fails OR cross-ancestry story collapses | **AJHG** (T1 alone); halt T2 work; reassess whether the project should pivot to a descriptive-catalog manuscript |

Thresholds above are approximate and will be revised once first-production signal counts are known. They are recorded here to commit the decision rule **before** seeing the numbers.

## Artifacts referenced

- Phase 9 pre-flight smoke: `.planning/phases/09-replication-in-independent-cohorts/09-SMOKE.md`
- Phase 9 UAT state: `.planning/phases/09-replication-in-independent-cohorts/09-HUMAN-UAT.md`
- Phase 5 validation (scout-integrated): `.planning/phases/05-pathway-partitioned-heritability/05-VALIDATION.md`
- Phase 5 MAGMA scout artifacts: `.planning/quick/260414-bmi-magma-scout/SCOUT-FINDINGS.md`, `.planning/quick/260414-ww3-resume-bmi-eur-magma-fdr-scout-v8-re-lau/SUMMARY.md`
- Env hardening (scout issues #4–#7 closed): `.planning/quick/260414-wzy-env-yml-hardening-remove-defaults-channe/SUMMARY.md`
- OSF pre-registration: DOI 10.17605/OSF.IO/PVB5J (public, no embargo; amendment posted 2026-04-13 at osf.io/az52u)

## Next checkpoints on this document

- **CP#1-final** — reissued after first-production LSF launch completes. Populates the three "pending" criteria above with numeric evidence and locks the submission target.
- **CP#2** — after Phase 3/4/8 complete (gates T3 Phases 6/7/10).

## Sign-off

- [x] REQ-11 acceptance met: `.planning/checkpoints/T1_review.md` exists with explicit go/no-go decision
- [x] Decision rule for submission target recorded pre-data
- [x] Conditions for final verdict enumerated and testable
- [x] Parallel-track authorization for T2 planning + T1 first-production run granted
- [ ] First-production LSF launch executed *(pending)*
- [ ] CP#1-final issued *(pending on first-production completion)*

**Signed:** Carter K. Clinton, 2026-04-15 (interim)
