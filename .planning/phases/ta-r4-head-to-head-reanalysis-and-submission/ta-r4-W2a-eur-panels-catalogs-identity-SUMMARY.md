---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: W2a-eur-panels-catalogs-identity
subsystem: EUR LD substrate (1000G legacy + R4 panels, A2/k2d payloads, catalogs, trait manifest)
tags: [ta-r4, d-03, d-10, d-11, d-12a, d-25, d-01, d-14, panels, known-answer]
requires: [ta-r4-W1-e2-orientation-tdd]
provides:
  - src/python/ta_r4/fetch_verified.py (https-only verified download)
  - src/snakemake/rules/ta_r4_panels.smk (r4_catalog, r4_panel_eur_legacy, r4_panel_eur_1kg, r4_identity_payload, r4_k2d_payload, r4_w2a_all)
  - src/python/ta_r4/panel_manifest.py (manifest | known-answers)
  - data/r4/ld/{legacy_repro/EUR, EUR_1kg_r4, EUR_identity_r4, k2d_identity/{EUR,AFR}, variants_legacy, variants_r4}
  - manifests panels_legacy_repro / panels_EUR_1kg_r4 / panels_EUR_identity_r4 / panels_k2d_identity / catalogs_sha256
  - config/ta_r4/trait_manifest.tsv
affects: [W2b (AFR/UKB panels reuse panel_manifest.py + the rule pattern), W2c (trait_manifest UNRESOLVED hypertension sdY; panel review), W3a (repro_routeC / repro_k2d_routeC panels), W5a (A3_1kg / A2_identity panels + receipt md5 gate), pre-W4 SNP_ID decision (measured below)]
tech-stack:
  added: []
  patterns: [blockwise Rscript inspection, manifest keyed by (ancestry, region_safe), live gate + fake-root negative controls]
key-files:
  created:
    - src/python/ta_r4/fetch_verified.py
    - tests/ta_r4/test_fetch_verified.py
    - src/snakemake/rules/ta_r4_panels.smk
    - src/snakemake/scripts/ta_r4/make_k2d_payload.R
    - src/snakemake/scripts/ta_r4/measure_trait_facts.R
    - src/python/ta_r4/panel_manifest.py
    - tests/ta_r4/test_known_answer_panels.py
    - config/ta_r4/trait_manifest.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/{downloads_sha256,ref_1000G_EUR_plink_sha256,catalogs_sha256,panels_legacy_repro,panels_EUR_1kg_r4,panels_EUR_identity_r4,panels_k2d_identity}.tsv
  modified:
    - tests/ta_r4/test_qtl_orient.py (5 slow e2e tests marked r4_heavy per §C)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
    - .planning/ROADMAP.md
decisions:
  - "The previous executor's outputs were deleted and every panel/payload/catalog was rebuilt from scratch; the rebuild is byte-identical (135/135 md5)."
  - "plink runs with --threads 1 (legacy rule used 2): the LSF profile gives 1 slot; threads do not change --r square values (legacy and R4 matrices compare equal to 0)."
  - "Panel memory is 32,000 MB for windows >= 2 Mb (plan: 16,000 for > 8,000 variants). Variant counts are not known before plink runs; the window rule covers PYHIN1 (15,236)."
  - "The .ld text is deleted right after the .rds is written; its md5 and size are kept in work/<panel>/<region>.ld.md5 (the .ld files are hundreds of MB each)."
  - "SNP_ID remedy (pre-W4 decision) NOT chosen; measurement only."
metrics:
  duration: "~2h (2026-10-26 11:14-13:15 EDT) on top of the stopped executor's 2026-10-23 session; FULL 27m49s, HEAVY 10m39s"
  completed: 2026-10-26
  tasks: 4
  files: 8 created code/config + 7 manifests + 1 test modified + LOG/STATE/ROADMAP/SUMMARY
---

# Phase ta-r4 Plan W2a: EUR panels, catalogs, identity payloads Summary

W2a puts the EUR LD substrate on /rs1. It contains 10 legacy-identical 1000G EUR panels, 29 R4 panels (`--keep-allele-order`
+ REF/ALT), 29 matched A2 identity payloads, 24 k2d reproduction payloads and 43 variant catalogs. Every file is
md5/sha256-manifested and read-only, and a live known-answer gate passes all 181 checks. The legacy SH2B3 panel
reproduces the 2026-05 audit exactly: 895 variants, and the same eigen spectrum.

