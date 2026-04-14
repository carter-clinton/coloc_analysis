---
phase: 09-replication-in-independent-cohorts
plan: 01
subsystem: infra
tags: [snakemake, conda, pytest, testthat, yaml, replication, finngen, mvp, bbj, gbmi, gcta, metafor]

# Dependency graph
requires:
  - phase: 00-data-access-infrastructure
    provides: DUA-gated cohort access (FinnGen R12 registration, MVP open-access verification, UKB-PPP Synapse cert, deCODE portal)
  - phase: 01-coloc-susie-fine-mapping-spine
    provides: .fit.rds discovery-signal fits (ingested in Plan 09-03)
  - phase: 02-3-way-qtl-colocalization
    provides: tier_assignments.tsv + negative_controls.yaml (reused for HLA negative control in Plan 09-05)
provides:
  - Phase 9 Snakemake rule module (replication.smk, 24 skeleton rules §A-§G)
  - Phase 9 conda env pair (gcta.yml new, r_coloc.yml extended with metafor+data.table)
  - Phase 9 cohort config (config/replication_cohorts.yaml; 4 cohorts × per-trait endpoint codes)
  - Phase 9 test scaffolding (pytest 13 tests + testthat 2 tests = 15 tests, 10 green/5 xfail)
  - MVP phs001672 inventory (resolves RESEARCH A1/Open Question 1)
affects: [09-02-ingest-harmonize, 09-03-manifest-susie-fit, 09-04-coloc-fiqt-meta, 09-05-cojo-aggregate]

# Tech tracking
tech-stack:
  added:
    - "GCTA 1.94.1 (COJO sensitivity)"
    - "r-metafor >= 3.0 (IVW meta-analysis backend)"
    - "r-data.table >= 1.14 (sumstats I/O)"
  patterns:
    - "Rule module pattern: include: \"src/snakemake/rules/<phase>.smk\" from top-level Snakefile"
    - "Skeleton-first: placeholder rules with touch {output} so DAG resolves before implementation"
    - "Session-scoped config fixture pattern for per-plan YAML validation (Phase 5 conftest extended)"

key-files:
  created:
    - "config/replication_cohorts.yaml"
    - "envs/gcta.yml"
    - "src/snakemake/rules/replication.smk"
    - "tests/phase9/__init__.py"
    - "tests/phase9/conftest.py"
    - "tests/phase9/test_cohort_ingest.py"
    - "tests/phase9/test_trait_harmonization.py"
    - "tests/phase9/test_meta_ivw.py"
    - "tests/phase9/test_cojo_sensitivity.py"
    - "tests/phase9/test_master_table_schema.py"
    - "tests/phase9/test_negative_controls.py"
    - "tests/phase9/r/test_fiqt.R"
    - "tests/phase9/r/test_coloc_replication.R"
    - ".planning/phases/09-replication-in-independent-cohorts/mvp_phs001672_inventory.md"
  modified:
    - "Snakefile"
    - "envs/r_coloc.yml"

key-decisions:
  - "MVP phs001672 enumeration confirmed only T2D (5 strata) + quantitative BP (SBP/DBP/PP × EUR + transethnic) are released; stroke/asthma/BMI explicitly NOT_RELEASED — replication for those traits runs FinnGen + BBJ + GBMI only"
  - "MVP phs001672 genome build is GRCh38 (not GRCh37 as plan draft assumed); liftover_required flipped to true"
  - "MVP column_map uses dbGaP GWAS-central schema (|β| absolute-value + Coded Allele direction) not REGENIE (BETA/LOG10P); harmonizer in Plan 09-02 must reconstruct signed β"
  - "configfile: directive takes string literal not Path(); config path is project-root-relative (matches top-level Snakefile convention)"
  - "workflow.basedir resolves to project root (top-level Snakefile location), not rule-file location; envs/ paths use Path(workflow.basedir) / 'envs' / ... with no .parent.parent"

patterns-established:
  - "Rule module via Snakefile include: path='src/snakemake/rules/<phase>.smk'; config via project-root-relative string literal"
  - "Pytest Phase-N scaffold: conftest.py session-scoped config fixture + tmp_path mock sumstats fixtures; production-code tests xfail until implementer plan lands"
  - "dbGaP FTP enumeration via HTTP Range: bytes=0-2000 on each phs######.pha#####.txt header to capture Name + Description without downloading full TSV"

requirements-completed: []

# Metrics
duration: 23min
completed: 2026-04-14
---

# Phase 09 Plan 01: Infrastructure Skeleton Summary

**Phase 9 foundation — 24 Snakemake placeholder rules, 2 conda env changes, 4-cohort YAML registry with MVP phs001672 trait inventory, and 15 pytest/testthat scaffolds — all downstream plans (09-02…09-05) have concrete artifacts to consume.**

## Performance

- **Duration:** 23 min (wall-clock across 3 task commits)
- **Started:** 2026-04-14 (execution start)
- **Completed:** 2026-04-14
- **Tasks:** 3 / 3
- **Files created:** 14
- **Files modified:** 2

