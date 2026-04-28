---
phase: m3-aou-afr-ld-panel-build
plan: 02
type: execute
wave: 2
depends_on: ["00", "01"]
files_modified:
  - .planning/notebooks/AOU-2_per_region_ld.ipynb
  - .planning/notebooks/AOU-4_validation.ipynb
  - data/interim/aou_ld_exports/AFR_aou/.touch_dev10
  - data/interim/aou_ld_exports/EUR_aou/.touch_dev10
  - tests/m3/test_validation_check_1_known_locus.py
  - tests/m3/test_validation_check_2_aou_eur_vs_1kg.py
  - tests/m3/test_validation_check_3_susie_convergence.py
  - tests/m3/test_validation_check_4_identity_ab.py
  - tests/m3/test_aou_export_landing.py
  - .planning/phases/m3-aou-afr-ld-panel-build/validation/check_1_known_locus_heatmaps/.gitkeep
  - .planning/phases/m3-aou-afr-ld-panel-build/validation/check_2_aou_eur_vs_1kg/.gitkeep
  - .planning/phases/m3-aou-afr-ld-panel-build/validation/check_3_susie_16q12_bmi_afr/.gitkeep
  - .planning/phases/m3-aou-afr-ld-panel-build/validation/check_4_identity_ab/.gitkeep
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md
  - m3_dev_complete.flag
autonomous: false
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-VALIDATION
  - REQ-AOU-LD-EGRESS
  - REQ-PUBLIC-DATA-ONLY

must_haves:
  truths:
    - "AOU-2 per-region LD notebook fires against config/ld_regions_dev.tsv (10 rows) and emits 10 .npz files into gs://${WORKSPACE_BUCKET}/ld/AFR_aou/ + 3 .npz into gs://${WORKSPACE_BUCKET}/ld/EUR_aou/ + 2 BlockMatrix-shard directories (HLA + 8p23 are Path A.3 per RESEARCH Q5 if region_class is large/xlarge)."
    - "Per-chromosome dev export bundle (1-2 chr at most for the 10 regions) lands on NCSU GPFS at data/interim/aou_ld_exports/{AFR_aou,EUR_aou}/ via AoU portal Notebooks/Files egress request — proves the egress pathway end-to-end on dev fixtures."
    - "Wave 3 .npz to .rds conversion and ld_panel: resolver wiring is NOT a Wave 2 task (it's Wave 3) — but Wave 2 produces the .rds outputs for the 10 dev regions via a bootstrap call to Wave 3's converter so Check 1+2+3+4 can run."
    - "Check 1 (known-locus LD pattern; FTO 16q12 + SORT1 1p13) emits heatmap PNG + invariants TSV; pass threshold = block boundaries within ±5 kb of published per AOU-LD-PIPELINE.md §9.1."
    - "Check 2 (AoU EUR vs 1000G EUR Pearson r) emits per-region pearson_r_by_maf_bin.tsv; mean r ≥ 0.97 for MAF ≥ 0.05 (RESEARCH Validation Architecture §)."
    - "Check 3 (SuSiE-RSS convergence on 16q12 BMI AFR) emits susie_fit.rds + summary.tsv; pass requires converged=TRUE, ≥1 CS at PIP 0.95, median CS size ≤ 30, lead PIP rs1558902 ≥ 0.1."
    - "Check 4 (AoU-AFR vs identity-placeholder A/B yield contrast) emits yield_table.tsv tabulating n_cs, median_cs_size, lead_pip per region per LD source — this is THE M3 headline figure."
    - "MAF drop sanity check: per-region n_var counts at MAF 0.005 vs 0.01 thresholds emitted to validation/check_4_identity_ab/maf_drop.tsv per RESEARCH Q10 — Wave 2 halts at Carter checkpoint if drop > 50% in any region."
    - "Carter manually reviews the 4 check outputs + sensitivity-cohort correlation table; signs and commits .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md (the validation memo, distinct from the Nyquist strategy doc m3-VALIDATION.md); touches m3_dev_complete.flag at project root."
  artifacts:
    - path: ".planning/notebooks/AOU-2_per_region_ld.ipynb"
      provides: "Per-region LD compute notebook driver consumed by Wave 2 dev fire AND Wave 4 production fire"
      min_lines: 50
    - path: ".planning/notebooks/AOU-4_validation.ipynb"
      provides: "R-kernel validation notebook running Checks 1-4 inside AoU on the 10 dev regions"
      min_lines: 80
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/validation/check_1_known_locus_heatmaps/"
      provides: "FTO 16q12 + SORT1 1p13 LD heatmap PNGs + check_1_invariants.tsv (block-boundary distances)"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/validation/check_2_aou_eur_vs_1kg/"
      provides: "Per-region pearson_r_by_maf_bin.tsv + check_2_summary.tsv (3 EUR-Track-A overlap regions)"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/validation/check_3_susie_16q12_bmi_afr/"
      provides: "susie_fit.rds + check_3_summary.tsv (converged, n_cs, median_cs_size, lead_pip)"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/validation/check_4_identity_ab/"
      provides: "yield_table.tsv (THE M3 headline figure) + maf_drop.tsv (RESEARCH Q10 sanity)"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md"
      provides: "4-check validation memo (consumed by Wave 5 OSF posting per D-M3-08)"
      contains: "Carter signoff"
    - path: "m3_dev_complete.flag"
      provides: "Snakemake target flag — required input to all Wave 4 production rules"
  key_links:
    - from: ".planning/notebooks/AOU-2_per_region_ld.ipynb"
      to: "src/python/aou_ld_panel.py"
      via: "from aou_ld_panel import compute_region_ld"
      pattern: "compute_region_ld"
    - from: ".planning/notebooks/AOU-4_validation.ipynb"
      to: "data/processed/ld_reference/{AFR_aou,EUR_aou}/*.rds"
      via: "Wave 3 converter run on the 10 dev .npz files (bootstrap)"
      pattern: "ld_reference/(AFR|EUR)_aou"
    - from: "m3-VALIDATION-MEMO.md"
      to: ".planning/phases/m3-aou-afr-ld-panel-build/validation/check_4_identity_ab/yield_table.tsv"
      via: "Embedded headline yield-contrast table"
      pattern: "yield_table"
