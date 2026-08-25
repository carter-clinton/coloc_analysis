---
phase: quick-260825-ngh
plan: 01
subsystem: m3-afr-ld-panel
tags: [pairwise-completeness, undefined-ld, deletion-boundary, prevalence-sweep, bed-reader, tdd, instrument-only, m3-07, stage-b]

requires:
  - "src/python/occlusion_span_filter.py (FROZEN: _COL_* / parse_bim_row / load_bim_rows / _Variant.span_end / is_deletion)"
  - ".planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md (the adopted brief)"
provides:
  - "src/python/pairwise_completeness_scan.py — a genotype-only detector of UNDEFINED LD, with the carriers-lost gradient"
  - "tests/m3/test_pairwise_completeness_scan.py — 62 RED-first items"
  - ".planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md — the in-perimeter block, WRITTEN AND UNRUN"
affects:
  - ".planning/HANDOFF.json (suite baseline CORRECTED; resume entry #0)"
  - ".planning/STATE.md"
  - ".planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md"

tech-stack:
  added: []
  patterns:
    - "seek-by-index binary reader with a bounded LRU decode cache (int8 only)"
    - "measure THE PROPERTY, never a proxy; the proxy survives only as a derived label"
    - "perturbation negative controls executed in scratch COPIES, fresh interpreter each"

key-files:
  created:
    - src/python/pairwise_completeness_scan.py
    - tests/m3/test_pairwise_completeness_scan.py
    - .planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md
  modified:
    - .planning/HANDOFF.json
    - .planning/STATE.md
    - .planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md

decisions:
  - "The primary test is invariance within the intersection, on BOTH members. carriers(X) subset-of missing(Y) is a DERIVED LABEL only."
  - "span_offset is anchor-relative and therefore asymmetric for a deletion-deletion pair. That is the convention, pinned by a test."
  - "offset == 0 and already_occluded are DIFFERENT predicates (the posted rule's left bound is strict)."
  - "The egress assertion is RECURSIVE with a cardinality bound, not a flat width check."
  - "The constants-identity test was retargeted to FUNCTIONS; small-int interning makes the constants version a false invariant (measured)."

metrics:
  duration: "~1 h 50 m wall (of which 14 m 13 s is the full-suite re-baseline)"
  completed: 2026-08-25
  tasks: 4
  commits: 4
  tests_added: 62
  reds_observed: 14 groups + 10 perturbation controls
  cost: "$0 — zero VM / Dataproc / OSF / gsutil / gcloud contact"
---

# Quick 260825-ngh: Build + TDD the Pairwise-Completeness Scanner — Summary

**Built the measuring device the Stage B halt asked for — a genotype-only detector of "within `called(X) ∩ called(Y)`, X or Y is constant" that sweeps signed offsets on BOTH sides and records the carriers-lost gradient — and answered none of the three open questions, by design.**

## What this is

`m2_region_00057` halted Stage B with a confined pairwise NaN between the 1 bp deletion `chr15:20394741:AT:A` and the SNP `chr15:20394743:T:C`, one base past the pre-registered REF span. The mechanism is CONFIRMED (0 of 871 deletion carriers called at the partner → the deletion is invariant within the 71,048-sample intersection → plink writes `0/0` → NaN, while its marginal MAF is a healthy 0.601%). Three things were, and remain, UNKNOWN. This task built the instrument that can measure them. It did not run it.

## Commits

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | T1 — fail-closed seek-by-index plink1 `.bed` reader | `94dd36d` | `src/python/pairwise_completeness_scan.py`, `tests/m3/test_pairwise_completeness_scan.py` |
| 2 | T2 — both-sides enumeration + the direct pairwise test + the gradient | `ddbe068` | same two |
| 3 | T3 — egress-clean TSV/summary + CLI + the PENDING PASTE | `72814e6` | same two + `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md` |
| 4 | T4 — re-baseline + docs + push | (this commit) | `.planning/HANDOFF.json`, `.planning/STATE.md`, `.continue-here.md`, PLAN, SUMMARY |

