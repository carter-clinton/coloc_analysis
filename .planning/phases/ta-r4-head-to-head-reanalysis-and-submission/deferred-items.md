# Deferred items (ta-r4)

## 2026-11-18 — found by the 15.5a FULL run (out of scope for 15.5a)

- `tests/m3/test_variant_catalog_fallback_legacy_semantics.py::test_the_five_must_not_move_sites_are_byte_identical[too_many_variants_payload]`
  and `::test_the_symbol_scoped_diff_is_exactly_one_removed_line` fail. They have failed since 6c6e9546 (15.1 N1 cap move):
  11 passed at 4a1b9d4a, 2 failed at 6c6e9546, 1f771281 and e9c0d400. They pin the `too_many_variants` payload of
  `run_susie_rss.R` byte-identical to dc4bbd2, and the authorized N1 change moved it. FULL was not run in 15.1-15.5.
  Needs a re-scope of the pin under DEC-2026-11-04-run-susie-rss-cap-after-ld-restriction-unfreeze (Carter / 15.6).
- 6 test ids present in the W4a FULL baseline (full_W4a.xml) are absent by e9c0d400: test_coloc_pair_r4::
  test_panel_rsid_override_is_refused_not_dropped, test_contrast_stats::test_category_edges[kw11..kw14-kappa_ok-*],
  test_run_aggregation::test_draft_writes_exactly_17_draft_tables. Removed between W4a and 15.5; check they were
  deliberate (15.6).
