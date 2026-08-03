---
phase: m3-aou-afr-ld-panel-build
plan: 04c
type: execute
wave: 2
depends_on: ["04b"]
files_modified:
  - src/python/build_curated_m2_crosswalk.py
  - src/python/plan_ld_egress.py
  - config/curated_to_m2_region_map.tsv
  - src/snakemake/rules/finemap.smk
  - src/snakemake/rules/m3_ingest_aou_ld.smk
  - src/snakemake/rules/m3_convert_npz_rds.smk
  - .planning/amendments/m3-egress-and-validation-protocol-addendum.md
  - .planning/amendments/aou-egress-audit-log.md
  - .planning/ROADMAP.md
  - tests/m3/test_curated_m2_crosswalk.py
  - tests/m3/test_m3_ingest_convert_destale.py
autonomous: false
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "The AFR_aou panel is REACHABLE from run_finemap. Today it is not: REGION_SAFE_TO_ID is built only from config/regions_curated.csv (12 curated Track-A slugs), while the AFR_aou chain head templates on {region_id} = m2_region_NNNNN. config/region_id_mapping.tsv contains ZERO curated slugs, so landing 276 .rds files would change nothing."
    - "The crosswalk changes ONLY the region_id argument passed to resolve_ld_path. run_finemap.params.region_id keeps resolving through REGION_SAFE_TO_ID, because it feeds run_susie_rss.R --region, which looks the id up in config/regions_curated.csv."
    - "A curated region with no M2 counterpart (BMI_Xq24 is chrX; M2 is autosomes-only per D-M2-09) is recorded as status=unmapped and falls through to the legacy chain, so the resolved path string is byte-identical to today's."
    - "m3_ingest_aou_ld.smk and m3_convert_npz_rds.smk match the REAL producer: AFR-only (EUR is the public UKBB 337k panel, EUR_aou will never be populated), 276 regions not 322 cells, and a region_id wildcard that admits the 123 subregion-split ids (m2_region_00040__sub00) the current r'm2_region_\\d{5}' silently excludes."
    - "The egress plan is produced by the EXISTING ld_egress_bundle.plan_egress_bundles. src/python/validate_bundle_sizes.py is NOT written: its function already shipped at ade6066."
    - "The egress UNIT is redefined and RECORDED: the producer writes per-region .npz DIRECTLY to gs://<bucket>/ld/AFR_aou/{region_id}.npz, so no stage exists at which a per-chromosome bundle OBJECT exists. Bundles are REQUEST-LEVEL groupings of object URIs, at most 22 AFR chromosome groups plus size splits, not 44."
    - "REQ-AOU-LD-VALIDATION Check 2 (AOU-LD-PIPELINE.md §9.2, 'AoU EUR vs 1000G EUR entry-wise r >= 0.97') is STRUCTURALLY UNRUNNABLE because there will be no AoU EUR panel. It is REDEFINED in writing, not silently dropped, and the redefinition is flagged for an OSF amendment-update because §9 is a pre-registered hard gate."
    - "The 50 GB egress ceiling is recorded as a CONSERVATIVE PROJECT WORKING CEILING, not a documented hard AoU API limit (ld_egress_bundle.py:9-15). The stale m3-04 plan treated it as hard fact."
    - "ROADMAP line 211 is replaced and m3-05 is marked SUPERSEDED-PENDING-REPLAN, because m3-05 inherits the same stale basis (322-row SHA-256 monolith, 44 sub-manifests, EUR_aou .rds, Path A.1/A.2/A.3 region counts)."
    - "Frozen contracts (plink_ld_to_npz.py, ld_npz_to_rds.R, condition_ld_matrix.py) and the four m3-07 modules keep a 0-line git diff."
  artifacts:
    - path: "src/python/build_curated_m2_crosswalk.py"
      provides: "Deterministic curated-region to M2-region crosswalk builder (GRCh37 interval containment, tightest-window tie-break, explicit unmapped status)"
      min_lines: 90
    - path: "config/curated_to_m2_region_map.tsv"
      provides: "12-row crosswalk: region_safe, curated_region_id, m2_region_id, chr, curated/M2 GRCh37 spans, containment, status"
    - path: "src/python/plan_ld_egress.py"
      provides: "Thin CLI over the EXISTING ld_egress_bundle.plan_egress_bundles; consumes a gsutil ls -l capture, emits the per-chromosome AFR egress request plan"
      min_lines: 60
    - path: "src/snakemake/rules/m3_ingest_aou_ld.smk"
      provides: "AFR-only ingest gate, widened region_id wildcard, 276-region manifest expectation, native-plink producer documented"
    - path: "src/snakemake/rules/m3_convert_npz_rds.smk"
      provides: "AFR-only .npz to .rds conversion; build_ld_rds_aou_eur retired with a documented reason"
    - path: ".planning/amendments/m3-egress-and-validation-protocol-addendum.md"
      provides: "The recorded egress-unit redefinition, the Check-2 redefinition (2a/2b/2c), and the EGRESS_CAP_GB provenance correction"
      min_lines: 90
    - path: ".planning/amendments/aou-egress-audit-log.md"
      provides: "APPENDED scope-correction section (44 bundles to at most 22 AFR groups). The file is append-only; the 2026-04-28 ruling text is never rewritten."
  key_links:
    - from: "src/snakemake/rules/finemap.smk"
      to: "config/curated_to_m2_region_map.tsv"
      via: "resolve_ld_path(region_id=...) argument"
      pattern: "curated_to_m2"
    - from: "src/snakemake/rules/m3_convert_npz_rds.smk"
      to: "data/processed/ld_reference/AFR_aou/{region_id}.rds"
      via: "build_ld_rds_aou_afr with a widened region_id wildcard"
      pattern: "__sub"
    - from: "src/python/plan_ld_egress.py"
      to: "src/python/ld_egress_bundle.py::plan_egress_bundles"
      via: "direct import; no reimplementation"
      pattern: "plan_egress_bundles"
---

<objective>
m3-04b closed the lockstep seam. This plan closes the three remaining gaps between "the panel
exists in a bucket" and "the panel is used", and then hands the billable fire to Carter.

**Gap 1 — the panel is UNREACHABLE.** `finemap.smk` translates a region via
`REGION_SAFE_TO_ID`, which the Snakefile builds ONLY from `config/regions_curated.csv` (12
curated Track-A slugs, whose `region_id` column is the slug itself). The `AFR_aou` chain head
templates on `{region_id}` = `m2_region_NNNNN`. `config/region_id_mapping.tsv` maps the M2
synthetic slugs (`r00001_1_10000_13506933`) to M2 ids and contains **zero** curated slugs.
So `resolve_ld_path` asks for `AFR_aou/FTO_16q12.rds` — a file the producer will never write —
and falls through to `AFR_1kg`. **Landing 276 `.rds` files changes nothing.** The CR-001
comment at `finemap.smk:118-123` asserts `REGION_SAFE_TO_ID` performs exactly this translation
("FTO_16q12 -> m2_region_00067"); it does not, and has not since it was written.