All four staged EXPLICIT paths. Never `git add .` / `-A`.

---

## HARD INVARIANTS — measured at the START and END of every task

**Frozen surfaces**, `git diff --stat 7b59721 HEAD -- src/python/occlusion_span_filter.py src/python/run_native_ld_panel.py src/python/fire_verifier.py .planning/amendments/ | wc -l`:

| Checkpoint | Result |
|---|---|
| T1 start / T1 end | `0` / `0` |
| T2 start / T2 end | `0` / `0` |
| T3 start / T3 end | `0` / `0` |
| T4 start / T4 end | `0` / `0` |

**Amendment paste block** — computed with the SAFE TWO-STEP FILE FORM (`awk` into a scratch file, then `wc -c` and `md5sum` on the file). The `awk … | tee >(wc -c) | md5sum` one-liner is racy and deterministically prints the phantom `2f2e9548e1b2952ac802a847ea5dff40` on an unchanged file; it was not used.

| Checkpoint | `wc -c` | `md5sum` |
|---|---|---|
| BEFORE (T1 start) | `22945` | `13a49f543cabcc27ce9f1e589783c060` |
| T2 start | `22945` | `13a49f543cabcc27ce9f1e589783c060` |
| T3 start | `22945` | `13a49f543cabcc27ce9f1e589783c060` |
| AFTER (T4) | `22945` | `13a49f543cabcc27ce9f1e589783c060` |

**Import isolation** (T-ngh-05): `grep -c pairwise_completeness_scan` in `run_native_ld_panel.py` / `fire_verifier.py` / `occlusion_span_filter.py` = `0` / `0` / `0`. Nothing outside the new test file imports the scanner (repo-wide count `0`).

**No forked `.bim` column indices:** `grep -c '_COL_BP *=\|_COL_CHR *=\|_COL_ID *=\|_COL_ALT *=\|_COL_REF *='` on the scanner = `0`, at every commit.

---

## Every RED, pasted

### T1 — the whole file, before the module existed

```
E       ModuleNotFoundError: No module named 'pairwise_completeness_scan'
...
25 failed in 2.48s
```

All 25 T1 items failed as *test* failures (import inside the test body), not as a collection error.

### T1 perturbation controls — scratch copies only, fresh interpreter each

Run under `/gpfs.../scratchpad/ngh/pert/<name>/{src/python,tests/m3}` with `PYTHONDONTWRITEBYTECODE=1` and a separate pytest process per perturbation, so the bytecode-cache trap (`feedback_negative_control_defeated_by_bytecode_cache`) cannot apply. **Nothing was ever perturbed in-tree.**

**P1 — high-to-low bit-pair packing:**
```
>           assert reader.read_variant(0).dosage.tolist() == [2, pcs.MISSING_DOSAGE, 1, 0]
E           assert [0, 1, -1, 2] == [2, -1, 1, 0]
E             At index 0 diff: 0 != 2
```
Exactly the reversal the docstring predicts. (7 of 25 failed.)

**P2 — perturbed seek offset `3 + i*(bpv+1)`:**
```
>           assert reader.read_variant(1).dosage.tolist() == [1] * n
E           assert [1, 1, 2, 2, 0, 0] == [1, 1, 1, 1, 1, 1]
E             At index 2 diff: 2 != 1
```
(4 of 25 failed.)

**P3 — reshape without truncating to `n_samples`:**
```
>           assert len(a) == n_samples
E           assert 8 == 5
E            +  where 8 = len(array([ 2,  1,  0, -1,  2,  2,  2,  2], dtype=int8))
>           assert len(a) == n_samples
E           assert 8 == 7
E            +  where 8 = len(array([ 2,  1,  0, -1,  2,  1,  0,  2], dtype=int8))
```
The phantom samples are visible in the array. (3 of 25 failed.)

