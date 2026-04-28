---
phase: m3-aou-afr-ld-panel-build
plan: 00
type: execute
wave: 0
depends_on: []
files_modified:
  - config/ld_regions.tsv
  - config/ld_regions_dev.tsv
  - config/pipeline.yaml
  - config/region_id_mapping.tsv
  - envs/m3-aou-dev.yml
  - envs/m3-r-ld.yml
  - src/python/build_ld_region_manifest.py
  - src/python/select_ld_regions_dev.py
  - src/python/ld_panel.py
  - src/python/aou_ld_panel.py
  - tests/m3/conftest.py
  - tests/m3/test_build_ld_region_manifest.py
  - tests/m3/test_ld_panel_resolver.py
  - tests/m3/test_aou_ld_panel_local.py
  - tests/m3/fixtures/build_synthetic_mt.py
  - .planning/amendments/aou-egress-audit-log.md
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
  - .planning/ROADMAP.md
  - .gitignore
autonomous: false
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI
  - REQ-PATH-PARAMETERIZATION

must_haves:
  truths:
    - "M2 union BED (161 GRCh37 regions) is reformatted into a 322-row (region times ancestry) GRCh38-native manifest with per-region radius (D-M3-02; RESEARCH Q1+Q2)."
    - "10-region dev subset is deterministically selected per D-M3-04 spec default with 3 EUR-Track-A overlap regions matching m2_region_00067/_00040/_00083 per RESEARCH Q11 overlap design."
    - "ld_panel: resolver in config/pipeline.yaml provides ordered fallback chains for AFR / EUR / TRANS plus pin override and strict_aou_only mode (D-M3-05; RESEARCH Q7)."
    - "envs/m3-aou-dev.yml pins python=3.11 + hail==0.2.x + pyspark + google-cloud-storage + pyliftover + pytest, matching CLAUDE.md Snakemake/Python pin (D-M3-06)."
    - "envs/m3-r-ld.yml pins python=3.11 + R 4.4 + reticulate + Matrix + testthat for the .npz to .rds converter."
    - "Hail driver src/python/aou_ld_panel.py uses corrected ordering (split_multi_hts BEFORE variant_qc per RESEARCH Hail API verification) and verified env-var names WORKSPACE_BUCKET / GOOGLE_PROJECT / WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH (RESEARCH Q9), with relatedness path hardcoded under gs://fc-aou-datasets-controlled/v7/.../aux/relatedness/relatedness_flagged_samples.tsv (NOT an env var)."
    - "Synthetic MT fixture (~100 samples × ~1500 variants × 2 chromosomes chr16+chr6) generated locally and exercises every Hail call path (RESEARCH Q6); pytest tests/m3 -x passes against it."
    - "Open Issue O1 (region-width acceptance) is logged as Carter ruling D-M3-09 in m3-CONTEXT.md before any AoU compute fires."
    - ".planning/amendments/aou-egress-audit-log.md is seeded with Q12 schema header and the Hard-Gate Egress Classification Ruling row (placeholder until Wave 1 Carter action lands the actual ruling)."
    - "ROADMAP.md M3 entry wording is updated per D-M3-01 to drop '+ UKB' from the parity description."
  artifacts:
    - path: "config/ld_regions.tsv"
      provides: "322-row region-times-ancestry manifest in AOU LD-PIPELINE §6 schema with start_grch37/end_grch37/start_grch38/end_grch38/radius_bp/region_class/liftover_status"
      min_lines: 323
    - path: "config/ld_regions_dev.tsv"
      provides: "10-row dev subset (3 EUR-Track-A overlap + 5 AFR-known + 2 HLA-stress)"
      min_lines: 11
    - path: "config/pipeline.yaml"
      provides: "ld_panel: block with AFR / EUR / TRANS chains, pin override, strict_aou_only flag"
      contains: "ld_panel:"
    - path: "envs/m3-aou-dev.yml"
      provides: "Local Hail dev env (python=3.11, hail==0.2.x, pyspark, google-cloud-storage, pyliftover, pytest)"
      contains: "hail"
    - path: "envs/m3-r-ld.yml"
      provides: ".npz to .rds R env (R 4.4, reticulate, Matrix, testthat)"
      contains: "reticulate"
    - path: "src/python/build_ld_region_manifest.py"
      provides: "GRCh37 to GRCh38 liftover + per-region radius_bp computation + region_class derivation; emits 322-row TSV"
    - path: "src/python/select_ld_regions_dev.py"
      provides: "Deterministic 10-region dev subset selector (D-M3-04 + RESEARCH Q11 overlap design)"
    - path: "src/python/ld_panel.py"
      provides: "resolve_ld_path(region_id, ancestry, config) helper consumed by finemap.smk (RESEARCH Q7)"
      exports: ["resolve_ld_path"]
    - path: "src/python/aou_ld_panel.py"
      provides: "Hail driver (cohort-define + per-region LD compute) — runs INSIDE AoU Workbench AND locally against synthetic MT"
    - path: "tests/m3/conftest.py"
      provides: "Shared pytest fixtures (synthetic MT loader, region manifest factory, mock AoU env vars)"
    - path: "tests/m3/test_build_ld_region_manifest.py"
      provides: "Unit test of liftover + radius + region_class invariants"
    - path: "tests/m3/test_ld_panel_resolver.py"
      provides: "Unit test of resolver fallback chain, pin override, strict mode"
    - path: "tests/m3/test_aou_ld_panel_local.py"
      provides: "Unit test of Hail driver against synthetic MT"
    - path: ".planning/amendments/aou-egress-audit-log.md"
      provides: "Append-only egress audit log seed with Q12 schema + classification-ruling header"
      contains: "Egress Classification Ruling (HARD GATE)"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv"
      provides: "Per-region span + region_class + path A.1/A.2/A.3 cost projection (consumed by Carter at O1 ruling task)"
  key_links:
    - from: "src/python/build_ld_region_manifest.py"
      to: "results/regions/union_region_list.bed"
      via: "pandas read_csv with sep=tab and 8-column GRCh37 schema"
      pattern: "results/regions/union_region_list.bed"
    - from: "src/python/build_ld_region_manifest.py"
      to: "data/external/liftover/hg19ToHg38.over.chain.gz"
      via: "pyliftover for GRCh37 to GRCh38 region-flank liftover"
      pattern: "pyliftover|LiftOver"
    - from: "src/python/ld_panel.py::resolve_ld_path"
      to: "config/pipeline.yaml ld_panel: block"
      via: "config['ld_panel'][ancestry] fallback walk"
      pattern: "config\\[.ld_panel.\\]"
    - from: "tests/m3/test_aou_ld_panel_local.py"
      to: "tests/m3/fixtures/build_synthetic_mt.py"
      via: "pytest fixture lazy-builds synthetic_aou.mt"
      pattern: "synthetic_aou\\.mt"
