---
phase: 00-data-access-infrastructure
verified: 2026-04-10T20:30:00Z
status: human_needed
score: 5/8 must-haves verified
overrides_applied: 0
gaps:
  - truth: "OSF pre-registration submitted"
    status: failed
    reason: "Plan 02 checkpoint pending -- user has not yet submitted OSF pre-registration. Zero evidence of OSF DOI in data_access.md or any project file."
    artifacts: []
    missing:
      - "User must submit OSF pre-registration and record DOI in .planning/data_access.md"
  - truth: "Corrupted supplementary tables (Table 1, 3, S4) fixed and DIAMANTE T2D dedup resolved"
    status: partial
    reason: "DIAMANTE dedup audit completed (commit 81611aa) confirming methodology is sound. However, Tables 1/3/S4 are manuscript-only (no CSV/TSV in legacy tree) -- they cannot be 'fixed' until tables are regenerated from new coloc.susie results in later phases. The audit commit explicitly documents this."
    artifacts:
      - path: "commit 81611aa"
        issue: "Audit is documented but tables themselves are not fixable at this stage"
    missing:
      - "Table regeneration from coloc.susie results (Phase 1+/Phase 11)"
human_verification:
  - test: "Complete Synapse certified-user registration and verify access to syn51364943 (UKB-PPP pQTL)"
    expected: "Synapse account active, certified-user quiz passed, syn51364943 accessible"
    why_human: "Portal registration requires browser interaction and personal credentials"
  - test: "Submit FinnGen registration form and confirm email receipt"
    expected: "FinnGen elomake form submitted, download instructions received via email"
    why_human: "Registration form requires manual browser submission"
  - test: "Manually verify deCODE summarydata portal in browser (client-side rendering blocks curl)"
    expected: "pQTL sumstats files visible and downloadable from decode.com/summarydata/"
    why_human: "Client-side rendered page cannot be verified via curl"
  - test: "Submit OSF pre-registration with analytical plan and record DOI"
    expected: "OSF registration DOI recorded in .planning/data_access.md"
    why_human: "OSF submission requires manual form entry and scientific content authoring"
  - test: "Verify toy 3-locus CI smoke test can complete end-to-end after data population"
    expected: "snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda completes in under 15 minutes"
    why_human: "Requires data download (Plan 02 checkpoint) and subset script execution first"
---

# Phase 0: Data Access + Infrastructure Verification Report

