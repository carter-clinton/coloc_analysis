---
phase: m3-aou-afr-ld-panel-build
plan: 02b
type: execute
wave: 0
depends_on: []
files_modified:
  - src/python/build_ld_region_manifest.py
  - src/python/select_ld_regions_dev.py
  - src/scripts/stitch_subregions_to_rds.R
  - .planning/notebooks/AOU-2_per_region_ld.ipynb
  - tests/m3/test_build_ld_region_manifest.py
  - tests/m3/test_stitch_subregions_to_rds.py
  - tests/m3/test_finemap_sparse_ld_payload.py
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
    - "build_ld_region_manifest.py accepts --max-subregion-span-mb (default 10) and --split-classes xlarge; an xlarge region spanning >50 Mb is replaced in the manifest by N=ceil(span/max_span) contiguous non-overlapping __sub{k:02d} rows, each re-classed (no sub-row is xlarge), each radius recomputed on the sub-span."
    - "A non-xlarge region (region_00006 at 17.7 Mb large; region_00027 medium) emits exactly ONE manifest row with NO __sub suffix — the 'only xlarge splits' decision is locked by test_nonxlarge_region_stays_whole."
    - "Each sub-region row carries provenance columns parent_region_id, subregion_index, n_subregions, subregion_start_grch38, subregion_end_grch38; the projection TSV carries a split_status column in {whole, parent, subregion}; the parent xlarge region is emitted into the projection (split_status=parent) but NOT as a compute manifest row."
    - "select_ld_regions_dev.py expands a selected xlarge parent (e.g. m2_region_00040) into its __sub rows so the dev manifest exercises at least one sub-region path."
    - "stitch_subregions_to_rds.R assembles N sub-region .npz files for one parent into ONE {parent_region_id}.rds via sparse Matrix::bdiag block-diagonal; cross-sub-region off-diagonal entries are exactly 0; dimnames are the genomic-position-sorted concatenation of sub-region snp_ids in ascending subregion_index order; each diagonal block is PSD; the .rds ld payload is a sparse dgCMatrix; provenance records cross_subregion_ld='zeroed (block-diagonal; >50Mb LD treated as 0 per WAVE-2 HIGH-3)'."
    - "A Wave-0 verify task confirms the finemap.smk SuSiE-RSS wrapper accepts a sparse Matrix ld payload (assumption A6) — NCSU-confirmable, no perimeter access."
    - "The AOU-2 notebook's executor-config cell sets PYSPARK_SUBMIT_ARGS BEFORE pyspark/hail import with spark.executor.cores=2, spark.executor.memory=24g (range 24-28g), spark.executor.memoryOverhead=10g (range 8-12g), spark.driver.memory=24g — the Q-RS2 n2-highmem-16 config, applied at probe time and validated on the probe (m3-02c)."
    - "All 9 named test families exist and pass against synthetic fixtures with no AoU/cluster access: test_xlarge_region_splits_into_subregions, test_nonxlarge_region_stays_whole, test_subregion_provenance_columns, test_subregion_radius_is_subspan, test_subregion_ids_are_npz_safe, test_stitch_block_diagonal_psd, test_stitch_snp_id_ordering, test_stitch_sparse_payload, test_whole_region_unchanged."
  artifacts:
    - path: "src/python/build_ld_region_manifest.py"
      provides: "Xlarge split logic: --max-subregion-span-mb/--split-classes CLI, __sub{k:02d} sub-rows, provenance columns, split_status projection"
      contains: "max-subregion-span-mb"
    - path: "src/python/select_ld_regions_dev.py"
      provides: "Dev-subset selector that expands a selected xlarge parent into its __sub rows"
      contains: "subregion"
    - path: "src/scripts/stitch_subregions_to_rds.R"
      provides: "N sub-region .npz -> 1 parent .rds sparse block-diagonal stitch with position-sorted dimnames + PSD per-block + zeroed cross-block provenance"
      min_lines: 80
    - path: "tests/m3/test_stitch_subregions_to_rds.py"
      provides: "test_stitch_block_diagonal_psd + test_stitch_snp_id_ordering + test_stitch_sparse_payload + test_whole_region_unchanged"
      min_lines: 60
    - path: "tests/m3/test_finemap_sparse_ld_payload.py"
      provides: "A6 verify: finemap.smk SuSiE-RSS wrapper accepts a sparse Matrix ld payload"
    - path: ".planning/notebooks/AOU-2_per_region_ld.ipynb"
      provides: "Executor-config cell (Q-RS2 cores=2 / 24-28g executor / 8-12g overhead) set via PYSPARK_SUBMIT_ARGS before pyspark import"
      contains: "spark.executor.cores=2"
  key_links:
    - from: "src/python/build_ld_region_manifest.py"
      to: "config/ld_regions.tsv sub-rows"
      via: "parent_region_id column written per __sub row"
      pattern: "parent_region_id"
    - from: "src/scripts/stitch_subregions_to_rds.R"
      to: "{parent_region_id}.rds"
      via: "Matrix::bdiag block-diagonal assembly"
      pattern: "bdiag"
    - from: "src/python/select_ld_regions_dev.py"
      to: "config/ld_regions_dev.tsv"
      via: "expand selected xlarge parent into __sub rows"
      pattern: "__sub"
