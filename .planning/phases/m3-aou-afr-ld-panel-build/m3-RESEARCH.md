# Phase M3: AoU AFR LD panel build — Research

**Researched:** 2026-04-27
**Phase:** M3 (`m3-aou-afr-ld-panel-build`)
**Status:** research-complete
**Domain:** All of Us Researcher Workbench (Terra / Dataproc / Hail v0.2.x) summary-only LD-matrix construction; NCSU `.npz → .rds` ingest; Snakemake `ld_panel:` resolver; 4-check validation
**Confidence:** HIGH on Hail v0.2.x API surface and AoU env-var paths (verified live); HIGH on M2 region-span structural finding (verified by direct grep of `union_region_list.bed`); MEDIUM on AoU export-classification policy mechanics (R1 risk; ultimately a written ruling from AoU support, not a research artifact); MEDIUM on cohort-size projections for v7 vs v8 (cited from AoU release notes language, not enumerated against current CDR).

---

## Summary

M3 builds per-region LD matrices for AFR + EUR ancestries inside the AoU Researcher Workbench from controlled-tier WGS, exports summary-only `.npz` artifacts to NCSU GPFS, converts to `.rds`, and integrates them into the Snakemake fine-mapping DAG. This RESEARCH.md (a) verifies Hail v0.2.x API signatures against live docs, (b) answers the 12 open questions from `m3-CONTEXT.md` with concrete recommended values, (c) surfaces a single material structural finding the spec did NOT anticipate — **M2 union regions are not 1-2 Mb; they are median 9 Mb and reach 102 Mb (chromosome-spanning), which invalidates the spec's `radius=2_500_000` setting on 92% of regions and forces a region-bounded `radius` design** — and (d) formalizes the 4-check validation protocol with measurable pass thresholds for `m3-VALIDATION.md`. Wave-by-wave findings are anchored to concrete file paths so the planner can break the work into atomic plans with no further investigation. The hard human-action gates (workspace creation → DUS/RPS/billing/P&P → egress classification in writing) are flagged as planner pre-conditions, not plan tasks.

