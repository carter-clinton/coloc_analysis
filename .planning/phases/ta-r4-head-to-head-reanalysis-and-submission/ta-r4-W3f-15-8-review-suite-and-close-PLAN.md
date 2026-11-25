---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8f
slug: W3f-15-8-review-suite-and-close
type: execute
wave: 15.8f
depends_on: ["ta-r4-W3f-multikey-fatal-and-chronology"]
gap_closure: true
files_modified:
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-AMENDMENT-REVIEW-as-received.md
  - .planning/HANDOFF.json
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md   # frontmatter depends_on only
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-SUMMARY.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Gates Q-157J and all five 2026-11-25 replies (gate_158.sh Q-158DIG Q-158R6S Q-158E7R Q-F3NL Q-158R7) pass, and every STOP reply named in a 15.8a–e SUMMARY (Q-158R2/R3/R5/R6, if any) re-gates with its pinned sha256"
    - "DRAFT (m) lists the 15.8 code commits with short labels (collector drop audit; OpenBLAS pin + guard; exact-precision writers; QTL_legacy NaN rule + E7 matched rounding; E7 filtered counts; multi-key fatal), only those that exist; the Pre-Paste gains one RESOLVED row each for R2–R7 and Q-F3N, with commit and plan (or the disclosed sentence's location where Carter kept a limitation); one script, old strings asserted unique; test_amendment_text.py green with its negative control"
    - "Before the review, a text-vs-code table in the LOG maps R2–R7 → code file:line at HEAD → DRAFT clause; a mismatch is fixed in the DRAFT only if the code is what the plan approved, else STOP"
    - "A brief-blind Codex review ran exactly as 15.7j's (same W4a instruction and wrapper lines, codex-cli and model as recorded in disposition_15_7j.md, read-only sandbox, prompt = instruction + extract only, from the repo root); output banked byte-for-byte (sha256 and byte count) in ta-r4-W3f-15-8-AMENDMENT-REVIEW-as-received.md with a disposition table whose row count equals the finding count; each finding verified at the reviewed HEAD with file:line"
    - "FULL under Slurm (cascadelake) reconciled per id against data/r4/tmp/w3f/q157/full_15_7j.xml: removed == the renames declared in 15.8a–e SUMMARYs (none expected); added == the union of their `New test ids`; outcome changes ⊆ the union of their `Declared spec updates`, each passed; 0 failed; totals == base (2,694 = 2,641 P / 53 S / 0 F) + Σ N_new (expected 7 + 11 + 8 + 6 + 6 + 2 = 40 → 2,734 = 2,681 P / 53 S / 0 F; read from the SUMMARYs, not typed); and against full_15_8e.xml: identical by id"
    - "HANDOFF w4a_checkpoint.production_blockers: the seven keys W3f157_R2, W3f157_R3, W3f157_R4, W3f157_R5, W3f157_R6, W3f157_R7 and W3f157_QF3N_premise (committed by 15.7j, b36b99d5, each marked 'decided by Carter → 15.8'; the names are final) must all exist (any missing is STOP); each value is replaced by a RESOLVED line (plan, commit, Carter label) with the old text kept under <key>_PRE_2026_11_24; new review OPEN items added as W3f158_*; resume_on_reconnect rewritten; every pre-existing string value still present"
    - "ta-r4-W4a-amendment-draft-review-locks-PLAN.md frontmatter depends_on == [\"ta-r4-W3f-15-8-review-suite-and-close\"]; `git diff` of that file is that one line"
    - "decision_rules.yaml locked: false; n_regions_min 7; no push, OSF, production fit or W4a-T3 lock"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-AMENDMENT-REVIEW-as-received.md"
      provides: "banked brief-blind review + dispositions"
  key_links:
    - from: "HANDOFF w4a_checkpoint.production_blockers"
      to: "the 15.8 SUMMARYs and the new review"
      via: "RESOLVED / OPEN entries"
      pattern: "W3f158_|RESOLVED 2026-11"
---

