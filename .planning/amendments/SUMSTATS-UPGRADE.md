# SUMSTATS-UPGRADE — cross-ancestry cardiometabolic coloc project

Amendment to the coloc_analysis planning record.
Author: Carter K. Clinton (NCSU ASHES Lab)
Pivot date: 2026-04-22
Companion data: `SUMSTATS-UPGRADE.tsv`

---

## 1. Purpose

The preliminary coloc_analysis draft was anchored on a 5-trait x 50-curated-region scope using 2018-era GWAS summary statistics. Track B (discovery-oriented cross-ancestry fine-mapping + colocalization) is bottlenecked by stale sumstats: BMI at Yengo-2018 N~700k EUR, T2D at DIAGRAM-2018, stroke at MEGASTROKE-2018, Evangelou-2018 BP. The 2021-2022 release cycle has produced meta-analyses that are 1.5x-5x larger, add AFR/EAS/SAS/HIS components, and materially change the set of genome-wide significant lead variants — the exact signal that Track B programmatic region generation depends on. Upgrading sumstats across 9 traits ensures the 579-job DAG is regenerating genome-wide regions against current evidence, not against 5-year-old lead lists. Phenotype-definition locks (section 3) were set by the project lead and must not be silently relaxed downstream.

## 2. Summary table

| Metric | Count |
|---|---|
| Rows in `SUMSTATS-UPGRADE.tsv` (incl. header) | 48 |
| Data rows | 47 |
| Traits covered | 12 (BMI, T2D, hypertension, stroke, asthma, CAD, LDL, HDL, TG, TC, eGFR, HbA1c) |
| Unique (trait x ancestry) pairs | 45 (BMI-EUR and BMI-AFR each carry two source rows pending source lock) |
| Distinct source consortia | 10 (GIANT-UKBB, GIANT-23andMe, PAGE, DIAMANTE, Evangelou-ICBP, MVP, GIGASTROKE, GBMI, CARDIoGRAM-C4D-MVP, GLGC, CKDGen, MAGIC) |
| Ancestry strata | EUR, AFR, EAS, SAS, HIS, TRANS, MULTI |
| Rows with `dua_required = yes` | 1 (MVP BP Giri-2019, dbGaP phs001672) |
| Rows with `dua_pending` status | 3 (DIAMANTE-AFR, DIAMANTE-HIS — released on manuscript acceptance; MVP BP-AFR) |
| Rows with `already_downloaded` status | 1 (Evangelou 2018 SBP EUR) |
| Approximate cumulative-N footprint across all rows | ~20M observations (double-counting overlapping cohorts); effective independent N is smaller and is why `--overlap` is essential |

## 3. Per-trait rationale

### BMI
The user's brief says "Yengo 2022 GIANT+UKBB meta". There is no Yengo 2022 BMI paper — Yengo's 2022 Nature publication is the height saturation paper (`10.1038/s41586-022-05275-y`). The 2022 BMI-focused meta-analysis with a comparable footprint is **Loh / Lindgren 2022 Nat Commun** (`10.1038/s41467-022-35553-2`, "Genomics and phenomics of body mass index reveals a complex disease network"), which reports ~1.1M EUR and ~100k AFR. The TSV lists **both** the Yengo 2018 GIANT+UKB meta (N=681k EUR, GCST006900) as a conservative fallback (fully released sumstats via GIANT portal) **and** the Loh 2022 multi-ancestry meta (pending GWAS Catalog accession confirmation). The phenotype is continuous BMI inverse-rank-normal, matching the lock. For AFR, the TSV carries two sources: Loh 2022 AFR subset and Wojcik 2019 PAGE (N=49k, smaller but fully released). If the user truly meant a 2022 Yengo BMI manuscript I could not locate, this requires clarification (open question 1).

UKB dominates EUR BMI, which means it overlaps heavily with Evangelou BP, Aragam CAD, GBMI asthma, MAGIC HbA1c, GLGC lipids, CKDGen, GIGASTROKE, and DIAMANTE. MTAG overlap correction is non-negotiable.

