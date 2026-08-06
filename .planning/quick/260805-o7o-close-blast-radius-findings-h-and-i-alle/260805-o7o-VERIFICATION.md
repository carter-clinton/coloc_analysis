---
phase: quick/260805-o7o
verified: 2026-08-06T00:38:34Z
status: passed
score: 7/7 must-haves verified
overrides_applied: 0
---

# Quick 260805-o7o: Close blast-radius findings H and I — Verification Report

**Task goal:** Close blast-radius findings H (allele-blind sumstats↔panel join in
`run_susie_rss.R`) and I (`finemap_summary.tsv` is panel-blind) — together the
`m3-04c-BLAST-RADIUS.md:140` gate row "Trusting any AFR fine-map result."

**Verified:** 2026-08-06T00:38:34Z
**Status:** passed
**Commits reviewed:** `10c14f2` (T1), `64f420a` (T2), `dc4bbd2` (T3), `fb839a4` (docs) — HEAD is
`fb839a4`, matches `git rev-parse HEAD`.

**Method:** Independent re-derivation, not trust of the SUMMARY. Read every touched line of
`run_susie_rss.R`'s matcher/flip/JSON-emit code, `ld_read_path.py`, `config/pipeline.yaml`,
the schema, `finemap.smk`, and `summarize_finemap_results.py` against the ORIGINAL blast-radius
finding text (not the plan's paraphrase). Independently **ran** the three new test modules, the
72 pre-existing loader/wiring/contract tests, the full `tests/m3` suite (not the executor's
self-report), `snakemake --list` on the base config and all three lsweep overlays, and
reproduced the schema negative control by hand (temporarily stripping the `allele_aware` schema
entry and re-running `--list`).

## Goal Achievement

### Observable Truths (must_haves.truths, from PLAN frontmatter)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | An AFR sumstats variant binds to the panel row whose REF/ALT it actually matches, never an arbitrary ALT at the same position | ✓ VERIFIED | `match_indices_allele_aware` (`run_susie_rss.R:220-323`) — two `match()` calls on 4-keys (`chr:pos:REF:ALT` exact and transposed), duplicated panel 4-keys nulled before matching. `test_multiallelic_site_binds_to_the_matching_alt` binds to the correct row (`AW_BOUND_ALT == "C"`, not the first-hit `"G"`); permanent negative control `test_negative_control_pre_change_loader_binds_the_first_alt` reproduces the pre-change defect against `git show 0378ec8:`. Both independently re-run, pass. |
| 2 | A swapped-orientation variant has z NEGATED, not dropped, not mis-signed | ✓ VERIFIED | `run_susie_rss.R:1082-1091`: `subset[, z := z * ld_result$allele_orient]`, placed AFTER the `subset_idx` shrink and AFTER `z` is computed, with a length guard that `stop()`s on mismatch. Source-read confirms `credible_sets` at `:1151` reads `BETA, SE` straight from `subset` — untouched by the flip, which only multiplies the `z` column. Non-vacuous full-script proof (`test_full_script_consumes_the_flag_and_actually_flips_z`) uses a MIXED-orientation fixture specifically because `estimate_s_rss` is exactly sign-flip-invariant on an all-transposed fixture (self-caught, documented, and independently re-verified true: `s(z,R)==s(-z,R)`). Independently re-ran: **29/29 wiring tests pass**, including this one. |
| 3 | An unresolvable variant (palindromic/incompatible/ambiguous/allele-less) is DROPPED and COUNTED, never matched on position alone | ✓ VERIFIED | `run_susie_rss.R:284-320` computes `pal`, `unus`, `amb` masks and excludes them from `keep_mask`; six counters (`exact/flipped/dropped_{ambiguous,palindromic,mismatch,unusable}`) are always present. Each classifier has an independently re-run passing test with an in-test negative control proving the counter isn't structurally stuck at a constant. |
| 4 | Every disposition class reaches the region JSON, the per-region receipt, and finemap_summary.tsv | ✓ VERIFIED | JSON: `run_susie_rss.R:1193-1200` (8 fields, `NA` not `0` when unmeasured). Receipt: `finemap.smk:441` one-liner reads all 8 keys. TSV: `summarize_finemap_results.py` FIELDNAMES appends the same 8 (plus 6 more panel-provenance fields) at `:170-183`. |
| 5 | For EUR/TRANS the new join is structurally unreachable — `identical()` on the WHOLE `load_ld_matrix` result vs pre-change | ✓ VERIFIED | `test_eur_result_object_is_identical_to_pre_change` — `identical()` on the entire returned list, HEAD vs `git show 0378ec8:`, both undeclared and declared-file EUR fixtures (`EUR_IDENTICAL=TRUE`, `EUR_DECL_IDENTICAL=TRUE`). Inverted negative control on an AFR fixture under `allele_aware=TRUE` returns `AFR_IDENTICAL=FALSE` — proves the comparison can detect a difference. `ld_status`/`ld_overlap_fraction` are NOT used as evidence anywhere in this test (confirmed by reading the assertions). Independently re-run, passes. |
| 6 | A reader of finemap_summary.tsv can tell an AoU-panel row from a 1kG-panel row without opening JSON | ✓ VERIFIED | `test_aou_row_and_1kg_row_are_distinguishable_in_the_tsv` + permanent negative control `test_negative_control_pre_change_rows_are_byte_identical` (proves the pre-change rows were identical — finding I reproduced). First 17 columns byte-identical/ordered vs `0378ec8` confirmed by direct source diff. Independently re-run, passes (7/7). |
| 7 | Every new assertion observed RED against reverted source before being accepted green | ✓ VERIFIED (with one legitimate, disclosed exception) | Sampled ~15 negative controls directly in source; all are genuine (would fail if the classifier/flip/JSON field were disabled), not tautological. One plan-specified negative control (schema-entry removal → `--list` failure) was **empirically unachievable** — independently reproduced: removing the `allele_aware` schema entry and re-running `--list` gives **rc=0**, not a failure, because `additionalProperties:false` is top-level only and `ld_read_path`'s sub-object declares none of its own. The SUMMARY discloses this as "Deviation 1" and substitutes an achievable, non-vacuous control (a non-boolean value IS rejected with the entry present, silently accepted without it) — independently reproduced and confirmed correct. |

**Score:** 7/7 truths verified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `src/legacy/region_analysis/scripts/run_susie_rss.R` | allele-aware matcher, orientation vector, disposition counters, two structured rejections, `--ld-allele-aware` flag, z flip, allele-keyed catalog join, new JSON fields | ✓ VERIFIED | All present, read directly at `:142-1091`. Additive fields attached only when non-NULL (R `list(k=NULL)` trap caught and fixed per SUMMARY, confirmed in source `:505-524`). |
| `src/python/ld_read_path.py::ld_allele_aware` | `"true"`/`"false"` off the same allow-list plus the `allele_aware` sub-key | ✓ VERIFIED | `:125-152`, matches design exactly, fail-safe direction confirmed. |
| `src/snakemake/schemas/pipeline.schema.yaml` | `ld_read_path.allele_aware: boolean` | ✓ VERIFIED | `:406-408`, confirmed present; `snakemake --list` rc=0 on base config and all 3 lsweep overlays (independently re-run). |
| `src/legacy/region_analysis/scripts/summarize_finemap_results.py` | 14 appended fields, order untouched | ✓ VERIFIED | First 17 `FIELDNAMES` entries byte-identical/ordered to `0378ec8` (direct `git show` diff, confirmed by hand, not just by the test). 14 new fields appended at end. `summary`/`json_error` dicts key-for-key parity confirmed by reading both blocks. |
| `tests/m3/test_ld_allele_aware_join.py` | loader acceptance suite at production thresholds, in-suite negative controls | ✓ VERIFIED | Independently re-run: **20 passed, 0 skipped**. Thresholds confirmed read from `config/susie_policy.yaml` (50/0.5/10), not hardcoded permissive values. |
| `tests/m3/test_ld_allele_aware_wiring.py` | config/schema/smk wiring + full-script flip proof + EUR `identical()` | ✓ VERIFIED | Independently re-run: **29 passed, 0 skipped**. |
| `tests/m3/test_finemap_summary_panel_visible.py` | AoU-vs-1kG discrimination + 5-consumer pin | ✓ VERIFIED | Independently re-run: **7 passed, 0 skipped**. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `config/pipeline.yaml ld_read_path` | `ld_read_path.py::ld_allele_aware` | same allow-list | ✓ WIRED | `config/pipeline.yaml:309-312` carries `allele_aware: true` inside the existing block; `ld_allele_aware()` reads it. |
| `finemap.smk params.ld_allele_aware` | `run_susie_rss.R --ld-allele-aware` | rendered shell arg | ✓ WIRED | `finemap.smk:411` — `grep -c` confirms exactly 1 occurrence in the shell block. `params.region_id` (`:350`) confirmed byte-unchanged and untouched by the diff (`git diff 0378ec8 HEAD -- finemap.smk \| grep -c region_id=lambda` → 0). |
| `load_ld_matrix(allele_aware=)` | `subset[, z := z * ld_result$allele_orient]` | orientation vector aligned to subset_idx | ✓ WIRED | `run_susie_rss.R:1082-1091`, placed after the shrink, guarded by a length check. Lockstep between `keep_idx`/`ld_idx`/`orient` reordering confirmed at `:298-306` (`order(keep_idx)` applied to all three together) and independently tested with an interleaved fixture (`test_allele_orient_is_aligned_to_subset_idx_on_every_return`). |
| `run_susie_rss.R result$ld_allele_*` | `summarize_finemap_results.py FIELDNAMES` | `data.get()` on appended fieldnames | ✓ WIRED | JSON emits 8 fields (`:1193-1200`), Python reads all 8 by name (`:66-73`), FIELDNAMES appends the same 8 plus 6 more (`:176-183`). |

### Behavioral Spot-Checks (independently executed, not self-reported)

| Behavior | Command | Result | Status |
|---|---|---|---|
| New loader test module | `pytest tests/m3/test_ld_allele_aware_join.py -q -rs` | 20 passed, 0 skipped | ✓ PASS |
| New wiring test module | `pytest tests/m3/test_ld_allele_aware_wiring.py -q -rs` | 29 passed, 4 warnings (deprecation only), 0 skipped | ✓ PASS |
| New summary test module | `pytest tests/m3/test_finemap_summary_panel_visible.py -q -rs` | 7 passed, 0 skipped | ✓ PASS |
| 6 pre-existing loader/wiring/contract modules unchanged | `pytest test_ld_read_path_ancestry_gate.py test_ld_read_path.py test_ld_declared_authoritative.py test_occlusion_lockstep_wiring.py test_finemap_loader_contract.py test_stitch_subregions_to_rds.py -q -rs` | 72 passed | ✓ PASS |
| Full `tests/m3` suite, independent run | `pytest tests/m3 -q -rs` | **641 passed, 31 skipped, 0 failed** in 757.82s | ✓ PASS (exact match to SUMMARY's claim: 584 baseline + 57 new = 641; 31 skips unchanged, 0 from new modules) |
| `snakemake --list` on base config | direct run | rc=0 | ✓ PASS |
| `snakemake --list` on all 3 lsweep overlays | direct run | rc=0 for all 3 | ✓ PASS |
| Schema-removal negative control | manually stripped `allele_aware` schema entry, re-ran `--list`, restored | rc=0 (does NOT fail) | ✓ PASS — reproduces SUMMARY's Deviation 1 finding exactly |
| Freeze re-pin gate | `git diff --exit-code dc4bbd2 -- run_susie_rss.R` | rc=0 | ✓ PASS |
| Frozen contracts 0-diff | `git diff --exit-code 0378ec8 -- plink_ld_to_npz.py ld_npz_to_rds.R condition_ld_matrix.py` | rc=0 | ✓ PASS |
| m3-07 modules 0-diff | `git diff --exit-code 0378ec8 -- occlusion_span_filter.py occlusion_manifest.py occlusion_present_rate_scan.py drop_occluded_from_sumstats.py` | rc=0 | ✓ PASS |
| m3-06 (NaN→0) not revived | `grep -rnE 'condition_ld_matrix\|nan_to_num\|NaN...-> *0'` over the 3 edited scripts | no matches (rc=1) | ✓ PASS |
| Changed-file set is exactly the plan's scope | `git diff --name-only 0378ec8 HEAD -- src config tests \| sort` | 10 files: 6 plan `files_modified` + 3 new test files + `test_ld_read_path_ancestry_gate.py` (AUTH-o7o-01) | ✓ PASS — no other pre-existing test, no frozen contract, no m3-07 module |
| No perimeter-contact commands in the diff | `git diff 0378ec8 HEAD -- src config tests \| grep -inE "gsutil\|gcloud\|\bbq\b\|dataproc\|hailctl\| wb "` | no matches | ✓ PASS |
| `.planning/STATE.md` / `HANDOFF.json` untouched | `git diff --stat 0378ec8 HEAD` | no diff | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| H | `260805-o7o-PLAN.md` | Allele-blind sumstats↔panel join | ✓ SATISFIED | See truths 1-3, 5, 7 above. |
| I | `260805-o7o-PLAN.md` | `finemap_summary.tsv` panel-blind | ✓ SATISFIED | See truth 6 above. |

No orphaned requirements found for this phase in REQUIREMENTS.md (this is a `.planning/quick/` task, not a roadmap phase; no REQUIREMENTS.md cross-reference applies).

### Anti-Patterns Found

None. No TODO/FIXME/placeholder markers, no empty-return stubs, no hardcoded-empty props in the
touched files. The one item that would normally read as a "vacuous assertion" red flag — the
schema-removal negative control specified in the plan — was caught by the executor itself,
disclosed as Deviation 1, and replaced with an achievable substitute; independently reproduced
above and confirmed both halves (the specified control's actual behavior, and the substitute's
correctness).

### Item-by-item response to `<verify_these_specifically>`

1. **H's specific degradation path (SNP_ID branch matches zero, CHR:POS `match()` takes first
   hit, REF/ALT ignored) is closed, not just counted.** Confirmed: under `allele_aware=TRUE`
   the legacy `match_indices` body (containing the `:171`-class `match()`) is **never
   constructed** — `match_indices` branches to `match_indices_allele_aware` before reaching it
   (`run_susie_rss.R:325-333`). The new matcher uses two 4-key `match()` calls
   (`chr:pos:REF:ALT` exact + transposed), so a multiallelic site binds to the row whose alleles
   actually match, confirmed by `test_multiallelic_site_binds_to_the_matching_alt` (binds to
   `SNP_ID="x2"`, `ALT="C"`, not the first-hit `"x1"`/`"G"`) and its permanent negative control
   reproducing the old defect against `0378ec8` source. Not a counter bolted onto the old path —
   the old path is structurally unreachable under the flag.

2. **Orientation logic re-derived independently, confirmed correct.** Panel signs LD on ALT
   (`plink_ld_to_npz.py:29-35`, `--keep-allele-order` hardcoded, confirmed by grep at
   `aou_ld_panel.py:2905`); harmonized sumstats sign BETA on ALT
   (`harmonize_sumstats.py:255-262`, `harmonize_mvp.py:96-98`). The flip
   (`run_susie_rss.R:1090`, `subset[, z := z * ld_result$allele_orient]`) is applied: (a) to `z`
   only — `credible_sets` at `:1151` reads `BETA, SE` from `subset` untouched by the flip line;
   (b) to the correct rows — `allele_orient` is aligned to `subset_idx` by construction
   (`match_indices_allele_aware` applies `order(keep_idx)` to `keep_idx`, `ld_idx`, AND `orient`
   together at `:301-306`, closing the one way this fix could itself mis-sign); (c) in the
   correct order relative to row selection — the flip happens strictly after
   `subset <- subset[ld_result$subset_idx]` (`:1029-1031`) and after `z` is computed (`:1062`),
   with a `stop()` length guard if `allele_orient` and `subset` ever diverge (`:1083-1089`).
   Reported `BETA`/`SE` confirmed NOT flipped by direct source read.

3. **Track-A EUR invariance.** `test_eur_result_object_is_identical_to_pre_change` uses
   `identical()` on the ENTIRE returned list (not selected fields) for both the undeclared-file
   and declared-file EUR shapes, both `TRUE`. The inverted control (AFR under `allele_aware=TRUE`)
   returns `AFR_IDENTICAL=FALSE`, proving the comparison isn't blind. `ld_status`/
   `ld_overlap_fraction` do not appear anywhere in this test's assertions — confirmed by reading
   the full test body. Independently re-run, passes.

4. **`estimate_s_rss` global-sign-flip invariance vacuity, and its fix.** Confirmed
   mathematically plausible and confirmed operationally: the shipped consumption proof
   (`test_full_script_consumes_the_flag_and_actually_flips_z`) explicitly builds a
   MIXED-orientation fixture (odd panel rows transposed) rather than an all-transposed one, with
   an explicit docstring explaining why an all-transposed fixture would be vacuous
   (`s(z,R)==s(-z,R)`). The discriminator (`d3b_ld_z_consistency_s`) is asserted to differ by
   more than `1e-6` between flag-on and flag-off AND to specifically *improve* (decrease) when
   the flag is on. Independently re-run, passes — this is a genuine, non-vacuous consumption
   proof.

5. **Finding I.** 14 fields appended, first 17 `FIELDNAMES` entries confirmed byte-identical and
   in the same order as `0378ec8` by direct `git show` diff (not just trusting the test).
   `json_error` dict confirmed key-for-key in parity with `summary` by direct source read
   (both list the same 8 new `ld_allele_*` keys plus the 6 panel fields, `None` in the error
   path). AoU-vs-1kG row discrimination confirmed with a permanent negative control reproducing
   the pre-change byte-identical rows.

6. **Negative controls.** Sampled roughly 15 across all three new test modules directly in
   source (byte-identity, multiallelic first-hit, swap/flip, palindromic drop, mismatch drop,
   ambiguous drop, unusable drop, absent-position non-inflation, both structured rejections,
   EUR `identical()`, schema type-check, argv-delta self-consistency, `.pyc` staleness). All are
   genuine — each has either an in-test negative shape or a permanent `git show 0378ec8:`
   comparison that would fail if the fix were reverted. The one plan-specified control found
   unachievable (schema-removal → `--list` failure) was independently reproduced as genuinely
   unachievable (rc=0 without the entry) and the SUMMARY's substitute (non-boolean type
   rejection) was independently confirmed correct. The `.pyc` hardening
   (`summarize_finemap_results` test loader uses `compile()` on freshly-read source text, never
   `importlib.import_module`) structurally avoids the bytecode-cache class of bug rather than
   merely testing around it — confirmed by reading `_load_module` in
   `test_finemap_summary_panel_visible.py:71-96`, which also cross-checks the executed
   `FIELDNAMES` against a second independent parse of the same source text.