**Gap 2 — the ingest/convert rules describe a retired producer.** They gate on per-chromosome
flags for `AFR|EUR`, expect 322 cells, and carry a `build_ld_rds_aou_eur` rule reading a
directory that will never be populated (the EUR chain head has been `EUR_ukbb_pub` since
m3-02e). Their `region_id=r"m2_region_\d{5}"` wildcard silently excludes **123 of the 276**
subregion-split ids.

**Gap 3 — two pre-registered protocol items are unrunnable as written**, and must be
redefined in the open rather than dropped: the egress UNIT (there is no bundle object to size)
and REQ-AOU-LD-VALIDATION Check 2 (there will be no AoU EUR panel to compare).

Tasks 1 and 2 are NC-State, `$0`, no perimeter. Task 3 is the terminal blocking gate: the
in-perimeter arc is entirely Carter's trigger and needs the AoU VPC-SC perimeter, which is not
reachable from the NC State node.

Purpose: without Task 1 the ~11-day, ~$385-1,084 fire produces a panel nothing consumes.
Without Task 3's PRE-FIRE items the fire produces a panel whose pre-registered provenance
never leaves the perimeter.

Output: a curated-to-M2 crosswalk, a reachable `AFR_aou` chain head, de-staled ingest and
convert rules, an egress request planner built on the existing helper, two recorded protocol
redefinitions, an updated ROADMAP, and a fully enumerated human-action gate.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/amendments/AOU-LD-PIPELINE.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-02e-AFR-NATIVE-FIRE-BRIEF.md
@.claude/skills/aou-ld-pipeline/SKILL.md

Read ONLY lines 1-50 of `.planning/STATE.md` (732 KB file; the 2026-07-16 RESUME-HERE block
is authoritative). Read the STALE `m3-04-W4-production-and-egress-PLAN.md` for history only —
it is left in place deliberately and must NOT be edited or deleted.

<interfaces>
All VERIFIED against the live tree at HEAD `9fe26f6`.

--- THE REACHABILITY FACTS ---
    Snakefile:47-63   REGION_SAFE_TO_ID is built from config["paths"]["regions_curated"]
                      = config/regions_curated.csv -> 12 rows. Its region_id column holds the
                      curated slug itself, so REGION_SAFE_TO_ID["FTO_16q12"] == "FTO_16q12".
    config/regions_curated.csv ids: FTO_16q12, MC4R_18q21, SH2B3_12q24, APOL1_22q12,
                      PYHIN1_1q23, CXADR_F2RL1_6p21, BMI_5q13.3, BMI_Xq24, 9p21_CDKN2A,
                      APOE_19q13, HLA_6p21, SLC2A9_urate.   Columns: region_id, ancestry,
                      chr, start, end, lead_snp, gene, trait_list, source, canonical_pairs
                      (start/end are GRCh37 — config genome_build: GRCh37).
    config/region_id_mapping.tsv: 276 data rows, columns region_safe, region_id, source, notes.
                      region_safe values look like r00001_1_10000_13506933 and
                      r00161__sub12_9_120643630_131516640.  ZERO curated slugs present
                      (grep -c FTO_16q12 == 0).
    config/pipeline.yaml:218  AFR chain head =
                      data/processed/ld_reference/AFR_aou/{region_id}.rds
    finemap.smk:124-131  ld_matrix=resolve_ld_path(region_id=REGION_SAFE_TO_ID[w.region], ...)
    finemap.smk:158      params.region_id=REGION_SAFE_TO_ID[w.region]  <- MUST STAY AS-IS;
                      it feeds run_susie_rss.R --region against config/regions_curated.csv.
    src/python/ld_panel.py::resolve_ld_path(region_id, ancestry, config, region_safe=None)
                      substitutes {region_id} and {region_safe} INDEPENDENTLY. The fix is to
                      hand it the crosswalked M2 id while region_safe stays the curated slug.

--- THE REGION MANIFEST (config/ld_regions.tsv) ---
    552 data rows = 276 AFR + 276 EUR; 276 UNIQUE region_id (each id appears once per ancestry)
    123 of the 276 unique ids carry "__sub" (e.g. m2_region_00040__sub00)
    20 columns: region_id, chr, start_grch37, end_grch37, start_grch38, end_grch38, ancestry,
      source_trait, lead_variant, parent_region_id, subregion_index, n_subregions,
      core_start_grch38, core_end_grch38, window_start_grch38, window_end_grch38, buffer_bp,
      radius_bp, region_class, liftover_status
    region_class counts (over all 552 rows): 406 medium, 90 small, 56 large

--- THE REAL PRODUCER (off-DAG, in-perimeter) ---
    src/python/run_native_ld_panel.py  (native plink1.9, Hail-free, single AoU Cloud Analysis VM)
    :733       gs:// mode -> compute_dir is LOCAL SCRATCH
    :822       ocm.append_occlusion_rows(compute_dir, ...) -> {compute_dir}/occlusion_manifest.tsv
    :922-938   UPLOAD SET = {region_id}.npz, {region_id}.afreq, {region_id}.occluded.excludelist
               -> the occlusion manifest is NEVER uploaded.  See Task 3 PRE-FIRE item 1.
    :946-953   uploads are gated on ok (content_verify_npz passed)
    _reclaim_region_scratch globs {region_id}.* , so occlusion_manifest.tsv survives per-region
               reclaim but dies with the scratch / VM.
    Output layout: gs://<bucket>/ld/AFR_aou/{region_id}.npz   (per-region, DIRECT; no staging)
    Panel TSV:     gs://<bucket>/ld/AFR_aou/m3-W2-native-plink-panel.tsv  (9 columns since m3-07b)

--- REUSE, DO NOT REWRITE ---
    src/python/ld_egress_bundle.py (ade6066, m3-02d):
        EGRESS_CAP_GB = 50    # CONSERVATIVE PROJECT WORKING CEILING, not a hard AoU API limit
        plan_egress_bundles(cell_sizes: list[{region_id, chr, bytes}], cap_bytes=...) -> list[dict]
            returns {bundle_id, chr, region_ids, total_bytes, n_cells};
            within-chromosome greedy split to chrN_a / chrN_b when over the cap
        bundle_gib(bundle), n_bundles_over_cap(bundles), chromosomes_split(bundles)
    DO NOT create src/python/validate_bundle_sizes.py. Its function already shipped.

--- CURRENT STALE RULES ---
    m3_ingest_aou_ld.smk:120  ancestry=r"AFR|EUR"
    m3_ingest_aou_ld.smk:198-204  expand(..., ancestry=["AFR","EUR"], chr=1..22)  -> 44 flags
    m3_ingest_aou_ld.smk:322  region_id=r"m2_region_\d{5}"      <- misses 123 __sub ids
    m3_ingest_aou_ld.smk:74   comment "M2 region manifest path (322 rows...)"
    m3_ingest_aou_ld.smk:8-9  docstring mentions BlockMatrix bm/ dirs (Path A.3, RETIRED)
    m3_convert_npz_rds.smk:103,145  region_id=r"m2_region_\d{5}"  (both rules)
    m3_convert_npz_rds.smk:122-158  rule build_ld_rds_aou_eur      <- EUR_aou never populated
    build_ld_rds_aou_eur has NO code or test references outside .planning docs (verified by grep).

