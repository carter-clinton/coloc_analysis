---
quick_task: 260425-ieh
title: results_identity_ld/ tracking decision (don't commit; document)
type: docs
date: 2026-04-25
commit: ec86832
phase_context: quick / Track A finalization (post-k2d deferral resolution)
files_changed: 4
insertions: 115
deletions: 1
decisions:
  - DEC-2026-04-25-01
requirements:
  - QUICK-260425-IEH
---

# Quick Task 260425-ieh: results_identity_ld/ tracking decision — Summary

**One-liner:** Locked the policy that the 160 MB k2d identity-LD fit tree (`results_identity_ld/`, 95 SuSiE JSONs + 95 RDS + 1 manifest) is excluded from git via .gitignore and documented through a tracked 96-line CS-yield summary at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`; resolves the `results_identity_ld/` half of the post-k2d deferral logged at STATE.md L27 via DEC-2026-04-25-01.

## Files Landed (single load-bearing commit `ec86832`)

| File | Status | Bytes | Δ |
|---|---|---|---|
| `.gitignore` | modified | 2,863 | +1 line (`results_identity_ld/` rule, line 80) |
| `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` | created | 12,565 | +96 lines (header + 95 data rows × 13 cols) |
| `.planning/DECISIONS.md` | modified | 42,625 | +17 lines (DEC-2026-04-25-01 entry) |
| `.planning/STATE.md` | modified | 80,079 | -1 / +1 lines (L27 deferral text replaced with resolved-state sentence) |

Total commit: 4 files, 115 insertions, 1 deletion.

## Sanity Gate Results

All four sanity gates from the plan passed at TSV-write time:

- **g1 — file enumeration:** 95 JSON files matched at `results_identity_ld/fine_mapping/susie/*.json`. PASS.
- **g2 — TSV line count:** Output is 96 lines (header + 95 data rows). PASS.
- **g3 — status vocabulary:** Distribution `{ok: 65, too_many_variants: 24, no_variants: 6}`. The two non-`ok` values were not in the planner's predicted vocabulary; per plan instruction these emit a stderr WARN and the summarizer continues (status field is preserved verbatim in the TSV for downstream audits).
- **g4 — SH2B3_12q24 EUR n_CS hard-cross-check:** `{asthma: 0, bmi: 3, hypertension: 10, stroke: 10, t2d: 2}` — exact match to orchestrator-verified locked scalars. PASS.

Per-trait region coverage (regions with ≥1 CS, identity-LD baseline): asthma 7, bmi 10, hypertension 10, stroke 14, t2d 7 (total 48 of 95 fits non-empty under identity-LD).

## .gitignore Verification

After Task 1, `find results_identity_ld -type f | xargs git check-ignore | wc -l` returned **191 / 191** — every file in the tree (95 JSONs caught by the new `results_identity_ld/` rule, 95 RDS objects ALSO caught by the directory rule, 1 manifest TSV caught by the directory rule). `git status --porcelain` no longer surfaces `results_identity_ld/` as `??`. The blanket `*.rds` rule at .gitignore line 105 was already catching the RDS half independently; the new directory rule is what catches the 95 JSONs and the manifest TSV.

Sample `git check-ignore -v` output:

```
.gitignore:80:results_identity_ld/   results_identity_ld/fine_mapping/susie/asthma.EUR.SH2B3_12q24.json
.gitignore:80:results_identity_ld/   results_identity_ld/fine_mapping/finemap_manifest.tsv
.gitignore:80:results_identity_ld/   results_identity_ld/fine_mapping/susie/asthma.AFR.9p21_CDKN2A.fit.rds
```

## DECISIONS.md Entry: DEC-2026-04-25-01

Format mirrors prior 2026-04-24 entries (DEC-2026-04-24-01 / DEC-2026-04-24-02): `## YYYY-MM-DD — DEC-YYYY-MM-DD-NN: <title>` heading, then **Decision** / **Alternatives considered** / **Why** / **How to apply** sections separated by blank lines, no internal horizontal rules. Four alternatives considered: (a) commit everything (rejected — convention violation + 160 MB inflation); (b) commit JSONs only (rejected — partial reconstructibility); (c) git-lfs (rejected — infrastructure cost for a one-shot artifact set in a solo-author public-data project); (d) document only (adopted).

How-to-apply section names all three reproducibility paths: re-fire driver `scripts/fire_identity_ld_rerun.sh` (committed at `08beb4c`), identity-LD payload regenerator `src/snakemake/scripts/make_identity_ld_refs.R`, and the canonical CS-yield summary TSV.

## STATE.md L27 Update

Old text:

> "results_identity_ld/ commit + Fig 1A + Fig 3 builders deferred to post-M1-kickoff /gsd-quick (file sets disjoint from M1 pipeline; STATE.md writes serialize against M1 progress writes)."

New text (in-place at L27, surrounding paragraph preserved):

> "**Both halves of the post-k2d deferral are now resolved:** Fig 1A + Fig 3 builders landed via quick task `260425-1vy` (commits `105484d`, `f862f55`); `results_identity_ld/` tracking decision is locked at DEC-2026-04-25-01 (don't commit; document via .gitignore + canonical CS-yield summary at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`)."

The L27 paragraph header sentence ("k2d identity-LD re-fire complete (2026-04-25):") and the Track A figure-roster context ("Empirically unblocks Track A Figure 1A and Figure 3 ...") were preserved; only the trailing deferral sentence was rewritten. The "(currently untracked in git)" parenthetical on the manifest landing was also dropped since the directory is now formally gitignored, not informally untracked.

## TSV Schema Snapshot

Header row + 95 data rows; columns:

```
trait, ancestry, region_id, chr, start, end, status, n_CS, cs_sizes,
pip_sum_total, ld_overlap, ld_overlap_fraction, sumstats_path
```

Sort order: ascending by `(trait, ancestry, region_id)` — deterministic across re-runs of the summarizer.

Sample first three lines:

```
trait    ancestry   region_id     chr  start      end        status  n_CS  cs_sizes        pip_sum_total  ld_overlap  ld_overlap_fraction  sumstats_path
asthma   AFR        9p21_CDKN2A   9    21000000   23000000   ok      0                     0.000000       0           0.000000             data/processed/sumstats_harmonized/asthma.AFR.tsv.bgz
asthma   AFR        APOE_19q13    19   44000000   46000000   ok      7     3;3;3;3;3;3;3   10.017500      0           0.000000             data/processed/sumstats_harmonized/asthma.AFR.tsv.bgz
```

## Reproducibility Paths Preserved

The decision deliberately preserves three independent reconstruction routes for the identity-LD fit content:

1. **Binary fits:** `bash scripts/fire_identity_ld_rerun.sh` (LSF serial, ~1 hr wall, idempotent under k2d driver). Reads from `data/processed/ld_reference_identity/` + `data/processed/sumstats_harmonized/`.
2. **Identity-LD LD payloads:** `src/snakemake/scripts/make_identity_ld_refs.R` over the 12 region × {EUR, AFR} grid in `config/pipeline_identity_overlay.yaml`.
3. **Empirical CS-yield content:** the new TSV at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` (committed; deterministic; read by future quick tasks via cheap text-join instead of binary RDS load).

Figure scripts (`src/R/figures/fig3_sh2b3_eur_collapse_forest.R`) that read JSONs at runtime continue to function unchanged because the on-disk tree is untouched — only its git-tracking status changed.

## Deviations from Plan

None. The three tasks executed exactly as specified. The g3 stderr WARN on the two non-`ok` status values (`too_many_variants`, `no_variants`) is expected behavior per the plan ("Do NOT hard-fail on unexpected values — print a WARN and continue") — these are valid SuSiE-RSS pre-flight outcomes preserved verbatim in the TSV `status` column.

## Honest Framing Compliance

The DECISIONS.md DEC-2026-04-25-01 entry, the new TSV, the .gitignore line, and the STATE.md L27 update collectively contain zero instances of `revision`, `cleanup`, `fix-up`, `placeholder`, `TBD`, `for now`, `v1`, or `simplified`. The decision is framed as original-research artifact-management policy per `feedback_original_research_framing` user memory.

## Cross-References

- DECISIONS.md: DEC-2026-04-25-01 (this task) ← STATE.md L27 ← this SUMMARY.
- Companion task: quick `260425-1vy` (Fig 1A + Fig 3 builders, commits `105484d` load-bearing + `f862f55` docs) — closes the figure-builder half of the same L27 deferral.
- Source artifact: k2d identity-LD re-fire from quick `260424-k2d` (LSF PID 830748).
- Empirical context: `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` (Stage 2 trait-pair coloc.susie identity-vs-real LD numerics).

## Single Load-Bearing Commit

```
ec86832 docs(quick-260425-ieh): lock results_identity_ld/ tracking decision (DEC-2026-04-25-01)
```

Files: `.gitignore`, `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`, `.planning/DECISIONS.md`, `.planning/STATE.md`. PLAN.md and this SUMMARY.md are committed separately by the orchestrator at step 7+ along with the quick-tasks-table row append in STATE.md.
