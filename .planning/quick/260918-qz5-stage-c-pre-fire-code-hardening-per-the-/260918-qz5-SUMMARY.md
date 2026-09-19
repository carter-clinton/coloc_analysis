---
task: 260918-qz5
status: complete
executed: 2026-09-18 → 2026-09-19
base: b6076b2
head: 0206a71
commits: 9
authored_by: ORCHESTRATOR, from the executor's hand-back — the executor's harness refused the report-file write (the plan's own Step-7 fallback; see [[feedback_subagent_summary_write_blocked]]). Every figure below was reproduced by the orchestrator independently; §11 records what the orchestrator measured firsthand.
---

# 260918-qz5 — Stage C pre-fire code hardening (SUMMARY, orchestrator-written)

Implements the two code changes the external reviewer named as HARD requirements before Stage C,
plus Carter's gate-semantics decision, the closeout enforcer, and the runbook + paste-surface sync.
Records side is `quick-260918-qz0`. **Nothing fired. No push. No cloud/OSF/reviewer/network action.**

## 1. Commits (BASE `b6076b2` → HEAD `0206a71`; branch 12 ahead of origin, NOT pushed)

| # | SHA | Task | What |
|---|---|---|---|
| 1 | `b1d3ff3` | 1 | test: X1 RED (7/7 observed) |
| 2 | `201f572` | 1 | fix: X1 — coordinate-only evidence on every square outcome |
| 3 | `15721d9` | 2 | test: `raised_nan:` producer RED (4/4) |
| 4 | `4e34e83` | 2 | feat: P2 — **the ast vocabulary enforcer is RED at this commit, by design** |
| 5 | `4cfd111` | 2 | feat: P3 — `raised_nan:` is its own verifier class |
| 6 | `0fe89f3` | 3 | test: stateful stage-C + closeout enforcer RED (9/9) |
| 7 | `58caee5` | 3 | feat: `--prev-report`, the aliasing guard, the zero-row FAIL, coverage |
| 8 | `236735c` | 4 | test: the named runbook enforcers — **two-surface RED at this commit, by design** |
| 9 | `0206a71` | 4 | docs: the four runbooks + the corrected skip-count docstring |

Nine files changed, frozen-list intersection EMPTY: `run_native_ld_panel.py` `c00ea0d96b3c1a50161e0f944fd4ad39` (1487→1656) · `fire_verifier.py` `99df638fe2b1ccaacf926de7c6b60db8` (1186→1668) · `test_run_native_ld_panel.py` `342f9962ae7625f197defcabff314018` (2723→3298) · `test_fire_verifier.py` `b64e3baa0b28777ea0851a51a6fa7675` (1166→1760) · `test_fire_runbook_pins.py` `0689f609e0a2f9a3b3a3049b5b75f55a` (new, 327) · `260812-ox1-AGENT-PROMPT.md` `831c3bc566f2c428f42998e9ea8410c3` (709→814) · `260812-ox1-BROWSER-PASTE.md` `36ec97d0f0c5197e6268f84d6eb2b014` (816→905) · `260812-ox1-READY-TO-FIRE.md` `a3555a53601a33022e1b2aef47fc953c` (525→595) · `SKILL.md` `fc7e64b9a266644bf5c6e6cbe607974a` (114→115).

## 2. What landed

**X1 — a posted commitment made TRUE in code.** mk7ze P248-250 commits that every region's occlusion
count AND its occluded-site inflation fold in at closeout. It was FALSE for every raising region:
the uploads sat inside `if ok:`, and — the correction to the reviewer's own prescribed fix — a
raising region never reaches that block at all, because the frozen reader raises upstream of it.
`_upload_coordinate_artifacts` (existence-gated, four suffixes) is now called from **site (a)**
after `result["n_var"] = n_var` and BEFORE the reader (UNGUARDED: on `ok`,
`_reclaim_region_scratch` deletes the evidence, so a swallowed failure would destroy it silently),
**site (b)** inside the `except` (GUARDED: one bad region never aborts the loop, and the region
keeps its ORIGINAL failure), and the deferral branch. Bounded retry `_COORD_UPLOAD_ATTEMPTS=3`,
backoff 2 s/5 s, `time.sleep` monkeypatchable, no test sleeps. **The `.npz` gate did not move**
(R8) and no retry leaked to it (asserted: exactly ONE `.npz` attempt on a persistent failure).
Banded mode is a proven no-op.

**`raised_nan:` is its own class end to end.** Matched by MESSAGE HEAD
(`_NAN_RAISE_MESSAGE_HEAD = "square LD carries NaN"`), never by exception type — the read path has
9 `ValueError` sites and 0 `try` blocks, so the raise propagates unwrapped and type-matching would
be a lie. `n_var` preserved, detail suffix intact through the panel-TSV round trip, `RAISED-NAN`
stderr line. `STATUS_RAISED_NAN` is tested before the failure branches and is deliberately NOT in
`_DEFERRAL_PREFIXES`, so it can never reach the PASS-as-the-gates-working branch.

**B2 — the framing the adjudication disqualified is gone.** On a raise-bearing panel the PASS
detail states all five counts (reconciling to `n_rows`) and replaces the deferral-guidance clause
with one naming the contract executing, "NOT the occlusion gates working, and NOT a deferral". On a
zero-raise panel the shipped sentence survives VERBATIM, pinned by a control. `n_bankable` stays
ok-class only; the new counts are keyword-only with 0 defaults, so every 3-positional call site is
byte-unchanged.

**Stage C is stateful (Carter's decision).** `--prev-report`; exit 1 only on a NEW failure since the
last check-in; acknowledged raises still reported and still counted; disappeared row → HARD_STOP
with the rotation remedy; unknown status never acknowledgeable; fail-closed on missing, unparseable
or pre-change (`acknowledgeable_schema`) reports, each remedy asserted — reachable only because the
loaders return a `Check`. **The aliasing guard is pinned on the FILE** (md5 of the prev report
unchanged across an aliased call), runs in `main()` BEFORE the checks and returns without writing.
Exit codes match the re-measured BASE column for all seven panel shapes, with exactly one
deliberate change: **header-only 0 → 1**, in `_stage_c` (mandated, not the executor's choice,
because `classify_statuses` also feeds stage-a and stage-b), listing five routes into that state
without asserting one.

**Closeout enforcer** `raised_nan_class_coverage` / `check_raised_nan_coverage` /
`test_raised_nan_class_coverage_live_gate_against_the_repo_file`, reading `## R5-RAISED-NAN`
(present at `deferred-items.md:1454`). It SKIPS while no measured panel TSV is in-repo — that skip
IS the enforcer — and checks **presence, count and the UNCLASSIFIED default only**, because the
classifier (LOW-1) is deferred until COST-1 measures a per-region wall time. Nothing claims
classification exists.

**Runbooks.** All ten enumerated edits; the log monitor corrected at all THREE occurrences with zero
stale bare copies remaining; both FALSE-under-P1 egress sentences corrected (the four coordinate
artifacts no longer imply a banked region — only `.npz` presence does, which is why liveness stays
the `.npz` count); the day-one line (before the first region completes both the `gsutil cp` and the
gate fail — that is the gate failing closed, not a fire defect); the X2 scratch-headroom line; the
plink-only `peak_ram_gib` caveat. **BROWSER-PASTE now carries the condensed raise posture** — the
real gap, since qz0's block was agent-surface-only. READY-TO-FIRE got a pointer plus one
resume-class clause, NOT a third copy (it is Carter's go/no-go document, not an operating surface;
and this same task had to repair three stale copies of one monitor line — duplication is the defect
class here).

## 3. Observed REDs — every added assertion has one

Task 1 7/7 · Task 2 producer 4/4 · **the required enforcer RED, banked:**
`test_shipped_status_vocabulary_is_covered_by_the_allow_list` failed with
`uncovered == ['raised_nan: ']` while `…extractor_is_not_vacuous` stayed GREEN (`len(found)` 7→8),
committed red at `4e34e83` and green at `4cfd111`, with no hand-back between those steps · Task 3
9/9 (`SystemExit: 2` from argparse, `AttributeError` for the absent check) · Task 4 two-surface RED
observed twice, and the byte pin proven able to fail on a mutated copy. The closeout enforcer's
predicate discriminates four ways (region omitted/listed, heading renamed, extractor on a renamed
heading).

## 4. Suite reconciliation by test id — the criterion met exactly

```
BASE 1262 ids {passed 1229, skipped 33}
POST 1299 ids {passed 1265, skipped 34}
REMOVED 0 · OUTCOME CHANGES 0 · ADDED 37 (36 passed + EXACTLY ONE skipped)
ADDED not-passed: ['test_raised_nan_class_coverage_live_gate_against_the_repo_file']
skips 33 -> 34
```
`tests/phase2` 136 passed / 1 skipped. The 20 pre-existing reds outside `tests/m3` (m2/phase5/phase9)
are unrelated and unchanged. `test_no_hardcoded_shipped_constants_in_the_module` passes — no numeric
literal was added to `fire_verifier.py`. `tests/m3/sparse_parent_benchmark.tsv` restored with
`git checkout --` after every full run.

## 5. Byte pins

Fire command `16a8417991547c3e423fc356cec41f89` (2 lines, 330 B); STEP 9d
`7dd6c73ec14b640dcaf41526f1221fca` (149 lines, 7,972 B). Both blocks verified byte-identical at
`940df48` and `b6076b2` — qz0's +38 lines touched neither, and all eight AGENT-PROMPT hunks land at
`:615+`, clear of the fire command (`:595-596`) and STEP 9d (`:440-588`). The pin's exit route is in
the test's own docstring: re-pin these two constants and nothing else, in the same commit as a
recorded decision, never to silence an unexplained red.

## 6. Findings — measured, not adjusted

1. **The plan's own Step-3c narrowed-form regex was VACUOUS.** `[^.]{0,400}` terminates on the
   period inside `` `.npz` ``, so the span could never contain `error:` and the mandated
   non-vacuity control could not be satisfied. Replaced with a real sentence bound
   (`.{0,600}?\.(?=\s|$)`), proven RED on the reviewer's C5 sentence and not false-positive on the
   corrected one. This strengthened the gate from unfailable to failable.
2. **T1.8(iii) was stale**: it demanded "exactly `_COORD_UPLOAD_ATTEMPTS` cp calls"; measured 6 =
   2 × ATTEMPTS, the direct consequence of the plan's own W-r2-4 decision (a site-(a) failure leaves
   `coords_uploaded` False, so site (b) re-runs the helper). Pinned at `2 * ATTEMPTS` plus a
   per-site WARN decomposition — strictly tighter than "exactly 3".
3. **T3.4's "no `raised_nan` string in the output" was unsatisfiable** — the two new checks' own
   NAMES contain it and `_print_summary` prints every name. Replaced with the actual intent:
   present-but-SILENT (`0 raised-NaN row(s)`).
4. **Step 5b's premise about pytest output was false**: `pytest -q -rs` prints
   `SKIPPED [1] <file>:<line>: <reason>` with no test NAME. Replaced with a by-id JUnit parse
   asserting the skipped set equals exactly the two named ids — pinning WHICH two skip.
5. **A pre-existing behaviour worth Carter's eye.** At BASE, an otherwise-`ok` region whose
   gate-sidecar upload failed banked its `.npz` and THEN recorded `error:`. After site (a) that
   failure costs the region instead of banking an `error:`-labelled `.npz`. T1.5 pins the new
   behaviour.

Also recorded, not silently fixed: the adjudication's `mk7ze P247-250` is one line early (the
sentence is at posted 248); `M22`'s annotation `BROWSER-PASTE:535` for anchor B4 measured at `:536`
(secondary annotation only — anchors were the locator).

