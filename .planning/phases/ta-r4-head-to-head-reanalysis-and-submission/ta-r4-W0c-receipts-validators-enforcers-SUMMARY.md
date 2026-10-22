---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: W0c-receipts-validators-enforcers
subsystem: D-13 receipts / validator / R4 fit rule / matched variant sets
tags: [ta-r4, d-13, d-28, d-01, silent-identity, ld-receipt, frozen-script, snakemake, fixture-e2e]
requires: [ta-r4-W0b2-pair-manifest-osf-gate-workflow]
provides:
  - src/python/ta_r4/validate_r4_fits.py (validate_fit, classify_fit, manifest_row, validate_file, production_fit_dirs, CLI exit 1 on any violation)
  - src/python/ta_r4/write_ld_receipt.py (per-fit .ld_receipt.json; exit 3 on md5 mismatch / missing row / duplicate key / absent non-legacy panel)
  - src/python/ta_r4/commands.py (fit_command / receipt_command / validate_command, shared by the rule and the e2e tests)
  - src/snakemake/rules/ta_r4_finemap.smk (rule r4_run_finemap)
  - src/snakemake/scripts/ta_r4/make_matched_identity_payload.R (A2 payload = A3 variants frame + diag(n))
  - tests/ta_r4/test_no_silent_identity.py (named D-13 enforcer: unit + live gate)
  - tests/ta_r4/test_arm_variant_sets_identical.py (named matched-set enforcer: fixture + live gate)
  - tests/ta_r4/test_frozen_script_armed_e2e.py + fixtures/build_fixture_region.R
affects: [W0d, W2a (EUR_1kg_r4 panels + manifest feed the receipt; A2 payloads via make_matched_identity_payload.R), W2b (AFR661_A2 / isect pairs), W3a (repro arms run through r4_run_finemap with legacy_any), W5a/W5c/W6 (live gates go active)]
tech-stack:
  added: []
  patterns: [one argv builder shared by rule and test, receipt-before-fit md5 gate, validator after the frozen script, in-test controls for live gates, fixture repo real Snakemake run]
key-files:
  created:
    - src/python/ta_r4/validate_r4_fits.py
    - src/python/ta_r4/write_ld_receipt.py
    - src/python/ta_r4/commands.py
    - src/snakemake/rules/ta_r4_finemap.smk
    - src/snakemake/scripts/ta_r4/make_matched_identity_payload.R
    - tests/ta_r4/fixtures/build_fixture_region.R
    - tests/ta_r4/test_no_silent_identity.py
    - tests/ta_r4/test_frozen_script_armed_e2e.py
    - tests/ta_r4/test_arm_variant_sets_identical.py
  modified:
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
    - .planning/STATE.md
    - .planning/ROADMAP.md
decisions:
  - "Script choice follows ARMS[arm]['script'], not route: repro_routeC is route legacy but runs the current frozen script with its full argument list (ld-authoritative/allele-aware false from the repro overlay); only arms whose script is the 3dd76df copy get the 3dd76df option set."
  - "--ld-dir for legacy_any arms is data/r4/ld/<panel_dir> (the legacy {ld_dir}/{ancestry}/{region}.rds layout of legacy_repro and k2d_identity); production arms get data/r4/ld_dir_unused, which must not exist."
  - "SUSIE_MAX_VARIANTS=16000 is carried inside the argv as `env SUSIE_MAX_VARIANTS=16000 Rscript ...` so the e2e tests run the identical environment; Python steps run as `env PYTHONPATH=src/python <snakemake python> -m ...`."
  - "conda: str(Path(workflow.basedir)/'envs'/'r_coloc.yml') (the W0b2 convention). It is byte-identical to src/snakemake/rules/envs/r_coloc.yml, which plain 'envs/r_coloc.yml' would resolve to; the fixture repo copies only top-level envs/."
  - "The rule's input function calls the OSF gate FIRST, then checks resolve_ld_path == ta_r4.paths.panel_path at DAG time (WorkflowError on mismatch)."
  - "Legacy_any receipts: an absent panel is recorded (present false); a PRESENT legacy panel must still match its manifest row md5 (exit 3), so a swapped repro panel also stops the job."
  - "The validator also checks receipt sha256, the receipt's arm validator_mode against the CLI mode, and that the receipt's declared path is ta_r4.paths.panel_path(arm, region_safe, ancestry)."
metrics:
  duration: "~40 min active + 19.5 min FULL (2026-10-22T15:56Z-16:40Z)"
  completed: 2026-10-22
  tasks: 3
  files: 9 code/test + LOG/STATE/ROADMAP/SUMMARY
---

# Phase ta-r4 Plan W0c: Receipts, validators, enforcers Summary

