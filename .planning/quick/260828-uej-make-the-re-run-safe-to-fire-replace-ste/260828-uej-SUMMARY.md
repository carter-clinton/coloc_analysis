---
phase: quick-260828-uej
plan: 01
subsystem: m3-afr-ld-panel
tags: [pairwise-completeness, runbook-freshness-gate, stale-artifact-rotation, output-quarantine, false-invariant, composite-parse, prereg-prediction, m3-07, stage-b, fire-safety]

requires:
  - "quick-260826-qq9 (the ancestry-keyed manifest read; the instrument this plan makes SAFE TO RUN)"
  - "the five-way adversarial review banked at 260828-uej-CODEX-REVIEW-as-received.md"
provides:
  - "a behavioural STEP 0 freshness gate (content hash + byte size + last-touching commit + a POSITIVE capability check) replacing a commit-SUBJECT match that PASSED on the 8x code"
  - "STEP 2b ROTATE + a STEP 3 pre-flight existence guard, so the contaminated 871 MB artifact cannot be read as a fresh result"
  - "write-then-reconcile-then-quarantine in main(): <out>.SUSPECT + return 2, nothing survives at --out, ~4h18m of compute salvaged"
  - "an empty-after-strip --region-ids is an ERROR, not a silent 276-region scan"
  - "one closed FALSE INVARIANT + one composite-parse pin with its production divergence MEASURED and monitored"
  - "the derived, arithmetically-enforced pre-registration 353089 / 353090"
affects:
  - "the in-perimeter STEP 3 re-run procedure (NOT YET RUN)"

tech-stack:
  added: []
  patterns:
    - "recompute-the-pin-at-call-time (never a frozen SHA) for document<->code content gates"
    - "strip inline code spans, then word-boundary match, for never-delete enforcement in prose+command documents"
    - "^-anchored heading slices for document-section assertions"

key-files:
  created:
    - ".planning/quick/260828-uej-make-the-re-run-safe-to-fire-replace-ste/260828-uej-SUMMARY.md"
  modified:
    - "src/python/pairwise_completeness_scan.py"
    - "tests/m3/test_pairwise_completeness_scan.py"
    - ".planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md"
    - ".planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md"
    - ".planning/STATE.md  (WRITTEN, deliberately NOT staged/committed — see Deviations)"

decisions:
  - "The reconciliation is INVERTED, not weakened: write -> reconcile -> quarantine -> return 2. The arithmetic is byte-identical; only position and failure handling moved."
  - "The quarantine name is built by STRING CONCATENATION, never Path.with_suffix, and a prior .SUSPECT is ROTATED not clobbered."
  - "The STEP 0 gate is expressed in Python against _read_regions_tsv, never as a command-line flag, because the runbook's forbidden-token pin is load-bearing for the UNMODIFIED STEP 3 command."
  - "The composite whitespace divergence is RECORDED AND MONITORED, not closed — closing it would break the byte-faithful production mirror."
  - "N = 11 new tests, not the plan's 12. The plan's Task 2 arithmetic and its own bullet list disagree; reconciled by naming every test two independent ways."

metrics:
  duration: "~2h10m"
  tasks: 4
  commits: 4
  tests_added: 11
  tests_renamed: 1
  completed: "2026-08-28"
---

# quick-260828-uej: Make the re-run SAFE TO FIRE — Summary

A five-way adversarial review found the **instrument** sound and the **RUN** unsafe.
This plan replaced a freshness gate that matched a commit *subject* (and therefore
**passed on the 8x code**) with a content-hash + behavioural gate, moved the
contaminated 871 MB artifact off the read path three independent ways, inverted the
reconciliation so a disagreement costs a rename instead of ~4h18m of compute, closed
one false invariant, and pre-registered the derived `353089 / 353090`.

**NOTHING WAS FIRED. $0. THE RE-RUN HAS NOT HAPPENED.**

---

## Commits