---

<objective>
Wave 2 fires the 10-region dev panel inside AoU (1-2 cluster-hours wall clock; AFR + EUR), egresses the 13 .npz files (10 AFR + 3 EUR) plus 2 BlockMatrix-shard directories (HLA + 8p23 are likely Path A.3) to NCSU GPFS, runs the bootstrap .npz to .rds conversion using Wave 3's converter (called early — not yet wave-promoted), runs the 4-check validation protocol on the 10 dev regions, and ends with the Carter signoff that touches `m3_dev_complete.flag` to unblock Wave 4 production.

Purpose: This is the canonical promotion gate per AOU-LD-PIPELINE.md §9 + REQ-AOU-LD-VALIDATION + D-M3-03. No "we'll fix it in production" override — Wave 4 production fire (322 cells) literally cannot run without this flag.

Output: 4 validation-output directories with check-specific artifacts, the validation memo, the Carter signoff flag, and the 5 Wave 4 pytest scaffolds (test_validation_check_1..4 + test_aou_export_landing).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION.md
@.planning/amendments/AOU-LD-PIPELINE.md

<interfaces>
<!-- Wave 0 + Wave 1 deliverables that Wave 2 consumes. -->

src/python/aou_ld_panel.py exports (Wave 0):
- compute_region_ld(region_row: dict, mt_source: hl.MatrixTable, out_bucket: str) -> dict
  Path A.1 small: to_numpy() + np.savez_compressed
  Path A.2 medium: BlockMatrix.sparsify_triangle() + to_numpy() + savez
  Path A.3 large/xlarge: BlockMatrix.write(...) (densification deferred to NCSU)

config/ld_regions_dev.tsv (Wave 0; 10 rows):
- 5 AFR-only: m2_region_00006, _00027, _00067, _00040, _00083, plus 2 HLA + 8p23
- 3 EUR-only: m2_region_00067, _00040, _00083 (the EUR halves of overlap regions)

src/python/ld_panel.py::resolve_ld_path (Wave 0):
- Walks ld_panel: chain; returns first existing .rds path

3 checkpoint MTs in workspace bucket (Wave 1):
- gs://${WORKSPACE_BUCKET}/ld/mt_afr_qc.mt
- gs://${WORKSPACE_BUCKET}/ld/mt_afr_pca_selfid_qc.mt
- gs://${WORKSPACE_BUCKET}/ld/mt_eur_qc.mt

Validation Architecture pass thresholds (RESEARCH Validation Architecture §):
Check 1: visual block-boundary alignment + ≥0.85 pixel correlation (stretch goal)
Check 2: mean Pearson r ≥ 0.97 for MAF ≥ 0.05; secondary ≥ 0.90 for MAF 0.01-0.05
Check 3: converged=TRUE; ≥1 CS at PIP 0.95; median CS ≤ 30; lead rs1558902 PIP ≥ 0.1
Check 4: no hard threshold; expected direction = AoU LD > identity LD on n_cs / lead PIP