7. **Scope discipline.** `git diff --name-only 0378ec8 HEAD -- src config tests` contains
   exactly 10 files: the 6 plan `files_modified`, the 3 new test modules, and
   `tests/m3/test_ld_read_path_ancestry_gate.py` (the one authorized pre-existing-test edit,
   AUTH-o7o-01 — see below). No other pre-existing test file, no frozen contract
   (`plink_ld_to_npz.py`, `ld_npz_to_rds.R`, `condition_ld_matrix.py` all 0-diff vs `0378ec8`),
   no m3-07 module (all 4 confirmed 0-diff), and no reference to `condition_ld_matrix` / NaN→0
   in the three edited scripts. `m3_convert_npz_rds.smk`, `qtl_coloc.smk`, and every file
   relevant to findings E, G, J, K, L, M, and BLOCKER-D's large-region classes are absent from
   the diff — those findings are genuinely untouched, not silently discharged. No `gsutil` /
   `gcloud` / `bq` / `dataproc` / `hailctl` / `wb` string anywhere in the diff.
   `.planning/STATE.md` and `.planning/HANDOFF.json` confirmed untouched (`git diff --stat`
   empty against `0378ec8`).

### Noteworthy but non-blocking observations

- **AUTH-o7o-01** (widening `EXPECTED_ADDED_TOKENS` from 4 to 6 tokens in the pre-existing
  `tests/m3/test_ld_read_path_ancestry_gate.py`) is a genuine exception to hard rule 3 ("do not
  edit any pre-existing test file"). It is disclosed as required by hard rule 5 (STOP and
  surface a failing pre-existing test), the SUMMARY records the exact observed RED, and the
  widening is paid for with a new direct-property test
  (`test_params_ld_allele_aware_values`, which itself carries a genuine negative control: EUR
  put on the allow-list must render `"true"`, independently re-run and passing as part of the
  72-test pre-existing batch above). This is process-compliant, not a scope violation, but it is
  worth the developer's awareness since it is the one file outside the plan's declared
  `files_modified` that changed.
