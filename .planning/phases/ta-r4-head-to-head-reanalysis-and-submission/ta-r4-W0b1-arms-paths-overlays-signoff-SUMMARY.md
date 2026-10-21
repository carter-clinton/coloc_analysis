---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: W0b1-arms-paths-overlays-signoff
subsystem: arms / paths / overlays / Carter sign-off
tags: [ta-r4, arms, overlays, paths, signoff, sentinels, auto-mode-guard]
requires: [ta-r4-W0a-storage-envs-survivors]
provides:
  - src/python/ta_r4/arms.py (ARMS: 13 arms, 8 production + 5 repro; arm_stage, production_arms, arm_ancestries)
  - src/python/ta_r4/paths.py (panel_path/panel_template, panel_manifest_path, fit_json/fit_rds/ld_receipt_json, sumstats_path, catalog_path, coloc_json, ld_dir_unused, regions_csv, result_dirs)
  - src/python/ta_r4/signoff.py (SCHEMAS, SignoffError, parse_signoff, record_signoff, verify_signoff, canonical_sha256, CLI)
  - config/ta_r4 overlay_base + 13 arm overlays, susie_policy_repro_iter100.yaml, coloc_priors.yaml
  - tests/ta_r4/test_signoffs.py conditional sentinels (vacuous in the real repo until the guarded files exist)
  - tests/ta_r4/__init__.py import-clash fix (src/python first + pkgutil.extend_path)
affects: [W0b2 (Snakefile.ta_r4 imports ta_r4.arms/paths), W0c, W0d, W2a/W2c (trait_manifest source columns), every Carter checkpoint]
tech-stack:
  added: []
  patterns: [code-owned stage table, ARMS-derived result globs, chain-replace + pin overlays, typed sign-off token parsed by code, conditional sentinels tested on fixture repos]
key-files:
  created:
    - src/python/ta_r4/__init__.py
    - src/python/ta_r4/arms.py
    - src/python/ta_r4/paths.py
    - src/python/ta_r4/signoff.py
    - config/ta_r4/overlay_base.yaml
    - config/ta_r4/overlay_{A3_1kg,A2_identity,A3_ukb,A3_ukb_isect,A3_1kg_isect,AFR661_A3,AFR661_A2,AFR504_A3,repro_routeC,repro_routeL,repro_k2d_routeC,repro_k2d_routeL,repro_sh2b3_r2}.yaml
    - config/ta_r4/susie_policy_repro_iter100.yaml
    - config/ta_r4/coloc_priors.yaml
    - tests/ta_r4/test_overlay_semantics.py
    - tests/ta_r4/test_import_isolation.py
    - tests/ta_r4/test_signoff.py
    - tests/ta_r4/test_signoffs.py
  modified:
    - tests/ta_r4/__init__.py
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
    - .planning/ROADMAP.md
decisions:
  - "ta_r4 import clash fixed per the orchestrator decision: tests/ta_r4/__init__.py puts src/python first and extends __path__; proven by test_import_isolation.py (RED without extend_path)"
  - "Repro arms carry ancestry ('EUR','AFR') (sh2b3: ('EUR',)); multi-ancestry panel dirs legacy_repro and k2d_identity use {panel_dir}/{ancestry}/{region_safe}.rds, the legacy loader's layout"
  - "ARMS rows carry an extra `script` key (current run_susie_rss.R vs data/r4/legacy_code/run_susie_rss_3dd76df.R); route is r4|legacy and selects catalog (variants_r4|variants_legacy) and the bmi.EUR D-18 sumstats"
  - "Sign-off records also store min_date and extra_required so verify can re-parse; signoff CLI has --signoff-dir (needed for tmp_path tests; no validation override)"
  - "Trait-manifest sentinel contract: a Carter-resolved cell F has its source in column F_source = 'Carter <token date>'; review_decisions.yaml carries trait facts under trait_facts: {trait.<t>.<anc>.<field>: value}"
metrics:
  duration: "~35 min (2026-10-21T21:34Z start)"
  completed: 2026-10-21
  tasks: 3
  files: 25 code + LOG/STATE/ROADMAP/SUMMARY
---


# Phase ta-r4 Plan W0b1: Arms, paths, overlays, sign-off Summary

