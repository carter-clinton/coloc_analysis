---
quick_id: 260424-mqo
title: "Route A R2 — figure-number alignment (snappy-humming-pine §2.3 ↔ track_a_pivot.md L291–L297)"
date: 2026-04-24
parent_plan: /home/ckclinto/.claude/plans/snappy-humming-pine.md
upstream_handoff: .planning/quick/260424-lpy-route-a-step-2-3-build-figure-1-cs-yield/260424-lpy-SUMMARY.md (Handoff (b))
authoritative_numbers: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
must_haves:
  truths:
    - "Manuscript Figure 2 slot in docs/manuscript/track_a_pivot.md is the credible-set-yield figure (per L138 in-text reference and L293 caption); the R1-built fig_cs_yield.{R,pdf,png} is the as-built artifact for that slot."
    - "Manuscript Figure 1 = identity-vs-real-LD scatter + LocusZoom panels; Figure 3 = survival forest plot; Figure 4 = pathway enrichment; Figure 5 = variant mechanism + scorecard. snappy-humming-pine.md §2.3 Fig 2 (SH2B3 locus) and §2.3 Fig 3 (pathway enrichment) are *components* of manuscript Figure 1B and Figure 4 respectively, not standalone figures."
    - "The lpy bar plot is the scalar form of manuscript Figure 2's caption description; the per-fit paired beeswarm in the L293 caption remains BLOCKED on the identity-LD re-run (lpy Handoff (a) / snappy-humming-pine §2.2.d pending #4) and is downgraded to a deferred supplementary upgrade in this pass."
  artifacts:
    - "src/R/figures/fig2_cs_yield.R (renamed from fig_cs_yield.R; header comment + OUT_PDF/OUT_PNG paths updated to fig2_*; figure-number note replaced with R2-resolved provenance)"
    - "docs/manuscript/figures/fig2_cs_yield.pdf (renamed from fig_cs_yield.pdf — bytes unchanged)"
    - "docs/manuscript/figures/fig2_cs_yield.png (renamed from fig_cs_yield.png — bytes unchanged)"
    - "docs/manuscript/track_a_pivot.md L293 Figure 2 caption — amended to describe the as-built scalar bar plot AND flag the per-fit paired beeswarm as a deferred supplementary upgrade pending the identity-LD re-run"
    - ".planning/quick/260424-mqo-.../260424-mqo-SUMMARY.md"
  key_links:
    - "/home/ckclinto/.claude/plans/snappy-humming-pine.md (workspace plan, OUT-OF-REPO; §2.3 reconciliation note appended pointing to TRACK-A-PIVOT.md §5 / manuscript captions as the canonical 5-figure scheme — workspace-only edit, NOT in atomic commit)"
---

# Route A R2 — figure-number alignment (snappy-humming-pine §2.3 ↔ track_a_pivot.md L291–L297)

## Context

Quick task `260424-lpy` (commit `46c6ddb`) built the Track A credible-set-yield figure as a 2-bar comparison (12/96 identity-LD vs 51/96 real-LD; 4.25× fold-increase) and saved it under the **neutral filename stem** `fig_cs_yield` because of an unresolved figure-numbering conflict between two authoritative references:

