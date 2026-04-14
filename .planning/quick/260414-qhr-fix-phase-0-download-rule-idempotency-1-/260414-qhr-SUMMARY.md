---
phase: quick-260414-qhr
plan: 01
subsystem: phase-0-download-idempotency
tags: [snakemake, pathway, idempotency, ldsc, magma, phase0, hpc]
requires: [src/snakemake/rules/pathway.smk]
provides:
  - "download_ldsc_baseline rule that detects pre-staged data and skips re-fetch"
  - "tools/magma_v1.10/magma symlink resolving to manually-staged binary"
  - "data/reference/ldsc/.baseline_download_done flag file"
affects: [src/snakemake/rules/pathway.smk]
tech-stack:
  added: []
  patterns:
    - "preflight on-disk-sentinel check with touch-and-exit-0 early return inside snakemake shell block"
    - "out-of-tree symlink reconciliation for path-mismatched rule outputs (avoids rule/config surgery)"
key-files:
  created:
    - "tools/magma_v1.10/magma (symlink, gitignored)"
    - "data/reference/ldsc/.baseline_download_done (flag, gitignored)"
  modified:
    - "src/snakemake/rules/pathway.smk (download_ldsc_baseline shell block)"
decisions:
  - "D-01: symlink over rule/config edit for MAGMA path mismatch (smallest diff, preserves rule-output contract)"
  - "D-02: preflight guard at top of existing shell block (no rule-type change; wget fallback preserved)"
  - "D-03: 5-sentinel detection set (baselineLD.22.l2.M, 3 subdirs, snplist) — chr22 as alphabetical-last proxy"
  - "D-04: out-of-scope rules explicitly NOT touched (download_ldsc_seg, download_magma_ref, download_hess_*, download_sumstats)"
metrics:
  duration: "~5min"
  completed: "2026-04-14T23:10:29Z"
  tasks: 2
  files: 3
  commits: 1
requirements:
  - QHR-01
  - QHR-02
  - QHR-03
---

# Phase quick-260414-qhr Plan 01: Phase 0 download-rule idempotency Summary

**One-liner:** Patched `download_ldsc_baseline` with a 5-sentinel on-disk preflight guard and reconciled MAGMA binary path via symlink, making `snakemake all_pathway --dry-run` resolve cleanly (577 jobs, both target rules absent) against Carter's 32 GB of pre-staged Phase 0 references.

## Objective Recap

Two Phase 0 download rules in `src/snakemake/rules/pathway.smk` were not idempotent against manually-staged reference data, blocking any real-data execution of the Phase 5 DAG:

1. `download_ldsc_baseline` would unconditionally wget ~5 GB from Broad S3 + GCS requester-pays (the latter fails without auth), despite all artifacts already on disk.
2. `download_magma_binary` expected `tools/magma_v1.10/magma`; Carter's manual download landed at `data/reference/magma/magma` (CNCR JS-gate blocks curl; path mismatch alone prevented detection).

Goal: make both rules drop out of the `--dry-run` job list without rewriting the download logic or breaking fresh-clone fallback.

## What Was Done

**Change A — `src/snakemake/rules/pathway.smk`:** Inserted a 14-line preflight guard at the top of `download_ldsc_baseline`'s shell block (immediately after `mkdir -p {params.outdir}`), checking for all five canonical sentinel artifacts. When all present, logs a skip message to stderr, touches the flag output, and exits 0. When any missing, falls through to the existing wget block unchanged.

```bash
# Idempotency guard (D-02, D-03): if references are already staged on disk,
# touch the flag + snplist outputs and exit cleanly. Prevents re-fetching
# ~5 GB from Broad S3 + GCS requester-pays (the latter fails without auth)
# on systems where Carter has manually staged the data from Zenodo.
if [ -f {params.outdir}/baselineLD.22.l2.M ] && \
   [ -d {params.outdir}/1000G_EUR_Phase3_plink ] && \
   [ -d {params.outdir}/1000G_Phase3_frq ] && \
   [ -d {params.outdir}/1000G_Phase3_weights_hm3_no_MHC ] && \
   [ -f {output.hapmap3} ]; then
    echo "download_ldsc_baseline: detected pre-staged LDSC reference data on disk; skipping download" >&2
    touch {output.baseline_done}
    exit 0
fi
```

