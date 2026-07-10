---
phase: m3-aou-afr-ld-panel-build
plan: 07b
type: execute
wave: 2
depends_on: ["07a"]
tags: [ld, occlusion, span-filter, provenance, manifest, aou, afr, tdd]
files_modified:
  - src/python/occlusion_span_filter.py
  - src/python/occlusion_manifest.py
  - src/python/aou_ld_panel.py
  - src/python/run_native_ld_panel.py
autonomous: true
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-VALIDATION
  - REQ-AOU-LD-EGRESS
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "occlusion_span_filter.detect_occluded_variants applies the CONSERVATIVE rule — V is occluded iff ∃ D with len(REF_D)>1 and POS_D < POS_V ≤ POS_D + len(REF_D)−1 — computed over the ORIGINAL window; on the region-1 `.bim` fixture (from 07a) it returns EXACTLY {1980475, 5733487, 5922718, 7492693, 8375822} (5 occluded; the 5922716/5922718/5922724 tangle collapses to the single 5922718 drop) and edges capture occluder→occluded incl. the second-order 5922718↔5922724 as disjoint."
    - "Footprint is len(REF)=len(A2) ONLY: an SNV (len(REF)=1) never occludes, and an insertion (len(ALT)>len(REF), footprint = single anchor base) never occludes a downstream base; a boundary variant at POS_D+len(REF_D)−1 IS occluded, one at POS_D+len(REF_D) is NOT (grep/test-verifiable in test_occlusion_span_filter.py)."
    - "build_plink_ld_command gains an optional `exclude=` param that appends `--exclude <path>` BEFORE `--r` only when non-None, and `--keep-allele-order` still appears on EVERY issued command (test_run_native_ld_panel.py -k exclude proves both)."
    - "process_region reads the raw window `.bim` BEFORE `_run_plink` (plain `_window_bim_n_var`, no retry — no concurrent writer), runs the filter, writes `{out_prefix}.occluded.excludelist` (one `.bim` col-2 id/line), passes it as `exclude=`, so the excluded window `.npz` carries NO NaN and PASSES content_verify_npz — the frozen read_square_bin NaN-raise never trips."
    - "Drop accounting is split: panel column `n_dropped_occluded` (APPENDED to _PANEL_COLUMNS, never reordered) = len(occluded_ids in-window); `n_dropped_monomorphic` = (raw_window_n_var − len(occluded_ids)) − window_n_var — the existing `_retained_window_bim` snplist-alignment fires automatically because exclusion makes bin_n_var != raw_window_n_var (no change to that machinery)."
    - "occlusion_manifest emits, per excluded variant, the Stage-A record (region_id, chr, variant_id, pos_grch38, ref, alt, ref_span_start/end_grch38, occluding_deletion_id, occluding_deletion_ref_len, reason='reference-occlusion → undefined-LD', occlusion_order) resume-safe (dedup by (region_id, variant_id)) plus an aggregate `occlusion_catalog.tsv` rollup — the genome-wide Angle-1/3 occlusion catalog. Stage-A is coordinate/id-only (egress-clean; REQ-AOU-LD-EGRESS)."
    - "Stage-B enrichment adds pos_grch37 via the ld_npz_to_rds.R liftover recipe (pyliftover, chain data/external/liftover/hg38ToHg19.over.chain.gz, pos−1 in / +1 out) + chain SHA-256 and matches the hinge-check values 5922716/5922718/5922724 → 5982776/5982778/5982784; traits_present columns are populated by the 07c present-rate scan (a documented seam)."
    - "Frozen contracts stay byte-unchanged: `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` is EMPTY and the run_native_ld_panel.py content_verify_npz body is untouched — the fix removes occluded rows UPSTREAM of `--r` so no NaN reaches the reader; m3-06 condition_ld_matrix.py is NOT touched (NaN→0 stays dead)."
  artifacts:
    - path: "src/python/occlusion_span_filter.py"
      provides: "Pure detect_occluded_variants(rows) -> (occluded_ids, edges); deterministic conservative deletion-span occlusion rule; stdlib only, no plink, no I/O"
      exports: ["detect_occluded_variants"]
      min_lines: 40
    - path: "src/python/occlusion_manifest.py"
      provides: "Per-region resume-safe occlusion manifest (Stage-A coordinate-only) + Stage-B liftover/chain-sha enrichment + aggregate occlusion_catalog.tsv rollup"
      exports: ["append_occlusion_rows", "enrich_occlusion_manifest", "build_occlusion_catalog"]
    - path: "src/python/aou_ld_panel.py"
      provides: "build_plink_ld_command extended with optional exclude= (--exclude before --r; --keep-allele-order invariant preserved)"
      contains: "exclude"
    - path: "src/python/run_native_ld_panel.py"
      provides: "process_region reordered to read raw window .bim + run occlusion filter + write exclude list BEFORE plink; n_dropped_occluded split; _PANEL_COLUMNS appended; Stage-A manifest hook"
      contains: "n_dropped_occluded"
  key_links:
    - from: "src/python/run_native_ld_panel.py"
      to: "src/python/occlusion_span_filter.py"
      via: "detect_occluded_variants on the raw window .bim rows BEFORE _run_plink"
      pattern: "detect_occluded_variants"
    - from: "src/python/run_native_ld_panel.py"
      to: "src/python/aou_ld_panel.py"
      via: "build_plink_ld_command(..., exclude=exclude_path)"
      pattern: "exclude="
    - from: "src/python/aou_ld_panel.py"
      to: "plink1.9 --exclude"
      via: "append --exclude <path> before --r when exclude is non-None"
      pattern: "--exclude"
    - from: "src/python/run_native_ld_panel.py"
      to: "src/python/occlusion_manifest.py"
      via: "append_occlusion_rows for the excluded ids/edges (Stage-A, in the loop)"
      pattern: "append_occlusion_rows"
    - from: "src/python/occlusion_manifest.py"
      to: "src/scripts/ld_npz_to_rds.R"
      via: "reuse the pyliftover GRCh38->GRCh37 recipe + chain SHA-256 (do NOT modify ld_npz_to_rds.R)"
      pattern: "hg38ToHg19"