The frozen `run_susie_rss.R` exits 0 on three silent identity shapes, so an R4 fit's exit code is not
treated as evidence. A post-fit validator is. Each fit now writes an LD receipt bound to the committed panel
manifest by md5/sha256. The new rule `r4_run_finemap` runs: OSF gate, then resolved-equals-declared, `test -s`,
receipt, the unedited script armed only by flags, the validator, and the existing receipt one-liner. On a 60-SNP
fixture this shows the authoritative, allele-aware EUR read (1 flipped, 1 palindrome dropped, 59/60 retained), and
A2 and A3 retain identical variant sets. A missing declared panel still exits 0 on identity, and the validator rejects it.

## Commits

| Task | Commit | Content |
|---|---|---|
| 1 | `dbc2c19d` | validate_r4_fits.py, write_ld_receipt.py, test_no_silent_identity.py |
| 2 | `fef3589f` | commands.py, ta_r4_finemap.smk, make_matched_identity_payload.R, build_fixture_region.R, test_frozen_script_armed_e2e.py, test_arm_variant_sets_identical.py, live-gate controls in test_no_silent_identity.py |
| 3 | wave-close commit (see LOG) | LOG, STATE, ROADMAP, this SUMMARY |

## Acceptance evidence (commands run, output as observed)

### Task 1
- **RED** (test written first): `pytest tests/ta_r4/test_no_silent_identity.py -q` → `55 failed in 2.20s`, every failure
  `ModuleNotFoundError: No module named 'ta_r4.validate_r4_fits'` or `No module named ta_r4.write_ld_receipt`.
- **GREEN:** `54 passed, 1 skipped in 1.64s`, with `-rs`: `SKIPPED [1] ...: no production fits yet (W5a enables)`.
  There are 24 injected negative shapes, each asserted by violation name: 19 real_ld + 5 identity_matched. Also covered:
  3 positives, 4 legacy_any classifications, 6 early-exit cases, manifest lookup/duplicate/no-ancestry,
  3 CLI cases, and 9 receipt-writer cases.
- **Sabotage RED** (`conv = ""`, i.e. `convergence_status` ignored), run with `-B`:
  ```
  FAILED tests/ta_r4/test_no_silent_identity.py::test_silent_shape_rejected_by_name[a2_identity_fallback]
  FAILED tests/ta_r4/test_no_silent_identity.py::test_silent_shape_rejected_by_name[identity_fallback]
  2 failed, 52 passed, 1 skipped in 0.87s
  ```
  Restored (`cmp` identical) → `54 passed, 1 skipped`.
- **Receipt-writer control** (md5 comparison disabled): `FAILED test_receipt_writer_exits_3[md5_mismatch]`, `1 failed, 53 passed`. Restored identical.
- **CLI from src/python** on an identity fixture (`ld_matrix identity`, `ld_status ld_dir_missing`): it printed 5 lines
  (`VIOLATION LD_MATRIX_IDENTITY`, `LD_DIR_MISSING`, `LD_STATUS_NOT_LOADED`, `IDENTITY_SUBSTRING`, `LD_MATRIX_NE_DECLARED`), then
  `validate_r4_fits mode=real_ld n=1 early_exit=0 ld_source_class=missing violations=5`, and `echo $?` → **1**.

### Task 2
- **RED** (tests written before `commands.py` and the rule): `3 failed, 1 passed, 1 skipped, 6 errors`.
  The 6 errors were the session fixture failing with `ImportError: cannot import name 'commands' from 'ta_r4'`.
  The 3 failures:
  - `test_rule_runs_on_fixture_repro_arm`
  - `test_rule_production_arm_refused_without_gate`: no OsfGateError in the output
  - `test_rule_listed_via_fire_script`: `--list` showed no `r4_run_finemap`

  The 1 pass was `test_pairs_are_production_arms` and the 1 skip was the live gate.
- **GREEN:** verify command (e2e + variant + freeze pins) → `49 passed, 1 skipped in 26.78s`. After the controls were
  added, e2e 9 + variant 4 + silent 56 gave `67 passed, 2 skipped`.
- **Fixture A3 JSON:** `ld_matrix` = `data/r4/ld/EUR_1kg_r4/FIX_1.rds` (== `ld_file_declared`), `ld_status` =
  `ld_loaded;overlap_ok;59;0.983`, `ld_allele_flipped` = **1**, `ld_allele_dropped_palindromic` = **1**, `status ok`.
  A2: `ld_matrix data/r4/ld/EUR_identity_r4/FIX_1.rds`, same ld_status, PIPs differ from A3 (asserted).
  **Retained variants: A3 59, A2 59**, identical id sets. 59 = 60 − 1 palindrome = `ld_overlap` on both.
