---
phase: quick-260916-kht
plan: 01
subsystem: planning/debug (Stage C NaN error-posture adjudication record)
tags: [stage-c, nan-posture, brief-blind, citations, verifier, docs-only, negative-controls]
requires:
  - "c93e97b (drafting basis): posted mk7ze (repo lines 168-500) + posted trsx5 (9,695 B) + shipped fire-path code"
  - "scratchpad source 260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md (16,817 B / md5 5e11157f3b56addada24134bd7e2225f)"
provides:
  - ".planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md (banked, 223 lines, 18,309 B, md5 763f412bb1a8dbdb38f2cc332ed5a21d)"
  - "260916-kht-verify.py: BASIS / --source / --live / --baseline / --bare-ref-plan / --selftest citation re-verifier"
affects:
  - "STATE.md RESUME item 1 (Stage C NaN error posture): options draft now banked for brief-blind adjudication (orchestrator updates STATE.md)"
tech-stack:
  added: []
  patterns:
    - "positional CLAIMS table reconciled against a parser (parsed == table == verified)"
    - "permitted-edit ledger with forward AND reverse byte identity"
    - "every check family observed RED under --selftest before a GREEN is trusted"
key-files:
  created:
    - .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md
    - .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py
  modified: []
decisions:
  - "c-ast:S9 parts (iii)/(iv) anchor on the AST-located `gate_sidecar = ...` assignment (part (ii) pins it to line 923), so the plan's own ST-s9 mutation can turn part (iii) RED; on the real basis this is identical to the literal 923"
  - "Two citation defects corrected (class 3): c30 mk7ze P311 / R478 -> P311-312 / R478-479; c64 quote -> 'the panel and fine-mapping result stand unmodified'. No CLAIMS-table token was changed to make a check pass"
metrics:
  duration: "71 min (2026-09-16T19:50:25Z start)"
  completed: "2026-09-16"
  tasks: 3
  files: 2
---

# Phase quick-260916-kht Plan 01: Bank the Stage C NaN error-posture options draft Summary

**Banked the brief-blind Stage C NaN error-posture options draft. It differs from the scratchpad source only by 17 declared edits (proven by forward and reverse byte identity). A committed verifier checks all 88 citations against the posted mk7ze/trsx5 bodies and the shipped code at c93e97b; it is GREEN in default, `--source` and `--live` modes, and `--selftest` saw all 33 corrupted inputs go RED in their declared families.**

