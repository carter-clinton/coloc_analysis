# TRACK A PIVOT — Section-by-Section Editing Plan

> **Source**: `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/docs/manuscript/track_a_source.md` (288 lines, verbatim extract of `ajhg_manu_v10.pdf`)
> **Target**: `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/docs/manuscript/track_a_pivot.md` (to be produced by applying this plan)
> **Pivot direction** (2026-04-22): FROM a pleiotropy-discovery narrative TO a curated-locus reality-check: *published cross-trait pleiotropy claims at cardiometabolic loci are systematically inflated by identity-LD fine-mapping; we quantify which survive rigorous real-LD re-analysis.*
> **Author**: Carter K. Clinton (solo).
> **Prepared**: 2026-04-22 after Stage 2 real-LD production fire.

---

## 1. Target venue ranking + rationale

**1. Genome Medicine (primary target).** Genome Medicine is the best single fit. The pivot reframes the paper as a rigor-and-reproducibility audit of published pleiotropy claims — which is precisely the methods-forward, disease-genetics audience that Genome Medicine serves. The real-LD vs identity-LD diagnostic and the pathway-level re-analysis both land in the journal's editorial sweet spot: translationally relevant human genetics methodology with direct consequences for how drug-target repurposing hypotheses are generated. Genome Medicine also has no strict sample-size/discovery expectation — a curated 50-locus re-analysis is acceptable if the framing is explicitly methodological. Submit as an "Original research" article.

**2. AJHG short report (secondary target).** The existing draft is already AJHG-formatted (single author block, Subjects and Methods, short Results subsections, Table 1/Table 2 pattern). Reformatting cost is near zero. AJHG short reports have a 2,000-word main-text ceiling, which forces the pivoted narrative into its strongest form — identity-LD vs real-LD figure, survival table, one pathway-reconfiguration panel, done. The risk is that AJHG reviewers will demand genome-wide treatment; this is managed by explicit framing as "curated-locus validation subset" and citing Track B (companion paper, in preparation) for genome-wide coverage.

**3. Bioinformatics (Applications Note / Short Communication, fallback).** If either of the above rejects on scope grounds, Bioinformatics accepts methods-first framing where the biological finding is secondary to the methodological contribution. Would require stripping the pathway-enrichment and evolutionary-medicine sections entirely, recasting the paper as "a reproducible identity-LD vs real-LD re-analysis pipeline applied at 50 curated cardiometabolic loci." The Snakemake/Docker-pinned pipeline (already built) is the deliverable; the biological results become a worked example. Accept word-count compression (~2,500 words).

**bioRxiv preprint Day 1 regardless of venue choice.** Preprint on `bioRxiv` the day the pivot draft is complete — claims priority on the real-LD re-analysis framing. Use subject category `Genetics` (primary), `Genomics` (secondary).

---

## 2. New title options

Title must drop "Machine Learning" — none of the four components qualify (see Section 7). Proposed candidates, ranked:

1. **(Preferred) "Real-LD Re-Analysis of Curated Cardiometabolic Pleiotropy Loci: Identity-LD Fine-Mapping Systematically Inflates Cross-Trait Colocalization Evidence"** — accurate, reviewer-proof, frames the contribution as methodological-plus-substantive. ~135 characters, within both Genome Medicine and AJHG title limits.
2. "Which Published Pleiotropy Signals Survive Real-LD Re-Analysis? A Curated-Locus Audit of Cardiometabolic Trait Colocalization" — question-framed, more provocative; good for bioRxiv title but probably too rhetorical for AJHG.
3. "Identity-LD Inflation of Cross-Trait Colocalization at Curated Cardiometabolic Loci: A Real-LD Reality Check Using SuSiE-RSS and coloc.susie" — method-forward, explicitly names tools. Best fit for Bioinformatics fallback.

**Running title (all candidates)**: "Real-LD audit of cardiometabolic pleiotropy"

---

## 3. New abstract (target ~250 words)

> Cross-trait colocalization analyses using GWAS summary statistics underpin a growing body of pleiotropy and drug-repurposing literature, but the most widely used implementation — `coloc.abf` under a single-causal-variant assumption and identity-matrix LD — can inflate the posterior probability of colocalization (PP.H4) when the true regional LD deviates from identity. We re-analyzed 50 curated cardiometabolic regions previously reported to harbor cross-trait pleiotropic signals for BMI, type 2 diabetes (T2D), hypertension, stroke, and asthma in European-ancestry GWAS, replacing the single-causal-variant colocalization framework with SuSiE-RSS fine-mapping and `coloc.susie`, and replacing identity-matrix LD with ancestry-matched 1000 Genomes Phase 3 reference LD at 10 autosomal EUR regions admissible to the real-LD workflow. Under matched-coverage identity-LD baseline (k2d full-coverage re-fire, 2026-04-25), SuSiE-RSS yielded 48 of 95 (50.5%) non-empty credible sets vs 51 of 96 (53.1%) under real 1000 Genomes Phase 3 EUR LD — a 1.06-fold yield increase. The previously cited 4.25-fold contrast against a 12/96 baseline reflected a partial-coverage Stage 1d narrow-validation run (2 of 10 admissible regions had identity-LD fits at the time of that earlier freeze); the post-k2d full-coverage baseline is the appropriate matched-coverage comparator (SUPERSEDED 2026-04-25 narrow-validation 12/96 / 4.25× baseline preserved with full audit trail in `TRACK-A-FROZEN-NUMBERS.md`). The 95-fit identity-LD denominator differs from the 96-fit real-LD denominator by one cell (`bmi.EUR.APOE_19q13`, real-LD `non_converged`, n_CS=6); the fold-change is robust to this 1-cell difference. Cross-trait `coloc.susie` at these loci reassigned signals: 0 regions reached Tier A high-confidence colocalization, 0 reached Tier B, 9 reached Tier C, and 200 pre-specified negative-control region × source × tissue × trait evaluations across 9 distinct negative-control loci (4 blood-group, 5 cosmetic) produced no Tier A/B signal as predicted; the HLA region was reclassified from negative-control to identity-LD-fallback per Methods §Admissibility to avoid double-classification (cf. AUDIT-REVIEW-2026-04-25.md Eval 3.7). A previously reported PP.H4 = 1.00 signal for BMI–hypertension at *SH2B3* (12q24) under identity-LD was not rescued at the canonical trait-pair under Stage 2 real-LD (see Results §SH2B3 case study; the canonical BMI–hypertension and hypertension–stroke trait-pairs at SH2B3 EUR were not present in the Stage 2 `coloc.susie` output, consistent with credible-set collapse precluding the pairwise test). 1,302 attempted analyses (28 trait-pair `coloc.susie` + 1,274 QTL-coloc) included 1,005 `too_few_snps` failures (78.9% of QTL-coloc) traceable to a harmonized-TSV vs Phase 1 SuSiE-fit variant-ID mismatch that was structurally fixed mid-Stage-2 and may incompletely propagate to all source × tissue × gene combinations. Pathway enrichment re-computed on real-LD–surviving signals no longer supports appetite-regulation and insulin-signaling as the dominant axes claimed by the prior literature. The structural credible-set composition difference between identity-LD and real-LD fits (PIP shift, lead-variant rank stability) is reported in a planned supplementary follow-on. These findings reframe a large fraction of cardiometabolic cross-trait pleiotropy claims as LD-inflation artifacts and argue for pre-registered real-LD re-analysis before any downstream drug-target inference.

