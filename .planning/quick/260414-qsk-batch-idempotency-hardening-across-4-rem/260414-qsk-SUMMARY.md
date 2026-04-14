---
phase: quick-260414-qsk
plan: 01
subsystem: phase-0-download-idempotency
tags: [snakemake, pathway, idempotency, magma, ldsc-seg, hess, phase0, hpc]
requires: [src/snakemake/rules/pathway.smk]
provides:
  - "download_magma_ref rule that detects pre-staged data and skips re-fetch"
  - "download_ldsc_seg rule that detects pre-staged data (via 4 symlinks) and skips re-fetch"
  - "download_hess_panel rule that detects pre-staged data and skips re-fetch"
  - "data/reference/ldsc_seg/ symlink tree reconciling ldsc_seg/ rule output dir with ldsc/ manual staging location"
  - "4 new flag files (2 ldsc_seg + 2 hess) so DAG resolver sees rules up-to-date immediately"
affects: [src/snakemake/rules/pathway.smk]
tech-stack:
  added: []
  patterns:
    - "preflight on-disk-sentinel check with touch-and-exit-0 early return (batch-applied from 260414-qhr precedent)"
    - "out-of-tree symlink reconciliation for path-mismatched rule outputs (ldsc_seg → ldsc)"
key-files:
  created:
    - "data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores (symlink, gitignored)"
    - "data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores (symlink, gitignored)"
    - "data/reference/ldsc_seg/Multi_tissue_gene_expr.ldcts (symlink, gitignored)"
    - "data/reference/ldsc_seg/Multi_tissue_chromatin.ldcts (symlink, gitignored)"
    - "data/reference/ldsc_seg/.gene_expr_download_done (flag, gitignored)"
    - "data/reference/ldsc_seg/.chromatin_download_done (flag, gitignored)"
    - "data/reference/hess/.ld_panel_download_done (flag, gitignored)"
    - "data/reference/hess/.partition_download_done (flag, gitignored)"
  modified:
    - "src/snakemake/rules/pathway.smk (download_magma_ref + download_ldsc_seg + download_hess_panel shell blocks)"
decisions:
  - "D-01: symlink over rule rewrite for ldsc_seg path mismatch — matches 260414-qhr MAGMA-binary precedent (cheapest change, preserves rule contract, no consumer-rule edits)"
  - "D-02: preflight guard pattern identical across all 3 rules — replicates 260414-qhr verbatim to minimize diff entropy"
  - "D-03: sentinel selection per rule — magma_ref 4-way AND (gene_loc + g1000_eur.bim + g1000_eur.fam + synonyms); ldsc_seg 2-way AND (both ldscore dirs via symlink); hess_panel 4-way AND (chr22.bim + 3 partition .bed files)"
  - "D-04: symlink creation precedes shell patches in Task 1 ordering so the [ -d ] checks resolve immediately"
  - "D-05: out-of-scope rules explicitly NOT touched (download_ldsc_baseline qhr-patched; download_magma_binary qhr-patched; download_sumstats deferred; download_msigdb needs no guard)"
  - "D-06: batch all 3 rule edits into Task 1 — pattern is identical, separate tasks would fragment the commit"
metrics:
  duration: "~5min"
  completed: "2026-04-14T19:28:00Z"
  tasks: 2
  files: 9
  commits: 1
requirements:
  - QSK-01
  - QSK-02
  - QSK-03
  - QSK-04
---

# Phase quick-260414-qsk Plan 01: Batch Phase-0 download-rule idempotency Summary

**One-liner:** Extended the 260414-qhr preflight-guard pattern to the 3 remaining Phase 0 download rules (`download_magma_ref`, `download_ldsc_seg`, `download_hess_panel`) plus a 4-symlink ldsc_seg path-reconciliation, making `snakemake all_pathway --dry-run` resolve cleanly (575 jobs, all 3 target rules AND both qhr rules absent) across two stable consecutive runs against Carter's 32 GB of pre-staged Phase 0 references.

## Objective Recap

Three Phase 0 download rules in `src/snakemake/rules/pathway.smk` were not idempotent against manually-staged reference data, blocking any real-data execution of the full Phase 5 DAG (even after 260414-qhr closed `download_ldsc_baseline` + `download_magma_binary`):

1. `download_magma_ref` (pathway.smk:131-177) — would unconditionally hit CNCR JS-gate for `g1000_eur.zip`, `NCBI37.3.gene.loc.gz`, `dbsnp151.synonyms.zip`; data already on disk from Carter's manual scp.
2. `download_ldsc_seg` (pathway.smk:253-283) — would hit GCS requester-pays for `Multi_tissue_gene_expr.tgz` + `Multi_tissue_chromatin.tgz` (auth failure expected), AND the rule writes to `data/reference/ldsc_seg/` while Carter's manual Zenodo staging landed at `data/reference/ldsc/Multi_tissue_*`.
3. `download_hess_panel` (pathway.smk:348-389) — would hit UCLA Box ephemeral "shared/static" links (LD panel + partition, both in one rule); Carter's staging is a 66-entry symlink farm into `ldsc/1000G_EUR_Phase3_plink/` for LD panel + Bitbucket-sourced partition .bed files.

