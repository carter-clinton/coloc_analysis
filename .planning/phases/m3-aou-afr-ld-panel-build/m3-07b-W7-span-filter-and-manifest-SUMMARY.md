---
phase: m3-aou-afr-ld-panel-build
plan: 07b
subsystem: ld-panel
tags: [ld, occlusion, span-filter, provenance, manifest, aou, afr, tdd]
requires:
  - m3-07a (RED suite + region-1 fixture + OSF gate)
  - m3_region1_nan_geometry_verdict.md (mechanism, anchor 4543dcf4…)
  - m3_panel_occlusion_policy_decision.md (policy, anchor 42d70167…)
provides:
  - occlusion_span_filter.detect_occluded_variants (pure, coordinate-only)
  - occlusion_manifest Stage-A records + Stage-B liftover + aggregate catalog
  - build_plink_ld_command(exclude=) — --exclude before --r
  - process_region span-filter reorder + n_dropped_occluded split
affects:
  - m3-07c (present-rate scan populates the traits_present seam; lockstep drop)
tech-stack:
  added: [pyliftover (lazy, Stage-B only)]
  patterns: [RED-first TDD, resume-safe dedup append, coordinate-only egress boundary]
key-files:
  created:
    - src/python/occlusion_span_filter.py
    - src/python/occlusion_manifest.py
  modified:
    - src/python/aou_ld_panel.py
    - src/python/run_native_ld_panel.py
decisions:
  - "n_dropped_occluded INSERTED before n_dropped_monomorphic (not appended after) — the plan's prose conflicted with a passing test pinning _PANEL_COLUMNS[-1]"
  - "edges = 2-field NamedTuple (hashable, == plain 2-tuple); one attribution edge per occluded variant"
  - "Nested-deletion tie-break = NEAREST upstream covering deletion (deterministic)"
  - "occlusion_order = 'direct' for every coordinate-derived record; no second_order"
metrics:
  tasks: 2
  completed: 2026-07-15
---

# Phase m3 Plan 07b: Span Filter and Manifest Summary

Reference-occlusion span filter wired upstream of plink `--r` (exclude-before-LD, so
no NaN is ever produced) plus the load-bearing coordinate-only provenance manifest —
turning the 07a RED suite GREEN without touching a single frozen contract.

## What was built

**T1 — `src/python/occlusion_span_filter.py` (new, pure stdlib).**
`detect_occluded_variants(rows) -> (occluded_ids, edges)` implements the settled
conservative rule `POS_D < POS_V <= POS_D + len(REF_D) − 1` over the ORIGINAL window,
with the footprint defined by `len(REF)` only. On the region-1 fixture it returns
EXACTLY the 5 settled ids `{1980475, 5733487, 5922718, 7492693, 8375822}`; the
5922716/5922718/5922724 tangle collapses to the single 5922718 drop, attributed to the
UPSTREAM `DEL 5922716`. Malformed rows RAISE `ValueError` (T-m3-07b-04). Also exports
`load_bim_rows` (required by the gated real-`.bim` test) and `parse_bim_row`.

**T1 — `build_plink_ld_command(exclude=None)`** (`aou_ld_panel.py`): appends
`--exclude <path>` after the window flags and BEFORE the `--r` block in both branches;
`--keep-allele-order` preserved on every command. `exclude=None` yields a
BYTE-IDENTICAL argv to the pre-07b command (verified).

**T1 — `process_region` reorder** (`run_native_ld_panel.py`): the raw window `.bim` is
now read BEFORE `build_plink_ld_command` via the PLAIN `_window_bim_n_var` (no retry —
there is no concurrent writer pre-plink); the filter runs; `{out_prefix}.occluded.excludelist`
is written and passed as `exclude=`; the existing `_needs_retained_subset` /
`_retained_window_bim` snplist machinery fires automatically and is UNCHANGED.

**T2 — `src/python/occlusion_manifest.py` (new).** Stage-A `build_region_records` /
`append_region_manifest` (resume-safe dedup on `(region_id, variant_id)`),
`aggregate_manifests` → genome-wide `occlusion_catalog.tsv`, Stage-B
`add_grch37_positions` (pyliftover, lazy import) + `chain_sha256` +
`enrich_occlusion_manifest`. Driver hook `append_occlusion_rows` is called from
`process_region`, guarded so a manifest write can never abort a region.

## Region-1 fixture result (the headline)

5 occluded ids, the tangle collapsing to one drop, each attributed to a real upstream
covering deletion:

| occluded | occluder | ref span (GRCh38) | order |
|---|---|---|---|
| 1980475 | 1980423 (60 bp) | 1980423–1980482 | direct |
| 5733487 | 5733474 (29 bp) | 5733474–5733502 | direct |
| **5922718** | **5922716 (7 bp)** — UPSTREAM, not 5922724 | 5922716–5922722 | direct |
| 7492693 (itself a deletion) | 7492679 (31 bp) | 7492679–7492709 | direct |
| 8375822 (boundary = last covered base) | 8375794 (29 bp) | 8375794–8375822 | direct |

The excluded window `.npz` is NaN-free, shape (6,6) = 11 raw − 5 occluded, and passes
`content_verify_npz`. The frozen `read_square_bin` NaN-raise never trips because the
cause is removed upstream — nothing is zeroed. NaN→0 stays DEAD.

## Frozen-contract gate — CONFIRMED EMPTY

```
git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R
(empty)
git diff --stat src/python/condition_ld_matrix.py
(empty — m3-06 FROZEN/HELD, untouched)
```
`content_verify_npz` body untouched; the banded branch untouched.

## Stage-A egress-clean schema

`region_id, chr, variant_id, pos_grch38, ref, alt, ref_span_start_grch38,
ref_span_end_grch38, occluding_deletion_id, occluding_deletion_ref_len, reason,
occlusion_order` — coordinate/id geometry only, all derivable from a `.bim`. No
genotypes, no per-person/per-sample counts (REQ-AOU-LD-EGRESS). The 07a RED enforces
this with a substring/token scan over every emitted key.

Stage-B adds `pos_grch37` (+ `chain_sha256`), matching the settled hinge-check anchors
5922716/5922718/5922724 → 5982776/5982778/5982784 against the ONLY in-repo chain
(`data/external/liftover/hg38ToHg19.over.chain.gz`), reusing the exact
`ld_npz_to_rds.R:167-183` recipe (pos−1 in / +1 out). A failed lift records an explicit
NA — never a guessed or passed-through coordinate.

**`traits_present` 07c seam:** `STAGE_B_TRAIT_COLUMNS = [traits_present,
n_traits_present, n_traits_scanned]` are DECLARED here and left empty; the 07c
present-rate scan populates them via `enrich_occlusion_manifest(present_rate=…)`. They
are declared even when empty so a consumer can distinguish "not yet scanned" from
"scanned, absent".

## Deviations from Plan

### 1. [BLOCKER — reported, NOT resolved] `n_dropped_occluded` in `_PANEL_COLUMNS`: two tests contradict each other

The plan's acceptance criterion says `n_dropped_occluded` must be "APPENDED after
n_dropped_monomorphic in `_PANEL_COLUMNS`". Two pre-existing, currently-PASSING driver
tests make the full plan-prose impossible:

- `test_panel_columns_include_n_dropped_monomorphic:1281` pins
  `_PANEL_COLUMNS[-1] == "n_dropped_monomorphic"` → forbids appending AFTER it.
  **Resolved in code:** inserted `n_dropped_occluded` at index 7 (leading 7 columns keep
  their exact positions; monomorphic stays last). Both tests pass. Deviation from plan
  prose only; the intent (append-only, never reorder the leading columns) is preserved.
- `test_panel_tsv_append_resume_safe:392` pins the panel TSV's columns to an EXACT
  8-item list that does not contain `n_dropped_occluded`. Because
  `_append_panel_row_local` writes `columns=_PANEL_COLUMNS`, this DIRECTLY contradicts
  the 07a RED `test_panel_columns_include_n_dropped_occluded:1589`
  (`"n_dropped_occluded" in drv._PANEL_COLUMNS`). **No implementation satisfies both.**

Per the executor's standing instruction ("if you believe a test is genuinely wrong,
STOP and report it rather than editing it"), the test was NOT edited. This is an
OMISSION in the 07a RED scaffold, not a deliberate expectation — the precedent is
explicit: commit `1a9d170` (Carter, quick-260701-qcy), which added the previous panel
column `n_dropped_monomorphic` RED-first, states in its own message *"updated the
panel-TSV column-list assertion for the appended column"* and made exactly that
companion edit in the same RED commit. 07a added
`test_panel_columns_include_n_dropped_occluded` but did not make the companion update.

**Proposed 1-line companion edit (awaiting approval, NOT applied)** —
`tests/m3/test_run_native_ld_panel.py:392-395`:

```python
    assert list(df.columns) == [
        "region_id", "chr", "n_var", "wall_min", "peak_ram_gib", "output_gib", "status",
        "n_dropped_occluded",     # m3-07b: occlusion drop-count provenance
        "n_dropped_monomorphic",  # 260701-qcy hardening H2: drop-count provenance
    ]
```

Dropping `n_dropped_occluded` from `_PANEL_COLUMNS` instead would fail the 07a RED and
would silently discard the per-region occlusion drop count from the panel TSV — i.e.
the exact provenance the OSF amendment-update (osf.io/az52u) pre-registers. That is not
an acceptable resolution.

### 2. [Rule 1 - Bug, self-inflicted] Source-scan guards caught my own comment

`test_no_nan_to_zero_conditioning_in_the_driver` and
`test_driver_does_not_touch_retired_hail_path` substring-scan the driver source for
retired markers. A comment I wrote asserting the retired m3-06 module is never imported
literally contained the forbidden symbol name. The guards are RIGHT (they cannot
distinguish comment from code, and should not have to). Comment reworded to name no
retired symbol. No production behavior involved.

### 3. Manifest API names: tests pin different names than the plan's prose

The plan's frontmatter declares exports `append_occlusion_rows` /
`enrich_occlusion_manifest` / `build_occlusion_catalog`; the 07a RED pins
`build_region_records` / `append_region_manifest` / `aggregate_manifests` /
`add_grch37_positions` / `REASON_REFERENCE_OCCLUSION`. Tests are the contract, so the
test-pinned names are PRIMARY. The plan's names are also provided and are real:
`append_occlusion_rows` is the driver-facing Stage-A hook (satisfying the plan's
`grep append_occlusion_rows run_native_ld_panel.py` criterion),
`enrich_occlusion_manifest` is the file-level Stage-B wrapper, and
`build_occlusion_catalog` is an alias of `aggregate_manifests`. No test was edited.

### 4. [Rule 2 - Missing critical functionality] Excludelist durability

The 07a RED requires `{out_prefix}.occluded.excludelist` to exist AFTER the run and
calls it "durable provenance, not a scratch temp", but `_reclaim_region_scratch`'s
`{region_id}.*` glob would have deleted it. Added it to the keep-set alongside the
`.npz` in local mode, and in `gs://` mode it is uploaded next to the verified `.npz`
before reclaim (coordinate/id-only, egress-clean). Without this the pre-registered
audit trail would be destroyed on every region in the real bucket-first fire.

### 5. Nested-deletion attribution tie-break (undetermined by the RED)

`test_doubly_occluded_variant_appears_exactly_once` requires a deterministic single
attribution to *some* real covering deletion but does not pin which. Chose the NEAREST
upstream covering deletion (greatest `POS_D`; ties by longest footprint, then by id) —
the most proximal reference-span explanation, and independent of input row order.
Documented in `_attribute_occluder`.

## Contract details verified against the reconciled plan

- `edges` are HASHABLE 2-tuples — a 2-field `NamedTuple` (`OcclusionEdge`) that compares
  equal to a plain 2-tuple. `set(edges)` and `for (o, v) in edge_set` both work. No
  `geometry` field, no third field.
- NO disjoint/second-order edge: del4 (5922724) contributes no edge; `edge_set` is
  EXACTLY the 5 direct edges. The 5922718↔5922724 NaN pair is genotype-layer and is not
  synthesized; it resolves as a consequence of the single 5922718 drop.
- `occlusion_order` is `"direct"` for every record; no `"second_order"` value exists.
- Left bound is STRICT (`POS_D < POS_V`) — a distinct co-located variant is not occluded.
- No variant position is hardcoded anywhere in either new module (verified by grep).

## Gated / out-of-scope boundary

The real 276-region `.bim` validation remains GATED (no AoU perimeter access this
phase). `test_region1_real_window_known_answer_gated` SKIPS cleanly and stands as the
concrete expected answer for the gated run: occluded row indices
`{10328, 44784, 46714, 59097, 66730}` (0-based; the origin still needs confirming
against the real `.bim` header), 7-deletion inventory 60/29/7/31/31/17/29 bp, 0
same-position. Unit coverage is on the region-1 synthetic fixture, which mirrors that
topology (RESEARCH assumptions A1/A2). No perimeter access, no loop contact, no re-fire.
07c NOT started (Carter: "07b then PAUSE").
