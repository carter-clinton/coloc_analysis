# Phase M3 — Wave-2 RE-SCOPE Research ADDENDUM (real-cohort LD compute)

**Researched:** 2026-06-18
**Domain:** AoU/Verily RW2.0 Dataproc vCPU quota mechanics; Hail `row_correlation`/BlockMatrix sample-count scaling; xlarge-region splitting in `build_ld_region_manifest.py`; banded block-diagonal stitching in `ld_npz_to_rds.R`; cost-probe methodology
**Confidence:** HIGH on the compute-scaling dimensional argument and the split/stitch code design (verified against the actual source); MEDIUM on the Pan-UKBB cluster anchor (cited, public); LOW on AoU-specific quota ceiling + lead time (live-only confirmable — flagged below)
**Status:** ADDENDUM — supplements `m3-RESEARCH.md` (still valid for pipeline mechanics, Hail API, validation architecture, egress). This file answers ONLY the new questions the dev-10 capacity wall surfaced.

---

## Scope note (what this addendum does and does NOT do)

The three re-scope decisions are LOCKED (split xlarge ≤75k var; n2-highmem-16 / 384 vCPU; cost-probe before full fire). This research does not relitigate them — it answers "how to implement them well." Everything in `m3-RESEARCH.md` (the 12 Q answers, Hail v0.2.x API table, the 4-check Validation Architecture, the §6 manifest schema, the OOM driver-memory math, egress) remains the authoritative base. The dev-10 kill invalidated exactly one thing in the base: the **cost model** (the `est_cluster_hours_per_ancestry` column in `build_ld_region_manifest.py` lines 348–357 and the ~1,117 cluster-h total in D-M3-09) was sized off a 2,000-sample synthetic repro and is now known-stale-low. Q-RS5 redoes it.

---

## Q-RS1 — AoU vCPU quota mechanics (n2-highmem-16 × 24 = 384 vCPU)

### Findings

**Quota dimension that blocks the cluster `[VERIFIED: cloud.google.com/dataproc/quotas + GCP machine-family quota model]`:** Dataproc clusters are plain Compute Engine VMs, so cluster size is bounded by **regional Compute Engine quotas in `us-central1`**, NOT a Dataproc-specific limit. The blocking dimension for a 24× n2-highmem-16 + 1 master (25 × 16 = **400 vCPU**) cluster is the **regional `N2_CPUS` quota** (machine-family-specific), which is a *separate* quota from the generic `CPUS` (legacy N1) and from `CPUS_ALL_REGIONS` (global). A project that has plenty of generic `CPUS` headroom can still fail to start an all-N2 cluster if `N2_CPUS` in `us-central1` is low (the common default for a fresh project is 24–32). This is consistent with the dev-10 diagnosis: the original 24-worker build failed, the 2→16 resize *succeeded* — which means the cap is a numeric ceiling on concurrent vCPUs of that family, not a project-level block. `[VERIFIED: discuss.google.dev "CPU quota vs All CPUs" — per-family quotas are distinct]`

**Critical N1-vs-N2 trap `[CITED: cloud.google.com/compute/quotas machine-family model]`:** the existing AoU runbook (SKILL.md "Fresh-clone re-run checklist" step 1) specifies **N1** workers (`n2-standard-16` is named there but historical clusters used n1-highmem). The re-fire moves to **N2** (`n2-highmem-16`). The quota that must be raised is therefore `N2_CPUS`, and a request that raises `CPUS` (N1) will NOT unblock an N2 cluster. **Carter's quota-increase request MUST name the N2 family and `us-central1` explicitly.** `[ASSUMED]` that the workspace region is `us-central1` — this is consistent with SKILL.md ("HAIL 0.2.135, 24 workers, us-central1") and the RW2.0 coordinates, but reconfirm in the env panel before filing.

**n2-highmem-16 availability `[VERIFIED: cloud.google.com/dataproc supported-machine-types]`:** N2 machine types (including n2-highmem-16: 16 vCPU / 128 GB) are supported as both Dataproc master and worker types and are available in `us-central1`. n2-highmem-16 is a stock predefined type (no custom-type request needed).

**Request path + lead time `[ASSUMED — live-only confirmable, see flag]`:** the standard GCP path is IAM & Admin → Quotas → filter `N2 CPUs` / region `us-central1` → Edit Quotas → submit increase. **BUT** in the AoU RW2.0 / Verily perimeter the billing project (`wb-perky-corn-6639`) is org-managed, and the Console quota page may be restricted by the VPC-SC perimeter / org policy (the same wall that blocks data-plane gsutil from HPC per memory `reference_wb_cli_hpc_setup`). The realistic path is likely an **AoU support / Verily request ticket**, not a self-serve Console edit. AoU support's documented SLA for routine requests is "2–5 business days" (same SLA cited for egress in `m3-RESEARCH.md` Q3), but quota increases that require GCP-side approval can take **longer (days to ~2 weeks)** and are not guaranteed to the full requested ceiling.

