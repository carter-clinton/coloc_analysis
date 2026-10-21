# ta-r4 input inventory — 2026-10-21

> Banked from a read-only background investigation agent's hand-back (model output,
> not independently re-verified line by line). [M] = the agent ran a command;
> [I] = inferred. Treat as INPUT to planning; planners re-measure before relying on
> any single figure.

**Headline:** every fit behind the frozen Track A numbers is gone, along with their
real-LD and identity-LD panels and the GTEx inputs. `targeted_rerun_outputs/hpc_inventory.tsv`
(2026-05-07 cluster snapshot, 302,746 rows) lists them all [M]. They were never
committed: `results/*`, `results_identity_ld/` and `*.rds` are gitignored, and
`git log --all -- 'results/fine_mapping/*'` is empty [M]. Commit c2dfb08 did not remove
them; it removed tracked env/config files incl. `envs/qtl_processing.yml` [M]. Likely
cause: the 30-day `/share` purge [I] (directory mtimes cluster at ~00:34–00:41 on dates
May 28–Aug 2; lsweep backups lost every Apr-29 `fit.rds` while May-3 JSONs survived [M]).

## 1. Per-fit SuSiE-RSS objects
| Item | 2026-05-07 [M] | Now [M] |
|---|---|---|
| `results/fine_mapping/susie/` (real LD, Stage 2) | 96 json + 96 fit.rds | gone; `results/fine_mapping/` absent |
| `results/fine_mapping/finemap_summary.tsv` (md5 8c3e04a2 in frozen record) | present | gone |
| `results_identity_ld/fine_mapping/susie/` (k2d, 2026-04-25) | 95 json + 95 fit.rds | gone |
| `results_lsweep_L{15,20,30}.{preFix,preNiter500}.bak.*` | 3 json + 3 fit.rds + manifest each (SH2B3 EUR bmi/htn/stroke) | json + manifest only |
| `results/fine_mapping_psd_regularized/` | — | 2 small TSVs, no fits |
| `.planning/debug/stage2_narrow_validation/{reald_fits,identity_fits}` | — | survive: 10 real + 7 identity fit.rds, SH2B3/FTO EUR, 2026-04-21 (pre-Stage-2, not the frozen 96) |
| `targeted_rerun_package_20260507_222752.zip` | — | survives: 24 rds paired identity-vs-real coloc.susie objects, SH2B3 EUR (htn×stroke, htn×t2d, stroke×t2d) |
| Summaries | — | `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` (95 rows: n_CS, cs_sizes, ld_overlap); `/rs1/.../region_analysis/results/fine_mapping/` = legacy Feb-2026 run, not Track A |

## 2. LD panels
- Stage 2 EUR panel came from rule `build_ld_rds_1kg_eur` (`ld_reference.smk:273`): plink on
  `data/reference/ldsc/1000G_EUR_Phase3_plink/1000G.EUR.QC.{chr}` (LDSC 1000G Phase 3 EUR,
  HM3-filtered, 503 EUR) → `data/processed/ld_reference/EUR/{region}.rds`. AFR from
  `build_ld_rds` (1000G VCF; identity placeholder when >6,000 variants). HLA used UKBB-LD tiles [M, code].
- 2026-05-07: `data/processed/ld_reference/{EUR,AFR,variants}` 12 entries each + identity backups;
  `ld_reference_identity/EUR` 12; `1000G_EUR_Phase3_plink/` 66 files [M].
- Now: `data/processed/ld_reference/` absent (BLOCKER-B satisfied: no `EUR_ukbb_pub/`);
  `ld_reference_identity/` holds a dangling `variants` link; `data/reference/ldsc/` holds a
  dangling tgz link; all 66 `data/reference/hess/ld_panel/EUR/chr*` are dangling [M].
