---
phase: quick-260828-uej
plan: 01
type: execute
wave: 1
depends_on: []
subsystem: m3-afr-ld-panel
tags: [pairwise-completeness, runbook-freshness-gate, stale-artifact-rotation, output-quarantine, false-invariant, composite-parse, prereg-prediction, m3-07, stage-b, fire-safety]

files_modified:
  - src/python/pairwise_completeness_scan.py
  - tests/m3/test_pairwise_completeness_scan.py
  - .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md
  - .planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md
  - .planning/STATE.md
  - .planning/quick/260828-uej-make-the-re-run-safe-to-fire-replace-ste/260828-uej-PLAN.md
  - .planning/quick/260828-uej-make-the-re-run-safe-to-fire-replace-ste/260828-uej-SUMMARY.md

autonomous: true

requirements:
  - PCS-RUNBOOK-BEHAVIOURAL-FRESHNESS-GATE
  - PCS-RUNBOOK-ROTATE-BEFORE-SWEEP
  - PCS-RUNBOOK-ENV-RECORDS-AND-NAMED-REGION-IDS
  - PCS-RUNBOOK-FRESH-ARTIFACT-MTIME-REPORTED
  - PCS-WRITE-BEFORE-RECONCILE-AND-QUARANTINE
  - PCS-EMPTY-REGION-IDS-IS-AN-ERROR
  - PCS-FALSE-INVARIANT-ANCESTRY-RAISE-CLOSED
  - PCS-COMPOSITE-ANCESTRY-PARSE-PINNED
  - PCS-PREREG-POOLED-ROWS-353089
  - PCS-RESIDUALS-RECORDED-NOT-FIXED
  - PCS-FROZEN-SURFACES-UNCHANGED
  - PCS-SUITE-REBASELINE
  - PCS-NOTHING-FIRED

user_setup: []

