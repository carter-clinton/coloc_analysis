---
phase: m3-aou-afr-ld-panel-build
plan: 07
type: execute
wave: 1
depends_on: []
tags: [ld, occlusion, span-filter, provenance, manifest, aou, afr, osf-prereg, present-rate]
files_modified:
  - .planning/amendments/osf-amendment-panel-occlusion-exclusion-2026-07-10.md
  - src/python/occlusion_span_filter.py
  - src/python/occlusion_manifest.py
  - src/python/occlusion_present_rate_scan.py
  - src/python/drop_occluded_from_sumstats.py
  - src/python/aou_ld_panel.py
  - src/python/run_native_ld_panel.py
  - tests/m3/test_occlusion_span_filter.py
  - tests/m3/test_occlusion_manifest.py
  - tests/m3/test_occlusion_present_rate_scan.py
  - tests/m3/test_occlusion_lockstep_drop.py
  - tests/m3/test_run_native_ld_panel.py
autonomous: false
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-VALIDATION
  - REQ-AOU-LD-EGRESS
  - REQ-OSF-PREREG
  - REQ-PUBLIC-DATA-ONLY
  - REQ-SNAKEMAKE-CI

must_haves:
  truths:
    - "The OSF gate is honored: `.planning/amendments/osf-amendment-panel-occlusion-exclusion-2026-07-10.md` exists describing the panel overlapping-variant policy = exclusion + provenance (never zeroing), it is POSTED to osf.io/az52u, and its OSF file id + SHA-256 + a git tag are RECORDED before any code task begins (mirrors the `tcujq` / 999.1 OSF-gate precedent)."
    - "occlusion_span_filter.detect_occluded_variants applies the CONSERVATIVE rule — V is occluded iff ∃ D with len(REF_D)>1 and POS_D < POS_V ≤ POS_D + len(REF_D)−1 — computed over the ORIGINAL window; on the region-1 `.bim` fixture it returns EXACTLY {1980475, 5733487, 5922718, 7492693, 8375822} (5 occluded; the 5922716/5922718/5922724 tangle collapses to the single 5922718 drop) and edges capture occluder→occluded incl. the second-order 5922718↔5922724 as disjoint."
    - "Footprint is len(REF)=len(A2) ONLY: an SNV (len(REF)=1) never occludes, and an insertion (len(ALT)>len(REF), footprint = single anchor base) never occludes a downstream base; a boundary variant at POS_D+len(REF_D)−1 IS occluded, one at POS_D+len(REF_D) is NOT (grep/test-verifiable in test_occlusion_span_filter.py)."
    - "build_plink_ld_command gains an optional `exclude=` param that appends `--exclude <path>` BEFORE `--r` only when non-None, and `--keep-allele-order` still appears on EVERY issued command (test_run_native_ld_panel.py -k exclude proves both)."
    - "process_region reads the raw window `.bim` BEFORE `_run_plink` (plain `_window_bim_n_var`, no retry — no concurrent writer), runs the filter, writes `{out_prefix}.occluded.excludelist` (one `.bim` col-2 id/line), passes it as `exclude=`, so the excluded window `.npz` carries NO NaN and PASSES content_verify_npz — the frozen read_square_bin NaN-raise never trips."
    - "Drop accounting is split: panel column `n_dropped_occluded` (APPENDED to _PANEL_COLUMNS, never reordered) = len(occluded_ids in-window); `n_dropped_monomorphic` = (raw_window_n_var − len(occluded_ids)) − window_n_var — the existing `_retained_window_bim` snplist-alignment fires automatically because exclusion makes bin_n_var != raw_window_n_var (no change to that machinery)."
    - "occlusion_manifest emits, per excluded variant, the Stage-A record (region_id, chr, variant_id, pos_grch38, ref, alt, ref_span_start/end_grch38, occluding_deletion_id, occluding_deletion_ref_len, reason='reference-occlusion → undefined-LD') resume-safe (dedup by (region_id, variant_id)) plus an aggregate `occlusion_catalog.tsv` rollup — the genome-wide Angle-1/3 occlusion catalog."
    - "Stage-B enrichment adds pos_grch37 via the ld_npz_to_rds.R liftover recipe (pyliftover, chain data/external/liftover/hg38ToHg19.over.chain.gz, pos−1 in / +1 out) and matches the hinge-check values 5922716/5922718/5922724 → 5982776/5982778/5982784; traits_present + n_traits_present come from the present-rate scan."
    - "occlusion_present_rate_scan reports PRESENT-vs-ABSENT rate per occluded variant (k/n) over the 9 public GRCh37 AFR harmonized sumstats (header CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD), auto-detecting CHR/POS cols — REQ-PUBLIC-DATA-ONLY (no perimeter, read-only)."
    - "drop_occluded_from_sumstats(sumstats_df, manifest, build='GRCh37') removes EXACTLY the manifest's GRCh37 (CHR,POS) rows (drop-only, no re-key — snp_id_bridge.R (CHR,POS) semantics), logs each drop, leaves non-occluded rows byte-identical, and is idempotent; wiring into the m3-04 consume seam is a DOCUMENTED deferred hook (finemap.smk:89-93 STALE/SUPERSEDED-PENDING-REPLAN)."
    - "Frozen contracts stay byte-unchanged: `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` is EMPTY and the run_native_ld_panel.py content_verify_npz body is untouched — the fix removes occluded rows UPSTREAM of `--r` so no NaN reaches the reader."
  artifacts:
    - path: ".planning/amendments/osf-amendment-panel-occlusion-exclusion-2026-07-10.md"
      provides: "The scoped OSF amendment-update: panel overlapping-variant policy = exclusion + provenance, never zeroing (the HARD GATE artifact)"
      contains: "exclusion"
    - path: "src/python/occlusion_span_filter.py"
      provides: "Pure detect_occluded_variants(rows) -> (occluded_ids, edges); deterministic conservative deletion-span occlusion rule; stdlib only, no plink, no I/O"
      exports: ["detect_occluded_variants"]
      min_lines: 40
    - path: "src/python/occlusion_manifest.py"
      provides: "Per-region resume-safe occlusion manifest (Stage-A coordinate-only) + Stage-B liftover/traits enrichment + aggregate occlusion_catalog.tsv rollup"
      exports: ["append_occlusion_rows", "build_occlusion_catalog"]
    - path: "src/python/occlusion_present_rate_scan.py"
      provides: "Genome-wide present-rate-per-ancestry scan of occluded variants over the 9 AFR harmonized GRCh37 sumstats"
      exports: ["present_rate_for_variants"]
    - path: "src/python/drop_occluded_from_sumstats.py"
      provides: "Reusable manifest-driven (CHR,POS) drop-only lockstep sumstats filter; idempotent; wiring deferred to m3-04 replan"
      exports: ["drop_occluded_from_sumstats"]
    - path: "src/python/aou_ld_panel.py"
      provides: "build_plink_ld_command extended with optional exclude= (--exclude before --r; --keep-allele-order invariant preserved)"
      contains: "exclude"
    - path: "src/python/run_native_ld_panel.py"
      provides: "process_region reordered to read raw window .bim + run occlusion filter + write exclude list BEFORE plink; n_dropped_occluded split; _PANEL_COLUMNS appended; manifest hook"
      contains: "n_dropped_occluded"
    - path: "tests/m3/test_occlusion_span_filter.py"
      provides: "RED-first occlusion-rule tests incl. the region-1 .bim fixture (5 occluded), boundary/SNV/insertion cases"
      contains: "detect_occluded_variants"
    - path: "tests/m3/test_occlusion_manifest.py"
      provides: "RED-first manifest schema + ref_span + reason + resume-safe dedup + aggregate rollup + liftover (skip if chain absent)"
    - path: "tests/m3/test_occlusion_present_rate_scan.py"
      provides: "RED-first present-rate k/n on synthetic sumstats fixtures"
    - path: "tests/m3/test_occlusion_lockstep_drop.py"
      provides: "RED-first: drop = exactly manifest (CHR,POS); idempotent; non-occluded rows untouched"
    - path: "tests/m3/test_run_native_ld_panel.py"
      provides: "Extended: --exclude argv + --keep-allele-order preserved + occlusion integration (no NaN) + n_dropped_occluded/n_dropped_monomorphic split"
      contains: "exclude"
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
      via: "append_occlusion_rows for the excluded ids/edges"
      pattern: "append_occlusion_rows"
    - from: "src/python/occlusion_manifest.py"
      to: "src/scripts/ld_npz_to_rds.R"
      via: "reuse the pyliftover GRCh38->GRCh37 recipe + chain SHA-256 (do NOT modify ld_npz_to_rds.R)"
      pattern: "hg38ToHg19"
    - from: "src/python/drop_occluded_from_sumstats.py"
      to: "src/R/regularization/snp_id_bridge.R"
      via: "(CHR,POS) drop-only membership semantics (no re-key)"
      pattern: "CHR.*POS"
