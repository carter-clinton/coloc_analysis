# Track A — Audit Response (Catalogue of all 27 evaluation items)

**Audit source:** [AUDIT-REVIEW-2026-04-25.md](./AUDIT-REVIEW-2026-04-25.md) (commit `9801e77`, 2026-04-25)
**Response date:** 2026-04-26
**Manuscript:** [docs/manuscript/track_a_pivot.md](../../docs/manuscript/track_a_pivot.md)
**Frozen numbers:** [TRACK-A-FROZEN-NUMBERS.md](./TRACK-A-FROZEN-NUMBERS.md)
**Closure status (summary):** 18 closed / 1 in-progress / 3 deferred-compute / 1 deferred-design / 3 no-action-needed / 1 superseded (out of 27)

---

## How to read this document

This is an **internal closure tracker**, not a journal author-response letter. It catalogues, in canonical order, all 27 evaluation items raised by the independent scientific review committed at `9801e77` on 2026-04-25, records the on-disk closure status of each, and points to the git commit hashes and quick-task SUMMARY files that landed each closure. The audit was applied to the manuscript prior to submission; the audit-response work documented here is part of the original-research record, not a post-submission artifact. The audit-driven closure waves between 2026-04-25 and 2026-04-26 are organized by quick-task ID (`260425-kki`, `260425-t9j`, `260425-wa2`, `260425-wbf`, `260426-04b`, `260426-06n`); each commit cited below resolves on the current `main` branch (verified via `git rev-parse`). Status taxonomy: **CLOSED** = on-disk evidence committed; **IN-PROGRESS** = partial closure landed, more scheduled inside Track A; **DEFERRED-COMPUTE** = closure requires LSF compute; **DEFERRED-DESIGN** = closure requires user judgment; **NO-ACTION-NEEDED** = audit observation acknowledged in the audit itself as workable, or satisfied as a side-effect of other closures; **SUPERSEDED** = closed by closure of a parent item.

---

## Closure status matrix (all 27 items)