must_haves:
  truths:
    - "STEP 0 STOPS ON THE WRONG CODE BY MEASUREMENT, NOT BY A COMMIT NAME. The commit-NAME gate is GONE from `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`. In its place: (i) `git status --porcelain src/python/pairwise_completeness_scan.py` must be EMPTY; (ii) `md5sum` and byte size of that file must equal the values measured AFTER Task 1 lands (the pre-change values were md5 `664921c7943c8dc1ce4bba87fd4cb957` / 69258 B at HEAD `e6f4f79` -- Task 1 CHANGES BOTH, so the gate carries the POST-Task-1 values, never these); (iii) `git log -1 --format='%h %s' -- src/python/pairwise_completeness_scan.py` must name the Task 1 commit; and (iv) a POSITIVE BEHAVIOURAL CAPABILITY CHECK -- an inline `python3` block calling `_read_regions_tsv('config/ld_regions.tsv', None)` asserting EXACTLY 276 windows with EXACTLY 276 distinct region ids (MEASURED during planning; the 8x code returns 552 and a pre-fix checkout raises `TypeError` on the keyword form). Pin what the code DOES: the contaminated run pulled to `769afa6`, whose SUBJECT LINE CONTAINS `quick-260825-qpf` (MEASURED: `git log -1 --format='%s' 769afa6 | grep -c 'quick-260825-qpf'` -> 1), so the old gate PASSED on the 8x code and false-STOPPED on `352ac9e`."
    - "THE GATE TEXT NEVER NAMES THE TWO-DASH ANCESTRY COMMAND-LINE TOKEN, AND SAYS SO INLINE. `tests/m3/test_pairwise_completeness_scan.py::test_pending_paste_step3_carries_no_ancestry_flag_so_the_default_is_load_bearing` asserts the runbook contains that token ZERO times, because the unmodified STEP 3 command's correctness rests entirely on `DEFAULT_ANCESTRY == 'AFR'`. The capability check is therefore expressed in Python against `_read_regions_tsv`, and the runbook carries an inline warning naming that test so no one reintroduces it. That pin stays GREEN, untouched, at every commit."
    - "THE STALE CONTAMINATED ARTIFACTS ARE ROTATED BEFORE THE SWEEP, NEVER DELETED, AND THE SWEEP REFUSES TO START IF THEY ARE STILL THERE. A new ROTATE step precedes `=== STEP 3` and `mv`s BOTH `/home/jupyter/occ_measure/pcs_pairs.tsv` (871,038,152 B, 2,865,514 lines -- EVIDENCE) and `pcs_summary.json` to `<name>.STALE.<UTC>`, then prints `ls -l --time-style=full-iso` on the directory. `rm` is forbidden there by the project ruling (`.planning/debug/260824-STAGE-A-env-stop-plink1.9-and-stale-scratch-TSV.md:34-38`). The STEP 3 python block opens with a pre-flight that raises `SystemExit` naming the path if EITHER artifact still exists -- so an operator who skipped the rotate is stopped BEFORE the sweep instead of `wc -l`-ing a contaminated file that returns 2865514."
    - "STEP 0 RECORDS THE `.bim` THE BANKED pair_keys ARE RELATIVE TO, PLUS THE INTERPRETER. `pair_key` is a GLOBAL `.bim` row index, so the 13 banked keys are comparable ONLY against a byte-identical `.bim`. STEP 0 runs `wc -l /home/jupyter/afr_cohort.bim` (EXPECT 20,767,864; any other value is a STOP), `ls -l --time-style=full-iso` on the `.bed`/`.bim`/`.fam` trio, `python3 -V` and the numpy version. These are FIELD RECORDS, in the same class as the existing founder-count block -- not decisions."
    - "THE 21 REGION IDS ARE NAMED, NOT COUNTED. STEP 3 prints every id read from `occ_measure_sample.tsv`, one per line, in addition to the existing count. A count of 21 is satisfiable by the WRONG 21 (`feedback_aggregate_agreement_hides_component_errors`). The paste-back list is extended to include those ids and `ls -l --time-style=full-iso` on the NEW artifacts, so a stale file cannot masquerade as fresh output."
    - "THE TSV IS WRITTEN BEFORE THE RECONCILIATION, AND A DISAGREEMENT QUARANTINES IT INSTEAD OF LEAVING A TRACEBACK. `main()` calls `write_tsv(all_results, args.out)` (and writes the summary JSON) FIRST, THEN computes `pooled_candidate_rows` and compares it to `len(all_results)`. On disagreement it renames the output by STRING CONCATENATION to `<out>.SUSPECT` (NEVER `Path.with_suffix`, which would turn `pcs_pairs.tsv` into `pcs_pairs.SUSPECT`), quarantines `<summary>.SUSPECT` the same way, prints ONE `ERROR:` line on stderr naming BOTH numbers, the token `n_candidate_rows` and the quarantine path, and RETURNS 2 -- matching every other failure path in `main()`. Three properties hold at once: (a) nothing survives at `--out`, so the operator's `wc -l` fails loudly instead of returning a stale 2865514; (b) the ~4h18m of compute is salvaged in `<out>.SUSPECT`; (c) the reconciliation's CONTENT is byte-identical to today's -- only POSITION and FAILURE HANDLING change, because the identity is verified correct (300 randomized end-to-end runs, zero failures) and is NOT re-litigated."
    - "A PRE-EXISTING `.SUSPECT` IS ROTATED, NEVER CLOBBERED. If `<out>.SUSPECT` already exists when a second disagreement fires, it is first moved to `<out>.SUSPECT.<UTC>`; the earlier bytes survive. Same project ruling as the runbook rotate."
    - "A `--region-ids` VALUE THAT STRIPS TO EMPTY IS AN ERROR, NOT A SILENT 276-REGION SCAN. `--region-ids ' , '` previously produced `[]` -> falsy -> `wanted = None` -> NO filter -> all 276 regions, a ~13x cost blow-up that failed loudly nowhere. It now raises `ValueError` inside the existing `try:`, so `main()` prints `ERROR: ...` naming the flag and the offending value and returns 2 BEFORE any scan and BEFORE any file is written. The flag ABSENT still means 'all regions' -- that path is UNCHANGED and is the negative control."
    - "THE FALSE INVARIANT IS CLOSED AND ITS CLOSURE WAS OBSERVED RED. `test_region_only_in_the_unrequested_ancestry_raises_naming_the_id` currently passes because its FIXTURE FILE is named `eur_only.tsv` while the error interpolates `{path}`. The fixture is renamed to `anc_split.tsv` and the assertion is scoped to the message segment AFTER the interpolated path (`str(excinfo.value).split(str(regions), 1)[1]`), so only the `{missing}` list can satisfy it. NEGATIVE CONTROL, MEASURED AND RECORDED: deleting `: {missing}` from the f-string at `src/python/pairwise_completeness_scan.py:1316` makes the repaired test RED -- it was GREEN under that same mutation before. The mutation changes the file LENGTH, so the bytecode-cache trap does not apply (`feedback_negative_control_defeated_by_bytecode_cache`); the file is restored and its md5 re-verified equal to the pre-mutation value."
    - "THE COMPOSITE ANCESTRY PARSE IS PINNED WHERE THE SELECTION HAPPENS, NOT ONLY AT THE PREDICATE. A test drives a whitespace-padded ancestry cell (`'  AFR  '`) through `_read_regions_tsv` and pins TODAY'S ACTUAL BEHAVIOUR: `_tsv_field` strips, so the scanner SELECTS the row. The same test MEASURES the divergence rather than asserting it in prose -- it ast-extracts `run_native_ld_panel._filter_ancestry` at call time (same technique as the existing enforcer, never `import`) and shows production DROPS that row. A companion test asserts the REAL `config/ld_regions.tsv` carries ZERO padded-or-quoted ancestry cells (MEASURED: 0 of 552), keeping the divergence LATENT AND MONITORED -- it goes RED the day such a row appears. RED mechanism, observed: removing `.strip()` from `_tsv_field` drops the padded row and the pin fails."
    - "THE PRE-REGISTERED PREDICTION GAINS THE DERIVED POOLED ROW COUNT, AND THE TWO ADDED NUMBERS RECONCILE BY A COMMITTED TEST. Section (e) of `.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md` ADDS exactly two rows: `POOLED candidate rows` = **353089** and `wc -l pcs_pairs.tsv` = **353090**, marked derived-before-the-run with the same status as the rest of (e). Derivation shown, not asserted: every AFR-pass row had both members inside the AFR window, so each was duplicated exactly 4x -> `1,412,356 / 4 = 353,089` EXACTLY; EUR's `1,453,157 / 4 = 363,289.25` is NON-INTEGRAL, independently corroborating the non-uniform-multiplicity account already at (b1). A committed test parses both numbers out of (e) and asserts `wc == rows + 1` AND `rows * 4 == 1412356` (`feedback_a_count_is_a_claim_scope_and_reconcile`). The pre-registered 15 / 13 / 10-3 and the offset histogram are NOT touched."
    - "THE TWO STALE CLAIMS THE CODE CHANGE CREATES ARE RECONCILED IN THE SAME COMMIT. (i) `src/python/pairwise_completeness_scan.py:1530` says 'This runs BEFORE write_tsv, so a disagreeing instrument leaves NO output'; (ii) the prereg record at (b1) says `main()` 'RAISES (before any output file is written)'. Both become FALSE the moment Task 1 lands and both are rewritten to the new contract (write -> reconcile -> quarantine -> return 2). Section (e)'s '**The command does not change.**' is clarified: the scanner argv is unchanged IN MEANING, while the runbook around it now gates behaviourally, rotates prior artifacts and names the 21 ids -- and NO predicted number changes as a result. HISTORICAL records (`.planning/quick/260825-*`, `260826-qq9-SUMMARY.md`, `-VERIFICATION.md`) are NOT rewritten: they are accurate records of what was true when written."
    - "THE RESIDUALS THAT ARE NOT BEING FIXED ARE RECORDED, WITH REASONS. A `RESIDUAL -- KNOWN, NOT FIXED` subsection of the prereg record names: (1) the `__sub12`/`__sub13` window overlap -- MEASURED: `m2_region_00040__sub12` AFR 93,681,040-104,615,815 vs `__sub13` AFR 98,615,815-109,550,590, and `m2_region_00060__sub12` AFR 81,228,215-91,874,650 vs `__sub13` AFR 85,874,650-93,521,095, i.e. 6,000,000 bp of overlap in each pair -- so the same `.bim` rows enter two regions' candidate sets and the POOLED candidate DENOMINATOR double-counts them; a pre-existing region-DEFINITION property, not a scanner defect, affecting the denominator and NOT the 15 findings (both regions carry 0 undefined rows), and present on the SAME basis in the 1,412,356 that 353,089 is derived from; (2) the scanner's denominator is pre-`--mac 1` / pre-`--exclude` while the panel's LD matrix is post-, so ANY fraction computed from these counts MUST name its denominator and none of them is a panel prevalence; (3) the residual of this plan's OWN code fix -- EARLY-exit paths (missing bfile component, `no windows selected`, duplicate region_id, empty `--region-ids`) return 2 BEFORE any write, so a stale artifact at the output path SURVIVES them; that hole is closed by the runbook's ROTATE step plus the STEP 3 pre-flight, NOT by the code, and is stated as such; and (4) a pointer to `260828-uej-CODEX-REVIEW-as-received.md` for the declined items (positional-vs-header manifest parse MEDIUM; iterator-level whitespace/case alias LOW), each with a one-line reason. The already-recorded pair-level 5-rows-vs-3-pairs undercount is CITED at its existing location, never duplicated."
    - "NOTHING WAS FIRED. Zero enclave / VM / Dataproc / OSF / `gsutil` / `gcloud` / network contact; \\$0. No per-sample data is created, read or moved. The re-run has NOT happened and the SUMMARY says so."
    - "NO CRITERION, THRESHOLD OR POLICY MOVED. `git diff --stat e6f4f79 HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py src/python/aou_ld_panel.py .planning/amendments/` is EMPTY at EVERY commit. `run_native_ld_panel.py` is READ by two ast enforcers and never written. The pre-registered 15 / 13 / 10-3 and the offset histogram are byte-unchanged."
    - "THE SUITE IS RE-BASELINED COMPONENT-EXACT. `tests/m3` reports 0 FAILED at every commit and the skip count STAYS at 33 (a new test landing as a SKIP is a BLOCKER -- `feedback_skip_guard_masks_not_fixes`; every test added here is pure-synthetic or a read-only parse of an in-repo file and cannot legitimately skip). The SUMMARY names every added test and shows `1122 + N == new_passed`, with the fast independent control `tests/m3/test_pairwise_completeness_scan.py` alone moving from its MEASURED baseline of 101 passed (0.91 s) to `101 + N`. Expected `N = 12`; a different N is acceptable ONLY if every test is named and the arithmetic re-derived -- an unreconciled delta is a BLOCKER. `git checkout -- tests/m3/sparse_parent_benchmark.tsv` after every full run; it is NEVER staged."
    - "THE SHARED GPFS TREE WAS NOT TRAMPLED. Every commit stages EXPLICIT paths (never `git add .` / `-A` -- `feedback_multi_terminal_staging`); no worktree isolation; branch stays `m3-W2-aou-deltas`. The pre-existing untracked and modified entries present at session start -- including the FOREIGN `.planning/STATE.md` modification, `targeted_rerun_*`, `results_lsweep_*`, the other `.planning/quick/` dirs -- are LEFT EXACTLY AS FOUND unless Task 4's STATE.md rule applies."
  artifacts:
    - path: "src/python/pairwise_completeness_scan.py"
      provides: "write-then-reconcile with `<out>.SUSPECT` quarantine + return 2, and an empty-after-strip `--region-ids` error"
      contains: "SUSPECT"
      min_lines: 1400
    - path: "tests/m3/test_pairwise_completeness_scan.py"
      provides: "RED-first coverage of the quarantine and stale-truncation properties, the empty-region-ids error, the repaired ancestry-raise invariant, the composite whitespace parse with its measured production divergence and real-manifest monitor, the three runbook enforcers, and the prereg arithmetic reconciler"
      contains: "anc_split"
      min_lines: 3400
    - path: ".planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md"
      provides: "behavioural STEP 0 gate, ROTATE step, .bim/interpreter field records, named 21 region ids, STEP 3 pre-flight existence guard, fresh-artifact ls in the paste-back list"
      contains: ".STALE."
    - path: ".planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md"
      provides: "the added derived prediction 353089 / 353090, the reconciled stale claims, and the RESIDUAL -- KNOWN, NOT FIXED subsection"
      contains: "353089"
  key_links:
    - from: ".planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md (STEP 0 gate)"
      to: "src/python/pairwise_completeness_scan.py (md5 + byte size)"
      via: "a committed test that RECOMPUTES the hash and size at call time and asserts both strings appear in the runbook"
      pattern: "hashlib"
    - from: ".planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md (capability EXPECT)"
      to: "_read_regions_tsv('config/ld_regions.tsv', None)"
      via: "a committed test that computes 276 / 276 at call time and asserts those are the numbers the gate expects"
      pattern: "_read_regions_tsv"
    - from: "main() reconciliation"
      to: "<out>.SUSPECT quarantine + return 2"
      via: "rename after write_tsv, exercised end-to-end by a monkeypatched off-by-one summary"
      pattern: "SUSPECT"
    - from: "prereg (e) 353089 / 353090"
      to: "prereg (b1) AFR-pass 1,412,356"
      via: "a committed test parsing both numbers and asserting wc == rows + 1 and rows * 4 == 1412356"
      pattern: "1412356"