---

<objective>
Plan **07b of the m3-07 split** — the core fix. Two tasks:
(T1) the overlapping-deletion **span-filter** (`occlusion_span_filter.py`) wired into the
panel-build path — exclude the occluded record from the LD window BEFORE plink `--r`
(`build_plink_ld_command(exclude=)` + `process_region` reorder + `n_dropped_occluded` split);
(T2) the **load-bearing provenance manifest** (`occlusion_manifest.py`) — Stage-A coordinate-only
per-region record + Stage-B liftover/chain-sha enrichment + the aggregate genome-wide
`occlusion_catalog.tsv` (Angle-1/3).

**Depends on 07a** (the OSF gate + the RED test scaffolds/fixture): `depends_on: ["07a"]`.
This plan turns the 07a RED tests for span_filter + manifest + the driver exclude/occlusion
behavior GREEN. The T3/T4 suites stay RED until 07c — that is EXPECTED; this plan's
verification is scoped to ITS OWN tests only.

The SCIENCE is settled (mechanism = occlusion `4543dcf4…`; policy = exclude-in-lockstep +
provenance `42d70167…`). Do NOT re-litigate. `NaN→0` is DEAD; m3-06 `condition_ld_matrix.py`
stays FROZEN/HELD and is NOT touched.

Output: `occlusion_span_filter.py`, `occlusion_manifest.py`, surgical edits to
`build_plink_ld_command` + `process_region` — all confirmable on synthetic + region-1's
characterized topology; frozen contracts git-diff-gated.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/amendments/m3_region1_nan_geometry_verdict.md
@.planning/amendments/m3_panel_occlusion_policy_decision.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-07a-W7-osf-gate-and-red-scaffold-PLAN.md
@src/python/run_native_ld_panel.py
@src/python/aou_ld_panel.py
@src/python/plink_ld_to_npz.py

