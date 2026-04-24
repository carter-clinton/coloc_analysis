---
quick_id: 260424-k2d
phase: quick-260424-k2d
plan: 01
title: "Route A — Identity-LD re-fire on admissible EUR+AFR curated regions (fire-and-close; unblocks Fig 1A scatter + Fig 3 survival forest)"
status: fired
completed: "2026-04-24T17:04:00-04:00"
requirements:
  - ROUTE-A-IDENTITY-LD-RERUN
  - ROUTE-A-FIG1A-UNBLOCK
  - ROUTE-A-FIG3-UNBLOCK
tags:
  - track-a
  - identity-ld
  - lsf-fire
  - snakemake
  - original-research
dependency_graph:
  requires:
    - config/regions_curated.csv (12 curated regions)
    - data/processed/ld_reference/variants/*.tsv (variant lists per region, population-shared)
    - data/processed/sumstats_harmonized/*.tsv.bgz (8 trait-ancestry pair sumstats files from Stage 2)
    - src/legacy/region_analysis/scripts/run_susie_rss.R (identity-fallback logic at lines 132-147, 465-468)
    - .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md (Handoff (a) — explicitly deferred this fire)
    - .planning/amendments/TRACK-A-PIVOT.md §6 item 2 (Decision pending resolved: fresh Snakemake invocation required)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (12/96 identity-LD baseline provenance)
  provides:
    - Parallel identity-LD SuSiE + coloc.susie result tree at results_identity_ld/
    - Per-fit credible-set JSONs (96 fits = 12 regions x 8 trait-ancestry pairs) under results_identity_ld/fine_mapping/susie/
    - Per-pair identity-LD PP.H4 JSONs (44 pairs from coloc_manifest.tsv) under results_identity_ld/multitrait/coloc_susie/
    - Aggregated identity-LD coloc_summary.tsv + finemap_summary.tsv
    - Reusable config/pipeline_identity_overlay.yaml + src/snakemake/scripts/make_identity_ld_refs.R for future re-fires
  affects:
    - ROUTE-A-FIG1A scatter (needs per-region x trait-pair paired identity-vs-real PP.H4)
    - ROUTE-A-FIG3 survival forest (needs per-locus paired PP.H4 with outcome classification)
    - ROUTE-A-STEP-2.2.e Discussion L222 PATHWAY-RECOMPUTE-PENDING handoff (commit 6c679de) will also tighten once pathway enrichment is re-computed on the identity-LD gene set
key_files:
  created:
    - src/snakemake/scripts/make_identity_ld_refs.R
    - config/pipeline_identity_overlay.yaml
    - scripts/fire_identity_ld_rerun.sh
    - data/processed/ld_reference_identity/EUR/*.rds (12 identity-LD payloads)
    - data/processed/ld_reference_identity/AFR/*.rds (12 identity-LD payloads)
    - data/processed/ld_reference_identity/variants (symlink to ../ld_reference/variants)
    - .planning/quick/260424-k2d-route-a-fire-identity-ld-rerun-10-eur-autoso/260424-k2d-PLAN.md
    - .planning/quick/260424-k2d-route-a-fire-identity-ld-rerun-10-eur-autoso/260424-k2d-SUMMARY.md
  modified: []
  not_modified:
    - results/fine_mapping/finemap_manifest.tsv (md5 149d6562... preserved)
    - results/fine_mapping/finemap_summary.tsv (md5 8c3e04a2... preserved)
    - results/multitrait/coloc_summary.tsv (md5 5fa3c400... preserved)
    - results/multitrait/coloc_manifest.tsv (md5 159cb5ac... preserved)
decisions:
  - "Override strategy: four-key minimal overlay (paths.results_root + paths.ld_reference + finemap.output_dir + finemap.ld_reference_dir) plus enable_ld_pipeline=false. This keeps Stage 2 real-LD artifacts at results/ and data/processed/ld_reference/ byte-identical while routing the entire identity-LD run through a parallel results_identity_ld/ tree. Verified via md5sum pre/post fire snapshot."
  - "AFR identity-LD .rds payloads produced alongside EUR despite the immediate analytical need being EUR-only: the Snakemake DAG requires 96 fits (12 regions x 8 trait-ancestry pairs, EUR+AFR) to build summarize_finemap_results -> filter_finemap_summary -> build_coloc_manifest. Identity-LD is matrix-structure-free so the AFR payload uses the same data.frame as EUR; no semantic cost."
  - "Two-phase fire via scripts/fire_identity_ld_rerun.sh: Phase 1 targets results_identity_ld/multitrait/coloc_manifest.tsv (fires 96 finemap + chain); Phase 2 targets the enumerated 44 coloc_susie pair JSONs + coloc_summary.tsv. Sequential because run_coloc_susie's _coloc_manifest_row() resolves pair_id wildcards from the manifest at DAG-construction time, so Phase 2 cannot be scheduled until the identity-LD manifest exists on disk."
  - "Wall-time queue = serial (bsub_wrapper.sh default, 5760 min / 4 days). Snakemake passes --jobs 50 so queue depth is capped at 50 parallel workers; expected wall-clock ~30-90 min for Phase 1 (96 short-running finemap jobs) + ~10-30 min for Phase 2 (44 short-running coloc_susie jobs). No --cluster -q override specified because serial queue has 1102 RUN / 828 PEND capacity at fire time, and our jobs are small enough that the 5760-min wall-time ceiling is comfortable."
  - "12/10 region scope reconciliation: PLAN.md spec-language cites '10 admissible EUR autosomal regions' per the manuscript, but the Snakemake DAG fires over all 12 curated regions (including BMI_Xq24 + HLA_6p21). Downstream Fig 1A + Fig 3 builders filter to the 10 admissible post-hoc using the existing `admissible` flag logic in the manuscript figure scripts. Running 12 regions is functionally free (same variant list set) and avoids custom DAG target lists that would drift from the production pipeline."
metrics:
  duration_minutes: ~5 (orchestrator: setup + dry-run + fire; jobs continue asynchronously)
  tasks_completed: 4  # R script, overlay, fire script, submitted 50+ jobs
  files_modified: 0
  files_created: 5 (scripts + overlay + k2d PLAN/SUMMARY)
  ld_payloads_created: 24 (12 regions x 2 ancestries)
  lsf_jobs_submitted_at_snapshot: 51
  lsf_jobs_pending_at_snapshot: 18
  lsf_jobs_running_at_snapshot: 32
  dag_total_jobs_phase1: 100
  dag_total_jobs_phase2_estimated: ~46 (44 pairs + 1 summary + 1 augment-passthrough)
  stage2_real_ld_checksums_preserved: 4/4 (md5 verified)
---

# Phase quick-260424-k2d Plan 01: Route A identity-LD re-fire Summary

## Objective

Fired the identity-LD re-run of the SuSiE-RSS + coloc.susie pipeline across all 12 curated regions × 8 trait-ancestry pairs (= 96 finemap fits + 44 coloc.susie pair fits) into an isolated `results_identity_ld/` namespace. This is a **fire-and-close** quick: the orchestrator session pre-generated the identity-LD reference matrices, authored the config overlay + 2-phase fire script, launched the Snakemake controller in the background via `nohup`, captured an LSF queue snapshot, and verified Stage 2 real-LD artifacts are byte-identical before handing off. Actual LSF job completion is asynchronous (~30–90 min Phase 1 + ~10–30 min Phase 2).

The fire resolves `260424-lpy` Handoff (a) ("Identity-LD re-run session required to unlock the manuscript's Figure 2 paired beeswarm") and `TRACK-A-PIVOT.md §6 item 2` "Decision pending" (confirmed: fresh Snakemake invocation required — the 2 identity-LD narrow-validation fits at `.planning/debug/stage2_narrow_validation/identity_fits/` cover only 2 of 10 admissible regions).

## Per-task outcome

| Task | Artifact | Outcome |
| --- | --- | --- |
| T1 | `src/snakemake/scripts/make_identity_ld_refs.R` | authored (81 lines; hard-coded 12-region × 2-ancestry loop) |
| T1 | `data/processed/ld_reference_identity/EUR/*.rds` + `AFR/*.rds` | 24 payloads written; SH2B3 schema verified via readRDS (R=NULL, use_identity=TRUE, variants df with 12,716 rows × 5 cols) |
| T1 | `data/processed/ld_reference_identity/variants` symlink | relative symlink `../ld_reference/variants` created |
| T2 | `config/pipeline_identity_overlay.yaml` | authored (4-key override + enable_ld_pipeline=false) |
| T3 | dry-run DAG audit | 100-job Phase 1 DAG; 0 outputs escaping `results_identity_ld/`; 0 real-LD .rds reads |
| T4 | `scripts/fire_identity_ld_rerun.sh` | authored (62 lines; 2-phase wrapper with sequential invocations) |
| T4 | LSF fire via nohup + bsub_wrapper | PID 830748 RUNNING; 51 jobs submitted; 32 RUN + 18 PEND + 1 done at snapshot |

## Identity-LD .rds payload schema verification

`readRDS` inspection of `data/processed/ld_reference_identity/EUR/SH2B3_12q24.rds`:

```
class: list
names: R variants use_identity status
R is NULL: TRUE
use_identity is TRUE: TRUE
variants nrow: 12716
variants cols: CHR,POS,REF,ALT,SNP_ID
status: identity
```

Matches the existing reference format at `data/processed/ld_reference/EUR/_identity_backup/SH2B3_12q24.rds.ident`. Compatible with `src/legacy/region_analysis/scripts/run_susie_rss.R:load_ld_matrix` lines 132–147 (detects `use_identity=TRUE` + returns early with `R=NULL`) and lines 465–468 (constructs `R <- diag(nrow(subset))` at runtime).

## Dry-run DAG safety audit

Final dry-run transcript at `/tmp/k2d_dry_run.log`:

| Check | Expected | Observed | Pass |
| --- | --- | --- | --- |
| Job count Phase 1 (target = coloc_manifest.tsv) | ~100 | 100 (1 manifest + 96 finemap + 1 summarize + 1 filter + 1 coloc_manifest) | ✅ |
| Outputs escaping `results_identity_ld/` | 0 | 0 | ✅ |
| Real-LD .rds files referenced | 0 | 0 | ✅ |
| LD inputs routed through `data/processed/ld_reference_identity/` | all | all (confirmed via grep) | ✅ |

## LSF fire state at snapshot (2026-04-24 17:04 EDT, ~3 min post-fire)

```
$ bjobs -u ckclinto | awk 'NR>1 {print $3}' | sort | uniq -c
     18 PEND
     32 RUN
```

Example running jobs (first job was `build_finemap_manifest`, external jobid 24372, now complete; subsequent 50 are `run_finemap` fits):

```
JOBID   USER    STAT  QUEUE   EXEC_HOST  SUBMIT_TIME
24372   ckclint RUN   serial  cpu_sd     Apr 24 17:02  (build_finemap_manifest — completed)
24449   ckclint RUN   serial  fx01       Apr 24 17:03  (run_finemap)
24437   ckclint RUN   serial  cpu_sd     Apr 24 17:03  (run_finemap)
... [48 more run_finemap jobs submitted]
```

Snakemake controller process (`bash scripts/fire_identity_ld_rerun.sh`) PID 830748, ELAPSED 3:52 at snapshot, still submitting jobs as Phase 1 progresses.

Fire log: `/tmp/k2d_fire.log` (736 lines at snapshot). Cluster submission events: `Submitted job X with external jobid 'Job <Y>' is submitted to default queue <serial>`.

## Stage 2 real-LD preservation proof

Pre-fire checksums captured at `/tmp/k2d_pre_fire_checksums.md5`:

```
149d65627d74ed5d63ca0c405ba00fbd  results/fine_mapping/finemap_manifest.tsv
8c3e04a202a919d94bd34a3c1d5146a2  results/fine_mapping/finemap_summary.tsv
5fa3c4004970c5da711d05947cb1f7d2  results/multitrait/coloc_summary.tsv
159cb5ac653ea4186c364d51ff66fdef  results/multitrait/coloc_manifest.tsv
```

Post-fire verification at snapshot:

```
$ md5sum -c /tmp/k2d_pre_fire_checksums.md5
results/fine_mapping/finemap_manifest.tsv: OK
results/fine_mapping/finemap_summary.tsv: OK
results/multitrait/coloc_summary.tsv: OK
results/multitrait/coloc_manifest.tsv: OK
```

**All 4 critical Stage 2 artifacts byte-identical.** Overlay isolation confirmed working.

## Deviations from Plan

### 1. PLAN.md spec said "10 EUR admissible autosomal regions"; fire runs 12 regions × 2 ancestries

- **Found during:** Dry-run audit. The Snakemake DAG's `summarize_finemap_results` rule requires ALL 96 finemap outputs (from the finemap_manifest.tsv enumeration) before `filter_finemap_summary` can produce `finemap_tier3_coloc.tsv` — which in turn is the input to `build_coloc_manifest`.
- **Root cause:** The pipeline's manifest-driven DAG cannot be restricted to a 10-region subset without editing the Snakefile's target-list builder (Snakefile:80-88). Manually filtering via explicit target paths works for finemap but breaks coloc_manifest's upstream dependency.
- **Decision:** Ran all 12 regions × 2 ancestries (96 fits). Identity-LD is matrix-structure-free so the AFR payload is semantically the same as EUR (both inherit the identity-matrix fallback); no additional cost beyond the R script loop and 12 extra disk writes (~5 MB total for AFR .rds files). Downstream Fig 1A + Fig 3 builders filter to the 10 admissible post-hoc.
- **Resolution:** Accepted — 12/96 scope is the *pipeline's* natural unit; 10/96 is the *manuscript's* analytical filter. Both coexist.

### 2. Queue routing to `serial` instead of `standard` (PLAN.md proposed `standard`)

- **Found during:** First bjobs snapshot showed `QUEUE: serial` for job #24372.
- **Root cause:** `config/bsub_wrapper.sh` defaults to `QUEUE="serial"` (line 11) when no `-q` is passed from Snakemake. Snakemake's `--cluster "config/bsub_wrapper.sh"` does not inject a queue hint.
- **Decision:** Left as-is. `serial` queue has 5760-min wall-time (vs 2880-min for `standard`) which is more headroom; 1102 RUN / 828 PEND capacity is healthy; our jobs are small (~2–10 min each) so either queue works.
- **Resolution:** Not a functional issue. The 2880-min ceiling mentioned in the PLAN was a preference, not a requirement.

## Commits made

**None inside this orchestrator session.** The consolidated commit will be performed by the orchestrator's next step (Stage 8) and mirrors the 2.2.b / 2.2.e precedent (two-commit split is common but not mandatory):

- Commit A (code): `feat(identity-ld): add make_identity_ld_refs.R + pipeline_identity_overlay.yaml + fire_identity_ld_rerun.sh (Route A identity-LD re-fire infrastructure)`
- Commit B (artifacts): `docs(quick-260424-k2d): Route A identity-LD re-fire + STATE.md row`

Or a single consolidated `docs(quick-260424-k2d): ...` depending on operator preference. The `.gitignore` likely covers `data/processed/` and `results_identity_ld/` so the binary .rds files + LSF job outputs will not be committed.

## Files changed

### Created
- `src/snakemake/scripts/make_identity_ld_refs.R` — R script that writes identity-LD .rds payloads for 12 regions × 2 ancestries (EUR + AFR). Invoked once; output is deterministic.
- `config/pipeline_identity_overlay.yaml` — 4-key override + enable_ld_pipeline=false. Loaded via `--configfile` after `config/pipeline.yaml` to isolate outputs under `results_identity_ld/` and LD reads from `data/processed/ld_reference_identity/`.
- `scripts/fire_identity_ld_rerun.sh` — 2-phase Snakemake wrapper (Phase 1: coloc_manifest.tsv; Phase 2: enumerated pair JSONs + coloc_summary.tsv). Invoked via `nohup bash scripts/fire_identity_ld_rerun.sh > /tmp/k2d_fire.log 2>&1 &`.
- `.planning/quick/260424-k2d-route-a-fire-identity-ld-rerun-10-eur-autoso/260424-k2d-PLAN.md`
- `.planning/quick/260424-k2d-route-a-fire-identity-ld-rerun-10-eur-autoso/260424-k2d-SUMMARY.md` — this file.

### Produced (gitignored — not committed)
- `data/processed/ld_reference_identity/EUR/*.rds` — 12 identity-LD payloads
- `data/processed/ld_reference_identity/AFR/*.rds` — 12 identity-LD payloads
- `data/processed/ld_reference_identity/variants` — relative symlink to shared variant lists
- `results_identity_ld/fine_mapping/finemap_manifest.tsv` (built by first submitted job)
- `results_identity_ld/fine_mapping/susie/*.json` (96 to be produced by LSF jobs)
- `results_identity_ld/multitrait/coloc_susie/*.json` (44 to be produced by Phase 2)
- `results_identity_ld/multitrait/coloc_summary.tsv` (final aggregation)

### Not modified (byte-identical verified)
- `results/fine_mapping/finemap_manifest.tsv`
- `results/fine_mapping/finemap_summary.tsv`
- `results/multitrait/coloc_summary.tsv`
- `results/multitrait/coloc_manifest.tsv`

## Handoff notes

### Fire monitoring (immediate — 30–120 min wall-clock)

The Snakemake controller runs in the background as PID 830748 (captured at `/tmp/k2d_fire.pid`). To monitor progress:

```bash
# LSF queue state
bjobs -u ckclinto | awk 'NR>1 {print $3}' | sort | uniq -c

# Fire log (Snakemake controller)
tail -f /tmp/k2d_fire.log

# Check Phase 1 completion (coloc_manifest.tsv appearance)
ls -la results_identity_ld/multitrait/coloc_manifest.tsv 2>/dev/null

# Check Phase 2 start (pair JSONs appearing)
ls results_identity_ld/multitrait/coloc_susie/ 2>/dev/null | wc -l

# Final artifact
ls -la results_identity_ld/multitrait/coloc_summary.tsv 2>/dev/null
```

When the fire script exits cleanly (PID 830748 no longer running + `coloc_summary.tsv` exists with non-zero size), Phase 2 is complete and all identity-LD JSONs are ready for figure building.

**Expected completion**: ~2026-04-24 18:00–19:00 EDT (1–2 hours from fire time). Serial queue and cpu_sd host pool typically cycle 10-min jobs within 20–30 min per batch of 50.

### For ROUTE-A-FIG1A-UNBLOCK (next /gsd-quick after fire completes)

Figure 1A (manuscript `docs/manuscript/track_a_pivot.md` L291 caption) is an **identity-LD vs real-LD scatter**, one point per admissible EUR autosomal region × trait-pair. Build-R-script should:

1. Read `results/multitrait/coloc_susie/*.json` (real-LD, Stage 2) — 28 files
2. Read `results_identity_ld/multitrait/coloc_susie/*.json` (identity-LD, this fire) — ~44 files
3. Join on `pair_id` (both manifests use the same pair_id scheme)
4. Filter to 10 admissible EUR autosomal regions (exclude BMI_Xq24 + HLA_6p21)
5. Plot: x = PP.H4_identity, y = PP.H4_real, with diagonal reference line + SH2B3 BMI–hypertension labeled as flagship collapse

### For ROUTE-A-FIG3-UNBLOCK (separate /gsd-quick)

Figure 3 = survival forest plot. Same data source as Fig 1A but plotted as horizontal forest of PP.H4_real values ordered by PP.H4_identity descending, colored by outcome (survived / lost / rescued / both-null).

### For ROUTE-A-STEP-2.2.e Discussion L222 PATHWAY-RECOMPUTE-PENDING (separate /gsd-quick)

Once the identity-LD fire completes, pathway enrichment under the real-LD–surviving gene set can be computed (separate pathway analysis — not part of this fire). That pass will:

1. Locate the handoff flag via `grep -n PATHWAY-RECOMPUTE-PENDING docs/manuscript/track_a_pivot.md` → L222.
2. Resolve the conditional framing ("if the real-LD re-compute substantially weakens these enrichments") to definite language.
3. Remove the `<!--PATHWAY-RECOMPUTE-PENDING-->` HTML comment.

### For failure mode: Snakemake controller exits with error

If `tail /tmp/k2d_fire.log` shows "Error in rule" or the PID is no longer running AND coloc_summary.tsv is absent, inspect:

1. `logs/lsf/*.err` — per-job LSF stderr output for failed finemap or coloc jobs
2. `tail -n 100 /tmp/k2d_fire.log` — controller error trace
3. `bjobs -u ckclinto -d | head` — recently finished job states

Common issues:
- **SUSIE_MAX_VARIANTS exceeded** at large regions (BMI_5q13_3, PYHIN1_1q23, SLC2A9_urate, 9p21_CDKN2A, APOE_19q13, CXADR_F2RL1_6p21) — these emit `status=too_many_variants` placeholder JSONs, NOT fatal errors. Expected behavior; mirrors Stage 2 real-LD at the same regions.
- **Conda env mismatch** — `.snakemake/conda/` should be pre-populated from Stage 2; `--conda-prefix .snakemake/conda` flag in fire script reuses.
- **Missing LD reference for HLA_6p21 AFR** — HLA is specifically excluded from identity-LD analysis per admissibility. If fire halts here, consider excluding HLA_6p21 rows from `results_identity_ld/fine_mapping/finemap_manifest.tsv` before re-firing.

## Self-Check: PASSED

- `[✓]` `src/snakemake/scripts/make_identity_ld_refs.R` exists (81 lines; references `use_identity = TRUE` and `saveRDS`)
- `[✓]` `config/pipeline_identity_overlay.yaml` exists (parses as valid YAML; contains `results_identity_ld` + `ld_reference_identity`)
- `[✓]` `scripts/fire_identity_ld_rerun.sh` exists (executable; 2-phase wrapper)
- `[✓]` 24 identity-LD .rds payloads written (12 EUR + 12 AFR); SH2B3 EUR schema verified via readRDS
- `[✓]` Dry-run DAG: 100 Phase 1 jobs scheduled, 0 escape routes to Stage 2 paths
- `[✓]` LSF fire launched: PID 830748; 51 jobs submitted (32 RUN + 18 PEND + 1 completed) at 3-min snapshot
- `[✓]` Stage 2 real-LD artifacts byte-identical (4/4 md5 match) post-fire
- `[✓]` Fire-and-close pattern: orchestrator returns; jobs continue asynchronously on LSF
- `[✓]` Handoff documentation: monitoring commands + Fig 1A + Fig 3 + L222 pathway-recompute next-step pointers present
