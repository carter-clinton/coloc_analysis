---
phase: quick-260413-vtk
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/phases/09-replication-in-independent-cohorts/09-01-PLAN.md
  - .planning/phases/09-replication-in-independent-cohorts/09-03-PLAN.md
  - .planning/phases/09-replication-in-independent-cohorts/09-05-PLAN.md
autonomous: true
requirements:
  - BUG-1: Plan 01 references nonexistent src/snakemake/Snakefile; actual Snakefile is at ./Snakefile
  - BUG-2: Plan 03 references nonexistent src/snakemake/scripts/run_susie_rss.R; actual legacy script at src/legacy/region_analysis/scripts/run_susie_rss.R
  - BUG-3: Plan 05 references nonexistent data/processed/ld_reference/1kg_{ancestry}/chr{N}.bed; actual 1000G plink files unpack under data/reference/ldsc/1000G_Phase3_plinkfiles/ via Phase 5 pathway.smk download_ldsc_baseline
must_haves:
  truths:
    - "09-01-PLAN.md no longer references 'src/snakemake/Snakefile' anywhere; all occurrences replaced with 'Snakefile' (project root)"
    - "09-01-PLAN.md include directive is 'include: \"src/snakemake/rules/replication.smk\"' (full path, matching existing Snakefile convention) in ALL occurrences (action step, verify grep, done bullet)"
    - "09-03-PLAN.md @-import and interfaces block no longer invent a helper in a nonexistent file; describe Phase 1's real architecture (legacy runsusie called via shell from src/snakemake/rules/finemap.smk:79 using src/legacy/region_analysis/scripts/run_susie_rss.R)"
    - "09-05-PLAN.md no longer references 'data/processed/ld_reference/1kg_' anywhere; COJO rule input, shell script comment, key_link all use data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.{EUR,AFR}.QC.{chrom}.{bed,bim,fam}"
    - "09-05-PLAN.md Task 2 read_first explicitly documents dependency on Phase 5 pathway.smk rule download_ldsc_baseline (which must run before COJO; no new download rule needed)"
    - "grep -r 'src/snakemake/Snakefile' .planning/phases/09-replication-in-independent-cohorts/ returns 0 matches"
    - "grep -r 'src/snakemake/scripts/run_susie_rss.R' .planning/phases/09-replication-in-independent-cohorts/ returns 0 matches"
    - "grep -r 'data/processed/ld_reference/1kg_' .planning/phases/09-replication-in-independent-cohorts/ returns 0 matches (09-RESEARCH.md line 540 also scrubbed or flagged as stale research snippet)"
  artifacts:
    - path: ".planning/phases/09-replication-in-independent-cohorts/09-01-PLAN.md"
      provides: "Phase 9 Plan 01 with correct Snakefile path (./Snakefile) and full-path include directive"
      contains: "include: \"src/snakemake/rules/replication.smk\""
    - path: ".planning/phases/09-replication-in-independent-cohorts/09-03-PLAN.md"
      provides: "Phase 9 Plan 03 with accurate Phase 1 architecture description (no fake helper)"
      contains: "src/legacy/region_analysis/scripts/run_susie_rss.R"
    - path: ".planning/phases/09-replication-in-independent-cohorts/09-05-PLAN.md"
      provides: "Phase 9 Plan 05 COJO references Phase 5 LDSC baseline download artifacts"
      contains: "data/reference/ldsc/1000G_Phase3_plinkfiles"
  key_links:
    - from: ".planning/phases/09-replication-in-independent-cohorts/09-01-PLAN.md"
      to: "./Snakefile (project root)"
      via: "files_modified, key_links, Task 2 action/verify/done"
      pattern: '^Snakefile$|"Snakefile"'
    - from: ".planning/phases/09-replication-in-independent-cohorts/09-05-PLAN.md"
      to: "src/snakemake/rules/pathway.smk rule download_ldsc_baseline"
      via: "Task 2 read_first + documented prerequisite"
      pattern: "download_ldsc_baseline"
---

