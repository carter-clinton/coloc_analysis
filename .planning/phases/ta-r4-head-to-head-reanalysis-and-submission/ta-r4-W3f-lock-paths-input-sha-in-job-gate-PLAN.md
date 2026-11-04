---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.2
slug: W3f-lock-paths-input-sha-in-job-gate
type: execute
wave: 15.2
depends_on: ["ta-r4-W3f-producer-cap-fit-names-early-exit"]
gap_closure: true
files_modified:
  - src/python/ta_r4/r4_lock_gate.py
  - src/python/ta_r4/verify_inputs.py
  - src/python/ta_r4/commands.py
  - src/python/ta_r4/run_qtl_group_r4.py
  - src/snakemake/rules/ta_r4_finemap.smk
  - src/snakemake/rules/ta_r4_coloc.smk
  - src/snakemake/rules/ta_r4_qtl.smk
  - src/snakemake/rules/ta_r4_sim.smk
  - bin/r4_fire.sh
  - config/ta_r4/data_sources.yaml
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - tests/ta_r4/test_lock_gate.py
  - tests/ta_r4/test_verify_inputs.py
  - tests/ta_r4/test_in_job_gate.py
  - tests/ta_r4/test_data_sources_labels.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: true
requirements:
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-OSF-PREREG

must_haves:
  truths:
    - "LOCKED_PATHS covers every live analytical dependency of the R4 rules, including config/susie_policy.yaml, config/pipeline.yaml, src/snakemake/scripts/qtl_orient.R, config/qtl_sources.yaml, src/python/build_tissue_n_lookup.py and config/pph4_thresholds.yaml; a committed change to any of them after the lock fails the gate (Codex N3)"
    - "Every production fit, coloc and QTL job verifies the sha256 of its GWAS summary statistics, variant catalog and harmonized QTL inputs against the committed manifests before reading them; a mismatch or an unlisted input fails the job (Codex N4)"
    - "Every production job re-runs the offline lock gate as its first shell command, not only at DAG construction; the r4_fire.sh comment states what the jobs actually check (Codex N5)"
    - "config/ta_r4/data_sources.yaml labels AFR type 2 diabetes T2DGGI (Suzuki 2024), matching trait_manifest.tsv (T1)"
  artifacts:
    - path: "src/python/ta_r4/verify_inputs.py"
      provides: "verify(files, manifests, repo) and CLI `python -m ta_r4.verify_inputs --file F ...`; exit 1 on mismatch/unlisted"
    - path: "src/python/ta_r4/r4_lock_gate.py"
      provides: "extended LOCKED_PATHS"
    - path: "tests/ta_r4/test_in_job_gate.py"
      provides: "rendered production shell begins with the gate; gate in a job fails after locked-path drift"
  key_links:
    - from: "src/snakemake/rules/ta_r4_finemap.smk r4_run_finemap shell"
      to: "ta_r4.r4_lock_gate check --stage production; ta_r4.verify_inputs"
      via: "commands.gate_command(stage) and commands.verify_command(...) rendered before the fit"
      pattern: "r4_lock_gate"
    - from: "src/python/ta_r4/run_qtl_group_r4.py"
      to: "manifests/qtl_harmonized_sha256.tsv"
      via: "verify_inputs.verify on each harmonized file before qtl_command"
      pattern: "verify_inputs"
---

<objective>
W3f fix-up, plan 2 of 6: make the freeze and input integrity claims true in code (review N3, N4, N5) and fix
the AFR T2D source label (T1).

Purpose: the amendment says the analysis is fixed by a lock commit; today shared configs that change results
escape the lock, inputs are hashed but never checked at fit time, and the gate runs only when the DAG is built.
Output: extended LOCKED_PATHS, an input-verification module wired into every production job, an in-job gate,
a corrected comment in r4_fire.sh, the T1 label fix, tests with RED and negative controls.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md

Standing rules: PLAN-INDEX §A/§B/§C. §B.7: never edit config/pipeline.yaml, Snakefile or non-ta_r4 rules (locking
pipeline.yaml in LOCKED_PATHS is not an edit). Fixture lock records only under pytest tmp_path
(tests/ta_r4/fixtures/make_fixture_repo.py: make_fixture_repo, write_fixture_lock, git).

