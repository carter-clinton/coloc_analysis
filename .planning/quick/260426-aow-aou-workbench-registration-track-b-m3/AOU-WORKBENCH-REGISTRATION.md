# All of Us Researcher Workbench — Workspace Registration

**Project:** coloc_analysis Track B + M3 (AFR LD reference panel build)
**PI:** Carter K. Clinton, ASHES Lab, North Carolina State University
**ORCID:** 0000-0003-2669-8200
**Email:** carterclinton@carterclinton.com
**OSF root pre-registration:** [osf.io/pvb5j](https://osf.io/pvb5j) (DOI [10.17605/OSF.IO/PVB5J](https://doi.org/10.17605/OSF.IO/PVB5J))
**OSF amendment record:** [osf.io/az52u](https://osf.io/az52u)
**Workspace scope:** Track B + M3 only — see "Track A explicit omission" at the end of the Scientific Approach section.
**Workspace tier required:** Controlled Tier (whole-genome sequence access)
**Drafted:** 2026-04-26

> **Paste-time note.** This document is sized conservatively for the AoU
> Researcher Workbench Research Purpose Statement (RPS) form. Each
> section header corresponds to a portal field; **trim each section to
> the live portal character limit at paste time** (limits typically range
> 1,000–4,000 characters per RPS sub-prompt and may change). All factual
> claims carry inline `[src: <path> §<section>]` footnotes pointing back
> into the project's planning artifacts so accuracy can be verified
> before paste. **Track A is explicitly out of scope for this workspace
> and does not need AoU access** — see the explicit-omission paragraph at
> the end of "Scientific Approach."

---

## 1. Workspace Title

> Cross-trait pleiotropy and novel-variant discovery across nine
> cardiometabolic, metabolic, and respiratory traits in European and
> African ancestries, using All of Us controlled-tier whole-genome
> sequencing as the African-ancestry linkage-disequilibrium reference
> panel.

`[src: .planning/PROJECT.md "What" §Track B; .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §1, §5]`

---

## 2. Research Summary (Plain-Language Summary)

Genome-wide association studies have identified thousands of common
genetic variants associated with cardiometabolic, metabolic, and
respiratory traits, but turning a statistical signal into a putative
causal variant — fine-mapping — depends critically on a
linkage-disequilibrium (LD) reference panel that matches the ancestry
composition of the people contributing to the original GWAS. For
European-ancestry signals, ample LD references exist. For
African-ancestry signals, the field default has been the 1000 Genomes
Phase 3 AFR superpopulation of n = 661 participants — too small for
stable LD estimates and demographically unrepresentative of the admixed
African-American populations dominating modern GWAS cohorts (MVP, the
PAGE consortium, and All of Us itself).
`[src: .planning/amendments/AOU-LD-PIPELINE.md §1]`

This project will use All of Us controlled-tier whole-genome sequencing
(target n ≈ 60,000–95,000 African-ancestry participants post-QC) to
build per-region LD correlation matrices that are ancestry-matched at
roughly 100× the sample size of 1000G AFR.
`[src: .planning/amendments/AOU-LD-PIPELINE.md §3.3]`
These matrices will then drive genome-wide cross-trait pleiotropy
discovery and novel-variant identification across nine complex traits in
European and African ancestries
`[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §4]`,
directly addressing the underrepresentation of African-ancestry
populations in post-GWAS fine-mapping. All All-of-Us-derived outputs
that leave the workbench will be aggregate summary statistics
(per-region LD matrices, validation memos, QC tables); no individual
participant data will be exported.
`[src: .planning/amendments/AOU-LD-PIPELINE.md §7; .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md paragraph (f)]`

---

## 3. Scientific Approach

The project executes Track B milestones M0–M6 of the coloc_analysis
program (overall pre-registration osf.io/pvb5j, DOI 10.17605/OSF.IO/PVB5J;
amendment record osf.io/az52u).
`[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §3, §9.2]`
The five-step analytical pipeline:

1. **Sumstats harmonization (M1, complete 2026-04-25).** Nine published
   GWAS summary-statistics datasets covering BMI, type-2 diabetes,
   stroke, systolic blood pressure, asthma, coronary artery disease,
   lipids (LDL primary; HDL/TG/TC secondary), eGFR, and HbA1c are
   harmonized to GRCh37 with frozen SHA-256 checksums per ancestry
   stratum (EUR + AFR; trans-ancestry where the source releases it).
   `[src: .planning/PROJECT.md "Current status" §M1; .planning/amendments/SUMSTATS-UPGRADE.tsv]`

2. **Genetic-correlation matrix (M2).** LDSC (Bulik-Sullivan 2015) with
   per-pair bivariate intercepts; the intercept matrix is the input to
   MTAG `--overlap` so that overlap-driven sample correlation across
   the UK Biobank–saturated trait set is correctly modeled.
   `[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §6 #1, #2]`

3. **Multi-trait joint-signal discovery (M2).** MTAG (Turley 2018) with
   `--overlap` for multi-trait amplitude boost of per-variant z-scores
   under a constant-covariance assumption; CPASSOC (Zhu 2015) SHom and
   SHet statistics as the orthogonal joint-signal test that does **not**
   assume constant covariance. Cross-method intersection (MTAG ∩ CPASSOC)
   yields the high-confidence joint-signal subset; per-trait PLINK
   clumping (p < 5e-8, r² < 0.01, 1 Mb) plus the joint-signal additions
   produces a discovery region union of approximately 1,500–3,000
   ~2 Mb fine-mapping windows.
   `[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §6 #2, #3, #4]`

4. **AFR LD reference panel build (M3, this workspace).** Inside the
   AoU Researcher Workbench: cohort-define genetically-inferred AFR
   participants (`ancestry_pred == 'afr'`), prune at KING ≥ 0.0442,
   apply per-ancestry variant QC (MAF ≥ 0.005, call rate ≥ 0.95, HWE
   p ≥ 1×10⁻⁶, exclude AoU-flagged variants), then for each
   discovery region compute a Pearson correlation LD matrix from
   genotype dosages via `hl.ld_matrix()` on a Hail BlockMatrix
   (Path A, primary) with PLINK `--r square` as a per-region fallback
   (Path B). An optional EUR sensitivity panel (target n ≈ 130k–150k
   AoU EUR) is built on the same regions to validate AoU LD against
   1000G EUR.
   `[src: .planning/amendments/AOU-LD-PIPELINE.md §3, §4, §5.1, §5.2]`

5. **Genome-wide fine-mapping, colocalization, and prioritization
   (M4–M5, NCSU side).** Two-stage scalable colocalization — fast ABF
   coloc (Giambartolomei 2014; Wallace 2020) genome-wide as a triage
   filter, then SuSiE-RSS (Zou 2022) on regions with PP.H4 > 0.5, with
   PolyFun baselineLF2 functional priors (Weissbrod 2020) for rescue of
   underpowered AFR credible sets; HyPrColoc (Foley 2021) for
   ≥3-trait shared-architecture inference; L2G / Open Targets Genetics
   (Mountjoy 2021) for variant-to-gene prioritization; Borzoi
   (Linder 2024) and Enformer (Avsec 2021) variant-effect scoring on
   Tier A credible-set variants for tissue-specific mechanistic context.
   `[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §6 #5–#11]`

### Track A explicit omission

**Track A** of the coloc_analysis program — a short-form methods paper
re-analyzing 50 curated cardiometabolic candidate-locus pleiotropy
claims under fully pre-registered SuSiE-RSS + coloc.susie with real LD
on 10 EUR autosomal regions — uses **only 1000 Genomes Phase 3 EUR
(n = 503)** as its real-LD reference and only publicly-available GWAS
summary statistics. Track A requires **no All of Us controlled-tier
access**, is scientifically independent of Track B per the project
amendment, and is being finalized for submission to *Genome Medicine*
(primary) → *AJHG* short report (fallback 1) → *Bioinformatics
Applications Note* (fallback 2) in the 2026-05 / 2026-06 window, ahead
of this AoU-workbench-dependent Track B work. **This workspace
registration covers Track B + M3 only.**
`[src: .planning/PROJECT.md "What" §Track A, "Why" paragraph; .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §8; .planning/amendments/TRACK-A-PIVOT.md §1]`

---

## 4. Methods Inventory

| # | Method | Purpose | Citation | Ancestry strata | Milestone | AoU-specific notes |
|---|---|---|---|---|---|---|
| 1 | **LDSC** | Genetic-correlation matrix + bivariate intercepts (input to MTAG `--overlap`) | Bulik-Sullivan 2015 | EUR, AFR | M2 | None — runs on harmonized sumstats outside AoU |
| 2 | **MTAG `--overlap`** | Multi-trait z-score boost with sample-overlap correction; `max_FDR` filter for constant-covariance violations | Turley 2018 *Nat Genet* | EUR, AFR | M2 | None — outside AoU |
| 3 | **CPASSOC (SHom / SHet)** | Orthogonal joint-signal test (no constant-covariance assumption); cross-method corroboration of MTAG | Zhu 2015 *AJHG* | EUR, AFR | M2 | None — outside AoU |
| 4 | **PLINK clumping** | Per-trait genome-wide region definition (`--clump p < 5e-8 r² < 0.01 1 Mb`); union with MTAG/CPASSOC novel = discovery region BED | — | EUR, AFR | M2 | None — outside AoU |
| 5 | **ABF-coloc** | Compute-linear approximate-Bayes-factor coloc as a genome-wide triage filter (PP.H4 > 0.5 gates entry to SuSiE-RSS) | Giambartolomei 2014; Wallace 2020 | EUR, AFR | M4 | None — outside AoU |
| 6 | **SuSiE-RSS** | Bayesian fine-mapping with reference standard error; per-region credible sets and PIPs; L = 10 default | Zou 2022 *Biostatistics* | EUR, AFR | M4 | **AFR fine-mapping consumes AoU-derived LD (M3 output) as the primary innovation** |
| 7 | **HyPrColoc** | Simultaneous coloc across ≥3 traits when shared architecture exists | Foley 2021 *Commun Biol* | EUR, AFR | M4 | None — outside AoU |
| 8 | **PolyFun baselineLF2** | Functional-annotation-informed priors to rescue underpowered SuSiE-RSS credible sets (especially AFR) | Weissbrod 2020 *Nat Methods* | EUR, AFR | M4 | None — outside AoU |
| 9 | **mtCOJO** | Sensitivity check (MR-style conditioning on multiple traits) when post-MTAG mean χ² > 1.2 and LDSC intercept > 1.1 still hold | Zhu 2018 *Genet Epidemiol* | EUR, AFR | M2 sensitivity | None — outside AoU |
| 10 | **L2G / Open Targets Genetics** | Variant-to-gene prioritization (distance + chromatin + ML features); reference catalog for Class 4 novelty | Mountjoy 2021 *Nat Genet* | EUR, AFR | M5 | None — outside AoU |
| 11 | **Borzoi / Enformer** | Deep-learning variant-effect scoring for tissue-specific RNA-seq tracks; Tier A credible-set variants only | Linder 2024; Avsec 2021 *Nat Genet* | EUR, AFR | M5 | None — outside AoU |
| 12 | **Hail `hl.ld_matrix()`** | **AFR LD matrix computation inside AoU** — Pearson correlation of genotype dosages, BlockMatrix → dense float32 NPZ per region; PLINK `--r square` fallback for OOM regions | — | AFR (primary), EUR (optional sensitivity) | M3 | **In-workbench Dataproc Hail v0.2.x — only summary-level NPZ matrices exported per AoU policy** |

`[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §6 (Method Stack); .planning/amendments/AOU-LD-PIPELINE.md §5.1 (Hail BlockMatrix), §5.2 (PLINK fallback); SuSiE-RSS L=10 default per §9.3]`

---

## 5. Components & Notebooks Inventory

### 5.1 Inside the All of Us Researcher Workbench (Terra-hosted Google Cloud)

All individual-level computation occurs inside the workbench. Compute
substrate is Dataproc + Hail v0.2.x; orchestration is via Jupyter
notebooks in the workspace.
`[src: .planning/amendments/AOU-LD-PIPELINE.md §5, §11]`

| # | Component | Environment | Inputs | Outputs | Storage |
|---|---|---|---|---|---|
| AOU-1 | **Cohort definition + QC notebook** (Python / Hail) | Dataproc, Hail v0.2.x | AoU v7 WGS MatrixTable; ancestry-prediction HT (`ancestry_pred`); precomputed relatedness HT | Checkpointed `mt_afr_qc.mt` (n ≈ 60–95k samples post-QC; ~9M variants post-MAF/HWE/call-rate/AoU-flag filtering) | Workspace bucket `gs://fc-secure-<workspace-id>/ld/` |
| AOU-2 | **Per-region LD matrix computation notebook** (Python / Hail) | Dataproc, Hail v0.2.x | `mt_afr_qc.mt`; region manifest TSV (per-region chr/start_grch38/end_grch38, ancestry, source_trait, lead_variant) | Per-region `.npz` (lower-triangular float32 LD + variant_ids + rsids) | Workspace bucket then exported via AoU review |
| AOU-3 | **Optional EUR sensitivity panel notebook** (Python / Hail) | Dataproc, Hail v0.2.x | Same as AOU-1/AOU-2 with `ancestry_pred == 'eur'`; target n ≈ 130–150k post-QC | Per-region `.npz` for AoU-EUR (LD matrices for cross-ancestry sensitivity vs 1000G EUR) | Workspace bucket then exported via AoU review |
| AOU-4 | **4-check validation memo notebook** (R) | Jupyter (R kernel) | AoU AFR LD matrices (10 dev regions); known-locus published LD heatmaps; AoU EUR LD; identity-placeholder LD comparator | Validation memo (Check 1: known-locus LD pattern vs published; Check 2: AoU EUR vs 1000G EUR Pearson r per cell ≥ 0.97 for MAF ≥ 0.05; Check 3: SuSiE-RSS convergence + ≥1 CS at PIP coverage 0.95 with median CS ≤ 30 variants on AFR BMI 16q12; Check 4: identity-placeholder A/B yield differential) | TSV + PNG figures, summary-only export |
| AOU-5 | **LD QC log writer** (Python pandas) | Dataproc | Per-region run results | `ld_afr_run_log.tsv` (region_id, status, n_var, out_path, wall_time) | Summary TSV, exportable |

`[src: .planning/amendments/AOU-LD-PIPELINE.md §5.1 (Path A pseudocode), §3.3 (target N), §9.1–§9.4 (4-check validation)]`

### 5.2 Outside the All of Us Researcher Workbench (NCSU GPFS)

Downstream consumption of the exported summary-level artifacts.

| # | Component | Environment | Inputs | Outputs |
|---|---|---|---|---|
| NCSU-1 | **NPZ → RDS conversion** (`src/scripts/ld_npz_to_rds.R` via reticulate) | NCSU GPFS, R + Python | Exported `.npz` per region | `data/processed/ld_reference/AFR_aou/{region_id}.rds` (xz-compressed) |
| NCSU-2 | **Snakemake LD reference build rule** (`rule build_ld_rds_aou_afr` in `src/snakemake/rules/ld_reference.smk`) | LSF cluster + conda | NPZ batches | RDS batches integrated with existing 1000G EUR/AFR rules |
| NCSU-3 | **Fine-mapping pipeline** (existing M4 rules; `config/finemap.yaml` selector `ld_panel.AFR: aou`) | LSF + conda | Region BED + harmonized sumstats + AFR_aou RDS | SuSiE-RSS credible sets, PIP tables |
| NCSU-4 | **Coloc / HyPrColoc / PolyFun pipeline** (existing M4 rules) | LSF + conda | SuSiE-RSS outputs + cross-trait sumstats | PP.H4 tables, HyPrColoc shared-architecture outputs |
| NCSU-5 | **Manuscript assembly** | Local R + LaTeX | All M4–M5 outputs + 4-check validation memo + AoU acknowledgment template | Track B Nature Genetics manuscript; M3 Scientific Data data descriptor |

`[src: .planning/amendments/AOU-LD-PIPELINE.md §8.1 (target layout), §8.2 (NPZ → RDS converter), §8.3 (Snakemake rule), §8.4 (config flag)]`

---

## 6. Data Use and Egress Plan (per OSF Amendment paragraph (f))

### 6.1 Egress paragraph — mirrored verbatim from the OSF amendment

The egress framing for this workspace is the same paragraph posted to
the OSF amendment record at osf.io/az52u so that AoU registration and
OSF pre-registration cannot drift:

> **(f) All of Us Controlled Tier Whole Genome Sequencing
> (~100,000 AFR individuals) as the AFR LD reference panel, computed
> inside the All of Us Researcher Workbench with only summary-level LD
> matrices exported per the All of Us data-egress policy. This replaces
> 1000 Genomes AFR (N = 661) as the AFR LD default — an approximately
> 150-fold sample size upgrade.**

`[src: .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md paragraph (f); .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §5]`

### 6.2 Permitted exports (post AoU review)

| Artifact | Classification | Format | Approximate aggregate size | Approval pathway |
|---|---|---|---|---|
| Per-region LD matrices | Aggregate summary statistics — every cell is computed across all n ≈ 60–95k participants, well above the ≥ 20-person suppression floor | Lower-triangular float32 `.npz` with variant_ids + rsids | 500 GB – 1 TB compressed across 1,500–3,000 regions | Standard AoU export review (per-chromosome bundled requests) |
| Validation heatmaps + figures | Research results, no participant-level data | PNG / PDF | < 100 MB | No additional review |
| LD QC summary table | Region-level metadata (counts, convergence flags, wall times) | TSV | < 10 MB | No additional review |
| Manuscript results tables | Publication-ready aggregate summary | TSV / supplementary tables | 10 – 100 MB | AoU manuscript-disclosure review |

`[src: .planning/amendments/AOU-LD-PIPELINE.md §7.1 (two-stage export path), §7.2 (file size + throughput), §13.4 (data availability statement)]`

### 6.3 Explicit prohibitions

- ✗ **Individual-level genotypes** — never exported.
- ✗ **Sample-level metadata** (phenotypes, covariates, demographics) — never exported.
- ✗ **Cell counts < 20** — must suppress; LD-matrix computation across the full n ≈ 60–95k cohort means no cell is computed from < 20 participants, so this floor is satisfied by construction.
- ✗ **Re-import of exported aggregates as individual-level data** — never attempted.

`[src: .planning/amendments/AOU-LD-PIPELINE.md §7.1, §1 (RPS template "no individual-level genotypes or phenotypes will be exported, and no cell counts below 20")]`

### 6.4 Manuscript publication pathway

- **Methods paragraph** in the Track B Nature Genetics manuscript will use the templated language describing AoU v7 controlled-tier WGS, KING kinship cutoff 0.0442, ancestry restriction (`ancestry_pred == 'afr'`), variant QC filters, and Hail v0.2.x LD computation. `[src: .planning/amendments/AOU-LD-PIPELINE.md §13.1]`
- **Acknowledgments** will reproduce the standard AoU funding-acknowledgment block (verified at submission against current AoU guidance). `[src: .planning/amendments/AOU-LD-PIPELINE.md §13.2]`
- **Required citation:** "The All of Us Research Program (ClinicalTrials.gov Identifier: NCT03658122)." `[src: .planning/amendments/AOU-LD-PIPELINE.md §13.3]`
- **Data availability statement:** "Aggregate LD matrices derived from All of Us data will be deposited in Zenodo at publication, after All of Us review and approval. Individual-level All of Us data are not publicly available; qualified researchers may apply for controlled-tier access at researchallofus.org." `[src: .planning/amendments/AOU-LD-PIPELINE.md §13.4]`

### 6.5 Publications & Presentations (P&P) draft registration

A draft P&P registration will be filed in the AoU Researcher Workbench
**before any manuscript submission**, in accordance with AoU
publication-disclosure requirements. The draft is registered at the
draft stage and updated at major changes; final disclosure precedes the
Track B Nature Genetics submission.
`[src: .planning/amendments/AOU-LD-PIPELINE.md §2 prerequisite P6, §12 risk R6]`

---

## 7. Anticipated Findings

Track B pre-registers two co-equal scientific aims — cross-trait
pleiotropy discovery and novel-variant discovery across five
operationally-defined classes — each with an honest, order-of-magnitude
yield estimate based on rates from comparable published studies. These
priors are reported in the manuscript so reviewers can audit whether
the realized yield is in or out of expectation.
`[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §7.1, §7.3]`

| Class | Definition (summary) | Expected yield | Notes |
|---|---|---|---|
| **Class 1 — Joint-signal novelty** | (MTAG p < 5e-8 OR CPASSOC p < 5e-8) AND max(single-trait p) ≥ 5e-8 AND no single-trait GWS hit within ±500 kb in GWAS Catalog v_lock | **50–200 loci** | Cross-method intersection (MTAG ∩ CPASSOC) yields the high-confidence subset |
| **Class 2 — Ancestry-specific novelty (AFR)** | AFR PP.H4 ≥ 0.8 with credible-set size ≤ 25 AND (no overlapping EUR coloc signal at the same locus, OR AFR lead variant MAF_AFR ≥ 0.01 with MAF_EUR < 0.005) | **5–30 loci** | Direct beneficiary of the AoU AFR LD panel; AFR sample-size ceiling caps yield |
| **Class 3 — Secondary-signal novelty** | SuSiE-RSS credible-set index ≥ 2 AND CS purity ≥ 0.5 AND PIP_max(CS) ≥ 0.5 AND lead variant of CS index ≥ 2 not within ±100 kb of prior GWAS Catalog v_lock entries | **100–400 secondary CSs** | Within-locus independence rather than new-locus discovery |
| **Class 4 — Pleiotropy-class novelty** | Cross-trait PP.H4 ≥ 0.8 (pairwise) or HyPrColoc PP ≥ 0.8 (≥3 traits) AND not in Pickrell 2016, Watanabe 2019, or Open Targets L2G top-3 at v_lock | **30–150 trait-pair-locus combinations** | Densest novelty axis once the genome-wide pipeline runs |
| **Class 5 — Functional-mechanism novelty** | Top-decile Borzoi/Enformer tissue-specific effect score on Tier A credible-set lead variant AND no ClinVar pathogenic AND no prior PubMed functional characterization | **10–50 variants** | Reported as supplementary mechanistic context, not primary novelty |

Total claimed-novel locus count is expected in the **low hundreds**
across all classes; the manuscript will report per-class breakdown
rather than a single headline number.
`[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §7.2 (reporting framework), §7.3 (yield estimates)]`

Drug-repositioning candidates (cross-trait colocalized loci) are
reported as a secondary product of the pleiotropy aim, not as a
primary drug-discovery claim.
`[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §7.3 closing paragraph]`

---

## 8. Disease Focus — Nine Traits × Two Ancestries (AFR Emphasis)

### 8.1 Trait inventory

The nine Track B traits with EUR + AFR availability and source-cohort
detail. Per-row source: [`.planning/amendments/SUMSTATS-UPGRADE.tsv`](../../amendments/SUMSTATS-UPGRADE.tsv).

| # | Trait | EUR source / N | AFR source / N | Phenotype definition | Build |
|---|---|---|---|---|---|
| 1 | **BMI** | Yengo 2018 GIANT+UKBB / 681,275 (alt: Loh 2022 *Nat Commun* / ~1.1M) | Loh 2022 *Nat Commun* AFR subset / ~100,000 (alt: PAGE Wojcik 2019 / 49,335) | Continuous BMI inverse-rank-normal | GRCh37 |
| 2 | **Type 2 diabetes** | DIAMANTE 2022 EUR / 933,970 (80,154 cases) | DIAMANTE 2022 AFR / 50,251 (29,014 cases) — DUA-pending | Doctor-diagnosed T2D case-control | GRCh37 |
| 3 | **Stroke** | GIGASTROKE 2022 EUR / 1,296,908 (73,652 cases) | GIGASTROKE 2022 AFR / 23,991 (3,961 cases) | All-stroke case-control (ischemic + hemorrhagic pooled — phenotype lock) | GRCh37 |
| 4 | **Systolic blood pressure** | Evangelou 2018 ICBP+UKBB / 757,601 | Giri 2020 MVP-AFR / 318,891 — DUA-pending dbGaP phs001672 (D-06 fallback to AoU AFR-SBP derivation) | Continuous SBP (mmHg), medication-adjusted | GRCh37 |
| 5 | **Asthma** | GBMI 2022 EUR / 995,917 (58,559 cases) | GBMI 2022 AFR / 29,682 (1,978 cases) | Pooled adult + child asthma case-control (PheCode harmonized) | GRCh38 → GRCh37 lift |
| 6 | **Coronary artery disease** | Aragam 2022 CARDIoGRAM+UKB+MVP EUR / 1,001,226 (156,336 cases) | Klarin 2018 MVP-AFR (D-03 fallback) / ~8,500 cases | CAD case-control (broad MI + revascularization + documented angina) | GRCh37 |
| 7 | **Lipids — LDL primary; HDL/TG/TC secondary** | GLGC 2021 EUR / 931,721 | GLGC 2021 AFR / 91,016 | LDL inverse-normal primary; HDL, log(TG), TC secondary | GRCh37 |
| 8 | **eGFR** | CKDGen Wuttke 2019 EUR / 567,460 | CKDGen Morris 2019 AFR companion / 15,863 | log(eGFR-creatinine) continuous | GRCh37 |
| 9 | **HbA1c** | MAGIC Chen 2021 EUR / 123,665 | MAGIC Chen 2021 AFR / 7,564 | HbA1c continuous (mmol/mol), adjusted for age/sex/study | GRCh37 |

`[src: .planning/amendments/SUMSTATS-UPGRADE.tsv rows 2–48; .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §4 (Trait Inventory)]`

### 8.2 AFR emphasis rationale

The AFR LD calibration gap is the central methodological problem
motivating this workspace. Two independent reasons make 1000G AFR
(n = 661) chronically miscalibrated for fine-mapping the AFR strata
above:

1. **Sample-size ceiling on LD estimation.** Standard errors on
   off-diagonal LD matrix entries scale as 1/√n ≈ 0.04 at n = 661,
   large enough that SuSiE-RSS — which treats the LD matrix as fixed
   and known — frequently fails to converge or emits inflated
   credible-set sizes for AFR signals.
   `[src: .planning/amendments/AOU-LD-PIPELINE.md §1 (paragraph 1)]`
2. **Population-composition mismatch.** 1000G AFR is a panel of
   continental African reference samples (YRI, LWK, ESN, GWD, MSL, ACB,
   ASW) whose allele-frequency spectrum and haplotype structure diverge
   materially from the admixed African-American populations dominating
   contemporary GWAS cohorts (MVP, All of Us itself, PAGE, UK Biobank
   AFR-like).
   `[src: .planning/amendments/AOU-LD-PIPELINE.md §1 (paragraph 1, second half)]`

All of Us controlled-tier WGS at target n ≈ 60,000–95,000 AFR
participants post-QC is **the first resource at this scale that is
demographically matched to the modern African-American GWAS cohorts
the project fine-maps against**. To the project's knowledge, no
published genome-wide pleiotropy fine-mapping study has used AoU WGS
for AFR LD, making this a methodological-novelty axis for the Track B
Nature Genetics manuscript.
`[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §5 (final two sentences)]`

---

## 9. Why I Am Interested in This Research

I am the sole author of the coloc_analysis program at the ASHES Lab
(Anthropology, Social Health, and Evolutionary Studies) at North
Carolina State University. The program is hypothesis-driven original
research designed to address a specific, well-documented statistical
problem: the chronically miscalibrated LD reference panels available
for African-ancestry GWAS fine-mapping. Accurate LD is a precondition
for every major fine-mapping method (SuSiE-RSS, FINEMAP, PAINTOR), and
without an ancestry-matched reference, African-ancestry GWAS signals
cannot be resolved to putative causal variants with the same confidence
afforded European-ancestry signals. Stage-2 real-LD evidence from the
project's own pre-pivot work (51/96 non-empty credible sets under real
1000G EUR LD vs 48/95 under matched-coverage k2d identity-LD; AFR
regions had to remain on identity-placeholder fallback because no
fit-for-purpose AFR panel was available) made this gap concrete and
prompted the 2026-04-22 program pivot to a two-track design that
explicitly closes the AFR-LD gap as a primary methodological
contribution.
`[src: .planning/PROJECT.md "Who", "Why" paragraph; .planning/amendments/AOU-LD-PIPELINE.md §1 (paragraph 1)]`

The All of Us Research Program is the only resource that combines (a)
controlled-tier whole-genome sequencing, (b) sample-size at scale
(target n ≈ 60–95k AFR post-QC — approximately 100× the n = 661 of
1000 Genomes Phase 3 AFR), and (c) ancestral composition that matches
the admixed African-American populations dominating modern GWAS cohorts
(MVP, PAGE, AoU itself). Building the AFR LD reference panel inside the
AoU workbench and releasing summary-level LD matrices to the community
via Zenodo addresses the AFR-fine-mapping gap directly and creates a
reusable substrate that other researchers can adopt.
`[src: .planning/amendments/AOU-LD-PIPELINE.md §1 (paragraph 2); .planning/amendments/AOU-LD-PIPELINE.md §13.4 (Zenodo deposit at publication)]`

The broader scientific aim is genome-wide cross-trait joint-signal
discovery and novel-variant identification across nine complex traits
(BMI, T2D, stroke, SBP, asthma, CAD, lipids, eGFR, HbA1c) in EUR and
AFR ancestries, with two co-equal pre-registered scientific aims —
cross-trait pleiotropy and novel-variant discovery — both of which
benefit from ancestry-matched real LD on the AFR strata. As a
solo-author program, the project depends on multi-method triangulation,
strict OSF pre-registration, and Snakemake-pinned pipelines for rigor;
the AoU workspace is the load-bearing infrastructure for the AFR half
of that triangulation.
`[src: .planning/PROJECT.md "What" §Track B, "Constraints" §Solo author; .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §1, §7]`

---

## 10. Use of Race, Ancestry, and Demographics

This project uses **genetic-ancestry classifications derived from
principal-components analysis** (the AoU `ancestry_pred` field) to
define the African-ancestry cohort whose genotypes contribute to the
AFR LD reference panel. Self-reported race and ethnicity are **not
used as a gate for inclusion** in the LD cohort, but are used as a
**sensitivity-check substrate** to verify that PCA-based inclusion
does not materially change LD estimates relative to a
self-identification-restricted cohort.

### 10.1 How demographics WILL be used

- **PCA-based ancestry assignment for cohort definition.** Primary
  inclusion: `ancestry_pred == 'afr'` AND `NOT related at KING ≥ 0.0442`
  AND `sample_qc.call_rate ≥ 0.98`.
  `[src: .planning/amendments/AOU-LD-PIPELINE.md §3.1, §3.2]`
- **Stratified GWAS analysis.** Track B fine-maps each of the nine
  traits separately by ancestry stratum (EUR + AFR) using
  ancestry-matched LD (1000G EUR for EUR signals; AoU AFR for AFR
  signals via the M3 panel built in this workspace).
  `[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §6 #1, §5]`
- **Relatedness pruning** via the AoU-precomputed KING relatedness
  table (kinship coefficient ≥ 0.0442 = up-to-third-degree relatives),
  preserving the sample with higher call rate per related pair.
  `[src: .planning/amendments/AOU-LD-PIPELINE.md §3.1]`
- **Per-ancestry variant QC** (MAF, HWE) computed within the AFR
  cohort rather than across all of AoU, to avoid admixture-driven
  false QC flags.
  `[src: .planning/amendments/AOU-LD-PIPELINE.md §4]`

### 10.2 How demographics WILL NOT be used

- **No individual-level prediction or risk assignment.** No
  participant is identifiable; no clinical prediction is performed on
  the All of Us cohort.
- **No group-level biological-essentialism claims.** Ancestry strata
  are treated as operationally-defined cohorts for statistical
  purposes — LD estimation, GWAS power stratification — not as
  carriers of intrinsic biological group differences.
- **No assignment of risk categories to ethnic groups.** Reported
  ancestry-specific findings are framed as consequences of sample-size
  ceilings and LD-reference mismatches, with explicit acknowledgement
  that even with the AoU AFR LD upgrade, AFR sumstats sample sizes
  remain 5–10× smaller than EUR, capping AFR power.
  `[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §7.3 (Class 2 yield framing)]`
- **Self-reported race/ethnicity is not used as a hard inclusion
  gate.** Doing so would exclude AFR-predominant participants who
  self-identify differently and would systematically under-sample
  admixed populations, which are precisely the populations the project
  targets. Restricted-to-self-ID is run as a **sensitivity check**
  only; if PCA-based vs. self-ID LD correlation is r > 0.995 at lead
  loci, the project proceeds with the PCA-based cohort and reports the
  comparison.
  `[src: .planning/amendments/AOU-LD-PIPELINE.md §3.2]`

### 10.3 Equity statement

This work directly addresses the underrepresentation of
African-ancestry populations in post-GWAS fine-mapping by contributing
ancestry-matched methodology at scale. African-ancestry participants
in the All of Us Research Program will benefit from improved
fine-mapping resolution at loci relevant to traits disproportionately
affecting their communities (e.g., CAD, T2D, CKD). All outputs that
leave the workbench are summary statistics; no participant is
identifiable.
`[src: .planning/amendments/AOU-LD-PIPELINE.md §2.1 RPS template "Community considerations"]`

---

## 11. Expected Publications

| # | Manuscript | Target venue | Scope | Estimated submission |
|---|---|---|---|---|
| 1 | **Track B primary** | **Nature Genetics** | Genome-wide cross-trait pleiotropy discovery + novel-variant discovery across 9 complex traits in EUR + AFR using MTAG + CPASSOC + ABF/SuSiE-RSS coloc + HyPrColoc + PolyFun + L2G/Borzoi, with AoU-derived ancestry-matched AFR LD as a methodological-novelty axis | M6, est. 2027-04 / 2027-05 |
| 2 | **M3 deliverable** | **Scientific Data** (data descriptor) + **Zenodo** deposit | The AoU-derived AFR LD reference panel itself: per-region LD matrices for ~1,500–3,000 fine-mapping windows, validation memo (4 checks), QC log. Released as a community resource (summary-only, post AoU manuscript-disclosure review) for downstream coloc / fine-mapping pipelines | Aligned with M6 (paper #1) submission timeline; Zenodo deposit at publication |

`[src: target venue Nature Genetics — .planning/PROJECT.md "What" §Track B; M3 Zenodo deposit + AoU-disclosure data-availability statement — .planning/amendments/AOU-LD-PIPELINE.md §13.4; .planning/PROJECT.md "Goals" #4]`

> **Note on the Scientific Data data-descriptor commitment.** The
> project's planning artifacts commit to releasing the AoU-derived AFR
> LD matrices via Zenodo at publication and acknowledge the standard
> AoU disclosure. A standalone *Scientific Data* data-descriptor
> manuscript covering the M3 deliverable as a community resource is a
> reasonable companion publication and is committed here in the AoU
> workspace registration; this commitment can be recorded as a project
> decision in `.planning/DECISIONS.md` if desired.

### 11.1 OSF cross-link

- **Root pre-registration:** [osf.io/pvb5j](https://osf.io/pvb5j) (DOI [10.17605/OSF.IO/PVB5J](https://doi.org/10.17605/OSF.IO/PVB5J)), posted 2026-04-10. Original candidate-locus design across 5 traits.
- **Amendment record:** [osf.io/az52u](https://osf.io/az52u). Holds the distal-gene expansion amendment (PDF, 2026-04-13) and the Track B / AoU AFR LD egress amendment (paragraph (f), 2026-04-25). The Track B amendment expands the original pre-registration to 9 traits across EUR + AFR with MTAG + CPASSOC + HyPrColoc + PolyFun + AoU AFR LD; declares Track A as the pre-specified methods-validation subset; does not retract any prior analyses.

`[src: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §9.2 (coordination with existing OSF record); .planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md (paste-ready amendment body)]`

---

## 12. Publications & Presentations Disclosure Note

A draft P&P registration will be filed in the All of Us Researcher
Workbench **before** submission of the Track B Nature Genetics
manuscript. The draft is registered at draft stage and updated at major
changes; the final disclosure will name both this workspace and the
Track B manuscript title.

`[src: .planning/amendments/AOU-LD-PIPELINE.md §2 prerequisite P6, §12 risk R6]`

---

## Appendix A — Source-citation index

Primary planning artifacts cited by inline `[src: ...]` footnotes
throughout this document. All paths are repository-relative from
`/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/`.

- [`.planning/PROJECT.md`](../../../PROJECT.md) — Who, What, Where, Why, Constraints, Goals, Current status.
- [`.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`](../../amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md) — Authoritative pivot charter; §4 Trait Inventory, §5 AFR LD Panel Strategy, §6 Method Stack, §7 Novel-Variant Discovery + yield estimates, §8 Track A Integration, §9 OSF Amendment Plan, §11 Timeline.
- [`.planning/amendments/AOU-LD-PIPELINE.md`](../../amendments/AOU-LD-PIPELINE.md) — §1 Purpose, §2 Prerequisites + RPS template, §3 Cohort Definition, §4 Variant QC, §5 Hail BlockMatrix Pipeline, §7 Export Protocol, §9 Validation Protocol, §11 Compute Cost, §12 Risks, §13 AoU Publication Policy Integration.
- [`.planning/amendments/SUMSTATS-UPGRADE.tsv`](../../amendments/SUMSTATS-UPGRADE.tsv) — Authoritative trait × ancestry × source-cohort × N inventory.
- [`.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md`](../../amendments/OSF-AMENDMENT-TEXT-2026-04-22.md) — Paste-ready OSF amendment body; paragraph (f) is the egress-language source-of-truth.
- [`.planning/amendments/TRACK-A-PIVOT.md`](../../amendments/TRACK-A-PIVOT.md) — Track A working title and venue ladder, for the Track A omission paragraph in §3.
- [`.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`](../../amendments/TRACK-A-FROZEN-NUMBERS.md) — Frozen Stage-2 real-LD numerics (1000G Phase 3 EUR n = 503).

**Verification command suggested before paste:**

```bash
grep -E '\[src:[^]]+\]' AOU-WORKBENCH-REGISTRATION.md \
  | sort -u | wc -l    # expect ≥ 20 distinct source citations
```

**End of paste-ready document.**
