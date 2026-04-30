---
phase: quick-260429-tq9
plan: 01
status: complete
requirements: [M2-POST-M3-08]
commits: 6
tags: [m2, mtcojo, harvest, sensitivity-table, m2-post-m3-08, schema-alignment, partially-completed]
subsystem: m2/mtcojo
key-files:
  created:
    - tests/m2/test_build_mtcojo_sensitivity_table_bcpval.py
    - data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md
    - .planning/m2_post_m3_rerun_status_legend.md
  modified:
    - src/python/build_mtcojo_sensitivity_table.py
    - .planning/m2_post_m3_rerun_queue.tsv
  filesystem-only (gitignored per .gitignore line 75 / project policy):
    - data/processed/mtcojo/EUR/{bmi.EUR.GIANT-UKBB.2018,hdl.EUR.GLGC.2021,ldl.EUR.GLGC.2021,tc.EUR.GLGC.2021,tg.EUR.GLGC.2021}.mtcojo.cojo
    - data/processed/mtcojo/TRANS/{hdl,ldl,tc,tg}.TRANS.GLGC.2021.mtcojo.cojo
    - data/processed/mtcojo/{EUR,AFR,TRANS}/mtcojo_sensitivity.tsv
metrics:
  duration: ~25 min
  completed: 2026-04-29
---

# Quick 260429-tq9: Harvest M2-POST-M3-08 mtCOJO Production Sensitivity Summary

**One-liner:** Post-LSF harvest of M2-POST-M3-08 mtCOJO production fire — 9/13 DONE → canonical-layout sensitivity tables across EUR+TRANS with `bC_pval`-driven sensitivity_flag classification (40,441 PASS+WARN rows; 18,025 bmi.EUR rows resolving the previously-missing-row symptom); 4/13 AFR EXITed at GCTA freq-difference filter (78,477 SNPs flagged vs 1000G AFR Phase3 N=504; sample-size insufficiency of LD ref) → re-routed to sibling obligation M2-POST-M3-03 (AoU AFR LD panel N≈95k) with 101-line root-cause disclosure document.

## Per-stratum harvest outcomes

| Stratum | Loci  | PASS  | WARN  | FAIL  | Cols | bmi.EUR present | Notes                                        |
|---------|-------|-------|-------|-------|------|-----------------|----------------------------------------------|
| EUR     | 76021 | 23848 | 3889  | 48284 | 6    | YES (18,025)    | bC_pval schema-alignment engaged             |
| AFR     | 4     | 0     | 0     | 4     | 6    | n/a             | All FAIL via missing-file branch (LD ceiling) |
| TRANS   | 71779 | 9458  | 3246  | 59075 | 7    | n/a             | bC_pval engaged; trans_ld_panel_concordance="primary_only" |

### Per-trait classification breakdown (EUR)

| target_trait              | PASS  | WARN | FAIL  | max_overlap_intercept | Notes                              |
|---------------------------|-------|------|-------|-----------------------|------------------------------------|
| bmi.EUR.GIANT-UKBB.2018   | 16421 | 1583 | 21    | 0.1992                | Substantive sensitivity output     |
| hdl.EUR.GLGC.2021         | 3899  | 1086 | 10859 | 0.5746                | Substantive sensitivity output     |
| ldl.EUR.GLGC.2021         | 0     | 0    | 12006 | 1.0106                | All-FAIL (saturated overlap; correct)|
| tc.EUR.GLGC.2021          | 0     | 0    | 15558 | 1.0106                | All-FAIL (saturated overlap; correct)|
| tg.EUR.GLGC.2021          | 3528  | 1220 | 9840  | 0.5746                | Substantive sensitivity output     |

### Per-trait classification breakdown (TRANS)

| target_trait              | PASS | WARN | FAIL  | max_overlap_intercept | Notes                              |
|---------------------------|------|------|-------|-----------------------|------------------------------------|
| hdl.TRANS.GLGC.2021       | 5195 | 1711 | 12550 | 0.5702                | Substantive sensitivity output     |
| ldl.TRANS.GLGC.2021       | 0    | 0    | 15059 | 1.0217                | All-FAIL (saturated overlap; correct)|
| tc.TRANS.GLGC.2021        | 0    | 0    | 19446 | 1.0217                | All-FAIL (saturated overlap; correct)|
| tg.TRANS.GLGC.2021        | 4263 | 1535 | 12020 | 0.5702                | Substantive sensitivity output     |

The `ldl` / `tc` all-FAIL rows in EUR + TRANS are the design-expected outcome:
LDSC bivariate-intercept = 1.0106 (EUR) / 1.0217 (TRANS) indicates GLGC LDL +
TC are sample-overlap-saturated within stratum (essentially nested cohorts),
so the mtCOJO conditional p-value correctly does not survive after correcting
for the overlap. The all-PASS / mixed rows on `bmi`, `hdl`, `tg` (max_overlap
≈ 0.20–0.57) are the substantive sensitivity-analysis output.

