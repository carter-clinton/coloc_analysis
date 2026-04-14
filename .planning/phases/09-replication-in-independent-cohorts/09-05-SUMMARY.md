---
phase: 09-replication-in-independent-cohorts
plan: 05
subsystem: replication-cojo-aggregate
tags: [python, pandas, bash, gcta, snakemake, pytest, cojo, master-table, cross-ancestry, holdout, methods-doc]

# Dependency graph
requires:
  - phase: 09-replication-in-independent-cohorts
    provides: "Plan 09-04 per-cohort effect_size/{cohort}.tsv + IVW ivw_meta.tsv + fiqt/discovery_beta_fiqt.tsv + coloc/{signal_id}_{cohort}.coloc.json"
  - phase: 05-pathway-heritability
    provides: "pathway.smk rule download_ldsc_baseline — produces data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.{EUR|AFR}.QC.{chrom}.{bed,bim,fam} + flag file .baseline_download_done"
  - external:
      package: "gcta=1.94.1"
      provides: "--cojo-slct conditional+joint analysis; env envs/gcta.yml from Plan 09-01"
      usage: "src/snakemake/scripts/run_cojo.sh"
provides:
  - "D-07 output 1 — results/replication/master_table.tsv (RESEARCH §16 schema; 4 effect-size columns; per-cohort × 5 blocks; meta block; 6 sample_overlap_flag columns; low_maf_founder_flag)"
  - "D-07 output 2 — results/replication/cross_ancestry_generalization_tier_ab.tsv (Tier A+B × BBJ-EAS only; D-05c enforced; is_generalization=True)"
  - "D-07 output 3 — results/replication/cojo_sensitivity.tsv (GCTA --cojo-slct per complex locus × cohort; TIER-2 supplementary per gotcha #1)"
  - "D-07 output 4 — results/replication/replication_holdout_supplementary.tsv (leave-one-cohort-out IVW jack-knife)"
  - "docs/methods/phase9_replication.md (manuscript fragment for Phase 11; covers D-01 4 cohorts, D-03 joint criterion, D-04 FIQT, D-05/D-05c ancestry matching, gotcha #1 COJO N=503 3-layer caveat, gotcha #3 stroke endpoint heterogeneity)"
  - "Replication §F + §G fully implemented (grep 'TODO plan' on replication.smk → 0 hits; 25 production rules)"
affects: [11-manuscript]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "I-3 per-cohort sample_overlap_flag — KNOWN_OVERLAP_PAIRS dict keyed by (trait, cohort) with wildcard ('*', cohort) fallback resolves trait-specific before structural overlap"
    - "I-2 meta merge key — (signal_id, discovery_ancestry) composite key prevents signal_id collision across ancestries; meta_ancestry column carried through for traceability"
    - "Gotcha #1 three-layer enforcement — (1) run_cojo.sh stderr WARN on N<4000, (2) test_cojo_sensitivity.py asserts '4000' + 'WARN' literal presence, (3) docs/methods/phase9_replication.md narrative caveat"
    - "aggregate_per_cohort_combined producer — new Snakemake rule concatenates per-cohort effect_size/{cohort}.tsv into per_cohort_combined.tsv that both IVW meta (Plan 09-04) and holdout (Plan 09-05) depend on; dependency was implicit in Plan 09-04 docstring, now made explicit"
    - "Stale-docstring discipline — replication.smk module docstring updated from 'skeleton' language to 'production rules' because §F + §G filled; grep 'TODO plan' on the file is a hard lint now"

