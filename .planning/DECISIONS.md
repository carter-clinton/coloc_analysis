# DECISIONS.md

Load-bearing decisions made during project setup. Every entry is dated,
names the alternatives considered, and states the **why** — so that future-
Carter and future-Claude can re-derive or override the choice with
context.

---

## 2026-04-09 — Repo scope: canonical here, data symlinked

**Decision:** `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/` is
the **canonical git repo**. It tracks code (`src/`), config, small tables,
planning state, and symlinks that point at data on `/rs1`. Actual data bytes
never live in the repo.

**Alternatives considered:** (a) Canonical on `/rs1` where the code already
lived, with a thin GPFS pointer; (b) Full code + data mirror into GPFS
(~32 GB); (c) Two-repo split (planning on GPFS, code on `/rs1`).

**Why:** GSD already had planning artifacts in the GPFS directory and the
user wants **one** auditable home for the manuscript code. Data is already
on `/rs1` and there's no reason to duplicate 30 GB of harmonized sumstats.
Symlinks let a fresh clone on the same HPC inherit the data layout without
any mirror step.

**How to apply:** Any new code, config, or planning artifact goes in this
directory and is committed. Any new data goes to `/rs1` and is symlinked in.

---

## 2026-04-09 — Scope tier: T1 spine in full + T1→T2 checkpoint

**Decision:** Plan T1 phases (Phase 0, 1, 2, 5, 9) in full detail up front.
Plan T2 phases (3, 4, 8) as conditional — planned at Checkpoint #1 if T1
results support Nature Genetics ambition. T3 (6, 7, 10) planned only if
Checkpoint #2 lights green.

**Alternatives considered:** (a) T1 + T2 full for Nature Genetics target;
(b) All tiers including T3.

**Why:** Rigor over speed is the binding constraint, but scope creep is
the biggest risk. Every T2 and T3 phase depends on T1 outputs, so nothing
is lost by gating them. The T1 set alone is an honest AJHG submission, and
the decision to go for Nature Genetics vs. AJHG should be evidence-based,
not ambition-based.

**How to apply:** `/gsd-plan-phase` is run for T1 phases now and T2/T3
phases only after the corresponding checkpoint .md file is written with a
"go" verdict.

---

## 2026-04-09 — Data access runs in parallel from Day 1 (Phase 0 Track 0a)

**Decision:** DUA applications for UK Biobank, UKB-PPP, deCODE pQTL,
FinnGen, MVP, All of Us, BBJ, and Pan-UKBB are a dedicated **parallel
sub-track** inside Phase 0 (Track 0a) that **kicks off on the first
working day** and does **not** block any other phase work.

**Alternatives considered:** (a) Treat DUAs as a serial gate before
Phase 2 (3-way QTL coloc); (b) Defer DUAs until after T1 is complete and
the Nature Genetics pivot is decided.

**Why:** DUAs take weeks to months. Treating them as gates would stall
Phase 2 indefinitely and drag out the revision. Treating them as parallel
work lets Phase 0 infrastructure + Phase 1 fine-mapping proceed while
applications sit in queues. This was `GSD_BRIEFING.md` §5.2 gap #1 — the
single longest critical path in the project. REQ-1 enforces it.

**How to apply:** `.planning/data_access.md` is the tracker. Every DUA
row has `date_submitted`, `expected_lead_time`, `tracking_id`, `status`,
and `contact`. `/gsd-progress` surfaces "blocked on DUA X" for any phase
downstream of a pending DUA.

---

## 2026-04-09 — Data access verified — critical path dissolves

**Decision:** Six of the eight data providers originally treated as DUA
gates are actually **open-access summary statistics**. Only UK Biobank
main (individual-level, not needed for sumstats coloc) and All of Us
Controlled Tier (gated on an NC State institutional DURA) are real
access gates. **Data access is no longer the longest critical path**
in this revision.

**What verification found** (full details in `data_access.md`):

| Source | Was assumed | Actually is |
|---|---|---|
| UKB-PPP pQTL | Full UKB DUA + PPP-specific application, weeks | Open on Synapse `syn51364943` with a certified-user profile, same-day |
| deCODE pQTL | Email request, weeks | Open direct download at `decode.com/summarydata`, no account |
| FinnGen | DUA, weeks | Click-wrap registration form, same-day to next-day |
| Pan-UKBB | DUA per the UKB umbrella | Open CC-BY-4.0 anonymous S3 download |
| BBJ | JSPS-routed DUA, weeks | Open NBDC download `hum0197-v3`, no account |
| MVP | VA approval, 8-16 weeks | **Individual-level is CLOSED to non-VA researchers** — but sumstats are on dbGaP `phs001672` with no DAR, same-day |
| UK Biobank main | DUA, ~15 weeks, £3-9K+ | Still a real DUA — but **not needed** for sumstats-level coloc, MR, or replication work. Deferred to "not-needed-unless". |
| All of Us Controlled Tier | DUA, 4-6 weeks | Requires NCSU to have a signed institutional DURA. If in place, ~2 business days for account activation. **This is the one real gate.** |

**Why this matters:**

- Phase 2 (3-way QTL coloc — the highest-leverage methodological change in
  the revision) is no longer DUA-gated. All three QTL spines (GTEx, UKB-PPP,
  deCODE) can be downloaded on Day 1.
