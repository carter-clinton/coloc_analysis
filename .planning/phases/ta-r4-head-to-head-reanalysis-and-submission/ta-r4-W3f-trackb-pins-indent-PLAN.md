---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.5c
slug: W3f-trackb-pins-indent
type: execute
wave: 15.5c
depends_on: ["ta-r4-W3f-ukb-panels-biallelic"]
gap_closure: true
files_modified:
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-trackb-pins-indent-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-trackb-pins-and-push-reply-2026-11-19.txt
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-trackb-n1-emit-line-reply-2026-11-19.txt
  - .planning/DECISIONS.md
  - tests/m3/test_variant_catalog_fallback_legacy_semantics.py
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/deferred-items.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-review-suite-and-close-PLAN.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md
  - .planning/STATE.md
  - .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-trackb-pins-indent-SUMMARY.md
autonomous: true
requirements:
  - REQ-SNAKEMAKE-CI
  - REQ-NEGATIVE-CONTROLS
  - REQ-SUSIE-RSS-POLICY

must_haves:
  truths:
    - "test_the_five_must_not_move_sites_are_byte_identical[too_many_variants_payload] passes: the default-path payload at HEAD equals dc4bbd2's line by line after stripping LEADING spaces/tabs only. Line count, field order, interior and trailing characters are compared exactly"
    - "The other four MUST-NOT-MOVE regions (init_pair, path1_block, no_variants_payload, success_payload) are still compared byte-for-byte; re-indenting any one of them in memory goes RED"
    - "The too_many_variants extractor is shown to return the DEFAULT-path payload (no 'after LD restriction', no cap_stage); the N1 flag-true payload has both and is a different block"
    - "test_the_symbol_scoped_diff_is_exactly_one_removed_line passes against dc4bbd2. Within one hunk, a removed and an added line differing only in leading whitespace cancel as a re-indentation. Removed must be exactly [variant_catalog_fallback <- TRUE]; added must be exactly the one N1 emit line (Carter, Question 3: A). Two stricter checks, added by the planner and not part of Carter's choice: the line sits in the N1 payload, and the file carries exactly one more emit line than dc4bbd2 (2 -> 3)"
    - "The 20 new test ids listed in <new_tests> exist and pass. Each negative control is in memory, observed failing, and leaves the working tree unchanged; indentation alone passes for both payload and diff"
    - "The module's 9 other tests are AST-identical and green. PRE_K1_REF is still dc4bbd2. No file under src/ changes"
    - "FULL (Slurm) per id vs full_15_5b.xml: 0 removed; exactly 2 outcome changes, the two deferred ids failed -> passed; added ids = exactly the 20 in <new_tests>, all passed; totals 2,555 = 2,502 P / 53 S / 0 F"
    - "deferred-items.md marks both items resolved; the 6 W4a ids are recorded as deliberate renames (7a3415df; ade4e9c5 then bed315d4; 92caa306), and 15.6's FULL reconciliation is scoped to allow exactly those 6 removed ids, each with its named successor present, plus this plan's 20 tests/m3 ids"
  artifacts:
    - path: "tests/m3/test_variant_catalog_fallback_legacy_semantics.py"
      provides: "_lstrip_lines, _assert_region_unmoved, _symbol_scoped_changes, _assert_symbol_diff_is_k1_only, _difflib_diff, N1_CAP_ANCHOR, LEGACY_KEY_EMIT, INDENT_INSENSITIVE_REGIONS and the 20 tests in <new_tests>"
    - path: ".planning/DECISIONS.md"
      provides: "DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation, quoting both reply files byte-for-byte; names 15.5c's own §C exceptions"
    - path: ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-review-suite-and-close-PLAN.md"
      provides: "depends_on + the scoped FULL-reconciliation allowance (6 renames + 20 tests/m3 ids), nothing else"
  key_links:
    - from: "test_the_five_must_not_move_sites_are_byte_identical"
      to: "_assert_region_unmoved"
      via: "the indentation-insensitive branch applies only to region == too_many_variants_payload"
      pattern: "INDENT_INSENSITIVE_REGIONS"
    - from: "test_the_symbol_scoped_diff_is_exactly_one_removed_line"
      to: "_assert_symbol_diff_is_k1_only(diff, new_src, old_src)"
      via: "git diff dc4bbd2 -- run_susie_rss.R (working tree), as today"
      pattern: "_assert_symbol_diff_is_k1_only\\("
    - from: "the NC-I4/I5/I7/I8[interior] diff controls"
      to: "_assert_symbol_diff_is_k1_only"
      via: "_difflib_diff over in-memory sources; the parity test shows git and difflib agree on the real source"
      pattern: "difflib.unified_diff"
---

<objective>
Gap closure for the two tests/m3 failures in deferred-items.md, red since 6c6e9546 (the 15.1 N1 cap move). Per
Carter 2026-11-19: "Ignore indentation (Recommended)" (Question 1) and "A: Allow the one N1 emit line (Recommended)"
(Question 3).

