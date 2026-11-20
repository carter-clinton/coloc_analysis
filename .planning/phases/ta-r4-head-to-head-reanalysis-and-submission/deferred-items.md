# Deferred items (ta-r4)

## 2026-11-18 — found by the 15.5a FULL run (out of scope for 15.5a)

- `tests/m3/test_variant_catalog_fallback_legacy_semantics.py::test_the_five_must_not_move_sites_are_byte_identical[too_many_variants_payload]`
  and `::test_the_symbol_scoped_diff_is_exactly_one_removed_line` fail. They have failed since 6c6e9546 (15.1 N1 cap move):
  11 passed at 4a1b9d4a, 2 failed at 6c6e9546, 1f771281 and e9c0d400. They pin the `too_many_variants` payload of
  `run_susie_rss.R` byte-identical to dc4bbd2, and the authorized N1 change moved it. FULL was not run in 15.1-15.5.
  Needs a re-scope of the pin under DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze (Carter / 15.6).
  - RESOLVED 2026-11-19 (15.5c): fb08a75f (DEC-2026-11-19-trackb-legacy-semantics-pins-ignore-indentation + Carter
    replies) and dc15a630 (test file only; PRE_K1_REF stays dc4bbd2; 20 in-memory tests). FULL Slurm 1990243: both ids
    failed -> passed (2 F -> P); 2,555 = 2,502 P / 53 S / 0 F.
- 6 test ids present in the W4a FULL baseline (full_W4a.xml) are absent by e9c0d400: test_coloc_pair_r4::
  test_panel_rsid_override_is_refused_not_dropped, test_contrast_stats::test_category_edges[kw11..kw14-kappa_ok-*],
  test_run_aggregation::test_draft_writes_exactly_17_draft_tables. Removed between W4a and 15.5; check they were
  deliberate (15.6).
  - RESOLVED 2026-11-19 (15.5c): deliberate renames, not lost tests; 15.6's FULL reconciliation allows exactly these 6
    (scoped edit, 15.5c). Rename map (each successor present and passed in full_15_5c.xml, check_W4a.py):
    - test_coloc_pair_r4::test_panel_rsid_override_is_refused_not_dropped -> ..._maps_through_panel_not_dropped
      (7a3415df, N2 spec update)
    - test_run_aggregation::test_draft_writes_exactly_17_draft_tables -> ..._exactly_19_draft_tables (17 -> 18 in
      ade4e9c5, 18 -> 19 in bed315d4)
    - test_contrast_stats::test_category_edges[kw11-kappa_ok-True], [kw12-kappa_ok-False], [kw13-kappa_ok-True],
      [kw14-kappa_ok-False] -> [kw12-kappa_ok-True], [kw13-kappa_ok-False], [kw14-kappa_ok-True], [kw15-kappa_ok-False]
      (92caa306, N7 inserted one mcnemar case; [kw11-mcnemar-ns] present)