---

<objective>
Build the UPSTREAM, panel-build-stage **overlapping-deletion span-filter** for the
region-1-class NaN in the AoU AFR native-plink LD panel, plus its **load-bearing provenance
manifest**, a **genome-wide present-rate-per-ancestry scan**, and a **reusable lockstep
sumstats-side drop filter** — all NC-State code, no perimeter access, no loop re-fire.

The SCIENCE is settled and LOCKED in the byte-verified amendment doc-set (mechanism =
overlapping-deletion occlusion, `m3_region1_nan_geometry_verdict.md` `4543dcf4…`; policy =
exclude-in-lockstep + provenance, `m3_panel_occlusion_policy_decision.md` `42d70167…`; join
impact = `m3_region1_occlusion_hinge_check.md`). Do NOT re-litigate. This plan implements the
CODE.

Purpose: the raw panel `.npz` correctly RAISES on the region-1 NaN (`read_square_bin`);
this wave supplies the correct fix — remove the occluded record from the LD window BEFORE
plink `--r` so plink never computes the structurally-undefined `0/0 → NaN` pair, the frozen
NaN-raise never trips, and every dropped variant is auditable in a provenance manifest that
doubles as the Angle-1/3 genome-wide occlusion catalog. `NaN→0` is DEAD; m3-06
`condition_ld_matrix.py` stays FROZEN/HELD and is NOT touched here.

Output: `occlusion_span_filter.py`, `occlusion_manifest.py`, `occlusion_present_rate_scan.py`,
`drop_occluded_from_sumstats.py`, surgical edits to `build_plink_ld_command` + `process_region`,
and RED-first pytest suites — all confirmable on synthetic + region-1's characterized topology.

⚠ **EXECUTION ORDER (hard):** Task 1 is the OSF pre-registration HARD GATE. It BLOCKS every
code task (Tasks 2–6). No fix code lands until the amendment-update is POSTED to OSF and its
file id/SHA-256/git tag are RECORDED. Planning is complete now; code execution is gated on
Task 1.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/amendments/m3_region1_nan_geometry_verdict.md
@.planning/amendments/m3_panel_occlusion_policy_decision.md
@.planning/amendments/m3_region1_occlusion_hinge_check.md
@src/python/run_native_ld_panel.py
@src/python/aou_ld_panel.py
@src/python/plink_ld_to_npz.py