## Commits

| Task | Commit | Content |
|---|---|---|
| 1 | `f19d6398` | fetch_verified + tests; Zenodo tgz verified; 66 members extracted; EUR n = 489 (previous executor) |
| 2 | `8a5c75e2` | ta_r4_panels.smk, make_k2d_payload.R, catalogs_sha256.tsv; full rebuild |
| 3 | `b266e1d8` | panel_manifest.py, test_known_answer_panels.py, 4 panel manifests, trait_manifest.tsv, measure_trait_facts.R |
| 4 | wave-close commit | test_qtl_orient r4_heavy marks, LOG, STATE, ROADMAP, this SUMMARY |

## Resume handling

- Task 1 had been committed by the previous executor. I re-checked it today: `md5sum` gives `a7773ab485827b533cb300c76356d76b`, `stat` gives
  `288277344`, the 22 `.fam` rows have 1 distinct sha256, and `wc -l 1000G.EUR.QC.1.fam` = **489** (D-25: not 503).
  RED was re-derived: with `fetch_verified.py` moved aside, `1 error in 0.21s` (ImportError at collection). The HTML
  negative control (magic check disabled) gave `FAILED tests/ta_r4/test_fetch_verified.py::test_html_body_with_200_fails_magic`,
  `1 failed, 10 passed`. The file was restored (`cmp` identical) and the suite is back to 11 passed.
- The Tasks 2-3 WIP was read against the plan. It conformed, apart from the deviations listed below. The earlier fire had
  ended badly: the first run (2026-10-23 22:11) was terminated at 130/136, and a resume fire was killed with its jobs in flight.
  A stale `.snakemake/locks` (5 output paths, all W2a) blocked the dry-run. No Snakemake process or LSF job was alive,
  so I unlocked through `bin/r4_fire.sh ... --unlock`.
- **Every earlier output was deleted** (`EUR_1kg_r4 EUR_identity_r4 k2d_identity legacy_repro variants_legacy
  variants_r4 work`) and rebuilt. Afterwards all 135 files were byte-identical to the deleted build (md5 join: `same 135`).
- The trait facts were re-measured with the same script and inputs: the output is byte-identical to the WIP `trait_facts.tsv`.

## Task 2: panels built

Dry-run (`bash bin/r4_fire.sh repro repro_routeC r4_w2a_all -n`, first 40 lines; forbidden §B.7 substrings: 0 hits):

```
Using profile config/ta_r4/cluster_lsf for setting default command line arguments.
Config file config/pipeline.yaml is extended by additional config specified via the command line.
Building DAG of jobs...
Your conda installation is not configured to use strict channel priorities. ...
Job stats:
job                    count
-------------------  -------
r4_catalog                43
r4_identity_payload       29
r4_k2d_payload            24
r4_panel_eur_1kg          29
r4_panel_eur_legacy       10
r4_w2a_all                 1
total                    136

[Mon Oct 26 11:16:07 2026]
rule r4_panel_eur_1kg:
    input: data/r4/ref/1000G_EUR_Phase3_plink/1000G.EUR.QC.16.bed, ....16.bim, ....16.fam, src/snakemake/scripts/plink_ld_to_rds.R
    output: data/r4/ld/EUR_1kg_r4/NC_MC1R.rds
    jobid: 66
    reason: Missing output files: data/r4/ld/EUR_1kg_r4/NC_MC1R.rds
    wildcards: region=NC_MC1R
    resources: mem_mb=8000, mem_mib=7630, disk_mb=1000, disk_mib=954, tmpdir=<TBD>

[Mon Oct 26 11:16:07 2026]
rule r4_panel_eur_legacy:
    input: data/r4/ref/1000G_EUR_Phase3_plink/1000G.EUR.QC.19.bed, ....19.bim, ....19.fam, src/snakemake/scripts/plink_ld_to_rds.R
    output: data/r4/ld/legacy_repro/EUR/APOE_19q13.rds
    jobid: 52
    reason: Missing output files: data/r4/ld/legacy_repro/EUR/APOE_19q13.rds
    wildcards: region=APOE_19q13
    resources: mem_mb=32000, mem_mib=30518, disk_mb=1000, disk_mib=954, tmpdir=<TBD>

[Mon Oct 26 11:16:07 2026]
rule r4_catalog:
    input: data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz, data/processed/sumstats_harmonized/t2d.EUR.tsv.bgz, ...
    output: data/r4/ld/variants_r4/NC_NULL_06.tsv
```

