---
phase: quick-260425-ieh
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .gitignore
  - .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv
  - .planning/DECISIONS.md
  - .planning/STATE.md
autonomous: true
requirements:
  - QUICK-260425-IEH
must_haves:
  truths:
    - "Untracked results_identity_ld/ tree no longer surfaces as ?? in git status (caught by .gitignore)."
    - "Empirical CS-yield content of the 95 identity-LD SuSiE fits is preserved in a tracked TSV at .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv with exactly 95 data rows + 1 header row."
    - "DECISIONS.md tail contains a dated DEC-2026-04-25-01 entry naming the locked decision (don't commit; document) with Decision / Alternatives / Why / How to apply sections."
    - "STATE.md L27 deferral text is updated to mark the results_identity_ld/ tracking decision as RESOLVED with a pointer to DEC-2026-04-25-01 and to this quick task's commit."
    - "Reproducibility provenance is intact: re-fire path (scripts/fire_identity_ld_rerun.sh + src/snakemake/scripts/make_identity_ld_refs.R + data/processed/ld_reference_identity/) is unchanged; the directory itself remains on disk for figure scripts that read JSONs at runtime."
  artifacts:
    - path: ".gitignore"
      provides: "results_identity_ld/ exclusion line under the existing # --- Results / logs ... section"
      contains: "results_identity_ld/"
    - path: ".planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv"
      provides: "95-row CS-yield aggregation across the 95 identity-LD SuSiE fits"
      min_lines: 96
    - path: ".planning/DECISIONS.md"
      provides: "DEC-2026-04-25-01 entry locking the tracking decision"
      contains: "DEC-2026-04-25-01"
    - path: ".planning/STATE.md"
      provides: "Updated L27 deferral text marking results_identity_ld/ tracking decision RESOLVED"
      contains: "DEC-2026-04-25-01"
  key_links:
    - from: ".planning/DECISIONS.md"
      to: "scripts/fire_identity_ld_rerun.sh"
      via: "How to apply section names the re-fire driver"
      pattern: "fire_identity_ld_rerun\\.sh"
    - from: ".planning/DECISIONS.md"
      to: "src/snakemake/scripts/make_identity_ld_refs.R"
      via: "How to apply section names the identity-LD payload regenerator"
      pattern: "make_identity_ld_refs\\.R"
    - from: ".planning/DECISIONS.md"
      to: ".planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv"
      via: "How to apply section names the canonical CS-yield record"
      pattern: "IDENTITY-LD-K2D-FIT-SUMMARY\\.tsv"
    - from: ".planning/STATE.md"
      to: ".planning/DECISIONS.md"
      via: "L27 update points to DEC-2026-04-25-01"
      pattern: "DEC-2026-04-25-01"
---

<objective>
Resolve the post-k2d "results_identity_ld/ tracking" deferral logged at STATE.md L27 by formalizing the locked decision: don't commit the 160 MB binary fit tree; document the empirical content via .gitignore exclusion + a small tracked CS-yield summary TSV + a dated DECISIONS.md entry + the STATE.md L27 update.

Purpose: Honor the project convention (.gitignore header: "Results and logs are regeneratable; not committed"), avoid 160 MB of binary fit objects in the repo, and preserve reproducibility through (a) the existing k2d fire artifacts (scripts/fire_identity_ld_rerun.sh + src/snakemake/scripts/make_identity_ld_refs.R + data/processed/ld_reference_identity/), and (b) a canonical 95-row CS-yield summary TSV that captures the empirical content independently of the binary RDS fits.

Output: .gitignore line, .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv (new), .planning/DECISIONS.md DEC-2026-04-25-01 appended, .planning/STATE.md L27 updated. All four files committed in a single commit. Figure scripts (fig3_sh2b3_eur_collapse_forest.R) that read JSONs at runtime continue to work because the on-disk tree is untouched.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.gitignore
@.planning/DECISIONS.md
@.planning/amendments/TRACK-A-FROZEN-NUMBERS.md
@.planning/quick/260424-k2d-route-a-fire-identity-ld-rerun-10-eur-autoso/
@results_identity_ld/fine_mapping/finemap_manifest.tsv
@results_identity_ld/fine_mapping/susie/asthma.EUR.SH2B3_12q24.json

