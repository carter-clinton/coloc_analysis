---
task: quick-260831-kw8
verified: 2026-08-31T21:56:00Z
status: passed
score: 19/19 must-haves verified (1 with an explicitly accepted, self-invalidating deviation)
overrides_applied: 0
human_verification: []
---

# quick-260831-kw8: Close Seth's brief-blind review — Verification Report

**Task goal:** close a brief-blind external review that found two real defects in
`src/python/pairwise_completeness_scan.py` (already_occluded is ANCHOR-RELATIVE,
not the `--exclude` side; the invariant party is the DELETION) via a post-hoc
panel-wide reclassifier needing no re-run, a corrected/enforced semantics, a
staged (not fired) same-position probe, and an honest record — without moving
pre-registered numbers or disturbing the in-flight ~4h20m sweep.

**Commits:** `bdb0a28` (T1) · `c49e10a` (T2-partial) · `e7b058e` (T3) · `7978ee6`
(T4), on `m3-W2-aou-deltas`, base `ff94bb3`.
**Verified:** 2026-08-31
**Status:** passed
**Method:** all checks are direct re-derivation against the codebase (running
tests, mutating and reverting code to drive gates RED, diffing against named
base commits, running the full suite) — not trust of SUMMARY.md prose.

## Known, accepted deviation (not re-reported as a gap)

Per explicit instruction, T2's prose correction to
`pairwise_completeness_scan.py:122` is **DEFERRED**, not dropped, because a
docstring-only edit moves the scanner's whole-file md5/size and turns the live
runbook's STEP 0 freshness gate RED while a ~4h20m sweep is running against
those pinned bytes. This was independently re-verified below (not merely
trusted) and is treated as accepted, not a gap.