### T2D (DIAMANTE 2022 Mahajan)
Mahajan et al. Nat Genet 2022 (`10.1038/s41588-022-01058-3`) is the definitive cross-ancestry T2D GWAS as of the pivot date: trans-ancestry N~1.34M (180,834 cases / 1.16M controls) across EUR, EAS, SAS, AFR, HIS. Phenotype is doctor-diagnosed T2D case-control, harmonized across contributing cohorts. EUR, EAS, SAS sumstats are publicly released from diagram-consortium.org. **AFR and HIS ancestry-specific sumstats are held until publication of the ancestry-stratified methods papers** per DIAGRAM's download page — as of 2026-04-22 these remain gated; need to recheck quarterly. Cohort overlap: UKB (EUR), BBJ (EAS), MVP (partial), FinnGen (partial). MTAG correction required for every EUR T2D pairing against BMI, CAD, HbA1c, lipids, BP.

### Hypertension (Evangelou 2018 SBP, MVP Giri 2019 AFR)
Evangelou 2018 ICBP+UKBB (GCST006624) is already on GPFS per user. Phenotype: SBP continuous, medication-adjusted (+15 mmHg adder for treated individuals). No adequate 2021+ public EUR replacement exists; the Keaton 2024 MVP+UKB BP meta is plausible but post-dates the pivot scope. For AFR, Giri 2019 MVP (`10.1038/s41588-018-0303-9`) is the largest publicly-documented AFR-SBP source but sits behind dbGaP phs001672 and requires a DUA. **This is the only DUA-gated row in the full TSV** and is on the critical path for AFR-BP.

### Stroke (GIGASTROKE 2022 Mishra)
Mishra et al. Nature 2022 (`10.1038/s41586-022-05165-3`, PMID 36180795). Trans-ancestry N~1.61M (110,182 cases / 1.5M controls). Phenotype lock is **all-stroke (AS)**, not ischemic-only (IS) or any subtype — this deviates from the preliminary draft which used MEGASTROKE IS. AFR subset is real and released: N=23,991 (3,961 cases / 20,030 controls) from PAGE, MVP-AFR, AAASPS, REGARDS. GWAS Catalog accessions GCST90104539-GCST90104544 span trait x ancestry combinations; exact per-row GCST must be resolved via the GWAS Catalog publication page at download time. Overlap: UKB (EUR), BBJ (EAS), FinnGen (EUR), MVP (AFR + EUR). Heavy MTAG correction required against CAD, BP, BMI.

### Asthma (GBMI Zhou 2022 Cell Genomics)
Zhou et al. Cell Genomics 2022 (`10.1016/j.xgen.2022.100210`, PMID 36778051). Multi-ancestry meta across 18 biobanks (UKB, FinnGen, BBJ, MGI, Estonia, BioMe, Lifelines, GS, GNH, many more). N=1.8M total (153,763 cases / 1.65M controls). EUR: 58,559 cases / 937,358 controls. AFR: 1,978 cases / 27,704 controls (small but non-zero). Phenotype lock is the GBMI harmonized PheCode pooling adult + childhood asthma — **does not separate severe/mild/allergic subtypes**. This limitation must be disclosed in the manuscript. Overlap: UKB, FinnGen, BBJ drive massive sharing with every other trait's GWAS that uses those biobanks.

### CAD (Aragam 2022 CARDIoGRAM+UKB+MVP)
Aragam et al. Nat Genet 2022 (`10.1038/s41588-022-01233-6`, PMID 36474045, GCST90132314). Trans-ancestry N~1.17M (181,522 cases). Primary release bundle is `Aragam_2022_CARDIoGRAM_CAD_GWAS.zip` hosted at `personal.broadinstitute.org/ryank/` (verified via KP4CD dataset page). Phenotype: composite CAD (MI + revascularization + angina-with-documented-CAD). **AFR-specific subset is NOT guaranteed to be released as a standalone file** — the paper reports a small cross-ancestry meta with Japanese BBJ but the ancestry-stratified AFR file may require direct author request. Check the ZIP contents after download; if AFR is absent, fall back to `no_adequate_source_available` and note in paper. Overlap: UKB (EUR), MVP (EUR + AFR), BBJ (EAS) — overlaps with Aragam-CAD-trans against Evangelou BP, Giri BP-AFR, DIAMANTE, GIGASTROKE, GLGC, GIANT.