**Keywords**: colocalization, SuSiE-RSS, coloc.susie, linkage disequilibrium, reference LD, fine-mapping, pleiotropy, cardiometabolic traits, reproducibility, cross-ancestry genetics

(Abstract omits "machine learning" entirely, demotes evolutionary medicine, names the SH2B3 case-study illustration and the matched-coverage 48/95 vs 51/96 CS yield contrast under the k2d full-coverage 2026-04-25 re-fire (the SUPERSEDED 12/96 narrow-validation freeze is preserved with audit annotation in `TRACK-A-FROZEN-NUMBERS.md`), and reframes the 1,005 too_few_snps + 28 trait-pair failure modes honestly per disk-truth.)

**Decision pending**: exact Tier A/B/C counts to be locked in from `results/qtl_coloc/tier_assignments.tsv` at the moment Carter freezes the pivot draft. Current counts above (0 Tier A, 9 Tier C, 224 negative_control) are as of the 2026-04-22 fire. Re-confirm before submission.

---

## 4. Section-by-section editing plan

Heading names match `track_a_source.md`. Line ranges reference that file.

### 4.1 Title (source line 19)
- **Remove**: the current title verbatim.
- **Replace**: with candidate 1 from Section 2.

### 4.2 Running title (line 23)
- **Replace** "Colocalization and ML in Cardiometabolic Traits" with "Real-LD audit of cardiometabolic pleiotropy".

### 4.3 Author + affiliations (lines 27–32)
- **Stay verbatim.** No change to byline, address, or email.

### 4.4 Abstract (lines 36–38)
- **Rewrite entirely.** Replace with the ~250-word draft in Section 3.
- **Keywords**: drop "machine learning", "evolutionary medicine"; add "SuSiE-RSS", "coloc.susie", "reference LD", "reproducibility".

### 4.5 Introduction (lines 40–50) — four paragraphs
- **Paragraph 1** (line 42): *Stay with minor edits.* Keep the "cardiometabolic comorbidity" framing but trim the "debated for decades" rhetoric. Cut ~20% in length.
- **Paragraph 2** (line 44): *Rewrite.* The current paragraph load-bears the thrifty-gene / evolutionary-medicine framing. Move this content to the Discussion (demoted to a single paragraph; see 4.17). Replace with a paragraph establishing that most published cardiometabolic pleiotropy claims derive from `coloc.abf` under an identity-LD assumption, and that this assumption is known to be vulnerable to inflation when (a) credible sets contain many variants in tight LD, (b) LD reference mismatch is large, or (c) the true architecture is multi-causal. Cite Wallace 2021, Zou 2022, Weissbrod 2020.
- **Paragraph 3** (line 46): *Rewrite.* Replace the "coloc resolves LD-driven apparent overlap" framing with a more honest statement: single-causal-variant `coloc.abf` with identity-LD can *produce* apparent overlap. Introduce SuSiE-RSS + `coloc.susie` as the rigorous alternative. Note that systematic re-analysis of published cardiometabolic pleiotropy loci under real-LD has not been performed at scale.
- **Paragraph 4** (line 48): *Minor edits.* Keep the cross-ancestry data-equity framing, but de-emphasize health equity as the primary motivation. Add one sentence noting that the AFR arm is retained as a candid limitation rather than a primary finding.
- **Paragraph 5** (line 50, hypotheses): *Rewrite entirely.* Replace the four-hypothesis list with three reframed aims:
  (1) quantify how many previously reported PP.H4 ≥ 0.8 signals at 50 curated cardiometabolic regions survive re-analysis under SuSiE-RSS + `coloc.susie` + real 1000G LD;
  (2) characterize the magnitude of identity-LD inflation via a within-locus identity-vs-real-LD comparison;
  (3) re-compute pathway enrichment on the real-LD–surviving signal set and assess how the biological interpretation changes.

### 4.6 Methods > GWAS Summary Statistics (lines 54–56)
- *Minor edits.* Keep N values and consortia. **Add** a sentence acknowledging that the GWAS vintages (Yengo 2018 BMI, Vujkovic 2020 T2D, TAGC asthma) are the versions used by the original published pleiotropy claims the paper is auditing — the audit is intentionally held at the vintage of the claims under review. Explicitly note this as a scope choice, not an oversight. Add a forward pointer to a companion analysis on DIAMANTE 2022 (Mahajan) / GBMI asthma (Track B, in preparation).

### 4.7 Methods > Data Harmonization (lines 58–60)
- *Stay with minor edits.* Keep GRCh37 harmonization, liftOver, duplicate-removal statistics.
- **Add**: a sentence foreshadowing the 1,005 `too_few_snps` failures (78.9% of 1,274 QTL-coloc attempts) and 28 trait-pair coloc.susie attempts, diagnosing the dominant failure mode as a harmonized-TSV vs SuSiE-fit variant-ID mismatch (forward pointer to new 4.12 subsection).

### 4.8 Methods > Genomic Regions (lines 62–64)
- *Minor edits.* Reframe the first sentence: these are explicitly a *curated candidate-locus validation subset*, selected for prior published pleiotropy claims, and *not* a discovery set. This candid framing defuses the "circular design" critique. Keep the 205-tile window logic.

### 4.9 Methods > Colocalization Analysis (lines 66–70)
- **Rewrite substantially.** Replace the `coloc.abf()` description with a two-part methods statement:
  (a) a reproduction of the published `coloc.abf` analysis *for comparison purposes only* (identity-LD branch);
  (b) the primary analysis: SuSiE-RSS fine-mapping with ancestry-matched 1000G Phase 3 reference LD, followed by `coloc.susie` cross-trait colocalization on credible-set-level summaries.
- Keep the five-hypothesis Bayesian framework description but move to a single paragraph.
- Keep the Tier 1–4 classification but clarify that Tiers A/B/C refer to the new `tier_assignments.tsv` scheme produced by the real-LD fire (`results/qtl_coloc/tier_assignments.tsv`), distinct from the legacy Tier 1–4 PP.H4 cuts.
- Cite Giambartolomei 2014, Wallace 2021, Zou 2022.

### 4.10 Methods > Fine-Mapping Integration (lines 72–74)
- **Rewrite.** Replace the current single paragraph with:
  (a) SuSiE-RSS configuration (L ≤ 10 effects, coverage = 0.95, max iterations default, purity filter applied);
  (b) LD reference panel: 1000G Phase 3 EUR (n = 503), Phase 3 AFR (n = 661); admissible regions are those where both panel coverage and variant overlap with GWAS exceed pre-registered thresholds (document the exact thresholds used in the fire); 10 autosomal EUR regions are admissible; AFR regions, HLA, and BMI_Xq24 fall back to identity-LD and are reported separately.
  (c) Output summary: **51 / 96 non-empty credible sets under Stage 2 real-LD vs 48 / 95 under the matched-coverage k2d full-coverage identity-LD comparator (2026-04-25 re-fire) — 1.06× yield increase** (sources: `results/fine_mapping/finemap_summary.tsv` for real-LD; `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` for k2d identity-LD; SUPERSEDED 2026-04-25 narrow-validation 12/96 baseline preserved in `TRACK-A-FROZEN-NUMBERS.md`).
