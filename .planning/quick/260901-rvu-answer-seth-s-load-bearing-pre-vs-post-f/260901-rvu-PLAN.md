---
phase: quick-260901-rvu
plan: 01
type: execute
wave: 1
depends_on: []
subsystem: m3-afr-ld-panel
tags: [pairwise-completeness, occlusion, panel-wide-excludelist, pre-vs-post-filter, partial-confounding-tail, informative-carriers, carrier-distribution-no-floor, post-hoc-no-rerun, staged-not-run, prereg-unchanged, nothing-fired]

files_modified:
  - tests/m3/test_pcs_panelwide_reclassify.py
  - src/python/pcs_panelwide_reclassify.py
  - .planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md
  - .planning/quick/260901-rvu-answer-seth-s-load-bearing-pre-vs-post-f/260901-rvu-PLAN.md
  - .planning/quick/260901-rvu-answer-seth-s-load-bearing-pre-vs-post-f/260901-rvu-RECORD-what-changes-and-the-survivors-route.md
  - .planning/quick/260901-rvu-answer-seth-s-load-bearing-pre-vs-post-f/260901-rvu-SUMMARY.md
  - .planning/STATE.md

autonomous: true

requirements:
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

user_setup: []

must_haves:
  truths:
    - "THE LOAD-BEARING QUESTION IS ANSWERABLE BY AN INSTRUMENT, NOT BY AN ARGUMENT. `src/python/pcs_panelwide_reclassify.py` classifies the DEFINED-row partial-confounding TAIL (`max(del_carriers_lost_frac, partner_carriers_lost_frac) >= 0.9`, the 3,094 rows) against the SAME production excludelist it already computes for undefined rows, and reports the split at BOTH row and pair level: `n_tail_rows_member_occluded_panelwide` (PRE-filter — the posted rule already discards them) versus `n_tail_rows_neither_member_occluded_panelwide` (POST-filter — they survive into the banked panel). The two are separate keys, reconciled arithmetically or the tool STOPS; nothing in the output permits collapsing them into one number."
    - "THE TAIL PREDICATE IS NOT A SILENT FORK OF THE SCANNER'S. `pairwise_completeness_scan.py` is CODE-FROZEN against `cb199b6` by the live runbook's STEP 0 gate, which `tests/m3/test_pairwise_completeness_scan.py` EXECUTES in a subprocess and requires to exit 0 — so the predicate CANNOT be extracted into a shared helper there. It is therefore declared once in the new module and pinned by a DIFFERENTIAL test that runs `pairwise_completeness_scan.summarize` (the REAL name — there is no `summarize_region`, and the scanner is code-frozen so an alias cannot be added) over synthetic `PairResult`s and requires `n_defined_lost_frac_ge_0p9` to equal the local predicate's count, on a grid that includes `frac == 0.9` EXACTLY (which is in the tail AND in the `(0.5,0.9]` bin — the bins and the tail deliberately disagree at the boundary), the float neighbours either side, del-only / partner-only / both, and UNDEFINED rows (excluded from the tail on both sides). The differential is observed RED under a one-character perturbation of the local predicate."
    - "THE INFORMATIVE-CARRIER DISTRIBUTION IS EMITTED AND NO FLOOR IS PROPOSED ANYWHERE. Per DEFINED row the tool emits `informative_carriers_rarer` — the retained (pairwise-complete) minor-allele carrier count of the RARER member — and reports its DISTRIBUTION: integer nearest-rank percentiles at q in {0,1,5,10,25,50,75,90,99,100}, exact counts for every m in 0..100, and cumulative counts at m <= {0,1,2,5,10,25,50,100}, computed TWICE — over all in-scope defined rows, and over defined rows REACHING THE MATRIX (Seth's `retained pairs`). A named guard fails if the module ever declares a carrier-floor CONSTANT, if any code path COMPARES an informative-carrier value against a numeric literal (where a floor is APPLIED), if any summary key matches the bare substrings `pass|fail|reliable|unreliable`, or if the printed banner stops saying that no floor is proposed. ⚠ `floor` is deliberately ABSENT from the key-name ban: the compliant key `no_floor_notice` DISCLAIMS a floor, and banning the word in key names would fire the guard on the tool's own unperturbed output — a floor cannot live in a key name, so it is banned where it can actually exist. Seth's calibration context (`m = 25` -> `SE(r) ~ 0.20`, `m = 100` -> `~0.10`) appears in the RECORD only, never as a threshold in code."
    - "`THE RARER VARIANT` IS DEFINED ONCE, TIE-BROKEN CONSERVATIVELY, AND ITS DISAGREEMENT WITH THE PRECISION-BINDING QUANTITY IS COUNTED RATHER THAN ASSUMED AWAY. Rarity is decided by `*_maf_marginal` (each member's minor-allele frequency over its OWN called set — NOT by `*_carriers_marginal`, which is not comparable across members because `n_called_del != n_called_partner` is the entire phenomenon under study). On an exact MAF tie the member with the SMALLER `*_carriers_retained` is chosen (the WORSE precision — the same conservative shape as the scanner's own MINOR-ALLELE TIE RULE), then smaller `*_carriers_marginal`, then `del`; `rarer_by_maf_tie` makes the tie visible. `informative_carriers_min = min(del_carriers_retained, partner_carriers_retained)` is emitted BESIDE it because `SE(r) ~ 1/sqrt(m)` binds on the minimum, and `n_defined_rows_rarer_and_min_definitions_disagree` counts the rows where the two differ — a near-miss between them may not motivate a hypothesis (`feedback_aggregate_agreement_hides_component_errors`)."
    - "THE MONOTONICITY CONDITION TRAVELS WITH THE TAIL CLAIM, NOT BESIDE IT. Occlusion is MONOTONE in the row set, so a PRE-filter (occluded) verdict on the tail is SOUND and a POST-filter (not-occluded) verdict is CONDITIONAL on the row set. A `tail_verdict_scope` sentence stating exactly this is written into the summary and PRINTED with the pre/post split, and the existing `provenance` block (bim path / sha256 / line count / per-region in-window row counts) is what it is relative to. A test asserts the split cannot be printed without the condition attached."
    - "ADDING DEFINED ROWS TO THE INPUT DOES NOT MOVE ONE UNDEFINED-SCOPE NUMBER. The banked run's `n_undefined_rows_in 15`, `n_undefined_distinct_pairs_in 13`, `n_rows_member_occluded_panelwide 14`, `n_rows_neither_member_occluded_panelwide 1`, `n_pairs_member_occluded_panelwide 12`, `n_pairs_neither_member_occluded_panelwide 1`, `n_pairs_neither_occluded_and_no_globally_invariant_member 1`, `n_pairs_with_ambiguous_member_id 0`, `ambiguous_member_ids []`, `occluded_member_vids` and `n_defined_rows_in 353074` keep their EXACT names and semantics. A regression test runs the SAME fixture with and without defined rows and asserts every one of the thirteen pre-existing `POOLED_KEYS` is identical between the two runs."
    - "THE POST-HOC-ONLY PROPERTY IS ENFORCED BY AN ALLOWLIST, NOT A BLACKLIST, AND THE GATE HAS BEEN SEEN RED IN BOTH DIRECTIONS. The AST gate is refactored into a callable that takes SOURCE TEXT, so it can be driven with perturbed text IN MEMORY (no stale `__pycache__` can decide the outcome). It now asserts the module's top-level import set is a SUBSET of an explicitly named allowlist (`__future__`, `argparse`, `csv`, `hashlib`, `json`, `sys`, `collections`, `pathlib`, `occlusion_span_filter`, `pairwise_completeness_scan`) — closed under future additions, unlike the banned-name list it replaces, which it RETAINS. Committed negative controls: injecting `import numpy`, injecting a `.bed` string literal in CODE, and injecting a `BedReader` attribute each make the gate RAISE; the unperturbed source passes."
    - "THE FROZEN SURFACES ARE UNTOUCHED AND THE SCANNER'S CODE PIN IS STILL GREEN. `git status --porcelain` is EMPTY for `src/python/pairwise_completeness_scan.py`, `src/python/occlusion_span_filter.py`, `src/python/run_native_ld_panel.py`, `src/python/fire_verifier.py`, `src/python/aou_ld_panel.py`, `tests/m3/source_freeze.py`, `.planning/amendments/` and `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`. The runbook's STEP 0 `assert_code_frozen(..., cb199b6, LANG_PY)` subprocess still exits 0."
    - "IT IS BUILT AND STAGED, AND IT HAS NOT BEEN RUN. A NEW `.planning/debug/260901-PENDING-PASTE-...md` carries `STATUS: STAGED — NOT RUN` on its own first lines, a ROTATE-NEVER-DELETE pre-flight, a one-region smoke invocation BEFORE the full 21-region one, and a COST NOTE whose only basis is the MEASURED 6-region/1h53m banked run — stated as an extrapolation basis, never as a prediction. The already-run `260831-PENDING-PASTE-...md` is NOT edited (its BLOCK A has fired; re-marking it would make it lie), and the live sweep runbook is NOT edited. A committed test feeds the STAGED argv from the new doc to `pcs_panelwide_reclassify._build_parser`, so a staged typo fails on THIS node instead of inside the perimeter."
    - "SETH GETS THE THINGS HE ASKED FOR AND THE ONE THING HE GOT WRONG. The record states, for the record and with no new code: the survivor `chr7:89454077:GCGTA:G` (span `[89454077, 89454081]`) x `chr7:89454076:C:T` sits ONE BASE BEFORE the anchor, OUTSIDE the span, and NEITHER member is occluded panel-wide — so there is no occluding deletion at all, present or absent. His prediction 2 (`any nonzero count must come from a case where the occluding deletion is absent from the panel`) does NOT explain it; the route is ADJACENCY WITHOUT OCCLUSION, the `-1` mirror of `00057`'s `+1`. Separately, his status line's `constant still 0.0005` is FLAGGED as stale with the three-step evidence (the `:3` sentence is a repo-local DRAFT banner OUTSIDE the posted paste block; the amendment posted as `mk7ze`; the producer compares against `OCCLUSION_SITE_FRACTION_CEILING` / `OCCLUSION_INFLATION_CEILING`) — flagged to him, never silently corrected in his words."
    - "NO PRE-REGISTERED OR MEASURED NUMBER MOVED. `353089` / `353090`, `353074`, 15 rows, 13 pairs, 10/3, the offset histogram `{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}`, panel-wide 12/1 pairs and 14/1 rows, and the 3,094-row (0.876%) tail are all UNCHANGED. `.planning/debug/260826-PCS-...-prereg-prediction.md` and every file under `.planning/amendments/` are not edited at all."
    - "THE SUITE IS RE-BASELINED BY NAME, NON-VACUOUSLY. Baseline `1168 passed / 33 skipped / 0 failed`. After the work: 0 failed; skipped STAYS exactly 33 (a new test landing as a SKIP is a BLOCKER, `feedback_skip_guard_masks_not_fixes`); the delta is reconciled per FILE and per TEST NAME (added/removed enumerated), never in aggregate only."
    - "NOTHING WAS FIRED. Zero enclave / VM / Dataproc / OSF / `gsutil` / `gcloud` / network contact; $0. The VM stays STOPPED. No genotype, no `.bed`, no per-sample datum is read, created or moved anywhere in this plan."
  artifacts:
    - path: "src/python/pcs_panelwide_reclassify.py"
      provides: "Tail pre/post-filter classification + informative-carrier distribution, added BESIDE the untouched undefined-scope quantities"
      contains: "TAIL_VERDICT_SCOPE"
      min_lines: 900
    - path: "tests/m3/test_pcs_panelwide_reclassify.py"
      provides: "RED-first spec: the differential tail pin, the rarer-member rule, the percentile definition, the undefined-scope invariance regression, the allowlist gate with three in-memory negative controls, the no-floor guard, the staged-argv gate"
      contains: "def test_"
      min_lines: 1500
    - path: ".planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md"
      provides: "STAGED, NOT RUN paste-ready invocation (smoke then full), pre-flight with ROTATE-NEVER-DELETE, cost note, and WHAT EACH ANSWER MEANS for the pre/post fork"
      contains: "STATUS: STAGED"
    - path: ".planning/quick/260901-rvu-answer-seth-s-load-bearing-pre-vs-post-f/260901-rvu-RECORD-what-changes-and-the-survivors-route.md"
      provides: "What the extension changes, the survivor's route (ADJACENCY WITHOUT OCCLUSION), and the stale-0.0005 flag with its three-step evidence"
      contains: "ADJACENCY WITHOUT OCCLUSION"
  key_links:
    - from: "src/python/pcs_panelwide_reclassify.py"
      to: "occlusion_span_filter.detect_occluded_variants"
      via: "the SAME per-region excludelist already built for undefined rows, reused for tail rows — never a second call with a different row set"
      pattern: "detect_occluded_variants\\(window_rows\\)"
    - from: "tests/m3/test_pcs_panelwide_reclassify.py"
      to: "pairwise_completeness_scan.summarize"
      via: "differential pin of the local tail predicate against the scanner's own n_defined_lost_frac_ge_0p9"
      pattern: "summarize\\("
    - from: ".planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md"
      to: "pcs_panelwide_reclassify._build_parser"
      via: "a committed test that parses the staged argv out of the doc and feeds it to the parser"
      pattern: "_build_parser"