**Primary recommendation:** Adopt CONTEXT.md's locked decisions D-M3-01 through D-M3-08 as-is, but require Wave 0 to (i) compute `radius` per region as `region_span_bp + safety_margin` rather than the spec's static 2.5 Mb, and (ii) explicitly resolve the `radius` decision against the M2 union BED span distribution before any AoU compute fires.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-M3-01 — EUR parity panel built inside AoU Workbench** (parallel to AFR), not on NCSU GPFS. AoU EUR `ancestry_pred == 'eur'` (~130-150k post-QC); 1000G EUR Phase 3 plinkfiles at `data/reference/ldsc/1000G_EUR_Phase3_plink/` serve as Check 2 comparator only. Output lands at `data/processed/ld_reference/EUR_aou/{region_id}.rds`. ROADMAP wording will be updated by M3 Wave 0.
- **D-M3-01.1 — UKB EUR augmentation deferred** (out of M3 scope). UKB DUA timing is not on the M3 → M4 critical path.
- **D-M3-02 — All 161 regions × both ancestries — 322 cells in production scope.** Region manifest `config/ld_regions.tsv` enumerates 322 rows.
- **D-M3-03 — Production fire = single batch (Dev-10 → Production-322 single fire)** after the 4-check validation memo + Carter signoff. Per-chromosome export bundling = 44 entries (22 chr × 2 ancestries).
- **D-M3-04 — Dev region selection — spec default** (3 EUR-comparable + 5 AFR-known + 2 HLA-stress).
- **D-M3-05 — M2 supersede triggering — separate M2-supplementary phase, not M3 close-out.** All 8 M2-POST-M3-* obligations stay open at M3 close; M2-supplementary phase consumes M3 outputs (slug `m2-supp-aou-afr-rerun`).
- **D-M3-06 — Local dev mirror** per AOU-LD-PIPELINE.md §2 P5 (`envs/m3-aou-dev.yml` + synthetic MT fixture under `tests/m3/fixtures/synthetic_mt/`).
- **D-M3-07 — Ancestry inclusion logic — PCA-primary** (`ancestry_pred == 'afr'`) with self-report sensitivity check at the 10-region dev subset. KING kinship ≥ 0.0442 (third-degree, conservative).
- **D-M3-08 — Validation-memo external review — OSF deposit as substitute** (post to existing osf.io/az52u amendment record; same form as M1's posting at osf.io/az52u/files/k8w7n).

### Claude's Discretion

The 12 open questions in CONTEXT.md `<open_questions>` are explicitly Claude's discretion — answered concretely in `## Answers to the 12 Open Questions` below. The planner consumes these answers directly.

### Deferred Ideas (OUT OF SCOPE)

- UKB EUR LD augmentation (D-M3-01.1; future supplementary phase if UKB lands by M5/M6)
- AoU AFR ld-score derivation for AFR-AFR LDSC (M2-POST-M3-05; M2-supplementary)
- TRANS mtCOJO 1000G AFR sensitivity check (M2-POST-M3-04; M2-supplementary)
- AFR LDSC matrix re-fire under AoU AFR ld-scores (M2-POST-M3-02; M2-supplementary)
- AFR PLINK clumping re-fire (M2-POST-M3-01; M2-supplementary)
- AFR mtCOJO re-fire (M2-POST-M3-03; M2-supplementary)
- GWAS Catalog v_lock_M5 refresh (M2-POST-M3-06; deferred to M5)
- MTAG `--fdr` LSF re-fire (M2-POST-M3-07; M2-supplementary)
- mtCOJO production sensitivity LSF re-fire (M2-POST-M3-08; M2-supplementary)
- AoU v8 re-run (watch-item, not scope)
- HIS LD panel (deferred, out of 9-trait inventory)
- AoU CAD/eGFR/SBP AFR sumstats derivations (M1-supplementary or M5)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-AOU-LD-EGRESS | AoU P&P + RPS + egress classification gates; per-region `.npz` summary-only export; local landing under `data/processed/ld_reference/{AFR_aou,EUR_aou}/`; conversion to `.rds` per AOU-LD-PIPELINE.md §8.2 | Verified env-var paths for AoU controlled-tier (`WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH`, `WORKSPACE_BUCKET`, `GOOGLE_PROJECT`); auxiliary path `gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/relatedness/relatedness_flagged_samples.tsv` confirmed; per-chromosome export bundle structure designed (Q12 below) |
| REQ-AOU-LD-VALIDATION | 4-check protocol passes on 10-region dev subset before scale-up | `## Validation Architecture` formalizes Checks 1-4 with measurable pass thresholds and Snakemake DAG-encodable gates |
| REQ-PUBLIC-DATA-ONLY | All M3 work uses AoU controlled-tier WGS (DUA-covered); no individual-level data leaves the workspace; OSF posting confirms public-summary-only artifacts | OSF amendment trail at osf.io/az52u inherited; egress audit log entry schema designed (Q12 below); no data inventory required |
| REQ-SNAKEMAKE-CI | M3 Snakemake rules (`m3_*.smk`) registered in main pipeline; toy_3locus extended with AFR identity-placeholder | Existing rule directory `src/snakemake/rules/` and `LD_BUILD_ENV` absolute-path conda pattern reused for `m3_ingest_aou_ld.smk` + `m3_convert_npz_rds.smk` + `m3_validation.smk` |
| REQ-PATH-PARAMETERIZATION | All AoU-side and NCSU-side path resolution goes through `config/pipeline.yaml` `ld_panel:` block | `resolve_ld_path(region_id, ancestry, config)` helper designed (Q7 below); existing `paths:` block layout and `ld_reference: "data/processed/ld_reference"` value extended with new `ld_panel:` selector |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

These directives bind the M3 plan and are non-negotiable:

- **100% public data.** AoU controlled-tier under standard academic DUA qualifies; OSF pre-registration discipline applies (REQ-OSF-PREREG).
- **Solo author.** Validation memo OSF deposit replaces external reviewer (D-M3-08).
- **Timeline is not a binding constraint.** Rigor over speed; do not compress the dev-10 → Carter-signoff → production gate to save days.
- **No web/JS stack.** Snakemake + Python (Hail/pyspark inside AoU; numpy/pandas + reticulate at NCSU) + R (`Matrix`, `reticulate` for `.npz → .rds`); bash for orchestration.
- **GPFS filesystem.** Mode `solo` with `git.isolation: branch`. **No worktree isolation.** All NCSU-side branches operate on the canonical working tree.
- **Snakemake 7.32.4 requires Python 3.11.** Never invoke snakemake from miniconda3 base (Python 3.13). Use `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` or rely on `--use-conda` env resolution. M3 envs (`m3-aou-dev.yml`, `m3-r-ld.yml`) MUST pin `python=3.11`.
- **LSF queue rules.** Use `standard` / `serial` / `long` queues; `bsub_wrapper.sh` sets `-W` to queue max (serial=5760 min, long=14400 min, standard=2880 min); `LSF_UNIT_FOR_LIMITS=GB`. NCSU-side `.npz → .rds` conversion fits in `serial` (per-region); `m3_validation.smk` 4-check pipeline fits in `standard`. Production AoU compute is NOT on LSF — it runs on Dataproc.
- **HPC PATH conventions.** `node` from `~/miniconda3/bin` (prepend PATH for GSD CLI). Not load-bearing for M3 plan tasks but applies to any GSD invocations.

---

## Hail v0.2.x API Verification (verified 2026-04-27 against live docs)

All four primary Hail entry points used by `src/python/aou_ld_panel.py` were verified against the canonical Hail v0.2 documentation page `hail.is/docs/0.2/methods/genetics.html` on 2026-04-27. The spec pseudocode in AOU-LD-PIPELINE.md §5.1 is API-correct except for the `radius` interpretation (see Q2 below).

### `hl.ld_matrix(entry_expr, locus_expr, radius, coord_expr=None, block_size=None) -> BlockMatrix`

| Property | Verified value | Implication for M3 |
|----------|---------------|---------------------|
| `entry_expr` type | Float64Expression (entry-indexed; typically `hl.GT.n_alt_alleles()` returning 0/1/2 dosage) | Spec pseudocode `hl.ld_matrix(mt_r.GT.n_alt_alleles(), mt_r.locus, ...)` is correct |
| `locus_expr` type | LocusExpression (row-indexed; must align with entry_expr source) | Correct in spec |
| `radius` units | Base pairs (when `coord_expr=None`); inclusive upper bound on locus-position distance | **Spec sets `radius=2_500_000` assuming ~2 Mb regions; ≈ 92 % of M2 regions exceed this — see Q2 below** |
| `coord_expr` | Optional Float64Expression (ascending per contig); defaults to locus position | Not used; we want bp distance |
| `block_size` | Optional int; default = `BlockMatrix.default_block_size()` (typically 4096) | Tunable for OOM avoidance — see Q5 below |
| Return | Symmetric `BlockMatrix` shape (n_variants × n_variants); diagonal=1.0; off-diag = Pearson r within radius on same contig; **0.0 outside radius** | This is the right LD for SuSiE-RSS (Pearson r on dosages, not r²) |
| Handling of constant rows | Constant-value rows → NaN in correlation; **must filter zero-variance variants beforehand** | Variant QC `vqc.AF[1] >= 0.005 AND vqc.AF[1] <= 0.995` already handles this — verify post-`split_multi_hts` |

**Critical clarification on `radius`:** `hl.ld_matrix` does NOT compute LD only between variants within the supplied region. It builds an n_variants × n_variants BlockMatrix where pairs with locus distance > `radius` get value 0.0. So if a region is 30 Mb wide and `radius=2_500_000`, the resulting matrix has true LD only on a 2.5 Mb-banded diagonal — long-range LD entries are forced to 0.0 (spurious). This is acceptable when the region IS ≤ 2 Mb (the spec's mental model), but it's wrong when regions are 30+ Mb and SuSiE-RSS will see structurally-zero off-diagonal blocks. **Fix: set `radius = (end_bp − start_bp) + safety_margin_bp` per region** so the entire region is "inside the band."

### `hl.sample_qc(mt, name='sample_qc') -> MatrixTable`

| Property | Verified value | Implication |
|----------|---------------|-------------|
| Output struct fields | `call_rate` (float64), `n_called`, `n_not_called`, `n_filtered`, `n_hom_ref`, `n_het`, `n_hom_var`, `dp_stats`, `gq_stats`, `r_ti_tv`, `r_het_hom_var` | Spec pseudocode uses `mt_afr.sqc.call_rate >= 0.98` — verified field name |
| `name=` kwarg | Supported; default `'sample_qc'` | Spec uses `name="sqc"` — fine, no API conflict |
| Heterozygosity ±3 SD filter | NOT a built-in field; must compute as `hl.agg.stats(mt.sqc.r_het_hom_var)` then `mean ± 3*stdev` | Spec § 3.1 mentions this filter — must be implemented in driver code, not a one-liner |

### `hl.variant_qc(mt, name='variant_qc') -> MatrixTable`

| Property | Verified value | Implication |
|----------|---------------|-------------|
| Output struct fields | `AF` (array<float64>; index 1 = alt allele freq for biallelic post-split), `call_rate`, `p_value_hwe`, `n_het`, `n_hom_var`, `n_called`, `n_not_called`, `dp_stats`, `gq_stats` | Spec pseudocode uses `vqc.AF[1] >= 0.005`, `vqc.call_rate >= 0.95`, `vqc.p_value_hwe >= 1e-6` — all correct |
| `name=` kwarg | Supported; default `'variant_qc'` | Spec uses `name="vqc"` — fine |
| HWE p-value definition | Computed across all included samples post-`split_multi_hts`; computed within ancestry-restricted MT (matches D-M3-07's "AFR-only HWE filter") | Correct application of within-AFR HWE per spec §4 |

### `hl.split_multi_hts(ds, keep_star=False, left_aligned=False, vep_root='vep', permit_shuffle=False) -> MatrixTable`

| Property | Verified value | Implication |
|----------|---------------|-------------|
| Behavior | Decomposes multiallelic sites into biallelic rows; updates GATK GT/AD/DP/GQ/PL fields appropriately; left-normalizes alleles | Spec calls this AFTER variant QC — correct ordering: split first to ensure HWE/AF computed on biallelic site, OR split LAST and re-compute QC. **Recommended:** split before computing variant QC; see Q-driver below |
| Difference from `hl.split_multi` | `_hts` updates GATK fields; plain `split_multi` does not | AoU MT carries GATK fields → use `_hts` |
| Indel handling | Small indels (<50 bp typical) are decomposed; SVs (≥50 bp) should be filtered prior | Spec §4 already excludes SVs |
| `keep_star=False` default | Drops `*` (spanning deletion) alleles | Correct; SuSiE-RSS doesn't model `*` cleanly |

### Recommended `aou_ld_panel.py` ordering (corrected against spec §5.1)

The spec pseudocode runs `variant_qc` BEFORE `split_multi_hts`. This is technically permitted but produces AF/HWE on multiallelic loci that then split into multiple biallelic rows where the per-row AF is **not** what was filtered. Recommended canonical ordering:

```
1. mt = hl.read_matrix_table(WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH)   # AoU env var
2. mt = mt.filter_cols(mt.s in ancestry_afr)                       # PCA cohort
3. mt = mt.anti_join_cols(related_samples_ht)                      # KING ≥ 0.0442
4. mt = hl.split_multi_hts(mt)                                     # split FIRST
5. mt = hl.sample_qc(mt, name='sqc'); filter call_rate ≥ 0.98
6. mt = hl.variant_qc(mt, name='vqc'); filter MAF/HWE/call_rate
7. mt = mt.filter_rows(hl.len(mt.filters) == 0)                    # AoU-flagged drop
8. mt = mt.checkpoint("gs://fc-secure-<workspace-id>/ld/mt_afr_qc.mt")
9. for region in regions: ld = hl.ld_matrix(mt.GT.n_alt_alleles(), mt.locus, radius=region_span+margin)
```

This ordering is documented in `## Wave 1 Findings` below.

---

## Answers to the 12 Open Questions

### Q1 — Region BED coordinate system (GRCh37 → GRCh38 liftover)

**Recommendation:** **Liftover at the Wave 0 reformatter step (one-shot).** Emit `config/ld_regions.tsv` with `start_grch38` / `end_grch38` columns already in GRCh38 native coordinates. The AoU-side driver stays pure: it reads the manifest and feeds GRCh38 intervals directly to `hl.parse_locus_interval(...,reference_genome="GRCh38")`.

**Rationale:** AoU's MatrixTable is GRCh38-native (verified via Hail v0.2 default reference setting in the spec pseudocode `hl.init(default_reference="GRCh38", ...)` at AOU-LD-PIPELINE.md §5.1 line 122). Project's canonical analytic plane is GRCh37 (DEC-2026-04-24-01); the existing UCSC chain at `data/external/liftover/hg38ToHg19.over.chain.gz` is bidirectional. Liftover at the reformatter is a one-shot, version-controlled operation; liftover inside the AoU driver pollutes pure-Hail logic with NCSU file dependencies and adds a non-obvious failure mode.

**How:** Wave 0 task `build_ld_region_manifest.py` accepts `results/regions/union_region_list.bed` (GRCh37) + `data/external/liftover/hg37ToHg38.over.chain.gz` (need to add the reverse chain — verify it's already present alongside `hg38ToHg19`; if not, source from UCSC at the same access point), runs per-region liftover via `pyliftover` (Python; no R dependency), and emits `config/ld_regions.tsv` with both `start_grch37` / `end_grch37` (provenance) AND `start_grch38` / `end_grch38` (AoU-side input) columns. Variant ID liftover (the GRCh38 → GRCh37 direction) happens at NCSU-side `ld_npz_to_rds.R` per the existing chain, AFTER AoU export.

**Risk:** Liftover failures (regions whose flanks land in GRCh38 gaps, ALT contigs, or multi-segment hits) — handle by emitting a `liftover_status` column with values `{primary, multi-segment, failed}` and dropping `failed` rows from production with an audit log entry. M2 union regions are autosomal (chr1-22, no ALT) so multi-segment is the only realistic failure mode (rare for ±1 Mb windows, more common for the 100 Mb chromosome-spanning regions).

**Confidence:** HIGH — pyliftover is the standard tool; chain file is project-locked.

### Q2 — Hail `hl.ld_matrix` `radius` parameter — **STRUCTURAL FINDING**

**Recommendation:** **Override the spec's static `radius=2_500_000`. Compute `radius = (region_end_bp − region_start_bp) + 500_000` per region** (i.e., region span + 500 kb safety margin). Pass per-region.

**Rationale (the headline finding in this RESEARCH.md):** A direct measurement of `results/regions/union_region_list.bed` reveals that the M2 union regions are NOT "~1-2 Mb fine-mapping windows" as AOU-LD-PIPELINE.md §3 mental model assumed. The empirical span distribution is:

| Percentile | Region span |
|------------|-------------|
| Min | 2.0 Mb |
| P10 | 2.6 Mb |
| P25 | 4.5 Mb |
| **P50 (median)** | **9.0 Mb** |
| P75 | 21.7 Mb |
| P90 | 35.8 Mb |
| P95 | 46.4 Mb |
| P99 | 89.0 Mb |
| **Max** | **102.7 Mb** (chr6, region m2_region; effectively chromosome-spanning) |

Only **13 of 161 regions (8 %)** fit within the spec's `radius=2_500_000` band. The remaining **148 regions (92 %)** would have structurally-zeroed off-diagonal blocks if M3 used the spec's static value. This is because M2 union construction (`build_region_union.py` with `_LEAD_PRUNE_BP=2_500_000`, default bedtools merge with no `-d`) chains adjacent ±1 Mb lead windows into wide merged blocks where multiple lead variants and contributing methods cluster into single regions. This was a M2 design choice (D-M2-09) that the AoU spec was not informed by.

**Compute consequence:** Setting `radius` to the per-region span means the BlockMatrix LD computation now spans the full region (no banded-zero artifact), but compute and memory cost grow as O(n_var²) where `n_var ≈ region_span_Mb × variant_density_per_Mb_AFR`. For a 50 Mb region at AFR density (~10k common variants per Mb at MAF ≥ 0.01 post-QC), n_var ≈ 500k variants, giving an LD matrix with ≈ 2.5 × 10¹¹ entries. **This will OOM `to_numpy()` on any reasonable Dataproc driver.** Cost levers (in priority order):

1. **MAF tightening for export.** MAF ≥ 0.01 in AFR cuts variant density ~30 % (per spec §7.2); for a 50 Mb region this drops n_var from 500k to ~350k.
2. **Lower-triangular sparsified storage** via `BlockMatrix.sparsify_triangle()` then `BlockMatrix.write()` to bucket — DO NOT call `to_numpy()` on dense full matrices for regions ≥ 5 Mb.
3. **Per-region staged densification at export.** Dense `to_numpy()` happens only for regions ≤ 5 Mb. Larger regions are exported as upper-triangular `BlockMatrix` directories (Hail-native binary), then densified at NCSU-side ingest in `ld_npz_to_rds.R`.
4. **Region sub-tiling.** For regions ≥ 30 Mb, consider tiling into ≤ 10 Mb sub-regions and emitting block-diagonal LD (this is what the existing UKBB-LD HLA_6p21 rule does — `ld_source='ukbb_ld_tiled_block_diagonal'` per `src/snakemake/rules/ld_reference.smk` line 343). Trade-off: SuSiE-RSS sees only intra-tile LD; cross-tile credible-set linkage is lost. Defensible for chromosome-spanning regions but introduces methodological complexity.

**Open issue surfaced:** This finding may itself motivate revisiting M2's region-merging strategy. For example, if the planner decides 50 Mb regions are unfit for fine-mapping anyway, the M2 `build_region_union.py` may need a "max region width" parameter that splits oversize merges into ≤ 10 Mb tiles. **This decision is NOT a research output** — flagged as `Open issue O1` below for the planner / Carter to resolve.

**How (interim, M3 plan default):** Wave 0 reformatter emits `radius_bp` as a derived column in `config/ld_regions.tsv` per `radius_bp = (end_grch38 − start_grch38) + 500_000`. Wave 1 driver `compute_region_ld()` reads `radius_bp` per row and passes it to `hl.ld_matrix`. Wave 2 dev fire MUST exercise at least one ≥ 30 Mb region and verify Hail BlockMatrix write to bucket without OOM (the 2 HLA-stress slots in D-M3-04 cover this).

**Confidence:** HIGH on the structural finding (direct measurement); MEDIUM on the per-region radius mitigation (the export-time densification trade-off curve has not been empirically tested).

### Q3 — AoU bucket vs Workbench Jupyter export semantics

**Recommendation:** **Stage `.npz` files in the workspace bucket at `gs://fc-secure-<workspace-id>/ld/{ANCESTRY}_aou/{region_id}.npz`, then file egress requests against the bucket path via the AoU portal Notebooks/Files UI.** The `aou_workbench_client` Python export endpoint is documented for notebook outputs but its applicability to bucket-stored binary artifacts is not confirmed in current AoU support docs (cited in spec §7.1 with `**needs verification**`).

**Rationale:** The AoU egress UI documented at `support.researchallofus.org` Workbench → Notebooks/Files → Request export is the canonical path with the longest production track record. Requesting via the UI also produces the AoU-side review queue entry that anchors the egress audit log (Q12 below). Programmatic export is a v2 nice-to-have, not a blocker. Per-chromosome bundling means Carter files 22 + 22 = 44 export requests across the production run — manageable as a Wave 4 human-action task.

**How:** Carter (human action, Wave 4) opens the AoU portal per chromosome, navigates to `gs://fc-secure-<workspace-id>/ld/AFR_aou/` (and EUR_aou), selects the chr-specific subset, files an export request with the descriptive label `M3 LD chrN AFR_aou` (linking back to the OSF amendment record), receives an AoU-issued export request ID, and appends a row to `.planning/amendments/aou-egress-audit-log.md` per Q12 schema. AoU review SLA is documented at "typically 2-5 business days" for routine summary-statistics requests; credible window for 44 sequential requests is ~3-4 weeks if not parallelized.

**Confidence:** HIGH on the UI path; LOW on the programmatic path (treat as out of scope unless verified by Carter against AoU support before Wave 4).

### Q4 — Per-chromosome export bundle size estimate

**Recommendation:** **Bundle per chromosome × ancestry. Estimate per-bundle compressed size: 5-30 GB AFR; 8-60 GB EUR (denser).**

**Rationale:** Per-region size depends on n_var, which scales with region span and ancestry-specific MAF density. Empirical anchor from spec §7.2: a 2 Mb region with 20k variants at float32 lower-triangular = ~800 MB dense; ~250-300 MB compressed. Generalizing to M2's spans + per-chromosome region counts (computed from `union_region_list.bed`):

| Chr | n_regions | Sum span (Mb) | Estimated AFR bundle compressed (GB) | Estimated EUR bundle compressed (GB) |
|----|-----------|---------------|--------------------------------------|--------------------------------------|
| chr1 | 14 | 222 | 12-18 | 18-28 |
| chr2 | 14 | 233 | 13-19 | 20-30 |
| chr3 | 8 | 194 | 11-16 | 17-25 |
| chr4 | 11 | 187 | 10-15 | 16-24 |
| chr5 | 16 | 169 | 10-14 | 15-22 |
| chr6 | 5 | 167 | 11-17 (HLA dense) | 17-27 (HLA dense) |
| chr7 | 7 | 155 | 9-13 | 14-21 |
| chr8 | 6 | 143 | 8-12 | 13-19 |
| chr9 | 3 | 110 | 6-10 | 10-16 |
| chr10 | 10 | 131 | 8-12 | 12-19 |
| chr11 | 12 | 131 | 8-12 | 12-19 |
| chr12 | 6 | 130 | 7-11 | 11-17 |
| chr13-22 | 49 | 685 | 5-10 each | 8-16 each |
| **Total (44 bundles)** | **161** | **2456** | **~250-400 GB** | **~400-700 GB** |

(EUR is denser than AFR at any MAF threshold because of LD block structure and lower MAF cutoff retention.)

**Mitigations from spec §7.2 (already on the table):**
1. MAF ≥ 0.01 export threshold (vs 0.005 internal) → ~30 % size cut
2. Lower-triangular float32 NPZ → 50 % size cut from full square
3. Sparse `|r| < 0.01` zeroing → variable; not used because SuSiE-RSS needs full matrices
4. Per-chromosome rather than per-region bundling → reduces AoU review request count from 322 to 44

**AoU per-batch limit:** AoU's documented per-export-request size limit is not stated as a hard number in public docs; the practical constraint is reviewer time, not technical. Spec §7 implies "reasonable batch" without enumeration. **Recommendation:** if any bundle exceeds 50 GB compressed, split it within-chromosome by region count (e.g., chr1 AFR → chr1a_AFR (regions 1-7), chr1b_AFR (regions 8-14)). Wave 4 task includes a `validate_bundle_sizes.py` check before each request.

**Confidence:** MEDIUM — empirical sizes will only be known after Wave 2 dev-10 fire; pre-fire estimates use a 2× safety margin over spec §7.2 anchor.

### Q5 — Hail BlockMatrix `block_size` tuning + `to_numpy()` driver-memory limits

**Recommendation:** **Default `block_size = BlockMatrix.default_block_size()` (4096) for regions ≤ 10 Mb. For regions > 10 Mb, write to bucket as `BlockMatrix` directly (skip `to_numpy()` entirely); densify at NCSU-side `ld_npz_to_rds.R` which reads the BlockMatrix shards via `pyhail` or fallback to numpy reads of the per-block float files.**

**Rationale:** `to_numpy()` loads the entire dense n_var × n_var float32 matrix into Dataproc driver RAM. Approximate driver-memory budgets:

| Region span | n_var (AFR, MAF≥0.005) | Dense float32 (GB) | Driver RAM needed (GB; 2× working memory) | Fits on `n1-highmem-16` driver (104 GB)? |
|-------------|------------------------|--------------------|-------------------------------------------|------------------------------------------|
| 2 Mb | 20k | 1.6 | 3.2 | yes |
| 5 Mb | 50k | 10 | 20 | yes |
| 10 Mb | 100k | 40 | 80 | barely (< 25 % headroom) |
| 20 Mb | 200k | 160 | 320 | NO — `to_numpy()` will OOM driver |
| 50 Mb | 500k | 1000 | 2000 | NO |
| 100 Mb | 1M | 4000 | 8000 | NO |

Spec §11 recommends `n1-highmem-16` workers; driver is `n1-standard-8` per spec §11. Dataproc driver default is 8 vCPU + 30 GB RAM; even at `n1-highmem-32` driver (208 GB) only regions ≤ 10 Mb can be densified safely. **The spec's `to_numpy()` line in §5.1 is incorrect for the actual M2 region distribution** (consistent with the Q2 finding above).

**Fallback paths:**

1. **Path A.1 (regions ≤ 5 Mb):** `to_numpy()` direct → `np.savez_compressed` → upload to bucket. Spec §5.1 verbatim.
2. **Path A.2 (regions 5-10 Mb):** Sparsify lower triangle (`BlockMatrix.sparsify_triangle()`), `to_numpy()` (now n_var × n_var/2), savez_compressed.
3. **Path A.3 (regions > 10 Mb):** `BlockMatrix.write("gs://.../bm/{region}.bm", overwrite=True)` then download the sharded directory at NCSU-side. NCSU-side `ld_npz_to_rds.R` reads the BlockMatrix block-by-block (or invokes a `bm_to_npz.py` helper inside `envs/m3-aou-dev.yml` that reads the BM sharded directory and writes a single `.npz` for ingest — but this NPZ then approaches the driver-RAM limit AGAIN unless we accept it being lower-triangular sparsified). For these regions, a tile-based block-diagonal approach (Q2 mitigation 4) becomes more attractive.

**`block_size` tuning:** Hail default 4096 is well-tuned for genome-scale operations. Increasing block_size reduces per-block overhead but increases per-block memory. For OOM avoidance, the recommendation is **decrease** `block_size` to 1024 or 2048 on dense regions to push more parallelism into the workers. This is a Wave 2 dev-fire empirical tuning task — not a Wave 0 commit.

**How:** Wave 1 driver `compute_region_ld(region_row, mt_source)` accepts a `region_class` parameter (`small`/`medium`/`large` based on region span + n_var), with three code paths corresponding to A.1 / A.2 / A.3. Default thresholds: small ≤ 3 Mb, medium 3-10 Mb, large > 10 Mb. Region class is computed once at Wave 0 reformatter time and pinned in `config/ld_regions.tsv` as a `region_class` column.

**Confidence:** HIGH on the OOM math; MEDIUM on the A.3 path mechanics (BlockMatrix-to-NPZ shipping is plumbing-level engineering; the wave-2 dev fire will verify).

### Q6 — Local synthetic MT fixture for `envs/m3-aou-dev.yml` testing

**Recommendation:** **100 samples × 1500 variants × 2 chromosomes (chr16 + chr6 for HLA stress).** Schema: GATK HTS (GT, AD, DP, GQ, PL); variants seeded with 2-5 % multiallelic for `split_multi_hts` exercise; ~5 % of samples with simulated relatedness pairs for kinship-pruning exercise.

**Rationale:** Minimum viable schema must exercise every Hail call path in `aou_ld_panel.py`:
- `hl.read_matrix_table(...)` → satisfied by any `.mt` directory
- Cohort filter `mt.ancestry == 'afr'` → seed 60 samples with `ancestry='afr'` annotation, 30 with `'eur'`, 10 with `'oth'`
- Anti-join with `relateds` HT → seed 5 sample IDs into a separate HT
- `hl.sample_qc` → output struct schema verified
- `hl.variant_qc` → AF, call_rate, p_value_hwe verified
- `hl.split_multi_hts` → triggered by ~30 multiallelic variants
- `hl.filter_intervals` → triggered by 2-3 region intervals
- `hl.ld_matrix` → BlockMatrix on 100 samples × ~500 region-restricted variants

**Implementation:** Generate via Hail's `hl.balding_nichols_model(...)` with 3 populations (AFR/EUR/OTH proxy), 1500 variants on 2 chromosomes, then annotate samples with synthetic `ancestry` field. Save as `tests/m3/fixtures/synthetic_mt/synthetic_aou.mt` (gitignored — not committed; rebuilt on first test invocation by `tests/m3/fixtures/build_synthetic_mt.py`).

**Sample size:** 100 samples is small enough to run on a laptop in under 2 minutes but large enough that LD matrices have non-trivial structure (n=100 gives Pearson r SE ~0.1 — won't match production LD numerically but exercises every code path).

**Confidence:** HIGH — `hl.balding_nichols_model` is a well-documented Hail testing primitive.

### Q7 — `config/pipeline.yaml` `ld_panel:` resolver implementation

**Recommendation:** Add the following to `config/pipeline.yaml` (sibling to existing `finemap:` block at line 180):

```yaml
ld_panel:
  # Per-ancestry-token, an ordered fallback chain. M4 finemap.smk consults
  # config["ld_panel"][ancestry] and walks the list, returning the first
  # path that exists.
  EUR:
    - {source: "EUR_aou",   path: "data/processed/ld_reference/EUR_aou/{region_id}.rds"}
    - {source: "EUR_ukbb",  path: "data/processed/ld_reference/EUR_ukbb_ld/{region_safe}.rds"}
    - {source: "EUR_1kg",   path: "data/processed/ld_reference/EUR/{region_safe}.rds"}
  AFR:
    - {source: "AFR_aou",   path: "data/processed/ld_reference/AFR_aou/{region_id}.rds"}
    - {source: "AFR_hgdp",  path: "data/processed/ld_reference/AFR_hgdp_1kg/{region_safe}.rds"}
    - {source: "AFR_1kg",   path: "data/processed/ld_reference/AFR/{region_safe}.rds"}
  TRANS:
    - {source: "TRANS_aou_eur", path: "data/processed/ld_reference/EUR_aou/{region_id}.rds"}
    - {source: "EUR_1kg",       path: "data/processed/ld_reference/EUR/{region_safe}.rds"}
  # Strict mode: if true, missing AoU panel for a region is a hard error.
  # Default false: walk the fallback chain.
  strict_aou_only: false
  # Optional explicit override: pin a specific source for one ancestry.
  # Used by Track A finalization to keep EUR_1kg even after AoU lands.
  pin:
    EUR: null      # e.g., "EUR_1kg" to force-pin
    AFR: null
    TRANS: null
```

Plus a Python helper `src/python/ld_panel.py::resolve_ld_path(region_id, ancestry, config) -> Path`:

```python
def resolve_ld_path(region_id: str, ancestry: str, config: dict) -> Path:
    """Walk config['ld_panel'][ancestry] fallback chain; return first existing .rds.
    Honor pin override if set. Raise FileNotFoundError if strict_aou_only and
    AFR_aou path missing, else if no path in chain exists.
    """
    panel_cfg = config["ld_panel"]
    pin = panel_cfg.get("pin", {}).get(ancestry)
    chain = panel_cfg[ancestry]
    if pin is not None:
        chain = [c for c in chain if c["source"] == pin]
        if not chain:
            raise ValueError(f"pin {pin} not in {ancestry} chain")
    for entry in chain:
        # region_id is the M2 manifest ID (e.g., m2_region_00067); region_safe
        # is the legacy curated naming (e.g., FTO_16q12). Wave 0 manifest emits
        # both; resolver picks based on path template.
        path_str = entry["path"].format(region_id=region_id, region_safe=region_id)
        path = Path(path_str)
        if path.exists():
            return path
        if panel_cfg.get("strict_aou_only", False) and entry["source"].endswith("_aou"):
            raise FileNotFoundError(f"strict_aou_only: {ancestry} AoU panel missing for {region_id}")
    raise FileNotFoundError(f"No LD panel found for {region_id} {ancestry}")
```

**Integration point:** `src/snakemake/rules/finemap.smk` line 56-60 `ld_matrix` input becomes:

```python
ld_matrix=lambda wildcards: str(
    resolve_ld_path(
        wildcards.region,
        wildcards.ancestry,
        config,
    )
),
```

**Rationale:** Three-tier fallback handles the staged rollout cleanly (e.g., during Wave 4 production fire, the `AFR_aou/{region_id}.rds` for some regions may not yet have arrived, while others have — fallback to `AFR_hgdp_1kg` keeps M4 unblocked for early regions, with strict mode available for the final manuscript-freeze run). Pin override gives Track A (EUR_1kg) and Carter cross-panel sensitivity tests a clean handle. The `region_id` vs `region_safe` dual-format handling is a known wart from the legacy region-naming convention; plan task should explicitly normalize these (resolver fallback is the cheap mitigation; M2-supplementary or M5 may decide a one-time migration).

**Confidence:** HIGH — all existing `paths:` resolution patterns honor this design; `resolve_ld_path` is unit-testable against `tests/m3/test_ld_panel_resolver.py`.

### Q8 — AoU `ancestry_pred` field name verification

**Recommendation:** **Use `ancestry_pred`** (verified against `All Of Us Research Program Genomic Research Data Quality Report` (researchallofus.org Feb 2022 PDF) and the cited public AoU "Genetic ancestry and population structure" paper (PMC12049439, 2024). The CDR-version-flexibility flag in spec §3.1 (`pca_ancestry_category` as alternative) is a v5/v6 legacy term not present in the current v7 documentation).

**Rationale:** AoU's published genomic data quality report explicitly uses `ancestry_pred` as the column name; v7 release notes inherit that convention. The values are six-class continental: `{afr, amr, eas, eur, sas, mid, oth}` (oth = "other"; mid = Middle Eastern / West Asian). The ancestry-prediction TSV is described in support docs as "a .tsv file along with a plot of the ancestry predictions (html file)" sorted by research_id, accessed under `gs://fc-aou-datasets-controlled/{cdr_version}/wgs/.../aux/ancestry/` (path inferred from the corresponding relatedness path verified at Q9).

**How:** Pin in `aou_ld_panel.py` driver as a top-of-file constant:

```python
# Verified against AoU C2025Q1 CDRv7 docs (2026-04-27); reverify at submission
ANCESTRY_FIELD = "ancestry_pred"
ANCESTRY_VALUES = {"afr", "amr", "eas", "eur", "sas", "mid", "oth"}
```

**Risk:** If AoU v8 (rumored 2026-Q3 release) renames or restructures, M3 re-run on v8 must update this constant. R7 risk row in spec §12 catches this.

**Confidence:** HIGH — verified against two independent AoU public sources.

### Q9 — AoU `RELATED_SAMPLES_HT_PATH` env var

**Recommendation:** **`RELATED_SAMPLES_HT_PATH` is NOT an AoU-provided env var.** The actual canonical path on v7 is hardcoded under `gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/relatedness/relatedness_flagged_samples.tsv` (verified via `AoUPRS` open-source library Python snippet on GitHub, 2026-04-27). The accompanying `relatedness.tsv` (full pairwise table) lives in the same `aux/relatedness/` directory.

**Recommended driver pattern:**

```python
# AoU env vars (verified)
WORKSPACE_BUCKET = os.getenv("WORKSPACE_BUCKET")     # workspace egress staging
GOOGLE_PROJECT   = os.getenv("GOOGLE_PROJECT")       # billing
WGS_MT_PATH      = os.getenv("WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH")  # AoU-provided ACAF MT
WGS_VDS_PATH     = os.getenv("WGS_VDS_PATH")         # full VDS (alternative; we don't need)

# Hardcoded auxiliary paths (NOT env vars; pin to CDR version in driver)
CDR_VERSION = "v7"  # or "v8" once released
AUX_BASE = f"gs://fc-aou-datasets-controlled/{CDR_VERSION}/wgs/short_read/snpindel/aux"
RELATED_SAMPLES_PATH = f"{AUX_BASE}/relatedness/relatedness_flagged_samples.tsv"
RELATEDNESS_FULL_PATH = f"{AUX_BASE}/relatedness/relatedness.tsv"
ANCESTRY_PREDS_PATH = f"{AUX_BASE}/ancestry/ancestry_preds.tsv"   # Q8 inferred path
```

The spec §5.1 line 142's `os.environ["RELATED_SAMPLES_HT_PATH"]` will fail at runtime — confirmed it does not exist as an AoU-set env var. Replace with the explicit path constant pattern above. Hail Table loading: `hl.import_table(RELATED_SAMPLES_PATH, key='sample_id')` (the file is a TSV, not a Hail Table; the variable name in spec `relateds = hl.read_table(...)` is also misleading — it's an `import_table`, not `read_table`).

**Confidence:** HIGH on the path (verified against AoUPRS open-source GitHub library); MEDIUM on the ancestry preds path (inferred — the planner should add a Wave 0 quick-verify task that runs `gsutil ls $AUX_BASE/ancestry/` from inside the AoU workspace to confirm the exact filename).

### Q10 — MAF lower bound for export vs internal

**Recommendation:** **Adopt spec §7.2 default exactly: MAF ≥ 0.005 internal (Hail variant_qc filter), MAF ≥ 0.01 at export.** Document the variant-count drop in `m3-VALIDATION.md` Check 4 ancillary table.

**Rationale:** The spec rationale stands on its own merits: SuSiE benefits from denser variant grids; the n ≈ 60-95k AFR cohort gives stable LD estimates at MAF ≥ 0.005 (SE per off-diagonal entry ≈ 1/sqrt(n) ≈ 0.003); the export-tier MAF ≥ 0.01 cuts size ~30 % per AFR (per spec §7.2 cited number); novel-variant discovery (REQ-NOVELTY-CLASS-2 AFR-specific) targets variants with `MAF_AFR ≥ 0.01` as the operational definition (per `REQUIREMENTS.md` REQ-NOVELTY-CLASS-2 line 314), so MAF ≥ 0.01 export retains every variant the project will downstream-claim.

**Variant-count drop check:** The 30 % drop figure from spec §7.2 is unverified for AoU AFR specifically. **Wave 2 dev-10 fire MUST emit per-region n_var counts at both thresholds (0.005 internal, 0.01 export)** as a sanity check before production. If the AFR drop > 50 % in any dev region, halt for a Carter checkpoint to reconsider — the structural concern is that AFR has more rare alleles than EUR by population genetics, so the drop could be larger than expected.

**Confidence:** MEDIUM-HIGH on accepting the spec default; HIGH on the requirement to verify drop empirically before production.

### Q11 — MTAG-novel exemplar dev region candidates (5 AFR-known slots)

**Recommendation for the 5 AFR-known dev slots (D-M3-04):**

Direct grep of `union_region_list.bed` against published AFR GWAS lead loci yields these candidates (region IDs found):

| Region ID | Coords (GRCh37) | Span | M2 provenance hits | Published AFR GWAS context | Check coverage |
|-----------|-----------------|------|---------------------|------------------------------|----------------|
| **m2_region_00067** | chr16:46.2M-91.1M | 44.9 Mb | Includes `bmi.AFR.PAGE.2019.AFR` MTAG (FTO 16q12) | Locke 2015 / Graff 2017 PAGE BMI AFR; rs1558902 lead | Check 1 + Check 3 (16q12 BMI AFR is the spec §9.3 canonical Check 3 region) |
| **m2_region_00006** | chr1:104.6M-122.2M | 17.7 Mb | `ldl.AFR / tc.AFR / tg.AFR` GLGC-AFR MTAG (SORT1 1p13 family) | Willer 2008 / Teslovich 2010 / Graham 2021 GLGC; rs12740374 lead | Check 1 (SORT1 published AFR LD) + Check 3 (SuSiE-RSS lipids AFR) |
| **m2_region_00040** | chr12:37.7M-126.8M | 89.0 Mb | `ldl.AFR / tc.AFR / hdl.AFR` GLGC-AFR + SH2B3 12q24 region | Graham 2021 GLGC-AFR lipids; SH2B3 published AFR | Check 1 + 4 (HLA-stress-adjacent at 89 Mb span) |
| **m2_region_00083** | chr19:27.3M-60.1M | 32.8 Mb | `ldl.AFR / tc.AFR / hdl.AFR / tg.AFR` GLGC-AFR + APOE 19q13 | Graham 2021 GLGC-AFR; APOE 19q13.32 well-characterized AFR | Check 1 + Check 3 |
| **m2_region_00027** | chr11:23.7M-40.5M | 16.9 Mb | LDLR 11p13 region (no AFR-specific lead but classic lipids region) | Willer 2008 EUR-primary; Graham 2021 GLGC-AFR sensitivity | Check 1 + Check 4 |

**The 2 HLA-stress slots:**

| Region ID | Coords | Span | Why HLA-stress |
|-----------|--------|------|-----------------|
| Find via `awk '$1=="chr6" && $2 >= 25e6 && $3 <= 40e6'` on `union_region_list.bed` | chr6 ~28-34 Mb HLA classical | varies | Densest LD region in genome; tests Path A.3 BlockMatrix write |
| **8p23 inversion** — chr8:7.9M-... region 8p23 inversion neighborhood (one of the chr8 regions in M2 union; first chr8 region starts at 7.89 Mb per direct measurement) | chr8 7.9M-... | varies | Inversion creates anomalous LD blocks; tests SuSiE convergence on structured non-Pearson LD |

**The 3 EUR-Track-A-comparable slots (D-M3-04 spec):** Pick from the 11 Track A `data/processed/ld_reference/EUR/*.rds` files. Recommended:
- `FTO_16q12.rds` (matches m2_region_00067 region — direct overlap for EUR vs AoU EUR comparison)
- `SH2B3_12q24.rds` (matches m2_region_00040)
- `APOE_19q13.rds` (matches m2_region_00083)

This yields 3 dev slots where Check 2 (AoU EUR vs 1000G EUR Pearson r) AND Check 1 (AoU AFR vs published) AND Check 3 (SuSiE-RSS) AND Check 4 (A/B yield) all converge on the same 3 underlying regions. **This is a much stronger validation matrix than 3 disjoint EUR + 5 disjoint AFR regions** — it exercises cross-ancestry comparability on identical genomic substrate. **Strongly recommend the planner adopt this overlapping-slot design.**

**Carter checkpoint required:** D-M3-04 explicitly says "Suggested" picks; the 8p23 inversion choice and the precise HLA boundary are flagged for Carter review at Wave 0 dev-subset selector commit.

**Confidence:** HIGH on the M2 region IDs (verified by direct grep); MEDIUM on the published-AFR-GWAS lead variant matchup (inferred from M2 provenance JSON; full verification requires checking each region's MTAG-novel.tsv detail).

### Q12 — Per-chromosome egress audit log structure

**Recommendation for `.planning/amendments/aou-egress-audit-log.md`:**

```markdown
# AoU Egress Audit Log

This file is appended-only. Each entry documents one AoU export request.
Schema columns: see header row in audit table below.
OSF cross-reference: osf.io/az52u (Project amendment record).

## Egress Classification Ruling (HARD GATE)

| Date | Request type | Classifier (AoU support email/case ID) | Ruling | Document |
|------|--------------|----------------------------------------|--------|----------|
| YYYY-MM-DD | Variant×variant LD matrix from n≥60k AFR | AoU support case #_____ | Aggregate summary statistic / not derived individual data | (link to AoU email or PDF cap) |

## Per-Bundle Audit Entries

| Timestamp (ISO-8601 UTC) | Phase | Chr | Ancestry | n_regions | Compressed size (GB) | AoU export request ID | OSF cross-ref | SHA-256 manifest path | Bundle content (region_ids) | Reviewed by AoU on | Egressed to NCSU on | Notes |
|--------------------------|-------|-----|----------|-----------|----------------------|------------------------|---------------|------------------------|------------------------------|--------------------|---------------------|-------|
| 2026-MM-DDTHH:MM:SSZ | M3 | 1 | AFR_aou | 14 | 14.2 | AoU-EXPORT-12345 | osf.io/az52u | .planning/amendments/sha256/m3_chr1_afr_aou.tsv | m2_region_00001..m2_region_00014 | 2026-MM-DD | 2026-MM-DD | — |
| 2026-MM-DDTHH:MM:SSZ | M3 | 1 | EUR_aou | 14 | 22.8 | AoU-EXPORT-12346 | osf.io/az52u | .planning/amendments/sha256/m3_chr1_eur_aou.tsv | m2_region_00001..m2_region_00014 | 2026-MM-DD | 2026-MM-DD | — |
... (44 rows for M3) ...

## M1-AFR-SBP cross-reference (DEC-2026-04-24-02)

| Timestamp | Phase | ... |
|-----------|-------|-----|
| (M1-supplementary fills here) | M1 | ... |
```

**Rationale:** The schema must (a) prove the 20-cell suppression floor was respected for every bundle (aggregate from n ≥ 60k AFR / n ≥ 130k EUR clears it trivially — encoded as a column reference back to the cohort summary), (b) capture AoU's export request ID for paper-trail audit (linked to AoU's review queue), (c) capture SHA-256 for byte-for-byte reproducibility on Zenodo deposit at publication, (d) cross-reference OSF amendment id (osf.io/az52u) to keep AoU registration and OSF pre-registration aligned (per DEC-2026-04-25-02), (e) capture the egress classification ruling once (Header section) so all 44 bundles inherit the same legal basis. **The classification ruling is the critical hard-gate row** — without it filed in writing, Carter cannot start any Dataproc compute (Risk R1 in spec §12).

**Append-only enforcement:** A Wave 0 task adds `.planning/amendments/aou-egress-audit-log.md` to `.gitattributes` with `merge=union` so accidental edits don't overwrite history; alternatively, just commit-discipline. An optional Wave 5 task creates `.planning/amendments/sha256/m3_chr{N}_{ANCESTRY}_aou.tsv` per bundle (44 small files) so the SHA-256 manifest is auditable per-bundle, not a single 322-row monolith.

**Confidence:** HIGH — schema is a direct elaboration of the project's existing `sha256_manifest_*.tsv` + OSF amendment pattern.

---

## Validation Architecture

> **Required by `nyquist_validation: true`** in `.planning/config.json`. This section is consumed by `m3-VALIDATION.md` template fill-in and by the Snakemake DAG gate `m3_dev_complete.flag` per D-M3-03.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.x for AoU driver unit tests; Snakemake 7.32.4 for end-to-end DAG validation; R-side `testthat` for `ld_npz_to_rds.R` |
| Config file | `pyproject.toml` (root) for pytest; existing `Snakefile` for snakemake; `tests/m3/conftest.py` (NEW) for shared fixtures |
| Quick run command | `pytest tests/m3 -x --tb=short` (≈ 30s on synthetic MT) |
| Full suite command | `pytest tests/m3 && snakemake --snakefile Snakefile --cores 4 --use-conda m3_dev_complete` |
| Phase gate | `m3_dev_complete.flag` (Snakemake target; touched only after Carter signoff per D-M3-03) → required input for production rules |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| REQ-AOU-LD-EGRESS | AoU `.npz` lands at `data/interim/aou_ld_exports/{ANCESTRY}/{region_id}.npz` | integration | `pytest tests/m3/test_aou_export_landing.py` | ❌ Wave 0 |
| REQ-AOU-LD-EGRESS | `.npz` converts to `.rds` with symmetric matrix + dimnames | unit | `pytest tests/m3/test_ld_npz_to_rds.py` | ❌ Wave 3 |
| REQ-AOU-LD-VALIDATION Check 1 | Known-locus LD pattern matches published (FTO 16q12 + SORT1 1p13) | manual + automated | `pytest tests/m3/test_validation_check_1_known_locus.py` (invariants) + Wave 4 visual review against published figures | ❌ Wave 4 |
| REQ-AOU-LD-VALIDATION Check 2 | AoU EUR vs 1000G EUR entry-wise Pearson r ≥ 0.97 for MAF ≥ 0.05 | unit | `pytest tests/m3/test_validation_check_2_aou_eur_vs_1kg.py` | ❌ Wave 4 |
| REQ-AOU-LD-VALIDATION Check 3 | SuSiE-RSS converges on 16q12 BMI AFR; ≥1 CS at PIP coverage 0.95; median CS ≤ 30; lead PIP ≥ 0.1 | integration | `pytest tests/m3/test_validation_check_3_susie_convergence.py` | ❌ Wave 4 |
| REQ-AOU-LD-VALIDATION Check 4 | AoU-AFR vs identity-placeholder A/B yield contrast tabulated | unit + integration | `pytest tests/m3/test_validation_check_4_identity_ab.py` | ❌ Wave 4 |
| REQ-PUBLIC-DATA-ONLY | OSF posting confirms public-summary-only artifacts; no individual-level data exported | manual | Wave 5 OSF deposit + Carter signoff | governance |
| REQ-SNAKEMAKE-CI | Toy 3-locus pipeline includes AFR identity-placeholder LD | integration | Existing `tests/toy_3locus/Snakefile.test --cores 2` extended with new `*.AFR.rds` paths | ❌ Wave 5 |
| REQ-PATH-PARAMETERIZATION | `ld_panel:` resolver returns expected path under all chains | unit | `pytest tests/m3/test_ld_panel_resolver.py` | ❌ Wave 0 |

### Sampling Rate (per Nyquist Dimension 8)

- **Per task commit:** `pytest tests/m3 -x` (~30s; covers latest unit tests)
- **Per wave merge:** `pytest tests/m3 && snakemake --snakefile Snakefile --cores 4 --dry-run m3_dev_complete` (DAG resolution check)
- **Phase gate (M3 → M4):** Full suite + `m3_dev_complete.flag` exists + Carter signoff committed in `m3-VALIDATION.md`

### The 4-Check Validation Protocol — Formalized Pass Thresholds

This is the canonical measurable specification of REQ-AOU-LD-VALIDATION, derived from AOU-LD-PIPELINE.md §9 and tightened against the project's existing comparator substrate.

**Check 1 — Known-locus LD pattern.**
- **What:** Render AoU AFR LD heatmap for FTO 16q12 (m2_region_00067, focused on rs1558902 ±500 kb) and SORT1 1p13 (m2_region_00006, focused on rs12740374 ±500 kb).
- **Comparator:** Published AFR LD figures from Locke et al. 2015 *Nature* (FTO) and Teslovich et al. 2010 *Nature* (SORT1) plus PAGE 2017 *Nature* (Graff et al.) AFR-specific haplotype panels.
- **Pass threshold:** LD block boundaries within ±5 kb of published published panel positions; block-major-axis diagonal extent agreement on visual inspection (Carter signoff). **Quantitative metric:** correlation of pixel intensity in 100×100 pixel binned heatmap ≥ 0.85 against the published reference image (after registration to common coordinate grid). Stretch goal — not a hard gate at first iteration.
- **Output:** `validation/check_1_known_locus_heatmaps/{region_id}.png`; `validation/check_1_invariants.tsv` with block-boundary-distance column.
- **Fail mode:** If LD blocks visually do not match published, halt for diagnostic. Possible causes: ancestry-pred miscall, kinship-pruning miscall, MAF threshold mismatch with published study.

**Check 2 — AoU EUR vs 1000G EUR entry-wise Pearson correlation.**
- **What:** For each of the 3 EUR-Track-A-comparable dev regions, compute entry-wise Pearson r between AoU EUR LD and 1000G EUR Phase 3 LD (existing `data/processed/ld_reference/EUR/{region}.rds` substrate).
- **Pass threshold:** **mean r ≥ 0.97 for variants with MAF ≥ 0.05 in BOTH panels** (spec §9.2). Secondary threshold: mean r ≥ 0.90 for MAF 0.01-0.05.
- **Failure handling:** If any region falls below 0.97 at MAF ≥ 0.05, document in validation memo + flag the region as "EUR_aou-1kg-discrepant" — does NOT block production fire (Risk R4 in spec §12: "expected for MAF 0.01-0.05; would be unexpected for common variants"). If ≥ 2 of 3 regions are discrepant at MAF ≥ 0.05, halt for diagnostic — likely indicates a systemic AoU-EUR cohort QC issue.
- **Output:** `validation/check_2_aou_eur_vs_1kg/{region_id}_pearson_r_by_maf_bin.tsv`; aggregated to `validation/check_2_summary.tsv`.

**Check 3 — SuSiE-RSS convergence on 16q12 BMI AFR.**
- **What:** Run SuSiE-RSS with `L=10` and `min_abs_corr=0.5` (per `config/susie_policy.yaml`) on FTO 16q12 BMI AFR using AoU AFR LD vs published AFR BMI sumstats (PAGE 2017 Graff et al. or Loh 2022 BMI AFR).
- **Pass thresholds (all four required):**
  1. SuSiE `converged == TRUE`
  2. ≥ 1 credible set at PIP coverage 0.95
  3. Median credible-set size ≤ 30 variants (matching EUR-pipeline expectations from Track A)
  4. Lead variant (rs1558902 in FTO) PIP ≥ 0.1 (spec §9.3 — does NOT require it ranked #1)
- **Output:** `validation/check_3_susie_16q12_bmi_afr/susie_fit.rds`; `validation/check_3_summary.tsv` (converged, n_cs, median_cs_size, lead_pip).
- **Fail mode:** If converged=FALSE → likely LD-singularity issue at radius boundary or zero-variance variants. If n_cs=0 → underpowered (lower priority; document but don't halt). If median CS > 30 → LD precision problem (likely): halt for diagnostic.

**Check 4 — AoU-AFR vs identity-placeholder A/B yield contrast.**
- **What:** For all 7 dev regions with AFR signal (5 AFR-known + 2 HLA-stress), run SuSiE-RSS twice — once with AoU AFR LD, once with identity-placeholder LD (existing `_identity_backup` substrate). Tabulate per-region: n_cs, median_cs_size, lead_pip, converged.
- **Pass threshold:** **No hard pass threshold** — this is the headline validation NUMBER that justifies M3's existence. Expected direction: AoU AFR yields more credible sets, smaller median CS, higher lead PIP than identity-placeholder. Document the magnitude per region.
- **Output:** `validation/check_4_identity_ab/yield_table.tsv`; this is THE validation memo's headline figure.
- **Soft expectation:** mean(AoU LD CS) > mean(identity LD CS) by ≥ 1 region in 4 of 7 regions; mean(AoU lead PIP) > mean(identity lead PIP) on at least 5 of 7 regions. If reversed, halt — methodological anomaly.

### Wave 0 Gaps

These test artifacts must be created in Wave 0 (or Wave 3/4 as specified), before the corresponding production work fires:

- [ ] `tests/m3/conftest.py` — shared fixtures (synthetic MT loader, region manifest factory, mock AoU env)
- [ ] `tests/m3/test_build_ld_region_manifest.py` — Wave 0; tests Q1 + Q2 reformatter (liftover + radius computation)
- [ ] `tests/m3/test_ld_panel_resolver.py` — Wave 0; tests Q7 resolver fallback chain
- [ ] `tests/m3/test_aou_ld_panel_local.py` — Wave 0; runs Hail driver against synthetic MT (Q6)
- [ ] `tests/m3/fixtures/build_synthetic_mt.py` — Wave 0; generates `synthetic_aou.mt` via balding_nichols_model
- [ ] `tests/m3/test_ld_npz_to_rds.py` — Wave 3; tests `.npz → .rds` round-trip + symmetry recovery
- [ ] `tests/m3/test_validation_check_{1..4}*.py` — Wave 4; per-check invariant tests
- [ ] `tests/m3/test_aou_export_landing.py` — Wave 4; verifies bundle structure + sizes
- [ ] Framework install (already on disk): pytest 8.x + Hail 0.2.x in `envs/m3-aou-dev.yml`

---

## Wave-by-Wave Research Findings

### Wave 0 — Workspace + envs + region manifest + dev-subset selector + ld_panel resolver

**Reuse vs build new:**

| Task | Reuse | Build new |
|------|-------|-----------|
| Region manifest reformatter | `src/python/build_region_union.py` pattern | `src/python/build_ld_region_manifest.py` (sibling); reads `results/regions/union_region_list.bed`, expands provenance JSON, performs GRCh37 → GRCh38 liftover (Q1), computes per-region `radius_bp` (Q2), emits `config/ld_regions.tsv` (322 rows, 9 columns: region_id, chr, start_grch37, end_grch37, start_grch38, end_grch38, ancestry, source_trait, lead_variant, radius_bp, region_class) |
| Dev-subset selector | none | `src/python/select_ld_regions_dev.py` (D-M3-04 spec default; 10 rows; emits `config/ld_regions_dev.tsv`) |
| ld_panel: config | `config/pipeline.yaml` `paths:` block layout | `ld_panel:` block (Q7 above) |
| Conda envs | `envs/ld_build.yml` convention | `envs/m3-aou-dev.yml` (Python 3.11 + hail 0.2.x + pyspark + google-cloud-storage + pandas + numpy + pytest); `envs/m3-r-ld.yml` (R 4.4 + reticulate + Matrix; per CLAUDE.md Snakemake/Python pin) |
| ROADMAP wording update | none | One-line patch to `.planning/ROADMAP.md` M3 entry per D-M3-01 |
| .gitignore additions | existing `data/raw/*` etc. | Explicit lines for `data/interim/aou_ld_exports/`, `data/processed/ld_reference/AFR_aou/`, `data/processed/ld_reference/EUR_aou/` per spec §10.2 |
| Egress audit log seed | none | `.planning/amendments/aou-egress-audit-log.md` (per Q12 schema) |
| AoU workspace (HUMAN GATE) | none | Carter pastes `AOU-WORKBENCH-REGISTRATION.md` into AoU portal; files DUS/RPS/billing/P&P/egress classification |

**File inventory:**
- `config/ld_regions.tsv` (322 rows; new)
- `config/ld_regions_dev.tsv` (10 rows; new)
- `config/pipeline.yaml` (modified — add `ld_panel:` block)
- `envs/m3-aou-dev.yml` (new)
- `envs/m3-r-ld.yml` (new)
- `src/python/build_ld_region_manifest.py` (new)
- `src/python/select_ld_regions_dev.py` (new)
- `src/python/ld_panel.py` (new — Q7 resolver helper)
- `tests/m3/test_build_ld_region_manifest.py` (new)
- `tests/m3/test_ld_panel_resolver.py` (new)
- `tests/m3/conftest.py` (new)
- `tests/m3/fixtures/build_synthetic_mt.py` (new)
- `.planning/amendments/aou-egress-audit-log.md` (new)
- `.gitignore` (modified)

### Wave 1 — AoU cohort definition pipeline (AOU-1)

**Reuse vs build new:**

| Task | Reuse | Build new |
|------|-------|-----------|
| Hail driver | None — first AoU code in repo | `src/python/aou_ld_panel.py` (Hail driver; runs INSIDE AoU Workbench Dataproc Jupyter; mirrored locally for unit testing against synthetic MT). Implements canonical ordering per `## Hail v0.2.x API Verification > Recommended driver ordering` above. |

**Driver code patterns to honor:**
- AoU env vars verified: `WORKSPACE_BUCKET`, `GOOGLE_PROJECT`, `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` (from Q9)
- Hardcoded auxiliary paths under `gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/` (from Q9 + Q8)
- `ANCESTRY_FIELD = "ancestry_pred"`, `ANCESTRY_VALUES = {"afr","amr","eas","eur","sas","mid","oth"}` constants (Q8)
- KING kinship threshold: 0.0442 (third-degree, conservative — D-M3-07)
- `mt.checkpoint("gs://fc-secure-<workspace-id>/ld/mt_afr_qc.mt")` per spec §5.1
- Sample QC ordering: `split_multi_hts` BEFORE `variant_qc` (corrected from spec; `## Hail v0.2.x API Verification` above)

**Sensitivity-check pattern (D-M3-07):**
```python
# Two cohort tables emitted at AOU-1
mt_afr_pca = filter to ancestry_pred == 'afr' + kinship + sample_qc  # primary
mt_afr_pca_selfid = mt_afr_pca.filter(self_report in {'Black or African American'})  # sensitivity
# 10-region dev fire emits LD for both; sensitivity_check_correlation table in m3-VALIDATION.md
```

**File inventory:**
- `src/python/aou_ld_panel.py` (new) — Hail driver; ~400 lines including the `compute_region_ld()` function with three Path A.1/A.2/A.3 branches per Q5
- `notebooks/AOU-1_cohort_definition.ipynb` (new) — Jupyter wrapper invoking driver functions; lives ONLY inside AoU workspace (not committed to NCSU repo; reference copy in `.planning/notebooks/AOU-1_template.ipynb`)
- `notebooks/AOU-2_per_region_ld.ipynb` (new) — same pattern
- `tests/m3/test_aou_ld_panel_local.py` (new) — runs driver against `synthetic_aou.mt`

### Wave 2 — 10-region dev fire + Check 1+2+3+4 validation + Carter signoff

**Reuse vs build new:**

| Task | Reuse | Build new |
|------|-------|-----------|
| Dev-fire orchestration | `notebooks/AOU-2_per_region_ld.ipynb` from Wave 1 | Wave 2 calls AOU-2 with `config/ld_regions_dev.tsv` (10 regions) instead of full 322 |
| Validation harness | None | `notebooks/AOU-4_validation.ipynb` (R kernel; runs Checks 1-4); NCSU-side `src/python/m3_validation_*.py` for reproducibility |
| Validation outputs | None | `validation/check_{1,2,3,4}*.{tsv,png}` files (per Q11 + Validation Architecture above); aggregated to `m3-VALIDATION.md` |
| Carter signoff gate | Existing GSD checkpoint pattern | `m3_dev_complete.flag` Snakemake target; required input for any Wave 4 production rule |

**Hard human-action gate inside Wave 2:** Carter signs `m3-VALIDATION.md` after reviewing the 4 check outputs + the EUR_aou vs 1000G EUR comparator + the A/B yield contrast — this is the canonical "promotion gate" per AOU-LD-PIPELINE.md §9 + REQ-AOU-LD-VALIDATION.

### Wave 3 — NCSU `.npz → .rds` ingest + ld_panel: resolver wiring

**Reuse vs build new:**

| Task | Reuse | Build new |
|------|-------|-----------|
| `.npz → .rds` converter | `envs/r_coloc.yml` for R deps; spec §8.2 R script as starting point | `src/scripts/ld_npz_to_rds.R` (verbatim from spec §8.2) + per-region `data/external/liftover/hg38ToHg19.over.chain.gz` for variant ID b37 conversion (DEC-2026-04-24-01) |
| Snakemake ingest rules | `src/snakemake/rules/m1_download.smk` flag-driven pattern; `src/snakemake/rules/ld_reference.smk` `LD_BUILD_ENV` absolute-path conda pattern | `src/snakemake/rules/m3_ingest_aou_ld.smk` (NPZ-arrives flag rule); `src/snakemake/rules/m3_convert_npz_rds.smk` (`.npz → .rds`) |
| ld_panel: resolver integration | `src/snakemake/rules/finemap.smk` line 56 `ld_matrix` input | Modify finemap.smk to call `resolve_ld_path(...)` from `src/python/ld_panel.py` (Q7) |
| M4 hand-off integration test | Existing `tests/toy_3locus/Snakefile.test` | Extension: add an AoU AFR identity-placeholder smoke fixture that exercises the resolver fallback chain in CI |

**File inventory:**
- `src/scripts/ld_npz_to_rds.R` (new; from spec §8.2, with chr-prefix-handling fix)
- `src/python/bm_to_npz.py` (new; only if Wave 2 dev fire needs Path A.3 — densifies Hail BlockMatrix sharded directory to NPZ for ingest)
- `src/snakemake/rules/m3_ingest_aou_ld.smk` (new; flag-driven AoU export-arrives rule)
- `src/snakemake/rules/m3_convert_npz_rds.smk` (new; `build_ld_rds_aou_afr` + `build_ld_rds_aou_eur`)
- `src/snakemake/rules/finemap.smk` (modified — `ld_matrix` input via resolver)
- `Snakefile` (modified — include new rules)
- `tests/m3/test_ld_npz_to_rds.py` (new)

### Wave 4 — Production fire 322 cells + per-chromosome egress + audit log

**Reuse vs build new:**

| Task | Reuse | Build new |
|------|-------|-----------|
| Production fire | `notebooks/AOU-2_per_region_ld.ipynb` from Wave 1 | Run with `config/ld_regions.tsv` full 322 rows; gated on `m3_dev_complete.flag` |
| Per-chromosome export | none | Carter human action: 22 × 2 = 44 export requests via AoU portal Notebooks/Files UI (Q3) |
| Audit log appends | `.planning/amendments/aou-egress-audit-log.md` from Wave 0 | One row per bundle (Q12) committed as bundles arrive |
| 4-check production tabulation | `notebooks/AOU-4_validation.ipynb` from Wave 2 | Run with full 322 cells (sampling-based — full 4-check at production scale would be 322× compute); minimum: re-run Check 4 yield contrast on a random 30-region sample |

**File inventory:**
- `src/snakemake/rules/m3_validation.smk` (new; runs Check 4 sampling at production scale)
- `validation/check_*` per-bundle outputs (incremental as bundles arrive)
- `data/processed/ld_reference/AFR_aou/{region_id}.rds` (161 files)
- `data/processed/ld_reference/EUR_aou/{region_id}.rds` (161 files)
- `data/interim/aou_ld_exports/{AFR_aou,EUR_aou}/*.npz` (322 files; deleted post-conversion per spec §10.3)

### Wave 5 — Close-out

**Reuse vs build new:**

| Task | Reuse | Build new |
|------|-------|-----------|
| Validation memo finalize | M2's `m2-VALIDATION.md` template + Wave 2 `m3-VALIDATION.md` draft | Final m3-VALIDATION.md committed |
| Egress audit log finalize | Wave 4 incremental appends | Final 44-row table |
| Phase close-out artifact | M2's `m2-PHASE-CLOSEOUT.md` template | New m3-PHASE-CLOSEOUT.md |
| SHA-256 freeze | M2's `sha256_manifest_m2_frozen.tsv` template | `sha256_manifest_m3_frozen.tsv` (322 .rds + 44 .npz pre-deletion checksums) |
| OSF posting prep | osf.io/az52u amendment record | M3 validation memo PDF posted to osf.io/az52u as supplementary file (Carter manual; same form as M1's osf.io/az52u/files/k8w7n) |
| M2-supplementary phase setup | ROADMAP successor pattern | ROADMAP.md adds `m2-supp-aou-afr-rerun` slug as M3 successor + `M2-POST-M3-*` obligation status note |
| Toy 3-locus extension | `tests/toy_3locus/data/ld_ref/EUR/*.rds` | `*.AFR.rds` identity-placeholder per REQ-SNAKEMAKE-CI |

**File inventory:**
- `.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION.md` (final)
- `.planning/phases/m3-aou-afr-ld-panel-build/m3-PHASE-CLOSEOUT.md` (new)
- `.planning/amendments/sha256_manifest_m3_frozen.tsv` (new)
- `.planning/amendments/aou-egress-audit-log.md` (final)
- `.planning/m2_post_m3_rerun_queue.tsv` (modified — status note "M3 complete; M2-supplementary eligible")
- `.planning/ROADMAP.md` (modified — M2-supplementary entry)
- `tests/toy_3locus/data/ld_ref/EUR/*.AFR.rds` (new identity-placeholder fixtures)

---

## Hard Gates / Human Action Items (NOT planner-actionable)

These items block the Wave 1+ Dataproc spend. They are explicitly Carter human action; the M3 plan can SCHEDULE them as pre-conditions but cannot resolve them in code:

| # | Gate | Source | Blocking | Carter action |
|---|------|--------|----------|---------------|
| 1 | AoU workspace creation | spec §2 P2 + Carter directive | Wave 1+ | Paste from `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md` into AoU portal |
| 2 | DUS approval | spec §2 P2 | Wave 1+ | AoU portal — Data Use Statement signoff |
| 3 | RPS approval | spec §2 P3 | Wave 1+ | AoU portal — Research Purpose Statement (template language already in registration doc §10) |
| 4 | Billing profile attached | spec §2 P4 | Wave 1+ | AoU portal — confirm ASHES Lab credits cover controlled-tier compute (or attach personal GCP profile) |
| 5 | P&P draft registration | spec §2 P6 | Wave 1+ (NOT manuscript submission — draft stage) | AoU portal Publications & Presentations module |
| 6 | **Egress classification in writing (R1 risk; HARD GATE)** | spec §12 R1 | Wave 1+ Dataproc spend | AoU support email exchange OR portal-issued ruling letter; classifies variant×variant LD matrices as "aggregate summary statistics" not "derived individual data" |
| 7 | Carter signoff on `m3-VALIDATION.md` | D-M3-03 | Wave 4 production fire | Sign + commit `m3-VALIDATION.md` after Wave 2 dev-10 4-check completion |
| 8 | OSF posting of validation memo | D-M3-08 | Phase close (Wave 5) | Manual upload to osf.io/az52u as supplementary file |

**These items MUST appear as `<human_gate>` blocks in the plan, NOT as task tasks that an executor agent can complete.**

---

## Open Issues / Known Unknowns (NOT resolved by research; planner must flag)

After research, these remain open for the planner / Carter to resolve:

### O1 — M2 region width vs M3 fine-mapping unit (CRITICAL — blocking design decision)

**The issue:** M2's `build_region_union.py` produces regions with median 9 Mb and max 102 Mb spans (verified empirically). The AoU spec assumed ~1-2 Mb regions. Per Q2 above, this forces per-region `radius` ≥ region span which scales LD compute as O(region_span²).

**Two viable resolutions:**

1. **Accept the wide regions and compute LD across each one fully.** Cost: 161 regions × O(region_span²) compute. For the 102 Mb region, this is 4 TB dense LD memory; only viable via Path A.3 (BlockMatrix write-to-bucket, never densify). Worth the cost: keeps the M2 region union as the canonical fine-mapping unit, no methodological asymmetry between M2 and M3, no re-derivation of M2.

2. **Re-merge M2 regions into ≤ 10 Mb max-width tiles before M3.** Inserts a new "Wave 0.5" task: `src/python/tile_wide_regions.py` reads `union_region_list.bed`, splits any region > 10 Mb at natural break points (lowest LD-density valleys), emits a "tiled" successor BED with provenance back to source M2 region. Cost: M2's region union is no longer the M3 fine-mapping unit; M4 fine-mapping operates on tiles, not original M2 regions; novelty calls (REQ-NOVELTY-CLASS-2 AFR-specific) become tile-anchored, not region-anchored. **Cleaner compute; messier methodology.**

**Recommendation:** **Resolution 1 (accept wide regions; use Path A.3 for > 10 Mb).** Methodological purity > compute convenience for a fine-mapping LD panel; the BlockMatrix-write path is engineering, not science. **Carter checkpoint required before Wave 0 final commit** if the planner is uncomfortable with this.

### O2 — AoU CDR version pinning (v7 vs v8)

**The issue:** AoU v8 is rumored 2026-Q3 release per spec §3.3 + R5 risk. M3 driver pins `CDR_VERSION = "v7"`. If v8 lands during Wave 1-4, do we re-run on v8?

**Recommendation:** Pin v7 at Wave 0 commit; explicit watch-item in Carter checkpoint reviews. If v8 lands during Wave 1-3, re-pin and re-run; if it lands during Wave 4 production fire, defer to a v8 supplementary phase post-M3 close. Document the pin date in the AoU egress classification ruling header.

### O3 — Wave 0 "ancestry preds" path verification

**The issue:** Q8 inferred `gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv` from the verified relatedness path pattern. Direct verification requires `gsutil ls` access from inside an AoU workspace.

**Recommendation:** First task of Wave 1 (after workspace gate) is a `gsutil ls $AUX_BASE/ancestry/` smoke check; if the actual filename differs, update the driver constant before any compute fires. Do NOT block Wave 0 on this.

### O4 — Region-level radius vs spec's static radius (already covered in Q2)

Surfaced and resolved above; carried forward as a Wave 2 dev-fire empirical-tuning task (verifying the 500 kb safety margin is sufficient).

### O5 — AoU EUR cohort relatedness with AFR cohort

**The issue:** Spec §3.4 builds AoU EUR with `ancestry_pred == 'eur'` independently. Some samples MAY appear in both kinship-pruning passes (i.e., a single individual ancestry_pred = 'afr' but `relateds` HT shows them related to a cousin ancestry_pred = 'eur'). The two cohorts will have shared excluded relateds but disjoint included samples — verify this is the spec-correct behavior (it should be; LD is computed per-cohort).

**Recommendation:** Wave 1 driver code includes a sanity check: `len(set(afr_samples) & set(eur_samples)) == 0` after both cohorts are defined. If non-zero, halt for diagnostic.

### O6 — `region_id` vs `region_safe` naming

**The issue:** Track A used `FTO_16q12.rds` (curated `region_safe` slug). M2 uses `m2_region_00067.rds` (sequential `region_id`). The `ld_panel:` resolver (Q7) handles both via path-template substitution, but downstream M4 finemap rule wildcards `{region}` need to be unambiguous about which family they expect.

**Recommendation:** Wave 0 task adds a one-time `region_id ↔ region_safe` mapping table at `config/region_id_mapping.tsv` so downstream code can translate. Do NOT rename existing `data/processed/ld_reference/EUR/*.rds` files in Wave 0 — that's a separate cleanup task for M5 or after.

### O7 — Whether the 30 % MAF-export drop applies in AoU AFR specifically

Surfaced in Q10. Verifiable empirically at Wave 2 dev-10 fire. Recommended as a Carter checkpoint sub-item of the Wave 2 → Wave 4 promotion review.

---

## Reference Inventory

Ranked by load-bearing weight for the M3 planner + executor (1 = read first; 5 = read on-demand):

### Priority 1 (READ BEFORE PLANNING)

1. **`.planning/amendments/AOU-LD-PIPELINE.md`** — full M3 architectural source-of-truth (~570 lines): cohort definition (§3), variant QC (§4), Hail BlockMatrix pipeline (§5.1), PLINK fallback (§5.2), parallelism strategy (§5.3), region list format (§6), export protocol (§7), local integration (§8), 4-check validation protocol (§9), storage naming + .gitignore (§10), compute cost (§11), risks (§12), AoU publication policy (§13), timeline (§14), open questions (§15).
2. **`.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md`** — 9 locked decisions D-M3-01 through D-M3-08; deliverable manifest; requirements traceability.
3. **`results/regions/union_region_list.bed`** — M2 deliverable; 161 regions; **MUST inspect span distribution before planning Wave 0 reformatter** (the structural finding in this RESEARCH.md hinges on it).
4. **This RESEARCH.md** — answers to the 12 open questions; Validation Architecture; wave-by-wave findings.

### Priority 2 (READ DURING PLANNING)

5. **`.planning/REQUIREMENTS.md`** — REQ-AOU-LD-EGRESS, REQ-AOU-LD-VALIDATION, REQ-PUBLIC-DATA-ONLY, REQ-SNAKEMAKE-CI, REQ-PATH-PARAMETERIZATION; novelty class definitions for forward-compat with M4.
6. **`.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md`** — paste-ready 13-section AoU portal registration document.
7. **`src/snakemake/rules/ld_reference.smk`** lines 274-334, 349-448 — existing `build_ld_rds_1kg_eur`, `download_ukbb_ld_tiles`, `build_hgdp_1kg_ld` rules; M3 extends the same conventions.
8. **`src/snakemake/rules/finemap.smk`** lines 45-102 — `run_finemap` rule (the LD-consuming downstream); modified by Wave 3 Q7 resolver wiring.
9. **`src/python/build_region_union.py`** — M2's region-union builder; sibling pattern for Wave 0 `build_ld_region_manifest.py`.
10. **`config/pipeline.yaml`** lines 21-52 (`paths:`), 180-196 (`finemap:`) — config layout reference; Wave 0 adds `ld_panel:` block.

### Priority 3 (READ DURING EXECUTION)

11. **Hail v0.2 docs:** https://hail.is/docs/0.2/methods/genetics.html (verified API surface in this RESEARCH.md `## Hail v0.2.x API Verification`).
12. **AoU Researcher Workbench docs:** https://support.researchallofus.org/hc/en-us/articles/29475228181908-How-the-All-of-Us-Genomic-data-are-organized
13. **AoU genomic data quality report (Feb 2022):** https://www.researchallofus.org/wp-content/themes/research-hub-wordpress-theme/media/2022/03/Feb2022_All_of_Us_Beta_Release_Genomic_Quality_Report.pdf — `ancestry_pred` field name; KING kinship.
14. **AoU genetic ancestry paper (PMC12049439, 2024):** https://pmc.ncbi.nlm.nih.gov/articles/PMC12049439/ — six-class continental ancestry framework.
15. **AoUPRS GitHub (v7+ env-var pattern reference):** https://github.com/AhmedMKhattab/AoUPRS — verified env-var names (`WORKSPACE_BUCKET`, `GOOGLE_PROJECT`, `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH`, `WGS_VDS_PATH`).
16. **PGS Catalog Calculator AoU integration docs:** https://pgsc-calc.readthedocs.io/en/latest/how-to/AOU.html — verified `gs://fc-aou-datasets-controlled/v7/...` dataset path family.
17. **`envs/ld_build.yml`** — convention reference for new `envs/m3-aou-dev.yml`, `envs/m3-r-ld.yml`.
18. **`src/snakemake/rules/m1_download.smk`** lines 46-62 — flag-driven download rule pattern.
19. **`tests/toy_3locus/data/ld_ref/*.rds`** — current EUR identity-placeholder LD; Wave 5 extends with AFR identity-placeholder.

### Priority 4 (READ ON-DEMAND)

20. **`CLAUDE.md`** — project rules; Snakemake/Python pin; LSF queue rules.
21. **`.planning/m2_post_m3_rerun_queue.tsv`** — 8 M2-supersede obligations (status updated at M3 close).
22. **`.planning/STATE.md`** — phase progression state.
23. **`.planning/DECISIONS.md`** — DEC-2026-04-22-04, DEC-2026-04-24-01, DEC-2026-04-24-02, DEC-2026-04-25-02.

### Priority 5 (REFERENCE LITERATURE)

24. **Locke et al. 2015** *Nature* — FTO 16q12 published AFR LD figures (Check 1 comparator).
25. **Teslovich et al. 2010** *Nature* — SORT1 1p13 published AFR LD figures (Check 1 comparator).
26. **Graham et al. 2021** *Nature* — GLGC-AFR lipids; published AFR-specific lead variants for the lipids regions (m2_region_00006, _00040, _00083 dev candidates).
27. **Wallace 2020** *PLoS Genet* / **Zou 2022** *Biostatistics* — SuSiE-RSS reference (Check 3 method).
28. **Bulik-Sullivan 2015** *Nat Genet* — LDSC; cross-reference for M2-supplementary AFR ld-score derivation.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | AoU Researcher Workbench supports Dataproc + Hail v0.2.x as standard image | spec §5; assumed available | Worse case: workbench supports a different Hail version (e.g., 0.2.130 vs 0.2.131 — backward-compatible per Hail SemVer); driver code still runs. Verify at Wave 1 first cluster fire. |
| A2 | The auxiliary path pattern `gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/` extends to ancestry preds (path inferred for `ancestry_preds.tsv` from confirmed relatedness path) | Q9 / O3 | Wave 1 first-cluster fire fails on ancestry table read; fix is a one-liner driver constant update |
| A3 | AoU export reviewers will rule "aggregate summary statistics" classification on variant×variant LD matrices from n ≥ 60k AFR | Hard Gate #6; spec §12 R1 | If ruling is "derived individual data" — pipeline cannot egress, M3 cannot land. Fallback per spec §12: "compute LD inside AoU and run SuSiE inside AoU, only exporting credible-set tables" — methodologically degraded but viable. **This is the single largest M3 risk and is NOT resolvable in code.** |
| A4 | The 30 % AFR variant-count drop figure (MAF 0.005 → 0.01) cited in spec §7.2 holds for AoU AFR specifically | Q10 | If drop > 50 %, Wave 2 dev-10 emits a Carter checkpoint; cap at MAF ≥ 0.005 export with size penalty |
| A5 | Hail BlockMatrix write to bucket + densify-at-NCSU works end-to-end at scale | Q5 Path A.3 | Untested at production region scale; Wave 2 dev fire MUST exercise this on the 2 HLA-stress regions |
| A6 | AoU v7 will not be deprecated during M3 execution timeline | O2 | If v8 lands mid-Wave-4, defer v8 re-run to supplementary phase |
| A7 | The published AFR LD figures for FTO + SORT1 are recoverable as comparator images for Check 1 | Validation Architecture Check 1 | If figures unrecoverable from published PDFs, Check 1 falls to "qualitative-block-pattern" rather than "quantitative-pixel-correlation" — degraded but acceptable |
| A8 | The reverse liftover chain `hg37ToHg38.over.chain.gz` is sourceable from UCSC | Q1 | If unavailable in usual location, sourceable from `data/external/liftover/` companion directory or NCBI; not blocking |
| A9 | `pyliftover` (Python) is available in `envs/m3-r-ld.yml` for region-flank coordinate liftover | Q1 | If not in conda-forge, pip-install is fine (already pip pattern in `envs/ld_build.yml`) |
| A10 | The `n1-highmem-16` × 4 worker Dataproc cluster spec from §11 is current AoU-supported instance type | spec §11 | GCP instance types deprecate occasionally; verify at Wave 1 cluster spin-up |
| A11 | SuSiE-RSS will converge against AoU AFR LD with the existing `config/susie_policy.yaml` settings | Validation Architecture Check 3 | If not, may need policy updates; flag as M4-supplementary if so |

---

## Sources

### Primary (HIGH confidence; verified live 2026-04-27)

- Hail v0.2 methods documentation — https://hail.is/docs/0.2/methods/genetics.html — `hl.ld_matrix`, `hl.sample_qc`, `hl.variant_qc`, `hl.split_multi_hts` API signatures + return types + parameter semantics
- AoU Genomic Data Organization (current) — https://support.researchallofus.org/hc/en-us/articles/29475228181908-How-the-All-of-Us-Genomic-data-are-organized — auxiliary path family + ACAF threshold callset organization
- AoUPRS GitHub library — https://github.com/AhmedMKhattab/AoUPRS — verbatim env var names: `WORKSPACE_BUCKET`, `GOOGLE_PROJECT`, `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH`, `WGS_VDS_PATH`; verbatim aux path: `gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/relatedness/relatedness_flagged_samples.tsv`
- PGS Catalog Calculator AoU integration — https://pgsc-calc.readthedocs.io/en/latest/how-to/AOU.html — `gs://fc-aou-datasets-controlled/v7/wgs/...` dataset path family; ACAF threshold v7.1 PLINK bed location
- Direct measurement of `results/regions/union_region_list.bed` — span distribution, per-chromosome region counts, dev-region candidate IDs (FTO 16q12 = m2_region_00067, etc.)

### Secondary (MEDIUM confidence; verified against official source)

- AoU Genomic Quality Report Feb 2022 — `ancestry_pred` field name + KING kinship convention — https://www.researchallofus.org/wp-content/themes/research-hub-wordpress-theme/media/2022/03/Feb2022_All_of_Us_Beta_Release_Genomic_Quality_Report.pdf
- AoU Genetic Ancestry paper PMC12049439 (2024) — six-class continental ancestry framework — https://pmc.ncbi.nlm.nih.gov/articles/PMC12049439/
- AoU VDS format support article — https://support.researchallofus.org/hc/en-us/articles/14927774297620-The-new-VariantDataset-VDS-format-for-All-of-Us-short-read-WGS-data
- AoU Smaller Callsets article — https://support.researchallofus.org/hc/en-us/articles/14929793660948-Smaller-Callsets-for-Analyzing-Short-Read-WGS-SNP-Indel-Data-with-Hail-MT-VCF-and-PLINK

### Tertiary (LOW confidence; flagged for Wave 1 first-fire verification)

- Inferred ancestry preds path: `gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv` (path-pattern inference; verified-on-arrival)
- AoU export per-batch size limit (no explicit number in public docs; Q4 estimate uses 50 GB recommended ceiling per bundle inferred from "reasonable batch" language in spec §7)

---

## Metadata

**Confidence breakdown:**
- Hail v0.2.x API: HIGH — verified live against canonical docs
- AoU env-var names: HIGH — verified against open-source library + spec
- Region span distribution (Q2 structural finding): HIGH — direct measurement
- Per-chromosome export bundle sizes (Q4): MEDIUM — extrapolation from spec anchor
- BlockMatrix OOM thresholds (Q5): MEDIUM — math verified; empirical scaling is Wave 2
- Validation Architecture pass thresholds: HIGH — directly inherited from spec §9
- Egress classification ruling outcome (Hard Gate #6): NOT in research scope — Carter human action
- AoU EUR cohort size estimates (~130-150k): MEDIUM — cited from spec; not enumerated against current CDR
- Open Issue O1 resolution (region width): UNRESOLVED — flagged for Carter checkpoint at Wave 0

**Research date:** 2026-04-27
**Valid until:** 2026-05-27 (30 days, stable; re-verify if AoU v8 lands or Hail releases a major version bump)
**Researcher:** gsd-phase-researcher
**Phase:** M3 / m3-aou-afr-ld-panel-build
