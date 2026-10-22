---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: W0d-pair-coloc-r4-script
subsystem: R4 trait-pair colocalization (A1 matched / A1 all-variants / coloc.susie / labelled fallback) + rules + toy e2e
tags: [ta-r4, d-01, d-02, d-21, coloc, priors, fallback, snakemake, use-conda, req-snakemake-ci]
requires: [ta-r4-W0c-receipts-validators-enforcers]
provides:
  - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R (--mode susie | A1_matched | A1_allvars)
  - src/snakemake/rules/ta_r4_coloc.smk (r4_coloc_pair; r4_coloc_A1 in A3_1kg / AFR661_A3 only; R4_COLOC_TARGETS(arm))
  - src/python/ta_r4/commands.py coloc_command / coloc_output / A1_FIT_ARMS / P12_KEYS (shared by rule and tests)
  - tests/ta_r4/test_fallback_labelled.py (named D-02 enforcer + live gate)
  - tests/ta_r4/test_priors_constant.py (named priors enforcer + live gate)
  - tests/ta_r4/test_coloc_pair_r4.py, tests/ta_r4/test_snakemake_toy_e2e.py
  - tests/ta_r4/fixtures/build_fixture_pair.R, build_toy_workflow.py
  - R4 r_coloc job env 0f3436279d4146c376747a0ea5bfd4bf_ (R 4.4.2, coloc 5.2.3, susieR 0.14.2) in the R4 conda prefix
affects: [W2a (trait_manifest.tsv; panel SNP_ID convention decides the name-override issue), W4a/W4b (decision below before the code lock), W5b (r4_coloc_pair / r4_coloc_A1 production; live gates switch on), W3d (consumes the JSON keys)]
tech-stack:
  added: []
  patterns: [one argv builder for rule and tests, fallback computed by the A1 code path (identity by construction), fail-closed name alignment, live gates over result_dirs with in-test controls, fixture-repo --use-conda e2e with a tmp-only sentinel + verify_online receipt]
key-files:
  created:
    - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
    - src/snakemake/rules/ta_r4_coloc.smk
    - tests/ta_r4/fixtures/build_fixture_pair.R
    - tests/ta_r4/fixtures/build_toy_workflow.py
    - tests/ta_r4/test_coloc_pair_r4.py
    - tests/ta_r4/test_fallback_labelled.py
    - tests/ta_r4/test_priors_constant.py
    - tests/ta_r4/test_snakemake_toy_e2e.py
  modified:
    - src/python/ta_r4/commands.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
    - .planning/ROADMAP.md
decisions:
  - "Fit-name alignment replicates run_coloc_susie.R (fit name -> sumstats SNP_ID or CHR:POS -> chr:pos key), except that an unmapped fit name stops the job (UNMAPPED_FIT_NAMES) instead of being silently dropped. The panel-rsid override shape is NOT resolved here (see Decision needed)."
  - "fallback_abf calls the same a1_matched() function as --mode A1_matched, so its PPs, n_snps and variant_set_sha256 are identical, not merely close."
  - "A1_allvars matches on CHR:POS plus unordered {REF,ALT}; rows with missing alleles match on CHR:POS only (n_matched_pos_only). Multi-row positions match on allele set only; ambiguous ones are dropped and counted (n_dropped_duplicate). Non-finite BETA/SE or SE <= 0 rows are dropped and counted (n_dropped_unusable)."
  - "coloc.susie whose PPs are all NA after trimming keeps method coloc_susie with pp_h4_max null (no new status key, no fallback); an empty summary stops the job (COLOC_SUSIE_EMPTY). An early-exit fit (no lbf_variable) stops the job (FIT_EARLY_EXIT)."
  - "dataset N = trait_manifest N_median (unused by coloc.abf when beta/varbeta are given; recorded for provenance)."
