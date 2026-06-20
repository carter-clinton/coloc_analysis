---
quick_id: 260619-rqs
type: execute
mode: quick
autonomous: true
tdd: true
files_modified:
  - src/python/build_ld_region_manifest.py
  - tests/m3/test_build_ld_region_manifest.py
  - config/ld_regions.tsv
  - config/ld_regions_dev.tsv
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv
  - config/region_id_mapping.tsv
requirements: [REQ-AOU-LD-EGRESS, REQ-PATH-PARAMETERIZATION]

must_haves:
  truths:
    - "config/ld_regions.tsv carries m2_region_00040__sub00 compute rows for BOTH AFR and EUR"
    - "config/ld_regions.tsv carries m2_region_00145 __sub compute rows for BOTH ancestries"
    - "every __sub compute row has buffer_bp == 10_000_000 (NOT 50_000_000)"
    - "m2_region_00006 remains a single WHOLE medium row per ancestry (passthrough unchanged)"
    - "split_existing_manifest emits __sub rows byte-identical to build_manifest on shared geometry columns"
    - "config/ld_regions_dev.tsv carries m2_region_00040__sub00 for AFR and EUR (capped per DEV_SUBREGION_CAP)"
  artifacts:
    - path: "src/python/build_ld_region_manifest.py"
      provides: "split_existing_manifest() + shared _assemble_region_rows() helper + --split-existing-manifest CLI mode (XOR with --bed/--chain)"
      contains: "def split_existing_manifest"
    - path: "config/ld_regions.tsv"
      provides: "post-split 20-column manifest with __sub compute rows for the 8 xlarge parents"
      contains: "m2_region_00040__sub00"
    - path: "config/ld_regions_dev.tsv"
      provides: "regenerated dev subset with split-parent __sub substitution"
      contains: "m2_region_00040__sub00"
    - path: "tests/m3/test_build_ld_region_manifest.py"
      provides: "RED-first split-existing + faithfulness tests"
      contains: "split_existing"
  key_links:
    - from: "split_existing_manifest"
      to: "_assemble_region_rows"
      via: "shared row-assembly helper (same one build_manifest calls)"
      pattern: "_assemble_region_rows"
    - from: "config/ld_regions.tsv"
      to: "config/ld_regions_dev.tsv"
      via: "select_ld_regions_dev.py --manifest config/ld_regions.tsv"
      pattern: "select_ld_regions_dev"
---

<objective>
Regenerate the post-split LD region manifest (`config/ld_regions.tsv`) and its
dev subset (`config/ld_regions_dev.tsv`) by SPLITTING THE EXISTING committed
manifest in place (Path B), because the canonical `--bed`/`--chain` regen inputs
are gone (forward `hg19ToHg38` chain deleted — only `hg38ToHg19` remains; the M2
union BED is nowhere on the tree).

m3-02b shipped the xlarge-split CODE (`split_region_overlapping`, the split
branch in `build_manifest`, the `--subregion-buffer-mb` knob) but NEVER
regenerated the manifest. The committed `config/ld_regions.tsv` is still the
**OLD 12-column schema** (no `parent_region_id`/`subregion_index`/`buffer_bp`/
`core_*`/`window_*` columns, 0 `__sub` rows). The m3-02c cost probe needs the
8 xlarge parents (incl. `m2_region_00040` SH2B3 chr12 + `m2_region_00145` chr6
HLA) expressed as `__sub` compute rows.

Purpose: unblock m3-02c (it preflight-counts + cost-probes the post-split cells).
Output: a 20-column post-split `config/ld_regions.tsv` + regenerated
`config/ld_regions_dev.tsv` + a regenerated projection + mapping TSV, plus a NEW
`split_existing_manifest` entrypoint whose `__sub` rows are byte-identical (on the
shared geometry columns) to what `build_manifest` would emit.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@CLAUDE.md
@src/python/build_ld_region_manifest.py
@src/python/select_ld_regions_dev.py
@tests/m3/test_build_ld_region_manifest.py
@.planning/phases/m3-aou-afr-ld-panel-build/m3-02b-W2-rescope-split-stitch-code-SUMMARY.md

<critical_ground_truth>
Verified on disk 2026-06-19 (do NOT re-discover — these are load-bearing):

