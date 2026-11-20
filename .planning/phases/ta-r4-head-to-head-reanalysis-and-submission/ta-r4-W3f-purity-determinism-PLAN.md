---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7f
slug: W3f-purity-determinism
type: execute
wave: 15.7f
depends_on: ["ta-r4-W3f-none-rows-denominators"]
gap_closure: true
files_modified:
  - .planning/DECISIONS.md
  - src/legacy/region_analysis/scripts/run_susie_rss.R
  - src/snakemake/scripts/run_qtl_coloc.R
  - src/snakemake/scripts/ta_r4/simulate_coloc_r4.R
  - src/python/ta_r4/commands.py
  - src/python/ta_r4/run_qtl_group_r4.py
  - config/ta_r4/cluster_slurm/config.yaml          # only if the QTL memory measurement in Task 1 requires it (resource line only)
  - tests/ta_r4/test_purity_determinism.py
  - tests/ta_r4/test_qtl_group_runner.py           # declared spec updates, if the argv tests pin the QTL argv (Task 2 step 1)
  - tests/ta_r4/test_unique_allele_key_guard.py    # declared spec updates (fixture helper _argv)
  - tests/ta_r4/test_json_cs_equals_fit_sets.py    # declared spec update (fixture helper pre_fix_argv)
  - tests/m3/test_source_freeze_pins.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/purity_flip_measurement.tsv
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-purity-determinism-SUMMARY.md
autonomous: true
requirements:
  - REQ-SUSIE-RSS-POLICY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Gates: Q-F2 prints \"A: Exact purity, third unfreeze (Recommended)\" and Q-F2Q prints \"i: Same treatment on the QTL side (Recommended)\", each with the <question> text and sha256; any other result → nothing is edited"
    - "Two DEC entries quote the replies: DEC-2026-11-20-run-susie-rss-exact-purity-unfreeze (the third §B.6 D-28 lift; scope = the --exact-purity flag in run_susie_rss.R only) and DEC-2026-11-20-ta-r4-qtl-exact-purity-flag (run_qtl_coloc.R is not D-28 frozen but is Track B-shared, so its opt-in flag gets its own entry under Q-F2Q)"
    - "Before any code change, manifests/purity_flip_measurement.tsv is committed: per pilot A3_1kg_newcat component with V > 1e-9 and a 95% set > 100 variants (109 at planning; 12 fits), set size, exact min |r| over all pairs, share of 1,000 seeded 100-member subsamples with min |r| ≥ 0.5, kept in the recorded fit; plus the largest set size (3,350 at planning) and the job's peak RSS"
    - "run_susie_rss.R gains --exact-purity (default false; anything but true/false stops). When true: ladder_policy$n_purity is the number of variants and susie_call passes it to susie_rss; the post-hoc min_abs_corr sweep and L-saturation susie_get_cs calls pass n_purity = nrow(R_cs). Default path byte-identical in behaviour to PRE_157F_REF; non-legacy production arms pass true; repro arms and Track B do not"
    - "simulate_coloc_r4.R passes n_purity in its ladder policy, so simulated fits use the production purity rule"
    - "run_qtl_coloc.R gains --exact-purity (default false): when true both runsusie calls pass n_purity = the number of bridged variants; QTL_A3 and QTL_A2 pass true; QTL_legacy and Track B do not; the default path is identical to PRE_157F_REF"
    - "Memory is sized: exact purity of an s-member set builds an s×s submatrix (8·s² bytes; 2.05 GB at s = 16,000, the cap), and get_purity also holds its absolute values and the upper-triangle vector, so with the fit's own R the transient peak is about 5-6 GB at the cap. Fits run with 48 GB (cluster profile). The QTL job runs with the 8 GB default; Task 1 measures peak RSS of exact purity on the largest QTL region's full bridged set and raises r4_qtl_group memory with one resource line if the peak exceeds 6 GB"
    - "tests/m3/test_variant_catalog_fallback_legacy_semantics.py is green without edits; R_CODE_REF is re-pinned to the edit commit in its own commit under the unfreeze DEC; test_source_freeze_pins green; every tests/m3 outcome equals full_15_7e.xml"
    - "The 13 ids in <new_tests> pass; FULL vs full_15_7e.xml: 0 removed, added == <new_tests>, 0 outcome changes except declared spec updates (listed in the SUMMARY); 2,667 = 2,614 P / 53 S / 0 F"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/purity_flip_measurement.tsv"
      provides: "pre-fix exposure, flip probability, largest set size and memory"
    - path: "tests/ta_r4/test_purity_determinism.py"
      provides: "the 13 tests in <new_tests>"
  key_links:
    - from: "commands.fit_command (non-legacy)"
      to: "run_susie_rss.R --exact-purity true"
      via: "argv beside --cap-after-ld-restriction / --require-unique-allele-key"
      pattern: "exact-purity"
    - from: "run_qtl_group_r4.qtl_command (QTL_A3, QTL_A2)"
      to: "run_qtl_coloc.R --exact-purity true"
      via: "argv"
      pattern: "exact-purity"
