---
phase: 01-coloc-susie-fine-mapping-spine
plan: 03
plan_id: 01-03
plan_name: "HGDP+1kG AFR LD panel (gnomAD v3.1.2 phased BCFs)"
subsystem: ld_reference
tags: [ld, hgdp, 1kg, afr, plink2, bcftools, wave2b, req-2]
dependency_graph:
  requires:
    - 01-01 (run_susie_rss.R .fit.rds loader, G3_complex regions, susie_policy.yaml)
    - 01-02 (envs/ld_build.yml, LD_BUILD_ENV absolute-path pattern, sidecar .meta.json convention)
  provides:
    - REQ-2 G4 AFR-leg LD source (hgdp_1kg_afr) plumbing
    - build_hgdp_1kg_ld Snakemake rule wired via LD_BUILD_ENV
    - src/snakemake/scripts/build_hgdp_1kg_ld.py (metadata fetch + AFR extraction + BCF slice + plink LD)
    - src/snakemake/scripts/plink_ld_to_rds.R (plink LD text -> .rds, native saveRDS)
    - T-1-02 BCF slice + metadata SHA256 provenance chain
    - T-1-04 AFR ld_source='hgdp_1kg_v3_1_2' in .meta.json
    - Extended pipeline schema (hgdp_1kg block, paths.hgdp_1kg_scratch)
    - AFR sample count test bounds grounded in preflight (950-1010, not plan's nominal ~730)
  affects:
    - Plan 01-04 (coloc.susie consumes AFR .rds once liftover resolves)
    - Plan 01-05 (QC dashboard reads ld_source flag)
    - Plan 01-06 (methods fragment surfaces Scope B + DEF-01-04 liftover gate)
tech_stack:
  added:
    - bcftools=1.21 via envs/ld_build.yml (HTTPS streaming via htslib 1.22 verified in preflight)
    - plink2 via envs/ld_build.yml (multi-flag fallback: --r-phased / --r2-phased / --r2)
  patterns:
    - "Anonymous HTTPS BCF streaming: curl -sL + bcftools view -r chr22:... <bucket-url>"
    - "plink2 LD output locator handles .phased.vcor / .phased.vcor2 / .vcor / .ld extension drift across plink2 builds"
    - "Sample-id reconciliation via BCF header (bcftools query -l) with prefix-variant fallback loop (Pitfall 3 defensive)"
    - "data.table::fread strict numeric coercion for plink LD text; NA rejection before saveRDS (T-1-02b)"
    - "lambda-wrapped params values to prevent Snakemake from misreading '{chrom}' template as a wildcard"
    - "Independent HGDP_REGION_INFOS autosome filter (not reused from UKBB_LD_REGION_INFOS per handoff note 5)"
key_files:
  created:
    - src/snakemake/scripts/build_hgdp_1kg_ld.py
    - src/snakemake/scripts/plink_ld_to_rds.R
    - .planning/phases/01-coloc-susie-fine-mapping-spine/01-03-scope-decision.md
    - .planning/phases/01-coloc-susie-fine-mapping-spine/wave2b_preflight.log
  modified:
    - src/snakemake/rules/ld_reference.smk
    - src/snakemake/schemas/pipeline.schema.yaml
    - config/pipeline.yaml
    - tests/phase1/test_ld_panels.py
    - .planning/phases/01-coloc-susie-fine-mapping-spine/deferred-items.md
decisions:
  - "Scope B chosen (11 autosomal curated regions; BMI_Xq24 excluded because HGDP+1kG v2 chrX uses a separate BCF triplet). Compute is NOT the binding constraint -- the real 22-autosome footprint is ~17 GB vs plan's 100 GB worst case -- but the GRCh38/GRCh37 genome-build deviation IS: curated regions are GRCh37 while the v2 BCFs are GRCh38 (DEF-01-04 tracks the liftover requirement)."
  - "Metadata URL corrected to release/3.1/secondary_analyses/hgdp_1kg/metadata_and_qc/gnomad_meta_v1.tsv (plan's pre-spec release/3.1.2/pca/gnomad.v3.1.2.hgdp_tgp_meta.tsv returns HTTP 404 -- verified against 5 URL variants in preflight step 1b/1h)."
  - "Region column is hgdp_tgp_meta.Genetic.region (dot-separated Hail export), NOT genetic_region as plan pre-spec assumed."
  - "AFR sample count: 1003 in metadata, 986 in chr22 BCF after reconciliation. Plan's nominal ~730 was a legacy 1kG-only figure. Task 1-03-03 test bounds widened to 950-1010."
  - "Sample IDs match BCF header directly (HGDP00xxx, NA, LP, SS prefixes) -- no HGDP_/1KG_ prefix mapping required. Pitfall 3 fallback loop retained defensively for future BCF re-releases."
  - "Scratch default /rs1/researchers/c/ckclinto/hgdp_1kg_scratch (29 TB) because /rs1/scratch does not exist on this cluster (pattern inherited from Plan 01-02)."
  - "Independent HGDP_REGION_INFOS construction (not reusing UKBB_LD_REGION_INFOS) per Wave 2b handoff note 5, so future UKBB scope changes cannot silently alter AFR coverage."
  - "plink_ld_to_rds.R uses native saveRDS (no pyreadr on R side) per handoff note 6."
  - "lambda-wrapped params in the rule so '{chrom}' in the BCF filename template is not misread as a Snakemake wildcard -- first dry-run raised WildcardError; fix was straightforward."
metrics:
  completed: "2026-04-12"
  duration_min: 19
  tasks_completed: 4
  commits: 4
---

# Phase 1 Plan 03: HGDP+1kG AFR LD panel (gnomAD v3.1.2 phased BCFs) Summary

**One-liner:** Lands HGDP+1kG AFR LD panel plumbing -- bcftools HTTPS BCF streaming driver, plink2 multi-flag LD caller with plink-version-tolerant output locator, native-R plink-text -> .rds converter, new Snakemake rule wired via LD_BUILD_ENV, config + schema + test bound extensions (AFR 950-1010) -- all dry-run-gated; real execution is explicitly gated on GRCh38 liftover of regions_curated.csv (DEF-01-04).

## Deliverables

### New files (4)

| File | Purpose |
|---|---|
| `src/snakemake/scripts/build_hgdp_1kg_ld.py` | 424-line driver: metadata TSV fetch, AFR sample extraction with Pitfall 3 prefix fallback, bcftools HTTPS region slicing, plink2 LD (tries `--r-phased` / `--r2-phased` / `--r2` in order), plink output locator (handles `.phased.vcor` / `.phased.vcor2` / `.vcor` / `.ld`), SHA256 provenance per slice + metadata, sidecar `.meta.json` writer with `ld_source='hgdp_1kg_v3_1_2'`, `--dry-run` mode, `safe_region_id` sanitizer (T-1-03) |
| `src/snakemake/scripts/plink_ld_to_rds.R` | Small R helper: `data.table::fread` strict numeric parsing, symmetry enforcement, NA rejection (T-1-02b), `.pvar` vs `.bim` variant-file dispatch, native `saveRDS` (no pyreadr R-side dependency) |
| `.planning/phases/01-coloc-susie-fine-mapping-spine/01-03-scope-decision.md` | Scope B pilot decision with empirical budget table, 11-region selection rationale, and DEF-01-04 pointer |
| `.planning/phases/01-coloc-susie-fine-mapping-spine/wave2b_preflight.log` | Preflight record: metadata URL discovery (plan's 404'd), column-name hunt, AFR sample count (1003/986), BCF HTTPS streaming via bcftools 1.22 verified, contig naming (chr22 GRCh38), full summary |

### Modified files (5)

| File | Change |
|---|---|
| `src/snakemake/rules/ld_reference.smk` | Adds `HGDP_1KG_SCRATCH`, `HGDP_1KG_OUT_DIR`, `HGDP_REGION_INFOS` (autosome filter built independently of UKBB's), and the `build_hgdp_1kg_ld` rule using `LD_BUILD_ENV` absolute-path conda directive |
| `config/pipeline.yaml` | Adds `hgdp_1kg` block (bucket, template, metadata_url, region_column, sample_column, genome_build, expected_afr_n_min/max), adds `paths.hgdp_1kg_scratch`, flips `ld_reference.AFR_source` from `onekg_phase3` to `hgdp_1kg_afr` |
| `src/snakemake/schemas/pipeline.schema.yaml` | Adds `hgdp_1kg` top-level + `paths.hgdp_1kg_scratch` so `additionalProperties: false` stays enforced |
| `tests/phase1/test_ld_panels.py` | Adds `test_hgdp_afr_sample_count` with bounds 950-1010 + `ld_source='hgdp_1kg_v3_1_2'` guard |
| `.planning/phases/.../deferred-items.md` | Adds DEF-01-04 (GRCh38 liftover blocker) and DEF-01-05 (pre-existing TRANS.samples missing input) |

## Commits

| SHA | Message |
|---|---|
| `b37468a` | `chore(01-03): Wave 2b preflight -- verify HGDP+1kG v2 bucket + metadata schema` |
| `bd4ff8a` | `docs(01-03): scope decision -- Scope B pilot (11 autosomal regions)` |
| `2883693` | `feat(01-03): wire HGDP+1kG AFR LD panel downloader + rule + config` |
| `74ac9f8` | `test(01-03): add AFR sample count + ld_source assertion to test_ld_panels.py` |

Previous commit (plan base): `e3592f7 docs(01-02): complete UKBB-LD tiled EUR panel plan`.

## Wave 2b verification gates

| Gate | Result | Evidence |
|---|---|---|
| `build_hgdp_1kg_ld` rule present in `ld_reference.smk` | PASS | `grep -q build_hgdp_1kg_ld` -> 0 |
| Rule uses `LD_BUILD_ENV` absolute-path conda directive | PASS | `grep -q "conda: LD_BUILD_ENV"` -> 0 (via `conda: LD_BUILD_ENV` block) |
| Preflight records AFR sample count | PASS | `AFR_N_IN_BCF: 986` in `wave2b_preflight.log` step 8 (plan's ~730 spec was incorrect legacy 1kG-only figure -- reconciled test bounds to 950-1010 in Task 1-03-03) |
| `01-03-scope-decision.md` committed with chosen scope + rationale | PASS | Scope B box checked, empirical budget + 11-region selection + DEF-01-04 pointer documented; commit `bd4ff8a` |
| `test_ld_panels.py` still collects | PASS | `pytest --collect-only` -> 3 items |
| `test_hgdp_afr_sample_count` present | PASS | `grep` + pytest discovery |
| Snakemake dry-run resolves `build_hgdp_1kg_ld` in DAG (without `--use-conda` per DEF-01-01) | PASS | `snakemake --snakefile Snakefile --dry-run build_hgdp_1kg_ld` -> 11 autosomal regions resolve (BMI_Xq24 excluded); `snakemake --snakefile tests/toy_3locus/Snakefile.test --dry-run build_hgdp_1kg_ld` -> 3 toy regions resolve |
| `python -m py_compile build_hgdp_1kg_ld.py` | PASS | exit 0 |
| `Rscript -e 'parse(plink_ld_to_rds.R)'` | PASS | exit 0 |
| JSON schema validation of `config/pipeline.yaml` against extended `pipeline.schema.yaml` | PASS | `jsonschema.Draft7Validator(schema).iter_errors(cfg)` -> empty |

All 9 gates PASS. Result: **DONE**.

## Deviations from Plan

### Auto-fixed (Rule 1 + Rule 2 -- preflight-driven corrections)

**1. [Rule 1 - Bug] Metadata URL was wrong in plan pre-spec**
- **Found during:** Task 1-03-00 preflight step 1
- **Issue:** Plan's metadata URL `https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/pca/gnomad.v3.1.2.hgdp_tgp_meta.tsv` returns HTTP 404. Tried 5 URL variants; all 404.
- **Fix:** Bucket exploration (step 1d/1h) located the actual file at `release/3.1/secondary_analyses/hgdp_1kg/metadata_and_qc/gnomad_meta_v1.tsv`. HTTP 200, 5.7 MB, 4150 sample rows. `build_hgdp_1kg_ld.py` `META_URL` constant uses the verified path; config `hgdp_1kg.metadata_url` mirrors it.
- **Files modified:** `src/snakemake/scripts/build_hgdp_1kg_ld.py`, `config/pipeline.yaml`
- **Commit:** `b37468a` (preflight) + `2883693` (script)

**2. [Rule 1 - Bug] Region column name was wrong in plan pre-spec**
- **Found during:** Task 1-03-00 preflight step 4
- **Issue:** Plan assumed column `genetic_region`. Actual metadata is Hail-exported with dot-separated column names; the correct column is `hgdp_tgp_meta.Genetic.region`.
- **Fix:** Updated `DEFAULT_REGION_COL` in `build_hgdp_1kg_ld.py` and `hgdp_1kg.region_column` default in `config/pipeline.yaml` + schema.
- **Commit:** `2883693`

**3. [Rule 1 - Bug] AFR sample count expected range was wrong**
- **Found during:** Task 1-03-00 preflight step 5
- **Issue:** Plan specified test bounds `700 <= n <= 770` with nominal ~730. Actual v2 panel has 1003 AFR in metadata and 986 reconciled against chr22 BCF header. 730 was an older 1kG-Africa-only figure; the combined HGDP+1kG panel is substantially larger.
- **Fix:** Task 1-03-03 test bounds widened to `950 <= n <= 1010`. `config/pipeline.yaml` records `expected_afr_n_min: 950`, `expected_afr_n_max: 1010`.
- **Files modified:** `tests/phase1/test_ld_panels.py`, `config/pipeline.yaml`
- **Commit:** `2883693` + `74ac9f8`

**4. [Rule 3 - Blocking] Snakemake wildcard error on `{chrom}` in params**
- **Found during:** First dry-run of `build_hgdp_1kg_ld`
- **Issue:** `params.bcf_template = "hgdp1kgp_chr{chrom}.filtered..."` caused `WildcardError: Wildcards in params cannot be determined from output files`. Snakemake interprets brace-curlies in `params` as wildcards.
- **Fix:** Wrapped each `params` value in `lambda wildcards: config.get(...)` so the `{chrom}` token is only resolved at script-runtime inside the Python driver.
- **Files modified:** `src/snakemake/rules/ld_reference.smk`
- **Commit:** `2883693`

**5. [Rule 2 - Safety] `--force-samples` on bcftools view**
- **Found during:** Task 1-03-02 script authoring
- **Issue:** Plan's bcftools command did not pass `--force-samples`. With the v2 BCF header mismatch (some metadata samples not in BCF), a strict `-S` would abort. Reconciliation now happens pre-flight in Python, but `--force-samples` is added as a defensive belt-and-suspenders.
- **Commit:** `2883693`

**6. [Rule 2 - Safety] plink2 output file locator**
- **Found during:** Task 1-03-02 script authoring
- **Issue:** Plan hardcoded `.phased.vcor2` which is only produced by certain plink2 builds. Real plink2 emits `.phased.vcor`, `.phased.vcor2`, `.vcor`, or `.ld` depending on version + flag combination.
- **Fix:** Added `locate_plink_ld_output` + `locate_plink_variants` helpers that probe extension variants in order. This avoids a silent `FileNotFoundError` on first real execution.
- **Commit:** `2883693`

### Architectural (Rule 4 -- paused, deferred)

**7. [Rule 4 - Architectural] GRCh37/GRCh38 genome build mismatch**
- **Found during:** Task 1-03-00 preflight step 13
- **Issue:** HGDP+1kG v2 BCFs declare `##contig=<ID=chr22>` (GRCh38). `config/pipeline.yaml` declares `genome_build: GRCh37` and `config/regions_curated.csv` holds GRCh37 coordinates. Real per-region LD builds cannot execute end-to-end until this is resolved via UCSC liftOver (or per-panel coordinate translation).
- **Why not fixed:** This is architectural -- requires a new liftover stage, schema extensions, policy for mixing builds across panels, and affects every downstream plan that consumes LD. Plan 01-03 is a plumbing plan, not a data-build plan.
- **Captured as:** **DEF-01-04** in `.planning/phases/01-coloc-susie-fine-mapping-spine/deferred-items.md`; cross-referenced from `01-03-scope-decision.md` rationale. Resolution targeted at Plan 01-04 or 01-05.
- **Does NOT block plan completion** -- the plan explicitly requires plumbing and dry-run gating, not real LD builds.

### Out-of-scope discoveries (logged, not fixed)

**DEF-01-05 (new):** Legacy `build_ld_rds` rule fires for `TRANS` ancestry without a `TRANS.samples` file, breaking all-target `snakemake --dry-run`. Verified pre-existing via `git stash` reproduction. Does NOT block the `build_hgdp_1kg_ld` single-rule dry-run (which is what the plan verify gate requires). Logged in `deferred-items.md` for Plan 01-04+.

## Known Stubs

None. All files carry real, executable content gated on the documented DEF-01-04 liftover, not placeholder data.

## Threat Flags

None. New surface is all within `<threat_model>` T-1-02, T-1-02b, T-1-03, T-1-04 dispositions already declared in the plan; mitigations are implemented:
- T-1-02: SHA256 per BCF slice + metadata, recorded in sidecar
- T-1-02b: data.table::fread strict numeric + NA rejection in plink_ld_to_rds.R
- T-1-03: `safe_region_id` regex sanitizer with '/' and '..' rejection
- T-1-04: `ld_source='hgdp_1kg_v3_1_2'` in every sidecar .meta.json

## Self-Check: PASSED

**Files verified (9/9):**
- FOUND: src/snakemake/scripts/build_hgdp_1kg_ld.py
- FOUND: src/snakemake/scripts/plink_ld_to_rds.R
- FOUND: src/snakemake/rules/ld_reference.smk
- FOUND: config/pipeline.yaml
- FOUND: src/snakemake/schemas/pipeline.schema.yaml
- FOUND: tests/phase1/test_ld_panels.py
- FOUND: .planning/phases/01-coloc-susie-fine-mapping-spine/01-03-scope-decision.md
- FOUND: .planning/phases/01-coloc-susie-fine-mapping-spine/wave2b_preflight.log
- FOUND: .planning/phases/01-coloc-susie-fine-mapping-spine/deferred-items.md

**Commits verified (4/4):**
- FOUND: b37468a
- FOUND: bd4ff8a
- FOUND: 2883693
- FOUND: 74ac9f8