---

<objective>
Re-scope Wave 2 of M3 to make real-cohort LD compute tractable, code-side only (NCSU, no cluster, no AoU perimeter). The dev-10 fire was killed as a CAPACITY wall: the correlation matmul inner dimension IS the sample count (AFR 73,122 / EUR 220,098), so each block is ~36x (AFR) to ~110x (EUR) heavier than the 2,000-sample synthetic repro measured. The structural fix is to SPLIT the ~16 xlarge regions into ≤10 Mb sub-regions at manifest-build time (so no sub-region is A.3-dense-scratch), STITCH the sub-region .npz files back into one parent .rds via a sparse block-diagonal assembly (cross-sub-region LD beyond the 50 Mb radius is ≈0 — already the accepted WAVE-2 HIGH-3 treatment), and apply the Q-RS2 n2-highmem-16 executor config in the AOU-2 notebook.

This plan delivers EVERY code + test artifact named in m3-RESEARCH-W2-RESCOPE.md (Q-RS3 split, Q-RS4 stitch, Q-RS2 executor config, A6 sparse-payload verify) and the full 9-test-family suite. It is fully executable now.

Purpose: This is the load-bearing structural change. Post-split, the manifest contains no xlarge compute rows — only small/medium/sub-region rows that route to A.1/A.2 (no 65 GiB dense scratch, no driver crash). The cost probe (m3-02c) measures the post-split throughput; the full 322-cell production fire stays OUT of scope here (Wave 4 / m3-04).

Output: split-aware manifest builder, the new sparse stitch script, dev-subset expansion, the executor-config notebook cell, and 9 passing test families.

LOCKED (do NOT relitigate): the A.3 fix (_write_a3_banded_correlation_bm) is correct; ordering A is kept (banded==dense under span+500kb); the 3 cohort MTs are intact. Splitting (not re-ordering) shrinks the dense intermediate.
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
- derive_region_class(start_b38, end_b38) -> small ≤5Mb / medium ≤25Mb / large ≤50Mb / xlarge >50Mb
- build_manifest(bed_df, chain, ancestries) -> (manifest_df, projection_df);
  projection row already has: region_id, chr, start/end ×2, span_bp_grch38,
  span_mb_grch38, region_class, radius_bp, path_a_class, est_cluster_hours_per_ancestry, liftover_status
- parse_args() currently has: --bed --chain --out-manifest --out-projection --out-mapping --ancestries
- est_cluster_hours table (lines 346-357): small 0.5 / medium 1.5 / large 8.0 / xlarge 24.0 (KNOWN-STALE per Q-RS5; m3-02c redoes it)

src/python/select_ld_regions_dev.py (existing):
- AFR_KNOWN_REGIONS includes m2_region_00040 (an xlarge after the real BED liftover)
- select_dev_rows(manifest_df) filters by region_id + ancestry; drops dups on [region_id, ancestry]

src/python/aou_ld_panel.py (existing, consumes the manifest — do NOT modify in this plan):
- compute_region_ld(region_row, mt_source, out_bucket) reads region_row["region_id"|"chr"|
  "start_grch38"|"end_grch38"|"radius_bp"|"region_class"] — sub-region rows flow through unchanged
  (a __sub row is just a region with a smaller span and a non-xlarge class)
- _existing_region_npz / _save_npz key the .npz/.bm naming on region_id — __sub{k:02d} is npz-safe
- MIN_VARIANTS_PER_REGION = 10 — a sub-region that lands off-target is caught by the existing skip + _assert_blockmatrix_written

src/scripts/ld_npz_to_rds.R (existing; 1 npz -> 1 rds; do NOT modify — the stitch is a NEW sibling script):
- symmetry recovery (M + t(M))/2 ; chr-strip ; GRCh38->GRCh37 liftover ; drop unmappable ; dimnames ;
  saveRDS(list(ld=<matrix>, snp_ids=<chr vec>, provenance=<named list>), compress="xz")
