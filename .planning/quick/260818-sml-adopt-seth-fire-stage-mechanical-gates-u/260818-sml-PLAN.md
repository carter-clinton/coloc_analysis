---
phase: quick-260818-sml
plan: 01
type: tdd
wave: 1
depends_on: []
mode: quick-full
autonomous: true
requirements: [SML-01, SML-02, SML-03, SML-04]
files_modified:
  - src/python/fire_verifier.py
  - tests/m3/test_fire_verifier.py
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md
  - .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md
  - .planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-COURIER-TO-SETH-adjudication.md
  - .planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-controls-transcript.txt
  - .planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-SUMMARY.md
  - .planning/STATE.md

must_haves:
  truths:
    - "A single command run on the AoU VM after `git pull` evaluates the Stage-A / Stage-B / Stage-C fire-stage invariants and exits non-zero if any of them is red."
    - "Every check in the module has been OBSERVED red at least once, with the verbatim red output recorded in-repo."
    - "The status allow-list matches the vocabulary the SHIPPED producer can actually emit, and a newly-added shipped status makes a test go red instead of passing silently."
    - "A real `deferred_infeasible_square: n_var=... > ceiling=...` row from the shipped producer classifies as RECOGNIZED (the gates working), not as an unknown status."
    - "The NaN falsification runs against the BANKED artifact through the SHIPPED verification path, memory-bounded, and names a NaN as a NaN rather than as an asymmetry."
    - "The browser agent's runbook says exactly when to run each gate, what to paste to Carter, and that it must never chain past a red."
    - "The R4-COVERAGE disclosure obligation has a NAMED enforcer that goes red the moment a measured panel TSV lands in-repo."
    - "260817-vbu-verify.sh is still green after every runbook edit."
    - "tests/m3 moves ONLY by the newly added tests: 0 failed, skips 31 -> 32, passed strictly greater than 914."
  artifacts:
    - path: "src/python/fire_verifier.py"
      provides: "Fire-stage mechanical gate library + argparse CLI (stage-a / stage-b / stage-c / disclosure)"
      exports: ["Check", "PASS", "HARD_STOP", "FINDING", "parse_panel_tsv", "check_nan_falsification", "check_manifest_rows", "check_occlusion_ceiling", "check_region1_status", "check_peak_ram", "check_maf_depression", "check_cost_denominator", "classify_statuses", "check_coverage_disclosure_resolved", "summarize", "main"]
      min_lines: 300
    - path: "tests/m3/test_fire_verifier.py"
      provides: "Green + red case for every check; the shipped-vocabulary AST drift guard; the live disclosure gate"
      min_lines: 400
    - path: ".planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-COURIER-TO-SETH-adjudication.md"
      provides: "The shipped-code-wins adjudication report Carter couriers back to Seth"
      contains: "D-02"
    - path: ".planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-controls-transcript.txt"
      provides: "Verbatim red output for each negative control, so a green is evidence"
  key_links:
    - from: "src/python/fire_verifier.py"
      to: "src/python/run_native_ld_panel.py"
      via: "import of _PANEL_COLUMNS, _OCCLUSION_ANOMALY_FRACTION, _DEFAULT_MAX_N_VAR, _DEFAULT_PANEL_NAME, content_verify_npz"
      pattern: "import run_native_ld_panel"
    - from: "src/python/fire_verifier.py"
      to: "src/python/plink_ld_to_npz.py"
      via: "import of the FROZEN _has_any_nan_blocked / nan_variant_indices (import, never fork)"
      pattern: "_has_any_nan_blocked"
    - from: "src/python/fire_verifier.py"
      to: "src/python/aou_ld_panel.py"
      via: "import of _MIN_REGION_NPZ_BYTES (the MED-6 byte floor)"
      pattern: "_MIN_REGION_NPZ_BYTES"
    - from: "tests/m3/test_fire_verifier.py"
      to: "src/python/run_native_ld_panel.py source text"
      via: "ast walk over result['status'] assignment sites -> allow-list coverage assertion"
      pattern: "ast.parse"
    - from: ".planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md"
      to: "src/python/fire_verifier.py"
      via: "STEP 8 / STEP 9 / STEP 10 gate invocations + R6 allowed-file extension"
      pattern: "fire_verifier.py"
---

<objective>
Convert Seth's fire-stage pre-fire checklist from a reference prototype into a
SHIPPED, TDD-pinned, fail-closed gate module wired into the fire runbook — with
every check adjudicated BY MEASUREMENT against the shipped producer/converter, and
every disagreement resolved in the shipped code's favour and reported back to him.

Purpose: the fire resumes at the Step 3 GATE and is imminent. A checklist a human
must remember works at region 1 with full attention and fails at region 180 at
3am. This makes the evidence for each go/no-go mechanical; it never makes the
decision (an agent never fires it).

Output:
- `src/python/fire_verifier.py` — library + argparse CLI, runnable on the VM after `git pull`
- `tests/m3/test_fire_verifier.py` — green + red for every check, negative controls observed red
- runbook wiring in the three `260812-ox1` fire packages
- a courier note back to Seth listing every shipped-code-wins adjudication
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-SETH-COURIER-mechanical-gates-as-received.md
@.planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/fire_verifier.py
@.planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/test_fire_verifier.py
@src/python/run_native_ld_panel.py
@src/python/plink_ld_to_npz.py
@.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md
@.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh
@tests/m3/source_freeze.py
@tests/m3/test_source_freeze_pins.py
@.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
</context>

<hard_rules>
1. **SHIPPED CODE WINS.** Every disagreement between Seth's prototype and the
   shipped producer/converter resolves in the shipped code's favour, and is
   RECORDED in the courier note. Never bend the shipped code to a prototype.
2. **DO NOT TOUCH the frozen modules.** `src/python/plink_ld_to_npz.py`,
   `src/python/occlusion_span_filter.py`, `src/python/condition_ld_matrix.py`,
   `src/legacy/region_analysis/scripts/run_susie_rss.R`. The verifier CONSUMES
   their behaviour. If a check needs a helper from a frozen module, **import it —
   never copy-paste-fork it** (a forked copy is a silent divergence with no
   enforcer).
