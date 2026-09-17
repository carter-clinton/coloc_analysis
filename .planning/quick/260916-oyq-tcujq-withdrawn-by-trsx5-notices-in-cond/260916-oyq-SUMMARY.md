---
phase: quick-260916-oyq
plan: 01
subsystem: frozen NaN-conditioning modules (m3-06, HELD) + source-freeze pins
tags: [tcujq, trsx5, withdrawal-notice, source-freeze, code-pin, enforcer, docs, negative-controls]
requirements-completed: [QUICK-260916-oyq]
key-files:
  created:
    - tests/m3/test_tcujq_withdrawal_notices.py
  modified:
    - tests/m3/test_source_freeze_pins.py
    - .planning/DECISIONS.md
    - src/python/condition_ld_matrix.py
    - src/python/write_conditioned_ld_npz.py
key-decisions:
  - "condition_ld_matrix.py's freeze is CODE-only (DEC-2026-09-16-condition-ld-matrix-freeze-code-only); plink_ld_to_npz.py and occlusion_span_filter.py keep the whole-file numstat pin as a recorded non-change"
  - "The tcujq correction is ADDITIVE and quotes the POSTED trsx5 withdrawal sentence; code and both 'pre-registered' raise strings are unchanged"
commits: [b6b1f70, b709ce1, 48b8828]
pre_head: 0231cbf97944a7d7897851bdd6e9b2043b3d6b19
authored_by_note: "Written by the ORCHESTRATOR from the executor's hand-back report: the harness refused the executor subagent's Write of this file ('Subagents should return findings as text'). Every figure below is the executor's reported measurement; verbatim raw outputs are in the scratch directory named in §9. Independently re-observed by the orchestrator where marked [ORCH]."
---

# Quick 260916-oyq — tcujq WITHDRAWN-by-trsx5 notices + code-only freeze for condition_ld_matrix.py — Summary

**Carter's decision (2026-09-16, verbatim option):** "Both files + rescope pin (Recommended)" — additive WITHDRAWN-by-trsx5 notice in the docstrings of BOTH modules (history kept, code strings untouched so the code pin stays green); condition_ld_matrix.py's freeze recorded as CODE-only (whole-file numstat assertion replaced by the existing code pin, proven able to fail); named enforcer test.

**Premise correction that triggered the decision (measured by the orchestrator before planning):** the recorded defect said the tcujq mentions were docstrings at `condition_ld_matrix.py:4,153` / `write_conditioned_ld_npz.py:4,17,85` and that docstring edits were "free" under a code-only pin. False on three counts: (1) `test_source_freeze_pins.py:194-199` was a WHOLE-FILE byte (numstat) pin, so any committed docstring edit went RED; (2) `:153`/`:200` are code strings inside `raise`, `:85` is a comment; (3) the full list is condition_ld_matrix.py docstring 1/3/26/123/130 + code-string 153/200, write_conditioned_ld_npz.py docstring 4/17/18 + comment 85. The planner further measured that trsx5:19 withdraws ONLY the isolated-pair NaN→0 branch, the zeroing ceiling and BRANCH_AFR_COND_*, while trsx5:35/:37/:39 RETAIN PSD regularization, the fully-NaN-row drop rule and the raw NaN-raise contract — so the notices are scoped to that.

## 1. Commits (branch m3-W2-aou-deltas, PRE 0231cbf)

| # | SHA | Files | Subject |
|---|---|---|---|
| C1 | `b6b1f70` | `.planning/DECISIONS.md` +127/−0, `tests/m3/test_source_freeze_pins.py` +38/−2 | rescope condition_ld_matrix.py freeze to CODE-only per DEC-2026-09-16-condition-ld-matrix-freeze-code-only |
| C2 | `b709ce1` | `tests/m3/test_tcujq_withdrawal_notices.py` +521/−0 | RED — named enforcer (ast, not grep; 9 committed negative controls + caller-scan positive controls) |
| C3 | `48b8828` | `src/python/condition_ld_matrix.py` +37/−0, `src/python/write_conditioned_ld_npz.py` +29/−0 | additive WITHDRAWN-by-trsx5 notices (code untouched; enforcer GREEN) |

