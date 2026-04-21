---
phase: 02-3-way-qtl-colocalization
plan: RECOVERY
plan_id: 02-RECOVERY
plan_name: "Phase 2 zero-Tier-A recovery: trait-pair gap + SuSiE yield + gene scope"
type: recovery
authored_on: 2026-04-21
authored_by: carter
trigger: "Phase 2 first-production returned 0 Tier A / 0 Tier B / 0 Tier C from 1,010 QTL colocalizations"
root_causes:
  - "Trait-pair coloc never fired (results/multitrait/coloc_summary.tsv = 1 byte)"
  - "Only 12/96 SuSiE fits produced credible sets -> 942 rows report too_few_snps"
  - "Gene-scope mismatch: manifest maps one gene per region; causal gene is often distal (FTO -> IRX3/IRX5)"
stage_count: 4
estimated_hours: 12-21
strategy: "Z -> SuSiE diagnostic -> Y -> re-evaluate CP#1-final"
gsd_routing:
  stage_1: /gsd-debug multitrait_coloc_empty
  stage_2: /gsd-debug susie_credible_set_yield
  stage_3: /gsd-plan-phase  (new sub-plan 02-07-distal-gene-scope-expansion)
  stage_4: /gsd-execute-phase + /gsd-verify-work + CP#1-final signing
depends_on: [02-01, 02-02, 02-03, 02-04, 02-05]
files_touched_at_plan_time: []
---

# Phase 2 Recovery Plan — Zero Tier A Resolution

## Context

The T1 Phase 2 first-production run (2026-04-20) fired end-to-end for the first time and produced:

- 1,010 QTL colocalizations across gtex_eqtl + gtex_sqtl
- **26 successes** (all FTO, max PP.H4 = 0.1142)
- **942 `too_few_snps` / 42 `no_qtl_cs`**
- Tier assignment: **0 Tier A / 0 Tier B / 0 Tier C**

Per CP#1-final's decision rule, < 5 Tier A triggers the AJHG fallback. But session diagnosis revealed this outcome is dominated by structural gaps, not biology:

1. `results/multitrait/coloc_summary.tsv` is 1 byte — trait-pair coloc never fired
2. Only 12/96 Phase 1 SuSiE fits produced credible sets — the input to Phase 2 is structurally thin
3. The FTO/Muscle_Skeletal top signal (PP.H3=0.86, PP.H4=0.11) is the textbook "shared locus, distinct causal variants" signature — the GWAS signal colocalizes with IRX3/IRX5 regulation, not FTO expression (Smemo 2014; Claussnitzer 2015). The manifest maps FTO_16q12 -> FTO only.

Signing CP#1-final on this state would declare a biological null on the basis of a scope-and-machinery artifact. This recovery plan fixes the gaps, then re-evaluates CP#1-final on the corrected data.

## Strategy

```
Stage 1 (Z: trait-pair gap diagnosis/fix)        [2-4 hrs]
    |
    v
Stage 2 (SuSiE credible-set yield fix)           [4-8 hrs]  <-- structural bottleneck
    |
    v
Stage 3 (Y: gene scope expansion)                [4-6 hrs]  (partial overlap with Stage 2)
    |
    v
Stage 4 (re-evaluate + CP#1-final decision)      [2-3 hrs]
```

Sequencing rationale: Z first because it's cheap and diagnostic; SuSiE second because it's the structural bottleneck limiting everything downstream; Y third because gene-scope expansion only pays off at regions with credible sets; CP#1-final last so signing happens on corrected data.

## Stage 1 — Trait-Pair Coloc Gap (Option Z)

**Goal:** Determine why `results/multitrait/coloc_summary.tsv` is empty and fix so tier assignment has its required input.
**GSD entry:** `/gsd-debug multitrait_coloc_empty`
**Time:** 2-4 hrs

### Step 1.1 — Trace the Snakemake dependency chain

```bash
wc -l results/fine_mapping/finemap_tier3_coloc.tsv
head -5 results/fine_mapping/finemap_tier3_coloc.tsv
wc -l results/multitrait/coloc_manifest.tsv
head -5 results/multitrait/coloc_manifest.tsv
ls -la results/multitrait/coloc_summary.tsv
wc -l results/fine_mapping/finemap_summary.tsv
head -20 results/fine_mapping/finemap_summary.tsv
```

### Step 1.2 — Identify the failure mode

- **Mode A:** `finemap_tier3_coloc.tsv` empty -> no Phase 1 SuSiE fit passed tier3 threshold -> root cause is the 12/96 credible-set rate -> Stage 2 dependency
- **Mode B:** `coloc_manifest.tsv` has content but `run_coloc_pair` never fired -> fix: add summary to `all` target or invoke explicitly
- **Mode C:** `run_coloc_pair` fired but produced empty/error JSONs -> debug like QTL coloc build/ID mismatch (commit `931a9c8` pattern)

### Step 1.3 — Wire trait-pair coloc into the fire script

