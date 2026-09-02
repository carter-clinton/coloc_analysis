---
phase: quick-260901-rvu
plan: 01
subsystem: m3-afr-ld-panel
tags: [pairwise-completeness, occlusion, panel-wide-excludelist, pre-vs-post-filter, partial-confounding-tail, informative-carriers, carrier-distribution-no-floor, post-hoc-no-rerun, staged-not-run, prereg-unchanged, nothing-fired]

requires:
  - phase: quick-260831-kw8
    provides: "pcs_panelwide_reclassify.py — the per-region panel-wide excludelist and the undefined-row verdicts this extension reuses unchanged"
  - phase: quick-260901-l55
    provides: "the STEP 0 gate rescoped onto a git-ref CODE pin (assert_code_frozen vs cb199b6), which is the constraint that forced the DIFFERENTIAL tail pin instead of a shared helper"
provides:
  - "DEFINED-row tail classification: PRE-filter vs POST-filter at BOTH row and pair level, as separate reconciled keys, against the SAME per-region excludelist"
  - "the informative-carrier distribution Seth says he lacks — integer nearest-rank percentiles, exact counts for every m in 0..100, cumulative low tail — computed twice (all defined rows / rows reaching the matrix)"
  - "a differential pin of the tail predicate against the CODE-FROZEN scanner's own n_defined_lost_frac_ge_0p9, plus an optional runtime --pcs-summary reconciliation"
  - "an import ALLOWLIST replacing the post-hoc surface blacklist, RED in three directions"
  - "a STAGED-NOT-RUN invocation whose argv is parsed by _build_parser on this node"
  - "the record: the survivor's route is ADJACENCY WITHOUT OCCLUSION, and Seth's 'constant still 0.0005' is flagged stale"
affects: [m3-afr-ld-panel, osf-preregistration, seth-consultation, pcs-sweep]

tech-stack:
  added: []
  patterns:
    - "DIFFERENTIAL pin instead of shared extraction when the donor module is code-frozen"
    - "guard scoped to where the banned thing can ACTUALLY exist (numeric-valued floor constants; comparisons; not key names)"
    - "call-time threshold resolution so a module-global monkeypatch is not silently inert"
    - "split by row_class BEFORE rolling up, so two scopes never share a rollup"

key-files:
  created:
    - .planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md
    - .planning/quick/260901-rvu-answer-seth-s-load-bearing-pre-vs-post-f/260901-rvu-RECORD-what-changes-and-the-survivors-route.md
  modified:
    - src/python/pcs_panelwide_reclassify.py
    - tests/m3/test_pcs_panelwide_reclassify.py

key-decisions:
  - "The tail predicate is DECLARED in pcs_panelwide_reclassify and pinned DIFFERENTIALLY against pairwise_completeness_scan.summarize, because the scanner is CODE-FROZEN against cb199b6 by a runbook gate a committed test executes in a subprocess. The design is forced, not a shortcut."
  - "NO carrier floor anywhere — not a constant, not a comparison, not a key name. Seth's m=25 -> SE(r)~0.20 calibration is recorded and explicitly NOT adopted."
  - "The no-floor guard's (e1) check is scoped to NUMERIC-VALUED module-level assignments. The plan's literal '(?i)floor on any target' was MEASURED firing on the tool's own compliant NO_FLOOR_NOTICE."
  - "The invariance regression asserts EQUALITY on the eleven undefined-scope banked keys and EXACT MOVEMENT on the two input-basis keys, because n_rows_in_tsv and n_defined_rows_in must move when defined rows are added — equality there would assert a bug."
  - "n_defined_rows_out_of_scope added as a 19th new pooled key so the defined-row reconciliation is checkable from the artifact alone."
  - "Seth's stale 'constant still 0.0005' is FLAGGED with three-step evidence, never silently corrected inside his words."

patterns-established:
  - "A negative control on a threshold requires the threshold to be resolved at CALL time; a default argument freezes it at def time and makes the control vacuous."
  - "A key-collection AST gate needs an ANCHOR assertion: POOLED_KEYS became a BinOp concatenation and the gate silently collected zero keys."

