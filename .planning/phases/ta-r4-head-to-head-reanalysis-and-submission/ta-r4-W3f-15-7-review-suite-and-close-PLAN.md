---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.7j
slug: W3f-15-7-review-suite-and-close
type: execute
wave: 15.7j
depends_on: ["ta-r4-W3f-pilot-fit-disclosure"]
gap_closure: true
files_modified:
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-AMENDMENT-REVIEW-as-received.md
  - .planning/HANDOFF.json
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-review-suite-and-close-SUMMARY.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "DRAFT (m) lists every 15.7 code commit with a short label; the Pre-Paste OPEN row for F1–F15 is replaced by one row per finding: RESOLVED with the commit sha and plan, or (for a Carter choice that kept a limitation) the disclosed sentence's location"
    - "Before the review, each 15.7 behaviour change is checked against its DRAFT sentence (a table in the LOG: finding → code file:line → DRAFT clause), so the review sees text that already describes the code"
    - "A brief-blind Codex review ran on the extract of the changed DRAFT exactly as 15.6 did (same instruction, codex-cli and model as recorded in 15.6, read-only sandbox, prompt = instruction + extract only); its output is banked byte-for-byte with sha256 and byte count in ta-r4-W3f-15-7-AMENDMENT-REVIEW-as-received.md, followed by a disposition table whose row count equals the finding count"
    - "Each new finding is verified against the code at the reviewed HEAD and marked CONFIRMED / PARTLY / REFUTED with file:line; DRAFT-text fixes only; anything needing code is OPEN for Carter and becomes a HANDOFF production blocker"
    - "FULL under Slurm reconciled per id against data/r4/tmp/w3f/full_W3f.xml: removed == exactly the declared renames (15.7d's _19_ → _20_), each successor passed; added == the union of the 15.7a–15.7i SUMMARY id lists (15.7h2 included); outcome changes ⊆ the declared spec-update ids, read by check_15_7j.py from the `Declared spec updates` section of every 15.7 SUMMARY (15.7a–15.7i, 15.7h2 included; no list is typed into the check; a SUMMARY missing the section is a STOP), each still passed; totals = 2,555 + 138 − 1 = 2,692, 0 failed; and per id against full_15_7i.xml: identical"
    - "HANDOFF w4a_checkpoint: each production_blockers.W3f_F* value is replaced by a RESOLVED line (plan, commit, Carter label where one applied) with the old text kept under W3f_F*_PRE_2026_11_20; new review OPEN items added as W3f157_*; resume_on_reconnect rewritten for W4a-T3; every other pre-existing key and string kept"
    - "ta-r4-W4a-amendment-draft-review-locks-PLAN.md frontmatter depends_on == [\"ta-r4-W3f-15-7-review-suite-and-close\"]; no other line of that file changes"
    - "decision_rules.yaml locked: false; no push, OSF, W4a-T3 lock or n_regions_min change"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-AMENDMENT-REVIEW-as-received.md"
      provides: "banked review + dispositions"
  key_links:
    - from: "HANDOFF w4a_checkpoint.production_blockers"
      to: "the 15.7 SUMMARYs and the new review"
      via: "RESOLVED / OPEN entries"
      pattern: "W3f157_|RESOLVED 2026-11"
---

<objective>
Close 15.7: bring the DRAFT's commit list and Pre-Paste table up to date, re-run the brief-blind review on the changed
extract as 15.6 did, run FULL with a cumulative per-id reconciliation, and refresh the resume records so W4a-T3 is the
next step.
Output: banked review, reconciled FULL, HANDOFF / STATE / LOG / PLAN-INDEX / W4a depends_on, SUMMARY. No push.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-review-suite-and-close-PLAN.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-review-suite-and-close-SUMMARY.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-AMENDMENT-REVIEW-as-received.md

**Standing rules:** PLAN-INDEX §A, §B and the 15.7 shared protocol. Memory rules
`feedback_internal_validation_cannot_catch_misspecified_premise` (the review is brief-blind and is not skipped) and
`reference_codex_cli_for_gsd_review`.

