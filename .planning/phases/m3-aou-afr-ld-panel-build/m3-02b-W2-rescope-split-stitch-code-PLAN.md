---
phase: m3-aou-afr-ld-panel-build
plan: 02b
type: execute
wave: 0
depends_on: []
files_modified:
  - src/python/build_ld_region_manifest.py
  - src/python/select_ld_regions_dev.py
  - src/python/aou_ld_panel.py
  - src/scripts/stitch_subregions_to_rds.R
  - src/scripts/ld_npz_to_rds.R
  - .planning/notebooks/AOU-2_per_region_ld.ipynb
  - tests/m3/test_build_ld_region_manifest.py
  - tests/m3/test_stitch_subregions_to_rds.py
  - tests/m3/test_finemap_loader_contract.py
  - tests/m3/test_sparse_parent_benchmark.py
autonomous: true
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION

must_haves:
  truths:
    - "build_ld_region_manifest.py accepts --max-subregion-span-mb (default 10) and --split-classes xlarge; an xlarge region spanning >50 Mb is replaced in the manifest by N=ceil(core_span/max_span) compute rows. Each sub-region has a NON-OVERLAPPING CORE ownership interval (half-open [core_start_k, core_end_k)) and a COMPUTE WINDOW = core extended by buffer_bp on EACH side ([core_start_k - buffer_bp, core_end_k + buffer_bp], clamped to the parent). The cores tile the parent exactly (no gap, no overlap); the compute windows OVERLAP by buffer_bp. Every compute row carries buffer_bp = the region's radius_bp (the band/buffer knob)."
    - "A non-xlarge region (region_00006 at 17.7 Mb large; region_00027 medium) emits exactly ONE manifest row with NO __sub suffix — the 'only xlarge splits' decision is locked by test_nonxlarge_region_stays_whole."
    - "Each compute row carries provenance columns parent_region_id, subregion_index, n_subregions, core_start_grch38, core_end_grch38, window_start_grch38, window_end_grch38, buffer_bp; the compute row's start_grch38/end_grch38 = the WINDOW (so compute_region_ld computes pairs across the buffer), and radius_bp = buffer_bp. The projection TSV carries split_status in {whole, parent, subregion}; the parent xlarge region is emitted into the projection (split_status=parent) but NOT as a compute manifest row."
    - "buffer_bp is an explicit manifest column AND a CLI param (--subregion-buffer-mb, default = the region radius i.e. min(core_span+500kb, 50Mb)); the cost probe (m3-02c) measures the buffer's real cost and the radius-narrowing-to-10Mb-Pan-UKBB lever is the YELLOW disposition. A SMALL targeted research follow-up is flagged in the SUMMARY if the correct buffer width (AFR/EUR LD-decay horizon vs the formal 50 Mb radius) cannot be resolved from existing research."
    - "select_ld_regions_dev.py resolves dev picks from requested (parent_id, ancestry) tuples and expands a selected xlarge parent (e.g. m2_region_00040) into its __sub COMPUTE rows for that ancestry; the dev set is CAPPED (e.g. <=2 sub-rows per expanded parent + a configurable cap) so a 9-sub-region parent does not balloon the dev fire."
    - "stitch_subregions_to_rds.R assembles N sub-region .npz files for ONE parent + ancestry into ONE {parent_region_id}.rds whose payload satisfies the REAL loader run_susie_rss.R::load_ld_matrix(): it provides obj$R (the LD matrix) + obj$variants (a data.frame with at least CHR, POS, REF, ALT, SNP_ID). Assembly is BANDED (NOT block-diagonal): each pair (i,j) with one variant owned by a core and |pos_i - pos_j| <= buffer_bp is placed at its global (variant_i, variant_j) index; only pairs beyond buffer_bp are 0. Result is block-tridiagonal-like (intra-core blocks + cross-core band within buffer_bp). Variant membership = core ownership (each variant in exactly ONE core; no variant duplicated across windows). Provenance records cross_subregion_ld='banded within radius_bp; zeroed beyond'."
    - "The stitch is allele-aware: variants are ordered by GRCh38 variant_id (chr:pos:ref:alt) BEFORE liftover; uniqueness is exact; child-count and child-index coverage are exact; no variant is duplicated across windows (asserted); row/col permutation after liftover filtering is bijective; matching is on (CHR,POS,REF,ALT) not position-only. The alignment check is NOT skipped when ids are rsids."
    - "No whole-parent dense materialization of a 600k-var panel: the stitched obj$R is a sparse banded dgCMatrix; a benchmark (test_sparse_parent_benchmark on a realistically-sized fixture) records peak RAM, on-disk .rds size, read time, and the per-fine-map-window densification cost, proving the SuSiE wrapper densifies lazily per credible-set window rather than the whole parent."
    - "A Wave-0 verify task exercises the ACTUAL resolve_ld_path -> load_ld_matrix() -> susie_rss() path on a fixture (NOT a direct susie_rss() call): load_ld_matrix() returns obj$R+obj$variants, susie_rss() returns a credible set. This is NCSU-confirmable, no perimeter access. The existing ld_npz_to_rds.R whole-region payload is RECONCILED to the SAME R+variants schema so the whole-region path keeps working under the real loader."
    - "The AOU-2 notebook's executor-config cell sets PYSPARK_SUBMIT_ARGS BEFORE pyspark/hail import with spark.executor.cores=2, spark.executor.memory=24g (range 24-28g), spark.executor.memoryOverhead=10g (range 8-12g), spark.driver.memory=24g — the Q-RS2 n2-highmem-16 config, applied at probe time and validated on the probe (m3-02c)."
    - "compute_region_ld emits allele-frequency metadata in the .npz payload (allele_freq array, same row order as variant_ids); _save_npz asserts it present; the stitched .rds carries AF into obj$variants (an AF column). The phase deliverable is LD + AF metadata."
    - "The post-split COMPUTE WINDOW routes correctly via the REAL _route_region_path: a 10 Mb core + 2x buffer_bp window may exceed PATH_A2_MAX_MB (10 Mb) and demote to A.3; the worst-case dense scratch for the largest compute window is BOUNDED and asserted (no 65 GiB master crash). test_subregion_window_routes_via_real_router asserts the actual routed path per cell, not just region_class != xlarge."
    - "In the designated M3 conda env, missing R / Matrix / susieR makes the stitch + loader-contract + sparse-payload tests FAIL (no UNVERIFIED skip sentinel for must_have A6); the 'A6 confirmed' must_have cannot be satisfied by a skip."
    - "All named test families exist and pass against synthetic fixtures with no AoU/cluster access."
  artifacts:
    - path: "src/python/build_ld_region_manifest.py"
      provides: "Xlarge split: --max-subregion-span-mb/--split-classes/--subregion-buffer-mb CLI, core+window columns, buffer_bp, split_status projection"
      contains: "max-subregion-span-mb"
    - path: "src/python/select_ld_regions_dev.py"
      provides: "Dev selector resolving from (parent_id, ancestry) tuples + capped expansion of a split xlarge parent into __sub compute rows"
      contains: "parent_region_id"
    - path: "src/python/aou_ld_panel.py"
      provides: "AF metadata in the .npz payload (allele_freq array + _save_npz assertion)"
      contains: "allele_freq"
    - path: "src/scripts/stitch_subregions_to_rds.R"
      provides: "N sub-region .npz -> 1 parent .rds BANDED sparse stitch (cross-core band within buffer_bp; zeroed beyond) emitting obj$R + obj$variants(CHR,POS,REF,ALT,SNP_ID,AF) for the real loader; allele-aware ordering"
      min_lines: 120
    - path: "src/scripts/ld_npz_to_rds.R"
      provides: "Whole-region payload reconciled to obj$R + obj$variants(CHR,POS,REF,ALT,SNP_ID,AF) so load_ld_matrix() accepts it"
      contains: "variants"
    - path: "tests/m3/test_stitch_subregions_to_rds.py"
      provides: "test_stitch_banded_psd + test_stitch_cross_core_band_retained + test_stitch_allele_aware_alignment + test_stitch_no_duplicate_variant_across_windows + test_stitch_overlap_pair_agreement + test_stitch_sparse_payload + test_whole_region_unchanged"
      min_lines: 100
    - path: "tests/m3/test_finemap_loader_contract.py"
      provides: "A6 verify: resolve_ld_path -> load_ld_matrix() -> susie_rss() on a fixture returns obj$R+obj$variants and a credible set; NO skip in the M3 env"
    - path: "tests/m3/test_sparse_parent_benchmark.py"
      provides: "Realistically-sized fixture benchmark: peak RAM, .rds size, read time, lazy per-window densification cost (no whole-parent dense materialization)"
    - path: ".planning/notebooks/AOU-2_per_region_ld.ipynb"
      provides: "Executor-config cell (Q-RS2 cores=2 / 24-28g executor / 8-12g overhead) set via PYSPARK_SUBMIT_ARGS before pyspark import"
      contains: "spark.executor.cores=2"
  key_links:
    - from: "src/python/build_ld_region_manifest.py"
      to: "config/ld_regions.tsv compute rows"
      via: "window start/end as the compute interval + buffer_bp column per __sub row"
      pattern: "buffer_bp"
    - from: "src/scripts/stitch_subregions_to_rds.R"
      to: "{parent_region_id}.rds obj$R + obj$variants"
      via: "banded sparse assembly placing each pair within buffer_bp at its global index"
      pattern: "buffer_bp"
    - from: "src/scripts/stitch_subregions_to_rds.R"
      to: "run_susie_rss.R::load_ld_matrix()"
      via: "obj$R + obj$variants(CHR,POS,REF,ALT,SNP_ID,AF) payload schema"
      pattern: "variants"
    - from: "src/python/select_ld_regions_dev.py"
      to: "config/ld_regions_dev.tsv"
      via: "resolve (parent_id, ancestry) tuples then expand split parent into capped __sub rows"
      pattern: "__sub"
