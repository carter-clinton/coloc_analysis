---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 13
slug: W3c-simulation-harness
subsystem: ta-r4 E8 simulation calibration
tags: [simulation, susie-rss, coloc, known-truth, pre-lock]
requires: [ta-r4-W3b-sh2b3-known-answer-and-findings]
provides:
  - src/snakemake/scripts/ta_r4/simulate_coloc_r4.R (E8 harness)
  - config/ta_r4/simulation.yaml (design; locked false until W4b)
  - src/snakemake/rules/ta_r4_sim.smk (r4_sim, gated; r4_sim_all; R4_SIM_TARGETS)
  - run_coloc_pair_r4.R::coloc_pair_core (shared coloc core; main-guarded)
affects: [W4a (amendment cites the harness commit), W4b (locks simulation.yaml), W5c (100-job production run)]
tech-stack:
  added: []
  patterns: [frozen functions parsed out of the frozen file (no copy), sys.nframe() main guard, header-comment TSV status]
key-files:
  created:
    - config/ta_r4/simulation.yaml
    - src/snakemake/scripts/ta_r4/simulate_coloc_r4.R
    - src/snakemake/rules/ta_r4_sim.smk
    - tests/ta_r4/test_simulation_harness.py
  modified:
    - src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
decisions:
  - "Harness SuSiE = the frozen run_susie_rss.R functions (%||%, regularize_ld, run_susie_with_ladder) parsed out of the frozen file at load time, not a copy; the fit wrapper mirrors the script's R symmetrize/unit-diagonal, L = min(L, m), identity fallback and annotate_susie"
  - "simulation.yaml per-trait sample size key is n_per_trait: R yaml reads a bare `n:` key as FALSE (YAML 1.1)"
  - "simulation.yaml carries the 10 admissible region ids (sorted) so the stable seed index is self-contained and lockable"
  - "H3 causal pair: uniform over ordered (c1, c2), c1 != c2, with r^2 in the closed bin under the fit panel; H4: one uniform causal; mean and covariance both use the PSD-clipped generation R"
metrics:
  duration: "~2 h 40 min (2026-11-03 19:21 EST start; wave close Slurm 1672481 ended 21:02 EST)"
  completed: "2026-11-03"
  tasks: 2
  files: 7
---

# Phase ta-r4 Plan W3c: Simulation Harness Summary

The E8 harness simulates z ~ N(R·sqrt(n)·b, R) from the PSD-clipped generation-panel window. It fits A2 (R = I) and A3 (fit
panel) with the frozen run_susie_rss.R ladder, whose functions are parsed out of the frozen file at load time rather than copied. It
runs A1/A2/A3 coloc through the same `coloc_pair_core` as the real-data CLI. Its PIPs equal the frozen script's (max |ΔPIP| 0.0) and its
PPs equal the CLI's (max |ΔPP| 0.0). The 100-job rule is production-gated; no production simulation was run.

## Commits

| Task | Commit | Subject |
|---|---|---|
| 1 | 0efac930 | feat(ta-r4-W3c): E8 simulation harness, config and gated rule |
| 2 | (docs commit after this SUMMARY) | feat(ta-r4-W3c): wave close — LOG, STATE, ROADMAP, SUMMARY |

## Precondition

`cd src/python && $PY -m ta_r4.signoff verify W3b-T3` → exit 0. Carter's instructions (`proceed. 1. ive read it, 2. lets fix these
mismatches, ... 4. findings dont change the pre-reg`): none concerns the simulation design. Item 4 applies: the design values are the
plan's.

## Task 1

**RED** (harness, config and rule absent): `4 failed, 17 errors in 6.98s`. Failure causes: `'.../simulate_coloc_r4.R' is not an
existing file` (11 R-driven setups), FileNotFoundError on `config/ta_r4/simulation.yaml`, and no `r4_sim` rule.

**Refactor** run_coloc_pair_r4.R: the top-level body moved into `main()`; `dataset`, `run_abf`, `a1_matched` and
`coloc_pair_core(fa, fb, ti_a, ti_b, pri, mode, labels)` are top-level and take explicit priors/labels; `if (sys.nframe() == 0L) main()`.
W0d CLI before/after on the W0d pair fixture: 4 regions × 2 p12 keys × 3 modes = 24 outputs (20 JSON + 4 expected `UNMAPPED_FIT_NAMES`
refusals on FIXP_OVR A1_matched/susie). Parsed-dict diff `{}`, and the snapshot files are byte-identical (`cmp`).
Script: `data/r4/tmp/w3c/w0d_cli_snapshot.py`.

**GREEN:** `tests/ta_r4/test_simulation_harness.py` 21 passed. Plan verify (`test_simulation_harness.py test_coloc_pair_r4.py
test_fallback_labelled.py test_priors_constant.py`): `51 passed, 2 skipped` (the 2 pre-existing W5b "no R4 coloc result dir" skips).

- Generator (5×5 AR(0.6), 20,000 draws): max |cov − R| 0.0231, max |mean| 0.0140 (b = 0); max |mean − R·sqrt(n)b| 0.0061.
  Same seed identical, different seed different. The PSD clip equals V·diag(pmax(λ,0))·Vᵀ (min eigenvalue ≥ −1e-10).
- SuSiE identity: frozen script via `commands.fit_command` on a fixture with BETA = z/sqrt(n), SE = 1/sqrt(n), N = n (60 variants,
  no allele drops). A2_identity: max|ΔPIP| 0.0, 5 = 5 CS. A3_1kg: max|ΔPIP| 0.0, 1 = 1 CS. Both converged_primary.
- Coloc identity: harness rows equal the run_coloc_pair_r4.R CLI on the harness's own fits for A1_matched, A2 susie and A3 susie:
  max|ΔPP| 0.0; method and n_cs equal.
- no_qualifying_pair (R = I window, H3_r2_0.6): header `# status=no_qualifying_pair`, column header, 0 rows.

