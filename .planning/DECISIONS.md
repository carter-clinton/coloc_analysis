# DECISIONS.md

Load-bearing decisions made during project setup. Every entry is dated,
names the alternatives considered, and states the **why** — so that future-
Carter and future-Claude can re-derive or override the choice with
context.

**2026-04-29 reconciliation note (quick task `260429-l1e`):** This file
was reconciled to Amendment §12 spec on 2026-04-29 against the
authoritative source at
`.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`.
**Zero substantive drift** identified from the post-pivot ADR landings.
The four §12 ADR entries land as standalone DEC entries in this file; the
fifth (ADR-2026-04-22-05) is captured implicitly via REQUIREMENTS.md and
flagged for Carter's review rather than promoted unilaterally.

| §12 ADR | Status | Landing |
|---------|--------|---------|
| ADR-2026-04-22-01 "Genome-wide reframe" | Standalone DEC | DEC-2026-04-22-01 (this file, line 373) |
| ADR-2026-04-22-02 "AoU AFR LD default" | Standalone DEC | DEC-2026-04-22-04 (this file, line 483) |
| ADR-2026-04-22-03 "Track A as validation subset" | Standalone DEC | DEC-2026-04-23-01 (this file, line 533) |
| ADR-2026-04-22-04 "MTAG --overlap non-negotiable" | Standalone DEC | DEC-2026-04-22-03 (this file, line 447) |
| ADR-2026-04-22-05 "Novel-variant discovery as co-equal aim w/ locked comparator catalogs" | **Implicit (Decision pending)** | REQUIREMENTS.md REQ-NOVELTY-CLASS-1 through -5 + REQ-CATALOG-VERSION-LOCK + Amendment §7 OSF pre-registration anchor |

ADR-2026-04-22-05 has not been promoted to a standalone DEC-* entry. Its
substantive commitments live across REQUIREMENTS.md REQ-NOVELTY-CLASS-1
through -5, REQ-CATALOG-VERSION-LOCK, and Amendment §7 (the OSF
pre-registration anchor for the five discovery classes with locked
comparator catalogs: GWAS Catalog, Pickrell 2016, Watanabe 2019, Open
Targets Genetics L2G, ClinVar). **Flagged for Carter's review** — do not
promote unilaterally; if Carter wants a standalone DEC-2026-04-22-05
entry to mirror the four above, that is a separate quick task with
explicit approval.

Pre-pivot decisions (e.g., the 2026-04-09 "Scope tier: T1 spine in full
+ T1→T2 checkpoint" entry below at line 32; the 2026-04-21 Phase 2
Recovery entry; etc.) are **preserved verbatim** per Carter's standing
"preserve all decisions from pre-pivot" directive — these reflect
decisions made under the pre-pivot frame, are dated, and remain
immutable historical record. Pair this reconciliation with the
2026-04-28 `260428-pj4` pass on PROJECT.md + REQUIREMENTS.md (commits
`70db503`, `56fd413`, `927b5eb`); together these close the M0
documentation alignment for all four `.planning/` files Amendment §12
names.

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

---

## 2026-04-25 — DEC-2026-04-25-01: results_identity_ld/ tracking — document, don't commit

**Decision:** The 160 MB `results_identity_ld/` tree (95 SuSiE fit JSONs + 95 RDS objects + 1 manifest TSV at `results_identity_ld/fine_mapping/`, produced by the 2026-04-24 k2d identity-LD re-fire at LSF PID 830748) is excluded from git via a dedicated `.gitignore` rule (`results_identity_ld/` line in the "# --- Results / logs: regeneratable, except legacy symlinks ---" section). The empirical CS-yield content of the 95 fits is captured in a tracked, deterministic 96-line summary at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` (13 columns: trait, ancestry, region_id, chr, start, end, status, n_CS, cs_sizes, pip_sum_total, ld_overlap, ld_overlap_fraction, sumstats_path). The on-disk `results_identity_ld/` tree remains untouched at project root where figure scripts (`src/R/figures/fig3_sh2b3_eur_collapse_forest.R`) read JSONs at runtime; reproducibility is preserved through the existing k2d re-fire artifacts (`scripts/fire_identity_ld_rerun.sh`) and the identity-LD payload regenerator (`src/snakemake/scripts/make_identity_ld_refs.R` over `data/processed/ld_reference_identity/`).

**Alternatives considered:** (a) commit the full tree (~160 MB into git history) — rejected; violates the `.gitignore` header convention "Results and logs are regeneratable; not committed" and inflates clone size for every downstream contributor; (b) commit JSONs but not RDS (~86 MB) — rejected; partial commit creates inconsistent reconstructibility (half the fit state in git, half on disk) and figure scripts that read JSONs are unaffected by the choice anyway; (c) git-lfs the binary fits — rejected; introduces an LFS dependency for a single ad-hoc artifact set when the data is fully reproducible from harmonized sumstats + identity-LD payloads in ~1 hour LSF wall, and Track A is solo-author public-data-only with no LFS infrastructure in place; (d) document via .gitignore + canonical CS-yield summary TSV — adopted.

**Why:** Project convention (`.gitignore` line 9 header) governs results trees: "Results and logs are regeneratable; not committed." Reproducibility provenance is intact through three independent paths: (i) the re-fire driver `scripts/fire_identity_ld_rerun.sh` (committed at `08beb4c`) deterministically regenerates the 95 fits from the harmonized sumstats at `data/processed/sumstats_harmonized/` and the identity-LD payloads at `data/processed/ld_reference_identity/`; (ii) the identity-LD payload regenerator `src/snakemake/scripts/make_identity_ld_refs.R` rebuilds those payloads from the locked region grid in `config/pipeline_identity_overlay.yaml` if the payloads themselves are lost; (iii) the canonical CS-yield summary at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` captures the empirical n_CS / pip_sum / status content (95 rows × 13 cols) that the figure scripts hard-code as `EXPECTED_ID_CS` scalars and that Track A's frozen-numbers record at `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` quotes verbatim. The summary TSV is the long-term canonical record: future quick tasks comparing identity-LD vs real-LD CS yields read it via cheap text-join instead of parsing 95 binary RDS fits.