---

<objective>
Answer Seth's load-bearing question — **are the 3,094 defined rows with
`carriers_lost_frac >= 0.9` PRE-filter or POST-filter?** — by extending the
instrument that already computes the panel-wide excludelist so that it also
classifies the DEFINED-row tail, and by emitting the informative-carrier
distribution he says he lacks.

**Purpose:** the question is UNMEASURED, not mis-scoped. `pcs_panelwide_reclassify.py:465`
filters to `undefined` rows and `:335` loops only those, so all **353,074**
defined rows were READ and never CLASSIFIED. The machinery is correct; it is
pointed at the wrong subset.

**Output:** an extended post-hoc tool (build only), a STAGED-NOT-RUN invocation,
and a record carrying the survivor's route and the flag on Seth's stale status line.

⚠ **THIS TASK FIRES NOTHING.** The input `pcs_pairs.tsv` is IN-PERIMETER and the
VM is STOPPED. Running it is Carter's call, from the staged doc, later.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/quick/260901-rvu-answer-seth-s-load-bearing-pre-vs-post-f/260901-rvu-SETH-REPLY-as-received.md
@.planning/quick/260831-kw8-close-seth-s-brief-blind-review-already-/260901-kw8-PANELWIDE-RECLASSIFICATION-as-received.md
@src/python/pcs_panelwide_reclassify.py
@tests/m3/test_pcs_panelwide_reclassify.py
@.planning/debug/260831-PENDING-PASTE-POSTHOC-panelwide-reclass-and-samepos-probe.md