**P4 — reader hardcoded to always seek block 0:**
```
>           assert reader.read_variant(1).dosage.tolist() == [1] * n
E           assert [2, 2, 2, 2, 2, 2] == [1, 1, 1, 1, 1, 1]
```
and the window-relative-index documentation test also collapses:
```
E           AssertionError: fixture must make the two blocks distinguishable
E           assert not True
```
(2 of 25 failed.)

**P5 — fork `parse_bim_row` and re-declare `_COL_BP`:**
```
>       assert pcs.parse_bim_row is osf.parse_bim_row
E       AssertionError: assert <function parse_bim_row at 0x7f0fd2b263e0> is <function parse_bim_row at 0x7f0fd2b26340>

>       assert assignments == [], f"forked .bim column index declarations: {assignments}"
E       AssertionError: forked .bim column index declarations: ['_COL_BP']
E       assert ['_COL_BP'] == []
```

### ⚠ The interning trap, MEASURED — why the constants-identity test was retargeted

On that same forked module:

```
two independently written 5s satisfy is: True
FORKED module still passes _COL_BP identity: True
FORKED module fails function identity      : False
```

`pcs._COL_BP is osf._COL_BP` returns **True on a module that genuinely forked the constant**, because CPython interns small ints. Had the identity test been written against the constants, it would have been a green assertion that can never fail — a false invariant. It is written against the FUNCTIONS (which are never interned across modules) and the constants are guarded TEXTUALLY. Both halves were seen red above.

### T2 — before enumeration / the pairwise test / the gradient existed

```
E           AttributeError: module 'pairwise_completeness_scan' has no attribute 'scan_region'
...
19 failed, 26 passed in 1.25s
```

19 of the 20 new T2 items were red. The 20th, `test_default_window_bp_is_25_and_is_a_measurement_window`, was green on arrival because T1 had already shipped `DEFAULT_WINDOW_BP = 25`. **Reported honestly rather than restructured to look red**, and given its own negative control (P10 below) so no assertion in this file is green-without-ever-having-failed.

### T2 perturbation controls

**P6 — the primary test replaced by the one-directional `carriers(del) ⊆ missing(partner)` shortcut:**
```
>       assert pr.undefined is True
E       AssertionError: assert False is True
E        +  where False = PairResult(...confounding_pattern='perfect_partner_confounding').undefined
```
FAILED: `test_undefined_without_carriers_subset_of_missing`, `test_partner_is_the_invariant_member`, `test_lost_frac_one_implies_undefined`. This is the load-bearing control: it proves the primary path is the PROPERTY, not the shortcut.

**P7 — one-sided window (`offset >= 0` only):**
```
>       assert set(by_pos) == {997, 1005}
E       assert {1005} == {997, 1005}
E         Extra items in the right set: 997
```

**P8 — `<` instead of `<=` at the window boundary:**
```
>       assert offsets == [-K, K]
E       assert [-5] == [-5, 5]
E         Right contains one more item: 5
```

**P9 — the empty-intersection branch dropped:**
```
>       assert pr.undefined is True
E       AssertionError: assert False is True
E        +  where False = PairResult(...confounding_pattern='empty_intersection').undefined
```

**P10 — `DEFAULT_WINDOW_BP` moved to 10:**
```
>       assert pcs.DEFAULT_WINDOW_BP == 25
E       AssertionError: assert 10 == 25
```

### T3 — before the TSV / summary / CLI / paste existed

```
E       NotImplementedError: the CLI lands in T3
...
17 failed, 45 passed in 1.42s
```

### T3 egress negative control, run OUTSIDE `pytest.raises` (the raw red)

```
AssertionError: emitted name 'sample_ids' contains forbidden egress token 'sample'
```
```
AssertionError: distribution 'undefined_offset_histogram' holds 7313 entries (> 512); that is per-sample scale
```

---

