# GSD Briefing — coloc_analysis

**Purpose of this file:** when a new GSD session starts in this directory, read this briefing before asking questions. It contains the vision, current state, critical constraints, and an independent evaluation of the existing revision plan that you (GSD) should treat as input, not re-derive.

**GSD version in use:** GSD v1 (`get-shit-done-cc@1.34.2`, the Claude Code plugin by TÂCHES). Slash commands use the `/gsd-<name>` form (hyphen, not colon): `/gsd-new-project`, `/gsd-discuss-phase`, `/gsd-research-phase`, `/gsd-plan-phase`, `/gsd-execute-phase`. State lives under `.planning/` in this directory.

---

## 1. Who / what / where

- **Author / single owner:** Carter K. Clinton, ASHES Lab, NCSU. Solo-author project.
- **Working directory:** `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/` (this directory)
- **Upstream code/data:** `/share/clintonlab/ckclinto/admixmap/` (the actual analysis code and primary results live here; this working directory contains configs, symlinks, and the revision plan)
- **Environment:** NCSU HPC, GPFS shared filesystem. Miniconda3 at `/rs1/researchers/c/ckclinto/miniconda3/`. GSD was installed into a dedicated conda env `gsd-tools` (Node 24 + gsd-pi 2.67.0). Activate with `conda activate gsd-tools`.
- **Git state:** **Not a git repo yet.** `git init` has not been run. One of the planned outputs of this work is converting it into a tracked repo.

## 2. Project in one paragraph

A cross-ancestry colocalization analysis of 5 cardiometabolic traits (BMI, T2D, hypertension, stroke, asthma) across ~50 pleiotropic loci, currently using coloc.abf with EUR-heavy GWAS and a small AFR fragment. A draft manuscript (`ajhg_manu_v10.pdf`) exists. On re-evaluation, the draft has multiple methodological weaknesses that would be flagged by any competent reviewer at a specialty journal, and an ambitious revision plan has been written to address them. **Target journals (in order):** Nature Genetics → American Journal of Human Genetics → Nature Metabolism → Cell Genomics → Genome Medicine.

## 3. Two goals for this GSD session (and why you're being called)

**Goal A — Reorganize the directory under GSD.** Right now `coloc_analysis/` is not a git repo, has scattered `.DS_Store` and `~$*` lock files, obsolete `AJHG_files*` directories from prior submission attempts, unpinned conda envs, no Snakemake DAG, and no top-level README. The first deliverable is a clean, tracked project layout that fits an R/Python/Snakemake research analysis (not a JS/code-project layout). `.gsd/` scaffolding should reflect that.

**Goal B — Turn the existing revision plan into executable GSD milestones.** The file [Revision_Plan.md](./Revision_Plan.md) at the root of this directory is a 559-line prose document that lays out 10 analytical phases for the manuscript revision. It has never been turned into tracked milestones/slices/tasks. That's what `/plan-milestone` (and upstream `/discuss`) is for.

**Read `Revision_Plan.md` before doing anything else.** It is the north-star document. Every analytical decision should reference it.

## 4. Critical constraints

- **100% publicly available data.** No wet-lab, no functional validation, no proprietary/industry datasets. All GWAS, QTL, single-cell, ancient DNA, chromatin, MPRA datasets are either public or available under standard academic DUAs.
- **Solo author.** No co-author review. Rigor must come from multi-method triangulation, pre-registration, and hold-out replication cohorts — see Revision_Plan §8.
- **Timeline is not a binding constraint.** Rigor and impact matter more than speed. Don't compress phases to save time.
- **Shared filesystem (GPFS).** GSD's default worktree isolation may behave badly on `/gpfs_common/` — **prefer `mode: solo` with `git.isolation: branch`** over worktree-based isolation.
- **No web/app tech stack.** Skip skill packs aimed at React/Next/Vite/etc. The relevant stack is R (coloc, susieR, TwoSampleMR, MendelianRandomization), Python (LDSC, PRS-CSx, selscan, Enformer/Borzoi inference), bash, Snakemake, conda. A genomics/research-analysis skill profile is the correct fit.
- **Data access lead times are the real critical path.** UKB-PPP, deCODE pQTL, FinnGen, MVP, All of Us, BBJ, Pan-UKBB require DUAs that take weeks-to-months. These applications should be kicked off in parallel with Milestone 1, not treated as gates.

## 5. Independent evaluation of Revision_Plan.md

(The following was produced by a separate review pass before this GSD session started. Trust it as a prior — do not re-derive.)