3. **DO NOT MODIFY `src/python/run_native_ld_panel.py`.** It is not frozen, but it
   is the fire-path producer and this task is additive-only. If a check appears to
   need a producer change, STOP and report — that is a separate decision.
4. **Never hand-transcribe a shipped constant.** Import `_PANEL_COLUMNS`,
   `_OCCLUSION_ANOMALY_FRACTION`, `_DEFAULT_MAX_N_VAR`, `_DEFAULT_PANEL_NAME`,
   `_MIN_REGION_NPZ_BYTES`. A literal `0.0005` or `120000` or a re-declared `256`
   anywhere in `fire_verifier.py` is a defect.
5. **Memory-bounded verification only.** No `np.isnan(m)` / `np.allclose(m, m.T)` /
   `np.triu(m)` over a full dense matrix. Region 1 is 102,421^2 x 4 B = ~42 GB; an
   extra full-size temporary is how a verify OOMs a 120 GB VM. Use the frozen
   blocked helpers.
6. **GPFS.** No worktrees. Explicit-path `git add` only — never `git add .` / `-A`.
   Never commit `tests/m3/sparse_parent_benchmark.tsv` (a test rewrites it;
   `git checkout -- tests/m3/sparse_parent_benchmark.tsv` if dirtied).
7. **Nothing here fires anything.** No OSF contact, no perimeter contact, no
   network, $0. Push is the orchestrator's, not the executor's.
8. **A green is evidence only if it has been seen red.** Every negative control
   must be OBSERVED failing and its verbatim output recorded in
   `260818-sml-controls-transcript.txt`.
</hard_rules>

<planner_measurements>
These were MEASURED by the planner against the working tree on 2026-08-18. They
are LEADS with the exact command that produced them — **the executor re-confirms
each before relying on it** and records any discrepancy as a blocker.

**M1 — Panel TSV schema (9 columns).** `run_native_ld_panel.py:101-121`
`_PANEL_COLUMNS = [region_id, chr, n_var, wall_min, peak_ram_gib, output_gib,
status, n_dropped_occluded, n_dropped_monomorphic]`. 1-based awk positions: `$1`
region_id, `$3` n_var, `$4` wall_min, `$5` peak_ram_gib, `$7` status, `$8`
n_dropped_occluded — matches the runbook's own awk and STEP 4's "n_dropped_occluded
as the 8th (index 7)". Written by `_append_panel_row_local` (`:593`) via
`pandas.to_csv(sep="\t", index=False)`, so `None` renders as an empty field.
`append_panel_row` REFUSES (raises) on a stale header rather than repairing it.
Confirm: `grep -n "_PANEL_COLUMNS = " -A 22 src/python/run_native_ld_panel.py`

**M2 — Shipped status vocabulary (7 emission sites, NOT bare tokens).**

| site | emitted |
|---|---|
| `:774` | `"skipped_idempotent"` |
| `:785` | `"error"` (the initialiser) |
| `:831` | `f"deferred_infeasible_square: n_var={...} > ceiling={...}"` |
| `:854` | `f"deferred_occlusion_anomaly: {...} occluded of {...} (ceiling {...})"` |
| `:991` | `"ok" if ok else "verify_failed"` |
| `:1028` | `f"error: {e}"` |

Confirm: `grep -n 'result\["status"\]' src/python/run_native_ld_panel.py` and
`grep -n '"status":' src/python/run_native_ld_panel.py`

⚠ **This defeats Seth's `classify_deferrals` outright.** His exact-membership test
`s not in _EXPECTED_DEFERRALS` would flag EVERY REAL deferral (which carries a
detail suffix) as unrecognized -> HARD_STOP on the gates working, at every Stage-C
check-in. Matching must be PREFIX-based.

