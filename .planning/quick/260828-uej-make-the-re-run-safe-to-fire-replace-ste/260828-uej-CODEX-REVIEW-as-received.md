**Newly Introduced**

**HIGH** Stale contaminated TSV can survive a failed “re-run,” despite the new “no output” safety claim.  
Evidence: `.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md:17-23` reuses `/home/jupyter/occ_measure/pcs_pairs.tsv`; `:67-71` records that this contaminated file already exists with `2,865,514` lines; `src/python/pairwise_completeness_scan.py:1531-1541` raises before `write_tsv` but never unlinks or quarantines an existing output. Tests only use fresh paths: `tests/m3/test_pairwise_completeness_scan.py:3077-3090`, `:3204-3233`.  
Failing scenario: rerun in the same enclave directory after the bad run, hit `ERROR: no windows selected` from a wrong/missing ancestry label or hit the denominator guard. The process exits before writing, but the old 871 MB contaminated `pcs_pairs.tsv` remains at the exact path the runbook later `wc -l`s.

**HIGH** The unmodified paste still has a stale freshness gate that will stop the repaired rerun.  
Evidence: `.planning/debug/260825-PENDING-PASTE-pairwise-completeness-sweep.md:48-61` says stop unless `git log -1` shows a `quick-260825-qpf` commit; current state says the repair is `quick-260826-qq9` at `.planning/STATE.md:17` and `.planning/STATE.md:40`.  
Failing scenario: operator follows the paste literally after `git pull`; HEAD is the repaired `quick-260826-qq9` closeout, not `quick-260825-qpf`, so Step 0 instructs them to stop before producing the pre-registered rerun.

**MEDIUM** The scanner’s composite ancestry parse does not mirror production on whitespace-shaped rows.  
Evidence: `_tsv_field` strips at `src/python/pairwise_completeness_scan.py:1240`, then `_read_regions_tsv` feeds that stripped value to `_matches_ancestry` at `:1304`; production preserves the parsed value in `_filter_ancestry` at `src/python/run_native_ld_panel.py:1178-1181` and also does a non-stripping `.lower()` compare in main at `:3073-3075`.  
Failing input: a manifest row with column 7 equal to `"  AFR  "`. The scanner selects it for `--ancestry AFR`; the LD-panel production filter drops it. The checked-in `config/ld_regions.tsv` does not have this shape, so this is not a blocker for that exact file.

**MEDIUM** The scanner is positional while production is header-keyed, so reordered or malformed manifests can diverge silently.  
Evidence: scanner hard-codes ancestry at `_REGIONS_TSV_ANCESTRY_COL = 6` and bounds at `14/15` in `src/python/pairwise_completeness_scan.py:1213-1217`, then indexes raw `parts` at `:1295-1308`; production reads a pandas header dictionary at `src/python/aou_ld_panel.py:3031-3036` and filters `r.get("ancestry", "")` at `src/python/run_native_ld_panel.py:1180-1181`.  
Failing input: same columns, different order, with a valid `ancestry` header not at position 7. Production selects the intended rows; scanner drops them or reads an unrelated column as ancestry.

**LOW** The duplicate guard only protects exact `str(region_id)` equality, not whitespace/case aliases passed directly to the iterator.  
Evidence: `src/python/pairwise_completeness_scan.py:696` counts `str(window[0])`; `iter_bim_windows` then returns exact-string keys at `:740-768`. The TSV parser strips manifest ids at `:1298`, so this is mostly an API/single-mode hole, not a real-manifest hole.  
Failing input: `iter_bim_windows(bim, [("R","15",1000,1005), (" R ","15",1000,1005)])` or `("R", ...)` plus `("r", ...)` with identical bounds. No guard trips; two region keys carry the same physical rows and the pooled denominator identity still reconciles.

**Pre-Existing**

**MEDIUM** The pair-level “ANY ordered row” rollup can understate row-level upstream blindness unless both numbers are carried forward.  
Evidence: `summarize` classifies distinct pairs by `pair_key` at `src/python/pairwise_completeness_scan.py:1145-1148`; the public prediction table labels `n_undefined_already_occluded`/`not` without “distinct-pair” in `.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md:544-548`; the state file admits the 5-row vs 3-pair undercount at `.planning/STATE.md:38`.  
Failing scenario: a deletion-deletion neighbor where one ordered row is interior/occluded and the reciprocal row is upstream/unoccluded. The unordered pair is counted “already occluded,” while one emitted undefined row is outside the posted rule. Reporting only `3` is not honest for the row-level question; reporting `3 pairs` and `5 rows` is.

**Test Quality**

**MEDIUM** The ancestry contract test is green while missing the actual composite divergence.  
Evidence: `tests/m3/test_pairwise_completeness_scan.py:2795-2801` compares `_matches_ancestry(row_value, ancestry)` directly to production, but the real scanner path is `_tsv_field(...).strip()` then `_matches_ancestry(...)` at `src/python/pairwise_completeness_scan.py:1240` and `:1304`.  
Failing mutation: keep `_matches_ancestry` exactly as tested, strip in `_tsv_field`, and use a whitespace-padded ancestry cell. The test stays green while scanner and production select different row sets.

**Checked, No Finding**

The checked-in real manifest itself looks clean for this fix: `config/ld_regions.tsv` has 553 lines, 276 `AFR`, 276 `EUR`, and no ancestry/region-id whitespace in the rows I checked. The pooled denominator identity is guaranteed in the current construction: `scan_region` returns a list at `src/python/pairwise_completeness_scan.py:1020`, that same list is extended into `all_results` at `:1482`, and `summarize` sets `n_candidate_rows = len(rows)` at `:1182`; zero-candidate and edge-clipped regions do not break it.

**Verdict**

Do not re-run as-is. The core real-manifest ancestry repair appears correct for the checked-in file, but the runbook/output hygiene is not safe enough for a paid enclave rerun feeding a public pre-registration: the stale freshness gate blocks the repaired commit, and a failed rerun can leave the known-contaminated TSV at the exact output path. Fix those before firing the instrument.
