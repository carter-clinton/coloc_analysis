# Phase ta-sh2b3-canonical-and-cache-refresh — Research

**Researched:** 2026-04-29
**Domain:** R / Snakemake / LSF dispatch + variant-ID propagation + manuscript-anchor preservation rename
**Confidence:** HIGH overall (most claims verified by direct file inspection); MEDIUM on a few items flagged inline

---

## Summary

This phase has two locked computational scopes (Issue 1: SH2B3 EUR L-sweep + canonical-pair `coloc.susie`; Issue 2: variant-ID cache invalidation + Snakemake re-fire) plus a Wave-6 mechanical rename and a Wave-7 closeout. The CONTEXT.md is fully prescriptive — 13 locked decisions, 8-wave skeleton, all invariants spelled. The planner's job is therefore mechanics, not strategy.

The research surfaced **three load-bearing planning gaps that the planner must address explicitly** before executing:

1. **Repo path discrepancy.** CONTEXT.md and original GSD-add brief reference `scripts/python/`, `scripts/R/`, `workflow/Snakefile`, `bin/bsub_wrapper.sh` — none of those exist. Real layout: `src/python/`, `src/R/{aggregators,figures}/`, top-level `Snakefile`, `config/bsub_wrapper.sh`. Every PLAN.md task that references the wrong path will fail. `[VERIFIED: ls + Snakefile read]`
2. **No `--L` CLI flag in `run_susie_rss.R`.** The L value is sourced from `config/susie_policy.yaml` (`susie.L`, default 10). Snakemake's `run_finemap` rule passes a fixed `--policy` flag. To execute D-TA-02's L-sweep {15, 20, 30}, the planner must choose a sweep mechanism: (a) per-L policy YAML overlays + a custom driver script (precedent: `scripts/fire_identity_ld_rerun.sh` + `config/pipeline_identity_overlay.yaml`); (b) extend `run_susie_rss.R` to accept `--L`; (c) direct Rscript invocation outside Snakemake with three on-the-fly policy files. Recommendation: option (a). `[VERIFIED: run_susie_rss.R lines 227-251 + finemap.smk inspection]`
3. **No `variant_ids` top-level key in SuSiE-RSS fit JSONs.** The CONTEXT-prescribed Wave-0 diagnostic ("inspect `variant_ids[0]`") is mechanically unrunnable as written. The actual signal lives inside `credible_sets.CSn` (per-CS list of `{CHR, POS, BETA, SE, pip}` records — no SNP_ID) AND in the sibling `.fit.rds` file's `colnames(fit$alpha)` / `names(fit$pip)` (which carry the rsid-vs-chrpos token that decides D-TA-04). The diagnostic must read the `.fit.rds` via Rscript, not `jq` the JSON. `[VERIFIED: python json inspection of 4 SH2B3/FTO fit JSONs + run_susie_rss.R lines 510-559]`

**Primary recommendation:** Plan in 8 waves (Wave 0–7) per the locked outline. The planner must (a) absorb the path corrections above into every task spec, (b) commit to the per-L policy overlay strategy for Wave 1, and (c) write the Wave-0 variant-ID diagnostic as an Rscript task that reads the `.fit.rds`, not a `jq` task that reads the JSON.

---

## User Constraints (from CONTEXT.md)

### Locked Decisions

The following 13 decisions were locked when Carter accepted all recommended defaults at 2026-04-28T22:42:00-04:00. Copy verbatim — DO NOT re-litigate any.