- **Missing-panel negative control, observed outcome (verbatim test print):**
  `NC outcome: rc 0; {'ld_matrix': 'identity', 'ld_status': 'ld_dir_missing', 'ld_file_declared': 'data/r4/ld/EUR_1kg_r4/FIX_1.rds'} violations: ['LD_MATRIX_IDENTITY', 'LD_DIR_MISSING', 'LD_STATUS_NOT_LOADED', 'IDENTITY_SUBSTRING', 'LD_MATRIX_NE_DECLARED']`.
  So the outcome was the **named violation**, not a non-zero exit, and the validator CLI returned rc 1.
- **Rule runs** (fixture repo from `make_fixture_repo` + fixture inputs at FTO_16q12 coordinates):
  - repro_routeC ran `r4_run_finemap` for real. The printed shell contains `shlex.join` of all three `commands.*`
    argvs, the receipt has `present: true` / `legacy_panel`, the JSON reads the legacy panel with `ld_authoritative false`,
    and the estimate_s log reads `ld_fields_present`.
  - A3_1kg dry-run → `OsfGateError ... sentinel absent`.
  - Manifest md5 swapped → rc ≠ 0 with `LD_RECEIPT_REFUSED: declared md5 ... != manifest md5`. The frozen script never
    started and no JSON was written.
- **Sabotage controls** (each restored, `cmp` identical):
  - (a) `--ld-file` dropped → the A3 fit ran **rc 0 at `status ok` on `ld_matrix identity` / `ld_dir_missing`** (the D-13
    hazard itself); `test_command_runs_the_frozen_script` and `test_a3_reads...` went RED.
  - (b) receipt md5 check off → `test_rule_fails_on_panel_swap` went RED.
  - (c) payload drops a variant → `retained variants: A3 59, A2 58`, and the fixture set test went RED.
  - (d) gate call removed from the input function → `test_rule_production_arm_refused_without_gate` went RED.
- **Live gates** (`test_live_r4_fits_have_no_identity`, `test_live_matched_arms_have_identical_variant_sets`) skip while
  no result dir exists. Each has an in-test control that is GREEN only because the gate reports a planted problem:
  - D-13 gate: an empty arm dir gives "0 fit JSONs", and an identity fit gives `LD_MATRIX_IDENTITY`.
  - Matched-set gate: a lone A3 gives "A2_identity present=False but A3_1kg present=True", and a 58-id A2 gives the
    "58 ids != 59 ids" line.
  - The D-13 gate's dir list == `result_dirs("fits")`, which contains A3_1kg_isect and no repro dir.
- **Matrix::Diagonal (plan question):** measured on the fixture. A `Matrix::Diagonal(60)` payload is accepted by the frozen
  loader (rc 0, `ld_loaded;overlap_ok;59;0.983`, `converged_primary`), because the loader returns `as.matrix(R)`. The builder
  uses base `diag(n)` as specified.
- **D-28:** `git diff --quiet HEAD -- src/legacy/region_analysis/scripts/run_susie_rss.R; echo $?` → `0`; `test_source_freeze_pins.py` → `39 passed`.
- `bash bin/r4_fire.sh repro repro_routeC --list` → rc 0, `r4_run_finemap` listed.

### Task 3 (wave close, §C)
- QUICK `time $PY -m pytest tests/ta_r4 -x -q -m 'not r4_heavy'` → `235 passed, 20 deselected`, real **18.8 s**.
- HEAVY → `18 passed, 2 skipped, 235 deselected` (231 s). 20 = 6 (W0b2) + 14 (W0c).
- FULL (`tests/ta_r4 tests/m3 tests/phase1 tests/phase2 -q -rA --junitxml=data/r4/logs/full_W0c.xml`) →
  `1681 passed, 48 skipped, 4 warnings in 1168.39s`, rc 0.
- **Join by junit id vs W0b2** (`full_W0b2.xml`): baseline 1660 (1614 passed / 46 skipped), new 1729 (1681 / 48).
  The two runs have 1660 ids in common, with **0 removed** and **0 changed**. **69 ids were added**: test_no_silent_identity 56, e2e 9,
  variant_sets 4, of which 67 passed and 2 skipped (the live gates).
  Reconciliation: 1660 + 69 = 1729, 1614 + 67 = 1681, 46 + 2 = 48. tests/m3: 1299 baseline ids, 0 missing, 0 changed.
  `tests/m3/sparse_parent_benchmark.tsv` was restored after the run.
- `git fsck --connectivity-only` was clean before the first commit (dangling blobs only). The after-commit check and the push result are in the hand-back and the LOG.

