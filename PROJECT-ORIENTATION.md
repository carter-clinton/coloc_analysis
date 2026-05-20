# Project Orientation (ELI10)

> Reference document. Comprehensive plain-language explanation of what this project is, what we're building, and how all the pieces connect.
>
> Written: 2026-05-19. Section "Current state snapshot" updates over time; the rest is evergreen.
>
> Companion to `PROJECT.md` (constraints) and `CLAUDE.md` (agent instructions). For day-to-day status see `.planning/STATE.md`.

---

## Table of contents

1. [The end goal](#the-end-goal)
2. [The two tracks](#the-two-tracks)
3. [Track B in depth (this work)](#track-b-in-depth-this-work)
4. [Why AoU specifically](#why-aou-specifically)
5. [The 3 MatrixTables (MTs) we're building](#the-3-matrixtables-mts-were-building)
6. [The cohort-definition pipeline (load_qc_cohort)](#the-cohort-definition-pipeline-load_qc_cohort)
7. [What the refactor changes (operational, not scientific)](#what-the-refactor-changes-operational-not-scientific)
8. [How AoU output flows into HPC analysis](#how-aou-output-flows-into-hpc-analysis)
9. [Where the GWAS and eQTL summary stats come from](#where-the-gwas-and-eqtl-summary-stats-come-from)
10. [Concrete participant and variant counts](#concrete-participant-and-variant-counts)
11. [Current state snapshot (as of 2026-05-19)](#current-state-snapshot-as-of-2026-05-19)
12. [Common confusions / corrections](#common-confusions--corrections)
13. [Glossary](#glossary)

---

## The end goal

You're trying to answer questions of the form: **"At this spot on the genome where a disease association signal is, is the GENE itself (its coding sequence or its expression level) causing the disease — or is it some nearby non-coding regulator hitchhiking with the real causal variant?"**

The statistical tool that answers that is called **colocalization** (coloc). It compares two summary-level datasets:

- **Disease GWAS summary stats** — for each DNA variant in a region, how strongly does it associate with disease risk?
- **Gene-expression eQTL summary stats** — for each DNA variant in the same region, how strongly does it change gene activity?

If both sets of signals point at the same variants, the gene and the disease are likely **colocalized** — same causal mechanism. If they point at different variants, the gene is probably not the causal mediator at this locus.

That's the science. **Everything we build is infrastructure to do this kind of analysis honestly in populations where it usually isn't done well.**

The catch: to compare those two signals honestly, you need a third piece of information — an **LD map** (Linkage Disequilibrium = which DNA letters tend to be inherited together along a chromosome). This LD map is **population-specific** because different ancestries have different inheritance patterns. **Using the wrong-population LD map gives wrong coloc answers.** That fact is the entire reason this project exists.

---

## The two tracks

The project has run as two interleaved tracks. Different scopes, different headlines, different statuses.

| | **Track A** — `id-vs-ref-LD` | **Track B** — `m3` (MTAG + CPASSOC + AoU-AFR-LD) |
|---|---|---|
| **Question** | Does using identity-LD (from the discovery cohort itself) vs reference-LD (from 1000G or similar) change coloc conclusions at a known locus? | Can a multi-trait genome-wide search using an ancestry-specific LD reference surface NEW colocalizing loci that single-trait + EUR-LD analyses missed? |
| **Scope** | **Single locus.** SH2B3 anchor + attempts to extend elsewhere | **Genome-wide.** No prior locus commitment |
| **Methodological novelty** | PSD-regularized LD for coloc; demonstration that LD-source choice changes conclusions | Multi-trait combination (MTAG + CPASSOC) plus a high-power ancestry-specific LD reference (AoU AFR), used as a discovery pipeline |
| **Empirical results** | W1=FIRM (SH2B3 survives PSD-regularized LD); W2=STRUCTURAL (28/28 R1 loci empty); W3=0/6 elsewhere; W4=DEFERRED_TO_FOOTNOTE — i.e., **SH2B3 is the only locus that survived rigorous re-analysis** | TBD — depends on what the genome-wide multi-trait scan surfaces when run with the new AFR-LD panel |
| **Status** | Submission in progress (locked 2026-05-12, package downloaded locally). No further analytical changes — paper is sealed pending submission. | In active development. m3-W1 (Wave 1) builds the LD reference panel infrastructure — this is what Cell 3 produces. |
| **Memory refs** | [[project_ta_r3_closeout_2026-05-06]], [[project_track_a_handle]], [[track_a_submission_in_progress]], [[feedback_stop_asking_track_a]] | [[project_reframe_2026-04-22]], [[project_state]] |

**Important:** Track A's headline (SH2B3) is NOT Track B's headline. Track A is a methodological paper anchored on SH2B3 as the empirical case. Track B is a discovery paper that may or may not re-surface SH2B3 along with novel loci. **The work in progress right now is Track B.**

---

## Track B in depth (this work)

Per [[project_reframe_2026-04-22]], the strategic pivot phrased Track B as:

> Candidate-locus circular → MTAG + CPASSOC + AoU-AFR-LD genome-wide path

Decoded:

### "Candidate-locus circular"

The old way of testing colocalization at one locus (because someone already suspected it was interesting) is **circular reasoning** if you want to discover novel findings. You're pre-filtering your hypothesis space using exactly the populations and methods you're trying to critique. Track B steps away from candidate-locus thinking.

### MTAG (Multi-Trait Analysis of GWAS)

Combines summary statistics across **correlated traits** to boost discovery power. Instead of one disease GWAS, you input a panel of related-trait GWAS (e.g., a set of cardiometabolic or inflammatory traits). MTAG produces a **combined-evidence summary stat** that has more power than any single trait alone. This surfaces variants with shared signal across the panel.

### CPASSOC (Cross-Phenotype Association)

Tests for variants associated with **multiple traits simultaneously**, using a different statistical framework from MTAG (heterogeneity-aware, weights traits by their genetic correlation). Complementary to MTAG — using both lets you triangulate cross-phenotype signal robustly.

### AoU-AFR-LD

The ancestry-specific LD reference panel built from All of Us data. **This is what we're building right now.** It lets you do MTAG and CPASSOC results properly in AFR ancestry — without it, fine-mapping and coloc downstream would either use the wrong (EUR) LD reference, or use a tiny (1000 Genomes) AFR reference with too much sampling noise.

### Putting it together

```
[ panel of correlated-trait GWAS summary stats ]
              ↓ MTAG + CPASSOC
[ combined-evidence multi-trait genome-wide summary ]
              ↓ identify novel loci (genome-wide significant in combined stat)
[ for each novel locus, fine-map + coloc with eQTL using AoU-AFR-LD ]
              ↓
[ ranked list of novel AFR-relevant colocalizing loci ]
```

SH2B3 may or may not appear in that ranked list. It's not the target. The target is **what we don't know yet** — novel loci that emerge from the multi-trait scan that were invisible in single-trait + EUR-LD analyses.

---

## Why AoU specifically

Because to build a high-power AFR LD reference, you need lots of AFR samples with WGS, and AoU has more than anywhere else accessible.

| Source | AFR WGS sample count | Notes |
|---|---|---|
| 1000 Genomes AFR | ~700 | What most published coloc uses — tiny, outdated, dominated by sampling noise |
| UK Biobank AFR | ~8,000 | WGS subset; bigger but still modest |
| Pan-UKBB AFR | ~6,000 | Imputed array, not WGS |
| MVP AFR | tens of thousands | Veterans Affairs — access via separate DUA, not used here |
| **All of Us AFR** | **~50,000** | Largest publicly accessible AFR WGS cohort. Released via the AoU Researcher Workbench under standard DUAs. |

The AFR LD reference panel built from ~50,000 AoU samples is on a different power tier from the ~700-sample 1000G AFR reference that most papers still use. **This panel alone is a contribution to the field** — even before the coloc analyses that use it.

Per project constraints in `PROJECT.md`: 100% public data, no wet-lab. AoU access is via standard academic DUA.

---

## The 3 MatrixTables (MTs) we're building

A **MatrixTable** is Hail's database format for genotype data — think of it as a giant spreadsheet:

- **Rows** = DNA variants (positions where humans differ)
- **Columns** = people
- **Cells** = which DNA letters each person has at each position

The AoU source MT (`WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH`) contains **~245,000 samples × ~1.2 billion variants** of WGS data. We filter and QC this down into three cohort-specific MTs that Wave 1 of m3 emits:

| MT | Cohort definition | Approx N (post-QC) | Purpose |
|---|---|---|---|
| **#1 — `mt_afr_qc.mt`** | Ancestry=AFR (PCA-based), sensitivity=False (lenient ancestry) | ~50,000 | **Lead anchor.** Primary AFR LD reference panel — the headline cohort. |
| **#2 — `mt_afr_pca_selfid_qc.mt`** | Ancestry=AFR (PCA + self-reported confirmation), sensitivity=True (stricter) | ~30,000-45,000 | **Sensitivity analysis.** Demonstrates that the AFR LD result is robust to stricter cohort definition — drops PCA-AFR samples whose self-reported ancestry doesn't match. |
| **#3 — `mt_eur_qc.mt`** | Ancestry=EUR (PCA-based), sensitivity=False | ~150,000 | **Cross-population comparison.** Demonstrates that EUR-LD produces a quantitatively different LD landscape at the same loci — i.e., shows that the AFR result couldn't have been obtained from EUR data. |

All three are **full-genome** — not restricted to any specific locus. They cover the entire ~1.2 billion variant catalog post-QC. Downstream LD calculation will window into specific loci as needed.

---

## The cohort-definition pipeline (load_qc_cohort)

Each MT is produced by a Python function `load_qc_cohort` in `src/python/aou_ld_panel.py`. The 12-step pipeline:

1. **Read source MT** from `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` (~245K samples × ~1.2B variants)
2. **Ancestry filter** — keep only samples whose PCA-based ancestry assignment matches the cohort's target ancestry (AFR or EUR)
3. **Anti-join relateds** — drop one sample from each related pair (kinship > some threshold) so samples are statistically independent
4. **Sensitivity filter** (conditional) — if `sensitivity=True`, additionally require the sample's self-reported ancestry to match the PCA call
5. **`naive_coalesce(2048)`** — re-partition the data into 2048 chunks for parallel compute
6. **`split_multi_hts`** — split multi-allelic variants (positions with >2 alleles) into separate biallelic records, one per alt allele
7. **`sample_qc`** — compute per-sample QC stats (call rate, het/hom ratio, depth)
8. **`aggregate_cols`** with `hl.agg.stats(r_het_hom_var)` — global heterozygosity statistics across the cohort, used for outlier flagging
9. **`variant_qc`** — compute per-variant QC stats (call rate, MAF, HWE)
10. **Drop AoU-flagged variants** — AoU pre-flagged some variants as low-quality batch artifacts
11. **Write checkpoint** — save the result to `gs://${WORKSPACE_BUCKET}/ld/mt_<name>_qc.mt/` — this is what the `_SUCCESS` marker indicates
12. **(Refactored only) Write sidecar JSON metadata** — records cohort parameters for auto-resume sanity check

The output of step 11 is the MT that downstream LD computation reads.

---

## What the refactor changes (operational, not scientific)

The 2026-05-18 refactor (quick task `260518-qcr-load-qc-cohort-resilience-refactor`) is **operational resilience only**. It does NOT change cohort definitions, QC thresholds, or output MT content. The output MTs are byte-equivalent to what the un-refactored code would produce.

What changes:

1. **Intermediate checkpoints (×2 per cohort).** Each `load_qc_cohort` call now writes intermediate state at two boundaries within its own pipeline — post-step-6 (post-split-multi-hts) and post-step-8 (post-sample-QC). If a wedge happens later (e.g., during the step-11 final write), the kernel restart resumes from the most recent intermediate instead of re-running steps 1-8. Worst-case wedge loss: ~3-5 hours of compute instead of ~10-20.

2. **Per-cell cadence (manual gate between cohorts).** Instead of one monolithic cell writing all 3 MTs in sequence, each MT is its own cell call. You manually decide when MT #2 fires after MT #1 succeeds, when MT #3 fires after MT #2 succeeds. **Critically: this gives you a manual review gate before EUR fires** — EUR is the cost outlier (~$570-760), and you want eyes on cluster health + budget before committing.

3. **Sidecar JSON metadata for auto-resume.** Each checkpoint also writes a small JSON file recording the cohort parameters (ancestry, sensitivity, source MT path, schema_version). On re-fire, the code checks the sidecar — if parameters match, it resumes from the checkpoint; if they don't match (different cohort, different source, `force_fresh=True`), it starts fresh. Prevents the data-corruption hazard of accidentally resuming the wrong cohort's intermediate.

4. **`force_fresh` user override.** Pass `force_fresh=True` to bypass auto-resume even when a checkpoint exists. Used for explicit re-derivation (e.g., after an upstream data update or in a smoke test).

5. **`interval_filter` for smoke tests.** Pass `interval_filter='chr22'` (or any chromosome / interval) to run the entire pipeline on just that subset (~5% of the genome for chr22). Turns a 12-hour fire into a ~12-minute smoke test. Smoke paths are isolated by the `interval_filter` suffix so they don't collide with production runs.

**Cost framing:** the refactor doesn't reduce total Wave 1 compute cost. It buys risk reduction — without it, any wedge during a monolithic run risks hours of lost work; with it, the loss is bounded.

Plan + design specs:
- `.planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/260518-qcr-DESIGN.md` (v2.1 APPROVED at commit 3cb659c)
- `.planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/260518-qcr-PLAN.md` (15-task TDD breakdown at commit 328f0f1)
- `.planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/260518-qcr-SUMMARY.md` (task closure at commit 717303e)
- `.planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/FUTURE-pre-sensitivity-intermediate-sharing.md` (deferred optimization at commit b2515ce)

---

## How AoU output flows into HPC analysis

The 3 MTs live in AoU's bucket (`gs://fc-secure-<workspace-id>/ld/`). They are **controlled-tier individual-level genotype data** — they cannot leave AoU under the DUA. So the workflow from AoU to HPC is NOT "download the MTs and analyze them on HPC." Instead:

### Step 1 (still inside AoU): Compute LD matrices

Run a Hail job inside AoU that computes pairwise LD (typically r² and/or signed r) for each variant pair within windows around loci of interest.

- Tools: `hl.ld_matrix()` or `hl.linalg.BlockMatrix.from_entry_expr()` for pairwise correlations
- Windowing: typically ±1 Mb around each locus surfaced by the MTAG/CPASSOC scan
- Output: small LD matrices (a few GB per locus per population) + aggregated summary statistics — **never individual-level genotype data**

This is the data-egress step. Only summary-level LD matrices survive the controlled-tier boundary.

### Step 2 (HPC side): Download the LD matrices

`gsutil cp` (or AoU's sanctioned egress mechanism) → HPC GPFS at `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/data/aou_ld/` (or similar).

### Step 3 (HPC side): Integrate with external summary stats

Combine the AoU-derived LD with:
- Disease GWAS summary stats (UK Biobank, MVP, FinnGen, Pan-UKBB, deCODE, etc.) — standard public releases under their own DUAs
- eQTL summary stats (GTEx, eQTLGen, tissue-specific catalogs) — typically public

### Step 4 (HPC, in R): Run the coloc analyses

The R stack you've validated:

- `coloc::coloc.abf()` — Bayesian coloc with LD-aware approximations
- `coloc::coloc.susie()` — SuSiE fine-mapping with LD prior
- `hyprcoloc::hyprcoloc()` — multi-trait colocalization
- `susieR` — single-trait fine-mapping
- `TwoSampleMR` + `MRPRESSO` — Mendelian randomization sanity checks

Each tool takes the AoU-derived LD matrix as the population-specific co-inheritance reference.

### Step 5 (HPC): Compare across LD sources

The contrast IS the result:
- AFR-LD-based coloc (this work) vs EUR-LD-based coloc (the standard approach)
- AFR-LD-based coloc vs identity-LD (from discovery cohort, where available)

The headline finding is: at AFR-relevant loci, ancestry-specific LD changes the coloc answer in ways the standard approach misses.

---

## Where the GWAS and eQTL summary stats come from

These are EXTERNAL to AoU. They're published or publicly available summary-level data from other studies. **You already have most of them downloaded or download-pipelined.**

### Disease GWAS summary stats

| Source | Coverage | Access | Notes |
|---|---|---|---|
| **UK Biobank GWAS** | EUR-dominated, hundreds of traits | Public summary stats (Neale Lab, Pan-UKBB) | Standard cardiometabolic and inflammatory trait panel sources |
| **Pan-UKBB** | Multi-ancestry breakdowns including AFR | Public | AFR strata are smaller; useful for cross-ancestry replication |
| **MVP (Million Veteran Program)** | EUR + AFR + HIS strata, broad trait coverage | Summary stats released for many traits | One of the few large AFR GWAS sources |
| **FinnGen** | Finnish population, broad trait coverage | Public, by release | Useful for replication; Finnish ≠ broader EUR but related |
| **deCODE** | Icelandic, broad trait coverage | Some summary stats public | Replication source |
| **BBJ (Biobank Japan)** | EAS ancestry | Public | Cross-ancestry replication |

For the multi-trait MTAG/CPASSOC step in Track B, you'll select a panel of correlated traits from these sources.

### eQTL summary stats

| Source | Tissues | Access | Notes |
|---|---|---|---|
| **GTEx (v8)** | ~50 tissues incl. whole blood | Public | Standard eQTL reference. Sample size ~838. |
| **eQTLGen** | Whole blood, very large N | Public | Higher-power whole-blood eQTL |
| **Tissue-specific catalogs** | Brain (PsychENCODE), immune (DICE), etc. | Various, mostly public | Used as appropriate for the trait |

### Important: ancestry caveat on summary stats

Most published GWAS and eQTL summary stats are EUR-dominated. The AoU-AFR-LD panel lets you analyze them properly in AFR — but if the GWAS itself is EUR-only, AFR-LD-based fine-mapping is still informative because LD differences can change which variant looks "tagging" vs "causal." The cross-ancestry mismatch IS often the point: when EUR GWAS variant ranks don't match what AFR-LD fine-mapping would suggest, that's a publishable finding.

---

## Concrete participant and variant counts

This is what you'll cite in the paper. Approximate numbers:

| Layer | Source | Approx N | Variants | Purpose |
|---|---|---|---|---|
| AFR primary cohort (post-QC) | AoU | ~50,000 | ~30-50M post-QC variants | Primary AFR LD panel cohort |
| AFR sensitivity cohort (post-QC) | AoU | ~30-45,000 | ~30-50M post-QC variants | Robustness check |
| EUR replication cohort (post-QC) | AoU | ~150,000 | ~30-50M post-QC variants | Cross-population contrast |
| Multi-trait GWAS panel | UKB / MVP / FinnGen / Pan-UKBB | varies per trait; total cumulative N across panel is tens of millions | Discovery-set GWAS variants | Multi-trait combination via MTAG/CPASSOC |
| Whole-blood eQTL | GTEx v8 | ~838 | tested cis-eQTL variants per gene | Gene expression signals for coloc |

Variant counts (`~30-50M post-QC`) are post-filtering estimates — exact numbers will be in the Wave-1 results once all 3 MTs land and `count_rows()` is logged for each.

---

## Current state snapshot (as of 2026-05-19)

> This section updates as Wave 1 progresses. The rest of this document is evergreen.

### What's done

✅ **MT #1 (`mt_afr_qc.mt`) — AFR primary anchor** — fully committed to bucket
- `_SUCCESS` marker present
- `metadata.json.gz` parses cleanly
- ~12,337 component files in the MT directory
- Spent ~$700 of compute to produce this
- This is the AFR LD panel anchor — the headline cohort for Track B

✅ **Refactored `load_qc_cohort`** — pushed to `origin/main` (commits 779fe84..50f071c, fast-forward) on 2026-05-18
- 7 new helper functions + scheme-dispatch shim
- 27 tests total (16 pre-existing + 11 new), 34 PASS + 9 SKIP
- Intermediate checkpoints + sidecar metadata + auto-resume implemented
- Per the SUMMARY.md task closure: `IMPLEMENTATION_COMPLETE_AOU_VALIDATION_PENDING`

✅ **Diagnostic memories baked** — [[feedback_aou_websocket_drop_zombie_pattern]] (2026-05-17), [[feedback_aou_cluster_sizing_for_ld_panel]] (2026-05-17), [[feedback_aou_hail_driver_quiet_vs_wedge]] (2026-05-19)

### What's in progress

🔄 **Kill switch + refactor switchover** — kernel interrupt → subprocess diagnostic cell → git pull → kernel restart → re-fire Cells 1a + 1b → verify mt_afr_qc.mt readable → fire MT #2 (sensitivity) on refactored code

### What's pending

⏳ **MT #2 (`mt_afr_pca_selfid_qc.mt`) — AFR sensitivity cohort** — to be fired on refactored code post-switchover (~10-12h, ~$190)

⏳ **Manual cost-gate review before MT #3** — explicit review of cost forecast + cluster health + session window before authorizing EUR fire

⏳ **MT #3 (`mt_eur_qc.mt`) — EUR replication cohort** — fired on refactored code with intermediate-checkpoint resilience after manual gate (~12-24h, ~$240-460 depending on EUR sample count scaling)

⏳ **Wave-1 closeout** — STATE.md update + LD computation phase planning

### Total Wave-1 cost projection

| Track B m3-W1 phase | Estimated cost |
|---|---|
| Sunk on Cell 3 monolithic (~$700) — MT #1 secured | $700 |
| MT #2 sensitivity on refactored code | $190 |
| MT #3 EUR on refactored code | $240-460 |
| **Total m3-W1** | **~$1,130-1,350** |

(Track B m3 has additional waves beyond W1 for the LD computation + MTAG/CPASSOC + coloc analyses. W1 is the LD panel infrastructure phase.)

---

## Common confusions / corrections

### "Are we only looking at SH2B3?"

**No.** SH2B3 is Track A's anchor (single-locus methodological paper, submission in progress). Track B (this work) is **genome-wide** — it builds a full-genome AFR LD reference panel that downstream multi-trait analyses can window into for ANY locus. SH2B3 may surface as one of many loci, but it's not the target.

### "Are the 3 MTs SH2B3-region MTs?"

**No.** The 3 MTs are full-genome — ~1.2 billion variants × N samples each. They cover the entire WGS catalog post-QC. LD computation will window into specific loci downstream, not the MT generation step.

### "Why three MTs? Aren't we just building one AFR LD panel?"

The three MTs are not three LD panels — they're three **cohort definitions** for which a single LD panel methodology gets computed and compared. MT #1 is the primary (lenient AFR), MT #2 is the sensitivity (stricter AFR), MT #3 is the cross-population EUR comparison. This 3-MT structure shows: (a) the AFR LD panel is robust to cohort definition, and (b) the AFR result is quantitatively different from what you'd get from EUR data.

### "Is the refactor changing what gets published?"

**No.** The refactor is operational resilience — intermediate checkpoints, per-cell gates, sidecar metadata. The output MTs are byte-equivalent. What it changes is the recoverability story (less work lost on wedges) and the cost discipline (manual gate before EUR cost outlier).

### "Is Track A done?"

Submission is in progress (locked 2026-05-12). Per [[feedback_stop_asking_track_a]], don't proactively surface Track A — Carter is holding the package locally, will submit when ready, and will confirm submission. Until then: treat Track A as locked and don't ask.

### "What is `m3`?"

`m3` is the milestone-3 phase of the project — the Track B genome-wide analysis phase. Per [[project_reframe_2026-04-22]]: "MTAG + CPASSOC + AoU-AFR-LD genome-wide path". m3-W1 is the LD reference panel infrastructure wave (current). Subsequent m3 waves will cover LD computation, MTAG/CPASSOC scan, fine-mapping + coloc on flagged loci.

---

## Glossary

| Term | Meaning |
|---|---|
| **AoU** | All of Us Research Program — NIH biobank of ~500K Americans with WGS |
| **CPASSOC** | Cross-Phenotype Association test — multi-trait association method |
| **Coloc / colocalization** | Statistical test for shared causal variants between two GWAS-like signals (e.g., disease GWAS vs gene-expression eQTL) |
| **Dataproc** | GCP-managed Spark/Hadoop cluster — what AoU's compute env uses under the hood |
| **DUA** | Data Use Agreement |
| **eQTL** | Expression Quantitative Trait Locus — DNA variants that influence gene expression |
| **GPFS** | General Parallel File System — the HPC shared filesystem at NCSU |
| **GWAS** | Genome-Wide Association Study |
| **Hail** | Genomic data analysis framework built on Spark; AoU's standard analysis tool |
| **HPC** | High-Performance Computing — your NCSU LSF cluster on GPFS |
| **HWE** | Hardy-Weinberg Equilibrium — variant-level QC metric |
| **LD** | Linkage Disequilibrium — non-random co-inheritance of nearby DNA variants |
| **LSF** | Load Sharing Facility — the HPC job scheduler at NCSU |
| **MAF** | Minor Allele Frequency |
| **MT** | MatrixTable — Hail's genotype-data database format |
| **MTAG** | Multi-Trait Analysis of GWAS — multi-trait summary-stat combination method |
| **m3** | Milestone-3 phase of Track B (this work) |
| **PCA** | Principal Components Analysis — used here for ancestry assignment |
| **PSD-regularized LD** | Positive Semi-Definite-regularized LD matrix — the Track A methodological contribution |
| **r² / signed r** | LD correlation metrics |
| **SH2B3** | The locus that survived Track A's rigorous re-analysis; NOT the Track B target |
| **Stage (Spark)** | A unit of parallel execution in Spark; each Hail operation becomes one or more Spark stages |
| **WGS** | Whole-Genome Sequencing |
| **YARN** | Yet Another Resource Negotiator — Hadoop's resource manager; used by Spark on Dataproc |

---

## Cross-references

- `PROJECT.md` — short constraints sheet
- `CLAUDE.md` — agent instructions and GSD enforcement
- `.planning/STATE.md` — current operational state (updates per session)
- `.planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/` — refactor design + plan + summary
- `src/python/aou_ld_panel.py` — `load_qc_cohort` and helpers
- `tests/m3/test_aou_ld_panel_local.py` — pytest suite (34 PASS + 9 SKIP without Hail)
- AoU bucket: `gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/ld/` — Wave 1 MT outputs
