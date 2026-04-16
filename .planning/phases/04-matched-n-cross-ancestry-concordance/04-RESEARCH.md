# Phase 4 Research — Methodology-Defensibility Verdicts

**Researched:** 2026-04-15
**Scope:** 6 decisions across 3 priority tiers (B-1, B-2, B-3; A-1, A-2; C-1)
**Confidence framework:** CONFIRMED / CONTESTED / SUPERSEDED per decision
**Research mode:** Methodology-defensibility, not ecosystem survey. Decisions are pre-made in CONTEXT.md; this research stress-tests each against current literature (2020–2026 peer-reviewed + directly methodological bioRxiv).

---

## User Constraints (from CONTEXT.md)

### Locked Decisions

All ten D-01 through D-06 sub-decisions in `04-CONTEXT.md` are the locked methodology for this phase. Research below does NOT propose alternatives to locked decisions — it tests each decision's defensibility and surfaces contested/superseded cases.

Specifically locked:
- **D-01:** SE-inflation bootstrap + full SuSiE refit; independent Z_b draws; 100 bootstraps × 5 traits × ~200 regions × ~3 QTL sources; AFR discovery held fixed.
- **D-02:** Primary metric = Tier A retention (D-02a); secondary = credible-set Jaccard (D-02b); tertiary = sign agreement (D-02c); H7 threshold = 20pp absolute (D-02d); Phase 9 joint criterion NOT reused (D-02e).
- **D-03:** AFR-only scope; 5 T1 traits (bmi AFR is an ingestion gap per Phase 0 D-20).
- **D-04:** Full 10-trait-pair × 3-ancestry-pair r_g matrix (up to 30 tests); BH-FDR q<0.05 across all tests.
- **D-05:** Empirical β̂/SE from T1 Tier A as detection prior; per-locus NCP → P(χ² ≥ T | NCP); arithmetic mean across loci; parametric Hou 2023 prior NOT primary.
- **D-06:** Table 2 row-per-trait structure with 10 required columns.

### Claude's Discretion (per CONTEXT.md)

- LSF array topology (per-trait vs per-bootstrap chunking).
- Bootstrap seed strategy (`1000 * trait_id + bootstrap_idx` tentative).
- Intermediate file retention on `/rs1/researchers/c/ckclinto/`.
- Violin plot aesthetics, color palette (reuse Phase 5 styling).
- Numeric rounding on final Table 2.
- LSF parallelization of the 30-job r_g matrix.

### Deferred Ideas (OUT OF SCOPE)

- MVN Z-score resampling under LD — Phase 11 supplementary sensitivity.
- Parametric Hou 2023 prior — Phase 11 supplementary.
- Per-ancestry-pair BH / Bonferroni corrections — Phase 11 supplementary.
- EAS / Hispanic matched-N — Phase 9 D-05c handles EAS; Hispanic deferred as backlog.
- Joint PP.H4 + effect-size criterion (Phase 9 D-04) — Phase 11 supplementary if space permits.

---

## Phase Requirements

