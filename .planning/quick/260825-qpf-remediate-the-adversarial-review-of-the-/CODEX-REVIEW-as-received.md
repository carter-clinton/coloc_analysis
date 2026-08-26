**Findings**

1. **HIGH: sample-set mismatch can create false negatives.**  
   `pairwise_completeness_scan.py` counts every `.fam` row and evaluates every sample in `called_del & called_partner`: [line 192](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:192), [lines 620-627](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:620). PLINK 1.9 LD docs say LD calculations “only consider founders” by default, while the production square command adds `--nonfounders`: [aou_ld_panel.py:2914](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/aou_ld_panel.py:2914).  
   Failing input: founders-only pair has deletion invariant in joint calls; nonfounders add retained deletion carriers. PLINK without `--nonfounders` writes NaN; scanner includes nonfounders and reports defined. Consequence: under-reported undefined pairs unless the scan is explicitly tied to the exact LD command/sample policy. Official PLINK source: LD docs note founder-only default and allele-count correlations.

2. **HIGH: region-edge clipping can miss candidates.**  
   `iter_bim_windows()` only returns rows whose own position is inside the region: [lines 503-505](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:503). Only after that does `enumerate_candidates()` apply `window_bp`: [lines 431-435](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:431).  
   Failing input: region `1000-2000`, deletion `1999:AT:A` span end `2000`, SNP at `2001`, `window_bp=25`. The pair is offset `+1` but never loaded. Consequence: false low boundary prevalence at region edges. If the intended universe is exactly PLINK’s `--from-bp/--to-bp` matrix, this needs to be reported as clipping, not silently treated as absence.

3. **HIGH: no real PLINK cross-check for the load-bearing assumption.**  
   Tests explicitly run “No plink”: [test file line 31](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/tests/m3/test_pairwise_completeness_scan.py:31). The observed “both marginals variable, diagonal 1, one symmetric NaN pair” is strong evidence against mean imputation and whole-region listwise deletion, but not a proof of the implementation contract. PLINK docs say `--r` is allele-count correlation, but the public docs do not spell out pairwise-complete handling; PLINK source comments do show missingness masks and terms over nonmissing observations.  
   Cheap falsifier: 3 variants X/Y/Z, with X carriers missing only at Y and called at Z. Pairwise-complete predicts only X-Y is NaN; mean-impute predicts X-Y finite; listwise over all three predicts X-Z also NaN. Run exact production modifiers: `--keep-allele-order --nonfounders --r square bin4`.

4. **MEDIUM: duplicate variant IDs collapse distinct pairs in summaries.**  
   `pair_key` is sorted IDs only: [line 459](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:459). Summary distinct counts use that key: [lines 825-858](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:825).  
   Failing input: two different partner rows both named `.` or same rsID near one deletion; one undefined, one defined. Consequence: `n_distinct_pairs` and undefined occlusion split are wrong. This can undercount distinct undefined pairs.

5. **MEDIUM: `af_a1 == 0.5` tie can hide the carrier-loss tail.**  
   `_minor_allele_carriers()` chooses A1 on ties: [lines 561-566](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:561).  
   Failing input: A1 frequency exactly 0.5, all A2 carriers are missing at partner, A1 carriers retained. Scanner tracks A1 carriers and reports low/zero loss. Consequence: partial-confounding tail can be binned as reassuring even though the other allele is depleted.

6. **LOW: `read_variant()` normalizes to `idx` but seeks with raw `index`.**  
   Bounds use `idx`: [line 281](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:281). Offset uses `index`: [line 292](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:292).  
   Failing input: API caller passes `"1"` or `1.0`. Bounds pass or coerce, then seek calculation fails or mis-types. CLI path uses ints, so this is not the main false-negative path.

7. **LOW: `summarize(..., n_deletions=None)` lies for isolated deletions.**  
   Default derives deletions from result rows only: [lines 846-847](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:846).  
   Failing input: one deletion, no candidate partners. `results=[]`, summary reports `n_deletions=0`. CLI passes `n_deletions`, so direct API use is the risk.

**No Defect Found**

`.bed` decoding matches the PLINK binary contract: magic bytes, variant-major blocks, low-to-high 2-bit packing, code meanings, rounded-up block size, and padding truncation align with PLINK’s file-format docs and code lines [198](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:198), [211-233](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:211), [269-272](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:269), [292-294](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:292).

The invariance test correctly catches empty intersections, `n_both_called == 1`, all hom-ref, all het, and all hom-alt, assuming PLINK’s unphased allele-count `--r` is pairwise-complete: [lines 629-639](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:629).

`already_occluded` does not suppress enumeration; it is only an emitted flag: [lines 456-458](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/src/python/pairwise_completeness_scan.py:456).

**Tests**

Load-bearing tests: decoder packing/padding/seek tests [227-349](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/tests/m3/test_pairwise_completeness_scan.py:227), measured 00057 mirror [950-1021](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/tests/m3/test_pairwise_completeness_scan.py:950), partial-confounding gradient [1024-1062](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/tests/m3/test_pairwise_completeness_scan.py:1024), and proxy-refutation test [1091-1128](/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/tests/m3/test_pairwise_completeness_scan.py:1091).

Missing tests that matter: real PLINK oracle, founder/`--nonfounders` parity, region-edge clipping, duplicate IDs, exact 0.5 allele-frequency tie, overlapping regions, and retained `.snplist`/`--mac 1` parity.

Theatre/governance tests: docstring wording, pending-paste token checks, column tuple exactness, and egress width checks. They are useful process guards, but they do not reduce the false-negative risk.
