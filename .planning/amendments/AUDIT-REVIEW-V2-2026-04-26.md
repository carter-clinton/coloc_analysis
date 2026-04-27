# Track A Audit — Re-Review of `coloc_analysis_track_a_b3ee506_2026-04-26`

**Subject:** updated archive `coloc_analysis_track_a_b3ee506_2026-04-26.tar.gz`
**Reviewed:** 2026-04-26
**Prior review:** `AUDIT-REVIEW-2026-04-25.md` (commit `9801e77` per `TRACK-A-AUDIT-RESPONSE-2026-04-26.md`)
**Scope:** manuscript (`docs/manuscript/track_a_pivot.md`), planning artifacts (`TRACK-A-AUDIT-RESPONSE-2026-04-26.md`, `TRACK-A-FROZEN-NUMBERS.md`, `IDENTITY-LD-K2D-FIT-SUMMARY.tsv`), and rendered figures (Fig 1A, 1B, 2, 3, 5, S7).

---

## TL;DR

This is a substantial, methodologically honest revision. **18 of 27 audit items closed** with verifiable disk evidence; the load-bearing critiques (Eval 1 comparator, Eval 3.1 LD-overlap=0, Eval 3.4 SH2B3 missing-run, Eval 3.7 HLA double-class, Eval 3.10 ghost numbers) are all resolved. Figure 2 now correctly contrasts **48/95 (50.5%) vs 51/96 (53.1%) = 1.06×**, derived live from disk; Figure 3 has gained a per-fit data-quality disclosure subtable that is genuinely informative; new Figure S7 (LD-overlap dose-response) directly addresses HQ#3 and produces a striking observation: **33/60 EUR Stage-2 fits sit below the Benner et al. 2017 calibration threshold of 0.5**.

Three high-stakes issues remain. **(i)** The audit closure was structurally good but partial — Abstract, Discussion opening, Conclusion claim 1, Figure 3 caption, and Table 3 still carry the *pre-revision* "credible-set collapse / manufactures PP.H4 / four of five non-converged" narrative that §3.4 explicitly retracted. The manuscript is now internally contradictory between the Results body and the Abstract/Discussion/Conclusion/captions. **(ii)** A reference-number error: §3.4 cites "Wang et al. 2020²⁹" but ref ²⁹ is Wallace 2021. **(iii)** The Conclusion attributes the inflation to `coloc.abf` (claim 1, L254), but the actual head-to-head data presented is for `SuSiE-RSS + coloc.susie` — the audited method (`coloc.abf` under identity-LD) was never directly contrasted against `coloc.abf` under real-LD in this snapshot.

The good news: every remaining issue is a prose-level fix achievable in a single sweep before bioRxiv. The compute-deferred items (L=20 SH2B3 re-fit, canonical-pair `coloc.susie`, L-saturation re-fire) are correctly scoped as future work.

---

## Evaluation 1 — Methodological soundness (the comparator problem) — CLOSED

**Original critique:** 4.25× headline rested on a stale 12/96 from session-log scalars; same-pipeline k2d re-fire gives 48/95 ≈ 50.5%, indistinguishable from real-LD 53.1%.

**Closure quality: A.** `fig2_cs_yield.R` no longer hard-codes `12L` — verified: Fig 2 PNG now shows "48/95 (50.5%)" vs "51/96 (53.1%)" with a "1.06× yield (matched-coverage)" annotation. `TRACK-A-FROZEN-NUMBERS.md` carries a LIVE block at L9–25 with the correct 51/48 = 1.06× scalar; the legacy 12/96/4.25× block is preserved verbatim under "SUPERSEDED 2026-04-25" markup, which is the right scientific-integrity move. Manuscript L28 (Abstract), L82 (Methods), L138 (Headline Result), L216 (Discussion opener), L222 (Pathway), L252 (Conclusion), and L295 (Figure 2 caption) all carry "we tightened the comparator and the inflation magnitude shifted from 4.25× to 1.06×."

