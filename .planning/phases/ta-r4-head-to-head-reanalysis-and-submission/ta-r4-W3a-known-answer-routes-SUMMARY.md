---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 11
slug: W3a-known-answer-routes
subsystem: ta-r4 known-answer reproduction
tags: [susie-rss, reproduction, known-answer, legacy-code, lsf]
requires: [ta-r4-W2d-apply-review-decisions]
provides:
  - data/r4/legacy_code/run_susie_rss_3dd76df.R (Route L code)
  - 382 repro fits under data/r4/results/{repro_routeC,repro_routeL,repro_k2d_routeC,repro_k2d_routeL}
  - manifests/known_answer_W3a.tsv (per-fit Route C vs Route L vs frozen)
affects: [W3b (findings checkpoint reads known_answer_W3a.tsv and these findings)]
tech-stack:
  added: []
  patterns: [LSF exit-255 stall watchdog (no RUN/PEND job for 5 min -> kill, unlock, re-fire)]
key-files:
  created:
    - bin/r4_extract_legacy_code.sh
    - src/snakemake/rules/ta_r4_repro.smk
    - src/python/ta_r4/known_answer_compare.py
    - tests/ta_r4/test_known_answer_repro.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/legacy_code_sha256.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/fits_repro_sha256.tsv
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/known_answer_W3a.tsv
  modified:
    - src/python/ta_r4/commands.py (repro_fit_keys, safe_region_id, k2d_record_rows; fit_command unchanged)
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
decisions:
  - "Real-LD and k2d fit sets come from the frozen k2d record: real-LD = its 8 trait.ancestry x 12 regions (96); k2d = its 95 rows"
  - "The alternate refs 0948a76 / 1635d37 were not run. Their run_susie_rss.R blob (75f2d34) is identical to 3dd76df, and Route L reproduced the k2d record on status and n_CS"
  - "fits_repro_sha256.tsv lists fit .json + .fit.rds only (2 x 382 = 764); receipts are not listed"
metrics:
  duration: 295 min (2026-10-29T01:07Z to 06:03Z; mostly LSF fire)
  completed: 2026-10-29
  tasks: 3
  files: 10
---

# Phase ta-r4 Plan W3a: Known-Answer Routes Summary

Both routes reproduce each other exactly: 3dd76df legacy code (Route L) and current frozen code under iter-100
reproduction semantics (Route C). That holds for 96/96 real-LD and 95/95 k2d fits, with PIPs bitwise equal. Route L
reproduces the k2d record on status (95/95) and n_CS (95/95), and the frozen real-LD non-empty count (51/96). The
frozen real-LD status split differs by 4 fits (44 ok / 22 non_converged, against 48 / 18), and the k2d record's
cs_sizes column turns out to be a summariser defect. Both are recorded as findings.

## Commits

| Task | Commit | Subject |
|---|---|---|
| 1 | 49a8f47b | feat(ta-r4-W3a): Route L legacy-code extraction + repro fit targets |
| 2 | 741f44b5 | chore(ta-r4-W3a): fire the four repro arms; manifest 382 fits |
| 3 | 26a6bb5f | test(ta-r4-W3a): known-answer comparison tool, live test, committed table |
| close | (this docs commit) | docs(ta-r4-W3a): wave close |

Interleaved: 037fc14c and 31c27614 are an orchestrator handoff written during the fire. They are not this executor's commits.

## Task 1: legacy code and repro rules

- `git fsck --no-dangling` clean. At 3dd76df, `run_susie_rss.R` has only `library()` calls, so there are no `source()`
  dependencies. `legacy_code_sha256.tsv` has 2 rows (the tree copy + `run_susie_rss_3dd76df.R`, sha256 62fbe9da…).
  `git hash-object` of the copy = 75f2d34 = `git rev-parse 3dd76df:<path>`.
- `git log 3dd76df..08beb4c -- src/legacy/region_analysis/scripts/` is empty. The script blob is 75f2d34 at 3dd76df,
  0948a76, 1635d37 and 08beb4c. `config/susie_policy.yaml` is 0-diff vs 3dd76df.
- Resolver negative controls (scratch repo): a literal `source()` chain → 3 files extracted; `source(f)` →
  `REFUSED: non-literal`, rc 4; `source("nope.R")` → `REFUSED ... not in HEAD`, rc 4. The first draft swallowed the
  refusal (rc 0) inside process substitution. It was fixed before the 3dd76df run.
- The W0c legacy branch was already complete. `fit_command` is unchanged and **ta_r4_finemap.smk is untouched**. Route
  L prints `Rscript data/r4/legacy_code/run_susie_rss_3dd76df.R ... --ld-dir data/r4/ld/legacy_repro ... --policy
  config/susie_policy.yaml` with no `--ld-file`. Route C passes `--ld-authoritative false`, which makes the current
  script ignore `--ld-file` entirely.
