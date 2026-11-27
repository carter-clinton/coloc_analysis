---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8g
slug: W3f-15-8-insert-review-and-close
type: execute
wave: 15.8g
depends_on: ["ta-r4-W3f-15-8-review-suite-and-close"]
gap_closure: true
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158AEIW-reply-<date>.txt   # written by the orchestrator; committed as received
  - .planning/DECISIONS.md                                                                                   # Q-158AEIW DEC
  - .planning/amendments/osf-amendment-r4-DRAFT.md
  - tests/ta_r4/test_asthma_eur_eaf_disclosure.py                                                           # test C appended
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-AMENDMENT-REVIEW-as-received.md
  - .planning/HANDOFF.json
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md   # frontmatter depends_on only
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-insert-review-and-close-SUMMARY.md
autonomous: true
requirements:
  - REQ-OSF-PREREG
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "Runs only if the orchestrator's resume message states the sha256 of W3f-carter-15-8-Q-158AEIW-reply-<date>.txt and the file's label is `Approve as written`; the executor pins that sha256 in gate_158.sh and STOPs on any mismatch; `Hold — do not insert`, `Reword (give the wording)` or `Leave the reference comparison out of the sentence` → STOP, nothing inserted (a reworded or reduced sentence is a new approval round, never an executor edit); the executor never writes the reply file"
    - "Gates Q-157J, the five 2026-11-25 replies, Q-158R2, Q-158OR/PAL/EL, Q-158R6G, Q-158KW, Q-158DFX, Q-158AEI, Q-158AEIM and Q-158AEIW pass (15.8f's <question> tables plus Q-158AEIW); the AEIW reply's question line contains 15.8f's $Q8/aeiw_sentence_15_8f.txt verbatim exactly once"
    - "DRAFT (c) gains the approved sentence after the orientation-step sentence (old string asserted unique): the inserted text, unwrapped, has sha256 == $Q8/aeiw_sentence_15_8f.sha256 == the sentence in the approved question line, asserted before and after insertion; DEC-<date>-ta-r4-draft-c-asthma-eaf-wording quotes the reply `cmp`-equal"
    - "Test C, test_draft_asthma_eaf_sentence_matches_the_manifests, matches every number in the sentence to the 15.8f manifests (none typed) and requires the anchor exactly once; NCs (iv) `19 of 225` → `18 of 225` and (v) the sentence removed each make it fail"
    - "DRAFT (m) lists the 15.8 code commits with short labels (collector drop audit; r4 sumstats in the catalog's orientation (15.8a2); production on the oriented inputs, catalogs a fixed point (15.8a3); eligibility re-measured on the oriented inputs (15.8a4); OpenBLAS pin + guard; exact-precision writers; QTL_legacy NaN rule + E7 matched rounding; E7 filtered counts; multi-key fatal; asthma EUR EAF diagnostic (15.8f)), only those that exist; the Pre-Paste gains one RESOLVED row each for R2–R7 and Q-F3N, with commit and plan (R2: resolved by 15.8a2–a4 under Carter's Q-158R2 D, the 15.8a audit being its measurement; not by 15.8a alone) (or the disclosed sentence's location where Carter kept a limitation); one script, old strings asserted unique; test_amendment_text.py green with its negative control"
    - "Before the review, a text-vs-code table in the LOG maps R2–R7, Q-F3N, matched rounding and the (c) EAF sentence → code / manifest file:line at HEAD → DRAFT clause; a mismatch is fixed in the DRAFT only if the code is what the plan approved, else STOP"
    - "A brief-blind Codex review ran exactly as 15.7j's (same W4a instruction and wrapper lines, codex-cli and model as recorded in disposition_15_7j.md, read-only sandbox, prompt = instruction + extract only, from the repo root); output banked byte-for-byte (sha256 and byte count) in ta-r4-W3f-15-8-AMENDMENT-REVIEW-as-received.md with a disposition table whose row count equals the finding count; each finding verified at the reviewed HEAD with file:line; a finding on Carter's approved (c) wording is OPEN for Carter"
    - "FULL under Slurm (cascadelake) reconciled per id against data/r4/tmp/w3f/q157/full_15_7j.xml: removed == the renames declared in the ten 15.8a–f SUMMARYs (15.8a, 15.8a2, 15.8a3, 15.8a4, 15.8b, 15.8c, 15.8c2, 15.8d, 15.8e, 15.8f; none expected); added == the union of their `New test ids` plus this plan's 1 id; outcome changes ⊆ the union of their `Declared spec updates`, each passed; 0 failed; totals == base (2,694 = 2,641 P / 53 S / 0 F) + Σ N_new (expected 72 + 2 + 1 = 75 → 2,769 = 2,716 P / 53 S / 0 F; read from the SUMMARYs, not typed); and against full_15_8f.xml: identical by id except exactly test C added, passed; test C also green in its own sbatch run before FULL"
    - "HANDOFF w4a_checkpoint.production_blockers: the seven keys W3f157_R2, W3f157_R3, W3f157_R4, W3f157_R5, W3f157_R6, W3f157_R7 and W3f157_QF3N_premise (committed by 15.7j, b36b99d5; names final) must all exist (any missing is STOP); each value replaced by a RESOLVED line (plan, commit, Carter label) with the old text kept under <key>_PRE_2026_11_24; W3f158f_Q158AEIW_pending (15.8f) replaced by a RESOLVED line with its old text under W3f158f_Q158AEIW_pending_PRE_15_8g; new review OPEN items added as W3f158_*; W3f158_asthma_eur_grch37_fasta, if present, stays OPEN; resume_on_reconnect rewritten; every pre-existing string value still present"
    - "ta-r4-W4a-amendment-draft-review-locks-PLAN.md frontmatter depends_on == [\"ta-r4-W3f-15-8-insert-review-and-close\"]; `git diff` of that file is that one line"
    - "decision_rules.yaml locked: false; n_regions_min 7; no push, OSF, production fit or W4a-T3 lock"
  artifacts:
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-AMENDMENT-REVIEW-as-received.md"
      provides: "banked brief-blind review + dispositions"
  key_links:
    - from: "DRAFT (c) sentence"
      to: "W3f-carter-15-8-Q-158AEIW-reply-<date>.txt"
      via: "sha256 of the approved sentence asserted at insertion"
      pattern: "As a diagnostic, not a filter: in asthma EUR"
    - from: "HANDOFF w4a_checkpoint.production_blockers"
      to: "the 15.8 SUMMARYs and the new review"
      via: "RESOLVED / OPEN entries"
      pattern: "W3f158_|RESOLVED 2026-11"