---

<objective>
Wave 0 lays the entire NCSU-side foundation for M3 BEFORE any AoU Dataproc spend: the region manifest reformatter (with the structural per-region radius fix from RESEARCH.md Q2), the dev-subset selector (D-M3-04 + Q11 overlap design), the ld_panel: resolver + config block (Q7), the two conda envs (D-M3-06), the Hail driver (locally testable against a synthetic MT — Q6), the four pytest scaffolds, the egress audit log seed (Q12), the ROADMAP wording fix (D-M3-01), the .gitignore additions, AND a Carter human-action gate to rule on Open Issue O1 (region-width acceptance) and log the ruling as D-M3-09.

Purpose: De-risk Wave 1+ AoU compute by catching every code-level pipeline bug locally on a 100-sample synthetic MT, surfacing the 161-region span distribution + cost projection to Carter for explicit O1 ruling, and ensuring the resolver + config wiring is unit-tested before any production rule consumes it.

Output: 14 source files, 5 config/governance/docs files, 1 region-class projection TSV, 1 D-M3-09 ruling row appended to m3-CONTEXT.md, plus all 4 Wave 0 pytest tests passing on synthetic MT in <=30 s.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION.md
@.planning/amendments/AOU-LD-PIPELINE.md

<interfaces>
<!-- Patterns the executor must match. Extracted from codebase 2026-04-27. -->

config/pipeline.yaml lines 21-52 (paths: block) layout reference:
```yaml
paths:
  ld_reference: "data/processed/ld_reference"
  finemap_output: "results/fine_mapping"
```

config/pipeline.yaml lines 161-196 (existing ld_reference: + finemap: blocks) — ld_panel: gets inserted as sibling AFTER line 196:
```yaml
ld_reference:
  EUR_source: "ukbb_ld_tiled"
  AFR_source: "hgdp_1kg_afr"

finemap:
  ld_reference_dir: "data/processed/ld_reference"
```

results/regions/union_region_list.bed is M2 deliverable (161 rows, tab-separated, NO header):
```
chr  start  end  region_id  score=.  strand=.  provenance_json  lead_token(optional)
```
(GRCh37 coordinates per DEC-2026-04-24-01.)

provenance_json schema (per M2 D-M2-09):
```json
{"sources": ["clump", "mtag", "cpassoc"], "ancestries": ["EUR", "AFR", "TRANS"], "traits": ["bmi", "hypertension"]}
```

src/snakemake/rules/ld_reference.smk top-of-file conda-env workaround pattern:
```python
LD_BUILD_ENV = str(Path(workflow.basedir) / "envs" / "ld_build.yml")
```

envs/ld_build.yml (channel + python=3.11 reference for new env yamls):
```yaml
name: ld_build
channels:
  - conda-forge
  - bioconda
dependencies:
  - python=3.11
```

Hail v0.2.x verified APIs (RESEARCH §"Hail v0.2.x API Verification"):
```python
hl.ld_matrix(entry_expr=Float64Expression, locus_expr=LocusExpression, radius=int_bp, coord_expr=None, block_size=None) -> BlockMatrix
hl.sample_qc(mt, name='sqc') -> MatrixTable           # output struct: call_rate, n_called, r_het_hom_var
hl.variant_qc(mt, name='vqc') -> MatrixTable          # output struct: AF (array), call_rate, p_value_hwe
hl.split_multi_hts(ds, keep_star=False) -> MatrixTable
```

Verified AoU env vars (RESEARCH Q9):
- WORKSPACE_BUCKET (workspace egress staging)
- GOOGLE_PROJECT (billing)
- WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH (AoU-provided ACAF MT path)

Hardcoded AoU auxiliary paths (NOT env vars; pin to CDR version):
- gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/relatedness/relatedness_flagged_samples.tsv
- gs://fc-aou-datasets-controlled/v7/wgs/short_read/snpindel/aux/ancestry/ancestry_preds.tsv  (INFERRED — Wave 1 first-fire verification)

Region radius algorithm (RESEARCH Q2):
```
radius_bp = (end_grch38 - start_grch38) + 500_000
radius_bp = min(radius_bp, 50_000_000)
region_class = "small"  if span_mb <= 5  else
               "medium" if span_mb <= 25 else
               "large"  if span_mb <= 50 else
               "xlarge"
```

