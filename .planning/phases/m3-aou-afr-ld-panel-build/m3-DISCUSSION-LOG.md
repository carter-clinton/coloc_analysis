# Phase M3: AoU AFR LD panel build — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in [`m3-CONTEXT.md`](m3-CONTEXT.md) — this log preserves the alternatives considered.

**Date:** 2026-04-27
**Phase:** m3-aou-afr-ld-panel-build
**Areas discussed:** EUR parity location, Region-list scope, Staging strategy, M2 supersede triggering, Spec-default carry-forwards (locked to defaults)

---

## Gray-area selection (multiSelect)

**Question presented:** "Which M3 gray areas do you want to discuss before planning?"

| Option | Description | Selected |
|--------|-------------|----------|
| EUR parity location | ROADMAP says "1000G + UKB"; AOU-LD-PIPELINE §3.4/§5.1 envisions in-AoU EUR build (~130-150k post-QC). Need to reconcile. | ✓ |
| Region-list scope | M2 produced 161 union regions; M3 fires both ancestries → 322 cells. Build subset vs full vs per-stratum split. | ✓ |
| Staging strategy | Spec §11 staging written for 3000 regions; collapses for our 161. Single-fire vs phased vs per-chromosome. | ✓ |
| M2 supersede triggering | 3 high-priority M2 obligations (clumping, LDSC slice, mtCOJO) want re-fire when AFR_aou lands. M3 vs M2-supplementary vs M4-defer. | ✓ |

**User's choice:** All 4 areas selected.

---

## Area 1 — EUR Parity Location

### Q1.1 — Where does the EUR parity LD panel get built?

| Option | Description | Selected |
|--------|-------------|----------|
| AoU EUR (parallel, in-Workbench) (Recommended) | Same Hail pipeline against `ancestry_pred=='eur'` (~130-150k post-QC). Check 2 becomes a methodological asset; same code path; same QC; one P&P. ~+40% AoU credit; reconciles ROADMAP wording by treating "1000G + UKB" as Check 2 comparator. | ✓ |
| NCSU 1000G + UKB | Keep EUR build on GPFS. 1000G EUR Phase3 plinkfiles already staged; UKB tile fetch DUA-gated (months). No code reuse with AoU half; UKB DUA timing is critical path. | |
| Defer EUR parity to M3-supplementary | Ship M3 with AFR_aou only; EUR_aou tagged for M3-supplementary. Smallest M3 footprint; deferred Check 2; M4 EUR uses existing 1000G EUR Phase3. | |
| AoU EUR at dev-only (10 regions) | Build full AFR_aou (161); EUR_aou at 10 dev regions ONLY (Check 2). M4 EUR continues on 1000G EUR Phase3. | |

**User's choice:** AoU EUR (parallel, in-Workbench). Recommended option.
**Recorded as:** D-M3-01

### Q1.2 — How does UKB fit into the EUR LD picture?

| Option | Description | Selected |
|--------|-------------|----------|
| UKB out of M3; keep AoU EUR alone (Recommended) | M3 ships AFR_aou + EUR_aou panels only. UKB DUA is critical path; not a M3 gate. ROADMAP M3 wording updated by Wave 0 to reflect "AoU EUR" as parity panel. UKB → M5/M6 supplementary if it lands. | ✓ |
| Stage UKB in parallel; merge if it lands | Continue UKB tile-access registration; if UKB lands by M3 close, merge (~480k composite). Highest possible eventual N; introduces M3 schedule uncertainty. | |
| Hard-block M3 on UKB EUR DUA | Wait for UKB DUA before firing M3. Cleanest endpoint; pushes M4 critical path months. | |

**User's choice:** UKB out of M3; keep AoU EUR alone. Recommended option.
**Recorded as:** D-M3-01.1

---

## Area 2 — Region-list Scope

### Q2.1 — How many region × ancestry cells does M3 build?

| Option | Description | Selected |
|--------|-------------|----------|
| All 161 × both ancestries = 322 cells (Recommended) | Build AFR_aou and EUR_aou for every region in `union_region_list.bed`. M4 has both panels available genome-wide; all 8 M2-supersede obligations have inputs; clean methodological symmetry. Highest credit burn (mitigated by §11 cost levers). | ✓ |
| AFR_aou × 161 + EUR_aou × 10 dev only | Full AFR; EUR only for Check 2. ~1.5× credit vs ~2×; M4 EUR continues on 1000G EUR Phase3. | |
| Priority subset × both — ~50 regions in first cut | Filter to MTAG/CPASSOC novel union (~50). Smallest production footprint; risks orphaning the 111 non-priority regions. | |
| Per-stratum split — 161 AFR + per-AFR-availability EUR | Build EUR_aou only for regions with AFR-stratum lead (~40-60 regions). Matches M4 cross-ancestry coloc demand; introduces region-classification step. | |

**User's choice:** All 161 × both ancestries = 322 cells. Recommended option.
**Recorded as:** D-M3-02

---

## Area 3 — Staging Strategy

### Q3.1 — How is the production fire structured after the 10-region dev pipeline passes the 4 checks?

| Option | Description | Selected |
|--------|-------------|----------|
| Dev-10 → Production-322 single fire (Recommended) | After dev clears Checks 1-4 and Carter signs the validation memo, fire all 322 production cells in one batch. Parallelism via concurrent Dataproc jobs. One Carter checkpoint; one egress entry per ancestry × per-chromosome batch. | ✓ |
| Dev-10 → Priority-50 → Remaining-272 | 50 highest-priority cells → checkpoint → remaining 272. Catches systemic-cost surprises mid-fire; extra checkpoint delays critical path. | |
| Dev-10 → Per-chromosome batches (22 fires) | Per-chromosome fire. Aligns with §7.2 per-chromosome export bundling; 22 fires = lots of human-action surface. | |
| Dev-10 → AFR-first-then-EUR (two fires) | All 161 AFR_aou first, then all 161 EUR_aou. AFR is critical path for novelty; doubles wall clock for total panel availability. | |

