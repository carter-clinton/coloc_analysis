---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.6
slug: W3f-review-suite-and-close
type: execute
wave: 15.6
depends_on: ["ta-r4-W3f-eligibility-measurement-and-draft"]
gap_closure: true
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-AMENDMENT-REVIEW-as-received.md
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md
  - .planning/HANDOFF.json
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI
  - REQ-NEGATIVE-CONTROLS

must_haves:
  truths:
    - "The changed DRAFT extract survived a brief-blind Codex review against the W3f code; output banked verbatim, every finding dispositioned (text fixed, or recorded as an open item for Carter if it needs code)"
    - "The FULL suite ran under Slurm and is reconciled by test id against data/r4/tmp/w4a/full_W4a.xml (2069 / 2017 / 52 / 0): 0 removed ids, 0 outcome changes in tests/m3, every added skip or fail explained by id; any failure is a STOP"
    - "All W4a production blockers (N1, N2) and the other code items (N3-N7, N9, N10, N12, N14, T1) are recorded as resolved with their commits in HANDOFF.json w4a_checkpoint; the new confirmatory_sha256 and the proposed n_regions_min 7 are the values presented at W4a-T3"
    - "W4a's frontmatter depends_on points at ta-r4-W3f-review-suite-and-close; W4a's tasks are untouched"
    - "No production fit ran, decision_rules.yaml is still locked: false, and no signoff file or carter-approved text was written"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-AMENDMENT-REVIEW-as-received.md"
      provides: "verbatim Codex delta review + disposition table"
    - path: ".planning/HANDOFF.json"
      provides: "w4a_checkpoint refreshed (blockers resolved, new sha, n_regions_min 7, region-contribution flag)"
  key_links:
    - from: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md"
      to: "ta-r4-W3f-review-suite-and-close"
      via: "frontmatter depends_on"
      pattern: "ta-r4-W3f-review-suite-and-close"
---

<objective>
W3f fix-up, plan 6 of 6: attack the changed public text against the new code, run and reconcile the full suite,
refresh the resume records, and hand W4a-T3 back to Carter with the new sha.

Purpose: the DRAFT changed substantively after its W4a review; internal tests cannot catch a mis-specified premise
(memory feedback_internal_validation_cannot_catch_misspecified_premise), so it is re-attacked brief-blind before
Carter locks against it.
Output: banked review + dispositions, reconciled FULL run, refreshed HANDOFF/STATE/LOG/PLAN-INDEX, W4a depends_on edit, push.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4-AMENDMENT-REVIEW-as-received.md