# The amendment doc-set is the SPEC OF RECORD for the SCIENCE (do NOT re-derive). This plan is
# the CODE. m3-07-RESEARCH.md is the code-path map (file:line insertion points, #1 crux
# resolution, reuse inventory). m3-06-W6-...-PLAN.md is the CONVENTION TEMPLATE (frontmatter
# shape + must_haves style + XML task structure).

<interfaces>
<!-- Contracts the executor needs. Extracted from the working tree @ m3-W2-aou-deltas. Use directly — no exploration. -->

The `.bim` REF-span crux is RESOLVED (RESEARCH §2). A plink `.bim` DOES carry full multi-char
indel allele strings. From src/python/plink_ld_to_npz.py:105-119 (load_bim — FROZEN, read only):
```
.bim columns: [chr, snp_id, cm, bp, A1, A2]. Under hl.export_plink:
  A1 = ALT = alleles[1]   (col 5, parts[4])
  A2 = REF = alleles[0]   (col 6, parts[5])
canonical vid = chr:pos:REF:ALT = {chr}:{bp}:{A2}:{A1}
So for a row: POS = int(parts[3]); REF = parts[5]; ALT = parts[4]; len(REF) = len(parts[5]).
A deletion has len(REF) > 1; its reference footprint is [POS, POS + len(REF) − 1].
```
Reuse the 6-col parser `plink_ld_to_npz._read_bim_rows(path) -> list[list[str]]` (returns parts[:6]).

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
#      MUST remain on every command (test asserts).
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

