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
    - "osf-amendment-r4-FINAL.md cites commit A as the locked-configuration commit; osf-amendment-r4-PUBLIC.md == extract(FINAL) byte-for-byte; PUBLIC is the file Carter uploads, and the sentinel's amendment_path/amendment_sha256 refer to PUBLIC (checker W4)"
    - "At hand-off the gate is provably closed (`r4_osf_gate check --stage production` exits 1, 'sentinel absent')"
    - "The posting step is a checkpoint:human-action: production opens only when Carter's reply parses as `carter-approved YYYY-MM-DD` + `posted: yes` AND `verify-online` (one OSF API call) and the offline `check` both exit 0 against Carter's committed sentinel (D-05, D-27, B1)"
    - "The executor NEVER posts to OSF and NEVER creates OSF-R4-POSTED.json; the sentinel's commit is not one of the executor's commits"
  artifacts:
    - path: ".planning/amendments/osf-amendment-r4-FINAL.md"
      provides: "final amendment with Pre-Paste checklist (internal) and the PASTE block"
      contains: "--- PASTE INTO OSF FROM HERE ---"
    - path: ".planning/amendments/osf-amendment-r4-PUBLIC.md"
      provides: "the exact file Carter uploads to osf.io/az52u; its sha256 is what the gate verifies"
  key_links:
    - from: ".planning/amendments/osf-amendment-r4-PUBLIC.md (sha256)"
      to: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/OSF-R4-POSTED.json (Carter)"
      via: "amendment_sha256 field; verified against the OSF API by r4_osf_gate verify-online"
      pattern: "amendment_sha256"
---

<objective>
Wave 4b applies Carter's locks in a single configuration commit, finalizes the amendment, produces
the paste-only public file whose hash the gate verifies, and stops at a posting checkpoint that
auto-mode cannot pass. Carter alone posts the public file on osf.io/az52u and commits the sentinel.