D-M3-03 Single-fire-after-dev gate:
m3_dev_complete.flag is touched ONLY after Carter signoff on m3-VALIDATION-MEMO.md.
Wave 4 production rules require m3_dev_complete.flag as input.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: AOU-2 per-region LD compute notebook (dev fire) + 13 .npz egress to GPFS</name>
  <files>.planning/notebooks/AOU-2_per_region_ld.ipynb, data/interim/aou_ld_exports/AFR_aou/.touch_dev10, data/interim/aou_ld_exports/EUR_aou/.touch_dev10</files>
  <read_first>
    - .planning/notebooks/AOU-1_template.ipynb (Wave 1 deliverable; cohort-definition pattern reference)
    - src/python/aou_ld_panel.py compute_region_ld() function (Wave 0)
    - .planning/amendments/AOU-LD-PIPELINE.md §5.1 lines 173-225 (per-region loop pattern) AND §7 (export protocol)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Q3 — AoU bucket vs Workbench Jupyter export semantics" (lines 191-199) AND "Q5 — Hail BlockMatrix block_size tuning" (lines 236-263)
    - config/ld_regions_dev.tsv (Wave 0; 10 dev rows)
  </read_first>
  <action>
    Create `.planning/notebooks/AOU-2_per_region_ld.ipynb` (8 cells; Carter mirrors into AoU workspace):

    Cell 1 (markdown): "# AOU-2 — Per-region LD compute. Phase M3 / Wave 2 dev fire OR Wave 4 production fire. Driven by config/ld_regions_dev.tsv (Wave 2; 10 rows) OR config/ld_regions.tsv (Wave 4; 322 rows). Selector: variable USE_DEV_SUBSET (True for Wave 2; False for Wave 4)."

    Cell 2 (code):
    ```python
    import os, sys, pandas as pd, hail as hl
    sys.path.insert(0, "/home/jupyter/coloc_analysis/src/python")
    from aou_ld_panel import init_hail, compute_region_ld
    init_hail()
    USE_DEV_SUBSET = True   # Wave 2; flip to False for Wave 4 production fire
    MANIFEST = "config/ld_regions_dev.tsv" if USE_DEV_SUBSET else "config/ld_regions.tsv"
    regions = pd.read_csv(MANIFEST, sep="\t")
    print(f"Loaded {len(regions)} region rows from {MANIFEST}")
    ```

    Cell 3 (code) — Load checkpoint MTs:
    ```python
    mt_afr = hl.read_matrix_table(f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_afr_qc.mt")
    mt_eur = hl.read_matrix_table(f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/mt_eur_qc.mt")
    print(f"AFR MT: {mt_afr.count_cols()} samples; EUR MT: {mt_eur.count_cols()} samples")
    ```

    Cell 4 (code) — Drive per-region LD compute:
    ```python
    OUT_BUCKET_AFR = f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/AFR_aou"
    OUT_BUCKET_EUR = f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/EUR_aou"
    results = []
    for r in regions.itertuples(index=False):
        row = r._asdict()
        mt_source = mt_afr if row["ancestry"] == "AFR" else mt_eur
        out_bucket = OUT_BUCKET_AFR if row["ancestry"] == "AFR" else OUT_BUCKET_EUR
        result = compute_region_ld(row, mt_source, out_bucket)
        results.append(result)
        print(f"{row['region_id']}/{row['ancestry']}: {result['status']} n_var={result.get('n_var', 'NA')}")
    pd.DataFrame(results).to_csv("ld_run_log_dev.tsv" if USE_DEV_SUBSET else "ld_run_log_prod.tsv", sep="\t", index=False)
    ```

    Cell 5 (markdown): "## Egress (per-chromosome bundle requests via AoU portal Notebooks/Files UI per Q3). For Wave 2 dev fire (10 regions, 1-2 chromosomes), file 1-2 export requests; for Wave 4 production (44 bundles), 22 chr × 2 ancestries."

    Cell 6 (code) — Per-chromosome bundle landing inventory:
    ```python
    chr_summary = pd.DataFrame(results).groupby(["ancestry", "chr"]).agg(
        n_regions=("region_id", "count"),
        sizes_listed_in_bucket=("status", lambda s: f"{(s == 'ok').sum()} of {len(s)} ok"),
    ).reset_index()
    chr_summary.to_csv("egress_bundles_dev.tsv" if USE_DEV_SUBSET else "egress_bundles_prod.tsv", sep="\t", index=False)
    print(chr_summary)
    ```

    Cell 7 (markdown): "## NEXT (human action): Carter files egress request via AoU Workbench Notebooks/Files UI for `gs://${WORKSPACE_BUCKET}/ld/{AFR_aou,EUR_aou}/`. AoU returns export request IDs (capture; will be appended to .planning/amendments/aou-egress-audit-log.md per Q12 schema during Wave 4 production fire). For Wave 2 dev fire, this is 1-2 export requests; for Wave 4 production, 44 export requests bundled per chromosome × ancestry."

    Cell 8 (markdown): "## Land .npz files at NCSU GPFS data/interim/aou_ld_exports/{AFR_aou,EUR_aou}/ via AoU egress download (gsutil cp from approved bucket path on NCSU side once AoU release ID received)."

    ALSO create empty marker files:
    - `data/interim/aou_ld_exports/AFR_aou/.touch_dev10` (zero-byte; gitignored — git would not track contents but the directory existence is required by Wave 3 ingest rules)
    - `data/interim/aou_ld_exports/EUR_aou/.touch_dev10` (zero-byte; ditto)

    These are placeholder .touch_dev10 files. Carter creates the actual .npz files via the egress download cell — once AoU has approved the dev bundle and Carter runs `gsutil cp gs://${WORKSPACE_BUCKET}/ld/AFR_aou/*.npz data/interim/aou_ld_exports/AFR_aou/`. Snakemake then unblocks Wave 3 conversion when the .npz files appear.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; python -c "import json; nb=json.load(open('.planning/notebooks/AOU-2_per_region_ld.ipynb')); assert len(nb['cells']) >= 8; print('OK')" &amp;&amp; test -d data/interim/aou_ld_exports/AFR_aou &amp;&amp; test -d data/interim/aou_ld_exports/EUR_aou</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .planning/notebooks/AOU-2_per_region_ld.ipynb` exits 0.
    - `python -c "import json; nb=json.load(open('.planning/notebooks/AOU-2_per_region_ld.ipynb')); assert len(nb['cells']) >= 8" && echo OK` prints OK.
    - `grep -c "USE_DEV_SUBSET" .planning/notebooks/AOU-2_per_region_ld.ipynb` returns ≥ 2 (selector flag).
    - `grep -c "compute_region_ld" .planning/notebooks/AOU-2_per_region_ld.ipynb` returns ≥ 1.
    - `grep -c "config/ld_regions_dev.tsv" .planning/notebooks/AOU-2_per_region_ld.ipynb` returns ≥ 1.
    - `grep -c "config/ld_regions.tsv" .planning/notebooks/AOU-2_per_region_ld.ipynb` returns ≥ 1 (Wave 4 selector path).
    - `test -d data/interim/aou_ld_exports/AFR_aou && test -d data/interim/aou_ld_exports/EUR_aou` exits 0.
    - `test -f data/interim/aou_ld_exports/AFR_aou/.touch_dev10 && test -f data/interim/aou_ld_exports/EUR_aou/.touch_dev10` exits 0.
  </acceptance_criteria>
  <done>
    AOU-2 notebook lands; Carter mirrors into AoU workspace; fires dev-10 region LD compute (1-2 cluster-hours wall clock; ~$10-20 in credits per RESEARCH cost analysis). 10 .npz files (AFR_aou) + 3 .npz files (EUR_aou) + 2 BlockMatrix-shard directories (HLA + 8p23 if region_class is large/xlarge per Wave 0 manifest) land in workspace bucket. Carter files 1-2 AoU egress requests for the dev bundles; AoU approves; Carter `gsutil cp`s the .npz files into data/interim/aou_ld_exports/{AFR_aou,EUR_aou}/.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: 4-check validation harness — AOU-4 notebook + 5 pytest scaffolds + check outputs</name>
  <files>.planning/notebooks/AOU-4_validation.ipynb, tests/m3/test_validation_check_1_known_locus.py, tests/m3/test_validation_check_2_aou_eur_vs_1kg.py, tests/m3/test_validation_check_3_susie_convergence.py, tests/m3/test_validation_check_4_identity_ab.py, tests/m3/test_aou_export_landing.py, .planning/phases/m3-aou-afr-ld-panel-build/validation/check_1_known_locus_heatmaps/.gitkeep, .planning/phases/m3-aou-afr-ld-panel-build/validation/check_2_aou_eur_vs_1kg/.gitkeep, .planning/phases/m3-aou-afr-ld-panel-build/validation/check_3_susie_16q12_bmi_afr/.gitkeep, .planning/phases/m3-aou-afr-ld-panel-build/validation/check_4_identity_ab/.gitkeep</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Validation Architecture > The 4-Check Validation Protocol — Formalized Pass Thresholds" (lines 519-550) — verbatim Check 1+2+3+4 spec
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION.md (Nyquist contract; per-task verification map)
    - .planning/amendments/AOU-LD-PIPELINE.md §9 (lines 399-426) — original 4-check protocol source
    - data/processed/ld_reference/EUR/*.rds — existing Track A 1000G EUR LD substrate (Check 2 comparator)
    - tests/m3/conftest.py (Wave 0; shared fixtures)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Q10 — MAF lower bound for export vs internal" (lines 403-411) — MAF drop check belongs in Check 4 maf_drop.tsv
  </read_first>
  <behavior>
    - test_check_1_block_boundary_invariants: Check 1 invariants TSV has columns {region_id, block_start_kb, block_end_kb, distance_to_published_kb}; assert |distance| <= 5 for FTO + SORT1.
    - test_check_2_pearson_correlation: parse pearson_r_by_maf_bin.tsv; assert mean r >= 0.97 for MAF >= 0.05 bin in each of the 3 EUR-Track-A overlap regions.
    - test_check_3_susie_convergence: parse check_3_summary.tsv; assert converged==True, n_cs >= 1, median_cs_size <= 30, lead_pip >= 0.1 for FTO 16q12 BMI AFR row.
    - test_check_4_yield_contrast: parse yield_table.tsv; assert at least 5 of 7 AFR regions show mean(AoU LD lead PIP) > mean(identity LD lead PIP); per-region n_cs and median_cs_size populated.
    - test_check_4_maf_drop: parse maf_drop.tsv; assert max(per-region drop ratio) <= 0.50 (per RESEARCH Q10 halt threshold).
    - test_aou_export_landing: verify expected .npz file count per chromosome under data/interim/aou_ld_exports/{AFR_aou,EUR_aou}/ matches egress_bundles_dev.tsv from Task 1.
  </behavior>
  <action>
    1. Create `.planning/notebooks/AOU-4_validation.ipynb` (R-kernel notebook OR Python with reticulate; 12+ cells). Carter mirrors into AoU workspace. Cells:
       - Cell 1 (md): "# AOU-4 — 4-check validation harness. RESEARCH Validation Architecture §. Inputs: 13 .npz files in workspace bucket (Wave 2 dev fire output). Outputs: 4 validation-output directories at .planning/phases/m3-aou-afr-ld-panel-build/validation/."
       - Cells 2-4 (Check 1 — known-locus LD pattern): for FTO 16q12 (m2_region_00067) and SORT1 1p13 (m2_region_00006), render LD heatmap PNG via R `Matrix` + `lattice::levelplot()`; compute LD-block boundaries via `LDheatmap::LDheatmap` boundary detection; emit `check_1_invariants.tsv` with `{region_id, block_start_kb, block_end_kb, distance_to_published_kb}`. Published reference loci: FTO rs1558902 ±500 kb (Locke 2015), SORT1 rs12740374 ±500 kb (Teslovich 2010).
       - Cells 5-6 (Check 2 — AoU EUR vs 1000G EUR): for each of m2_region_00067, _00040, _00083, load AoU EUR LD `.rds` AND 1000G EUR LD `.rds` from `data/processed/ld_reference/EUR/{FTO_16q12,SH2B3_12q24,APOE_19q13}.rds` (consult Wave 0 region_id_mapping.tsv); align variants on intersect; compute entry-wise Pearson r per MAF bin {<0.01, 0.01-0.05, ≥0.05}; emit per-region `pearson_r_by_maf_bin.tsv` and aggregated `check_2_summary.tsv`.
       - Cells 7-8 (Check 3 — SuSiE-RSS on 16q12 BMI AFR): load AoU AFR LD for m2_region_00067; load published BMI AFR sumstats (PAGE 2017 Graff et al.; pre-existing under data/processed/sumstats/bmi/AFR/); run `susieR::susie_rss()` with `L=10`, `min_abs_corr=0.5` per `config/susie_policy.yaml`; emit `susie_fit.rds` + `check_3_summary.tsv` row `{converged, n_cs, median_cs_size, lead_pip_rs1558902}`.
       - Cells 9-10 (Check 4 — A/B yield contrast): for each of 7 AFR regions (5 AFR-known + 2 HLA-stress), run SuSiE-RSS twice — once with AoU AFR LD, once with identity-placeholder LD (from `tests/toy_3locus/data/ld_ref/*.rds` family); tabulate per-region `{ancestry, region_id, n_cs, median_cs_size, lead_pip, converged, ld_source}`; emit `yield_table.tsv`. ALSO emit `maf_drop.tsv` with per-region n_var counts at MAF 0.005 vs 0.01 thresholds.
       - Cells 11-12 (Sensitivity-cohort correlation): for the 5 AFR-known dev regions, compute Pearson r between LD computed from `mt_afr_qc.mt` (PCA-only) and LD from `mt_afr_pca_selfid_qc.mt` (PCA + self-id Black/AA); emit `validation/sensitivity_cohort_r.tsv`. Per D-M3-07: if r > 0.995 at all 10 lead loci, the validation memo records "PCA-only sufficient for production"; if not, document and decide.

    2. Write `tests/m3/test_validation_check_1_known_locus.py`. Use a synthetic invariants TSV fixture (3 rows; FTO + SORT1 + a deliberate failure case); assert pandas-loaded df satisfies `abs(distance_to_published_kb) <= 5` for FTO + SORT1 rows.

    3. Write `tests/m3/test_validation_check_2_aou_eur_vs_1kg.py`. Use a synthetic per-region pearson TSV fixture (3 regions × 3 MAF bins); assert `mean_r >= 0.97` for `maf_bin == "ge_0.05"` in each region.

    4. Write `tests/m3/test_validation_check_3_susie_convergence.py`. Use a synthetic check_3_summary.tsv fixture; assert `converged == True`, `n_cs >= 1`, `median_cs_size <= 30`, `lead_pip >= 0.1`.

    5. Write `tests/m3/test_validation_check_4_identity_ab.py`. Use a synthetic yield_table.tsv fixture (7 regions × 2 LD sources = 14 rows); assert "AoU LD lead PIP > identity LD lead PIP" for ≥ 5 of 7 regions per RESEARCH Validation Architecture soft expectation.

    6. Write `tests/m3/test_aou_export_landing.py`. Mock `data/interim/aou_ld_exports/AFR_aou/` with synthetic `.npz` files (use `np.savez_compressed` on small random matrices); verify the directory structure matches Q12 expectations (per-chromosome bundling); assert at least 1 chr with at least 1 region.

    7. Touch `.gitkeep` files in 4 validation subdirectories so the directory structure is git-trackable.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_validation_check_1_known_locus.py tests/m3/test_validation_check_2_aou_eur_vs_1kg.py tests/m3/test_validation_check_3_susie_convergence.py tests/m3/test_validation_check_4_identity_ab.py tests/m3/test_aou_export_landing.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `python -c "import json; nb=json.load(open('.planning/notebooks/AOU-4_validation.ipynb')); assert len(nb['cells']) >= 12"` exits 0.
    - `grep -c "susie_rss\\|susie\\.rss\\|hyprcoloc" .planning/notebooks/AOU-4_validation.ipynb` returns ≥ 1 (Check 3 fires SuSiE-RSS).
    - `grep -c "rs1558902" .planning/notebooks/AOU-4_validation.ipynb` returns ≥ 1 (Check 1 + Check 3 reference variant).
    - `grep -c "rs12740374" .planning/notebooks/AOU-4_validation.ipynb` returns ≥ 1 (Check 1 SORT1 lead).
    - `grep -c "maf_drop.tsv" .planning/notebooks/AOU-4_validation.ipynb` returns ≥ 1 (RESEARCH Q10 sanity).
    - `pytest tests/m3/test_validation_check_*.py tests/m3/test_aou_export_landing.py -v` reports ≥ 5 passed with exit 0.
    - 4 `.gitkeep` files exist under `.planning/phases/m3-aou-afr-ld-panel-build/validation/`.
    - `grep -c "sensitivity" .planning/notebooks/AOU-4_validation.ipynb` returns ≥ 1 (D-M3-07 sensitivity-cohort correlation cells).
  </acceptance_criteria>
  <done>
    AOU-4 validation notebook lands; Carter mirrors + fires inside AoU. 4-check outputs land at .planning/phases/m3-aou-afr-ld-panel-build/validation/check_{1,2,3,4}/. 5 pytest scaffolds pass against synthetic fixtures (no AoU access required for the unit tests). REQ-AOU-LD-VALIDATION pre-conditions ready for Carter signoff at Task 3.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 3: Carter signoff on m3-VALIDATION-MEMO.md + touch m3_dev_complete.flag (D-M3-03 dev to production gate)</name>
  <files>.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md, m3_dev_complete.flag</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/validation/check_1_known_locus_heatmaps/* (Task 2 output)
    - .planning/phases/m3-aou-afr-ld-panel-build/validation/check_2_aou_eur_vs_1kg/* (Task 2 output)
    - .planning/phases/m3-aou-afr-ld-panel-build/validation/check_3_susie_16q12_bmi_afr/* (Task 2 output)
    - .planning/phases/m3-aou-afr-ld-panel-build/validation/check_4_identity_ab/yield_table.tsv (Task 2 output) AND maf_drop.tsv
    - .planning/phases/m3-aou-afr-ld-panel-build/validation/sensitivity_cohort_r.tsv (Task 2 output; D-M3-07 evidence)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md decision D-M3-03 (single-fire gate)
    - .planning/amendments/AOU-LD-PIPELINE.md §9 + §15 Q8 (validation memo external review = OSF deposit per D-M3-08)
  </read_first>
  <action>See &lt;human_gate&gt; block. This task is a Carter human-action checkpoint; no agent action. The agent's role is to verify acceptance_criteria after Carter completes the gate.</action>
  <human_gate>
    <gate>4-check validation memo signoff + Wave 4 production unblock flag</gate>
    <description>
      Carter reviews the 4 check outputs + the sensitivity-cohort correlation table + the MAF drop table; writes the validation memo at `.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` (10-15 pages of structured Markdown — distinct from the Nyquist strategy doc m3-VALIDATION.md). The memo MUST contain:

      Section 1 — Summary: per-check pass/fail summary with data tables.

      Section 2 — Check 1: FTO + SORT1 LD heatmap visual review. Carter must compare AoU heatmaps against published Locke 2015 / Teslovich 2010 panels (PDF / image references). Block-boundary distance documented per region.

      Section 3 — Check 2: per-region Pearson r table at MAF ≥ 0.05 (must be ≥ 0.97 per region; if any region < 0.97, document — does NOT auto-block per RESEARCH Validation Architecture).

      Section 4 — Check 3: SuSiE-RSS converged on FTO 16q12 BMI AFR; n_cs, median CS size, lead PIP rs1558902 — all four pass thresholds met (or documented if not).

      Section 5 — Check 4: yield contrast table (5 AFR-known + 2 HLA-stress regions × 2 LD sources). The headline number: how many regions show AoU AFR LD > identity LD on n_cs / lead PIP / median CS size?

      Section 6 — Sensitivity-cohort correlation (D-M3-07): per-locus correlation between PCA-only AFR LD and PCA + self-id AFR LD. If r > 0.995 at all 10 lead loci, "PCA-only sufficient for production"; if not, document.

      Section 7 — MAF drop sanity check (RESEARCH Q10): per-region n_var at MAF 0.005 vs 0.01. If max drop > 50%, halt.

      Section 8 — Cost & timing: actual cluster-hours used; .npz bundle sizes per chromosome; approximate AoU credit consumption.

      Section 9 — Carter signoff statement: "I, Carter Clinton, sign off on the 4-check validation; Wave 4 production fire (322 cells) is unblocked. Path A.1/A.2/A.3 region-class branches per Wave 0 D-M3-09 ruling are accepted. Date: YYYY-MM-DD."

      After memo committed, touch `m3_dev_complete.flag` at project root with `touch m3_dev_complete.flag` and commit it (this is the Snakemake target flag that gates Wave 4 production rules).
    </description>
    <unblocks>Wave 4 m3-04-W4-production-and-egress-PLAN.md production fire (322 cells)</unblocks>
    <how-to-resolve>
      1. Review .planning/phases/m3-aou-afr-ld-panel-build/validation/check_{1,2,3,4}/* outputs (heatmaps + TSVs).
      2. Compare Check 1 heatmaps against published Locke 2015 + Teslovich 2010 panels — visual sanity check.
      3. If any check fails the threshold from RESEARCH Validation Architecture: halt, diagnose, document the diagnostic outcome, decide whether to proceed (per RESEARCH Check 2 R4 risk: discrepant MAF 0.01-0.05 acceptable; ≥ 2 of 3 regions discrepant at MAF ≥ 0.05 = halt).
      4. Write m3-VALIDATION-MEMO.md per the 9-section structure above.
      5. `touch m3_dev_complete.flag`; commit both files with token `(m3-W2-T3)` in subject.
      6. Type "approved" to resume; Wave 4 unblocked.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f m3_dev_complete.flag &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md &amp;&amp; grep -c "Carter Clinton" .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md</automated>
  </verify>
  <acceptance_criteria>
    - `test -f m3_dev_complete.flag` exits 0 (project-root flag exists).
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` exits 0.
    - `wc -l .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` returns ≥ 100 (10+ pages of structured Markdown).
    - `grep -c "Section 9.*signoff\\|Carter Clinton" .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` returns ≥ 1.
    - `grep -c "Check 1\\|Check 2\\|Check 3\\|Check 4" .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` returns ≥ 4.
    - `grep -c "D-M3-09" .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` returns ≥ 1 (references the Wave 0 Carter ruling).
    - `grep -c "rs1558902" .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` returns ≥ 1 (Check 3 lead variant).
    - Git log shows a commit with `(m3-W2-T3)` token in the subject line.
  </acceptance_criteria>
  <done>
    Validation memo committed with Carter signoff. m3_dev_complete.flag touched. Wave 4 production fire is now unblocked. The OSF posting trail (D-M3-08; Wave 5) consumes this memo verbatim.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| AoU workspace ↔ NCSU GPFS | First boundary crossing — 13 .npz files (10 AFR + 3 EUR) and 2 BlockMatrix-shard directories cross from AoU to NCSU via the approved egress mechanism. Audit log records 1-2 dev-fire export request IDs. |
| Validation outputs ↔ OSF amendment trail | m3-VALIDATION-MEMO.md is the artifact that Wave 5 posts to osf.io/az52u (D-M3-08 form). Public-summary-only by construction (4-check outputs are aggregate-LD-statistics tables). |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M3-EGR-W2 | Information disclosure | First .npz egress from AoU to NCSU GPFS | mitigate | Egress goes through AoU portal Notebooks/Files UI per Q3 (NOT bypassed); AoU-issued export request ID captured; the HARD GATE classification ruling from Wave 1 governs; per-cell suppression-floor argument trivially clears (each LD entry computed from n ≥ 60k AFR or n ≥ 130k EUR). |
| T-M3-S2-W2 | Reproducibility / provenance | Validation memo Carter signoff | mitigate | Memo records all 4 check thresholds + actual values + the 9-section structure (verifiable by grep). Carter signoff line + ISO date locked. m3_dev_complete.flag is git-tracked + commit token (m3-W2-T3) audit. |
| T-M3-AUTH-W2 | Authorization | Wave 4 production fire gating on m3_dev_complete.flag | mitigate | Wave 4 Snakemake rules MUST take this flag as input (encoded in Wave 4 plan). No "we'll fix it in production" override possible without Carter touching the flag. |
| T-M3-EGR-VAL | Information disclosure | Check 2 published-panel comparator | accept | The 1000G EUR Phase 3 LD substrate at data/processed/ld_reference/EUR/*.rds is fully public (1000G); no AoU-derived data in the Check 2 reference panel. |
</threat_model>

<verification>
**Wave 2 phase-level checks:**

1. `pytest tests/m3 -x --tb=short` passes (all 8 tests now: 3 from W0 + 5 from W2).
2. `test -f m3_dev_complete.flag` exits 0.
3. `wc -l .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` ≥ 100.
4. `grep -c "Section 9" .planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION-MEMO.md` ≥ 1.
5. 4 .gitkeep files exist under validation/ (verifiable: `find .planning/phases/m3-aou-afr-ld-panel-build/validation/ -name .gitkeep | wc -l` returns 4).
6. AoU dev-fire egress request IDs captured in m3-VALIDATION-MEMO.md (≥ 1 mention of "AoU-EXPORT-").
</verification>

<success_criteria>
- AOU-2 per-region LD compute notebook lands; Carter mirrors + fires dev-10 in AoU.
- AOU-4 validation notebook lands; 4 check outputs emitted under .planning/phases/m3-aou-afr-ld-panel-build/validation/.
- 5 pytest scaffolds (Check 1+2+3+4 + aou_export_landing) pass on synthetic fixtures.
- m3-VALIDATION-MEMO.md committed with Carter signoff (Section 9 + ISO date).
- m3_dev_complete.flag touched at project root.
- D-M3-07 sensitivity check evidence in memo (PCA-only sufficient OR documented otherwise).
- RESEARCH Q10 MAF drop check evidence in memo (no region drops > 50%).
- Wave 4 production fire is unblocked.
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-02-W2-dev-fire-and-validation-SUMMARY.md` recording:
- Dev-fire 13 cells timing (cluster-hours used)
- Per-check pass/fail outcome with key numbers
- Carter signoff date
- AoU credit balance after dev fire
- Surprises, if any (e.g., regions that needed Path A.3 unexpectedly; MAF drops)
</output>
