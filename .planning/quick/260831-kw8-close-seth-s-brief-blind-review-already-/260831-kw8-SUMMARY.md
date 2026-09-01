---
phase: quick-260831-kw8
plan: 01
subsystem: m3-afr-ld-panel
tags: [pairwise-completeness, occlusion, already-occluded, anchor-relative, panel-wide-excludelist, post-hoc-reclassification, false-docstring-claim, deferred-correction, byte-proxy-gate, same-position, split-multi-hts, brief-blind-review, prereg-unchanged, nothing-fired]
requires: [pairwise_completeness_scan.py, occlusion_span_filter.py (FROZEN, import only)]
provides: [pcs_panelwide_reclassify.py, samepos_missingness_probe.py, the anchor-relative behavioural enforcer, the staged post-hoc runbook, the review record]
affects: [tests/m3, .planning/debug, .planning/STATE.md]
tech-stack:
  added: []
  patterns: [self-invalidating documentation note, function-identity reuse assertion, decision-rule-before-run, census-beside-sample]
key-files:
  created:
    - src/python/pcs_panelwide_reclassify.py
    - tests/m3/test_pcs_panelwide_reclassify.py
    - src/python/samepos_missingness_probe.py
    - tests/m3/test_samepos_missingness_probe.py
    - .planning/debug/260831-PENDING-PASTE-POSTHOC-panelwide-reclass-and-samepos-probe.md
    - .planning/debug/260831-seth-brief-blind-review-already-occluded-is-anchor-relative.md
    - .planning/debug/260831-DEFERRED-pairwise-completeness-scan-docstring.patch
  modified:
    - tests/m3/test_pairwise_completeness_scan.py
    - .planning/STATE.md
decisions:
  - "The prose correction to pairwise_completeness_scan.py:122 is DEFERRED to the post-sweep window, because a LIVE runbook pins that file's whole-file md5 and those pins are CURRENTLY TRUE about an in-flight sweep."
  - "already_occluded is NOT renamed while the in-flight artifact contract stands; trigger = next OSF version, post-sweep."
  - "The STEP 0 byte-proxy gate is a REPEAT of feedback_scope_a_guard_to_the_property_not_a_proxy (2026-08-06); the durable rescope to a docstring-insensitive code hash is scheduled, not applied."
metrics:
  tasks_completed: 4 (one PARTIAL by coordinator decision)
  commits: 4
  duration: one session
  completed: 2026-08-31
---

# Phase quick-260831-kw8: Close Seth's brief-blind review Summary

Confirmed both findings of a brief-blind external review, built a post-hoc tool that answers the panel-wide `--exclude` question from the artifact an in-flight sweep is already producing (no `.bed`, no re-run), and **deferred** the one-line prose fix because a live runbook's byte pin is currently a true statement about that running sweep.

## What shipped

| Task | Commit | What |
|---|---|---|
| T1 | `bdb0a28` | `pcs_panelwide_reclassify.py` (pre-existing; verified, not redone) |
| T2-partial | `c49e10a` | Behavioural enforcer + rename-decline pin + the TRUE semantics in the UNPINNED tool |
| T3 | `e7b058e` | `samepos_missingness_probe.py` — built, tested, **NOT RUN** |
| T4 | `7978ee6` | Staged NOT-RUN paste doc + the review record |

## ⚠ THE ONE DEVIATION, AND THE MEASUREMENT THAT JUSTIFIED IT

**Task 2's prose edit was NOT landed.** I stopped, reported, and the coordinator ruled A+D-now / C-post-sweep.

**Measured:** a docstring-only edit to `pairwise_completeness_scan.py` moves its whole-file md5/size from `e03078ff73502c3c877b0d2ebf93941d` / `73772` to `fc1d68dff1f493f6eb57dd427bed638a` / `78843`. The live runbook's STEP 0 gate pins those values and `test_pending_paste_step0_pins_the_scanner_by_a_CURRENT_content_hash` recomputes both at call time:

```
FAILED tests/m3/test_pairwise_completeness_scan.py::test_pending_paste_step0_pins_the_scanner_by_a_CURRENT_content_hash
AssertionError: the STEP 0 gate does not pin the CURRENT scanner md5 fc1d68dff1f493f6eb57dd427bed638a.
1 failed, 171 passed, 2 skipped in 4.47s   # scanner + freeze-pins + occlusion-filter files
```

⚠ **THAT CAPTURE IS VERBATIM BUT WAS NOT SCOPED — corrected here.** It was taken on a
tree that ALSO held the third (secondary text) T2 test, which I then deliberately did NOT
land. So it is `1 + 171 + 2 = 174` items. A reader re-running it on the SHIPPED tree gets a
different number and would think the record was wrong. **All three states, each MEASURED:**

| tree | result | items |
|---|---|---|
| HEAD as shipped (patch NOT applied) | `171 passed, 2 skipped` — 0 failed | 173 |
| HEAD + the parked patch applied | `1 failed, 170 passed, 2 skipped` | 173 |
| the capture above (tree also held the withheld 3rd test) | `1 failed, 171 passed, 2 skipped` | 174 |

The 1-item delta between rows 2 and 3 **is** the withheld test. The substantive claim is
identical in every row and is what the deferral rests on: **exactly one failure, and it is
the STEP 0 gate.** (Caught by the independent verifier; a count is a claim and must carry
the tree it was measured on — `feedback_a_count_is_a_claim_scope_and_reconcile`.)

Exactly one failure. Only one test file reads that runbook (`grep -rln` over `tests/`). The scanner is NOT in `PY_FROZEN_RELS` — the plan's freeze analysis was right about `source_freeze` but `source_freeze` is not the guard that fired.

**Three plan constraints were mutually unsatisfiable:** (1) edit the docstring, (2) that test file at 0 failed, (3) the live runbook's `git status` EMPTY. The only fix satisfying all three is rewriting an operational STOP gate whose pinned values are *currently a true statement about the ~4h20m sweep that is running* — which would make the record lie about which instrument produced it, an unrecoverable cost, whereas the prose fix is recoverable. Rule 4, not Rule 3.

**Mitigation landed instead (costs no pinned bytes):** the TRUE semantics are in `pcs_panelwide_reclassify.py` §(1b) — new, unpinned, and where the at-risk reader arrives — naming the false sentence and marking it FALSE. The note is **SELF-INVALIDATING**: its claims about the scanner are recomputed from disk, so it goes RED the instant the parked patch lands.

**Parked patch:** `.planning/debug/260831-DEFERRED-pairwise-completeness-scan-docstring.patch` (committed, durable) — also at `<session scratchpad>/T2-scanner-docstring-correction.patch`.

**Recorded as a REPEAT** of `feedback_scope_a_guard_to_the_property_not_a_proxy` (2026-08-06), a gate we designed ourselves in `quick-260828-uej` T3. Durable fix scheduled: docstring-insensitive CODE hash, proven able to fail before being trusted.

## RED observations — verbatim, every one actually seen