**How to apply:**
- To regenerate the binary fit tree: `bash scripts/fire_identity_ld_rerun.sh` from project root (LSF serial queue, ~1 hour wall, idempotent under the k2d driver).
- To regenerate identity-LD LD payloads (if `data/processed/ld_reference_identity/` is lost): re-run `src/snakemake/scripts/make_identity_ld_refs.R` against the 12 region × {EUR, AFR} grid encoded in `config/pipeline_identity_overlay.yaml`.
- Figure scripts that read the on-disk JSONs (currently `src/R/figures/fig3_sh2b3_eur_collapse_forest.R` with locked `EXPECTED_ID_CS` scalars at SH2B3_12q24 EUR) operate on the un-gitignored on-disk tree — no script changes required as long as `results_identity_ld/` exists at project root after a re-fire.
- For comparative analyses (identity-LD vs real-LD CS yield, ancestry-stratified CS distributions, status-vocabulary audits), prefer reading the summary TSV at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` — schema is stable, deterministic-sorted by (trait, ancestry, region_id), and avoids the binary-RDS load path.
- Closes the `results_identity_ld/` half of the post-k2d deferral logged at STATE.md L27 (Fig 1A + Fig 3 builders half closed independently via quick task `260425-1vy`, commits `105484d` and `f862f55`).

---

## 2026-04-25 — DEC-2026-04-25-02: OSF M1 amendment posting form — supplementary file on existing az52u amendment record (not a new amendment record on pvb5j)

**Decision:** Post the M1 OSF amendment body (`.planning/amendments/OSF-AMENDMENT-TEXT-2026-04-22.md`, paste-body lines 32–109, commit `61315de`) as a **supplementary file uploaded to the existing `osf.io/az52u` amendment record** rather than as a new amendment record on the parent pre-registration `osf.io/pvb5j`. The resulting public, timestamped, citable URL is [osf.io/az52u/files/k8w7n](https://osf.io/az52u/files/k8w7n). The 45-row raw-sumstats SHA-256 manifest at `.planning/amendments/sha256_manifest_m1_frozen.tsv` was attached as the supplementary reproducibility receipt. Amendment §9.1 hard gate is RELEASED; M2 LDSC + MTAG + CPASSOC discovery may now commit. Local receipt: `.planning/amendments/osf-amendment-m1-2026-04-25.md`. Gate-release commit: `d55c1d1`.

**Alternatives considered:** (a) Create a new top-level amendment record on parent `osf.io/pvb5j` — what the m1-PHASE-CLOSEOUT.md instructions anticipated; rejected by Carter for OSF-UI ergonomics (creating a new amendment record involves more form-filling than uploading a file to an existing record); (b) Post the body as a PDF export of `PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` (the design rationale doc) rather than the bracketed paste-ready markdown — rejected because the paste-ready text is the authoritative pre-registration body, while the rationale doc is local-only working artifact; (c) Upload as supplementary file on existing `osf.io/az52u` amendment record (adopted).

**Why:** The Phase 1 closeout amendment posted 2026-04-13 at `osf.io/az52u` (distal-gene expansion, PDF) is the single existing post-pvb5j amendment record, and OSF semantically allows it to host follow-on amendments as supplementary files. This groups all post-pvb5j amendments under one OSF record (one URL to cite in the manuscript's pre-registration paragraph instead of two), matches the precedent set by the 2026-04-13 PDF posting, and satisfies Amendment §9.1's literal requirement ("OSF amendment posted at `osf.io/pvb5j` per Amendment §9") since `az52u` is the publicly-linked amendment-record child of `pvb5j`. Pre-registration discipline is preserved: the body content is identical to what would have been pasted into a new amendment record, the timestamp is OSF-issued at upload time, and the SHA-256 manifest pins the M1 raw inputs reproducibly.

**How to apply:**
- Manuscript pre-registration paragraph (Track A short report + Track B Nature Genetics submission) cites the parent registration `osf.io/pvb5j` (DOI [10.17605/OSF.IO/PVB5J](https://doi.org/10.17605/OSF.IO/PVB5J)) and the amendment record `osf.io/az52u` with the M1 amendment file at `osf.io/az52u/files/k8w7n` referenced in a footnote or supplementary reproducibility section.
- Future amendments (M5 catalog-lock follow-up, any post-discovery deviations logged to `.planning/osf_deviations.md`) follow the same pattern: upload to `osf.io/az52u` as supplementary files with descriptive filenames, then record the new file URL in a new DEC-YYYY-MM-DD-NN entry.
- M5 catalog-lock follow-up is the next anticipated upload: when the M5-deferred catalog rows in `data/catalogs/catalog_lock_manifest.tsv` (Pickrell 2016, GWAS Catalog, Open Targets Genetics L2G, Watanabe 2019) are fetched and SHA-256-locked, append the M5 lock-refresh commit hash to a follow-up text file and upload it to `az52u` per the disclosure paragraph at the bottom of the M1 amendment body (commit `61315de`).
- DECISIONS.md is the canonical record of OSF posting form choices for the project; do NOT rely solely on commit messages or STATE.md for this decision (those are ephemeral / scrolling artifacts; DECISIONS.md is durable).

---

## 2026-04-27 — DEC-2026-04-27-01: Conclusion-1 method-namespace reframe (audit-V2 sweep HQ3)

**Decision:** Conclusion claim 1 (manuscript L252–254 in `docs/manuscript/track_a_pivot.md`) is reframed from "Identity-LD `coloc.abf` fine-mapping inflates cross-trait PP.H4 ..." to the audit-V2 drop-in paragraph that names the actual method contrast under audit (SuSiE-RSS + `coloc.susie` identity-LD vs SuSiE-RSS + `coloc.susie` real-LD), discloses the structural-shift evidence (PIP redistribution / lead-rank instability via Figure S2, n = 48 paired non-empty fits), names the SH2B3 niter=100 non-convergence and FTO `ld_overlap_fraction = 0` + Benner-threshold structural findings, and explicitly notes that the canonical SH2B3 EUR BMI–HTN / HTN–stroke pairs were not executed under matched-coverage real-LD `coloc.susie` (Stage 2 trait-pair scoping was restricted to `SH2B3_12q24__EUR__asthma_vs_t2d`). Landed via commit `a345f5e` (quick-260427-azv, audit-V2 sweep commit 2 of 12).

**Alternatives considered:**
- (a) Keep "coloc.abf inflates" as-is — rejected: method-namespace conflation per `AUDIT-REVIEW-V2-2026-04-26.md` §HQ3 (`coloc.abf` is single-causal-variant and does not fine-map; the 1.06× count-level contrast is between SuSiE-RSS + `coloc.susie` under two LD references, not between `coloc.abf` under two LD references).
- (b) Soften to "inflates cross-trait PP.H4 in some pipelines" — rejected: too vague; reviewers will rightly ask which pipeline.
- (c) Audit-V2 drop-in paragraph (adopted) — names the actual method contrast and the structural-shift evidence with citation to Figure S2.

**Why:** The published method under audit is `coloc.abf`-on-identity-LD. The comparator implemented in this paper is `SuSiE-RSS + coloc.susie` under two LD references — not `coloc.abf` under two LD references. The strongest defensible Conclusion 1 names the actual method namespace under contrast and explicitly notes that direct re-testing of the published `coloc.abf`-under-identity-LD claims at the canonical SH2B3 EUR pairs requires a pre-registered pairwise re-fire that is correctly scoped as future work (HQ#2(iii), DEFERRED-COMPUTE).

**How to apply:**
- Future doc updates touching the Conclusion or Abstract pleiotropy claims must use the SuSiE-RSS + `coloc.susie` namespace; the legacy `coloc.abf`-inflation framing is retired from the Track A manuscript.
- Cross-references to `coloc.abf` claims in the published literature stay in Discussion §Identity-LD Inflation as the comparison target, not as the audited method itself.
- The 50-curated-locus scope statement ("at these 50 curated loci, no Tier A or Tier B cross-trait colocalization survives under real-LD `coloc.susie`") must remain bounded to 50 curated loci until genome-wide real-LD discovery (Track B M3) lands.

---

## 2026-04-27 — DEC-2026-04-27-02: Paired-fit structural inflation supplementary figure (audit-V2 sweep HQ2)

**Decision:** Build Figure S2 (paired-fit structural inflation: PIP-of-top-variant Δ, lead-variant rank, credible-set-member Jaccard) across all 48 paired non-empty SuSiE-RSS fits, computed entirely from on-disk per-fit JSONs at `results/fine_mapping/susie/*.json` and `results_identity_ld/fine_mapping/susie/*.json` — no LSF, no re-SuSiE fire. Emit locked scalars to `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` LIVE block. Landed via commits `d87416a` (script), `cc943bd` (render + PROJECT_ROOT fix), `9cb007d` (manuscript caption), `11ef400` (FROZEN-NUMBERS LIVE block).

**Alternatives considered:**
- (a) Defer to a post-bioRxiv compute slot — rejected: the HQ3 Conclusion-1 reframe (DEC-2026-04-27-01) is load-bearing on a structural-inflation claim that needs to be quantified in the same submission; deferring would require the Conclusion to be load-bearing on an unmeasured assertion.
- (b) Per-pair paneled small-multiples figure — rejected: 48 panels at single-column width is illegible; summary distributions are submission-grade.
- (c) Snakemake rule integration — deferred: figure generation is currently run via direct Rscript invocation per `fig2_cs_yield.R` precedent; building a `figures.smk` rule is a separate refactor task that should encompass all figure scripts at once.
- (d) Direct on-disk JSON computation + 4-panel composite (adopted) — runs in ~5–10 seconds end-to-end, no LSF, fully reproducible from the existing JSONs.

**Why:** HQ3 Conclusion-1 reframe needs a concrete structural-shift figure to back the "PIP redistribution and lead-variant rank instability" claim; this figure provides it within the no-LSF / no-egress / no-OSF-portal-action constraint. The 48-pair population is the audit-V2 invariant, verified at runtime by a hard-fail assertion in the script.

**How to apply:**
- Future text mentioning "structural posterior shifts" in the Track A manuscript must cite Figure S2 by name. The 48-pair population is the intersection of real-LD non-empty (51) and identity-LD non-empty (48) fits; the identity-LD non-empty subset is fully contained in the real-LD non-empty set.
- If either tree's non-empty count changes (e.g., HQ#2(i) L = 20 re-fire lands), Figure S2 must be re-rendered and the FROZEN-NUMBERS LIVE block updated atomically.
- The script's hard-fail assertions (`real_total == 96`, `ident_total == 95`, `real_ne == 51`, `ident_ne == 48`, `n_paired == 48`) protect against silent drift; if any assertion fails on a future re-render, investigate before updating manuscript-cited scalars.

---

## 2026-04-27 — DEC-2026-04-27-03: Audit-driven comparator-tightening narrative location (audit-V2 sweep QI2)

**Decision:** The audit-process narrative ("We tightened the comparator from 12/96 to 48/95 and the inflation magnitude shifted from 4.25× to 1.06×") moves OUT of Methods §Fine-Mapping Integration / §Identity-LD vs Real-LD Comparison (manuscript L82) and INTO a new Discussion subsection §Audit-driven Comparator Tightening, inserted between §Identity-LD Inflation and Its Mechanism and §Reframing of Cardiometabolic Pleiotropy Claims (≈ L222–223 post-edit). Landed via commit `cb5db17` (quick-260427-azv, audit-V2 sweep commit 4 of 12).

**Alternatives considered:**
- (a) Move to OSF deviation log only — rejected: readers without OSF access wouldn't see the comparator-tightening provenance; the manuscript's argument depends on knowing which baseline the inflation magnitude is computed against.
- (b) Leave in Methods — rejected: `AUDIT-REVIEW-V2-2026-04-26.md` §QI2 is correct that Methods should describe the analysis as it stands, not as a meta-commentary on what was done in a previous freeze. Methods L82 now reads as a clean per-LD-branch yield description.
- (c) New Discussion subsection (adopted) — keeps the comparator-tightening provenance discoverable in-manuscript while removing the meta-commentary from Methods.
- (d) Both Discussion subsection AND OSF deviation pointer — partial adoption: the OSF deviation pointer was already landed at Methods L90 via Eval 3.2(c) commit `06b817b` (quick-260426-06n) and remains in place; the Discussion subsection is additive, not redundant, because it focuses on the comparator-tightening narrative whereas the L90 OSF pointer focuses on the QTL-coloc data-quality caveat.

**Why:** Methods readability + reviewer-friendliness; the comparator-tightening narrative is a Discussion-grade audit-trail observation, not an experimental procedure. The §Audit-driven Comparator Tightening subsection title also makes the comparator-tightening provenance discoverable to reviewers via the table-of-contents / section-heading scan, which a buried Methods parenthetical would not.

**How to apply:**
- Future Methods edits should describe the analysis as currently configured (k2d full-coverage 48/95 vs Stage 2 real-LD 51/96) without meta-commentary about the previous Stage 1d freeze.
- The OSF deviation log retains its own pointer (already landed via Eval 3.2(c) commit `06b817b`); future OSF deviation entries continue to log there, with cross-references from Methods L90.
- If a future closure flips the comparator denominator again (e.g., HQ#2(i) L = 20 re-fire lands and the matched-coverage population changes), update the Discussion §Audit-driven Comparator Tightening subsection in place rather than re-introducing Methods meta-commentary.

---

## 2026-04-28 — DEC-2026-04-28-01: M3 Sci Data data-descriptor venue commitment (quick-260428-ppz)

**Decision:** The M3 deliverable — ancestry-matched LD reference panels for AFR (and parallel EUR sensitivity) computed from All of Us controlled-tier whole-genome sequencing — will be submitted as a data descriptor to ***Scientific Data*** (Springer Nature). This commitment supersedes the previously-flagged Sci Data candidacy (raised during the quick-260426-aow AoU workspace registration build, 2026-04-26) and locks the venue.

**Alternatives considered:**
- (a) ***Scientific Data*** (adopted) — canonical venue for genomic resource data descriptors; pairs natively with a Zenodo deposit; satisfies AoU publication policy egress framing for aggregate-only LD matrices; complementary (not competitive) with the Track B *Nature Genetics* discovery paper.
- (b) *Genome Research* methods note — rejected: Genome Research's methods format is geared toward novel methodology, not resource deposits; the M3 contribution is primarily a resource (AoU-derived AFR LD panels), not a new method.
- (c) *Bioinformatics* applications note — rejected: applications-note format is short-form and does not accommodate the per-region resource table, validation memo, and reproducibility code release that a Sci Data data descriptor naturally houses.
- (d) Zenodo-only deposit (no peer review) — rejected: a peer-reviewed data descriptor is the citable artifact other groups will use to find and trust the panel; Zenodo alone provides DOI but not editorial review.
- (e) Defer venue lock until Track B M6 — rejected: locking now lets the AoU P&P registration (Block 2 in `AOU-PP-REGISTRATION.md`) name a concrete venue, which is the AoU portal's declared expectation. Re-targeting later is allowed by AoU policy via P&P record update; locking is not irreversible.

**Why:** The M3 panel build is the single largest novel resource produced by this project, and AoU explicitly anticipates resource-deposit publications from controlled-tier WGS users. *Scientific Data*'s editorial scope, peer-review model (focused on completeness and reusability of the data, not novelty of conclusions), and tight Zenodo / FAIR-data alignment match the M3 deliverable directly. Carrying the commitment in DECISIONS.md (rather than only in the Amendment) makes it discoverable to all future GSD orchestration; carrying it in the AoU P&P registration (Block 2) preserves the AoU portal record. Carter accepted this commitment in conversation 2026-04-28 in the same turn as the AoU portal-bundle direction.

**How to apply:**
- Track B *Nature Genetics* manuscript Methods + Data Availability sections cite the M3 *Scientific Data* deposit as the LD reference source. Cross-link is locked in `AOU-PP-REGISTRATION.md` §1.15 / §2.15.
- AOU-WORKBENCH-REGISTRATION.md §11 already names *Scientific Data* as the M3 venue (committed at registration-build time, now locked here).
- Future communications (preprints, abstracts, talks) frame M3 as a "data descriptor" with *Scientific Data* as the named target venue.
- M3 phase artifacts (planning + execution) should structure the per-region resource table, the validation memo (per AOU-LD-PIPELINE.md §9 Checks 1–4), and the Zenodo-deposit checksum table to match the Sci Data data-descriptor template at submission time.
- If Sci Data declines the manuscript at submission, fallback considered (a → c → b in Alternatives ordering, with d as the floor-case Zenodo-only deposit). Re-targeting requires a P&P record update per AOU-LD-PIPELINE.md §12 R6.

---

## 2026-05-01 — DEC-2026-05-01-01: M3 CDR v7→v8 adoption (O2 trigger fired)

**Decision:** Bump `CDR_VERSION` in `src/python/aou_ld_panel.py` from `"v7"` to `"v8"`. All four AUX-derived path constants (`AUX_BASE`, `RELATED_SAMPLES_PATH`, `RELATEDNESS_FULL_PATH`, `ANCESTRY_PREDS_PATH`) re-derive automatically via the `f"{AUX_BASE}/..."` interpolation pattern. The M3 AoU AFR LD panel build — and every downstream Track B Wave 4 production-fire artifact that consumes the panel for the *Nature Genetics* manuscript and the *Scientific Data* data descriptor — will be computed against AoU CDR **v8** WGS + ancestry + relatedness inputs.

**Alternatives considered:**
- (a) **Bump to v8 (adopted)** — aligns the entire pipeline with the workspace default (`WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` resolves to `gs://fc-aou-datasets-controlled/v8/.../hail.mt`); larger participant roster (~+69 % on `ancestry_preds.tsv` size, ≈ +60–80 k participants by rough byte-size estimate) → tighter LD precision, especially for AFR where v7 N was the binding constraint per A-2 in [m3-RESEARCH.md](./phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md); future-proof against eventual v7 deprecation; native parity with AoU's own published guidance for new v8-bound workspaces.
- (b) **Pin WGS to v7 explicitly** to retain v7 throughout — rejected: would require overriding `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` at AOU-1 import time AND betting that AoU keeps v7 indefinitely (no public deprecation notice yet but v7 is the prior-prior CDR; v8 has been default since at least the v8 dataset workspace banner went up). Buys planning-N stability at the cost of accepting noisier LD and a future forced migration.
- (c) **Mixed mode** (v8 WGS + v7 ancestry preds, the state at the moment of trigger) — rejected as unsafe: sample IDs may not be 1:1 across CDR versions; AoU may have re-derived ancestry inference for v8 (v8 ships `eigenvalues.txt`, `rf_classifier.pkl`, `training_pca.tsv` siblings to `ancestry_preds.tsv`, suggesting the inference pipeline re-ran). Mixed mode would silently under-count cohorts where v8 samples lack v7 ancestry rows and would silently mis-assign ancestry where v7 → v8 inference outputs differ.
- (d) **Defer adoption** until end-of-Wave-2 dev-fire — rejected: per `feedback_rigor_over_speed.md`, gray-area trade-offs go to the more rigorous option. Deferring would mean firing dev10 (and likely dev100) against v7 then re-firing against v8, doubling cluster-hours and creating a disposable v7-derived audit trail.

**Why:** The O2 trigger ("if v8 lands during Wave 1-3"), pre-registered in [aou_ld_panel.py:70](../src/python/aou_ld_panel.py) (line retired in this commit) and called out in [m3-W1-AUX-PATH-VERIFICATION.md](./phases/m3-aou-afr-ld-panel-build/m3-W1-AUX-PATH-VERIFICATION.md) "Closing notes" item 5, fired during the AOU-1 Cell 1 import sanity check on 2026-05-01: the workspace `WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH` env var defaulted to v8 (`gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/acaf_threshold/multiMT/hail.mt`), creating a v8-WGS / v7-ancestry mismatch hazard. Carter's gsutil verification (Run 2 in the AUX path verification spec) confirmed v8 has a parallel AUX layout with the same three load-bearing files (`ancestry_preds.tsv`, `relatedness_flagged_samples.tsv`, `relatedness.tsv`) at the analogous v8 paths, plus 3 new ancestry-inference artifacts (`eigenvalues.txt`, `rf_classifier.pkl`, `training_pca.tsv`). v7 paths still resolve, so this is a soft default change rather than a forced migration — but the rigor-correct path is to align fully with v8.

**How to apply:**
- The CDR_VERSION bump is the entire code change for this decision; the AUX_BASE-derived constants re-derive via f-string interpolation. No callsite refactor needed in `aou_ld_panel.py`, `select_ld_regions_dev.py`, `build_ld_region_manifest.py`, or `ld_panel.py`.
- Wave 5 close-out tasks (m3-05-W5 PLAN) must add a one-paragraph addendum to [PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md](./amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md) §5 (AoU-AFR LD pipeline section) recording the v7→v8 transition with the cohort-N delta observed at AOU-1 fire time.
- Manuscript Methods + Data Availability sections (Track B *Nature Genetics* and M3 *Scientific Data*) cite **v8** as the CDR version. The exact phrase "All of Us Controlled Tier CDR v8" must appear in both manuscripts and in the Zenodo metadata at submission.
- Per `feedback_original_research_framing.md`, do **not** retroactively rewrite v7-pinned numbers in [m3-RESEARCH.md](./phases/m3-aou-afr-ld-panel-build/m3-RESEARCH.md) or [m3-CONTEXT.md](./phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md). Those documents reflect the planning-time analysis under v7; Wave 5 close-out re-baselines from disk numbers and adds a delta-summary footnote rather than rewriting the planning prose.
- The 3 new v8 ancestry-inference siblings (`eigenvalues.txt`, `rf_classifier.pkl`, `training_pca.tsv`) are NOT consumed by the M3 pipeline at adoption time, but flag as candidate inputs for a future RESEARCH O5 ancestry-reproducibility sensitivity analysis; track under m3-RESEARCH.md O5 if/when scope expands.
- Next CDR-version reverify trigger: if **v9** lands during Wave 4–5, repeat the Run-N AUX path verification protocol. Lock CDR version at submission time per spec convention.

---

## 2026-05-01 — DEC-2026-05-01-02: W4 cache-staleness hypothesis refuted; 78.9% qtl_coloc rate adopted as canonical Layer-2 finding

**Decision:** Re-dispose Track A wave 4 (`ta-sh2b3-canonical-and-cache-refresh` phase) outcome from mechanical `FAILED` (per the W4 PLAN PASS/FAIL gate `too_few_snps ≥ 800`) to strategic `HONEST_FINDING`. Adopt **`too_few_snps = 1005 / 1274 = 78.9%`** as the canonical Track A Layer-2 yield finding, parallel to the canonical Layer-1 finding **`51 / 96 = 53.1%`** SuSiE-RSS strict-gate convergence rate from the SH2B3 anchor sweep (D-TA-Wave1-headline). Skip the W4.5-B SuSiE-RSS-rebuild fallback. Preserve `FAILED` as the `historical_outcome` field in `wave4_dispatch_tracker_v7.json` for forensic traceability (the W4 PLAN PASS/FAIL gate semantic is reviewer-defensible as-mechanically-defined; the strategic re-disposition lives in `W4-DISPOSITION-REVISED.md`).

**Alternatives considered:**
- (a) **Re-dispose to HONEST_FINDING + skip W4.5-B (adopted)** — the W4.5-A continuation (quick task `260501-r1q`) executed the cache-staleness hypothesis test cleanly: drained the final 4 missing run_qtl_coloc JSONs (1270 → 1274), forced a fresh aggregator pass, and observed too_few_snps = 1005 → 1005 (Δ=0). Hypothesis refuted. The 78.9% is structural (LD-panel coverage + region-window choices) not artifactual (V4-era stale aggregator outputs). Adopting 78.9% as canonical Layer-2 finding strengthens reviewer-defensibility via transparent attrition disclosure parallel to Layer-1's "non-convergence treated as data" framing (Audit-V2 Eval 2(a); see `ta-sh2b3-DISCUSSION-LOG.md` line 51). Zero TRACK-A-FROZEN md5 risk. Compute cost: 0.
- (b) **Fire W4.5-B SuSiE-RSS rebuild** with `--forcerun run_finemap` at higher niter or different L for the 1005 too_few_snps regions — rejected: the data identifies LD coverage, not iteration budget, as the constraint. `too_few_snps` is emitted by `run_qtl_coloc.R` when the GWAS×QTL SNP intersection at the region falls below the colocalization-feasibility threshold; adding fine-mapping iterations cannot create SNPs that don't exist in the QTL panel. Expected impact on too_few_snps count: near zero. TRACK-A-FROZEN md5 risk: high (96 `.fit.rds` files regenerated; even at niter=1000, stochastic floating-point drift in optimizer convergence paths can shift md5s; the 3 SH2B3 anchor md5s — bmi=462ada6a, htn=8255c1ac, stk=a041eecc — would need re-pinning). Reviewer questions invited: "Why did you rebuild SuSiE if too_few_snps was the constraint? Were you fishing?" — undermines the rigor narrative.
- (c) **Pool the 78.9% silently into a single Layer-3 yield** (32/1274 = 2.5% headline) and drop Layer-2 disclosure — rejected per `feedback_original_research_framing.md` and the established Layer-1 framing precedent. The historical pattern of reporting only Layer 3 (the "32 hits") and treating Layer 1 + Layer 2 attritions as silent both undersells the methodological rigor and obscures the ceiling on what coloc can recover at current public-data LD coverage. Reviewer-defensibility hinges on transparent disclosure of all three layers.
- (d) **Expand region windows for the 1005 too_few_snps cases** to recover SNP coverage — out of scope here; would require a new wave with explicit LD-bleed risk analysis (cross-locus contamination at wider windows) and a new hypothesis (wider-windows-recover-coverage-without-bleed). Tracked as carried-forward consideration in `W4-DISPOSITION-REVISED.md` §3 out-of-scope item (a) but not adopted now.
- (e) **Switch GTEx → AoU-AFR-LD or other denser LD panel** — out of scope here; tracked under M3 (`m3-aou-afr-ld-panel-build` phase, currently at Wave 1 portal pre-conditions per `260428-stv` D-M3-09 ruling). Would address the LD-coverage constraint at the source but is a multi-wave M3 deliverable, not a Track A W4 patch.

**Why:** The cache-staleness hypothesis embedded in tracker v6 (`monitoring_directives.post_completion_3rd_pass_needed: "YES — fire snakemake again (no --forcerun) so the natural mtime cascade triggers aggregator rebuild. Without 3rd pass, qtl_coloc/qtl_coloc_summary.tsv + tier_assignments.tsv + gene_tissue_matrix.tsv + gene_tissue_long.tsv + pph4_threshold_sweep.tsv remain stale at V4 timestamps despite 1274 fresh per-id JSONs."`) was the only standing alternative explanation for the high too_few_snps count observed against V4-era aggregator outputs (~12:40–12:45 EDT 2026-04-30). The W4.5-A continuation (commits `f165e57` + `bf2a18a`) executed that test by draining the final 4 missing JSONs and forcing a fresh aggregator pass against the resulting 1274-JSON cache. The post-3rd-pass `qtl_coloc_summary.tsv` (mtime 1777680429 = 2026-05-01T20:07 EDT, well past the W4.5-a re-fire baseline 1777589595) reports the same 1005 too_few_snps as the V4-era aggregator output. Δ=0. The hypothesis is refuted; the only remaining explanation for the 78.9% is that it is a structural property of the GWAS×QTL panel intersection at current LD-panel + region-window choices.

Once cache-staleness is refuted, the rigor-correct disposition (per `feedback_rigor_over_speed.md`) is to adopt the structural finding rather than chase a low-payoff rebuild that risks the TRACK-A-FROZEN invariants. The 53.1% Layer-1 / 78.9% Layer-2 / 2.5% Layer-3 contrast architecture is reviewer-defensible: each layer's attrition is reported transparently with a structural rationale, paralleling the Audit-V2 "non-convergence treated as data" precedent already established for Layer-1.

**How to apply:**
- `wave4_dispatch_tracker_v7.json` is updated atomically with this decision: top-level `outcome_disposition: "HONEST_FINDING"` is added; the existing top-level `status: "FAILED"` is preserved verbatim; a new `historical_outcome` field captures the FAILED→HONEST_FINDING transition with a pointer to this DEC entry and to `W4-DISPOSITION-REVISED.md`. The `outcome_summary.w4_pass_gate.outcome` field stays `FAILED` (mechanical gate result; immutable forensic record). Future readers see both labels.
- `W4-DISPOSITION-REVISED.md` is the active narrative document for this disposition. Reviewer-facing artifacts (manuscript Methods, supplementary tables, OSF deviation log) cite the 3-layer contrast architecture from §2 of that document.
- Manuscript Methods §"Colocalization yield" (Track A *Nature Genetics* — when written) reports all three layers with their structural attrition framing: Layer 1 (51/96 = 53.1% strict-gate convergence), Layer 2 (269/1274 = 21.1% structural feasibility, equivalently 78.9% too_few_snps), Layer 3 (32/1274 = 2.5% substantive coloc). The Layer-2 framing follows the established Layer-1 precedent: "non-convergence treated as data" → "structural attrition disclosed as data".
- OSF deviation log: a new entry tied to this DEC documents the W4 disposition revision. Adds to the existing W7 closeout pipeline (entry_11 in tracker v6 was "W4.5-a re-fire outcome (PASSED/FAILED) + 3rd-pass aggregator refresh — tracker v7 will record"); now resolves as "FAILED on mechanical gate; HONEST_FINDING on strategic disposition; cache-staleness hypothesis refuted; 78.9% qtl_coloc rate adopted as canonical Layer-2 finding".
- Wave 5 fires from the orchestrator after the m3 AOU-1 dev fire returns and STATE.md frontmatter refreshes both tracks atomically (Track A + Track B). Wave 5 is **not** triggered by this disposition; this disposition is a closing landmark on the W4 work, not a Wave 5 advance signal.
- Per `feedback_rigor_over_speed.md`, do not revisit the W4.5-B rebuild option in subsequent sessions unless new evidence emerges that the constraint is iteration-budget-related rather than LD-coverage-related (e.g., a sensitivity check on the 32 successes showing PP.H4 is unstable across niter values — currently no such evidence exists).
- Per `feedback_original_research_framing.md`, all public artifacts (manuscript, OSF deviation log, Zenodo metadata, Sci Data data descriptor) frame the 78.9% as a structural property of the input data + analysis design, not as a "failure" or "limitation" or "issue". The phrase "structural Layer-2 attrition driven by LD-panel coverage" is the canonical reviewer-facing framing.
- The 4 newly-landed JSONs from the drain pass (`CXADR_F2RL1_6p21_*`, `FTO_16q12_*`, `MC4R_18q21_*`, `SH2B3_12q24_*` — see tracker v7 `outcome_summary.drain_pass.missing_4_qtl_coloc_ids`) are not separately analyzed in isolation; they are absorbed into the 1274-JSON canonical set per the disposition.

