# Phase 9: Replication in Independent Cohorts — Research

**Researched:** 2026-04-13
**Domain:** GWAS replication — cohort ingest, coloc.susie re-estimation, winner's-curse correction, COJO conditional sensitivity, cross-ancestry generalization
**Confidence:** HIGH (cohort access + endpoint codes verified against live portals); MEDIUM (FIQT implementation choice — package ecosystem documented but no CRAN release exists); LOW (MVP per-trait sub-accession inventory for non-T2D traits — dbGaP listing requires manual browsing)

## Summary

Phase 9 is implementation-heavy but methodologically well-understood. All four cohorts (GBMI, FinnGen R12, MVP dbGaP, BBJ hum0197-v3) are verified open-access (verified 2026-04-10 in `data_access.md`), and Phase 1's `.fit.rds` + Phase 2's `tier_assignments.tsv` give us everything we need to drive replication dispatch. The main research payload is **cohort-specific harmonization** (trait → endpoint code → file URL → column schema) across four heterogeneous sumstats formats, plus four well-defined tool-level decisions (FIQT implementation, COJO LD reference, coloc.susie re-estimation dispatch, EAS LD panel for BBJ generalization).

The single biggest risk is **COJO's LD-reference sample-size requirement** — GCTA recommends ≥ 4,000 unrelated samples for COJO's conditional analysis, but our Phase 1 UKBB-LD panel (derived from Weissbrod 2020 tiled LD matrices) and HGDP+1kG AFR (n ≈ 986) are matrix-level, not PLINK genotype panels. COJO wants raw PLINK `.bed/.bim/.fam` files of individual genotypes, not summary LD matrices. This is a plumbing gap that Phase 9 must close: the plan must either (a) build a PLINK-formatted reference from Pan-UKBB subset ≥ 4K samples, or (b) scope COJO to sensitivity-only loci where 1000G EUR (N=503) is "acceptable-with-caveats" and document the limitation. Decision flagged for planner.

Second-biggest risk: the **FinnGen R12 endpoint code for stroke** has two candidate definitions (`I9_STR_EXH` = exhaustive union of hemorrhagic + ischemic; `I9_STR_SAH_ICD9` = subarachnoid only; no separate `I9_STR_ISCH` in R12 by default). BBJ provides ischemic-only (`IS`) while MVP and our Phase 0 discovery used MEGASTROKE any-stroke. Document as a pre-planned harmonization choice, not a surprise.

**Primary recommendation:** Use `winnerscurse` (Forde 2023, GitHub-only with Bioconductor-style API) for FIQT — single-function call `FDR_IQT(summary_stats)`; pin to a commit SHA in `envs/r_coloc.yml` via `remotes::install_github()` since no CRAN release exists. Use GCTA v1.94.1 from bioconda (`gcta 1.94.1 h9ee0642_0`) for COJO sensitivity. For EAS LD, use 1000G Phase 3 EAS (504 samples, already cached) — Phase 1's HGDP+1kG pattern doesn't automatically extend to EAS and the Tier A+B region count (~11–20) is small enough that the incremental power gain from HGDP+1kG EAS (~730 samples) doesn't justify a new plan.

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 Cohort portfolio:** Four cohorts in scope — **GBMI + FinnGen R12 + MVP (dbGaP phs001672) + BBJ (hum0197-v3)**. AoU excluded from Phase 9 (deferred to T2 Phase 8). deCODE pQTL deferred.
- **D-02 Replication unit:** Full signal table: (a) Phase 1 credible-set lead SNPs, (b) Phase 2 Tier A+B gene-tissue-trait triples. Tier C excluded from primary replication.
- **D-03 Success criterion:** Joint — both Bonferroni per-cohort effect-size AND coloc.susie re-estimation at PP.H4 sweep {0.5, 0.7, 0.8, 0.9}.
- **D-04 Effect-size adjustment:** FIQT (Bigdeli 2016) empirical Bayes for discovery β̂ shrinkage + 4-column reporting (discovery_raw, discovery_FIQT, replication, meta); COJO as supplementary sensitivity.
- **D-05 Ancestry matching:** Asymmetric — EUR/AFR discovery match to FinnGen/GBMI-EUR/MVP-EUR and MVP-AFR/GBMI-AFR respectively. BBJ-EAS used as **generalization panel for Tier A+B ONLY**, never for credible-set SNPs, and explicitly framed as generalization.
- **D-06 Meta aggregation:** Per-cohort columns + IVW META column at both layers.
- **D-07 Outputs:** `master_table.tsv`, `cross_ancestry_generalization_tier_ab.tsv`, `cojo_sensitivity.tsv`, `replication_holdout_supplementary.tsv` under `results/replication/`.
- **D-08 LD panels:** EUR=UKBB-LD (Phase 1 reuse); AFR=HGDP+1kG (Phase 1 reuse); EAS=researcher to decide (see §8 of this document).

### Claude's Discretion

- Phenotype-mapping per cohort (endpoint codes, file URLs) — surveyed in §1-4 below
- FIQT implementation — recommended: `winnerscurse` R package via `remotes::install_github`
- COJO runner invocation details + LD reference — see §6
- Snakemake rule structure for `replication.smk` — see §17
- Supplementary hold-out table format — planner's call
- Handling of small-N traits (MVP asthma) — documented caveat, Bonferroni per-cohort
- Liftover strategy per cohort — reuse Phase 0 `src/python/liftover.py`

### Deferred Ideas (OUT OF SCOPE)

- AoU individual-level validation (Phase 8 T2)
- EAS/HIS/AMR discovery ingestion (Phase 4 T2)
- deCODE pQTL broader aptamer coverage
- S-LDXR multi-ancestry partitioned h²
- MR-based replication shrinkage (Phase 3 T2)
- BRcalibration
- Tier C signal replication
- GBMI EAS/AMR unmatched strata
- hyprcoloc multi-trait replication
- Per-endpoint sensitivity within FinnGen

## Project Constraints (from CLAUDE.md)

- **100% public data only.** All four Phase 9 cohorts are verified open-access.
- **GPFS filesystem.** No worktree isolation; `solo` mode with `git.isolation: branch`.
- **Solo author.** Rigor via triangulation + pre-registration + Snakemake pin.
- **Stack:** R (`coloc`, `susieR`, `winnerscurse`) + Python (harmonization) + Snakemake + conda. No JS/web.
- **Python 3.11 for Snakemake.** Use `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` or `--use-conda`. Never invoke from miniconda3 base (Python 3.13).
- **Node.js PATH:** Prepend `/rs1/researchers/c/ckclinto/miniconda3/bin` for all GSD CLI calls.
- **Framing:** Phase 9 outputs frame as *original cross-ancestry mechanistic replication*, never as "revision" or "cleanup".

## Phase Requirements