## 7. Deviations

1. `$SCRATCH` already existed from the stopped pre-flight run; the plan forbids deleting it, so it
   was PRESERVED BY RENAME and every pre-flight fact re-measured from scratch (no transcript
   inherited).
2. Finding 1's regex fix. 3. T1.3/T1.9 were GREEN at BASE (no-change regression pins) and were
   proven able to fail in a mutated shared clone — the first mutation worked for a side-effect
   reason, so a confound-free second mutation was used. 4. Finding 2's fix. 5. T1.1's blanket
   "no cp destination ends `.npz`" was unsatisfiable with a second legitimately-`ok` region in the
   manifest (which is what proves the loop continued); scoped to the raising region, with
   `.bed/.bim/.fam` still banned globally. 6. Finding 3's fix. 7. Finding 4's fix.
8. **A control bug caught and fixed:** the byte-pin's able-to-fail control first mutated the ANCHOR,
   breaking the extractor rather than the pin — a control that passes for the wrong reason.
   Replaced with an `--ancestry AFR → EUR` mutation (a one-token edit a diff review slides past,
   and one that would fire the whole panel against the wrong cohort).
9. Task 3 landed in 2 commits, not 3 (one file edit, artificial to split).
10. ⚠ **One bullet inside qz0's landed block was corrected** — `⚠ WHAT THE GATE CAN SEE TODAY`,
    whose stated precondition was literally "Until quick-260918-qz5 lands the distinct
    non-deferral raise status and its own verifier class". That has now happened, so the bullet was
    FALSE in the operator's primary runbook. Corrected with the retired wording preserved verbatim;
    qz0's four operative rules untouched; not done to satisfy any test. **Orchestrator reviewed and
    APPROVED this** (§11).