---

<objective>
Close 15.8 after Carter's Q-158AEIW approval: insert the approved DRAFT (c) sentence, bring DRAFT (m) and the
Pre-Paste up to date, re-run the brief-blind Codex review on the changed extract as 15.7j did, run FULL with a
cumulative per-id reconciliation against full_15_7j.xml over the ten 15.8a–f SUMMARYs, and refresh the resume records
so that W4a-T3 (or any new OPEN item) is next.
Output: AEIW DEC; the (c) sentence; test C; (m)/Pre-Paste; banked review; reconciled FULL; HANDOFF / STATE / LOG /
PLAN-INDEX / W4a depends_on; SUMMARY. No push.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<question>
All replies of 15.8f's <question> (Q-157J; the five 2026-11-25 replies; Q-158R2, Q-158OR, Q-158PAL, Q-158EL; Q-158R6G,
Q-158KW, Q-158DFX, Q-158AEI, Q-158AEIM with their tracked-file checks) are re-gated exactly as there.
Q-158AEIW: question and options as in 15.8f's <question>. File `W3f-carter-15-8-Q-158AEIW-reply-<YYYY-MM-DD>.txt`,
written by the orchestrator; sha256 = the value stated in the 15.8g resume message (the executor copies it into
gate_158.sh and the LOG; a missing value or a mismatch is STOP). Proceed only on label `Approve as written`.
</question>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-PLAN.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-review-suite-and-close-SUMMARY.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-review-suite-and-close-PLAN.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-7-AMENDMENT-REVIEW-as-received.md
@data/r4/tmp/w3f/q157/disposition_15_7j.md