## Goal Achievement — the 8 items specified for this verification

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 1 | Live-fire guard: scanner md5/size machine-checked, not attestation | ✓ VERIFIED | `md5sum src/python/pairwise_completeness_scan.py` = `e03078ff73502c3c877b0d2ebf93941d`, `wc -c` = `73772`. `test_pending_paste_step0_pins_the_scanner_by_a_CURRENT_content_hash` recomputes both **at call time** (`hashlib.md5(scanner.read_bytes())`) and asserts the runbook's STEP 0 gate carries those live values — 1 passed. |
| 2 | No re-run required: AST-check, imports FROZEN detector | ✓ VERIFIED | Independent AST walk of `pcs_panelwide_reclassify.py`: no `BedReader`/`Genotypes`/`MISSING_DOSAGE` import, no `BedReader` name/attr reference, no `read_variant` call, no `.bed` string literal outside a docstring, a `.bim` literal present. Imports confirmed: `from occlusion_span_filter import detect_occluded_variants`, `from pairwise_completeness_scan import DEFAULT_ANCESTRY, TSV_COLUMNS, _read_regions_tsv, iter_bim_windows`. Identity check: `R.detect_occluded_variants is O.detect_occluded_variants` and `R.iter_bim_windows is P.iter_bim_windows` both True. |
| 3 | Behavioural enforcer is real — driven RED, then reverted | ✓ VERIFIED | Mutated `pairwise_completeness_scan.py:617` (`deletion.span_end` → `deletion.span_end + 10`), ran `test_already_occluded_is_anchor_relative_and_is_not_the_exclude_side` → **FAILED** with `AssertionError: ANCHOR-RELATIVE: 1004 < 1008 <= 1005 is FALSE / assert True is False` (matches SUMMARY's quoted RED #2b verbatim). `git checkout --` reverted; md5 back to `e03078ff…`/`73772`; `git status --porcelain` showed only the pre-existing `.planning/STATE.md` modification — nothing else lost. |
| 4 | Self-invalidating deferral note — patch applied, §(1b) test flips RED, reverted | ✓ VERIFIED | `git apply --check` on `.planning/debug/260831-DEFERRED-pairwise-completeness-scan-docstring.patch` → clean. Applied → scanner md5/size moved to `fc1d68dff1f493f6eb57dd427bed638a`/`78843`. `test_the_tool_docstring_carries_the_true_semantics_and_flags_the_scanners_false_claim` → **FAILED**: `"the scanner's false claim is GONE -- the DEFERRAL note in pcs_panelwide_reclassify.py is now STALE..."` (matches SUMMARY's RED-B2 verbatim). Reverted with `git checkout --`; md5 restored to `e03078ff…`/`73772`; test re-run → 1 passed; tree clean except pre-existing STATE.md. |
| 5 | Staged probe is STAGED, NOT RUN | ✓ VERIFIED | `.planning/debug/260831-PENDING-PASTE-POSTHOC-panelwide-reclass-and-samepos-probe.md` line 3 = `STATUS: STAGED — NOT RUN`. No probe/reclassifier output artifacts (`pcs_panelwide_reclass.*`, `samepos_pairs.tsv`, `samepos_summary.json`, `occ_measure/*`) exist anywhere in the repo tree. Both staged argvs parse cleanly against the real `_build_parser()`s (confirmed by running the gate from a file, avoiding a `bash -c` regex-mangling artifact noted independently — see below); the broken-argv negative control correctly raised `SystemExit`. `hl.split_multi_hts` claim is explicitly labelled `INFERENCE FROM DOCUMENTATION, NOT A MEASUREMENT` in the staged doc, the review record, and the probe's own docstring — never presented as measured. |
| 6 | Nothing fired, nothing moved | ✓ VERIFIED | `git diff ff94bb3 HEAD -- .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` → 0 lines. `git diff ff94bb3 HEAD -- .planning/debug/260826-PCS-...-prereg-prediction.md` → 0 lines. `git diff 352ac9e HEAD --` for `occlusion_span_filter.py`, `run_native_ld_panel.py`, `fire_verifier.py`, `aou_ld_panel.py`, `.planning/amendments/` → 0 lines each. |
| 7 | Full `tests/m3` suite | ✓ VERIFIED | Ran to completion (not sampled): **`1167 passed, 33 skipped, 0 failed in 814.43s (0:13:34)`** — exact match to the SUMMARY's claim. `git checkout -- tests/m3/sparse_parent_benchmark.tsv` restored the benchmark artifact the run touches; tree returned to clean (only pre-existing STATE.md modified). Per-file collect: `test_pairwise_completeness_scan.py` 114, `test_pcs_panelwide_reclassify.py` 21, `test_samepos_missingness_probe.py` 11. Reconciles: `1054 + 114 + 21 + 11 = 1200 = 1167 + 33`. |
| 8 | Record's honesty | ✓ VERIFIED | `.planning/debug/260831-seth-brief-blind-review-already-occluded-is-anchor-relative.md` carries: the deferral **with its trigger** ("the post-sweep window — once the sweep LANDS and its artifacts are BANKED. Not before."); the byte-proxy gate named a **REPEAT** of `feedback_scope_a_guard_to_the_property_not_a_proxy`, naming the 2026-08-06 precedent explicitly and the scheduled durable fix (docstring-insensitive code hash, to be proven able to fail before trusted); Seth's ±5bp/±50bp prices labelled `SETH-COMPUTED`, `NOT INDEPENDENTLY RE-DERIVED BY US`, with the reason re-derivation wasn't attempted (needs in-perimeter region-1 `.bim`); the 0.0078/0.014 ratio labelled `DIRECTIONALLY CONSISTENT, NOT EVIDENCE`, citing the exact 2026-08-18 Seth quote (verified against the source file — quote matches verbatim) as the governing, more-conservative ruling. No wording found anywhere presenting the Hail inference as a measurement. |

## Independent re-derivations beyond the 8 specified items

| Check | Result |
|---|---|
| All 8 SUMMARY-claimed key-files exist on disk | ✓ confirmed individually |
| All 4 SUMMARY-claimed commits exist in `git log` | ✓ confirmed individually (`bdb0a28`, `c49e10a`, `e7b058e`, `7978ee6`) |
| T1 known-answer + monotonicity + reconciliation tests | `pytest tests/m3/test_pcs_panelwide_reclassify.py -q` → 21 passed |
| T3 probe tests (co_called/complementary/mixed known answers + negative control) | `pytest tests/m3/test_samepos_missingness_probe.py -q` → 11 passed; probe contract check prints `PROBE CONTRACT OK; labels ['co_called', 'complementary', 'mixed']` |
| T2 rename-decline structural enforcer | `test_the_already_occluded_rename_is_declined_while_the_sweep_artifact_contract_stands` → 1 passed |
| Prereg enforcer untouched-and-green | `test_prereg_pooled_row_prediction_reconciles_with_the_afr_pass` → 1 passed |
| Freeze-pin + frozen-detector suites green | `test_source_freeze_pins.py` + `test_occlusion_span_filter.py` → 57 passed, 2 skipped |
| T1's post-hoc-only AST gate driven RED independently | Inserted `from pairwise_completeness_scan import BedReader` into `pcs_panelwide_reclassify.py` → gate raised `AssertionError: GENOTYPE SURFACE IMPORTED: BedReader` (matches SUMMARY exactly); reverted; gate green again; tree clean |
| Key link: `pad_bp=0` + `TSV_COLUMNS` strict-equality check present in reclassifier | Confirmed by grep: `pad_bp=0` comment naming `run_native_ld_panel.py:851-878`; header parsed via `TSV_COLUMNS` with RAISE on mismatch |
| Audit-table spot checks (T2 §audit) | `:122` false sentence still present (deferred, as claimed); `:1149` "already covers"/`:446` `_pair_key` docstring content match the audit table's verdicts exactly |
| Scanner test-count delta explained | Plan specified 3 new scanner tests; only 2 landed (the docstring-absence test was correctly *not* added because the docstring itself was not changed under the deferral) — consistent, not a gap |

## Minor discrepancies noted (non-blocking)

1. **SUMMARY quotes "1 failed, 171 passed, 2 skipped in 4.47s"** for the
   scanner+freeze-pins+occlusion-filter suites with the parked patch applied.
   Independently re-running that exact scenario twice gives **"1 failed, 170
   passed, 2 skipped"** (baseline unpatched is 171 passed/2 skipped = 173 total;
   patched is 170 passed + 1 failed + 2 skipped = 173 total — arithmetically
   self-consistent). The SUMMARY's "171" appears to be a copy-paste artifact
   from the unpatched baseline rather than a re-measurement. The substantive
   claim under test — **exactly one failure, and it is the STEP 0 gate** — is
   independently reconfirmed true both times. Does not affect the deferral's
   validity or the goal.
2. **`.planning/STATE.md`'s current (uncommitted) ★RESUME★ header** says "three
   commits" (`bdb0a28`, `c49e10a`, `e7b058e`) even though a fourth, `7978ee6`
   (T4), has landed; the body text does reflect T4's deliverables (staged doc,
   full 1167/33/0 suite result) even though the header enumeration is stale.
   STATE.md is explicitly left modified-and-uncommitted for the orchestrator's
   docs commit per the executor contract, so this is expected to be finalized
   in that commit, not a functional gap.
