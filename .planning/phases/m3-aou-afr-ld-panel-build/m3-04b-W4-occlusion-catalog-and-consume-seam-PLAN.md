---
phase: m3-aou-afr-ld-panel-build
plan: 04b
type: execute
wave: 1
depends_on: []
files_modified:
  - src/python/assemble_occlusion_catalog.py
  - src/python/occlusion_lockstep_cli.py
  - src/snakemake/rules/m3_occlusion_lockstep.smk
  - src/snakemake/rules/finemap.smk
  - Snakefile
  - config/pipeline.yaml
  - tests/m3/test_occlusion_catalog_assembly.py
  - tests/m3/test_occlusion_lockstep_wiring.py
autonomous: true
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "The four ZERO-CALLER m3-07b/07c functions (add_grch37_positions, enrich_occlusion_manifest, aggregate_manifests/build_occlusion_catalog, scan_present_rate) have a production caller: one CLI plus one Snakemake rule assemble the genome-wide enriched occlusion catalog from the per-region Stage-A manifests, the hg38ToHg19 chain, and the 9 public AFR harmonized sumstats."
    - "The assembled catalog ALWAYS carries chr, pos_grch37, chain_sha256 and the STAGE_B trait columns, INCLUDING when it is empty. Otherwise drop_occluded_from_sumstats._load_manifest_keys fails CLOSED (by design) and the whole seam is unrunnable until the fire lands."
    - "When the per-region Stage-A manifests did not reach NC-State, the catalog can be reconstructed in DEGRADED form from the {region_id}.occluded.excludelist objects (variant ids are chr:pos:ref:alt on GRCh38), stamped provenance_source=excludelist_degraded, and the CLI REFUSES to emit a degraded catalog unless --allow-degraded is passed explicitly."
    - "run_finemap consumes an occlusion-filtered AFR sumstats mirror AND an occlusion-filtered AFR variant list. BOTH inputs are repointed: repointing only sumstats leaves ld_reference.smk::collect_region_variants re-introducing the occluded rows through run_finemap.input.variants."
    - "The filter is ancestry-gated (AFR only). For every non-AFR ancestry the resolved input path strings are byte-identical to today's expressions, so Track-A / EUR numerics cannot move."
    - "The filtered sumstats mirror is real bgzip plus tabix, not an uncompressed file wearing a .bgz name: drop_occluded_from_sumstats writes PLAIN bytes, while run_susie_rss.R reads with gunzip -c and collect_region_variants.py reads with compression='gzip'."
    - "drop_occluded_from_sumstats is reused VERBATIM for the variant list (plain TSV in, plain TSV out, CHR and POS located by name). No second implementation, no second chance to disagree with the panel."
    - "occlusion_span_filter.py, occlusion_manifest.py, occlusion_present_rate_scan.py and drop_occluded_from_sumstats.py have a 0-line git diff: this plan CALLS them, it does not edit them."
    - "Frozen contracts (plink_ld_to_npz.py, ld_npz_to_rds.R, condition_ld_matrix.py) have a 0-line git diff. m3-06 stays HELD; nothing here imports condition_ld_matrix or nan_to_num."
  artifacts:
    - path: "src/python/assemble_occlusion_catalog.py"
      provides: "Genome-wide occlusion catalog assembler and CLI (aggregate, lift, present-rate scan, enrich); empty-catalog Stage-B column guarantee; degraded excludelist reconstruction"
      min_lines: 120
    - path: "src/python/occlusion_lockstep_cli.py"
      provides: "filter-sumstats / filter-variants subcommands plus the two path resolvers, wrapping drop_occluded_from_sumstats so the 07c module stays at 0-line diff"
      min_lines: 80
    - path: "src/snakemake/rules/m3_occlusion_lockstep.smk"
      provides: "m3_assemble_occlusion_catalog, occlusion_filter_sumstats, occlusion_filter_variants rules"
      min_lines: 90
    - path: "src/snakemake/rules/finemap.smk"
      provides: "run_finemap.input.sumstats and run_finemap.input.variants routed through the ancestry-gated lockstep seam"
      contains: "occlusion_lockstep"
    - path: "config/pipeline.yaml"
      provides: "occlusion_lockstep block (enabled / ancestries / catalog / sumstats_dir / variants_dir_name / manifest_dir / excludelist_dir / allow_degraded)"
      contains: "occlusion_lockstep"
    - path: "tests/m3/test_occlusion_catalog_assembly.py"
      provides: "RED-first suite for the assembler, including the empty-catalog Stage-B guarantee and the degraded-fallback refusal"
    - path: "tests/m3/test_occlusion_lockstep_wiring.py"
      provides: "RED-first suite for the seam: both inputs repointed for AFR, byte-identical strings for EUR, real gzip output"
  key_links:
    - from: "src/python/assemble_occlusion_catalog.py"
      to: "src/python/occlusion_manifest.py::enrich_occlusion_manifest"
      via: "direct call in the assembler pipeline"
      pattern: "enrich_occlusion_manifest"
    - from: "src/python/assemble_occlusion_catalog.py"
      to: "src/python/occlusion_present_rate_scan.py::scan_present_rate"
      via: "direct call in the assembler pipeline"
      pattern: "scan_present_rate"
    - from: "src/snakemake/rules/finemap.smk"
      to: "data/processed/sumstats_harmonized_occl/{trait}.AFR.tsv.bgz"
      via: "run_finemap.input.sumstats ancestry-gated lambda"
      pattern: "lockstep_sumstats_path"
    - from: "src/snakemake/rules/finemap.smk"
      to: "data/processed/ld_reference/variants_occl/{region}.tsv"
      via: "run_finemap.input.variants ancestry-gated lambda"
      pattern: "lockstep_variants_path"
    - from: "src/snakemake/rules/m3_occlusion_lockstep.smk"
      to: "src/python/drop_occluded_from_sumstats.py::drop_occluded_from_sumstats"
      via: "occlusion_lockstep_cli filter-sumstats / filter-variants"
      pattern: "drop_occluded_from_sumstats"