**One residual concern:** the manuscript's *interpretive frame* did not fully follow the numbers down. Calling 1.06× "modest at the count level" while still asserting (L216) that identity-LD "manufactures PP.H4 signals" is a category error — manufacturing requires the contrast, and the contrast is now small. The honest read is closer to: "at the count level, identity-LD vs real-LD CS yield is statistically indistinguishable in this curated set." The compositional claim (PIP/lead-variant rank) is plausible but **not yet measured in this snapshot** — it is still flagged as "planned supplementary follow-on" in the Abstract. Until that supplementary analysis lands, the Discussion's "manufacture" language overstates what the data show.

---

## Evaluation 2 — Statistical rigor 🟡 PARTIALLY CLOSED, NEW DISCOVERY SURFACED

**(a) Non-convergence — CLOSED with a twist.** Figure 3 now exposes per-fit `convergence_status`, `L_saturated`, and `niter` in a disclosure subtable. This is excellent. Reading the new subtable, however, surfaces a methodological discovery the manuscript hasn't yet absorbed:

| Trait | Branch | susie_status | L_saturated | niter |
|---|---|---|---|---|
| BMI | identity-LD | "converged" | **TRUE** | **100** |
| hypertension | identity-LD | "converged" | FALSE | **100** |
| stroke | identity-LD | "converged" | FALSE | **100** |
| BMI | real-LD | non_converged | FALSE | 100 |
| hypertension | real-LD | non_converged | FALSE | 100 |
| stroke | real-LD | non_converged | FALSE | 100 |

Three identity-LD fits at SH2B3 EUR ran to `niter = 100` (the iteration cap) — *that* is the published SuSiE definition of non-convergence (Wang et al. 2020, *JRSS-B* §3.2: "fitting terminates if `iter == max_iter`"). The label `susie_status = "converged"` on those identity-LD fits is the SuSiE-RSS implementation's behavior of marking iteration-cap exits as "converged"; the underlying numerical fact is that under both LD references SuSiE failed to reach the convergence criterion. Combined with `L_saturated = TRUE` for BMI under identity-LD, **the truth is closer to "at SH2B3 EUR, no SuSiE-RSS fit at L=10 reaches a stable posterior under either LD reference."** That changes the §3.4 narrative meaningfully and strengthens the paper's central methodological claim, but the manuscript hasn't yet used this disclosure.

**(b) L-saturation — DEFERRED-COMPUTE.** Correctly scoped as a future LSF compute item. The closure tracker explicitly preserves the open status (item 3, ≥11 saturated fits requiring L=20 or L=30 re-fire). No issue with the deferral — this is appropriate triage.

**(c) No CIs — NO-ACTION-NEEDED.** Acceptable disposition; the audit acknowledged the absence of posterior intervals as the right move. The closure rationale (compute-intensive `n_samples > 0` re-fit out of scope) is sound.

---

## Evaluation 3 — Data integrity 🟢 LARGELY CLOSED, residual prose drift

| # | Item | Status | Quality |
|---|------|--------|---------|
| 3.1 | FTO `ld_overlap_fraction = 0` | CLOSED | A — surfaced as load-bearing in §Tier-C disclosure paragraph at L140 |
| 3.2 | 78.9% QTL-coloc bug | CLOSED (prose) | B+ — Methods L90, Discussion L220, Limitations bullet 5 all carry the unverified-quality language and OSF deviation pointer; structural fix correctly deferred |
| 3.3 | 28/28 empty `coloc.susie` | IN-PROGRESS | Correct — gated on HQ#2(i) + HQ#2(iii) compute closure |
| 3.4 | SH2B3 "missing run" | CLOSED | A — §3.4 rewrite at L148 explicitly says "**not executed**" and "missing run rather than a documented credible-set collapse" |
| 3.5 | 95 vs 96 denominator | CLOSED | A — single missing fit named: `bmi.EUR.APOE_19q13` (real-LD non_converged, n_CS = 6). Methods §Admissibility carries the reconciliation |
| 3.6 | identity-LD `ld_overlap = 0` schema confusion | CLOSED | A — L140 parenthetical correctly identifies real-LD per-fit JSONs (`ld_overlap_fraction` = 0.003–1.000) as schema-disjoint authoritative source vs the all-zero identity-LD column |
| 3.7 | HLA double-class | CLOSED | A — HLA reframed to identity-LD-fallback only, removed from negative-control panel |
| 3.8 | "224 negative-control rows" → 9 distinct loci | CLOSED | A — restated as 9 loci / 200 rows (4 blood-group + 5 cosmetic) |
| 3.9 | DIAMANTE T2D vintage | CLOSED | A — pinned to Mahajan 2018, N=898,130, DOI 10.1038/s41588-018-0241-6 |
| 3.10 | 1,446 / 861 ghost numerics | CLOSED | A — `grep -c "1,446\|1446\|861" .planning/amendments/TRACK-A-PIVOT.md` returns 0 |