## Accomplishments

- **MVP dbGaP phs001672 enumerated.** Fetched HTTP Range byte-0-2000 headers for all 335 `pha*.txt` analysis files; grep'd Name+Description for each target trait; confirmed **T2D** (pha004943-4947, 5 ancestry strata) and **quantitative BP** (SBP primary + DBP/PP sensitivity, EUR-only + transethnic flavors) are released, and marked **stroke**, **asthma**, **BMI** as `NOT_RELEASED_AS_OF_2026-04` with action `exclude_from_MVP_cohort_column`. This resolves RESEARCH Open Question 1 and Assumption A1.
- **Genome build corrected:** all MVP phs001672 metadata headers declare `Human genome build: 38`; plan draft YAML had claimed GRCh37. Fixed YAML to `genome_build: GRCh38, liftover_required: true`.
- **MVP column schema corrected:** dbGaP GWAS-central schema (`Chr ID`, `|β|`, `Coded Allele`, `Sample size`) not REGENIE (`CHROM`, `BETA`, `LOG10P`). Harmonizer in Plan 09-02 must reconstruct signed β from `|β|` × coded-allele orientation.
- **Snakemake rule skeleton** (24 rules across §A ingest → §G aggregation) included from top-level `Snakefile`; `snakemake --list` emits `all_replication` plus 23 other Phase 9 targets; DAG resolves cleanly with placeholder `touch {output}` bodies.
- **Test harness** scaffolded: 13 pytest + 2 testthat (15 total) collected; 10 pass on infrastructure, 5 xfail on production-code placeholders (to flip green in Plans 09-02…09-05).

## Task Commits

1. **Task 1: MVP dbGaP phs001672 enumeration + replication_cohorts.yaml** — `d1c1621` (feat)
2. **Task 2: Conda envs + Snakemake rule skeleton + Snakefile include** — `db1d847` (feat)
3. **Task 3: Pytest + testthat scaffolding (15 tests)** — `7143ec1` (test)

## Files Created/Modified

- `config/replication_cohorts.yaml` — 4-cohort registry (FinnGen R12, MVP phs001672, BBJ hum0197-v3, GBMI) × 5 traits × per-trait endpoint codes, PP.H4 sweep thresholds, LD panel mapping, COJO LD caveat
- `envs/gcta.yml` — GCTA 1.94.1 for COJO sensitivity (bioconda)
- `envs/r_coloc.yml` — extended with `r-metafor >= 3.0` + `r-data.table >= 1.14` for IVW meta
- `src/snakemake/rules/replication.smk` — 24 skeleton rules (5 ingest + 6 harmonize + 2 manifest/fit + 1 coloc + 3 FIQT/meta + 2 COJO + 4 aggregation + 1 master target)
- `Snakefile` — `include: "src/snakemake/rules/replication.smk"` appended after pathway.smk
- `tests/phase9/` — 10 files total (`__init__.py`, `conftest.py`, 6 pytest, 2 testthat in `r/`)
- `.planning/phases/09-replication-in-independent-cohorts/mvp_phs001672_inventory.md` — MVP trait availability evidence file

## Decisions Made

- **Skeleton-first Snakemake rule module** (all rules `touch {output}` in Wave 1) lets Plans 09-02…09-05 replace individual rule bodies without redefining the DAG structure. Same pattern as Phase 5 pathway.smk's "Placeholder analysis rules to be filled in Plans 02-05" pattern.
- **MVP hypertension proxy:** SBP primary, DBP+PP sensitivity. Mirrors BBJ's SBP-only encoding (no binary HTN). Cross-cohort meta with FinnGen's binary `I9_HYPTENSESS` requires z-score-scale harmonization downstream (flagged for Plan 09-04 meta rule).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected MVP phs001672 genome build GRCh37 → GRCh38**
- **Found during:** Task 1 (MVP metadata enumeration)
- **Issue:** Plan draft YAML claimed `genome_build: GRCh37, liftover_required: false` for MVP. All 335 metadata headers fetched from the dbGaP FTP return `# Human genome build: 38`.
- **Fix:** Updated YAML to `genome_build: GRCh38, liftover_required: true`; Plan 09-02 harmonizer will liftover MVP alongside FinnGen + BBJ.
- **Files modified:** `config/replication_cohorts.yaml`
- **Verification:** Sample metadata verified via `curl --range 0-2000 https://ftp.ncbi.nlm.nih.gov/dbgap/studies/phs001672/analyses/phs001672.pha004945.txt | grep 'Human genome build'` → `38`.
- **Committed in:** `d1c1621` (Task 1 commit)

