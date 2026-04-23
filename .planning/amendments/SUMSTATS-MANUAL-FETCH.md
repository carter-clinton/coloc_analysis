# Sumstats requiring manual fetch (not scripted in download_sumstats_v2.sh)

These sources require portal navigation, click-through ToS, Google Sheets manifest
inspection, or DUA submission. `bin/download_sumstats_v2.sh` does NOT attempt them.

Authoritative source-map: `.planning/amendments/SUMSTATS-UPGRADE.tsv`

## Portal-navigation (manual click-through, no DUA)

### 1. GIANT Yengo 2018 BMI (EUR)
- **Portal**: https://giant-consortium.web.broadinstitute.org/index.php/GIANT_consortium_data_files
- **Target file**: `Meta-analysis_Locke_et_al+UKBiobank_2018_UPDATED.txt.gz`
- **Destination**: `data/raw/sumstats_v2/GIANT2018/BMI/EUR/`
- **Steps**: open portal → navigate to "GIANT 2018 GWAS Meta-analysis Summary Statistics" → right-click direct link → save as. 15 seconds.

### 2. Loh 2022 BMI (EUR + AFR)
- **Portal**: https://www.nature.com/articles/s41467-022-35553-2
- **Target**: supplementary data + GWAS Catalog GCST90275125 (if applicable)
- **Destination**: `data/raw/sumstats_v2/Loh2022/BMI/{EUR,AFR}/`
- **Steps**: open Nature article → scroll to "Data availability" → click GWAS Catalog link → download EUR + AFR stratified files. Decision: Loh 2022 vs Yengo 2018 as primary BMI source — unresolved pending Carter's phenotype-lock confirmation.

### 3. PAGE BMI AFR (Wojcik 2019)
- **Portal**: https://www.ebi.ac.uk/gwas/publications/31217584
- **Target**: `PAGE_BMI_AFR_ALL_2019-06.tsv`
- **Destination**: `data/raw/sumstats_v2/PAGE2019/BMI/AFR/`
- **Steps**: open EBI GWAS Catalog publication → scroll to "Summary statistics" → download AFR-stratified file. Some PAGE sumstats require dbGaP DUA — verify before committing to this source.

### 4. DIAMANTE 2022 T2D (all ancestries)
- **Portal**: https://diagram-consortium.org/downloads.html
- **Target files**: `DIAMANTE-TA.sumstat.txt.gz`, `DIAMANTE-EUR.sumstat.txt.gz`, `DIAMANTE-EAS.sumstat.txt.gz`, `DIAMANTE-SAS.sumstat.txt.gz`
- **Destination**: `data/raw/sumstats_v2/DIAMANTE2022/T2D/{TRANS,EUR,EAS,SAS}/`
- **Steps**: open downloads page → ToS click-through → direct file links. ~5 min total.
- **Gated**: DIAMANTE-AFR and DIAMANTE-HIS NOT YET RELEASED (held until ancestry-stratified companion manuscripts publish). Quarterly recheck required.

### 5. GIGASTROKE 2022 (all ancestries)
- **Portal**: https://www.ebi.ac.uk/gwas/publications/36180795
- **Target**: per-ancestry `GCST90104539`…`GCST90104542` series (TRANS/EUR/AA/EAS/SAS)
- **Destination**: `data/raw/sumstats_v2/GIGASTROKE2022/stroke/{TRANS,EUR,AFR,EAS,SAS}/`
- **Steps**: open EBI GWAS Catalog publication page → per-accession navigation (5 per-ancestry accessions; ~15 min). JS-rendered, so curl can't fetch directly.

### 6. GBMI Asthma 2022 (multi + EUR + AFR)
- **Portal**: https://www.globalbiobankmeta.org/resources
- **Target files**: `Asthma_Bothsex_inv_var_meta_GBMI_052021.txt.gz` (multi), plus `_EUR_` and `_AFR_` stratified variants
- **Destination**: `data/raw/sumstats_v2/GBMI2022/asthma/{MULTI,EUR,AFR}/`
- **Steps**: portal → phenotype manifest (Google Sheets embedded) → per-ancestry direct download links. ~10 min.

### 7. MAGIC HbA1c (all ancestries)
- **Portal**: https://magicinvestigators.org/downloads/index.html
- **Target files**: `MAGIC1000G_HbA1c_TA.tsv.gz`, `_EUR.tsv.gz`, `_AA.tsv.gz`, `_EAS.tsv.gz`, `_SAS.tsv.gz`, `_HISP.tsv.gz`
- **Destination**: `data/raw/sumstats_v2/MAGIC2021/HbA1c/{TRANS,EUR,AFR,EAS,SAS,HIS}/`
- **Steps**: page listed 7 files. MAGIC uses FTP (port 21) for actual file serving per SUMSTATS-UPGRADE agent report — test FTP access from NCSU HPC first; if blocked, use HTTPS mirror if available or fall back to a different network.

## DUA-gated (human submission required)

### 8. MVP BP Giri 2019 AFR SBP
- **dbGaP accession**: phs001672
- **Portal**: https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs001672
- **Destination**: `data/raw/sumstats_v2/MVP2019/BP/AFR/`
- **Critical path**: DUA submission → NIH ERA Commons → study PI review → approximate 4–8 weeks
- **Status**: not initiated
- **Action item for Carter**: submit DUA via dbGaP. Research purpose text drafted in `.planning/amendments/AOU-LD-PIPELINE.md` can be adapted.

## Already downloaded (skip)

### 9. Evangelou 2018 BP (EUR SBP)
- **Status**: already_downloaded per SUMSTATS-UPGRADE.tsv
- **Local path**: existing pipeline at `data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz`
- **Note**: verify GRCh build (Evangelou 2018 is GRCh37)

---

## Integration back into pipeline

After each source lands in `data/raw/sumstats_v2/{source}/{trait}/{ancestry}/`:

1. Compute variant count + MAF histogram sanity check (logs/sumstats_v2/qc/{source}_{trait}_{ancestry}.qc.txt)
2. Harmonize to GRCh37 (liftover GRCh38 sources: Loh 2022, GBMI asthma)
3. Re-index tabix bgzip format per existing pipeline
4. Update Snakemake config to point at v2 sumstats
5. Re-run LDSC genetic-correlation matrix on upgraded sources (prerequisite for MTAG)
6. Post OSF amendment BEFORE MTAG+CPASSOC fires (see PROJECT-AMENDMENT-2026-04-22)

Track B milestone alignment:
- **M1** = sumstats upgrade + harmonization + AoU AFR LD bootstrap → this file closes when all 47 TSV rows resolve (downloaded or DUA-approved or explicitly deferred)
- **M2** = MTAG + CPASSOC discovery (pre-registered before firing)
- **M3** = programmatic region generation (PLINK clump union + MTAG/CPASSOC novel-signal loci)