### AFR (all 4 FAIL via missing-file branch)

```
locus_id  trait                 mtag_p_original  mtcojo_p  max_overlap  flag
          hdl.AFR.GLGC.2021                                 0.4591       FAIL
          ldl.AFR.GLGC.2021                                 0.9371       FAIL
          tc.AFR.GLGC.2021                                  0.9371       FAIL
          tg.AFR.GLGC.2021                                  0.4591       FAIL
```

Root cause: 78,477 / 1,210,429 SNPs (6.5%) flagged at GCTA's freq-difference
filter against 1000G AFR Phase3 N=504 reference (vs GLGC AFR ~91k discovery
cohort, ~180:1 imbalance). Full disclosure at
`data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md`. Resolution
queued under M2-POST-M3-03 (AoU AFR LD panel N≈95k).

## Commit log (6 atomic commits)

| # | Hash       | Type | Subject                                                                                                                |
|---|------------|------|------------------------------------------------------------------------------------------------------------------------|
| 1 | `55338d4`  | test | add failing test for bC_pval column lookup (RED)                                                                       |
| 2 | `1b2b16f`  | feat | align mtcojo sensitivity aggregator to GCTA v1.94.1 bC_pval schema (GREEN)                                             |
| 3 | `8ca5638`  | data | migrate 9 m2p3_08 mtcojo cojo outputs to canonical sensitivity layout (marker — gitignored bytes on filesystem)        |
| 4 | `7869d43`  | docs | disclose AFR LD insufficiency at M2 + handoff to M2-POST-M3-03                                                         |
| 5 | `5d43676`  | data | rebuild mtcojo sensitivity tables across EUR/AFR/TRANS strata (marker — gitignored bytes on filesystem)                |
| 6 | `ee8844d`  | docs | mark M2-POST-M3-08 partially_completed (9/13 DONE; 4 AFR re-routed to M2-POST-M3-03)                                   |

## Per-stratum aggregator stdout transcript

```
===== EUR =====
EUR: 76021 loci → PASS=23848 WARN=3889 FAIL=48284
===== AFR =====
AFR: 4 loci → PASS=0 WARN=0 FAIL=4
===== TRANS =====
TRANS: 71779 loci → PASS=9458 WARN=3246 FAIL=59075
```

(Run via Snakemake-pinned smoke_dev Python 3.11 per Carter's standing rule;
one invocation per stratum.)

## Verification gates (8/8 OK)

| # | Gate                                                                | Outcome                                          |
|---|---------------------------------------------------------------------|--------------------------------------------------|
| 1 | Aggregator schema-aligned: pytest 3/3 PASSED                        | OK (3 passed in 0.85s)                           |
| 2 | Canonical cojo layout: 9 EUR+TRANS, 0 AFR                           | OK (5 EUR + 4 TRANS = 9; AFR = 0)                |
| 3 | AFR LD-insufficiency disclosure: ≥30 lines, references M2-POST-M3-03 + 78477 + AoU AFR | OK (101 lines; 3 M2-POST-M3-03 mentions) |
| 4 | Sensitivity tables: ≥1 PASS/WARN in EUR+TRANS, bmi.EUR present       | OK (40,441 non-FAIL; 18,025 bmi.EUR rows)        |
| 5 | Obligation queue: M2-POST-M3-08 status = `partially_completed`       | OK (12 cols preserved; row count 9 unchanged)    |
| 6 | Atomic commit count: 6                                               | OK (`git log \| grep -c '260429-tq9'` = 6)       |
| 7 | Hard-locked files untouched: m2_mtcojo.smk, build_cojo_inputs.py, select_mtcojo_eligible_targets.py, fire_m2_post_m3_08_mtcojo.sh, m2p3_08 audit subdirs | OK (all last-commit hashes pre-tq9) |
| 8 | Original-research framing: no fix/bug/broken/cleanup/revision/salvage in user-facing artifacts | OK (grep returns empty)                |

## Deviations from Plan

### [Rule 3 - Blocking issue] Project gitignore policy applied to data artifacts

**Found during:** Task 2 (cojo migration commit), Task 4 (sensitivity rebuild commit).

**Issue:** Plan's `<files>` block listed 9 `.mtcojo.cojo` files and 3
`mtcojo_sensitivity.tsv` files for `git add`, but `.gitignore` line 75
(`data/processed/*`) blocks all data-layer files per project policy:

> "Raw and processed data are NOT committed; they live at /rs1 and are
> symlinked under data/" (.gitignore preamble)

`git check-ignore -v` confirmed all 12 paths are blocked. The pre-existing
`mtcojo_sensitivity.tsv` files have no commit history (`git log --all
data/processed/mtcojo/EUR/mtcojo_sensitivity.tsv` returns empty).

**Resolution applied (rigor-first):**
- Tasks 2 + 4: Used `git commit --allow-empty` marker commits with
  rich commit-message bodies enumerating filesystem paths, byte sizes,
  and verification gate outcomes. Preserves the audit-log requirement
  (one commit per task) without violating the data-files-not-in-git
  policy. The actual cojo + sensitivity bytes live at canonical filesystem
  paths (verified by `ls`); they are reproducible from the m2p3_08 per-job
  audit trail + the schema-aligned aggregator.