| Task | Commit | Subject (truncated) |
|---|---|---|
| T1 | `cb199b6` | `fix(quick-260828-uej): T1 — write the TSV BEFORE the reconciliation and QUARANTINE it to .SUSPECT on disagreement …` |
| T2 | `bdaf705` | `test(quick-260828-uej): T2 — the ancestry-raise test was a FALSE INVARIANT (its own fixture FILENAME satisfied the assertion) …` |
| T3 | `5e2b31a` | `fix(quick-260828-uej): T3 — the runbook's freshness gate matched a COMMIT SUBJECT (which PASSED on the 8x code at 769afa6 …) …` |
| T4 | `9cf9baa` | `docs(quick-260828-uej): T4 — PRE-REGISTER the derived POOLED candidate rows 353089 (= 1,412,356 / 4, exact) and wc -l 353090 …` |

Branch `m3-W2-aou-deltas`, no worktree isolation, **explicit paths at every commit**
(never `git add .` / `-A`).

---

## The POST-Task-1 values the STEP 0 gate now pins

Measured from the committed tree, after T1 landed:

```
git status --porcelain src/python/pairwise_completeness_scan.py   (EMPTY)
md5sum  src/python/pairwise_completeness_scan.py   e03078ff73502c3c877b0d2ebf93941d
stat -c '%s'                                       73772
git log -1 --format='%h %s' -- <that file>         cb199b6 fix(quick-260828-uej): T1 — …
```

Pre-change values, for contrast (T1 changed BOTH, exactly as the plan predicted):
`664921c7943c8dc1ce4bba87fd4cb957` / `69258`.

### The gate's own capability block, EXECUTED LOCALLY (verbatim)

Extracted from the runbook and run as written:

```
manifest windows: 276 distinct region ids: 276
CAPABILITY CHECK PASSED
```

### Why the old gate had to go — MEASURED

```
git log -1 --format='%s' 769afa6 | grep -c 'quick-260825-qpf'   ->  1
git log -1 --format='%s' 352ac9e | grep -c 'quick-260825-qpf'   ->  0
```

`769afa6` is the commit the **contaminated** run pulled to. The old gate therefore
**PASSED on the 8x-duplication code** and **false-STOPPED on `352ac9e`**.

Pre-fix behaviour of the capability call, measured at `d8f4d54^` so the runbook's
"what each failure means" is not a guess:

```
_read_regions_tsv('config/ld_regions.tsv', None)                 -> 552 windows / 276 ids
_read_regions_tsv('config/ld_regions.tsv', None, ancestry='AFR') -> TypeError: unexpected keyword argument 'ancestry'
```

---

## RED FIRST — every new assertion, with what was actually seen

### T1 — the five assertions, RED against the pre-change code

`pytest -k "quarantine or suspect or stale_artifact or region_ids"` before implementing:

```
FAILED …::test_pooled_candidate_rows_disagreement_quarantines_the_output_and_returns_2
FAILED …::test_a_stale_artifact_at_out_does_not_survive_a_quarantined_run
FAILED …::test_a_preexisting_suspect_is_rotated_not_clobbered
FAILED …::test_the_quarantine_name_is_built_by_string_concatenation_not_with_suffix
FAILED …::test_an_empty_after_strip_region_ids_is_an_error_while_the_absent_flag_still_means_all_regions
5 failed, 2 passed, 99 deselected in 0.85s
```

The four quarantine reds all had the same cause — the code **raised** instead of
returning 2:

```
src/python/pairwise_completeness_scan.py:1533: ValueError: POOLED denominator disagreement: sum of per-region
n_candidate_rows = 3 but the emitted TSV carries 2 candidate rows. These MUST be the same basis; a difference
means at least one region was evaluated more than once (or a summary was built from a different row set).
```

The fifth proved the silent cost blow-up, via a monkeypatched `iter_bim_windows`
sentinel:

```
E   AssertionError: the scan STARTED on an empty --region-ids
```

### NC-1 — the SUCCESS-path stale test needed its own mutation

`test_a_stale_artifact_at_out_does_not_survive_a_successful_run` is green by
construction today (`write_tsv` opens `"w"`), so it was made RED by flipping
`open(out_path, "w", …)` to `"a"`:

```
md5 before  664921c7943c8dc1ce4bba87fd4cb957
md5 during  23b5a24da3f039e943b9b9481e0dca85
E       JUNK-STALE-CONTAMINATED-ROW-1
E       JUNK-STALE-CONTAMINATED-ROW-2 …
FAILED …::test_a_stale_artifact_at_out_does_not_survive_a_successful_run
md5 after restore  664921c7943c8dc1ce4bba87fd4cb957   (git status clean)
```

