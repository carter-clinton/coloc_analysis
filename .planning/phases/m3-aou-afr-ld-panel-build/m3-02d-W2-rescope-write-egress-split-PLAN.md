---
phase: m3-aou-afr-ld-panel-build
plan: 02d
type: execute
wave: 2
depends_on: ["02b", "02c"]
files_modified:
  - src/python/build_ld_region_manifest.py
  - src/python/select_ld_regions_dev.py
  - src/python/aou_ld_panel.py
  - config/ld_regions.tsv
  - config/ld_regions_dev.tsv
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv
  - .planning/notebooks/AOU-2_per_region_ld.ipynb
  - src/python/ld_egress_bundle.py
  - src/python/redo_ld_cost_model.py
  - tests/m3/test_build_ld_region_manifest.py
  - tests/m3/test_aou_ld_panel_local.py
  - tests/m3/test_ld_egress_bundle.py
  - tests/m3/test_redo_ld_cost_model.py
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md
autonomous: false
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-PATH-PARAMETERIZATION

must_haves:
  truths:
    - "PER-ANCESTRY BUFFER (Carter's locked scientific call 2026-06-22): build_ld_region_manifest emits AFR sub-region compute windows banded at buffer_bp = 3 Mb and EUR at buffer_bp = 5 Mb, with --max-subregion-span-mb 5 (CORE span) for BOTH. The current single global --subregion-buffer-mb cannot express this — the CODE is extended so the window geometry is ancestry-specific (an AFR sub-row and the matching EUR sub-row may carry DIFFERENT window_start/window_end). buffer_bp is grep-able per row and equals 3,000,000 for AFR rows / 5,000,000 for EUR rows at the locked flags; it is NOT silently 50 Mb."
    - "config/ld_regions.tsv + config/ld_regions_dev.tsv + the projection TSV are REGENERATED at the locked sizes via the existing split_existing_manifest Path-B regen (the --bed/--chain inputs are gone). After regen EVERY AFR compute cell is <= ~80k var and EVERY EUR compute cell is <= ~60k var (single-digit GiB banded output) — the buffer-floor fix from research Q3 (the prior 10 Mb buffer forced every cell >75k var). A regression test asserts the regenerated dev manifest's AFR/EUR window spans match the 3/5 Mb buffer geometry."
    - "ORDERING B is ENABLED in _write_a3_banded_correlation_bm (band-before-checkpoint per DRAFT-orderingB-band-before-checkpoint.md Change 1): the radius band (sparsify_row_intervals(blocks_only=False)) is applied to the LAZY correlation BEFORE the checkpoint, so the checkpoint materializes the radius-BANDED matrix (~GB at radius<<span) NOT the dense O(n_var^2) scratch (the measured ~0.15-tasks/min write bottleneck). blocks_only stays False (exact in-band r, numerics byte-identical to ld_matrix). An AST ordering-lock test (test_a3_band_before_checkpoint_ordering) asserts sparsify precedes checkpoint so a future edit cannot silently revert to ordering A."
    - "Every .npz producer preserves the lower_triangular flag contract (feedback_npz_triangle_flag_contract): _save_npz still writes lower_triangular=; the ordering-B change does NOT touch the flag's value or any reader's halving/doubling behavior; the existing flag-contract tests stay GREEN."
    - "The split/over_threshold criterion is RE-DERIVED around the REAL binding constraints (research Q2) — A.3 WRITE block-count + per-cell EGRESS output GiB — NOT the retired 75k-var MEMORY proxy. _preflight_estimates / write_preflight_counts expose est_block_count (banded in-band block count) + est_output_gib (0.5 * n_var^2 * band_frac * 4 bytes) and an over_threshold predicate keyed on BOTH a write-block ceiling AND a per-cell output-GiB ceiling (single-digit GiB target), not on n_var alone. A test asserts a cell that is small in n_var but large in band-block-count is flagged."
    - "PER-CHROMOSOME EGRESS BUNDLING (research Q5) is implemented in a reusable helper src/python/ld_egress_bundle.py: it groups compute-cell .npz outputs by chromosome, sums est/real bundle bytes, and SPLITS a chromosome bundle into chrN_a/chrN_b when it exceeds the 50 GB working ceiling (EGRESS_CAP_GB=50, a CONSERVATIVE project working ceiling per Q5/A2 — AoU's real mechanism is an alert threshold + manual relaxation, confirmed on first export, NOT a documented hard cap). REQ-AOU-LD-EGRESS: only summary LD + AF crosses; nothing individual-level."
    - "redo_ld_cost_model.py (the m3-02c Task 4 that was NEVER BUILT — this plan finalizes it) extrapolates the COMPLETING-cell blocks_per_min over the REAL re-split preflight n_var/block_count (not span guesses), applies the MEASURED EUR factor (from the mandatory completing EUR cell) or 3.01x +/-20% fallback, keeps THREE separate totals (322 logical parent panels / expanded ancestry compute cells > 322 / aggregate parent = Sigma over sub-region rows), computes MASTER-INCLUSIVE end-to-end cluster-hours, applies a contingency factor from probe variance, projects per-chromosome egress bundles vs the 50 GB ceiling, and evaluates the EXACT gate predicate PROJECTED * 1.3 <= BUDGET_CAP_CLUSTER_H with dispositions GREEN / YELLOW-narrow-radius / YELLOW-finer-split / RED."
    - "THE RE-PROBE (autonomous:false, Carter fires in-perimeter): re-run STEP A preflight on the RE-SPLIT manifest confirming cells are now under target (the prior preflight showed every cell >75k var at the 10 Mb buffer), then fire COMPLETING properly-sized cells — AFR core5/buf3 (~80k var) + the MANDATORY EUR core5/buf5 (~60k var) + an HLA region_00145 sub-region preflight — on the EXISTING 64 GB n2-standard-16 x24 HAIL cluster (20260604) at executor cores=1 (NO n2-highmem; NO quota ticket — research Q6 + N2_CPUS=5000 pre-satisfied), comparing ordering A vs B on wall-clock. Each cell is data-layer-verified (gsutil du + Hail count, _SUCCESS is NOT evidence per D-M3-10) and the cluster is shut down with a verified shutdown artifact. The prior m3-W2-cost-probe.tsv is INTERRUPTED/partial (blocks_per_min=NA) and is REPLACED by completing-cell rates."
    - "The go/no-go ends at a defensible GREEN/RED disposition for the 322-cell production fire, which stays EXPLICITLY OUT of scope here (Wave 4 / m3-04). m3-W2-budget-redo.md records the three totals + the contingency + the per-chrom egress projection + BUDGET_CAP + the 1.3x headroom evaluation + the disposition."
  artifacts:
    - path: "src/python/build_ld_region_manifest.py"
      provides: "Per-ancestry buffer (AFR 3 Mb / EUR 5 Mb) overlapping-window split; ancestry-specific window geometry; re-derived write+egress over_threshold inputs"
      contains: "ancestry"
    - path: "config/ld_regions.tsv"
      provides: "Regenerated at core5/buf3(AFR)/buf5(EUR): AFR cells <=80k var, EUR <=60k var, single-digit-GiB banded output"
      contains: "buffer_bp"
    - path: "config/ld_regions_dev.tsv"
      provides: "Regenerated dev subset at the locked sizes (capped expansion); the re-probe cells"
      contains: "__sub"
    - path: "src/python/aou_ld_panel.py"
      provides: "Ordering-B A.3 write (band-before-checkpoint) + lower_triangular flag preserved + write/egress over_threshold estimators"
      contains: "sparsify_row_intervals"
    - path: "src/python/ld_egress_bundle.py"
      provides: "Per-chromosome egress bundling helper; splits a bundle into chrN_a/chrN_b above EGRESS_CAP_GB=50"
      min_lines: 60
    - path: "src/python/redo_ld_cost_model.py"
      provides: "Real-count extrapolation; 3 separate totals; master-inclusive end-to-end cluster-hours; contingency; per-chrom egress projection; PROJECTED * 1.3 <= BUDGET_CAP gate"
      min_lines: 90
    - path: "tests/m3/test_build_ld_region_manifest.py"
      provides: "test_per_ancestry_buffer_geometry + test_regen_cells_under_target + test_write_egress_over_threshold"
      min_lines: 60
    - path: "tests/m3/test_aou_ld_panel_local.py"
      provides: "test_a3_band_before_checkpoint_ordering (AST ordering lock) + the lower_triangular flag-contract tests stay green"
    - path: "tests/m3/test_ld_egress_bundle.py"
      provides: "Per-chrom bundle grouping + the >50 GB within-chrom split"
    - path: "tests/m3/test_redo_ld_cost_model.py"
      provides: "3-totals separation + real-count extrapolation + master-inclusive accounting + measured-EUR-factor + contingency + egress projection + the 1.3x gate predicate (GREEN and RED sides)"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv"
      provides: "REPLACED with >=2 COMPLETING-cell rows (AFR core5/buf3 + the mandatory EUR core5/buf5) carrying a real blocks_per_min (the prior was INTERRUPTED/NA)"
      contains: "blocks_per_min"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md"
      provides: "The 3 totals + contingency + per-chrom egress projection + BUDGET_CAP + PROJECTED * 1.3 <= BUDGET_CAP disposition (GREEN/YELLOW/RED)"
      contains: "PROJECTED"
  key_links:
    - from: "src/python/build_ld_region_manifest.py"
      to: "config/ld_regions.tsv per-ancestry compute rows"
      via: "ancestry-specific buffer_bp (3 Mb AFR / 5 Mb EUR) driving window_start/window_end"
      pattern: "buffer_bp"
    - from: "src/python/aou_ld_panel.py::_write_a3_banded_correlation_bm"
      to: "the banded GCS scratch checkpoint"
      via: "sparsify_row_intervals applied BEFORE checkpoint (ordering B)"
      pattern: "sparsify_row_intervals"
    - from: "src/python/redo_ld_cost_model.py"
      to: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv"
      via: "reads the COMPLETING-cell blocks_per_min + measured EUR factor"
      pattern: "blocks_per_min"
    - from: "src/python/redo_ld_cost_model.py"
      to: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md"
      via: "writes PROJECTED (3 totals) + per-chrom egress + the PROJECTED * 1.3 <= BUDGET_CAP disposition"
      pattern: "BUDGET_CAP"
