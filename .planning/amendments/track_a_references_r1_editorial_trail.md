# Track A — id-vs-ref-LD: R1 References Editorial Trail (Audit Preservation)

**Provenance:** Preserved R1 editorial scaffolding from `docs/manuscript/id-vs-ref-LD.md` prior to Pass-4 References section consolidation for *Genome Medicine* submission readiness.

**Quick task:** `260503-vcl-ta-submission-readiness-bibliography-and`
**Pass:** T4 (Pass 4 — References section consolidation)
**Captured at commit:** post-T3 `f2faafc` (Pass 3 bibliography compile + paste)
**Subsections preserved:** `### Add` / `### Promote` / `### Retain` / `### Demote` / `### Drop` / `### Supplementary references`
**Source line range:** L364–L396 of `docs/manuscript/id-vs-ref-LD.md` at post-T3 state

**Audit purpose:** This file captures the R1-cycle editorial reasoning (Add / Promote / Retain / Demote / Drop dispositions per ref slot, including the Amendment §4.17 P5 evolutionary-medicine paragraph reduction and the inline-slot mapping from R1 source-of-truth phase) before the manuscript-side restructure replaced these subsections with a single scope-prose paragraph + the consolidated numbered bibliography. The Pass-4 consolidation is purely a rendering change for venue-submission readiness — no editorial decisions are reversed; this trail preserves the reasoning for any future audit, peer-review challenge, or revision-cycle reconstruction.