**Standing rules:** 15.8 shared protocol; memory feedback_internal_validation_cannot_catch_misspecified_premise (the
review is brief-blind and is not skipped) and reference_codex_cli_for_gsd_review. `$Q8` = data/r4/tmp/w3f/q158.

**Review invocation (as 15.7j; read the exact command, CLI path and model from disposition_15_7j.md run notes and the
15.7j LOG entry, and record them):** `cd src/python && $PY -m ta_r4.extract_paste_block --in
../../.planning/amendments/osf-amendment-r4-DRAFT.md --out ../../$Q8/review_input.md`; `$Q8/codex_prompt.md` = the W4a
instruction verbatim + the W4a wrapper lines (prefix and suffix byte-equal to 15.7j's `$Q/codex_prompt.md` around its
extract; assert) + the new extract, nothing else (no CONTEXT, LOG, SUMMARY, finding list or 15.7j review);
`codex exec --skip-git-repo-check --sandbox read-only -m <15.7j model> - < $Q8/codex_prompt.md` from the repo root. On CLI
failure: record, retry once with the model the account's cache lists; a second failure is STOP (not skipped).

**Forbidden:** any src edit (a finding needing code is OPEN for Carter); any fit; any wording of the (c) sentence other
than Carter's approved text; W4a PLAN edits beyond depends_on; removing any HANDOFF string.
</context>

<new_tests>
tests/ta_r4/test_asthma_eur_eaf_disclosure.py gains 1 junit id (no parametrize); 15.8f's tests A and B are not changed.
- C. `test_draft_asthma_eaf_sentence_matches_the_manifests` (quick): the DRAFT, hard wraps joined with single spaces,
  contains `As a diagnostic, not a filter: in asthma EUR` exactly once; the sentence's numbers, parsed by the template
  15.8f Task 2 step 6 filled (the a ≥ 1 or the a == 0 form, both group clauses), equal: n = per-row row count;
  m_f / m_u = the aggregate asthma EUR flipped / unflipped medians rounded to 3 decimals; k = rows with
  abs_delta_eaf > 0.2; j = indels among them; a / a_f / a_u38, a_hi / a_lo (matching-row denominators), c_hi / c_lo,
  g_u37 (or x_hi / x_lo / x_u37) from the per-row manifest, and the u_-prefixed counts (u_n, u_k, u_a, u_a_f, u_a_u38,
  u_a_hi, u_a_lo, u_c_hi, u_c_lo, u_g_u37 or u_x_*) from the control manifest, by the definitions there; every printed
  numerator ≤ its printed denominator; GRCh38- and GRCh37-undetermined counts parsed separately; `no frequency filter`
  present.