<interfaces>
<!-- Identity-LD SuSiE fit JSON schema (extracted from results_identity_ld/fine_mapping/susie/asthma.EUR.SH2B3_12q24.json). -->
<!-- The summary script in Task 2 aggregates these top-level keys across all 95 JSONs. -->
<!-- All field names below are confirmed present in the sample JSON read during planning. -->

Top-level keys consumed by Task 2 summarizer:
- trait                       (str)   e.g. "asthma"
- ancestry                    (str)   e.g. "EUR"
- region_id                   (str)   e.g. "SH2B3_12q24"
- chrom                       (str)   e.g. "12"        # NB: key is "chrom", not "chr"
- start                       (int)   e.g. 111400000
- end                         (int)   e.g. 112000000
- sumstats                    (str)   e.g. "data/processed/sumstats_harmonized/asthma.EUR.tsv.bgz"
- status                      (str)   controlled vocabulary; observed value "ok"
- ld_overlap                  (int)   e.g. 0
- ld_overlap_fraction         (number) e.g. 0
- credible_sets               (list)  list of CS objects (may be empty); len() = n_CS at default min_abs_corr
- pip                         (list)  per-variant PIP array; sum() = pip_sum_total
- min_abs_corr_sweep          (list)  list of {min_abs_corr, n_CS, cs_sizes, cs_pip_sum} dicts at thresholds [0.1, 0.5, 0.9]

Manifest schema (results_identity_ld/fine_mapping/finemap_manifest.tsv, 8 cols, 96 rows incl. header):
- trait, ancestry, method, region_id, chr, start, end, sumstats_path

Naming convention for JSONs: {trait}.{ancestry}.{region_id}.json
File enumeration: glob "results_identity_ld/fine_mapping/susie/*.json" → expect 95 hits.
</interfaces>

<conventions>
<!-- DECISIONS.md format (from 2026-04-24 DEC-2026-04-24-02 entry, last in file). -->
Format:
## YYYY-MM-DD — DEC-YYYY-MM-DD-NN: <title>

**Decision:** <one-paragraph statement of what was decided>

**Alternatives considered:** (a) ... — rejected/adopted; (b) ... ; (c) ...

**Why:** <rationale paragraph>

**How to apply:** <operational guidance — file paths, commands, downstream consequences>

<!-- Amendment naming (from .planning/amendments/ listing). -->
Pattern: ALL-CAPS-HYPHENATED.{md,tsv}; trait-or-topic identifier first; date suffix optional for one-off snapshots (TRACK-A-FROZEN-NUMBERS.md, SUMSTATS-UPGRADE.tsv, sha256_manifest_m1_frozen.tsv, etc.)
This task's TSV: IDENTITY-LD-K2D-FIT-SUMMARY.tsv (mirrors SUMSTATS-UPGRADE.tsv pattern).

