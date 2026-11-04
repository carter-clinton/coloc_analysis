---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15
slug: W3e-qtl-harmonize-and-group-runner
subsystem: ta-r4 QTL layer (pre-gate harmonization; pre-lock runner code)
tags: [qtl, harmonization, coloc, fallback_abf, coverage, lock-gate, pre-lock]
requires: [ta-r4-W3d-estimators-and-branch-classifier]
provides:
  - data/r4/qtl/harmonized/ (23,310 files) + manifests/qtl_harmonized_sha256.tsv
  - src/python/ta_r4/harmonize_qtl_r4.py
  - src/python/ta_r4/run_qtl_group_r4.py
  - run_coloc_pair_r4.R --mode qtl_abf
  - src/snakemake/rules/ta_r4_qtl.smk (r4_qtl_harmonize, r4_qtl_group, r4_qtl_aggregate, r4_qtl_tiers, r4_qtl_all)
affects: [W4a (amendment cites 4d27ac00 + 0ca16af9; QTL decisions below), W6 (fires r4_qtl_all per QTL arm; 899 group jobs each)]
tech-stack:
  added: []
  patterns: [shipped harmonizer run on a per-feature frame via a scoped reader swap, differential bridge test by tracing coloc::check_dataset, per-group coverage vs the static manifest]
key-files:
  created:
    - src/python/ta_r4/harmonize_qtl_r4.py
    - src/python/ta_r4/run_qtl_group_r4.py
    - src/snakemake/rules/ta_r4_qtl.smk
    - tests/ta_r4/test_qtl_harmonize_r4.py
    - tests/ta_r4/test_qtl_group_runner.py
    - tests/ta_r4/fixtures/qtl_group_fixture.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/qtl_harmonized_sha256.tsv
  modified:
    - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
    - tests/ta_r4/test_coloc_pair_r4.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
    - .planning/ROADMAP.md
decisions:
  - "Harmonization unit is the manifest feature (molecular_trait_id), not gene_id: the shipped sQTL harmonizer filters on gene_id and would mix the junctions of 376 genes (882 junctions) in one file"
  - "QTL tiers read only coloc_susie rows (aggregate_qtl_coloc.py reads `summary`, which run_qtl_coloc.R leaves empty for no-CS rows); fallback_abf PPs are in each row JSON (pp_h*, fallback) — W4a decision"
  - "Below-floor LD_JOIN_FATAL (panel_bridge_below_threshold, qtl_orient_below_threshold) is a row (method none, status ld_join_fatal:<reason>); any other R failure writes no row, so coverage exits 1"
  - "run_qtl_coloc.R is not edited: its coloc.susie uses package priors, so the runner refuses a priors yaml that differs from them"
metrics:
  duration: "~2 h 40 min (23:10 EST 2026-11-03 start)"
  completed: "2026-11-04"
  tasks: 3
  files: 12
  commits: [4d27ac00, 0ca16af9]
---

# Phase ta-r4 Plan W3e: QTL Harmonize and Group Runner Summary

Every QTL manifest feature is harmonized on /rs1 with a sha256 manifest: 23,310 files, 0 empty. One gated runner executes all
manifest rows of a (QTL arm, region, source, QTD) group. It runs the fixed arms (A3, A2) and the exact pre-fix argv (legacy),
labels the no-CS rows fallback_abf, and fails the group on any missing or extra row. No QTL coloc was run on real data.

## Commits (cite in W4a as analysis-code commits, with W0d/W3c/W3d)

| Task | Commit | Subject |
|---|---|---|
| 1 | 4d27ac00 | harmonize every QTL manifest slice pre-gate, with a sha256 manifest |
| 2 | 0ca16af9 | QTL group runner, qtl_abf fallback mode, gated group/aggregate/tier rules |
| 3 | (docs commit after this SUMMARY) | wave close: LOG, STATE, ROADMAP, SUMMARY |

## Task 1: harmonization (pre-gate, D-05)

**Fire.** `r4_qtl_harmonize` runs one job per (source, qtd, region) group: 899 groups. It was dry-run first through
`bin/r4_fire.sh repro repro_routeC -n r4_qtl_harmonize_all`, which listed 899 + 1 jobs. The real fire went through the same
script inside Slurm 1675878, with `--profile data/r4/tmp/w3e/local_profile --cores 8` and a `bsub` shim that refuses on PATH.
The log shows `Provided cores: 8`, so execution was local and nothing went to LSF. Result: `900 of 900 steps (100%) done` in
13.5 min. The follow-up dry-run says `Nothing to be done`.