| ID | Decision | Wave |
|----|----------|------|
| **D-TA-01** | All Wave 0 + Wave 1 + Wave 2 + Wave 4 LSF compute uses `/rs1/researchers/c/ckclinto/coloc_analysis/` as canonical repo path. Pre-fire git work may use the GPFS mount `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/`, but every `bsub` / Snakemake invocation passes `/rs1/...` explicitly. | 0–4 |
| **D-TA-02** | L-sweep {15, 20, 30} pre-registered supplementary fire. Re-fit BMI + hypertension + stroke at all three L; report `n_CS` per fit per L; primary-result L is the lowest where `n_CS << L` for all three traits. | 1 |
| **D-TA-Wave1-headline** | Headline numerator (51/96 vs recomputed) decision is **deferred to post-Wave-1**. Wave 1 SUMMARY reports per-trait convergence outcomes; does NOT update the headline. Wave 6 task makes the recompute-vs-disclose-column choice. | 1 → 6 |
| **D-TA-03** | Wave 2 fires `coloc.susie` on **9 new SH2B3 EUR trait-pairs** (lattice minus already-on-disk `asthma_vs_t2d`): asthma–bmi, asthma–hypertension, asthma–stroke, bmi–hypertension, bmi–stroke, bmi–t2d, hypertension–stroke, hypertension–t2d, stroke–t2d. | 2 |
| **D-TA-Wave3-thresholds** | Wave 3 `checkpoint:human-verify` uses standard manuscript thresholds: collapse `PP.H4 < 0.5` / partial `[0.5, 0.8)` / survive `≥ 0.8`. Branch (a/b/c) is recorded as `D-TA-WAVE3-OUTCOME-XX` in CONTEXT addendum AFTER Wave 2. | 3 |
| **D-TA-04** | **Diagnostic-driven** cache scope: Wave 0 reads sample SuSiE-RSS fits to determine variant-ID format. rsid → QTL-coloc only (~10 hr); chr:pos → both layers (~15 hr); mixed → CONSERVATIVE-BOTH. | 0 → 4 |
| **D-TA-05** | Wave 0 verifies OSF pre-reg coverage at `osf.io/pvb5j` + `osf.io/az52u`. If covered → Wave 1 cleared. If uncovered → Carter posts amendment (Wave 1 hard-blocked). | 0 |
| **D-TA-Cache-OSF** | OSF treatment of Issue 2 cache invalidation = **deviation-log entry only** (append to `.planning/amendments/osf_deviations.md`). Cache hygiene fix, NOT new analysis. | 7 |
| **D-TA-06** | id-vs-ref-LD nickname rename bundled in Wave 6: `docs/manuscript/track_a_pivot.md` → `id-vs-ref-LD.md`; `.planning/amendments/TRACK-A-PIVOT.md` → `ID-VS-REF-LD-STRATEGY.md`; `bin/build_track_a_submission_bundle.sh` → `bin/build_id_vs_ref_ld_submission_bundle.sh`. **Keep** `TRACK-A-FROZEN-NUMBERS.md` (carter-flagged optional; widely cross-ref'd). | 6 |
| **D-TA-Wave-6-timing** | Rename + reference fix-ups bundled into Wave 6 (zero extra waves). Mechanical tasks first, then narrative atomic-update per-file. | 6 |

### Claude's Discretion

None. Carter accepted all 13 recommended defaults. Every item that would have been Claude's discretion is now a locked decision.

### Deferred Ideas (OUT OF SCOPE)

- MAXIMUM cross-region replication (FTO_16q12 + MC4R_18q21 + APOE_19q13 + CXADR_F2RL1_6p21 against post-L=20 fits).
- Threshold-lowering to 0.3 (would surface FTO Tier-C 0.3099 as "partial"; rejected during quick-260427-e8n).
- Pre-emptive OSF amendment for all Issue 1+2 sub-decisions (verify-then-amend chosen instead).
- Cache-invalidation pre-reg amendment (deviation-log only).
- `TRACK-A-FROZEN-NUMBERS.md` rename.
- `bin/build_id_vs_ref_LD_submission_bundle.sh` mixed-case (lowercase chosen).
- Wave 0.5 / Wave 6.5 dedicated rename waves (Wave 6 bundled).
- M2-POST-M3-08 mtCOJO re-fire (Terminal A capacity; file-disjoint).
- Sumstats Route C manual-fetch refresh (Terminal A capacity; file-disjoint).

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **REQ-PUBLIC-DATA-ONLY** | Every dataset used must be public or open-DUA. | All inputs (1000G EUR Phase 3, Evangelou-2018 / GIANT / GIGASTROKE / Mahajan / asthma sumstats; GTEx eQTL/sQTL) are public. Wave-7 SUMMARY restates compliance. |
| **REQ-SUSIE-RSS-POLICY** | Pipeline ships explicit policy for L cap, convergence failures, `min_abs_corr`. | Wave 1 L-sweep produces sensitivity table; `config/susie_policy.yaml` already locks max_iter ladder + min_abs_corr sweep `[0.1, 0.5, 0.9]`. The L-sweep updates `policy.l_saturation.supplementary_rerun_L` outcome from "20" prediction to a measured value. |
| **REQ-PP.H4-THRESHOLD-SWEEP** | Track A reports tier counts across PP.H4 ∈ {0.5, 0.7, 0.8, 0.9}. | Wave 5 aggregator `aggregate_qtl_coloc.py` already builds `pph4_threshold_sweep.tsv` (downstream rule `pph4_threshold_sweep` in `qtl_coloc.smk` — verify rule name at planning time). Wave 5 must rebuild this table against post-refresh disk state. |
| **REQ-OSF-PREREG** | OSF pre-reg posted before any execution; D-TA-05 enforces. | Wave 0 verifies coverage; Wave 7 records the deviation-log entry per D-TA-Cache-OSF. |
| **REQ-SNAKEMAKE-CI** | Pipeline runs end-to-end on toy 3-locus subset. | Wave 4's `--use-conda -j 50` re-fire exercises the full QTL-coloc DAG; toy-3-locus regression is OUT of phase scope but Wave 7 SUMMARY can note it ran successfully. |
| **REQ-PATH-PARAMETERIZATION** | All paths through `config/pipeline.yaml`. | Already enforced; the rename in Wave 6 must NOT introduce hardcoded `id-vs-ref-LD` paths into `src/R/`, `src/python/`, `src/snakemake/`, `config/`. Verify via `grep -r "/rs1/researchers" src/R src/python src/snakemake config` returns 0 — pre-existing acceptance test. |

---

## Project Constraints (from CLAUDE.md)

The project's CLAUDE.md and user-memory pins impose the following non-negotiable directives. Plans must verify compliance per task.

| Directive | Source | How it applies to this phase |
|-----------|--------|------------------------------|
| **100% public data; no wet-lab; no proprietary data** | CLAUDE.md `### Constraints` | All Wave 1/2/4 inputs (1000G EUR Phase 3, GTEx v8, public GWAS sumstats) are public. Wave 7 SUMMARY restates compliance. |
| **No web/JS stack; R + Python + Snakemake + bash + conda only** | CLAUDE.md | All planned tooling complies. |
| **GPFS filesystem; do NOT use worktree isolation; `solo` mode + `git.isolation: branch`** | CLAUDE.md | `.planning/config.json` confirms `branching_strategy: "none"` and `use_worktrees: false`. Plans must NOT reference worktrees. |
| **Never invoke snakemake from miniconda3 base (Python 3.13)** | memory `project_python_311_pin.md` | Use `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` (Snakemake 7.32.4 + Python 3.11) — VERIFIED present 2026-04-29. Or `--use-conda` flag. |
| **Never tell user to `conda activate`** | memory `feedback_no_conda.md` | All commands use absolute conda env paths; never wrap in `conda activate`. |
| **Use `serial` queue for SuSiE-RSS + coloc.susie work; `la_multitrait_r` env** | memory `feedback_lsf_queues.md` + AUDIT-RESPONSE L260 | Wave 1 + Wave 2 use `serial` (5760-min wall) + `la_multitrait_r`. |
| **`LSF_UNIT_FOR_LIMITS=GB`; `bsub_wrapper.sh` sets `-W` to queue max** | memory `feedback_lsf_queues.md` + `config/bsub_wrapper.sh` | Snakemake LSF dispatch via `--profile config/cluster_lsf` honors this. Direct `bsub` invocations (Wave 1 driver script) must respect it too. |
| **Never `git add .` or `-A` on GPFS shared tree** | memory `feedback_multi_terminal_staging.md` | Every commit task in PLAN.md uses explicit file paths. |
| **id-vs-ref-LD nickname for FUTURE artifacts only; DO NOT rewrite git history** | memory `project_track_a_handle.md` | Wave 6 commits keep going forward; pre-2026-04-28 commit messages with `track_a_pivot` tokens are historical record — do not amend. |
| **Original-research framing — never "revision" / "correction" / "cleanup" / "fix"** | memory `feedback_original_research_framing.md` | Wave 6 manuscript prose, Wave 7 SUMMARY language, atomic-commit messages all use "original hypothesis-driven research" framing. |
| **Always pick rigor over time-saving in gray-area decisions** | memory `feedback_rigor_over_speed.md` | Plan must NOT compress Wave 1 to L=20-only or Wave 2 to MINIMUM 2-pair scope; locked decisions already chose the rigorous L-sweep + 9-pair lattice. Per-task verification dimensions take rigor over speed. |
| **`results_identity_ld/` NOT committed; gitignored (DEC-2026-04-25-01)** | `.planning/DECISIONS.md` | Wave 5 aggregators that read `results_identity_ld/...` paths read regenerable artifacts; nothing added to git from that namespace. |

---

## Standard Stack

### Core (already on disk; no new installs)

| Tool | Version | Path | Purpose |
|------|---------|------|---------|
| Snakemake | 7.32.4 (Python 3.11) | `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` | DAG + LSF dispatch | `[VERIFIED: --version + path]` |
| R / Rscript | la_multitrait_r env | `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript` | SuSiE-RSS fitter, coloc.susie, all figures, all R aggregators | `[VERIFIED: ls]` |
| pandoc | 3.x in la_multitrait_r | `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/pandoc` | Wave 7 submission bundle PDF render | `[VERIFIED: ls]` |
| LSF (bsub / bjobs) | 10.1 | `/usr/local/lsf/10.1/...` | Job submission | `[VERIFIED: which bsub on this node 2026-04-29]` |
| `susieR` | per la_multitrait_r yaml lock | (R lib) | Used by `run_susie_rss.R` (`susieR::susie_rss`, `susieR::susie_get_cs`, `susieR::kriging_rss`). | `[VERIFIED: source code grep]` |
| `coloc` | per la_multitrait_r yaml lock | (R lib) | `coloc::coloc.susie`, `coloc::runsusie`, `coloc:::annotate_susie`. | `[VERIFIED: source code grep]` |

**Key R libraries used in Wave 5 aggregators / figures:** `data.table`, `tidyverse` (dplyr/readr/tibble/ggplot2), `jsonlite`, `patchwork` (figure composition), `optparse` (CLI parsing). All ship with `la_multitrait_r`.

### Repo-internal infrastructure (reusable; no new code)

| Asset | Purpose | Re-use in this phase |
|-------|---------|----------------------|
| `bin/fire_phase2_stage2_refit.sh` | Stage 2 production-fire LSF driver pattern | Wave 1 + Wave 2 derive from this (proven 2026-04-22). `[CITED: file content]` |
| `scripts/fire_identity_ld_rerun.sh` | Two-phase Snakemake fire with `--cluster bsub_wrapper.sh --jobs 50 --use-conda`; uses overlay yaml | Wave 1 (L-sweep) + Wave 4 (cache re-fire) directly mirror this pattern. `[VERIFIED: file content]` |
| `config/pipeline_identity_overlay.yaml` | Overlay-yaml pattern that re-bases `results_root` + `ld_reference` to a parallel namespace | **Critical precedent:** Wave 1 should create `config/susie_policy_L15.yaml` / `_L20.yaml` / `_L30.yaml` as policy overlays + a parallel-output overlay yaml for `results_lsweep_L{15,20,30}/` to avoid clobbering `results/fine_mapping/susie/*.fit.rds`. `[VERIFIED: file content]` |
| `config/bsub_wrapper.sh` | LSF queue + walltime + GB-mem dispatcher | Used by `--profile config/cluster_lsf`. `[VERIFIED: file content]` |
| `config/cluster_lsf/config.yaml` | Snakemake LSF profile — `--cluster "config/bsub_wrapper.sh -q ..."`, `jobs: 1024`, `latency-wait: 120`, `use-conda: true` | Wave 4 dispatch via `--profile config/cluster_lsf -j 50 --keep-going --rerun-incomplete --use-conda --conda-prefix .snakemake/conda` (mirrors fire_identity_ld_rerun pattern). `[VERIFIED: file content]` |
| `bin/build_track_a_submission_bundle.sh` | 488-line bundle builder; 5-engine PDF chain (xelatex → lualatex → pdflatex → tectonic → weasyprint → HTML fallback); MIT + CC-BY-4.0 licenses; ORCID-as-TODO | Wave 6 renames to `bin/build_id_vs_ref_ld_submission_bundle.sh`; Wave 7 fires the renamed script. `[VERIFIED: file content]` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff (chosen path) |
|------------|-----------|------------------------|
| `--profile config/cluster_lsf` | Hand-rolled `bsub` per task | Snakemake profile is the proven path; `bin/fire_phase2_stage2_refit.sh` did NOT use direct `bsub` per task — it used `$SMK --profile config/cluster_lsf`. `[VERIFIED]` Wave 1 + Wave 2 + Wave 4 use Snakemake profile. |
| Per-L policy YAML overlays (Wave 1) | Add `--L` CLI flag to `run_susie_rss.R` | YAML overlay reuses the existing `--policy` flag with zero code change. `[VERIFIED: lines 237-238]` Code change is rejectable as scope-creep. |
| Append to `results/multitrait/coloc_summary.tsv` (Wave 2) | Parallel-output `coloc_summary_R2.tsv` | The Stage 2 md5 byte-identical preservation rule (invariant 5) makes parallel-output the safer default for Wave 2. Wave 5 then re-renders the canonical `coloc_summary.tsv` from the merged manifest as part of the explicit cache-refresh fan-out. |

---

## Architecture Patterns

### Recommended layout (no changes; existing layout is correct)

```
coloc_analysis/
├── Snakefile                      # top-level; includes src/snakemake/rules/*.smk
├── config/
│   ├── pipeline.yaml              # paths.results_root, paths.ld_reference, traits, ancestries, finemap.{methods,output_dir}
│   ├── susie_policy.yaml          # SuSiE L (10) + max_iter ladder + min_abs_corr sweep
│   ├── pipeline_identity_overlay.yaml  # PRECEDENT: parallel-output overlay
│   ├── bsub_wrapper.sh            # LSF dispatcher (NOT bin/bsub_wrapper.sh — CONTEXT.md path is wrong)
│   └── cluster_lsf/
│       └── config.yaml            # Snakemake LSF profile
├── src/
│   ├── snakemake/
│   │   ├── rules/                 # finemap.smk, qtl_coloc.smk, multitrait.smk, coloc.smk, ...
│   │   └── scripts/               # run_qtl_coloc.R, run_coloc_susie.R (Phase-2 R)
│   ├── legacy/region_analysis/scripts/
│   │   └── run_susie_rss.R        # Phase-1 SuSiE-RSS fitter (NOT scripts/R/run_susie_rss.R)
│   ├── R/
│   │   ├── aggregators/           # aggregate_table1_pleiotropic_loci.R, aggregate_table3_admissible_pairs.R, aggregate_per_trait_pair_and_hubs.R
│   │   └── figures/               # fig1a_pipeline_schematic.R, fig1b_locus_panels.R, fig2_cs_yield.R, fig3_sh2b3_eur_collapse_forest.R, fig5_variant_mech_scorecard.R, fig_h3_ld_overlap_dose_response.R, fig_s2_paired_fit_structural_inflation.R
│   └── python/
│       ├── aggregate_qtl_coloc.py
│       ├── aggregate_pathway_results.py
│       ├── aggregate_coloc_manifest_errors.py
│       └── ... (~50 other Track-B-aimed scripts)
├── bin/
│   ├── fire_phase2_stage2_refit.sh
│   └── build_track_a_submission_bundle.sh   # → renamed at Wave 6
├── scripts/
│   ├── fire_identity_ld_rerun.sh   # PRECEDENT for Wave 1 + Wave 4 driver
│   ├── run_ci_smoke.sh
│   └── subset_toy_loci.py
├── results/
│   ├── fine_mapping/susie/         # 192 files (96 .json + 96 .fit.rds)
│   ├── multitrait/
│   │   ├── coloc_manifest.tsv      # 28-row Stage 2 manifest (md5 verifiable)
│   │   ├── coloc_summary.tsv       # md5: 5fa3c4004970c5da711d05947cb1f7d2
│   │   └── coloc_susie/            # 28 per-pair JSONs
│   ├── qtl_coloc/                  # 1,274 per-attempt JSONs (cache invalidation target)
│   └── track_a_aggregations/       # Wave 5 outputs (TSVs Track A bundle ships)
├── results_identity_ld/             # gitignored per DEC-2026-04-25-01
└── .planning/
    ├── amendments/
    │   ├── TRACK-A-FROZEN-NUMBERS.md
    │   ├── TRACK-A-AUDIT-RESPONSE-2026-04-26.md
    │   ├── TRACK-A-PIVOT.md         # → renamed at Wave 6
    │   └── osf_deviations.md        # DOES NOT YET EXIST; Wave 7 creates
    └── phases/ta-sh2b3-canonical-and-cache-refresh/
```

`[VERIFIED: ls + Snakefile read 2026-04-29]`

### Pattern 1: Two-phase Snakemake fire with parallel-output overlay (Wave 1 + Wave 4)

**What:** Run Snakemake against the canonical Snakefile but redirect outputs to a parallel namespace via an overlay YAML. Avoids clobbering existing artifacts; preserves Stage 2 md5 byte-identical invariant.

**When to use:** Any time you need to fire the same DAG against varied inputs (different L, different LD reference, different cache state) without overwriting frozen outputs.

**Example (precedent: `scripts/fire_identity_ld_rerun.sh` lines 19-30):**

```bash
#!/bin/bash
set -euo pipefail
cd /rs1/researchers/c/ckclinto/coloc_analysis        # D-TA-01 canonical path

SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
CONFIGS=(--configfile config/pipeline.yaml --configfile config/pipeline_lsweep_L20_overlay.yaml)
CLUSTER=(--cluster "config/bsub_wrapper.sh" --jobs 50 --keep-going --rerun-incomplete
         --use-conda --conda-prefix .snakemake/conda --latency-wait 120)

$SMK "${CONFIGS[@]}" "${CLUSTER[@]}" -s Snakefile \
  results_lsweep_L20/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json \
  results_lsweep_L20/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.json \
  results_lsweep_L20/fine_mapping/susie/stroke.EUR.SH2B3_12q24.json
```

The overlay YAML rebases `paths.results_root` + `finemap.output_dir` per the `pipeline_identity_overlay.yaml` precedent.

**Anti-pattern to avoid:** Modifying `config/susie_policy.yaml`'s `susie.L` in-place between fires — race-prone on multi-terminal staging; breaks the precedent of overlay-yaml isolation.

### Pattern 2: SuSiE policy override via `--policy` (Wave 1 L-sweep mechanism)

**What:** `run_susie_rss.R` accepts `--policy <yaml>` (default `config/susie_policy.yaml`) at line 237. To do an L-sweep, create three new policy YAMLs at `config/susie_policy_L15.yaml`, `_L20.yaml`, `_L30.yaml` (each = a copy of `susie_policy.yaml` with only `susie.L` differing), and pass them via the per-L overlay yaml.

**Example (one-time policy YAML scaffold):**

```yaml
# config/susie_policy_L20.yaml — Wave 1 L-sweep override (D-TA-02)
# Copy of config/susie_policy.yaml with susie.L: 20.
# Used by Wave 1 driver script via:
#   snakemake --configfile config/pipeline_lsweep_L20_overlay.yaml
# where pipeline_lsweep_L20_overlay.yaml sets:
#   finemap:
#     policy: "config/susie_policy_L20.yaml"
susie:
  L: 20
  coverage: 0.95
  max_iter_primary: 100
  max_iter_retry: 200
  ld_regularization_eps: 1.0e-4
  min_abs_corr_default: 0.5
  min_abs_corr_sweep: [0.1, 0.5, 0.9]
  min_ld_overlap: 50
  min_ld_coverage: 0.5
  min_ld_min_use: 10
  l_saturation:
    action: flag
    supplementary_rerun_L: 30
  convergence_failure:
    action: retry_ladder
    ladder:
      - increase_max_iter
      - regularize_ld
      - flag_and_exclude_tier1
complex_regions: {}   # inherit from parent (or copy verbatim if parent merge isn't transitive)
```

**Caveat (LOW confidence):** The `finemap.smk` rule uses `policy="config/susie_policy.yaml"` as a hard-coded `input` (line 70-71 of `finemap.smk`). If Snakemake's config-merge does NOT propagate `finemap.policy` overrides into the rule's `input`, the planner needs option (b): patch `finemap.smk` to read `config["finemap"].get("policy", "config/susie_policy.yaml")`. **Wave 0 task should test this with a single-locus dry-run before committing to the overlay strategy.** `[ASSUMED: behavior of Snakemake config override on rule inputs]`

### Pattern 3: `checkpoint:human-verify` task (Wave 3 outcome gate)

**What:** GSD's `checkpoint:human-verify` task type pauses execute-phase and prompts the user via AskUserQuestion-equivalent. The plan annotates the task so the executor stops and waits for Carter input.

**Example annotation** (recommended PLAN.md task shape; verify exact GSD-task-type tokens at planning time):

```yaml
- id: W3-T1
  type: checkpoint:human-verify
  title: "BMI–HTN canonical PP.H4 outcome branch (D-TA-WAVE3-OUTCOME-XX)"
  inputs:
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json   # Wave 2 output
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__hypertension_vs_stroke.json
  prompt: |
    Inspect Wave-2 BMI–HTN PP.H4 (and the other 8 SH2B3 EUR pairs). Choose branch:
      (a) collapse  PP.H4 < 0.5
      (b) partial   PP.H4 ∈ [0.5, 0.8)
      (c) survive   PP.H4 ≥ 0.8
    Record the choice as D-TA-WAVE3-OUTCOME-XX in CONTEXT.md addendum.
  records_decision_in: .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md
  blocks: [W4-*, W5-*, W6-*]   # nothing fires until decision recorded
```

**Decision recording:** Append `D-TA-WAVE3-OUTCOME-XX` as a new sub-section under `<decisions>` in `ta-sh2b3-CONTEXT.md`. NOT a separate file. `[ASSUMED: GSD convention; verify with planner agent]`

### Pattern 4: LIVE-block update in `TRACK-A-FROZEN-NUMBERS.md` (Wave 5)

**What:** The frozen-numbers file uses **H2-section markers `## ...— LIVE`** (no `<!-- LIVE-BLOCK-START -->` / `<!-- LIVE-BLOCK-END -->` sentinels). Update mechanism: identify the affected `## ... — LIVE` section by header, replace its body in-place via Edit tool (NOT sed; whitespace-fragile + atomic-commit-friendly).

**Existing LIVE blocks (verified 2026-04-29 grep):**

```
L10:  ## Stage 2 fine-mapping yield (post-k2d full-coverage identity-LD comparator, 2026-04-25) — LIVE
L30:  ## H3 LD-reference-quality dose-response (post-wa2 H3 figure, 2026-04-26) — LIVE
L58:  ## Paired-fit structural inflation (Figure S2, 2026-04-27) — LIVE
L83:  ## Pre-bioRxiv placeholder-fill (2026-04-27) — LIVE
L226: ## Negative-control behavior (post-t9j HLA reclassification 2026-04-26) — LIVE
```

**Wave 5 must update:** L10 (51/96 → updated value if D-TA-Wave1-headline branch (a) recompute fires), L30 (32/1274 → post-refresh `success` count), L83 (28 attempted → updated count if Wave 2 appended new pairs; PP.H4 columns now non-empty for the 9 new SH2B3 EUR pairs).

`[VERIFIED: grep on TRACK-A-FROZEN-NUMBERS.md 2026-04-29]`

### Anti-Patterns to Avoid

- **Don't run Snakemake from miniconda3 base.** Always use `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake`. The base env has Python 3.13; Snakemake 7.32.4 needs 3.11. Source: `feedback_no_conda.md` + `project_python_311_pin.md`.
- **Don't `git add .` or `git add -A` on GPFS.** Multi-terminal collisions baked the rule on 2026-04-28. Always pass explicit file paths.
- **Don't tell user to `conda activate`.** Use absolute env paths.
- **Don't modify `results/multitrait/coloc_summary.tsv` in-place during Wave 2.** Stage-2 md5 byte-identical preservation invariant. Wave 2 writes to a parallel surface (e.g., `results/multitrait/coloc_susie_R2/`) and Wave 5 explicitly merges + re-renders.
- **Don't pre-write Wave-6 narrative against an anticipated Wave-3 branch.** Invariant 2 — narrative writes ONLY in Wave 6 AFTER Wave-5 disk freeze.
- **Don't break the honest-framing-lock chain.** Anchor points at L148 / L295 / L220 / L90 of the manuscript file (now `id-vs-ref-LD.md` post-rename) survive Wave 6 byte-identical (line numbers may shift but content is preserved word-for-word and verified via `grep -n "anchor_phrase"` post-rename).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| LSF dispatch with proper queue + wall + mem-GB conversion | A custom bsub-wrapper script | `config/bsub_wrapper.sh` + `--profile config/cluster_lsf` | Already handles `LSF_UNIT_FOR_LIMITS=GB`, `-W` to queue max, GPFS latency-wait. `[VERIFIED]` |
| L-value override for SuSiE-RSS L-sweep | Patch `run_susie_rss.R` to take `--L` | Per-L policy YAML overlay (Pattern 1 + Pattern 2) | Reuses existing `--policy` flag; zero code change. `[VERIFIED: option_list at line 227-240]` |
| Variant-ID format diagnostic | `jq` on the JSON top-level | Rscript reading `.fit.rds` `colnames(fit$alpha)` | The JSON has CHR/POS records, not SNP_ID tokens; the variant-ID format is in the binary `.fit.rds`. `[VERIFIED: JSON inspection + run_susie_rss.R lines 510-559]` |
| Snakemake re-fire after cache invalidation | Per-target `bsub` driver | `snakemake -s Snakefile --profile config/cluster_lsf -j 50 --use-conda all_qtl_coloc` | The DAG resolves; `--rerun-triggers=mtime` (or output-removal) re-fires only what's stale. Precedent: `bin/fire_phase2_stage2_refit.sh`. `[VERIFIED]` |
| 5-engine PDF fallback chain | Custom pandoc dispatcher | Existing `bin/build_track_a_submission_bundle.sh` 5-engine chain (xelatex → lualatex → pdflatex → tectonic → weasyprint → HTML fallback) | Already handles missing engine fallback; gives HTML when no PDF engine present. `[VERIFIED: lines 70-150 of bundle script]` |
| Aggregator orchestration order | Custom workflow runner | Manual sequenced invocation per-aggregator | Wave 5 runs ~7 aggregators; topological order is documented inline (see Validation Architecture section). |

**Key insight:** Every dispatch primitive needed is already on disk and proven. The phase is wiring + sequencing, NOT new infrastructure.

---

## Runtime State Inventory

This is a refactor + rename phase that includes a state-modifying Snakemake fire. Mandatory inventory:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| **Stored data** | `results/qtl_coloc/` 1,274 per-attempt JSONs (1,005 `too_few_snps` baseline) — Wave 4 invalidation target. `results/fine_mapping/susie/` 192 files (96 .json + 96 .fit.rds) — Wave 4 SuSiE-RSS layer conditional invalidation per D-TA-04. `results/multitrait/coloc_summary.tsv` md5 `5fa3c4004970c5da711d05947cb1f7d2` — Stage 2 md5-locked; do NOT edit in-place during Wave 2 (parallel write `results/multitrait/coloc_susie_R2/` then merged at Wave 5). `[VERIFIED: file count + md5 2026-04-29]` | Wave 4 `mv` to `.preFix.bak` (always for QTL-coloc; conditional for SuSiE-RSS); Wave 5 reaggregates against post-refresh state. |
| **Live service config** | None. No Datadog / Cloudflare / external SaaS bound to this phase's rename targets. The OSF deposits at `osf.io/pvb5j` + `osf.io/az52u` are LIVE but Wave 7 only APPENDS a deviation-log entry — no rename-token propagation needed in OSF UI. | None — verified: no external systems carry the `track_a_pivot` token in user-managed configuration. |
| **OS-registered state** | None. No Windows Task Scheduler tasks; no pm2 / launchd / systemd entries; no LSF queue scheduled-task bindings tied to filenames. (Carter's interactive bash + LSF `bsub` lifecycle is not affected by file renames.) | None — verified: this is an HPC-research repo with no daemonized state. |
| **Secrets / env vars** | `SUSIE_MAX_VARIANTS` env var (consumed by `run_susie_rss.R` line 243; default 6000; Stage 2 driver sets to 16000). `LSF_UNIT_FOR_LIMITS=GB` (memory rule). `PATH` requires `/rs1/researchers/c/ckclinto/miniconda3/bin` prepended for GSD CLI per `feedback_node_path.md`. None of these reference `track_a` / `pivot` / `id-vs-ref-LD` tokens. | None — env vars unaffected by rename. |
| **Build artifacts / installed packages** | `.snakemake/conda/` env caches (per-env `.yml` hash directory) — these reference files via Snakemake's content-hash, NOT filename tokens. `results_identity_ld/` is regenerable in ~1 hr via `scripts/fire_identity_ld_rerun.sh` (DEC-2026-04-25-01). The submission bundle at commit `cacdbfe` is FROZEN; Wave 7 builds a NEW bundle from the renamed `id-vs-ref-LD.md` source. | None — no stale build artifacts triggered by the rename. The bundle build script's heredoc-generated `README.md` + `CITATION.cff` content also gets `track_a_pivot` → `id-vs-ref-LD` substitution as part of the script rename. |

**Critical gotcha:** The cache invalidation in Wave 4 itself is a stored-data state change — but D-TA-04 already covers it explicitly with `mv ... .preFix.bak` (data preservation rather than deletion).

---

## Common Pitfalls

### Pitfall 1: Wave 0 path verification fails because /rs1/... is mounted only on login02

**What goes wrong:** D-TA-01's verification command `[ -d /rs1/researchers/c/ckclinto/coloc_analysis/.git ]` returns false from the GPFS interactive shell on certain nodes.

**Why it happens:** /rs1 is the cluster-canonical research-storage mount; some interactive nodes mount it (verified: this 2026-04-29 shell does, since `/rs1/researchers/c/ckclinto/conda_envs/...` resolved). Some may not (in particular non-login compute nodes during direct SSH).

**How to avoid:** Run the verification from `login02.hpc.ncsu.edu` specifically. If `/rs1/researchers/c/ckclinto/coloc_analysis/.git` is missing on the current node, the planner records this finding and gates Wave 0 on Carter logging into login02. Note: 2026-04-29 verification shows `/rs1/researchers/c/ckclinto/conda_envs/...` is reachable from this node so /rs1 IS mounted — but `coloc_analysis` was not found. Investigate at planning time whether `/rs1/.../coloc_analysis` is a sym-link, a separate clone, or relies on a fresh `git clone` after Stage 2 commits.

**Warning signs:** `Snakemake` errors with `directory not found`; `bsub` jobs silently use the wrong working tree.

`[VERIFIED finding 2026-04-29: /rs1/researchers/c/ckclinto/coloc_analysis/.git was not found on the current GPFS node although /rs1/researchers/c/ckclinto/conda_envs/ was. Wave 0 investigation required.]`

### Pitfall 2: L-sweep policy YAML override doesn't propagate through Snakemake to `run_susie_rss.R`

**What goes wrong:** The Wave 1 driver passes `--configfile config/pipeline_lsweep_L20_overlay.yaml`, but `finemap.smk:71` hardcodes `policy="config/susie_policy.yaml"` as a rule input. Snakemake config-merge does not propagate into rule input definitions automatically.

**Why it happens:** Snakemake `--configfile` overlays affect `config[...]` references at the top of the Snakefile, NOT static input declarations inside rule bodies.

**How to avoid:** Wave 0 should include a single-locus dry-run that proves the overlay reaches `run_susie_rss.R` with the new L value. If it doesn't, two acceptable fallbacks: (a) patch `finemap.smk` line 71 to `policy=lambda wc: config["finemap"].get("policy", "config/susie_policy.yaml")` (read-only minor change; one atomic commit); (b) bypass Snakemake for Wave 1 only and call `Rscript src/legacy/region_analysis/scripts/run_susie_rss.R --policy config/susie_policy_L20.yaml ...` directly via a hand-rolled per-trait LSF driver (similar to `bin/fire_phase2_stage2_refit.sh`).

**Warning signs:** Wave 1 fits return `L_used: 10` instead of `L_used: 20` in the JSON.

`[CITED: finemap.smk lines 64-89]`

### Pitfall 3: `coloc.susie` Wave 2 attempts append to coloc_summary.tsv, breaking md5 byte-identical invariant

**What goes wrong:** `summarize_coloc_results` rule (multitrait.smk line 151) reads the `coloc_manifest.tsv` and rebuilds `coloc_summary.tsv` from per-pair `coloc_susie/{pair_id}.json` files. If Wave 2 adds 9 new pair JSONs, the next `summarize_coloc_results` run rebuilds the summary, mutating the file's bytes.

**Why it happens:** The aggregator is monolithic over the manifest; it doesn't know about R2 vs R1 pairs.

**How to avoid:** Wave 2 writes per-pair JSONs to a parallel directory `results/multitrait/coloc_susie_R2/` and updates a parallel manifest `results/multitrait/coloc_manifest_R2.tsv`. Wave 5 explicitly merges the two manifests + per-pair JSON sets and writes a new top-level summary `results/multitrait/coloc_summary.tsv` (this is THE file that updates with Wave 5 numbers; the md5 invariant is intentionally relaxed for this file in Wave 5 only). Document the exemption in Wave 5 SUMMARY.

**Warning signs:** `md5sum results/multitrait/coloc_summary.tsv` differs after Wave 2 instead of after Wave 5.

`[VERIFIED: multitrait.smk + 28 existing per-pair JSONs in coloc_susie/]`

### Pitfall 4: variant-ID diagnostic reads .json instead of .fit.rds — gives no signal

**What goes wrong:** A `jq '.variant_ids[0]'` against a SuSiE-RSS fit JSON returns null. The JSON has no `variant_ids` key; CS members are `{CHR, POS, BETA, SE, pip}` (no SNP_ID).

**Why it happens:** The R script writes the JSON via `toJSON(result, ...)` where `result.credible_sets[[paste0("CS", i)]]` = `subset[set_indices, list(CHR, POS, BETA, SE, pip = ...)]` (run_susie_rss.R line 516). SNP_ID is never in the JSON; it goes into the `.fit.rds` via `coloc:::annotate_susie(fit, snp_names, R)` (line 575) where `snp_names` is `subset$SNP_ID` if present else `chr:pos`.

**How to avoid:** Wave 0 diagnostic uses Rscript:

```bash
/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript - <<'RS'
for (path in c(
  "results/fine_mapping/susie/bmi.EUR.SH2B3_12q24.fit.rds",
  "results/fine_mapping/susie/bmi.EUR.FTO_16q12.fit.rds",
  "results/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.fit.rds")) {
  fit <- readRDS(path)
  ids <- if (!is.null(fit$alpha) && !is.null(colnames(fit$alpha))) {
    colnames(fit$alpha)
  } else if (!is.null(names(fit$pip))) {
    names(fit$pip)
  } else NULL
  ids_no_null <- ids[ids != "null"]
  fmt <- if (any(grepl("^rs[0-9]+$", ids_no_null))) {
    if (any(grepl("^[0-9XY]+:[0-9]+$", ids_no_null))) "MIXED" else "RSID"
  } else if (any(grepl("^[0-9XY]+:[0-9]+$", ids_no_null))) "CHRPOS" else "UNKNOWN"
  cat(sprintf("%s\t%s\t%s\n", path, fmt, paste(head(ids_no_null, 3), collapse=",")))
}
RS
```

Aggregate: rsid in all three → D-TA-04-DIAGNOSTIC = RSID; chr:pos in all three → CHRPOS; mixed → MIXED → CONSERVATIVE-BOTH.

**Warning signs:** Wave-0 diagnostic returns `null` (the literal string) — that means the diagnostic path is wrong; the SNP `null` is the sentinel column appended by `coloc::annotate_susie` when `n_CS < L` (run_qtl_coloc.R line 144 already handles it).

`[VERIFIED: run_susie_rss.R lines 510-583 + run_qtl_coloc.R lines 122-180]`

### Pitfall 5: Wave 4 cache invalidation backs up to wrong path (overwrite collision)

**What goes wrong:** `mv results/qtl_coloc results/qtl_coloc.preFix.bak` fails if `qtl_coloc.preFix.bak` already exists from a prior aborted attempt; or `mv` succeeds but Wave 4 Snakemake re-fires the dispatch from a non-canonical path.

**Why it happens:** Idempotent `mv` requires backup-name uniqueness across phase fires.

**How to avoid:** Use timestamped backup: `mv results/qtl_coloc results/qtl_coloc.preFix.bak.$(date +%Y%m%d_%H%M%S)`. Verify pre-existing backup directories before mv: `ls -d results/qtl_coloc.preFix.bak* 2>/dev/null`.

**Warning signs:** `mv: cannot move ... directory not empty`.

### Pitfall 6: Wave 6 rename breaks `bin/build_track_a_submission_bundle.sh` heredoc-generated content

**What goes wrong:** The bundle script has heredoc-generated `README.md` text at lines ~250-310 that hard-codes `track_a_pivot.md` and `bin/build_track_a_submission_bundle.sh` — `git mv`-ing the script doesn't auto-update its own heredoc content.

**Why it happens:** Heredocs are string literals; rename mechanics don't introspect them.

**How to avoid:** After `git mv bin/build_track_a_submission_bundle.sh bin/build_id_vs_ref_ld_submission_bundle.sh`, also do an in-place sed/Edit pass on the renamed script's heredoc to substitute `track_a_pivot.md` → `id-vs-ref-LD.md` and `build_track_a_submission_bundle.sh` → `build_id_vs_ref_ld_submission_bundle.sh`. Verify with `grep -nE "track_a_pivot|track_a_submission" bin/build_id_vs_ref_ld_submission_bundle.sh` returns 0.

**Warning signs:** Wave 7 bundle ZIP contains `manuscript/track_a_pivot.md` instead of `manuscript/id-vs-ref-LD.md`.

`[VERIFIED: lines 28, 69, 78, 137, 227-230, 250, 308-314, 475-477 of build_track_a_submission_bundle.sh]`

### Pitfall 7: Honest-framing-lock anchor line numbers shift after Wave 6 narrative edits

**What goes wrong:** Plan says "preserve L148 byte-identical." But Wave 6 narrative edits to upstream sections add lines, shifting the honest-framing-lock paragraph from L148 to L153.

**Why it happens:** Line numbers are inherently fragile under edits.

**How to avoid:** Verify by **content phrase**, not line number. E.g., `grep -nF "key honest-framing-lock phrase verbatim"` before+after the edit; require the same content at SOME line. Update the CONTEXT.md addendum with the new line numbers post-edit.

**Warning signs:** Wave 6 verification dimension fails because L148 of post-rename file has different content than pre-rename.

---

## Code Examples

Verified patterns from existing repo files.

### Wave 0: Source-repo path verification (D-TA-01)

```bash
# Run from login02.hpc.ncsu.edu
[ -d /rs1/researchers/c/ckclinto/coloc_analysis/.git ] && \
  cd /rs1/researchers/c/ckclinto/coloc_analysis && \
  git rev-parse HEAD
# Expected: SHA matching `git rev-parse HEAD` from /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
```

### Wave 0: Code-fix ancestry verification

```bash
cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
git merge-base --is-ancestor 069b34f HEAD && echo "069b34f: ancestor" || \
  echo "069b34f: NOT ancestor — cherry-pick required"
git merge-base --is-ancestor 7d54183 HEAD && echo "7d54183: ancestor" || \
  echo "7d54183: NOT ancestor — cherry-pick required"
# Verified 2026-04-29: BOTH return ancestor on current branch (HEAD = 31dae31).
```

`[VERIFIED 2026-04-29]`

### Wave 0: Variant-ID format diagnostic (D-TA-04)

(See Pitfall 4 above for the canonical Rscript snippet.)

### Wave 1: SuSiE-RSS L-sweep dispatch (mirrors fire_identity_ld_rerun.sh pattern)

```bash
#!/bin/bash
# bin/fire_susie_lsweep.sh — Wave 1 L-sweep driver (D-TA-02)
set -euo pipefail
cd /rs1/researchers/c/ckclinto/coloc_analysis        # D-TA-01

SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
LOG="logs/wave1_susie_lsweep_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs/lsf logs

# 9 fits = 3 traits × 3 L values
for L in 15 20 30; do
  echo "[$(date +%H:%M:%S)] L=${L} fire starting"
  $SMK \
    --configfile config/pipeline.yaml \
    --configfile config/pipeline_lsweep_L${L}_overlay.yaml \
    --profile config/cluster_lsf \
    --jobs 50 --keep-going --rerun-incomplete --use-conda \
    --conda-prefix .snakemake/conda --latency-wait 120 \
    -s Snakefile \
    results_lsweep_L${L}/fine_mapping/susie/bmi.EUR.SH2B3_12q24.json \
    results_lsweep_L${L}/fine_mapping/susie/hypertension.EUR.SH2B3_12q24.json \
    results_lsweep_L${L}/fine_mapping/susie/stroke.EUR.SH2B3_12q24.json \
    >> "$LOG" 2>&1
done
```

Each fit ~2-4 hr per AUDIT-RESPONSE L260 estimate; 9 fits = ~12-15 hr aggregate (parallelizable across LSF slots → wall time ~4 hr).

### Wave 1: Per-fit convergence verification (n_CS << L per Zou 2022)

```bash
/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript - <<'RS'
library(jsonlite)
fits <- list.files("results_lsweep_L20/fine_mapping/susie",
                   pattern="^(bmi|hypertension|stroke)\\.EUR\\.SH2B3_12q24\\.json$",
                   full.names=TRUE)
for (f in fits) {
  j <- jsonlite::fromJSON(f, simplifyVector=TRUE)
  cat(sprintf("%-60s L_used=%d  n_CS=%d  L_saturated=%s  conv=%s\n",
              basename(f), j$L_used,
              length(j$credible_sets), j$L_saturated, j$convergence_status))
}
RS
```

PASS criterion: every line shows `n_CS < L_used` AND `L_saturated=FALSE` AND `conv=converged_*`. Fail if `n_CS == L_used` (saturation; fall through to higher L).

### Wave 2: Canonical-pair coloc.susie LSF dispatch

The `run_coloc_susie` rule (coloc.smk line 88) requires `coloc_manifest.tsv` to enumerate `pair_id` wildcards. Strategy: **build a parallel R2 manifest** with the 9 new SH2B3 EUR pairs, then dispatch only those pair targets:

```bash
#!/bin/bash
# bin/fire_canonical_susie_pairs.sh — Wave 2 driver (D-TA-03)
set -euo pipefail
cd /rs1/researchers/c/ckclinto/coloc_analysis

# Step 0: Pin coloc_manifest_R2.tsv (9 SH2B3 EUR pairs against Wave-1 fits at primary-result-L)
# (Build script: src/python/build_coloc_manifest_r2.py — produced by Wave 2 Task 0)

SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
PAIRS=(
  SH2B3_12q24__EUR__asthma_vs_bmi
  SH2B3_12q24__EUR__asthma_vs_hypertension
  SH2B3_12q24__EUR__asthma_vs_stroke
  SH2B3_12q24__EUR__bmi_vs_hypertension
  SH2B3_12q24__EUR__bmi_vs_stroke
  SH2B3_12q24__EUR__bmi_vs_t2d
  SH2B3_12q24__EUR__hypertension_vs_stroke
  SH2B3_12q24__EUR__hypertension_vs_t2d
  SH2B3_12q24__EUR__stroke_vs_t2d
)
TARGETS=()
for p in "${PAIRS[@]}"; do
  TARGETS+=("results/multitrait/coloc_susie_R2/${p}.json")
done

$SMK \
  --configfile config/pipeline.yaml \
  --configfile config/pipeline_canonical_r2_overlay.yaml \
  --profile config/cluster_lsf \
  --jobs 50 --keep-going --rerun-incomplete --use-conda \
  --conda-prefix .snakemake/conda --latency-wait 120 \
  -s Snakefile \
  "${TARGETS[@]}"
```

Per-pair compute: ~2 hr (per AUDIT-RESPONSE 2026-04-26 estimate); 9 pairs aggregate ~18 hr LSF (parallelizable across slots → wall time ~3-4 hr).

### Wave 4: QTL-coloc cache re-fire

```bash
#!/bin/bash
# bin/fire_qtl_coloc_cache_refresh.sh — Wave 4 driver (D-TA-04)
set -euo pipefail
cd /rs1/researchers/c/ckclinto/coloc_analysis

# Backup with timestamp (Pitfall 5)
TS=$(date +%Y%m%d_%H%M%S)
mv results/qtl_coloc results/qtl_coloc.preFix.bak.${TS}

# Conditional: SuSiE-RSS layer in scope per D-TA-04-DIAGNOSTIC outcome
if [ "${SUSIE_LAYER_SCOPE:-no}" = "yes" ]; then
  mv results/fine_mapping/susie results/fine_mapping/susie.preFix.bak.${TS}
fi

SMK=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake
$SMK \
  --configfile config/pipeline.yaml \
  --profile config/cluster_lsf \
  --jobs 50 --keep-going --rerun-incomplete --use-conda \
  --conda-prefix .snakemake/conda --latency-wait 120 \
  -s Snakefile \
  --config 'phase2_enabled_sources=["gtex_eqtl","gtex_sqtl"]' \
  all_qtl_coloc
```

Compute: ~10 hr at 50 LSF cores for 1,274 QTL-coloc attempts (mirrors `bin/fire_phase2_stage2_refit.sh` envelope). +~5 hr if SuSiE-RSS layer in scope. `serial` queue 5760-min wall is ample.

### Wave 4: PASS / FAIL verification

```bash
TOO_FEW=$(grep -h '"status"' results/qtl_coloc/*.json | grep -c '"too_few_snps"')
SUCCESS=$(grep -h '"status"' results/qtl_coloc/*.json | grep -c '"success"')
NOQTLCS=$(grep -h '"status"' results/qtl_coloc/*.json | grep -c '"no_qtl_cs"')
echo "too_few_snps=$TOO_FEW (baseline 1005; PASS <= 200; FAIL ~1000)"
echo "success=$SUCCESS (baseline 32)"
echo "no_qtl_cs=$NOQTLCS (baseline 235)"
[ "$TOO_FEW" -le 200 ] && echo "PASS" || echo "FAIL — investigate Wave 4.5"
```

`[VERIFIED: aggregate_qtl_coloc.py STATUS field structure + qtl_coloc.smk rule shape]`

### Wave 6: Rename + reference fix-up enumeration

```bash
# Run from /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis (any node)
# Reference-fix-up grep ENUMERATION (post-D-TA-06 token list)

# All files referencing the manuscript path
grep -rl "track_a_pivot\.md" --include="*.R" --include="*.py" --include="*.sh" \
                              --include="*.md" --include="*.smk" --include="*.yaml" \
                              --include="*.yml" --include="*.json" --include="*.tsv"

# All files referencing the strategy-doc path
grep -rl "TRACK-A-PIVOT\.md" --include="*.R" --include="*.py" --include="*.sh" \
                              --include="*.md" --include="*.smk" --include="*.yaml"

# All files referencing the bundle build script
grep -rl "build_track_a_submission_bundle" --include="*.R" --include="*.py" \
                                            --include="*.sh" --include="*.md"
```

**Findings (verified 2026-04-29):**

- `track_a_pivot.md` referenced in: ROADMAP.md, STATE.md, DECISIONS.md, 4 amendments (TRACK-A-AUDIT-RESPONSE, AUDIT-REVIEW-2026-04-25, AUDIT-REVIEW-V2-2026-04-26, TRACK-A-FROZEN-NUMBERS, TRACK-A-PIVOT itself), 7 R figure scripts (fig1a, fig1b, fig2, fig3, fig5, fig_h3, fig_s2), 3 R aggregators (per_trait_pair_and_hubs, table1_pleiotropic_loci, table3_admissible_pairs), `bin/build_track_a_submission_bundle.sh` (lines 28, 69, 78, 137, 227-230, 250, 314, 475-477), 27 quick-task PLAN/SUMMARY files in `.planning/quick/` (commit messages — DO NOT REWRITE per memory `project_track_a_handle.md`).

- `TRACK-A-PIVOT.md` referenced in: ROADMAP.md, STATE.md, DECISIONS.md, PROJECT.md, 5 amendments (the file itself + AUDIT-REVIEW-V2 + PROJECT-AMENDMENT-2026-04-22 + TRACK-A-AUDIT-RESPONSE + AUDIT-REVIEW-2026-04-25), 7 R figure scripts (in cross-reference comment headers), 3 R aggregators, ~25 quick-task PLAN/SUMMARY files (DO NOT REWRITE).

- `build_track_a_submission_bundle` referenced in: ROADMAP.md, STATE.md, 5 quick-task PLAN/SUMMARY files (DO NOT REWRITE the historical ones), `bin/build_aou_portal_bundle.sh` (verify if it cross-refs), CONTEXT.md (this phase), DISCUSSION-LOG.md (this phase), QUESTIONS.json (this phase).

**Wave 6 plan must enumerate at minimum:**

| File | Type | Update Action |
|------|------|---------------|
| `docs/manuscript/track_a_pivot.md` → `id-vs-ref-LD.md` | rename | `git mv` |
| `.planning/amendments/TRACK-A-PIVOT.md` → `ID-VS-REF-LD-STRATEGY.md` | rename | `git mv` |
| `bin/build_track_a_submission_bundle.sh` → `build_id_vs_ref_ld_submission_bundle.sh` | rename | `git mv` + heredoc sed pass |
| 7 figure scripts in `src/R/figures/` | reference fix-up | Edit `track_a_pivot.md` → `id-vs-ref-LD.md` and `TRACK-A-PIVOT.md` → `ID-VS-REF-LD-STRATEGY.md` in comment headers |
| 3 aggregator scripts in `src/R/aggregators/` | reference fix-up | Same as above |
| `.planning/STATE.md` (forward refs only — internal "pivot" event language preserved) | reference fix-up | Update path tokens; preserve "pivot" for the 2026-04-22 strategic event |
| `.planning/DECISIONS.md` (forward refs only) | reference fix-up | Same |
| `.planning/ROADMAP.md` (forward refs only) | reference fix-up | Update path tokens |
| `.planning/PROJECT.md` (forward refs only) | reference fix-up | Update path tokens |
| `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` (CROSS-REFS, NOT THE FILE ITSELF — keep filename per D-TA-06) | reference fix-up | Update inline links from `track_a_pivot.md` → `id-vs-ref-LD.md` |
| `.planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md` | reference fix-up | Same |
| `.planning/amendments/AUDIT-REVIEW-2026-04-25.md` | reference fix-up | Same |
| `.planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md` | reference fix-up | Same |
| `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` | reference fix-up | Same |
| `.planning/quick/*-PLAN.md`, `*-SUMMARY.md` (~50 files) | **NO CHANGE** — historical record per memory `project_track_a_handle.md` | Skip; document the skip explicitly in Wave 6 SUMMARY |
| `bin/build_track_a_submission_bundle.sh` heredoc-generated `README.md` + `CITATION.cff` | embedded text | sed/Edit pass on the renamed script |

`[VERIFIED 2026-04-29: exhaustive grep results above]`

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Stage 2 fire with chr:pos-only matching breaks QTL-coloc | run_qtl_coloc.R commit `069b34f` adds chr:pos tolerance via candidate-based best-overlap match (rsid / chrpos / variant_id) | 2026-04-21 | Already in repo. The 1,005 too_few_snps results are a CACHE staleness, not a code bug. Cache invalidation alone (Wave 4) likely sufficient. |
| Sumstats SNP_ID mismatch with LD panel rsids breaks SuSiE-RSS naming | run_susie_rss.R commit `7d54183` adds LD-panel rsid override when LD has rsids and sumstats has chr:pos | 2026-04-21 | Already in repo. SuSiE-RSS layer rebuild (Wave 4 conditional) only needed if D-TA-04 diagnostic returns chr:pos or mixed format. |

**Deprecated / outdated patterns:** None relevant to this phase scope.

---

## Environment Availability

Verified 2026-04-29 from current GPFS interactive shell.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Snakemake (Python 3.11 lock) | Wave 1, 2, 4 | ✓ | 7.32.4 at `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` | — |
| Rscript (la_multitrait_r) | Wave 0, 1, 2, 5, 6, 7 | ✓ | la_multitrait_r env at `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/Rscript` | — |
| pandoc | Wave 7 bundle render | ✓ | la_multitrait_r at `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/pandoc` | — |
| LSF `bsub` / `bjobs` | Wave 1, 2, 4 dispatch | ✓ | LSF 10.1 (`/usr/local/lsf/10.1/...`) | — |
| `git merge-base`, `git mv`, `git rev-parse` | Wave 0, 6 | ✓ | system git | — |
| `069b34f` ancestor of HEAD | Wave 0 verification | ✓ (verified) | — | cherry-pick if missing |
| `7d54183` ancestor of HEAD | Wave 0 verification | ✓ (verified) | — | cherry-pick if missing |
| `/rs1/researchers/c/ckclinto/coloc_analysis/.git` | D-TA-01 path verification | **✗ from current GPFS node** (but `/rs1/.../conda_envs/...` resolves) | — | **Investigate at Wave 0**: log into login02; verify path; if missing, may need fresh clone or sym-link decision before fires can run |
| OSF web portal access | Wave 0 (D-TA-05), Wave 7 (D-TA-Cache-OSF) | (Carter only — outside Claude tooling) | — | Carter web-UI |
| PDF engine (xelatex / lualatex / pdflatex / tectonic / weasyprint) | Wave 7 bundle PDF render | (depends on env — not verified by Claude) | — | HTML fallback already wired in `build_track_a_submission_bundle.sh` |

**Missing dependencies with no fallback:** None — but the `/rs1/.../coloc_analysis` path-resolution gap is BLOCKING for D-TA-01 verification on this specific node. Wave 0 must check from login02.

**Missing dependencies with fallback:** PDF engines — bundle script already has 5-engine chain + HTML fallback. Wave 7 SUMMARY should document which engine the bundle ended up using.

---

## Validation Architecture

> Phase requires `## Validation Architecture` section per `.planning/config.json` `workflow.nyquist_validation: true`. This section enables the workflow to auto-generate VALIDATION.md.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | bash + Rscript + jq + grep — there is no `pytest`/`Rtest` testing harness for this phase scope |
| Config file | none (in-line per-task verification) |
| Quick run command | per-task — see Phase Requirements → Test Map below |
| Full suite command | `bin/verify_ta_sh2b3_phase.sh` (Wave 0 task to scaffold; runs all D1–D7 dimension checks) |
| CI smoke (existing) | `scripts/run_ci_smoke.sh` (REQ-SNAKEMAKE-CI; out-of-phase; Wave 7 SUMMARY notes if it ran clean) |

### Phase Requirements → Test Map

| Req / Claim | Behavior | Test Type | Automated Command | Expected Output | File Exists? |
|-------------|----------|-----------|-------------------|----|---|
| **C1**: D-TA-01 path verified | `/rs1/.../coloc_analysis/.git` HEAD matches GPFS HEAD | smoke | `[ -d /rs1/researchers/c/ckclinto/coloc_analysis/.git ] && cd /rs1/researchers/c/ckclinto/coloc_analysis && git rev-parse HEAD` | matches `git -C /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis rev-parse HEAD` | ⚠️ Wave 0 (path may need investigation) |
| **C2**: 069b34f + 7d54183 ancestors of HEAD | Code fixes already landed | unit | `git merge-base --is-ancestor 069b34f HEAD && git merge-base --is-ancestor 7d54183 HEAD` | exit 0 | ✓ verified 2026-04-29 |
| **C3**: D-TA-04 diagnostic outcome recorded | Variant-ID format = rsid / chrpos / mixed | unit | `Rscript Wave-0 diagnostic snippet` (Pitfall 4) → grep result; record in CONTEXT addendum as `D-TA-04-DIAGNOSTIC-XX` | one of {RSID, CHRPOS, MIXED} per fit; aggregate decision recorded | ⚠️ Wave 0 |
| **C4**: D-TA-05 OSF coverage verified | OSF deposit at osf.io/pvb5j or osf.io/az52u contains L-sweep + canonical-pair pre-reg phrases | smoke + manual | Carter web-UI grep for "L-sweep", "{15, 20, 30}", "L = 20", "canonical pair", "BMI-HTN", "HTN-stroke"; record outcome in `D-TA-OSF-COVERAGE-XX` | covered → Wave 1 cleared; uncovered → amendment first | ⚠️ Wave 0 (Carter only) |
| **C5**: SuSiE-RSS converges at chosen L for SH2B3 EUR BMI/HTN/stroke | Per-fit `n_CS << L` AND `L_saturated=FALSE` AND `convergence_status` matches `^converged_` | unit | `Rscript Wave-1 convergence verification snippet` | per-fit JSON shows `n_CS < L_used` with `L_saturated: false` and `convergence_status: "converged_*"` | ⚠️ Wave 1 |
| **C6**: BMI–HTN reference-LD coloc.susie produced | `results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json` exists with finite PP.H4 | unit | `jq '.summary."PP.H4.abf"' results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json` | numeric in [0, 1] | ⚠️ Wave 2 |
| **C7**: All 9 SH2B3 EUR new pairs produced | 9 per-pair JSONs exist | unit | `ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json \| wc -l` | 9 | ⚠️ Wave 2 |
| **C8**: D-TA-WAVE3-OUTCOME recorded | Branch (a/b/c) decision in CONTEXT.md addendum | manual | `grep "D-TA-WAVE3-OUTCOME-" .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` | matches one of `BRANCH_A_COLLAPSE`, `BRANCH_B_PARTIAL`, `BRANCH_C_SURVIVE` | ⚠️ Wave 3 |
| **C9**: Cache refresh produces materially different numerics | post-Wave-4 `too_few_snps` ≤ 200 (PASS) | unit | `grep -h '"status"' results/qtl_coloc/*.json \| grep -c '"too_few_snps"'` | ≤ 200 (target); FAIL ≈ 1000 → Wave 4.5 SuSiE-RSS layer fallback | ⚠️ Wave 4 |
| **C10**: Wave-5 aggregator outputs refreshed against post-cache-refresh disk | `results/track_a_aggregations/qtl_coloc_status_distribution.tsv` (and Table 1 / Tier-A / Pathway / Fig S7 underlying TSV) post-Wave-4-refresh have updated mtimes vs pre-Wave-4 | unit | `stat -c '%Y' results/track_a_aggregations/*.tsv` newer than `stat -c '%Y' results/qtl_coloc/*.json` median | TSV mtime > JSON mtime; values consistent with `aggregate_qtl_coloc.py` logic | ⚠️ Wave 5 |
| **C11**: TRACK-A-FROZEN-NUMBERS LIVE block updated | The L10 Stage-2 LIVE block reflects post-Wave-1 numerator decision (51/96 OR recomputed value) | unit | `grep -A 20 "Stage 2 fine-mapping yield" .planning/amendments/TRACK-A-FROZEN-NUMBERS.md` | block reflects D-TA-Wave1-headline outcome | ⚠️ Wave 5 |
| **C12**: Stage 2 md5 invariant preserved on non-target files | `md5sum results/multitrait/coloc_summary.tsv` differs only at intentional Wave-5 update; all other file md5s unchanged | unit | `md5sum results/qtl_coloc/qtl_coloc_manifest.tsv results/fine_mapping/finemap_manifest.tsv` (pre vs post phase, both should change ONLY where intentional) | per-file md5 diff matches a curated whitelist of files this phase rewrites | ⚠️ Wave 7 final check |
| **C13**: Manuscript anchors at L148/L295/L220/L90 preserved byte-identical | Content phrases at the 4 honest-framing-lock anchor points exist in `docs/manuscript/id-vs-ref-LD.md` post-rename | unit | `grep -nF "<honest-framing-lock anchor phrase>" docs/manuscript/id-vs-ref-LD.md` returns same content (line number may shift; content exact match required) | each of 4 anchor phrases returns ≥ 1 hit | ⚠️ Wave 6 |
| **C14**: Bundle is reproducible and clean | `unzip -t track_a_genome_medicine_submission.zip` clean; SHA-256 of bundle archive recorded in manifest | unit + smoke | `unzip -t <bundle.zip>` AND `sha256sum <bundle.zip>` | exit 0 + sha256 hash captured in `bundle_manifest.tsv` | ⚠️ Wave 7 |
| **C15**: OSF deviation log entry added | `.planning/amendments/osf_deviations.md` exists and contains an entry dated 2026-04-XX-XX with cache-invalidation discovery+rationale+commit pointers | unit | `grep -E "Cache invalidation|2026-04-(28\|29)" .planning/amendments/osf_deviations.md` | ≥ 1 entry block | ⚠️ Wave 7 (file does NOT exist yet — Wave 7 task creates) |

### Sampling Rate

- **Per task commit:** Run the targeted unit check from the table above (the C-row matching the task).
- **Per wave merge:** Run all C-rows for that wave + the cumulative Stage-2 md5 check (C12).
- **Phase gate (Wave 7 closeout):** Full C1–C15 sweep + manuscript-anchor preservation re-verify + bundle integrity check.

### Wave 0 Gaps

- [ ] `bin/verify_ta_sh2b3_phase.sh` — Wave-0 scaffold script that runs all C1–C15 checks and emits PASS/WARN/FAIL JSON. Aligns with phase verification dimensions D1–D7.
- [ ] `config/susie_policy_L15.yaml`, `_L20.yaml`, `_L30.yaml` — three policy YAML overlays for Wave 1 (per-L override).
- [ ] `config/pipeline_lsweep_L{15,20,30}_overlay.yaml` — three pipeline overlays that point `finemap.policy` at the per-L susie YAML AND rebase `paths.results_root` to `results_lsweep_L{15,20,30}/`. (Verify Snakemake config-merge propagation per Pitfall 2 first.)
- [ ] `config/pipeline_canonical_r2_overlay.yaml` — Wave 2 overlay that rebases `MULTITRAIT_DIR` to `results/multitrait/coloc_susie_R2/`.
- [ ] `bin/fire_susie_lsweep.sh` — Wave 1 driver script (mirror `scripts/fire_identity_ld_rerun.sh` pattern).
- [ ] `bin/fire_canonical_susie_pairs.sh` — Wave 2 driver.
- [ ] `bin/fire_qtl_coloc_cache_refresh.sh` — Wave 4 driver.
- [ ] `src/python/build_coloc_manifest_r2.py` — manifest builder that emits the 9-row R2 manifest (filtered slice of `create_coloc_manifest.py` output).
- [ ] `.planning/amendments/osf_deviations.md` — Wave 7 task creates (does not yet exist).

---

## Security Domain

**Skipping** (`security_enforcement` not configured in `.planning/config.json`). The phase scope is academic-research code on a controlled HPC cluster with public data — no auth, session, network-perimeter, or input-validation surfaces are introduced. This is consistent with project precedent (no security domain in prior Track A phases).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| **A1** | Wave-1 L-sweep can be implemented via per-L policy YAML overlays without modifying `run_susie_rss.R` or `finemap.smk`. | Pattern 2 / Pitfall 2 | If Snakemake config-merge does NOT propagate `--configfile` overrides into rule-input declarations, the planner needs option (b): patch `finemap.smk` to read `lambda wc: config["finemap"].get("policy", "config/susie_policy.yaml")`. Either fallback works; cost is 1 extra sub-task in Wave 1. **Wave 0 dry-run mitigates.** |
| **A2** | The GSD `checkpoint:human-verify` task type pauses execute-phase and stores the user's branch decision in CONTEXT.md addendum (not a separate file). | Pattern 3 | If the GSD convention is different (e.g., emits a separate `D-TA-WAVE3-OUTCOME.md`), the planner uses that pattern instead. Cosmetic difference; no scientific impact. |
| **A3** | The OSF deposits at `osf.io/pvb5j` (Methods) and `osf.io/az52u` (closeout PDF) already cover D-TA-02 (L-sweep) and D-TA-03 (canonical-pair scope). | D-TA-05 | Per AUDIT-RESPONSE 2026-04-26 line 269, HQ#2(iii) is "pre-registered in TRACK-A-FROZEN-NUMBERS.md"; the L-sweep wording is already in the Methods §Fine-Mapping Configuration of the in-tree draft. If OSF deposits don't carry these phrases, Carter posts an amendment (~30 min web-UI). Either way, Wave 0 D-TA-05 verification gates Wave 1. |
| **A4** | The Wave 4 cache invalidation produces `too_few_snps ≤ 200` PASS criterion. | C9 / Wave 4 PASS | The 1,005 baseline could be partly cache staleness (resolved by re-fire) AND partly genuine `too_few_snps` from regions with sparse QTL coverage. If the genuine-failure floor is higher than 200, the criterion may need recalibration with disclosure. **Wave 4 SUMMARY documents the actual outcome regardless of pass/fail.** |
| **A5** | The Wave 7 bundle build script's heredoc-generated `README.md` content for `Track A genome medicine submission` text only references the renamed paths after the heredoc + sed Wave-6 task. | Pitfall 6 | If Wave 6 misses a heredoc reference, Wave 7 bundle ZIP will contain stale path mentions (visible to journal reviewers). Wave 6 verification dimension D5 catches this with a `grep "track_a_pivot\|build_track_a_submission_bundle"` on the renamed bundle script returning 0. |
| **A6** | `/rs1/researchers/c/ckclinto/coloc_analysis/.git` is reachable from login02 even though it didn't resolve from this 2026-04-29 GPFS shell node. | D-TA-01, Pitfall 1 | If `/rs1/.../coloc_analysis` doesn't exist anywhere on the cluster, Carter must `git clone` to that path (one-time, ~10 min). Wave 0 task picks this up before Wave 1 fires. |
| **A7** | The GSD-task type for parallel-output build (Wave 6 R2-manifest fanout vs Stage-2-manifest preservation) does not require special infrastructure — it's just an additional Snakemake `--configfile` overlay. | Pattern 1, Wave 2 dispatch | Standard Snakemake config-overlay pattern; precedent in `pipeline_identity_overlay.yaml`. Low risk. |
| **A8** | Wave 7's PDF engine fallback chain still works in 2026-04. | Pitfall 7 | The pandoc-engine availability is environment-specific; if all 5 engines fail, the script falls through to HTML — already tested in commit `cacdbfe` produced `track_a_pivot.html` + `minimal.css` per CONTEXT.md (HTML fallback is the existing default behavior). |

**Note: This table flags items the planner / Carter should explicitly verify or accept as risk before execution. None of these would change the locked decisions in CONTEXT.md.**

---

## Open Questions

1. **Does `/rs1/researchers/c/ckclinto/coloc_analysis/` exist on login02 (and is it the same git tree as the GPFS interactive mount)?**
   - What we know: `/rs1/researchers/c/ckclinto/conda_envs/...` resolves from this 2026-04-29 GPFS shell. The `coloc_analysis` subdirectory does NOT resolve from the same shell.
   - What's unclear: Whether `/rs1/.../coloc_analysis/.git` exists on login02 only, or whether the path needs creation via fresh clone.
   - Recommendation: Wave 0 includes an `ssh login02 '[ -d /rs1/.../coloc_analysis/.git ]'` check; if false, Carter is prompted to either `git clone` or symlink GPFS path → /rs1/... This is a Wave-0 Carter-mediated investigation, not a Claude-resolvable item.

2. **Does the Snakemake `--configfile` overlay correctly propagate `finemap.policy` to the `run_finemap` rule's `policy` input?**
   - What we know: `finemap.smk:71` declares `policy="config/susie_policy.yaml"` as a static rule input (not config-driven).
   - What's unclear: Whether `finemap.policy: config/susie_policy_L20.yaml` in the overlay yaml will reach the rule's `--policy` flag substitution at line 91.
   - Recommendation: Wave 0 task — single-locus dry-run of the L=20 overlay; verify the produced JSON's `L_used` field equals 20. If 10, fall back to patching `finemap.smk` line 71-72 to be config-aware.

3. **What is the canonical path for the GSD-task `checkpoint:human-verify` decision recording?**
   - What we know: CONTEXT.md says "Decision recorded as `D-TA-WAVE3-OUTCOME-XX` in CONTEXT.md addendum after Wave 2 completes."
   - What's unclear: Whether GSD's executor agent appends a CONTEXT.md addendum directly or writes to a sibling decision file.
   - Recommendation: Planner agent verifies with the GSD framework convention; defaults to in-place CONTEXT.md append in `<decisions>` section under a new `### D-TA-WAVE3-OUTCOME` heading.

4. **Does `bin/build_aou_portal_bundle.sh` reference `build_track_a_submission_bundle`?**
   - What we know: Grep showed `bin/build_aou_portal_bundle.sh` in the rename-reference list.
   - What's unclear: Whether the reference is a comment or an `exec`-able line.
   - Recommendation: Wave 6 includes a manual inspection of `bin/build_aou_portal_bundle.sh` for any cross-bundle dependency; update if found.

---

## Sources

### Primary (HIGH confidence — read directly 2026-04-29)

- `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` (full read; 443 lines; 13 locked decisions)
- `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-DISCUSSION-LOG.md` (full read; option-by-option audit trail)
- `.planning/ROADMAP.md` lines 314-462 (phase scope + invariants + suggested wave structure)
- `.planning/REQUIREMENTS.md` (REQ-PUBLIC-DATA-ONLY, REQ-SUSIE-RSS-POLICY, REQ-PP.H4-THRESHOLD-SWEEP, REQ-OSF-PREREG, REQ-SNAKEMAKE-CI, REQ-PATH-PARAMETERIZATION)
- `.planning/STATE.md` (lines 1-80; pivot context + Stage 2 fire numerics)
- `.planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md` (lines 240-330; HQ#2(i)/(ii)/(iii) DEFERRED-COMPUTE/DESIGN closure framing)
- `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` (lines 1-100; LIVE-block schema and locked scalars)
- `CLAUDE.md` (project constraints)
- `.planning/config.json` (workflow.nyquist_validation: true)
- `Snakefile` (lines 1-212; rule wiring + ALL_TARGETS + all_qtl_coloc)
- `src/snakemake/rules/finemap.smk` (rule run_finemap structure; --policy flag inspection)
- `src/snakemake/rules/qtl_coloc.smk` (rules + QTL_COLOC_OUTPUTS + manifest pattern)
- `src/snakemake/rules/multitrait.smk` (rule build_coloc_manifest + run_multitrait_placeholder + summarize_coloc_results)
- `src/snakemake/rules/coloc.smk` (rule run_coloc_susie at line 88)
- `src/snakemake/scripts/run_qtl_coloc.R` (lines 1-280; chr:pos tolerance + best-overlap match)
- `src/legacy/region_analysis/scripts/run_susie_rss.R` (lines 1-660; option_list + L_DEFAULT loading + credible_sets serialization + annotate_susie)
- `config/bsub_wrapper.sh` (full content)
- `config/cluster_lsf/config.yaml` (Snakemake LSF profile)
- `config/susie_policy.yaml` (full content; L: 10 default; min_abs_corr_sweep)
- `config/pipeline_identity_overlay.yaml` (full content; PRECEDENT for parallel-output overlay)
- `bin/fire_phase2_stage2_refit.sh` (full content; Stage 2 driver pattern)
- `scripts/fire_identity_ld_rerun.sh` (full content; two-phase Snakemake fire pattern)
- `bin/build_track_a_submission_bundle.sh` (lines 1-310; bundle build flow + heredoc README)
- 4 SuSiE-RSS sample fits: `results/fine_mapping/susie/{bmi,hypertension,stroke}.EUR.SH2B3_12q24.json` and `bmi.EUR.FTO_16q12.json` (top-level keys, credible_sets schema, L_used, convergence_status)
- 7 R figure scripts in `src/R/figures/` (cross-reference scan)
- 3 R aggregator scripts in `src/R/aggregators/` (cross-reference scan)
- `src/python/aggregate_qtl_coloc.py` (lines 1-100)

### Secondary (MEDIUM confidence — confirmed by multiple sources)

- LSF queue / wall / mem rules (memory `feedback_lsf_queues.md` + verified in `config/bsub_wrapper.sh`)
- Conda env paths for la_multitrait_r + smoke_dev (memory pins + verified by `ls`)
- Honest-framing-lock anchor enumeration (memory `feedback_original_research_framing.md` + CONTEXT.md L83-91)
- AUDIT-RESPONSE 2026-04-26 line 260 wall-time estimate (~2-4 hr per fit)

### Tertiary (LOW confidence — flagged with `[ASSUMED]` in body)

- GSD task-type convention for `checkpoint:human-verify` (verified pattern with GSD planner agent at planning time)
- Snakemake config-merge propagation behavior into static rule inputs (verified with Wave 0 dry-run before Wave 1 commits)

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — every binary/library/conda env verified by direct ls/--version on 2026-04-29
- Architecture (paths + dispatch patterns): HIGH — 100% verified via direct file reads (Snakefile + .smk + R + bash)
- Pitfalls: HIGH for #1, #3, #4, #6 (verified by direct code inspection); MEDIUM for #2 (Snakemake config-merge behavior is an assumption tested by Wave 0 dry-run); HIGH for #5, #7
- Validation Architecture: HIGH for C1-C7, C9-C15 (test commands derived from existing tooling); MEDIUM for C8 (depends on GSD checkpoint convention)
- Honest-framing-lock anchor enumeration: HIGH (verified by exhaustive grep 2026-04-29; ~50 quick-task files identified as DO-NOT-REWRITE; 17 forward-facing files identified for Wave 6 reference fix-up)
- Rename-reference enumeration: HIGH (exhaustive grep verified; complete file table in Code Examples / Wave 6 section)

**Research date:** 2026-04-29
**Valid until:** 2026-05-15 (16 days; while phase remains in active planning + execution; treat as stale if any of the locked decisions revisited or if Snakemake config-merge propagation tested with new outcome)

---

*Researcher: gsd-researcher (Claude Opus 4.7 1M)*
*For phase: ta-sh2b3-canonical-and-cache-refresh*
*Next: `/gsd-plan-phase ta-sh2b3-canonical-and-cache-refresh`*