- **`/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.3** (workspace plan) labels the CS-yield figure as **"Fig 1"** in a 3-figure scheme:
  - Fig 1 = CS yield bar plot
  - Fig 2 = SH2B3 12q24 locus plot
  - Fig 3 = pathway enrichment reconfiguration
- **`docs/manuscript/track_a_pivot.md` L289–L297** (live manuscript captions) labels the CS-yield figure as **"Figure 2"** in a 5-figure scheme that agrees with the more developed `.planning/amendments/TRACK-A-PIVOT.md` §5 spec (Figures 1–5 + S1–S6 supplementary).

The lpy SUMMARY's **Handoff (b)** flagged this as the R2 task, with the explicit constraint that "the rename + caption edit + manuscript cross-references must all land in one commit to avoid divergent figure numbering between filename, caption, and in-text reference." This plan delivers that atomic commit.

**Reconciliation direction (auto-mode decision).** Two against one — the manuscript captions (`track_a_pivot.md` L289–L297) and the canonical pivot plan (`.planning/amendments/TRACK-A-PIVOT.md` §5) agree on the **5-figure scheme with CS yield = Figure 2**. The workspace plan (`snappy-humming-pine.md` §2.3) is the outlier and is the artifact to align. The manuscript scheme is also more developed (5 figures + S1–S6) and matches existing in-text cross-references at `track_a_pivot.md` L136 (Figure 1A, Figure S1), L138 (Figure 2 = headline 51/96-vs-12/96 result), L154 (Figure 1A, Figure 3), L170 (Figure 2B, Table S3), and L138 explicitly invokes "Figure 2" for the 4.25× fold-increase that the lpy bar plot delivers.

**Scalar-bar vs paired-beeswarm distinction.** The L293 manuscript Figure 2 caption currently describes a *paired beeswarm of per-fit credible-set sizes*. The lpy artifact is a *2-bar scalar comparison of the 12/96 vs 51/96 counts*. Both convey the headline 4.25× fold-increase, but the per-fit beeswarm requires per-fit identity-LD output that does not exist on disk and is BLOCKED on the identity-LD re-run (lpy Handoff (a) / snappy-humming-pine.md §2.2.d pending #4). This R2 pass amends the L293 caption to describe what was actually built (the bar plot) and flags the paired-beeswarm form as a deferred supplementary upgrade. No content claim changes — both forms render the same 51/96-vs-12/96 contrast.

## Task

### Task 1 — Atomic figure-number alignment commit

**Action:** Six surgical edits in one atomic commit, preserving the lpy artifact bytes:

1. `git mv src/R/figures/fig_cs_yield.R src/R/figures/fig2_cs_yield.R`
2. `git mv docs/manuscript/figures/fig_cs_yield.pdf docs/manuscript/figures/fig2_cs_yield.pdf`
3. `git mv docs/manuscript/figures/fig_cs_yield.png docs/manuscript/figures/fig2_cs_yield.png`
4. **Edit `src/R/figures/fig2_cs_yield.R`** — three inline edits, no body logic changes:
   - L1 header: `# fig_cs_yield.R — Track A Figure 1 (...)` → `# fig2_cs_yield.R — Track A Figure 2 (...)`
   - L25–L26 OUT path comments: `fig_cs_yield.{pdf,png}` → `fig2_cs_yield.{pdf,png}` (both lines)
   - L32 invocation example: `Rscript src/R/figures/fig_cs_yield.R` → `Rscript src/R/figures/fig2_cs_yield.R`
   - L36–L42 figure-number note block: replace the "filename stem is neutral pending R2" deferral with an R2-resolved provenance note pointing to `track_a_pivot.md` L289–L297 + `.planning/amendments/TRACK-A-PIVOT.md` §5 as the canonical Figure-2-slot owner; cross-reference this quick task `260424-mqo` as the alignment-pass artifact
   - Locate `OUT_PDF` and `OUT_PNG` line(s) (search for `fig_cs_yield.pdf` and `fig_cs_yield.png` literals) and replace with `fig2_cs_yield.{pdf,png}`. Inspect via grep first; the lpy SUMMARY tail-listing shows two `ggsave(OUT_*, ...)` calls, so the path constants must be the only literal occurrences.
   - Verify with `grep -n "fig_cs_yield" src/R/figures/fig2_cs_yield.R` — expected count: **0** (zero residual `fig_cs_yield` literals after edit).

5. **Edit `docs/manuscript/track_a_pivot.md` L293 (Figure 2 caption)** — amend the existing caption to describe the as-built scalar bar plot AND flag the paired-beeswarm form as a deferred supplementary upgrade. Replace the existing L293 caption text with:

   > **Figure 2.** Credible-set yield under each LD condition. Two-bar comparison of non-empty SuSiE-RSS credible-set counts across the 96 admissible EUR autosomal SuSiE fits: **12 / 96 (12.5%)** under identity-LD fallback vs **51 / 96 (53.1%)** under real 1000 Genomes Phase 3 EUR LD — a **4.25× fold-increase** in fine-mapping yield. Per-fit paired-beeswarm distribution of credible-set sizes (originally specified for this slot) is deferred to a planned supplementary figure (Figure S2) pending the identity-LD per-fit re-run; the scalar headline 51/96 vs 12/96 contrast is preserved verbatim in both forms.

   This change preserves the 51/96 / 12/96 / 4.25× claims (which appear at L138 and elsewhere unchanged), keeps the "Figure 2" slot stable, and explicitly down-references the paired-beeswarm to `Figure S2` so the manuscript's S1–S6 supplementary roster (L297) accommodates it without renumbering.