1. **The committed `config/ld_regions.tsv` is the OLD 12-column schema.** Header
   is exactly:
   `region_id, chr, start_grch37, end_grch37, start_grch38, end_grch38,
    ancestry, source_trait, lead_variant, radius_bp, region_class, liftover_status`
   It has **NO** split-provenance columns (`parent_region_id, subregion_index,
   n_subregions, core_start_grch38, core_end_grch38, window_start_grch38,
   window_end_grch38, buffer_bp`) and **0** `__sub` rows. 322 data rows (161
   regions x 2 ancestries; row count incl. header = 323).
   IMPLICATION: `split_existing_manifest` must OUTPUT the full 20-column
   `MANIFEST_COLUMNS` schema — it ADDS the 8 split columns (the existing rows
   do not carry them). For non-xlarge passthrough rows it must inject the
   whole-region convention (`parent_region_id=""`, `subregion_index=-1`,
   `n_subregions=1`, `core==window==region`, `buffer_bp=radius_bp`) — exactly as
   `build_manifest`'s WHOLE branch does.

2. **8 xlarge parents** (each x 2 ancestries = 16 rows), confirmed via
   `region_class=="xlarge"`: `m2_region_00040` (chr12, 37463740-126289702 b38),
   `m2_region_00060` (chr15), `m2_region_00088` (chr2), `m2_region_00111` (chr3),
   `m2_region_00120` (chr4), `m2_region_00145` (chr6 HLA), `m2_region_00146`
   (chr7), `m2_region_00161` (chr9).

3. **`source_trait` + `lead_variant` cannot be recomputed without the provenance
   JSON** (which lived in the gone BED). They are PRESENT in the existing manifest
   rows — CARRY THEM THROUGH per-row. Same for `start_grch37`/`end_grch37`
   (need the chain to recompute — carry through).

4. **The projection TSV** (`.planning/.../m3-region-class-projection.tsv`) and the
   **mapping TSV** (`config/region_id_mapping.tsv`) are ALSO the pre-split schema
   (projection has no `split_status`/`n_subregions`). The split-existing path
   regenerates BOTH (see DESIGN DECISIONS D3) — the projection from the split
   row assembly, the mapping from the standard `write_mapping(manifest_df)`.

5. **No `--bed`/`--chain` available.** Forward chain GONE; M2 BED GONE. This is
   exactly WHY Path B exists. Do NOT attempt to restore them.

6. pytest binary: `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest`
   (miniconda3 base has no pytest). Node PATH: prepend miniconda3/bin per
   project convention. Full `tests/m3` baseline (m3-02b SUMMARY) = 194 passed /
   0 failed / 30 skipped — keep 0 failed.
</critical_ground_truth>

<design_decisions>
The planner has MADE these calls (stated explicitly per the task):