---

<objective>
Close the five-way adversarial review's RUN-safety gaps so the 21-region
pairwise-completeness sweep is safe to fire. The INSTRUMENT was repaired in
`quick-260826-qq9` and is sound; what is unsafe is the RUN -- a freshness gate
that passes on the 8x code and stops on the repaired code, and a contaminated
871 MB artifact sitting at the exact path the operator `wc -l`s.

Purpose: an operator following the runbook literally must be UNABLE to (a) run
the wrong code undetected, (b) be false-stopped by a text-matching gate, (c) read
a stale artifact as if it were a fresh result, or (d) lose ~4h18m of compute to a
reconciliation traceback.

Output: a behavioural STEP 0 gate + a ROTATE step in the runbook, a
write-then-reconcile-then-quarantine `main()`, one closed false invariant, one new
composite-parse pin, and the derived `353089` added to the pre-registration.

NOTHING IS FIRED BY THIS PLAN. No enclave contact, no VM action, no OSF contact, $0.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/quick/260828-uej-make-the-re-run-safe-to-fire-replace-ste/260828-uej-CODEX-REVIEW-as-received.md
@.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md
@.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md
@src/python/pairwise_completeness_scan.py
@tests/m3/test_pairwise_completeness_scan.py

<interfaces>
<!-- Everything below was MEASURED during planning. Do not re-derive it and do   -->
<!-- not re-investigate the confirmed findings. Verify only where a task says so -->

PYTHON (the ONLY interpreter for every command in this plan):
  /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python      (3.11.15, numpy 2.4.4)

STARTING STATE (MEASURED 2026-08-28):
  HEAD                                                  e6f4f79 (pushed; origin == local)
  branch                                                m3-W2-aou-deltas  (no worktree isolation)
  md5sum src/python/pairwise_completeness_scan.py       664921c7943c8dc1ce4bba87fd4cb957
  stat -c %s src/python/pairwise_completeness_scan.py   69258
  git log -1 --format=%h -- <that file>                 1333f3f
  git status --porcelain on the 4 edited files          CLEAN (STATE.md is dirty from another terminal)
  pytest tests/m3/test_pairwise_completeness_scan.py -q 101 passed in 0.91s
  full tests/m3 baseline (given)                        1122 passed / 33 skipped / 0 failed, ~14 min

THE REAL MANIFEST (MEASURED):
  wc -l config/ld_regions.tsv                           553  (1 header + 276 x 2)
  ancestry column (1-based 7) value counts              276 AFR / 276 EUR
  _read_regions_tsv('config/ld_regions.tsv', None)      276 windows, 276 distinct ids
  _read_regions_tsv(..., ancestry='EUR')                276 windows, 276 distinct ids
  padded-or-quoted ancestry cells                       0    (the divergence is LATENT, not live)
  first AFR window                                      ('m2_region_00001', '1', 10000, 13506933)
  the 8x (pre-qq9) code returned                        552 windows for both