### Lipids (GLGC 2021 Graham — LDL, HDL, TG, TC)
Graham et al. Nature 2021 (`10.1038/s41586-021-04064-3`). Hosted at `csg.sph.umich.edu/willer/public/glgc-lipids2021/` — verified live. Directory structure:
- `results/ancestry_specific/` — 90 files (5 traits x 5 ancestries x {main, nonFinnish-only, without-UKB}, tabix-indexed)
- `results/trans_ancestry/` — 20 files (5 traits x {main, without-UKB}, tabix-indexed)
- `results/sex_and_ancestry_specific_summary_stats/` — 200 files (for Phase 4 sex-stratified if needed)

Filename convention: `<TRAIT>_INV_<ANC>_HRC_1KGP3_others_ALL.meta.singlevar.results.gz` for AFR/EUR/SAS; `<TRAIT>_INV_<ANC>_1KGP3_ALL.meta.singlevar.results.gz` for EAS/HIS. Trait tokens: HDL, LDL, TC, logTG (note log-transformed), nonHDL. The TSV uses `TG` for the trait label but the file prefix is `logTG` — harmonization step must rename and document the log transform.

GLGC has 4 separate trait files per ancestry (LDL, HDL, TG, TC) — fanning out the TSV to 4 x 4 ancestries (trans, EUR, AFR, + EAS/SAS/HIS for LDL only as proof-of-concept) produces 16 rows. For scope control I kept LDL with all 5 ancestries and the other three traits with trans+EUR+AFR only. Adding EAS/SAS/HIS for HDL/TG/TC is straightforward — copy the LDL rows and swap file prefix.

Overlap: UKB, MVP, BBJ dominant. HDL x LDL x TG x TC within-GLGC sample overlap is ~100% (same-sample different-traits) — MTAG will need within-GLGC block structure in the bivariate-intercept matrix, not just cross-consortium structure.

### eGFR / CKD (CKDGen 2019 Wuttke + Morris 2019 AFR companion)
Wuttke et al. Nat Genet 2019 (`10.1038/s41588-019-0407-x`) is the largest released eGFR GWAS at pivot date. The brief's "CKDGen 2019" lock is accepted. **No published CKDGen 2021+ release has superseded Wuttke 2019** as of 2026-04-22 public knowledge — the Stanzick 2021 PRS extension and the Liu 2023 sex-stratified release exist but are smaller or task-specific. Phenotype: log(eGFR-creatinine) continuous, adjusted for age, sex, study covariates.

Trans-ethnic: N=765,348 (61 studies). European-American: N=567,460 (42 studies). **AFR-specific eGFR GWAS from CKDGen is Morris et al. 2019 Nat Commun** (`10.1038/s41467-019-11704-w`, N~16k AFR) — a companion paper to Wuttke. The TSV treats this as `Morris 2019 / Wuttke 2019` dual-citation for the AFR row. Files are at `ckdgen.imbi.uni-freiburg.de/files/Wuttke2019/` — verified live, direct HTTP download, no DUA.

Overlap: UKB + MGI dominate trans-ethnic; AFR has MVP-AFR overlap with Giri BP-AFR, Aragam CAD-AFR, DIAMANTE-AFR.

### HbA1c (MAGIC 2021 Chen)
Chen et al. Nat Genet 2021 (`10.1038/s41588-021-00852-9`). The multi-ancestry HbA1c paper. Files at `magicinvestigators.org/downloads/` (page returned 403 to WebFetch but URL is live — the 403 was anti-bot, verified via Wayback + search listing). Six ancestry files released: TA (trans-ancestry, N=281,416), EUR (N=123,665), AA (N=7,564), EAS (N=20,838), SAS (N=8,874), HISP (N=20,475), plus Uganda (excluded from the 9-trait scope). Phenotype: HbA1c continuous (mmol/mol), adjusted for age, sex, study.

FTP URLs use `ftp://web-ftp.ex.ac.uk/docs/downloads/` — FTP protocol, may require `curl --ftp-method` or plain wget. Note: Chen 2021 MAGIC uses rsid-based SNPID column which differs from chr:pos — harmonization step must cross-reference against a 1000G rsid-to-position map.

Overlap: UKB (EUR, heavy), BBJ (EAS partial), HCHS/SOL (HIS, AFR). Shares HCHS/SOL with GLGC-HIS/AFR, PAGE BMI-AFR, DIAMANTE-HIS. Shares BBJ with DIAMANTE-EAS, GIGASTROKE-EAS.

## 4. Sample overlap correction strategy

