---
phase: quick-260414-uqf
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/snakemake/rules/pathway.smk
  - envs/gprofiler.yml
autonomous: false
requirements:
  - SCOUT-ISSUE-8  # msigdbr 26 API drift (from .planning/quick/260414-bmi-magma-scout/SCOUT-FINDINGS.md)

must_haves:
  truths:
    - "download_msigdb rule uses msigdbr ≥10.0 collection=/subcollection= API (no deprecated category=/subcategory= calls remain)"
    - "KEGG path writes KEGG_LEGACY (186 gene sets, original KEGG) to c2.cp.kegg.gmt — filename unchanged for downstream consumer compatibility"
    - "Hallmark call uses collection=\"H\" with NO subcollection argument (Hallmark has no subcollection in msigdbr 26)"
    - "envs/gprofiler.yml relaxes r-base and r-msigdbr pins to accommodate msigdbr 26 against R ≥4.4 builds; documents why (comment) without touching other pins"
    - "snakemake all_pathway --dry-run returns 575 jobs (no DAG regression) with updated spec"
    - "Live execution of download_msigdb produces c2.cp.kegg.gmt, c2.cp.reactome.gmt, c5.go.bp.gmt, h.all.gmt with real content (first-line sanity check: KEGG file starts with KEGG_*)"
    - ".snakemake/conda/ contents untouched (existing d905eea16… prefix already satisfies relaxed spec)"
  artifacts:
    - path: "src/snakemake/rules/pathway.smk"
      provides: "download_msigdb rule body updated to msigdbr 26 API + KEGG_LEGACY subcollection"
      contains: "collection=\"C2\", subcollection=\"CP:KEGG_LEGACY\""
    - path: "envs/gprofiler.yml"
      provides: "Relaxed r-base + r-msigdbr pins with inline justification comment"
      contains: "r-msigdbr>=10.0"
    - path: "data/reference/msigdb/c2.cp.kegg.gmt"
      provides: "KEGG_LEGACY gene sets GMT (186 sets expected)"
      produced_by: "snakemake download_msigdb --use-conda --cores 1"
    - path: "data/reference/msigdb/c2.cp.reactome.gmt"
      provides: "Reactome gene sets GMT"
      produced_by: "snakemake download_msigdb --use-conda --cores 1"
    - path: "data/reference/msigdb/c5.go.bp.gmt"
      provides: "GO Biological Process gene sets GMT"
      produced_by: "snakemake download_msigdb --use-conda --cores 1"
    - path: "data/reference/msigdb/h.all.gmt"
      provides: "Hallmark gene sets GMT"
      produced_by: "snakemake download_msigdb --use-conda --cores 1"
    - path: ".planning/quick/260414-uqf-update-download-msigdb-rule-for-msigdbr-/260414-uqf-SUMMARY.md"
      provides: "Quick task summary with verbatim verification output for all 4 gates"
  key_links:
    - from: "src/snakemake/rules/pathway.smk download_msigdb"
      to: "envs/gprofiler.yml (r-msigdbr>=10.0)"
      via: "conda: GPROFILER_ENV directive"
      pattern: "msigdbr.*collection="
    - from: "src/snakemake/rules/pathway.smk download_msigdb"
      to: "write_gmt R helper (gs_name / gene_symbol columns)"
      via: "data frame column references inside Rscript heredoc"
      pattern: "df\\$gs_name|df\\$gene_symbol"
---

<objective>
Update the `download_msigdb` Snakemake rule to use the msigdbr ≥10.0 API
(`collection=`/`subcollection=`) and pick `CP:KEGG_LEGACY` for backward
compatibility with prior Phase 5 development assumptions. Relax the two pins in
`envs/gprofiler.yml` that are incompatible with fresh mamba solves against
R ≥4.4 builds. Verify via 4 gates (dry-run DAG, rule-scoped dry-run, live
execution, file-content sanity check).