<!-- .gitignore section to extend. -->
Section header (line 78): # --- Results / logs: regeneratable, except legacy symlinks ---
Existing entries: results/* (line 79), logs/, *.log, !results/README.md, !results/legacy, !envs/.gitkeep, tests/toy_3locus/results/
Insert "results_identity_ld/" immediately after the "results/*" line so identity-LD exclusion is visually grouped with the canonical results/ exclusion. The blanket "*.rds" rule (line 105) already catches the RDS half; the new line is needed because JSONs are not caught by any existing rule.

<!-- Project framing rule (from feedback_original_research_framing user memory). -->
Frame the decision as ORIGINAL RESEARCH artifact-management policy. Do NOT use "revision", "cleanup", "fix", "fix-up", "placeholder", "TBD", "for now", "v1", or "simplified" anywhere in the prose.
</conventions>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Formalize results_identity_ld/ exclusion in .gitignore</name>
  <files>.gitignore</files>
  <action>Edit .gitignore to add a single line `results_identity_ld/` immediately after the existing `results/*` line (currently line 79), inside the "# --- Results / logs: regeneratable, except legacy symlinks ---" section. Place it adjacent to `results/*` so the visual grouping documents that identity-LD fit outputs are governed by the same project convention as the canonical `results/` tree. Do NOT modify any other gitignore rule. Do NOT touch the blanket `*.rds` rule (line 105) — it already catches the RDS half of the directory; the new line exists to catch the 95 JSON files that the existing `results/*` rule does not match (because that rule patterns the literal directory name `results/`, not `results_identity_ld/`).

After the edit, verify the rule classifies a representative file from each subtree by running `git check-ignore` on (a) one JSON: `results_identity_ld/fine_mapping/susie/asthma.EUR.SH2B3_12q24.json`, (b) one RDS: any `results_identity_ld/fine_mapping/susie/*.rds` file, and (c) the manifest: `results_identity_ld/fine_mapping/finemap_manifest.tsv`. All three must be reported as ignored. Confirm `git status` no longer shows `results_identity_ld/` as `??`.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && git check-ignore -v results_identity_ld/fine_mapping/susie/asthma.EUR.SH2B3_12q24.json results_identity_ld/fine_mapping/finemap_manifest.tsv && [ -n "$(ls results_identity_ld/fine_mapping/susie/*.rds 2>/dev/null | head -1)" ] && git check-ignore -v "$(ls results_identity_ld/fine_mapping/susie/*.rds | head -1)" && ! git status --porcelain | grep -q '^?? results_identity_ld/'</automated>
  </verify>
  <done>.gitignore contains `results_identity_ld/` line in the Results/logs section; `git check-ignore` confirms all three sample paths (JSON, RDS, manifest TSV) are ignored; `git status` no longer lists `results_identity_ld/` as untracked.</done>
</task>

<task type="auto">
  <name>Task 2: Aggregate 95 identity-LD SuSiE fits into IDENTITY-LD-K2D-FIT-SUMMARY.tsv</name>
  <files>.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv</files>
  <action>Produce the canonical CS-yield summary TSV at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` by aggregating the 95 JSON SuSiE fits at `results_identity_ld/fine_mapping/susie/*.json`. Use a one-shot inline Python invocation (no helper script committed to the repo — output is the TSV only). The decision to embed the script inline rather than commit it follows the locked recommendation: this is a one-shot canonical record, not reusable infrastructure. If a future task needs to regenerate the TSV, the k2d re-fire driver (`scripts/fire_identity_ld_rerun.sh`) reproduces the JSONs and the summarizer logic is short enough to re-derive.

Use `/rs1/researchers/c/ckclinto/miniconda3/bin/python` (verified during planning: `python -c "import json, csv, pathlib; print('stdlib ok')"` → ok). The summarizer uses stdlib only (json, csv, pathlib, glob, statistics) — no pandas, no third-party deps.

TSV schema (header row + 95 data rows = 96 lines total). Columns, in order:
  1. trait                  — from JSON key `trait`
  2. ancestry               — from JSON key `ancestry`
  3. region_id              — from JSON key `region_id`
  4. chr                    — from JSON key `chrom` (note: JSON key is "chrom"; output column is "chr" to match finemap_manifest.tsv convention)
  5. start                  — from JSON key `start`
  6. end                    — from JSON key `end`
  7. status                 — from JSON key `status` (verbatim; expect controlled vocabulary)
  8. n_CS                   — len(JSON.credible_sets)
  9. cs_sizes               — semicolon-joined list of len(cs) for each cs in JSON.credible_sets; empty string if no CS
  10. pip_sum_total         — sum(JSON.pip), formatted to 6 decimal places; "0.000000" if empty
  11. ld_overlap            — from JSON key `ld_overlap`
  12. ld_overlap_fraction   — from JSON key `ld_overlap_fraction`, formatted to 6 decimal places
  13. sumstats_path         — from JSON key `sumstats`

Field separator: TAB. Line terminator: LF. No quoting (the schema has no embedded tabs/newlines in any string field; cs_sizes uses `;` not `\t`).

Sort order: ascending by (trait, ancestry, region_id) so the TSV is deterministic across re-runs.

Sanity gates the summarizer must enforce (raise + exit non-zero on failure):
  (g1) Exactly 95 JSON files matched by glob.
  (g2) Output TSV has exactly 96 lines (header + 95 data rows).
  (g3) `status` field values are confined to a small controlled vocabulary; print the unique set to stderr for the executor to record in the summary. Do NOT hard-fail on unexpected values — print a WARN and continue (the locked schema does not exhaustively enumerate the vocabulary).
  (g4) Cross-check the SH2B3_12q24 EUR n_CS scalars against the orchestrator-verified values: asthma=0, bmi=3, hypertension=10, stroke=10, t2d=2. Hard-fail if any mismatch.

After the TSV is written:
  - Confirm size in the 10–20 KB range (planner-predicted).
  - Print `wc -l` and `head -3` for the executor's summary block.
  - Print the `status` value distribution to confirm vocabulary.
  - Print the per-trait n_CS distribution at SH2B3_12q24 EUR for the gate check.

The TSV must be tracked by git (it lives under `.planning/amendments/` which is not gitignored). Verify with `git status --porcelain .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` showing `??` (new file) before commit.</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && [ -f .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv ] && [ "$(wc -l < .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv)" = "96" ] && head -1 .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv | grep -q '^trait	ancestry	region_id	chr	start	end	status	n_CS	cs_sizes	pip_sum_total	ld_overlap	ld_overlap_fraction	sumstats_path$' && awk -F'\t' 'NR>1 && $3=="SH2B3_12q24" && $2=="EUR" {print $1, $8}' .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv | sort | tr '\n' ';' | grep -q 'asthma 0;bmi 3;hypertension 10;stroke 10;t2d 2;' && git status --porcelain .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv | grep -q '^??'</automated>
  </verify>
  <done>TSV exists at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` with header + 95 data rows; header schema matches the locked column order; SH2B3_12q24 EUR n_CS scalars match the orchestrator-verified values (asthma=0, bmi=3, hypertension=10, stroke=10, t2d=2); file is staged-eligible (untracked, not gitignored).</done>
</task>

<task type="auto">
  <name>Task 3: Append DEC-2026-04-25-01 to DECISIONS.md and update STATE.md L27</name>
  <files>.planning/DECISIONS.md, .planning/STATE.md</files>
  <action>This task is load-bearing for the decision artifact. It commits the locked policy to the project record (DECISIONS.md) and removes the deferral text from STATE.md L27 in the same edit chain so the resolution is atomic with the artifact landing.

Step 3a — DECISIONS.md append. Append a new entry to the tail of `.planning/DECISIONS.md`, mirroring the format of the prior 2026-04-24 entries. Header: `## 2026-04-25 — DEC-2026-04-25-01: results_identity_ld/ tracking — document, don't commit`. Sections:

  **Decision:** State that the 160 MB `results_identity_ld/` tree (95 JSONs + 95 RDS + 1 manifest TSV; produced by the 2026-04-24 k2d re-fire at LSF PID 830748) is excluded from git via `.gitignore` and documented via the canonical CS-yield summary at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`. The on-disk tree remains where figure scripts (`src/R/figures/fig3_sh2b3_eur_collapse_forest.R`) read it at runtime; reproducibility is preserved through the existing k2d re-fire artifacts.

  **Alternatives considered:** (a) commit everything (~160 MB into git — rejected; violates the .gitignore header convention "Results and logs are regeneratable; not committed" and inflates clone size); (b) commit JSONs but not RDS (rejected; partial commit creates inconsistent reconstructibility — half the fit state is on disk, half in git, and figure scripts that load both halves break for any clone that doesn't pull-LFS); (c) git-lfs (rejected; introduces an LFS dependency for a single ad-hoc artifact set when the data is fully reproducible from sumstats + identity matrix in ~1 hour LSF wall, and Track A is solo-author public-data-only with no LFS infrastructure in place); (d) document only — adopted.

  **Why:** Project convention (.gitignore line 9) governs results trees. Reproducibility provenance is intact through three independent paths: (i) re-fire driver `scripts/fire_identity_ld_rerun.sh` (committed at 08beb4c); (ii) identity-LD payload regenerator `src/snakemake/scripts/make_identity_ld_refs.R` operating on `data/processed/ld_reference_identity/`; (iii) the canonical CS-yield summary TSV at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` which captures the empirical content (95 rows × 13 cols) the figure scripts hard-code as `EXPECTED_ID_CS` scalars. The summary TSV is the long-term record: future quick tasks comparing identity-LD vs real-LD CS yields read it instead of binary RDS fits.

  **How to apply:**
    - To regenerate the binary fit tree: `bash scripts/fire_identity_ld_rerun.sh` from project root (LSF serial queue, ~1 hour wall, idempotent under the k2d driver).
    - To regenerate identity-LD LD payloads (if `data/processed/ld_reference_identity/` is lost): re-run `src/snakemake/scripts/make_identity_ld_refs.R` against the 12 region × {EUR, AFR} grid encoded in `config/pipeline_identity_overlay.yaml`.
    - Figure scripts that read the on-disk JSONs (currently `src/R/figures/fig3_sh2b3_eur_collapse_forest.R`) operate on the un-gitignored on-disk tree — no script changes required as long as `results_identity_ld/` exists at project root.
    - For comparative analyses that previously would have read JSONs/RDS, prefer reading the summary TSV at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`.

Step 3b — STATE.md L27 edit. Locate the deferral sentence in STATE.md L27 (read at planning time: "results_identity_ld/ commit + Fig 1A + Fig 3 builders deferred to post-M1-kickoff /gsd-quick (file sets disjoint from M1 pipeline; STATE.md writes serialize against M1 progress writes)."). Update so both halves of the deferral are explicitly resolved with commit pointers:

  - Fig 1A + Fig 3 builders → resolved by quick task `260425-1vy` (commits `105484d` and `f862f55` per orchestrator audit).
  - results_identity_ld/ tracking → resolved by this task's commit (the executor will substitute the actual commit SHA at commit time) plus DEC-2026-04-25-01.

Replacement text (verbatim, single sentence in the same paragraph position; preserve surrounding sentences):
  "**Both halves of the post-k2d deferral are now resolved:** Fig 1A + Fig 3 builders landed via quick task `260425-1vy` (commits `105484d`, `f862f55`); `results_identity_ld/` tracking decision is locked at DEC-2026-04-25-01 (don't commit; document via .gitignore + canonical CS-yield summary at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`)."

Use `Edit` (not `Write`) on STATE.md to preserve the rest of the file. The orchestrator handles the quick-task table row append at step 7 — Task 3 does NOT add a row to the quick-tasks table. Only the L27 paragraph is touched.

Step 3c — Commit. After Tasks 1, 2, and 3 are all complete on disk, stage the four files explicitly (no `git add -A`) and create a single commit:

  Files staged: `.gitignore`, `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`, `.planning/DECISIONS.md`, `.planning/STATE.md`.

  Commit message (HEREDOC):
    docs(quick-260425-ieh): lock results_identity_ld/ tracking decision (DEC-2026-04-25-01)

    Don't commit the 160 MB k2d identity-LD fit tree; document via .gitignore +
    canonical CS-yield summary at .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv
    (95 rows aggregated from results_identity_ld/fine_mapping/susie/*.json).
    Resolves the results_identity_ld/ half of the post-k2d deferral logged at
    STATE.md L27.

    DECISIONS.md DEC-2026-04-25-01 records the locked policy and re-fire path.

  Do NOT use `git commit --amend`. Do NOT skip hooks. Standard non-isolated commit on `main` per project rule (`git.isolation: branch`, but quick-task convention has been single-commits on main throughout the recent log).</action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && grep -q '^## 2026-04-25 — DEC-2026-04-25-01: results_identity_ld/ tracking' .planning/DECISIONS.md && grep -q 'IDENTITY-LD-K2D-FIT-SUMMARY.tsv' .planning/DECISIONS.md && grep -q 'fire_identity_ld_rerun.sh' .planning/DECISIONS.md && grep -q 'make_identity_ld_refs.R' .planning/DECISIONS.md && grep -q 'DEC-2026-04-25-01' .planning/STATE.md && grep -q '260425-1vy' .planning/STATE.md && ! grep -q 'results_identity_ld/ commit + Fig 1A + Fig 3 builders deferred' .planning/STATE.md && git log -1 --pretty=%s | grep -q 'quick-260425-ieh' && git log -1 --pretty=%B | grep -q 'DEC-2026-04-25-01' && git diff HEAD~1 HEAD --name-only | sort | tr '\n' ';' | grep -q '.gitignore;.planning/DECISIONS.md;.planning/STATE.md;.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv;'</automated>
  </verify>
  <done>DECISIONS.md tail contains DEC-2026-04-25-01 entry with all four sections (Decision / Alternatives / Why / How to apply); How-to-apply names both `fire_identity_ld_rerun.sh` and `make_identity_ld_refs.R`. STATE.md L27 deferral text replaced with the resolved-state sentence pointing to DEC-2026-04-25-01 and 260425-1vy. Single commit on main contains all four files (.gitignore, summary TSV, DECISIONS.md, STATE.md). Working tree is clean except for the orchestrator's pending step-7 STATE-row write.</done>
</task>

</tasks>

<verification>
After all three tasks complete:

1. `git status --porcelain` does NOT list `results_identity_ld/` as untracked. The 160 MB tree is gitignored.
2. `wc -l .planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` reports `96` (header + 95 data rows).
3. `git log -1 --stat` shows a single commit touching exactly four files: `.gitignore`, `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv`, `.planning/DECISIONS.md`, `.planning/STATE.md`.
4. `grep -c 'DEC-2026-04-25-01' .planning/DECISIONS.md` >= 1 (the entry header).
5. `grep -c 'DEC-2026-04-25-01' .planning/STATE.md` >= 1 (the L27 cross-reference).
6. The on-disk `results_identity_ld/fine_mapping/susie/asthma.EUR.SH2B3_12q24.json` and the manifest TSV are unchanged (no edits to the fit tree itself; figure scripts that read JSONs at runtime continue to function).
7. The k2d re-fire path is verifiable via `[ -x scripts/fire_identity_ld_rerun.sh ] && [ -f src/snakemake/scripts/make_identity_ld_refs.R ]` (sanity check that the re-fire artifacts referenced in DEC-2026-04-25-01 §How-to-apply still exist on disk).

Cross-check against orchestrator audit: 95 JSONs (orchestrator counted), 95 RDS (caught by blanket `*.rds` rule), 1 manifest TSV (caught by new `results_identity_ld/` rule), 191 files total — all 191 must show as ignored after Task 1. Quick spot-check: `find results_identity_ld -type f | xargs git check-ignore | wc -l` should equal 191.
</verification>

<success_criteria>
- `results_identity_ld/` is fully ignored by git (191/191 files matched by .gitignore).
- `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` is a tracked, deterministic 96-line TSV with the 13-column schema and the locked CS-yield scalars at SH2B3_12q24 EUR (asthma=0, bmi=3, hypertension=10, stroke=10, t2d=2).
- `.planning/DECISIONS.md` tail carries DEC-2026-04-25-01 with all four required sections; the How-to-apply section names the three reproducibility paths (fire driver, identity-LD payload regenerator, summary TSV).
- `.planning/STATE.md` L27 deferral text is replaced with a resolved-state sentence cross-referencing DEC-2026-04-25-01 and quick task `260425-1vy`.
- All four edits land in a single commit on `main` with message header `docs(quick-260425-ieh): lock results_identity_ld/ tracking decision (DEC-2026-04-25-01)`.
- Reproducibility is intact: `scripts/fire_identity_ld_rerun.sh` and `src/snakemake/scripts/make_identity_ld_refs.R` exist on disk and are referenced from DECISIONS.md.
- Figure scripts that read `results_identity_ld/fine_mapping/susie/*.json` at runtime are unaffected (the directory remains on disk; only its git-tracking status changes).
</success_criteria>

<output>
After completion, the orchestrator will append a quick-tasks-table row to `.planning/STATE.md` at step 7. No SUMMARY.md is required for this quick task — the DECISIONS.md DEC-2026-04-25-01 entry IS the load-bearing record. The executor returns the commit SHA so the orchestrator can write it into the STATE row.
</output>