MTAG (Turley et al. 2018) requires an explicit accounting of sample overlap between each pair of input GWAS; the `--overlap` flag consumes an LDSC-bivariate-intercept matrix. Without it, MTAG's default assumption of independent samples systematically over-weights correlated traits (same-sample pairs produce inflated bivariate-intercept values that MTAG interprets as genetic correlation), inflating discovery counts and producing false-positive MTAG-specific loci.

**LDSC bivariate-intercept matrix construction.**
For each of the 45 input sumstats, munge to LDSC format (`munge_sumstats.py` with HM3-SNP set, N harmonized from source). Then run `ldsc.py --rg` pairwise across all `C(45,2) = 990` pairs, or equivalently use `--rg-cross` with a trait list and a single LDSC invocation that produces the full matrix. The bivariate intercept (not the rg, not the h2) is the value MTAG needs. Output lives at `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv` — 45 x 45 symmetric, diagonal = 1 (single-trait intercept from univariate LDSC), off-diagonal = bivariate intercepts. Store provenance of which LD panel (EUR-only 1KG Phase 3 for EUR-EUR pairs; AFR-only for AFR-AFR; cross-ancestry pairs use the shared-AFR+EUR LDSC release or PopCorn).

**Highest-overlap source pairs.** UKB drives the densest overlap: every EUR row listed UKB in `sample_source_cohort`. Expected bivariate intercepts > 0.5 for these pairs (each contributes ~400k UKB samples out of 600k-1M total per-trait N):
- BMI-EUR <-> Evangelou BP-EUR
- BMI-EUR <-> Aragam CAD-EUR
- BMI-EUR <-> GBMI Asthma-EUR
- BMI-EUR <-> GLGC LDL/HDL/TG/TC-EUR
- BMI-EUR <-> MAGIC HbA1c-EUR
- BMI-EUR <-> CKDGen eGFR-EUR
- BMI-EUR <-> DIAMANTE T2D-EUR
- BMI-EUR <-> GIGASTROKE Stroke-EUR
- (and every pairwise combination of the above — 36 UKB-UKB pairs total)

Within-GLGC overlap: LDL-EUR, HDL-EUR, TG-EUR, TC-EUR are **same-sample different-traits**. Bivariate intercept ~1.0 expected for these 6 within-trait pairs. MTAG will appropriately downweight these to the single-trait contribution after correction.

BBJ-BBJ overlap: DIAMANTE-EAS, GIGASTROKE-EAS, MAGIC-EAS, GLGC-EAS, GBMI-EAS, Aragam-EAS share BBJ. 15 pair combinations.

MVP-MVP overlap: Aragam-AFR, Giri BP-AFR, DIAMANTE-AFR, CKDGen AFR (via Morris 2019 MVP-AFR contribution). 6 pair combinations.

**Alternatives if MTAG overlap correction is insufficient.**
If post-MTAG mean chi^2 remains >1.2 and LDSC intercept > 1.1 on the MTAG output, escalate to mtCOJO (Zhu et al. 2018, `gcta64 --mtcojo-file`). mtCOJO conditions each focal trait on the others via a Mendelian-Randomization-style instrumental-variable adjustment and handles unmeasured confounders better than MTAG's fixed-covariance assumption. Trade-off: mtCOJO does not multi-trait meta-analyze, so it is a filter rather than a booster — use for sensitivity analysis, not primary discovery. If mtCOJO still shows residual inflation, drop the worst-offender pair from the MTAG input set.

**Validation checklist (post-MTAG).**
1. LDSC single-trait intercept on each MTAG output column — target <= 1.05 (match input); flag if >1.1.
2. Mean chi^2 of MTAG output vs. input — ratio should track MTAG's theoretical power gain (1.05-1.25x), not 1.5x+ which indicates inflation leaking through.
3. Manhattan plot comparison: MTAG-specific loci (hits gained after MTAG) should co-localize with biologically plausible neighbors; run a manual check on top 20 MTAG-only hits to look for implausible clusters.
4. Compare MTAG-EUR output to ancestry-specific replication in AFR/EAS for top hits — true signals should show same-direction effect in other ancestries.

## 5. Download strategy (ordered by ease)

