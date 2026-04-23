# PROJECT AMENDMENT — Genome-Wide Reframe

**Date**: 2026-04-22
**Author**: Carter K. Clinton (solo author, NCSU ASHES Lab)
**Status**: Adopted; OSF amendment pending (see Section 9)
**Supersedes scope of**: OSF pre-registration osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J) and amendment osf.io/az52u (distal-gene expansion, April 2026)
**Companion documents**: `TRACK-A-PIVOT.md`, `SUMSTATS-UPGRADE.tsv` / `.md`, `AOU-LD-PIPELINE.md`

---

## 1. Executive Summary

coloc_analysis is being reframed from a 50-region candidate-locus pleiotropy study into a genome-wide, joint-signal discovery study across 9 complex traits in EUR and AFR ancestries, with **two co-equal scientific aims**: (i) cross-trait pleiotropy discovery (shared-architecture inference, colocalized credible-set identification, ancestry-stratified replication); and (ii) novel-variant discovery (single-trait and joint-signal loci not previously reported in the GWAS Catalog or in published pleiotropy catalogs). These aims share the same upstream pipeline — MTAG (Turley 2018) and CPASSOC (Zhu 2015) for multi-trait signal aggregation, coloc/SuSiE-RSS (Wallace 2020; Zou 2022) for credible-set resolution, HyPrColoc (Foley 2021) for shared-architecture inference, All of Us controlled-tier AFR WGS (~100k samples) for real, matched-ancestry LD at scale — but produce distinct deliverables and are pre-registered as separable claims. The pivot is motivated by a fundamental circularity in the candidate-locus design that Phase 2 Stage 2 real-LD results on 2026-04-22 made quantitative: the 50 hand-curated regions were chosen because published pleiotropy claims existed there, and when real-LD is imposed, previously-reported signals (e.g., SH2B3 asthma EUR, PP.H4 identity-LD = 1.0, n_cs_a = 0 under real-LD) do not survive — while no novel Tier A signals emerge because the design cannot discover them, in either the pleiotropy sense or the single-trait variant sense. A companion short-form paper (Track A) will publish the candidate-locus real-LD re-analysis as a pre-specified methods-validation result; the main manuscript (Track B) will pursue both genome-wide pleiotropy discovery and novel-variant discovery on upgraded, larger-N sumstats with ancestry-matched real LD and multi-method triangulation.

---

## 2. Rationale

### 2.1 Why the candidate-locus design fails the Nature Genetics bar

The 205 analysis windows tiling 50 hand-curated regions across 8 seed pleiotropic loci (SH2B3, FTO, APOE, MC4R, APOL1, 9p21/CDKN2A, CXADR/F2RL1, HLA/6p21, plus SLC2A9, PYHIN1, BMI_5q13_3, BMI_Xq24) were drawn from prior literature reporting cross-trait association. The inference target was "is there colocalizing pleiotropy in these regions?" The answer is almost mechanically yes for any region picked because prior evidence already said yes. The study is therefore not discovering pleiotropy — it is re-confirming a pre-selected subset with a new method. The same circularity blocks novel-variant discovery: the candidate-locus design also cannot surface variants outside the 50 chosen regions, and within the regions the only "novel" variants it could discover would be secondary signals at known loci — already a constrained slice of the discovery space. A reviewer at a top genetics journal will see both failures immediately and correctly reject the claim that the findings generalize.

Nature Genetics calibre for a pleiotropy + variant-discovery paper in 2026 requires (a) genome-wide, hypothesis-agnostic region generation; (b) joint-signal discovery methods that gain power from the pleiotropy itself rather than assuming it ex ante; (c) real, matched-ancestry LD so credible sets are defensible; (d) multi-method triangulation so no single method's assumption failure drives the result; (e) at least one non-EUR ancestry handled at a power level that isn't a footnote; and (f) explicit comparison of all claimed novel loci against locked versions of public catalogs (GWAS Catalog, Open Targets Genetics, prior pleiotropy catalogs) to substantiate "novel" as a positive claim, not a default. The current design meets (d) partially and fails (a), (b), (e), and (f).

### 2.2 The Stage 2 evidence

The Phase 2 Stage 2 real-LD production fire on 2026-04-22 returned 51/96 non-empty credible sets against a target of ≥40 (up from a 12-set identity-LD baseline) — so the pipeline works. But 0 signals reached Tier A, and the flagship SH2B3 × asthma EUR coloc that showed PP.H4 = 1.0 under identity-LD collapsed to n_cs_a = 0 under real-LD. Identity-LD inflation has been known since Benner 2017; our own data now demonstrate it on a signal the literature treats as canonical. This is a defensible Track A finding. It is also a fatal weakness for the Track B claim "these 50 regions are the pleiotropic architecture of the 5-trait space."

### 2.3 The circularity argument, formally

Define the candidate set C as regions previously reported to show cross-trait association. Let H₁ = "region has true colocalizing pleiotropy," H₀ = "null." P(H₁ | region ∈ C) ≫ P(H₁ | random region), by construction. Any test restricted to C has no discovery content for the population of all regions; it is a precision estimate of the replication rate of prior claims conditional on a new method. The same argument applies to novel-variant claims: define the variant set V_C as variants residing in C, and let N = "variant is novel relative to GWAS Catalog v_lock." Conditioning on V_C constrains discovery to a tiny, biased fraction of the genome; the candidate-locus design is therefore non-informative about genome-wide novel-variant yield. Both claim types — pleiotropy and novel-variant — require genome-wide region generation. That is a valid methods contribution (Track A) but is not a Nature Genetics discovery paper.

### 2.4 Relevant T1 spine artifacts