--- KNOWN-ANSWER CROSSWALK (planner-verified 2026-08-03 against the live tree) ---
    The algorithm in Task 1 step 2 was DRY-RUN on the real inputs. Use this as the oracle;
    if the executor's builder disagrees with any row, the builder is wrong.

      curated_region_id   chr  GRCh37 span              -> m2_region_id            status
      FTO_16q12           16   53800000-54400000        -> m2_region_00067         contained
      MC4R_18q21          18   56000000-56600000        -> m2_region_00078         contained
      SH2B3_12q24         12   111400000-112000000      -> m2_region_00040__sub00  contained  (18 candidates)
      APOL1_22q12         22   36200000-36600000        -> m2_region_00105         contained
      PYHIN1_1q23          1   158000000-162000000      -> m2_region_00008         contained
      CXADR_F2RL1_6p21     6   10300000-11800000        -> m2_region_00142         contained
      BMI_5q13.3           5   72000000-76000000        -> m2_region_00135         contained
      BMI_Xq24             X   118000000-122000000      -> (none)                  unmapped
      9p21_CDKN2A          9   21000000-23000000        -> m2_region_00159         contained
      APOE_19q13          19   44000000-46000000        -> m2_region_00083         contained
      HLA_6p21             6   25000000-35000000        -> m2_region_00143         contained
      SLC2A9_urate         4   9000000-11000000         -> m2_region_00114         contained

    11 of 12 map; only chrX is unmapped, exactly as D-M2-09 predicts.
    NOTE FTO_16q12 -> m2_region_00067. That is VERBATIM the example the CR-001 comment at
    finemap.smk:118-123 claims REGION_SAFE_TO_ID already produces. The intent was right; the
    implementation never existed. The crosswalk supplies it.
    NOTE SH2B3_12q24 has EIGHTEEN containing candidates, all subregions of the split parent
    m2_region_00040. The tightest-window tie-break is therefore load-bearing, not decorative,
    and it selects a SUBREGION — which is the scientifically right answer (a narrower window
    gives denser, better-conditioned LD for the same locus).