**Negative controls** (`-B -p no:cacheprovider`; each file restored, sha256 identical; `data/r4/tmp/w3c/nc_out.txt`):

```
NC1 frozen call + estimate_residual_variance=TRUE  FAILED test_susie_identity_vs_frozen_script[A2_identity], [A3_1kg]   2 failed
NC2 L = policy L - 5                                FAILED test_susie_identity_vs_frozen_script[A2_identity]            1 failed, 1 passed
NC3 harness p12 = p12_sensitivity                   FAILED test_coloc_identity_harness_vs_cli                          1 failed
NC4 no PSD clip                                     FAILED test_generator_psd_clip                                     1 failed
NC5 seed off by one                                 FAILED test_seed_is_stable_index_..., test_output_seeds_and_determinism  2 failed
NC6 H3 bin ignored                                  FAILED test_h3_causal_pair_in_bin, test_h3_output_pairs_in_bin     2 failed
NC7 rule without the lock gate                      FAILED test_sim_rule_refused_without_lock                          1 failed
NC8 rule passes --reps-override 2                   FAILED test_sim_rule_100_jobs_..._no_reps_override (assert not True)  1 failed
```
NC2 leaves A3 green because the A3 fixture fit has a single CS, so L = 5 does not move it; A2 (5 CS) catches it.

**Gate:** `bash bin/r4_fire.sh production A3_1kg -n data/r4/results/sim/SH2B3_12q24.H4.gen_1kg.tsv; echo $?` → `1`,
`LockGateError: (a) lock record absent: .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/R4-LOCK.json`. Snakemake level
(fixture repo): without a lock record the sim target is refused at DAG time; with a fixture lock, `r4_sim_all` dry-runs as 100
`r4_sim` jobs, and no printed shell line contains `--reps-override`.

**Smoke** (pre-gate; not used in any estimate): `data/r4/tmp/sim_smoke/SH2B3_12q24.H4.gen_1kg.tsv` (realpath /rs1/.../ta_r4/tmp/sim_smoke/), 6.2 s:

```
# simulate_coloc_r4 region=SH2B3_12q24 scenario=H4 gen_panel=gen_1kg
# reps_override=2
# status=ok
# n_qualifying_pairs=NA
# window_variants=745 reps=2 config_sha256=147b85964da4a8b3bbbd7dff0565143840ef91ef5d7b630b1598d484083fee99
region	scenario	gen_panel	rep	seed	arm	method	pp_h0	pp_h1	pp_h2	pp_h3	pp_h4	pp_h4_max	n_cs_a	n_cs_b	causal_a	causal_b	r2_causal
SH2B3_12q24	H4	gen_1kg	1	20278622	A1	A1_abf_matched	1.16e-15	4.46e-06	5.22e-13	5.56e-07	0.999995	0.999995	NA	NA	12:111894952	12:111894952	1
SH2B3_12q24	H4	gen_1kg	1	20278622	A2	coloc_susie	7.37e-17	9.62e-07	1.53e-13	6.42e-08	0.999999	0.999999	7	1	12:111894952	12:111894952	1
SH2B3_12q24	H4	gen_1kg	1	20278622	A3	coloc_susie	7.02e-17	9.16e-07	1.53e-13	6.54e-07	0.999998	0.999998	1	1	12:111894952	12:111894952	1
```
PP columns are rounded here for width; the file carries full precision. Seed check: SH2B3 is region 9 of 10 and H4 is scenario 5 of 5,
so ((8·5·2) + 4·2 + 0)·200 + 1 = 17601, and 20261021 + 17601 = 20278622. The H3_r2_0.6 smoke has 4782 qualifying pairs, and rep 1 has
r² 0.5764.