**M3 — The NaN falsification reader identity.** `plink_ld_to_npz.read_square_bin`
(`:198`) reads the plink **`.ld.bin`**, i.e. the PRE-`.npz` artifact, which is
deleted after a successful region (`_reclaim_region_scratch(..., keep_npz=not
gs_mode)`; the fire runs gs:// mode -> nothing local survives). The BANKED artifact
is the `.npz`. The shipped re-read of the banked `.npz` is
`run_native_ld_panel.content_verify_npz` (`:343`), which:
- `np.load`s the `.npz` and validates dtype float32, square shape,
  `np.allclose(np.diag(ld), 1.0, atol=1e-3)`, and
  `pln._is_symmetric_blocked(ld, atol=1e-4)`;
- **returns `(ok, reason)` — it does NOT raise**;
- detects NaN only INDIRECTLY: NaN on the diagonal fails the diag check, NaN
  anywhere fails the blocked symmetry check (`np.allclose` with default
  `equal_nan=False`) — and reports it as `"not symmetric (atol 1e-4)"`, i.e. it
  MISREPORTS the cause, which is exactly what the frozen reader's own comment
  (`plink_ld_to_npz.py:213-217`) warns against.

Confirm: `grep -n "def content_verify_npz" -A 42 src/python/run_native_ld_panel.py`

**M4 — Memory-bounded helpers exist and are frozen.**
`plink_ld_to_npz._has_any_nan_blocked` (`:151`, bounded by `block * n_var` bool
bytes), `nan_variant_indices` (`:163`, ranks source rows worst-first — handles the
whole-row-NaN-with-1.0-diagonal fire-#3 fingerprint), `_is_symmetric_blocked`
(`:136`), `_strict_upper_is_zero_blocked` (`:182`). Import these.

**M5 — The clause-(d) constant.** `_OCCLUSION_ANOMALY_FRACTION = 0.0005` (`:133`),
a MODULE GLOBAL read at evaluation time, **deliberately NOT CLI-tunable** ("a knob
would invite silent deviation from the public commitment"). The comparison is
`len(occluded_ids) > _OCCLUSION_ANOMALY_FRACTION * pre_window_n_var` — FLOAT
ceiling, STRICT `>`. Seth's boundary test (60 @ 120,000 passes / 61 fails)
reproduces the shipped comparison exactly. `_DEFAULT_MAX_N_VAR = 120000` (`:143`)
IS pinned-by-test to `config/pipeline.yaml` `m3_convert_max_n_var`
(`test_max_n_var_default_pins_consumer_ceiling` READS the YAML).

**M6 — VM RAM.** `.planning/debug/m3-producer-unbounded-dense-read.md:17` —
"n1-standard-32, 120 GB". `vm_gib=120` is repo-documented, not a guess.
Confirm: `grep -n "n1-standard-32" .planning/debug/m3-producer-unbounded-dense-read.md`

**M7 — `min_bytes=256` is the shipped floor.** `aou_ld_panel._MIN_REGION_NPZ_BYTES
= 256` (`:418`), the MED-6 resume-guard byte floor. Seth's default coincides
exactly; import it rather than re-declare it.

**M8 — The R4-COVERAGE disclosure text.**
`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`, section
`## R4-COVERAGE ...` at line 1148 running to EOF (1197). Measured content:
`| regions deferring at the 120k cap | **29 / 276 = 10.5%** |`,
`| bankable target | **~247 regions** |`, `| largest deferred span | **48.5 Mb** |`,
`⚠ **These are Seth's estimates, not measurements.**`, `a ~10.5%`.

⚠ **Two of Seth's four `estimate_markers` are DEAD**: the literal `ESTIMATE`
(uppercase) does NOT occur, and `~29` does NOT occur (the text reads `29 / 276`).
`estimate` matches only via the word "estimates" and would false-positive on
innocent prose such as "estimated from Stage B".
Confirm: `grep -n "ESTIMATE" .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`
and `grep -n "10.5%" .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`

**M9 — `n_total = 276`.** `awk -F'\t' 'NR>1 && $7=="AFR"' config/ld_regions.tsv |
wc -l` = 276. Correct today; make it a REQUIRED argument anyway so it can never go
silently stale.

**M10 — The `260817-vbu` card block boundaries.** `section_card` extracts
`AGENT-PROMPT` between `^STEP 6b` and `^STEP 7`; `BROWSER-PASTE` between `^## 6b`
and `^## 7`; `READY-TO-FIRE` between `^## 6b` and `^## 7[.]`. **All wiring in this
task lands OUTSIDE those ranges** (AGENT-PROMPT R6 / STEP 8 / STEP 9 / STEP 10;
BROWSER-PASTE Stage A/B/C blocks; READY-TO-FIRE items 9/10). Nothing may be
inserted between `STEP 6b` and `STEP 7`.

**M11 — `source_freeze` pin scope.** `tests/m3/test_source_freeze_pins.py`
`PY_FROZEN_RELS` gates only files MEASURED 0-diff against `PY_CODE_REF = bf16289`,
and its own comment states that adding a file there "requires a RECORDED DECISION
that it is frozen, not an inference". A brand-new module cannot exist at
`bf16289`, so adding `fire_verifier.py` would be a category error and would
re-plant the nuisance-repin timebomb the SR4 rescope removed. **DECISION: do NOT
add `fire_verifier.py` to any freeze registry.** Its enforcer is its own test
module. Record this in the SUMMARY and the courier note.
</planner_measurements>

<adjudications>
The design below is already adjudicated. The executor **verifies** each
adjudication against the shipped code (commands in `<planner_measurements>`) and
then implements it. Any measurement that disagrees is a BLOCKER: stop, report, do
not silently redesign.

**A-01 — NaN falsification: shipped path first, diagnosis second.**
`check_nan_falsification(npz_path, *, verifier=rnlp.content_verify_npz,
nan_scanner=pln._has_any_nan_blocked, ranker=pln.nan_variant_indices,
min_bytes=alp._MIN_REGION_NPZ_BYTES, mode="square")`:
1. missing file -> FAIL closed. size < `min_bytes` -> FAIL closed.
2. call the SHIPPED `verifier` (not a re-implementation). `ok=True` -> PASS, with a
   detail stating that the shipped pre-upload verification re-read the banked
   `.npz` and that `ok` therefore entails NaN-free (this implication is PINNED by
   fixture tests, not asserted by argument).
3. `ok=False` -> load the array ONCE MORE and run the FROZEN `nan_scanner`. NaN
   present -> HARD_STOP naming NaN and the ranked source rows, with the verbatim
   sentence *"occlusion is NOT the sole NaN mechanism"*. NaN absent -> HARD_STOP
   carrying the shipped `reason` verbatim and explicitly NOT claiming NaN.
4. any exception -> FAIL closed (`_guard`), and the detail must not claim NaN.

This is memory-bounded: at most one ~42 GB array is live at a time, and the second
load happens only on the already-failing path.

**A-02 — `classify_deferrals` -> `classify_statuses`, PREFIX matching.**
Allow-list, derived from M2:
- ok-class (exact): `ok`, `skipped_idempotent`
- deferral prefixes (recognized, PASS, counted — the gates working):
  `deferred_infeasible_square`, `deferred_occlusion_anomaly`
- failure class: `verify_failed`, `error` (exact) and `error:` (prefix)

Dispositions: ok-class -> PASS. deferral-class -> PASS (never "fix" mid-fire).
failure-class -> **FAIL at FINDING** (a region that banked nothing is not the gates
working; Stage C runs without `--fail-fast` so the loop legitimately continues —
the correct response is report-to-Carter, not auto-abort). Anything else, and any
empty status -> **FAIL at HARD_STOP**.

**A-03 — the allow-list gets a NAMED drift enforcer.** A test walks the SHIPPED
`run_native_ld_panel.py` with `ast` and extracts the constant prefix of every value
assigned to `result["status"]` or written as a `"status":` dict entry, handling
`Constant`, `JoinedStr` (take the leading `Constant` part) and `IfExp` (both
branches). It asserts (a) the extracted set is NON-EMPTY (non-vacuity — an
extractor that finds nothing would pass trivially), and (b) every extracted prefix
is covered by the allow-list. A shipped status added tomorrow makes this red.

**A-04 — `check_region1_not_deferred` -> `check_region1_status`, widened.** Region
1 runs under `--fail-fast`, where `RegionGateError` fires on ANY `status != 'ok'`
(`run_native_ld_panel.py:1161`). Anything other than exactly `ok` is the finding,
not just a `deferred` prefix. Severity stays **FINDING** per Seth's own judgment
call and the runbook's own language ("a deferral there would itself be the
finding"). ⚠ Record in the module docstring AND the SUMMARY: flipping to HARD_STOP
is a ONE-CONSTANT change reserved for Carter, and `exit_code` is non-zero either
way, so nothing operational rides on the tier.

**A-05 — `parse_panel_tsv` is the SINGLE TSV parser.** No check does ad-hoc column
indexing. Reads with the stdlib `csv` module (`delimiter="\t"`), asserts the header
is EXACTLY the imported `_PANEL_COLUMNS` (refuse, never repair — mirroring the
shipped `append_panel_row` behaviour), refuses ragged rows, and returns
`list[dict]` with `n_var` / `wall_min` / `peak_ram_gib` / `n_dropped_occluded`
coerced to numbers-or-None (empty field -> None) and `status` kept as a raw string.

**A-06 — `check_coverage_disclosure_resolved(path)` takes a FILE, not a string.**
It extracts the `## R4-COVERAGE` block from
`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` (heading regex to
next `^## ` or EOF; an EMPTY or short block is a FAIL, per the `260817-vbu` V0
vacuity lesson). Markers are MEASURED sentinels from M8, deliberately not the bare
word "estimate": `"29 / 276 = 10.5%"`, `"Seth's estimates, not measurements"`,
`"~247 regions"`, `"48.5 Mb"`, `"~10.5%"`. It ALSO requires a `MEASURED:`
provenance line naming the panel-TSV source — so the obligation cannot be
discharged by deleting the warning and shipping nothing.

**A-07 — the disclosure gate SKIPS pre-fire, with three anti-masking guards.** The
pytest that runs A-06 against the LIVE repo file skips while no measured panel TSV
exists in-repo. The skip condition is derived, not invented: glob the repo for the
imported `run_native_ld_panel._DEFAULT_PANEL_NAME`. Guards:
(a) the check FUNCTION's own green + red cases run UNCONDITIONALLY against fixture
text — the function is proven able to fail whether or not the live gate runs;
(b) the finder itself is SHOWN VALID by a test that hands it a tmp tree with and
without the file (a skip-guard hides the bug unless the skipped check is shown
valid);
(c) the skip moves the pinned tests/m3 skip count 31 -> 32 — a visible, recorded
baseline move, registered in the SUMMARY and HANDOFF as the named enforcer of the
R4-COVERAGE obligation.

**A-08 — `check_cost_denominator(n_regions_used, n_bankable, n_total)`: `n_total`
is REQUIRED**, no default. 276 is correct today (M9) but a default is how a count
goes silently stale.

**A-09 — `check_peak_ram(peak_gib, vm_gib=_VM_TOTAL_GIB, headroom_frac=0.15)`**
with `_VM_TOTAL_GIB = 120.0` and a docstring citing M6's file:line. The runbook
passes `--vm-gib 120` explicitly so the number is visible at the call site.

**A-10 — `check_manifest_rows` gains a `region_id` assertion.** The runbook's own
expectation is "6 lines (header + exactly 5 records), region_id m2_region_00001 on
every record row" — the shipped `occlusion_manifest` writer emits a `region_id`
column, so the check must assert it, not just the row count.

**A-11 — no freeze-registry entry.** Per M11.

**A-12 — MAF depression: function + tests now, wiring deferred.** The
(panel_maf, sumstats_maf) pairs come from occlusion manifests joined to harmonized
sumstats — Stage-B-report-side plumbing that does not exist yet. Implement
`check_maf_depression` and its three tests; do NOT build the join. Record the
plumbing as a Stage-B runbook NOTE naming what would have to be produced.
</adjudications>

<cli_contract>
`python3 src/python/fire_verifier.py <subcommand> [args] [--report PATH]`

| subcommand | required args | checks run |
|---|---|---|
| `stage-a` | `--panel-tsv`, `--region-id`, `--manifest`, `--npz` | nan_falsification, manifest_rows, occlusion_ceiling, region1_status, classify_statuses |
| `stage-b` | `--panel-tsv`, `--n-total` | peak_ram (all rows), classify_statuses, cost_denominator |
| `stage-c` | `--panel-tsv` | classify_statuses (+ a by-status rollup in `measured`) |
| `disclosure` | `--file` | coverage_disclosure_resolved |

Optional everywhere: `--report PATH` (writes the `summarize()` dict as JSON),
`--vm-gib` (stage-b, default `_VM_TOTAL_GIB`), `--expected-records` (stage-a,
default 5).

`--npz` is **REQUIRED** for `stage-a`. There is no skip on the fire path: a
falsification that did not run is not a falsification. `stage-a` derives
`n_occluded` (`$8`) and `n_var` (`$3`) for `--region-id` from the parsed panel TSV
— never from a CLI number a human typed.

`summarize()` returns `{all_pass, exit_code, n_checks, hard_stops, findings,
report[]}`; `main()` prints a human-readable block then `sys.exit(exit_code)`.
`Check.status` is `PASS` or `FAIL` only.

EGRESS: the module emits counts, booleans, file sizes, row indices and policy
labels. No genotypes, no LD values, no per-sample data. Safe to run in-perimeter
and paste out.
</cli_contract>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: RED — adjudicate against shipped code, then write the full test surface</name>
  <files>tests/m3/test_fire_verifier.py, .planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-controls-transcript.txt</files>
  <behavior>
Establish the pre-change baseline FIRST, then write tests encoding the adjudicated
contracts. Every check gets a green case AND at least one red case. The suite must
be RED at the end of this task (the module does not exist yet).

Required test families (names indicative; `_RED_` in the name marks a negative
control):

`parse_panel_tsv` — green over a 9-column fixture; RED on a renamed header column;
RED on a missing file; RED on a ragged row; green proving a real
`deferred_infeasible_square: n_var=102421 > ceiling=120000` status survives the tab
split intact (spaces, `=` and `>` inside the field).

vocabulary drift guard (A-03) — the AST extractor over the SHIPPED
`run_native_ld_panel.py` returns a NON-EMPTY prefix set; every extracted prefix is
covered by the allow-list; and a `_RED_` control runs the SAME extractor over a tmp
fixture module containing `result["status"] = "banana"` and asserts the coverage
assertion fails for it (proves the guard is not vacuous).

`classify_statuses` (A-02) — green on the REAL detail-bearing deferral strings from
M2 (the regression pin for the prototype defect); green on `skipped_idempotent`;
`_RED_` on `"banana"`; `_RED_` on `""`; `_RED_` on `"deferred_mystery_reason"`;
`_RED_` on `"verify_failed"` asserting severity == FINDING (not HARD_STOP, not
PASS); `_RED_` on a real `"error: n_var mismatch for m2_region_00001: ..."`
asserting severity == FINDING.

`check_nan_falsification` (A-01) — green on a valid small `.npz` written the way the
shipped converter writes one (`np.savez_compressed` with a float32 symmetric
unit-diagonal `ld`); `_RED_` NaN on the diagonal; `_RED_` whole-row NaN WITH a 1.0
diagonal (the fire-#3 fingerprint) asserting the detail names NaN AND the ranked
source row AND the verbatim "occlusion is NOT the sole NaN mechanism"; `_RED_`
missing file; `_RED_` file below `_MIN_REGION_NPZ_BYTES`; `_RED_` corrupt bytes
asserting the detail does NOT claim NaN; `_RED_` a `verifier` that raises a non-NaN
OSError still FAILS. PLUS a direct implication pin: call the SHIPPED
`content_verify_npz` on both NaN fixtures and assert `ok is False` — the "ok
entails NaN-free" claim must be measured, not argued.

`check_manifest_rows` (A-10) — green on header + 5 records carrying
`m2_region_00001`; `_RED_` wrong line count; `_RED_` `_SUCCESS` placeholder rows at
the right line count; `_RED_` missing file; `_RED_` a record row carrying a
different region_id.

`check_occlusion_ceiling` (M5) — green on region 1's real (5, 102421) with
`ceiling == pytest.approx(51.2105, abs=1e-3)`; `_RED_` on (52, 102421) asserting the
detail says DEFER; boundary (60 @ 120000 PASS / 61 FAIL); and an IDENTITY assertion
that the default frac IS `run_native_ld_panel._OCCLUSION_ANOMALY_FRACTION` (never a
literal).

`check_region1_status` (A-04) — green on `"ok"`; `_RED_` on the real
`deferred_infeasible_square: ...` string asserting severity == FINDING; `_RED_` on
`"verify_failed"` (the widening pin); `_RED_` on `""`.

`check_peak_ram` (A-09) — green 78.2; `_RED_` 110.0; `_RED_` None asserting "FAIL
CLOSED"; and an assertion that `_VM_TOTAL_GIB == 120.0`.

`check_maf_depression` (A-12) — green; `_RED_` no systematic depression asserting
severity == FINDING; `_RED_` empty pairs.

`check_cost_denominator` (A-08) — green used==bankable; `_RED_` used=276 /
bankable=247 asserting "understates"; `_RED_` used != bankable; and a
`pytest.raises(TypeError)` proving `n_total` has NO default.

`check_coverage_disclosure_resolved` (A-06/A-07) — UNCONDITIONAL fixture cases:
`_RED_` on a fixture reproducing the current R4 text (asserting the detail names the
sentinel it found); green on a fixture with measured numbers AND a `MEASURED:`
provenance line; `_RED_` empty file; `_RED_` missing file; `_RED_` sentinels removed
but no `MEASURED:` line; and a FALSE-POSITIVE guard proving innocent prose
containing the word "estimated" does NOT trip the check. PLUS the live gate: a test
that SKIPs when the repo contains no `_DEFAULT_PANEL_NAME` artifact (skip reason
must name the exact filename), and a test that the finder returns `[]` on a tmp tree
without the file and a path on a tmp tree with it (the skip condition SHOWN VALID).
PLUS an identity assertion that the filename is imported from the producer.

`summarize` / CLI — all-pass -> exit_code 0; any FAIL -> exit_code 1 with the name in
the correct bucket; HARD_STOP and FINDING bucketed separately; `--report` JSON
round-trips through `json.load` and contains every check name; `stage-a` without
`--npz` exits as an argparse error.
  </behavior>
  <action>
1. **Baseline first.** Record the pre-change suite state verbatim:
   `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3 -q 2>&1 | tail -5`
   EXPECT `914 passed, 31 skipped` (0 failed). ⚠ Anything else is a BLOCKER — stop
   and report before writing a line of code. Then
   `git status --short tests/m3/sparse_parent_benchmark.tsv` and, if dirty,
   `git checkout -- tests/m3/sparse_parent_benchmark.tsv`.
2. **Re-confirm M1-M11** with the commands in `<planner_measurements>`. Record each
   confirmation (or discrepancy) in a scratch note for the SUMMARY. A discrepancy on
   M2, M3 or M5 is a BLOCKER.
3. Write `tests/m3/test_fire_verifier.py` following the conventions of
   `tests/m3/test_run_native_ld_panel.py` (module docstring explaining what runs
   where; `PROJECT_ROOT = Path(__file__).resolve().parents[2]`; `src/python` on
   `sys.path`; `import fire_verifier as fv`). Import the shipped modules for the
   identity assertions (`import run_native_ld_panel as rnlp`,
   `import plink_ld_to_npz as pln`, `import aou_ld_panel as alp`).
4. Use `tmp_path` for all fixtures. Keep every `.npz` fixture SMALL (n <= 64) — the
   memory discipline is enforced by construction (imported blocked helpers), never by
   allocating a real 42 GB matrix in a test.
5. Run the new file and OBSERVE RED:
   `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_fire_verifier.py -q 2>&1 | tail -20`
   Expect a collection error (`ModuleNotFoundError: fire_verifier`). Capture the
   verbatim output as the first entry of `260818-sml-controls-transcript.txt`.
6. Commit with explicit paths:
   `git add tests/m3/test_fire_verifier.py .planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-controls-transcript.txt`
   then
   `git commit -m "test(quick-260818-sml): RED — fire-stage mechanical gate contracts, adjudicated against shipped code"`.
   On a GPFS `invalid object ... Error building trees` failure, run the guarded
   `git hash-object -w` recovery loop over `git ls-files -s` (rewrite ONLY when the
   working-tree file hashes to the wanted sha) and retry once.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_fire_verifier.py -q 2>&1 | tail -20</automated>
  </verify>
  <done>
Baseline recorded as 914 passed / 31 skipped / 0 failed. M1-M11 re-confirmed (or a
discrepancy escalated as a blocker). `tests/m3/test_fire_verifier.py` exists covering
every family above with at least one `_RED_` control per check. The run is RED with
the verbatim output banked in the controls transcript. One `test(quick-260818-sml)`
commit landed; `sparse_parent_benchmark.tsv` is not staged.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: GREEN — implement src/python/fire_verifier.py and drive every control red</name>
  <files>src/python/fire_verifier.py, .planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-controls-transcript.txt</files>
  <behavior>
The module makes Task 1's tests green WITHOUT weakening any of them. Structure:
`Check` dataclass + `_guard` fail-closed wrapper (keep Seth's shape — it is sound
and his three design rules are correct), then the checks per `<adjudications>`,
then `parse_panel_tsv`, `summarize`, and `main()` implementing `<cli_contract>`.

Module docstring must state: the three design rules (fail closed / measure the data
layer never a marker / every check proven able to fail); the EGRESS class; the A-04
severity note (the region-1 tier is a one-constant change reserved for Carter, and
`exit_code` is non-zero either way); and that it never makes the go/no-go decision.
  </behavior>
  <action>
1. Write `src/python/fire_verifier.py`. Bootstrap `src/python` onto `sys.path`
   exactly as `run_native_ld_panel.py:90-94` does, then
   `import run_native_ld_panel as rnlp`, `import plink_ld_to_npz as pln`,
   `import aou_ld_panel as alp`. **Every constant comes from those imports** (M1, M5,
   M7, and `_DEFAULT_PANEL_NAME`); the only literals allowed are
   `_VM_TOTAL_GIB = 120.0` (docstring-cited to M6) and `headroom_frac = 0.15`.
2. Implement the checks exactly as adjudicated. `check_nan_falsification` follows
   A-01's four-step order — shipped verifier first, one extra load ONLY on the failing
   path, frozen blocked scanner for the diagnosis. A non-NaN failure must never be
   reported as a NaN finding.
3. Implement `main()` per `<cli_contract>`; `--report` writes the `summarize()` dict
   via `json.dump(..., indent=2)`; the human-readable block prints one line per check
   as `{status}  {severity}  {name}: {detail}` followed by the hard_stops / findings
   lists.
4. Run the module's tests to GREEN:
   `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_fire_verifier.py -q`
5. **Drive every negative control red on the SHIPPED code** (never a
   re-implementation): for each `_RED_` test, perturb the shipped check just enough to
   make that control fail, capture the verbatim red, revert, and re-confirm green.
   ⚠ `importlib` validates cached bytecode on `(mtime_seconds, size)` — a
   byte-length-identical edit reverted within the same second runs STALE bytecode.
   Either change the byte length, or
   `find . -name '__pycache__' -prune -exec rm -rf {} +` between perturbation and
   revert, and prove the revert took by re-running the control and seeing it GREEN
   again. Append every verbatim red to `260818-sml-controls-transcript.txt` with its
   control name. (If perturbing all controls individually is impractical, group them:
   one perturbation per CHECK that fires all of that check's controls at once, and say
   so explicitly in the transcript — but no check may be trusted without at least one
   observed red of its own.)
6. Run the FULL suite and record the baseline move verbatim:
   `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3 -q 2>&1 | tail -5`
   Required invariants: **0 failed**, **skips exactly 32** (31 + the A-07 disclosure
   gate), **passed strictly greater than 914**. Record the exact triple — do NOT
   pre-commit to a predicted pass count. ⚠ Any OTHER movement (a previously-passing
   test now failing or skipping) is a BLOCKER, not a note. Then
   `git checkout -- tests/m3/sparse_parent_benchmark.tsv` if dirtied.
7. Sanity-run the CLI against synthetic fixtures in the session scratchpad to prove
   the exit codes and the JSON report
   (`python3 src/python/fire_verifier.py stage-c --panel-tsv <fixture> --report <tmp>.json; echo $?`).
   This is a local smoke, not a fire action.
8. Commit with explicit paths:
   `git add src/python/fire_verifier.py .planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-controls-transcript.txt`
   then
   `git commit -m "feat(quick-260818-sml): fire-stage mechanical gates — fail-closed verifier wired to the shipped producer/converter contracts"`.
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3 -q 2>&1 | tail -5</automated>
  </verify>
  <done>
`src/python/fire_verifier.py` exists, imports every shipped constant (no `0.0005`,
no `120000`, no re-declared `256`, no forked frozen helper), and
`tests/m3/test_fire_verifier.py` is fully green. Every check has at least one
OBSERVED red banked verbatim in the controls transcript with its control name. Full
`tests/m3` is 0 failed / 32 skipped / >914 passed, exact triple recorded, no other
baseline movement. CLI exit codes and JSON report smoke-verified locally. One
`feat(quick-260818-sml)` commit landed.
  </done>
</task>

<task type="auto">
  <name>Task 3: Wire the gates into the fire runbook, courier the adjudication, close out</name>
  <files>.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md, .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md, .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md, .planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-COURIER-TO-SETH-adjudication.md, .planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-SUMMARY.md, .planning/STATE.md</files>
  <action>
1. **Before-shot.** Run
   `bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all > /tmp/vbu-before.txt 2>&1; echo $?`
   and keep the output. It must be exit 0.
2. **AGENT-PROMPT wiring** (all edits OUTSIDE `STEP 6b`..`STEP 7` — see M10):
   - **R6** (line ~32): extend the allowed-file list with
     `/home/jupyter/fire_gate_stageA.json`, `/home/jupyter/fire_gate_stageB.json`,
     `/home/jupyter/fire_gate_stageC_<date>.json`, and the gate's working copies
     under `/home/jupyter/native_ld_scratch/` (the panel-TSV snapshot, the per-region
     manifest copy, and the downloaded region-1 `.npz`). Add the one narrow deletion
     exception: *"you may delete ONLY the `.npz` copy you yourself downloaded into
     `native_ld_scratch/`, to reclaim the tens of GB — nothing else, and never
     anything in the bucket."*
   - **New hard rule R8**: *"Every GATE below now has a MECHANICAL gate. Run it, paste
     its full output to Carter, and NEVER chain past a red — a red is a STOP under
     R1/R3 regardless of how the raw numbers look. The gate makes the evidence
     mechanical; it never makes the decision."*
   - **STEP 8 (Stage A)**, appended after the existing manifest-check block: the
     download + gate sequence, with `git pull` first: `gsutil du -h <region-1 .npz>`
     and `df -h /home/jupyter` (proceed only if free space is comfortably above the
     object size); `gsutil cp` the `.npz`, the per-region occlusion manifest and the
     panel TSV into `/home/jupyter/native_ld_scratch/`; then
     `python3 src/python/fire_verifier.py stage-a --panel-tsv ... --region-id
     m2_region_00001 --manifest ... --npz ... --report
     /home/jupyter/fire_gate_stageA.json; echo "gate exit: $?"`; then the local `rm`
     of the downloaded `.npz`. EXPECT lines must state that the re-read loads a
     ~42 GB dense float32 array and can take many minutes — **that is not a hang** —
     and that exit 0 is required to proceed.
   - **STEP 9 (Stage B)**: after the existing rollup, snapshot the panel TSV and run
     `fire_verifier.py stage-b --panel-tsv ... --vm-gib 120 --n-total 276 --report
     /home/jupyter/fire_gate_stageB.json`. Add the A-12 note: the MAF-depression
     direction check is IMPLEMENTED but NOT WIRED — it needs
     (panel_maf, sumstats_maf) pairs from the occlusion manifests joined to the
     harmonized sumstats, which is Carter's planning-side work, not the agent's.
   - **STEP 10 (Stage C)**: add one line to the every-2-3-days check-in loop —
     snapshot the panel TSV and run
     `fire_verifier.py stage-c --panel-tsv ... --report /home/jupyter/fire_gate_stageC_$(date +%Y%m%d).json`,
     paste the output, never chain past a red. State explicitly that `deferred_*` rows
     PASS (the gates working), `verify_failed` / `error:` rows are FINDINGS to report,
     and an UNRECOGNIZED status is a HARD_STOP.
3. **BROWSER-PASTE**: mirror the same three invocations into its Stage A / Stage B /
   Stage C blocks (edits outside `## 6b`..`## 7`). Same commands, same expectations.
4. **READY-TO-FIRE**: add one pointer line each to item 9 (STEP A) and item 10
   (STEP B) naming `src/python/fire_verifier.py` as the mechanical gate for that stage
   and its exit-0 requirement (edits outside `## 6b`..`## 7.`).
5. **After-shot.** Re-run
   `bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all > /tmp/vbu-after.txt 2>&1; echo $?`
   — MUST still be exit 0, and `diff /tmp/vbu-before.txt /tmp/vbu-after.txt` must be
   empty. If not, ATTRIBUTE every line of the diff in the SUMMARY or revert. The
   `260814-guk-verify.sh fire` section red stays as documented and is NOT a defect.
6. **Courier note** — `260818-sml-COURIER-TO-SETH-adjudication.md`. Open by confirming
   his 29/29 (18 negative controls) reproduced firsthand as received, and that we took
   the checks not the file. Then one section per adjudication, each with shipped
   file:line evidence:
   - **D-01** reader identity (M3): `read_square_bin` reads the pre-`.npz` `.ld.bin`,
     deleted on success in gs:// mode; the banked artifact is the `.npz` and the
     shipped re-read is `content_verify_npz`, which RETURNS `(ok, reason)` rather than
     raising and detects NaN only indirectly — reporting it as an asymmetry, the very
     misattribution the frozen reader's own comment warns about. Our gate calls the
     shipped verifier and, only on a red, re-loads once to DIAGNOSE with the frozen
     blocked scanner. The "ok entails NaN-free" implication is pinned by fixture
     tests, not argued.
   - **D-02** `classify_deferrals` is DEFEATED by the shipped code: statuses carry
     detail suffixes, so his exact-membership test flags EVERY REAL deferral as
     unrecognized and would HARD_STOP on the gates working at every check-in.
     Separately, his own hole is worse than "banana": `skipped_idempotent` is a REAL
     shipped status (every resumed region) and passes silently. Ours prefix-matches
     the measured vocabulary and has an AST drift enforcer.
   - **D-03** the measured 7-site vocabulary (the M2 table).
   - **D-04** `verify_failed` / `error:` rows pass under his classifier; ours fail them
     at FINDING, with the reasoning (a region that banked nothing is not the gates
     working; Stage C runs without `--fail-fast`).
   - **D-05** `check_region1_not_deferred` widened to `check_region1_status` because
     `--fail-fast` raises on ANY non-`ok` status.
   - **D-06** his `min_bytes=256` coincides exactly with the shipped
     `_MIN_REGION_NPZ_BYTES` MED-6 floor; we now import it.
   - **D-07** his `frac=0.0005` and strict `>` match the shipped clause-(d) gate
     exactly, including the float ceiling and his 60/61 @ 120,000 boundary; we import
     the constant rather than re-declare it.
   - **D-08** `vm_gib=120` CONFIRMED from `m3-producer-unbounded-dense-read.md:17`.
   - **D-09** two of his four `estimate_markers` are DEAD against the real disclosure
     text (`ESTIMATE` uppercase and `~29` do not occur), and `estimate` would
     false-positive on innocent prose; replaced with measured sentinels plus a required
     `MEASURED:` provenance line so the obligation cannot be discharged by deletion.
   - **D-10** `n_total=276` made a required argument (correct today; a default is how a
     count goes stale).
   - **D-11** region-1 severity kept FINDING per his judgment call and the runbook's own
     wording; flipping it is a one-constant change reserved for Carter, and `exit_code`
     is non-zero either way.
   - **D-12** we did NOT add the module to `test_source_freeze_pins.py`: that registry
     gates only files measured 0-diff against `PY_CODE_REF = bf16289`, and a new module
     cannot exist at that ref — adding it would re-plant the nuisance-repin timebomb the
     SR4 rescope removed. The module's enforcer is its own test file.
   - **D-13** the R4-COVERAGE gate SKIPS pre-fire (no measured panel TSV in-repo yet)
     with three anti-masking guards, and the skip moves the pinned suite skip count
     31 -> 32 so the deferral is visible in the baseline rather than silent.
   Close with the open items: the MAF-depression pairs are not yet derivable (A-12), and
   we ask whether he wants the region-1 tier flipped.
7. **SUMMARY + STATE.** Write `260818-sml-SUMMARY.md` (exact pre/post suite triples, the
   adjudication list, the controls-transcript pointer, the D-12 no-freeze-entry decision,
   the A-04 one-constant note, and the A-07 obligation-enforcer registration). Add the
   STATE.md quick-task row and refresh the "Stopped at" block per
   `[[feedback_state_md_keep_current]]` — atomic with this commit, not deferred.
8. Commit with explicit paths only:
   `git add .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-BROWSER-PASTE.md .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md .planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-COURIER-TO-SETH-adjudication.md .planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-SUMMARY.md .planning/STATE.md`
   then
   `git commit -m "docs(quick-260818-sml): wire the mechanical gates into the fire runbook + courier the shipped-code-wins adjudication to Seth"`.
  </action>
  <verify>
    <automated>bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all > /tmp/vbu-after.txt 2>&1; echo "vbu exit: $?"; diff /tmp/vbu-before.txt /tmp/vbu-after.txt && echo "VBU DIFF EMPTY"; grep -c "fire_verifier.py" .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md</automated>
  </verify>
  <done>
All three `260812-ox1` runbooks carry the gate invocations for their stage; the
AGENT-PROMPT R6 list covers every file the gate makes and the one narrow local-`rm`
exception; new hard rule R8 forbids chaining past a red. `260817-vbu-verify.sh all`
exits 0 with an EMPTY before/after diff (or every diff line is attributed). Nothing
was inserted between `STEP 6b` and `STEP 7` (or the `## 6b`..`## 7` equivalents).
The courier note carries D-01..D-13 with shipped file:line evidence. SUMMARY records
the exact pre/post suite triples. STATE.md refreshed atomically. One
`docs(quick-260818-sml)` commit landed.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| AoU bucket -> VM local disk | `gsutil cp` of a banked `.npz` / manifest / panel TSV the gate then parses. Untrusted-shaped (a truncated or partially-written object is possible). |
| VM -> Carter (chat paste) | Gate stdout + JSON report leave the perimeter as text. Must carry no genotypes, no LD values, no per-sample data. |
| Repo docs -> gate | The R4 disclosure file is parsed by the gate; a renamed heading yields an empty block. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-sml-01 | Information disclosure | gate stdout / `--report` JSON pasted out of the perimeter | mitigate | Checks emit only counts, booleans, byte sizes, row indices and policy labels. `nan_variant_indices` returns ROW INDICES, never LD values. Stated in the module docstring and asserted by a test that the report JSON contains no float array. |
| T-sml-02 | Tampering | a partially-downloaded or truncated `.npz` read as if whole | mitigate | `min_bytes` floor imported from `aou_ld_panel._MIN_REGION_NPZ_BYTES`, plus the shipped `content_verify_npz` which fails closed on an unreadable/truncated file. |
| T-sml-03 | Spoofing | a `_SUCCESS`-style marker file standing in for real manifest records | mitigate | `check_manifest_rows` asserts multi-field parseability AND the `region_id` value on every record row, not just the line count (the exact defect class that cost $2,140). |
| T-sml-04 | Elevation of privilege | the browser agent taking a gate red as licence to retry/repair | mitigate | New hard rule R8 in AGENT-PROMPT: a red is a STOP under R1/R3; the agent pastes and waits. R6 authorizes exactly one new local deletion (the `.npz` copy it downloaded) and nothing in the bucket. |
| T-sml-05 | Denial of service | the ~42 GB re-read OOMs or fills the VM disk mid-fire | mitigate | Frozen blocked helpers only; at most one full array live; the runbook checks `gsutil du -h` + `df -h` BEFORE the download and deletes the copy after. |
| T-sml-06 | Repudiation | a green that was never observed red | mitigate | Every control driven red on the SHIPPED code with verbatim output banked in `260818-sml-controls-transcript.txt`; bytecode-cache trap called out explicitly. |
| T-sml-07 | Tampering | a renamed heading silently empties the disclosure block, making the gate vacuously green | mitigate | Empty/short extracted block is a FAIL (the `260817-vbu` V0 vacuity lesson), with its own negative control. |
| T-sml-08 | Information disclosure | the fire runbook itself | accept | The runbook already carries the bucket URI and workspace ids; this task adds no new secret and the files are already in-repo. |
</threat_model>

<verification>
1. `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3 -q` — 0 failed,
   32 skipped, passed > 914; no movement other than the new tests.
2. `bash .planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-verify.sh all`
   — exit 0, before/after diff empty.
3. `grep -n "0\.0005\|120000\|= 256" src/python/fire_verifier.py` — no hardcoded
   shipped constant (the only expected literals are `120.0` and `0.15`).
4. `git diff --numstat HEAD~3 HEAD -- src/python/plink_ld_to_npz.py src/python/occlusion_span_filter.py src/python/condition_ld_matrix.py src/python/run_native_ld_panel.py`
   — EMPTY. Nothing frozen or fire-path-producer was touched.
5. `git status --short` — `tests/m3/sparse_parent_benchmark.tsv` not staged or modified.
6. `awk '/^STEP 6b/{p=1} /^STEP 7/{p=0} p' .planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-AGENT-PROMPT.md | grep -c fire_verifier`
   — 0 (nothing inserted inside the pinned card block).
7. The controls transcript names every check and carries at least one verbatim red
   per check.
</verification>

<success_criteria>
- `python3 src/python/fire_verifier.py stage-c --panel-tsv <fixture>` exits 1 on a
  red row and 0 on a clean rollup, proven locally.
- A real `deferred_infeasible_square: n_var=... > ceiling=...` row classifies as
  RECOGNIZED (this is the single most consequential adjudication: the prototype
  would have HARD_STOPped the fire on the gates working).
- Adding a new status to the shipped producer makes `tests/m3/test_fire_verifier.py`
  red (drift enforcer, shown non-vacuous).
- `tests/m3`: 0 failed, 32 skipped, > 914 passed; exact triple recorded in the SUMMARY.
- `260817-vbu-verify.sh all` still exits 0.
- Seth has a courier note listing D-01..D-13 with shipped file:line evidence for each.
- Zero perimeter contact, $0, nothing fired.
</success_criteria>

<output>
After completion, create
`.planning/quick/260818-sml-adopt-seth-fire-stage-mechanical-gates-u/260818-sml-SUMMARY.md`.
</output>