**User's choice:** Dev-10 → Production-322 single fire. Recommended option.
**Recorded as:** D-M3-03

### Q3.2 — How is the 10-region dev subset selected?

| Option | Description | Selected |
|--------|-------------|----------|
| Spec default: 3 EUR-comparable + 5 AFR-known + 2 HLA-stress (Recommended) | AOU-LD-PIPELINE §14 week 2-3 default exactly. Balanced across 4 checks; uses Track A's 11 EUR autosomal regions for Check 2 comparator. | ✓ |
| Track A 10 EUR autosomal regions only | Maximum Track A comparability; under-tests Check 1 + Check 3; no HLA stress. | |
| MTAG-novel intersection — first 10 by p-value | De-risks M4 directly at high-value loci; not necessarily HLA-stress-positive; not necessarily AFR-known-signal-positive. | |
| Hybrid — spec default + 1-2 MTAG-novel exemplars | Spec default + 1-2 production-priority loci (12 regions). Modest deviation from spec; small extra dev compute. | |

**User's choice:** Spec default 3 EUR-comparable + 5 AFR-known + 2 HLA-stress. Recommended option.
**Recorded as:** D-M3-04

---

## Area 4 — M2 Supersede Triggering

### Q4.1 — When the AFR_aou panel lands, how do the 3 high-priority M2-supersede obligations fire (M2-POST-M3-01 AFR clumping, -02 AFR LDSC, -03 AFR mtCOJO)?

| Option | Description | Selected |
|--------|-------------|----------|
| M2-supplementary phase (recommended) | M3 closes with panels + validation memo + egress audit log. Separate `m2-supp-aou-afr-rerun` phase fires the 3 re-runs. Clean M3/M2 boundaries; supersede artifacts get own SUMMARY.md + verification. Extra phase boundary. | ✓ |
| M3 close-out fires the 3 high-priority re-runs (extends M3 scope) | M3 ships panels + 3 superseded artifacts in one milestone. Faster end-to-end; if AFR clumping/LDSC reveals issue, M3 verification fails with large unblock iteration. | |
| M4 consumes new panel directly; M2 obligations close as "no-op pending need" | M4 uses AFR_aou directly; M2 obligations only fire if M4 demand surfaces divergence. Smallest scope; postpones cost; risks needing supersede mid-M4. | |
| Hybrid — M3 fires LDSC-02 only; supplementary phase for clumping-01 + mtCOJO-03 | M3 closes lightest obligation (LDSC ld-score swap); heavy ones to supplementary. Splits supersede story across two boundaries. | |

**User's choice:** M2-supplementary phase. Recommended option.
**Recorded as:** D-M3-05

---

## Spec-default carry-forwards

### Q5.1 — Three spec-level questions inherit AOU-LD-PIPELINE §15 defaults unless you want to revisit:

| Option | Description | Selected |
|--------|-------------|----------|
| Local dev mirror (P5) | Default per spec: build local conda env (hail + pyspark + google-cloud-storage) + tiny synthetic MT before any Dataproc spend. | |
| Ancestry inclusion logic | Default per spec §3: PCA-predicted as primary; self-report Black/AA as sensitivity check. | |
| Validation-memo external review | Default per spec §15 Q8: OSF deposit serves as external-reviewer substitute for sole-author constraint. | |
| None — lock all three to spec defaults | Skip all three; M3 plan inherits spec defaults verbatim. | ✓ |

**User's choice:** None — lock all three to spec defaults.
**Recorded as:** D-M3-06 (local dev mirror), D-M3-07 (ancestry inclusion), D-M3-08 (validation memo OSF posting)

---

## Claude's Discretion

None — all decisions resolved with Carter selection or explicit spec-default carry-forward.

---

## Deferred Ideas

Captured in [`m3-CONTEXT.md`](m3-CONTEXT.md) `<deferred_ideas>` section — 12 items including UKB EUR augmentation (D-M3-01.1), AoU AFR ld-score derivation (M2-POST-M3-05), AFR PLINK clumping/LDSC/mtCOJO re-fires (M2-POST-M3-01/02/03), GWAS Catalog v_lock_M5 refresh (M2-POST-M3-06), MTAG --fdr LSF re-fire (M2-POST-M3-07), mtCOJO production sensitivity LSF re-fire (M2-POST-M3-08), AoU v8 re-run policy, Hispanic-ancestry LD panel, AoU AFR/eGFR/SBP sumstats.

---

## Scope creep redirected

None during this discussion — all gray areas stayed within the AOU-LD-PIPELINE.md scope boundary.

---

## Discussion stats

- Areas presented: 4 + spec-default consolidation question
- Areas discussed: 4 (all selected)
- Questions asked: 6 (1 multiSelect gray-area pick + Q1.1 + Q1.2 + Q2.1 + Q3.1 + Q3.2 + Q4.1 + Q5.1 = 8 total)
- Recommended option taken on: 8 / 8 questions (Carter accepted all spec-aligned recommendations)
- Decisions locked: D-M3-01, D-M3-01.1, D-M3-02, D-M3-03, D-M3-04, D-M3-05, D-M3-06, D-M3-07, D-M3-08 (9 total)