Purpose: D-05, D-26, D-27, REQ-OSF-PREREG. Split from the original W4 (checker W14); PUBLIC extract
(checker W4); human-action posting (B1) with the code gate kept.
Output: locked configs (commit A), FINAL + PUBLIC amendment files (commit B), the posting sign-off.
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
Sentinel schema (r4_osf_gate.py): {osf_url, osf_file_guid, posted_utc, amendment_path, amendment_sha256, head_sha}
Gate CLI: python -m ta_r4.r4_osf_gate verify-online --stage production (submit host; one API call; writes data/r4/gate/osf_receipt_<HEAD>.json)
          python -m ta_r4.r4_osf_gate check --stage production (offline)
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
  <name>Task 2: FINAL amendment, PUBLIC extract, commit B; prove the gate closed</name>
  <files>.planning/amendments/osf-amendment-r4-FINAL.md, .planning/amendments/osf-amendment-r4-PUBLIC.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md</files>
  <read_first>
    - .planning/amendments/osf-amendment-r4-DRAFT.md
    - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md §C
  </read_first>
  <action>
    1. Copy DRAFT → `osf-amendment-r4-FINAL.md`, replace every `‹CARTER-LOCK›` with the locked
       values, and cite commit A's sha in paragraph (m) as the locked-configuration commit, alongside
       the analysis-code shas. Fill the Pre-Paste checklist (outside the extract):
       1. upload `.planning/amendments/osf-amendment-r4-PUBLIC.md` UNCHANGED as a supplementary file on osf.io/az52u (not FINAL);
       2. copy the OSF file GUID;
       3. `sha256sum .planning/amendments/osf-amendment-r4-PUBLIC.md`;
       4. create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/OSF-R4-POSTED.json` with osf_url, osf_file_guid, posted_utc (ISO-8601 Z), `amendment_path: .planning/amendments/osf-amendment-r4-PUBLIC.md`, amendment_sha256, head_sha (`git rev-parse HEAD` at posting);
       5. `git add` that file explicitly, commit, push;
       6. record the URL and timestamp in `.planning/osf_deviations.md` under the R4 entry;
       7. reply to the checkpoint with `carter-approved YYYY-MM-DD` and `posted: yes`.
    2. `cd src/python && $PY -m ta_r4.extract_paste_block --in ../../.planning/amendments/osf-amendment-r4-FINAL.md --out ../../.planning/amendments/osf-amendment-r4-PUBLIC.md`.
    3. Run `test_amendment_text.py` (FINAL and PUBLIC checks now active: no placeholder, no banned
       word, no internal content anywhere in the extract, PUBLIC == extract(FINAL)).
    4. Run §C with label `W4b`, commit type `docs` (commit B). Record
       `sha256sum .planning/amendments/osf-amendment-r4-PUBLIC.md` in the LOG.
    5. `cd src/python && $PY -m ta_r4.r4_osf_gate check --stage production`; paste its non-zero
       refusal ("sentinel absent"). This proves the gate is closed at hand-off.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py -q -rs && cd src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.r4_osf_gate check --stage production; test $? -ne 0 && echo GATE_CLOSED</automated>
  </verify>
  <acceptance_criteria>
    - the amendment text test passes with the FINAL/PUBLIC checks RUN (no skip); `GATE_CLOSED` printed
    - the PUBLIC sha256 is in the LOG; FINAL and PUBLIC are committed and pushed
  </acceptance_criteria>
  <done>The pre-registration is final and committed; the public file is exactly the paste block; the gate is closed.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 3: OSF POSTING GATE — Carter posts the PUBLIC file and commits the sentinel (human-action; auto-mode cannot pass it)</name>
  <what-built>Locked configs (commit A), FINAL + PUBLIC amendment (commit B) with the Pre-Paste checklist, and a closed production gate.</what-built>
  <how-to-verify>
    1. Follow the Pre-Paste checklist in `.planning/amendments/osf-amendment-r4-FINAL.md` (upload PUBLIC unchanged to osf.io/az52u; commit and push the sentinel).
    2. Reply as below.
  </how-to-verify>
  <resume-signal>Carter replies with the first line exactly `carter-approved YYYY-MM-DD`, then `posted: yes`. Any other reply, including a bare "approved", means WAIT. Even a valid reply opens production only if the gate checks below pass.</resume-signal>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/signoffs/W4b-T3.yaml, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md</files>
  <action>
    1. Validate the reply without writing: `$PY -c "from ta_r4.signoff import parse_signoff; ..."`
       (min_date = date of commit B). Invalid → WAIT (re-present; write nothing).
    2. Run `cd src/python && $PY -m ta_r4.r4_osf_gate verify-online --stage production && $PY -m ta_r4.r4_osf_gate check --stage production`.
       Either non-zero → log the reason and WAIT. Never write OSF-R4-POSTED.json or a receipt by hand.
    3. On success: `record W4b-T3` from the saved reply; log the OSF URL, GUID, posted_utc and both
       gate outputs; commit the sign-off and the LOG with explicit paths; push. (This commit moves
       HEAD; each production fire runs `verify-online` again through `bin/r4_fire.sh`.)
  </action>
  <verify><automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.signoff verify W4b-T3 && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.r4_osf_gate verify-online --stage production && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m ta_r4.r4_osf_gate check --stage production && echo GATE_OPEN</automated></verify>
  <acceptance_criteria>
    - `GATE_OPEN` printed; `test_signoffs.py` passes (tracked sentinel ⇒ valid W4b-T3)
    - the sha of the commit that added the sentinel (`git log --format=%h --diff-filter=A -- .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/OSF-R4-POSTED.json`) is NOT in the list of commits this executor created (listed in the SUMMARY)
  </acceptance_criteria>
  <done>The R4 analysis is publicly pre-registered, and production is unlocked by verified evidence and Carter's recorded sign-off.</done>
  <read_first>
    - .planning/amendments/osf-amendment-r4-FINAL.md (Pre-Paste checklist)
  </read_first>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| repo → public OSF record | an irreversible, public action (Carter only) |
| auto-mode → gate | an auto-selected option must not open production |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W4b-01 | Spoofing | sentinel fabricated | mitigate | OSF API sha256 check in verify-online; §B.12; human-action posting checkpoint; sentinel commit must not be the executor's |
| T-r4-W4b-02 | Repudiation | parameters changed after the posting | mitigate | lock commit A cited in the public text; W5a–W6 diff analysis paths against commit A before every fire |
| T-r4-W4b-03 | Information disclosure | internal content uploaded | mitigate | Carter uploads PUBLIC = extract(FINAL), tested for internal content; the gate hashes PUBLIC |
| T-r4-W4b-04 | Elevation of privilege | auto-approval of posting | mitigate | `checkpoint:human-action` + `carter-approved` token + both gate checks |
</threat_model>

<verification>
Configs locked in one commit tied to Carter's sign-off. PUBLIC == extract(FINAL). The gate was closed
at hand-off and opens only on verified posting plus Carter's recorded reply.
</verification>

<success_criteria>
The comparison is publicly pre-registered with every decision rule fixed by Carter before any
production result exists, and the code enforces that ordering.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4b-amendment-final-and-posting-gate-SUMMARY.md`
</output>