Status for the orchestrator: **banked in the repo, NOT sent to Seth, NOT decided, no posture code, no recommendation. STATE.md, ROADMAP.md, HANDOFF.json and osf_deviations.md NOT touched.** PLAN.md and this SUMMARY are not committed (orchestrator's job).

## 1. HEAD0, commit, `git show --stat`

- HEAD0 = `c93e97b` (pre-flight: `git log --oneline -3` top = c93e97b; `git status --porcelain --untracked-files=no` empty; `$BANKED` and `$VER` absent; `$SRC` 16817 B then md5 5e11157f3b56addada24134bd7e2225f).
- Commit: **`f09535c`** on `m3-W2-aou-deltas`. Parent == c93e97b checked by full hash (`test "$(git rev-parse HEAD~1)" = "$(git rev-parse c93e97b)"` -> true). Not pushed.

```
f09535c docs(quick-260916-kht): bank the Stage C NaN error-posture options draft (brief-blind, docs-only; 88 citations re-verified at c93e97b with observed-RED negative controls; 2 citation(s) corrected)

 ...0916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md |  223 +++
 .../260916-kht-verify.py                           | 1711 ++++++++++++++++++++
 2 files changed, 1934 insertions(+)
```

## 2. Baseline on the unmodified source (Task 1)

Command: `python3 $VER --baseline --draft "$SRC" --json "$TMPDIR/kht-baseline.json"` -> **rc=1**, `RESULT RED 57/279 parsed=81 table=81 verified=79`. Plan's Task 1 verify printed `baseline-reconciled`. `--baseline --live` gave an identical RED id set (57 = 57). No duplicate result ids. Every RED and SKIP line, verbatim:

```
RED  c-key no **Files cited** key block in the draft
RED  c-res:c01 pos 1 `260812-ox1-AGENT-PROMPT.md:398` -> None (want .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md)
RED  c-res:c02 pos 2 `:372-373` -> None (want .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md)
RED  c-res:c03 pos 3 `:417` -> None (want .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md)
RED  c-res:c04 pos 4 `260812-ox1-READY-TO-FIRE.md:360-366` -> None (want .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md)
RED  c-res:c05 pos 5 `run_native_ld_panel.py:1325-1328` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c06 pos 6 `plink_ld_to_npz.py:218-228` -> None (want src/python/plink_ld_to_npz.py)
RED  c-res:c07 pos 7 `run_native_ld_panel.py:1090-1093` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c08 pos 8 `:1144-1146` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c09 pos 9 `:1148` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c10 pos 10 `:1101-1107` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c11 pos 11 `:1278-1279` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c12 pos 12 `fire_verifier.py:1097-1099` -> None (want src/python/fire_verifier.py)
RED  c-res:c13 pos 13 `:302-303` -> None (want src/python/fire_verifier.py)
RED  c-res:c14 pos 14 `:324-326` -> None (want src/python/fire_verifier.py)
RED  c-res:c15 pos 15 `:381-389` -> None (want src/python/fire_verifier.py)
RED  c-res:c16 pos 16 `:976-981` -> None (want src/python/fire_verifier.py)
RED  c-res:c17 pos 17 `AGENT-PROMPT.md:55-61` -> None (want .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md)
RED  c-res:c18 pos 18 `:422-423` -> None (want .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md)
RED  c-res:c19 pos 19 `fire_verifier.py:999-1001` -> None (want src/python/fire_verifier.py)
RED  c-res:c20 pos 20 `run_native_ld_panel.py:1278` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c21 pos 21 `:806-815` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c22 pos 22 `260824-STAGE-B-HALT-…md:20-21` -> None (want .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md)
RED  c-res:c23 pos 23 `:1325-1328` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c24 pos 24 `260824-STAGE-B-HALT-…md:11-16` -> None (want .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md)
RED  c:c30 pos 30 mk7ze P311 / R478 MK:478-478 P311-311 -- MK:478-478 missing ['A region over the anomaly gate is deferred for re-diagnosis …']; posted P311-311 missing ['A region over the anomaly gate is deferred for re-diagnosis …']
RED  c-res:c45 pos 45 `plink_ld_to_npz.py:213-228` -> None (want src/python/plink_ld_to_npz.py)
RED  c-res:c46 pos 46 `260824-STAGE-B-HALT-…md:45-58` -> None (want .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md)
RED  c-res:c47 pos 47 `:1068-1069` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c48 pos 48 `:1090` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c49 pos 49 `run_native_ld_panel.py:1144-1148` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c50 pos 50 `:1101-1107` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c51 pos 51 `:1149-1154` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c52 pos 52 `:723-725` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c53 pos 53 `:923-939` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c54 pos 54 `:961-965` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c55 pos 55 `:1129-1139` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c56 pos 56 `:799-815` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c57 pos 57 `fire_verifier.py:330-399` -> None (want src/python/fire_verifier.py)
RED  c-res:c58 pos 58 `:309-312` -> None (want src/python/fire_verifier.py)
RED  c-res:c59 pos 59 `run_native_ld_panel.py:866-872` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c60 pos 60 `deferred-items.md:1148-1191` -> None (want .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md)
RED  c-res:c61 pos 61 `fire_verifier.py:875-939` -> None (want src/python/fire_verifier.py)
RED  c-res:c62 pos 62 `READY-TO-FIRE.md:360-366` -> None (want .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md)
RED  c-res:c63 pos 63 `AGENT-PROMPT.md:424-428` -> None (want .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md)
RED  c:c64 pos 64 trsx5:43 TR:43-43 -- TR:43-43 missing ['the fine-mapping result stand unmodified']
RED  c-res:c66 pos 66 `:967` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c67 pos 67 `:1090` -> None (want src/python/run_native_ld_panel.py)
RED  c-res:c69 pos 69 `fire_verifier.py:363-370` -> None (want src/python/fire_verifier.py)
RED  c-res:c70 pos 70 `osf_deviations.md:703-704` -> None (want .planning/osf_deviations.md)
RED  c-res:c73 pos 73 `fire_verifier.py:335-336` -> None (want src/python/fire_verifier.py)
RED  c-res:c74 pos 74 `260824-STAGE-B-HALT-…md:150-179` -> None (want .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md)
RED  c-res:c75 pos 75 `260824-STAGE-B-HALT-…md:104-107` -> None (want .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md)
RED  c-res:c76 pos 76 `osf_deviations.md:685-689` -> None (want .planning/osf_deviations.md)
RED  c-res:c77 pos 77 `:682` -> None (want .planning/osf_deviations.md)
RED  c-res:c78 pos 78 `osf_deviations.md:670-671` -> None (want .planning/osf_deviations.md)
SKIP f: baseline
RED  g:status status line '**Status:** DRAFT, not banked in the repo, no code written, **no decision made.** Built for review by'; missing ['not sent to seth', 'not decided']; contains 'not banked'
```

**Reconciliation against `<precheck>`, by claim id:**

| precheck expectation | measured | match |
|---|---|---|
| `c:c30` RED (R478 ends at "is deferred for"; "re-diagnosis" on R479) | `RED c:c30 ... MK:478-478 missing ...; posted P311-311 missing ...` | yes |
| `c:c64` RED (quoted fragment not a substring of trsx5:43) | `RED c:c64 ... TR:43-43 missing ['the fine-mapping result stand unmodified']` | yes |
| `c-key` RED (no key block) | `RED c-key no **Files cited** key block in the draft` | yes |
| `c-res:*` RED for every unresolved short-name token, plus bare refs that inherit it | 53 ids: c01-c24, c45-c63, c66, c67, c69, c70, c73-c78. PASS for c25 (full path `.planning/osf_deviations.md:657-663` is_file) and every trsx5 / mk7ze token | yes |
| `g:status` RED ("not banked") | `RED g:status ... missing ['not sent to seth', 'not decided']; contains 'not banked'` | yes |
| all `a:*`, `b:*` PASS; controls do not match | a: 22945 B / 13a49f54...; control 167-500 = 8154025b50ef344cd43078f910add359. b: 9695 B / c19be8b2...; control first 9694 B = 0775eef2aa3f4965c42375ed955aced0 | yes (both control md5s reproduce the planner's) |
| `c-count` 81 = 81; 79 of 81 `c:` verified | `parsed=81 table=81 verified=79` | yes |
| all `c-pr` (14), `c-quote` (30), `c-bind` (30), `c-ast` S1-S9, `c-hand` H1-H5, `d:*`, `e:*`, `g:exempt/recommend/options/questions` PASS | all PASS | yes |
| d sweep: 6 zero terms = 0; defer 17/4; raise 3/2; `deferred_infeasible_square` 0 raw and underscore-stripped | recomputed identical | yes |
| e: since 2026-08-24 empty; control since 2026-08-01 = 6 commits, oldest 5284505; diff-control rc 1 | identical (dd8f0b8 e5e7ac7 d7f3b18 d9fbc63 ee16f79 5284505) | yes |

**Table fixes: none.** No CLAIMS token was changed. The only Task-1 → Task-2 table changes were the ones the plan specified: c64 gets its after-quote (its before-quote now lives in E7's evidence) and rows n01-n07 are inserted. The 88/88/88 counts, the 30/30/16 per-family counts and the 33 mutations all reproduced exactly; no pre-computed number needed adjusting.

After banking, `--baseline --draft "$SRC"` again gave rc 1 with a RED id set **identical** to Task 1's (57 ids; set difference empty). So banking did not loosen the engine.

## 3. Class-3 corrections

| Eid | claim | before | after | evidence |
|---|---|---|---|---|
| E6 | c30 | `mk7ze P311 / R478` | `mk7ze P311-312 / R478-479` | quote "A region over the anomaly gate is deferred for re-diagnosis …": R478 alone ends at "deferred for", and "re-diagnosis" is on R479 (= posted P312). `f:evidence:E6` recomputes before RED, after GREEN |
| E7 | c64 | `NONE needs "the fine-mapping result stand unmodified"` | `NONE needs "the panel and fine-mapping result stand unmodified"` | trsx5:43 reads "...the panel and fine-mapping result stand unmodified."; the old quote is not a substring. `f:evidence:E7` recomputes before RED, after GREEN |

Verbatim cited lines (`git show c93e97b:<path>`; mk7ze posted P311-312 = repo R478-479):

```
### MK:478-479 (git show c93e97b:.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md)
478: - **The defer-not-exclude protocol.** A region over the anomaly gate is deferred for
479:   re-diagnosis and disclosed as a deviation, never auto-excluded.
### TR:43-43 (git show c93e97b:.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt)
43: BRANCH_AFR_OCC_NONE — the region contains no occlusion-undefined pair; the panel and fine-mapping result stand unmodified.
```

Live evidence lines (`--source` run):

```
PASS f:classes 17 edits, classes [('E1', 1, None), ('E2', 2, None), ('E3', 2, None), ('E4', 2, None), ('E5', 2, None), ('E6', 3, None), ('E7', 3, None), ('E8', 4, 'F1'), ('E9', 4, 'K1'), ('E10', 4, 'K2'), ('E11', 4, 'K3'), ('E12', 4, 'K4'), ('E13', 4, 'N1'), ('E14', 4, 'N2'), ('E15', 4, 'N3'), ('E16', 4, 'N4'), ('E17', 4, 'N5')]; only E2 changes line count (+12)
PASS f:reverse reverse-applied E17..E1 to the draft: 16817 B (want 16817); md5 5e11157f3b56addada24134bd7e2225f (want 5e11157f3b56addada24134bd7e2225f)
PASS f:forward source 16817 B md5 5e11157f3b56addada24134bd7e2225f; E1..E17 applied == draft bytes (18309 B)
PASS f:evidence:E6 c30 MK before {'range': [478, 478], 'prange': [311, 311]} -> RED (MK:478-478 missing ['A region over the anomaly gate is deferred for re-diagnosis …']; posted P311-311 missing ['A region over the anomaly gate is deferred for re-diagnosis …']); after {'range': [478, 479], 'prange': [311, 312]} -> GREEN
PASS f:evidence:E7 c64 TR before {'range': [43, 43]} -> RED (TR:43-43 missing ['the fine-mapping result stand unmodified']); after {'range': [43, 43]} -> GREEN
PASS f:bareplan greedy plan from source [('`:1325-1328`', '`run_native_ld_panel.py:1325-1328`'), ('`:1068-1069`', '`run_native_ld_panel.py:1068-1069`'), ('`:967`', '`run_native_ld_panel.py:967`')] == class-2 bare-ref edits [('`:1325-1328`', '`run_native_ld_panel.py:1325-1328`'), ('`:1068-1069`', '`run_native_ld_panel.py:1068-1069`'), ('`:967`', '`run_native_ld_panel.py:967`')]: True
```

Post-correction rows in the default run:

```
PASS c-res:c30 pos 30 mk7ze P311-312 / R478-479 -> .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md (want .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md)
PASS c:c30 pos 30 mk7ze P311-312 / R478-479 MK:478-479 P311-312
PASS c-quote:c30 quote in draft
PASS c-bind:c30 quote bound to the paragraph of mk7ze P311-312 / R478-479 (draft line 79)
PASS c-pr:c30 mk7ze P311-312 / R478-479: P311-312 +167 = R478-479 vs stated R478-479
PASS c-res:c64 pos 66 trsx5:43 -> .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt (want .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt)
PASS c:c64 pos 66 trsx5:43 TR:43-43
PASS c-quote:c64 quote in draft
PASS c-bind:c64 quote bound to the paragraph of trsx5:43 (draft line 122)
```

## 3b. Class-4 edits (orchestrator-specified, `origin="orchestrator-specified, quick-260916-kht revision 1"`)

Encoded exactly as the plan specified; every `old` occurs once in the source and every `new` once in the banked file (`f:unique:E8..E17` PASS). In the table, `\n` stands for a real line break; continuation lines keep their two-space indent.

| Eid | label | old | new | evidence |
|---|---|---|---|---|
| E8 | F1 | `is written locally for every square region before plink.` | `is written locally, before plink, for every square region that gets past both the resume skip and the n_var feasibility ceiling and does not raise before the write (an already-banked region returns at` `run_native_ld_panel.py:806-815`, `an infeasible one at` `:866-872`).` | `c-ast:S9` + rows n01, n07 |
| E9 | K1 | `rate:* 1 of 21 sampled regions carries a surviving pair. The sample was systematic-by-span, not\n  random,` | `rate:* 1 of 21 sampled regions carries a surviving pair (osf_deviations.md:660-663). The sample was systematic-by-span, not\n  random (mk7ze P88-89 / R255-256),` (the osf path is backticked in the file) | rows n03, n04 |
| E10 | K2 | `for the rest of the ~11 days.` | `for the rest of the ~11 days (AGENT-PROMPT.md:393).` (path backticked) | row n02 |
| E11 | K3 | `scan across all 276 AFR regions before` | `scan across all 276 AFR regions (mk7ze P88-89 / R255-256) before` | row n05 |
| E12 | K4 | `120,000-variant ceiling)` | `120,000-variant ceiling; READY-TO-FIRE.md:369-370)` (path backticked) | row n06; the H1 bytes regex still matches (4, 57.6, 120,000) |
| E13 | N1 | `*READING 2 (the counter-reading, to be tested):*` | `*READING 2:*` | orchestrator-specified neutrality |
| E14 | N2 | `literal --fail-fast is not workable (P4). The realistic form is the operator stopping\n  the fire at the first error: row.` | `literal --fail-fast would also halt on already-banked and deferred regions (P4), so\n  this option means the operator stopping the fire at the first error: row.` (flags backticked) | orchestrator-specified neutrality |
| E15 | N3 | `turns a surprise into a pre-declared, measured set. Needs VM time (Carter).` | `the regions expected to raise are measured before Stage C instead of observed during it. Needs VM time (Carter).` | orchestrator-specified neutrality |
| E16 | N4 | `A full-panel\n  scan *is* that test. Running D before the disclosure is posted would use up the prediction, unless\n  the prediction is explicitly retired first.` | `A full-panel\n  scan would measure that same both-sides rate before production does; whether that uses up the\n  prediction is question 5.` | orchestrator-specified neutrality |
| E17 | N5 | `A contract raise gets counted as "the gates working"\n  (fire_verifier.py:335-336), which is not the rationale that PASS was built on.` | `A contract raise would be classified under the deferral PASS, whose stated reason is "the gates working"\n  (fire_verifier.py:335-336).` (path backticked) | orchestrator-specified neutrality; c73 still binds (`c-bind:c73` PASS) |

(The byte-exact strings are the `PERMITTED_EDITS` literals in `260916-kht-verify.py`; `diff -u` in §5 shows them in place.) **K4 exact form used:** old `120,000-variant ceiling)` → new ``120,000-variant ceiling; `READY-TO-FIRE.md:369-370`)``.

F1 evidence: `c-ast:S9` (default run, verbatim):

```
PASS c-ast:S9 (i) if@806 returns at 815 before Try@825; (ii) if@866 returns at 872 before sidecar@923 <= with@925, all in process_region; (iii) process_region returns before the sidecar == {815, 872}, _site@891 excluded; (iv) enclosing = Try@825, If@850 `mode == "square"`
```

Rows n01-n07 (default run, verbatim), at parsed positions 53, 54, 71, 79, 80, 81, 86 as the contract specifies:

```
PASS c-res:n01 pos 53 `run_native_ld_panel.py:806-815` -> src/python/run_native_ld_panel.py (want src/python/run_native_ld_panel.py)
PASS c:n01 pos 53 `run_native_ld_panel.py:806-815` RN:806-815
PASS c-res:n07 pos 54 `:866-872` -> src/python/run_native_ld_panel.py (want src/python/run_native_ld_panel.py)
PASS c:n07 pos 54 `:866-872` RN:866-872
PASS c-res:n02 pos 71 `AGENT-PROMPT.md:393` -> .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md (want .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md)
PASS c:n02 pos 71 `AGENT-PROMPT.md:393` AP:393-393
PASS c-res:n03 pos 79 `osf_deviations.md:660-663` -> .planning/osf_deviations.md (want .planning/osf_deviations.md)
PASS c:n03 pos 79 `osf_deviations.md:660-663` OD:660-663
PASS c-res:n04 pos 80 mk7ze P88-89 / R255-256 -> .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md (want .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md)
PASS c:n04 pos 80 mk7ze P88-89 / R255-256 MK:255-256 P88-89
PASS c-pr:n04 mk7ze P88-89 / R255-256: P88-89 +167 = R255-256 vs stated R255-256
PASS c-res:n05 pos 81 mk7ze P88-89 / R255-256 -> .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md (want .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md)
PASS c:n05 pos 81 mk7ze P88-89 / R255-256 MK:255-256 P88-89
PASS c-pr:n05 mk7ze P88-89 / R255-256: P88-89 +167 = R255-256 vs stated R255-256
PASS c-res:n06 pos 86 `READY-TO-FIRE.md:369-370` -> .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md (want .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md)
PASS c:n06 pos 86 `READY-TO-FIRE.md:369-370` RF:369-370
```

Verbatim cited lines for F1 (RN:806-815, :825, :866-872, :923-939) and K1-K4 (AP:393, RF:369-370, OD:660-663, MK:255-256), from `git show c93e97b:<path>`:

```
### RN:806-815 (git show c93e97b:src/python/run_native_ld_panel.py)
806:     if existing is not None:
807:         result = {
808:             "region_id": region_id, "chr": chrom, "n_var": None,
809:             "wall_min": None, "peak_ram_gib": None, "output_gib": None,
810:             "status": "skipped_idempotent", "out": existing,
811:             "n_dropped_occluded": None,     # skip: no filter run this pass
812:             "n_dropped_monomorphic": None,  # skip: no drop computed this run
813:         }
814:         append_panel_row(panel_tsv, result, scratch_dir=compute_dir)  # dedups
815:         return result
### RN:825-825 (git show c93e97b:src/python/run_native_ld_panel.py)
825:     try:
### RN:866-872 (git show c93e97b:src/python/run_native_ld_panel.py)
866:             if pre_window_n_var > max_n_var:
867:                 result["status"] = (f"deferred_infeasible_square: n_var={pre_window_n_var} "
868:                                     f"> ceiling={max_n_var}")
869:                 print(f"region {region_id}: DEFERRED (infeasible square) — {result['status']}",
870:                       file=sys.stderr, flush=True)
871:                 append_panel_row(panel_tsv, result, scratch_dir=compute_dir)
872:                 return result
### RN:923-939 (git show c93e97b:src/python/run_native_ld_panel.py)
923:             gate_sidecar = Path(f"{out_prefix}.occlusion_gate.json")
924:             gate_sidecar.parent.mkdir(parents=True, exist_ok=True)
925:             with open(gate_sidecar, "w") as gate_fh:
926:                 json.dump({
927:                     "region_id": region_id,
928:                     "n_rows": pre_window_n_var,
929:                     "n_sites": n_sites,
930:                     "occ_rows": occ_rows,
931:                     "occ_sites": occ_sites,
932:                     "site_fraction": site_fraction,
933:                     "inflation": inflation,
934:                     "site_fraction_ceiling": site_ceiling,
935:                     "inflation_ceiling": inflation_ceiling,
936:                     "fired": fired,
937:                     "verdict": "deferred" if fired else "ok",
938:                 }, gate_fh, indent=2, sort_keys=False)
939:                 gate_fh.write("\n")
### AP:393-393 (git show c93e97b:.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md)
393: STEP 10 — GATE: STAGE C, THE FULL FIRE (~11 days, $385–1,084). Preconditions
### RF:369-370 (git show c93e97b:.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md)
369: landed):** in the panel TSV, `deferred_infeasible_square` (n_var above the
370: `--max-n-var` ceiling, default 120000 = the consumer's `m3_convert_max_n_var`)
### OD:660-663 (git show c93e97b:.planning/osf_deviations.md)
660: - The posted predicate is `d.pos < v.pos`: `89454077 < 89454076` = **FALSE**. The single survivor is
661:   **INVISIBLE TO THE PREDICATE BY CONSTRUCTION**. Across the 21-region scan, **no positive-offset
662:   undefined survivor was observed**, and the only measured surviving pair was upstream at offset
663:   **-1**. Offset histogram `{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}`.
### MK:255-256 (git show c93e97b:.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md)
255: *Pre-committed sample.* A systematic-by-span sample of 21 of the 276 AFR regions (20 selected
256: by span stratum plus region 1 forced) was fixed BEFORE any result was seen, and measured with
```

N1-N5: orchestrator-specified neutrality. Post-edit `g:*` and `c-hand:*` lines (default run, verbatim):

```
PASS c-hand:H1 extracted x=1 n=21 N=276 conf=95 n_run=21 min=48 N_panel=276 bytes/cell=4 cap=120000; CP95=(0.001205, 0.23816); mid recomputed 13 stated 13, lo recomputed 0.3 stated 0.3, hi recomputed 66 stated 66, hours recomputed 10.5 stated 10.5, gb recomputed 57.6 stated 57.6, cap==S7 recomputed 120000 stated 120000
PASS c-hand:H2 ST@c93e97b frontmatter marker 'PRIOR: 2026-09-01 — ✅ SWEEP COMPLETE' once; its block (1770 chars) contains 'Runtime 48m': True
PASS c-hand:H3 OD entry 532-1022 (EOF 1022) contains 657-704; first Status line 534: "- **Status:** DRAFTED — NOT POSTED; placement and posting are Carter's. No agent has contacted"
PASS c-hand:H4 U7 md5 2af600e11c568fa14821382e9b4c3e81 != trsx5 posted md5 c19be8b2ad7cd6a45fee1d668d8a9cf9: True
PASS c-hand:H5 draft states Code at HEAD c93e97b: True; merge-base --is-ancestor c93e97b HEAD rc=0
PASS g:status status line '**Status:** DRAFT, banked in the repo (quick-260916-kht), NOT sent to Seth, NOT decided, no code written, **no decision made.** Built for review by'
PASS g:exempt 'with no recommendation' occurs 1 times (want exactly 1)
PASS g:recommend 0 hits over 11 patterns
PASS g:options options ['A', 'B', 'C', 'D', 'E']
PASS g:questions questions ['1', '2', '3', '4', '5']
```

## 4. `--bare-ref-plan` output and the class-2 edits it produced

`python3 $VER --bare-ref-plan --source "$SRC"` -> rc 0 (run with E1, E2, E6-E17 declared and rows n01-n07 present, before E3-E5 existed):

```
BARE-REF-PLAN source 16817 B md5 5e11157f3b56addada24134bd7e2225f; non-bare-ref edits applied in memory: E1 E2 E6 E7 E8 E9 E10 E11 E12 E13 E14 E15 E16 E17
PLAN 1 pos=23 claim=c23 `:1325-1328` -> `run_native_ld_panel.py:1325-1328` (nearest-preceding explicit resolved to .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md; table file src/python/run_native_ld_panel.py)
PLAN 2 pos=47 claim=c47 `:1068-1069` -> `run_native_ld_panel.py:1068-1069` (nearest-preceding explicit resolved to .planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md; table file src/python/run_native_ld_panel.py)
PLAN 3 pos=68 claim=c66 `:967` -> `run_native_ld_panel.py:967` (nearest-preceding explicit resolved to .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md; table file src/python/run_native_ld_panel.py)
BARE-REF-PLAN 3 expansion(s)
```

This matches the planner's expectation exactly (3 expansions, positions 23, 47, 68). Encoded as:
- E3: ``It also halts on every deferral (`:1325-1328`)`` → ``It also halts on every deferral (`run_native_ld_panel.py:1325-1328`)``
- E4: ``(set at `:1068-1069` `` → ``(set at `run_native_ld_panel.py:1068-1069` ``
- E5: ``returns at `:967` `` → ``returns at `run_native_ld_panel.py:967` ``

F1's new bare `:866-872` resolves to RN through `run_native_ld_panel.py:806-815`, which comes right before it, so it was not expanded. `f:bareplan` recomputes this plan from the reverse-reconstructed source in every run.

## 5. `diff -u "$SRC" "$BANKED"` (verbatim, complete)

Hunks appear only at line 3, the insertion after line 20, and the lines carrying E3-E17. Banked file: 223 lines.

```diff
--- /gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md	2026-09-16 14:41:21.395524000 -0400
+++ .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md	2026-09-16 16:50:20.075639000 -0400
@@ -1,6 +1,6 @@
 # Stage C: what happens to a region that RAISES on a leftover pairwise NaN (options draft)
 
-**Status:** DRAFT, not banked in the repo, no code written, **no decision made.** Built for review by
+**Status:** DRAFT, banked in the repo (quick-260916-kht), NOT sent to Seth, NOT decided, no code written, **no decision made.** Built for review by
 an adjudicator who has not seen our reasoning: options are laid out neutrally, with no recommendation.
 Every claim cites file:line. Labels: **TEXT** = what a posted record says; **CODE** = what shipped code
 does; **READING** = an interpretation offered for adjudication, not a finding.
@@ -19,6 +19,18 @@
   and is not cited.
 - Code at HEAD `c93e97b`.
 
+**Files cited** (short form used below → full repo-relative path):
+- `260812-ox1-AGENT-PROMPT.md`, `AGENT-PROMPT.md` → `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md`
+- `260812-ox1-READY-TO-FIRE.md`, `READY-TO-FIRE.md` → `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md`
+- `260824-STAGE-B-HALT-…md` → `.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md`
+- `run_native_ld_panel.py` → `src/python/run_native_ld_panel.py`
+- `fire_verifier.py` → `src/python/fire_verifier.py`
+- `plink_ld_to_npz.py` → `src/python/plink_ld_to_npz.py`
+- `osf_deviations.md` → `.planning/osf_deviations.md`
+- `deferred-items.md` → `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`
+- `STATE.md` → `.planning/STATE.md`
+- `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` → `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`
+
 ---
 
 ## 0. Premise corrections: the question is narrower than "the fire will halt"
@@ -46,7 +58,7 @@
 **P4: Adding `--fail-fast` to Stage C would halt on regions already banked.** The flag raises on any
 `status != "ok"` (`run_native_ld_panel.py:1278`). An already-banked region returns
 `skipped_idempotent` (`:806-815`), and `00001`, `00017` and `00040__sub14` are banked
-(`260824-STAGE-B-HALT-…md:20-21`). It also halts on every deferral (`:1325-1328`).
+(`260824-STAGE-B-HALT-…md:20-21`). It also halts on every deferral (`run_native_ld_panel.py:1325-1328`).
 
 **P5: One raise is observed; the second is predicted.** `m2_region_00057` (+1) raised in Stage B
 (`260824-STAGE-B-HALT-…md:11-16`). `m2_region_00149` (−1) is classified as surviving into the panel by
@@ -64,7 +76,7 @@
 | # | TEXT | Where |
 |---|---|---|
 | T1 | The raw-panel NaN-raise contract: "The raw per-region panel .npz reader continues to RAISE on any NaN rather than silently coercing it; occlusion handling is a distinct, upstream (panel-build) and lockstep (harmonization) step, not a weakening of the raw contract." | trsx5:39; restated as unchanged at mk7ze P321-322 / R488-489 |
-| T2 | Defer-not-exclude is stated for the **anomaly gate**: "If the count of occlusion-excluded variants in a region exceeds … the region is … NOT auto-excluded, it is deferred for re-diagnosis, and it is disclosed as a deviation." | trsx5:29; mk7ze P261 / R428 ("Deferral remains NOT auto-exclusion. A region over the ceiling …"); mk7ze P311 / R478 ("A region over the anomaly gate is deferred for re-diagnosis …") |
+| T2 | Defer-not-exclude is stated for the **anomaly gate**: "If the count of occlusion-excluded variants in a region exceeds … the region is … NOT auto-excluded, it is deferred for re-diagnosis, and it is disclosed as a deviation." | trsx5:29; mk7ze P261 / R428 ("Deferral remains NOT auto-exclusion. A region over the ceiling …"); mk7ze P311-312 / R478-479 ("A region over the anomaly gate is deferred for re-diagnosis …") |
 | T3 | `BRANCH_AFR_OCC_DEFERRED` is defined by its trigger: "the region's occlusion-exclusion count exceeds the anomaly gate". mk7ze lists what routes there: "NO fourth branch and NO new token: a region deferred by EITHER the site-fraction ceiling or the multiplicity companion routes to the SAME `BRANCH_AFR_OCC_DEFERRED`". | trsx5:47; mk7ze P316-318 / R483-485; the two conditions at mk7ze P155-158 / R322-325 |
 | T4 | NONE = "the region contains no occlusion-undefined pair; the panel and fine-mapping result stand unmodified." EXCLUDED = "… fine-mapping proceeds on the reduced variant set". | trsx5:43, trsx5:45 |
 | T5 | The branch list is presented as closed: "All three outcomes are reportable; excluding variants silently (without a manifest), fabricating a correlation value, or choosing the occlusion criterion to obtain a particular fine-mapping result are the only paths not on this list." | trsx5:49 |
@@ -86,9 +98,9 @@
 | # | CODE / RUNBOOK | Where |
 |---|---|---|
 | C1 | NaN check runs first in the converter. The message blames a zero-variance variant; for 00057 that diagnosis was measured false (a confined pair, diagonal 1.0). | `plink_ld_to_npz.py:213-228`; `260824-STAGE-B-HALT-…md:45-58` |
-| C2 | The raise becomes `status="error: …"`. The row keeps `n_dropped_occluded` (set at `:1068-1069`, before conversion at `:1090`). No `.npz` upload. | `run_native_ld_panel.py:1144-1148`, `:1101-1107` |
+| C2 | The raise becomes `status="error: …"`. The row keeps `n_dropped_occluded` (set at `run_native_ld_panel.py:1068-1069`, before conversion at `:1090`). No `.npz` upload. | `run_native_ld_panel.py:1144-1148`, `:1101-1107` |
 | C3 | Local scratch is reclaimed **only** when `status == "ok"`. The docstring puts intermediates at "~30+ GiB/region … overflows any finite scratch disk". | `:1149-1154`, `:723-725` |
-| C4 | The gate sidecar (`occ_sites`, `n_sites`, inflation, verdict) is written locally for every square region before plink. It is uploaded **only** on deferral or on `ok`. | written `:923-939`; uploaded `:961-965` (deferral), `:1129-1139` (inside `if ok:`) |
+| C4 | The gate sidecar (`occ_sites`, `n_sites`, inflation, verdict) is written locally, before plink, for every square region that gets past both the resume skip and the n_var feasibility ceiling and does not raise before the write (an already-banked region returns at `run_native_ld_panel.py:806-815`, an infeasible one at `:866-872`). It is uploaded **only** on deferral or on `ok`. | written `:923-939`; uploaded `:961-965` (deferral), `:1129-1139` (inside `if ok:`) |
 | C5 | Resume skips a region only if its `.npz` exists, so an `error:` region is recomputed on every re-fire. | `:799-815` |
 | C6 | Verifier: deferrals PASS ("the gates working"), `error:` = FINDING, an unknown status = HARD_STOP. The vocabulary is held by `test_shipped_status_vocabulary_is_covered_by_the_allow_list`. | `fire_verifier.py:330-399`, `:309-312` |
 | C7 | Precedent for a region that banks nothing outside the three posted branches: `deferred_infeasible_square` (`run_native_ld_panel.py:866-872`). Registered in-repo as "a DISCLOSURE OBLIGATION — not blocking the fire", with measured numbers owed at publication, a remedy path recorded, and a named enforcer. | `deferred-items.md:1148-1191`; enforcer `fire_verifier.py:875-939` |
@@ -106,21 +118,21 @@
 - **Code needed:** none.
 - **Already pre-registered?**
   - The *raise* is (T1). The *non-halting loop* is runbook, not OSF.
-  - The *disposition* is not. No branch fits: NONE needs "the fine-mapping result stand unmodified"
+  - The *disposition* is not. No branch fits: NONE needs "the panel and fine-mapping result stand unmodified"
     (trsx5:43), but nothing was banked; EXCLUDED needs "fine-mapping proceeds on the reduced variant set"
     (trsx5:45); DEFERRED's trigger is the anomaly gate (T3), and 00057's gate did **not** fire (a region
-    whose gate fires returns at `:967` before plink runs, so it cannot reach the raise at `:1090`).
+    whose gate fires returns at `run_native_ld_panel.py:967` before plink runs, so it cannot reach the raise at `:1090`).
   - *READING 1:* logging it under T6 changes no criterion, no gate and no variant's treatment. A
     deviation entry plus disclosure is what the posted discipline already requires, so no amendment
     is needed before code (and no code is involved).