- The k2d record lacks one combination, bmi.EUR.APOE_19q13. It was "absent from the k2d Snakemake manifest input"
  (260425-kki PLAN:1110; TRACK-A-FROZEN-NUMBERS.md:26).
- Dry-run `r4_repro_fits`: **96 / 96 / 95 / 95** `r4_run_finemap` jobs = 382. W0c e2e + W0d toy e2e: `15 passed`.

Panel availability (checker W-3), reconciled from the receipts:

| Ancestry | Fits | With legacy_repro panel | Without |
|---|---|---|---|
| EUR | 5 × 12 = 60 | 5 × 10 = 50 | 5 × {HLA_6p21, BMI_Xq24} = 10 |
| AFR | 3 × 12 = 36 | 3 × 12 = 36 (n_AFR = 12; all `use_identity` placeholders, W2b) | 0 |
| Total | 96 | 86 (receipts legacy_panel/present) | 10 (receipts missing/absent) |

k2d: all 95 fits have a k2d_identity payload (95 legacy_panel receipts). Of the 10 panel-absent EUR fits, 9 exit early
(HLA: asthma/hypertension/stroke/t2d too_many_variants; Xq24: asthma/bmi/hypertension/stroke no_variants, t2d
too_many_variants). bmi.EUR.HLA_6p21 fits with no panel (ok, n_CS 10). Their statuses equal the k2d record for the same
10 fits. The frozen HLA EUR real-LD fire used UKBB-LD tiles (INVENTORY §2), so any per-fit difference there comes from
the absent panel, not from code drift.

## Task 2: fires

- Per arm, JSON / .fit.rds / receipts: routeC 96/96/96, routeL 96/96/96, k2d_routeC 95/95/95, k2d_routeL 95/95/95. Each
  re-run with `-n` reports "Nothing to be done".
- `fits_repro_sha256.tsv` rows = 764 = 2 × (96 + 96 + 95 + 95).
- Infrastructure: 15 jobs died at LSF start with exit 255 ("Cannot open your job file"; 1 with an empty .err): C 7,
  L 4, k2dC 1, k2dL 3. The known stall followed (Snakemake waits with no job alive). The first stall was stopped by
  hand: kill, `--unlock`, re-fire. After that, `data/r4/tmp/w3a_fire_chain.sh` handled it with a watchdog (no RUN/PEND
  job for 5 minutes → kill -9, unlock, re-fire, at most 4 attempts) and `--max-jobs-per-second 2`. Three stalls were
  caught. No job failed in R, and no reproduction failure occurred.

## Task 3: comparison (RED → GREEN)

RED (module absent):

```
E   ImportError: cannot import name 'known_answer_compare' from 'ta_r4' (.../tests/ta_r4/__init__.py)
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 1.43s
```

Negative controls (in place, `PYTHONDONTWRITEBYTECODE=1`, pycache cleared, restored and checked with `cmp`):
- tolerance 1e-10 → 1e-8 plus id-set short-circuit: `FAILED test_pip_perturbation_1e9_not_equal`,
  `FAILED test_missing_variant_reported_not_nan_filled` (2 failed, 5 passed);
- `build_table` drops the first row: live test `assert (95 == 96)`, 1 failed;
- one committed table cell edited: live test 1 failed.

GREEN: `8 passed` (live test run, 0 skips).

Headline (known_answer_W3a.tsv, 191 rows = 96 real_ld + 95 k2d; every count reconciles to its total):

| Comparison | Equal | Differ | Total |
|---|---|---|---|
| Route C ≡ Route L, real-LD (status, n_CS, cs_sizes, ids, max abs dPIP ≤ 1e-10) | 96 | 0 | 96 |
| Route C ≡ Route L, k2d | 95 | 0 | 95 |
| k2d status vs record (C = L) | 95 | 0 | 95 |
| k2d n_CS vs record (C = L) | 95 | 0 | 95 |
| k2d cs_sizes vs record (C = L) | 47 | 48 | 95 |

max |ΔPIP| = 0 on all 131 fits with a PIP vector (66 real-LD + 65 k2d). The 60 early exits (30 + 30) have no PIP
vector; status, n_CS and cs_sizes are compared for them.

Real-LD aggregates (C = L) vs TRACK-A-FROZEN-NUMBERS.md:

| | ok | non_converged | too_many_variants | no_variants | total | non-empty |
|---|---|---|---|---|---|---|
| reproduced | 44 | 22 | 24 | 6 | 96 | 51 |
| frozen | 48 | 18 | 24 | 6 | 96 | 51 |