Expected FULL: full_15_8f.xml (expected 2,768) + 1 = 2,769 = 2,716 P / 53 S / 0 F.
</new_tests>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: gate Q-158AEIW (sha256 from the orchestrator); DEC; insert the approved (c) sentence; test C with NCs</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-15-8-Q-158AEIW-reply-<date>.txt, .planning/DECISIONS.md, .planning/amendments/osf-amendment-r4-DRAFT.md, tests/ta_r4/test_asthma_eur_eaf_disclosure.py</files>
  <read_first>
    - ta-r4-W3f-multikey-fatal-and-chronology-PLAN.md (R7 insertion: sha256 of the approved text before and after)
    - 15.8f SUMMARY and LOG entry (sentence sha256, cross-tab, column definitions)
  </read_first>
  <behavior>
    - test C RED before insertion (anchor count 0), GREEN after; fails on NC (iv) and NC (v)
  </behavior>
  <action>
    1. `git rev-parse HEAD > $Q8/start_15_8g.txt`; re-run every gate of 15.8f Task 1 step 1 (gate_157j.sh; gate_158.sh
       with all 2026-11-25 and 2026-11-26 QIDs; tracked-file checks; gate_158r2.sh; gate_158a2.sh).
    2. Q-158AEIW: the resume message's sha256 == `sha256sum` of the reply file, else STOP. Line 2 ==
       `Carter reply (verbatim, selected option): Approve as written`, else STOP (Hold: nothing inserted; Reword / Leave
       out: STOP for a new approval round). The file has exactly 2 lines (line 2 the reply line); line 1 contains
       the text of `$Q8/aeiw_sentence_15_8f.txt` (`grep -cF` == 1) and `Tables:` with the crosstab and rows paths, whose
       stated sha256 values equal `sha256sum` of those files now and `$Q8/aeiw_tables_15_8f.sha256` (else STOP); that
       sentence file's sha256 == `$Q8/aeiw_sentence_15_8f.sha256` == the value in the 15.8f SUMMARY. Add Q-158AEIW to
       gate_158.sh (pinned sha256, label, `sed`-copied question, `F[]` full name, NC hooks); `bash $Q8/gate_158.sh
       Q-158AEIW` rc 0; its three NCs exit 2. DECISIONS.md copied to `$Q8/DECISIONS.pre_15_8g.md`, then DEC `DEC-<date>-ta-r4-draft-c-asthma-eaf-wording` (Follows
       DEC-2026-11-26-ta-r4-asthma-eur-eaf-disclose-no-filter, not edited; quote by `cat`, `cmp`-equal; rest of
       DECISIONS.md byte-equal to `$Q8/DECISIONS.pre_15_8g.md`). Commit the reply file and DECISIONS.md, explicit paths.
    3. RED: append test C; run → `$Q8/red_15_8g.txt` (fails: anchor absent).
    4. DRAFT (c), one script: after the orientation-step sentence (quote it in the LOG; old string asserted unique),
       insert the text of `$Q8/aeiw_sentence_15_8f.txt`, wrapped as the paragraph is; the inserted text unwrapped has
       sha256 == `$Q8/aeiw_sentence_15_8f.sha256`, asserted before and after. Test C, test_amendment_text.py and
       test_prelock_pilot_fits.py green, and tests A, B, C green in one dedicated sbatch run (cascadelake; junit
       `$Q8/green_abc_15_8g_<jobid>.xml`; job id in the LOG). NCs on the DRAFT in place (sha256 before, restored from
       `$Q8/nc_bak/`, sha256 equal after; `$Q8/nc_15_8g.txt`): (iv) `19 of 225` → `18 of 225` → C fails; (v) the whole
       sentence removed → C fails (exactly once). Commit `docs(ta-r4-W3f): DRAFT (c) asthma EUR EAF diagnostic,
       measured, in Carter's approved wording (Q-158AEI/AEIM/AEIW) (15.8g)`, explicit paths: DRAFT and test file.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && bash data/r4/tmp/w3f/q158/gate_157j.sh && bash data/r4/tmp/w3f/q158/gate_158.sh Q-158R6G Q-158KW Q-158DFX Q-158AEI Q-158AEIM Q-158AEIW && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_asthma_eur_eaf_disclosure.py tests/ta_r4/test_amendment_text.py -q -p no:cacheprovider -k "not rederive" && test -z "$(git diff --name-only $(cat data/r4/tmp/w3f/q158/start_15_8g.txt) HEAD -- src)"</automated>
  </verify>
  <done>Q-158AEIW gated against the orchestrator's sha256 and recorded; the (c) sentence is byte-for-byte (unwrapped) the approved one; test C green in its own sbatch run with NCs (iv) and (v) failing; no src change.</done>
</task>

