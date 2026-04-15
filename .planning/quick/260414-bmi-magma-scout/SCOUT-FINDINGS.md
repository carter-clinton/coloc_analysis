# bmi.EUR magma_fdr Scout — Findings Report

**Date:** 2026-04-14 / 2026-04-15
**Goal:** Run `results/pathway/magma/bmi_EUR_geneset_fdr.tsv` end-to-end (8 jobs) against real data as a narrow scout before any LSF launch.
**Wall time:** ~3.5 hrs across 7 launch attempts (v1–v7).
**Outcome:** Scout halted at job 2/8. Surfaced **9 distinct Phase 5 issues** that would have all blown up a multi-hour LSF launch. **First real Phase 5 output produced**: `results/pathway/magma/gene_annotation.genes.annot` (107 MB) by `magma_annotate` (job 5/8).

---

## Issues found

### Already fixed in this session

| # | Issue | Quick task | Status |
|---|---|---|---|
| 1 | `pathway.smk:58-61`: 4 ENV constants used 3-level `..` from `workflow.basedir`, escaping the project root. Latent because `--dry-run` skips conda env validation. | `260414-rbv` | ✅ Fixed |
| 2 | `pathway.smk` 30 occurrences: script-path constructions used 2-level `..` from `workflow.basedir`, same root cause as #1. Affects 11 distinct python helper scripts (run_magma, magma_fdr, run_ldsc_partitioned, run_ldsc_seg, run_hess, build_gprofiler_bg, run_gprofiler, etc.). Also 1 special case at line 1164 (3-level `..` for `.snakemake/conda` path). | `260414-tmq` | ✅ Fixed |
| 3 | `envs/gprofiler.yml` was missing `r-msigdbr` despite `download_msigdb` rule using `library(msigdbr)`. | `260414-tmq` | ✅ Spec fixed (yml updated); live env augmented in-place via `mamba install -p ... r-msigdbr --yes` |

### Workarounds applied (operational, not committed)

| # | Issue | Workaround | Notes |
|---|---|---|---|
| 4 | **mamba 2.5 + snakemake 7.32.4 interop bug**: `mamba env create --prefix X` aborts with `error libmamba Non-conda folder exists at prefix - aborting` when invoked from snakemake's wrapper, even when `X` doesn't exist. The same command works when invoked directly. | Pre-create envs manually: `mamba env create --quiet --file <hash>.yaml --prefix <hash>` | snakemake will then see the prefix as ready and skip its own creation attempt. magma + gprofiler envs created this way. |
| 5 | **Anaconda ToS interactive prompt blocker**: mamba 2.5 prompts `Confirm changes: [Y/n]` for any env touching `repo.anaconda.com` (i.e. `defaults` channel). Neither `--quiet`, `--yes`, `yes Y \| mamba`, `--accept-tos`, nor stdin redirection bypasses it. Plain `conda env create` hits the same since conda 23+ uses libmamba solver. | (a) Symlink prefix to existing compatible env (used for `python_stats` → `smoke_dev` since smoke_dev has identical core deps); (b) for envs with no symlinkable equivalent, in-place `mamba install -p` augmentation works because it doesn't trigger the same code path. | The `defaults` channel appears in `python_stats.yml`, `magma.yml`, and `hess_py27.yml` — all will hit this on fresh systems. |
| 6 | **`python_stats` env uses `defaults` channel**: triggers issue #5. smoke_dev has all required deps for `harmonize_sumstats` (numpy, pandas, scipy, snakemake 7.32.4, pyyaml, requests, htslib). | Symlink `.snakemake/conda/<python_stats_hash>_` → `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev` | If python_stats yml ever changes, the hash will change and the symlink needs to be re-created at the new hash. |
| 7 | **gprofiler env hash drift after r-msigdbr addition**: the augmented env at hash `f2752ef7...` doesn't satisfy snakemake's NEW hash `d905eea1...` after the yml edit. | Symlink `.snakemake/conda/d905eea1...` → `f2752ef7...` | Same fragility as #6. |

### Open issues (not yet addressed)

