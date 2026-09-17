---
phase: quick-260916-oyq
plan: 01
type: execute
wave: 1
depends_on: []            # ordering constraint is ENFORCED in Task 1 pre-flight: quick-260916-ocb (RAM-1) fix + close-out must already be committed
mode: quick-full
branch: m3-W2-aou-deltas
worktree: none            # GPFS: worktrees disabled project-wide. Scratch CLONES (git clone --shared) live OUTSIDE the repo.
autonomous: true
push: false               # commit only; the orchestrator commits PLAN/SUMMARY/STATE afterwards
requirements: ["QUICK-260916-oyq"]   # STATE.md RESUME item 3 (tcujq docstring defect) + Carter decision 2026-09-16 "Both files + rescope pin (Recommended)"
revision: 1               # plan-checker round 1 adopted (see <revision_log>)

files_modified:
  - tests/m3/test_source_freeze_pins.py            # C1: ONE assertion rescoped + its comments/docstrings (Task 1)
  - .planning/DECISIONS.md                         # C1: APPEND one entry at EOF (Task 1)
  - tests/m3/test_tcujq_withdrawal_notices.py      # C2: CREATED, the named enforcer, committed RED (Task 2)
  - src/python/condition_ld_matrix.py              # C3: DOCSTRING TEXT ONLY, additive (Task 3)
  - src/python/write_conditioned_ld_npz.py         # C3: DOCSTRING TEXT + ONE NEW COMMENT LINE, additive (Task 3)
  - .planning/quick/260916-oyq-tcujq-withdrawn-by-trsx5-notices-in-cond/260916-oyq-SUMMARY.md   # CREATED, NOT committed by the executor

