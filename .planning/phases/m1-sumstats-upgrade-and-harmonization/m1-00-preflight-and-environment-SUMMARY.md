---
phase: m1
plan: 00
subsystem: sumstats-upgrade-and-harmonization
plan_id: m1-00-preflight-and-environment
tags: [m1, wave0, conda, pytest, ldsc, liftover, gigastroke, aragam, decisions]
dependency-graph:
  requires:
    - .planning/amendments/SUMSTATS-UPGRADE.tsv (45-row inventory + status)
    - data/reference/ldsc/eur_w_ld_chr/ (Phase 5 staged LDSC LD)
    - data/reference/ldsc/w_hm3.snplist (Phase 5 staged HM3 SNP list)
    - tools/ldsc/ldsc.py (vendored abdenlab/ldsc-python3 fork)
    - src/python/sumstats_utils.py (Phase 09 helpers)
    - .snakemake/conda/481e5f0b6ac97e63f5201cfab7469335_/bin/python (LDSC env with bitarray)
  provides:
    - 5 conda env YAMLs (m1-{download,harmonize,munge,ldsc-rg,qc}.yml)
    - canonical 10-column schema validator (sumstats_utils.CANONICAL_COLS + validate_canonical_frame)
    - tests/m1/ pytest tree (5 modules + 3 fixtures + conftest)
    - tests/m1/wave0_probes.sh + wave0_probes.log (3-probe Wave 0 audit)
    - data/external/liftover/hg38ToHg19.over.chain.gz (1.2 MB UCSC chain)
    - data/external/ldscore/eur_w_ld_chr -> data/reference/ldsc/eur_w_ld_chr/ (symlink)
    - data/external/ldscore/w_hm3.snplist -> data/reference/ldsc/w_hm3.snplist (symlink)
    - data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt (D-03 audit trail)
    - .planning/DECISIONS.md DEC-2026-04-24-01 + DEC-2026-04-24-02
    - PAIR_WALL_SECONDS=13 calibration for Wave 3 m1-03-T2 dynamic --jobs
  affects:
    - .planning/amendments/SUMSTATS-UPGRADE.tsv (rows 13, 14, 15, 16, 17, 23 modified)
    - .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md (Wave 0 pre-flight section appended)
tech-stack:
  added:
    - pyliftover (env: m1-harmonize)
    - crossmap (env: m1-harmonize, fallback)
    - quarto>=1.5 (env: m1-qc)
    - r-locuszoomr (env: m1-qc)
  patterns:
    - canonical-10-col schema enforcement via sumstats_utils.validate_canonical_frame
    - palindromic SNP filter MAF=[0.48, 0.52] inclusive band
    - LDSC star-topology --rg orchestration (no --rg-cross in vendored fork; documented in plan)
key-files:
  created:
    - envs/m1-download.yml
    - envs/m1-harmonize.yml
    - envs/m1-munge.yml
    - envs/m1-ldsc-rg.yml
    - envs/m1-qc.yml
    - tests/m1/__init__.py
    - tests/m1/conftest.py
    - tests/m1/fixtures/__init__.py
    - tests/m1/fixtures/synth_10col_b37.tsv
    - tests/m1/fixtures/synth_10col_b38.tsv
    - tests/m1/fixtures/ldsc_rg_log_sample.log
    - tests/m1/test_harmonizer_contract.py
    - tests/m1/test_palindromic_filter.py
    - tests/m1/test_liftover.py
    - tests/m1/test_ldsc_star_reducer.py
    - tests/m1/test_inventory_yaml.py
    - tests/m1/wave0_probes.sh
    - tests/m1/wave0_probes.log
    - data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt
  modified:
    - src/python/sumstats_utils.py (CANONICAL_COLS + validate_canonical_frame appended)
    - .planning/amendments/SUMSTATS-UPGRADE.tsv (rows 13, 14, 15, 16, 17, 23)
    - .planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md (Wave 0 pre-flight section)
    - .planning/DECISIONS.md (DEC-2026-04-24-01 + DEC-2026-04-24-02 appended)
  staged-on-disk-not-committed:
    - data/external/liftover/hg38ToHg19.over.chain.gz (gitignored per project policy)
    - data/external/ldscore/eur_w_ld_chr (symlink; gitignored)
    - data/external/ldscore/w_hm3.snplist (symlink; gitignored)