<task type="auto">
  <name>Task 2: DRAFT (m) + Pre-Paste; text-vs-code table; brief-blind review; bank; dispositions (DRAFT text and the review file only)</name>
  <files>.planning/amendments/osf-amendment-r4-DRAFT.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-AMENDMENT-REVIEW-as-received.md</files>
  <read_first>
    - the ten 15.8a–f SUMMARYs (commits, DRAFT sentences, Carter replies)
    - the 15.7j review file (header, verbatim block and disposition format)
  </read_first>
  <action>
    1. DRAFT (one script; old strings asserted unique): (m) adds the 15.8 code commits per must_haves (the 15.8f module
       commit labelled "asthma EUR EAF diagnostic (15.8f)"); Pre-Paste: one RESOLVED row each for R2–R7 and Q-F3N (the
       Pre-Paste has no 15.7j OPEN rows for them). test_amendment_text.py + test_prelock_pilot_fits.py + test C green.
    2. Text-vs-code table in the LOG (R2–R7, Q-F3N, matched rounding, and the (c) EAF sentence → orientation_eaf.py
       file:line → the per-row manifest); and the 15.8e flag: src/snakemake/scripts/ta_r4/cs_cross_purity.R:13's header line no longer
       lists REFUSED_MULTI_KEY among the errors — a header-comment fix is code, so it is OPEN for Carter unless the DRAFT
       is what is wrong).
    3. Review per <context>; save prompt, sha256, stdout, stderr, rc, start time and HEAD under `$Q8/codex_*`.
    4. Bank: 3-line header (date + reviewed HEAD, command, prompt sha256), output verbatim with sha256 and byte count
       (assert equal to raw stdout), then the disposition table (finding → verified at HEAD with file:line →
       CONFIRMED / PARTLY / REFUTED → "DRAFT fixed" / "rejected with evidence" / "OPEN for Carter (needs code)" /
       "OPEN for Carter (approved wording)"); findings == rows, reconciled arithmetically.
    5. Apply DRAFT-text fixes only (never inside the approved (c) sentence); test_amendment_text.py green with its
       negative control (a banned word inserted in (a) fails the framing test; restore; sha256 equal); test C green;
       the (c) sentence's unwrapped sha256 still == `$Q8/aeiw_sentence_15_8f.sha256`. Commit `docs(ta-r4-W3f): 15.8
       DRAFT (m)/Pre-Paste; brief-blind re-review banked; dispositions (15.8g)`, explicit paths.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/ta_r4/test_amendment_text.py tests/ta_r4/test_prelock_pilot_fits.py tests/ta_r4/test_asthma_eur_eaf_disclosure.py -q -p no:cacheprovider -k "not rederive" && test "$(cat data/r4/tmp/w3f/q158/codex_rc.txt)" = 0 && test -s .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-AMENDMENT-REVIEW-as-received.md</automated>
  </verify>
  <done>(m)/Pre-Paste updated; review banked byte-for-byte; every finding verified and dispositioned; the approved sentence untouched.</done>
</task>

<task type="auto">
  <name>Task 3: FULL under Slurm; cumulative per-id reconciliation vs full_15_7j.xml over the ten 15.8a–f SUMMARYs, and vs full_15_8f.xml</name>
  <files>(scratch only: $Q8/full_15_8g.xml, $Q8/check_15_8g.py, $Q8/reconcile_15_8g.txt)</files>
  <action>
    1. `$Q8/close.sh 15_8g` under sbatch (protocol, `--constraint=cascadelake`, `--mem=64G` or more; 15.8e's FULL used
       the full 64G).
    2. `$Q8/check_15_8g.py` (from check_15_8f.py): (a) vs full_15_7j.xml with NEW = union of the `## New test ids`
       sections and declared = union of the `## Declared spec updates` sections of the ten 15.8a–f SUMMARYs (15.8a,
       15.8a2, 15.8a3, 15.8a4, 15.8b, 15.8c, 15.8c2, 15.8d, 15.8e, 15.8f), parsed (junit ids one per line; a SUMMARY
       missing a section or a malformed line is STOP; nothing typed), plus this plan's 1 id; renames as declared; expect
       = base totals read from full_15_7j.xml + Σ N_new. (b) vs full_15_8f.xml: removed 0, added == test C (passed),
       every other id identical. Arithmetic line in `$Q8/reconcile_15_8g.txt`. Any miss → STOP; no clean-close records.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 data/r4/tmp/w3f/q158/check_15_8g.py</automated>
  </verify>
  <done>FULL 2,769 reconciled cumulatively and against 15.8f; arithmetic recorded.</done>
</task>