**RED #1 — docstring test vs the pre-fix docstring (natural RED):**
```
>       assert "already visible as ``already_occluded``" not in flat
E       'already visible as ``already_occluded``' is contained here:
E         ` side is already visible as ``already_occluded``; * the ``--mac 1`` side is the new ...
1 failed, 2 passed, 112 deselected
```

**RED #2a — behavioural test, fixture mutation (deletion B widened to cover the SNP):**
```
E       AssertionError: assert 1013 == 1005
E        +  where 1013 = CandidatePair(..., del_ref_len=10, ..., already_occluded=True, ...)
```

**RED #2b — behavioural test, MODULE mutation (predicate's right bound dropped) — hits the target assertion:**
```
>       assert anchored_on_b.already_occluded is False, ("ANCHOR-RELATIVE: 1004 < 1008 <= 1005 is FALSE")
E       AssertionError: ANCHOR-RELATIVE: 1004 < 1008 <= 1005 is FALSE
E       assert True is False
```

**RED #2c — behavioural test, detector stubbed to `((), ())` — hits the panel-wide half:**
```
E       AssertionError: the panel-wide excludelist must contain the SNP that the B-anchored pair reports as already_occluded=False
E       assert '1:1008:T:C' in ()
```

**RED #3 — rename-decline test, `SUMMARY_KEYS` entry renamed:**
```
>       assert "n_undefined_not_already_occluded" in pcs.SUMMARY_KEYS
E       AssertionError: assert 'n_undefined_not_already_occluded' in ('region_id', 'window_bp', ...)
```

**RED-B1 — the mitigation note's quoted false claim removed:**
```
E       assert 'already visible as ``already_occluded``' in 'POST-HOC panel-wide ...'
```

**RED-B2 — SELF-INVALIDATION #1, simulating the parked patch LANDING:**
```
E       AssertionError: the scanner's false claim is GONE -- the DEFERRAL note in pcs_panelwide_reclassify.py is now STALE. Remove section (1b) in the same commit that lands the parked patch.
```

**RED-B3 — SELF-INVALIDATION #2, scanner bytes moved but sentence kept:**
```
E       AssertionError: the note quotes a stale scanner md5; the file on disk is 6d1201beacee4af1784173b75130969a
```

**RED (T3) — before `samepos_missingness_probe.py` existed:**
```
E       ModuleNotFoundError: No module named 'samepos_missingness_probe'
tests/m3/test_samepos_missingness_probe.py:114: ModuleNotFoundError
11 failed in 0.28s
```

**RED-C1 — `label_for_fraction` returns a CONSTANT:**
```
E       AssertionError: assert 'co_called' == 'complementary'
E       AssertionError: assert 'co_called' == 'mixed'
2 failed, 9 passed
```

**RED-C2 — the multiplicity skip counter silenced:** `E assert 0 == 1` (1 failed)

**RED-C3 — a per-sample vector leaked into the summary:**
```
E       AssertionError: summary.provenance.per_sample_called: list of length 8 >= n_samples
```

**T1's post-hoc-only AST gate — GREEN and RED (re-demonstrated this session):**
```
GREEN: POST-HOC-ONLY GATE OK: no BedReader/Genotypes import, no BedReader reference, no
       read_variant, no .bed literal outside docstrings, .bim literal present -> cannot re-run
RED  : AssertionError: GENOTYPE SURFACE IMPORTED: BedReader
```
Reverted; green again. The gate parses SOURCE READ AT CALL TIME, so a stale `__pycache__` cannot rescue it — but `__pycache__` was cleared before every mutation anyway.

## Task 2 audit — every site inspected, hits AND non-hits

The prose fix is deferred, so these are the sites the parked patch touches, plus the ones judged already correct.

| Site | Verdict | Action |
|---|---|---|
| `:115-135` RETAINED-SET PARITY bullet, sentence at `:122` | **HIT — FALSE** | rewritten in the parked patch |
| `:616` the `already_occluded` computation comment ("THE POSTED RULE") | **HIT — overstates** (it is the posted rule against the ANCHOR only) | scoped in the parked patch |
| `:1149` `summarize()` docstring ("the POSTED criterion already covers") | **HIT — overstates** (reads as panel-wide) | scoped in the parked patch |
| `:477-481` `span_offset` note ("already covered") | **HIT — mild** (true but unscoped) | scoped in the parked patch |
| `:1169` rollup comment on `occluded_keys` | **HIT — mild** (no scope note) | comment added in the parked patch |
| `:446` `_pair_key` docstring (INDEX-keyed on purpose) | **NON-HIT — correct** | unchanged |
| `:442` `CandidatePair.already_occluded` field decl | **NON-HIT** — bare declaration, no prose claim | unchanged |
| `:793` `PairResult.already_occluded` field decl | **NON-HIT** — bare declaration | unchanged |
| `:852` `globally_invariant` "RETAINED-SET PARITY bookkeeping, not a verdict" | **NON-HIT — correct** | unchanged |
| `:1045-1046` `SUMMARY_KEYS` entries | **NON-HIT** — bare names | unchanged |
| tests `:719-746` `test_offset_zero_and_already_occluded_are_not_the_same_predicate` | **NON-HIT — correct** (asserts the two predicates differ) | unchanged |
| tests `:894-902` `test_interior_partner_is_flagged_already_occluded` ("'already covered' by the posted rule") | **HIT — mild**, anchor-scoped in context | left; superseded by the new behavioural test |
| tests `:989` `assert pr.already_occluded is False  # the posted rule correctly declined` | **NON-HIT** — true of that anchor | unchanged |
| tests `:2295` RETAINED-SET reference in `test_globally_invariant_variant_is_reported_separately` | **NON-HIT — correct** (`--mac 1` side) | unchanged |