N1 (DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze) wrapped the default-path `too_many_variants`
block of `run_susie_rss.R` in `if (!cap_after_ld) { ... }`, re-indenting it by 2 spaces. It also added a flag-true
payload, and that payload writes one more `variant_catalog_fallback = variant_catalog_fallback` line.

The two pins in `tests/m3/test_variant_catalog_fallback_legacy_semantics.py` compare raw text against dc4bbd2:
- The payload pin fails on indentation alone.
- The symbol-scoped diff fails on that re-indentation, and also on the one new N1 emit line.

This plan changes only that test file. dc4bbd2 stays the reference, and every other check keeps its strength.

Purpose: 15.6 runs FULL and must not stop on these two failures or on the 6 renamed W4a ids.
Output:
- the test-file change with in-memory negative controls;
- a DEC;
- FULL reconciled per id;
- records;
- the 15.6 depends_on plus a scoped edit to its FULL reconciliation.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/deferred-items.md
@.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-ukb-panels-biallelic-SUMMARY.md
@tests/m3/test_variant_catalog_fallback_legacy_semantics.py

**Standing rules:** PLAN-INDEX §A and §B.
- Stage explicit paths only; never `git add .` or `-A`. Never stage `.planning/config.json` or the two
  `data/processed/...` deletions.
- RED first, with the negative controls observed failing.
- Pin behaviour, not text.
- A count is a claim: reconcile it by component.
- Close per §C, **without `git push`**; the orchestrator pushes.

Python: `PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11`. Scratch: `W=data/r4/tmp/w3f/indent/`
(create it). This module is pure text plus `git` and runs in under a second, so it runs inline. FULL runs only under
sbatch. Run the module through pytest from the repo root; a bare import fails on `conftest.R_SUBPROCESS_TIMEOUT_S`.

**Forbidden:**
- Any edit under `src/`, including `run_susie_rss.R`.
- Changing `PRE_K1_REF` (it stays `"dc4bbd2"`).
- Editing any of the module's other 9 tests, or any other test file.
- Writing a file on disk from a negative control.
- Editing anything in the 15.6 PLAN beyond what Task 2 step 4 names.
- Push, fires, OSF.

**Measured at planning (re-measured in Task 1 step 1; do not copy).**
- HEAD 61201774; origin/m3-W2-aou-deltas..HEAD = 0. Module result: 2 failed, 9 passed.
- `TOO_MANY_ANCHOR` (`if (nrow(subset) > SUSIE_MAX_VARIANTS)`) occurs once at HEAD and once at dc4bbd2.
  - The N1 block starts `if (cap_after_ld && nrow(subset) > SUSIE_MAX_VARIANTS)` (run_susie_rss.R:1079), which does
    not contain the anchor.
  - So the extractor returns the default payload (:967 onwards).
- Default payload:
  - 17 lines on both sides, equal after `lstrip()`.
  - The HEAD side has 0 lines with trailing whitespace and contains neither "after LD" nor "cap_stage".
  - The other four regions are byte-equal.
- Symbol-scoped diff, `git diff dc4bbd2 -- run_susie_rss.R`: the code lines that mention a fallback symbol are the
  set of 4 (hunk header, raw line) pairs below. Line numbers (1-based in the diff output) are for reading only;
  **compare by the pair, never by position**.

  | hunk header | raw diff line | role |
  |---|---|---|
  | `@@ -943,41 +963,45 @@ if (nrow(subset) == 0) {` | `-    variant_catalog_fallback = variant_catalog_fallback` | default payload, dc4bbd2 indentation (diff line 65) |
  | `@@ -943,41 +963,45 @@ if (nrow(subset) == 0) {` | `+      variant_catalog_fallback = variant_catalog_fallback` | the same line re-indented (diff line 99) |
  | `@@ -1006,11 +1030,24 @@ repeat {` | `-    variant_catalog_fallback <- TRUE` | the K-1 deletion (diff line 126) |
  | `@@ -1030,6 +1067,51 @@ if (!is.null(ld_result$subset_idx)) {` | `+    variant_catalog_fallback = variant_catalog_fallback` | N1 flag-true payload, run_susie_rss.R:1102 (diff line 184) |

- Lines equal to `variant_catalog_fallback = variant_catalog_fallback` after strip(): 2 at dc4bbd2 (the no_variants
  and too_many payloads) and 3 at HEAD (plus the N1 payload). The success payload's line ends in a comma and is not
  counted.
- The W4a vs 15.5b comparison by id:
  - tests/m3 adds 0 ids. The only tests/m3 outcome changes are the 2 deferred ids, passed → failed.
  - Exactly 6 W4a ids are removed, and they are the renames.
  - All 311 HEAVY ids (`heavy_15_5b.xml`) are inside `full_15_5b.xml`.

**Carter's decisions (record; quote byte-for-byte via `cat`, never retype; never quote this plan's wording):**
- `W3f-carter-trackb-pins-and-push-reply-2026-11-19.txt`, sha256
  `55d716a4ce809fcad7d4c83a4ceaa2606fc6852aff401b65a1339f81985da61d`.
  - Q1 → "Ignore indentation (Recommended)". It was described to him as: "Small gap plan 15.5c. Compare each line
    with its leading whitespace stripped (the payload and the one-removed-line diff), keep dc4bbd2 as the reference,
    add a negative control that changes one field and must fail, then run 15.6. Every check except the indentation
    one stays as it is."
  - Q2 (push 15.5b) is done.