T1 spine completion on 2026-04-14 (Phases 0, 1, 2, 5, 9) produced: Phase 0 reference data (32 GB, LD panels, functional annotations, MAGMA gene windows); Phase 1 SuSiE-RSS fine-mapping outputs across 205 windows; Phase 2 Stage 1 identity-LD coloc (12 credible sets) and Stage 2 real-LD coloc (51 credible sets, 0 Tier A); Phase 5 LDSC partitioned heritability, HESS local-h², MAGMA gene-set (h2_summary.tsv, HESS 290, MAGMA 8/8, LDSC-SEG); Phase 9 replication scaffolding. All of these outputs are preserved and repurposed, not discarded, per Section 8.

---

## 3. New Milestone Sequence (M0–M6)

| Milestone | Content | Est. Duration | Critical-Path Dependencies | Deliverable Artifacts |
|---|---|---|---|---|
| **M0 — Pivot scaffolding** | This amendment; update .planning/ scaffold (Section 12); lock 9-trait × 2-ancestry trait inventory; lock phenotype definitions; write TRACK-A-PIVOT.md, SUMSTATS-UPGRADE, AOU-LD-PIPELINE.md. | 1–2 weeks | None (planning only) | `PROJECT-AMENDMENT-2026-04-22-*.md`, updated PROJECT.md/ROADMAP.md/REQUIREMENTS.md/DECISIONS.md/STATE.md, trait-inventory TSV |
| **M1 — Sumstats upgrade and harmonization** | Download Yengo 2022, DIAMANTE 2022, GIGASTROKE 2022, Giri 2020 MVP, GBMI asthma 2022, Aragam 2022 CAD, GLGC 2021 lipids, CKDGen 2019 eGFR, MAGIC 2021 HbA1c. Harmonize to GRCh38, lift deCODE rsids, filter MAF ≥ 0.005, INFO ≥ 0.8, per-ancestry QC. Build LDSC-ready and MTAG-ready formats. Verify ancestries and sample-overlap flags per trait. | 4–6 weeks | Download lead times (some DUAs in place; GBMI and MVP need verification) | Harmonized sumstats parquet; per-trait QC report; LDSC munged files |
| **M2 — LDSC + MTAG + CPASSOC discovery** | LDSC pairwise rg across all 9 traits × 2 ancestries; MTAG with `--overlap` using LDSC intercept matrix for UKB/MVP cohort overlap; CPASSOC orthogonal joint test; `max_FDR` filter on MTAG per Turley 2018. Genome-wide clumping (PLINK `--clump p=5e-8 r²<0.01 1Mb`) per trait × ancestry; union of clumped regions + MTAG-novel + CPASSOC-novel = discovery region list (~1,500–3,000 regions). **Novel-variant deliverable (Discovery Class 1)**: extract joint-signal novel loci where MTAG or CPASSOC reaches p < 5e-8 and no contributing single trait does, intersected with GWAS Catalog v_lock for prior-art exclusion. | 6–8 weeks | M1 complete; OSF amendment posted BEFORE this milestone begins (Section 9) | `rg_matrix.tsv`, MTAG per-trait outputs, CPASSOC outputs, union region BED, novelty annotation, `joint_signal_novel.tsv` |
| **M3 — AoU AFR LD panel build** | Inside AoU Researcher Workbench (Terra), build LD matrices per region × ancestry from controlled-tier WGS (~100k AFR). Export summary-only (LD matrix + allele-frequency metadata), verify AoU data-egress policy compliance. Parallel: rebuild EUR LD from 1000G+UKB for parity. | 4–6 weeks (with ~1–2 weeks Terra iteration) | Region list from M2; AoU Workbench access (Carter has controlled-tier) | Per-region LD `.rds` files AFR + EUR; egress audit log; `AOU-LD-PIPELINE.md` executed |
| **M4 — Scalable coloc + fine-mapping** | Two-stage coloc: fast ABF-coloc (Giambartolomei 2014) genome-wide first, then SuSiE-RSS only where PP.H4 > 0.5 (cuts compute 10–20×). Region-level PP.H4 FDR correction. HyPrColoc across ≥3 traits simultaneously. PolyFun baselineLF2 functional priors (Weissbrod 2020) for rescue of underpowered credible sets. AFR fine-mapping with AoU LD; EUR with 1000G+UKB LD. **Novel-variant deliverables (Discovery Classes 2 + 3)**: extract AFR-specific lead variants (Class 2 — AFR PP.H4 ≥ 0.8 or AFR-only single-trait lead with minimum-overlap EUR signal) and secondary independent credible sets (Class 3 — SuSiE-RSS credible-set index ≥ 2 at GWAS-Catalog-known loci). | 8–12 weeks (LSF heavy) | M3 LD panels; M2 region list | Per-region coloc + SuSiE + HyPrColoc tables; PolyFun-rescued CSs; Tier A/B/C classification; `afr_specific_novel.tsv`; `secondary_signals.tsv` |
| **M5 — Variant→gene prioritization + novelty cross-reference** | L2G (Open Targets) prior; eQTL/pQTL coloc refreshed with upgraded sumstats; Borzoi variant-effect scoring on Tier A credible-set variants (Linder 2024); MAGMA gene-set re-run. **Novel-variant deliverables (Discovery Classes 4 + 5)**: cross-reference colocalized loci against locked versions of Pickrell 2016, Watanabe 2019 GWAS Atlas, and Open Targets Genetics L2G to extract pleiotropy-class novel loci (Class 4); annotate Tier A credible-set variants with Borzoi/Enformer effect scores in tissue-specific tracks against ClinVar v_lock + GWAS Catalog v_lock + primary-literature search to extract functional-mechanism novel variants (Class 5). 2–3 days of annotation pipeline work for catalog cross-reference. | 4–6 weeks | M4 Tier A list | Gene-prioritization table per Tier A signal; Borzoi scores; `pleiotropy_novel.tsv`; `functional_novel.tsv`; consolidated novelty manifest |
| **M6 — Manuscript and replication** | Draft Track B manuscript; run hold-out replication on FinnGen / Pan-UKBB / MVP release n+1 where available; generate figures; OSF deposit of all post-registration outputs; submit to Nature Genetics. | 8–12 weeks | M5 complete | Submitted manuscript; GitHub pipeline release; OSF data deposit |