**Review invocation (as 15.6, from its <interfaces> and the 15.6 LOG entry):** `cd src/python && $PY -m
ta_r4.extract_paste_block --in ../../.planning/amendments/osf-amendment-r4-DRAFT.md --out
../../$Q/review_input.md`; prompt `$Q/codex_prompt.md` = the W4a instruction verbatim + the W4a wrapper lines + the
extract, nothing else; `codex exec --skip-git-repo-check --sandbox read-only -m gpt-6.1-sol - < $Q/codex_prompt.md`
from the repo root (codex-cli 0.166.0 from the W4a scratch prefix). On CLI failure: record, retry once with the model
the account's cache lists; a second failure is STOP (the review is not skipped).

**Forbidden:** analysis-code edits (a finding needing code is OPEN for Carter); any fit; W4a PLAN edits beyond depends_on;
removing any HANDOFF string.
</context>

<tasks>

<task type="auto">
  <name>Task 1: DRAFT (m) + Pre-Paste; text-vs-code table; brief-blind review; bank; dispositions (DRAFT text only)</name>
  <files>.planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-AMENDMENT-REVIEW-as-received.md</files>
  <read_first>
    - all ten 15.7a–15.7i SUMMARYs (15.7h2 included) (commit shas, branches, DRAFT sentences, id lists)
    - the 15.6 review file (header, verbatim block and disposition format)
  </read_first>
  <action>
    0. `git rev-parse HEAD > $Q/start_15_7j.txt`; `git log --oneline` shows every 15.7 commit.
    1. DRAFT: (m) adds the 15.7 code commits (labels: runtime config guard; completeness by identity; cross-panel
       variant resolution; A1 allvars table; none-row denominators; deterministic purity; QTL sweep; null windows;
       proxy asthma pilot fits and exact-purity proxy; pilot-fit manifest; only those that exist). Pre-Paste: replace the F-list OPEN row with one row per finding.
       One script; old strings asserted unique. test_amendment_text.py green.
    2. Text-vs-code table in the LOG for F1–F15 (finding → code file:line at HEAD → DRAFT clause). A mismatch → fix
       the DRAFT text if the code is what the plan approved; otherwise STOP.
    3. Run the review (as in <context>); save prompt, sha256, stdout, stderr, rc, start time and HEAD under `$Q/`.
    4. Bank: 3-line header (date + reviewed HEAD, command, prompt sha256), the output verbatim with its sha256 and byte
       count, then the disposition table (finding → verified at HEAD with file:line → CONFIRMED / PARTLY / REFUTED →
       "DRAFT fixed" / "rejected with evidence" / "OPEN for Carter (needs code)"); counts reconciled (findings == rows).
       Assert the banked block's sha256 equals the raw stdout's.
    5. Apply DRAFT-text fixes only; test_amendment_text.py green, with its negative control (an inserted banned word
       fails the framing test; restore; sha256 equal). Commit 1 (`docs(ta-r4-W3f): 15.7 DRAFT (m)/Pre-Paste; brief-blind
       re-review banked; dispositions (15.7j)`), explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider && test -s .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-AMENDMENT-REVIEW-as-received.md && test "$(cat data/r4/tmp/w3f/q157/codex_rc.txt)" = 0</automated>
  </verify>
  <done>Review banked byte-for-byte; every finding verified and dispositioned; DRAFT text only changed.</done>
</task>