**Reconciliation** (`data/r4/tmp/w3e/harmonized_reconcile.txt`; header columns 1 qtl_row_id, 5 source, 7 qtd, 8 gene_id,
9 molecular_trait_id):
```
done records 23310 rehash mismatches 0
files on disk 23310 records == files: True
distinct (source,qtd,molecular_trait_id,region) 23310  distinct (source,qtd,gene_id,region) 22804
record keys == manifest features: True
by source {'eqtl': 21149, 'sqtl': 2161}
empty outputs 0
total harmonized rows 91853028
```
- `awk 'NR>1' $MAN/qtl_harmonized_sha256.tsv | wc -l` = 23310, equal to the file count.
- The plan's literal verify keys on gene_id, column 8, and prints 22804. The 506 difference is all sQTL: 376 genes carry
  882 junctions, and 882 − 376 = 506 (see Deviation 1).
- Arithmetic: eqtl 21,149 + sqtl 2,161 = 23,310, and 23,310 × 5 traits = 116,550 manifest rows.
- No harmonizer returned empty, so no empty-output messages are listed.

**RED:** `ImportError: cannot import name 'harmonize_qtl_r4'` with the module removed (collection error). **GREEN:** 7 passed.

**Negative controls** (`data/r4/tmp/w3e/nc_t1_out.txt`; restored sha256 df93aded…):
```
NC1 no molecular_trait_id cut   1 failed: test_sqtl_partitions_the_shipped_gene_level_rows
NC2 reader not restored         3 failed: sqtl_partitions, empty_feature, reader_restored
```

## Task 2: qtl_abf + group runner + rules

**RED** (`data/r4/tmp/w3e/red_t2b.txt`; runner present, R script at its pre-change bytes, smk at Task 1). Result:
`15 failed, 15 passed`. The 15 failures are every R-driven and Snakemake test: `long flag "gwas-fit" is invalid`, plus no
`r4_qtl_group` rule. The 15 passes are pure-Python unit tests of the runner module, which was present. With the runner module
also removed, both test modules fail at collection (`red_t2.txt`).

**GREEN** (plan verify): `tests/ta_r4/test_qtl_group_runner.py tests/ta_r4/test_coloc_pair_r4.py tests/phase2/test_run_qtl_coloc.py`
gave `65 passed in 202.45s`.

**Fixture group** (2 traits × 2 eQTL features; tA and f1 carry a signal, tB and f2 are null). QTL_A3 and QTL_legacy both gave
`{'coloc_susie': 1, 'fallback_abf': 3}`, with missing [] and extra []:

| row | status (run_qtl_coloc.R) | method | fallback_reason |
|---|---|---|---|
| tA × f1 | success | coloc_susie | – |
| tA × f2 | no_qtl_cs | fallback_abf | qtl_n_cs==0 |
| tB × f1 | no_gwas_cs | fallback_abf | gwas_n_cs==0 |
| tB × f2 | no_qtl_cs (n_cs_gwas 0) | fallback_abf | gwas_n_cs==0&qtl_n_cs==0 |

- QTL_A3 orientation counters: exact 173, flipped 23, palindromic dropped 4. That sums to 200, which equals ld_panel_overlap, and
  n_snps_overlap 196 = 173 + 23.
- QTL_legacy has no qtl_orient_* keys, n_snps 200, and n_cs_qtl 3 on f1 where A3 has 1. That is the un-oriented transposed rows
  producing extra signal: E-2 in miniature.
- Each fallback's abf n_snps equals run_qtl_coloc.R's n_snps_overlap. The runner refuses the row if they differ.

**Bridge differential:** the qtl_abf variant set equals run_qtl_coloc.R's own bridged set. That set was captured by tracing
`coloc::check_dataset` (its `d$snp`) and compared by sha256 and count for {QTL_A3, QTL_legacy} × {tA×f1, tB×f2}: 196 under
join+orient, 200 ungated. The qtl_abf PPs equal a direct `coloc.abf` on those rows with the yaml priors (exact `==`).

**W0d unchanged:** the W3c CLI snapshot script ran before and after the refactor: 24 outputs, the same 4 expected refusals,
and `cmp` byte-identical (`data/r4/tmp/w3e/w0d_before.json`, `w0d_after.json`).

