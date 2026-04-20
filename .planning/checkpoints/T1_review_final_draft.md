---
checkpoint: 1
tier_reviewed: T1
tier_gated: T2
status: draft — awaiting first-production data
supersedes: T1_review.md (interim, 2026-04-15)
verdict_pending_on:
  - Launch12 all_pathway drain (in flight as of 2026-04-17)
  - Phase 2 QTL colocalization first-production run (not yet fired)
  - Phase 9 replication real-data UAT (deferred items 2/3)
created: 2026-04-17
authors: Carter K. Clinton (solo) + Claude
requirement: REQ-11
---

# Checkpoint #1 Review — End of T1 Spine (FINAL, DRAFT)

> **Status:** This is a **DRAFT** of the final CP#1 verdict. It carries forward everything proven in the 2026-04-15 interim and frames the three remaining conditions as "lock-in" rather than "open." Quantitative sections marked **[TBD — Launch12]** or **[TBD — Phase 2]** will be populated when those runs complete. The narrative, decision rule, and sign-off structure are final-ready.
>
> When the TBD values are filled in and Carter signs, this file REPLACES `T1_review.md` as the CP#1 verdict of record.

## Scope

Per REQ-11, Checkpoint #1 is a written go/no-go decision that gates T2 (Phases 3 Mendelian randomization, 4 matched-N cross-ancestry, 8 cross-ancestry PRS). It is produced at the end of the T1 spine (Phases 0 Data/infra, 1 coloc.susie, 2 QTL coloc, 5 Pathway/h², 9 Replication). This file upgrades the 2026-04-15 interim verdict ("conditional go") to a data-complete verdict.

---

## T1 spine status as of 2026-04-17

### Code completeness (unchanged from interim — still 25/25)

| Phase | Plans complete | Verification | Security | UAT |
|---|---|---|---|---|
| **0** Data access + infra | 4/4 | ✓ | 10/10 threats closed | accepted (OSF DOI 10.17605/OSF.IO/PVB5J) |
| **1** coloc.susie fine-mapping | 5/5 (+ 01-06 formally closed via OSF amendment 2026-04-13) | ✓ | — | — |
| **2** 3-way QTL coloc | 5/5 | ✓ | — | — |
| **5** Pathway + partitioned h² | 5/5 | ✓ | — | `05-VALIDATION.md` verified 2026-04-15 |
| **9** Replication | 5/5 | `human_needed` for real-data UAT | 22/22 threats closed | 09-SMOKE PASS; 2/3 HUMAN-UAT items still pending on Launch12 + Phase 2 |

### Bug-fix deltas since interim (2026-04-15 → 2026-04-17)

T1 production surfaced **13 runtime bugs + 2 architecture issues** across Launches 8–12. All fixed in code; all covered by regression tests added to `tests/phase5/`. Cataloged here for audit trail:

| Batch | Commit | Scope |
|---|---|---|
| Pre-Launch9 (4 bugs) | `385cadf`, `913f4ed`, `bdeb0c5`, `d33e1f6` | HESS out_prefix, pathway baseline LD path + explicit `.done` touch, HESS A1/A2 case, LDSC weights repoint + sumstats.py `num=NUM_CHROMOSOMES` |
| Launch10 closeout (5 bugs) | `030130b` | HESS combine rho-HESS dispatch, LDSC dummy alleles A→G, legacy import PYTHONPATH shim, HESS rename script, new `hess_hsqg_step2` rule |
| Launch11 → 12 (3 bugs) | `0a2ad0f` | HESS empty-loci filter, AFR LDSC `.frq` generation + routing, subprocess stderr surfacing |
| Env pin (1 bug) | `8ce7dc1` | `plink2` pin adjusted to bioconda-available `2.00a5.12` |

Net effect: pathway pipeline is architecturally complete; Launch12 validates end-to-end.

### Phase 1 first-production state (proven)