# Key files
key-files:
  created:
    - "src/snakemake/scripts/prepare_cojo_ma.py — canonical sumstats -> GCTA 8-column .ma at a single locus"
    - "src/snakemake/scripts/run_cojo.sh — GCTA 1.94.1 --cojo-slct wrapper with N<4000 WARN + set -euo pipefail hardening (T-09-07 mitigation)"
    - "src/python/build_cojo_sensitivity_table.py — aggregates .jma.cojo outputs with defensive missing-file handling"
    - "src/python/build_master_replication_table.py — full RESEARCH §16 master table assembler including I-2 and I-3 revisions"
    - "src/python/build_cross_ancestry_panel.py — Tier A+B × BBJ-EAS generalization panel (D-05c enforcement with assert)"
    - "src/python/build_replication_holdout.py — leave-one-cohort-out IVW jack-knife grouped by (signal_id × cohort_ancestry)"
    - "docs/methods/phase9_replication.md — 166-line manuscript methods fragment for Phase 11"
  modified:
    - "src/snakemake/rules/replication.smk — §F (prepare_cojo_ma, run_cojo_slct, assemble_cojo_sensitivity_supplementary) + §G (aggregate_per_cohort_combined, assemble_master_replication_table, assemble_cross_ancestry_generalization_bbj, assemble_replication_holdout_supplementary) promoted from skeleton-TODO to production; wildcard_constraints for ancestry=EUR|AFR"
    - "tests/phase9/test_cojo_sensitivity.py — 12 tests for COJO wrapper (prepare_cojo_ma, run_cojo.sh content, build_cojo_sensitivity_table, replication.smk §F de-TODO)"
    - "tests/phase9/test_master_table_schema.py — 10 tests for master table (schema completeness, I-3 overlap flags, I-2 meta_ancestry, wildcard resolution, §G de-TODO, methods doc content)"
    - "tests/phase9/test_negative_controls.py — HLA Layer-3 check xfail/skip tolerant of pre-execution state"

# Decisions
decisions:
  - "ancestry wildcard constraint — wildcard_constraints: ancestry=EUR|AFR enforced at rule scope (not just at snakemake invocation) so {ancestry} in plink_bed template cannot resolve to lowercase or non-AFR/EUR values even if a downstream rule tries to pass eur/afr; matches Broad LDSC 1000G.{EUR|AFR}.QC.{chrom} filename convention"
  - "LDSC flag path corrected — pathway.smk emits data/reference/ldsc/.baseline_download_done (not .download_ldsc_baseline.done as plan draft assumed); run_cojo_slct depends on the real flag to avoid a phantom dependency the DAG can't resolve"
  - "COJO filename disambiguation — output path includes {signal_id}_{ancestry}_{chrom} in addition to {cohort}_{trait}_{locus} so GCTA doesn't collide when two signals in the same locus dispatch to COJO; prepare_cojo_ma output mirrors the same stem"
  - "Per-cohort combined aggregator — aggregate_per_cohort_combined materialized as a first-class rule (not a lambda) so the DAG consumes an on-disk TSV with deterministic column ordering; IVW meta (09-04) and holdout (09-05) share the same input"
  - "D-05c enforcement belt-and-braces — build_cross_ancestry_panel.py both filters signal_class IN ('tier_A_triple','tier_B_triple') AND asserts no credible_set_SNP rows remain post-filter; tests hit both the filter path and the assertion"
  - "Methods doc framed as original research — 'Phase 9 Replication Methods' (not 'Supplementary to Phase 1') per project feedback memory; deliberately written in present/past tense + active voice for direct manuscript consumption"

metrics:
  duration: 7min
  tasks: 2
  files: 11
  commits: 4
  completed: 2026-04-14
---

# Phase 9 Plan 5: replication-cojo-aggregate Summary

**One-liner:** Phase-9 gate: produces the four D-07 output artifacts (master_table, cross-ancestry generalization, COJO sensitivity, leave-one-cohort-out holdout) plus the manuscript methods fragment, embedding the gotcha #1 COJO-N=503 caveat at three layers (shell WARN + tests + methods) and the gotcha #3 ischemic-primary stroke endpoint decision.

## What was built

### Task 1 — COJO sensitivity pipeline (commit 488f121)