Total M1–M6: ~7–11 months assuming single-threaded solo execution and LSF availability.

---

## 4. Trait Inventory

Nine traits × up to two ancestries = up to 18 trait × ancestry combinations. Ancestry column "EUR / AFR / TRANS" indicates primary analysis plane; TRANS means the upstream meta-analysis is multi-ancestry and ancestry-stratified subfiles are used when available.

| Trait | Ancestry | Source (first-author year) | N (cases / controls or total) | Phenotype lock | Status | UKB overlap? | MVP overlap? |
|---|---|---|---|---|---|---|---|
| BMI | EUR | Yengo 2022 GIANT+UKBB | ~700k total | Continuous, inverse-rank-normal | to download | **Yes (heavy)** | No |
| BMI | AFR | PAGE + AoU | PAGE ~50k; AoU ~50k AFR | Continuous, inverse-rank-normal | to download | No | No |
| T2D | TRANS (+ AFR stratum) | DIAMANTE 2022 Mahajan | ~1.4M trans; AFR ~29k cases | Case-control, T2D diagnosis | to download | Partial (UKB in TRANS) | **Yes (MVP in TRANS)** |
| Stroke | TRANS (+ AFR stratum) | GIGASTROKE 2022 Mishra | ~2.2M trans; AFR ~13k cases | **All-stroke** (not ischemic-only) | to download | Partial | **Yes (MVP in TRANS)** |
| SBP | EUR | Evangelou 2018 | ~1M | Continuous SBP (not DBP, not binary HTN) | already downloaded | **Yes** | No |
| SBP | AFR | Giri 2020 MVP | ~300k | Continuous SBP | to download (DUA verify) | No | **Yes (source)** |
| Asthma | TRANS (covers AFR) | GBMI Zhou 2022 | ~1.5M multi-ancestry | Pooled adult + child asthma | to download | **Yes (UKB in GBMI)** | No |
| CAD | EUR | Aragam 2022 CARDIoGRAM+UKB | ~1.2M | Case-control CAD | to download | **Yes** | No |
| Lipids (LDL primary; HDL/TG/TC secondary) | EUR + AFR | GLGC 2021 Graham | ~1.6M multi-ancestry | LDL-C continuous primary; HDL, TG, TC secondary | to download | **Yes (UKB in GLGC)** | Partial |
| eGFR | EUR + AFR | CKDGen 2019 Wuttke | ~1M | Continuous eGFR (creatinine-based) | to download | Partial | No |
| HbA1c | EUR + AFR | MAGIC 2021 Chen | ~280k multi-ancestry | Continuous HbA1c | to download | Partial | No |

**UKB-overlap traits flagged for MTAG `--overlap` treatment**: BMI, SBP, Asthma, CAD, Lipids, and plausibly T2D/Stroke (TRANS meta-analyses include UKB contributors). The LDSC intercept matrix must be estimated on all pairs before MTAG runs so the overlap-correction covariance block is populated; mtCOJO (Zhu 2018) is an orthogonal check where trait-pair overlap is extreme.

**MVP-overlap traits**: DIAMANTE T2D, GIGASTROKE, Giri SBP-AFR — these three co-ingest MVP subjects and cannot be treated as independent cohorts in MTAG; LDSC intercept correction again mandatory.

**Previously-downloaded from T1 spine, reusable**: Evangelou 2018 SBP EUR, GBMI asthma pilot subset, Giant+UKB BMI earlier release — all will be re-verified against the upgraded versions above before use.

---

## 5. AFR LD Panel Strategy

AFR fine-mapping and coloc on all Track B regions will use All of Us controlled-tier WGS as the reference LD panel (~100k AFR-ancestry participants), computed inside the AoU Researcher Workbench (Terra) with only summary-level LD matrices and per-variant allele-frequency metadata exported per AoU data-egress policy. This replaces the 1000G AFR panel (N = 661) that has been the field default and that Phase 2 Stage 2 already demonstrated is insufficient for robust credible-set construction in AFR. The AoU panel is a ~150× N increase and is matched to the AFR GWAS cohorts actually contributing to the sumstats we analyze. We treat this LD-panel upgrade as a methodological novelty point for the manuscript — to our knowledge no published pleiotropy fine-mapping at genome-wide scale has used AoU WGS for AFR LD. Implementation plan, egress policy compliance, Terra compute budget, and verification protocol are in `AOU-LD-PIPELINE.md`.

---

## 6. Method Stack

1. **LDSC genetic correlations** (Bulik-Sullivan 2015): re-run on upgraded sumstats, yields the rg matrix and the per-pair intercept needed for MTAG `--overlap`. Non-optional precursor.
2. **MTAG** (Turley 2018): multi-trait boost of per-variant z-scores under an assumed constant covariance of effects. `--overlap` with LDSC intercept matrix handles UKB/MVP overlap. `max_FDR` filter controls the constant-covariance-assumption violation per region.
3. **CPASSOC** (Zhu 2015): orthogonal joint-signal test (SHom / SHet statistics) that does not assume constant covariance; use as independent corroboration of MTAG novel loci.
4. **PLINK clumping** (`--clump p=5e-8 r²<0.01 1Mb`): per trait × ancestry, then union with MTAG + CPASSOC novel signals to produce the ~1,500–3,000-region discovery list. Standard genome-wide region-definition procedure.
5. **ABF-coloc** (Giambartolomei 2014; Wallace 2020): fast approximate Bayes factor coloc run genome-wide first as a triage filter. Compute-linear in variants, not N².
6. **SuSiE-RSS** (Zou 2022): sum-of-single-effects fine-mapping on regions with PP.H4 > threshold from ABF-coloc. 10–20× compute savings vs SuSiE-on-all-regions.
7. **HyPrColoc** (Foley 2021): simultaneous coloc across ≥3 traits; more powerful than pairwise coloc when shared architecture exists, which is the target of this study.
8. **AoU AFR LD** (Section 5): matched-ancestry real LD at ~100k scale for all AFR fine-mapping.
9. **PolyFun baselineLF2** (Weissbrod 2020): functional-annotation-informed priors on SuSiE credible sets to rescue underpowered signals (relevant especially for AFR where N is lower).
10. **L2G / Open Targets** (Mountjoy 2021): secondary gene-prioritization axis independent of coloc/eQTL, using distance + chromatin + L2G training features.
11. **Borzoi variant-effect scoring** (Linder 2024): deep-learning RNA-seq-track predictor for Tier A credible-set variants to narrow causal-variant identity when coloc credible sets contain >1 variant.