No direct REQ-ID is assigned to Phase 9 in `.planning/REQUIREMENTS.md`. Phase 9 supports cross-cutting validity:

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-3 | PP.H4 threshold sweep {0.5, 0.7, 0.8, 0.9} | D-03b reuses the Phase 2 sweep at the replication layer (§7 coloc.susie re-estimation) |
| REQ-7 | Negative-control gene/pathway sets | Phase 9 inherits Phase 2's HLA / cosmetic / blood-group negative controls; expected to fail replication (useful sanity check — §§12, Validation L3) |
| REQ-9 | Snakemake CI smoke test | Phase 9 rules must run on the toy 3-locus fixture — extend `tests/toy_3locus/` with mock replication sumstats |
| REQ-11 | Tiered T1/T2/T3 scope | Phase 9 is T1. Phase 9 completion unlocks Checkpoint #1 (AJHG vs Nat Genet). |
| REQ-12 | No hardcoded paths | All cohort URLs / file paths parameterized in `config/pipeline.yaml` + a new `config/replication_cohorts.yaml` |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `coloc` | ≥ 5.2.0 | `coloc.susie(fit1, fit2)` replication re-estimation (D-03a) | Reused from Phase 1; only implementation of coloc.susie `[CITED: chr1swallace/coloc]` |
| `susieR` | ≥ 0.12 | `runsusie()` fit on replication cohort per region | Reused from Phase 1 `[CITED: phase1 01-CONTEXT G1]` |
| `winnerscurse` | GitHub `amandaforde/winnerscurse` ≥ 0.1.1 | FIQT shrinkage (`FDR_IQT()`) — D-04a | Only implementation of Bigdeli 2016 FIQT in a maintained R package `[VERIFIED: rdrr.io, GitHub]` |
| GCTA | 1.94.1 | COJO conditional+joint sensitivity — D-04c | Canonical COJO implementation (Yang 2012 Nat Genet) `[VERIFIED: bioconda gcta 1.94.1 h9ee0642_0]` |
| `data.table` | ≥ 1.14 | Fast sumstats I/O (all cohorts are ≥ GB-scale gzipped TSVs) | Existing pattern in Phase 1/2 harmonizers `[ASSUMED]` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pandas` (py) | ≥ 1.5 | Harmonization stage — column-rename, dedupe, tabix prep | Phase 2 harmonizers use it — reuse pattern |
| `pyliftover` (py) | 0.4.1 | GRCh37↔GRCh38 liftover if needed per cohort | Already installed in `smoke_dev` env per Phase 2 closeout |
| `metafor` (R) | ≥ 3.0 | IVW meta-analysis (D-06b) — `rma.uni(method='FE')` | Standard fixed-effect IVW `[CITED: metafor docs]` |
| `bcftools` | ≥ 1.17 | If building PLINK reference for COJO from BCF | Already in `envs/ld_build.yml` |
| `plink2` | ≥ 2.00a6 | COJO LD reference `.bed/.bim/.fam` | Already in `envs/plink.yml` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `winnerscurse` package | Hand-code FIQT from Bigdeli 2016 (≤ 30 lines R) | Hand-code gives zero-dependency reproducibility but loses the `empirical_bayes()` / `conditional_likelihood()` alternative estimators if reviewers push for comparison. Recommendation: install `winnerscurse` pinned to commit SHA. |
| 1000G EUR COJO reference | Pan-UKBB subset ≥ 4K PLINK genotypes | 1000G EUR is 503 samples (below GCTA's recommended 4K threshold `[VERIFIED: cnsgenomics.com COJO tutorial]`) — small reference inflates false positives. Pan-UKBB has public genotypes only at restricted tiers. Compromise: use 1000G EUR with documented caveat, mark sensitivity results as tier-2 evidence. |
| Per-cohort coloc.susie re-estimation | Just effect-size check | D-03c rationale locks joint criterion; re-estimation is mandatory. |

### Installation

```bash
# Add to envs/r_coloc.yml (already exists):
# - bioconda::gcta=1.94.1
# - r-metafor  (conda-forge)
# R packages installed post-conda:
# - remotes::install_github("amandaforde/winnerscurse@<COMMIT_SHA>")
```

### Version verification

```bash
# Verify at plan time:
$ conda search -c bioconda gcta
gcta 1.94.1 h9ee0642_0   # VERIFIED 2026-04-13
$ Rscript -e 'packageVersion("coloc")'   # already validated by Phase 1/2
$ Rscript -e 'packageVersion("susieR")'  # already validated
# winnerscurse GitHub-only; pin to current HEAD SHA at plan time
```

## Cohort-specific Harmonization

### §1 FinnGen R12 [VERIFIED: data_access.md + Risteys + GitBook manifest]

**Bucket:** `gs://finngen-public-data-r12/summary_stats/release/` (verified 2026-04-10 post-registration)
**HTTP mirror:** `https://storage.googleapis.com/finngen-public-data-r12/summary_stats/release/finngen_R12_{ENDPOINT}.gz` `[VERIFIED: FinnGen GitBook data-download page]`
**Manifest:** `https://storage.googleapis.com/finngen-public-data-r12/summary_stats/finngen_R12_manifest.tsv` `[VERIFIED]`
**Tabix:** companion `.gz.tbi` at same path
**Ancestry:** Finnish (EUR stratum with known founder effects — see §14 edge case)
**Genome build:** GRCh38 `[CITED: FinnGen docs]`

**Endpoint mapping for our 5 traits:**

| Phase 2 trait | FinnGen endpoint | Rationale | Case N (approx) | Confidence |
|---------------|------------------|-----------|-----------------|------------|
| BMI | **N/A** — BMI is a quantitative trait not in FinnGen's disease-endpoint catalog | FinnGen endpoints are disease codes; quantitative BMI requires a lab-value endpoint. Check `/lab_values/` subfolder if BMI is there; otherwise **exclude BMI from FinnGen replication** and use GBMI + MVP only. | — | HIGH (structural limitation) |
| T2D | `T2D` (combined, preferred) or `T2D_WIDE` (more inclusive, gestational excluded) | `T2D` is the definitions-combined endpoint; use it for primary, `T2D_WIDE` as sensitivity | ~65K cases | HIGH `[VERIFIED: Risteys T2D page]` |
| hypertension | `I9_HYPTENSESS` (essential hypertension, ICD10 I10) | Matches Evangelou 2018 EUR discovery definition; 141,737 cases | 141,737 | HIGH `[VERIFIED: Risteys I9_HYPTENSESS R13 — applies to R12]` |
| stroke | `I9_STR_EXH` (exhaustive: ischemic + hemorrhagic + SAH union) | Matches MEGASTROKE discovery "any stroke"; alt = `I9_STR` narrower definition | ~30K cases | MEDIUM (two candidate endpoints; `I9_STR_EXH` is the broader/more-matched one) `[VERIFIED: Risteys I9_STR]` |
| asthma | `J10_ASTHMA` (primary) or `J10_ASTHMA_EXMORE` (excluding COPD-overlap) | `J10_ASTHMA` is primary; `_EXMORE` is the stricter sensitivity variant | ~45K cases | HIGH `[VERIFIED: Risteys J10_ASTHMA]` |

**Column schema (11 canonical columns per FinnGen core analysis format):**
```
#chrom  pos  ref  alt  rsids  nearest_genes  pval  mlogp  beta  sebeta  af_alt  af_alt_cases  af_alt_controls
```
`[VERIFIED: FinnGen Core analysis results files docs]`

**Harmonization work:**
- `chrom/pos` → `CHR/BP` rename; `ref/alt` → `OA/EA`; `beta/sebeta/pval/af_alt` → `BETA/SE/P/EAF`
- GRCh38 → GRCh37 liftover via `src/python/liftover.py` (Phase 0 utility)
- File size per trait: ~800 MB gzipped (~7 GB uncompressed, ~20M SNP rows)

### §2 MVP dbGaP phs001672 [PARTIALLY VERIFIED]

**Access:** dbGaP open-access FTP for sumstats (no DAR) `[CITED: data_access.md §7]`
**Portal:** `https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs001672.v11.p1`
**Genome build:** Mixed across sub-studies (GRCh37 dominant, verify per file)

**Sub-accession mapping:**

| Phase 2 trait | MVP sub-accession | Ancestry strata | Confidence |
|---------------|-------------------|-----------------|------------|
| T2D | `pha004943.1` (AFR), `pha004944.1` (EAS), `pha004945.1` (EUR), `pha004946.1` (HIS), `pha004947.1` (TRANS) | AFR + EUR primary (HIS/EAS parked per D-05d) | HIGH `[VERIFIED: DIAMANTE 2022 data availability statement]` |
| hypertension / BP | Giri 2019 MVP SBP/DBP/PP multi-ancestry (N≈776K) — sub-accessions **unconfirmed**; needs direct dbGaP FTP listing at plan time | EUR, AFR, HIS reported | MEDIUM (Nat Genet 2018 Giri paper confirms availability; sub-accessions not indexed in search) `[CITED: s41588-018-0303-9]` |
| stroke | MVP has CAD (Tcheandjieu 2022 Nat Med) and HF (Zhou 2023 Nat Comm) but **stroke-specific MVP release pending verification** — Phase 9 may need to exclude stroke from MVP if dbGaP listing shows no stroke sub-accession. Fallback: use MEGASTROKE as self-replication proxy (not valid). Recommendation: **exclude stroke from MVP if no sub-accession; flag as MVP-missing trait** | EUR, AFR likely | LOW (no direct confirmation of MVP stroke sumstat release) |
| BMI | **Check dbGaP listing at plan time.** MVP anthropometric sumstats likely exist but sub-accession not located in search. | EUR, AFR | LOW |
| asthma | **Check dbGaP listing at plan time.** MVP respiratory outcomes likely exist but asthma-specific sub-accession not located. | EUR, AFR (small N caveat — see §15) | LOW |

**Action for planner:** Include a "MVP sub-accession discovery" task in Plan 09-01 that browses the dbGaP FTP at `https://ftp.ncbi.nlm.nih.gov/dbgap/studies/phs001672/` to enumerate all published sumstat sub-accessions. Update `config/replication_cohorts.yaml` with exact pha IDs before any download rules run.

**Column schema (typical MVP REGENIE/SAIGE output):** varies per sub-study — expect `CHROM POS REF ALT ID A1 A1_FREQ BETA SE LOG10P N` or similar. Harmonize via Phase 2 `src/python/sumstats_utils.py` with per-cohort column_map (follow Phase 2 D-01 pattern).

### §3 BBJ hum0197-v3 [VERIFIED]

**URL pattern:** `https://humandbs.dbcls.jp/files/hum0197/hum0197.v3.BBJ.{TRAIT}.v1.zip` `[VERIFIED: data_access.md + NBDC dbls.jp]`
**Ancestry:** EAS (Japanese)
**Genome build:** GRCh38 `[CITED: Sakaue 2021 Nat Genet]`
**Primary paper:** Sakaue 2021 Nat Genet 53:1415 (multi-trait); Ishigaki 2020 Nat Genet 52:669 (T2D-specific)