<interfaces>
<!-- Extracted from the codebase during planning. The executor should use these
     directly. No codebase scavenger hunt is required to start. -->

`src/python/pairwise_completeness_scan.py` — READ-ONLY, CODE-FROZEN (see the
HARD CONSTRAINT below). The relevant surface:

```python
TSV_COLUMNS: tuple = PairResult._fields          # a must-be-identity link

class PairResult(NamedTuple):
    region_id: str; del_index: int; del_vid: str; del_chr: str; del_pos: int
    del_ref_len: int; del_span_end: int
    partner_index: int; partner_vid: str; partner_pos: int
    offset: int; side: str; already_occluded: bool; pair_key: str
    n_called_del: int; n_called_partner: int; n_both_called: int
    del_invariant: bool; del_globally_invariant: bool
    partner_invariant: bool; partner_globally_invariant: bool
    undefined: bool; invariant_member: str
    del_carriers_marginal: int; del_carriers_retained: int
    del_carriers_lost: int; del_carriers_lost_frac: float
    del_maf_marginal: float; del_minor_allele_tie: bool
    partner_carriers_marginal: int; partner_carriers_retained: int
    partner_carriers_lost: int; partner_carriers_lost_frac: float
    partner_maf_marginal: float; partner_minor_allele_tie: bool
    confounding_pattern: str

# The TAIL predicate, INLINE inside summarize (NOT a named function):
#     for r in defined_rows:
#         frac = max(r.del_carriers_lost_frac, r.partner_carriers_lost_frac)
#         if frac >= 0.9:
#             n_tail += 1
# -> summary key "n_defined_lost_frac_ge_0p9"
#
# NOTE the deliberate boundary disagreement: _lost_frac_bin(0.9) == "(0.5,0.9]"
# while the tail predicate INCLUDES 0.9. Bins are NOT a substitute for the tail.

# ⚠ THE NAME IS `summarize`. There is NO `summarize_region` (verified:
# hasattr(pcs, 'summarize_region') is False), region_id is POSITIONAL-FIRST and
# results POSITIONAL-SECOND, and the scanner is CODE-FROZEN so no alias can be
# added. Every existing call site reads:
#     pcs.summarize("R", rows, n_deletions=1, n_candidates_edge_clipped=0)
def summarize(region_id: str, results: Iterable[PairResult], *,
              window_bp: int = DEFAULT_WINDOW_BP, n_deletions: int,
              n_candidates_edge_clipped: int) -> dict     # -> SUMMARY_KEYS
def _render_field(value) -> str        # floats via repr() -> exact round-trip
def iter_bim_windows(bim_path, windows, *, pad_bp=0) -> dict
def _read_regions_tsv(regions_tsv, region_ids, *, ancestry) -> list
DEFAULT_ANCESTRY: str

# The emitted pcs_summary.json is a DICT keyed by region_id -> per-region summary.
```

`src/python/pcs_panelwide_reclassify.py` — THE FILE TO EXTEND. Existing shape:

```python
OUT_COLUMNS: tuple      # 20 per-row verdict columns
PROVENANCE_KEYS: tuple  # 14 keys
POOLED_KEYS: tuple      # 13 keys  <- ALL THIRTEEN KEEP THEIR NAME AND VALUE
PER_REGION_KEYS: tuple  # 15 keys
VERDICT_SCOPE: str

def _parse_bool(value) -> bool                 # raises on anything but True/False
def _count_distinct_pairs(rows) -> int
def _reconcile_or_raise(scope, unit, member, neither, total) -> None
def _read_pairs_tsv(pairs_tsv) -> list         # strict header == TSV_COLUMNS
def _classify_region(region_id, chrom, start_bp, end_bp, indexed_rows,
                     undefined_rows) -> (out_rows, sorted_occluded,
                                         n_window_rows, ambiguous_vids)
def _roll_up(scope, out_rows, ambiguous_vids) -> dict
def reclassify(pairs_tsv, bim_path, regions_tsv, *, ancestry, region_ids) -> (rows, summary)
def write_out_tsv(out_rows, path) -> None
def _build_parser() -> argparse.ArgumentParser   # DECLARED CROSS-TASK CONTRACT
def main(argv=None) -> int

# THE TWO LINES THIS PLAN EXISTS TO CHANGE:
#   reclassify():  undefined_rows = [r for r in rows if _parse_bool(r["undefined"])]
#   reclassify():  windows = [w for w in windows_selected if w[0] in scan_ids]
#                  # scan_ids is built from UNDEFINED rows only -> 6 of 21 regions
```
</interfaces>

<hard_constraints>
**⚠ `src/python/pairwise_completeness_scan.py` MUST NOT BE EDITED — not one code line.**
The LIVE runbook `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`
STEP 0 gate calls `source_freeze.assert_code_frozen("src/python/pairwise_completeness_scan.py",
"cb199b6", LANG_PY)`, and `tests/m3/test_pairwise_completeness_scan.py` EXECUTES that
gate block in a subprocess and requires exit 0 + `CODE PIN PASSED`. Editing the
scanner's code turns that test RED, and the runbook may not be edited to repair it.
Therefore: **do not extract the tail predicate into the scanner.** Declare it in the
new module and pin it by the differential test in Task 1. This is a REAL constraint,
recorded, not a preference.

**Do not edit:** `occlusion_span_filter.py`, `run_native_ld_panel.py`,
`fire_verifier.py`, `aou_ld_panel.py`, `tests/m3/source_freeze.py`,
`.planning/amendments/**`, `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`,
`.planning/debug/260831-PENDING-PASTE-POSTHOC-panelwide-reclass-and-samepos-probe.md`
(its BLOCK A has RUN; re-marking it STAGED would make it lie),
`.planning/debug/260826-PCS-...-prereg-prediction.md`.

**Do not propose a carrier floor.** Emit the DISTRIBUTION only. Seth withheld the
value deliberately: *"picking a number from 'what passes' is the error we have now
made twice."* `m = 25 -> SE(r) ~ 0.20` and `m = 100 -> ~0.10` are CALIBRATION CONTEXT
for the record, never a constant in code.

**Do not change any measured or pre-registered number.** `353089` / `353090` /
`353074`, 15 rows, 13 pairs, 10/3, the offset histogram, panel-wide 12/1 and 14/1,
and the 3,094-row (0.876%) tail all STAND.

**Environment.** `PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python`.
Full `tests/m3` is ~14 min — allow >= 1,200,000 ms; afterwards
`git checkout -- tests/m3/sparse_parent_benchmark.tsv`.
Baseline **1168 passed / 33 skipped / 0 failed** — reconcile BY NAME.
Never `git add -A` / `.`; explicit paths only (GPFS shared tree, multi-terminal).