requirements-completed:
  - RVU-TAIL-CLASSIFIED-PRE-VS-POST-FILTER-NEVER-COLLAPSED
  - RVU-TAIL-PREDICATE-PINNED-TO-THE-SCANNERS-OWN-SUMMARIZER
  - RVU-CARRIER-DISTRIBUTION-EMITTED-NO-FLOOR-PROPOSED
  - RVU-RARER-MEMBER-RULE-STATED-TIE-BROKEN-AND-DISAGREEMENT-COUNTED
  - RVU-UNDEFINED-SCOPE-NUMBERS-BYTE-IDENTICAL-UNDER-THE-EXTENSION
  - RVU-POSTHOC-SURFACE-ALLOWLIST-NOT-BLACKLIST-SEEN-RED
  - RVU-SCANNER-CODE-PIN-UNBROKEN
  - RVU-STAGED-NOT-RUN-WITH-AN-ARGV-GATE
  - RVU-SURVIVOR-ROUTE-RECORDED-ADJACENCY-WITHOUT-OCCLUSION
  - RVU-SETHS-STALE-CONSTANT-FLAGGED-NOT-SILENTLY-CORRECTED
  - RVU-PREREG-NUMBERS-DO-NOT-MOVE
  - RVU-SUITE-REBASELINE-COMPONENT-EXACT-BY-NAME
  - RVU-NOTHING-FIRED

duration: ~55min
completed: 2026-09-01
---

# quick-260901-rvu: Seth's load-bearing PRE- vs POST-filter question — the instrument, built and staged

**The 3,094-row defined tail is now CLASSIFIABLE against the same production excludelist the tool already builds — PRE-filter vs POST-filter, at row and pair level, as separate reconciled keys — and the informative-carrier distribution Seth says he lacks is emitted twice, with no floor proposed anywhere. BUILT, TESTED, STAGED. NOT RUN. $0.**

## Performance

- **Duration:** ~55 min
- **Tasks:** 4/4
- **Files modified:** 2 code, 2 new records, 1 new staged doc
- **Nothing fired:** no enclave, VM, Dataproc, OSF, `gsutil`, `gcloud` or network contact. VM STOPPED.

## What was wrong, and what is now true

Seth conceded Q4 — *"a detector keyed to the endpoint is structurally blind to the neighbourhood of the endpoint, and the neighbourhood is where almost all the mass is"* — and then refused the rest of the consultation until one question is settled: **are the 3,094 defined rows with `carriers_lost_frac >= 0.9` PRE-filter or POST-filter?**

It was **UNMEASURED, not mis-scoped.** `pcs_panelwide_reclassify` filtered its row set to `undefined` rows, so all **353,074** defined rows were READ and never CLASSIFIED. The machinery was correct and pointed at the wrong subset. **The denominator is settled: 353,074 = 353,089 candidate − 15 undefined; 3,094 / 353,074 = 0.876%.**

## Accomplishments

### Task 1 — RED first (20 new/renamed tests, every one observed failing for the right reason)

18 failures on the first run, all assert / `AttributeError` / `KeyError` **inside test bodies**, zero collection errors — the module is imported inside each test, mirroring the file's existing discipline.

### Task 2 — GREEN, without moving one banked number

`_classify_region` now takes the defined rows too and classifies them against **the SAME single `detect_occluded_variants` call per region** — never a second call over a different row set, which would break the monotonicity argument the soundness of every occluded verdict rests on. Emission stays bounded to `undefined + tail` and the tool **refuses to return** if that identity fails.

⚠ **`out_rows` is split by `row_class` BEFORE rolling up.** `_roll_up` (the banked thirteen) sees the UNDEFINED subset alone; `_roll_up_tail` is a second, separately-scoped call. Both share `_occlusion_split` so they cannot diverge in *how* they count, while operating on disjoint subsets.

### Task 3 — the post-hoc surface gate becomes an ALLOWLIST

`_assert_no_genotype_or_network_surface(text)` takes SOURCE TEXT, so the controls run **in memory** and no stale `__pycache__` can decide the outcome. It RETAINS every prior assertion and adds: imported module roots ⊆ a named allowlist (collected by `ast.walk`, i.e. anywhere, not only top-level); `.fam` / `gs://` / `http://` / `https://` banned in CODE; `subprocess` / `socket` / `urlopen` / `Popen` / `system` banned as name or attribute.

### Task 4 — staged, recorded, not run