⚠ `"w"` and `"a"` are the **same byte length**, so
`feedback_negative_control_defeated_by_bytecode_cache` applies directly:
`src/python/__pycache__` was **cleared before and after** the mutation. This is the
one mutation in this plan where the trap was live.

### T2 NC-A — the FALSE INVARIANT, both observations side by side

The property is *"the error names the missing id"*. The mutation is deleting
`: {missing}` from the f-string in `_read_regions_tsv`.

**BEFORE the repair (fixture `eur_only.tsv`, assertion `"eur_only" in str(excinfo.value)`):**

```
--- running the UNREPAIRED test under the mutation (expect GREEN = FALSE INVARIANT) ---
1 passed, 105 deselected in 0.18s
```

The id came from the interpolated **path** — the fixture's own FILENAME satisfied
the assertion.

**AFTER the repair (fixture `anc_split.tsv`, assertion scoped to the message TAIL):**

```
tests/m3/test_pairwise_completeness_scan.py:2870: in test_region_only_in_the_unrequested_ancestry_raises_naming_the_id
    assert "eur_only" in tail, (
E   AssertionError: the missing id is not named AFTER the interpolated path — only the path itself carried it:
    "region ids not found in /…/anc_split.tsv for ancestry 'AFR'"
E   assert 'eur_only' in " for ancestry 'AFR'"
FAILED …::test_region_only_in_the_unrequested_ancestry_raises_naming_the_id
```

The mutation changes the file LENGTH (`73772` → `73761`), so the bytecode-cache trap
does **not** apply here. Restored md5 `e03078ff73502c3c877b0d2ebf93941d`, `git status`
clean.

### T2 NC-B — the composite parse

Removing `.strip()` from `_tsv_field` (`73772` → `73764`, length changes):

```
tests/m3/test_pairwise_completeness_scan.py:2922: in test_composite_whitespace_ancestry_parse_selects_where_production_drops
    assert got == [("padded", "1", 1000, 2000)], (
E   AssertionError: the scanner no longer selects a whitespace-padded ancestry cell: []
E   assert [] == [('padded', '1', 1000, 2000)]
```

Restored, md5 re-verified `e03078ff73502c3c877b0d2ebf93941d`.

### T2 NC-C — the latency monitor

Padding one ancestry cell in the real `config/ld_regions.tsv` (mutated and restored
within seconds; md5 `62d1fb0bf6333eea037146fc8f09c5e0` before **and** after,
`git status` clean):

```
E   AssertionError: the real manifest now carries padded-or-quoted ancestry cells, so the scanner-vs-production
    whitespace divergence pinned by test_composite_whitespace_ancestry_parse_selects_where_production_drops is
    LIVE and must be closed, not recorded: [(2, '  AFR  ')]
```

### T3 NC-D — the content-hash enforcer

Appending one comment line to the scanner (`73772` → `73834`):

```
E   AssertionError: the STEP 0 gate does not pin the CURRENT scanner md5 9add4f958d4f9aa201021aa63263143b.
    The scanner changed and the gate was not regenerated — run the four commands in the runbook's
    HOW TO REGENERATE block and update the gate.
```

Restored md5 `e03078ff73502c3c877b0d2ebf93941d`.

### T3 NC-E — the capability-numbers enforcer

Changing the gate's EXPECT line `276` → `277`:

```
E   AssertionError: the gate's EXPECT line does not match what the block actually prints
FAILED …::test_pending_paste_step0_capability_numbers_are_the_real_manifest_numbers
```

### T3 NC-F — the never-`rm` enforcer, BOTH directions

**Direction 1** — a real deletion inserted into the ROTATE block
(`rm -f /home/jupyter/occ_measure/pcs_pairs.tsv`):

```
E   AssertionError: the ROTATE block deletes something. The contaminated artifacts are EVIDENCE; the project
    ruling is rotate, never delete (.planning/debug/260824-STAGE-A-env-stop-plink1.9-and-stale-scratch-TSV.md)
FAILED …::test_pending_paste_rotates_before_the_sweep_and_never_deletes
```

