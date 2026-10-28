---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 17
slug: W4b-amendment-final-and-posting-gate
type: execute
wave: 17
depends_on: ["ta-r4-W4a-amendment-draft-review-locks"]
files_modified:
  - config/ta_r4/coloc_priors.yaml
  - config/ta_r4/decision_rules.yaml
  - config/ta_r4/simulation.yaml
  - .planning/amendments/osf-amendment-r4-FINAL.md
  - .planning/amendments/osf-amendment-r4-PUBLIC.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/R4-LOCK.json
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W4b-T3.yaml
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
autonomous: false
requirements:
  - REQ-OSF-PREREG
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "This plan starts only if `python -m ta_r4.signoff verify W4a-T3` exits 0"
    - "Commit A (`chore(ta-r4-W4b): lock pre-registration parameters`) contains only the three config files, with Carter's values and locked: true; test_signoffs passes with the lock sentinel live (config values == W4a-T3 values)"
    - "osf-amendment-r4-FINAL.md cites commit A as \"analysis locked in commit <sha> before production\"; osf-amendment-r4-PUBLIC.md == extract(FINAL) byte-for-byte (checker W4)"
    - "Task 2 writes and commits `$P/R4-LOCK.json` {\"lock_sha\": <commit A full sha>}; at hand-off the gate is provably closed (`r4_lock_gate check --stage production` exits 1, '(i) W4b-T3')"
    - "The lock step is a checkpoint:human-action: production opens only when Carter's reply parses as `carter-approved YYYY-MM-DD` + `lock_sha: <40-hex>` equal to the lock record AND `r4_lock_gate check --stage production` exits 0 (DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf)"
    - "The executor never posts to OSF; OSF posting of PUBLIC is optional and nothing reads it"
  artifacts:
    - path: ".planning/amendments/osf-amendment-r4-FINAL.md"
      provides: "final amendment with Pre-Paste checklist (internal) and the PASTE block"
      contains: "--- PASTE INTO OSF FROM HERE ---"
    - path: ".planning/amendments/osf-amendment-r4-PUBLIC.md"
      provides: "the public extract (Carter may upload it to OSF; optional)"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/R4-LOCK.json"
      provides: "lock record: lock_sha = commit A"
  key_links:
    - from: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/R4-LOCK.json (lock_sha)"
      to: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W4b-T3.yaml (Carter)"
      via: "lock_sha equality, checked by r4_lock_gate"
      pattern: "lock_sha"
---

<objective>
Wave 4b applies Carter's locks in a single configuration commit (commit A), writes the lock record,
finalizes the amendment and its public extract, and stops at a lock checkpoint that auto-mode cannot
pass: Carter confirms commit A's sha. OSF posting is optional (DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf).

Purpose: D-05, D-26, D-27, REQ-OSF-PREREG. Split from the original W4 (checker W14); PUBLIC extract
(checker W4); human-action posting (B1) with the code gate kept.
Output: locked configs (commit A), lock record + FINAL + PUBLIC amendment files (commit B), the W4b-T3 lock sign-off.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-SUMMARY.md
@.planning/amendments/osf-amendment-r4-DRAFT.md

<interfaces>
Sign-offs: python -m ta_r4.signoff verify W4a-T3 / record W4b-T3
Lock record (r4_lock_gate.LOCK_RECORD_REL): $P/R4-LOCK.json = {"lock_sha": <commit A full 40-hex sha>}
Gate CLI: python -m ta_r4.r4_lock_gate check --stage production (offline); python -m ta_r4.r4_lock_gate paths
Extractor: python -m ta_r4.extract_paste_block --in FINAL --out PUBLIC
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Verify the lock sign-off; apply the locks in commit A</name>
  <files>config/ta_r4/coloc_priors.yaml, config/ta_r4/decision_rules.yaml, config/ta_r4/simulation.yaml</files>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W4a-T3.yaml
    - tests/ta_r4/test_signoffs.py (the lock sentinel)
  </read_first>
  <action>
    1. `cd src/python && $PY -m ta_r4.signoff verify W4a-T3`. Non-zero → STOP.
    2. Write the recorded values into the configs (p12_primary → coloc_priors.yaml; kappa_cut,
       n_both_min, partial_rule.* → decision_rules.yaml) and set `locked: true` in all three.
       simulation.yaml changes only its `locked` flag.
    3. Run `$PY -m pytest tests/ta_r4/test_signoffs.py tests/ta_r4/test_estimands.py tests/ta_r4/test_branch_classifier.py -q`.
       The lock sentinel is now live and must pass; estimand outputs stay DRAFT (no gate yet).
    4. Run `git fsck --connectivity-only`, then commit A with exactly the three files:
       `chore(ta-r4-W4b): lock pre-registration parameters`. Run fsck again; push. Record commit A's
       sha in the LOG.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import yaml;print([yaml.safe_load(open(f'config/ta_r4/{n}.yaml'))['locked'] for n in ('coloc_priors','decision_rules','simulation')])" && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_signoffs.py -q && git log -1 --name-only --format=%s</automated>
  </verify>
  <acceptance_criteria>
    - prints `[True, True, True]`; test_signoffs passes; the last commit lists exactly the three config files
  </acceptance_criteria>
  <done>The decision rule, priors and simulation design are locked in one commit tied to Carter's sign-off.</done>
</task>