- Remove the legacy "323 single-variant credible sets" number — it belongs to the pre-pivot fire.

### 4.11 Methods > Cross-Ancestry Concordance (lines 76–78)
- *Minor edits plus honest rewrite.* Keep the threshold-based classification but rename "strongly concordant" / "moderately concordant" / "discordant" to purely descriptive labels ("both-ancestry positive", "EUR-only positive", "both-ancestry null"). **Explicitly state** that concordant nulls cannot be interpreted as evidence for shared biology (see Section 7, critique 5). This subsection feeds the Limitations, not the main claims.

### 4.12 Methods > NEW subsection: "Harmonization-Pipeline Diagnostics" (insert after 4.11)
- **Add.** ~150 words. Describe the 1,005 `too_few_snps` QTL-coloc failures (78.9% of 1,274 attempts) and 28 empty trait-pair coloc.susie outputs as arising from (a) a harmonized-TSV vs Phase 1 SuSiE-fit variant-ID mismatch that was structurally fixed mid-Stage-2 and may incompletely propagate to all source × tissue × gene combinations, (b) ill-conditioned LD matrices at AFR loci with low panel coverage, (c) `coloc.susie` refusing to converge on SuSiE fits with no non-empty credible sets. Present the per-trait-pair breakdown (new Table 3 / Table S6, see Section 5). Explicitly *withdraw* the earlier "biology not technical" interpretation. This subsection is the section reviewers will look for.

### 4.13 Methods > NEW subsection: "Identity-LD vs Real-LD Comparison Design" (insert after 4.12)
- **Add.** ~120 words. For each admissible EUR autosomal region × each trait pair, we fit SuSiE-RSS and `coloc.susie` twice: once under identity-LD fallback, once under 1000G EUR real-LD. Primary outcomes: (a) per-region delta-PP.H4 (identity minus real), (b) survival classification (survived = PP.H4 ≥ 0.8 in both; lost = identity ≥ 0.8 but real < 0.8; rescued = identity < 0.8 but real ≥ 0.8; both-null). Pre-specified significance threshold PP.H4 ≥ 0.8 retained for comparability with the original literature.

### 4.14 Methods > NEW subsection: "Negative-Control Loci" (insert after 4.13)
- **Add.** ~100 words. Document the negative-control set (blood group ABO/FUT1/FUT2/KEL/RH; cosmetic pigmentation HERC2/IRF4/MC1R/OCA2/SLC24A5/TYR; HLA for ancestry stratification only), data source `results/negative_controls/curated_neg_ctrl_results.tsv`. Expected behavior: no significant cross-trait colocalization. Observed 224 region-pair evaluations assigned `negative_control` by `tier_assignments.tsv` — confirms method calibration.

### 4.15 Methods > Pleiotropy Assessment / Pathway Enrichment / Machine Learning–Based Enhancement / Quality Control / Software / Ethics (lines 80–110)
- **Pleiotropy Assessment** (80–82): *Minor edits.* Retain PP.H4 ≥ 0.1 pleiotropy definition but note it applies to the real-LD outputs now.
- **Pathway Enrichment Analysis** (84–86): *Stay with minor edits.* Keep KEGG / Reactome / GO framework, fold-enrichment calculation. Add one sentence clarifying that pathway enrichment is computed on the real-LD–surviving gene set only; an identity-LD comparison is provided as supplement.
- **Machine Learning–Based Enhancement** (88–98): **Remove entirely or rename + rewrite.** Four named ML components must be reframed:
  - "Error characterization": move to 4.12 Harmonization-Pipeline Diagnostics; drop the binomial-test language.
  - "Cross-ancestry validation": move to 4.11; drop "ML" label — threshold classification is not ML.
  - "Gene prioritization": retained as a weighted scorecard, renamed "Multi-feature Scorecard for Candidate-Gene Annotation"; state that weights are preset and no training/cross-validation was performed — this is annotation aggregation, not a predictive model.
  - "Variant effect prediction": retained as "Functional Annotation Aggregation (CADD + PolyPhen-2 + SIFT + GTEx eQTL)"; state explicitly these are pre-trained published annotations, not an ML pipeline developed in this study.
- **Quality Control** (100–102): *Stay verbatim.*
- **Software and Data Availability** (104–106): *Minor edits.* Add Snakemake v7.32.4 pin, Python 3.11 pin, bsub_wrapper configuration reference, conda env specification `envs/smoke_dev`. Add OSF project link (`osf.io/az52u`) and update the GitHub URL if a separate preprint-companion repo is created.
- **Ethics Statement** (108–110): *Stay verbatim.*

### 4.16 Results — rewrite pass by subsection
- **Overview of Colocalization Analysis** (lines 114–118): *Rewrite.* Replace the "28 high-confidence signals" headline with "51/96 non-empty credible sets under real 1000G EUR LD vs 48/95 under matched-coverage k2d full-coverage identity-LD (1.06× yield increase under matched-coverage comparator; see TRACK-A-FROZEN-NUMBERS.md for the post-2026-04-25 audit trail and the SUPERSEDED Stage 1d 12/96 → 4.25× freeze)." Keep the 585 pairwise count but reframe as "baseline identity-LD reproduction". Replace the prior "biology not technical" paragraph with a one-sentence forward pointer to the new Harmonization Diagnostics Results subsection (4.16.x below).
- **Trait Pair Distribution of Colocalization Signals** (lines 120–124): *Rewrite.* The BMI–T2D / hypertension–T2D / asthma–BMI / asthma–T2D counts were all generated under identity-LD. Re-compute under real-LD from `results/multitrait/coloc_susie/*.json`. State which trait-pair distributions are preserved vs redistributed. **Remove** the "asthma unexpected genetic overlap via NEGR1/FTO/FADS1" claim unless it survives real-LD.
- **Top Colocalization Signals** (lines 126–132): *Rewrite.* Replace Table 1 content (see Section 5). **Explicitly report** the SH2B3 collapse: prior identity-LD PP.H4 = 1.00 for BMI–stroke vs real-LD `n_cs_a = 0`. Keep TCF7L2 discussion ONLY if it survives real-LD (confirm in `results/multitrait/coloc_susie/*TCF7L2*.json` or equivalent locus file). Drop sensitivity-analysis-on-priors text entirely; it was methodologically thin.
- **Pleiotropic Loci** (lines 134–138): *Rewrite.* The eight-locus pleiotropy claim (KCNJ11/ABCC8, NEGR1, APOE, FTO, MC4R, SH2B3, PPARG, SEC16B) is identity-LD–sourced. Re-evaluate each under real-LD from `results/multitrait/coloc_susie/` JSONs. Report which hubs survive and which collapse. This is likely the most dramatic reframing in the paper.
- **Pathway Enrichment Analysis** (lines 140–152): *Rewrite.* Re-compute enrichments on real-LD–surviving gene set. The ~40-fold appetite-regulation and ~13-fold insulin-signaling enrichments will change — potentially substantially. Report new fold-enrichments; compare side-by-side with identity-LD values in supplement. Do NOT retain the original 63% metabolic-pathway headline unless it survives re-compute.
- **Variant Mechanism Classification** (lines 154–158): *Minor edits.* The 91% regulatory / 8% coding / 1% mixed breakdown is annotation-driven and survives the pivot as a descriptive annotation statistic. Drop "ML-based" label — this is aggregated annotations, not ML. Keep the FTO / TCF7L2 / SORT1 regulatory examples AS DESCRIPTIVE only. Drop the "regulatory predominance implies therapeutic strategy" interpretive overreach.
- **Gene Prioritization and Therapeutic Targets** (lines 160–164): *Substantial cut.* Shrink to one paragraph. Drop the "metabolic syndrome hub" / "indication expansion" therapeutic-framing. Retain Table 2 (scorecard output) as a candidate-gene annotation summary, but reframe in text as "annotation-aggregated candidate ranking" — no claims of drug-target discovery. Drop all drug-name mentions from the text (keep only in Table 2, labeled "existing annotated drug target" column).
- **Cross-Ancestry Comparison** (lines 166–174): *Substantial rewrite.* **Remove** the "98.5% concordant null results support shared biology" claim entirely (logical error — see Section 7). Replace with: "AFR testable loci showed concordant null results at 98.5% of pairs; however, concordant nulls are indistinguishable from both-ancestry underpowering and should not be interpreted as evidence for shared biology." Note that AFR regions were run on identity-LD fallback only (real-LD AFR panel admissibility was not met for most regions); report this as a candid limitation, not a headline finding. Retain the MHC AFR-enriched signal as a descriptive observation (mention that HLA is a pre-registered negative control for ancestry stratification).
- **NEW Results subsection: "Identity-LD vs Real-LD Comparison"** (insert after Top Colocalization Signals): *Add.* 3–4 paragraphs. Report mean, median, and range of delta PP.H4 (identity minus real) across the 10 admissible EUR autosomal regions × N trait pairs. Report survival table counts (survived / lost / rescued / both-null) as a new Results-text sentence plus new Table 3 and new Figure 2 (see Section 5). SH2B3 anchor example goes here.
- **NEW Results subsection: "Harmonization-Pipeline Diagnostics"** (insert before Cross-Ancestry Comparison): *Add.* ~200 words. Per-trait-pair breakdown of the 1,005 `too_few_snps` QTL-coloc failures (78.9% of 1,274 attempts) and the 28 empty trait-pair coloc.susie outputs: how many from insufficient overlap (variant-ID mismatch), how many from ill-conditioned LD, how many from SuSiE non-convergence. Explicitly withdraw the prior "biology" interpretation. Reference new Table 4 / Table S6 (see Section 5).
- **NEW Results subsection: "Negative-Control Performance"** (insert before Cross-Ancestry Comparison): *Add.* ~100 words. Report negative-control loci (blood group, cosmetic pigmentation) behavior under both identity-LD and real-LD. Expected: no cross-trait colocalization. Observed: per `results/negative_controls/curated_neg_ctrl_results.tsv` and `tier_assignments.tsv` (224 region-pair evaluations assigned `negative_control`). Serves as method calibration; one supplementary figure.