`git diff --stat 0231cbf HEAD` = exactly 5 files, 752 insertions, 2 deletions [ORCH]. The pins file's two deletions are planned (the `for rel in PY_FROZEN_RELS:` header replaced; the docstring closing line reopened to append a caveat); the two original numstat statements are byte-identical. Every commit ends with the Co-Authored-By trailer. No GPFS object error. Not pushed.

## 2. Pre-flight (order per addendum O-2: a, b, d, f, then c, e)

- (a) branch correct; tracked status empty.
- (b) RAM-1 landed: last commit on run_native_ld_panel.py = `9a3eb97 fix(quick-260916-ocb)`; `test_run_plink_peak_rss.py` at HEAD; HEAD subject starts `docs(quick-260916-ocb)`.
- (d) live-pytest guard inline: `POSITIVE CONTROL -> [2202625 python -m pytest -p no:cacheprovider tests/m3 -f /dev/null]`, `REAL CHECK -> []`.
- (f) kht verifier before `$SCRATCH` existed: `RESULT GREEN checks=317 parsed=88 table=88 verified=88`.
- (e) Python 3.11.15; pre md5s condition_ld_matrix.py `f48e3c3b…`, write_conditioned_ld_npz.py `09950f23…`, pins `8fddc3c3…`.

Re-derived M1/M2/M5/M17 all matched the plan:
```
src/python/condition_ld_matrix.py {'DOCSTRING': [1, 3, 26, 123, 130], 'CODE-STRING': [153, 200], 'COMMENT': [], 'UNCLASSIFIED': []}
src/python/write_conditioned_ld_npz.py {'DOCSTRING': [4, 17, 18], 'CODE-STRING': [], 'COMMENT': [85], 'UNCLASSIFIED': []}
src/python/condition_ld_matrix.py: raise_sites=4 say_pre-registered=2 name_BRANCH_AFR_COND_DEFERRED=1 fully_NaN_row=1
src/python/write_conditioned_ld_npz.py: raise_sites=2 say_pre-registered=0 ...
M2 numstat bf16289..HEAD: [] for all 4 files
n_py: 187  n_other: 161 {'Snakefile': 2, '.sh': 65, '.R': 46, '.yml': 4, '.yaml': 5, '.smk': 39}; tools/ 0; .ipynb 0; parse failures: []
importers: {'condition_ld_matrix': ['src/python/write_conditioned_ld_npz.py'], 'write_conditioned_ld_npz': []}; non-.py text hits: none
```

## 3. Proofs that the old pin fails and the rescoped pin can fail (committed probes in `git clone --shared` scratch clones; the working tree was never a probe surface)

- **A (old assertion, committed docstring probe):** `AssertionError: src/python/condition_ld_matrix.py is NO LONGER 0-diff vs bf16289 ('1\t1\tsrc/python/condition_ld_matrix.py'); it left the measured basis for AUTH-SR4-EXTEND` — 1 failed; code pins 25 passed.
- **B1 (docstring probe, rescoped form):** rescoped 1 passed, code pins 25 passed; old form in the same clone RED.
- **B2 (raise string → `pre-registeredX`):** `AssertionError: the CODE of src/python/condition_ld_matrix.py (whole file) has MOVED off its pin bf16289.` (first difference at code-line index 34); symbol pins 1 failed / 2 passed (`test_python_symbol_code_is_frozen[src/python/condition_ld_matrix.py-condition_ld_matrix]`).
- **B3 (`ceiling_frac` 0.0005 → 0.0006):** `...has MOVED off its pin bf16289.` (index 32) — 1 failed.
- **B4 / B5 (docstring probe on plink_ld_to_npz.py / occlusion_span_filter.py):** `... is NO LONGER 0-diff vs bf16289 ('1\t1\t...')` — each 1 failed (numstat pin deliberately kept).
- Key-link `for rel in code_only:` 0 at PRE → 1 now.
- **C-i..C-iv at 48b8828:** C-i 1 passed; C-ii `37 0 src/python/condition_ld_matrix.py`; C-iii old test run in memory from PRE's text → `RED (expected): ... NO LONGER 0-diff vs bf16289 ('37\t0\t...')`; C-iv raise-string probe clone RED (`...(whole file) has MOVED off its pin bf16289`), docstring probe clone handoff 1 passed + enforcer 17 passed.