**D1 — Entrypoint shape: BOTH a sibling function AND a CLI mode.**
Add `split_existing_manifest(in_manifest_df, *, subregion_buffer_mb,
max_subregion_span_mb, split_classes)` returning `(manifest_df, projection_df)`,
AND a `--split-existing-manifest IN.tsv` argparse mode. argparse must ENFORCE the
XOR: `--split-existing-manifest` is mutually exclusive with `--bed`/`--chain`
(explicit post-parse check raising an argparse error if both are given OR if
neither mode's required inputs are present). The function is the unit-test
surface; the CLI mode is the regen surface.

**D2 — Faithfulness via a SHARED row-assembly helper (the load-bearing reuse).**
FACTOR OUT of `build_manifest` the per-region SPLIT-branch + WHOLE-branch row/
projection assembly (current lines ~507-657) into a new module-level helper, e.g.:

  `_assemble_region_rows(*, region_id, chr_int_str, start_b37, end_b37,
   start_b38, end_b38, region_class, radius_bp, status, ancestries,
   trait_lead_fn, split_set, core_span_bp, buffer_override_bp) ->
   tuple[list[dict], list[dict]]`  # (manifest_rows, projection_rows)

where `trait_lead_fn(ancestry) -> (source_trait, lead_variant)`.
- `build_manifest` calls it post-liftover with
  `trait_lead_fn = lambda a: derive_source_trait_and_lead(prov, a)`.
- `split_existing_manifest` calls it reading grch38/region_class/radius/grch37/
  liftover_status STRAIGHT FROM the existing row, with
  `trait_lead_fn = lambda a: lookup[a]` built from the existing per-ancestry rows.
DO NOT reimplement `split_region_overlapping` or the row geometry — reuse via the
helper. The WR-01 SUBREGION_BUFFER_GUARD (lines ~520-536) MOVES INTO the helper so
split-existing ALSO refuses the silent 50 Mb footgun when no explicit buffer is
given. With `--subregion-buffer-mb 10` the guard never fires (explicit override
honored).

Refactor discipline: this is a pure extract-method. After the extract,
`build_manifest`'s output MUST be unchanged — the existing m3-02b tests
(`test_subregion_provenance_columns`, `test_buffer_bp_is_explicit_column_and_param`,
`test_nonxlarge_region_stays_whole`,
`test_default_buffer_parent_spanning_window_guard_raises`, etc.) are the
regression net. Run them GREEN after the extract, BEFORE adding
`split_existing_manifest`.

**D3 — split-existing rewrites BOTH projection AND mapping.**
`split_existing_manifest` returns `(manifest_df, projection_df)` (same shape as
`build_manifest`); the CLI mode writes the manifest, the projection (with
`split_status`/`n_subregions`), and — if `--out-mapping` given — calls the
existing `write_mapping(manifest_df, projection_df, path)` (derives purely from
the manifest, so it is faithful). The regen step (Task 2) passes all three
out-paths so all three are rewritten in place.

**D4 — Non-xlarge rows pass through with EXACT existing values + the whole-region
convention columns added.** The helper's WHOLE branch already does this for
`build_manifest`; split-existing gets identical output by sharing the helper. The
passthrough test asserts a sampled medium row (`m2_region_00006`) has its existing
12 columns identical pre/post and is NOT split.
</design_decisions>

<interfaces>
Key existing surfaces the executor reuses (src/python/build_ld_region_manifest.py):

```python
MANIFEST_COLUMNS = [  # the 20-col output schema split-existing must emit
  "region_id","chr","start_grch37","end_grch37","start_grch38","end_grch38",
  "ancestry","source_trait","lead_variant","parent_region_id","subregion_index",
  "n_subregions","core_start_grch38","core_end_grch38","window_start_grch38",
  "window_end_grch38","buffer_bp","radius_bp","region_class","liftover_status"]

DEFAULT_MAX_SUBREGION_SPAN_MB = 10.0   # core width
DEFAULT_SPLIT_CLASSES = "xlarge"
SUBREGION_WINDOW_PARENT_SPAN_GUARD_FRAC = 0.90  # WR-01 guard

def split_region_overlapping(start_b38, end_b38, core_span_bp, buffer_bp) -> list[dict]
    # dicts: {subregion_index, n_subregions, core_start, core_end, window_start, window_end}
def compute_radius_bp(start_b38, end_b38) -> int
def derive_region_class(start_b38, end_b38) -> str
def write_tsv(df, path) -> None
def write_mapping(manifest_df, projection_df, path) -> None
```

From src/python/select_ld_regions_dev.py:
```python
DEV_SUBREGION_CAP = 2
def select_dev_rows(manifest_df: pd.DataFrame) -> pd.DataFrame  # resolves split parents -> capped __sub
# CLI: --manifest <ld_regions.tsv> --out <ld_regions_dev.tsv>
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Extract shared row-assembly helper + add split_existing_manifest (RED-first)</name>
  <files>src/python/build_ld_region_manifest.py, tests/m3/test_build_ld_region_manifest.py</files>
  <behavior>
    RED-first. Add these tests to tests/m3/test_build_ld_region_manifest.py
    (reuse the existing `_IdentityChain` / `_build_split_manifest` patterns):

    - test_split_existing_emits_sub_rows_for_xlarge:
        Build a synthetic EXISTING-manifest DataFrame (OLD 12-col schema: one row
        per (region, ancestry)) with an xlarge `m2_region_00040` (chr12, a ~88 Mb
        b38 span) for AFR+EUR plus an xlarge chr6 `m2_region_00145` for AFR+EUR.
        Call `blm.split_existing_manifest(df, subregion_buffer_mb=10.0,
        max_subregion_span_mb=10.0, split_classes="xlarge")`. Assert: __sub rows
        exist for m2_region_00040 for BOTH AFR and EUR (region_id matches
        r"m2_region_00040__sub\d{2}$"); m2_region_00145 also yields __sub rows for
        both ancestries; the bare parent ids are ABSENT as compute rows.

    - test_split_existing_buffer_is_10mb:
        Every __sub compute row has buffer_bp == 10_000_000 (and != 50_000_000).

    - test_split_existing_cores_tile_parent_half_open:
        For one split parent (single ancestry), the __sub core_start_grch38/
        core_end_grch38 tile the parent [start_grch38, end_grch38) exactly:
        sub0.core_start == parent.start, last.core_end == parent.end, adjacent
        cores share a boundary (core_k.start == core_{k-1}.end).

    - test_split_existing_nonxlarge_passthrough_unchanged:
        Put a medium `m2_region_00006` row (specific source_trait, radius_bp,
        liftover_status) in the synthetic existing manifest. Assert output has
        exactly ONE row per ancestry for it, NOT split (no "__sub"), and the
        carried-through columns (start_grch37, end_grch37, start_grch38,
        end_grch38, source_trait, lead_variant, radius_bp, region_class,
        liftover_status) are IDENTICAL to the input row's values. Also assert the
        whole-region convention columns: subregion_index == -1, n_subregions == 1,
        parent_region_id == "".

    - test_split_existing_matches_build_manifest_faithfulness:
        THE faithfulness test. For ONE synthetic xlarge region with KNOWN coords:
        (a) run `build_manifest` on a one-row bed_df + _IdentityChain producing the
            same b38 coords (identity chain so b37==b38; subregion_buffer_mb=10.0,
            max_subregion_span_mb=10.0),
        (b) build the EQUIVALENT existing-manifest rows from build_manifest's
            PARENT coords (or directly from the same start/end), run
            `split_existing_manifest` with the same buffer/span,
        (c) assert the two __sub manifests are EQUAL row-for-row on the SHARED
            geometry columns: ["region_id","chr","ancestry","parent_region_id",
            "subregion_index","n_subregions","core_start_grch38","core_end_grch38",
            "window_start_grch38","window_end_grch38","buffer_bp","start_grch38",
            "end_grch38","region_class"] (sort BOTH by [region_id, ancestry] +
            reset_index first; compare the shared-column subset via
            assert_frame_equal or .equals).
        This proves the shared helper is the single source of geometry.

    - test_split_existing_cli_xor_with_bed:
        Invoke the module via subprocess with BOTH --split-existing-manifest and
        --bed -> nonzero exit (argparse error). Then invoke with
        --split-existing-manifest IN.tsv (a tiny written existing-manifest TSV) +
        --out-manifest/--out-projection + --subregion-buffer-mb 10 -> exit 0 and
        the output manifest contains __sub rows.

    All new tests FAIL first (split_existing_manifest / CLI mode absent), then PASS
    after implementation. The pre-existing m3-02b build_manifest tests must STILL
    PASS (the extract-method regression net).
  </behavior>
  <action>
    1. EXTRACT METHOD (no behavior change to build_manifest): pull the per-region
       SPLIT-branch + WHOLE-branch row/projection assembly out of `build_manifest`
       (lines ~507-657) into module-level `_assemble_region_rows(*, region_id,
       chr_int_str, start_b37, end_b37, start_b38, end_b38, region_class,
       radius_bp, status, ancestries, trait_lead_fn, split_set, core_span_bp,
       buffer_override_bp) -> tuple[list[dict], list[dict]]`. MOVE the WR-01
       SUBREGION_BUFFER_GUARD (lines ~520-536) inside this helper so BOTH callers
       get the guard. `build_manifest` becomes: liftover -> compute radius/class ->
       call `_assemble_region_rows(..., trait_lead_fn=lambda a:
       derive_source_trait_and_lead(prov, a))` -> extend its lists. Keep the
       failed-liftover projection branch in `build_manifest` (liftover-specific,
       not shared). Run the EXISTING m3-02b tests GREEN before step 2.

    2. ADD `split_existing_manifest(in_manifest_df, *, subregion_buffer_mb=None,
       max_subregion_span_mb=DEFAULT_MAX_SUBREGION_SPAN_MB,
       split_classes=DEFAULT_SPLIT_CLASSES) -> tuple[pd.DataFrame, pd.DataFrame]`:
       - normalize split_set + core_span_bp + buffer_override_bp exactly as
         build_manifest does.
       - group the existing manifest by region_id (each group = per-ancestry rows).
         For each group: read canonical fields from the FIRST row (region_id, chr,
         start_grch37, end_grch37, start_grch38, end_grch38, region_class,
         radius_bp, liftover_status); build a per-ancestry (source_trait,
         lead_variant) lookup from the group's rows; derive `ancestries` from the
         group's distinct ancestry values (preserve input order, AFR then EUR).
         chr_int_str = str(chr) with any "chr" prefix stripped (existing rows store
         bare ints — handle both). Coerce numeric coords to int.
       - call `_assemble_region_rows(..., trait_lead_fn=lambda a: lookup[a])`.
       - concat manifest rows -> DataFrame(columns=MANIFEST_COLUMNS); concat
         projection rows -> DataFrame. Return both.
       NOTE: split-existing does NOT liftover and does NOT recompute radius/class —
       it carries radius_bp/region_class/grch37 straight from the existing rows
       (chain gone; recomputation impossible AND unnecessary — geometry is
       GRCh38-only). region_class drives the split decision exactly as
       build_manifest.

    3. ADD CLI mode in `parse_args` + `main`:
       - Make `--bed`/`--chain` NOT unconditionally required (drop `required=True`;
         default None). Add `--split-existing-manifest IN.tsv` (type=Path,
         default None). Post-parse XOR check via `p.error(...)`: error if
         `split_existing_manifest` is set AND (`bed` or `chain`) is set; error if
         `split_existing_manifest` is None AND NOT (`bed` and `chain`).
       - In `main`: if `--split-existing-manifest` set, `pd.read_csv(sep="\t")`,
         call `split_existing_manifest(df, subregion_buffer_mb=args.subregion_buffer_mb,
         max_subregion_span_mb=args.max_subregion_span_mb,
         split_classes=args.split_classes)`, `write_tsv` manifest + projection, and
         if `--out-mapping` call `write_mapping(manifest_df, projection_df,
         args.out_mapping)`. Else: existing bed/chain path unchanged.

    GPFS/staging: explicit-path git add ONLY for
    src/python/build_ld_region_manifest.py + tests/m3/test_build_ld_region_manifest.py.
    NEVER `git add -A`.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && PATH=$HOME/miniconda3/bin:$PATH /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_build_ld_region_manifest.py -x -q</automated>
  </verify>
  <done>
    The 6 new split-existing tests PASS (incl. the faithfulness equality test);
    ALL pre-existing build_manifest/split tests in the file still PASS;
    split_existing_manifest + _assemble_region_rows + the --split-existing-manifest
    CLI XOR mode exist. No `git add -A` used.
  </done>
</task>

<task type="auto">
  <name>Task 2: Regenerate manifest + projection + mapping + dev manifest in place; full-suite regression</name>
  <files>config/ld_regions.tsv, .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv, config/region_id_mapping.tsv, config/ld_regions_dev.tsv</files>
  <action>
    1. Back up the current manifest to a non-tracked sidecar (NOT committed; used
       as the read source so the in-place rewrite does not race its own input):
       `cp config/ld_regions.tsv config/ld_regions.tsv.presplit.bak`
       Do NOT `git add` the .bak.

    2. Run the new split-existing CLI mode in place (PATH prepend per project
       convention), writing manifest + projection + mapping:

       PATH=$HOME/miniconda3/bin:$PATH python src/python/build_ld_region_manifest.py \
         --split-existing-manifest config/ld_regions.tsv.presplit.bak \
         --out-manifest config/ld_regions.tsv \
         --out-projection .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv \
         --out-mapping config/region_id_mapping.tsv \
         --subregion-buffer-mb 10 \
         --max-subregion-span-mb 10

       (--max-subregion-span-mb 10 is the DEFAULT but pass explicitly for the
       audit trail. --subregion-buffer-mb 10 = the Pan-UKBB band; the cost-probe
       INPUT value, NOT the final resolved band — see CAVEAT.)

    3. Regenerate the dev manifest from the new split manifest:

       PATH=$HOME/miniconda3/bin:$PATH python src/python/select_ld_regions_dev.py \
         --manifest config/ld_regions.tsv \
         --out config/ld_regions_dev.tsv

    4. Remove the .bak sidecar so it never gets staged:
       `rm config/ld_regions.tsv.presplit.bak`

    5. The verify block runs `verify_regen.py` (the must_have invariant checks:
       m2_region_00040__sub00 for AFR+EUR, region_00145 __sub present, all __sub
       buffer_bp==10000000, m2_region_00006 still whole medium, dev manifest carries
       m2_region_00040__sub00 AFR+EUR) THEN the full tests/m3 suite (keep 0 failed;
       baseline 194 passed / 0 failed / 30 skipped per the m3-02b SUMMARY, plus the
       6 new split-existing tests). Any NEW failure is a regression and blocks.

    CAVEAT to record (do NOT silently treat 10 Mb as final): the 10 Mb buffer is
    the documented Pan-UKBB lever the m3-02c probe will MEASURE — it is the
    cost-probe input, not the resolved AFR/EUR LD-decay band. m3-02c owns resolving
    the correct width + counting region_00145 chr6 density (may demand
    --max-subregion-span-mb 7 there). This regen uses 10 Mb because it is the
    effectively-mandatory split-realizing value per the m3-02b SUMMARY.

    GPFS/staging: explicit-path git add ONLY for config/ld_regions.tsv,
    config/ld_regions_dev.tsv,
    .planning/phases/m3-aou-afr-ld-panel-build/m3-region-class-projection.tsv,
    config/region_id_mapping.tsv. NEVER `git add -A`. Do NOT stage the .bak.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && PATH=$HOME/miniconda3/bin:$PATH python3 .planning/quick/260619-rqs-regenerate-post-split-ld-region-manifest/verify_regen.py && PATH=$HOME/miniconda3/bin:$PATH /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3 -q</automated>
  </verify>
  <done>
    config/ld_regions.tsv has the 20-col schema with __sub rows for all 8 xlarge
    parents (incl. m2_region_00040 + m2_region_00145), every __sub buffer_bp ==
    10_000_000, m2_region_00006 still a whole medium row; config/ld_regions_dev.tsv
    carries m2_region_00040__sub00 for AFR+EUR capped per DEV_SUBREGION_CAP;
    projection + mapping regenerated; full tests/m3 has 0 failed. .bak removed, no
    `git add -A`.
  </done>
</task>

</tasks>

<verification>
- verify_regen.py exits 0 (MANIFEST_REGEN_OK) — all 6 manifest/dev invariants hold.
- `pytest tests/m3/test_build_ld_region_manifest.py` — 6 new split-existing tests
  PASS incl. the build_manifest-vs-split_existing faithfulness equality; all
  pre-existing build_manifest/split tests still PASS.
- Full `pytest tests/m3` — 0 failed (baseline 194 passed + the 6 new = 200 passed
  expected; ~30 skipped unchanged).
- `git status` shows ONLY the 6 declared files modified (plus the quick-task
  planning dir); NO .presplit.bak staged; NO `git add -A` used.
</verification>

<success_criteria>
- config/ld_regions.tsv is the post-split 20-column manifest: 8 xlarge parents
  replaced by their __sub compute rows (m2_region_00040 + m2_region_00145
  confirmed for AFR+EUR), every __sub buffer_bp == 10_000_000, non-xlarge rows
  unchanged (m2_region_00006 stays whole medium).
- split_existing_manifest reuses _assemble_region_rows (the SAME helper
  build_manifest calls) — faithfulness test proves byte-identical __sub geometry.
- config/ld_regions_dev.tsv regenerated; carries m2_region_00040__sub00 AFR+EUR
  capped per DEV_SUBREGION_CAP=2.
- projection + mapping TSVs regenerated to the post-split schema.
- 10 Mb buffer caveat recorded (cost-probe input, NOT the final m3-02c band).
- Full tests/m3 green (0 failed). GPFS staging discipline honored.
</success_criteria>

<output>
After completion, create
`.planning/quick/260619-rqs-regenerate-post-split-ld-region-manifest/260619-rqs-SUMMARY.md`
recording: the split-existing entrypoint design (shared _assemble_region_rows
helper + CLI XOR), the regenerated row counts (manifest total, # __sub rows, dev
rows), the faithfulness-test result, and the 10 Mb-buffer-is-the-probe-input
caveat for m3-02c. Stage ONLY the declared files (explicit-path git add).
</output>