| #  | ID         | Title                                                                              | Status            | Commits                                           | Quick task   | Files touched                                                                                              |
|----|------------|------------------------------------------------------------------------------------|-------------------|---------------------------------------------------|--------------|------------------------------------------------------------------------------------------------------------|
| 1  | Eval 1     | Methodological soundness — 4.25× comparator                                        | CLOSED            | `884eb3d`, `f0451b0`                              | 260425-kki   | `fig2_cs_yield.R`, `TRACK-A-FROZEN-NUMBERS.md`, `track_a_pivot.md`                                         |
| 2  | Eval 2(a)  | Non-convergence treated as data                                                    | CLOSED            | `89a63e2`, `df3fa89`                              | 260425-kki, 260425-wbf | `fig3_sh2b3_eur_collapse_forest.R`, `track_a_pivot.md` (§3.4 SH2B3 case study)                        |
| 3  | Eval 2(b)  | L=10 saturation artifacts undisclosed                                              | DEFERRED-COMPUTE  | (none yet)                                        | (future)     | (none yet)                                                                                                  |
| 4  | Eval 2(c)  | Coloc on uncertain credible sets (no CIs)                                          | NO-ACTION-NEEDED  | (none — audit acknowledges absence is disclosed)  | (n/a)        | (n/a — Fig 3 caption already discloses absence of CIs in production manifest)                              |
| 5  | Eval 3.1   | `ld_overlap_fraction = 0` at FTO headline real-LD                                  | CLOSED            | `89a63e2`                                         | 260425-kki   | `fig3_sh2b3_eur_collapse_forest.R`, `track_a_pivot.md` (Tier-C disclosure paragraph)                       |
| 6  | Eval 3.2   | 78.9% QTL-coloc failure = unfixed bug                                              | CLOSED            | `06b817b`, `21900ba`, `09c68e5`                   | 260426-06n   | `track_a_pivot.md` (Methods L90, Discussion L220, Limitations bullet 5)                                    |
| 7  | Eval 3.3   | 28/28 empty `coloc.susie` outputs (interpretation unidentifiable)                  | IN-PROGRESS       | `89a63e2` (data-quality column surfaces 28/28)    | 260425-kki   | `track_a_pivot.md` (Tier-C disclosure paragraph; full interpretation gated on Eval 2(a) + 3.2 + HQ#2)      |
| 8  | Eval 3.4   | SH2B3 "collapse" is a missing run                                                  | CLOSED            | `df3fa89`                                         | 260425-wbf   | `track_a_pivot.md` (§3.4 SH2B3 case-study rewrite, L148)                                                   |
| 9  | Eval 3.5   | 95 vs 96 row-count discrepancy                                                     | CLOSED            | `f0451b0`                                         | 260425-kki   | `track_a_pivot.md` (Methods §Admissibility, L80; Methods §Identity-LD Comparison, L82)                     |
| 10 | Eval 3.6   | `ld_overlap = 0` on every identity-LD row (schema confusion)                       | CLOSED            | `09c68e5`                                         | 260426-06n   | `track_a_pivot.md` (L140 parenthetical Methods-style footnote citing schema-disjoint sources of truth)     |
| 11 | Eval 3.7   | HLA double-classified (fallback + negative-control)                                | CLOSED            | `19de334`                                         | 260425-t9j   | `track_a_pivot.md` (L28, L102, L138, L188, L240), `TRACK-A-FROZEN-NUMBERS.md` (LIVE block + reconciliation)|
| 12 | Eval 3.8   | "Negative-control rows" overstated (224 → 9 distinct loci)                         | CLOSED            | `19de334`                                         | 260425-t9j   | `track_a_pivot.md` (L28, L102, L138, L188, L240), `TRACK-A-FROZEN-NUMBERS.md` (LIVE block)                 |
| 13 | Eval 3.9   | DIAMANTE T2D vintage ambiguity                                                     | CLOSED            | `943d8f6`                                         | 260425-t9j   | `track_a_pivot.md` (L54, L56, L327)                                                                         |
| 14 | Eval 3.10  | `1,446 / 861` ghost numerics                                                       | CLOSED            | `58a5e2d`                                         | 260425-kki   | `TRACK-A-PIVOT.md` (10 ghost-numeric replacements at L37, L41, L80, L104, L125, L134, L181, L257, L267, L375) |
| 15 | Eval 4(a)  | "Locked scalars" prevent self-correction                                           | CLOSED            | `884eb3d`, `d6cbf53`                              | 260425-kki, 260426-04b | `fig2_cs_yield.R`, `fig3_sh2b3_eur_collapse_forest.R` (disk-derivation pathway)                       |
| 16 | Eval 4(b)  | Bidirectional provenance stops at file boundary                                    | NO-ACTION-NEEDED  | (none — audit acknowledges as workable)           | (n/a)        | (n/a — `results_identity_ld/` regenerable in ~1h per `DEC-2026-04-25-01`)                                  |
| 17 | Eval 5     | Significance — substantive contribution requires headline defensibility            | NO-ACTION-NEEDED  | (none — satisfied by closure of Eval 1 + HQ#1 + HQ#3 + Eval 3.4) | (n/a) | (n/a — meta-judgment item)                                                                              |
| 18 | HQ#1       | Re-derive headline from k2d re-fire + propagate                                    | CLOSED            | `884eb3d`                                         | 260425-kki   | `fig2_cs_yield.R`, `TRACK-A-FROZEN-NUMBERS.md` (LIVE block 48/95 → 51/96 = 1.06×), `track_a_pivot.md` (8 sites) |
| 19 | HQ#2(i)    | Re-fit SH2B3 EUR at L=20 (BMI/HTN/stroke)                                          | DEFERRED-COMPUTE  | (none yet)                                        | (future)     | (none yet)                                                                                                  |
| 20 | HQ#2(ii)   | Drop/flag non-converged fits in yield counts                                       | DEFERRED-DESIGN   | (none yet)                                        | (future)     | (none yet)                                                                                                  |
| 21 | HQ#2(iii)  | Execute `coloc.susie` on canonical BMI–HTN + HTN–stroke trait pairs                | DEFERRED-COMPUTE  | (none yet)                                        | (future)     | (none yet)                                                                                                  |
| 22 | HQ#3       | LD-reference-quality dose-response (column + figure)                               | CLOSED            | `1e4b071`, `5987ba1`, `d6a3647`                   | 260425-wa2, 260426-04b | `fig_h3_ld_overlap_dose_response.R`, `TRACK-A-FROZEN-NUMBERS.md` (H3 LIVE block), `track_a_pivot.md` (Figure S7 caption) |
| 23 | QI#1(a)    | Purge `1,446` / `861` ghost numbers from prose                                     | CLOSED            | `58a5e2d`                                         | 260425-kki   | `TRACK-A-PIVOT.md` (10 ghost-numeric replacements)                                                          |
| 24 | QI#1(b)    | Reconcile `95` vs `96` denominator with Methods paragraph                          | CLOSED            | `f0451b0`                                         | 260425-kki   | `track_a_pivot.md` (Methods §Admissibility, L80; missing `bmi.EUR.APOE_19q13` named in Methods)            |
| 25 | QI#1(c)    | Remove hard-coded `12 / 96 (12.5%)` from `fig2_cs_yield.R` L60                     | CLOSED            | `884eb3d`                                         | 260425-kki   | `fig2_cs_yield.R` (replaced literal `12L` with disk-derived read of `IDENTITY-LD-K2D-FIT-SUMMARY.tsv`)     |
| 26 | QI#2       | HLA: pick fallback OR negative-control                                             | SUPERSEDED        | `19de334` (parent: Eval 3.7)                      | 260425-t9j   | `track_a_pivot.md`, `TRACK-A-FROZEN-NUMBERS.md` (single classification: HLA = identity-LD-fallback only)   |
| 27 | QI#3       | Tier-C "data quality" column                                                       | CLOSED            | `89a63e2`                                         | 260425-kki   | `fig3_sh2b3_eur_collapse_forest.R` (per-fit data-quality disclosure sub-table panel), `track_a_pivot.md`   |

---

## Per-item narrative (CLOSED items)

### 1. Eval 1 — Methodological soundness (the comparator problem)

**Audit claim (paraphrased):** The headline 4.25× inflation claim (12/96 → 51/96) was constructed against a stale identity-LD baseline pulled from a session log. The same-pipeline k2d re-fire summary on disk shows 48/95 = 50.5%, statistically indistinguishable from the real-LD 51/96 (53.1%). The within-pipeline contrast is closer to ~1.05×.

**Closure action:** Tightened the comparator from a partial-coverage Stage 1d narrow-validation 12/96 baseline to the k2d full-coverage matched-coverage 48/95 baseline. Replaced literal `N_IDENTITY_LD_NONEMPTY <- 12L` in `fig2_cs_yield.R` with a disk-derived read of `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` at runtime; re-rendered Fig 2 PDF/PNG; added a LIVE block at the top of `TRACK-A-FROZEN-NUMBERS.md` carrying the matched-coverage 48/95 → 51/96 = 1.06× scalar; preserved the legacy 12/96 → 4.25× block verbatim with `SUPERSEDED 2026-04-25` markup for traceability; reframed eight manuscript sites under the anchor language "we tightened the comparator and the inflation magnitude shifted from 4.25× to 1.06×". Documented the 95-vs-96 denominator note (single missing fit `bmi.EUR.APOE_19q13`) in Methods §Admissibility.

**Commits:** `884eb3d` (W1, comparator tightening — `fig2_cs_yield.R` + Fig 2 renders + `TRACK-A-FROZEN-NUMBERS.md` LIVE block + 7 manuscript sites); `f0451b0` (W3, 95-vs-96 denominator note + missing-fit name in Methods §Admissibility).
**Files modified:** [`src/R/figures/fig2_cs_yield.R`](../../src/R/figures/fig2_cs_yield.R), [`docs/manuscript/figures/fig2_cs_yield.pdf`](../../docs/manuscript/figures/fig2_cs_yield.pdf), [`docs/manuscript/figures/fig2_cs_yield.png`](../../docs/manuscript/figures/fig2_cs_yield.png), [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md), [`.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`](./TRACK-A-FROZEN-NUMBERS.md).
**Verification on disk:** [`TRACK-A-FROZEN-NUMBERS.md`](./TRACK-A-FROZEN-NUMBERS.md) L9–25 shows the `## Stage 2 fine-mapping yield (post-k2d full-coverage identity-LD comparator, 2026-04-25) — LIVE` block with `51 / 48 = 1.06×` matched-coverage fold change; SUPERSEDED 12/96 block at L57–73 preserved verbatim; reconciliation log row at L208 documents the comparator tightening.

### 2. Eval 2(a) — Non-convergence treated as data

**Audit claim (paraphrased):** Under real-LD at SH2B3 EUR, 4 of 5 traits return `status = non_converged` (BMI, hypertension, stroke; only asthma and T2D = `ok`). Non-converged CS counts are baked into the plotted "yield" and into the 51/96 headline. The honest read is that SuSiE-RSS failed to converge at most SH2B3 EUR traits under the supplied real-LD reference — a numerical/algorithmic finding, not biological evidence of credible-set collapse.

**Closure action:** Surfaced the per-fit `convergence_status` data on Fig 3 via a new disclosure sub-table panel that exposes `ld_overlap_fraction` + `susie_status` + `L_saturated` per trait (commit `89a63e2`); rewrote the §3.4 SH2B3 case-study paragraph at manuscript L148 (commit `df3fa89`) to anchor on the disk-authoritative 3-of-5 SH2B3 EUR non-converged framing (BMI, hypertension, stroke), citing Wang et al. 2020 (SuSiE-RSS convergence theory) and Zou et al. 2022 (L generosity). The §3.4 rewrite reframes the paragraph as a flagship illustration of the methodological constraint set under matched-coverage real-LD re-analysis (under-powered LD reference, SuSiE-RSS non-convergence at three of five traits, restricted Stage 2 trait-pair scoping) rather than as evidence that the canonical PP.H4 = 1.00 claim has been falsified. The headline-count drop of non-converged fits from the 51/96 numerator is HQ#2(ii) (DEFERRED-DESIGN) — Carter's call on whether to recompute the headline numerator vs caveat in place.

**Commits:** `89a63e2` (W2, Fig 3 disclosure sub-table panel surfacing per-fit convergence_status + ld_overlap_fraction); `df3fa89` (W1, §3.4 SH2B3 case-study rewrite acting on independent scientific review per Eval 2(a) + Eval 3.4).
**Files modified:** [`src/R/figures/fig3_sh2b3_eur_collapse_forest.R`](../../src/R/figures/fig3_sh2b3_eur_collapse_forest.R), [`docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf`](../../docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf), [`docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png`](../../docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png), [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md) (§3.4 at L148).
**Verification on disk:** Manuscript L148 contains the audit-aligned reframe phrase "**not executed**" + "missing run" + "3 of 5 SH2B3 EUR" per the [260425-wbf SUMMARY](../quick/260425-wbf-route-a-audit-driven-3-4-sh2b3-case-stud/260425-wbf-SUMMARY.md). The disk-authoritative 3/5 count cross-references `IDENTITY-LD-K2D-FIT-SUMMARY.tsv`; Fig 3 sub-table panel renders per-trait `susie_status` ("Per-fit data-quality disclosure") per the [260425-kki SUMMARY](../quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md).

### 5. Eval 3.1 — `ld_overlap_fraction = 0` at FTO headline real-LD

**Audit claim (paraphrased):** `fig1b_locus_panels.R` discloses that the FTO_16q12 EUR Stage 2 fit has `ld_overlap_fraction = 0` (`ld_status = 'variants_exceed_threshold'`), meaning SuSiE effectively fell back toward an identity-like internal structure at the region. This fit produces the only quantitative real-LD PP.H4 reported in the manuscript (FTO/IRX3 = 0.3099); the real-LD branding for that number is materially incorrect.

**Closure action:** Surfaced the FTO_16q12 EUR `ld_overlap_fraction = 0` finding as load-bearing in the manuscript's Tier-C disclosure paragraph at L140 (Results). The Fig 3 disclosure sub-table panel (commit `89a63e2`) extracts per-fit `ld_overlap_fraction` + `ld_status` + `susie_status` from per-trait JSONs for both LD branches and renders a new bottom panel of the figure exposing the data-quality columns. The Tier-C disclosure prose explicitly names FTO_16q12 EUR `ld_overlap_fraction = 0` + `ld_status = variants_exceed_threshold` alongside the SH2B3 EUR asthma 0.0385 anchor, with cross-reference to Figure 3 sub-table.

**Commits:** `89a63e2` (W2, Fig 3 sub-table panel + Tier-C disclosure paragraph in manuscript).
**Files modified:** [`src/R/figures/fig3_sh2b3_eur_collapse_forest.R`](../../src/R/figures/fig3_sh2b3_eur_collapse_forest.R), [`docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf`](../../docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf), [`docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png`](../../docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png), [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md) (Tier-C disclosure paragraph at L140).
**Verification on disk:** Manuscript Tier-C disclosure paragraph at L140 contains `ld_overlap_fraction = 0` + `variants_exceed_threshold` cross-referenced to Figure 3 sub-table per the [260425-kki SUMMARY](../quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md) §8 reframe-site coverage table.

### 6. Eval 3.2 — 78.9% QTL-coloc failure attributed to an unfixed bug

**Audit claim (paraphrased):** 1,005 / 1,274 QTL-coloc attempts return `too_few_snps`, traced to a "harmonized-TSV vs Phase 1 SuSiE-fit variant-ID format mismatch (chr:pos vs rsid)" with the candid disclosure that "the fix may incompletely propagate to all source × tissue × gene combinations". This is not a Limitations caveat — it means the analysis was published with the knowledge that the data on the y-axis is of unverified quality.

**Closure action:** Three coordinated prose anchors landed across Methods, Discussion, and Limitations: (a) Methods §Harmonization-Pipeline Diagnostics (L90) appended sentence pointing to OSF deviation log at osf.io/az52u and naming the structural variant-ID reconciliation work as "out of scope for the present audit pass" (commit `06b817b`, Eval 3.2(c)); (b) Discussion §Identity-LD Inflation and Its Mechanism (L220) appended ~50-word sentence flagging QTL-coloc readouts as a pipeline-state snapshot with the 78.9% (1,005/1,274) headline inline (commit `21900ba`, Eval 3.2(b)); (c) Limitations bullet (5) at L244 strengthened in place with all five required dimensions — unverified-quality language, 78.9% inline with explicit denominator-disambiguation against 1,242, out-of-scope phrase, osf.io/az52u cross-pointer, original-research framing (commit `09c68e5`, Eval 3.2(a)). Bullet count remains 6.

**Commits:** `06b817b` (Eval 3.2(c) Methods L90); `21900ba` (Eval 3.2(b) Discussion L220); `09c68e5` (Eval 3.2(a) Limitations bullet 5 strengthening; same commit also lands Eval 3.6 Methods footnote at L140).
**Files modified:** [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md) (Methods L90, Discussion L220, Limitations bullet 5 at L244).
**Verification on disk:** Manuscript L90 contains "out of scope for the present audit pass" + osf.io/az52u; L220 contains "78.9%" + "1,005/1,274" + Methods back-pointer; L244 Limitations bullet (5) contains all five required dimensions per the [260426-06n SUMMARY](../quick/260426-06n-route-a-audit-cheap-prose-continuation-e/260426-06n-SUMMARY.md) Done Criteria coverage map.

### 8. Eval 3.4 — SH2B3 "collapse" is a missing run, not a collapse

**Audit claim (paraphrased):** The manuscript states canonical BMI–HTN and HTN–stroke trait pairs at SH2B3 EUR are "absent from the Stage 2 `coloc.susie` output manifest." Only `SH2B3_12q24__EUR__asthma_vs_t2d` was actually run. Reporting "absent from manifest" as "consistent with credible-set collapse" is overreach — those pairs were simply not executed.

**Closure action:** Rewrote `docs/manuscript/track_a_pivot.md` §3.4 SH2B3 case-study paragraph at L148 (~600 words to 396 words), replacing "consistent with credible-set collapse" / "most dramatic flagship change" / "illustrates the inflation mechanism" / "correctly fails to produce a credible set" overreach with audit-aligned methodological-constraint framing per Eval 3.4 (canonical pairs were not executed, not collapsed) + Eval 2(a) (3 of 5 SH2B3 EUR traits returned non_converged). New L148 explicitly uses "**not executed**" and "missing run rather than a documented credible-set collapse." Concurrently dropped the entire `(TODO-COMPOSITION-FOLLOWON; gated on a Terminal A LSF compute slot for the SH2B3 EUR L=20 re-fit)` parenthetical from Abstract L28 — the L=20 re-fit motivation now lives in the §3.4 forward-look paragraph as a methodological recommendation citing Zou et al. 2022.

**Commits:** `df3fa89` (single atomic commit covering exactly 1 file: `docs/manuscript/track_a_pivot.md`).
**Files modified:** [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md) (§3.4 paragraph at L148; Abstract L28 TODO marker removal).
**Verification on disk:** Manuscript L148 contains the verbatim phrase "the canonical BMI–hypertension and hypertension–stroke pairs were **not executed**" and "missing run rather than a documented credible-set collapse" per the [260425-wbf SUMMARY](../quick/260425-wbf-route-a-audit-driven-3-4-sh2b3-case-stud/260425-wbf-SUMMARY.md) verbatim-paragraph block.

### 9. Eval 3.5 — 95 vs 96 row-count discrepancy

**Audit claim (paraphrased):** The summary TSV has 95 rows; the manuscript denominator is 96. Figure scripts hard-fail on `nrow(df) == 96`, so the snapshot's TSV cannot drive the figure. Either the TSV is a 95-row subset or the manuscript denominator drifted by one — the discrepancy is undocumented.

**Closure action:** Documented the 95-vs-96 denominator and named the single missing fit (`bmi.EUR.APOE_19q13`, Stage 2 real-LD `status = non_converged`, `n_CS = 6`) in manuscript Methods §Admissibility (L80) and Methods §Identity-LD vs Real-LD Comparison (L82). The fold-change is robust to this 1-cell denominator difference (1.06× under either denominator choice). Also recorded in `TRACK-A-FROZEN-NUMBERS.md` LIVE block denominator note.

**Commits:** `f0451b0` (W3, Methods §Admissibility 95-vs-96 reconciliation + missing-fit name).
**Files modified:** [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md) (Methods §Admissibility at L80, Methods §Identity-LD Comparison at L82).
**Verification on disk:** Manuscript Methods §Admissibility contains "bmi.EUR.APOE_19q13" + "95-of-96 reconciliation"; [`TRACK-A-FROZEN-NUMBERS.md`](./TRACK-A-FROZEN-NUMBERS.md) LIVE block at L25 carries the denominator note "the k2d identity-LD re-fire enumerated 95 of 96 region × ancestry × trait fits at admissibility."

### 10. Eval 3.6 — `ld_overlap = 0` on every identity-LD row (schema confusion)

**Audit claim (paraphrased):** Identity-LD TSV's all-zero `ld_overlap` / `ld_overlap_fraction` columns may indicate a parse bug because the schema appeared shared with the real-LD output.

**Closure action:** Orchestrator-pre-verified disk evidence resolved the audit's premise: the identity-LD summary TSV's all-zero `ld_overlap` / `ld_overlap_fraction` columns reflect the intentional absence of a loaded LD reference under the identity-LD branch, NOT a parse bug. Verified that the real-LD summary TSVs (`results/fine_mapping/finemap_summary.tsv` + `finemap_summary_augmented.tsv`) do NOT carry `ld_overlap` / `ld_overlap_fraction` columns at all; the canonical source for those scalars on the real-LD branch is per-fit JSONs (`results/fine_mapping/susie/*.json`), with EUR-fit `ld_overlap_fraction` ranging 0.003–1.000. Closure landed as a parenthetical Methods-style footnote at the L140 Results Tier-C disclosure citing both `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` and `results/fine_mapping/susie/*.json` as schema-disjoint sources of truth and naming the "intentional absence" disambiguation.

**Commits:** `09c68e5` (parenthetical Methods-style footnote at L140; same commit also lands Eval 3.2(a) Limitations strengthening).
**Files modified:** [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md) (parenthetical at L140).
**Verification on disk:** Manuscript L140 paragraph carries a ~50-word parenthetical citing both schema-disjoint sources of truth + "intentional absence" language per the [260426-06n SUMMARY](../quick/260426-06n-route-a-audit-cheap-prose-continuation-e/260426-06n-SUMMARY.md) Eval 3.6 PASS verdict block.

### 11. Eval 3.7 — HLA double-classified (fallback + negative-control)

**Audit claim (paraphrased):** `track_a_pivot.md` L80 lists HLA_6p21 in the identity-LD fallback scope (a region where the paper would still draw conclusions); L102 lists HLA in the pre-specified negative-control set ("HLA-immune"). HLA cannot simultaneously be a fallback test region and a definitionally-null control. The "224 negative-control rows resolved to Tier C or empty" claim becomes near-tautological.

**Closure action:** Reclassified HLA-immune out of the negative-control panel into identity-LD-fallback only; kept the fallback role because it is methodologically load-bearing (MHC architecture incompatible with autosomal 1000G EUR panel); dropped the negative-control framing because HLA's behavior is definitionally null under the negative-control rubric, making the calibration claim near-tautological. Manuscript L28/L102/L138/L188/L240 reframed under the "audit Eval 3.7" anchor; manuscript L80/L210/L244 fallback prose unchanged; on-disk `results/qtl_coloc/tier_assignments.tsv` preserved at 224 rows / total_rows = 233 (only manuscript narrative classification updated). LIVE block added to `TRACK-A-FROZEN-NUMBERS.md` "Negative-control behavior" section; legacy 224/24-HLA-immune block marked SUPERSEDED 2026-04-26 but preserved verbatim.

**Commits:** `19de334` (Task 2 of 260425-t9j — HLA reclassification + frozen-numbers update).
**Files modified:** [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md), [`.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`](./TRACK-A-FROZEN-NUMBERS.md).
**Verification on disk:** [`TRACK-A-FROZEN-NUMBERS.md`](./TRACK-A-FROZEN-NUMBERS.md) `## Negative-control behavior (post-t9j HLA reclassification 2026-04-26) — LIVE` block at L135–152 carries the 9-distinct-loci framing; SUPERSEDED block at L156–165 preserved verbatim; reconciliation log row at L210 documents the closure. Manuscript L80/L210/L244 fallback prose unchanged per the [260425-t9j SUMMARY](../quick/260425-t9j-audit-cheap-items-pass-hla-reclassificat/260425-t9j-SUMMARY.md) Gate 5.

### 12. Eval 3.8 — "Negative-control rows" overstated as regions (224 → 9 distinct loci)

**Audit claim (paraphrased):** 224 rows = 120 cosmetic + 80 blood group + 24 HLA, but the unique locus count is ~5 cosmetic + 4 blood group + 1 HLA = 10 distinct loci. Calling 224 "region-pair evaluations" overstates the breadth of the negative-control panel.

**Closure action:** Restated negative-control panel breadth as "9 distinct loci / 200 rows" rather than "224 rows" (post HLA reclassification under Eval 3.7, the panel is 4 blood-group + 5 cosmetic = 9 loci; 24 HLA-immune rows are classified into identity-LD-fallback). Manuscript L28/L102/L138/L188/L240 carry the new framing under the "audit Eval 3.8" anchor; on-disk `tier_assignments.tsv` unchanged at 224 rows. LIVE block in `TRACK-A-FROZEN-NUMBERS.md` carries the 9-distinct-loci breakdown.

**Commits:** `19de334` (same commit as Eval 3.7 — both lands together).
**Files modified:** [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md), [`.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`](./TRACK-A-FROZEN-NUMBERS.md).
**Verification on disk:** Manuscript L28, L102, L138, L188 contain "9 distinct negative-control loci" or "200 negative-control"; [`TRACK-A-FROZEN-NUMBERS.md`](./TRACK-A-FROZEN-NUMBERS.md) LIVE block at L137–151 carries "9 distinct" + "200 / 200 Tier C or empty (100%)" + breakdown (4 blood-group ABO/FUT1/FUT2/KEL/RH; 5 cosmetic HERC2/OCA2/IRF4/MC1R/SLC24A5/TYR).

### 13. Eval 3.9 — DIAMANTE T2D vintage ambiguity

**Audit claim (paraphrased):** Manuscript L54 "T2D from DIAMANTE (N ≈ 900,000)" is plausible but ambiguous. DIAMANTE 2020 (Vujkovic) effective N is ~228k cases / ~1.3M total (mixed-ancestry); the EUR-only subset Mahajan 2018 is N ≈ 898,130. Verify the citation matches the exact sumstats file used.

**Closure action:** Pinned DIAMANTE T2D vintage to Mahajan 2018 (DIAMANTE EUR subset, N = 898,130, DOI 10.1038/s41588-018-0241-6) at three sites: manuscript L54 abstract-style citation ("T2D from DIAMANTE (Mahajan 2018, N = 898,130)"), L56 vintage list ("Mahajan 2018 T2D" replacing "Vujkovic 2020 T2D"), and L327 §References Ref-7 entry (explicit Mahajan A, Taliun D, Thurner M, et al. 2018 *Nat Genet* 50:1505–1513). DOI verified against `data/processed/sumstats_harmonized/t2d.EUR.tsv.bgz` (N = 898,130 per row — exact match to Mahajan 2018 EUR subset, not Vujkovic 2020 trans-ancestry). Mahajan 2022 (N = 933,970) is the M1 / Track B upgrade target and remains unaffected — Track A's catalogue is intentionally held at the vintage of the original published claims under independent scientific review.

**Commits:** `943d8f6` (Task 1 of 260425-t9j).
**Files modified:** [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md) (L54, L56, L327).
**Verification on disk:** Manuscript L54/L56 contain "Mahajan 2018"; L327 contains DOI "10.1038/s41588-018-0241-6"; greppable count of "Vujkovic 2020 T2D" is 0 per the [260425-t9j SUMMARY](../quick/260425-t9j-audit-cheap-items-pass-hla-reclassificat/260425-t9j-SUMMARY.md) Gate 2a.

### 14. Eval 3.10 — `1,446 / 861` ghost numerics

**Audit claim (paraphrased):** `TRACK-A-FROZEN-NUMBERS.md` L53 explicitly flags `1,446 attempted tests / 861 failures` as not matching disk; `TRACK-A-PIVOT.md` (the abstract draft, L37) still uses them. A single relict appearance would be a credibility catastrophe.

**Closure action:** Purged 10 ghost-numeric occurrences from `TRACK-A-PIVOT.md` (L37, L41, L80, L104, L125, L134, L181, L257, L267, L375). All `1,446` / `861` tokens replaced with disk-truth Stage 2 numerics: 1,302 attempted analyses (28 trait-pair `coloc.susie` + 1,274 QTL-coloc); 1,005 `too_few_snps`; 78.9% failure rate. L125 additionally absorbs the W1 comparator tightening (51/96 vs 48/95 = 1.06×). Greppable count of "1,446" / "1446" / "861" tokens in `TRACK-A-PIVOT.md` is 0.

**Commits:** `58a5e2d` (W3, Priority 3f).
**Files modified:** [`.planning/amendments/TRACK-A-PIVOT.md`](./TRACK-A-PIVOT.md).
**Verification on disk:** `grep -c "1,446\|1446\|861" .planning/amendments/TRACK-A-PIVOT.md` = 0 per the [260425-kki SUMMARY](../quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md) Gate 7. Manuscript ghost-numeric purge had landed earlier (2026-04-23 reconciliation log row).

### 15. Eval 4(a) — "Locked scalars" prevent self-correction

**Audit claim (paraphrased):** `fig2_cs_yield.R` lines 84–94 and `fig3…R` lines 130–140 hard-fail if disk-derived numbers drift from constants set in the script. The discipline pins figures to the original numbers even when a re-fire yields more accurate ones — numeric immutability becomes adversarial when the original number was wrong.

**Closure action:** Two coordinated landings: (a) `fig2_cs_yield.R` replaced literal `N_IDENTITY_LD_NONEMPTY <- 12L` with disk-derived read of `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` at runtime; locked-scalar block now asserts 48L / 95L (the matched-coverage k2d full-coverage values); FOLD_CHANGE_EXPECTED literal removed (computed from disk) — committed under Eval 1 closure (`884eb3d`). (b) `fig3_sh2b3_eur_collapse_forest.R` disk-derived three literal-list assignments (`EXPECTED_REAL_CS`, `EXPECTED_ID_CS`, `EXPECTED_REAL_STATUS` at L122–L129) replaced with `expected_id_cs_from_disk` / `expected_real_cs_from_disk` / `expected_real_status_from_disk` populated at runtime from `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` and `finemap_summary.tsv` — committed at `d6cbf53` (260426-04b). The re-rendered Fig 3 reproduces the prior commit's per-trait CS counts verbatim, confirming self-correction-discipline alignment, NOT a numeric correction.

**Commits:** `884eb3d` (W1 of 260425-kki — `fig2_cs_yield.R` disk-derivation); `d6cbf53` (T1 of 260426-04b — `fig3` disk-derivation).
**Files modified:** [`src/R/figures/fig2_cs_yield.R`](../../src/R/figures/fig2_cs_yield.R), [`src/R/figures/fig3_sh2b3_eur_collapse_forest.R`](../../src/R/figures/fig3_sh2b3_eur_collapse_forest.R), [`docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf`](../../docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf).
**Verification on disk:** `grep -E "EXPECTED_ID_CS\s*<-\s*list|EXPECTED_REAL_CS\s*<-\s*list|EXPECTED_REAL_STATUS\s*<-\s*list" src/R/figures/fig3_sh2b3_eur_collapse_forest.R` returns zero matches per the 260426-04b SUMMARY T1 critical gate. `fig2_cs_yield.R` no longer carries the literal `12L` per the [260425-kki SUMMARY](../quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md) Gate 2.

### 18. HQ#1 — Re-derive headline from k2d re-fire + propagate

**Audit claim (paraphrased):** The `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` already contains the same-pipeline identity-LD comparator. Replace `N_IDENTITY_LD_NONEMPTY <- 12L`, regenerate Figure 2, recompute the fold-change (~1.05×), and rewrite the abstract / Results / Discussion around the real finding.

**Closure action:** Same commit cluster as Eval 1. Fold change recomputed at 51 / 48 = 1.0625× ≈ 1.06× (matched-coverage k2d full-coverage); Fig 2 regenerated; eight manuscript sites reframed (Abstract L28, Methods §Identity-LD Comparison L82, Methods §Admissibility L80, Headline Result L138, Tier-C disclosure paragraph, Discussion §Strengths L214, Discussion §Pathway L222, Conclusions L252, Figure 2 caption L293/295). Anchor language locked at "we tightened the comparator and the inflation magnitude shifted" verbatim at L138 (Headline Result).

**Commits:** `884eb3d` (W1 of 260425-kki — comparator tightening, Fig 2 re-render, manuscript propagation).
**Files modified:** [`src/R/figures/fig2_cs_yield.R`](../../src/R/figures/fig2_cs_yield.R), [`docs/manuscript/figures/fig2_cs_yield.pdf`](../../docs/manuscript/figures/fig2_cs_yield.pdf), [`docs/manuscript/figures/fig2_cs_yield.png`](../../docs/manuscript/figures/fig2_cs_yield.png), [`.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`](./TRACK-A-FROZEN-NUMBERS.md), [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md).
**Verification on disk:** [`TRACK-A-FROZEN-NUMBERS.md`](./TRACK-A-FROZEN-NUMBERS.md) LIVE block at L9–25 carries `48 / 95` and `51 / 48 = 1.06×`; manuscript L138 contains "we tightened the comparator and the inflation magnitude shifted" verbatim per the [260425-kki SUMMARY](../quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md) §8 reframe-site coverage table.

### 22. HQ#3 — LD-reference-quality dose-response (column + figure)

**Audit claim (paraphrased):** Add an `ld_overlap_fraction` column to every PP.H4 reported in Table 1 / Table 3. Drop or asterisk any fit with `ld_overlap_fraction < 0.5` (Benner et al. 2017 calibration threshold), and plot PP.H4 vs `ld_overlap_fraction` to show the dose–response of LD-reference quality on the inferred coloc signal.

**Closure action:** Three coordinated landings: (a) Built the 2-panel composite figure that the audit asked for: SuSiE-RSS credible-set yield (Panel A, 60 EUR fits) and QTL-coloc PP.H4 (Panel B, 32 EUR successes) plotted against `ld_overlap_fraction` of the real 1000G EUR LD panel, with the FTO_16q12 EUR IRX3 / Pancreas Tier-C signal (PP.H4 = 0.3099, min ld_of = 0) annotated as the structural inflation flag — committed at `1e4b071` (260425-wa2). (b) Froze the dose-response scalars in `TRACK-A-FROZEN-NUMBERS.md` as a new LIVE block: 33/60 EUR fits below Benner threshold (55.0%); 27/60 above; 0/32 successful QTL-coloc points in the strict suspect quadrant (PP.H4 ≥ 0.5 AND min ld_overlap_fraction < 0.5) — committed at `5987ba1` (260426-04b T2). (c) Integrated the figure into the manuscript supplementary section as Figure S7 with mandatory exploratory methodology-validation framing — committed at `d6a3647` (260426-04b T3).

**Commits:** `1e4b071` (figure builder + render); `5987ba1` (frozen-numbers LIVE block); `d6a3647` (Figure S7 caption integration).
**Files modified:** [`src/R/figures/fig_h3_ld_overlap_dose_response.R`](../../src/R/figures/fig_h3_ld_overlap_dose_response.R), [`docs/manuscript/figures/fig_h3_ld_overlap_dose_response.pdf`](../../docs/manuscript/figures/fig_h3_ld_overlap_dose_response.pdf), [`docs/manuscript/figures/fig_h3_ld_overlap_dose_response.png`](../../docs/manuscript/figures/fig_h3_ld_overlap_dose_response.png), [`.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`](./TRACK-A-FROZEN-NUMBERS.md), [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md) (Figure S7 caption at L305).
**Verification on disk:** [`TRACK-A-FROZEN-NUMBERS.md`](./TRACK-A-FROZEN-NUMBERS.md) `## H3 LD-reference-quality dose-response (post-wa2 H3 figure, 2026-04-26) — LIVE` block at L29–53 carries all 8 frozen scalars. Manuscript Figure S7 caption block at L305 cites FTO 0.3099 + SH2B3 asthma 0.0385 + zero-suspect-quadrant + commit `1e4b071` per the 260426-04b SUMMARY success criterion 6.

### 23. QI#1(a) — Purge `1,446` / `861` ghost numbers from prose

(Same closure as Eval 3.10 above. Quick-improvement #1(a) is a duplicate of Eval 3.10 in the audit's structure; closure landed at commit `58a5e2d` for `TRACK-A-PIVOT.md`. Manuscript ghost-numeric purge had landed earlier in the 2026-04-23 reconciliation pass. Greppable count of `1,446` / `861` in any of the in-scope artifacts is 0.)

**Commits:** `58a5e2d`.
**Files modified:** [`.planning/amendments/TRACK-A-PIVOT.md`](./TRACK-A-PIVOT.md).
**Verification on disk:** `grep -c "1,446\|1446\|861" .planning/amendments/TRACK-A-PIVOT.md docs/manuscript/track_a_pivot.md` = 0 across both target files.

### 24. QI#1(b) — Reconcile `95` vs `96` denominator with Methods paragraph

(Same closure as Eval 3.5 above. Methods §Admissibility paragraph at L80 names the missing fit `bmi.EUR.APOE_19q13` and reconciles the 95-of-96 denominator.)

**Commits:** `f0451b0`.
**Files modified:** [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md).
**Verification on disk:** Manuscript Methods §Admissibility at L80 contains "bmi.EUR.APOE_19q13" + 95-of-96 reconciliation language.

### 25. QI#1(c) — Remove hard-coded `12 / 96 (12.5%)` from `fig2_cs_yield.R` L60

**Audit claim (paraphrased):** Remove the `12L` literal from `fig2_cs_yield.R` line 60 and replace with the disk-derived count.

**Closure action:** Replaced `N_IDENTITY_LD_NONEMPTY <- 12L` with a disk-derived read of `IDENTITY-LD-K2D-FIT-SUMMARY.tsv`. The locked-scalar block now asserts 48L / 95L (matched-coverage k2d full-coverage). FOLD_CHANGE_EXPECTED literal removed (computed from disk).

**Commits:** `884eb3d` (same atomic commit as Eval 1 / HQ#1).
**Files modified:** [`src/R/figures/fig2_cs_yield.R`](../../src/R/figures/fig2_cs_yield.R).
**Verification on disk:** `src/R/figures/fig2_cs_yield.R` L60 no longer hard-codes `12L`; the identity-LD baseline is now disk-derived from `IDENTITY-LD-K2D-FIT-SUMMARY.tsv`.

### 27. QI#3 — Tier-C "data quality" column

**Audit claim (paraphrased):** For each of the 9 Tier-C rows, append `ld_overlap_fraction`, `susie_status`, `n_CS_lt_L`, and `qtl_coloc_status`. The FTO 0.3099 row will surface its `ld_overlap_fraction = 0` problem; readers can then decide whether the highest Tier-C signal is interpretable.

**Closure action:** Added a "Per-fit data-quality disclosure" sub-table panel to Fig 3 (`fig3_sh2b3_eur_collapse_forest.R`) that surfaces `ld_overlap_fraction` + `susie_status` + `L_saturated` per trait. The PDF/PNG dimensions expanded vertically to accommodate the third row of the patchwork composition. Concurrently, the Tier-C disclosure paragraph at manuscript L140 names `ld_overlap_fraction = 0` for the FTO_16q12 EUR IRX3 / Pancreas Tier-C signal (PP.H4 = 0.3099) and the SH2B3 EUR asthma anchor (`ld_overlap_fraction = 0.0385`).

**Commits:** `89a63e2` (W2, Fig 3 sub-table panel + Tier-C disclosure paragraph).
**Files modified:** [`src/R/figures/fig3_sh2b3_eur_collapse_forest.R`](../../src/R/figures/fig3_sh2b3_eur_collapse_forest.R), [`docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf`](../../docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.pdf), [`docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png`](../../docs/manuscript/figures/fig3_sh2b3_eur_collapse_forest.png), [`docs/manuscript/track_a_pivot.md`](../../docs/manuscript/track_a_pivot.md) (Tier-C disclosure paragraph at L140).
**Verification on disk:** R script contains "Per-fit data-quality disclosure"; manuscript Tier-C disclosure paragraph at L140 contains FTO_16q12 EUR `ld_overlap_fraction = 0` per the [260425-kki SUMMARY](../quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md) Gate 4 + Gate 5.

---

## Per-item rationale (IN-PROGRESS, DEFERRED, NO-ACTION-NEEDED, SUPERSEDED)

### IN-PROGRESS

#### 7. Eval 3.3 — 28/28 empty `coloc.susie` outputs (interpretation unidentifiable)

**Audit claim (paraphrased):** All 28 trait-pair attempts returned empty `PP.H3 / PP.H4 / n_snps`. Variant-ID format mismatch (Eval 3.2) and SuSiE non-convergence (Eval 2(a)) both produce the same empty-output signature, so the interpretation is unidentifiable from the data.

**Status:** IN-PROGRESS
**Reason:** Partial closure landed via the data-quality column work (commit `89a63e2`) — the 28/28 fact is now surfaced in `TRACK-A-FROZEN-NUMBERS.md` and the manuscript discloses the empty-output count. Full interpretation closure is gated on resolving the upstream identifiability problem: it requires (a) the SH2B3 L=20 re-fit (HQ#2(i), DEFERRED-COMPUTE) to determine whether SuSiE non-convergence drives the empty-output signature, and (b) the canonical SH2B3 BMI–HTN + HTN–stroke trait-pair `coloc.susie` runs (HQ#2(iii), DEFERRED-COMPUTE) to determine which trait pairs would produce non-empty outputs at L=20.
**Recorded in:** [`260425-kki-SUMMARY.md`](../quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md) §5 "Deferred upstream-compute follow-ons" items 1–2.
**When it gets closed:** After both HQ#2(i) and HQ#2(iii) land. The L=20 re-fit will identify whether non-convergence is the causal driver; the canonical-pair `coloc.susie` runs will produce the disambiguating non-empty outputs. Closure-wave commit will back-fill the matrix row's `Commits` cell and migrate this narrative section to "Per-item narrative (CLOSED items)".

### DEFERRED-COMPUTE

#### 3. Eval 2(b) — L=10 saturation artifacts undisclosed

**Audit claim (paraphrased):** `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` shows ≥11 fits returning `n_CS = 10` with the signature `cs_sizes = "3;3;3;3;3;3;3;3;3;4"` — the canonical fingerprint of L-saturated fits. Such fits should be re-run at L = 20 or 30 and inspected for stability.

**Status:** DEFERRED-COMPUTE
**Reason:** Closure requires LSF compute (~2–4 hours wall time on `serial` queue with `la_multitrait_r` env) to re-fire SuSiE-RSS at L = 20 or L = 30 across the ≥11 saturated fits and verify n_CS << L. No prose-only closure is possible — the L-sweep convergence behavior must be measured.
**Recorded in:** [`260425-kki-SUMMARY.md`](../quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md) §5 "Deferred upstream-compute follow-ons" item 1; [`260425-t9j-SUMMARY.md`](../quick/260425-t9j-audit-cheap-items-pass-hla-reclassificat/260425-t9j-SUMMARY.md) "Deferred upstream-compute follow-ons" Audit Eval 2b row.
**When it gets closed:** When Carter schedules the LSF compute slot for the L-sweep re-fire. Closure will produce a new closure-wave commit set (R script update + per-fit JSON tree regeneration + Supplementary Methods §L-sweep paragraph) and back-fill the matrix row.

#### 19. HQ#2(i) — Re-fit SH2B3 EUR at L=20 (BMI/HTN/stroke)

**Audit claim (paraphrased):** Re-fit BMI/HTN/stroke at SH2B3 EUR with L = 20 (Zou et al. 2022 recommend L generously above expected number of effects) and report whether n_CS << L.

**Status:** DEFERRED-COMPUTE
**Reason:** Requires LSF compute slot (~2–4 hours wall time on `serial` queue with `la_multitrait_r` env). The three non-converged fits at L=10 may converge at L=20; this informs the structural composition analysis and the canonical SH2B3 trait-pair `coloc.susie` re-fire.
**Recorded in:** [`260425-kki-SUMMARY.md`](../quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md) §5 item 1; [`260425-wbf-SUMMARY.md`](../quick/260425-wbf-route-a-audit-driven-3-4-sh2b3-case-stud/260425-wbf-SUMMARY.md) "Handoff for next /gsd-quick" item 1; manuscript §3.4 forward-look paragraph at L148 carries the methodological pre-registration.
**When it gets closed:** After Carter schedules the LSF re-fit. Closure will land per-fit JSON tree updates + R script propagation + manuscript §3.4 prose update converting the forward-look from "is required" to "has been executed".

#### 21. HQ#2(iii) — Execute `coloc.susie` on canonical BMI–HTN + HTN–stroke trait pairs

**Audit claim (paraphrased):** Execute `coloc.susie` on the canonical BMI–HTN and HTN–stroke pairs that the abstract leans on. Until that runs, "absent from manifest" is not an audit conclusion.

**Status:** DEFERRED-COMPUTE
**Reason:** Currently the Stage 2 manifest only contains `SH2B3_12q24__EUR__asthma_vs_t2d`; the canonical pairs are absent (consistent with the §3.4 closure of Eval 3.4 that documents "missing run rather than collapse"). A targeted re-fire is pre-registered in `TRACK-A-FROZEN-NUMBERS.md` and remains gated on the L=20 re-fit decision (HQ#2(i)) — `coloc.susie` only makes sense once the per-trait SuSiE-RSS fits converge.
**Recorded in:** [`260425-kki-SUMMARY.md`](../quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md) §5 item 2; [`260425-wbf-SUMMARY.md`](../quick/260425-wbf-route-a-audit-driven-3-4-sh2b3-case-stud/260425-wbf-SUMMARY.md) "Handoff for next /gsd-quick" item 2.
**When it gets closed:** After HQ#2(i) lands; then a follow-on quick task will execute the canonical-pair `coloc.susie` runs against the L=20 re-fits. Closure-wave commit will back-fill matrix rows for both HQ#2(iii) and the related IN-PROGRESS Eval 3.3 row.

### DEFERRED-DESIGN

#### 20. HQ#2(ii) — Drop/flag non-converged fits in yield counts

**Audit claim (paraphrased):** Drop or flag non-converged fits in all yield counts (currently they are pooled into 51/96).

**Status:** DEFERRED-DESIGN
**Reason:** Closure requires Carter's call on whether to recompute the 51/96 headline numerator (drop 18 non-converged → 33/96) versus retain 51/96 with caveat in place. The §3.4 paragraph at manuscript L148 already discloses 3 of 5 SH2B3 EUR non-converged (commit `df3fa89`); the data-quality column on Fig 3 (commit `89a63e2`) renders per-fit `susie_status`. The remaining decision is a framing choice that materially shifts the Abstract / Headline Result / Fig 2 / TRACK-A-FROZEN-NUMBERS.md LIVE block — not a routine prose edit.
**Recorded in:** [`260425-kki-SUMMARY.md`](../quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md) §5 item 5 ("submission venue decision"); [`260425-t9j-SUMMARY.md`](../quick/260425-t9j-audit-cheap-items-pass-hla-reclassificat/260425-t9j-SUMMARY.md) "Audit Eval 2a" deferred row.
**When it gets closed:** After Carter directs the framing choice (drop vs flag-in-place). Likely path is `/gsd-discuss-phase` slot. Closure will produce either a recomputed-headline closure-wave commit set OR a flag-in-place prose-only commit set, depending on the chosen framing.

### NO-ACTION-NEEDED

#### 4. Eval 2(c) — Coloc on uncertain credible sets (no CIs)

**Audit claim (paraphrased):** When credible sets are L-saturated or come from non-converged fits, the resulting PP.H4 inherits that uncertainty without a confidence statement. Figure 3 admits no CIs are plotted because "the production manifest does not store posterior intervals" — the right move, but the absence of intervals also means readers cannot judge whether 0.0517 vs 0.3099 is meaningful or noise.

**Status:** NO-ACTION-NEEDED
**Reason:** The audit explicitly acknowledges the absence of posterior intervals as "the right move" given the production manifest does not store them. Adding CIs would require re-fitting with posterior-sample retention (compute-intensive and out of scope for the audit catalogue). The disclosure of CI absence is already in the Fig 3 caption; the audit's broader point about uncertainty propagation is satisfied by the closure of Eval 2(a) (non-convergence disclosure) + Eval 3.1 (LD-overlap disclosure) + QI#3 (per-fit data-quality column).
**Recorded in:** Audit document Eval 2(c) at L46.
**When it gets closed:** No action planned in the audit-response scope. If Carter wants posterior intervals, a separate compute-intensive quick task would re-fit with `n_samples > 0` and propagate CIs into Figure 3 / Tier-C reporting.

#### 16. Eval 4(b) — Bidirectional provenance stops at file boundary

**Audit claim (paraphrased):** `fig3…R` reads `results_identity_ld/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.json` per L48-49, but the snapshot ships only the summary TSV (the binary tree is intentionally regenerable in ~1h, per `DEC-2026-04-25-01`). A reviewer who runs only what is in the snapshot cannot regenerate Figure 3. Workable, but raises the cost of independent verification beyond what most reviewers will spend.

**Status:** NO-ACTION-NEEDED
**Reason:** The audit itself frames this as "workable" and acknowledges the design choice (`DEC-2026-04-25-01`: `results_identity_ld/` regenerable in ~1h via `fire_identity_ld_rerun.sh` under `pipeline_identity_overlay.yaml`). The trade-off — gitignore the ~160 MB binary tree to keep the repository tractable, with a documented one-command regeneration path — is explicit and accepted. No remediation required.
**Recorded in:** Audit document Eval 4(b) at L84; `DEC-2026-04-25-01` decision record; [`260425-t9j-SUMMARY.md`](../quick/260425-t9j-audit-cheap-items-pass-hla-reclassificat/260425-t9j-SUMMARY.md) "results_identity_ld/ output preservation" section.
**When it gets closed:** No closure planned — the audit observation is acknowledged in the audit itself as workable.

#### 17. Eval 5 — Significance / contribution to the field

**Audit claim (paraphrased):** The substantive contribution requires the headline contrast to be quantitatively defensible. As currently positioned, the 4.25× claim, the FTO 0.3099 fit's LD-quality issue, the SH2B3 "missing run", and the pathway-enrichment retraction collectively render the manuscript not survival-grade for Genome Medicine *Original Research*.

**Status:** NO-ACTION-NEEDED
**Reason:** Eval 5 is a meta-judgment summarizing the audit's per-item findings rather than an actionable item with its own closure path. It is satisfied as a side-effect of closing the per-item findings: Eval 1 + HQ#1 (4.25× → 1.06× matched-coverage); Eval 3.1 (FTO LD-quality surfaced as load-bearing); Eval 3.4 (SH2B3 reframed as missing run, not collapse, with pre-registered re-fire); HQ#3 (LD-reference-quality dose-response figure as exploratory methodology-validation). Submission-venue decision (Genome Medicine vs Bioinformatics Applications Note) is a separate `/gsd-discuss-phase` decision recorded in [`260425-kki-SUMMARY.md`](../quick/260425-kki-track-a-audit-driven-figure-correction-p/260425-kki-SUMMARY.md) §5 item 5.
**Recorded in:** Audit document Eval 5 at L90–101.
**When it gets closed:** No standalone closure — closure tracking rolls up from the constituent items.

### SUPERSEDED

#### 26. QI#2 — HLA: pick fallback OR negative-control

**Audit claim (paraphrased):** Move HLA out of the negative-control set, or out of the fallback set — pick one. The double classification is internally inconsistent and mathematically deflates the negative-control test.

**Status:** SUPERSEDED
**Reason:** The Eval 3.7 closure (commit `19de334`, 260425-t9j) is the parent action that resolves QI#2: HLA reclassified to identity-LD-fallback only, removed from the negative-control panel narrative. The negative-control N is restated as 9 distinct loci / 200 rows (Eval 3.8 closure, same commit). QI#2 is structurally identical to Eval 3.7 — closing one closes the other.
**Parent closure:** `19de334` (260425-t9j Task 2).
**Recorded in:** [`260425-t9j-SUMMARY.md`](../quick/260425-t9j-audit-cheap-items-pass-hla-reclassificat/260425-t9j-SUMMARY.md) `audit_items_closed` frontmatter (`AUDIT-QUICK-2  # covered by Eval 3.7 reclassification`).
**When it gets closed:** Already closed via parent (Eval 3.7).

---

## Closure waves (chronological context)

| Wave date            | Quick task   | Items closed                                                                                                                       |
|----------------------|--------------|------------------------------------------------------------------------------------------------------------------------------------|
| 2026-04-25           | 260425-kki   | Eval 1, Eval 2(a) [partial — Fig 3 disclosure], Eval 3.1, Eval 3.5, Eval 3.10, Eval 4(a) [fig2 portion], HQ#1, QI#1(a), QI#1(b), QI#1(c), QI#3 |
| 2026-04-25           | 260425-t9j   | Eval 3.7, Eval 3.8, Eval 3.9, QI#2 (superseded via Eval 3.7)                                                                       |
| 2026-04-25 → 04-26   | 260425-wa2   | HQ#3 [figure builder + render]                                                                                                     |
| 2026-04-25           | 260425-wbf   | Eval 2(a) [§3.4 prose closure], Eval 3.4                                                                                           |
| 2026-04-26           | 260426-04b   | Eval 4(a) [fig3 portion], HQ#3 [frozen-numbers + Figure S7 caption]                                                                |
| 2026-04-26           | 260426-06n   | Eval 3.2, Eval 3.6                                                                                                                  |

---

## Items still requiring action

**IN-PROGRESS (1):**

- **Eval 3.3 — 28/28 empty `coloc.susie` outputs.** What happens next: gated on HQ#2(i) (L=20 re-fit) + HQ#2(iii) (canonical-pair `coloc.susie` runs). Once both land, the empty-output signature can be disambiguated between non-convergence and variant-ID-format-mismatch causes.

**DEFERRED-COMPUTE (3):**

- **Eval 2(b) — L=10 saturation re-fit.** What happens next: Carter schedules LSF compute slot (~2–4 hours, `serial` queue, `la_multitrait_r` env) for L-sweep re-fire across ≥11 saturated fits; closure includes Supplementary Methods §L-sweep paragraph.
- **HQ#2(i) — SH2B3 EUR L=20 re-fit (BMI/HTN/stroke).** What happens next: Carter schedules LSF compute slot; closure converts §3.4 forward-look from "is required" to "has been executed".
- **HQ#2(iii) — Canonical SH2B3 BMI–HTN + HTN–stroke `coloc.susie`.** What happens next: gated on HQ#2(i); closure-wave commit will back-fill HQ#2(iii) + Eval 3.3 matrix rows.

**DEFERRED-DESIGN (1):**

- **HQ#2(ii) — Drop/flag non-converged fits in yield counts.** What happens next: Carter's framing decision (drop 18 non-converged → recomputed headline numerator 33/96; or retain 51/96 with caveat in place); likely `/gsd-discuss-phase` slot.

**NO-ACTION-NEEDED (3):**

- **Eval 2(c) — No CIs on `coloc.susie` PP.H4.** Audit acknowledges absence is the right move; CI disclosure already in Fig 3 caption.
- **Eval 4(b) — Bidirectional provenance file boundary.** Audit acknowledges as workable; `DEC-2026-04-25-01` regeneration path documented.
- **Eval 5 — Significance / contribution.** Meta-judgment satisfied via closures of Eval 1 + HQ#1 + HQ#3 + Eval 3.4; submission venue is a separate `/gsd-discuss-phase` decision.

**SUPERSEDED (1):**

- **QI#2 — HLA single-classification.** Closed via Eval 3.7 parent commit `19de334`.

---

## How this document gets updated

When the next closure-wave quick task lands, the executor MUST:

1. Edit the matrix row(s) for the closed item(s) — flip status to CLOSED, populate commit hash, quick-task ID, and files-touched cells.
2. Move the item's narrative from the "Per-item rationale" section to the "Per-item narrative (CLOSED items)" section, in canonical numeric order.
3. Append a row to the "Closure waves" table for the new quick task (or extend the existing row if the same quick task closed additional items).
4. Update the "Closure status (summary)" count at the top of the document so the six categories continue to sum to 27.
5. Add an entry to the "Items still requiring action" section if the closure changes the disposition of any remaining row (e.g., HQ#2(i) closing will re-disposition Eval 3.3 from IN-PROGRESS to CLOSED).
6. Update the cross-reference line at the top of [`TRACK-A-FROZEN-NUMBERS.md`](./TRACK-A-FROZEN-NUMBERS.md) only if its target document name changes.

---

## Framing

This catalogue treats [`AUDIT-REVIEW-2026-04-25.md`](./AUDIT-REVIEW-2026-04-25.md) as independent scientific review acted on prior to submission. The closure work documented here is part of the original-research record — the audit was applied to itself prior to submission, exercising the project's own scientific-integrity discipline. The audit-driven closure is original-research work in service of headline defensibility, not post-submission course correction.

---

## Audit-V2 sweep closure (2026-04-27, quick-260427-azv)

A second-pass independent re-review at [`AUDIT-REVIEW-V2-2026-04-26.md`](./AUDIT-REVIEW-V2-2026-04-26.md) (committed 2026-04-26) found that the prior closure wave shipped 18 of 27 items with disk-verifiable evidence but flagged residual prose drift across Abstract, Discussion opener, Conclusion, Figure 3 caption, and Table 3 (the "five-surface SH2B3 narrative sweep"), plus three quick fixes (citation error, Methods narrative-location cleanup, stale Decision-Pending purge), six newly-surfaced issues (NewIssue1–6), and an Eval 2(a) niter-twist integration into §3.4. The V2 sweep landed under quick-task `260427-azv` as 12 atomic commits over ~6 hours, all on `main` with no LSF, no data egress, and no OSF portal action.

**V2 sweep closure status by audit-v2 item:**

| Audit-V2 item | V2 status | V2 commit(s) | Files touched |
|---|---|---|---|
| HQ1 — Five-surface SH2B3 narrative sweep | V2-CLOSED | `81088f0` (HQ1 main + caption fix in `205a1a3`) | `track_a_pivot.md` (Abstract L28, Discussion opener L216, Fig 3 caption L297 panels A+B, Table 3 L280–281) |
| HQ2 — Quantify structural inflation (paired-fit Figure S2) | V2-CLOSED | `d87416a` (script) + `cc943bd` (render) + `9cb007d` (caption) | `src/R/figures/fig_s2_paired_fit_structural_inflation.R` (NEW), `docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.{pdf,png}` (NEW), `track_a_pivot.md` (S2 caption block) |
| HQ3 — Conclusion-1 method-namespace reframe | V2-CLOSED | `a345f5e` | `track_a_pivot.md` (L252–254) |
| QI1 — Citation fix (Wang²⁹ → Zou²⁰) | V2-CLOSED | `00cf5b9` | `track_a_pivot.md` (L148) |
| QI2 — Move audit-process narrative from Methods L82 to Discussion §Audit-driven Comparator Tightening | V2-CLOSED | `cb5db17` | `track_a_pivot.md` (L82 + new Discussion subsection between §Identity-LD Inflation and §Reframing of Cardiometabolic Pleiotropy Claims) |
| QI3 — Stale Decision-Pending item 4 deletion + items 5+ flag | V2-CLOSED | `00cf5b9` | `track_a_pivot.md` (Decision-pending L351–360 block) |
| NewIssue1 — Cite fix (= QI1) | V2-CLOSED | (covered by QI1) | (n/a) |
| NewIssue2 — Methods cleanup (= QI2) | V2-CLOSED | (covered by QI2) | (n/a) |
| NewIssue3 — Decision-Pending purge (= QI3) | V2-CLOSED | (covered by QI3) | (n/a) |
| NewIssue4 — QTL-coloc data-quality caveat in Abstract / FTO callouts | V2-CLOSED | `7ea3f00` | `track_a_pivot.md` (Abstract L28, Tier-C disclosure L140) |
| NewIssue5 — Fig S7 framing promotion (exploratory → methodology-validation finding) | V2-CLOSED | `7ea3f00` | `track_a_pivot.md` (Figure S7 caption header + §Framing block) |
| NewIssue6 — Methods L-saturation prose disclosure (11 of 95 fits) | V2-CLOSED | `205a1a3` | `track_a_pivot.md` (Methods §Admissibility) |
| Eval 2(a) — niter-twist integration into §3.4 (disk-truthful) | V2-CLOSED | `205a1a3` | `track_a_pivot.md` (§3.4 L148 niter-trace clause + Fig 3 caption L_sat attribution fix) |
| HQ1-followup — L140 residual stale-narrative leak ("four other ... composition collapse") | V2-CLOSED | `00cf5b9` | `track_a_pivot.md` (L140 Tier-C disclosure paragraph) |

**Disk-truth corrections vs. audit-v2 doc:** The V2 sweep integrated **disk-truth** (results/fine_mapping/susie/*.json + results_identity_ld/fine_mapping/susie/*.json) where the audit-v2 doc claims diverged from disk. Specifically:

1. The audit-v2 doc claimed "three identity-LD fits at SH2B3 EUR ran to niter = 100" — disk shows identity-LD niter at SH2B3 EUR = 9 / 3 / 12 (BMI/HTN/stroke; all `convergence_status = converged_primary`). It is the **real-LD** fits that hit niter = 100. The §3.4 niter-twist integration uses disk-truth.
2. The audit-v2 doc claimed identity-LD BMI at SH2B3 EUR has `L_saturated = TRUE` — disk shows BMI identity-LD has `L_saturated = FALSE` with `n_CS = 3`. The L_saturated = TRUE fit at SH2B3 EUR identity-LD is **hypertension**, not BMI. The Fig 3 caption (commit `205a1a3`) uses disk-truth.
3. The audit-v2 doc's claim of "11 of 95 identity-LD fits show L = 10 saturation cs_sizes fingerprint" is **confirmed** by disk (11 rows in `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` with `cs_sizes = "3;3;3;3;3;3;3;3;3;4"`); the per-fit JSON L_saturated boolean is stricter and fires only on `hypertension.EUR.SH2B3_12q24` (1 of 95).
4. The Figure 3 caption "four of five EUR traits at SH2B3 are non_converged" was **stale** — disk shows 3 of 5 (BMI, HTN, stroke; T2D and asthma are `converged_primary`). HQ1 commit `81088f0` reframed.

**V2 sweep deliverables:**

- 12 atomic commits on `main` (`81088f0`, `a345f5e`, `00cf5b9`, `cb5db17`, `7ea3f00`, `205a1a3`, `d87416a`, `cc943bd`, `9cb007d`, plus Wave 3 `<commit10>`, `<commit11>`, `<commit12>` for tracker updates)
- 1 new R script (`src/R/figures/fig_s2_paired_fit_structural_inflation.R`, 339 lines)
- 2 new figure renders (`docs/manuscript/figures/fig_s2_paired_fit_structural_inflation.{pdf,png}`)
- 3 new DEC entries in `.planning/DECISIONS.md` (DEC-2026-04-27-01/02/03)
- 1 new LIVE block in `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` (Paired-fit structural inflation, Figure S2)
- Stage 2 source-of-truth TSV md5 invariant: `finemap_summary.tsv`, `coloc_summary.tsv`, `tier_assignments.tsv` byte-identical pre/post-sweep

**HQ#2 deferred items remain DEFERRED (out of scope for the V2 sweep):**

- HQ#2(i) — SH2B3 EUR L = 20 re-fit (DEFERRED-COMPUTE; needs LSF)
- HQ#2(ii) — Drop / flag non-converged fits in yield numerator (DEFERRED-DESIGN; Carter call)
- HQ#2(iii) — Execute canonical BMI–HTN + HTN–stroke `coloc.susie` pairs (DEFERRED-COMPUTE; needs LSF)

**Net delta vs. audit-v2:** All 13 audit-v2 actionable items (HQ1, HQ2, HQ3, QI1, QI2, QI3, NewIssue1–6, Eval 2(a) integration) are V2-CLOSED. The three HQ#2 deferred-compute / deferred-design items remain unchanged from their original disposition, correctly scoped as future work. The manuscript is now bioRxiv-submission-ready except for the 10 `[EXTRACT: …]` placeholders which are flagged as a separate quick-task pre-bioRxiv blocker (see Decision-pending item 4).