## Task 2: wave close (§C; Slurm 1672481, c207n03, HEAD 0efac930, 1h05m)

Scheduler switched from LSF to Slurm per Carter (2026-11-03). Job PATH = the login PATH (sbatch `--export=ALL`; `Rscript` is not on PATH
in either place, the same as under LSF: tests use absolute R paths). Skips reconciled by id below.

| Suite | Result |
|---|---|
| QUICK | 371 passed, 67 deselected (97 s) |
| HEAVY | 63 passed, 4 skipped (21m44s; the same 4 W5a/W5b skips) |
| Pins (D-28) | 39 passed |
| FULL | 1912 ids = 1862 passed + 50 skipped + 0 failed (41m56s, `data/r4/tmp/w3c/full_W3c.xml`) |

By id vs `data/r4/tmp/261102-log/full_261103.xml` (`data/r4/tmp/w3c/reconcile.py`): common 1891, removed 0, added 21 (all
`test_simulation_harness`, all passed), changed 0; 1891 − 0 + 21 = 1912. The 50 skipped ids are the same 50 (0 changed outcomes, so no
passed→skipped). tests/m3 1299 (1265 / 34) unchanged. `sparse_parent_benchmark.tsv` clean. `git fsck --connectivity-only`: no
broken/missing links before or after the Task 1 commit (dangling only). run_susie_rss.R 0-diff vs 53106f8.

## Deviations from Plan

1. **[Rule 1 - Bug] `n` → `n_per_trait` in simulation.yaml.** R `yaml` reads the bare key `n:` as boolean FALSE (YAML 1.1), so the
   harness got `cfg$n = NULL` and every susie_rss call errored (`argument is of length zero`). The Python config test passed because
   PyYAML keeps `n`. The key was renamed, and the harness now refuses missing or non-positive numeric config keys (`CONFIG` error).
2. **[Rule 2] Frozen SuSiE functions parsed, not mirrored.** The plan said "frozen-call mirror". The harness instead evaluates the frozen
   file's own `%||%`, `regularize_ld` and `run_susie_with_ladder` definitions, so the call cannot drift. The plan's NC (flip
   `estimate_residual_variance`) was done by replacing the ladder call in the harness with a direct `susie_rss(..., estimate_residual_variance
   = TRUE)` call, which is the frozen call with that one argument flipped (NC1).
3. **Interface details the plan left open:** `coloc_pair_core(fa, fb, ti_a, ti_b, pri, mode, labels)` (fa/fb = `list(fit, keys, rows)`;
   `fit = NULL` allowed for A1 → n_cs NA), not `(fit_a, fit_b, ds_a, ds_b, priors, mode)`. Harness CLI adds `--gen`, `--policy`,
   `--credible-set` (the rule passes `ARMS["A3_1kg"]["policy"]` and `config.finemap.credible_set`, as fit_command does).
   `--fit-panel/--gen-panel` are .rds paths whose directory must equal the config panel name (PANEL error otherwise). simulation.yaml
   also carries the 10 admissible region ids (tested equal to the pair_manifest primary EUR admissible set) and `p12_key: p12_primary`.
4. **Added `rule r4_sim_all`** (input `R4_SIM_TARGETS`) so the 100-job count and the no-`--reps-override` property are testable by dry
   run (the same check W5c will make from the printed shell).
5. **Test-code fixes before the first green** (my own new test file, pre-commit): str.format braces in two R templates, the shell-line
   filter matching the `input:` line, and the fixture LD (binary genotype LD had no pair in 0.55–0.65; replaced by AR(0.985)).
   Harness `fwrite` uses `quote = FALSE` (with `na = "NA"` it quoted every string).

## Known Stubs

None.

## Notes for W3d / W5c

- TSV readers must skip `#` header lines (`status`, `reps_override`, `n_qualifying_pairs`, `config_sha256`). A `no_qualifying_pair` file
  has 0 data rows and must be counted, never filled in.
- A1 rows have n_cs NA by design. Panel sizes (isect EUR): SH2B3 745 (window = all 745); the other 9 are 1120–12746 (window = 1000). The largest panel R (PYHIN1, 12746²) is ~1.3 GB in memory, within mem_mb 8000.
- coloc.abf prints its PP summary to stdout; the rule sends it to the job log.

## Self-Check
Files exist: simulation.yaml, simulate_coloc_r4.R, ta_r4_sim.smk, test_simulation_harness.py, smoke TSV, full_W3c.xml.
Commit 0efac930 is in `git log`.

## Self-Check: PASSED
