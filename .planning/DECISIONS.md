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
ID-VS-REF-LD-STRATEGY.md. The 205 analysis windows and 96 Stage 2 coloc cells are
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
- Track A finalization proceeds per ID-VS-REF-LD-STRATEGY.md and the ROADMAP
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

**Decision:** Conclusion claim 1 (manuscript L252–254 in `docs/manuscript/id-vs-ref-LD.md`) is reframed from "Identity-LD `coloc.abf` fine-mapping inflates cross-trait PP.H4 ..." to the audit-V2 drop-in paragraph that names the actual method contrast under audit (SuSiE-RSS + `coloc.susie` identity-LD vs SuSiE-RSS + `coloc.susie` real-LD), discloses the structural-shift evidence (PIP redistribution / lead-rank instability via Figure S2, n = 48 paired non-empty fits), names the SH2B3 niter=100 non-convergence and FTO `ld_overlap_fraction = 0` + Benner-threshold structural findings, and explicitly notes that the canonical SH2B3 EUR BMI–HTN / HTN–stroke pairs were not executed under matched-coverage real-LD `coloc.susie` (Stage 2 trait-pair scoping was restricted to `SH2B3_12q24__EUR__asthma_vs_t2d`). Landed via commit `a345f5e` (quick-260427-azv, audit-V2 sweep commit 2 of 12).

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

---

## 2026-05-03 — DEC-2026-05-03-vcl-Item1: Track A venue locked at *Genome Medicine*

**Decision:** Lock the Track A primary submission venue at ***Genome Medicine*** (BMC, IF ≈ 13). Fallback ladder: *AJHG* short report → *Bioinformatics* applications note. bioRxiv preprint Day 1 regardless of venue selection. Quick task `260503-vcl` Pass 2 atomic commit consolidates this lock as the editorial trail closes the prior open-decision-pending posture in the manuscript body.

**Alternatives considered:**
- (a) **Genome Medicine (adopted)** — original-research article format aligns with the 5-figure roster + Figs S1–S7 supplementary scope; BMC house style accepts the disclosure-honest empty-row Table 1 framing; impact factor matches the audit's contribution profile (post-pivot real-LD audit of curated cardiometabolic pleiotropy claims at scale, with Wave 2 R2 SH2B3 BRANCH_C SURVIVE counter-example).
- (b) ***AJHG* short report (fallback)** — short-form format would compress the §SH2B3 case study + §Identity-LD Inflation mechanism prose; preserved as the second-rung fallback if Genome Medicine declines.
- (c) ***Bioinformatics* applications note (floor fallback)** — applications-note format is geared toward novel software methodology, not audit-of-published-claims; preserved as the floor fallback.
- (d) bioRxiv-only (no peer-review submission) — rejected: the Track A pivot's contribution is reviewer-defensibility of the candidate-locus design's real-LD survival rate, which requires peer-review imprimatur to land in the cardiometabolic pleiotropy literature ecosystem.

**Why:** Per `feedback_original_research_framing.md`, Track A is hypothesis-driven original research (real-LD audit of curated cardiometabolic pleiotropy claims), not a methods paper or a re-analysis-only commentary; *Genome Medicine* is the appropriate venue for the contribution profile. Locking the venue now closes the manuscript body's standing open-decision item and unblocks the Pass-6 bundle regeneration.

**How to apply:**
- Manuscript Methods §Software and Data Availability (L128) cites the canonical GitHub URL `https://github.com/carter-clinton/coloc_analysis` (aligned in Pass 1 of `260503-vcl`); the bundle build target `bin/build_id_vs_ref_ld_submission_bundle.sh` renders the manuscript per *Genome Medicine* house style.
- The fallback ladder is preserved in `.planning/amendments/ID-VS-REF-LD-STRATEGY.md`; revisit only if Genome Medicine declines at submission.
- Cross-reference: `.planning/amendments/track_a_decision_items_resolution_log.md` Item 1 (editorial trail).

---

## 2026-05-03 — DEC-2026-05-03-vcl-Item2: Aggregator freeze locked at Wave 5 R2-merge state (md5 558fca45…)

**Decision:** Lock the aggregator freeze for `results/qtl_coloc/tier_assignments.tsv` and `results/multitrait/coloc_summary.tsv` at the **Wave 5 R2-merge state** landed via quick task `260501-wdn`. The proposed 2026-04-26 freeze date (in the original manuscript decision-pending item 2) was advanced to capture the Wave 2 R2 SH2B3 EUR canonical-pair `coloc.susie` re-fire merge (3 substantive Tier-A signals at PP.H4 = 1.0 at rs3184504); the Wave 5 freeze is the canonical post-R2-merge state. `coloc_summary.tsv` md5 = `558fca45…` (37 rows total: 28 R1 canonical-locus + 9 R2 SH2B3 EUR canonical-and-lattice).

**Alternatives considered:**
- (a) **Wave 5 R2-merge freeze (adopted)** — captures the Wave 2 R2 substantive Tier-A pass at SH2B3 EUR (BRANCH_C SURVIVE per Wave 3 outcome decision token `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE`); aligns with the Stage 2 SH2B3 anchor `.fit.rds` md5 invariants (bmi.EUR=`462ada6a…`, hypertension.EUR=`8255c1ac…`, stroke.EUR=`a041eecc…`); zero TRACK-A-FROZEN risk.
- (b) Pre-R2-merge 2026-04-26 freeze (the original proposal) — rejected: would lock the manuscript body to the all-empty-PP.H4 R1 slice without the substantive 3-Tier-A SH2B3 R2 re-fire results, materially weakening the audit's reviewer-defensibility (the SH2B3 BRANCH_C SURVIVE is the load-bearing counter-example to a uniform-inflation reading).
- (c) Defer freeze until Track B M2 discovery returns — rejected: Track B M2 is many waves out (currently at m3-W2 in the m3-aou-afr-ld-panel-build phase per STATE.md); deferring freeze blocks Track A submission indefinitely; per `feedback_rigor_over_speed.md`, gray-area trade-offs go to the more rigorous + nearer-term path.

**Why:** The Wave 5 freeze is the canonical post-R2-merge state and matches the Stage 2 anchor md5 invariants exactly; per `feedback_state_md_keep_current.md`, locking aggregator state atomically with the relevant work prevents disconnect-resilient resume from drifting.

**How to apply:**
- Manuscript Table 1 row count derives from the Wave 5 freeze (3 SH2B3 EUR R2 Tier-A rows + R1 slice empty-body footer; see manuscript L168 + L276-279).
- `bin/build_id_vs_ref_ld_submission_bundle.sh` Pass-6 regeneration in `260503-vcl` packages the Wave 5 freeze state inside the submission zip.
- `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` §Pre-bioRxiv placeholder-fill (2026-04-27) — LIVE captures the per-cell scalars consistent with the Wave 5 freeze.
- Cross-reference: `.planning/amendments/track_a_decision_items_resolution_log.md` Item 2 (editorial trail).

---

## 2026-05-03 — DEC-2026-05-03-vcl-Item3: GitHub repository name locked at carter-clinton/coloc_analysis

**Decision:** Lock the canonical Track A GitHub repository at `https://github.com/carter-clinton/coloc_analysis`. The legacy `The-ASHES-Laboratory` organization slug (referenced verbatim in earlier manuscript drafts) is superseded; no public-facing redirect is required because the legacy slug never went live as the canonical repo (the rename pre-dated the manuscript draft). Manuscript L128 was aligned to the canonical URL in Pass 1 of `260503-vcl` (T1 commit `a9d72eb`).

**Alternatives considered:**
- (a) **carter-clinton/coloc_analysis (adopted)** — already STATE.md L23 canonical (`**GitHub remote:** https://github.com/carter-clinton/coloc_analysis`); already AoU Workbench `git clone` target for Wave 2 of m3 phase per STATE.md; matches the post-pivot honest-framing convention per `feedback_original_research_framing.md` (the original-research framing precludes legacy-suffix references in public-facing artifacts).
- (b) Keep the legacy slug carrying the historical org/suffix nomenclature — rejected: would propagate the legacy nomenclature into manuscript prose at L128 and into the bundle manifest, breaking the honest-framing-lock chain on the public submission package.
- (c) Add a public redirect from the legacy slug to the canonical slug — rejected as unnecessary: the legacy slug never went live, so there is no broken-link surface to redirect from.

**Why:** Per `feedback_original_research_framing.md`, the canonical URL in the public submission package must not carry the legacy nomenclature; the alignment is mechanical (one URL replacement at manuscript L128) and was completed atomically in Pass 1 of `260503-vcl`.

**How to apply:**
- Manuscript L128 is the canonical insertion point; aligned in Pass 1 commit `a9d72eb`.
- All future references to the analysis-code source point at `https://github.com/carter-clinton/coloc_analysis`.
- Cross-reference: `.planning/amendments/track_a_decision_items_resolution_log.md` Item 3 (editorial trail).

---

## 2026-05-03 — DEC-2026-05-03-vcl-Item4: Table 1 row count locked at 3 Tier-A SH2B3 EUR R2 rows + R1 slice empty-body footer

**Decision:** Lock Table 1 at **3 substantive Tier-A rows** (Wave 2 R2 SH2B3 EUR canonical-and-lattice pairs, all at PP.H4 = 1.0 at lead rs3184504, nsnps = 168: BMI–hypertension, hypertension–stroke, hypertension–T2D) plus the **R1 slice empty-body footer** (28 canonical-locus trait-pair rows under disclosure-honest empty-PP.H4 framing). Final row count = 3 substantive rows + 1 disclosure-honest summary row footer. Closes the original manuscript decision-pending item 4 (which was already partially resolved on 2026-04-27 via quick task `260427-e8n` for the R1 slice; the R2 re-fire results landed subsequently and complete the resolution).

**Alternatives considered:**
- (a) **3 Tier-A R2 rows + R1 empty-body footer (adopted)** — substantively reflects the disk-authoritative Wave 2 R2 outcome (3 of 9 canonical-and-lattice pairs SURVIVE at the pre-registered Tier-A threshold per Wave 3 outcome `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE`); preserves the disclosure-honest empty-row framing for the R1 slice that has no non-empty PP.H4 columns; matches manuscript L168 narrative + L276-279 rendered table + L262 Conclusion §1 SURVIVE callout.
- (b) Original 10–20 row target (the manuscript decision-pending item 4 phrasing) — rejected: presupposes a non-zero base survival rate at PP.H4 ≥ 0.8 across the 28 R1 canonical-locus rows (which all returned empty PP.H4 columns); fabricating rows would violate `feedback_original_research_framing.md` rigor.
- (c) Empty-only Table 1 (suppress the 3 SH2B3 R2 Tier-A rows) — rejected: the SH2B3 BRANCH_C SURVIVE is the substantive Tier-A pass that anchors the §SH2B3 case study and the §Reframing of Cardiometabolic Pleiotropy Claims dual-evidence narrative; suppressing it would understate the audit's positive findings.

**Why:** The disclosure-honest framing is reviewer-defensible per `feedback_original_research_framing.md`; the 3 SH2B3 R2 Tier-A rows are substantive findings that survive matched-coverage real-LD `coloc.susie`; both row classes are reported transparently. The combined framing makes Table 1 informative on both axes (positive findings + structural attrition disclosure).

**How to apply:**
- Manuscript Table 1 (L274-279): 3 substantive rows (rendered) + 1 footer row (R1 slice empty-body summary referring to `results/track_a_aggregations/table1_surviving_rows.tsv`).
- Source TSV: `results/track_a_aggregations/table1_surviving_rows.tsv`.
- Wave 2 R2 commit: `b3395d9` (Snakemake target `bin/fire_canonical_susie_pairs.sh`).
- Wave 3 outcome decision token: `D-TA-WAVE3-OUTCOME-BRANCH_C_SURVIVE` (`.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` `<decisions>` block).
- Quick task R1 slice resolution: `260427-e8n`.
- Cross-reference: `.planning/amendments/track_a_decision_items_resolution_log.md` Item 4 (editorial trail).

---

## 2026-05-03 — DEC-2026-05-03-vcl-Item5: OSF amendment posted at osf.io/az52u + 10-entry consolidated deviation log

**Decision:** Lock the OSF amendment posting at `osf.io/az52u` (DOI `10.17605/OSF.IO/PVB5J`), originally landed via `/gsd-quick 260424-mxp` on 2026-04-24, and consolidated into a 10-entry deviation log via quick task `260503-kfq` (Wave 7 closeout) at `.planning/amendments/osf_deviations.md` (entries 8–17 covering the Track B m3 + m2-post-m3 + earlier quick-task cascade). Closes the original manuscript decision-pending item 5; coordination with Track B amendment posting is preserved as a Track B M2-discovery-time gate per `PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §9.1.

**Alternatives considered:**
- (a) **Maintain consolidated 10-entry log at .planning/amendments/osf_deviations.md (adopted)** — single source of truth for OSF deviations; entries 1–7 cover pre-Wave-7 history; entries 8–17 cover Wave 4 + Wave 4.5 + m3 + m2-post-m3 + W7 closeout; matches the manuscript L128 cross-reference path (post-Pass-1 alignment).
- (b) Per-wave deviation logs (one log file per wave) — rejected: fragments the audit trail across 17+ files, breaks single-source-of-truth reviewer-discoverability.
- (c) Pre-register only the original 2026-04-24 amendment text and skip the W7 consolidation — rejected: the 10-entry consolidation captures Wave 4 cache-staleness refutation + Wave 1 SuSiE-RSS L-sweep PRESERVE-WITH-DISCLOSURE + m3 CDR v7→v8 adoption, all of which are substantive deviations from the original Project Plan that must appear in the OSF log for reviewer-defensibility.

**Why:** The OSF amendment + consolidated deviation log are the public pre-registration anchor for Track A's submission. Per `feedback_original_research_framing.md`, deviation transparency is a correctness requirement, not an optional feature; the W7 consolidation locks the Track A deviation surface ahead of *Genome Medicine* submission.

**How to apply:**
- Manuscript L128 (post-Pass-1 alignment) cross-references `.planning/amendments/osf_deviations.md` as the canonical deviation log path.
- Future Track A deviations append to `.planning/amendments/osf_deviations.md` as entries 18+ (preserve append-only convention).
- Track B M2-discovery-time OSF amendment is a separate gate per `PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §9.1.
- Cross-reference: `.planning/amendments/track_a_decision_items_resolution_log.md` Item 5 (editorial trail).

---

## 2026-05-03 — DEC-2026-05-03-vcl-Item6: Figure roster locked at 5 main + 7 supplementary (S2 + S7 landed; S1, S3–S6 caption-only)

**Decision:** Lock the Track A figure roster at **5 main-text figures** (Figure 1A + 1B, Figure 2, Figure 3, Figure 4 demoted to Figure S5, Figure 5) plus **7 supplementary figures** (Figure S1, S2, S3, S4, S5, S6, S7). Substantively rendered: Figs 1A, 1B, 2, 3, S2, S7. Caption-only at this freeze: Figs S1, S3, S4, S5, S6. Figure 4 was demoted to Figure S5 because the pathway-enrichment input set is empty at the manuscript's PP.H4 ≥ 0.5 confidence threshold (see Results §Pathway Enrichment Analysis). Figure 5 is partial-descriptive-only by design (Tier A+B = 0; only Tier C descriptors).