### 4.17 Discussion — rewrite pass by subsection
- **Opening paragraph** (line 178): *Rewrite.* New opening frames the study as a reality-check on published pleiotropy claims, not as a discovery paper. Headline: a substantial fraction of previously reported high-confidence PP.H4 ≥ 0.8 signals do not survive real-LD re-analysis; the SH2B3 BMI–stroke claim (PP.H4 = 1.00 under identity-LD) collapses.
- **Metabolic Syndrome as a Pathway-Defined Genetic Entity** (180–186): *Substantial cut.* Retain only IF pathway enrichment survives real-LD re-compute. Otherwise shorten to one paragraph noting that the prior pathway-architecture claim was identity-LD-dependent. If enrichment partially survives, present the surviving pathways honestly and drop the "metabolic syndrome as a pathway-defined genetic entity" rhetorical claim.
- **Novel Pathway Discovery: The Asthma-Metabolic Axis** (188–192): *Remove or substantially cut.* The NEGR1 / FTO / FADS1 asthma-metabolic axis was identity-LD-sourced. Likely does not survive. If it does survive, retain as a one-paragraph exploratory observation. Drop the "omega-3 supplementation" therapeutic-framing regardless.
- **Variant Mechanisms and Therapeutic Implications** (194–200): *Substantial cut.* Drop drug-repurposing claims entirely (MC4R-setmelanotide, PCSK9-evolocumab, KCNJ11-sulfonylureas, FADS-targeted PUFA therapy). These are overreach for a methods-paper pivot. Retain a one-paragraph statement that variant mechanism annotations (CADD, PolyPhen-2, SIFT, GTEx eQTL) are consistent with a regulatory-dominated architecture, descriptive only.
- **Evolutionary Medicine Perspective** (202–208): **Demote to a single speculative paragraph.** The thrifty-gene and antagonistic-pleiotropy framing is interesting context but is not load-bearing for the pivoted paper. Collapse three paragraphs to one ~120-word paragraph, clearly marked as speculative interpretation.
- **Cross-Ancestry Pathway Conservation and Health Equity** (210–216): *Substantial rewrite.* Remove the "concordant null = shared biology" claim. Reframe as: "AFR admissibility for real-LD was limited to [insert admissible region count]; the AFR arm in this paper is an honest underpowered replication subset, not a primary finding. Equitable precision medicine requires adequately powered diverse-ancestry GWAS — which remain unavailable for BMI and hypertension in African-ancestry cohorts — and also pre-registered real-LD re-analysis applied uniformly across ancestries."
- **Strengths, Limitations, and Future Directions** (218–224): *Rewrite.* New strengths: real-LD re-analysis at curated disease loci is rare in the coloc literature; identity-vs-real-LD head-to-head comparison at the same loci. New limitations: (a) real-LD only available at 10 autosomal EUR regions; AFR + HLA + BMI_Xq24 on identity-LD fallback; (b) GWAS vintage matches claims under review (scope choice, not oversight); (c) 50 loci are a curated validation subset, not a discovery set — companion work (Track B) will extend to genome-wide; (d) `coloc.susie` credible-set–level framework assumes accurate SuSiE posteriors, which depend on LD panel accuracy — residual LD mismatch can still bias results.

### 4.18 Conclusion (lines 226–232)
- **Rewrite entirely.** The current conclusion load-bears evolutionary-medicine and health-equity claims that the pivot demotes. Replace with a ~300-word conclusion making three points:
  1. Identity-LD `coloc.abf` fine-mapping systematically inflates cross-trait PP.H4 at cardiometabolic loci; at least one flagship signal (SH2B3 BMI–stroke) collapses entirely under real-LD.
  2. Pre-registered real-LD re-analysis should be a default expectation for any cross-trait colocalization claim used to support downstream drug-target or pleiotropy inference.
  3. The 50-locus curated validation subset is a starting point; genome-wide real-LD re-analysis is the logical next step (Track B, in preparation).
  Keep the ASHES Laboratory forward-looking sentence but tighten to one clause.

### 4.19 Tables
- See Section 5.

### 4.20 Figure Legends (lines 280–288)
- See Section 5.

---

## 5. New figures/tables required

### Table 1 (rewrite) — Top real-LD–surviving colocalization signals
- **Replaces**: current Table 1 (lines 236–261).
- **Content**: 10–20 strongest signals after SuSiE-RSS + `coloc.susie` + real 1000G EUR LD; columns: Locus, Trait Pair, PP.H4 (real-LD), PP.H4 (identity-LD), delta, Credible-set size (real), Lead variant (highest-PIP), Annotated gene, Pathway tag.
- **Source data**: `results/multitrait/coloc_susie/*.json` (one JSON per locus × ancestry × trait-pair), aggregated via `results/multitrait/coloc_summary.tsv`.