k2d aggregates reproduced: 65 / 24 / 6 and non-empty 48/95 (= record).

## Findings (§B.10: recorded, nothing adjusted)

1. **No code drift under reproduction semantics.** Current code with `ld_read_path` off and iter-100 produces
   bitwise-identical fits to the 3dd76df code: 191/191.
2. **k2d record cs_sizes column is a summariser defect.** It equals `len("CS<i>")` for i = 1..n_CS on 95/95 rows (a
   must-be-identity check, not a near-miss): `3` per set, `4` for CS10. The summariser iterated the CS dict keys. The 48
   cs_sizes "mismatches" are exactly the 48 non-empty fits. Per-fit cs_sizes cannot be checked against this record;
   status and n_CS match 95/95.
3. **Real-LD status split differs by 4 fits.** 44 ok / 22 non_converged against the frozen 48 / 18. Non-empty (51) and
   the early-exit counts match. The per-fit frozen table was purged, so the 4 fits cannot be identified. Per-fit
   evidence that survives: bmi.EUR.APOE_19q13 non_converged n_CS 6 = frozen (1/1); the 10 04-21 narrow-validation
   survivor fits (FTO + SH2B3 EUR, a pre-fire run) match 10/10 on status, n_CS and cs_sizes.
4. **Frozen-record internal tension (SH2B3 EUR).** Line 72 calls asthma "sole ok SH2B3 EUR fit". Reproduction (and the
   04-21 survivor) also gives t2d ok (n_CS 9), consistent with line 222 (asthma_vs_t2d was the only SH2B3 EUR manifest
   row, and the manifest admits only ok fits). Asthma ld_overlap_fraction 0.0385 is reproduced.
5. **Scope caveat.** Both routes used the same R env (r_coloc, susieR 0.14.2). Route C ≡ Route L measures code drift
   only. Environment drift since 04-22 is a candidate for finding 3 and was not tested.

## Wave close (§C)

LSF 432078 (c017n03, HEAD 741f44b5):
- QUICK `346 passed, 52 deselected in 100.36s`
- HEAVY `48 passed, 4 skipped, 346 deselected in 1228.63s`; the 4 skips are the same W5a/W5b reasons as W2d
- pins `39 passed`
- FULL (full_W3a.xml) tests 1872 / failures 0 / errors 0 / skipped 50 → 1822 passed (38m31s)

By-id reconciliation vs full_W2d.xml (1864 / 1814 / 50 / 0): common 1864, removed 0, added 8 (all
`tests.ta_r4.test_known_answer_repro::*`, passed), changed 0. 1814 + 8 = 1822 passed and 50 skipped unchanged. tests/m3
1299 ids unchanged. `sparse_parent_benchmark.tsv` was restored, and `run_susie_rss.R` is 0-diff.

## Deviations from Plan

1. **[Rule 1 - Bug] `/rs1/researchers` literal in src.** The first close job (431883) failed QUICK on
   `test_storage_on_rs1::test_no_rs1_or_share_literals_in_r4_config_and_src`. `known_answer_compare.RSCRIPT` now reads
   `R4_RSCRIPT` (default `Rscript`), and the live test pins the r_coloc Rscript. The table was regenerated and is
   sha256-identical (8b58f2db…).
2. **[Rule 3 - Blocking] LSF exit-255 stalls.** I added a fire-chain watchdog plus `--max-jobs-per-second 2`, in data/r4/tmp,
   not committed. These were infrastructure retries without changing `mem_mb`, because the failures were not memory.
3. **[Rule 1 - Bug] Extraction resolver** swallowed a refusal inside process substitution. I fixed it before the real run.
4. **Plan-text notes.** The plan's `<verify>` dry-run with no target lists only `r4_gate_probe` (1 job). The 96/96/95/95
   counts come from target `r4_repro_fits`. The real-LD frozen comparison is aggregate-only plus spot checks, as the
   plan anticipated. The PIP loader streams Rscript stdout, because GPFS left `TemporaryDirectory` cleanup failing
   (ENOTEMPTY on empty dirs, which were removed).
5. Precondition note (orchestrator context): `decision_rules.yaml` / `simulation.yaml` are absent and treated as
   unlocked. This plan does not read them.

## Known Stubs

None.

## Self-Check: PASSED

- FOUND: bin/r4_extract_legacy_code.sh, src/snakemake/rules/ta_r4_repro.smk, src/python/ta_r4/known_answer_compare.py,
  tests/ta_r4/test_known_answer_repro.py, manifests/{legacy_code_sha256,fits_repro_sha256,known_answer_W3a}.tsv,
  data/r4/legacy_code/run_susie_rss_3dd76df.R
- FOUND commits: 49a8f47b, 741f44b5, 26a6bb5f