**Tier 1 — direct public HTTP/FTP download, no portal nav, script-automatable.**
- GLGC 2021 — `csg.sph.umich.edu/willer/public/glgc-lipids2021/` open Apache directory index, wget recursive
- CKDGen 2019 Wuttke — `ckdgen.imbi.uni-freiburg.de/files/Wuttke2019/` open download, wget single file
- MAGIC 2021 Chen — `ftp://web-ftp.ex.ac.uk/docs/downloads/` FTP, curl `--ftp-method nocwd`
- Aragam 2022 CAD — `personal.broadinstitute.org/ryank/Aragam_2022_CARDIoGRAM_CAD_GWAS.zip` single ZIP, wget
- GIGASTROKE — GWAS Catalog FTP via GCST accessions (per-row accession must be resolved from `www.ebi.ac.uk/gwas/publications/36180795` at download time — page returned placeholder data in automated fetch, manual check required once during download, then scriptable via the resolved GCST)
- Yengo 2018 BMI — GIANT portal link `Meta-analysis_Locke_et_al+UKBiobank_2018_UPDATED.txt.gz`, wget

**Tier 2 — public but portal-gated, requires click-through on a consent/ToS page.**
- DIAMANTE 2022 — `diagram-consortium.org/downloads.html` — checkbox acceptance of "will not attempt re-identification" DUA-lite, then download links appear. Scriptable with cookie persistence (curl -c/-b) once accepted once. EUR, EAS, SAS available now; AFR and HIS pending.
- GBMI asthma — `globalbiobankmeta.org/resources` — Google-Sheets phenotype manifest manual lookup to resolve the exact asthma file URL, then direct download. Scriptable after first-time manifest scrape.
- PAGE Wojcik 2019 BMI-AFR — via GWAS Catalog; may require dbGaP accession phs000920 for raw individual data (not needed here; only sumstats).

**Tier 3 — DUA-gated.**
- MVP BP Giri 2019 (AFR SBP) — dbGaP phs001672. **Carter's action item:** submit DUA via NCBI dbGaP. Typical turnaround: 4-8 weeks. This is the sole DUA-required row.

**Tier 4 — AoU workbench-only (cannot export).**
- None of the 9 primary-trait locked sources live here. AoU is a backup for BMI-AFR / BP-AFR / HbA1c-AFR if other AFR sources fail — must be computed on the workbench and only effect sizes/SEs exported (AoU policy forbids individual-level export but allows sumstat-level export after review). Not needed for Track B discovery unless AFR-N is insufficient.

## 6. Harmonization pipeline alignment

Existing Phase 1 harmonization writes bgzipped, tabix-indexed TSV to `data/processed/sumstats_harmonized/<trait>_<ancestry>_<consortium>_<year>_GRCh37.tsv.bgz`. The following new sources slot in without custom code once column mapping is applied:

- **GIANT BMI Yengo 2018** — standard GIANT format (SNP, CHR, POS, Tested_Allele, Other_Allele, Freq_Tested_Allele, BETA, SE, P, N).
- **DIAMANTE 2022** — uses `chromosome(b37)`, `position(b37)`, `effect_allele`, `other_allele`, `effect_allele_frequency`, `beta`, `standard_error`, `p_value`, `Neff`. Uses Neff not N — harmonizer must preserve effective-N column.
- **GIGASTROKE** — GWAS Catalog harmonized format (standard).
- **CKDGen Wuttke** — uses `Chr`, `Pos_b37`, `Allele1`, `Allele2`, `Freq1`, `Effect`, `StdErr`, `P-value`, `n_total_sum` — straightforward.
- **GLGC 2021** — RVTESTS meta format, tabix pre-indexed. Already in bgzip+tbi shape — can symlink rather than re-tabix.
- **Aragam 2022** — uses `markername`, `chr`, `bp_hg19`, `effect_allele`, `noneffect_allele`, `effect_allele_freq`, `beta`, `se`, `pvalue`, `n_samples` — standard.
- **Yengo height/BMI GIANT** — standard GIANT.

**Custom harmonization flagged:**
- **MAGIC 2021 Chen** — uses rsid-only SNP_ID (no chr:pos). Requires an rsid-to-chr:pos crosswalk from 1000G Phase 3 or HRC to populate CHR/POS fields before tabix indexing. The existing Phase 1 `run_susie_rss.R` rsid-override logic (commit 7d54183) handles the reverse direction; a forward crosswalk step is needed here.
- **GLGC logTG** — trait file is `logTG_INV_*` but internal columns report betas on the log scale; colocalization with TG-reported external QTL or clinical TG measurements requires consistent log-transform.
- **GBMI asthma** — harmonized PheCode pooling requires explicit metadata column in the harmonized output so downstream phenotype-sensitivity analyses can re-stratify adult-vs-child if GBMI ever releases substrata.
- **Evangelou 2018 BP** — already harmonized in existing pipeline (user confirms `already_downloaded`).