files_frozen:
  - src/python/plink_ld_to_npz.py                  # keeps its whole-file numstat pin (recorded non-change)
  - src/python/occlusion_span_filter.py            # keeps its whole-file numstat pin (recorded non-change)
  - src/python/run_native_ld_panel.py              # owned by quick-260916-ocb
  - src/python/fire_verifier.py
  - tests/m3/source_freeze.py                      # REUSE assert_code_frozen; never edit, never re-implement a stripper
  - tests/m3/test_source_freeze.py
  - tests/m3/test_run_plink_peak_rss.py            # owned by quick-260916-ocb
  - .planning/amendments/**                        # posted OSF bodies, NEVER edited
  - .planning/osf_deviations.md
  - .planning/HANDOFF.json
  - .planning/STATE.md                             # the ORCHESTRATOR updates STATE.md
  - .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt
  - .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/**
  - everything else not listed in files_modified

must_haves:
  truths:
    - "Pre-flight passes only when: RAM-1's `fix(quick-260916-ocb)` commit is the last commit touching src/python/run_native_ld_panel.py, tests/m3/test_run_plink_peak_rss.py exists at HEAD, HEAD's subject starts `docs(quick-260916-ocb)`, the live-pytest guard is silent AFTER its fake-process positive control was observed, and the kht verifier default mode is GREEN before any change"
    - "The MODULE docstring of BOTH src/python/condition_ld_matrix.py and src/python/write_conditioned_ld_npz.py (as returned by ast.get_docstring) contains exactly one WITHDRAWN POLICY NOTICE block that begins within the first 5 docstring lines, whose BODY names tcujq, trsx5, 2026-07-04, 2026-07-10, exclude-in-lockstep, 'not called by the pipeline' and DEC-2026-09-16-condition-ld-matrix-freeze-code-only, and contains the whitespace-normalized POSTED trsx5 withdrawal sentence (posted body line 19, up to 'is withdrawn.')"
    - "The FUNCTION docstring of condition_ld_matrix.condition_ld_matrix carries a short withdrawal notice (withdrawn / tcujq / trsx5 / 2026-07-10 / pointer to the module WITHDRAWN POLICY NOTICE / the retained fully-NaN-row rule) in its first 7 lines"
    - "The notice edits are purely ADDITIVE and code-inert: `git diff --numstat <PRE> HEAD` shows 0 deleted lines for both src files; PRE's whitespace token sequence is a subsequence of HEAD's for both; source_freeze.code_lines(...) is identical PRE vs HEAD for both files; the two raise-message f-strings that say 'pre-registered' are byte-unchanged"
    - "test_the_handoff_frozen_claim_is_recorded_as_partly_false holds condition_ld_matrix.py to assert_code_frozen(rel, PY_CODE_REF, LANG_PY) inside a `for rel in code_only:` loop and keeps the whole-file numstat assertion for EXACTLY plink_ld_to_npz.py and occlusion_span_filter.py; PY_CODE_REF == 'bf16289', PY_FROZEN_RELS, the 22-symbol derivation and every other test in the file are unchanged"
    - "The rescoped assertion is PROVEN able to fail, observed in scratch clones (never the working tree) and never while a full-suite run is live: a COMMITTED docstring-only edit to condition_ld_matrix.py is RED under the OLD form and GREEN under the rescoped form; a committed one-token CODE edit (the raise-message text; the ceiling_frac default) is RED under the rescoped form; a committed docstring-only edit to plink_ld_to_npz.py or occlusion_span_filter.py is still RED. After C3, the OLD form, executed from PRE's file text against the real repo, is RED, and a code-token probe on the post-notice file is RED under the rescoped form"
    - "tests/m3/test_tcujq_withdrawal_notices.py is RED at its own commit (exactly the 3 positive notice tests; 3 failed / 14 passed) and fully GREEN (17 passed) after C3, both in the real repo and in a scratch clone. Its committed negative controls (removed / moved into a # comment / moved into a module-level string constant / body token misspelled / quoted sentence altered / moved to docstring end / duplicated / function notice removed / function notice moved into a comment) each raise the SPECIFIC expected AssertionError. The same mutations applied in-memory to the REAL post-C3 file texts are all observed RED (16/16)"
    - "Neither module has a caller in any tracked pipeline file (Snakefile, src/, scripts/, bin/, tools/). This is enforced by the new test with a must-be-identity non-vacuity (the only importer of condition_ld_matrix is src/python/write_conditioned_ld_npz.py) AND positive controls for both other detectors: m3_occlusion_lockstep.smk is a text hit for occlusion_span_filter, run_ld_build_plan.py is a script-path hit for build_ld_rds, and a docstring-only mention is NOT a script-path hit"
    - ".planning/DECISIONS.md gains exactly one appended entry DEC-2026-09-16-condition-ld-matrix-freeze-code-only (premise correction measured incl. working-tree-vs-commit semantics, Carter's verbatim choice, what changes, what does NOT change incl. plink_ld_to_npz.py + occlusion_span_filter.py named, observation for Carter, cross-refs). The file's first byte-length(PRE) bytes are byte-identical to PRE's DECISIONS.md and the file is longer, with 0 deletions in numstat; the prefix check was observed RED on a bullet-deleted scratch copy"
    - "Full tests/m3 reconciled BY NAME between the PRE baseline and the final HEAD: 0 removed, 0 outcome changes, and exactly 17 added test ids, all in tests/m3/test_tcujq_withdrawal_notices.py and all passed"
    - "260916-kht-verify.py default mode prints `RESULT GREEN checks=317 parsed=88 table=88 verified=88` both at pre-flight and after the last commit"
  artifacts:
    - path: "tests/m3/test_tcujq_withdrawal_notices.py"
      provides: "named enforcer: ast module/function docstring notice checks + posted-trsx5 byte anchor + pipeline-caller scan with positive controls + committed negative controls"
      contains: "c19be8b2ad7cd6a45fee1d668d8a9cf9"
    - path: "tests/m3/test_source_freeze_pins.py"
      provides: "rescoped test_the_handoff_frozen_claim_is_recorded_as_partly_false (condition_ld_matrix.py -> CODE pin; other two keep numstat)"
      contains: "DEC-2026-09-16-condition-ld-matrix-freeze-code-only"
    - path: "src/python/condition_ld_matrix.py"
      provides: "additive WITHDRAWN-by-trsx5 notice in module + condition_ld_matrix() docstrings"
      contains: "==== WITHDRAWN POLICY NOTICE (tcujq -> trsx5)"
    - path: "src/python/write_conditioned_ld_npz.py"
      provides: "additive WITHDRAWN-by-trsx5 notice in module docstring + one comment line at the conditioning call"
      contains: "==== WITHDRAWN POLICY NOTICE (tcujq -> trsx5)"
    - path: ".planning/DECISIONS.md"
      provides: "the recorded decision"
      contains: "## 2026-09-16 — DEC-2026-09-16-condition-ld-matrix-freeze-code-only"
  key_links:
    - from: "tests/m3/test_source_freeze_pins.py::test_the_handoff_frozen_claim_is_recorded_as_partly_false"
      to: "tests/m3/source_freeze.py::assert_code_frozen"
      via: "reused call for condition_ld_matrix.py only, inside the new code_only loop (no stripper re-implemented, no actual_text seam). Pattern measured ABSENT at PRE (0 hits), unlike the bare call which already matches :145"
      pattern: "for rel in code_only:"
    - from: "tests/m3/test_tcujq_withdrawal_notices.py"
      to: ".planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt"
      via: "size 9695 FIRST, then md5 c19be8b2…, then splitlines()[18] up to 'is withdrawn.'"
      pattern: "POSTED_TRSX5_MD5"
    - from: "tests/m3/test_tcujq_withdrawal_notices.py"
      to: "src/python/condition_ld_matrix.py, src/python/write_conditioned_ld_npz.py"
      via: "ast.parse + ast.get_docstring(clean=True), never a text grep"
      pattern: "ast\\.get_docstring"
---

<objective>
Correct the tcujq docstring defect honestly and permanently, exactly as Carter chose on
2026-09-16 (~17:45 EDT, AskUserQuestion). His verbatim option was **"Both files + rescope pin
(Recommended)"**: *"Additive WITHDRAWN-by-trsx5 notice in the docstrings of BOTH modules (history
kept, code strings :153/:200 untouched so the code pin stays green). Records a decision that
condition_ld_matrix.py's freeze is CODE-only: replace its whole-file numstat assertion at :194-199
with the existing code pin, proven able to fail. Named enforcer test for the notices. Matches the
scope-a-guard-to-the-property rule."*

Three atomic commits, TDD order:
- **C1** (Task 1): record `DEC-2026-09-16-condition-ld-matrix-freeze-code-only` and rescope the ONE
  numstat assertion for `condition_ld_matrix.py` to its CODE pin. Prove it can fail BEFORE committing.
- **C2** (Task 2): the named enforcer `tests/m3/test_tcujq_withdrawal_notices.py`, committed RED.
- **C3** (Task 3): the additive notices, docstrings only. Code, code strings, imports, constants,
  signatures and behaviour stay untouched. The enforcer turns GREEN. Then run the post-commit proofs,
  the full-suite by-name reconciliation and the kht verifier (must stay GREEN), and write the SUMMARY.

Purpose: "pre-registered" was TRUE when written (tcujq, OSF 2026-07-04), and trsx5 (OSF 2026-07-10)
later WITHDREW the policy. Deleting the historical wording would falsify the record, and leaving it
unannotated misleads. The honest correction is an additive notice with a named enforcer. The old freeze
made that docstring edit cost a red test, which means it was guarding a byte proxy instead of the property.

Output: 3 commits on `m3-W2-aou-deltas`, `260916-oyq-SUMMARY.md` (uncommitted), no push.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<execution_rules>
These apply to EVERY step of EVERY task.
- **R1: no concurrent pytest.** While a background full-suite run (PRE or POST) is live, run NO pytest anywhere, in the
  real tree or in a scratch clone. Only read-only Python/git scripts are allowed. Load could flake RAM-1's RSS/timing tests.
  "Live" means the run's log has no `EXIT=` line yet.
- **R2: every STOP cleans its clones.** On ANY STOP, once `$SCRATCH/lib.sh` exists, run `source $SCRATCH/lib.sh && cleanup_clones`
  before reporting. It is path-guarded and removes `$SCRATCH/clones/*` only. Keep `$SCRATCH` itself (PRE, logs, XML) for
  diagnosis, and say in the report whether a background suite run was still live at STOP time.
- **R3: commit hygiene.** Before every commit, HEAD must equal `$SCRATCH/expected_head`. Stage explicit paths only (never
  `git add .`/`-A`), and `git diff --cached --name-only` must equal exactly the task's files. A GPFS "invalid object" or
  "Error building trees" = STOP (no recovery attempt). Every commit message ends with a blank line +
  `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
- **R4: the real working tree is never a probe surface.** All perturbation probes run in `mkclone` scratch clones or in memory.
</execution_rules>

<context>
@./CLAUDE.md
@src/python/condition_ld_matrix.py
@src/python/write_conditioned_ld_npz.py
@tests/m3/test_source_freeze_pins.py
@.planning/DECISIONS.md   (read ONLY the last ~120 lines for entry format; the sr4 entry starts at `## 2026-08-06 — DEC-2026-08-06-sr4-freeze-scope`)
@.planning/osf_deviations.md   (lines 95-189 only: the tcujq posting + the trsx5 withdrawal record)
@.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt   (lines 17-19 and 35-39 only)

<measured_by_planner at="11f61e8, 2026-09-16 (M1-M12 initial; M13-M18 revision 1)">
Re-measure M1/M2/M5 at execution time (Task 1 Step 3). The SUMMARY must carry the executor's OWN
outputs, not these.

M1. Classification of every "pre-registered"/"pre-registration" occurrence (ast docstring spans +
    tokenize). It matches the orchestrator's brief exactly:
    condition_ld_matrix.py      DOCSTRING 1, 3, 26, 123, 130 · CODE-STRING (f-strings in `raise ValueError`) 153, 200
    write_conditioned_ld_npz.py DOCSTRING 4, 17, 18 · COMMENT 85
    ⇒ the recorded defect list (`condition_ld_matrix.py:4,153`, `write_conditioned_ld_npz.py:4,17,85`) was INCOMPLETE.
M2. `git diff --numstat bf16289 HEAD --` is EMPTY for condition_ld_matrix.py, write_conditioned_ld_npz.py,
    plink_ld_to_npz.py and occlusion_span_filter.py.
M3. THE PREMISE WAS WRONG, and the brief's suggested working-tree method CANNOT show it. The old assertion
    (test_source_freeze_pins.py:194-199) runs `git diff --numstat PY_CODE_REF HEAD -- rel`, which compares
    COMMIT to COMMIT. A working-tree-only edit leaves it GREEN; only a COMMITTED edit turns it RED. Measured in a
    `git clone --shared` scratch clone (2.1 s): a committed docstring-only probe on condition_ld_matrix.py gave
    `AssertionError: src/python/condition_ld_matrix.py is NO LONGER 0-diff vs bf16289 ('1\t1\tsrc/python/condition_ld_matrix.py')`
    (1 failed), while the 3 module + 22 symbol CODE pins stayed GREEN (25 passed). In the same clone,
    test_source_freeze.py + test_condition_ld_matrix.py + test_write_conditioned_ld_npz.py gave 65 passed.
    ⇒ This plan does ALL probes in scratch clones and NEVER temporarily edits the shared working tree,
    so the .pyc mtime/size trap cannot arise in the real tree.
    The rescoped `assert_code_frozen` reads the WORKING TREE for its actual side, while the old numstat compared two COMMITS.
M4. trsx5 does NOT withdraw everything this module does. The posted body is 9,695 B, md5 c19be8b2…, 59 lines with
    NO trailing newline (count with str.splitlines(), never `wc -l`):
      line 19: "The off-diagonal NaN→0 conditioning of isolated pairwise-undefined entries (prior amendment tcujq item (a) isolated-off-diagonal-pair branch and item (b) the per-region zeroing ceiling), together with its BRANCH_AFR_COND_CLEAN / BRANCH_AFR_COND_APPLIED / BRANCH_AFR_COND_DEFERRED outcome branches, is withdrawn." (followed by " Rationale: …" on the same line)
      Line 35 RETAINS PSD regularization. Line 37 RETAINS "The fully-NaN-row → drop rule", which this module's
      fully-NaN-row RAISE branch enforces by directing an upstream MAF/missingness drop. Line 39 RETAINS the raw-panel
      NaN-raise contract.
    ⇒ The notice must say that the isolated-pair zeroing, the zeroing ceiling and BRANCH_AFR_COND_* are withdrawn,
    NOT that "the module" is withdrawn wholesale. The repo trsx5 draft's copy of this sentence (amendments :51) is
    byte-identical, so there is no discrepancy, but the quote is still sourced ONLY from the posted file.
M5. Callers: tracked `Snakefile src/ scripts/ bin/ tools/` hold 187 .py files (all parse under py3.11) and 161
    .smk/.sh/.R/.yaml/.yml/Snakefile files (0 tracked .ipynb; 0 tracked files under tools/). The ONLY importer of
    `condition_ld_matrix` is `src/python/write_conditioned_ld_npz.py`. Nothing imports or names
    `write_conditioned_ld_npz`, and non-.py pipeline files have zero text hits.
M6. HAZARDS in tests/m3/test_source_freeze.py, which reads condition_ld_matrix.py's TEXT. All stay GREEN under the
    notice design below (verified: 104 passed across test_source_freeze.py, test_source_freeze_pins.py,
    test_condition_ld_matrix.py and test_write_conditioned_ld_npz.py with the final notice text applied):
    - `test_a_docstring_only_edit_is_invisible`: the module docstring's FIRST line must stay non-blank and occur
      EXACTLY ONCE in the file ⇒ keep line 1 as-is and never repeat it.
    - `_py_concealment_fixtures`: `real.index("\ndef ") + 1` ⇒ NO docstring line may start with `def ` at column 0.
    - `test_the_python_mask_stripper_agrees_with_the_ast_canonicaliser` compares a hand scanner with ast ⇒ NO
      backslashes, NO `"""` or `'''`, and (belt-and-braces) NO apostrophes inside the notice text.
M7. `test_no_production_call_site_supplies_the_control_seam` (an AST walk of every tests/m3/*.py) forbids any call to
    `assert_code_frozen`/`assert_unchanged_on_disk` with `actual_text=` or `**kwargs` outside test_source_freeze.py.
    `test_every_pin_constant_declares_its_bucket` scans module-level `str` constants named `*_REF`/`*_REV`/
    `BASE_COMMIT`/`BASELINE_REV` in every tests/m3/*.py ⇒ the new test file must define NO such names.
M8. `test_source_freeze_pins.py`'s module docstring says "Every pin here is a CODE pin", and
    DEC-2026-08-06-sr4-freeze-scope says docstrings are "deliberately outside every freeze gate". Both were FALSE for
    all three PY_FROZEN_RELS while :194-199 existed, and both stay false for plink_ld_to_npz.py + occlusion_span_filter.py
    after this task. HANDOFF.json:261 and STATE.md:61 carry the wrong "docstring edits are FREE" premise
    (orchestrator-owned; NOT edited here).
M9. Line numbers WILL shift once the notices are inserted ⇒ no new comment, docstring or notice may cite a line number
    of condition_ld_matrix.py / write_conditioned_ld_npz.py. DECISIONS may cite those lines only as "at <PRE sha>".
M10. Full tests/m3 takes about 14 min (1187 passed / 33 skipped at 2026-09-02), more than the 10-min Bash cap ⇒ run it in the background.
M11. `260916-kht-verify.py` default mode today prints `RESULT GREEN checks=317 parsed=88 table=88 verified=88` (5.9 s).
     It cites none of this task's files.
M12. The repo has no `.git/hooks` directory and no `core.hooksPath` ⇒ the RED commit C2 is not blocked by a hook.
M13. LIVE-PYTEST GUARD. `pgrep -u "$USER" -af 'pytest.*tests/m3'` matches its OWN `bash -c` wrapper (measured rc=0 and a hit
     with no pytest running) ⇒ unusable. `ps -u "$USER" -o pid=,args= | awk '$2 ~ /python/ && / -m pytest/ && /tests\/m3/'`
     prints nothing with no pytest running, even from a shell whose own command line contains those words. Positive control
     measured: `( exec -a "python -m pytest -p no:cacheprovider tests/m3" tail -f /dev/null ) &` was detected
     (`… python -m pytest -p no:cacheprovider tests/m3 -f /dev/null`), and the guard was silent again after `kill`.
     W4 checks at 11f61e8 (RAM-1 not yet landed) all FAIL as they must; the same command forms succeed on known positives
     (`docs(quick-260916-kht)` subject at HEAD; `git cat-file -e HEAD:tests/m3/test_source_freeze_pins.py`).
M14. CLONE COVERAGE. A clone with only `tests src config` checked out runs the enforcer as `16 failed, 1 passed`, because the
     enforcer reads the posted trsx5 body and Snakefile/scripts/bin. `git checkout HEAD -- tools` errors with
     `pathspec 'tools' did not match any file(s) known to git`. With `tests src config Snakefile scripts bin <posted trsx5 file>`
     checked out, the prototype enforcer gives `3 failed, 14 passed` with notices absent and `17 passed` with them applied.
M15. CALLER-SCAN POSITIVES (same detector code, other stems). Text hits for `occlusion_span_filter` =
     {`src/snakemake/rules/m3_occlusion_lockstep.smk`}. Script-path hits for `build_ld_rds` ⊇
     {`src/legacy/region_analysis/scripts/run_ld_build_plan.py` (code string `"scripts/build_ld_rds.py"`; its docstring ALSO
     names the file), `src/legacy/region_analysis/tmp_run_tiles.py`}.
M16. APPEND-ONLY CHECK. `git diff | grep -c '^-[^-]'` returns 0 for BOTH a deleted `- ` bullet and a deleted blank line (blind).
     The byte-prefix check (below, `dec_prefix_check`) is RED for both, GREEN for a pure append, and RED for an unchanged file
     (it also requires the file to be longer). `sed -i '0,/^- /{/^- /d}'` deletes exactly 1 line (the first bullet).
M17. RAISE SITES in condition_ld_matrix.py: 4 in total. Exactly 2 messages contain "pre-registered" (the unsupported-policy
     raise and the over-ceiling raise), exactly 1 contains BRANCH_AFR_COND_DEFERRED (the over-ceiling raise, one of those
     two), and 1 is the fully-NaN-row raise. write_conditioned_ld_npz.py has 2 raise sites and neither says "pre-registered".
M18. PLANNER PROTOTYPE of the full enforcer spec, run in scratch clones:
     - RED state `3 failed, 14 passed` (exactly the 3 positive notice tests); GREEN state `17 passed`.
     - Code-inert and token-subsequence True for both files; both raise strings present exactly once.
     - 16/16 real-file mutations RED with matching messages (e.g. `… the notice begins at docstring line 48 (> 4) -- not prominent`).
     - W3 confirmed: without the blank line after the fixture See-line, `function_notice_removed` yields
       `SyntaxError: unterminated triple-quoted string literal`.
     - FOUND BY THE PROTOTYPE: with a one-line historical tail, the synthetic `moved_to_docstring_end` control lands the notice
       at docstring line 4 (≤ 4) and DID NOT RAISE. The fixture needs a longer tail, and the control must assert its own
       premise. Both are specified below.
</measured_by_planner>

<interfaces>
From tests/m3/source_freeze.py (REUSE; never edit, never re-implement):
```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
LANG_PY = "py"
def code_lines(text: str, lang: str) -> list[str]          # ast: docstrings+comments stripped, code string constants KEPT
def assert_code_frozen(rel_path: str, ref: str, lang: str, symbol: str | None = None, *,
                       actual_text: str | None = None, pin_constant: str | None = None) -> None
    # ACTUAL side = WORKING TREE read_text(); REFERENCE = git show <ref>:<rel>; raises
    # AssertionError("...the CODE of <rel> (whole file) has MOVED off its pin <ref>...first difference...")
def git_show(ref: str, rel_path: str) -> str
```
From tests/m3/test_source_freeze_pins.py (already imported there: LANG_PY, LANG_R, PROJECT_ROOT, assert_code_frozen, git_show):
```python
PY_CODE_REF = "bf16289"
PY_FROZEN_RELS = ("src/python/plink_ld_to_npz.py", "src/python/condition_ld_matrix.py", "src/python/occlusion_span_filter.py")
def _git(*args: str) -> subprocess.CompletedProcess        # cwd=PROJECT_ROOT
def test_the_handoff_frozen_claim_is_recorded_as_partly_false():   # lines 178-199 at PRE; the ONLY function edited
```
</interfaces>

<scratch_and_probe_library>
Fixed scratch root, OUTSIDE the repo: `SCRATCH=/gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916`.
Create `$SCRATCH/lib.sh` with the Write tool in Task 1 Step 1 and `source` it at the top of every Bash call that needs it
(shell state does not persist between calls):

```bash
REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
SCRATCH=/gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916
PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
POSTED_TRSX5=.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt
export PYTHONDONTWRITEBYTECODE=1
live_pytest() {   # prints any live `python -m pytest … tests/m3` of this user; silent = none (M13; never use pgrep here)
  ps -u "$USER" -o pid=,args= | awk '$2 ~ /python/ && / -m pytest/ && /tests\/m3/'
}
mkclone() {   # mkclone NAME -> echoes the clone path; clone == REPO's CURRENT HEAD. Checks out EVERYTHING any probe reads
              # (M14): tests src config + Snakefile scripts bin (enforcer caller scan) + the posted trsx5 body.
              # NOT tools: no tracked files, the pathspec errors.
  local c="$SCRATCH/clones/$1"
  case "$c" in "$SCRATCH"/clones/?*) ;; *) echo "REFUSING clone path $c" >&2; return 1 ;; esac
  rm -rf -- "$c"
  git clone -q --shared --no-checkout "$REPO" "$c" \
    && git -C "$c" reset -q \
    && git -C "$c" checkout HEAD -- tests src config Snakefile scripts bin "$POSTED_TRSX5" || return 1
  [ "$(git -C "$c" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse HEAD)" ] || { echo "CLONE HEAD MISMATCH" >&2; return 1; }
  echo "$c"
}
cleanup_clones() {   # R2: removes scratch clones ONLY
  case "$SCRATCH" in /gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916) rm -rf -- "$SCRATCH/clones"; mkdir -p "$SCRATCH/clones" ;; *) echo "REFUSING cleanup of $SCRATCH" >&2; return 1 ;; esac
}
probe_commit() {   # probe_commit CLONE REL OLD NEW: exact ONE-occurrence replace, committed IN THE CLONE ONLY
  "$PY" - "$1/$2" "$3" "$4" <<'EOF'
import sys
p, old, new = sys.argv[1:4]
t = open(p, encoding="utf-8").read()
assert t.count(old) == 1, f"probe anchor occurs {t.count(old)} times in {p}"
open(p, "w", encoding="utf-8").write(t.replace(old, new, 1))
EOF
  git -C "$1" -c user.name=oyq-probe -c user.email=oyq-probe@example.invalid commit -q -m "oyq probe" -- "$2" || return 1
  git -C "$1" diff --numstat HEAD~1 HEAD
}
pins() {   # pins CLONE TESTFILE KEXPR: prints the E-lines and the summary line
  (cd "$1" && "$PY" -m pytest -p no:cacheprovider -q "$2" -k "$3" 2>&1 | grep -E "^E +|[0-9]+ (passed|failed)" | head -12)
}
dec_prefix_check() {   # dec_prefix_check FILE: success iff FILE begins with PRE's DECISIONS.md bytes AND is strictly longer (M16)
  git -C "$REPO" show "$(cat "$SCRATCH/PRE")":.planning/DECISIONS.md > "$SCRATCH/dec_pre.md" || return 2
  local n; n=$(stat -c %s "$SCRATCH/dec_pre.md")
  head -c "$n" "$1" | cmp -s - "$SCRATCH/dec_pre.md" && [ "$(stat -c %s "$1")" -gt "$n" ]
}
```
Probe anchors (each measured to occur EXACTLY once at PRE, and still exactly once after the notices land):
- DOC_CLM (docstring-only, condition_ld_matrix.py): `"""Pre-registered AFR native-plink LD NaN conditioning (ROADMAP 999.1 §3).` → append ` [oyq docstring-only probe]`
- STR_153 (code string): `f"is pre-registered (osf-amendment-afr-native-ld-nan-psd-2026-07-03.md)."` → `f"is pre-registeredX (osf-amendment-afr-native-ld-nan-psd-2026-07-03.md)."`
- CONST (code constant): `ceiling_frac: float = 0.0005,` → `ceiling_frac: float = 0.0006,`
- DOC_PLINK: `"""plink_ld_to_npz.py -- m3-02e Move 1: convert a NATIVE plink1.9 per-region LD` → append ` [oyq probe]`
- DOC_OCC: `"""Overlapping-deletion REFERENCE-OCCLUSION span filter (m3-07b, T1).` → append ` [oyq probe]`
</scratch_and_probe_library>

<notice_text>
The EXACT text to insert (Task 3). Keep every line exactly as written below. Hyphenated tokens and the DEC id must NOT
be broken across lines, because the enforcer compares whitespace-normalized text. Non-ASCII: `→` (U+2192) appears only
inside the quoted sentence and in "NaN→0 is prohibited". Both files are already UTF-8 (they contain `§` and `—`).
All four blocks were verified by the planner prototype (M18): no line longer than 88 characters, no apostrophe, no backslash,
no line starting `def `.

N1: condition_ld_matrix.py MODULE docstring. Insert the block below (including its trailing blank line) immediately
BEFORE the line that starts ``` ``condition_ld_matrix`` applies the off-diagonal```, i.e. after the blank line that
follows the title line. The STATUS counts are exact per M17:

```
==== WITHDRAWN POLICY NOTICE (tcujq -> trsx5) -- READ BEFORE ANYTHING BELOW ====

The isolated-pair off-diagonal ``NaN -> 0`` zeroing and the per-region zeroing
ceiling that this module implements WERE pre-registered: OSF file tcujq on az52u,
posted 2026-07-04T04:14:46Z. They were then WITHDRAWN by the amendment-update OSF
file trsx5 on az52u, posted 2026-07-10T13:32:22Z. The posted trsx5 body, under
"What is withdrawn:", reads:

    The off-diagonal NaN→0 conditioning of isolated pairwise-undefined entries
    (prior amendment tcujq item (a) isolated-off-diagonal-pair branch and item
    (b) the per-region zeroing ceiling), together with its
    BRANCH_AFR_COND_CLEAN / BRANCH_AFR_COND_APPLIED / BRANCH_AFR_COND_DEFERRED
    outcome branches, is withdrawn.

The replacement pre-registered by trsx5 is overlapping-deletion occlusion
exclude-in-lockstep (LD panel AND harmonized summary statistics) with a mandatory
provenance manifest; NaN→0 is prohibited. trsx5 RETAINS, unchanged, the
fully-NaN-row drop rule (this module raises on a fully-NaN row), the PSD
regularization methods, and the raw-panel NaN-raise contract.

STATUS: this module is retained FROZEN / HELD as a historical record and is NOT
called by the pipeline. Two of the four error-message strings at its ``raise``
sites still say "pre-registered", and one of those two also names
BRANCH_AFR_COND_DEFERRED. These strings are CODE under the source-freeze pin
(tests/m3/test_source_freeze_pins.py) and are deliberately left unchanged --
read them in light of this withdrawal. The text below this notice is the
original 2026-07 wording, kept as written. Recorded:
DEC-2026-09-16-condition-ld-matrix-freeze-code-only (quick-260916-oyq).

==== END WITHDRAWN POLICY NOTICE ====

```

N2: condition_ld_matrix() FUNCTION docstring. Insert the block below (4-space indented, including its trailing blank
line) immediately BEFORE the line `    Parameters` that follows
`    """Apply the pre-registered off-diagonal ``NaN -> 0`` conditioning to ``m``.` and its blank line. The last sentence is
the retained-rule pointer (trsx5:37; the function raises on a fully-NaN row and directs an upstream MAF/missingness drop).
All tokens sit in docstring lines 2-6, inside the 7-line window:

```
    WITHDRAWN POLICY: this conditioning (tcujq, OSF 2026-07-04) was WITHDRAWN by
    trsx5 (OSF 2026-07-10) and replaced by occlusion exclude-in-lockstep; this
    function is NOT called by the pipeline. See the WITHDRAWN POLICY NOTICE in the
    module docstring. Its fully-NaN-row raise is NOT part of the withdrawal: trsx5
    retains the fully-NaN-row drop rule that this raise directs.

```

N3: write_conditioned_ld_npz.py MODULE docstring. Insert the block below (including its trailing blank line)
immediately BEFORE the line that starts ``` ``write_conditioned_npz`` runs ```, i.e. after the blank line that follows
the two-line title ending `(m3-06-W6-T3, ROADMAP 999.1 §4).`:

```
==== WITHDRAWN POLICY NOTICE (tcujq -> trsx5) -- READ BEFORE ANYTHING BELOW ====

The conditioning this module banks -- the isolated-pair off-diagonal ``NaN -> 0``
zeroing and the per-region zeroing ceiling, run by ``condition_ld_matrix`` -- WAS
pre-registered: OSF file tcujq on az52u, posted 2026-07-04T04:14:46Z. It was then
WITHDRAWN by the amendment-update OSF file trsx5 on az52u, posted
2026-07-10T13:32:22Z. The posted trsx5 body, under "What is withdrawn:", reads:

    The off-diagonal NaN→0 conditioning of isolated pairwise-undefined entries
    (prior amendment tcujq item (a) isolated-off-diagonal-pair branch and item
    (b) the per-region zeroing ceiling), together with its
    BRANCH_AFR_COND_CLEAN / BRANCH_AFR_COND_APPLIED / BRANCH_AFR_COND_DEFERRED
    outcome branches, is withdrawn.

The replacement pre-registered by trsx5 is overlapping-deletion occlusion
exclude-in-lockstep (LD panel AND harmonized summary statistics) with a mandatory
provenance manifest; NaN→0 is prohibited.

STATUS: this module (m3-06, HELD) is retained as a historical record and is NOT
called by the pipeline. Its code, its error strings and its on-disk provenance
keys (``nan_policy``, ``n_zeroed``, ``zeroed_pairs``, ``ceiling_frac``) are
deliberately left unchanged -- read them, and the "pre-registered" wording below,
in light of this withdrawal. The text below this notice is the original 2026-07
wording, kept as written. Recorded:
DEC-2026-09-16-condition-ld-matrix-freeze-code-only (quick-260916-oyq).

==== END WITHDRAWN POLICY NOTICE ====

```

N4: write_conditioned_ld_npz.py COMMENT. Insert ONE new line (83 characters) immediately AFTER the existing line
`    # Apply the pre-registered conditioning (RAISES propagate here -> no file written).` Do NOT edit that line:

```
    # (Policy WITHDRAWN by trsx5, OSF 2026-07-10; see the module docstring notice.)
```
</notice_text>

<enforcer_spec>
`tests/m3/test_tcujq_withdrawal_notices.py`. Stdlib + pytest only, NO skips, NO `*_REF`/`*_REV` names (M7), no call to
`assert_code_frozen` (M7). Read files with `encoding="utf-8"`. Counts below were observed on the planner prototype (M18).
A prototype that met these exact counts was left at
`/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/proto/test_tcujq_withdrawal_notices.py`
(planner scratch, may be gone). If present it MAY be a starting point, but this spec is authoritative: its docstring must be
rewritten, and every count must be re-observed.

Module docstring: this is THE NAMED ENFORCER for the tcujq WITHDRAWN-by-trsx5 notices
(DEC-2026-09-16-condition-ld-matrix-freeze-code-only, quick-260916-oyq). It pins BEHAVIOUR via `ast` (the docstring as
Python sees it), never a grep. A notice moved into a `#` comment or a module-level string constant keeps every token in
the file TEXT and must still go RED. The file carries its own negative controls. State the operational definition of
"the pipeline" (tracked `Snakefile`, `src/`, `scripts/`, `bin/`, `tools/`) and its limit: untracked files and anything
outside those paths are not scanned. Also state that the positive-control anchor files are live data: renaming one is a
re-measure decision, not a fixup.

Constants:
```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
NOTICE_MODULES = ("src/python/condition_ld_matrix.py", "src/python/write_conditioned_ld_npz.py")
NOTICE_MODULE_IDS = ("condition_ld_matrix", "write_conditioned_ld_npz")
NOTICE_FUNCTIONS = (("src/python/condition_ld_matrix.py", "condition_ld_matrix"),)
POSTED_TRSX5_REL = ".planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt"
POSTED_TRSX5_SIZE = 9695
POSTED_TRSX5_MD5 = "c19be8b2ad7cd6a45fee1d668d8a9cf9"
POSTED_WITHDRAWAL_LINE = 19          # 1-based, via str.splitlines(); the file has NO trailing newline (wc -l says 58)
POSTED_SENTENCE_PREFIX = "The off-diagonal NaN→0 conditioning of isolated pairwise-undefined entries"
POSTED_SENTENCE_END = "is withdrawn."
NOTICE_BEGIN = "==== WITHDRAWN POLICY NOTICE (tcujq -> trsx5)"
NOTICE_END = "==== END WITHDRAWN POLICY NOTICE ===="
NOTICE_MAX_START_LINE = 4            # 0-based index into ast.get_docstring(clean=True).split("\n")
FUNCTION_NOTICE_WINDOW = 7           # the function notice must sit in the first 7 docstring lines
MODULE_BODY_TOKENS = ("withdrawn", "tcujq", "trsx5", "2026-07-04", "2026-07-10", "exclude-in-lockstep",
                      "not called by the pipeline", "dec-2026-09-16-condition-ld-matrix-freeze-code-only")
FUNCTION_TOKENS = ("withdrawn", "tcujq", "trsx5", "2026-07-10", "withdrawn policy notice")
PIPELINE_PATHSPECS = ("Snakefile", "src/", "scripts/", "bin/", "tools/")
NON_PY_SUFFIXES = (".smk", ".sh", ".R", ".r", ".yaml", ".yml", ".ipynb")
NOTICE_STEMS = ("condition_ld_matrix", "write_conditioned_ld_npz")
POSITIVE_TEXT_HIT = ("occlusion_span_filter", "src/snakemake/rules/m3_occlusion_lockstep.smk")                    # M15
POSITIVE_SCRIPT_PATH_HIT = ("build_ld_rds", "src/legacy/region_analysis/scripts/run_ld_build_plan.py")          # M15
```
Helpers (the messages are load-bearing: the controls `match=` them):
- `_norm(s)` = `" ".join(s.split()).casefold()`.
- `posted_withdrawal_sentence()`: read BYTES; assert `len == POSTED_TRSX5_SIZE` FIRST (the 2026-08-14 size-adjudicates
  rule), then md5; decode utf-8; take `splitlines()[POSTED_WITHDRAWAL_LINE - 1]`; assert it startswith the prefix; return the
  text up to and including the first `POSTED_SENTENCE_END`.
- `notice_body(source, where)`: `doc = ast.get_docstring(ast.parse(source), clean=True)`; assert doc →
  `f"{where}: NO module docstring"`. BEGIN lines = indices whose `.strip().startswith(NOTICE_BEGIN)`; assert exactly 1 →
  `f"{where}: the module DOCSTRING holds {n} WITHDRAWN POLICY NOTICE blocks, not exactly 1"`. END lines = `.strip() == NOTICE_END`;
  assert exactly one AND it follows BEGIN → `f"{where}: the notice END marker is missing, duplicated or precedes BEGIN"`.
  Assert BEGIN index ≤ NOTICE_MAX_START_LINE → `f"{where}: the notice begins at docstring line {i} (> {NOTICE_MAX_START_LINE}) -- not prominent"`.
  Return the lines STRICTLY between the markers (the BODY; marker text never satisfies a token).
- `assert_module_notice(source, where)`: `body = _norm(notice_body(...))`; for each token in MODULE_BODY_TOKENS →
  `f"{where}: required token {tok!r} is missing from the notice BODY"`; then `_norm(posted_withdrawal_sentence()) in body` →
  `f"{where}: the verbatim POSTED trsx5 withdrawal sentence is missing from the notice BODY"`.
- `assert_function_notice(source, func, where)`: exactly one top-level `FunctionDef` named `func` (else a clear message);
  `head = _norm("\n".join((ast.get_docstring(node, clean=True) or "").split("\n")[:FUNCTION_NOTICE_WINDOW]))`; each FUNCTION_TOKENS →
  `f"{where}::{func}: required token {tok!r} is missing from the first {FUNCTION_NOTICE_WINDOW} lines of the FUNCTION docstring"`.
- `py_hits(source, stem, rel_stem) -> tuple[bool, bool]`: a PURE, stem-parameterised classifier returning `(importer, script_path)`.
  - importer: an `ast.Import` alias name, or an `ast.ImportFrom` module or alias name, whose last dotted component == `stem`.
  - script_path: a NON-docstring `str` Constant containing `f"{stem}.py"`, only when `rel_stem != stem` (a module is never its
    own caller). Docstrings use the same owner rule as source_freeze: the first-statement `Expr(Constant str)` of
    Module/FunctionDef/AsyncFunctionDef/ClassDef.
- `pipeline_scan(stems) -> dict`: ONE pass over `git ls-files -z -- *PIPELINE_PATHSPECS` (cwd PROJECT_ROOT, check=True).
  `.py` → `py_hits` per stem (all parse, M5). Non-.py (suffix in NON_PY_SUFFIXES or basename `Snakefile`) → text hit when the
  stem occurs. Returns `{"n_py", "n_other", "importers": {stem: set}, "script_path": {stem: set}, "text": {stem: set}}`.
  A tracked file that cannot be read is an error, never a skip.

Tests (stable ids, 17 total):
1. `test_the_posted_trsx5_body_is_the_byte_exact_reconstruction`
2. `test_module_docstring_carries_the_withdrawal_notice[condition_ld_matrix|write_conditioned_ld_npz]`: real file text → `assert_module_notice`.
3. `test_function_docstring_carries_the_withdrawal_notice[condition_ld_matrix]`
4. `test_neither_notice_module_has_a_pipeline_caller`: `pipeline_scan(NOTICE_STEMS)`. Floors `n_py >= 150`, `n_other >= 100`
   (non-vacuity, not equality); must-be-identity `importers["condition_ld_matrix"] == {"src/python/write_conditioned_ld_npz.py"}`;
   `importers["write_conditioned_ld_npz"] == set()`; no script-path hits and no text hits for either stem.
5. `test_the_pipeline_scan_detects_known_positives` (W6): `pipeline_scan((POSITIVE_TEXT_HIT[0], POSITIVE_SCRIPT_PATH_HIT[0]))`;
   assert `POSITIVE_TEXT_HIT[1] in text[...]` and `POSITIVE_SCRIPT_PATH_HIT[1] in script_path[...]` (SUBSET checks, not equality).
6. `test_a_docstring_only_mention_is_not_a_script_path_hit` (W6):
   `py_hits('"""Mentions condition_ld_matrix.py in a docstring only."""\nX = 1\n', "condition_ld_matrix", "other") == (False, False)`
   and `py_hits('X = "src/python/condition_ld_matrix.py"\n', "condition_ld_matrix", "other") == (False, True)`.
7. `test_the_synthetic_fixture_is_green`: the GOOD synthetic module passes both asserts (non-vacuity for the controls).
8. `test_module_notice_negative_control[<id>]` for 7 ids, each on the SYNTHETIC fixture with `pytest.raises(AssertionError, match=...)`:
   - `removed` ("not exactly 1")
   - `moved_into_comment` ("not exactly 1")
   - `moved_into_string_constant` ("not exactly 1")
   - `body_token_misspelled` (trsx5→trxs5 in BODY lines only; "required token 'trsx5'")
   - `sentence_altered` ("is withdrawn." → "is retained.", exactly one replacement; "verbatim POSTED")
   - `moved_to_docstring_end` ("not prominent"). **Premise check first (M18):** assert the mutated docstring's BEGIN index is
     `> NOTICE_MAX_START_LINE` ("fixture too short for this control"), THEN assert RED.
   - `duplicated` ("not exactly 1")

   For `moved_into_comment` and `moved_into_string_constant`, ALSO assert every MODULE_BODY_TOKENS token is in `_norm(mutated)`.
   This proves a text grep would have been GREEN.
9. `test_function_notice_negative_control[<id>]` for `function_notice_removed` and `function_notice_moved_into_comment`
   (match "required token 'withdrawn'").

Mutation helpers (private, pure `str -> str`, reusable on REAL texts in Task 3). Locate the block in RAW text: first line whose
`.strip().startswith(NOTICE_BEGIN)` through the next line whose `.strip() == NOTICE_END`. Insert comment/constant copies right
after the line `from __future__ import annotations`. `moved_to_docstring_end` re-parses after deletion and inserts before the
docstring's closing line (assert that line `.strip() == '"""'`). The function notice is the line whose `.strip()` starts with
`WITHDRAWN POLICY:` plus the contiguous non-blank lines after it. EVERY mutation asserts `mutated != source` and
`ast.parse(mutated)` succeeds, so a RED can never be a SyntaxError masquerade. Collect them in
`MODULE_MUTATIONS = {id: (fn, match)}` and `FUNCTION_MUTATIONS = {id: (fn, match)}` and parametrize the controls from those dicts
(`pytest.raises` patterns regex-safe via `re.escape` on literal fragments).

Synthetic GOOD fixture (built from constants plus `posted_withdrawal_sentence()`), the lines below joined with `"\n"`.
The historical tail is deliberately 7 lines long (M18), and there is a blank line after the See-line (W3; it mirrors N2):
`'"""Synthetic title line for the enforcer controls.'`, `""`, `NOTICE_BEGIN + " -- READ BEFORE ANYTHING BELOW ===="`, `""`,
`"Pre-registered in tcujq (OSF 2026-07-04); WITHDRAWN by trsx5 (OSF 2026-07-10)."`, `<sentence>`,
`"Replaced by exclude-in-lockstep. This module is NOT called by the pipeline."`,
`"Recorded: DEC-2026-09-16-condition-ld-matrix-freeze-code-only."`, `""`, `NOTICE_END`, `""`,
`"Historical text, kept as written."`, `""`, `"A second historical paragraph."`, `""`, `"A third historical paragraph."`, `""`,
`"A fourth historical paragraph."`, `'"""'`, `"from __future__ import annotations"`, `""`, `""`, `"def condition_ld_matrix(m):"`,
`'    """Apply the synthetic conditioning.'`, `""`,
`"    WITHDRAWN POLICY: tcujq (OSF 2026-07-04) was WITHDRAWN by trsx5 (OSF 2026-07-10)."`,
`"    See the WITHDRAWN POLICY NOTICE in the module docstring."`, `""`, `'    """'`, `"    return m"`, `""`.
</enforcer_spec>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Pre-flight + PRE baseline + record DEC-2026-09-16 + rescope the ONE numstat assertion, proven able to fail BEFORE commit (C1)</name>
  <files>tests/m3/test_source_freeze_pins.py, .planning/DECISIONS.md</files>
  <action>
Obey `<execution_rules>` R1-R4 throughout.

**Step 1: Pre-flight.** Any failure = STOP and report (after R2 cleanup once lib.sh exists); do not "fix" the environment.
- (a) `git -C $REPO rev-parse --abbrev-ref HEAD` == `m3-W2-aou-deltas`, and `git -C $REPO status --porcelain --untracked-files=no`
  is EMPTY. Pre-existing untracked `??` noise is expected and ignored.
- (b) RAM-1 has FULLY landed (W4). ALL three must succeed; any failure = STOP ("RAM-1 not landed or close-out missing: the
  baseline would be measured on the wrong tree and HEAD could move mid-run"):
  ```bash
  git -C $REPO log -1 --format=%s -- src/python/run_native_ld_panel.py | grep -q '^fix(quick-260916-ocb)'
  git -C $REPO cat-file -e HEAD:tests/m3/test_run_plink_peak_rss.py
  git -C $REPO log -1 --format=%s | grep -q '^docs(quick-260916-ocb)'     # the orchestrator's RAM-1 close-out IS HEAD
  ```
  Also `git -C $REPO status --porcelain -- src/python/run_native_ld_panel.py tests/m3/test_run_plink_peak_rss.py` must be empty.
- (c) `$SCRATCH` must NOT exist. If it does, STOP with this explanation: "`/gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916`
  already exists. It is the leftover of an earlier attempt at quick-260916-oyq and only ever holds `--shared` scratch clones,
  lib.sh, PRE/expected_head, logs and JUnit XML, never repo state. Listing attached (`ls -la $SCRATCH; cat $SCRATCH/PRE
  $SCRATCH/expected_head 2>/dev/null`). Cleanup, for the orchestrator after confirming no executor of this task and no suite run
  is live: `rm -rf -- /gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916`, then re-launch. The executor never deletes it."
  Otherwise `mkdir -p $SCRATCH/clones` and Write `$SCRATCH/lib.sh` from `<scratch_and_probe_library>`.
- (d) LIVE-PYTEST GUARD with its positive control FIRST (B1, M13), in ONE Bash call:
  ```bash
  source /gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916/lib.sh
  ( exec -a "python -m pytest -p no:cacheprovider tests/m3" tail -f /dev/null ) & FAKE=$!
  hit=""; for i in $(seq 200); do hit=$(live_pytest); [ -n "$hit" ] && break; done
  kill $FAKE; wait $FAKE 2>/dev/null
  echo "POSITIVE CONTROL -> [$hit]"          # MUST be non-empty and show the fake; empty = the guard is blind = STOP
  echo "REAL CHECK -> [$(live_pytest)]"       # MUST be empty; non-empty = another suite/executor is live = STOP
  ```
  Paste both lines into the SUMMARY. Never use `pgrep` for this: it matches its own wrapper.
- (e) Record `git -C $REPO rev-parse HEAD > $SCRATCH/PRE`; `cp $SCRATCH/PRE $SCRATCH/expected_head`; `$PY --version` (expect 3.11.x);
  md5sum of both src modules and tests/m3/test_source_freeze_pins.py → `$SCRATCH/pre_md5.txt`.
- (f) PRE-FLIGHT kht verifier (I11), so RAM-1 drift is separable from this task:
  `mkdir -p $SCRATCH/khtmp && TMPDIR=$SCRATCH/khtmp /usr/bin/python3 $REPO/.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py | tail -1 | tee $SCRATCH/kht_pre.txt`
  → must be `RESULT GREEN checks=317 parsed=88 table=88 verified=88`. Anything else = STOP: the drift predates this task and is
  not ours to fix.

**Step 2: PRE full-suite baseline (background, about 14 min).** Launch with run_in_background:
`cd $REPO && PYTHONDONTWRITEBYTECODE=1 $PY -m pytest -p no:cacheprovider tests/m3 -q -rfEs --junitxml=$SCRATCH/suite_pre.xml > $SCRATCH/suite_pre.log 2>&1; echo "EXIT=$?" >> $SCRATCH/suite_pre.log`.
From launch until `EXIT=` appears in the log, R1 applies: no pytest anywhere and NO write to the repo working tree.

**Step 3: Re-derive M1/M2/M5 yourself** (read-only scratch Python scripts under $SCRATCH: ast docstring spans + tokenize; numstat;
the tracked-file caller scan including .ipynb). No pytest, so this is allowed during the baseline. Save the outputs for the
SUMMARY and the DECISIONS entry. If ANY result differs from `<measured_by_planner>`, STOP and report before editing. Then WAIT
for `EXIT=` in `$SCRATCH/suite_pre.log` (use the background-completion notification or a Monitor until-loop; never foreground sleep).

**Step 4: Proof A, AFTER the baseline finished, BEFORE any edit, on the OLD assertion.** Run
`source $SCRATCH/lib.sh; c=$(mkclone A1)` and
`probe_commit $c src/python/condition_ld_matrix.py '<DOC_CLM old>' '<DOC_CLM new>'`. Then:
`pins $c tests/m3/test_source_freeze_pins.py handoff_frozen_claim` → expect RED `... is NO LONGER 0-diff vs bf16289 ...`.
`pins $c tests/m3/test_source_freeze_pins.py "python_module_code_is_frozen or python_symbol_code_is_frozen"` → expect 25 passed.
Save the verbatim output as Proof A.

**Step 5: Edit tests/m3/test_source_freeze_pins.py.** Change ONLY these four things:
(a) In `test_the_handoff_frozen_claim_is_recorded_as_partly_false`, replace the final `for rel in PY_FROZEN_RELS:` numstat
block with:
```python
    # DEC-2026-09-16-condition-ld-matrix-freeze-code-only (Carter, 2026-09-16):
    # condition_ld_matrix.py's freeze is CODE-only. The whole-file numstat check
    # below was a BYTE proxy: it made the additive tcujq WITHDRAWN-by-trsx5
    # docstring notice (quick-260916-oyq) cost a red test. The property the
    # freeze protects is the CODE, which assert_code_frozen pins -- docstrings and
    # comments ignored, code string constants (e.g. the raise messages that still
    # say "pre-registered") KEPT. It reads the WORKING TREE, where the numstat
    # compared two COMMITS. plink_ld_to_npz.py and occlusion_span_filter.py
    # deliberately KEEP the byte-level numstat pin: a recorded non-change.
    code_only = ("src/python/condition_ld_matrix.py",)
    assert set(code_only) <= set(PY_FROZEN_RELS), (
        "the CODE-only rescope names a file outside PY_FROZEN_RELS -- its branch "
        "would be dead and would guard nothing"
    )
    numstat_pinned = [rel for rel in PY_FROZEN_RELS if rel not in code_only]
    assert numstat_pinned == [
        "src/python/plink_ld_to_npz.py",
        "src/python/occlusion_span_filter.py",
    ], f"the byte-pinned set changed shape without a decision: {numstat_pinned}"
    for rel in code_only:
        assert_code_frozen(rel, PY_CODE_REF, LANG_PY)
    for rel in numstat_pinned:
        # <the ORIGINAL two statements, byte-identical: `numstat = _git(...)` and `assert not numstat, (...)`>
```
(b) Append one paragraph to that function's docstring: condition_ld_matrix.py is held here to its CODE pin, not a byte pin, per
DEC-2026-09-16-condition-ld-matrix-freeze-code-only; the other two frozen modules keep the 0-numstat requirement.
(c) In the MODULE docstring, additively, right after the paragraph that starts "Every pin here is a CODE pin", add this
caveat paragraph (M8): "⚠ ONE byte-level assertion remains (measured 2026-09-16): ``test_the_handoff_frozen_claim_is_recorded_as_partly_false``
still requires ``plink_ld_to_npz.py`` and ``occlusion_span_filter.py`` to be 0-``numstat`` vs ``PY_CODE_REF`` at HEAD -- a whole-file BYTE
pin, so a COMMITTED docstring edit to either IS red. ``condition_ld_matrix.py`` was moved to its CODE pin by
DEC-2026-09-16-condition-ld-matrix-freeze-code-only; the other two were deliberately left as they are (same entry)."
(d) Add one `#:` line at the END of the comment block directly above `PY_FROZEN_RELS`:
`#: condition_ld_matrix.py: CODE-only since DEC-2026-09-16-condition-ld-matrix-freeze-code-only (no longer 0-numstat-pinned).`
Do NOT touch: `PY_CODE_REF` or the comment block directly above it (the bucket scan reads that block), `PY_FROZEN_RELS`' value,
`MOVED_SINCE_PY_CODE_REF`, `PY_SYMBOL_CASES`, or any other test. New text must cite no line numbers of src files (M9).
Key-link check (I7): `grep -c 'for rel in code_only:' tests/m3/test_source_freeze_pins.py` was 0 at PRE and must be 1 now.

**Step 6: Proof B, on the rescoped form, BEFORE commit.** Run each probe in a FRESH clone with the edited test file copied in:
`c=$(mkclone <NAME>)`; `cp $REPO/tests/m3/test_source_freeze_pins.py $c/tests/m3/`; probe_commit; pins.
- B1 DOC_CLM → `handoff_frozen_claim` GREEN (1 passed) AND `python_module_code_is_frozen or python_symbol_code_is_frozen` 25 passed.
  Side-by-side in the SAME clone: `git -C $c show HEAD:tests/m3/test_source_freeze_pins.py > $c/tests/m3/test_oyq_old_pins_copy.py`
  (HEAD still holds the OLD file), then `pins $c tests/m3/test_oyq_old_pins_copy.py handoff_frozen_claim` → RED "NO LONGER 0-diff".
- B2 STR_153 → `handoff_frozen_claim` RED with "the CODE of src/python/condition_ld_matrix.py (whole file) has MOVED off its pin bf16289",
  and the first-difference line names `pre-registeredX`. Also `pins $c tests/m3/test_source_freeze_pins.py "python_symbol_code_is_frozen and condition_ld_matrix"`
  → exactly 1 failed (the `condition_ld_matrix` symbol) / 2 passed. This proves code strings are CODE.
- B3 CONST → `handoff_frozen_claim` RED (MOVED off its pin).
- B4 DOC_PLINK → `handoff_frozen_claim` RED "src/python/plink_ld_to_npz.py is NO LONGER 0-diff" (numstat retained).
- B5 DOC_OCC → `handoff_frozen_claim` RED "src/python/occlusion_span_filter.py is NO LONGER 0-diff" (numstat retained).
If any probe's observed colour differs from its expectation, STOP and report. Never adjust the test to match.

**Step 7: Append the DECISIONS.md entry at EOF.** Append only, and match the file's style: `## date — ID: headline`, bold
lead paragraphs, `###` subsections, `**Cross-refs:**`. Heading:
`## 2026-09-16 — DEC-2026-09-16-condition-ld-matrix-freeze-code-only: condition_ld_matrix.py's freeze is CODE-only; its whole-file numstat pin is retired so an additive WITHDRAWN-by-trsx5 docstring notice is free`
Required content:
- **Decision (CARTER, 2026-09-16 ~17:45 EDT, AskUserQuestion):** the verbatim option label and description, quoted from `<objective>`.
- `### The premise, corrected (MEASURED at <PRE sha>)`:
  (1) The recorded defect list was incomplete; paste your Step 3 classification.
  (2) "condition_ld_matrix.py is CODE-pinned, so docstring edits are free" was WRONG. The numstat assertion compared
  `bf16289` to HEAD (commit vs commit), so a COMMITTED docstring edit was RED; cite Proof A's AssertionError line.
  (3) The raise-message f-strings are code string constants: of the module's 4 raise sites, 2 messages say "pre-registered" and
  1 of those names BRANCH_AFR_COND_DEFERRED (M17). Editing them trips the code pins (Proof B2).
  (4) "pre-registered" was TRUE when written: tcujq was posted 2026-07-04T04:14:46Z and withdrawn by trsx5, posted
  2026-07-10T13:32:22Z (quote the withdrawal sentence from posted body line 19). So the correction is additive, never a
  deletion. trsx5 also RETAINS the fully-NaN-row drop rule, PSD and the raw NaN-raise contract (posted lines 35/37/39).
- `### What changes`:
  - The rescoped assertion (summarize Proofs B1-B5).
  - **Semantics note (I12):** the rescoped check (`assert_code_frozen`) reads the WORKING TREE for its actual side, whereas the
    retired numstat compared two COMMITS (`bf16289`..HEAD). Consequences: an uncommitted CODE edit now turns it RED immediately
    (stronger for code), while a committed docstring or comment edit no longer does (the intended freedom).
  - The additive notices in both modules' docstrings plus one new comment line in write_conditioned_ld_npz.py (Task 3,
    quick-260916-oyq).
  - The named enforcer `tests/m3/test_tcujq_withdrawal_notices.py` (Task 2).
- `### What does NOT change`:
  - `PY_CODE_REF` stays `bf16289` (no re-pin), and `PY_FROZEN_RELS` and the 22 derived symbols are unchanged.
  - `test_python_module_code_is_frozen` and `test_python_symbol_code_is_frozen` are unchanged.
  - Every line of code, code string, import, constant, signature and behaviour of both modules is unchanged, both raise messages included.
  - **`src/python/plink_ld_to_npz.py` and `src/python/occlusion_span_filter.py` KEEP their whole-file numstat pin. Name them
    explicitly as unchanged.**
  - OSF records, `.planning/amendments/` and `osf_deviations.md` are untouched.
  - The earlier DEC-2026-08-06-sr4-freeze-scope entry is NOT edited (append-only). This entry is the correction of record for
    that entry's "outside every freeze gate" sentence as it applied to these files.
- `### Observation for Carter (NOT decided here)`: the same proxy-vs-property question applies to plink_ld_to_npz.py and
  occlusion_span_filter.py, where a committed docstring edit is still RED (Proofs B4/B5). The pins-file module docstring
  now carries a caveat saying so. HANDOFF.json:261 and STATE.md:61 still carry the wrong "docstring edits are FREE" premise
  (orchestrator to refresh).
- **Cross-refs:**
  - DEC-2026-08-06-sr4-freeze-scope.
  - `.planning/osf_deviations.md` entries `## 2026-07-04 — AFR native-panel LD NaN→0 …` and
    `## 2026-07-10 — AFR native-panel occlusion exclude-in-lockstep amendment-update …`.
  - The posted body `.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt`
    (9,695 B / c19be8b2ad7cd6a45fee1d668d8a9cf9).
  - `.planning/amendments/osf-amendment-afr-native-ld-nan-psd-2026-07-03.md` (the tcujq project-side copy).
  - quick-260916-oyq.
  - The memory rules "scope a guard to the property, not a proxy" and "a claimed invariant needs a named enforcer".
Do not restate md5s of other frozen artifacts (sr4 precedent: one source of truth per literal).

**Step 8: Verify on the real tree, guard, commit C1.**
- (i) `cd $REPO && PYTHONDONTWRITEBYTECODE=1 $PY -m pytest -p no:cacheprovider -q tests/m3/test_source_freeze_pins.py tests/m3/test_source_freeze.py`
  → all pass, with the same passed count these two files had in the PRE baseline.
- (ii) APPEND-ONLY for DECISIONS.md (W5, M16). All must hold:
  - `source $SCRATCH/lib.sh && dec_prefix_check $REPO/.planning/DECISIONS.md && echo PREFIX-GREEN` prints PREFIX-GREEN.
  - `git -C $REPO diff --numstat -- .planning/DECISIONS.md` has a deletions column of `0`.
  - NEGATIVE CONTROL, observed and pasted: `cp $REPO/.planning/DECISIONS.md $SCRATCH/dec_neg.md && sed -i '0,/^- /{/^- /d}' $SCRATCH/dec_neg.md && source $SCRATCH/lib.sh; dec_prefix_check $SCRATCH/dec_neg.md; rc=$?; [ $rc -eq 1 ] && echo "NEG RED (correct, rc=1)" || { echo "NEG INVALID rc=$rc"; exit 1; }`
    must print `NEG RED (correct, rc=1)` (any rc other than 1 — e.g. 127 function-not-defined, 2 PRE unreadable, 0 GREEN — is a STOP), with `diff $SCRATCH/dec_neg.md $REPO/.planning/DECISIONS.md | grep -c '^>'` == 1. A GREEN here means
    the check is blind = STOP.
- (iii) `git diff --stat` shows exactly the 2 files.
- (iv) R3 guard (HEAD == `$SCRATCH/expected_head`; `git log --oneline -1` equals the pre-flight HEAD). Then
  `git add -- tests/m3/test_source_freeze_pins.py .planning/DECISIONS.md`; `git diff --cached --name-only` == exactly those two.
  Commit message: `test(quick-260916-oyq): rescope condition_ld_matrix.py freeze to CODE-only per DEC-2026-09-16-condition-ld-matrix-freeze-code-only (proven able to fail in scratch clones)`
  + R3 trailer. Write the new HEAD to `$SCRATCH/expected_head`. Then `cleanup_clones`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && PYTHONDONTWRITEBYTECODE=1 /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest -p no:cacheprovider -q tests/m3/test_source_freeze_pins.py tests/m3/test_source_freeze.py && grep -c "DEC-2026-09-16-condition-ld-matrix-freeze-code-only" .planning/DECISIONS.md tests/m3/test_source_freeze_pins.py && grep -c "for rel in code_only:" tests/m3/test_source_freeze_pins.py && git show --stat --format=%s HEAD | grep -E "quick-260916-oyq|test_source_freeze_pins.py|DECISIONS.md" && bash -c 'source /gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916/lib.sh && dec_prefix_check "$REPO/.planning/DECISIONS.md" && echo PREFIX-GREEN'</automated>
  </verify>
  <done>
Pre-flight passed: RAM-1 fix + test file + close-out HEAD present, the live-pytest positive control observed then the real check silent,
PRE recorded, kht pre-flight GREEN. The PRE baseline XML+log exist with `EXIT=`, and NO pytest ran while it was live. M1/M2/M5 were
re-derived and match. Proof A (old form RED on a committed docstring probe; 25 code pins GREEN) and Proofs B1-B5 were observed exactly
as expected, with verbatim output saved. C1 is committed, containing ONLY tests/m3/test_source_freeze_pins.py and .planning/DECISIONS.md.
The pins + source_freeze tests pass on the real tree. DECISIONS.md passes the byte-prefix check with 0 deletions, and the check was
observed RED on a bullet-deleted copy.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: The named enforcer tests/m3/test_tcujq_withdrawal_notices.py, committed RED (C2)</name>
  <files>tests/m3/test_tcujq_withdrawal_notices.py</files>
  <behavior>
    - test_the_posted_trsx5_body_is_the_byte_exact_reconstruction: size 9695 then md5 c19be8b2…; line 19 starts with the prefix; the returned sentence ends "is withdrawn." → GREEN now.
    - test_module_docstring_carries_the_withdrawal_notice[condition_ld_matrix] and [write_conditioned_ld_npz] → RED now ("holds 0 WITHDRAWN POLICY NOTICE blocks, not exactly 1").
    - test_function_docstring_carries_the_withdrawal_notice[condition_ld_matrix] → RED now ("required token 'withdrawn' is missing from the first 7 lines of the FUNCTION docstring").
    - test_neither_notice_module_has_a_pipeline_caller → GREEN now (importer identity holds; floors met; no script-path/text hits).
    - test_the_pipeline_scan_detects_known_positives → GREEN now (m3_occlusion_lockstep.smk text hit; run_ld_build_plan.py script-path hit).
    - test_a_docstring_only_mention_is_not_a_script_path_hit → GREEN now ((False, False) for docstring-only; (False, True) for a code string).
    - test_the_synthetic_fixture_is_green + 7 module + 2 function negative controls → GREEN now (each raises its SPECIFIC message; moved_to_docstring_end asserts its own premise first).
  </behavior>
  <action>
Obey `<execution_rules>`. **Guard:** HEAD == `$SCRATCH/expected_head` (C1), the tracked tree is clean, and `live_pytest` is silent.
Otherwise STOP (R2).

**Write** `tests/m3/test_tcujq_withdrawal_notices.py` exactly per `<enforcer_spec>`: constants, helpers with the stated
messages, 17 tests with the stated ids, mutation helpers, and the synthetic fixture (7-line historical tail + blank after the See-line).
Rules:
- Pin behaviour via `ast`, never grep (memory: "A grep gate matches text, not meaning").
- No `*_REF`/`*_REV`/`BASE_COMMIT`/`BASELINE_REV` names; no `assert_code_frozen`/`assert_unchanged_on_disk` calls (M7).
- No skips, no network, nothing written to disk.
- The mutation helpers and the `MODULE_MUTATIONS` / `FUNCTION_MUTATIONS` dicts must be importable at module level, because Task 3
  reuses them on the real texts.

**Run the RED:** `cd $REPO && PYTHONDONTWRITEBYTECODE=1 $PY -m pytest -p no:cacheprovider -q -rf tests/m3/test_tcujq_withdrawal_notices.py`
→ expect EXACTLY `3 failed, 14 passed`, and the 3 failed ids must be precisely the two module-notice tests and the one
function-notice test, failing for the documented reasons. Paste the `FAILED …` lines and each `E   AssertionError:` line into
the SUMMARY. If any OTHER test fails (posted anchor, caller scan, positives, a control, the synthetic fixture), fix THE NEW FILE until
only the 3 documented REDs remain. Never edit src/, source_freeze.py or any other test to get there. If that is impossible,
STOP and report (R2).

**Cross-file gates** that walk every tests/m3/*.py:
`$PY -m pytest -p no:cacheprovider -q tests/m3/test_source_freeze_pins.py tests/m3/test_source_freeze.py` → all pass
(the bucket scan and the control-seam AST walk now include the new file).

**Guard + commit C2 (R3):** `git add -- tests/m3/test_tcujq_withdrawal_notices.py`; `git diff --cached --name-only` == exactly that file.
Commit message: `test(quick-260916-oyq): RED — named enforcer for the tcujq WITHDRAWN-by-trsx5 docstring notices (ast, not grep; 9 committed negative controls + caller-scan positive controls)`
+ R3 trailer. There is no pre-commit hook (M12). Update `$SCRATCH/expected_head`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && PYTHONDONTWRITEBYTECODE=1 /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest -p no:cacheprovider -q tests/m3/test_tcujq_withdrawal_notices.py 2>&1 | tail -1 | grep -E "^3 failed, 14 passed" && PYTHONDONTWRITEBYTECODE=1 /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest -p no:cacheprovider -q tests/m3/test_source_freeze_pins.py tests/m3/test_source_freeze.py</automated>
  </verify>
  <done>
C2 is committed with only the new test file. At C2, the file shows exactly 3 failed (the 3 positive notice tests, for the
documented reasons) and 14 passed. The RED lines are saved for the SUMMARY. The pins and source_freeze suites stay green
with the new file present.
  </done>
</task>

<task type="auto">
  <name>Task 3: Additive notices (C3, GREEN) + post-commit proofs + real-file controls + full-suite by-name reconciliation + kht verifier + SUMMARY</name>
  <files>src/python/condition_ld_matrix.py, src/python/write_conditioned_ld_npz.py, .planning/quick/260916-oyq-tcujq-withdrawn-by-trsx5-notices-in-cond/260916-oyq-SUMMARY.md</files>
  <action>
Obey `<execution_rules>`. **Guard:** HEAD == `$SCRATCH/expected_head` (C2), the tracked tree is clean, and `live_pytest` is silent.
Otherwise STOP (R2).

**Step 1: Insert N1, N2, N3 and N4 from `<notice_text>`.** Use a scratch Python script (`$SCRATCH/apply_notices.py`) that inserts
by exact text anchors, asserts each anchor occurs exactly once, and writes UTF-8. Per D-Carter, the edits are ADDITIVE ONLY:
no existing line is modified or removed, and no code, code string, import, constant, signature or behaviour is touched. Honour M6:
keep line 1; no line starting `def `; no backslash, triple quote or apostrophe in inserted text.

**Step 2: Pre-commit checks on the real tree.** All must pass; paste the outputs.
a. `$PY -m pytest -p no:cacheprovider -q tests/m3/test_tcujq_withdrawal_notices.py` → `17 passed`.
b. ADDITIVE: `git diff --numstat -- src/python/condition_ld_matrix.py src/python/write_conditioned_ld_npz.py` has deletions == 0
   for both. Then run a scratch script over both files: `git show $(cat $SCRATCH/PRE):<rel>` `.split()` must be a SUBSEQUENCE of the new
   file's `.split()` (print True True).
c. CODE-INERT: a scratch script does `sys.path.insert(0, "$REPO/tests/m3")`, `from source_freeze import code_lines, git_show, LANG_PY`, and
   checks `code_lines(new_text, LANG_PY) == code_lines(git_show(PRE, rel), LANG_PY)` for both files (print True True). It also checks that
   `f"is pre-registered (osf-amendment-afr-native-ld-nan-psd-2026-07-03.md)."` and
   `f"condition_ld_matrix: n_zeroed_pairs={n_zeroed} exceeds the pre-registered "` each occur exactly once, byte-identical.
d. Import smoke: `$PY -c "import sys; sys.path.insert(0,'src/python'); import condition_ld_matrix as c, write_conditioned_ld_npz as w; print(c.__doc__.split(chr(10))[2]); print(w.__doc__.split(chr(10))[3])"`
   → both print the `==== WITHDRAWN POLICY NOTICE (tcujq -> trsx5) …` line.
e. Neighbours: `$PY -m pytest -p no:cacheprovider -q tests/m3/test_source_freeze_pins.py tests/m3/test_source_freeze.py tests/m3/test_condition_ld_matrix.py tests/m3/test_write_conditioned_ld_npz.py`
   → all pass, and `$PY -m pytest -p no:cacheprovider -q tests/m3/test_run_native_ld_panel.py -k no_nan_to_zero_conditioning_in_the_driver` → 1 passed.

**Step 3: Guard + commit C3 (R3).** `git add -- src/python/condition_ld_matrix.py src/python/write_conditioned_ld_npz.py`;
`git diff --cached --name-only` == exactly those two. Commit message:
`docs(quick-260916-oyq): additive WITHDRAWN-by-trsx5 notices in condition_ld_matrix.py + write_conditioned_ld_npz.py docstrings (code untouched; enforcer GREEN)`
+ R3 trailer. Update `$SCRATCH/expected_head`.

**Step 4: Proof C, AFTER the notices, on the real repo and fresh clones.** No suite run is live at this point; Steps 4-5 MUST
finish before Step 6 launches (R1). Paste everything verbatim.
- C-i: real repo `$PY -m pytest -p no:cacheprovider -q tests/m3/test_source_freeze_pins.py -k handoff_frozen_claim` → 1 passed.
- C-ii: `git diff --numstat bf16289 HEAD -- src/python/condition_ld_matrix.py` is NON-empty, with a deletions column of 0. This is exactly
  the input that turns the old form RED.
- C-iii: execute the OLD test function against the real repo WITHOUT writing any file. A scratch Python script sets
  `src = git show <PRE>:tests/m3/test_source_freeze_pins.py` and `fake = "$REPO/tests/m3/_oyq_old_pins_probe_NOT_ON_DISK.py"`, then runs
  `exec(compile(src, fake, "exec"), {"__file__": fake, "__name__": "oyq_old_pins_probe"})` and calls
  `test_the_handoff_frozen_claim_is_recorded_as_partly_false()` inside try/except AssertionError. Expect RED
  "src/python/condition_ld_matrix.py is NO LONGER 0-diff vs bf16289". Afterwards, assert `fake` does not exist and the tracked tree is clean.
  (The planner dry-ran this mechanism at 11f61e8: GREEN before the notice, with no file created.)
- C-iv: `c=$(mkclone C4)` (now at the C3 HEAD); probe STR_153 → `handoff_frozen_claim` RED (MOVED off its pin).
  `c=$(mkclone C5)`; probe DOC_CLM → `handoff_frozen_claim` GREEN AND `pins`-style run of `tests/m3/test_tcujq_withdrawal_notices.py`
  (`cd $c && $PY -m pytest -p no:cacheprovider -q tests/m3/test_tcujq_withdrawal_notices.py`) → `17 passed`. The widened `mkclone`
  checkout (M14) supplies the posted trsx5 body and Snakefile/scripts/bin; a `16 failed, 1 passed` here means the checkout regressed = STOP (R2).

**Step 5: One-shot controls on the REAL post-C3 texts, in memory only.** A scratch script does
`sys.path.insert(0, "$REPO/tests/m3")` and `import test_tcujq_withdrawal_notices as enf` (PYTHONDONTWRITEBYTECODE=1). It first
prints GREEN for `enf.assert_module_notice` on both real texts and for `enf.assert_function_notice` on condition_ld_matrix.py
(non-vacuity). Then, for each real module × each `enf.MODULE_MUTATIONS` id, and for condition_ld_matrix.py × each
`enf.FUNCTION_MUTATIONS` id, it applies the mutation to the real text, calls the matching assert, and prints
`RED  <module> <id>: <first line of the AssertionError>`. If an assert does NOT raise, it prints `GREEN(!!) …`.
Expected: 14 + 2 = 16 RED lines, zero GREEN(!!). Every RED must match its dict `match` pattern (M18 observed 16/16). Any GREEN(!!)
or mismatch = STOP (R2). Then `cleanup_clones`.

**Step 6: POST full suite (background, about 14 min).** Confirm `live_pytest` is silent, then use the same command as Task 1 Step 2
with `suite_post.xml` / `suite_post.log`. R1 applies until `EXIT=` appears.

**Step 7: Reconcile BY NAME** (after `EXIT=`). Write `$SCRATCH/reconcile.py PRE.xml POST.xml`. Key = `classname::name`. Outcome = failed if
`<failure>`/`<error>`, skipped if `<skipped>`, else passed; a duplicate key takes the worst outcome and the duplicate count is reported.
It prints per-side outcome counts, REMOVED keys, ADDED keys with outcomes, and CHANGED keys. It exits 0 only if REMOVED = ∅,
CHANGED = ∅, every ADDED key starts with `tests.m3.test_tcujq_withdrawal_notices::` with outcome passed, exactly 17 were added,
and each side has ≥ 1000 testcases (a floor, not an equality).
Self-control FIRST, observed:
(i) `reconcile.py suite_pre.xml suite_pre.xml` → exit 0.
(ii) Copy suite_pre.xml to `$SCRATCH/flipped.xml` with ONE passed testcase given a `<failure message="oyq-control"/>` child →
`reconcile.py suite_pre.xml flipped.xml` → exit ≠ 0 naming that key.
Then run the real reconciliation. Also quote the final summary line of both logs.
If a CHANGED key is in `test_source_freeze*.py`, `test_condition_ld_matrix.py`, `test_write_conditioned_ld_npz.py`,
`test_run_native_ld_panel.py`, `test_run_plink_peak_rss.py` or the new file, STOP (R2).
For any other CHANGED key, re-run that single test at HEAD (no suite run live) and record both outputs. A test that passes in isolation
is reported prominently as a suspected flake (for example the known R-subprocess timeout class). It is never silently counted as PASS,
and no test is edited.

**Step 8: kht verifier, post-commit.** Run `TMPDIR=$SCRATCH/khtmp /usr/bin/python3 $REPO/.planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py | tail -1`
→ it must print `RESULT GREEN checks=317 parsed=88 table=88 verified=88`, identical to `$SCRATCH/kht_pre.txt`. Anything else = STOP (R2).

**Step 9: Final guard.** HEAD == expected_head (C3). `git log --oneline -4` shows C3, C2, C1, then PRE (the RAM-1 close-out).
`git diff --stat $(cat $SCRATCH/PRE) HEAD` lists EXACTLY the 5 committed files. The tracked tree is clean. No push.

**Step 10: Write `260916-oyq-SUMMARY.md`** (do NOT commit it; the orchestrator does). Include:
- the pre-flight record: PRE sha, the three RAM-1 checks, the live-pytest positive-control line and real-check line, python version, kht pre-flight line;
- the re-derived M1/M2/M5 outputs;
- Proof A and Proofs B1-B5 verbatim;
- the DECISIONS prefix check and its NEG RED line;
- the C2 RED lines;
- the Step 2 a-e outputs;
- Proofs C-i to C-iv verbatim;
- the 16 real-file RED lines;
- the reconciliation self-control plus the real reconciliation output (counts, 17 added, removed/changed = none) and both log summary lines;
- the kht post-commit tail line;
- the 3 commit SHAs + subjects;
- a "Deviations / contradictions of the brief" section. It must at least record M3 (working-tree edits cannot turn a HEAD-vs-ref
  numstat RED, so scratch clones were used), M4 (the notice is scoped to what trsx5 actually withdrew), M8 (sr4/pins-docstring
  "every pin is a CODE pin" was false for the numstat assertion; HANDOFF.json:261 / STATE.md:61 carry the wrong premise and need an
  orchestrator refresh), M9 (STATE/HANDOFF line cites :4/:153 etc. are now stale) and M13/M14 (the pgrep and narrow-clone traps
  avoided);
- the observation for Carter about plink_ld_to_npz.py + occlusion_span_filter.py.
Then `cleanup_clones` (R2 form). Keep the logs/XML under $SCRATCH.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && PYTHONDONTWRITEBYTECODE=1 /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest -p no:cacheprovider -q tests/m3/test_tcujq_withdrawal_notices.py tests/m3/test_source_freeze_pins.py tests/m3/test_source_freeze.py tests/m3/test_condition_ld_matrix.py tests/m3/test_write_conditioned_ld_npz.py && git diff --numstat "$(cat /gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916/PRE)" HEAD -- src/python/condition_ld_matrix.py src/python/write_conditioned_ld_npz.py | awk '{ if ($2 != 0) exit 1 } END { print "additive-only OK" }' && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python /gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916/reconcile.py /gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916/suite_pre.xml /gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916/suite_post.xml && TMPDIR=/gpfs_common/share01/clintonlab/ckclinto/tmp/oyq-260916/khtmp /usr/bin/python3 .planning/quick/260916-kht-bank-the-stage-c-nan-error-posture-optio/260916-kht-verify.py | tail -1 | grep -F "RESULT GREEN checks=317 parsed=88 table=88 verified=88"</automated>
  </verify>
  <done>
C3 is committed with only the two src files: additions only, code_lines identical to PRE, both raise strings byte-identical.
The enforcer shows 17 passed in the real repo and in clone C5. Proofs C-i to C-iv were observed as expected. 16/16 real-file mutations
are RED with matching messages. No pytest ran concurrently with either suite run. The PRE vs POST reconciliation exits 0 (17 added,
all in the new file, all passed; 0 removed; 0 changed), and its self-control was observed RED. The kht verifier is GREEN before and
after. The final guard passed. The SUMMARY is written (uncommitted) with every verbatim output and the contradictions section.
Scratch clones are removed.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| public OSF record → repo docstrings | Text quoted from the posted trsx5 body enters source docstrings. A misquote or over-claim would misstate the pre-registration record |
| freeze gate → future edits | The rescoped assertion decides what a future edit to condition_ld_matrix.py can change silently |
| shared GPFS working tree ↔ concurrent executors | Another quick task (260916-ocb) and other terminals write the same tree/branch and run suites on the same node |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-oyq-01 | Tampering | notice quote of trsx5 | mitigate | The enforcer checks the posted-body size (9695) FIRST, then md5 c19be8b2…, then derives line 19 via splitlines() and requires the whitespace-normalized sentence in each notice BODY; `sentence_altered` control observed RED |
| T-oyq-02 | Tampering | freeze scope of condition_ld_matrix.py | mitigate | Rescope limited to `code_only = ("src/python/condition_ld_matrix.py",)` with subset + exact byte-pinned-list assertions; Proofs B2/B3/C-iv show code edits RED, B4/B5 show the other two still byte-pinned |
| T-oyq-03 | Repudiation | freeze-scope change | mitigate | DEC-2026-09-16-condition-ld-matrix-freeze-code-only appended (byte-prefix-verified append-only, with an observed-RED control) with Carter's verbatim choice, the measured premise, the working-tree-vs-commit semantics and explicit non-changes; tests cite the ID |
| T-oyq-04 | Tampering (silent guard weakening) | notice enforcer | mitigate | ast docstring extraction (not grep); 9 committed controls incl. moved-into-comment / string-constant with a "grep would be green" assertion and a premise-checked moved-to-end control; the same mutations observed RED on the real texts |
| T-oyq-05 | Denial of Service / collision | shared tree, branch, node load | mitigate | Pre-flight: clean tracked tree; RAM-1 fix + test + close-out HEAD; `ps`/`awk` live-pytest guard whose positive control is observed before its silence is trusted (pgrep rejected: self-match); R1 no pytest during a suite run; HEAD == expected_head before every commit; explicit-path staging; probes only in widened `git clone --shared` scratch clones outside the repo; R2 clone cleanup on every STOP; GPFS invalid-object = STOP |
| T-oyq-06 | Information disclosure | test/docstring text | accept | Only public OSF GUIDs, timestamps and posted text; no genotypes, no AoU data, no credentials, no network |
| T-oyq-07 | Tampering (false claim in notice) | "NOT called by the pipeline" | mitigate | `test_neither_notice_module_has_a_pipeline_caller` with a must-be-identity importer check, non-vacuity floors, and positive controls for the text and script-path detectors plus a docstring-only negative |
</threat_model>

<verification>
- Pre-flight: RAM-1 three checks pass; live-pytest positive control observed, real check silent; kht pre-flight GREEN.
- `pytest tests/m3/test_tcujq_withdrawal_notices.py` → 17 passed at HEAD; 3 failed / 14 passed at C2 (observed).
- `pytest tests/m3/test_source_freeze_pins.py tests/m3/test_source_freeze.py tests/m3/test_condition_ld_matrix.py tests/m3/test_write_conditioned_ld_npz.py` → all pass at HEAD.
- `git diff --numstat <PRE> HEAD` → exactly 5 files. Both src files have 0 deletions; DECISIONS.md passes `dec_prefix_check` with 0 deletions (NEG control RED).
- source_freeze.code_lines identical PRE vs HEAD for both src modules. PY_CODE_REF is still `bf16289`. `for rel in code_only:` present once.
- Proofs A, B1-B5 and C-i to C-iv observed with the expected colours, none concurrent with a suite run; 16/16 real-file mutation controls RED.
- Full tests/m3 PRE vs POST reconciled by name: +17 (new file, passed), -0, changed 0; the reconcile self-control was observed RED.
- kht verifier default mode: `RESULT GREEN checks=317 parsed=88 table=88 verified=88` at pre-flight and post-commit.
- Nothing outside files_modified changed. No push, no network, no OSF/AoU contact.
</verification>

<success_criteria>
- Both modules tell any reader (source, `help()`, `__doc__`) that the NaN→0 zeroing + ceiling + BRANCH_AFR_COND_* were
  pre-registered in tcujq and WITHDRAWN by trsx5. The notice quotes the posted text verbatim, states exactly which raise strings
  still carry the historical wording, points to the retained fully-NaN-row rule, keeps the history, and changes no code.
- condition_ld_matrix.py's freeze is CODE-only and proven able to fail. The other two frozen modules keep their byte pin by
  recorded decision.
- The notices and the "not called by the pipeline" claim each have a named, ast-based enforcer whose negative controls were
  observed RED and whose detectors have observed positive controls.
- The decision is on record in DECISIONS.md, verified append-only by a check that was itself observed RED. The suite reconciles by
  name, with only the 17 new tests added.
</success_criteria>

<output>
After completion, create `.planning/quick/260916-oyq-tcujq-withdrawn-by-trsx5-notices-in-cond/260916-oyq-SUMMARY.md`
(executor writes it and does NOT commit it; the orchestrator commits PLAN/SUMMARY/STATE).
</output>

<revision_log>
Revision 1 (plan-checker round 1, 2026-09-16). Every item was re-verified by the planner (M13-M18) before adoption.
- BLOCKER 1: live-pytest guard switched from self-matching `pgrep` to `ps`/`awk` (`live_pytest`), with an observed fake-process positive control in pre-flight.
- BLOCKER 2: `mkclone` widened to `tests src config Snakefile scripts bin <posted trsx5>` for ALL clones (NOT tools); R1 forbids any pytest during a suite run; Proof A moved after the PRE baseline; Steps 4-5 of Task 3 must finish before the POST run.
- W3: blank line after the fixture See-line. Planner prototype ALSO found and fixed a too-short fixture tail that let `moved_to_docstring_end` pass for free; that control now asserts its premise.
- W4: RAM-1 landed = fix commit on run_native_ld_panel.py + test file at HEAD + `docs(quick-260916-ocb)` close-out is HEAD.
- W5: DECISIONS append-only = byte-prefix check (`dec_prefix_check`) + numstat deletions 0 + observed-RED bullet-deletion control.
- W6: stem-parameterised `py_hits`/`pipeline_scan`; positive controls (m3_occlusion_lockstep.smk text hit; run_ld_build_plan.py script-path hit) and a docstring-only negative. Test count 15 → 17 (RED 3F/14P; GREEN 17P; 17 added in reconciliation).
- I7: key_link pattern → `for rel in code_only:` (0 hits at PRE).
- I8: N1 STATUS states the exact counts (2 of 4 raise strings say "pre-registered"; 1 of those names BRANCH_AFR_COND_DEFERRED).
- I9: N2 adds the retained fully-NaN-row rule pointer (trsx5:37).
- I10: no mk7ze mention (not needed).
- I11: kht verifier also run at pre-flight.
- I12: R2 clone cleanup on every STOP; the `$SCRATCH exists` refusal explains the cleanup; DECISIONS records the working-tree-vs-commit semantics.
- N4 comment shortened to 83 characters.
</revision_log>

<orchestrator_addendum date="2026-09-16" source="plan-checker iteration 2 (0 blockers / 1 warning / 3 info) — adopted under Carter's --auto --chain">
BINDING; overrides conflicting text above. Record each in the SUMMARY.
O-1 (checker W-a, APPLIED IN PLACE above, Task 1 Step 8(ii)): the DECISIONS negative control previously printed "NEG RED (correct)" when `dec_prefix_check` was undefined (rc 127) or PRE unreadable (rc 2) — measured by the checker. It now sources lib.sh and accepts ONLY rc == 1; any other rc is a STOP.
O-2 (checker I-b): in Task 1 Step 1, run (d) the live-pytest guard with an INLINE `ps -u "$USER" -o pid=,args= | awk '$2 ~ /python/ && / -m pytest/ && /tests\/m3/'` (plus its fake-process positive control) and (f) the pre-flight kht verifier run BEFORE (c) creates `$SCRATCH` (write the kht output to a temp file under the orchestrator scratchpad first, then move it into `$SCRATCH` once created), so a STOP at (d)/(f) leaves no `$SCRATCH` and a re-launch is not blocked.
O-3 (checker I-a): the orchestrator guarantees the RAM-1 close-out commit subject starts `docs(quick-260916-ocb)` and that NOTHING else is committed before this executor launches (this PLAN stays untracked until the oyq close-out). If HEAD's subject is anything else at pre-flight, STOP and report.
O-4 (checker I-c): a load-induced flake in `tests/m3/test_run_plink_peak_rss.py` during reconciliation stays a hard STOP (fails safe) — report it verbatim with the junit message; do not re-run to green.
</orchestrator_addendum>