# 07a authored the RED tests (test_occlusion_span_filter.py, test_occlusion_manifest.py, the extended
# test_run_native_ld_panel.py) + the region-1 fixture. This plan makes them GREEN. Do NOT modify the
# test files' expectations. m3-07-RESEARCH.md §1-4 is the code-path map (file:line insertion points).

<interfaces>
<!-- Contracts the executor needs. Extracted from the working tree @ m3-W2-aou-deltas. Use directly — no exploration. -->

The `.bim` REF-span crux is RESOLVED (RESEARCH §2). From src/python/plink_ld_to_npz.py:105-119 (load_bim — FROZEN, read only):
```
.bim columns: [chr, snp_id, cm, bp, A1, A2]. Under hl.export_plink: A1 = ALT (col 5, parts[4]);
A2 = REF (col 6, parts[5]). canonical vid = {chr}:{bp}:{A2}:{A1} = chr:pos:REF:ALT.
For a row: POS=int(parts[3]); REF=parts[5]; ALT=parts[4]; len(REF)=len(parts[5]).
Deletion: len(REF)>1; reference footprint = [POS, POS + len(REF) − 1].
Reuse `plink_ld_to_npz._read_bim_rows(path) -> list[list[str]]` (returns parts[:6]).
```

THE DETERMINISTIC OCCLUSION RULE (RESOLVED — conservative, RESEARCH §2 / §7 decisions 1+2):
```
Variant V is OCCLUDED iff ∃ another window variant D with len(REF_D) > 1 (a deletion) such that
    POS_D < POS_V ≤ POS_D + len(REF_D) − 1
computed over the ORIGINAL window (all in-window variants). Exclude every occluded V.
Insertions (len(ALT)>len(REF)) footprint = single anchor base -> NEVER occlude. SNVs never occlude.
Excluding the downstream occluded member removes every occlusion edge (occluder always has smaller POS).
```

From src/python/aou_ld_panel.py:2854 (build_plink_ld_command — EXTEND with exclude=):
```python
def build_plink_ld_command(bfile_prefix, chrom, from_bp, to_bp, out_prefix, mode="square",
                           ld_window_kb=3000, r2_floor=0.0, threads=None) -> list[str]:
# square argv today: plink1.9 --bfile <p> --keep-allele-order --chr <c> --from-bp <a> --to-bp <b>
#                    --mac 1 --nonfounders --write-snplist --r square bin4 --out <o>
# ADD: exclude: str | None = None  ->  when non-None, append ["--exclude", str(exclude)] BEFORE the
#      --r block (plink applies --exclude with the window + --mac before --r). --keep-allele-order
#      MUST remain on every command (test asserts). exclude=None -> argv byte-identical to today.
```

From src/python/run_native_ld_panel.py (the per-region seam — REORDER for T1):
```
_PANEL_COLUMNS (L99-105): region_id, chr, n_var, wall_min, peak_ram_gib, output_gib, status,
                          n_dropped_monomorphic   # APPEND n_dropped_occluded (never reorder leading cols)
_window_bim_n_var(bim_path, chrom, from_bp, to_bp) -> (n_var, window_bim_path)  # L275; plain read, PRE-plink safe
_needs_retained_subset(bin_n_var, raw_window_n_var) -> bool                     # L352; True when a drop occurred
_retained_window_bim(raw_window_bim, snplist, region_id=, expect_nonzero=)      # L365; snplist-order alignment (KEEP snplist retry)
_append_panel_row_local(tsv_path, row)                                          # L462; resume-safe dedup-by-region_id pattern to mirror
process_region square branch: L601-674 (build cmd -> _run_plink -> bin_n_var -> raw window -> retained subset -> n_dropped)
```

Liftover recipe (reuse from src/scripts/ld_npz_to_rds.R:167-183, chain SHA-256 at :96 — do NOT modify that file):
```python
from pyliftover import LiftOver
lo = LiftOver('data/external/liftover/hg38ToHg19.over.chain.gz')       # 1.2 MB, present
pos37 = lo.convert_coordinate('chr'+str(chrom), pos38 - 1)[0][1] + 1   # pos-1 in / +1 out
# hinge-check anchors: 5922716->5982776, 5922718->5982778, 5922724->5982784
```

