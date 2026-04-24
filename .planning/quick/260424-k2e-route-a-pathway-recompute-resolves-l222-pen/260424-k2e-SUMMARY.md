---
quick_id: 260424-k2e
phase: quick-260424-k2e
plan: 01
title: "Route A — Pathway re-compute resolution (real-LD Tier A+B = 0 empirically confirmed; L190 [EXTRACT:] resolved + L222 conditional tightened)"
status: complete
completed: "2026-04-24T17:20:00-04:00"
requirements:
  - ROUTE-A-PATHWAY-RECOMPUTE
  - ROUTE-A-L190-EXTRACT-RESOLVE
  - ROUTE-A-L222-CONDITIONAL-TIGHTEN
tags:
  - track-a
  - manuscript
  - pathway-enrichment
  - pathway-recompute
  - original-research
dependency_graph:
  requires:
    - results/qtl_coloc/tier_assignments.tsv (233 rows; authoritative tier classification)
    - .planning/amendments/TRACK-A-FROZEN-NUMBERS.md (frozen Tier A = 0, Tier B = 0, Tier C = 9 values)
    - .planning/amendments/TRACK-A-PIVOT.md §4.17 P2 (verbatim quote to preserve)
    - docs/manuscript/track_a_pivot.md (L190 + L222 edit targets)
    - Commit 6c679de (k2c Discussion R1 that placed PATHWAY-RECOMPUTE-PENDING marker)
  provides:
    - L190 Pathway Enrichment Analysis section resolved to concrete zero-gene finding
    - L222 Reframing paragraph tightened from conditional to definite
    - `<!--PATHWAY-RECOMPUTE-PENDING-->` marker removed (grep count 1 → 0)
    - Empirical proof file at `results/pathway/gprofiler/tier_ab_genes.txt` (0 bytes)
  affects:
    - Route A Step 2.4 bioRxiv preprint package (definitive manuscript prose without placeholders)
    - Route A Step 2.3 Fig 1A + Fig 3 builders — no longer need to wait on pathway re-compute (independent of pathway result)
    - Rule-hardening handoff (extract_tier_ab_genes should accept `resolving_gene` column name) — separate future quick
key_files:
  created:
    - .planning/quick/260424-k2e-route-a-pathway-recompute-resolves-l222-pen/260424-k2e-PLAN.md
    - .planning/quick/260424-k2e-route-a-pathway-recompute-resolves-l222-pen/260424-k2e-SUMMARY.md
    - results/pathway/gprofiler/tier_ab_genes.txt (0 bytes; gitignored — evidence on disk)
  modified:
    - docs/manuscript/track_a_pivot.md (3 lines: L190, L192, L222)
decisions:
  - "Not a Snakemake fire. The extract_tier_ab_genes rule's Python body is deterministic on the tier_assignments.tsv filter (tier in ['Tier A','Tier B']); we ran it inline via pandas to produce the empirical-zero proof file. Running the full Snakemake rule would require fixing an unrelated column-name bug (rule looks up `gene_symbol` or `gene`; current tier_assignments.tsv has `resolving_gene`) — separate future quick."
  - "Retain the identity-LD-era fold-enrichment numbers (40/13/13/10-fold + 63% dominance) as explicitly withdrawn claims rather than deleted ones. Readers can see what the pivot withdraws, matching §4.17's pivot narrative of exposing identity-LD inflation at each scale (locus → pathway). Paragraph remains candid about what the identity-LD era reported before the real-LD audit."
  - "Preserve the §4.17 P2 verbatim quote `primarily an LD-inflation artifact` at L222 — this is the anchor sentence for the Reframing subsection and is quoted verbatim from the amendments file. k2c committed this; k2e retains it while tightening the surrounding conditional clause."
metrics:
  duration_minutes: ~15
  tasks_completed: 3
  paragraphs_edited: 3 (L190 + L192 + L222)
  paragraphs_no_op: Discussion + Conclusion remainder (L216-L257) byte-identical apart from L222
  files_modified: 1
  files_created: 3 (PLAN + SUMMARY + 0-byte proof)
  extract_placeholders_delta: -1 (17 → 16 file-wide)
  pathway_recompute_pending_delta: -1 (1 → 0 file-wide)
---

# Phase quick-260424-k2e Plan 01: Route A pathway re-compute resolution Summary

## Objective