- imports Matrix, reticulate, jsonlite, digest

Q-RS3 split design (verbatim):
- --max-subregion-span-mb default 10 ; --split-classes xlarge
- region_id = f"{parent_id}__sub{k:02d}" e.g. m2_region_00040__sub00 .. __sub06
- density anchor: region_00006 = 17.7 Mb -> 122,678 var = ~6,930 var/Mb (AFR); 10 Mb -> ~69k var (< 75k target)
- parent NOT emitted as a compute row; emitted into projection with split_status=parent, n_subregions=N

Q-RS4 stitch design (verbatim):
- Matrix::bdiag(block_0 .. block_{N-1}) sparse ; dimnames = concat(snp_ids_0 .. snp_ids_{N-1}) ascending index
- cross_subregion_ld = "zeroed (block-diagonal; >50Mb LD treated as 0 per WAVE-2 HIGH-3)"
- keep sparse dgCMatrix (a 615k-var parent dense form is ~1.5 TB -> OOM); sort by subregion_index column not filename

Q-RS2 executor config (n2-highmem-16, 16 vCPU / 128 GB) — applied in AOU-2 notebook:
- spark.executor.cores = 2 ; spark.executor.memory = 24-28g ; spark.executor.memoryOverhead = 8-12g ;
  spark.driver.memory = 24g ; block_size = Hail default 4096
