# Post-Wave-1 Roadmap (ELI10)

> Reference document. Plain-language explanation of what an MT is, what we have when Wave 1 finishes, and everything that comes next — operational closeout, the next compute phase, and the actual scientific output.
>
> Written: 2026-05-20 (during MT #3 / Stage 62 wait). Companion to `PROJECT-ORIENTATION.md` (comprehensive project scope) and `PROJECT.md` (constraints sheet).
>
> Style: ELI10 throughout — simple language, plain analogies, minimal jargon. Aim is "future-Carter, or a collaborator who's never seen this project, can pick this up cold."

---

## Table of contents

1. [What "MT" stands for](#what-mt-stands-for)
2. [What we have right now](#what-we-have-right-now)
3. [Immediate operational closeout (right after MT #3 lands)](#immediate-operational-closeout-right-after-mt-3-lands)
4. [Wave 2 — the LD matrix computation phase](#wave-2--the-ld-matrix-computation-phase)
5. [Wave 3+ — the HPC analysis (the actual paper)](#wave-3--the-hpc-analysis-the-actual-paper)
6. [Productive work to do during waits](#productive-work-to-do-during-waits)
7. [TL;DR](#tldr)

---

## What "MT" stands for

**MT = MatrixTable.** It's Hail's database format for genotype data.

Think of it as a giant spreadsheet that's too big to open in Excel:

- **Rows** = each row is one position on the genome where humans differ from each other (e.g., "chromosome 2, position 12,345,678 — some people have an A here, others have a G")
- **Columns** = each column is one person
- **Cells** = which DNA letters that person has at that position

Each MT we're building is **~50,000-150,000 people × ~1.2 billion DNA positions** of clean, filtered genotype data, ready to feed into the next analysis step.

Why not a regular table or CSV file? Because the data is too big for normal tools. A naive CSV of 150,000 people × 1.2 billion positions would be ~180 trillion cells — terabytes of text. Hail's MT format chunks the data into 2,048 parallel partitions so Spark can work on it in parallel across many machines simultaneously.

---

## What we have right now

We've been baking 3 MTs in a giant All of Us oven (the Dataproc cluster) for the last ~60+ hours. The result is one MT per **cohort** (a defined group of people):

| MT | Cohort | Approximate N | Status | What it's for |
|---|---|---|---|---|
| **MT #1 — `mt_afr_qc.mt`** | AFR primary (lenient ancestry filter) | ~50,000 | ✅ DONE in bucket | The **headline cohort** — primary AFR LD reference |
| **MT #2 — `mt_afr_pca_selfid_qc.mt`** | AFR sensitivity (stricter ancestry filter — PCA + self-reported confirmation) | ~30-45,000 | ✅ DONE in bucket (presumed; formal verify pending terminal recovery) | **Robustness check** — shows the AFR result holds under stricter cohort definition |
| **MT #3 — `mt_eur_qc.mt`** | EUR replication | ~150,000 | 🍞 STILL COOKING (Stage 62 in progress) | **Cross-population contrast** — shows EUR-LD gives a quantitatively different answer than AFR-LD |

These three MTs are **raw ingredients**, not the dish. The actual scientific output comes from processing them further (see Wave 2 below).

**Insurance note:** even if MT #3 wedges right now and never completes, MT #1 and MT #2 are immutable GCS objects in the bucket. They're preserved forever. Worst case for MT #3 is a re-fire on refactored code — wouldn't have to redo MT #1 or MT #2.

---

## Immediate operational closeout (right after MT #3 lands)

When MT #3 finishes (estimated ~today or tomorrow morning EDT, depending on Stage 62's velocity), do these in order. Should take ~30-60 minutes total.

### 1. Manually pause the AoU env immediately

**Why:** The Dataproc cluster costs $19.03/hour while RUNNING. When Cell 3 finishes, the kernel goes idle, and 30 minutes later the env would auto-pause to ~$0.14/hour. Manually pausing right when MT #3 _SUCCESS lands skips the 30-min idle wait and saves ~$10.

**How:** Workbench dashboard → env panel → click **Pause Environment**. (No iframe needed; this is a workbench-level control.)

### 2. Formally verify all 3 MTs in the bucket

**Why:** MT #2 was presumed-complete based on Spark UI evidence but not formally gsutil-verified at the time (the terminal was dead). After env resume (when needed for Wave 2), run a quick verification.

**How:** Once the env is resumed (in Wave 2 prep) and terminal is working:

```bash
for mt in mt_afr_qc.mt mt_afr_pca_selfid_qc.mt mt_eur_qc.mt; do
  echo "=== $mt ==="
  gsutil ls "$WORKSPACE_BUCKET/ld/$mt/_SUCCESS"
  gsutil cat "$WORKSPACE_BUCKET/ld/$mt/metadata.json.gz" | gunzip | python3 -c "import json,sys; m=json.load(sys.stdin); print('keys:', list(m.keys()))"
done
```

Each MT should print its `_SUCCESS` marker path + the canonical Hail metadata keys.

### 3. Save the cooking log (`/tmp/hail.log`)

**Why:** It's the full record of how Cell 3 ran for 60+ hours. Useful for retrospective if anything weird shows up later, and for the methods section of the paper.

**How:**

```bash
gsutil cp /tmp/hail.log "$WORKSPACE_BUCKET/forensics/hail.log.cell3-complete.$(date -u +%Y%m%dT%H%M%S).txt"
```

### 4. Update `.planning/STATE.md`

**Why:** Project journal. Marks m3-W1 (Wave 1) as complete. Future-you will appreciate the note.

**What to update:**
- Frontmatter status: `m3-W1 IN PROGRESS` → `m3-W1 COMPLETE`
- Quick Tasks table: append `260518-qcr` final closeout note if not already there
- Session Continuity: add 2026-05-20 entry with final cost, asset list, transition to Wave 2

### 5. Commit `PROJECT-ORIENTATION.md` and this file

**Why:** Both are sitting uncommitted on disk. Commit them so they're part of the repo permanently.

**How:**

```bash
git add PROJECT-ORIENTATION.md POST-WAVE-1-ROADMAP.md
git commit -m "docs: add PROJECT-ORIENTATION.md and POST-WAVE-1-ROADMAP.md reference docs"
```

(Explicit paths per [[feedback_multi_terminal_staging]] — never `git add .`.)

---

## Wave 2 — the LD matrix computation phase

This is the **next major compute phase.** The 3 MTs are the input; LD matrices are the output we actually need for downstream analysis.

### What is LD?

**LD = Linkage Disequilibrium.** ELI10 version: **"which DNA letters tend to travel together in groups along a chromosome."**

Because chromosomes get inherited as chunks (with occasional crossovers during reproduction), nearby DNA letters tend to be inherited as a package. If Alice's grandparent had the haplotype `A-T-G` at three nearby positions, Alice likely inherits all three together — not a mix of A from one ancestor and G from another.

**Critically, LD patterns differ between populations.** Different ancestries have different historical recombination patterns, founder effects, and selection pressures — which means the LD around a given DNA position can look quite different in AFR vs EUR vs EAS people. **Using the wrong-population LD when fine-mapping a GWAS association can give wrong causal-variant answers.** This is THE central methodological reason for the entire project.

### What is an LD matrix?

The LD matrix is a giant lookup table that says, for each pair of DNA positions, how strongly they're correlated (= how often they travel together) in a given population.

If you have N variants in a window, the LD matrix is an N×N matrix where cell `[i,j]` is the LD correlation (typically r² or signed r) between variant i and variant j.

For a single 1 Mb window around a locus, N might be ~10,000-50,000 variants → 10,000² = 100 million numbers → ~800 MB as float64. For multiple loci, the total LD matrix output is a few GB.

### What Wave 2 actually does

Compute LD matrices from each of the 3 MTs, inside AoU (where the genotype data lives — it can't leave).

**Inputs:** the 3 MTs in `gs://<bucket>/ld/`
**Outputs:** LD matrices in `gs://<bucket>/ld_matrices/` (or similar prefix), one per (cohort, locus-window)

**Hail tools used:**
- `hl.ld_matrix()` for pairwise LD calculation
- `hl.linalg.BlockMatrix.from_entry_expr()` for the underlying block-matrix construction
- Optionally `hl.experimental.ld_score()` for related metrics
- Write outputs as Hail BlockMatrix native format OR convert to PLINK `.ld` / matrix-market format

### Design questions to settle before firing Wave 2

Worth a `/gsd-quick --discuss` to settle these:

1. **Full-genome pre-compute, or locus-by-locus on-demand?**
   - **Full-genome:** compute LD for the whole genome (in chunks). Pro: immediately available for any locus that surfaces from MTAG/CPASSOC. Con: bigger compute, bigger output, may overcompute regions we never use.
   - **Locus-by-locus:** only compute LD around specific loci of interest. Pro: smaller compute, smaller output. Con: requires knowing the locus list first (chicken-and-egg with the MTAG scan).
   - **Hybrid:** pre-compute genome-wide at modest resolution (e.g., r² for variants within 500 kb of each other), then refine on-demand at higher resolution around hits.

2. **Which LD metric?**
   - **r² (squared correlation)** — standard for coloc; sign doesn't matter
   - **signed r** — needed for SuSiE fine-mapping; preserves direction
   - Probably compute both (signed r is sufficient since r² = signed_r²)

3. **Block size for BlockMatrix?** Affects memory pressure during compute and chunk size for write. Hail default is 4096; AoU's documented best practice may differ.

4. **Output format for HPC consumption?**
   - **Hail BlockMatrix native** — needs Hail to read on HPC (overhead)
   - **PLINK `.ld` text format** — universal but large
   - **Matrix-market (`.mm`) or HDF5** — Python/R friendly
   - **Sparse format (`.mtx` sparse)** — only LD > some threshold (e.g., r² > 0.001) — much smaller

5. **Per-population separately, or pooled?** Definitely per-population — the whole point is to compare AFR-LD vs EUR-LD. Three separate LD computations from three MTs.

6. **Variant frequency filter?** Probably restrict to MAF ≥ some threshold (e.g., 0.001 or 0.005) for downstream fine-mapping stability — very rare variants have noisy LD estimates.

7. **How to coordinate with the MTAG locus list?** MTAG produces a list of loci that look interesting in the multi-trait scan. LD needs to be available for those loci. Sequencing: pre-compute genome-wide LD → run MTAG → look up LD per surfaced locus.

### Wave 2 cost estimate (rough)

Computing LD matrices from a Hail MT is generally cheaper than the QC pipeline that built the MT, because:
- Fewer per-task transformations (just compute correlations vs full QC)
- Smaller output per cohort (a few GB vs many GB of MT)

Rough estimate: each cohort's LD compute = ~$50-200 depending on full-genome vs locus-by-locus and resolution choices. Total Wave 2 across 3 cohorts: ~$150-600.

---

## Wave 3+ — the HPC analysis (the actual paper)

This is where the LD matrices get combined with external summary stats to produce the scientific result. **All of this happens on HPC (your NCSU LSF cluster on GPFS) using the R coloc stack.**

### Step 1: Egress LD matrices from AoU to HPC

LD matrices are summary-level data, so they're allowed to leave AoU under the DUA. Copy them to HPC:

```bash
# from HPC, with appropriate gcloud auth
gsutil cp -r "gs://$WORKSPACE_BUCKET/ld_matrices/" /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/data/aou_ld/
```

### Step 2: Multi-trait GWAS panel selection

Pick the panel of correlated traits to feed into MTAG and CPASSOC. Considerations:
- Trait correlations (MTAG works best on traits with genetic correlation r_g > ~0.3)
- Sample sizes (bigger = more power)
- AFR-relevance (some traits have different genetic architecture in AFR; choose accordingly)
- Public availability under reasonable DUAs

Likely sources:
- **UK Biobank** (Pan-UKBB for multi-ancestry strata)
- **MVP** (Million Veteran Program, EUR + AFR + HIS strata)
- **FinnGen** (Finnish cohort)
- **deCODE** (Icelandic cohort)
- **BBJ** (Biobank Japan, for EAS cross-ancestry)

### Step 3: Run MTAG and CPASSOC genome-wide scan

This is the main discovery step.

- **MTAG** (Multi-Trait Analysis of GWAS): Python package, runs on HPC with the panel of GWAS summary stats as input. Outputs combined-evidence summary statistics per variant.
- **CPASSOC** (Cross-Phenotype Association): R package, complementary multi-trait method using heterogeneity-aware statistics.

Both produce ranked lists of variants with elevated multi-trait signal. Combine the two lists; take the union (or intersection, depending on stringency preference).

### Step 4: For each surfaced locus, fine-map + coloc

For every locus that comes out of the multi-trait scan (typically ~10-100 loci depending on thresholds):

1. **Pull the AFR LD matrix** for the locus window (±1 Mb)
2. **Run SuSiE fine-mapping** (`susieR::susie_rss()`) using the GWAS summary stats + LD matrix → identifies the ~1-5 most likely causal variants per locus
3. **Pull the eQTL summary stats** for nearby genes (GTEx, eQTLGen, tissue-specific catalogs)
4. **Run colocalization tests:**
   - `coloc::coloc.abf()` for fast Bayesian coloc (LD-aware approximation)
   - `coloc::coloc.susie()` for SuSiE-based coloc with LD prior
   - `hyprcoloc::hyprcoloc()` for multi-trait coloc across the original trait panel
5. **Record the coloc posterior probabilities** for each (locus, gene) pair

### Step 5: Cross-LD-source comparison

This is the **headline result** of Track B.

For each surfaced locus, re-run Steps 2-4 with three different LD inputs:
- **AFR primary LD** (from MT #1)
- **AFR sensitivity LD** (from MT #2)
- **EUR LD** (from MT #3)

**Compare:**
- Do the SuSiE credible sets shift between LD sources?
- Do the coloc posterior probabilities change?
- Are there loci where AFR-LD says "colocalized with gene X" but EUR-LD says "not colocalized"?

**The contrast IS the result.** Loci where ancestry-specific LD changes the answer demonstrate why population-specific LD references matter — and identify novel AFR-relevant colocalizing loci that prior EUR-LD-based analyses would have missed.

### Step 6: Mendelian Randomization sanity checks (optional but reviewer-defensive)

For top colocalized hits:
- `TwoSampleMR::mr()` — IVW + weighted median + MR-Egger
- `MRPRESSO::mr_presso()` — outlier-corrected MR

These corroborate causal direction (does gene expression cause disease, vs reverse).

### Step 7: Manuscript drafting

By this point you have:
- A list of novel AFR-relevant colocalized loci (the headline result)
- LD-source comparison tables (the methodological contribution)
- Sensitivity analyses across the 3 cohorts (robustness)
- MR support for top hits (reviewer-defense)

Draft sections in this order:
1. **Methods** — easy first, you have all the scaffolding in PROJECT-ORIENTATION.md
2. **Results** — drive from the tables/figures
3. **Discussion** — interpret the AFR-LD vs EUR-LD contrast in context
4. **Introduction** — write last (you know exactly what story to set up)

Target venue per [[user_profile]]: Nature Genetics.

---

## Productive work to do during waits

While Cell 3 finishes baking (and during similar future waits), do these:

### During the remaining Stage 62 wait (next 6-19h)

1. **Draft the Wave 2 LD-computation Hail script.** Can be written locally on HPC or AoU. Pure code, no MTs needed for drafting. Be ready to fire as soon as env resumes post-MT-#3.

2. **Decide the 7 Wave-2 design questions above.** Worth a `/gsd-quick --discuss` session. Especially #1 (full-genome vs locus-by-locus) and #4 (output format) — these have downstream implications.

3. **Plan the multi-trait GWAS panel.** Which traits, which studies, sample sizes, where each lives on HPC (or where to download from). Could be its own `/gsd-quick --research` session.

4. **Smoke-test HPC R coloc stack.** Make sure `susieR`, `coloc`, `hyprcoloc`, `TwoSampleMR`, `MRPRESSO` all install and run on synthetic input. Quick `Rscript -e 'library(coloc); library(susieR); library(hyprcoloc); ...'` smoke. Worth catching dependency issues now.

5. **Draft methods section of the paper.** `PROJECT-ORIENTATION.md` has cohort definitions, sample counts, the QC pipeline, the LD computation strategy outline. Could write 2-3 pages of methods today. Best time to draft methods is while it's all fresh.

### After MT #3 lands (during env-paused window before Wave 2 fires)

1. **Verify all 3 MTs formally** (gsutil + metadata parse)
2. **Plan Wave 2 firing sequence** — which cohort first, what locus list (if locus-by-locus), what hours of compute budget
3. **Pre-fire validation:** ensure refactored code at `src/python/aou_ld_panel.py` has all the helpers Wave 2 will need; identify any new helpers Wave 2 requires

### During Wave 2 fires

Wave 2 will be shorter than Wave 1 (LD compute is cheaper than QC) but still hours-long. During those waits:
- Draft Wave 3 (HPC analysis) code in R
- Sketch figure layouts
- Plan locus-prioritization rules for the post-MTAG analysis

---

## TL;DR

**MT** = MatrixTable = Hail's giant-spreadsheet database of who-has-what-DNA-letters. Each MT = ~50K-150K people × ~1.2B genomic positions.

**Right now:** 2 of 3 MTs in the bucket (MT #1 done, MT #2 done, MT #3 still cooking). All 3 will be in the bucket sometime today or tomorrow morning EDT.

**After MT #3 lands:**
1. Pause env immediately (saves ~$10)
2. Verify all 3 MTs via gsutil
3. Save `/tmp/hail.log` to forensics bucket
4. Update STATE.md (m3-W1 → complete)
5. Commit PROJECT-ORIENTATION.md + POST-WAVE-1-ROADMAP.md

**Next compute phase (Wave 2):** Compute LD matrices from each MT inside AoU. LD = "which DNA letters travel together." LD matrix output is small enough to legally leave AoU. ~$150-600 compute, runs on resumed env.

**After Wave 2 (Wave 3+, on HPC):**
1. Egress LD matrices to HPC GPFS
2. Pick multi-trait GWAS panel (UKB / MVP / FinnGen / Pan-UKBB / etc.)
3. Run MTAG + CPASSOC genome-wide scan → list of interesting loci
4. For each locus: fine-map (SuSiE) + coloc using AoU-derived LD
5. Compare across LD sources (AFR vs AFR-sensitivity vs EUR) — **this is the headline result**
6. MR sanity checks on top hits
7. Draft manuscript → Nature Genetics

**Productive things to do while waiting:** draft Wave 2 code, plan trait panel, smoke-test R tools, draft methods section.

---

## Cross-references

- `PROJECT-ORIENTATION.md` — comprehensive project orientation (the whole arc, including the Track A vs Track B distinction and detailed cohort definitions)
- `PROJECT.md` — short constraints sheet (public data only, solo author, no web stack, etc.)
- `CLAUDE.md` — agent instructions and GSD workflow enforcement
- `.planning/STATE.md` — current operational state (updates per session)
- `.planning/quick/260518-qcr-load-qc-cohort-resilience-refactor/` — refactor design + plan + summary (the resilience refactor implemented during this session)
- `src/python/aou_ld_panel.py` — `load_qc_cohort` (the function that produces MTs) and helpers
- AoU bucket: `gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/ld/` — Wave 1 MT outputs
- AoU bucket: `gs://fc-secure-f72fd8d8-90e7-469f-b53d-8cd80cf7823a/forensics/` — preserved hail.log captures