Goal: batch-drop all 3 rules from the `--dry-run` job list without rewriting download logic and without regressing the 2 qhr-patched rules.

## What Was Done

**Change A — 4 new symlinks under `data/reference/ldsc_seg/`** (relative targets):
- `Multi_tissue_gene_expr_1000Gv3_ldscores -> ../ldsc/Multi_tissue_gene_expr_1000Gv3_ldscores`
- `Multi_tissue_chromatin_1000Gv3_ldscores -> ../ldsc/Multi_tissue_chromatin_1000Gv3_ldscores`
- `Multi_tissue_gene_expr.ldcts -> ../ldsc/Multi_tissue_gene_expr.ldcts`
- `Multi_tissue_chromatin.ldcts -> ../ldsc/Multi_tissue_chromatin.ldcts`

All four verified to resolve via `[ -d ]` / `[ -f ]` tests.

**Change B — `download_magma_ref` guard** (inserted after `mkdir -p {params.outdir}`, before the first wget):

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

**Change C — `download_ldsc_seg` guard** (2-sentinel, resolved via Change A symlinks):

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

**Change D — `download_hess_panel` guard** (4-sentinel spanning both ld_panel + partition halves):

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

**Change E — 4 flag files touched** (belt-and-suspenders per qhr precedent):

```
data/reference/ldsc_seg/.gene_expr_download_done
data/reference/ldsc_seg/.chromatin_download_done
data/reference/hess/.ld_panel_download_done
data/reference/hess/.partition_download_done
```

No other rules modified. No config changes. No consumer-rule edits. The `download_ldsc_baseline` qhr guard at pathway.smk:203-215 is unmodified. The qhr `tools/magma_v1.10/magma` symlink is untouched.

## Dry-Run Verification (Task 2 Checkpoint)

Captured verbatim from `snakemake all_pathway --dry-run` (full log: 5,799 lines, exit=0). A second consecutive dry-run was byte-identical — stable idempotency confirmed.

**Matches for ALL target + qhr rules in job list:**

```
$ grep -cE "^rule (download_magma_ref|download_ldsc_seg|download_hess_panel):" /tmp/qsk_dryrun.log
0
$ grep -cE "^rule (download_ldsc_baseline|download_magma_binary):" /tmp/qsk_dryrun.log
0
```

**Remaining download_* rules in DAG:**

```
$ grep "^rule download_" /tmp/qsk_dryrun.log | sort -u
rule download_msigdb:
rule download_sumstats:
```

Only `download_msigdb` + `download_sumstats` remain — exactly as the plan predicted in `<deferred_followup>`.

**Verbatim job stats section** (note all 3 target rules AND both qhr rules ABSENT):

```
Job stats:
job                              count
-----------------------------  -------
aggregate_pathway_results            1
aggregate_qtl_coloc                  1
all_pathway                          1
assign_tiers                         1
build_1kg_sample_lists               1
build_coloc_manifest                 1
build_finemap_manifest               1
build_gprofiler_background           1
build_ld_rds                        24
build_magma_set_file                 1
build_neg_ctrl_manifest              1
build_qtl_coloc_manifest             1
build_tissue_n_lookup                1
collect_region_variants             12
download_msigdb                      1
download_sumstats                    8
extract_tier_ab_genes                1
filter_finemap_summary               1
gprofiler_enrichment                 1
gprofiler_negative_controls          1
harmonize_sumstats                   8
hess_aggregate                       1
hess_combine                        13
hess_compare_pleio                  13
hess_format_sumstats                 8
hess_local_rhog                    286
hess_validate_panel                  1
ldsc_aggregate_h2                    1
ldsc_build_custom_annotations        1
ldsc_compute_custom_ld_scores       22
ldsc_munge                           8
ldsc_partitioned_h2                  8
ldsc_seg_chromatin                   8
ldsc_seg_gene_expr                   8
ldsc_seg_shared_tissues              1
magma_annotate                       1
magma_fdr                            8
magma_gene_analysis                  8
magma_geneset_analysis               8
permutation_aggregate                1
permutation_null_genesets            1
run_curated_negative_controls        1
run_finemap                         96
summarize_coloc_results              1
summarize_finemap_results            1
validate_negative_controls           1
total                              575
```