6. **Edit `docs/manuscript/track_a_pivot.md` L297 (Supplementary figures roster)** — re-purpose the existing `S2` slot to make the deferred paired-beeswarm explicit. Current text is `(S2) full trait-pair signal distribution comparison identity-vs-real`. Replace with:

   > (S2) per-fit paired-beeswarm of credible-set sizes under identity-LD vs real-LD across the 96 admissible SuSiE fits — **deferred pending identity-LD re-run** (snappy-humming-pine.md §2.2.d pending #4 / quick-task 260424-lpy Handoff (a)); the original full-trait-pair distribution-comparison content moves to S2b once both are buildable;

   Net effect on supplementary count: still S1–S6 (S2 slot now annotated with two deferred sub-panels). No re-numbering downstream.

**Files:**
- `src/R/figures/fig_cs_yield.R` → rename to `src/R/figures/fig2_cs_yield.R`
- `docs/manuscript/figures/fig_cs_yield.pdf` → rename to `docs/manuscript/figures/fig2_cs_yield.pdf`
- `docs/manuscript/figures/fig_cs_yield.png` → rename to `docs/manuscript/figures/fig2_cs_yield.png`
- `docs/manuscript/track_a_pivot.md` (L293 + L297 edits)

**No re-render required.** The figure title rendered into the PDF/PNG is `"SuSiE-RSS credible-set yield across 96 admissible fits"` (already-verified at lpy R script line 172 — no "Figure N" label baked into the image), so the renamed PDF/PNG bytes remain canonical without re-rendering. This avoids any risk of producing different bytes from the same code under a non-pinned env state.

**Verify:**
- `git diff --stat HEAD` shows: 3 renames (R100), 1 modified Rscript (`fig2_cs_yield.R`), 1 modified manuscript (`track_a_pivot.md`).
- `grep -c "fig_cs_yield" src/R/figures/fig2_cs_yield.R` returns `0` (zero residual literals).
- `grep -n "fig_cs_yield" docs/manuscript/track_a_pivot.md` returns nothing (no manuscript references to the old stem).
- `grep -n "Figure 2" docs/manuscript/track_a_pivot.md` returns L138 + L293 + L170 (existing Figure 2B reference) — Figure 2 slot stable, in-text cross-reference at L138 still resolves, the survival-forest references to "Figure 3" at L295 unchanged.
- `grep -n "Figure S2" docs/manuscript/track_a_pivot.md` returns L297 (supplementary roster row 2) — slot annotated.
- `wc -c docs/manuscript/figures/fig2_cs_yield.pdf` returns `23540` (lpy artifact byte-identical).
- `wc -c docs/manuscript/figures/fig2_cs_yield.png` returns `219016` (lpy artifact byte-identical).

**Done:** All six edits committed atomically as `figs(track-a): rename fig_cs_yield → fig2_cs_yield + align manuscript Figure 2 caption to as-built bar form (R2 alignment pass)` — exactly one commit (per the lpy Handoff (b) explicit constraint that rename + caption edit + cross-references land in one commit).

### Task 2 — Workspace-plan housekeeping (out-of-repo, NOT in commit)

**Action:** Append a one-paragraph reconciliation note to `/home/ckclinto/.claude/plans/snappy-humming-pine.md` §2.3 immediately after the existing Fig 1/Fig 2/Fig 3 bullet block, pointing forward readers to the canonical manuscript scheme:

> **R2 reconciliation (260424-mqo, 2026-04-24):** the integer-numbered scheme above is a workspace-plan early sketch; the canonical Track A figure roster (5 figures + S1–S6 supplementary) lives in `.planning/amendments/TRACK-A-PIVOT.md` §5 and `docs/manuscript/track_a_pivot.md` L289–L297. CS-yield bar plot above maps to **manuscript Figure 2** (built per quick-task 260424-lpy as `src/R/figures/fig2_cs_yield.R`); SH2B3 12q24 locus plot above maps to **manuscript Figure 1B** (LocusZoom-style anchor-locus panel — quick-task pending, see lpy Handoff (d)); pathway-enrichment reconfiguration above maps to **manuscript Figure 4** (revise — blocked on pathway-recompute per `<!--PATHWAY-RECOMPUTE-PENDING-->` marker in track_a_pivot.md Discussion + lpy Handoff (e)).

**Files:**
- `/home/ckclinto/.claude/plans/snappy-humming-pine.md` (workspace-plan dir; OUT-OF-REPO — not staged, not committed)

**Verify:**
- `grep -n "R2 reconciliation" /home/ckclinto/.claude/plans/snappy-humming-pine.md` returns one line in §2.3.
- The original three Fig 1/Fig 2/Fig 3 bullets remain unchanged (preserved as historical record of the workspace-plan early sketch).

**Done:** Out-of-repo file edited; no git activity. The fact that this file is outside the repo is intentional — it's the user's personal workspace plan, not a project artifact. The cross-walk note ensures any future re-read of §2.3 immediately routes to the manuscript-canonical scheme.

### Task 3 — Quick-task SUMMARY.md

**Action:** Author `260424-mqo-SUMMARY.md` documenting:
- The six surgical edits in Task 1 + the one workspace-plan annotation in Task 2.
- Verbatim diff hunks for the L293 + L297 manuscript edits and the R-script header / OUT path edits.
- The verification grep / wc-c results from Task 1.
- Updated handoff status: lpy Handoff (b) **resolved** by this task; lpy Handoffs (a), (c), (d), (e) **still open** (none addressed by R2).
- Cross-reference to TRACK-A-FROZEN-NUMBERS.md for the canonical 51/96, 12/96, 4.25× scalars (which remain authoritative and unchanged).

**Files:**
- `.planning/quick/260424-mqo-route-a-r2-figure-number-alignment-recon/260424-mqo-SUMMARY.md`

**Verify:**
- File exists with frontmatter (quick_id, title, date, status, route=A, step="2.3.R2", parent_plan, upstream_handoff).
- All six Task-1 edits documented with file:line references.
- All four still-open lpy handoffs explicitly listed (a, c, d, e) so no future reader assumes R2 closed them.

**Done:** SUMMARY.md authored; orchestrator commits in Step 8 alongside PLAN.md + STATE.md (per gsd-quick workflow contract).

## Verification (end-to-end)

After Tasks 1–3 land:

```bash
# In repo root /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis:
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis

# (a) Renames and bytes
ls -la src/R/figures/fig2_cs_yield.R \
       docs/manuscript/figures/fig2_cs_yield.pdf \
       docs/manuscript/figures/fig2_cs_yield.png
[ ! -f src/R/figures/fig_cs_yield.R ] && [ ! -f docs/manuscript/figures/fig_cs_yield.pdf ] \
  && [ ! -f docs/manuscript/figures/fig_cs_yield.png ] \
  && echo "RENAMES OK"
[ "$(wc -c < docs/manuscript/figures/fig2_cs_yield.pdf)" = "23540" ] \
  && [ "$(wc -c < docs/manuscript/figures/fig2_cs_yield.png)" = "219016" ] \
  && echo "BYTES PRESERVED"

# (b) R-script self-consistency
grep -c "fig_cs_yield" src/R/figures/fig2_cs_yield.R   # expect 0
grep -c "fig2_cs_yield" src/R/figures/fig2_cs_yield.R  # expect ≥4 (header + 2 OUT paths + invocation example)

# (c) Manuscript edits
grep -n "Figure 2\." docs/manuscript/track_a_pivot.md       # expect L293 (caption)
grep -n "Figure S2" docs/manuscript/track_a_pivot.md        # expect L297 (supplementary roster)
grep -n "fig_cs_yield\|fig2_cs_yield" docs/manuscript/track_a_pivot.md  # expect 0 (manuscript references figures by caption number, not filename)
grep -c "51 / 96\|51/96" docs/manuscript/track_a_pivot.md   # ≥2 (L138 + L293 amended caption)
grep -c "12 / 96\|12/96" docs/manuscript/track_a_pivot.md   # ≥2

# (d) Atomic-commit sanity
git log -1 --stat | grep -E "^\s(rename|.*fig2_cs_yield|.*track_a_pivot\.md|.*fig_cs_yield)"   # exactly 4-5 lines
git log -1 --pretty=format:"%s"  # exact commit message string match

# (e) Workspace-plan housekeeping (out-of-repo)
grep -n "R2 reconciliation" /home/ckclinto/.claude/plans/snappy-humming-pine.md  # 1 hit in §2.3

# (f) STATE.md row (orchestrator step 7)
grep -n "260424-mqo" .planning/STATE.md  # ≥1 hit (Quick Tasks Completed table)
```

All eight verification gates above must pass before STATE.md is updated.

## Out of scope

- **Re-rendering the figure.** No content claim changes; bytes remain canonical from the lpy session. Re-rendering risks producing different bytes from the same code under a non-pinned env state.
- **Building per-fit paired beeswarm.** Blocked on identity-LD re-run (lpy Handoff (a) / snappy-humming-pine.md §2.2.d pending #4). Scope deferred to Figure S2 slot per Task 1 edit #6.
- **SH2B3 locus plot (manuscript Fig 1B).** Separate quick task per lpy Handoff (d).
- **Pathway-enrichment reconfiguration (manuscript Fig 4).** Blocked on pathway-recompute per `<!--PATHWAY-RECOMPUTE-PENDING-->` marker (lpy Handoff (e)).
- **Editing TRACK-A-FROZEN-NUMBERS.md.** Scalars unchanged (51/96, 12/96, 4.25×).
- **Editing `.planning/amendments/TRACK-A-PIVOT.md` §5.** Already aligned with the manuscript scheme — no changes needed; this R2 pass aligns the *workspace plan* and the *manuscript figure caption + filename* to TRACK-A-PIVOT.md §5, not the other way around.
- **Updating prior quick-task SUMMARY (lpy).** Historical artifact; the Handoff (b) resolution is captured in this mqo SUMMARY going forward.
