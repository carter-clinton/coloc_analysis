---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.8e
subsystem: ta-r4 W3f (Q-157J R5 multi-key cross-purity member; R7 Purpose chronology)
tags: [cross-panel-purity, variant-matching, amendment-text, chronology]
requires: [ta-r4-W3f-e7-filtered-cs-counts]
provides: [cs_cross_purity.R REFUSED_MULTI_KEY fatal, DRAFT (e) E4 multi-key error, DRAFT Purpose R7 sentence]
affects: [15.8f]
tech-stack:
  added: []
  patterns: ["measure the production-panel exposure before turning a counted exclusion into an error"]
key-files:
  created: []
  modified:
    - src/snakemake/scripts/ta_r4/cs_cross_purity.R
    - tests/ta_r4/test_cs_cross_purity_resolution.py
    - tests/ta_r4/test_amendment_text.py
    - .planning/amendments/osf-amendment-r4-DRAFT.md
decisions:
  - "Q-157J R5 (Carter: go with recommendation): a credible-set member that resolves to more than one allele key stops cross-panel purity (REFUSED_MULTI_KEY) unless --allow-duplicate-rows; measured exposure on the 20 production-panel pilot fits = 0, so no Q-158R5"
  - "Q-158R7 (Carter: Approve as written (Recommended)): Purpose drops the (h) parenthetical and gains the approved sentence byte-for-byte (sha256 59c2631a…72be)"
metrics:
  completed: 2026-11-27
  duration: "2026-11-26 21:10 - 2026-11-27 00:20 EST (one FULL, 2h14m)"
---

# Phase ta-r4 Plan 15.8e: multi-key member fatal and Purpose chronology Summary

Cross-panel purity no longer quietly leaves out a credible-set member whose name resolves to more than one allele key.
cs_cross_purity.R now stops with `REFUSED_MULTI_KEY`, with or without --allow-absent, and only --allow-duplicate-rows
(pre-15.5a measurement) keeps the catalog-order choice. Before the change, the 123 credible-set members of the 20
production-panel pilot fits were measured: 0 resolve to more than one key. The DRAFT Purpose now separates gated
production execution from pilot fitting, in Carter's approved wording.

## Commits

| Task | Commit | What |
|------|--------|------|
| 1 | (none; scratch only) | multikey_15_8e.tsv, multikey_catalogs_15_8e.tsv, multikey_oriented_15_8e.tsv |
| 2 | f4e4e567 | cs_cross_purity.R fatal vector + header; 2 new tests + declared spec update; DRAFT (e) E4 + Purpose |
| 3 | (records) | LOG, PLAN-INDEX, STATE, this SUMMARY |

## Gates

- Start 95af37b7 (data/r4/tmp/w3f/q158/start_15_8e.txt).
- gate_157j.sh rc 0 (805afcd8…0503e); gate_158.sh Q-158R7 rc 0 (a9a6866e…61b8, `Approve as written (Recommended)`);
  originals' sha256sum match (gate_15_8e.txt).
- Gate NCs (gate_nc_15_8e.txt): GATE_NC_MUTATE=1 on both → rc 2 (cmp differs); GATE_NC_FREE_TEXT on Q-157J → rc 2;
  both gates rc 0 again afterwards.

## Multi-key measurement (Task 1; Slurm 2118320, c205n10, 4m38s, 16G)

multikey_15_8e.R reads only each pilot fit RDS's member names (`unique(colnames(fit$lbf_variable)[unlist(fit$sets$cs)])`)
and calls variant_match.R `resolve_fit_names` without --allow-duplicate-rows. It uses the sumstats file recorded in
the fit JSON (all 5 distinct files in manifests/sumstats_r4_sha256.tsv, sha256 verified), cs_cross_purity.R's
window, the r4 catalog `data/r4/ld/variants_r4/<region>.tsv` (sha256 = catalogs_r4_fixed_point.tsv final_sha256_pinned)
and the EUR_1kg_r4 fit panel's variants. No LD, no purity, no colocalization, and cs_cross_purity.R was not run on any
pilot fit.