**Alternatives considered:**
- (a) **5 main + 7 supplementary (adopted)** — matches the disk-authoritative figure landing cascade documented in `track_a_decision_items_resolution_log.md` Item 6 per-figure provenance table; matches the manuscript Figure legends section L342-L356; preserves the audit-driven additions Figure S2 (paired-fit structural inflation, audit-v2 §HQ2) and Figure S7 (LD-reference-quality dose-response, audit-v2 HQ#3).
- (b) Render all S1, S3–S6 placeholders before submission — rejected for this freeze: the captioned-but-unrendered slots are non-load-bearing for the audit's primary claims (per-region pairwise test counts at S1 is metadata; NEGR1/TMEM18 detail at S3/S4 is contingent on hub survival which did not occur at this freeze; S5/S6 are identity-LD comparison + negative-control behavior which are described in main-text Results); future Track B work covers these slots when the genome-wide signal set populates.
- (c) Drop Figure 5 entirely (since Tier A+B = 0) — rejected: the partial-descriptive Figure 5 with explicit "Tier A+B = 0; only Tier C descriptors" panel labeling is itself the figure's argument (the visible emptiness at the Tier A+B level is consistent with the §Discussion "primarily an LD-inflation artifact" framing per the Figure 5 caption at L350).

**Why:** The 5-main + 7-supplementary roster is the disk-authoritative figure landing state per the Wave 5 closeout (quick task `260501-wdn`). All audit-author High-Quality recommendations (HQ#2 Figure S2, HQ#3 Figure S7) are addressed with rendered outputs. The caption-only supplementary placeholders are reviewer-discoverable but do not block submission; future Track B work (the genome-wide MTAG/CPASSOC/HyPrColoc + AoU-AFR-LD discovery program) is the appropriate setting for populating S1/S3/S4/S5/S6 slots when the discovery signal set is non-empty.

**How to apply:**
- Manuscript Figure legends section (L342-L356) renders the 5-main + 7-supplementary captions; the rendered outputs at `docs/manuscript/figures/*.pdf` + `*.png` are the disk-authoritative artifacts.
- Pass-6 bundle regeneration (`bin/build_id_vs_ref_ld_submission_bundle.sh`) packages the rendered figures inside the *Genome Medicine* submission zip.
- Future caption-only S1, S3–S6 rendering tracked under Track B M2-discovery-time work, not Track A submission.
- Cross-reference: `.planning/amendments/track_a_decision_items_resolution_log.md` Item 6 (editorial trail).

## 2026-05-05 — DEC-2026-05-05-osf-r3-defer: OSF amendment posting deferred for TA-R3 audit-v2-driven phase; operator override; W5 closeout follow-up

**Decision:** Bypass the pre-execute hard gate `D-TA-R3-OSF-COVERAGE: COVERED` in the `ta-r3-audit-v2-driven-psd-and-r1-refire` phase by setting the token to `OVERRIDDEN at 2026-05-05T13:49:10Z` in `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md`. The amendment text at `.planning/amendments/osf-amendment-r3-2026-05-04.md` (drafted 2026-05-04) is committed locally; the OSF web-UI posting to `osf.io/az52u` is deferred. W5 closeout brief flags this deviation to Cowork-side for v5 disclosure decision. This permits W1 LSF dispatch (15 PSD-regularized SuSiE-RSS fits) to fire on 2026-05-05 without serializing on the OSF posting workflow.

**Alternatives considered:**
- (a) **Override + defer to W5 disclosure decision (adopted)** — keeps HPC compute moving on 2026-05-05; preserves the option for Cowork-side to decide retroactive posting vs. cover-letter disclosure at v5 ship time; honors the project's "rigor over speed" principle (`feedback_rigor_over_speed.md`) by surfacing the deviation in the disk-authoritative deviation log + DECISIONS.md row + W5 closeout brief — i.e., the rigor concern (pre-registration timing) is addressed via *transparent disclosure*, not by *not running the analysis*.
- (b) Block W1 dispatch until OSF posting clears — rejected: serializes ~15 min of HPC parallelizable wall on a manual web-UI workflow; the analysis content is fully specified and locked on disk; the cost of posting *first* vs. *with disclosure* is asymmetric (the analysis itself does not change).
- (c) Skip the amendment entirely — rejected: this would violate `feedback_original_research_framing.md` (deviations from pre-registration must be transparently disclosed); the override is a *timing* deviation, not a *disclosure* deviation.

**Why:** The audit-v2 finding HQ#2(i) on the SH2B3 12q24 EUR LD matrix (23.46% negative eigenvalues / 50.4% effective rank / 6.7% variant coverage with all 3 backing per-trait SuSiE fits flagged `convergence_status = non_converged`) is the primary substrate driving the v5 manuscript revision; the W1 PSD-regularized re-fit is the analytical response. The decision matrix (FIRM / PARTIAL / COLLAPSE / NON_CONVERGE) is pre-specified in the on-disk amendment text and not Claude-selectable. Deferring the posting trades a small registration-timing concession for ~15 min of immediate HPC progress, with full transparency preserved via the deviation log + DECISIONS.md row + W5 closeout brief. Per `feedback_rigor_over_speed.md`, rigor is preserved through transparent disclosure rather than through speed-blocking the analysis.

**How to apply:**
- W1-W5 LSF dispatch under `ta-r3-audit-v2-driven-psd-and-r1-refire` proceeds without waiting on OSF posting.
- W5 closeout brief surfaces `DEC-2026-05-05-osf-r3-defer` and `D-TA-R3-OSF-COVERAGE: OVERRIDDEN` explicitly in the Cowork-side handoff package.
- Cowork-side decides at v5 ship time: (i) retroactive OSF posting + post-hoc deviation note, or (ii) v5 cover-letter disclosure as pre-registration limitation. Both are acceptable.
- Cross-references: `.planning/osf_deviations.md` (under "Deviations (OSF amendment required)"); `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` D-TA-R3-OSF-COVERAGE token; `.planning/amendments/osf-amendment-r3-2026-05-04.md` amendment text.


## 2026-06-01 — DEC-2026-06-01-aou-r8-env-derive: R9→R8 CDR switch + env-derive/suffix-discover AoU AUX paths (Track B m3)

**Decision:** (1) Switch the AoU workspace CDR reference from the unresolvable `C2024Q3R9` to `C2024Q3R8` (cdrv8; + `prep_C2024Q3R8`). (2) Make `src/python/aou_ld_panel.py` resolve the AUX ancestry/relatedness tables fully from the runtime environment instead of hardcoded literals: `_resolve_aux_base` env-derives the AUX base from `$WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH`, and `_resolve_aux_file` discovers each table by its canonical filename SUFFIX. Commits `f4c495c`, `e196ac1`, `9646ac9` (env-derive base + close CHECK-C gate), `3ee42c8`, `09c1e32` (suffix-discover filenames).

**Context (all confirmed live this session):**
- R9 was bound in workspace metadata but **unresolvable by the env-creation CDR binder** — a genuine Standard Analysis (Jupyter) env's startup log threw `cdrv8 - R9 not found` (not a featherweight artifact). R8 binds cleanly (`WORKSPACE_CDR=…C2024Q3R8`). R8 and R9 are both **cdrv8/v8** → genomically identical for the pure-Hail LD build (the R-revision refreshes the curated/BigQuery tier we do not use + applies participant withdrawals).
- The RW 2.0 controlled genomic bucket is **`gs://vwb-aou-datasets-controlled/`** (was `fc-aou-datasets-controlled`). `_resolve_aux_base` absorbed the rename with no code edit (`ENV-DERIVED: True`).
- The R8 aux files carry **pipeline-version filename prefixes** (`aux/ancestry/echo_v4_r2.ancestry_preds.tsv`, `aux/relatedness/samples_relatedness_flagged_samples.tsv`); schemas unchanged (research_id/ancestry_pred; sample_id — verified by byte-range header peek). `_resolve_aux_file` discovers them by suffix; `samples_relatedness.tsv` (pairwise i.s/j.s/kin) is correctly NOT selected.

**Alternatives considered:**
- Keep the R9 pin and re-probe (rejected — R9 is a broken pin; a broken pin is not a valid pin; reopen-trigger of the q04 keep-pin lock was met).
- Hardcode the new R8 literals (bucket + `echo_v4_r2.`/`samples_` filenames) (rejected — these are platform/pipeline-version strings that already drifted twice (fc→vwb, bare→prefixed) and will drift again; "discover, don't pin" per [[feedback_extract_reusable_utilities]] / [[feedback_rigor_over_speed]]).
- Auto-tie-break ancestry ambiguity (rejected — silently picking among >1 ancestry-prediction files could corrupt the cohort; hard-fail and stop instead).

**Why:** R9 will not bind, so it cannot be the analysis CDR; R8 is genomically equivalent for this pure-Hail build and is the pre-migration revision. Env-derivation + suffix-discovery make the whole AoU path surface (bucket / CDR version / filename prefix) a no-op for future platform changes, removing the manual CHECK-C gate from the critical path while keeping the code reviewer-defensible.

**How to apply (Track B reproducibility / OSF disclosure):**
- Disclose the **CDR-revision deviation (C2024Q3R9 → C2024Q3R8, both cdrv8)** in the Track B methods/deviation trail; note R8/R9 are genomically identical for the LD build.
- Provenance sidecars record the RESOLVED (discovered, prefixed) aux paths, so the exact files used are captured per fire.
- Adjudicated adversarial-review dispositions (2 rounds) recorded in `.planning/quick/260601-cca-env-derive-aux-base-close-check-c/SUMMARY.md`.
- Reopen only if a future CDR fails to expose WGS/AUX at AOU-0 (same trigger as the prior keep-pin lock).

## 2026-08-05 — DEC-2026-08-05-m3-ld-read-path: BLOCKER-1 remedy locked at threading `{input.ld_matrix}` into `run_susie_rss.R` behind a new `--ld-file`

**Decision:** Fix the AFR_aou LD-panel unreachability by **passing `{input.ld_matrix}` into `run_susie_rss.R` through a new `--ld-file` argument**, making `resolve_ld_path` the single source of truth for which LD matrix a fit reads. The `--ld-dir`-based reconstruction stays as a fallback so no existing caller breaks. Carter's call, taken at a `/gsd-resume-work` on 2026-08-04/05; the two alternatives were rejected (below). **This is the gate on the ~11-day / $385–1,084 AoU fire** and the premise m3-04c must be REPLANNED around — the existing m3-04c plan's Task 1 cannot deliver its headline `must_have` as written.

**Context (re-verified firsthand this session, not inherited from the handoff):**
- `run_finemap`'s `shell:` block passes only `--ld-dir {params.ld_dir}` and `--region {params.region_id}`. It **never passes `{input.ld_matrix}`** — that input is a **DAG declaration only**. Repo-wide, the sole `shell:` block consuming that variable is `qtl_coloc.smk:316`, a different rule.
- `run_susie_rss.R:125-127` **rebuilds its own path** as `file.path(ld_dir, ancestry, paste0(region_id, ".rds"))`, where `ancestry` is `AFR` and never `AFR_aou`; no rule anywhere promotes `AFR_aou/*.rds` into `AFR/`. On a miss it falls **silently to an identity matrix** (`:472-474`).
- ⇒ The m3-04c curated→M2 crosswalk is **NECESSARY BUT NOT SUFFICIENT**. Proven by simulating the post-fire world: with the panel present, `resolve_ld_path` returns `…/AFR_aou/m2_region_00067.rds` (exists) while SuSiE opens `…/AFR/FTO_16q12.rds` (absent). The 2026-08-03 diagnosis was right but **one layer too shallow** — it verified three ways, all at the declaration layer.
- ⚠ `run_finemap.params.region_id` is now at **`finemap.smk:206`**, not the `:158` the m3-04c plan and older docs cite. m3-04b inserted +48 lines above `params:`, so **every `finemap.smk` line number in the m3-04c plan is stale** and its do-not-touch guard now points at the block the executor must edit. Re-anchor to `2bda675`.

**Alternatives considered:**
- **A promote/symlink rule** materializing `AFR_aou/*.rds` into the `AFR/` directory the R script already reads (rejected — leaves the declare-vs-read split alive, mixes two provenances inside one directory, and adds a materialization step that can go stale silently; it papers over the defect instead of removing it).
- **A per-ancestry `ld_dir`** so `params.ld_dir` already points at `AFR_aou` for AFR fits (rejected — smallest diff and no R edit, but the resolver and the dir logic would then encode the same `AFR → AFR_aou` mapping in two places, worsening the existing duplicated-path-defaults problem the blast radius logged as MEDIUM-4).

**Why:** The chosen remedy kills the declare-vs-read split **permanently** rather than routing around it, and makes the artifact Snakemake declares provably identical to the artifact the script opens. Both alternatives leave a second, independent place where the mapping can drift — the precise failure mode that produced this blocker. It does touch a frozen-adjacent R script, which is why it required Carter's authorization rather than an agent's judgment. Consistent with [[feedback_declared_input_is_not_the_read_path]] and [[feedback_rigor_over_speed]].

**How to apply:**
- **Do NOT fire the loop until this lands.** Otherwise the ~$385–1,084 buys a panel that the fine-mapping DAG silently ignores — the exact outcome the m3-04 replan existed to prevent.
- **REPLAN m3-04c around this decision**: re-anchor every `finemap.smk` line number to `2bda675`; fold the BLOCKER-2 test rewrite in as an **explicit reviewed task** (`test_occlusion_lockstep_wiring.py:410` asserts the exact string m3-04c must replace, and the real `params.region_id` pin sits immediately above it at `:406` — so "just make tests/m3 pass" baits an executor at the one line that must never change); strike the `snakemake --dry-run --quiet` acceptance criterion as unsatisfiable pre-fire, citing D-04b-03.
- **Only the `resolve_ld_path(region_id=)` argument may change.** `run_finemap.params.region_id` stays untouched.
- Acceptance test for the remedy: prove `resolved == what-the-script-opens` — grep the rule's `shell:` for `{input.ld_matrix}`, then assert the R script opens that exact path. A green DAG is not evidence.
- Cross-refs: `.planning/phases/m3-aou-afr-ld-panel-build/m3-04b-BLAST-RADIUS.md` §4 (recommended sequence) and §3 (gate binding).

---

## 2026-08-06 — DEC-2026-08-06-sr4-freeze-scope: the source freeze is a CODE pin, not a byte pin; comments are deliberately FREE

**Decision:** The **source-file** freeze in this repository pins **CODE**, not
bytes. Comments, Python docstrings, blank lines and trailing whitespace are
**deliberately outside** every freeze gate. Landed by `quick-260806-sr4` under
`AUTH-SR4-RESCOPE`, `AUTH-SR4-K3` and `AUTH-SR4-EXTEND` (Carter, 2026-08-06).

**What is pinned:**

- The **CODE** of `src/legacy/region_analysis/scripts/run_susie_rss.R` at
  `bf04199` — a whole-file code-only **floor** plus five named numeric-bearing
  symbols (`regularize_ld`, `run_susie_with_ladder`, `safe_region_id`,
  `load_ld_matrix`, `assert_declared_ld_authoritative`). The symbol pins are
  **diagnostics** (they name *which* block moved); **the floor is the safety
  net**, and it is not optional: `:659-1357` — roughly 700 lines including the
  fitting flow and all three `toJSON` emits — lives inside **no function at
  all**.
- The **CODE** of `src/python/plink_ld_to_npz.py`,
  `src/python/condition_ld_matrix.py` and `src/python/occlusion_span_filter.py`
  at `bf16289` — whole-file plus all **22** top-level symbols (13 + 3 + 6),
  **derived from the source at the pin, never hand-transcribed**. Before this,
  `bf16289` was enforced by **zero** tests anywhere in the repository.

**What is deliberately FREE:** comments, docstrings, blank lines, trailing
whitespace. **Fixing a wrong comment in a frozen file now costs nothing** — no
unfreeze, no re-pin, no decision.

**Why a guard exists at all:** `BLOCKER-1` proved this pipeline can move Track A
numbers **silently** — fixing the LD read path moved EUR `r[1,2]` 0.1 → 0.9,
credible sets 3 → 10, nonzero PIPs 200 → 78, while `ld_status` and
`ld_overlap_fraction` (the two fields anyone would check to argue nothing moved)
stayed **byte-identical**. And there is no cheap regression oracle: re-checking
the AFR side needs the AoU perimeter and the ~11-day billed fire. **Silent
numeric drift with no cheap oracle is the threat.** The guard is not weakened
here; it is aimed at the right target.

**Context — the cost of the old scope was concrete.** The byte pin
(`git diff --exit-code <SHA> -- <file>`) appeared in **no** `DECISIONS.md` entry;
it grew up downstream as a proxy for Track A's frozen NUMBERS. It made shipping a
**known-false** census figure the *cheaper* option: finding **K-3** shipped
`1,944` (correct `1,909`) inside a comment at `run_susie_rss.R:1018-1019` because
correcting a comment would have "cost an unfreeze". **A rule that makes shipping
a falsehood cheaper than fixing it is mis-scoped.** K-3 is closed in the same
window as the proof that the new mechanism permits it: the correction landed and
**the pin did not move**.

**What this is NOT.** This does **not** touch
`.planning/amendments/TRACK-A-FROZEN-NUMBERS.md`, the aggregator md5 lock
recorded in `DEC-2026-05-03-vcl-Item2`, or the three SH2B3 EUR `.fit.rds` md5
pins. (Those md5 literals are deliberately NOT restated here: they are recorded
in exactly the two places that own them, and a copy in a third entry is a second
source of truth waiting to drift.) Those are frozen **NUMBERS** — Carter's recorded decisions — and they are a
**different thing that happens to share a word**. Conflating the two either
breaks a recorded decision or manufactures one.

**Alternatives considered:**

- (a) **Keep whole-file byte pins** — rejected. It makes shipping a known
  falsehood the cheaper option, which is *how K-3 happened*, and
  `[[feedback_fixed_sha_whole_file_pin_is_a_timebomb]]` names the failure mode
  (a fixed-SHA whole-file pin is green once and red forever after; b77's stalled
  a task one day after the pin was written).
- (b) **Symbol pins only, no whole-file floor** — rejected. ~700 lines of
  `run_susie_rss.R`, including all three `toJSON` emits, live inside no function,
  so an enumerate-the-symbols design has a silent hole. **Proven by NC-SR4, not
  argued:** perturbing the `:1357` emit goes RED on the floor while all five
  symbol pins stay GREEN.
- (c) **A naive `#`-to-end-of-line stripper** — rejected. It makes a code change
  concealed after an in-string `#` **invisible**. **Proven by NC-SR3, not
  argued:** the same synthetic fixture is RED under the utility and *identical*
  under the naive stripper, in **both** languages. That would have converted the
  guard into the structurally-incapable-assertion class this project has been
  bitten by eight times.
- (d) **Gate all 8 files `HANDOFF.json` calls frozen** — rejected. **Five have
  demonstrably moved** and declaring a moving file frozen is a **decision**, not
  an inference.

**Why:** The guard's justification is real and is preserved; only its *aim* was
wrong. It pinned BYTES when what needs protecting is NUMERIC BEHAVIOUR.

**How to apply:**

- The forward gate is `pytest tests/m3/test_source_freeze_pins.py`. The utility
  is `tests/m3/source_freeze.py`. `git diff --exit-code` on `run_susie_rss.R`
  survives nowhere in `tests/`.
- **THE RE-PIN PROTOCOL, IN ONE SENTENCE:** an authorized **code** change updates
  **exactly one constant per FROZEN SUBJECT** — `R_CODE_REF` for
  `run_susie_rss.R`, `PY_CODE_REF` for the three Python modules — to the landing
  commit's SHA, **and nothing else**. `FROZEN_R_CODE_REV` and `FREEZE_CODE_REF`
  are **import aliases** of `R_CODE_REF`, so they follow automatically.
  **Comment and docstring changes update nothing.**
- **THE NEVER-RE-PIN RULE, as a DERIVED GATE rather than a hand-written list.**
  Differential substrates are not pins, and a sweep that bumps one silently
  destroys a control (`[[feedback_fixing_a_split_unpins_what_it_pinned]]`). A
  hand-enumeration is the wrong shape — there are **eight** `PRE_CHANGE_REF`s
  plus `BASE_COMMIT` and two `BASELINE_REV`s across `tests/m3/`, and any omission
  *licenses* a sweeper to bump the ones left out. So: **every `*_REF` / `*_REV` /
  `BASE_COMMIT` / `BASELINE_REV` constant in `tests/m3/` must carry a `#:` bucket
  annotation from {CODE PIN | DIFFERENTIAL SUBSTRATE | HISTORICAL NARRATIVE}, and
  only CODE PINs ever move.** Enforced permanently by
  `test_source_freeze_pins.py::test_every_pin_constant_declares_its_bucket` (17
  constants found on 2026-08-06), not by this prose.
- `K3_PRE_FIX_REF` is a **DIFFERENTIAL SUBSTRATE** by name: it is what makes the
  acceptance proof survive the first re-pin. Today it and `R_CODE_REF` both hold
  `bf04199` — a **coincidence of this window** — and they diverge **by design**
  the moment a code change moves `R_CODE_REF`.
- **Extending the freeze to a new file** is a one-line addition to the pin table
  **plus a recorded decision that the file is frozen.**
- **The stripper inventory — this is not the first stripper.** **NINE** ad-hoc
  comment-strippers already existed when `source_freeze.py` was written
  (`strip_py_comments`, `r_code_only`, `code_only`, `_code_lines`,
  `_strip_py_comments`, `_strip_r_comments`, `_code_only`, `_strip_comments`,
  `_strip_hash_comments`), and `_code_lines` in
  `test_variant_catalog_fallback_legacy_semantics.py` is a hand-rolled instance
  of this very utility. They are **registered and superseded going forward**;
  **none is refactored**, because each backs a different assertion with
  deliberate semantics (`strip_py_comments` KEEPS triple-quoted strings because a
  Snakemake `shell:` body IS one; `code_only` DELETES them) and rewiring them is
  unauthorized and carries real regression risk. `r_code_only` is deliberately
  **kept** and consumed as an **independent R cross-check** of the new mask.
  What existed **nowhere** was the **FREEZE convention** itself — no
  `DECISIONS.md` entry, and `bf16289` enforced by zero tests.
- **What this does NOT cover, stated as a limit rather than sold as coverage:**
  the pins are over **source text** only. They detect *that code moved*, never
  *whether a number moved*. No fit is run and no `.rds`, `.npz` or region JSON is
  produced or compared. YAML support was deliberately **not** built.
- Cross-refs: `[[feedback_extract_reusable_utilities]]`,
  `[[feedback_fixed_sha_whole_file_pin_is_a_timebomb]]`,
  `[[feedback_green_assertion_needs_a_negative_control]]`,
  `[[feedback_negative_control_defeated_by_bytecode_cache]]`,
  `[[feedback_fixing_a_split_unpins_what_it_pinned]]`; K-3 in
  `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`;
  `DEC-2026-08-05-m3-ld-read-path` (BLOCKER-1 — the reason a guard exists).

## 2026-08-07 — DEC-2026-08-07-e2-orientation-disposition: E-2 disposed as option A (leave the code, DISCLOSE a MATERIAL exposure)

**Decision:** Adopt **option A** for blast-radius item **E-2** (the QTL-beta ↔
panel-ALT orientation). The code is **NOT** changed. The exposure is **disclosed
as a stated limitation** in the manuscript and the OSF record. Carter's call,
2026-08-07, on measured evidence.

**Why A and not B, on the evidence:**

1. **B is currently unexercisable.** `build_qtl_coloc_manifest.py::_ancestry_for_region`
   returns `"EUR"` unconditionally (**E-4**), so **zero** AFR QTL-coloc jobs exist.
   A fix gated to AFR would be the **third** correct-but-inert closure in this arc
   after findings **E** and **G**.
2. **B moves Track A numbers**, and Track A is **in submission**.
3. **The only substrate available to validate B is an identity-LD stub tree**
   (`use_identity = TRUE`, `R` NULL, EUR/AFR/TRANS byte-identical). Making a
   Track-A-moving correction validated against stubs would be worse than the
   defect.

**⚠ THE EXPOSURE IS MATERIAL, NOT MINOR — DO NOT SOFTEN THIS IN THE WRITE-UP.**
Measured 2026-08-07 with the shipped `ld_allele_join_indices()` over the 207 real
region variant catalogs (`e2-exposure-measure.R`, `e2-exposure-real-corpus.tsv`).
Across the **five regions Track A's coloc numbers actually depend on**:

| Track A region | exact | flipped | ratio |
|---|---|---|---|
| `CXADR_F2RL1_6p21` | 28,415 | 18 | **0.06%** |
| `MC4R_18q21` | 14,141 | 10 | **0.07%** |
| `SH2B3_12q24` | 11,826 | 333 | **2.74%** (tiles 1–2 = **0.00%**; **tile 3 = 20.33%**) |
| `APOL1_22q12` | 4,910 | 1,108 | **18.41%** |
| `FTO_16q12` | 7,188 | 2,245 | **23.80%** |
| **pooled** | 66,480 | 3,714 | **5.29%** |

Whole corpus: per-region **median 17.82%**, max 38.68%, **195 of 206** regions
affected.

**⚠ A CORRECTION TO THE RECORD.** An interim report stated SH2B3 tile 3 was
"0.20%". It is **20.33%** — a ratio of `0.2033` misread as a percentage, a 100×
error in the reassuring direction, in the very claim this decision was first
proposed on. The corrected numbers are the ones above. **The anchor tiles (1, 2)
are genuinely 0.00%; tile 3 is not.**

**What the number means, precisely.** It is the share of bindable variants whose
REF/ALT are **transposed between the region variant catalog and the panel's
`variants` frame at the same coordinate** — i.e. the **population in which an
orientation error can occur**, not a count of realized sign errors. It does not
by itself demonstrate that any published `PP.H4` is wrong. It does mean **"we
checked and it is immaterial" is NOT a defensible statement** for `APOL1_22q12`
or `FTO_16q12`.

**Obligations this decision creates (none discharged yet):**

1. A manuscript **limitation** paragraph carrying the real per-region numbers —
   naming `APOL1_22q12` (18.41%) and `FTO_16q12` (23.80%) explicitly rather than
   quoting only the flattering 5.29% pooled figure.
2. An **OSF record** entry, consistent with the standing "state it, do not let a
   reader find it by diffing" discipline.
3. ⚠ **An open question that is above an executor's authority and is NOT settled
   by this decision: is this a LIMITATION or a CORRECTION?** Two of five coloc
   regions carrying ~18–24% transposed variants is large enough that a reviewer
   may reasonably read it as the latter. Registered for Carter.

**Rejected alternatives:**
- **B now (correct the orientation)** — rejected: inert without E-4, moves
  Track A numbers mid-submission, and validatable only against stub panels.
- **Quote the pooled 5.29% alone** — rejected: it is dragged down by the two
  clean large regions and hides that two regions sit near 20%. A fit is
  per-region; the per-region figures are the honest unit.

**When B becomes right:** bundled with **E-4**, after the AoU panel exists, with
a real-LD re-measurement, a before/after comparison and the OSF disclosure the
E-2 entry already specifies. **E-2 and E-4 are coupled; neither alone is a
complete change.**

**Cross-refs:** `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`
(E-2, E-4 and the 2026-08-07 evidence update);
`.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` (untouched by this decision);
`[[feedback_a_count_is_a_claim_scope_and_reconcile]]`.

## 2026-08-11 — DEC-2026-08-11-e2-framing-correction: E-2 is framed as a CORRECTION (framing B); the matched pair ms-correction + osf-correction is selected

**Decision:** E-2's disclosure is framed as **B — CORRECTION**. The complete
matched pair `ms-correction` (the manuscript paragraph) + `osf-correction` (the
OSF record entry) from the `260811-oku` drafts is **selected**. Carter's call,
**2026-08-11**, delegated to the standing recommendation on the oku decision
surface:

> "Based on your recommendation, choose the pair for E-2, and for SR4-OPEN,
> correct the handoff language"

This **resolves obligation (3)** of `DEC-2026-08-07-e2-orientation-disposition`
— *"is this a LIMITATION or a CORRECTION?"* — which that entry registered as an
open question above executor authority. Obligation (3) is **DISCHARGED**.

**⚠ THE AXIS GUARD — framing B is NOT disposition option B.**
`DEC-2026-08-07-e2-orientation-disposition` disposed E-2 as **option A**, and
that disposition stands unmoved: the code is still not changed, no Track A
number moves, and nothing here reopens it. Only the **framing** axis moved. The
two Bs sit on different axes, and an entry that let them blur would read as an
undeclared reversal of a Carter decision.

**Why B — the four grounds, as recorded on the decision surface:**

1. **Accuracy.** A limitation is something the data cannot do; this is something
   the pipeline **did wrongly** — matching on coordinates while ignoring the
   alleles. Filing it under Limitations describes it inaccurately, and inaccuracy
   in the **reassuring** direction is exactly the class of error this arc has
   already committed twice (the 100× tile-3 misread; the `46/182` fixture quoted
   as a measurement).
2. **The magnitude claim is bounded either way.** Both bodies carry the same
   identity-LD-stub caveat and the same "population, not realised errors"
   sentence. B corrects the **convention** — provable in code, substrate-
   independent — while **bounding** the magnitude, which is stub-bound. It does
   not over-claim the size of anything.
3. **B's extra obligation is one the E-4 bundle already carries.** The real-LD
   re-measurement, the before/after comparison and the further OSF update are
   already the stated conditions under which the code change becomes right. B
   puts them on the public record instead of in a planning file.
4. **The asymmetry favours B.** Over-correcting costs a paragraph. Under-calling
   a measured 18–24% exposure that a real panel later confirms costs the record
   showing the softer word was chosen **after** measuring 18.41% and 23.80%.
   Standing posture: rigor over speed in any gray-area trade-off.

**⚠ PRE-PLACEMENT VERIFICATION STEP — Carter's, and it happens before placement.**
It is a step, not an unresolved question, and it is not a reason to reopen the
framing. The target journal's policy is the one input to this decision that is
not in this repository. Before the paragraph is placed, check whether the
journal's process reads a "correction" framing on a manuscript **in submission**
as a formal **post-publication correction notice**. If it does, keep **B's
CONTENT** and use **A's PLACEMENT** — the Limitations section — per the flip
condition recorded on the oku decision surface. That is a **placement** change
only: it does not reopen the framing, does not change a number, and does not
change a sentence of either selected body.

**What becomes PUBLIC on posting.** The `osf-correction` body closes with a
commitment: the join is made allele-aware; the exposure is re-measured on the
real panel; the affected African-ancestry results are **regenerated and
re-reported** with a before-and-after comparison; and both are posted as a
further update **whether or not the reported conclusions change**. Today that is
an **internal** E-4 obligation. **Posting converts it into a public commitment**,
and at that point it must be registered as a tracked obligation of the E-4 work
(oku post-paste checklist item 6) so it cannot be lost.

**Discharge status:**

| Obligation | Status | Discharges when |
|---|---|---|
| **(3)** LIMITATION vs CORRECTION | ✅ **DISCHARGED** by this entry | the framing is chosen **and** recorded in `.planning/DECISIONS.md` — done here |
| **(1)** manuscript paragraph | ⛔ **OPEN** — Carter's external action | `ms-correction` is placed in the Track A (`id-vs-ref-LD`) manuscript, after the pre-placement journal-policy check above |
| **(2)** OSF record entry | ⛔ **OPEN** — Carter's external action | `osf-correction` is posted as a **NEW supplementary file** on `osf.io/az52u` — never a new version of `trsx5` or `tcujq` — **and** its URL + timestamp are recorded in `.planning/osf_deviations.md` |

⚠ **The oku OSF draft's post-paste checklist item 3 does NOT conflict with this,
and must not be reported as conflicting.** That checklist sequences the same
recording *after* posting and asks it to cite the entry's URL. Obligation (3)
discharges **here**, per the discharge table on the oku decision surface — the
framing is chosen and recorded. The URL cross-reference is an addition made when
**(2)** discharges, and it does not un-discharge (3).

**How to apply:**

- The paste-ready selected pair is
  `.planning/quick/260811-tf3-record-carter-decisions-e-2-framing-b-co/260811-tf3-SELECTED-PAIR-correction.md`.
  Its two bodies are **byte-identical** to their oku source blocks, proven by
  `cmp` against a machine extraction rather than by inspection.
- ⛔ **No agent posts to OSF, edits a manuscript file, or edits the body of a
  posted amendment.** OSF bodies are append-only. Obligations (1) and (2)
  discharge only by Carter's external actions.
- ⛔ **Never quote the pooled 5.29% alone.** It is **dragged** down by the two
  clean large regions; name 18.41% (`APOL1_22q12`) and 23.80% (`FTO_16q12`) in
  the same breath.
- ⛔ **Never cite these as the real-LD exposure.** Every panel measured is an
  identity-LD stub, so they are catalog↔panel-frame transposition rates for
  variant bookkeeping and nothing more.
- The unselected `ms-limitation` / `osf-limitation` texts stay in the oku
  directory as the record of what was considered, and are **not** to be posted.
- The oku harness `260811-oku-check-drafts.sh` was **green at selection time**,
  and the tf3 extraction is byte-identical to its blocks, so the extraction
  inherits that clause evidence by identity instead of re-asserting it.

**Alternatives considered:**

- (a) **Framing A — LIMITATION.** Rejected on grounds 1 and 4. It is not a wrong
  description of the *magnitude* — both bodies bound that identically — it is a
  wrong description of the *defect*.
- (b) **Defer the framing until a real panel exists.** Rejected. Obligations (1)
  and (2) cannot be written in no framing at all, Track A is in submission now,
  and the one future fact that would have argued for A — a near-0% real-panel
  measurement — is already covered as a further OSF update rather than as a
  retraction.
- (c) **B's content with A's placement.** **NOT rejected.** It is held as the
  conditional outcome of the pre-placement journal-policy check above.

**Cross-refs:** `DEC-2026-08-07-e2-orientation-disposition` (obligation (3));
the three oku deliverables —
`.planning/quick/260811-oku-discharge-e-2-disclosure-obligations-dra/260811-oku-e2-framing-decision-surface.md`,
`…/260811-oku-e2-manuscript-limitation-drafts.md`,
`…/260811-oku-e2-osf-entry-drafts.md`;
`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` (E-2 and E-4);
`[[feedback_a_count_is_a_claim_scope_and_reconcile]]`,
`[[feedback_rigor_over_speed]]`.

## 2026-08-11 — DEC-2026-08-11-sr4-disposition: SR4-OPEN is answered NEVER ACTUALLY FROZEN; the handoff language was wrong and is corrected

**Decision:** the five files were **NEVER ACTUALLY FROZEN**. The handoff's
"frozen/pinned at `bf16289`" language for them was **wrong**, and it is
**corrected, not defended**. **No drift review is required.** Carter's call,
**2026-08-11**:

> "Based on your recommendation, choose the pair for E-2, and for SR4-OPEN,
> correct the handoff language"

The five, with their measured drift vs `bf16289`:
`src/python/occlusion_manifest.py` **+46 / −8** ·
`src/python/occlusion_present_rate_scan.py` **+154 / −21** ·
`src/python/drop_occluded_from_sumstats.py` **+97 / −24** ·
`src/scripts/ld_npz_to_rds.R` **+313 / −62** ·
`src/snakemake/schemas/pipeline.schema.yaml` **+119 / −0**.

**Evidence.** The dossier at
`.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-DOSSIER.md`,
landed by `f78bbc1` (T1), `399c50f` (T2) and `2b13dce`. Four independent
measurements agree, and none contradicts:

1. **`bf16289` is not a freeze commit.** It is a `docs(handoff)` session-close
   commit that changed **one** file — `.continue-here.md`, +19 / −3 — and touched
   **none** of the eight. A pin that never touched what it pinned was a
   **bookmark**, not an act of freezing.
2. **The freeze convention did not exist in the register until after all the
   drift.** `DEC-2026-08-06-sr4-freeze-scope` is the only freeze entry;
   `grep -c '<basename>' .planning/DECISIONS.md` returned **0** for all five;
   and `bf16289` matched **zero** files under `tests/ src/ config/ Snakefile` at
   **every one of the 8 drift commits** — measured at the drift commits
   themselves rather than inferred from today.
3. **All 8 distinct drift commits are traceable.** For each, the task token
   resolves to a real artifact directory **and** the commit's short SHA is named
   inside that artifact (13 grep hits). There is no untraceable commit, so
   nothing is forced to `DRIFT-NEEDS-REVIEW`; every one landed under a planned,
   executed and summarised GSD task.
4. **The label was COLLECTIVE, and it was a status report, not a prohibition.**
   The five were never declared frozen individually. Four of them appear only
   inside one sentence — *"All 7 pinned files 0-line diff vs `bf16289`"* — whose
   grammatical content is an observation that they were currently unchanged, not
   an instruction that they must not change.

**⚠ The two facts that cut the other way — stated, not buried:**

- **F1–F4: that collective label PREDATED the drift.** `2bda675` is dated
  **2026-08-03**, and `git merge-base --is-ancestor` confirms it precedes
  `3bb8783`, `bf963df`, `fac9a93` and `57b381f`. Something *had* been written
  about these files before they moved, and they moved anyway. This is **genuine
  contrary evidence** and is weighed rather than dismissed. Three things bound
  how much it carries: it is a **status report** (*"0-line diff"*), not a freeze
  instruction; it lives in a **handoff narrative** rather than in the decision
  register, and this project has already baked the rule that an invariant with
  no named enforcer is a belief; and it was enforced by **measured zero** at each
  drift commit.
- **F5 (`src/snakemake/schemas/pipeline.schema.yaml`) was NEVER in the "7 pinned
  files" roster at all** — that roster is 4 m3-07 modules + 3 frozen contracts —
  and its only individual label (`HANDOFF.json` `freeze_state` at `63453db`,
  2026-08-06) **postdates all of its drift**. It was called frozen only after it
  had stopped moving, so **there is nothing to review**.

**Stated limits.** `NEVER ACTUALLY FROZEN` is a statement about **process and
intent**, and it is **not a code review**: nobody read the `+46 / −8` or the
`+313 / −62` to judge whether the changes were right. The narrative
first-appearance dates are **LOWER BOUNDS** — 17 `HANDOFF.json`, 29 `STATE.md`
and 22 `.continue-here.md` history objects could not be read (missing loose git
objects, a known recurring GPFS failure), and the unreadable set skews **old**,
which is exactly where an earlier freeze label would live. ⚠ **Recovering an
earlier label would not move this disposition**, because nothing enforced it at
any drift commit and every drift commit is traceable to a reviewed SUMMARY.

**Consequences:**

- **No drift review.** The set that is deliberately *not* being reviewed is named
  so it is explicit: `3bb8783`, `bf963df`, `fac9a93`, `aeed8c0`, `57b381f`,
  `64f420a`, `2563451`, `d7dfa67` — 8 commits across the tasks `260804-rtc`,
  `260805-23d`, `260805-o7o`, `260805-w7u` and `m3-04b`.
- **The three genuinely 0-diff files stay gated.** `src/python/plink_ld_to_npz.py`,
  `src/python/condition_ld_matrix.py` and `src/python/occlusion_span_filter.py`
  remain gated by `tests/m3/source_freeze.py` at `PY_CODE_REF`, unchanged by this
  entry.
- **NO NEW PIN is created by this decision.** None of the five is added to
  `PY_FROZEN_RELS`, and
  `test_the_handoff_frozen_claim_is_recorded_as_partly_false` stays green
  asserting that they are **out** of the pinned set.
- **Any future pin is its own task**, and it costs: a recorded decision that the
  file is frozen; a `#:` bucket annotation on the new constant; a **negative
  control** OBSERVED red; a change to the handoff-claim test, which goes RED the
  moment a file is added; and — for F5 only — a YAML code-stripper that
  `tests/m3/source_freeze.py` does not have, since it supports `LANG_R` and
  `LANG_PY` only.
- ⚠ **An honest note on what a pin would buy.** A pin at `bf16289` is **not
  available** for these five: they have moved, so it would be red at birth. Any
  pin would therefore be the weaker claim *"these must not change from here"*
  rather than *"these have not changed since the freeze."* That is legitimate to
  want and legitimate to decline.

**How to apply:**

- `HANDOFF.json` and `.planning/STATE.md:39` already carry the explicit
  retraction of *"All 7 pinned files 0-line diff vs `bf16289`"*. **Do not repeat
  the retracted claim.**
- ⚠ **Residual live sites, OUT of the write scope of the task that landed this
  entry and registered here as the follow-up:** `.planning/STATE.md:15` and
  `.planning/ROADMAP.md:1077` both still assert `ld_npz_to_rds.R` is
  frozen/unchanged when it is **+313 / −62**. Correcting them is a separate task.
- ⚠ **The dated historical `>` blocks are NOT correction sites**
  (`STATE.md:266`, `:278`, `:297`, `:301`, `:311`, `:349`, `:362`;
  `.continue-here.md:57`, `:113`, `:205`, `:217`, `:233`, `:249`, `:252`). They
  correctly describe what was believed when they were written, and rewriting them
  would destroy the record this disposition rests on.

**Alternatives considered:**

- (a) **FROZEN-AND-DRIFTED**, i.e. review the 8 commits — rejected on the
  evidence. F5 would be its least defensible member: never in the roster, and its
  label postdates its drift, so there is no window in which changing it violated
  anything.
- (b) **Answer NEVER-FROZEN and pin the five at today's HEAD in the same breath**
  — rejected as a bundled decision. Declining today forecloses nothing: the pin
  question is independent of the SR4-OPEN answer and can be taken up whenever it
  is worth its own recorded decision and its own observed-red control.

**Cross-refs:** `DEC-2026-08-06-sr4-freeze-scope`;
`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` (SR4-OPEN);
the `260811-pmv` dossier;
`[[feedback_a_claimed_invariant_needs_a_named_enforcer]]`,
`[[feedback_green_assertion_needs_a_negative_control]]`,
`[[feedback_fixed_sha_whole_file_pin_is_a_timebomb]]`.


---

## 2026-08-12 — DEC-2026-08-12-adversarial-review-remediation: the five-way review is remediated; ONE canonical stale-site table supersedes the three divergent lists

**Decision:** the 2026-08-11/12 five-way adversarial review of commit range
`7d575a5..42c060e` is **remediated in three parts** — a **v2** E-2 outgoing
disclosure pair, the **260811-rcw PRE-FIRE gate review corrected in place**, and
a **claim-level sweep** of the record surfaces. This entry is the register of
what was found, what was fixed, and what was **deliberately left**. Carter's
call, **2026-08-11**: *"Run it"* (following *"100% certain we have all our bases
covered ... comprehensive adversarial review using codex and
/assess-blast-radius"*).

**⛔ THE TWO 2026-08-11 DECISIONS STAND UNCHANGED AND ARE NOT REOPENED.**
`DEC-2026-08-11-e2-framing-correction` (E-2 framing = **B, CORRECTION**) and
`DEC-2026-08-11-sr4-disposition` (**never actually frozen**). The review found no
reason to revisit either. **This work fixes texts and surfaces, never decisions.**

### The review, including what it CLEARED

Reviewers: **Codex CLI v0.141.0** (external, read-only sandbox) plus **four blind
parallel read-only investigators** (D1 record-surface consistency, D2 fire-surface
fidelity, D3 disclosure content, D4 guard integrity + repo health). Every finding
was evidence-cited by at least one reviewer; the blockers were independently
confirmed by two.

**What it CLEARED is load-bearing and is recorded so it is not re-litigated:**
all eleven outgoing figures re-derive to the digit from the two `e2-exposure`
TSVs (three independent re-derivations); the pooled 5.29% never appears alone;
the identity-LD-stub caveat is present in both outgoing bodies; the
46/182 = 25.3% synthetic-fixture and the 100× misread are correctly labelled and
were never externally reported; **no posted OSF body was contradicted or
touched**; no frozen number moved; the word "revision" appears nowhere; the
`260811-pmv` SR4 dossier's evidence chain held under attack; DECISIONS.md was
provably append-only (252/0) and HANDOFF.json parsed; §5 of the rcw review is
faithful to m3-04c PLAN Task 3; **zero perimeter contact proven by log grep**;
no source/test/config drift in the whole range; `origin == 42c060e`; the standing
`test_source_freeze_pins.py` gate untouched with 39 passed; and STATE.md's
frontmatter byte-identical with its pre-existing unparseability **not aggravated**.

### What it FOUND, and what was done (by part and finding ID)

**PART A — the outgoing E-2 disclosure pair. A **v2** pair now supersedes v1.**

| ID | Finding | Fix |
|---|---|---|
| **A-BLOCKER-1** | v1 said the catalog↔panel join *"matched on coordinates alone and ignored the alleles"*. **False of that join.** `src/snakemake/scripts/ld_allele_join.R:205-270` is a 4-key allele-aware matcher (`k4_exact` + `k4_swap`, palindromes dropped at `:232-239`, duplicated 4-keys removed from the match table at `:211-219`) and **its own `flipped` counter PRODUCED every disclosed percentage** | v2 attributes the numbers to the shipped matcher; names the disclosed property as the orientation **measured and reported but deliberately NOT APPLIED** to the QTL beta at `run_qtl_coloc.R:478-479` (a recorded decision, `DEC-2026-08-07-e2-orientation-disposition` option A); and confines the allele-blind CHR:POS description to the **fine-map-side** join, **fixed for AFR only and still position-only on EUR today** because `config/pipeline.yaml`'s `ld_read_path` is ancestry-scoped |
| **A-BLOCKER-2** | v1 committed to *"the join is made allele-aware"* — **already shipped** — and to regenerating *"the affected African-ancestry results"* — an ancestry with **zero** coloc jobs (E-4: `_ancestry_for_region` returns `"EUR"` unconditionally) | v2 names the **real** three-part remedy (apply the measured orientation to the QTL beta; a GRCh38→GRCh37 allele reconciliation on the QTL side; an ancestry gate if Track A must not move) and scopes the re-report to **every affected ancestry that HAS results at remediation time, explicitly including EUR**. Condition-bounded on E-4 + a real non-identity panel; **no schedule** |
| **A-BLOCKER-3** | the ms paragraph had lost its bounding and nowhere said the code was unchanged — a Methods reader could infer a fix had been made and results regenerated | v2 restores all three: population-**not**-realised-errors; **the analysis code is unchanged by this disclosure**; and no PP.H4 is shown wrong. (Framing B is **not** disposition option B) |
| **A-HIGH-1** | unit equivocation: the **tile-row** median was labelled per-region | v2 states **both** units, labelled: per TILE-ROW **195 of 206**, median **17.82%**, max **38.68%**; per LOCUS **49 of 51**, median **0.4234%**, max **38.6824%**; the five-region table is labelled LOCUS-unit |
| **A-MEDIUM** | missing measurement basis + provenance pointer; "published" → "**reported**" direction of effect; the trsx5 interaction merely **asserted** unaffected; no original-research framing sentence; `(3 cells)` | all five fixed. The trsx5 interaction is now **reasoned**: the posted 2026-07-10 body premises a **position-based** join (`:47`) and lockstep exclusion (`:57`), and palindrome-dropping is a **new one-sided drop class** relative to that premise — recorded as a **premise update**, bounded at **144,176** palindromic drops = **19.34%** of the bindable set, and **counted** in `dropped_palindromic`, therefore auditable |
| **A-HARNESS** | the v1 harness could not have caught any of it: token-presence not number↔label fidelity; a file-scoped pooled guard; no word boundaries on (UN)DISCHARGED; `expect_red` hard-wired to the `ms` group | `260812-09a-check-v2-pair.sh` — 45 clauses, 3 groups, **16 controls all OBSERVED RED**, including an APOL1↔CXADR label swap, a block-scoped pooled-alone isolator with an out-of-block companion, and an UNDISCHARGED→DISCHARGED flip |

**PART B — the PRE-FIRE gate review. It FALSE-PASSED its own check.**

**B-BLOCKER-1** is the one that could have cost money. The document Carter reads
immediately before a ~11-day / **$385–1,084** fire told him to poll with
`gsutil ls gs://${WORKSPACE_BUCKET}/ld/AFR_aou/*.npz | wc -l`. `WORKSPACE_BUCKET`
**already carries `gs://`** (`SKILL.md:43`), so that double-prefixes: gsutil errors
to **stderr**, stdout is **empty**, `wc -l` prints **0** — which is exactly what
the pre-fire *"expected: 0"* row EXPECTS, and which during STEP B polling reads a
**healthy fire as dead**. Same defect class the project already fixed once in
**quick-260611-tbw** (gap C3). Corrected **at all three points of use** (§4 row 1,
the liveness-arbiter block and STEP B — the latter two previously carried **no
command at all**), in the literal-bucket primary form, with a correctly-quoted env
alternate and a never-prefix warning at each site.

**B-HIGH-1**: **276 is not a pass bar** — restored to both the liveness paragraph
and STEP B. **B-MEDIUM 1–5**: the open-items table refreshed and dated; the
`<panel-uri>` placeholder replaced by a URI **derived from the producer**
(`run_native_ld_panel.py:122/:732/:734` + `SKILL.md:12`) rather than from the
reviewer's guess; the real-`.bim` row now says honestly that no runnable command
can be written from NC State and that the 0-vs-1-based index origin is **OPEN**;
three §2 rows labelled last-known with an explicit re-verification ruling each,
plus a **new §4 row 5** for the cohort MTs; and a new **§2.1(9)** recording the
m3-04c PLAN's branch (ii)/(iii) self-contradiction with the **code-correct**
reading. **B-LOW 1–4**: three wrong line anchors fixed and their echoes chased,
"four" negative-control tests → **three**, and `L-11` / `L-09` / `L-16` rescoped
to claim exactly what their commands prove. A dated
`## Corrections (2026-08-12)` changelog names every finding ID.

⚠ **Three of the review order's own anchors were wrong at HEAD** (`:1494-1497`,
`:920-926`, `:942`) and one range was short (`:715-718` vs the measured
`:716-718`). **The measured values were used and the disagreements are recorded**
in the changelog rather than propagated.

### The scoped SR4 grep restatement (Codex #4) — the evidence, honestly bounded

The `260811-pmv` dossier reported **0 hits** for each of the five basenames in
`.planning/DECISIONS.md`. That measurement was taken at **`0e7e309`**
(`git cat-file -t 0e7e309` → commit), **before `DEC-2026-08-11-sr4-disposition`
itself named those basenames**. Re-measured **at HEAD, 2026-08-12**, the same
`grep -c` now counts:

| basename | @ `0e7e309` | @ HEAD |
|---|---|---|
| `occlusion_manifest.py` | 0 | **1** |
| `occlusion_present_rate_scan.py` | 0 | **1** |
| `drop_occluded_from_sumstats.py` | 0 | **1** |
| `ld_npz_to_rds.R` | 0 | **2** |
| `pipeline.schema.yaml` | 0 | **2** |

Every hit at HEAD is **self-reference by the disposition entry**. **This does not weaken the disposition** — the finding it supported was that *nothing in
`src/`, `tests/`, `config/` or `Snakefile` ever enforced the `bf16289` pin*, which
is unchanged. It scopes the **evidence** honestly, so that no future reader re-runs the grep, gets a non-zero count, and concludes the dossier was wrong.

### The oku harness caveat (D4-10) — what "enforced by" actually bought

Two surfaces read `260811-oku-check-drafts.sh` as **standing enforcement of 29
control-backed clauses**. The measured figure is **4 observed-red of 29 clauses,
and all six of its controls target the `ms` group alone**; the other 25 clauses
were **never observed failing**, so they are green without a negative control.
The harness is also **task-local and was never in CI**. Both STATE.md surfaces are
rescoped to **"gated at selection time by (task-local, not CI)"**. The
defeat-resistant replacement is `260812-09a-check-v2-pair.sh`.
⛔ **The closed `260811-oku` SUMMARY and VERIFICATION are deliberately NOT
edited** — a closed task's record stands; the caveat is recorded here instead.

### ★ THE ONE CANONICAL RESIDUAL / STALE-SITE TABLE

**This table SUPERSEDES the three divergent lists that had grown across
`DECISIONS.md`, `HANDOFF.json` and `STATE.md`.** There is now one list, and it is
**RENDERED FROM** `.planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/260812-09a-stale-claim-sweep.tsv`
— never retyped — so the register and its evidence cannot diverge into a fourth.

⚠ **Scope, stated so the counts reproduce.** `grep -r` does **not** follow
symlinks on this GPFS tree (it silently **under**-counts) and recursing from the
repo root silently **over**-counts, so the sweep used an **explicit file list**:
`.planning/*.md`, `.planning/*.json`,
`.planning/phases/m3-aou-afr-ld-panel-build/*.md` **plus `.continue-here.md`**
(which the glob misses), and `.claude/skills/*/SKILL.md` — **83 files**.
⚠ The TSV is **tab-separated and not CSV-quoted**: its excerpts contain quote
characters, and a `QUOTE_MINIMAL` csv reader merges rows (it read 130 back as 118
during authoring). Split on TAB.
⚠ **One scope exclusion, and it is not a convenience.** `DECISIONS.md` is swept
**up to this very heading**. This entry is the **record of** the enumeration, not a
subject of it — it necessarily *quotes* every stale claim in order to register it,
so counting itself would make the sweep circular and self-inflating. That is the
same scoping discipline the `260811-rcw` review states for its own Reconciliation
log. **Everything before this heading IS swept** — and it contributes 9 of the 86
left rows (C1 ×3, C4 ×1, C5 ×5). The generator and
`260812-09a-check-sweep.sh` apply the **identical** cut, or the residual assertion
would be meaningless.

| Claim | The stale claim | fixed | left | elim. | Where it is LEFT, and why |
|---|---|---|---|---|---|
| **C1** | the RETRACTED "all 7 pinned files 0-line diff vs `bf16289`" freeze claim | 3 | 38 | 0 | `STATE.md` ×12; `.continue-here.md` ×6; `m3-04b-W4-occlusion-catalog-and-consume-seam-PLAN.md` ×5; `m3-04b-W4-SUMMARY.md` ×4; `DECISIONS.md` ×3; `m3-07a-UAT.md` ×2; `HANDOFF.json` ×1; `deferred-items.md` ×1; `m3-04b-BLAST-RADIUS.md` ×1; `m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md` ×1; `m3-07c-W7-present-rate-and-lockstep-PLAN.md` ×1; `m3-07c-W7-present-rate-and-lockstep-SUMMARY.md` ×1 — DECISIONS.md is STRICTLY APPEND-ONLY / INSIDE THE FRONTMATTER FENCE (measured: lines 1-24). The frontmatter must stay byte-identical and its YAML is pre-existing-unparseable / dated deferred-items entry that already carries the correct disposition inline; superseded by DEC-2026-08-12 / dated historical block or quick-task ledger row / dated phase record (PLAN/SUMMARY/REVIEW/BLAST-RADIUS/UAT/CONTEXT/RESEARCH/VALIDATION) stating what that plan asserted on its own date; rewriting it would falsify the historical record / explicitly DATED key (headline_2026_08_0X) / inside a dated historical '>' block |
| **C2** | "ZERO Carter decisions outstanding" carrying a stale outstanding-list | 8 | 0 | 0 | **none** — no surviving un-annotated hit anywhere in scope |
| **C3** | "THREE E-2 obligations / all UNDISCHARGED" after (3) was discharged | 3 | 0 | 0 | **none** — no surviving un-annotated hit anywhere in scope |
| **C4** | the LIMITATION-vs-CORRECTION framing question presented as OPEN | 3 | 3 | 0 | `DECISIONS.md` ×1; `STATE.md` ×1; `deferred-items.md` ×1 — DECISIONS.md is STRICTLY APPEND-ONLY / dated deferred-items entry that already carries the correct disposition inline; superseded by DEC-2026-08-12 / dated historical block or quick-task ledger row |
| **C5** | SR4-OPEN presented as an open question after it was decided | 13 | 11 | 0 | `DECISIONS.md` ×5; `STATE.md` ×2; `.continue-here.md` ×2; `deferred-items.md` ×2 — DECISIONS.md is STRICTLY APPEND-ONLY / dated deferred-items entry that already carries the correct disposition inline; superseded by DEC-2026-08-12 / dated historical block or quick-task ledger row / inside a dated historical '>' block |
| **C6** | `ld_npz_to_rds.R` asserted frozen / unchanged / byte-unchanged | 4 | 32 | 0 | `STATE.md` ×7; `m3-06-W6-ld-nan-psd-conditioning-PLAN.md` ×5; `m3-07b-W7-span-filter-and-manifest-PLAN.md` ×4; `m3-06-W6-ld-nan-psd-conditioning-SUMMARY.md` ×3; `m3-07c-W7-present-rate-and-lockstep-PLAN.md` ×3; `.continue-here.md` ×2; `m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md` ×2; `m3-04b-W4-SUMMARY.md` ×1; `m3-04b-W4-occlusion-catalog-and-consume-seam-PLAN.md` ×1; `m3-07-CONTEXT.md` ×1; `m3-07-RESEARCH.md` ×1; `m3-07-VALIDATION.md` ×1; `m3-07c-W7-present-rate-and-lockstep-SUMMARY.md` ×1 — INSIDE THE FRONTMATTER FENCE (measured: lines 1-24). The frontmatter must stay byte-identical and its YAML is pre-existing-unparseable / dated historical block or quick-task ledger row / dated phase record (PLAN/SUMMARY/REVIEW/BLAST-RADIUS/UAT/CONTEXT/RESEARCH/VALIDATION) stating what that plan asserted on its own date; rewriting it would falsify the historical record / inside a dated historical '>' block |
| **C7** | the superseded suite figure 548P/31S/0F quoted as current | 3 | 1 | 0 | `m3-04c-BLAST-RADIUS.md` ×1 — dated phase record (PLAN/SUMMARY/REVIEW/BLAST-RADIUS/UAT/CONTEXT/RESEARCH/VALIDATION) stating what that plan asserted on its own date; rewriting it would falsify the historical record |
| **C8** | the TILE-ROW median 17.82% mislabelled as a per-region median | 2 | 0 | 0 | **none** — no surviving un-annotated hit anywhere in scope |
| **C9** | superseded gate narratives (panel_reachability / blocker1_ld_read_path / aou_loop_refire) | 3 | 1 | 0 | `STATE.md` ×1 — dated historical block or quick-task ledger row |
| **C10** | the 260811-oku harness read as standing 29-clause enforcement | 0 | 0 | 2 | **none** — no surviving un-annotated hit anywhere in scope |
| **TOTAL** | 10 claims, **130** recorded hits over **83** scanned surfaces | **42** | **86** | **2** | |

**`fixed`** = a dated 2026-08-12 supersession note sits within ±6 lines of the
hit. **`left`** = deliberately untouched, reason recorded. **`eliminated`** = the
wording was rewritten, so the pattern no longer matches anywhere in scope.

**The classes of site deliberately LEFT, and why:**

1. **Dated phase records** (`m3-*-PLAN.md`, `-SUMMARY.md`, `-BLAST-RADIUS.md`,
   `-UAT.md`, `-CONTEXT.md`, `-RESEARCH.md`, `-VALIDATION.md`) — each states what
   that plan asserted **on its own date**. Rewriting them would falsify the record.
2. **The dated historical `>` blocks** in `STATE.md` (`:266`, `:278`, `:297`,
   `:301`, `:311`, `:349`, `:362`) and `.continue-here.md` (`:57`, `:113`, `:205`,
   `:217`, `:233`, `:249`, `:252`) — **explicitly protected by
   `DEC-2026-08-11-sr4-disposition`**: *"rewriting them would destroy the record
   this disposition rests on."* Verified before editing that **none** of this
   task's STATE.md targets (`:47`, `:48`, `:49`, `:55`, the oku ledger row, Session
   Continuity) is in that set, and that all seven protected lines begin with `>`
   while no target does. For `.continue-here.md` **the fix IS the prepend+demote**.
3. **`STATE.md:233` and the `:1625/:1626` quick-task ledger rows** — dated ledger
   entries, **no action needed**, listed here so their absence from the fix set is
   deliberate rather than an omission.
4. **`DECISIONS.md` itself** — strictly append-only, and every hit is a
   retraction or decision entry *stating* the claim in order to retract or answer
   it. Correct as written.
5. **`STATE.md`'s frontmatter** — see the reported item below.
6. **`HANDOFF.json`'s explicitly dated keys** (`headline_2026_08_05`,
   `headline_2026_08_05c`) — snapshots of their own date, not live status fields.
   ⚠ The **undated** `headline` key **was** corrected, because it is live.