**Direction 2** — prose containing the two letters
(`confirm` / `warm` / `storm` / `term` / `form` / `norm`) inserted into the same block:

```
1 passed, 110 deselected in 0.14s
```

So the guard catches a real deletion **and** is not the collision bug it exists to
prevent. Runbook restored byte-for-byte both times
(md5 `e03d6578f84f46b8c502eacec26a40a5`).

### T4 NC-G — the arithmetic enforcer, three ways

```
(1) wc 353090 -> 353091 :
E   AssertionError: the predicted wc -l (353091) is not the predicted row count (353089) plus one header
(2) rows 353089 -> 353088 :
E   AssertionError: the predicted wc -l (353090) is not the predicted row count (353088) plus one header
(3) BOTH shifted consistently (353088 / 353089), so wc == rows + 1 STILL HOLDS and the x4 check is isolated :
E   AssertionError: the predicted POOLED candidate rows (353088) x 4 is 1412352, not the AFR pass 1412356 that
    it is DERIVED from
```

Prereg record restored to md5 `de60c957fcf6ddf7713a677570f4cfa1` after each.

---

## Verify gates — literal output

### Task 1

```
$ pytest tests/m3/test_pairwise_completeness_scan.py -q | tail -3
106 passed in 0.87s

$ pytest … -k "suspect or quarantine or stale or region_ids" -v | tail
tests/m3/test_pairwise_completeness_scan.py::test_assert_unique_region_ids_names_the_offending_ids_and_their_counts PASSED
tests/m3/test_pairwise_completeness_scan.py::test_pooled_candidate_rows_disagreement_quarantines_the_output_and_returns_2 PASSED
tests/m3/test_pairwise_completeness_scan.py::test_a_stale_artifact_at_out_does_not_survive_a_successful_run PASSED
tests/m3/test_pairwise_completeness_scan.py::test_a_stale_artifact_at_out_does_not_survive_a_quarantined_run PASSED
tests/m3/test_pairwise_completeness_scan.py::test_a_preexisting_suspect_is_rotated_not_clobbered PASSED
tests/m3/test_pairwise_completeness_scan.py::test_the_quarantine_name_is_built_by_string_concatenation_not_with_suffix PASSED
tests/m3/test_pairwise_completeness_scan.py::test_an_empty_after_strip_region_ids_is_an_error_while_the_absent_flag_still_means_all_regions PASSED
7 passed, 99 deselected in 0.34s

$ git diff --stat e6f4f79 HEAD -- <the four frozen modules> .planning/amendments/
(EMPTY)
```

Expected 106 — **got 106.**

### Task 2

```
$ pytest tests/m3/test_pairwise_completeness_scan.py -q | tail -3
108 passed in 0.73s

$ pytest … -k "unrequested_ancestry or composite or padded or whitespace" -v
tests/m3/…::test_region_only_in_the_unrequested_ancestry_raises_naming_the_id PASSED
tests/m3/…::test_composite_whitespace_ancestry_parse_selects_where_production_drops PASSED
tests/m3/…::test_real_manifest_carries_no_padded_or_quoted_ancestry_cells PASSED
tests/m3/…::test_cli_region_only_in_the_unrequested_ancestry_exits_2_and_writes_no_tsv PASSED
4 passed, 104 deselected in 0.12s

$ git status --porcelain src/python/pairwise_completeness_scan.py; md5sum …
(no output)
e03078ff73502c3c877b0d2ebf93941d  src/python/pairwise_completeness_scan.py
```

Expected 109 — **got 108.** See Deviations.

### Task 3

```
$ pytest tests/m3/test_pairwise_completeness_scan.py -q | tail -3
111 passed in 0.72s

$ pytest … -k "pending_paste" -v
…::test_pending_paste_exists_and_carries_the_harness_crosscheck PASSED
…::test_pending_paste_carries_the_falsifier_tokens PASSED
…::test_pending_paste_runs_the_falsifier_before_the_crosscheck_and_the_sweep PASSED
…::test_pending_paste_no_longer_claims_it_calls_no_plink PASSED
…::test_pending_paste_step3_carries_no_ancestry_flag_so_the_default_is_load_bearing PASSED
…::test_pending_paste_step0_pins_the_scanner_by_a_CURRENT_content_hash PASSED
…::test_pending_paste_step0_capability_numbers_are_the_real_manifest_numbers PASSED
…::test_pending_paste_rotates_before_the_sweep_and_never_deletes PASSED
8 passed, 103 deselected in 0.10s

$ python -c "… _read_regions_tsv('config/ld_regions.tsv', None) …"
manifest windows: 276 distinct region ids: 276
CAPABILITY CHECK PASSED
```

