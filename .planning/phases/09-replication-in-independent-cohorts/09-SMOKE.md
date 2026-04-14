---
phase: 09-replication-in-independent-cohorts
smoke_date: 2026-04-14
smoke_scope: code-path validation on real cohort data (T2D × TCF7L2 single-signal)
smoke_status: PASS (core pipeline) + 4 findings (tracked below)
---

# Phase 9 Code-Path Smoke Report — TCF7L2/T2D Positive Control

## Objective

Validate Phase 9 code paths end-to-end on real cohort data, focused on a
single high-confidence positive control (TCF7L2 rs7903146, known to
replicate across all major T2D cohorts). This is **Strategy A** (pre-flight
smoke) before committing to full first-production runs of Phase 0→1→2→5→9.

**Scope:** 1 trait (T2D) × 1 signal (TCF7L2/rs7903146) × 4 cohorts
(FinnGen R12, MVP phs001672 EUR+AFR, BBJ hum0197-v3). Exercises:
- Cohort data download + format inspection
- Region extraction
- Canonical schema conversion
- FIQT winner's-curse correction via `winnerscurse::FDR_IQT` (pinned SHA 2ed00bb)
- IVW fixed-effect meta via `metafor::rma.uni(method='FE')`
- Master table assembly with 4-column effect-size reporting (D-04b)
- Cross-ancestry generalization panel for EAS (D-05c)

**Not in scope:** coloc.susie re-estimation (needs LD panels we haven't
built); COJO sensitivity (needs 1000G PLINK reference from Phase 5 LDSC
download); Phase 1 discovery fits (synthesized via MVP EUR as proxy).

## Result

✓ **PASS** — Core pipeline validates cleanly.

### TCF7L2 rs7903146 effect sizes (T-allele = T2D risk-increasing)

| Cohort | Ancestry | β | SE | P | N_eff |
|--------|----------|-----|------|-----|-------|
| FinnGen R12 | EUR | 0.256 | 0.007 | 1e-282 | 219K |
| MVP phs001672 | EUR | 0.280 | 0.005 | 2e-305 | 515K |
| MVP phs001672 | AFR | 0.226 | 0.014 | 6e-60 | 55K |
| BBJ hum0197-v3 | EAS | 0.318 | 0.022 | 2e-47 | 135K |

**EUR meta (FinnGen + MVP EUR):** β_meta = 0.272, SE = 0.004, p < 1e-308.

### Code-path verification

| Module | Result |
|--------|--------|
| `run_fiqt.R` (+ winnerscurse install from pinned SHA 2ed00bb) | ✓ executes; produces `beta_FIQT`, `se_FIQT` columns; shrinkage correctly negligible at z > 30 |
| `aggregate_replication_meta.R` (metafor) | ✓ executes; EUR meta row emitted; BBJ correctly excluded as `is_generalization=TRUE`; AFR single-cohort correctly produces no meta row |
| Master table schema assembly | ✓ 4-column effect-size reporting + per-cohort + meta columns land in expected schema |
| Cross-ancestry generalization panel | ✓ BBJ EAS row emitted separately (D-05c) |
| Bonferroni + same-direction checks | ✓ 3/3 replication rows pass (genome-wide significant; same T-allele direction) |

## Findings

### Finding 1 — Genome-build config mismatch (non-blocking)

**Empirical observation:**
- **FinnGen R12:** config says `genome_build: GRCh38`. Actual data: rs7903146 at chr10:112998590 — this is the **GRCh37** coord. FinnGen R12 appears to be served in GRCh37 despite our config.
- **MVP phs001672:** config says `genome_build: GRCh38` (plan 09-01 correction). Actual data: rs7903146 at chr10:112998589 — **GRCh37**. File header claims "Human genome build: 38" but the coordinate is unambiguously GRCh37.
- **BBJ hum0197-v3:** config says `genome_build: GRCh38`. Actual data: rs7903146 at chr10:114758349 — **GRCh38** ✓ matches config.

**Impact:** Harmonizer liftover step (`liftover_to_grch37` with 5% drop-rate hard fail) would incorrectly attempt GRCh37→GRCh37 no-op on FinnGen + MVP, which would blow past the 5% drop threshold and RuntimeError. BBJ liftover is correct.

**Fix required before first production:** Update `config/replication_cohorts.yaml`:
- `finngen_r12.genome_build: GRCh37`, `liftover_required: false`
- `mvp_phs001672.genome_build: GRCh37`, `liftover_required: false`
- `bbj_hum0197_v3.genome_build: GRCh38`, `liftover_required: true` (unchanged)

Recommended: inline verification step in `validate_replication_sumstats.py` that picks 2-3 well-known rsids per trait and cross-references their GRCh37/GRCh38 coords from a bundled lookup table. Would catch this class of config error automatically.

### Finding 2 — MVP publishes top-hits only, not full sumstats (design constraint)

**Empirical observation:** MVP dbGaP phs001672 public release for T2D contains 7,281 (AFR) / 655,579 (EUR) rows total — far fewer than the millions expected from a full GWAS. Examination shows only nominally-significant (p < ~0.01) SNPs are published. Full sumstats are not available via dbGaP without a VA collaborator.

**Impact on coloc.susie:** Reduced SNP density in TCF7L2 1Mb region (131 AFR / 1,108 EUR SNPs). coloc.susie requires dense region data for credible-set inference. At the strongest signals this is tolerable, but for Tier B signals (PP.H4 0.5-0.8) MVP replication coloc will be severely underpowered or return low-confidence PP.H4 values.

**Impact on effect-size replication:** Effect-size + Bonferroni criterion works fine (TCF7L2 passes). Any signal below the MVP top-hits threshold won't exist in MVP and will produce a missing-cohort row.