**New issue surfaced by the closure work — ABSTRACT/DISCUSSION/CAPTION DRIFT.** The Results §3.4 closure landed correctly, but four downstream surfaces still carry the *pre-closure* narrative:

1. **Abstract L28:** "the canonical BMI–hypertension and hypertension–stroke trait-pairs at SH2B3 EUR were not present in the Stage 2 `coloc.susie` output, **consistent with credible-set collapse precluding the pairwise test**." — directly contradicts the L148 §3.4 retraction.
2. **Discussion opener L216:** "are absent from the Stage 2 real-LD `coloc.susie` output manifest — **consistent with credible-set collapse on at least one partner trait under real-LD, and inconsistent with the published high-confidence pleiotropy claim**." — contradicts L148.
3. **Conclusion claim 1 L254:** "trait-pairs that reached PP.H4 = 1.00 under identity-LD ... are absent from the Stage 2 real-LD `coloc.susie` output manifest — **consistent with credible-set composition collapse rather than count collapse on at least one partner trait under real-LD**." — softer than the Abstract but still asserts collapse, not "not executed."
4. **Figure 3 caption L297:** "**four of five** EUR traits at SH2B3 are non_converged under real-LD" — but the §3.4 paragraph now says "**three of five**" (BMI, hypertension, stroke). The figure-3 PNG itself shows **3 of 5** (asthma `ok`, BMI `non_converged`, hypertension `non_converged`, stroke `non_converged`, T2D `ok`). The caption's "four of five" is a stale string.
5. **Table 3 L280–281:** SH2B3 BMI–HTN and HTN–stroke rows still labeled "**lost** (pair absent from Stage 2 manifest — re-fire pre-registered)." But §3.4 says these were **not executed**. "Lost" implies a measurement was made and went null; "not executed" means no measurement exists.

The manuscript is now **internally inconsistent on its flagship locus** — every reader will land in one of these four contradictions. This is a non-trivial pre-submission issue.

---

## Evaluation 4 — Reproducibility & auditability 🟢 SUBSTANTIALLY IMPROVED

**(a) Locked scalars — CLOSED.** `fig2_cs_yield.R` now disk-derives `N_IDENTITY_LD_NONEMPTY` from `IDENTITY-LD-K2D-FIT-SUMMARY.tsv`; `fig3_sh2b3_eur_collapse_forest.R` had its three `EXPECTED_*` literal lists replaced with runtime disk reads (verified per the 260426-04b SUMMARY). The numeric-immutability adversarial behavior is gone; figures will now self-update on re-fire.

**(b) Provenance file boundary — NO-ACTION-NEEDED.** Acceptable disposition.

**New addition that improves auditability further:** the `TRACK-A-AUDIT-RESPONSE-2026-04-26.md` closure tracker is itself a remarkable artifact — every audit item has a status, commit hashes, files touched, and a verification recipe. This is, frankly, beyond what most published Genome Medicine submissions ship. It substantially raises the credibility floor for the submission package.

---

## Evaluation 5 — Significance & contribution 🟢 STRENGTHENED + 🟡 ONE NEW LIABILITY

**Strengthened:** The headline now says what the data actually support — modest count-level differential, with structural composition flagged as the load-bearing inflation pathway. The audit-response artifact itself becomes part of the contribution: this is a paper *and* a worked example of pre-submission audit discipline. For a methods-and-rigor venue (Genome Medicine, AJHG short report, or Bioinformatics Applications Note) that is the right framing.

**New liability — Conclusion claim 1 attribution error.** L254 reads: "Identity-LD `coloc.abf` fine-mapping inflates cross-trait PP.H4 at curated cardiometabolic loci primarily through structural credible-set composition rather than count-level yield." But:

- `coloc.abf` is the **single-causal-variant** method that does *not* fine-map; it produces five posterior probabilities directly from marginal sumstats. There is no "credible-set composition" inside `coloc.abf` — fine-mapping is the SuSiE-RSS step that *replaces* `coloc.abf`.
- The 1.06× contrast presented in this paper is between **identity-LD SuSiE-RSS** and **real-LD SuSiE-RSS**, not between identity-LD `coloc.abf` and real-LD `coloc.abf`. The published method under audit is `coloc.abf`-on-identity-LD; the comparator implemented is `SuSiE-RSS+coloc.susie`-on-identity-LD. These are different methods.
- The audit's inflation mechanism (Discussion §Identity-LD Inflation L218–220) describes SuSiE-RSS-under-identity-LD pathology, not `coloc.abf` pathology.

The paper does provide evidence that the *replacement pipeline* (SuSiE-RSS+coloc.susie) is sensitive to LD-reference quality (Figure S7 dose-response). It does *not* directly demonstrate that legacy `coloc.abf` claims are inflated. These are different scientific claims and Conclusion 1 conflates them. The published `coloc.abf` literature being "audited" was tested by the SH2B3 EUR canonical pairs — which were **not executed** (Eval 3.4 closure). So the strongest defensible Conclusion 1 is: "Where SuSiE-RSS+coloc.susie can be run with adequate LD-reference overlap, no Tier-A or Tier-B cross-trait colocalization survives at these curated loci, in contrast to the published `coloc.abf`-under-identity-LD literature." That's a real and important finding; it just requires precise wording.

---

## New issues introduced or surfaced by the revision

1. **Citation-number error at §3.4 L148:** "Wang et al. 2020²⁹" — but ref ²⁹ is Wallace 2021 (`coloc.susie`), not Wang et al. 2020 (the SuSiE *JRSS-B* paper). The Wang paper isn't in the current reference list at all. Either add it as a new ref slot (44+) or replace the citation with Zou et al. 2022²⁰ which is already in the list and covers the same convergence-theory point.