Expected 112 — **got 111.** All five pre-existing runbook pins green, including the
`--ancestry`-count pin, which is the proof the edits did not reintroduce the
forbidden token (whole-document count measured independently: **0**).

### Task 4

```
$ pytest tests/m3/test_pairwise_completeness_scan.py -q | tail -3
112 passed in 1.10s

$ pytest tests/m3 -q | tail -1
1133 passed, 33 skipped, 4 warnings in 817.91s (0:13:37)
$ git checkout -- tests/m3/sparse_parent_benchmark.tsv
$ git status --porcelain tests/
(no output)

$ git diff --stat e6f4f79 HEAD -- <the four frozen modules> .planning/amendments/
(EMPTY)
$ git log --oneline e6f4f79..HEAD
9cf9baa docs(quick-260828-uej): T4 — …
5e2b31a fix(quick-260828-uej): T3 — …
bdaf705 test(quick-260828-uej): T2 — …
cb199b6 fix(quick-260828-uej): T1 — …
8265507 fix(quick-260828-uej): PLAN revision — …
ad5a907 docs(quick-260828-uej): bank the external reviewer verdict AS-RECEIVED — …
c5cd80c docs(quick-260828-uej): PLAN — …
branch: m3-W2-aou-deltas
```

Expected 113 / 1134 — **got 112 / 1133.** See Deviations. The log shows the four task
commits **plus the three planning commits that already existed at HEAD when execution
began** (`e6f4f79` was measured before the PLAN itself was committed).

---

## Component-exact suite reconciliation

| Quantity | Baseline | Now | Delta |
|---|---|---|---|
| `tests/m3` passed | 1122 | **1133** | +11 |
| `tests/m3` skipped | 33 | **33** | **0** |
| `tests/m3` failed | 0 | **0** | 0 |
| `test_pairwise_completeness_scan.py` alone | 101 | **112** | +11 |
| non-scanner collect-only (independent control) | 1054 | **1054** | **0** |

Three independent derivations agree:

```
1122 + 11 = 1133                       (full suite)
 101 + 11 =  112                       (single-file control)
1054 + 112 = 1166 = 1133 + 33          (collect-only vs passed+skipped)
```

**Name-level collect diff vs `e6f4f79`** (never a count diff): **12 added, 1 removed**,
where the removed name is the RENAME of the reconciliation test → **net +11**.

The 11 new tests, named, by task:

| Task | Test |
|---|---|
| T1 | `test_a_stale_artifact_at_out_does_not_survive_a_successful_run` |
| T1 | `test_a_stale_artifact_at_out_does_not_survive_a_quarantined_run` |
| T1 | `test_a_preexisting_suspect_is_rotated_not_clobbered` |
| T1 | `test_the_quarantine_name_is_built_by_string_concatenation_not_with_suffix` |
| T1 | `test_an_empty_after_strip_region_ids_is_an_error_while_the_absent_flag_still_means_all_regions` |
| T2 | `test_composite_whitespace_ancestry_parse_selects_where_production_drops` |
| T2 | `test_real_manifest_carries_no_padded_or_quoted_ancestry_cells` |
| T3 | `test_pending_paste_step0_pins_the_scanner_by_a_CURRENT_content_hash` |
| T3 | `test_pending_paste_step0_capability_numbers_are_the_real_manifest_numbers` |
| T3 | `test_pending_paste_rotates_before_the_sweep_and_never_deletes` |
| T4 | `test_prereg_pooled_row_prediction_reconciles_with_the_afr_pass` |

Plus **one rename, zero net items**:
`test_pooled_candidate_rows_reconciliation_raises_when_the_bases_disagree` →
`test_pooled_candidate_rows_disagreement_quarantines_the_output_and_returns_2`.