Purpose: Unblock Phase 5 scout v8 — this is SCOUT-FINDINGS issue #8 (the only
remaining blocker in download_msigdb). Downstream g:Profiler + enrichment
consumers expect the 4 GMT filenames unchanged.

Output:
  - `src/snakemake/rules/pathway.smk` with msigdbr 26 API + KEGG_LEGACY
  - `envs/gprofiler.yml` with relaxed r-base / r-msigdbr pins + justification comment
  - 4 GMT files under `data/reference/msigdb/` produced by live execution
  - `260414-uqf-SUMMARY.md` with verbatim 4-gate verification output
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/quick/260414-bmi-magma-scout/SCOUT-FINDINGS.md
@.planning/STATE.md
@./CLAUDE.md
@src/snakemake/rules/pathway.smk
@envs/gprofiler.yml

<interfaces>
<!-- Relevant contracts extracted from codebase so the executor does not need to hunt. -->

Current rule location: src/snakemake/rules/pathway.smk lines ~312-371.

Current rule body (to be replaced):
```python
rule download_msigdb:
    """Download MSigDB gene sets via msigdbr R package."""
    output:
        kegg=os.path.join(PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"), "c2.cp.kegg.gmt"),
        reactome=os.path.join(PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"), "c2.cp.reactome.gmt"),
        gobp=os.path.join(PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"), "c5.go.bp.gmt"),
        hallmark=os.path.join(PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"), "h.all.gmt"),
    params:
        outdir=PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"),
    conda:
        GPROFILER_ENV
    shell:
        r"""
        mkdir -p {params.outdir}
        Rscript -e '
        library(msigdbr)

        write_gmt <- function(df, path) {{
            sets <- split(df, df$gs_name)
            con <- file(path, "w")
            for (nm in names(sets)) {{
                genes <- unique(sets[[nm]]$gene_symbol)
                cat(nm, "msigdb", paste(genes, collapse="\t"), "\n",
                    sep="\t", file=con)
            }}
            close(con)
        }}

        kegg <- msigdbr(species="Homo sapiens", category="C2", subcategory="CP:KEGG")
        write_gmt(kegg, "{params.outdir}/c2.cp.kegg.gmt")

        reactome <- msigdbr(species="Homo sapiens", category="C2", subcategory="CP:REACTOME")
        write_gmt(reactome, "{params.outdir}/c2.cp.reactome.gmt")

        gobp <- msigdbr(species="Homo sapiens", category="C5", subcategory="GO:BP")
        write_gmt(gobp, "{params.outdir}/c5.go.bp.gmt")

        hallmark <- msigdbr(species="Homo sapiens", category="H")
        write_gmt(hallmark, "{params.outdir}/h.all.gmt")

        cat("MSigDB download complete\\n")
        '
        """
```

Current envs/gprofiler.yml (lines 1-18):
```yaml
# envs/gprofiler.yml -- R environment for g:Profiler enrichment analysis (Phase 5)
# Used by: gprofiler_enrichment rule in pathway.smk.
# g:Profiler2 R package provides programmatic access to the g:Profiler web
# service for functional enrichment analysis (Kolberg et al. 2020).
name: gprofiler_r
channels:
  - conda-forge
  - bioconda
dependencies:
  # REQ-9: exact version pins for reproducibility. Versions chosen to match
  # the conda-forge/bioconda snapshot at the time of Phase 5 initial build
  # (Apr 2026). Bump via a deliberate decision, not drift.
  - r-base=4.3.1
  - r-gprofiler2=0.2.2
  - r-dplyr=1.1.4
  - r-readr=2.1.5
  - r-yaml=2.3.8
  - r-msigdbr=7.5.1
```