**⚠ A green assertion is evidence ONLY if seen RED.** Nineteen text-vs-meaning
bites in this repo. Every gate in this plan asserts on parsed structure or runtime
behaviour. Normalise whitespace before any prose check; strip commas before numerics.
</hard_constraints>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: RED — spec the tail pre/post-filter split, the rarer-member rule, the carrier distribution, and the undefined-scope invariance</name>
  <files>tests/m3/test_pcs_panelwide_reclassify.py</files>
  <behavior>
    Write these tests FIRST. Every one must be observed RED for the right reason
    (an assert/attribute failure inside the test body, never a collection error —
    the module is imported INSIDE each test, mirroring the existing file).

    **(a) The tail predicate is pinned to the scanner, differentially.**
    `test_the_tail_predicate_agrees_with_the_scanners_own_defined_lost_frac_ge_0p9`
    — build a list of synthetic `pairwise_completeness_scan.PairResult`s covering:
    `frac` exactly `0.9`; `0.8999999999999999`; `0.9000000000000001`; `0.0`; `1.0`
    on an UNDEFINED row; del-side-high/partner-side-low; partner-side-high/del-side-low;
    both high. Call
    `pcs.summarize("R", rows, window_bp=25, n_deletions=0, n_candidates_edge_clipped=0)`
    — ⚠ `region_id` is POSITIONAL-FIRST and `results` POSITIONAL-SECOND; the function
    is `summarize`, NOT `summarize_region`, and no alias may be added because the
    scanner is code-frozen. Then assert
    `summary["n_defined_lost_frac_ge_0p9"] == sum(1 for r in rows if not r.undefined
    and R.is_tail_row(<row-as-dict>))`. Assert the count is NON-ZERO and NON-TOTAL
    (a predicate that is always-true or always-false would otherwise pass vacuously).
    Add `test_the_tail_differential_is_not_vacuous` as its NEGATIVE CONTROL:
    monkeypatch `R.TAIL_MIN_CARRIERS_LOST_FRAC` (or perturb via a locally-defined
    `>` instead of `>=` predicate applied to the same grid) and assert the equality
    FAILS at the `frac == 0.9` case specifically.
    Also assert `pcs._lost_frac_bin(0.9) == "(0.5,0.9]"` — the boundary disagreement
    between the bins and the tail is REAL and must be pinned, not discovered later.

    **(b) The tail rows are classified against the SAME excludelist.**
    `test_a_tail_row_whose_member_is_occluded_is_PRE_filter` and
    `test_a_tail_row_with_neither_member_occluded_is_POST_filter` — extend
    `_region1_fixture` with DEFINED rows carrying `del_carriers_lost_frac=0.994`
    (one whose partner is `R1_OCCLUDED`, one on a clean pair) and assert:
    `row_class == "tail"`, the `del_occluded_panelwide` / `partner_occluded_panelwide` /
    `pair_reaches_matrix` columns, and the pooled keys
    `n_tail_rows_member_occluded_panelwide` / `n_tail_rows_neither_member_occluded_panelwide`
    and their PAIR twins.
    `test_a_defined_row_below_the_tail_is_not_emitted_and_an_undefined_row_is_never_tail`
    — a defined row at `frac == 0.5` produces NO output row; an undefined row with
    `frac == 1.0` is emitted with `row_class == "undefined"`, never `"tail"`.
    `test_the_tail_counts_reconcile_or_the_tool_raises` — monkeypatch
    `R._count_distinct_pairs` into disagreement and assert `_reconcile_or_raise` fires
    naming the TAIL scope (mirror the existing `test_the_two_counts_reconcile_or_the_tool_raises`).

    **(c) `THE RARER VARIANT` — the rule, the tie, and the disagreement.**
    `test_the_rarer_member_is_chosen_by_marginal_maf_not_by_marginal_carrier_count`
    — construct a row where `del_maf_marginal < partner_maf_marginal` but
    `del_carriers_marginal > partner_carriers_marginal` (possible because
    `n_called_del != n_called_partner`) and assert `rarer_member == "del"` and
    `informative_carriers_rarer == del_carriers_retained`.
    `test_an_exact_maf_tie_picks_the_worse_precision_and_flags_the_tie` — equal
    `*_maf_marginal`, unequal `*_carriers_retained`: assert the member with the
    SMALLER retained count is chosen, `rarer_by_maf_tie is True`, and
    `informative_carriers_rarer == informative_carriers_min`.
    `test_the_two_carrier_definitions_can_disagree_and_the_disagreement_is_counted`
    — a row where the rarer-by-MAF member has MORE retained carriers than its
    partner: assert `informative_carriers_rarer != informative_carriers_min`,
    `informative_carriers_defs_disagree is True`, and that the pooled key
    `n_defined_rows_rarer_and_min_definitions_disagree` counts it.

    **(d) The distribution.** `test_the_percentiles_are_integer_nearest_rank_on_a_known_array`
    — feed a fixture whose `informative_carriers_rarer` values are a KNOWN multiset
    and assert every emitted percentile against hand-derived nearest-rank values
    (`rank = ceil(q*n/100)`, clamped to >= 1; `p0` is the MIN, `p100` the MAX).
    `test_the_low_tail_counts_are_exact_and_cumulative_and_cover_every_m_to_100` —
    assert `informative_carriers_low_tail_*` carries a key for EVERY m in 0..100
    (including zeros) and that the cumulative `n_le_*` entries equal the prefix sums,
    plus `n_gt_100`.
    `test_the_distribution_is_reported_twice_over_all_defined_rows_and_over_rows_reaching_the_matrix`
    — a fixture with one occluded-member defined tail row and one clean one: the two
    distributions must DIFFER, and `n_defined_rows_reaching_matrix +
    n_defined_rows_member_occluded_panelwide == n_defined_rows_in`.

    **(e) NO FLOOR — and the guard must not ban its own disclaimer.**
    `test_no_carrier_floor_is_declared_anywhere` — parse the module with `ast` AT CALL
    TIME and assert THREE things, each scoped to where a floor can ACTUALLY exist:

    * **(e1) DECLARED** — no module-level assignment target matches `(?i)floor`.
    * **(e2) APPLIED** — no `ast.Compare` node anywhere in the module has an operand
      naming an informative-carrier quantity (a `Name`/`Attribute`/`Subscript` whose
      rendered text contains `informative_carriers`) on one side and a NUMERIC
      `ast.Constant` on the other. This is the assertion with teeth: a floor is a
      COMPARISON, and (e1) alone would miss `if row["informative_carriers_rarer"] < 25`.
    * **(e3) NAMED** — no key in `POOLED_KEYS + PER_REGION_KEYS + OUT_COLUMNS` matches
      the bare substrings `(?i)(pass|fail|reliable|unreliable)`.

    ⚠ **`floor` is DELIBERATELY NOT in the (e3) ban list, and the test says so in its
    docstring.** Task 2 requires the pooled key `no_floor_notice`, whose name
    DISCLAIMS a floor; banning the substring `floor` in key names fires the guard on
    the tool's own compliant, unperturbed output — green becomes unreachable while the
    key stays required. That is the text-vs-meaning failure mode, inside the gate
    written to enforce the discipline against it. A floor cannot live in a KEY NAME
    (a key is a label, not a threshold), so `floor` is banned in (e1) and (e2), where
    a real one would actually live, and not in (e3).

    Also assert the module carries a literal sentence saying no floor is proposed and
    that `main()`'s captured stdout contains it (whitespace-normalised).

    THREE NEGATIVE CONTROLS, all in-memory, each asserted non-vacuous:
    (i) `CARRIER_FLOOR = 25` injected at module level -> (e1) RAISES;
    (ii) `if row["informative_carriers_rarer"] < 25: pass` injected into a
    `FunctionDef` byte span -> (e2) RAISES;
    (iii) a key renamed to `n_tail_rows_unreliable` -> (e3) RAISES.
    The unperturbed module — INCLUDING its `no_floor_notice` key — passes all three.

    **(f) THE INVARIANCE REGRESSION — the one that protects the banked numbers.**
    `test_adding_defined_rows_does_not_move_any_undefined_scope_pooled_key` — run the
    SAME fixture twice, once with undefined rows only and once with defined rows added,
    and assert every one of the THIRTEEN pre-existing `POOLED_KEYS` is EQUAL between
    the two summaries, enumerated by name. Assert the thirteen names are still present
    verbatim in `R.POOLED_KEYS` (`set(...) >= {...}` with the literal thirteen).

    **(g) UPDATE the existing pinned-shape tests** — `test_summary_key_sets_are_exact`
    (add the new literal keys; keep the thirteen), `test_only_undefined_rows_are_reclassified`
    (RENAME to `test_defined_rows_below_the_tail_are_counted_but_not_emitted` and keep
    asserting `n_defined_rows_in`), and the CLI test's header assertion (auto-follows
    `OUT_COLUMNS`). Do NOT weaken any existing assertion to make room.
  </behavior>
  <action>