`tests/m3/sparse_parent_benchmark.tsv` restored after the full run and **never staged**
(`git status --porcelain tests/` blank).

---

## Deviations from Plan

### 1. [Rule 1 — plan arithmetic error] N = 11, not 12; the counts are 108 / 111 / 112 / 1133

**Found during:** Task 2.
**Issue:** the plan's Task 2 gate expects `109 passed (106 + 3 new)` and Task 4.F
expects `N = 12 (5 T1 + 3 T2 + 3 T3 + 1 T4)` — but Task 2's own `<behavior>` block
describes exactly **three items, one of which is the MODIFIED (not added)
ancestry-raise test**: the repaired invariant, the composite-parse pin, and the
latency monitor. That is **two** new tests, so `106 + 2 = 108`, and `5 + 2 + 3 + 1 = 11`.
**Measurement that settles it:** a name-level collect-only diff against `e6f4f79`
returns exactly 12 added / 1 removed, the removed one being the rename → **net +11**,
cross-checked three ways above.
**Action:** delivered the two tests the plan describes; did **not** invent a third to
hit a number. The plan explicitly permits this: *"a different N is acceptable ONLY if
every test is named and the arithmetic re-derived."* Every test is named above and the
arithmetic is re-derived three independent ways.
**Downstream:** every expected count shifts by −1: 108 (T2), 111 (T3), 112 (T4),
**1133** (full suite). Skips **stayed at 33** — no new test landed as a SKIP.

### 2. [Rule 2 — a name is a claim] The reconciliation test was RENAMED as well as inverted

**Found during:** Task 1.
**Issue:** the plan says to invert `test_pooled_candidate_rows_reconciliation_raises_when_the_bases_disagree`
to `rc == 2`, but leaves the name saying `_raises_`. After T1 it does not raise.
**Action:** renamed to
`test_pooled_candidate_rows_disagreement_quarantines_the_output_and_returns_2`,
docstring records the inversion and why the surviving `not out.exists()` half is still
meaningful. **Item count unchanged** (1 → 1), so no plan arithmetic is affected.

### 3. [Rule 1 — my own substring collision, caught by its own RED] The prereg slices are `^`-anchored

**Found during:** Task 4.D.
**Issue:** the arithmetic enforcer's first draft sliced section (e) with
`text.index("### RESIDUAL — KNOWN, NOT FIXED, AND WHY")`. My **own** (b1) correction
paragraph contains that heading as a CROSS-REFERENCE (`See \`### RESIDUAL …\` below`),
~16 kB earlier. Measured: `i, j = 32191, 16980` → a **negative-length slice**, silently
empty, so the table lookup failed with *"the prediction table has no row for 'POOLED
candidate rows'"*.
**Action:** all four heading lookups now use `re.search(rf"^{re.escape(heading)}", text, re.M)`
plus an explicit ordering assertion, so a future collision fails loudly with the indices.
This is the exact class the plan's standing rule exists to prevent — it bit inside the
plan that wrote the rule, and it was caught only because the assertion was run and seen
RED rather than assumed.

### 4. [Rule 3 — process] `git checkout` on an UNCOMMITTED file reverted real work

**Found during:** Task 3, negative controls.
**Issue:** the enforcer NCs mutate the runbook. Reverting with
`git checkout -- <runbook>` while the T3 edits were still **uncommitted** restored the
file to `HEAD`, wiping the new STEP 0 gate, the field records, STEP 2b and the STEP 3
pre-flight (measured: `wc -l` back to 488, `grep -c 'BEHAVIOURAL FRESHNESS GATE'` → 0).
**Action:** re-applied all three edits, then switched to **backup-to-scratchpad and
restore-by-copy** for every subsequent document mutation, verifying the restored md5
against the backup's. No content was lost; the affected NC (NC-E) had already produced
its RED observation before the revert.

### 5. Refinement to the runbook's stated failure meanings (accuracy, not scope)

The plan says a `TypeError` means "a pre-fix checkout". Measured at `d8f4d54^`: through
the **positional** call the gate actually uses, a pre-fix checkout returns **552 / 276**;
the `TypeError` arises only through the **keyword** form. The runbook states both,
each with its measurement, rather than the shorter claim.