<objective>
Quick fix: Three pre-existing-file-reality mismatches in Phase 9 plan documents (09-01, 09-03, 09-05). Orchestrator-level scan caught them before execution.

Purpose: Prevent executors from creating a second, wrong Snakefile at src/snakemake/Snakefile, from looking for a nonexistent helper in Phase 1's new wrapper, and from requiring a nonexistent 1000G LD reference directory that would block COJO. Plan document text edits only — no code changes, no new rules, no config changes.

Output: Three edited plan files. Zero grep hits for the three old (wrong) paths across Phase 9 plans after edits.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/09-replication-in-independent-cohorts/09-01-PLAN.md
@.planning/phases/09-replication-in-independent-cohorts/09-03-PLAN.md
@.planning/phases/09-replication-in-independent-cohorts/09-05-PLAN.md

<ground_truth>
Verified by `ls` and `grep` at plan time (2026-04-13):

1. Top-level Snakefile location: `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/Snakefile` — NOT `src/snakemake/Snakefile` (that path does not exist).

2. Existing `^include:` directives in the real Snakefile use full paths:
   ```
   include: "src/snakemake/rules/sumstats.smk"
   include: "src/snakemake/rules/regions.smk"
   include: "src/snakemake/rules/qc.smk"
   include: "src/snakemake/rules/multitrait.smk"
   include: "src/snakemake/rules/pgs.smk"
   include: "src/snakemake/rules/mr.smk"
   include: "src/snakemake/rules/qtl_download.smk"
   include: "src/snakemake/rules/qtl_coloc.smk"
   include: "src/snakemake/rules/negative_controls.smk"
   include: "src/snakemake/rules/pathway.smk"
   ```
   So the correct Phase 9 include is: `include: "src/snakemake/rules/replication.smk"`.