---

<objective>
Close F2 (CONFIRMED) with Carter's Q-F2 A and Q-F2Q i. susieR 0.14.2 `get_purity` draws `sample(pos, 100)` for a
credible set larger than 100 variants (`n_purity = 100`), and neither `run_susie_rss.R` (`:45-47`, `:1393`, `:1407`)
nor `run_qtl_coloc.R` (`:657-662`, `coloc::runsusie`) sets a seed or `n_purity`. Which sets pass min_abs_corr 0.5 is a
random draw that decides `coloc_susie` vs `fallback_abf`. On the 20 corrected-input A3_1kg pilot fits, 109 components
in 12 fits had a subsampled purity; all 109 were dropped in their draw. Exact purity removes the draw.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-F2: file `W3f-carter-15-7-Q-F2-reply-2026-11-20.txt`, sha256 `5788606334769a728a4fbf4456db987f923c98f15b10556067bfaea3adc52e5a`.
Question text: For credible sets with more than 100 variants, susieR 0.14.2 computes purity on a random 100-variant subsample, and run_susie_rss.R sets no seed. In the 20 corrected-input pilot fits, 109 components in 12 fits got a random purity, and all were dropped in that draw. That draw decides coloc_susie vs fallback_abf. Track B is unchanged under every option. Which fix?
Required label: `A: Exact purity, third unfreeze (Recommended)`

Q-F2Q: file `W3f-carter-15-7-Q-F2Q-reply-2026-11-20.txt`, sha256 `63a54f5f70736d5a06bc75c07647ba2c93bd2a18975f1d36cac3d1c9e3ab790e`.
Question text: coloc::runsusie in run_qtl_coloc.R, which Track B also uses, has the same random purity on the QTL side. How should it be handled?
Required label: `i: Same treatment on the QTL side (Recommended)`
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@src/legacy/region_analysis/scripts/run_susie_rss.R
@src/snakemake/scripts/run_qtl_coloc.R
@src/python/ta_r4/commands.py
@tests/m3/test_source_freeze_pins.py

**Gates.** `$PY $Q/gate_reply.py Q-F2 --question … --sha256 … "A: Exact purity, third unfreeze (Recommended)"` and
`$PY $Q/gate_reply.py Q-F2Q --question … --sha256 … "i: Same treatment on the QTL side (Recommended)"` (texts and
sha256 from `<question>`). Either non-zero → STOP, edit nothing.

**Forbidden:** run_susie_rss.R or run_qtl_coloc.R edits beyond the flag; any default-path change; edits inside the five
MUST-NOT-MOVE regions of test_variant_catalog_fallback_legacy_semantics.py (if unavoidable, STOP); changes to repro
arms, QTL_legacy, Track B rule files.

