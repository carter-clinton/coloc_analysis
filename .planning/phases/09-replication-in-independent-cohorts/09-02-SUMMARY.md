---
phase: 09-replication-in-independent-cohorts
plan: 02
subsystem: harmonization
tags: [python, pandas, pyliftover, snakemake, pytest, finngen, gbmi, mvp, bbj, replication]

# Dependency graph
requires:
  - phase: 09-replication-in-independent-cohorts
    provides: "Plan 09-01 — cohort registry (config/replication_cohorts.yaml), 24-rule replication.smk skeleton, test scaffolding"
  - phase: 00-data-access-infrastructure
    provides: "liftover chain file (hg38ToHg19.over.chain.gz), pyliftover env"
  - phase: 02-3-way-qtl-colocalization
    provides: "Phase-2 harmonize_eqtl.py pattern (chunked read, write_harmonized); reuse reference"
provides:
  - "Plan 09-02 — 4 cohort harmonizers (FinnGen R12, GBMI, MVP, BBJ) producing canonical 10-column schema at data/processed/replication/harmonized_grch37/"
  - "Shared sumstats_utils Phase 9 helpers: is_palindromic, filter_palindromic_ambiguous, liftover_to_grch37"
  - "liftover_coordinates single-coordinate helper in src/python/liftover.py (pyliftover-backed, cached)"
  - "validate_replication_sumstats.py canonical-schema + liftover-QC gate"
  - "10 real Snakemake rules in §A+§B (4 download + BBJ zip extract + 4 harmonize + validate) — no TODO markers"
  - "37 passing Phase 9 tests (5 xfailed placeholders for future plans)"
affects: [09-03-manifest-susie-fit, 09-04-coloc-fiqt-meta, 09-05-cojo-aggregate]

# Tech tracking
tech-stack:
  added:
    - "pyliftover — pure-Python UCSC chain lookup for per-coordinate liftover (already installed in smoke_dev env; documented as runtime dep in harmonize_* modules)"
  patterns:
    - "Schema-dispatching harmonizer: single entry point + _detect_schema() + _harmonize_<schema>() sub-functions (harmonize_mvp.py) lets a single module handle both REGENIE-style and dbGaP GWAS-central layouts in the same cohort"
    - "Inline liftover in the harmonizer rule (not a separate Snakemake step) — keeps the DAG leaner and guarantees palindromic filter runs AFTER liftover so the MAF band is applied to GRCh37 coords"
    - "B-2 guard pattern: fail loudly with the expected-vs-observed columns list when an ancestry stratum is missing from a pan-ancestry file (harmonize_gbmi.py); prevents silent empty output breaking the D-05b AFR panel"
    - "sys.path.insert(0, src/python) + flat-name imports as the project convention (matches phase2/phase5 tests); avoids the `from src.python.*` pattern that would require an __init__.py and setup.py"

key-files:
  created:
    - "src/python/harmonize_finngen.py (141 lines)"
    - "src/python/harmonize_gbmi.py (132 lines)"
    - "src/python/harmonize_mvp.py (238 lines)"
    - "src/python/harmonize_bbj.py (137 lines)"
    - "src/python/validate_replication_sumstats.py (61 lines)"
    - "tests/phase9/test_sumstats_utils.py (126 lines, 7 tests)"
    - "tests/phase9/test_harmonize_finngen.py (91 lines, 3 tests)"
    - "tests/phase9/test_harmonize_gbmi.py (50 lines, 4 tests)"
    - "tests/phase9/test_harmonize_mvp.py (113 lines, 6 tests)"
    - "tests/phase9/test_harmonize_bbj.py (108 lines, 7 tests)"
    - ".planning/phases/09-replication-in-independent-cohorts/deferred-items.md (DEF-09-02-01 logged)"
  modified:
    - "src/python/sumstats_utils.py (appended ~125 lines: is_palindromic, filter_palindromic_ambiguous, liftover_to_grch37)"
    - "src/python/liftover.py (added liftover_coordinates + _load_pyliftover cached loader, ~60 lines)"
    - "src/snakemake/rules/replication.smk (replaced 10 placeholder rules with real implementations; removed obsolete liftover_replication_sumstats_grch38_to_37; inserted _build_mvp_pha_index + _mvp_trait/ancestry_from_pha helpers)"