All 13 arms are defined in one code-owned table, `ta_r4.arms.ARMS` (8 production, 5 repro).
Every R4 path comes from `ta_r4.paths`, and every result glob comes from
`result_dirs()`, which reads ARMS. The 14 overlays replace the LD chain wholesale and pin it.
The base config is unchanged. `ta_r4.signoff` accepts only `carter-approved YYYY-MM-DD` plus
the checkpoint's exact keys, so the auto-mode string `approved` cannot be recorded.
`test_signoffs.py` ties each guarded configuration state to a valid sign-off.

## Commits

| Task | Commit | Content |
|---|---|---|
| 1 | `714df7a5` | arms.py, paths.py, `__init__`s (incl. the tests/ta_r4 import fix), 14 overlays, repro policy, priors, test_overlay_semantics.py, test_import_isolation.py |
| 2 | `c6e9297f` | signoff.py, test_signoff.py, test_signoffs.py |
| 3 | (docs commit) | LOG, STATE Track A bullet, ROADMAP tick, this SUMMARY |

## Acceptance evidence (commands run, output as observed)

### Task 1
- **RED (modules and overlays absent)**, `pytest tests/ta_r4/test_overlay_semantics.py tests/ta_r4/test_import_isolation.py -q`:
  ```
  tests/ta_r4/test_overlay_semantics.py:9: in <module>
      from ta_r4 import arms as arms_mod
  E   ImportError: cannot import name 'arms' from 'ta_r4' (/gpfs_common/.../tests/ta_r4/__init__.py)
  ERROR tests/ta_r4/test_overlay_semantics.py
  1 error in 0.72s
  ```
- **Import-clash negative control.** Modules implemented, and `tests/ta_r4/__init__.py` holds only the `sys.path` insert (no `extend_path`). Result: `test_import_isolation.py` → `E ModuleNotFoundError: No module named 'ta_r4.arms'`, `1 failed, 1 passed`, and test_overlay_semantics still fails at collection with the same ImportError. After adding `__path__ = __import__("pkgutil").extend_path(__path__, __name__)`: `27 passed in 1.52s`. `test_source_modules_resolve` asserts that `ta_r4.paths.__file__` and `ta_r4.arms.__file__` sit in `src/python/ta_r4`. `test_m3_conftest_import_still_works` runs a subprocess pytest in both orders: a tests/ta_r4 test plus `tests/m3/test_ld_npz_to_rds.py::test_bm_to_npz_omitted_allele_freq_is_all_nan_and_warns`, a module that does `from conftest import R_SUBPROCESS_TIMEOUT_S`. It asserts rc 0 and `2 passed`. That m3 test was picked because it is 0.01 s; the full module is 76 s, too slow for QUICK.
- **Pin-removal negative control.** `sed -i '/^  pin:/d' config/ta_r4/overlay_A3_1kg.yaml` gives `E AssertionError: assert None == 'EUR_1kg_r4'`, `FAILED ...test_production_overlay_arms_and_pins[A3_1kg]`, `1 failed, 24 passed`. After restoring the file: `25 passed`.
- **result_dirs relabel negative control.** `test_result_dirs_reads_arms_not_a_literal` monkeypatches ARMS to relabel repro_routeC as production and asserts its dirs appear. It passes against the real code. To prove that test can fail, `result_dirs` was temporarily switched to a hard-coded list of the 8 production arms (run with `-B`): `AssertionError: assert 'data/r4/results/repro_routeC/fine_mapping/susie' in [...]`, `FAILED ...test_result_dirs_reads_arms_not_a_literal`, `1 failed, 24 passed`. After restoring (`cmp` identical): `25 passed`.
- `$PY -c "...from ta_r4.arms import ARMS;print(sorted(ARMS))"` →
  `['A2_identity', 'A3_1kg', 'A3_1kg_isect', 'A3_ukb', 'A3_ukb_isect', 'AFR504_A3', 'AFR661_A2', 'AFR661_A3', 'repro_k2d_routeC', 'repro_k2d_routeL', 'repro_routeC', 'repro_routeL', 'repro_sh2b3_r2']`. 13 arms, 8 with stage production; 13 = 8 + 5.