### 5.1 Strengths to preserve
- **Methodological upgrades are grounded in primary citations.** coloc.abf → coloc.susie (Wallace 2021), ad-hoc enrichment → MAGMA + LDSC partitioned heritability (de Leeuw 2015, Finucane 2015/2018), cross-ancestry concordance → matched-N + Hou 2023 power-corrected framework. Each swap fixes a specific flaw, not fashion-chasing.
- **Triangulation is baked in at every step.** MR uses IVW + Egger + weighted median + MR-PRESSO + MR-CAUSE + Steiger; pathway uses MAGMA + g:Profiler + LDSC; deep-learning uses Enformer + Borzoi + Sei + AlphaMissense. This substitutes for the absent internal co-author QC.
- **Phase 10 is clever.** Deep-learning variant prioritization + public MPRA overlap is a defensible all-computational substitute for wet-lab validation. Few papers at this level try this; done well it's a differentiator.
- **Section 12 correctly identifies Phase 2 (3-way QTL coloc against eQTL/pQTL/sQTL) as the single highest-leverage change.** Agreed — this is what unlocks causal-gene resolution and is the prerequisite for Phases 3, 4, 5, 8.
- **§10 quick wins are zero-regret.** Table 1/3 regeneration, dropping KCNJ11 asthma–HTN Tier-1 (n_SNPs=6 < stated ≥50 QC threshold), cleaning `.DS_Store`, citation reordering.
- **Honest about risks (§6).** Explicitly accepts that pathway-restricted PRS may not beat genome-wide PRS and commits to reporting null results. Unusual and good.

### 5.2 Gaps the plan under-weights — address these in planning

1. **Data access is the longest critical path, not Phase 0.** UKB-PPP, deCODE, FinnGen, MVP, All of Us, BBJ, Pan-UKBB all require DUAs with weeks-to-months lead times. The plan says "apply now" in §6 but the phase table treats access as a checkpoint. **Action:** insert a Milestone 0 ("Phase −1") for data access applications that starts on Day 1 and runs in parallel with everything else.

2. **Phase 1 SuSiE handling is under-specified for complex regions.** SuSiE default `L=10` credible sets means some regions yield up to 10×10 = 100 credible-set pair comparisons. No policy for regions where L hits the cap, no convergence-failure handling, no sensitivity sweep on `min_abs_corr`. Will matter at ≥5 of the 50 loci. **Action:** add an explicit slice under the Phase 1 milestone for "complex-region handling policy".

3. **Phase 2 Tier A/B/C PP.H4 ≥ 0.8 is hardcoded.** Phase 1 sensitivity-sweeps the coloc prior p12 ∈ {1e-6, 1e-5, 1e-4}; Phase 2 should similarly sweep the PP.H4 threshold (0.5, 0.7, 0.8, 0.9) and report tier assignments as a function of threshold. **Action:** add a threshold-sweep slice under the Phase 2 milestone. Reviewers will ask.

4. **Phase 3 cross-ancestry MR has winner's-curse / weak-instrument risk in AFR/EAS.** Small AFR instrument sets inflate MR bias; plan mentions Lawson 2020 but no concrete mitigation (MR-RAPS, IVW with correction, trans-ancestry MR of Lyon et al. 2023). Doesn't discuss whether to use ancestry-specific or trans-ancestry instruments. **Action:** add an explicit weak-instrument mitigation slice.

5. **Phase 6 polygenic selection test is the highest-risk phase scientifically.** Berg/Coop had to be corrected post-Sohail 2019; even the corrected version has known issues with UK-Biobank-trained effect sizes. The plan cites the right references but should **pre-specify in the plan itself** that a null polygenic selection result does not invalidate the single-locus selection signatures (iHS/PBS/SDS) — otherwise one null result dissolves the whole "selection" narrative. **Action:** add a "pre-specified fallback framing" slice.

6. **Phase 8 PRS evaluation only covers discrimination (R², AUC).** Missing: **calibration** (Hosmer-Lemeshow, calibration slope) and **clinical utility** (NRI, decision-curve analysis). Standard for a translational PRS deliverable at NG level. **Action:** calibration + clinical-utility slices under the Phase 8 milestone.

7. **No negative-control genes/pathways.** Standard rigor move: show that HLA (immune), pigmentation, or eye-color pathways don't show spurious colocalization/enrichment. Adds modest work and pre-empts an obvious reviewer criticism. **Action:** add a negative-control slice under the Phase 2 and Phase 5 milestones.

