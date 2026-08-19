---
phase: quick-260818-sml
plan: 01
subsystem: m3-aou-afr-ld-panel-build / fire-stage gating
tags: [fire-gate, tdd, negative-controls, adjudication, r4-coverage, egress-safe]
requires:
  - src/python/run_native_ld_panel.py (producer contracts; NOT modified)
  - src/python/plink_ld_to_npz.py (FROZEN blocked NaN helpers; imported, not forked)
  - src/python/aou_ld_panel.py (_MIN_REGION_NPZ_BYTES MED-6 floor)
provides:
  - src/python/fire_verifier.py (Stage-A/B/C + disclosure mechanical gates, CLI)
  - tests/m3/test_fire_verifier.py (78 tests; a _RED_ control for every check)
  - AGENT-PROMPT hard rule R8 (never chain past a red)
  - a NAMED enforcer for the R4-COVERAGE disclosure obligation
affects:
  - .planning/quick/260812-ox1-.../260812-ox1-{AGENT-PROMPT,BROWSER-PASTE,READY-TO-FIRE}.md
tech-stack:
  added: []
  patterns: [fail-closed-gates, prefix-status-matching, ast-drift-enforcer, observed-red-controls]
key-files:
  created:
    - src/python/fire_verifier.py
    - tests/m3/test_fire_verifier.py
    - .planning/quick/260818-sml-.../260818-sml-COURIER-TO-SETH-adjudication.md
    - .planning/quick/260818-sml-.../260818-sml-controls-transcript.txt
  modified:
    - .planning/quick/260812-ox1-.../260812-ox1-AGENT-PROMPT.md
    - .planning/quick/260812-ox1-.../260812-ox1-BROWSER-PASTE.md
    - .planning/quick/260812-ox1-.../260812-ox1-READY-TO-FIRE.md
decisions:
  - DEC-2026-08-18-sml-no-freeze-registry-entry (D-12)
  - DEC-2026-08-18-sml-region1-severity-stays-FINDING (A-04 / D-11)
  - DEC-2026-08-18-sml-prefix-status-matching (A-02 / D-02)
metrics:
  tasks: 3
  commits: 3
  tests_pre: "914 passed, 31 skipped, 0 failed (783.22s)"
  tests_post: "992 passed, 32 skipped, 0 failed (795.87s)"
  negative_controls_observed_red: 22
  completed: 2026-08-18
---

# quick-260818-sml: Adopt Seth's fire-stage checks as SHIPPED mechanical gates — Summary

Seth's pre-fire checklist prototype is now a shipped, TDD-pinned, fail-closed gate
module (`src/python/fire_verifier.py`) wired into all three `260812-ox1` fire
runbooks under a new hard rule R8 — with every check re-adjudicated BY MEASUREMENT
against the shipped producer/converter, thirteen disagreements resolved in the
shipped code's favour, and all 22 negative controls driven red against the shipped
module with verbatim output banked in-repo.

**The single most consequential finding:** Seth's `classify_deferrals` used
exact-membership matching, but the shipped producer emits statuses with detail
suffixes (`deferred_infeasible_square: n_var=181004 > ceiling=120000`). As
written, his check would have HARD_STOPped a healthy $385–1,084 fire **on the
gates working**, at every Stage-C check-in, for every one of the expected ~29+
deferrals. Ours prefix-matches the MEASURED vocabulary and has an AST drift
enforcer.

## What shipped

| Artifact | Lines | What it is |
|---|---|---|
| `src/python/fire_verifier.py` | 1,014 | `Check` + `_guard` fail-closed wrapper, 8 checks, `parse_panel_tsv`, `classify_statuses`, `summarize`, argparse CLI (`stage-a` / `stage-b` / `stage-c` / `disclosure`) |
| `tests/m3/test_fire_verifier.py` | 923 | 78 tests + 1 skip; a green AND at least one `_RED_` control per check; the AST vocabulary drift guard; the live R4 disclosure gate |
| `260818-sml-COURIER-TO-SETH-adjudication.md` | 436 | D-01…D-13, each with shipped `file:line` evidence |
| `260818-sml-controls-transcript.txt` | 1,716 | 22 perturbations, verbatim red + proven revert, plus the CLI smoke and the baseline-move reconciliation |

CLI, runnable on the VM after `git pull`:

```
python3 src/python/fire_verifier.py stage-a --panel-tsv … --region-id … --manifest … --npz … --report …
python3 src/python/fire_verifier.py stage-b --panel-tsv … --vm-gib 120 --n-total 276 --report …
python3 src/python/fire_verifier.py stage-c --panel-tsv … --report …
python3 src/python/fire_verifier.py disclosure --file …
```

