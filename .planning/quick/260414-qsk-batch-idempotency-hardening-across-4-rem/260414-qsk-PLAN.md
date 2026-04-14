---
phase: quick-260414-qsk
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/snakemake/rules/pathway.smk
  - data/reference/magma/NCBI37.3.gene.loc
  - data/reference/magma/g1000_eur.bed
  - data/reference/magma/dbsnp151.synonyms
  - data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores
  - data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores
  - data/reference/ldsc_seg/Multi_tissue_gene_expr.ldcts
  - data/reference/ldsc_seg/Multi_tissue_chromatin.ldcts
  - data/reference/ldsc_seg/.gene_expr_download_done
  - data/reference/ldsc_seg/.chromatin_download_done
  - data/reference/hess/.ld_panel_download_done
  - data/reference/hess/.partition_download_done
autonomous: false
requirements:
  - QSK-01  # download_magma_ref idempotent against on-disk references (CNCR JS-gate workaround)
  - QSK-02  # download_ldsc_seg idempotent against on-disk references (GCS requester-pays workaround) + ldsc_seg/ path reconciled with ldsc/ manual staging via symlinks
  - QSK-03  # download_hess_panel idempotent against on-disk references (UCLA Box ephemeral link workaround)
  - QSK-04  # snakemake all_pathway --dry-run shows ALL THREE rules absent from job list, stable across consecutive runs

must_haves:
  truths:
    - "`snakemake all_pathway --dry-run` does NOT list `download_magma_ref` as a job to run"
    - "`snakemake all_pathway --dry-run` does NOT list `download_ldsc_seg` as a job to run"
    - "`snakemake all_pathway --dry-run` does NOT list `download_hess_panel` as a job to run"
    - "Re-running `snakemake all_pathway --dry-run` a second time is still clean (stable idempotency)"
    - "All three patched rules, when executed on a system WITHOUT pre-staged data, still function (logic is additive — only early-exit guards added)"
    - "The previously-patched `download_ldsc_baseline` rule and its guard from 260414-qhr is NOT altered"
    - "`download_sumstats` and `download_msigdb` are NOT modified by this task"
    - "Downstream ldsc_seg_chromatin / ldsc_seg_gene_expr / ldsc_seg_shared_tissues rules can still locate their inputs under `data/reference/ldsc_seg/` (symlink resolution)"
  artifacts:
    - path: "src/snakemake/rules/pathway.smk"
      provides: "Three preflight idempotency guards inserted at the top of download_magma_ref, download_ldsc_seg, and download_hess_panel shell blocks"
      contains: "Idempotency guard"
    - path: "data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores"
      provides: "Symlink (relative) to ../ldsc/Multi_tissue_gene_expr_1000Gv3_ldscores so rule output dir matches manual staging location"
      is_symlink: true
    - path: "data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores"
      provides: "Symlink (relative) to ../ldsc/Multi_tissue_chromatin_1000Gv3_ldscores"
      is_symlink: true
    - path: "data/reference/ldsc_seg/Multi_tissue_gene_expr.ldcts"
      provides: "Symlink to ../ldsc/Multi_tissue_gene_expr.ldcts (metadata file needed by downstream ldsc_seg_* rules)"
      is_symlink: true
    - path: "data/reference/ldsc_seg/Multi_tissue_chromatin.ldcts"
      provides: "Symlink to ../ldsc/Multi_tissue_chromatin.ldcts"
      is_symlink: true
    - path: "data/reference/ldsc_seg/.gene_expr_download_done"
      provides: "Flag file touched so DAG resolution sees download_ldsc_seg up-to-date"
    - path: "data/reference/ldsc_seg/.chromatin_download_done"
      provides: "Flag file for the second output of download_ldsc_seg"
    - path: "data/reference/hess/.ld_panel_download_done"
      provides: "Flag file touched so DAG resolution sees download_hess_panel up-to-date (LD panel half)"
    - path: "data/reference/hess/.partition_download_done"
      provides: "Flag file for the partition half of download_hess_panel"
  key_links:
    - from: "rule download_magma_ref"
      to: "data/reference/magma/{NCBI37.3.gene.loc, g1000_eur.bim, g1000_eur.fam, dbsnp151.synonyms}"
      via: "shell [ -f ... ] preflight that touches all three outputs (gene_loc + ref_prefix + synonyms) and exits 0 when sentinels present"
      pattern: "Idempotency guard.*download_magma_ref"
    - from: "rule download_ldsc_seg"
      to: "data/reference/ldsc_seg/{Multi_tissue_gene_expr_1000Gv3_ldscores, Multi_tissue_chromatin_1000Gv3_ldscores}"
      via: "symlinks + preflight that touches both flag outputs and exits 0"
      pattern: "Idempotency guard.*download_ldsc_seg"
    - from: "rule download_hess_panel"
      to: "data/reference/hess/{ld_panel/EUR/chr22.bim, partition/EUR_fourier_ls-all.bed, partition/AFR_fourier_ls-all.bed, partition/EAS_fourier_ls-all.bed}"
      via: "shell preflight that touches both flag outputs and exits 0"
      pattern: "Idempotency guard.*download_hess_panel"
---

<objective>
Batch the 5-sentinel idempotency preflight pattern established in 260414-qhr across the three remaining Phase 0 download rules in `src/snakemake/rules/pathway.smk` so `snakemake all_pathway --dry-run` resolves cleanly without attempting to re-fetch data that is already on disk.