Resolved the `PATHWAY-RECOMPUTE-PENDING` handoff placed at `docs/manuscript/track_a_pivot.md` L222 by the k2c Discussion R1 (commit 6c679de). The empirical re-compute yields a decisive zero-gene result under real-LD at Tier A + Tier B confidence, which fully confirms the §4.17 P2 "primarily an LD-inflation artifact" conclusion embedded in the Discussion. Because the re-compute's input gene list is empirically empty, this is an analytical resolution (not a Snakemake compute fire): write the zero-gene finding into L190 Pathway Enrichment Analysis, tighten the L222 conditional to definite, remove the handoff marker, and drop an empirical proof file at `results/pathway/gprofiler/tier_ab_genes.txt` (0 bytes).

## Per-edit outcome

| Line | Section | Pre state | Post state | Delta |
| --- | --- | --- | --- | --- |
| L190 | Results §Pathway Enrichment Analysis | `[EXTRACT: fold enrichments from results/pathway/ outputs using the real-LD–filtered gene list]` placeholder + conditional "re-evaluated under real-LD" framing | Concrete prose: "Tier A + Tier B gene set contains **zero genes**" + 3 named Tier C genes (APOL1, IRX3, ATXN2, all < 0.5 PP.H4) + "too few (n = 3) for well-powered enrichment" + explicit withdrawal of identity-LD claims | +150 words; `[EXTRACT:]` resolved |
| L192 | Results §Pathway Enrichment Analysis (follow-on) | "We do NOT retain the "63% ..." headline unless it survives the re-compute. If the enrichment pattern changes substantially..." | "The "63% ..." headline does not survive the re-compute and is retracted. The biological-interpretation section below is reframed accordingly." | Definite retraction language; removes "unless"/"if" hedge |
| L222 | Discussion §Reframing of Cardiometabolic Pleiotropy Claims | "Pathway enrichment ... is re-computed in Results §Pathway Enrichment Analysis; if the real-LD re-compute substantially weakens these enrichments, `<!--PATHWAY-RECOMPUTE-PENDING-->` the previously-reported pathway-level architecture ... primarily an LD-inflation artifact..." | "Pathway enrichment ... reported in Results §Pathway Enrichment Analysis, yields zero Tier A + Tier B genes at the manuscript's confidence threshold (PP.H4 ≥ 0.5), making the enrichment test non-computable at threshold. The previously-reported pathway-level architecture ... primarily an LD-inflation artifact..." | Conditional "if" clause removed; `<!--PATHWAY-RECOMPUTE-PENDING-->` HTML comment removed; §4.17 P2 verbatim quote preserved |

## Before / after diffs

### L190 (Pathway Enrichment Analysis paragraph 1)

**Before:**
> Re-computed on the real-LD–surviving gene set, pathway enrichment [EXTRACT: fold enrichments from `results/pathway/` outputs using the real-LD–filtered gene list]. The original identity-LD–sourced claims — ~40-fold appetite-regulation enrichment, ~13-fold insulin-signaling enrichment, ~13-fold glucose-metabolism enrichment, ~10-fold fatty-acid-metabolism enrichment, 63% metabolic pathway dominance — are all re-evaluated under real-LD; a side-by-side identity-vs-real-LD comparison is provided in Figure S5 / Table S7.

**After:**
> Under real-LD, the Tier A + Tier B gene set filtered from `results/qtl_coloc/tier_assignments.tsv` (Tier A: GWAS PP.H4 ≥ 0.8 AND QTL PP.H4 ≥ 0.8; Tier B: GWAS PP.H4 ≥ 0.8 AND QTL PP.H4 ≥ 0.5) contains **zero genes** (0 Tier A + 0 Tier B rows, confirmed at `results/pathway/gprofiler/tier_ab_genes.txt`, 0 bytes). The 9 Tier C rows contain only 3 named resolving genes (APOL1 on cultured fibroblasts, PP.H4 = 0.013; IRX3 on pancreas, PP.H4 = 0.310; ATXN2 on adrenal gland, PP.H4 = 0.052) — all below the 0.5 confidence threshold used for pathway-enrichment input, and too few (n = 3) to support a well-powered enrichment test under any standard framework. The original identity-LD–sourced claims — ~40-fold appetite-regulation enrichment, ~13-fold insulin-signaling enrichment, ~13-fold glucose-metabolism enrichment, ~10-fold fatty-acid-metabolism enrichment, 63% metabolic-pathway dominance — therefore cannot be reproduced under real-LD at the manuscript's confidence threshold. These claims are withdrawn; the side-by-side comparison in Figure S5 / Table S7 reports "real-LD Tier A+B = 0 genes; pathway enrichment non-computable at threshold" against the identity-LD fold-enrichment columns.