## Suite triples — EXACT, and reconciled by component

```
PRE   914 passed, 31 skipped, 4 warnings in 783.22s (0:13:03)   [0 failed]
POST  992 passed, 32 skipped, 4 warnings in 795.87s (0:13:15)   [0 failed]
```

| | pre | post | delta | attribution |
|---|---|---|---|---|
| passed | 914 | 992 | **+78** | exactly the 78 passing tests in `test_fire_verifier.py` (it reports `78 passed, 1 skipped` in isolation) |
| skipped | 31 | 32 | **+1** | exactly `test_coverage_disclosure_live_gate_against_the_repo_file` (the A-07 R4-COVERAGE enforcer) |
| failed | 0 | 0 | 0 | — |

**Nothing else moved.** No previously-passing test began failing or skipping.
The plan's required invariants (0 failed / skips exactly 32 / passed strictly >
914) are all met, and the deltas were checked as COMPONENTS rather than trusting
the aggregate line.

## M1–M11 re-confirmation (all measured against the working tree)

| ID | Claim | Verdict |
|---|---|---|
| M1 | `_PANEL_COLUMNS` = 9 cols, `n_dropped_occluded` 8th | **CONFIRMED** (`run_native_ld_panel.py:101-121`) |
| M2 | 7 status emission sites, statuses carry detail suffixes | **CONFIRMED** (`:774, :785, :831, :854, :991 (IfExp → 2), :1028`) |
| M3 | `read_square_bin` reads the pre-`.npz` `.ld.bin`; `content_verify_npz` returns `(ok, reason)` and misreports NaN as an asymmetry | **CONFIRMED** (`:343-383`, `:351`; scratch reclaim at `:1037`) |
| M4 | Frozen blocked helpers exist | **CONFIRMED** (`plink_ld_to_npz.py:136, :151, :163, :182`) |
| M5 | `_OCCLUSION_ANOMALY_FRACTION = 0.0005` module global, STRICT `>` | **CONFIRMED** (`:133`, comparison at `:853`); `_DEFAULT_MAX_N_VAR` at `:143` |
| M6 | VM = n1-standard-32, 120 GB | **CONFIRMED** (`.planning/debug/m3-producer-unbounded-dense-read.md:17`) |
| M7 | `_MIN_REGION_NPZ_BYTES = 256` | **CONFIRMED** (`aou_ld_panel.py:418`) |
| M8 | Two of Seth's four estimate markers are DEAD | **CONFIRMED** — `grep ESTIMATE` rc=1; text reads `29 / 276`, never `~29` |
| M9 | `n_total = 276` | **CONFIRMED** (`awk … $7=="AFR" … \| wc -l` = 276) |
| M10 | Card-block boundaries | **CONFIRMED** — all wiring landed OUTSIDE; guards return 0 for all three files |
| M11 | `PY_CODE_REF = bf16289`; adding a file needs a recorded decision | **CONFIRMED** (`test_source_freeze_pins.py:52, :81-83`) |

No discrepancies. Nothing escalated as a blocker.

## Adjudications implemented (A-01…A-12 → D-01…D-13)

- **A-01 / D-01** — NaN falsification calls the SHIPPED `content_verify_npz` first
  and re-loads ONCE, only on the failing path, to diagnose with the FROZEN blocked
  scanner. The "ok entails NaN-free" implication is PINNED by
  `test_shipped_verifier_rejects_both_nan_fixtures`, not argued. A non-NaN failure
  can never be reported as a NaN finding (asserted: the token `NaN` is absent from
  every non-NaN failure detail).
- **A-02 / D-02, D-04** — `classify_deferrals` → `classify_statuses`, PREFIX
  matching. ok-class and deferral-class PASS; `verify_failed` / `error:` FAIL at
  FINDING; unknown or empty FAIL at HARD_STOP. Also closes Seth's quiet hole:
  `skipped_idempotent` is a REAL shipped status that passed silently under his
  classifier.
- **A-03 / D-03** — AST drift enforcer over the shipped producer, proven
  non-vacuous two ways (non-empty extraction + a fixture producer carrying
  `"banana"`).
- **A-04 / D-05, D-11** — `check_region1_not_deferred` → `check_region1_status`,
  widened to ANY non-`ok` (matching `--fail-fast` at `:1161-1162`). Severity stays
  FINDING.
- **A-05** — `parse_panel_tsv` is the SINGLE parser; refuses a renamed header and
  a ragged row rather than repairing.