## 7. Pre-processing QC checklist (per downloaded sumstat file)

Before a file is accepted into `data/processed/sumstats_harmonized/`, it must pass:

1. **Variant count sanity**: >= 5M variants for genome-wide EUR, >= 10M for trans-ancestry (imputation-dependent). Fail if <3M — likely a chromosome subset or a clumped file.
2. **MAF distribution**: plot MAF histogram; expect a U-shape in HRC/1KG-imputed data and a right-skew in array-only. Fail if >5% of variants have MAF=0 (bad QC upstream).
3. **GRCh build verification**: cross-check 10 random rsIDs (e.g., rs429358 at 19:44908684 for b37 / 19:45411941 for b38) against position. Fail if mismatch rate > 5%.
4. **Effect allele unambiguous**: column must be explicitly labeled `effect_allele` / `ALT` / `A1`. If label is just `Allele1`, require paper's README to disambiguate before accept.
5. **SE/beta ratio sanity via LDSC intercept**: run `munge_sumstats.py` and `ldsc.py --h2` on each file. Target intercept 1.0-1.1 for unlabeled confounding-free meta. Flag if intercept > 1.15 (residual stratification or sample overlap inflation).
6. **Lambda GC**: compute genomic control lambda. Flag if >1.2 for N>100k (indicates residual stratification not absorbed by LDSC intercept).
7. **Concordance with known positive control loci**: check FTO (16:53.8Mb b37) for BMI, TCF7L2 (10:114.7Mb) for T2D, APOE (19:45.4Mb) for LDL, UMOD (16:20.3Mb) for eGFR, 9p21.3 (9:22.1Mb) for CAD, ADRB1 (10:115.8Mb) for SBP. All should show p < 1e-8 at the lead SNP. Fail if any control locus is absent — likely wrong trait file.
8. **Strand consistency**: count the fraction of strand-ambiguous SNPs (A/T, C/G) and confirm MAF < 0.4 threshold applied by the source meta. If not, harmonizer drops ambiguous SNPs.
9. **N column integrity**: per-variant N should not exceed source-paper reported total N by >1%. Flag extreme outlier Ns (single-study leakage).

Each of the above writes a one-line PASS/FAIL record to `data/processed/sumstats_harmonized/qc_log/<trait>_<ancestry>_<year>_qc.tsv` with timestamp.

## 8. Storage plan

```
/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/
  data/
    raw/
      sumstats/
        giant_bmi_yengo_2018/
        diamante_t2d_mahajan_2022/
        gigastroke_mishra_2022/
        gbmi_asthma_zhou_2022/
        aragam_cad_2022/
        glgc_lipids_graham_2021/
        ckdgen_egfr_wuttke_2019/
        magic_hba1c_chen_2021/
        evangelou_bp_2018/              # already populated
        mvp_giri_bp_afr_2019/           # DUA-gated placeholder
        page_wojcik_bmi_afr_2019/
    processed/
      sumstats_harmonized/
        <trait>_<ancestry>_<consortium>_<year>_GRCh37.tsv.bgz
        <trait>_<ancestry>_<consortium>_<year>_GRCh37.tsv.bgz.tbi
        qc_log/
      ldsc_overlap/
        bivariate_intercept_matrix_2026-04.tsv
        munged/
```

Naming convention: `<trait>_<ancestry>_<consortium>_<year>_<build>.tsv.bgz` where trait is lowercase (bmi, t2d, sbp, stroke, asthma, cad, ldl, hdl, tg, tc, egfr, hba1c), ancestry is EUR|AFR|EAS|SAS|HIS|TRANS|MULTI, consortium is GIANT|DIAMANTE|GIGASTROKE|GBMI|CARDIoGRAM|GLGC|CKDGen|MAGIC|Evangelou|MVP|PAGE.

Symlinks: `data/processed/sumstats_harmonized/_LATEST/<trait>_<ancestry>.tsv.bgz -> <full filename>` so downstream Snakemake rules can reference stable paths across version bumps.