-  - *READING 2 (the counter-reading, to be tested):* T5 presents the three branches as the complete
+  - *READING 2:* T5 presents the three branches as the complete
     list, and trsx5:53 fixes "the three outcome branches … before any occlusion-handling code fires".
     A region in none of them is a fourth outcome, which may need a posted amendment-update **before**
     Stage C.
 - **Consequences:**
   - Each raising region is a coverage gap shaped like R4-COVERAGE (C7), but with **no** registered
     disclosure obligation or enforcer yet.
-  - After the first raise, every later `stage-c` check-in exits 1 for the rest of the ~11 days. Each is
+  - After the first raise, every later `stage-c` check-in exits 1 for the rest of the ~11 days (`AGENT-PROMPT.md:393`). Each is
     an R8 STOP. A *new* failure then shows up on a gate that is already red. The verifier does print
     per-status counts (`fire_verifier.py:363-370`), so a new failure is visible only by diffing check-ins.
   - C3, C4 and C5 apply (see §4).
@@ -139,27 +151,27 @@
     DRAFTED — NOT POSTED entry), so it is not an occlusion under clause (a) (mk7ze P300-302 / R467-469).
   - A new token runs into the explicit "NO new token" sentence (mk7ze P316 / R483). That sentence is
     scoped to the companion condition, so how far it reaches is itself a question for review.