<objective>
Close 15.8: bring the DRAFT's commit list and Pre-Paste rows up to date, re-run the brief-blind Codex review on the
changed extract as 15.7j did, run FULL with a cumulative per-id reconciliation against full_15_7j.xml, and refresh the
resume records so that W4a-T3 (or any new OPEN item) is next.
Output: banked review, reconciled FULL, HANDOFF / STATE / LOG / PLAN-INDEX / W4a depends_on, SUMMARY. No push.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
Q-157J: file `W3f-carter-15-7j-open-items-reply-2026-11-24.txt`, sha256
`805afcd812902605dd9797d63c15fb201eae1fd2870db348182c1d38a640503e` (free text and question as in 15.8a <question>).
The five 2026-11-25 replies (question texts in 15.8a's <question> table), all re-gated here:
| QID | file | sha256 | label |
|---|---|---|---|
| Q-158DIG | `W3f-carter-15-8-Q-158DIG-reply-2026-11-25.txt` | `ea8fe4cdaf4bbcf802d65e68c75e66d3b095777f0e518e9ed57c088d3246ceb4` | `A: Exact round-trip everywhere r4 thresholds (Recommended)` |
| Q-158R6S | `W3f-carter-15-8-Q-158R6S-reply-2026-11-25.txt` | `7b3d1045f770bdea49123a85d58866501a46dbe62b0d9ddf5f9ac6bf36875b2d` | `Proceed, pin r_coloc only (Recommended)` |
| Q-158E7R | `W3f-carter-15-8-Q-158E7R-reply-2026-11-25.txt` | `43a4d89900c7225576a9edef1980716db999ca8c3193694305fca2c42376bd09` | `Add a matched-rounding column (Recommended)` |
| Q-F3NL | `W3f-carter-15-8-Q-F3NL-reply-2026-11-25.txt` | `9b4c0bb009e5262c38262da953e2a009b8c1859447bbb0975a24c68c9162b6a1` | `Keep legacy rule for QTL_legacy (Recommended)` |
| Q-158R7 | `W3f-carter-15-8-Q-158R7-reply-2026-11-25.txt` | `a9a6866eb9c4b518c7a98206273ddd55fe0cbd4e2e49c1b3d7264d2f69a261b8` | `Approve as written (Recommended)` |
STOP replies (Q-158R2/R3/R5/R6), if any were asked: re-gated with the sha256 pinned in their plans.
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-collector-drop-audit-PLAN.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-review-suite-and-close-PLAN.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-AMENDMENT-REVIEW-as-received.md
@data/r4/tmp/w3f/q157/disposition_15_7j.md

**Standing rules:** 15.8 shared protocol; memory feedback_internal_validation_cannot_catch_misspecified_premise (the
review is brief-blind and is not skipped) and reference_codex_cli_for_gsd_review.

**Review invocation (as 15.7j; read the exact command, CLI path and model from disposition_15_7j.md run notes and the
15.7j LOG entry, and record them):** `cd src/python && $PY -m ta_r4.extract_paste_block --in
../../.planning/amendments/osf-amendment-r4-DRAFT.md --out ../../$Q8/review_input.md`; `$Q8/codex_prompt.md` = the W4a
instruction verbatim + the W4a wrapper lines (prefix and suffix byte-equal to 15.7j's `$Q/codex_prompt.md` around its
extract; assert) + the new extract, nothing else (no CONTEXT, LOG, SUMMARY, finding list or 15.7j review);
`codex exec --skip-git-repo-check --sandbox read-only -m <15.7j model> - < $Q8/codex_prompt.md` from the repo root. On CLI
failure: record, retry once with the model the account's cache lists; a second failure is STOP (not skipped).

**Forbidden:** analysis-code edits (a finding needing code is OPEN for Carter); any fit; W4a PLAN edits beyond
depends_on; removing any HANDOFF string.
</context>

<tasks>

<task type="auto">
  <name>Task 1: DRAFT (m) + Pre-Paste; text-vs-code table; brief-blind review; bank; dispositions (DRAFT text only)</name>
  <files>.planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-AMENDMENT-REVIEW-as-received.md</files>
  <read_first>
    - the six 15.8a–e SUMMARYs (15.8c2 included: commits, DRAFT sentences, id lists, Carter replies)
    - the 15.7j review file (header, verbatim block and disposition format)
  </read_first>
  <action>
    0. `git rev-parse HEAD > $Q8/start_15_8f.txt`; `bash $Q8/gate_157j.sh`; `bash $Q8/gate_158.sh Q-158DIG Q-158R6S
       Q-158E7R Q-F3NL Q-158R7`; re-gate any STOP reply with its pinned sha256.
    1. DRAFT (one script; old strings asserted unique): (m) adds the 15.8 code commits; Pre-Paste: the 15.7j rows for
       R2–R7 and Q-F3N: add one RESOLVED row each (the Pre-Paste has no 15.7j OPEN rows for them). test_amendment_text.py + test_prelock_pilot_fits.py green.
    2. Text-vs-code table in the LOG (R2–R7, Q-F3N, matched rounding).
    3. Review per <context>; save prompt, sha256, stdout, stderr, rc, start time and HEAD under `$Q8/codex_*`.
    4. Bank: 3-line header (date + reviewed HEAD, command, prompt sha256), output verbatim with sha256 and byte count
       (assert equal to raw stdout), then the disposition table (finding → verified at HEAD with file:line →
       CONFIRMED / PARTLY / REFUTED → "DRAFT fixed" / "rejected with evidence" / "OPEN for Carter (needs code)");
       findings == rows, reconciled arithmetically.
    5. Apply DRAFT-text fixes only; test_amendment_text.py green with its negative control (a banned word inserted in
       (a) fails the framing test; restore; sha256 equal). Commit 1 (`docs(ta-r4-W3f): 15.8 DRAFT (m)/Pre-Paste;
       brief-blind re-review banked; dispositions (15.8f)`), explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_157j.sh && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py tests/ta_r4/test_prelock_pilot_fits.py -q -p no:cacheprovider && test "$(cat data/r4/tmp/w3f/q158/codex_rc.txt)" = 0 && test -s .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-AMENDMENT-REVIEW-as-received.md</automated>
  </verify>
  <done>Review banked byte-for-byte; every finding verified and dispositioned; only DRAFT text changed.</done>
</task>

<task type="auto">
  <name>Task 2: FULL under Slurm; cumulative per-id reconciliation vs full_15_7j.xml (2,694 = 2,641 P / 53 S / 0 F)</name>
  <files>(scratch only: $Q8/full_15_8f.xml, $Q8/check_15_8f.py, $Q8/reconcile_15_8f.txt)</files>
  <action>
    1. `$Q8/close.sh 15_8f` under sbatch (protocol, `--constraint=cascadelake`).
    2. `$Q8/check_15_8f.py`: (a) vs full_15_7j.xml with NEW = union of the `## New test ids` sections (parsed as junit ids,
       `tests.ta_r4.test_x::test_y`, one per line; a line not of that form is STOP) and declared =
       union of the `## Declared spec updates` sections of the six 15.8a–e SUMMARYs (15.8c2 included), parsed (a SUMMARY missing a
       section is STOP; nothing typed into the check); renames = those the SUMMARYs declare; expect = base totals
       (read from full_15_7j.xml) + Σ N_new. (b) vs full_15_8e.xml: identical by id. Arithmetic line in
       `$Q8/reconcile_15_8f.txt`. Any miss → STOP; no clean-close records.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8f.py</automated>
  </verify>
  <done>FULL reconciled cumulatively and against 15.8e; arithmetic recorded.</done>
</task>

<task type="auto">
  <name>Task 3: Records — HANDOFF w4a_checkpoint, STATE, LOG, PLAN-INDEX, W4a depends_on (frontmatter only); commit (no push)</name>
  <files>.planning/HANDOFF.json, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-SUMMARY.md</files>
  <action>
    1. HANDOFF (one script, `data/r4/tmp/w3f/handoff_edit.py` as the pattern): per must_haves; `w4a_checkpoint.read_first`
       gains the new review file; `suite_baselines_ta_r4_latest` = full_15_8f.xml counts. Assert key count after ==
       before + added keys and every pre-existing string value still present.
    2. W4a PLAN: frontmatter `depends_on: ["ta-r4-W3f-15-8-review-suite-and-close"]`; paste the one-line `git diff` in the LOG.
    3. PLAN-INDEX: 15.8f row COMPLETE with the review counts; the 15.8 paragraph's last sentence says W4a now depends on
       15.8f. STATE ★ RESUME HERE — LATEST ★ (NEXT = W4a-T3 lock presentation, or new OPEN items first; NOT PUSHED);
       prior block SUPERSEDED. LOG entry. SUMMARY (with `## Declared spec updates`: none, and `## New test ids`: none).
    4. PINS (`pytest tests/m3/test_source_freeze_pins.py`) and `git status --porcelain` on files_modified; `git fsck
       --connectivity-only` before and after; commit 2 (`docs(ta-r4-W3f): 15.8 close — review banked, FULL reconciled,
       HANDOFF refreshed, W4a depends_on (no push)`), explicit paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && head -8 .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md | grep -qF 'depends_on: ["ta-r4-W3f-15-8-review-suite-and-close"]' && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import json,yaml;h=json.load(open('.planning/HANDOFF.json'));b=h['w4a_checkpoint']['production_blockers'];K=['W3f157_R2','W3f157_R3','W3f157_R4','W3f157_R5','W3f157_R6','W3f157_R7','W3f157_QF3N_premise'];assert all(k in b and k+'_PRE_2026_11_24' in b and b[k].startswith('RESOLVED') for k in K), [k for k in K if k not in b or k+'_PRE_2026_11_24' not in b];d=yaml.safe_load(open('config/ta_r4/decision_rules.yaml'));assert d['locked'] is False" && test -z "$(git status --porcelain -- .planning/HANDOFF.json .planning/STATE.md)"</automated>
  </verify>
  <done>Records committed with explicit paths; W4a depends on 15.8f; nothing pushed.</done>
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
| T-r4-158f-01 | Repudiation | review provenance | mitigate | prompt and output sha256; banked block byte-equal to raw stdout; wrapper byte-equal to 15.7j's |
| T-r4-158f-02 | Tampering | silent test loss across 15.8 | mitigate | cumulative per-id reconciliation vs full_15_7j.xml from parsed SUMMARY sections |
| T-r4-158f-03 | Tampering | HANDOFF history | mitigate | old text under _PRE_2026_11_24 keys; string-preservation assert |
| T-r4-158f-04 | Information disclosure | push / OSF | accept | none in 15.8 |
</threat_model>

<verification>
- Review banked; check_15_8f.py passes; HANDOFF and W4a depends_on asserts pass; decision_rules.yaml locked false.
</verification>

<success_criteria>
- 15.8 closes with R2–R7 resolved or carried as Carter-dispositioned items, a fresh brief-blind review, and W4a-T3 next.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-SUMMARY.md`
</output>