key-decisions:
  - "Schema-dispatching MVP harmonizer supports BOTH REGENIE-style (fixture) AND dbGaP GWAS-central (real phs001672 per Wave-1 correction); _detect_schema() inspects columns and routes to _harmonize_regenie or _harmonize_dbgap"
  - "dbGaP signed BETA reconstructed from |β| + Coded Allele via reconstruct_signed_beta() — sign = +1 when coded == EA, -1 when coded == OA, NaN otherwise (unclassified allele)"
  - "Inline liftover in each harmonizer (not a separate liftover_replication_sumstats rule) — removes one DAG node, guarantees palindromic filter runs on GRCh37 coords"
  - "All 4 harmonizers write to data/processed/replication/harmonized_grch37/ (not harmonized/) — aligns with Plan 09-03 consumer paths that were drafted assuming the post-liftover canonical location"
  - "liftover_coordinates() added to src/python/liftover.py as a pyliftover-backed per-coordinate helper; cached per chain file via functools.lru_cache(maxsize=4) so 100 M-variant datasets don't reload the chain for each row"
  - "Palindromic filter applied AFTER liftover (not before) so MAF-band exclusion operates on post-lift EAF values; matches Phase 2 harmonize_eqtl ordering"
  - "Project-convention imports: sys.path.insert + flat module names (matches phase2 + phase5 tests); the plan's from-src.python.X draft pattern would require __init__.py in src/ and src/python/ which the project deliberately avoids"
  - "GBMI no-liftover rule: flagship releases are GRCh37 natively; harmonize_gbmi emits NO qc.json, and validate_harmonized_sumstats was updated to treat missing QC JSON as a pass (required for GBMI rows to validate)"

patterns-established:
  - "Canonical 10-column schema: CHR BP SNP EA OA BETA SE P EAF N [N_CASES N_CTRLS] palindromic_flag — enforced by validate_replication_sumstats.validate_schema() on a 100-row header slice"
  - "QC JSON sidecar: harmonize_{finngen,mvp,bbj}.py emit a JSON file next to the output TSV with n_input/n_lifted/n_dropped/drop_rate + n_after_palindromic/n_palindromic_dropped — check_liftover_qc(qc_json, max_drop=0.05) enforces the 5% drop-rate ceiling"
  - "TDD RED -> GREEN commit pairs for util-layer task (Task 1); combined RED+GREEN commits for each cohort harmonizer (Tasks 2-5) since the test file and implementation file are written as a pair in the same session"

requirements-completed: []

# Metrics
duration: 11min
completed: 2026-04-14
---

# Phase 09 Plan 02: Ingest + Harmonize All 4 Replication Cohorts

**Four cohort-specific Python harmonizers (FinnGen R12, GBMI, MVP phs001672, BBJ hum0197-v3) converge heterogeneous raw sumstats into a canonical 10-column schema, lift GRCh38→GRCh37 where required, apply a palindromic-ambiguity filter, and emit QC sidecars — the largest data-plumbing wave in Phase 9 and the last one before Plan 09-03 starts consuming canonical inputs.**

## Performance

- **Duration:** ~11 min wall clock (start 03:30:59Z → end 03:42:24Z)
- **Tasks:** 5 / 5 (all real, no checkpoints)
- **Files created:** 11
- **Files modified:** 3
- **Commits:** 7 (6 task commits + 1 RED test commit pre-Task-1 GREEN)
- **Test outcomes:** 27 new phase9 tests added (all pass); 37 total phase9 tests pass + 5 xfailed placeholders for Plans 09-03/04/05

## Accomplishments