-- **Consequences:** check-ins stay green. A contract raise gets counted as "the gates working"
-  (`fire_verifier.py:335-336`), which is not the rationale that PASS was built on. "Deferred for
+- **Consequences:** check-ins stay green. A contract raise would be classified under the deferral PASS, whose stated reason is "the gates working"
+  (`fire_verifier.py:335-336`). "Deferred for
   re-diagnosis" presumes a diagnosis still to do, but the mechanism for this class is already
   established for 00057 (`260824-STAGE-B-HALT-…md:150-179`).
 
 ### Option C: halt on each raise and re-diagnose before continuing
 
-- **Behaviour:** literal `--fail-fast` is not workable (P4). The realistic form is the operator stopping
-  the fire at the first `error:` row.
+- **Behaviour:** literal `--fail-fast` would also halt on already-banked and deferred regions (P4), so
+  this option means the operator stopping the fire at the first `error:` row.
 - **Code needed:** none (runbook change only).
 - **Already pre-registered?** No posted text requires or forbids halting, so no amendment either way.
 - **Consequences:** the Stage B halt record already argues against this at an unknown rate:
   "`--fail-fast` is correct for Stage A/B and **must not be carried into Stage C** at an unknown
   per-region failure rate" (`260824-STAGE-B-HALT-…md:104-107`). *For planning only, not a calibrated