AFR harmonized sumstats (9 files, PUBLIC GRCh37) — data/processed/sumstats_harmonized/*.AFR*.tsv.bgz
header: `CHR  POS  REF  ALT  BETA  SE  P  EAF  N  SNP_ID  TRAIT  ANCESTRY  BUILD`

Panel↔sumstats join (src/R/regularization/snp_id_bridge.R:107-121): membership is (CHR,POS)-only,
FIRST record wins on a multi-allelic collision. The T4 drop keys on (CHR,POS); drop-only, NO re-key.

Test conventions (tests/m3/test_run_native_ld_panel.py:48-163): `_write_bim(path, rows)` where a row is
(chr, snp_id, cm, bp, A1, A2) with A1=ALT, A2=REF (indel -> multi-char A2); `_MockPlink` models
--mac/--write-snplist and records every argv; PROJECT_ROOT/src/python on sys.path; env =
/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest (py3.11, numpy/pandas, no hail).
</interfaces>
</context>

<tasks>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 1 (HARD GATE — BLOCKS Tasks 2–6): OSF pre-registration of the scoped panel overlapping-variant policy amendment-update</name>
  <read_first>
    .planning/amendments/m3_panel_occlusion_policy_decision.md (the settled policy — the doc restates it),
    .planning/amendments/m3_region1_nan_geometry_verdict.md (the mechanism it pre-registers),
    .planning/amendments/osf-amendment-afr-native-ld-nan-psd-2026-07-03.md (the tcujq / 999.1 OSF-gate PRECEDENT — mirror its shape + posting discipline).
  </read_first>
  <files>.planning/amendments/osf-amendment-panel-occlusion-exclusion-2026-07-10.md</files>
  <action>
    AUTONOMOUS PART (Claude, at execution): DRAFT `.planning/amendments/osf-amendment-panel-occlusion-exclusion-2026-07-10.md`
    per <what-built> below — the scoped amendment-update stating the panel overlapping-variant policy = exclusion +
    provenance, never zeroing, in original-research framing, citing the byte-verified anchors 4543dcf4 and 42d70167 and
    cross-linking osf.io/az52u. Commit the doc with explicit paths.
    HUMAN PART (Carter, BLOCKING — no CLI): POST the doc to osf.io/az52u and RECORD its OSF file id + SHA-256 + a git
    tag (PANEL-OCCLUSION-OSF-AMENDMENT-POSTED-2026-07-10) per <human-action>. ⛔ This task BLOCKS Tasks 2–6: NO fix code
    lands until the amendment is posted + recorded (mirrors the tcujq / AFR-NANPSD-OSF-AMENDMENT-POSTED-2026-07-04 precedent).
  </action>
  <what-built>
    Claude (autonomous part) DRAFTS `.planning/amendments/osf-amendment-panel-occlusion-exclusion-2026-07-10.md`
    — the scoped OSF amendment-update. It states, in original-research framing (never "fix/cleanup/revision"):
      (1) the panel overlapping-variant policy = **exclusion + provenance, never zeroing** — a variant whose
          LD is structurally undefined because an overlapping deletion's REF span makes it uncallable in the AoU
          AFR reference is EXCLUDED in lockstep from BOTH the LD panel and the harmonized sumstats, with an
          auditable provenance manifest (per-variant: ID + both-build positions + occluding deletion + REF span
          + locus + traits-present + reason=reference-occlusion→undefined-LD);
      (2) the deterministic upstream span-filter across all 276 regions (the conservative rule, cited from the
          geometry verdict — 5 direct ref_span_overlap + 1 second-order, 0 same-position);
      (3) NaN→0 is retired as directionally wrong (cite the concrete harm: rs182965575 present 7/9 AFR sumstats);
      (4) the genome-wide present-rate scan quantifies the scientific cost (Angle-1/3 catalog).
    Cite the byte-verified anchors (4543dcf4… / 42d70167…) and cross-link osf.io/az52u.
  </what-built>
  <human-action>
    Carter (carterclinton@ncsu.edu; researcher account cclinton@researchallofus.org is AUTH-ONLY — never email it):
    POST the drafted amendment-update to the OSF project **osf.io/az52u** (same project as the tcujq AFR NaN-PSD
    amendment), then RECORD provenance: the OSF file id + the file's SHA-256 + a git tag (pattern
    `PANEL-OCCLUSION-OSF-AMENDMENT-POSTED-2026-07-10`) on the commit that lands the amendment doc. This is a human
    web action with no CLI — Claude cannot post to OSF.
  </human-action>
  <acceptance_criteria>
    - `.planning/amendments/osf-amendment-panel-occlusion-exclusion-2026-07-10.md` exists and contains the strings
      "exclusion", "provenance", and "never zeroing" (or equivalent), AND cites both anchors `4543dcf4` and `42d70167`.
    - The amendment is POSTED to osf.io/az52u (human confirms the OSF file id).
    - The OSF file id + SHA-256 + git tag are RECORDED (in the commit message / STATE.md) BEFORE Task 2 starts.
    - ⛔ Tasks 2–6 MUST NOT begin until this gate is cleared (mirrors the `AFR-NANPSD-OSF-AMENDMENT-POSTED-2026-07-04` precedent).
  </acceptance_criteria>
  <verify>
    <automated>test -f .planning/amendments/osf-amendment-panel-occlusion-exclusion-2026-07-10.md && grep -qi 'exclusion' .planning/amendments/osf-amendment-panel-occlusion-exclusion-2026-07-10.md && grep -q '4543dcf4' .planning/amendments/osf-amendment-panel-occlusion-exclusion-2026-07-10.md && echo GATE_DOC_OK</automated>
    Note: the automated check confirms the DRAFTED doc only; the OSF POSTING + file-id/SHA-256/tag recording is the human resume-signal (no CLI).
  </verify>
  <done>The amendment-update doc exists (exclusion + provenance, never zeroing; anchors cited), is POSTED to osf.io/az52u, and its OSF file id + SHA-256 + git tag are RECORDED before Task 2 begins. Tasks 2–6 remain blocked until then.</done>
  <resume-signal>Reply "OSF posted: file id &lt;id&gt;, sha256 &lt;hash&gt;, tag &lt;tag&gt;" — then Tasks 2–6 are unblocked. If blocked, describe the blocker.</resume-signal>
</task>

<task type="auto">
  <name>Task 2 (Wave 0 — RED-first): occlusion test scaffolds + the region-1 `.bim` fixture helper</name>
  <read_first>
    tests/m3/test_run_native_ld_panel.py:40-163 (fixture helpers _write_bim/_default_bim_rows/_MockPlink/_setup_cohort + the argv-assertion test at 366-388),
    tests/m3/test_condition_ld_matrix.py + tests/m3/test_nan_guard.py + tests/m3/conftest.py (RED-first + PROJECT_ROOT/sys.path + skip-if-no-chain conventions),
    m3-07-RESEARCH.md §5 (the region-1 .bim fixture table + task-shaped RED tests),
    m3-07-VALIDATION.md (Wave 0 Requirements checklist).
  </read_first>
  <files>tests/m3/test_occlusion_span_filter.py, tests/m3/test_occlusion_manifest.py, tests/m3/test_occlusion_present_rate_scan.py, tests/m3/test_occlusion_lockstep_drop.py, tests/m3/test_run_native_ld_panel.py</files>
  <action>
    Author ALL the RED-first test scaffolds (they FAIL now because the impl modules do not exist — that IS the
    Wave 0 RED state). Mirror the tests/m3 conventions (PROJECT_ROOT via Path(__file__).resolve().parents[2];
    insert src/python on sys.path; env smoke_dev py3.11 numpy/pandas). Reuse the `_write_bim(path, rows)` helper
    shape (row = (chr, snp_id, cm, bp, A1, A2), A1=ALT/A2=REF; an indel sets A2 to a multi-char REF string).

    (1) tests/m3/test_occlusion_span_filter.py — a module-level `_REGION1_BIM_ROWS` fixture helper reproducing the
        verdict's coordinates (chr1; deletions get a multi-char A2/REF of the exact span length):
          bp=1980423 del1  A1=G A2=<60-char>  ; bp=1980475 snpA A1=A A2=A (occluded)
          bp=5733474 del2  A1=G A2=<29-char>  ; bp=5733487 snpB A1=A A2=A (occluded)
          bp=5922716 del3  A1=G A2=<7-char>   ; bp=5922718 snpC A1=A A2=A (occluded by del3)
          bp=5922724 del4  A1=G A2=<31-char>
          bp=7492679 del5  A1=G A2=<31-char>  ; bp=7492693 del6 A1=G A2=<17-char> (occluded by del5)
          bp=8375794 del7  A1=G A2=<29-char>  ; bp=8375822 snpD A1=A A2=A (occluded)
        (Use variant ids = f"1:{bp}:{A2}:{A1}" so col-2 is the production chr:pos:ref:alt form.) Assert
        `detect_occluded_variants(rows)` returns EXACTLY the 5 occluded ids {snpA,snpB,snpC,del6,snpD}; plus unit
        cases: no-deletion window -> []; single deletion covering a downstream SNP -> that SNP; a SNP UPSTREAM of a
        deletion -> NOT occluded (disjoint); off-by-one boundary (POS_V==POS_D+len(REF_D)−1 occluded; ==+len(REF_D)
        not); an SNV (len REF=1) never occludes; an INSERTION (len ALT>len REF) never occludes a downstream base;
        `edges` records occluder→occluded and marks the 5922718↔5922724 pair as disjoint/second-order.
    (2) tests/m3/test_occlusion_manifest.py — Stage-A record has all coordinate columns + correct ref_span_start/end
        (from the OCCLUDING deletion) + occluding_deletion_id + occluding_deletion_ref_len + reason; resume-safe
        dedup by (region_id, variant_id); aggregate rollup concatenates per-region records. A liftover test
        (skip if `data/external/liftover/hg38ToHg19.over.chain.gz` absent, per the conftest chain-skip pattern)
        asserts pos_grch37 for 5922716/5922718/5922724 == 5982776/5982778/5982784.
    (3) tests/m3/test_occlusion_present_rate_scan.py — on tiny synthetic TSV fixtures with the harmonized header
        (CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD), a variant present in k of n files ->
        present-rate k/n; a variant absent -> 0; CHR/POS auto-detected.
    (4) tests/m3/test_occlusion_lockstep_drop.py — `drop_occluded_from_sumstats` removes exactly the manifest's
        GRCh37 (CHR,POS) rows, logs each drop, leaves non-occluded rows byte-identical, is idempotent (2nd apply =
        no-op), and does NOT re-key.
    (5) EXTEND tests/m3/test_run_native_ld_panel.py — extend `_MockPlink` to honor an `--exclude <file>` argv (drop
        those col-2 ids from the window BEFORE sizing the `.ld.bin`/snplist, composing with the existing
        `--write-snplist`/`mono_snps` modeling). Add tests: (a) the driver writes `{out_prefix}.occluded.excludelist`
        containing exactly the occluded ids for a cohort seeded with the region-1 topology; (b) `--exclude` reaches
        the plink argv (`-k exclude`); (c) `--keep-allele-order` still present on every call; (d) the resulting
        `.npz` has NO NaN and passes content_verify_npz (`-k occlusion`); (e) `n_dropped_occluded` is recorded and
        `n_dropped_monomorphic` is correctly SEPARATED (an in-window mono variant + an occluded variant both present
        -> each counted in its own column).

    Commit RED (explicit paths — GPFS, NEVER `git add -A`/`.`), tag m3-07-W7-T-WAVE0. The suite must FAIL only on
    "module/attribute not found" / the not-yet-wired driver behavior — not on syntax/collection errors.
  </action>
  <acceptance_criteria>
    - The 4 new test files + the extended test_run_native_ld_panel.py exist and are COLLECTED by pytest.
    - `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_span_filter.py tests/m3/test_occlusion_manifest.py tests/m3/test_occlusion_present_rate_scan.py tests/m3/test_occlusion_lockstep_drop.py --collect-only -q` exits 0 (collection succeeds).
    - Running those suites FAILS RED (ModuleNotFoundError / missing impl), NOT collection errors.
  </acceptance_criteria>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_span_filter.py tests/m3/test_occlusion_manifest.py tests/m3/test_occlusion_present_rate_scan.py tests/m3/test_occlusion_lockstep_drop.py --collect-only -q</automated>
  </verify>
  <done>All 4 new test files + the extended driver tests collect cleanly and fail RED (impl absent); region-1 `.bim` fixture helper present. Committed RED with explicit paths.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3 (T1 — the core): occlusion_span_filter.py + build_plink_ld_command exclude= + process_region reorder + n_dropped_occluded</name>
  <read_first>
    src/python/occlusion_span_filter.py (to create), src/python/aou_ld_panel.py:2854-2913 (build_plink_ld_command),
    src/python/run_native_ld_panel.py:99-105,275-302,352-449,538-706 (_PANEL_COLUMNS, _window_bim_n_var,
    _needs_retained_subset/_retained_window_bim, process_region), src/python/plink_ld_to_npz.py:88-119,205-228
    (FROZEN — _read_bim_rows/load_bim contract + read_square_bin NaN-raise; read only), tests/m3/test_run_native_ld_panel.py (from Task 2).
  </read_first>
  <files>src/python/occlusion_span_filter.py, src/python/aou_ld_panel.py, src/python/run_native_ld_panel.py, tests/m3/test_occlusion_span_filter.py, tests/m3/test_run_native_ld_panel.py</files>
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
    GREEN the Task-2 RED tests. (1) Create src/python/occlusion_span_filter.py implementing detect_occluded_variants
    exactly per the rule in <interfaces>; stdlib only; import nothing from plink_ld_to_npz beyond `_read_bim_rows`
    if convenient (the driver may parse and pass rows). Keep it pure + CI-runnable. (2) EXTEND
    build_plink_ld_command (aou_ld_panel.py:2854) with `exclude: str | None = None`; when non-None append
    `["--exclude", str(exclude)]` immediately before the `--r` block (both square and banded branches; square is the
    fire path). Do NOT alter `--keep-allele-order` / `--mac` / `--write-snplist` ordering. (3) REORDER process_region
    (run_native_ld_panel.py square branch): move `bim_path = f"{bfile_prefix}.bim"` + the raw window read to BEFORE
    `build_plink_ld_command`, using plain `_window_bim_n_var(bim_path, chrom, from_bp, to_bp)` (the pre-plink read
    has no concurrent writer, so the retry wrapper is unneeded — RESEARCH §1 step 2); parse raw_window_bim rows and
    call detect_occluded_variants; write the exclude list + pass `exclude=exclude_path`; run plink; keep the existing
    post-plink bin_n_var + `_needs_retained_subset`/`_retained_window_bim(..., expect_nonzero=(bin_n_var>0))` block
    UNCHANGED (it now fires because exclusion drops variants); compute the split n_dropped_occluded /
    n_dropped_monomorphic; append the panel column; emit a LOUD stderr line per region when n_dropped_occluded>0.
    Leave the banded branch and content_verify_npz body UNTOUCHED. Do NOT modify plink_ld_to_npz.py or ld_npz_to_rds.R.
    Commit GREEN, explicit paths, tag m3-07-W7-T1.
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
  <name>Task 4 (T2): occlusion_manifest.py — the load-bearing provenance manifest (Stage-A coordinate-only + Stage-B liftover/traits) + aggregate catalog</name>
  <read_first>
    src/python/occlusion_manifest.py (to create), src/python/run_native_ld_panel.py:462-477 (_append_panel_row_local
    resume-safe pattern to mirror), src/scripts/ld_npz_to_rds.R:96,162-198 (liftover recipe + chain SHA-256 — reuse,
    do NOT modify), src/python/occlusion_span_filter.py (edges from T1), tests/m3/test_occlusion_manifest.py (from Task 2),
    .planning/amendments/m3_panel_occlusion_policy_decision.md (the schema is load-bearing, not optional logging).
  </read_first>
  <files>src/python/occlusion_manifest.py, src/python/run_native_ld_panel.py, tests/m3/test_occlusion_manifest.py</files>
  <behavior>
    - Stage A (in-perimeter-safe, coordinate/id-only — egress-clean): append_occlusion_rows writes one row per
      excluded variant to `{out_dir}/occlusion_manifest.tsv`, resume-safe (dedup by (region_id, variant_id) —
      mirror _append_panel_row_local). Columns: region_id, chr, variant_id, pos_grch38, ref, alt,
      ref_span_start_grch38, ref_span_end_grch38, occluding_deletion_id, occluding_deletion_ref_len, reason
      (constant "reference-occlusion → undefined-LD"), occlusion_order (direct|second_order). ref_span_* come from
      the OCCLUDING deletion (POS_D .. POS_D+len(REF_D)−1). NO genotypes, NO per-person counts.
    - Stage B (NC-State enrichment): pos_grch37 via the ld_npz_to_rds.R liftover recipe (pyliftover, chain
      hg38ToHg19.over.chain.gz, pos−1 in/+1 out) + chain SHA-256 recorded for provenance; traits_present +
      n_traits_present / n_traits_scanned come from the T3 present-rate scan. Liftover matches the hinge-check
      anchors (5922716/5922718/5922724 -> 5982776/5982778/5982784).
    - build_occlusion_catalog concatenates all per-region manifests into a genome-wide `occlusion_catalog.tsv`
      (the Angle-1/3 catalog seed). The second-order tangle is recorded honestly: one drop (5922718) resolving two
      NaN edges is a single manifest row with occlusion_order="second_order" noted (RESEARCH open-risk #6).
    - process_region calls append_occlusion_rows for the T1 occluded_ids/edges (Stage-A only, in the loop).
  </behavior>
  <action>
    GREEN the Task-2 manifest tests. Create src/python/occlusion_manifest.py: `append_occlusion_rows(out_dir,
    region_id, chr, edges, rows_by_id)` (Stage-A, resume-safe dedup — mirror _append_panel_row_local's
    exists/dedup/append logic with pandas), `enrich_occlusion_manifest(manifest_path, chain_path, present_rate=None)`
    (Stage-B: add pos_grch37 + chain_sha256 + traits_present; import pyliftover lazily so the Stage-A path needs no
    chain), and `build_occlusion_catalog(manifest_paths, out_path)` (concatenate to occlusion_catalog.tsv). Reuse the
    EXACT ld_npz_to_rds.R liftover convention (do NOT modify ld_npz_to_rds.R). Wire a Stage-A `append_occlusion_rows`
    call into process_region right where the T1 occluded_ids/edges are known (before the panel-row append), guarded
    so a manifest write never aborts the region (mirror the one-bad-region-never-aborts discipline). Commit GREEN,
    explicit paths, tag m3-07-W7-T2.
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
  <done>Per-region resume-safe Stage-A manifest (coordinate/id-only) + Stage-B liftover/traits enrichment + aggregate occlusion_catalog.tsv; liftover matches the hinge-check anchors; process_region emits manifest rows for the excluded set; frozen files byte-unchanged.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 5 (T3): occlusion_present_rate_scan.py — genome-wide present-rate-per-ancestry scan over the 9 public AFR sumstats</name>
  <read_first>
    src/python/occlusion_present_rate_scan.py (to create), .planning/amendments/m3_region1_occlusion_hinge_check.md:124-141
    (the zcat|awk scan prototype + auto-detect CHR/POS), src/python/occlusion_manifest.py (T2 — consumes the rate),
    tests/m3/test_occlusion_present_rate_scan.py (from Task 2).
  </read_first>
  <files>src/python/occlusion_present_rate_scan.py, tests/m3/test_occlusion_present_rate_scan.py</files>
  <behavior>
    - present_rate_for_variants(variants_grch37, sumstats_paths) -> per-variant {present_count, scanned_count,
      present_rate, files_present}. For each occluded variant (already lifted to GRCh37 (CHR,POS)), does a sumstats
      row exist at that (CHR,POS)? Auto-detect CHR/POS columns from the harmonized header (CHR POS REF ALT BETA SE P
      EAF N SNP_ID TRAIT ANCESTRY BUILD; fall back to cols 1/2). "per ancestry" generalizes the scan to each
      {trait}.{ANC} group (here all 9 AFR files). PUBLIC GRCh37 sumstats only, read-only (REQ-PUBLIC-DATA-ONLY);
      no perimeter, no spend. Reads .tsv.bgz via the same zcat|awk-equivalent (pandas chunked or subprocess zcat).
    - Synthetic-fixture unit: variant present in k of n files -> present_rate k/n; absent -> 0.
    - The REAL 9-file genome-wide scan is an integration/validation step (gated, out of scope for unit CI) — the
      function is unit-covered on synthetic fixtures now.
  </behavior>
  <action>
    GREEN the Task-2 present-rate tests. Create src/python/occlusion_present_rate_scan.py with
    present_rate_for_variants(...) as above, reusing the hinge-check auto-detect-CHR/POS scan logic. Keep it a pure,
    deterministic function over file paths so it is CI-runnable on tiny synthetic TSV fixtures (plain TSV or .bgz).
    Output a per-variant present-rate table (the metric that sizes the Angle-1/3 scientific cost). Commit GREEN,
    explicit paths, tag m3-07-W7-T3.
  </action>
  <acceptance_criteria>
    - `pytest tests/m3/test_occlusion_present_rate_scan.py -x` exits 0 (k/n present-rate on synthetic fixtures; absent -> 0; CHR/POS auto-detected).
    - `grep -c "present_rate" src/python/occlusion_present_rate_scan.py` >= 1.
    - `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` is EMPTY.
  </acceptance_criteria>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_present_rate_scan.py -x -q</automated>
  </verify>
  <done>present_rate_for_variants reports PRESENT-vs-ABSENT k/n per occluded variant over public GRCh37 AFR sumstats (auto-detected CHR/POS); unit-covered on synthetic fixtures; frozen files byte-unchanged.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 6 (T4): drop_occluded_from_sumstats.py — reusable lockstep (CHR,POS) drop-only filter (m3-04 wiring DEFERRED)</name>
  <read_first>
    src/python/drop_occluded_from_sumstats.py (to create), src/R/regularization/snp_id_bridge.R:107-121 ((CHR,POS)
    membership, first-wins collision), src/snakemake/rules/finemap.smk:89-93 (m3-04-W4 STALE/SUPERSEDED-PENDING-REPLAN
    — the wiring seam is DEFERRED), src/python/occlusion_manifest.py (the manifest this consumes),
    tests/m3/test_occlusion_lockstep_drop.py (from Task 2), .planning/amendments/m3_region1_occlusion_hinge_check.md
    (rs182965575 present 7/9 — the orphan this prevents).
  </read_first>
  <files>src/python/drop_occluded_from_sumstats.py, tests/m3/test_occlusion_lockstep_drop.py</files>
  <behavior>
    - drop_occluded_from_sumstats(sumstats_df, manifest, build="GRCh37") -> (filtered_df, drop_log). Removes EXACTLY
      the rows whose (CHR,POS) matches a manifest entry's GRCh37 (chr, pos_grch37). Drop-only — NO re-key, NO allele
      re-orientation (snp_id_bridge.R (CHR,POS) semantics; first-wins on multi-allelic collision). drop_log records
      each dropped (chr,pos,variant_id,reason). Non-occluded rows are byte-identical (same order, same values).
      IDEMPOTENT: a second application is a no-op (drop_log empty). Prevents orphaning a sumstats-present occluded
      variant (rs182965575 present 7/9 AFR) — the reason panel-only-exclude is unsafe.
    - This is the REUSABLE filter (RESEARCH open-decision #3, RESOLVED). The EXACT m3-04 consume wiring
      (run_susie_rss.R sumstats-load vs a pre-fit harmonization filter vs a Snakemake rule) is DEFERRED to the m3-04
      replan — documented as an explicit seam in the module docstring, NOT wired here (finemap.smk:89-93 is STALE).
  </behavior>
  <action>
    GREEN the Task-2 lockstep tests. Create src/python/drop_occluded_from_sumstats.py implementing the (CHR,POS)
    drop-only filter above (pandas; deterministic; idempotent). Docstring MUST state the DEFERRED wiring seam
    explicitly: "the m3-04 consume rule is SUPERSEDED-PENDING-REPLAN (finemap.smk:89-93); this reusable filter is
    wired at the sumstats-load seam when the m3-04 consume replan lands — keyed on the same manifest (CHR,POS) as the
    panel exclusion so panel and sumstats stay in lockstep (no orphaned variant)." Do NOT modify finemap.smk or any
    consume rule in this plan (that is the m3-04 replan's job). Commit GREEN, explicit paths, tag m3-07-W7-T4.
  </action>
  <acceptance_criteria>
    - `pytest tests/m3/test_occlusion_lockstep_drop.py -x` exits 0 (drop = exactly manifest (CHR,POS); non-occluded rows byte-identical; idempotent; no re-key).
    - `grep -c "SUPERSEDED-PENDING-REPLAN\|m3-04" src/python/drop_occluded_from_sumstats.py` >= 1 (deferred seam documented).
    - `git diff --stat src/snakemake/rules/finemap.smk src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` is EMPTY (no consume wiring, no frozen-contract change).
  </acceptance_criteria>
  <verify>
    <automated>/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_lockstep_drop.py -x -q</automated>
  </verify>
  <done>Reusable manifest-driven (CHR,POS) drop-only filter GREEN (idempotent, no re-key, no orphan); the m3-04 consume wiring is a documented deferred seam (finemap.smk untouched); frozen files byte-unchanged.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| window `.bim` (untrusted indel geometry) → occlusion filter | A malformed / adversarial `.bim` row (bad bp, short row, unexpected allele string) crosses into detect_occluded_variants; a wrong footprint could over- or under-exclude and silently corrupt the panel. |
| occlusion manifest → egress boundary | Only aggregate coordinate/id metadata (Stage-A manifest) is designed to leave the AoU perimeter; individual-level `.bed/.bim/.fam` never egress (export_cohort_to_plink boundary). |
| panel ↔ sumstats join ((CHR,POS)) | Excluding a panel record without a lockstep sumstats drop orphans a sumstats-present variant (rs182965575 present 7/9 AFR) — a desync boundary. |
| occluded pair → plink `--r` → read_square_bin | An occluded `0/0 → NaN` reaching the frozen reader would trip the NaN-raise; the filter must remove the record BEFORE `--r`. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-m3-07-01 | Tampering | occlusion_span_filter (silent over-exclusion corrupts the panel) | mitigate | Deterministic conservative rule + manifest audits EVERY drop (T2) + `n_dropped_occluded` accounting; unit tests pin the EXACT excluded set {1980475,5733487,5922718,7492693,8375822} on the region-1 fixture; chains flagged in the catalog (occlusion_order). |
| T-m3-07-02 | Information disclosure | occlusion manifest / present-rate scan | mitigate | Stage-A manifest is coordinate/id-only (no genotypes, no per-person counts) — egress-clean by construction; Stage-B enrichment + present-rate run NC-State on already-PUBLIC GRCh37 sumstats (REQ-AOU-LD-EGRESS, REQ-PUBLIC-DATA-ONLY). |
| T-m3-07-03 | Tampering / integrity | panel↔sumstats desync (orphaned variant) | mitigate | Lockstep drop (T4) keyed on the SAME manifest (CHR,POS); drop-only, no re-key; idempotent; prevents orphaning rs182965575. |
| T-m3-07-04 | Tampering | occluded NaN reaches the fine-mapper | mitigate | Exclude BEFORE `--r` (T1) → the frozen read_square_bin NaN-raise never trips; the `.npz` is NaN-free by construction; frozen contracts git-diff-clean. |
| T-m3-07-05 | Tampering (input validation, ASVS V5) | malformed `.bim` row into the filter | mitigate | detect_occluded_variants validates ≥6 fields + integer bp and RAISES ValueError on a malformed row (loud, not silent) — mirrors _read_bim_rows / _retained_window_bim uniqueness guards. |
</threat_model>

<verification>
- Task 1 (OSF gate): the amendment-update doc exists, is POSTED to osf.io/az52u, and its file id/SHA-256/git tag are recorded BEFORE any code task begins. Tasks 2–6 are execution-blocked until then.
- Task 2 (Wave 0): the 4 new test files + extended driver tests collect cleanly and fail RED.
- Task 3 (T1): `pytest tests/m3/test_occlusion_span_filter.py tests/m3/test_run_native_ld_panel.py -x` all green; `--exclude` reaches argv before `--r`; `--keep-allele-order` on every call; `.npz` NaN-free; `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` empty.
- Task 4 (T2): `pytest tests/m3/test_occlusion_manifest.py -x` all green (Stage-A schema + liftover anchors + rollup); frozen files byte-unchanged.
- Task 5 (T3): `pytest tests/m3/test_occlusion_present_rate_scan.py -x` all green (k/n on synthetic sumstats).
- Task 6 (T4): `pytest tests/m3/test_occlusion_lockstep_drop.py -x` all green (exact (CHR,POS) drop, idempotent, no re-key); finemap.smk untouched.
- Full regression: `pytest tests/m3 -q` stays green (baseline ≈336 passed / 30 skipped + the new suites; no regressions in the frozen modules).
- Frozen-contract gate (phase): `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` EMPTY; run_native_ld_panel.py content_verify_npz body untouched.
- NO perimeter access, NO loop contact, NO re-fire. The genome-wide 276-region filter run against the REAL in-perimeter `.bim` (+ the region-1 re-run validation) is GATED / out-of-scope; its logic is unit-covered on the region-1 fixture now.
</verification>

<success_criteria>
- The OSF pre-registration HARD GATE is honored: exclusion + provenance (never zeroing) is posted + recorded before any fix code lands (REQ-OSF-PREREG).
- occlusion_span_filter clears the occlusion upstream of `--r`: the region-1 fixture yields exactly the 5 occluded ids (the tangle collapses to one drop), footprint = len(REF) only, and the excluded window `.npz` is NaN-free.
- `--exclude` threads through build_plink_ld_command before `--r` with `--keep-allele-order` preserved; process_region reads the window pre-plink, writes the exclude list, and splits n_dropped_occluded from n_dropped_monomorphic.
- The provenance manifest is load-bearing: per-variant Stage-A coordinate/id-only record + Stage-B both-build positions + traits-present + reason, resume-safe, rolled up into the genome-wide occlusion_catalog.tsv (Angle-1/3).
- The present-rate scan quantifies PRESENT-vs-ABSENT per occluded variant over public GRCh37 AFR sumstats.
- The reusable lockstep (CHR,POS) drop-only filter exists + is tested (idempotent, no re-key, no orphan); the m3-04 consume wiring is a documented deferred seam.
- Frozen contracts (read_square_bin NaN-raise, content_verify_npz, the raw `.npz` format, ld_npz_to_rds.R) are byte-unchanged; m3-06 `condition_ld_matrix.py` is NOT touched (NaN→0 stays dead).
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-07-W7-overlapping-deletion-span-filter-and-provenance-SUMMARY.md`.
Record: the OSF file id/SHA-256/git tag for the amendment-update; the region-1 fixture result
(5 occluded ids; the tangle collapse); the frozen-contract git-diff-clean confirmation; the
deferred m3-04 consume-wiring seam for the T4 lockstep filter; and the gated 276-region
real-`.bim` validation boundary (unit-covered on the region-1 fixture now, empirically
confirmed only at the gated region-1 re-run — RESEARCH assumptions A1/A3).
</output>