---

<objective>
Close **the unwired seam** that m3-07c formally deferred to the m3-04 replan: there is no
Snakemake rule between the harmonized sumstats and `run_finemap`, so the pre-registered
**exclude-in-lockstep** policy (osf.io/az52u, file `trsx5`, POSTED 2026-07-10T13:32:22Z) is
today enforced on the LD panel ONLY. Panel-only exclusion is not a smaller version of the
policy; it is a different and wrong one. `rs182965575` (GRCh37 `1:5982778`) is present in
**7 of 9** AFR sumstats, so a panel-only drop orphans it in 7 traits.

This plan lands the two NC-State-side pieces that make the policy real and that require
**no AoU perimeter, no compute spend, and no panel on disk**:

1. **A production caller for the catalog.** `add_grch37_positions`, `enrich_occlusion_manifest`,
   `aggregate_manifests` / `build_occlusion_catalog` and `scan_present_rate` shipped in
   m3-07b/07c with **ZERO callers**. One CLI plus one rule turn them into the genome-wide
   enriched occlusion catalog: the Angle-1/3 catalog seed AND the artifact the lockstep drop
   keys on.
2. **The consume seam.** An occlusion-filtered AFR sumstats mirror and an occlusion-filtered
   AFR variant list, both wired into `run_finemap`, both AFR-gated so EUR / Track-A numerics
   cannot move.

The seam is wired **now and permanently**, not "when the panel lands": the catalog rule emits
a schema-complete EMPTY catalog when no manifests exist, so the drop is a documented, audited
**no-op** (`n_dropped == 0`) until the fire banks real manifests, and then becomes live with
zero further wiring. That removes the wire-it-later-and-forget failure mode this phase has
already paid for twice.

Purpose: the panel and the sumstats must agree about which variants exist. Every downstream
fine-map inherits the mismatch if they do not.

Output: `src/python/assemble_occlusion_catalog.py`, `src/python/occlusion_lockstep_cli.py`,
`src/snakemake/rules/m3_occlusion_lockstep.smk`, an ancestry-gated `finemap.smk`, an
`occlusion_lockstep:` config block, and two RED-first pytest suites.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-07-CONTEXT.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-07-RESEARCH.md
@.planning/amendments/AOU-LD-PIPELINE.md

Read ONLY lines 1-50 of `.planning/STATE.md`. The file is 732 KB; the 2026-07-16
RESUME-HERE block is the authoritative state.

<superseded_signature_warning>
**`m3-07-RESEARCH.md` §T4 (line 187) CARRIES A SIGNATURE THAT DID NOT SHIP.** It recommends

    drop_occluded_from_sumstats(sumstats_df, manifest, build="GRCh37") -> (filtered_df, drop_log)

The SHIPPED contract (`ed3e122`, verified against the module and its tests) is

    drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> dict

FILE-IN / FILE-OUT. Returns `{"n_in", "n_dropped", "n_out"}`. Logs each drop to STDERR.
Idempotent on its own output. Planning or coding against the RESEARCH signature reproduces
exactly the drift `8d4087a` had to fix. Rule baked twice: **GREP THE NAME, THEN READ THE
ASSERTIONS.** `tests/m3/test_occlusion_lockstep_drop.py` is the contract.
</superseded_signature_warning>

<interfaces>
Everything below is VERIFIED against the live tree at HEAD `9fe26f6`. Use it directly; no
codebase exploration is required to execute this plan.

--- src/python/drop_occluded_from_sumstats.py (m3-07c T4; DO NOT EDIT) ---
    def drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> dict
    returns {"n_in", "n_dropped", "n_out"}; invariant n_in - n_dropped == n_out
    INPUT  : plain .tsv OR .gz/.bgz (gzip-transparent via _open_binary)
    OUTPUT : ALWAYS PLAIN, UNCOMPRESSED BYTES  <- out_path.open("wb"); no re-compression
    KEY    : manifest columns "chr" + "pos_grch37"; sumstats CHR + (POS|BP) located BY NAME
    FAILS CLOSED: raises ValueError if the manifest lacks pos_grch37 (a Stage-A manifest)
    Survivor rows are byte-identical and order-preserved. Header written verbatim.