8. **Equity framing is inconsistent between §2 and §3.9.** §2 ("equitable polygenic risk prediction") promises equity wins; §3.9 honestly notes pathway-restricted PRS may trade accuracy for equity. The manuscript abstract/framing should reconcile this — **sell it as a quantified equity-vs-accuracy trade-off**, not an equity win. **Action:** capture this as a decision in `.gsd/DECISIONS.md` so the manuscript milestone inherits the framing.

9. **No CI strategy for reproducibility.** §7 commits to Snakemake + containers but nothing enforces that the pipeline still runs after changes. **Action:** nightly smoke-test Snakemake invocation on a toy 3-locus subset; treat as a slice under the Phase 0 infrastructure milestone.

10. **Target journal list is missing Nature Metabolism and Cell Metabolism.** For a cardiometabolic paper with a PRS deliverable, Nat Metab is a natural fit between AJHG and Nat Genet. **Action:** expand target list in the writing milestone.

11. **Scope creep is the biggest risk the plan doesn't address.** 10 phases × 50 loci × 4 ancestries × 5 traits is enormous. No phase is marked as stretch — all are presented as must-have. **Action:** apply the tier structure below.

### 5.3 Recommended priority tiering (apply when decomposing milestones)

| Tier | Revision_Plan phases | Rationale |
|---|---|---|
| **T1 — Spine (must-ship)** | Phase −1 (data access, new), 0, 1, 2, 5, 9 | Core methodological upgrade + replication. Without all six, no honest submission at any target journal. |
| **T2 — Nat Genet lift** | 3 (MR), 4 (matched-N cross-ancestry), 8 (PRS) | These move the paper from AJHG-level to Nat Genet-level. Add only after T1 is running cleanly. |
| **T3 — Stretch / cover-letter hooks** | 6 (selection), 7 (single-cell), 10 (deep learning) | High-novelty but high-risk. Add only if T1+T2 results support a Nat Genet pitch. Phase 6 in particular may produce a null polygenic selection result. |

**Two explicit decision checkpoints** the roadmap should encode:
- **End of T1 (after replication milestone):** decide whether to proceed to T2 or submit to AJHG with T1 only.
- **End of T2 (after PRS milestone):** decide whether to add T3 for a Nat Genet cover-letter hook, or submit to Nat Metab / Cell Metab / AJHG without T3.

These are not just review moments — they are real branch points where the paper's target journal can change. The roadmap should make them visible as gates.

## 6. Suggested GSD phase sequence (starting point, adapt during `/gsd-new-project`)

This is a starting frame, not a commitment. Adjust during `/gsd-new-project` (where the ROADMAP.md is created) if the actual decomposition should be different. Phase numbers below are the GSD-roadmap phase numbers (what you pass to `/gsd-plan-phase <N>`), not the Revision_Plan phase numbers. The mapping is called out in each item.

- **Phase 1 — Directory reorganization + .planning scaffolding.** Convert to git repo, clean obsolete artifacts (`.DS_Store`, `~$*`, `AJHG_files*`), pin conda envs into `env/*.yml`, create top-level structure (`src/phase*/`, `workflow/` for Snakemake, `data/`, `results/`, `manuscript/`, `docs/`). Capture this briefing's constraints into the project decision log. *(Goal A of §3.)*
- **Phase 2 — Data access applications** *(Revision_Plan Phase −1, newly added).* Kick off all DUAs in parallel: UKB-PPP, deCODE pQTL, FinnGen R12, MVP, All of Us v8, BBJ, Pan-UKBB. Blocks nothing else; unblocks Phases 5, 7, 9, 10 downstream.
- **Phase 3 — Infrastructure + data fixes + expanded GWAS catalog** *(Revision_Plan Phase 0).* Execute §10 quick wins, audit DIAMANTE dedup, characterize CAAPA lift-over loss, add AFR/EAS/Hispanic GWAS, stand up Snakemake DAG, draft OSF pre-registration.
- **Phase 4 — coloc.susie spine** *(Revision_Plan Phase 1).* Replaces coloc.abf as primary analysis. Includes the complex-region handling policy from §5.2 gap #2.
- **Phase 5 — 3-way QTL coloc (highest-leverage change)** *(Revision_Plan Phase 2).* Blocked on partial Phase 2. Includes the PP.H4 threshold sensitivity sweep from §5.2 gap #3 and negative-control pathway check from gap #7.
- **Phase 6 — Pathway + partitioned heritability** *(Revision_Plan Phase 5).* MAGMA + LDSC + HESS. Parallel with Phases 7/8.
- **Phase 7 — Replication in independent cohorts** *(Revision_Plan Phase 9).* FinnGen, GBMI, MVP, All of Us, BBJ. Blocked on Phases 2, 4, 5.
- **🚦 Checkpoint: end of T1.** Decide: proceed to T2, or submit AJHG with T1 only?
- **Phase 8 — Mendelian randomization** *(Revision_Plan Phase 3).* Includes weak-instrument mitigation from §5.2 gap #4.
- **Phase 9 — Cross-ancestry matched-N** *(Revision_Plan Phase 4).*
- **Phase 10 — Cross-ancestry PRS (PRS-CSx)** *(Revision_Plan Phase 8).* Includes calibration + clinical-utility slices from §5.2 gap #6.
- **🚦 Checkpoint: end of T2.** Decide: add T3, or submit to Nat Metab / Cell Metab / AJHG?
- **Phase 11 — Selection scans** *(Revision_Plan Phase 6).* Scientifically highest-risk. Includes pre-specified null-result fallback framing from §5.2 gap #5.
- **Phase 12 — Single-cell + EpiMap + ABC** *(Revision_Plan Phase 7).*
- **Phase 13 — Deep-learning variant effect + public MPRA overlap** *(Revision_Plan Phase 10).*
- **Phase 14 — Writing, bioRxiv, journal submission.** Target cover letter per journal (NG primary, AJHG/Nat Metab/Cell Genomics/Genome Medicine fallbacks).