| Count | Result |
|-------|--------|
| pilot fits (A3_1kg_newcat) | 20; 7 with credible sets; 0 missing inputs |
| credible-set members | 123 (74 ok, 49 duplicate_row) |
| members with more than one allele key | **0** (also 0 with the catalog the fit JSON records, raw_sha256_pinned) |
| catalog bound: SNP_IDs with more than one normalized key, 31 r4 catalogs | **0** |
| oriented-input bound: SNP_IDs with more than one in-catalog key, 8 oriented files × 31 regions | **0** in all 248 rows (8/8 sha256 match) |

Members by fit (n_members / multi-key): asthma FTO 95/0, bmi FTO 6/0, bmi MC4R 4/0, bmi SH2B3 1/0, hypertension
SH2B3 2/0, stroke SH2B3 3/0, t2d FTO 12/0; the other 13 fits have no credible set. Total 0, so there was no Q-158R5 STOP.

NCs (same job, `MK_NC=1`): one in-catalog member row relabelled to another member's SNP_ID → 4 refused members over
3 fits. Catalog row 2 takes row 1's SNP_ID → 30 of 31 catalogs flag 1. Every in-catalog row takes one SNP_ID → 241 of
248 rows flag. Each counter can report a non-zero count.

## What changed (Task 2, f4e4e567)

- cs_cross_purity.R: `"refused_multi_key"` added to the fatal status vector (`REFUSED_MULTI_KEY: <n> of <m> credible-set
  members of <fit> (first: …)`); header comment: "a base with several keys is an error (REFUSED_MULTI_KEY) unless
  --allow-duplicate-rows, which takes the (N+1)-th key in catalog order". The per-set counting and the
  `n_refused_multi_key` column are unchanged (always 0 in a written row).
- DRAFT (draft_15_8e.py; each old string asserted unique): (e) E4 `… is left out of the purity and counted, and its
  set is noted.` → `… is an error.`; Purpose: ` (the pre-lock pilot fits are listed in (h))` removed, the R7 sentence
  added after the Purpose sentence. R7 text taken from the PLAN `<context>`, wraps joined: 416 characters, sha256
  59c2631a6baa441c44754bbf3d55cb1f0eadd7b18356b7af6762d92a557672be, asserted before insertion and on the inserted text
  in place; present exactly once. DRAFT sha256 26cb7d33…2e0d → e172a8ab…4f2f; `git diff --word-diff` shows only these
  three changes. (h) and the approved pilot-fit paragraph untouched (test_draft_paragraph_equals_the_approved_file_unwrapped green).
- Tests: `test_multi_key_member_is_fatal_with_or_without_allow_absent` (new); `test_purpose_states_gated_production_vs_pilot_fitting`
  (new); declared spec update of `test_multi_key_base_is_refused_and_counted_in_production_and_chosen_by_catalog_order_only_when_allowed`.
  Its production block now asserts a non-zero exit with `REFUSED_MULTI_KEY` and `rsM` in stderr; the
  --allow-duplicate-rows and BAD_OCCURRENCE blocks are unchanged, and the fixture moved to a shared `MULTI_KEY` constant.
- RED (Slurm 2118377, red_15_8e.txt): 3 failed (rc 0 where non-zero was required ×2; Purpose still had the parenthetical).
- Green (Slurm 2118424, cascadelake): the 6 plan files, 71 passed / 2 skipped (FINAL/PUBLIC, W4b).
- NCs (Slurm 2118480, nc_15_8e.txt): refused_multi_key removed from the vector → test 1 fails; old parenthetical
  restored in the DRAFT → test 2 fails; md5 / sha256 restore OK; both pass after restore.

## Deviations from Plan