### L192 (follow-on paragraph)

**Before:**
> We do NOT retain the "63% of pleiotropic genes converge on metabolic pathways" headline unless it survives the re-compute. If the enrichment pattern changes substantially, the biological-interpretation section below is reframed accordingly.

**After:**
> The "63% of pleiotropic genes converge on metabolic pathways" headline does not survive the re-compute and is retracted. The biological-interpretation section below is reframed accordingly.

### L222 (Discussion Reframing paragraph — target sentence only)

**Before:**
> Pathway enrichment on the real-LD–surviving gene set is re-computed in Results §Pathway Enrichment Analysis; if the real-LD re-compute substantially weakens these enrichments, `<!--PATHWAY-RECOMPUTE-PENDING-->` the previously-reported pathway-level architecture of cardiometabolic pleiotropy is, at these 50 curated loci, primarily an LD-inflation artifact rather than a biological signal.

**After:**
> Pathway enrichment on the real-LD–surviving gene set, reported in Results §Pathway Enrichment Analysis, yields zero Tier A + Tier B genes at the manuscript's confidence threshold (PP.H4 ≥ 0.5), making the enrichment test non-computable at threshold. The previously-reported pathway-level architecture of cardiometabolic pleiotropy is, at these 50 curated loci, primarily an LD-inflation artifact rather than a biological signal.

The surrounding L222 prose (identity-LD fold-enrichment recap, SH2B3 micro-scale analog, Track B forward-pointer) is byte-identical.

## Guardrail verification results

| Check | Expected | Observed | Pass |
| --- | --- | --- | --- |
| `grep -c 'PATHWAY-RECOMPUTE-PENDING' docs/manuscript/track_a_pivot.md` | 0 | 0 | ✅ |
| Pathway `[EXTRACT:]` in L188–L192 | 0 | 0 | ✅ |
| Conditional "if the real-LD re-compute" in L222 | 0 | 0 | ✅ |
| "zero genes" or "Tier A + Tier B" in L190 | ≥ 1 | 1 | ✅ |
| §4.17 P2 quote "primarily an LD-inflation artifact" at L222 | 1 | 1 | ✅ |
| Net `[EXTRACT:]` file delta (pre=17, post=16) | -1 | -1 | ✅ |
| `results/pathway/gprofiler/tier_ab_genes.txt` exists, 0 bytes | 0 | 0 | ✅ |
| Stage 2 real-LD artifacts (finemap_manifest, finemap_summary, coloc_summary, coloc_manifest) md5 preserved | 4/4 OK | 4/4 OK | ✅ |
| k2d identity-LD fire (PID 830748) unaffected (elapsed increases, still running) | running | running (18:23 → 25+ min) | ✅ |

## Empirical proof — tier_ab_genes.txt on disk

```
$ ls -la results/pathway/gprofiler/tier_ab_genes.txt
-rw-r--r-- 1 ckclinto clintonlab 0 Apr 24 17:18 results/pathway/gprofiler/tier_ab_genes.txt
$ wc -l results/pathway/gprofiler/tier_ab_genes.txt
0 results/pathway/gprofiler/tier_ab_genes.txt
```

The file is gitignored (under `results/`) — its existence on disk is the evidence; the git history records the commit that described it.

## Deviations from Plan

### 1. Not running the full Snakemake `extract_tier_ab_genes` rule

- **Found during:** inspection of `src/snakemake/rules/pathway.smk` line 1920–1933 before firing.
- **Issue:** The rule's Python body looks for `gene_symbol` or `gene` column names and ValueErrors if neither exists. The current `results/qtl_coloc/tier_assignments.tsv` has column `resolving_gene` — neither of the expected names. Running the Snakemake rule would fail with a ValueError before producing the empty file.
- **Decision:** Reproduce the rule's filtering logic inline via pandas with `resolving_gene` as the column name. This produces the same empirical result (empty tier_ab_genes.txt) without requiring a separate rule-patch commit.
- **Resolution:** Accepted. A separate /gsd-quick should land the rule hardening (accept `resolving_gene` as a valid column name) — flagged as a handoff below. Not in k2e's scope.

## Authentication gates

None. Pure local manipulation of on-disk artifacts and manuscript prose.

## Handoff notes

### For Route A Step 2.4 (bioRxiv preprint package)