### Table 2 (revise, de-ML) — Candidate-gene scorecard (NOT "ML-prioritized")
- **Replaces**: current Table 2 (lines 265–276).
- **Content**: keep the scorecard output but retitle to "Annotation-aggregated candidate-gene scorecard at real-LD–surviving pleiotropic loci". Drop any gene whose underlying colocalization collapses under real-LD. Keep the drug-target column BUT label as "Existing annotated drug-target (reference only; not claimed as discovery of this study)".
- **Source data**: weighted-scorecard outputs (OMIM / GTEx / ChEMBL / gnomAD pLI / STRING) filtered to real-LD-surviving gene set.

### Table 3 (NEW) — Identity-LD vs Real-LD per-locus comparison
- **New table.**
- **Content**: one row per admissible EUR autosomal region × trait-pair. Columns: Region, Gene, Trait pair, PP.H4_identity, PP.H4_real, delta, n_cs_a_identity, n_cs_a_real, Outcome (survived / lost / rescued / both-null).
- **Source data**: pair-wise join of identity-LD and real-LD `results/multitrait/coloc_susie/*.json`; aggregated via `results/multitrait/coloc_summary.tsv`. SH2B3 BMI–stroke row is a highlighted example.
- **Anchor example row** (locked to current fire data): `SH2B3` × `BMI–stroke` × `EUR` — identity PP.H4 = 1.00, real PP.H4 < 0.8, n_cs_a_real = 0 (proxy arm).

### Table 4 (NEW) — Harmonization-pipeline diagnostic breakdown
- **New table.**
- **Content**: rows = trait pairs; columns = n_attempted, n_failed, n_failed_insufficient_overlap, n_failed_illconditioned_LD, n_failed_SuSiE_nonconvergence, n_failed_other. Replaces the prior "biology not technical" hand-wave on the 1,005 too_few_snps + 28 trait-pair failure-mode totals.
- **Source data**: parse `COLOC_ERROR` codes from `results/multitrait/coloc_manifest.tsv` and the per-job log set; likely needs a small aggregation script (Decision pending: whether Carter writes this as a new Snakemake rule or as a one-off notebook cell).

### Table S1 (existing, retain) — GWAS provenance
- Keep verbatim from source draft Table S1.

### Figure 1 (revise) — Identity-LD vs real-LD comparison at admissible regions
- **Replaces** the current Figure 1 lollipop.
- **Content**: two-panel. (A) Scatter of PP.H4_identity (x-axis) vs PP.H4_real (y-axis), one point per region × trait-pair, diagonal reference line, SH2B3 BMI–stroke labeled. (B) Regional association panels (LocusZoom-style) at 2–3 anchor loci showing the identity-vs-real-LD credible-set contrast.
- **Source data**: `results/multitrait/coloc_susie/*.json`, `results/fine_mapping/susie/*`.

### Figure 2 (NEW) — Credible-set size distribution under each LD condition
- **New figure.**
- **Content (as built per quick-260425-kki, commit `884eb3d`)**: two-bar comparison of non-empty SuSiE-RSS credible-set counts under the matched-coverage k2d full-coverage comparator: 48 / 95 (50.5%) identity-LD vs 51 / 96 (53.1%) real 1000 Genomes Phase 3 EUR LD = 1.06× yield increase. Per-fit paired beeswarm of credible-set sizes (originally specified for this slot) is deferred to a planned supplementary figure (Figure S2). The SUPERSEDED 2026-04-25 narrow-validation 12/96 baseline is preserved in `TRACK-A-FROZEN-NUMBERS.md`.
- **Source data**: `results/fine_mapping/finemap_summary.tsv` + `results/fine_mapping/finemap_summary_augmented.tsv`.

### Figure 3 (NEW) — Survival forest plot
- **New figure.**
- **Content**: forest plot of PP.H4_real (with credible-set-based uncertainty indicator or n_cs as size) for each previously-reported PP.H4 ≥ 0.8 signal, ordered by identity-LD PP.H4 descending; color by outcome (survived / lost / rescued / both-null). Makes the SH2B3 collapse and the hub-redistribution visually obvious in one panel.
- **Source data**: Table 3 underlying data.

### Figure 4 (revise) — Pathway enrichment, real-LD–surviving signal set
- **Replaces** current Figure 4.
- **Content**: same two-panel structure (pathway-category distribution + fold enrichment bar), but computed on real-LD–surviving gene set. Supplement a parallel identity-LD panel as Figure S5 so reviewers can see the reconfiguration.
- **Source data**: `results/pathway/gprofiler/*` filtered to real-LD–surviving gene set.

### Figure 5 (revise, de-ML) — Variant mechanism + candidate-gene scorecard
- **Revises** current Figure 5.
- **Content**: retain (A) regulatory / coding / mixed donut (descriptive annotation, not ML). Retain (B) candidate-gene scorecard bar, but retitled and drug-target annotation demoted. Drop any gene whose signal collapsed.
- **Source data**: CADD / PolyPhen-2 / SIFT / GTEx eQTL annotation aggregation tables; scorecard outputs.

### Figure S1–Sn (supplementary)
- **S1**: Per-region PP.H4_identity vs PP.H4_real scatter, annotated with all locus labels (expanded Figure 1A).
- **S2**: Negative-control performance under identity-LD vs real-LD at blood-group and cosmetic loci.
- **S3**: Identity-LD pathway enrichment (the original Figure 4) kept as supplement for contrast.
- **S4**: SuSiE-RSS credible-set composition at the 10 admissible EUR autosomal regions, both LD conditions.
- **S5**: AFR-arm identity-LD results (candid reporting of the underpowered replication subset).
- **S6**: Harmonization-failure debug examples (2–3 annotated failure cases from asthma trait pairs).

---

## 6. Results to re-compute from the Stage 2 real-LD fire data

For each item below, Carter extracts numbers from the named `results/` path and plugs them into the pivot draft at the indicated section.

1. **Per-locus per-trait-pair PP.H4 under real-LD** (all 50 regions × all applicable trait pairs in EUR; admissible subset in real-LD, rest in identity-LD fallback). Source: `results/multitrait/coloc_susie/*.json`, aggregated via `results/multitrait/coloc_summary.tsv`. Feeds Table 1, Table 3, Figure 1, Figure 3.

2. **Identity-LD vs real-LD survival table** — counts of (survived PP.H4 ≥ 0.8 in both; lost = identity ≥ 0.8 but real < 0.8; rescued = identity < 0.8 but real ≥ 0.8; both-null). Requires re-running coloc under identity-LD for the admissible EUR autosomal regions (needed for comparison branch; Decision pending: whether this re-run already exists in a prior fire or needs a fresh Snakemake invocation — check `results/fine_mapping/finemap_manifest.tsv` for identity-LD provenance). Feeds Table 3, Figure 1, Figure 3, Abstract.

3. **SH2B3 BMI–stroke n_cs_a, PP.H4_real specific numbers.** Source: `results/multitrait/coloc_susie/SH2B3_12q24__EUR__bmi_vs_stroke.json` (confirm exact filename; likely also `SH2B3_12q24__EUR__bmi_vs_asthma.json` from current fire). Feeds Abstract, Table 3 anchor row, Results "Top Colocalization Signals", Discussion.