**Realistic ceiling for a controlled-tier workspace `[ASSUMED — live-only confirmable]`:** unknown from public docs. Pan-UKBB ran 500× n1-standard-8 = **4,000 vCPU** on Dataproc (but on the Broad's own GCP project, not an AoU controlled-tier workspace) `[CITED: pan.ukbb LD release blog]`. AoU controlled-tier workspaces have historically been capped well below that. 384 vCPU is a modest ask by Dataproc standards and is plausibly grantable, but **treat the ceiling as unknown until Carter gets a number back.**

### Recommendation (planner-actionable)

1. **Pre-cluster human-action gate (Carter):** file the quota-increase request naming **`N2_CPUS` ≥ 400, region `us-central1`** (24 workers + 1 master × 16 vCPU = 400; ask for 400–512 to leave headroom). Do this FIRST — it is the longest-lead item and gates the cost probe. Log it as a gate in the plan exactly like the egress gate.
2. **Fallback ladder if the full 384 is not granted:** the cluster size is a tuning knob, not a correctness gate (the *split* is what makes xlarge tractable, per the rescope). If only ~256 vCPU (16 workers) is granted, the cost probe still runs and the full fire just takes proportionally longer wall-clock. Plan should encode "cluster size = min(granted N2 quota, 400 vCPU)".
3. **Verify the family in the env panel before the probe** — the AoU env panel must show n2-highmem workers, not n1-highmem; otherwise the resize lands on the wrong family and the spill problem persists.

### Live-only flags
- ⚠️ The exact request path (Console self-serve vs AoU/Verily ticket) is **VPC-SC-gated and confirmable only from inside the perimeter / via AoU support**. Do not assume the Console quota page is reachable.
- ⚠️ The grantable ceiling for this controlled-tier workspace is **unknown from public docs** — Carter must get a number.
- ⚠️ Reconfirm workspace region == `us-central1` in the env panel before filing.

---

## Q-RS2 — Hail row_correlation / BlockMatrix scaling with sample count

### Findings — the dimensional argument is correct

The correlation is `C = Z @ Z.T` where `Z` is the standardized genotype matrix of shape `(n_var, n_samples)` (Hail `row_correlation` standardizes each variant row, then Grams the rows). The output `C` is `(n_var, n_var)` — **its shape does NOT depend on n_samples.** But the *cost to compute each output block* does: each entry `C[i,j] = Σ_s Z[i,s]·Z[j,s]` is a dot product over the **sample axis**, so the FLOP count for the full matmul is `O(n_var² · n_samples)`. The sample count is the **contracted (inner) dimension** of the matmul. `[VERIFIED: linear-algebra first principles + Hail row_correlation docstring — standardize-then-Gram]`

This confirms the rescope's claim dimensionally:
- AFR 73,122 / repro 2,000 = **36.6×** more FLOP per output block. `[VERIFIED: arithmetic]`
- EUR 220,098 / 2,000 = **110.0×**. `[VERIFIED: arithmetic]`
- EUR / AFR = 220,098 / 73,122 = **3.01×** per block — the "EUR ~3× AFR" weighting in the cost model is exactly the sample ratio. `[VERIFIED: arithmetic]`

The repro (928 s for 130k var × 1024 blocks at n=2,000) measured the *operation shape* (blocks advance, no driver-collect hang) but, because wall-time per block scales ~linearly with the inner dim, its 928 s was **never representative** of a 36–110× heavier real-cohort block. This is the banked lesson (`feedback_size_cost_experiments_on_real_data_dimensions`); the dimensional analysis here is its formal backing.

**Block size `[VERIFIED: Hail BlockMatrix.default_block_size == 4096]`:** Hail tiles the `(n_var, n_var)` matrix into 4096×4096 blocks. Per-block memory during the matmul holds two standardized panels of shape `(4096, n_samples)` plus the `(4096, 4096)` output block:
- `2 × 4096 × n_samples × 8 bytes (float64 standardized) + 4096² × 8`
- AFR (73,122): `2 × 4096 × 73,122 × 8 ≈ 4.79 GiB` of input panels **per block-pair** + 128 MiB output. EUR (220,098): `≈ 14.4 GiB` input panels per block-pair.
- This is why the **16 GB workers spilled** on the dev cluster — a single EUR block-pair's standardized panels alone (~14 GiB) do not fit alongside Spark/JVM overhead in a 16 GB executor. The 128 GB n2-highmem-16 worker holds many concurrent block-pairs without spill. `[VERIFIED: block-memory arithmetic; consistent with the dev-10 spill observation]`

**The master crash `[VERIFIED: consistent with code + dev-10 observation]`:** the A.3 helper `_write_a3_banded_correlation_bm` checkpoints the materialized correlation to scratch. For region_00006 (122,678 var) the dense correlation is `122,678² × 4 bytes ≈ 56 GiB` — matching the observed ~65 GiB scratch that destabilized the 64 GB master. **The split (Q-RS3) directly fixes this:** a ≤75k-var sub-region's dense scratch is `75,000² × 4 ≈ 21 GiB` (and region_00006 at 122k stays WHOLE per the locked decision — see the caveat in Q-RS3). The n2-highmem-16 master (128 GB) also raises the ceiling under which a whole-region scratch must fit.

**Pan-UKBB anchor (the load-bearing external data point) `[CITED: pan.ukbb.broadinstitute.org/blog/2020/10/29/ld-release]`:** genome-wide in-sample LD (BlockMatrix) for **all six ancestries** at a **10 Mb radius** took **~16 h wall-clock on 500× n1-standard-8 preemptible = ~64,000 CPU-hours**, producing 43.3 TB (AFR alone 12.0 TB). Two implications:
1. **Radius matters enormously.** Pan-UKBB banded at **10 Mb**, not `span + 500 kb` (the current manifest's scheme, which for xlarge regions caps at 50 Mb and for whole regions equals the full span). The current scheme materializes a **far wider band** than Pan-UKBB does. Narrowing the export radius is a free, un-explored cost lever (see Q-RS5 recommendation 4). Note `feedback`: dropping below `span` re-opens the retired-ordering-B benefit, but that is out of scope here — flag for the cost-probe outcome.
2. **n1-standard-8 = 7.5 GB/vCPU** is the memory-per-CPU "sweet spot" the UKB community cites for BlockMatrix shuffles `[CITED: community.ukbiobank Hail GWAS thread]`. n2-highmem-16 is **8 GB/vCPU** — slightly richer, appropriate for the larger AoU sample panels. The locked choice is sound.

### Recommended executor configuration for n2-highmem-16 (16 vCPU / 128 GB)

Apply the established project lever — `hl.init(spark_conf=...)` is silently dropped on YARN, so set `PYSPARK_SUBMIT_ARGS` **before** the pyspark/hail import (SKILL.md baked Cell-1a guard; memory `feedback_aou_dataproc_pyspark_submit_args`):

| Setting | Value | Rationale |
|---|---|---|
| `spark.executor.cores` | **2** (raise from W1's `1`) | W1's `cores=1` was the v8 partition-explosion OOM remediation for the *cohort build* (290k-partition genome-wide plan). The LD matmul is a different workload — block-parallel, memory-bound on the sample panel. With 128 GB workers the per-block panel (~5 GiB AFR / ~14 GiB EUR) fits with cores=2; this doubles matmul parallelism per worker vs cores=1. **Validate on the cost probe** — if EUR spills at cores=2, drop to cores=1. |
| `spark.executor.memory` | **~24–28 g** | Leave ~30% of the 128 GB node for off-heap/JVM/shuffle. At cores=2 that is ~12–14 g/core, comfortably above one EUR block-panel. |
| `spark.executor.memoryOverhead` | **~8–12 g** | BlockMatrix shuffles are off-heap heavy; under-provisioning overhead is the classic Dataproc OOM-kill. |
| `spark.driver.memory` | **~24 g** (n2-highmem-16 master = 128 GB) | The A.3 path no longer driver-collects the matmul (the fix), but the checkpoint coordination + `_assert_blockmatrix_written` read-back need headroom. |
| `block_size` | **Hail default 4096** (per Q3 in `m3-02-W2-DESIGN-DELTA`, no tuning) | Revisit only if a sub-region OOMs at scale on the probe. |

`[ASSUMED]` on the exact memory split — these are defensible Dataproc-for-Hail starting points, not measured on AoU n2-highmem-16. **The cost probe (Q-RS5) is where these get tuned;** do not lock them as decisions before the probe.

### Live-only flags
- ⚠️ `cores=2` vs `cores=1` and the exact memory split must be **validated on the probe** with real EUR (220k) samples — the spill threshold is sample-count-dependent and only measurable in-perimeter.

---

## Q-RS3 — Encoding the xlarge split in `build_ld_region_manifest.py`

### Findings (from reading the actual source)

The manifest builder (read in full) currently: lifts each M2 region GRCh37→GRCh38, computes `radius_bp = min(span + 500kb, 50Mb)`, assigns `region_class ∈ {small,medium,large,xlarge}` by span, and emits **one manifest row per (region, ancestry)** with columns `MANIFEST_COLUMNS` (region_id, chr, start/end ×2 builds, ancestry, source_trait, lead_variant, radius_bp, region_class, liftover_status). The dev selector (`select_ld_regions_dev.py`) filters this; the AoU driver `compute_region_ld` consumes `region_row["region_id"|"chr"|"start_grch38"|"end_grch38"|"radius_bp"|"region_class"]`; the `.npz`/`.bm` naming is keyed on `region_id` everywhere (driver line 2326 `{out_bucket}/bm/{rid}.bm`, sidecars `{rid}.variant_ids.tsv`).

**The boundary question — bp window vs variant-count pass:** the locked target is "≤75k variants per sub-region." But the builder runs at NCSU **with no access to the cohort MT** (the variant set lives in the AoU perimeter). A true ≤75k-variant split would require an in-perimeter `count_rows()` pass over each xlarge region's filtered MT first. **Recommendation: do NOT require a live pre-pass.** Use a **bp-window heuristic** derived from the known AFR variant density, and let the driver's existing `MIN_VARIANTS_PER_REGION` skip + the `_assert_blockmatrix_written` read-back catch any sub-region that lands wildly off-target.

Density anchor `[VERIFIED: from the dev-10 data point]`: region_00006 is **17.7 Mb → 122,678 variants** at the MAF≥0.005 export band = **~6,930 var/Mb** (AFR). To stay ≤75k var: `75,000 / 6,930 ≈ 10.8 Mb` per sub-region. A **conservative 10 Mb bp window** yields ~69k var/sub-region at this density — safely under 75k, and (not coincidentally) matches the **Pan-UKBB 10 Mb radius** anchor. EUR is denser per Mb in common variants but the dominant cost axis is samples, not var-count; a 10 Mb window is a reasonable single heuristic for both. `[ASSUMED]` that density is roughly uniform across xlarge regions — gene deserts will be sparser (fewer var, fine) and HLA/6p21 denser (region_00145 — flag for the probe).

### Recommendation (planner-actionable)

**Encode the split at manifest-build time as additional sub-region rows, with parent provenance.** Concretely:

1. **New CLI param** `--max-subregion-span-mb` (default **10**) and `--split-classes xlarge` (so only xlarge splits; non-xlarge incl. region_00006 stay whole per the locked decision).
2. **Splitting logic** (sibling to `derive_region_class`): for an `xlarge` region spanning `[start38, end38]`, emit `N = ceil(span / max_span)` contiguous sub-windows of equal bp width. For each sub-window emit a manifest row with:
   - `region_id = f"{parent_id}__sub{k:02d}"` (e.g. `m2_region_00040__sub00` … `__sub06`). Keeps the existing `region_id`-keyed `.npz`/`.bm`/sidecar naming working unchanged — the driver, idempotency guard, and egress all treat a sub-region exactly like a region.
   - **New provenance columns** `parent_region_id` (= `m2_region_00040`), `subregion_index` (k), `n_subregions` (N), `subregion_start_grch38`, `subregion_end_grch38`. The parent's full `[start,end]` stays available via `parent_region_id` lookup for the stitch (Q-RS4).
   - `radius_bp` recomputed for the **sub-window** (`min(sub_span + 500kb, 50Mb)`); since sub_span ≤ ~10 Mb, radius ≈ sub_span — each sub-region is now a normal/medium region, NOT xlarge.
   - `region_class` re-derived on the sub-span → `small`/`medium` → routes to A.1/A.2 (or A.3 only if span still >25 Mb, which it won't at 10 Mb). **This is the structural win: post-split there are no A.3-dense-scratch sub-regions.**
3. **Parent row handling:** do NOT emit a compute row for the parent xlarge region itself (it is replaced by its sub-rows). DO emit the parent into the projection TSV (with `n_subregions`) so the cost model and the stitch know the parent→children mapping. Add a `split_status ∈ {whole, parent, subregion}` column to the projection.
4. **Dev-subset consistency:** the dev manifest currently names `m2_region_00040` (an xlarge) in both AFR and EUR. After the split that ID no longer exists as a compute row. Update `select_ld_regions_dev.py` to expand a selected xlarge parent into its sub-rows (so the dev fire exercises at least one sub-region — the probe needs exactly this).
5. **Downstream `region_id` parsing contract:** the `__sub{k}` suffix is the single load-bearing naming convention. Document it once; the stitch (Q-RS4) and any region-anchored novelty mapping must parse `parent_region_id` from the manifest column, NOT by string-splitting the suffix (string-splitting works but the column is the contract).

### Testability (existing pytest scaffolds)

The existing `tests/m3/test_build_ld_region_manifest.py` + the synthetic-MT fixture cover this without any live access — all NCSU-side, pure pandas/pyliftover:
- `test_xlarge_region_splits_into_subregions` — feed a synthetic 90 Mb xlarge BED row, assert N = ceil(90/10) = 9 sub-rows, contiguous non-overlapping windows covering `[start,end]`, each `region_class ≠ xlarge`.
- `test_nonxlarge_region_stays_whole` — region_00006-scale (17.7 Mb, large) emits ONE row, no `__sub` suffix (locks the "only xlarge splits" decision).
- `test_subregion_provenance_columns` — `parent_region_id`, `subregion_index`, `n_subregions` present and consistent.
- `test_subregion_radius_is_subspan_not_parent` — radius recomputed on sub-span.
- `test_subregion_ids_are_npz_safe` — `__sub00` round-trips through `_save_npz`/`_existing_region_npz` naming (the idempotency key).

### Live-only flags
- ⚠️ The 10 Mb→~69k-var mapping assumes region_00006's AFR density generalizes. **HLA/6p21 (region_00145) is denser** — its sub-regions may exceed 75k var. The probe should fire one region_00145 sub-region to confirm; if it overshoots, the planner can set `--max-subregion-span-mb 7` for chr6 specifically (or accept a slightly larger HLA sub-region — still ≪ the 615k-var parent).
- ⚠️ A true variant-count split would need an in-perimeter pre-pass; the bp heuristic deliberately avoids that. Tradeoff: sub-region var-counts will vary ±20% around target. Acceptable — the goal is "tractable," not "exactly 75k."

---

## Q-RS4 — Banded block-diagonal stitching in `ld_npz_to_rds.R`

> ⚠️ **SUPERSEDED by m3-REVIEWS.md HIGH#1 (2026-06-18):** the stitch is **OVERLAPPING-WINDOW BANDED** (cross-boundary pairs within `buffer_bp` RETAINED), **NOT** block-diagonal / `Matrix::bdiag`. The binding stitch spec is **m3-02b Task 2 + m3-REVIEWS HIGH#1**. The block-diagonal description below is retained ONLY as the rejected design — do not implement it.


### Findings (from reading the actual R script + the rescope)

The current `ld_npz_to_rds.R` converts ONE `.npz`/`.bm`-derived matrix → ONE `.rds` (symmetry recovery via `(M + t(M))/2`, GRCh38→37 liftover of variant IDs, drop unmappable, set dimnames, save `list(ld, snp_ids, provenance)`). It has **no notion of sub-regions** — it is 1 npz → 1 rds. After the split, an xlarge parent produces N sub-region `.npz` files that must reassemble into the **single** per-parent `.rds` that `finemap.smk`'s `ld_panel:` resolver expects (the resolver keys on `region_id = m2_region_00040`, not on `__sub00`).

**The rescope's treatment (locked, WAVE-2 HIGH-3):** drop cross-sub-region LD beyond the 50 Mb radius — "it's ≈0, already the accepted treatment." So the reassembly is a **block-DIAGONAL stitch**: intra-sub-region blocks populated with the computed Pearson r; cross-sub-region off-diagonal entries = 0. This is *exactly* the banding the whole pipeline already does — the A.3 path already zeroes pairs beyond `radius_bp`, and `compute_region_ld`'s comment (lines 2205–2213) documents that xlarge LD is "50-Mb-banded" and "downstream must treat as banded." Splitting just makes the band-zeroing happen at the sub-region boundary instead of via `sparsify_row_intervals`.

**Variant-ID ordering contract (the load-bearing invariant):** the stitched matrix's row/column order MUST be the **genomic concatenation of the sub-regions in ascending `subregion_index` order**, and within each sub-region the variant order is whatever that sub-region's `.npz` `variant_ids` vector carries (which the driver guarantees aligns to the BlockMatrix row order — `aou_ld_panel.py` lines 2264–2275 assert `len(variant_ids) == n_var` from the same single `aggregate_rows` pass). Because sub-windows are contiguous and non-overlapping in bp, concatenating them in index order yields a **globally position-sorted** variant list — the same order a whole-region build would have produced. SuSiE-RSS requires the LD matrix row order to match the z-score vector's variant order; the finemap consumer aligns by `snp_ids` dimnames, so as long as the stitched `snp_ids` are correct and the `ld` rows/cols are in the same order, alignment holds. `[VERIFIED: against ld_npz_to_rds.R dimnames contract + compute_region_ld row-alignment asserts]`

**SuSiE-RSS / coloc tolerance of block-diagonal LD `[VERIFIED via Track A precedent + CITED susieR]`:** a block-diagonal (banded) LD matrix is valid input. The off-diagonal zeros encode "these distant variants are in linkage equilibrium" — a true statement at >50 Mb. The existing `ld_reference.smk` already ships a `ukbb_ld_tiled_block_diagonal` source for HLA_6p21 (m3-RESEARCH Q2 mitigation 4 cites it), so block-diagonal LD is already in the consumer's diet. The one concern is **PSD**: a block-diagonal matrix is PSD iff every diagonal block is PSD. Each sub-region block is a Pearson correlation matrix → PSD by construction (up to float32 noise). The off-diagonal zeros do not break PSD (block-diag of PSD blocks is PSD). The existing `(M + t(M))/2` symmetrization + Track A's PSD-regularization precedent (memory: Track A SH2B3 anchor survives PSD-regularized LD) handle residual float drift. `[CITED: susieR/coloc accept banded/regularized LD; project Track A precedent]`

### Recommendation (planner-actionable)

Add a **stitch step** that runs BEFORE (or as a mode of) `ld_npz_to_rds.R`:

1. **New script or mode** `stitch_subregions_to_rds.R` (or `ld_npz_to_rds.R --stitch parent_id sub00.npz sub01.npz …`). Inputs: the N sub-region `.npz` files for one parent + the chain. Output: one `{parent_id}.rds`.
2. **Assembly:** for each sub-region, run the existing per-npz pipeline (symmetry recovery, chr-strip, GRCh38→37 liftover, drop unmappable, dimnames) to get a `(n_k × n_k)` block + its `snp_ids_k`. Then build a **sparse block-diagonal** matrix `Matrix::bdiag(block_0, …, block_{N-1})` (the script already imports `Matrix`), set global `dimnames = c(snp_ids_0, …, snp_ids_{N-1})` in ascending `subregion_index` order, and save in the same `list(ld, snp_ids, provenance)` schema.
   - Use `Matrix::bdiag` (sparse) for the assembly to avoid materializing the full dense `(Σn_k)²` matrix in R — for a 615k-var parent the dense form is ~1.5 TB and would OOM the NCSU node. **The stitched `.rds` should stay sparse (`dgCMatrix`/banded), not dense.** Confirm the finemap consumer accepts a sparse `Matrix` (Track A `.rds` files are dense for small regions; verify the SuSiE-RSS wrapper coerces or accepts sparse — **flag as a Wave-0 verify** since it changes the `.rds` payload type for xlarge parents).
3. **Provenance:** extend the provenance list with `subregion_npz_paths` (the N inputs), `n_subregions`, `parent_region_id`, `cross_subregion_ld = "zeroed (block-diagonal; >50Mb LD treated as 0 per WAVE-2 HIGH-3)"` so any reviewer can audit that the off-diagonal zeros are a deliberate banding choice, not missing data.
4. **Ordering enforcement:** sort sub-region inputs by `subregion_index` (parse from the manifest column, not the filename) before `bdiag`. Add an assertion that the concatenated `snp_ids` are monotonic in genomic position (catches a mis-ordered stitch).
5. **PSD:** apply the same Track A PSD-regularization that the project already uses, per diagonal block (or rely on each block being a correlation matrix). Do NOT regularize across the zeroed off-diagonal (that would re-introduce spurious cross-block LD).

### Testability
- `test_stitch_block_diagonal_psd` — two synthetic sub-blocks → `bdiag` → assert symmetric, PSD (all eigenvalues ≥ −1e-6), off-diagonal cross-block entries == 0.
- `test_stitch_snp_id_ordering` — concatenated dimnames are position-sorted; mis-ordered input raises.
- `test_stitch_sparse_payload` — xlarge parent `.rds` `ld` is a sparse `Matrix`, round-trips, and the finemap resolver loads it.
- `test_whole_region_unchanged` — a non-split region still produces a dense `.rds` byte-identical to the current path (no regression).

### Live-only flags
- ⚠️ Whether the SuSiE-RSS / coloc wrapper in `finemap.smk` accepts a **sparse `Matrix`** `ld` payload (vs requiring base `matrix`) is **confirmable on NCSU** (not in-perimeter) — make it a Wave-0 verify task. If it requires dense, the xlarge `.rds` will be huge; the fallback is to keep the sparse banded form and densify lazily inside the SuSiE wrapper per-credible-set.

---

## Q-RS5 — Cost-probe methodology (re-derive the 322-cell budget)

### Findings

The stale model (`build_ld_region_manifest.py` lines 348–357 + D-M3-09): A.1=0.5h, A.2=1.5h, large-A.3=8h, xlarge-A.3=24h per ancestry → 558.5 cluster-h/ancestry, ~1,117 total. **Every number predates the sample-count discovery and is low** (it was implicitly sized near the 2,000-sample repro regime; real blocks are 36–110× heavier). After the split, the "xlarge=24h" rows vanish (replaced by ~7 medium sub-rows each) — so the model must be rebuilt bottom-up from **measured real-cohort blocks/min**.

### The minimal defensible probe

**Two cells, both AFR, on the sized cluster** (the cheapest representative pair):
1. **One normal/medium WHOLE region** — `region_00006` (the rescope names it: cheapest A.3 region, 122,678 var, 17.7 Mb; it stays WHOLE per the locked decision and is the single best-characterized region from the dev-10 attempt — direct before/after comparability). Captures the throughput of the dominant region class.
2. **One xlarge SUB-REGION** — one `m2_region_00040__sub00` (a ~10 Mb / ~69k-var sub-region of the 615k-var parent). Captures the post-split sub-region throughput and proves the split actually makes the worst region tractable.

Optionally a **third cell: one EUR sub-region** of the same parent, to measure the EUR/AFR factor empirically rather than assuming exactly 3.01× (sample-ratio predicts 3.01×, but spill/parallelism may inflate it). If credits are tight, skip it and use the 3.01× sample-ratio multiplier with a stated ±20% band.

### Exact metric to capture

For each probe cell, record from the Spark UI / driver log:
- **`blocks_per_min`** = (Stage-4 total blocks) / (Stage-4 wall-minutes). This is the portable unit (independent of region size — a region's cost = its block count / blocks_per_min).
- **block count** for the region (Hail reports it; for an `n_var`-row region with default 4096 block_size and radius band, blocks ≈ banded-block-count).
- **peak executor memory + any spill** (confirms cores=2 / memory config from Q-RS2; spill ⇒ drop to cores=1).
- **wall-clock + cluster vCPU** → cluster-hours = wall_h × (vCPU/16 worker-equivalent) — but report **cluster-hours directly** (wall_h × n_workers) since that is what bills.
- Tag each by **(ancestry, region_class)**.

### Extrapolation (clean)

1. Compute `blocks_per_min` for AFR-medium (region_00006) and AFR-subregion.
2. **Per-region cluster-h = region_block_count / blocks_per_min / 60 × (probe wall→cluster-h factor).** Apply the matching class rate to every region in the manifest (post-split: only small/medium/sub-region classes remain).
3. **AFR→EUR:** multiply EUR cells by the measured factor (or 3.01× ± 20% if not measured).
4. **xlarge parent aggregate cost = Σ over its N sub-regions** (each priced at the sub-region rate). A 615k-var parent → ~9 sub-regions × (sub-region cost) — replaces the single fictional "24h" with a measured ~9× sub-region figure (likely *higher* total compute than the old 24h, but **tractable** — no single cell weeks-long, no master crash, fully parallelizable).
5. Sum all 322 cells (AFR + EUR, whole + sub-regions) → the new production budget. Convert cluster-h → AoU credit-$ at the n2-highmem-16 rate (~$0.95–1.10/hr/worker `[ASSUMED — confirm current AoU/GCP n2-highmem-16 on-demand price]`; 24 workers ≈ $23–26/hr).

### Go / no-go threshold structure

Gate the full fire on the measured number, not the model:
- **GREEN — fire the full 322:** projected total ≤ Carter's approved credit cap (GATE-1 budget) with ≥30% headroom. Proceed.
- **YELLOW — narrow the radius first:** projected total over cap but the **export radius is the lever** — drop the export band from `span+500kb`/50Mb toward the **Pan-UKBB 10 Mb** (Q-RS2 finding). For sub-regions already ≤10 Mb this is a no-op; for any remaining wide bands it cuts block-count. Re-probe one cell at the narrower radius, re-extrapolate. (This is also where retired-ordering-B would re-acquire value — out of scope, flag only.)
- **YELLOW — split finer:** if a *specific* class (e.g. EUR sub-regions, or HLA) is the cost driver, set `--max-subregion-span-mb` lower for that class and re-probe.
- **RED — re-negotiate budget / phase the fire:** if even at 10 Mb radius + finer split the total exceeds cap, escalate to Carter (per D-M3-03 the fire is single-batch, but the cost gate can force a phased AFR-first / chr-batched fire as a fallback).

Concretely: define `BUDGET_CAP_CLUSTER_H` (from GATE-1) and `PROJECTED = Σ cells`. Fire iff `PROJECTED × 1.3 ≤ BUDGET_CAP_CLUSTER_H`. Record the probe's blocks/min table in a `m3-W2-cost-probe.tsv` so the projection is auditable (mirrors the existing `m3-region-class-projection.tsv`).

### Live-only flags
- ⚠️ `blocks_per_min` at real sample counts is **only measurable in-perimeter** on the sized cluster — this is the entire point of the probe.
- ⚠️ The EUR/AFR factor *should* be 3.01× by sample ratio but spill behavior can inflate it; measure if credits allow.
- ⚠️ Current n2-highmem-16 AoU/GCP hourly price needs confirming for the credit-$ conversion.

---

## Validation Architecture delta

The split touches the 4-check protocol (`m3-RESEARCH.md` Validation Architecture) in exactly two places; the other checks are unchanged:

- **Check 1 (known-locus LD pattern) + Check 3 (SuSiE-RSS convergence):** for any region that was xlarge and is now split, these checks run on the **stitched `.rds`** (block-diagonal), not on a single matrix. Add a sub-check: assert the stitched matrix's diagonal blocks are dense-populated and the off-diagonal cross-block region is exactly zero (the band is where it should be). The lead variant for Check 1 / Check 3 lives inside one sub-region's block — confirm the credible set does not straddle a sub-region boundary (if it does, that is a real loss of cross-boundary LD and must be noted in the validation memo — but per WAVE-2 HIGH-3 the >50 Mb cross-LD is ≈0, so a credible set spanning >50 Mb is not expected).
- **Check 4 (A/B identity-placeholder yield):** unchanged in logic, but the dev-10 manifest must include at least **one xlarge sub-region** (per Q-RS3 rec 4) so the split path is validated before the production fire. The probe (Q-RS5) cell #2 doubles as this validation input.

New Wave-0 test gaps (all NCSU-side, no live access): the `test_xlarge_region_splits_*` and `test_stitch_block_diagonal_*` families above. Framework, config, and sampling-rate from the base `m3-RESEARCH.md` Validation Architecture are unchanged.

---

## Assumptions Log (items needing confirmation before they become locked decisions)

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | AoU quota request path is an AoU/Verily ticket (not self-serve Console), region us-central1 | Q-RS1 | Carter files via the wrong channel → lead-time slip |
| A2 | Grantable N2_CPUS ceiling for this controlled-tier workspace is ≥384 | Q-RS1 | Cluster sized below target; wall-clock longer (not a correctness gate) |
| A3 | `cores=2` + ~24g executor is safe for EUR (220k) on n2-highmem-16 | Q-RS2 | EUR spills; drop to cores=1 (probe catches this) |
| A4 | region_00006's ~6,930 var/Mb AFR density generalizes to other xlarge regions | Q-RS3 | HLA sub-regions exceed 75k var; set finer split for chr6 |
| A5 | 10 Mb bp window is the right default sub-region size | Q-RS3 | Sub-regions over/under target; tune `--max-subregion-span-mb` |
| A6 | finemap.smk SuSiE-RSS wrapper accepts a sparse `Matrix` `ld` payload | Q-RS4 | Xlarge `.rds` must densify; large files (NCSU-verifiable) |
| A7 | EUR/AFR per-block cost ≈ 3.01× (sample ratio) | Q-RS2/5 | Probe the EUR cell to measure instead of assume |
| A8 | n2-highmem-16 ≈ $0.95–1.10/hr/worker for the credit-$ conversion | Q-RS5 | Budget projection off; confirm current price |

**All other claims in this addendum are VERIFIED (arithmetic / source-read) or CITED (public docs).**

---

## Sources

### Primary (HIGH confidence)
- `src/python/build_ld_region_manifest.py`, `src/python/aou_ld_panel.py` (compute_region_ld / _route_region_path / _write_a3_banded_correlation_bm / _assert_blockmatrix_written), `src/scripts/ld_npz_to_rds.R` — read in full; the split/stitch design is grounded in the actual code contracts.
- Linear-algebra first principles for `Z @ Z.T` inner-dimension scaling (36×/110×/3.01× all verified arithmetic against AFR 73,122 / EUR 220,098 / repro 2,000).
- Hail BlockMatrix default block_size = 4096; row_correlation standardize-then-Gram semantics.

### Secondary (MEDIUM / CITED)
- Pan-UKBB LD release blog (pan.ukbb.broadinstitute.org/blog/2020/10/29/ld-release) — 10 Mb radius, 500× n1-standard-8, ~16h, ~64,000 CPU-h, 43.3 TB (AFR 12.0 TB). The single best biobank-scale anchor.
- cloud.google.com/dataproc/quotas + cloud.google.com/dataproc supported-machine-types — N2 family quota model, n2-highmem-16 Dataproc availability.
- community.ukbiobank Hail GWAS thread — 7.5 GB/vCPU memory sweet spot for BlockMatrix shuffles.
- AoU RW2.0 / CDRv8 controlled-tier release notes (support.researchallofus.org) — workspace migration context, us-central1.

### Project-internal (authoritative)
- `WAVE-2-RESCOPE-real-cohort-compute.md`, `.continue-here.md`, `STATE.md`, `m3-CONTEXT.md` (D-M3-01..10), `m3-RESEARCH.md` (base), `DRAFT-orderingB-band-before-checkpoint.md` (retired), `aou-ld-pipeline` SKILL.md.
- Memories: `feedback_size_cost_experiments_on_real_data_dimensions`, `feedback_aou_dataproc_pyspark_submit_args`, `feedback_aou_cluster_sizing_for_ld_panel`, `feedback_aou_success_marker_not_evidence_of_data`, `reference_aou_rw2_mirror_vpcsc`.

### Live-only (NOT confirmable from NCSU / public)
- AoU quota request channel + grantable ceiling (Q-RS1) — in-perimeter / AoU support only.
- Real-cohort `blocks_per_min`, spill behavior, EUR/AFR measured factor (Q-RS2/5) — the cost probe itself.
- Workspace region confirmation, current n2-highmem-16 price (env panel / billing).

---

## RESEARCH COMPLETE

The re-scope is implementable from this addendum + the base `m3-RESEARCH.md`. The load-bearing findings: (1) the 36×/110× claim is dimensionally exact (sample count is the matmul inner dim); (2) the split is best encoded as `__sub{k}` provenance rows with a 10 Mb bp-window heuristic (no live pre-pass needed) — matching the Pan-UKBB radius anchor; (3) ⚠️ **SUPERSEDED by m3-REVIEWS.md HIGH#1 (2026-06-18) — see Q-RS4 banner:** the stitch is an **OVERLAPPING-WINDOW BANDED** assembly (cross-boundary pairs within `buffer_bp` RETAINED), **NOT** a `Matrix::bdiag` block-diagonal — the block-diagonal phrasing below is the rejected design; the binding spec is m3-02b Task 2 + m3-REVIEWS HIGH#1; (4) the cost probe is two AFR cells (whole region_00006 + one xlarge sub-region) measuring `blocks_per_min`, gated on `PROJECTED × 1.3 ≤ BUDGET_CAP`. The only items that MUST be resolved live before/during the re-fire are the AoU N2 quota grant (longest lead — file first) and the probe measurements; everything code-side (split, stitch, tests, executor config) is NCSU-implementable now.