11. Byte-pin constants labelled with BOTH `940df48` and `b6076b2`, both verified identical.
12. Two keyword names differ from the plan's text (`acknowledged=` not `acknowledged_regions=`)
    because the latter would shadow the module-level `acknowledged_regions()` function. Defaults
    `None` ⇒ today's behaviour, so no call site moved.
13. The cost-denominator detail gained explicit `raised-NaN` wording, and its test asserts the
    PROPERTY (`1 raised-NaN`, `0 operational failure(s)`, and that the two-reason detail differs
    from the control's) rather than a bare word.
14. Two negative assertions re-scoped off loose literals to avoid the forbidden-literal trap
    (`"ALL recognized (the gates"` and `"do NOT 'fix' a deferral mid-fire"` rather than the
    ambiguous `"the gates working"`, which the raise branch legitimately contains).
15. SUMMARY handed back rather than written (this file).

**Orchestrator-made, before execution:** the post-qz0 runbook re-pin (`f5584d4d…`/46,052 B →
`48295e10…`/709/46,067 B, 5 md5 + 6 byte sites); the Step-3c probe 3 re-word
(`never changes the inputs`, n=0 against qz0's landed wording → `inputs or the criterion`, n=1 and
already satisfied by the Step-3b block); three live-gate base references re-based `940df48` →
`b6076b2`. ⚠ **An orchestrator error, caught and fixed:** the probe re-word was applied with a
blanket replace that also corrupted the Step-3b block's own sentence into "It inputs or the
criterion or the criterion." The replacement count (2, not 1) surfaced it; line 1466 was restored to
"It never changes the inputs or the criterion." and all five probes re-verified in both surfaces.

## 8. The weakest gate, stated plainly

The two-surface posture check is a TEXT check — the weakest gate in this task under R4. It pins the
presence of the operative language, not a behaviour. That is what is at stake for a human-read
runbook and nothing stronger exists for prose; it must not be reported as a behavioural pin.

## 9. Threat register

T-qz5-01 (four-suffix allow-list closed; `.bed/.bim/.fam` asserted absent), -03
(`acknowledgeable_schema`, fail-closed, disappeared→HARD_STOP), -04 (`raised_nan:` deliberately not
a deferral; unknown un-acknowledgeable), -05 (message-head match behaviour-pinned + unrelated
`ValueError` control), -06 (site (b) guarded), -07 (site (a) unguarded) all mitigated as specified.
T-qz5-02 accepted, with the untouched `test_gs_resume_*` tests green. No new threat flags: no new
network endpoint, auth path or trust boundary beyond the `--prev-report` file input (already
T-qz5-03).

## 10. Known stubs

None. No stub was introduced.

## 11. Orchestrator verification (independent of the executor)

Measured firsthand after the hand-back, on the real tree at `0206a71`:
- 9 commits, 9 changed files, `git diff --name-only b6076b2 HEAD` exactly as listed; frozen-path
  diff EMPTY; `plink_ld_to_npz.py` `6f8a0e33…` and `condition_ld_matrix.py` `cf6f5655…` unchanged;
  tracked tree clean; 12 ahead of origin, unpushed.
- `_status_class` order OK → DEFERRAL → RAISED_NAN → FAILURE_STATUSES → FAILURE_PREFIXES, and
  `raised_nan` is NOT in `_DEFERRAL_PREFIXES` — so a raise is structurally unable to reach the
  deferral PASS branch.
- Call-site ordering: `result["n_var"] = n_var` (:1365) → **site (a)** (:1380) → the frozen reader
  (:1386) → `content_verify_npz` (:1391) → `if ok:` (:1398) → `.npz` upload (:1416); deferral site
  (:1245); site (b) (:1448). `_COORD_UPLOAD_ATTEMPTS=3`, backoff `2.0, 5.0`.
- The aliasing guard precedes both `args._run(args)` and the `json.dump`, uses `resolve()`, and
  returns early.
- The B2 branch is gated on `if by_class[STATUS_RAISED_NAN]:`, states all five counts summing to
  `len(status_rows)`, and the zero-raise path keeps the shipped sentence.
- qz0's four operative rules each occur exactly once in the runbook after the edit, alongside
  `ALREADY IN THE BUCKET` and `BOTH deferred_* classes`; Deviation 10's bullet keeps its heading,
  adds a dated update and preserves the retired wording — **approved**.
- The five named tests exist in `tests/m3/test_fire_runbook_pins.py`.
- The full `tests/m3` suite was re-run by the orchestrator; the result is recorded in the STATE
  ledger row for this task.