- `git diff --quiet HEAD -- config/pipeline.yaml Snakefile src/snakemake/rules/finemap.smk src/legacy/region_analysis/scripts/run_susie_rss.R; echo $?` → `0`. `git diff --quiet HEAD -- src/snakemake/rules/` → `0`.
- `diff config/susie_policy.yaml config/ta_r4/susie_policy_repro_iter100.yaml`:
  ```
  10c10
  <   max_iter_retry: 200
  ---
  >   max_iter_retry: 100
  ```
  Recorded max_iter values: `config/susie_policy.yaml` primary 100 / retry 200; `config/susie_policy_L15.yaml` primary 500 / retry 1000; the repro policy primary 100 / retry 100. `test_repro_policy_differs_only_in_retry` pins this.
- `result_dirs("fits")` returns 8 dirs, including `A3_1kg_isect`. `result_dirs("coloc")` returns 10 dirs = 8 production + `A1_EUR` + `A1_AFR`. No repro dir appears in either list.
- `test_storage_on_rs1.py` (the literal scan now covers the new config/ta_r4 and src/python/ta_r4 files) → `7 passed`.

### Task 2
- **RED:** `pytest tests/ta_r4/test_signoff.py tests/ta_r4/test_signoffs.py -q` → `E ModuleNotFoundError: No module named 'ta_r4.signoff'` (both modules), `2 errors in 0.15s`.
- **GREEN:** `57 passed in 1.21s` (35 + 22).
- **Relaxed-regex negative control, run twice:**
  - NC1 is exactly as the plan specifies: `TOKEN_RE = re.compile(r"^(carter-)?approved")`. Result: `8 failed, 27 passed`. Every *valid* reply now fails, because group 1 is the prefix, not a date. The bare-`approved` rejection tests stay green, because the second layer still raises: the absent date fails `_date`, and the missing required key also raises. So this literal relaxation does not show the bare-`approved` test going RED.
  - NC2 is a relaxation that actually admits the auto-mode string: `^(?:carter-)?[Aa]pproved\.?(?: (\d{4}-\d{2}-\d{2}))?$`, with the date falling back to today. Result: `FAILED test_rejections[approved\ninstructions: x\n]`, `FAILED test_rejections[carter-approved\ninstructions: x\n]`, `2 failed, 33 passed`. A bare `approved` with no keys is still rejected (missing key).
  - Restored (`cmp` identical) → `57 passed`.
- **Fixture negative controls** (problem lists printed from the check functions on fresh tmp repos):
  ```
  locked, no sign-off: ['W4a-T3: WAIT: no sign-off recorded at <tmp>/.../signoffs/W4a-T3.yaml']
  kappa differs: ["locked config kappa_cut=0.6 != W4a-T3 '0.7'"]
  W9 checked, no W9-T4: ['W9-T4: WAIT: no sign-off recorded at <tmp>/.../signoffs/W9-T4.yaml']
  trait cell edited: ["trait_manifest trait.bmi.EUR.sdY='1.1' != W2c-T4 '1.0'"]
  confirmatory edited: ['decision_rules confirmatory block sha256 != W4a-T3 confirmatory_sha256']
  ```
  Each matching positive fixture (consistent sign-off) returns `[]`.
- **Each sentinel blinded (`return []`) → its fixture tests go RED:** check_locks 4 failed; check_review_decisions 4 failed; check_w9_roadmap 1; check_osf_sentinel 1; check_venue_overlay 1; check_all_signoffs_verify 1. After restoring (`cmp` identical): green.
- CLI: `test_cli_record_bare_approved_exits_1` runs `python -m ta_r4.signoff record W3b-T3 --raw-file <approved> --min-date 2026-10-01 --signoff-dir <tmp>`. It asserts rc 1, `WAIT:` in the output, and no file written. `test_cli_record_then_verify` asserts record rc 0, verify rc 0, and verify of an absent id rc 1 with `WAIT:`.
- Real repo: there is no signoffs/ dir, review_decisions.yaml, locked config, tracked sentinel, venue overlay or checked W9 line, so the 6 `test_real_repo[...]` cases pass vacuously, as the plan expects.