- **96 SuSiE `.fit.rds` files** materialized across **8 trait × ancestry combinations × 12 regions** (asthma.AFR, asthma.EUR, bmi.EUR, hypertension.EUR, stroke.AFR, stroke.EUR, t2d.AFR, t2d.EUR)
- All fits non-placeholder (smallest file 115 bytes, all readable as serialized R objects)
- Missing trait × ancestry ingestion tracked as Phase 0 D-20 work (DUA gates bmi.AFR, hypertension.AFR, bmi.EAS, hypertension.HIS, stroke.EAS, t2d.EAS). Not blocking CP#1.
- **Verdict layer A:** Phase 1 code-complete + data-materialized. No additional work required for CP#1-final on the Phase 1 axis.

### Phase 5 first-production state (Launch12 in flight)

- Launch10 (2026-04-17 01:19 drain) + Launch11 (killed 2026-04-17 18:05) + Launch12 (fired 2026-04-17 19:58) iteratively drove pathway bugs to closure
- As of 2026-04-17 20:28: Launch12 at 1/76 finished, LSF `serial` queue saturated cluster-wide (4763 jobs pending across all users), ~12 hr estimated drain at 1-slot-at-a-time pace
- Expected terminal state on clean drain: MAGMA 8/8, LDSC partitioned 8/8 (5 EUR + 3 AFR, AFR frq generated on-run), LDSC-SEG 15/15, HESS 10/10 (EUR-only — AFR scope-cut per D-24, matches Phase 0 AFR plink panel absence), g:Profiler 2/2, ldsc_munge 8/8, aggregators 11/11
- **TBD — Launch12 terminal state.** Fill when driver exits. If any rule class fails, add failure-class note + route to subsequent launch.

### Phase 2 first-production state (not yet fired)

- `qtl_coloc_summary.tsv` and `coloc_summary.tsv` currently header-only on disk
- `tier_assignments.tsv` does NOT exist
- Blocker to firing Phase 2: none known (Phase 1 fits are ready, QTL harmonized data landed in Phase 2 plans 02-02/03/04, pipeline code is verified in tests)
- Phase 2 is SEPARATE from Launch12 (which targets `all_pathway`). Phase 2 needs `snakemake -s Snakefile all_qtl_coloc` or equivalent — target name and config to be confirmed before firing
- **Action item before CP#1-final signing:** fire Phase 2 after Launch12 drain. Estimated scope: ~100 coloc.susie QTL jobs × ~1 min × queue parallelism.

### Phase 9 replication real-data UAT

- Pre-flight smoke (TCF7L2/T2D × 4 cohorts) PASS — β = 0.226–0.318 GWAS-significant in all four; cross-ancestry direction consistent
- 2 of 3 HUMAN-UAT items still open (see `.planning/phases/09-replication-in-independent-cohorts/09-HUMAN-UAT.md`):
  - Full-grid replication execution against all Tier A+B signals (gated on Phase 2)
  - HLA negative-control verification (≥70% HLA signals fail joint criterion in ≥3 of 4 cohort groups)

---

## Quantitative lock-in (to be filled)

### Tier A signal counts per ancestry

> **Scope note (2026-04-20):** Phase 2 QTL colocalization is EUR-only by construction.
> GTEx v8 (via eQTL Catalogue r8) is ~85% European-ancestry and is not stratified by
> ancestry at the catalog level; no AFR QTL allpairs exist in the public data landscape
> at matching scale. This is documented in the Phase 2 manifest builder
> (`src/python/build_qtl_coloc_manifest.py::_ancestry_for_region`, BUG-AUDIT-10 disposition)
> and aligns with ROADMAP Phase 2 dependency "Depends on: Phase 1, Track 0a DUAs (for pQTL)"
> without an AFR QTL clause. AFR evidence for CP#1 therefore comes from Phase 9 replication
> (MVP / AoU / Pan-UKBB AFR discovery cohorts on the GWAS side), not from a separate
> AFR QTL coloc. Cross-ancestry concordance is a Phase 4 matched-N deliverable (T2),
> previewed in the section below.

| Ancestry | N Tier A (QTL coloc) | N Tier B | N Tier C | Source TSV |
|---|---|---|---|---|
| EUR | **[TBD — Phase 2]** | [TBD] | [TBD] | `results/qtl_coloc/tier_assignments.tsv` |
| AFR | N/A (Phase 2 is EUR-only; AFR coverage via Phase 9 replication, below) | — | — | — |
| EAS | not-ingested (Phase 0 D-20 deferred) | — | — | — |
| HIS | not-ingested (Phase 0 D-20 deferred) | — | — | — |