metrics:
  duration: "~95 min (2026-10-22T16:38Z-18:15Z), incl. 22m43s FULL and 7m14s HEAVY"
  completed: 2026-10-22
  tasks: 3
  files: 9 code/test (8 new + commands.py) + LOG/STATE/ROADMAP/SUMMARY
---

# Phase ta-r4 Plan W0d: R4 pair-coloc script Summary

Every R4 trait-pair number now comes from one tested R script. It takes p1, p2 and p12 only from
`config/ta_r4/coloc_priors.yaml` and writes them into every output. A pair where either trait has 0 credible sets
is labelled `fallback_abf` with a reason, and its PPs equal A1_matched exactly. `coloc_susie` reproduces a direct
`coloc::coloc.susie` call with |diff| = 0.0. Two gated rules run the script, and a toy 3-region
`Snakefile.ta_r4 --use-conda` run passes end to end under A3_1kg and A2_identity.

## Decision needed (STOP point, not chosen)

The frozen `run_susie_rss.R` renames chr:pos sumstats SNP_IDs to the LD panel's rsids, measured on the fixture as
"Overriding 59 sumstats SNP_IDs with LD-panel rsids". The plan says to replicate `run_coloc_susie.R`'s alignment.
That alignment maps fit names through the sumstats only, so on this shape it drops every non-CS variant, measured as
`fit_b=1/57 (intersect=0)`, and colocalizes nothing. Copying it literally would change what is computed. I did not
choose a mapping. Instead, `run_coloc_pair_r4.R` refuses with `UNMAPPED_FIT_NAMES` (fail closed). The plan's
rsid-vs-chr:pos shape, where both scripts agree, works.

W2a's 1000G panels take SNP_ID from the .bim, which is likely rsids. If so, every hypertension/stroke/t2d pair
(chr:pos sumstats) will refuse in W5b. The code freezes at the OSF lock, so this must be decided before W4a/W4b.
Options:
- (a) map fit names through the arm's panel variants frame as well. This adds the declared panel as a coloc input;
  for A2 the payload carries the same frame.
- (b) have W2a write chr:pos SNP_IDs into the R4 panels, so the override never fires.
- (c) another rule Carter picks.

## Commits

| Task | Commit | Content |
|---|---|---|
| 1 | `99e05961` | run_coloc_pair_r4.R, commands.coloc_command, build_fixture_pair.R, build_toy_workflow.py (shared fixture), 3 test modules |
| 2 | `c536547c` | ta_r4_coloc.smk, toy workflow builder, test_snakemake_toy_e2e.py |
| 3 | wave-close commit | LOG, STATE, ROADMAP, this SUMMARY |

## Acceptance evidence (commands run, output as observed)

### Task 1
- **RED** (script absent; fixture fits built by the frozen script through `commands.fit_command`):
  `16 failed, 14 passed, 2 skipped`. Every failure was `Fatal error: cannot open file 'src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R'`.
  The 14 passes were gate-checker unit tests on synthetic trees, each controlled below. The 2 skips were the live gates.
- **GREEN:** verify command → `30 passed, 2 skipped in 102.70s`. Skip text:
  `SKIPPED [1] tests/ta_r4/test_fallback_labelled.py:134: no R4 coloc result dir exists yet (W5b enables)`
  and the same line for `test_priors_constant.py:126`.
- **Fixture numbers (verbatim prints):**
  - coloc_susie (FIXP_SAME, n_cs 2 / 1): `pp_h4_max 0.999999999998337 direct 0.999999999998337 max|diff| 0.0`
  - fallback (FIXP_NULL, `n_cs_b==0`):
    - `p12_primary: fallback pp_h4 0.0267819546730813 A1_matched pp_h4 0.0267819546730813`
    - `p12_sensitivity: fallback pp_h4 0.0521667809824499 A1_matched pp_h4 0.0521667809824499`
    - the test asserts all five PPs with `==`
  - A1_matched (FIXP_MIX):
    - `p12_primary: n_snps 57 pp_h4 0.999441327677598 direct 0.999441327677598 max|diff| 0.0; package-default pp_h4 0.999720585788306`
    - the negative control asserts the package-default value `!=` ours
  - A1 allvars: n_snps 60 = 59 allele-matched + 1 position-only, ≥ matched 57. The transposed B row matches; the B row
    with no alleles matches on position only.