**Phase Goal:** Establish all data sources, fix legacy issues, build reproducible Snakemake skeleton with CI smoke test.
**Verified:** 2026-04-10T20:30:00Z
**Status:** human_needed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All 7 open-access data sources downloaded or confirmed reachable | VERIFIED | HPC connectivity verified for all 7 sources via curl HEAD requests (commit 12abd06). 7 checked items in data_access.md. GTEx, Pan-UKBB, BBJ, MVP, GBMI confirmed HTTP 200. Synapse, FinnGen reachable but require user registration (separate checkpoint). |
| 2 | All of Us institutional DURA status documented in .planning/data_access.md | VERIFIED | data_access.md line 173: "Carter already has Controlled Tier access (confirmed 2026-04-09)" -- AoU DURA check is moot because user is already credentialed. |
| 3 | Corrupted supplementary tables (Table 1, 3, S4) fixed and DIAMANTE T2D dedup resolved | PARTIAL | DIAMANTE T2D dedup audit documented in commit 81611aa. Position-level dedup confirmed methodologically sound. BUT: Tables 1/3/S4 exist only as manuscript prose, not as CSV/TSV data files in the legacy tree. Tables cannot be "fixed" until regenerated from new coloc.susie results. The dedup half is resolved; the table fix half is deferred by necessity. |
| 4 | Legacy hardcoded paths parameterized via config/pipeline.yaml (grep returns 0 matches) | VERIFIED | `grep -r "admixmap\|admix_map\|/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/R src/python src/snakemake config` returns 0 matches. REQ-12 acceptance test passes. |
| 5 | Conda envs pinned under envs/*.yml with exact versions | VERIFIED | r_coloc.yml: r-base=4.4.2, r-coloc=5.2.3, r-susier=0.14.2. python_stats.yml: snakemake=7.32.4, python=3.11. plink.yml: plink=1.90b6.21, plink2=2.00a6.1, bcftools=1.21. All use =version format. |
| 6 | Snakemake skeleton built with per-trait/ancestry schema validation | VERIFIED | Snakefile at project root: `validate(config, "src/snakemake/schemas/pipeline.schema.yaml")`. All 8 rules refactored in src/snakemake/rules/ with config-based paths. All 8 rules have conda: directives. 1,071 lines of rule code total. |
| 7 | Toy 3-locus CI smoke test completes in under 15 minutes | PARTIAL | Scaffolding complete: Snakefile.test, config_test.yaml, regions_toy.csv (3 loci), expected_results.yaml, subset script, LSF cron wrapper. Snakefile.test reuses production rules. Config override paths all under tests/toy_3locus/. Cannot verify 15-minute completion until toy data is populated (requires data downloads from Plan 02 checkpoint). |
| 8 | OSF pre-registration submitted | FAILED | No evidence of OSF submission or DOI in any project file. Plan 02 Task 2 checkpoint:human-verify is pending. |

**Score:** 5/8 truths verified (2 partial, 1 failed)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `config/pipeline.yaml` | Single source of truth for paths (D-08) | VERIFIED | Contains data_root, EAS/HIS ancestries, GRCh37 build, no absolute paths |
| `config/datasets.yaml` | Per-source column maps (D-21) | VERIFIED | 12 datasets (8 legacy + 4 new ancestry: bbj_eas, gurdasani, hoffmann, page_hchs) |
| `config/cluster_lsf.yaml` | LSF profile (D-07) | VERIFIED | __default__ + 7 per-rule overrides |
| `data/manifest.yaml` | 20-source data catalog (D-12) | VERIFIED | 20 sources, all with genome_build field, FinnGen flagged needs_liftover: true |
| `envs/r_coloc.yml` | Pinned R + coloc env (D-24) | VERIFIED | r-base=4.4.2, r-coloc=5.2.3, r-susier=0.14.2, r-yaml=2.3.10 |
| `envs/python_stats.yml` | Pinned Python env (D-24) | VERIFIED | snakemake=7.32.4, python=3.11 (fixes legacy 8.* bug) |
| `envs/plink.yml` | Pinned PLINK env (D-24) | VERIFIED | plink=1.90b6.21, plink2=2.00a6.1, bcftools=1.21 |
| `src/R/utils/load_config.R` | R config loader (D-09) | VERIFIED | load_pipeline_config() + resolve_path() + helpers, 91 lines |
| `src/snakemake/schemas/pipeline.schema.yaml` | JSON Schema validation (D-06) | VERIFIED | Draft-07, required fields enforced |
| `src/snakemake/schemas/datasets.schema.yaml` | JSON Schema for datasets (D-06) | ORPHANED | File exists (substantive) but NOT wired via validate() in Snakefile |
| `Snakefile` | Top-level workflow (D-07) | VERIFIED | 162 lines, imports all 8 rules, validates config, conditional includes |
| `src/snakemake/rules/sumstats.smk` | Refactored sumstats rule (D-05) | VERIFIED | 197 lines, config["paths"] throughout, conda: directives |
| `src/snakemake/rules/regions.smk` | Refactored regions rule (D-05) | VERIFIED | 29 lines, config-based paths |
| `src/snakemake/rules/ld_reference.smk` | Refactored LD reference rule (D-05) | VERIFIED | 174 lines, 3 conda directives |
| `src/snakemake/rules/finemap.smk` | Refactored fine-mapping rule (D-05) | VERIFIED | 149 lines, 5 rules, conda: envs/r_coloc.yml + envs/python_stats.yml |
| `src/snakemake/rules/qc.smk` | QC rules (D-05) | VERIFIED | 93 lines, 4 rules, conda: envs/python_stats.yml |
| `src/snakemake/rules/multitrait.smk` | Multitrait rules (D-05) | VERIFIED | 319 lines, 13 rules, conda: envs/r_coloc.yml |
| `src/snakemake/rules/mr.smk` | MR manifest + stub (D-05) | VERIFIED | 55 lines, intentional stub (legacy behavior preserved per D-04) |
| `src/snakemake/rules/pgs.smk` | PGS manifest + stub (D-05) | VERIFIED | 55 lines, intentional stub (legacy behavior preserved per D-04) |
| `src/python/liftover.py` | GRCh38-to-GRCh37 utility (D-02) | VERIFIED | 188 lines, 2 functions, real implementation with BED conversion + liftOver invocation |
| `config/regions_curated.csv` | Curated regions without KCNJ11 (D-19) | VERIFIED | 8 regions, KCNJ11 absent (grep returns 0) |
| `tests/toy_3locus/Snakefile.test` | Smoke test Snakefile (D-15) | VERIFIED | Includes production rules, configfile: tests/toy_3locus/config_test.yaml |
| `tests/toy_3locus/config_test.yaml` | Test config override (D-15) | VERIFIED | All paths under tests/toy_3locus/, valid YAML, schema-compatible |
| `tests/toy_3locus/data/regions_toy.csv` | 3 toy loci (D-14) | VERIFIED | FTO, TCF7L2, SH2B3 with correct coordinates |
| `tests/toy_3locus/expected/expected_results.yaml` | Expected PP.H4 values (D-16) | VERIFIED | 3 loci with pp_h4 and tolerance values (placeholders, noted) |
| `scripts/subset_toy_loci.py` | Subsetting utility | VERIFIED | TOY_LOCI dict with 3 loci, tabix-based extraction |
| `scripts/run_ci_smoke.sh` | LSF cron wrapper (REQ-9) | VERIFIED | bsub invocation, ci_status.md logging, executable |
| `.planning/ci_status.md` | CI status log (REQ-9) | VERIFIED | Markdown table header present (Status in header row) |
| `.planning/data_access.md` | Data access tracker (REQ-1) | VERIFIED | 7 checked items, HPC connectivity annotations, AoU status documented |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| config/pipeline.yaml | src/snakemake/schemas/pipeline.schema.yaml | validate() in Snakefile | WIRED | Line 18: `validate(config, "src/snakemake/schemas/pipeline.schema.yaml")` |
| config/datasets.yaml | src/snakemake/schemas/datasets.schema.yaml | validate() call | NOT WIRED | datasets.yaml loaded via yaml.safe_load() but NOT validated against schema |
| config/pipeline.yaml | src/R/utils/load_config.R | yaml::read_yaml default path | WIRED | load_config.R defaults to "config/pipeline.yaml" (line 25), uses yaml::read_yaml (line 37) |
| Snakefile | src/snakemake/rules/*.smk | include directives | WIRED | 8 include directives (lines 104-116), 6 unconditional + 2 conditional |
| src/snakemake/rules/sumstats.smk | config/pipeline.yaml | config["paths"] dict | WIRED | 10+ references to config["paths"] throughout file |
| src/snakemake/rules/finemap.smk | envs/r_coloc.yml | conda: directive | WIRED | conda: "envs/r_coloc.yml" at line 73 (run_finemap rule) |
| tests/toy_3locus/Snakefile.test | src/snakemake/rules/*.smk | include directives | WIRED | 4 includes: sumstats, regions, finemap (conditional), ld_reference (conditional) |
| tests/toy_3locus/config_test.yaml | config/pipeline.yaml | Override of same schema | WIRED | Same keys (traits, ancestries, genome_build, paths), validated against same schema |
| .planning/data_access.md | data/manifest.yaml | Manual update | WIRED | manifest has download_date fields for manual population |

### Data-Flow Trace (Level 4)

Not applicable -- Phase 0 produces infrastructure files (configs, schemas, rule definitions), not components that render dynamic data. Data flow through the Snakemake pipeline will be verified when the pipeline actually executes (Phase 1+).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| pipeline.yaml is valid YAML with required keys | `python3 -c "import yaml; d=yaml.safe_load(open('config/pipeline.yaml')); assert 'EAS' in d['ancestries']"` | Passed | PASS |
| datasets.yaml has 12 datasets including new ancestry | `python3 -c "import yaml; d=yaml.safe_load(open('config/datasets.yaml')); assert 'bbj_eas' in d['datasets']"` | Passed | PASS |
| REQ-12 grep returns 0 matches | `grep -r "admixmap\|admix_map\|/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/R src/python src/snakemake config \| wc -l` | 0 | PASS |
| KCNJ11 absent from regions | `grep -c "KCNJ11" config/regions_curated.csv` | 0 | PASS |
| All 8 rule files have conda directives | Per-file grep | All 8 have 1+ conda: lines | PASS |
| Conda envs have version pins | grep analysis | All deps use =version format | PASS |
| Data manifest has 20 sources with genome_build | python3 analysis | 20 sources, 20 with genome_build | PASS |
| DIAMANTE dedup audit commit exists | `git log --oneline \| grep DIAMANTE` | 81611aa found | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-----------|-------------|--------|----------|
| REQ-1 | 00-02 | Data access runs in parallel from Day 1 | PARTIAL | HPC connectivity verified for all 7 sources. 7 items checked in data_access.md. AoU DURA status documented. BUT: Synapse, FinnGen, deCODE registrations pending (checkpoint:human-verify). OSF pre-registration not submitted. |
| REQ-9 | 00-04, 00-03 | Snakemake pipeline has CI smoke test | PARTIAL | Smoke test scaffolding complete (Snakefile.test, config override, 3 loci, expected results, LSF cron wrapper, ci_status.md). Cannot verify 15-min completion until toy data populated. Conda envs pinned. |
| REQ-12 | 00-01, 00-03 | Legacy path references are parameterized | SATISFIED | grep acceptance test returns 0 matches. All rules use config["paths"]. No hardcoded absolute paths in any created file. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| src/snakemake/schemas/datasets.schema.yaml | N/A | Orphaned -- exists but never called by validate() | WARNING | Schema validation for datasets.yaml is not enforced; invalid datasets.yaml would silently pass |
| src/snakemake/rules/mr.smk | 35 | Intentional stub: `run_mr_placeholder` | INFO | Expected -- legacy MR rule is a placeholder, preserved per D-04 |
| src/snakemake/rules/pgs.smk | 35 | Intentional stub: `run_pgs_placeholder` | INFO | Expected -- legacy PGS rule is a placeholder, preserved per D-04 |
| tests/toy_3locus/expected/expected_results.yaml | 5-8 | PP.H4 values are approximate placeholders | INFO | Expected -- values will be updated after first real run with data |

### Human Verification Required

### 1. Complete Portal Registrations (Synapse, FinnGen, deCODE)

**Test:** Register on Synapse (UKB-PPP access), submit FinnGen elomake form, manually verify deCODE portal in browser.
**Expected:** Synapse certified-user account active with syn51364943 access. FinnGen download instructions received. deCODE pQTL files visible.
**Why human:** Portal registrations require browser interaction, personal credentials, and institutional affiliation verification.

### 2. Submit OSF Pre-registration

**Test:** Create OSF registration documenting the 5 traits, analytical phases, PP.H4 threshold sweep values, replication cohorts, and equity framing plan.
**Expected:** OSF registration DOI recorded in .planning/data_access.md.
**Why human:** Scientific pre-registration requires manual content authoring and form submission.

### 3. Verify Toy 3-Locus CI Smoke Test End-to-End

**Test:** After data downloads, run `python scripts/subset_toy_loci.py` then `snakemake --snakefile tests/toy_3locus/Snakefile.test --cores 2 --use-conda`.
**Expected:** Pipeline completes in under 15 minutes. PP.H4 values within tolerance.
**Why human:** Requires populated toy data (dependent on data downloads) and HPC job submission.

### Gaps Summary

**1 definite gap, 1 partial gap, 5 items needing human verification.**

**Gap 1 (FAILED): OSF pre-registration not submitted.** This is ROADMAP SC #8 and a Plan 02 checkpoint:human-verify deliverable. No evidence of any OSF activity. This blocks phase completion.

**Gap 2 (PARTIAL): Supplementary table fixes.** The DIAMANTE T2D dedup audit is done (commit 81611aa confirming methodology is sound). However, Tables 1/3/S4 exist only as manuscript prose, not as data files. They cannot be "fixed" at this stage -- they will be regenerated from new coloc.susie results. The ROADMAP SC wording "fixed" may be overly prescriptive given that no CSV/TSV table files exist to fix. The dedup resolution half IS complete.

**datasets.schema.yaml orphan:** The schema file exists and is substantive but is not wired into the Snakefile via a validate() call. This is a minor wiring gap (WARNING severity, not a blocker) that should be addressed but does not block the phase goal.

**Plan 02 checkpoint status:** Plan 02 Task 1 (HPC connectivity verification) is complete. Task 2 (checkpoint:human-verify) is pending user action for portal registrations and OSF pre-registration. This is the primary blocker for phase completion.

---

_Verified: 2026-04-10T20:30:00Z_
_Verifier: Claude (gsd-verifier)_