## The rename DECLINE — three reasons and its trigger

1. **A sweep is MID-FLIGHT** and will emit a header carrying this exact column. `TSV_COLUMNS` *is* the emitted header, and `pcs_panelwide_reclassify.py` checks it by STRICT EQUALITY → a rename makes the new tool RAISE on the in-flight artifact.
2. **The pre-registration names the two summary keys.** Renaming a pre-registered key in response to a review is the exact move pre-registration exists to prevent.
3. **`TSV_COLUMNS IS PairResult._fields`** — one rename moves the emitted header, `SUMMARY_KEYS`, the banked BLOCK 2 identity pull and every consumer at once.

**Trigger:** next OSF version, AFTER the sweep lands and its artifacts are banked. **Enforcer:** `test_the_already_occluded_rename_is_declined_while_the_sweep_artifact_contract_stands`.

## The derived quantity, with its scope

On rows synthesized from the BANKED vids — a **SUBSET** row set:

* **ROW level 5 = 3 + 2.** Three rows (offsets −14, −9, −6) belong to pairs with a panel-wide-occluded member; two (−3 `m2_region_00008`, −1 `m2_region_00149`) are UNKNOWN.
* **PAIR level 3 = 1 + 2.** One member-occluded (`46714|46715`, the −6); two UNKNOWN.

Occlusion is **monotone in the row set**, so an OCCLUDED verdict on a subset is **SOUND** and a NOT-OCCLUDED verdict is **NOT**. The three positives stand; **the two negatives are UNKNOWN** until the full-window in-perimeter run.

⚠ **This does not move 15 / 13 / 10 / 3 or `{-14: 1, -9: 1, -6: 1, -3: 1, -1: 1, 0: 10}`.**

## Provenance of the three accepted-without-action figures

| Figure | Whose | Did WE re-derive it? |
|---|---|---|
| ±5bp = 6.5× the current rule | **Seth's**, 2026-08-29 reply §6 | **No.** Not attempted — needs region 1's `.bim`, which is in-perimeter (MEASURED: no `afr_cohort*.bim` / `*region_00001*.bim` under the repo). Appears nowhere else in `.planning/`. |
| ±50bp = 12.66% of the panel | **Seth's**, same source | **No.** Same blocker. |
| MAF ~0.0078 vs ~0.014 (ratio 0.557) | **Ours**, `m3_panel_occlusion_policy_decision.md:52` | **No** — and recorded as **DIRECTIONALLY CONSISTENT, NOT EVIDENCE**, because Seth ruled it ambiguous on 2026-08-18 and that earlier, more conservative ruling **governs**. |

The decline rests on the **geometry argument**, not on the two prices — a later correction to either would not reopen it.

## Suite reconciliation — component-exact, both bases