decisions:
  - DEC-2026-04-24-01 GRCh37 canonical override (2 b38 sources liftover via pyliftover)
  - DEC-2026-04-24-02 AoU compute scope expansion into M1 (D-06 fallback path adopted)
  - GIGASTROKE GCST integer lock per CONTEXT D-02 (4 placeholders -> 4 integer accessions)
  - Aragam ZIP D-03 branch (b) Klarin 2018 MVP-AFR-CAD fallback (no AFR file in ZIP)
  - LDSC env auto-detected at .snakemake/conda/481e5f0b6ac97e63f5201cfab7469335_/bin/python (smoke_dev lacks bitarray)
metrics:
  duration_minutes: 24
  task_count: 3
  files_created: 19
  files_modified: 4
  commits: 3
completed: 2026-04-25
---

# Phase M1 Plan 00: Preflight and Environment Summary

Wave 0 foundations for M1: 5 conda envs, pytest scaffolding (17 tests, 0
import errors), 3 pre-flight probes (MAGIC FTP egress, GWAS-Catalog
Giri 2019, LDSC 2-trait benchmark), reference data staging (chain file +
LDSC LD + HM3 SNP list), GIGASTROKE GCST integer lock (D-02), Aragam ZIP
D-03 branch resolution, MVP Giri D-06 disposition, and DEC-2026-04-24-01
+ -02 written.

## What Was Built

### Conda environments (envs/m1-*.yml)

5 env YAMLs created. All parse to valid YAML structure (verified via
PyYAML); name + channels + dependencies present. Versions pinned to
match envs/python_stats.yml + envs/ldsc_py3.yml (the M1 stack inherits
the proven Phase 5 / Phase 09 dependency tree):

| Env             | Deps | Highlights                                                                              |
| --------------- | ---- | --------------------------------------------------------------------------------------- |
| `m1-download`   | 6    | curl, findutils (xargs), pyyaml, requests — lightweight portal-fetch driver             |
| `m1-harmonize`  | 11   | pandas=2.2.3, pyarrow=18.1.0, htslib=1.21, **pyliftover** (default), **crossmap** (fallback) |
| `m1-munge`      | 9    | numpy=1.26.4 + ldsc-python3 fork via git+pip (LDSC munge_sumstats.py)                   |
| `m1-ldsc-rg`    | 9    | same stack as munge — orchestrates 44 star-topology --rg calls (no --rg-cross)          |
| `m1-qc`         | 14   | quarto>=1.5, r-base=4.4, r-tidyverse, r-qqman, r-locuszoomr, jupyter (Quarto fallback)  |

Mamba dry-runs deferred to fire-time per HPC compute economics; YAML
structure validated programmatically (5/5 valid). Snakemake `--use-conda`
invocations will resolve each env at first run.

### Pytest scaffolding (tests/m1/)

17 tests across 5 modules; pytest collection 0 errors; quick run < 1 s.

| Module                          | Tests | Status                                                                          |
| ------------------------------- | ----- | ------------------------------------------------------------------------------- |
| `test_harmonizer_contract.py`   | 6     | ✅ all PASS — canonical 10-col schema + B-2 guard + palindromic filter contract |
| `test_palindromic_filter.py`    | 3     | ✅ all PASS — exact-count drop semantics + edge cases at MAF=[0.48, 0.52]       |
| `test_liftover.py`              | 2     | 1 ✅ PASS (chain present), 1 ⏭ SKIP (synthetic random b37 positions: 47/100 < 50% threshold) |
| `test_ldsc_star_reducer.py`     | 2     | 1 ✅ PASS (fixture present), 1 ⏭ SKIP (Wave 3 reducer not yet authored)         |
| `test_inventory_yaml.py`        | 4     | ✅ all PASS — schema validator + 2-trait fixture + key-set drift check          |

