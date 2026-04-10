# docs/legacy/

Analytical narratives and summary documents preserved from the pre-revision
analysis on `/rs1`. **Read-only reference.** These describe the state of the
analysis as of ~Jan-Feb 2026, before the methodological revision strategy in
`Revision_Plan.md`.

## Summary documents (prose)

| File | What it describes |
|---|---|
| `FINAL_COLOC_SUMMARY.md` | End-state summary of the region-based colocalization analysis |
| `COMPLETE_ANALYSIS_FINDINGS.md` | Comprehensive findings across all traits × ancestries |
| `HYPERTENSION_COLOC_ANALYSIS.md` | Hypertension-specific deep-dive |
| `HYPERTENSION_COLOC_FINAL_SUMMARY.md` | HTN closeout summary |
| `AFR_COLOC_RERUN_SUMMARY.md` | Rationale + outcome of AFR coloc rerun |
| `AFR_COLOC_RESULTS_ANALYSIS.md` | AFR-specific results interpretation |
| `PATHWAY_ANALYSIS_SUMMARY.txt` | Ad-hoc pathway enrichment results (flagged as methodologically weak in `Revision_Plan.md` §1) |
| `GENOME_WIDE_MANUSCRIPT_SUMMARY.md` | Genome-wide coloc summary tied to the v10 draft |

## Target manifests (what got run)

| File | Contents |
|---|---|
| `coloc_targets.txt` | Full list of region × trait-pair × ancestry targets submitted to the legacy coloc.abf pipeline |
| `coloc_no_overlap_targets.txt` | Targets for the no-overlap variant of the coloc runs |
| `coloc_no_overlap_afr_targets.txt` | AFR-specific no-overlap targets |
| `coloc_no_overlap_missing.txt` | Targets that failed / were missing in the no-overlap run |
| `coloc_no_overlap_afr_missing.txt` | AFR-specific missing targets |

## Tables and tabular summaries

| File | Purpose |
|---|---|
| `Table1_HighConfidence_Signals_Annotated.tsv` | Annotated Tier-1 signals from the pre-revision analysis (flagged as corrupted in `Revision_Plan.md` §10 — will be regenerated in Phase 0) |
| `pathway_enrichment_summary.tsv` | Tabular version of the pathway-enrichment narrative above |

## What's NOT here

Other supplementary tables (Table2, Table3, Table4) existed on `/rs1` but only
as broken symlinks pointing to `/share/clintonlab/ckclinto/admixmap/` — the
path that never resolved. They're preserved as-is under
`archive/pre-revision-2026/shadow-dirs/ml/data/` for audit trail. The
authoritative new Tables 1-4 will be regenerated in Phase 0 (Table 1, 3) and
Phase 4 (new matched-N Table 2) of the revision.