- Fire 1: 124/136 steps. 7 LSF jobs exited before their script ran (`Cannot open your job file: /home/ckclinto/.lsbatch/...`
  on c018n02 / c014n04 / c002n01). Because no `.jobfailed` marker was written, Snakemake waited indefinitely. I stopped it
  (TERM, then KILL; no LSF jobs were alive), unlocked, and checked with a dry-run: 12 steps remained, all "Missing output". Fire 2 finished
  `12 of 12 steps (100%) done`. The final dry-run reports `Nothing to be done`.
- Counts: `ls | wc -l` gives EUR_1kg_r4 **29**, EUR_identity_r4 **29**, legacy_repro/EUR **10**, variants_legacy 12, variants_r4 31,
  k2d EUR 12 + AFR 12 = **24**. These equal the distinct (ancestry, region) pairs in IDENTITY-LD-K2D-FIT-SUMMARY.tsv
  (95 rows, 24 distinct pairs: EUR 12, AFR 12). Catalogs: `catalogs_sha256.tsv` has **43** rows (legacy 12 + r4 31).
  Total 29 + 29 + 10 + 24 + 43 = 135 files (+ r4_w2a_all = 136 steps).
- `data/processed/ld_reference` does not exist (it was purged earlier), so `find ... -newer data/r4/ld/variants_legacy | wc -l` = 0.
- Work dirs keep `.bim/.log/.nosex/.snplist` plus `.ld.md5` (29 each for R4); there are 0 `.ld` files left.

### Variant-ID format (for the open pre-W4 decision; measured, not acted on)

| set | rows | rsid (`^rs[0-9]+$`) | chr:pos | other |
|---|---|---|---|---|
| EUR_1kg_r4 panels (29) | 86,035 | 86,035 | 0 | 0 |
| legacy_repro/EUR panels (10) | 68,214 | 68,214 | 0 | 0 |
| asthma.EUR sumstats, 10 admissible regions | 187,237 | 154,746 | 0 | 32,491 (empty SNP_ID) |
| hypertension.EUR | 47,442 | 0 | 47,442 | 0 |
| stroke.EUR | 50,387 | 0 | 50,387 | 0 |
| t2d.EUR | 167,314 | 0 | 167,314 | 0 |
| bmi.EUR (R4 restored) | 15,449 | 15,449 | 0 | 0 |
| asthma.AFR | 133,918 | 110,447 | 0 | 23,471 (empty) |
| stroke.AFR | 37,655 | 0 | 37,655 | 0 |
| t2d.AFR | 133,497 | 0 | 133,497 | 0 |

The 1000G panels carry **rsids only**. hypertension, stroke and t2d (EUR, plus stroke/t2d AFR) carry **chr:pos only**.
Those fits will therefore have the "override" shape that W0d measured, and the R4 coloc script refuses that shape with
UNMAPPED_FIT_NAMES. The row counts equal `trait_facts.tsv` n_rows. run_susie_rss.R and run_coloc_susie.R were not touched.

### Legacy vs R4 orientation

A1 in the legacy `.bim` and the R4 `.bim` agrees for all 68,214 variants in the 10 shared regions (0 differ; 0 ID mismatches).
The LDSC 1000G `.bim` already has A1 as plink's minor allele, so `--keep-allele-order` recodes nothing. The R4 and
legacy matrices are **equal including sign** (SH2B3 signed max |diff| = 0; `abs_r_equal` 0.000e+00 in all 10 regions).
In the R4 panels, REF/ALT := A2/A1 of this `.bim` (the W1 design). That gives the minor allele as ALT, not the genome
reference allele; the allele-aware join handles either.

## Task 3: manifests, live gate, trait manifest