Append the new tests to `tests/m3/test_pcs_panelwide_reclassify.py` in new numbered
sections following the file's existing layout, and edit the three existing tests named
in (g). Reuse the existing fixture builders (`_pairs_row`, `_write_pairs_tsv`,
`_write_bim`, `_write_regions_tsv`, `_region1_fixture`, `_row_for`) — `_pairs_row`
already derives its defaults from `PairResult.__annotations__`, so new columns cannot
silently make the fixtures short. Import `pcs_panelwide_reclassify` INSIDE each test
body (never at module top) so the file COLLECTS cleanly and every test fails as an
assert/attribute error.

For (a), build `PairResult` instances via `pcs.PairResult(**{...})` with every field
supplied — derive the field list from `pcs.PairResult._fields`, never hand-typed.

⚠ Do NOT use `text.replace(...)` for any negative control. Perturbations are either
(i) a monkeypatch on a MODULE-GLOBAL symbol, or (ii) an AST-scoped byte-range edit of
source text held IN MEMORY, each asserting BOTH that it changed something AND that it
landed where the test claims. The planner's own first control for the STEP 0 gate was
defeated by a first-match replace that hit a DOCSTRING (`.planning/STATE.md` §M7 TRAP).
  </action>
  <verify>
    <automated>PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python; $PY -m pytest tests/m3/test_pcs_panelwide_reclassify.py -q 2>&1 | tail -40; echo "EXPECT: the NEW tests FAIL (AttributeError/assert); the 21 pre-existing ones except the 3 edited in (g) still PASS"</automated>
  </verify>
  <done>Every new test is RED for the right reason (assert/AttributeError inside the test body, NOT a collection error), enumerated by name in the run output. The 18 untouched pre-existing tests are still GREEN. Nothing in `src/python/` has been edited yet — `git status --porcelain src/python/` is EMPTY.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: GREEN — classify the defined tail and emit the informative-carrier distribution, without moving one undefined-scope number</name>
  <files>src/python/pcs_panelwide_reclassify.py</files>
  <behavior>
    Turn every Task 1 test GREEN. Nothing else may change: the thirteen existing
    `POOLED_KEYS` keep their names AND their values, and the fifteen `PER_REGION_KEYS`
    keep theirs.
  </behavior>
  <action>
**Constants (module level, after `VERDICT_SCOPE`):**

```
TAIL_MIN_CARRIERS_LOST_FRAC: float = 0.9
```
with a docstring stating it REPRODUCES `pairwise_completeness_scan.summarize`'s
own `frac >= 0.9` boundary and the summary key `n_defined_lost_frac_ge_0p9` (the
3,094-row / 0.876% tail) — that it is a RE-DERIVATION of an existing pre-registered
quantity and NOT a new threshold, that the scanner is CODE-FROZEN against `cb199b6`
so the predicate cannot be shared from there, and NAMING the differential test that
fails if the two ever disagree.

```
NO_FLOOR_NOTICE: str = (
  "NO CARRIER FLOOR IS PROPOSED BY THIS TOOL. It emits the informative-carrier "
  "DISTRIBUTION only. A floor, if ever adopted, must be derived from a location "
  "statistic on this distribution with a stated purpose and margin and live in a "
  "ledger slot, not as a literal here."
)

TAIL_VERDICT_SCOPE: str = (
  "PRE-filter vs POST-filter carries the SAME monotonicity asymmetry as the "
  "undefined-row verdicts: a tail row classified PRE-filter (a member IS on the "
  "panel-wide excludelist) is SOUND, while a tail row classified POST-filter "
  "(NEITHER member is) is CONDITIONAL on the row set named in provenance and can "
  "flip to PRE-filter once more rows are supplied. It cannot flip the other way."
)
```

**Predicate helpers (module-global, so tests can monkeypatch them into disagreement):**

* `pair_max_lost_frac(row) -> float` — `max(float(row["del_carriers_lost_frac"]),
  float(row["partner_carriers_lost_frac"]))`. Floats were written by
  `_render_field` via `repr`, so `float()` round-trips EXACTLY; a parse failure RAISES.
* `is_tail_row(row, *, threshold=TAIL_MIN_CARRIERS_LOST_FRAC) -> bool` —
  `(not _parse_bool(row["undefined"])) and pair_max_lost_frac(row) >= threshold`.
* `rarer_member(row) -> (str, bool)` — returns `("del"|"partner", maf_tie)`.
  Rarity by `*_maf_marginal`. On an EXACT tie: smaller `*_carriers_retained`, then
  smaller `*_carriers_marginal`, then `"del"`. Docstring states WHY MAF and not
  marginal carrier count (`n_called_del != n_called_partner` is the phenomenon under
  study, so marginal counts are not comparable across members) and WHY the tie breaks
  toward the worse precision (same conservative shape as the scanner's own
  MINOR-ALLELE TIE RULE, which reports the LARGER `lost_frac` at `af_a1 == 0.5`).
* `_percentiles(sorted_values, quantiles) -> dict` — INTEGER nearest-rank, integer
  arithmetic only: `rank = -(-q * n // 100)`, clamped to `>= 1`, value
  `sorted_values[rank - 1]`; `{}` when `n == 0`. Docstring states the convention
  explicitly (`p0` is the MIN, `p100` the MAX) so no reader has to guess.
* `_low_tail_counts(values, *, cap=100, cumulative_at=(0,1,2,5,10,25,50,100)) -> dict`
  — `{"m_0": .., ..., "m_100": ..}` for EVERY m in `0..cap` including zeros, plus
  `n_le_<K>` prefix sums and `n_gt_100`.

**`OUT_COLUMNS` — APPEND (never reorder the existing 20):**
`row_class`, `carriers_lost_frac_pair_max`, `n_both_called`,
`del_carriers_retained`, `partner_carriers_retained`,
`del_maf_marginal`, `partner_maf_marginal`,
`rarer_member`, `rarer_by_maf_tie`,
`informative_carriers_rarer`, `informative_carriers_min`,
`informative_carriers_defs_disagree`.

**`_classify_region` — the core change.** Take `undefined_rows` AND `defined_rows`
for the region. Build the excludelist ONCE per region (the existing single
`detect_occluded_variants(window_rows)` call — do NOT add a second call). Then:

* EMIT a per-row verdict dict for every UNDEFINED row (`row_class="undefined"`,
  exactly as today) and for every TAIL row (`row_class="tail"`).
