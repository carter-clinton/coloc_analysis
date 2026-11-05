---
phase: ta-r4-head-to-head-reanalysis-and-submission
plan: 15.1
slug: W3f-producer-cap-fit-names-early-exit
subsystem: ta-r4 fine-map producer + coloc consumer (W3f fix-up; review N1, N2, N8)
tags: [w3f, cap, fit-names, method-none, frozen-script, d28-lift]
requires: [ta-r4-W4a Tasks 1-2]
decisions: [DEC-2026-11-04-ta-r4-w3f-fix-all, DEC-2026-11-04-ta-r4-n7-region-signflip-and-floor, DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze]
commits: [e38a519c, 4a1b9d4a, 6c6e9546, 3e895261, 1f771281, e5792b8b, 7a3415df, 215ddde3]
---

# 15.1 SUMMARY — N1 cap after LD restriction; N2 fit-name alignment; N8 method none

## Task 1 — Carter's decisions
`W3f-carter-decisions-2026-11-04.txt`, `W3f-carter-n1-unfreeze-reply.txt` (verbatim); DEC fix-all + N7 (e38a519c), N1 unfreeze (4a1b9d4a).

## Task 2 — N1
- `run_susie_rss.R --cap-after-ld-restriction` (default false, strict true/false); under true the SUSIE_MAX_VARIANTS check runs on
  the panel-restricted subset; early-exit records n_variants, n_variants_pre_ld, cap_stage. `commands.fit_command` passes `true` for
  non-legacy arms on CURRENT_SCRIPT.
- RED `data/r4/tmp/w3f/t2_red.txt`: 5 failed / 1 passed. GREEN `t2_green.txt`: 6 passed.
- NC1 (post-restriction check compares pre-LD count) `t2_nc1.txt`: 1 failed. NC2 (flag dropped from fit_command) `t2_nc2.txt`: 1 failed.
- Pins RED `t2_pins_red.txt` (R code pin + K-3 containment, 2 failed) → re-pin → 39 passed.
- Frozen-script neighbours (`t2_baseline.xml` vs `t2_after2.xml`): 132 pass / 1 skip → 138 / 1; the 6 added are test_cap_after_panel; 0 changed.
- **Deviation:** the code change landed in two commits (6c6e9546, then 1f771281 wrapping the pre-LD cap block in
  `if (!cap_after_ld)` as planned), each with its own re-pin (3e895261, e5792b8b). Acceptance asked for one code + one re-pin commit.

## Task 3 — N2 + N8
- `map_fit_names()` in run_coloc_pair_r4.R (direct / panel exact / swapped / strand for non-palindromic SNVs; else
  UNMAPPED_FIT_NAMES with per-reason counts and first 5); `--ld-panel` required for susie / A1_matched and checked against the
  fit JSON (FIT_PANEL_MISMATCH); used in qtl_abf. `name_map_a` / `name_map_b` in the output.
- N8: early-exit fits, empty coloc.susie summary, no finite PP.H4 → method `none` + `none_reason`; `estimands.region_stat` → (nan, False).
- RED `t3_red.txt`: 30 failed, 2 errors (incl. `COLOC_SUSIE_EMPTY`, UNMAPPED message cases, region_stat).
- NC1 (accept any allele pair) `t3_nc1.txt`: 3 failed (mismatch, palindrome_mismatch, message counts). NC2 (drop FIT_PANEL_MISMATCH)
  `t3_nc2.txt`: 1 failed. NC3 (region_stat returns PP for none) `t3_nc3.txt`: 1 failed.
- Spec updates (by id): test_coloc_pair_r4::test_output_keys_exact (+none_reason, name_map_a, name_map_b);
  test_panel_rsid_override_is_refused_not_dropped → ..._maps_through_panel_not_dropped;
  test_simulation_harness::test_coloc_identity_harness_vs_cli (passes --ld-panel + fit JSON). No other assertion changed.
- SH2B3_12q24 hypertension × stroke (repro_routeC, `sh2b3_hypertension_vs_stroke.susie.p12_primary.json`): rc 0, method coloc_susie,
  n_snps 583. hypertension 589 = 0 direct + 589 panel_exact + 0 swapped + 0 strand; stroke 622 = 0 + 622 + 0 + 0 (was 589/589 unmapped).

## Close (Slurm 1716306, c207n04, HEAD 7a3415df, 2026-11-05)
- Plan verify (+ test_qtl_group_runner): 104 passed, 1 skipped (W5b).
- QUICK 531 passed / 2 skipped in 185.9 s (budget 120 s — over; carried to 15.6).
- HEAVY 1 failed / 95 passed / 4 skipped: `test_json_cs_equals_fit_sets::test_fit_rds_unchanged_by_the_fix` — runs
  run_susie_rss.R@656529a, which rejects the new `--cap-after-ld-restriction`. Outside this plan's test list. Fixed in the test
  (215ddde3): the pre-fix substrate run strips that flag pair (fails if absent); md5 identity assertion unchanged. 3 passed (Slurm 1717387).
- PINS 39 passed.