- RED: with `panel_manifest.py` moved to scratch, `ImportError: cannot import name 'panel_manifest' from 'ta_r4'`,
  `1 error in 0.33s`. After restoring it (sha256 OK), the unit tests ran `6 passed, 2 deselected`.
- Sabotage controls (each restored, `cmp` identical):
  symmetry check off → `FAILED test_bad_matrix_refused[R[1,2] <- 0.3-symmetric]`;
  duplicate check off → `FAILED test_duplicate_key_refused`;
  identity_exact forced true → `FAILED test_manifest_rows`;
  md5 read from manifest → `FAILED test_md5_check_sees_a_corrupted_byte` (each `1 failed, 5 passed`).
- Manifests (bsub, 167 s, 4 GB max): legacy **10**, EUR_1kg_r4 **29**, EUR_identity_r4 **29**, k2d **24** (12 EUR + 12 AFR).
  Every matrix has max asymmetry 0.000e+00 and max |diag - 1| 0.000e+00, and is all-finite. Identity payloads: identity_exact true 29/29.
  k2d r_kind null 24/24. has_ref_alt is true for R4 / identity / k2d and false for legacy. n_samples = 489 for 1kg, NA otherwise.
  Sum n_var: R4 86,035 = identity 86,035; legacy 68,214; k2d 1,632,026 = 2 × 816,013.
- `chmod a-w` on all 92 .rds files; `stat -c %A data/r4/ld/EUR_1kg_r4/SH2B3_12q24.rds` → `-r--r-----`; 0 writable .rds.
- Live gate (bsub, 3 GB): `8 passed in 147.08s` (0 skips). `data/r4/findings/panel_known_answers.tsv`: 181 rows =
  md5 92 (10 + 29 + 29 + 24) + n_var_equal 10 + abs_r_equal 10 + identity_variants_identical 29 + has_ref_alt 39 (29 + 10)
  + sh2b3_legacy_n_var 1, **all PASS, 0 FINDING**:

```
check               ancestry  region_safe       expected  observed   status
n_var_equal         EUR       9p21_CDKN2A       7576      7576       PASS
n_var_equal         EUR       APOE_19q13        7734      7734       PASS
n_var_equal         EUR       APOL1_22q12       1335      1335       PASS
n_var_equal         EUR       BMI_5q13_3        14025     14025      PASS
n_var_equal         EUR       CXADR_F2RL1_6p21  6113      6113       PASS
n_var_equal         EUR       FTO_16q12         2404      2404       PASS
n_var_equal         EUR       MC4R_18q21        2229      2229       PASS
n_var_equal         EUR       PYHIN1_1q23       15236     15236      PASS
n_var_equal         EUR       SH2B3_12q24       895       895        PASS
n_var_equal         EUR       SLC2A9_urate      10667     10667      PASS
abs_r_equal         (all 10)                    <=1e-12   0.000e+00  PASS
sh2b3_legacy_n_var  EUR       SH2B3_12q24       895       895        PASS
(md5 92 / identity_variants_identical 29 / has_ref_alt 39: all PASS)
```

- Live-gate negative controls (fake root with edited manifest copies; real panels; 181 checks each):
  legacy SH2B3 row pointed at the R4 panel → `has_ref_alt SH2B3_12q24 false true FAIL` (n_var/|R| pass, since the matrices are equal);
  identity MC4R row → FTO payload → `identity_variants_identical MC4R_18q21 true false FAIL`;
  legacy MC4R row → FTO legacy panel → `n_var_equal MC4R_18q21 2404 2229 FAIL` + `abs_r_equal NA FAIL`;
  SH2B3 n_var recorded 894 → `sh2b3_legacy_n_var 895 894 FINDING` (not FAIL, §B.10). The committed test
  `test_live_md5_negative_control` corrupts one byte in a copy of SH2B3 and passes because md5_mismatches returns `['SH2B3_12q24']`.
- SH2B3 beyond n_var: the reproduced legacy panel has 210 negative eigenvalues, 81 below -1e-6, effective rank 451, min -1.2566e-05,
  max 1.8427e+02, condition number 1.466e+07 and 0 below -1e-3. All are identical to ta-sh2b3-W1.5-ld-audit.md §2.