## The 1/10-scale mirror of the measured case — arithmetic

`test_mirrors_a_measured_case_00057_perfect_confounding_MIRRORS_A_MEASURED_CASE`. Provenance is the halt record §MECHANISM CONFIRMED; the measurement is **cited, never re-derived**. `n_samples = 7313` is deliberately `% 4 == 1`, so this realistic fixture also exercises the padding-truncation path.

| Joint cell (del, partner) | Count |
|---|---|
| `('0','0')` | 7024 |
| `('0','NA')` | 57 |
| `('0','1')` | 82 |
| `('1','NA')` | 87 |
| `('NA','NA')` | 60 |
| `('NA','1')` | 1 |
| `('NA','0')` | 2 |
| **total** | **7313** (asserted) |

| Quantity | Hand-computed | Measured (real, 00057) |
|---|---|---|
| `n_both_called` | 7024 + 82 = **7106** | 71,048 |
| deletion carriers | **87**, retained **0**, lost **87**, `lost_frac == 1.0` | 871, 0 of 871 called |
| `n_called_del` | 7024+57+82+87 = **7250** | 72,489 |
| deletion marginal MAF | 87 / (2 × 7250) = **0.600%** | **0.601%** |
| `invariant_member` | `"deletion"` | deletion collapses; partner stays variable |
| partner | called **7109**, carriers **83**, retained **82**, lost **1** | variable in the intersection |
| `offset` / `already_occluded` | **+1** / `False` | +1 past `span_end` 20394742; the posted rule correctly declined |

The 0.600% vs 0.601% agreement is **a fixture property** (the mirror was built at 1/10 scale from the measured cells), not an independent rederivation — the test says so in its own assertion comment.

**The blind spot, instrumented** (`test_partial_confounding_is_DEFINED_and_the_gradient_sees_it`): the identical fixture with 5 of the 87 `('1','NA')` moved to `('1','0')` returns `undefined == False` — plink would compute a **finite `r`** and **no NaN check anywhere in the pipeline fires** — while the gradient reports `del_carriers_lost == 82` of 87, `lost_frac == 0.9425`, `confounding_pattern == "partial"`, and the region summary counts it in the `>= 0.9 AND defined` tail bin.

---

## Suite re-baseline — reconciled COMPONENT-EXACT

**Measured 2026-08-25 at `72814e6`:** `tests/m3` = **1083 passed / 33 skipped / 0 failed**, 1116 collected, 852.55 s (0:14:12).
**Baseline:** 1021 passed / 33 skipped / 0 failed, 1054 collected (2026-08-22 at `14e62eb`).

```
1021 passed    + 62 = 1083 passed     ✓
1054 collected + 62 = 1116 collected  ✓   (and 1083 + 33 = 1116 ✓)
33 skipped     +  0 = 33 skipped      ✓
```

**Checked a third, independent way** rather than trusting arithmetic that happens to agree (`feedback_aggregate_agreement_hides_component_errors`):

```
pytest tests/m3 --collect-only -q                                             -> 1116
pytest tests/m3 --collect-only -q --ignore=.../test_pairwise_completeness_scan.py -> 1054   <- EXACTLY the baseline
pytest tests/m3/test_pairwise_completeness_scan.py --collect-only -q           ->   62
```

The pre-existing set is *provably* untouched, so the `+62` cannot be masking an offsetting add/remove. **0 removed, 0 renamed.**

**The 62, enumerated by test name** (parametrize expansions counted as items, not as one):