- **FinnGen R12 harmonizer** — `harmonize_finngen_sumstats` reads the public GCS tsv.gz, renames to canonical, liftovers GRCh38→GRCh37 via the shared helper, and applies the palindromic filter. N comes from the config case_n + ctrl_n (FinnGen endpoint files have no per-variant N).
- **GBMI harmonizer with B-2 guard** — `harmonize_gbmi_sumstats` uses `ANCESTRY_PREFIX_MAP` to extract per-ancestry columns (`eur → all_meta_*`, `afr → afr_meta_*`, ...). When the requested ancestry's prefix columns are absent (e.g., AFR requested from an EUR-only file), raises `ValueError` listing expected vs observed columns — no silent empty output.
- **MVP dual-schema harmonizer** — `harmonize_mvp_sumstats` inspects columns and dispatches to REGENIE-style (fixture layout) or dbGaP GWAS-central (real phs001672 layout per the Wave-1 correction). dbGaP |β| + Coded Allele orientation is unwound by `reconstruct_signed_beta()` into signed BETA. `log10p_to_pval()` clips LOG10P to [0, 300] before exponentiation per Phase-2 convention.
- **BBJ zip-aware harmonizer** — `extract_bbj_zip()` picks the first `.tsv/.txt` payload and skips README entries (T-09-10 mitigation); `harmonize_bbj_sumstats` then renames + lifts + filters. BBJ is always GRCh38.
- **Shared helpers in sumstats_utils** — `is_palindromic`, `filter_palindromic_ambiguous` (MAF [0.48, 0.52] band drop, tags `palindromic_flag`), `liftover_to_grch37` (hard-fails on drop_rate > 5%).
- **liftover_coordinates** — new per-coordinate helper in `liftover.py` backed by `pyliftover`, cached per chain file via `functools.lru_cache(maxsize=4)`. Replaces the nonexistent signature assumed by the plan draft.
- **Canonical-schema validator** — `validate_replication_sumstats.py` CLI exits 1 on any missing canonical column or drop_rate > max_drop; QC JSON is optional (GBMI emits none).
- **Snakemake rule updates** — 10 real §A/§B rules (4 download + BBJ zip extract + 4 harmonize + 1 validate); the obsolete `liftover_replication_sumstats_grch38_to_37` placeholder has been removed since all 4 harmonizers lift inline. Output paths repointed to `data/processed/replication/harmonized_grch37/` to match Plan 09-03's consumer map.

## Task Commits

1. **RED — failing sumstats_utils tests** — `32571b4` (test)
2. **Task 1 GREEN — sumstats_utils + liftover_coordinates** — `8eb5a7b` (feat)
3. **Task 2 — FinnGen R12 harmonizer + rules** — `527a07b` (feat)
4. **Task 3 — GBMI harmonizer with B-2 guard + rules** — `aab7017` (feat)
5. **Task 4 — MVP dual-schema harmonizer + rules** — `fe46ccb` (feat)
6. **Task 5 — BBJ harmonizer + validator + rules** — `19ff642` (feat)

## Files Created / Modified

See frontmatter `key-files.created` and `key-files.modified` for the full list.

## Decisions Made

- **Dual-schema MVP harmonizer** rather than forking into two modules. `_detect_schema()` is a 3-line column inspection that returns 'regenie' or 'dbgap'; adding a third schema later is a single-line branch. Keeps the operator-facing CLI surface identical (one `harmonize_mvp.py --input FILE`).
- **Inline liftover** (per-harmonizer) instead of a standalone rule. Shrinks the DAG, keeps QC co-located with the harmonized TSV, and guarantees the palindromic filter operates on GRCh37 coords.
- **Repoint harmonize outputs to `harmonized_grch37/`** so Plan 09-03's path resolver (`_resolve_rep_path()`) works without modification. The original `harmonized/` layer had been an artifact of the separate-liftover skeleton.
- **`sys.path.insert` + flat-name imports** over the plan draft's `from src.python.X import Y` pattern. The draft pattern would require adding `__init__.py` to both `src/` and `src/python/` (project deliberately doesn't have these) and reorganising the entire Phase 2/5 test suite. Out of scope for this wave.
- **`pyliftover` for the per-coordinate helper** rather than spawning the UCSC `liftOver` binary per row. The binary path is kept for batch operations in `liftover_sumstats`; the per-row pyliftover path is used inside the DataFrame apply in `liftover_to_grch37`. `lru_cache(maxsize=4)` amortises chain-file load across multiple harmonizer invocations.
- **Palindromic filter *after* liftover** (not before). Keeps the MAF-band test operating on the same coordinate space that downstream coloc will use. Matches Phase 2 harmonize_eqtl ordering.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing functionality] Added `liftover_coordinates` to `src/python/liftover.py`**
- **Found during:** Task 1 implementation.
- **Issue:** The plan draft's `liftover_to_grch37` in sumstats_utils.py calls `from liftover import liftover_coordinates`, but `liftover.py` only shipped `liftover_sumstats` (a batch DataFrame → subprocess UCSC liftOver call). Row-by-row invocation of the subprocess path would spawn 100k+ processes per harmonization — catastrophically slow.
- **Fix:** Added `liftover_coordinates(chain_file, chrom, pos) -> (chrom, pos) | None` using `pyliftover` (already installed in smoke_dev per Phase 2 STATE decision). Chain-file loader cached via `functools.lru_cache(maxsize=4)` so the chain file parses once per Snakemake job.
- **Files modified:** `src/python/liftover.py`
- **Verification:** All 7 sumstats_utils tests pass; harmonize_finngen / _bbj / _mvp liftover QC flows through.
- **Committed in:** `8eb5a7b`