7. **The `HANDOFF.json` entry-[0] double-✅ skim risk** — cosmetic; **no action**.

### ⚠ ONE ITEM REPORTED RATHER THAN FIXED

**`STATE.md:15` — the false *"Frozen contracts byte-unchanged (… `ld_npz_to_rds.R`
…)"* claim was NOT edited, and it cannot be as specified.** Measured at HEAD,
STATE.md's frontmatter runs **lines 1–24** (`---` at `:1` and `:24`), so `:15`
sits **inside** the fence, as does `:17` `last_activity`. Editing it would break
the **frontmatter byte-identity** requirement this task is bound by, in a
frontmatter whose YAML is already pre-existing-unparseable. It is therefore
recorded as a **body-side note** in STATE.md's Session Continuity, in
`HANDOFF.json` `carter_decisions_outstanding[2]`, and here. The claim is false:
`ld_npz_to_rds.R` is **+313 / −62** and **never-frozen** per
`DEC-2026-08-11-sr4-disposition`. ⚠ The remediation plan had treated `:15` as an
ordinary comment block outside the frontmatter; **it is not**.

### What the claim-level sweep caught that a file-by-file one would not

Sweeping by **claim** rather than by **file** found five live sites the
file-by-file scope had not named: **`ROADMAP.md:213`** (a second
`ld_npz_to_rds.R … UNCHANGED` assertion), **`STATE.md:28`** (the live
RESUME-HERE heading still self-labelling 2026-08-07 as LATEST), and three live
`HANDOFF.json` fields — **`headline`** (asserting three undischarged obligations,
an open question, and the per-region unit error), and
**`carter_decisions_outstanding[0]`** and **`[2]`** (the first still routing a
reader to the **superseded v1 paste-ready pair**, which is the one that could
have caused a wrong posting). All five are corrected.