- **Differential vs run_coloc_susie.R** (A rsid-named, B chr:pos-named): its stdout `chr:pos rewrite fit_a=59/59
  fit_b=57/57 (intersect=57)`; mine n_snps 57. Hits, nsnps and idx are identical. PPs agree to its JSON precision: it
  writes jsonlite default `digits=4` (5 significant digits), so the comparison is `rel_tol=1e-4`.
- **Reader check:** the frozen script reads sumstats with `fread(cmd = "gunzip -c <path>")`, and so does
  `run_coloc_pair_r4.R`. run_coloc_susie.R uses `fread(<.bgz>)`, which needs R.utils. The named r_coloc env lacks it
  (measured `To read gz files directly, fread() requires 'R.utils'`), so there it silently skips its rewrite. The R4-solved env has R.utils 2.12.3.
- **Sabotage REDs** (each restored, `cmp` identical):
  - `P12 <- 1e-5` hard-coded → `2 failed, 7 passed, 1 skipped`, with `test_priors_constant.py:57: assert ('p12_primary' == 'p12_primary' ...` and
    `:72: assert (1e-05 == 1e-05 and 0.999999999999169 != 0.999999999999169)`.
  - fallbacks labelled `coloc_susie` → `2 failed, 8 passed, 1 skipped`, `assert ('coloc_susie' == 'fallback_abf'`.
  - Gate-checker controls:
    - glob every `results/*/coloc` → both repro-tree tests RED;
    - n_cs check removed → the mislabelled-row case RED;
    - p12 not compared → `[over0-p12 1e-05 != yaml 5e-06]` RED;
    - cross-arm check made a no-op → `test_gate_flags_cross_arm_p12` RED.
  - UNMAPPED refusal disabled → `test_panel_rsid_override_is_refused_not_dropped` RED.

### Task 2
- **RED** (rule moved aside): `4 failed, 1 passed`. The A3 run failed with rc 1 in 1.0 s on `MissingRuleException: No rule to produce
  data/r4/results/A1_EUR/coloc/FIX_1__EUR__asthma_vs_bmi.matched.p12_primary.json`. The 1 pass is the receipt negative
  control, which exercises only the existing fit rule.
- **First r_coloc solve into the R4 prefix** happened in that RED run, through the negative control's `--use-conda` fit job. It produced env
  `0f3436279d4146c376747a0ea5bfd4bf_`: R 4.4.2, coloc 5.2.3, susieR 0.14.2, data.table 1.16.4, R.utils 2.12.3, yaml 2.3.10,
  jsonlite 2.0.0, digest 0.6.39, optparse 1.7.5.
- **Shared cache** `/rs1/researchers/c/ckclinto/conda_pkgs`:
  - before: 2188 entries, listing sha256 `f094b37d…9085`, 23348 MB, 0 archives;
  - after every `--use-conda` run (toy RED, GREEN, HEAVY): identical on all four measures, and 0 entries newer than the start marker;
  - R4 pkgs dir: 809 → 1095 entries (546 archives); envs 3 → 4.
- **GREEN:** `5 passed in 92.07s`.
  - `toy A3_1kg: rc 0, 24 targets, wall 50.3 s`: 6 fits, 6 coloc, 12 A1.
  - `toy A2_identity: rc 0, 12 targets, wall 26.0 s`.
  - All 12 fits have receipts and `validate_fit == []`.
  - The live-gate functions, run on the fixture tree, give 24 JSONs in A3_1kg / A2_identity / A1_EUR with no violations.
  - Methods are coloc_susie at FIX_1/2 and fallback_abf at FIX_3 in both arms.
  - At FIX_3, A3 fallback = A2 fallback = A1 matched in PPs and variant_set_sha256.