- `prepare_cojo_ma.py` (102 lines) — region-filtered canonical → GCTA 8-column .ma file. Handles `.gz` and plain TSV. Validates all 10 canonical columns present before emit.
- `run_cojo.sh` (63 lines) — hardened GCTA wrapper: `set -euo pipefail`; positional `$1-$4` arg validation; stderr WARN when `.fam` row count < 4000; exits 3 (not 0) when `.fam` is missing. Mitigates T-09-07 (shell arg injection) + T-09-22 (silent under-powered LD).
- `build_cojo_sensitivity_table.py` (151 lines) — aggregates `.jma.cojo` across the manifest. Missing files → silently skipped (COJO is supplementary; absent rows do not inflate the table). `parse_cojo_jma` picks the min-pJ row as top-SNP with explicit fallback when `pJ` column is absent.
- `replication.smk §F` — three production rules (`prepare_cojo_ma`, `run_cojo_slct`, `assemble_cojo_sensitivity_supplementary`) replacing three TODO placeholders. Declares explicit input dep on `data/reference/ldsc/.baseline_download_done` (pathway.smk's download flag) — no new download rule introduced.
- 12 tests green: in-memory `canonical_to_ma` correctness + file-on-disk contract (A1=EA, A2=OA per GCTA) + script-content assertions for `--cojo-slct`, `--cojo-p 5e-8`, `--cojo-wind 10000`, `4000` literal, `WARN` token, `set -euo pipefail` hardening + aggregator end-to-end with a 1-signal manifest and a 2-independent-signal `.jma.cojo`.

### Task 2 — 4 D-07 tables + cross-ancestry panel + methods (commit 5c01544)

- `build_master_replication_table.py` (307 lines) — full RESEARCH §16 assembler.
  - **I-2 revision**: meta merge key is `(signal_id, discovery_ancestry)` with fallback paths for legacy meta tables; always back-fills `meta_ancestry` column even when IVW meta is empty.
  - **I-3 revision**: 6 `{cohort}_sample_overlap_flag` columns (finngen_r12, gbmi_eur, gbmi_afr, mvp_eur, mvp_afr, bbj) populated via `resolve_overlap_flag(trait, cohort)` which checks `(trait, cohort)` then wildcard `("*", cohort)`. Five registered pairs (gbmi structural overlaps + trait-specific HTN/BMI/stroke).
  - Per-cohort block renamer drops the raw `cohort` column before prefixing to avoid `<cohort>_cohort` collision.
  - Schema contract: even when an upstream per-cohort file is missing, all `PER_COHORT_EMPTY_SUFFIXES` are emitted as null columns so the downstream schema is constant.
- `build_cross_ancestry_panel.py` (95 lines) — Tier A+B × BBJ-EAS panel. Filters `signal_class ∈ {tier_A_triple, tier_B_triple}` AND `cohort == 'bbj'`, then asserts no `credible_set_SNP` rows remain (belt-and-braces D-05c). Merges BBJ per-cohort effect-size if available; emits `is_generalization=True` + `framing_note` column on every row.
- `build_replication_holdout.py` (109 lines) — leave-one-cohort-out IVW jack-knife. Groups by `(signal_id, cohort_ancestry)` so EUR/AFR never pool; signals with < 2 valid cohorts contribute no rows; each hold-out row carries `loco_n_cohorts` counter.
- `docs/methods/phase9_replication.md` (166 lines) — Phase-11 manuscript fragment. Covers D-01 (4-cohort portfolio table), D-03 (joint criterion conjunction), D-04 (FIQT pinned to SHA 2ed00bb), D-05/D-05c (ancestry routing table + BBJ generalization framing), gotcha #1 (COJO N=503 with 3-layer enforcement narrative), gotcha #3 (stroke endpoint heterogeneity with explicit ischemic-primary decision + sensitivity note).
- `replication.smk §G` — four production rules + `aggregate_per_cohort_combined` new rule that materializes `per_cohort_combined.tsv` consumed by both IVW meta (09-04) and holdout (09-05). TODO markers fully removed including stale docstring language.
- 10 tests green + 1 xfail (expected pre-execution HLA Layer-3).

## Deliverables

| D-07 artifact | File | Row count |
|---------------|------|-----------|
| Master replication table | `results/replication/master_table.tsv` | TBD post-real-run; test fixture emits 2 rows × 64 columns (5 cohorts × ~12 suffixes + meta + flags + discovery) |
| Cross-ancestry generalization | `results/replication/cross_ancestry_generalization_tier_ab.tsv` | TBD; test fixture emits 2 rows (credible_set excluded) |
| COJO sensitivity | `results/replication/cojo_sensitivity.tsv` | TBD; test fixture emits 1 row (1 .jma.cojo present) |
| Replication hold-out | `results/replication/replication_holdout_supplementary.tsv` | TBD; test fixture emits 3 rows (3 cohorts × 1 signal, each held out once) |

## Deviations from Plan

### Rule 3 – blocking fix: LDSC flag file path

- **Found during:** Task 1 Step 4
- **Issue:** Plan Step 4 used `data/reference/ldsc/.download_ldsc_baseline.done` as the dependency flag. The real `download_ldsc_baseline` rule in `src/snakemake/rules/pathway.smk` (line 188) emits `.baseline_download_done` (different stem). Using the plan path would create a phantom dependency Snakemake cannot resolve.
- **Fix:** `run_cojo_slct` depends on the actual flag `.baseline_download_done`. Plan's own §read_first note explicitly permitted: *"if it differs, use the actual flag path"*.
- **Files modified:** `src/snakemake/rules/replication.smk`
- **Commit:** 488f121

### Rule 2 – missing critical functionality: per_cohort_combined producer

- **Found during:** Task 2 Step 4
- **Issue:** `replication.smk` rule `ivw_meta_aggregate` (Plan 09-04) declared input `per_cohort_combined.tsv` with docstring promise *"that aggregator concatenates the per-cohort effect_size/{cohort}.tsv outputs into a single long TSV"* — but no rule produced it. Plan 09-05 also declared the file as holdout input without a producer. Shipping without this rule would break both `ivw_meta.tsv` (Plan 09-04 output) and `replication_holdout_supplementary.tsv` (Plan 09-05 output).
- **Fix:** Added `aggregate_per_cohort_combined` rule to §G: concatenates `effect_size/{cohort}.tsv` across the 6 cohorts listed in `config['panels']['all_replication_cohorts']` with safe fallback on missing files; emits `effect_size/per_cohort_combined.tsv` with deterministic column ordering.
- **Files modified:** `src/snakemake/rules/replication.smk`
- **Commit:** 5c01544

### Rule 1 – bug: docstring hard-lint conflict

- **Found during:** Task 2 verification (grep 'TODO plan' = 1 instead of 0)
- **Issue:** The remaining "TODO plan" match was in the module docstring describing the file's former skeleton state — not in any rule body — but the plan verify check uses `grep -c 'TODO plan'` as a hard lint, so a stale historical comment would trip the gate.
- **Fix:** Rewrote docstring to reflect production state ("This file was seeded as a Wave-1 skeleton and progressively filled in by Plans 09-02 through 09-05..."). `grep 'TODO plan' → 0` now.
- **Files modified:** `src/snakemake/rules/replication.smk`
- **Commit:** 5c01544

## Deferred Issues

None. The 1 xfail in `test_negative_controls.py::test_hla_fails_replication_joint` is by design — the test is a scientific Layer-3 check that activates only after the pipeline runs on real data; `pytest.xfail` pre-execution is the documented expected state.

## Scientific Layer 3: HLA negative control outcome

Pre-execution: test xfails (no `master_table.tsv` on disk yet). Post-execution expectation per plan: ≥ 70% of HLA-region rows (chr6:28-33Mb) fail the joint criterion in ≥ 3 of the 4 cohort groups. Test hardened to treat NaN as fail-null (absence of evidence), and to skip when no HLA signals entered Tier A/B/credible-set at all.

## Checkpoint #1 readiness

Plan 09-05 is the Phase-9 gate. After this plan:

| T1 Phase | Status | Notes |
|----------|--------|-------|
| Phase 0  | complete | Closeout 2026-04-10 (OSF DOI 10.17605/OSF.IO/PVB5J) |
| Phase 1  | complete | Closeout 2026-04-13 (OSF amendment osf.io/az52u) |
| Phase 2  | complete | 5 plans complete |
| Phase 5  | complete | 5 plans complete; DEF-RO7-02/03 deferred to Phase 9 window per 2026-04-13 decision |
| Phase 9  | **complete** (this plan) | All 5 plans complete; 4 D-07 artifacts have production rules |

Ready for `/gsd-verify-work` on Phase 9 and subsequent Checkpoint #1 (AJHG vs Nat Genet decision).

## Self-Check: PASSED

Files claimed vs found:

- FOUND: src/snakemake/scripts/prepare_cojo_ma.py
- FOUND: src/snakemake/scripts/run_cojo.sh
- FOUND: src/python/build_cojo_sensitivity_table.py
- FOUND: src/python/build_master_replication_table.py
- FOUND: src/python/build_cross_ancestry_panel.py
- FOUND: src/python/build_replication_holdout.py
- FOUND: docs/methods/phase9_replication.md
- FOUND: tests/phase9/test_cojo_sensitivity.py (updated)
- FOUND: tests/phase9/test_master_table_schema.py (updated)
- FOUND: tests/phase9/test_negative_controls.py (updated)
- FOUND: src/snakemake/rules/replication.smk (modified)

Commits:

- FOUND: 2f52bd1 (test Task 1 RED)
- FOUND: 488f121 (feat Task 1 GREEN)
- FOUND: 523faa0 (test Task 2 RED)
- FOUND: 5c01544 (feat Task 2 GREEN)

All four commits present; all 11 files present on disk.