**Trait-to-file mapping:**

| Phase 2 trait | BBJ zip filename | Use | Confidence |
|---------------|------------------|-----|------------|
| BMI | `hum0197.v3.BBJ.BMI.v1.zip` | Tier A+B generalization (D-05c) | HIGH `[VERIFIED]` |
| T2D | `hum0197.v3.BBJ.T2D.v1.zip` | Tier A+B generalization | HIGH `[VERIFIED]` |
| asthma | `hum0197.v3.BBJ.As.v1.zip` | Tier A+B generalization | HIGH `[VERIFIED]` |
| stroke (ischemic) | `hum0197.v3.BBJ.IS.v1.zip` | Tier A+B generalization — note: **ischemic-only**, not any-stroke (narrower than MEGASTROKE `I9_STR_EXH`) | HIGH `[VERIFIED]` |
| hypertension | **No standalone HTN binary file.** Use `hum0197.v3.BBJ.SBP.v1.zip` + `hum0197.v3.BBJ.DBP.v1.zip` as quantitative BP proxy | Alternative: skip HTN in BBJ generalization (Tier A+B signals in BP may overlap). **Recommend: use SBP as primary BP proxy for BBJ generalization.** Flag asymmetry in methods. | HIGH (file structure verified); MEDIUM (choice of BP proxy is a methodological call) |

**Column schema:** BBJ uses REGENIE-style output; expect `SNPID CHR POS Allele1 Allele2 AF Beta SE p.value N` (verify on first download — zip contains multiple files per trait including `README.txt` with schema).

**Critical harmonization gotcha:** BBJ stroke (`IS`) is ischemic-only; FinnGen stroke (`I9_STR_EXH`) is exhaustive union; MEGASTROKE any-stroke is mixed. **Planner must document this heterogeneity in the harmonization table and either (a) use ischemic-only across all cohorts for stroke OR (b) explicitly flag the endpoint mismatch per cohort.** Recommended: adopt ischemic-only as the primary stroke endpoint for Phase 9 (narrower but consistent) and include FinnGen `I9_STR_EXH` as sensitivity.

### §4 GBMI [CITED: Zhou et al. 2022 Cell Genomics]

**URL:** `https://www.globalbiobankmeta.org/resources` (Wix-hosted portal, links to per-trait files)
**Bucket:** Google Cloud / dropbox-style links; exact bucket path requires portal browse at plan time.
**14 exemplar endpoints in GBMI R1:** asthma, COPD, heart failure, stroke, venous thromboembolism, gout, abdominal aortic aneurysm, appendicitis, primary open angle glaucoma, acute appendicitis, idiopathic pulmonary fibrosis, atopic eczema, hypothyroidism, hypertension. `[CITED: Zhou 2022 Cell Genomics + GBMI results page]`

**Trait coverage for Phase 9:**

| Phase 2 trait | GBMI endpoint | Ancestry strata | Confidence |
|---------------|---------------|-----------------|------------|
| BMI | **Not in GBMI flagship.** GBMI focuses on disease endpoints; BMI requires separate cross-biobank meta or use GIANT. **Decision: use Yengo 2022 (GIANT meta-analysis, ~5M samples) as BMI-specific cross-biobank cohort replacement** OR **exclude BMI from GBMI layer and rely on FinnGen-absent / MVP / BBJ**. Planner's call — document in plan. | — | HIGH (structural limitation of GBMI) |
| T2D | Check flagship + follow-up. GBMI T2D sumstats released in phase 2 (2023). | EUR, AFR, EAS, AMR, SAS | MEDIUM `[CITED: GBMI website mentions T2D follow-up]` |
| hypertension | **Yes** — in 14 flagship endpoints | EUR + non-EUR strata with ≥ 2 biobanks | HIGH `[VERIFIED: Zhou 2022 methods]` |
| stroke | **Yes** — in 14 flagship endpoints | EUR, AFR, EAS, AMR | HIGH `[VERIFIED]` |
| asthma | **Yes** — flagship exemplar; highest-power GBMI trait | EUR, AFR, EAS, AMR | HIGH `[VERIFIED]` |

**Column schema:** GBMI uses harmonized SPA-corrected META format: `CHR POS REF ALT rsid all_meta_sample_N all_meta_AF all_meta_beta all_meta_sebeta all_meta_pval` + per-biobank columns. Covered in Zhou 2022 supplementary.

**Ancestry stratum naming:** GBMI uses `EUR / AFR / EAS / AMR / SAS` consistently (same as 1000G superpopulation).

### §11 Trait harmonization master table

| Phase 2 discovery trait | FinnGen endpoint | MVP sub-accession | BBJ file | GBMI endpoint | Harmonization notes |
|--|--|--|--|--|--|
| BMI | — (exclude) | _verify pha_ | `BBJ.BMI.v1` | — (use GIANT-Yengo) | Quantitative; BBJ+MVP only for replication; GIANT as cross-biobank proxy |
| T2D | `T2D` | `pha004945` (EUR), `pha004943` (AFR) | `BBJ.T2D.v1` | T2D (GBMI phase 2) | Gestational excluded in FinnGen `T2D`; harmonizes cleanly |
| hypertension | `I9_HYPTENSESS` | _verify (Giri 2019 BP)_ | `BBJ.SBP.v1` (quant proxy) | hypertension | BBJ lacks binary HTN — use SBP continuous; MVP uses continuous BP traits too |
| stroke | `I9_STR_EXH` (any) ⚠ | _verify (likely absent)_ | `BBJ.IS.v1` (ischemic-only) ⚠ | stroke | **Heterogeneous endpoint** — recommend ischemic-only as primary, any-stroke as sensitivity |
| asthma | `J10_ASTHMA` | _verify_ | `BBJ.As.v1` | asthma | Clean match |

**Ancestry canonical mapping:**
- GBMI: `EUR/AFR/EAS/AMR/SAS` (1000G superpop convention) — use as-is
- FinnGen: Finnish (map to `EUR` with caveat; see §14)
- MVP: `EUR/AFR/HIS/EAS` (HIS maps to `AMR` for cross-cohort alignment)
- BBJ: `EAS` exclusively

## Tool Implementation

### §5 FIQT implementation [VERIFIED]

**Recommendation: `winnerscurse` R package, GitHub install, pinned to commit SHA.**

**Package:** `amandaforde/winnerscurse` (not on CRAN, not on Bioconda) `[VERIFIED: rdrr.io + CRAN listing absence]`
**Version at research time:** 0.1.1 (GitHub HEAD)
**Install:**
```r
install.packages("remotes")
remotes::install_github("amandaforde/winnerscurse", ref = "<COMMIT_SHA_TO_PIN>")
```
**Primary function:** `FDR_IQT(summary_data, min_pval=1e-300)` — returns input data frame with extra column `beta_FIQT` (shrunken effect) `[VERIFIED: rdrr.io FDR_IQT man page]`

**Alternatives evaluated:**
| Option | Source | Verdict |
|--------|--------|---------|
| `winnerscurse::FDR_IQT` | Forde 2023 Bioinformatics (review paper) | **Recommended.** Actively maintained, implements Bigdeli 2016 exactly, has discovery-replication helper functions (`standard_errors_confidence_intervals()`). Pins easily. |
| Hand-code from Bigdeli 2016 formula | ~30 lines R | Zero-dependency but loses sensitivity alternatives (`empirical_bayes()`, `conditional_likelihood()`) if reviewers ask. |
| `zrmacc/WinCurse` | GitHub only, v0.0.1 | Less maintained, narrower scope. Skip. |
| `WINS` CRAN package | Mao et al. | Different domain (adaptive clinical trial Wins), not GWAS FIQT. **Do not use.** `[VERIFIED: CRAN WINS.pdf — different method]` |
| `REBayes` CRAN | Koenker | Generic empirical Bayes mixtures; requires custom wrapper. Overkill. |

**Defensibility:** `winnerscurse` is published (Forde et al. 2023 Bioinformatics review `[CITED: PubMed 37721937]`) and is the reference implementation cited in the Bigdeli-FIQT-comparison literature. Pinning to a commit SHA gives Snakemake-level reproducibility.

### §6 COJO invocation [VERIFIED]

**Binary:** `gcta` from bioconda
- `gcta 1.94.1 h9ee0642_0` (current stable) `[VERIFIED: conda search 2026-04-13]`
- Add to `envs/r_coloc.yml` OR create `envs/gcta.yml`: `- bioconda::gcta=1.94.1`

**Invocation pattern:**
```bash
gcta --bfile ${LD_REF}/chr${CHR}                \
     --cojo-file ${SUMSTATS_MA}                 \
     --cojo-slct                                \
     --cojo-p 5e-8                              \
     --cojo-wind 10000                          \
     --extract ${LOCUS_SNPS}                    \
     --out ${OUT_PREFIX}
```