**2. [Rule 1 - Bug] Plan draft's `from src.python.X import Y` imports would fail at runtime**
- **Found during:** Task 1 initial test collection.
- **Issue:** The plan draft used `from src.python.sumstats_utils import ...` style imports throughout. This requires `src/__init__.py` and `src/python/__init__.py`, which the project deliberately does not have (Phase 2 + Phase 5 tests established `sys.path.insert(0, PROJECT_ROOT / "src" / "python")` + flat-name imports as the convention). The draft pattern would ImportError on both library and test import.
- **Fix:** Followed project convention throughout: `sys.path.insert(0, HERE)` at the top of each harmonizer module, `sys.path.insert(0, PROJECT_ROOT / "src" / "python")` in each test file, then `import sumstats_utils as _su` / `from harmonize_finngen import ...`.
- **Files modified:** `src/python/harmonize_{finngen,gbmi,mvp,bbj}.py`, `src/python/sumstats_utils.py`, `src/python/validate_replication_sumstats.py`, `tests/phase9/test_sumstats_utils.py` + 4 harmonizer test files.
- **Verification:** All 37 phase9 tests pass under `pytest tests/phase9` (flat command, no `-p` or `rootdir` gymnastics).
- **Committed in:** `8eb5a7b` (library) + per-task commits for tests.

**3. [Rule 1 - Bug] `pd.read_csv(sep=None, engine='python', low_memory=False)` raises ValueError**
- **Found during:** Task 5, running `test_bbj_canonical`.
- **Issue:** The `low_memory` kwarg is only supported by the C parser; pandas raises `ValueError: The 'low_memory' option is not supported with the 'python' engine` when combined with `sep=None, engine='python'` (which BBJ needs because some zip payloads are whitespace-delimited).
- **Fix:** Removed `low_memory=False` from the BBJ `pd.read_csv` call; added a clarifying comment.
- **Files modified:** `src/python/harmonize_bbj.py`
- **Verification:** All 7 BBJ tests pass.
- **Committed in:** `19ff642`