- `W3f-carter-trackb-n1-emit-line-reply-2026-11-19.txt`, sha256
  `19c38aafbef0e7459c5a582d397d423a5f088a791615aa1f9806741967f54f12`. Q3 → "A: Allow the one N1 emit line
  (Recommended)". Quote the file itself.
- The DEC must say that the "in the N1 payload" and "2 → 3" checks are the planner's, stricter than Carter's choice,
  and not attributed to him.

**15.5c's own §C exceptions.** These are authorized by this plan and must be named in the DEC and the LOG:
- 2 pre-existing tests/m3 outcome changes (failed → passed);
- 20 new tests in tests/m3, where §C expects additions only in tests/ta_r4;
- QUICK and HEAVY not run separately. No file under src/ or tests/ta_r4 changes, and FULL runs tests/ta_r4 including
  every HEAVY id (311/311 HEAVY ids were in FULL at 15.5b). Task 2 re-checks that the HEAVY ids are in
  full_15_5c.xml; if any is missing, run HEAVY.
- PINS (`tests/m3/test_source_freeze_pins.py`) runs inside FULL.
</context>

<new_tests>
The exact new ids; N_new = 20. The two existing failing tests keep their names, so their ids do not change.
1. `test_the_too_many_extractor_picks_the_default_path_payload`
2. `test_the_real_payload_differs_from_pre_k1_only_in_indentation`. Raw HEAD payload != dc4bbd2 payload, and
   `_assert_region_unmoved` passes. Proves the normalization is exercised.
3. `test_nc_i1_a_payload_content_change_is_red[value]`
4. `test_nc_i1_a_payload_content_change_is_red[dropped]`
5. `test_nc_i1_a_payload_content_change_is_red[reordered]`
6. `test_nc_i1_a_payload_content_change_is_red[interior_ws]`
7. `test_nc_i1_a_payload_content_change_is_red[trailing_ws]`
8. `test_nc_i2_payload_indentation_alone_is_green[mixed]`
9. `test_nc_i2_payload_indentation_alone_is_green[plus4]`
10. `test_nc_i3_the_other_four_regions_stay_byte_exact[init_pair]`
11. `test_nc_i3_the_other_four_regions_stay_byte_exact[path1_block]`
12. `test_nc_i3_the_other_four_regions_stay_byte_exact[no_variants_payload]`
13. `test_nc_i3_the_other_four_regions_stay_byte_exact[success_payload]`
14. `test_the_difflib_diff_agrees_with_git_on_the_real_source` (parity)
15. `test_nc_i4_diff_with_the_path2_assignment_back_is_red`
16. `test_nc_i5_diff_reindentation_alone_is_green`
17. `test_nc_i6_the_reindent_cancellation_is_load_bearing`
18. `test_nc_i7_diff_extra_emit_outside_the_n1_payload_is_red`
19. `test_nc_i8_not_a_reindentation_is_not_cancelled[interior]`
20. `test_nc_i8_not_a_reindentation_is_not_cancelled[cross_hunk]`

Module: 11 → 31 ids. FULL expected: 2,535 + 20 = 2,555 ids = (2,480 + 2 + 20) = 2,502 P / 53 S / 0 F. If the
executor finds that a test must be split or merged, STOP and report: the list is the contract that both FULL
reconciliations are checked against.
</new_tests>

<interfaces>
tests/m3/test_ld_read_path.py (imported, read-only):
  _brace_block(text, anchor) -> str      # first text.find(anchor), balanced {...}
  _paren_block(text, anchor) -> str      # first text.find(anchor), balanced (...)
  _success_result_block(src) -> str; _shell_command_block(smk) -> str
tests/m3/test_variant_catalog_fallback_legacy_semantics.py (existing):
  PRE_K1_REF = "dc4bbd2"; LEGACY_KEY_ASSIGNMENT = "variant_catalog_fallback <- TRUE"
  PATH1_ANCHOR, PATH2_ANCHOR, NO_VARIANTS_ANCHOR, TOO_MANY_ANCHOR
  _git_show, _pre_k1_source, _code_lines, _init_pair_region, _early_exit_payload(src, anchor),
  _assert_path2_does_not_set_the_legacy_key(text), _named_region(src, name), MUST_NOT_MOVE_REGIONS
  NC-K2 pattern (lines 233-263): unique marker asserted count == 1 -> in-memory replace -> pytest.raises -> assert
  SUSIE_R.read_text() == src