<task type="auto">
  <name>Task 2: lock record, FINAL amendment, PUBLIC extract, commit B; prove the gate closed</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/R4-LOCK.json, .planning/amendments/osf-amendment-r4-FINAL.md, .planning/amendments/osf-amendment-r4-PUBLIC.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>
    0. Write `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/R4-LOCK.json` =
       `{"lock_sha": "<commit A full sha>"}` (the record cannot live in the commit it names).
    1. Copy DRAFT → `osf-amendment-r4-FINAL.md`, replace every `‹CARTER-LOCK›` with the locked
       values, and cite commit A in paragraph (m) as "analysis locked in commit <sha> before
       production", alongside the analysis-code shas. Never write "pre-registered on OSF" for R4.
       Fill the optional Pre-Paste checklist (outside the extract): Carter MAY upload
       `.planning/amendments/osf-amendment-r4-PUBLIC.md` unchanged to osf.io/az52u; if he does, the URL
       is recorded in `.planning/osf_deviations.md`. Nothing reads it; it never blocks W5.
    2. `cd src/python && $PY -m ta_r4.extract_paste_block --in ../../.planning/amendments/osf-amendment-r4-FINAL.md --out ../../.planning/amendments/osf-amendment-r4-PUBLIC.md`.
    3. Run `test_amendment_text.py` (FINAL and PUBLIC checks now active: no placeholder, no banned
       word, no internal content anywhere in the extract, PUBLIC == extract(FINAL)).
    4. Run §C with label `W4b`, commit type `docs` (commit B, including R4-LOCK.json). Record
       `sha256sum .planning/amendments/osf-amendment-r4-PUBLIC.md` in the LOG.
    5. `cd src/python && $PY -m ta_r4.r4_lock_gate check --stage production`; paste its non-zero
       refusal ("(i) W4b-T3"). This proves the gate is closed at hand-off.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py -q -rs && cd src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.r4_lock_gate check --stage production; test $? -ne 0 && echo GATE_CLOSED</automated>
  </verify>
  <acceptance_criteria>
    - the amendment text test passes with the FINAL/PUBLIC checks RUN (no skip); `GATE_CLOSED` printed
    - the PUBLIC sha256 is in the LOG; R4-LOCK.json, FINAL and PUBLIC are committed and pushed
  </acceptance_criteria>
  <done>The analysis is locked and recorded; the public file is exactly the paste block; the gate is closed.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 3: LOCK GATE — Carter confirms the lock commit (human-action; auto-mode cannot pass it)</name>
  <what-built>Locked configs (commit A), the lock record, FINAL + PUBLIC amendment (commit B), and a closed production gate.</what-built>
  <how-to-verify>
    1. Check that commit A (`git show --stat <lock_sha>`) is the lock you approve and that it is pushed.
    2. Reply as below. (Optional: upload PUBLIC to osf.io/az52u; if you do, the URL goes in `.planning/osf_deviations.md`.)
  </how-to-verify>
  <resume-signal>Carter replies with the first line exactly `carter-approved YYYY-MM-DD`, then `lock_sha: <40-hex sha of commit A>`. Any other reply, including a bare "approved", means WAIT. Even a valid reply opens production only if the lock gate passes.</resume-signal>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W4b-T3.yaml, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <action>
    Sign-off integrity (§B.15): the executor never authors, types or completes any
    `carter-approved` text and never writes signoffs/*.yaml except via `python -m ta_r4.signoff record`.
    The raw file is written only from the resume payload the orchestrator passes, which must be
    Carter's message pasted verbatim (never a summary, paraphrase or auto response). The SUMMARY
    quotes the resume payload next to the recorded raw_sha256.

    1. Validate the reply without writing: `$PY -c "from ta_r4.signoff import parse_signoff; ..."`
       (min_date = date of commit B). Invalid, or its lock_sha != R4-LOCK.json → WAIT (re-present; write nothing).
    2. `record W4b-T3` from the saved reply; commit the sign-off and the LOG with explicit paths.
    3. `cd src/python && $PY -m ta_r4.r4_lock_gate check --stage production` must exit 0; paste it. Non-zero → log
       the reason and STOP. Push.
  </action>
  <verify><automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.signoff verify W4b-T3 && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.r4_lock_gate check --stage production && echo GATE_OPEN</automated></verify>
  <acceptance_criteria>
    - `GATE_OPEN` printed; `test_signoffs.py` passes (tracked lock record ⇒ valid W4b-T3 with equal lock_sha)
    - the SUMMARY quotes the resume payload verbatim next to the recorded raw_sha256
  </acceptance_criteria>
  <done>The R4 analysis is locked in commit A before production, and production is unlocked only by the lock gate and Carter's recorded lock_sha (DEC-2026-10-28-ta-r4-w5-gate-git-lock-not-osf).</done>
  <read_first>
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/R4-LOCK.json
  </read_first>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| repo → public OSF record | optional, irreversible, public action (Carter only) |
| auto-mode → gate | an auto-selected option must not open production |
| executor → lock record | a fabricated or moved lock_sha must not open production |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W4b-01 | Spoofing | lock record fabricated | mitigate | Carter's W4b-T3 lock_sha must equal the record; lock_sha ancestor of HEAD with all configs locked; §B.12 |
| T-r4-W4b-02 | Repudiation | parameters changed after the lock | mitigate | lock commit A cited in the public text; W5a–W6 diff analysis paths against commit A before every fire |
| T-r4-W4b-03 | Information disclosure | internal content uploaded | mitigate | if Carter uploads, it is PUBLIC = extract(FINAL), tested for internal content |
| T-r4-W4b-04 | Elevation of privilege | auto-approval of the lock | mitigate | `checkpoint:human-action` + `carter-approved` token + lock gate |
</threat_model>

<verification>
Configs locked in one commit tied to Carter's sign-off. PUBLIC == extract(FINAL). The gate was closed
at hand-off and opens only through the lock record plus Carter's recorded lock_sha.
</verification>

<success_criteria>
The analysis is locked in commit A with every decision rule fixed by Carter before any production
result exists, and the code enforces that ordering.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4b-amendment-final-and-posting-gate-SUMMARY.md`
</output>