---

## 7. Novel Variant Discovery as Co-Equal Scientific Aim

The Track B reframe is not pleiotropy-primary with novelty as a downstream by-product. It is a dual-aim study: cross-trait pleiotropy and novel-variant discovery share the upstream pipeline but are reported as separable claims, each with its own pre-registered novelty definition, comparator catalog, and expected yield. This section enumerates the five discovery classes that constitute the novel-variant aim, how each is operationalized in the milestone sequence, the reporting framework, and order-of-magnitude yield expectations. Novelty is treated explicitly as a spectrum: some loci will be unambiguously new (no prior GWS hit within ±500 kb across any catalog at lock date), some will be "novel enough" by one criterion but already implicated by another (e.g., joint-signal novel under MTAG but with a sub-threshold prior-art trend), and a small number will be revolutionary (large-effect novel variants in well-trodden physiological pathways or AFR-specific haplotypes that re-shape clinical interpretation). The paper will say which is which.

### 7.1 The five discovery classes

**Class 1 — Joint-signal novelty via MTAG / CPASSOC.** Loci where no contributing single trait reaches genome-wide significance but the multi-trait test does. This is the discovery mode Turley 2018 highlights as MTAG's principal contribution: when k correlated traits each carry sub-threshold signal at a shared variant, the multi-trait z-score boost can push the locus over 5e-8 even when no constituent trait exceeds it. CPASSOC's SHom and SHet statistics provide the orthogonal corroboration filter (no constant-effect-covariance assumption). Operationalization: M2 produces per-trait clumped GWS loci, MTAG per-trait outputs, and CPASSOC per-locus joint-test outputs; Class 1 novel = (MTAG p < 5e-8 OR CPASSOC p < 5e-8) AND max(single-trait p) ≥ 5e-8 AND no single-trait GWS hit within ±500 kb in GWAS Catalog v_lock. Cross-method corroboration (MTAG ∩ CPASSOC) yields the high-confidence subset.

**Class 2 — Ancestry-specific novelty.** AFR lead variants masked by EUR LD in prior fine-mapping work, or AFR lead variants at AFR-specific MAF that EUR-only studies are formally underpowered to detect (canonical examples: APOL1 G1/G2 in CKD, G6PD A- in oxidative-stress phenotypes, HBB sickle-cell-trait haplotypes in pregnancy / kidney / multiple downstream traits). With 1000G AFR (N=661) the LD-driven uncertainty in credible-set construction has been the field bottleneck; the AoU AFR LD panel (~100k AFR WGS) collapses that uncertainty for the first time at genome-wide scale and is itself a methodological novelty axis (Section 5). Operationalization: M3 builds the AoU AFR LD panel; M4 runs AFR fine-mapping with AoU LD; Class 2 novel = AFR PP.H4 ≥ 0.8 (with high-confidence AFR credible set, |CS| ≤ 25) AND either (a) no overlapping EUR coloc signal at the same locus, or (b) AFR lead variant has MAF_AFR ≥ 0.01 with MAF_EUR < 0.005 (AFR-specific haplotype). The EUR-non-overlap test guards against false novelty from EUR underpower at AFR-MAF variants.

**Class 3 — Secondary-signal novelty.** SuSiE-RSS produces L credible sets per region where L ≥ 1; credible-set indices ≥ 2 at known loci frequently represent independent causal variants whose existence prior single-signal fine-mapping (PAINTOR, FINEMAP top-1) could not surface. Modern fine-mapping practice routinely reports secondary signals, but they are not always claimed as "novel," producing a discovery deficit at well-trodden loci. Operationalization: M4 SuSiE-RSS allows L = 10 by default; Class 3 novel = credible-set index ≥ 2 AND CS purity ≥ 0.5 AND PIP_max(CS) ≥ 0.5 AND lead variant of CS index ≥ 2 not within ±100 kb of prior GWAS Catalog v_lock entries for the same trait. Tighter ±100 kb (vs ±500 kb for Class 1) reflects that secondary-signal novelty is about within-locus independence, not new-locus discovery.

**Class 4 — Pleiotropy-class novelty.** Loci colocalized across trait pairs that have not been flagged in prior pleiotropy catalogs. The two reference catalogs are Pickrell 2016 (16-trait LCV-style cross-trait analysis, *Nature Genetics*) and the Watanabe 2019 GWAS Atlas (cross-trait shared-loci compilation across 558 GWAS, *Nature Genetics*). Open Targets Genetics L2G (Mountjoy 2021) is a third reference for variant-to-gene mapping novelty within the pleiotropy axis. Operationalization: M5 takes the M4 colocalized-loci table (cross-trait PP.H4 ≥ 0.8 or HyPrColoc PP ≥ 0.8) and intersects against locked exports of all three catalogs; Class 4 novel = colocalized cross-trait pair NOT present in Pickrell 2016 supplement, NOT present in Watanabe 2019 GWAS Atlas as cross-trait shared, AND target gene NOT in Open Targets Genetics L2G top-3 for either trait at the locus. Class 4 is the densest novelty axis once the genome-wide pipeline runs.