- set via PYSPARK_SUBMIT_ARGS BEFORE pyspark/hail import (the baked project lever; hl.init(spark_conf=) is dropped on YARN)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Xlarge split logic in build_ld_region_manifest.py + select_ld_regions_dev.py expansion + 5 manifest test families</name>
  <files>src/python/build_ld_region_manifest.py, src/python/select_ld_regions_dev.py, tests/m3/test_build_ld_region_manifest.py</files>
  <read_first>
    - src/python/build_ld_region_manifest.py (FULL — MANIFEST_COLUMNS, parse_args, compute_radius_bp, derive_region_class, build_manifest lines 297-400, est_cluster_hours lines 346-357)
    - src/python/select_ld_regions_dev.py (FULL — AFR_KNOWN_REGIONS, select_dev_rows)
    - tests/m3/test_build_ld_region_manifest.py (FULL — existing test patterns, _run_reformatter helper)
    - tests/m3/conftest.py (union_bed_fixture, chain_fixture)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS3" (lines 86-121) — split design verbatim
  </read_first>
  <behavior>
    - test_xlarge_region_splits_into_subregions: feed a synthetic 90 Mb xlarge BED row (chr in fixture); assert N = ceil(90/10) = 9 sub-rows in the manifest; the 9 sub-windows are contiguous, non-overlapping, and exactly cover [start_grch38, end_grch38]; every sub-row region_class != "xlarge"; every sub-row region_id matches r"__sub\d{2}$".
    - test_nonxlarge_region_stays_whole: a 17.7 Mb (large) region and a medium region each emit exactly ONE manifest row per ancestry with NO "__sub" in region_id (locks "only xlarge splits").
    - test_subregion_provenance_columns: every __sub row has parent_region_id == the parent id, subregion_index in 0..N-1 (contiguous, unique), n_subregions == N (constant across siblings); projection has split_status column with the parent row == "parent" and sub rows == "subregion" and whole rows == "whole".
    - test_subregion_radius_is_subspan: a __sub row's radius_bp == compute_radius_bp(subregion_start_grch38, subregion_end_grch38) (≈ sub_span + 500kb, < parent radius) — NOT the parent's radius.
    - test_subregion_ids_are_npz_safe: "m2_region_00040__sub00" contains only [A-Za-z0-9_] (round-trips through the _save_npz/_existing_region_npz region_id key); assert re.fullmatch(r"[A-Za-z0-9_]+", rid).
  </behavior>
  <action>
    In `src/python/build_ld_region_manifest.py`:

    1. Add two CLI params in parse_args(): `--max-subregion-span-mb` (type=float, default=10.0, help="Sub-window bp width in Mb for splitting xlarge regions (Q-RS3 density anchor: 10 Mb ~= 69k AFR var < 75k target)") and `--split-classes` (default="xlarge", help="Comma-separated region_class values to split; non-listed classes stay whole").

    2. Add `parent_region_id, subregion_index, n_subregions, subregion_start_grch38, subregion_end_grch38` to MANIFEST_COLUMNS (after lead_variant, before radius_bp). For a WHOLE region these are: parent_region_id="" (or the region_id itself — pick the empty-string convention and assert it in the test), subregion_index=-1, n_subregions=1, subregion_start_grch38/subregion_end_grch38 = the region's own start/end.

    3. Add a `split_region(region_id, start_b38, end_b38, max_span_bp) -> list[tuple[int,int]]` helper (sibling to derive_region_class): N = math.ceil((end_b38 - start_b38) / max_span_bp); return N contiguous half-open windows of equal integer width covering [start_b38, end_b38] exactly (last window absorbs the remainder so windows[-1][1] == end_b38 and windows[0][0] == start_b38; no gaps, no overlap).

    4. In build_manifest(): after computing region_class for a region, branch on `region_class in split_classes`:
       - NOT split (whole): emit exactly today's behavior PLUS the 5 new provenance columns (whole convention from step 2); projection row gets split_status="whole".
       - split (xlarge): do NOT emit a compute manifest row for the parent. Emit ONE projection row for the parent with split_status="parent", n_subregions=N, and the parent's own span/class. Then for k in 0..N-1 with (sub_start, sub_end) = windows[k]: re-derive sub_radius = compute_radius_bp(sub_start, sub_end), sub_class = derive_region_class(sub_start, sub_end) (will be small/medium since sub_span ≤ 10 Mb), and emit ancestry manifest rows with region_id=f"{parent_id}__sub{k:02d}", start_grch38=sub_start, end_grch38=sub_end, radius_bp=sub_radius, region_class=sub_class, parent_region_id=parent_id, subregion_index=k, n_subregions=N, subregion_start_grch38=sub_start, subregion_end_grch38=sub_end. Also emit a projection row per sub-region with split_status="subregion" (re-derive path_a_class on sub_class via the existing A.1/A.2/A.3 mapping — sub-regions will be A.1/A.2, NOT A.3).
       - Thread `max_subregion_span_mb` and `split_classes` (parsed from the comma string) from main() into build_manifest().

    In `src/python/select_ld_regions_dev.py`:

    5. After select_dev_rows builds the AFR-known/EUR-overlap/HLA-stress picks, add an expansion step: for any selected region_id that does NOT appear as a compute row in the manifest but whose `{region_id}__sub*` rows DO appear (i.e. it was split), replace the selected row with all its __sub rows for that ancestry. Implement by: detect split parents via `manifest_df["parent_region_id"]`; if a selected (region_id, ancestry) is absent but `manifest_df[(parent_region_id==region_id) & (ancestry==anc)]` is non-empty, substitute those sub-rows. This guarantees the dev manifest exercises ≥1 sub-region (m2_region_00040 is xlarge in AFR_KNOWN_REGIONS).

    In `tests/m3/test_build_ld_region_manifest.py`:

    6. Add the 5 behavior tests above. Build a synthetic 90 Mb xlarge BED fixture inline (or extend conftest) — a single chr row with end-start = 90_000_000 in GRCh38-mappable coordinates; if the existing chain fixture can't map a synthetic 90 Mb span cleanly, construct the manifest_df by calling build_manifest on a hand-built bed_df + a stubbed chain (monkeypatch liftover_region to identity for the synthetic coords), OR call split_region + derive_region_class directly for the pure-logic assertions and reserve the full-pipeline assertion for the contiguity/coverage check. Keep all assertions on exact integer windows + grep-able column names.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_build_ld_region_manifest.py -v --tb=short -k "split or subregion or whole or npz_safe"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "max-subregion-span-mb" src/python/build_ld_region_manifest.py` returns ≥ 1.
    - `grep -c "split-classes\|split_classes" src/python/build_ld_region_manifest.py` returns ≥ 1.
    - `grep -c "parent_region_id" src/python/build_ld_region_manifest.py` returns ≥ 2 (MANIFEST_COLUMNS + emit).
    - `grep -c "subregion_index\|n_subregions\|subregion_start_grch38\|subregion_end_grch38" src/python/build_ld_region_manifest.py` returns ≥ 4.
    - `grep -c "split_status" src/python/build_ld_region_manifest.py` returns ≥ 1.
    - `grep -c "def split_region" src/python/build_ld_region_manifest.py` returns 1.
    - `grep -c "__sub" src/python/build_ld_region_manifest.py` returns ≥ 1 (the f"{parent_id}__sub{k:02d}" pattern).
    - `grep -c "parent_region_id\|__sub" src/python/select_ld_regions_dev.py` returns ≥ 1 (dev expansion).
    - `pytest tests/m3/test_build_ld_region_manifest.py -k "split or subregion or whole or npz_safe"` reports ≥ 5 passed, 0 failed.
    - `pytest tests/m3/test_build_ld_region_manifest.py` (full file) reports 0 failed (no regression on the existing manifest tests).
  </acceptance_criteria>
  <done>
    The manifest builder splits xlarge regions into __sub{k:02d} rows with full provenance; non-xlarge regions stay whole; the dev selector expands a selected xlarge parent; 5 manifest test families pass; no regression on existing manifest/dev-selector tests.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: stitch_subregions_to_rds.R sparse block-diagonal assembly + 4 stitch test families</name>
  <files>src/scripts/stitch_subregions_to_rds.R, tests/m3/test_stitch_subregions_to_rds.py</files>
  <read_first>
    - src/scripts/ld_npz_to_rds.R (FULL — the 1-npz->1-rds pipeline: symmetry recovery, chr-strip, GRCh38->GRCh37 liftover, dimnames, saveRDS list(ld, snp_ids, provenance) schema; the stitch reuses these per-block steps)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS4" (lines 125-156) — stitch design verbatim
    - tests/m3/test_ld_npz_to_rds.py (existing converter test patterns; how .npz fixtures are built + how the .rds is loaded back for assertions)
    - src/python/build_ld_region_manifest.py (the parent_region_id / subregion_index columns the stitch sorts by)
  </read_first>
  <behavior>
    - test_stitch_block_diagonal_psd: two synthetic sub-region .npz blocks (each a small correlation matrix) -> stitch -> load the .rds; assert the ld matrix is symmetric, every eigenvalue ≥ -1e-6 (PSD), and every cross-block off-diagonal entry (rows of block 0 × cols of block 1) is exactly 0.
    - test_stitch_snp_id_ordering: the stitched snp_ids are the concatenation of the sub-region snp_ids in ascending subregion_index order and are monotonic in genomic position; a deliberately mis-ordered input (sub01 passed before sub00) either raises OR the script sorts by subregion_index and still yields the correct monotonic order — assert the monotonic-position invariant holds on output.
    - test_stitch_sparse_payload: the stitched .rds `ld` is a sparse Matrix (inherits "sparseMatrix" / is a dgCMatrix), round-trips through saveRDS/readRDS, and reports the same dims as sum(n_k).
    - test_whole_region_unchanged: a single non-split region run through the EXISTING ld_npz_to_rds.R still produces a dense .rds with the same schema (no regression — the stitch script is additive, the whole-region path is untouched). Assert by running ld_npz_to_rds.R on a 1-npz fixture and checking is.matrix(ld) (dense) + the list schema.
  </behavior>
  <action>
    Create `src/scripts/stitch_subregions_to_rds.R` (NEW — do NOT modify ld_npz_to_rds.R):

    1. CLI: `Rscript src/scripts/stitch_subregions_to_rds.R <parent_region_id> <out_rds_path> <chain_path> <manifest_tsv> <sub00.npz> <sub01.npz> ...` — OR accept a `--stitch` style arg list. The manifest_tsv supplies the subregion_index per .npz so ordering is by the COLUMN, not the filename (Q-RS4 rec 4).

    2. For each sub-region .npz, run the EXISTING per-npz pipeline (reuse the logic from ld_npz_to_rds.R: numpy load via reticulate, symmetry recovery (M + t(M))/2, chr-strip, GRCh38->GRCh37 liftover via pyliftover on chain_path, drop unmappable, set per-block dimnames) to obtain a (n_k x n_k) block matrix + its snp_ids_k vector. Convert each block to a sparse Matrix via `Matrix::Matrix(block, sparse = TRUE)` (or `as(block, "dgCMatrix")`).

    3. Sort the blocks by subregion_index (read from manifest_tsv, matched to the parent_region_id), ascending. Assemble `ld <- Matrix::bdiag(block_0, ..., block_{N-1})` — this keeps the cross-block off-diagonal exactly 0 (block-diagonal banding) and stays sparse (never materializes the (sum n_k)^2 dense form; a 615k-var parent dense is ~1.5 TB -> OOM).

    4. Set global `dimnames(ld) <- list(all_ids, all_ids)` where all_ids = c(snp_ids_0, ..., snp_ids_{N-1}) in ascending subregion_index order. Add an assertion that the concatenated ids are monotonic non-decreasing in genomic position (parse chr:pos from chr:pos:ref:alt ids; for rsids skip the check or resolve via the npz order which the driver guarantees) — raise stop("STITCH_ORDER: non-monotonic snp position at index ...") if violated, to catch a mis-ordered stitch (the silent variant↔LD misalignment threat).

    5. PSD: rely on each diagonal block being a Pearson correlation matrix (PSD by construction up to float noise); do NOT regularize across the zeroed off-diagonal (that would re-introduce spurious cross-block LD). Apply the same (M + t(M))/2 symmetrization per block that ld_npz_to_rds.R uses.

    6. Provenance: build the named list with `parent_region_id`, `n_subregions = N`, `subregion_npz_paths = <the N input paths>`, `cross_subregion_ld = "zeroed (block-diagonal; >50Mb LD treated as 0 per WAVE-2 HIGH-3)"`, plus the chain_sha256 + datetime + per-block n_var fields mirroring ld_npz_to_rds.R provenance. saveRDS(list(ld = ld, snp_ids = all_ids, provenance = provenance), out_rds_path, compress = "xz").

    Create `tests/m3/test_stitch_subregions_to_rds.py` with the 4 behavior tests. Build 2-3 synthetic sub-region .npz files (np.savez_compressed with `ld` lower-triangular small correlation blocks + `variant_ids` chr:pos:ref:alt strings with ascending positions + `rsids` empty strings) under tmp_path, write a tiny manifest_tsv with subregion_index, invoke the R script via subprocess (Rscript), readRDS via reticulate or a small R one-liner, and assert the invariants. Gate on Rscript availability with pytest.skip if r-base/Matrix is not importable (matches the existing ld_npz_to_rds test gating pattern).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_stitch_subregions_to_rds.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `test -f src/scripts/stitch_subregions_to_rds.R` exits 0.
    - `grep -c "bdiag" src/scripts/stitch_subregions_to_rds.R` returns ≥ 1.
    - `grep -c "dgCMatrix\|sparse = TRUE\|sparse=TRUE" src/scripts/stitch_subregions_to_rds.R` returns ≥ 1.
    - `grep -c "cross_subregion_ld" src/scripts/stitch_subregions_to_rds.R` returns ≥ 1.
    - `grep -c "zeroed (block-diagonal; >50Mb LD treated as 0 per WAVE-2 HIGH-3)" src/scripts/stitch_subregions_to_rds.R` returns ≥ 1.
    - `grep -c "subregion_index" src/scripts/stitch_subregions_to_rds.R` returns ≥ 1 (sort by column, not filename).
    - `grep -c "STITCH_ORDER\|monotonic" src/scripts/stitch_subregions_to_rds.R` returns ≥ 1 (mis-order assertion).
    - `grep -c "parent_region_id\|n_subregions\|subregion_npz_paths" src/scripts/stitch_subregions_to_rds.R` returns ≥ 3.
    - `pytest tests/m3/test_stitch_subregions_to_rds.py -v` reports ≥ 4 passed (or skipped if Rscript unavailable — but at least test_whole_region_unchanged + the python-side ordering assertion run).
  </acceptance_criteria>
  <done>
    The new stitch script assembles N sub-region .npz into one sparse block-diagonal parent .rds with zeroed cross-block LD, position-sorted dimnames, PSD per-block, and audit provenance; 4 stitch test families pass; ld_npz_to_rds.R (whole-region path) is unchanged.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: A6 finemap sparse-payload verify + AOU-2 Q-RS2 executor-config cell</name>
  <files>tests/m3/test_finemap_sparse_ld_payload.py, .planning/notebooks/AOU-2_per_region_ld.ipynb</files>
  <read_first>
    - src/snakemake/rules/finemap.smk (the SuSiE-RSS wrapper / ld_panel resolver — find where the .rds ld payload is loaded and passed to susie_rss; confirm whether it requires a base matrix or accepts a Matrix)
    - tests/m3/test_ld_panel_resolver.py (existing resolver test patterns)
    - .planning/notebooks/AOU-2_per_region_ld.ipynb (FULL — the existing cells; find the import/init cells where PYSPARK_SUBMIT_ARGS would go)
    - .planning/notebooks/AOU-1_template.ipynb Cell 1a (lines 54-63 — the BAKED PYSPARK_SUBMIT_ARGS pattern to mirror, but with the Q-RS2 LD-workload values, NOT the cores=1/5g cohort-build values)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS2 Recommended executor configuration" (lines 67-83) + assumption A6 (line 227)
    - .claude/skills/aou-ld-pipeline/SKILL.md "Baked-vs-manual edit table" + "feedback_aou_dataproc_pyspark_submit_args"
  </read_first>
  <behavior>
    - test_finemap_accepts_sparse_ld_payload: construct a small sparse Matrix::dgCMatrix LD payload + matching z-score vector aligned by dimnames; invoke the finemap.smk SuSiE-RSS wrapper path (or the R loader it calls) and assert it either accepts the sparse Matrix directly OR documents the coercion point. If the wrapper requires a dense base matrix, the test asserts the EXPECTED fallback (sparse banded form densified lazily inside the wrapper) and the test records A6=FALSE in a committed note so m3-04 knows xlarge .rds must densify. The test's pass condition is: the A6 question is ANSWERED with a grep-able verdict (A6_SPARSE_OK = TRUE or FALSE) written to tests/m3/A6_sparse_payload_verdict.txt.
  </behavior>
  <action>
    1. Write `tests/m3/test_finemap_sparse_ld_payload.py` that resolves assumption A6 (m3-RESEARCH-W2-RESCOPE.md line 227, Q-RS4 line 155 — "make it a Wave-0 verify task"): inspect the finemap.smk SuSiE-RSS wrapper and determine whether `susieR::susie_rss()` (or the project wrapper) accepts a sparse `Matrix` as the `R` LD argument. Build a synthetic sparse dgCMatrix block-diagonal LD (via R `Matrix::bdiag`) + an aligned z vector, run it through the wrapper (or the minimal R call the wrapper makes), and write the verdict to `tests/m3/A6_sparse_payload_verdict.txt` (content: "A6_SPARSE_OK=TRUE" or "A6_SPARSE_OK=FALSE; fallback=densify-lazily-in-wrapper"). The pytest asserts the verdict file exists and contains one of the two sentinels. Gate on susieR/Rscript availability with pytest.skip if not installed, but ALWAYS write the verdict file (skip -> "A6_SPARSE_OK=UNVERIFIED-NO-R-ENV" so m3-04 sees the gap).

    2. Add a new executor-config cell to `.planning/notebooks/AOU-2_per_region_ld.ipynb` (mirroring the AOU-1 Cell 1a baked pattern but with Q-RS2 LD-workload values). Insert it BEFORE any `import hail` / pyspark import in AOU-2. Cell content (Python):
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
       Add a markdown cell immediately above it noting: "Q-RS2 executor config — applied at probe time (m3-02c), tuned on the probe. block_size stays Hail default 4096." Preserve the existing notebook cells (nbformat-preserving insert; do not delete the existing AOU-2 cells).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_finemap_sparse_ld_payload.py -v --tb=short &amp;&amp; python -c "import json; nb=json.load(open('.planning/notebooks/AOU-2_per_region_ld.ipynb')); src=''.join(''.join(c.get('source',[])) for c in nb['cells']); assert 'spark.executor.cores=2' in src; assert 'PYSPARK_SUBMIT_ARGS' in src; print('OK')"</automated>
  </verify>
  <acceptance_criteria>
    - `pytest tests/m3/test_finemap_sparse_ld_payload.py -v` reports 1 passed (or skipped-with-verdict-written).
    - `test -f tests/m3/A6_sparse_payload_verdict.txt` exits 0 and `grep -c "A6_SPARSE_OK=" tests/m3/A6_sparse_payload_verdict.txt` returns ≥ 1.
    - `python -c "import json; nb=json.load(open('.planning/notebooks/AOU-2_per_region_ld.ipynb')); s=''.join(''.join(c.get('source',[])) for c in nb['cells']); assert 'spark.executor.cores=2' in s" && echo OK` prints OK.
    - `grep -c "spark.executor.memory=24g" .planning/notebooks/AOU-2_per_region_ld.ipynb` returns ≥ 1.
    - `grep -c "spark.executor.memoryOverhead=10g" .planning/notebooks/AOU-2_per_region_ld.ipynb` returns ≥ 1.
    - `grep -c "Q-RS2" .planning/notebooks/AOU-2_per_region_ld.ipynb` returns ≥ 1.
    - `python -c "import json; nb=json.load(open('.planning/notebooks/AOU-2_per_region_ld.ipynb'))" && echo VALID_JSON` prints VALID_JSON (notebook still valid).
  </acceptance_criteria>
  <done>
    The A6 sparse-payload question is answered with a committed grep-able verdict; the AOU-2 notebook carries the Q-RS2 executor config (cores=2 / 24g / 10g overhead / 24g driver) set via PYSPARK_SUBMIT_ARGS before the pyspark import; notebook remains valid JSON.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Stitch input order → SuSiE-RSS alignment | The stitched .rds dimnames must match the z-score variant order downstream. A mis-ordered bdiag silently corrupts variant↔LD alignment fed to SuSiE-RSS. |