**Gitignore rules (already in place; confirm `.gitignore` excludes `data/`). Add explicit rule for `data/raw/sumstats/mvp_giri_bp_afr_2019/` so no accidental commit of dbGaP-covered data can occur even if the DUA permits local storage only.**

## 9. DUA / access critical path

| Source | DUA entity | Accession | Status as of 2026-04-22 | Timeline estimate | Action item |
|---|---|---|---|---|---|
| MVP BP Giri 2019 | dbGaP NCBI | phs001672 | Not submitted | 4-8 weeks from submission | Carter submits DUA via dbGaP eRA Commons portal |
| DIAMANTE AFR | DIAGRAM consortium | (email request) | Released on manuscript acceptance | Unknown — quarterly recheck | Watchlist `diagram-consortium.org/downloads.html`; no DUA until released |
| DIAMANTE HIS | DIAGRAM consortium | (email request) | Released on manuscript acceptance | Unknown — quarterly recheck | Same |

**Not DUA-gated (public download only):** everything else in the 45 rows.

For the preliminary Track B run, AFR BP is the single hard gap. Options:
1. Submit MVP dbGaP DUA immediately (4-8 week gate) — preserves full power.
2. Fall back to Giri 2019 summary-level in GWAS Catalog if the paper's public release exists (verify at `ebi.ac.uk/gwas/publications/30578418`).
3. Use AoU workbench to derive an independent AFR SBP GWAS on Carter's controlled-tier access, export sumstats only after AoU review (slower but no external DUA).

## 10. Open questions

1. **User's "Yengo 2022" for BMI** — no such paper exists for BMI. Confirm whether the intended source is Loh 2022 Nat Commun (1.1M EUR + 100k AFR multi-ancestry) or Yengo 2018 GIANT+UKB (700k EUR only). TSV carries both, but the authoritative lock must be set before download script launches.
2. **GIGASTROKE per-row GCST accessions** — the per-ancestry GCST numbers (e.g., the AFR all-stroke accession) could not be resolved via automated WebFetch of the GWAS Catalog publication page (returned placeholder data, likely JS-rendered). Manual browse of `ebi.ac.uk/gwas/publications/36180795` to pin each (trait, ancestry, subtype) to a GCST is a 15-minute human task before download-script writing. TSV rows list a placeholder like `GCST90104540-series`; fill in the exact integer.
3. **Aragam AFR release status** — the AFR CAD subset may not be in the public ZIP. Verify contents of `Aragam_2022_CARDIoGRAM_CAD_GWAS.zip` after first download. If absent, either remove the AFR row or fall back to an earlier MVP-AFR-CAD sumstat (Klarin 2018).
4. **GLGC trait coverage fanout** — TSV has LDL at 5 ancestries but HDL/TG/TC at only 3 (TRANS/EUR/AFR). Confirm whether Track B needs EAS/SAS/HIS for HDL/TG/TC or if LDL-only is sufficient for the cross-ancestry sensitivity analysis. Trivial expansion if needed.
5. **MAGIC FTP accessibility from NCSU HPC** — some HPC clusters block outbound FTP (port 21). Test `curl ftp://web-ftp.ex.ac.uk/docs/downloads/MAGIC1000G_HbA1c_TA.tsv.gz --head` from a compute node before scripting the download rule. Fallback: FTP via a login-node proxy or via the EBI-hosted mirror if MAGIC has one.
6. **PAGE BMI-AFR DUA status** — flagged as `dua_required = no` in the TSV per GWAS Catalog public availability, but individual-level PAGE data requires dbGaP phs000920. Confirm that the sumstat-only download is truly public (it should be, per Wojcik 2019 data availability statement), or flip to `dua_required = yes` and add a second dbGaP submission to the critical path.
7. **Build harmonization (b37 vs b38)** — Loh 2022 BMI and GBMI asthma are released on GRCh38; all other listed sources are GRCh37. Existing Phase 1 harmonization runs on b37. Either lift these two to b37 via CrossMap + HRC rsid remap (a Phase 1 sub-rule), or bump the whole pipeline to b38. Decision has downstream LD-panel implications (1KG Phase 3 b37 panels already landed per T1 production status). Recommend b38->b37 liftover for just these two sources to avoid full pipeline migration.

---

*End of SUMSTATS-UPGRADE amendment. Promotes to `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/amendments/SUMSTATS-UPGRADE.tsv` (data) and this file (rationale). Cross-reference OSF amendment when final trait lock is confirmed.*
