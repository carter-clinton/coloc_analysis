---
task: quick-260828-uej
verified: 2026-08-29T04:23:29Z
status: passed
score: 16/16 must-haves verified
overrides_applied: 0
re_verification: no (initial verification)
---

# quick-260828-uej: Make the re-run SAFE TO FIRE — Verification Report

**Task goal:** close the five-way adversarial review's six RUN-safety findings
(behavioural freshness gate, artifact rotation, false invariant, composite-parse
pin, empty-`--region-ids` error, write-then-reconcile-then-quarantine) without
firing anything.

**Verified:** 2026-08-29T04:23:29Z
**Status:** passed
**Method:** every claim below was RE-DERIVED against the live tree — the scanner
was mutated and restored four separate times, the runbook was mutated and
restored four separate times (all four `rm` forms + the collision-word control),
the prereg record was mutated and restored once, and the **full `tests/m3` suite
was re-run live** (not taken from the SUMMARY) to completion: `1133 passed, 33
skipped, 0 failed in 811.96s`, matching the SUMMARY's claim exactly.

## Goal Achievement

### Observable Truths (from PLAN frontmatter `must_haves.truths`)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | STEP 0 stops on wrong code by MEASUREMENT, not a commit name | ✓ VERIFIED | Old `quick-260825-qpf` paragraph is GONE (confirmed by diff: only that paragraph + STEP3 preamble/args lines removed). Gate now: `git status --porcelain` EMPTY check + md5/size (recomputed live: `e03078ff73502c3c877b0d2ebf93941d` / `73772`, matches gate text) + `git log -1` naming `cb199b6` (matches) + positive capability check (`_read_regions_tsv(...)` → 276/276, executed live, printed `CAPABILITY CHECK PASSED`). WHY paragraph cites `769afa6` MEASURED 1 / `352ac9e` MEASURED 0 — reproduced independently below. |
| 2 | Gate text never names `--ancestry`, says so inline | ✓ VERIFIED | `text.count("--ancestry")` on the whole runbook = **0** (independently computed). `test_pending_paste_step3_carries_no_ancestry_flag_so_the_default_is_load_bearing` present and green. |
| 3 | Stale artifacts ROTATED (never deleted), sweep refuses if still present | ✓ VERIFIED | `=== STEP 2b — ROTATE ===` sits between STEP 2 and STEP 3 (heading-index order confirmed: STEP 0 < STEP 1 < STEP 2 < STEP 2b < STEP 3 < EGRESS). Uses `mv -v ... .STALE.$STAMP`, never `rm`. STEP 3 python heredoc opens with an `os.path.exists` pre-flight raising `SystemExit` naming both paths. |
| 4 | STEP 0 records the `.bim` the banked pair_keys are relative to, plus interpreter | ✓ VERIFIED | `wc -l ... EXPECT 20767864` present; `.bed/.bim/.fam` `ls -l --time-style=full-iso` present; `python3 -V` / numpy version present; GLOBAL-index rationale stated. |
| 5 | The 21 region ids are NAMED, not counted | ✓ VERIFIED | STEP 3 heredoc: `for rid in ids: print("  region id:", rid)` present, plus the existing count line. Paste-back list extended with `ls -l --time-style=full-iso` on both new artifacts. |
| 6 | TSV written before reconciliation; disagreement quarantines instead of traceback | ✓ VERIFIED | Read `main()` source directly: `write_tsv(...)` and summary write occur **before** `pooled_candidate_rows = sum(...)`. On disagreement: `_quarantine_output` (string concatenation `Path(str(path)+".SUSPECT")`, never `with_suffix`), one `ERROR:` line naming both numbers + `n_candidate_rows` + quarantine path, `return 2`. Reproduced live via `test_pooled_candidate_rows_disagreement_quarantines_the_output_and_returns_2` (passed) and by reading `_quarantine_output`'s docstring/body directly. |
| 7 | A pre-existing `.SUSPECT` is rotated, never clobbered | ✓ VERIFIED | `_quarantine_output`: `if suspect.exists(): suspect.replace(Path(str(suspect)+"."+stamp))` before `Path(path).replace(suspect)`. `test_a_preexisting_suspect_is_rotated_not_clobbered` passed live. |
| 8 | Empty-after-strip `--region-ids` is an error, not a silent 276-region scan | ✓ VERIFIED | Code at :1413-1420 (current file) raises `ValueError` inside the existing `try:` when the stripped list is empty; absent flag still means `None` (all regions, unchanged). `test_an_empty_after_strip_region_ids_is_an_error_while_the_absent_flag_still_means_all_regions` passed live. |
| 9 | False invariant closed, observed RED | ✓ VERIFIED (reproduced independently) | Fixture renamed to `anc_split.tsv` (does not contain "eur_only"); assertion scoped to `message.split(str(regions),1)[1]`. **I deleted `: {missing}` from the f-string myself** and re-ran the test: it went RED with the exact message shown in the SUMMARY. Restored, md5 verified `e03078ff73502c3c877b0d2ebf93941d`, test green again. |
| 10 | Composite parse pinned at selection layer, not just predicate | ✓ VERIFIED | `test_composite_whitespace_ancestry_parse_selects_where_production_drops` drives `"  AFR  "` through `_read_regions_tsv` (selects), then ast-extracts `_filter_ancestry` from `run_native_ld_panel.py` at call time via `exec` in an empty namespace (never `import`) and shows production drops it. `test_real_manifest_carries_no_padded_or_quoted_ancestry_cells` monitors the real manifest for 0 such rows. Both passed live. |
| 11 | Prereg gains derived 353089/353090, reconciled by a committed test | ✓ VERIFIED (reproduced independently) | `1,412,356 / 4 = 353,089` exact (recomputed: `353089*4==1412356`, `1412356 % 4 == 0`); `353,089+1=353,090`; EUR's `1,453,157/4=363,289.25` non-integral (recomputed: `1453157 % 4 == 1`). **I mutated the doc's `353090`→`353091` myself**: `test_prereg_pooled_row_prediction_reconciles_with_the_afr_pass` went RED with the exact message shown in the SUMMARY. Restored, md5 verified `de60c957fcf6ddf7713a677570f4cfa1`, test green again. |
| 12 | Three stale RAISES claims reconciled; historical records untouched | ✓ VERIFIED | `git diff 8265507 HEAD` on the scanner shows the stale "runs BEFORE write_tsv" comment gone (grep for "runs BEFORE write_tsv" in current file: 0 hits). Prereg (b1) and (e):~605 both rewritten to the QUARANTINE contract (read directly). `git diff --stat 8265507 HEAD -- .planning/quick/260825-qpf.../ .planning/quick/260826-qq9.../ .planning/quick/260825-ngh.../` = **EMPTY** (0 lines) — historical SUMMARY/VERIFICATION records genuinely untouched. See Anti-Patterns for one **out-of-scope** stale cross-reference found elsewhere in the prereg doc. |
| 13 | Residuals recorded with reasons | ✓ VERIFIED | `### RESIDUAL — KNOWN, NOT FIXED, AND WHY` section present with all 4 items: `__subNN` 6,000,000 bp overlap (both region pairs' bounds match MEASURED values exactly), pre-mac/pre-exclude denominator caveat, this plan's own early-exit residual, and the CODEX-REVIEW declined items table (file exists, tracked, 6079 B). |
| 14 | Nothing fired | ✓ VERIFIED | `git diff 8265507 HEAD` over all touched files grepped for `hl.`, `dataproc`, `Workbench`, `researchallofus`, `gs://`, `bigquery`, `gsutil`, `gcloud`, `curl`, `wget`, `ssh`, ip/socket calls — **zero hits** in added lines. Only 4 files touched across 4 commits (scanner, test file, runbook, prereg doc) — all doc/test-only except the scanner's `main()` logic, which runs against synthetic tmp fixtures in tests, never `/home/jupyter/*`. |
| 15 | No criterion/threshold/policy moved (frozen surfaces) | ✓ VERIFIED | `git diff --stat 352ac9e HEAD -- occlusion_span_filter.py run_native_ld_panel.py fire_verifier.py aou_ld_panel.py .planning/amendments/` = EMPTY (also checked vs task base `8265507` — EMPTY). 15/13/10-3 and histogram `{-14:1,-9:1,-6:1,-3:1,-1:1,0:10}` present unchanged in current HEAD; removed-lines diff of the prereg doc contains only the 3 stale RAISES sentences, no digits from the frozen prediction. |
| 16 | Suite re-baselined component-exact | ✓ VERIFIED (full suite re-run live) | `tests/m3` **1133 passed, 33 skipped, 0 failed in 811.96s** (independently re-run, not taken from SUMMARY). `1122+11=1133` ✓, single-file control `101+11=112` ✓ (independently collected: scanner file now has 112 items). Non-scanner collect-only independently re-collected: **1054** (exact match). Name-level diff (`comm` on sorted `def test_` names, e6f4f79 vs HEAD): **12 added, 1 removed** (the 1 removed is exactly `test_pooled_candidate_rows_reconciliation_raises_when_the_bases_disagree`, renamed to `..._disagreement_quarantines_the_output_and_returns_2`) → net **+11**, matching the plan's own permitted-deviation clause. `sparse_parent_benchmark.tsv` was perturbed by the run (confirmed) and restored via `git checkout --` (confirmed clean after). |

**Score:** 16/16 truths verified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `src/python/pairwise_completeness_scan.py` | write-then-reconcile + `.SUSPECT` quarantine + return 2; empty-region-ids error; contains "SUSPECT"; ≥1400 lines | ✓ VERIFIED | 1661 lines; `SUSPECT` appears 8x; code read directly, matches spec exactly; wired via 112 passing tests that import and exercise it. |
| `tests/m3/test_pairwise_completeness_scan.py` | RED-first coverage per plan; contains "anc_split"; ≥3400 lines | ✓ VERIFIED | 4135 lines; `anc_split` appears 2x; all named tests present and green; 4 negative controls independently re-run RED, then restored green. |
| `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` | behavioural gate, ROTATE, field records, named ids, pre-flight; contains ".STALE." | ✓ VERIFIED | `.STALE.` appears; structure confirmed by direct read + 3 heading-order checks + 4 independent `rm`-form mutation tests. |
| `.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md` | derived 353089/353090, reconciled claims, RESIDUAL section; contains "353089" | ✓ VERIFIED | `353089` appears; all content confirmed by direct read; one out-of-scope stale test-name cross-reference noted below (does not affect any must-have). |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| STEP 0 gate | scanner md5+size | test recomputing hash+size at call time | ✓ WIRED | `test_pending_paste_step0_pins_the_scanner_by_a_CURRENT_content_hash` uses `hashlib.md5` genuinely at call time (not a frozen literal) — confirmed by appending a byte to the scanner and observing the test go RED with the *new* md5 named in the failure message, then restoring. |
| STEP 0 capability EXPECT | `_read_regions_tsv(...)` | test computing 276/276 at call time | ✓ WIRED | `test_pending_paste_step0_capability_numbers_are_the_real_manifest_numbers` present and green; independently ran the gate's own capability block live: `manifest windows: 276 distinct region ids: 276` / `CAPABILITY CHECK PASSED`. |
| `main()` reconciliation | `<out>.SUSPECT` quarantine + return 2 | monkeypatched off-by-one summary, exercised end-to-end | ✓ WIRED | `test_pooled_candidate_rows_disagreement_quarantines_the_output_and_returns_2` passed live; source code confirms the write→reconcile→quarantine→return-2 order directly. |
| prereg (e) 353089/353090 | prereg (b1) 1,412,356 | test parsing both, asserting `wc==rows+1` and `rows*4==1412356` | ✓ WIRED | `test_prereg_pooled_row_prediction_reconciles_with_the_afr_pass` present; independently mutated `353090`→`353091` in the doc and observed the exact RED failure message, then restored (md5-verified). |

### Behavioural Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Gate's own capability block runs against shipped tree | inline `python3` block from the runbook, executed verbatim | `manifest windows: 276 distinct region ids: 276` / `CAPABILITY CHECK PASSED` | ✓ PASS |
| `--ancestry` forbidden-token pin | `text.count("--ancestry")` over the whole runbook | `0` | ✓ PASS |
| Rotate-block `rm` enforcer, direction 1 (4 real-deletion forms) | insert `rm -f <path>`, `rm <path>`, `/bin/rm "$f"`, `rm -rf $f` into ROTATE block one at a time, re-run enforcer | all 4 forms → test FAILED (RED) | ✓ PASS |
| Rotate-block `rm` enforcer, direction 2 (collision words) | insert `confirm`/`warm`/`storm`/`term`/`form`/`norm`/`alarm` prose into ROTATE block | `1 passed` (GREEN, correctly not a false positive) | ✓ PASS |
| Content-hash enforcer recomputes, not frozen | append a comment line to the scanner, re-run enforcer | test FAILED naming the NEW md5 (`44c54677...`), not the old one | ✓ PASS |
| False-invariant closure | delete `: {missing}` from the f-string, re-run repaired test | FAILED with `assert 'eur_only' in " for ancestry 'AFR'"` | ✓ PASS |
| Prereg arithmetic enforcer | change `353090`→`353091` in doc, re-run enforcer | FAILED: `353091 == (353089 + 1)` is False | ✓ PASS |
| Full `tests/m3` suite | `pytest tests/m3 -q` (full, live, ~811s) | `1133 passed, 33 skipped, 4 warnings in 811.96s` | ✓ PASS |

All mutations were reverted and md5-verified equal to their pre-mutation values before proceeding; `git status --porcelain` was empty on every touched file after every restore.

### Requirements Coverage

This is a `/gsd-quick` task; `.planning/REQUIREMENTS.md` does not track the `PCS-*` requirement IDs declared in the PLAN frontmatter (expected — quick tasks self-contain their requirements in the plan, unlike phase work). All 13 declared requirement IDs (`PCS-RUNBOOK-BEHAVIOURAL-FRESHNESS-GATE` through `PCS-NOTHING-FIRED`) map 1:1 onto the 16 observable truths verified above; none are orphaned or unaddressed.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md` | 379 | The "(b) ROOT CAUSE" fix-table still cites the enforcer by its **old** name, `test_pooled_candidate_rows_reconciliation_raises_when_the_bases_disagree`, which T1 renamed to `test_pooled_candidate_rows_disagreement_quarantines_the_output_and_returns_2` | ℹ️ Info | Cosmetic only — not one of the plan's three explicitly-scoped stale RAISES claims (code comment :1530, prereg (b1), prereg (e):~605), all three of which ARE correctly reconciled. The underlying enforcer still exists and still functions (verified live). An operator following this specific table row to find the test by name would not find it under that name. Does not affect run safety, does not violate any must-have, and is not one of the six findings this task was scoped to close. Recommended as a low-priority follow-up doc fix, not a blocker. |

No blocker or warning-level anti-patterns found. No placeholder/stub/TODO markers, no empty-return stubs, no console-log-only implementations in any of the 4 touched files.

### Human Verification Required

None. Every claim in this task is a text/code property that was mechanically re-derivable and was, in fact, re-derived live (hash recomputation, mutation-observe-restore cycles ×9, and a full live 811.96s test-suite run). The runbook text itself targets a future in-perimeter VM session that this task explicitly does not fire — its correctness is fully covered by the committed enforcer tests, all of which were re-run and independently confirmed here.

### Gaps Summary

No gaps. All 16 observable truths derived from the PLAN's `must_haves.truths`, all 4 required artifacts, and all 4 key links were independently verified against the live codebase — not merely trusted from the SUMMARY. Nine separate mutate-observe-restore cycles were performed independently (scanner content-hash enforcer, false-invariant closure, prereg arithmetic enforcer, and four ROTATE `rm`-detection forms plus the collision-word control) and every one matched the SUMMARY's claimed RED/GREEN behavior exactly. The full `tests/m3` suite was re-run live to completion (811.96s) rather than trusted from the SUMMARY log, and reproduced `1133 passed / 33 skipped / 0 failed` exactly. Frozen surfaces are empty-diff at both `352ac9e` and the task's own base `8265507`. Historical quick-task records (`260825-qpf`, `260825-ngh`, `260826-qq9`) are byte-for-byte untouched. Nothing was fired: zero cloud/enclave/network contact appears anywhere in the diff, and the working tree ends in the identical state it started in plus the two intentional additions (unstaged `STATE.md`, untracked `SUMMARY.md`).

One informational (non-blocking) documentation-drift item was found and is recorded above for optional follow-up; it is outside the plan's explicitly-scoped three stale-claims list and does not affect any must-have.

---

_Verified: 2026-08-29T04:23:29Z_
_Verifier: Claude (gsd-verifier)_