Canonical Hail driver ordering (RESEARCH §"Recommended aou_ld_panel.py ordering"):
1. mt = hl.read_matrix_table(WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH)
2. mt = mt.filter_cols(mt.s in ancestry_afr)
3. mt = mt.anti_join_cols(related_samples_ht)
4. mt = hl.split_multi_hts(mt)             # BEFORE variant_qc — corrects spec inversion
5. mt = hl.sample_qc(mt, name='sqc'); filter call_rate >= 0.98
6. mt = hl.variant_qc(mt, name='vqc'); filter MAF/HWE/call_rate
7. mt = mt.filter_rows(hl.len(mt.filters) == 0)
8. mt = mt.checkpoint("gs://${WORKSPACE_BUCKET}/ld/mt_afr_qc.mt")
9. for region in regions: hl.ld_matrix(mt.GT.n_alt_alleles(), mt.locus, radius=region.radius_bp)
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Region manifest reformatter + dev-subset selector + region-class projection</name>
  <files>src/python/build_ld_region_manifest.py, src/python/select_ld_regions_dev.py, config/ld_regions.tsv, config/ld_regions_dev.tsv, config/region_id_mapping.tsv, .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv, tests/m3/conftest.py, tests/m3/test_build_ld_region_manifest.py</files>
  <read_first>
    - results/regions/union_region_list.bed (M2 deliverable; 161 GRCh37 rows; 8-column schema with provenance_json)
    - src/python/build_region_union.py (M2 sibling pattern; pandas + json.loads + bedtools idiom)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md sections "Q1 — Region BED coordinate system" (lines 146-156), "Q2 — Hail hl.ld_matrix radius parameter — STRUCTURAL FINDING" (lines 158-189), "Q11 — MTAG-novel exemplar dev region candidates" (lines 414-443)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md decision D-M3-04 (dev region selection) and D-M3-02 (322 cells)
    - .planning/amendments/AOU-LD-PIPELINE.md §6 (lines 259-285) — required AOU §6 schema
    - data/processed/ld_reference/EUR/*.rds — confirm Track A EUR LD .rds filenames so the 3-overlap design picks FTO_16q12, SH2B3_12q24, APOE_19q13
  </read_first>
  <behavior>
    - test_reformatter_emits_322_rows: build_ld_region_manifest.py reads 161-row union BED and emits config/ld_regions.tsv with exactly 322 data rows + 1 header.
    - test_per_region_radius: every row has radius_bp = min((end_grch38 - start_grch38) + 500_000, 50_000_000); region_class derived per RESEARCH Q2.
    - test_liftover_emits_both_coord_systems: every row has start_grch37/end_grch37 AND start_grch38/end_grch38.
    - test_liftover_status_column: every row has liftover_status in {primary, multi-segment, failed}; failed rows dropped from production manifest with stderr audit line.
    - test_dev_subset_overlap_design: select_ld_regions_dev.py emits 10 rows including m2_region_00067 (FTO; AFR+EUR), m2_region_00006 (SORT1; AFR), m2_region_00040 (SH2B3 12q24; AFR+EUR), m2_region_00083 (APOE; AFR+EUR), m2_region_00027 (LDLR; AFR), at least 1 chr6 HLA region (28-34 Mb), at least 1 chr8 region (7-13 Mb).
    - test_region_id_mapping_table: config/region_id_mapping.tsv maps Track A region_safe slugs to M2 region_ids.
  </behavior>
  <action>
    1. Write `src/python/build_ld_region_manifest.py` (Python 3.11; argparse `--bed`, `--chain`, `--out-manifest`, `--out-mapping`, `--out-projection`). Read `results/regions/union_region_list.bed` (8 col GRCh37, no header). For each region: parse `provenance_json`, expand into per-ancestry rows (every region duplicated for AFR + EUR per D-M3-02 → 322 rows). Liftover start/end via `pyliftover.LiftOver('hg19','hg38').convert_coordinate(...)`; set `liftover_status` to `primary` (single hit), `multi-segment` (multiple hits — keep min-start/max-end), or `failed` (no hit — drop with stderr audit line). Compute `radius_bp = min((end_grch38 - start_grch38) + 500_000, 50_000_000)`. Compute `region_class` ∈ {small (≤5 Mb), medium (5-25 Mb), large (25-50 Mb), xlarge (>50 Mb)}. Pull `source_trait` and `lead_variant` from the JSON's first ancestry-matching trait + lead. Emit 12-column TSV: region_id, chr, start_grch37, end_grch37, start_grch38, end_grch38, ancestry, source_trait, lead_variant, radius_bp, region_class, liftover_status. ALSO write `.planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv` (per-region span + class + Path A.1/2/3 + estimated cluster-hours per RESEARCH Q5 OOM table — feeds Carter's O1 ruling at Task 4).
    2. Write `src/python/select_ld_regions_dev.py` (Python 3.11; argparse `--manifest`, `--out`). Implements RESEARCH Q11 overlap design verbatim: pick m2_region_00067 (FTO 16q12; emit BOTH AFR + EUR), m2_region_00006 (SORT1; AFR only), m2_region_00040 (SH2B3 12q24; BOTH), m2_region_00083 (APOE; BOTH), m2_region_00027 (LDLR; AFR only); then filter manifest for `chr==6 AND start_grch38 BETWEEN 28e6 AND 34e6` (HLA stress; AFR only) AND `chr==8 AND start_grch38 BETWEEN 7e6 AND 13e6` (8p23; AFR only). Total = 10 rows: 5 AFR-only + 3 EUR-only (the EUR halves of the overlap regions) + 2 HLA-stress AFR-only.
    3. Write `config/region_id_mapping.tsv` (4-column TSV: region_safe TAB region_id TAB source TAB notes). Hard-code 11 rows for the 11 Track A EUR LD .rds files at `data/processed/ld_reference/EUR/*.rds` and their M2-union counterparts (FTO_16q12 → m2_region_00067, SH2B3_12q24 → m2_region_00040, APOE_19q13 → m2_region_00083 confirmed; remaining 8 mapped by chr+coord overlap inspection).
    4. Write `tests/m3/conftest.py` with 4 fixtures: (a) `union_bed_fixture` returns a 5-row mini union BED with EUR-only and TRANS-stratum provenance, (b) `chain_fixture` returns absolute path to `data/external/liftover/hg19ToHg38.over.chain.gz`, (c) `mock_aou_env` monkeypatches WORKSPACE_BUCKET=gs://fc-secure-test, GOOGLE_PROJECT=test-proj, WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH (overridden by synthetic MT path), (d) `synthetic_mt_path` lazy-builds synthetic_aou.mt via Task 3's build script if absent.
    5. Write `tests/m3/test_build_ld_region_manifest.py` covering the 6 behaviors. Use `subprocess.run([sys.executable, "src/python/build_ld_region_manifest.py", ...])` against the union_bed_fixture; assert row count == 10 (= 5 mini regions × 2 ancestries), schema columns present, radius_bp algorithm correct, region_class boundaries correct, dev-subset selection deterministic.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_build_ld_region_manifest.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `wc -l config/ld_regions.tsv` outputs `323` (1 header + 322 rows). Verifiable: `[[ $(wc -l &lt; config/ld_regions.tsv) == 323 ]]`.
    - `head -1 config/ld_regions.tsv` contains all 12 columns including `radius_bp`, `region_class`, `liftover_status`.
    - `wc -l config/ld_regions_dev.tsv` outputs `11` (1 header + 10 dev rows).
    - `awk -F'\t' 'NR>1 && $11=="" { print "BAD"; exit 1 }' config/ld_regions.tsv` returns no output.
    - `awk -F'\t' 'NR>1 { x=$6-$5; r=$10; if (r != x+500000 && r != 50000000) { print "BAD radius for "$1; exit 1 } }' config/ld_regions.tsv` returns exit 0.
    - `grep -c "m2_region_00067" config/ld_regions_dev.tsv` returns ≥ 2 (AFR + EUR rows).
    - `pytest tests/m3/test_build_ld_region_manifest.py -v` reports `8 passed` with exit 0.
    - `wc -l .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv` returns ≥ 162.
    - `wc -l config/region_id_mapping.tsv` returns 12.
  </acceptance_criteria>
  <done>
    Manifest reformatter, dev-subset selector, region-class projection, region-id mapping, and pytest scaffold all land. Test passes with the per-region radius algorithm + liftover semantics matching RESEARCH Q1 + Q2 verbatim. The 322-row manifest is committed as a config artifact (REQ-PATH-PARAMETERIZATION) along with the 10-row dev subset.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: ld_panel: resolver helper + pipeline.yaml ld_panel: block + resolver pytest</name>
  <files>src/python/ld_panel.py, config/pipeline.yaml, tests/m3/test_ld_panel_resolver.py</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Q7 — config/pipeline.yaml ld_panel: resolver implementation" (lines 286-358) — verbatim ld_panel: YAML block + resolve_ld_path() function source
    - config/pipeline.yaml lines 21-52 (paths: block layout) AND lines 180-196 (existing finemap: block — ld_panel: gets inserted as sibling AFTER line 196)
    - src/snakemake/rules/finemap.smk lines 45-102 — line 56 ld_matrix input is the M4 consumer (do NOT modify finemap.smk in this task — that is Wave 3)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md decision D-M3-05 (M2 supersede chain handled by fallback path; explains why AFR_aou is chain head)
  </read_first>
  <behavior>
    - test_resolver_returns_first_existing_path: when AFR_aou path exists for region X, returns AFR_aou Path; when missing, falls back to AFR_hgdp_1kg; when both missing, AFR_1kg.
    - test_resolver_strict_mode_raises: when strict_aou_only=True and AFR_aou path missing, raises FileNotFoundError with message containing "strict_aou_only".
    - test_resolver_pin_override: when pin.EUR='EUR_1kg', returns EUR_1kg path even if EUR_aou exists.
    - test_resolver_unknown_ancestry: TRANS uses TRANS_aou_eur → EUR_1kg fallback chain.
    - test_resolver_region_id_vs_region_safe: substitutes both `{region_id}` and `{region_safe}` per RESEARCH Q7 wart handling.
    - test_resolver_no_match_raises: when nothing exists in chain, raises FileNotFoundError with "No LD panel found".
  </behavior>
  <action>
    1. Append the verbatim `ld_panel:` YAML block from RESEARCH.md Q7 (lines 290-313) to `config/pipeline.yaml` after line 196 (immediately following the existing finemap: block). Block keys: `EUR` (3-entry chain EUR_aou → EUR_ukbb → EUR_1kg), `AFR` (3-entry AFR_aou → AFR_hgdp → AFR_1kg), `TRANS` (2-entry TRANS_aou_eur → EUR_1kg), `strict_aou_only: false`, `pin: {EUR: null, AFR: null, TRANS: null}`. Each chain entry is a dict with `source` and `path` keys; templates contain `{region_id}` or `{region_safe}` placeholders.
    2. Write `src/python/ld_panel.py` — single function `resolve_ld_path(region_id: str, ancestry: str, config: dict) -> pathlib.Path`. Body verbatim from RESEARCH Q7 (lines 319-341), with `from pathlib import Path` and top-of-file `__all__ = ["resolve_ld_path"]`. Add docstring referencing RESEARCH Q7 and inline comment about D-M3-05 fallback chain.
    3. Write `tests/m3/test_ld_panel_resolver.py` covering the 6 behaviors above. Use `tmp_path` pytest fixture for scratch dirs; use `yaml.safe_load` to load a tiny config dict matching the ld_panel: block; use `Path.touch()` to simulate `.rds` presence/absence. Test must NOT depend on the production pipeline.yaml — it should construct config dicts inline so the test is hermetic.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_ld_panel_resolver.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "^ld_panel:" config/pipeline.yaml` returns `1` (block at column 0).
    - `python -c "import yaml; cfg=yaml.safe_load(open('config/pipeline.yaml')); assert 'ld_panel' in cfg; assert set(cfg['ld_panel']) >= {'AFR','EUR','TRANS','strict_aou_only','pin'}; print('OK')"` prints `OK`.
    - `python -c "from src.python.ld_panel import resolve_ld_path; assert resolve_ld_path.__doc__"` exits 0.
    - `pytest tests/m3/test_ld_panel_resolver.py -v` reports ≥ 6 passed with exit 0.
    - `grep -E "AFR_aou" config/pipeline.yaml` returns ≥ 1 match (AFR chain head per D-M3-05).
    - `grep -E "strict_aou_only:[[:space:]]+false" config/pipeline.yaml` returns 1 match.
  </acceptance_criteria>
  <done>
    `ld_panel:` block lands in `config/pipeline.yaml` as the canonical M4-side LD path resolver source. Resolver helper at `src/python/ld_panel.py` is unit-tested and ready for Wave 3 to wire into `finemap.smk` line 56. REQ-PATH-PARAMETERIZATION closed for the M3 surface.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Conda envs + Hail driver (canonical ordering) + synthetic MT fixture + driver pytest + .gitignore</name>
  <files>envs/m3-aou-dev.yml, envs/m3-r-ld.yml, src/python/aou_ld_panel.py, tests/m3/fixtures/build_synthetic_mt.py, tests/m3/test_aou_ld_panel_local.py, .gitignore</files>
  <read_first>
    - envs/ld_build.yml (channels + python=3.11 reference)
    - envs/r_coloc.yml (R env reticulate dependency pattern)
    - .planning/amendments/AOU-LD-PIPELINE.md §5.1 "Path A — Hail BlockMatrix" (lines 113-225) — spec pseudocode (NOTE spec inverts split_multi_hts/variant_qc order — implement corrected canonical ordering per RESEARCH lines 124-141)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md sections "Hail v0.2.x API Verification" (lines 81-141), "Q5 — Hail BlockMatrix block_size tuning" (lines 236-263), "Q6 — Local synthetic MT fixture" (lines 265-283), "Q8 — AoU ancestry_pred field name" (lines 360-376), "Q9 — AoU RELATED_SAMPLES_HT_PATH env var" (lines 378-401)
    - CLAUDE.md "Snakemake 7.32.4 requires Python 3.11" rule
    - .gitignore lines 70-80 (existing data/raw/*, data/processed/*, data/external/* gitignores)
  </read_first>
  <behavior>
    - test_synthetic_mt_built_via_balding_nichols: tests/m3/fixtures/build_synthetic_mt.py emits tests/m3/fixtures/synthetic_mt/synthetic_aou.mt with hl.balding_nichols_model(n_populations=3, n_samples=100, n_variants=1500), populated ancestry / multiallelic / GATK fields.
    - test_aou_driver_loads_synthetic_mt: aou_ld_panel.py::load_qc_cohort runs against the synthetic MT and emits a checkpointed cohort with non-zero rows.
    - test_canonical_ordering: split_multi_hts is invoked BEFORE variant_qc (verifiable via inspection of function source AND assertion that variant_qc fires only on biallelic rows).
    - test_compute_region_ld_path_a1: for a synthetic 1.5 Mb region (region_class='small', radius_bp=2_000_000), compute_region_ld returns dict with status='ok', n_var > 0, and produces a (n_var × n_var) symmetric float32 numpy LD matrix that np.savez_compressed serializes.
    - test_compute_region_ld_skipped_few_variants: for a region with n_var < 10, returns dict with status='skipped_few_variants' (matching spec §5.1 lines 186-187).
    - test_env_yaml_pins_python_311: envs/m3-aou-dev.yml has python=3.11 and hail==0.2.* (Snakemake 7.32.4 compat per CLAUDE.md).
    - test_gitignore_has_explicit_aou_entries: .gitignore contains explicit lines for data/interim/aou_ld_exports/, data/processed/ld_reference/AFR_aou/, data/processed/ld_reference/EUR_aou/, tests/m3/fixtures/synthetic_mt/.
  </behavior>
  <action>
    1. Write `envs/m3-aou-dev.yml` with channels `[conda-forge, bioconda]` and dependencies: `python=3.11`, `openjdk=11`, `pip`, `numpy`, `scipy`, `pandas`, `pyspark=3.5.*`, `google-cloud-storage`, `pyliftover`, `pytest=8.*`, plus pip-only `hail==0.2.130`.
    2. Write `envs/m3-r-ld.yml` with channels `[conda-forge, bioconda]` and dependencies: `python=3.11`, `r-base=4.4.*`, `r-reticulate`, `r-matrix`, `r-testthat`, `r-jsonlite`, `numpy`, `pyliftover`.
    3. Write `src/python/aou_ld_panel.py` (~400 lines). Top-of-file constants:
       ```
       ANCESTRY_FIELD = "ancestry_pred"
       ANCESTRY_VALUES = {"afr","amr","eas","eur","sas","mid","oth"}
       KING_KINSHIP_THRESHOLD = 0.0442
       CDR_VERSION = "v7"
       AUX_BASE = f"gs://fc-aou-datasets-controlled/{CDR_VERSION}/wgs/short_read/snpindel/aux"
       RELATED_SAMPLES_PATH = f"{AUX_BASE}/relatedness/relatedness_flagged_samples.tsv"
       ANCESTRY_PREDS_PATH = f"{AUX_BASE}/ancestry/ancestry_preds.tsv"  # INFERRED — Wave 1 verification
       ```
       Functions:
       - `init_hail(default_reference="GRCh38", log_path="/tmp/hail.log") -> None` — wraps `hl.init(...)`.
       - `load_qc_cohort(mt_path, ancestry, sensitivity=False) -> hl.MatrixTable` — implements canonical ordering verbatim from RESEARCH lines 128-138. Steps: (1) hl.read_matrix_table(mt_path); (2) annotate_cols ancestry from `hl.import_table(ANCESTRY_PREDS_PATH, key='research_id')`; (3) anti_join_cols `hl.import_table(RELATED_SAMPLES_PATH, key='sample_id')`; (4) `mt = hl.split_multi_hts(mt)` (BEFORE variant_qc); (5) `mt = hl.sample_qc(mt, name='sqc')` + filter `mt.sqc.call_rate >= 0.98`; (6) compute het_hom mean +/- 3 SD via `hl.agg.stats(mt.sqc.r_het_hom_var)` then filter; (7) `mt = hl.variant_qc(mt, name='vqc')` + filter MAF 0.005-0.995, call_rate ≥ 0.95, p_value_hwe ≥ 1e-6; (8) `mt = mt.filter_rows(hl.len(mt.filters) == 0)`; (9) `mt = mt.checkpoint(f"gs://{WORKSPACE_BUCKET}/ld/mt_{ancestry}_qc.mt", overwrite=True)`. If `sensitivity=True`, add filter `mt.self_report.contains('Black or African American')` between steps 2 and 3.
       - `compute_region_ld(region_row: dict, mt_source: hl.MatrixTable, out_bucket: str) -> dict` — three branches per RESEARCH Q5:
         * Path A.1 (region_class=='small'): `to_numpy()` + `np.savez_compressed`.
         * Path A.2 (region_class=='medium'): `BlockMatrix.sparsify_triangle()` + `to_numpy()` lower-tri + savez_compressed.
         * Path A.3 (region_class in {'large','xlarge'}): `BlockMatrix.write(f"{out_bucket}/bm/{region_id}.bm", overwrite=True)` (NEVER densify on driver; Wave 3 NCSU densifies via bm_to_npz.py).
         All branches use `radius=region_row['radius_bp']` (NOT spec's static 2_500_000). Skip if `n_var < 10` returning `{'region_id': rid, 'status': 'skipped_few_variants', 'n_var': n_var}`.
       - `main()` — argparse harness; reads `config/ld_regions_dev.tsv` (or full manifest); iterates compute_region_ld per row; writes `ld_run_log.tsv`.
    4. Write `tests/m3/fixtures/build_synthetic_mt.py` (~80 lines): if `tests/m3/fixtures/synthetic_mt/synthetic_aou.mt` is absent, build via `hl.balding_nichols_model(n_populations=3, n_samples=100, n_variants=1500, fst=[0.05,0.05,0.05])`. Annotate ancestry (60 'afr', 30 'eur', 10 'oth'); seed 30 multiallelic synthetic sites for split_multi_hts exercise; annotate `filters=hl.empty_set(hl.tstr)`, `rsid=hl.missing(hl.tstr)`. Place 1000 variants on chr16 (50e6-52e6) and 500 on chr6 (28e6-34e6). Write to `tests/m3/fixtures/synthetic_mt/synthetic_aou.mt`.
    5. Write `tests/m3/test_aou_ld_panel_local.py` covering the 5 driver behaviors. Use `synthetic_mt_path` and `mock_aou_env` fixtures from conftest.py. Set `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` to the synthetic MT path. Skip-if-no-hail with `pytest.importorskip("hail")` for CI graceful-degrade.
    6. Append to `.gitignore` (with leading section comment):
       ```
       # M3 AoU LD panel build (per AOU-LD-PIPELINE.md §10.2)
       data/interim/aou_ld_exports/
       data/processed/ld_reference/AFR_aou/
       data/processed/ld_reference/EUR_aou/
       tests/m3/fixtures/synthetic_mt/
       ```
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_aou_ld_panel_local.py -v --tb=short</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "python=3.11" envs/m3-aou-dev.yml` returns ≥ 1.
    - `grep -c "hail==0.2" envs/m3-aou-dev.yml` returns ≥ 1.
    - `grep -c "r-reticulate" envs/m3-r-ld.yml` returns 1.
    - `grep -n "split_multi_hts" src/python/aou_ld_panel.py` returns line number BEFORE the line number of the FIRST `variant_qc` call (verifies canonical ordering).
    - `grep -c "WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH" src/python/aou_ld_panel.py` returns ≥ 1.
    - `grep -c "RELATED_SAMPLES_HT_PATH" src/python/aou_ld_panel.py` returns 0 (the broken env var name from spec must NOT appear; verifies RESEARCH Q9 correction).
    - `grep -c "relatedness_flagged_samples.tsv" src/python/aou_ld_panel.py` returns ≥ 1 (correct hardcoded path).
    - `grep -c "data/interim/aou_ld_exports" .gitignore` returns 1.
    - `pytest tests/m3/test_aou_ld_panel_local.py -v` reports ≥ 5 passed with exit 0 (or ≥ 5 skipped if hail not installed locally — both are acceptable).
    - Static-source check: `python -c "import ast; tree=ast.parse(open('src/python/aou_ld_panel.py').read()); names=[n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)]; assert 'split_multi_hts' in names and 'variant_qc' in names and 'sample_qc' in names and 'ld_matrix' in names; print('OK')"` prints OK.
  </acceptance_criteria>
  <done>
    Two conda envs land with python=3.11 + hail==0.2.x. Hail driver implements canonical ordering (split_multi_hts BEFORE variant_qc; verified env vars only). Synthetic MT fixture builds via balding_nichols_model on demand. Driver pytest passes (or skips gracefully). .gitignore explicitly records the M3 ephemeral / local-only paths.
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 4: Egress audit log seed + ROADMAP wording fix + STATE.md note</name>
  <files>.planning/amendments/aou-egress-audit-log.md, .planning/ROADMAP.md, .planning/STATE.md</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Q12 — Per-chromosome egress audit log structure" (lines 445-481) — verbatim Q12 schema
    - .planning/ROADMAP.md lines 146-180 — current M3 entry to update per D-M3-01 wording
    - .planning/STATE.md (entire file) — to append "phase m3 wave 0 in progress" note in current-position section
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md decisions D-M3-01 + D-M3-08 (drives ROADMAP M3 wording fix)
    - .planning/amendments/AOU-LD-PIPELINE.md §12 R1 "AoU export policy classifies LD matrices as derived individual-level data" — the gate the audit log header must capture
  </read_first>
  <action>
    1. Create `.planning/amendments/aou-egress-audit-log.md` verbatim from RESEARCH Q12 (lines 449-475) — append-only document with: (a) "Egress Classification Ruling (HARD GATE)" table seeded with one PLACEHOLDER row (`Date: TBD-Wave-1`, `Request type: Variant×variant LD matrix from n>=60k AFR`, `Classifier: TBD`, `Ruling: PENDING`, `Document: TBD`); (b) "Per-Bundle Audit Entries" table with 13-column header but NO data rows (rows landed Wave 4); (c) "M1-AFR-SBP cross-reference (DEC-2026-04-24-02)" placeholder section. The placeholder ruling row makes the gate visible at Wave 1 even before resolution.
    2. Edit `.planning/ROADMAP.md` lines 146-180 (M3 entry) per D-M3-01 wording fix:
       - Line 146 stays `### M3: AoU AFR LD panel build`.
       - Replace line 153 `Parallel: rebuild EUR LD from 1000G + UKB for parity (Amendment §3 M3, §5).` with `Parallel: build EUR LD parity panel inside the AoU Workbench against ancestry_pred=='eur' (D-M3-01); 1000G EUR Phase 3 plinkfiles serve as the Check 2 entry-wise correlation comparator only. UKB EUR augmentation deferred per D-M3-01.1 — UKB DUA timing not on the M3 to M4 critical path.`
       - Update line 155 `**Requirements**: REQ-AOU-LD-EGRESS, REQ-AOU-LD-VALIDATION, REQ-PUBLIC-DATA-ONLY` to include the missing two: `REQ-AOU-LD-EGRESS, REQ-AOU-LD-VALIDATION, REQ-PUBLIC-DATA-ONLY, REQ-SNAKEMAKE-CI, REQ-PATH-PARAMETERIZATION`.
       - Replace line 168 `data/processed/ld_reference/EUR_1kg_ukb/*.rds` with `data/processed/ld_reference/EUR_aou/*.rds`.
       - Update **Status** line 173 `Status: not planned; gated on M2 region list; partially parallel with M2 once prerequisites P1-P7 land.` to `Status: planning complete 2026-04-28 (6 plans, 6 waves); Wave 0 foundations + Wave 1+ Carter hard-gate stack pending fire.`
       - Update **Plans** count + add 6-plan numbered list under M3 section per GSD ROADMAP plan-list convention (matching M2 entry format at lines 138-144). Plan IDs: `m3-00-W0-foundations-PLAN.md`, `m3-01-W1-aou-cohort-and-hard-gates-PLAN.md`, `m3-02-W2-dev-fire-and-validation-PLAN.md`, `m3-03-W3-ncsu-ingest-and-resolver-PLAN.md`, `m3-04-W4-production-and-egress-PLAN.md`, `m3-05-W5-closeout-and-osf-PLAN.md`.
    3. Edit `.planning/STATE.md` `stopped_at:` field (line 6) to `Phase m3 plans created (6 plans, 6 waves; m3-00 Wave 0 in progress); ready to fire /gsd-execute-phase m3-aou-afr-ld-panel-build`. Update `last_activity:` to today's date with text `Phase m3 plan-phase complete (6 plan files committed under .planning/phases/m3-aou-afr-ld-panel-build/)`. Do NOT touch other STATE.md fields.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; grep -c "Egress Classification Ruling" .planning/amendments/aou-egress-audit-log.md &amp;&amp; grep -c "ancestry_pred=='eur'" .planning/ROADMAP.md &amp;&amp; grep -c "REQ-PATH-PARAMETERIZATION" .planning/ROADMAP.md &amp;&amp; grep -c "m3-00-W0-foundations-PLAN.md" .planning/ROADMAP.md</automated>
  </verify>
  <acceptance_criteria>
    - `wc -l .planning/amendments/aou-egress-audit-log.md` returns ≥ 30.
    - `grep -c "HARD GATE" .planning/amendments/aou-egress-audit-log.md` returns ≥ 1.
    - `grep -c "AoU export request ID" .planning/amendments/aou-egress-audit-log.md` returns ≥ 1 (Q12 schema column).
    - `grep -c "REQ-PATH-PARAMETERIZATION" .planning/ROADMAP.md` returns ≥ 1 (added to M3 line).
    - `grep -c "EUR_1kg_ukb" .planning/ROADMAP.md` returns 0 (old wording removed per D-M3-01).
    - `grep -c "EUR_aou" .planning/ROADMAP.md` returns ≥ 1 (new wording).
    - `grep -c "m3-00-W0-foundations-PLAN.md" .planning/ROADMAP.md` returns 1 (plan listed).
    - `grep -c "m3-05-W5-closeout-and-osf-PLAN.md" .planning/ROADMAP.md` returns 1.
    - `grep -E "^stopped_at:" .planning/STATE.md` line contains the string `Phase m3 plans created`.
    - `grep -c "DEC-2026-04-24-02" .planning/amendments/aou-egress-audit-log.md` returns ≥ 1 (M1-AFR-SBP cross-ref section).
  </acceptance_criteria>
  <done>
    Egress audit log exists with classification-ruling header (placeholder); ROADMAP M3 wording matches D-M3-01 + D-M3-01.1; ROADMAP plan list updated with all 6 plan filenames. STATE.md `stopped_at` reflects M3 planning complete.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 5: Carter ruling on Open Issue O1 — region-width acceptance — log as D-M3-09</name>
  <files>.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "Q2 — Hail hl.ld_matrix radius parameter — STRUCTURAL FINDING" (lines 158-189) — span distribution table + 8% / 92% finding
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md "O1 — M2 region width vs M3 fine-mapping unit (CRITICAL — blocking design decision)" (lines 730-740) — two viable resolutions
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv (emitted by Task 1) — per-region span + class + Path-A.1/2/3 + estimated cluster-hours
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md (entire file) — to append D-M3-09 ruling row
  </read_first>
  <action>See &lt;human_gate&gt; block. This task is a Carter human-action checkpoint; no agent action. The agent's role is to verify acceptance_criteria after Carter completes the gate.</action>
  <human_gate>
    <gate>Open Issue O1 — region-width acceptance ruling</gate>
    <description>
      RESEARCH.md surfaced that 92% of M2 union regions exceed the AOU-LD-PIPELINE.md spec's static `radius=2_500_000` setting (median 9 Mb; max 102 Mb on chr6). Wave 0 implements the per-region radius algorithm (radius_bp = (end - start) + 500_000, capped at 50 Mb) — but Carter must explicitly accept the implication that ≥ 30 Mb regions follow Path A.3 (BlockMatrix-write-to-bucket; never densify on driver; densify NCSU-side at .npz to .rds conversion) which is methodologically defensible but engineering-heavier.

      The two viable resolutions per RESEARCH O1 (lines 730-740):

      Resolution 1 (RECOMMENDED): Accept wide regions; use Path A.3 for &gt; 10 Mb regions. Cost: methodological purity preserved; M2 union remains canonical fine-mapping unit; engineering plumbing only. Per-class cost projection at .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv.

      Resolution 2: Re-merge M2 regions into ≤ 10 Mb tiles before M3. Cost: M2's region union ceases to be M3 fine-mapping unit; novelty calls become tile-anchored not region-anchored. Cleaner compute; messier methodology. Inserts a new src/python/tile_wide_regions.py task.

      What unblocks the next task: Carter writes a 5-line ruling row appended to m3-CONTEXT.md as D-M3-09 in the &lt;decisions&gt; block, of the form:

      ### D-M3-09: Open Issue O1 ruling — region-width acceptance

      **Decision:** Resolution 1 — accept wide regions; Path A.3 for &gt;10 Mb regions.   (or Resolution 2)

      **Why:** [Carter's rationale]

      **How to apply:** Wave 1+ honor the per-region radius from config/ld_regions.tsv; Wave 4 production honors Path A.1/A.2/A.3 branches in src/python/aou_ld_panel.py per region_class.   (or: Wave 0 adds tile_wide_regions.py and re-emits config/ld_regions.tsv with ≤10 Mb tiles.)

      Without this ruling committed, Wave 1 cannot fire (the AoU 6-gate stack is downstream of this).
    </description>
    <unblocks>Wave 1 m3-01-W1-aou-cohort-and-hard-gates-PLAN.md (specifically the Carter portal-action gates + Hail driver fire on synthetic MT)</unblocks>
    <how-to-resolve>
      1. Review .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv for per-region span + estimated cluster-hours per Path-A class.
      2. Review RESEARCH O1 (lines 730-740) for full pros/cons of Resolutions 1 and 2.
      3. Append a D-M3-09 ruling block (5-10 lines) to m3-CONTEXT.md `<decisions>` section.
      4. Commit with token `(m3-W0-T5)` in the commit subject.
      5. Type "approved" to resume execution; OR describe the chosen resolution path for any course correction.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; grep -c "D-M3-09" .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "D-M3-09" .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` returns ≥ 2 (header + at least one body reference).
    - `grep -A 5 "D-M3-09" .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md | grep -E "Resolution [12]|tile_wide_regions|Path A\\.3"` returns ≥ 1 match (verifies Carter selected one of the two resolutions).
    - Git log shows a commit with `(m3-W0-T5)` token in the subject line.
  </acceptance_criteria>
  <done>
    D-M3-09 row committed to m3-CONTEXT.md `<decisions>` block. Carter has explicitly chosen Resolution 1 (accept wide regions; Path A.3 for &gt;10 Mb) OR Resolution 2 (re-merge M2 regions into ≤10 Mb tiles). Wave 1 unblocked.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| NCSU GPFS ↔ AoU Workbench | All M3 compute happens INSIDE AoU; only summary `.npz` artifacts cross this boundary (Wave 4). Wave 0 lays the contracts but does not yet exercise this boundary. |
| Source code ↔ test fixtures | Synthetic MT fixture is the ONLY substrate code is exercised against in Wave 0 — guarantees no AoU access required for Wave 0 testing. |
| Local conda env ↔ AoU Dataproc | `envs/m3-aou-dev.yml` is the local mirror; identical Hail version (0.2.130) on both sides per AOU-LD-PIPELINE.md §2 P5. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M3-EGR-W0 | Information disclosure | aou_ld_panel.py local synthetic-MT testing | mitigate | Test fixture uses `hl.balding_nichols_model` exclusively (synthetic genotypes; no AoU access). `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` is monkeypatched to the synthetic path in conftest.py — production access is impossible from a local pytest run. |
| T-M3-S1-W0 | Tampering / supply chain | envs/m3-aou-dev.yml + envs/m3-r-ld.yml | mitigate | Pinned channels (`conda-forge`, `bioconda`); pinned major versions (`python=3.11`, `hail==0.2.130`, `r-base=4.4.*`); SHA-256 of resolved env captured at first activation per existing M1 / M2 convention. |
| T-M3-S2-W0 | Reproducibility / provenance | config/ld_regions.tsv + config/ld_regions_dev.tsv | mitigate | Manifest reformatter is fully deterministic (single chain file, fixed algorithm); Wave 0 commits both the input BED SHA-256 and the output manifest SHA-256 to the audit log. Liftover failures are explicitly logged with `liftover_status` column rather than silently dropped. |
| T-M3-AUTH-W0 | Authorization | Wave 0 cannot create or use AoU credentials | accept | Wave 0 is entirely NCSU-local; no AoU credentials touched. The Carter human gates for AoU portal action live in Wave 1. |
| T-M3-EGR-AUDIT | Information disclosure | .planning/amendments/aou-egress-audit-log.md (Q12 schema) | mitigate | Audit log lands at Wave 0 with the HARD GATE row visible (PENDING placeholder); the actual AoU egress classification ruling (Wave 1 human action) is bound to fire BEFORE any production data leaves AoU. The placeholder makes the gate visible to all downstream tasks. |
</threat_model>

<verification>
**Wave 0 phase-level checks (run AFTER all 5 tasks land):**

1. `pytest tests/m3 -x --tb=short` — all 3 Wave 0 tests pass (test_build_ld_region_manifest.py, test_ld_panel_resolver.py, test_aou_ld_panel_local.py); ≤ 30 s wall.
2. `python -c "import yaml; cfg=yaml.safe_load(open('config/pipeline.yaml')); assert 'ld_panel' in cfg and set(cfg['ld_panel']) >= {'AFR','EUR','TRANS','strict_aou_only','pin'}; print('OK')"` prints OK.
3. `wc -l config/ld_regions.tsv` returns 323 (322 rows + header).
4. `wc -l config/ld_regions_dev.tsv` returns 11 (10 rows + header).
5. `grep -c "split_multi_hts" src/python/aou_ld_panel.py` ≥ 1 AND `grep -c "RELATED_SAMPLES_HT_PATH" src/python/aou_ld_panel.py` == 0 (verifies RESEARCH Q9 correction).
6. `grep -c "D-M3-09" .planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md` ≥ 2 (Carter O1 ruling committed).
7. `grep -c "EUR_1kg_ukb" .planning/ROADMAP.md` == 0 (old D-M3-01 wording removed).
8. `grep -c "data/interim/aou_ld_exports" .gitignore` == 1 (explicit M3 entries present).
</verification>

<success_criteria>
- 322-row `config/ld_regions.tsv` lands with per-region radius + region_class.
- 10-row `config/ld_regions_dev.tsv` lands with the Q11 overlap design (3 EUR-Track-A regions overlap 3 of the 5 AFR-known regions).
- `ld_panel:` block in `config/pipeline.yaml` provides AFR / EUR / TRANS chains + pin override + strict mode.
- `src/python/ld_panel.py::resolve_ld_path` is unit-tested.
- `src/python/aou_ld_panel.py` implements the corrected Hail ordering (split_multi_hts BEFORE variant_qc; verified env vars only; per-region radius; three Path-A branches).
- `tests/m3/{conftest,fixtures,test_*}.py` pytest suite passes in <= 30 s.
- `envs/m3-aou-dev.yml` and `envs/m3-r-ld.yml` pin python=3.11 (CLAUDE.md Snakemake compat).
- `.planning/amendments/aou-egress-audit-log.md` exists with Q12 schema + HARD GATE placeholder row.
- ROADMAP.md M3 entry wording matches D-M3-01 + D-M3-01.1; plan list includes all 6 plan filenames.
- STATE.md `stopped_at` reflects M3 plan-phase complete.
- D-M3-09 (Open Issue O1 ruling) committed to `m3-CONTEXT.md` `<decisions>` block.
- `.gitignore` carries explicit M3 entries.
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-00-W0-foundations-SUMMARY.md` recording:
- Tasks completed (5)
- Test pass count (>= 14 pytest assertions across 3 test files)
- D-M3-09 ruling chosen (Resolution 1 vs Resolution 2)
- Region-class distribution (count of small / medium / large / xlarge from m3-region-class-projection.tsv)
- Wave 1 readiness checklist (which Carter portal actions remain)
</output>