1. **[Rule 2 - extra measurement] Second catalog column.** The 20 pilot fits record the pre-dedup catalog
   (`/rs1/…/measure_asthma_fix/catalogs/r4/<region>.tsv`, = catalogs_r4_fixed_point raw_sha256_pinned), and
   paths.catalog_path("r4") is the final catalog. The plan's measurement uses the r4 catalog. I added the same count
   with the recorded catalog as a secondary column. Both are 0.
2. **[Rule 3 - memory] Sumstats window read.** cs_cross_purity.R reads the whole file with `gunzip -c`. My script
   pre-filters on CHR/POS (cols 1/2, header checked) with awk, then applies cs_cross_purity.R's own window filter.
   The window rows are the same.
3. **Test 1 is one id.** It loops over (no flag) and (--allow-absent) in sub-directories instead of parametrizing,
   which keeps N_new = 2 and the expected 2,766.

## Observations (not in scope)

- 49 of the 123 pilot-fit members have status `duplicate_row` (make.unique `.N` names from the pre-dedup catalog).
  cs_cross_purity.R already refuses these without --allow-duplicate-rows (15.7c). The pilot fits are never production
  inputs, and production fits are built on the deduplicated catalog.
- cs_cross_purity.R:13 still lists "DUPLICATE_ROW, BAD_OCCURRENCE, UNRESOLVED and AMBIGUOUS are errors even under
  --allow-absent". REFUSED_MULTI_KEY is not added there, because the plan limits the comment change to :7-8. The
  sentence is still true but not complete. Candidate for 15.8f's review.
- Green's seff peak was 16.0 GB of 16 GB, which may include page cache, and it completed.

## FULL (Task 3)

- Checker NC (Slurm 2118515, check_nc_15_8e.txt): full_15_8d.xml as NEW → 4 MISS, CHECK FAIL rc 1.
- FULL (Slurm 2118513, c020n03 Cascade Lake, HEAD f4e4e567, 2h13m49s, `--mem=64G -t 04:00:00`): QUICK 910 P / 2 S,
  HEAVY 355 P / 5 S, PINS 39 P; FULL 2,766 = 2,713 P / 53 S / 0 F (full_15_8e.xml, sha256
  982d7ed80943ad429a868741af3ac3cf6f3200f88e9096e465436a84c4a89d89).
- check_15_8e.py (Slurm 2119223) vs full_15_8d.xml (2,764 read from the file): 0 removed; +2 added, both passed
  (test_purpose_states_gated_production_vs_pilot_fitting, test_multi_key_member_is_fatal_with_or_without_allow_absent);
  0 outcome changes; declared id passed -> passed; CHECK PASS (check_15_8e.txt). sparse_parent_benchmark.tsv restored.
- ⚠ Memory: sacct MaxRSS 67,109,432 KiB = the full 64G request, the same as 15.8d run 2, with exit 0. The sampled
  figure may include page cache, but 15.8f should not size FULL below 64G and could request more for headroom.
- Base for 15.8f = data/r4/tmp/w3f/q158/full_15_8e.xml (expected 2,768).

## New test ids

tests.ta_r4.test_cs_cross_purity_resolution::test_multi_key_member_is_fatal_with_or_without_allow_absent
tests.ta_r4.test_amendment_text::test_purpose_states_gated_production_vs_pilot_fitting

## Declared spec updates

tests.ta_r4.test_cs_cross_purity_resolution::test_multi_key_base_is_refused_and_counted_in_production_and_chosen_by_catalog_order_only_when_allowed

(Its production block now asserts a non-zero exit with REFUSED_MULTI_KEY and rsM in stderr; the id is kept per the
protocol although its name says "counted". No renames.)

## Known Stubs

None.

## Self-Check

PASSED: the 4 modified repo files and the 11 scratch records (multikey ×3, gate ×2, red, nc, draft, full xml, check, check NC) exist; f4e4e567 is a commit touching exactly the 4 planned code/test/DRAFT files; the fatal vector holds refused_multi_key; the R7 sha256 is recorded twice (before, in place) in draft_15_8e.txt.
