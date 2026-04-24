---
quick_id: 260424-mqo
title: "Route A R2 — figure-number alignment (snappy-humming-pine §2.3 ↔ track_a_pivot.md L291–L297)"
date: 2026-04-24
status: complete
route: A
step: "2.3.R2"
parent_plan: /home/ckclinto/.claude/plans/snappy-humming-pine.md
upstream_handoff: .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md (Handoff (b))
authoritative_numbers: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
outputs:
  - src/R/figures/fig2_cs_yield.R (renamed + edited; 9 hunks)
  - docs/manuscript/figures/fig2_cs_yield.pdf (renamed; bytes unchanged 23,540)
  - docs/manuscript/figures/fig2_cs_yield.png (renamed; bytes unchanged 219,016)
  - docs/manuscript/track_a_pivot.md (L293 caption + L297 supplementary roster amended)
  - /home/ckclinto/.claude/plans/snappy-humming-pine.md §2.3 (out-of-repo R2 reconciliation annotation)
commits:
  - 08944a8 — atomic R2 alignment pass (3 renames + 1 manuscript modify; 4 files, 20+/13- lines)
  - 7bb7d8c — chore follow-on aligning 4 diagnostic-message self-name strings (Rule 3 deviation; see below)
---

# Route A R2 — figure-number alignment (snappy-humming-pine §2.3 ↔ track_a_pivot.md L291–L297) — SUMMARY

## Objective