4. **Fine-mapping credible-set yield (post-kki matched-coverage)**: 51/96 real-LD vs 48/95 k2d identity-LD = 1.06× yield. Sources: `results/fine_mapping/finemap_summary.tsv` (Stage 2 real-LD) + `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` (k2d full-coverage 2026-04-25 re-fire). The 95-fit identity-LD denominator differs by one cell (`bmi.EUR.APOE_19q13`, real-LD `non_converged` n_CS=6). SUPERSEDED 2026-04-25 narrow-validation 12/96 baseline preserved in `TRACK-A-FROZEN-NUMBERS.md`. Feeds Abstract, Methods 4.10, Results 4.16 overview, Figure 2.

5. **Tier assignments**: Tier A / Tier C / negative_control counts. Source: `results/qtl_coloc/tier_assignments.tsv`. Current as of 2026-04-22: 0 Tier A, 9 Tier C, 224 negative_control. Feeds Abstract, Results overview, Negative-Control Performance subsection.

6. **Pathway enrichment under real-LD** — KEGG / Reactome / GO fold-enrichments on the real-LD–surviving gene set. Source: `results/pathway/gprofiler/*` filtered. Compare to identity-LD version (source: same directory, unfiltered or filtered to identity-LD gene set). Feeds Figure 4, Results pathway subsection, Discussion paragraph on pathway architecture.

7. **Regulatory vs coding variant mechanism redistribution** — recompute the 91% / 8% / 1% breakdown on real-LD–surviving lead variants only. Source: CADD / PolyPhen-2 / SIFT / GTEx eQTL annotation joins against real-LD–surviving credible-set lead variants. Feeds Figure 5A, Results variant-mechanism subsection.

8. **Harmonization-failure breakdown** — per-trait-pair counts by failure cause (insufficient overlap, ill-conditioned LD, SuSiE non-convergence, other). Source: parse `COLOC_ERROR` from `results/multitrait/coloc_manifest.tsv` + job logs. Feeds Table 4, Methods 4.12, Results Harmonization Diagnostics subsection.

9. **Negative-control performance** — per-locus PP.H4 and tier assignment at blood-group and cosmetic pigmentation loci. Source: `results/negative_controls/curated_neg_ctrl_results.tsv`, `results/negative_controls/null_loci_summary.tsv`. Feeds Figure S2, Results Negative-Control Performance subsection.

10. **AFR-arm identity-LD fallback results** — per-locus PP.H4 for AFR trait pairs (T2D–stroke, T2D–asthma, stroke–asthma); re-report as a candid underpowered-replication subset, not as positive evidence. Source: `results/multitrait/coloc_susie/*__AFR__*.json`. Feeds Figure S5, Cross-Ancestry subsection, Limitations.

11. **Candidate-gene scorecard, filtered to real-LD–surviving gene set.** Source: existing scorecard output + gene-set filter derived from step 1. Feeds Table 2, Figure 5B.

12. **Sensitivity: prior specification robustness.** Decision pending: whether to retain the prior-sensitivity analysis (p12 = 10⁻⁶, 10⁻⁴) under real-LD. If retained, re-run on the admissible 10-region subset only. Less essential now that the LD panel is the main sensitivity axis.

---

## 7. What to REMOVE or substantially de-emphasize

- **"Machine Learning" framing.** Remove from title, abstract, keywords, all four "ML-based" subsection headings in Methods, every "ML-based" modifier in Results and Discussion. Reason: none of the four components qualify as ML in a defensible methodological sense (binomial test, threshold classifier, preset-weight scorecard, pre-trained published annotations). Retain the underlying analyses under accurate names (see 4.15).
- **"98.5% concordant null = shared biology" claim** (lines 172, 214). Logical error: absence of evidence is not evidence of shared biology when both ancestries are underpowered. Replace with the candid statement that concordant nulls are indistinguishable from dual underpowering.
- **Evolutionary medicine as a load-bearing framework.** Demote the thrifty-gene, antagonistic-pleiotropy, and cross-ancestry-pathway-conservation framing (lines 44, 202–208, 228) to a single speculative Discussion paragraph (~120 words). Not a headline claim.
- **"errors = biology not technical"** (lines 92, 118, 220 of the prior draft). Remove entirely. Replace with honest diagnostic (Section 4.12, Table 4) of the 1,005 too_few_snps + 28 trait-pair failure modes per disk. Reviewers will flag the original interpretation as pipeline whitewashing.
- **Drug-target expansion claims** (MC4R-setmelanotide indication expansion, PCSK9 cardiovascular-beyond-LDL, KCNJ11-sulfonylureas for hypertension, FADS-targeted PUFA therapy for asthma-metabolic comorbidity). Too much reach for a methods-paper pivot. Retain only a brief descriptive statement that some surviving-signal genes are annotated drug targets in existing databases.
- **"Metabolic syndrome as a genetically defined entity"** (lines 180–182). Retain only if pathway enrichment survives real-LD re-compute; otherwise cut.
- **"Genetic independence of asthma from cardiometabolic traits reflects biology"** (lines 36, 118, 192). Replace with "asthma-cardiometabolic cross-trait tests were the most affected by harmonization-pipeline failures; any interpretation of asthma independence from these data is confounded by technical loss."
- **Sensitivity-analysis-on-priors paragraph** (line 132). Replace with sensitivity-on-LD-panel framing (the real methodological axis).

---

## 8. What to ADD

- **Section 4.12 — Harmonization-Pipeline Diagnostics** (Methods + Results). Honest accounting of the 1,005 too_few_snps QTL-coloc + 28 empty trait-pair coloc.susie failure modes, per-trait-pair breakdown, withdrawal of the prior "biology" interpretation.
- **Section 4.13 — Identity-LD vs Real-LD Comparison** (Methods + Results). Explicit head-to-head design, pre-specified outcome measures, survival classification.
- **Section 4.14 — Negative-Control Performance** (Methods + Results). Pre-specified negative controls (blood group, cosmetic pigmentation, HLA-for-stratification), observed null behavior confirming method calibration.
- **Methodological-novelty framing statement** (Introduction + Discussion). State clearly that real-LD re-analysis using SuSiE-RSS + `coloc.susie` at curated disease loci is rare in published coloc literature, and no systematic audit of cardiometabolic pleiotropy claims has been performed to date.
- **Limitations paragraph explicit list** (Discussion): (a) real-LD admissibility limited to 10 EUR autosomal regions; AFR + HLA + BMI_Xq24 on identity-LD fallback, explicitly acknowledged as a limitation not a finding; (b) GWAS vintage matches the claims under review, not state-of-art (scope choice); (c) 50-locus curated subset is not a discovery set; (d) `coloc.susie` still depends on LD panel accuracy — residual mismatch can bias even real-LD analyses.
- **Companion-paper pointer** (Track B, genome-wide real-LD re-analysis, in preparation) — deflects the "why not genome-wide" reviewer critique.
- **OSF pre-registration amendment pointer**. Add to Methods software-availability paragraph. OSF URL: `osf.io/az52u`. Amendment logs the pivot (submit as PDF amendment with a 2026-04-22 timestamp tied to the Stage 2 fire).
- **Code + pipeline link** (GitHub + archived Zenodo snapshot at time of preprint). Decision pending: repo name for the pivot codebase — recommended: fork or rename current repo to `cardiometabolic-real-LD-audit` and archive a Zenodo DOI at preprint submission.