3. **`bash -c`-embedded regex mangling.** Independently reproduced the same
   class of issue the SUMMARY flags (embedding the T4 argv-extraction regex
   directly in a `Bash(python -c "...")` call silently converted `\` + newline
   into literal `\n` tokens and broke argv parsing). Writing the identical
   script to a file and running it produced the correct result. This confirms
   the SUMMARY's own noted in-session deviation and is a property of the shell
   invocation, not of the shipped code — not a gap.

## Requirements Coverage

This is a quick task (not a phase); the 15 requirement IDs in the PLAN
frontmatter (`PCS-PANELWIDE-*`, `PCS-DOCSTRING-*`, `PCS-RENAME-*`,
`PCS-SAMEPOS-*`, `PCS-REVIEW-*`, `PCS-PREREG-*`, `PCS-FROZEN-*`, `PCS-SUITE-*`,
`PCS-NOTHING-FIRED`) are task-local and are not present in the global
`.planning/REQUIREMENTS.md` (expected for quick tasks). Coverage is assessed via
the must-haves table above; every requirement maps to a verified truth.

## Anti-Patterns Found

None. Scanned `pcs_panelwide_reclassify.py` and `samepos_missingness_probe.py`
for `TODO`/`FIXME`/`PLACEHOLDER`/empty-return patterns — no matches. Both files
substantially exceed their `min_lines` requirements (707 vs 200, 436 vs 180;
their test files 958 vs 250 and 328 vs 200).

### Human Verification Required

None. Every must-have in this task is machine-checkable (test suites, AST
gates, byte-identical diffs against named commits, negative controls), and
every one was independently re-derived above rather than trusted from the
SUMMARY.

### Gaps Summary

No gaps. All 8 explicitly specified verification items pass on independent
re-derivation, all must-haves in the PLAN frontmatter are satisfied (with the
T2 prose-deferral treated as an accepted, disclosed, self-invalidating
deviation per explicit instruction rather than a gap), the full suite is
green at exactly 1167/33/0, nothing fired, the in-flight sweep's target files
are byte-identical to their pre-task state, and the pre-registered numbers
(15/13/10-3, offset histogram) are unmoved because the file carrying them was
never edited.

---

_Verified: 2026-08-31_
_Verifier: Claude (gsd-verifier)_