## 4. C1 real-tree checks
- pins + source_freeze: 80 passed (same as PRE, 39 + 41).
- DECISIONS.md append-only: `PREFIX-GREEN`, numstat `127 0`; negative control `NEG RED (correct, rc=1)` with 1 `>` line (a deleted `- Phase 2 (3-way QTL coloc — ...` bullet).

## 5. C2 — enforcer committed RED
```
E       AssertionError: src/python/condition_ld_matrix.py: the module DOCSTRING holds 0 WITHDRAWN POLICY NOTICE blocks, not exactly 1
E       AssertionError: src/python/write_conditioned_ld_npz.py: the module DOCSTRING holds 0 WITHDRAWN POLICY NOTICE blocks, not exactly 1
E           AssertionError: src/python/condition_ld_matrix.py::condition_ld_matrix: required token 'withdrawn' is missing from the first 7 lines of the FUNCTION docstring
3 failed, 14 passed
```
Re-observed [ORCH] in a scratch clone with src at `b709ce1`: the same 3 FAILED ids, `3 failed, 14 passed`. Cross-file gates with the new file present: 80 passed. In-memory meta-controls 18/18 (blinded asserts → all 9 controls `DID NOT RAISE`; a 1-line fixture tail trips `fixture too short for this control: BEGIN lands at docstring line(s) [4]`; wrong size/md5/line → posted-anchor RED; caller-scan floor RED; blinded `py_hits` breaks identity and the SCRIPT-PATH positive; importer detector sees `plink_ld_to_npz` importers; blinded docstring-owner rule → docstring-only negative RED).

## 6. C3 — notices, pre-commit checks and real-file controls
- N1–N4 byte-identical to the plan's `<notice_text>`; max line length 81/82/81/83; no apostrophe/backslash/triple-quote/`def ` line.
- enforcer 17 passed; numstat `37 0` / `29 0`; `TOKEN-SUBSEQUENCE: True True`; `CODE-INERT: True True` (code_lines 57=57, 21=21); both raise strings occur once, lines byte-identical; both imports print the `==== WITHDRAWN POLICY NOTICE (tcujq -> trsx5) -- READ BEFORE ANYTHING BELOW ====` banner; neighbours 104 passed; `no_nan_to_zero_conditioning_in_the_driver` 1 passed; in-memory controls detect a code edit and a deleted token.
- **Real-file controls 16/16 RED, 0 unexpected** (unmutated GREEN first): per module — removed / moved into a comment / moved into a string constant → `holds 0 ... not exactly 1`; token misspelled → `required token 'trsx5'...`; posted sentence altered → `the verbatim POSTED trsx5 withdrawal sentence is missing...`; moved to docstring end → `the notice begins at docstring line 48 (> 4) -- not prominent` (37 for write_conditioned_ld_npz.py); duplicated → `holds 2 ... not exactly 1`. Function notice removed / moved into a comment → `required token 'withdrawn' is missing from the first 7 lines of the FUNCTION docstring`.
- [ORCH] at HEAD: enforcer + pins + source_freeze + test_condition_ld_matrix + test_write_conditioned_ld_npz = 121 passed. The orchestrator also read the notice against the posted trsx5 body (quote = posted line 19; retained rules = lines 35/37/39) and `osf_deviations.md:104`/`:155` timestamps.

## 7. Full-suite reconciliation by test id (rule R1: no pytest anywhere while a suite ran)
- PRE: `1212 passed, 33 skipped, 4 warnings in 807.12s (0:13:27)`, EXIT=0 (1245 testcases).
- POST: `1229 passed, 33 skipped, 4 warnings in 813.73s (0:13:33)`, EXIT=0 (1262 testcases).
- REMOVED 0, CHANGED 0, ADDED 17 — all `tests.m3.test_tcujq_withdrawal_notices::*`, all passed; `RECONCILE: OK`. No flake in `test_run_plink_peak_rss.py`.
- Reconciler self-controls: identity `--expect-added 0` exit 0; one flipped testcase → `~ tests.m3.test_aou_export_landing::test_npz_count_per_ancestry_matches_inventory: passed -> failed`, exit 1; synthetic PRE+17 passed → OK; one of them failed → FAIL; one PRE key removed → FAIL.
- kht verifier after the last commit: `RESULT GREEN checks=317 parsed=88 table=88 verified=88`, identical to pre-flight. The plan's literal Task 3 verify block exits 0.
- **Tracked benchmark TSV:** both full runs rewrote `tests/m3/sparse_parent_benchmark.tsv` (numstat `1 1`, timing columns only: PRE `read_s 1.133→0.996`, `densify_window_s 0.236→0.156`; POST `read_s 1.133→0.973`, `densify_window_s 0.236→0.153`). Each saved + diffed to scratch and restored with exactly `git checkout -- tests/m3/sparse_parent_benchmark.tsv`; clean-tree guards ran after the restore.