<task type="auto">
  <name>Task 4: Records — HANDOFF w4a_checkpoint, STATE, LOG, PLAN-INDEX, W4a depends_on (frontmatter only), SUMMARY; commit (no push)</name>
  <files>.planning/HANDOFF.json, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-insert-review-and-close-SUMMARY.md</files>
  <action>
    1. HANDOFF (one script, `data/r4/tmp/w3f/handoff_edit.py` pattern): per must_haves; `w4a_checkpoint.read_first`
       gains the new review file; `suite_baselines_ta_r4_latest` = full_15_8g.xml counts. Assert key count after ==
       before + added keys and every pre-existing string value still present.
    2. W4a PLAN: frontmatter `depends_on: ["ta-r4-W3f-15-8-insert-review-and-close"]`; paste the one-line `git diff` in the LOG.
    3. PLAN-INDEX: 15.8g row COMPLETE with the review counts; the 15.8 paragraph's last sentence says W4a now depends on
       15.8g. STATE ★ RESUME HERE — LATEST ★ (NEXT = W4a-T3 lock presentation, or new OPEN items first; NOT PUSHED);
       prior block SUPERSEDED. LOG entry. SUMMARY with `## Declared spec updates`: none, and `## New test ids`: test C,
       junit form.
    4. PINS (`pytest tests/m3/test_source_freeze_pins.py`) and `git status --porcelain` on files_modified; `git fsck
       --connectivity-only` before and after; commit `docs(ta-r4-W3f): 15.8 close — review banked, FULL reconciled,
       HANDOFF refreshed, W4a depends_on (no push)`, explicit paths. No push.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && head -8 .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W4a-amendment-draft-review-locks-PLAN.md | grep -qF 'depends_on: ["ta-r4-W3f-15-8-insert-review-and-close"]' && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -c "import json,yaml;h=json.load(open('.planning/HANDOFF.json'));b=h['w4a_checkpoint']['production_blockers'];K=['W3f157_R2','W3f157_R3','W3f157_R4','W3f157_R5','W3f157_R6','W3f157_R7','W3f157_QF3N_premise'];assert all(k in b and k+'_PRE_2026_11_24' in b and b[k].startswith('RESOLVED') for k in K), [k for k in K if k not in b or k+'_PRE_2026_11_24' not in b];d=yaml.safe_load(open('config/ta_r4/decision_rules.yaml'));assert d['locked'] is False" && test -z "$(git status --porcelain -- .planning/HANDOFF.json .planning/STATE.md)"</automated>
  </verify>
  <done>Records committed with explicit paths; W4a depends on 15.8g; nothing pushed.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries
| Boundary | Description |
|----------|-------------|
| internal records → public text | only a brief-blind reviewer reading code can catch a mis-specified claim |
| Carter's approval → DRAFT | the approval binds one exact sentence (sha256), presented in 15.8f |

## STRIDE Threat Register
| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-158g-01 | Repudiation | review provenance | mitigate | prompt and output sha256; banked block byte-equal to raw stdout; wrapper byte-equal to 15.7j's |
| T-r4-158g-02 | Tampering | silent test loss across 15.8 | mitigate | cumulative per-id reconciliation vs full_15_7j.xml from ten parsed SUMMARYs |
| T-r4-158g-03 | Tampering | HANDOFF history | mitigate | old text under _PRE keys; string-preservation assert |
| T-r4-158g-04 | Spoofing | AEIW reply | mitigate | sha256 stated by the orchestrator, pinned and gated; question line contains the exact sentence; executor never writes it |
| T-r4-158g-05 | Tampering | (c) sentence | mitigate | inserted text sha256 == approved sentence before and after; test C + NCs (iv), (v) |
| T-r4-158g-06 | Information disclosure | push / OSF | accept | none in 15.8 |
</threat_model>

<verification>
- AEIW gated against the orchestrator's sha256; sentence inserted byte-for-byte; test C green with its NCs; review
  banked; check_15_8g.py passes; HANDOFF and W4a depends_on asserts pass; decision_rules.yaml locked false; n_regions_min 7.
</verification>

<success_criteria>
- 15.8 closes with R2–R7 resolved or carried as Carter-dispositioned items, the asthma EUR EAF diagnostic disclosed in
  measured numbers in Carter's approved wording, a fresh brief-blind review, and W4a-T3 next.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-15-8-insert-review-and-close-SUMMARY.md`
</output>