| Manifest sub-region rows → AoU compute driver | The __sub rows define what gets computed in-perimeter; an off-target split would compute the wrong genomic window. |
| (Code-only plan; no AoU egress, no perimeter crossing in this plan — those land in m3-02c / m3-04.) | The egress / VPC-SC threats are mitigated in the probe + production plans, not here. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M3RS-STITCH-01 | Tampering / Integrity | stitch_subregions_to_rds.R bdiag ordering | mitigate | Sort blocks by the subregion_index manifest COLUMN (not filename); assert concatenated snp_ids are monotonic non-decreasing in genomic position and stop("STITCH_ORDER") on violation (Task 2); test_stitch_snp_id_ordering locks it. |
| T-M3RS-STITCH-02 | Integrity | block-diagonal PSD / cross-block zeros | mitigate | Each diagonal block is a Pearson correlation matrix (PSD by construction); cross-block off-diagonal exactly 0 (encodes >50Mb linkage equilibrium, true); NO regularization across the zeroed off-diagonal; test_stitch_block_diagonal_psd asserts eigenvalues ≥ -1e-6 + cross-block == 0. |
| T-M3RS-SPLIT-01 | Integrity | xlarge split window coverage | mitigate | split_region emits contiguous non-overlapping windows that exactly cover [start,end] (windows[0][0]==start, windows[-1][1]==end); test_xlarge_region_splits_into_subregions asserts coverage + contiguity; radius re-derived per sub-span (test_subregion_radius_is_subspan). |
| T-M3RS-COST-01 | DoS / cost-overrun | post-split compute volume | accept (in this plan) | The split makes each cell tractable (no 65 GiB dense scratch); the absolute 322-cell cost is GATED in m3-02c via the PROJECTED × 1.3 ≤ BUDGET_CAP go/no-go. This code plan only ships the split; the cost gate is the next plan. |
| T-M3RS-EGRESS-01 | Information disclosure | controlled-tier AoU genotypes | accept (out of scope here) | No data crosses the perimeter in this NCSU-only code plan. Egress (summary LD + AF only, never individual genotypes; REQ-AOU-LD-EGRESS) is mitigated at the m3-02c probe + m3-04 production fire via the AoU Files-UI per-bundle review. |
</threat_model>