## 8. Deviations and contradictions
1. **Reconcile self-control contradiction in the plan:** Step 7 required `reconcile.py suite_pre.xml suite_pre.xml` → exit 0, but the script may only exit 0 when exactly 17 are added (literal spec gave `RECONCILE: FAIL -- 0 added, not 17`, kept as `reconcile.v1.py`). Added optional `--expect-added N` (default 17) used ONLY for self-controls; the real reconciliation used the default.
2. **Stale line citation in the plan:** the wrong "docstring edits are free" premise sits at STATE.md:**82** at PRE, not :61 (RAM-1's close-out inserted lines above it). HANDOFF.json:261 still correct. The DECISIONS entry cites both "at `0231cbf`".
3. **Executor's own meta-control expectation was wrong:** a bare `assert` outside pytest carries no message, so one blinded check printed "RED-BUT-WRONG-MESSAGE"; switched to exception-type matching with the discriminating value printed; re-ran 18/18.
4. **This SUMMARY was written by the orchestrator** (harness blocked the subagent's Write); nothing was worked around by the executor.
5. Recorded per plan: M3 committed probes only in clones; M4 notices scoped to trsx5:19 with retained :35/:37/:39 named; **M8** "Every pin here is a CODE pin" (pins docstring) and sr4's "deliberately outside every freeze gate" were FALSE for all three frozen modules and stay false for the other two — the pins docstring now carries a caveat; **M9** all pre-C3 line citations into the two src files are stale (+31 below the module notice in condition_ld_matrix.py, +28 in write_conditioned_ld_npz.py), incl. the STATE/HANDOFF item-3 text; M13/M14 `ps`/`awk` guard and widened clone checkout used.

## 9. Evidence location
Raw outputs (verbatim): `/gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916/` — `m1_m2_m5.txt`, `proof_A.txt`, `proof_B.txt`, `proof_C.txt`, `c2_red.txt`, `c2_crossfile.txt`, `c2_meta_controls*.txt`, `c3_precommit.txt`, `real_file_controls.txt`, `suite_pre.{log,xml}`, `suite_post.{log,xml}`, `reconcile_output.txt`, `reconcile.py` / `reconcile.v1.py`, `kht_pre.txt` / `kht_post.txt`, `sparse_parent_benchmark.{pre,post}_run.{tsv,diff}`, `dec_pre.md` / `dec_neg.md`, `lib.sh`, `PRE`, `expected_head`. `clones/` is empty.

## 10. Observations for Carter (not decided)
- `plink_ld_to_npz.py` and `occlusion_span_filter.py` keep the whole-file numstat pin by the recorded decision; a committed docstring-only fix to either is still RED (Proofs B4/B5) — the same proxy-vs-property question applies and would need its own decision.
- Refresh `HANDOFF.json:261` and `STATE.md` item 3 wording ("docstring edits are free", `:4,153`) — superseded by this task.

## Known Stubs
None.

## Threat Flags
None.

## Self-Check
Commits b6b1f70 / b709ce1 / 48b8828 FOUND on branch; 5-file diff FOUND [ORCH]; tracked tree clean [ORCH]; enforcer RED-on-pre-notice / GREEN-at-HEAD re-observed [ORCH]; independent gsd-verifier: status PASSED 11/11 (see 260916-oyq-VERIFICATION.md), incl. its own mutations (notice moved into another function docstring, one-hyphen and date-token edits, same-size posted-body edit, staged importer / .smk / bin/ subprocess path) all RED. Known limits recorded by the verifier: the caller scan does not see dynamic imports (importlib) or untracked files (documented in the enforcer docstring; none exist today).