* For DEFINED rows BELOW the tail: compute the occlusion flags and
  `informative_carriers_rarer` for the AGGREGATES ONLY — do not append them to
  `out_rows`. The emitted TSV must stay bounded (undefined + tail), and `reclassify`
  must assert `len(all_out) == n_undefined_emitted + n_tail_emitted` before returning.
* Return the aggregate accumulators alongside the existing tuple: the defined-row
  `informative_carriers_rarer` values (all, and reaching-matrix only), the
  defs-disagree count, and the defined occluded/reaching counts.

⚠ Missing-vid handling: today `_classify_region` RAISES if a pair member is absent
from the window row set. KEEP that for undefined AND tail rows (a not-occluded verdict
on a member you cannot see is a silent fabrication). For below-tail defined rows the
same rule applies — a mismatched `.bim` must be loud, not quietly partial.

**`reclassify` — scope change.** Replace the undefined-only filter with:
`undefined_rows` (as today) and `defined_rows = [r for r in rows if not
_parse_bool(r["undefined"])]`. Build `scan_ids` from the union so ALL regions carrying
rows are scanned (6 -> 21 in the real artifact); the existing unknown-region raise
must now cover defined rows too. `pad_bp=0` stays — it is load-bearing and AST-pinned.

**New `POOLED_KEYS` (APPEND to the thirteen — none removed, none renamed):**
`tail_min_carriers_lost_frac`, `n_tail_rows_in`, `n_tail_rows_out_of_scope`,
`n_tail_distinct_pairs_in`, `n_tail_rows_member_occluded_panelwide`,
`n_tail_rows_neither_member_occluded_panelwide`,
`n_tail_pairs_member_occluded_panelwide`,
`n_tail_pairs_neither_member_occluded_panelwide`, `n_tail_regions_with_rows`,
`n_defined_rows_member_occluded_panelwide`, `n_defined_rows_reaching_matrix`,
`n_defined_rows_rarer_and_min_definitions_disagree`,
`informative_carriers_percentiles_defined_rows`,
`informative_carriers_percentiles_defined_rows_reaching_matrix`,
`informative_carriers_low_tail_defined_rows`,
`informative_carriers_low_tail_defined_rows_reaching_matrix`,
`no_floor_notice`, `tail_verdict_scope`.

**New `PER_REGION_KEYS` (append):** `n_defined_rows_in`,
`n_defined_rows_reaching_matrix`, `n_tail_rows_in`, `n_tail_distinct_pairs_in`,
`n_tail_rows_member_occluded_panelwide`,
`n_tail_rows_neither_member_occluded_panelwide`,
`n_tail_pairs_member_occluded_panelwide`,
`n_tail_pairs_neither_member_occluded_panelwide`.

**⚠ SPLIT `out_rows` BY `row_class` BEFORE ROLLING UP.** `_roll_up` is called on
the UNDEFINED-ONLY subset (`row_class == "undefined"`) and produces the existing
thirteen `POOLED_KEYS` UNCHANGED; a SECOND, tail-scoped roll-up is called on the
TAIL-ONLY subset (`row_class == "tail"`) and produces the new `n_tail_*` keys. Rolling
up the combined `all_out` would fold tail rows into `n_undefined_rows_in` /
`n_rows_member_occluded_panelwide` / the pair twins and silently move the banked
15 / 13 / 14-1 / 12-1 — the exact violation Task 1(f) exists to catch. Do not let the
combined list reach `_roll_up`.

**Reconciliation (a count is a claim).** Call `_reconcile_or_raise` for the TAIL
scope at BOTH row and pair level, and assert
`n_defined_rows_member_occluded_panelwide + n_defined_rows_reaching_matrix ==
n_defined_rows_in` (in-scope basis). Add an OPTIONAL `--pcs-summary` input: when
given, sum `n_defined_lost_frac_ge_0p9` over the SCANNED regions of the scanner's own
summary JSON (a dict keyed by region_id) and RAISE if it differs from `n_tail_rows_in`,
naming both numbers and both bases. That closes the tail predicate against the
scanner's OWN measurement at runtime, in addition to the differential test.

**`_build_parser`.** Add `--tail-min-lost-frac` (default `TAIL_MIN_CARRIERS_LOST_FRAC`;
help says it REPRODUCES the scanner's pre-registered boundary, is NOT a policy
threshold, and that changing it invalidates the `--pcs-summary` reconciliation) and
`--pcs-summary` (optional). The prog name and every existing flag name stay EXACTLY as
they are — `_build_parser` is a declared cross-task contract.

**`main` stdout.** Print, in this order: the existing POOLED block; then a
`=== THE TAIL: PRE-FILTER vs POST-FILTER ===` block giving the row-level and
pair-level split with `TAIL_VERDICT_SCOPE` printed IMMEDIATELY beside it (never
above a screenful of other output); then
`=== INFORMATIVE-CARRIER DISTRIBUTION (Seth's quantity) ===` with both percentile
sets and both low-tail blocks; then `NO_FLOOR_NOTICE`.

**Module docstring.** Add a section `(6) THE DEFINED-ROW TAIL AND THE
INFORMATIVE-CARRIER DISTRIBUTION` stating: the question (PRE- vs POST-filter),
`the rarer variant`'s definition and tie rule, the monotonicity condition on
POST-filter verdicts, that NO floor is proposed, and that the scanner could not host
the shared predicate because its CODE is pinned at `cb199b6` by the live runbook's
STEP 0 gate — name the differential test as the enforcer. Keep the module PURE STDLIB.
  </action>
  <verify>
    <automated>PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python; $PY -m pytest tests/m3/test_pcs_panelwide_reclassify.py -q 2>&1 | tail -20 && $PY -m pytest tests/m3/test_pairwise_completeness_scan.py -q 2>&1 | tail -10 && git status --porcelain src/python/pairwise_completeness_scan.py src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py src/python/aou_ld_panel.py tests/m3/source_freeze.py .planning/amendments/ | tee /dev/stderr | wc -l | grep -qx 0 && echo "FROZEN SURFACES CLEAN"</automated>
  </verify>
  <done>All tests in `test_pcs_panelwide_reclassify.py` pass; `test_pairwise_completeness_scan.py` is unchanged and still passes INCLUDING the STEP 0 code-pin subprocess; `git status --porcelain` is empty for every frozen path. The thirteen original `POOLED_KEYS` names are present verbatim and the invariance regression (Task 1f) is green.</done>
</task>

<task type="auto">
  <name>Task 3: Extend the post-hoc surface gate to an ALLOWLIST and prove it RED in three directions</name>
  <files>tests/m3/test_pcs_panelwide_reclassify.py, src/python/pcs_panelwide_reclassify.py</files>
  <action>
Refactor `test_the_tool_never_opens_a_bed_or_decodes_a_genotype`'s inline AST walk into
a module-level helper in the TEST file:

```
def _assert_no_genotype_or_network_surface(text: str) -> None
```

It must (i) RETAIN every existing assertion (banned imports `BedReader` /
`Genotypes` / `MISSING_DOSAGE`; banned `BedReader` name/attr; banned `read_variant`
attr; no `.bed` string literal OUTSIDE a docstring; at least one `.bim` literal), and
(ii) ADD the closure that makes it survive future edits:

* **AN ALLOWLIST, NOT A BLACKLIST.** The set of top-level imported module roots must be
  a SUBSET of exactly `{"__future__", "argparse", "csv", "hashlib", "json", "sys",
  "collections", "pathlib", "occlusion_span_filter", "pairwise_completeness_scan"}`.
  A blacklist decays the moment someone adds a surface nobody thought to ban; a
  subset check does not. State that reasoning in the helper's docstring.
* Ban `.fam`, `gs://`, `http://`, `https://` string literals in CODE (docstrings exempt,
  same byte-range technique).
* Ban the attribute/name `subprocess`, `socket`, `urlopen`, `Popen`, `system`.

Call it from the existing test with the REAL source, then add
`test_the_surface_gate_fails_on_an_injected_surface` driving it with THREE perturbed
sources held **in memory**:
1. `import numpy` prepended after `from __future__ ...` (allowlist violation),
2. a `.bed` path literal injected into a FUNCTION BODY (never a docstring), located by
   AST byte range,
3. a `BedReader` attribute reference injected into a function body.
Each must raise `AssertionError`; the unperturbed source must not. Assert each
perturbation actually CHANGED the text and landed inside a `FunctionDef` byte span —
a control that is vacuous is worse than no control.

Then add `test_the_staged_doc_argv_parses_against_the_declared_contract`: read
`.planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md`,
extract every fenced `bash` block, select the lines invoking
`src/python/pcs_panelwide_reclassify.py`, `shlex.split` them (after joining
backslash-continued lines), strip the leading `python3 <script>` tokens, and feed the
remainder to `pcs_panelwide_reclassify._build_parser().parse_args(...)`. Assert it
does NOT raise and that BOTH staged invocations (smoke and full) are found. NEGATIVE
CONTROL: mutate one flag to `--pairs-tsvv` in memory and assert `SystemExit`.

⚠ This test depends on Task 4's document. Write it here and expect it RED until
Task 4 lands; Task 4's `<verify>` is where it turns green.
  </action>
  <verify>
    <automated>PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python; $PY -m pytest tests/m3/test_pcs_panelwide_reclassify.py -q -k "surface or staged_doc_argv" 2>&1 | tail -25; echo "EXPECT: the surface-gate tests PASS; the staged-doc argv test FAILS (doc not written yet)"</automated>
  </verify>
  <done>`_assert_no_genotype_or_network_surface` passes on the real module and RAISES on all three in-memory perturbations, each proven non-vacuous and AST-located. The staged-argv test exists and is RED pending Task 4.</done>
</task>

<task type="auto">
  <name>Task 4: Stage the invocation (NOT RUN), write the record, refresh STATE.md, commit</name>
  <files>.planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md, .planning/quick/260901-rvu-answer-seth-s-load-bearing-pre-vs-post-f/260901-rvu-RECORD-what-changes-and-the-survivors-route.md, .planning/quick/260901-rvu-answer-seth-s-load-bearing-pre-vs-post-f/260901-rvu-SUMMARY.md, .planning/STATE.md</files>
  <action>
**(1) The STAGED doc** — a NEW file, first lines `# PENDING PASTE — the DEFINED-row
tail: PRE-filter or POST-filter, and the informative-carrier distribution` /
`STATUS: STAGED — NOT RUN`. Model it on
`.planning/debug/260831-PENDING-PASTE-POSTHOC-panelwide-reclass-and-samepos-probe.md`
(which it must NOT edit — BLOCK A of that doc has already FIRED). Contents:

* **What it answers and why the sweep could not** — the two reasons, stated: the
  scanner enumerates from the RAW `.bim` and never applies `--exclude` (its own
  docstring says the `--exclude` side is only PARTLY visible); and
  `pcs_panelwide_reclassify` filtered to `undefined` rows, so all 353,074 defined rows
  were READ and never CLASSIFIED. **The question was UNMEASURED, not mis-scoped.**
* **PRE-FLIGHT with a STOP on each check** — `pcs_pairs.tsv` must exist and be the
  banked artifact (`md5 287b16b1991f63423ff3933996c0334d`, `353090` lines — verify,
  do not assume); both output paths must be free, and if occupied
  **ROTATE, NEVER DELETE** (`mv <path> <path>.PRE-$(date -u +%Y%m%dT%H%M%SZ)`).
* **SMOKE FIRST** — a `--region-ids m2_region_00149` invocation, then the full
  21-region one. Both `python3 src/python/pcs_panelwide_reclassify.py` with
  `--pairs-tsv /home/jupyter/occ_measure/pcs_pairs.tsv`,
  `--bfile-prefix /home/jupyter/afr_cohort`, `--regions-tsv config/ld_regions.tsv`,
  `--ancestry AFR`, `--pcs-summary /home/jupyter/occ_measure/pcs_summary.json`, and
  distinct `--out` / `--summary` paths per invocation.
* **COST NOTE, basis stated, NOT a prediction** — the banked run built excludelists
  for **6** regions (`n_rows_in_window` totalling ~1.01M rows) in **1h53m** at ~99%
  CPU including two sha256 passes over a 20.7M-line `.bim`. This run builds them for
  all **21**. State that as the extrapolation BASIS and explicitly refuse to state a
  runtime.
* **WHAT EACH ANSWER MEANS** — the fork, both branches, in Seth's own terms:
  `n_tail_rows_neither_member_occluded_panelwide == 0` -> **PRE-filter**, the rule
  already discards them, amend for neither finding and disclose both;
  `> 0` -> **POST-filter**, a prevalent systematic silent corruption in the banked
  matrix, unambiguously pre-registration-level, amend for the TAIL with the single
  surviving pair folded in as a disclosed residual. And the condition, stated ONCE and
  attached: a POST-filter verdict is CONDITIONAL on the row set (monotonicity); a
  PRE-filter verdict is not.
* **NO EXPECTED VALUE IS STATED** for any tail count, and **no carrier floor is
  proposed** — the doc says so explicitly.
* A line stating the doc fires nothing on its own and that running it requires the VM,
  which is Carter's call.

**(2) The RECORD** — `260901-rvu-RECORD-what-changes-and-the-survivors-route.md`:
* What Seth's reply changes: **Q4 CONCEDED** (the retained NaN-raise is a ZERO-detector,
  not a residual detector — it stays, its billing changes); the consultation is
  BLOCKED on the pre/post question; his proposed replacement is a pairwise
  informative-carrier floor whose VALUE he deliberately withheld.
* **The denominator, settled: 353,074 DEFINED rows** = 353,089 candidate rows - 15
  undefined. Seth guessed ~353,196; neither of his two hypotheses. 3,094 / 353,074 =
  0.876%.