**Change B — Symlink:** `tools/magma_v1.10/magma -> ../../data/reference/magma/magma` (relative target for repo-relocatability). Verified the target is executable and `tools/magma_v1.10/magma --version` reports `MAGMA version: v1.10 (linux/s)`.

**Change C — Flag touch:** `data/reference/ldsc/.baseline_download_done` touched explicitly so Snakemake's DAG resolution sees the rule as up-to-date on the very first dry-run (without needing a first no-op rule execution).

No other download rules modified. No config changes. No consumer-rule edits.

## Dry-Run Verification (Task 2 Checkpoint)

Captured verbatim from `snakemake all_pathway --dry-run` (full log: 5,819 lines, exit=0).

**Matches for target rules in job list:**
```
$ grep -cE "^rule (download_ldsc_baseline|download_magma_binary):" /tmp/qhr_dryrun.log
0
```

**Job stats section (head — note BOTH target rules ABSENT):**
```
Building DAG of jobs...
Job stats:
job                              count
-----------------------------  -------
aggregate_pathway_results            1
aggregate_qtl_coloc                  1
all_pathway                          1
assign_tiers                         1
build_1kg_sample_lists               1
build_coloc_manifest                 1
build_finemap_manifest               1
build_gprofiler_background           1
build_ld_rds                        24
build_magma_set_file                 1
build_neg_ctrl_manifest              1
build_qtl_coloc_manifest             1
build_tissue_n_lookup                1
collect_region_variants             12
download_hess_panel                  1
download_ldsc_seg                    1
download_msigdb                      1
download_sumstats                    8
extract_tier_ab_genes                1
filter_finemap_summary               1
gprofiler_enrichment                 1
gprofiler_negative_controls          1
harmonize_sumstats                   8
hess_aggregate                       1
hess_combine                        13
hess_compare_pleio                  13
hess_format_sumstats                 8
hess_local_rhog                    286
hess_validate_panel                  1
ldsc_aggregate_h2                    1
ldsc_build_custom_annotations        1
ldsc_compute_custom_ld_scores       22
ldsc_munge                           8
ldsc_partitioned_h2                  8
ldsc_seg_chromatin                   8
ldsc_seg_gene_expr                   8
ldsc_seg_shared_tissues              1
magma_annotate                       1
magma_fdr                            8
magma_gene_analysis                  8
magma_geneset_analysis               8
permutation_aggregate                1
permutation_null_genesets            1
run_curated_negative_controls        1
run_finemap                         96
summarize_coloc_results              1
summarize_finemap_results            1
validate_negative_controls           1
total                              577

This was a dry-run (flag -n). The order of jobs does not reflect the order of execution.
```

Cross-check — both target rules confirmed absent:
- `download_ldsc_baseline`: NOT in job list (was present before patch; now preflight guard fires, flag file exists → DAG marks up-to-date)
- `download_magma_binary`: NOT in job list (was present before patch; now symlink satisfies `output.binary="tools/magma_v1.10/magma"` → DAG marks up-to-date)

**Stability check (second dry-run):**
```
$ /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run 2>&1 | grep -cE "^rule (download_ldsc_baseline|download_magma_binary):"
0
$ # total jobs: 577 (identical to first run — fully stable)
```

**Automated guards (all passed):**
```
$ grep -c "Idempotency guard" src/snakemake/rules/pathway.smk      # → 1
$ test -L tools/magma_v1.10/magma && test -x tools/magma_v1.10/magma  # → OK
$ test -f data/reference/ldsc/.baseline_download_done                  # → OK
$ snakemake --list | grep -E "^(download_ldsc_baseline|download_magma_binary)$"
download_ldsc_baseline
download_magma_binary
```

The rules still exist in the graph (as expected — they remain executable for fresh-clone systems) but are resolved as up-to-date by the DAG.

## Requirements Traceability