*T1 — the `.bed` reader, 25 items.* `test_frozen_bim_symbols_are_imported_not_forked`; `test_module_declares_no_bim_column_indices_of_its_own`; `test_all_four_two_bit_codes_decode_to_expected_dosages`; `test_packing_is_low_to_high_within_a_byte`; `test_n_samples_multiple_of_four_decodes_exact_length`; **`test_padding_bits_cannot_manufacture_a_phantom_sample[5]`, `[7]` — a 2-way parametrize = 2 items**; `test_seek_by_index_returns_the_right_block`; `test_bad_magic_raises`; `test_individual_major_mode_raises`; `test_truncated_bed_raises`; `test_over_long_bed_raises`; `test_bim_line_count_mismatch_raises`; `test_fam_line_count_mismatch_raises`; **`test_out_of_range_index_raises[-1]`, `[3]`, `[99]` — 3-way = 3 items**; **`test_missing_bfile_component_raises[.bed]`, `[.bim]`, `[.fam]` — 3-way = 3 items**; `test_window_relative_index_reads_the_wrong_block`; `test_reader_does_not_slurp_the_bed`; `test_decode_cache_is_bounded_and_evicts`; `test_cache_variants_one_is_still_correct`; `test_missing_dosage_sentinel_and_called_property`.

*T2 — enumeration, the property, the gradient, 20 items (no parametrize).* `test_span_offset_signed_convention_table`; `test_offset_zero_and_already_occluded_are_not_the_same_predicate`; `test_default_window_bp_is_25_and_is_a_measurement_window`; `test_enumerate_emits_both_sides_with_signed_offsets`; `test_window_boundary_is_inclusive_at_exactly_plus_and_minus_K`; `test_only_deletions_anchor_candidates`; `test_self_pairs_are_never_emitted`; `test_deletion_deletion_neighbour_emits_two_rows_one_pair_key`; `test_unsorted_input_raises`; `test_mixed_chromosome_input_raises`; `test_interior_partner_is_flagged_already_occluded`; `test_iter_bim_windows_one_pass_global_indices`; `test_mirrors_a_measured_case_00057_perfect_confounding_MIRRORS_A_MEASURED_CASE`; `test_partial_confounding_is_DEFINED_and_the_gradient_sees_it`; `test_partner_is_the_invariant_member`; `test_undefined_without_carriers_subset_of_missing`; `test_empty_intersection_is_undefined`; `test_fully_defined_pair_has_zero_gradient`; `test_lost_frac_one_implies_undefined`; `test_scan_region_evaluates_every_candidate_row`.

*T3 — egress, summary, CLI, paste, 17 items (no parametrize).* `test_tsv_columns_exact_tuple_equality`; `test_pair_result_fields_are_the_tsv_columns`; `test_summary_keys_exact_equality`; `test_egress_emitted_names_and_field_widths_are_clean`; `test_egress_assertion_catches_a_per_sample_field`; `test_no_summary_key_names_a_rate_or_prevalence`; `test_write_tsv_header_equals_tsv_columns`; `test_summarize_counts_every_number`; `test_summarize_separates_already_occluded_from_newly_discovered`; `test_summarize_offset_histogram_over_undefined_rows_only`; `test_summarize_defined_lost_frac_bins_and_tail`; `test_pending_paste_exists_and_carries_the_harness_crosscheck`; `test_cli_single_region_reproduces_the_00057_oracles`; `test_cli_multi_region_one_bim_pass`; `test_cli_cache_variants_one_is_byte_identical`; `test_cli_missing_bfile_exits_nonzero_and_writes_no_partial_tsv`; `test_cli_help_mentions_measurement_window`.

**25 + 20 + 17 = 62.**

**Skips stayed at 33** — every added test is pure-synthetic (`tmp_path` fixtures only), needing no perimeter, no hail, no chain file and no measured artifact, so none of them *can* land as a skip. A new SKIP here would have been a blocker, not a rounding difference (`feedback_skip_guard_masks_not_fixes`).

**Collateral:** `tests/phase2` = 136 passed / 1 skipped / 0 failed — identical to its recorded baseline.

---

## Deviations from Plan