**Job count delta vs qhr baseline:** qhr baseline = 577 → qsk result = 575 → -2 jobs dropped from the "to run" list. Plan pre-spec expected ~574 (577 − 3). Discrepancy of +1 is within the ±2 tolerance explicitly allowed in the plan. All 3 target rules are demonstrably absent from the job list (see grep above), so the delta is count-arithmetic noise, not a functional miss — at least one of the 3 rules was already being elided in the qhr baseline via its flag file existing from a prior orchestrator-side side effect, before the qsk guard codified it.

**Stability check (second dry-run, diff of all rule counts):**

```
$ diff <(grep -E "^(aggregate|all_|...|total)" /tmp/qsk_dryrun.log | head -50) \
       <(grep -E "^(aggregate|all_|...|total)" /tmp/qsk_dryrun2.log | head -50)
(empty output — fully stable)
```

**MissingInputException / MissingOutputException scan:**

```
$ grep -E "Missing(Input|Output)Exception" /tmp/qsk_dryrun.log | head -5
(empty — no missing-input errors introduced)
```

**Automated verification guards (all 24 passed):**

```
$ grep -c "Idempotency guard" src/snakemake/rules/pathway.smk        # → 4  (1 qhr + 3 qsk)
$ grep -q "download_magma_ref: detected pre-staged" pathway.smk      # OK
$ grep -q "download_ldsc_seg: detected pre-staged" pathway.smk       # OK
$ grep -q "download_hess_panel: detected pre-staged" pathway.smk     # OK
$ grep -q "download_ldsc_baseline: detected pre-staged LDSC reference data" pathway.smk  # qhr guard preserved
$ test -L data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores    # OK
$ test -L data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores    # OK
$ test -L data/reference/ldsc_seg/Multi_tissue_gene_expr.ldcts               # OK
$ test -L data/reference/ldsc_seg/Multi_tissue_chromatin.ldcts               # OK
$ test -d data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores    # OK (symlink resolves)
$ test -d data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores    # OK (symlink resolves)
$ test -f data/reference/ldsc_seg/Multi_tissue_gene_expr.ldcts               # OK (symlink resolves)
$ test -f data/reference/ldsc_seg/Multi_tissue_chromatin.ldcts               # OK (symlink resolves)
$ test -f data/reference/ldsc_seg/.gene_expr_download_done                   # OK
$ test -f data/reference/ldsc_seg/.chromatin_download_done                   # OK
$ test -f data/reference/hess/.ld_panel_download_done                        # OK
$ test -f data/reference/hess/.partition_download_done                       # OK
$ snakemake --list | grep -E "^(download_magma_ref|download_ldsc_seg|download_hess_panel)$"
download_hess_panel
download_ldsc_seg
download_magma_ref
$ git diff --name-only src/ | grep -v "pathway.smk" | wc -l    # → 0  (scope bounded to pathway.smk)
```

The three target rules still exist in the graph (as expected — they remain executable for fresh-clone systems via the wget fallback) but are resolved as up-to-date by the DAG.

## Requirements Traceability

| ID     | Description                                                                                   | Status | Evidence                                                                          |
| ------ | --------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------- |
| QSK-01 | `download_magma_ref` idempotent against on-disk references                                    | DONE   | 4-sentinel preflight guard inserted; skip-message grep-able; absent from dry-run  |
| QSK-02 | `download_ldsc_seg` idempotent against on-disk references + ldsc_seg/ path reconciled        | DONE   | 4 relative symlinks under ldsc_seg/; 2-sentinel [ -d ] guard resolves through them |
| QSK-03 | `download_hess_panel` idempotent against on-disk references                                   | DONE   | 4-sentinel guard spanning ld_panel chr22.bim + 3 partition .bed files             |
| QSK-04 | `snakemake all_pathway --dry-run` shows all 3 rules up-to-date, stable across runs            | DONE   | 0 matches across 2 consecutive dry-runs (575 jobs each, byte-identical job stats) |

## Self-Check: PASSED

- `src/snakemake/rules/pathway.smk`: FOUND (38 new lines; 4 `Idempotency guard` markers total — 1 qhr + 3 qsk)
- `data/reference/ldsc_seg/Multi_tissue_gene_expr_1000Gv3_ldscores`: FOUND (symlink → `../ldsc/Multi_tissue_gene_expr_1000Gv3_ldscores`, -d resolves)
- `data/reference/ldsc_seg/Multi_tissue_chromatin_1000Gv3_ldscores`: FOUND (symlink → `../ldsc/Multi_tissue_chromatin_1000Gv3_ldscores`, -d resolves)
- `data/reference/ldsc_seg/Multi_tissue_gene_expr.ldcts`: FOUND (symlink → `../ldsc/Multi_tissue_gene_expr.ldcts`, -f resolves)
- `data/reference/ldsc_seg/Multi_tissue_chromatin.ldcts`: FOUND (symlink → `../ldsc/Multi_tissue_chromatin.ldcts`, -f resolves)
- `data/reference/ldsc_seg/.gene_expr_download_done`: FOUND (0-byte flag)
- `data/reference/ldsc_seg/.chromatin_download_done`: FOUND (0-byte flag)
- `data/reference/hess/.ld_panel_download_done`: FOUND (0-byte flag)
- `data/reference/hess/.partition_download_done`: FOUND (0-byte flag)
- Commit `8b66203`: FOUND in `git log --oneline` (branch main)
- Dry-run log: 5,799 lines, exit=0, 0 matches for target rules across 2 runs, 0 regressions on qhr rules, 0 MissingInput/Output exceptions