- **A-06 / D-09** — disclosure check takes a FILE; measured sentinels replace the
  dead/false-positive-prone markers; requires a `MEASURED:` provenance line; an
  empty or renamed-heading block is a vacuity FAIL.
- **A-07 / D-13** — the live gate SKIPS pre-fire with three anti-masking guards.
- **A-08 / D-10** — `n_total` is REQUIRED (proven by `pytest.raises(TypeError)`).
- **A-09 / D-08** — `_VM_TOTAL_GIB = 120.0`, docstring-cited to M6's file:line.
- **A-10** — `check_manifest_rows` asserts the `region_id` VALUE on every record
  row, not just the line count.
- **A-11 / D-12** — no freeze-registry entry (see Decisions).
- **A-12** — `check_maf_depression` implemented + tested, deliberately NOT wired;
  recorded as an explicit "do not improvise this" note in the Stage-B runbook.

## Decisions recorded

**DEC-2026-08-18-sml-no-freeze-registry-entry (D-12).** `fire_verifier.py` is NOT
added to `tests/m3/test_source_freeze_pins.py`. That registry gates only files
MEASURED 0-diff against `PY_CODE_REF = bf16289`, and its own comment requires a
recorded decision rather than an inference. A module created today cannot exist at
that ref, so adding it would be a category error and would re-plant the
nuisance-repin timebomb the SR4 rescope removed. **Its enforcer is its own test
module** — 78 tests, every check with at least one observed-red control, which is
a strictly stronger and refactor-durable pin than a whole-file SHA
(`[[feedback_a_fixed_sha_whole_file_pin_is_a_timebomb]]`).

**DEC-2026-08-18-sml-region1-severity-stays-FINDING (A-04 / D-11).** Region-1
failure is a FINDING, not a HARD_STOP, per Seth's judgment call and the runbook's
own wording. ⚠ Flipping it is a **ONE-CONSTANT change** — `_REGION1_SEVERITY` in
`src/python/fire_verifier.py` — and is **reserved for Carter**. `exit_code` is
non-zero either way, so nothing operational rides on the tier; only the human's
reading of it.

**DEC-2026-08-18-sml-prefix-status-matching (A-02 / D-02).** Status recognition is
PREFIX-based against the measured 7-site vocabulary, never exact membership.

## R4-COVERAGE obligation — now has a NAMED enforcer

Registered: `tests/m3/test_fire_verifier.py::test_coverage_disclosure_live_gate_against_the_repo_file`.

It SKIPS today (skip reason names `m3-W2-native-plink-panel.tsv` explicitly) and
goes RED the moment a measured panel TSV lands in-repo. **That skip is the +1 in
the 31 → 32 baseline move** — the deferral is visible in the suite counts rather
than silent. The check function itself is red today when run directly
(`fire_verifier.py disclosure --file …` → exit 1, all five sentinels found), and
its green/red fixture cases run unconditionally regardless of the skip. The finder
that drives the skip is itself shown valid on a tmp tree with and without the
artifact — and was driven red (NC-12), which also proved the live gate stops
skipping and goes red as designed.

Pointer added to `260812-ox1-READY-TO-FIRE.md` item 10's post-fire disclosure
paragraph.

## Negative controls — 22, all OBSERVED red on the SHIPPED module

`260818-sml-controls-transcript.txt`. Method: perturb the shipped module → clear
`__pycache__` → run the selection and capture verbatim → restore byte-exact →
clear cache → re-run and PROVE the revert took (every one came back green). The
`(mtime_seconds, size)` bytecode-cache trap was handled explicitly.

| ID | Check | Observed |
|---|---|---|
| NC-00 | the module does not exist (TDD RED) | `ModuleNotFoundError: No module named 'fire_verifier'` |
| NC-01 | `parse_panel_tsv` refusals | 3 failed |
| NC-02 | `_status_class` + AST drift enforcer | 9 failed |
| NC-03 | `classify_statuses` failure tier | 2 failed |
| NC-04a | shipped `ok=False` verdict is load-bearing | 3 failed |
| NC-04b | NaN check fail-closed preconditions | 6 failed |
| NC-05 | `check_manifest_rows` | 4 failed |
| NC-06 | clause-(d) STRICT `>` | 3 failed |
| NC-07 | `check_region1_status` widening | 3 failed |
| NC-08 | `check_peak_ram` | 3 failed |
| NC-09 | `check_maf_depression` | 2 failed |
| NC-10 | `check_cost_denominator` + required `n_total` | 3 failed |
| NC-11 | disclosure sentinels / vacuity / provenance | 6 failed |
| NC-12 | the live-gate SKIP CONDITION | 2 failed |
| NC-13 | `summarize` exit code | 6 failed |
| NC-14 | `--npz` required on `stage-a` | 1 failed |
| NC-15 | no hand-transcribed shipped constants | 1 failed |
| NC-16 | shipped-constant accessors are identities | 4 failed |
| NC-16b | the two identity controls NC-16 MISSED | 2 failed |
| NC-17 | `Check.status` is PASS/FAIL only | 1 failed |
| NC-18 | T-sml-01: no float arrays in the report | 1 failed |
| NC-19 | `--report` actually writes | 1 failed |
| NC-20 | the AST extractor is non-vacuous | 2 failed |