- Trait manifest: 8 rows, 8 columns.
  - `hypertension.EUR` is **SBP, continuous** (sha256 a740bb26… equals the `sbp.EUR.Evangelou-ICBP-UKBB.2018` harmonized file;
    trait_inventory phenotype_lock "SBP continuous (mmHg), medication-adjusted"). Its type is quant, and its **sdY is UNRESOLVED**
    (the mmHg SD is not documented in the repo; sdY.est median 10.72) → W2c.
  - BMI: quant, sdY = 1 (trait_inventory "continuous BMI inverse-rank-normal"; sdY.est median 1.012).
  - The other six (asthma/stroke/t2d × EUR/AFR) are cc.
  - Recorded in evidence: stroke.EUR is METASTROKE (Traylor 2012) with a constant N 75000, and its sha256 ≠ the GIGASTROKE EUR inventory entry.
    stroke.AFR sha256 ≠ the GIGASTROKE AFR inventory entry (I added this). t2d.AFR N is a fractional Neff (T2DGGI AFA).
  - A spot check found a stale-mtime `.tbi` warning on t2d.AFR / asthma.EUR. For t2d.AFR at SH2B3, tabix and a full zcat scan agree (3269 = 3269).

## Task 4: wave close

- QUICK first run `304 passed, 41 deselected in 125.73s` (over the 120 s budget). The 5 slowest are test_qtl_orient e2e
  (~12.5 s each). Per §C they are marked `r4_heavy` → `299 passed, 46 deselected in 73.12s`.
- HEAVY `42 passed, 4 skipped` (10m39s). 42 = W1's 35 + 2 live known-answer + 5 moved. The skips are the W5a/W5b live gates.
- Freeze pins `39 passed`.
- FULL `1769 passed, 50 skipped` (27m49s; junit `data/r4/logs/full_W2a.xml`). Joined BY NAME against `full_W1.xml`:
  common 1800, removed 0, changed 0, added 19 (fetch_verified 11, known_answer_panels 8; all passed);
  1800 + 19 = 1819, 1750 + 19 = 1769, 50 + 0 = 50. tests/m3 1299 (1265/34), phase1 38 (27/11), phase2 137 (136/1), 0 changed.
- sparse_parent_benchmark.tsv was restored (clean). Frozen files are 0-diff: run_susie_rss.R, run_coloc_susie.R, Snakefile, pipeline.yaml,
  finemap.smk, envs/r_coloc.yml, Snakefile.ta_r4.
- Shared conda cache `/rs1/.../conda_pkgs` before: 2188 entries / listing sha256 f094b37d…9085 / 23348 MB / 0 archives.
  After: 2188 / f094b37d…9085 / 0 archives / 0 entries newer than the session start. R4 pkgs 1095 → 1095 (no env solve was needed).

## Deviations from Plan

1. **[Rule 3] Stale Snakemake lock** from the killed resume fire. Its content was verified as W2a paths only and no process was alive; I unlocked via r4_fire.sh.
2. **[Rule 3] LSF pre-script failures hang Snakemake** (7 jobs, "Cannot open your job file"). I stopped the fire and re-fired the 12 missing
   steps. No profile change was made: a `--cluster-status` script would be new infrastructure, so it is recorded here for W2b/W5.
3. **plink `--threads 1`** instead of the legacy 2 (1-slot serial queue). Values are unaffected (legacy == R4 to 0).
4. **mem_mb by window width** (32,000 for ≥ 2 Mb) instead of 16,000 for > 8,000 variants.
5. **`.ld` deleted before the manifest row** (its md5 + size go to `.ld.md5` first); the plan's ordering would keep ~GBs of text.
6. **test_qtl_orient.py**: 5 e2e tests marked r4_heavy (§C budget rule; the file is outside files_modified).
7. Added a stroke.AFR sha-mismatch note to the trait-manifest evidence.

## Known Stubs

None. The `UNRESOLVED` sdY for hypertension.EUR is deliberate (D-25) and goes to Carter at W2c (signoff W2c-T4).

## Threat Flags

None. There are no new network endpoints beyond the plan's Zenodo download, and no writes outside data/r4.

## Self-Check: PASSED