| ID     | Description                                                            | Status | Evidence                                                           |
| ------ | ---------------------------------------------------------------------- | ------ | ------------------------------------------------------------------ |
| QHR-01 | `download_ldsc_baseline` idempotent against on-disk references         | DONE   | Preflight guard inserted; 5-sentinel check + touch + exit 0        |
| QHR-02 | `download_magma_binary` path reconciled with manual staging            | DONE   | `tools/magma_v1.10/magma` symlink resolves to `data/reference/magma/magma` |
| QHR-03 | `snakemake all_pathway --dry-run` shows both rules up-to-date          | DONE   | 0 matches in job list across 2 consecutive dry-runs (577 jobs each) |

## Self-Check: PASSED

- `src/snakemake/rules/pathway.smk`: FOUND (14 new lines; 1 new `Idempotency guard` marker)
- `tools/magma_v1.10/magma`: FOUND (symlink → `../../data/reference/magma/magma`; target executable)
- `data/reference/ldsc/.baseline_download_done`: FOUND (0-byte flag)
- Commit `e936aea`: FOUND in `git log --oneline` (branch main)
- Dry-run log: 5,819 lines, exit=0, 0 matches for target rules across 2 runs

## Deviations from Plan

None — plan executed exactly as written. All three changes (A, B, C) applied as specified. Plan's 5-sentinel detection set matched the on-disk reality verbatim on first try; no fallback scenarios hit (relative symlink resolved cleanly on gpfs — no need for absolute-target fallback).

Task 2's `checkpoint:human-verify` was treated as a capture-output gate per the orchestrator's environment notes: the dry-run was run locally, both target rules confirmed absent across two consecutive runs, and the output transcript is embedded in this SUMMARY so the orchestrator can verify without re-running the ~60s dry-run.

## Authentication Gates

None. No credentials required; all work on local filesystem. The whole point of this patch was to avoid hitting GCS requester-pays auth (download_ldsc_baseline) and CNCR JS-gate (download_magma_binary) in the first place.

## Deferred Follow-ups

Tracked for a subsequent quick task (not this one; per plan's `<deferred_followup>` block):
- `download_ldsc_seg` (pathway.smk:239) — Multi_tissue_gene_expr + chromatin from GCS requester-pays; same idempotency gap. Data already staged (per STATE.md 2026-04-14 PM findings).
- `download_magma_ref` (pathway.smk:131) — NCBI37.3.gene.loc + g1000_eur + dbsnp151.synonyms from CNCR JS-gate; same gap. Data already staged.
- `download_hess_panel` (pathway.smk:334) — Carter has symlink farm under `data/reference/hess/ld_panel/EUR/`; worth auditing whether `build_ld_rds` etc. resolve cleanly after a similar guard.
- `download_hess_partition` — EUR/AFR/EAS partitions already staged from Bitbucket.
- `download_sumstats` — 8 trait/ancestry combos; needs separate scoping (cache/downloads vs `data/raw/sumstats`, URL-rot audit, overwrite-protection for existing Feb-11 harmonized files).

Also visible in this dry-run log (pre-existing, NOT regressions from QHR):
- `download_sumstats` × 8 (trait/ancestry combos) still in job list — expected; this rule was explicitly out of scope per task constraints.
- `download_ldsc_seg`, `download_hess_panel`, `download_msigdb` still in job list — expected; deferred follow-up above.

## Known Stubs

None. This task added no placeholder data, no mock values, no TODO-gated code paths. The preflight guard is production-quality: it fires only when real data is on disk (5-sentinel check) and otherwise falls through to the original wget implementation.

## Commits

| Task | Description                                                         | Hash      |
| ---- | ------------------------------------------------------------------- | --------- |
| 1    | fix(quick-260414-qhr): make download_ldsc_baseline idempotent       | `e936aea` |
| 2    | (checkpoint — no code commit; verification transcript in this SUMMARY) | —         |

## Threat Flags

None. The patch is defense-in-depth for existing trust boundaries (accepts pre-staged data at `data/reference/ldsc/` and `data/reference/magma/magma` which were already trusted in prior Phase 0 data-landing work). No new network endpoints, no new auth paths, no new filesystem surface. All threats from the plan's `<threat_model>` remain at their planned dispositions (T-qhr-01/02/05/06 `accept`; T-qhr-03/04 `mitigate` — mitigations implemented as specified: 5-sentinel check, explicit touch conditional on verified on-disk state).