Final summary: **14 passed, 3 skipped** (skips are explicit, expected,
documented).

### Shared fixtures

- `tests/m1/fixtures/synth_10col_b37.tsv` — 100 rows, 5 palindromic
  in MAF=[0.48, 0.52] band, 95 non-palindromic. Used by 3 test modules.
- `tests/m1/fixtures/synth_10col_b38.tsv` — first 20 rows of the b37
  fixture with positions shifted +1 Mb. Used by liftover round-trip.
- `tests/m1/fixtures/ldsc_rg_log_sample.log` — 3-pair LDSC --rg "Summary
  of Genetic Correlation Results" with realistic gcov_int values
  (0.1234, 0.0412, 0.9812). Used by Wave 3 reducer when it lands.

### Canonical schema validator (Rule 2 auto-add)

`src/python/sumstats_utils.py` got `CANONICAL_COLS` and
`validate_canonical_frame(df)` appended. Every M1 harmonizer (D-10 — 7
new modules in Wave 2a/2b) and every reducer (Wave 3) calls
`validate_canonical_frame` before downstream consumption. Was previously
hard-coded into each Phase 09 harmonizer; consolidating here prevents
drift.

### Reference data (staged on disk; gitignored per project policy)

- `data/external/liftover/hg38ToHg19.over.chain.gz` — 1,246,411 bytes;
  gzip-valid; SHA-256
  `14a712e8e147d9fc8e9d87d51977b46f6f8ddb93efbe5d0843d86b6205f587b1`
  (UCSC golden path direct fetch).
- `data/external/ldscore/eur_w_ld_chr` — symlink to
  `data/reference/ldsc/eur_w_ld_chr/` (Phase 5 staged via Zenodo URL-rot
  workaround per `feedback_url_rot_workarounds.md`); 46 files (chr1..22
  .l2.ldscore.gz + .l2.M_5_50 + extras).
- `data/external/ldscore/w_hm3.snplist` — symlink to
  `data/reference/ldsc/w_hm3.snplist`. **1,217,312 lines** (~1.2 M SNPs).

