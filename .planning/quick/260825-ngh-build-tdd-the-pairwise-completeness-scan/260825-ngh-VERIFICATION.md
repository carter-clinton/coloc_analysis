---
phase: quick-260825-ngh
verified: 2026-08-25T18:40:00Z
status: passed
score: 21/21 checks verified
overrides_applied: 0
---

# Quick 260825-ngh: Build + TDD the Pairwise-Completeness Scanner — Verification Report

**Task Goal:** Build + TDD the pairwise-completeness scanner (genotype-only undefined-LD
detector, seek-by-index `.bed` reader, both-sides candidate enumeration, carriers-lost
gradient, egress-clean TSV/summary) plus a written-not-run PENDING PASTE for the 21-region
in-perimeter sweep. INSTRUMENT ONLY — no criterion/threshold/span/NaN-policy change, no
producer change, no result asserted, nothing fired.

**Verified:** 2026-08-25
**Status:** passed
**Mode:** Initial verification (READ-ONLY re-execution; no tracked files edited, no commits)

## Pre-confirmed items (reconfirmed cheaply, as instructed)

| # | Claim | Command | Observed |
|---|---|---|---|
| 1 | Frozen-surface diff empty vs `7b59721` | `git diff --stat 7b59721 HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py .planning/amendments/ \| wc -l` | `0` |
| 2 | Amendment paste block size/md5 (safe two-step file form) | `awk '/PASTE INTO OSF FROM HERE/{f=1;next}/PASTE ENDS HERE/{f=0}f' A > pb.txt; wc -c < pb.txt; md5sum pb.txt` | `22945` B / `13a49f543cabcc27ce9f1e589783c060` |
| 3 | `tests/m3 --collect-only` = 1054 (new file ignored) / 1116 (included) | `pytest tests/m3 --collect-only -q [--ignore=...]` | `1054` / `1116` — exact match |
| 4 | New file alone = 62 passed | `pytest tests/m3/test_pairwise_completeness_scan.py -q` | `62 passed in 0.40s` |
| 5 | 0 re-declared `_COL_*` constants | `grep -cE '^\s*(_COL_CHR\|_COL_ID\|_COL_BP\|_COL_ALT\|_COL_REF)\s*=' src/python/pairwise_completeness_scan.py` | `0` |

## Correctness-of-instrument checks (primary verification effort)