**Class 5 — Functional-mechanism novelty.** Borzoi (Linder 2024) and Enformer (Avsec 2021) variant-effect scoring identifies variants with large predicted regulatory effect on specific tissues and cell types. Loci where the Tier A credible-set lead variant has a high tissue-specific effect score in a tissue not previously functionally implicated for the trait — and where ClinVar / GWAS Catalog / primary-literature searches yield no prior functional characterization — represent mechanistic novelty. This is the most discriminating axis: many loci can be statistically novel without being mechanistically interesting; functional-mechanism novelty narrows to loci where the biology is genuinely under-explored. Operationalization: M5 Borzoi runs on Tier A credible-set variants only; Class 5 novel = max-tissue Borzoi/Enformer effect score in top decile across the credible set AND no ClinVar pathogenic/likely-pathogenic entry for the variant AND no primary-literature functional characterization (PubMed search via mcp__claude_ai_PubMed). Functional novelty is reported as supplementary mechanistic context, not as the primary novelty claim, because Borzoi/Enformer training-distribution caveats apply.

### 7.2 Reporting framework

The manuscript will report novel-locus claims via a single consolidated table with one row per claimed-novel locus and columns: locus_id, lead_variant, trait(s), ancestry, novelty_class (1–5; multiple classes possible), GWAS_Catalog_v_lock_status, Pickrell2016_status, Watanabe2019_status, Open_Targets_L2G_status, ClinVar_status, PubMed_search_date, Borzoi_max_tissue_score, novelty_confidence (high / medium / "novel by one criterion only"). The catalog versions used as the prior-art baseline will be locked at the M5 cross-reference date and reported in the supplement with download URLs and SHA-256 checksums; this avoids the well-known reviewer objection that catalog drift between submission and revision can convert "novel" into "not novel" without any analytical change. The honest framing — some loci are novel by Class 1 only and would not survive Class 4 cross-reference; some are novel by Class 4 only because they use a wider pleiotropy comparator — will be explicit in the table and the discussion.

### 7.3 Expected novel-locus yield (order-of-magnitude estimates)

These estimates are honest priors based on published rates from comparable studies; actual yields will differ and will be reported as-observed in M5. They are included here so reviewers can audit whether the realized yield is in or out of the expected range.

- **Class 1 (joint-signal novel)**: 50–200 loci across 9 traits. Turley 2018 reported ~30–80 MTAG-novel loci per 4-trait MTAG run; with 9 traits and orthogonal CPASSOC corroboration filter, the high-confidence intersection yield is likely in the 50–200 range. Lower bound if `--overlap` correction is aggressive; upper bound if many sub-threshold concordant signals exist across the 9-trait correlated block.
- **Class 2 (AFR-specific novel)**: 5–30 loci. AFR sample sizes in even the upgraded sumstats remain 5–10× smaller than EUR; even with AoU LD, AFR power ceiling caps yield. Most yield will be at AFR-MAF-frequent variants where EUR underpower is structural.
- **Class 3 (secondary-signal novel)**: 100–400 secondary credible sets across all M4 regions. SuSiE-RSS routinely returns multiple credible sets at high-power loci; the novel-claim subset (no prior GWAS Catalog within ±100 kb) will be a fraction of these, plausibly 20–40% based on current fine-mapping literature.
- **Class 4 (pleiotropy-class novel)**: 30–150 trait-pair-locus combinations. Pickrell 2016 covered 16 traits and Watanabe 2019 covered 558 GWAS but with sparser coloc-grade resolution; the combination of upgraded sumstats, HyPrColoc 3+ traits, and AoU AFR LD will surface pleiotropy combinations these catalogs missed.
- **Class 5 (functional-mechanism novel)**: 10–50 variants. Smallest yield by design — this is the Tier-A-only, mechanism-substantiated tail. The high discrimination is the point.

Total claimed-novel locus count is expected in the low hundreds across all classes. The paper will not aggregate these into a single headline number; the per-class breakdown is the honest framing.

---

## 8. Track A Integration

The T1 spine outputs (205 SuSiE credible sets, 96 Stage 2 coloc cells, 51 non-empty real-LD credible sets, h² partitioned heritability, HESS, MAGMA, LDSC-SEG) are not discarded. They become the **candidate-locus real-LD validation subset** of Track B — i.e., a pre-specified appendix demonstrating that the method replicates on prior-literature regions — and are the primary data for **Track A**, a short-form methods paper re-framed from the existing ajhg_manu_v10.pdf preliminary draft. Track A's claim is quantitative: of N published cross-trait pleiotropy claims in the 50 candidate loci, what fraction survive a fully-pre-registered real-LD re-analysis with current best-practice coloc + SuSiE-RSS? "Machine Learning" is dropped from the draft title because the existing work does not deploy ML in a load-bearing way. Target venue ordering: Genome Medicine → AJHG short report → Bioinformatics. Track A submission is expected in 2–4 weeks and precedes Track B M6 by several months; the Track A paper will cite the Track B OSF amendment as "pre-specified upstream discovery effort," establishing that Track A is validation ahead of discovery rather than a post-hoc carve-out. Full content and venue strategy in `TRACK-A-PIVOT.md`.

---

## 9. OSF Amendment Plan

### 9.1 Timing

The Track B amendment will be posted **after** M1 sumstats harmonization verifies (harmonized files frozen, checksums recorded, ancestry and sample-overlap flags locked) and **before** any MTAG or CPASSOC discovery run executes in M2. This ordering preserves pre-registration integrity on the core discovery claim — region novelty from MTAG+CPASSOC — while allowing the amendment to cite concrete, verified input data rather than aspirational sumstats. Carter confirmed this sequencing.

### 9.2 Coordination with existing OSF record