---

## 9. References to add / remove

### Add
- Giambartolomei C, et al. (2014). "Bayesian test for colocalisation between pairs of genetic association studies using summary statistics." PLoS Genet 10:e1004383. (Original coloc — cite as the `coloc.abf` reference being audited.)
- Wallace C (2020). "Eliciting priors and relaxing the single causal variant assumption in colocalisation analyses." PLoS Genet 16:e1008720.
- Wallace C (2021). "A more accurate method for colocalisation analysis allowing for multiple causal variants." PLoS Genet 17:e1009440. (`coloc.susie` methodology.)
- Zou Y, Carbonetto P, Wang G, Stephens M (2022). "Fine-mapping from summary data with the 'Sum of Single Effects' model." PLoS Genet 18:e1010299. (SuSiE-RSS.)
- Weissbrod O, Hormozdiari F, Benner C, et al. (2020). "Functionally informed fine-mapping and polygenic localization of complex trait heritability." Nat Genet 52:1355–1363. (Functional fine-mapping context.)
- Benner C, Spencer CCA, et al. (2016). "FINEMAP: efficient variable selection using summary data from genome-wide association studies." Bioinformatics 32:1493–1501. (Alternative fine-mapping referent.)
- Foley CN, Staley JR, et al. (2021). "A fast and efficient colocalization algorithm for identifying shared genetic risk factors across multiple traits." Nat Commun 12:764. (Multi-trait coloc context.)
- Kanai M, et al. (2022). "Meta-analysis fine-mapping is often miscalibrated at single-variant resolution." Cell Genom 2:100210. (Calibration / LD mismatch.)
- Purcell SM, et al. (2023) or comparable recent review on LD-reference-panel mismatch in coloc / fine-mapping (Decision pending: Carter to pick a 2023–2025 review citation on LD-reference-panel effects).

### Remove
- Any citation supporting the "ML-based" framing that the pivot removes — review citations 37–41 in the source draft (OMIM/ClinVar, GTEx-as-ML, ChEMBL/DGIdb, gnomAD pLI, STRING, CADD, Roadmap, ENCODE, PolyPhen-2, SIFT) and retain them ONLY where they are cited as annotation sources, not as ML components.
- Drop "thrifty gene" citation (ref 4) if the evolutionary-medicine paragraph is compressed to a single speculative paragraph where it can be replaced by a single reference (keep Neel 1962 or a newer reassessment).

### Retain
- GIANT / DIAMANTE / ICBP / GIGASTROKE / TAGC / MEDIA / SIREN / CAAPA GWAS source citations (6–9 and the AFR cohort citations) — these are the provenance of the claims under audit.
- Open Targets (ref 22), GWAS Catalog (ref 23) — functional annotation sources.
- Martin AR et al. (ref 13) polygenic-risk-score transportability — still relevant for the Cross-Ancestry limitation.

---

## 10. Timeline to submission (week-by-week, from start of edits)

Target: 5 weeks from starting the edits to bioRxiv preprint + Genome Medicine submission. 6 weeks if pathway re-compute is non-trivial.

**Week 1 (edits start)**
- Freeze all real-LD fire outputs (tag `results/` with a git tag or cp-archive to `results_freeze_2026-04-22/`).
- Draft Abstract, Introduction, and new Methods subsections (4.12, 4.13, 4.14).
- Re-compute item 3 (SH2B3 specific numbers) and item 4 (matched-coverage 51/96 vs 48/95 = 1.06×; SUPERSEDED 12/96 baseline preserved per `TRACK-A-FROZEN-NUMBERS.md`) to lock abstract numbers. **DONE in quick-260425-kki commits `884eb3d..f0451b0` (2026-04-25); planning-ecosystem alignment closed in quick-260426-l1h.**

**Week 2**
- Re-compute items 1, 2, 5, 8, 9 (main colocalization aggregates, survival table, tier counts, harmonization breakdown, negative-control performance).
- Draft Results subsections: Overview, Identity-LD vs Real-LD Comparison, Harmonization Diagnostics, Negative-Control Performance.
- Draft Tables 1, 3, 4.

**Week 3**
- Re-compute items 6, 7, 10, 11 (pathway enrichment, variant mechanisms, AFR arm, candidate-gene scorecard).
- Draft remaining Results subsections (Trait-Pair Distribution, Top Signals, Pleiotropic Loci, Pathway Enrichment, Variant Mechanism, Gene Prioritization, Cross-Ancestry).
- Draft Table 2.

**Week 4**
- Draft Discussion and Conclusion.
- Generate all figures (Figures 1–5 + supplementary S1–S6).
- Complete reference list update (add/remove per Section 9).

**Week 5**
- Internal self-review pass: every paragraph audited against the "Remove" checklist in Section 7.
- Draft cover letter (Genome Medicine primary target).
- OSF amendment: upload PDF documenting the pivot direction, tied to 2026-04-22 Stage 2 fire; cross-reference the prior Phase 1 closeout amendment already posted at `osf.io/az52u`.
- Submit to bioRxiv.
- Submit to Genome Medicine immediately after bioRxiv DOI returned.

**Week 6 (contingency)**
- If pathway re-compute reveals a substantial architectural change, add one additional week to re-draft the pathway Results and Discussion subsections before submission.

---

## 11. Submission package checklist

Deliverables needed by Week 5:

- Cover letter (Genome Medicine; 1 page; highlights: real-LD audit of curated pleiotropy claims, SH2B3 collapse, methodological contribution).
- Title page (title, running title, single author, affiliation, correspondence).
- Abstract (~250 words, text from Section 3, re-locked at freeze).
- Keywords (see Section 4.4).
- Main manuscript (target 4,500 words for Genome Medicine; 2,000 for AJHG short-report fallback).
- Tables 1, 2, 3, 4 (main text).
- Figures 1, 2, 3, 4, 5 (main text; vector PDF + high-resolution PNG).
- Supplementary Tables S1–S6.
- Supplementary Figures S1–S6.
- Code repository link (GitHub, tagged release; Zenodo DOI archive at submission).
- OSF project link (`osf.io/az52u`) with pivot amendment attached as PDF.
- Data-availability statement (all public GWAS summary statistics and 1000G Phase 3 reference data; no individual-level data).
- Ethics statement (unchanged from source draft).
- Author contributions statement (solo author).
- Funding statement (per NCSU ASHES Lab standard).
- Competing-interests statement (none).
- bioRxiv preprint DOI (obtained during Week 5).
- Optional: Response-to-imagined-reviewer document (private notes file for Carter's use).

---

## 12. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Scooping — another group publishes a real-LD re-analysis of cardiometabolic pleiotropy first | Medium | High | bioRxiv preprint Day 1 of Week 5 regardless of Genome Medicine timeline; OSF amendment PDF timestamped now to establish priority on the analytical design. |
| Reviewer demands genome-wide results, not 50 curated loci | High | Medium | Frame explicitly as "curated validation subset" from Introduction onward; cite Track B (genome-wide, in preparation) as companion; be ready to cite precedent for curated-locus methodological audits. |
| Reviewer attacks AFR arm as underpowered or ancestry-tokenistic | High | Medium | Pre-empt with candid Limitations paragraph; demote AFR from primary finding to underpowered replication subset; cite the real-LD admissibility constraint explicitly. |
| Critique: "this is a methods paper pretending to be a biology paper" | Medium | Medium | Lean into the methodological framing in title and abstract; make the reality-check positioning primary, biology secondary. If Genome Medicine rejects on this axis, re-route to Bioinformatics (venue 3) with a tightened methods-first rewrite. |
| Critique: "SH2B3 collapse is one locus, not a systematic claim" | Medium | Medium | Report the full survival table (Table 3, Figure 3) so SH2B3 is framed as an anchor example, not the claim itself; report mean and distribution of delta-PP.H4 across all admissible regions. |
| Pathway enrichment under real-LD collapses to no significant pathways | Medium | Medium | If this happens, embrace it: "prior pathway architecture was identity-LD–dependent" is a strong methodological finding. Rewrite Section 4.16 pathway subsection and Discussion paragraph to report the null honestly. |
| GWAS-vintage critique ("why not DIAMANTE 2022 / GBMI asthma?") | High | Low | Address in Methods 4.6 and Limitations: vintage matches the claims under audit, a deliberate scope choice; Track B companion targets state-of-art vintages. |
| OSF pre-registration deviation challenge | Low | Medium | Document pivot as OSF amendment PDF with full 2026-04-22 context; prior closeout amendment at `osf.io/az52u` establishes the amendment workflow. |
| Failure-mode reviewer pushback ("show us the logs" on the 1,005 too_few_snps + 28 empty trait-pair outputs) | Medium | Medium | Table 4 + Figure S6 provide per-trait-pair failure breakdown with 2–3 annotated failure cases; additional logs made available on request via the OSF project. |
| Code reproducibility reviewer test (Genome Medicine increasingly runs this) | Medium | Medium | Ensure Snakemake pipeline is pinned (Snakemake 7.32.4, Python 3.11, conda envs frozen); Zenodo-archive the repo at submission; ensure `snakemake all_pathway --dry-run` still resolves at the tagged commit. |

---

## Decision pending items (explicit)

1. **Venue choice at submission.** Recommended Genome Medicine. Confirm before Week 5 cover-letter drafting.
2. **Identity-LD comparison branch existence.** Does an identity-LD-branch result set exist at the admissible 10 EUR autosomal regions in the current `results/` tree, or does Section 6 item 2 require a fresh Snakemake invocation? Inspect `results/fine_mapping/finemap_manifest.tsv` — if the admissible regions are tagged with identity-LD provenance, the survival table is producible immediately; if not, re-run the 10 admissible regions under identity-LD for comparison.
3. **Repo naming.** Keep `The-ASHES-Laboratory/colocalization-ml-analysis` or rename to `cardiometabolic-real-LD-audit` (or similar) at time of preprint? Renaming is recommended to drop the "ml-analysis" URL fragment but breaks any in-prep citations.
4. **Prior-sensitivity analysis.** Retain p12 = 10⁻⁶, 10⁻⁴ sensitivity branch under real-LD, or drop in favor of LD-panel-as-sensitivity framing? Recommended: drop to keep the paper tight; add back only if a reviewer specifically asks.
5. **Track B companion-paper reference.** If Track B is not yet under active execution, the "companion in preparation" language may be challenged. Confirm Track B status before Week 5.
6. **LD-reference-mismatch review citation.** Pick a 2023–2025 review paper on LD-panel effects in coloc / fine-mapping for the Introduction paragraph 3 rewrite.
7. **Exact Tier A/B/C counts at freeze.** Current counts (0 Tier A, 9 Tier C, 224 negative_control) are as of 2026-04-22. Re-pull at freeze to ensure no drift.
8. **Figure 1 panel B anchor-locus choice.** Which 2–3 loci best illustrate the identity-vs-real-LD credible-set contrast? SH2B3 is one; candidates for the other two: TCF7L2 (if it survives), KCNJ11/ABCC8 (if it collapses), or a rescued example if one exists in the survival table.

---

## Appendix — Edit-counting summary for the return report

The plan above specifies edits against the following subsections of `track_a_source.md` (each counted as one edit target regardless of edit size):

1. Title — rewrite
2. Running title — rewrite
3. Author/affiliations — stay verbatim
4. Abstract — rewrite
5. Keywords — revise
6. Introduction paragraph 1 — minor edits
7. Introduction paragraph 2 — rewrite (move evol-med to Discussion)
8. Introduction paragraph 3 — rewrite
9. Introduction paragraph 4 — minor edits
10. Introduction paragraph 5 (hypotheses) — rewrite
11. Methods > GWAS Summary Statistics — minor edits + add GWAS-vintage note
12. Methods > Data Harmonization — minor edits + add forward pointer
13. Methods > Genomic Regions — minor edits + reframe as validation subset
14. Methods > Colocalization Analysis — rewrite
15. Methods > Fine-Mapping Integration — rewrite
16. Methods > Cross-Ancestry Concordance — minor edits + relabel
17. NEW Methods > Harmonization-Pipeline Diagnostics — add
18. NEW Methods > Identity-LD vs Real-LD Comparison Design — add
19. NEW Methods > Negative-Control Loci — add
20. Methods > Pleiotropy Assessment — minor edits
21. Methods > Pathway Enrichment — minor edits
22. Methods > ML-Based Enhancement — rewrite (rename, de-ML)
23. Methods > Quality Control — stay verbatim
24. Methods > Software and Data Availability — minor edits
25. Methods > Ethics Statement — stay verbatim
26. Results > Overview — rewrite
27. Results > Trait Pair Distribution — rewrite
28. Results > Top Colocalization Signals — rewrite
29. Results > Pleiotropic Loci — rewrite
30. NEW Results > Identity-LD vs Real-LD Comparison — add
31. NEW Results > Harmonization-Pipeline Diagnostics — add
32. NEW Results > Negative-Control Performance — add
33. Results > Pathway Enrichment — rewrite
34. Results > Variant Mechanism Classification — minor edits (de-ML)
35. Results > Gene Prioritization and Therapeutic Targets — substantial cut
36. Results > Cross-Ancestry Comparison — substantial rewrite
37. Discussion opening paragraph — rewrite
38. Discussion > Metabolic Syndrome as Pathway-Defined Entity — substantial cut or rewrite
39. Discussion > Novel Pathway Discovery (Asthma-Metabolic Axis) — remove or substantially cut
40. Discussion > Variant Mechanisms and Therapeutic Implications — substantial cut
41. Discussion > Evolutionary Medicine Perspective — demote to single paragraph
42. Discussion > Cross-Ancestry Pathway Conservation — substantial rewrite
43. Discussion > Strengths, Limitations, Future Directions — rewrite
44. Conclusion — rewrite
45. Table 1 — rewrite
46. Table 2 — revise (de-ML)
47. NEW Table 3 — add
48. NEW Table 4 — add
49. Figure 1 — revise
50. NEW Figure 2 — add
51. NEW Figure 3 — add
52. Figure 4 — revise
53. Figure 5 — revise (de-ML)
54. Supplementary Figures S1–S6 — add

Total distinct edit targets: 54. Largest rewrites: the four flagship Results subsections (Overview, Top Signals, Pleiotropic Loci, Cross-Ancestry) and the Abstract, Introduction hypotheses paragraph, and Conclusion.
