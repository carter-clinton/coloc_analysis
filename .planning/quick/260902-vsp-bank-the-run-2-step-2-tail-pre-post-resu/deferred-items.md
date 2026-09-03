# Deferred items — quick-260902-vsp

Out-of-scope discoveries and deliberate non-actions. **Not done by this task**
(SCOPE BOUNDARY: this task is DOCS-ONLY by explicit constraint; only issues
directly caused by this task's own changes are auto-fixed).

## 1. DEFERRED — the `0.0005` bound is a LIVE CONTRADICTION in `src/` (code fix)

**Measured in the tree at execution time, four citations:**

```
src/python/pairwise_completeness_scan.py:45   "...the error that produced the withdrawn ``0.0005`` bound."
src/python/condition_ld_matrix.py:120         ceiling_frac: float = 0.0005      (LIVE DEFAULT)
src/python/write_conditioned_ld_npz.py:64     ceiling_frac: float = 0.0005      (LIVE DEFAULT)
src/python/write_conditioned_ld_npz.py:17     "...records the pre-registered 0.0005 ceiling..."
```

One module calls the bound **withdrawn**; another calls it **pre-registered**;
the value is **live in both**. At most one of those docstrings can be true.

**Why it is NOT fixed here:** this task is DOCS-ONLY by non-negotiable
constraint. `git status --porcelain -- src tests` was EMPTY at plan time and is
EMPTY at commit time, and that emptiness is itself a verified gate of this task.
Editing a docstring — never mind deciding which reading is correct — would break
the gate that makes this record's scope claim checkable.

**What would discharge it:** a separate quick that (a) DECIDES whether the bound
is withdrawn or pre-registered, (b) makes both docstrings agree with the live
default (or changes the default, if the decision goes that way), and (c) lands a
**named enforcer test** so the agreement has a guard rather than a belief. A
claimed invariant with no named enforcer is belief only.

**Where it is flagged:** `## ACTION ITEM — THE 0.0005 BOUND IS A LIVE
CONTRADICTION (NOT FIXED HERE)` in
`.planning/debug/260902-COURIER-TO-SETH-RUN2-tail-PRE-vs-POST-filter-heterogeneity-and-definitional-disagreement.md`.

## 2. DEFERRED — four prior quick tasks have no `### Quick Tasks Completed` row in STATE.md

`260828-uej`, `260831-kw8`, `260901-l55` and `260901-rvu` all completed, all have
`.planning/quick/` directories with their own SUMMARYs, and **none has a row** in
the `### Quick Tasks Completed` table (which ended at the `260826-qq9` row before
this task appended `260902-vsp` after it). Each IS represented in the
`last_activity` frontmatter and in a narrative section, so nothing is lost — only
the table is behind.

**Why it is NOT backfilled here:** authoring four descriptions from other tasks'
summaries, inside a task whose entire purpose is to bank a measurement without
introducing an unverified claim, is exactly the failure mode this record must not
contain. A count is a claim; so is a description.

**What would discharge it:** a separate quick that writes each row **from that
task's own SUMMARY**, one row per source document, with the commit hash taken
from that task's own commit rather than inferred.

⚠ Note the table's existing last row (`260826-qq9`) carries only **3** cells, not
6. That is PRE-EXISTING and was NOT touched by this task, which edits exactly one
insertion point. Repairing it belongs with the backfill above.

## 3. NOT DEFERRED — REPORTED. The FLAG-1 attribution, and what was not edited

The planner raised FLAG-1: the task brief called
`.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md`
"the pre-registration this run answers", and the tree does not support that. It
was **right**, and `CONTENT-SPEC.md` was corrected at source before execution:
the section formerly headed `## PRE-REGISTERED VALUES` is now `## COMPLETION
CHECK` plus a new `## THE TWO PRE-REGISTRATIONS`. The three values
`n_tail_rows_in` 3094 / `n_tail_rows_out_of_scope` 0 /
`n_defined_rows_out_of_scope` 0 are an **INVARIANT CHECK**, not a
pre-registration: 3094 was already measured in the smoke and carried forward, and
the two zeros follow by construction. The record says so and never calls them a
pre-registration.

**What was NOT edited, deliberately:**
`.planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md`
is a **FIRED runbook** and is read-only for this task. Its
`### NO EXPECTED VALUE IS STATED` block at `:211-216` is QUOTED in the record and presented as a
**STRENGTH** — it is why none of the three findings can have been shaped by an
expectation. If Carter wants that disclaimer's wording narrowed, that is a
**separate task and Carter's call**; this record handles it by attribution, not
by amendment.

⚠ Related residue, reported not smoothed: the spec's own `## HONEST LIMITATIONS`
paragraph still contains the pre-correction phrase "the three **pre-registered**
values". It is reproduced **unedited** in the record's VERBATIM APPENDIX, because
the appendix is byte-equal to the spec by construction and byte-equality is the
guarantee that no number was retyped. The record annotates it explicitly in its
own `## HONEST LIMITATIONS` section and states that the governing
characterisation is the COMPLETION CHECK. Correcting that one phrase in the spec
would move the spec's md5 and is therefore its own decision, not a silent tidy.