**1. [Rule 1 — Bug] `partner_maf_marginal` was never passed to `PairResult`**
- **Found during:** T2 GREEN
- **Issue:** `TypeError: PairResult.__new__() missing 1 required positional argument: 'partner_maf_marginal'` — 8 tests red.
- **Fix:** added `partner_maf_marginal=partner_maf` to the constructor call.
- **Commit:** `ddbe068`

**2. [Rule 1 — Bug] My own fixture arithmetic was wrong in two places, caught before it could pass**
- (a) `test_deletion_deletion_neighbour_emits_two_rows_one_pair_key` asserted offsets `[-8, 8]`. The offset is **anchor-relative**, so anchoring on the 2 bp deletion at 1010 puts its partner at `1000 - 1010 = -10`, not `-8`. Corrected to `[-10, 8]` **and** the asymmetry is now documented in the test and in `span_offset`'s docstring as the convention working, not a defect.
- (b) `test_summarize_defined_lost_frac_bins_and_tail` asserted `"(0.9,0.99]": 3` while also asserting the bins sum to 7 — self-contradictory. The true count is **2** (0.9425 and 0.93-via-the-partner). Corrected, and an explicit `len(results) - 1 == 7` reconciliation line added so the bin dict and the row count must agree arithmetically.
- **Commits:** `ddbe068`, `72814e6`

**3. [Rule 2 — Missing critical functionality] The egress assertion needed to be RECURSIVE, not flat**
- **Found during:** T3 GREEN — the flat "every field renders to ≤ 64 chars" rule **false-positived** on `defined_carriers_lost_frac_bins` (88 chars), which is a 6-entry aggregate distribution the plan itself requires.
- **Why this mattered:** a guard that fires on correct output makes weakening the guard the cheap fix (`feedback_scope_a_guard_to_the_property_not_a_proxy`).
- **Fix:** the helper now recurses into dict values — every key and value inside a distribution must itself be a short scalar, and a distribution's **cardinality** is bounded at 512, which a 73,122-entry per-sample map can never satisfy. This is **strictly stronger** than the flat check for those two fields. A third negative control (a per-sample map hidden inside a distribution) was added and seen red.
- **Commit:** `72814e6`

**4. [Rule 2] `test_default_window_bp_...` was green on arrival; given a negative control**
- It could not be red at T2 because T1 already shipped the constant. Rather than report a green assertion that had never failed, perturbation **P10** was run to observe its red. Reported, not hidden.

**5. [Plan wording] `.continue-here` is `.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md`**
- No file named `.continue-here` exists at the repo root and none is tracked. The tracked artifact is the phase-scoped `.continue-here.md`; that is what was updated.

**6. [Verification method] `bash -n` on the whole PENDING PASTE block fails — and so does the house-style predecessor's**
- The paste is a **runbook** (prose interleaved with commands), not a standalone script, exactly like `260819-PENDING-PASTE-3-site-basis-sweep.md`, which fails `bash -n` identically at its own line 2. Verified instead, per the plan: both embedded `python3` heredocs pass `py_compile`; each executable command run passes `bash -n` in isolation; and **every CLI flag the paste uses exists in the shipped `main`** (`--help`-checked, exit 0).

**7. [Out of scope — observed, restored, NOT committed] a full `tests/m3` run dirties a tracked file**
- Running the suite rewrote `tests/m3/sparse_parent_benchmark.tsv` — only the wall-clock columns moved (`read_s` 1.133 → 0.991, `densify_window_s` 0.236 → 0.156). It is regenerated by `tests/m3/test_sparse_parent_benchmark.py`; the byte-size and RAM columns are unchanged, so this is machine timing noise, not a behaviour change.
- **Not caused by this task and not fixed by it.** The file was `git restore`d so no unrelated diff rode along in the T4 commit. Worth knowing: the m3 suite is not idempotent on the working tree, so "clean tree" checks after a full run will show this one file every time.

No architectural changes. No Rule 4 checkpoint was reached.

---

## Threat model — dispositions verified

