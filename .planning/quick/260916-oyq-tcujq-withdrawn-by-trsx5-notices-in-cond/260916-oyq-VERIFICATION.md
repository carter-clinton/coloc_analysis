---
phase: quick-260916-oyq
verified: 2026-09-17T01:12:59Z
status: passed
score: 11/11 must-haves verified
overrides_applied: 0
---

# Quick task 260916-oyq: tcujq WITHDRAWN-by-trsx5 notices — Verification Report

**Goal:** Add WITHDRAWN-by-trsx5 notices to the docstrings of `src/python/condition_ld_matrix.py` and `src/python/write_conditioned_ld_npz.py`. The notices only add text: no code or code string changes. They must be true against the POSTED trsx5 body and must not claim more than trsx5 says. Move `condition_ld_matrix.py` from its whole-file numstat pin to the existing CODE pin, per Carter's "Both files + rescope pin (Recommended)". `plink_ld_to_npz.py` and `occlusion_span_filter.py` keep numstat. Add a named `ast`-based enforcer. Record the decision in `.planning/DECISIONS.md`, appending only.
**Verified:** 2026-09-17T01:12:59Z. HEAD `48b8828`; commits C1 `b6b1f70`, C2 `b709ce1` and C3 `48b8828`, on parent `0231cbf`.
**Status:** passed
**Re-verification:** No. This is the first verification.
**Method:** I did not rely on the executor's SUMMARY; this report rests on my own checks. I did not edit the real repo and ran no pytest in it. All probes ran in a `git clone --shared` scratch clone under the session scratchpad, checked out with `tests src config Snakefile scripts bin` plus the posted trsx5 file. The clone was deleted afterwards. No processes were left running and no network was used.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Both module docstrings (from `ast.get_docstring`) hold exactly one notice. It starts at docstring line index 2 (clm) or 3 (wcn), which is ≤ 4. It names tcujq, trsx5, 2026-07-04, 2026-07-10, exclude-in-lockstep, "not called by the pipeline" and the DEC id, and contains the POSTED line-19 sentence up to "is withdrawn." | VERIFIED | Independent script: posted file is **9695 B** (size checked first), md5 `c19be8b2ad7cd6a45fee1d668d8a9cf9`, no trailing newline, 59 `splitlines()`. Line 17 is `What is withdrawn:`. The token sequence of the quoted block equals the posted sentence exactly in both files. The enforcer's positive tests pass in the clone at HEAD. |
| 2 | The `condition_ld_matrix()` function docstring has a short notice in its first 7 lines (withdrawn / tcujq / trsx5 / 2026-07-10 / pointer to the module notice / the retained fully-NaN-row rule) | VERIFIED | Docstring lines 2-6. `c.condition_ld_matrix.__doc__` shows `WITHDRAWN POLICY: this conditioning (tcujq, OSF 2026-07-04) was WITHDRAWN by…` |
| 3 | The notice is TRUE and does not claim more than the sources support | VERIFIED | Checked sentence by sentence. See "Notice truth audit" below. |
| 4 | The src edits are purely additive and change no code | VERIFIED | numstat `0231cbf..HEAD`: clm **+37/-0**, wcn **+29/-0**. PRE lines are an ordered subsequence of HEAD lines (213→250, 112→141). `source_freeze.code_lines` is identical PRE vs HEAD for both files, and also identical bf16289 vs HEAD. The AST with docstrings stripped is identical. All raise-message constants are identical PRE vs HEAD. Both "pre-registered" raise-string lines occur exactly once, byte-identical, at PRE and at HEAD. |
| 5 | `test_the_handoff_frozen_claim_is_recorded_as_partly_false` holds clm to `assert_code_frozen(rel, PY_CODE_REF, LANG_PY)` inside `for rel in code_only:`, and keeps numstat for exactly plink + occlusion. `PY_CODE_REF`, `PY_FROZEN_RELS` and every other test are unchanged. | VERIFIED | AST comparison of all 38 top-level nodes PRE vs HEAD: only this one function differs. `PY_CODE_REF = 'bf16289'` and `PY_FROZEN_RELS` are unchanged. `for rel in code_only:` occurs 0 times at PRE and 1 at HEAD. The original numstat statements are still present byte-identical. |
| 6 | The rescoped assertion can fail (seen in a scratch clone) | VERIFIED | (a) Committed docstring-only edit to clm: rescoped test **1 passed**, 25 code pins passed. The OLD form in the same clone was **RED** (`… is NO LONGER 0-diff vs bf16289 ('38\t1\t…')`). (b) Committed raise-string edit `pre-registered`→`pre-registeredX`: **RED** `the CODE of src/python/condition_ld_matrix.py (whole file) has MOVED off its pin bf16289`, and the first difference names `pre-registeredX`. (b') Committed `ceiling_frac` 0.0005→0.0006: **RED**. (c) Committed docstring-only edit to `plink_ld_to_npz.py`: **RED** `NO LONGER 0-diff`. (c') The same on `occlusion_span_filter.py`: **RED**. (d) An *uncommitted* raise-string edit: **RED**, confirming the note that the rescoped check reads the working tree. (e) Committed comment-only edit to clm: **GREEN**. At unmodified HEAD the OLD form is RED (`37\t0`) and the rescoped form is GREEN. |
| 7 | The enforcer fails at C2 (3 failed / 14 passed, exactly the 3 positive notice tests) and passes after C3 (17 passed) | VERIFIED | In the clone, with b709ce1's src restored: `3 failed, 14 passed`, and the three failures are `test_module_docstring…[condition_ld_matrix]`, `[write_conditioned_ld_npz]` and `test_function_docstring…[condition_ld_matrix]`. At HEAD: `17 passed` (all ids listed). Enforcer + pins + source_freeze + both module test files: **121 passed**. |
| 8 | The enforcer is sound: it parses the MODULE docstring with `ast`; a notice moved into a comment or string constant goes RED; it has caller-scan positive controls | VERIFIED | My own mutations on the REAL files, independent of the enforcer's helpers, all went RED with the specific message: notice moved into `#` comments after `import sys` → "holds 0 … not exactly 1". Moved into a module-level `_NOTICE = """…"""` → same. Moved into the *function* docstring of `write_conditioned_npz` → same. One hyphen removed from the quoted sentence → "verbatim POSTED … missing". `2026-07-10`→`-11` in the wcn body → "required token '2026-07-10'". Function notice removed → "required token 'withdrawn'". Function notice pushed past the 7-line window → "required token 'trsx5'". Module notice pushed to docstring line 6 → "not prominent". Posted body +1 byte → "9696 B, not 9695 B". Same-size 1-char edit → md5 mismatch. Caller scan: a staged `scripts/` importer, a `.smk` text mention and a `bin/` subprocess script path each went **RED**. The positive-control test passes, and both anchors exist (`m3_occlusion_lockstep.smk` names `occlusion_span_filter`; `run_ld_build_plan.py:123` has `"scripts/build_ld_rds.py"`). |
| 9 | Neither module has a caller in tracked pipeline files | VERIFIED | Independent `git grep` over ALL tracked files outside `.planning` (not only the pipeline paths): the stems appear only in the two modules and in tests. The only import is `write_conditioned_ld_npz.py` → `condition_ld_matrix`. There are no untracked files under the pipeline paths, and nothing in the untracked `targeted_rerun_scripts/` or `targeted_rerun_jobs/`. `test_run_native_ld_panel.py::test_no_nan_to_zero_conditioning_in_the_driver` also forbids both stems in the driver. |
| 10 | DECISIONS.md is append-only vs 0231cbf, and the entry records Carter's exact wording, the measured premise correction, and that the other two frozen modules do not change | VERIFIED | The first 193,875 bytes of HEAD equal PRE; HEAD is 203,326 B; numstat is `127 0`. My negative control (first bullet deleted) made the prefix check fail (rc=1). The entry quotes the option label and description word for word, and the quote matches the PLAN `<objective>`. It records the premise correction measured at `0231cbf`. I re-derived that classification myself and got the same result: clm DOCSTRING 1/3/26/123/130, CODE-STRING 153/200; wcn DOCSTRING 4/17/18, COMMENT 85. Its `:194-199` cite matches the numstat block at 0231cbf. It covers Proof A, B1-B5, the working-tree-vs-commit semantics, and a **named non-change for `plink_ld_to_npz.py` and `occlusion_span_filter.py`**. The observation for Carter and the cross-refs are present, and the `STATE.md:82` / `:61@11f61e8` and `HANDOFF.json:261` cites check out. |
| 11 | Full-suite by-name reconciliation, and the kht verifier stays GREEN | VERIFIED | I parsed the executor's JUnit files myself. PRE `suite_pre.xml`: 1245 ids = **1212 passed / 33 skipped**, 0 failures/errors, 0 duplicates, run 20:14-20:27 EDT at 0231cbf (C1 landed 20:37). POST `suite_post.xml`: 1262 ids = **1229 passed / 33 skipped**, run 20:46-20:59 EDT at 48b8828 (C3 landed 20:42). **ADDED 17**, all `tests.m3.test_tcujq_withdrawal_notices::…` and all passed. **REMOVED 0, CHANGED 0.** Both logs end `EXIT=0`. kht verifier default mode, run by me: `RESULT GREEN checks=317 parsed=88 table=88 verified=88`, with the tracked tree still clean afterwards. |