--- VALIDATION PROTOCOL STATE ---
    .planning/phases/m3-aou-afr-ld-panel-build/validation/ has 4 subdirs, ALL containing only
    .gitkeep. The 4-check protocol has never been run. AOU-LD-PIPELINE.md:423 calls it
    "a hard gate for promoting the pipeline from dev to production".
    §9.2 Check 2 = "AoU EUR vs 1000G EUR, mean entry-wise r >= 0.97 (MAF >= 0.05);
    >= 0.90 (MAF 0.01-0.05)".
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Panel reachability — curated-to-M2 region crosswalk, and the one resolver argument that has to change</name>
  <files>src/python/build_curated_m2_crosswalk.py, config/curated_to_m2_region_map.tsv, src/snakemake/rules/finemap.smk, tests/m3/test_curated_m2_crosswalk.py</files>
  <read_first>
    - Snakefile :44-63 (how REGION_SAFE_TO_ID is actually built — this is the root of the gap)
    - src/python/ld_panel.py (resolve_ld_path; note region_id and region_safe substitute independently)
    - src/snakemake/rules/finemap.smk :108-131 (the CR-001 comment that asserts a translation which does not exist) and :155-169 (params — do not touch)
    - config/regions_curated.csv (all 12 rows; note BMI_Xq24 is chrX and HLA_6p21 is the 69k-variant region)
    - config/ld_regions.tsv header + a few rows (start_grch37 / end_grch37 are the join columns)
  </read_first>
  <behavior>
    RED-first. `tests/m3/test_curated_m2_crosswalk.py`, importing the module inside each test:

    T1.1 test_crosswalk_covers_every_curated_region — the emitted TSV has exactly one row per
      row of `config/regions_curated.csv` (12), keyed on `region_safe`.

    T1.2 test_containment_wins_over_overlap — a synthetic curated interval fully inside two
      candidate M2 windows resolves to the TIGHTER window, deterministically, and is marked
      `status=contained`.

    T1.3 test_partial_overlap_is_marked_not_silently_promoted — a curated interval that no M2
      window contains but that overlaps one gets `status=partial` and records the overlap
      fraction. A partial match must never be presented as a clean containment.

    T1.4 test_chrx_region_is_unmapped — a chrX curated region (BMI_Xq24 in production) gets
      `m2_region_id` empty and `status=unmapped`. M2 is autosomes-only per D-M2-09.

    T1.5 test_resolver_receives_the_m2_id_for_mapped_regions — the `finemap.smk` helper
      returns the crosswalked `m2_region_NNNNN` for a mapped curated slug, so the `AFR_aou`
      chain head templates to `AFR_aou/m2_region_NNNNN.rds`.

    T1.6 test_unmapped_region_path_is_byte_identical_to_today — for an unmapped curated slug
      the helper falls back to `REGION_SAFE_TO_ID[region]`, so the resolved path string is
      character-for-character today's. No frozen numerics move.

    T1.7 test_params_region_id_still_uses_region_safe_to_id — a regression guard on the
      sibling argument. `params.region_id` feeds `run_susie_rss.R --region`, which looks the
      id up in `config/regions_curated.csv`; handing it an M2 id would break that lookup.
      (m3-04b T2.7 pins the same invariant from the other side; keep both.)

    T1.8 test_crosswalk_is_deterministic — building twice over the same inputs produces a
      byte-identical TSV (sorted, stable tie-break).
  </behavior>
  <action>
    1. RED suite first; commit; confirm failures are call-time, not collection errors.

    2. Create `src/python/build_curated_m2_crosswalk.py`:

           def build_curated_m2_crosswalk(regions_curated_csv, ld_regions_tsv, out_tsv) -> dict

       Algorithm, on the GRCh37 plane (the project's canonical analytic plane, D-01):
       * read `config/regions_curated.csv` -> (region_safe = the slug with `.` and `/`
         replaced by `_`, matching `Snakefile:49`; curated_region_id; chr; start; end).
       * read `config/ld_regions.tsv`, keep `ancestry == "AFR"` rows (all 276 unique ids are
         present under AFR), and use `start_grch37` / `end_grch37` as the M2 window.
       * CONTAINED: every M2 window with `m2_start <= curated_start` and
         `m2_end >= curated_end`. If any, pick the one with the SMALLEST span; break ties on
         `region_id` lexicographic ascending. `status="contained"`.
       * else PARTIAL: the M2 window with the largest intersection length. Record
         `overlap_bp` and `overlap_frac` (over the curated span). `status="partial"`.
       * else `m2_region_id=""`, `status="unmapped"`.
       * emit columns, in order: `region_safe, curated_region_id, chr, curated_start_grch37,
         curated_end_grch37, m2_region_id, m2_start_grch37, m2_end_grch37, overlap_bp,
         overlap_frac, status`. Sort by `region_safe`. Add an `argparse` `main()`.

       Chromosome comparison must strip a `chr` prefix on BOTH sides before comparing
       (`_chrom_match_key` in `run_native_ld_panel.py` exists precisely because a literal `==`
       against a `chr`-prefixed contig silently matched zero rows for 17 hours and banked
       0/276 — do not repeat it).

    3. Run the builder and COMMIT the emitted `config/curated_to_m2_region_map.tsv`. It is a
       reproducible config artifact, so it belongs in the repo (same convention as
       `config/region_id_mapping.tsv`).

    4. Edit `src/snakemake/rules/finemap.smk`:
       * load the crosswalk once at module scope into
         `CURATED_TO_M2: dict[str, str]`, skipping rows whose `status == "unmapped"` or whose
         `m2_region_id` is empty. If the file is absent, log a WARN and use `{}` — the DAG
         must still build on a fresh clone before the crosswalk rule has run.
       * change ONLY the `region_id=` argument of the `resolve_ld_path` call inside
         `input.ld_matrix` to
         `CURATED_TO_M2.get(w.region, REGION_SAFE_TO_ID[w.region])`.
       * leave `region_safe=w.region` unchanged (the 1kg / HGDP / UKBB tails template on it).
       * REPLACE the CR-001 comment block at :117-123 with the corrected account: the
         translation it claimed `REGION_SAFE_TO_ID` performed does not exist for curated
         regions, and the crosswalk is what actually performs it. Cite
         `config/curated_to_m2_region_map.tsv`.
       * DO NOT touch `params.region_id` at :158, and DO NOT touch the sumstats/variants
         lambdas that m3-04b landed.

    5. **RECORD, do not silently apply, the scientific consequence.** Add a comment above the
       crosswalk load stating plainly: the first curated AFR region whose `AFR_aou/.rds`
       exists will switch from the `AFR_1kg` panel to the AoU AFR panel and its fine-mapping
       numerics WILL change. That is the intended purpose of M3 (1000G AFR n=661 is the
       miscalibration this phase exists to fix), but it is a disclosable analysis change.
       Point at `config/pipeline.yaml ld_panel.pin.AFR` as the switch to hold it at a specific
       source while the change is disclosed, and carry it into the plan SUMMARY.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_curated_m2_crosswalk.py tests/m3 -q &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile Snakefile --dry-run --quiet &amp;&amp; git diff --exit-code -- src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R src/python/condition_ld_matrix.py src/python/occlusion_manifest.py src/python/drop_occluded_from_sumstats.py</automated>
  </verify>
  <acceptance_criteria>
    - `config/curated_to_m2_region_map.tsv` exists with 13 lines (header + 12 curated regions).
    - `awk -F'\t' 'NR>1 && $NF=="unmapped"' config/curated_to_m2_region_map.tsv` returns at
      least the `BMI_Xq24` row (chrX is out of the M2 autosome scope).
    - At least one curated region resolves to a real `m2_region_` id
      (`grep -c "m2_region_" config/curated_to_m2_region_map.tsv` is at least 1).
    - `grep -c "curated_to_m2\|CURATED_TO_M2" src/snakemake/rules/finemap.smk` is at least 2.
    - `grep -n "params:" -A 8 src/snakemake/rules/finemap.smk | grep -c "region_id=lambda"` is
      exactly 1 and still references `REGION_SAFE_TO_ID`.
    - Full `tests/m3` shows 0 failed and no new skips.
    - Full-workflow `snakemake --dry-run --quiet` exits 0.
    - Building the crosswalk twice yields byte-identical files (`md5sum` match).
  </acceptance_criteria>
  <done>
    The AoU AFR panel is reachable from `run_finemap` for every curated region that has an M2
    counterpart, and provably inert for those that do not. The latent CR-001 defect (a comment
    asserting a translation that does not exist) is corrected in code, not just in prose.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: De-stale the ingest/convert rules, build the egress request plan on the existing helper, and record the two protocol redefinitions</name>
  <files>src/snakemake/rules/m3_ingest_aou_ld.smk, src/snakemake/rules/m3_convert_npz_rds.smk, src/python/plan_ld_egress.py, .planning/amendments/m3-egress-and-validation-protocol-addendum.md, .planning/amendments/aou-egress-audit-log.md, .planning/ROADMAP.md, tests/m3/test_m3_ingest_convert_destale.py</files>
  <read_first>
    - src/snakemake/rules/m3_ingest_aou_ld.smk (WHOLE FILE)
    - src/snakemake/rules/m3_convert_npz_rds.smk (WHOLE FILE)
    - src/python/ld_egress_bundle.py (WHOLE FILE — the helper to REUSE; its docstring :9-15 carries the EGRESS_CAP_GB provenance correction verbatim)
    - .planning/amendments/AOU-LD-PIPELINE.md §7 (export protocol) and §9 (validation protocol, especially §9.2)
    - .planning/amendments/aou-egress-audit-log.md (note: the file declares itself APPEND-ONLY at line 10)
    - .planning/ROADMAP.md lines 200-215
  </read_first>
  <behavior>
    RED-first. `tests/m3/test_m3_ingest_convert_destale.py` — these are static rule-file
    contract tests (read the `.smk` text and assert on it) plus one behavioural test:

    T2.1 test_subregion_ids_match_the_region_wildcard — the `region_id` wildcard pattern in
      BOTH rule files matches `m2_region_00040__sub00` AND `m2_region_00001`. Drive this from
      the REAL manifest: assert every one of the 276 unique ids in `config/ld_regions.tsv`
      matches the compiled pattern. This is the case the current `r"m2_region_\d{5}"` fails
      for 123 ids.

    T2.2 test_ingest_is_afr_only — the ancestry wildcard constraint no longer admits EUR, and
      the aggregate expand no longer iterates EUR.

    T2.3 test_eur_aou_convert_rule_is_retired — `build_ld_rds_aou_eur` is absent from
      `m3_convert_npz_rds.smk`, and the file carries a comment naming `EUR_ukbb_pub` as the
      reason.

    T2.4 test_egress_plan_uses_the_shipped_helper — `plan_ld_egress` imports
      `plan_egress_bundles` from `ld_egress_bundle` and does not define its own bin-packer
      (assert `plan_egress_bundles` appears in the module source and no local function name
      contains `bin_pack` / `split_bundle`).

    T2.5 test_egress_plan_groups_by_chromosome_and_splits_over_cap — a synthetic size table
      with one 60 GB chromosome yields `chrN_a` / `chrN_b` sub-bundles, each at or under the
      cap; a 10 GB chromosome yields a single `chrN`.

    T2.6 test_no_validate_bundle_sizes_module — `src/python/validate_bundle_sizes.py` does NOT
      exist. The stale plan asked for it; its function shipped at `ade6066`.
  </behavior>
  <action>
    1. RED suite first; commit; confirm failures.

    2. `src/snakemake/rules/m3_ingest_aou_ld.smk`:
       * `ancestry=r"AFR"` in both `wildcard_constraints` blocks; `expand(..., ancestry=["AFR"], ...)`
         in `m3_ingest_aou_export_arrives_all` -> at most 22 flags, not 44.
       * `region_id=r"m2_region_\d{5}(__sub\d{2})?"`.
       * the inventory `run:` block filters the manifest on `ancestry == "AFR"` and reports the
         276-region scope in its error strings.
       * rewrite the module docstring: the producer is `src/python/run_native_ld_panel.py`
         (native plink1.9, Hail-free, single AoU Cloud Analysis VM) writing per-region `.npz`
         DIRECTLY to `gs://<bucket>/ld/AFR_aou/{region_id}.npz`. Delete the `bm/`
         BlockMatrix-shard language (Path A.3 is RETIRED) and the "322 rows" comment at :74.
       * keep the per-chromosome flag as the arrival gate: the egress runs over multiple
         weeks and partial arrival must still let partial conversion proceed.

    3. `src/snakemake/rules/m3_convert_npz_rds.smk`:
       * widen `region_id` in `build_ld_rds_aou_afr` identically.
       * RETIRE `build_ld_rds_aou_eur`. Replace the rule with a comment block recording why:
         m3-02e Move 2 made `EUR_ukbb_pub` the `ld_panel.EUR` chain head (public UKBB 337k,
         `$0` compute), so `data/interim/aou_ld_exports/EUR_aou/` will never be populated and
         the rule could only ever fail on a missing input. Reference
         `src/snakemake/rules/m3_public_eur_ld.smk` as the live EUR producer. Verified: the
         rule has no code or test references outside `.planning` docs.
       * update the module docstring accordingly.

    4. Create `src/python/plan_ld_egress.py` — a THIN CLI over the shipped helper:
       * `--sizes-tsv` (columns `region_id`, `chr`, `bytes`; produced from a
         `gsutil ls -l gs://<bucket>/ld/AFR_aou/*.npz` capture — the command belongs in the
         Task 3 gate, not here), `--cap-gb` (default `ld_egress_bundle.EGRESS_CAP_GB`),
         `--out`.
       * call `plan_egress_bundles` directly. Do NOT reimplement grouping or splitting.
       * emit `.planning/amendments/m3_egress_plan_AFR.tsv` with one row per bundle:
         `bundle_id, chr, n_cells, total_bytes, total_gb, region_ids`, plus a trailing summary
         of `n_bundles_over_cap` and `chromosomes_split`.

    5. Create `.planning/amendments/m3-egress-and-validation-protocol-addendum.md`. Three
       recorded decisions, each with its evidence:

       **(a) Egress UNIT redefinition.** The stale plan assumed a per-chromosome bundle OBJECT
       that could be sized and split. The real producer writes per-region `.npz` DIRECTLY to
       `gs://<bucket>/ld/AFR_aou/{region_id}.npz` (`run_native_ld_panel.py:922-938`); no stage
       exists at which a "chr1 AFR bundle" object exists. The bundle is therefore a
       REQUEST-LEVEL grouping of object URIs: at most 22 AFR chromosome groups, plus
       within-chromosome size splits, transferred with `gsutil -m cp` per group. Scope moves
       from 44 bundles (22 chr x 2 ancestries) to at most 22 (AFR only; EUR is the public
       UKBB 337k panel at `$0` on NC State).

       **(b) EGRESS_CAP_GB provenance correction.** 50 GB is a CONSERVATIVE PROJECT WORKING
       CEILING, NOT a documented hard AoU API limit (`ld_egress_bundle.py:9-15`). AoU's real
       mechanism is an alert threshold plus manual relaxation at egress-request time; the real
       number is confirmed on the first export. The stale m3-04 plan treated it as hard fact.

       **(c) REQ-AOU-LD-VALIDATION Check 2 redefinition.** AOU-LD-PIPELINE.md §9.2 requires
       "AoU EUR vs 1000G EUR entry-wise r >= 0.97". There will be no AoU EUR panel, so the
       check is STRUCTURALLY UNRUNNABLE. It is redefined into three parts, which together
       preserve a check that can actually FAIL:

       * **2a (HARD GATE, replaces §9.2).** *Code-path equivalence on a public substrate.* Run
         `run_native_ld_panel.process_region` over the public 1000G plink files already on
         disk (the LDSC `1000G_EUR_Phase3_plink` set), for 2-3 curated-overlapping windows,
         and compare the resulting `.npz` LD against an independent
         `plink1.9 --r square bin4 --keep-allele-order` computed directly on the same window.
         PASS: identical variant ordering and entry-wise `max |delta| <= 1e-6`. This validates
         the EXACT estimator plus IO path that produces the AFR panel — the same
         `--keep-allele-order`, the same `.ld.bin` reader, the same `.npz` writer and the same
         `lower_triangular` flag. `$0`, no perimeter, and it can fail for a real code reason.
         Honest limitation, to be stated in the memo: it validates the CODE, not the AoU
         substrate or the cohort QC.
       * **2b (REPORTED, explicitly NOT thresholded).** *AoU AFR vs 1000G AFR entry-wise
         Pearson r*, on shared variants at the validation regions, stratified by MAF. A
         threshold here would be scientifically wrong: 1000G AFR (n=661, continental African)
         and AoU AFR (n~73k, admixed African-American) differ in both population and n, and
         that divergence is the entire rationale for M1a (AOU-LD-PIPELINE.md §1). A LOW r is
         the expected and desired finding. Reporting the number IS the deliverable.
       * **2c (SANITY, not a hard gate).** *EUR_ukbb_pub vs 1000G EUR entry-wise r* at the same
         regions, MAF >= 0.05, expected r >= 0.90. This validates the EUR chain head actually
         shipped. The original 0.97 bar is inappropriate here: both panels are external and
         differ in n (337k vs 503).

       State plainly that §9 is a PRE-REGISTERED hard gate, so this redefinition requires an
       **OSF amendment-update posting before any redefined check is cited as passed** —
       mirroring the m3-07a gate discipline (draft by agent, POST by Carter, record the file
       GUID). Route it through the Task 3 gate.

    6. APPEND (never rewrite) a scope-correction section to
       `.planning/amendments/aou-egress-audit-log.md`. The file declares itself append-only at
       line 10 and its 2026-04-28 HARD GATE ruling text must remain byte-intact. The new
       section records: the M3 egress scope stated in the header (44 bundles, 22 chr x 2
       ancestries) is superseded to at most 22 AFR chromosome groups; the reason (m3-02e cost
       re-architecture: EUR moved to the public UKBB 337k panel, AFR moved to native plink);
       and a pointer to the protocol addendum. Do NOT edit the header line itself.

    7. `.planning/ROADMAP.md`:
       * REPLACE line 211's `m3-04` entry with:

             - [ ] m3-04b-W4-occlusion-catalog-and-consume-seam-PLAN.md + m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md
               — Wave 4 REPLANNED 2026-08-03. `m3-04-W4-production-and-egress-PLAN.md` is
               RETAINED AS HISTORY and is STALE on 9 axes (Hail/BlockMatrix substrate; 322
               cells vs 276 regions; symmetric AFR+EUR AoU build vs AFR-only + public UKBB
               EUR; 160-260 cluster-h / $5-10k vs ~263 VM-h / ~$385-1,084; per-chromosome
               bundle OBJECTS that never exist; the unreachable `m3_dev_complete.flag` gate;
               total silence on the occlusion lockstep; stale downstream ingest/convert rules;
               and a curated-to-M2 region crosswalk that never existed so the AFR_aou chain
               head was unreachable). It was NEVER EXECUTED — 5 of its 6 `files_modified`
               paths do not exist. The replan CONSUMES m3-02e's AFR-native `.npz` plus the
               public EUR `.rds`; it does not rebuild LD.
               **m3-04b** (autonomous, `$0`, NC State): occlusion catalog assembler giving the
               four zero-caller m3-07b/07c functions a production caller, plus the lockstep
               consume seam wiring occlusion-filtered AFR sumstats AND variant lists into
               `run_finemap` — discharging the m3-07c disclosed deferral.
               **m3-04c** (`autonomous:false`): curated-to-M2 crosswalk so the panel is
               reachable at all; de-staled ingest/convert rules (AFR-only, `__sub` region ids,
               `build_ld_rds_aou_eur` retired); egress request planner on the EXISTING
               `ld_egress_bundle.plan_egress_bundles`; recorded egress-unit and Check-2
               redefinitions; then the terminal Carter gate for the in-perimeter fire.
       * ADD to the m3-05 entry (line 212): **SUPERSEDED-PENDING-REPLAN (2026-08-03)** — it
         inherits the same stale basis (322-row SHA-256 monolith, 44 sub-manifests, `EUR_aou`
         `.rds`, "Path A.1/A.2/A.3 region count"). Replan AFTER the panel lands, when the real
         banked-region count and the real bundle count are observable rather than assumed.
       * Update the phase `**Plans**:` count line (200) to include m3-04b and m3-04c.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3/test_m3_ingest_convert_destale.py tests/m3 -q &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --snakefile Snakefile --dry-run --quiet &amp;&amp; test ! -e src/python/validate_bundle_sizes.py &amp;&amp; grep -q "Aggregate summary statistic" .planning/amendments/aou-egress-audit-log.md</automated>
  </verify>
  <acceptance_criteria>
    - Every one of the 276 unique region_id values in config/ld_regions.tsv matches the
      region_id wildcard pattern in BOTH m3_ingest_aou_ld.smk and m3_convert_npz_rds.smk
      (today 123 of them do not).
    - `grep -c "AFR|EUR" src/snakemake/rules/m3_ingest_aou_ld.smk` is 0.
    - `grep -c "rule build_ld_rds_aou_eur" src/snakemake/rules/m3_convert_npz_rds.smk` is 0,
      and `grep -c "EUR_ukbb_pub" src/snakemake/rules/m3_convert_npz_rds.smk` is at least 1.
    - `grep -ci "blockmatrix" src/snakemake/rules/m3_ingest_aou_ld.smk` is 0.
    - `test ! -e src/python/validate_bundle_sizes.py` exits 0.
    - `grep -c "plan_egress_bundles" src/python/plan_ld_egress.py` is at least 1.
    - `.planning/amendments/m3-egress-and-validation-protocol-addendum.md` exists, is at least
      90 lines, and contains `2a`, `2b`, `2c`, `CONSERVATIVE PROJECT WORKING CEILING`, and
      `OSF amendment-update`.
    - `.planning/amendments/aou-egress-audit-log.md` keeps its 2026-04-28 ruling byte-intact:
      `grep -q "Aggregate summary statistic"` succeeds AND `git diff` on that file shows only
      added lines.
    - `grep -c "m3-04b\|m3-04c" .planning/ROADMAP.md` is at least 2, and the m3-05 entry
      contains `SUPERSEDED-PENDING-REPLAN`.
    - Full tests/m3 shows 0 failed and no new skips; full-workflow snakemake --dry-run --quiet
      exits 0.
  </acceptance_criteria>
  <done>
    The consume path matches the real producer: AFR-only, 276 regions, subregion-split ids
    admitted, no retired EUR_aou rule, no reimplemented bundle sizer. The two protocol items
    that could not survive the m3-02e re-architecture are redefined in writing with their
    evidence, and the pre-registration consequence is routed to Carter rather than absorbed
    silently. The ROADMAP no longer advertises a plan that was never executed.
  </done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 3: The in-perimeter arc — PRE-FIRE fixes, the region-1 gate, the ~11-day billed fire, and egress</name>
  <files>none (Carter action; the agent verifies afterwards)</files>
  <action>See the human_gate block. No agent action. The agent's role is to verify the
  acceptance criteria after Carter completes the gate, and to re-run the m3-04b catalog rule
  once the real manifests land.</action>
  <human_gate>
    <gate>AoU perimeter: PRE-FIRE fixes, region-1 validation, the 276-region native-plink LD fire, and egress</gate>
    <description>
      Every step below needs the AoU VPC-SC perimeter, which is NOT reachable from the NC
      State node (the `wb` control plane works; `gsutil` / `gcloud` / `bq` are walled). All of
      it is Carter's trigger. The AoU VM is STOPPED-not-deleted and holds the
      `/home/jupyter/afr_cohort` bfile; `.npz` is 0/276; nothing is running; $0.
      Read `.claude/skills/aou-ld-pipeline/SKILL.md` before any perimeter contact.

      PRE-FIRE 1 — THE MANIFEST HAS NO PATH OUT OF THE PERIMETER (HIGH; decide before firing).
        `run_native_ld_panel.py:822` writes `{compute_dir}/occlusion_manifest.tsv`; in gs://
        mode `compute_dir` is LOCAL SCRATCH (:733); the upload set at :922-938 is ONLY `.npz`,
        `.afreq` and `.occluded.excludelist`. The manifest is never uploaded and dies with the
        scratch / VM. `_reclaim_region_scratch` globs `{region_id}.*`, so it survives per-region
        reclaim but not the VM.

        WHY IT IS NOT CODE IN m3-04b OR m3-04c: it edits the fire driver Carter is about to run
        for ~11 days, at exactly the moment the standing discipline says freeze-and-gate, and
        its only real verification is the fire itself. It belongs with the other PRE-FIRE items
        (panel-TSV rotate, real-.bim validation) under the same review, not buried in a
        plumbing plan. m3-04b is deliberately built NOT to depend on it.

        WHAT IS AND IS NOT LOST WITHOUT IT: the LOCKSTEP still works. Production varids are
        `chr:pos:ref:alt` on GRCh38 (run_native_ld_panel.py:391-400), so `chr` and `pos_grch38`
        are recoverable from the excludelists, which ARE uploaded — that is exactly what
        m3-04b's degraded reconstruction path is for. What is NOT recoverable is the occluder
        attribution, the REF spans, `occluding_deletion_ref_len`, and the reason / order labels
        — i.e. precisely the per-drop provenance the OSF amendment-update (osf.io/az52u, file
        `trsx5`) COMMITS TO PUBLISHING. So this is a PRE-REGISTRATION compliance item, not a
        mechanics item, and it should be treated with that weight.

        RECOMMENDATION: land it as its own reviewed `/gsd-quick` BEFORE the fire, uploading the
        manifest inside the existing `if ok:` block alongside the excludelist.
        RISK, STATED HONESTLY: `occlusion_manifest.tsv` is ONE file appended to by EVERY region.
        A bare `_gsutil_upload` overwrite races nothing on a single serial VM but would race
        under any future sharded fan-out, and the P3 lesson (`ff8cc47`) is that one upload
        helper serving two callers with opposite failure-safety needs silently destroyed banked
        provenance. LOWER-RISK OPTION, preferred: upload a PER-REGION
        `{region_id}.occlusion_manifest.tsv` so no object is ever overwritten —
        `aggregate_manifests` already expects a LIST of per-region manifests, and m3-04b's
        catalog rule already globs them.

      PRE-FIRE 2 — ROTATE THE STALE gs:// PANEL TSV (zero risk, zero compute cost).
        `gsutil stat <panel-uri>`; if present, `gsutil cat <uri> | head -1` must show 9
        tab-separated columns (the m3-07b `n_dropped_occluded` column sits at `_PANEL_COLUMNS`
        index 7); otherwise `gsutil rm`.
        "0/276 banked" is measured in `.npz` and does NOT evidence the TSV's absence: the
        `.npz`, not the TSV, gates the resume skip, and the June/July fires appended
        `status=error` rows unconditionally at :808 on both 7-column and 8-column code.

      PRE-FIRE 3 — THE GATED REAL-.bim VALIDATION.
        Byte-check that the occlusion exclude list computed on the REAL cohort `.bim` is exactly
        the five expected region-1 ids at 1980475, 5733487, 5922718, 7492693, 8375822.
        OPEN AND UNRESOLVED: the 0- vs 1-based index origin of
        `_REGION1_REAL_WINDOW_OCCLUDED_ROW_INDICES`. Settle it against the real `.bim` before
        trusting the comparison; an off-by-one here would validate the wrong rows.

      STEP A — REGION-1 RE-RUN GATE.
        Re-run region 1 ONLY. PASS = `.npz` count 0 -> 1, panel `status == ok`, `n_var` slightly
        under 102,421, `n_dropped_occluded` around 5 logged, no "not symmetric", no "Killed",
        no dmesg OOM. FAIL -> stop and report; do not proceed to 276.

      STEP B — THE FIRE (~263 VM-h, ~11 days, ~$385-1,084).
        `nohup` plus `timeout 312h`, server-side, on the STOPPED-not-deleted Cloud Analysis VM.
        LIVENESS IS THE GCS `.npz` OBJECT LISTING CLIMBING TO 276 — not the kernel light, not a
        `_SUCCESS` marker, not the log. Do NOT restart the kernel. Check in every 2-3 days.
        Teardown is UI-only (the in-perimeter pet SA has list-only Dataproc permissions), so
        there is no self-delete; the `timeout` wall-cap is the backstop.

      STEP C — SIZE AND PLAN THE EGRESS.
        `gsutil ls -l` over `ld/AFR_aou/*.npz` -> a `region_id, chr, bytes` TSV ->
        `python src/python/plan_ld_egress.py` -> `.planning/amendments/m3_egress_plan_AFR.tsv`.
        Expect at most 22 chromosome groups plus size splits. Confirm the REAL AoU egress
        threshold on the FIRST request: 50 GB is our working ceiling, not AoU's documented cap.

      STEP D — EGRESS TO NC STATE, PER GROUP.
        File the AoU egress request per group; `gsutil -m cp` the group's object URIs into
        `data/interim/aou_ld_exports/AFR_aou/`; ALSO fetch the `.occluded.excludelist` files,
        the `.afreq` sidecars, the panel TSV, and — if PRE-FIRE 1 landed — the occlusion
        manifest(s). Append one row per group to `.planning/amendments/aou-egress-audit-log.md`
        under `## Per-Bundle Audit Entries` with the Q12 schema, plus a per-group SHA-256
        sub-manifest under `.planning/amendments/sha256/`. Commit per group with token
        `(m3-04c-T3-chr{N}-AFR)`.

      STEP E — HAND BACK TO THE DAG.
        Re-run m3-04b's catalog rule: it now assembles the REAL catalog and the lockstep filter
        stops being a no-op. Then run the per-chromosome ingest flags and the `.npz` -> `.rds`
        conversion.

      STEP F — OSF AMENDMENT-UPDATE FOR THE CHECK-2 REDEFINITION.
        `.planning/amendments/m3-egress-and-validation-protocol-addendum.md` redefines a
        PRE-REGISTERED hard gate (AOU-LD-PIPELINE.md §9). Agent DRAFTS, Carter POSTS to
        osf.io/az52u, and the file GUID is recorded in-repo — the m3-07a discipline. No
        redefined check may be cited as PASSED before that posting is recorded.
    </description>
    <unblocks>the m3-05 replan (closeout + OSF), the M2-supplementary phase (slug m2-supp-aou-afr-rerun), and M4 genome-wide fine-mapping</unblocks>
    <how-to-resolve>
      1. Decide PRE-FIRE 1: land the manifest upload as a reviewed quick task (per-region file
         preferred), or accept the degraded excludelist reconstruction WITH the pre-registration
         consequence recorded in the SUMMARY.
      2. Run PRE-FIRE 2 and PRE-FIRE 3.
      3. Fire the region-1 gate; proceed only on PASS.
      4. Fire the 276-region loop; check in every 2-3 days against the GCS `.npz` count.
      5. Plan and file the egress; land the objects on GPFS; commit the audit rows.
      6. Re-run the catalog rule and the conversion rules.
      7. Type "approved" when all six are complete, or describe exactly where it stopped.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; NPZ=$(ls data/interim/aou_ld_exports/AFR_aou/*.npz 2&gt;/dev/null | wc -l) &amp;&amp; RDS=$(ls data/processed/ld_reference/AFR_aou/*.rds 2&gt;/dev/null | wc -l) &amp;&amp; CAT=$(tail -n +2 data/processed/occlusion/occlusion_catalog_m3.tsv 2&gt;/dev/null | wc -l) &amp;&amp; echo "npz=$NPZ rds=$RDS catalog_rows=$CAT of 276 planned" &amp;&amp; test "$NPZ" -gt 0 &amp;&amp; test "$RDS" -eq "$NPZ" &amp;&amp; test "$CAT" -gt 0 &amp;&amp; grep -q 'Aggregate summary statistic' .planning/amendments/aou-egress-audit-log.md &amp;&amp; /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python -m pytest tests/m3 -q</automated>
  </verify>
  <acceptance_criteria>
    - `ls data/interim/aou_ld_exports/AFR_aou/*.npz | wc -l` equals the number of regions the
      fire actually banked, and that number is recorded in the SUMMARY against the 276 planned.
      Do NOT hardcode 276 as a pass bar before the fire has run: a partial bank is a real,
      reportable outcome, not a failure to be papered over.
    - `ls data/processed/ld_reference/AFR_aou/*.rds | wc -l` equals the banked `.npz` count.
    - `data/processed/occlusion/occlusion_catalog_m3.tsv` has more than 0 data rows, and its
      `provenance_source` column is `stage_a_manifest` (PRE-FIRE 1 landed) or
      `excludelist_degraded` (it did not) — never absent, never mixed silently.
    - At least one `(m3-04c-T3-chr` commit token per egress group appears in the git log, with
      a matching SHA-256 sub-manifest under `.planning/amendments/sha256/`.
    - `.planning/amendments/aou-egress-audit-log.md` still contains its 2026-04-28 ruling text
      byte-intact.
    - The occlusion catalog's row count and the panel TSV's summed `n_dropped_occluded` agree,
      making "the panel and the sumstats dropped the same variants" a checked claim.
    - `pytest tests/m3` still shows 0 failed after the real artifacts land.
  </acceptance_criteria>
  <done>
    The AFR LD panel exists on GPFS, its occlusion provenance crossed the egress boundary in a
    recorded form (full or explicitly degraded), the lockstep filter is live rather than a
    no-op, and the audit log carries one row per egress group. m3-05 can be replanned against
    observed numbers instead of assumed ones.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| AoU bucket to NCSU GPFS | The production egress crossing. Only aggregate summary artifacts cross: per-region `.npz` LD, `.afreq`, `.occluded.excludelist`, the panel TSV, and (if PRE-FIRE 1 lands) the occlusion manifest. No `.bed` / `.bim` / `.fam` ever leaves the compute node (`run_native_ld_panel.py` docstring, REQ-AOU-LD-EGRESS). |
| Curated Track-A region namespace vs the M2 276-region namespace | The crosswalk is the ONLY place the two naming conventions meet. A wrong row silently points a fine-map at another locus's LD matrix. |
| Pre-registered protocol (OSF `az52u`) vs what is executable | Two §9 / §7 items cannot be run as written. Redefining them in-repo without an OSF amendment-update would be an undisclosed pre-registration deviation. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-m3-04c-01 | Tampering | curated-to-M2 crosswalk | mitigate | Containment beats overlap; a partial match is labelled `partial` and never promoted to `contained`; an unmapped region resolves to the byte-identical legacy path. Determinism (byte-identical rebuild) is pinned by T1.8. Chromosome comparison strips a `chr` prefix on both sides — a literal `==` against a `chr`-prefixed contig is the exact bug that banked 0/276 for 17 hours. |
| T-m3-04c-02 | Repudiation | occlusion manifest never leaving the perimeter | mitigate + transfer | m3-04b's degraded reconstruction makes the loss VISIBLE in the artifact (`provenance_source=excludelist_degraded`) rather than inferable from absence. The producer-side fix is escalated to Carter as PRE-FIRE 1 with its blast radius stated, because it edits the fire driver. |
| T-m3-04c-03 | Information disclosure | egress request grouping | mitigate | Grouping is REQUEST-LEVEL over already-egress-clean aggregate objects; `plan_egress_bundles` never touches genotypes. Every group gets an audit-log row (AoU request id, size, region ids, SHA-256 sub-manifest) under the 2026-04-28 HARD GATE classification. |
| T-m3-04c-04 | Tampering | the append-only audit log | mitigate | The scope correction is APPENDED; the 2026-04-28 ruling text stays byte-intact, enforced by a `git diff` additions-only acceptance check plus a grep for `Aggregate summary statistic`. |
| T-m3-04c-05 | Repudiation | Check-2 redefinition without disclosure | mitigate | The redefinition is written to a dated in-repo addendum with its evidence, and STEP F routes an OSF amendment-update through Carter before any redefined check may be cited as passed. Mirrors the m3-07a gate discipline. |
| T-m3-04c-06 | Denial of service | an ~11-day unattended billed fire | mitigate | `timeout 312h` hard wall-cap; 2-3 day check-in cadence; liveness measured as the GCS `.npz` listing, not the kernel light (the parked-thread false alarm that nearly triggered a wrong kill); resume-safe skip guard keyed on the banked `.npz`. |
| T-m3-04c-07 | Tampering | silent numerics change on curated AFR regions | mitigate | Task 1 step 5 records that the first curated AFR region with an `AFR_aou/.rds` switches panels and its fine-mapping numerics WILL change, and names `ld_panel.pin.AFR` as the hold switch. Disclosed, not absorbed. |
| T-m3-04c-08 | Spoofing / integrity | a stale 8-column gs:// panel TSV seeding the resume mirror | mitigate | PRE-FIRE 2 rotates it; `_append_panel_row_local` already raises on a column-count mismatch and `_gsutil_panel_object_size` fails CLOSED on an indeterminate stat (`ff8cc47`). |
| T-m3-04c-09 | Information disclosure | `.npz` triangle-flag disagreement | accept (already mitigated upstream) | `plink_ld_to_npz.py` writes `lower_triangular` and `ld_npz_to_rds.R` honours it; both are FROZEN here (0-line diff verified). No new `.npz` producer or consumer is introduced by this plan. |
</threat_model>

<verification>
Plan-level checks. Items 1-6 are NC-State, $0, no perimeter; items 7-8 apply only after the
Task 3 gate.

1. `pytest tests/m3 -q` reports 0 failed and no new skips (baseline 0F / 420P / 31S).
2. `git diff --exit-code` is clean for `plink_ld_to_npz.py`, `ld_npz_to_rds.R`,
   `condition_ld_matrix.py`, and the four m3-07 modules.
3. Full-workflow `snakemake --dry-run --quiet` exits 0.
4. Every one of the 276 unique `region_id` values in `config/ld_regions.tsv` matches the
   `region_id` wildcard in both M3 rule files.
5. `test ! -e src/python/validate_bundle_sizes.py` exits 0 (the helper already shipped).
6. `.planning/amendments/aou-egress-audit-log.md` diff shows additions only.
7. Banked `.npz` count equals the `.rds` count, and both are recorded against 276 planned.
8. The occlusion catalog row count agrees with the panel TSV's summed `n_dropped_occluded`.
</verification>

<success_criteria>
- The AoU AFR panel is REACHABLE: a curated region with an M2 counterpart resolves to
  `AFR_aou/m2_region_NNNNN.rds`, and an unmapped one resolves to the byte-identical legacy path.
- The ingest and convert rules describe the producer that actually exists: AFR-only, 276
  regions, subregion-split ids admitted, `build_ld_rds_aou_eur` retired.
- The egress plan is produced by the shipped `plan_egress_bundles`; no duplicate sizer exists.
- Both unrunnable protocol items are redefined in a dated, evidenced, in-repo addendum, and the
  OSF amendment-update is routed to Carter rather than skipped.
- The ROADMAP no longer advertises a never-executed plan, and m3-05 is marked for replan.
- The in-perimeter arc is fully enumerated with its PRE-FIRE decisions, its liveness signal,
  and its honest risk statement, and is gated on Carter.
</success_criteria>

<output>
After completion, create
`.planning/phases/m3-aou-afr-ld-panel-build/m3-04c-W4-panel-reachability-egress-and-fire-SUMMARY.md`
recording:
- The full 12-row crosswalk with each region's `status`, and which curated regions are now
  eligible to switch from `AFR_1kg` to `AFR_aou` (the disclosable numerics change).
- The PRE-FIRE 1 decision actually taken (manifest upload landed, or degraded reconstruction
  accepted) and, if degraded, an explicit statement of the pre-registered provenance not
  published.
- The region-1 gate result, the fire's wall clock and dollar cost against the ~263 VM-h /
  ~$385-1,084 estimate, and the banked region count against 276.
- The realised egress group count and per-group sizes against the at-most-22 projection, plus
  the REAL AoU egress threshold learned on the first request (vs our 50 GB working ceiling).
- Any region failures with their `status` strings from the panel TSV.
- The OSF amendment-update posting state for the Check-2 redefinition (GUID once posted).
- What m3-05 must now be replanned against: the observed banked-region count, the observed
  egress group count, AFR-only artifacts, and no `EUR_aou` `.rds`.
</output>