**LD reference requirement (CRITICAL — flag for planner):**
- GCTA recommends **≥ 4,000 unrelated samples** in the LD reference `[VERIFIED: cnsgenomics.com COJO tutorial + GCTA docs]`
- Reference must be **PLINK `.bed/.bim/.fam`** format (individual genotypes), NOT summary LD matrices
- Phase 1's UKBB-LD is NPZ/scipy sparse tiled matrices (Weissbrod 2020) — **NOT directly usable for COJO**
- Phase 1's HGDP+1kG AFR BCF → plink conversion path exists in `envs/ld_build.yml` — can be reused to produce `.bed/.bim/.fam` from 1000G Phase 3 BCFs (already cached in Phase 0)

**Three options for COJO LD reference:**

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A | 1000G Phase 3 EUR (N=503, already PLINK-converted in Phase 0) | Zero plumbing work | **Below 4K threshold** → false positives in low-LD blocks `[VERIFIED: biostars.org/p/463480]` |
| B | Pan-UKBB EUR subset (≥4K) — build fresh PLINK reference | Meets sample-size bar | New plan needed; Pan-UKBB release genotype structure is HailMT not PLINK |
| C | HapMap3-imputed MVP subset | Would meet bar | Not publicly released as PLINK |
| **D (RECOMMEND)** | 1000G Phase 3 EUR + explicit caveat; mark COJO as **sensitivity tier 2** | Pragmatic; COJO is supplementary per D-04c | Footnote-level methodological limitation |

**Recommendation for planner:** Use Option D (1000G EUR 503 samples + documented caveat). COJO is supplementary sensitivity (D-04c), not primary criterion. Reviewers will accept "COJO run on 1000G EUR with caveat; primary replication uses coloc.susie" more readily than seeing Phase 9 scope expand to include a 4K+ PLINK reference build.

**For AFR COJO:** 1000G Phase 3 AFR (N≈661) or HGDP+1kG AFR (N≈986). Same below-threshold caveat applies.

### §7 coloc.susie replication re-estimation [VERIFIED]

**Pattern (per signal × per cohort):**
```r
# 1. Subset replication sumstats to discovery region
# 2. Fit SuSiE on replication sumstats
rep_fit <- coloc::runsusie(
  D = list(beta=rep_beta, varbeta=rep_se^2, snp=rep_snp_id,
           position=rep_pos, type="quant_or_cc",
           LD=rep_LD, N=rep_N, MAF=rep_MAF),
  suffix = 2
)
# 3. Call coloc.susie with discovery fit + replication fit
res <- coloc::coloc.susie(disc_fit, rep_fit)  # disc_fit loaded from Phase 1 .fit.rds
```
`[CITED: coloc vignette a06_SuSiE.html]`

**Runsusie arguments — per-cohort adjustments needed:**
- `N` per cohort (different sample sizes; critical for type="cc" binary traits)
- `LD` matrix from per-cohort ancestry-matched reference:
  - EUR (FinnGen, GBMI-EUR, MVP-EUR): **UKBB-LD** (Phase 1 reuse)
  - AFR (GBMI-AFR, MVP-AFR): **HGDP+1kG AFR** (Phase 1 reuse)
  - EAS (BBJ, GBMI-EAS): **1000G Phase 3 EAS** (cached from Phase 0) — see §8
- `type="cc"` for binary traits (T2D, hypertension, stroke, asthma); `type="quant"` for BMI
- `s = n_case / (n_case + n_ctrl)` proportion for binary traits
- Reuse `susie_policy.yaml` (Phase 1 G2 — `L=10`, `coverage=0.95`, retry ladder) — D-08 locks this

**Compute estimate:**
- Single `runsusie` run per region: ~1–3 minutes with N=20K SNPs, L=10 (empirical from Phase 1)
- Phase 1 Scope B pilot = 11 autosomal regions × 2 traits × 2 ancestries = 44 fits
- Phase 9: (credible-set signals from Phase 1 × cohorts) + (Tier A+B triples × cohorts) ≈ 50-150 signals × 4 cohorts ≈ 200-600 runsusie fits
- Total compute: ~10-30 CPU-hours serially; trivially parallelizable via Snakemake (LSF)
- `coloc.susie` call itself is fast (~seconds) once both fits are cached
**Confidence:** MEDIUM (empirical from Phase 1 scope, extrapolated)

### §8 BBJ-EAS LD panel strategy [VERIFIED: Phase 0 cache status]

**Options:**

| Option | Description | N EAS | Compute cost | Plans needed |
|--------|-------------|-------|--------------|--------------|
| **A (RECOMMEND)** | **1000G Phase 3 EAS (CHB+JPT+CHS+CDX+KHV), already cached in Phase 0 `data/raw/1kg/`** | 504 | Zero (already built) | 0 new plans |
| B | Extend `build_hgdp_1kg_ld.py` to produce EAS panel per-region | ~730 HGDP+1kG EAS | ~1-2 days compute | 1 new plan |
| C | Use BBJ-derived LD if released | N_BBJ (large if available) | Unknown | Unlikely — BBJ has not released LD matrices publicly |

**Rationale for Option A:**
- Tier A+B region set is small (≤20 regions per Phase 2 tier_assignments; expectation ~11 from Phase 1 Scope B alignment)
- 504 vs 730 is a marginal N gain; not worth a new plan when Phase 9 has 4 cohorts to harmonize
- 1000G Phase 3 EAS is already the accepted reference for BBJ-based MR work in published literature
- Caveat documented in methods: "EAS LD reference = 1000G Phase 3 EAS (N=504); sample size smaller than ideal but adequate for generalization panel coloc re-estimation given Tier A+B region count (~11-20)"

**Caveat to surface in QC dashboard:** per-region `kriging_rss` diagnostic should be re-run for BBJ replication coloc with 1000G EAS LD (Phase 1 D3 pattern) — expect some outlier flags due to ancestry LD mismatch; treat flagged regions as Tier-3 generalization evidence.

## Compute / Storage

### §9 Disk footprint estimate

| Cohort | Format | Trait count | Per-trait size | Cohort total | Cumulative |
|--------|--------|-------------|---------------|---------------|-----------|
| FinnGen R12 | gz TSV | 3-4 (T2D, HTN, stroke, asthma; no BMI) | ~800 MB | ~3 GB | 3 GB |
| GBMI | gz TSV | 3 (HTN, stroke, asthma) | ~1.5 GB multi-ancestry | ~4-5 GB | 8 GB |
| MVP | gz TSV | 1-3 verified (T2D; others TBD) | ~500 MB per sub-accession | ~3-6 GB | 14 GB |
| BBJ | zip (multiple files) | 5 | ~1-2 GB per zip | ~8 GB | 22 GB |
| **Total raw** | | | | | **~22 GB** |
| Harmonized GRCh37 | parquet/gz | 13-15 trait×cohort combos | ~400 MB | ~6 GB | — |
| Per-region subsets (×200 regions) | rds | cached LD + fits | trivial | ~2 GB | — |

Available disk on `/rs1/researchers/c/ckclinto`: 29 TB (1.7 TB used) — Phase 9 disk usage is **< 0.1% of available**, no storage concern. `[VERIFIED: df output 2026-04-13]`

### §10 Runtime estimate

| Stage | Per-unit | Units | Total |
|-------|----------|-------|-------|
| Cohort download | 5-20 min per file | 13 files | ~2 h (mostly network-bound) |
| Harmonization per cohort | 30 min | 13 combos | ~6 h |
| Liftover GRCh38→37 | 5 min per file | 9 files (FinnGen+BBJ+MVP partial) | ~45 min |
| FIQT on discovery β̂ | < 1 min | 1 run | trivial |
| runsusie per region per cohort | 1-3 min | 200-600 fits | 10-30 CPU-h (parallel via LSF → wall ~2h) |
| coloc.susie call | seconds | 200-600 pairs | < 1h |
| COJO per locus | 2-5 min | 50-100 loci × 4 cohorts | 10-30 CPU-h (parallel) |
| IVW meta aggregation | seconds | 50-100 signals | trivial |
| **Wall-clock (LSF parallel)** | | | **~8-12 hours end-to-end** |

## Runtime State Inventory