THE __subNN OVERLAP (MEASURED -- residual #1, recorded not fixed):
  m2_region_00040__sub12 AFR 93681040 104615815 | __sub13 AFR 98615815 109550590 -> 6,000,000 bp
  m2_region_00060__sub12 AFR 81228215  91874650 | __sub13 AFR 85874650  93521095 -> 6,000,000 bp

THE CODE SITES (line numbers as of e6f4f79; re-locate by SYMBOL, not by number):
  write_tsv                                   :1097  opens "w" -- truncates on success only
  the `: {missing}` f-string                  :1316  the false invariant's mutation target
  --region-ids argparse                       :1358
  --out / --summary argparse                  :1377 / :1378   both type=Path
  the strip-to-empty bug                      :1413-1417  `[r.strip() ...] if args.region_ids else None`
  main()'s try/except ValueError -> return 2  :1408-1437
  the POOLED reconciliation                   :1520-1541  comment at :1530 says "runs BEFORE write_tsv"
  write_tsv + summary write                   :1543-1545

THE TESTS THAT MUST CHANGE (not merely be added to):
  test_pooled_candidate_rows_reconciliation_raises_when_the_bases_disagree   ~:3186-3233
      asserts `pytest.raises(ValueError)` and `not out.exists()`. Task 1 INVERTS
      the first half to `rc == 2` with a clean stderr. The `not out.exists()`
      assertion SURVIVES and stays meaningful (the file is renamed AWAY, not left
      behind) -- keep it and add the `.SUSPECT` half.
  test_region_only_in_the_unrequested_ancestry_raises_naming_the_id          ~:2825-2848
      fixture `name="eur_only.tsv"` + `assert "eur_only" in str(excinfo.value)`.

THE PINS ON THE RUNBOOK THAT MUST STAY GREEN (tests/m3/test_pairwise_completeness_scan.py):
  :1646  test_pending_paste_exists_and_carries_the_harness_crosscheck       (9 needles)
  :2456  test_pending_paste_carries_the_falsifier_tokens                    (14 needles)
  :2485  test_pending_paste_runs_the_falsifier_before_the_crosscheck_and_the_sweep
             STEP 1 index < STEP 2 index < STEP 3 index; `Do not skip STEP 1.`;
             regex `Do NOT run STEP 2\.\s+Do\s+NOT run STEP 3\.`
  :2527  test_pending_paste_no_longer_claims_it_calls_no_plink              (negative needle + PATH export)
  :2717  test_pending_paste_step3_carries_no_ancestry_flag_so_the_default_is_load_bearing
             `"=== STEP 3" in text`; `'"--regions-tsv", "config/ld_regions.tsv"' in text`;
             THE HARD CONSTRAINT: `text.count("--ancestry") == 0`
  A new ROTATE heading inserted BETWEEN STEP 2 and STEP 3 does NOT break the order
  pin (it compares only the three named headings) -- VERIFIED by reading it.

THE PROJECT RULING ON STALE ARTIFACTS (.planning/debug/260824-STAGE-A-...:34-38):
  "ROTATE, never delete -- `mv ... .STALE.<UTC>`". The contaminated
  /home/jupyter/occ_measure/pcs_pairs.tsv (871,038,152 B / 2,865,514 lines) is
  EVIDENCE, exactly like m2_region_00057.ld.bin.

THE PREREG ARITHMETIC TO ADD (derivation given; do NOT re-derive the inputs):
  AFR pass 1,412,356 / 4 = 353,089   EXACT       -> POOLED candidate rows: 353089
  353,089 + 1 header                             -> wc -l: 353090
  EUR pass 1,453,157 / 4 = 363,289.25 NON-INTEGRAL (corroborates non-uniform multiplicity)
  Already at (b1): 2,865,513 = 1,412,356 + 1,453,157; wc -l 2,865,514.

VERIFIED SAFE -- DO NOT TOUCH, DO NOT RE-LITIGATE:
  the reconciliation is an identity over the same list object and cannot
  false-positive (300 randomized end-to-end runs, zero failures); scanner and
  production select identical region sets and window bounds; all 15 undefined rows
  sit >= 1.97 Mb inside their AFR windows so the AFR-narrowing is inert; argv is
  unchanged in meaning; output is deterministic.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Write the TSV BEFORE the reconciliation, quarantine it to `.SUSPECT` on disagreement, and make an empty `--region-ids` an error</name>
  <files>src/python/pairwise_completeness_scan.py, tests/m3/test_pairwise_completeness_scan.py</files>
  <behavior>
    RED FIRST. Every assertion below must be SEEN RED against the current code
    before the implementation lands, and the red output captured verbatim for the
    SUMMARY. A green assertion is evidence ONLY if it has been seen fail.

    - QUARANTINE, END TO END. Reusing the existing `off_by_one` monkeypatch shape
      from `test_pooled_candidate_rows_reconciliation_raises_when_the_bases_disagree`:
      `main()` RETURNS 2 (it does NOT raise); stderr carries one `ERROR:` line
      containing BOTH numbers (`3` and `2`), the token `n_candidate_rows`, and the
      quarantine path; `out` does NOT exist; `str(out) + ".SUSPECT"` DOES exist;
      its data-row count equals `len(all_results)` (2), so the compute is salvaged;
      with `--summary` passed, the JSON is quarantined the same way (`summary`
      gone, `str(summary) + ".SUSPECT"` present and parseable as JSON).
      RED mechanism: today the call RAISES, so `rc == 2` fails and no `.SUSPECT` exists.

    - THE STALE-FILE PROPERTY, PINNED DIRECTLY (this is BLOCKER-2's read path).
      Pre-create `out` with 5 junk lines mimicking a contaminated artifact.
      (i) SUCCESS path: a normal run leaves `out` holding ONLY the fresh header plus
      fresh rows -- zero junk lines survive. (ii) FAILURE path (off-by-one
      monkeypatch): afterwards `out` does NOT exist, so a `wc -l` at that path FAILS
      LOUDLY, and `str(out) + ".SUSPECT"` holds the FRESH rows, not the junk.
      RED mechanism: revert the write/reconcile order and (ii) leaves the junk at `out`.

    - A PRE-EXISTING `.SUSPECT` IS ROTATED, NOT CLOBBERED. Pre-create
      `str(out) + ".SUSPECT"` with a marker line, then trigger a disagreement.
      Afterwards exactly one `out.name + ".SUSPECT.*"` sibling exists and still
      holds the marker; the fresh `.SUSPECT` holds the new rows. RED mechanism: a
      bare `Path.replace` onto the existing `.SUSPECT` destroys the marker.

    - THE NAME IS BUILT BY STRING CONCATENATION. Assert the quarantined name ENDS
      WITH `.tsv.SUSPECT`, so a future `with_suffix` refactor (which would silently
      produce `pcs_pairs.SUSPECT`) goes RED.

    - `--region-ids` THAT STRIPS TO EMPTY IS AN ERROR. `main([... "--region-ids", " , ", ...])`
      returns 2; stderr names the flag and shows the offending value; NO output file
      is created; the scan never starts. NEGATIVE CONTROL, kept green: the same
      manifest with the flag ABSENT still scans every region and returns 0.
      RED mechanism: today the same call returns 0 after scanning ALL regions and
      writes a TSV.
  </behavior>
  <action>
    IMPLEMENT (after the tests are red):

    1. In `main()`, MOVE `write_tsv(all_results, args.out)` and the
       `if args.summary is not None: ...write_text(...)` block to BEFORE the
       `pooled_candidate_rows = sum(...)` line. Keep the sum expression and the
       equality comparison BYTE-IDENTICAL -- the identity is verified correct and
       is NOT being re-litigated; only position and failure handling change.

    2. Replace the `raise ValueError(...)` with a quarantine-and-return-2 block:
       `suspect = Path(str(args.out) + ".SUSPECT")` (STRING CONCATENATION -- never
       `with_suffix`); if `suspect` exists, first move it to
       `Path(str(suspect) + "." + stamp)` where
       `stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")` (ROTATE,
       never delete); then `Path(args.out).replace(suspect)`; same for
       `args.summary` when not None; `print(f"ERROR: ...", file=sys.stderr)`
       PRESERVING today's message text (both numbers, `n_candidate_rows`, the
       "MUST be the same basis" sentence) and APPENDING the quarantine path;
       `return 2`.

    3. Rewrite the comment block above the reconciliation (:1520-1541, whose last
       line claims "This runs BEFORE write_tsv, so a disagreeing instrument leaves
       NO output"). The new comment states all three reasons for the inversion:
       (a) writing first TRUNCATES any stale artifact at the read path -- the
       871 MB / 2,865,514-line contaminated `pcs_pairs.tsv` is the concrete case;
       (b) the rename leaves NOTHING at `--out`, so an operator's `wc -l` fails
       loudly instead of returning a stale number; (c) ~4h18m of compute is salvaged
       in `<out>.SUSPECT` instead of being discarded by a traceback. It also states
       the RESIDUAL honestly: EARLY-exit paths (missing bfile, `no windows
       selected`, duplicate region_id, empty `--region-ids`) still return 2 before
       any write, so a stale artifact survives THOSE -- closed by the runbook's
       ROTATE step and the STEP 3 pre-flight, not here.

    4. Fix the strip-to-empty hole at :1413-1417: replace the conditional
       expression with an explicit block; when `args.region_ids is not None`, build
       the stripped list and, if EMPTY, `raise ValueError(...)` naming the flag and
       `repr(args.region_ids)` -- inside the EXISTING `try:` so it lands on the
       existing `except ValueError` -> `ERROR:` + `return 2` path (no traceback).
       The flag ABSENT must still mean `region_ids = None` = all regions. Update the
       `--region-ids` argparse help accordingly.

    5. Grep the test module for any existing call passing `--region-ids ""` or
       relying on the falsy-means-all behaviour BEFORE changing it; if one exists,
       REPORT it rather than silently adapting it.

    Do NOT change: the reconciliation arithmetic, any threshold/criterion/policy,
    `TSV_COLUMNS`, `_render_field`, `summarize`, the stdout POOLED text, or the
    success-path `return 0`. Do NOT touch `occlusion_span_filter.py`,
    `run_native_ld_panel.py`, `fire_verifier.py`, `aou_ld_panel.py`, or
    `.planning/amendments/`.

    COMMIT (explicit paths only):
    `fix(quick-260828-uej): T1 -- write the TSV BEFORE the reconciliation and QUARANTINE it to .SUSPECT on disagreement (no stale file survives at the read path; ~4h18m of compute is salvaged), and an empty --region-ids is an ERROR, not a silent 276-region scan`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_pairwise_completeness_scan.py -q 2>&1 | tail -3</automated>
    Expect `106 passed` (MEASURED baseline 101 + 5 new; the rewritten test adds no
    item), 0 failed, 0 skipped, seconds not minutes. Any other number is an
    unreconciled delta -- name every test and re-derive before proceeding.

    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_pairwise_completeness_scan.py -q -k "suspect or quarantine or stale or region_ids" -v 2>&1 | tail -12</automated>
    Every new test must appear BY NAME and PASS. This is the runtime demonstration
    of the quarantine and the empty-region-ids error -- not a source grep.

    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git diff --stat e6f4f79 HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py src/python/aou_ld_panel.py .planning/amendments/</automated>
    Expect EMPTY output.
  </verify>
  <done>
    `main()` writes, then reconciles, then quarantines to `<out>.SUSPECT` (string
    concatenation; a pre-existing `.SUSPECT` rotated with a UTC stamp) and returns 2
    with a clean stderr line carrying both numbers and the quarantine path. A stale
    file at `--out` survives NEITHER the success nor the disagreement path. An
    empty-after-strip `--region-ids` returns 2 before any scan while the absent flag
    still means all regions. The stale "runs BEFORE write_tsv" comment is rewritten
    and states the early-exit residual. All five new assertions were seen RED first
    and the red output is captured. Frozen surfaces empty-diff. Committed with
    explicit paths.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Close the false invariant in the ancestry-raise test, and pin the composite whitespace parse where the SELECTION happens</name>
  <files>tests/m3/test_pairwise_completeness_scan.py</files>
  <behavior>
    - THE REPAIRED INVARIANT. `test_region_only_in_the_unrequested_ancestry_raises_naming_the_id`
      builds its fixture as `name="anc_split.tsv"` (so the FILENAME can no longer
      satisfy the assertion) and asserts on the id SPECIFICALLY: take
      `message = str(excinfo.value)`, split once on `str(regions)` (the interpolated
      path), and assert `"eur_only"` appears in the TAIL -- i.e. in the `{missing}`
      list, the only remaining route. Keep the existing EUR-reachability half
      unchanged (it proves the raise is about the ancestry key, not an absent id).
      The docstring names the false invariant it replaces and records that the CLI
      sibling `test_cli_region_only_in_the_unrequested_ancestry_exits_2_and_writes_no_tsv`
      (fixture `ancerr.tsv`) already covered the property BY ACCIDENT.

    - THE COMPOSITE PARSE, AT THE SELECTION LAYER. A new test writes a manifest
      whose ancestry cell is `"  AFR  "` and drives it through `_read_regions_tsv`
      (NOT through `_matches_ancestry`), pinning TODAY'S ACTUAL BEHAVIOUR:
      `_tsv_field` strips, so the row IS selected and the window IS returned. In the
      SAME test, MEASURE the production divergence rather than asserting it in prose
      -- ast-extract `_filter_ancestry` from `src/python/run_native_ld_panel.py` at
      call time and `exec` it in an empty namespace (identical technique to the
      existing enforcer; never `import run_native_ld_panel`, so a stale `.pyc`
      cannot make it green), then assert production DROPS `{"ancestry": "  AFR  "}`
      while the scanner SELECTS it. The docstring says plainly: this is a DIVERGENCE,
      it is LATENT not live, and the monitor below is what keeps it latent.

    - THE LATENCY MONITOR. A second new test reads the REAL `config/ld_regions.tsv`
      and asserts ZERO data rows have an ancestry cell differing from its own
      `.strip()` or containing a `"` character (MEASURED: 0 of 552). This goes RED
      the day a padded cell appears -- the only condition under which the divergence
      becomes live.
  </behavior>
  <action>
    Make the three test changes above. Then OBSERVE BOTH NEGATIVE CONTROLS and
    capture the verbatim output:

    (a) THE FALSE-INVARIANT CONTROL. Record `md5sum src/python/pairwise_completeness_scan.py`.
        Delete `: {missing}` from the f-string in `_read_regions_tsv` (~:1316). Run
        ONLY the repaired test -- it MUST go RED. (It was GREEN under this same
        mutation before the fix; state both observations side by side in the
        SUMMARY.) Restore with `git checkout -- src/python/pairwise_completeness_scan.py`,
        re-check the md5 EQUALS the recorded value, re-run the file green. The
        mutation changes the file LENGTH, so the bytecode-cache trap
        (`feedback_negative_control_defeated_by_bytecode_cache`) does not apply --
        say so explicitly rather than leaving it unaddressed.

    (b) THE COMPOSITE-PARSE CONTROL. Same record-mutate-restore-verify discipline:
        remove `.strip()` from `_tsv_field`; the composite test MUST go RED (the
        padded row is dropped and no window is returned). Restore, verify md5,
        re-run green.

    Both mutations are SCRATCH-ONLY and neither is committed:
    `git status --porcelain src/python/pairwise_completeness_scan.py` must be EMPTY
    before committing. Do NOT change any production code in this task -- the scanner
    must be byte-identical to its Task 1 state when this task commits.

    COMMIT (explicit paths only):
    `test(quick-260828-uej): T2 -- the ancestry-raise test was a FALSE INVARIANT (its own fixture FILENAME satisfied the assertion); rename to anc_split.tsv, assert on the id AFTER the path, and pin the composite whitespace parse where the SELECTION happens plus the monitor that keeps its production divergence latent`
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_pairwise_completeness_scan.py -q 2>&1 | tail -3</automated>
    Expect `109 passed` (106 + 3 new; the repaired test is modified, not added), 0
    failed, 0 skipped.

    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_pairwise_completeness_scan.py -q -k "unrequested_ancestry or composite or padded or whitespace" -v 2>&1 | tail -10</automated>
    Every one of those tests must appear BY NAME and PASS.

    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git status --porcelain src/python/pairwise_completeness_scan.py; md5sum src/python/pairwise_completeness_scan.py</automated>
    `git status --porcelain` must print NOTHING (both scratch mutations reverted)
    and the md5 must EQUAL the Task 1 post-commit value recorded in the SUMMARY.
  </verify>
  <done>
    The ancestry-raise test can no longer be satisfied by its own fixture filename
    and was OBSERVED RED under the `{missing}` deletion, with the pre-fix GREEN
    observation recorded beside it. The composite whitespace parse is pinned through
    `_read_regions_tsv`, its divergence from production is MEASURED by ast
    extraction at call time, and a monitor asserts the real manifest carries zero
    such rows. Both negative controls observed, both mutations reverted, scanner
    byte-identical to its Task 1 state. Committed with explicit paths.
  </done>
</task>

<task type="auto">
  <name>Task 3: Replace the runbook's commit-NAME freshness gate with a BEHAVIOURAL one, add the ROTATE step and the field records, and give all three a named enforcer</name>
  <files>.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md, tests/m3/test_pairwise_completeness_scan.py</files>
  <action>
    ORDER MATTERS: this task runs AFTER Tasks 1-2 are committed, because Task 1
    CHANGES the scanner's md5 and byte size. FIRST measure the values the gate will
    pin, from the committed tree:

      git status --porcelain src/python/pairwise_completeness_scan.py   (MUST be empty)
      md5sum src/python/pairwise_completeness_scan.py
      stat -c '%s' src/python/pairwise_completeness_scan.py
      git log -1 --format='%h %s' -- src/python/pairwise_completeness_scan.py

    THE HARD CONSTRAINT ON EVERY EDIT BELOW: the runbook must still contain the
    two-dash `ancestry` command-line token ZERO times
    (`test_pending_paste_step3_carries_no_ancestry_flag_so_the_default_is_load_bearing`
    pins it, because the unmodified STEP 3 command is correct only by virtue of
    `DEFAULT_ANCESTRY == "AFR"`). Express the capability check in Python against
    `_read_regions_tsv`, never by naming the flag, and STATE THAT CONSTRAINT INLINE
    in the runbook, naming that test, so no one reintroduces it.

    A. STEP 0 -- REPLACE THE GATE.
       Delete the paragraph beginning "If `git log -1` does not show a
       `quick-260825-qpf` commit ...". BEFORE deleting, grep the test module for the
       tokens in the sentence being removed and confirm nothing pins them; report if
       something does. KEEP the "NCSU must have been PUSHED first" warning -- it is
       still true and still load-bearing.
       In its place, with an EXPECT value and a STOP consequence for each:
         - `git status --porcelain src/python/pairwise_completeness_scan.py` -> EMPTY
           (a local edit means the gate's hash is not what will run).
         - `md5sum` -> the measured value; `stat -c '%s'` -> the measured size.
         - `git log -1 --format='%h %s' -- src/python/pairwise_completeness_scan.py`
           -> the Task 1 commit.
         - THE BEHAVIOURAL CAPABILITY CHECK, as a paste-able block that imports the
           module from `src/python` and calls
           `_read_regions_tsv("config/ld_regions.tsv", None)`, prints
           `manifest windows: <n> distinct region ids: <n>`, asserts BOTH are 276,
           and prints `CAPABILITY CHECK PASSED`.
           Say what each failure MEANS: `552` is the 8x-duplication code (the
           contaminated run); a `TypeError` is a pre-fix checkout; anything else is
           a STOP.
       Add a short WHY paragraph: the old gate matched a commit SUBJECT LINE, and
       the contaminated run's HEAD `769afa6` CONTAINS the string `quick-260825-qpf`
       (MEASURED: `git log -1 --format='%s' 769afa6 | grep -c 'quick-260825-qpf'`
       -> 1), so it PASSED on the 8x code and false-STOPPED on `352ac9e`. Pin what
       the code DOES, not what a commit is called.
       Add a HOW TO REGENERATE THIS GATE line (the four commands above), so a
       legitimate future change to the scanner has a named, cheap remedy rather than
       a dead pin.

    B. STEP 0 -- FIELD RECORDS (records, not decisions; same class as the existing
       founder-count block):
         wc -l /home/jupyter/afr_cohort.bim          EXPECT 20767864
         ls -l --time-style=full-iso /home/jupyter/afr_cohort.bed /home/jupyter/afr_cohort.bim /home/jupyter/afr_cohort.fam
         python3 -V
         python3 -c "import numpy; print('numpy', numpy.__version__)"
       State WHY the `.bim` line is a STOP on mismatch: `pair_key` is a GLOBAL `.bim`
       row index, so the 13 banked pair_keys are comparable ONLY against a
       byte-identical `.bim`.

    C. A NEW ROTATE STEP, placed AFTER STEP 2 and BEFORE `=== STEP 3` (heading:
       `=== STEP 2b -- ROTATE the prior artifacts. Never delete. ===`). It stamps
       `STAMP=$(date -u +%Y%m%dT%H%M%SZ)`, `mv -v`s each of
       `/home/jupyter/occ_measure/pcs_pairs.tsv` and
       `/home/jupyter/occ_measure/pcs_summary.json` to `<path>.STALE.$STAMP` when it
       exists, then prints `ls -l --time-style=full-iso /home/jupyter/occ_measure/`.
       Plus: NEVER `rm`. The contaminated `pcs_pairs.tsv` (871,038,152 B,
       2,865,514 lines, 2026-08-26) is EVIDENCE, exactly like
       `m2_region_00057.ld.bin`. Project ruling:
       `.planning/debug/260824-STAGE-A-env-stop-plink1.9-and-stale-scratch-TSV.md`.
       Note that STEP 0's `df -h /home/jupyter` must show room for the rotated
       871 MB copy PLUS the new artifact.

    D. STEP 3 -- PRE-FLIGHT + NAMED IDS. Inside the existing python heredoc (leave
       `'"--regions-tsv", "config/ld_regions.tsv"'` byte-identical -- it is pinned):
         - open with an existence pre-flight over BOTH output paths that raises
           `SystemExit` naming the offending path and telling the operator to run
           STEP 2b first, with the reason: a stale artifact at this path is exactly
           how a contaminated file masqueraded as a fresh result;
         - after `print("regions in the pre-committed sample:", len(ids))`, print
           EVERY id, one per line. A count of 21 is satisfiable by the WRONG 21.
       After the `wc -l` line add `ls -l --time-style=full-iso` on both new
       artifacts, and extend the PASTE BACK list to include the 21 named ids and
       those `ls -l` lines, with the reason: a stale file must not be able to
       masquerade as fresh output, and the mtime must post-date the STEP 2b stamp.

    E. THREE NAMED ENFORCERS in `tests/m3/test_pairwise_completeness_scan.py` (a
       claimed invariant with no enforcer is belief only --
       `feedback_a_claimed_invariant_needs_a_named_enforcer`). All three are
       RUNTIME-COMPUTED or parsed-structure, never a loose source grep:
         1. `test_pending_paste_step0_pins_the_scanner_by_a_CURRENT_content_hash`:
            recompute `hashlib.md5(...).hexdigest()` and `stat().st_size` of
            `src/python/pairwise_completeness_scan.py` AT CALL TIME and assert both
            strings appear in the runbook. It goes RED the moment the scanner
            changes without the gate being regenerated -- that is the point, and the
            runbook's REGENERATE line is the remedy. The docstring must say so and
            must distinguish this from `feedback_fixed_sha_whole_file_pin_is_a_timebomb`:
            the pinned value is RECOMPUTED here, never frozen.
         2. `test_pending_paste_step0_capability_numbers_are_the_real_manifest_numbers`:
            compute `len(_read_regions_tsv("config/ld_regions.tsv", None))` and the
            distinct-id count at call time (276 / 276), assert those exact numbers
            are the ones the gate EXPECTs, and assert `552` is named as the failure
            meaning.
         3. `test_pending_paste_rotates_before_the_sweep_and_never_deletes`: parsed
            structure only -- assert the ROTATE heading's index falls between the
            STEP 2 and STEP 3 heading indices; SLICE the text between the ROTATE
            heading and `=== STEP 3` and assert WITHIN THAT SLICE that `.STALE.` and
            `mv ` are present and that neither artifact is `rm`'d; then SLICE the
            STEP 3 block and assert the pre-flight guard names BOTH paths and raises
            `SystemExit`. Also assert the whole-document count of the two-dash
            ancestry token is still 0 (belt-and-braces with the existing pin).

    Do NOT alter STEP 1, STEP 2, the falsifier tokens, the EGRESS RULE, the plink
    pin, or the scanner argv's meaning.

    COMMIT (explicit paths only):
    `fix(quick-260828-uej): T3 -- the runbook's freshness gate matched a COMMIT SUBJECT (which PASSED on the 8x code at 769afa6 and false-STOPPED on 352ac9e); replace it with a content-hash + BEHAVIOURAL capability gate, ROTATE the contaminated artifacts before the sweep, record the .bim the banked pair_keys are relative to, and NAME the 21 ids -- each with a named enforcer`
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_pairwise_completeness_scan.py -q 2>&1 | tail -3</automated>
    Expect `112 passed` (109 + 3 enforcers), 0 failed, 0 skipped.

    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_pairwise_completeness_scan.py -q -k "pending_paste" -v 2>&1 | tail -12</automated>
    All FIVE pre-existing runbook pins plus the THREE new enforcers must appear BY
    NAME and PASS. The `--ancestry`-count pin among them is the proof the edits did
    not reintroduce the forbidden token.

    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -c "
import sys; sys.path.insert(0,'src/python')
import pairwise_completeness_scan as pcs
w = pcs._read_regions_tsv('config/ld_regions.tsv', None)
print('manifest windows:', len(w), 'distinct region ids:', len({x[0] for x in w}))
assert len(w) == 276 and len({x[0] for x in w}) == 276
print('CAPABILITY CHECK PASSED')
"</automated>
    This EXECUTES the gate's own logic against the shipped tree. It must print
    `manifest windows: 276 distinct region ids: 276` then `CAPABILITY CHECK PASSED`
    -- i.e. the gate the operator will paste actually passes here. Paste the verbatim
    output into the SUMMARY.
  </verify>
  <done>
    STEP 0 gates on content hash + byte size + last-touching commit + a POSITIVE
    behavioural capability check, and no longer on any commit subject line; it
    carries the WHY (769afa6 measured), the regeneration recipe, and the inline
    warning about the forbidden token. The `.bim` line count, the trio's `ls -l`,
    the interpreter and numpy versions are recorded with the pair_key rationale.
    A ROTATE step sits between STEP 2 and STEP 3 and never deletes; STEP 3 refuses
    to start if either artifact is still at its path and NAMES all 21 region ids;
    the paste-back list carries the ids and the fresh-artifact `ls -l`. Three named
    enforcers hold the gate current, and all five pre-existing runbook pins are
    green. Committed with explicit paths.
  </done>
</task>

<task type="auto">
  <name>Task 4: Add the derived 353089 / 353090 to the pre-registration, reconcile the two claims the code change made stale, record the residuals, and re-baseline the suite</name>
  <files>.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md, tests/m3/test_pairwise_completeness_scan.py, .planning/STATE.md</files>
  <action>
    A. SECTION (e) -- ADD, NEVER REVISE. Append exactly two rows to the prediction
       table:
         | `POOLED candidate rows` | **353089** |
         | `wc -l pcs_pairs.tsv`   | **353090** |
       Immediately below, SHOW the derivation (do not assert it): every AFR-pass row
       had both members inside the AFR window, so each was duplicated exactly 4x ->
       `1,412,356 / 4 = 353,089` EXACTLY; `353,089 + 1 header = 353,090`; and EUR's
       `1,453,157 / 4 = 363,289.25` is NON-INTEGRAL, which independently corroborates
       the non-uniform-multiplicity account already recorded at (b1). Mark both as
       DERIVED BEFORE THE RUN, same status as the rest of (e), and restate that a
       mismatch is a finding to report, never a number to adjust.
       DO NOT touch 15 / 13 / 10-3 or the offset histogram. Leave the existing
       sentence about 21 table lines in place -- it is now numerically pinned by the
       two new rows.

    B. RECONCILE THE TWO CLAIMS TASK 1 MADE STALE.
       (i) In (b1), "`main()` RAISES (before any output file is written)" becomes the
           new contract: `main()` writes the TSV, THEN reconciles, and on
           disagreement QUARANTINES the output to `<out>.SUSPECT` (rotating any
           prior `.SUSPECT`) and returns 2 -- so nothing survives at the read path
           and the compute is salvaged. Cite `quick-260828-uej`.
       (ii) In (e), "**The command does not change.**" is clarified: the scanner
            argv is unchanged IN MEANING, while the runbook around it now gates
            behaviourally (content hash + capability check, not a commit name),
            ROTATEs the prior artifacts, records the `.bim`, and NAMES the 21 ids --
            and NO predicted number changes as a result.
       Do NOT rewrite the historical records under `.planning/quick/260825-*` or
       `260826-qq9-{SUMMARY,VERIFICATION}.md`: they are accurate records of what was
       true when written.

    C. NEW SUBSECTION `### RESIDUAL -- KNOWN, NOT FIXED, AND WHY`, placed
       immediately before `## WHAT THIS RECORD DOES **NOT** ESTABLISH`. Four entries:
       1. The `__sub12`/`__sub13` 6 Mb window overlap. Show the MEASURED bounds
          (`m2_region_00040__sub12` AFR 93,681,040-104,615,815 vs `__sub13` AFR
          98,615,815-109,550,590; `m2_region_00060__sub12` AFR 81,228,215-91,874,650
          vs `__sub13` AFR 85,874,650-93,521,095 -- 6,000,000 bp each). The same
          `.bim` rows enter two regions' candidate sets, so the POOLED candidate
          DENOMINATOR double-counts them. A pre-existing region-DEFINITION property,
          not a scanner defect; it affects the denominator, NOT the 15 findings (both
          regions carry 0 undefined rows); and it is present on the SAME basis in the
          1,412,356 from which 353,089 is derived, so the prediction is consistent
          with it rather than contradicted by it.
       2. The scanner's denominator is pre-`--mac 1` / pre-`--exclude` while the
          panel's LD matrix is post-. ANY fraction computed from these counts MUST
          name its denominator; none of them is a panel prevalence.
       3. The residual of THIS plan's own code fix: early-exit paths (missing bfile
          component, `no windows selected`, duplicate region_id, empty
          `--region-ids`) return 2 BEFORE any write, so a stale artifact at the
          output path survives them. Closed by the runbook's STEP 2b ROTATE plus the
          STEP 3 pre-flight existence guard -- NOT by the code. State it plainly.
       4. Declined from the as-received review, with a one-line reason each:
          positional-vs-header manifest parse (MEDIUM -- the checked-in manifest has
          the expected column order, MEASURED) and the iterator-level whitespace/case
          alias duplicate guard (LOW -- an API-only path, not on the runbook's
          route). Point to
          `.planning/quick/260828-uej-make-the-re-run-safe-to-fire-replace-ste/260828-uej-CODEX-REVIEW-as-received.md`.
       CITE the already-recorded pair-level 5-rows-vs-3-pairs undercount at its
       existing location; do NOT duplicate it.

    D. THE ARITHMETIC ENFORCER (one new test): parse the two added numbers out of
       section (e) and assert `wc == rows + 1` AND `rows * 4 == 1412356`, and that
       `1412356` still appears in (b1) so the two sections cannot drift apart. RED
       mechanism, to be observed: change either number in the doc and the test fails.

    E. STATE.md. Append a row for this quick task ONLY IF
       `git diff --stat .planning/STATE.md` shows no FOREIGN in-flight edit from
       another terminal (there was one at session start). If a foreign edit is
       present, leave STATE.md untouched and say so explicitly in the SUMMARY --
       never stage another terminal's work (`feedback_multi_terminal_staging`).

    F. THE FULL SUITE, ONCE, AND THE COMPONENT-EXACT RECONCILIATION. Run all of
       `tests/m3` (allow >= 1,200,000 ms). Then
       `git checkout -- tests/m3/sparse_parent_benchmark.tsv` -- restore, NEVER
       stage. Reconcile: `1122 + N == passed`, skipped STILL 33, failed 0, with
       `N` derived by NAMING every added test (expected 12: 5 from T1, 3 from T2,
       3 from T3, 1 from T4) and cross-checked against the single-file control
       (`101 + N`). An unreconciled delta or a new SKIP is a BLOCKER, not a rounding
       difference.

    COMMIT (explicit paths only):
    `docs(quick-260828-uej): T4 -- PRE-REGISTER the derived POOLED candidate rows 353089 (= 1,412,356 / 4, exact) and wc -l 353090 BEFORE the re-run, reconcile the two claims the write-then-reconcile change made stale, and record the residual denominator caveats that are NOT being fixed`
  </action>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_pairwise_completeness_scan.py -q 2>&1 | tail -3</automated>
    Expect `113 passed` (112 + 1 arithmetic enforcer), 0 failed, 0 skipped.

    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3 -q 2>&1 | tail -3; git checkout -- tests/m3/sparse_parent_benchmark.tsv; git status --porcelain tests/</automated>
    Expect `1134 passed, 33 skipped` (1122 + 12), 0 failed. Then
    `git status --porcelain tests/` must print NOTHING. Allow >= 1,200,000 ms.

    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git diff --stat e6f4f79 HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py src/python/aou_ld_panel.py .planning/amendments/; git log --oneline e6f4f79..HEAD</automated>
    The frozen-surface diff must be EMPTY. The log must show exactly the four task
    commits, on `m3-W2-aou-deltas`, and nothing else.
  </verify>
  <done>
    Section (e) carries `POOLED candidate rows: 353089` and `wc -l: 353090` as
    derived-before-the-run, with the exact-division derivation and the non-integral
    EUR corroboration shown; 15 / 13 / 10-3 and the histogram are byte-unchanged.
    The two stale claims are reconciled; the historical records are not. The four
    residuals are recorded with reasons. The arithmetic enforcer holds the two new
    numbers to `wc == rows + 1` and `rows * 4 == 1412356`. The full suite is
    reconciled component-exact (`1122 + 12`), skips still 33,
    `sparse_parent_benchmark.tsv` restored and never staged. Nothing was fired.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| runbook text -> in-perimeter operator | An agent/operator executes the paste literally; a wrong gate or a missing rotate becomes a wrong NUMBER in a public pre-registration |
| prior run's artifacts -> this run's read path | `/home/jupyter/occ_measure/pcs_pairs.tsv` is untrusted input to the operator's `wc -l` |
| `--region-ids` / `--out` argv -> `main()` | Operator-supplied strings that silently change scope or destination |
| this quick's edits -> frozen fire path + posted OSF amendment | A run-safety repair must not move a criterion, a threshold or the public record |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-uej-01 | Spoofing | STEP 0 freshness gate | mitigate | The commit-NAME match is replaced by md5 + byte size + last-touching commit + a POSITIVE behavioural capability check (276/276 through `_read_regions_tsv`); MEASURED: the old gate passed on `769afa6`, the 8x code |
| T-uej-02 | Tampering | stale `pcs_pairs.tsv` at the read path | mitigate | STEP 2b ROTATE to `.STALE.<UTC>` (never `rm`), STEP 3 pre-flight `SystemExit` if the path is occupied, and `write_tsv` now truncating before the reconciliation |
| T-uej-03 | Repudiation | a contaminated artifact reported as a fresh result | mitigate | `ls -l --time-style=full-iso` on the NEW artifacts in the paste-back list; the mtime must post-date the STEP 2b stamp; the 21 ids are NAMED, not counted |
| T-uej-04 | Denial of Service | `--region-ids` that strips to empty | mitigate | Returns 2 before any scan instead of a silent ~13x (21 -> 276 region) cost blow-up |
| T-uej-05 | Information Disclosure | per-sample data crossing the perimeter | accept | Unchanged by this plan: the EGRESS RULE is untouched, the TSV stays in-perimeter, only aggregates and variant IDs cross; no new field is emitted |
| T-uej-06 | Elevation of Privilege | a run-safety repair silently becoming a criterion change | mitigate | `git diff --stat e6f4f79 HEAD` over the four frozen modules and `.planning/amendments/` is EMPTY at every commit; the pre-registered 15/13/10-3 and the histogram are byte-unchanged; only the derived 353089/353090 is ADDED |
| T-uej-07 | Spoofing | a green test that was never seen red | mitigate | Every new assertion is seen RED first; the two scratch mutations (`: {missing}`, `_tsv_field.strip()`) are observed, reverted, and md5-verified; the flag-absent path is kept green as the negative control |
| T-uej-08 | Tampering | the shared GPFS tree / another terminal's STATE.md edit | mitigate | Explicit paths at every commit; STATE.md appended only if no foreign in-flight edit; `sparse_parent_benchmark.tsv` restored, never staged |
</threat_model>

<verification>
1. The STEP 0 gate's own capability block, EXECUTED here, prints `manifest windows: 276 distinct region ids: 276` + `CAPABILITY CHECK PASSED`.
2. No commit-subject string gates anything; the gate is md5 + size + last-touching commit + behaviour, with a regeneration recipe and an enforcer that recomputes the hash at call time.
3. `text.count("--ancestry") == 0` on the runbook still holds; all five pre-existing runbook pins are green.
4. The ROTATE heading sits between STEP 2 and STEP 3; its block `mv`s to `.STALE.<UTC>` and never `rm`s; STEP 3 raises `SystemExit` naming the path if either artifact still exists.
5. STEP 0 records `wc -l afr_cohort.bim` (EXPECT 20767864), the `.bed/.bim/.fam` `ls -l`, `python3 -V`, numpy version -- with the GLOBAL-`.bim`-index rationale.
6. STEP 3 prints all 21 region ids by name; the paste-back list carries them plus `ls -l --time-style=full-iso` on the new artifacts.
7. `main()` writes -> reconciles -> quarantines to `<out>.SUSPECT` (ending `.tsv.SUSPECT`) -> returns 2; a pre-existing `.SUSPECT` is rotated, not clobbered; a pre-seeded junk file at `--out` survives neither path.
8. `--region-ids " , "` returns 2 with no output; the flag ABSENT still scans all regions (control green).
9. `test_region_only_in_the_unrequested_ancestry_raises_naming_the_id` uses `anc_split.tsv`, asserts after the interpolated path, and was OBSERVED RED under the `{missing}` deletion (GREEN under the same mutation before).
10. The composite whitespace parse is pinned through `_read_regions_tsv` with the production divergence MEASURED by ast extraction; the real manifest is asserted to carry 0 padded/quoted ancestry cells.
11. Section (e) adds 353089 / 353090 only; a committed test asserts `wc == rows + 1` and `rows * 4 == 1412356`; 15/13/10-3 and the histogram are byte-unchanged.
12. The two stale claims (code comment :1530 and prereg (b1)) are reconciled; historical quick records are NOT rewritten.
13. The four residuals are recorded with reasons, including this plan's OWN early-exit residual.
14. `tests/m3`: 1134 passed / 33 skipped / 0 failed, reconciled as `1122 + 12` and cross-checked as `101 + 12` on the single-file control; `sparse_parent_benchmark.tsv` restored, never staged.
15. Frozen surfaces empty-diff at every commit; branch `m3-W2-aou-deltas`; explicit paths only.
16. NOTHING FIRED: zero enclave / VM / Dataproc / OSF / `gsutil` / `gcloud` / network contact; $0.
</verification>

<success_criteria>
- An operator following the runbook literally CANNOT run the wrong code undetected (content hash + behavioural capability gate), CANNOT be false-stopped by a commit name, and CANNOT read a stale artifact as a fresh result (ROTATE + pre-flight + write-truncates).
- A reconciliation disagreement costs a rename and an exit code, not ~4h18m of compute and a traceback; nothing plausible-looking survives at `--out`.
- The one false invariant is closed and was seen RED; the one untested composite parse is pinned at the SELECTION layer with its production divergence measured and monitored.
- The pre-registration gains exactly one derived, arithmetically enforced prediction and loses nothing; every claim the code change falsified is corrected in the same commit; every residual that is NOT fixed is written down with a reason.
- Every new assertion has a stated, reachable way to fail, and both scratch mutations were observed and reverted.
- `tests/m3` 0 failed, skips 33, delta reconciled component-exact two independent ways. Frozen surfaces and the posted OSF amendment byte-unchanged. Nothing fired.
</success_criteria>

<output>
After completion, create
`.planning/quick/260828-uej-make-the-re-run-safe-to-fire-replace-ste/260828-uej-SUMMARY.md`.

It MUST contain: the verbatim RED output for every new assertion before its fix;
the two scratch-only negative-control observations (`: {missing}` deletion --
RED after the repair, and the recorded GREEN-before observation that proves it was
a false invariant; `_tsv_field.strip()` removal) with the md5-restored proof; the
POST-Task-1 md5 / byte size / last-touching commit that the STEP 0 gate now pins;
the verbatim output of the gate's capability block executed locally; the
component-exact suite reconciliation naming every added test with the `1122 + N`
and `101 + N` arithmetic; the frozen-surface empty-diff output; whether STATE.md
was appended or deliberately left to another terminal; and an explicit statement
that THE RE-RUN HAS NOT HAPPENED, that the 353089 / 353090 prediction was recorded
BEFORE it, and that nothing was fired ($0).
</output>