New, this plan (exact names):
  N1_CAP_ANCHOR = "if (cap_after_ld && nrow(subset) > SUSIE_MAX_VARIANTS)"
  LEGACY_KEY_EMIT = "variant_catalog_fallback = variant_catalog_fallback"
  INDENT_INSENSITIVE_REGIONS = frozenset({"too_many_variants_payload"})
  _lstrip_lines(text) -> list[str]              # [ln.lstrip(" \t") for ln in text.splitlines()]
  _assert_region_unmoved(region, new, old) -> None
  _symbol_scoped_changes(diff_text, cancel_reindent=True) -> (removed: list[str], added: list[str], n_reindented: int)
  _assert_symbol_diff_is_k1_only(diff_text, new_src, old_src) -> None    # no cancel_reindent kwarg
  _difflib_diff(old_src, new_src) -> str        # "".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), "a", "b"))
data/r4/tmp/w3f/ukbbi/junit_cmp.py <base.xml> <new.xml>: prints "removed N", "added N ...", "outcome changes N", "  ~ <id> a -> b", "tests/m3 outcome changes N"
data/r4/tmp/w3f/ukbbi/close_b.sh: the FULL invocation (tests/ta_r4 tests/m3 tests/phase1 tests/phase2, -p no:cacheprovider, --junitxml)
</interfaces>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Gate, DEC, indentation-insensitive payload and diff pins with in-memory negative controls</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-trackb-pins-indent-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-trackb-pins-and-push-reply-2026-11-19.txt, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/W3f-carter-trackb-n1-emit-line-reply-2026-11-19.txt, .planning/DECISIONS.md, tests/m3/test_variant_catalog_fallback_legacy_semantics.py</files>
  <read_first>
    - tests/m3/test_variant_catalog_fallback_legacy_semantics.py (whole file; the NC-K2 pattern at :233-263)
    - tests/m3/test_ld_read_path.py :117-170 (_brace_block, _paren_block, _success_result_block)
    - src/legacy/region_analysis/scripts/run_susie_rss.R :960-1000 and :1079-1113 (read only)
    - .planning/DECISIONS.md, entries DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze and
      DEC-2026-11-18-ta-r4-ukb-native-multiallelic-a1 (format to mirror)
  </read_first>
  <behavior>
    - #1 extractor choice:
      - TOO_MANY_ANCHOR count == 1 at HEAD;
      - the extracted payload has neither "after LD restriction" nor "cap_stage";
      - `_early_exit_payload(src, N1_CAP_ANCHOR)` has both, and differs from it.
    - #2: raw HEAD payload != dc4bbd2 payload, and `_assert_region_unmoved("too_many_variants_payload", head, old)` passes.
    - #3-7 NC-I1. Each perturbation of the default payload is RED:
      - [value]: `"too_many_variants"` → `"too_many_variantz"`;
      - [dropped]: the `notes = ...` line deleted;
      - [reordered]: the `chrom = reg$chr,` and `start = reg$start,` lines swapped;
      - [interior_ws]: `trait = opt$trait` → `trait  = opt$trait`;
      - [trailing_ws]: one line gets a trailing space.
    - #8-9 NC-I2. Indentation-only perturbations pass. Each asserts perturbed != old AND perturbed != head, so neither
      equals a real side:
      - [mixed]: lines after the first alternate: odd-indexed lines get their leading whitespace replaced by one tab,
        even-indexed lines get +2 spaces;
      - [plus4]: every line after the first gets +4 spaces.
    - #10-13 NC-I3. Each of the four other regions, re-indented +2 in memory, is RED under `_assert_region_unmoved`
      (they stay byte-exact).
    - #14 parity:
      - `_assert_symbol_diff_is_k1_only(_difflib_diff(old, src), src, old)` passes, as the git diff does;
      - `_symbol_scoped_changes` gives n_reindented ≥ 1 on both the git diff and the difflib diff.
    - #15 NC-I4: the NC-K2 splice (Path-2 assignment re-added) → `_difflib_diff` → predicate RED.
    - #16 NC-I5: the no_variants payload's emit line re-indented +2 in memory → difflib diff → predicate passes, and
      n_reindented == parity's + 1.
    - #17 NC-I6: asserts directly on `_symbol_scoped_changes(git_diff, cancel_reindent=False)`:
      - n_reindented == 0;
      - `LEGACY_KEY_EMIT in removed`;
      - `removed != [LEGACY_KEY_ASSIGNMENT]`.

      This proves the predicate's first assertion would fail without cancellation. The predicate has no
      cancel_reindent kwarg.
    - #18 NC-I7: a second `variant_catalog_fallback = variant_catalog_fallback` line inserted into the no_variants
      payload in memory → difflib diff → predicate RED.
    - #19 NC-I8[interior]: the default payload's emit line changed to `variant_catalog_fallback = used_variant_catalog`
      → difflib diff → predicate RED.
    - #20 NC-I8[cross_hunk]: a synthetic two-hunk unified-diff string, `-    <emit>` in hunk 1 and `+      <emit>` in
      hunk 2 → `_symbol_scoped_changes` returns n_reindented == 0, with both lines kept.
  </behavior>
  <action>
    0. **Gate.**
       - HEAD is 15.5b's docs commit or later; record `git rev-list --count origin/m3-W2-aou-deltas..HEAD`.
       - `sha256sum` of both reply files goes to `$W/replies.sha256`, and they must equal the two sha256 values in
         <context>.
       - `grep -cFx 'Carter reply (verbatim, selected option): A: Allow the one N1 emit line (Recommended)'` on the n1
         emit-line file must print 1. Otherwise → STOP, no edit.
       - `git rev-parse HEAD > $W/start_sha.txt`.
    1. **Re-measure.**
       - Run the module inline with `set -o pipefail`: expect exactly 2 failed / 9 passed.
       - In a throwaway `$W/measure.py`, parse the git diff into hunks and print the set of (hunk header, raw line)
         pairs for symbol-mentioning code lines. Also print the emit counts (2 / 3) and the payload facts.
       - The set must equal the 4 pairs in <context> exactly, compared as sets of tuples, not by line position. Any
         difference → STOP and report.
    2. **DEC.** Append `## 2026-11-19 — DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation: the two K-1
       pins ignore leading whitespace; the one N1 emit line is allowed (Carter)`, mirroring the 2026-11-18 entry.
       - Decider.
       - Both reply files with their sha256, each quoted with `cat` inside a ```text fence. Afterwards, extract each
         fenced block and `cmp` it to its file.
       - Scope:
         - only the test file; PRE_K1_REF stays dc4bbd2;
         - normalization strips leading spaces/tabs only, and applies only to `too_many_variants_payload` and to
           same-hunk re-indentation pairs in the symbol-scoped diff;
         - the added side allows exactly the one N1 emit line (Carter Q3 A).
       - A sentence stating that the two extra checks (in the N1 payload; 2 → 3) are the planner's, stricter than
         Carter's choice, and not attributed to him.
       - Not authorized: any `src/` edit, the other 9 tests, the other four regions.
       - The 15.5c §C exceptions from <context>, named as authorized.

       Commit 1 (`docs(ta-r4-W3f): DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation + Carter replies +
       15.5c PLAN (15.5c)`). Stage explicitly: this PLAN file, DECISIONS.md and the two reply files.
    3. **RED first.** Add the constants, helpers and the 20 tests from <new_tests>/<behavior>, with these helper bodies
       first:
       - `_assert_region_unmoved`: byte-exact `new == old` for every region;
       - `_symbol_scoped_changes`: ignores `cancel_reindent`, never cancels;
       - `_assert_symbol_diff_is_k1_only`: the old `removed == [..]` / `added == []`.

       Rewire the two failing tests to call them, keeping both names. Run the module (`set -o pipefail`; output in
       `$W/red.txt`). Expected RED:
       - the 2 original tests;
       - #2, #8, #9, #14, #16.

       Each of #3-7, #10-13, #15, #18 and #19 must already pass, because it raises as intended. #1, #17 and #20 are
       green under the stub, which never cancels. #17 shows its value only in contrast with #14's n_reindented ≥ 1
       once cancellation exists; record all three outcomes.
    4. **GREEN.**
       - `_assert_region_unmoved`:
         - for a region in INDENT_INSENSITIVE_REGIONS: assert equal line counts, then
           `_lstrip_lines(new) == _lstrip_lines(old)`; the message names the region, the first differing line index
           and both raw lines;
         - every other region keeps the existing byte-exact assertion and message verbatim.
       - `_symbol_scoped_changes`:
         - Split on `@@` hunk headers. Per hunk, apply today's filters unchanged: skip `+++`/`---`; keep `+`/`-`
           lines only; strip the marker first; drop `#` comments; keep only lines that mention
           `variant_catalog_fallback` or `ld_overlap_zero_fallback`.
         - Keep the raw bodies. If `cancel_reindent`, walk the removed bodies in order. Pair each with the first
           unpaired added body in the **same hunk** for which `a != r and a.lstrip(" \t") == r.lstrip(" \t")`, and
           drop both.
         - Return the stripped remainders and the pair count.
       - `_assert_symbol_diff_is_k1_only` (calls `_symbol_scoped_changes(diff_text)` with the default
         cancel_reindent=True), asserting:
         - `removed == [LEGACY_KEY_ASSIGNMENT]` (existing message);
         - `added == [LEGACY_KEY_EMIT]` (message cites the N1 DEC and the 15.5c DEC);
         - `_code_lines(_early_exit_payload(new_src, N1_CAP_ANCHOR)).count(LEGACY_KEY_EMIT) == 1`;
         - `_code_lines(new_src).count(LEGACY_KEY_EMIT) == _code_lines(old_src).count(LEGACY_KEY_EMIT) + 1`.
       - The diff test keeps its `git diff PRE_K1_REF -- SUSIE_R_REL` call and the `diff.strip()` non-vacuity assert,
         then calls the predicate on (diff, `SUSIE_R.read_text()`, `_pre_k1_source()`).
       - Docstrings: one sentence each for the two tests and the module docstring's claim 2, citing the 15.5c DEC.
         Keep edits short.
       - Every NC follows NC-K2:
         - assert the marker or region count == 1 before replacing, and `perturbed != src`;
         - perturb by replacing the extracted region inside an in-memory copy of the full source, then re-extract;
         - wrap RED cases in `pytest.raises(AssertionError)`, and check the message names the region or K-1;
         - end with `assert SUSIE_R.read_text() == src`.
       - Run the module (`set -o pipefail`): exactly 31 passed, 0 failed. Then `pytest --collect-only -q` on the module
         and diff its id list against the 11 old ids + the 20 in <new_tests>; it must be equal.
    5. **No-weakening** (output to `$W/noweaken.txt`):
       - AST comparison of the file at `$(cat $W/start_sha.txt)` vs the working tree. `ast.dump` must be equal for
         every pre-existing top-level node except the two rewired test functions and the module docstring. That
         includes the 5 other test functions, every existing helper, `_named_region`, `MUST_NOT_MOVE_REGIONS` and the
         `PRE_K1_REF` assignment.
       - `git diff --quiet HEAD -- src/`.
       - `git status --porcelain -- tests/` lists only this file.
    6. Commit 2 (`test(ta-r4-W3f): K-1 pins ignore leading whitespace; N1 emit line allowed; 20 in-memory tests
       (15.5c)`): the test file only.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && set -o pipefail && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/m3/test_variant_catalog_fallback_legacy_semantics.py -q -p no:cacheprovider && test "$(/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 -m pytest tests/m3/test_variant_catalog_fallback_legacy_semantics.py --collect-only -q -p no:cacheprovider | grep -c '::')" = 31 && git diff --quiet HEAD -- src/ && test "$(grep -c 'DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation' .planning/DECISIONS.md)" -ge 1 && grep -qx 'PRE_K1_REF = "dc4bbd2"' tests/m3/test_variant_catalog_fallback_legacy_semantics.py && sha256sum -c data/r4/tmp/w3f/indent/replies.sha256</automated>
  </verify>
  <done>
    - The gate passed. Both replies and this PLAN are committed, byte-matched, with the DEC.
    - RED was observed as listed, then the module is 31/31 green and its ids equal the 11 old ids + <new_tests>.
    - The on-disk file never changed during the NCs. The AST check is clean and src/ is unchanged.
    - Two commits with explicit paths; no push.
  </done>