Quick task `260424-mqo` is the R2 alignment pass that resolves the figure-numbering drift flagged by **lpy Handoff (b)**: the workspace-plan early-sketch (`/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.3) labelled the credible-set-yield artifact as "Fig 1" in a 3-figure scheme, while the canonical manuscript scheme (`docs/manuscript/track_a_pivot.md` L289–L297 + `.planning/amendments/TRACK-A-PIVOT.md` §5) places it at the Figure 2 slot in a 5-figure + S1–S6 supplementary roster. R1 deferred the rename to "R2 with manuscript caption alignment in one atomic commit" — this task delivers that atomic commit.

Reconciliation direction: two-against-one — manuscript captions agree with the canonical pivot plan on **CS yield = Figure 2 in the 5-figure scheme**. The workspace plan was the outlier and is the artifact to align.

## Edits delivered

### Task 1 — Atomic figure-number alignment commit (commit 08944a8)

Six surgical edits in one atomic commit per the lpy Handoff (b) explicit one-commit constraint:

**Renames (git mv, recorded as 100/100/85% similarity):**

1. `src/R/figures/fig_cs_yield.R` → `src/R/figures/fig2_cs_yield.R` (R85)
2. `docs/manuscript/figures/fig_cs_yield.pdf` → `docs/manuscript/figures/fig2_cs_yield.pdf` (R100)
3. `docs/manuscript/figures/fig_cs_yield.png` → `docs/manuscript/figures/fig2_cs_yield.png` (R100)

**R-script edits (4 hunks inside `src/R/figures/fig2_cs_yield.R`):**

4. **L1 header** —
   - Before: `# fig_cs_yield.R — Track A Figure 1 (identity-LD vs real-LD credible-set yield)`
   - After: `# fig2_cs_yield.R — Track A Figure 2 (identity-LD vs real-LD credible-set yield)`

5. **L25–L26 OUT path comments** —
   - Before:
     ```
     #   docs/manuscript/figures/fig_cs_yield.pdf   (cairo_pdf, 85 mm x 70 mm)
     #   docs/manuscript/figures/fig_cs_yield.png   (600 dpi, 85 mm x 70 mm)
     ```
   - After:
     ```
     #   docs/manuscript/figures/fig2_cs_yield.pdf  (cairo_pdf, 85 mm x 70 mm)
     #   docs/manuscript/figures/fig2_cs_yield.png  (600 dpi, 85 mm x 70 mm)
     ```

6. **L31–L39 invocation example + figure-number provenance block** —
   - Before (R1 R2-deferral note): "Figure-number note: filename stem is neutral ('fig_cs_yield') pending manuscript caption-alignment pass (R2). snappy-humming-pine.md §2.3 labels this as 'Fig 1'; docs/manuscript/track_a_pivot.md L291-L297 currently labels Fig 1 as the scatter + LocusZoom panels. Integer-rename is an R2 handoff task."
   - After (R2-resolved provenance): full annotation of the canonical 5-figure scheme as the slot owner, cross-referencing `track_a_pivot.md` L289–L297, `.planning/amendments/TRACK-A-PIVOT.md` §5, and `TRACK-A-FROZEN-NUMBERS.md` for the locked scalars (12 / 96 / 51 / 4.25×). Also updated invocation-example path from `Rscript src/R/figures/fig_cs_yield.R` to `Rscript src/R/figures/fig2_cs_yield.R` and author-line from `(quick-260424-lpy)` to `(built quick-260424-lpy; aligned quick-260424-mqo)`.

7. **L59–L60 OUT_PDF / OUT_PNG path constants** —
   - Before:
     ```r
     OUT_PDF   <- file.path(OUT_DIR, "fig_cs_yield.pdf")
     OUT_PNG   <- file.path(OUT_DIR, "fig_cs_yield.png")
     ```
   - After:
     ```r
     OUT_PDF   <- file.path(OUT_DIR, "fig2_cs_yield.pdf")
     OUT_PNG   <- file.path(OUT_DIR, "fig2_cs_yield.png")
     ```

**Manuscript edits (2 hunks inside `docs/manuscript/track_a_pivot.md`):**

8. **L293 Figure 2 caption** — amended from the originally-specified per-fit paired-beeswarm description (which is BLOCKED on the identity-LD per-fit re-run) to describe the as-built scalar two-bar credible-set-yield comparison. Verbatim diff hunk:
   - Before: `**Figure 2.** Credible-set size distribution under each LD condition (NEW). Paired beeswarm plot over the 96 admissible SuSiE fits showing credible-set size under identity-LD (left) vs real-LD (right). Zero-size (empty credible set) fits are counted below the axis; the 51/96 non-empty (real-LD) vs 12/96 non-empty (identity-LD) contrast is annotated.`
   - After: `**Figure 2.** Credible-set yield under each LD condition. Two-bar comparison of non-empty SuSiE-RSS credible-set counts across the 96 admissible EUR autosomal SuSiE fits: **12 / 96 (12.5%)** under identity-LD fallback vs **51 / 96 (53.1%)** under real 1000 Genomes Phase 3 EUR LD — a **4.25× fold-increase** in fine-mapping yield. Per-fit paired-beeswarm distribution of credible-set sizes (originally specified for this slot) is deferred to a planned supplementary figure (Figure S2) pending the identity-LD per-fit re-run; the scalar headline 51/96 vs 12/96 contrast is preserved verbatim in both forms.`

9. **L297 Supplementary figures roster** — re-purposed S2 slot to make the deferred per-fit paired-beeswarm explicit. S2 net count unchanged (still S1–S6); original full-trait-pair distribution-comparison content moves to S2b once both are buildable. Verbatim diff hunk:
   - Before: `**Figure S1–S6.** Supplementary figures covering (S1) per-region pairwise test counts; (S2) full trait-pair signal distribution comparison identity-vs-real; (S3, S4) NEGR1/TMEM18 regional detail if they survive; (S5) pathway enrichment identity-vs-real side-by-side; (S6) negative-control behavior.`
   - After: `**Figure S1–S6.** Supplementary figures covering (S1) per-region pairwise test counts; (S2) per-fit paired-beeswarm of credible-set sizes under identity-LD vs real-LD across the 96 admissible SuSiE fits — **deferred pending identity-LD re-run** (snappy-humming-pine.md §2.2.d pending #4 / quick-task 260424-lpy Handoff (a)); the original full-trait-pair distribution-comparison content moves to S2b once both are buildable; (S3, S4) NEGR1/TMEM18 regional detail if they survive; (S5) pathway enrichment identity-vs-real side-by-side; (S6) negative-control behavior.`

**Atomic commit envelope:**

```
commit 08944a8df51e5a1a43edd9b411cb2605be39c070
Author: Carter K. Clinton <carterclinton@ncsu.edu>
Date:   Fri Apr 24 16:35:41 2026 -0400

    figs(track-a): rename fig_cs_yield → fig2_cs_yield + align manuscript Figure 2 caption to as-built bar form (R2 alignment pass)

 .../{fig_cs_yield.pdf => fig2_cs_yield.pdf}        | Bin
 .../{fig_cs_yield.png => fig2_cs_yield.png}        | Bin
 docs/manuscript/track_a_pivot.md                   |   4 +--
 src/R/figures/{fig_cs_yield.R => fig2_cs_yield.R}  |  29 +++++++++++++--------
 4 files changed, 20 insertions(+), 13 deletions(-)
```

Stat envelope: exactly 4 files — 3 renames (R85 / R100 / R100) + 1 manuscript modify. Matches PLAN line 79 expectation verbatim.

### Task 2 — Workspace-plan housekeeping (out-of-repo, NOT in commit)

Appended one-paragraph R2 reconciliation note to `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.3 immediately after the existing Fig 1/Fig 2/Fig 3 bullet block (now line 157). The original three workspace-plan bullets (Fig 1 = CS yield / Fig 2 = SH2B3 / Fig 3 = pathway) remain unchanged as historical record of the early-sketch numbering. The R2 reconciliation note explicitly cross-walks each workspace-plan bullet to its canonical manuscript-scheme target:

- Workspace Fig 1 (CS yield) → manuscript **Figure 2** (built per quick-260424-lpy as `src/R/figures/fig2_cs_yield.R`)
- Workspace Fig 2 (SH2B3 12q24 locus) → manuscript **Figure 1B** (LocusZoom-style anchor-locus panel — quick-task pending, see lpy Handoff (d))
- Workspace Fig 3 (pathway enrichment) → manuscript **Figure 4** (revise — blocked on pathway-recompute per `<!--PATHWAY-RECOMPUTE-PENDING-->` marker + lpy Handoff (e))

This file is OUTSIDE the project repo (lives under `/home/ckclinto/.claude/plans/`); per PLAN, the edit is workspace-only and not staged.

### Task 3 — This SUMMARY (authored, not committed by executor)

This file at `.planning/quick/260424-mqo-route-a-r2-figure-number-alignment-recon/260424-mqo-SUMMARY.md`. Per gsd-quick workflow contract, the orchestrator commits this alongside the PLAN.md and STATE.md row in Step 8.

## Verification gates — verbatim output

All 8 gates PASS. Verbatim output captured below.

### Gate (a) — Renames + bytes preserved

```
=== (a1) renamed artifacts present ===
-rw-r--r--. 1 ckclinto clintonlab  23540 Apr 24 15:48 docs/manuscript/figures/fig2_cs_yield.pdf
-rw-r--r--. 1 ckclinto clintonlab 219016 Apr 24 15:48 docs/manuscript/figures/fig2_cs_yield.png
-rw-r--r--. 1 ckclinto clintonlab   9197 Apr 24 16:38 src/R/figures/fig2_cs_yield.R

=== (a2) old-stem files absent ===
RENAMES OK

=== (a3) bytes preserved ===
BYTES PRESERVED
 23540 docs/manuscript/figures/fig2_cs_yield.pdf
219016 docs/manuscript/figures/fig2_cs_yield.png
```

### Gate (b) — R-script self-consistency

```
=== (b1) residual fig_cs_yield literals (expect 0) ===
0
=== (b2) fig2_cs_yield literal count (expect ≥4) ===
11
```

Note: gate (b1) initially returned 4 after the atomic commit `08944a8` — four `fig_cs_yield.R:` self-name strings inside `stop()` and `message()` diagnostic calls were missed in the header-only Task-1 sweep. Resolved via follow-up `chore` commit `7bb7d8c` (see "Deviations from Plan" below). Final state: 0 residual literals as PLAN-required.

### Gate (c) — Manuscript edits

```
=== (c1) residual filename literals in manuscript (expect 0) ===
0
=== (c2) 51/96 references (expect ≥2) ===
3
=== (c3) 12/96 references (expect ≥2) ===
3
=== (c4) deferred / Figure S2 markers ===
293:**Figure 2.** Credible-set yield under each LD condition. Two-bar comparison of non-empty SuSiE-RSS credible-set counts across the 96 admissible EUR autosomal SuSiE fits: **12 / 96 (12.5%)** under identity-LD fallback vs **51 / 96 (53.1%)** under real 1000 Genomes Phase 3 EUR LD — a **4.25× fold-increase** in fine-mapping yield. Per-fit paired-beeswarm distribution of credible-set sizes (originally specified for this slot) is deferred to a planned supplementary figure (Figure S2) pending the identity-LD per-fit re-run; the scalar headline 51/96 vs 12/96 contrast is preserved verbatim in both forms.
297:**Figure S1–S6.** Supplementary figures covering (S1) per-region pairwise test counts; (S2) per-fit paired-beeswarm of credible-set sizes under identity-LD vs real-LD across the 96 admissible SuSiE fits — **deferred pending identity-LD re-run** (snappy-humming-pine.md §2.2.d pending #4 / quick-task 260424-lpy Handoff (a)); the original full-trait-pair distribution-comparison content moves to S2b once both are buildable; (S3, S4) NEGR1/TMEM18 regional detail if they survive; (S5) pathway enrichment identity-vs-real side-by-side; (S6) negative-control behavior.
```

### Gate (d) — Atomic-commit sanity (R2 alignment commit 08944a8)

```
=== (d1) atomic-commit stat envelope ===
commit 08944a8df51e5a1a43edd9b411cb2605be39c070
 .../{fig_cs_yield.pdf => fig2_cs_yield.pdf}        | Bin
 .../{fig_cs_yield.png => fig2_cs_yield.png}        | Bin
 docs/manuscript/track_a_pivot.md                   |   4 +--
 src/R/figures/{fig_cs_yield.R => fig2_cs_yield.R}  |  29 +++++++++++++--------
 4 files changed, 20 insertions(+), 13 deletions(-)

=== (d2) atomic-commit subject ===
figs(track-a): rename fig_cs_yield → fig2_cs_yield + align manuscript Figure 2 caption to as-built bar form (R2 alignment pass)
```

Subject string matches PLAN line 87 exactly.

### Gate (e) — Workspace-plan housekeeping (out-of-repo)

```
157:> **R2 reconciliation (260424-mqo, 2026-04-24):** the integer-numbered scheme above is a workspace-plan early sketch; the canonical Track A figure roster (5 figures + S1–S6 supplementary) lives in `.planning/amendments/TRACK-A-PIVOT.md` §5 and `docs/manuscript/track_a_pivot.md` L289–L297. ...
```

One hit, in §2.3, immediately after the Fig 1/Fig 2/Fig 3 bullet block. Original bullets unchanged.

### Gates summary

| Gate | Description | Expected | Actual | Status |
| ---- | ----------- | -------- | ------ | ------ |
| (a1) | Renamed artifacts present | 3 files | 3 files | PASS |
| (a2) | Old-stem files absent | none | none | PASS |
| (a3) | Bytes preserved | 23540 / 219016 | 23540 / 219016 | PASS |
| (b1) | Residual fig_cs_yield literals | 0 | 0 (after `7bb7d8c`) | PASS |
| (b2) | fig2_cs_yield literal count | ≥4 | 11 | PASS |
| (c1) | Manuscript filename literals | 0 | 0 | PASS |
| (c2) | 51/96 references | ≥2 | 3 | PASS |
| (c3) | 12/96 references | ≥2 | 3 | PASS |
| (c4) | Deferred/Figure S2 markers | L293 + L297 | L293 + L297 | PASS |
| (d1) | Atomic commit stat envelope | 4 files (3 renames + 1 modify) | 4 files (R85 + R100 + R100 + M) | PASS |
| (d2) | Commit subject string | exact PLAN match | exact PLAN match | PASS |
| (e)  | R2 reconciliation note in workspace plan | 1 hit in §2.3 | 1 hit at L157 | PASS |

12 of 12 sub-gates PASS (the PLAN's "8 gates" expand to 12 sub-checks; all green).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking issue] Diagnostic-message self-name strings split into follow-on `chore` commit `7bb7d8c`**

- **Found during:** Verification gate (b1) after atomic commit `08944a8`.
- **Issue:** PLAN line 56/80 specified gate (b1) as `grep -c "fig_cs_yield" src/R/figures/fig2_cs_yield.R` returns `0`. After `08944a8` landed, the count was 4 — four `fig_cs_yield.R:` self-name string literals inside `stop()` and `message()` diagnostic calls (lines 72, 87, 107, 202 of the renamed script) were missed in the Task-1 header-and-paths sweep. These are the script's own name reported in error/diagnostic stdout to the user; they do not affect functionality and are not load-bearing path references.
- **Resolution:** Renamed all four diagnostic-message self-name strings from `fig_cs_yield.R:` to `fig2_cs_yield.R:` (4 hunks, 4 insertions / 4 deletions, single file). Final state of gate (b1) = 0 residual literals as PLAN-required.
- **Commit:** `7bb7d8c chore(track-a): align fig2_cs_yield.R diagnostic-message self-name strings to renamed stem`
- **Atomicity-constraint impact:** This split into a second commit is a real deviation from the lpy Handoff (b) "exactly one commit" constraint. The deviation is documented transparently here. **Mitigating factors:** (i) The load-bearing portion of Handoff (b) — "rename + caption edit + manuscript cross-references" — DID land atomically in `08944a8` as required; (ii) the residual literals are diagnostic-message self-name strings, not load-bearing path references or manuscript cross-references; (iii) two descendant commits (`d355a4a docs(m1): research — sumstats upgrade and harmonization` + `1e3a9df docs(m1): add Nyquist validation strategy`) authored by a parallel session landed on top of `08944a8` between the executor's atomic commit and the gate (b1) re-check, making `git commit --amend` of `08944a8` unsafe per the GSD safety protocol's prohibition on destructive operations against descendant commits. A `git rebase -i HEAD~3` to fold the four-string edit into `08944a8` would have required reordering / force-pushing through the two intervening commits, which is forbidden by the safety protocol.
- **Files modified:** `src/R/figures/fig2_cs_yield.R` only (4 hunks, all string-literal renames inside `stop()`/`message()` calls).

No other deviations. The plan's six surgical edits (Task 1) all landed atomically in `08944a8`; the workspace-plan annotation (Task 2) landed at L157 of `snappy-humming-pine.md`; this SUMMARY (Task 3) is authored at the canonical path.

## Locked scalars — unchanged

Per PLAN constraint #6, the following Stage 2 scalars from `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` were preserved verbatim across all edits and were not re-derived in this pass:

| Scalar | Value | Source row in TRACK-A-FROZEN-NUMBERS.md |
| ------ | ----- | --------------------------------------- |
| Total admissible EUR autosomal SuSiE fits | **96** | denominator row |
| Identity-LD fallback non-empty CS count | **12** | pre-Stage-2 baseline row |
| Real 1000G Phase 3 EUR LD non-empty CS count | **51** | Stage 2 production-fire row |
| Fold-change in CS yield | **4.25×** | derived (51 / 12) |

These scalars appear in the manuscript at the L138 in-text reference (unchanged), the L293 amended Figure 2 caption (newly emphasized), the supplementary roster L297 (cited in the deferred-S2 annotation), and as `N_TOTAL_FITS = 96L`, `N_IDENTITY_LD_NONEMPTY = 12L`, `N_REAL_LD_NONEMPTY = 51L`, `FOLD_CHANGE_EXPECTED = 4.25` in the renamed R script. All references remain consistent.

## Handoff status update

Per lpy SUMMARY's five handoff flags:

| Handoff | Topic | Status after R2 (260424-mqo) |
| ------- | ----- | ---------------------------- |
| (a) | Identity-LD per-fit re-run session (50-fit subset) | **STILL OPEN** — blocks per-fit paired beeswarm at S2; planned bsub queue decision pending. R2 explicitly accommodates this by routing the deferred beeswarm to the S2 slot with the "deferred pending identity-LD re-run" flag in the L297 caption. |
| (b) | R2 figure-number alignment pass | **RESOLVED** by this task. CS-yield artifact is now `fig2_cs_yield` aligned to manuscript Figure 2 slot; rename + caption edit + manuscript cross-references landed in atomic commit `08944a8`. |
| (c) | Dedicated figure-build env (`envs/r_figures.yml`) | **STILL OPEN** — `la_multitrait_r` remains the de-facto build env for R1 + R2; no functional impact on R2 since no re-render was performed. Low priority; not blocking. |
| (d) | Figure 2 build — SH2B3 12q24 locus plot (manuscript Figure 1B per the R2 reconciliation cross-walk) | **STILL OPEN** — separate quick task; design decision (LocusZoom embed vs custom ggplot vs Manhattan strip) outstanding. |
| (e) | Figure 3 build — pathway enrichment reconfiguration (manuscript Figure 4 per the R2 reconciliation cross-walk) | **STILL OPEN** — blocked on pathway Results re-compute per `<!--PATHWAY-RECOMPUTE-PENDING-->` marker (lpy Handoff (e)). |

Net: R2 closes 1 of the 5 open handoffs (b). The remaining 4 (a, c, d, e) are unchanged and remain queued for subsequent quick-task sessions.

## What R2 explicitly did NOT do

- **Did not re-render the figure.** PDF/PNG bytes are byte-identical to lpy artifacts (23,540 / 219,016 bytes) — the figure title rendered into the image is `"SuSiE-RSS credible-set yield across 96 admissible fits"` (no "Figure N" baked into the image), so the rename is content-stable without re-render.
- **Did not build the per-fit paired beeswarm.** Blocked on the identity-LD per-fit re-run; deferred to S2 slot per L297 amendment.
- **Did not edit `TRACK-A-FROZEN-NUMBERS.md`.** Locked scalars unchanged.
- **Did not edit `.planning/amendments/TRACK-A-PIVOT.md` §5.** Already aligned with the manuscript scheme — R2 aligns the workspace plan and the manuscript caption to TRACK-A-PIVOT.md §5, not the other way around.
- **Did not update STATE.md.** Per PLAN, the orchestrator owns the STATE.md row update in Step 7.
- **Did not update lpy SUMMARY.** Historical artifact; lpy Handoff (b) resolution is captured here in the mqo SUMMARY going forward.

## Self-check

File existence verification:

| Artifact | Expected path | Present |
| -------- | ------------- | ------- |
| Renamed R script | `src/R/figures/fig2_cs_yield.R` | yes (9,197 bytes) |
| Renamed Figure PDF | `docs/manuscript/figures/fig2_cs_yield.pdf` | yes (23,540 bytes — byte-identical to lpy) |
| Renamed Figure PNG | `docs/manuscript/figures/fig2_cs_yield.png` | yes (219,016 bytes — byte-identical to lpy) |
| Old-stem R script | `src/R/figures/fig_cs_yield.R` | absent (renamed) |
| Old-stem PDF | `docs/manuscript/figures/fig_cs_yield.pdf` | absent (renamed) |
| Old-stem PNG | `docs/manuscript/figures/fig_cs_yield.png` | absent (renamed) |
| Manuscript caption edit | `docs/manuscript/track_a_pivot.md` L293 | present (verified via gate c4) |
| Manuscript supplementary roster edit | `docs/manuscript/track_a_pivot.md` L297 | present (verified via gate c4) |
| Workspace-plan annotation | `/home/ckclinto/.claude/plans/snappy-humming-pine.md` L157 | present (verified via gate e) |
| This SUMMARY | `.planning/quick/260424-mqo-route-a-r2-figure-number-alignment-recon/260424-mqo-SUMMARY.md` | yes |

Commit existence verification:

| Commit | Subject | Exists |
| ------ | ------- | ------ |
| `08944a8` | `figs(track-a): rename fig_cs_yield → fig2_cs_yield + align manuscript Figure 2 caption to as-built bar form (R2 alignment pass)` | yes (verified via `git log -1 --pretty=format:"%s" 08944a8`) |
| `7bb7d8c` | `chore(track-a): align fig2_cs_yield.R diagnostic-message self-name strings to renamed stem` | yes (verified via `git log -1 --pretty=format:"%s" 7bb7d8c`) |

Framing audit: no occurrences of the three forbidden framing terms (the project memory's banned framing-context vocabulary) appear in this SUMMARY body, the atomic commit message, the chore commit message, the R-script provenance comment block, the manuscript caption edits, or the workspace-plan annotation. R2 is consistently framed as an "alignment pass" / "R2 alignment pass" / "R2 reconciliation" per the project memory rule on hypothesis-driven original-research framing.

Citation audit (each referenced by name at least once):

- `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` — cited in Locked scalars table + R-script provenance block.
- `.planning/amendments/TRACK-A-PIVOT.md` §5 — cited in Objective, R-script provenance block, and What R2 explicitly did NOT do.
- `docs/manuscript/track_a_pivot.md` L289–L297 — cited in Objective, R-script provenance block, and verification gate (c4).
- `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.3 — cited in Objective, Task 2, and the §2.3 annotation itself.
- `260424-lpy-SUMMARY.md` Handoff (b) — cited in Objective, Edits delivered, Deviations, and Handoff status update.

**Self-Check: PASSED**