- **Cosmetic-only inconsistency**: `test_rendered_argv_delta_vs_3f431ab_is_exactly_four_tokens`'s
  name and docstring still say "four tokens" after AUTH-o7o-01 widened the list to six; the
  assertion itself (`added == EXPECTED_ADDED_TOKENS`) is correct and was independently confirmed
  passing. Purely a stale name/comment, no functional effect.

### Human Verification Required

None. Every must-have in this task is either a static code-structure claim (directly read and
confirmed against the original blast-radius finding text) or a claim provable by a deterministic
test/command that was independently re-executed in this verification pass — the manuscript-level
implications (documented plainly in the SUMMARY under "THE BEHAVIOUR CHANGE, NAMED PLAINLY") are
a disclosure obligation for the OSF/manuscript record, not something requiring interactive human
testing to verify code correctness.

### Gaps Summary

None. All 7 must-have truths verified against the actual codebase, not the SUMMARY's claims.
Every negative control sampled was genuine. The full `tests/m3` suite was independently re-run
(not trusted from the executor's self-report) and matched the SUMMARY's figures exactly
(641 passed / 31 skipped / 0 failed, 672 collected). Scope discipline (findings E, G, J, K, L, M,
BLOCKER-D large-region classes; frozen contracts; m3-06; no perimeter contact) confirmed by
direct diff inspection, not trust.

---

_Verified: 2026-08-06T00:38:34Z_
_Verifier: Claude (gsd-verifier)_