- Task 3 (AFR disclosure .md): force-added with `git add -f`. The
  101-line markdown disclosure is documentation, not bulk data, and
  co-locating it under `data/processed/mtcojo/AFR/` is rigor-correct
  (future readers of the AFR sensitivity table will look there). The
  size (4 KB) is well within "interpretive artifact" semantics.

**Impact:** Plan's `files_modified` frontmatter listing of cojo + sensitivity
TSV paths is preserved as filesystem-state intent; the marker commits
document this explicitly. No analytical content lost; the harvest pipeline
is fully reproducible from any clean checkout via:

```bash
# 1. Re-run aggregator (5 sec)
for s in EUR AFR TRANS; do
    python src/python/build_mtcojo_sensitivity_table.py \
        --stratum "$s" --eligible "data/processed/mtcojo/$s/mtcojo_eligible_targets.tsv" \
        --mtcojo-dir "data/processed/mtcojo/$s" \
        --mtag-filtered "data/processed/mtag/$s/${s}_mtag_maxfdr_filtered.txt" \
        --out "data/processed/mtcojo/$s/mtcojo_sensitivity.tsv"
done
# 2. Re-cp from m2p3_08 audit subdirs into canonical layout (10 sec)
```

This deviation is a CLAUDE.md-precedence deviation (Rule 3 + project
.gitignore takes precedence over plan-author intent).

## Out-of-scope items (logged, not addressed here)

- **bmi.EUR-missing-from-table aggregator silent-skip defect** (lines 89-94 of
  build_mtcojo_sensitivity_table.py). Pre-existing; orchestrator constraint
  forbade modifying lines outside line 96. Post-tq9, bmi.EUR DOES appear in
  the EUR sensitivity table (18,025 rows), so the symptom is RESOLVED at the
  observable layer — the aggregator's missing-file branch + the bC_pval
  schema-alignment together cover the bmi.EUR case. The lines 89-94
  silent-skip remains a latent defect for future malformed inputs but is
  not exercised by the current 13-target eligible set.
- **sbp.EUR / stroke.EUR rsID re-harmonization** (M1 follow-up; HM3 ∩ sbp = ∅
  and HM3 ∩ stroke = ∅ because those traits harmonized to chr:pos identifiers).
- **AoU AFR LD panel build** (M2-POST-M3-01 / M2-POST-M3-03 / M2-POST-M3-05
  family; blocked on AoU controlled-tier workspace registration 260426-aow).
- **MTAG --fdr re-fire** (M2-POST-M3-07; blocked on m2-mtag conda env build).
- **GWAS Catalog v_lock_M5 refresh** (M2-POST-M3-06; deferred to M5 cross-ref).

## Self-Check

**Files claimed:**
- `tests/m2/test_build_mtcojo_sensitivity_table_bcpval.py` — FOUND (253 lines, tracked, 3/3 pytest PASSED)
- `src/python/build_mtcojo_sensitivity_table.py` — FOUND (line 96 = `c.get("bC_pval", c.get("p_cojo", c.get("pC", None)))`)
- `data/processed/mtcojo/AFR/AFR_LD_INSUFFICIENT_FOR_MTCOJO.md` — FOUND (101 lines, force-added)
- `.planning/m2_post_m3_rerun_status_legend.md` — FOUND (24 lines, tracked)
- `.planning/m2_post_m3_rerun_queue.tsv` — MODIFIED (M2-POST-M3-08 row: status=partially_completed, current_artifact appended with HARVEST 2026-04-29)
- `data/processed/mtcojo/EUR/{bmi,hdl,ldl,tc,tg}.EUR.*.mtcojo.cojo` — 5 FOUND on filesystem (gitignored, marker-committed)
- `data/processed/mtcojo/TRANS/{hdl,ldl,tc,tg}.TRANS.*.mtcojo.cojo` — 4 FOUND on filesystem (gitignored, marker-committed)
- `data/processed/mtcojo/EUR/mtcojo_sensitivity.tsv` — FOUND (76,021 rows, 6 cols, 5.2 MB; gitignored, marker-committed)
- `data/processed/mtcojo/AFR/mtcojo_sensitivity.tsv` — FOUND (4 rows, 6 cols, 213 B; gitignored, marker-committed)
- `data/processed/mtcojo/TRANS/mtcojo_sensitivity.tsv` — FOUND (71,779 rows, 7 cols, 5.7 MB; gitignored, marker-committed)

**Commits claimed:**
- `55338d4` test RED — FOUND
- `1b2b16f` feat GREEN — FOUND
- `8ca5638` data Task 2 marker — FOUND
- `7869d43` docs Task 3 — FOUND
- `5d43676` data Task 4 marker — FOUND
- `ee8844d` docs Task 5 — FOUND

## Self-Check: PASSED