### 6. `.planning/STATE.md` — WRITTEN, deliberately NOT staged or committed

Task 4.E permits appending a row when no FOREIGN in-flight edit is present.
**Measured at Task 4:** `git diff --stat .planning/STATE.md` is **EMPTY** — the foreign
modification present at session start has since been resolved by the other terminal, so
the plan's condition is satisfied and the block was appended.
**But the orchestrator's execution brief states: "Do NOT commit docs artifacts
(SUMMARY.md, STATE.md, PLAN.md) — the orchestrator handles the docs commit."**
So the new 2026-08-28 block is **in the working tree, unstaged and uncommitted**, for the
orchestrator's docs commit. Nothing of another terminal's was staged
(`feedback_multi_terminal_staging`).

---

## Items the plan asked to be REPORTED

* **Task 1 item 5** — grep for any existing test passing `--region-ids ""` or relying on
  the falsy-means-all behaviour: **NONE FOUND.** All ten `"--region-ids"` call sites in
  the test module pass non-empty id lists; no `region_ids=[]`, no empty-string form,
  anywhere in the repo. Nothing had to be adapted.
* **Task 3.A** — grep for anything pinning the tokens in the deleted sentence: the only
  hits for `quick-260825-qpf` in `tests/` are three section-banner **comments** and one
  assertion at `:2562`, and that assertion is scoped to the **R6 block of
  `260812-ox1-AGENT-PROMPT.md`**, not to the runbook. `adversarial-review remediation`,
  `pre-qpf` and `reviewed-but-unfixed` return **0** hits. **Nothing pinned the removed
  sentence.** The "NCSU must have been PUSHED first" warning was KEPT.

---

## Frozen surfaces + public record

```
$ git diff --stat e6f4f79 HEAD -- src/python/occlusion_span_filter.py \
    src/python/run_native_ld_panel.py src/python/fire_verifier.py \
    src/python/aou_ld_panel.py .planning/amendments/
(EMPTY)
```

Verified EMPTY at **every** commit. `run_native_ld_panel.py` is READ by two `ast`
enforcers and never written. The posted OSF amendment is untouched.

**The pre-registered numbers are byte-unchanged.** Every removed line in the prereg
record's diff is one of the three stale RAISES claims; `15`, `13`, `10`, `3` and
`{-14: 1, -9: 1, -6: 1, -3: 1, -1: 1, 0: 10}` are identical in HEAD and worktree
(checked line-by-line, not by eye).

---

## Nothing was fired

Zero enclave / VM / Dataproc / OSF / `gsutil` / `gcloud` / network contact. **$0.**
No per-sample data was created, read or moved. Every command ran at NCSU against the
repo and the checked-in `config/ld_regions.tsv`.

**THE RE-RUN HAS NOT HAPPENED.** The `353089` / `353090` prediction was **recorded
before it**, in commit `9cf9baa`, derived from `1,412,356 / 4` exactly and enforced by
a committed test. **A mismatch is a finding to report, never a number to adjust.**

## Known Stubs

None. Every artifact this plan produced is wired: the runbook gate is executed by two
committed enforcers, the ROTATE block by a third, and the pre-registered arithmetic by a
fourth. The one thing that is deliberately *recorded rather than closed* — the
scanner-vs-production whitespace divergence — is not a stub: it is pinned at the
selection layer, MEASURED against production by `ast` extraction, and held latent by a
monitor that goes RED the day the real manifest acquires such a row.

## Self-Check: PASSED

All five claimed files exist on disk. All four claimed commits resolve
(`cb199b6`, `bdaf705`, `5e2b31a`, `9cf9baa`) on `m3-W2-aou-deltas`. The working
tree carries exactly two intentional uncommitted entries — `.planning/STATE.md`
(written, left for the orchestrator's docs commit) and this SUMMARY (untracked,
likewise) — plus `.planning/debug/m3-producer-unbounded-dense-read.md`, which was
untracked at session start and is LEFT EXACTLY AS FOUND. `src/`, `tests/` and
`config/` are clean; the scanner still hashes to the gated
`e03078ff73502c3c877b0d2ebf93941d`.