msigdbr 26 API semantics (from issue #8 context):
- `msigdbr(species="Homo sapiens", collection="C2", subcollection="CP:KEGG_LEGACY")` → 186 sets
- `msigdbr(species="Homo sapiens", collection="C2", subcollection="CP:REACTOME")` → Reactome
- `msigdbr(species="Homo sapiens", collection="C5", subcollection="GO:BP")` → GO BP
- `msigdbr(species="Homo sapiens", collection="H")` → Hallmark (NO subcollection arg)
- Column names `gs_name` and `gene_symbol` are stable across msigdbr 7.x → 26.x per msigdbr release notes (verify live in Task 1).

Live conda env already satisfies relaxed spec:
- Path: `.snakemake/conda/d905eea16d857e4c4b9da644fbd9aae7_/`
- R 4.5.3 + msigdbr 26.1.0 already installed (auto-upgraded by mamba during `260414-tmq`)
- DO NOT touch this prefix. snakemake will treat the relaxed spec as satisfied.

DAG expectation: `snakemake all_pathway --dry-run` currently returns 575 jobs
(per SCOUT-FINDINGS wall-time accounting and the 579-job DAG context from
STATE.md last activity — the 575 figure is the pathway-only subset; exact value
recorded in gate (a)). The edits here must not change job count.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Update download_msigdb rule body + relax gprofiler.yml pins</name>
  <files>src/snakemake/rules/pathway.smk, envs/gprofiler.yml</files>

  <action>
  (A) Edit `src/snakemake/rules/pathway.smk` — rule `download_msigdb` shell block (lines ~336-371). Change the four `msigdbr(...)` calls from the deprecated `category=`/`subcategory=` form to the msigdbr ≥10.0 `collection=`/`subcollection=` form, and pick KEGG_LEGACY for KEGG:

  - KEGG:      `msigdbr(species="Homo sapiens", collection="C2", subcollection="CP:KEGG_LEGACY")`
  - Reactome:  `msigdbr(species="Homo sapiens", collection="C2", subcollection="CP:REACTOME")`
  - GO BP:     `msigdbr(species="Homo sapiens", collection="C5", subcollection="GO:BP")`
  - Hallmark:  `msigdbr(species="Homo sapiens", collection="H")`  # NO subcollection arg

  Preserve everything else verbatim:
  - Output file paths (c2.cp.kegg.gmt, c2.cp.reactome.gmt, c5.go.bp.gmt, h.all.gmt) — downstream consumers depend on these exact filenames.
  - The `write_gmt` R helper (uses `df$gs_name` and `df$gene_symbol`). These column names are stable across msigdbr 7.x → 26.x per msigdbr release notes; the Task 2 live gate will catch any regression if they were in fact renamed.
  - The `conda: GPROFILER_ENV` directive and params block.
  - The `mkdir -p {params.outdir}` and closing `cat("MSigDB download complete\\n")`.

  Add a brief inline comment above the four msigdbr calls noting the API change:
  `# msigdbr >=10.0 API: collection=/subcollection= (was category=/subcategory=); KEGG_LEGACY preserves Phase 5 dev assumptions (186 sets, original KEGG).`

  (B) Edit `envs/gprofiler.yml` — relax the two pins that are incompatible with msigdbr 26 against R ≥4.4 conda-forge builds:

  - `r-base=4.3.1` → `r-base>=4.3`
  - `r-msigdbr=7.5.1` → `r-msigdbr>=10.0`

  Leave all other pins (r-gprofiler2=0.2.2, r-dplyr=1.1.4, r-readr=2.1.5, r-yaml=2.3.8) unchanged.

  Preserve the existing REQ-9 comment block, and ADD an adjacent comment immediately above the two relaxed pins (inline with the REQ-9 paragraph so the audit trail stays together) documenting why these two are deliberately relaxed. Suggested wording:

  ```yaml
  # NOTE (quick 260414-uqf): r-base and r-msigdbr are deliberately relaxed from
  # REQ-9 strict pins. Rationale: r-msigdbr 7.x is only available against
  # conda-forge r42 builds; mamba solvers upgrade to R ≥4.4 + msigdbr ≥10.0
  # anyway, and the deprecated category=/subcategory= API raises
  # "Unknown subcollection" at runtime. Downstream consumers key on output
  # GMT filenames only (c2.cp.kegg.gmt etc.), so a floor constraint is
  # sufficient for reproducibility here. See
  # .planning/quick/260414-bmi-magma-scout/SCOUT-FINDINGS.md issue #8.
  ```

  (C) Do NOT touch any other rule, any other env file, any file under `.snakemake/conda/`, or any symlink. Do NOT change the magma rule chain. Do NOT change r-gprofiler2 / r-dplyr / r-readr / r-yaml pins.
  </action>

  <verify>
    <automated>
    # Sanity-check the rule body and yml edits landed correctly.
    cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis && \
      grep -n 'CP:KEGG_LEGACY\|collection="C2"\|collection="C5"\|collection="H"' src/snakemake/rules/pathway.smk | head -20 && \
      ! grep -n 'subcategory="CP:KEGG"\|category="C2", subcategory' src/snakemake/rules/pathway.smk && \
      grep -n 'r-msigdbr>=10.0\|r-base>=4.3' envs/gprofiler.yml && \
      ! grep -n 'r-msigdbr=7.5.1\|r-base=4.3.1' envs/gprofiler.yml
    </automated>
  </verify>

  <done>
  - `pathway.smk` download_msigdb rule contains exactly 4 msigdbr calls, all using `collection=`/`subcollection=` (or bare `collection=` for Hallmark); no `category=`/`subcategory=` references remain in this rule.
  - KEGG call uses `subcollection="CP:KEGG_LEGACY"`.
  - Output filenames unchanged (c2.cp.kegg.gmt, c2.cp.reactome.gmt, c5.go.bp.gmt, h.all.gmt).
  - `envs/gprofiler.yml` has `r-base>=4.3` and `r-msigdbr>=10.0` in place of the old strict pins; all other dependency pins unchanged.
  - A justification comment block is present in `envs/gprofiler.yml` referencing the quick ID + SCOUT-FINDINGS issue #8.
  - No other files modified.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: 4-gate verification (dry-run DAG + rule dry-run + live execution + content sanity)</name>
  <files>.planning/quick/260414-uqf-update-download-msigdb-rule-for-msigdbr-/260414-uqf-SUMMARY.md</files>

  <what-built>
  Task 1 updated the download_msigdb rule body to use the msigdbr ≥10.0 API
  with KEGG_LEGACY, and relaxed two pins in envs/gprofiler.yml. This task runs
  the 4 verification gates against real conda envs and real MSigDB data,
  captures verbatim output, and writes it to the quick-task SUMMARY.md.
  </what-built>

  <action>
  Run all 4 gates below from the project root. Capture verbatim stdout/stderr
  of each into variables (or temp files) so they can be embedded in SUMMARY.md.
  Use the pinned snakemake binary at
  `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` (Python 3.11
  compatible — never invoke snakemake from miniconda3 base per MEMORY.md).

  Prepend miniconda3/bin to PATH for any gsd-tools calls.

  **Gate (a) — Full DAG dry-run (no regression):**
  ```
  /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run 2>&1 | tail -40
  ```
  PASS criterion: the job-count summary line near the tail shows a non-zero
  total; the value reported here is the post-edit baseline. Expected ≈575 jobs
  per the constraints block; if it differs, record the actual value in
  SUMMARY.md and confirm no new rule fired (diff against the pre-edit baseline
  if needed). Any failure (missing input, syntax error, MissingInputException)
  is a hard FAIL.

  **Gate (b) — Rule-scoped dry-run with conda:**
  ```
  /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
    data/reference/msigdb/c2.cp.kegg.gmt --dry-run --use-conda 2>&1 | tail -20
  ```
  PASS criterion: resolves cleanly; snakemake reports `download_msigdb` as the
  rule to run; shows the 4 outputs; env hash resolves to the existing
  `.snakemake/conda/d905eea1…` prefix (or equivalent) — NOT a new hash that
  would trigger env re-creation. If snakemake prints "Creating conda
  environment" that is a FAIL signal (means the relaxed spec hashed to a new
  prefix).

  **Gate (c) — Live execution:**
  ```
  /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake \
    data/reference/msigdb/c2.cp.kegg.gmt --use-conda --cores 1 2>&1 | tail -60
  ```
  Expected wall time: ~1-3 min. PASS criterion: all 4 output files produced:
  ```
  ls -la data/reference/msigdb/{c2.cp.kegg.gmt,c2.cp.reactome.gmt,c5.go.bp.gmt,h.all.gmt}
  ```
  All 4 files exist, non-zero size, mtime within the last few minutes.

  **Gate (d) — Content sanity (per constraint — one full run produces all 4; spot-check each):**
  ```
  head -2 data/reference/msigdb/c2.cp.kegg.gmt
  head -2 data/reference/msigdb/c2.cp.reactome.gmt
  head -2 data/reference/msigdb/c5.go.bp.gmt
  head -2 data/reference/msigdb/h.all.gmt
  wc -l data/reference/msigdb/c2.cp.kegg.gmt
  ```
  PASS criteria:
  - c2.cp.kegg.gmt first line starts with `KEGG_` (KEGG_LEGACY set-name prefix)
  - c2.cp.reactome.gmt first line starts with `REACTOME_`
  - c5.go.bp.gmt first line starts with `GOBP_` or `GO_`
  - h.all.gmt first line starts with `HALLMARK_`
  - KEGG line count ≈186 (KEGG_LEGACY expected count; a count near 658 would
    mean KEGG_MEDICUS was selected instead — FAIL)
  - Each sampled line is tab-separated with at least a handful of gene
    symbols (not an empty `\t\t\n` row; confirms `df$gs_name` and
    `df$gene_symbol` column names are still valid under msigdbr 26).

  **After all 4 gates pass**, write `260414-uqf-SUMMARY.md` to this quick-task
  directory. Template:

  ```markdown
  # Quick 260414-uqf — SUMMARY

  **Task:** Update `download_msigdb` rule for msigdbr 26 API + KEGG_LEGACY pick;
  relax r-msigdbr / r-base pins in envs/gprofiler.yml.

  **Motivation:** Closes SCOUT-FINDINGS issue #8 (.planning/quick/260414-bmi-magma-scout/).

  **Files changed:**
  - src/snakemake/rules/pathway.smk (download_msigdb rule body)
  - envs/gprofiler.yml (2 pins relaxed with justification comment)

  **Decisions:**
  - KEGG_LEGACY (186 sets) chosen over KEGG_MEDICUS (658 sets) for backward
    compatibility with prior Phase 5 development assumptions.
  - r-base and r-msigdbr pins relaxed to floor constraints (≥4.3, ≥10.0);
    other 4 pins unchanged; REQ-9 deviation documented inline.
  - .snakemake/conda/ contents untouched — existing d905eea1… prefix already
    satisfies the relaxed spec.

  ## Verification — verbatim gate output

  ### Gate (a): `snakemake all_pathway --dry-run`
  ```
  <paste verbatim tail output; note job count>
  ```

  ### Gate (b): Rule-scoped dry-run with --use-conda
  ```
  <paste verbatim output; confirm existing env hash was reused>
  ```

  ### Gate (c): Live execution
  ```
  <paste verbatim tail; note wall-time>
  ```
  File listing post-execution:
  ```
  <ls -la output for 4 GMT files>
  ```

  ### Gate (d): Content sanity
  ```
  <paste head -2 for each of 4 files + wc -l for KEGG>
  ```

  ## Next moves

  Resume scout v8: `snakemake results/pathway/magma/bmi_EUR_geneset_fdr.tsv ...`
  (per SCOUT-FINDINGS recommended next moves #2-3).
  ```

  After SUMMARY.md is written, commit ONLY the 3 intended files
  (pathway.smk, gprofiler.yml, 260414-uqf-SUMMARY.md) — do NOT stage anything
  under `.snakemake/` or `data/reference/msigdb/` (those are gitignored or
  out-of-scope). Use gsd-tools commit helper:

  ```
  PATH=/home/ckclinto/miniconda3/bin:$PATH \
    node "$HOME/.claude/get-shit-done/bin/gsd-tools.cjs" commit \
      "fix(quick-260414-uqf): update download_msigdb for msigdbr 26 API + KEGG_LEGACY; relax 2 gprofiler.yml pins" \
      --files src/snakemake/rules/pathway.smk envs/gprofiler.yml \
               .planning/quick/260414-uqf-update-download-msigdb-rule-for-msigdbr-/260414-uqf-SUMMARY.md
  ```

  Pause for user to confirm SUMMARY.md content and gate outputs before marking
  this task complete.
  </action>

  <how-to-verify>
  User reviews 260414-uqf-SUMMARY.md and confirms:
  1. Gate (a) ran cleanly — job count recorded, no missing input errors, no new-rule surprises.
  2. Gate (b) resolved to the existing conda env hash (NOT a new one).
  3. Gate (c) produced all 4 GMT files in the expected directory with non-zero size and recent mtime.
  4. Gate (d) content spot-checks pass — KEGG line count near 186 (KEGG_LEGACY, NOT 658 which would mean KEGG_MEDICUS leaked in), prefixes match expected collection tags, rows are tab-delimited with real gene symbols.
  5. Commit landed with exactly the 3 intended files.
  </how-to-verify>

  <resume-signal>
  Type "approved" if all 4 gates passed and SUMMARY.md is accurate;
  otherwise describe which gate failed or what needs adjustment.
  </resume-signal>

  <done>
  - All 4 verification gates passed with verbatim output captured.
  - 260414-uqf-SUMMARY.md exists in this quick-task directory with the full gate output embedded.
  - Single commit on main containing pathway.smk + gprofiler.yml + SUMMARY.md edits.
  - No changes under .snakemake/conda/ or other unrelated files.
  - Phase 5 scout v8 is now unblocked on issue #8.
  </done>
