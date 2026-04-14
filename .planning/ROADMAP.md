# Roadmap: coloc_analysis

## Overview

Cross-ancestry colocalization revision from descriptive catalog to mechanistically resolved framework. Tiered execution: T1 spine (Phases 0, 1, 2, 5, 9) ships an honest AJHG submission. T2 (Phases 3, 4, 8) adds MR + matched-N + PRS for Nature Genetics ambition — gated on Checkpoint #1. T3 (Phases 6, 7, 10) adds selection scans + deep learning — gated on Checkpoint #2. Phase 11 (manuscript) runs in parallel from Phase 9 onward.

## Phases

**Phase Numbering:** Preserves Revision_Plan.md numbering. Phases are non-sequential because T2/T3 phases interleave.

**Tier Legend:** **T1** = must-ship spine. **T2** = gated on CP#1. **T3** = gated on CP#2. **M** = manuscript (parallel).

- [ ] **Phase 0: Data access + infrastructure** - DUAs, data ingest, Snakemake skeleton, CI smoke test [T1]
- [ ] **Phase 1: coloc.susie fine-mapping spine** - SuSiE-RSS + coloc.susie replaces coloc.abf [T1]
- [ ] **Phase 2: 3-way QTL colocalization** - eQTL/pQTL/sQTL coloc, gene-tissue matrix, threshold sweep [T1]
- [ ] **Phase 5: Pathway + partitioned heritability** - MAGMA, g:Profiler, LDSC-SEG, HESS [T1]
- [ ] **Phase 9: Replication in independent cohorts** - FinnGen, GBMI, MVP, AoU, BBJ [T1]
- [ ] **Phase 3: Mendelian randomization** - Bidirectional MR, weak-instrument mitigation [T2, gated on CP#1]
- [ ] **Phase 4: Matched-N cross-ancestry concordance** - Power-corrected Table 2 replacement [T2, gated on CP#1]
- [ ] **Phase 8: Cross-ancestry PRS** - PRS-CSx, calibration, clinical utility, equity trade-off [T2, gated on CP#1]
- [ ] **Phase 6: Selection scans + polygenic selection** - iHS/SDS/PBS, thrifty-gene tests [T3, gated on CP#2]
- [ ] **Phase 7: Single-cell + EpiMap + ABC** - Cell-type-resolved integration [T3, gated on CP#2]
- [ ] **Phase 10: Deep-learning variant effect + MPRA overlap** - Enformer/Borzoi/Sei/AlphaMissense [T3, gated on CP#2]
- [ ] **Phase 11: Manuscript + figures + submission** - Full manuscript assembly and submission [M, parallel from Phase 9]

## Phase Details

### Phase 0: Data access + infrastructure
**Goal**: Establish all data sources, fix legacy issues, build reproducible Snakemake skeleton with CI smoke test. Two parallel sub-tracks: Track 0a (DUA applications, non-blocking) and Track 0b (infrastructure, blocks Phase 1).
**Depends on**: Nothing (first phase)
**Requirements**: REQ-1, REQ-9, REQ-12
**Tier**: T1
**Success Criteria** (what must be TRUE):
  1. All 7 open-access data sources downloaded or confirmed reachable
  2. All of Us institutional DURA status documented in .planning/data_access.md
  3. Corrupted supplementary tables (Table 1, 3, S4) fixed and DIAMANTE T2D dedup resolved
  4. Legacy hardcoded paths parameterized via config/pipeline.yaml (grep returns 0 matches)
  5. Conda envs pinned under envs/*.yml with exact versions
  6. Snakemake skeleton built with per-trait/ancestry schema validation
  7. Toy 3-locus CI smoke test completes in under 15 minutes
  8. OSF pre-registration submitted
**Plans**: 4 plans

Plans:
- [x] 00-01-PLAN.md — Config foundation: pipeline.yaml, datasets.yaml, cluster_lsf.yaml, schemas, conda envs, R config loader, data manifest
- [x] 00-02-PLAN.md — Data access checklist: verify connectivity, portal registrations, OSF pre-registration
- [x] 00-03-PLAN.md — Snakemake skeleton: refactor 8 legacy rules, top-level Snakefile, path parameterization, data fixes
- [x] 00-04-PLAN.md — Toy 3-locus CI smoke test: test scaffolding, config override, subsetting script

Track 0a detail (non-blocking DUAs):
- UKB-PPP (Synapse), deCODE pQTL, FinnGen, GTEx v8, Pan-UKBB, BBJ, MVP — all same-day registration/download
- All of Us Researcher Workbench — institutional DURA check first
- UK Biobank main DUA deferred (not-needed-unless status)

Track 0b detail (infrastructure, blocks Phase 1):
- Fix corrupted supplementary tables per Revision_Plan.md section 10
- Audit DIAMANTE T2D dedup (76/63%/26 denominator mismatch)
- Drop KCNJ11 asthma-HTN Tier-1 signal (n_SNPs=6 < 50 threshold)
- Ingest new ancestry GWAS: AFR BMI (Gurdasani 2019), AFR HTN (Hoffmann), AFR T2D, EAS (BBJ), Hispanic (PAGE/HCHS)
- Parameterize 174 hardcoded path references (REQ-12)
- Pin conda envs (REQ-9)
- Build Snakemake skeleton with schema validation
- Build toy 3-locus CI subset (REQ-9)
- OSF pre-registration

### Phase 1: coloc.susie fine-mapping spine
**Goal**: Replace coloc.abf with coloc.susie across the entire pipeline. SuSiE-RSS fine-mapping per trait x ancestry with explicit complex-region policy and sensitivity sweeps.
**Depends on**: Phase 0 (Track 0b)
**Requirements**: REQ-2
**Tier**: T1
**Success Criteria** (what must be TRUE):
  1. SuSiE-RSS fine-mapping completes for all trait x ancestry combinations
  2. config/susie_policy.yaml exists with explicit rules for convergence failures, L cap, min_abs_corr
  3. min_abs_corr sensitivity sweep (3+ values) reported for complex regions as supplementary table
  4. coloc.susie replaces coloc.abf in the pipeline (no coloc.abf calls remain)
  5. Per-locus fine-mapping QC report generated
**Plans**: 6 plans

Plans:
- [x] 01-01-PLAN.md — Wave 1: policy YAML + schema + run_susie_rss.R in-place mod (fit persistence + retry ladder + policy loader + D1/D2/D3 diagnostics + sweep) + 4 G3_complex rows + cache-clear + A6 dispatch test with runsusie fallback + finemap.smk multi-output
- [x] 01-02-PLAN.md — Wave 2: UKBB-LD tiled EUR panel (Weissbrod 2020) via boto3 + per-region NPZ→.rds + HLA block-diagonal flag
- [x] 01-03-PLAN.md — Wave 3: HGDP+1kG AFR LD panel (gnomAD v3.1.2) via anonymous HTTPS + bcftools + plink2 (pilot-scope fallback). Serialized after 01-02 — shares ld_reference.smk + pipeline.yaml + test_ld_panels.py
- [x] 01-04-PLAN.md — Wave 4: coloc.smk + run_coloc_susie.R + rename run_coloc.R → run_coloc_abf_legacy.R + rewire multitrait.smk
- [x] 01-05-PLAN.md — Wave 5: Quarto QC dashboard D1+D2+D3+D4+D6 with HLA red-flag styling + standalone REQ-2 supplementary sweep table
- [ ] 01-06-PLAN.md — Wave 6: filter_finemap_summary.py update + first REAL CI smoke + methods_fragment.md + OSF amendment (DOI 10.17605/OSF.IO/PVB5J)

Seeds: src/legacy/region_analysis/scripts/run_susie_rss.R, src/legacy/genome_wide/scripts/run_coloc_genomewide.R

### Phase 2: 3-way QTL colocalization
**Goal**: Build the causal gene x tissue x cell-type matrix through eQTL, pQTL, sQTL, and sc-eQTL colocalization with rigorous threshold sweep and negative controls. Highest-leverage T1 phase.
**Depends on**: Phase 1, Track 0a DUAs (for pQTL)
**Requirements**: REQ-3, REQ-7
**Tier**: T1
**Success Criteria** (what must be TRUE):
  1. GTEx v8 eQTL coloc completed per tissue, cross-referenced to Open Targets Locus2Gene
  2. sQTL coloc (GTEx) completed
  3. PP.H4 threshold sweep across {0.5, 0.7, 0.8, 0.9} reported with tier counts per ancestry
  4. Negative controls (HLA, cosmetic, blood group gene sets) all null — PP.H4 < threshold
  5. Causal gene x tissue x cell-type matrix assembled
  6. Tier A/B/C confidence assignment with reported threshold dependence
**Plans**: 5 plans

Plans:
- [x] 02-01-PLAN.md — Infrastructure: liftover + config (pph4_thresholds.yaml, negative_controls.yaml, qtl_sources.yaml) + conda env + LPA/KIV-2 policy update + QTL test fixtures
- [x] 02-02-PLAN.md — GTEx v8 eQTL coloc backbone: download rules + harmonize_eqtl.py + tissue-N lookup + run_qtl_coloc.R + qtl_coloc.smk manifest dispatch
- [x] 02-03-PLAN.md — GTEx v8 sQTL + UKB-PPP pQTL: harmonize_sqtl.py + harmonize_pqtl.py + sdY estimation + download_ukbppp.py + extended download rules
- [x] 02-04-PLAN.md — OneK1K sc-eQTL (14 immune cell types): download + harmonize + manifest extension (broad trigger on all loci)
- [x] 02-05-PLAN.md — Negative controls (3 curated + matched nulls) + PP.H4 threshold sweep + tier A/B/C assignment + L2G concordance + gene-tissue matrix + methods fragment

Architecture: harmonize-then-unify. Per-source harmonization produces common intermediate TSV (variant_id, beta, se, maf, position, N, sdY, gene_id, tissue). One unified run_qtl_coloc.R consumes all sources.

### Phase 5: Pathway + partitioned heritability
**Goal**: Formal pathway enrichment with proper nulls and partitioned heritability analysis. Replaces the ad-hoc enrichment from the original manuscript.
**Depends on**: Phase 1
**Requirements**: REQ-7
**Tier**: T1
**Success Criteria** (what must be TRUE):
  1. MAGMA gene-based + gene-set enrichment completed
  2. g:Profiler run with discoverability-matched null (per-trait background)
  3. LDSC partitioned heritability reported per pathway per trait
  4. LDSC-SEG tissue-specific heritability completed
  5. Negative-control pathway set is null (enrichment q > 0.05)
  6. Permutation null for colocalization gene list computed
**Plans**: 5 plans

Plans:
- [x] 05-01-PLAN.md — Wave 1: Infrastructure — 4 conda envs, custom pathway GMT sets, negative control GMT, sumstats_utils.py, build_magma_geneset.py, build_ldsc_annot.py, munge_sumstats_ldsc.py, pathway.smk skeleton, test scaffolding
- [x] 05-02-PLAN.md — Wave 2: MAGMA 3-step enrichment (annotate, gene-analysis, gene-set) + g:Profiler with discoverability-matched 5-trait union background
- [x] 05-03-PLAN.md — Wave 3: LDSC partitioned heritability (baseline v2.2 + custom annotations) + LDSC-SEG tissue-specific enrichment (GTEx 53-tissue + Roadmap chromatin) + LDSC-SEG negative controls
- [x] 05-04-PLAN.md — Wave 4: HESS/rho-HESS local genetic covariance per trait pair x ancestry + HESS negative controls
- [x] 05-05-PLAN.md — Wave 5: Negative control validation (all 5 methods) + 1000 permutation null gene sets (matched for length, LD, MAF) + cross-method aggregation + methods fragment

### Phase 9: Replication in independent cohorts
**Goal**: Validate T1 findings in independent cohorts to establish reproducibility for the submission.
**Depends on**: Phases 1, 2; Track 0a DUAs (for FinnGen, MVP, AoU, BBJ)
**Requirements**: (none directly; supports overall validity)
**Tier**: T1
**Success Criteria** (what must be TRUE):
  1. At least 2 independent cohort replications completed (from FinnGen, GBMI, MVP, AoU, BBJ)
  2. Replication-adjusted effect sizes calculated
  3. Hold-out replication tables generated for supplementary material
**Plans**: 5 plans

Plans:
- [x] 09-01-PLAN.md — Wave 1: Infrastructure — envs (GCTA, r_coloc extended), config/replication_cohorts.yaml (4 cohorts × 5 traits), MVP phs001672 FTP enumeration, replication.smk skeleton (20+ rules), tests/phase9/ scaffolding (9 files)
- [x] 09-02-PLAN.md — Wave 2: Ingest + harmonize 4 cohorts — FinnGen R12 + GBMI + MVP + BBJ harmonizers with canonical 10-column schema + GRCh38→37 liftover + palindromic SNP exclusion
- [x] 09-03-PLAN.md — Wave 3: Replication manifest (signal × cohort crossmap per D-02/D-05) + run_replication_susie.R (reuses Phase 1 susie_policy.yaml) + run_fiqt.R (winnerscurse::FDR_IQT)
- [x] 09-04-PLAN.md — Wave 4: coloc.susie re-estimation with PP.H4 sweep {0.5,0.7,0.8,0.9} + per-cohort Bonferroni effect-size test + same-direction + post-hoc power + IVW meta (metafor)
- [ ] 09-05-PLAN.md — Wave 5: COJO sensitivity (1000G EUR/AFR with N<4000 caveat) + master_table.tsv + cross_ancestry_generalization_tier_ab.tsv (BBJ Tier A+B only, D-05c) + replication_holdout_supplementary.tsv + methods fragment

### Checkpoint #1: End of T1 spine
**Type**: Decision gate (not a phase)
**Depends on**: Phases 0, 1, 2, 5, 9 all complete
**Requirements**: REQ-11
**Produces**: .planning/checkpoints/T1_review.md with:
- Tier A signals that survived PP.H4 sweep + replication
- Ancestry-level power retention under matched-N preview
- Go/no-go decision for T2 with explicit evidence
- Submission target: AJHG (T1 alone) vs. Nat Genet pivot (proceed to T2)

**No T2 phase is planned until this file exists with a "go" verdict.**

### Phase 3: Mendelian randomization
**Goal**: Establish causal direction between trait pairs via bidirectional MR with robust weak-instrument mitigation for non-EUR ancestries.
**Depends on**: CP#1 (go verdict)
**Requirements**: REQ-4
**Tier**: T2 (gated)
**Success Criteria** (what must be TRUE):
  1. IVW + MR-Egger + weighted median triangulation completed for all trait pairs
  2. MR-PRESSO + MR-CAUSE outlier robustness applied
  3. MR-RAPS implemented for AFR and EAS with explicit ancestry-specific vs. trans-ancestry choice
  4. Weak-instrument diagnostic table (F-stat, I-squared, Q-stat) produced per ancestry per trait pair
  5. Bidirectional causal graph assembled
**Plans**: TBD

Seeds: src/legacy/region_analysis/scripts/create_mr_design.py, src/legacy/region_analysis/workflow/rules/mr.smk

### Phase 4: Matched-N cross-ancestry concordance
**Goal**: Replace broken Table 2 with power-corrected cross-ancestry concordance using matched-N bootstrap.
**Depends on**: CP#1 (go verdict)
**Requirements**: (none directly; fixes Table 2)
**Tier**: T2 (gated)
**Success Criteria** (what must be TRUE):
  1. EUR down-sampled to match AFR N with 100x bootstrap concordance
  2. Expected detection probability under Hou et al. 2023 null computed
  3. LDSC cross-ancestry r_g calculated as global benchmark
  4. New Table 2 generated, replacing old incomparable-trait-pair comparison
**Plans**: TBD

### Phase 8: Cross-ancestry PRS
**Goal**: Build and evaluate cross-ancestry polygenic risk scores with full calibration and clinical utility metrics, quantifying the equity-vs-accuracy trade-off.
**Depends on**: CP#1 (go verdict)
**Requirements**: REQ-6, REQ-8
**Tier**: T2 (gated)
**Success Criteria** (what must be TRUE):
  1. PRS-CSx training in EUR and transfer to AFR/EAS/Hispanic completed
  2. Pathway-restricted vs. genome-wide PRS comparison reported
  3. Discrimination metrics (R-squared, AUC, incremental C-statistic) produced per ancestry
  4. Calibration metrics (Hosmer-Lemeshow, slope, intercept, obs-vs-expected plot) produced
  5. Clinical utility metrics (NRI, DCA, net benefit) produced
  6. Equity-vs-accuracy trade-off quantified with explicit numbers for AFR/EAS/Hispanic vs. EUR
**Plans**: TBD

Seeds: src/legacy/region_analysis/scripts/create_pgs_manifest.py, src/legacy/region_analysis/workflow/rules/pgs.smk

### Checkpoint #2: End of T2
**Type**: Decision gate (not a phase)
**Depends on**: Phases 3, 4, 8 all complete
**Requirements**: REQ-11
**Produces**: .planning/checkpoints/T2_review.md with:
- Are T1+T2 results a Nature Genetics story or a Nature Metabolism story?
- Is T3 worth the schedule risk?
- Updated journal target decision

**No T3 phase is planned until this file exists.**

### Phase 6: Selection scans + polygenic selection
**Goal**: Test evolutionary medicine hypotheses with formal selection scans and polygenic selection tests. Pre-specified fallback framing required before execution.
**Depends on**: CP#2 (go verdict)
**Requirements**: REQ-5
**Tier**: T3 (gated)
**Success Criteria** (what must be TRUE):
  1. iHS, SDS, PBS, XP-EHH scans completed across 1000G + HGDP
  2. Pathway-level enrichment of selection signatures computed
  3. Pre-specified fallback framing exists in PLAN.md before first execution run
  4. Thrifty-gene and antagonistic-pleiotropy hypothesis tests completed
**Plans**: TBD

### Phase 7: Single-cell + EpiMap + ABC
**Goal**: Cell-type-resolved regulatory integration using single-cell eQTL, chromatin state, and enhancer-gene models.
**Depends on**: CP#2 (go verdict)
**Requirements**: (none directly; adds mechanistic depth)
**Tier**: T3 (gated)
**Success Criteria** (what must be TRUE):
  1. Cell-type-resolved eQTL integration completed
  2. Roadmap/EpiMap chromatin state overlap analysis done
  3. ABC enhancer-gene linking model applied to credible-set variants
  4. CELLECT/scDRS enrichment computed
**Plans**: TBD

### Phase 10: Deep-learning variant effect + MPRA overlap
**Goal**: Computational variant effect prediction and validation against experimental MPRA data.
**Depends on**: CP#2 (go verdict)
**Requirements**: (none directly; adds functional evidence)
**Tier**: T3 (gated)
**Success Criteria** (what must be TRUE):
  1. Enformer + Borzoi inference completed per credible-set variant
  2. Sei regulatory activity scores computed
  3. AlphaMissense coding-variant scores retrieved
  4. Overlap with public MPRA datasets (Abell 2022, Tewhey 2016) quantified
  5. Composite functional-evidence score produced per variant
**Plans**: TBD

### Phase 11: Manuscript + figures + submission
**Goal**: Assemble the full manuscript with regenerated figures, methods rewrite, equity framing, cover letters, and submission package.
**Depends on**: Phase 9 (runs in parallel from Phase 9 onward)
**Requirements**: REQ-8, REQ-10
**Tier**: M (parallel)
**Success Criteria** (what must be TRUE):
  1. Figures 1-6 regenerated from new analytical data
  2. New Table 2 (matched-N) + regenerated Tables 1, 3
  3. Methods section rewritten — one subsection per analytical phase
  4. Equity-as-trade-off framing reconciled across abstract/intro/discussion (REQ-8)
  5. Cover letters written per target journal (REQ-10)
  6. GitHub repo public release + Zenodo DOI minted
  7. OSF final registration updated
**Plans**: TBD

## Progress

**Execution Order:**
T1: 0 → 1 → 2 → 5 → 9 → CP#1
T2 (if go): 3, 4, 8 → CP#2
T3 (if go): 6, 7, 10
M: 11 (parallel from Phase 9)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 0. Data access + infrastructure | 0/4 | Planning complete | - |
| 1. coloc.susie fine-mapping | 0/TBD | Not started | - |
| 2. 3-way QTL colocalization | 0/5 | Planning complete | - |
| 5. Pathway + partitioned h2 | 0/TBD | Not started | - |
| 9. Replication | 0/TBD | Not started | - |
| 3. Mendelian randomization | - | Gated (T2) | - |
| 4. Matched-N concordance | - | Gated (T2) | - |
| 8. Cross-ancestry PRS | - | Gated (T2) | - |
| 6. Selection scans | - | Gated (T3) | - |
| 7. Single-cell + EpiMap | - | Gated (T3) | - |
| 10. DL variant effect | - | Gated (T3) | - |
| 11. Manuscript | - | Not started | - |
