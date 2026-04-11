# Phase 1 CONTEXT — coloc.susie fine-mapping spine

## Context

Phase 1 replaces `coloc.abf` with `coloc.susie` across the cross-ancestry colocalization pipeline and ships an explicit SuSiE policy (REQ-2). Phase 0 closed with 1000G Phase 3 LD panels built, per-trait/ancestry harmonized sumstats, and a working Snakemake skeleton (`finemap.smk` + `ld_reference.smk`). The existing legacy script [run_susie_rss.R](src/legacy/region_analysis/scripts/run_susie_rss.R) fits SuSiE-RSS per (trait × ancestry × region) and emits credible-set JSON — but discards the fitted SuSiE object, so `coloc::coloc.susie()` cannot consume it. The current coloc path at [run_coloc.R:420](src/legacy/region_analysis/scripts/run_coloc.R#L420) calls `coloc.abf()`. Phase 1 wires `coloc.susie` end-to-end, formalizes a SuSiE policy in `config/susie_policy.yaml`, upgrades LD panels for EUR and AFR, and produces a per-locus QC dashboard.

This is the T1 spine — blocking Phases 2, 5, and 9. Scope creep (PP.H4 sweep, negative controls, hyprcoloc, QTL coloc) is **deferred to Phase 2**.

## Locked decisions

### G1 — coloc.susie wiring strategy: **Option A (persist fit + new coloc rule)**

- Modify `run_susie_rss.R` to additionally `saveRDS(fit, <output>.fit.rds)` alongside the existing JSON.
- New script `src/snakemake/scripts/run_coloc_susie.R` loads both `.fit.rds` files for a trait-pair × ancestry × region and calls `coloc::coloc.susie(fit1, fit2)`.
- New rule `run_coloc_susie` in `src/snakemake/rules/coloc.smk` (new file) depends on two `run_finemap` outputs.
- Legacy JSON output and `summarize_finemap_results.py` consumer stay intact — the `.fit.rds` is purely additive.
- **Why:** smallest diff from working legacy, cacheable fits, no quadratic re-fitting when a trait appears in multiple pairs.

### G2 — `config/susie_policy.yaml`

**G2a — L cap:** `L=10` default (unchanged from legacy/susie_rss default) with **L-saturation flag** emitted when all 10 slots retained post-purity filter.

**G2b — `min_abs_corr` sensitivity sweep:** `{0.1, 0.5, 0.9}` — liberal/default/strict. The sweep is post-processing only via `susie_get_cs(fit, min_abs_corr=...)` — no SuSiE refit, so cost is trivial.

**G2c — Convergence-failure retry ladder:**
1. Retry with `max_iter=200` (susie_rss default is 100)
2. If still non-converged, regularize LD with `eps=1e-4` and retry
3. If still non-converged, mark region `status: non_converged` in JSON, keep results, and downstream `filter_finemap_summary.py` excludes from Tier 1

**G2d — L-saturation policy:** Flag in QC only. A supplementary `L=20` rerun on flagged regions is produced as a sensitivity table. No auto in-line retry (avoids unbounded compute).

**Policy YAML skeleton:**
```yaml
# config/susie_policy.yaml
susie:
  L: 10
  coverage: 0.95
  max_iter_primary: 100
  max_iter_retry: 200
  ld_regularization_eps: 1.0e-4
  min_abs_corr_default: 0.5
  min_abs_corr_sweep: [0.1, 0.5, 0.9]
  l_saturation:
    action: flag
    supplementary_rerun_L: 20
  convergence_failure:
    action: retry_ladder
    ladder:
      - increase_max_iter
      - regularize_ld
      - flag_and_exclude_tier1

complex_regions:
  pre_specified:
    - region_id: HLA
      chr: 6
      start: 25000000
      end: 35000000
      rationale: MHC; extreme long-range LD
    - region_id: APOE
      chr: 19
      start: 44000000
      end: 46000000
      rationale: APOE/TOMM40/APOC1 complex signal
    - region_id: LPA_KIV2
      chr: 6
      start: 160000000
      end: 162000000
      rationale: KIV-2 copy number variation
    - region_id: 9p21
      chr: 9
      start: 21000000
      end: 23000000
      rationale: CDKN2A/CDKN2B/ANRIL dense signal
    - region_id: SLC2A9_urate
      chr: 4
      start: 9000000
      end: 11000000
      rationale: Large urate effect, multi-signal
    - region_id: chr8_inversion
      chr: 8
      start: 8000000
      end: 12000000
      rationale: Common inversion polymorphism
  data_flagged:
    triggers:
      - l_saturated
      - n_cs_ge: 3   # at default min_abs_corr=0.5
```

### G3 — Complex-region definition: **Hybrid (curated + data-flagged)**

- Pre-specified list: HLA, APOE, LPA/KIV-2, 9p21, SLC2A9, chr8 inversion (6 regions — accepted as-is).
- Data-flagged: any region with `l_saturated` OR `n_CS ≥ 3` at default `min_abs_corr=0.5`.
- The REQ-2 supplementary sensitivity table has two row-groups: "known complex" and "data-flagged complex", each reporting `n_CS` and `total_PIP_sum` at `min_abs_corr ∈ {0.1, 0.5, 0.9}`.

### G4 — LD reference source: **Option D hybrid (Pan-UKBB EUR + HGDP+1kG AFR + 1000G EAS/SAS/AMR)**

- **EUR:** Pan-UKBB public LD matrices (aligns with Pan-UKBB sumstats provider's own finemapping). Requires new rule `download_panukbb_ld` + conversion to per-region `.rds` format matching legacy loader.
- **AFR:** gnomAD HGDP+1000G merged panel (v3.1.2, AFR n ≈ 730 after merge vs 661 in 1000G alone). Requires new rule `build_hgdp_1kg_ld` + per-ancestry extraction. **Scope flag:** this is Phase-0-level plumbing added to Phase 1 — planner must account for extra compute/download time.
- **EAS, SAS, AMR:** 1000G Phase 3 (already cached from Phase 0 via `ld_reference.smk`). AMR has the weakest sample (n≈347) — documented caveat in methods.
- Legacy LD loader in [run_susie_rss.R:22](src/legacy/region_analysis/scripts/run_susie_rss.R#L22) already handles per-ancestry subdirectories; wiring Pan-UKBB and HGDP+1kG is a matter of producing `.rds` files in the same `{LD_REF_DIR}/{ancestry}/{region}.rds` pattern.
- Existing fallback chain (matched → regularized → identity) stays as-is.

### G5 — Per-locus QC report

**Dimensions to include:** D1 + D2 + D3 + D4 + D6 (D5 plots deferred — can be generated on-demand from cached fits).

- **Baseline (all runs):** `region_id`, `trait`, `ancestry`, `status`, `n_variants`, `L_used`, `n_CS`, `max_PIP`, `ld_source`, `ld_status`, `ld_overlap`, `ld_coverage`, `variant_catalog_used`, `min_abs_corr_used`.
- **D1 — z-score sanity:** per-region KS test of z-scores vs N(0,1), max|z|, λ_GC.
- **D2 — SuSiE convergence:** `niter`, `converged` flag, final ELBO.
- **D3 — LD quality:** `susieR::kriging_rss()` output — expected-vs-observed z-score correlation, flagged outlier variant count.
- **D4 — CS-level quality:** per-CS purity (post-filter `min_abs_corr`), per-CS effective size, top-3 variant IDs + PIPs per CS.
- **D6 — Aggregated HTML dashboard:** single Quarto/Rmd report with sortable/filterable table, jump-to-problem-locus links. One row per (trait × ancestry × region).

## Critical files to modify

| File | Action | Notes |
|------|--------|-------|
| [src/legacy/region_analysis/scripts/run_susie_rss.R](src/legacy/region_analysis/scripts/run_susie_rss.R) | **Modify** | Add `saveRDS(fit, *.fit.rds)`; load policy from `config/susie_policy.yaml` (replaces env-var constants at lines 14-16); add retry ladder for non-convergence; add D1/D2/D3 diagnostics to JSON output |
| `config/susie_policy.yaml` | **Create** | REQ-2 deliverable. Schema under `schemas/` |
| `schemas/susie_policy.schema.yaml` | **Create** | Schema validation for the policy config (consistent with Phase 0 D-06 pattern) |
| `src/snakemake/rules/finemap.smk` | **Modify** | New output `{region}.fit.rds`; new rule `run_finemap_sweep` producing per-region sweep JSON for `min_abs_corr ∈ {0.1, 0.5, 0.9}`; remove placeholder `stroke_afr_susie_sweep` rule (true sweep replaces it) |
| `src/snakemake/rules/coloc.smk` | **Create** | New rule file for `coloc.susie` — replaces legacy `coloc.abf` invocation |
| `src/snakemake/scripts/run_coloc_susie.R` | **Create** | Loads two `.fit.rds` files, calls `coloc::coloc.susie(fit1, fit2)`, writes JSON matching legacy coloc output schema for downstream consumers |
| `src/legacy/region_analysis/scripts/run_coloc.R` | **Deprecate** | Keep as `run_coloc_abf_legacy.R` for reference; remove from active Snakefile imports |
| `src/snakemake/rules/ld_reference.smk` | **Extend** | Add `download_panukbb_ld` rule + `build_hgdp_1kg_ld` rule; produce per-region `.rds` for new EUR/AFR panels |
| `src/snakemake/scripts/download_panukbb_ld.py` | **Create** | Pan-UKBB LD downloader + region-tile conversion |
| `src/snakemake/scripts/build_hgdp_1kg_ld.py` | **Create** | gnomAD HGDP+1kG AFR LD builder |
| `src/snakemake/scripts/susie_qc_report.qmd` | **Create** | Quarto dashboard template (D6) |
| `src/snakemake/rules/qc.smk` | **Extend** | New rule `build_susie_qc_dashboard` rendering the Quarto template |
| `src/legacy/region_analysis/scripts/filter_finemap_summary.py` | **Modify** | Exclude `non_converged` from Tier 1; surface L-saturation and complex-region flags |
| `envs/r_coloc.yml` | **Verify** | Ensure `coloc ≥ 5.2.0` (first version with `coloc.susie`) and `susieR ≥ 0.12` pinned |
| `.planning/REQUIREMENTS.md` | **No change** | REQ-2 acceptance is the target — cross-reference from plan |
| `.planning/phases/01-coloc-susie-fine-mapping-spine/01-CONTEXT.md` | **Create** | After plan approval, this plan file's content becomes the real CONTEXT.md via `/gsd-plan-phase 1` |

## Reuse inventory (do NOT re-implement)

- **LD loader with overlap/coverage logic** — [run_susie_rss.R:22-181](src/legacy/region_analysis/scripts/run_susie_rss.R#L22) — handles SNP_ID/CHR+POS matching, partial-overlap fallback, identity fallback. Keep as-is; only extend to read policy config instead of env vars.
- **Allele reconciliation (strand + ambiguous rescue)** — [run_coloc.R:215-279](src/legacy/region_analysis/scripts/run_coloc.R#L215) — `reconcile_effect_alleles()` with A/T and C/G ambiguous rescue via EAF delta. Lift into a shared R utility and reuse in `run_coloc_susie.R`.
- **Region tabix reader** — [run_coloc.R:35-47](src/legacy/region_analysis/scripts/run_coloc.R#L35) — `read_region_tabix()`. Reuse.
- **Finemap manifest builder** — [create_finemap_tasks.py](src/legacy/region_analysis/scripts/create_finemap_tasks.py) — already driven by config.
- **Filter/tier logic** — [filter_finemap_summary.py](src/legacy/region_analysis/scripts/filter_finemap_summary.py) — extend for new QC fields; don't rewrite.
- **Snakemake config schema pattern** — Phase 0 introduced `schemas/*.yaml` with `validate()`; follow the same convention for `susie_policy.schema.yaml`.

## Scope boundaries

**In Phase 1:**
- SuSiE-RSS fine-mapping for all trait × ancestry × region combinations
- `config/susie_policy.yaml` + schema + documented defaults
- `min_abs_corr` sensitivity sweep at {0.1, 0.5, 0.9} with complex-region supplementary table
- `coloc.susie` replaces `coloc.abf` for all pairwise coloc in the pipeline
- Pan-UKBB EUR LD + HGDP+1kG AFR LD plumbing
- Per-locus QC report (D1+D2+D3+D4) + HTML dashboard (D6)
- Legacy `coloc.abf` call site deprecated

**Out of scope (redirect):**
- PP.H4 threshold sweep → Phase 2 (REQ-3)
- Negative-control regions/genes → Phase 2 (REQ-7)
- hyprcoloc multi-trait colocalization → Phase 2
- eQTL/pQTL/sQTL coloc → Phase 2
- Per-locus LocusZoom PDFs → generated on-demand from cached fits (not a Phase 1 artifact)
- Methods section text → Phase 11 (Phase 1 produces a fragment that Phase 11 assembles)
- Replication cohort application → Phase 9

## Verification plan

**Unit-level:**
1. `run_susie_rss.R` produces both JSON and `.fit.rds` for the 3 toy regions in the CI smoke test (`test/config_override.yaml` from Phase 0).
2. `config/susie_policy.yaml` loads cleanly via `schemas/susie_policy.schema.yaml` validation (add to Snakefile preamble).
3. `run_coloc_susie.R` produces valid JSON for at least one trait-pair × ancestry × region on the toy dataset, output schema matches legacy `run_coloc.R` for downstream compatibility.

**Integration-level:**
4. Dry-run the full Phase 1 Snakemake DAG on the toy 3-locus config — verify all new rules resolve and DAG completes in the dry-run planner.
5. Run the real CI smoke test (deferred from Phase 0 — first real execution now unblocks): Phase 1 rules execute end-to-end on 3 loci × 2 ancestries × 2 traits in the `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/` env (Python 3.11 + snakemake 7.32.4 + pulp<2.8).
6. `grep -r "coloc.abf\|coloc\\.abf" src/snakemake src/legacy` returns zero matches in active (non-legacy-deprecated) code.

**REQ-2 acceptance verification:**
7. `config/susie_policy.yaml` exists, schema-validates, and is loaded by `finemap.smk` (grep for config reference).
8. `min_abs_corr` sensitivity sweep table exists at `results/finemap/sweep_complex_regions.tsv` with rows for all pre-specified complex regions × 3 `min_abs_corr` values × trait × ancestry combinations that have data.
9. Per-locus QC dashboard renders at `results/finemap/qc_dashboard.html` and contains D1/D2/D3/D4 columns.
10. CI smoke test (full run, not dry-run) passes with coloc.susie replacing coloc.abf.

**Manual UAT:**
11. Spot-check one complex region (HLA or APOE) at all three `min_abs_corr` values — verify `n_CS` monotonically decreases as `min_abs_corr` increases (sanity).
12. Spot-check one AFR region — verify Pan-UKBB EUR and HGDP+1kG AFR LD matrices are being used (not 1000G) by checking `ld_source` field in JSON.
13. Review QC dashboard for a handful of flagged regions — confirm `kriging_rss` outlier counts look reasonable (not universally zero, not universally massive).

## Open risks (surface to planner)

- **Pan-UKBB LD artifact size and tile alignment:** Pan-UKBB publishes LD matrices at specific region tilings; these may not match `config/regions_curated.csv` tile boundaries. The `download_panukbb_ld` script must either (a) remap to legacy tiles with overlap logic, or (b) re-tile `regions_curated.csv` to match Pan-UKBB. Researcher should investigate actual Pan-UKBB LD release format before planner commits to an approach.
- **HGDP+1kG AFR panel format:** gnomAD v3.1.2 publishes genotype matrices but LD matrices may need to be computed locally via plink2. Compute/IO cost for 22 chromosomes × ~300 regions × 1 ancestry needs scoping.
- **Conda env compatibility:** `envs/r_coloc.yml` must pin `coloc ≥ 5.2.0` — verify this version resolves cleanly in the `smoke_dev` env or make a fresh env.
- **Non-convergence prevalence:** if the retry ladder is rarely needed on current data, the complexity is low-risk. If >5% of regions hit the ladder, the flag-and-exclude policy for Tier 1 may shrink the analysis set meaningfully — planner should include an audit pass after first full run.
- **Scope flag from G4 choice:** Option D adds Pan-UKBB EUR and HGDP+1kG AFR plumbing. This is a meaningful expansion of Phase 1 work vs Options A or C. Planner must allocate plan-count accordingly (likely 5-6 plans instead of 3-4).

## Downstream impact

- **Phase 2** consumes `coloc.susie` output schema for QTL coloc — Phase 1 must document the output JSON schema so Phase 2's QTL coloc rules can plug in.
- **Phase 5** consumes credible-set variant lists for pathway enrichment background — Phase 1's `finemap_tier*.tsv` outputs are the inputs.
- **Phase 9** replication uses the same policy — `config/susie_policy.yaml` is reused, not forked.
- **Phase 11** methods section references `config/susie_policy.yaml` and the supplementary sensitivity table — Phase 1 produces a methods fragment at `.planning/phases/01-coloc-susie-fine-mapping-spine/methods_fragment.md`.

## Post-approval flow

1. User approves this plan via `ExitPlanMode`.
2. User runs `/gsd-plan-phase 1` which spawns gsd-phase-researcher with this CONTEXT.md.
3. Researcher produces `RESEARCH.md` investigating Pan-UKBB LD format, HGDP+1kG AFR availability, and coloc.susie output schema.
4. gsd-planner produces 5-6 PLAN.md files wave-ordered.
5. `/gsd-execute-phase 1` runs the plans.