**Score:** 11/11 truths verified

### Notice truth audit (sentence by sentence)

| Claim in notice | Source | Verdict |
|---|---|---|
| tcujq on az52u, posted 2026-07-04T04:14:46Z | `osf_deviations.md:97` ("OSF file `tcujq` on parent record az52u"), `:104` `2026-07-04T04:14:46.635031Z` | True (seconds truncation) |
| trsx5 on az52u, amendment-update, posted 2026-07-10T13:32:22Z | `osf_deviations.md:135`, `:155` `2026-07-10T13:32:22.212989Z`; posted body line 1 "Amendment-update …" | True |
| Quoted "What is withdrawn:" sentence | Posted body line 17 heading and line 19, cut at "is withdrawn." Tokens match exactly. The repo-canonical trsx5 copy (`amendments/…UPDATE-2026-07-10.md:51`) holds the same sentence byte for byte, so the two known versions of the body agree on this sentence. | True, verbatim |
| Replacement = occlusion exclude-in-lockstep (panel AND harmonized sumstats), mandatory provenance manifest; NaN→0 prohibited | Posted lines 21, 25 (b), 27 (c); line 25 "correlation fabrication (NaN→0) … prohibited" | True (a summary; the anomaly gate and present-rate reporting are left out, which does not overstate anything) |
| trsx5 RETAINS unchanged: fully-NaN-row drop rule, PSD methods, raw-panel NaN-raise contract | Posted line 33 heading, lines 35/37/39 | True |
| "this module raises on a fully-NaN row" | clm `raise ValueError(… FULLY NaN …)` after `_fully_nan_rows_blocked`. The smoke run raised on a 3×3 all-NaN off-diagonal matrix. | True |
| Only the isolated-pair zeroing + ceiling + BRANCH_AFR_COND_* are withdrawn, not "the module" wholesale | Matches line 19. The function notice says the fully-NaN-row raise is NOT part of the withdrawal. | Stays within what trsx5 says |
| "Two of the four error-message strings at its raise sites still say 'pre-registered', and one of those two also names BRANCH_AFR_COND_DEFERRED" | AST walk of clm: 4 `Raise` nodes; 2 contain "pre-registered"; 1 contains BRANCH_AFR_COND_DEFERRED, and that one also says "pre-registered"; 1 fully-NaN raise. wcn: 2 raises, 0 "pre-registered". | True, exact |
| Those strings are CODE under the source-freeze pin | Probe (b): a raise-string edit makes the code pin RED | True |
| FROZEN / HELD; m3-06 HELD | `PY_FROZEN_RELS`; STATE.md:5 "m3-06 HELD, condition_ld_matrix.py FROZEN"; ROADMAP.md:213; HANDOFF.json:41 | True |
| NOT called by the pipeline (both modules; function too) | Truth 9 | True (clm's only importer is wcn, which has no caller) |
| "original 2026-07 wording, kept as written" | `git log --follow`: each file had exactly one prior commit (ccca5b8 / f147041, 2026-07-07). PRE lines are a subsequence of HEAD. | True |
| wcn: code, error strings, provenance keys (`nan_policy`, `n_zeroed`, `zeroed_pairs`, `ceiling_frac`) unchanged | All four keys are in `np.savez_compressed`, and the code is identical PRE vs HEAD | True |
| New comment line: "Policy WITHDRAWN by trsx5, OSF 2026-07-10" | as above | True, and the existing comment line is untouched |

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `tests/m3/test_tcujq_withdrawal_notices.py` | Named enforcer; contains `c19be8b2…` | VERIFIED | 521 lines. 5 uses of `ast.get_docstring`. No `*_REF`/`*_REV` names, no `assert_code_frozen` call, no skip or xfail. Imported and run by pytest (17 ids in the POST JUnit). |
| `tests/m3/test_source_freeze_pins.py` | Rescoped test; contains the DEC id | VERIFIED | +38/-2. The 2 removed lines are the docstring closing line and `for rel in PY_FROZEN_RELS:`. Module-docstring caveat and `#:` line added. |
| `src/python/condition_ld_matrix.py` | `==== WITHDRAWN POLICY NOTICE (tcujq -> trsx5)` | VERIFIED | Module notice and function notice; additions only |
| `src/python/write_conditioned_ld_npz.py` | same marker | VERIFIED | Module notice and one comment line; additions only |
| `.planning/DECISIONS.md` | `## 2026-09-16 — DEC-2026-09-16-condition-ld-matrix-freeze-code-only` heading | VERIFIED | Appended at EOF; byte-prefix check passes |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| pins `test_the_handoff_frozen_claim…` | `source_freeze.assert_code_frozen` | `for rel in code_only:` | WIRED | Calls the existing function (no new stripper, no `actual_text` seam). Probes (b)/(b')/(d) RED, (a)/(e) GREEN. |
| enforcer | posted trsx5 reconstruction | size → md5 → `splitlines()[18]` | WIRED | +1 byte fails the size check; a same-size edit fails the md5 check |
| enforcer | both src modules | `ast.parse` + `ast.get_docstring(clean=True)` | WIRED | The comment, string-constant and function-docstring relocations are all RED even though every token is still in the file text |

### Data-Flow Trace (Level 4)

Not applicable: the task changes docstrings, tests and a decision record, and renders no dynamic data.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Enforcer + neighbours at HEAD (clone) | `pytest -q test_tcujq_withdrawal_notices.py test_source_freeze_pins.py test_source_freeze.py test_condition_ld_matrix.py test_write_conditioned_ld_npz.py` | `121 passed` | PASS |
| Enforcer against pre-notice src (clone) | `git checkout b709ce1 -- <2 src>`; pytest enforcer | `3 failed, 14 passed` (the 3 declared ids) | PASS |
| `__doc__` shows the notice at runtime | import both modules in the clone | Line 2 of clm `__doc__` and line 3 of wcn `__doc__` are the `==== WITHDRAWN POLICY NOTICE …` line | PASS |
| Behaviour unchanged | clm on a 4×4 matrix with one isolated NaN pair → over-ceiling raise; 3×3 fully-NaN → fully-NaN raise | Both raise with the original messages | PASS |
| kht verifier default mode | `TMPDIR=<scratch> /usr/bin/python3 …/260916-kht-verify.py \| tail -1` | `RESULT GREEN checks=317 parsed=88 table=88 verified=88` | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| QUICK-260916-oyq | 260916-oyq-PLAN.md | STATE RESUME item 3 (the tcujq docstring defect) and Carter's 2026-09-16 decision "Both files + rescope pin (Recommended)" | SATISFIED | Truths 1-11 |

### Anti-Patterns Found

None in the added lines (no TODO, FIXME, placeholder, etc.). No notice line has an apostrophe, backslash or triple quote, or starts with `def ` (the hazards from M6); `test_source_freeze.py` passes. No notice line is longer than 88 characters; the long lines in these files were already there before this task.

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `tests/m3/test_tcujq_withdrawal_notices.py` | `py_hits` / `pipeline_scan` | Dynamic imports are not detected: a staged `importlib.import_module("write_conditioned_ld_npz")` stayed GREEN (probe CN4). Untracked files are also not scanned (probe CN5). The second limit is stated in the docstring; the first falls outside the stated working definition (imports / `<stem>.py` string / non-.py text). | Info | Nothing is affected today: an independent `git grep` finds no mention of either stem in any tracked non-test file. It is a gap to keep in mind if the enforcer is ever cited as full caller coverage. |
| `.planning/osf_deviations.md` (context, not changed) | ADJUDICATED / RECHARACTERIZED 2026-08-14 | The posted trsx5 body is recorded as a truncated / "unexplained third" version. | Info | The notice quotes only line 19, which is in the posted body, and the repo-canonical copy has the same sentence byte for byte. The notice makes no claim that the body is complete, so the quote holds. |

### Human Verification Required

None. Every claim in the notice was checked against the posted body, `osf_deviations.md`, and the modules' AST and runtime behaviour. The OSF timestamps are checked against the repo ledger (`osf_deviations.md:104/:155`) as the brief specified; I did not contact OSF.

### Gaps Summary

No gaps. The notices add text only, change no code, match the POSTED trsx5 sentence exactly, and are limited to what trsx5 actually withdrew. They state the raise-site counts correctly and point to the retained fully-NaN-row rule. The rescope works as intended. In a scratch clone, committed docstring and comment edits to `condition_ld_matrix.py` are now free, while any code-token edit (committed or not) is RED. `plink_ld_to_npz.py` and `occlusion_span_filter.py` are still byte-pinned. The enforcer reads the docstrings through `ast` and fails on every relocation, tampering and caller mutation I tried, independently of its own committed controls. The decision record is append-only and faithful. The full suite reconciles by name: +17 (all in the new file, all passed), -0, 0 changed.

Housekeeping: I ran no pytest in the real repo and left the tracked tree clean. The scratch clone and my probe scripts were removed, `$SCRATCH/clones` is still empty, and no pytest process is running.

---

_Verified: 2026-09-17T01:12:59Z_
_Verifier: Claude (gsd-verifier)_