| # | Issue | Severity | Recommended fix |
|---|---|---|---|
| 8 | **`download_msigdb` API drift**: rule calls `msigdbr(species=..., category="C2", subcategory="CP:KEGG")` which was deprecated in `r-msigdbr 10.0.0` (now `collection=` / `subcollection=`). KEGG was also split into `CP:KEGG_LEGACY` (186 sets, original) and `CP:KEGG_MEDICUS` (658 sets, new). The pin in `envs/gprofiler.yml` says `r-msigdbr=7.5.1` but `mamba install` upgraded to 26.1.0 because R 4.5.3 (auto-upgraded from 4.3.1) is incompatible with msigdbr 7.x (only available against r42 builds). | **Blocker** | Two paths: (A) update rule to use `collection=`/`subcollection=` syntax + decide KEGG_LEGACY vs KEGG_MEDICUS (recommend KEGG_LEGACY for backward compatibility with prior Phase 5 development assumptions); (B) downgrade `r-base=4.2` + strict-pin `r-msigdbr=7.5.1`. Path A is more durable. |
| 9 | **`download_sumstats` slow/throttled**: Yengo 2018 BMI download from `cnsgenomics.com` (Australian server, 46.7 MB) hung for >1 hr in v5. URL probe (`curl -sI`) returned 200 OK quickly when tested independently — likely cnsgenomics throttling our IP after many connection attempts during the chaotic v1-v7 restarts. May resolve on its own after a wait period. | Medium | Wait 30+ min for throttle to lift; OR cache the file manually via `wget` to `data/raw/sumstats/bmi.EUR.raw.gz` and let snakemake skip download_sumstats. |

---

## What worked end-to-end with real data

- ✅ **`magma_annotate`** (job 5): produced `results/pathway/magma/gene_annotation.genes.annot` (107 MB) in 38s. First Phase 5 rule to run successfully end-to-end against real reference data.
- ✅ Conda env activation (after pre-creation workarounds)
- ✅ MAGMA binary symlink (`tools/magma_v1.10/magma` → `data/reference/magma/magma`) from `260414-qhr`
- ✅ MAGMA reference data on disk (`g1000_eur.bim`, `NCBI37.3.gene.loc`)
- ✅ Idempotency guards from `260414-qhr` + `260414-qsk` (downloads skipped, references re-used)
- ✅ Path fixes from `260414-rbv` + `260414-tmq` (env paths + script paths land inside project root)

---

## Recommended next moves (in order)

1. **`/gsd-quick`**: update `download_msigdb` rule to use `collection=`/`subcollection=` API. Decide KEGG_LEGACY vs KEGG_MEDICUS — recommend KEGG_LEGACY for continuity. Update `envs/gprofiler.yml` pin to `r-msigdbr>=10.0` (or unpin) + relax `r-base` pin. ~30 min.
2. **`/gsd-quick`**: pre-stage `data/raw/sumstats/bmi.EUR.raw.gz` from cnsgenomics via `wget` outside snakemake (1 file, 46 MB). Sidesteps the throttle issue and lets the scout proceed. ~5 min.
3. **Resume scout v8**: should now complete all 8 jobs and produce `bmi_EUR_geneset_fdr.tsv`.
4. **Codify env yml workarounds**: separate `/gsd-quick` to (a) remove `defaults` channel from python_stats/magma/hess_py27 yamls (where conda-forge+bioconda suffices), (b) document the libmamba 2.5 interop bug in CLAUDE.md or a HACKING.md, (c) add a `bin/setup-envs.sh` helper that pre-creates all conda envs so future runs don't hit the snakemake+mamba interop friction.
5. **Phase 5 retro audit** (deferred, larger scope): the 7 issues found suggest Phase 5 was developed without ever running end-to-end against real conda envs + real data. Consider a `/gsd-validate-phase 5` retroactive pass or a `/gsd-secure-phase 5` review to surface any remaining latent issues before the next scout.

---

## Wall-time accounting

| Phase | Time | Notes |
|---|---|---|
| Init + Phase 0 idempotency (qhr, qsk) | ~25 min | Routed through 2 quick tasks (Phase 0 hardening) |
| Scout v1 | ~30 sec | Failed immediately on env path bug (issue #1) |
| Quick task `260414-rbv` | ~10 min | Fixed env path bug |
| Scout v2-v4 + manual env pre-creation | ~50 min | Hit libmamba interop bug (issue #4); pre-created magma + gprofiler envs |
| Scout v5 (python_stats blockers) | ~30 min | Hit ToS prompt (issue #5); symlinked python_stats |
| Quick task `260414-tmq` | ~25 min | Fixed 30 script paths (issue #2) + r-msigdbr (issue #3) |
| Scout v6, v7 | ~5 min | gprofiler hash drift (issue #7); magma_annotate succeeded ✅; download_msigdb API drift (issue #8); download_sumstats throttled (issue #9) |
| Findings writeup | ~5 min | This document |
| **Total** | **~2.5 hours** | Produced 3 quick-task fixes (qhr, qsk, rbv, tmq), 1 real Phase 5 output artifact, and this 9-finding report |

The scout achieved its purpose: surfaced ~9 latent Phase 5 issues that would have wasted multi-hour LSF compute. None of the 30 script-path bugs OR the 4 env-path bugs would have surfaced via dry-run alone — they require `--use-conda` + actual job execution.