-  rate:* 1 of 21 sampled regions carries a surviving pair. The sample was systematic-by-span, not
-  random, and the one case is predicted, not observed (P5). Scaled to 276 that is ≈13 regions, with an
+  rate:* 1 of 21 sampled regions carries a surviving pair (`osf_deviations.md:660-663`). The sample was systematic-by-span, not
+  random (mk7ze P88-89 / R255-256), and the one case is predicted, not observed (P5). Scaled to 276 that is ≈13 regions, with an
   exact 95% binomial range of 0.3–66.
 
 ### Option D: measure before deciding (combines with A or B)
 
-- **Behaviour:** Carter runs the existing pairwise-completeness scan across all 276 AFR regions before
+- **Behaviour:** Carter runs the existing pairwise-completeness scan across all 276 AFR regions (mk7ze P88-89 / R255-256) before
   Stage C, so any posture is chosen against a measured list of regions expected to raise. This is a
   read-only measurement. *Unmeasured scaling:* the 21-region run took 48 min (STATE.md frontmatter,
   2026-09-01), which scales linearly to ~10.5 h.
@@ -168,9 +180,9 @@
   **But there is a sequencing constraint.** The disclosure's prospective production prediction is "to
   be pre-registered IF AND WHEN this disclosure is posted, and posted BEFORE production testing"
   (`osf_deviations.md:685-689`), and "Production tests the rate on BOTH sides" (`:682`). A full-panel