Provenance manifest schema (Stage-A, per excluded variant): region_id, chr, variant_id, pos_grch38, ref, alt,
ref_span_start_grch38, ref_span_end_grch38 (from the OCCLUDING deletion), occluding_deletion_id,
occluding_deletion_ref_len, reason="reference-occlusion → undefined-LD", occlusion_order (direct|second_order).
Stage-B adds pos_grch37 + chain_sha256 (+ traits_present populated by 07c). NO genotypes, NO per-person counts.

Env = /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest (py3.11, numpy/pandas, no hail).
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1 (T1 — the core): occlusion_span_filter.py + build_plink_ld_command exclude= + process_region reorder + n_dropped_occluded</name>
  <read_first>
    src/python/occlusion_span_filter.py (to create), src/python/aou_ld_panel.py:2854-2913 (build_plink_ld_command),
    src/python/run_native_ld_panel.py:99-105,275-302,352-449,538-706 (_PANEL_COLUMNS, _window_bim_n_var,
    _needs_retained_subset/_retained_window_bim, process_region), src/python/plink_ld_to_npz.py:88-119,205-228
    (FROZEN — _read_bim_rows/load_bim contract + read_square_bin NaN-raise; read only), tests/m3/test_occlusion_span_filter.py + tests/m3/test_run_native_ld_panel.py (RED from 07a — do NOT edit expectations).
  </read_first>
  <files>src/python/occlusion_span_filter.py, src/python/aou_ld_panel.py, src/python/run_native_ld_panel.py</files>
  <behavior>
    - occlusion_span_filter.detect_occluded_variants(rows) -> (occluded_ids: list[str], edges: list[dict]).
      `rows` = list of 6-col sequences (idx 1=id, 3=bp, 5=A2=REF). Deterministic CONSERVATIVE rule over the
      ORIGINAL window: V occluded iff ∃ D (len(REF_D)>1) with POS_D < POS_V ≤ POS_D+len(REF_D)−1. Footprint =
      len(REF)=len(A2) ONLY. occluded_ids = sorted unique col-2 ids of every occluded V; edges = one dict per
      (occluder_id, occluded_id, geometry∈{"ref_span_overlap"}) — plus, for the tangle, a "disjoint"/second-order
      note that removing the upstream-occluded member also resolves the downstream NaN edge. Pure: no I/O, no plink.
      Validates each row is ≥6 fields with integer bp; RAISES ValueError on a malformed row.
    - Region-1 fixture -> EXACTLY {1980475,5733487,5922718,7492693,8375822} (5 ids; tangle collapses to 5922718).
    - build_plink_ld_command(..., exclude=None): when exclude is a non-None path, append `--exclude <path>` BEFORE
      the `--r` block; `--keep-allele-order` stays on EVERY command. exclude=None -> argv byte-identical to today.
    - process_region: read raw window `.bim` via plain `_window_bim_n_var` (NO retry — no concurrent writer pre-plink);
      parse rows; occluded_ids, edges = detect_occluded_variants(rows); if occluded_ids -> write
      `{out_prefix}.occluded.excludelist` (one col-2 id/line) and pass exclude=that; run plink; the existing
      `_needs_retained_subset`/`_retained_window_bim` path fires automatically (bin_n_var != raw_window_n_var) and
      aligns n_var/.bim/.npz to the snplist (snplist read keeps its Defect-1 retry). Split accounting:
      n_dropped_occluded = count of occluded ids in-window; n_dropped_monomorphic = (raw_window_n_var −
      n_dropped_occluded) − window_n_var. Append `n_dropped_occluded` to _PANEL_COLUMNS (never reorder leading cols)
      and to every result dict (None on skip/banded/error rows, mirroring n_dropped_monomorphic).
    - The excluded window `.npz` carries NO NaN and passes content_verify_npz — read_square_bin NaN-raise never trips.
  </behavior>
  <action>
    GREEN the 07a RED tests for the filter + the driver exclude/occlusion behavior. (1) Create
    src/python/occlusion_span_filter.py implementing detect_occluded_variants exactly per the rule in <interfaces>;
    stdlib only; may import `_read_bim_rows` from plink_ld_to_npz for parsing (the driver may parse and pass rows).
    Keep it pure + CI-runnable. (2) EXTEND build_plink_ld_command (aou_ld_panel.py:2854) with `exclude: str | None =
    None`; when non-None append `["--exclude", str(exclude)]` immediately before the `--r` block (both square and
    banded branches; square is the fire path). Do NOT alter `--keep-allele-order` / `--mac` / `--write-snplist`
    ordering. (3) REORDER process_region (run_native_ld_panel.py square branch): move `bim_path = f"{bfile_prefix}.bim"`
    + the raw window read to BEFORE `build_plink_ld_command`, using plain `_window_bim_n_var(bim_path, chrom, from_bp,
    to_bp)` (the pre-plink read has no concurrent writer, so the retry wrapper is unneeded — RESEARCH §1 step 2);
    parse raw_window_bim rows and call detect_occluded_variants; write the exclude list + pass `exclude=exclude_path`;
    run plink; keep the existing post-plink bin_n_var + `_needs_retained_subset`/`_retained_window_bim(...,
    expect_nonzero=(bin_n_var>0))` block UNCHANGED (it now fires because exclusion drops variants); compute the split
    n_dropped_occluded / n_dropped_monomorphic; append the panel column; emit a LOUD stderr line per region when
    n_dropped_occluded>0. Leave the banded branch and content_verify_npz body UNTOUCHED. Do NOT modify
    plink_ld_to_npz.py or ld_npz_to_rds.R. Commit GREEN, explicit paths, tag m3-07b-W7-T1.
  </action>
  <acceptance_criteria>
    - `pytest tests/m3/test_occlusion_span_filter.py -x` exits 0 (region-1 fixture -> the 5 expected ids; boundary/SNV/insertion cases pass).
    - `pytest tests/m3/test_run_native_ld_panel.py -k "exclude or occlusion or keep_allele" -x` exits 0 (exclude list written = occluded ids; `--exclude` in argv; `--keep-allele-order` on every call; `.npz` NaN-free passes content_verify_npz; n_dropped_occluded recorded + separated from n_dropped_monomorphic).
    - `grep -c "n_dropped_occluded" src/python/run_native_ld_panel.py` >= 1 AND it is APPENDED after n_dropped_monomorphic in _PANEL_COLUMNS.
    - `grep -c "exclude" src/python/aou_ld_panel.py` >= 1; `grep -c -- "--keep-allele-order" src/python/aou_ld_panel.py` unchanged (still present).
    - `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` is EMPTY.
  </acceptance_criteria>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_span_filter.py "tests/m3/test_run_native_ld_panel.py" -x -q</automated>
  </verify>
  <done>Occlusion filter GREEN on the region-1 fixture (5 ids); `--exclude` threads through build_plink_ld_command before `--r` with `--keep-allele-order` preserved; process_region excludes occluded rows upstream so the `.npz` is NaN-free and passes content_verify_npz; n_dropped_occluded split from n_dropped_monomorphic; plink_ld_to_npz.py + ld_npz_to_rds.R byte-unchanged.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2 (T2): occlusion_manifest.py — the load-bearing provenance manifest (Stage-A coordinate-only + Stage-B liftover) + aggregate catalog</name>
  <read_first>
    src/python/occlusion_manifest.py (to create), src/python/run_native_ld_panel.py:462-477 (_append_panel_row_local
    resume-safe pattern to mirror), src/scripts/ld_npz_to_rds.R:96,162-198 (liftover recipe + chain SHA-256 — reuse,
    do NOT modify), src/python/occlusion_span_filter.py (edges from T1), tests/m3/test_occlusion_manifest.py (RED from 07a — do NOT edit expectations),
    .planning/amendments/m3_panel_occlusion_policy_decision.md (the schema is load-bearing, not optional logging).
  </read_first>
  <files>src/python/occlusion_manifest.py, src/python/run_native_ld_panel.py</files>
  <behavior>
    - Stage A (in-perimeter-safe, coordinate/id-only — egress-clean): append_occlusion_rows writes one row per
      excluded variant to `{out_dir}/occlusion_manifest.tsv`, resume-safe (dedup by (region_id, variant_id) —
      mirror _append_panel_row_local). Columns: region_id, chr, variant_id, pos_grch38, ref, alt,
      ref_span_start_grch38, ref_span_end_grch38, occluding_deletion_id, occluding_deletion_ref_len, reason
      (constant "reference-occlusion → undefined-LD"), occlusion_order (direct|second_order). ref_span_* come from
      the OCCLUDING deletion (POS_D .. POS_D+len(REF_D)−1). NO genotypes, NO per-person counts (REQ-AOU-LD-EGRESS).
    - Stage B (NC-State enrichment): pos_grch37 via the ld_npz_to_rds.R liftover recipe (pyliftover, chain
      hg38ToHg19.over.chain.gz, pos−1 in/+1 out) + chain SHA-256 recorded for provenance; a `traits_present` /
      `n_traits_present` / `n_traits_scanned` column set that the 07c present-rate scan populates (documented seam).
      Liftover matches the hinge-check anchors (5922716/5922718/5922724 -> 5982776/5982778/5982784).
    - build_occlusion_catalog concatenates all per-region manifests into a genome-wide `occlusion_catalog.tsv`
      (the Angle-1/3 catalog seed). The second-order tangle is recorded honestly: one drop (5922718) resolving two
      NaN edges is a single manifest row with occlusion_order="second_order" noted (RESEARCH open-risk #6).
    - process_region calls append_occlusion_rows for the T1 occluded_ids/edges (Stage-A only, in the loop).
  </behavior>
  <action>
    GREEN the 07a manifest tests. Create src/python/occlusion_manifest.py: `append_occlusion_rows(out_dir,
    region_id, chr, edges, rows_by_id)` (Stage-A, resume-safe dedup — mirror _append_panel_row_local's
    exists/dedup/append logic with pandas), `enrich_occlusion_manifest(manifest_path, chain_path, present_rate=None)`
    (Stage-B: add pos_grch37 + chain_sha256 + traits_present; import pyliftover lazily so the Stage-A path needs no
    chain), and `build_occlusion_catalog(manifest_paths, out_path)` (concatenate to occlusion_catalog.tsv). Reuse the
    EXACT ld_npz_to_rds.R liftover convention (do NOT modify ld_npz_to_rds.R). Wire a Stage-A `append_occlusion_rows`
    call into process_region right where the T1 occluded_ids/edges are known (before the panel-row append), guarded
    so a manifest write never aborts the region (mirror the one-bad-region-never-aborts discipline). Commit GREEN,
    explicit paths, tag m3-07b-W7-T2.
  </action>
  <acceptance_criteria>
    - `pytest tests/m3/test_occlusion_manifest.py -x` exits 0 (Stage-A columns + ref_span + occluder + reason; resume-safe dedup; aggregate rollup).
    - `pytest tests/m3/test_occlusion_manifest.py -k liftover -x` passes OR skips cleanly if the chain is absent (asserts 5982776/5982778/5982784 when present).
    - `grep -c "reference-occlusion" src/python/occlusion_manifest.py` >= 1; `grep -c "append_occlusion_rows" src/python/run_native_ld_panel.py` >= 1.
    - `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` is EMPTY.
  </acceptance_criteria>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_manifest.py -x -q</automated>
  </verify>
  <done>Per-region resume-safe Stage-A manifest (coordinate/id-only) + Stage-B liftover/chain-sha enrichment + aggregate occlusion_catalog.tsv; liftover matches the hinge-check anchors; process_region emits manifest rows for the excluded set; frozen files byte-unchanged.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| window `.bim` (untrusted indel geometry) → occlusion filter | A malformed `.bim` row (bad bp, short row) crosses into detect_occluded_variants; a wrong footprint could over-/under-exclude and silently corrupt the panel. |
| occlusion manifest → egress boundary | Only aggregate coordinate/id metadata (Stage-A manifest) is designed to leave the AoU perimeter; individual-level `.bed/.bim/.fam` never egress (export_cohort_to_plink boundary). |
| occluded pair → plink `--r` → read_square_bin | An occluded `0/0 → NaN` reaching the frozen reader would trip the NaN-raise; the filter removes the record BEFORE `--r`. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-m3-07b-01 | Tampering | occlusion_span_filter (silent over-exclusion corrupts the panel) | mitigate | Deterministic conservative rule + manifest audits EVERY drop (T2) + `n_dropped_occluded` accounting; the 07a unit tests pin the EXACT excluded set {1980475,5733487,5922718,7492693,8375822} on the region-1 fixture; chains flagged (occlusion_order). |
| T-m3-07b-02 | Information disclosure | occlusion manifest (Stage-A) | mitigate | Stage-A manifest is coordinate/id-only (no genotypes, no per-person counts) — egress-clean by construction (REQ-AOU-LD-EGRESS); Stage-B enrichment runs NC-State. |
| T-m3-07b-03 | Tampering | occluded NaN reaches the fine-mapper | mitigate | Exclude BEFORE `--r` (T1) → the frozen read_square_bin NaN-raise never trips; the `.npz` is NaN-free by construction; frozen contracts git-diff-clean. |
| T-m3-07b-04 | Tampering (input validation, ASVS V5) | malformed `.bim` row into the filter | mitigate | detect_occluded_variants validates ≥6 fields + integer bp and RAISES ValueError on a malformed row (loud, not silent) — mirrors _read_bim_rows / _retained_window_bim guards. |
</threat_model>

<verification>
- Task 1 (T1): `pytest tests/m3/test_occlusion_span_filter.py tests/m3/test_run_native_ld_panel.py -x` all green; `--exclude` before `--r`; `--keep-allele-order` on every call; `.npz` NaN-free; `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` empty.
- Task 2 (T2): `pytest tests/m3/test_occlusion_manifest.py -x` all green (Stage-A schema + liftover anchors + rollup); frozen files byte-unchanged.
- Plan-scoped regression: `pytest tests/m3 -k "occlusion_span_filter or occlusion_manifest or run_native_ld_panel" -q` green. NOTE: the present-rate + lockstep suites stay RED until 07c — that is EXPECTED; do NOT gate this plan on them.
- Frozen-contract gate: `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` EMPTY; content_verify_npz body untouched; m3-06 condition_ld_matrix.py NOT touched.
- NO perimeter access, NO loop contact, NO re-fire. Unit-covered on synthetic + region-1's characterized topology; the real 276-region `.bim` run is gated/out-of-scope.
</verification>

<success_criteria>
- occlusion_span_filter clears the occlusion upstream of `--r`: the region-1 fixture yields exactly the 5 occluded ids (the tangle collapses to one drop), footprint = len(REF) only, and the excluded window `.npz` is NaN-free.
- `--exclude` threads through build_plink_ld_command before `--r` with `--keep-allele-order` preserved; process_region reads the window pre-plink, writes the exclude list, and splits n_dropped_occluded from n_dropped_monomorphic.
- The provenance manifest is load-bearing: per-variant Stage-A coordinate/id-only record + Stage-B both-build positions + chain-sha, resume-safe, rolled up into the genome-wide occlusion_catalog.tsv (Angle-1/3); traits_present is a documented 07c seam.
- Frozen contracts (read_square_bin NaN-raise, content_verify_npz, the raw `.npz` format, ld_npz_to_rds.R) are byte-unchanged; m3-06 condition_ld_matrix.py is NOT touched (NaN→0 stays dead).
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-07b-W7-span-filter-and-manifest-SUMMARY.md`.
Record: the region-1 fixture result (5 occluded ids; the tangle collapse); the frozen-contract git-diff-clean
confirmation; the Stage-A egress-clean manifest schema; the traits_present 07c seam; and the gated 276-region
real-`.bim` validation boundary (unit-covered on the region-1 fixture now — RESEARCH assumptions A1/A2).
</output>