<interfaces>
src/python/ta_r4/r4_lock_gate.py:
  LOCKED_PATHS: tuple of repo-relative paths/globs used in `git diff --name-only <sha> HEAD -- *LOCKED_PATHS`
  check_lock_gate(repo_root, stage) ('repro' passes; 'production' runs checks (a)-(i), memoized per (realpath, HEAD))
  CLI: python -m ta_r4.r4_lock_gate check --stage production|repro  (fresh process; exit 1 + "LockGateError: ..." on failure); `paths` prints LOCKED_PATHS
src/python/ta_r4/commands.py: _PY = ["env", "PYTHONPATH=src/python", sys.executable, "-m"]; receipt_command/validate_command pattern
Snakefile.ta_r4 (never edited): gate_input(w) -> check_lock_gate at DAG time; STAGE = arm_stage(ARM)
src/snakemake/rules/ta_r4_finemap.smk r4_run_finemap shell: set -euo pipefail; {params.check}; {params.receipt}; {params.fit}; {params.validate}; ...
src/snakemake/rules/ta_r4_coloc.smk r4_coloc_pair / r4_coloc_A1 shell: "{params.cmd} > {log} 2>&1"
src/snakemake/rules/ta_r4_qtl.smk r4_qtl_group / r4_qtl_aggregate / r4_qtl_tiers; _r4_qtl_gate(w) uses arm_stage(fit_arm(qtl_arm))
src/snakemake/rules/ta_r4_sim.smk r4_sim (production, A3_1kg invocation)
Manifests ($MAN): sumstats_r4_sha256.tsv (path, sha256, bytes, role); catalogs_sha256.tsv; qtl_harmonized_sha256.tsv (rel_path, sha256, n_rows, ...)
bin/r4_fire.sh:66 echo "Do not commit locked paths until this fire ends: in-job gate checks re-diff them against the lock commit."
config/ta_r4/data_sources.yaml:103 AFR T2D labelled "DIAMANTE 2022"; config/ta_r4/trait_manifest.tsv t2d AFR = T2DGGI (Suzuki 2024)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: N3 — LOCKED_PATHS covers every live analytical dependency</name>
  <files>src/python/ta_r4/r4_lock_gate.py, tests/ta_r4/test_lock_gate.py, .planning/amendments/osf-amendment-r4-DRAFT.md</files>
  <read_first>
    - src/python/ta_r4/r4_lock_gate.py, tests/ta_r4/test_lock_gate.py (fixture-repo gate tests)
    - src/python/ta_r4/arms.py:6, src/python/ta_r4/commands.py, src/python/ta_r4/harmonize_qtl_r4.py:22, src/python/ta_r4/run_qtl_group_r4.py:84, src/snakemake/scripts/run_qtl_coloc.R:181-190, src/snakemake/rules/ta_r4_qtl.smk:136, Snakefile.ta_r4 (configfile)
    - tests/ta_r4/test_amendment_text.py:55-60 and test_draft_extract_names_every_frozen_path (it requires DRAFT (m) to name every LOCKED_PATHS entry)
  </read_first>
  <behavior>
    - LOCKED_PATHS contains config/susie_policy.yaml, config/pipeline.yaml, src/snakemake/scripts/qtl_orient.R, config/qtl_sources.yaml, src/python/build_tissue_n_lookup.py, config/pph4_thresholds.yaml (each exists in the repo)
    - fixture repo with a valid fixture lock: committing a one-byte change to each of those six files after lock_sha makes check_lock_gate(repo, "production") raise LockGateError naming the file under check (g); restoring makes it pass
    - completeness: every repo file opened by the R4 rules and their scripts that is not data (configs, R/Python code) is covered by some LOCKED_PATHS entry (test enumerates the dependency list written in step 1 and asserts `git ls-files -- <LOCKED_PATHS>` covers it)
  </behavior>
  <action>
    1. Measure the dependency set before writing code: list every config/code file read by Snakefile.ta_r4, the
       ta_r4_*.smk rules, the scripts they call (run_susie_rss.R, run_coloc_pair_r4.R, simulate_coloc_r4.R,
       run_qtl_coloc.R, qtl_orient.R, ld_allele_join.R, plink_ld_to_rds.R, cs_cross_purity.R) and the ta_r4 Python
       modules (yaml/csv/tsv/source()/import of a repo path). Record the list and how it was found (commands +
       output) in the LOG. The six Codex paths are verified to exist at the paths above (`config/qtl_sources.yaml`,
       not config/ta_r4/). Any further non-data dependency found that is not covered is ADDED too (rigor rule);
       data inputs (sumstats, panels, catalogs, QTL files) are covered by Task 2, not by LOCKED_PATHS.
    2. RED: add tests to test_lock_gate.py: the six named paths in LOCKED_PATHS; the per-file drift case
       (parametrized over the six); the completeness assertion over the measured list (written as a module constant
       in the test, sourced from step 1). Run; paste failures.
    3. Append the paths to LOCKED_PATHS (keep the existing order; one entry per path).
    4. GREEN. Negative control: remove `config/susie_policy.yaml` from LOCKED_PATHS → its drift case and the
       completeness case fail (paste); restore. Note: test_amendment_text.py::test_draft_extract_names_every_frozen_path
       now fails until DRAFT (m) lists the new paths — update (m)'s frozen-path list in
       `.planning/amendments/osf-amendment-r4-DRAFT.md` in this task (paths only; the remaining (m) text is plan 15.5)
       so the text test stays green; record that in the SUMMARY.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_lock_gate.py tests/ta_r4/test_amendment_text.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - test_lock_gate.py and test_amendment_text.py pass; RED and NC outputs pasted
    - `$PY -m ta_r4.r4_lock_gate paths` (cwd src/python) prints each of the six paths (exit 0)
    - the LOG lists the measured dependency set with the commands used; any additional path added is named with its reader file:line
  </acceptance_criteria>
  <done>A post-lock change to any file that can change an R4 number fails the production gate.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: N4 — runtime sha256 verification of GWAS, catalog and QTL inputs inside each job</name>
  <files>src/python/ta_r4/verify_inputs.py, src/python/ta_r4/commands.py, src/python/ta_r4/run_qtl_group_r4.py, src/snakemake/rules/ta_r4_finemap.smk, src/snakemake/rules/ta_r4_coloc.smk, tests/ta_r4/test_verify_inputs.py</files>
  <read_first>
    - $MAN/sumstats_r4_sha256.tsv, $MAN/catalogs_sha256.tsv, $MAN/qtl_harmonized_sha256.tsv (headers; does every path that fit_command / coloc_command / run_qtl_group_r4 read appear, including data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz?)
    - src/python/ta_r4/commands.py, src/python/ta_r4/paths.py (sumstats_path, catalog_path), src/python/ta_r4/run_qtl_group_r4.py (where the harmonized path is resolved per row), src/python/ta_r4/write_ld_receipt.py:54 (the panel hashing pattern)
    - src/snakemake/rules/ta_r4_finemap.smk, src/snakemake/rules/ta_r4_coloc.smk
  </read_first>
  <behavior>
    - verify(files, manifests, repo): each file must appear in one of the manifests (column `path` or `rel_path`, repo-relative); its streamed sha256 must equal the recorded value; returns None or raises InputIntegrityError listing every failing file with expected/observed sha256 (unlisted files reported as "not in manifest")
    - CLI `python -m ta_r4.verify_inputs --manifest M [--manifest M2] --file F [--file F2]` exits 0 on success, 1 on any failure with the message on stderr
    - a one-byte change to a fixture input → exit 1 naming the file; an unlisted file → exit 1; a correct file → exit 0
    - commands.verify_command(arm, trait, ancestry, region_safe) for fits checks sumstats + catalog; commands.coloc_verify_command(arm, row, mode) checks both sumstats; rendered first in the r4_run_finemap shell (after the gate, Task 3) and in r4_coloc_pair / r4_coloc_A1 before the R script
    - run_qtl_group_r4 calls verify_inputs.verify on every harmonized QTL file and every GWAS sumstats file of its group before running any row; a mismatch fails the group (no JSON written)
  </behavior>
  <action>
    1. Measure first: for every production arm, list the sumstats and catalog paths the rules would read
       (commands.fit_command / coloc_command over pair_manifest admissible rows) and check each is in a manifest.
       Paste the counts (listed / not listed). If any production input is not listed, STOP and report (do not add
       hashes for files whose provenance is not recorded). Repro arms: apply verification too if all their inputs are
       listed; otherwise apply it to production arms only and record the unlisted repro paths in the LOG.
    2. RED: tests/ta_r4/test_verify_inputs.py with the behaviours above (tmp_path fixture files + tmp manifests;
       one r4_heavy case that verifies the real asthma.EUR sumstats against sumstats_r4_sha256.tsv). Run; paste.
    3. Implement verify_inputs.py (hashlib.sha256, 1 MiB chunks; no caching across files or processes), the two
       command builders in commands.py, the shell wiring in ta_r4_finemap.smk and ta_r4_coloc.smk (params rendered
       with shlex.join, executed under `set -euo pipefail` so a failure stops the job), and the call in
       run_qtl_group_r4.py before the first row is processed.
    4. GREEN. Negative controls (paste): NC1 make verify skip unlisted files → the unlisted case fails; NC2 remove the
       verify call from run_qtl_group_r4 → its fixture test (tampered harmonized file must fail the group) fails.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_verify_inputs.py tests/ta_r4/test_qtl_group_runner.py tests/ta_r4/test_coloc_pair_r4.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - tests pass; RED and NC1/NC2 outputs pasted
    - measured: every production sumstats and catalog input is listed in a manifest (counts pasted, listed = total)
    - `$SMK -n -p` on a fixture repo (as test_snakemake_toy_e2e / test_sim_rule tests build it) renders verify_inputs in the r4_run_finemap and r4_coloc_pair shells (checked by parsing the printed shell, in test_in_job_gate.py of Task 3)
  </acceptance_criteria>
  <done>Production jobs refuse to read a GWAS, catalog or QTL input whose bytes differ from the recorded hash.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: N5 in-job gate + r4_fire.sh comment; T1 label; commit, push, LOG</name>
  <files>src/python/ta_r4/commands.py, src/snakemake/rules/ta_r4_finemap.smk, src/snakemake/rules/ta_r4_coloc.smk, src/snakemake/rules/ta_r4_qtl.smk, src/snakemake/rules/ta_r4_sim.smk, bin/r4_fire.sh, config/ta_r4/data_sources.yaml, tests/ta_r4/test_in_job_gate.py, tests/ta_r4/test_data_sources_labels.py, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <read_first>
    - Snakefile.ta_r4 (gate_input, STAGE), all src/snakemake/rules/ta_r4_*.smk shells (which rules run in production)
    - tests/ta_r4/test_lock_gate.py, tests/ta_r4/test_simulation_harness.py::test_sim_rule_100_jobs_with_lock_and_no_reps_override (fixture lock + dry-run pattern)
    - bin/r4_fire.sh, config/ta_r4/data_sources.yaml (around :103), config/ta_r4/trait_manifest.tsv
  </read_first>
  <behavior>
    - commands.gate_command(stage) -> _PY + ["ta_r4.r4_lock_gate", "check", "--stage", stage] for "production"; ["true"] for "repro"
    - in a fixture repo with a valid fixture lock, `$SMK -n -p` for each production rule (r4_run_finemap, r4_coloc_pair, r4_coloc_A1, r4_sim, r4_qtl_group, r4_qtl_aggregate, r4_qtl_tiers) prints a shell whose first command is the gate command (parsed, not grepped as free text: split the printed shell on newlines/`&&`, first non-`set` command equals shlex.join(gate_command("production")))
    - behavioural: after the dry-run passes, commit a change to a LOCKED_PATHS file in the fixture repo; executing the rendered gate command in that repo exits 1 with "(g) locked paths drifted"; before the change it exits 0
    - data_sources.yaml parsed: the AFR t2d entry's label equals the trait_manifest.tsv t2d AFR study label (T2DGGI, Suzuki 2024); no entry contains "DIAMANTE 2022" for AFR t2d
  </behavior>
  <action>
    1. RED: tests/ta_r4/test_in_job_gate.py (r4_heavy: runs $SMK) and tests/ta_r4/test_data_sources_labels.py
       (yaml.safe_load + csv; not heavy). Run; paste.
    2. Implement commands.gate_command; render it as the first command of every production rule's shell listed
       above (params.gate = shlex.join(r4cmd.gate_command(STAGE)) or the QTL fit-arm stage for QTL rules, followed by
       `&&` / a new line under `set -euo pipefail`). Snakefile.ta_r4 is not edited (its header says later plans never
       edit it); the DAG-time gate_input stays.
    3. bin/r4_fire.sh: replace the line-66 echo with
       `echo "Do not commit locked paths until this fire ends: every production job re-runs the lock gate before reading inputs and fails on drift from the lock commit."`
       and make the DIRTY check use the gate's own list: `DIRTY=$(git status --porcelain -- $(cd src/python && "$PY" -m ta_r4.r4_lock_gate paths))`
       (behaviour test: a modified config/susie_policy.yaml in a fixture copy makes `bin/r4_fire.sh production A3_1kg -n` exit 2 before Snakemake starts, if the script can be exercised in a fixture; otherwise record why it cannot and cover it by the gate tests).
    4. config/ta_r4/data_sources.yaml: change the AFR T2D label to the trait_manifest.tsv wording (T2DGGI, Suzuki 2024); nothing else.
    5. GREEN. Negative controls (paste): NC1 render the gate only for r4_run_finemap → the parametrized cases for the
       other rules fail; NC2 restore "DIAMANTE 2022" → the label test fails.
    6. §C: $QUICK (wall time), $HEAVY for this plan's heavy files, pins file. `git fsck`; explicit-path commit of
       every file in files_modified except the LOG (`fix(ta-r4-W3f): N3 locked paths, N4 in-job input sha256, N5 in-job gate, T1 label`);
       `git fsck`; push. LOG entry (measured dependency list, input-listing counts, RED/GREEN/NC, commit, QUICK time); refresh the W3f progress line in STATE.md (§C); commit LOG and STATE.md; push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_in_job_gate.py tests/ta_r4/test_data_sources_labels.py tests/ta_r4/test_lock_gate.py tests/ta_r4/test_snakemake_toy_e2e.py tests/ta_r4/test_simulation_harness.py -q -rs</automated>
  </verify>
  <acceptance_criteria>
    - tests pass; RED and NC outputs pasted
    - the drift case shows rc 0 before and rc 1 after the fixture commit (both rc values pasted)
    - `git log origin/m3-W2-aou-deltas..HEAD` is empty after the push
  </acceptance_criteria>
  <done>Each production job checks the lock and its inputs itself; the fire script's claim matches the jobs.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| lock commit → running jobs | code or configs can change between DAG construction and job execution |
| recorded checksums → bytes read | an input can be replaced after its hash was recorded |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3f2-01 | Tampering | shared configs outside LOCKED_PATHS | mitigate | measured dependency list; six named paths + any found added; per-file drift tests |
| T-r4-W3f2-02 | Tampering | GWAS/catalog/QTL inputs | mitigate | verify_inputs in-job, fails on mismatch or unlisted; NC on skip-unlisted |
| T-r4-W3f2-03 | Elevation of privilege | jobs running after a post-DAG commit | mitigate | gate command first in every production shell; fresh process, no cache |
</threat_model>

<verification>
Gate drift tests per new path, in-job gate render + behaviour tests, input verification tests, and the T1 label
test pass with observed RED and negative controls.
</verification>

<success_criteria>
The freeze, checksum and gate statements in the amendment are enforced by code that a test has seen fail.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-lock-paths-input-sha-in-job-gate-SUMMARY.md`
</output>