**Negative controls** (`data/r4/tmp/w3e/nc_t2_out.txt`; each restored sha256-identical):
```
NC1 no-CS rows labelled coloc_susie       2 failed (group methods, QTL_A3 + QTL_legacy)
NC2 legacy gets --qtl-orient false        2 failed (exact pre-fix argv, unit + recorded argv)
NC3 coverage drops missing                2 failed (coverage unit NC, deleted real output)
NC4 bridge keeps orientation drops        2 failed, 2 passed (QTL_A3 differential; legacy unaffected, as expected)
NC5 bridge always keys on chrpos          4 failed (all four differentials)
NC6 qtl_abf on p12_sensitivity            1 failed (direct coloc.abf equality)
NC7 QTL gate removed                      1 failed (fixture-repo QTL_A3 dry-run refusal)
NC8 every R failure becomes a row         1 failed (CLI exit 1 naming the missing rows)
```
The plan's coverage negative control is a test in two forms. In `test_deleted_output_fails_coverage`, deleting one real output
returns `([<id>], [])`. In `test_cli_exit_1_names_the_missing_row`, removing one feature's harmonized file gives rc 1,
`COVERAGE FAILED missing=2 extra=0`, both ids named, and no `.done` written.

**Dry-run proofs** (committed tree, HEAD 0ca16af9):
```
$ bash bin/r4_fire.sh production A3_1kg -n data/r4/results/QTL_A3/qtl/SH2B3_12q24.eqtl.QTD000116.done   -> rc 1
LockGateError: (a) lock record absent: .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/R4-LOCK.json
$ bash bin/r4_fire.sh repro repro_routeL -n data/r4/results/QTL_legacy/qtl/SH2B3_12q24.eqtl.QTD000116.done -> rc 0
r4_qtl_group 1 / total 1
$ bash bin/r4_fire.sh repro repro_routeL -n r4_qtl_all -> rc 0
r4_coloc_pair 100, r4_qtl_aggregate 1, r4_qtl_all 1, r4_qtl_group 899, r4_qtl_tiers 1; total 1002
```
The in-rule gate is shown independently by `test_qtl_A3_group_refused_without_lock`: in a fixture repo with no lock record,
Snakemake raises LockGateError at DAG time on `r4_qtl_group` (NC7 above).

## Task 3: wave close

Run under Slurm 1677128 (c024n04, HEAD 0ca16af9, 56m45s), using `data/r4/tmp/w3e/close_W3e.sh` (the W3d pattern).

| Suite | Result |
|---|---|
| QUICK | 491 passed, 83 deselected (108 s; budget 120 s) |
| HEAVY | 79 passed, 4 skipped (the same 4 W5a/W5b skips) |
| Pins (D-28) | 39 passed |
| FULL | **2048 ids = 1998 passed + 50 skipped + 0 failed** (`data/r4/tmp/w3e/full_W3e.xml`) |

**By id vs `data/r4/tmp/w3d/full_W3d.xml`** (`data/r4/tmp/w3c/reconcile.py`; output in `data/r4/tmp/w3e/reconcile_W3e.txt`):
- common 2011, removed 0, added 37, changed 0; 2011 − 0 + 37 = 2048.
- The 37 added ids all passed: test_qtl_group_runner 23, test_coloc_pair_r4 7, test_qtl_harmonize_r4 7.
- No passed→skipped. tests/m3: 1299 (1265 / 34), unchanged.
- Quick vs heavy split: +21 quick (7 + 14) and +16 heavy (9 + 7), matching QUICK 470 → 491 and HEAVY 63 → 79.
- `sparse_parent_benchmark.tsv` is clean. `git fsck --connectivity-only` reports dangling objects only, before and after each commit.

## Deviations from Plan

1. **[Rule 1 - Bug] Per-junction sQTL harmonization (not per gene_id).**
   - The manifest's sQTL feature is `molecular_trait_id` (a junction). The shipped `harmonize_sqtl()` filters on `gene_id` and
     drops `molecular_trait_id`. A gene-level file therefore holds every junction's rows, with duplicate variant_ids, and
     run_qtl_coloc.R's `match()` would bind each variant to whichever junction comes first.
   - `ta_r4.harmonize_qtl_r4` reads the window once with the shipped reader. For each feature it cuts the window to that
     `molecular_trait_id`, then runs the shipped harmonize function on the cut through a scoped reader swap. Every other step is
     shipped code.
   - Paths use `{molecular_trait_id}` where the plan wrote `{gene_id}`. They are identical for eQTL.
   - Tests: eQTL output equals the shipped CLI byte-for-byte after decompression. The sQTL junction files partition the shipped
     gene-level rows exactly (multiset equality).
   - The group job also reads the window once instead of once per id, as the plan's shell loop would have.
   - New file not in files_modified: `src/python/ta_r4/harmonize_qtl_r4.py`, plus its test.