| # | Check | Command / Method | Observed |
|---|---|---|---|
| 1a | Independent hand-built `.bed`: n_samples=6 (not %4==0), 3 variants, all 4 codes, padding bits set to 1 in the last byte | Wrote raw bytes myself (`build_and_check.py`, not reusing test's `_pack_variant`/`_write_bfile` helpers); decoded via `BedReader` | `[2,-1,1,0,2,-1]`, `[1]*6`, `[0]*6` — all exact matches; padding=`0b11` did NOT manufacture phantom dosage values |
| 1b | `variant i` read from `offset = 3 + i*bpv` | Compared `BedReader`'s reads against raw-file seeks at `3+i*bpv` computed independently | Byte-identical at all 3 indices |
| 1c | Bad magic / individual-major / truncated all RAISE | Mutated the hand-built file 3 ways, called `BedReader()` on each | All 3 raised `ValueError` with the expected diagnostic text (magic bytes quoted, "INDIVIDUAL-major" named, size mismatch with expected/actual bytes) |
| 2 | Primary test is `np.unique(dosage[both]).size==1` per member, plus empty-intersection; `test_undefined_without_carriers_subset_of_missing` genuinely proves the proxy would miss it | Read `evaluate_pair` source; hand-recomputed the fixture: `carriers(deletion)=30` (20+10), of which only 10 are in `missing(partner)` — **not** a subset (30≠10) — yet `partner_invariant=True` within the 420-sample intersection (partner constant at value "0"), so `undefined=True` via the property while the shortcut is false | Hand arithmetic matches every asserted value in the test (`n_both_called=420`, `del_carriers_marginal=30`, `del_carriers_retained=20`, `lost_frac=10/30`); proxy demonstrably false, property demonstrably true |
| 3 | Partial-confounding case is DEFINED with hand-checkable gradient | Re-derived `test_partial_confounding_is_DEFINED_and_the_gradient_sees_it` from its own joint table by hand: total 7313; `n_both_called=7024+82+5=7111`; del values {0,1} in intersection → variable, not invariant; partner values {0,1} in intersection → variable; `del_carriers_marginal=87`, `retained=5`, `lost=82`, `lost_frac=82/87=0.94253≈0.9425`; `confounding_pattern="partial"` | All hand-computed values match the test's assertions exactly; `undefined=False` correctly reproduces "plink would return a finite r that no NaN check sees" |
| 4 | Offsets swept both sides, one signed convention; `offset==0` ≠ `already_occluded` | Hand-traced `span_offset`/`enumerate_candidates` against `test_offset_zero_and_already_occluded_are_not_the_same_predicate` and `test_enumerate_emits_both_sides_with_signed_offsets`: co-located partner (pos==del.pos) → offset 0, `already_occluded=False` (strict left bound `d.pos<v.pos` fails at equality); interior partner (pos=1001) → offset 0, `already_occluded=True`; upstream partner → negative offset | Matches code and doc convention exactly; the two predicates provably disagree on the co-located row |
| 5 | Egress recursive guard with cardinality bound rejects a per-sample map hidden in a distribution | Re-ran `test_egress_assertion_catches_a_per_sample_field` in isolation, verbose | `PASSED` — 3rd negative control (`undefined_offset_histogram` polluted with 7313 entries) raises `AssertionError: ... per-sample scale` as claimed |
| 6 | No result asserted anywhere (prevalence/boundary-width/tail number as a finding) | `grep -rn '0\.9425'` across module/tests/paste/SUMMARY; `grep -niE '(prevalence\|boundary width) (is\|of\|=\|:)'` across all four; grep module docstring, PENDING PASTE, STATE.md, HANDOFF.json, SUMMARY for "OPEN" | `0.9425` appears ONLY in the test file as a synthetic fixture oracle (4 occurrences, all in-test with `#` comments citing the derivation); no sentence anywhere states a prevalence/width/tail number as a finding; all three OPEN questions are stated OPEN, verbatim, in the module docstring (`"Three things are OPEN and are NOT answered here"`), `.planning/debug/260825-PENDING-PASTE-...md` (§"WHAT THIS DOES NOT DECIDE"), `.planning/STATE.md` (2026-08-25 entry), `.planning/HANDOFF.json` (`resume_on_reconnect[0]`), and the SUMMARY ("WHAT THIS DOES NOT ESTABLISH" §1-3) |
| 7 | PENDING PASTE: written not run; 00057 discard-all cross-check with 71048/871/offset+1/both variant IDs; targets pre-committed 21-region sample and `/home/jupyter/afr_cohort`; aggregate-egress-only; VM start/stop is Carter's; agent never fires | Full read of `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md`; `grep -c` for each token | `71048`✓ `871`✓ `20394741`✓ `20394743`✓ (both variant IDs present); STEP 1 explicitly says "DISCARD ALL RESULTS" on mismatch and runs alone before STEP 2; `/home/jupyter/afr_cohort` and `occ_measure_sample.tsv` present; "EGRESS RULE" section states aggregate-counts-only, full TSV stays in-perimeter; "OPERATIONAL NOTES" states VM start/stop is Carter's and "An agent NEVER fires anything billable" |
| 8a (fresh control 1) | Extra CLI-flag sanity: every flag literal used in the PENDING PASTE's actual commands exists in the shipped `argparse` parser (the bare `--r`/`--ff-only`/`--oneline` hits are prose/git, not scanner flags) | Extracted `--[a-z-]+` tokens from the paste, cross-referenced against `pcs._build_parser()._actions` | All real scanner flags (`--bfile-prefix --chr --from-bp --out --region-id --region-ids --regions-tsv --summary --to-bp --window-bp`) present in parser; both embedded `python3` heredocs `py_compile` cleanly |
| 8b (fresh control 2, primary) | Minor-allele tie boundary (`af_a1 == 0.5` exactly) matches the documented `<=0.5 → A1 minor` convention, and is a genuinely discriminating boundary (not incidentally satisfied by both branches) | Built a fixture with 5×dosage-2 + 5×dosage-0 (af_a1 exactly 0.5) and compared the shipped `_minor_allele_carriers` against a deliberately-perturbed `<0.5` (strict) variant | Shipped code: carriers = the 5 dosage-2 samples (A1 minor, matches docstring). Perturbed `<` variant: carriers = the OTHER 5 samples (A2 minor). The two masks are provably different — the `<=` boundary is load-bearing, not cosmetic, and the shipped code is on the documented side of it. (No test in the suite exercises this exact tie point; the `window_bp < 0` raise in `enumerate_candidates` is likewise coded but not directly unit-tested — neither is a plan must-have, noted as a minor observation, not a gap.) |
| 9 | Full regression: `tests/m3` = 0 FAILED, skips stay at 33 | `pytest tests/m3 -q -rs` (independent full run, not trusting the SUMMARY) | `1083 passed, 33 skipped, 4 warnings in 819.02s (0:13:39)` — exact match to SUMMARY's claimed baseline; 0 failed |

## Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `src/python/pairwise_completeness_scan.py` | Instrument, ≥400 lines, `TSV_COLUMNS` present, imports `occlusion_span_filter` | ✓ VERIFIED | 1065 lines; `occlusion_span_filter` imported once; 0 forked `.bim` constants |
| `tests/m3/test_pairwise_completeness_scan.py` | RED-first suite, ≥500 lines, `MIRRORS_A_MEASURED_CASE` present | ✓ VERIFIED | 1850 lines; `MIRRORS_A_MEASURED_CASE` occurs 2×; 62/62 passing |
| `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` | In-perimeter block, ≥80 lines, contains `71048` | ✓ VERIFIED | 174 lines; all required tokens present; discard-all-on-mismatch rule present; never-run |
| `.planning/HANDOFF.json` | Corrected suite baseline, resume entry naming instrument BUILT-AND-UNRUN, 3 questions OPEN | ✓ VERIFIED | `suite_baselines["tests/m3"]` REPLACED (not appended) with component-exact reconciliation (1021+62=1083, 1054+62=1116); resume entry #0 states instrument built/untested-on-data, all 3 questions OPEN |

## Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `occlusion_span_filter.py` (`_COL_*`/`parse_bim_row`/`load_bim_rows`) | `pairwise_completeness_scan.py` | import binding, object identity | ✓ WIRED | `pcs.parse_bim_row is osf.parse_bim_row` asserted and passing; textual guard for 0 forked constants passing |
| plink1 `.bed` byte layout | `BedReader.read_variant` | `seek(3+index*bpv)+read(bpv)` | ✓ WIRED | Independently reproduced with a hand-built file outside the test helpers (Check 1a/1b) |
| measured `m2_region_00057` table | `MIRRORS_A_MEASURED_CASE` fixture | 1/10-scale mirror, cited not re-derived | ✓ WIRED | Hand-recomputed from the fixture's own joint table; matches halt record's cited numbers exactly |
| `pairwise_completeness_scan.py` | `PENDING-PASTE...md` | STEP 0 pull+SHA, STEP 1 cross-check discard-all | ✓ WIRED | Read in full; discard-all-on-mismatch and freshness gate both present |

## Requirements Coverage

All 8 declared requirements (`PCS-BED-READER-FAIL-CLOSED`, `PCS-CANDIDATE-ENUMERATION-BOTH-SIDES`, `PCS-PAIRWISE-PROPERTY-DIRECT`, `PCS-GRADIENT-PARTIAL-CONFOUNDING`, `PCS-CLI-EGRESS-CLEAN-SUMMARY`, `PCS-PENDING-PASTE-00057-CROSSCHECK`, `PCS-FROZEN-SURFACES-UNCHANGED`, `PCS-SUITE-REBASELINE`) are SATISFIED by the checks above. No orphaned requirements found (this is a quick task, not a phase with a separate REQUIREMENTS.md mapping).

## Anti-Patterns Found

None. No TODO/FIXME/placeholder/HACK strings in the module. No stub returns, no empty handlers, no hardcoded-empty egress fields. The one honestly-disclosed "green on arrival" test (`test_default_window_bp_is_25_and_is_a_measurement_window`) is explicitly reported as such in the SUMMARY and backstopped by perturbation P10 — not hidden, not a blocker.

## Human Verification Required

None. Every claim in this task is programmatically checkable (constants, byte layout, arithmetic, egress shape, file existence/content) and was checked.

## Gaps Summary

No gaps found. Two minor, non-blocking observations (not must-haves, not requested checks, recorded for completeness):
- The `af_a1 == 0.5` exact-tie boundary in `_minor_allele_carriers` and the `window_bp < 0` raise in `enumerate_candidates` are correctly implemented (verified by my own fresh negative controls / code reading) but have no dedicated unit test in the shipped suite. Neither affects the primary `undefined` property (which is what the halt's mechanism depends on) — both only affect secondary gradient/CLI-input-validation paths. Not a plan must-have; not blocking.
- Running the full `tests/m3` suite (done for this verification) dirties `tests/m3/sparse_parent_benchmark.tsv` (timing columns only) exactly as the SUMMARY's Deviation #7 disclosed; restored via `git checkout` after verification so the tree is clean.

Every plan must-have was independently re-derived or re-executed rather than trusted from the SUMMARY, including: the frozen-import discriminator (functions, not interned small ints), the primary-property-vs-proxy distinction (hand-verified on a fixture where they diverge), the partial-confounding blind-spot gradient (hand-recomputed from its joint table), the signed-offset/already_occluded non-equivalence, the egress recursive/cardinality guard's negative control (re-run), the "no result asserted" scan, the PENDING PASTE's discard-all/freshness/egress rules, and a full independent 819s run of `tests/m3` (0 failed, 33 skipped — matching the claimed baseline exactly). Nothing in this task fired, changed a criterion, or asserted a result.

---

_Verified: 2026-08-25_
_Verifier: Claude (gsd-verifier)_
