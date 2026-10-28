# ta-r4 W2 review packet (W2c-T4)

Date: 2026-10-28. Branch `m3-W2-aou-deltas`. `$MAN` = `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests`.
Each table lists the command that produced it. The full command outputs are in `ta-r4-LOG.md` (2026-10-28 W2c entry).

## 1. Measured EUR n vs the draft

| source | EUR n |
|---|---|
| `data/r4/ref/1000G_EUR_Phase3_plink/*.fam` (22 files, each 489 lines; 489 distinct FID IID) | **489** |
| `$MAN/panels_EUR_1kg_r4.tsv` n_samples (29/29 rows) | 489 |
| draft `docs/manuscript/id-vs-ref-LD.md` lines 72, 78, 372 | 503 |

AFR: 661 = 504 + ASW 61 + ACB 96 (`$MAN/afr_samples_sha256.tsv`). The draft's AFR figure is also 661.

`wc -l < .fam` ×22; `cut -d' ' -f1-2 *.fam | sort -u | wc -l`; `grep -n 503 docs/manuscript/id-vs-ref-LD.md`

## 2. Panels: count and n_var range per class; SH2B3

| class | panels | n_var min | n_var max | n_samples |
|---|---|---|---|---|
| EUR_1kg_r4 | 29 | 228 | 15,236 | 489 |
| EUR_identity_r4 | 29 | 228 | 15,236 | NA |
| legacy_repro (EUR) | 10 | 895 | 15,236 | 489 |
| k2d_identity | 24 | 10,992 | 321,083 | NA |
| legacy_repro_AFR (12/12 use_identity placeholders) | 12 | 10,992 | 321,083 | NA |
| AFR661_1kg_r4 | 10 | 1,875 | 21,323 | 661 |
| AFR661_identity_r4 | 10 | 1,875 | 21,323 | NA |
| AFR504_1kg_r4 | 10 | 1,887 | 21,154 | 504 |
| EUR_ukb337k_r4 (native) | 30 | 364 | 34,361 | NA |
| EUR_ukb337k_isect_r4 | 29 | 195 | 12,746 | NA |
| EUR_1kg_isect_r4 | 29 | 195 | 12,746 | 489 |

SH2B3_12q24 n_var: legacy 895, R4 895, expected 895 → `n_var_equal 895 895 PASS`, `abs_r_equal 0.000e+00 PASS`.
Known-answer checks overall: 181 PASS, 0 FAIL, 0 FINDING (`data/r4/findings/panel_known_answers.tsv`).

`awk` over `$MAN/panels_*.tsv` columns n_var / n_samples; `grep SH2B3_12q24 data/r4/findings/panel_known_answers.tsv`

## 3. BMI allele restoration (D-18)

| class | rows |
|---|---|
| frozen bmi.EUR rows | 2,336,269 |
| exact | 2,327,244 |
| flipped | 0 |
| value_mismatch | 0 |
| unjoined (dropped; all A/T 3,844 or C/G 5,181) | 9,025 |
| kept | 2,327,244 |
| sign-uninformative (BETA 0.0, kept as exact) | 23,896 |
| raw cross-check: Tested_Allele == ALT | 10,000 / 10,000 = 1.000000 |

2,327,244 + 0 + 0 + 9,025 = 2,336,269. Source: `$MAN/bmi_allele_restoration_report.tsv`.

## 4. Trait manifest: open items

`config/ta_r4/trait_manifest.tsv` has 8 rows. UNRESOLVED cells: `hypertension.EUR.sdY` and its `sdY_source` (one decision).

**Q4a. hypertension.EUR sdY.** Evidence:

| fact | value | source |
|---|---|---|
| file | Evangelou 2018 UKB+ICBP **SBP** (continuous; not binary hypertension); `type` = quant | trait_manifest evidence; trait_inventory phenotype_lock "SBP continuous (mmHg), medication-adjusted" |
| effect units | mmHg per allele, untransformed SBP (+15 mmHg if on BP medication) | Evangelou 2018 Online Methods (PMC6284793): "three (untransformed) continuous, medication-adjusted BP traits" |
| SBP SD, UK Biobank + BiLEVE | 20.7 mmHg (N 458,575); UKB 20.6; BiLEVE 20.8 | Evangelou 2018 Supp. Table 1a, `data/r4/downloads/evangelou2018_supp/41588_2018_205_MOESM3_ESM.xlsx` (sha256 a24bdb44…) |
| SBP SD, ICBP cohorts | vary by cohort (e.g. AGES 20.26, ARIC 16.70) | Supp. Table 1b |
| `coloc:::sdY.est` median over the 10 regions | 10.72 | `data/r4/findings/trait_facts.tsv` |
| N range in the file | 662,274 – 757,601 | trait_facts.tsv |

Reply key `trait.hypertension.EUR.sdY`: a number (the SD in mmHg units to use).

**Q4b. stroke.AFR source (evidence only; no reply key).** The R4 input `stroke.AFR.tsv.bgz` is GCST90104553, not the GIGASTROKE all-stroke file that `config/trait_inventory.yaml` lists.

| fact | GCST90104553 (in use) | GCST90104549 (inventory entry) |
|---|---|---|
| GWAS Catalog trait (meta.yaml) | **Small vessel stroke** (EFO_1001504) | **Stroke** (EFO_0000712) |
| ancestry | African American | African American |
| sample_size (meta.yaml) | 20,453 | 23,991 (inventory: 3,961 cases / 20,030 controls) |
| N in the file in use | 20,271 (constant) | — |
| local md5 = published md5 | c63fdaba… = c63fdaba… | 15d6213c… = 15d6213c… |
| sha256 raw | — | 220d2610… = inventory sha256_raw |
| derivation | stroke.AFR.tsv.bgz rows 5,259,724 = raw rows; BETA/SE/P/EAF equal on all 5,259,724; 0 flipped | inventory harmonized file present, sha256 3c58b250… = inventory sha256_harmonized |

datasets.yaml `megastroke_metastroke` AFR → `GCST90104553_buildGRCh37.tsv.gz`. stroke.EUR is METASTROKE (Traylor 2012), N 75,000.
A valid sign-off without a remark keeps stroke.AFR as recorded. To change it, raise it instead of signing.

## 5. AFR panel size (> 16,000 = finemap susie_max_variants)

| panel | region | n_var |
|---|---|---|
| AFR661_1kg_r4 | BMI_5q13_3 | 21,323 |
| AFR661_1kg_r4 | PYHIN1_1q23 | 20,818 |
| AFR504_1kg_r4 | BMI_5q13_3 | 21,154 |
| AFR504_1kg_r4 | PYHIN1_1q23 | 20,686 |

A fit whose sumstats-panel overlap also exceeds 16,000 reports `too_many_variants`. Source: `data/r4/findings/afr_panel_size.tsv`.

## 6. UKB-native panel size; decision `ukb_native`

Native panels above 16,000 (`data/r4/findings/ukb_native_panel_size.tsv`):

| region | n_var | tiles | zero-filled pairs |
|---|---|---|---|
| HLA_6p21 (exploratory) | **34,361** | 3 (28–33 Mb hole: 7 tile .npz 404) | 293,039,198 |
| PYHIN1_1q23 | 26,050 | 3 | 45,317,232 |
| BMI_5q13_3 | 24,121 | 3 | 36,769,777 |
| SLC2A9_urate | 16,752 | 1 | 0 |

The other 26 native panels are 364–13,647. Isect panels: 29, max 12,746.
Under `native`, the HLA_6p21 A3_ukb exploratory fits report `too_many_variants` (n_var 34,361 > 16,000). The HM3 count is not measured. W2d would build it, and only under `hm3` would it be known whether HLA gets under the cap. This is decided once, here (not at W4a).

Reply key `ukb_native`: `native` (keep as built) or `hm3` (pre-register the HM3 restriction; W2d builds `EUR_ukb337k_hm3_r4` before the lock).

## 7. QTL scope vs the frozen layer