⚠ **NC-16b exists because the aggregate lied.** NC-16 reported "5 selected, 4
failed"; reconciling the components found (a) a control that never fired — CPython
returns `"" + s` **unchanged**, so the "copy" I made to break the identity was the
same object — and (b) a test that was never selected, because its name carries
`min_bytes`, not `min_npz_bytes`. Both were re-fired with a provably-different
perturbation. This is `[[feedback_aggregate_agreement_hides_component_errors]]`
applied to the controls transcript itself.

## Runbook wiring (Task 3)

- **AGENT-PROMPT** — R6 extended (the three `fire_gate_stage*.json` reports, the
  gate's `native_ld_scratch/` working copies, and the ONE narrow deletion
  exception: only the `.npz` the agent itself downloaded, never anything in the
  bucket). New **hard rule R8**: run the gate, paste the full output, NEVER chain
  past a red. New **STEP 8-GATE** (`git pull` → `gsutil du -h` + `df -h` BEFORE the
  download → copy the three inputs → `stage-a` → local `rm`), with an explicit
  "the ~42 GB re-read takes many minutes, THAT IS NOT A HANG". New **STEP 9-GATE**
  (`stage-b`, `--vm-gib 120 --n-total 276`) plus the A-12 not-wired note. **STEP
  10** check-in loop gained the `stage-c` invocation with the read-it-this-way
  rules (`deferred_*` PASS, `verify_failed`/`error:` FINDING, unknown HARD_STOP).
- **BROWSER-PASTE** — the same three invocations mirrored into §9 / §9b / §9c.
- **READY-TO-FIRE** — pointer lines on items 9 and 10, plus the R4-COVERAGE named
  enforcer paragraph.

**Pinned-card enforcer, before and after:**

```
bash .planning/quick/260817-vbu-.../260817-vbu-verify.sh all   → exit 0 (before)
bash .planning/quick/260817-vbu-.../260817-vbu-verify.sh all   → exit 0 (after)
diff /tmp/vbu-before.txt /tmp/vbu-after.txt                    → EMPTY
```

Card-block guards (nothing inserted between `STEP 6b`..`STEP 7` / `## 6b`..`## 7`):
**0 / 0 / 0** for AGENT-PROMPT / BROWSER-PASTE / READY-TO-FIRE.

`260814-guk-verify.sh fire` remains red on exactly the SAME 3 checks
(`F3` × 3 files) before and after the edits — the only change is a line-number
shift in AGENT-PROMPT (110 → 125) from lines added above the card. That section
enforces the SUPERSEDED two-body card and its red is documented as EXPECTED, not a
defect. `F10` (the retired "nothing is lost" framing appears 0 times) still PASSES,
so the new prose did not reintroduce it.

## Verification results

| # | Gate | Result |
|---|---|---|
| 1 | `pytest tests/m3 -q` | **992 passed, 32 skipped, 0 failed** ✓ |
| 2 | `260817-vbu-verify.sh all` | **exit 0, before/after diff EMPTY** ✓ |
| 3 | `grep -n "0\.0005\|120000\|= 256" src/python/fire_verifier.py` | **no match (rc=1)** ✓ |
| 4 | `git diff --numstat HEAD~3 HEAD -- <frozen> <producer>` | **EMPTY** ✓ |
| 5 | `git status --short tests/m3/sparse_parent_benchmark.tsv` | **clean, never staged** ✓ |
| 6 | card-block `grep -c fire_verifier` | **0 / 0 / 0** ✓ |
| 7 | controls transcript names every check with ≥1 verbatim red | **22 entries** ✓ |

## Success criteria

- ✅ `stage-c` exits 0 on a clean rollup and 1 on a red row — proven locally.
- ✅ A real `deferred_infeasible_square: n_var=181004 > ceiling=120000` row
  classifies as RECOGNIZED (PASS). **The single most consequential adjudication.**