## 7. What not to do

- **Don't treat `.planning/` as throwaway scratch.** GSD v1 stores real project state there — PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md, CONTEXT.md (per phase), RESEARCH.md, PLAN.md. These become the methods section and reviewer-response document at submission time.
- **Don't skip `/gsd-discuss-phase` before `/gsd-plan-phase`.** The discuss step locks implementation decisions into CONTEXT.md so the research and planning agents don't re-ask them. Skipping it produces vaguer plans.
- **Don't auto-install web/app skills.** Decline React/Next/Vite/TypeScript skill suggestions during `/gsd-new-project`. The relevant stack is R (coloc, susieR, TwoSampleMR), Python (LDSC, PRS-CSx, selscan, Enformer/Borzoi), bash, Snakemake, conda. A genomics/research-analysis profile is the correct fit.
- **Don't compress timelines.** Revision_Plan.md §5 explicitly says timeline is not binding. Rigor first.
- **Don't treat data access as a gate.** It runs in parallel from Day 1.
- **Don't use `--auto` for the first few phases.** Phases 1–5 involve real methodological decisions that should go through interactive `/gsd-discuss-phase` rather than autonomous mode.

## 8. Entry point for this session (GSD v1 workflow)

The correct kick-off sequence, in order:

1. **`/gsd-new-project`** — creates `.planning/PROJECT.md`, `config.json`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`. When it asks for the project description or vision, respond: **"Read `GSD_BRIEFING.md` in this directory first, then read `Revision_Plan.md` in this directory. Those two files are the vision. Use the phase sequence proposed in GSD_BRIEFING.md §6 as the starting structure for ROADMAP.md, applying the T1/T2/T3 tier gates from §5.3 as decision checkpoints between phases. The 11 gaps in §5.2 are requirements that must appear in REQUIREMENTS.md."**
2. **`/gsd-discuss-phase 1`** — discuss the directory reorganization phase. Lock decisions about git layout, conda env pinning, Snakemake structure, what to archive vs delete.
3. **`/gsd-plan-phase 1`** — produce the PLAN.md for directory reorganization.
4. **`/gsd-execute-phase 1`** — execute it. After this phase completes, `coloc_analysis/` should be a git repo with the new layout.
5. **Repeat the discuss → research → plan → execute cycle for Phases 2, 3, 4, …** Phase 2 (data access applications) starts in parallel with Phase 3 and doesn't block Phase 3 execution.

**Alternative fast path:** `/gsd-plan-phase 1 --prd Revision_Plan.md` passes the revision plan directly as a PRD to the planner agent, skipping the discuss step. Acceptable for Phase 1 (directory reorg, low methodological stakes) but **not recommended for Phases 4+** (analytical phases where interactive discussion matters).

**Note on current session:** GSD v1 was just installed into `~/.claude/skills/` while this Claude Code session was running. Newly installed skills may not be visible in the slash-command menu until you **restart Claude Code** (close and reopen the session). After restart, typing `/gsd-` should surface the 68 GSD skills including `/gsd-new-project` and `/gsd-plan-phase`.