3. `src/snakemake/scripts/run_susie_rss.R` DOES NOT EXIST. What exists:
   - `src/legacy/region_analysis/scripts/run_susie_rss.R` (legacy; finemap.smk shells to this at line 79)
   - `src/snakemake/scripts/run_coloc_susie.R` (Phase 1's new wrapper — different script, different role)

4. `src/snakemake/rules/finemap.smk:63` declares `script_dep="src/legacy/region_analysis/scripts/run_susie_rss.R"` and line 79 invokes `Rscript src/legacy/region_analysis/scripts/run_susie_rss.R ...`. That IS the real "reuse runsusie pattern" source Plan 03 should reference.

5. `data/processed/ld_reference/1kg_{ancestry}/chr{N}.bed` DOES NOT EXIST and no rule produces it. What DOES get produced:
   - `src/snakemake/rules/pathway.smk` rule `download_ldsc_baseline` (line 180) downloads `1000G_Phase3_plinkfiles.tgz` from the Broad requester-pays bucket and unpacks to `data/reference/ldsc/1000G_Phase3_plinkfiles/` (confirmed via `PATHWAY_CFG.get("ldsc_plink", "data/reference/ldsc/1000G_Phase3_plinkfiles")` at lines 626, 667).
   - LDSC plinkfile archive naming convention: `1000G.{EUR|AFR}.QC.{chrom}.{bed,bim,fam}` (Broad resource naming).

6. `09-RESEARCH.md:540` also contains a stale code snippet `gcta --bfile data/processed/ld_reference/1kg_EUR/chr${CHR} ...`. Task 3 scrubs or annotates this as stale.
</ground_truth>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Fix BUG-1 — correct Snakefile path + include directive in 09-01-PLAN.md</name>
  <files>.planning/phases/09-replication-in-independent-cohorts/09-01-PLAN.md</files>
  <read_first>
    - .planning/phases/09-replication-in-independent-cohorts/09-01-PLAN.md (full file; 7 occurrences to patch per <ground_truth> point 1-2)
  </read_first>
  <action>
    Apply SEVEN edits to `.planning/phases/09-replication-in-independent-cohorts/09-01-PLAN.md`. Use the `Edit` tool with exact string matches. All edits change `src/snakemake/Snakefile` → `Snakefile` (project root) and fix the include directive to use the full path `src/snakemake/rules/replication.smk` matching the convention already in the real Snakefile.

    **Edit 1** — frontmatter `files_modified` entry (line 12):
    FROM: `  - src/snakemake/Snakefile`
    TO:   `  - Snakefile`

    **Edit 2** — frontmatter `key_links` from (line 54):
    FROM: `    - from: "src/snakemake/Snakefile"`
    TO:   `    - from: "Snakefile"`

    **Edit 3** — Task 2 `<files>` attribute (line 300):
    FROM: `  <files>envs/gcta.yml, envs/r_coloc.yml, src/snakemake/rules/replication.smk, src/snakemake/Snakefile</files>`
    TO:   `  <files>envs/gcta.yml, envs/r_coloc.yml, src/snakemake/rules/replication.smk, Snakefile</files>`

    **Edit 4** — Task 2 `<read_first>` bullet (line 304):
    FROM: `    - src/snakemake/Snakefile (top-level; pattern for \`include:\` directives)`
    TO:   `    - Snakefile (project root top-level; pattern for \`include:\` directives — uses full paths like \`include: "src/snakemake/rules/pathway.smk"\`)`

    **Edit 5** — Task 2 Step 4 action paragraph (line 481):
    FROM: `    Step 4 — Edit \`src/snakemake/Snakefile\` to ADD \`include: "rules/replication.smk"\` after the existing rule module includes (append; do not reorder existing includes). Add comment: \`# Phase 9 — replication cohorts\`.`
    TO:   `    Step 4 — Edit \`Snakefile\` (project root) to ADD \`include: "src/snakemake/rules/replication.smk"\` after the existing rule module includes (append; do not reorder existing includes). Note: the real Snakefile uses full paths for includes (e.g., \`include: "src/snakemake/rules/pathway.smk"\`) — match that convention. Add comment: \`# Phase 9 — replication cohorts\`.`

    **Edit 6** — Task 2 `<automated>` grep in verify (line 486):
    FROM (substring to replace inside the long one-line command):
      `grep -q 'include: "rules/replication.smk"' src/snakemake/Snakefile`
    TO:
      `grep -q 'include: "src/snakemake/rules/replication.smk"' Snakefile`
    (Keep the rest of the line identical — all other grep clauses and `&&` chain untouched.)

    **Edit 7** — Task 2 `<done>` bullet (line 495):
    FROM: `    - Snakefile includes rules/replication.smk`
    TO:   `    - Snakefile (project root) includes "src/snakemake/rules/replication.smk" (full path, matching existing convention)`

    Do NOT touch any other lines in 09-01-PLAN.md. Do NOT add new sections or bullets.
  </action>
  <verify>
    <automated>PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH" bash -c 'set -euo pipefail; F=.planning/phases/09-replication-in-independent-cohorts/09-01-PLAN.md; grep -q "src/snakemake/Snakefile" "$F" && { echo "FAIL: still contains src/snakemake/Snakefile"; exit 1; }; grep -q "include: \"rules/replication.smk\"" "$F" && { echo "FAIL: still contains short-path include"; exit 1; }; grep -q "include: \"src/snakemake/rules/replication.smk\"" "$F" || { echo "FAIL: missing corrected full-path include"; exit 1; }; grep -c "\"Snakefile\"\\|- Snakefile\\| Snakefile " "$F" | awk "{if (\$1 >= 3) exit 0; else {print \"FAIL: expected >=3 Snakefile refs, got \" \$1; exit 1}}"; echo OK'</automated>
  </verify>
  <done>
    - Zero occurrences of literal `src/snakemake/Snakefile` in 09-01-PLAN.md
    - Zero occurrences of short-form `include: "rules/replication.smk"` in 09-01-PLAN.md (action, verify grep, done bullet all use full path)
    - At least one occurrence of `include: "src/snakemake/rules/replication.smk"` in the action/verify/done
    - `files_modified` lists `Snakefile` (not `src/snakemake/Snakefile`)
    - `key_links` `from` field is `"Snakefile"` (not `"src/snakemake/Snakefile"`)
  </done>
</task>

<task type="auto">
  <name>Task 2: Fix BUG-2 + BUG-3 — correct run_susie_rss.R reference in 09-03; correct LD reference paths in 09-05</name>
  <files>.planning/phases/09-replication-in-independent-cohorts/09-03-PLAN.md, .planning/phases/09-replication-in-independent-cohorts/09-05-PLAN.md, .planning/phases/09-replication-in-independent-cohorts/09-RESEARCH.md</files>
  <read_first>
    - .planning/phases/09-replication-in-independent-cohorts/09-03-PLAN.md lines 66-95 (context + interfaces block) and line 353 (read_first bullet)
    - .planning/phases/09-replication-in-independent-cohorts/09-05-PLAN.md lines 50-62 (key_links), line 111 (Task 2 read_first), line 158 (shell script comment), line 244 (rule input path)
    - .planning/phases/09-replication-in-independent-cohorts/09-RESEARCH.md line 540 (stale COJO snippet)
  </read_first>
  <action>
    **Part A — BUG-2 fixes in 09-03-PLAN.md**

    **Edit A1** — `<context>` `@` import (line 71):
    FROM: `@src/snakemake/scripts/run_susie_rss.R`
    TO:   `@src/legacy/region_analysis/scripts/run_susie_rss.R`

    **Edit A2** — `<interfaces>` block (lines 86-90). Replace the entire sub-block:
    FROM (exact):
    ```
    From Phase 1 `src/snakemake/scripts/run_susie_rss.R` (reused pattern):
    ```r
    # Pattern: read policy, read region sumstats, load LD, call runsusie, saveRDS
    source_susie_policy <- function(policy_path) { yaml::read_yaml(policy_path) }
    ```
    ```
    TO (exact):
    ```
    From Phase 1 runsusie invocation (real architecture — verified 2026-04-13):
    Legacy `src/legacy/region_analysis/scripts/run_susie_rss.R` is the runsusie entry point; the new Snakemake rule `src/snakemake/rules/finemap.smk` (rule `fit_susie`, line 79) shells out to it:
    ```
    Rscript src/legacy/region_analysis/scripts/run_susie_rss.R \
      <region_sumstats> <ld_matrix> <policy_yaml> <out.fit.rds>
    ```
    Pattern to reuse for Phase 9: read `config/susie_policy.yaml`, read region sumstats, load LD matrix, call `coloc::runsusie()` with ladder retries, apply `annotate_susie()`, `saveRDS()`. There is NO helper function `source_susie_policy()` — plan pre-spec was factually wrong. Inline `yaml::read_yaml(policy_path)` where needed.
    ```

    **Edit A3** — read_first bullet in Task 2 (line 353):
    FROM: `    - src/snakemake/scripts/run_susie_rss.R (Phase 1 — reuse runsusie pattern, retry ladder, policy loader)`
    TO:   `    - src/legacy/region_analysis/scripts/run_susie_rss.R (Phase 1 legacy — real runsusie entry point; retry ladder + policy loading live inline, no helper function)`
    (If the exact-match line number has drifted slightly, search for the unique substring `src/snakemake/scripts/run_susie_rss.R (Phase 1 — reuse` and replace it once.)

    **Part B — BUG-3 fixes in 09-05-PLAN.md**

    Target path pattern: replace `data/processed/ld_reference/1kg_{ancestry}/chr{N}.bed` and `data/processed/ld_reference/1kg_eur/chr10` style strings with the real post-download path `data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.{ancestry_code}.QC.{chrom}.bed` where `{ancestry_code}` ∈ {EUR, AFR}. When a wildcard for {chrom} is needed, use `{chrom}` (matching existing Phase 5 convention).

    **Edit B1** — frontmatter `key_links` entry (lines 54-57 block):
    FROM (exact block):
    ```
        - from: "src/snakemake/scripts/run_cojo.sh"
          to: "data/processed/ld_reference/1kg_{ancestry}/chr{N}.bed"
          via: "--bfile argument"
          pattern: "--bfile"
    ```
    TO (exact block):
    ```
        - from: "src/snakemake/scripts/run_cojo.sh"
          to: "data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.{EUR|AFR}.QC.{chrom}.bed"
          via: "--bfile argument (depends on Phase 5 pathway.smk rule download_ldsc_baseline)"
          pattern: "--bfile"
    ```

    **Edit B2** — Task 2 `<read_first>` (line 111):
    FROM: `    - data/processed/ld_reference/ (check for existing 1000G EUR/AFR PLINK files; build if needed)`
    TO:   `    - data/reference/ldsc/1000G_Phase3_plinkfiles/ (1000G Phase 3 PLINK files; produced by Phase 5 \`src/snakemake/rules/pathway.smk\` rule \`download_ldsc_baseline\` which unpacks the Broad LDSC archive — filenames follow \`1000G.{EUR|AFR}.QC.{chrom}.{bed,bim,fam}\`). DO NOT add a new download rule; declare dependency on existing \`download_ldsc_baseline\` flag.`

    **Edit B3** — shell script comment example (line 158):
    FROM: `    PLINK_PREFIX="$2"   # e.g., data/processed/ld_reference/1kg_eur/chr10`
    TO:   `    PLINK_PREFIX="$2"   # e.g., data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.EUR.QC.10`

    **Edit B4** — Snakemake rule input in Task 1 action (line 244, within the `rule run_cojo_slct:` block):
    FROM: `            plink_bed = "data/processed/ld_reference/1kg_{ancestry}/chr{chrom}.bed",`
    TO:   `            plink_bed = "data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.{ancestry}.QC.{chrom}.bed",`
    (Note: this rule must also declare a dependency on the `download_ldsc_baseline` flag file. Add a sibling input line AFTER `plink_bed`:)
    ```
                ldsc_flag = "data/reference/ldsc/.download_ldsc_baseline.done",
    ```
    (Match existing Phase 5 flag-file pattern per STATE.md quick RO7 note. If flag filename differs in pathway.smk, the executor MUST verify the exact flag path at execute time and use that.)

    **Edit B5** — If the wildcard `{ancestry}` elsewhere in Plan 05 uses lowercase `eur/afr`, add a constraint note to Task 1 action (append paragraph BEFORE Step 5 — before the `tests/phase9/test_cojo_sensitivity.py` section):
    ```
    Wildcard note: `{ancestry}` in the `plink_bed` path MUST be upper-case (EUR or AFR) matching the Broad LDSC `1000G.{EUR|AFR}.QC.{chrom}` naming. Use a Snakemake `wildcard_constraints: ancestry="EUR|AFR"` block or upper-case the ancestry in the manifest dispatch lookup. Do NOT invent a new download rule — `src/snakemake/rules/pathway.smk` rule `download_ldsc_baseline` already produces these files.
    ```

    **Part C — 09-RESEARCH.md stale snippet (line 540)**

    **Edit C1** — line 540 snippet context (stale COJO example):
    FROM (exact): `gcta --bfile data/processed/ld_reference/1kg_EUR/chr${CHR} \`
    TO (exact):   `gcta --bfile data/reference/ldsc/1000G_Phase3_plinkfiles/1000G.EUR.QC.${CHR} \`

    Only this one line in 09-RESEARCH.md needs to change. Research is a historical artifact — we do not rewrite it broadly, but this specific path would be copy-pasted into code by executors reading the research doc, so it gets the same fix.

    Do NOT touch any other lines across the three files. Do NOT add or remove sections, tasks, or frontmatter fields.
  </action>
  <verify>
    <automated>PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH" bash -c 'set -euo pipefail; D=.planning/phases/09-replication-in-independent-cohorts; grep -rn "src/snakemake/scripts/run_susie_rss.R" "$D" && { echo "FAIL: BUG-2 residual"; exit 1; } || true; ! grep -rn "src/snakemake/scripts/run_susie_rss.R" "$D" >/dev/null; grep -rn "data/processed/ld_reference/1kg_" "$D" && { echo "FAIL: BUG-3 residual"; exit 1; } || true; ! grep -rn "data/processed/ld_reference/1kg_" "$D" >/dev/null; grep -q "src/legacy/region_analysis/scripts/run_susie_rss.R" "$D/09-03-PLAN.md" || { echo "FAIL: 09-03 missing legacy path"; exit 1; }; grep -q "1000G_Phase3_plinkfiles" "$D/09-05-PLAN.md" || { echo "FAIL: 09-05 missing LDSC path"; exit 1; }; grep -q "download_ldsc_baseline" "$D/09-05-PLAN.md" || { echo "FAIL: 09-05 missing Phase 5 dep"; exit 1; }; grep -q "1000G.EUR.QC" "$D/09-RESEARCH.md" || { echo "FAIL: 09-RESEARCH missing scrub"; exit 1; }; echo OK'</automated>
  </verify>
  <done>
    - `grep -r 'src/snakemake/scripts/run_susie_rss.R' .planning/phases/09-replication-in-independent-cohorts/` returns zero matches
    - `grep -r 'data/processed/ld_reference/1kg_' .planning/phases/09-replication-in-independent-cohorts/` returns zero matches
    - 09-03-PLAN.md interfaces block describes Phase 1's real architecture (shell invocation from finemap.smk to legacy script; no invented `source_susie_policy` helper)
    - 09-05-PLAN.md Task 2 read_first explicitly declares dependency on Phase 5 pathway.smk rule `download_ldsc_baseline` and states NO new download rule to be added
    - 09-05-PLAN.md rule `run_cojo_slct` input block includes both `plink_bed` (new path) AND `ldsc_flag` dependency
    - 09-RESEARCH.md line ~540 uses real LDSC path in the `gcta --bfile` snippet
  </done>
</task>

</tasks>

<verification>
Phase-level: After both tasks, run the unified grep sweep:

```bash
PATH="/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH" bash -c '
  D=.planning/phases/09-replication-in-independent-cohorts
  echo "=== BUG-1 residual ==="; grep -rn "src/snakemake/Snakefile" "$D" || echo "clean"
  echo "=== BUG-2 residual ==="; grep -rn "src/snakemake/scripts/run_susie_rss.R" "$D" || echo "clean"
  echo "=== BUG-3 residual ==="; grep -rn "data/processed/ld_reference/1kg_" "$D" || echo "clean"
  echo "=== Short-form include residual ==="; grep -rn "include: \"rules/replication.smk\"" "$D" || echo "clean"
'
```

All four sections must print `clean`. Any residual hit fails verification.
</verification>

<success_criteria>
- All three bug fixes applied (BUG-1 in 09-01, BUG-2 in 09-03, BUG-3 in 09-05 + 09-RESEARCH line 540)
- Zero grep hits across Phase 9 plans for: `src/snakemake/Snakefile`, `src/snakemake/scripts/run_susie_rss.R`, `data/processed/ld_reference/1kg_`, `include: "rules/replication.smk"` (short form)
- At least one grep hit for each corrected path: `Snakefile` (standalone), `src/legacy/region_analysis/scripts/run_susie_rss.R`, `data/reference/ldsc/1000G_Phase3_plinkfiles`, `include: "src/snakemake/rules/replication.smk"`, `download_ldsc_baseline`
- 09-05 rule `run_cojo_slct` depends on Phase 5 `download_ldsc_baseline` flag file (no new download rule invented)
- No code changes, no new rules, no config changes — plan documents only
</success_criteria>

<output>
After completion, create `.planning/quick/260413-vtk-fix-3-file-path-bugs-in-phase-9-plans/260413-vtk-SUMMARY.md` documenting:
1. Which lines changed in each of the 4 files (09-01-PLAN.md, 09-03-PLAN.md, 09-05-PLAN.md, 09-RESEARCH.md)
2. Verification grep output showing zero residual hits
3. Git commit hash
</output>