--- src/python/occlusion_manifest.py (m3-07b T2; DO NOT EDIT) ---
    STAGE_A_COLUMNS = ["region_id","chr","variant_id","pos_grch38","ref","alt",
        "ref_span_start_grch38","ref_span_end_grch38","occluding_deletion_id",
        "occluding_deletion_ref_len","reason","occlusion_order"]
    STAGE_B_TRAIT_COLUMNS = ["traits_present","n_traits_present","n_traits_scanned"]
    REASON_REFERENCE_OCCLUSION = "reference-occlusion → undefined-LD"

    def aggregate_manifests(manifest_paths, out_path) -> Path   # build_occlusion_catalog = alias
    def add_grch37_positions(records, *, chain_path) -> list[dict]   # adds pos_grch37 (None if unlifted)
    def chain_sha256(chain_path) -> str
    def enrich_occlusion_manifest(manifest_path, chain_path, *, out_path=None,
                                  present_rate=None) -> Path

    enrich RAISE BOUNDARY (pinned by tests; do not rediscover):
      unlifted row                                            -> pd.NA, never a raise
      present_rate non-empty + >=1 liftable row + ZERO matches -> raises ValueError
      present_rate non-empty + ZERO liftable rows              -> no raise, all pd.NA

    ** EMPTY-INPUT SHORT-CIRCUIT (occlusion_manifest.py:361-363) **
        if df.empty: df.to_csv(out_path); return out_path
      -> an empty catalog is written with the INPUT's columns and NO pos_grch37.
         This is the single most important gotcha in this plan. See Task 1 step 3.

--- src/python/occlusion_present_rate_scan.py (m3-07c T3; DO NOT EDIT) ---
    def scan_present_rate(variants_grch37, sumstats_paths) -> dict
    variants_grch37: iterable of (chr, pos_grch37) GRCh37 pairs, POST-liftover
    returns {(chr,pos): {"n_traits_present","n_traits_scanned","present_rate","traits_present"}}
    keys are CANONICALIZED: ('1', 5982778) -> (1, 5982778), directly feedable to
    enrich_occlusion_manifest(present_rate=...)

--- src/python/ld_egress_bundle.py (m3-02d; REUSE, DO NOT REWRITE) ---
    EGRESS_CAP_GB = 50   # a CONSERVATIVE PROJECT WORKING CEILING, not a hard AoU API limit
    def plan_egress_bundles(cell_sizes, cap_bytes=EGRESS_CAP_BYTES) -> list[dict]
    (consumed by m3-04c, not by this plan; listed so nobody writes validate_bundle_sizes.py)

--- src/snakemake/rules/finemap.smk (CURRENT, lines 97-158) ---
    rule run_finemap:
        input:
            sumstats=lambda w: os.path.join(HARMONIZED_DIR, f"{w.trait}.{w.ancestry}.tsv.bgz"),
            variants=lambda w: os.path.join(config["paths"]["ld_reference"], "variants",
                                            f"{w.region}.tsv"),
            ld_matrix=lambda w: str(resolve_ld_path(
                region_id=REGION_SAFE_TO_ID[w.region], ancestry=w.ancestry,
                config=config, region_safe=w.region)),
            ...
        params:
            region_id=lambda w: REGION_SAFE_TO_ID[w.region]     # <- DO NOT TOUCH

--- src/snakemake/rules/ld_reference.smk::collect_region_variants (the OTHER leak) ---
    rule collect_region_variants:
        input:  harmonized=HARMONIZED_ALL, regions=config["paths"]["regions_curated"]
        output: os.path.join(VARIANT_LIST_DIR, "{region}.tsv")  # {ld_reference}/variants
    collect_region_variants.py POOLS ALL harmonized files, ancestry-agnostic, OrderedDict dedup.
    Emitted columns: CHR, POS, REF, ALT, SNP_ID (plain TSV, header present).
    => filtering only the sumstats leaves the occluded coordinate alive in the variant list.

--- consumers that decide the compression contract ---
    run_susie_rss.R:275              read_cmd <- sprintf("gunzip -c %s", shQuote(opt$sumstats))
    collect_region_variants.py:40,56 pd.read_csv(..., compression="gzip")
    sumstats.smk::harmonize_sumstats conda: envs/python_stats.yml ; uses `bgzip -f` + `tabix -f -S 1 -s 1 -b 2 -e 2`
    => envs/python_stats.yml is the env that HAS bgzip/tabix. `bgzip` is NOT on the login
       PATH and is NOT in smoke_dev, so the filter rule MUST declare a conda env.