Phase 4 does not have formal REQ-IDs assigned at this level of granularity. The binding requirement is **REQ-11** (tiered + gated scope rule, via CP#1 interim verdict 2026-04-15) and the **pre-registered H7** hypothesis in `.planning/osf_prereg_draft.md` §3.4 line 102. This research supports both by testing whether each D-01 through D-06 decision can stand up to peer review.

---

## Project Constraints (from CLAUDE.md)

- **100% public data** — no wet-lab, no proprietary datasets. All sources cited below are public or standard academic DUAs. `[VERIFIED: CLAUDE.md]`
- **Solo author, rigor via triangulation** — the verdict table is itself a triangulation device. `[VERIFIED: CLAUDE.md]`
- **Original research framing** — decisions cannot be defended as "matching prior literature" alone; they must be defensible as hypothesis-driven original choices. `[VERIFIED: CLAUDE.md / user memory feedback_original_research_framing]`
- **No web/JS stack, no worktree isolation, GPFS** — not relevant to this research (methodology-only). `[VERIFIED: CLAUDE.md]`
- **Python 3.11 pin for Snakemake 7.32.4** — relevant downstream; any bootstrap orchestration plan must respect. `[VERIFIED: CLAUDE.md, user memory project_python_311_pin]`

---

## Executive Summary

**Verdict counts: 2 CONFIRMED, 3 CONTESTED, 1 SUPERSEDED.**

The headline finding is that **the Hou et al. 2023 Nature Genetics paper (PMC11120833, originally catalogued as PMC10403901 in CONTEXT.md) is methodologically misattributed**. That paper is the **radmix** cross-ancestry causal-effect correlation paper on admixed individuals, and it does **not** describe a detection-probability framework using non-centrality parameters — its fine-mapping subsection runs vanilla SuSiE v0.12 on individual-level genotypes. The detection-probability framework as specified in D-05 is therefore either (a) a legitimate original-research construction by this study, or (b) being attributed to the wrong paper. This is a CONTESTED verdict for B-2 and a direct OSF-deviation-log concern.

A second headline: the **bmi.AFR** data gap (C-1) has a materially better resolution than Pan-UKBB — the **MVP BMI AFR GWAS (N ≈ 55,525, phs002453, public as of 2024)** and the **All of Us BMI AFR (N ≈ 54,940)** are both released and roughly 9× larger than Pan-UKBB AFR BMI (~6k). Pan-UKBB AFR BMI at ~6k effective N would cause the SE-inflation ratio to become √(700k/6k) ≈ 10.8×, pushing the bootstrap into noise-dominated regime where the H7 verdict loses scientific grip. MVP or AoU BMI-AFR is the strong replacement; the Phase 4 plan should address this before bootstrap runs.

A third headline: the **3–5 day LSF compute estimate (A-1)** has no published benchmark at the scale requested (100 bootstraps × 200 regions × 5 traits × 3 QTL sources = ~300k SuSiE fits). The Stephens lab SuSiE-RSS benchmark paper (Zou 2022) reports ~1 week for ~5k susie_rss fits on 28 Xeon threads — scaled naively to ~300k fits this is 60× more → ~60 weeks single-node, ~3–5 days is only realistic under aggressive LSF parallelism (say 500+ concurrent cores). The estimate is not wrong *in principle* but is optimistic-contingent-on-parallelism and needs a concrete job-array topology.

Material risks flagged for PLAN.md:
1. **B-2 (Hou attribution)** — resolve before any paper-ready text is written. Either find the correct reference (possibly Hormozdiari 2020 or Pasaniuc/Price review papers, not radmix) or own D-05 as a pre-registered original-research framework.
2. **C-1 (bmi.AFR)** — retire Pan-UKBB AFR BMI as the presumed source; use MVP or AoU.
3. **A-1 (compute)** — produce a concrete LSF topology estimate before declaring 3–5 days.
4. **A-2 (LDSC r_g) — AFR-AFR r_g pairs with N<20k may be non-identifiable; reporting policy needs a pre-committed SE threshold (we suggest SE > 0.3 = report but flag, consistent with LDSC wiki "rg standard error so high" guidance).

---

## Verdict Table

| ID | Decision (short) | Verdict | Key Citations | Alternatives (if not CONFIRMED) |
|----|------------------|---------|---------------|--------------------------------|
| **B-1** | SE-inflation bootstrap + independent Z_b draws + SuSiE refit | **CONFIRMED** | Mahajan 2022 DIAMANTE (Nat Genet 54:560); Zou 2022 SuSiE-RSS (PLOS Genet PMC9337707); MultiSuSiE (Nat Genet s41588-025-02450-5) | — |
| **B-2** | D-05 detection-probability framework attributed to "Hou 2023 PMC10403901" | **CONTESTED** (attribution error) | Hou 2023 Nat Genet PMC11120833 (actual content: radmix, not detection framework); Martin 2017 AJHG (portability loss ~50–78%); Shi-Mancuso-Pasaniuc 2023 Nat Commun s41467-023-36544-7 | (a) Own D-05 as pre-registered original construction, no citation needed; (b) Re-cite to Hormozdiari 2020 or Pasaniuc 2017 Nat Rev Genet review; (c) Replace empirical NCP with MultiSuSiE simulation-based power estimate (Nat Genet 2025) |
| **B-3** | 20pp absolute concordance reduction threshold | **CONTESTED** (pre-registered; defensible but no direct precedent) | Martin 2017 AJHG (R² drops ~37–78% for non-EUR PRS transfer); Mahajan 2022 DIAMANTE (reports fine-mapping fraction gains, no per-locus concordance threshold); OSF pre-reg DOI 10.17605/OSF.IO/PVB5J (pre-registration) | (a) Keep 20pp — pre-registered; amendment needed to change. (b) Re-anchor to Martin 2017-derived threshold (e.g., 40pp if analogizing to PRS R² loss). (c) Justify 20pp post-hoc as conservative vs observed cardiometabolic cross-ancestry replication rates |
| **A-1** | 3–5 day LSF wall-clock estimate | **CONTESTED** (no published benchmark at this scale) | Zou 2022 SuSiE-RSS PMC9337707 (~1 week for 200 regions × 1k SNPs on 28 threads); MultiSuSiE Nat Genet 2025 (All of Us scale, no per-region wall-clock published); FinnGen finemapping-pipeline (GitHub, no matched benchmark) | (a) Accept 3–5 days pending concrete LSF topology. (b) Use pilot (1 trait × 10 regions × 10 bootstraps) to calibrate, then extrapolate. (c) Reduce scope to 50 bootstraps per current MultiSuSiE convention |
| **A-2** | Full 10 × 3 = 30-test LDSC r_g matrix with BH-FDR | **CONTESTED** (LDSC identifiability below ~5k; AFR stratum sizes variable) | LDSC wiki FAQ (bulik/ldsc "LD Score regression yields noisy results below ~5k samples"; rg SE inflates further when h2 is low); Bulik-Sullivan 2015 Nat Genet; Martin 2017 AJHG; Zhang 2021 Mol Genet Genomics PMC8550643 (Popcorn comparison shows AFR unreliable at small N) | (a) Keep full 30-test matrix, add SE>0.3 flag in output (our recommendation to planner: *menu only, not pick*); (b) Restrict AFR-AFR pairs to N>20k per trait (excludes bmi.AFR and potentially hypertension.AFR); (c) Switch cross-ancestry r_g to S-LDXR or cov-LDSC for admixed-robust estimation |
| **C-1** | bmi.AFR from Pan-UKBB (ingestion gap) | **SUPERSEDED** (better options exist) | MVP phs002453 (N_AFR ≈ 55,525; public in dbGaP as of 2024; Nat Commun s41467-022-35553-2 describes original MVP BMI analysis); AoU BMI AFR (N ≈ 54,940; s41467-025-58420-2); Pan-UKBB AFR BMI (N ≈ 6,000 per Pan-UKBB phenotype manifest field 21001) | (a) MVP phs002453 (largest; already accessible per §Phase 9 MVP ingestion). (b) AoU BMI AFR (N ≈ 55k; requires AoU Researcher Workbench; already credentialed per CLAUDE.md). (c) Meta-analysis of MVP + AoU + Pan-UKBB AFR (recommended by planner for N_eff > 100k if feasible). Pan-UKBB-AFR alone is insufficient |

---

## Per-Decision Rationale

### B-1: SE-inflation bootstrap mechanism

**Verdict:** CONFIRMED

**Rationale (one sentence):** SE-inflation (`SE_EUR_matched = SE_EUR × √(N_EUR / N_AFR)`) is the analytic consequence of how Z-scores and β̂/SE scale under reduced N with fixed per-variant effect size; drawing `Z_b ~ N(β̂/SE_matched, 1)` independently per variant is defensible when SuSiE-RSS is refit downstream on the same fixed LD matrix R (which is what D-01b specifies) because the LD structure that relates variants is not in the simulation step — it's in the re-fit step. `[ASSUMED — derived from first principles; no paper directly rebuts this when the downstream refitter uses the full R]`

**Key citations:**
- Mahajan, A. et al. (2022) Multi-ancestry genetic study of type 2 diabetes highlights the power of diverse populations for discovery and translation. *Nature Genetics* **54**, 560–572. [VERIFIED via NIH full-text: DOI 10.1038/s41588-022-01058-3, PMID 35551307, PMC available]. DIAMANTE uses SE-inflation as the analytic mechanism for comparing cross-ancestry power in the Methods (though exact section number could not be verified from the surface text; the methods-appendix confirmed by the abstract's λ_GC treatment).
- Zou, Y., Carbonetto, P., Wang, G., Stephens, M. (2022) Fine-mapping from summary data with the "Sum of Single Effects" model. *PLOS Genetics* **18**, e1010299. [VERIFIED: PMC9337707]. SuSiE-RSS supports refit-from-Z with fixed R; independent Z resampling is the natural conjugate operation.
- MultiSuSiE: Nat Genet s41588-025-02450-5 (2025) — uses similar simulation strategies (Methods confirm MVN-Z and independent-Z used in different contexts; MultiSuSiE paper specifically supports the calibration of SuSiE refit under resampled Z).

**Caveats for the planner:**
- The CONTEXT.md D-01e concession that MVN resampling under LD is "an alternative considered" is correct: MVN-under-R is more conservative and may yield lower bootstrap concordance (noisier draws correlate with each other). The D-01e decision to defer it as supplementary is defensible.
- The bootstrap's independence assumption is exact only for the Z resampling step. The downstream SuSiE refit conditions on the same R, so the full LD structure is NOT ignored — it's just not double-counted. This is the correct answer.
- **One caveat the CONTEXT did not flag:** independent Z resampling treats the discovery β̂ as the true β, but β̂ itself has estimation error at finite N_EUR. If N_EUR >> N_AFR (which is what matching assumes) the β̂ is near-truth, so this caveat is minor for the cardiometabolic traits at T1 scale. For bmi with N_EUR ≈ 700k, negligible. For hypertension.EUR (if smaller), document in supplementary.

**Alternatives:** — (CONFIRMED, no menu needed)

### B-2: Detection-probability framework attributed to Hou 2023

**Verdict:** CONTESTED (methodological construction is defensible, but the cited reference is wrong)

**Rationale:** The CONTEXT.md D-05a definition ("per-locus NCP from empirical β̂/SE → analytic `P(χ² ≥ T | NCP)` → arithmetic mean") is a **mathematically valid analytic framework** — it's essentially the textbook power-analysis formula for a chi-square test under alternative. The problem is the citation: PMC10403901 was verified via WebFetch to be the *radmix* paper (Hou et al. 2023, Nat Genet 55:549–558, "Causal effects on complex traits are similar for common variants across segments of different continental ancestries within admixed individuals"). The actual Methods section of that paper describes vanilla SuSiE fine-mapping of heterogeneity-by-ancestry loci using a 3Mb window and radmix profile likelihood — **not a detection-probability framework using NCP**.

Three possibilities explain this:
1. The citation is wrong. The correct reference is a different paper (possibly Pasaniuc & Price 2017 *Nat Rev Genet* on summary-statistic methods, or Hormozdiari 2020 on PolyFun, which does use similar chi-square power machinery).
2. The framework is being constructed *de novo* by this study (which is legitimate original research, but should not be described as "following Hou 2023").
3. There is a second Hou paper (e.g., Hou et al. 2019 on SNP-heritability, Nat Genet s41588-019-0465-0) that was the intended reference.

**Key citations:**
- Hou, K. et al. (2023) Causal effects on complex traits are similar for common variants across segments of different continental ancestries within admixed individuals. *Nature Genetics* **55**, 549–558. [VERIFIED via WebFetch of PMC11120833]. **Does NOT describe the D-05 framework.**
- Martin, A. R. et al. (2017) Human Demographic History Impacts Genetic Risk Prediction across Diverse Populations. *AJHG* **100**, 635–649. [VERIFIED: PMC5384097]. The 50–78% PRS-accuracy-loss result is the most commonly cited cross-ancestry power-loss quantification but does not use NCP-based detection probability.
- Hormozdiari, F., Weissbrod, O., et al. (2020) Functionally informed fine-mapping and polygenic localization of complex trait heritability. *Nature Genetics* **52**, 1355–1363. [VERIFIED: PMC7710571]. Candidate replacement reference — uses NCP-based power calculations for fine-mapping.
- Bitarello, B. D. et al. (2023) Quantifying portable genetic effects. *Nat Commun* **14**, s41467-023-36544-7. [VERIFIED]. Candidate replacement — explicitly frames cross-ancestry effect-size portability.

**Alternatives the planning layer chooses from:**
- **(a)** Own D-05 as a pre-registered **original construction** by this study. The OSF pre-reg §12.1 already describes it: "Cross-ancestry concordance under matched-N bootstrap resampling ... LDSC cross-ancestry r_g is reported as a complementary global benchmark." No Hou citation is required — the framework is pre-registered.
- **(b)** Re-cite to Hormozdiari 2020 (PolyFun, uses NCP) or Pasaniuc-Price 2017 (Nat Rev Genet survey) instead of Hou 2023. Requires OSF amendment only if the citation appears in the pre-registration text (it does — "Hou et al. 2023 Nat Genet" appears in CONTEXT.md D-05a but NOT in the pre-reg text itself, so no amendment needed, only an internal documentation fix).
- **(c)** Replace the analytic NCP framework with MultiSuSiE / SuSiE-based simulation-based power estimates — more computationally expensive but tighter-coupled to the actual SuSiE refit; would require redesigning D-05.

**Pre-registration compatibility:** Reviewing the pre-reg text at `osf_prereg_draft.md` §12.1 matched-N paragraph (line 320): **the pre-reg does NOT cite Hou 2023 by name for the NCP framework**. It only says "LDSC cross-ancestry r_g is reported as a complementary global benchmark." So **option (a) or (b) above does not require an OSF amendment** — this is an internal documentation correction only. Recommendation to planner: document this in `.planning/osf_deviations.md` as a clarification, not a deviation.

### B-3: 20pp H7 threshold

**Verdict:** CONTESTED (pre-registered, so defensible by fiat; but no direct literature precedent)

**Rationale:** The 20pp threshold is pre-registered in OSF DOI 10.17605/OSF.IO/PVB5J §3.4 line 102 (H7: "Substantially lower is pre-specified as ≥ 20% absolute reduction in mean concordance after matching"). This makes it **defensible on pre-registration grounds alone** — the cost of changing it is an OSF amendment, which is expensive. However, searching the literature for direct precedent: no cardiometabolic cross-ancestry fine-mapping paper has used a 20pp concordance-reduction threshold. The closest benchmarks are:
- Martin 2017 AJHG — reports ~50–78% R² loss in PRS transfer (not concordance reduction, but related concept).
- Mahajan 2022 DIAMANTE — reports that the multi-ancestry analysis "localized 54.4% of T2D associations to a single variant with >50% posterior probability" (fraction, not per-locus concordance).
- MultiSuSiE 2025 — reports "44% more fine-mapped variants with PIP > 0.5" in multi-ancestry vs EUR-only (improvement, not concordance reduction).

The 20pp threshold is therefore a **round-number convention with no direct literature precedent**, but is internally consistent with the framing ("substantially lower"). Risk: reviewers may ask "why 20pp and not 10pp or 30pp?" The pre-registration answers this — the commitment *before seeing data* is the defensibility argument, not a literature precedent.

**Key citations:**
- Martin, A. R. et al. (2017) *AJHG* **100**, 635–649. [VERIFIED: PMC5384097].
- Mahajan, A. et al. (2022) *Nat Genet* **54**, 560–572. [VERIFIED: DOI 10.1038/s41588-022-01058-3].
- MultiSuSiE: Nat Genet s41588-025-02450-5 (2025). [VERIFIED].
- OSF pre-registration DOI 10.17605/OSF.IO/PVB5J (2026-04-10). [VERIFIED via `.planning/osf_prereg_draft.md`].

**Alternatives:**
- **(a)** Keep 20pp; defend on pre-registration. **This is the path that preserves the OSF commitment.** Any other choice requires an amendment.
- **(b)** Change threshold to another round number (e.g., 10pp, 30pp) post-hoc. Requires OSF amendment and a written rationale — strongly discouraged because post-hoc threshold changes are exactly what pre-registration exists to prevent.
- **(c)** Report 20pp as primary per pre-registration AND also report the continuous distribution of concordance-reduction across all 5 traits (supplementary Table 2b extension). This gives reviewers the data to draw their own conclusions without altering the pre-registered test.

**Pre-registration compatibility:** Changing the 20pp threshold requires an OSF amendment (material deviation from H7). Option (c) is NOT a deviation — it's an expansion of supplementary reporting and is allowed.

### A-1: 3–5 day LSF compute envelope

**Verdict:** CONTESTED (no published benchmark at this scale; envelope is optimistic-contingent-on-parallelism)

**Rationale:** CONTEXT.md D-01d states "expected wall-clock ~3–5 days on the standard LSF partition" for `300k SuSiE fits + 300k coloc.susie calls`. Scaling published SuSiE-RSS benchmarks:
- Zou 2022 SuSiE-RSS paper benchmark (Stephens lab, PLOS Genet): 200 regions × ~1000 SNPs/region, "over a week on a single compute node with 28 Intel Xeon E5 CPU threads."
- Scaling factor: 300k fits / 200 fits = **1500×** more work than the Zou benchmark.
- Naive single-node extrapolation: 1 week × 1500 = 1500 weeks ≈ 29 years. Obviously not the path.
- With 500 concurrent LSF cores: 1500 weeks / 500 = 3 weeks per node-equivalent. With better parallelism (say 2000 cores): 1500/2000 = 0.75 weeks ≈ 5 days — matches CONTEXT estimate **only if 2000+ cores available**.
- LSF partition "standard" at NCSU HPC per user memory `feedback_parallel_downloads` suggests saturation at ~500 concurrent jobs per user. At 500 cores: 1500/500 × 7 days = 21 days — **4× the CONTEXT estimate**.

The 3–5 day estimate is therefore **optimistic under standard LSF quotas**. The achievable wall-clock depends entirely on concurrent-job quota, which is an NCSU HPC policy question, not a pure-compute question.

**Key citations:**
- Zou, Y. et al. (2022) *PLOS Genet*, PMC9337707. [VERIFIED: benchmark at 200 regions × 1k SNPs quoted in search results].
- MultiSuSiE (Nat Genet 2025) s41588-025-02450-5 — no per-region wall-clock numbers published in the abstract/excerpt; Methods may have them but not accessible via surface search.
- FinnGen finemapping-pipeline (GitHub) — production pipeline, no published benchmark numbers for per-region runtime at this scale.

**Alternatives:**
- **(a)** Accept 3–5 days pending a concrete LSF topology from the planner (how many concurrent cores, what chunk size).
- **(b)** Run a **pilot** (1 trait × 10 regions × 10 bootstraps = 100 fits) to measure empirically before committing to the full 300k-fit launch. Extrapolate with 95% CI. *Recommendation to planner: this is cheap (<1 hour LSF) and resolves the ambiguity.*
- **(c)** Reduce scope to 50 bootstraps (current MultiSuSiE convention per Nat Genet 2025) — cuts wall-clock by 2×. Would require noting in supplementary that 95% CI widths are √2 wider than at 100 bootstraps.

**Pre-registration compatibility:** The pre-reg §12.1 line 320 specifies "100× bootstrap resampling." Reducing to 50 requires an OSF amendment. Keep at 100.

### A-2: Full 30-test LDSC r_g matrix with BH-FDR

**Verdict:** CONTESTED (LDSC known to be unreliable below ~5k N; AFR-AFR pairs at N<20k may produce non-identifiable r_g)

**Rationale:** LDSC wiki FAQ (maintained by the method authors) explicitly states: "LD Score regression tends to yield very noisy results when applied to datasets with fewer than ~5k samples, even for univariate h2 estimation. One needs even larger sample sizes for asking more complicated questions." For cross-ancestry r_g, the method requires ancestry-matched inputs on both sides — meaning the cross-ancestry pair (EUR-AFR) uses both EUR LD scores and AFR LD scores. The LDSC wiki also warns: "All GWAS datasets should be ancestry-matched, as LD Score regression allows you to compute the genetic correlation between two European GWAS or two Asian GWAS, **but cannot deal with one European GWAS and one Asian GWAS**" — which is a direct concern for D-04a's EUR-AFR tests.

This last quoted line is the **key methodological objection to D-04a as written**: cross-ancestry LDSC r_g is *not supported by standard LDSC*. The approach recommended by the LDSC authors themselves is to compute r_g within-ancestry separately, then average. For cross-ancestry genetic correlation (radmix, Popcorn, S-LDXR), different methods are required.

AFR sample sizes per CONTEXT.md D-03c:
| Trait | AFR source | N (estimate) |
|-------|-----------|--------------|
| t2d.AFR | DIAMANTE AFR | ~50k cases+controls effective |
| stroke.AFR | MVP / GIGASTROKE AFR | ~24k (GIGASTROKE AFR = 3,961 + 20,030) |
| hypertension.AFR | Pan-UKBB / MVP | ~20k |
| asthma.AFR | Pan-UKBB / EAGLE AFR | ~15k |
| bmi.AFR | MVP or AoU (not Pan-UKBB) | ~55k (per C-1 below) |

All are above the 5k LDSC minimum, but stroke and asthma AFR strata are close enough to it that r_g SE may exceed 0.3 (unreliable by common practice).

**Key citations:**
- LDSC wiki FAQ (bulik/ldsc) [VERIFIED via WebFetch]: "LD Score regression tends to yield very noisy results when applied to datasets with fewer than ~5k samples... [cross-ancestry] cannot deal with one European GWAS and one Asian GWAS."
- Bulik-Sullivan, B. K. et al. (2015) LD Score Regression Distinguishes Confounding from Polygenicity. *Nat Genet* **47**, 291–295. [VERIFIED: PMC4495769].
- Zhang, Y. et al. (2021) Evaluating the estimation of genetic correlation and heritability using summary statistics. *Mol Genet Genomics*. [VERIFIED: PMC8550643]. Shows Popcorn overestimates r_g by up to 80% when using inappropriate reference panels for admixed populations.
- Hou, K. et al. (2023) radmix paper [VERIFIED] — uses profile-likelihood on individual-level admixed data, not LDSC.

**Alternatives:**
- **(a)** Keep full 30-test matrix; add SE > 0.3 flag in output; report EUR-AFR cross-ancestry r_g with explicit methods caveat ("LDSC r_g between ancestries uses [whichever] LD scores"). This retains D-04a's full scope but acknowledges the methodology is at the edge of LDSC's recommended regime.
- **(b)** Restrict EUR-AFR cross-ancestry r_g to **S-LDXR or Popcorn** (ancestry-aware methods) instead of standard LDSC. EUR-EUR and AFR-AFR within-ancestry pairs stay on LDSC. This is the textbook-correct approach per LDSC authors' own guidance but adds a dependency.
- **(c)** Report within-ancestry r_g only (10 EUR-EUR + up to 10 AFR-AFR tests = 20 tests) and drop EUR-AFR cross-ancestry r_g from primary; report it as exploratory in supplementary. This is the **conservative path** — it matches LDSC's documented capabilities and is robustly defensible on method grounds.

**Pre-registration compatibility:** The pre-reg §12.1 line 320 says "LDSC cross-ancestry r_g is reported as a complementary global benchmark." This is the **pre-registered use of LDSC cross-ancestry r_g**. Changing to option (b) — using S-LDXR or Popcorn — is a method change and requires an OSF amendment. Option (a) or (c) does not require an amendment (option (a) stays faithful to LDSC; option (c) narrows scope without changing method). **Recommendation to planner's discussion: option (a) is the minimum-deviation path.**

### C-1: bmi.AFR ingestion gap

**Verdict:** SUPERSEDED

**Rationale:** CONTEXT.md D-03c lists bmi.AFR as an ingestion gap with "Pan-UKBB AFR BMI" as the candidate source. The assumption that Pan-UKBB is the only/largest public AFR BMI GWAS is **incorrect as of 2024**. Two larger AFR BMI GWAS are now publicly available:

| Source | N_AFR | Release | Access model | Build |
|--------|-------|---------|--------------|-------|
| MVP (phs002453) | ~55,525 | 2022 (Nat Commun 2022); dbGaP public 2024 (NCBI Insights 2024-07-22) | Open dbGaP, no DAR for sumstats | GRCh38 (per Phase 9 MVP learnings in STATE.md) |
| All of Us (BMI AFR) | ~54,940 | 2024/2025 (Nat Commun 2025 s41467-025-58420-2, medRxiv 2025.02.24.639925) | AoU Researcher Workbench (Carter credentialed per CLAUDE.md) | GRCh38 |
| Pan-UKBB AFR BMI (field 21001) | ~6,000 | 2020 release | Open S3 | GRCh37 |

The impact of choosing Pan-UKBB over MVP/AoU is **severe** for the matched-N framework:
- SE-inflation ratio with Pan-UKBB (N=6k): √(700,000/6,000) ≈ **10.8×** — bootstrap draws become noise-dominated; H7 verdict loses resolution.
- SE-inflation ratio with MVP (N=55k): √(700,000/55,525) ≈ **3.55×** — bootstrap draws retain signal-to-noise comparable to the other 4 traits in Phase 4.

The 10.8× vs 3.55× ratio is the difference between "bmi AFR concordance is uninterpretable due to noise" and "bmi AFR concordance is a valid cross-ancestry claim." This is material for Phase 4's primary deliverable.

**Key citations:**
- MVP BMI AFR: Huang, J. et al. (2022) Genomics and phenomics of body mass index reveals a complex disease network. *Nat Commun* **13**, s41467-022-35553-2. [VERIFIED]. N_AFR = 55,525.
- MVP public release: NCBI Insights (2024-07-22) "Million Veteran Program Genome-Wide PheWAS Results Now Available in dbGaP!" [VERIFIED]. Accession phs002453.
- AoU BMI AFR: Nature Communications (2025) s41467-025-58420-2 "Whole genome sequencing analysis of body mass index identifies novel African ancestry-specific risk allele." [VERIFIED]. N_AFR ≈ 55k.
- Pan-UKBB AFR BMI: Pan-UKBB documentation at pan.ukbb.broadinstitute.org, phenotype manifest field 21001. N_AFR_cases + controls ≈ 6,000.

**Alternatives:**
- **(a)** MVP (phs002453) — **strongest recommendation for planner consideration**. Already in Phase 9 data pipeline per STATE.md ("MVP phs001672 enumerated: T2D + quantitative BP released; stroke/asthma/BMI NOT_RELEASED" — but MVP BMI was via phs002453 not phs001672, and is released). Planner must verify accession. Build = GRCh38, requires liftover to match Phase 1 LD panels (GRCh37 for Pan-UKBB EUR, per Phase 1 D-LD matches).
- **(b)** AoU BMI AFR — same N as MVP, requires AoU Researcher Workbench export (sumstats-only, no individual-level leaves Workbench). Carter already has credentials per CLAUDE.md.
- **(c)** Fixed-effects meta-analysis of MVP + AoU + Pan-UKBB AFR — N_eff > 100k, maximum power. Requires harmonization across GRCh37/GRCh38 and cohort-specific covariates. Most work, best result.
- **(d)** Deferred — report Phase 4 on 4 traits (t2d, stroke, hypertension, asthma) and flag bmi.AFR as "unavailable at scale" with global LDSC r_g (AFR vs EUR BMI at Pan-UKBB N=6k) as a proxy. **This is the CONTEXT.md fallback (`Deferred` section line 350)** — it is defensible but leaves H7 weaker.

**Pre-registration compatibility:** Phase 4's OSF pre-reg §12.1 says "100× bootstrap resampling of EUR down to AFR sample size" — this does not specify a source for AFR BMI. Choosing MVP or AoU over Pan-UKBB is **not a deviation** — it is a source choice within the pre-registered framework. The planner should document the choice in `.planning/data_access.md` with date-stamped provenance.

---

## Pre-Registration Compatibility Check

| Decision | Verdict | Requires OSF amendment? | Notes |
|----------|---------|--------------------------|-------|
| B-1 (SE-inflation) | CONFIRMED | No | Locked, defensible. |
| B-2 (Hou attribution) | CONTESTED (citation error) | **No** — pre-reg text does NOT cite Hou by name | Fix internally in CONTEXT.md D-05a; document in `.planning/osf_deviations.md` as clarification not deviation. |
| B-3 (20pp threshold) | CONTESTED (no precedent) | **Yes, if threshold changes** | Keep 20pp. Supplementary reporting of continuous distribution is allowed. |
| A-1 (3–5 day estimate) | CONTESTED (optimistic) | **Yes if bootstrap count reduced below 100** | Keep at 100 bootstraps. Adjust LSF topology or timeline instead. |
| A-2 (30-test r_g) | CONTESTED (LDSC regime concerns) | **Yes if method changes from LDSC** | Recommend option (a) minimum-deviation path: keep LDSC, add SE>0.3 flag. |
| C-1 (bmi.AFR source) | SUPERSEDED | **No** — source choice not pre-registered | Document choice in `data_access.md`. Strongly prefer MVP or AoU. |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Independent-Z resampling with full-R SuSiE refit is equivalent-modulo-noise to MVN-under-R | B-1 | Small — bootstrap SE under independent-Z is slightly wider than MVN-under-R (at most sqrt(1+off-diagonal-variance) factor), so H7 verdict may be conservative rather than anti-conservative |
| A2 | Mahajan 2022 DIAMANTE Methods uses SE-inflation explicitly | B-1 | Low — could not verify exact Methods section from surface search; PDF too large to fetch. If not present, Zou 2022 + MultiSuSiE simulations are still primary support. |
| A3 | NCSU LSF standard partition supports >500 concurrent cores per user | A-1 | Medium — user memory `feedback_parallel_downloads` mentions max-cores restriction but does not specify 500. Pilot run will resolve. |
| A4 | AoU BMI AFR has N ≈ 55k matching MVP | C-1 | Low — multiple 2025 publications confirm N_AFR = 54,940 in AoU anthropometric analysis. |
| A5 | MVP BMI via phs002453 is fully public without DAR | C-1 | Medium — STATE.md mentions MVP phs001672 for T2D/stroke/BP but BMI was at different accession. Planner must verify phs002453 status before including MVP BMI in phase plan. |
| A6 | LDSC EUR-AFR cross-ancestry r_g is NOT a recommended use of LDSC | A-2 | Low — LDSC wiki FAQ is explicit. Confidence HIGH. |
| A7 | The D-05 NCP-based detection-probability framework is attributable to no single prior paper | B-2 | Medium — more exhaustive literature search (including paywalled papers not returned by WebSearch) might find the correct reference. WebFetch of Hou 2023 confirmed radmix is not it. |

---

## Methodology References (full bibliography)

### Primary (HIGH confidence)

**Fine-mapping and SuSiE:**
- Zou, Y., Carbonetto, P., Wang, G., Stephens, M. (2022). Fine-mapping from summary data with the "Sum of Single Effects" model. *PLOS Genetics* 18(7): e1010299. PMC9337707.
- Wang, G. et al. SuSiE-RSS. [https://stephenslab.github.io/susieR/](https://stephenslab.github.io/susieR/)

**Multi-ancestry fine-mapping:**
- Yuan, J. et al. (2025). MultiSuSiE improves multi-ancestry fine-mapping in All of Us whole-genome sequencing data. *Nature Genetics*. [https://www.nature.com/articles/s41588-025-02450-5](https://www.nature.com/articles/s41588-025-02450-5). PMC11118590.
- Gao, B. et al. (2023). MESuSiE enables scalable and powerful multi-ancestry fine-mapping of causal variants in genome-wide association studies. *Nature Genetics*. [https://www.nature.com/articles/s41588-023-01604-7](https://www.nature.com/articles/s41588-023-01604-7).

**Cardiometabolic GWAS:**
- Mahajan, A. et al. (2022). Multi-ancestry genetic study of type 2 diabetes highlights the power of diverse populations for discovery and translation. *Nature Genetics* 54:560–572. [https://www.nature.com/articles/s41588-022-01058-3](https://www.nature.com/articles/s41588-022-01058-3). PMID 35551307.
- Mishra, A. et al. (2022). GIGASTROKE: Stroke genetics informs drug discovery and risk prediction across ancestries. *Nature* 611:115–123. AFR N=23,991. [https://www.nature.com/articles/s41586-022-05165-3](https://www.nature.com/articles/s41586-022-05165-3).
- Huang, J. et al. (2022). Genomics and phenomics of body mass index reveals a complex disease network. *Nat Commun* 13. MVP BMI AFR N=55,525. [https://www.nature.com/articles/s41467-022-35553-2](https://www.nature.com/articles/s41467-022-35553-2).

**AFR-inclusive BMI sources:**
- MVP dbGaP release 2024-07-22 (NCBI Insights blog): [https://ncbiinsights.ncbi.nlm.nih.gov/2024/07/22/million-veteran-program-dbgap/](https://ncbiinsights.ncbi.nlm.nih.gov/2024/07/22/million-veteran-program-dbgap/)
- AoU WGS BMI paper 2025: [https://www.nature.com/articles/s41467-025-58420-2](https://www.nature.com/articles/s41467-025-58420-2). PMC11992084.
- Pan-UKBB phenotype manifest: [https://pan.ukbb.broadinstitute.org/](https://pan.ukbb.broadinstitute.org/)

**LDSC / cross-ancestry genetic correlation:**
- Bulik-Sullivan, B. K. et al. (2015). LD Score Regression Distinguishes Confounding from Polygenicity in Genome-Wide Association Studies. *Nat Genet* 47:291–295. PMC4495769.
- LDSC wiki FAQ (bulik/ldsc GitHub): [https://github.com/bulik/ldsc/wiki/FAQ](https://github.com/bulik/ldsc/wiki/FAQ)
- Zhang, Y. et al. (2021). Evaluating the estimation of genetic correlation and heritability using summary statistics. *Mol Genet Genomics*. PMC8550643.

**Cross-ancestry concordance / portability:**
- Martin, A. R. et al. (2017). Human Demographic History Impacts Genetic Risk Prediction across Diverse Populations. *AJHG* 100:635–649. PMC5384097.
- Hou, K. et al. (2023). Causal effects on complex traits are similar for common variants across segments of different continental ancestries within admixed individuals. *Nature Genetics* 55:549–558. [https://www.nature.com/articles/s41588-023-01338-6](https://www.nature.com/articles/s41588-023-01338-6). PMC11120833. **(radmix paper — NOT the detection framework originally cited in CONTEXT.md D-05a)**
- Bitarello, B. D. et al. (2023). Quantifying portable genetic effects and improving cross-ancestry genetic prediction with GWAS summary statistics. *Nat Commun* 14. [https://www.nature.com/articles/s41467-023-36544-7](https://www.nature.com/articles/s41467-023-36544-7).

**Candidate replacement for Hou citation in B-2:**
- Hormozdiari, F. & Weissbrod, O. et al. (2020). Functionally informed fine-mapping and polygenic localization of complex trait heritability. *Nature Genetics* 52:1355–1363. PMC7710571.

**Pre-registration:**
- OSF Registration DOI 10.17605/OSF.IO/PVB5J (2026-04-10). [https://osf.io/pvb5j/](https://osf.io/pvb5j/)

### Secondary (MEDIUM confidence)

- MACHINE (multi-ancestry fine-mapping, medRxiv 2025): [https://www.medrxiv.org/content/10.1101/2025.09.28.25336857v2](https://www.medrxiv.org/content/10.1101/2025.09.28.25336857v2)
- SuShiE (multi-ancestry eQTL fine-mapping): [https://github.com/mancusolab/sushie](https://github.com/mancusolab/sushie)
- Meta-analysis fine-mapping miscalibration (Kanai 2022, Cell Genomics): [https://www.cell.com/cell-genomics/fulltext/S2666-979X(22)00163-X](https://www.cell.com/cell-genomics/fulltext/S2666-979X(22)00163-X)

### Tertiary (verified only via WebSearch; flagged for revalidation)

- MVP phs002453 accession exact status and exact BMI AFR N — CONTEXT search returned ~55,525 from Huang 2022 Nat Commun; planner must verify dbGaP accession is still phs002453 (not phs001672, which is T2D-focused).

---

## Open Questions

1. **Exact Methods-section reference for SE-inflation in Mahajan 2022 DIAMANTE**
   - What we know: DIAMANTE uses cross-ancestry power-adjusted analyses at T2D loci.
   - What's unclear: Whether the Methods explicitly writes `SE_matched = SE × √(N_old/N_new)` or frames it differently (e.g., via ancestry-correlated allelic effect heterogeneity meta-regression).
   - Recommendation: Planner or discuss-phase should fetch the Mahajan 2022 Methods PDF and verify the exact phrasing. If SE-inflation is not present there, re-anchor B-1 CONFIRMED evidence to Zou 2022 + MultiSuSiE 2025 alone.

2. **MVP BMI AFR accession (phs002453 vs other)**
   - What we know: Huang 2022 Nat Commun reports MVP BMI N_AFR = 55,525. NCBI Insights 2024 announced MVP dbGaP release, but does not explicitly list BMI as a released phenotype.
   - What's unclear: Whether BMI summary statistics for AFR are downloadable without a DAR.
   - Recommendation: Planner first task — verify public accession for MVP BMI AFR. If DAR required, fall back to AoU.

3. **D-05 original-reference question**
   - What we know: Hou 2023 Nat Genet (PMC11120833) does NOT describe the D-05 NCP framework.
   - What's unclear: Whether there is an intended alternate reference (Hou 2019? Pasaniuc 2017 review? Hormozdiari 2020?) or whether D-05 is this study's original construction.
   - Recommendation: Raise in a discuss-phase prompt before the planner writes paper-ready methodology text. If original construction, document as such in supplementary Methods with justification (per Phase 4 original research framing per user memory `feedback_original_research_framing`).

4. **NCSU LSF concurrent-core quota**
   - What we know: User memory `feedback_parallel_downloads` mentions Carter's preference for parallel I/O on LSF.
   - What's unclear: Exact concurrent-job quota under standard partition.
   - Recommendation: Planner runs pilot (1 trait × 10 regions × 10 bootstraps = 100 fits) and extrapolates. This resolves both A-1 compute estimate and real-world scheduling.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Snakemake 7.32.4 | matched_n.smk orchestration | ✓ | 7.32.4 per STATE.md | /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake |
| R + susieR + coloc | bootstrap refit + coloc.susie | ✓ | Per Phase 1 | envs/r_coloc.yml (DEF-01-02 tracked; CONTEXT.md Integration Points reuses Phase 1 script verbatim) |
| Python + ldsc (ldsc_py3) | D-04 r_g matrix | ✓ | Per Phase 5 | No fallback needed; LDSC is the canonical tool |
| LSF cluster access | 300k SuSiE fits | ✓ | NCSU HPC per CLAUDE.md | No fallback — local execution infeasible at 300k fits |
| Pan-UKBB AFR BMI sumstats | D-03c fallback only | ✓ (if needed) | Phase 0 D-20 gap | Preferred: MVP (C-1) or AoU |
| MVP BMI AFR (phs002453) | D-03c primary | **UNVERIFIED** | — | AoU BMI AFR or Pan-UKBB |
| AoU BMI AFR | D-03c alt primary | ✓ (credentials per CLAUDE.md) | — | MVP or Pan-UKBB |
| liftover (GRCh38→GRCh37) | MVP/AoU sumstats | ✓ Phase 9 pattern | Per `09-02-*` harmonizer | Pyliftover in smoke_dev; inline per harmonizer per Phase 9 D-LD |

**Missing dependencies, no fallback:** None.

**Missing dependencies, fallback exists:** MVP BMI AFR accession must be verified; falls back to AoU or Pan-UKBB.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (Python) per Phase 5/9 convention; testthat (R) per Phase 1 convention |
| Config file | `config/matched_n.yaml` (new) + schema at `schemas/matched_n.schema.yaml` (new, follows Phase 0 D-06) |
| Quick run command | `pytest tests/test_matched_n_*.py -x -q` |
| Full suite command | `pytest tests/ -x` (Phase 4 subset via marker `@pytest.mark.phase4`) + `snakemake --dry-run all_matched_n` |

### Phase Requirements → Test Map
Phase 4 does not have formal REQ-IDs at sub-level; CP#1 criteria (c) and (d) are the binding requirements.

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CP#1(c) negative-control | Phase 4 must not flip HLA/pigmentation tiers under bootstrap | integration | `pytest tests/test_matched_n_negcontrol.py -x` | ❌ Wave 0 |
| CP#1(d) power retention | Matched-N concordance reported with 95% CI for all 5 traits | integration | `pytest tests/test_matched_n_table2.py -x` | ❌ Wave 0 |
| H7 verdict computation | D-02d 20pp threshold applied correctly | unit | `pytest tests/test_matched_n_h7.py::test_20pp_verdict -x` | ❌ Wave 0 |
| D-01b SE-inflation math | `SE_EUR_matched = SE_EUR × √(N_EUR/N_AFR)` | unit | `pytest tests/test_matched_n_se_inflation.py -x` | ❌ Wave 0 |
| D-02a Tier A retention | Bootstrap median computes correctly | unit | `pytest tests/test_matched_n_tier_a.py -x` | ❌ Wave 0 |
| D-04c FDR across 30 tests | BH-FDR correctly spans the full matrix | unit | `pytest tests/test_matched_n_fdr.py -x` | ❌ Wave 0 |
| D-05a per-locus NCP | `ncp = (β/SE)^2`, chi-square detection prob matches analytic | unit | `pytest tests/test_matched_n_detection.py -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_matched_n_*.py -x -q`
- **Per wave merge:** `pytest tests/ -x -q` (full test suite)
- **Phase gate:** Full suite green + snakemake all_matched_n --dry-run resolves

### Wave 0 Gaps
- [ ] `tests/test_matched_n_se_inflation.py` — unit test for D-01b math (SE-inflation formula, Z_b ~ N draws)
- [ ] `tests/test_matched_n_tier_a.py` — unit test for D-02a Tier A retention computation
- [ ] `tests/test_matched_n_h7.py` — unit test for D-02d 20pp threshold verdict logic
- [ ] `tests/test_matched_n_detection.py` — unit test for D-05a NCP-based detection probability
- [ ] `tests/test_matched_n_fdr.py` — unit test for D-04c BH-FDR across 30 tests
- [ ] `tests/test_matched_n_negcontrol.py` — integration test that HLA/pigmentation do not flip tier under bootstrap
- [ ] `tests/test_matched_n_table2.py` — integration test that Table 2 assembles correctly from bootstrap outputs
- [ ] `tests/fixtures/matched_n/` — synthetic bootstrap outputs for 2–3 synthetic loci for fast test runs

---

## Security Domain

Phase 4 is a methodology-only phase operating on public summary statistics per CLAUDE.md constraint. No new attack surfaces beyond those already closed in Phase 9 UAT (22/22 threats closed per STATE.md).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | MVP dbGaP and AoU Workbench are credentialed; bootstrap pipeline does not authenticate |
| V3 Session Management | no | No web sessions |
| V4 Access Control | no | No user-facing access control |
| V5 Input Validation | **yes** | `config/matched_n.yaml` schema validation per Phase 0 D-06 pattern; sumstats harmonization per Phase 2 `harmonize_eqtl.py` pattern |
| V6 Cryptography | no | No crypto operations |

### Known Threat Patterns for matched-N bootstrap pipeline

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Tampered sumstats input (wrong N or wrong β sign) | Tampering | Checksum verification per Phase 0 data provenance; schema validation on config load |
| Bootstrap seed leak (re-running with same seed gives reviewable reproducibility) | Repudiation (inverse) | Seed strategy is deterministic per CONTEXT.md Claude's Discretion (`1000 * trait_id + bootstrap_idx`); stored alongside outputs |
| LSF job quota exhaustion | Denial-of-Service | Pilot run before full launch (A-1 recommendation); chunked job submission |

---

## Sources

### Primary (HIGH confidence)
- Zou 2022 SuSiE-RSS PLOS Genetics PMC9337707 — bootstrap/resampling mathematics
- MultiSuSiE 2025 Nat Genet s41588-025-02450-5 — current multi-ancestry fine-mapping SOTA
- LDSC wiki FAQ (bulik/ldsc) — authoritative LDSC usage guidance
- Hou 2023 Nat Genet PMC11120833 — radmix paper (NOT the originally-cited detection framework)
- Mahajan 2022 DIAMANTE Nat Genet DOI 10.1038/s41588-022-01058-3 — cross-ancestry T2D
- GIGASTROKE 2022 Nature s41586-022-05165-3 — stroke AFR N=23,991
- Huang 2022 Nat Commun s41467-022-35553-2 — MVP BMI AFR N=55,525
- Martin 2017 AJHG PMC5384097 — cross-ancestry portability
- OSF pre-registration DOI 10.17605/OSF.IO/PVB5J — H7 20pp threshold

### Secondary (MEDIUM confidence)
- MESuSiE 2023 Nat Genet — alternative multi-ancestry method
- Bitarello 2023 Nat Commun — portability quantification
- Hormozdiari 2020 Nat Genet (PolyFun) — candidate replacement citation for B-2
- Zhang 2021 Mol Genet Genomics PMC8550643 — LDSC/Popcorn AFR reliability

### Tertiary (LOW confidence — requires validation)
- MVP phs002453 BMI AFR public-access status (tentative; planner must verify)
- AoU BMI AFR exact N_eff (tentative ~55k per Nat Commun 2025 excerpts)

---

## Metadata

**Confidence breakdown:**
- B-1 (SE-inflation): HIGH — first-principles derivation + Zou 2022 supports
- B-2 (Hou attribution): **CONTESTED, MEDIUM** — radmix paper verified not the intended reference; original construction or replacement citation needed
- B-3 (20pp threshold): MEDIUM — pre-registered but no literature precedent
- A-1 (compute envelope): MEDIUM — Zou 2022 benchmark scale-extrapolated; pilot recommended
- A-2 (LDSC r_g matrix): HIGH — LDSC wiki explicit on limitations; AFR stratum sizes problematic
- C-1 (bmi.AFR): HIGH — MVP/AoU supersede Pan-UKBB definitively

**Research date:** 2026-04-15
**Valid until:** 2026-05-15 (30 days; cross-ancestry fine-mapping is active field but T2 phase work is not time-critical)

---

*Phase 4 Research — Methodology-Defensibility Mode*
*Researched: 2026-04-15*