- Root pre-registration: **osf.io/pvb5j** (DOI **10.17605/OSF.IO/PVB5J**) — candidate-locus design, 50 regions, 5 traits.
- Existing amendment: **osf.io/az52u** — distal-gene expansion, April 2026 (PDF posted).
- New amendment (this document's posting): adds 4 traits (CAD, lipids, eGFR, HbA1c); expands region generation from candidate-locus to genome-wide; adds MTAG, CPASSOC, HyPrColoc, PolyFun, AoU AFR LD; declares Track A as pre-specified methods validation subset; does not retract any prior analyses.

### 9.3 Draft amendment text (for OSF paste)

The following block is the proposed amendment body. Carter may adapt phrasing but the technical commitments are intended to be verbatim.

> **Amendment to pre-registration osf.io/pvb5j: genome-wide pleiotropy discovery expansion**
>
> **Date**: 2026-[M1 completion month]
>
> **Investigator**: Carter K. Clinton, NCSU ASHES Lab
>
> **Purpose of amendment**: This amendment expands the scope of the coloc_analysis pre-registration from a candidate-locus analysis across 5 traits to a genome-wide, joint-signal, multi-trait analysis across 9 traits in EUR and AFR ancestries with two co-equal pre-registered scientific aims: (i) cross-trait pleiotropy discovery and (ii) novel single-trait and joint-signal variant discovery. The original candidate-locus analysis is retained as a pre-specified methods-validation subset and will be reported separately (see Track A below).
>
> **Motivation**: The original candidate-locus design identified 50 hand-curated regions tiled into 205 analysis windows around 8 seed pleiotropic loci drawn from published cross-trait literature. Fine-mapping and colocalization within this set quantifies the replication rate of prior claims under current best-practice methods (SuSiE-RSS with real, matched-ancestry LD), which is informative but does not itself support discovery-level inference about the broader genomic architecture of pleiotropy. Genome-wide region generation using multi-trait methods (MTAG, Turley et al. 2018, *Nature Genetics*; CPASSOC, Zhu et al. 2015, *Am J Hum Genet*) is required for non-circular discovery.
>
> **Expanded trait inventory**: (1) BMI — Yengo 2022 EUR, PAGE+AoU AFR, continuous inverse-rank-normal; (2) T2D — DIAMANTE 2022 (Mahajan et al. 2022, *Nature*) trans-ancestry case-control; (3) Stroke — GIGASTROKE 2022 (Mishra et al. 2022, *Nature*) trans-ancestry all-stroke case-control; (4) SBP — Evangelou 2018 (*Nature Genetics*) EUR continuous, Giri 2020 (*Hypertension*) MVP AFR; (5) Asthma — GBMI 2022 (Zhou et al. 2022, *Cell Genomics*) trans-ancestry pooled adult + child; (6) CAD — Aragam 2022 (*Nature Genetics*) EUR case-control; (7) Lipids — GLGC 2021 (Graham et al. 2021, *Nature*) multi-ancestry, LDL-C primary, HDL/TG/TC secondary; (8) eGFR — CKDGen 2019 (Wuttke et al. 2019, *Nature Genetics*) multi-ancestry continuous; (9) HbA1c — MAGIC 2021 (Chen et al. 2021, *Nature Genetics*) multi-ancestry continuous.
>
> **New analytical commitments**: (a) per-ancestry PLINK clumping (p=5e-8, r²<0.01, 1 Mb) with MTAG and CPASSOC novel-loci added to the union region list; (b) MTAG with LDSC-intercept-based `--overlap` correction for UKB and MVP cohort overlap, max_FDR filter to control constant-covariance violation; (c) two-stage coloc (ABF triage followed by SuSiE-RSS on PP.H4 > 0.5 regions) with region-level PP.H4 FDR correction; (d) HyPrColoc across ≥3 traits for shared-architecture inference; (e) PolyFun baselineLF2 functional priors for rescue of underpowered credible sets; (f) All of Us controlled-tier WGS (~100k AFR) as the AFR LD panel, computed inside the AoU Researcher Workbench with only summary-level LD exported per AoU data-egress policy, replacing 1000G AFR (N=661) as the AFR default; (g) L2G (Open Targets, Mountjoy 2021) and Borzoi (Linder 2024) for gene and variant-level resolution on Tier A signals.
>
> **Pre-registered novel-variant discovery aim**: In addition to cross-trait pleiotropy claims, this analysis pre-registers four operational definitions of variant-level novelty, each with a locked comparator catalog. (i) **Novel joint-signal loci** = MTAG p < 5e-8 OR CPASSOC p < 5e-8, AND no contributing single-trait association at p < 5e-8 within ±500 kb per GWAS Catalog vYYYY-MM-DD (locked at M5 cross-reference date). (ii) **Novel ancestry-specific loci (AFR)** = AFR PP.H4 ≥ 0.8 with credible-set size ≤ 25, OR AFR single-trait lead variant at p < 5e-8 with no overlapping EUR signal at p < 1e-5 within ±500 kb. (iii) **Novel pleiotropy loci** = cross-trait PP.H4 ≥ 0.8 (pairwise coloc) or HyPrColoc PP ≥ 0.8 (≥3 traits), AND not reported as cross-trait shared in {Pickrell 2016 *Nature Genetics* supplement, Watanabe 2019 GWAS Atlas, Open Targets Genetics L2G top-3} as locked on M5 cross-reference date. (iv) **Novel secondary-signal loci** = SuSiE-RSS credible-set index ≥ 2 with CS purity ≥ 0.5 and PIP_max ≥ 0.5, AND lead variant of secondary CS not within ±100 kb of prior GWAS Catalog v_lock entry for the same trait. All catalog versions, download URLs, and SHA-256 checksums will be reported in the manuscript supplement. Functional-mechanism novelty (Borzoi/Enformer-driven) is reported as supplementary mechanistic context, not a primary novelty claim.
>
> **Track A (pre-specified methods-validation subset)**: The original 50-region candidate-locus analysis has been completed and will be published as a separate short-form methods paper reporting the fraction of published cross-trait pleiotropy claims in the candidate set that survive real-LD re-analysis. This is pre-specified validation ahead of discovery and does not involve data-dependent region reselection.
>
> **What is not changing**: ancestry-stratified analysis plan (EUR + AFR); preference for trans-ancestry discovery then ancestry-stratified replication; commitment to open Snakemake pipeline release; commitment to OSF deposit of post-registration outputs.
>
> **Expected timeline**: M1 harmonization complete (this amendment posted at the end of M1); M2–M6 follow. Full milestone table available at the companion repository path `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`.

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| **AoU data-egress policy rejects LD matrix export** | Blocks M3 AFR LD; blocks AFR fine-mapping at scale | Pre-consult with AoU Data Access Committee before M3 execution; exported artifact is summary-only LD matrix + AF metadata (no individual-level data); fallback to 1000G AFR + Pan-UKBB AFR merged panel (~5k) with explicit power caveats |
| **AFR power ceiling even with AoU LD** | Many AFR signals remain underpowered; AFR claims downgraded to replication-only | Frame manuscript as EUR-discovery with AFR-replication-where-possible; PolyFun functional priors for rescue; report N_credible-variant distributions per ancestry |
| **MTAG `--overlap` insufficiently corrects UKB/MVP inflation** | False-positive novel loci in MTAG output inflates discovery claim | Orthogonal CPASSOC required-corroboration filter; max_FDR ≤ 0.05 per Turley 2018; mtCOJO sensitivity check on top-N MTAG novel loci |
| **Compute blowup at M4 genome-wide SuSiE** | LSF queue saturation; multi-week runtimes | Two-stage ABF → SuSiE gate cuts compute 10–20×; PP.H4 > 0.5 triage; parallelize by chromosome × ancestry; expected ~500× T1 compute, multi-week LSF |
| **Reviewer pushback on scope expansion** ("did you cherry-pick post-hoc?") | Rejection or major-revision at submission | OSF amendment posted before M2 MTAG run (Section 9.1); Track A paper demonstrates honest reporting of candidate-locus result ahead of discovery; pre-registration history is fully public including the 2026-04-14 checkpoint artifacts |
| **OSF pre-registration disclosure — timing of amendment** | Perception of post-hoc rationalization if amendment posts too late | Amendment posts at end of M1, before any MTAG/CPASSOC result is computed; amendment cites concrete harmonized-sumstats checksums, not aspirational data |
| **Sumstats DUA delays (MVP, DIAMANTE restricted strata)** | M1 slips by weeks to months | Parallel DUA requests from Day 1 of M0 per the REQ-1 convention; fallback to public strata only where restricted strata delay |
| **HyPrColoc assumptions fail on >5-trait blocks** | Overconfident shared-signal claims | Cap HyPrColoc at 3–5 traits per block per Foley 2021; sensitivity analysis against pairwise coloc on all pairs within the block |
| **Borzoi scoring non-reproducibility on novel regions** | Variant-prioritization figure weakens | Report Borzoi scores only for Tier A credible sets; note Linder 2024 training-distribution caveats; treat as supplementary, not primary, evidence |
| **Novelty-comparator catalog version drift** | "Novel" claims at submission may not be novel by revision-cycle catalog (GWAS Catalog updates monthly) | Lock catalog versions at M5 cross-reference date with SHA-256 checksums; report version+date in manuscript and supplement; for any locus that becomes non-novel under updated catalogs during review, report both the locked-version status (primary claim) and the updated-version status (transparent supplement) — do not silently rebase claims to newer catalogs |
| **MTAG joint-signal "novelty" inflated by UKB sample overlap if `--overlap` correction underperforms** | Class 1 novel loci are statistical artifacts of correlated noise across overlapping subjects, not real biology | Mandatory LDSC intercept matrix as `--overlap` input per Turley 2018; CPASSOC orthogonal-corroboration filter (intersection requirement for high-confidence Class 1); mtCOJO sensitivity check on top-N MTAG-novel loci; report MTAG-only vs MTAG ∩ CPASSOC counts separately |
| **Secondary-signal (Class 3) novelty vulnerable to LD-panel sensitivity** | Secondary CSs that appear in one LD panel may disappear under another, undermining the claim | Run SuSiE-RSS with both 1000G+UKB EUR panel and AoU EUR sub-panel as a parity check on a randomized chromosome subset; report secondary-CS replication rate; downgrade secondary-CS novel claims that fail the cross-panel consistency check |
| **Reviewer critique that joint-signal "novelty" is purely a statistical artifact of borrowing strength** | Class 1 claims dismissed as not biologically novel, only statistically convenient | Pre-register the cross-method (MTAG ∩ CPASSOC) requirement for high-confidence Class 1; report colocalization status of Class 1 loci across the contributing traits as biological corroboration (a true joint-signal locus should also colocalize); discuss the borrowing-strength concern explicitly in the Discussion rather than letting reviewers raise it |

---

## 11. Timeline

Calendar estimates assume Carter works single-threaded, one milestone at a time, with no blocking DUA delays beyond those already anticipated. LSF availability and AoU Workbench iteration are the dominant schedule risks.

| Milestone | Calendar estimate | Target end-month |
|---|---|---|
| M0 pivot scaffolding | 1–2 weeks | 2026-05 |
| M1 sumstats upgrade + harmonization | 4–6 weeks | 2026-06 / 2026-07 |
| M2 LDSC + MTAG + CPASSOC | 6–8 weeks | 2026-08 / 2026-09 |
| M3 AoU AFR LD build | 4–6 weeks (partially parallel with M2) | 2026-09 / 2026-10 |
| M4 scalable coloc + fine-mapping | 8–12 weeks | 2026-12 / 2027-01 |
| M5 variant→gene prioritization + novelty cross-reference | 4–6 weeks (includes ~2–3 days catalog cross-reference annotation) | 2027-02 |
| M6 manuscript + replication + submission | 8–12 weeks | 2027-04 / 2027-05 |

Track A submission (methods paper) targets 2026-05 / 2026-06, running in parallel with M1.

---

## 12. Integration with Existing .planning/ Scaffold

| File | Required update |
|---|---|
| `PROJECT.md` | Replace scope section with 9-trait × 2-ancestry genome-wide framing; add "Track A / Track B" structural note; preserve constraints block verbatim |
| `ROADMAP.md` | Retire T1 milestone description as "complete and repurposed as candidate-locus validation subset"; insert M0–M6 milestone table from Section 3; preserve phase-history appendix |
| `REQUIREMENTS.md` | Add REQ-2 through REQ-N covering: genome-wide region generation (MTAG + CPASSOC union), AoU AFR LD mandate, two-stage coloc gate, HyPrColoc 3+ traits, PolyFun priors, L2G+Borzoi gene/variant prioritization, OSF amendment timing constraint (post after M1, before M2), and the four pre-registered novel-variant operational definitions from Section 7 (Classes 1–4 with thresholds; Class 5 as supplementary) |
| `DECISIONS.md` | Append ADR-2026-04-22-01 "Genome-wide reframe" (this document); ADR-2026-04-22-02 "AoU AFR LD default"; ADR-2026-04-22-03 "Track A as candidate-locus validation subset"; ADR-2026-04-22-04 "MTAG --overlap non-negotiable for UKB/MVP pairs"; ADR-2026-04-22-05 "Novel-variant discovery as co-equal aim with locked comparator catalogs (GWAS Catalog, Pickrell 2016, Watanabe 2019, Open Targets Genetics L2G)" |
| `STATE.md` | Mark T1 spine "repurposed as candidate-locus validation subset"; set current milestone to M0; unblock CP#1-final contingent on M0 scaffolding commit |
| `osf_prereg_draft.md` | Add a NEW subsection at end of file containing the Section 9.3 draft amendment text; do not edit original content |
| `osf_deviations.md` | Add entry for 2026-04-22 noting that the genome-wide reframe supersedes the distal-gene expansion amendment's scope while preserving its substantive commitments |
| `data_access.md` | Add rows for DIAMANTE 2022, GIGASTROKE 2022, Yengo 2022, GBMI asthma 2022, Aragam 2022 CAD, GLGC 2021 lipids, CKDGen 2019 eGFR, MAGIC 2021 HbA1c, Giri 2020 MVP SBP AFR; add AoU controlled-tier DUA status row |

---

## 13. Companion Documents

- **`TRACK-A-PIVOT.md`** — short-form methods paper strategy: repositioning of ajhg_manu_v10.pdf from "identified 28 pleiotropic signals" to "quantifies real-LD survival rate of published candidate-locus pleiotropy claims"; title without "Machine Learning"; venue ladder Genome Medicine → AJHG short report → Bioinformatics; 2–4 week submission horizon.
- **`SUMSTATS-UPGRADE.tsv` / `SUMSTATS-UPGRADE.md`** — per-trait upgrade plan with source URL, release date, N, ancestry coverage, UKB/MVP overlap flags, DUA status, checksum-to-record on download, pre-MTAG QC criteria.
- **`AOU-LD-PIPELINE.md`** — AoU Researcher Workbench (Terra) implementation plan for the AFR LD panel: environment setup, region-by-region LD matrix computation, data-egress policy compliance (summary-only export), expected runtime per region, verification against 1000G AFR for EUR-overlap regions as sanity check.

---

## Decision pending

- **Exact MTAG `max_FDR` threshold**: Turley 2018 suggests 0.05 but some downstream papers use 0.01 for pleiotropy applications — locking in M2 kickoff.
- **ABF-coloc PP.H4 triage threshold for SuSiE gate**: 0.5 is a reasonable default but may be tuned empirically during M4 pilot on a single chromosome.
- **HyPrColoc max block size**: 3 vs 5 traits — depends on LDSC rg matrix sparsity pattern; decide in M2 once rg is computed.
- **Tier A / B / C classification cutoffs at genome-wide scale**: current T1 cutoffs were tuned for the 50-region design; genome-wide FDR control will require recalibration in M4.
- **Whether to include BBJ EAS as a third ancestry**: Carter has not committed. EAS AFR-independent replication would strengthen the paper but adds an LD panel and a DUA. Flagged for M1 checkpoint discussion.
- **Class 1 prior-art window (±500 kb)**: chosen to match Turley 2018 + standard pleiotropy-novelty practice but ±250 kb (stricter) and ±1 Mb (more lenient) are defensible. Carter to sanity-check before OSF amendment posts at end of M1.
- **Class 2 AFR-specific MAF gating (MAF_AFR ≥ 0.01 with MAF_EUR < 0.005)**: a single defensible operational cutoff but the literature also uses MAF_EUR < 0.001 (very rare in EUR) for "AFR-specific haplotype" claims. Carter to confirm whether to tighten.
- **Class 3 secondary-signal CS purity (≥ 0.5) and PIP_max (≥ 0.5) thresholds**: SuSiE-RSS defaults are 0.5 / 0.5 but the field has migrated toward 0.5 / 0.95 for "high-confidence single-variant" claims. The ≥ 0.5 PIP_max chosen here is permissive to avoid over-filtering legitimate secondary signals at lower-power loci; Carter to confirm.
- **Class 4 pleiotropy-comparator set composition**: locked to {Pickrell 2016, Watanabe 2019, Open Targets Genetics L2G top-3}. Open question: should EBI GWAS Catalog cross-trait shared-locus annotation also be included as a fourth comparator? Adding it tightens novelty but the cross-trait annotation in GWAS Catalog is sparse and inconsistently maintained; Carter's call.
- **GWAS Catalog version-lock date**: proposed at M5 cross-reference date (concretely 2027-01 / 2027-02 if timeline holds), but if Carter prefers an earlier lock (e.g., M2 kickoff date) for stronger pre-registration, the manuscript would also need a delta-analysis showing what changed between lock-date and submission.
- **Whether to claim Class 5 (functional-mechanism novel) as a primary or supplementary novelty axis**: currently scoped as supplementary because Borzoi/Enformer training-distribution caveats apply. Carter may want to elevate Class 5 to primary if a small number of variants have unusually high cross-tissue effect scores and clean prior-art negation; defer until M5 results are in hand.

---

*End of amendment.*