2. **[Rule 3] Harmonize fire under Slurm, not the LSF profile.** `bin/r4_fire.sh` hard-wires `--profile config/ta_r4/cluster_lsf`
   (bsub). The fire passed a second `--profile` (a local profile under data/r4/tmp; argparse takes the last value). A `bsub` shim
   that refuses was put on PATH, and the job ran inside one Slurm job. bin/r4_fire.sh is unchanged. **W6 needs a Slurm path:**
   reuse this pattern, or add a `cluster_slurm` profile (a W6 decision).
3. **[Plan literal] "6 bridged variants → n_snps 6"** cannot hold. The replicated bridge keeps run_qtl_coloc.R's floor of 50, so
   6 variants means too_few_snps and no fallback (`test_qtl_abf_refuses_below_the_bridge_floor`). The fixture uses 200 variants,
   giving 196 bridged under join+orient and 200 ungated.
4. **[Plan literal] "2 features × 2 traits: one gwas-0, one qtl-0, the rest coloc_susie".** A GWAS fit is per (trait, region),
   so a null trait is null for both features. The fixture's four rows are therefore 1 coloc_susie, 1 qtl_n_cs==0,
   1 gwas_n_cs==0 and 1 with both reasons.
5. **Interface details the plan left open:**
   - `--gene-id` is the molecular_trait_id. The row JSON also carries `ensembl_gene_id` and `molecular_trait_id`.
   - `--sample-size` is the GTEx tissue N (`build_tissue_n_lookup.GTEX_V8_TISSUE_N_FALLBACK`, the frozen lookup's source).
     `--sdy` is `config/qtl_sources.yaml` sdY (1.0).
   - Row JSON top-level `pp_h0..pp_h4`: the best summary row for coloc_susie, the abf for fallback_abf, null for none.
   - R temporary JSONs go under `data/r4/tmp/qtl_runner/`, never under `results/*/qtl/` (run_aggregation rglobs `*.json` there).
   - `r4_qtl_tiers` builds its `--gwas-coloc` input from the fit arm's susie-mode p12_primary trait-pair JSONs (admissible EUR rows
     in the 10 QTL regions). For QTL_legacy this adds 100 `r4_coloc_pair` jobs on the repro_routeL fits.
   - The sweep table is `qtl_tiers_sweep.tsv`. The aggregate is `qtl_coloc_summary.tsv`.
6. **[Rule 3] R.utils.** The standalone `conda_envs/r_coloc` R that older tests use has no R.utils, so `fread` cannot read the
   `.tsv.gz` harmonized files. The Snakemake job env built from `envs/r_coloc.yml` pins `r-r.utils` and is the R the rules run.
   The W3e fixture therefore selects that job env by matching its yaml to envs/r_coloc.yml. Production is unaffected.
7. **New fixture module** `tests/ta_r4/fixtures/qtl_group_fixture.py`, shared by both test files.

## For Carter (W4a amendment decisions)

1. **sQTL unit = junction** (Deviation 1). The frozen layer harmonized sQTL per gene with the same shipped code, so its sQTL
   rows for multi-junction genes were mixed. This is a finding about the frozen layer to state, not to adjust.
2. **Fallback rows and tiers.** Tiers count coloc_susie rows only, as the legacy aggregator does. fallback_abf values are
   reported per row but are not tiered. The alternative is to tier fallback PPs as well.
3. **QTL_legacy tier input.** The trait-pair side is the routeL fits run through run_coloc_pair_r4.R (100 jobs). The alternative
   is the frozen trait-pair coloc, which R4 does not hold.
4. **Below-floor rows** (method none, status `ld_join_fatal:<reason>` / `too_few_snps`) are kept and counted, not dropped.
5. **Priors.** run_qtl_coloc.R uses the coloc.susie package priors, which equal the current yaml (p12_primary 5e-6). If W4a
   changes p12_primary, the runner refuses to run, and run_qtl_coloc.R would need a priors flag before the lock.
6. **W6 sizing.** Rows run serially within a group (5 to 670 rows per group, median 80). Per-row cost on real windows is
   unmeasured; the W2c estimate of 232.8 core-h is still a fixture lower bound.

## Known Stubs

None.

## Threat Flags

None. No network or auth surface. The runner calls repo scripts on local files; the gate is on the production rules (T-r4-W3e-03).

## Self-Check
Files exist: harmonize_qtl_r4.py, run_qtl_group_r4.py, ta_r4_qtl.smk, test_qtl_harmonize_r4.py, test_qtl_group_runner.py,
qtl_group_fixture.py, qtl_harmonized_sha256.tsv, full_W3e.xml, nc_t1_out.txt, nc_t2_out.txt, red_t2b.txt, harmonized_reconcile.txt.
Commits 4d27ac00 and 0ca16af9 are in `git log`.

## Self-Check: PASSED