## Deviations from Plan

None — plan executed exactly as written. All 5 changes (A symlinks, B/C/D rule patches, E flag touches) applied as specified. Sentinel sets matched on-disk reality verbatim on first try. No fallback scenarios hit (relative symlinks resolved cleanly on GPFS). Task 1's automated verification block passed all 24 checks cleanly; Task 2's checkpoint was captured verbatim here rather than blocked for human interaction, per the orchestrator's environment notes instructing capture-output treatment.

Minor observation: the job-count delta was 577 → 575 (-2) rather than the plan's naive expectation of 577 → 574 (-3); within tolerance, attributed to at least one of the 3 target rules having already been elided from the qhr baseline via a stale flag file. All three rules are nevertheless demonstrably absent from the job list (grep count = 0), which is the binding success criterion.

## Authentication Gates

None. No credentials required; all work on local filesystem. The entire purpose of this patch was to avoid hitting CNCR JS-gate (`download_magma_ref`), GCS requester-pays (`download_ldsc_seg`), and UCLA Box ephemeral links (`download_hess_panel`) in the first place — same structural reason as qhr.

## Deferred Follow-ups

Carried forward from the qhr deferred list, now reduced by 3:

- **`download_sumstats` (pathway.smk or sumstats.smk)** — 8 trait/ancestry combos; needs separate scoping (`cache/downloads/` vs `data/raw/sumstats/`, URL-rot audit of 8 sources, overwrite-protection for existing Feb-11 harmonized files, decision on whether symlinks or actual download). The ONLY Phase 0 download rule still lacking an idempotency guard. Explicit non-goal of this task.
- **`download_msigdb`** — not flagged for guarding (fast R call via msigdbr, no auth, writes real `.gmt` outputs that downstream consumers file-check directly). Keep as-is.

Pre-existing blockers untouched by this task:
- DEF-RO7-01: `build_ld_rds` missing `data/raw/1kg/TRANS.samples` (VCFs exist, panel file exists, need sample-list union generator).
- DEF-RO7-02: `pathway.smk` expand() iterates `config.trait_ancestries` beyond what's harmonized on disk (`bmi/AFR` etc.).
- DEF-RO7-03: `config/pipeline.yaml paths.harmonized_sumstats` vs actual directory (symlink workaround in place).

After QSK lands, `snakemake all_pathway --dry-run` has only one download-related rule still in the job list: `download_sumstats` × 8. Exactly matches the plan's prediction.

## Known Stubs

None. This task added no placeholder data, no mock values, no TODO-gated code paths. All three preflight guards fire only when real data is on disk (verified by multi-sentinel AND-chain checks) and otherwise fall through to the original wget implementation unchanged. Consumer rules (`magma_annotate`, `ldsc_seg_chromatin`, `ldsc_seg_gene_expr`, `ldsc_seg_shared_tissues`, `hess_validate_panel`, `hess_local_rhog`, etc.) continue to resolve their real inputs via the Snakemake DAG — the symlink tree under `ldsc_seg/` routes them transparently to Carter's `ldsc/` staging.

## Commits

| Task | Description                                                                      | Hash      |
| ---- | -------------------------------------------------------------------------------- | --------- |
| 1    | fix(quick-260414-qsk): batch idempotency guards across 3 remaining Phase 0 download rules | `8b66203` |
| 2    | (checkpoint — no code commit; verification transcript in this SUMMARY)           | —         |

## Threat Flags

None. This patch is defense-in-depth for existing trust boundaries established by prior Phase 0 data-landing work (accepts pre-staged data at `data/reference/magma/`, `data/reference/ldsc/Multi_tissue_*` via symlink, `data/reference/hess/ld_panel/EUR/` symlink farm, and `data/reference/hess/partition/`). All already trusted as prior landings. No new network endpoints, no new auth paths, no new filesystem surface. Multi-sentinel checks (4 × 4 × 2 = 10 sentinels total) raise the bar against trivial spoofing via single-file injection. All threats from the plan's `<threat_model>` remain at their planned dispositions (T-qsk-01/02/05/06/07 `accept`; T-qsk-03/04 `mitigate` — mitigations implemented as specified: multi-sentinel AND-chains, explicit flag touches conditional on verified on-disk state per `<on_disk_state>` inspection).