- **Negative control:** with the FIX_2 row deleted from the A3 panel manifest and the fit forced, the run gives rc 1 with `Error in rule r4_run_finemap:` and
  `LD_RECEIPT_REFUSED: no manifest row (EUR, FIX_2) in .planning/.../manifests/panels_EUR_1kg_r4.tsv`.
- **Coloc gate refusal** (added; fixture repo, no sentinel, the A1 allvars target, which has no fit dependency): OsfGateError
  `sentinel absent` in rule r4_coloc_A1. With the gate call removed, the result is `MissingInputException in rule r4_coloc_A1` (RED), and the file was restored.
  My first sabotage run of this test was void: the test had put the target after `--configfile`, which consumes it as a
  config file. I fixed the argument order and re-ran both.
- **Production dry-run in the real repo** (`bash bin/r4_fire.sh production A3_1kg -n data/r4/results/A3_1kg/coloc/SH2B3_12q24__EUR__bmi_vs_hypertension.p12_primary.json`):
  - before the commit: `REFUSED: uncommitted changes in the analysis tree (the receipt binds HEAD): ?? src/snakemake/rules/ta_r4_coloc.smk`, rc 2;
  - after the commit: `OsfGateError: (a) sentinel absent: .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/OSF-R4-POSTED.json`, rc 1.
    This comes from the fire script's verify-online step, and Snakemake never starts.
  - Direct `$SMK -n` (no fire script): `InputFunctionException in rule r4_coloc_pair ... OsfGateError: (a) sentinel absent`, and the same in
    r4_coloc_A1. The gate fires before any panel or fit path is resolved.
  - No `data/r4/gate/`, no sentinel, and no `carter-approved` text were written. data/r4/results stays empty.
- `bash bin/r4_fire.sh repro repro_routeC --list` → rc 0 and lists `r4_coloc_pair`. `r4_coloc_A1` is listed under the A3_1kg overlay only.

### Task 3 (wave close, §C)
- QUICK `time $PY -m pytest tests/ta_r4 -x -q -m 'not r4_heavy'` → `254 passed, 39 deselected`, real **36.7 s**.
  The slowest test is `test_m3_conftest_import_still_works` at 9.0 s (pre-existing).
- HEAVY → `35 passed, 4 skipped, 254 deselected` (7m14s). The 4 skips are the live gates (silent identity, matched sets, fallback, priors).
- Freeze pins → `39 passed`.
- FULL → `1717 passed, 50 skipped, 4 warnings in 1362.88s`, rc 0 (junit `data/r4/logs/full_W0d.xml`).
- **Join by junit id vs W0c** (`full_W0c.xml`): baseline 1729 (1681 / 48), new 1767 (1717 / 50). Common 1729, **removed 0, changed 0, added 38**:
  - by module: coloc_pair 11, fallback 11, priors 10, toy 6;
  - by outcome: 36 passed + 2 skipped (live gates).
  - Reconciliation: 1729 + 38 = 1767, 1681 + 36 = 1717, 48 + 2 = 50.
  - Split: QUICK 254 − 235 = 19 new, HEAVY 39 − 20 = 19 new, and 19 + 19 = 38.
  - tests/m3: 1299 baseline ids, 0 missing, 0 changed.
  - `tests/m3/sparse_parent_benchmark.tsv` was restored.
- `git diff --quiet HEAD --` over run_susie_rss.R, run_coloc_susie.R, Snakefile, config/pipeline.yaml, finemap.smk,
  envs/r_coloc.yml and Snakefile.ta_r4 → 0.
- `git fsck --connectivity-only` before the first commit: dangling blobs only (0 other lines).

## Deviations from Plan