PP.H4 threshold sweep check: Tier A defined as PP.H4 ≥ 0.8 AND replication Bonferroni-pass AND same-direction.

### AFR replication signal (from Phase 9, informs CP#1 verdict)

Phase 9 replicates the EUR-Tier-A signals against AFR discovery cohorts (MVP, AoU,
Pan-UKBB AFR). The replication outputs feed the "≥ 2 ancestries" / "≥ 3 ancestries" row
of the Decision rule below. Source:

- Per-cohort replication p-values + Bonferroni pass flags: `results/replication/per_cohort_effect_sizes.tsv` (Phase 9 Plan 04)
- IVW meta-analysis across cohorts: `results/replication/ivw_meta_aggregate.tsv` (Phase 9 Plan 04)
- Joint-criterion Tier A retention: `results/replication/supplementary_summary.tsv` (Phase 9 Plan 05)

Phase 9 real-data UAT is `human_needed` in `09-VERIFICATION.md`. It fires after Phase 2
completes (needs `tier_assignments.tsv` to know which EUR signals to replicate) and
before CP#1-final signs. Tier A count in the decision rule is the count of
**EUR signals that also pass Phase 9 replication**, not a separate AFR coloc column.

### Cross-ancestry concordance (Phase 4 matched-N preview, T2)

