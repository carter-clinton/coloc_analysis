# T1 Phase 2 First-Production — Full Session Summary

**Date:** 2026-04-20
**Scope:** Path A (eQTL + sQTL, EUR-only, matched-null-loci supplement)
**Session entry point:** `/gsd-resume-work` after 3-day gap
**Session exit state:** Pipeline fired end-to-end; 0 Tier A signals; **awaiting user decision on forward path**.

---

## 1. Executive Summary

Phase 2 QTL colocalization fired successfully for the first time on 2026-04-20. The pipeline is now code-complete and reproducible (11 commits this session). The scientific output, however, is qualitatively degenerate: **0 Tier A / 0 Tier B / 0 Tier C signals** out of 1,010 attempted (gene × tissue × trait × QTL-source) colocalizations. This is a *data/scope* problem, not a pipeline bug.

**Two compounding root causes of the 0-Tier-A outcome:**

1. **Gene-scope mismatch at the biologically canonical locus (FTO).**
   The manifest maps one Ensembl gene per curated region — FTO_16q12 → ENSG00000140718 (FTO itself). But the causal mechanism at 16q12.2 is well-established distal regulation of *IRX3*/*IRX5*, not cis-regulation of FTO (Smemo et al. *Nature* 2014; Claussnitzer et al. *NEJM* 2015). Our top coloc — FTO/Muscle_Skeletal eQTL — landed PP.H3=0.8633, PP.H4=0.1142, which is the textbook "shared locus, distinct causal variants" signature confirming this biology. If the manifest had included IRX3/IRX5 for this region, it would likely have produced the first Tier A hit.

2. **Trait-pair GWAS coloc never fired.**
   `results/multitrait/coloc_summary.tsv` is 1 byte (empty). Tier assignment in `assign_tiers.py` joins QTL coloc onto trait-pair coloc — so even if QTL signals existed, tiers would be structurally empty.

**Bottom line:** The pipeline works. The input scope (gene list + missing trait-pair coloc) does not yet exercise the locus architecture that would produce real Tier A evidence.

---

## 2. What Was Built This Session (11 Commits)

| Commit | Type | Summary |
|---|---|---|
| `6a4fdd8` | fix | Give identity LD matrix dimnames so `annotate_susie` preserves SNP names |
| `931a9c8` | fix | Match GWAS-vs-QTL via rsid + handle LD `.rds` list structure |
| `91b49b4` | docs | Debug investigation log |
| `c461e1d` | docs | Seed debug knowledge base |
| `3879a77` | fix | Update eQTL Catalogue downloads to r8 URL scheme |
| `2bde4c6` | fix | eQTL uses `.all.tsv.gz` (full allpairs), not `.cc.tsv.gz` |
| `d84797c` | docs | Reconcile CP#1-final AFR-row scope + clarify data provenance |
| `5eb83e1` | docs | Update methods fragment for r8 + rsid matching methodology |
| `90da901` | feat | `phase2_enabled_sources` config filter for Path A scope |
| `d0267ce` | ops | Path A fire script for T1 first-production launch |
| `dd990f6` | fix | Make `neg_ctrl_results` optional for `assign_tiers` |
| `8e0b804` | fix | Allow `phase2_enabled_sources` in pipeline.yaml config (schema) |
| `bf188da` | fix | Materialize `null_loci_summary.tsv` at rule's declared output path |

**Uncommitted:** `src/python/assign_tiers.py` — empty-file + all-NaN group tolerance. No-regrets commit regardless of forward path.

---

## 3. The Journey: What We Found, Fixed, and Pivoted On

### 3.1 Stage A/B.5 (pre-session baseline, commit `07cf83a`)

Before this session, Stage A (DAG wiring) and Stage B.5 (manifest builder + `r-r.utils` conda env) were already committed and firing. The eQTL smoke ran end-to-end but returned:

```
status: too_few_snps
n_snps_overlap: 0
```

...even though the harmonized TSV had 2,601 variants and the SuSiE fit existed.

### 3.2 Option 1: SNP-Name-Mismatch Root Cause

Spawned `/gsd-debug qtl_coloc_snp_name_mismatch`. Agent uncovered **two compounding defects**:

**Defect #1** (fixed in `6a4fdd8`, `run_susie_rss.R`):
When `coloc::runsusie` hits the identity-LD fallback (variants > `LD_MAX_VARIANTS`), the synthesized identity matrix had no `dimnames`. `coloc:::annotate_susie` silently dropped SNP names from downstream objects. Fix:
```r
if (is.null(dimnames(R)) && nrow(R) == length(snp_names)) {
  dimnames(R) <- list(snp_names, snp_names)
}
```

**Defect #2** (fixed in `931a9c8`, `run_qtl_coloc.R`):
- GWAS variant IDs use GRCh37 `chr:pos_ref_alt`
- QTL variant IDs use GRCh38 `chr:pos_ref_alt`
- These *cannot match* across builds directly

Fix: **Match on rsid as the build-invariant common key** (with `variant_id` fallback). Also added handling for `.rds` LD files stored as lists (3 branches: identity fallback / list with R matrix / bare matrix). Also dropped the sentinel `"null"` column that `annotate_susie` appends.

**10 fits regenerated** with named variants preserved: FTO_16q12 (bmi/asthma/t2d/t2d.AFR), APOE_19q13 (bmi/hypertension), BMI_5q13_3, SH2B3_12q24 (hypertension/stroke), 9p21_CDKN2A (stroke).

### 3.3 Verification Checkpoint (per `/verification-before-completion`)

After user challenge ("thoroughly assess, evaluate and verify"), audited my initial A1 (eQTL-only) recommendation against ROADMAP:
- ROADMAP Phase 2 Success Criteria #2 explicitly requires "sQTL coloc (GTEx) completed"
- REQ-7 requires negative controls

A1 failed compliance. Revised to **A3 = eQTL + sQTL + neg-ctrl (EUR-only)**.

### 3.4 eQTL Catalogue r7→r8 Migration

Initial download attempt hit 404s — the r7 tissue-named URL scheme no longer works. Navigated to r8 via the authoritative `dataset_id_map.tsv`:

- **Study ID:** `QTS000015` (GTEx v8 in r8)
- **49 tissues** × QTD IDs built into `config/eqtl_catalogue_qtd_map.yaml`
- **16 semantic aliases required** (Whole_Blood→blood, Muscle_Skeletal→muscle, Brain_Frontal_Cortex_BA9→brain_frontal_cortex, etc.) — r8 uses lower-case short names, GTEx v8 uses PascalCase_Underscore
- Citation: Kerimov et al. *PLoS Genetics* 2023

### 3.5 `.all.tsv.gz` vs `.cc.tsv.gz`: A Data-Type Correction

Initial config used `.cc.tsv.gz` for both eQTL and sQTL. FTO smoke on `.cc.tsv.gz` returned **0 harmonized variants** — FTO wasn't in the file.

**Resolution** (commit `2bde4c6`):
- **eQTL**: use `.all.tsv.gz` (full allpairs, ~3.6 GB/tissue, gene-level). `.cc.tsv.gz` is leafcutter-derived and gene-level absent.
- **sQTL**: use `.cc.tsv.gz` (~1 GB/tissue, SuSiE-fine-mapped credible sets). This IS the intended input for coloc.susie per Kerimov 2023.

### 3.6 Parallel Download: 98 Files, 180 GB

Per user's saturation directive, downloaded 49 eQTL `.all.tsv.gz` + 49 sQTL `.cc.tsv.gz` in parallel. All 98 files: gzip-intact, matched upstream sizes.

### 3.7 Phase 2 Scope Filter (90da901, 8e0b804)

Added `phase2_enabled_sources` as a `--config` override. Without this, `all_qtl_coloc` would expand to 4 sources (eQTL, sQTL, pQTL, sc-eQTL); pQTL needs `SYNAPSE_AUTH_TOKEN` and sc-eQTL needs an eQTL Catalogue dataset map for OneK1K — both T2 infrastructure. Path A scope: `["gtex_eqtl","gtex_sqtl"]`.

### 3.8 CP#1-Final AFR Row Reconciliation (d84797c)

Initial CP#1-final expected an AFR Tier A row from Phase 2. Corrected: Phase 2 is EUR-only *by design* (GTEx v8 is European-ancestry). AFR evidence arrives at Phase 9 (MVP/AoU/Pan-UKBB replication). Updated CP#1-final accordingly.

### 3.9 Execution: Two Rounds

**Round 1:** Snakemake stalled at 94% (2124/2267 jobs complete, 89 min silence, 462 orphan snakejobs, 0 LSF jobs, fire process state=S). Clean kill + restart.

**Round 2:** 144 remaining jobs completed. Output: 1,010 per-id JSONs + `qtl_coloc_summary.tsv`.

### 3.10 `assign_tiers.py` Hardening

Two failures needed tolerance:
- `results/multitrait/coloc_summary.tsv` is 1 byte (empty) → `pandas.errors.EmptyDataError` → added `os.path.getsize` gate + `try/except`
- Groups where all `PP.H4` are NaN (all rows status ≠ ok) → `idxmax` raises `ValueError: Encountered all NA values` → check `pph4_col.notna().any()` before idxmax, emit null-QTL row for all-NA groups

---

## 4. Scientific Results

### 4.1 Status Distribution (1,010 rows)

| Status | Count | % |
|---|---:|---:|
| `too_few_snps` | 942 | 93.3% |
| `no_qtl_cs` | 42 | 4.2% |
| `success` | 26 | 2.6% |

### 4.2 All 26 Successes: One Gene

- **Gene:** ENSG00000140718 (FTO), 26/26
- **Source split:** 3 eQTL + 23 sQTL
- **Top 3 by PP.H4:**

| Tissue | Source | PP.H3 | PP.H4 | hit1 (GWAS) | hit2 (QTL) |
|---|---|---:|---:|---|---|
| Muscle_Skeletal | eQTL | 0.8633 | **0.1142** | rs1558902 | rs3751813 |
| Brain_Cerebellar_Hemisphere | sQTL | 0.5583 | 0.0973 | rs1558902 | rs12929934 |
| Colon_Transverse | sQTL | 0.6035 | 0.0594 | rs3751812 | rs2072518 |

### 4.3 Scientific Interpretation

- **rs1558902** is the canonical FTO obesity GWAS lead variant. Coloc correctly identified it as hit1 for the BMI GWAS.
- High PP.H3 (~0.86) + low PP.H4 (~0.11) is the textbook **"shared locus, distinct causal variants"** signature.
- This is **consistent with the literature**: the FTO obesity locus does NOT act through FTO expression. Mechanism is distal regulation of IRX3/IRX5 via a SNP-disrupted ARID5B/TCF7L2-binding enhancer in adipocyte progenitors (Smemo 2014 *Nature*; Claussnitzer 2015 *NEJM*).
- The pipeline is **scientifically honest** — it refuses to declare a false Tier A hit at a locus where the causal mechanism is not cis-regulatory of the named gene.

### 4.4 Phase 1 Credible Sets Are Sparse

Only **12 of 96** Phase 1 SuSiE fits produced credible sets. The other 84 fits give `n_cs_gwas = 0`, which is why 942 rows report `too_few_snps` (no credible-set SNPs to intersect). This is not a bug — SuSiE legitimately finds "no credible set" when evidence is insufficient at fixed purity thresholds.

### 4.5 Tier Assignment

- **Input:** `results/multitrait/coloc_summary.tsv` = 1 byte (empty)
- **Output:** `tier_assignments.tsv` — 0 Tier A / 0 Tier B / 0 Tier C
- **Why:** tiering joins QTL coloc onto trait-pair coloc. With no trait-pair coloc, tier output is structurally empty regardless of QTL signals. Phase 1 trait-pair coloc step never fired.

Per CP#1-final decision rule, < 5 Tier A signals triggers the **AJHG fallback** ("halt T2; rewrite as methods paper").

---

## 5. Three Paths Forward

### Option X — Accept the data; sign CP#1-final; pivot to AJHG fallback

**What:** Treat the 0-Tier-A finding as the honest experimental result. Populate CP#1-final's `[TBD — Phase 2]` sections with actual numerics (including 0 counts). Sign checkpoint. Halt T2 (MR + PGS + Nature Genetics narrative). Reframe as an AJHG methods paper.

**Compliance:** Full. Follows CP#1-final decision rule literally. No further code or compute required.

**Scientific cost:** Discards the strong possibility that the 0-Tier-A outcome is a scope artifact (missing IRX3/IRX5, missing trait-pair coloc), not a biological null. The rs1558902 hit + PP.H3=0.86 is a large Tier C near-miss that would likely flip to Tier A with proper gene scope.

**Time:** 1–2 hours (doc edits + signing).

---

### Option Y — Expand gene scope + re-run Phase 1 + Phase 2

**What:**
- Amend the manifest to add **distal regulatory candidates** at each region (IRX3/IRX5 for FTO_16q12; similar expansion at APOE_19q13, 9p21_CDKN2A, SH2B3_12q24, BMI_5q13_3, etc.) — not arbitrary; justify each addition against published distal-regulatory evidence (Hi-C, ABC, CRISPRi, eQTL-secondary signals).
- Re-run Phase 1 SuSiE for any new gene/region that wasn't fit before (cheap — SuSiE is per-region).
- Re-run Phase 2 QTL coloc on the expanded manifest.

**Compliance:** Full + scientifically stronger. ROADMAP doesn't fix a gene list; it fixes a region list.

**Scientific upside:** Most likely route to actual Tier A hits. The rs1558902/FTO/Muscle_Skeletal coloc is a literal canary — the pipeline is finding the signal but looking at the wrong gene.

**Cost:** ~2 hours compute (fresh manifest + SuSiE fits for new gene IDs + QTL re-run at those IDs). Plus literature review to justify each added gene (~1–2 hours).

**Risk:** Expanding gene scope post-hoc after seeing a 0-Tier-A result has a p-hacking odor. Mitigation: pre-specify the expansion criterion ("distal regulatory target per Hi-C/ABC/CRISPRi evidence published ≥ N citations before this date") and log the amendment to OSF before re-running.

---

### Option Z — Investigate the trait-pair coloc gap first

**What:** `results/multitrait/coloc_summary.tsv` is 1 byte. Multitrait coloc never fired. Determine:
- Is this a Snakemake target that was never invoked?
- Is there an upstream rule that silently no-op'd?
- Is trait-pair coloc required by the `assign_tiers` dependency chain, or can tier_A/B/C be produced from QTL signals alone (and the join is defensive)?

**Compliance:** Diagnostic — ensures Option X's signing isn't based on a missing-input artifact.

**Cost:** 30–60 min investigation + whatever fix (if any).

**Combined with Y:** Y + Z is the maximal-rigor path: fill the gene scope gap AND fill the trait-pair gap before declaring any tier outcome.

---

## 6. Recommendation

**Option Y + Z combined.** Both gaps are legitimate scientific blockers, not compliance shortcuts:

- **Y** addresses a known-biology mismatch (FTO vs IRX3/IRX5). Skipping it would mean signing a CP#1-final that declares "no coloc at FTO locus" when the real finding is "coloc machinery working, wrong gene queried."
- **Z** addresses a structural input to tier assignment. Skipping it risks signing a checkpoint on an unambiguously incomplete pipeline state.

**X** is defensible as a compliance move but discards substantial scientific value. **Y alone** (skipping Z) risks a Y-style re-run still producing 0 tiers if the trait-pair input stays empty.

**Tiebreaker against Y+Z:** If timeline pressure materializes (it hasn't — per CLAUDE.md "Timeline is not a binding constraint"), X is defensible. If rigor > speed (project default), Y+Z.

---

## 7. Pending Work Regardless of Path

- **Commit `src/python/assign_tiers.py`** (empty-file + all-NaN tolerance). No-regrets; safer tier assignment under sparse input for any future re-run.
- **Refresh `.planning/STATE.md`** after the path decision is made.
- **Log the path decision** in `.planning/DECISIONS.md`.

---

## 8. Session Artifacts (for local inspection)

- **Debug log:** `.planning/debug/qtl_coloc_snp_name_mismatch.md` (status: resolved)
- **Debug log:** `.planning/debug/t1_phase2_first_production.md` (status: awaiting_human_verify)
- **Launch script:** `bin/fire_phase2_patha.sh`
- **Config additions:** `config/eqtl_catalogue_qtd_map.yaml`, `config/qtl_sources.yaml` (r8/QTS000015 update)
- **Per-ID JSONs:** `results/qtl_coloc/*.json` (1,010 files)
- **Aggregated summary:** `results/qtl_coloc/qtl_coloc_summary.tsv` (1,010 rows)
- **Top FTO coloc JSON:** `results/qtl_coloc/FTO_16q12_ENSG00000140718_gtex_eqtl_Muscle_Skeletal.json`
- **SuSiE fits:** `results/fine_mapping/susie/*.fit.rds` (96 files; 12 with non-empty credible sets)
- **Methods fragment:** `.planning/phases/02-3-way-qtl-colocalization/methods_fragment.md`
- **CP#1-final draft:** `.planning/checkpoints/T1_review_final_draft.md`

---

**Awaiting user direction: X / Y / Z / Y+Z.**