**Fix required before first production:** Either
- (a) Accept the limitation — document in methods that MVP replication is "best available" and expect some missing-cohort rows
- (b) Find alternative MVP sumstats source (some exist on Zenodo / bioRxiv supplementary materials; Vujkovic 2022 + other publications may have more complete releases)
- (c) Exclude MVP from Tier B signal replication; keep for Tier A where signals are strong enough to appear in top-hits

**Recommended: (a) with methods caveat**, since changing approach now would require replanning.

### Finding 3 — LD panels required for coloc.susie aren't built (expected)

**Empirical observation:** coloc.susie re-estimation (the second half of D-03a joint criterion) requires per-region ancestry-matched LD panels. Phase 1 produces these only for the ~50 regions in its discovery scope. Phase 9 replication coloc needs the same LD panels for each cohort's ancestry:
- EUR replication: UKBB-LD (from Phase 1 Plan 01-02) — not yet built end-to-end
- AFR replication: HGDP+1kG AFR (from Phase 1 Plan 01-03) — not yet built end-to-end
- EAS generalization: 1000G Phase 3 EAS (not in Phase 1; new build for Phase 9)

**Fix required before first production:** Phase 1 must run end-to-end before Phase 9 coloc.susie re-estimation can execute. This is expected sequencing — not a bug.

**Smoke workaround:** Skipped coloc.susie for smoke; validated effect-size criterion only. Coloc path integration will be exercised when Phase 1 completes.

### Finding 4 — GBMI portal URL pattern not directly scriptable (design constraint)

**Empirical observation:** GBMI resources page at `https://www.globalbiobankmeta.org/resources` is a curated portal — per-trait download URLs aren't exposed in a scriptable pattern. The plan config has `portal_url` as the access method, implying manual browse-and-download for each trait.

**Impact:** 4-cohort smoke is effectively 3-cohort (FinnGen + MVP + BBJ); GBMI left out. Full D-05 panel design calls for GBMI as the "cross-biobank meta" layer in addition to per-ancestry natives — losing it weakens the replication story.

**Fix required before first production:** Identify the actual GBMI T2D sumstats URL via manual portal browse OR direct email to GBMI coordinators. Add to `config/replication_cohorts.yaml` `gbmi.file_pattern` or per-trait URL overrides. This is a one-time config fix, cheap.

**Quick-task candidate:** `/gsd-quick` to browse GBMI portal + populate config with real download URLs for all 5 traits.

## Closure: What this smoke validated

The Phase 9 code paths work correctly on real cohort data for the effect-size replication + meta-analysis + master-table-assembly half of the pipeline (D-03a criterion 1; D-04; D-06; D-07). This addresses approximately **2 of 3 HUMAN-UAT items**:

- ✓ **HUMAN-UAT #1 (partial)**: "Execute full Phase 9 DAG end-to-end" — effect-size path validated; coloc.susie path requires Phase 1 completion first
- ◇ **HUMAN-UAT #2 (deferred)**: HLA negative control check — not exercisable without coloc.susie (depends on PP.H4)
- ✓ **HUMAN-UAT #3 (partial)**: COJO N=503 caveat — code-verified at 3 levels (shell + test + methods); live WARN emission deferred to Phase 5 LDSC reference download + real COJO invocation

**Positive control claim:** TCF7L2 rs7903146 replicates convincingly in all 4 tested cohorts with same direction, genome-wide significance, and biologically plausible ORs (1.25-1.38). Cross-ancestry generalization to EAS is supported. This is the scientific Layer 3 positive control per VALIDATION.md.

## Forward work

1. **Immediate (small plan or quick):** Fix genome-build config per Finding 1. Catch the regression test will need.
2. **Medium (plan 09-06 or quick):** Identify GBMI URL pattern per Finding 4.
3. **Large (first-production Phase 0→1→2 runs):** Execute Phase 1 end-to-end to produce real discovery `.fit.rds` + Phase 2 tier_assignments.tsv. Then re-run Phase 9 smoke with coloc.susie enabled on 1 region to exercise the rest of D-03.
4. **Production (full Phase 9):** After Phase 1-5 land end-to-end, execute `snakemake all_replication` for all traits × all signals × all cohorts.

## Artifacts

- `results/replication/smoke_logs/tcf7l2_effect_sizes.tsv` — canonical 10-col per-cohort rows
- `results/replication/smoke_logs/fiqt_input.tsv` + `fiqt_output.tsv` — FIQT demonstration
- `results/replication/smoke_logs/meta_input.tsv` + `meta_output.tsv` — IVW EUR meta
- `results/replication/smoke_logs/master_table_smoke.tsv` — assembled master table
- `results/replication/smoke_logs/cross_ancestry_generalization_tier_ab_smoke.tsv` — BBJ EAS generalization panel

## Data on disk

- `data/raw/replication/finngen_r12/finngen_R12_T2D.gz` (820 MB) + `.tbi`
- `data/raw/replication/mvp/phs001672.pha004943.txt` (693 KB, AFR top-hits) + `phs001672.pha004945.txt` (64 MB, EUR top-hits)
- `data/raw/replication/bbj/hum0197.v3.BBJ.T2D.v1/` (extracted zip; auto + chrX txt.gz)
- `data/raw/replication/smoke_tcf7l2/*.tsv` — TCF7L2 region subsets per cohort

## Conda envs built (both new, committed)

- `/rs1/researchers/c/ckclinto/conda_envs/r_coloc/` (1.6 GB; R 4.4 + coloc 5.2.3 + susieR 0.14.2 + metafor + winnerscurse@2ed00bb)
- `/rs1/researchers/c/ckclinto/conda_envs/gcta/` (GCTA 1.94.1 for COJO sensitivity)