**Measured at planning:**
- `simulate_coloc_r4.R:25-39` parses `run_susie_with_ladder` from the frozen file; `:62` calls it with policy `lp`.
- `commands.fit_command:47-48` adds the non-legacy flags; the new flag goes beside them.
- Pilot exposure probe `data/r4/tmp/w3f/q157/planner_probes/f2_exposure.R` (109 components, 12 of 20 fits; largest 95%
  component 3,350 variants, asthma FTO_16q12).
- Memory: fits `r4_run_finemap:mem_mb=48000` (config/ta_r4/cluster_slurm/config.yaml:15); QTL groups
  `config["resources"]["default_mem_mb"]` = 8000 (config/pipeline.yaml:169, not editable); the largest EUR 1000G panel
  is 15,236 variants (DRAFT (k)).
</context>

<new_tests>
tests/ta_r4/test_purity_determinism.py; N_new = 13.
1. `test_default_path_unchanged_without_the_flag` (r4_heavy; toy region; fit JSON and RDS sets equal to those from
   run_susie_rss.R at the literal `PRE_157F_REF` via `git show` into tmp_path)
2. `test_exact_purity_equals_the_full_pairwise_minimum` (toy CS > 100 members)
3. `test_exact_purity_is_invariant_to_the_rng_seed`
4. `test_subsample_purity_depends_on_the_seed_without_the_flag` (negative control: the toy reaches the random path)
5. `test_sweep_and_l_saturation_use_exact_purity`
6. `test_bad_exact_purity_value_stops`
7. `test_fit_command_passes_exact_purity_for_production_arms`
8. `test_repro_arms_do_not_pass_exact_purity`
9. `test_simulation_ladder_uses_exact_purity`
10. `test_flip_measurement_manifest_matches_its_recount` (r4_heavy; recomputes two rows. It reads the pilot fits and
    panels under data/r4, which are gitignored and not in git; that is the r4_heavy data-read pattern, and the test
    fails, never skips, if a file listed in the committed manifest is absent)
11. `test_qtl_default_path_unchanged_without_the_flag` (r4_heavy; run_qtl_coloc.R at PRE_157F_REF vs HEAD on the
    test_qtl_group_runner fixture; output JSON equal)
12. `test_qtl_exact_purity_equals_the_full_pairwise_minimum` (r4_heavy)
13. `test_qtl_command_passes_exact_purity_except_legacy`
Expected FULL: base full_15_7e.xml (2,654) + 13 = 2,667 = 2,614 P / 53 S / 0 F. If tests in test_qtl_group_runner.py
pin the exact QTL argv (e.g. `test_fixed_arms_argv`), each changed assertion is a declared spec update named in the
SUMMARY before RED; `test_legacy_argv_is_the_exact_pre_fix_argv` must stay unchanged.
</new_tests>

<tasks>