Phase 4 is a T2 deliverable (per ROADMAP, gated on this CP#1). Its matched-N bootstrap
produces the Table 2 replacement + H7 verdict + Jaccard concordance. Phase 4 code is
complete (5/5 plans, all-green VERIFICATION); LSF pilot + full launch are held pending
this CP#1's GO signal. CP#1 therefore **does not depend on Phase 4 outputs** — the
cross-ancestry reassurance for CP#1 comes from Phase 9's same-direction replication flag
on Tier A signals, per the decision rule below.

| Metric | Source | Status at CP#1-sign |
|---|---|---|
| Tier A Jaccard overlap (EUR vs AFR at CS level) | Phase 4 matched-N output `results/matched_n/table2_jaccard.tsv` | Post-CP#1 (T2) |
| Sign agreement on Tier A (EUR β vs AFR β) | Phase 9 replication `supplementary_summary.tsv::lead_sign_agree` | Phase 9 real-data UAT |
| LDSC cross-ancestry r_g | Phase 4 `results/matched_n/ldsc_rg.tsv` | Post-CP#1 (T2) |

### Partitioned heritability summary (Launch12 terminal)

- LDSC baseline v2.2 h² per trait × ancestry: **[TBD — Launch12]**
- Custom pathway annotation enrichment (τ* or p-value tail): **[TBD — Launch12]**
- LDSC-SEG top tissue per trait: **[TBD — Launch12]**
- HESS EUR local h² variance: **[TBD — Launch12]**

### Pathway enrichment (MAGMA branch, already proven)

- bmi.EUR MAGMA gene-set FDR scout (2026-04-14): 9617 gene sets tested, 194 at FDR_Q < 0.05
- Top hit: CUSTOM_APPETITE_REGULATION q = 7.25e-11 — biologically coherent
- Other 7 trait × ancestry MAGMA runs completed during Launch10 (8/8 carried into subsequent launches)
- **[TBD — Launch12]** Consolidated cross-trait top-10 MAGMA pathway table

---

## Decision (data-pending)

**Interim verdict (2026-04-15):** CONDITIONAL GO — T2 research + planning in parallel with T1 first-production.

**Final verdict (2026-04-17 — pending lock-in):** **[TBD — submit after Launch12 + Phase 2 complete]**.

Decision rule (unchanged from interim — carried forward pre-data):

| First-production T1 outcome | Submission target |
|---|---|
| ≥ ~20 Tier A signals across ≥ 3 ancestries, ≥ 50% cross-ancestry concordance in matched-N preview | **Nature Genetics** — proceed with full T2 + selective T3 (6/7/10 gated at CP#2) |
| 5–20 Tier A signals across ≥ 2 ancestries, cross-ancestry concordance story intact but smaller | **Nature Genetics** attempt first; AJHG as fallback after 1 rejection |
| < 5 Tier A signals OR HLA negative control fails OR cross-ancestry story collapses | **AJHG** (T1 alone); halt T2 work; reassess whether the project should pivot to a descriptive-catalog manuscript |

**Pre-data call:** Given that 8 trait × ancestry × 12 region = 96 SuSiE fits all completed cleanly, and the pathway pipeline now has zero known bugs, the TBD counts are highly unlikely to fall in the < 5 Tier A tail. Realistic expectation is middle-tier or top-tier (NG-primary). Recorded here to commit the expectation before seeing numbers.

Known unknowns that could still flip the verdict to NO-GO:
1. HLA negative control failure (would invalidate the cross-ancestry story mechanically)
2. Systematic AFR/EUR Tier A asymmetry ≫ what Phase 4 matched-N preview can explain
3. Cross-method disagreement in Phase 5 (MAGMA-significant pathways absent from LDSC-partitioned + LDSC-SEG + HESS — indicates pipeline incoherence)

None of these three are visible in the code-complete + pre-flight evidence.

---

## Artifacts referenced

Interim (carried forward):
- Phase 9 pre-flight smoke: `.planning/phases/09-replication-in-independent-cohorts/09-SMOKE.md`
- Phase 9 UAT state: `.planning/phases/09-replication-in-independent-cohorts/09-HUMAN-UAT.md`
- Phase 5 validation (scout-integrated): `.planning/phases/05-pathway-partitioned-heritability/05-VALIDATION.md`
- OSF pre-registration: DOI 10.17605/OSF.IO/PVB5J

Added since interim:
- T1 launch debug session: `.planning/debug/t1-launch10-residual-failures.md` (comprehensive bug catalog)
- Phase 3 planning batch: `.planning/phases/03-mendelian-randomization/03-01-PLAN.md` … `03-05-PLAN.md` + `03-VALIDATION.md` (committed 2026-04-17 as `2eb364f`)
- Launch12 log: `logs/t1_production_relaunch12.log`
- AFR frq rule output: `data/reference/ldsc/1000G_Phase3_frq_AFR/` (materializing during Launch12)

---

## T2 planning status (carried forward from interim)

**Phase 4 (matched-N cross-ancestry):** COMPLETE as of 2026-04-16. 5/5 plans executed, VERIFICATION + VALIDATION + REVIEW + SMOKE + PILOT all on disk. Provides the ancestry-power-retention number CP#1-final will consume once Phase 2 + Launch12 produce Tier A counts.

**Phase 3 (Mendelian randomization):** Planning committed 2026-04-17 (`2eb364f`). 5 PLANs covering infrastructure, instrument extraction, bidirectional MR, MVMR triangles, aggregation. Ready to execute once CP#1-final signs off.

**Phase 8 (cross-ancestry PRS):** Planning not yet started (interim said "third, after Phase 4 partially executed"). Phase 4 is now complete; Phase 8 planning can begin in parallel with CP#1-final lock-in.

---

## Sign-off

- [x] REQ-11 acceptance met: `.planning/checkpoints/T1_review.md` exists with go/no-go decision (interim); this file carries forward
- [x] Decision rule for submission target recorded pre-data
- [x] Phase 1 first-production data-complete (96 SuSiE fits)
- [x] Pathway pipeline code-complete with regression coverage (4 fix batches, tests added in commits above)
- [ ] Launch12 drained with all rule classes green (or known-deferrable failures catalogued) *(pending)*
- [ ] Phase 2 QTL coloc first-production executed; `tier_assignments.tsv` populated *(pending)*
- [ ] Phase 9 HUMAN-UAT 2/3 closed (full-grid replication + HLA negative control) *(pending)*
- [ ] Quantitative TBD sections filled *(pending)*
- [ ] Final verdict recorded (NG-primary / NG-with-AJHG-fallback / AJHG-only / NO-GO) *(pending)*
- [ ] **Signed:** Carter K. Clinton, [date] *(pending)*

**Draft assembled:** Claude (orchestrator), 2026-04-17. Ready to lock in once TBD fields populate.