The staged doc carries `STATUS: STAGED — NOT RUN`, a pre-flight with a STOP on each check and **ROTATE-NEVER-DELETE**, a one-region smoke before the 21-region run, a COST NOTE stated as a BASIS with an explicit refusal to predict a runtime, and **WHAT EACH ANSWER MEANS** for both branches of the fork with the monotonicity condition attached.

## Deviations from Plan

### 1. [Rule 1 - Bug] The plan's literal no-floor check (e1) fires on the tool's own compliant source

- **Found during:** Task 1/2
- **Issue:** the plan specified *"no module-level assignment target matches `(?i)floor`"* while Task 2 REQUIRED the constant `NO_FLOOR_NOTICE` and the pooled key `no_floor_notice`. **MEASURED on the finished module:** the literal check returns one hit, `('NO_FLOOR_NOTICE', 'Constant', 'NOT numeric')` — i.e. it fires on the tool's own DISCLAIMER, making green unreachable while the constant stays required. This is the exact text-vs-meaning failure mode the plan called out for (e3), surviving one paragraph higher.
- **Fix:** (e1) is scoped to where a floor can ACTUALLY exist — a module-level assignment whose target matches `(?i)floor` **and whose value is NUMERIC**, plus a second clause banning numeric module-level constants whose target names `informative_carriers` (which the plan did not have and which catches `MIN_INFORMATIVE_CARRIERS = 25`, a floor that never says "floor"). The required RED observation is preserved: `CARRIER_FLOOR = 25` still raises.
- **Files:** `tests/m3/test_pcs_panelwide_reclassify.py`

### 2. [Rule 1 - Bug] The plan's literal invariance assertion is false by construction on two keys

- **Found during:** Task 1
- **Issue:** the plan required *"every one of the thirteen pre-existing POOLED_KEYS is identical between the two runs"*. **MEASURED:** `n_rows_in_tsv 1 -> 3` and `n_defined_rows_in 0 -> 2` when defined rows are added. They count the INPUT FILE, so equality would assert a bug — and the banked `n_defined_rows_in` is 353,074, never zero.
- **Fix:** EQUALITY on the eleven undefined-scope keys (the ones carrying the banked 15 / 13 / 14-1 / 12-1), EXACT MOVEMENT (`+ len(added)`) on the two input-basis keys. Strictly stronger than equality-or-nothing.
- **Files:** `tests/m3/test_pcs_panelwide_reclassify.py`

### 3. [Rule 2 - Missing critical functionality] `n_defined_rows_out_of_scope` added as a 19th new pooled key

- **Found during:** Task 2
- **Issue:** `n_defined_rows_member_occluded_panelwide + n_defined_rows_reaching_matrix` are IN-SCOPE quantities while `n_defined_rows_in` is the INPUT count. With `--region-ids` narrowing the run they differ, and nothing in the summary let a reader see by how much — the reconciliation would be uncheckable from the artifact. The plan already accepted `n_tail_rows_out_of_scope` for exactly this reason; the defined twin was an omission.
- **Fix:** key added; the tool reconciles on the in-scope basis internally and STOPS if it fails.
- **Files:** `src/python/pcs_panelwide_reclassify.py`, `tests/m3/test_pcs_panelwide_reclassify.py`

### 4. [Rule 1 - Bug] `is_tail_row`'s threshold must resolve at CALL time

- **Found during:** Task 1
- **Issue:** the plan's negative control monkeypatches `R.TAIL_MIN_CARRIERS_LOST_FRAC`. Bound as `threshold=TAIL_MIN_CARRIERS_LOST_FRAC` (a default argument, evaluated at `def` time) the monkeypatch would be **silently inert** and the control vacuous.
- **Fix:** `threshold=None` resolved from the module global at call time; the test asserts the perturbation changed the count by exactly 1 and names the inert-default hypothesis in its failure message.
- **Files:** `src/python/pcs_panelwide_reclassify.py`

### 5. [Rule 1 - Bug] The (e3) key collection silently narrowed to zero keys — observed RED

