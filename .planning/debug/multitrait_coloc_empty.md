---
session: multitrait_coloc_empty
status: fixed
opened: 2026-04-21
closed: 2026-04-21
stage: recovery_plan_stage_1
parent_plan: .planning/phases/02-3-way-qtl-colocalization/RECOVERY_PLAN.md
hypothesis: Label-mismatch bug between run_susie_rss.R (writes status="ok") and filter_finemap_summary.py (filters on status=="success"), PLUS latent coloc.smk schema mismatch (row["region"] vs manifest's "base_region").
next_action: None (Stage 1 resolved; Stage 1b carryover noted below).
---

## Current Focus

hypothesis: run_susie_rss.R line 622 overwrites the success-path status label from "success" → "ok" (introduced by commit f2c46dd, the REQ-2 policy refactor). Downstream filter_finemap_summary.py still expects "success" (lines 129 and 364). Result: every converged fit is marked as tier-ineligible regardless of credible-set content. tier1/tier2/tier3 all empty. coloc_manifest empty. coloc_summary empty.
test: Apply min fix to filter_finemap_summary.py to accept status ∈ {"success","ok"}; re-run filter_finemap_summary rule; confirm tier3 file populates; re-run build_coloc_manifest; confirm manifest populates; run run_coloc_susie + summarize_coloc_results; verify coloc_summary.tsv > 1 byte.
expecting: tier3 should yield ≥ 50 rows (all 50 "ok" fits); coloc_manifest should yield trait-pair × region combinations; coloc_summary should yield non-empty JSON summary TSV.
next_action: Edit filter_finemap_summary.py; re-run rule chain; verify.

## Symptoms

expected: `results/multitrait/coloc_summary.tsv` populated with one row per trait-pair × region from build_coloc_manifest. `assign_tiers.py` then joins QTL coloc onto trait-pair coloc to produce Tier A/B/C assignments.

actual: `results/multitrait/coloc_summary.tsv` is 1 byte. `coloc_manifest.tsv` is 73 bytes (header only). `results/multitrait/coloc/` directory does not exist — run_coloc_pair never fired. `tier_assignments.tsv` shows 0 Tier A / 0 Tier B / 0 Tier C. assign_tiers.py (commit 8fcade7) logged "GWAS coloc file is empty (0 bytes)".

errors: No Snakemake errors. The manifest builder appears to have run (produced a header-only file), then summarize_coloc_results produced a 1-byte empty file because there were no per-pair JSONs to concatenate.

reproduction: 2026-04-20 first-production run via `bin/fire_phase2_patha.sh`. Post-run: `wc -c results/multitrait/coloc_summary.tsv` = 1.

started: First production run of Phase 2 — this pipeline has never produced non-empty multitrait coloc output. Confirmed structural, not regression.

## Evidence

- timestamp: 2026-04-21 step 1 (upstream gate check)
  checked: `results/fine_mapping/finemap_tier3_coloc.tsv`
  found: 1 line total (header only), 376 bytes — zero tier3-eligible fits
  implication: The upstream gate that should drive trait-pair coloc is structurally empty.

- timestamp: 2026-04-21 step 1 (adjacent tier files)
  checked: `results/fine_mapping/finemap_tier1_high_conf.tsv`, `finemap_tier2_relaxed.tsv`
  found: Both are 359 bytes = header-only (zero tier1 and tier2 fits)
  implication: All three tier gates are empty. Confirms the 12/96 credible-set-bearing SuSiE yield from the 2026-04-20 session note was insufficient to populate any tier.

- timestamp: 2026-04-21 step 2 (manifest check)
  checked: `results/multitrait/coloc_manifest.tsv`
  found: 73 bytes, header line only: `base_region  ancestry  trait_a  trait_b  path_a  path_b  chr  start  end  pair_id`
  implication: build_coloc_manifest executed but emitted zero data rows — consistent with empty tier3 gate.

- timestamp: 2026-04-21 step 3 (run_coloc_pair outputs)
  checked: `results/multitrait/coloc/`
  found: Directory does not exist
  implication: No run_coloc_pair jobs ever fired in this run. Mode C (per-pair JSONs with errors) is ruled out.

- timestamp: 2026-04-21 step 1b (finemap_summary tally)
  checked: `awk` tally of credible_sets column in raw finemap_summary.tsv
  found: 37 / 96 fits have credible_sets > 0 (NOT 12 as earlier session note suggested). status tally: ok=50, too_many_variants=40, no_variants=6.
  implication: SuSiE yield is sufficient for trait-pair coloc (50 status=ok fits, 37 with credible sets). The empty tier files are NOT a yield problem.

- timestamp: 2026-04-21 step 5 (multitrait.smk audit)
  checked: `src/snakemake/rules/multitrait.smk` lines 76-95 (build_coloc_manifest), 151-167 (summarize_coloc_results)
  found: build_coloc_manifest takes `tier3=FINEMAP_DIR/finemap_tier3_coloc.tsv` as required input and passes it as --tier3 to create_coloc_manifest.py. summarize_coloc_results reads coloc_manifest.tsv and glob's results/multitrait/coloc_susie/*.json.
  implication: Confirmed the gate chain: finemap_tier3_coloc.tsv → coloc_manifest.tsv → per-pair JSONs → coloc_summary.tsv. Breaking at step 1 cascades all the way down.

- timestamp: 2026-04-21 step 5b (filter_finemap_summary.py audit)
  checked: `src/legacy/region_analysis/scripts/filter_finemap_summary.py` lines 108-158, 364
  found: _evaluate_tier() line 129 asserts `status_val != "success"` appends "status!=success" issue to tier1 and tier2. Line 364: `tier3_pass = row.get("status", "").lower() == "success"`.
  implication: All three tier gates require status == "success" (case-insensitive in tier3, exact in tier1/tier2). The filter has no "ok" fallback path.

- timestamp: 2026-04-21 step 5c (run_susie_rss.R audit)
  checked: `src/legacy/region_analysis/scripts/run_susie_rss.R` lines 495-629
  found: Line 505 initially sets `status = "success"` in the result list at the successful-fit exit point. Line 622 then OVERWRITES it: `result$status <- if (grepl("non_converged", convergence_status)) "non_converged" else "ok"`. The JSON written on line 629 thus has status="ok", never "success".
  implication: Root cause is the tail-overwrite on line 622 of run_susie_rss.R (introduced by commit f2c46dd, the REQ-2 policy refactor). Every successful fit now writes status="ok" to its JSON, which propagates into finemap_summary.tsv, where it is rejected by filter_finemap_summary.py's "success" check. This is NOT a yield problem; it is a label-contract breakage between two scripts in different commits.

- timestamp: 2026-04-21 step 5d (grep for other "success" consumers)
  checked: `grep -rn 'status.*success' src/`
  found: 9 additional files expect status=="success": cross_ancestry_compare.py:196-198, replication_compare.py:177-179, plot_additional_panels.R:141, plot_additional_figures.R:52, build_a_list_pip_summary.py:52, run_qtl_coloc.R:389 (writes), run_coloc_susie.R:155 (writes), run_matched_coloc.R:88,118 (writes+reads).
  implication: The "success" status contract is load-bearing across the codebase; run_susie_rss.R is the only SuSiE-path writer that violates it. Ideal fix would be to revert line 622 in run_susie_rss.R to preserve status="success" — but that requires re-running all 96 SuSiE jobs, which is out of scope for Stage 1 (explicitly forbidden by the Recovery Plan scope block). Minimum in-scope fix: accept status in {"success","ok"} in filter_finemap_summary.py. This unblocks Stage 1 and leaves the upstream-label issue as a tech debt item to be addressed alongside a legitimate Phase 1 re-run.

## Eliminated

- hypothesis: Mode B (Snakemake DAG never requested coloc_summary.tsv target)
  evidence: `results/multitrait/coloc_summary.tsv` exists with 1 byte (not absent) AND `results/multitrait/coloc_manifest.tsv` exists with header-only content. If the target had not been requested, neither output would exist. The rule chain (build_coloc_manifest → run_coloc_susie → summarize_coloc_results) clearly ran; it simply had nothing to do.
  timestamp: 2026-04-21 step 2-3

- hypothesis: Mode C (run_coloc_susie fired but produced empty/error JSONs)
  evidence: `results/multitrait/coloc_susie/` directory does not exist. Snakemake's `run_coloc_susie` rule would create this directory if it fired even once. Zero pair jobs were attempted.
  timestamp: 2026-04-21 step 3

- hypothesis: Mode A (SuSiE credible-set yield cascade)
  evidence: SuSiE yield is 50/96 status=ok fits and 37/96 with credible sets — sufficient for tier3. The problem is NOT that SuSiE under-produced; it is that filter_finemap_summary.py's "success" check rejects status="ok" output labels. The 2026-04-20 session note's "12/96 credible sets" number appears to have been derived from a stricter criterion than raw credible_sets > 0, but the actual 37/96 yield is more than sufficient to populate tier3 if the label check matched.
  timestamp: 2026-04-21 step 5c

## Resolution

root_cause: Three coupled defects prevented trait-pair coloc from producing any output on the 2026-04-20 first-production run:

1. **Label-contract breakage in the tier3 gate** (primary root cause).
   - `src/legacy/region_analysis/scripts/run_susie_rss.R:622` overwrites `result$status` from `"success"` → `"ok"` immediately before the JSON is written (introduced by commit `f2c46dd`, REQ-2 policy refactor).
   - `src/legacy/region_analysis/scripts/filter_finemap_summary.py:129,364` gates tier1/tier2/tier3 membership on `status == "success"`.
   - Consequence: all 96 SuSiE JSONs carry status="ok"; all three tier files get zero data rows; `finemap_tier3_coloc.tsv` is header-only; `build_coloc_manifest` emits zero trait-pair rows; `summarize_coloc_results` produces a 1-byte file.

2. **Schema mismatch in coloc.smk input function** (latent, surfaced by fix 1).
   - `src/snakemake/rules/coloc.smk:80` reads `row["region"]` but `create_coloc_manifest.py` emits `base_region`, not `region`. Every per-pair DAG resolution KeyErrors. Masked until now because the manifest was empty — no pair_ids meant no input-function calls.

3. **Missing fire-script target** (latent DAG reachability gap).
   - `bin/fire_phase2_patha.sh` only requested `all_qtl_coloc` + `null_loci_summary.tsv`. `coloc_summary.tsv` is in `ALL_TARGETS` (Snakefile:181) but is not in the `all_qtl_coloc` closure, so it was never reachable from the fire-script entry points. Adding it explicitly ensures future fires produce the trait-pair summary.

fix:
- **filter_finemap_summary.py:129,364** — accept status ∈ {"success","ok"} (min-blast-radius fix; avoids re-running SuSiE which is out of Stage 1 scope).
- **coloc.smk:80** — read `row["base_region"]` instead of `row["region"]` to match the manifest schema emitted by `create_coloc_manifest.py`.
- **bin/fire_phase2_patha.sh:31-37** — add `results/multitrait/coloc_summary.tsv` to the explicit target list.

verification:
- `wc -l results/multitrait/coloc_summary.tsv` = 55 (1 header + 54 data rows). File size = 4000 bytes (was 1 byte). **PASS** verification_target criterion #1.
- `python src/python/assign_tiers.py --input results/qtl_coloc/qtl_coloc_summary.tsv --gwas-coloc results/multitrait/coloc_summary.tsv --pph4-config config/pph4_thresholds.yaml --output /tmp/tier_assignments.tsv --sweep --sweep-output /tmp/pph4_sweep.tsv` does NOT emit the "GWAS coloc file is empty" warning. **PASS** verification_target criterion #2. (It still errors on a separate pre-existing column-name mismatch; see Stage 1b below.)
- Tier breakdown after re-run: tier1=2 rows, tier2=4 rows, tier3=50 rows (all converged ok fits now eligible for coloc, from 0 previously). Coloc manifest contains 58 trait-pair × region combinations across 8 base_regions × 2 ancestries (46 EUR, 12 AFR).
- Snakemake run: 54/58 pair JSONs landed (51 "no_signal" pre-check-gated, 3 "success" with usable summaries including SH2B3_12q24__EUR__hypertension_vs_stroke with PP.H4=1.0). 4 hard-errored inside `coloc.susie()` due to a cross-trait SNP naming mismatch (see Stage 1b carryover).

files_changed:
- src/legacy/region_analysis/scripts/filter_finemap_summary.py (2 edits: line 129, line 364)
- src/snakemake/rules/coloc.smk (1 edit: line 80)
- bin/fire_phase2_patha.sh (1 edit: add coloc_summary.tsv target)

## Stage 1b Carryover (Non-Blocking; Surfaced During Verification)

These defects are out of Stage 1 scope per the Recovery Plan but are now visible because the upstream gate is no longer masking them. Surfacing them here so downstream stages can address them in order.

**1. Cross-trait SNP naming drift inside coloc.susie (4 hard failures).**
   - `run_susie_rss.R:520-529` selects SNP names conditionally: rsid if `SNP_ID` column is populated, else `chr:pos`. Each trait/region fit makes this choice independently. Pairs where the two traits disagree (e.g., bmi fit uses rsids, hypertension fit uses chr:pos in the same APOE_19q13 region) produce `lbf_variable` matrices with zero overlapping colnames. `coloc::coloc.bf_bf` then returns `data.table(nsnps=NA)` without a `$summary` field, and `coloc::coloc.susie` line 22 errors on `ret$summary[, :=(...)]` against NULL.
   - Affected pairs on the 2026-04-20 snapshot: APOE_19q13__EUR__bmi_vs_hypertension, FTO_16q12__EUR__bmi_vs_t2d, SH2B3_12q24__EUR__bmi_vs_hypertension, SH2B3_12q24__EUR__bmi_vs_stroke.
   - Analogous to commit `931a9c8` (qtl_coloc_snp_name_mismatch). Fix: harmonize SNP names in a shared coordinate system before coloc.susie — either force chr:pos naming in `run_susie_rss.R` (consistent across traits by construction) OR adopt a rsid-aware variant alignment step in `run_coloc_susie.R`. Either fix requires re-running affected Phase 1 SuSiE fits OR a Phase 2 coloc re-pair, which are Stage 2/3 scope.

**2. Column-name contract drift between summarize_coloc_results.py and assign_tiers.py.**
   - `summarize_coloc_results.py:97,101-102` writes `base_region`, `PP.H3`, `PP.H4`.
   - `assign_tiers.py:146,161,199` expects `region`, `PP.H4.abf`.
   - Result: `assign_tiers.py` now proceeds past the empty-file check (verification_target criterion #2 MET) but errors downstream with `KeyError: 'region'` during the GWAS groupby. Either rename columns in `summarize_coloc_results.py` (preferred; legacy consumers elsewhere expect `PP.H4.abf`/`region`) or add an alias in `assign_tiers.py`. The scope block forbids "Change `assign_tiers` logic" so the fix belongs in the summarizer — tracked as Stage 1b.

**3. DAG wiring: summarize_coloc_results does not declare per-pair JSONs as inputs.**
   - `src/snakemake/rules/multitrait.smk:151-167` declares only `coloc_manifest.tsv` as input. Snakemake does not backward-chain to materialize the per-pair JSONs before running the summarizer. On this fire I worked around this by explicitly requesting the 58 pair targets before the summary target.
   - Fix: add an input function that expands over pair_ids from the manifest (similar to the existing `stroke_afr_coloc_targets` helper in the same file) and wires `results/multitrait/coloc_susie/{pair_id}.json` as inputs. Small edit but borderline Stage-1 scope; deferred.

**4. Upstream-label hygiene: run_susie_rss.R line 622 still downgrades status.**
   - The `filter_finemap_summary.py` fix aliases `"ok"` to match tier QC semantics, but 9 other consumers (cross_ancestry_compare.py, replication_compare.py, plot_additional_panels.R, plot_additional_figures.R, build_a_list_pip_summary.py) still filter on exact `"success"` match and will silently drop all rows until they receive analogous aliases OR `run_susie_rss.R` is fixed to preserve `status="success"` (requires Phase 1 re-run, out of Stage 1 scope).