- The manuscript has no remaining Discussion/Reframing placeholders. All pathway claims in the biology-interpretation sections are now empirical and anchored to `results/qtl_coloc/tier_assignments.tsv` row counts.
- L190 Pathway Enrichment Analysis is complete prose (not a placeholder). Figure S5 / Table S7 captions can be generated separately; they report the null result at Tier A+B with identity-LD fold enrichments in a comparison column.
- Conclusion (L248–L256, byte-identical in this quick) does NOT need to change because it already anchors on (a) identity-LD PP.H4 inflation mechanism and (b) the SH2B3 12q24 collapse — both of which stand independent of the pathway re-compute outcome.

### For `extract_tier_ab_genes` rule hardening (separate future /gsd-quick)

The rule at `src/snakemake/rules/pathway.smk:1901–1938` should accept `resolving_gene` as a valid gene-column name. Suggested minimal edit:

```python
for col in ("gene_symbol", "gene", "resolving_gene"):
    if col in tier_ab.columns:
        genes = sorted(tier_ab[col].dropna().unique())
        break
else:
    raise ValueError(...)
```

This lets the rule fire cleanly on the Stage 2 real-LD tier_assignments.tsv without an inline workaround. Separate quick; not blocking for manuscript.

### For Route A Step 2.3 Fig 1A + Fig 3 builders (pending k2d fire completion)

Independent of the pathway re-compute outcome. The k2d identity-LD re-fire (PID 830748, elapsed 25+ min at k2e commit) is still producing `results_identity_ld/fine_mapping/susie/*.json` and will produce `results_identity_ld/multitrait/coloc_susie/*.json` in Phase 2. Fig 1A + Fig 3 are blocked on k2d completion, not on this k2e resolution.

## Commits made

**None inside this editor session yet.** The orchestrator (this session) will perform a single consolidated commit matching the 2.2.e precedent: `docs(quick-260424-k2e): Route A pathway re-compute resolution — real-LD Tier A+B=0 empirical + L190/L222 manuscript edits + STATE.md row`.

Files to commit (all tracked or will be added):
- `docs/manuscript/track_a_pivot.md` (modified — 3 line-level edits)
- `.planning/quick/260424-k2e-route-a-pathway-recompute-resolves-l222-pen/260424-k2e-PLAN.md` (new)
- `.planning/quick/260424-k2e-route-a-pathway-recompute-resolves-l222-pen/260424-k2e-SUMMARY.md` (new, this file)
- `.planning/STATE.md` (row append)

NOT committed:
- `results/pathway/gprofiler/tier_ab_genes.txt` (gitignored under `results/pathway/gprofiler/*`; `*.txt` pattern; evidence on disk)

## Files changed

### Modified
- `docs/manuscript/track_a_pivot.md` — L190 Pathway Enrichment Analysis (concrete zero-gene finding), L192 follow-on (retraction language), L222 Reframing (conditional → definite + PATHWAY-RECOMPUTE-PENDING marker removed).
- `.planning/STATE.md` — append row for k2e under Quick Tasks Completed table.

### Created
- `results/pathway/gprofiler/tier_ab_genes.txt` — 0-byte empirical proof (gitignored).
- `.planning/quick/260424-k2e-route-a-pathway-recompute-resolves-l222-pen/260424-k2e-PLAN.md`
- `.planning/quick/260424-k2e-route-a-pathway-recompute-resolves-l222-pen/260424-k2e-SUMMARY.md`

### Not modified (verified byte-identical)
- `results/qtl_coloc/tier_assignments.tsv` (read-only input)
- `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` (already frozen)
- `results/fine_mapping/*` + `results/multitrait/*` (Stage 2 preserved)
- `results_identity_ld/*` (k2d fire output, in progress)

## Self-Check: PASSED

- `[✓]` `docs/manuscript/track_a_pivot.md` modified at L190 + L192 + L222 (git diff confirms 3+/3- lines)
- `[✓]` `results/pathway/gprofiler/tier_ab_genes.txt` exists at 0 bytes
- `[✓]` `PATHWAY-RECOMPUTE-PENDING` count in file = 0
- `[✓]` L190 `[EXTRACT:]` resolved (awk NR>=188 NR<=192 pathway-placeholder count = 0)
- `[✓]` L222 conditional tightened (no "if the real-LD re-compute")
- `[✓]` §4.17 P2 verbatim quote preserved at L222 (grep exact-string count = 1)
- `[✓]` Net `[EXTRACT:]` file delta = -1 (from 17 to 16)
- `[✓]` Stage 2 real-LD md5 preserved (4/4 OK against pre-fire checksums)
- `[✓]` k2d identity-LD fire (PID 830748) unaffected and still running at k2e commit time
- `[✓]` No executor-internal commit yet; orchestrator Step 8 performs the consolidated commit