- **Found during:** Task 2
- **Issue:** `POOLED_KEYS` became `BANKED_POOLED_KEYS + TAIL_SCOPE_POOLED_KEYS`, an `ast.BinOp` with no `.elts`. The gate walked three named tuples, collected **no tail keys at all**, and the `n_tail_rows_unreliable` control reported **`DID NOT RAISE`** — a green over an empty set.
- **Fix:** collect from EVERY module-level `*_KEYS` / `*_COLUMNS` tuple (suffix rule, closed under future splits) **plus an ANCHOR assertion** that `n_rows_in_tsv` is among the collected names, so a future narrowing says so instead of passing.
- **Files:** `tests/m3/test_pcs_panelwide_reclassify.py`

### 6. [Rule 1 - Bug] Fixture `pair_key` was not order-normalised

- **Found during:** Task 2
- **Issue:** `_defined_pairs_row` built `f"{del_index}|{partner_index}"` while the scanner's `_pair_key` is ORDER-NORMALISED over the sorted index pair. A defined row reusing 46714/46715 also collided with the banked undefined pair's key, making the two scopes indistinguishable in the output.
- **Fix:** fixture mirrors `min|max`; the PRE-filter tail row uses distinct indices (90001/90002).
- **Files:** `tests/m3/test_pcs_panelwide_reclassify.py`

## RED observations (a green assertion is evidence ONLY if seen RED)

| # | Gate | Perturbation | Observed |
|---|------|-------------|----------|
| 1 | tail differential | `is_tail_row` `>=` → `>` on disk, `__pycache__` cleared | `AssertionError: the local tail predicate (4) has drifted from the scanner's own n_defined_lost_frac_ge_0p9 (5)` — both differential tests RED |
| 2 | invariance regression | combined `out_rows` fed to `_roll_up` at region AND pooled level | `UNDEFINED-SCOPE KEY 'n_undefined_rows_in' MOVED when defined rows were added: 1 -> 3` |
| 3 | no-floor (e1) | `CARRIER_FLOOR = 25` injected at module level, in memory | raises, message contains `DECLARED` |
| 4 | no-floor (e2) | `if row["informative_carriers_rarer"] < 25: pass` injected into a FunctionDef byte span | raises, message contains `APPLIED` |
| 5 | no-floor (e3) | key renamed to `n_tail_rows_unreliable` | **first attempt: `DID NOT RAISE`** (deviation 5) — after the fix, raises naming the key |
| 6 | surface allowlist | `import numpy` after `from __future__` | raises, message contains `ALLOWLIST` and `numpy` |
| 7 | surface `.bed` | `.bed` path literal injected into a FunctionDef body (never a docstring) | raises naming `.bed` |
| 8 | surface `BedReader` | `_plink.BedReader` attribute injected into a FunctionDef body | raises naming `BedReader` |
| 9 | staged argv | `--bfile-prefix` → `--bfile-prefixx` in the STAGED DOC on disk | `pcs_panelwide_reclassify: error: the following arguments are required: --bfile-prefix` → `SystemExit` |
| 10 | plan-literal (e1) | run as written against the finished module | fires on `NO_FLOOR_NOTICE` (deviation 1) |
| 11 | plan-literal (f) | run as written | `n_rows_in_tsv 1 -> 3`, `n_defined_rows_in 0 -> 2` (deviation 2) |

Every perturbation asserted BOTH that it changed the text AND — for the byte-range injections — that it landed inside a `FunctionDef` span. No `text.replace` was used for a control that claims to land in code (the M7 trap).

## Frozen surfaces

`git status --porcelain` EMPTY for `pairwise_completeness_scan.py`, `occlusion_span_filter.py`, `run_native_ld_panel.py`, `fire_verifier.py`, `aou_ld_panel.py`, `tests/m3/source_freeze.py`, `.planning/amendments/`, and both already-fired PENDING-PASTE docs. `test_pending_paste_step0_pins_the_scanner_CODE_against_a_git_ref` **PASSED** — the runbook's STEP 0 `assert_code_frozen(..., cb199b6, LANG_PY)` subprocess still exits 0.

## No pre-registered number moved

`353089` / `353090` / `353074`, 15 rows, 13 pairs, 10-3, the offset histogram `{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}`, panel-wide 12-1 pairs and 14-1 rows, and the 3,094-row (0.876%) tail all STAND. `.planning/debug/260826-PCS-...-prereg-prediction.md` and everything under `.planning/amendments/` were not edited at all.

## STAGED, NOT RUN