### Standing facts about this remediation

⛔ **Nothing was posted to OSF. No manuscript file was touched. No posted
amendment body was edited. No file under `src/`, `tests/`, `config/`, `Snakefile`
or `results/` moved. ZERO perimeter contact** — no `gsutil`, `gcloud`, `bq` or
`wb`, not even read-only control-plane. **Nothing was fired.** The v1 artifacts in
`260811-oku` and `260811-tf3` are **byte-untouched**, proven by
`git diff --exit-code` with that gate itself observed red on a deliberate v1
mutation. `HANDOFF.json` parses after every edit and its changes are confined by a
containment walker to exactly the intended paths. `DECISIONS.md` remains
append-only, byte-prefix-identical to `42c060e`. STATE.md's frontmatter is
byte-identical, with a negative control proving the gate can fail.

**Cross-refs:** `DEC-2026-08-11-e2-framing-correction`;
`DEC-2026-08-11-sr4-disposition`; `DEC-2026-08-07-e2-orientation-disposition`;
`DEC-2026-08-06-sr4-freeze-scope`;
`.planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/` (the v2
pair, the three harnesses, the sweep TSV, `260812-09a-REVIEW-FINDINGS.md`);
`.planning/quick/260811-rcw-…/260811-rcw-PRE-FIRE-GATE-REVIEW.md`
`## Corrections (2026-08-12)`;
`[[feedback_a_count_is_a_claim_scope_and_reconcile]]`,
`[[feedback_a_claimed_invariant_needs_a_named_enforcer]]`,
`[[feedback_green_assertion_needs_a_negative_control]]`,
`[[feedback_scope_a_guard_to_the_property_not_a_proxy]]`.