### Task 3 (wave close, §C)
- QUICK `time $PY -m pytest tests/ta_r4 -x -q -m 'not r4_heavy'` → `91 passed in 6.38s`, real `0m8.348s` (< 120 s). 91 = 7 storage + 2 import + 25 overlay + 35 signoff + 22 signoffs.
- HEAVY → `91 deselected` (no r4_heavy tests yet; exit 5 as in W0a).
- `tests/m3/test_source_freeze_pins.py` → `39 passed`.
- FULL (`tests/ta_r4 tests/m3 tests/phase1 tests/phase2 -q -rA`) → `1519 passed, 46 skipped, 4 warnings in 907.42s (0:15:07)`, rc 0. Collection: `1565 tests collected`.
- Join by id vs `manifests/tests_baseline_W0a.tsv`: `collected 1565 outcomes {'passed': 1519, 'skipped': 46}`; `baseline 1474 common 1474 removed 0 added 91 changed 0`. Added by file: test_storage_on_rs1 7 (W0a), test_import_isolation 2, test_overlay_semantics 25, test_signoff 35, test_signoffs 22, all passed. Arithmetic: 1474 + 91 = 1565, and 1428 + 91 = 1519 passed. tests/m3 is unchanged (all 1299 baseline ids common, 0 outcome changes). The 5 `ERROR ...` lines in the log are captured log output from passing tests (`r_boom: ...`, `regBAD: ...`), not outcomes, as W0a recorded. `tests/m3/sparse_parent_benchmark.tsv` was restored after the run.
- fsck and push results are in the LOG entry.

## Deviations from Plan

1. **[Orchestrator decision, Rule 3 — blocking] `ta_r4` package clash fixed in `tests/ta_r4/__init__.py`.** It inserts `<repo>/src/python` (absolute, from `__file__`) at the front of sys.path, then sets `__path__ = pkgutil.extend_path(__path__, __name__)`. New test `tests/ta_r4/test_import_isolation.py` (not in files_modified) proves both properties, with RED observed when the extend_path line is absent. Both files were committed in Task 1.
2. **[Negative-control finding] The plan's literal relaxed regex does not turn the bare-`approved` test RED.** The parser has a second layer: a missing date or a missing key raises anyway. A relaxation that also defaults the date (NC2) does turn it RED. Both runs are recorded above. Nothing was weakened.
3. **[Detail] ARMS has an extra `script` key, and repro ancestry is a tuple.** `paths.panel_path(arm, region_safe, ancestry=None)` needs `ancestry` for the multi-ancestry dirs (`legacy_repro`, `k2d_identity`, layout `{dir}/{ancestry}/{region_safe}.rds`). Helper `arm_ancestries` added. `paths` also exports `panel_template`, `fit_rds` and `ld_receipt_json` (the `.fit.rds` / `.ld_receipt.json` siblings). All paths are repo-relative strings.
4. **[Detail] Repro overlays set chains for both EUR and AFR** (repro_sh2b3_r2 too), so no repro arm ever falls through to a Track B panel chain. finemap/paths keys are not set in the overlays (not specified; left for W0b2's Snakefile.ta_r4, which has `paths.ld_dir_unused()`).
5. **[Detail] The sign-off record stores `checkpoint_id`, `min_date` and `extra_required`** in addition to the specified fields, so verify can re-parse. The CLI takes `--signoff-dir` (default `signoffs/`), which tmp_path tests need. No environment variables are read and there is no validation override. `canonical_sha256` (sorted-key compact JSON) is the serialization for `confirmatory_sha256`.

## Hand-offs

- **W2a / W2c (trait manifest):** the W2c-T4 sentinel reads Carter-resolved cells as column `F` plus `F_source == "Carter <token date>"`. W2a's planned columns have `sdY_source` but no `type_source`. If hypertension `type` is UNRESOLVED, W2a must add a `type_source` column, or the sentinel will report the signed field as having "no Carter-sourced trait_manifest cell". `review_decisions.yaml` must carry trait facts as `trait_facts: {trait.<t>.<anc>.<field>: value}`.
- **W4a:** the confirmatory_sha256 Carter signs must be `ta_r4.signoff.canonical_sha256(decision_rules["confirmatory"])`. The checkpoint should print it from that function.

## Known Stubs

None. `coloc_priors.yaml` has `locked: false` by design (W4b flips it), and `citation_check` is a reminder for W4a.

## Threat Flags

None. No new network endpoints or auth paths. The sign-off CLI writes only under the given signoff dir and never overwrites.

## Self-Check: PASSED

All 12 listed files and 14 overlays exist and are tracked; commits 714df7a5 and c6e9297f exist; QUICK re-run after the docs edits: 91 passed.