**Full `tests/m3`: 1167 passed / 33 skipped / 0 failed** (816.91 s = 13:36).

```
PASSED basis:     1133 (ff94bb3) + 20 (T1) + 2 (T2p scanner) + 1 (T2p reclassify) + 11 (T3 probe) = 1167 ✓
COLLECTED basis:  baseline 112 + 1054 = 1166 = 1133 + 33
                  now      1054 + 114 + 21 + 11 = 1200 = 1167 + 33 ✓
SKIPPED:          33 -> 33  (no new test landed as a SKIP)
```

Per-file collect: `test_pairwise_completeness_scan` **114** (was 112), `test_pcs_panelwide_reclassify` **21** (was 20), `test_samepos_missingness_probe` **11** (new).

*Honesty note:* I did not re-run the full suite at `bdb0a28`; the `1133 + 20 = 1153` intermediate is reconciled from directly measured components (scanner 112, reclassify 20, both measured this session) plus the deltas above, and the final total is measured.

`tests/m3/sparse_parent_benchmark.tsv` restored; `git status --porcelain tests/` EMPTY.

## Gates — literal output

* Scanner bytes after **every** commit: `e03078ff73502c3c877b0d2ebf93941d` / `73772` — **UNMOVED**.
* STEP 0 check (i) `git status --porcelain <scanner>` → no output = **PASS**.
* Forbidden surfaces (`occlusion_span_filter.py`, `run_native_ld_panel.py`, `fire_verifier.py`, `aou_ld_panel.py`, `.planning/amendments/`, the live runbook, the pre-registration) → **EMPTY**.
* `STAGED ARGVS PARSE; NOT-RUN MARKER PRESENT; INFERENCE LABELLED` (both argvs against the real `_build_parser()`s; broken-argv negative control rejected).
* `RECORD OK: prereg numbers restated unchanged; prices labelled SETH-COMPUTED; the 0.0078/0.014 ratio recorded as directionally consistent, NOT evidence, with its citation; the deferral, the REPEAT precedent and the scheduled rescope all present`
* `PROBE CONTRACT OK; labels ['co_called', 'complementary', 'mixed']`
* `IDENTITY OK` equivalents: `S.BedReader is P.BedReader`, `R.detect_occluded_variants is O.detect_occluded_variants`.
* Prereg enforcer `test_prereg_pooled_row_prediction_reconciles_with_the_afr_pass` — **1 passed**.
* Branch `m3-W2-aou-deltas`; no worktree isolation; explicit-path staging only.

## In-session deviation worth recording

Two gate scripts were written inline in `bash -c` and the shell mangled the regex (`shlex` produced literal-newline tokens; then `ValueError: No escaped character`). Fixed by writing gates to files and folding shell continuations **line-wise** rather than with a clever regex. A gate that cannot survive its own quoting is not a gate.

Also: `git checkout --` silently reverted **uncommitted** work once (the §(1b) mitigation). Caught immediately by a `grep -c` check; re-applied and thereafter backed up to the scratchpad before every mutation.

## Known stubs

None. Every artifact is wired and tested.

## Nothing fired

No enclave / VM / Dataproc / OSF / `gsutil` / `gcloud` / network contact. **$0.** No per-sample data created, read or moved. The in-flight ~4h20m sweep was **neither touched nor required to re-run**; the live runbook is byte-identical. **No pre-registered number moved**, enforced structurally: the pre-registration file was not edited at all.

## Self-Check: PASSED

All 8 claimed files exist on disk. All 4 claimed commits exist in `git log`.
`git apply --check` confirms the parked docstring patch still applies cleanly to
HEAD, so the post-sweep task can re-apply it unchanged.

Tracked-tree state: only `.planning/STATE.md` is modified-and-uncommitted (left
for the orchestrator's docs commit, per the executor contract). The untracked
`.planning/debug/m3-producer-unbounded-dense-read.md` is **pre-existing** — it
was present in `git status` at session start and was not touched.