`.planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md` — `STATUS: STAGED — NOT RUN`. The input `pcs_pairs.tsv` is IN-PERIMETER and the VM is **STOPPED**. Running it is Carter's call, later. Its argv is parsed by `_build_parser` on this node by a committed test with a `SystemExit` negative control.

## Open, unchanged

- `src/python/samepos_missingness_probe.py` is still BUILT / TESTED / **NOT RUN**.
- **Seth's own check on his own answer is UNMEASURED:** *"Is the surviving pair inside, or adjacent to, a credible set or a known association signal for any of the 9 traits?"* Region 1's precedent (an occluded SNP present in 7 of 9 AFR traits with real effect estimates) is why that is not rhetorical.
- The consultation stays blocked until the staged run lands.

## Suite reconciliation, BY NAME

| | passed | skipped | failed | collected |
|---|---|---|---|---|
| baseline (`a7f1291`) | 1168 | 33 | 0 | 1201 |
| now (`e380840`) | **1187** | **33** | **0** | **1220** |

`1168 − 1 removed + 20 added = 1187` — exact. Run time 821.34s (13m41s).

**REMOVED (1):** `test_only_undefined_rows_are_reclassified` — RENAMED to
`test_defined_rows_below_the_tail_are_counted_but_not_emitted`, with every prior
assertion kept and `n_defined_rows_in` still pinned.

**ADDED (20):** `test_the_surface_gate_fails_on_an_injected_surface`,
`test_defined_rows_below_the_tail_are_counted_but_not_emitted`,
`test_the_tail_predicate_agrees_with_the_scanners_own_defined_lost_frac_ge_0p9`,
`test_the_tail_differential_is_not_vacuous`,
`test_a_tail_row_whose_member_is_occluded_is_PRE_filter`,
`test_a_tail_row_with_neither_member_occluded_is_POST_filter`,
`test_both_tail_verdicts_reconcile_at_row_and_pair_level`,
`test_a_defined_row_below_the_tail_is_not_emitted_and_an_undefined_row_is_never_tail`,
`test_the_tail_counts_reconcile_or_the_tool_raises`,
`test_the_rarer_member_is_chosen_by_marginal_maf_not_by_marginal_carrier_count`,
`test_an_exact_maf_tie_picks_the_worse_precision_and_flags_the_tie`,
`test_the_two_carrier_definitions_can_disagree_and_the_disagreement_is_counted`,
`test_the_percentiles_are_integer_nearest_rank_on_a_known_array`,
`test_the_low_tail_counts_are_exact_and_cumulative_and_cover_every_m_to_100`,
`test_the_distribution_is_reported_twice_over_all_defined_rows_and_over_rows_reaching_the_matrix`,
`test_the_tail_split_cannot_be_printed_without_its_scope_condition`,
`test_no_carrier_floor_is_declared_anywhere`,
`test_the_no_floor_guard_fires_on_each_injected_floor`,
`test_adding_defined_rows_does_not_move_any_undefined_scope_pooled_key`,
`test_the_staged_doc_argv_parses_against_the_declared_contract`.

**Per file:** `test_pcs_panelwide_reclassify.py` **21 → 40**;
`test_pairwise_completeness_scan.py` **115 → 115** (unedited); third file
**39 → 39**. **Skips held at exactly 33** — no new test landed as a SKIP.

## Commit

`e380840` — ONE commit, six explicit paths (`git add` by path only; never `-A` / `.`).

## Self-Check: PASSED

- All created/modified files FOUND on disk.
- Commit `e380840` FOUND in `git log --all`.
- `src/python/pcs_panelwide_reclassify.py` 1352 lines (min 900);
  `tests/m3/test_pcs_panelwide_reclassify.py` 2342 lines (min 1500).
- `TAIL_VERDICT_SCOPE` present in the module (5 occurrences);
  `ADJACENCY WITHOUT OCCLUSION` present in the RECORD.
- Staged doc first lines carry `STATUS: STAGED — NOT RUN`; it has NOT been executed.
- SUMMARY / STATE.md / PLAN deliberately LEFT UNCOMMITTED for the orchestrator's
  docs commit.

## Deferred

See `deferred-items.md`: `.planning/STATE.md`'s frontmatter does not parse as
strict YAML — **measured failing identically at `HEAD` and after this edit**, and
the segment this task prepended contains **0** double-quote characters. Not
introduced here, not worsened here, not fixed here (out of scope).