- Survives on /rs1: 1000G Phase 3 VCFs at `/rs1/researchers/c/ckclinto/coloc_analysis/region_analysis/data_raw/1kg/vcf`
  (48 files, 17 GB) + `EUR.samples`, `AFR.samples`, panel file. Legacy LD rds at
  `/rs1/.../region_analysis/data_processed/ld_reference/{EUR,AFR,TRANS}` (222 each) are NOT the
  Stage 2 panels (SH2B3 698×698 vs 12,716 Stage-2 variants) [M dims; I mismatch].
- Resolver: EUR is off `ld_read_path.ancestries: [AFR]` → `--ld-authoritative false` →
  `run_susie_rss.R` reads `{finemap.ld_reference_dir}/EUR/{region}.rds`. Snakemake's declared
  `input.ld_matrix` walks `EUR_ukbb_pub → EUR_aou → EUR_ukbb_ld → EUR/` separately. If nothing in
  the chain exists, `resolve_ld_path` raises (loud) [M].

## 3. Harmonized GWAS [M]
`data/processed/sumstats_harmonized` → `/rs1/.../region_analysis/data_processed/sumstats_harmonized_fixed`.
Track A combos (bmi.EUR, t2d.EUR, t2d.AFR, hypertension.EUR, asthma.EUR, asthma.AFR, stroke.EUR,
stroke.AFR): all 8 `.tsv.bgz` exist and sha256-match `.planning/amendments/sha256_manifest_harmonized_m1.tsv`.
No bmi/htn AFR in Track A. Newer M1 files (GIANT-UKBB, GIGASTROKE) sit alongside — must not be picked up.

## 4. QTL inputs [M]
`data/raw/gtex_v8/` (101 files on May 7), `data/raw/gtex_v8_sqtl/` (98), `data/processed/qtl_harmonized/`
and `results/qtl_coloc/` (1,274 json + `tier_assignments.tsv` md5 17ff46db) are gone. Re-downloadable
from eQTL Catalogue QTS000015 per `config/qtl_sources.yaml`.

## 5. Regeneration targets and code drift
Targets [M]: fits = rule `run_finemap` (`finemap.smk:274`) via `Snakefile` `FINEMAP_OUTPUTS`; fire
scripts `bin/fire_phase2_stage2_refit.sh`, `bin/fire_susie_lsweep.sh`. Identity = 
`scripts/fire_identity_ld_rerun.sh` + `config/pipeline_identity_overlay.yaml` after
`make_identity_ld_refs.R`. Trait-pair coloc = `coloc.smk:105` `run_coloc_susie` →
`run_coloc_susie.R`; `multitrait.smk` `summarize_coloc_results`. Canonical pairs =
`bin/fire_canonical_susie_pairs.sh` + `pipeline_canonical_r2_overlay.yaml` (needs lsweep fits, gone).
QTL = `rule all_qtl_coloc`. Policy `config/susie_policy.yaml` (L=10, max_iter 100, retry 200,
eps 1e-4) unchanged since 2026-04-21.

Commits after the 2026-04-22 Stage 2 fire touching fit/coloc [M]:
- `02c4404` (04-29) run_susie_rss.R `max_iterations`→`max_iter`: **numerics change** — frozen fits
  were effectively capped at 100 even on retry; non-converged fits (SH2B3 bmi/htn/stroke EUR,
  bmi.EUR.APOE) will move.
- `c0f02b6` R.utils optional (no numerics [I]); `840d1b6` policy path from config;
  `4cfe635`, `6d2e753` `input.ld_matrix` via resolver; `ec01ab3` (06-24) `EUR_ukbb_pub` chain head +
  `estimate_s` serialization; `37c51df` (08-03) occlusion lockstep reroutes AFR sumstats to
  `sumstats_harmonized_occl` (absent); `fb4f5f3`, `dfbd886`, `aeed8c0`, `51a60ca`, `ab19186`
  crosswalk/`--ld-file`/ancestry gate/authoritative panel (AFR only); `10c14f2`, `64f420a`
  allele-aware 4-key join (AFR only); `bf04199`, `656529a` fallback-cause JSON keys + code-freeze
  re-scope; `2563451`, `1815bfd` QTL-coloc LD via resolver, non-zero exit without bridge (AFR only);
  `9c0c67b` strict mode catches `TRANS_aou_eur`. Later commits touch only AoU producers.