**2. [Rule 1 - Bug] Corrected MVP column_map schema (dbGaP not REGENIE)**
- **Found during:** Task 1 (inspecting pha004943 + pha004945 headers)
- **Issue:** Plan draft mapped MVP columns as if files were raw REGENIE output (`CHROM, BETA, LOG10P, A1_FREQ`). Actual dbGaP schema is GWAS-central (`Chr ID, |β|, Coded Allele, Sample size`); β is absolute-value and direction must be reconstructed from the Coded Allele orientation during harmonization.
- **Fix:** Updated YAML column_map to dbGaP schema keys with `beta_abs` + `coded_allele` fields and a note that Plan 09-02 harmonizer must reconstruct signed β.
- **Files modified:** `config/replication_cohorts.yaml`
- **Verification:** Header inspection of pha004943/45/46/47 all show identical dbGaP column set.
- **Committed in:** `d1c1621` (Task 1 commit)

**3. [Rule 1 - Bug] Fixed configfile: directive in replication.smk**
- **Found during:** Task 2 (writing rule skeleton)
- **Issue:** Plan draft used `configfile: Path(workflow.basedir).parent.parent / "config" / "replication_cohorts.yaml"`. Two bugs: (a) `configfile:` directives only accept string literals, not Python expressions; (b) `workflow.basedir` resolves to the *top-level Snakefile directory* (project root), so `.parent.parent` would escape project root.
- **Fix:** Used `configfile: "config/replication_cohorts.yaml"` — relative-to-project-root string literal, matching top-level Snakefile convention (`configfile: "config/pipeline.yaml"`).
- **Files modified:** `src/snakemake/rules/replication.smk`
- **Verification:** `snakemake --list` executes cleanly (24 Phase 9 rules visible).
- **Committed in:** `db1d847` (Task 2 commit)

**4. [Rule 1 - Bug] Fixed envs/ path resolution**
- **Found during:** Task 2 (setting GCTA_ENV variable)
- **Issue:** Plan draft used `str(Path(workflow.basedir) / ".." / ".." / "envs" / "gcta.yml")` — also based on the incorrect assumption that `workflow.basedir` tracks the rule-file directory. Would fail at runtime with `ENOENT`.
- **Fix:** Used `str(Path(workflow.basedir) / "envs" / "gcta.yml")` matching `ld_reference.smk:31` pattern.
- **Files modified:** `src/snakemake/rules/replication.smk`
- **Verification:** Snakemake parses without error; `run_cojo_slct` rule surfaces in `--list`.
- **Committed in:** `db1d847` (Task 2 commit)

---

**Total deviations:** 4 auto-fixed (all Rule 1 bug fixes). All 4 were factual errors in the plan draft that would have caused runtime failures in Plan 09-02. No scope creep.
**Impact on plan:** Neutral — fixes ensure downstream plans work as intended; no new work added.

## Issues Encountered

- Fetching 335 MVP metadata headers serially hit FTP rate limits; switched to parallelized background curl with `--range 0-2000` to get only the metadata section. Reduced fetch time from ~40 min to ~3 min.
- One trait in phs001672 (`pha005043`) has a Name of "Renal" but Description mentions SBP — inspected and excluded (description mis-copied from SBP; trait is not usable for BP replication).

## User Setup Required

None - no external service configuration required for skeleton phase. DUAs for FinnGen R12 and MVP are already filed (Phase 0 closeout); BBJ NBDC and GBMI portal are open-access.

## Next Phase Readiness

- Plan 09-02 (ingest + harmonize) can begin immediately. It consumes:
  - `config/replication_cohorts.yaml` URLs + column_maps + endpoint codes
  - `src/snakemake/rules/replication.smk` skeleton rules (replace `touch {output}` with real download/harmonize shells)
  - `tests/phase9/conftest.py` mock fixtures (`mock_finngen_sumstats`, etc.) for unit-testing new `harmonize_*` functions
- MVP harmonizer must implement dbGaP-schema decoding (|β| + Coded Allele → signed β).
- All 5 `xfail` production-code placeholder tests will flip green as Plans 09-02…09-05 implement their respective scripts.

## Self-Check: PASSED

Verified present:
- FOUND: `config/replication_cohorts.yaml`
- FOUND: `envs/gcta.yml`
- FOUND: `src/snakemake/rules/replication.smk` (24 rules)
- FOUND: `tests/phase9/__init__.py`, `tests/phase9/conftest.py`, 6 pytest files, 2 testthat R files
- FOUND: `.planning/phases/09-replication-in-independent-cohorts/mvp_phs001672_inventory.md`

Verified commits:
- FOUND: `d1c1621` (Task 1 — config + inventory)
- FOUND: `db1d847` (Task 2 — envs + replication.smk + Snakefile include)
- FOUND: `7143ec1` (Task 3 — 15 phase9 tests)

Verified infrastructure:
- `python -c "import yaml; yaml.safe_load(open('config/replication_cohorts.yaml'))"` → OK
- `grep -c '^rule ' src/snakemake/rules/replication.smk` → 24 (≥ 20)
- `snakemake --list | grep -c '^all_replication$'` → 1
- `pytest tests/phase9 --collect-only -q` → 15 tests collected
- `pytest tests/phase9 -q` → 10 passed, 5 xfailed

---
*Phase: 09-replication-in-independent-cohorts*
*Completed: 2026-04-14*