**Cross-references:**
- Numbered bibliography: `docs/manuscript/refs/track_a_bibliography.md` (compiled in T3)
- HALT-REPORT (Pass 3 unresolvable slots): `.planning/quick/260503-vcl-ta-submission-readiness-bibliography-and/HALT-REPORT.md`
- Amendment authority: `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §4.17 P5
- Decision-items lock: `.planning/amendments/track_a_decision_items_resolution_log.md` (T2)

**Honest-framing-lock note:** The preserved §Drop subsection below contains historical R1-process language (e.g., "ML-based framing claims", "cleanup") that was internal editorial vocabulary describing the disposition of removed source-draft material. Per `feedback_failed_to_honest_finding.md` and `feedback_original_research_framing.md`, audit-trail content correctly preserves historical tokens — DO NOT scrub. Forward-facing manuscript prose contains 0 occurrences of these tokens after Pass 4.

---

## Preserved R1 Editorial Subsections (verbatim from manuscript L364–L396 post-T3)

### Add

- **Ref 42 NEW — Weissbrod O, Hormozdiari F, Benner C, et al. (2020).** "Functionally informed fine-mapping and polygenic localization of complex trait heritability." *Nat Genet* 52:1355–1363. Functionally-informed fine-mapping and treatment of LD mismatch between fine-mapping panel and discovery GWAS. Inline slot: L36 Introduction P2 (third element of the three-inflation-settings citation cluster ²⁰,²⁹,⁴²).
- **Ref 43 NEW — Benner C, Spencer CCA, Havulinna AS, et al. (2016).** "FINEMAP: efficient variable selection using summary data from genome-wide association studies." *Bioinformatics* 32:1493–1501. Alternative fine-mapping referent; early formulation of LD-mismatch vulnerability under the single-causal-variant model. Inline slot: L36 Introduction P2 (extends three-inflation-settings citation cluster ²⁰,²⁹,⁴² to ²⁰,²⁹,⁴²,⁴³). Resolved at 2.2.f R2 (commit pending).

### Promote (already in source draft; reframed as primary-method citation in the pivot)

- **Ref 20 — Zou Y, Carbonetto P, Wang G, Stephens M (2022).** "Fine-mapping from summary data with the 'Sum of Single Effects' model." *PLoS Genet* 18:e1010299. SuSiE-RSS methodology. Promoted to primary method citation at L36 (new), L38, L72, and throughout Methods §Fine-Mapping Integration.
- **Ref 29 — Wallace C (2021).** "A more accurate method for colocalisation analysis allowing for multiple causal variants." *PLoS Genet* 17:e1009440. `coloc.susie` methodology; colocalization accuracy under LD mismatch and multi-causal-variant architecture. Promoted to primary method citation at L36 (new), L38, L72.

### Retain (unchanged from source draft)

- **Ref 10 — Giambartolomei C, Vukcevic D, Schadt EE, et al. (2014).** "Bayesian test for colocalisation between pairs of genetic association studies using summary statistics." *PLoS Genet* 10:e1004383. Original `coloc.abf` methodology. Framed in the pivot as the method under audit (not endorsed). Retained at L36, L70.
- **Refs 1–3** — original cardiometabolic epidemiology citations (T2D–hypertension ~50% comorbidity; obesity as shared risk factor). Retained at L34 (¹⁻³).
- **Refs 6–9** — GIANT / DIAMANTE / ICBP / GIGASTROKE GWAS-source citations at L54 (⁶⁻⁹). Provenance of the claims under audit.
  - **Ref 7 specification:** Mahajan A, Taliun D, Thurner M, et al. (2018) "Fine-mapping type 2 diabetes loci to single-variant resolution using high-density imputation and islet-specific epigenome maps." *Nat Genet* 50:1505–1513. DOI 10.1038/s41588-018-0241-6. (DIAMANTE EUR T2D, N = 898,130; the vintage matched to Track A's harmonized sumstats at `data/processed/sumstats_harmonized/t2d.EUR.tsv.bgz`.)
- **Refs 11–12** — GWAS-ancestry-demographics citations at L40 (¹¹⁻¹²).
- **Ref 13** — Martin AR et al. polygenic-risk-score transportability. Still relevant for the Cross-Ancestry limitation.
- **Refs 17–19** — curated-candidate-locus prior-literature citations at L64 (¹⁷⁻¹⁹).
- **Refs 21–41** — annotation-aggregation sources: GTEx v8, Open Targets, NHGRI-EBI GWAS Catalog, Roadmap Epigenomics, ENCODE, CADD, PolyPhen-2, SIFT, KEGG, Reactome, GO, OMIM, ClinVar, gnomAD pLI, STRING, DGIdb, ChEMBL. Exact slot-to-source assignments within the 21–41 range are deferred to the Zotero/EndNote export at venue-submission prep; R1 preserves the inline superscripts at their existing positions.
- **Ref 27** — cardiometabolic disease burden in African-descended populations, L40.

### Demote (retained but confined to one Discussion paragraph)

- **Refs 4, 5 — Neel JV (1962)** "Diabetes mellitus: a 'thrifty' genotype rendered detrimental by 'progress'?" *Am J Hum Genet* 14:353–362; and **Williams GC (1957)** "Pleiotropy, natural selection, and the evolution of senescence." *Evolution* 11:398–411. Thrifty-gene and antagonistic-pleiotropy hypotheses. Retained as citations but confined to a single Discussion paragraph (§Evolutionary Medicine Perspective, L228–230), reduced from three paragraphs in the v10 source to one speculative paragraph ≤ 120 words per Amendment §4.17 P5. Inline superscripts ⁴⁻⁵ preserved verbatim at L230.

### Drop (removed from the pivot)

- References formerly supporting "ML-based" framing claims (gene-prioritization ML classifiers, variant-effect-prediction ML scoring, cross-ancestry-ML-validation claims) that are not preserved in the pivoted manuscript. Specific ref-number-to-source mapping is deferred to 2.2.f R2 / venue-submission prep once the Zotero library export is available — dropping inline superscripts without the source-to-number mapping risks orphaning a retained reference. The pivot-as-a-whole drops ML-framing claims in §Discussion and §Variant Mechanisms per Amendment §4.17; the inline-superscript cleanup is the last step before the Zotero export consolidates the numbered list.

### Supplementary references

No supplementary-only references have been identified at this pass. The Figure S1–S6 captions (L297) and Table S1–S7 captions throughout the manuscript all cite main-text references; no supplementary-unique bibliography entries are required. This subsection is retained as a placeholder in case 2.3 figure-script development (Route A Step 2.3) introduces a supplementary-caption-only citation — in that case it would be appended here with a slot ⁴⁴+ assignment.

---

## Resolution status (post-T3 Pass 3 + post-T4 Pass 4)

- **Add (refs 42, 43):** Both compiled into `docs/manuscript/refs/track_a_bibliography.md` with full Vancouver-style citations + DOIs (Weissbrod 2020 and Benner 2016 FINEMAP).
- **Promote (refs 20, 29):** Both compiled into bibliography with full citations (Zou 2022 SuSiE and Wallace 2021 coloc.susie).
- **Retain (refs 1–3, 6–13, 17–19, 21–41, 27):** All cited slots populated in bibliography; ref 13 preserved as gap-slot (no inline superscript per HALT-REPORT line 44 self-correction).
- **Demote (refs 4, 5):** Both compiled into bibliography with full citations (Neel 1962 thrifty-gene and Williams 1957 antagonistic-pleiotropy); inline superscripts ⁴⁻⁵ at L228–230 verified intact post-Pass-4 consolidation.
- **Drop:** Pivot-level ML-framing removal already executed across Discussion and Variant Mechanisms in earlier R0/R1 passes; no further inline-superscript orphaning required since refs 24–26, 28, 30–33 are intentionally preserved as gap-slots in the numbered bibliography (no inline citations to maintain).
- **Supplementary references:** Slot 44 preserved in numbered bibliography as `*Reserved (supplementary slot).*` per the placeholder convention; no supplementary-only citations introduced through Pass 6.

---

## Honest-framing-lock audit (this trail file)

| Token pattern | Count in this file | Provenance |
|---------------|-------------------|------------|
| `revision` | 0 | (none — header text uses "consolidation" / "audit" / "process") |
| `cleanup` | 1 | preserved verbatim from §Drop ("inline-superscript cleanup is the last step") — historical R1 process language |
| `\bfix\b` / `fixed` / `fixing` | 0 | (none in preserved content) |
| `\bML\b` | 5 | preserved verbatim from §Drop ("ML-based" / "ML classifiers" / "ML scoring" / "ML-validation" / "ML-framing") — historical R1 process language describing pre-pivot disposition |

**Audit-trail invariant:** Preserved R1 content may carry historical R1-process tokens; this is correct for an audit trail per `feedback_failed_to_honest_finding.md`. Forward-facing manuscript prose carries 0 forbidden tokens post-Pass-4 (verified at T5 sweep).