| Threat | Verified how |
|---|---|
| T-ngh-01 (tampering, `BedReader.__init__`) | 6 raise-tests, all seen red; magic/mode/size-both-directions/`.bim`-count/`.fam`-count/index |
| T-ngh-02 (info disclosure, emission) | `TSV_COLUMNS` and `SUMMARY_KEYS` pinned by exact equality; recursive egress helper with 3 seen-red negative controls |
| T-ngh-03 (window-relative vs global index) | `iter_bim_windows` derives global indices in one pass; the corruption is demonstrated by a documentation test |
| T-ngh-04 (repudiation of results) | PENDING PASTE STEP 1 cross-checks 00057 ALONE and DISCARDS ALL on mismatch; STEP 0 pastes the running SHA back |
| T-ngh-05 (scanner reaching the fire path) | `git diff --stat` empty at all 4 commits; scanner import count `0` in all 3 fire-path files |
| T-ngh-06 (unbounded decode memory) | seek-by-index only; LRU eviction test; `--cache-variants 1` byte-identical output |
| T-ngh-07 (stale clone) | STEP 0 `git pull --ff-only` + SHA + `ls -l`; NCSU pushed in T4 as the precondition |
| T-ngh-08 (inferring prevalence from n=1) | no `rate`/`prevalence`/`estimate`/`ceiling` key may exist (asserted); every deliverable states the three questions stay OPEN |

---

## WHAT THIS DOES NOT ESTABLISH

**This task built a measuring device and did not use it. It produces no fact about the AFR panel.**

1. **The PREVALENCE of undefined pairs is UNKNOWN.** Nothing here counts them in real data. One region (00057) carries a confirmed pair and one region (region 1, 7,951 multi-base-REF rows, 38.6 GB re-read) carries none. Those two facts do not determine a rate, and no rate is stated anywhere in this task's deliverables.

2. **The BOUNDARY WIDTH is UNKNOWN, and whether it is one-sided is UNKNOWN.** The scanner sweeps `±25 bp` because that is a **measurement window**, not because 25 is a boundary. The default is asserted to be 25 by a test purely so it cannot drift silently. The offset histogram is the thing that would *supply* an empirical width; it has never been populated with real data.

3. **Whether a PARTIAL-CONFOUNDING TAIL exists is UNKNOWN.** The gradient can now *see* one — that is new — but seeing an instrument work on a synthetic fixture is not the same as observing a tail. `0.9425` appears in this document only as a **synthetic fixture oracle**, never as a measurement.

4. **Region 1's NaN-free pass still does not mean region 1 is bias-free.** It establishes only that region 1 held no *perfectly* confounded pair. This task does not change that, and the Stage A falsification stands exactly as originally worded.

5. **No criterion, threshold, span rule or NaN policy changed**, and nothing here recommends one. Whether the posted occlusion criterion should be extended, whether an explicit pairwise-completeness policy is warranted, or what Stage C's error-handling posture should be, are **pre-registration questions** to be adjudicated brief-blind, with Seth, **after** the numbers exist. Deciding any of them from the single 00057 pair is exactly the error that produced the withdrawn `0.0005` constant, which was wrong by ~38× when finally measured.

6. **The instrument is UNVALIDATED AGAINST REAL DATA.** Every test is synthetic. The first real evidence it works is STEP 1 of the PENDING PASTE — the 00057 harness cross-check — and until that passes in-perimeter, no number this scanner produces should be believed. That is why STEP 1 runs ALONE, before the sweep, and discards everything on mismatch.

7. **Nothing was fired. `$0`.** Zero VM, Dataproc, OSF, `gsutil` and `gcloud` contact. The VM remains STOPPED. The PENDING PASTE is written and unrun. **An agent never fires.**

Also unchanged and still outstanding: **RAM-1** (`peak_ram_gib` is a monotone high-water mark; fix with `Popen` + `os.wait4` before Stage C) and **COST-1** (`m2_region_00071`, the worst-case anchor, never ran).