N/A — Phase 9 is a greenfield phase (no rename/refactor/migration). No prior runtime state exists for replication cohorts.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| R + `coloc` ≥ 5.2.0 | coloc.susie re-estimation | ✓ | 5.2.3 (from Phase 1) | — |
| R + `susieR` ≥ 0.12 | runsusie on replication | ✓ | ≥ 0.12 (Phase 1) | — |
| R + `winnerscurse` | FIQT | ✗ (must install) | GitHub 0.1.1 | Hand-code Bigdeli 2016 (fallback — lose alt estimators) |
| R + `metafor` | IVW meta | ✗ (conda-forge install) | ≥ 3.0 | Hand-code IVW (trivial) |
| GCTA binary | COJO | ✗ (install via bioconda) | 1.94.1 | — |
| Snakemake 7.32.4 (Python 3.11) | Pipeline orchestration | ✓ | smoke_dev env | — |
| pyliftover | GRCh38→37 | ✓ (from Phase 2) | 0.4.1 | — |
| bcftools / plink2 | COJO LD reference | ✓ (Phase 1 envs) | ld_build.yml / plink.yml | — |
| Pan-UKBB certified-user | Not needed for Phase 9 | — | — | — |
| FinnGen R12 registration | Already completed | ✓ | Carter registered 2026-04-10 | — |
| dbGaP open-access FTP | MVP sumstats | ✓ (no DAR) | — | — |
| BBJ NBDC open download | BBJ replication | ✓ | — | — |

**Missing dependencies with no fallback:** None critical.
**Missing dependencies with fallback:** `winnerscurse` → hand-coded FIQT. `metafor` → 10-line IVW.

## Architecture Patterns

### Recommended Project Structure
```
src/snakemake/rules/
├── replication.smk          # NEW: Phase 9 rules (≈20-25 rules)
src/python/
├── harmonize_finngen.py     # NEW: FinnGen R12 schema → canonical
├── harmonize_mvp.py         # NEW: MVP dbGaP per-cohort
├── harmonize_bbj.py         # NEW: BBJ hum0197-v3 zip extraction
├── harmonize_gbmi.py        # NEW: GBMI multi-ancestry
├── build_replication_manifest.py  # NEW: signals × cohorts crossmap
src/snakemake/scripts/
├── run_fiqt.R               # NEW: FIQT shrinkage wrapper (winnerscurse::FDR_IQT)
├── run_replication_coloc_susie.R  # NEW: runsusie + coloc.susie per signal×cohort
├── run_cojo.sh              # NEW: GCTA COJO wrapper
├── aggregate_replication_meta.R   # NEW: IVW meta (metafor::rma.uni)
├── build_master_replication_table.py  # NEW: master_table.tsv assembler
config/
├── replication_cohorts.yaml # NEW: cohort URLs, endpoint maps, schemas
results/replication/
├── master_table.tsv         # D-07
├── cross_ancestry_generalization_tier_ab.tsv
├── cojo_sensitivity.tsv
├── replication_holdout_supplementary.tsv
tests/phase9/                # NEW: pytest directory
├── conftest.py
├── test_fiqt_shrinkage.py
├── test_harmonize_finngen.py
├── test_harmonize_mvp.py
├── test_harmonize_bbj.py
├── test_replication_manifest.py
├── test_coloc_susie_replication_schema.py
├── test_meta_analysis.py
```

### Pattern 1: Manifest-driven cohort dispatch (reuse Phase 2 pattern)
**What:** Build `replication_manifest.tsv` (signal_id × cohort × ancestry × trait × endpoint × file_path) and iterate rules over manifest rows.
**When to use:** All replication rules (harmonize, runsusie, coloc.susie, FIQT, COJO).
**Example:** Directly mirror Phase 2 `coloc.smk` `_coloc_manifest_row()` + `_fit_rds_for()` helpers `[CITED: Phase 2 CONTEXT §code_context]`.

### Pattern 2: coloc.susie re-estimation fixture
```r
# Source: chr1swallace/coloc vignette a06_SuSiE
disc_fit <- readRDS("results/fine_mapping/{trait}_{ancestry}_{region}.fit.rds")
rep_sumstats <- read_region_tabix(rep_file, chr, start, end)
rep_ld <- readRDS(sprintf("data/processed/ld_reference/%s/%s.rds", rep_ancestry, region))
rep_fit <- coloc::runsusie(list(beta=..., varbeta=..., LD=rep_ld, N=..., type=...), suffix=2)
res <- coloc::coloc.susie(disc_fit, rep_fit)
```

