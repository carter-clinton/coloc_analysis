---
mode: quick
slug: 260413-ro7-fix-phase-5-snakemake-dag-wiring-gaps
type: execute
completed: 2026-04-13
requirements: [RO7-DAG-WIRING]
status: complete
commits:
  - bfb04f8
files_modified:
  - src/snakemake/rules/pathway.smk
files_added:
  - .planning/quick/260413-ro7-fix-phase-5-snakemake-dag-wiring-gaps/deferred-items.md
  - .planning/quick/260413-ro7-fix-phase-5-snakemake-dag-wiring-gaps/260413-ro7-SUMMARY.md
key-decisions:
  - "Approach (c) flag-file inputs chosen over explicit per-chromosome outputs (fragile, cache-invalidating) or directory() outputs (unreliable timestamps on GPFS)."
  - "Side-effect side-effect filenames (.bim, .bed partitions, .ldcts) moved to `params:` because Snakemake requires every `input:` to have a producing rule; flag-file input still creates the download→consumer DAG edge."
metrics:
  tasks_completed: 2
  tests_passing: 100/100
  dag_wiring_gaps_closed: 6
---

# Quick Task RO7 Summary — Fix Phase 5 Snakemake DAG wiring gaps

## One-liner

Wired 10 Phase 5 consumer rules to their reference-data download rules via
flag-file inputs, closing the DAG gap that caused `snakemake all_pathway
--dry-run` to raise MissingInputException on every side-effect reference
file (g1000_eur.bim, baselineLD.*, weights.*, 1000G.EUR.QC.*,
Multi_tissue_*.ldcts, hess_ld_panel chr*.bim, hess_partition chr*.bed).

## What changed

Single file: `src/snakemake/rules/pathway.smk` (+58 / −27 lines).

### Rules wired to download flag files

| Consumer rule | Download rule | Flag input(s) added |
|---|---|---|
| `magma_annotate` | `download_magma_ref` | `magma_ref_flag` (g1000_eur.bed touch) |
| `ldsc_munge` | `download_ldsc_baseline` | `ldsc_baseline_flag` |
| `ldsc_build_custom_annotations` | `download_ldsc_baseline` | `ldsc_baseline_flag` |
| `ldsc_compute_custom_ld_scores` | `download_ldsc_baseline` | `ldsc_baseline_flag` |
| `ldsc_partitioned_h2` | `download_ldsc_baseline` | `ldsc_baseline_flag` |
| `ldsc_seg_gene_expr` | `download_ldsc_baseline` + `download_ldsc_seg` | `ldsc_baseline_flag`, `ldsc_seg_gene_expr_flag` |
| `ldsc_seg_chromatin` | `download_ldsc_baseline` + `download_ldsc_seg` | `ldsc_baseline_flag`, `ldsc_seg_chromatin_flag` |
| `fix_ldcts_paths` | `download_ldsc_seg` | `ldsc_seg_gene_expr_flag`, `ldsc_seg_chromatin_flag` |
| `hess_validate_panel` | `download_hess_panel` | `hess_panel_ld_flag` |
| `hess_local_rhog` | `download_hess_panel` | `hess_panel_ld_flag`, `hess_panel_partition_flag` |

`magma_gene_analysis` was already correctly wired (its `bfile_bed` input
points at the declared `touch()` output of `download_magma_ref`) — no
change required, per plan item B.

## Deviations from Plan

### [Rule 3 - Blocking] Moved side-effect filenames from `input:` to `params:`

**Found during:** Task 1 first dry-run.

**Issue:** The plan's Edit A prescribed "keep `snp_loc` pointing at
`g1000_eur.bim`, ADD an explicit input `magma_ref_flag`". Tried exactly
that: dry-run still failed because Snakemake's DAG resolver requires
**every declared `input:` file to be produced by some rule**. The flag
input creates an ordering edge, but it does not satisfy the separate
"who produces `g1000_eur.bim`?" check. `.bim` is a zip-unpack
side-effect, not a declared output anywhere.