</task>

<task type="auto">
  <name>Task 2: FULL under Slurm, per-id reconciliation, W4a rename map, scoped 15.6 edit, records (no push)</name>
  <files>.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/deferred-items.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-review-suite-and-close-PLAN.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-PLAN-INDEX.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-LOG.md, .planning/STATE.md, .planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-trackb-pins-indent-SUMMARY.md</files>
  <read_first>
    - data/r4/tmp/w3f/ukbbi/close_b.sh, data/r4/tmp/w3f/ukbbi/junit_cmp.py, close_b_1987856.out
    - ta-r4-LOG.md, the "2026-11-18 — W3f 15.5b" entry (format); STATE.md, the ★ RESUME HERE ★ block (lines 29-41)
    - ta-r4-PLAN-INDEX.md rows 44-47 and §C (the full-suite rule)
    - the 15.6 PLAN: frontmatter (lines 1-8), the FULL must_have (line 26), Task 2 (lines 117-147)
  </read_first>
  <action>
    1. **FULL (sbatch).**
       - Copy close_b.sh to `$W/close_c.sh`, changing only `D=data/r4/tmp/w3f/indent` and the junit name
         `full_15_5c.xml`.
       - Run `git status --porcelain -- tests src` first; it must be empty.
       - Submit: `sbatch -p compute -A clintonlab_cpu -q normal -t 03:00:00 --mem=48G -o $W/close_c_%j.out
         $W/close_c.sh`. 48G is close_b's allocation.
       - It is done when the job is gone from `squeue` and the xml and the pytest tail line both exist.
       - Restore any test side-effect file (e.g. `tests/m3/sparse_parent_benchmark.tsv`) to HEAD.
    2. **Reconcile vs 15.5b.** Write `junit_cmp.py data/r4/tmp/w3f/ukbbi/full_15_5b.xml $W/full_15_5c.xml >
       $W/cmp_15_5b.txt`. Then assert with a script, `$W/check_15_5b.py`, which exits non-zero on any miss:
       - removed == 0;
       - the added id set == the 20 ids in <new_tests>, prefixed `tests.m3.test_variant_catalog_fallback_legacy_semantics::`,
         all passed;
       - exactly 2 outcome changes, both failed → passed, and they are the two deferred ids;
       - totals 2,555 = 2,502 P / 53 S / 0 F;
       - every id in `data/r4/tmp/w3f/ukbbi/heavy_15_5b.xml` is present in full_15_5c.xml. If not, run HEAVY in sbatch
         before going on.

       Any miss → STOP and report; do not write records claiming a clean close.
    3. **W4a rename map.** Run `junit_cmp.py data/r4/tmp/w4a/full_W4a.xml $W/full_15_5c.xml > $W/cmp_W4a.txt` and
       `$W/check_W4a.py`. It asserts that:
       - the removed set is exactly these 6 ids, and each named successor is present and passed:
         - `tests.ta_r4.test_coloc_pair_r4::test_panel_rsid_override_is_refused_not_dropped` →
           `..._maps_through_panel_not_dropped` (7a3415df, the N2 spec update);
         - `tests.ta_r4.test_run_aggregation::test_draft_writes_exactly_17_draft_tables` → `..._exactly_19_...`
           (17 → 18 in ade4e9c5, 18 → 19 in bed315d4);
         - `tests.ta_r4.test_contrast_stats::test_category_edges[kw11-kappa_ok-True]`, `[kw12-kappa_ok-False]`,
           `[kw13-kappa_ok-True]`, `[kw14-kappa_ok-False]` → `[kw12-kappa_ok-True]`, `[kw13-kappa_ok-False]`,
           `[kw14-kappa_ok-True]`, `[kw15-kappa_ok-False]`. 92caa306 (N7) inserted one mcnemar case (15 → 16), and
           `[kw11-mcnemar-ns]` is present;
       - tests/m3 relative to W4a: the added ids are exactly the 20, and there are 0 outcome changes on common
         tests/m3 ids.

       Confirm each commit with `git log -S'<old name>' --oneline -- tests/ta_r4`, or `-S'exactly_18'` /
       `-S'exactly_19'` for the tables test.
    4. **Scoped 15.6 edit.** In `ta-r4-W3f-review-suite-and-close-PLAN.md`, change only:
       - (a) frontmatter `depends_on`: add `"ta-r4-W3f-trackb-pins-indent"`;
       - (b) the FULL must_have (line 26): after "0 removed ids", add "except exactly the 6 W4a ids in deferred-items.md's
         rename map, each with its named successor present", and after "0 outcome changes in tests/m3", add "on common
         ids; tests/m3 additions only the 20 15.5c ids (DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation)";
       - (c) Task 2 step 2's "Required: removed 0" sentence and the acceptance criteria "removed 0" and "tests/m3 outcome
         Counter identical" bullets, with the same two allowances and a pointer to deferred-items.md.

       Add nothing else. Check that `git diff` of the file touches only those lines, and paste the diff into the LOG.
    5. **Records.**
       - deferred-items.md: append a RESOLVED line under each 2026-11-18 item, keeping the original text:
         - Item 1: the 15.5c commit shas, the DEC id, the FULL job id, 2 F → P.
         - Item 2: the rename map with commits; "deliberate renames, not lost tests; 15.6's FULL reconciliation
           allows exactly these 6 (scoped edit, 15.5c)".
       - PLAN-INDEX: insert a 15.5c row after 15.5b (`ta-r4-W3f-trackb-pins-indent-PLAN.md`, "W3f gap closure
         (tests/m3 K-1 pins ignore leading whitespace after the N1 re-indent; the one N1 emit line allowed; Carter
         2026-11-19 Q1 + Q3 A; test file only; 15.6 FULL scope for the W4a renames; no push)").
       - LOG: entry "2026-11-19 — W3f 15.5c (...)". It records:
         - gate shas, RED/GREEN counts, each NC and its observed failure, the AST check;
         - FULL job id and wall time, both per-id reconciliations with the arithmetic, the rename map;
         - the 15.6 diff;
         - the 15.5c §C exceptions named as authorized: 2 tests/m3 outcome changes; 20 new tests/m3 ids; QUICK/HEAVY
           not run separately, because no src/ or tests/ta_r4 file changed and FULL contains all HEAVY ids (checked in
           step 2).
       - STATE.md: a new ★ RESUME HERE — LATEST ★ block for 15.5c ("NEXT = 15.6. NOT PUSHED"). Mark the 15.5b block
         SUPERSEDED, following the existing pattern.
       - SUMMARY.
    6. **Close** per §C without push. Run `git fsck --connectivity-only` before and after. Commit 3
       (`docs(ta-r4-W3f): 15.5c LOG, STATE, SUMMARY, deferred-items, 15.6 depends_on + FULL scope (no push)`) with
       the six paths above, staged explicitly.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && set -o pipefail && W=data/r4/tmp/w3f/indent && P=.planning/phases/ta-r4-head-to-head-reanalysis-and-submission && grep -qx "removed 0" $W/cmp_15_5b.txt && grep -qx "outcome changes 2" $W/cmp_15_5b.txt && test "$(grep -c ' failed -> passed$' $W/cmp_15_5b.txt)" = 2 && grep -qx "removed 6" $W/cmp_W4a.txt && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 $W/check_15_5b.py && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python3.11 $W/check_W4a.py && test "$(grep -c RESOLVED $P/deferred-items.md)" -ge 2 && head -8 $P/ta-r4-W3f-review-suite-and-close-PLAN.md | grep -qF '"ta-r4-W3f-trackb-pins-indent"' && grep -q "15.5c" $P/ta-r4-PLAN-INDEX.md && git diff --quiet HEAD -- src/ && test -z "$(git status --porcelain -- src tests .planning/DECISIONS.md $P/deferred-items.md $P/ta-r4-W3f-review-suite-and-close-PLAN.md)"</automated>
  </verify>
  <done>
    - FULL ran under Slurm. Against 15.5b: 0 removed; exactly the 2 deferred ids failed → passed; the added ids equal
      <new_tests>; 2,555 = 2,502 / 53 / 0.
    - Against W4a: exactly the 6 renames removed, each with its successor present, and tests/m3 adds only the 20.
    - The 15.6 edit is scoped (depends_on + the two allowances) and its diff is in the LOG.
    - Records are committed with explicit paths. Nothing is pushed.
  </done>
</task>

</tasks>

<enforcers>
| must_have | enforcer (fails when broken) | negative control (observed failing) |
|---|---|---|
| payload unmoved except indentation | test_the_five_must_not_move_sites_are_byte_identical[too_many_variants_payload] | #3-7 NC-I1 value / dropped / reordered / interior_ws / trailing_ws |
| normalization exercised, indentation alone passes | #2 (raw != old) + #8-9 NC-I2 mixed / plus4 (each != old and != head) | RED under the byte-exact stub (step 3) |
| normalization scoped to one region | the four other parametrizations, byte-exact | #10-13 NC-I3 |
| extractor returns the default payload | #1 | the N1 payload contains "after LD restriction" / cap_stage and differs from it |
| only the K-1 line removed | test_the_symbol_scoped_diff_is_exactly_one_removed_line | #15 NC-I4; #19 NC-I8[interior] |
| cancellation is load-bearing | #17 NC-I6 (direct on `_symbol_scoped_changes(..., cancel_reindent=False)`) together with #14 (n_reindented ≥ 1 with cancellation) | #14 RED under the stub (step 3) |
| pairing is same-hunk and whitespace-only | _symbol_scoped_changes | #20 NC-I8[cross_hunk], #19; #16 NC-I5 green |
| the only addition is the one N1 emit line | _assert_symbol_diff_is_k1_only (added list + N1 payload count + 2 → 3) | #18 NC-I7 |
| git and difflib agree | #14 parity | — (identity check) |
| the other 9 tests not weakened | AST comparison vs start_sha | — (identity check) |
| FULL unchanged apart from the fix | check_15_5b.py vs full_15_5b.xml | — (per-id identity) |
| W4a gaps are renames only | check_W4a.py | — (per-id identity) |
</enforcers>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| test pins → frozen R script | the pins keep the legacy run_susie_rss.R semantics from drifting unnoticed |
| Carter's replies → plan scope | relaxing a guard needs his recorded authorization |
| 15.5c → 15.6 reconciliation | loosening 15.6's removed-ids rule could hide a lost test |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-r4-W3f5c-01 | Tampering | K-1 pins (weakened beyond Carter's choice) | mitigate | lstrip(" \t") on one named region; same-hunk whitespace-only pairs; one allowed emit line, plus two stricter planner checks; 20 tests, the NCs observed RED; AST check of the other 9 tests |
| T-r4-W3f5c-02 | Repudiation | decision record | mitigate | both replies sha256-checked, quoted with cat and cmp-checked; the DEC separates Carter's choice from the planner's stricter checks; the gate refuses to edit without Q3 = A |
| T-r4-W3f5c-03 | Tampering | run_susie_rss.R / src | mitigate | no src path in files_modified; `git diff --quiet HEAD -- src/` in both verifies; each NC asserts the on-disk file is unchanged |
| T-r4-W3f5c-04 | Repudiation | FULL claim | mitigate | check_15_5b.py / check_W4a.py exit non-zero on any unexpected id; arithmetic in the LOG |
| T-r4-W3f5c-05 | Tampering | 15.6 removed-ids rule | mitigate | the allowance names exactly 6 ids, each with its successor present (check_W4a.py), plus exactly 20 tests/m3 ids; the diff of the 15.6 file goes into the LOG |
| T-r4-W3f5c-06 | Information disclosure | push | accept | no push here; the orchestrator pushes; nothing public |
</threat_model>

<verification>
- The module is 31/31 inline. FULL (Slurm) passes check_15_5b.py and check_W4a.py.
- `git diff $(cat data/r4/tmp/w3f/indent/start_sha.txt)..HEAD --name-only` ⊆ files_modified, with no path under src/.
- `PRE_K1_REF` is still `"dc4bbd2"`. The 15.6 PLAN diff is limited to depends_on plus the two named allowances.
- No push: `git log origin/m3-W2-aou-deltas..HEAD` lists the three 15.5c commits.
</verification>

<success_criteria>
- Both deferred tests/m3 tests pass against dc4bbd2. Only leading whitespace and the one N1 emit line are tolerated.
- The 20 listed tests exist, and every negative control was observed failing in memory.
- FULL is otherwise unchanged per id. The 6 W4a ids are recorded as renames, and 15.6 will accept exactly those.
- DEC, LOG, STATE, PLAN-INDEX, SUMMARY, deferred-items and the 15.6 edit are committed. Nothing is pushed.
</success_criteria>

<output>
After completion, create `.planning/phases/ta-r4-head-to-head-reanalysis-and-submission/ta-r4-W3f-trackb-pins-indent-SUMMARY.md`
</output>