1. **[STOP point, fail-closed; affects what is computed if resolved] Name alignment on the panel-rsid override shape.**
   See "Decision needed". The script refuses rather than drop variants silently. Where `run_coloc_susie.R`'s
   semantics are correct, it reproduces them (differential test).
2. **[Rule 3] `commands.py` gained `coloc_command` / `coloc_output` / `A1_FIT_ARMS` / `P12_KEYS`.** This file is not in
   files_modified. W0c's convention is that the rule and the tests share one argv builder.
3. **[Rule 3] Fixture sumstats are built per region by `build_fixture_pair.R` (with `--seed`), then concatenated,
   bgzipped and tabixed in Python.** The plan named `build_fixture_region.R` for the toy regions. That builder
   hard-codes seed 20261021 and writes one trait per file, so it cannot give 3 seeds × 2 traits in one sumstats file per
   trait. The seeds follow the plan (20261021 + k). `build_toy_workflow.py` was created in Task 1 because the Task 1 tests share its region builder.
4. **[Rule 3] `--conda-frontend conda` was added to the toy Snakemake command.** The R4 profile pins it (W0b2: mamba is
   found in condabin, and isolation was measured for conda only). The toy does not use the profile.
5. **[Detail] Fixture design.** The traits are asthma (cc) and bmi (quant, sdY 1.0, from the trait manifest), and the panel SNP_IDs are chr:pos.
   The plan's "rsid names and chr:pos names" case needs a panel without rsids, because otherwise the frozen script renames both fits to panel rsids.
   - Trait B has one transposed row and one row with missing alleles, which exercise allvars matching.
   - FIX_3 / FIXP_NULL give B no signal, which exercises the fallback.
   - FIXP_OVR (rsid panel) reproduces the override shape.
6. **[Detail] Output keys.** The output keys go beyond the plan's list for provenance: trait_a/b, ancestry, region_id, type_a/b, sdY_a/b, p12_key, `summary`
   (all CS-pair rows), and the allvars counts (null in the other modes). `test_output_keys_exact` pins the full set.
7. **[Detail] The sdY test asserts PP.H0 moves, not PP.H4.** On this fixture PP.H4 is saturated: 0.999441327582268 at sdY 1 and
   at sdY 2. PP.H0 moves from 4.97e-35 to 4.29e-41, which shows sdY reaches coloc.abf.
8. **[Detail] The differential PP comparison uses rel_tol 1e-4**, the precision of run_coloc_susie.R's JSON writer (see Task 1).

## Hand-offs

- **W2a:** write `config/ta_r4/trait_manifest.tsv` with columns `trait, ancestry, type (cc|quant), sdY, sdY_source, N_median`.
  A quant trait without a finite sdY > 0 stops the coloc job (`SDY_MISSING`). The panel SNP_ID convention decides the override issue above.
- **W4a/W4b:** resolve "Decision needed" before the analysis-code lock.
- **W5b:** targets come from `R4_COLOC_TARGETS(arm)`. A1 runs only in the A3_1kg / AFR661_A3 invocations. The fallback and priors
  live gates switch on as soon as any `result_dirs("coloc")` dir exists, and a dir with 0 JSONs fails.
  An early-exit fit (too_many_variants / no_variants) stops its coloc job (`FIT_EARLY_EXIT`); W5b must decide how those rows are reported.
- **Lockfile:** the R4-solved r_coloc env (`0f343627…_`) has no committed lockfile. W0b2 committed one for the *named*
  env only. Versions are listed above.

## Known Stubs

None. The live gates skip by design until W5b, and the in-test controls show they fail when they should.

## Threat Flags

None beyond the plan's threat model. The script reads only its argv files and writes one JSON. The toy test writes a
fixture sentinel and receipt only under pytest tmp_path, and calls verify_online with a fake fetch (no network).

## Self-Check: PASSED

All 8 created files are tracked: Task 1 files at `99e05961`, Task 2 files at `c536547c`. Both commits exist. The QUICK, HEAVY,
FULL and join numbers above are as observed.