<task type="auto">
  <name>Task 1: Gates, two DECs, the pre-fix flip and memory measurement (read-only, Slurm)</name>
  <files>.planning/DECISIONS.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/purity_flip_measurement.tsv, config/ta_r4/cluster_slurm/config.yaml (conditional)</files>
  <read_first>
    - DECISIONS.md entries DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze and
      DEC-2026-11-17-run-susie-rss-unique-allele-key-guard-unfreeze (format, scope, re-pin wording)
    - susieR 0.14.2 `get_purity`, `susie_get_cs`; coloc 5.2.3 `runsusie` (print from r_coloc into the LOG)
  </read_first>
  <action>
    0. Gates. `git rev-parse HEAD > $Q/start_15_7f.txt`; write that sha into the test as the literal `PRE_157F_REF`.
       DECs per must_haves, each quoting its reply with `cat` + `cmp`. Commit 1 (DECISIONS.md).
    1. Flip measurement (sbatch `-t 02:00:00 --mem=32G --constraint=cascadelake`, read-only): per pilot fit, load the
       fit RDS and the panel its JSON declares; check the panel file's sha256 against the panel manifest row for that
       panel (a mismatch → STOP: the fit read another panel). Map every fit variable to a panel row with 15.7c's
       `variant_match.R::resolve_fit_names` (sumstats SNP_ID of the fit's own sumstats, then the panel-rsid override,
       then a unique CHR:POS; the make.unique `.N` suffix handled as 15.7c specifies, with allow_duplicate_rows on because these are pre-15.5a fits; about 40% of A3_1kg_newcat names
       carry one); an unmappable credible-set member stops that fit and is listed. Identity checks before any new number:
       (i) each component's 95% set recomputed from alpha equals the stored set for every stored set; (ii) for stored
       sets of ≤ 100 members, purity recomputed over all pairs equals the stored min.abs.corr within 1e-12. Either check
       failing → STOP. Then, for each qualifying component record set size, exact min |r| (computed in blocks so peak
       memory stays bounded: memory rule `feedback_dense_matrix_verify_memory_bounded`), and the share over seeds
       1..1000 of subsampled min ≥ 0.5. Reconcile rows == 109 and fits == 12; record the largest size and `sacct`
       MaxRSS. A component with exact purity ≥ 0.5, or a share strictly between 0 and 1, is a demonstrated flip; count
       them in the LOG. Commit the manifest with the script copied to `$Q/`.
    2. QTL memory: on the region with the largest 1000G panel, run `susieR::susie_get_cs` with `n_purity` = all
       variants on a synthetic fit whose one set is the whole bridged set (sbatch, `/usr/bin/time -v`). If peak RSS
       > 6 GB, add `- "r4_qtl_group:mem_mb=<ceil(peak·1.5) GB>"` under set-resources in
       config/ta_r4/cluster_slurm/config.yaml (resource only) and say so in the LOG; else leave it.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && test "$(grep -vc '^fit' .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/purity_flip_measurement.tsv)" -ge 109 && grep -q "DEC-2026-11-20-run-susie-rss-exact-purity-unfreeze" .planning/DECISIONS.md && grep -q "DEC-2026-11-20-ta-r4-qtl-exact-purity-flag" .planning/DECISIONS.md</automated>
  </verify>
  <done>Gates passed; both DECs; flip and memory measured and committed before any code change.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: --exact-purity in run_susie_rss.R and run_qtl_coloc.R (RED first); re-pin; DRAFT</name>
  <files>src/legacy/region_analysis/scripts/run_susie_rss.R, src/snakemake/scripts/run_qtl_coloc.R, src/snakemake/scripts/ta_r4/simulate_coloc_r4.R, src/python/ta_r4/commands.py, src/python/ta_r4/run_qtl_group_r4.py, tests/ta_r4/test_purity_determinism.py, tests/ta_r4/test_qtl_group_runner.py, tests/m3/test_source_freeze_pins.py, .planning/amendments/osf-amendment-r4-DRAFT.md</files>
  <read_first>
    - run_susie_rss.R :25-70, :705-770, :1190-1210, :1385-1410; run_qtl_coloc.R :1-120 (options), :640-670
    - tests/m3/test_source_freeze_pins.py :55-90, :170-260; tests/ta_r4/test_qtl_group_runner.py :40-70
  </read_first>
  <action>
    1. RED: the 13 tests (all RED except 1, 4, 8, 11, which are green now). Record.
    2. GREEN per must_haves. Argv positions: in `commands.fit_command`, `"--exact-purity", "true"` is appended right
       after `"--require-unique-allele-key", "true"` inside the `if not _legacy(arm)` block (same `cmd +=` list, last),
       so it precedes `--variant-list` and `test_fit_command_flag_per_arm`'s check index(--require-unique-allele-key) ==
       index(--cap-after-ld-restriction) + 2 still holds; in `run_qtl_group_r4.qtl_command`, it is appended after `--qtl-orient` and before `--output`
       for QTL_A3 and QTL_A2 only. Any existing argv-pinning test that changes is listed in the SUMMARY's `## Declared
       spec updates` before RED (`test_legacy_argv_is_the_exact_pre_fix_argv` must not change). Declared spec updates (fixture helpers only; ids
       kept, passed): `tests.ta_r4.test_unique_allele_key_guard::test_default_is_pre_guard_behaviour[None]` and
       `[false]` (`_argv` also strips `--exact-purity` and its value, because the pre-guard script at 1f77128 rejects
       it) and `tests.ta_r4.test_json_cs_equals_fit_sets::test_fit_rds_unchanged_by_the_fix` (`pre_fix_argv` also
       strips `--exact-purity`). Commit 2 (code), explicit paths.
    3. Re-pin `R_CODE_REF` in tests/m3/test_source_freeze_pins.py to commit 2's short sha, in its own commit 3 citing
       DEC-2026-11-20-run-susie-rss-exact-purity-unfreeze (as 3f4d0cb9 did). Run tests/m3 in full: every outcome equals
       full_15_7e.xml.
    4. DRAFT (k): after "min_abs_corr 0.5 (sweep 0.1/0.5/0.9 reported)" add "; set purity is computed over all pairs of
       set members, for GWAS and QTL fits and in the simulation (susieR otherwise uses a random 100-member subsample for
       sets larger than 100)". test_amendment_text.py green. Commit 4.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_purity_determinism.py tests/ta_r4/test_qtl_group_runner.py tests/ta_r4/test_unique_allele_key_guard.py tests/ta_r4/test_json_cs_equals_fit_sets.py tests/ta_r4/test_cap_after_panel.py tests/ta_r4/test_measure_fit_eligibility.py tests/ta_r4/test_coloc_pair_r4.py tests/m3/test_qtl_coloc_allele_join.py tests/ta_r4/test_frozen_script_armed_e2e.py tests/ta_r4/test_simulation_harness.py tests/m3/test_source_freeze_pins.py tests/m3/test_variant_catalog_fallback_legacy_semantics.py tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider</automated>
  </verify>
  <done>RED observed; the flag works on both sides; default paths, repro arms, QTL_legacy and Track B unchanged; re-pin in its own commit.</done>
</task>

<task type="auto">
  <name>Task 3: FULL under Slurm, per-id reconciliation vs full_15_7e.xml, records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-purity-determinism-SUMMARY.md</files>
  <action>
    Close per the 15.7 protocol, tag 15_7f: `$Q/check_15_7f.py` (removed 0; added == the 13; outcome changes only the
    declared spec updates (the 3 above and any argv ids named in the SUMMARY), still passed; tests/m3 unchanged; 2,667 = 2,614 / 53 / 0). PLAN-INDEX §B.6 note gains the
    third lift and the new R_CODE_REF. Records (STATE NEXT = 15.7g; NOT PUSHED; SUMMARY with ids). fsck; commit.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q157/check_15_7f.py && test -z "$(git status --porcelain -- src tests)"</automated>
  </verify>
  <done>FULL reconciled; records committed; no push.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| frozen fitting script (D-28) | edits need Carter's explicit authorization and a re-pin under a DEC |
| RNG state → credible-set retention | an unseeded draw decides coloc_susie vs fallback |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-157f-01 | Tampering | default paths of both scripts | mitigate | flags default off; tests 1 and 11 vs PRE_157F_REF; legacy-semantics pins untouched |
| T-r4-157f-02 | Repudiation | unfreeze authority | mitigate | gates on the verbatim replies; two DECs; re-pin in its own commit |
| T-r4-157f-03 | Denial of service | exact purity memory | mitigate | measured peak; QTL memory raised by a resource line only if needed |
| T-r4-157f-04 | Tampering | silent nondeterminism | mitigate | 2, 3, 5, 12 with negative control 4 |
</threat_model>

<verification>
- Flip measurement committed before any code change; check_15_7f.py passes.
</verification>

<success_criteria>
- Production and simulated credible-set retention no longer depends on an unseeded random draw, on the GWAS and QTL sides.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-purity-determinism-SUMMARY.md`
</output>