| dimension | frozen layer (re-derived) | R4 `config/ta_r4/qtl_manifest.tsv` |
|---|---|---|
| tuples | 1,274 (= TRACK-A-FROZEN-NUMBERS.md 1,274) | 23,310 features × 5 traits = 116,550 rows |
| ancestry | EUR | EUR |
| sources | gtex_eqtl + gtex_sqtl | eqtl + sqtl (same files: eQTL `.all`, sQTL `.cc`) |
| tissues | 49 | 49 |
| regions | 10 (incl. HLA_6p21; excl. BMI_5q13.3) | 10 admissible (incl. BMI_5q13_3; excl. HLA_6p21, D-24) |
| features | 13 curated genes | every molecular_trait_id with ≥ 1 row in the window |
| traits | first trait per region only | all 5 EUR traits |

Frozen-layer re-derivation: legacy `build_manifest` with sources gtex_eqtl+gtex_sqtl and the 49-tissue fallback lookup → 1,274 rows. The result files `results/qtl_coloc/` are gone, so this rebuild is the only check.

**FINDING (narrower than frozen).** 412 of the 1,274 frozen tuples have an R4 counterpart (same region, gene, source, tissue). 862 do not:
- HLA_6p21: 98 (inadmissible, D-24).
- The legacy map sends "SLC2A9" to ENSG00000109107. That ID has no row in any R4 window (98 tuples). The SLC2A9_urate window has ENSG00000109667 in 55 source-tissue cells.
- Gene ID with no row in its region's window, in any tissue:
  - CXADR ENSG00000154639 (98) and F2RL1 ENSG00000164251 (98), both in CXADR_F2RL1_6p21. ENSG00000164251 does appear in the BMI_5q13_3 window.
  - MC4R ENSG00000166603 (98).
- Gene present, but no row for that source/tissue: 372 (sQTL 359, eQTL 13).
- 98 × 5 + 372 = 862. Covered tuples: 379 eQTL + 33 sQTL = 412.

The sQTL `.cc` file is a subset. For eQTL QTD000116, `.cc` is 1,006,411,891 B vs `.all` 3,805,150,286 B. The eQTL Catalogue filter definition is UNVERIFIED. sQTL: 2,161 features, 10,805 rows.
`tissues_frozen` = all 49 tissues (`src/python/build_tissue_n_lookup.py:25 GTEX_V8_TISSUE_N_FALLBACK`). So `tissues_frozen` ≡ `full` and `tissues_frozen+eqtl_only` ≡ `eqtl_only`, byte-identical (sha256 0f10d922… and fce5f86b…).

## 8. QTL size and cost per scope; decision `qtl_scope`

`$MAN/qtl_compute_estimate.tsv` (rows × 3 QTL arms × t_row; storage = rows × 3 × 1,355 B):

| scope | n_rows | n_groups (per arm) | est core-hours | est storage GB |
|---|---|---|---|---|
| full | 116,550 | 899 | 232.8 | 0.474 |
| tissues_frozen | 116,550 | 899 | 232.8 | 0.474 |
| eqtl_only | 105,745 | 490 | 211.2 | 0.430 |
| tissues_frozen+eqtl_only | 105,745 | 490 | 211.2 | 0.430 |

t_row = 2.397 s is a **fixture lower bound, UNMEASURED on real data**. It is the median of 15 `run_qtl_coloc.R` calls on the 200-variant test_qtl_orient fixture (LSF 429976). No legacy QTL LSF logs survive. Real regions have up to 15,236 panel variants, so real cost is expected to be higher by an unmeasured factor.
Downloads: 98 files (49 tissues × 2), 180G on /rs1, all gzip_ok/tabix_ok. No published checksum exists, so files are verified by HEAD Content-Length plus sha256.

Reply key `qtl_scope`: `full` | `tissues_frozen` | `eqtl_only` | `tissues_frozen+eqtl_only`. W2d rebuilds the manifest before the lock if not `full`.

## 9. Reply format (exact)

The first line is exactly the token, dated on or after 2026-10-28. Then one line per key, and nothing else is required:

```
carter-approved YYYY-MM-DD
ukb_native: <native|hm3>
qtl_scope: <full|tissues_frozen|eqtl_only|tissues_frozen+eqtl_only>
trait.hypertension.EUR.sdY: <number>
```

Any other reply, including "approved", is WAIT and records nothing. To raise an issue instead (for example §4b or the §7 FINDING), describe it. That is also WAIT.
