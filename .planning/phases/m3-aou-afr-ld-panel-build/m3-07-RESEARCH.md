# Phase m3-07-W7: Overlapping-deletion span-filter + provenance manifest + present-rate scan — Research

**Researched:** 2026-07-10
**Domain:** AoU AFR native-plink LD panel build (Python driver + plink1.9), GRCh38↔GRCh37 liftover, harmonized-sumstats join
**Confidence:** HIGH (code-path map + #1 crux resolved from source; science CITED from byte-verified amendments)

> This is a CODE-mapping research doc. The SCIENCE (mechanism + policy) is settled and LOCKED in the
> byte-verified amendment doc-set — it is not re-litigated here. Every finding below is `[VERIFIED: <file>:<line>]`
> against the working tree at branch `m3-W2-aou-deltas`, or `[CITED: <amendment>]` for the settled science.

<user_constraints>
## User Constraints (from m3-07-CONTEXT.md)

### Locked Decisions (do NOT re-litigate — byte-verified amendment doc-set)
- **Mechanism:** Region-1 NaN = overlapping-deletion occlusion — a deletion's REF span physically covers a
  neighbor variant's POS → the base is uncallable on the deletion haplotype → `r` is **structurally
  undefined** (no "true r"). 6/6 pairs resolved: 5 direct `ref_span_overlap` + 1 second-order. 0 same-position,
  0 chance-degeneracy. SYSTEMIC (region 1 alone = 7 distinct deletions) → fix belongs UPSTREAM at panel-build.
- **Policy:** **Exclude-in-lockstep across panel AND sumstats, with an auditable provenance manifest.**
  NaN→0 is DEAD (m3-06 `condition_ld_matrix.py` stays FROZEN/HELD, never fed to a fit). Panel-only-exclude is
  UNSAFE (orphans a sumstats-present variant — rs182965575 is PRESENT in 7/9 AFR sumstats). The provenance
  manifest is a HARD requirement, not optional logging.
- **Provenance manifest schema (per excluded variant):** Variant ID + BOTH-build positions (GRCh38 panel +
  GRCh37 sumstats) + occluding deletion ID + its REF span (start–end) + locus/region id + traits-present +
  `reason = reference-occlusion → undefined-LD`. Aggregate rollup = genome-wide occlusion catalog (Angle-1/3).
- **Join key:** panel↔sumstats membership is decided by **(CHR, POS)** (`snp_id_bridge.R`), with `SNP_ID =
  chr:pos:ref:alt` as the join column after the chr:pos↔rsid bridge. Excluding a panel record MUST be mirrored
  by a lockstep sumstats-side drop or the join orphans the variant. Exclude-occluded drops variants, no re-key.

### Claude's Discretion (research options, recommend)
- Module boundaries for the new span-filter / manifest / scan code (reuse vs new machinery).
- The exact deterministic occlusion rule and its edge-case handling (chains, insertions) — recommend within the
  locked policy.
- Test fixture shapes reproducing the region-1 `ref_span_overlap` topology.

### Hard Gates / Constraints
- **⚠ OSF PRE-REGISTRATION GATE (BLOCKS all fix code):** the scoped OSF amendment-update (panel
  overlapping-variant policy = exclusion + provenance, never zeroing) MUST be posted + recorded BEFORE any fix
  code lands. Planning may proceed now; **execution is gated on the amendment-update being posted.** The plan
  MUST encode this as its FIRST hard gate (mirrors the `tcujq` / 999.1 OSF-gate precedent).
- **No perimeter access / no loop re-fire** from planning or code landing. The fix is NC-State-side panel-build
  code, tested on synthetic + region-1's characterized topology. The AoU loop stays untouched.
- **Frozen contracts stay frozen:** `read_square_bin`/`content_verify_npz` NaN-raise, the raw `.npz` format,
  `ld_npz_to_rds.R`. The fix removes occluded rows UPSTREAM (before `--r`) so no NaN reaches the reader.
- **TDD RED-first**; reuse existing utilities (window `.bim` reads, the `_retained_window_bim` snplist-threading
  pattern, block-wise memory discipline) rather than new machinery where possible.
- Rigor over speed; original-research framing.

### Deferred Ideas (OUT OF SCOPE)
- Re-firing the AoU loop (do NOT re-fire until this lands).
- NaN→0 / PSD conditioning of any kind (dead).
- Touching `read_square_bin` / `content_verify_npz` NaN-raise (they correctly surfaced this and STAY).
</user_constraints>

<phase_requirements>
## Phase Requirements (REQ-ID mapping)

| ID | Description (from REQUIREMENTS.md) | Research support |
|----|-------------------------------------|------------------|
| **REQ-AOU-LD-VALIDATION** [B] | Four-check validation before AoU LD enters production DAGs; validation memo committed before scale-up (`AOU-LD-PIPELINE.md` §9). | T1 correctness (no NaN reaches `read_square_bin`) and the 276-region filter are the gating precondition for re-validating region 1. See `## Validation Architecture`. |
| **REQ-AOU-LD-EGRESS** [B] | Only summary-level artifacts leave the Workbench; no individual-level data egresses; per-region `.npz`+AF land under `data/processed/ld_reference/AFR_aou/` (`AOU-LD-PIPELINE.md` §§7,13). | T1's exclude-list + T2's in-perimeter manifest-stub carry ONLY variant coordinates/IDs (aggregate metadata) — egress-clean by construction. The individual-level `.bed/.bim/.fam` stay in-perimeter (`export_cohort_to_plink` boundary, aou_ld_panel.py:2924-2926). |
| **REQ-OSF-PREREG** [AB] | Pre-registration on OSF; deviations disclosed. | The phase's FIRST hard gate: post the scoped amendment-update (exclusion + provenance, never zeroing) before any fix code lands. |
| **REQ-PUBLIC-DATA-ONLY** [AB] | 100% public / controlled-tier-under-DUA data; no proprietary. | The filter + manifest + scan operate only on AoU controlled-tier (under DUA) + public harmonized GWAS sumstats. No new data source. |
| **REQ-SNAKEMAKE-CI** [AB] | Pipeline steps reproducible / test-covered. | New code lands with RED-first pytest suites in `tests/m3/` (existing convention); the span-filter is a pure, deterministic, CI-runnable function. |
</phase_requirements>

## Summary

The phase adds an **upstream, panel-build-stage overlapping-deletion span-filter** (T1) that, for each of the
276 AFR regions, detects variants whose position is physically covered by a neighbouring deletion's REF span and
**excludes them from the LD window before plink `--r`** — so plink never computes the structurally-undefined
`0/0 → NaN` pair, and the frozen `read_square_bin` NaN-raise never trips. It emits a **load-bearing provenance
manifest** (T2), runs a **genome-wide present-rate-per-ancestry scan** (T3), and wires a **lockstep sumstats-side
drop** (T4) so panel and sumstats stay aligned on the `(CHR,POS)` / `chr:pos:ref:alt` join.

**The #1 crux is fully resolved and requires no new data plumbing.** A plink `.bim` in this pipeline **does**
carry full multi-character indel allele strings: `load_bim` (plink_ld_to_npz.py:105-119) documents and relies on
the `hl.export_plink` convention `A1 = ALT = alleles[1]`, `A2 = REF = alleles[0]`, reconstructing the canonical
vid `chr:pos:A2:A1 = chr:pos:REF:ALT`. So a deletion's REF span is `[POS, POS + len(A2) − 1]`, computable
directly from the cohort/window `.bim` columns `4` (bp) and `6` (A2=REF) — **no pvar/VCF needed**. The geometry
verdict independently re-derived every REF span from `len(REF)` (60/29/7/31/31/17/29 bp), confirming the `.bim`
retains full deletion spans (Hail `split_multi`/minrep does not collapse them). The exclusion is delivered via a
plink `--exclude <ids>` list (matched on `.bim` col-2 variant id) inserted before the existing `--r` call, and it
composes cleanly with the already-built `--mac 1 --write-snplist` + `_retained_window_bim` snplist-alignment
machinery.

**Primary recommendation:** Add one pure module `src/python/occlusion_span_filter.py`
(`detect_occluded_variants(window_bim_rows) -> (occluded_ids, occlusion_edges)`), thread an `--exclude` list into
`build_plink_ld_command` + `process_region` **before** `_run_plink`, emit a per-region occlusion manifest (stub
in-perimeter, enriched NC-State), and add a manifest-driven sumstats filter for the consume step. Reuse
`_window_bim_n_var`, `_retained_window_bim`, `_append_panel_row_local`, and the `ld_npz_to_rds.R` liftover
convention. Do not touch any frozen contract.

---

## 1. Code-path map (T1–T4)

### The per-region processing seam (all four tasks hook here)

`process_region(row, ...)` in `src/python/run_native_ld_panel.py:538-706` is the single per-region unit. The
loop `run_native_ld_panel` (L778-829) filters the manifest to AFR (`_filter_ancestry`, L729-732), static-shards,
and calls `process_region` per region. Manifest columns (config/ld_regions.tsv) actually used:
`region_id`, `chr`, `window_start_grch38`, `window_end_grch38`, `ancestry` `[VERIFIED: run_native_ld_panel.py:561-564,731]`.

Current SQUARE control flow inside `process_region` `[VERIFIED: run_native_ld_panel.py:601-674]`:

| Step | Line | What happens | Data available |
|------|------|--------------|----------------|
| build cmd | 602-605 | `alp.build_plink_ld_command(...)` | bfile prefix, window bounds |
| **plink `--r` runs** | 606 | `_run_plink(cmd)` → writes `{out_prefix}.ld.bin`, `.snplist`, `.afreq` | — |
| bin n_var | 618-619 | `_n_var_from_ld_bin(.ld.bin)` = √(bytes/4) | retained count |
| raw window .bim | 622-624 | `_window_bim_n_var_retry_on_zero(bfile.bim, chrom, from_bp, to_bp)` | **all in-window rows incl. A1/A2** |
| retained subset | 634-641 | `_retained_window_bim(raw_window_bim, snplist)` iff `bin_n_var != raw_window_n_var` | snplist-aligned rows |
| n_var check | 642-647 | raise on mismatch | — |
| monomorphic accounting | 652-660 | `n_dropped = raw_window_n_var − window_n_var`; panel col `n_dropped_monomorphic` | drop count |
| npz | 668-674 | `pln.plink_ld_to_npz(mode, ld_path, window_bim, af, out_npz, ...)` → `read_square_bin` (NaN-raise) | — |
| verify | 676-680 | `content_verify_npz` | — |

### T1 — Overlapping-deletion span-filter (exclude before `--r`)

**Insertion point:** move the raw-window-`.bim` read to **before** the plink call, run the occlusion filter,
write the exclude list, and pass it to `build_plink_ld_command`.

Recommended reordered SQUARE flow in `process_region`:
1. `bim_path = f"{bfile_prefix}.bim"` (already at L611).
2. `raw_window_n_var, raw_window_bim = _window_bim_n_var(bim_path, chrom, from_bp, to_bp)` — **before plink**.
   (Reading pre-plink is *safer* than the current post-plink read: the m3-02e-T4 transient-short-read race was
   specifically the cohort `.bim` being read at the instant plink finishes writing the 42 GB `.ld.bin`
   `[VERIFIED: run_native_ld_panel.py:108-116,305-349]`; there is no concurrent writer before plink, so
   `expect_nonzero` retry logic is unneeded here.)
3. `occluded_ids, edges = osf.detect_occluded_variants(raw_window_rows)` (NEW module — §3).
4. If `occluded_ids`: write `{out_prefix}.occluded.excludelist` (one variant id / line = `.bim` col-2 values).
5. `cmd = alp.build_plink_ld_command(..., exclude=exclude_path)` (NEW optional arg — §3).
6. `_run_plink(cmd)` → `.ld.bin` and `--write-snplist` now reflect `window − occluded − MAC0`.
7. Existing `_retained_window_bim` path (L634-641) **already** aligns `n_var`/`.bim`/`.npz` to the snplist,
   because `bin_n_var != raw_window_n_var` will now be true whenever anything was excluded
   `[VERIFIED: run_native_ld_panel.py:352-362,365-449]`. **No change needed to the alignment machinery.**
8. Split the drop accounting: add panel column `n_dropped_occluded` (APPEND per the L99-105 convention — never
   reorder leading columns) and recompute `n_dropped_monomorphic = (raw_window_n_var − len(occluded_ids)) −
   window_n_var`.
9. Emit T2 manifest rows for `occluded_ids` (§4).

`build_plink_ld_command` `[VERIFIED: aou_ld_panel.py:2854-2913]` currently builds `plink1.9 --bfile
--keep-allele-order --chr --from-bp --to-bp --mac 1 --nonfounders --write-snplist --r square bin4 --out`. Add an
`exclude: str | None = None` param that appends `--exclude <path>` (only when non-None). plink applies `--exclude`
alongside the position window and `--mac` before `--r`, so occluded variants are dropped before any LD is
computed. A test must assert `--keep-allele-order` still appears on every issued command
`[VERIFIED: test_run_native_ld_panel.py:366-388]`.

**Why "before `--r`" is mandatory (not a post-filter):** the occluded pair produces isolated off-diagonal NaN in
the `.ld.bin`; `read_square_bin` RAISES on any NaN `[VERIFIED: plink_ld_to_npz.py:213-228]`. Removing one member
of each occluded pair before plink runs means the NaN is never produced.

### T2 — Provenance manifest

**Emission point:** inside `process_region`, immediately after the span-filter identifies `occluded_ids/edges`
(before/around the panel-row append at L699). Mirror the resume-safe append pattern of
`_append_panel_row_local` `[VERIFIED: run_native_ld_panel.py:462-477]` for a per-region occlusion TSV/JSONL, plus
an aggregate rollup. **Two-stage** (egress boundary):
- **Stage A (in-perimeter, T1-time):** minimal record with GRCh38 coordinates only — egress-clean aggregate
  metadata (variant id, chr, pos_grch38, ref/alt, ref_span, occluding-deletion id + span, region_id, reason).
- **Stage B (NC-State, T2/T3):** enrich with GRCh37 position (liftover), traits-present, present-rate.

Full schema + columns in §4.

### T3 — Genome-wide present-rate-per-ancestry scan

**Data:** the 9 AFR harmonized sumstats live at `data/processed/sumstats_harmonized/*.AFR*.tsv.bgz`
`[VERIFIED: ls]`; header is `CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD` (GRCh37)
`[VERIFIED: zcat asthma.AFR.tsv.bgz | head -1]`. Present-rate = for each genome-wide occluded variant (lifted to
GRCh37), does a sumstats row exist at that `(CHR, POS)`? The exact scan is already prototyped in the hinge check
reproduce block (`zcat | awk`, auto-detect CHR/POS cols) `[CITED: m3_region1_occlusion_hinge_check.md:124-141]`.
This is NC-State, read-only. It runs over ALL AFR sumstats files; "per ancestry" generalizes the same scan to
each `{trait}.{ANC}` group. Output: catalog of present-vs-absent counts (sizes the Angle-1/3 scientific cost).

### T4 — Lockstep sumstats-side drop

**Where the panel meets sumstats:** the fine-mapping consume step `run_susie_rss.R::load_ld_matrix` reads
`obj$R + obj$variants` and joins to `{trait}.{ancestry}.tsv.bgz` via the LD-side `SNP_ID`
`[VERIFIED: ld_npz_to_rds.R:49-56,223-234; finemap.smk:99-141]`; membership is decided on `(CHR,POS)` through
`snp_id_bridge.R` `[VERIFIED: snp_id_bridge.R:107-121]`. The `refit_sh2b3_psd_regularized.R` path is the Track-A
EUR analogue of the same join `[VERIFIED: refit_sh2b3_psd_regularized.R:100-140]`.

**Insertion point (with caveat):** the m3-04 production consume rule is **STALE / SUPERSEDED-PENDING-REPLAN** —
`finemap.smk:89-93` states `m3-04-W4-production-and-egress-PLAN.md` must be re-planned to consume m3-02e's
AFR-native `.npz`. So the exact wiring seam is a genuine open decision (§7). **Recommendation:** build a reusable,
manifest-driven filter (Python or R) `drop_occluded_from_sumstats(sumstats_df, manifest, build="GRCh37") ->
(filtered_df, drop_log)` keyed on the manifest's GRCh37 `(CHR,POS)`, and wire it at the sumstats-load seam of
whatever the m3-04 consume step becomes (natural home: `run_susie_rss.R` sumstats load, or a pre-fit
harmonization filter). Because T1 already removes the variant from the panel, the sumstats-side drop's job is to
make the removal **explicit and auditable** (not rely on `intersect()` silently dropping it) and to prevent a
downstream step from testing a variant with no LD row. Drop variants only — no re-key (join-safest per policy).

---

## 2. Resolution of the #1 crux — REF-span availability (HIGH confidence)

**Question:** a `.bim` stores A1/A2 allele codes, not an explicit REF/ALT span. Where are the deletion spans
accessible so the filter can compute `POS..POS+len(REF)−1`?

**Answer — the `.bim` A1/A2 columns carry the full multi-character indel allele strings; no pvar/VCF needed.**

Evidence:
1. **`load_bim` contract** `[VERIFIED: plink_ld_to_npz.py:105-119]`:
   > `.bim` columns: `[chr, snp_id, cm, bp, A1, A2]`. Under `hl.export_plink`, **A1 = ALT = alleles[1]** and
   > **A2 = REF = alleles[0]**. The canonical project vid is `chr:pos:REF:ALT = {chr}:{bp}:{A2}:{A1}`.

   So for row `parts = line.split()`: `POS = int(parts[3])`, `REF = parts[5]` (A2), `ALT = parts[4]` (A1).
   `len(REF) = len(parts[5])`. A deletion has `len(REF) > len(ALT)`; its reference footprint is
   `[POS, POS + len(REF) − 1]`.
2. **`--keep-allele-order` preserves A1=ALT/A2=REF** — hardcoded on every LD call
   `[VERIFIED: aou_ld_panel.py:2860-2862,2892]`, so plink does not re-flip A1 to the minor allele and A2 stays
   REF.
3. **Independent re-derivation** — the geometry verdict recomputed every REF span "from the raw `bp`/`len(REF)`
   values" and obtained 60/29/7/31/31/17/29 bp `[CITED: m3_region1_nan_geometry_verdict.md:9-12,73-77]`. This
   only works if the `.bim` (or its source) retained full multi-char deletion alleles — confirming Hail
   `split_multi`/minrep does not collapse deletion spans (minimal representation of `GTTTT…`→`G` is already
   minimal and preserves length).
4. **The exclude list is content-agnostic to col-2.** plink `--exclude` matches on `.bim` col-2 (variant id).
   The filter identifies occluded rows by scanning the window `.bim` (it holds the whole row incl. col-2), so it
   writes those col-2 values regardless of whether col-2 is `chr:pos:ref:alt` (production `hl.export_plink`
   varids are `chr:pos:ref:alt` and unique `[VERIFIED: run_native_ld_panel.py:391-400]`) or an rsid.

**The deterministic occlusion rule (recommended):**
> Variant `V` is **occluded** iff there exists another window variant `D` with `len(REF_D) > 1` (a deletion) such
> that `POS_D < POS_V ≤ POS_D + len(REF_D) − 1` (i.e., `V`'s position falls strictly inside `D`'s reference
> footprint, downstream of `D`'s anchor). **Exclude every occluded `V`.**

Validation against the 6 pairs `[CITED: m3_region1_nan_geometry_verdict.md:15-22]`:
- Pair 1: DEL 1980423 (60bp) span `[1980423, 1980482]` ⊇ 1980475 ✓ → exclude 1980475.
- Pair 2: DEL 5733474 (29bp) span `[…, 5733502]` ⊇ 5733487 ✓ → exclude 5733487.
- Pair 3: DEL 5922716 (7bp) span `[…, 5922722]` ⊇ 5922718 ✓ → exclude 5922718.
- Pair 4 (`disjoint`): DEL 5922724 span `[5922724, 5922754]` does NOT contain 5922718 (upstream) — correctly not
  flagged by 5922724; 5922718 is already excluded by DEL 5922716. **Excluding 5922718 removes BOTH NaN edges**
  (5922716–5922718 and 5922718–5922724), collapsing the 3-record tangle with a single drop.
- Pair 5: DEL 7492679 (31bp) span `[…, 7492709]` ⊇ 7492693 ✓ (co-terminating) → exclude 7492693.
- Pair 6: DEL 8375794 (29bp) span `[…, 8375822]` ⊇ 8375822 ✓ → exclude 8375822.

Excluding the downstream (occluded) member removes every occlusion edge because the occluder always has the
smaller POS (a variant cannot sit inside a deletion whose anchor is downstream of it). Edge cases (chains,
insertions, MNVs) → §7.

---

## 3. Reuse inventory (build-on vs new)

### Reuse (existing utilities — do NOT re-implement)
| Utility | Location | Reused for |
|---------|----------|-----------|
| `_window_bim_n_var` | run_native_ld_panel.py:275-302 | Build the raw in-window `.bim` (verbatim rows incl. A1/A2) BEFORE plink → feeds the occlusion filter. |
| `_retained_window_bim` | run_native_ld_panel.py:365-449 | Aligns `n_var`/`.bim`/`.npz` to the post-exclude+post-MAC snplist — **already triggers** when the exclude drops variants (`_needs_retained_subset`, L352-362). |
| `_append_panel_row_local` | run_native_ld_panel.py:462-477 | Pattern for the resume-safe per-region manifest append (dedup by key). |
| `build_plink_ld_command` | aou_ld_panel.py:2854-2913 | Extend with an optional `--exclude` arg (SOLE plink-argv builder; keeps `--keep-allele-order` invariant). |
| `load_bim` | plink_ld_to_npz.py:105-119 | Canonical A2=REF / A1=ALT parsing + vid reconstruction (occlusion rule reads these columns). |
| `_load_af_sidecar` / `n_dropped_monomorphic` accounting | plink_ld_to_npz.py:68-81 / run_native_ld_panel.py:99-105,649-660 | Accounting pattern to mirror for `n_dropped_occluded` (APPEND panel column). |
| liftover convention | ld_npz_to_rds.py-equiv `ld_npz_to_rds.R:167-183` + hinge repro | GRCh38→GRCh37 for manifest b37 positions: pyliftover, chain `data/external/liftover/hg38ToHg19.over.chain.gz` (present, 1.2 MB `[VERIFIED: ls]`), `pos−1` in / `+1` out. |
| present-rate scan prototype | `m3_region1_occlusion_hinge_check.md:124-141` | `zcat | awk` scan of AFR sumstats at a lifted `(CHR,POS)` window (T3). |
| `snp_id_bridge.R` | snp_id_bridge.R:107-121 | The `(CHR,POS)` membership semantics the T4 drop must honor. |
| region-1 LD-topology fixture | test_condition_ld_matrix.py:58-65 | Reference for what "6 pairs / 11 rows" means (T2 manifest-count assertions); NOTE this is an LD matrix, not a `.bim` — T1 needs a coordinate `.bim` fixture (§5). |
| `_MockPlink` + `_write_bim`/`_setup_cohort` | test_run_native_ld_panel.py:48-163 | Test harness for the driver: synthetic `.ld.bin`/`.snplist` writer that already models `--mac`/`--write-snplist`; extend to model `--exclude`. |

### New modules needed
| New file | Purpose | Scope |
|----------|---------|-------|
| `src/python/occlusion_span_filter.py` | Pure `detect_occluded_variants(rows) -> (occluded_ids, edges)`; deterministic, no plink, no I/O. Reads POS (col 4) + REF=A2 (col 6) + id (col 2). | Python 3.11, stdlib only. CI-runnable. |
| `src/python/occlusion_manifest.py` | Per-region + aggregate manifest emitter (Stage A minimal in-perimeter; Stage B enrich). Optionally liftover + traits-present. | Python; pandas for the aggregate rollup. |
| `src/python/occlusion_present_rate_scan.py` (T3) | Genome-wide present-rate-per-ancestry scan over AFR sumstats. | Python; `zcat`/awk-equivalent or pandas chunked read. |
| sumstats lockstep filter (T4) | `drop_occluded_from_sumstats(...)` — manifest-driven, keyed on GRCh37 `(CHR,POS)`. Language TBD by consume-step seam (§7). | Python or R. |
| test suites | `tests/m3/test_occlusion_span_filter.py`, `test_occlusion_manifest.py`, `test_occlusion_present_rate_scan.py`, extend `test_run_native_ld_panel.py` + `test_build_plink_ld_command`-style for the `--exclude` arg. | pytest, RED-first. |

**Extend (surgical edits to existing files):** `build_plink_ld_command` (add `--exclude`), `process_region`
(reorder + wire filter + manifest + `n_dropped_occluded`), `_PANEL_COLUMNS` (append `n_dropped_occluded`).

**Do NOT touch (frozen):** `read_square_bin`, `content_verify_npz`, `plink_ld_to_npz` npz writer, `load_bim`
internals, `ld_npz_to_rds.R`, `condition_ld_matrix.py`/`write_conditioned_ld_npz.py` (m3-06, HELD/dead).

---

## 4. Provenance manifest — implementation notes

### Schema → concrete columns (per excluded variant)
| Column | Source | Stage |
|--------|--------|-------|
| `region_id` | manifest row | A (in-perimeter) |
| `chr` | window `.bim` col 1 (normalize `chr` prefix via `_chrom_match_key`) | A |
| `variant_id` | window `.bim` col 2 (`chr:pos:ref:alt` in production) | A |
| `pos_grch38` | window `.bim` col 4 | A |
| `ref` / `alt` | col 6 (A2) / col 5 (A1) | A |
| `ref_span_start_grch38` / `ref_span_end_grch38` | `POS` / `POS + len(REF) − 1` of the **occluding deletion** | A |
| `occluding_deletion_id` | occluder's col-2 id | A |
| `occluding_deletion_ref_len` | `len(REF_D)` | A |
| `pos_grch37` | pyliftover(`chr`, `pos_grch38`) via hg38ToHg19 chain | B (NC-State) |
| `traits_present` | list of `{trait}.AFR` files with a row at GRCh37 `(chr,pos)` | B |
| `n_traits_present` / `n_traits_scanned` | present-rate numerator/denominator | B |
| `reason` | constant `reference-occlusion → undefined-LD` | A |
| `occlusion_order` | `direct` vs `second_order` (tangle) | A (optional, from edges) |

### Format + emission
- **Per-region:** append-one-row-per-occluded-variant to `{out_dir}/occlusion_manifest.tsv` (or `.jsonl`),
  resume-safe (dedup by `(region_id, variant_id)`) — mirror `_append_panel_row_local`.
- **Aggregate rollup:** a genome-wide `occlusion_catalog.tsv` (all regions) = the Angle-1/3 catalog seed. Build
  by concatenating per-region records (pandas) at handback.
- **Egress:** Stage-A columns are pure variant-metadata / coordinate geometry — no genotypes, no per-person
  counts — matching the egress boundary honored by the geometry verdict itself
  `[CITED: m3_region1_nan_geometry_verdict.md:5-7]` and REQ-AOU-LD-EGRESS.

### Both-build position mapping
Reuse the exact `ld_npz_to_rds.R` liftover recipe `[VERIFIED: ld_npz_to_rds.R:167-183]`: pyliftover, chain
`data/external/liftover/hg38ToHg19.over.chain.gz`, `convert_coordinate("chr"+chr, pos38−1)` then `+1`. This is
the same convention the hinge check used to lift 5922716/5922718/5922724 → 5982776/5982778/5982784
`[CITED: m3_region1_occlusion_hinge_check.md:40-48,124-133]`. Runs NC-State in the `m3-r-ld` env (pyliftover
available there).

---

## 5. Test strategy (RED-first)

### Conventions (mirror existing tests/m3)
- `PROJECT_ROOT = Path(__file__).resolve().parents[2]`; insert `src/python` on `sys.path`
  `[VERIFIED: test_nan_guard.py:23-27; conftest.py:31-34]`.
- Env: `smoke_dev` py3.11, numpy/pandas only, no Hail — `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest`.
- `.bim` fixture writer `_write_bim(path, rows)` where a row is `(chr, snp_id, cm, bp, A1, A2)` and **A1=ALT,
  A2=REF** `[VERIFIED: test_run_native_ld_panel.py:48-61]`. For indels, set A2 (REF) to a multi-char string.
- Manifest writer uses columns `region_id, chr, ancestry, window_start_grch38, window_end_grch38`
  `[VERIFIED: test_run_native_ld_panel.py:71-75]`.
- Driver tests monkeypatch the single seam `drv._run_plink` with a `_MockPlink` that models
  `--mac`/`--write-snplist` `[VERIFIED: test_run_native_ld_panel.py:78-151]`.

### The region-1 `.bim` fixture (reproduces `ref_span_overlap`)
Build a synthetic chr1 window `.bim` at the verdict's real coordinates so the filter produces exactly the known
occluded set. Deletion rows get a multi-char REF (A2) of the exact span length:

| bp | id | A1 (ALT) | A2 (REF) len | role |
|----|----|----------|--------------|------|
| 1980423 | del1 | `G` | 60 | deletion |
| 1980475 | snpA | `A` | 1 | **occluded** |
| 5733474 | del2 | `G` | 29 | deletion |
| 5733487 | snpB | `A` | 1 | **occluded** |
| 5922716 | del3 | `G` | 7 | deletion |
| 5922718 | snpC | `A` | 1 | **occluded** (by del3) |
| 5922724 | del4 | `G` | 31 | deletion |
| 7492679 | del5 | `G` | 31 | deletion |
| 7492693 | del6 | `G` | 17 | **occluded** (by del5) |
| 8375794 | del7 | `G` | 29 | deletion |
| 8375822 | snpD | `A` | 1 | **occluded** |

Expected: `detect_occluded_variants` returns `{snpA, snpB, snpC, del6, snpD}` (5 occluded; the tangle collapses
to one drop `snpC`) and `edges` capture occluder→occluded incl. the second-order 5922718↔5922724 as `disjoint`
(no new edge). This is the coordinate-space analogue of the m3-06 LD-topology fixture (6 NaN pairs → 5 distinct
occluded records once the tangle collapses).

### Task-shaped RED tests
- **T1 unit** (`test_occlusion_span_filter.py`): pure-function tests — no-deletion window → `[]`; single
  deletion covering a downstream SNP → that SNP; SNP upstream of a deletion → NOT occluded (disjoint); the
  region-1 fixture → the 5 expected ids; off-by-one boundary (`POS_V == POS_D + len(REF)_D − 1` occluded; `== +
  len(REF)_D` not) ; a SNV (`len(REF)=1`) never occludes.
- **T1 driver integration** (extend `test_run_native_ld_panel.py`): extend `_MockPlink` to honor an `--exclude`
  file (drop those ids from the window before sizing `.ld.bin`/snplist); assert (a) an exclude list is written
  containing exactly the occluded ids, (b) `--exclude` reaches the plink argv, (c) `--keep-allele-order` still
  present, (d) resulting `.npz` has NO NaN and passes `content_verify_npz`, (e) `n_dropped_occluded` recorded and
  `n_dropped_monomorphic` correctly separated.
- **T2** (`test_occlusion_manifest.py`): Stage-A record has all coordinate columns + correct `ref_span` +
  occluder id + `reason`; resume-safe dedup; aggregate rollup concatenates. A liftover test (skips if chain
  absent, per `conftest.chain_fixture` skip pattern) asserts `pos_grch37` matches the hinge-check values
  (5982776/5982778/5982784).
- **T3** (`test_occlusion_present_rate_scan.py`): on a tiny synthetic `.tsv.bgz` (or plain TSV) fixture with the
  harmonized header, a variant present in k of n files → present-rate k/n; absent → 0. (Real 9-file scan is an
  integration/validation step, not a unit test — see Validation Architecture.)
- **T4** (`test_occlusion_lockstep_drop.*`): `drop_occluded_from_sumstats` removes exactly the manifest's
  GRCh37 `(CHR,POS)` rows, logs each drop, leaves non-occluded rows byte-identical, and is idempotent.

### Frozen-contract regressions
`git diff --stat` empty for `read_square_bin`/`content_verify_npz`/`plink_ld_to_npz` npz-writer/`ld_npz_to_rds.R`;
existing `tests/m3` suite stays green (baseline ≈336 passed / 30 skipped per m3-06 verification).

---

## 6. Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11 (`smoke_dev`) | T1/T2/T3 code + tests | ✓ | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python` | — |
| numpy / pandas | filter, manifest, scan | ✓ | in smoke_dev | — |
| pyliftover + hg38ToHg19 chain | manifest b37 positions (Stage B) | ✓ | `data/external/liftover/hg38ToHg19.over.chain.gz` (1.2 MB); pyliftover in `m3-r-ld` env | — |
| AFR harmonized sumstats (9 files) | T3 scan, T2 traits-present, T4 | ✓ | `data/processed/sumstats_harmonized/*.AFR*.tsv.bgz` | — |
| plink1.9 | real panel run (execution, gated) | N/A this phase (mocked in tests) | — | `_MockPlink` seam |
| AoU perimeter / cohort `.bed/.bim/.fam` | real execution of T1 | ✗ (no perimeter access this phase) | — | Test on synthetic + region-1 fixture; real run is gated/deferred |
| R + `m3-r-ld` env | T4 if wired R-side; liftover | ✓ | `/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld` | Python-side T4 filter |

**Missing with no fallback:** none blocking this phase (all NC-State code is testable on synthetic + the
characterized region-1 topology; the real in-perimeter run is explicitly out of scope / gated).

---

## 7. Open risks / unknowns (planner must decide)

1. **[MEDIUM] Occlusion rule edge cases beyond the 6 known pairs.** The recommended rule (exclude any `V` whose
   POS is inside any deletion's footprint, computed over the ORIGINAL window) is SAFE (removes all NaN) but can
   **over-exclude in deletion chains** (D1⊃D2⊃V3: V3 is dropped even if only D2 — now itself dropped — occluded
   it). Rigor-over-speed favors the simple conservative rule with the manifest auditing every drop; a tighter
   iterative rule (drop only the occluded member of each *surviving* NaN pair) is more complex. **Decision: which
   rule.** Recommend the simple rule + manifest, flag chains explicitly in the catalog.
2. **[MEDIUM] Insertions / MNVs / same-position.** The verdict found 0 same-position and the mechanism is
   deletion-span-specific `[CITED: m3_region1_nan_geometry_verdict.md:40-53]`. Confirm the filter keys on
   `len(REF) > 1` (deletion footprint) and does NOT treat insertions (`len(ALT) > len(REF)`, footprint = single
   anchor base) as occluders. **Decision: footprint definition = `len(REF)` only.**
3. **[MEDIUM] T4 exact insertion seam.** `m3-04-W4` consume rule is SUPERSEDED-PENDING-REPLAN
   `[VERIFIED: finemap.smk:89-93]`. The reusable manifest-driven filter is language-agnostic; the seam
   (run_susie_rss.R sumstats load vs a pre-fit harmonization filter vs a Snakemake rule) needs the planner to
   pick. Recommend: land the reusable filter now (Python + tests), wire it when the m3-04 consume replan lands —
   or wire into `run_susie_rss.R::load_ld_matrix`'s sumstats-load if that is the committed consume path.
4. **[LOW] `n_dropped_monomorphic` semantics change.** Splitting occluded from monomorphic drops changes the
   panel-TSV accounting; ensure the existing `test_run_native_ld_panel.py` monomorphic-drop assertions are
   updated, not silently broken.
5. **[LOW] Real `.bim` multi-char-allele confirmation.** The crux is HIGH-confidence from `load_bim`'s contract +
   the verdict's re-derivation, but the real in-perimeter cohort `.bim` cannot be inspected NC-State this phase.
   The gated re-run's region-1 validation is the empirical confirmation (byte-check that the exclude list matches
   the 5 expected ids on the real `.bim`). Flag as a validation-time assertion.
6. **[LOW] Second-order tangle representation in the manifest.** Ensure the manifest records that 5922718 removal
   resolves both the 5922716 and 5922724 edges (one drop, two edges) so the catalog count is honest.

---

## Validation Architecture

> `workflow.nyquist_validation: true` `[VERIFIED: .planning/config.json]` — included.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (py3.11 `smoke_dev`) + base-R `stopifnot` scripts for any R-side (mirroring `tests/testthat-phase1`) |
| Config file | none dedicated; `tests/m3/conftest.py` + root `tests/conftest.py` |
| Quick run | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3/test_occlusion_span_filter.py -x -q` |
| Full suite | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/pytest tests/m3 -q` |

### Phase Requirements → Test Map
| Req behavior | Test type | Automated command | File exists? |
|--------------|-----------|-------------------|--------------|
| Occlusion rule correct on region-1 topology | unit | `pytest tests/m3/test_occlusion_span_filter.py -x` | ❌ Wave 0 |
| `--exclude` reaches plink argv; `--keep-allele-order` preserved | unit | `pytest tests/m3/test_run_native_ld_panel.py -k exclude -x` | ⚠ extend existing |
| Excluded window → `.npz` has NO NaN (frozen `read_square_bin` passes) | integration | `pytest tests/m3/test_run_native_ld_panel.py -k occlusion -x` | ❌ Wave 0 |
| Manifest Stage-A columns + ref_span + reason; resume-safe dedup | unit | `pytest tests/m3/test_occlusion_manifest.py -x` | ❌ Wave 0 |
| b37 liftover matches hinge-check values | unit (skip if no chain) | `pytest tests/m3/test_occlusion_manifest.py -k liftover -x` | ❌ Wave 0 |
| Present-rate k/n on synthetic sumstats | unit | `pytest tests/m3/test_occlusion_present_rate_scan.py -x` | ❌ Wave 0 |
| Lockstep drop = exactly manifest `(CHR,POS)`; idempotent | unit | `pytest tests/m3/test_occlusion_lockstep_drop.py -x` | ❌ Wave 0 |
| Frozen contracts byte-unchanged | regression | `git diff --stat src/python/plink_ld_to_npz.py src/scripts/ld_npz_to_rds.R` empty | ✅ existing discipline |
| **276-region filter sanity (Nyquist sampling)** | integration/validation | scan all AFR manifest rows' windows for occlusion counts → catalog | ❌ Wave 0 (real run gated) |

### Sampling rate
- **Per task commit:** the task's targeted `pytest ... -x -q`.
- **Per wave merge:** `pytest tests/m3 -q` (full suite green, no frozen-module regressions).
- **Phase gate:** full suite green + `git diff --stat` empty on frozen files before `/gsd-verify-work`. The
  **genome-wide 276-region filter correctness** (does the filter fire sensibly across all regions? how many
  occluded / present?) is the REQ-AOU-LD-VALIDATION-class check — it produces the occlusion catalog and is the
  Nyquist "does the fix generalize" sample; it runs against the real `.bim` only at the gated re-run (out of
  scope here) but its logic is unit-covered on the region-1 fixture now.

### Wave 0 gaps
- [ ] `tests/m3/test_occlusion_span_filter.py` — covers the occlusion rule (region-1 fixture).
- [ ] `tests/m3/test_occlusion_manifest.py` — manifest schema + liftover.
- [ ] `tests/m3/test_occlusion_present_rate_scan.py` — present-rate.
- [ ] `tests/m3/test_occlusion_lockstep_drop.py` — T4 filter.
- [ ] extend `tests/m3/test_run_native_ld_panel.py` — `--exclude` argv + integration + `n_dropped_occluded`.
- [ ] synthetic region-1 `.bim` fixture helper (coordinate-space; §5 table).

---

## Security Domain

> `security_enforcement: null` `[VERIFIED: .planning/config.json]` → treated as enabled. This is NC-State,
> code-only, no auth/network surface; the real security boundary is **data egress + LD integrity**.

### Applicable ASVS categories
| ASVS | Applies | Control |
|------|---------|---------|
| V5 Input Validation | yes | `.bim`/manifest parsing already validates 6-col rows + loud raises (`_read_bim_rows`, `_retained_window_bim` uniqueness guard). New filter must validate `len(REF)`/POS are integers/strings and reject malformed rows. |
| V6 Cryptography | no (n/a) | liftover chain SHA-256 already captured for provenance (`ld_npz_to_rds.R:96`); reuse for the manifest's chain provenance. |
| V4 Access Control (egress) | yes | REQ-AOU-LD-EGRESS: only aggregate coordinate metadata (Stage-A manifest) may cross the perimeter; individual-level `.bed/.bim/.fam` never egress (`export_cohort_to_plink` boundary). |

### Threat patterns for this stack
| Pattern | STRIDE | Mitigation |
|---------|--------|-----------|
| Silent over-exclusion corrupts the panel (drops good variants) | Tampering | Deterministic rule + manifest auditing every drop + `n_dropped_occluded` accounting; unit tests pin the exact excluded set on the region-1 fixture. |
| Individual-level data leaks via the manifest | Information disclosure | Stage-A manifest is coordinate/id-only (no genotypes/counts) — egress-clean by construction; enrichment (traits-present, present-rate) runs NC-State on already-public GRCh37 sumstats. |
| Panel↔sumstats desync (orphaned variant) | Tampering / integrity | Lockstep drop (T4) keyed on the same manifest `(CHR,POS)`; drop-only, no re-key. |
| Occluded NaN reaches the fine-mapper | Tampering | Exclude BEFORE `--r` → frozen `read_square_bin` NaN-raise never trips; no NaN in the `.npz`. |

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | The real in-perimeter cohort `.bim` stores full multi-char indel REF in A2 (not `.`/normalized) — inferred from `load_bim`'s contract + the verdict's `len(REF)` re-derivation; not directly inspectable NC-State this phase. | §2 | If A2 were single-char/normalized, `len(REF)` would understate the span and the filter would miss occlusions — CONTRADICTED by the verdict's 60/29/7-bp spans, so risk is LOW; confirm at the gated re-run. |
| A2 | Excluding the downstream occluded member removes every NaN edge (no mutual occlusion). | §2 | A chain could leave a residual edge if over-exclusion is trimmed to a tighter rule — mitigated by the conservative rule + region-1 fixture test. |
| A3 | The T4 sumstats drop belongs at the (re-planned) m3-04 consume seam; the reusable filter is wired there later. | §1 T4, §7 | If wired at the wrong seam, a downstream step could still test an orphaned variant — flagged as an open decision; land the filter + tests now, wire on replan. |

**Non-assumed (VERIFIED):** the `.bim` column order + A1=ALT/A2=REF convention, the `process_region` control
flow + insertion point, `--exclude` composability with `_retained_window_bim`, the liftover recipe, the sumstats
layout/header, the frozen-contract set.

---

## Sources

### Primary (HIGH — read from working tree @ `m3-W2-aou-deltas`)
- `src/python/run_native_ld_panel.py` — driver, `process_region`, `_window_bim_n_var`, `_retained_window_bim`,
  `_needs_retained_subset`, `_append_panel_row_local`, `_PANEL_COLUMNS`.
- `src/python/aou_ld_panel.py` — `build_plink_ld_command` (2854), `export_cohort_to_plink`, `_save_npz`,
  `_existing_region_npz`, `_read_manifest`.
- `src/python/plink_ld_to_npz.py` — `load_bim` (A2=REF/A1=ALT), `read_square_bin` (NaN-raise), block-wise helpers,
  `plink_ld_to_npz` npz writer.
- `src/scripts/ld_npz_to_rds.R` — liftover recipe + chain SHA-256 provenance + `(R, variants)` payload.
- `src/R/regularization/snp_id_bridge.R` — `(CHR,POS)` membership join.
- `tests/m3/test_run_native_ld_panel.py`, `test_condition_ld_matrix.py`, `test_nan_guard.py`, `conftest.py` —
  fixture/RED-first conventions; region-1 topology fixture.
- `config/ld_regions.tsv` (columns), `data/processed/sumstats_harmonized/*.AFR*` (9 files, header), `.planning/config.json`.
- `src/snakemake/rules/finemap.smk` — consume path + `m3-04-W4 STALE/SUPERSEDED-PENDING-REPLAN`.

### Settled science (CITED — byte-verified amendment doc-set)
- `.planning/amendments/m3_region1_nan_geometry_verdict.md` (`4543dcf4…`) — mechanism, 6 pairs, REF spans.
- `.planning/amendments/m3_panel_occlusion_policy_decision.md` (`42d70167…`) — exclude-in-lockstep + provenance.
- `.planning/amendments/m3_region1_occlusion_hinge_check.md` — `(CHR,POS)` join, rs182965575 present 7/9, liftover repro.
- `.planning/phases/.../m3-06-W6-ld-nan-psd-conditioning-PLAN.md` — plan/test conventions; the HELD/dead conditioning path.
- `.planning/REQUIREMENTS.md` — REQ definitions.

## Metadata

**Confidence breakdown:**
- Code-path map (T1/T2): HIGH — read directly from source with line anchors.
- #1 REF-span crux: HIGH — `load_bim` contract + independent verdict re-derivation, two robust sources.
- T3 present-rate: HIGH — scan prototype already run in the hinge check; data present.
- T4 insertion seam: MEDIUM — reusable filter is clear; exact wiring is pending the m3-04 consume replan.
- Occlusion-rule edge cases: MEDIUM — recommended rule is sound on the 6 known pairs; chains/insertions need a decision.

**Research date:** 2026-07-10
**Valid until:** 2026-08-09 (stable internal codebase; re-check if the m3-04 consume replan lands or the AoU loop re-fires).

## RESEARCH COMPLETE
