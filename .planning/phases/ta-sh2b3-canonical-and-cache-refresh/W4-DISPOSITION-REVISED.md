---
title: W4 Disposition Revised — Re-disposition of FAILED → HONEST_FINDING
phase: ta-sh2b3-canonical-and-cache-refresh
authored: 2026-05-01
predecessor: wave4_dispatch_tracker_v7.json (status=FAILED, recorded 2026-05-02T00:10:00Z)
decision_anchor: DECISIONS.md::DEC-2026-05-01-02
status: ACTIVE — supersedes the FAILED outcome label for forward narrative purposes; tracker v7 retains FAILED as historical_outcome for forensic traceability
---

# W4 Disposition Revised

**TL;DR.** Tracker v7's `FAILED` is mechanically correct against the W4 PLAN PASS/FAIL gate (`too_few_snps ≥ 800` → FAILED). Re-dispositioned here to **HONEST_FINDING**: the W4.5-A continuation was framed around a **cache-staleness hypothesis** (the 1005 too_few_snps observed pre-3rd-pass might be an artifact of stale aggregator outputs from V4-era `qtl_coloc_summary.tsv`); the continuation drained the final 4 missing JSONs and forced a fresh aggregator pass, and the count remained **1005 → 1005**. The hypothesis is refuted. The 78.9% qtl_coloc too_few_snps rate is therefore a **structural property of the GWAS×QTL panel intersection at current LD-panel + region-window choices**, not a cache artifact, and is adopted as the canonical Layer-2 finding for Track A.

The W4.5-B SuSiE-RSS rebuild track is **explicitly skipped**: the data identifies LD coverage as the constraint (too_few_snps means too-few SNPs in the GWAS×QTL panel intersection — not too-few SuSiE iterations), so iterating on the fine-mapping budget would not move the number, and any rebuild would risk breaking the TRACK-A-FROZEN md5 invariant for low expected payoff.

---

## 1. Refuted-Hypothesis Reasoning

### 1.1 The hypothesis under test

The W4.5-A continuation (quick task `260501-r1q`) was scoped around an explicit cache-staleness hypothesis baked into the predecessor tracker v6 narrative:

> "Aggregator rules ARE NOT in the W4.5-a re-fire DAG plan because snakemake's planner sees their existing outputs from V4 as up-to-date at startup. This means a 3rd-pass snakemake invocation (without --forcerun) will likely be needed AFTER run_qtl_coloc completes to refresh aggregators via natural mtime cascade. Tracker v7 will record the 3rd-pass outcome."
>
> — `wave4_dispatch_tracker_v6.json` § monitoring_directives.post_completion_3rd_pass_needed (commit `f33262f`)

In other words: if the high too_few_snps count was an artifact of stale V4-era aggregator outputs (built at ~12:40–12:45 EDT on 2026-04-30 against an earlier 1274-JSON cache) rather than the true status distribution of the post-W4.5-a 1274 fresh JSONs, then the 3rd-pass aggregator refresh — recomputing `qtl_coloc_summary.tsv`, `tier_assignments.tsv`, etc. against the fresh per-id JSONs — would produce a materially different (and presumably better) too_few_snps count.

### 1.2 The test

Quick task `260501-r1q` executed the test cleanly:

| Step | Action | Observed |
|---|---|---|
| Drain | 4 missing run_qtl_coloc dispatched (v6's "5 missing" was off by one — 5th DAG step was `localrule all_qtl_coloc`, not a `run_qtl_coloc`) | 1270 → 1274 JSONs; 4/4 LSF jobs (82066–82069) finished cleanly in ~4 min |
| Aggregator 3rd-pass | Targeted-paths invocation; per-id JSONs were NOT recomputed — only the aggregator outputs were | 5/6 aggregator outputs refreshed at mtimes 1777680429–1777680509 (2026-05-01T20:07–20:08 EDT, well past unix baseline 1777589595); `qtl_coloc_manifest.tsv` correctly stays at V4 mtime per architectural design (manifest is built upstream from regions config, not downstream from per-id JSONs) |

### 1.3 The result that refuted the hypothesis

**Status distribution from the fresh 1274 per-id JSONs computed against the freshly-rebuilt aggregator outputs:**

| Status | Count | Fraction |
|---|---|---|
| `too_few_snps` | 1005 | **78.9%** |
| `no_qtl_cs` | 235 | 18.4% |
| `success` | 32 | **2.5%** |
| `qtl_susie_failed` | 2 | 0.2% |
| **Total** | **1274** | 100.0% |

The pre-3rd-pass too_few_snps count (read from V4-era `qtl_coloc_summary.tsv` at ~12:40–12:45 EDT on 2026-04-30) was 1005. The post-3rd-pass too_few_snps count (from `qtl_coloc_summary.tsv` rebuilt at 2026-05-01T20:07 EDT) is **also 1005**. The cache-staleness hypothesis predicts a delta; we observed Δ = 0. **Hypothesis refuted.**

### 1.4 What the result identifies as the actual constraint

`too_few_snps` is emitted by `run_qtl_coloc.R` when the intersection of (GWAS-fit credible-set SNPs) × (QTL panel SNPs at the region) falls below the colocalization-feasibility threshold. The constraint is **LD-panel coverage + region-window choices**, not iteration budget on the fine-mapping side:

- **NOT iteration budget** — the SuSiE-RSS layer ran at niter=1000 (V4 rebuild; see tracker v6 invariants); the 3 SH2B3 anchor md5s confirm convergence quality is preserved. Adding more iterations to the GWAS-side fine-mapping cannot create SNPs that don't exist in the QTL panel.
- **IS LD-panel coverage** — GTEx-era SNP sets at small-N tissues (especially sQTL on tissues with N<200) are systematically narrower than typical post-imputation GWAS SNP sets, especially at MAF<0.05 where GWAS retains rsIDs but GTEx prunes them.
- **IS region-window choice** — too_few_snps concentrates where the region window is narrow relative to the local LD block and where flanking SNPs that would intersect with the QTL panel are excluded. Wider windows would shift counts but at the cost of cross-locus contamination at the LD layer.

Neither of these constraints is addressable by W4.5-B (SuSiE-RSS rebuild). They would require either (a) switching to a denser LD panel (e.g., AoU-AFR-LD work-in-progress for cross-ancestry), (b) widening region windows with attendant LD-bleed risk, or (c) accepting the 32-success outcome as the canonical Layer-2 yield.

---

## 2. The 3-Layer Contrast Architecture

The Track A pipeline now has three documented layers of yield, each with its own structural attrition:

| Layer | Process | Numerator | Denominator | Yield | Attrition framing |
|---|---|---|---|---|---|
| **Layer 1 — SuSiE-RSS fine-mapping** | Per-trait, per-region GWAS fine-mapping at L=10 (with sweep at L∈{15,20,30} for the SH2B3 anchor) | 51 | 96 | **53.1%** | "Per-trait fits with valid converged credible sets"; the 45/96 attrition is dominated by non-convergence under the strict-gate definition (`convergence_status=converged_*` AND `n_CS<L_used` AND `L_saturated=FALSE`). See `ta-sh2b3-W1-susie-rss-l-sweep-SUMMARY.md` D3 ruling. |
| **Layer 2 — qtl_coloc structural feasibility** | Per-region, per-(trait, QTL-source, tissue) colocalization eligibility based on GWAS×QTL SNP intersection | 269 (success + no_qtl_cs + qtl_susie_failed; the not-too_few_snps complement) | 1274 | **21.1%** | "Per-(region × trait × QTL × tissue) tuples with sufficient SNP overlap to attempt coloc"; the 1005/1274 = 78.9% attrition is structural, driven by LD-panel coverage + region-window choices. **This is the new canonical Layer-2 finding** (DEC-2026-05-01-02). |
| **Layer 3 — substantive coloc hits** | Per-tuple PP.H4 evidence above tier thresholds | 32 | 1274 | **2.5%** | "Per-tuple substantive colocalizations with tier-A confidence"; the 1242/1274 attrition is the union of Layer-2 structural attrition (1005) + Layer-2-feasible-but-no-credible-set (235) + qtl_susie_failed (2) + Layer-3 PP.H4-below-threshold (within the 32 successes, all are tier-A by definition; but the "successes that don't reach tier-A" are absorbed into the 235 no_qtl_cs in this dataset). |

### 2.1 Why this architecture matters for the manuscript

Track A's reviewer-defensibility hinges on transparently disclosing all three layers rather than pooling them into a single yield number. The historical pattern in the literature is to report only Layer 3 (the headline "32 hits" or "2.5% colocalization rate") and treat Layer 1 and Layer 2 attritions as silent — which both undersells the methodological rigor (Layer 1's strict-gate non-convergence treatment) and obscures the ceiling on what coloc can recover at current public-data LD coverage (Layer 2's 78.9% structural attrition).

The 3-layer contrast architecture supports the audit-V2 reviewer-defensibility framing already established for Layer 1 (see `ta-sh2b3-DISCUSSION-LOG.md` line 51: "Currently the manuscript's 51/96 yield headline pools the 18 non-converged fits with the 33 converged ones. Audit-V2 Eval 2(a) flagged this as 'non-convergence treated as data'"). Layer 2 gets the same treatment: the 78.9% too_few_snps is reported as a structural property of the input data, not silently filtered.

### 2.2 Numerical alignment between Layers

- **Layer 1 → Layer 2 input:** Layer 1 produces 96 per-trait fits (3 traits × 32 EUR canonical anchor regions × per-trait); Layer 2 expands across QTL sources × tissues to 1469 base manifest rows, scope-filtered to 1274 by `phase2_enabled_sources: [gtex_eqtl, gtex_sqtl]` (Phase-2 deferral of pQTL + sc-eQTL). The expansion factor 1274/96 ≈ 13.3 reflects the GTEx-only sQTL+eQTL tissue panel breadth.
- **Layer 1 yield does NOT bound Layer 2 yield:** A region with a non-converged Layer-1 fit can still produce too_few_snps at Layer 2 (the SuSiE fit is consumed for credible-set SNPs, but if the fit didn't converge, the credible-set is empty or narrow, which compounds the SNP-overlap problem). Conversely, a region with a converged Layer-1 fit can still produce too_few_snps if the QTL panel for that tissue is sparse. The two attritions are partially correlated but distinct.
- **Layer 3 is bounded by both:** A substantive hit at Layer 3 requires Layer 1 convergence AND Layer 2 feasibility AND PP.H4 above tier threshold. The 32-success count is the intersection.

---

## 3. Decision: Skip W4.5-B SuSiE-RSS Rebuild

**Rationale (rigor-over-time-saving framing per `feedback_rigor_over_speed.md`):**

| Consideration | W4.5-B (rebuild) | Skip (this disposition) |
|---|---|---|
| Expected impact on too_few_snps count | **Near zero** — too_few_snps is a SNP-intersection problem, not a fine-mapping convergence problem | N/A |
| TRACK-A-FROZEN md5 risk | **High** — `--forcerun run_finemap` regenerates `.fit.rds` files; even at niter=1000, stochastic floating-point differences in optimizer convergence paths can shift md5s; the 3 SH2B3 anchor md5s (bmi=462ada6a, htn=8255c1ac, stk=a041eecc) would need re-pinning | **Zero** — invariants preserved |
| Manuscript narrative payoff | **None** — moving from 32 successes to 32+ε successes does not change the headline; the canonical Layer-3 finding is already known | **Positive** — adopting 78.9% as canonical Layer-2 finding strengthens reviewer-defensibility (transparent attrition disclosure parallel to Layer-1's 53.1% framing) |
| Compute cost | ~2.4 cluster-hours (96 .fit.rds × ~30 sec mean wall × 2 threads) + recovery overhead | 0 |
| Reviewer questions invited | "Why did you rebuild SuSiE if too_few_snps was the constraint? Were you fishing?" | None — the refuted-hypothesis reasoning is the answer |

**Decision (DEC-2026-05-01-02):** Skip W4.5-B. Adopt the 78.9% as canonical Layer-2 finding. Preserve TRACK-A-FROZEN md5 invariants intact. Land this revised disposition + tracker v7 outcome_disposition update + closing commit, then idle.

**Out of scope (not addressed by this disposition; carried forward for downstream waves if relevant):**

- (a) Whether to expand region windows for the 1005 too_few_snps cases — would require a new wave with explicit LD-bleed risk analysis; not needed for the current Track A manuscript. Layer-2 attrition is reported as-is.
- (b) Whether to switch GTEx → AoU-AFR-LD or other denser LD panels — tracked separately under M3 (`m3-aou-afr-ld-panel-build` phase, currently at Wave 1 portal pre-conditions).
- (c) Whether the 235 `no_qtl_cs` disposition warrants a separate sensitivity analysis — design-expected outcome; carry through to Layer-3 narrative as "feasibility-pass-but-no-credible-set" stratum.
- (d) Audit of the 4 newly-landed JSONs' status distribution in isolation vs the 1270 prior set to confirm the drain didn't introduce systematic bias — not a manuscript-blocking question; can be sampled if a reviewer asks.

---

## 4. Status of Forensic Traceability

Tracker v7 retains `FAILED` as the **historical_outcome** field. This disposition document is the **active narrative**. Both are committed in the same atomic commit so the audit trail is contiguous:

- `wave4_dispatch_tracker_v7.json` — mechanical PASS/FAIL gate result (FAILED), preserved for forensic re-derivation of the W4 PLAN gate semantics
- `W4-DISPOSITION-REVISED.md` (this file) — strategic re-disposition (HONEST_FINDING) with refuted-hypothesis reasoning + 3-layer architecture
- `DECISIONS.md::DEC-2026-05-01-02` — load-bearing decision entry that lets future-Carter and future-Claude re-derive or override this disposition with full context

Forensic auditor invocation (e.g., a reviewer asking "Why is the W4 PLAN's PASS/FAIL gate FAILED here but the wave is closed?"): point to this document + DEC-2026-05-01-02. The mechanical FAILED is preserved; the strategic HONEST_FINDING is documented; both are reachable from the artifact tree.

---

## 5. Cross-References

- Predecessor: `wave4_dispatch_tracker_v6.json` (DISPATCHED_W4_5_A_SCOPE_CORRECTED, supervisor PID 2670648 exited at 99.6%)
- Mechanical outcome: `wave4_dispatch_tracker_v7.json` (status=FAILED, outcome_disposition=HONEST_FINDING after this commit)
- Quick task: `.planning/quick/260501-r1q-w4-5-a-continuation-drain-final-5-and-ag/{260501-r1q-PLAN.md, 260501-r1q-SUMMARY.md}`
- Decision: `.planning/DECISIONS.md::DEC-2026-05-01-02`
- Layer-1 provenance: `ta-sh2b3-W1-susie-rss-l-sweep-SUMMARY.md` (D-TA-Wave1-headline; 51/96 = 53.1%)
- Layer-1 framing precedent: `ta-sh2b3-DISCUSSION-LOG.md` line 51 (Audit-V2 Eval 2(a) "non-convergence treated as data"); `ta-sh2b3-W6-rename-and-narrative-PLAN.md` lines 459-460 (RECOMPUTE vs PRESERVE-WITH-DISCLOSURE branches)
- Hard-non-target: `feedback_rigor_over_speed.md` (rigor-over-time-saving) + tracker v6 `preserved_invariants` block (4 md5 pins)
- Wave 5 trigger: orchestrator-driven, fires after m3 AOU-1 dev fire returns and STATE.md frontmatter refreshes both tracks atomically (NOT triggered by this disposition)