- Phase 9 (replication) has no DUA-gated sources in its primary path
  (FinnGen, GBMI, BBJ, Pan-UKBB, MVP dbGaP are all open).
- The only surviving gate is All of Us access for Phase 8 PRS work, and
  that's a T2 phase anyway — it doesn't block the T1 spine at all.

**The single Day-1 action that matters:** Contact NC State's Signing
Official to confirm whether an All of Us institutional DURA is in place
for NCSU. If yes, AoU access is ~2 days of per-researcher training +
account activation. If no, starting a DURA at NC State is now the
single slowest step in the revised access tracker.

**Alternatives considered:** (a) Treat everything as DUAs anyway and
submit them all on Day 1 regardless — wasteful; (b) Only verify the ones
that matter for the next phase — leaves landmines in later phases. Doing
the verification up front was the right call.

**How to apply:**

1. REQ-1 has been amended to describe the verified Day-1 checklist instead
   of a blanket "submit all DUAs in parallel".
2. `.planning/data_access.md` lists verified URLs, access models, and a
   revised gates table.
3. Phase 0 planning should include the Day-1 checklist as slices instead
   of "track DUA applications".
4. Phase 8 planning (T2, gated on CP#1) must start with "confirm AoU DURA
   status with NC State's Signing Official" as slice 0 — everything else
   in Phase 8 depends on it.
5. UK Biobank main DUA stays deferred. Revisit only at Phase 8 planning
   if the PRS work decides Pan-UKBB sumstats are insufficient.

**Limit of the verification:** A verification pass via web research is not
the same as actually completing the registrations, so the Day-1 checklist
is still real work — it's just "download and register" work, not
"apply-and-wait" work. Also, the research agent could not scrape the
deCODE summarydata portal (client-side rendering), so that one still needs
a manual browser visit before pipeline paths are hardcoded.

---

## 2026-04-09 — Legacy code reuse: refactor in place, extend the Snakemake workflow

**Decision:** Treat the recovered `src/legacy/` tree as the seed for the
revision, not as a read-only museum. Phase 0 audits what works; Phase 1
upgrades `run_coloc.R` (coloc.abf) to coloc.susie by extending the existing
`run_susie_rss.R`; MR / PGS Snakemake rules get fleshed out from their
current stubs rather than rewritten from scratch.

**Alternatives considered:** (a) Preserve `src/legacy/` as read-only and
write an entirely new pipeline in `src/R`, `src/python`, `src/snakemake`;
(b) Hybrid — keep the Snakemake rule structure, rewrite specific scripts
where `Revision_Plan.md` identifies methodological problems.

**Why:** The exploration discovered the prior code is **far more mature
than the planning docs hinted**: 182 files, ~11.5 MB, a complete Snakemake
workflow with modular rules (`finemap`, `mr`, `pgs`, `qc`, `ld_reference`,
`sumstats`, `regions`, `multitrait`), working `run_susie_rss.R`, and a
~7,150-row genome-wide coloc manifest. Rewriting from scratch would waste
weeks on infrastructure that already works (sumstats harmonization, LD
building, locuszoom plotting). The revision's **methodological** problems
— not the pipeline's engineering — are the target.

**How to apply:** New/rewritten scripts land in `src/R/`, `src/python/`,
or `src/snakemake/`. Legacy scripts under `src/legacy/` are never edited;
they're either (a) the reference that the new version replaces, (b) a
dependency imported until the new version lands, or (c) a module that's
fine as-is and stays under `src/legacy/` indefinitely (e.g. the LD-builder
utilities). The phase plans are explicit about which category each legacy
file falls into.

---

## 2026-04-09 — Historical backup tarball stays on /rs1

**Decision:** The 77 GB `coloc-attempt1-backup.tar.gz` and the 532 GB
`region_analysis/tmp/` scratch workspace at `/rs1/researchers/c/ckclinto/
coloc_analysis/` are **not extracted, not copied, and not referenced
from git**. They're referenced from this file and from
`src/legacy/README.md` and `archive/pre-revision-2026/prior-packages/
README.md` so they can be found if needed.

**Alternatives considered:** (a) Extract and diff against the live tree to
find unique files; (b) Delete to free space.

**Why:** Zero-cost preservation is the right trade-off. We already have
the live `/rs1/.../coloc_analysis/` tree as the authoritative source; the
backup tarball is redundant unless we discover something missing. Extracting
77 GB would cost scratch space and time for an unknown return. Deleting
would discard the only place where the *exact* pre-revision state is frozen.

**How to apply:** Do not touch. If the live `/rs1` tree changes, this
file should be updated with the new delta.

---

## 2026-04-09 — GSD mode: solo + branch isolation (not worktree)

**Decision:** GSD runs in `mode: solo` with `git.isolation: branch`.
Worktree isolation is disabled.

**Alternatives considered:** `mode: solo` + `git.isolation: worktree`
(GSD default).

**Why:** GPFS shared filesystems and git worktrees are a known-bad pairing
(`GSD_BRIEFING.md` §4). Locking semantics on GPFS produce spurious worktree
corruption. Branch isolation keeps everything in the main repo and moves
between branches for phase isolation, which GPFS handles fine.

**How to apply:** `.planning/config.yaml` (produced by `/gsd-new-project`)
must set these values. Do not accept the default worktree mode.

---

## 2026-04-09 — Target journal order

**Decision:** Nature Genetics → American Journal of Human Genetics → Nature
Metabolism → Cell Genomics → Genome Medicine.

**Alternatives considered:** The original Revision_Plan listed only NG →
AJHG → CellGen → GenMed; Nat Metab was missing despite being a natural fit
for a cardiometabolic paper with a PRS deliverable (REQ-10, from
`GSD_BRIEFING.md` §5.2 gap #10).

**Why:** Nature Metabolism is the right home for this paper if T1+T2 lands
but doesn't support a Nature Genetics pitch. It's a step up from AJHG on
the metabolism axis and a step down from Nat Genet on the human-genetics
axis. Slotting it between AJHG and Nat Genet in the ranked order matches
the expected outcomes at each tier decision checkpoint.

**How to apply:** `manuscript/cover_letter/` has one versioned cover
letter per target journal. Checkpoint #2 decides between Nat Genet
(T1+T2+T3) and Nat Metab (T1+T2). REQ-10 locks this in.

---

## 2026-04-09 — All of Us: already have Controlled Tier; workbench-in / summary-out strategy

**Decision:** Carter already has All of Us Controlled Tier access. AoU
individual-level data stays inside the Researcher Workbench (Google Cloud).
Summary statistics and aggregate metrics can be exported. The pipeline
architecture for AoU-touching phases is:

- **Phase 9 (replication, T1):** Export GWAS summary statistics from AoU
  (either pre-computed or by running GWAS inside the workbench), bring them
  back to HPC, and run replication comparison alongside FinnGen / BBJ /
  MVP / etc. on HPC.
- **Phase 8 (PRS, T2):** Upload PRS-CSx weight files (~MBs, trained on HPC
  from public sumstats) into the workbench → score AoU participants against
  the weights inside the workbench → compute all validation metrics
  (R², AUC, Hosmer-Lemeshow, calibration slopes, NRI, DCA) inside the
  workbench → export summary-level performance tables and plots.

**Alternatives considered:** (a) Skip AoU entirely — we have 5+ replication
cohorts, but AoU uniquely adds Hispanic representation, which is valuable
for the cross-ancestry equity story; (b) Move the entire pipeline into the
workbench — overkill, expensive, and loses Snakemake reproducibility.

**Why:** The Researcher Workbench is a walled garden for individual-level
data. The upload-weights / score-inside / export-summaries pattern is the
standard approach for external PRS validation against AoU and keeps 95% of
the pipeline on HPC where Snakemake reproducibility is enforced.

**How to apply:** Phase 8 planning must include workbench-specific slices:
(1) package PRS weights for upload, (2) write a workbench-compatible scoring
script (PLINK2 or Hail — both available in AoU), (3) write a validation
metrics script that runs inside the workbench, (4) define the summary-level
export format. Phase 9 planning needs a slice for AoU GWAS sumstat export.

---

## 2026-04-09 — Git config scope: local only, no global changes

**Decision:** `git config user.name` and `user.email` are set **locally**
for this repo only (`Carter K. Clinton`, `ckclinto@ncsu.edu`). Global git
config was left untouched.

**Why:** No durable instruction exists to modify Carter's global git
config. Local scope is sufficient and reversible.

**How to apply:** If the institutional email is wrong, run
`git config user.email <correct>` inside this directory to override.

---

## 2026-04-09 — Public-data-only policy

**Decision:** Every GWAS / QTL / single-cell / reference dataset used in
this project must be **publicly available** or available under **standard
academic DUAs**. No wet-lab work, no industry data, no proprietary sources.

**Why:** This constraint was set before the GSD session started
(`GSD_BRIEFING.md` §4). It's enforced by Phase 10's "computational
substitute for wet-lab validation" design (Enformer + Borzoi + Sei +
AlphaMissense + public MPRA).

**How to apply:** Every new data source added to
`config/data_sources.yaml` must have a `license` field and a `public: true`
field. DUAs count as public for this purpose as long as they're open to
academic researchers.

---

## 2026-04-21 — Phase 2 Recovery: Z -> SuSiE -> Y -> CP#1-final sequence

**Decision:** Phase 2 first-production (2026-04-20) returned 0 Tier A signals from 1,010 colocalizations. Rather than sign CP#1-final on this state and trigger the AJHG fallback, adopt a 4-stage recovery plan authored in `.planning/phases/02-3-way-qtl-colocalization/RECOVERY_PLAN.md`:

1. **Stage 1 (Z):** Diagnose + fix the trait-pair coloc gap (`results/multitrait/coloc_summary.tsv` = 1 byte) via `/gsd-debug multitrait_coloc_empty`.
2. **Stage 2:** Raise Phase 1 SuSiE credible-set yield from 12/96 to >= 40/96 via `/gsd-debug susie_credible_set_yield` — address Category A (identity-LD fallback) by computing proper LD from 1000G, Category C (variant mismatch) via rsid/chr:pos harmonization, and introduce coloc.abf fallback for true-no-signal regions (Wallace 2021).
3. **Stage 3 (Y):** Expand gene scope via new sub-plan `02-07-distal-gene-scope-expansion` (`/gsd-plan-phase`) — add published distal regulatory targets (FTO->IRX3/IRX5, CDKN2A/B->ANRIL, APOE->TOMM40/APOC1, SH2B3->ATXN2/BRAP). Pre-register expansion criterion BEFORE re-running.
4. **Stage 4:** Full pipeline re-run + tier re-evaluation + CP#1-final decision via `/gsd-execute-phase` tail + `/gsd-verify-work`.

**Alternatives considered:**
- **X (Accept + AJHG):** Sign CP#1-final as-is, pivot to methods paper. Compliance-clean but discards substantial scientific value — the 26-row FTO signal with PP.H3=0.86, PP.H4=0.11 is textbook "shared locus, distinct causal variants" pointing at IRX3/IRX5 rather than FTO. Signing on a scope artifact would misrepresent the pipeline's output as a biological null.
- **Y alone (skip Z + SuSiE diagnostic):** Expand gene scope without fixing trait-pair coloc or SuSiE yield. Would likely still produce 0 Tier A because tiering joins QTL coloc onto trait-pair coloc and 88% of regions lack credible sets regardless of gene scope.

**Why this sequence:**
- **Z first** because it's cheap and diagnostic (2-4 hrs) — establishes whether the trait-pair gap is (a) cascading from empty tier3, (b) a missing Snakemake target, or (c) downstream run errors.
- **SuSiE second** because it's the structural bottleneck — gene-scope expansion only pays off at regions producing credible sets; trait-pair coloc gate is tied to finemap_tier3_coloc.tsv.
- **Y third** because with credible sets in place at more regions, expanded gene queries have something to colocalize against.
- **CP#1-final last** so the signing decision is made on corrected data, not artifact.

**Pre-registration obligation:** Stage 3's gene-scope expansion MUST be pre-registered as an OSF amendment BEFORE re-running, to avoid p-hacking critique. Criterion: "For each curated region, add distal regulatory gene targets supported by at least one of: (a) published Hi-C or promoter-capture-Hi-C enhancer-promoter link, (b) ABC model score > 0.015, (c) published CRISPRi or MPRA evidence, (d) eQTL coloc in at least one GTEx tissue with PP.H4 > 0.5, each published in a peer-reviewed article with DOI prior to 2026-04-21."

**How to apply:** Every step lands via a GSD command (`/gsd-debug`, `/gsd-plan-phase`, `/gsd-execute-phase`, `/gsd-verify-work`) with atomic commits. No direct source edits outside GSD workflows. All stage artifacts live under `.planning/phases/02-3-way-qtl-colocalization/` and `.planning/debug/`. Checkpoint outcomes update STATE.md and this file.

---

## 2026-04-21 — Pre-registration: Distal gene-scope expansion (RECOVERY_PLAN Stage 3, Option C)

**Decision:** Amend the QTL colocalization manifest to include **distal regulatory gene targets** for the two curated regions with existing GWAS-pair successes. First-pass scope is minimal (no Phase 1 re-fits): **IRX3 at FTO_16q12, ATXN2 at SH2B3_12q24**. Expansion to IRX5 / BRAP deferred pending first-pass tier outcome.

**Rationale (strategic scope — "Option C", 2026-04-21):**
- FTO_16q12 EUR has `PP.H4=0.1142` with `PP.H3=0.8633` at FTO/Muscle_Skeletal eQTL: textbook "shared locus, distinct causal variants" signature. Literature attributes the obesity GWAS mechanism to distal IRX3 / IRX5 regulation via SNP-disrupted adipocyte-progenitor enhancer (Smemo 2014 *Nature* 507:371-375; Claussnitzer 2015 *NEJM* 373:895-907).
- SH2B3_12q24 EUR has PP.H4=1.0 for two trait pairs (`hypertension↔stroke` @ 12:111910219 and `bmi↔hypertension` @ 12:111884608) at Tier C because the QTL manifest maps SH2B3_12q24 → SH2B3, but literature implicates ATXN2 / BRAP in cardiometabolic pleiotropy at this locus (Machiela 2011 *Nature Genet* 43:1217-1218; Kato 2011 *Nature Genet* 43:531-538).
- Expected yield from this minimal expansion: up to 3 Tier A signals (2 SH2B3 pairs + 1 FTO pair) clearing the CP#1-final threshold.

**Alternatives considered:**
- **Full scope (IRX3+IRX5+ATXN2+BRAP):** requires extending region windows and re-fitting ~20 Phase 1 SuSiE fits (~20 min compute). Deferred to second pass if first pass is under-threshold.
- **All 52 regions expanded:** violates the "strategic scope" guidance and amplifies multiple-testing without corresponding scientific justification.

**Pre-registration criterion (applied verbatim from RECOVERY_PLAN.md Step 3.3):**

> For each curated region, add distal regulatory gene targets supported by at least one of:
> (a) published Hi-C or promoter-capture-Hi-C enhancer-promoter link,
> (b) ABC model score > 0.015,
> (c) published CRISPRi or MPRA evidence,
> (d) eQTL coloc in at least one GTEx tissue with PP.H4 > 0.5,
> each published in a peer-reviewed article with DOI prior to 2026-04-21.

**First-pass gene additions (criterion satisfaction):**

| Region | Gene | Ensembl ID (GRCh38, verified Ensembl REST) | TSS position | Evidence | Criterion |
|---|---|---|---|---|---|
| FTO_16q12 | IRX3 | ENSG00000177508 | chr16:54,283,304 | Smemo 2014 *Nature* 507:371-375 (Hi-C + transgenic zebrafish); Claussnitzer 2015 *NEJM* 373:895-907 (CRISPR-Cas9 editing of causal enhancer) | (a), (c) |
| SH2B3_12q24 | ATXN2 | ENSG00000204842 | chr12:111,443,485 | Machiela 2011 *Nature Genet* 43:1217-1218 (ATXN2 variant rs653178 as sentinel in cross-trait pleiotropy); Kato 2011 *Nature Genet* 43:531-538 (ATXN2 BP association + eQTL coloc) | (d) |

**Authoritative Ensembl ID provenance:** Verified 2026-04-21 against Ensembl REST `/lookup/id/{ensg}?expand=0` (assembly=GRCh38). Commit record includes the REST response summaries in the manifest-builder comment.

**Window-extension policy:** NO window extensions in this pre-registration. Gene TSS must fall within the existing `start_grch38`/`end_grch38` region window:
- IRX3 @ chr16:54,283,304 falls inside FTO_16q12 window 53,766,088–54,366,088 ✓
- ATXN2 @ chr12:111,443,485 falls inside SH2B3_12q24 window 110,962,196–111,562,196 ✓
- IRX5 @ chr16:54,930,865 (outside by 565 kb) and BRAP @ chr12:111,642,146 (outside by 80 kb) are EXCLUDED from this pass.

**OSF amendment obligation:** Post this amendment to OSF (osf.io/az52u) before committing tier outputs with IRX3/ATXN2 rows included. Window policy and criterion wording above are the locked language.

**How to apply:** First-pass runs QTL coloc for IRX3 × 49 tissues × {eqtl, sqtl} at FTO_16q12 (196 new rows) + ATXN2 × 49 tissues × {eqtl, sqtl} at SH2B3_12q24 (196 new rows) = 392 new manifest rows. If any of the 3 existing GWAS-pair successes at SH2B3 / the FTO QTL signal flip to Tier A, sign CP#1-final. Else amend criterion for window-extension second pass (IRX5+BRAP + 20 Phase 1 re-fits) and re-OSF-post.

---

## 2026-04-22 — DEC-2026-04-22-01: Candidate-locus design abandoned (Amendment §2)

**Decision:** Abandon the 50-region candidate-locus design as the primary
discovery vehicle. Adopt genome-wide, hypothesis-agnostic region generation
(MTAG + CPASSOC + per-trait PLINK clumping union) as the Track B discovery
mode. The candidate-locus outputs survive as Track A's pre-specified methods
validation subset per Amendment §8.

**Alternatives considered:** (a) Keep candidate-locus as primary + expand
region windows; (b) Abandon entirely with no Track A salvage; (c) Pivot to
Track B + publish Track A as short-form methods paper (adopted).

**Why:** The candidate-locus design is circular by construction — regions
were chosen from prior literature that already reported cross-trait signal,
so the test is not discovering pleiotropy but estimating the replication
rate of prior claims under a new method (Amendment §2.1, §2.3). Stage 2
real-LD production fire 2026-04-22 made the circularity quantitative: SH2B3
× asthma EUR collapsed from identity-LD PP.H4 = 1.0 to real-LD n_cs_a = 0
(TRACK-A-FROZEN-NUMBERS.md §Stage 2 trait-pair coloc.susie), and 0 of 233
Tier assignments reached Tier A (§Tier assignments). Nature Genetics calibre
requires (a) genome-wide hypothesis-agnostic region generation, (b)
joint-signal discovery methods, (c) matched-ancestry real LD, (d)
multi-method triangulation, (e) non-EUR ancestry at non-footnote power,
(f) explicit comparator-catalog novelty claims (Amendment §2.1). The
candidate-locus design fails (a), (b), (e), (f).

**How to apply:** Track B M0–M6 execution follows Amendment §3. Track A
finalization ships the candidate-locus real-LD audit independently per
TRACK-A-PIVOT.md. The 205 analysis windows and 96 Stage 2 coloc cells are
reusable per Amendment §8 as (i) Track A's primary data and (ii) Track B's
candidate-locus validation appendix.

---

## 2026-04-22 — DEC-2026-04-22-02: 9-trait × up-to-2-ancestry inventory locked (Amendment §4)

**Decision:** Lock Track B trait inventory at 9 traits: BMI, T2D, stroke,
SBP, asthma, CAD, lipids (LDL primary; HDL/TG/TC secondary), eGFR, HbA1c.
Ancestry coverage follows Amendment §4 column "Ancestry" (EUR primary for
all nine; AFR via ancestry-stratified subfiles from DIAMANTE-AFR,
GIGASTROKE-AA, Giri 2019 MVP-AFR, GBMI-AFR, GLGC-AFR, CKDGen-AFR /
Morris 2019, MAGIC-AFR, PAGE / Loh 2022 BMI-AFR, Aragam 2022 CAD-AFR where
released). Phenotype definitions locked per §4 "Phenotype lock" column
(stroke = all-stroke, not ischemic-only; LDL-C continuous primary; eGFR
creatinine-based continuous).

**Alternatives considered:** (a) Keep 5 traits (BMI, T2D, SBP, stroke,
asthma) from pre-pivot; (b) Expand to 12 traits including three additional
cardiometabolic phenotypes (CRP, fasting glucose, fasting insulin); (c)
Lock at 9 per Amendment §4 (adopted).

**Why:** 5 traits underpowers MTAG / HyPrColoc joint-signal discovery
(Turley 2018 reported ~30–80 MTAG-novel loci per 4-trait run; more traits
in the correlated cardiometabolic block yield higher Class 1 novelty —
Amendment §7.3). 12 traits adds fasting-glucose / fasting-insulin overlap
with HbA1c and CAD–CRP correlations that inflate `--overlap` correction
burden without proportional discovery gain. 9 traits covers the shared
cardiometabolic architecture span (anthropometry → glycemic → blood
pressure → lipids → renal → inflammatory-respiratory-diabetes cross-talk
via asthma) while keeping the LDSC intercept matrix tractable
(9 × 9 = 81 pairs vs 12 × 12 = 144 pairs).

**Decision pending** (open human-action item in PROJECT.md): BMI EUR
primary source is Loh 2022 (n ≈ 1.1M, GRCh38, GIANT+23andMe) vs Yengo 2022
GIANT+UKBB (n ≈ 700k, GRCh37). SUMSTATS-UPGRADE.tsv rows 2–3 list both;
Amendment §9.3 draft text cites Yengo 2022. To be locked at M1 kickoff
before LDSC munge.

**How to apply:** M1 sumstats harmonization per SUMSTATS-UPGRADE.tsv;
`config/trait_inventory.yaml` enumerates 9 traits × ancestry coverage;
REQUIREMENTS.md REQ-TRAIT-INVENTORY enforces.

---

## 2026-04-22 — DEC-2026-04-22-03: MTAG + CPASSOC joint-signal method stack adopted (Amendment §3 M2)

**Decision:** Adopt MTAG (Turley 2018, *Nature Genetics*) with `--overlap`
correction using LDSC pairwise intercept matrix as the primary joint-signal
discovery method. Adopt CPASSOC (Zhu 2015, *AJHG*) SHom / SHet statistics
as an orthogonal joint-signal test for cross-method corroboration. Retain
mtCOJO (Zhu 2018) as an overlap-correction sensitivity check for trait
pairs with extreme cohort overlap (e.g., UKB-heavy triples).

**Alternatives considered:** (a) S-MultiXcan (Barbeira 2019) —
interpretability constraints with shared eQTL tissues complicate
cross-ancestry application; (b) GFM / Generalized Factor Model — strong
parametric assumptions and less tested at genome-wide scale; (c) mtCOJO
alone as the primary discovery method — mtCOJO is overlap-correction-focused
rather than joint-signal-discovery focused; (d) MTAG alone — does not
corroborate under `--overlap` mis-calibration (Amendment §10 risks);
(e) MTAG + CPASSOC adopted as the joint-signal method stack with mtCOJO as
sensitivity check.

**Why:** MTAG's constant-covariance assumption is violated when trait-pair
cohort overlap inflates correlated noise; `--overlap` with LDSC intercept
matrix is the Turley-2018-recommended correction for UKB / MVP dominance
across the 9-trait block. CPASSOC's SHom / SHet do not assume constant
covariance and provide the orthogonal corroboration filter per Amendment
§7.1 Class 1 high-confidence definition (MTAG ∩ CPASSOC). mtCOJO rounds out
the robustness story on top-N MTAG-novel loci. S-MultiXcan / GFM are
rejected on interpretability and overlap-handling grounds (Amendment §6
method-stack justification).

**How to apply:** M2 (m2-ldsc-mtag-cpassoc-discovery) executes: LDSC
pairwise rg → MTAG per-trait with `--overlap` → CPASSOC per-locus → PLINK
clump (p=5e-8, r²<0.01, 1Mb) → union region list. REQUIREMENTS.md
REQ-MTAG-OVERLAP + REQ-CPASSOC-ORTHOGONAL enforce.

---

## 2026-04-22 — DEC-2026-04-22-04: All-of-Us controlled-tier WGS as AFR LD source with egress-aware summary-only pipeline (Amendment §3 M3; AOU-LD-PIPELINE.md)

**Decision:** Adopt All-of-Us v7 controlled-tier WGS as the Track B AFR LD
reference panel. Build per-region LD matrices inside the AoU Researcher
Workbench (Terra) from ~60–95k AFR-ancestry participants (post-QC). Export
only summary-level artifacts (LD matrix + AF metadata) per AoU data-egress
policy. 1000G AFR (n = 661) is retained as a validation-only fallback and
as the comparator for AOU-LD-PIPELINE.md §9 Check 4 (AoU-AFR vs
identity-placeholder A/B).

**Alternatives considered:** (a) 1000G AFR (n=661) as primary — Amendment
§2.2 and TRACK-A-FROZEN-NUMBERS.md (AFR regions remained on
identity-placeholder under Stage 2 for this reason) document that n=661
produces LD SEs ~1/sqrt(n) ≈ 0.04 per off-diagonal, incompatible with
SuSiE-RSS fixed-LD assumption; (b) H3Africa (~3,500 continental African
samples) — same continental-vs-admixed mismatch as 1000G AFR, bigger N but
wrong population for MVP / AoU / PAGE targets; (c) PAGE (~50k admixed) —
right population, slower access, smaller than AoU; (d) AoU controlled-tier
(adopted) — ~150× 1000G AFR N, population-matched to a Track B target
cohort (AoU itself) and near-match for MVP-AFR / PAGE-AFR.

**Why:** n ≈ 60k AFR WGS collapses LD SE to ~1/sqrt(60,000) ≈ 0.004, three
orders of magnitude below 1000G AFR and adequate for SuSiE-RSS
credible-set construction. Population match matters more than panel size
in admixed populations — 1000G AFR YRI/LWK/ESN/GWD/MSL/ACB/ASW does not
reflect MVP-AFR / AoU-AFR haplotype structure. AoU summary-only export is
AoU-data-egress-policy-compliant (AOU-LD-PIPELINE.md §7); the export is
aggregate summary statistics where every LD cell is computed from all n
participants (trivially ≥20 per-cell suppression floor). Using AoU WGS for
AFR LD is a methodological novelty axis in its own right (Amendment §5);
to our knowledge no published pleiotropy fine-mapping at genome-wide scale
has used it.

**Risks acknowledged** (AOU-LD-PIPELINE.md §12):
- R1 AoU export classification must be confirmed in writing before any
  Dataproc compute (Amendment §10 risk row).
- R3 compute cost: staged launch (10-region dev → 500-region priority
  batch → remaining) caps exposure.
- R10 critical-path risk: 10-region dev pipeline completes BEFORE M2
  region generation to de-risk M4 start.

**How to apply:** M3 (m3-aou-afr-ld-panel-build) executes per
AOU-LD-PIPELINE.md §§2–14. REQUIREMENTS.md REQ-AOU-LD-EGRESS +
REQ-AOU-LD-VALIDATION enforce. AoU P&P registered at draft stage before
any cluster spend. Local layout per AOU-LD-PIPELINE.md §8.1 under
`data/processed/ld_reference/AFR_aou/` (gitignored); `.rds` conversion per
§8.2.

---

## 2026-04-23 — DEC-2026-04-23-01: Two-track publication strategy adopted

**Decision:** Track A (short-form methods paper on real-LD audit of 50
curated cardiometabolic regions) and Track B (genome-wide 9-trait
joint-signal discovery + 5 novel-variant classes on upgraded sumstats)
ship as scientifically independent, co-primary outputs of the
coloc_analysis program. Track A targets Genome Medicine (primary), AJHG
short report (fallback 1), Bioinformatics Applications Note (fallback 2).
Track B targets Nature Genetics. Track A preprint (bioRxiv) establishes
priority on the real-LD-audit framing independently of the Track B
discovery timeline.

**Alternatives considered:** (a) Single Nature Genetics manuscript
combining the candidate-locus audit and the genome-wide discovery —
rejected because the two aims have incompatible scope claims (Amendment §2
circularity argument); (b) Track A only (candidate-locus audit as sole
deliverable) — rejected because it would leave the pipeline investment in
M1 sumstats and the AoU-AFR LD methodological novelty unpublished;
(c) Track B only (genome-wide only) — rejected because it discards the
Stage 2 real-LD identity-LD-inflation finding (SH2B3 × asthma EUR
PP.H4 = 1.0 → n_cs_a = 0) which is itself a publishable methods
contribution (TRACK-A-FROZEN-NUMBERS.md §Usage); (d) Two-track (adopted).

**Why:** Track A quantifies how published candidate-locus pleiotropy claims
survive fully-pre-registered real-LD re-analysis — a forward-looking,
pre-specified methods validation contribution targeting cardiometabolic
genetics audiences at Genome Medicine / AJHG. Track B pursues genome-wide
hypothesis-agnostic joint-signal discovery across 9 traits × 2 ancestries
with AoU-AFR LD — the Nature Genetics contribution. Scheduling the Track A
preprint in 2026-05 / 2026-06 (per Amendment §11) ahead of Track B M6
(2027-04 / 2027-05) establishes priority on the real-LD-audit framing and
positions Track A as "pre-specified validation ahead of discovery" rather
than a post-hoc carve-out (Amendment §8).

**How to apply:**
- Track A finalization proceeds per TRACK-A-PIVOT.md and the ROADMAP
  "Track-A-finalization" sub-task checklist.
- Track B proceeds per Amendment §3 M0–M6 with the OSF amendment posted
  at end of M1 and before any M2 MTAG/CPASSOC run.
- Each manuscript has its own cover letter under `manuscript/cover_letter/`
  per REQ-10-equivalent carry-forward.
- Pre-pivot spine artifacts (Phases 0, 1, 2, 5, 9) serve both tracks per
  Amendment §8 preservation commitment.

---

## 2026-04-24 — DEC-2026-04-24-01: GRCh37 canonical target for M1 harmonized sumstats (override of Amendment §3 M1 "GRCh38" wording)

**Decision:** Keep GRCh37 as the canonical analytic plane across all M1
harmonized sumstats per CONTEXT D-08. Amendment §3 M1 text reading
"Harmonize to GRCh38" is overridden. Two b38-native sources (Loh 2022 BMI
rows 3-4 of `SUMSTATS-UPGRADE.tsv`; GBMI asthma rows 18-20) undergo
b38→b37 liftover at harmonize step using `pyliftover` plus
`data/external/liftover/hg38ToHg19.over.chain.gz` (UCSC chain staged
2026-04-25 in Wave 0 Task 2; SHA-256
`14a712e8e147d9fc8e9d87d51977b46f6f8ddb93efbe5d0843d86b6205f587b1`) with
a 5% drop-rate hard-fail ceiling per
`sumstats_utils.liftover_to_grch37`. All other 42 source files are b37
native.

**Alternatives considered:** (a) GRCh38 per Amendment §3 literal — would
require lifting 42 sources instead of 2 + forcing LDSC reference LD
re-keying + breaking Evangelou 2018 T1-spine reuse;
(b) GRCh37 per D-08 (adopted).

**Why:** 42 of 47 source files (TSV rows 2, 5–13, 14–17, 21–48 minus the
five b38 rows) are b37 native. 1000G Phase 3 reference LD panels at
`data/external/ldscore/eur_w_ld_chr/` (Phase 5 staged 2026-04-14 via
Zenodo URL-rot workaround per `feedback_url_rot_workarounds.md`) are b37.
Evangelou 2018 SBP-EUR at
`data/processed/sumstats_harmonized/hypertension.EUR.tsv.bgz` (T1 spine
reuse per Amendment §8) is b37. Flipping canonical to b38 would force 42
liftovers and a reference-LD rebuild for 0 analytic gain.

**How to apply:** Harmonizer modules for Loh 2022
(`harmonize_yengo.py` loh-variant path) and GBMI asthma (extended
`harmonize_gbmi.py` with opt-in liftover flag) call
`sumstats_utils.liftover_to_grch37(df,
chain_file="data/external/liftover/hg38ToHg19.over.chain.gz",
max_drop_rate=0.05)`. Filename convention appends `.GRCh37` token
unconditionally per CONTEXT D-09. The tests/m1/test_liftover.py
round-trip test gates the chain file. `OSF-AMENDMENT-TEXT-2026-04-22.md`
pre-paste check (Wave 0 Task 3) confirmed no lingering "GRCh38"
assertion in the OSF body — no edit required.

---

## 2026-04-24 — DEC-2026-04-24-02: AoU Researcher Workbench compute scope expansion into M1 (override of DEC-2026-04-22-04 M3-only scope)

**Decision:** Adopt AoU Researcher Workbench AFR-SBP derivation as the M1
D-06 fallback path. Wave 0 Probe 2 (2026-04-25, GWAS-Catalog Giri 2019
publication-page check at `ebi.ac.uk/gwas/publications/30578418`)
returned **NO-SUMMARY-FOUND** (zero GCST accession matches in 63,005-byte
HTML body); the D-06 primary path (public summary-only download) is
therefore unavailable as of M1 kickoff. This adds an AoU compute path
to M1 that DEC-2026-04-22-04 had previously scoped to M3 (LD panel
build) only. Egress-audit scaffolding from `AOU-LD-PIPELINE.md` §2
P1–P7 is reusable for AFR-SBP derivation with minimal adaptation. Dual
egress-audit entries are required (one for M1 AFR-SBP if the derivation
fires, one for M3 AFR-LD).

**Alternatives considered:** (a) Keep M1 AoU-free by dropping AFR-BP —
rejected per CONTEXT D-06 ("drop AFR-BP from M1 is off-table";
Amendment §4 locked inventory holds);
(b) dbGaP phs001672 DUA submission — rejected per CONTEXT D-06
(critical-path killer; REQ-PUBLIC-DATA-ONLY path avoids DUA where
possible);
(c) Expand scope per CONTEXT D-07 (adopted).

**Why:** Amendment §4 lock on the 45-row trait × ancestry inventory is
binding. D-06 primary (GWAS-Catalog public summary-only) is the
preferred path; with that path closed (Probe 2 outcome), D-06 fallback
(AoU) is the only REQ-PUBLIC-DATA-ONLY-compatible option. dbGaP is
explicitly off-table. Scope expansion to M1 is a pragmatic acceptance
of the cost (single AFR-SBP derivation, ~1–2 weeks AoU compute, reuses
the P1–P7 scaffolding M3 was going to require anyway).

**How to apply:** Wave 1 download rule for `SUMSTATS-UPGRADE.tsv` row 13
(MVP-Giri SBP × AFR) emits `status=deferred_d06_fallback` with a
`.placeholder` file pointing to the AoU derivation SOP at
`AOU-LD-PIPELINE.md` §2 P1–P7. Carter initiates the AoU Workbench
derivation out of band (this is REQ-AOU-LD-EGRESS-equivalent for M1;
not an `/gsd-execute-phase` task). M1 closeout does NOT block on
AFR-SBP; the Wave 3 LDSC bivariate-intercept matrix has at most 44
keys instead of 45 until the AoU artifact lands. M2 MTAG / CPASSOC may
proceed on the 44-key matrix; the AFR-SBP row joins post-derivation
without reorchestrating Waves 1–4.
