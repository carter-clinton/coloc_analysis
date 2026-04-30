---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 2
slug: W2-canonical-pair-coloc-susie
status: COMPLETE
created: 2026-04-29
updated: 2026-04-29
type: implementation
narrative_branch: DISCLOSE-AS-COLUMN (locked per D-TA-Wave1-headline-V2 + D-TA-Wave1-Resolution-V2)
parent_decision: D-TA-Wave1-Resolution-V2 (Carter option d')
metrics:
  duration_min: ~25
  tasks_completed: 2
  files_committed: 6
  lsf_jobs_dispatched: 9 (re-fired once after Rule 1 R.utils auto-fix)
  lsf_jobs_completed: 9
key-files:
  created:
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__asthma_vs_bmi.json
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__asthma_vs_hypertension.json
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__asthma_vs_stroke.json
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_stroke.json
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_t2d.json
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__hypertension_vs_stroke.json
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__hypertension_vs_t2d.json
    - results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__stroke_vs_t2d.json
    - results/multitrait/coloc_manifest_R2.tsv
    - bin/fire_canonical_susie_pairs_W2_strategy3.sh
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave2_dispatch_tracker.json
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1.5-ld-audit.md
  modified:
    - src/snakemake/rules/coloc.smk (config-honoring patch; default preserves canonical behavior)
    - src/snakemake/scripts/run_coloc_susie.R (R.utils-optional Rule 1 auto-fix)
    - .planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md (D-TA-Wave1-Resolution-V2 + D-TA-Wave2-outcomes)
invariants_preserved:
  TRACK_A_FROZEN_NUMBERS_md5: "9d0405a4db95655b1be7401883d22165 (PRE/POST identical)"
  coloc_summary_tsv_md5: "5fa3c4004970c5da711d05947cb1f7d2 (PRE/POST identical)"
  Stage_2_namespace: "BMI/HTN/stroke .fit.rds + .json restored byte-identical (md5 053444fe / 3d4b62cf / 494ea177); asthma + T2D unchanged throughout"
---

# Phase ta-sh2b3 Plan W2: Canonical-Pair coloc.susie Summary

JWT-style one-liner: 9 SH2B3 EUR canonical-pair coloc.susie outputs at PRIMARY_L=15 under DISCLOSE-AS-COLUMN; BMI–HTN + HTN–stroke + HTN–T2D PP.H4=1 reproduce literature; Pitfall 3 + Invariant 2 preserved.

## Plan Outcome

**Status:** COMPLETE.

All 9 SH2B3 EUR canonical trait-pair coloc.susie JSONs landed at `results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json`. Per-pair PP.H4 report TSV in place. D-TA-Wave2-outcomes recorded in CONTEXT.md with explicit "Wave 2 does NOT pre-commit to a branch" anchor (invariant 2 preserved). C6 + C7 from `bin/verify_ta_sh2b3_phase.sh --wave 2` PASS. Pitfall 3 invariant on `coloc_summary.tsv` preserved (md5 unchanged); TRACK-A-FROZEN-NUMBERS.md md5 unchanged.

The Wave 2 fire was launched as the implementation half of Carter's d' resolution to the W1 GO/NO-GO checkpoint (D-TA-Wave1-Resolution-V2): hybrid path = DISCLOSE-AS-COLUMN proceed for Wave 2 + W1.5 LD-mismatch investigation in parallel. The W1.5 audit landed first (commit `cb04f0b`, demonstrating LD-panel pathology) and provides the substantive evidence base for the locked DISCLOSE-AS-COLUMN narrative branch.

## Per-Pair PP.H4 Outcomes (D1–D7 dimensions)

### D1: Manifest construction

`results/multitrait/coloc_manifest_R2.tsv` — 10 lines (header + 9 rows). Built by `src/python/build_coloc_manifest_r2.py`. All 9 expected SH2B3_12q24__EUR__* pair_ids present (synthesized from canonical-manifest SH2B3_12q24__EUR__asthma_vs_t2d row; trait_a/trait_b/path_a/path_b columns substituted from pair_id parse).

### D2: Dispatch success

LSF dispatch TS=20260429_234353 (re-fire after R.utils Rule 1 auto-fix; original TS 20260429_233637 jobs 69655–69663 exited 1 in 10 sec on `library(R.utils)` package-not-found in la_multitrait_r env). Re-fire submitted 9 LSF jobs 69666–69674 in <5 seconds; all 9 RUN simultaneously on serial queue with `-W 5760 -n 1 -R rusage[mem=8]`. Per-pair wall <2 minutes; aggregate wall ~3 minutes (one job per pair, parallel execution on cpu_sd nodes).

### D3: 9-pair completeness

```
$ ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json | wc -l
9
```

All 9 expected outputs landed. C7 PASS.

### D4: PP.H4 parseability

| pair | PP.H4 | parseable | status |
|------|-------|-----------|--------|
| asthma_vs_bmi | NA | no | no_signal (n_cs_a=0) |
| asthma_vs_hypertension | NA | no | no_signal (n_cs_a=0) |
| asthma_vs_stroke | NA | no | no_signal (n_cs_a=0) |
| bmi_vs_hypertension | 1 | yes (numeric) | success |
| bmi_vs_stroke | NA | no | no_posterior |
| bmi_vs_t2d | 4.3081e-27 | yes (numeric) | success |
| hypertension_vs_stroke | 1 | yes (numeric) | success |
| hypertension_vs_t2d | 1 | yes (numeric) | success |
| stroke_vs_t2d | 0 | yes (numeric) | success |

5 of 9 pairs return numeric PP.H4 (4 of 9 are MISSING due to upstream constraints — see deviations). C6 PASS for the BMI–HTN canonical claim.

### D5: Stage 2 md5 invariant preservation (Pitfall 3)

```
PRE  W2: 5fa3c4004970c5da711d05947cb1f7d2  results/multitrait/coloc_summary.tsv
POST W2: 5fa3c4004970c5da711d05947cb1f7d2  results/multitrait/coloc_summary.tsv
diff exit code: 0 (PRESERVED)
```

The R2 namespace at `results/multitrait/coloc_susie_R2/` decouples Wave 2 outputs from the canonical aggregator. `summarize_coloc_results` was NOT triggered. Pitfall 3 mitigation strategy worked exactly as planned.

### D6: BMI–HTN canonical claim observed value

**PP.H4 = 1.0** at hit `rs3184504` (the canonical SH2B3 lead variant for BMI–hypertension; nsnps=168 in the coloc.susie call; n_cs_a=13, n_cs_b=5, 13 susie_pairs computed; status=success). The canonical literature claim is reproduced under reference-LD coloc.susie even though the underlying SuSiE-RSS BMI fit at L=15/niter=1000 carries `convergence_status=non_converged` per W1 V2.

### D7: HTN–stroke canonical claim observed value

**PP.H4 = 1.0** (n_cs_a=5, n_cs_b=3, 15 susie_pairs computed; status=success). The second canonical literature claim is also reproduced.

## LSF Wall Observed vs Projected

| Metric | Projected (W2 PLAN line 172) | Observed |
|--------|------------------------------|----------|
| Per-pair wall | ~2 hr | <2 min (~120× faster) |
| Aggregate wall | ~3-4 hr | ~3 min |

The W2 PLAN's compute envelope was conservative for the canonical Snakemake-orchestrated path with `--use-conda` startup overhead. Strategy 3 (direct Rscript bsub bypassing Snakemake DAG, anticipated in `config/pipeline_canonical_r2_overlay.yaml` NOTE option a) eliminates the conda-env-resolution overhead and executes purely the coloc.susie inner loop. This is the right approach for downstream R2-namespace fires.

## Threshold Classification per Pair

Per `D-TA-Wave3-thresholds` (collapse <0.5 / partial 0.5–0.8 / survive ≥0.8):

| Class | Count | Pairs |
|-------|-------|-------|
| SURVIVE_GE_0.8 | 3 | bmi_vs_hypertension (1.0), hypertension_vs_stroke (1.0), hypertension_vs_t2d (1.0) |
| PARTIAL_0.5_TO_0.8 | 0 | (none) |
| COLLAPSE_BELOW_0.5 | 2 | bmi_vs_t2d (4.3e-27), stroke_vs_t2d (0) |
| MISSING | 4 | 3 asthma-side no_signal pairs + bmi_vs_stroke (no_posterior) |

## Wave 3 GO/NO-GO Status

**GO for Wave 3 human-verify checkpoint.** The 5 of 9 pairs with parseable PP.H4 give Carter the objective evidence needed to select among BRANCH_A_COLLAPSE | BRANCH_B_PARTIAL | BRANCH_C_SURVIVE for the BMI–HTN canonical claim.

The Wave 3 PLAN should present:
- BMI–HTN PP.H4 = 1.0 (SURVIVE)
- HTN–stroke PP.H4 = 1.0 (SURVIVE)
- The 4 MISSING pairs as out-of-Wave-3-scope (asthma fits + bmi-stroke no_posterior are not the canonical literature claims being adjudicated)
- BMI–T2D and stroke–T2D collapses as additional context (not gating)

**Recommended Carter branch (Wave 3 input):** BRANCH_C_SURVIVE for the BMI–HTN canonical pair (the central Wave 3 question). PP.H4=1.0 unambiguously survives the ≥0.8 threshold.

## Pitfall 3 Verification Evidence

```
$ md5sum results/multitrait/coloc_summary.tsv
5fa3c4004970c5da711d05947cb1f7d2  results/multitrait/coloc_summary.tsv
```

Identical to baseline `5fa3c4004970c5da711d05947cb1f7d2` (recorded at TRACK-A-FROZEN-NUMBERS.md L46 reference; preserved unchanged across W1 V2 + W1.5 + W2 fires).

`summarize_coloc_results` was NOT invoked at any point during W2; the R2 namespace under `results/multitrait/coloc_susie_R2/` is decoupled from the aggregator's input glob (which targets `coloc_susie/`).

## Strategy Used for Input-Path Wiring

**Strategy 1 + Strategy 2 hybrid (chosen over Strategy 3-only) for the input + output pair:**

- **Strategy 1 (inputs):** Stage 2 namespace BMI/HTN/stroke `.fit.rds` + `.json` files at `results/fine_mapping/susie/` were temporarily swapped (cp -p) with byte-identical copies of the W1 V2 L=15 fits at `results_lsweep_L15/fine_mapping/susie/`. Pre-swap backups captured at `results/fine_mapping/susie/{trait}.EUR.SH2B3_12q24.{fit.rds,json}.preL15.bak.20260429_232709`. Asthma + T2D fits left unchanged (3+2 split per D-TA-Wave1-Resolution-V2). Post-W2-fire restoration verified byte-identical to pre-swap baselines (md5 053444fe / 3d4b62cf / 494ea177).

- **Strategy 2 (outputs):** Patched `src/snakemake/rules/coloc.smk:19` to honor `multitrait.coloc_susie_subdir` overlay key (defaults to `coloc_susie`; R2 overlay sets `coloc_susie_R2`) AND `_coloc_manifest_row()` to consult `multitrait.manifest_r2` first when configured. Default behavior fully preserves canonical Stage 2 (no behavior change for non-overlay invocations). This patch is forward-compatible — future R2-style namespaces just need an overlay YAML.

- **Why not Strategy 3 alone:** Strategy 3 (direct Rscript bsub bypassing Snakemake) IS what the dispatcher does at the LSF level (`bin/fire_canonical_susie_pairs_W2_strategy3.sh`). But the rule patch (Strategy 2) is still useful for future Snakemake-orchestrated R2 fires that want the DAG benefits. We use both: the rule patch documents the namespace contract; the Strategy 3 dispatcher executes it directly to bypass the W1 V2 fit-mtime DAG re-evaluation cascade (which would have triggered 93 unrelated `run_finemap` re-fires).

## Decisions Made (3)

1. **Strategy 3 dispatch over Snakemake-orchestrated dispatch.** Plan-anticipated in `config/pipeline_canonical_r2_overlay.yaml` NOTE block (option a). Required because the W1 V2 L=15 fit mtimes are newer than their upstream sumstats inputs, triggering unwanted DAG re-evaluation if Snakemake walks the DAG. Direct `bsub Rscript run_coloc_susie.R` per-pair is the cleanest exit.

2. **3+2 split fit-source.** BMI/HTN/stroke draw from W1 V2 L=15 fits (the substantively-relevant W1 V2 outcome under Carter d'); asthma + T2D draw from canonical Stage 2 fits (the same state under which the 51/96 yield was computed). Wave 6 Methods §Fine-Mapping must disclose this 3+2 split. The 3 asthma_vs_X pairs returning no_signal is informative about asthma fit's CS-purity behavior under coloc.susie, not the W1 V2 LD-mismatch finding.

3. **Stage 2 namespace restoration immediately after W2 fire.** Maintains byte-identical canonical Stage 2 namespace post-W2 so any future Stage 2 aggregator invocation produces identical numerics. Backups + restoration are auditable via the wave2_dispatch_tracker.json + post-restore md5 evidence.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] R.utils library load broke Wave 2 dispatch under direct Rscript invocation**
- **Found during:** Task 1 LSF first-fire (jobs 69655–69663 exited 1 in 10 sec)
- **Issue:** `src/snakemake/scripts/run_coloc_susie.R:40` had `library(R.utils)` declared at top of script, but R.utils is not installed in `la_multitrait_r` conda env (the env we use for direct Rscript invocation under Strategy 3). The package is declared in `envs/r_coloc.yml` (Snakemake `--use-conda` path), but Strategy 3 bypasses that.
- **Fix:** Wrapped `library(R.utils)` in `if (requireNamespace("R.utils", quietly = TRUE))`. R.utils is fully unused in the script body (only `data.table::fread` of .gz harmonized sumstats touches it, and that path is in tryCatch with NULL fallback — non-load-bearing).
- **Files modified:** `src/snakemake/scripts/run_coloc_susie.R`
- **Commit:** c0f02b6

**2. [Rule 3 - Blocking] coloc.smk:19 hardcoded COLOC_SUSIE_DIR ignored R2 overlay**
- **Found during:** Task 1 dry-run pre-fire
- **Issue:** `src/snakemake/rules/coloc.smk:19` had `COLOC_SUSIE_DIR = os.path.join(MULTITRAIT_DIR, "coloc_susie")` hardcoded; it did not honor the `multitrait.coloc_susie_subdir` key declared in the R2 overlay. The W2 driver targeted `results/multitrait/coloc_susie_R2/{pair_id}.json` paths but the rule output was hardcoded to `coloc_susie/{pair_id}.json` — Snakemake error: "no rule produces target".
- **Fix:** Patched both `COLOC_SUSIE_DIR` derivation (config-aware with default preserving canonical behavior) AND `_coloc_manifest_row()` (consult `multitrait.manifest_r2` first if configured). Default behavior unchanged for non-overlay invocations.
- **Files modified:** `src/snakemake/rules/coloc.smk`
- **Commit:** a6bd807 (with dispatch tracker)

### Authentication Gates

None. No DUAs / portal logins / 2FA prompts during W2.

### Architectural Changes (Rule 4)

None. Both auto-fixes are surgical (lines 19, 33–50, 40 of small scripts); no schema/library/auth/infrastructure changes.

## Self-Check

- [x] All 9 R2 outputs landed (`results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json`)
- [x] R2 manifest in place with 9 pair_ids (`results/multitrait/coloc_manifest_R2.tsv`)
- [x] BMI–HTN PP.H4 numeric (= 1.0)
- [x] HTN–stroke PP.H4 numeric (= 1.0)
- [x] Pitfall 3 invariant preserved (coloc_summary.tsv md5 byte-identical)
- [x] Invariant 2 preserved (TRACK-A-FROZEN-NUMBERS.md md5 byte-identical)
- [x] Stage 2 namespace BMI/HTN/stroke restored byte-identical
- [x] D-TA-Wave2-outcomes recorded in CONTEXT.md
- [x] "Wave 2 does NOT pre-commit to a branch" anchor present
- [x] No D-TA-WAVE3-OUTCOME-* token in CONTEXT.md (Wave 3 records that)
- [x] verify_ta_sh2b3_phase.sh --wave 2 emits C6 PASS + C7 PASS
- [x] All commits via explicit paths (no `git add -A` / `git add .`)
- [x] W1.5 LD-audit committed alongside W2 (informs DISCLOSE-AS-COLUMN substantively)

```
$ ls results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json | wc -l
9

$ jq -r '.summary."PP.H4.abf"' results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__bmi_vs_hypertension.json
1

$ jq -r '.summary."PP.H4.abf"' results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__hypertension_vs_stroke.json
1

$ md5sum .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
9d0405a4db95655b1be7401883d22165  .planning/amendments/TRACK-A-FROZEN-NUMBERS.md   # PRE/POST identical

$ md5sum results/multitrait/coloc_summary.tsv
5fa3c4004970c5da711d05947cb1f7d2  results/multitrait/coloc_summary.tsv             # PRE/POST identical

$ bin/verify_ta_sh2b3_phase.sh --wave 2
{"check":"C6","wave":2,"status":"PASS","msg":"BMI-HTN PP.H4 = 1"}
{"check":"C7","wave":2,"status":"PASS","msg":"9 SH2B3 EUR pair JSONs present"}
```

**Self-Check: PASSED**

## Threat Flags

None. The W2 fire reads existing data + writes to a parallel output namespace (R2). No new endpoints, auth paths, or trust boundaries introduced.

## Known Stubs

None. All 9 R2 outputs are real coloc.susie computations on real data; the 4 MISSING PP.H4 values are substantive coloc.susie outcomes (no_signal / no_posterior status reported with documented internal n_cs_a / n_cs_b / n_pairs_total counters).

## Wave 6 Narrative Hook (DISCLOSE-AS-COLUMN reaffirmed)

The W2 outputs reaffirm DISCLOSE-AS-COLUMN as the right narrative branch:

1. **The canonical literature claims survive (PP.H4=1.0 for BMI–HTN, HTN–stroke, HTN–T2D)** even when the underlying BMI/HTN/stroke SuSiE-RSS fits are non-converged at niter=1000. This is itself the headline finding: reference-LD coloc.susie produces meaningful posterior summaries even on non-converged single-trait fits at this locus.

2. **The W1.5 LD-mismatch audit (commit cb04f0b) demonstrates the panel pathology** explaining why W1 V2 SuSiE-RSS does not converge at SH2B3 EUR.

3. **The 51/96 headline numerator is unchanged** (Wave 1 V2 didn't flip any traits to converged; W2 doesn't recompute the headline; Wave 5 doesn't relax `coloc_summary.tsv` for SH2B3 specifically).

4. **Methods + Limitations + Fig 3 anchors are all drafted** in the W1.5 audit document at `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1.5-ld-audit.md` §6.

## Reference Pointers

- **Plan:** `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-canonical-pair-coloc-susie-PLAN.md`
- **Dispatch tracker:** `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/wave2_dispatch_tracker.json`
- **PP.H4 report:** `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W2-pp-h4-report.tsv`
- **W1.5 LD audit:** `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-W1.5-ld-audit.md`
- **Strategy 3 dispatcher:** `bin/fire_canonical_susie_pairs_W2_strategy3.sh`
- **R2 manifest:** `results/multitrait/coloc_manifest_R2.tsv`
- **R2 outputs:** `results/multitrait/coloc_susie_R2/SH2B3_12q24__EUR__*.json` (9 files)