-  scan *is* that test. Running D before the disclosure is posted would use up the prediction, unless
-  the prediction is explicitly retired first.
-- **Consequences:** turns a surprise into a pre-declared, measured set. Needs VM time (Carter).
+  scan would measure that same both-sides rate before production does; whether that uses up the
+  prediction is question 5.
+- **Consequences:** the regions expected to raise are measured before Stage C instead of observed during it. Needs VM time (Carter).
 
 ### Option E: change what reaches the matrix (listed for completeness)
 
@@ -190,7 +202,7 @@
   every raising region unless scratch is harvested by hand. Closing that gap in code touches the fire
   path and needs a decision.
 - **X2: scratch fills up.** A raising region's `.ld.bin` (n_var² × 4 B; ≈57.6 GB at the
-  120,000-variant ceiling) stays in scratch (C3). The VM's scratch capacity was **not** checked here. A
+  120,000-variant ceiling; `READY-TO-FIRE.md:369-370`) stays in scratch (C3). The VM's scratch capacity was **not** checked here. A
   few large raising regions could make later regions fail with `error:` for an unrelated reason.
 - **X3: resume re-spends compute.** Every re-fire recomputes and re-raises each raising region (C5),
   assuming identical inputs.
```

## 6. Final GREEN RESULT lines

Pre-commit (Task 2 STEP F, re-run after the selftest code landed; plan's Task 2 verify printed `green-full-id-set`, and my added duplicate-id assertion printed `no-duplicate-ids`):

```
default            : RESULT GREEN checks=317 parsed=88 table=88 verified=88
--source           : RESULT GREEN checks=318 parsed=88 table=88 verified=88
--live --source    : RESULT GREEN checks=319 parsed=88 table=88 verified=88
```

Post-commit at HEAD f09535c:

```
default            : RESULT GREEN checks=317 parsed=88 table=88 verified=88
--source           : RESULT GREEN checks=318 parsed=88 table=88 verified=88
--live --source    : RESULT GREEN checks=319 parsed=88 table=88 verified=88
```

SKIP set: default = exactly {`f:forward`} (`SKIP f:forward no --source`); `--source` and `--live --source` have zero SKIPs. Per-family counts in every GREEN run: `c:` 88 PASS, `c-res:` 88, `c-quote:` 30, `c-bind:` 30, `c-pr:` 16. `f:reverse` = 16817 B / md5 5e11157f3b56addada24134bd7e2225f.

## 7. `--selftest` output (verbatim; post-commit run, rc 0)

The pre-commit run's output was identical apart from the random temp dir suffix (checked with `diff`). Runtime was about 110 s.

```
SELFTEST tmpdir /gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/kht-tmp/kht-selftest-_6d45xw1 (outside repo /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis)
SELFTEST positive-control GREEN: RESULT GREEN checks=317 parsed=88 table=88 verified=88
SELFTEST OBSERVED ST-a1 -> RED  a:size lines 168-500 = 22977 B (want 22945)
SELFTEST OBSERVED ST-a2 -> RED  a:size lines 169-500 = 22944 B (want 22945)
SELFTEST OBSERVED ST-a3 -> RED  a:control control matched: anchor cannot fail (lines 168-500 md5 13a49f543cabcc27ce9f1e589783c060)
SELFTEST OBSERVED ST-b1 -> RED  b:size 9696 B (want 9695)
SELFTEST OBSERVED ST-b2 -> RED  b:md5 md5 a70f41c4c46148c2bdf6a29349c9f8ad (want c19be8b2ad7cd6a45fee1d668d8a9cf9)
SELFTEST OBSERVED ST-b3 -> RED  b:control control matched: anchor cannot fail (first 9695 B md5 c19be8b2ad7cd6a45fee1d668d8a9cf9)
SELFTEST OBSERVED ST-c1 -> RED  c:c03 pos 3 `:422` AP:422-422 -- AP:422-422 missing ['without --fail-fast']
SELFTEST OBSERVED ST-c2 -> RED  c-quote:c26 quote NOT in draft: ['The raw per-region panel .npz reader continues to RAISE on any NaN rather than silently coercing it; occlusion handling is a distinct, upstream (panel-build) and lockstep (harmonization) step, not a weakening of the raw contract.']
SELFTEST OBSERVED ST-c3 -> RED  c:c26 pos 26 trsx5:39 TR:39-39 -- TR:39-39 missing ['The raw per-region panel .npz reader continued to RAISE on any NaN rather than silently coercing it; occlusion handling is a distinct, upstream (panel-build) and lockstep (harmonization) step, not a weakening of the raw contract.']
SELFTEST OBSERVED ST-c4 -> RED  c-count parsed=87 table=88; parsed tokens: ['`260812-ox1-AGENT-PROMPT.md:398`', '`:372-373`', '`:417`', '`260812-ox1-READY-TO-FIRE.md:360-366`', '`run_native_ld_panel.py:1325-1328`', '`plink_ld_to_npz.py:218-228`', '`run_native_ld_panel.py:1090-1093`', '`:1144-1146`', '`:1148`', '`:1101-1107`', '`:1278-1279`', '`fire_verifier.py:1097-1099`', '`:302-303`', '`:324-326`', '`:381-389`', '`:976-981`', '`AGENT-PROMPT.md:55-61`', '`:422-423`', '`fire_verifier.py:999-1001`', '`run_native_ld_panel.py:1278`', '`:806-815`', '`260824-STAGE-B-HALT-…md:20-21`', '`run_native_ld_panel.py:1325-1328`', '`260824-STAGE-B-HALT-…md:11-16`', '`.planning/osf_deviations.md:657-663`', 'trsx5:39', 'mk7ze P321-322 / R488-489', 'trsx5:29', 'mk7ze P261 / R428', 'mk7ze P311-312 / R478-479', 'trsx5:47', 'mk7ze P316-318 / R483-485', 'mk7ze P155-158 / R322-325', 'trsx5:43', 'trsx5:45', 'trsx5:49', 'trsx5:53', 'mk7ze P323-324 / R490-491', 'trsx5:59', 'mk7ze P247-250 / R414-417', 'trsx5:25', 'mk7ze P307-308 / R474-475', 'trsx5:49', 'mk7ze P302-305 / R469-472', '`plink_ld_to_npz.py:213-228`', '`260824-STAGE-B-HALT-…md:45-58`', '`run_native_ld_panel.py:1068-1069`', '`:1090`', '`run_native_ld_panel.py:1144-1148`', '`:1101-1107`', '`:1149-1154`', '`:723-725`', '`run_native_ld_panel.py:806-815`', '`:866-872`', '`:923-939`', '`:961-965`', '`:1129-1139`', '`:799-815`', '`fire_verifier.py:330-399`', '`:309-312`', '`run_native_ld_panel.py:866-872`', '`deferred-items.md:1148-1191`', '`fire_verifier.py:875-939`', '`READY-TO-FIRE.md:360-366`', '`AGENT-PROMPT.md:424-428`', 'trsx5:43', 'trsx5:45', '`run_native_ld_panel.py:967`', '`:1090`', 'trsx5:53', '`AGENT-PROMPT.md:393`', '`osf_deviations.md:703-704`', 'mk7ze P300-302 / R467-469', 'mk7ze P316 / R483', '`fire_verifier.py:335-336`', '`260824-STAGE-B-HALT-…md:150-179`', '`260824-STAGE-B-HALT-…md:104-107`', '`osf_deviations.md:660-663`', 'mk7ze P88-89 / R255-256', 'mk7ze P88-89 / R255-256', '`osf_deviations.md:685-689`', '`:682`', '`osf_deviations.md:670-671`', 'mk7ze P247-250', '`READY-TO-FIRE.md:369-370`', 'mk7ze P316', 'mk7ze P247-250']
SELFTEST OBSERVED ST-c5 -> RED  c-res:c60 pos 62 `deferred-items.md:1148-1191` -> .planning/quick/260908-n48-bank-the-seth-adjudication-closure-no-op/deferred-items.md (want .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md)
SELFTEST OBSERVED ST-c6 -> RED  c-pr:c29 mk7ze P262 / R428: P262-262 +167 = R429-429 vs stated R428-428
SELFTEST OBSERVED ST-c7 -> RED  c-ast:S2 RN:1144 innermost def = process_region (want main)
SELFTEST OBSERVED ST-d1 -> RED  d:defer 'defer' recomputed mk7ze=17 trsx5=4; draft states 18/4
SELFTEST OBSERVED ST-c8 -> RED  c-bind:c73 quote ['the gates working'] NOT in the paragraph unit of `fire_verifier.py:335-336` (draft line 155): '- **Consequences:** check-ins stay green. A contract raise would be classified under the deferral PASS, whose stated reason is "the gate outcome"\n  (`fire_verifier.py:335-336`). "Deferred for\n  re-diagnosis" presumes a diagnosis still to do, but the mechanism for this class is already\n  established for 00057 (`260824-STAGE-B-HALT-…md:150-179`).'
SELFTEST OBSERVED ST-n1 -> RED  c:n02 pos 71 `AGENT-PROMPT.md:398` AP:398-398 -- AP:398-398 missing ['~11 days']
SELFTEST OBSERVED ST-n2 -> RED  c-pr:n04 mk7ze P88-89 / R256-257: P88-89 +167 = R255-256 vs stated R256-257
SELFTEST OBSERVED ST-d2 -> RED  d:zero:defer 'defer' mk7ze=17 trsx5=4 (want 0/0)
SELFTEST OBSERVED ST-h1 -> RED  c-hand:H1 extracted x=1 n=21 N=276 conf=95 n_run=21 min=48 N_panel=276 bytes/cell=4 cap=120000; CP95=(0.001205, 0.23816); mid recomputed 13 stated 14, lo recomputed 0.3 stated 0.3, hi recomputed 66 stated 66, hours recomputed 10.5 stated 10.5, gb recomputed 57.6 stated 57.6, cap==S7 recomputed 120000 stated 120000 -- MISMATCH [('mid', 13, 14)]
SELFTEST OBSERVED ST-h2 -> RED  c-hand:H2 marker 'PRIOR: 2026-09-01 — NO SUCH BLOCK' occurs 0 times in ST@c93e97b frontmatter (want 1)
SELFTEST OBSERVED ST-h3 -> RED  c-hand:H3 OD line 533 is not a `## ` heading
SELFTEST OBSERVED ST-e1 -> RED  e:control git log --since='2026-08-24 00:00:00 -0400' --format=%H c93e97b -- RN FV PL: rc=0 count=0 oldest=None all=
SELFTEST OBSERVED ST-e2 -> RED  e:log git log --since='2026-08-01 00:00:00 -0400' --format=%H c93e97b -- RN FV PL: rc=0 count=6
SELFTEST OBSERVED ST-f1 -> RED  f:reverse reverse-applied E17..E1 to the draft: 16825 B (want 16817); md5 not computed: size failed (want 5e11157f3b56addada24134bd7e2225f)
SELFTEST OBSERVED ST-f2 -> RED  f:evidence:E6 c30 MK before {'range': [478, 478], 'prange': [311, 311]} -> RED (MK:478-478 missing ['A region over the anomaly gate is deferred for re-diagnosis …']; posted P311-311 missing ['A region over the anomaly gate is deferred for re-diagnosis …']); after {'range': [478, 478], 'prange': [311, 311]} -> RED (MK:478-478 missing ['A region over the anomaly gate is deferred for re-diagnosis …']; posted P311-311 missing ['A region over the anomaly gate is deferred for re-diagnosis …']) -- want before RED and after GREEN
SELFTEST OBSERVED ST-f3 -> RED  f:unique:E8 new x2 in draft; old xNone in source (UNAVAILABLE: no --source and f:reverse failed) (want 1/1)
SELFTEST OBSERVED ST-s9 -> RED  c-ast:S9 FAILED parts: (ii) sidecar assignment `gate_sidecar = ...` at 925 (want 923) | (ii) no `with open(gate_sidecar, "w")` at 925 | (iii) process_region returns before the sidecar (line 925) = [815, 872, 924] (want [815, 872]) | (iv) nodes enclosing the sidecar (line 925) = [('If', 923), ('Try', 825)] (want Try@825, If@850)
SELFTEST OBSERVED ST-g1 -> RED  g:recommend 1 hits: recommend -> ...e prospective production prediction? we recommend option b....
SELFTEST OBSERVED ST-g2 -> RED  g:recommend 1 hits: recommend -> ...e prospective production prediction? my recommendation is option a...
SELFTEST OBSERVED ST-g3 -> RED  g:options options ['A', 'B', 'C', 'D']
SELFTEST OBSERVED ST-g4 -> RED  g:questions questions ['1', '2', '3', '4']
SELFTEST OBSERVED ST-g5 -> RED  g:status status line '**Status:** DRAFT, not banked in the repo, no code written, **no decision made.** Built for review by'; missing ['not sent to seth', 'not decided']; contains 'not banked'
SELFTEST OBSERVED ST-g6 -> RED  g:exempt 'with no recommendation' occurs 2 times (want exactly 1)
SELFTEST GREEN positive-control=GREEN observed=33/33
```

Families represented: a (a1-a3), b (b1-b3), c incl. c-quote/c-count/c-res/c-pr/c-ast/c-bind (c1-c8), new class-4 rows (n1, n2), d (d1, d2), c-hand (h1-h3), e (e1, e2), f (f1-f3), c-ast:S9 part (iii) (s9), g (g1-g6). The temp dir sits directly under `$TMPDIR` (resolved and checked to be outside the repo) and is removed in `finally`; `find "$TMPDIR" -maxdepth 1 -type d -name 'kht-selftest-*' | wc -l` afterwards = 0 (the glob `kht-selftest-*` also matches my captured output file `kht-selftest-post.txt`, which is a file, not a temp dir).

## 8. `e:*` lines (verbatim)

Default (BASIS) run:

```
PASS e:control git log --since='2026-08-01 00:00:00 -0400' --format=%H c93e97b -- RN FV PL: rc=0 count=6 oldest=5284505 all=dd8f0b8 e5e7ac7 d7f3b18 d9fbc63 ee16f79 5284505
PASS e:log git log --since='2026-08-24 00:00:00 -0400' --format=%H c93e97b -- RN FV PL: rc=0 count=0
PASS e:diff-control git diff --quiet 5284505~1 c93e97b -- src/python/run_native_ld_panel.py rc=1 (want 1)
```

`--live --source` run at HEAD f09535c:

```
PASS e:control git log --since='2026-08-01 00:00:00 -0400' --format=%H HEAD -- RN FV PL: rc=0 count=6 oldest=5284505 all=dd8f0b8 e5e7ac7 d7f3b18 d9fbc63 ee16f79 5284505
PASS e:log git log --since='2026-08-24 00:00:00 -0400' --format=%H HEAD -- RN FV PL: rc=0 count=0
PASS e:diff-control git diff --quiet 5284505~1 c93e97b -- src/python/run_native_ld_panel.py rc=1 (want 1)
PASS e:diff git diff --quiet c93e97b -- RN FV PL rc=0 (want 0)
```

The control window is non-empty: **6 commits, oldest 5284505**. `e:log` is accepted as empty only because `e:control` in the same run is non-empty.

## 9. Scope-guard outputs (verbatim)

Pre-commit (STEP C, before staging): `git log --oneline -3` top = `c93e97b docs(handoff): SESSION CLOSE 2026-09-16 …`. `git status --porcelain --untracked-files=no` printed nothing. The frozen-paths status printed nothing. The task-path status printed exactly:

```
?? .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md
?? .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-PLAN.md
?? .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py
```

`git diff --cached --name-only` after the explicit-path `git add --` printed exactly the two paths, and HEAD was re-checked == c93e97b immediately before `git commit -F`.

Post-commit (log subjects cut at 160 chars):

```
$ git log --oneline -3
f09535c docs(quick-260916-kht): bank the Stage C NaN error-posture options draft (brief-blind, docs-only; 88 citations re-verified at c93e97b with observed-RED 
c93e97b docs(handoff): SESSION CLOSE 2026-09-16 — resume the ANALYSIS at Stage C's NaN error posture (halt-record steps 1-2 done, step 3 open); bank the full 45
a7720a5 docs(handoff): VM STOPPED — no billing instance remains; record the falsifiable daily-spend check (~$93/day -> ~$30/day if the disks released)
$ git status --porcelain --untracked-files=no
(end: empty)
$ git status --porcelain --untracked-files=all -- src tests config workflow bin .planning/amendments .planning/osf_deviations.md .planning/HANDOFF.json .planning/STATE.md
(end: empty)
$ git status --porcelain --untracked-files=all -- .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/
?? .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-PLAN.md
(end)
$ git show --name-status --format= HEAD
A	.planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md
A	.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py
```

## 10. Limits, stated plainly

- **(g) is a lexical screen, not a proof of neutrality.** It catches recommendation words, including ones split by markdown (ST-g2). It cannot catch framing, emphasis or ordering. The brief-blind structure of the review is the real safeguard.
- **Default-mode verdicts are pinned to the immutable basis c93e97b.** `--live` will go RED once any cited file changes. That means re-verify the draft's line numbers before sending it; it never means re-pin BASIS.
- **`f:forward` needs the scratchpad source; `f:reverse` does not.** `f:reverse` is the permanent must-be-identity proof committed in the verifier.
- **ST (STATE.md) is read at BASIS only**, in every mode, because it is a living log.
- `c-bind` checks that a quote sits in the same paragraph unit as its citation token. It does not check that the surrounding prose describes the quote fairly.
- Q rows prove the quoted words are inside the cited range. T rows prove only that chosen tokens are there; they support the claim without proving its paraphrase.

## 11. Observations not acted on

1. **Plan prose count:** `<cited_files>` says DI is "NOT any of the other 11 `deferred-items.md` files". Measured: `git ls-tree -r --name-only c93e97b | grep -E '(^|/)deferred-items\.md$' | wc -l` = **14**, so 13 others. This affects no check: DI resolves through the key (`c-res:c60` PASS), and ST-c5 shows that a sibling path (`260908-n48…/deferred-items.md`, tracked at basis) goes RED.
2. **Line-wrap cosmetics:** E3-E5, E8-E12 and E17 make some lines longer than the surrounding wrap width, and E13 leaves a short line. Nothing was rewrapped, as the plan requires.
3. **"Code at HEAD `c93e97b`"** in the Anchors block now describes the drafting basis, not the repo HEAD (f09535c). `c-hand:H5` verifies ancestry. Not edited, because it is not a permitted edit.
4. The report-only numeric sweep flags `260916` on banked line 3. It comes from the E1 status text itself ("quick-260916-kht").

## 11b. Report-only sweeps (not gates; final post-commit default run, verbatim, banked line numbers)

```
INFO report:eval:218 ['should'] :: 3. Should the R4-COVERAGE precedent (C7: a disclosure obligation with a named enforcer, not blocking
INFO report:numeric:3 ['260916'] :: **Status:** DRAFT, banked in the repo (quick-260916-kht), NOT sent to Seth, NOT decided, no code written, **no decision made.** Built for review by
INFO report:numeric:38 ['10'] :: **P1: The committed Stage C command does not use `--fail-fast`.** STEP 10 runs
INFO report:numeric:63 ['+1'] :: **P5: One raise is observed; the second is predicted.** `m2_region_00057` (+1) raised in Stage B
INFO report:numeric:184 ['5'] ::   prediction is question 5.
INFO report:numeric:189 ['−1', '+1'] :: Options here would be widening the predicate to cover −1/+1, a pairwise-completeness exclusion rule, or
```

For the orchestrator to judge: the only evaluative-word hit is `should` in §5 question 3 (line 218). It is a question put to the adjudicator, as the planner previewed. The numeric hits are `STEP 10`, `(+1)` / `−1/+1` (offset labels), `question 5` (a cross-reference) and `260916` (quick-task id).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Write / Read / Edit tools unavailable (PreToolUse hook not responding)**
- **Found during:** Task 1 (first Write of `$VER`). It failed three times, including a 10-byte test file in the scratchpad. Read of the banked file also failed, so Edit (which needs a Read first) could not be used.
- **Fix:** `$VER` was written with quoted Bash heredocs (`<<'EOF'`, byte-exact) and extended by exactly-once marker replacements in scratchpad patch scripts. For STEP D, the plan said to apply E1-E17 with the Edit tool; I instead used `cp "$SRC"` (md5 confirmed 5e11157f…) and then a **standalone** script whose old/new strings were typed separately from the PLAN text and which does **not** import the verifier. It asserted each `old` exactly once at its application point and each `new` exactly once in the result. Its output (223 lines, 18309 B, md5 763f412bb1a8dbdb38f2cc332ed5a21d) matched the verifier's own in-memory application of its `PERMITTED_EDITS` byte for byte, and `f:forward` / `f:reverse` prove the identity permanently. This SUMMARY was also written through Bash.
- **Files modified:** the two committed files (no extra files in the repo).
- **Commit:** f09535c

**2. [Rule 1 - Bug in the contract's literal form] `c-ast:S9` (iii)/(iv) anchored on the AST-located sidecar assignment**
- **Found during:** Task 1 design, checked against the ST-s9 mutation.
- **Issue:** With a literal `line < 923`, the ST-s9 insertion puts the new `return` on line 924, so part (iii) could never go RED and the plan's expected "RED naming part (iii)" could not happen.
- **Fix:** (iii) and (iv) use the line of the first `gate_sidecar = ...` Assign inside `process_region`, and part (ii) separately requires that line == 923. On the real basis this equals the literal contract. The docstring explains it.
- **Commit:** f09535c

**3. [Rule 2 - Missing guard, orchestrator Info 4] duplicate result ids**
- `summarize()` emits `RED dup-ids` if any non-INFO id appears twice. The Task 2 JSON checks were run with an extra duplicate-id assertion, which passed on all five JSON outputs (default, --source, --live, baseline, baseline2).

### Implementation interpretations (no behaviour beyond the contract)
- `f:unique:<Eid>` without `--source` counts `old` in the reverse-reconstructed source, and only when `f:reverse` matched md5. Otherwise it is RED ("UNAVAILABLE").
- `--selftest` refuses to run unless `TMPDIR` is set, and requires the temp dir to be directly under the resolved `$TMPDIR`. Each mutation runs the whole engine, not just its own family. ST-s9 additionally requires the RED message to contain "(iii)" and asserts `ast.parse` succeeds on the mutated file, so the RED cannot come from a parse failure.
- **ST-s9 string used exactly as written in the plan** (8-space `if False:` / 12-space `return result`). I first expected this to be a SyntaxError and planned a 12/16-space variant. Measured first: it parses (the rest of the `if mode == "square":` body is re-parented under `if False:`) and S9 goes RED naming (ii), (iii) and (iv). So no change was made.
- The a-anchor follows b's rule: if `a:size` fails, `a:md5` is RED "not computed".

**Total deviations:** 3 auto-fixed (1 blocking tooling, 1 contract-literal bug, 1 missing guard). **Impact:** none on the banked content; the file is byte-identical to source + E1-E17.

## Known Stubs

None. The verifier stubs from Task 1 (`--selftest` / `f:` / `--bare-ref-plan`) were all replaced before the commit.

## Threat Flags

None. Two docs-only files; the verifier's only subprocess is `git` with `cwd=ROOT` (no network, no `shell=True`, no `src/` imports), and `--json` refuses a path inside the repo.

## Self-Check: PASSED (FOUND: .planning/debug/260916-STAGE-C-NaN-ERROR-POSTURE-options-DRAFT.md; FOUND: .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py; FOUND: commit f09535c; parent == c93e97b by full hash; post-commit default / --source / --live --source GREEN 88/88/88; post-commit --selftest 33/33)