<task type="auto">
  <name>Task 2: FULL under Slurm; cumulative per-id reconciliation vs full_W3f.xml</name>
  <files>(scratch only: $Q/full_15_7j.xml, $Q/check_15_7j.py, $Q/reconcile_15_7j.txt)</files>
  <action>
    1. `$Q/close.sh 15_7j` under sbatch as in the protocol. Restore sparse_parent_benchmark.tsv.
    2. `$Q/check_15_7j.py`: (a) vs full_W3f.xml — removed == {`tests.ta_r4.test_run_aggregation::test_draft_writes_exactly_19_draft_tables`}
       with successor passed; added == union of the ten SUMMARY id lists (read from the SUMMARYs, not retyped);
       outcome changes on common ids ⊆ the union of the `Declared spec updates` sections of all 15.7 SUMMARYs (parsed, not
       typed; a SUMMARY without that section is a STOP (the plan's records are incomplete; report which)), all passed (a declared id that did not change is fine; an undeclared change is a STOP); totals = 2,555 + 138 − 1 =
       2,692 = 2,639 P / 53 S / 0 F (N_new 32 + 31 + 18 + 7 + 12 + 13 + 11 + 4 + 7 + 3 = 138, one rename), skips == 53. (b) vs full_15_7i.xml — identical
       by id. Arithmetic line in `$Q/reconcile_15_7j.txt`. Any miss → STOP; no clean-close records.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q157/check_15_7j.py</automated>
  </verify>
  <done>FULL reconciled cumulatively and against the last plan; arithmetic recorded.</done>
</task>

<task type="auto">
  <name>Task 3: Records — HANDOFF w4a_checkpoint, STATE, LOG, PLAN-INDEX, W4a depends_on (frontmatter only); commit (no push)</name>
  <files>.planning/HANDOFF.json, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-review-suite-and-close-SUMMARY.md</files>
  <action>
    1. HANDOFF (one script, `data/r4/tmp/w3f/handoff_edit.py` as the pattern): per must_haves; also
       `w4a_checkpoint.read_first` gains the new review file; `suite_baselines_ta_r4_latest` = full_15_7j.xml counts.
       Assert: key count after == before + added keys; every pre-existing string value still present somewhere.
    2. W4a PLAN: frontmatter `depends_on: ["ta-r4-W3f-15-7-review-suite-and-close"]`; `git diff` of the file is that one
       line (pasted in the LOG).
    3. PLAN-INDEX: 15.7j row COMPLETE with the review counts; the 15.7 paragraph's last sentence notes W4a now depends
       on 15.7j. STATE ★ RESUME HERE — LATEST ★ block (NEXT = W4a-T3 lock presentation, or the new OPEN items first;
       NOT PUSHED); prior block SUPERSEDED. LOG entry. SUMMARY.
    4. Run §C's PINS and `git status --porcelain` on files_modified; `git fsck --connectivity-only` before and after;
       commit 2 (`docs(ta-r4-W3f): 15.7 close — review banked, FULL reconciled, HANDOFF refreshed, W4a depends_on (no
       push)`), explicit paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && head -8 .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md | grep -qF 'depends_on: ["ta-r4-W3f-15-7-review-suite-and-close"]' && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import json,yaml;h=json.load(open('.planning/HANDOFF.json'));b=h['w4a_checkpoint']['production_blockers'];assert all(k+'_PRE_2026_11_20' in b for k in b if k.startswith('W3f_F') and not k.endswith('_PRE_2026_11_20'));assert yaml.safe_load(open('config/ta_r4/decision_rules.yaml'))['locked'] is False" && test -z "$(git status --porcelain -- .planning/HANDOFF.json .planning/STATE.md)"</automated>
  </verify>
  <done>HANDOFF, STATE, LOG, PLAN-INDEX, SUMMARY and W4a depends_on committed with explicit paths; nothing pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| internal records → public text | only a brief-blind reviewer reading code can catch a mis-specified claim |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-157j-01 | Repudiation | review provenance | mitigate | prompt and output sha256; banked block byte-equal to raw stdout |
| T-r4-157j-02 | Tampering | silent test loss across 15.7 | mitigate | cumulative per-id reconciliation vs full_W3f.xml |
| T-r4-157j-03 | Tampering | HANDOFF history | mitigate | old blocker text kept under _PRE_ keys; string-preservation assert |
| T-r4-157j-04 | Information disclosure | push / OSF | accept | none in 15.7 |
</threat_model>

<verification>
- Review banked; check_15_7j.py passes; HANDOFF and W4a depends_on asserts pass; decision_rules.yaml locked false.
</verification>

<success_criteria>
- 15.7 is closed with every W3f blocker resolved or carried as a dispositioned item, and W4a-T3 is the next step.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-review-suite-and-close-SUMMARY.md`
</output>