---

<objective>
Re-scope Wave 2 of M3 to make real-cohort LD compute tractable, code-side only (NCSU, no cluster, no AoU perimeter). The dev-10 fire was killed as a CAPACITY wall: the correlation matmul inner dimension IS the sample count (AFR 73,122 / EUR 220,098), so each block is ~36x (AFR) to ~110x (EUR) heavier than the 2,000-sample synthetic repro measured. The structural fix is to SPLIT the ~16 xlarge regions into ~10 Mb core sub-regions at manifest-build time (so each compute window routes off the A.3 dense-scratch path), compute on OVERLAPPING WINDOWS (core + buffer), STITCH the sub-region .npz files into one parent .rds via a BANDED sparse assembly (cross-core pairs WITHIN the buffer radius are RETAINED; only pairs beyond the radius are zeroed — the genuine WAVE-2 HIGH-3 treatment), and apply the Q-RS2 n2-highmem-16 executor config in the AOU-2 notebook.

REVISION (m3-REVIEWS.md, Codex HIGH #1-5/7 + MEDIUMs, Carter steering): the prior block-diagonal stitch was WRONG — it zeroed LD between variants base-pairs apart across an arbitrary 10 Mb boundary, a biologically false claim that can corrupt SuSiE-RSS credible sets while every test passed. Per Carter's locked steering, the MINIMAL CORRECT FIX is OVERLAPPING WINDOWS with cross-boundary variant pairs RETAINED inside the banding radius — a single per-parent BANDED panel, not block-diagonal, not independent sub-region fine-mapping. This revision also targets the REAL loader contract (run_susie_rss.R::load_ld_matrix expects obj$R + obj$variants, does as.matrix(R)), makes the parent panel sparse-banded (no whole-600k dense materialization), makes alignment allele-aware, fixes interval semantics, adds AF metadata to the output, and forbids critical-R-test skips in the M3 env.

This plan delivers EVERY code + test artifact named in m3-RESEARCH-W2-RESCOPE.md (Q-RS3 split, Q-RS4 stitch — re-interpreted as banded per the review, Q-RS2 executor config, A6 real-loader verify). It is fully executable now.

Purpose: This is the load-bearing structural change. Post-split, the manifest contains no xlarge whole-parent compute rows — only sub-region compute windows whose dense scratch is bounded (no 65 GiB scratch, no driver crash). The cost probe (m3-02c) measures the post-split throughput AND the buffer's real cost; the full 322-cell production fire stays OUT of scope here (Wave 4 / m3-04).

Output: split-aware manifest builder (core+window+buffer), the new banded sparse stitch script targeting the real loader, the whole-region payload reconciliation, AF metadata in the .npz/.rds, dev-subset expansion, the executor-config notebook cell, and the test families.

LOCKED (do NOT relitigate): the A.3 fix (_write_a3_banded_correlation_bm) is correct; ordering A is kept (banded==dense under span+500kb); the 3 cohort MTs are intact. The SPLIT itself is right — only the STITCH banding (was block-diagonal) is fixed to banded-within-radius. Splitting (not re-ordering) shrinks the dense intermediate.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/phases/m3-aou-afr-ld-panel-build/WAVE-2-RESCOPE-real-cohort-compute.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-REVIEWS.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
@.claude/skills/aou-ld-pipeline/SKILL.md

<interfaces>
<!-- Concrete contracts extracted from the source the executor will modify.
     Use these directly — no codebase scavenger hunt needed. -->

src/python/build_ld_region_manifest.py (existing):
- MANIFEST_COLUMNS = [region_id, chr, start_grch37, end_grch37, start_grch38,
  end_grch38, ancestry, source_trait, lead_variant, radius_bp, region_class,
  liftover_status]
- compute_radius_bp(start_b38, end_b38) -> min(span + 500_000, 50_000_000)
- derive_region_class(start_b38, end_b38) -> small <=5Mb / medium <=25Mb / large <=50Mb / xlarge >50Mb
- build_manifest(bed_df, chain, ancestries) -> (manifest_df, projection_df);
  projection row already has: region_id, chr, start/end x2, span_bp_grch38,
  span_mb_grch38, region_class, radius_bp, path_a_class, est_cluster_hours_per_ancestry, liftover_status
- parse_args() currently has: --bed --chain --out-manifest --out-projection --out-mapping --ancestries
- est_cluster_hours table (lines 346-357): small 0.5 / medium 1.5 / large 8.0 / xlarge 24.0 (KNOWN-STALE per Q-RS5; m3-02c redoes it)

src/python/select_ld_regions_dev.py (existing):
- AFR_KNOWN_REGIONS includes m2_region_00040 (an xlarge after the real BED liftover)
- EUR_OVERLAP_REGIONS includes m2_region_00040
- select_dev_rows(manifest_df) filters by region_id + ancestry; drops dups on [region_id, ancestry]

src/python/aou_ld_panel.py (existing — MODIFY for AF metadata + the routing assertion ONLY):
- compute_region_ld(region_row, mt_source, out_bucket) reads region_row["region_id"|"chr"|
  "start_grch38"|"end_grch38"|"radius_bp"|"region_class"] — sub-region COMPUTE rows flow through
  with start/end = the WINDOW (core + buffer) so cross-core pairs within buffer_bp ARE computed.
- INTERVAL SEMANTICS (load-bearing): line ~2193 builds
  `hl.parse_locus_interval(f"{chrom}:{start_b38}-{end_b38}", reference_genome="GRCh38")`.
  Hail locus intervals from "chr:start-end" are INCLUSIVE on BOTH ends ([start,end]) by default,
  NOT BED-style half-open. The core ownership intervals are half-open [core_start, core_end);
  reconcile the endpoint so adjacent cores neither duplicate nor drop the shared boundary variant.
- _route_region_path(region_class, span_mb): span_mb = (end-start)/1e6 of the COMPUTE window.
  PATH_A1_MAX_MB=5, PATH_A2_MAX_MB=10. Any A.1/A.2 with span_mb > 10 is HARD-DEMOTED to A.3.
  So a 10 Mb core + 2x10 Mb buffer = 30 Mb window -> A.3. ASSERT the routed path on the WINDOW.
- _save_npz(region_id, ld_np, variant_ids, rsids, ...) currently writes
  np.savez_compressed(ld=, variant_ids=, rsids=, lower_triangular=) — NO AF. Add allele_freq=.
- MIN_VARIANTS_PER_REGION = 10; _MIN_REGION_NPZ_BYTES = 256.
- The driver collects variant_ids+rsids in ONE aggregate_rows pass (vid = locus:ref:alt).
  AF must come from the SAME pass to preserve row-order alignment.

src/scripts/ld_npz_to_rds.R (existing; 1 npz -> 1 rds — RECONCILE the payload schema this plan):
- Current: saveRDS(list(ld=<matrix>, snp_ids=<chr vec>, provenance=<named list>), compress="xz").
- BROKEN under the real loader: load_ld_matrix() reads obj$R + obj$variants; obj$R is NULL here so
  the file is rejected. RECONCILE to list(R=<Matrix>, variants=<data.frame CHR,POS,REF,ALT,SNP_ID,AF>,
  snp_ids=<kept for back-compat>, provenance=...). Keep the symmetry recovery / chr-strip /
  GRCh38->37 liftover / drop-unmappable logic; just change the payload keys + add the variants frame.

THE REAL DOWNSTREAM LOADER — src/legacy/region_analysis/scripts/run_susie_rss.R::load_ld_matrix():
- candidate = file.path(ld_dir, ancestry, paste0(region_id, ".rds")) (or safe_region_id).
- obj <- readRDS(candidate); R <- obj$R; variants <- obj$variants.
- match_indices(subset, variants): matches on variants$SNP_ID first, then on variants$CHR + variants$POS.
  So obj$variants MUST be a data.frame/data.table with columns SNP_ID, CHR, POS (and we add REF, ALT, AF).
- On success: returns list(R = as.matrix(R), variants = variants[ld_idx,], ...) — DENSIFIES R via as.matrix.
  This is why the parent panel must densify LAZILY per-fine-map-window, not whole-parent (HIGH#2).
- Then run_susie_with_ladder(z, R, ...) -> susieR::susie_rss(z=, R=, ...). The A6 test must hit THIS path.

Q-RS3 split design (REVISED to overlapping windows):
- --max-subregion-span-mb default 10 (CORE width) ; --split-classes xlarge ;
  --subregion-buffer-mb default = the region radius (min(core_span+500kb, 50Mb)) = buffer_bp.
- region_id = f"{parent_id}__sub{k:02d}" e.g. m2_region_00040__sub00 .. __sub06.
- CORE ownership: half-open [core_start_k, core_end_k); cores tile the parent exactly.
- COMPUTE WINDOW: [core_start_k - buffer_bp, core_end_k + buffer_bp] clamped to parent; this is the
  compute row's start_grch38/end_grch38 so compute_region_ld computes the cross-core pairs in the buffer.
- density anchor: region_00006 = 17.7 Mb -> 122,678 var = ~6,930 var/Mb (AFR); 10 Mb core -> ~69k var.
- parent NOT emitted as a compute row; emitted into projection with split_status=parent, n_subregions=N.

Q-RS4 stitch design (REVISED to BANDED, per the review + Carter steering):
- For each parent+ancestry: load the N sub-region .npz (each computed on its WINDOW). For each variant,
  assign it to the ONE core whose [core_start,core_end) contains its GRCh38 pos (membership = dimnames set;
  no variant duplicated across windows). Global variant order = all core-owned variants sorted by GRCh38
  (chr,pos,ref,alt). For each computed pair (i,j) in any window with |pos_i - pos_j| <= buffer_bp AND
  at least one endpoint core-owned, place r at the global (i,j) index. Pairs beyond buffer_bp -> 0.
  Result = sparse BANDED dgCMatrix (block-tridiagonal-like). NOT Matrix::bdiag block-diagonal.
- cross_subregion_ld = "banded within radius_bp; zeroed beyond"
- keep sparse dgCMatrix; the SuSiE wrapper densifies lazily per credible-set window.

Q-RS2 executor config (n2-highmem-16, 16 vCPU / 128 GB) — applied in AOU-2 notebook:
- spark.executor.cores = 2 ; spark.executor.memory = 24-28g ; spark.executor.memoryOverhead = 8-12g ;
  spark.driver.memory = 24g ; block_size = Hail default 4096
- set via PYSPARK_SUBMIT_ARGS BEFORE pyspark/hail import (the baked project lever; hl.init(spark_conf=) is dropped on YARN)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Overlapping-window split in build_ld_region_manifest.py (core+window+buffer) + select_ld_regions_dev.py tuple-resolve + capped expansion + AF metadata in aou_ld_panel.py .npz + manifest/routing tests</name>
  <files>src/python/build_ld_region_manifest.py, src/python/select_ld_regions_dev.py, src/python/aou_ld_panel.py, tests/m3/test_build_ld_region_manifest.py</files>
  <read_first>
    - src/python/build_ld_region_manifest.py (FULL — MANIFEST_COLUMNS, parse_args, compute_radius_bp, derive_region_class, build_manifest lines 297-400, est_cluster_hours lines 346-357)
    - src/python/select_ld_regions_dev.py (FULL — AFR_KNOWN_REGIONS, EUR_OVERLAP_REGIONS, select_dev_rows)
    - src/python/aou_ld_panel.py lines 2135-2300 (compute_region_ld interval build + _route_region_path call + aggregate_rows pass) AND lines 2571-2610 (_save_npz)
    - src/python/aou_ld_panel.py lines 325-353 (_route_region_path: PATH_A2_MAX_MB veto)
    - tests/m3/test_build_ld_region_manifest.py (FULL — existing test patterns, fixtures)
    - tests/m3/conftest.py (union_bed_fixture, chain_fixture, synthetic-MT fixture if present)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS3" (lines 86-121) + the REVIEW's Carter-steering overlapping-window model in m3-REVIEWS.md
  </read_first>
  <behavior>
    - test_xlarge_region_splits_into_overlapping_windows: feed a synthetic 90 Mb xlarge BED row; assert N = ceil(90/10) = 9 compute rows; the 9 CORES are half-open [core_start_k, core_end_k), contiguous, non-overlapping, and tile [start_grch38, end_grch38) exactly (core_0 start == region start; core_{N-1} end == region end); each compute row's start_grch38/end_grch38 == its WINDOW = [core_start - buffer_bp, core_end + buffer_bp] clamped to the parent; adjacent windows OVERLAP by ~buffer_bp; every compute row region_id matches r"__sub\d{2}$".
    - test_core_intervals_are_half_open_and_tile: for a 25 Mb xlarge split at 10 Mb core, the 3 cores are [s, s+10M), [s+10M, s+20M), [s+20M, end); a variant exactly at core_1.start belongs to core_1 (not core_0); union of cores == [start,end) with no gap/overlap (test the shared-boundary endpoint explicitly).
    - test_compute_window_overlaps_by_buffer: window_k spans core_k +/- buffer_bp (clamped); window_0 start == max(region_start, core_0.start - buffer_bp); the overlap between window_k and window_{k+1} >= buffer_bp (so the cross-core band within buffer_bp is computed by BOTH).
    - test_buffer_bp_is_explicit_column_and_param: every compute row has buffer_bp column == the parsed --subregion-buffer-mb (default = the region radius); buffer_bp is grep-able in the manifest; NOT silently 50 Mb (assert buffer_bp != 50_000_000 when --subregion-buffer-mb 10 is passed).
    - test_nonxlarge_region_stays_whole: a 17.7 Mb (large) region and a medium region each emit exactly ONE manifest row per ancestry with NO "__sub" in region_id (locks "only xlarge splits").
    - test_subregion_provenance_columns: every __sub row has parent_region_id, subregion_index 0..N-1 (contiguous, unique), n_subregions == N (constant), core_start_grch38, core_end_grch38, window_start_grch38, window_end_grch38, buffer_bp; projection split_status: parent row == "parent", sub rows == "subregion", whole rows == "whole".
    - test_subregion_window_routes_via_real_router: import _route_region_path from aou_ld_panel; for each compute row compute span_mb of the WINDOW = (window_end - window_start)/1e6 and assert _route_region_path(region_class, span_mb) is the intended path; a 10 Mb core + 10 Mb buffer each side = 30 Mb window asserts == "A.3" (the router demotes >10 Mb). Assert the worst-case window dense scratch (window_n_var^2 * 4 bytes) is bounded below a stated ceiling (< 30 GiB, far under the 65 GiB master crash). Compute window_n_var with a CONSERVATIVE HLA-grade density of 13,000 var/Mb (NOT region_00006's ~6,930 var/Mb AFR anchor — HLA/6p21 m2_region_00145 on chr6 is much denser; 13,000 var/Mb brackets the HLA density band). NOTE: this is only the Wave-0 SIZING bound; the REAL per-cell density check is owned by the m3-02c preflight, which mandatorily counts region_00145.
    - test_subregion_ids_are_npz_safe: "m2_region_00040__sub00" matches r"[A-Za-z0-9_]+".
    - test_dev_selector_resolves_tuples_and_caps: select_dev_rows resolves from (parent_id, ancestry) tuples; a selected split parent (m2_region_00040, AFR) — absent as a compute row — is replaced by its __sub compute rows for AFR; the expanded count is CAPPED (<= the configured per-parent cap, e.g. 2); AFR and EUR sub-rows are NOT mixed for a single ancestry pick (the AFR pick yields only AFR sub-rows).
    - test_npz_payload_has_allele_freq: a synthetic compute_region_ld run (synthetic MT) writes a .npz containing an allele_freq array of length n_var aligned to variant_ids; _save_npz raises if allele_freq is missing/misaligned.
  </behavior>
  <action>
    In `src/python/build_ld_region_manifest.py`:

    1. Add CLI params in parse_args(): `--max-subregion-span-mb` (type=float, default=10.0, help="CORE window bp width in Mb for splitting xlarge regions; Q-RS3 density anchor 10 Mb ~= 69k AFR var < 75k"), `--split-classes` (default="xlarge"), and `--subregion-buffer-mb` (type=float, default=None, help="Banding buffer in Mb added to EACH side of a core to form the compute window; the band/buffer width and the single cost-vs-correctness knob. Default = the region radius min(core_span+500kb, 50Mb). The Pan-UKBB anchor bands at 10 Mb; the m3-02c cost probe measures this buffer's real cost and the narrow-to-10Mb lever is the YELLOW disposition. DO NOT silently keep 50 Mb.").

    2. Add `parent_region_id, subregion_index, n_subregions, core_start_grch38, core_end_grch38, window_start_grch38, window_end_grch38, buffer_bp` to MANIFEST_COLUMNS (after lead_variant, before radius_bp). For a WHOLE region: parent_region_id="" , subregion_index=-1, n_subregions=1, core_start/core_end = the region's own start/end, window_start/window_end = same, buffer_bp = the region radius. Assert the whole-region convention in test_nonxlarge_region_stays_whole.

    3. Add `split_region_overlapping(start_b38, end_b38, core_span_bp, buffer_bp) -> list[dict]` (sibling to derive_region_class): N = math.ceil((end_b38 - start_b38) / core_span_bp); produce N HALF-OPEN cores [core_start_k, core_end_k) of equal integer width tiling [start_b38, end_b38) exactly (core_0.start == start_b38; core_{N-1}.end == end_b38; last core absorbs the remainder; NO gap, NO overlap). For each core, window = (max(start_b38, core_start - buffer_bp), min(end_b38, core_end + buffer_bp)). Return per-sub dicts with core_start, core_end, window_start, window_end, subregion_index k, n_subregions N. DOCUMENT half-open core semantics in the docstring (a variant at exactly core_end belongs to the NEXT core).

    4. In build_manifest(): branch on `region_class in split_classes`:
       - WHOLE: today's behavior PLUS the new provenance columns (whole convention from step 2); projection split_status="whole".
       - SPLIT (xlarge): do NOT emit a compute row for the parent. Emit ONE projection row for the parent with split_status="parent", n_subregions=N. buffer_bp = parsed --subregion-buffer-mb if given else compute_radius_bp(core_start, core_end) for the parent's representative core. For k in 0..N-1: emit ancestry compute rows with region_id=f"{parent_id}__sub{k:02d}", start_grch38=window_start, end_grch38=window_end (the COMPUTE WINDOW — so compute_region_ld computes the cross-core buffer pairs), radius_bp=buffer_bp, region_class=derive_region_class(window_start, window_end) (the window may be 30 Mb -> "large"/"xlarge" by span; that's fine — the dense scratch is bounded by the WINDOW n_var, not the parent's), parent_region_id, subregion_index=k, n_subregions=N, core_start_grch38, core_end_grch38, window_start_grch38, window_end_grch38, buffer_bp. Projection row per sub with split_status="subregion" and path_a_class re-derived on the WINDOW span via the existing A.1/A.2/A.3 mapping.
       - Thread max_subregion_span_mb, split_classes, subregion_buffer_mb from main() into build_manifest().

    In `src/python/select_ld_regions_dev.py`:

    5. Refactor select_dev_rows to resolve from explicit (parent_id, ancestry) REQUEST TUPLES (build them from AFR_KNOWN_REGIONS x AFR, EUR_OVERLAP_REGIONS x EUR, plus the HLA-stress picks). For each request tuple: if (region_id, ancestry) exists as a compute row, take it; ELSE if manifest_df[(parent_region_id==region_id)&(ancestry==anc)] is non-empty (it was split), substitute its __sub compute rows for THAT ancestry only (never mix ancestries). Cap the substitution to the first `DEV_SUBREGION_CAP` (e.g. 2) sub-rows per expanded parent (sorted by subregion_index) so a 9-sub parent doesn't balloon the dev fire. Add `DEV_SUBREGION_CAP = 2` as a module constant.

    In `src/python/aou_ld_panel.py`:

    6. In compute_region_ld's single aggregate_rows pass (lines ~2245-2265), add `af=...` to the collected struct so AF is row-aligned with vid/rsid (use the AoU AF field if present in mt_r.row, e.g. hl.coalesce(mt_r.info.AF[0], <freq from call stats>) — read the MT row schema; if no precomputed AF field exists, compute call-stats AF via hl.agg.call_stats in the SAME pass or a coupled pass keyed identically). Collect allele_freq list aligned to variant_ids; assert len(allele_freq) == n_var. Pass allele_freq into _save_npz. In _save_npz, add parameter allele_freq, write `allele_freq=np.array(allele_freq)` into np.savez_compressed, and assert allele_freq is not None and len == ld_np.shape[0] (raise on misalignment). Keep float32 LD assertion unchanged.

    In `tests/m3/test_build_ld_region_manifest.py`:

    7. Add the manifest/routing/dev/AF behavior tests above. For the pure-logic core/window assertions call split_region_overlapping directly on hand-built coordinates (exact integer windows). For routing, import _route_region_path from src.python.aou_ld_panel and assert on the WINDOW span. For the AF test, use the synthetic-MT fixture + a synthetic out_local_dir and read back the .npz with np.load asserting 'allele_freq' in the keys. Keep all assertions on exact integers + grep-able column/key names.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_build_ld_region_manifest.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "max-subregion-span-mb" src/python/build_ld_region_manifest.py` returns >= 1.
    - `grep -c "subregion-buffer-mb\|subregion_buffer_mb\|buffer_bp" src/python/build_ld_region_manifest.py` returns >= 3.
    - `grep -c "core_start_grch38\|core_end_grch38\|window_start_grch38\|window_end_grch38" src/python/build_ld_region_manifest.py` returns >= 4.
    - `grep -c "def split_region_overlapping" src/python/build_ld_region_manifest.py` returns 1.
    - `grep -c "half-open\|half open\|\\[core_start" src/python/build_ld_region_manifest.py` returns >= 1 (documented core semantics).
    - `grep -c "__sub" src/python/build_ld_region_manifest.py` returns >= 1.
    - `grep -c "split_status" src/python/build_ld_region_manifest.py` returns >= 1.
    - `grep -c "DEV_SUBREGION_CAP\|parent_region_id" src/python/select_ld_regions_dev.py` returns >= 2.
    - `grep -c "allele_freq" src/python/aou_ld_panel.py` returns >= 3 (collect + savez + assertion).
    - `pytest tests/m3/test_build_ld_region_manifest.py -v` reports 0 failed; the named families test_xlarge_region_splits_into_overlapping_windows, test_core_intervals_are_half_open_and_tile, test_compute_window_overlaps_by_buffer, test_buffer_bp_is_explicit_column_and_param, test_nonxlarge_region_stays_whole, test_subregion_provenance_columns, test_subregion_window_routes_via_real_router, test_dev_selector_resolves_tuples_and_caps, test_npz_payload_has_allele_freq all PASS.
    - `pytest tests/m3 -q` reports 0 failed (no regression incl. existing aou_ld_panel + dev-selector tests; if an existing test pins the old .npz keys, UPDATE it to include allele_freq).
  </acceptance_criteria>
  <done>
    Manifest splits xlarge into overlapping-window __sub rows (half-open cores tiling the parent + core+/-buffer compute windows + explicit buffer_bp column/param, NOT silently 50 Mb); non-xlarge stays whole; the compute window's REAL routed path and bounded dense scratch are asserted; the dev selector resolves (parent,ancestry) tuples and caps expansion without mixing ancestries; the .npz payload carries row-aligned allele_freq with a _save_npz assertion; all named families pass; no regression.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: stitch_subregions_to_rds.R BANDED sparse assembly targeting the REAL loader (obj$R + obj$variants), allele-aware alignment, no-duplicate-across-windows + reconcile ld_npz_to_rds.R whole-region payload + banded/allele/loader tests</name>
  <files>src/scripts/stitch_subregions_to_rds.R, src/scripts/ld_npz_to_rds.R, tests/m3/test_stitch_subregions_to_rds.py</files>
  <read_first>
    - src/scripts/ld_npz_to_rds.R (FULL — symmetry recovery, chr-strip, GRCh38->37 liftover, dimnames, saveRDS schema; the stitch reuses these per-window steps AND this script's payload is reconciled here)
    - src/legacy/region_analysis/scripts/run_susie_rss.R lines 73-232 (load_ld_matrix: reads obj$R + obj$variants; match_indices uses variants$SNP_ID then variants$CHR+variants$POS; returns as.matrix(R)) — THE payload contract
    - src/python/aou_ld_panel.py lines 2237-2300 (.npz payload: ld, variant_ids[vid=locus:ref:alt], rsids, allele_freq, lower_triangular) + lines 2185-2222 (window interval + buffer_bp = radius_bp)
    - src/python/build_ld_region_manifest.py (the parent_region_id / subregion_index / core_start_grch38 / core_end_grch38 / buffer_bp columns the stitch reads)
    - **BINDING STITCH SPEC: `.planning/phases/m3-aou-afr-ld-panel-build/m3-REVIEWS.md` HIGH#1 (Codex, 2026-06-18) + Carter steering** — the stitch is OVERLAPPING-WINDOW BANDED (cross-boundary pairs within buffer_bp RETAINED), NOT block-diagonal. THIS task + m3-REVIEWS HIGH#1 are the authoritative spec.
    - m3-RESEARCH-W2-RESCOPE.md "Q-RS4" (lines 125-156) — SUBORDINATE / historical only: it documents the REJECTED `Matrix::bdiag` block-diagonal design (now carries a SUPERSEDED banner). Read it for the per-npz pipeline reuse (symmetry recovery, liftover, dimnames), NOT for the assembly model — the assembly is banded per m3-REVIEWS HIGH#1.
    - tests/m3/test_ld_npz_to_rds.py (existing converter test patterns; how .npz fixtures are built + .rds loaded back)
  </read_first>
  <behavior>
    - test_stitch_cross_core_band_retained: build 2 adjacent sub-region .npz with cores [0,10M) and [10M,20M), buffer_bp=5M; place two variants 1 kb apart STRADDLING the 10M boundary (one in each core) with a non-zero computed r in the overlapping window; stitch -> obj$R; assert R[straddle_i, straddle_j] == that non-zero r (NOT 0). This is the central correctness fix: cross-boundary pairs within buffer_bp are RETAINED, not zeroed.
    - test_stitch_zeroes_only_beyond_buffer: a pair with |pos_i - pos_j| > buffer_bp is exactly 0 in obj$R (genuine WAVE-2 HIGH-3 treatment); the matrix is sparse (banded), not block-diagonal (assert there EXIST non-zero cross-core entries within buffer_bp, so it is NOT bdiag).
    - test_stitch_banded_psd: obj$R is symmetric and (after the per-block correlation construction) eigenvalues >= -1e-6 on a small fixture; diagonal == 1.
    - test_stitch_allele_aware_alignment: variants ordered by GRCh38 (chr,pos,ref,alt) BEFORE liftover; obj$variants has columns CHR, POS, REF, ALT, SNP_ID, AF; matching across windows is on (CHR,POS,REF,ALT) (construct a fixture with a multiallelic site at the same pos but different ALT in two windows and assert they are NOT collapsed); the alignment check runs even when SNP_ID is an rsid (assert no skip path).
    - test_stitch_no_duplicate_variant_across_windows: a variant in the OVERLAP region (present in both window .npz files) appears exactly ONCE in obj$R/obj$variants — assigned to the ONE core that owns its position (half-open [core_start,core_end)); assert nrow(obj$variants) == sum of core-owned counts and no (CHR,POS,REF,ALT) key is duplicated.
    - test_stitch_overlap_pair_agreement: a GLOBAL pair whose BOTH endpoints fall inside the buffers of TWO neighboring windows is therefore computed TWICE (once per overlapping window); construct such a straddle pair, stitch -> obj$R, and assert (i) the two computed r values agree within 1e-4 (the step-5 reconciliation), (ii) the stitched matrix carries a SINGLE retained entry at that global (i,j) with the agreed r (not double-counted, not summed), and (iii) NO duplicate row/col is emitted for either endpoint (the de-dup of the duplicate-pair path).
    - test_stitch_sparse_payload: obj$R inherits "sparseMatrix" (dgCMatrix), round-trips through saveRDS/readRDS, dims == total core-owned variant count.
    - test_loader_accepts_stitched_payload: invoke run_susie_rss.R::load_ld_matrix() (source the R file, call the function) on the stitched .rds with a synthetic subset data.table (CHR,POS,SNP_ID); assert it returns a non-NULL R (as.matrix) + variants subset (NOT status ld_missing). This proves obj$R+obj$variants satisfies the REAL loader.
    - test_whole_region_payload_reconciled: ld_npz_to_rds.R on a 1-npz fixture now writes obj$R (a Matrix) + obj$variants(CHR,POS,REF,ALT,SNP_ID,AF); load_ld_matrix() accepts it (NOT ld_missing); back-compat obj$snp_ids still present.
  </behavior>
  <action>
    RECONCILE `src/scripts/ld_npz_to_rds.R` (whole-region path — HIGH#3):
    1. Change the saveRDS payload from list(ld, snp_ids, provenance) to list(R = <the symmetric Matrix>, variants = <data.frame>, snp_ids = <kept for back-compat>, provenance = ...). Build `variants` as a data.frame with columns SNP_ID (the rsid-or-vid), CHR, POS, REF, ALT parsed from the GRCh37 chr:pos:ref:alt id (rsids: fill CHR/POS from the pre-liftover vid if available, else NA — match_indices falls back to SNP_ID), and AF (read the .npz allele_freq array; align to kept rows after the liftover drop). Keep ALL existing logic (symmetry recovery, chr-strip, GRCh38->37 liftover, drop unmappable, dimnames). The dimnames(R) stay the b37 SNP_IDs. This makes the whole-region .rds satisfy load_ld_matrix().

    Create `src/scripts/stitch_subregions_to_rds.R` (NEW — banded, allele-aware):
    2. CLI: `Rscript src/scripts/stitch_subregions_to_rds.R --parent <parent_region_id> --ancestry <AFR|EUR> --out <out_rds> --chain <chain> --manifest <manifest_tsv> --npz <sub00.npz> --npz <sub01.npz> ...`. The --ancestry param is REQUIRED (AFR/EUR share sub-region ids — reject mixed). Read the manifest rows for (parent_region_id == parent) & (ancestry == anc) to get per-sub subregion_index, core_start_grch38, core_end_grch38, buffer_bp. REJECT: missing child (fewer .npz than n_subregions), duplicate child (two .npz for the same subregion_index), extra child (a .npz whose subregion_index is not in the parent's set), mixed ancestry (any .npz/manifest-row ancestry != anc) -> stop() with a STITCH_INPUT error.

    3. For each sub-region .npz, run the existing per-npz steps (numpy load via reticulate, symmetry recovery (M+t(M))/2, chr-strip, GRCh38->37 liftover, drop unmappable) to get the window's variants (each with GRCh38 chr:pos:ref:alt parsed to CHR,POS,REF,ALT, the b37 SNP_ID, AF from the npz allele_freq) + the window correlation block. ORDER all work by the GRCh38 variant_id (chr,pos,ref,alt) BEFORE liftover.

    4. CORE OWNERSHIP membership: for every variant seen across all windows, assign it to the ONE core whose half-open [core_start_grch38, core_end_grch38) (GRCh38 pos) contains it. The global variant set = the union of core-owned variants (each appears once — assert no (CHR,POS,REF,ALT) GRCh38 key is duplicated). Global order = sorted by GRCh38 (chr,pos,ref,alt). Build the global index map.

    5. BANDED assembly (NOT bdiag): initialize a sparse accumulator (build i/j/x triplets for a Matrix::sparseMatrix). For each window's computed pair (a, b) with computed correlation r: let ga, gb be the global indices of a and b (skip the pair if NEITHER endpoint is core-owned in THIS window's adjacency — but DO retain a pair where one endpoint is core-owned and the other is in the buffer of the neighbor, as long as |pos_a - pos_b| <= buffer_bp). Add (ga, gb, r) and (gb, ga, r) to the triplets when |pos_a - pos_b| <= buffer_bp. Where the same global pair is computed in two overlapping windows, they must agree (assert |r1 - r2| < 1e-4; keep one). Assemble `R <- Matrix::sparseMatrix(i, j, x=r, dims=c(M,M), symmetric=FALSE)` then symmetrize (R + t(R))/2 on the sparse form; set diag(R) <- 1. Result is a sparse banded dgCMatrix; pairs beyond buffer_bp are structurally absent (0). NEVER materialize the dense (M x M) form (a 615k-var parent dense is ~1.5 TB).

    6. dimnames(R) <- list(global_snp_ids_b37, global_snp_ids_b37). Build obj$variants = data.frame(SNP_ID=global_snp_ids_b37, CHR, POS (b37), REF, ALT, AF) in global order. Assert: nrow(variants) == nrow(R) == M; SNP_IDs unique; the (CHR,POS,REF,ALT) keys form a bijection with the row/col order (no duplicate, exact coverage of all core-owned children).

    7. Provenance named list: parent_region_id, ancestry, n_subregions = N, subregion_npz_paths, buffer_bp, cross_subregion_ld = "banded within radius_bp; zeroed beyond", chain_sha256, datetime, per-window n_var, M. saveRDS(list(R = R, variants = variants, snp_ids = global_snp_ids_b37, provenance = provenance), out_rds, compress = "xz").

    Create `tests/m3/test_stitch_subregions_to_rds.py` with the 8 behavior tests. Build adjacent sub-region .npz (np.savez_compressed with ld=window correlation block, variant_ids=chr:pos:ref:alt with the straddle pair 1 kb apart across the core boundary, rsids="", allele_freq aligned) + a manifest_tsv carrying subregion_index/core_start_grch38/core_end_grch38/buffer_bp per sub. Invoke the R script via subprocess; source run_susie_rss.R and ld_npz_to_rds.R for the loader-contract tests via a small Rscript one-liner or reticulate. In the M3 conda env, missing R/Matrix/susieR FAILS the stitch+loader+sparse tests (do NOT pytest.skip — use a module-level check that ERRORS if the M3 env R toolchain is absent, per the no-skip must_have; a non-M3 dev box may xfail but the M3 CI env must run them).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_stitch_subregions_to_rds.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `test -f src/scripts/stitch_subregions_to_rds.R` exits 0.
    - `grep -c "sparseMatrix\|dgCMatrix\|sparse" src/scripts/stitch_subregions_to_rds.R` returns >= 1 AND `grep -c "bdiag" src/scripts/stitch_subregions_to_rds.R` returns 0 (NOT block-diagonal).
    - `grep -c "banded within radius_bp; zeroed beyond" src/scripts/stitch_subregions_to_rds.R` returns >= 1.
    - `grep -c "buffer_bp" src/scripts/stitch_subregions_to_rds.R` returns >= 2.
    - `grep -c "core_start_grch38\|core_end_grch38\|core ownership\|half-open" src/scripts/stitch_subregions_to_rds.R` returns >= 2.
    - `grep -c "ancestry" src/scripts/stitch_subregions_to_rds.R` returns >= 2 (required param + mixed-ancestry reject).
    - `grep -c "STITCH_INPUT\|missing child\|duplicate child\|extra child" src/scripts/stitch_subregions_to_rds.R` returns >= 1.
    - `grep -c "variants" src/scripts/stitch_subregions_to_rds.R` returns >= 3 (obj$variants frame with CHR,POS,REF,ALT,SNP_ID,AF).
    - `grep -c "R = R\|R=R\|list(R" src/scripts/stitch_subregions_to_rds.R` returns >= 1 (obj$R payload key).
    - `grep -c "variants\b\|R = \|list(R" src/scripts/ld_npz_to_rds.R` returns >= 1 (whole-region payload reconciled to R+variants).
    - `grep -c "def test_stitch_overlap_pair_agreement" tests/m3/test_stitch_subregions_to_rds.py` returns 1 (the duplicate-pair reconciliation path is exercised).
    - `pytest tests/m3/test_stitch_subregions_to_rds.py -v` reports the named families test_stitch_cross_core_band_retained, test_stitch_zeroes_only_beyond_buffer, test_stitch_banded_psd, test_stitch_allele_aware_alignment, test_stitch_no_duplicate_variant_across_windows, test_stitch_overlap_pair_agreement, test_stitch_sparse_payload, test_loader_accepts_stitched_payload, test_whole_region_payload_reconciled all PASS (9 named stitch families; DO NOT skip in the M3 env — a skip on these fails the plan).
  </acceptance_criteria>
  <done>
    The new stitch script assembles N overlapping-window .npz into ONE sparse BANDED parent .rds with cross-core LD RETAINED within buffer_bp and zeroed beyond, allele-aware ordering, no variant duplicated across windows, emitting obj$R + obj$variants(CHR,POS,REF,ALT,SNP_ID,AF) that the REAL load_ld_matrix() accepts; ld_npz_to_rds.R whole-region payload is reconciled to the same R+variants schema; all named families pass without skipping in the M3 env.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: A6 real-loader verify (resolve_ld_path -> load_ld_matrix -> susie_rss on a fixture, no-skip) + sparse-parent benchmark (no whole-parent dense) + AOU-2 Q-RS2 executor-config cell</name>
  <files>tests/m3/test_finemap_loader_contract.py, tests/m3/test_sparse_parent_benchmark.py, .planning/notebooks/AOU-2_per_region_ld.ipynb</files>
  <read_first>
    - src/legacy/region_analysis/scripts/run_susie_rss.R (FULL — load_ld_matrix() obj$R+obj$variants contract, the candidate path resolution file.path(ld_dir, ancestry, region_id.rds), run_susie_with_ladder -> susieR::susie_rss)
    - src/snakemake/rules/finemap.smk (find the resolve_ld_path / ld_dir wiring + how run_susie_rss.R is invoked — confirm the resolver path the A6 test must exercise)
    - src/scripts/stitch_subregions_to_rds.R (from Task 2 — the sparse banded payload the benchmark loads)
    - .planning/notebooks/AOU-2_per_region_ld.ipynb (FULL — find the import/init cells where PYSPARK_SUBMIT_ARGS goes)
    - .planning/notebooks/AOU-1_template.ipynb Cell 1a (lines 54-63 — the BAKED PYSPARK_SUBMIT_ARGS pattern)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS2 Recommended executor configuration" (lines 67-83) + assumption A6 (line 227) + m3-REVIEWS.md HIGH #2 (intractable dense parent) + HIGH-tests-skip
    - .claude/skills/aou-ld-pipeline/SKILL.md "Baked-vs-manual edit table" + "feedback_aou_dataproc_pyspark_submit_args"
  </read_first>
  <behavior>
    - test_resolver_loads_and_susie_runs_on_stitched_parent: place a stitched banded sparse .rds (from the Task-2 script on a synthetic 2-window fixture) at the resolver's expected path (ld_dir/ancestry/{parent}.rds); build a synthetic subset sumstats data.table (CHR,POS,SNP_ID,BETA,SE) whose variants are covered by obj$variants; call the ACTUAL load_ld_matrix(ld_dir, ancestry, parent, subset) -> assert it returns non-NULL R (a dense as.matrix slice) + variants subset + overlap >= MIN_LD_OVERLAP; then call susieR::susie_rss(z, R, n) on the returned slice and assert it returns a fit with susie_get_cs(fit) yielding >= 0 credible sets (runs without error). This exercises the REAL resolver->loader->susie path, NOT a direct susie_rss() call.
    - test_loader_contract_no_skip_in_m3_env: if the M3 conda env is the active env, the test MUST run (R + Matrix + susieR + coloc present); a skip is a FAILURE. Detect the M3 env (e.g. envs/m3-r-ld.yml marker or susieR importability) and assert the toolchain is present rather than skipping.
    - test_no_whole_parent_dense_materialization: load the stitched sparse parent .rds; assert obj$R inherits sparseMatrix and is NOT a base dense matrix; assert object.size(obj$R) is far below the dense (M^2 * 8) bytes for the fixture M; the per-fine-map-window densification slices only the credible-set window's rows/cols (as.matrix on a sub-block), recorded in the benchmark.
    - test_sparse_parent_benchmark_records_metrics: on a realistically-sized fixture (e.g. M ~ 50k-75k banded), the benchmark records peak RAM (via resource/tracemalloc or /usr/bin/time), on-disk .rds size (bytes), readRDS time (s), and the cost of densifying ONE ~6k-var credible-set window; writes them to tests/m3/sparse_parent_benchmark.tsv; asserts peak RAM stays under a stated ceiling proving no whole-parent dense materialization.
  </behavior>
  <action>
    1. Write `tests/m3/test_finemap_loader_contract.py` (REPLACES the prior verdict-file approach — A6 is now answered by EXERCISING the loader, not a sentinel):
       - Generate a stitched banded sparse parent .rds via the Task-2 script on a 2-window synthetic fixture (or a small fixture builder helper).
       - Resolve the finemap.smk LD path convention (read finemap.smk for the ld_dir/ancestry/{region_id}.rds layout); place the .rds there.
       - source() run_susie_rss.R's load_ld_matrix into an R session (via subprocess Rscript or reticulate), call it on a synthetic subset, assert obj$R + obj$variants are returned and susie_rss runs and yields a credible set.
       - NO pytest.skip when the M3 R toolchain is present: add a module check `_require_m3_r_toolchain()` that ERRORS (not skips) if run inside the M3 env without susieR/Matrix/coloc. Outside the M3 env (e.g. a bare dev box) the test may xfail, but the must_have is the M3-env run.

    2. Write `tests/m3/test_sparse_parent_benchmark.py`:
       - Build a realistically-sized banded sparse fixture parent (M in the tens of thousands; do NOT build a full 615k dense — construct the sparse banded R directly in R/Python at the target M with a buffer_bp band).
       - Assert obj$R is sparse (not dense base matrix) and object.size << dense M^2*8.
       - Time readRDS, measure peak RAM during load + during a single ~6k-var window densification (as.matrix on the sub-block the SuSiE wrapper would slice), and write tests/m3/sparse_parent_benchmark.tsv with columns: M, rds_bytes, read_s, peak_ram_load_gib, window_var, densify_window_s, peak_ram_densify_gib. Assert peak_ram_load_gib < a stated ceiling (e.g. 8 GiB for the fixture) — the must_have "no whole-parent dense materialization."

    3. Add a new executor-config cell to `.planning/notebooks/AOU-2_per_region_ld.ipynb` (mirroring AOU-1 Cell 1a but with Q-RS2 LD-workload values). Insert BEFORE any `import hail`/pyspark import. Cell content (Python):
       ```python
       import os
       # Q-RS2 n2-highmem-16 LD-compute executor config (m3-W2 re-scope).
       # hl.init(spark_conf=dict) is silently dropped on AoU YARN; PYSPARK_SUBMIT_ARGS
       # before the pyspark/hail import is the only lever that binds
       # (feedback_aou_dataproc_pyspark_submit_args). NOTE: these are the LD-matmul
       # values (cores=2, big executor) — NOT the cohort-build cores=1/5g values in AOU-1.
       # Validated on the m3-02c cost probe; drop cores 2->1 if EUR (220k) spills.
       os.environ["PYSPARK_SUBMIT_ARGS"] = (
           "--conf spark.executor.cores=2 "
           "--conf spark.executor.memory=24g "
           "--conf spark.executor.memoryOverhead=10g "
           "--conf spark.driver.memory=24g "
           "pyspark-shell"
       )
       print("AOU-2 LD executor config (Q-RS2):", os.environ["PYSPARK_SUBMIT_ARGS"])
       ```
       Add a markdown cell immediately above noting: "Q-RS2 executor config — applied at probe time (m3-02c), tuned on the probe. block_size stays Hail default 4096." Preserve the existing notebook cells (nbformat-preserving insert; do not delete existing AOU-2 cells).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_finemap_loader_contract.py tests/m3/test_sparse_parent_benchmark.py -v --tb=short &amp;&amp; python -c "import json; nb=json.load(open('.planning/notebooks/AOU-2_per_region_ld.ipynb')); src=''.join(''.join(c.get('source',[])) for c in nb['cells']); assert 'spark.executor.cores=2' in src; assert 'PYSPARK_SUBMIT_ARGS' in src; print('OK')"</automated>
  </verify>
  <acceptance_criteria>
    - `pytest tests/m3/test_finemap_loader_contract.py -v` reports test_resolver_loads_and_susie_runs_on_stitched_parent + test_loader_contract_no_skip_in_m3_env PASS (NOT skipped in the M3 env).
    - `grep -c "load_ld_matrix" tests/m3/test_finemap_loader_contract.py` returns >= 1 (exercises the real loader, not a direct susie_rss call).
    - `grep -c "susie_rss\|susie_get_cs" tests/m3/test_finemap_loader_contract.py` returns >= 1 (credible set returned).
    - `grep -c "skip" tests/m3/test_finemap_loader_contract.py` shows no unconditional pytest.skip on the loader path (a _require_m3_r_toolchain ERROR, not skip).
    - `test -f tests/m3/sparse_parent_benchmark.tsv` exits 0 after the run; `head -1 tests/m3/sparse_parent_benchmark.tsv` contains rds_bytes, read_s, peak_ram_load_gib.
    - `pytest tests/m3/test_sparse_parent_benchmark.py -v` reports test_no_whole_parent_dense_materialization + test_sparse_parent_benchmark_records_metrics PASS.
    - `python -c "import json; nb=json.load(open('.planning/notebooks/AOU-2_per_region_ld.ipynb')); s=''.join(''.join(c.get('source',[])) for c in nb['cells']); assert 'spark.executor.cores=2' in s" && echo OK` prints OK.
    - `grep -c "spark.executor.memory=24g" .planning/notebooks/AOU-2_per_region_ld.ipynb` returns >= 1.
    - `grep -c "spark.executor.memoryOverhead=10g" .planning/notebooks/AOU-2_per_region_ld.ipynb` returns >= 1.
    - `grep -c "Q-RS2" .planning/notebooks/AOU-2_per_region_ld.ipynb` returns >= 1.
    - `python -c "import json; nb=json.load(open('.planning/notebooks/AOU-2_per_region_ld.ipynb'))" && echo VALID_JSON` prints VALID_JSON.
  </acceptance_criteria>
  <done>
    A6 is answered by EXERCISING resolve_ld_path -> load_ld_matrix() -> susie_rss() on a stitched-parent fixture (obj$R+obj$variants accepted, credible set returned), with NO skip allowed in the M3 env; the sparse-parent benchmark proves no whole-parent dense materialization (peak RAM bounded, lazy per-window densification) with recorded metrics; the AOU-2 notebook carries the Q-RS2 executor config before the pyspark import; notebook remains valid JSON.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Stitch input order -> SuSiE-RSS alignment | The stitched obj$R dimnames + obj$variants must match the z-score variant order downstream. A mis-ordered or position-only-matched stitch silently corrupts variant<->LD alignment fed to SuSiE-RSS. Mitigated by allele-aware (CHR,POS,REF,ALT) ordering + core-ownership de-dup. |
| Arbitrary window boundary -> false independence | The PRIOR block-diagonal stitch zeroed LD across an arbitrary 10 Mb boundary (variants base-pairs apart), fabricating independent signals / distorting PIPs. FIXED: banded assembly retains cross-core pairs within buffer_bp; only pairs beyond buffer_bp are zeroed. |
| Manifest compute window -> AoU driver dense scratch | The __sub compute WINDOW (core + 2x buffer) defines the in-perimeter dense scratch; an over-wide window re-creates the 65 GiB master crash. Mitigated by asserting the real routed path + bounded window dense scratch. |
| (Code-only plan; no AoU egress, no perimeter crossing here — those land in m3-02c / m3-04.) | The egress / VPC-SC threats are mitigated in the probe + production plans. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M3RS-STITCH-01 | Tampering / Integrity | stitch variant<->LD alignment | mitigate | Allele-aware ordering by GRCh38 (chr,pos,ref,alt) BEFORE liftover; exact uniqueness; child-count + child-index coverage; bijective row/col permutation after liftover filtering; matching on (CHR,POS,REF,ALT) not position-only; check NOT skipped for rsids; core-ownership guarantees no variant duplicated across windows. Locked by test_stitch_allele_aware_alignment + test_stitch_no_duplicate_variant_across_windows. |
| T-M3RS-STITCH-02 | Integrity | banded vs false-independence | mitigate | BANDED assembly (NOT bdiag): cross-core pairs within buffer_bp RETAINED at their global index; only pairs beyond buffer_bp zeroed (true >50 Mb linkage equilibrium). Each diagonal block is a Pearson correlation (PSD); symmetrize on sparse form; diag=1. test_stitch_cross_core_band_retained + test_stitch_zeroes_only_beyond_buffer + test_stitch_banded_psd lock it. |
| T-M3RS-STITCH-03 | Integrity | payload-loader mismatch | mitigate | Stitched + whole-region .rds emit obj$R + obj$variants(CHR,POS,REF,ALT,SNP_ID,AF) satisfying the REAL run_susie_rss.R::load_ld_matrix(); A6 verify exercises load_ld_matrix()->susie_rss() on a fixture (NOT a direct susie_rss call). test_loader_accepts_stitched_payload + test_whole_region_payload_reconciled + test_resolver_loads_and_susie_runs_on_stitched_parent. |
| T-M3RS-SPLIT-01 | Integrity | core coverage + window routing | mitigate | Half-open cores tile [start,end) exactly (no gap/overlap); compute window = core +/- buffer_bp; the REAL _route_region_path is asserted on the WINDOW span and the worst-case window dense scratch is bounded (no 65 GiB master crash). test_core_intervals_are_half_open_and_tile + test_subregion_window_routes_via_real_router. |
| T-M3RS-MEM-01 | DoS / OOM | whole-parent dense materialization | mitigate | obj$R is sparse banded dgCMatrix; the SuSiE wrapper densifies lazily per credible-set window (as.matrix on a sub-block), never the whole 600k-var parent. test_no_whole_parent_dense_materialization + the sparse-parent benchmark with a bounded peak-RAM ceiling. |
| T-M3RS-COST-01 | DoS / cost-overrun | post-split compute volume + buffer cost | accept (in this plan) | The split makes each window's dense scratch bounded; the buffer's real cost + the absolute 322-cell cost are GATED in m3-02c via PROJECTED x 1.3 <= BUDGET_CAP. The radius-narrow-to-10Mb lever ties to buffer_bp. This code plan ships the split + banding; the cost gate is the next plan. |
| T-M3RS-EGRESS-01 | Information disclosure | controlled-tier AoU genotypes | accept (out of scope here) | No data crosses the perimeter in this NCSU-only code plan. The phase deliverable LD + AF metadata is added to the output contract; egress review stays at m3-02c / m3-04 (REQ-AOU-LD-EGRESS). |
</threat_model>

<verification>
**Plan-level checks (all NCSU-local, no cluster):**

1. `pytest tests/m3/test_build_ld_region_manifest.py tests/m3/test_stitch_subregions_to_rds.py tests/m3/test_finemap_loader_contract.py tests/m3/test_sparse_parent_benchmark.py -v --tb=short` — all named families present and passing; the stitch + loader + sparse families MUST NOT skip in the M3 conda env.
2. Banded (not block-diagonal): `grep -c "bdiag" src/scripts/stitch_subregions_to_rds.R` returns 0; `grep -c "banded within radius_bp; zeroed beyond" src/scripts/stitch_subregions_to_rds.R` returns >= 1.
3. Real-loader payload: `grep -c "variants" src/scripts/stitch_subregions_to_rds.R` >= 3 AND the whole-region `ld_npz_to_rds.R` carries `R` + `variants` keys; `test_loader_accepts_stitched_payload` + `test_whole_region_payload_reconciled` pass.
4. AF metadata: `grep -c "allele_freq" src/python/aou_ld_panel.py` >= 3; the .npz + .rds carry AF.
5. Real routing asserted: `test_subregion_window_routes_via_real_router` imports the real `_route_region_path` and asserts on the WINDOW span + bounded dense scratch.
6. `pytest tests/m3 -q` — full m3 suite 0 failed (no regression).
7. REQ-PATH-PARAMETERIZATION: `grep -rn "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/build_ld_region_manifest.py src/python/select_ld_regions_dev.py src/scripts/stitch_subregions_to_rds.R src/scripts/ld_npz_to_rds.R` returns 0.
8. Notebook valid JSON + Q-RS2 cores=2 config (Task 3 acceptance).
</verification>

<success_criteria>
- build_ld_region_manifest.py splits xlarge into overlapping-window __sub rows: half-open cores tiling the parent + core+/-buffer compute windows + explicit buffer_bp column/param (NOT silently 50 Mb); non-xlarge stays whole.
- The compute window's REAL routed path and bounded dense scratch are asserted (no 65 GiB master crash).
- select_ld_regions_dev.py resolves (parent_id, ancestry) tuples and expands a split parent into capped __sub rows without mixing ancestries.
- compute_region_ld + _save_npz carry row-aligned allele_freq; the deliverable is LD + AF metadata.
- stitch_subregions_to_rds.R assembles N overlapping-window .npz into ONE sparse BANDED parent .rds (cross-core LD retained within buffer_bp, zeroed beyond) emitting obj$R + obj$variants(CHR,POS,REF,ALT,SNP_ID,AF) for the REAL loader; allele-aware; no variant duplicated across windows.
- ld_npz_to_rds.R whole-region payload reconciled to the same R+variants schema (whole-region path keeps working under load_ld_matrix()).
- A6 answered by exercising resolve_ld_path -> load_ld_matrix() -> susie_rss() on a fixture (NO skip in the M3 env).
- The sparse-parent benchmark proves no whole-parent dense materialization (bounded peak RAM, lazy per-window densification).
- AOU-2 notebook carries the Q-RS2 executor config (cores=2 / 24g / 10g / 24g) before pyspark import.
- No regression on the existing tests/m3 suite.
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-02b-W2-rescope-split-stitch-code-SUMMARY.md` recording:
- The exact CLI added (--max-subregion-span-mb, --split-classes, --subregion-buffer-mb defaults) + the new core/window/buffer manifest columns
- N sub-regions a real m2_region_00040 (or the largest xlarge) splits into at 10 Mb core; the compute-window span + its real routed path (A.1/A.2/A.3) + bounded dense scratch
- The buffer_bp default chosen and the radius-narrow-to-10Mb lever for m3-02c; **if the correct buffer width (AFR/EUR LD-decay horizon vs the formal 50 Mb radius) could NOT be resolved from existing research, FLAG a SMALL targeted research follow-up here** (do not guess silently)
- The A6 result: load_ld_matrix() accepts the banded sparse obj$R+obj$variants and susie_rss returns a credible set; the sparse-parent benchmark numbers (peak RAM, .rds size, read time, per-window densify cost)
- The whole-region payload reconciliation (ld_npz_to_rds.R now emits R+variants) and any downstream that read the old snp_ids/ld keys
- The test pass matrix (manifest/routing/dev/AF + banded/allele/loader + benchmark families), confirming NO skip on the R-dependent families in the M3 env
- Any sub-region the bp heuristic puts at risk of >75k var (e.g. HLA/6p21 region_00145 — flag for the probe to set --max-subregion-span-mb 7 on chr6)
</output>