<verification>
**Plan-level checks (all NCSU-local, no cluster):**

1. `pytest tests/m3/test_build_ld_region_manifest.py tests/m3/test_stitch_subregions_to_rds.py tests/m3/test_finemap_sparse_ld_payload.py -v --tb=short` — all 9 named test families present and passing (Rscript-gated tests may skip but must write their verdict/skip sentinel).
2. All 9 family names appear: `grep -roh "test_xlarge_region_splits_into_subregions\|test_nonxlarge_region_stays_whole\|test_subregion_provenance_columns\|test_subregion_radius_is_subspan\|test_subregion_ids_are_npz_safe\|test_stitch_block_diagonal_psd\|test_stitch_snp_id_ordering\|test_stitch_sparse_payload\|test_whole_region_unchanged" tests/m3/ | sort -u | wc -l` returns 9.
3. `pytest tests/m3 -q` — full m3 suite reports 0 failed (no regression).
4. REQ-PATH-PARAMETERIZATION held: `grep -rn "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/build_ld_region_manifest.py src/python/select_ld_regions_dev.py src/scripts/stitch_subregions_to_rds.R` returns 0 matches.
5. Notebook valid JSON + carries the Q-RS2 cores=2 config (Task 3 acceptance).
</verification>

<success_criteria>
- build_ld_region_manifest.py splits xlarge regions into __sub{k:02d} rows with parent_region_id/subregion_index/n_subregions/subregion_start_grch38/subregion_end_grch38 provenance + split_status projection; non-xlarge regions stay whole.
- select_ld_regions_dev.py expands a selected xlarge parent into its __sub rows.
- stitch_subregions_to_rds.R assembles N sub-region .npz into one sparse block-diagonal parent .rds (zeroed cross-block, position-sorted dimnames, PSD per-block, audit provenance).
- A6 sparse-payload verdict committed (tests/m3/A6_sparse_payload_verdict.txt).
- AOU-2 notebook carries the Q-RS2 executor config (cores=2 / 24g / 10g / 24g) before pyspark import.
- All 9 named test families pass (Rscript-gated families skip cleanly with a verdict where R is unavailable).
- No regression on the existing tests/m3 suite.
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-02b-W2-rescope-split-stitch-code-SUMMARY.md` recording:
- The exact CLI added (--max-subregion-span-mb default, --split-classes default) + the new manifest columns
- N sub-regions a real m2_region_00040 (or the largest xlarge) splits into at 10 Mb
- The A6 verdict (sparse OK or densify-fallback) and what m3-04 must do about it
- The 9-family test pass/skip matrix
- Any sub-region that the bp heuristic puts at risk of >75k var (e.g. HLA/6p21 region_00145 — flag for the probe to set --max-subregion-span-mb 7 on chr6)
</output>