## Deviations from Plan

1. **[Interpretation] Script selection by `ARMS[arm]["script"]`, not by route.** The plan says "route `legacy` arms call
   3dd76df". W0b1's ARMS gives repro_routeC/repro_k2d_routeC/repro_sh2b3_r2 `route: legacy` with the *current* script
   (Route C = current code, legacy semantics). Following the plan text literally would have put Route C on 3dd76df. Only
   routeL arms get the 3dd76df option set. This does not contradict W0b2.
2. **[Rule 3] `--ld-dir` for legacy_any arms = `data/r4/ld/<panel_dir>`.** The plan's `--ld-dir data/r4/ld_dir_unused`
   applies to every arm. For repro arms that would make the frozen loader find no panel. The plan says the legacy code
   "resolves `{ld_dir}/{ancestry}/<file>` itself", and paths.MULTI_ANCESTRY_PANEL_DIRS uses that layout.
3. **[Rule 3] `conda:` = `workflow.basedir/envs/r_coloc.yml`** instead of the literal `"envs/r_coloc.yml"`. The literal
   resolves rule-relative (src/snakemake/rules/envs/r_coloc.yml, byte-identical). The fixture repo copies only top-level
   `envs/`, so the first real rule run failed with `Failed to open source file .../rules/envs/r_coloc.yml`. This matches W0b2's ta_r4_env.smk.
4. **[Detail] `SUSIE_MAX_VARIANTS=16000`** is passed as `env SUSIE_MAX_VARIANTS=16000 Rscript ...` inside the argv, not as a
   separate `export` line. The e2e tests then run the identical environment. Python steps are `env PYTHONPATH=src/python <python> -m`.
   finemap.smk's `{PYTHON_BIN}` is `sys.executable`, and so is ours.
5. **[Rule 2] Extra validator checks:** receipt sha256 (both modes), receipt arm's validator_mode == CLI mode,
   receipt.declared == `paths.panel_path(arm, …)`, and receipt.declared == fit's ld_file_declared. The receipt writer
   also refuses `--legacy-any` on a non-legacy arm (and the reverse), and a `--stage` that differs from ARMS.
   A *present* legacy panel must match its manifest md5.
6. **[Rule 2] The rule's input function runs the OSF gate before resolving the panel**, and raises WorkflowError if
   `resolve_ld_path` != `paths.panel_path`. Otherwise a missing panel raises FileNotFoundError ahead of the gate.
7. **[Detail] Tests added beyond the plan:** rule-level real run on a repro fixture repo, production refusal, manifest-swap
   failure, receipt one-liner equivalence (executed, not text-compared), and in-test controls for both live gates.
   The live-gate refactor touched test_no_silent_identity.py in the Task 2 commit.
8. **[Detail] `status` vs `ld_status`:** the frozen script writes `ld_dir_missing` into `ld_status` (final `status` is ok /
   non_converged). The validator checks both fields.

## Hand-offs

- **W2a / W2b:** the panel manifests must have the columns `ancestry, region_safe, md5, sha256` (plus the rest of the §A
  columns) with a unique key. The receipt writer exits 3 on a duplicate key or a missing ancestry column. Build A2 / AFR661_A2
  payloads with `src/snakemake/scripts/ta_r4/make_matched_identity_payload.R --in <A3 .rds> --out <A2 .rds>`. Do not give
  them a `status` field: the loader would use it as ld_status, and the validator requires `^ld_loaded;`.
- **W3a:** repro arms need `panels_legacy_repro*.tsv` rows for every present legacy panel (md5-checked), and the catalog at
  `data/r4/ld/variants_legacy/`. 3dd76df arms need `data/r4/legacy_code/run_susie_rss_3dd76df.R`, which does not exist yet.
- **W5a / W5c / W6:** the two live gates switch on as soon as any production fit dir exists. A dir with zero fit JSONs fails.
- **R4 r_coloc env:** `r4_run_finemap` under `bin/r4_fire.sh` (`--use-conda`) will solve `envs/r_coloc.yml` into the R4
  prefix the first time. That env was NOT solved in this wave. The e2e tests used `$RSCRIPT` (the named r_coloc env).

## Known Stubs

None. The live gates skip by design until W5a. In-test controls show that they fail when they should.

## Threat Flags

None beyond the plan's threat model. The rule adds no network access. The receipt writer reads only the declared panel,
manifest, overlays and policy, and runs `git rev-parse HEAD`.


## Self-Check: PASSED

All 9 created files are tracked at `fef3589f`; commits `dbc2c19d` and `fef3589f` exist. QUICK/HEAVY/FULL/join numbers above are as observed.