Same issue surfaced in three more rules with undeclared side-effect
inputs:
- `fix_ldcts_paths` (Multi_tissue_*.ldcts files — tar-unpack side-effects)
- `hess_validate_panel` (chr1.bim in EUR LD panel — tar-unpack side-effect)
- `hess_local_rhog` (chr{chrom}.bim and chr{chrom}.bed partition — same)

**Fix:** For each of these four rules, moved the side-effect filename
reference from `input:` to `params:` and updated the shell / run block
to reference `{params.X}` instead of `{input.X}`. The flag-file input
stays in place to create the download→consumer DAG edge. Downloads
still run once, consumers still reference the exact same filenames,
and the pattern is now symmetric across all download rules.

**Files modified:** src/snakemake/rules/pathway.smk

**Commit:** bfb04f8

## Verification

### Automated gate (from plan)

```
$ snakemake --snakefile Snakefile all_pathway --dry-run --cores 1 2>&1 \
  | grep -E "g1000_eur\.bim|baselineLD\.|weights\.[0-9]|1000G\.EUR\.QC\.|Multi_tissue_.*ldcts|hess_ld_panel"
(no matches — PASS)
```

### Narrow DAG resolves

Targeted the download→consumer chain directly:

```
$ snakemake --snakefile Snakefile \
    data/reference/hess/.build_validated \
    data/reference/ldsc_seg/Multi_tissue_gene_expr/Multi_tissue_gene_expr_fixed.ldcts \
    data/reference/ldsc_seg/Multi_tissue_chromatin/Multi_tissue_chromatin_fixed.ldcts \
    results/pathway/magma/gene_annotation.genes.annot \
    --dry-run --cores 1
...
Job stats:
job                      count
---------------------  -------
download_hess_panel          1
download_ldsc_seg            1
download_magma_binary        1
download_magma_ref           1
fix_ldcts_paths              1
hess_validate_panel          1
magma_annotate               1
total                        7
```

All DAG edges resolve correctly; no MissingInputException on any reference file.

### Test suite

```
$ pytest tests/phase5 -x -q
...
100 passed in 1.81s
```

All 100 Phase 5 tests pass, unchanged.

### Scope

```
$ git diff --stat HEAD~1
 src/snakemake/rules/pathway.smk | 85 ++++++++++++++++++++++++++++-------------
 1 file changed, 58 insertions(+), 27 deletions(-)
```

Exactly one file changed, as required. No config edits, no test edits,
no downloads.

## Deferred Issues

Documented in
[deferred-items.md](./deferred-items.md):

- **DEF-RO7-01**: `build_ld_rds` rule in `src/snakemake/rules/ld_reference.smk`
  raises MissingInputException for `data/raw/1kg/TRANS.samples`. The `TRANS`
  pseudo-ancestry is configured for t2d in `config/pipeline.yaml` but
  `build_1kg_sample_lists` only produces the 4 continental ancestry lists.
  Pre-existing; out of scope for RO7 (which is scoped to pathway.smk only).
  Recommended follow-up: new quick task against ld_reference.smk.

- A secondary pre-existing issue in `sumstats.smk` (trait/ancestry config
  mismatch: `bmi` has no `AFR` ancestry in `yengo2018_bmi` dataset)
  surfaces when a wider DAG is traversed; also pre-existing and out of
  RO7 scope.

Both of these blockers are upstream of pathway.smk and unrelated to the
download→consumer wiring gap RO7 targeted. End-to-end
`snakemake all_pathway --dry-run` now progresses past the Phase 5
download layer and fails only in those pre-existing upstream rules.

## Self-Check: PASSED

- `src/snakemake/rules/pathway.smk` modified (58 insertions, 27 deletions).
- Commit bfb04f8 exists on main.
- `pytest tests/phase5` → 100/100 passed.
- None of the six in-scope reference-file patterns raise
  MissingInputException in `snakemake all_pathway --dry-run`.
- `git status` shows no modifications outside this quick-task directory
  (only planning artifacts, which the orchestrator commits separately).