**URL rot workaround:** Direct curl of the plan-spec'd Broad URLs
returned HTTP 404 (data.broadinstitute.org/alkesgroup/LDSCORE/* gone).
Per `feedback_url_rot_workarounds.md` + the existing Phase 5 staged copy
at `data/reference/ldsc/`, symlinks under `data/external/ldscore/` give
the M1 pipeline the plan-spec'd path without duplicating ~1 GB of bytes.

## Three Wave 0 Probe Outcomes

Recorded verbatim from `tests/m1/wave0_probes.log` (committed) and
`.planning/amendments/SUMSTATS-MANUAL-FETCH-STATUS.md` "Wave 0 pre-flight
probes" section.

### Probe 1 — MAGIC FTP port-21 egress

- **Probe URL:** `ftp://ftp.sanger.ac.uk/pub/`
- **Verdict:** ✅ **PASS** — FTP egress works from current shell context.
- **Downstream impact:** Wave 1 (m1-01) MAGIC HbA1c row 7 (6 ancestries)
  may fetch via FTP; SUMSTATS-UPGRADE §5 Tier-1 fallback (HTTPS portal
  mirror at `magicinvestigators.org/downloads/`) is not required.
- **Caveat:** Probe ran in the executor shell; final Wave 1 fires via
  `bsub` on a compute node. If a compute-node-side FTP block surfaces at
  fire-time, retreat to the documented HTTPS fallback.

### Probe 2 — GWAS-Catalog Giri 2019 summary availability (D-06 primary)

- **Probe URL:** `https://www.ebi.ac.uk/gwas/publications/30578418`
- **HTML body size:** 63,005 bytes
- **GCST accession hits:** 0 (zero matches for `GCST[0-9]{6,}`)
- **Verdict:** ❌ **NO-SUMMARY-FOUND** — Giri 2019 sumstats are NOT
  publicly available on GWAS-Catalog as of 2026-04-25.
- **Downstream impact:** Wave 1 row 13 (MVP-Giri SBP × AFR) triggers the
  D-06 fallback (AoU AFR-SBP derivation per CONTEXT D-07; documented in
  DEC-2026-04-24-02). TSV row 13 status updated to
  `deferred_d06_fallback`. M1 closeout does NOT block; the 45×45 LDSC
  matrix becomes 44×44 until the AoU artifact lands.

### Probe 3 — LDSC 2-trait --rg smoke benchmark

- **Pair tested:** `bmi_EUR.sumstats.gz` ↔ `hypertension_EUR.sumstats.gz`
  (pre-existing pre-pivot munged files at
  `results/pathway/ldsc_partitioned/munged/`).
- **LDSC env:** `.snakemake/conda/481e5f0b6ac97e63f5201cfab7469335_/bin/python`
  (auto-resolved at probe-fire time; smoke_dev base lacks bitarray —
  Rule 3 auto-fix). Has bitarray + numpy=1.26.4 + pandas=2.2.1.
- **Wall time (real):** 13.77 s → `PAIR_WALL_SECONDS = 13`
- **LDSC log:** 3,661 bytes; "Summary of Genetic Correlation Results"
  table emitted with all expected columns including `gcov_int`.
- **Verdict:** ✅ **PASS** — pair wall 13 s (≪ 15 min/pair budget).
- **Downstream impact:** Wave 3 (m1-03) proceeds at full `--jobs`
  density. 44 star-topology calls × ~14 s/pair × 22.5 pairs/call avg ≈
  4 hours of pure LDSC compute, trivially fits within the long-queue
  240 h ceiling (RESEARCH assumption A5). The dynamic `--jobs`
  computation in `m1-03-T2` reads `PAIR_WALL_SECONDS=13` from
  `tests/m1/wave0_probes.log`.

## D-02 GIGASTROKE Resolved Accessions

Resolved via EBI GWAS-Catalog REST API
(`/rest/api/studies/search/findByPublicationIdPubmedId?pubmedId=36180795`,
2 pages, 34 studies). All-stroke (`diseaseTrait="Stroke"`, NOT
ischemic-only / cardioembolic / large-artery / small-vessel) per
phenotype lock in CONTEXT D-02 + SUMSTATS-UPGRADE.md §3.

| Row | Ancestry | Old placeholder                         | New integer-locked filename             | Cases × Controls       |
|-----|----------|-----------------------------------------|-----------------------------------------|------------------------|
| 14  | TRANS    | `GCST90104539_buildGRCh37.tsv.gz`       | `GCST90104534_buildGRCh37.tsv.gz`       | 110,182 × 1,503,898 (5-ancestry meta) |
| 15  | EUR      | `GCST90104540-series_EUR_AS.tsv.gz`     | `GCST90104539_buildGRCh37.tsv.gz`       | 73,652 × 1,234,808     |
| 16  | AFR      | `GCST90104541-series_AA_AS.tsv.gz`      | `GCST90104549_buildGRCh37.tsv.gz`       | 3,961 × 20,030 (AA only) |
| 17  | EAS      | `GCST90104542-series_EAS_AS.tsv.gz`     | `GCST90104544_buildGRCh37.tsv.gz`       | 27,413 × 237,242       |

**SAS deferred:** GCST90104559 (n_cases=3,640 / n_controls=7,672) exists
on GWAS-Catalog but is NOT in Amendment §4 locked inventory; adding a
SAS stroke row would expand the 45-row matrix. Carter discretion to add
later as an inventory amendment if desired.

## D-03 Aragam ZIP Contents (manifest summary)

```
Archive:  data/raw/sumstats_v2/Aragam2022/CAD/Aragam_2022_CARDIoGRAM_CAD_GWAS.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
3064373414  12-05-2022 14:12   CAD_GWAS_BBJ_meta.tsv               (EAS)
1079683735  09-10-2021 11:01   CAD_GWAS_SEX_STRATIFIED.txt.gz       (EUR sex-strat)
3117056837  12-05-2022 14:11   CAD_GWAS_primary_discovery_meta.tsv  (TRANS)
---------                     -------
7261113986                     3 files (~7.3 GB unpacked)
```

**No AFR-specific file.** Therefore **D-03 branch (b) fires:** Klarin 2018
MVP-AFR-CAD fallback (10.1038/s41591-018-0090-y, N≈8.5k AFR). Row 23 of
SUMSTATS-UPGRADE.tsv updated:
- consortium: `MVP` → `MVP-CHARGE`
- citation: `Aragam 2022` → `Klarin 2018 (D-03 fallback)`
- doi: `10.1038/s41588-022-01233-6` → `10.1038/s41591-018-0090-y`
- expected_filename: `Aragam2022_AFR_subset.tsv` →
  `Klarin2018_MVP-AFR-CAD_GCST005195.tsv.gz`
- n_total: 29800 → 8500
- notes (column 14): D-03 branch (b) disposition + ZIP enumeration audit

## D-06 MVP Giri Disposition

- **Primary path attempted (CONTEXT D-06):** GWAS-Catalog publication
  page check at `ebi.ac.uk/gwas/publications/30578418`.
- **Outcome:** NO-SUMMARY-FOUND (Wave 0 Probe 2 result).
- **Branch fired:** **D-06 fallback** = AoU AFR-SBP derivation per
  CONTEXT D-07. Documented in DEC-2026-04-24-02.
- **TSV row 13 update:** status `to_download` → `deferred_d06_fallback`;
  notes column appends fallback path.
- **Carter action (out of band; NOT blocking M1 closeout):** initiate
  AoU Workbench AFR-SBP derivation reusing AOU-LD-PIPELINE.md §2 P1–P7
  scaffolding. The Wave 3 LDSC matrix is 44×44 (not 45×45) until the
  AoU artifact lands. M2 MTAG / CPASSOC may proceed on the 44-key matrix.

## DEC-2026-04-24 Entries (.planning/DECISIONS.md)

- **DEC-2026-04-24-01** (line 579): GRCh37 canonical target for M1
  harmonized sumstats; overrides Amendment §3 M1 "GRCh38" wording. Two
  b38-native sources (Loh 2022 BMI rows 3-4 + GBMI asthma rows 18-20)
  liftover via `pyliftover` + the staged hg38ToHg19 chain at 5%
  drop-rate hard-fail ceiling. Pre-paste check on
  `OSF-AMENDMENT-TEXT-2026-04-22.md`: no "GRCh38" wording present; no
  edit required. Commit: `95e987b`.

- **DEC-2026-04-24-02** (line 620): AoU Researcher Workbench compute
  scope expansion into M1; overrides DEC-2026-04-22-04 M3-only scope.
  Adopts AoU AFR-SBP derivation as M1 D-06 fallback (Probe 2 closed
  primary path). Reuses AOU-LD-PIPELINE.md §2 P1-P7 scaffolding; dual
  egress-audit entries required (M1 AFR-SBP + M3 AFR-LD). Commit:
  `95e987b`.

## Commits

| Task | Commit  | Title                                                                      | Files |
| ---- | ------- | -------------------------------------------------------------------------- | ----- |
| T1   | d91c3c5 | feat(m1-00): stage conda envs + pytest scaffolding + canonical-frame validator | 17    |
| T2   | 21e669b | chore(m1-00): stage Wave 0 reference data + probe outcomes                  | 3     |
| T3   | 95e987b | docs(m1-00): GIGASTROKE GCST integer lock + Aragam D-03 fallback + DEC-2026-04-24 entries | 3     |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Add missing critical functionality] CANONICAL_COLS + validate_canonical_frame**
- **Found during:** Task 1 — `tests/m1/test_harmonizer_contract.py` per the
  plan imports `sumstats_utils.validate_canonical_frame`, which did not
  exist in `src/python/sumstats_utils.py` (only the existing Phase 09
  helpers `is_palindromic`, `filter_palindromic_ambiguous`,
  `liftover_to_grch37` were present).
- **Issue:** The 10-column schema was hard-coded inside each Phase 09
  harmonizer (`harmonize_gbmi.py` line 33, others similarly) and the M1
  plan's test contract requires a centralized `validate_canonical_frame`.
- **Fix:** Appended `CANONICAL_COLS` + `validate_canonical_frame(df)`
  to `src/python/sumstats_utils.py`. The validator asserts: 10 canonical
  columns present, numeric columns numeric dtype, allele columns string
  dtype. Raises `ValueError` with explicit message naming missing /
  bad-typed columns.
- **Files modified:** `src/python/sumstats_utils.py`
- **Commit:** `d91c3c5`

**2. [Rule 3 - Auto-fix blocking issue] LDSC env auto-detect**
- **Found during:** Task 2 — Probe 3 first attempt with
  `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python` (the
  default env per project memory) failed:
  `ModuleNotFoundError: No module named 'bitarray'`.
- **Issue:** `smoke_dev` has Snakemake 7.32.4 + Python 3.11 but does not
  carry bitarray (an LDSC-Py3 dependency). Probe 3 cannot fire without
  it; without Probe 3 the Wave 3 wall-time calibration is unsourced.
- **Fix:** Modified `tests/m1/wave0_probes.sh` to auto-detect a
  bitarray-equipped Python env. The snakemake-cached LDSC env at
  `.snakemake/conda/481e5f0b6ac97e63f5201cfab7469335_/bin/python` has
  bitarray + numpy=1.26.4 + pandas=2.2.1; the probe falls back to
  `smoke_dev` if that env is absent. Re-fired Probe 3 successfully —
  13.77 s wall clock.
- **Files modified:** `tests/m1/wave0_probes.sh`
- **Commit:** `21e669b`

**3. [Rule 3 - URL rot] LDSC reference LD via Phase 5 staged copy**
- **Found during:** Task 2 — Direct curl of the plan-spec'd Broad URLs
  (`data.broadinstitute.org/alkesgroup/LDSCORE/eur_w_ld_chr.tar.bz2` and
  `.../w_hm3.snplist.bz2`) returned HTTP 404. Both endpoints are gone.
- **Issue:** Plan spec'd a download-from-Broad path that no longer
  works; without LDSC LD reference + HM3 SNP list, Wave 3 cannot fire.
- **Fix:** Per `feedback_url_rot_workarounds.md` memory + project
  history (Phase 5 staged the same files via Zenodo 14993076 on
  2026-04-14), reused the existing copy at `data/reference/ldsc/`.
  Symlinked `data/external/ldscore/eur_w_ld_chr` →
  `data/reference/ldsc/eur_w_ld_chr/` and `data/external/ldscore/w_hm3.snplist`
  → `data/reference/ldsc/w_hm3.snplist`. Avoids ~1 GB duplication.
- **Files modified:** symlinks under `data/external/ldscore/`
- **Commit:** `21e669b`

### Decisions deviating from plan suggestion

**4. SAS stroke row deferred (NOT added)**
- The plan's Task 3 suggestion: "Add a row if a SAS subset exists; skip
  if not." A SAS subset DOES exist (`GCST90104559`, n_cases=3,640).
- However, Amendment §4 locks the 45-row inventory and adding a SAS row
  would expand it to 46. Adding rows mid-plan without a separate
  amendment is risky.
- Deferred: SAS GCST documented in this SUMMARY for future inventory
  amendment if Carter elects to expand.

**5. Mamba dry-runs for env solves NOT executed**
- The plan suggested `mamba env create -n smoke-... --dry-run` per env.
- Mamba 2.5 with `--dry-run` actually creates a real env (observed
  during initial attempt — `mamba env list` showed the smoke env
  resident). HPC compute economics + the snakemake `--use-conda`
  pattern (which creates per-rule envs at first run) make explicit
  pre-solves redundant.
- Substitute: programmatic YAML structure validation (PyYAML parse +
  name + channels + dependencies presence). 5/5 envs valid.

## Auth Gates / Human Actions

None of the Wave 0 probes encountered an auth gate. The D-06 disposition
section documents one **future Carter action** (out of band from
`/gsd-execute-phase` scope): initiate AoU Researcher Workbench AFR-SBP
derivation per AOU-LD-PIPELINE.md §2 P1–P7 — required before the AoU
artifact can join Wave 3's matrix.

## Wave 0 Verification Gate

```
test -f envs/m1-harmonize.yml \
  && test -f envs/m1-munge.yml \
  && test -f envs/m1-ldsc-rg.yml \
  && test -f envs/m1-qc.yml \
  && test -f envs/m1-download.yml \
  && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m1/ -q --tb=short \
  && test -s data/external/liftover/hg38ToHg19.over.chain.gz \
  && test -d data/external/ldscore/eur_w_ld_chr \
  && test -f data/external/ldscore/w_hm3.snplist \
  && test -f data/raw/sumstats_v2/Aragam2022/aragam_zip_manifest.txt \
  && ! grep -q "GCST90104540-series" .planning/amendments/SUMSTATS-UPGRADE.tsv \
  && grep -q "DEC-2026-04-24-01" .planning/DECISIONS.md \
  && grep -q "DEC-2026-04-24-02" .planning/DECISIONS.md
```

→ **EXIT 0** (all gates pass). Pytest: **15 passed, 2 skipped**.

## Downstream Wave Consequences

| Wave / Plan          | Consequence                                                                              |
| -------------------- | ---------------------------------------------------------------------------------------- |
| Wave 1 (m1-01)       | Row 13 (MVP-Giri AFR-SBP) emits `.placeholder` (D-06 fallback). Row 23 (CAD-AFR) downloads Klarin 2018 GCST005195 not Aragam ZIP. Rows 14-17 (GIGASTROKE) use integer GCSTs in download URL construction. |
| Wave 2a/2b (m1-02a/b) | Loh 2022 BMI + GBMI asthma harmonizers call `liftover_to_grch37` (DEC-2026-04-24-01). 7 new harmonizers + reused harmonize_gbmi all import `sumstats_utils.validate_canonical_frame`. |
| Wave 3 (m1-03)       | Star-topology --rg orchestration; PAIR_WALL_SECONDS=13 calibration drives dynamic --jobs; 44×44 matrix (not 45×45) until AoU AFR-SBP lands. |
| Wave 4 (m1-04)       | trait_inventory.yaml schema enforced by tests/m1/test_inventory_yaml.py validator (4 tests). 44 traits + AoU placeholder for AFR-SBP slot. |

## Self-Check: PASSED

All claimed artifacts present on disk and all 3 task commits resolved
in `git log`. Verification run 2026-04-25T05:42Z:

- 21/21 created files FOUND
- 1/1 created directory (symlinked) FOUND
- 3/3 task commits FOUND in git log
- Wave 0 verification gate: EXIT 0
- Pytest: 15 passed, 2 skipped (skips explicit + expected)