2. **Methods narrative contamination (L82):** The Methods §Fine-Mapping Integration paragraph contains audit-process narrative — *"An earlier Stage 1d narrow-validation freeze had cited 12/96... We tightened the comparator and the inflation magnitude shifted from 4.25× to 1.06×."* This belongs in the Discussion (it's an audit-response trace), not in Methods. A reviewer who comes to Methods looking for "what was done" will be confused by the meta-commentary about what *was* done in a previous freeze. The closure work belongs in either a new Discussion subsection ("Audit-driven comparator tightening") or in the existing OSF deviation log — not embedded in Methods.

3. **Decision-pending item 4 is stale (L356):** *"Whether to compute identity-LD comparator branch output at admissible regions if not already produced"* — this question has been *answered* by the k2d re-fire. Delete the bullet.

4. **QTL-coloc disclosure ↔ Tier-C headline tension:** Methods L90 + Limitations L244(5) now correctly disclose that QTL-coloc data carries unverified quality. But the Abstract L28 + Headline Result L138 + Conclusion still carry the FTO `PP.H4 = 0.3099` / IRX3 / Pancreas number as the highest Tier-C signal. If QTL-coloc data is unverified, the highest-Tier-C number is not interpretable. Either downgrade the FTO 0.3099 callout to "subject to known data-quality caveat" in the Abstract, or pull the QTL-coloc data through a verification pass before keeping it as headline.

5. **Figure S7 framing understates the strength:** the dose-response panel shows 33/60 EUR fits below the Benner threshold — that is itself a *publishable observation* about LD-reference quality across this curated locus set, not "exploratory methodology-validation." Reviewers will (rightly) ask why a discovery-grade observation is positioned as exploratory. The framing language should be promoted to "Methodology validation finding: 55% of admissible Stage 2 EUR fits sit below the Benner et al. 2017 calibration threshold."

6. **Identity-LD K2D summary L=10 saturation undisclosed in manuscript:** 11+ identity-LD K2D fits carry the canonical L-saturation fingerprint `cs_sizes = "3;3;3;3;3;3;3;3;3;4"`. This is now visible in `IDENTITY-LD-K2D-FIT-SUMMARY.tsv` and the Figure 3 disclosure subtable surfaces L-saturation per-trait at SH2B3, but the manuscript's main text still doesn't disclose this pattern across the wider 95-fit set. Eval 2(b) is correctly DEFERRED-COMPUTE for the L=20 re-fire, but a one-paragraph **prose disclosure** of the L-saturation prevalence (e.g., a Methods note: "11 of 95 identity-LD fits show signatures consistent with L-saturation at L=10; an L-sweep re-fit is pre-registered as supplementary work") would close the disclosure half of the issue independently of the compute work.

---

## High-quality improvements (3) — for the next pass

1. **Sweep the four downstream surfaces still carrying the pre-closure SH2B3 narrative.** Abstract L28, Discussion L216, Conclusion L254, Figure 3 caption L297, Table 3 L280–281. The §3.4 closure language is now the source of truth ("not executed", "3 of 5 non_converged", "missing run rather than collapse"); propagate that exact phrasing into all five sites and `grep` for residual instances of "credible-set collapse" / "manufacture" / "four of five non_converged" / "lost (pair absent ...)" to verify the sweep is complete. ~2–3 hours of focused prose work; eliminates the largest remaining reviewer-objection vector.

2. **Quantify the structural inflation claim before submission.** The manuscript's central scientific argument has shifted from "count-level yield collapses 4.25×" (now defensibly modest at 1.06×) to "credible-set composition shifts even when count is preserved." That second claim is currently *asserted* but not *measured* in any panel. A modest follow-on analysis — paired-fit comparison of (PIP-of-top-variant, lead-variant rank, credible-set member overlap) between identity-LD and real-LD across all 48 paired non-empty fits — would produce the publishable measurement. This is computable from the on-disk JSONs in `results/fine_mapping/susie/*.json` and `results_identity_ld/fine_mapping/susie/*.json`, without re-firing SuSiE. Probably a half-day of scripting + a new supplementary figure (S2). Without this, the "structural inflation" framing is currently load-bearing on a claim the data doesn't yet quantify.

3. **Reframe Conclusion 1 to match what was actually measured.** Replace "Identity-LD `coloc.abf` fine-mapping inflates cross-trait PP.H4 ..." with a precise statement like: *"At admissible curated cardiometabolic loci, replacement of identity-LD with matched 1000G EUR LD under SuSiE-RSS + coloc.susie does not materially change credible-set count (1.06× yield ratio) but produces structural posterior shifts (PIP redistribution, lead-variant rank instability, non-convergence at three of five SH2B3 EUR traits, ld_overlap_fraction = 0 at the headline FTO Tier-C signal). At these 50 curated loci, no cross-trait colocalization signal reaches Tier A or Tier B under real-LD coloc.susie, in contrast to the multiple PP.H4 ≥ 0.8 claims in the published coloc.abf-under-identity-LD literature."* This says exactly what the data show, in the right method namespace, without overclaiming.

---

## Quick improvements (3)

1. **Fix the citation-number error at §3.4 L148.** Replace "Wang et al. 2020²⁹" with "Zou et al. 2022²⁰" (already in the reference list and covers the same SuSiE convergence point) OR add Wang et al. 2020 *JRSS-B* as ref ⁴⁴ and update the superscript. ~5 minutes.

2. **Move audit-process narrative out of Methods §Fine-Mapping Integration.** The "We tightened the comparator and the inflation magnitude shifted from 4.25× to 1.06×" sentence at L82 belongs in Discussion or in a brief "Audit-driven revisions" subsection. Methods should describe the analysis as it stands. ~10 minutes.

3. **Delete the stale Decision-Pending item 4 at L356** (the question it asks has been answered by the k2d re-fire). And update item 5 — the `[EXTRACT: ...]` placeholders in Tables 1 / 2 / 3 / 4 and Results §Trait Pair Distribution / §Pleiotropic Loci / §Variant Mechanism / §Cross-Ancestry must be filled before bioRxiv. ~5 minutes for the deletion, separate planning task for the placeholders.

---

## References used in this review

In addition to the previous list (Wang *JRSS-B* 2020, Zou *PLoS Genet* 2022, Wallace *PLoS Genet* 2021, Wallace *PLoS Genet* 2020, Kanai *Cell Genomics* 2022, Weissbrod *Nat Genet* 2020, Benner *AJHG* 2017 / *Bioinformatics* 2016, Pasaniuc & Price *Nat Rev Genet* 2017, Giambartolomei *PLoS Genet* 2014, Hukku *AJHG* 2021, Foley *Nat Commun* 2021):

- **Mahajan A, Taliun D, Thurner M, et al.** (2018). *Nat Genet* 50:1505–1513. DOI 10.1038/s41588-018-0241-6 — confirmed as the correct DIAMANTE EUR T2D vintage citation per Eval 3.9 closure.

---

## Bottom line

This is the most thorough audit-response I've reviewed for an academic manuscript. The closure tracker is exemplary. The remaining issues are *symmetric to* the closure work: prose drift in surfaces that the closure didn't touch, plus one citation error and one method-namespace conflation in the Conclusion. None are blocking; all are addressable in a single 1-day prose sweep before bioRxiv. After that sweep, this becomes a publishable, defensible methods-and-rigor paper. I would now route it to **Genome Medicine** with confidence, with the Conclusion-1 reframe (HQ#3 above) being the single most important pre-submission edit.

---

## Closure delta vs prior review

| Audit item | Prior status (2026-04-25) | Current status (2026-04-26) |
|---|---|---|
| Eval 1 (4.25× comparator) | OPEN — invalidates headline | CLOSED — 1.06× headline derived from disk |
| Eval 2(a) (non-convergence in headline) | OPEN | CLOSED (prose) + new evidence in Fig 3 disclosure |
| Eval 2(b) (L=10 saturation) | OPEN | DEFERRED-COMPUTE (correctly scoped) |
| Eval 2(c) (no CIs) | OPEN | NO-ACTION-NEEDED (acceptable) |
| Eval 3.1 (FTO ld_overlap=0) | OPEN — invalidates Tier-C peak | CLOSED — surfaced as load-bearing |
| Eval 3.2 (78.9% QTL-coloc bug) | OPEN | CLOSED (prose, 3 sites) |
| Eval 3.3 (28/28 empty coloc.susie) | OPEN | IN-PROGRESS (gated correctly) |
| Eval 3.4 (SH2B3 missing run) | OPEN — flagship overreach | CLOSED — §3.4 rewritten |
| Eval 3.5 (95 vs 96) | OPEN | CLOSED (missing fit named) |
| Eval 3.6 (schema confusion) | OPEN | CLOSED (parenthetical at L140) |
| Eval 3.7 (HLA double-class) | OPEN — tautology | CLOSED — HLA = fallback only |
| Eval 3.8 (224 → 9 loci) | OPEN | CLOSED — restated 9 loci/200 rows |
| Eval 3.9 (DIAMANTE vintage) | OPEN | CLOSED — Mahajan 2018 pinned |
| Eval 3.10 (1,446/861 ghosts) | OPEN | CLOSED — grep returns 0 |
| Eval 4(a) (locked scalars) | OPEN — adversarial | CLOSED — disk-derived |
| Eval 4(b) (provenance) | OPEN | NO-ACTION-NEEDED (acceptable) |
| Eval 5 (significance) | conditional on closures | satisfied via constituent closures |
| HQ#1 (re-derive headline) | recommended | CLOSED |
| HQ#2(i) (SH2B3 L=20) | recommended | DEFERRED-COMPUTE |
| HQ#2(ii) (drop non-converged) | recommended | DEFERRED-DESIGN (Carter call) |
| HQ#2(iii) (canonical pairs) | recommended | DEFERRED-COMPUTE |
| HQ#3 (LD-quality dose-response) | recommended | CLOSED — Figure S7 + frozen scalars |
| QI#1(a)/(b)/(c) (purges) | recommended | CLOSED |
| QI#2 (HLA pick one) | recommended | SUPERSEDED via Eval 3.7 |
| QI#3 (Tier-C data-quality column) | recommended | CLOSED — Fig 3 subtable |

**Net delta:** 18 of 27 items closed with disk-verifiable evidence; 1 in-progress; 4 deferred-compute (correctly); 3 no-action-needed; 1 superseded. The reviewer's 4.25× headline-invalidation finding has been fully resolved with the correct numeric and the legacy block preserved for audit traceability. This is a production-grade audit response.