* **WHICH ROUTE THE SURVIVOR TOOK — the answer to his open question.** The survivor is
  `chr7:89454077:GCGTA:G` (span `[89454077, 89454081]`) x `chr7:89454076:C:T`. The
  partner sits **one base BEFORE** the anchor, **outside** the span, and **neither
  member is occluded panel-wide**. So there is no occluding deletion at all — neither
  absent nor present. His prediction 2 (*"any nonzero count must come from a case where
  the occluding deletion is absent from the panel"*) does **not** explain it. **The
  route is ADJACENCY WITHOUT OCCLUSION**, the `-1` mirror of `00057`'s `+1`. That is
  the shape of the blind spot he asked for.
* **⚠ HIS STATUS LINE IS STALE — FLAGGED, NOT SILENTLY CORRECTED.** Reproduce the
  three-step evidence in order: the `.planning/amendments/...-2026-08-20.md:3`
  sentence is a repo-local DRAFT banner **OUTSIDE** the posted paste block (the posted
  text is the marker-delimited block, lines 167-501) and was never posted; the
  amendment WAS posted as `osf.io/mk7ze` on `az52u`, 2026-08-22; the producer today
  compares against `OCCLUSION_SITE_FRACTION_CEILING` (0.005056) and
  `OCCLUSION_INFLATION_CEILING` (3.42) at `run_native_ld_panel.py:160-161`. Note
  explicitly that reading only `:3` reverses this conclusion, which is why the
  paste-block boundary is stated rather than assumed.
* **What the tool now measures and what it does NOT**: it measures the PRE/POST split
  and the informative-carrier distribution; it establishes NO prevalence, proposes NO
  floor, and moves NO criterion. `m = 25 -> SE(r) ~ 0.20` and `m = 100 -> ~0.10` are
  recorded as HIS calibration context, explicitly not adopted.
* A statement that **nothing has been run**: the tool is BUILT, TESTED, STAGED.

**(3) SUMMARY + STATE.md** — write `260901-rvu-SUMMARY.md` and prepend a
`## 2026-09-01` block to `.planning/STATE.md` as the new `★ RESUME HERE ★`, demoting
the `quick-260901-l55` block. Record: the suite delta reconciled BY NAME and per file;
that no pre-registered number moved; that the VM is STOPPED and $0; and that the ONE
open action is Carter's decision whether to run the staged doc.

**(4) COMMIT** — one commit, explicit paths only (never `-A` / `.`):
`tests/m3/test_pcs_panelwide_reclassify.py`, `src/python/pcs_panelwide_reclassify.py`,
the new `.planning/debug/260901-PENDING-PASTE-...md`, the three files under
`.planning/quick/260901-rvu-.../`, and `.planning/STATE.md`.
If the commit fails with `invalid object` / `Error building trees`, that is the known
GPFS loose-object loss — recover per `reference_gpfs_git_object_store_loss`, do not
improvise.
  </action>
  <verify>
    <automated>PY=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python; $PY -m pytest tests/m3 -q 2>&1 | tail -15; git checkout -- tests/m3/sparse_parent_benchmark.tsv; git status --porcelain src/python/pairwise_completeness_scan.py src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py src/python/aou_ld_panel.py tests/m3/source_freeze.py .planning/amendments/ .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md .planning/debug/260831-PENDING-PASTE-POSTHOC-panelwide-reclass-and-samepos-probe.md | wc -l | grep -qx 0 && echo "FROZEN + ALREADY-RUN DOCS CLEAN"</automated>
  </verify>
  <done>Full `tests/m3` reports 0 failed and exactly 33 skipped; the pass total is reconciled BY NAME (added/removed enumerated) and per file. The staged-argv test is GREEN. The staged doc says `STATUS: STAGED — NOT RUN` and has NOT been executed. `git status --porcelain` is empty for every frozen path and for both already-fired paste docs. One commit landed with explicit paths.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| in-perimeter artifact -> this tool | `pcs_pairs.tsv` / cohort `.bim` are controlled-access AoU derivatives; the tool runs INSIDE the perimeter |
| this tool -> egress summary | the summary JSON is the artifact a human may carry out of the perimeter |
| staged doc -> operator's shell | the doc is pasted verbatim into an in-perimeter shell |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-rvu-01 | Information disclosure | the emitted verdict TSV | mitigate | Emission is bounded to undefined + tail rows and asserted (`len(all_out) == n_undefined + n_tail`); every emitted field is a count, a fraction, a coordinate or an id — no per-sample vector, no sample identifier, no dosage. The distribution keys are aggregate counts only. |
| T-rvu-02 | Information disclosure | genotype surface reachable from the tool | mitigate | The AST gate is upgraded from a blacklist to an import ALLOWLIST (Task 3) and is observed RED on three in-memory injections; `.bed` / `.fam` / `gs://` / `http` literals in CODE are banned. |
| T-rvu-03 | Tampering | the tail predicate silently drifting from the scanner's | mitigate | Differential pin against `summarize`'s own `n_defined_lost_frac_ge_0p9` on a grid that includes the exact `0.9` boundary, plus an optional runtime reconciliation against the banked `pcs_summary.json` via `--pcs-summary`. |
| T-rvu-04 | Tampering | a pre-registered number moved by an extension | mitigate | The invariance regression (Task 1f) asserts all thirteen original `POOLED_KEYS` are equal with and without defined rows; frozen paths are `git status`-clean in two `<verify>` blocks. |
| T-rvu-05 | Elevation of privilege | a staged typo executing wrongly inside the perimeter | mitigate | The staged argv is parsed by `_build_parser` on THIS node by a committed test, with a `SystemExit` negative control. |
| T-rvu-06 | Repudiation | a POST-filter claim quoted without its scope condition | mitigate | `TAIL_VERDICT_SCOPE` is written into the summary AND printed immediately beside the split; a test asserts the split cannot be printed without it. |
| T-rvu-07 | Denial of service | unbounded memory on 353,074 defined rows | accept | The banked run already read all 353,089 rows into memory successfully (1h53m, exit 0). Emission stays bounded; per-row aggregates are ints. Runtime grows with 21 vs 6 excludelists — disclosed as a COST NOTE with its measured basis, not a prediction. |
</threat_model>

<verification>
1. `tests/m3` -> **0 failed**, **exactly 33 skipped**, pass total reconciled BY NAME
   and per file against the 1168 baseline. A new test landing as a SKIP is a BLOCKER.
2. Every new gate observed **RED** before being trusted: the tail differential
   (perturbed predicate), the no-floor guard (injected `CARRIER_FLOOR`), the surface
   allowlist (three injections), the staged-argv gate (mutated flag).
3. `git status --porcelain` EMPTY for `pairwise_completeness_scan.py`,
   `occlusion_span_filter.py`, `run_native_ld_panel.py`, `fire_verifier.py`,
   `aou_ld_panel.py`, `tests/m3/source_freeze.py`, `.planning/amendments/`, and both
   already-fired PENDING-PASTE docs.
4. The scanner's STEP 0 `assert_code_frozen(..., cb199b6)` subprocess still exits 0.
5. `353089` / `353090` / `353074` / 15 / 13 / 10-3 / the offset histogram / 12-1 /
   14-1 / 3,094 / 0.876% appear NOWHERE as a changed value.
6. No enclave, VM, Dataproc, OSF, `gsutil`, `gcloud` or network contact. VM STOPPED. $0.
</verification>

<success_criteria>
- The tool classifies the DEFINED-row tail PRE-filter vs POST-filter at row AND pair
  level, reconciled or raising, with the monotonicity condition printed beside the split.
- The informative-carrier distribution is emitted over all defined rows AND over rows
  reaching the matrix, with a stated percentile convention and an exact low tail.
- No carrier floor exists anywhere in code, keys or stdout, and a guard fails if one appears.
- All thirteen original `POOLED_KEYS` are byte-identical between an undefined-only run
  and a run with defined rows added.
- The invocation is STAGED and NOT RUN, and its argv parses against `_build_parser` here.
- The record answers Seth's open question (ADJACENCY WITHOUT OCCLUSION) and flags his
  stale `constant still 0.0005` with the three-step evidence, without editing his words.
</success_criteria>

<output>
After completion, create
`.planning/quick/260901-rvu-answer-seth-s-load-bearing-pre-vs-post-f/260901-rvu-SUMMARY.md`.
</output>