Standing rules: PLAN-INDEX §A/§B/§C/§D. Slurm only (sbatch -p compute -A clintonlab_cpu -q normal, always -t). Do NOT:
run production, flip `locked: true`, write signoffs/*.yaml or `data/r4/tmp/signoff_W4a-T3.txt`, author `carter-approved`
text, edit W4a's tasks, post to OSF. HANDOFF.json is ~139 KB: edit with a Python json load/dump that preserves every
existing key; keep superseded strings verbatim and add dated annotations (the 2026-09-16 practice), never delete history.

<interfaces>
W4a review run (ta-r4-LOG.md W4a Task 2): codex-cli 0.166.0 from a scratch prefix, `codex exec --skip-git-repo-check
--sandbox read-only -m gpt-6.1-sol - < <prompt>` from the repo root; prompt = the W4a instruction + the extract only
(memory reference_codex_cli_for_gsd_review). W4a instruction text: "You are a hostile methods reviewer. For every factual
or methodological claim in this pre-registration, find the code or data file in this repository that implements or
supports it, and report any claim that the code contradicts, that is unsupported, or that is ambiguous enough to allow
post-hoc choice. Cite file:line."
Wave-close Slurm template: data/r4/tmp/w4a/close_W4a.sh (QUICK, HEAVY, PINS, FULL with --junitxml, then
`git restore tests/m3/sparse_parent_benchmark.tsv`); reconciliation format: data/r4/tmp/w4a/reconcile_W4a.txt
(base/new Counters, common/removed/added/changed, arithmetic line, added modules, tests/m3 before -> after)
HANDOFF.json keys: w4a_checkpoint {read_first, proposed_lock_values, resume_reply_format, production_blockers,
other_code_items, carried_decisions_a_to_g, signoff_written}, resume_on_reconnect, suite_baselines_ta_r4_latest, do_not, scheduler
STATE.md: the "## 2026-11-04 — TRACK A ta-r4: W4a Tasks 1–2 COMPLETE ... (★ RESUME HERE — LATEST ★)" block near line 29
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Brief-blind Codex review of the changed extract; bank verbatim; disposition; DRAFT text fixes only</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-AMENDMENT-REVIEW-as-received.md, .planning/amendments/osf-amendment-r4-DRAFT.md</files>
  <read_first>
    - memory reference_codex_cli_for_gsd_review and feedback_internal_validation_cannot_catch_misspecified_premise
    - ta-r4-LOG.md W4a Task 2 entry (exact invocation, model, scratch prefix) and ta-r4-W4-AMENDMENT-REVIEW-as-received.md (format: 3-line header, verbatim block, disposition table)
    - .planning/amendments/osf-amendment-r4-DRAFT.md
  </read_first>
  <action>
    1. `cd src/python && $PY -m ta_r4.extract_paste_block --in ../../.planning/amendments/osf-amendment-r4-DRAFT.md --out ../../data/r4/tmp/w3f/review_input.md`.
       Prompt file data/r4/tmp/w3f/codex_prompt.md = the W4a instruction (verbatim, from <interfaces>) + the extract,
       nothing else (no CONTEXT, LOG, SUMMARY or finding list: brief-blind). Record its sha256. Run Codex as at W4a from
       the repo root; save stdout/stderr/rc under data/r4/tmp/w3f/. If the CLI fails, record the error and retry once
       with the model the account's cache lists; a second failure is STOP-and-report (the review is not skipped).
    2. Bank the output byte-for-byte in `$P/ta-r4-W3f-AMENDMENT-REVIEW-as-received.md` under the 3-line header (date +
       reviewed HEAD, command, prompt sha256) with the output's own sha256 and byte count; then a disposition table:
       finding → verified against the code (file:line, checked by the executor) → "DRAFT fixed" / "rejected with
       evidence" / "OPEN for Carter (needs code)". Findings count == rows (both numbers written).
    3. Apply text fixes to the DRAFT only; re-run test_amendment_text.py. Do not change analysis code here: a finding
       that needs code is recorded OPEN and carried to HANDOFF (Task 3) as a production blocker for Carter.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py -q && grep -c "^| " .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-AMENDMENT-REVIEW-as-received.md</automated>
  </verify>
  <acceptance_criteria>
    - the banked block's sha256 equals the sha256 of the saved raw stdout (`sha256sum` of both pasted, equal)
    - disposition rows = findings (both counts pasted); every OPEN row names the code location
    - test_amendment_text.py passes after the text fixes
  </acceptance_criteria>
  <done>The new public text has been attacked against the new code and every finding has a recorded outcome.</done>
</task>

<task type="auto">
  <name>Task 2: FULL suite under Slurm, reconciled by test id against full_W4a.xml</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <read_first>
    - data/r4/tmp/w4a/close_W4a.sh, data/r4/tmp/w4a/reconcile_W4a.txt
    - the SUMMARYs of plans 15.1–15.5 (every deliberately changed test id and every spec update)
  </read_first>
  <action>
    1. Copy close_W4a.sh to data/r4/tmp/w3f/close_W3f.sh, changing only the junitxml path to data/r4/tmp/w3f/full_W3f.xml
       and the header comment. `git status --porcelain -- tests/ src/ config/ta_r4` must be empty first (commit any
       Task 1 DRAFT change before the run). Submit: `sbatch -p compute -A clintonlab_cpu -q normal -t 04:00:00 --mem=32G -o data/r4/tmp/w3f/close_W3f_%j.out data/r4/tmp/w3f/close_W3f.sh`.
       Wait by output file (END line), not by job state.
    2. Reconcile by id (junit XML parse, not text grep) vs data/r4/tmp/w4a/full_W4a.xml in the reconcile_W4a.txt
       format into data/r4/tmp/w3f/reconcile_W3f.txt: base/new Counters; common/removed/added/changed; the arithmetic
       line; added outcomes and modules; tests/m3 before → after. Required: removed 0; tests/m3 outcomes unchanged; 0
       failed. Every pre-existing test whose outcome or expectation changed in W3f must be one the plan SUMMARYs list as
       a deliberate spec update (list them by id); every new skip is explained by id (e.g. an r4_heavy test needing a
       tool absent in the job). Any unexplained change or any failure: STOP and report to the orchestrator — do not
       "fix" a test to make the count match.
    3. Confirm `git restore tests/m3/sparse_parent_benchmark.tsv` ran (porcelain for it empty). Paste QUICK wall time,
       HEAVY, PINS and FULL lines and the reconciliation into the LOG.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && tail -8 data/r4/tmp/w3f/reconcile_W3f.txt && git status --porcelain -- tests/m3/sparse_parent_benchmark.tsv</automated>
  </verify>
  <acceptance_criteria>
    - reconcile_W3f.txt shows removed 0, changed limited to listed spec updates (ids pasted), failed 0, and an arithmetic line base − removed + added = new that holds
    - tests/m3 outcome Counter identical before and after
    - sparse_parent_benchmark.tsv porcelain empty
  </acceptance_criteria>
  <done>The whole suite is green and every difference from the W4a baseline is accounted for by id.</done>
</task>

<task type="auto">
  <name>Task 3: Records — HANDOFF, STATE, LOG, PLAN-INDEX, W4a depends_on; commit; push</name>
  <files>.planning/HANDOFF.json, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md</files>
  <read_first>
    - .planning/HANDOFF.json keys w4a_checkpoint, resume_on_reconnect, suite_baselines_ta_r4_latest, do_not (jq only; the file is large)
    - .planning/STATE.md lines 1-60 (the W4a RESUME block)
    - ta-r4-W4a-amendment-draft-review-locks-PLAN.md frontmatter only
    - the plan 15.1–15.5 SUMMARYs and LOG entries (commit shas, sha old → new, region-contribution totals and FLAG)
  </read_first>
  <action>
    1. HANDOFF.json (Python json, indent preserved as in the file, all keys kept):
       - w4a_checkpoint.production_blockers: for N1 and N2 keep the original string as `<key>_PRE_2026_11_04` and set
         the key to "RESOLVED 2026-11-04 W3f <commit sha(s)>: <one line of the new behaviour>"; same treatment for each
         other_code_items entry (N3, N4, N5, N6, N7, N12, N14, T1, N9_N10_optional → resolved by widening the code);
         add any OPEN items from Task 1 as new production_blockers entries.
       - w4a_checkpoint.proposed_lock_values: confirmatory_sha256 → the new value (keep the old as
         `confirmatory_sha256_PRE_W3f`); add `n_regions_min: "7 (inside confirmatory:, bound by confirmatory_sha256)"`,
         `confirmatory_direction_test: "exact region-level sign-flip (DEC-2026-11-04-ta-r4-n7-region-signflip-and-floor)"`,
         and `region_contribution_proxy` with the per-contrast likely/unknown/unlikely totals and the FLAG text if raised.
         `decision_rules_yaml_locked` stays false; `signoff_written` stays false.
       - resume_on_reconnect: annotate step 4 "DONE 2026-11-04 (W3f, plans 15.1–15.6)"; step 3 unchanged (Carter's reply
         now carries the new confirmatory_sha256).
       - suite_baselines_ta_r4_latest: the new FULL counts + Slurm job id + data/r4/tmp/w3f/full_W3f.xml (keep the W4a
         string as `suite_baselines_ta_r4_W4a`).
       - do_not: annotate the run_susie_rss.R entry in place with
         " [2026-11-04: lifted once for the N1 cap move only — DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze; otherwise in force]";
         keep every other entry verbatim.
       Validate: `jq -e .w4a_checkpoint .planning/HANDOFF.json` exits 0 and the key count is ≥ the pre-edit count (print both).
    2. STATE.md: insert a new `## 2026-11-04 — **TRACK A ta-r4: W3f fix-up COMPLETE — W4a-T3 re-presented to Carter with confirmatory_sha256 <short>. NOTHING RUNNING.** (★ RESUME HERE — LATEST ★)`
       block above the W4a block (commits per plan, FULL counts, new sha, n_regions_min 7, region-contribution result and
       FLAG if raised, OPEN items if any, "Carter's reply format unchanged except the sha"); append "(SUPERSEDED by the
       W3f block above)" to the W4a block heading. Do not edit other blocks.
    3. W4a plan: change only the frontmatter line to `depends_on: ["ta-r4-W3f-review-suite-and-close"]`; verify with a
       yaml parse of the frontmatter and `git diff` showing exactly one changed line in that file.
    4. PLAN-INDEX: check that the plan-list rows 15.1–15.6 (added at planning time) and the §E/decision-coverage notes
       match what ran; correct facts only. Explicitly correct two standing rules (append a dated note, keep the old text):
       §B.6 — add "Lifted once for N1 (cap after LD restriction, flag default false) by DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze on Carter's explicit reply; otherwise in force; R_CODE_REF re-pinned to <sha7>" (if 15.1 stopped at its precondition, write that instead);
       §B.8 — LSF is superseded: "Cluster jobs via Slurm since 2026-11-03: sbatch -p compute -A clintonlab_cpu -q normal, always -t; Rscript is not on PATH in jobs (use $RSCRIPT)" (bsub_wrapper.sh / queue text marked superseded).
    5. LOG: W3f wave-close entry (review counts and dispositions, FULL reconciliation, sha old → new, HANDOFF fields
       changed, push result).
    6. `git fsck --connectivity-only`; explicit-path commit of the five files (+ the review file and DRAFT if not
       already committed) `docs(ta-r4-W3f): wave close — review banked, FULL reconciled, W4a-T3 re-presented (sha <short>)`;
       `git fsck`; `git push origin HEAD`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && export PATH=/home/ckclinto/miniconda3/bin:$PATH && jq -r '.w4a_checkpoint.proposed_lock_values.confirmatory_sha256, .w4a_checkpoint.signoff_written' .planning/HANDOFF.json && grep -m1 "^depends_on" .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import yaml; print(yaml.safe_load(open('config/ta_r4/decision_rules.yaml'))['locked'])" && ls .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/ && git log origin/m3-W2-aou-deltas..HEAD --oneline | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - HANDOFF prints the new sha (≠ f6e6e90f…) and signoff_written false; W4a depends_on line is `depends_on: ["ta-r4-W3f-review-suite-and-close"]`
    - decision_rules.yaml `locked` prints False; signoffs/ lists only W2c-T4.yaml and W3b-T3.yaml
    - `git diff <pre-W3f HEAD 72b99064>..HEAD -- ta-r4-W4a-amendment-draft-review-locks-PLAN.md` changes exactly one line
    - unpushed commit count prints 0
  </acceptance_criteria>
  <done>W4a-T3 is ready to re-present: blockers resolved on record, new sha published in the resume surfaces, nothing locked or signed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| repo → public OSF text | the reviewed extract becomes public after W4b |
| executor → Carter's lock | records must not pre-empt or simulate Carter's sign-off |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3f6-01 | Tampering | mis-specified premise in the changed text | mitigate | brief-blind Codex review against the code; verbatim bank; dispositions |
| T-r4-W3f6-02 | Spoofing | lock values without Carter | mitigate | no signoff/raw file written; locked stays false; verified in Task 3 |
| T-r4-W3f6-03 | Repudiation | suite drift hidden in aggregate counts | mitigate | reconciliation by test id; changed ids must be listed spec updates; STOP otherwise |
</threat_model>

<verification>
Review banked and dispositioned; FULL reconciled by id with 0 failures; HANDOFF/STATE/LOG/PLAN-INDEX refreshed;
W4a depends_on edited; pushed; nothing locked or signed.
</verification>

<success_criteria>
All W4a production blockers are resolved in code, the DRAFT matches the code, a new confirmatory_sha256 is recorded,
and the full suite is reconciled — W4a-T3 can be re-presented.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-review-suite-and-close-SUMMARY.md`
</output>