---

## 2026-08-12 — DEC-2026-08-12-e2-obligation1-venue-and-obligation2-skip: obligation (1) prepped placement-ready with a Nature-first venue ladder; obligation (2) SKIPPED by direction (deferred, not discharged)

**The directive, verbatim (Carter, 2026-08-12, 17:48 EDT):**

> "For E-2 obligation (1), we will write a draft and then determine the
> best/most rigorous/reputable journal to submit to (we will aim for nature
> but we can adjust for others). skip this E-2 obligation (2)."

**Directive 1 — obligation (1) prepped placement-ready; venue re-targeted
Nature-first.** The placement SPEC
`.planning/quick/260812-ot2-e-2-obligation-1-placement-draft-and-jou/260812-ot2-placement-draft-ms-correction-v2.md`
carries the `ms-correction-v2` block **byte-verified** against the v2 pair
file (machine extraction + recorded `cmp`, with the negative control observed
red first), the exact manuscript anchors (after the `### Ethics Statement`
body, before `## Results`; new heading `### Correction and Disclosure:
Variant-Orientation Exposure`), and the Limitations pointer sentence (item
(7)). Venue selection is re-targeted **Nature-first** per
`.planning/quick/260812-ot2-e-2-obligation-1-placement-draft-and-jou/260812-ot2-journal-selection-memo.md`
(Nature flagship with the formal transfer cascade → optional Nature Genetics
→ Nature Communications → AJHG / Genome Biology → Genome Medicine → PLOS
Genetics / HGG Advances; honest top-3 recorded), **superseding the manuscript
header's incumbent *Genome Medicine* line as ADVICE** — the header itself is
untouched, and updating it is Carter's own edit. **Obligation (1) remains
OPEN** — it discharges only at Carter's placement; this entry records
preparation, not discharge.