--- on-disk facts ---
    config/pipeline.yaml paths.harmonized_sumstats = "data/processed/sumstats_harmonized"
    config/pipeline.yaml paths.ld_reference        = "data/processed/ld_reference"  (DOES NOT EXIST YET)
    HARMONIZED_ALL (Snakefile:68) = 8 files: bmi.EUR, t2d.EUR, t2d.AFR, hypertension.EUR,
        asthma.EUR, asthma.AFR, stroke.EUR, stroke.AFR  -> 3 AFR members
    M3 present-rate scan scope = the 9 real AFR files under data/processed/sumstats_harmonized/
        matching *.AFR*.tsv.bgz, EXCLUDING asthma.AFR.grch38_backup.tsv.bgz (a build-38 backup)
    liftover chain: data/external/liftover/hg38ToHg19.over.chain.gz (1,246,411 B, present)
    harmonized header: CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD (GRCh37)
    variant-list header (toy fixture): CHR POS SNP_ID REF ALT
    settled hinge anchors: GRCh38 5922716/5922718/5922724 -> GRCh37 5982776/5982778/5982784 (chr1)
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Genome-wide occlusion catalog assembler — give the four zero-caller functions a production caller</name>
  <files>src/python/assemble_occlusion_catalog.py, src/snakemake/rules/m3_occlusion_lockstep.smk, Snakefile, config/pipeline.yaml, tests/m3/test_occlusion_catalog_assembly.py</files>
  <read_first>
    - src/python/occlusion_manifest.py (WHOLE FILE; especially the empty-input short-circuit at :361-363 and the enrich raise boundary documented at :344-354)
    - src/python/occlusion_present_rate_scan.py :124-175 (scan_present_rate contract and key canonicalization)
    - src/python/drop_occluded_from_sumstats.py :126-168 (_load_manifest_keys — the consumer whose fail-closed check dictates the catalog schema)
    - src/snakemake/rules/m3_convert_npz_rds.smk :24-75 (the _find_project_root + absolute-conda-env convention every M3 rule file follows, DEF-01-01)
  </read_first>
  <behavior>
    RED-first. `tests/m3/test_occlusion_catalog_assembly.py` must contain at least these
    cases and must FAIL before the module exists. Import the module INSIDE each test
    (mirroring `tests/m3/test_occlusion_lockstep_drop.py:30-40`) so a missing module is a
    test failure, not a collection error.

    T1.1 test_catalog_rolls_up_per_region_manifests — two synthetic per-region Stage-A
      manifests, built with `occlusion_manifest.append_region_manifest` so the schema is the
      REAL one and not a hand-typed guess, roll up into one catalog carrying both regions'
      rows, de-duplicated on (region_id, variant_id).

    T1.2 test_catalog_carries_stage_b_columns — the output has `pos_grch37`,
      `chain_sha256`, and all three `STAGE_B_TRAIT_COLUMNS`.

    T1.3 test_empty_catalog_still_carries_stage_b_columns — THE LOAD-BEARING ONE. With
      ZERO input manifests, the written catalog is header-only BUT its header still contains
      `chr` and `pos_grch37`, and
      `drop_occluded_from_sumstats(any_sumstats, that_catalog, out)` returns
      `n_dropped == 0` WITHOUT raising. Naive delegation to `enrich_occlusion_manifest`
      FAILS this: its empty-input branch short-circuits before the lift and writes the
      input's columns only.

    T1.4 test_present_rate_is_joined_from_the_real_scan — a synthetic AFR sumstats file
      containing the occluded variant's GRCh37 coordinate yields `n_traits_present == 1`,
      `n_traits_scanned == 1`, and a `present_rate` column of 1.0. Use the settled hinge
      anchors (GRCh38 5922718 -> GRCh37 5982778 on chr1).

    T1.5 test_degraded_reconstruction_from_excludelists — with no manifests but two
      `{region_id}.occluded.excludelist` files whose lines are `chr:pos:ref:alt` GRCh38 ids,
      `allow_degraded=True` produces a catalog whose rows carry `region_id`, `chr`,
      `variant_id`, `pos_grch38`, `ref`, `alt`, `reason`, and
      `provenance_source == "excludelist_degraded"`, with the ref-span and
      occluding-deletion columns explicitly NA.

    T1.6 test_degraded_reconstruction_refuses_without_flag — the same inputs WITHOUT
      `allow_degraded` raise with a message naming the missing manifests. Silent degradation
      is the failure mode this test exists to prevent.

    T1.7 test_catalog_columns_are_egress_clean — no emitted column name contains any of
      `sample`, `person`, `genotype`, `individual`, `_ac`, `_an` (mirrors the Stage-A guard
      in `tests/m3/test_occlusion_manifest.py`).
  </behavior>
  <action>
    1. Write the RED suite first (`tests/m3/test_occlusion_catalog_assembly.py`), commit it,
       and confirm every new test fails at call time. Do NOT weaken any existing test.

    2. Create `src/python/assemble_occlusion_catalog.py` exporting

           def assemble_occlusion_catalog(
               manifest_paths, chain_path, sumstats_paths, out_path, *,
               excludelist_paths=None, allow_degraded=False,
           ) -> dict   # {"n_regions","n_variants","n_lifted","n_unlifted","source"}

       Pipeline, in this exact order. Each step DELEGATES to the shipped function; do not
       re-derive any of them.

       a. `aggregate_manifests(manifest_paths, stage_a_tmp)` -> the Stage-A rollup.
       b. If the rollup is EMPTY and `excludelist_paths` is non-empty, reconstruct degraded
          records: parse each line as `chr:pos:ref:alt` (GRCh38; production `hl.export_plink`
          varids per `run_native_ld_panel.py:391-400`); derive `region_id` from the filename
          stem with the trailing `.occluded` stripped; set `reason` to
          `occlusion_manifest.REASON_REFERENCE_OCCLUSION` and `occlusion_order` to `"direct"`;
          leave `ref_span_start_grch38`, `ref_span_end_grch38`, `occluding_deletion_id` and
          `occluding_deletion_ref_len` as explicit NA; stamp
          `provenance_source="excludelist_degraded"`. RAISE unless `allow_degraded`.
          When the rollup is non-empty, stamp `provenance_source="stage_a_manifest"`.
          A line that does not parse as `chr:pos:ref:alt` is skipped with a loud STDERR
          warning and counted, never guessed at.
       c. `add_grch37_positions(records, chain_path=chain_path)` -> GRCh37 keys.
       d. `scan_present_rate([(r["chr"], r["pos_grch37"]) for r in lifted
          if r["pos_grch37"] is not None], sumstats_paths)`.
       e. `enrich_occlusion_manifest(stage_a_tmp, chain_path, out_path=out_path,
          present_rate=present_rate_or_None)`. Pass `None` (not `{}`) when there are no
          liftable rows, so enrich's documented raise boundary is not tripped.

    3. THE EMPTY / SCHEMA-COMPLETION GUARANTEE (do not skip; T1.3 pins it). After step (e),
       re-read `out_path` with pandas and ensure the frame carries, in this order,

           STAGE_A_COLUMNS + ["provenance_source", "pos_grch37", "chain_sha256"]
                           + STAGE_B_TRAIT_COLUMNS + ["present_rate"]

       adding any missing column as `pd.NA`, then rewrite. This makes the EMPTY catalog
       schema-complete, which is what lets `drop_occluded_from_sumstats._load_manifest_keys`
       return a clean, honest `n_dropped == 0` instead of raising its (correct, deliberate)
       fail-closed Stage-A error.

    4. Derive `present_rate` post-hoc as `n_traits_present / n_traits_scanned`, guarding
       n == 0 to `pd.NA`. This closes the first of the two PRE-EXISTING `63bdb59` consumer
       notes recorded in STATE.md ("present_rate is never persisted as a manifest column").

    5. Write `{out_path}.README.md` alongside the catalog documenting the second consumer
       note: `traits_present` serializes as a STRINGIFIED LIST (`"['bmi','ldl']"`), so a
       catalog reader gets a `str`, not a `list`. State the recommended parse
       (`ast.literal_eval`) explicitly. Do NOT change enrich's serialization; it is shipped
       and pinned by tests.

    6. Add an `argparse` `main()` plus `if __name__ == "__main__":` with `--manifest`
       (nargs="*"), `--excludelist` (nargs="*"), `--chain`, `--sumstats` (nargs="+"),
       `--out`, `--allow-degraded`. Print the returned dict as JSON to stdout.

    7. Create `src/snakemake/rules/m3_occlusion_lockstep.smk`. Follow the M3 rule-file
       convention verbatim from `m3_convert_npz_rds.smk:24-75` (workflow.basedir plus
       `_find_project_root` plus absolute conda-env paths, DEF-01-01). Add
       `rule m3_assemble_occlusion_catalog` with inputs `chain` and `sumstats` (the 9 real
       AFR files, glob-derived, EXCLUDING `*.grch38_backup.tsv.bgz`), output the
       config-parameterized `catalog`, params carrying the sorted manifest and excludelist
       globs plus the `--allow-degraded` switch, a log under `logs/m3_occlusion/`, and
       `conda: M3_R_LD_ENV` (that env carries pandas and pyliftover). The rule MUST succeed
       with zero manifests and zero excludelists, because that is the state of the tree
       today and CI must stay green.

    8. Add to `config/pipeline.yaml`, immediately after the `ld_panel:` block so the two M3
       resolver blocks sit together:

           occlusion_lockstep:
             enabled: true
             ancestries: [AFR]
             catalog: "data/processed/occlusion/occlusion_catalog_m3.tsv"
             sumstats_dir: "data/processed/sumstats_harmonized_occl"
             variants_dir_name: "variants_occl"
             manifest_dir: "data/interim/aou_ld_exports/AFR_aou"
             excludelist_dir: "data/interim/aou_ld_exports/AFR_aou"
             allow_degraded: false

       Precede it with a comment naming the pre-registration (osf.io/az52u, file trsx5) and
       stating why the block is AFR-only: the EUR chain head is the public UKBB 337k panel,
       which carries no occlusion manifest.

    9. `include: "src/snakemake/rules/m3_occlusion_lockstep.smk"` in the top-level `Snakefile`,
       placed AFTER the `m3_public_eur_ld.smk` include (line 125) and BEFORE the QTL includes.

    DO NOT edit `occlusion_manifest.py`, `occlusion_present_rate_scan.py`,
    `occlusion_span_filter.py` or `drop_occluded_from_sumstats.py`. Their 0-line diff is a
    verified acceptance criterion. Everything this task needs is additive.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_occlusion_catalog_assembly.py tests/m3 -q &amp;&amp; git diff --exit-code -- src/python/occlusion_manifest.py src/python/occlusion_present_rate_scan.py src/python/occlusion_span_filter.py src/python/drop_occluded_from_sumstats.py src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R src/python/condition_ld_matrix.py</automated>
  </verify>
  <acceptance_criteria>
    - `tests/m3/test_occlusion_catalog_assembly.py` exists and all 7 named cases PASS.
    - Full `tests/m3` shows 0 failed and at least 420 passed. The 2026-07-16 baseline is
      0F / 420P / 31S: no regression, no newly skipped test.
    - `git diff --exit-code` is CLEAN for all four m3-07 modules AND for the three frozen
      contracts (plink_ld_to_npz.py, ld_npz_to_rds.R, condition_ld_matrix.py).
    - All four previously-zero-caller functions are now called from
      `src/python/assemble_occlusion_catalog.py`: grep counts for
      `enrich_occlusion_manifest`, `scan_present_rate`, `add_grch37_positions` and
      `aggregate_manifests|build_occlusion_catalog` are each at least 1.
    - `grep -c "occlusion_lockstep" config/pipeline.yaml` is at least 1.
    - `grep -c "m3_occlusion_lockstep.smk" Snakefile` is exactly 1.
    - `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile Snakefile
      --dry-run data/processed/occlusion/occlusion_catalog_m3.tsv` exits 0.
    - Running the CLI with zero manifests writes a header-only catalog whose header contains
      BOTH `chr` and `pos_grch37`.
  </acceptance_criteria>
  <done>
    The genome-wide occlusion catalog has a real producer. The four functions m3-07b/07c
    shipped with zero callers are on the DAG. The catalog is schema-complete even when empty,
    so the consume seam in Task 2 is runnable today as an audited no-op and becomes live the
    moment the fire banks real per-region manifests.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: The lockstep consume seam — occlusion-filtered AFR sumstats AND variant list, both wired into run_finemap</name>
  <files>src/python/occlusion_lockstep_cli.py, src/snakemake/rules/m3_occlusion_lockstep.smk, src/snakemake/rules/finemap.smk, tests/m3/test_occlusion_lockstep_wiring.py</files>
  <read_first>
    - src/python/drop_occluded_from_sumstats.py (WHOLE FILE; the module docstring's "THE DEFERRED m3-04 SEAM — READ BEFORE WIRING" section at :49-56 names THIS plan)
    - tests/m3/test_occlusion_lockstep_drop.py (the CONTRACT; note the fixtures use PLAIN .tsv in and out)
    - src/snakemake/rules/finemap.smk :86-158 (run_finemap inputs, and the m3-02e B-1 boundary comment that declares this replan)
    - src/snakemake/rules/ld_reference.smk :203-225 (collect_region_variants — the second leak)
    - src/snakemake/rules/sumstats.smk :123-158 (the bgzip + tabix + envs/python_stats.yml convention to mirror)
  </read_first>
  <behavior>
    RED-first. `tests/m3/test_occlusion_lockstep_wiring.py`:

    T2.1 test_filter_sumstats_cli_writes_real_gzip — the `filter-sumstats` subcommand, given
      a bgzipped input and an out path ending `.tsv.bgz`, produces a file that
      `gzip.open(...).readline()` can read (magic `\x1f\x8b`). THIS IS THE CASE THAT CATCHES
      THE SHIPPED MODULE'S PLAIN-BYTES OUTPUT: `drop_occluded_from_sumstats` writes
      UNCOMPRESSED and `run_susie_rss.R` reads with `gunzip -c`.

    T2.2 test_filter_sumstats_preserves_counts — the emitted JSON satisfies
      `n_in - n_dropped == n_out`, and `n_out` equals the decompressed body-line count.

    T2.3 test_filter_variants_reuses_the_same_function — `filter-variants` drops the
      occluded (CHR,POS) from a plain 5-column variant list (`CHR POS SNP_ID REF ALT`) and
      leaves survivors byte-identical.

    T2.4 test_afr_inputs_are_repointed — with `occlusion_lockstep.enabled: true`, the
      resolved `run_finemap` sumstats path for an AFR wildcard set lives under
      `sumstats_dir`, and the resolved variants path lives under `variants_occl`.

    T2.5 test_non_afr_input_paths_are_byte_identical — for EUR, and for any ancestry not in
      `occlusion_lockstep.ancestries`, the two resolved path strings are
      character-for-character the legacy expressions
      `{HARMONIZED_DIR}/{trait}.{ancestry}.tsv.bgz` and
      `{ld_reference}/variants/{region}.tsv`. Track-A / EUR numerics must not move.

    T2.6 test_disabled_flag_restores_legacy_paths — `enabled: false` restores the legacy
      strings for AFR too. The kill switch works.

    T2.7 test_params_region_id_is_untouched — `run_finemap.params.region_id` still resolves
      through `REGION_SAFE_TO_ID` unchanged. It feeds `run_susie_rss.R --region`, which looks
      the id up in `config/regions_curated.csv`; swapping it would break the R script's
      region lookup. This is a guard rail for m3-04c, which DOES change the sibling
      `resolve_ld_path(region_id=...)` argument.

    Implement T2.4-T2.7 as pure-function tests over the two helper resolvers extracted in
    step 2, so they run without instantiating a Snakemake workflow.
  </behavior>
  <action>
    1. RED suite first. Commit `tests/m3/test_occlusion_lockstep_wiring.py` and confirm it
       fails before the implementation.

    2. Create `src/python/occlusion_lockstep_cli.py`, a THIN wrapper so
       `drop_occluded_from_sumstats.py` stays at 0-line diff. Two subcommands:

       * `filter-sumstats --in X.tsv.bgz --catalog C.tsv --out Y.tsv.bgz [--counts-json J]`
         writes the filtered rows to a temp PLAIN file via
         `drop_occluded_from_sumstats(in, catalog, tmp)`, then compresses with bgzip
         (`shutil.which("bgzip")`). If bgzip is absent, FAIL LOUDLY with `envs/python_stats.yml`
         named in the message. Do NOT silently fall back to `gzip`: that would break tabix
         indexability and hide an env misconfiguration. Emit the counts dict as JSON.
       * `filter-variants --in V.tsv --catalog C.tsv --out V_occl.tsv [--counts-json J]`
         calls the SAME function; no compression (the variant list is plain TSV in and out).

       Also expose the two path resolvers used by `finemap.smk`, so they are unit-testable:

           def lockstep_sumstats_path(trait, ancestry, config, harmonized_dir) -> str
           def lockstep_variants_path(region, ancestry, config, ld_reference_dir) -> str

       Both return the LEGACY string verbatim when
       `not config.get("occlusion_lockstep", {}).get("enabled", True)` or when `ancestry`
       is not in `config["occlusion_lockstep"].get("ancestries", ["AFR"])`.

    3. Add two rules to `src/snakemake/rules/m3_occlusion_lockstep.smk`:

       * `rule occlusion_filter_sumstats` — input the harmonized `{stem}.tsv.bgz` plus the
         catalog; output `{sumstats_dir}/{stem}.tsv.bgz` AND its `.tbi`; wildcard constraint
         `stem = r"[A-Za-z0-9_.\-]+\.AFR"` so it can never match a EUR stem; two logs
         (`{stem}.counts.json` and `{stem}.drops.log`, the latter capturing the module's
         per-drop STDERR, which is the in-run witness the pre-registration relies on);
         `conda: PYTHON_STATS_ENV` (the env that has bgzip and tabix); shell calls the CLI
         then `tabix -f -S 1 -s 1 -b 2 -e 2 {output.bgz}`, reproducing `sumstats.smk:157`
         exactly so the mirror keeps full parity with the source it shadows.
       * `rule occlusion_filter_variants` — input `{VARIANT_LIST_DIR}/{region}.tsv` plus the
         catalog; output `{LD_REF_DIR}/{variants_dir_name}/{region}.tsv`.

       The output directory MUST differ from the input directory
       (`sumstats_harmonized_occl` vs `sumstats_harmonized`, `variants_occl` vs `variants`).
       Same-directory wildcards would make each rule its own input and produce a DAG cycle.

    4. Edit `src/snakemake/rules/finemap.smk`:
       * import `lockstep_sumstats_path` and `lockstep_variants_path` from
         `occlusion_lockstep_cli` alongside the existing `resolve_ld_path` import. The
         `sys.path.insert` for `src/python` is already in place at :36-40.
       * replace `run_finemap.input.sumstats` with
         `lambda w: lockstep_sumstats_path(w.trait, w.ancestry, config, HARMONIZED_DIR)`.
       * replace `run_finemap.input.variants` with
         `lambda w: lockstep_variants_path(w.region, w.ancestry, config, config["paths"]["ld_reference"])`.
       * Retain the original expressions as `# OLD:` comments for audit, matching the house
         style already used for `ld_matrix` at :112-116.
       * Replace the `m3-02e (B-1) LD-BUILD BOUNDARY` block at :86-95. It currently declares
         `m3-04-W4-production-and-egress-PLAN.md` SUPERSEDED-PENDING-REPLAN. Update it to
         record that the replan LANDED as `m3-04b` (this plan) plus `m3-04c`, and that the
         deferred consume seam named in `drop_occluded_from_sumstats.py:49-56` is now WIRED
         here.
       * DO NOT touch `params.region_id` (:158) or `input.ld_matrix` (:124-131). The LD-path
         crosswalk change is m3-04c's, deliberately in a later wave so the two `finemap.smk`
         edits never collide.

    5. Update the `finemap.smk` module docstring to name the new seam, mirroring how the
       docstring already documents the m3-W3-T2 resolver change.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_occlusion_lockstep_wiring.py tests/m3 -q &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile Snakefile --dry-run --quiet &amp;&amp; git diff --exit-code -- src/python/drop_occluded_from_sumstats.py src/python/occlusion_manifest.py src/python/occlusion_present_rate_scan.py src/python/occlusion_span_filter.py src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R src/python/condition_ld_matrix.py</automated>
  </verify>
  <acceptance_criteria>
    - `tests/m3/test_occlusion_lockstep_wiring.py` exists and all 7 named cases PASS.
    - Full `tests/m3` shows 0 failed and at least 420 passed (no regression from the
      2026-07-16 0F / 420P / 31S baseline).
    - `git diff --exit-code` is CLEAN for the four m3-07 modules and the three frozen contracts.
    - `grep -c "lockstep_sumstats_path" src/snakemake/rules/finemap.smk` is exactly 1 and
      `grep -c "lockstep_variants_path" src/snakemake/rules/finemap.smk` is exactly 1.
    - `grep -c "REGION_SAFE_TO_ID" src/snakemake/rules/finemap.smk` is unchanged from before
      this task (params.region_id and the resolve_ld_path call are both untouched).
    - `grep -c "SUPERSEDED-PENDING-REPLAN" src/snakemake/rules/finemap.smk` is 0 (the stale
      declaration is replaced by the landed-replan record).
    - `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile Snakefile
      --dry-run --quiet` exits 0 with no cyclic-dependency error.
    - The filtered sumstats output is real gzip: `gzip.open(out).readline()` succeeds and the
      first two bytes of the file are `\x1f\x8b`.
  </acceptance_criteria>
  <done>
    The pre-registered exclude-in-lockstep policy is enforced end to end on the AFR path:
    the panel drops the occluded variant (m3-07b), the harmonized sumstats drop it
    (m3-07c filter, wired here), and the region variant list drops it (same filter, same
    manifest, same key). EUR and Track-A path strings are byte-identical, so no frozen
    numerics move. The seam is an audited no-op until the fire banks manifests, then live.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| AoU bucket to NCSU GPFS | Where the per-region occlusion manifests and `.occluded.excludelist` objects must cross. Today ONLY the excludelists are uploaded (`run_native_ld_panel.py:922-938`); the manifest is written to local scratch and never sent. This plan's degraded-reconstruction path is the honest response to that gap; the producer-side fix is m3-04c's PRE-FIRE item. |
| Occlusion catalog to harmonized sumstats | The catalog drives a DESTRUCTIVE filter on scientific data. A wrong, empty, or mis-keyed catalog silently changes what every downstream fine-map sees. |
| AFR filter to EUR / Track-A path | The filter must not reach EUR. Track-A numerics are frozen and byte-identity has been verified 16/16 in prior waves. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-m3-04b-01 | Tampering / integrity | occlusion catalog schema | mitigate | `drop_occluded_from_sumstats._load_manifest_keys` already fails CLOSED on a Stage-A (unlifted) manifest. Task 1 step 3 guarantees the Stage-B columns exist even for an EMPTY catalog, so the fail-closed path fires only on a genuinely malformed catalog and never on the legitimate no-op. T1.3 pins it. |
| T-m3-04b-02 | Repudiation / provenance | degraded excludelist reconstruction | mitigate | Degraded mode stamps `provenance_source=excludelist_degraded` on every row and REFUSES to run without an explicit `--allow-degraded`. Loss of the ref-span / occluder attribution is thereby visible in the artifact, not inferred from its absence. T1.5 + T1.6 pin both halves. |
| T-m3-04b-03 | Information disclosure | catalog columns crossing the egress boundary | mitigate | The catalog is built from `STAGE_A_COLUMNS`, which are coordinate/ID-only by construction (no genotypes, no per-person counts; REQ-AOU-LD-EGRESS). T1.7 re-runs the Stage-A token scan over the assembled catalog's own header, so a column cannot ride out through the rollup. |
| T-m3-04b-04 | Tampering | filtered mirror written uncompressed under a `.bgz` name | mitigate | `drop_occluded_from_sumstats` writes PLAIN bytes by contract; `run_susie_rss.R` reads with `gunzip -c`. The rule bgzips and tabix-indexes; the CLI fails loudly rather than falling back to plain `gzip`. T2.1 pins the gzip magic. |
| T-m3-04b-05 | Denial of service / scope creep | AFR filter reaching EUR or Track-A | mitigate | Ancestry gate in `lockstep_*_path` plus a rule-level wildcard constraint that cannot match a EUR stem. T2.5 asserts character-for-character identity of the EUR path strings; T2.6 pins the kill switch. |
| T-m3-04b-06 | Elevation of privilege / contract drift | an executor editing the 07b/07c modules to fit the plan | mitigate | `git diff --exit-code` over all four m3-07 modules AND the three frozen contracts is part of BOTH tasks' automated verify. The plan is additive by construction; nothing it needs requires editing them. |
| T-m3-04b-07 | Tampering | Snakemake DAG cycle from a same-directory filter rule | mitigate | Output directories are distinct by design (`*_occl`), and `snakemake --dry-run --quiet` over the whole workflow is in the automated verify. |
| T-m3-04b-08 | Information disclosure | STDERR drop log content | accept | The log names GRCh37 coordinates and manifest region/variant ids only — the same class of aggregate coordinate metadata the manifest itself is cleared to carry. No genotypes, no counts under 20. |
</threat_model>

<verification>
Plan-level checks, all NC-State, all $0, no perimeter:

1. `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3 -q`
   reports 0 failed and at least 420 passed (baseline 0F / 420P / 31S at 2026-07-16).
2. `git diff --exit-code -- src/python/occlusion_span_filter.py src/python/occlusion_manifest.py
   src/python/occlusion_present_rate_scan.py src/python/drop_occluded_from_sumstats.py`
   exits 0.
3. `git diff --exit-code -- src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R
   src/python/condition_ld_matrix.py` exits 0 (frozen contracts; m3-06 stays HELD).
4. `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile Snakefile
   --dry-run --quiet` exits 0.
5. `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile Snakefile
   --dry-run data/processed/occlusion/occlusion_catalog_m3.tsv` exits 0.
6. `grep -rn "condition_ld_matrix\|nan_to_num" src/python/assemble_occlusion_catalog.py
   src/python/occlusion_lockstep_cli.py src/snakemake/rules/m3_occlusion_lockstep.smk`
   returns nothing. NaN-to-0 is DEAD and must not be resurrected through this seam.
7. Commit tokens `(m3-04b-T1)` and `(m3-04b-T2)` appear in the git log, one atomic commit per
   task (RED and GREEN may be separate commits within a task, as in m3-07b/07c).
</verification>

<success_criteria>
- The genome-wide occlusion catalog has a production caller and a Snakemake rule; the four
  m3-07b/07c functions that shipped with ZERO callers are on the DAG.
- The catalog is schema-complete when empty, so the seam runs today as an audited no-op.
- `run_finemap` consumes occlusion-filtered AFR sumstats AND an occlusion-filtered AFR
  variant list. Both leaks are closed, not one.
- EUR / Track-A resolved path strings are byte-identical; frozen contracts and the four
  m3-07 modules are at 0-line diff.
- `tests/m3` has no reds and no new skips; the full-workflow dry run is clean.
- The m3-07c disclosed deferral ("the m3-04 consume-wiring stays a DISCLOSED deferral") is
  DISCHARGED, and `finemap.smk` no longer carries a SUPERSEDED-PENDING-REPLAN declaration.
</success_criteria>

<output>
After completion, create
`.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-W4-occlusion-catalog-and-consume-seam-SUMMARY.md`
recording:
- The exact `tests/m3` counts before and after (baseline 0F / 420P / 31S).
- Confirmation of the 0-line diff for all four m3-07 modules and all three frozen contracts.
- Any Rule-2 judgment call where the RED was silent, recorded rather than hidden (m3-07c
  precedent: three such calls were logged).
- The catalog's behaviour on the CURRENT tree (zero manifests, zero excludelists): header,
  row count, and the `n_dropped == 0` no-op result on one real AFR sumstats file.
- Whether `bgzip` resolved from `envs/python_stats.yml` on first use, and the exact conda env
  path Snakemake built.
- An explicit statement of what this plan does NOT cover, carried forward to m3-04c:
  panel reachability (curated-to-M2 crosswalk), the stale ingest/convert rules, the egress
  grouping, the Check-2 redefinition, and the in-perimeter fire.
</output>