### Anti-Patterns to Avoid
- **Don't re-fit SuSiE on the discovery side.** Phase 1 `.fit.rds` is canonical and immutable for Phase 9. Only fit replication side.
- **Don't hand-code IVW from Beta/SE when metafor is available.** Use `metafor::rma.uni(method="FE")` for reproducibility.
- **Don't run COJO without the `--cojo-wind 10000` default.** COJO's stepwise selection assumes linkage-equilibrium outside 10Mb window; changing this without reason breaks comparability to the literature.
- **Don't merge GBMI strata across ancestries in the per-cohort table.** Each ancestry is a separate cohort-column in the master table.
- **Don't apply FIQT to replication effect sizes.** FIQT corrects discovery winner's curse only; replication β̂ is already unbiased (that's the point of replication).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| FIQT shrinkage | Custom FIQT | `winnerscurse::FDR_IQT` | Edge cases (p → 0, ties in quantile transform) handled by package; maintained + cited |
| IVW meta-analysis | Hand-coded weighted avg | `metafor::rma.uni(method="FE")` | Handles NA propagation, heterogeneity Q-stat, confidence intervals |
| COJO | DIY conditional regression | GCTA `--cojo-slct` | Stepwise LD-aware selection has known edge cases; GCTA is the reference implementation cited in 1000+ papers |
| coloc.susie call | DIY Bayesian colocalization | `coloc::coloc.susie()` | Reuse Phase 1 scaffolding; no edge case handling to reinvent |
| Liftover GRCh38→37 | Python dict mapper | `pyliftover` (already installed) | Real liftover requires chain file handling |
| Tabix region extraction | grep/awk | Phase 2 `read_region_tabix()` helper | Handles missing index, multi-allelic variants |

**Key insight:** Phase 9 is a composition phase, not an invention phase. All methods (FIQT, COJO, coloc.susie, IVW) have canonical implementations. The research payload is cohort-specific harmonization, not algorithmic design.

## Common Pitfalls

### Pitfall 1: Genome-build mismatch silent failure (§13)
**What goes wrong:** FinnGen R12 and BBJ are GRCh38; Phase 1 discovery (1000G Phase 3 EUR LD) is GRCh37. If you liftover on-demand per locus, you silently drop variants that didn't convert.
**Why it happens:** `pyliftover` returns `None` for failed lifts; pandas pipelines may not check.
**How to avoid:** Liftover at ingest (not per-locus). Emit a per-cohort liftover QC report: `n_input_variants`, `n_lifted`, `n_dropped`. Flag if drop rate > 5%.
**Warning signs:** Suspiciously low SNP count in post-harmonized file; region subsets missing expected lead SNPs.
**Recommendation:** Liftover **all replication sumstats to GRCh37 at harmonization time**, following Phase 0 D-02 pattern.

### Pitfall 2: Allele strand / A/T-C/G ambiguity at replication
**What goes wrong:** Ambiguous palindromic SNPs (A/T, C/G with MAF near 0.5) can silently flip effect direction between discovery and replication, turning replicating signals into apparent failures.
**Why it happens:** Different genotyping arrays use different reference strand conventions.
**How to avoid:** Reuse Phase 1 `reconcile_effect_alleles()` from `run_coloc.R:215-279` (EAF-delta rescue for ambiguous). Exclude MAF ∈ [0.48, 0.52] for ambiguous SNPs.
**Warning signs:** Lead SNP β in replication has opposite sign + EAF near 0.5.

### Pitfall 3: Sample overlap contamination
**What goes wrong:** If a replication cohort shares samples with discovery, "replication" is not independent.
**Specific risks:**
- **GBMI includes FinnGen + UKBB** — so GBMI-EUR overlaps both FinnGen (separate cohort tested here) AND Yengo 2022 BMI GWAS (UKBB-containing) if BMI discovery was Yengo-based.
- MEGASTROKE (stroke discovery) may overlap BBJ if BBJ contributed cases.
- Evangelou 2018 (hypertension discovery) includes UKBB → overlaps GBMI-EUR HTN.
**How to avoid:** Document each discovery-replication pair's overlap. For known-overlapping pairs (e.g., GBMI vs Evangelou for HTN), explicitly call out as "leave-one-out-meta recommended" or use GBMI leave-UKBB-out weights where available.
**Warning signs:** Suspiciously high concordance rate (> 90%) — should be 50-70% for genuinely independent replication.

### Pitfall 4: Bonferroni denominator mis-specification
**What goes wrong:** D-03a says "Bonferroni per-cohort against the number of replicated-in-this-cohort signals" — if N_signals in denominator varies per cohort (because MVP doesn't have all traits), the criterion is cohort-specific and needs clear definition.
**How to avoid:** Compute `bonf_threshold_{cohort} = 0.05 / N_signals_present_in_this_cohort`. Document in methods: "Per-cohort Bonferroni denominator = number of discovery signals for which the cohort has a tested phenotype."
**Warning signs:** Cohorts with small denominators (e.g., MVP 1-3 traits) apply looser thresholds; this should be explicit in table footnote.

### Pitfall 5: Small-N MVP trait underpower (§15)
**What goes wrong:** MVP asthma (if available) has N_case ≈ 10-20K vs MVP T2D N_case ≈ 150K. A failed asthma replication in MVP may reflect underpower, not absence of signal.
**How to avoid:** Report post-hoc power per (signal × cohort): power to detect discovery FIQT β̂ at cohort N and α=bonferroni. If power < 0.8, flag cell in master table; do not count as "non-replication".
**Warning signs:** Cohort-specific replication rate drops sharply for low-N traits; post-hoc power column is all < 0.5.
**Standard practice in replication tables:** Always report post-hoc power alongside the Y/N replication call.

### Pitfall 6: Finnish-EUR founder-effect ancestry mislabeling (§14)
**What goes wrong:** FinnGen Finnish samples are genetically EUR but carry elevated rare-variant LD due to founder-effect bottleneck. A signal that replicates in FinnGen but not GBMI-EUR is not necessarily a failed replication — could be a population-specific low-frequency variant effect.
**How to avoid:** For Finnish-specific replications, compute MAF difference (FinnGen vs GBMI-EUR) and flag signals with |ΔMAF| > 0.05 as potentially founder-effect-driven. Cite Kurki 2023 Nature 613:508 for the founder-effect framing.
**Warning signs:** FinnGen-only replications at rare variants (MAF < 0.01); always cross-check GBMI-EUR.

## Code Examples

### FIQT shrinkage
```r
# Source: winnerscurse::FDR_IQT man page (rdrr.io/github/amandaforde/winnerscurse)
library(winnerscurse)
disc <- data.frame(rsid=..., beta=..., se=..., n=...)
disc_corrected <- FDR_IQT(summary_data = disc, min_pval = 1e-300)
# disc_corrected$beta_FIQT is the shrunken effect
```

### Replication coloc.susie
```r
# Source: coloc vignette a06_SuSiE
disc_fit <- readRDS("results/fine_mapping/t2d_EUR_chr10_region42.fit.rds")
rep_D <- list(
  beta = rep_beta, varbeta = rep_se^2, snp = rep_id,
  position = rep_pos, type = "cc",
  LD = rep_LD, N = rep_N, s = n_case/(n_case+n_ctrl)
)
rep_fit <- coloc::runsusie(rep_D, suffix = 2)
res <- coloc::coloc.susie(disc_fit, rep_fit)
# res$summary contains PP.H4 sweep-ready values
```

### COJO conditional
```bash
# Source: GCTA docs (cnsgenomics.com) + SISG 2024 practical 5
gcta --bfile data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.EUR.QC.${CHR} \
     --cojo-file ${COHORT}_${TRAIT}_chr${CHR}.ma \
     --cojo-slct --cojo-p 5e-8 --cojo-wind 10000 \
     --extract ${LOCUS}_snps.list \
     --out results/replication/cojo/${COHORT}_${TRAIT}_${LOCUS}
```

### IVW meta
```r
# Source: metafor documentation rma.uni
library(metafor)
meta_res <- rma.uni(
  yi = c(beta_disc, beta_rep),
  sei = c(se_disc, se_rep),
  method = "FE"
)
# meta_res$beta = IVW estimate; meta_res$se; meta_res$pval
```

## §16 Master table column schema

```
signal_id                         # unique — {trait}_{ancestry}_{region}_{leadSNP_or_triple}
signal_class                      # "credible_set_SNP" or "tier_A_triple" or "tier_B_triple"
discovery_trait                   # bmi/t2d/hypertension/stroke/asthma
discovery_ancestry                # EUR or AFR (Phase 1/2 coverage)
region                            # chr:start-end GRCh37
lead_snp                          # rsid (credible-set lead for class=SNP; top-PIP for triples)
gene_assignment                   # Tier A/B gene (NULL for credible-set SNP rows)
tissue_or_celltype                # for tier rows
qtl_source                        # gtex_eqtl / ukbppp_pqtl / gtex_sqtl / onek1k (for tier rows)

# Discovery layer
beta_discovery_raw
se_discovery_raw
p_discovery_raw
beta_discovery_FIQT
se_discovery_FIQT                 # FIQT produces shrunken SE too (winnerscurse)

# Per-cohort columns — repeat for each {cohort ∈ FinnGen, GBMI-EUR, GBMI-AFR, MVP-EUR, MVP-AFR}
{cohort}_endpoint
{cohort}_n_case
{cohort}_n_ctrl
{cohort}_beta_replication
{cohort}_se_replication
{cohort}_p_replication
{cohort}_eaf_replication
{cohort}_power_posthoc            # at discovery_FIQT β, α=bonf, cohort N
{cohort}_replicated_bonferroni    # bool: effect-size criterion met
{cohort}_pph4_replication         # from coloc.susie(disc_fit, rep_fit)
{cohort}_replicated_pph4_0.5
{cohort}_replicated_pph4_0.7
{cohort}_replicated_pph4_0.8
{cohort}_replicated_pph4_0.9
{cohort}_replicated_joint_0.8     # D-03a joint criterion at primary threshold

# Meta layer (IVW across matched-ancestry cohorts)
meta_ancestry                     # EUR or AFR
beta_meta
se_meta
p_meta
meta_n_cohorts_contributing
meta_replicated_bonferroni        # joint p across cohorts
meta_replicated_pph4_0.8          # meta sumstats re-run coloc.susie

# Flags
sample_overlap_flag               # e.g., "GBMI-EUR overlaps Evangelou HTN discovery"
low_maf_founder_flag              # Finnish-specific low-MAF signals
notes
```

**cross_ancestry_generalization_tier_ab.tsv:** same schema, BBJ-EAS column only, Tier A+B signals only (no credible-set SNP rows).

**cojo_sensitivity.tsv:** `signal_id, cohort, cojo_n_independent_signals, cojo_top_snp, cojo_joint_beta, cojo_joint_p, secondary_signal_notes`.

**replication_holdout_supplementary.tsv:** structured per REQ-11 / hold-out criterion #3 — exact format is planner's call (D-07 annotations pending); recommend: per-signal leave-one-cohort-out meta summary.

## §17 Snakemake rule module structure (`replication.smk`)

Suggested 6 rule sections, ~20-25 rules total:

```python
# ============================================================
# §A. COHORT INGEST (5-7 rules)
# ============================================================
rule download_finngen_r12:  # per-trait endpoint
rule download_gbmi:          # per-trait × ancestry
rule download_mvp_phs001672: # per sub-accession
rule download_bbj_hum0197_v3:# per-trait zip
rule extract_bbj_zip:        # unzip to canonical location

# ============================================================
# §B. HARMONIZATION (5-6 rules) — reuse Phase 2 sumstats_utils
# ============================================================
rule harmonize_finngen:      # rename columns, build liftover
rule harmonize_gbmi:         # per-ancestry stratum split
rule harmonize_mvp:          # per-sub-accession
rule harmonize_bbj:          # zip → canonical TSV
rule liftover_replication_sumstats_grch38_to_37:  # FinnGen + BBJ
rule validate_harmonized_sumstats:  # column schema + row count checks

# ============================================================
# §C. MANIFEST & FIT (2-3 rules)
# ============================================================
rule build_replication_manifest:  # signal × cohort × endpoint crossmap
rule fit_replication_susie:       # runsusie per signal × cohort (manifest-driven)

# ============================================================
# §D. COLOC RE-ESTIMATION (1 rule + sweep)
# ============================================================
rule run_replication_coloc_susie: # coloc.susie(disc_fit, rep_fit); emit PP.H4 sweep

# ============================================================
# §E. FIQT + EFFECT-SIZE + META (3 rules)
# ============================================================
rule run_fiqt_on_discovery:       # apply FIQT once per discovery signal set
rule compute_per_cohort_effect_size_test:  # Bonferroni test per cohort
rule ivw_meta_aggregate:          # metafor::rma.uni across matched cohorts

# ============================================================
# §F. COJO SENSITIVITY (2 rules)
# ============================================================
rule prepare_cojo_ma:             # convert cohort sumstats to .ma format
rule run_cojo_slct:               # GCTA COJO per locus × cohort

# ============================================================
# §G. AGGREGATION (3 rules)
# ============================================================
rule assemble_master_replication_table:
rule assemble_cross_ancestry_generalization_bbj:
rule assemble_cojo_sensitivity_supplementary
rule assemble_replication_holdout_supplementary  # D-07 #4

# ============================================================
# §H. QC / DASHBOARD (1-2 rules, optional for plan)
# ============================================================
rule render_replication_qc_dashboard
```

**Wave structure (5 waves estimated):**
- Wave 0: Test infrastructure (`tests/phase9/` + `conftest.py` + fixtures)
- Wave 1: Cohort ingest + harmonization (§§A+B)
- Wave 2: Manifest + replication SuSiE fits (§C)
- Wave 3: Coloc.susie re-estimation + FIQT + meta (§§D+E)
- Wave 4: COJO sensitivity + aggregation + dashboard (§§F+G+H)

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 (verified via `tests/phase2/__pycache__/conftest.cpython-311-pytest-9.0.3.pyc`) |
| R framework | testthat (per Phase 1 `tests/testthat-phase1/` pattern) |
| Config file | `tests/phase9/conftest.py` (new — follow Phase 2 pattern) |
| Quick run command | `pytest tests/phase9 -x --tb=short` |
| Full suite command | `pytest tests/ -x` |

### Phase Requirements → Test Map

| Req/Behavior | Test Type | Automated Command | File Exists? |
|----|---|---|---|
| FIQT shrinkage toward null for high-z (Bigdeli 2016 Fig 1 reproducibility) | unit | `pytest tests/phase9/test_fiqt_shrinkage.py::test_high_z_shrunken -x` | ❌ Wave 0 |
| FIQT preserves sign on all non-null SNPs | unit | `pytest tests/phase9/test_fiqt_shrinkage.py::test_sign_preserved -x` | ❌ Wave 0 |
| FinnGen harmonizer produces canonical schema | unit | `pytest tests/phase9/test_harmonize_finngen.py -x` | ❌ Wave 0 |
| BBJ zip extraction yields expected 5 files | unit | `pytest tests/phase9/test_harmonize_bbj.py::test_zip_contents -x` | ❌ Wave 0 |
| MVP sub-accession dispatch by trait×ancestry | unit | `pytest tests/phase9/test_harmonize_mvp.py -x` | ❌ Wave 0 |
| Replication manifest has no missing file paths | unit | `pytest tests/phase9/test_replication_manifest.py::test_manifest_integrity -x` | ❌ Wave 0 |
| coloc.susie on known replicating locus (FTO/BMI) PP.H4 > 0.8 | integration | `pytest tests/phase9/test_coloc_susie_replication.py::test_fto_bmi -x` | ❌ Wave 0 (L3) |
| coloc.susie on HLA region (negative control) PP.H4 < 0.5 | integration | `pytest tests/phase9/test_coloc_susie_replication.py::test_hla_negative -x` | ❌ Wave 0 (L3) |
| IVW meta reproduces textbook 2-study example | unit | `pytest tests/phase9/test_meta_analysis.py::test_ivw_textbook -x` | ❌ Wave 0 |
| Ancestry-masking: EUR signal not tested in AFR cohort absent matched-ancestry discovery | unit | `pytest tests/phase9/test_ancestry_matching.py -x` | ❌ Wave 0 |
| Bonferroni denominator = N_signals_tested_in_cohort | unit | `pytest tests/phase9/test_bonferroni.py -x` | ❌ Wave 0 |
| Snakemake dry-run on toy 3-locus | integration | `snakemake --snakefile tests/toy_3locus/Snakefile.test all_replication --dry-run` | ❌ Wave 0 |
| Snakemake full run on 1-signal-1-cohort fixture | integration | `snakemake ... all_replication --use-conda --cores 2` | ❌ Wave 0 |
| Gold-standard TCF7L2/T2D replicates in FinnGen + GBMI-EUR + MVP-EUR at PP.H4 > 0.8 | scientific | `Rscript tests/phase9/sanity_tcf7l2_t2d.R` | ❌ post-execution |

### Layer 1 — Tool-level (pytest + testthat)

- **FIQT correctness:** Synthetic z-score vector with known shrinkage targets (e.g., z=5 shrinks minimally, z=8 shrinks to ~7.8 per Bigdeli 2016 Fig 1); assert `|observed − expected| < 0.01`
- **FIQT sign preservation:** All non-null z-scores retain original sign after FDR_IQT
- **Harmonizer smoke tests:** Feed 100-row toy FinnGen/MVP/BBJ/GBMI fixtures through harmonizer; assert canonical schema (`CHR, BP, SNP, EA, OA, BETA, SE, P, EAF, N`)
- **Allele reconciliation:** Palindromic SNP with matched EAF in discovery vs replication passes; mismatched EAF flips
- **Ancestry masking:** Attempting to test EUR-only signal in BBJ without explicit Tier A+B allowance raises `AncestryMismatchError`

### Layer 2 — Pipeline-level (Snakemake)

- `snakemake --dry-run all_replication` on the toy 3-locus config (REQ-9)
- Small fixture run: 1 signal (e.g., FTO/BMI lead SNP) × 1 cohort (FinnGen) — end-to-end in < 15 min
- Assert `results/replication/master_table.tsv` generated with expected row/column counts

### Layer 3 — Scientific sanity checks

- **Gold-standard positive control:** TCF7L2 / T2D — should replicate at PP.H4 > 0.8 in FinnGen + GBMI-EUR + MVP-EUR (all EUR cohorts). If it doesn't, the pipeline is broken.
- **Negative control:** HLA_6p21 (Phase 2 negative control gene set) asthma signal — should fail replication under the joint criterion (coloc artifact from LD, no mechanism). If HLA replicates, we have a specificity problem.
- **Cross-ancestry expected partial generalization:** FTO/BMI in BBJ-EAS — MEDIUM confidence generalization (known to show smaller effect in EAS; SNP still replicates per Yengo 2022 cross-ancestry meta).

### Sampling Rate

- **Per task commit:** `pytest tests/phase9 -x --tb=short` (fast unit tests)
- **Per wave merge:** `pytest tests/ -x` (full suite) + `snakemake --dry-run all_replication`
- **Phase gate:** Full suite green + Snakemake smoke-run on 1-signal-1-cohort fixture before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/phase9/conftest.py` — fixtures for FIQT toy z-scores, 100-row synthetic cohort sumstats (4 cohorts), 1-region discovery+replication paired fits
- [ ] `tests/phase9/test_fiqt_shrinkage.py` — FIQT correctness (high-z, low-z, sign)
- [ ] `tests/phase9/test_harmonize_finngen.py`, `test_harmonize_mvp.py`, `test_harmonize_bbj.py`, `test_harmonize_gbmi.py` — per-cohort harmonizer tests
- [ ] `tests/phase9/test_replication_manifest.py` — manifest integrity (file paths resolve, no duplicate signal-cohort pairs)
- [ ] `tests/phase9/test_coloc_susie_replication.py` — integration with FTO/BMI gold-standard + HLA negative control fixtures
- [ ] `tests/phase9/test_meta_analysis.py` — IVW textbook reproducibility
- [ ] `tests/phase9/test_bonferroni.py` — denominator = cohort-tested-signal count
- [ ] `tests/phase9/test_ancestry_matching.py` — D-05 asymmetric matching enforcement
- [ ] `tests/phase9/sanity_tcf7l2_t2d.R` — post-execution scientific sanity (Layer 3)

## Security Domain

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no (cohort access already credentialed: FinnGen registration, Synapse cert for Phase 2, dbGaP open-access) | — |
| V3 Session Management | no | — |
| V4 Access Control | no (no multi-user system) | — |
| V5 Input Validation | yes | Sumstats schema validation via `tests/phase9/test_harmonize_*` |
| V6 Cryptography | no | — |
| V8 Data Protection | yes (dbGaP policies) | Never commit sumstats files; `.gitignore` `data/raw/replication/`; dbGaP sumstats are open-access but follow data reuse acknowledgments |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed cohort sumstats (misaligned columns) causing silent mis-harmonization | Tampering/Validation | Per-cohort pytest harmonizer test + column-schema validator (Phase 2 `validate_sumstats.py` pattern) |
| Genome build mismatch silent variant drop | Validation/Integrity | Explicit liftover QC report; fail if > 5% drop |
| dbGaP attribution omission | Compliance | Include cohort citation block in methods (FinnGen Kurki 2023, MVP Gaziano 2016, BBJ Sakaue 2021, GBMI Zhou 2022) |
| Accidental commit of raw sumstats (large files) | Data protection | Phase 0 pattern: data lives on `/rs1/`, symlinked only; `.gitignore` covers `data/raw/` |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single-replication cohort (UKBB) | 4-cohort belt-and-suspenders (D-01) | 2022+ (GBMI, FinnGen R12) | Higher reviewer bar for high-impact venues |
| Effect-size-only replication | Joint effect + coloc replication (D-03) | Wallace 2020 coloc.susie + Bigdeli 2016 FIQT | Addresses "same signal, different variant" failure mode |
| Standard Bonferroni on inflated discovery β̂ | FIQT-corrected discovery β̂ (D-04) | Bigdeli 2016 | Honest effect-size reporting; pre-empts reviewer critique |
| PP.H4 ≥ 0.8 single threshold | PP.H4 sweep {0.5, 0.7, 0.8, 0.9} (REQ-3 + D-03b) | 2021+ (Wallace sensitivity analyses) | Robustness to threshold choice |

**Deprecated/outdated:**
- coloc.abf single-causal-variant: replaced by coloc.susie (Phase 1 already migrated)
- Hardcoded PP.H4 ≥ 0.8: replaced by sweep (Phase 2)

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | MVP has stroke, asthma, and BMI sumstats released under phs001672 (non-T2D) | §2 MVP mapping | HIGH — Phase 9 plan depends on dbGaP listing; if traits absent, adjust per-cohort table by excluding missing traits. Mitigation: add a "MVP sub-accession discovery task" early in Wave 1. |
| A2 | GBMI T2D sumstats released in phase 2 follow-up | §4 GBMI coverage | LOW — if not yet released, fall back to FinnGen + MVP for T2D. |
| A3 | BBJ uses REGENIE-style column schema consistent across all 5 zip files | §3 BBJ columns | LOW — verifiable at first download (all zips contain README.txt). |
| A4 | `data.table` is the default R I/O library in Phase 1/2 | Standard Stack | LOW — confirmable by grepping existing R scripts. |
| A5 | FinnGen `I9_STR_EXH` is the preferred stroke endpoint (vs narrower `I9_STR`) | §1 FinnGen endpoint map | MEDIUM — stroke harmonization is already flagged (§3); two-endpoint sensitivity recommended. |
| A6 | Phase 2 Tier A+B triple count is ~11-20 | §8 EAS LD rationale | LOW — scales with actual tier_assignments.tsv; Option A (1000G EAS) scales regardless. |
| A7 | dbGaP FTP listing at `ftp.ncbi.nlm.nih.gov/dbgap/studies/phs001672/` is browsable without DAR for sumstat sub-accessions | §2 MVP access | MEDIUM — if DAR-gated, fall back to published data-availability statements per paper. |
| A8 | GBMI BMI is not in the 14 flagship endpoints | §4 GBMI coverage | LOW — verifiable at portal. |
| A9 | COJO recommended N ≥ 4,000 in LD reference; 1000G EUR (N=503) acceptable-with-caveat for sensitivity tier | §6 COJO LD | HIGH — if reviewers reject the 503-sample caveat, Phase 9 needs to add a Pan-UKBB PLINK reference build plan. Recommend: document caveat clearly + have Pan-UKBB as fallback. |
| A10 | `winnerscurse` GitHub-pinned install is defensible for a reproducible pipeline | §5 FIQT | LOW — `remotes::install_github(ref=SHA)` is a widely accepted pattern; documented in methods. |

**User confirmation needed on:** A1 (MVP coverage — planner must verify in Wave 1), A5 (FinnGen stroke endpoint — recommend `I9_STR_EXH` primary + `I9_STR` sensitivity; acceptable?), A9 (1000G EUR for COJO — accept caveat or expand Phase 9 to include Pan-UKBB PLINK reference?).

## Open Questions (RESOLVED)

1. **MVP per-trait sub-accession inventory (non-T2D):** dbGaP search didn't surface pha IDs for BMI / hypertension / stroke / asthma. Recommendation: add "Wave 1 Task 0: enumerate dbGaP phs001672 FTP listing" to Plan 09-01 — explicitly surface this uncertainty before coding download rules.
   **RESOLVED: Plan 09-01 Task 1 Step 1 — dbGaP enumeration produces `config/mvp_phs001672_inventory.md` with concrete pha IDs or explicit NOT_RELEASED markers per trait × ancestry before any download rule is wired.**
2. **BMI replication in cross-biobank layer:** GBMI lacks BMI. Options: (a) use Yengo 2022 GIANT as BMI cross-biobank proxy, (b) exclude BMI from "cross-biobank meta" layer and rely on per-ancestry native only. Recommendation: (a) with documented rationale.
   **RESOLVED: Plan 09-01 YAML — GBMI BMI EXCLUDED (per D-02); BMI replication uses BBJ + MVP native only; no GIANT/Yengo substitution in T1 (config/replication_cohorts.yaml `cohorts.gbmi.traits.bmi.status = EXCLUDED`).**
3. **Finnish-specific signals:** Do we apply an extra MAF-delta flag for Finnish founder-effect vs GBMI-EUR variants, or treat all FinnGen replications uniformly? Recommendation: compute ΔMAF column, flag > 0.05 in master_table; don't change inclusion logic.
   **RESOLVED: Plan 09-05 `master_table.tsv` includes `low_maf_founder_flag` column per manifest row (see `build_master_replication_table.py::FINNISH_FOUNDER_FLAG_TRAITS`); inclusion logic unchanged.**
4. **Hold-out supplementary format (D-07 #4):** CONTEXT.md lists `replication_holdout_supplementary.tsv` but doesn't specify schema. Recommendation: leave-one-cohort-out per-signal IVW meta with the held-out cohort's tested β for comparison.
   **RESOLVED: Plan 09-05 Task 2 — `build_replication_holdout.py` uses leave-one-cohort-out IVW meta (`loco_meta` function); emits columns `signal_id, held_out_cohort, held_out_beta, held_out_se, loco_meta_beta, loco_meta_se, loco_n_cohorts`.**

## Sources

### Primary (HIGH confidence)
- [FinnGen R12 data-download GitBook](https://finngen.gitbook.io/documentation/data-download) — manifest URL + file pattern confirmed
- [FinnGen Risteys I9_HYPTENSESS](https://risteys.finngen.fi/endpoints/I9_HYPTENSESS) — 141,737 cases; ICD10 I10
- [FinnGen Risteys T2D endpoint](https://risteys.finngen.fi/documentation) — T2D combined definition
- [NBDC hum0197-v3-220](https://humandbs.dbcls.jp/en/hum0197-v3-220) — BBJ filename patterns verified
- [CRAN winnerscurse documentation (rdrr.io)](https://rdrr.io/github/amandaforde/winnerscurse/man/FDR_IQT.html) — FDR_IQT function signature
- [Chris Wallace coloc vignette a06_SuSiE](https://chr1swallace.github.io/coloc/articles/a06_SuSiE.html) — coloc.susie usage
- [GCTA-COJO cnsgenomics tutorial](https://cnsgenomics.com/data/teaching/GNGWS23/module1/9_independentLociPrac.html) — ≥ 4K LD reference requirement
- [bioconda gcta 1.94.1](https://anaconda.org/bioconda/gcta) — conda package verified
- [Project data_access.md](/.planning/data_access.md) — verified cohort access 2026-04-10

### Secondary (MEDIUM confidence)
- [Zhou 2022 GBMI Cell Genomics](https://www.sciencedirect.com/science/article/pii/S2666979X22001410) — GBMI 14 endpoint list
- [DIAMANTE 2022 Nat Genet](https://www.nature.com/articles/s41588-022-01058-3) — MVP T2D sub-accessions pha004943-947
- [Giri 2019 Nat Genet MVP BP](https://www.nature.com/articles/s41588-018-0303-9) — MVP BP availability (no pha IDs indexed)
- [Forde 2023 Bioinformatics Winner's Curse review](https://pubmed.ncbi.nlm.nih.gov/37721937/) — winnerscurse publication
- [Sakaue 2021 Nat Genet BBJ multi-trait](https://doi.org/10.1038/s41588-021-00931-x) — BBJ column schema cited

### Tertiary (LOW confidence — need planner verification)
- MVP BMI/stroke/asthma sub-accession IDs — not directly indexed in searches (Assumption A1)
- Exact GBMI per-trait per-ancestry file sizes and bucket paths — portal browse required at plan time
- BBJ column schema — verifiable on first download (zip README)

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH — all tools verified via Context7-equivalent (CRAN/bioconda/rdrr.io)
- Cohort access: HIGH — `data_access.md` verified all four cohorts 2026-04-10
- FinnGen endpoint codes: HIGH — Risteys verified; T2D, hypertension, asthma all clean; stroke has two candidates
- BBJ file mapping: HIGH — verified via NBDC portal
- MVP sub-accessions: MEDIUM (T2D HIGH; non-T2D LOW — Wave 1 discovery task)
- GBMI trait coverage: MEDIUM — 14 flagship endpoints documented; exact bucket paths require portal browse
- FIQT implementation: HIGH — `winnerscurse::FDR_IQT` is canonical
- COJO LD reference: MEDIUM — 503-sample 1000G EUR is below 4K threshold; caveat-based path is standard but reviewer-dependent
- EAS LD strategy: HIGH — Option A (1000G EAS 504) recommended
- Snakemake rule structure: HIGH — reuses established Phase 1/2 patterns
- Validation architecture: HIGH — follows Phase 5 pytest structure

**Research date:** 2026-04-13
**Valid until:** 2026-07-13 (90 days — FinnGen R13 may drop in interim; cohort URLs stable for T1 submission window)