## 6. Frozen-numbers record [M]
`TRACK-A-FROZEN-NUMBERS.md` matches baseline (eee9b466); of 38 `md5_baseline.tsv` entries the
figure/aggregator scripts, `fire_canonical_susie_pairs.sh` and `regions_curated.csv` match.
`results/multitrait/coloc_summary.tsv` is now `073f8c05…` (W3 merge) — **not** the `5fa3c400…`
the manuscript cites (Stage 2); `85ab5aa2` (ta-r3 W2) is the third recorded version.
`docs/manuscript/id-vs-ref-LD.md` differs from its baseline (last edits 08-12). Fit JSONs,
`finemap_summary.tsv`, `tier_assignments.tsv` no longer exist. `wave4_susie_overwritten.txt`:
on 2026-04-30 W4 overwrote `results/fine_mapping/susie/*` with code including 02c4404, so the
May-7 on-disk fits were not the 04-22 frozen fits [M file; I implication].

## 7. Environments [M]
`envs/r_coloc.yml`: R 4.4.2, susieR 0.14.2, coloc 5.2.3; named env
`/rs1/researchers/c/ckclinto/conda_envs/r_coloc` matches (also `la_multitrait_r`; `m3-r-ld` R 4.5.3).
All 11 `.snakemake/conda/*_` envs purged to shells; `.snakemake/metadata` gone → fresh solves for
non-pinned deps. `envs/qtl_processing.yml` deleted by c2dfb08 but referenced by
`build_qtl_coloc_manifest`, `aggregate_qtl_coloc`, `assign_tiers`, `l2g_concordance`,
`build_gene_tissue_matrix` — restore via `git show c2dfb08^:envs/qtl_processing.yml`.

## Implications
**Reusable:** 8 sumstats (sha256-verified); 1000G VCFs + sample lists on /rs1; code/config;
pinned r_coloc env; `IDENTITY-LD-K2D-FIT-SUMMARY.tsv`, tracked aggregates and R2 JSONs as
comparison targets; May-7 inventory; SH2B3 narrow-validation fits and targeted_rerun objects as
spot-checks only.

**Must regenerate:** all 96 real + 95 identity fits; 1000G EUR panels (re-fetch LDSC
`1000G_Phase3_plinkfiles.tgz` via Zenodo mirror or rebuild from VCFs); AFR panels; variant lists;
identity payloads; all coloc.susie / coloc.abf outputs; GTEx v8 eQTL/sQTL; QTL-coloc tiers.

**Hazards (each = a silent difference):**
1. `02c4404` changes non-converged fits — reproduce with max_iter_retry=100 or disclose.
2. Current config routes AFR to AoU/M2 panels + occluded sumstats (fails loudly today) — a 1000G
   AFR rerun needs an overlay clearing `ld_read_path`/`occlusion_lockstep` ancestries.
3. EUR can silently fall to identity: if any EUR chain file exists while `EUR/{region}.rds` does
   not, the DAG is satisfied but `run_susie_rss.R:1114` falls back to `diag(n)` and exits 0 —
   assert `ld_source` in every JSON.
4. Identity overlay redirects `ld_reference_dir` but `ld_panel` chain paths are hard-coded, so the
   identity run demands the real EUR panel exist while `enable_ld_pipeline: false` builds nothing.
5. A VCF-based rebuild writes identity placeholders above 6,000 variants if LDSC 1000G.EUR.QC is
   unavailable — pin the LD source, record panel md5s before fitting.
6. Fresh conda solves + missing `qtl_processing.yml`.
7. New outputs on `/share` will be purged again — write to /rs1, commit manifests.
