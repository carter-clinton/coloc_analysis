---
archived: true
archived_date: 2026-04-23
archival_reason: superseded-by-m5
original_path: .planning/phases/03-mendelian-randomization/
new_home_reference: .planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md §3 M5
authored_pre_pivot: 2026-04-17
---

# Phase 03 Mendelian Randomization — Archived pre-pivot

## Status

**Archived.** The 5 plans in this directory (`03-01-PLAN.md` through `03-05-PLAN.md`) and their 4 supporting documents (`03-CONTEXT.md`, `03-DISCUSSION-LOG.md`, `03-RESEARCH.md`, `03-VALIDATION.md`) were authored on 2026-04-17 under the pre-pivot candidate-locus scope, which was abandoned on 2026-04-22. These plans are preserved for methodological reference and historical completeness — they are not active work.

## Why

1. **Pre-pivot authorship.** All 5 PLAN.md files were drafted 2026-04-17 as Phase 03 of the T1/T2/T3 tier structure that preceded the 2026-04-22 genome-wide reframe. That tier structure has been retired.

2. **Classical bidirectional MR folded into M5.** Under the adopted milestone sequence (M0–M6 per `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §3), classical bidirectional Mendelian randomization is no longer a standalone phase. It is one axis of **M5 — variant→gene prioritization + novelty cross-reference**, alongside L2G (Open Targets), eQTL/pQTL coloc refresh, Borzoi variant-effect scoring, and the 5-class novel-variant cross-reference pipeline (§7). M5's MR component inherits the methods stack from these archived plans (TwoSampleMR, MR-PRESSO, Steiger filtering, hyprcoloc-adjacent two-sample coloc) but operates on the genome-wide region list produced by M2 (LDSC+MTAG+CPASSOC), not on the 50 candidate loci these plans targeted.

3. **Fresh M5 plans will be drawn at M5 kickoff.** When the M5 slot opens (estimated 2027-02 per Amendment §11 timeline), a new `.planning/phases/` directory will be created under a name aligned with the M0–M6 convention (e.g., `.planning/phases/M5-variant-gene-prioritization/`). The M5 planning cycle will cite these archived plans as prior art, but will not reuse them verbatim — the scope change from 50 candidate loci to genome-wide Tier A coloc signals + AFR-specific credible sets changes the instrument-variant selection logic, the population-stratification guards, and the pleiotropy-sensitivity sweep substantially.

4. **Content remains readable.** Nothing is deleted. All 9 files remain accessible at this archive path for (a) reviewing the pre-pivot MR methodology when drafting M5, (b) citation in the Track A manuscript if the candidate-locus MR framing is discussed as part of the superseded design, and (c) forensic traceability of the pivot decision itself. `git log --follow <filename>` resolves back to the pre-move history for every file.

## Original scope snapshot

- Target: classical two-sample + bidirectional MR across 5 trait pairs (bmi↔t2d, bmi↔hypertension, asthma↔stroke, plus permutations) within the 50 pre-registered candidate regions.
- Methods stack: TwoSampleMR (inverse-variance weighted, MR-Egger, weighted median, weighted mode), MR-PRESSO for pleiotropy, Steiger directionality filtering, hyprcoloc as a pleiotropy-sanity secondary.
- Instrument selection: genome-wide-significant SNPs from discovery sumstats within each candidate region, LD-clumped r² < 0.01.
- 5 plans: 03-01 (instrument harvesting + harmonization), 03-02 (primary bidirectional MR), 03-03 (sensitivity + pleiotropy), 03-04 (hyprcoloc secondary), 03-05 (aggregation + validation per 03-VALIDATION.md contract).
- Execution gate at authorship time: CP#1-final (T1 first-production Tier A resolution). That gate never cleared under the pre-pivot design — the 2026-04-22 Stage 2 real-LD fire resolved 0 Tier A and triggered the pivot instead.

## What replaces this

`.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §3 (M5 row) describes the successor scope. Key differences relative to this archive:

- **Scope**: genome-wide Tier A + AFR-specific signals from M4, not 50 candidate regions.
- **MR as one axis among several**: L2G + eQTL/pQTL coloc + Borzoi + MR, with MR positioned as directional-evidence triangulation, not as the primary discovery engine.
- **Novelty cross-reference integrated**: M5 cross-references Tier A coloc loci against locked exports of Pickrell 2016, Watanabe 2019 GWAS Atlas, Open Targets Genetics L2G top-3, GWAS Catalog, and ClinVar + PubMed for functional-mechanism novelty (Classes 4 + 5 per Amendment §7).
- **Pre-registration**: M5's scope is covered by the forthcoming OSF amendment (posted end-of-M1 per Amendment §9.1), not by the original osf.io/pvb5j candidate-locus pre-reg.

## Pointers

- Pivot charter: [../../../amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md](../../../amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md)
- M0–M6 roadmap summary: Amendment §3
- Preserved artifacts manifest: Amendment §8
- Track A (real-LD audit of candidate-locus claims): [../../../amendments/TRACK-A-PIVOT.md](../../../amendments/TRACK-A-PIVOT.md)
- Session-continuity context for the 2026-04-22 pivot: `.planning/STATE.md` `### This session (2026-04-22 → 2026-04-23)` block.