Ensure `bin/fire_phase2_patha.sh` (or successor) explicitly requests both `results/qtl_coloc/qtl_coloc_summary.tsv` AND `results/multitrait/coloc_summary.tsv`.

### Step 1.4 — Verification (exit criterion)

`coloc_summary.tsv` no longer 1 byte; `assign_tiers.py` runs without error and produces structured output. Debug session resolves.

## Stage 2 — SuSiE Credible-Set Yield (Structural Bottleneck)

**Goal:** Raise credible-set yield from 12/96 (12.5%) to >= 40/96 (40%+) so Phase 1 output can seed both trait-pair and QTL colocalization.
**GSD entry:** `/gsd-debug susie_credible_set_yield`
**Time:** 4-8 hrs

### Step 2.1 — Audit all 96 fits

Classify failures into categories A-D:

- **Category A:** Identity LD fallback (n_variants > `LD_MAX_VARIANTS`) -> SuSiE with identity matrix rarely produces clean credible sets in LD-rich regions
- **Category B:** True no-signal (SuSiE converged with proper LD but no credible set at purity threshold)
- **Category C:** LD-GWAS variant mismatch (too few overlapping variants for SuSiE to work)
- **Category D:** SuSiE non-convergence (IBSS didn't converge in allotted iterations)

Diagnostic script: see RECOVERY_PLAN appendix — iterates `results/fine_mapping/susie_rss/*.json`, extracts `ld_source` / `converged` / `n_snps_overlap` / `n_credible_sets` per fit, bins into categories.

### Step 2.2 — Fix Category A (dominant failure mode, hypothesized)

Two options:
- **2.2a:** Compute proper LD matrices from 1000G Phase 3 via `plink --r2` / `plink2 --ld-window` for each region (matched by ancestry). Store as `.rds` files. Raise `LD_MAX_VARIANTS` or eliminate identity fallback.
- **2.2b:** Shrink region windows. Merge tiles sharing a GWAS peak into narrower focused windows (+/- 500 kb around lead SNP). Trade-off: loses "full-region" fine-mapping, gains credible sets — for coloc, credible sets matter more.

### Step 2.3 — Fix Category C (LD-GWAS variant mismatch)

The rsid-matching fix (`931a9c8`) addressed QTL coloc only. Verify Phase 1 SuSiE LD reference also uses GRCh37 variant IDs (config says `genome_build: GRCh37`). If mismatch exists, add rsid lookup or match on `chr:pos`.

### Step 2.4 — coloc.abf fallback for true-no-signal regions

For regions where SuSiE genuinely cannot produce credible sets (Category B), `coloc.susie` structurally cannot produce a result. Pragmatic hybrid:
- **Primary:** `coloc.susie` where at least one trait has a credible set
- **Fallback:** `coloc.abf` where neither trait has a credible set (flagged `method = "abf_fallback"`)
- **Supplementary:** coloc.abf vs coloc.susie agreement for regions where both ran

Scientifically defensible per Wallace 2021. Prevents losing 88% of regions.

### Step 2.5 — Re-run Phase 1 SuSiE

```bash
snakemake results/fine_mapping/finemap_summary.tsv --cores 8 --forcerun run_finemap
```

### Step 2.6 — Verification (exit criterion)

Credible-set yield >= 40%; `finemap_tier3_coloc.tsv` populated; remaining failures classified and justified.

## Stage 3 — Gene Scope Expansion (Option Y)

**Goal:** Fix gene-scope mismatch so loci with distal regulatory architecture (FTO -> IRX3/IRX5) get their causal genes queried.
**GSD entry:** `/gsd-plan-phase` -> new sub-plan `02-07-distal-gene-scope-expansion`
**Time:** 4-6 hrs

### Step 3.1 — Literature review for distal targets

Priority loci with published distal-target evidence:

| Region | Current Gene | Candidate Distal Gene(s) | Evidence |
|---|---|---|---|
| FTO_16q12 | FTO | IRX3, IRX5 | Smemo 2014 Nature; Claussnitzer 2015 NEJM |
| CDKN2A_B_9p21 | CDKN2A/B | CDKN2BAS (ANRIL) | Visel 2010; Harismendy 2011; Congrains 2012 |
| APOE_19q13 | APOE | TOMM40, APOC1 | Roses 2010; Linnertz 2014 |
| SH2B3_12q24 | SH2B3 | ATXN2, BRAP | Machiela 2011; Kato 2011 |
| FADS1_11q12 | FADS1 | FADS1/FADS2/FADS3 cluster | Lattka 2010 |

Document per addition: (a) published reference, (b) evidence type (Hi-C, ABC, CRISPRi, eQTL, MPRA), (c) distance from lead variant.

### Step 3.2 — Amend the manifest

Create `config/region_gene_map.tsv`:

```
region_id    ensembl_id         gene_symbol    role
FTO_16q12    ENSG00000140718    FTO            nearest_gene
FTO_16q12    ENSG00000176842    IRX3           distal_regulatory_target
FTO_16q12    ENSG00000176695    IRX5           distal_regulatory_target
CDKN2A_B_9p21    ENSG00000147889    CDKN2A    nearest_gene
CDKN2A_B_9p21    ENSG00000240498    CDKN2BAS   distal_regulatory_target
...
```

Modify manifest builder (`src/python/build_qtl_coloc_manifest.py`) to expand over all genes per region.

### Step 3.3 — Pre-register expansion criterion

Log to `.planning/DECISIONS.md` AND OSF amendment BEFORE re-running:

> **Criterion:** "For each curated region, add distal regulatory gene targets supported by at least one of: (a) published Hi-C / promoter-capture-Hi-C enhancer-promoter link, (b) ABC model score > 0.015, (c) published CRISPRi / MPRA evidence, (d) eQTL coloc in at least one GTEx tissue with PP.H4 > 0.5, each published in a peer-reviewed article with DOI prior to 2026-04-21."

### Step 3.4 — Window extensions for genes outside current tiles

Example: IRX5 TSS = chr16:54,964,657 (GRCh37) falls outside the current FTO_16q12 window (53,800,000-54,400,000). Extend end to ~55,100,000 or add a new tile.

### Step 3.5 — Re-run Phase 2 QTL coloc on expanded manifest

```bash
snakemake results/qtl_coloc/qtl_coloc_summary.tsv --cores 16 \
  --config phase2_enabled_sources='["gtex_eqtl","gtex_sqtl"]'
```

### Step 3.6 — Verification (exit criterion)

>= 1 signal with PP.H4 > 0.8 from gene-scope expansion; FTO vs IRX3 PP.H4 comparison at Muscle_Skeletal confirms distal-regulatory biology flip.

## Stage 4 — Re-run Tier Assignment + CP#1-final Decision

**Goal:** With all three structural gaps fixed, run full pipeline end-to-end and make an informed CP#1-final decision.
**GSD entry:** `/gsd-execute-phase` tail + `/gsd-verify-work` + CP#1-final signing
**Time:** 2-3 hrs

### Step 4.1 — Commit pending fixes

Each stage's code changes land via its GSD command's atomic commits. This plan assumes:

- Stage 1 commits: trait-pair coloc wiring
- Stage 2 commits: SuSiE LD + yield improvements
- Stage 3 commits: gene-scope manifest + manifest builder amendment
- No-regrets: `src/python/assign_tiers.py` empty-file / all-NaN tolerance (already drafted, uncommitted)

### Step 4.2 — Full pipeline end-to-end

```bash
bin/fire_phase2_patha.sh
```
(Updated to include Stage 1 trait-pair target.)

### Step 4.3 — CP#1-final decision matrix

| Tier A Count | Decision |
|:---:|---|
| >= 5 | **Continue T2** (MR + PGS + Nature Genetics narrative) |
| 3-4 | **Continue T2 with pQTL scope expansion** |
| 1-2 | **Targeted investigation** (all 49 GTEx tissues + pQTL) |
| 0 | **AJHG fallback** (genuine null after fixing all three structural gaps) |

### Step 4.4 — Document outcome

Update STATE.md, log to DECISIONS.md, update REVISION_PLAN timeline if continuing to T2, or draft AJHG reframing if pivoting.

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Most SuSiE failures are Category A (identity LD) | High | High | Compute proper LD from 1000G; raise LD_MAX_VARIANTS |
| IRX3 eQTL doesn't colocalize either | Medium | Medium | Try IRX5; expand tissues; add pQTL |
| Trait-pair gate structurally tied to SuSiE yield | High | High | Stage 2 precedes Stage 1 re-test |
| Gene-scope expansion criticized as post-hoc | Medium | Low | Pre-register criterion + OSF amendment |
| Still < 5 Tier A after all fixes | Medium | High | AJHG fallback is honest and publishable; pipeline is contribution |
| pQTL DUA delays | Medium | Medium | Start DUA application now in parallel with Stages 1-3 |

## Files to Inspect at Stage Start

| File | Check | Expected |
|---|---|---|
| `results/fine_mapping/finemap_tier3_coloc.tsv` | Row count | If 0: Mode A in Stage 1 |
| `results/multitrait/coloc_manifest.tsv` | Row count | If 0: cascading from empty tier3 |
| `results/fine_mapping/finemap_summary.tsv` | Credible-set counts | Expect 12 with CS > 0, 84 with CS = 0 |
| `results/fine_mapping/susie_rss/*.json` | `ld_source` per fit | Count identity vs actual LD |
| `data_processed/ld_reference/EUR/*.rds` | File sizes | Small = identity; large = real LD |
| `config/regions_tiled.csv` | Window sizes for failed regions | Large windows -> identity LD fallback |

## Source Authorship

This plan was authored by Carter K. Clinton on 2026-04-21 following the Phase 2 first-production diagnostic session (`.planning/session_summaries/2026-04-20_phase2_first_production.md`). The three-path presentation (X / Y / Z) in that summary was the input Carter used to converge on the Z -> SuSiE -> Y -> CP#1 sequencing documented here.