Purpose: Phase 0 data landing (2026-04-14 session) staged 32 GB of reference data at disk locations that mostly-but-not-perfectly match what the download rules expect. Predecessor task 260414-qhr (commit e936aea) fixed `download_ldsc_baseline` + MAGMA binary symlink. Three more rules still re-fetch unconditionally:

  1. `download_magma_ref` (pathway.smk:131-177) — would hit CNCR JS-gate for g1000_eur/gene_loc/synonyms
  2. `download_ldsc_seg` (pathway.smk:253-283) — would hit GCS requester-pays for Multi_tissue_gene_expr/chromatin, PLUS suffers a path mismatch (rule writes to `data/reference/ldsc_seg/`, Carter's data lives at `data/reference/ldsc/Multi_tissue_*`)
  3. `download_hess_panel` (pathway.smk:348-389) — would hit UCLA Box ephemeral links (partition + ld_panel, both handled in this single rule)

Current `snakemake all_pathway --dry-run` baseline: 577 jobs (post-qhr), with these three rules each counting for 1 job. After this task: expect ~574 jobs (577 − 3).

Output:
  - `download_magma_ref`: preflight guard with 4-sentinel check (NCBI37.3.gene.loc + g1000_eur.bim + g1000_eur.fam + dbsnp151.synonyms) that `touch`es the three declared outputs and exits 0
  - `download_ldsc_seg`: 4 symlinks under `data/reference/ldsc_seg/` (the two ldscore directories + the two .ldcts metadata files) + preflight guard with 2-sentinel check that touches both flag outputs
  - `download_hess_panel`: preflight guard with 4-sentinel check that touches both flag outputs
  - Both flag files for ldsc_seg + both flag files for hess_panel explicitly touched (belt-and-suspenders, matching the 260414-qhr precedent Change C)
  - Three touches on the magma rule's declared file-path outputs to make mtime fresh enough that Snakemake accepts them as up-to-date
  - Verified `snakemake all_pathway --dry-run` drops all three rules from the job list and is stable across consecutive runs
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@./CLAUDE.md
@src/snakemake/rules/pathway.smk
@.planning/quick/260414-qhr-fix-phase-0-download-rule-idempotency-1-/260414-qhr-PLAN.md
@.planning/quick/260414-qhr-fix-phase-0-download-rule-idempotency-1-/260414-qhr-SUMMARY.md

<precedent_from_qhr>
The 260414-qhr task established the canonical pattern. Inserted into `download_ldsc_baseline` immediately after `mkdir -p {params.outdir}`:

```bash
# Idempotency guard (D-02, D-03): if references are already staged on disk,
# touch the flag + snplist outputs and exit cleanly. Prevents re-fetching
# ~5 GB from Broad S3 + GCS requester-pays (the latter fails without auth)
# on systems where Carter has manually staged the data from Zenodo.
if [ -f {params.outdir}/baselineLD.22.l2.M ] && \
   [ -d {params.outdir}/1000G_EUR_Phase3_plink ] && \
   [ -d {params.outdir}/1000G_Phase3_frq ] && \
   [ -d {params.outdir}/1000G_Phase3_weights_hm3_no_MHC ] && \
   [ -f {output.hapmap3} ]; then
    echo "download_ldsc_baseline: detected pre-staged LDSC reference data on disk; skipping download" >&2
    touch {output.baseline_done}
    exit 0
fi
```

Visible at src/snakemake/rules/pathway.smk:200-215 (verified in-file during planning).

QSK follows this pattern identically (same sentinel-AND chain, same echo-stderr convention, same `touch {output.*} && exit 0` early-return) for each of the three target rules — only the sentinel files and outputs-to-touch change.
</precedent_from_qhr>

<on_disk_state>
Verified 2026-04-14 via ls inspection immediately before planning.

**MAGMA references (for download_magma_ref):**
```
data/reference/magma/NCBI37.3.gene.loc           (present, >0 bytes)
data/reference/magma/g1000_eur.bim               (present, >0 bytes)
data/reference/magma/g1000_eur.fam               (present, >0 bytes)
data/reference/magma/g1000_eur.bed               (present — note: rule output is touch() on this file)
data/reference/magma/dbsnp151.synonyms           (present, >0 bytes)
```

**LDSC-SEG references (for download_ldsc_seg) — PATH MISMATCH vs rule:**
```
# Carter's manual staging landed HERE (from Zenodo + scp):
data/reference/ldsc/Multi_tissue_gene_expr_1000Gv3_ldscores/       (directory; Franke.100.10.annot.gz etc. inside)
data/reference/ldsc/Multi_tissue_chromatin_1000Gv3_ldscores/       (directory; ENTEX.10.10.annot.gz etc. inside)
data/reference/ldsc/Multi_tissue_gene_expr.ldcts                   (metadata file)
data/reference/ldsc/Multi_tissue_chromatin.ldcts                   (metadata file)

# But the rule writes to a DIFFERENT directory:
data/reference/ldsc_seg/                                           (DOES NOT EXIST yet — must be created)
```

This is a direct analogue of 260414-qhr's MAGMA-binary path mismatch, handled with a symlink per D-01.

**HESS references (for download_hess_panel):**
```
data/reference/hess/ld_panel/EUR/chr22.bim                  (present — symlink farm from 2026-04-14 session, 66 symlinks pointing into ldsc/1000G_EUR_Phase3_plink/)
data/reference/hess/partition/EUR_fourier_ls-all.bed        (present)
data/reference/hess/partition/AFR_fourier_ls-all.bed        (present)
data/reference/hess/partition/EAS_fourier_ls-all.bed        (present)
```

**Flag files / symlinks MISSING (this plan creates them):**
```
data/reference/ldsc_seg/.gene_expr_download_done            (flag)
data/reference/ldsc_seg/.chromatin_download_done            (flag)
data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores    (symlink)
data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores    (symlink)
data/reference/ldsc_seg/Multi_tissue_gene_expr.ldcts               (symlink)
data/reference/ldsc_seg/Multi_tissue_chromatin.ldcts               (symlink)
data/reference/hess/.ld_panel_download_done                 (flag)
data/reference/hess/.partition_download_done                (flag)
```
</on_disk_state>

<interfaces>
From src/snakemake/rules/pathway.smk (read during planning):

```python
rule download_magma_ref:  # lines 131-177
    output:
        gene_loc=PATHWAY_CFG.get("magma_gene_loc", "data/reference/magma/NCBI37.3.gene.loc"),
        ref_prefix=touch(PATHWAY_CFG.get("magma_ref_panel", "data/reference/magma/g1000_eur") + ".bed"),
        synonyms=PATHWAY_CFG.get("magma_snp_synonyms", "data/reference/magma/dbsnp151.synonyms"),
    params:
        outdir="data/reference/magma",
        gene_loc_url="https://ctg.cncr.nl/software/MAGMA/aux_files/NCBI37.3.gene.loc.gz",
        ref_url="https://ctg.cncr.nl/software/MAGMA/ref_data/g1000_eur.zip",
        syn_url="https://ctg.cncr.nl/software/MAGMA/aux_files/dbsnp151.synonyms.zip",
    shell:
        r"""
        mkdir -p {params.outdir}
        # ... three wgets + gunzip/unzip blocks ...
        """
# NOTE: output.ref_prefix uses touch() wrapper — Snakemake auto-touches on rule exit.
# output.gene_loc and output.synonyms are real file paths (not touch()-wrapped).

rule download_ldsc_seg:  # lines 253-283
    output:
        gene_expr_done=touch("data/reference/ldsc_seg/.gene_expr_download_done"),
        chromatin_done=touch("data/reference/ldsc_seg/.chromatin_download_done"),
    params:
        outdir="data/reference/ldsc_seg",
        gene_expr_url="https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/Multi_tissue_gene_expr.tgz",
        chromatin_url="https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/Multi_tissue_chromatin.tgz",
    shell:
        r"""
        mkdir -p {params.outdir}
        # ... two wgets + tar xzf blocks ...
        """

rule download_hess_panel:  # lines 348-389
    output:
        ld_done=touch("data/reference/hess/.ld_panel_download_done"),
        partition_done=touch("data/reference/hess/.partition_download_done"),
    params:
        outdir="data/reference/hess",
        ld_url="https://ucla.box.com/shared/static/l8cjbl5fkge7plsb96xybnrjmhbmsgq5.gz",
        partition_url="https://ucla.box.com/shared/static/6pzgep7kuy0e3t4t1dpyk9mgpizlt28j.gz",
    shell:
        r"""
        mkdir -p {params.outdir}
        # ... two wgets + tar xzf + bim count validation ...
        """
```

HPC environment invariants (from memory):
  - Snakemake binary: `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` (Python 3.11 + snakemake 7.32.4)
  - Node PATH prefix: `/rs1/researchers/c/ckclinto/miniconda3/bin` for any GSD CLI calls
  - Never invoke `snakemake` from miniconda3 base
</interfaces>

<design_decisions>
D-01 (symlink over rule rewrite for ldsc_seg path mismatch):
  CHOSEN: Create 4 relative symlinks under `data/reference/ldsc_seg/` pointing into `../ldsc/Multi_tissue_*`.
  Rationale:
    - Matches the 260414-qhr D-01 precedent (MAGMA binary symlink) verbatim
    - Cheapest change (4 symlinks + preflight guard, no rule output / params surgery)
    - Preserves `download_ldsc_seg`'s rule contract so downstream consumers (`ldsc_seg_chromatin`, `ldsc_seg_gene_expr`, `ldsc_seg_shared_tissues` per pathway.smk grep) continue reading from `data/reference/ldsc_seg/*`
    - Relative targets (`../ldsc/Multi_tissue_*`) survive repo moves; consistent with hess/ld_panel/EUR symlink farm convention
  Rejected:
    - Modifying `params.outdir` or the rule outputs to point at `data/reference/ldsc/`: would break downstream consumer rules that expect `data/reference/ldsc_seg/` paths (already written in params of ldsc_seg_chromatin / ldsc_seg_gene_expr)
    - Adding a parallel guard-via-path-rewrite: same consumer-grep cost, larger diff
    - Copying instead of symlinking: duplicates ~12 GB across two locations for no benefit

D-02 (preflight guard pattern — identical to qhr):
  CHOSEN: For each of the three rules, insert a preflight block at the TOP of the existing shell block (immediately after `mkdir -p {params.outdir}`) that:
    1. Tests all sentinel artifacts via `[ -f ... ]` / `[ -d ... ]` AND-chain
    2. On success: logs skip message to stderr, touches all output flag/file paths, exits 0
    3. On miss: falls through to existing wget logic unchanged
  Rationale: Replicates 260414-qhr verbatim, minimizing diff entropy and review burden.
  Rejected: run: block refactor (larger diff, no functional gain); splitting each rule into detector + downloader (overengineering).

D-03 (sentinel selection per rule):
  **download_magma_ref** — 4 sentinels:
    - `{params.outdir}/NCBI37.3.gene.loc` (real file, matches output.gene_loc)
    - `{params.outdir}/g1000_eur.bim` (side-effect file from g1000_eur.zip unpack; NOT a declared rule output but necessary to verify the zip was fully unpacked)
    - `{params.outdir}/g1000_eur.fam` (additional zip artifact for completeness)
    - `{params.outdir}/dbsnp151.synonyms` (real file, matches output.synonyms)
    Rationale: .bim/.fam confirm g1000_eur.zip was fully unpacked (not just the .bed touched); gene_loc and synonyms are the other declared outputs. Four-way AND guards against partial unpacks.
    Touch-on-skip actions: `touch {output.gene_loc} {output.ref_prefix} {output.synonyms}` — all three outputs explicitly touched to update mtime so Snakemake sees them as fresh.

  **download_ldsc_seg** — 2 sentinels (post-symlink):
    - `{params.outdir}/Multi_tissue_gene_expr_1000Gv3_ldscores` (directory — resolves via symlink)
    - `{params.outdir}/Multi_tissue_chromatin_1000Gv3_ldscores` (directory — resolves via symlink)
    Rationale: After symlinks are created (Task 1), `[ -d ]` test resolves through them to the real dirs under `data/reference/ldsc/`. Both must exist. Not checking .ldcts files in the preflight because they're supporting metadata and would be redundant with the directory checks.
    Touch-on-skip actions: `touch {output.gene_expr_done} {output.chromatin_done}`.

  **download_hess_panel** — 4 sentinels:
    - `{params.outdir}/ld_panel/EUR/chr22.bim` (LD panel presence — chr22 as alphabetical-last proxy for complete unpack)
    - `{params.outdir}/partition/EUR_fourier_ls-all.bed` (EUR partition)
    - `{params.outdir}/partition/AFR_fourier_ls-all.bed` (AFR partition)
    - `{params.outdir}/partition/EAS_fourier_ls-all.bed` (EAS partition)
    Rationale: Both halves of the rule (LD panel + partition) must be satisfied since both flag outputs gate independently. 4-sentinel spans the two concerns. The three-ancestry partition set confirms the partition tarball was fully unpacked, not just the EUR one.
    Touch-on-skip actions: `touch {output.ld_done} {output.partition_done}`.

D-04 (symlink ordering in Task 1):
  Symlinks must be created BEFORE the preflight guard is expected to fire (otherwise the `[ -d Multi_tissue_* ]` check would miss). Task 1 creates symlinks first, then the shell patches, then the explicit flag-file touches (Change C) so dry-run is immediately clean.

D-05 (out-of-scope rules):
  NOT TOUCHED by this plan:
    - download_ldsc_baseline (already patched in 260414-qhr commit e936aea — leave alone)
    - download_magma_binary (already handled via symlink in 260414-qhr — leave alone)
    - download_sumstats (explicitly excluded per task constraints — separate cache/downloads scoping decision needed)
    - download_msigdb (no auth issues; fast R call; produces real .gmt outputs that downstream consumers file-check directly — per task constraints do NOT add a guard)

D-06 (single-task batching):
  CHOSEN: Batch all three rule edits into Task 1 (plus a distinct Task 2 human-verify checkpoint).
  Rationale: Pattern is identical across all three rules; three separate tasks would fragment the commit and triple the review surface. Symlink prep for ldsc_seg is interleaved with the rule edit for that rule (not a separate task) because the symlinks are pure filesystem prep with no cross-rule coupling — batching keeps the atomic unit "make rule X idempotent" intact.
  Rejected: Separating symlinks into their own task — would produce a weird half-landed state where symlinks exist but the rule still has no preflight check, confusing any rollback.
</design_decisions>

<deferred_followup>
NOT addressed in this task, tracked for future work:
  - `download_sumstats` — 8 trait/ancestry combos; needs separate scoping (cache/downloads vs `data/raw/sumstats/`, URL-rot audit, overwrite-protection for Feb-11 harmonized files already on disk)
  - DEF-RO7-01 (build_ld_rds missing TRANS.samples) — pre-existing, unrelated
  - DEF-RO7-02 (trait_ancestries harmonize mismatch) — pre-existing, unrelated
  - DEF-RO7-03 (paths.harmonized_sumstats config mismatch) — on-disk symlink workaround already applied 2026-04-14; full config fix deferred

After QSK lands, `snakemake all_pathway --dry-run` should have only one download-related rule still present: `download_sumstats` (× 8 trait/ancestry expansions).
</deferred_followup>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Patch three download rules with preflight idempotency guards + create ldsc_seg symlinks + touch flag files</name>
  <files>
    src/snakemake/rules/pathway.smk
    data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores (new symlink)
    data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores (new symlink)
    data/reference/ldsc_seg/Multi_tissue_gene_expr.ldcts (new symlink)
    data/reference/ldsc_seg/Multi_tissue_chromatin.ldcts (new symlink)
    data/reference/ldsc_seg/.gene_expr_download_done (new flag)
    data/reference/ldsc_seg/.chromatin_download_done (new flag)
    data/reference/hess/.ld_panel_download_done (new flag)
    data/reference/hess/.partition_download_done (new flag)
  </files>
  <action>
    Perform changes in this order. DO NOT reorder — symlinks must exist before any dry-run, and shell patches must be in place before the explicit flag touches are meaningful.

    ---

    **Change A — Create ldsc_seg symlinks (from repo root) [D-01, D-04]:**

    ```bash
    mkdir -p data/reference/ldsc_seg
    cd data/reference/ldsc_seg

    # Dir symlinks (the two ldscore dirs)
    ln -sfn ../ldsc/Multi_tissue_gene_expr_1000Gv3_ldscores Multi_tissue_gene_expr_1000Gv3_ldscores
    ln -sfn ../ldsc/Multi_tissue_chromatin_1000Gv3_ldscores Multi_tissue_chromatin_1000Gv3_ldscores

    # .ldcts metadata symlinks (supporting files that downstream ldsc_seg_* rules may consume)
    ln -sfn ../ldsc/Multi_tissue_gene_expr.ldcts Multi_tissue_gene_expr.ldcts
    ln -sfn ../ldsc/Multi_tissue_chromatin.ldcts Multi_tissue_chromatin.ldcts

    cd -

    # Verify all four symlinks resolve:
    test -d data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores || { echo "FAIL: gene_expr dir symlink broken" >&2; exit 1; }
    test -d data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores || { echo "FAIL: chromatin dir symlink broken" >&2; exit 1; }
    test -f data/reference/ldsc_seg/Multi_tissue_gene_expr.ldcts || { echo "FAIL: gene_expr ldcts symlink broken" >&2; exit 1; }
    test -f data/reference/ldsc_seg/Multi_tissue_chromatin.ldcts || { echo "FAIL: chromatin ldcts symlink broken" >&2; exit 1; }
    ```

    Use `ln -sfn` (force + no-dereference) so the command is idempotent if run twice. Relative targets (`../ldsc/Multi_tissue_*`) for repo-relocatability, matching the hess/ld_panel/EUR convention and 260414-qhr's MAGMA symlink pattern.

    ---

    **Change B — Patch `download_magma_ref` in src/snakemake/rules/pathway.smk [D-02, D-03]:**

    Locate the rule (currently starts at line 131). Inside the `shell:` block, insert the guard IMMEDIATELY AFTER the line `mkdir -p {params.outdir}` (currently line ~151) and BEFORE `# Gene location file` / the first wget.

    Exact text to insert:

    ```bash
            # Idempotency guard (qsk D-02, D-03): skip if MAGMA reference data already staged.
            # CNCR (ctg.cncr.nl) uses a JavaScript gate that blocks curl/wget for aux_files + ref_data.
            # When Carter has manually downloaded + scp'd these files, the rule must detect and
            # short-circuit; otherwise it hangs on the JS-gated URLs.
            if [ -f {params.outdir}/NCBI37.3.gene.loc ] && \
               [ -f {params.outdir}/g1000_eur.bim ] && \
               [ -f {params.outdir}/g1000_eur.fam ] && \
               [ -f {params.outdir}/dbsnp151.synonyms ]; then
                echo "download_magma_ref: detected pre-staged MAGMA reference data on disk; skipping download" >&2
                touch {output.gene_loc} {output.ref_prefix} {output.synonyms}
                exit 0
            fi
    ```

    Note the indentation: the rule uses a 4-space-indented `r"""` block, and the body content starts at column 9 (8 spaces + content). Match the surrounding indentation exactly — the existing `mkdir -p {params.outdir}` line sets the column.

    Note the 4 sentinels: `gene_loc` matches `output.gene_loc`; `.bim` + `.fam` verify the g1000_eur.zip was fully unpacked (the declared output `.bed` is `touch()`-wrapped so doesn't on-disk-exist meaningfully on its own); `synonyms` matches `output.synonyms`.

    The three `touch` targets use `{output.gene_loc}` / `{output.ref_prefix}` / `{output.synonyms}` Snakemake templates so they render to the correct paths even if `PATHWAY_CFG` overrides the defaults. All three are touched because `gene_loc` and `synonyms` are declared file-path outputs whose mtime must be fresh for Snakemake to see them as up-to-date; `ref_prefix` is already `touch()`-wrapped but touching it explicitly is defensive.

    ---

    **Change C — Patch `download_ldsc_seg` in src/snakemake/rules/pathway.smk [D-02, D-03]:**

    Locate the rule (currently starts at line 253). Inside the `shell:` block, insert the guard IMMEDIATELY AFTER the line `mkdir -p {params.outdir}` and BEFORE `# Multi-tissue gene expression LD scores`.

    Exact text to insert:

    ```bash
            # Idempotency guard (qsk D-02, D-03): skip if LDSC-SEG data already staged.
            # Upstream URL is GCS requester-pays (fails without GCP auth). Carter's manual
            # staging landed at data/reference/ldsc/Multi_tissue_*; symlinks under ldsc_seg/
            # are created out-of-band (see 260414-qsk plan Change A). The [ -d ] checks
            # resolve through those symlinks.
            if [ -d {params.outdir}/Multi_tissue_gene_expr_1000Gv3_ldscores ] && \
               [ -d {params.outdir}/Multi_tissue_chromatin_1000Gv3_ldscores ]; then
                echo "download_ldsc_seg: detected pre-staged LDSC-SEG data (via symlink) on disk; skipping download" >&2
                touch {output.gene_expr_done} {output.chromatin_done}
                exit 0
            fi
    ```

    Note: `[ -d ]` follows symlinks by default in bash, so the ldsc_seg symlinks from Change A will satisfy this test.

    ---

    **Change D — Patch `download_hess_panel` in src/snakemake/rules/pathway.smk [D-02, D-03]:**

    Locate the rule (currently starts at line 348). Inside the `shell:` block, insert the guard IMMEDIATELY AFTER the line `mkdir -p {params.outdir}` and BEFORE `# LD reference panel` / the first wget.

    Exact text to insert:

    ```bash
            # Idempotency guard (qsk D-02, D-03): skip if HESS panel + partition data already staged.
            # UCLA Box "shared/static/..." links are ephemeral (expire or break without notice).
            # Carter staged LD panel as a symlink farm (data/reference/hess/ld_panel/EUR/chr{1..22}.{bed,bim,fam})
            # pointing into ldsc/1000G_EUR_Phase3_plink, and partition files from Bitbucket ldetect-data.
            if [ -f {params.outdir}/ld_panel/EUR/chr22.bim ] && \
               [ -f {params.outdir}/partition/EUR_fourier_ls-all.bed ] && \
               [ -f {params.outdir}/partition/AFR_fourier_ls-all.bed ] && \
               [ -f {params.outdir}/partition/EAS_fourier_ls-all.bed ]; then
                echo "download_hess_panel: detected pre-staged HESS panel + partition data on disk; skipping download" >&2
                touch {output.ld_done} {output.partition_done}
                exit 0
            fi
    ```

    Note: `[ -f ]` resolves symlinks, so the chr22.bim symlink-farm entry will match.

    ---

    **Change E — Explicitly touch the four flag files (belt-and-suspenders, matching qhr precedent):**

    Even though each patched rule will touch its flag on invocation, Snakemake's DAG resolver looks at flag existence BEFORE invoking any rule. To make the very first `--dry-run` clean without needing a no-op rule execution:

    ```bash
    touch data/reference/ldsc_seg/.gene_expr_download_done
    touch data/reference/ldsc_seg/.chromatin_download_done
    touch data/reference/hess/.ld_panel_download_done
    touch data/reference/hess/.partition_download_done
    ```

    Safe because the on-disk data really IS complete (sentinels verified pre-planning); flags are pure Snakemake bookkeeping.

    ---

    **Constraints and DO-NOTs:**

    - DO NOT modify `download_ldsc_baseline` (already patched in 260414-qhr, commit e936aea — the existing "Idempotency guard (D-02, D-03)" block at lines 203-215 must remain IDENTICAL).
    - DO NOT modify `download_magma_binary` (already handled via symlink in 260414-qhr).
    - DO NOT modify `download_sumstats` (explicitly out of scope).
    - DO NOT modify `download_msigdb` (no guard needed per task constraints — fast R call, produces real .gmt outputs).
    - DO NOT change any `params:`, `output:`, `resources:`, or rule header — only the shell block bodies.
    - DO NOT remove any existing wget, tar, unzip, or validation logic. Guards are additive early-exits; the wget fallback MUST remain functional for fresh-clone systems.
    - After all edits, the word "Idempotency guard" must appear EXACTLY FOUR times in pathway.smk (one pre-existing from qhr + three new from qsk). This is the primary diff-scope canary.
  </action>
  <verify>
    <automated>
    # 1. Exactly 4 idempotency guards in pathway.smk (1 pre-existing qhr + 3 new qsk)
    test $(grep -c "Idempotency guard" src/snakemake/rules/pathway.smk) -eq 4

    # 2. Each of the 3 new rules has its own guard (confirm by echo-marker grep)
    grep -q "download_magma_ref: detected pre-staged" src/snakemake/rules/pathway.smk
    grep -q "download_ldsc_seg: detected pre-staged" src/snakemake/rules/pathway.smk
    grep -q "download_hess_panel: detected pre-staged" src/snakemake/rules/pathway.smk

    # 3. Original qhr guard still present unmodified
    grep -q "download_ldsc_baseline: detected pre-staged LDSC reference data" src/snakemake/rules/pathway.smk

    # 4. Symlinks created for ldsc_seg
    test -L data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores
    test -L data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores
    test -L data/reference/ldsc_seg/Multi_tissue_gene_expr.ldcts
    test -L data/reference/ldsc_seg/Multi_tissue_chromatin.ldcts

    # 5. Symlinks resolve (-d/-f follow symlinks)
    test -d data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores
    test -d data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores
    test -f data/reference/ldsc_seg/Multi_tissue_gene_expr.ldcts
    test -f data/reference/ldsc_seg/Multi_tissue_chromatin.ldcts

    # 6. Flag files exist
    test -f data/reference/ldsc_seg/.gene_expr_download_done
    test -f data/reference/ldsc_seg/.chromatin_download_done
    test -f data/reference/hess/.ld_panel_download_done
    test -f data/reference/hess/.partition_download_done

    # 7. Snakemake file still parses (proves shell-block insertion didn't break indentation)
    export PATH=/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --list >/dev/null
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --list | grep -q download_magma_ref
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --list | grep -q download_ldsc_seg
    /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake --list | grep -q download_hess_panel

    # 8. Out-of-scope rules NOT modified — git diff scope check
    # (should only show pathway.smk as modified code file; symlinks + flags are gitignored or expected additions)
    git diff --name-only src/snakemake/rules/ | grep -v pathway.smk | wc -l | grep -q '^0$'
    </automated>
  </verify>
  <done>
    - `src/snakemake/rules/pathway.smk` contains exactly FOUR `Idempotency guard` markers (1 pre-existing qhr + 3 new qsk)
    - Three new echo-skip markers grep-able: "download_magma_ref: detected pre-staged", "download_ldsc_seg: detected pre-staged", "download_hess_panel: detected pre-staged"
    - Pre-existing qhr guard ("download_ldsc_baseline: detected pre-staged LDSC reference data") unchanged
    - Four ldsc_seg symlinks in place, all resolving
    - Four new flag files in place (2 under ldsc_seg/, 2 under hess/)
    - `snakemake --list` succeeds (pathway.smk still parses)
    - git diff scope bounded to pathway.smk (plus gitignored/flag/symlink additions)
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: Verify `snakemake all_pathway --dry-run` reports all three rules as up-to-date, stable across two runs</name>
  <what-built>
    Task 1 patched `download_magma_ref`, `download_ldsc_seg`, and `download_hess_panel` in `src/snakemake/rules/pathway.smk` with preflight idempotency guards (pattern identical to 260414-qhr's `download_ldsc_baseline` patch). Created four symlinks under `data/reference/ldsc_seg/` (two ldscore dirs + two .ldcts files) to reconcile the rule's `params.outdir` with Carter's manual staging under `data/reference/ldsc/`. Touched four flag files so Snakemake's DAG resolver sees all three rules as up-to-date immediately.
  </what-built>
  <how-to-verify>
    1. Set up environment and run the dry-run (from repo root `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/`):

       ```bash
       export PATH=/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH
       /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run 2>&1 | tee /tmp/qsk_dryrun.log
       ```

    2. Check the job list — ALL THREE target rules must be ABSENT:

       ```bash
       grep -cE "^rule (download_magma_ref|download_ldsc_seg|download_hess_panel):" /tmp/qsk_dryrun.log
       # Expected: 0
       ```

       If this returns anything other than 0, identify which rule(s) still appear and investigate which sentinel test is failing (usually: a file or directory the preflight expects is not on disk, or a symlink didn't resolve).

    3. Also confirm the previously-patched (qhr) rules STAYED absent — regression check:

       ```bash
       grep -cE "^rule (download_ldsc_baseline|download_magma_binary):" /tmp/qsk_dryrun.log
       # Expected: 0
       ```

    4. Confirm no MissingInputException / MissingOutputException naming any of:
       - `.gene_expr_download_done` / `.chromatin_download_done`
       - `.ld_panel_download_done` / `.partition_download_done`
       - `NCBI37.3.gene.loc` / `g1000_eur.bed` / `dbsnp151.synonyms`

       ```bash
       grep -E "Missing(Input|Output)Exception" /tmp/qsk_dryrun.log | head -5
       # Expected: nothing related to QSK targets (pre-existing DEF-RO7-* failures are OK)
       ```

    5. Check the overall job count vs. the qhr baseline of 577. Expected: ~574 (577 − 3 rules removed from the DAG). Retrieve from the "total" line of the job stats section:

       ```bash
       grep -E "^total" /tmp/qsk_dryrun.log
       # Expected: total  574  (or near — minor drift if unrelated rules changed since qhr)
       ```

    6. Run the dry-run a SECOND time to prove stability (no silent state transition between runs):

       ```bash
       /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake all_pathway --dry-run 2>&1 | grep -cE "^rule (download_magma_ref|download_ldsc_seg|download_hess_panel):"
       # Expected: still 0
       ```

    7. (Optional, informational) Eyeball the remaining download rules in the job list:

       ```bash
       grep "^rule download_" /tmp/qsk_dryrun.log | sort -u
       ```

       Expected to see ONLY `download_sumstats` and `download_msigdb` entries. If `download_magma_ref`, `download_ldsc_seg`, or `download_hess_panel` appears — the guard is not firing for that rule.

    **Pass criteria (approve the checkpoint):**
      - All 3 target rules ABSENT from dry-run job list (both runs)
      - qhr's `download_ldsc_baseline` + `download_magma_binary` STILL absent (no regression)
      - Dry-run exits 0 (or with the expected pre-existing DEF-RO7-01 / DEF-RO7-02 / DEF-RO7-03 / missing-sumstats-chain errors — those are deferred, not new regressions)
      - Job count in the 570-576 range (577 baseline minus the 3 rules newly dropped; allow ±2 for unrelated drift)

    **Fail criteria (do NOT approve; return to Task 1 for fix-up):**
      - Any of the 3 target rules appears in the job list
      - `snakemake --list` fails or pathway.smk raises a SyntaxError on load (indentation slipped)
      - A previously-passing rule (e.g., `download_ldsc_baseline`) newly appears — indicates the qhr guard was accidentally modified

    If dry-run surfaces unrelated failures (DEF-RO7-*, sumstats chain, TRANS.samples) — those are OUT OF SCOPE for QSK. Note them in the approval message but do not block on them.
  </how-to-verify>
  <resume-signal>Type "approved" after confirming all three target rules are absent from the dry-run job list (twice in a row), no qhr regression, and job count is in expected range. If dry-run surfaces unrelated failures, note them in the approval message; they are out of scope for QSK.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| shell → filesystem | Preflight `[ -f ]` / `[ -d ]` tests run inside Snakemake-managed shell with full user creds; no untrusted input |
| Snakemake DAG → pre-staged data | Flag files and symlinks manually placed; we trust that Carter's Zenodo-staged + CNCR-staged + Bitbucket-staged data is genuine (out-of-band verified by ls + file sizes + prior Phase 0 integration test) |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-qsk-01 | Tampering | Sentinel files (NCBI37.3.gene.loc, g1000_eur.bim/.fam, etc.) spoofed by attacker to pass the preflight check with corrupted content | accept | Same reasoning as T-qhr-01 (qhr plan): on-disk data staged from content-addressable sources (Zenodo DOIs, CNCR tracked downloads, Bitbucket Git refs), HPC filesystem under per-user chmod. Multi-sentinel checks (4 files for magma_ref, 4 for hess_panel, 2 dirs for ldsc_seg) guard against trivial spoofing by single-file injection. |
| T-qsk-02 | Tampering | ldsc_seg symlinks could be redirected to malicious locations | accept | Symlinks owned by ckclinto; relative targets (`../ldsc/Multi_tissue_*`) point into the same project tree under user-controlled filesystem. No elevated privilege path. |
| T-qsk-03 | DoS (self-inflicted) | Preflight guard false-negative (one sentinel missing due to partial unpack) falls through to wget, which hangs on CNCR JS-gate / GCS requester-pays / UCLA Box expired link | mitigate | Each guard requires ALL sentinels present (4-way AND for magma_ref + hess_panel, 2-way AND for ldsc_seg). A partial unpack falls through to wget; wget uses `--timeout=300` (magma/ldsc_seg) or `--timeout=600` (hess) + `--max-redirect=3/5`, so upstream auth/404 failures return quickly (non-zero exit halts DAG). User receives actionable error instead of infinite hang. |
| T-qsk-04 | Information Disclosure | Flag file touched without real data underneath could mask a failure and produce garbage downstream pathway results (MAGMA genesets / LDSC-SEG tissue h2 / HESS local rhog) | mitigate | Sentinel checks are the guard. Explicit flag touches (Change E) are conditional on human verification of on-disk state — inspection done pre-planning (see `<on_disk_state>`). Downstream rules additionally perform file-content validation where relevant (MAGMA rejects empty gene.loc, LDSC-SEG rejects empty .l2.ldscore.gz, HESS rejects missing .bim). |
| T-qsk-05 | Repudiation | No audit trail if a sentinel is later removed and wget fails silently | accept | Snakemake logs all rule invocations to stderr + `.snakemake/log/`. Wget failures surface as non-zero exits. Low risk for solo-author pipeline. |
| T-qsk-06 | Elevation of Privilege | Shell blocks execute as ckclinto on HPC; no privilege change requested | accept | No sudo, no setuid, no cross-user filesystem writes. Executes within existing Snakemake shell contract. |
| T-qsk-07 | Spoofing | Symlink farm resolution could follow a hostile symlink chain at `data/reference/ldsc/` | accept | Same filesystem ownership as T-qsk-02; user-controlled tree; no network access required by preflight. |
</threat_model>

<verification>
Overall phase checks (bash-executable):

```bash
export PATH=/rs1/researchers/c/ckclinto/miniconda3/bin:$PATH
SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake

# 1. Files + symlinks in place
test -L data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores
test -L data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores
test -L data/reference/ldsc_seg/Multi_tissue_gene_expr.ldcts
test -L data/reference/ldsc_seg/Multi_tissue_chromatin.ldcts
test -d data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores   # follows symlink
test -d data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores
test -f data/reference/ldsc_seg/.gene_expr_download_done
test -f data/reference/ldsc_seg/.chromatin_download_done
test -f data/reference/hess/.ld_panel_download_done
test -f data/reference/hess/.partition_download_done

# 2. Snakemake still parses + all 3 target rules discoverable
$SMK --list >/dev/null
$SMK --list | grep -q "^download_magma_ref$"
$SMK --list | grep -q "^download_ldsc_seg$"
$SMK --list | grep -q "^download_hess_panel$"

# 3. NONE of the 3 target rules appears in the all_pathway dry-run job list
JOB_COUNT=$($SMK all_pathway --dry-run 2>&1 | grep -cE "^rule (download_magma_ref|download_ldsc_seg|download_hess_panel):")
test "$JOB_COUNT" -eq 0

# 4. qhr-patched rules STILL absent (no regression)
QHR_COUNT=$($SMK all_pathway --dry-run 2>&1 | grep -cE "^rule (download_ldsc_baseline|download_magma_binary):")
test "$QHR_COUNT" -eq 0

# 5. Stable across a second dry-run
JOB_COUNT_2=$($SMK all_pathway --dry-run 2>&1 | grep -cE "^rule (download_magma_ref|download_ldsc_seg|download_hess_panel):")
test "$JOB_COUNT_2" -eq 0

# 6. pathway.smk contains exactly 4 idempotency guards (1 qhr + 3 qsk)
test $(grep -c "Idempotency guard" src/snakemake/rules/pathway.smk) -eq 4

# 7. Each new guard's skip-message marker present
grep -q "download_magma_ref: detected pre-staged" src/snakemake/rules/pathway.smk
grep -q "download_ldsc_seg: detected pre-staged" src/snakemake/rules/pathway.smk
grep -q "download_hess_panel: detected pre-staged" src/snakemake/rules/pathway.smk

# 8. Out-of-scope code files NOT modified
# Only pathway.smk should appear in git diff for src/
git diff --name-only src/ | grep -v "pathway.smk" | wc -l | grep -q '^0$'

# 9. Out-of-scope rules' download_sumstats and download_msigdb still present (sanity — NOT modified)
grep -q "rule download_sumstats:" src/snakemake/rules/pathway.smk  # or sumstats.smk if separate
grep -q "rule download_msigdb:" src/snakemake/rules/pathway.smk
```
</verification>

<success_criteria>
- `snakemake all_pathway --dry-run` exits with ZERO jobs for each of `download_magma_ref`, `download_ldsc_seg`, `download_hess_panel`
- Second dry-run matches first (stable idempotency)
- qhr-patched rules (`download_ldsc_baseline`, `download_magma_binary`) still absent from dry-run — no regression
- All four ldsc_seg symlinks resolve to their targets under `data/reference/ldsc/`
- All four new flag files exist (2 ldsc_seg + 2 hess)
- Exactly FOUR `Idempotency guard` markers in pathway.smk (1 pre-existing qhr + 3 new qsk), no more, no fewer
- Three new skip-message echo strings are grep-able in pathway.smk
- git diff scope bounded: `src/snakemake/rules/pathway.smk` (code) + symlinks + flag files
- `download_sumstats` and `download_msigdb` remain unchanged (out of scope per constraints)
- Total dry-run job count drops from 577 (qhr baseline) to ~574 (3 rules removed from DAG execution)
- Any dry-run failures surfaced are pre-existing (DEF-RO7-01 / DEF-RO7-02 / DEF-RO7-03 / download_sumstats chain) — NOT new regressions introduced by QSK
- Deferred items clearly flagged in SUMMARY: `download_sumstats` (cache/downloads scoping) remains the only Phase-0 download rule lacking idempotency treatment
</success_criteria>

<output>
After completion, create `.planning/quick/260414-qsk-batch-idempotency-hardening-across-4-rem/260414-qsk-SUMMARY.md`
</output>