- ✅ Adding a new shipped status makes `tests/m3` red (drift enforcer, shown
  non-vacuous via NC-02 and NC-20).
- ✅ `tests/m3`: 0 failed / 32 skipped / 992 passed; exact triples recorded above.
- ✅ `260817-vbu-verify.sh all` still exits 0 with an empty diff.
- ✅ Seth has D-01…D-13 with shipped `file:line` evidence for each.
- ✅ Zero perimeter contact, $0, nothing fired, no network, no push.

## Deviations from plan

**1. [Rule 3 — blocking] `main(argv) -> int` instead of `main()` + `sys.exit()`.**
The `<cli_contract>` said `main()` prints then `sys.exit(exit_code)`. A `main()`
that always raises `SystemExit` cannot be asserted on from pytest. Shipped as
`main(argv=None) -> int` with `sys.exit(main())` under the `__main__` guard —
which is the EXISTING project convention (`plink_ld_to_npz.main`,
`run_native_ld_panel.main`) and preserves the observable shell behaviour
(`python3 src/python/fire_verifier.py stage-c …; echo $?` → 0/1, verified).
Argparse errors still raise `SystemExit(2)` as the contract requires.

**2. [Orchestrator constraint] STATE.md not touched; SUMMARY.md left
uncommitted.** The plan's Task 3 step 7–8 called for adding the STATE.md
quick-task row and committing it with the SUMMARY. The executor's constraints
reserve both for the orchestrator, so this SUMMARY is written but NOT committed
and `.planning/STATE.md` is untouched (`git status --short .planning/STATE.md` is
empty). **Action for the orchestrator:** add the quick-task row + refresh the
"Stopped at" block per `[[feedback_state_md_keep_current]]`, and commit this
SUMMARY.

**3. [Additive, in-scope] R4-COVERAGE enforcer paragraph in READY-TO-FIRE item
10.** The plan asked only for a pointer line on items 9 and 10. The `must_haves`
also required the obligation to have a NAMED enforcer, so the enforcer's name and
its skip semantics were written into item 10's post-fire disclosure paragraph
(outside the pinned card range; `vbu` diff still empty; `guk` F10 still green).

**4. [Additive] NC-16b.** Not in the plan; added because reconciling NC-16's
component counts showed two controls had not actually been observed red. See the
warning box above.

No architectural changes. No Rule 4 escalations. No auth gates.

## Known stubs

**`check_maf_depression` is implemented and tested but NOT WIRED into any
subcommand (A-12, intentional).** It is not a stub in the "empty value flows to
the UI" sense — the function is complete and has three tests including two
observed-red controls. What does not exist is the `(panel_maf, sumstats_maf)`
plumbing: those pairs require the per-region occlusion manifests joined to the
harmonized sumstats, which is Carter's planning-side work. Recorded as an explicit
"do not improvise this" note in both the AGENT-PROMPT STEP 9-GATE block and the
BROWSER-PASTE §9b block. **This does not prevent the plan's goal** — Stage B's
gate (peak RAM + cost denominator + status classification) is fully wired and the
MAF check was never in the runbook's Stage-B command list.

## Threat flags

None. Every file created is local, additive and non-executing on the fire path
until a human runs it; the module's own egress class (counts, booleans, byte
sizes, row indices, policy labels — never LD values) is asserted by
`test_report_json_carries_no_float_arrays` (T-sml-01), which was driven red
(NC-18). No new network endpoint, auth path, file-access pattern or schema at a
trust boundary was introduced beyond the `<threat_model>`'s registered surface.

## Commits

| Hash | Message |
|---|---|
| `125382f` | `test(quick-260818-sml): RED — fire-stage mechanical gate contracts, adjudicated against shipped code` |
| `d7f3b18` | `feat(quick-260818-sml): fire-stage mechanical gates — fail-closed verifier wired to the shipped producer/converter contracts` |
| `cbee927` | `docs(quick-260818-sml): wire the mechanical gates into the fire runbook + courier the shipped-code-wins adjudication to Seth` |

Not pushed (orchestrator's).

## Self-Check: PASSED

Created files verified present:
- `FOUND: src/python/fire_verifier.py`
- `FOUND: tests/m3/test_fire_verifier.py`
- `FOUND: .planning/quick/260818-sml-.../260818-sml-COURIER-TO-SETH-adjudication.md`
- `FOUND: .planning/quick/260818-sml-.../260818-sml-controls-transcript.txt`

Commits verified present in `git log --oneline`:
- `FOUND: 125382f`
- `FOUND: d7f3b18`
- `FOUND: cbee927`