**4. [Rule 1 - Bug] Plan expected `harmonized/` output path but Plan 09-03 reads `harmonized_grch37/`**
- **Found during:** Task 5, right before finalizing the rule outputs.
- **Issue:** The Wave-1 rule skeleton had two layers (`harmonized/` → `harmonized_grch37/`) connected by a standalone liftover rule. Plan 09-02's plan text wrote Wave-2 harmonizers to the first layer. But Plan 09-03's path resolver (`_resolve_rep_path` in 09-03-PLAN.md Task 1 Step ~161) hard-codes the canonical path as `data/processed/replication/harmonized_grch37/{cohort}/...`. With the standalone liftover rule removed (it's now inline per Fix #3), the harmonizer outputs would never land in the path 09-03 reads from.
- **Fix:** Repointed all 4 `harmonize_*` rule output paths from `harmonized/` → `harmonized_grch37/` so 09-03 consumers work unmodified. Removed the placeholder `liftover_replication_sumstats_grch38_to_37` rule (obsolete — harmonizers lift inline).
- **Files modified:** `src/snakemake/rules/replication.smk`
- **Verification:** `snakemake --list` clean; 10 real §A/§B rules; no TODO markers in those sections.
- **Committed in:** `19ff642`

### Out-of-scope discoveries (NOT fixed — deferred per Scope Boundary rule)

**DEF-09-02-01: Pre-existing Phase 2 test collection failures**
- `tests/phase2/test_negative_controls.py`, `test_pph4_sweep.py`, `test_tier_assignment.py` all fail collection with `ModuleNotFoundError: No module named 'tests'` because they `from tests.phase2.conftest import ...` but the project has no `tests/__init__.py`.
- Confirmed pre-existing via `git stash` reproduction.
- Logged in `.planning/phases/09-replication-in-independent-cohorts/deferred-items.md` with remediation options.

---

**Total deviations:** 4 auto-fixed (3 Rule 1 bugs + 1 Rule 2 missing functionality) + 1 deferred. All 4 fixes were required to make the plan draft executable; none changed the plan's scope or success criteria.

## Issues Encountered

- pandas' `engine='python'` / `low_memory` incompatibility was unexpected given that the C parser handles `low_memory` freely. Removed the kwarg in the BBJ path (one line).
- `src/python/liftover.py`'s existing interface (`liftover_sumstats(df, ...)`) is geared towards one-time batch calls through the UCSC binary. Rather than reroute the harmonizers through it (each harmonizer would need to write a temp CSV, shell out, read the result), I added a co-resident `liftover_coordinates` per-coordinate helper and wired `sumstats_utils.liftover_to_grch37` to that instead.

## User Setup Required

None — all cohort downloads run through public URLs (FinnGen GCS, dbGaP FTP, NBDC BBJ endpoint, GBMI portal). If the GBMI portal starts requiring manual Forms-gate downloads the operator can place the file at `data/raw/replication/gbmi/{trait}_{ancestry}.tsv.gz` manually; the `download_gbmi` rule's shell recipe exits 1 with a clear message pointing to `data_access.md`.

## Next Phase Readiness

Plan 09-03 (manifest + SuSiE fit) can begin immediately. It consumes:
- `data/processed/replication/harmonized_grch37/{cohort}/{trait|trait_endpoint}.tsv.gz` for all 4 cohorts
- `data/processed/replication/harmonized_grch37/{cohort}/{file}.qc.json` for FinnGen + MVP + BBJ (GBMI emits no QC JSON)
- The canonical 10-column schema is stable — Plan 09-03's `_resolve_rep_path()` paths work without modification.

## Self-Check: PASSED

Verified present:
- FOUND: `src/python/harmonize_finngen.py`
- FOUND: `src/python/harmonize_gbmi.py`
- FOUND: `src/python/harmonize_mvp.py`
- FOUND: `src/python/harmonize_bbj.py`
- FOUND: `src/python/validate_replication_sumstats.py`
- FOUND: `src/python/sumstats_utils.py` (with `is_palindromic`, `filter_palindromic_ambiguous`, `liftover_to_grch37`)
- FOUND: `src/python/liftover.py` (with `liftover_coordinates`)
- FOUND: `tests/phase9/test_sumstats_utils.py`
- FOUND: `tests/phase9/test_harmonize_finngen.py`
- FOUND: `tests/phase9/test_harmonize_gbmi.py`
- FOUND: `tests/phase9/test_harmonize_mvp.py`
- FOUND: `tests/phase9/test_harmonize_bbj.py`
- FOUND: `.planning/phases/09-replication-in-independent-cohorts/deferred-items.md`

Verified commits:
- FOUND: `32571b4` (RED sumstats_utils tests)
- FOUND: `8eb5a7b` (Task 1 GREEN)
- FOUND: `527a07b` (Task 2 FinnGen)
- FOUND: `aab7017` (Task 3 GBMI)
- FOUND: `fe46ccb` (Task 4 MVP)
- FOUND: `19ff642` (Task 5 BBJ + validator)

Verified infrastructure:
- `pytest tests/phase9 --tb=short -q` → 37 passed, 5 xfailed (future-plan placeholders)
- `snakemake --list` → clean, 10 real §A/§B rules (4 download + BBJ extract + 4 harmonize + validate)
- `awk '/^# §A/{f=1} /^# §C/{f=0} f' replication.smk | grep -c "TODO plan 09-02"` → 0 (no TODOs remaining in §A/§B)
- `pytest tests/phase5 --tb=short -q` → 100 passed (regression — no Phase 5 breakage)

---
*Phase: 09-replication-in-independent-cohorts*
*Completed: 2026-04-14*