</task>

</tasks>

<verification>
Full phase acceptance requires all 4 gates in Task 2 to pass with verbatim
output in the SUMMARY.md. A failure on any gate — particularly gate (d) if
the KEGG line count lands near 658 (indicating KEGG_MEDICUS was emitted) or
if column names `gs_name` / `gene_symbol` were silently renamed in msigdbr 26
(would manifest as empty tab-row GMT lines) — halts the task and routes back
to Task 1 for a fix (e.g. updating the `write_gmt` helper to use the new
column names if that turns out to be the regression).
</verification>

<success_criteria>
- SCOUT-FINDINGS issue #8 is closed: download_msigdb rule uses msigdbr 26 API, picks KEGG_LEGACY, and produces all 4 GMT files against the live conda env.
- snakemake DAG job count unchanged (≈575 jobs for all_pathway --dry-run).
- envs/gprofiler.yml has exactly 2 pins relaxed with REQ-9-deviation comment; all other pins untouched.
- No modifications under .snakemake/conda/, data/reference/msigdb/ in git history, or any unrelated rule/env.
- SUMMARY.md contains verbatim output of all 4 gates so Carter can audit the decision trail later.
- Phase 5 scout v8 has a clear green-light on issue #8 (issue #9 — cnsgenomics throttle — is a separate quick task per SCOUT-FINDINGS recommended move #2).
</success_criteria>

<output>
After completion, the quick-task directory contains:
- 260414-uqf-PLAN.md (this file)
- 260414-uqf-SUMMARY.md (written in Task 2)

Commit landed with message:
`fix(quick-260414-uqf): update download_msigdb for msigdbr 26 API + KEGG_LEGACY; relax 2 gprofiler.yml pins`
</output>