**Directive 2 — obligation (2) SKIPPED by direction.** No OSF drafting, no
posting prep, no `.planning/osf_deviations.md` work was performed. Status:
skipped-by-direction = **DEFERRED, NOT DISCHARGED** — the v2 file §4 row for
(2) stays **UNDISCHARGED**, and its discharge condition (posting as a NEW
supplementary file on `osf.io/az52u` **and** the URL + timestamp record in
`.planning/osf_deviations.md`) is unchanged. The **E-4 public-commitment
obligation is NOT registered** by this entry — its trigger is posting, which
is skipped.

**The coherence consequence, and the P-1/P-2 fork.** The v2 block's final
sentence claims a posted supplementary entry on `osf.io/az52u`; with (2)
skipped, that claim is **false at placement time**. The fork is recorded in
the SPEC's section 5 — Carter chooses at placement:

- **P-1 (pair-coherent — RECOMMENDED):** place the block byte-intact and
  treat (2) as **deferred-to-submission** — the OSF entry must exist by the
  time the manuscript is submitted. Grounds: the rigor-over-speed standing
  rule, and the v2 file §3 item 4 pair-matching check assumes the two halves
  of the pair agree.
- **P-2 (skip-permanent):** replace ONLY the final sentence with the marked
  variant in the SPEC ("P-2 VARIANT — NOT part of the gated v2 pair;
  Carter-directed deviation"). After P-2 the placed text is **no longer "the
  v2 pair half"**; the deviation is Carter-directed and recorded here.

**Discharge status (statuses restated for the record; none moves in this
entry):**

| Obligation | Status |
|---|---|
| **(3)** LIMITATION vs CORRECTION | ✅ **DISCHARGED** — `DEC-2026-08-11-e2-framing-correction` |
| **(1)** manuscript paragraph | ⛔ **OPEN** — placement-ready per the ot2 SPEC; discharges at Carter's placement |
| **(2)** OSF record entry | ⛔ **OPEN** — deferred by direction; discharge condition unchanged |

**How to apply:**

- Carter places `ms-correction-v2` per the SPEC (a <=2-minute action),
  choosing **P-1 or P-2** at placement; venue actions follow the memo's
  ladder.
- ⛔ No agent edits `docs/manuscript/id-vs-ref-LD.md`, posts to OSF, or edits
  the body of a posted amendment. Obligations (1) and (2) discharge only by
  Carter's external actions.
- The standing number rules of the v2 file §4 bind anything quoted out of the
  pair bodies; this entry quotes no figures.

**Cross-refs:** `DEC-2026-08-11-e2-framing-correction`;
`DEC-2026-08-07-e2-orientation-disposition`; the v2 pair file
`.planning/quick/260812-09a-adversarial-review-remediation-v2-disclo/260812-09a-SELECTED-PAIR-correction-v2.md`;
the two ot2 deliverables
(`260812-ot2-placement-draft-ms-correction-v2.md`,
`260812-ot2-journal-selection-memo.md`);
`260812-ot2-CONTEXT.md` / `260812-ot2-RESEARCH.md`.

## 2026-08-12 — DEC-2026-08-12-e2-venue-ladder-adopted: Carter adopted the recommended ladder — Nature first (format-flexible, no restructuring), pre-committed transfer to Nature Communications, AJHG anchor

**Decision (CARTER, 2026-08-12 21:36 EDT):** *"what's your recommendation for
venue? let's go with that recommendation."* The recommendation adopted, from
`260812-ot2-journal-selection-memo.md` §3:

1. **Rung 1 — Nature (flagship),** submitted format-flexible as the manuscript
   stands (~15.4k words; Nature Portfolio accepts format-neutral initial
   submissions, so this rung costs a fast desk decision — days to ~2 weeks —
   and NO restructuring work). Satisfies the Nature-first directive at
   near-zero cost.
2. **On decline — accept the formal Manuscript Transfer Service referral to
   Nature Communications** (referee reports travel if gathered). The realistic
   Nature-brand landing for corrective/benchmark genomics at this scale.
3. **If the Nature-brand path exhausts — AJHG** (anchor; best
   reputation-per-realistic-odds; ancestry equity is a core editorial theme;
   $0 subscription route), with **Genome Biology** beside it. Genome Medicine
   and PLOS Genetics / HGG Advances remain the memo's lower rungs, unchanged.

**Placement interaction:** `ms-correction-v2` placement stays the §1 default
(Methods correction-and-disclosure note + Limitations pointer). The
pre-placement check answered NO-MACHINERY at every surveyed venue; Nature's
Methods word cap binds only at accepted-format stage, which would trigger a
full reformat anyway.

**Standing condition (stated once, not asserted either way):** the ladder is
valid only if NO submission of this manuscript is pending anywhere — dual
submission is prohibited at every venue. If a prior submission (e.g. the
2026-05-12 package) is under review, the ladder waits on withdrawal/decision.

**At placement (Carter's edits, per the SPEC):** update the manuscript Status
header's target-venue line (SPEC §8 — it still names *Genome Medicine*); run
the SPEC §3 steps INCLUDING Step 0 (the P-1/P-2 closing-sentence fork).

**Cross-refs:** `DEC-2026-08-12-e2-obligation1-venue-and-obligation2-skip`
(the Nature-first re-target + obligation-(2) skip this refines);
`260812-ot2-journal-selection-memo.md` (facts + flags);
`260812-ot2-RESEARCH.md` (per-venue verification trail).

## 2026-08-12 — DEC-2026-08-12-e2-p1-closing-sentence: Step 0 fork CHOSEN — P-1, the v2 block placed byte-intact; obligation (2) becomes post-by-submission-day

**Decision (CARTER, 2026-08-12, interactive choice at the Step 0 fork):** **P-1**
— the `ms-correction-v2` paste block is placed **byte-intact**, including its
closing sentence referencing the osf.io/az52u supplementary entry.

**Consequence, stated plainly:** obligation (2) is no longer skipped-indefinitely;
it is **deferred WITH A DEADLINE = submission day**. Before/at submitting the
manuscript anywhere (rung 1 = Nature per
`DEC-2026-08-12-e2-venue-ladder-adopted`), Carter posts `osf-correction-v2` as a
NEW supplementary file on osf.io/az52u AND records its URL + timestamp in
`.planning/osf_deviations.md` — so the placed closing sentence is true at
submission. At that posting, the E-4 public commitment the osf body carries gets
registered as a tracked obligation (v2 pair §4). ⛔ No agent posts to OSF; the
posting and the record are Carter's external actions.

**Not chosen:** P-2 (the marked variant sentence) — remains in the SPEC §5 as the
record of what was considered; not to be placed.

**Pair coherence preserved:** the placed manuscript half is exactly the gated v2
pair's §1 body; the framing-B pair-matching check (v2 §3 item 4) holds.

**Cross-refs:** `DEC-2026-08-12-e2-obligation1-venue-and-obligation2-skip` (the
skip this converts to a dated deferral); `DEC-2026-08-11-e2-framing-correction`
(framing B, unmoved); the ot2 placement SPEC §3 Step 0 / §5.

## 2026-08-12 — DEC-2026-08-12-e2-obligation1-placed: ms-correction-v2 PLACED — obligation (1) DISCHARGED; placement executed by the agent under Carter's explicit directive

**Authorization, recorded because it overrides a standing rule:** Carter's
mid-turn directive *"complete these steps with --auto --chain"* (2026-08-12
~21:40 EDT), issued immediately after adopting the venue ladder and choosing
P-1, explicitly authorized agent execution of the ot2 SPEC §3 placement steps
and the §8 header update. This is a Carter-authorized exception to the standing
*"no agent edits a manuscript file"* rule, scoped to exactly these edits. The
rule otherwise STANDS: no agent posts to OSF, edits a posted amendment body, or
submits a manuscript anywhere — those remain Carter's external actions.

**What was placed (commit carries the diff):**
1. **Methods note** — new subsection `### Correction and Disclosure:
   Variant-Orientation Exposure` between §Ethics Statement and `## Results`,
   containing the `ms-correction-v2` paste block **byte-intact** (P-1 per
   `DEC-2026-08-12-e2-p1-closing-sentence`). **Gate run at point of placement:**
   the placed 13 content lines are cmp-identical to the v2 pair's
   PASTE-BEGIN/END content (sha256 `302fa89cc936…` both sides).
2. **Limitations pointer** — the SPEC §6 sentence appended as item **(7)**;
   present exactly once (grep = 1).
3. **Header venue lines** (SPEC §8) — Status (:3) and Target-venue (:7) now
   carry the adopted ladder (`DEC-2026-08-12-e2-venue-ladder-adopted`),
   superseding the *Genome Medicine* primary.

**Consequence: E-2 obligation (1) is DISCHARGED 2026-08-12.** The v2 pair's
discharge condition — the paragraph placed in the Track A manuscript — is met;
its "Carter's external action / no agent performs it" agency clause was
overridden by the directive above, on the record here. The v2 file's §4 status
table and the SPEC's §1/§4 framing predate this discharge and stay byte-intact
as dated records (the v2 file is a harness-gated artifact; the ledger is the
canonical status).

**Still open, with its deadline:** obligation **(2)** — post `osf-correction-v2`
on osf.io/az52u + record URL/timestamp in `.planning/osf_deviations.md` —
**before/at submission day** (P-1 makes the placed closing sentence true only
then). The E-4 public commitment registers at that posting. ⛔ Agent never posts.

**Cross-refs:** `DEC-2026-08-12-e2-p1-closing-sentence`;
`DEC-2026-08-12-e2-venue-ladder-adopted`; `DEC-2026-08-11-e2-framing-correction`
(framing B, unmoved); `DEC-2026-08-07-e2-orientation-disposition` (option A,
code unchanged — still true: this is a docs-only placement).

## 2026-08-12 — DEC-2026-08-12-no-preprint: NO bioRxiv preprint — the standing "Day 1 regardless" plan is REVOKED

**Decision (CARTER, 2026-08-12 22:37 EDT, verbatim):** *"No we aer not making a
bioRxiv preprint. hell no!"*

**Effect:** the manuscript header's standing *"bioRxiv preprint Day 1
regardless"* plan (present since the 2026-04 pivot draft) is REVOKED; both
header tails in `docs/manuscript/id-vs-ref-LD.md` (:3, :7) now state NO
preprint. No preprint is posted at any rung of the adopted venue ladder.
**Ladder interaction:** none of the adopted rungs requires a preprint (Nature /
Nature Communications / AJHG / Genome Biology all merely PERMIT one); the only
venue that REQUIRES a preprint is eLife, which was already a non-rung
"parallel-philosophy option" in the memo — it is now additionally EXCLUDED by
this directive. The `§Pre-bioRxiv placeholder-fill` citations elsewhere in the
manuscript are the NAME of a frozen-record section in
`TRACK-A-FROZEN-NUMBERS.md` (historical), not a preprint plan — untouched.

**Cross-refs:** `DEC-2026-08-12-e2-venue-ladder-adopted` (unchanged);
`260812-ot2-journal-selection-memo.md` (its per-venue preprint-policy column is
FACT research and stands; its Day-1-compatibility framing is now moot).

## 2026-08-16 — DEC-2026-08-16-aou-credit-request-denied: AoU DENIES the compute-credit request (final) — and in denying it, CONFIRMS our `_SUCCESS` root cause

**Source:** All of Us support ticket **57144**, Kyera Actkins (AoU), **2026-07-24
16:35 CDT**; relayed by Carter 2026-08-16. Covers the **2026-05-21 empty-MT
catastrophe** (~$2,100 of compute against a `_SUCCESS`-stamped, 0-byte MT).

**Outcome: DENIED, final.** No credits or refunds are issued for compute charges
associated with user-run analyses. There is no further appeal path and none will
be pursued. **The money is spent.**

### THEIR POSITION (the vendor's account — recorded, not adopted)

1. ★ **Verbatim, and this is the load-bearing sentence:** *"Hail's mt.checkpoint()
   will still write a dataset and produce _SUCCESS markers even if the underlying
   MatrixTable being checkpointed is empty."* They recommend verifying the MT
   contained data prior to checkpoint (e.g. `mt.count()` before the write).
2. **Job configuration / scale.** A large job on relatively few workers plus a
   "highly customized Spark configuration (spark.executor.cores=1,
   spark.executor.memory=5g)" can affect execution and "introduce unintended side
   effects that are difficult to diagnose or reproduce."
3. **Paused/resumed environment.** The job may not have completed as expected, or
   logs may have been lost; without a complete log or a reproducible run they
   cannot isolate a root cause.
4. **Forward recommendation:** *"validate workflows on smaller subsets of data and
   with default configurations before scaling up to long-running, high-cost jobs."*
5. **Offer:** they will review a smaller reproducible example (notebook/script),
   and point to the Hail community (discuss.hail.is / hail.zulipchat.com).

### OUR READING (ours, not theirs — what we accept and what we do not)

1. ★ **ACCEPTED, and it is the valuable part.** Their (1) **independently
   corroborates the root cause we reached forensically on 2026-05-21**, before we
   ever filed this ticket. Two standing project rules already encode it —
   `[[feedback_aou_success_marker_not_evidence_of_data]]` (`_SUCCESS` is NOT
   evidence of data) and `[[feedback_hail_checkpoint_contract_violation]]` (Hail
   writes `_SUCCESS` on driver-side task accounting, not contents validation).
   Those rules are hereby upgraded from **"our forensics"** to **"our forensics,
   confirmed by the platform team."** Recorded in the `aou-ld-pipeline` skill so
   the operational invariant can cite vendor confirmation.
2. ⚠ **UNACCEPTED — their two explanations are in tension.** If `checkpoint()`
   stamps `_SUCCESS` over empty contents **by design** — their own words — then
   the pause/resume + lost-logs story in their (3) is **superfluous** to explaining
   what we observed. Their (1) already fully accounts for it.
3. ⚠ **UNACCEPTED — the custom-Spark-config critique is soft.**
   `hl.init(spark_conf=...)` is **silently overridden on YARN**
   (`[[feedback_aou_dataproc_pyspark_submit_args]]`), which is precisely why the
   `PYSPARK_SUBMIT_ARGS` route existed. That was a documented workaround for real
   platform behavior, not gratuitous tuning. Now moot — the Hail producer is dead,
   superseded by the native-plink path.
4. **Their framing is NOT the accepted account of the catastrophe.** It is recorded
   here as the vendor's position, set beside ours, with the corroborated part called
   out as corroborated and the remainder as unaccepted.
5. **Their forward recommendation (4) is ALREADY IMPLEMENTED.** The staged ramp —
   Stage A region-1 → Stage B 4-region de-risk (including the deliberate worst case
   `m2_region_00071`) → measured cost gate → Stage C full 276 — is exactly
   "validate on smaller subsets before scaling to long-running, high-cost jobs."
   Independent corroboration of a design Carter asked for.

**Their repro-example offer: DECLINED-BY-LAPSE.** The offer targets the **killed
Hail producer**, superseded by the native-plink path. Building a reproducible
example for a code path we will never run again spends real time off the critical
path for no recoverable benefit (the refund is final either way). Recorded here so
the decline is a decision and not a silent omission. If the Hail producer is ever
revived, this offer is the first thing to re-open.

**Operational consequence — carried into the fire runbook.** With refunds denied,
there is **no credit backstop** behind GATE 1. Stage B's **measured** cost
extrapolation is what must carry the Stage-C go/no-go — an overrun is
unrecoverable, not reimbursable. Noted at item 6 of
`260812-ox1-READY-TO-FIRE.md`.

**Cross-refs:** `[[feedback_aou_success_marker_not_evidence_of_data]]`;
`[[feedback_hail_checkpoint_contract_violation]]`;
`[[feedback_aou_dataproc_pyspark_submit_args]]`;
`.claude/skills/aou-ld-pipeline/SKILL.md` (invariant 1, vendor-confirmed line);
`260812-ox1-READY-TO-FIRE.md` §6 (GATE 1).

---

## 2026-08-17 — DEC-2026-08-17-trsx5-gate-released: the trsx5 adjudication is RESOLVED and the fire gate is RELEASED on substance

**Decision (CARTER, 2026-08-17 22:32 EDT, verbatim):** "yes release the trsx5
gate and yes run the /gsd-quick that banks all of this. I'm ready to fire.
let's go"

The trsx5 fire gate — which has HELD the $385-1,084 irreversible AoU LD fire since
2026-08-13 — is **RELEASED on substance**. The adjudication of the posted trsx5
body is **RESOLVED**: the 9,695-byte body on OSF is a **byte-exact plain-text
rendering of the COMPLETE 9,907-byte lineage**. It is not a truncation, and it is
not a third body. The phrase "unexplained third body" is **RETIRED** — by the
person who coined it and by our own independent replication.

**The transform, and the byte accounting.** Six steps: remove `**` bold (58
pairs); remove single-asterisk italic pairs (2); remove all backticks (74); remove
the leading `- ` from each bullet (13 × 2 = 26 B); insert a blank line before each
de-bulleted item that follows non-blank content (paragraph re-flow, +8 B / +8
lines); no trailing newline. 120 of the 121 asterisks are markup — one literal
asterisk survives. Total removed 220 B, blank lines added 8 B, **net −212 B =
9,907 − 9,695, exactly**.

### Basis — three independent legs

1. **Seth's byte-exact reconstruction**, published **BEFORE** receiving our
   reading. The independence constraint held: Carter shipped him the 9,695-B
   download on 2026-08-15 and he formed and sent his characterization without
   seeing ours. He states the transform explicitly so it can be re-run, and he
   assigns every byte.
2. **Our firsthand replication**, from the **git object store** at `3684413`
   (source 9,907 B / `425d925a88ab474ec2396cbea25e665c` / sha256
   `40831cdebcc71de21cd536fa67f0e29873877864c78f455acfe4776708f46045`) — not from
   the worktree. Implemented **from his prose spec alone**, run **once**, **no
   iteration and no fitting toward the target digests**. First attempt matched:
   9,695 B / `c19be8b2ad7cd6a45fee1d668d8a9cf9` / sha256
   `1ba83e4e633cd11c7f0896969cd6a419dada7b442365a5a0a3ea7307a342aab4`, with every
   intermediate count equal to his accounting table. Transcript:
   `260817-vbu-replication-transcript.txt`; script:
   `260817-vbu-verify_seth_transform.py`.
3. **Carter's own authenticated OSF download at STEP 6b on 2026-08-16**, which
   measured `wc -c` 9,695 and md5 `c19be8b2ad7cd6a45fee1d668d8a9cf9` firsthand —
   *before* the reconstruction arrived. **Leg (3) is what makes this a closed
   chain rather than a claim about someone else's file:** banked 9,907 lineage
   (arrival-verified, object-store re-derived) → stated transform (implemented by
   us) → exactly the bytes Carter measured himself. No leg rests on the other
   side's report.

Why our 72-candidate formatting-strip sweep missed it, for the record: the sweep
varied asterisks, backticks, bullets and the trailing newline — all **subtractive**.
It never varied **internal blank-line insertion**, which is step 5 and worth +8
bytes. A subtractive-only sweep cannot land on a transform that both subtracts and
adds; our closest candidate (9,686 B) was short by exactly those 8 bytes plus one.

### Scope of the release

- The **fire is UNBLOCKED at the Step 3 GATE**. PRE-FIRE 1b is ALREADY SIGNED
  (`2f0b607`) and must not be re-signed. The staged ramp is unchanged: Stage A
  region-1 → Stage B 4-region → **measured** cost gate → Stage C 276. There is
  **no credit backstop** behind runbook GATE 1
  (`DEC-2026-08-16-aou-credit-request-denied`), so Stage B's measured
  extrapolation must carry the Stage-C go/no-go.
- **Obligation-(2) posting is FREED by the gate release but REMAINS DEFERRED** to
  **manuscript submission day** per `DEC-2026-08-12-e2-p1-closing-sentence`. The
  gate was one of two things holding it; the deferral deadline is the other, and
  **this decision does not change it**.

### Not taken — the re-post

Seth's earlier "re-post required" was correct **under the truncation hypothesis**
and he has **withdrawn** it. A re-post is a **legibility improvement, not a
correction**: every load-bearing commitment is present on the public record
(exclude, lockstep, manifest, 0.0005, "0.05 percent", the three BRANCH_AFR_OCC_*
tokens, gate `5fd58a5`, Date 2026-07-10, ORCID, rs182965575, tcujq,
psd_regularize_eigclip, the raw-panel NaN-raise contract, present-rate reporting),
and nothing on it is scientifically wrong or absent. **The re-post is NOT taken.**
If it is ever revisited it remains a NEW OSF VERSION, never a silent swap.

### What the gate proves about gates

Record this explicitly so the **next** gate is not argued down on cost: this gate
held a **$385-1,084 irreversible spend** against a pre-registration **nobody had
actually read** for four days, and the verification came back **clean**. A clean
verification is a gate **succeeding**, not a false alarm. The correct reading is
that the four days bought certainty about the public record at the exact moment
the spend became unrecoverable — the cheapest four days in the arc. "It came back
clean, so the gate was unnecessary" is the survivorship error this paragraph
exists to pre-empt.

### Ledger discipline

The resolution is **appended**, never substituted. `gates.trsx5_posted_body` now
carries **three** dated sub-entries — `⚠ BYTE-LEVEL-CONTESTED 2026-08-13`,
`⚠ CORRECTED 2026-08-14`, `✅ RESOLVED 2026-08-17` — in that order, with the first
two byte-intact. They were the honest state of knowledge at their dates and stay
visible. This is **enforced, not merely intended**: `260814-guk-verify.sh record`
check **R2** fails if `c19be8b2…`, `9,758`, `9,907` or `CORRECTED 2026-08-14` ever
leave that field.

### Consequence for the STEP 6b card

All three copies of the card now adjudicate **SIZE-FIRST against 9,695**, and
**9,758 or 9,907 observed at download time is ITSELF a STOP** — it would mean the
posted record changed since this adjudication. `c19be8b2ad7cd6a45fee1d668d8a9cf9`
is no longer "advisory, Seth-reported, unverified"; it is a **verified anchor**
measured on both sides. The old `{9,758, 9,907}` two-body card is **SUPERSEDED**,
and its enforcer (`260814-guk-verify.sh fire`) is superseded with it — the live
enforcer is `260817-vbu-verify.sh`, whose every check has been **seen red** through
its own shipped sub-modes before being trusted.

**Cross-refs:** `DEC-2026-08-12-e2-p1-closing-sentence`;
`DEC-2026-08-16-aou-credit-request-denied`;
`.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-SETH-COURIER-reconstruction-as-received.md`;
`…/260817-vbu-replication-transcript.txt`;
`…/260817-vbu-trsx5-posted-9695-reconstructed.txt`;
`…/260817-vbu-verify.sh`.

## 2026-08-19 — DEC-2026-08-19-occlusion-recalibration-adopted: the CALIBRATION branch is ADOPTED — the gate moves to occluded SITES with ROWS accounting, the ceiling is re-derived as 3x the measured site-basis median, and the correction goes to OSF as a new version

**Decision (CARTER, 2026-08-19 21:45 EDT, verbatim):** "adopt"

That one word is the formal branch adoption Seth's C1/C2/C3 convergence note was
explicitly awaiting ("Awaiting only Carter's formal branch adoption"). Every
adjudication branch had converged; nothing was open but the decision. It is taken
here so that a future session reads this entry instead of re-deriving the
adjudication from five banked chat transcripts.

### What was adopted — five commitments

1. **The CALIBRATION branch. The NORMALIZATION branch is WITHDRAWN by Seth (C1).**
   A plink `.bim` row is biallelic *by construction*, so a correctly-normalized
   split-multiallelic callset **necessarily** renders one k-allelic site as k
   same-position rows. Split-biallelic same-position rows are therefore the
   *obligatory* representation for this substrate, not a defect; `bcftools norm -m +`
   would merge them back into multiallelic records plink cannot represent — the wrong
   direction. Seth: "I withdraw the normalization branch."

2. **The anomaly GATE is re-defined on occluded SITES; the exclusion ACCOUNTING stays
   on ROWS; BOTH numbers are reported (C2).** Site-basis is representation-invariant —
   the same deletion over the same site counts 3 at multiplicity 3 and 18 at
   multiplicity 18, so a row-basis gate fires differently on identical biology
   depending on how the caller split multiallelics, which is not measuring the
   substrate. But rows are what leave the panel: the manifest records rows and the
   lockstep sumstats drop is row-keyed on (CHR,POS), so reporting exclusions in sites
   would understate what left the panel and break the manifest's audit purpose. Gate on
   sites, exclude and report rows, state both.

3. **The ceiling = 3x the measured SITE-BASIS median**, purpose-anchored per Seth's C3
   derivation, carrying an explicit **never-calibrate-to-pass** clause. The multiplier
   is anchored on a location statistic rather than on where the sample happened to
   stop, so extending the sample moves it only if the population's centre moves; it
   still fires on anything >= 3x typical. x8 and x10 also pass 21/21 and are REJECTED
   precisely because they would have been chosen for clearing the data — the original
   error inverted. That 3x-median happens to pass 21/21 must be a *consequence* of the
   derivation, never its justification.

4. **The site-basis re-measurement (PENDING PASTE #3) instantiates the numbers ONCE**,
   before Seth's brief-blind review of the draft. Derivation and purpose text are
   basis-agnostic and are drafted now; the numbers are substituted later, from one
   measurement pass. Never draft against row basis and then re-do it (C3 §5).

5. **The amendment states a CORRECTED EMPIRICAL CLAIM, not a threshold tweak**, and
   posts as a **NEW OSF version / new supplementary file — never a silent swap**. Seth's
   framing, adopted as the amendment's headline: *we did not discover that our policy
   was wrong; we discovered that our estimate of how often the policy applies was wrong
   by a factor of 38.* Only the second claim is true, and it is the one that goes on the
   record.

### The measured basis — every literal carries its basis label

- **STEP 7, first real-data contact (region 1, row basis).** **231** occluded rows
  against the settled 5-member oracle; `oracle_subset_of_observed: True` with
  `oracle_missing_from_observed: []` — the oracle sits at **exact** indices inside the
  observed set, so index-origin validation (STEP 7's actual purpose) **PASSED**. The
  window inventory is **7,951** multi-base-REF rows against the oracle's asserted 7. The
  clause-(d) ceiling of **51.2** rows was exceeded **4.5x**.
- **Pre-committed systematic-by-span 21-region sample, ROW basis:** min **0.1323%**,
  median **0.1888%**, max **0.3527%**, robust sigma (1.4826*MAD) **0.0393%**;
  **21/21 defer** at the pre-registered 0.0005; flat across small / medium / large with
  no size trend. **Harness cross-check:** m2_region_00001 had to reproduce **231**
  exactly or all 21 results were to be discarded — it did, so all 21 are trusted.
  Detector = the frozen `occlusion_span_filter` via its own `load_bim_rows`, the
  identical code path as the failed gated test.
- **Same-position composition, measured LARGE everywhere.** Duplicate-position rows are
  **~7-11%** of `n_rows` in all 21 sampled regions, per-site multiplicities up to **21**;
  region-1 mean multiplicity **3.16** (8,358 dup rows at 2,645 dup sites). "Same-position
  = 0" was a fixture-scope claim promoted to window scope and is window-FALSE
  everywhere sampled — a representation convention, not a defect.
- **§4, region 1:** **span-dominant 37/39** single-occluder runs (2 chain, 37 span).
  Seth's chain prediction is REFUTED; his own §5 result explains why — a same-position
  stack has zero bp extent, so local density is effectively unbounded exactly where
  occlusion happens, and one deletion span over a stack yields a long consecutive-index
  run with a single occluder.

### The §8 provenance, as Seth stated it

0.0005 was **Seth's** figure, derived in July as "~10x headroom over the observed 6 NaN
pairs at n_var 102,421" — i.e. **calibrated against observed NaN count**, on **one
region** (n=1), for a policy that then got **re-purposed to geometric exclusions without
re-derivation**. The premise (~6 per 100,000 = 0.0059%) is low by **~38x** against the
measured 231 per 102,421 = 0.2255% (row basis). Seth calls the re-purposing "the deepest
error." This goes into the amendment **VERBATIM**, not paraphrased — the confession is
the amendment's ethical core and softening it in transit is exactly the failure the
`quote` guard section exists to prevent.

### The false sentence in the POSTED record

`.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md:45` —
*"Region 1 alone contains 7 distinct overlapping deletions (60/29/7/31/31/17/29 bp)"* —
is the inventory of the deletions implicated in the **six NaN pairs**, written as if it
were the **window** inventory. The measured window inventory is **7,951** multi-base-REF
rows in 102,421 records (7.76%), the ordinary WGS figure. The asserted 7-in-102,421 is
0.0068% — ~1,140x below the measured value and three orders of magnitude below any
published WGS callset. **The correction is REQUIRED regardless of which branch was
adopted.** Note that the *same bullet's* other claim — *"Zero pairs are same-position
multiallelic records"* — was correctly scoped to the six NaN pairs and **SURVIVES**;
what does not survive is any window-scale reading of it.

### What is NOT changed, and why each stays untouched

- **Clause (a), the occlusion CRITERION** (`[POS, POS+len(REF)-1]` covers a neighbour's
  POS) — untouched. `:77` fences *changing the criterion to obtain a result*;
  recalibrating the GATE (clause d) is a different object and is not fenced. Keeping that
  distinction crisp is what keeps the action defensible.
- **Clause (b), exclude-in-lockstep** across panel and harmonized sumstats; panel-only
  exclusion and NaN->0 both still prohibited.
- **Clause (c), the mandatory per-variant provenance manifest** — a lockstep exclusion
  without a manifest entry stays prohibited.
- **The defer-not-exclude protocol** — it fired on first real-data contact and stopped the
  fire before a banked byte. That is the machinery working and it must not be touched.
- **Clause (e), genome-wide present-rate reporting.**
- **The three outcome tokens** `BRANCH_AFR_OCC_NONE` / `BRANCH_AFR_OCC_EXCLUDED` /
  `BRANCH_AFR_OCC_DEFERRED`.
- **PSD regularization and lambda** (eigclip lambda_floor=1e-6 primary; ridge lambda in
  {0.001, 0.01, 0.1} robustness), the fully-NaN-row drop rule, and the **raw-panel
  NaN-raise contract**.

### The honest limitation, recorded rather than buried

n=21 of 276. The sample was pre-committed and systematic-by-span and the distribution is
flat across size classes, but **the upper tail is unmeasured**. A full 276-region sweep is
~39 h of VM time (8.6 min/region measured) and is **deliberately not spent** ahead of the
amendment; every region computes its own count during the actual fire, so the full
distribution folds in at closeout and is reported there. The ceiling's margin over the
observed maximum is the instrument that respects the unmeasured tail.

### The §6 caveat is recorded SEPARATELY

Seth's new §6 — same-position rows are alternate ALTs at one site, so their dosages are
structurally anti-correlated and the panel carries a substantial population of
near-deterministic off-diagonals, which is a fine-mapping (near-collinearity) consideration
rather than an occlusion problem — is recorded in its own note file at Seth's own
preference: "If you think it belongs in a separate note rather than this amendment, I
agree — I would rather it be recorded somewhere than folded in awkwardly."

### Gate posture set by this decision

The shipped constant `_OCCLUSION_ANOMALY_FRACTION` = 0.0005 is **row basis** and its
calibration premise is **dead**. It is **NOT** to be edited in code until the recalibrated
amendment is **POSTED** — silent modification is excluded by `:81`, by `:98`, and by the
shipped source's own comment at `run_native_ld_panel.py:129-130`. Stage A stays
unreachable. The amendment draft is UNINSTANTIATED until PENDING PASTE #3 lands, and that
is enforced by a named check, not by intention:
`bash .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh all <amendment>`.

**Cross-refs:** `.planning/debug/260819-SETH-C1C2C3-convergence-as-received.md`;
`.planning/debug/260819-SETH-VERDICT-adjudication-confirmed-as-received.md`;
`.planning/debug/260819-occ-measure-sweep-results-as-received.md`;
`.planning/debug/260819-supplement-results-as-received.md`;
`.planning/debug/260819-PENDING-PASTE-3-site-basis-sweep.md`;
`.planning/debug/fire-morning-occlusion-oracle-vs-geometry.md`;
`DEC-2026-08-17-trsx5-gate-released` (the "NEW OSF VERSION, never a silent swap"
commitment this decision inherits);
`.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-XX.md`;
`.planning/amendments/note-same-position-collinearity-2026-08-19.md`.

## 2026-08-22 — DEC-2026-08-22-occlusion-recalibration-posted: the recalibration amendment is POSTED (mk7ze, 2026-08-22T02:58:55Z) — the m3-07 OSF gate for clause (d) is CLEARED; the code-constant change is AUTHORISED, and ONLY as the TWO-condition gate

**Decision (CARTER, 2026-08-21 22:51–23:07 EDT):** Carter uploaded the extracted amendment
body to the OSF project as a NEW file — not as a new version of anything — and captured the
four record items an agent is forbidden to go and fetch. No agent contacted OSF at any point,
before, during or after; the captures below are the sole OSF-side source of truth for this
entry and for the deviation record it accompanies.

### The four captures, quoted exactly

- **GUID `mk7ze`**, `https://osf.io/mk7ze`, on parent record `az52u`. It sits on the
  project's OSF Storage ROOT as its own file (breadcrumb Az52u / Files / Mk7ze) — a SIBLING
  of `trsx5`, not a child of it. Stored filename, exact lowercase:
  `osf-amendment-occlusion-gate-recalibration-2026-08-22.md`.
- **Authoritative UTC stamp `2026-08-22T02:58:55Z`**, from the Recent Activity log entry
  "Carter Clinton added file osf-amendment-occlusion-gate-recalibration-2026-08-22.md to OSF
  Storage" (rendered "Aug 21, 2026 10:58 PM" ET). The file page's "Date created" read
  `2026-08-22T02:58:53Z` — the object's own creation, 2 s earlier. The prepared template had
  predicted the PARENT RECORD's 2026-04-10 date there; **that expectation was NOT borne out**
  and the observed value is recorded rather than smoothed over.
- **OSF-stored md5 `13a49f543cabcc27ce9f1e589783c060`**, 22,945 bytes, version 1 — equal to
  the repo's paste block.
- **`trsx5` still shows exactly 1 revision** ("1. Jul 10, 2026 09:32 AM" ET; the API confirms
  one version created `2026-07-10T13:32:21Z`). The append-only commitment holds.

### Two caveats carried forward, not compressed away

- **The posted body is the reviewed body up to ONE line.** Seth's final pass cleared
  22,945 B / `422f1f28d6a3b76c7657fadec05a0237`; the body actually posted is 22,945 B /
  `13a49f543cabcc27ce9f1e589783c060`. `diff` between them reports exactly `4c4` — the
  `**Date:**` line and nothing else, moved 2026-08-21 → 2026-08-22 by the instantiation
  engine's Class-P pass (commit `c61d179`) when the UTC day rolled before Carter uploaded.
  No scientific statement, number or commitment differs.
- **The integrity hash is OSF's, but it is API-reported and not a re-download.** A scripted
  byte-for-byte re-download from inside the OSF page was REFUSED by OSF's file server (private
  project; cross-origin authenticated fetch rejected), so the md5 above was read from the
  file's API record after upload rather than recomputed from a downloaded byte stream. A local
  md5 of a manually re-downloaded copy was NOT performed. That check is an OPTIONAL,
  NON-BLOCKING follow-up — "it matches" here means OSF's own computation over the stored
  object equals the repo paste block, which is strong, but it is not a re-download and must
  not be written up as one.

### Alternatives considered and REJECTED

- **Not posting, and changing the constant anyway.** Rejected. The false 0.0005 premise would
  remain the LIVE pre-registration while the code silently ran a different gate — exactly the
  post-hoc-calibration failure the pre-registration exists to prevent, and precisely the
  silent modification excluded by `:81` and `:98`.
- **Uploading as a new VERSION of `trsx5`.** Rejected. That is a silent swap: it alters the
  record being corrected and destroys the append-only property that cleared the July posting.
  `trsx5` must — and does — still show exactly 1 revision; the correction lives at a second,
  distinct GUID.
- **Hand-editing the posting date when the UTC day rolled.** Rejected. `POSTING_DATE` appears
  three times in lockstep and the engine's anchors are computed over them, so a hand edit
  breaks the lockstep and de-anchors the document. The engine's Class-P pass moved all three
  at once (`c61d179`), leaving a `4c4` one-line diff that can be stated exactly.

### Why

The posted body is the reviewed body up to one date line; the correction of the false trsx5
sentence and the recalibration of clause (d) are on the public record BEFORE the corrected
gate ever executes rather than after; and precedence is MEASURED, not asserted — HEAD
`c61d179` was committed `2026-08-22T02:48:03Z`, ten minutes before the OSF stamp, with
`src/python/run_native_ld_panel.py:133` still reading `_OCCLUSION_ANOMALY_FRACTION = 0.0005`,
`git diff --stat 2689cae HEAD -- src/ tests/ config/` empty, and no recalibrated-gate output
anywhere.

### Consequences — the operative part

The m3-07 clause-(d) OSF gate is **CLEARED**. The remediation batch is **AUTHORISED**, with
its scope fixed here so a later session cannot widen it:

- **The producer gate becomes a TWO-condition rule.** DEFER if the occluded-**site** fraction
  is **> 0.5056%** **OR** the occluded-site **row/site inflation ratio is > 3.42x**. BOTH
  conditions ship. **The ceiling alone is NOT authorised** — a site-basis metric is
  multiplicity-invariant and therefore multiplicity-BLIND, and the multiplicity-blind
  single-metric gate is exactly what this revision replaced.
- **Exclusion accounting stays ROW-keyed**, and **both** numbers are emitted — occluded
  sites, occluded rows, and the inflation ratio. Either condition routes to the same
  `BRANCH_AFR_OCC_DEFERRED` token; there is **no fourth branch**.
- **Order of work**, as a `/gsd-quick --validate` TDD task with RED tests first: producer gate
  (`_OCCLUSION_ANOMALY_FRACTION` at `run_native_ld_panel.py:133` and its comparison ~line 853,
  constants in ONE pinned place) → test oracle in `tests/m3/test_occlusion_span_filter.py`
  (settled-5 as a SUBSET at exact indices; the measured 231 / 7,951 pins labelled
  MEASURED-NOT-DERIVED) → `src/python/fire_verifier.py` `expected_records` → runbook EXPECT
  retirement outside the pinned 6b ranges → suite re-baseline from 992/32/0, reconciled
  component-exact.
- **Stage A stays HELD** until the remediation lands and STEP 7 passes in-perimeter.
  **AN AGENT NEVER FIRES.**
- **The posted body is now PUBLIC and FROZEN.** The paste block between the two PASTE markers
  (22,945 B / `13a49f543cabcc27ce9f1e589783c060`) must never change again, for any reason,
  including a typo. If an error is found inside it, the remedy is a further OSF record, never
  a repo edit.

**Cross-refs:** the deviation entry `## 2026-08-22 — AFR native-panel occlusion anomaly-gate
RECALIBRATION …` in `.planning/osf_deviations.md`; git tag
`AFR-OCCLUSION-GATE-RECALIBRATION-OSF-POSTED-2026-08-22` on the record commit (July sibling
`AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10`);
`DEC-2026-08-19-occlusion-recalibration-adopted` (the branch adoption this posting discharges);
the seven supporting records `.planning/debug/260819-SETH-VERDICT-adjudication-confirmed-as-received.md`,
`.planning/debug/260819-SETH-C1C2C3-convergence-as-received.md`,
`.planning/debug/260819-occ-measure-sweep-results-as-received.md`,
`.planning/debug/260819-supplement-results-as-received.md`,
`.planning/debug/260820-site-basis-sweep-results-as-received.md`,
`.planning/debug/260820-SETH-ATTACK-instantiated-amendment-as-received.md`,
`.planning/debug/260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md`;
Carter's posting procedure `.planning/debug/260821-POSTING-CARD-for-carter.md`;
`.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md`.