---

<objective>
Re-scope Wave 2 of M3 around the binding constraint the 2026-06-22 cost probe MEASURED: the A.3 BlockMatrix WRITE stage + the per-cell EGRESS bundle size — NOT memory/spill. The probe proved (on the existing 64 GB n2-standard-16 x24 HAIL cluster at executor cores=1) that a real EUR cell (78,730 var) ran the entire correlation matmul AND started the write with ZERO spill and a stable master, but the write was crawling at ~0.15 tasks/min (~40+ projected hours) because ordering A checkpoints the full dense O(n_var^2) correlation to GCS scratch before banding. The cell was interrupted write-bound, so the cost model has NO completing blocks_per_min.

The structural fix (research V2, Carter's locked scientific call): shrink the banding buffer to a PER-ANCESTRY width (AFR 3 Mb / EUR 5 Mb) over a 5 Mb core, which (a) lands every AFR cell at ~80k var / ~3.5 GiB and every EUR cell at ~60k var / ~2.4 GiB — fixing the write, the egress, AND the buffer-floor (the prior 10 Mb buffer alone forced every cell >75k var); and (b) makes the radius << span for the FIRST time, which makes ORDERING B (band-before-checkpoint) non-vacuous — its banded scratch is ~7x smaller than ordering A's dense scratch, directly attacking the measured write bottleneck.

This plan delivers FIVE NCSU code+test artifacts (autonomous TDD, no cluster): (1) per-ancestry buffer in build_ld_region_manifest + regenerate the manifests; (2) ordering-B A.3 write + the npz flag contract + the AST ordering lock; (3) the re-derived write+egress over_threshold criterion; (4) the per-chromosome egress bundling helper; (5) redo_ld_cost_model.py (the m3-02c Task 4 that was never built). It then delivers ONE in-perimeter RE-PROBE (autonomous:false, Carter fires) that produces COMPLETING properly-sized AFR + EUR cells (ordering A vs B), refreshes the INTERRUPTED cost-probe TSV, and runs the cost model + go/no-go on the real completing rates.

Purpose: turn the INTERRUPTED probe into a defensible GREEN/RED go/no-go for the 322-cell production fire. The full 322-cell fire stays OUT of scope (Wave 4 / m3-04).

Output: the per-ancestry-buffer manifest builder + regenerated manifests, the ordering-B A.3 write, the write+egress split criterion, the per-chrom egress helper, redo_ld_cost_model.py + tests, the refreshed completing-cell cost-probe TSV, the verified shutdown artifact, and the budget-redo memo with the disposition.

LOCKED (do NOT relitigate):
- BAND WIDTH = AFR 3 Mb / EUR 5 Mb, core span 5 Mb both (Carter's scientific call 2026-06-22). Per-ancestry buffer is a REQUIRED code change (the current --subregion-buffer-mb is a single global knob).
- BINDING CONSTRAINTS = A.3 write throughput + egress bundle size (NOT memory). The 75k-var over_threshold was a memory proxy; re-derive around write-block-count + per-cell output GiB.
- A.3 WRITE = ordering B (band-before-checkpoint per the DRAFT). Preserve the npz lower_triangular flag contract.
- CLUSTER = existing 64 GB HAIL clusters (20260604/05), cores=1. NO n2-highmem (uncreatable via the Verily UI). NO quota ticket (N2_CPUS=5000 pre-satisfied).
- EGRESS = per-chromosome bundling; the AoU cap is an alert threshold + manual relaxation (Q5/A2), with 50 GB as the conservative project working ceiling; confirm the real number on first export.
- The split itself (m3-02b: split_region_overlapping, overlapping-window BANDED stitch, AF metadata, the real-loader contract) is correct and NOT relitigated; this plan changes the buffer width + the write ordering + builds the cost model.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE-V2.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md
@.planning/phases/m3-aou-afr-ld-panel-build/DRAFT-orderingB-band-before-checkpoint.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv
@.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv
@.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md
@.claude/skills/aou-ld-pipeline/SKILL.md

<interfaces>
<!-- Concrete contracts extracted from the source the executor will modify (m3-02b LANDED these). -->

src/python/build_ld_region_manifest.py (EXISTING — m3-02b landed the split machinery; this plan ADDS per-ancestry buffer):
- parse_args(): ALREADY has --max-subregion-span-mb (float, default DEFAULT_MAX_SUBREGION_SPAN_MB),
  --split-classes (default 'xlarge'), --subregion-buffer-mb (float, default None = global single knob),
  --split-existing-manifest (Path B regen; --bed/--chain are GONE so regen uses THIS), --ancestries.
- split_region_overlapping(start_b38, end_b38, core_span_bp, buffer_bp) -> list[dict] with
  core_start, core_end (half-open tiling), window_start, window_end (= core +/- buffer_bp clamped),
  subregion_index k, n_subregions N.  *** This takes a SINGLE buffer_bp — the per-ancestry change
  must call it per-ancestry (AFR buffer vs EUR buffer) so window geometry differs by ancestry. ***
- _assemble_region_rows(*, ..., ancestries, trait_lead_fn, split_set, core_span_bp,
  buffer_override_bp) -> (manifest_rows, projection_rows).  *** CURRENT BUG FOR PER-ANCESTRY: the
  SPLIT branch computes ONE buffer_bp + ONE set of subs, then loops `for ancestry in ancestries`
  emitting the SAME window_start/window_end/buffer_bp for EVERY ancestry (lines ~545-568). To make
  the buffer per-ancestry, the window geometry (split_region_overlapping call + the projection sub
  row) must be computed PER ANCESTRY, so an AFR __sub row and the matching EUR __sub row carry
  DIFFERENT window_start/window_end/buffer_bp. ***
- WR-01 SUBREGION_BUFFER_GUARD (lines ~484-500): raises ValueError if buffer_override_bp is None AND
  the widest window >= SUBREGION_WINDOW_PARENT_SPAN_GUARD_FRAC * span. An EXPLICIT buffer is always
  honored. The locked 3/5 Mb buffers are explicit so the guard does not fire.
- build_manifest(bed_df, chain, ancestries, max_subregion_span_mb, split_classes, subregion_buffer_mb)
  and split_existing_manifest(in_manifest_df, *, subregion_buffer_mb, max_subregion_span_mb,
  split_classes) BOTH route through _assemble_region_rows. The per-ancestry change is threaded through
  BOTH (the regen uses split_existing_manifest since --bed/--chain are gone).
- MANIFEST_COLUMNS already include parent_region_id, subregion_index, n_subregions,
  core_start_grch38, core_end_grch38, window_start_grch38, window_end_grch38, buffer_bp, radius_bp.
- compute_radius_bp(s,e)=min(span+500k, 50M); derive_region_class small<=5/medium<=25/large<=50/xlarge>50.

src/python/aou_ld_panel.py (EXISTING):
- _route_region_path(region_class, span_mb): PATH_A1_MAX_MB=5, PATH_A2_MAX_MB=10; any A.1/A.2 with
  span_mb > 10 demotes to A.3. (The ~11/15 Mb windows route A.3.)
- _preflight_estimates(n_var, span_mb, region_class, ...) (line ~385) + write_preflight_counts(
  region_rows, mt_by_ancestry, out_path) (line ~434): the preflight count pass; this plan RE-DERIVES
  the over_threshold predicate here around write-block-count + output-GiB (not n_var alone).
- _dense_footprint_bytes(n_var) = n_var^2 * 4 (line ~2583); A3_DENSE_SCRATCH_WARN_BYTES = 300 GiB.
- _a3_scratch_uri(bm_uri) -> the .corr_scratch.bm sibling URI.
- _write_a3_banded_correlation_bm(mt_r, radius_bp, bm_uri, *, stage_locally=True, n_var=None)
  (line ~2630): *** CURRENTLY ORDERING A *** — lines 2701-2716:
    corr_bm = hl.row_correlation(...)            # 1 lazy
    corr_bm = corr_bm.checkpoint(scratch_uri)    # 2 MATERIALIZE DENSE  <- the bottleneck
    starts, stops = hl.linalg.utils.locus_windows(mt_r.locus, radius=radius_bp)   # 3
    banded = corr_bm.sparsify_row_intervals(starts, stops, blocks_only=False)     # 4 band
    banded.write(bm_uri, ...)                     # 5
  ORDERING B (DRAFT Change 1) reorders to band(3,4)-then-checkpoint(2): sparsify the LAZY corr FIRST,
  then checkpoint the BANDED matrix, then write. blocks_only stays False. Numerics byte-identical.
- _save_npz(region_id, ld_np, variant_ids, rsids, out_bucket, out_local_dir, lower_triangular=False,
  allele_freq=None) (line ~2724): ALREADY writes lower_triangular= AND allele_freq= (m3-02b landed).
  The ordering-B change must NOT touch the flag value or readers (feedback_npz_triangle_flag_contract).

DRAFT-orderingB-band-before-checkpoint.md:
- Change 1 = the full ordering-B helper body (ready-to-paste; keep signature, _a3_scratch_uri,
  n_var observability, cleanup; only the op order + docstring change).
- Change 2 = test_a3_band_before_checkpoint_ordering (AST: first sparsify_row_intervals line <
  first checkpoint line). Pure-Python, runs on NCSU.
- Change 3 = doc/comment touchpoints (call-site comment ~2217, _a3_scratch_uri docstring,
  _dense_footprint_bytes docstring, WAVE-2-GATE-READINESS.md, the debug session) to flip
  "ordering A / CR-01 open" -> "ordering B / CR-01 resolved".
- Existing A.3 tests check op PRESENCE not order -> they stay GREEN; the NEW ordering-lock test
  enforces the order.

select_ld_regions_dev.py (EXISTING — m3-02b landed tuple-resolve + cap):
- AFR_KNOWN_REGIONS, EUR_OVERLAP_REGIONS, DEV_SUBREGION_CAP=2, _resolve_request_tuple,
  select_dev_rows. Re-run after the per-ancestry regen so the dev manifest carries the new geometry.

m3-W2-cost-probe.tsv (EXISTING, INTERRUPTED): 1 row, status=INTERRUPTED_write_bound, blocks_per_min=NA
  (EUR m2_region_00040__sub00, 78,730 var, write-bound at 56 min). This plan REPLACES it with
  completing-cell rows.
m3-W2-preflight-counts.tsv (EXISTING): 15 rows at the OLD 10 Mb buffer, EVERY cell over_threshold=True
  (buffer-floor). Re-generated at the new buffers by STEP A of the re-probe.

Live coordinates (SKILL.md):
- Workspace aou-rw-476cdac2 . project wb-perky-corn-6639 . bucket gs://rw-migration-aou-rw-476cdac2
- Run branch m3-W2-aou-deltas (NOT main). Cohorts: AFR_pca 73,122 ; EUR_pca 220,098.
- Cluster: 64 GB n2-standard-16 x24 HAIL (20260604/05), cores=1 / 11g / 3g, STOPPED/restartable.
  NO n2-highmem (uncreatable via UI). NO quota ticket (N2_CPUS=5000 pre-satisfied).
- Measured AFR density ~7,300 var/Mb; EUR ~4,000 var/Mb (use the real preflight counts).
- GATE-1 BUDGET_CAP_CLUSTER_H = Carter's approved credit cap (re-confirm the number at the gate).
- D-M3-10: every .npz/.bm write contents-validated (gsutil du + Hail count), _SUCCESS is NOT evidence.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Per-ancestry banding buffer (AFR 3 Mb / EUR 5 Mb, core 5 Mb) in build_ld_region_manifest.py + regenerate config/ld_regions.tsv, config/ld_regions_dev.tsv, the projection TSV at the locked sizes + per-ancestry geometry tests</name>
  <files>src/python/build_ld_region_manifest.py, src/python/select_ld_regions_dev.py, config/ld_regions.tsv, config/ld_regions_dev.tsv, .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv, tests/m3/test_build_ld_region_manifest.py</files>
  <read_first>
    - src/python/build_ld_region_manifest.py (FULL — parse_args lines 101-148, split_region_overlapping 320-380, _assemble_region_rows 438-613 [THE per-ancestry change point: SPLIT branch loops ancestries with ONE window], build_manifest 616-724, split_existing_manifest 727-811, main 843-871, MANIFEST_COLUMNS, WR-01 guard)
    - src/python/select_ld_regions_dev.py (FULL — AFR_KNOWN_REGIONS, EUR_OVERLAP_REGIONS, DEV_SUBREGION_CAP, _resolve_request_tuple, select_dev_rows)
    - config/ld_regions.tsv (the committed post-m3-02b manifest at the OLD buffer — the Path-B regen input) + config/ld_regions_dev.tsv
    - tests/m3/test_build_ld_region_manifest.py (FULL — existing split/geometry test patterns + fixtures)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE-V2.md "Q1" + "Q3" + the Decision Table (the 3/5 Mb buffer is Carter's locked call; core 5 Mb)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv (the OLD-buffer cell sizes the regen must shrink)
  </read_first>
  <behavior>
    - test_per_ancestry_buffer_geometry: split a synthetic 30 Mb xlarge region with core_span 5 Mb, AFR buffer 3 Mb, EUR buffer 5 Mb. Assert the AFR __sub00 compute row's window = [core_start - 3Mb, core_end + 3Mb] (clamped) and buffer_bp == 3_000_000; the EUR __sub00 window = [core_start - 5Mb, core_end + 5Mb] and buffer_bp == 5_000_000. The AFR and EUR window_start/window_end for the SAME subregion_index DIFFER (the AFR window is narrower). The half-open CORES are identical across ancestries (the core tiling does not depend on the buffer); only the windows differ.
    - test_per_ancestry_buffer_default_falls_back: with NO per-ancestry override (the legacy single --subregion-buffer-mb path), AFR and EUR get the SAME buffer_bp == the global value — back-compat with m3-02b is preserved (the per-ancestry feature is opt-in via the new flags).
    - test_locked_flags_produce_3_5_buffers: invoking the builder with the locked flags (--max-subregion-span-mb 5, AFR buffer 3, EUR buffer 5) yields buffer_bp == 3_000_000 on every AFR compute row and 5_000_000 on every EUR compute row; NO row carries buffer_bp == 50_000_000.
    - test_regen_cells_under_target: after the Path-B regen at the locked sizes, the est n_var per compute cell (n_var ~= window_span_mb * density, AFR 7,300 / EUR 4,000 var/Mb) is <= ~80k (AFR) / ~60k (EUR) for the represented regions — the buffer-floor fix. Use the projection span + the research density anchors; assert the AFR core5/buf3 window span ~= 11 Mb and the EUR core5/buf5 window span ~= 15 Mb (geometry-level, no MT).
    - test_dev_regen_carries_new_geometry: config/ld_regions_dev.tsv after regen has AFR __sub rows with buffer_bp 3_000_000 and EUR __sub rows with buffer_bp 5_000_000; the capped expansion (DEV_SUBREGION_CAP) still holds; AFR/EUR are not mixed for a single ancestry pick.
    - test_whole_region_unaffected: a non-xlarge region still emits ONE whole row per ancestry with the whole-region convention (no __sub), unchanged by the per-ancestry buffer feature.
  </behavior>
  <action>
    In `src/python/build_ld_region_manifest.py`:

    1. Add per-ancestry buffer CLI. KEEP the existing global `--subregion-buffer-mb` for back-compat (a single value applied to all ancestries). ADD `--subregion-buffer-mb-by-ancestry` (a comma-separated `ANC:MB` mapping, e.g. `AFR:3,EUR:5`; type=str, default=None). When the per-ancestry flag is given it OVERRIDES the global for the named ancestries; unnamed ancestries fall back to the global (or the radius default if neither given). Parse it in parse_args into a dict `{ancestry: buffer_mb_float}`; document that the LOCKED M3 value is `AFR:3,EUR:5` with `--max-subregion-span-mb 5`. DO NOT hardcode 3/5 in the library code — they are CLI values (pass-through), so the geometry is a parameter, not a constant.

    2. Thread a `buffer_override_bp_by_ancestry: dict[str,int] | None` through build_manifest -> _assemble_region_rows AND split_existing_manifest -> _assemble_region_rows (alongside the existing scalar buffer_override_bp; the scalar stays the global fallback).

    3. In `_assemble_region_rows` SPLIT branch: resolve the per-ancestry buffer at the TOP — for each ancestry compute `buf_anc = by_ancestry.get(ancestry) if by_ancestry else (buffer_override_bp if not None else radius_bp)`. RESTRUCTURE the split emission so the window geometry is computed PER ANCESTRY: move the `split_region_overlapping(start_b38, end_b38, core_span_bp, buf_anc)` call INSIDE a per-ancestry loop (the half-open CORES are buffer-independent so they stay identical across ancestries — assert that in a test — but the WINDOWS = core +/- buf_anc differ). Emit one projection sub row PER (subregion_index) using a representative/widest ancestry window OR (cleaner) emit a projection sub row per (subregion_index, ancestry) with that ancestry's window + buffer_bp; choose the per-(sub,ancestry) projection so the projection faithfully carries the per-ancestry geometry the cost model consumes. Each manifest compute row carries window_start/window_end/buffer_bp = THAT ancestry's geometry. PRESERVE the WR-01 guard (it fires only on the radius-default; the explicit 3/5 Mb buffers bypass it).

    4. In `main()`: thread `args.subregion_buffer_mb_by_ancestry` (parsed dict) into BOTH build_manifest and split_existing_manifest.

    In `src/python/select_ld_regions_dev.py`:

    5. No logic change required (the tuple-resolve reads whatever manifest it is given); just confirm select_dev_rows works on the regenerated per-ancestry manifest (the geometry tests cover it). If select_dev_rows assumed AFR/EUR share window coords for a parent, FIX that assumption (the windows now differ by ancestry) — _resolve_request_tuple already filters by (region_id|parent_region_id, ancestry) so it should be agnostic; add a guard test.

    REGENERATE the manifests (NCSU, free; Path B since --bed/--chain are gone):

    6. Run the builder via `--split-existing-manifest config/ld_regions.tsv --max-subregion-span-mb 5 --subregion-buffer-mb-by-ancestry AFR:3,EUR:5 --out-manifest config/ld_regions.tsv --out-projection .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv` (write to a temp then move, OR overwrite — the input is the committed manifest; commit the regenerated version). Then regenerate config/ld_regions_dev.tsv via select_ld_regions_dev.py against the new manifest. Record the regen command in the SUMMARY.

    In `tests/m3/test_build_ld_region_manifest.py`:

    7. Add the per-ancestry geometry behavior tests above. For the pure-geometry assertions call split_region_overlapping directly with buffer 3Mb and 5Mb and assert the windows differ; for the manifest-level assertions build a tiny synthetic in-manifest DataFrame (an xlarge region) and call split_existing_manifest with the per-ancestry dict, asserting AFR rows carry buffer_bp 3_000_000 and EUR 5_000_000 with differing windows + identical cores. Keep assertions on exact integers + grep-able column names.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_build_ld_region_manifest.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "subregion-buffer-mb-by-ancestry\|subregion_buffer_mb_by_ancestry\|by_ancestry" src/python/build_ld_region_manifest.py` returns >= 3.
    - `grep -c "AFR:3,EUR:5\|AFR:3\|per-ancestry\|per ancestry" src/python/build_ld_region_manifest.py` returns >= 1 (the locked value is documented as the CLI default-of-record, not a code constant).
    - `grep -cE "DEFAULT_BUFFER_AFR_MB *= *3|DEFAULT_BUFFER_EUR_MB *= *5|buffer_bp *= *3_000_000|buffer_bp *= *5_000_000" src/python/build_ld_region_manifest.py` returns 0 (the 3/5 are CLI values threaded through, NOT hardcoded library constants).
    - `pytest tests/m3/test_build_ld_region_manifest.py -v` reports 0 failed; test_per_ancestry_buffer_geometry, test_per_ancestry_buffer_default_falls_back, test_locked_flags_produce_3_5_buffers, test_regen_cells_under_target, test_dev_regen_carries_new_geometry, test_whole_region_unaffected all PASS.
    - `awk -F'\t' 'NR==1{for(i=1;i<=NF;i++)if($i=="ancestry")a=i;else if($i=="buffer_bp")b=i;next}$a=="AFR"&&$b!=3000000{print;n++}END{exit n>0}' config/ld_regions.tsv` exits 0 (every AFR compute row has buffer_bp 3_000_000 after regen; tolerate whole-region rows which carry radius — restrict to __sub rows in the actual check).
    - `grep -c "buffer_bp" config/ld_regions.tsv` returns >= 1 AND `awk -F'\t' 'NR==1{for(i=1;i<=NF;i++){if($i=="ancestry")a=i;if($i=="buffer_bp")b=i}next}$a=="EUR"&&$b==5000000{n++}END{exit !(n>0)}' config/ld_regions.tsv` exits 0 (EUR __sub rows carry buffer_bp 5_000_000, checked by header-resolved field not column position).
    - `pytest tests/m3 -q` reports 0 failed (no regression; update any test pinning the old single-buffer geometry).
  </acceptance_criteria>
  <done>
    build_ld_region_manifest emits ancestry-specific overlapping-window geometry (AFR buffer 3 Mb / EUR buffer 5 Mb over a 5 Mb core) via a per-ancestry CLI threaded through both build_manifest and split_existing_manifest (the 3/5 values are CLI parameters, NOT hardcoded constants); the cores stay identical across ancestries while the windows differ; config/ld_regions.tsv + ld_regions_dev.tsv + the projection are regenerated at the locked sizes; all named geometry tests pass; no regression.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Enable ordering B (band-before-checkpoint) in _write_a3_banded_correlation_bm + AST ordering-lock test + preserve the npz lower_triangular flag contract + re-derive the write+egress over_threshold criterion in the preflight estimators + the per-chromosome egress bundling helper</name>
  <files>src/python/aou_ld_panel.py, src/python/ld_egress_bundle.py, tests/m3/test_aou_ld_panel_local.py, tests/m3/test_ld_egress_bundle.py</files>
  <read_first>
    - src/python/aou_ld_panel.py lines 2630-2722 (_write_a3_banded_correlation_bm — CURRENT ORDERING A: checkpoint(2701-2707) BEFORE sparsify(2708-2713)) + lines 2583-2628 (_dense_footprint_bytes, A3_DENSE_SCRATCH_WARN_BYTES, _a3_scratch_uri) + lines 2724-2790 (_save_npz: lower_triangular= + allele_freq= already present)
    - src/python/aou_ld_panel.py lines 320-460 (_route_region_path, _preflight_estimates, write_preflight_counts — the over_threshold predicate to re-derive)
    - .planning/phases/m3-aou-afr-ld-panel-build/DRAFT-orderingB-band-before-checkpoint.md (FULL — Change 1 ready-to-paste helper body, Change 2 the AST ordering-lock test, Change 3 doc touchpoints; the retirement banner's revisit condition radius<<span is NOW MET)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE-V2.md "Q2" (the write-block + egress over_threshold re-derivation + the banded output formula 0.5*n^2*band_frac*4) + "Q4" (ordering B non-vacuous; keep blocks_only=False) + "Q5" (per-chrom bundling, 50 GB working ceiling, alert-threshold model)
    - tests/m3/test_aou_ld_panel_local.py (FULL — the existing A.3 op-presence tests + the lower_triangular flag-contract tests that must stay GREEN; the comment block ~2546 to reorder per Change 3)
    - .claude/skills/aou-ld-pipeline/SKILL.md "A.3-write history / CR-01" + "feedback_npz_triangle_flag_contract" + "feedback_aou_success_marker_not_evidence_of_data"
    - .planning/amendments/aou-egress-audit-log.md (the existing per-bundle 50 GB schema + the "split chr1 into 1a+1b" affordance the helper must mirror)
  </read_first>
  <behavior>
    - test_a3_band_before_checkpoint_ordering (DRAFT Change 2, AST, NO Hail): parse _write_a3_banded_correlation_bm; the FIRST sparsify_row_intervals call line < the FIRST checkpoint call line (band BEFORE checkpoint = ordering B). A regression to band-after-checkpoint (ordering A) FAILS this. Pure-Python, runs on NCSU.
    - test_a3_keeps_blocks_only_false: the sparsify_row_intervals call passes blocks_only=False (exact in-band r; numerics byte-identical to ld_matrix — Q4).
    - test_a3_existing_op_presence_tests_green: the existing test_a3_branch_uses_materialize_then_band_not_fused_write, test_a3_helper_does_not_call_fused_ld_matrix_write, test_a3_scratch_uri_is_path_isolated_and_idempotent, test_dense_footprint_bytes_matches_n2_times_4, test_dense_footprint_helper_used_by_a3_write_for_observability still PASS (they check op PRESENCE / the scratch URI / the dense upper-bound math, all preserved under ordering B).
    - test_lower_triangular_flag_contract_preserved: _save_npz still writes lower_triangular= and the value is unchanged by the ordering-B edit; the existing flag-contract test (the CR-01 doubling / BR-01 halving regression guard) stays GREEN — ordering B touches the BlockMatrix write path, NOT the .npz triangle flag.
    - test_over_threshold_keys_on_write_and_egress_not_nvar: _preflight_estimates / the over_threshold predicate flags a cell on EITHER (est_block_count > WRITE_BLOCK_THRESHOLD) OR (est_output_gib > OUTPUT_GIB_THRESHOLD), NOT on n_var alone. Construct a cell with n_var below 75k but a band-block-count above the write ceiling and assert over_threshold is True (the memory-proxy 75k rule would have missed it).
    - test_egress_bundle_groups_by_chrom: ld_egress_bundle groups compute-cell outputs by chromosome and sums bytes per chromosome.
    - test_egress_bundle_splits_over_cap: a chromosome whose summed bundle exceeds EGRESS_CAP_GB=50 is split into chrN_a / chrN_b sub-bundles each <= the cap; a chromosome under the cap stays a single bundle; the cap is a documented CONSERVATIVE working ceiling (Q5/A2), not a hard API limit.
  </behavior>
  <action>
    In `src/python/aou_ld_panel.py`:

    1. Apply DRAFT Change 1 to `_write_a3_banded_correlation_bm`: reorder so the radius band is applied to the LAZY correlation BEFORE the checkpoint. KEEP the signature, _a3_scratch_uri, the n_var observability log (relabel the dense footprint as the UN-BANDED UPPER BOUND under ordering B per the DRAFT), and the cleanup. The body becomes: row_correlation (lazy) -> locus_windows -> sparsify_row_intervals(blocks_only=False) (band the lazy corr) -> checkpoint(scratch_uri) (materialize the BANDED matrix) -> write(bm_uri). Update the docstring to band-then-checkpoint (ordering B / CR-01 resolution) per the DRAFT. blocks_only stays False.

    2. Apply DRAFT Change 3 doc touchpoints: the call-site comment (~line 2217 region), the _a3_scratch_uri docstring, the _dense_footprint_bytes docstring (note it is the un-banded upper bound under ordering B), and the test comment block (~2546) to reorder to match B. Keep the WR-02 scratch log; relabel the materialized scratch as the banded subset.

    3. Re-derive the over_threshold criterion in `_preflight_estimates` / `write_preflight_counts`: add module constants `WRITE_BLOCK_THRESHOLD` (a banded-block-count ceiling tied to the measured write rate; pick a defensible value, e.g. the block count at which the projected ordering-B write exceeds the per-cell wall budget, ~300 blocks — document the derivation referencing the probe's ~0.15 dense tasks/min and the ~7x ordering-B reduction) and `OUTPUT_GIB_THRESHOLD` (single-digit-GiB ceiling, e.g. 10 GiB — the egress-tractable target). est_block_count = banded in-band block count = (ceil(n_var/4096))^2 / 2 * band_frac where band_frac = min(2*buffer_bp / window_span_bp, 1); est_output_gib = 0.5 * n_var^2 * band_frac * 4 / 1e9. over_threshold = (est_block_count > WRITE_BLOCK_THRESHOLD) OR (est_output_gib > OUTPUT_GIB_THRESHOLD). DOCUMENT that this REPLACES the retired 75k-var MEMORY proxy (the probe proved no spill — memory is not the constraint; the write + egress are).

    Create `src/python/ld_egress_bundle.py` (NEW reusable helper — feedback_extract_reusable_utilities):

    4. `EGRESS_CAP_GB = 50` (a CONSERVATIVE PROJECT WORKING CEILING per Q5/A2 — AoU's real mechanism is an alert threshold + manual relaxation, confirmed on first export, NOT a documented hard 50 GB API cap; docstring says so). `plan_egress_bundles(cell_sizes: list[dict]) -> list[dict]`: each input {region_id, chr, bytes}; group by chr; sum per chr; for any chr whose sum > EGRESS_CAP_GB*1e9 split into chrN_a/chrN_b (greedy bin-pack the cells so each sub-bundle <= the cap; mirror the aou-egress-audit-log "split chr1 into 1a+1b" affordance). Return per-bundle {bundle_id, chr, region_ids, total_bytes, n_cells}. REQ-PATH-PARAMETERIZATION: no hardcoded /share|/rs1|/gpfs_common paths. REQ-AOU-LD-EGRESS: only summary LD+AF is bundled; the helper carries a comment that nothing individual-level crosses.

    Tests:

    5. Add `test_a3_band_before_checkpoint_ordering` + `test_a3_keeps_blocks_only_false` + `test_over_threshold_keys_on_write_and_egress_not_nvar` to `tests/m3/test_aou_ld_panel_local.py` (AST + pure-Python where possible). Create `tests/m3/test_ld_egress_bundle.py` with the grouping + over-cap-split tests. Confirm the existing A.3 op-presence + lower_triangular flag-contract tests stay green (do NOT delete or weaken them).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_aou_ld_panel_local.py tests/m3/test_ld_egress_bundle.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `grep -n "sparsify_row_intervals\|checkpoint" src/python/aou_ld_panel.py` shows the FIRST sparsify_row_intervals line < the FIRST checkpoint line WITHIN _write_a3_banded_correlation_bm (ordering B). The AST test enforces this.
    - `grep -c "blocks_only=False" src/python/aou_ld_panel.py` returns >= 1 (exact in-band r preserved).
    - `grep -c "ordering B\|band-before-checkpoint\|band-then-checkpoint\|CR-01 resolution\|CR-01 resolved" src/python/aou_ld_panel.py` returns >= 1 (doc flip applied).
    - `grep -c "lower_triangular" src/python/aou_ld_panel.py` returns >= 2 (the flag contract is intact in _save_npz, untouched by the reorder).
    - `grep -c "WRITE_BLOCK_THRESHOLD\|OUTPUT_GIB_THRESHOLD\|band_frac\|est_output_gib" src/python/aou_ld_panel.py` returns >= 3 (the write+egress over_threshold re-derivation).
    - `test -f src/python/ld_egress_bundle.py` exits 0; `grep -c "EGRESS_CAP_GB\|def plan_egress_bundles\|working ceiling\|alert threshold" src/python/ld_egress_bundle.py` returns >= 3.
    - `grep -rn "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/ld_egress_bundle.py` returns 0 (REQ-PATH-PARAMETERIZATION).
    - `pytest tests/m3/test_aou_ld_panel_local.py -v` reports test_a3_band_before_checkpoint_ordering, test_a3_keeps_blocks_only_false, test_over_threshold_keys_on_write_and_egress_not_nvar PASS AND the existing test_a3_* + the lower_triangular flag-contract tests still PASS (0 failed).
    - `pytest tests/m3/test_ld_egress_bundle.py -v` reports test_egress_bundle_groups_by_chrom + test_egress_bundle_splits_over_cap PASS.
    - `pytest tests/m3 -q` reports 0 failed (no regression).
  </acceptance_criteria>
  <done>
    _write_a3_banded_correlation_bm applies the radius band BEFORE the checkpoint (ordering B; banded scratch ~7x smaller, attacking the measured write bottleneck) with an AST ordering-lock test guarding against silent reversion; blocks_only stays False (numerics identical); the lower_triangular flag contract is preserved; the over_threshold criterion is re-derived around write-block-count + per-cell output GiB (not the retired 75k-var memory proxy); a reusable per-chromosome egress-bundling helper splits a >50 GB bundle into chrN_a/chrN_b; all named + existing tests pass.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Build redo_ld_cost_model.py (the m3-02c Task 4 that was never written) — real-count extrapolation, 3 separate totals, master-inclusive end-to-end cluster-hours, contingency, per-chrom egress projection, the PROJECTED * 1.3 <= BUDGET_CAP go/no-go gate + unit tests</name>
  <files>src/python/redo_ld_cost_model.py, tests/m3/test_redo_ld_cost_model.py</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-02c-W2-rescope-quota-probe-and-gonogo-PLAN.md Task 4 (lines 313-372 — the FULL spec for this script: load_probe_rates, load_preflight_counts, eur_factor, n_workers_plus_master, project_cell_hours, three_totals, apply_contingency, project_egress_bundles, evaluate_gate, main; the EXACT predicate; the dispositions; the budget-redo memo contents)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE-V2.md "Q6" (the re-probe feeds this; measured EUR factor; three totals; master-inclusive; contingency; egress; the gate predicate unchanged; note YELLOW-narrow-radius has LESS room post-Q3 so YELLOW-finer-split is the likelier lever)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv (the schema the model reads — region_id, ancestry, region_class, n_var, block_count, stage4_wall_min, end_to_end_wall_min, blocks_per_min, peak_executor_mem_gib, any_spill, cluster_vcpu, n_workers, cluster_hours, status) + m3-W2-preflight-counts.tsv (region_id, ancestry, region_class, window_span_mb, n_var, routed_path, est_block_count, est_output_gib, over_threshold)
    - src/python/ld_egress_bundle.py (Task 2 — reuse plan_egress_bundles for the egress projection; do NOT re-implement)
    - src/python/build_ld_region_manifest.py (the projection TSV with split_status in {whole,parent,subregion} + parent_region_id + n_subregions; xlarge parent = Sigma over its subregion rows)
    - config/ld_regions.tsv + .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv (the regenerated 322 logical parents + the expanded compute cells from Task 1)
  </read_first>
  <behavior>
    - test_three_separate_totals: returns (a) n_logical_parent_panels == 322, (b) n_compute_cells > 322 (post-split), (c) aggregate parent cost where an xlarge parent == sum over its split_status=="subregion" rows grouped by parent_region_id. Assert total_compute_cells > 322 and the per-parent aggregate equals the sub-row sum.
    - test_real_count_extrapolation_not_span: per-cell cluster-h from the PREFLIGHT n_var/block_count, NOT span; feed a preflight row whose n_var implies a different block_count than its span would and assert the model uses the preflight block_count.
    - test_master_inclusive_end_to_end_hours: cluster_hours per cell = (end_to_end_wall_min / 60) * (n_workers + 1) — the +1 is the MASTER; assert a cell's hours use n_workers+1 (not n_workers) and end_to_end wall (not stage4-only).
    - test_eur_factor_measured_then_fallback: with a COMPLETING measured EUR cell in the probe TSV, EUR_factor = afr_rate/eur_rate (measured); with no completing EUR cell, factor = 3.01 with a +/-20% band recorded as the source. (The prior probe row is INTERRUPTED/NA and must NOT be used as a rate — assert NA/INTERRUPTED rows are excluded.)
    - test_excludes_interrupted_rows: a probe TSV row with status=INTERRUPTED_write_bound / blocks_per_min=NA is EXCLUDED from the rate basis (the model errors or skips it, never treats NA as a rate) — guards the exact failure mode the prior probe hit.
    - test_contingency_factor_from_variance: a contingency factor from the observed probe blocks_per_min variance is applied; PROJECTED_with_contingency >= PROJECTED_raw and the factor is recorded (floor e.g. 1.15).
    - test_egress_bundle_projection: the model projects per-chromosome egress bundles (via ld_egress_bundle.plan_egress_bundles over the compute cells' est_output_gib) and flags vs EGRESS_CAP_GB=50.
    - test_gate_predicate_green: PROJECTED such that PROJECTED * 1.3 <= BUDGET_CAP -> disposition == "GREEN".
    - test_gate_predicate_red_and_levers: PROJECTED * 1.3 > BUDGET_CAP -> disposition in {"YELLOW-narrow-radius","YELLOW-finer-split","RED"}; YELLOW-finer-split recommended when a class dominates and the buffer is already narrow (post-Q3); RED when no lever room.
  </behavior>
  <action>
    1. Write `src/python/redo_ld_cost_model.py` per the m3-02c Task 4 spec (it was never built): `load_probe_rates(probe_tsv)` (EXCLUDING status=INTERRUPTED/NA rows — only completing cells contribute a rate), `load_preflight_counts(preflight_tsv)`, `eur_factor(probe_rates)` (measured afr/eur or 3.01 +/-20% fallback), `n_workers_plus_master(cluster_vcpu)` (workers + 1 master), `project_cell_hours(preflight_df, probe_rates, eur_factor)` (preflight_block_count / matched_blocks_per_min / 60 * (n_workers+1), EUR scaled by eur_factor, end_to_end overhead_factor from the probe's end_to_end/stage4 ratio), `three_totals(projected_df)` (322 logical / >322 compute / aggregate parent = Sigma over subregion rows), `apply_contingency(total_h, variance)` (1 + k*CoV, floor 1.15), `project_egress_bundles(preflight_df)` (REUSE ld_egress_bundle.plan_egress_bundles; sum est_output_gib per chrom; flag vs EGRESS_CAP_GB), `evaluate_gate(projected, budget_cap, *, lever_room)` encoding the EXACT predicate `projected * 1.3 <= budget_cap` with dispositions GREEN / YELLOW-narrow-radius / YELLOW-finer-split / RED. `main()` CLI `--probe-tsv --preflight-tsv --projection --budget-cap-cluster-h --out-budget-md` writing m3-W2-budget-redo.md with the THREE totals + contingency + per-chrom egress projection + BUDGET_CAP + the predicate evaluation + the credit-$ + the disposition. REQ-PATH-PARAMETERIZATION: no hardcoded /share|/rs1|/gpfs_common.

    2. Write `tests/m3/test_redo_ld_cost_model.py` with the 9 behavior tests above using synthetic in-memory preflight + probe TSVs (no cluster). Assert the exact gate predicate on BOTH GREEN and RED sides; assert the three-totals separation, the master-inclusive (n_workers+1) accounting, and the INTERRUPTED-row exclusion explicitly.

    3. Do NOT run the model against real data here — the real run happens in Task 5 (the gate) AFTER the re-probe produces completing rates. This task builds + unit-tests the script only.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_redo_ld_cost_model.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `test -f src/python/redo_ld_cost_model.py` exits 0.
    - `grep -c "projected \* 1.3 <= budget_cap\|projected\*1.3<=budget_cap\|PROJECTED.*1.3.*BUDGET_CAP" src/python/redo_ld_cost_model.py` returns >= 1 (exact predicate).
    - `grep -c "def evaluate_gate\|def project_cell_hours\|def eur_factor\|def three_totals\|def apply_contingency\|def project_egress_bundles\|def load_preflight_counts\|def load_probe_rates" src/python/redo_ld_cost_model.py` returns >= 7.
    - `grep -c "GREEN\|YELLOW-narrow-radius\|YELLOW-finer-split\|RED" src/python/redo_ld_cost_model.py` returns >= 4 (all dispositions).
    - `grep -c "n_workers + 1\|n_workers+1\|master" src/python/redo_ld_cost_model.py` returns >= 1 (master-inclusive).
    - `grep -c "INTERRUPTED\|NA\|status\|completing" src/python/redo_ld_cost_model.py` returns >= 1 (excludes interrupted/NA rows).
    - `grep -c "plan_egress_bundles\|ld_egress_bundle\|EGRESS_CAP" src/python/redo_ld_cost_model.py` returns >= 1 (reuses the egress helper, not re-implemented).
    - `grep -rn "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/redo_ld_cost_model.py` returns 0 (REQ-PATH-PARAMETERIZATION).
    - `pytest tests/m3/test_redo_ld_cost_model.py -v` reports >= 9 passed, 0 failed (incl. test_excludes_interrupted_rows + both gate-predicate sides).
  </acceptance_criteria>
  <done>
    redo_ld_cost_model.py exists, extrapolates COMPLETING-cell blocks_per_min over REAL preflight n_var/block_count (excluding INTERRUPTED/NA rows), keeps three separate totals (322 logical parents / expanded compute cells / aggregate = Sigma over sub-regions), computes master-inclusive end-to-end cluster-hours, applies a contingency factor, projects per-chromosome egress bundles (reusing ld_egress_bundle) vs the 50 GB ceiling, and evaluates the exact PROJECTED * 1.3 <= BUDGET_CAP gate with all four dispositions; >= 9 unit tests pass.
  </done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 4: IN-PERIMETER RE-PROBE — STEP A preflight on the RE-SPLIT manifest (confirm cells now under target) + fire COMPLETING AFR core5/buf3 + MANDATORY EUR core5/buf5 cells (ordering A vs B) + HLA region_00145 preflight on the existing 64 GB cluster (cores=1), data-layer-verified, guaranteed verified shutdown; REPLACE the INTERRUPTED cost-probe TSV with completing-cell rates</name>
  <files>.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv, .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv, .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE-V2.md "Q6" (the FULL re-probe design: the 64 GB cluster at cores=1, NOT n2-highmem; the 4 cells; both compute cells must COMPLETE; the 90-min wall control; A-vs-B comparison) + "Common Pitfalls" (don't re-apply n2-highmem/cores=2; don't treat _SUCCESS/interrupted as a rate; HLA density)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv + m3-W2-cluster-shutdown.md (the PRIOR INTERRUPTED probe — what to fix: produce COMPLETING cells)
    - .claude/skills/aou-ld-pipeline/SKILL.md "Fresh-clone re-run checklist" + "LD compute (AOU-2) specifics" + "The invariants" (the 3 prep landmines; data-layer verify; the websocket-drop orphan-kernel kill; do-not-run-from-main; the fan-out GCS-listing liveness arbiter)
    - config/ld_regions_dev.tsv (REGENERATED by Task 1 at core5/buf3 AFR / buf5 EUR — the re-probe cells) + config/ld_regions.tsv
    - .planning/notebooks/AOU-2_per_region_ld.ipynb (the per-region loop; the executor-config cell — set cores=1 per Q6, NOT cores=2)
    - feedback_push_ncsu_before_aou_clone_fire (PUSH origin == local HEAD before the clone-based fire; the AoU Workbench pulls origin)
  </read_first>
  <action>The Task-1/2/3 code + the regenerated manifests must be COMMITTED AND PUSHED (origin == local HEAD) before this fire — the AoU Workbench clones origin. The agent's only pre-fire actions: confirm config/ld_regions_dev.tsv carries the re-probe cells at the new geometry (AFR m2_region_00040__sub00 buffer_bp 3_000_000, EUR m2_region_00040__sub00 buffer_bp 5_000_000, an HLA region_00145 sub-row) and confirm origin is pushed. The agent does NOT cross the perimeter. Carter fires; the agent verifies the recorded TSVs + the shutdown artifact afterward.</action>
  <human_gate>
    <gate>Re-probe: completing AFR + EUR cells at the locked buffers (ordering A vs B) on the 64 GB cluster, data-layer-verified, verified shutdown</gate>
    <description>
      The prior probe (2026-06-22) was INTERRUPTED write-bound at the 10 Mb buffer (blocks_per_min=NA) — the cost model has no completing rate. This re-probe produces COMPLETING properly-sized cells at the locked 3/5 Mb buffers so the cost model gets a real rate.

      PRE-FLIGHT (on the existing 64 GB cluster — NO n2-highmem, NO new quota):
      - PUSH first: confirm origin == local HEAD (the Workbench clones origin; [[feedback_push_ncsu_before_aou_clone_fire]]).
      - START the existing 64 GB n2-standard-16 x24 HAIL cluster 20260604 (already provisioned, no-spill-validated by the prior probe). Confirm region us-central1.
      - git checkout m3-W2-aou-deltas (NOT main) -> git pull -> git checkout -f (the Workbench filter re-dirties notebooks).
      - The 3 prep landmines (SKILL.md): symlink ~/coloc_analysis -> synced repo; pin WORKSPACE_BUCKET=gs://rw-migration-aou-rw-476cdac2 via a HARD os.environ override; os.chdir(~/coloc_analysis) before the per-region loop.
      - Executor config = cores=1 / 11g / 3g (the prior probe ran clean at cores=1 with ZERO spill; do NOT raise to cores=2 — research Q6 Pitfall 1 says cores=2 is UNVALIDATED). Confirm PYSPARK_SUBMIT_ARGS bound before pyspark import.

      STEP A — PREFLIGHT COUNT PASS on the RE-SPLIT manifest (cheap, in-perimeter):
      Run a count-only pass over the re-split compute cells -> REPLACE m3-W2-preflight-counts.tsv (same columns: region_id, ancestry, region_class, window_span_mb, n_var, routed_path, est_block_count, est_output_gib, over_threshold). CONFIRM the fix: at core5/buf3 (AFR) / buf5 (EUR) the cells are now ~80k var (AFR) / ~60k var (EUR) and over_threshold flips to False for the represented cells (the prior preflight had EVERY cell over_threshold=True at the 10 Mb buffer). MANDATORY: include the HLA region_00145 sub-region(s) — if HLA/chr6 density pushes a cell over ~80k var, set --max-subregion-span-mb 3 for chr6 and re-split (the preflight catches it, research A6).

      STEP B — FIRE COMPLETING PROBE CELLS (hard cost controls; both MUST complete):
      Encode the controls in the loop BEFORE firing: MAX_WALL_MIN_PER_CELL = 90 (if exceeded, that itself is a finding -> write still too slow -> finer split / harder on ordering B); MAX_PROBE_CREDIT_USD (~$60); spill/OOM kill (drop to cores=1 if any spill appears — though none is expected). Fire:
      1. AFR m2_region_00040__sub00 re-split at core5/buf3 (~80k var, ~200 blocks, ~3.5 GiB) — the dominant AFR cost class; must COMPLETE the write.
      2. MANDATORY EUR m2_region_00040__sub00 at core5/buf5 (~60k var, ~112 blocks, ~2.4 GiB) — measures the REAL EUR/AFR factor (not the assumed 3.01x); must COMPLETE.
      3. ORDERING A vs B: fire the SAME AFR cell via ordering A and ordering B and record both wall-clocks; pick the faster (B is the favored hypothesis — banded scratch ~7x smaller at radius<<span). Numerics are byte-identical either way.
      4. HLA region_00145 sub-region: preflight count (STEP A) is sufficient unless it overshoots ~80k var, in which case probe one re-split HLA cell.

      DATA-LAYER VERIFY (D-M3-10 — _SUCCESS is NOT evidence): for each fired cell gsutil du -s the .bm/.npz under gs://rw-migration-aou-rw-476cdac2/ld/{AFR_aou,EUR_aou}/ (>> 0) AND a Hail/np read-back count BEFORE recording the cell as complete. Use the GCS object-listing liveness arbiter (not jstack) during quiescent gaps.

      BAND-EDGE CHECK (closes research A1): on a completing cell, record max |r| for variant pairs at the band edge (~buffer distance) — confirm it is at noise level (evidence the 3/5 Mb buffer is wide enough). Note it in the SUMMARY.

      RECORD m3-W2-cost-probe.tsv — REPLACE the INTERRUPTED row with >= 2 COMPLETING rows (AFR core5/buf3 + the mandatory EUR core5/buf5; plus the ordering-A AFR row if both were fired), each with a REAL non-NA blocks_per_min, the master-inclusive end_to_end cluster_hours, any_spill, status=COMPLETED. The columns are the existing schema. Tag (ancestry, region_class).

      STEP C — GUARANTEED SHUTDOWN + VERIFICATION:
      STOP the cluster and UPDATE m3-W2-cluster-shutdown.md with: the stop command + output, the timestamp, state == STOPPED, and a $0/idle billing check. Prose alone does not satisfy this.
    </description>
    <unblocks>Task 5 (the cost-model run + go/no-go gate — needs the completing-cell rates)</unblocks>
    <how-to-resolve>
      1. PUSH (origin == local HEAD); start 20260604; checkout m3-W2-aou-deltas; the 3 landmines; cores=1 confirmed.
      2. STEP A: count pass on the re-split manifest -> REPLACE m3-W2-preflight-counts.tsv; confirm cells now under target; re-split chr6 finer if HLA overshoots.
      3. STEP B: fire AFR core5/buf3 + the MANDATORY EUR core5/buf5 to COMPLETION (both writes finish); fire ordering A vs B on the AFR cell; data-layer-verify each; record the band-edge max |r|.
      4. REPLACE m3-W2-cost-probe.tsv with >= 2 COMPLETING rows carrying real blocks_per_min (status=COMPLETED, not INTERRUPTED).
      5. STEP C: STOP the cluster; update m3-W2-cluster-shutdown.md with the stop output + $0 idle check.
      6. Type "reprobe-recorded" to resume; Task 5 reads the refreshed TSVs.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv &amp;&amp; head -1 .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv | grep -q "routed_path" &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv &amp;&amp; head -1 .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv | grep -q "blocks_per_min" &amp;&amp; test $(grep -ci "COMPLETED" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv) -ge 2 &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md &amp;&amp; echo OK</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv` exits 0; `head -1` contains n_var, routed_path, est_block_count, over_threshold.
    - `grep -c "region_00145\|HLA\|6p21" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv` returns >= 1 (HLA in the re-probe preflight).
    - The re-split preflight shows at least one cell with over_threshold == False (the buffer-floor fix landed — was all-True at the 10 Mb buffer): `grep -ci "False\|false" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv` returns >= 1.
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` exits 0; `head -1` contains region_id, ancestry, region_class, block_count, blocks_per_min, end_to_end_wall_min, cluster_hours.
    - `grep -ci "COMPLETED" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` returns >= 2 (>= 2 COMPLETING cells — NOT INTERRUPTED; the prior NA basis is replaced).
    - `grep -c "EUR" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` returns >= 1 (the MANDATORY EUR cell completed).
    - No COMPLETED row has blocks_per_min == NA: `awk -F'\t' 'NR>1 && tolower($0) ~ /completed/ && ($8=="NA"||$8=="") {n++} END{exit n>0}' .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` exits 0 (every completing cell carries a real rate).
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md` exits 0; `grep -ci "stop\|stopped\|deleted" m3-W2-cluster-shutdown.md` (phase dir) returns >= 1 AND `grep -ci "\\$0\|idle\|no running\|billing" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md` returns >= 1.
  </acceptance_criteria>
  <done>
    A re-split preflight confirms the cells are now under target (over_threshold flips False for represented cells; HLA region_00145 included + re-split finer if needed); the re-probe fires COMPLETING AFR core5/buf3 + the MANDATORY EUR core5/buf5 cells (ordering A vs B, faster picked) to write-completion on the 64 GB cluster at cores=1 with hard cost controls; each cell is data-layer-verified; the band-edge max |r| is recorded; m3-W2-cost-probe.tsv is REPLACED with >= 2 COMPLETING rows carrying real blocks_per_min (the prior INTERRUPTED/NA basis is gone); the cluster is shut down with a verified artifact.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 5: Run redo_ld_cost_model.py on the completing-cell rates + write m3-W2-budget-redo.md with the 3 totals, contingency, per-chrom egress projection, and the PROJECTED * 1.3 <= BUDGET_CAP go/no-go disposition (322-cell fire stays in m3-04)</name>
  <files>.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md</files>
  <read_first>
    - src/python/redo_ld_cost_model.py (Task 3 — the model + its main() CLI)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv (Task 4 — the REPLACED completing-cell rates + measured EUR factor) + m3-W2-preflight-counts.tsv (Task 4 — the re-split REAL per-cell counts)
    - config/ld_regions.tsv + .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv (Task 1 — the 322 logical parents + expanded compute cells at the new geometry)
    - .planning/STATE.md (BUDGET_CAP_CLUSTER_H — Carter's approved credit cap; re-confirm the number at the gate)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE-V2.md "Q6" (the dispositions; post-Q3 YELLOW-finer-split is the likelier lever since the radius is already narrow)
  </read_first>
  <action>
    1. Run `python src/python/redo_ld_cost_model.py --probe-tsv .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv --preflight-tsv .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv --projection .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv --budget-cap-cluster-h <BUDGET_CAP_CLUSTER_H from STATE.md, re-confirmed with Carter> --out-budget-md .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md`.

    2. The memo MUST state: the THREE totals (322 logical parents / expanded compute cells / aggregate parent = Sigma over sub-regions), the contingency factor (from probe variance), the per-chromosome egress bundle projection vs the 50 GB working ceiling (noting it is a conservative project ceiling, not a documented hard cap; confirm on first export per Q5/A2), the BUDGET_CAP_CLUSTER_H, the evaluated `PROJECTED * 1.3 <= BUDGET_CAP` result, the disposition (GREEN / YELLOW-narrow-radius / YELLOW-finer-split / RED) — where post-Q3 YELLOW-finer-split (lower --max-subregion-span-mb) is the likelier lever since the buffer is already narrow — the measured EUR/AFR factor, the ordering A-vs-B winner from the re-probe, the band-edge max |r| (A1 closure), and EXPLICITLY that the full 322-cell production fire is OUT of scope here and stays in Wave 4 (m3-04). If GREEN, state m3-04 is unblocked; if RED/YELLOW, state the next lever + that a re-probe is needed before m3-04.

    3. This task runs the ALREADY-UNIT-TESTED model (Task 3) on the REAL completing rates (Task 4) — no new code. If the model surfaces a bug on the real TSVs, fix it in redo_ld_cost_model.py + add a regression test (do not patch the memo around a model bug).
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_redo_ld_cost_model.py -q &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md &amp;&amp; grep -c "PROJECTED" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` exits 0.
    - `grep -c "PROJECTED" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1.
    - `grep -c "BUDGET_CAP" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1.
    - `grep -cE "GREEN|YELLOW|RED" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1 (the disposition).
    - `grep -ci "logical parent\|compute cell\|aggregate" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1 (3 totals stated).
    - `grep -ci "contingency" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1.
    - `grep -ci "egress\|50 GB\|per-chrom" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1 (egress projection).
    - `grep -ci "ordering A\|ordering B" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1 (the A-vs-B winner recorded).
    - `grep -ci "out of scope\|Wave 4\|m3-04" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1 (322-cell fire stays in m3-04).
    - `pytest tests/m3/test_redo_ld_cost_model.py -q` reports 0 failed (the model still passes after any real-data fix).
  </acceptance_criteria>
  <done>
    redo_ld_cost_model.py is run on the COMPLETING-cell rates + re-split real preflight counts; m3-W2-budget-redo.md records the three totals + contingency + per-chrom egress projection vs the 50 GB ceiling + BUDGET_CAP + the exact PROJECTED * 1.3 <= BUDGET_CAP evaluation + the disposition (GREEN/YELLOW/RED, with YELLOW-finer-split flagged as the likely post-Q3 lever) + the measured EUR factor + the ordering A-vs-B winner + the band-edge A1 closure + the explicit note that the 322-cell fire stays in m3-04.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| AoU perimeter -> NCSU | The re-probe + preflight produce summary LD .npz/.bm + AF + count metrics in the in-perimeter bucket; nothing crosses to NCSU except the hand-recorded cost/count metrics (blocks_per_min, n_var, cluster_hours) in the TSVs. No individual-level genotypes leave the perimeter (REQ-AOU-LD-EGRESS). |
| Buffer width -> LD completeness | A too-narrow band zeroes real cross-core LD; the locked 3/5 Mb buffers are 3-5x the LD-decay scale, and the overlapping-window stitch RETAINS within-buffer pairs. The band-edge max-|r| check (Task 4) confirms the band is wide enough (closes A1). |
| Ordering reorder -> numerics | Ordering B moves the checkpoint position but composes the SAME three ops (row_correlation -> band -> write); numerics are byte-identical. The AST ordering-lock test prevents silent reversion to the dense-scratch ordering A. |
| Interrupted rate -> cost model | The prior probe's NA/INTERRUPTED row, if fed as a rate, produces a garbage budget; the model EXCLUDES non-completing rows and the re-probe REPLACES the TSV with completing cells. |
| Cluster spend -> credit balance | The re-probe spends real AoU credits; executable cost controls (90-min wall, ~$60 credit cap, spill/OOM kill, guaranteed verified shutdown) cap the probe; the go/no-go gate caps the much larger production spend. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M3RS2-EGRESS-01 | Information disclosure | controlled-tier AoU genotypes during the re-probe + the future production export | mitigate | The re-probe emits only summary LD + AF to the in-perimeter bucket (REQ-AOU-LD-EGRESS); each cell (60k+ AFR / 60k+ EUR) trivially clears the n>=20 suppression floor; nothing individual-level crosses to NCSU. The per-chrom egress bundling helper (Task 2) + the cost-model egress projection (Task 3/5) size the FUTURE export vs the 50 GB working ceiling; no egress request is filed here (it stays in m3-04). |
| T-M3RS2-WRITE-01 | DoS / cost-overrun | the A.3 write stage (the measured bottleneck) + the production 322-cell fire | mitigate | Ordering B shrinks the materialized scratch ~7x at radius<<span (attacking the measured ~0.15 dense-tasks/min write); the smaller per-ancestry buffer drops every cell to single-digit GiB / ~200 blocks; the re-derived write-block + output-GiB over_threshold flags any cell that would still be write-intractable BEFORE the production fire. |
| T-M3RS2-NUMERICS-01 | Integrity | the ordering-B reorder silently changing LD values | mitigate | Ordering B is byte-identical to ordering A (same three ops, only the checkpoint position moves); blocks_only stays False (exact in-band r); the AST ordering-lock test + the retained op-presence tests guard it; the re-probe fires BOTH orderings and the numerics are cross-checked. |
| T-M3RS2-BAND-01 | Integrity | a 3/5 Mb buffer zeroing real cross-core LD (A1) | mitigate | The buffers are 3-5x the cited AFR/EUR LD-decay scale and below Pan-UKBB's conservative 10 Mb; the overlapping-window stitch retains within-buffer pairs; the Task-4 band-edge max-|r| check empirically confirms the band edge is at noise level (closes A1). |
| T-M3RS2-COST-01 | Integrity / under-estimation | a too-cheap projection re-greenlighting an intractable fire (the dev-10 / interrupted-probe trap) | mitigate | The cost model consumes REAL re-split preflight n_var/block_count (not span guesses), the MEASURED EUR factor (the mandatory completing EUR cell), MASTER-inclusive end-to-end cluster-hours, a contingency factor, three separate totals, and EXCLUDES INTERRUPTED/NA rows — closing both the 36-110x dev-10 under-estimate and the NA-rate trap. |
| T-M3RS2-PROBE-01 | Integrity / false-completion | _SUCCESS over an empty/partial .npz/.bm masking a non-completing cell (the exact prior failure) | mitigate | D-M3-10 contents-validation: each cell is gsutil-du + Hail/np count verified BEFORE being recorded; the cost model excludes non-COMPLETED rows; the re-probe requires the WRITE to finish (the prior probe failed precisely because it didn't). |
| T-M3RS2-HLA-01 | Integrity | HLA/6p21 (region_00145) density exceeding the core5/buf3 ~80k-var assumption (A6) | mitigate | The re-probe STEP-A preflight MANDATORILY includes region_00145; if it overshoots ~80k var, --max-subregion-span-mb is dropped to 3 for chr6 and the region re-split before the cost model consumes it. |
| T-M3RS2-CLUSTER-01 | Availability / wrong-sizing | re-applying the unvalidated n2-highmem/cores=2 recommendation | accept->mitigate | The probe overturned the n2-highmem premise (no spill at cores=1 on 64 GB); the re-probe runs on the EXISTING 64 GB cluster at cores=1; cores=2 is only revisited if a completing cell shows new spill. No quota ticket (N2_CPUS=5000 pre-satisfied). |
</threat_model>

<verification>
**Plan-level checks:**

1. build_ld_region_manifest emits per-ancestry buffer geometry (AFR 3 Mb / EUR 5 Mb, core 5 Mb) threaded as CLI parameters (not hardcoded); config/ld_regions.tsv + ld_regions_dev.tsv + the projection are regenerated at the locked sizes (Task 1).
2. _write_a3_banded_correlation_bm applies the band BEFORE the checkpoint (ordering B), guarded by the AST ordering-lock test; the lower_triangular flag contract is preserved; the over_threshold criterion is re-derived around write-block-count + output-GiB; the per-chrom egress helper splits >50 GB bundles (Task 2).
3. `pytest tests/m3/test_redo_ld_cost_model.py -v` >= 9 passed; redo_ld_cost_model.py exists with the exact PROJECTED * 1.3 <= BUDGET_CAP predicate, the four dispositions, master-inclusive accounting, and INTERRUPTED-row exclusion (Task 3).
4. m3-W2-preflight-counts.tsv regenerated on the re-split manifest (cells under target, over_threshold flips False for represented cells, HLA included); m3-W2-cost-probe.tsv REPLACED with >= 2 COMPLETING rows carrying real blocks_per_min incl. the mandatory EUR cell; m3-W2-cluster-shutdown.md updated with a verified shutdown (Task 4).
5. m3-W2-budget-redo.md states the THREE totals + contingency + per-chrom egress projection + BUDGET_CAP + the `PROJECTED * 1.3 <= BUDGET_CAP` evaluation + disposition + the ordering A-vs-B winner + the band-edge A1 closure + the explicit "322-cell fire stays in m3-04" note (Task 5).
6. REQ-PATH-PARAMETERIZATION: `grep -rn "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/ld_egress_bundle.py src/python/redo_ld_cost_model.py` returns 0.
7. `pytest tests/m3 -q` reports 0 failed (no regression; the lower_triangular flag-contract + existing A.3 op-presence tests stay green).
</verification>

<success_criteria>
- The banding buffer is per-ancestry (AFR 3 Mb / EUR 5 Mb over a 5 Mb core), threaded as CLI parameters through both build_manifest and split_existing_manifest; the manifests are regenerated at the locked sizes with every AFR cell <= ~80k var and every EUR cell <= ~60k var (the buffer-floor fix).
- The A.3 write uses ordering B (band-before-checkpoint), guarded by an AST ordering-lock test; numerics are byte-identical (blocks_only=False); the npz lower_triangular flag contract is preserved.
- The split/over_threshold criterion is re-derived around A.3 write block-count + per-cell egress output GiB (not the retired 75k-var memory proxy); a reusable per-chromosome egress-bundling helper splits a >50 GB bundle.
- redo_ld_cost_model.py is built + unit-tested (the m3-02c Task 4 that was never written): real-count extrapolation, three separate totals, master-inclusive end-to-end cluster-hours, contingency, per-chrom egress projection, the exact PROJECTED * 1.3 <= BUDGET_CAP gate, and INTERRUPTED-row exclusion.
- The in-perimeter re-probe produces COMPLETING AFR core5/buf3 + the MANDATORY EUR core5/buf5 cells (ordering A vs B) on the existing 64 GB cluster at cores=1, data-layer-verified, with a verified shutdown; m3-W2-cost-probe.tsv is replaced with real completing-cell rates (the prior INTERRUPTED/NA basis is gone).
- m3-W2-budget-redo.md records the three totals + cap + disposition (GREEN/YELLOW/RED) + the ordering winner + the band-edge A1 closure + the explicit out-of-scope note; the full 322-cell production fire stays in Wave 4 (m3-04). This plan ends at the go/no-go decision.
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-02d-W2-rescope-write-egress-split-SUMMARY.md` recording:
- The per-ancestry buffer change (how the geometry was made ancestry-specific without hardcoding 3/5) + the regen command + the resulting cell sizes (AFR/EUR var counts, banded output GiB)
- The ordering-B enablement + the AST ordering-lock test + confirmation the lower_triangular flag contract + existing A.3 tests stayed green
- The re-derived write+egress over_threshold criterion (the chosen WRITE_BLOCK_THRESHOLD + OUTPUT_GIB_THRESHOLD + their derivation) + the per-chrom egress helper
- redo_ld_cost_model.py (the previously-unbuilt m3-02c Task 4): the functions, the INTERRUPTED-row exclusion, the test count
- The re-probe: the re-split preflight (cells now under target; HLA region_00145 outcome + any chr6 finer split); the COMPLETING AFR + EUR blocks_per_min; the measured EUR/AFR factor (vs the assumed 3.01x); the ordering A-vs-B winner + wall-clocks; the band-edge max |r| (A1 closure); the cost controls that fired; the verified shutdown ($0 idle)
- The new PROJECTED (all THREE totals) vs the stale ~1,117 + the contingency factor + the per-chrom egress projection vs the 50 GB ceiling + the BUDGET_CAP_CLUSTER_H + the disposition (GREEN/YELLOW/RED) + the next step (m3-04 unblocked, or which lever + re-probe)
</output>
