# Phase M3: AoU AFR LD panel build — Context

**Gathered:** 2026-04-27
**Status:** Ready for planning
**Slug:** m3-aou-afr-ld-panel-build
**Discuss round:** R1 (post M2 closeout 2026-04-27; STATE.md `m2_closed -> m3_planning`; AoU workspace registration document drafted but not yet pasted into portal)

<domain>
## Phase Boundary

Build per-region linkage-disequilibrium reference matrices for both AFR and EUR ancestries inside the All of Us Researcher Workbench (Terra-hosted Google Cloud / Dataproc / Hail) from controlled-tier WGS, export the summary-only `.npz` artifacts to NCSU GPFS per AoU data-egress policy, convert to `.rds`, integrate into the Snakemake fine-mapping DAG, run the 4-check validation protocol per [`AOU-LD-PIPELINE.md`](../../amendments/AOU-LD-PIPELINE.md) §9 on a 10-region dev subset, and ship the validation memo + AoU egress audit log.

**In scope:** AoU workspace finalization (paste the registration doc, file DUS / RPS / billing / P&P draft, get egress classification in writing); Hail/Dataproc cohort definition pipeline (`mt_afr_qc.mt`, `mt_eur_qc.mt`); per-region LD matrix computation via `hl.ld_matrix` for all 161 regions × 2 ancestries (AFR_aou + EUR_aou) = 322 cells; 10-region dev subset with the 4-check validation memo + Carter signoff before scale-up; full production fire of the remaining 312 cells; per-chromosome egress requests; NCSU-side `.npz → .rds` conversion + Snakemake `ld_panel:` selector wiring; validation memo OSF posting to the existing osf.io/az52u amendment record; AoU egress audit log under `.planning/amendments/aou-egress-audit-log.md`.

**Out of scope (belongs to M4 / M2-supplementary / later):**
- Two-stage coloc (ABF + SuSiE-RSS) on union regions and HyPrColoc 5-trait shared-architecture (M4)
- PolyFun baselineLF2 functional priors (M4)
- Per-tissue Borzoi/Enformer scoring on Tier A credible sets (M5)
- M2 AFR re-firing of clumping (M2-POST-M3-01), LDSC matrix slice (-02), and AFR mtCOJO (-03) **with the new AoU AFR panel** — these become a separate **M2-supplementary** phase consuming the M3 outputs (D-M3-05)
- UKB EUR LD augmentation — DUA-gated, deferred (D-M3-01.1)
- AoU AFR ld-score re-derivation for proper AFR-AFR LDSC (M2-POST-M3-05; deferred to M2-supplementary)
- TRANS mtCOJO 1000G AFR sensitivity check (M2-POST-M3-04; deferred to M2-supplementary)
- AFR-SBP M1 derivation under DEC-2026-04-24-02 — separate AoU compute path with its own egress-audit entry (handled in M1-supplementary, not M3)
- GWAS Catalog v_lock_M5 refresh (M2-POST-M3-06; deferred to M5)

**Gating in:** M2 union region BED (161 regions); AoU workspace creation + DUS approval + RPS approved + billing attached + P&P draft filed + egress classification in writing.
**Gating out:** M3 outputs gate (a) M4 (`results/finemap/`, `results/coloc/` consume `data/processed/ld_reference/{AFR_aou,EUR_aou}/{region_id}.rds`) and (b) the M2-supplementary phase (D-M3-05).
</domain>

<inputs>
## Inputs Available from M2 (and earlier phases)

**Region union BED (M2 deliverable per D-M2-09):** `results/regions/union_region_list.bed` — 161 regions, 8 columns (`chr`, `start`, `end`, `region_id`, `score=.`, `strand=.`, `provenance_json`, optional `lead_token`). `provenance_json` encodes contributing source ∈ {`clump`, `mtag`, `cpassoc`} per stratum. **Schema gap:** AOU-LD-PIPELINE.md §6 expects 7 flat columns including `ancestry`, `source_trait`, `lead_variant` per row; the M2 BED encodes ancestry/source_trait inside the JSON. M3 Wave 0 includes a region-manifest reformatter task (`build_ld_region_manifest.py`) that emits `config/ld_regions.tsv` in the AOU §6 schema, with 161 × 2 = 322 rows (one per region × ancestry).

**Pre-pivot LD scaffolding (NCSU side):** `src/snakemake/rules/ld_reference.smk` (lines 274-334 + 349-448) holds the existing `build_ld_rds_1kg_eur`, `download_ukbb_ld_tiles`, `build_hgdp_1kg_ld` rules. Snakemake convention pinned: rule directory `src/snakemake/rules/`, output convention `os.path.join(LD_REF_DIR, "{ancestry}", "{region}.rds")`, conda envs at `envs/` with absolute-path workaround `LD_BUILD_ENV = str(Path(workflow.basedir) / "envs" / "ld_build.yml")`.

**Existing 1000G EUR LD on disk (Track A real-LD substrate; reusable as Check 2 comparator):** `data/processed/ld_reference/EUR/*.rds` (11 curated EUR regions from Track A Stage 2). The 10-region dev subset will pick 3 of these as the AoU-EUR vs 1000G-EUR Check 2 comparator regions.

**1000G EUR Phase 3 plinkfiles (existing):** `data/reference/ldsc/1000G_EUR_Phase3_plink/chr{1..22}.{bed,bim,fam}` (LDSC-staged 2026-04-14). Used by the existing `build_ld_rds_1kg_eur` rule; NOT used by M3's AoU pipeline directly.

**Pipeline config:** `config/pipeline.yaml` (lines 180-196) has a `finemap:` block with `ld_reference_dir: "data/processed/ld_reference"`. **No `ld_panel:` block exists.** M3 Wave 0 adds the `ld_panel:` selector per AOU-LD-PIPELINE.md §8.4.

**`.gitignore`:** `data/raw/*`, `data/processed/*`, `data/external/*` are already gitignored at line 74-76. **Spec §10.2 explicit entries are missing** for `data/interim/aou_ld_exports/`, `data/processed/ld_reference/AFR_aou/`, `data/processed/ld_reference/EUR_aou/`. M3 Wave 0 task adds these explicitly for clarity (even though the wildcard would catch them).

**Conda envs:** `envs/ld_build.yml` is the closest — `python=3.11`, `numpy`, `scipy`, `pandas`, `boto3`, `plink2`, `bcftools`. **No Hail / pyspark / google-cloud-storage env exists.** M3 Wave 0 builds `envs/m3-aou-dev.yml` (local mirror per AOU-LD-PIPELINE.md §2 P5) and `envs/m3-r-ld.yml` (R + reticulate for `.npz → .rds` conversion).

**AoU workspace registration (drafted, not posted):** `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md` — 518-line paste-ready Markdown document, 13 portal-section headers, 46 inline `[src: ...]` citations to upstream amendments. Track A is explicitly OUT of this workspace.

**Test toy fixtures:** `tests/toy_3locus/data/ld_ref/*.rds` — currently identity-placeholder for FTO_16q12, SH2B3_12q24, TCF7L2_10q25 (EUR). M3 Wave 5 extends with AFR identity-placeholder fixtures (no AoU data in CI).

**Decisions inheriting into M3:**
- DEC-2026-04-22-04 — AoU controlled-tier WGS as AFR LD source; 1000G AFR (n=661) is fallback only (M3's primary architectural premise)
- DEC-2026-04-24-01 — GRCh37 canonical analytic plane; AoU emits GRCh38; M3 conversion step (`ld_npz_to_rds.R`) liftovers variant IDs to b37 via the existing UCSC chain at `data/external/liftover/hg38ToHg19.over.chain.gz`
- DEC-2026-04-24-02 — AFR-SBP M1 fallback established the AoU compute path scaffolding; M3 reuses the workspace-registration discipline (separate `.planning/amendments/aou-egress-audit-log.md` entries per derivation)
- D-M2-02 — M2 used 1000G AFR provisional; **M3 lands the supersede artifact for the AFR LD half**, but the AFR clumping/LDSC/mtCOJO re-fires move to a separate M2-supplementary phase per D-M3-05

**Open carry-forward gates (Carter human action):**
- AoU workspace creation in the portal (paste from `AOU-WORKBENCH-REGISTRATION.md`)
- AoU DUS approval, RPS approval, billing profile attached, P&P draft registered (AOU-LD-PIPELINE.md §2 P1-P7)
- AoU egress classification of variant×variant LD matrices as aggregate summary statistics in writing (AOU-LD-PIPELINE.md §12 Risk R1) — **HARD GATE** before any Dataproc spend
</inputs>

<decisions>
## Locked Decisions (M3 gray-area resolutions, 2026-04-27)

### D-M3-01: EUR parity panel built inside AoU Workbench (parallel to AFR), not on NCSU GPFS

**Decision:** Build the EUR parity LD panel inside the AoU Researcher Workbench using the same Hail BlockMatrix pipeline against `ancestry_pred == 'eur'` (target ~130-150k post-QC). Output goes to `gs://fc-secure-<workspace-id>/ld/EUR_aou/{region_id}.npz` and lands on GPFS at `data/processed/ld_reference/EUR_aou/{region_id}.rds`. Reconciles ROADMAP M3 wording ("rebuild EUR LD from 1000G + UKB for parity") by treating "1000G + UKB" as the **comparator** for AOU-LD-PIPELINE.md §9.2 Check 2 (entry-wise Pearson correlation of AoU EUR vs 1000G EUR with mean r ≥ 0.97 for MAF ≥ 0.05), not as the build source. The 1000G EUR Phase 3 plinkfiles already on disk at `data/reference/ldsc/1000G_EUR_Phase3_plink/` serve as the Check 2 comparator only.

**Alternatives considered:** (a) NCSU 1000G + UKB build (matches ROADMAP literal wording but writes a second pipeline with no code reuse with AoU half; UKB DUA timing is months, the actual critical path); (b) Defer EUR parity to M3-supplementary (smallest M3 footprint, but loses Check 2 validation substrate and loses cross-ancestry symmetry); (c) AoU EUR at dev-only 10 regions (smallest credit burn that still validates pipeline, but M4 EUR loses option to use AoU EUR as primary). Adopted (a) for code-reuse, methodological symmetry, and Check 2 utility. ROADMAP wording will be updated by M3 Wave 0 to reflect "AoU EUR with 1000G EUR Check 2 comparator" as the parity construct.

**How to apply:** AoU Workbench notebook `AOU-1` (cohort definition) emits two checkpointed MatrixTables: `mt_afr_qc.mt` and `mt_eur_qc.mt`. The same `compute_region_ld(region_row, mt_source)` driver runs against both. Region manifest `config/ld_regions.tsv` enumerates 161 × 2 = 322 (region × ancestry) cells. Per-chromosome export bundles are filed separately for AFR and EUR (44 export requests total).

### D-M3-01.1: UKB EUR augmentation deferred (out of M3 scope)

**Decision:** UKB does not enter M3. The AoU EUR cohort (~130-150k) is shipped as the standalone EUR parity panel for M3. UKB tile-access registration continues in parallel as background; if UKB EUR LD becomes available later, an M5 or M6 supplementary phase merges it (~150k AoU EUR + ~330k UKB EUR ≈ ~480k composite). UKB DUA timing (months, possibly 2026-Q3/Q4) is not a critical-path gate for M3 → M4.

**Alternatives considered:** (a) Stage UKB in parallel and merge if it lands (introduces M3 schedule uncertainty); (b) Hard-block M3 on UKB DUA (cleanest scientific endpoint, slowest — pushes M4 critical path months). Adopted standalone-AoU-EUR.

**How to apply:** ROADMAP M3 wording update (Wave 0) drops "+ UKB" from the parity description; UKB EUR augmentation is recorded as a `<deferred>` item with cross-reference to a future supplementary phase slot.

### D-M3-02: All 161 regions × both ancestries — 322 cells in production scope

**Decision:** M3 builds AFR_aou and EUR_aou per-region LD matrices for every region in `results/regions/union_region_list.bed` (161 regions). Production scope is 161 × 2 = 322 cells. Pros: M4 has both panels available genome-wide; all 8 M2-supersede obligations have inputs available; clean methodological symmetry; no late "we need EUR_aou here too" surprises. Cons: highest credit burn — mitigated by AOU-LD-PIPELINE.md §11 cost levers (preemptible secondary workers for ~60% low-density regions; staged launch caps exposure).

**Alternatives considered:** (a) AFR_aou × 161 + EUR_aou × 10 dev only (~1.5x credit; M4 EUR continues on 1000G EUR Phase3); (b) Priority subset (~50 regions × both, requires explicit priority-ranking Wave-0 task; risks orphaning the non-priority 111 regions); (c) Per-stratum split (AFR_aou × 161 + EUR_aou only for regions with AFR-stratum lead — ~40-60 regions; clever but introduces region-classification complication). Adopted full × full.

**How to apply:** Region manifest `config/ld_regions.tsv` enumerates 322 rows (one per region × ancestry). Snakemake region wildcard expansion fans out to 322 `compute_region_ld` invocations across the AoU-side driver. Per-region timing budget per AOU-LD-PIPELINE.md §11 (15-25 min typical region; 45-90 min HLA-adjacent stress) gives ~80-130 cluster-hours per ancestry, ~160-260 cluster-hours combined. With 8-12 concurrent Dataproc jobs at AoU's quota ceiling, ~3-5 day wall clock for production fire.

### D-M3-03: Production fire = single batch (Dev-10 → Production-322 single fire)

**Decision:** After the 10-region dev subset (D-M3-04) clears Checks 1-4 (AOU-LD-PIPELINE.md §9) and Carter signs the validation memo, fire all 322 production cells in one Snakemake/Dataproc batch. Parallelism comes from concurrent Dataproc jobs at AoU's quota ceiling, not from a phased schedule. One Carter checkpoint between dev and production; one egress-audit-log entry per ancestry × per-chromosome batch (44 entries total).

**Alternatives considered:** (a) Dev-10 → Priority-50 → Remaining-272 (extra Carter checkpoint; "priority" subset requires definition); (b) Dev-10 → Per-chromosome batches (22 fires; lots of human-action surface; net longer wall clock); (c) Dev-10 → AFR-first-then-EUR (doubles wall clock; M4 EUR delayed). Adopted single-fire after dev gate because (i) our 161-region count is small enough that the spec's 3000-region staging math collapses, (ii) the 4-check validation memo already de-risks systemic-bug surprises, (iii) AoU export per-chromosome bundling provides natural batch granularity for the egress audit anyway.

**How to apply:** Snakemake target `m3_dev_complete` is the dev gate (10-region subset, all 4 checks, validation memo committed, Carter signoff). Once `m3_dev_complete.flag` exists, Snakemake target `m3_prod_complete` fires the remaining 312 cells in one DAG. Per-chromosome export requests (44 total) are filed at the AoU portal in parallel as the Dataproc jobs complete; the per-chromosome bundling is enforced at the egress step, not at the compute step.

### D-M3-04: Dev region selection — spec default (3 EUR-comparable + 5 AFR-known + 2 HLA-stress)

**Decision:** The 10-region dev subset follows AOU-LD-PIPELINE.md §14 week 2-3 default exactly:
- **3 EUR regions** with existing Track A 1000G EUR LD `.rds` files for AOU-LD-PIPELINE.md §9.2 Check 2 (AoU EUR vs 1000G EUR entry-wise correlation comparator). Pick from the 11 curated EUR regions Track A produced. Suggested: SH2B3_12q24, TCF7L2_10q25_2, FTO_16q12_2 (or any 3 with strong real-LD signal in Track A).
- **5 AFR regions** with published GWAS lead variants for §9.1 Check 1 (known-locus LD pattern matches published AFR figures) and §9.3 Check 3 (SuSiE-RSS convergence on 16q12 BMI AFR). Suggested: FTO 16q12 (rs1558902), SORT1 1p13 (rs12740374) per spec, plus 3 more from the M2 union region list with AFR-stratum signal.
- **2 HLA-adjacent stress-test regions** for OOM and dense-region resilience, e.g., HLA 6p21, 8p23 inversion neighborhood.

The 4-check validation memo (§9.4 Check 4: AoU-AFR vs identity-placeholder A/B) consumes all 5 AFR-known + 2 HLA = 7 regions for the headline yield contrast.

**Alternatives considered:** (a) Track A 10 EUR autosomal regions only (max Track A comparability, but under-tests Checks 1, 3, and the HLA stress); (b) MTAG-novel intersection — first 10 by p-value (de-risks M4 directly but no comparator for Check 2; not necessarily HLA-stress-positive); (c) Hybrid: spec default + 1-2 MTAG-novel exemplars (12-region; small deviation from spec; modest extra dev compute). Adopted spec default for cleanest 4-check coverage.

**How to apply:** A Wave-0 task selects the 10-region dev subset deterministically: 3 EUR-Track-A-comparable picks from `data/processed/ld_reference/EUR/*.rds` (sorted by region size and LD-pattern complexity), 5 AFR-known picks from a curated list (FTO, SORT1, ABCG5/8, LDLR, APOE — all in M2 union region list), 2 HLA-stress picks from the M2 union region list filtered by `chr == 6 AND start_grch38 BETWEEN 28e6 AND 34e6` (HLA 6p21) plus `chr == 8 AND start_grch38 BETWEEN 7e6 AND 13e6` (8p23 inversion). The 10-region manifest is committed to `config/ld_regions_dev.tsv` and consumed by both the AoU-side dev fire and the NCSU-side validation harness.

### D-M3-05: M2 supersede triggering — separate M2-supplementary phase, not M3 close-out

**Decision:** M3 closes when: (a) AFR_aou + EUR_aou panels land at `data/processed/ld_reference/{AFR_aou,EUR_aou}/*.rds`, (b) the 4-check validation memo + Carter signoff are committed, (c) the AoU egress audit log lands at `.planning/amendments/aou-egress-audit-log.md`, and (d) the `ld_panel:` selector in `config/pipeline.yaml` is wired so M4 fine-mapping rules can target the new panels. The 3 high-priority M2-supersede obligations (M2-POST-M3-01 AFR clumping, M2-POST-M3-02 AFR LDSC matrix slice, M2-POST-M3-03 AFR mtCOJO) become a separate **M2-supplementary phase** (suggested slug: `m2-supp-aou-afr-rerun`) consuming M3 outputs. The 5 medium/low M2-supersede obligations (M2-POST-M3-04 through -08) fold into the same supplementary phase or remain on the durable queue per priority.

**Alternatives considered:** (a) M3 close-out fires the 3 high-priority re-runs (extends M3 scope; faster end-to-end, but if AFR clumping/LDSC reveals an issue the M3 verification fails and unblocking iteration is large); (b) M4 consumes the new panel directly with M2 obligations closing as "no-op pending need" (smallest M3 scope; risks needing supersede mid-M4 with iteration cost; leaves M2 in partially-superseded state on OSF amendment trail); (c) Hybrid — M3 fires LDSC-02 only at close-out; clumping-01 + mtCOJO-03 to supplementary (mixed-precision close-out audit). Adopted clean M3-supplementary boundary because: (i) M2-POST-M3-01 AFR clumping + M2-POST-M3-03 AFR mtCOJO depend on the actual AoU AFR PLINK bfile derivation, which is itself non-trivial (AOU-LD-PIPELINE.md §5.2 Path B — PLINK export of 60k samples × autosomes is hours of compute and PLINK1 bfile is size-inefficient); (ii) M2-POST-M3-02 LDSC matrix slice depends on AoU AFR ld-score derivation (M2-POST-M3-05) which is not a trivial swap; (iii) the supplementary phase produces its own SUMMARY.md + verification + closes specific obligation IDs against the durable queue — clean audit trail.

**How to apply:** M3 plan ends with a "Phase Close-out" wave that updates `.planning/m2_post_m3_rerun_queue.tsv` to reflect "M3 complete; M2-supplementary phase eligible to start" (no obligations marked closed yet — all 8 stay open until the supplementary phase fires). M2-supplementary phase is added to ROADMAP.md as a successor to M3 (slug `m2-supp-aou-afr-rerun`); its CONTEXT will be drafted via `/gsd-discuss-phase m2-supp-aou-afr-rerun` after M3 closes.

### D-M3-06: Local dev mirror — build per AOU-LD-PIPELINE.md §2 P5 (locked to spec default)

**Decision:** M3 Wave 0 builds `envs/m3-aou-dev.yml` (Python 3.11 + `hail==0.2.x` + `pyspark` + `google-cloud-storage` + `pandas` + `numpy`) and a tiny synthetic MatrixTable test fixture so the cohort-definition + per-region-LD pipeline can be developed against a toy MT before any AoU Dataproc spend. Iteration cycles run locally; first cluster fire is the production dev-10 panel.

**Why:** Spec recommendation; matches the existing M1/M2 conda-env discipline (`envs/m1-download.yml`, `envs/ld_build.yml`); de-risks the dev-10 fire by catching most pipeline bugs locally; saves AoU credits on dev iteration.

**How to apply:** Wave 0 task `build_aou_dev_env` materializes `envs/m3-aou-dev.yml` and a synthetic MT fixture under `tests/m3/fixtures/synthetic_mt/`. The Hail driver code (`src/python/aou_ld_panel.py`) is testable locally against the synthetic MT before any cluster fire. Tests live at `tests/m3/test_aou_ld_panel_local.py`.

### D-M3-07: Ancestry inclusion logic — PCA-primary with self-report sensitivity check (locked to spec default)

**Decision:** Per AOU-LD-PIPELINE.md §3.1: primary cohort definition is `ancestry_pred == 'afr'` (or `'eur'` for the EUR panel) with kinship pruning at KING coefficient ≥ 0.0442 (third-degree, conservative) and standard sample QC (call rate ≥ 0.98, heterozygosity ±3 SD). Sensitivity check per §3.2: compute LD on the PCA-based AFR cohort, then re-fit LD on the subset that **also** self-reports Black/African American at the 10-region dev subset. If correlation > 0.995 at all 10 lead loci, proceed with PCA-only for the production fire. Document the sensitivity-check yield in the validation memo.

**Why:** Spec recommendation; preserves admixed African-American participants who are AFR-predominant by genetic ancestry but self-identify differently; defensible community-considerations position per the registration document's §10 framing; the sensitivity check provides a transparent audit trail.

**How to apply:** AoU Workbench notebook `AOU-1` cohort-definition rule produces two cohort tables: `cohort_afr_pca.tsv` (primary, n ≈ 60-95k) and `cohort_afr_pca_and_selfid.tsv` (sensitivity, n ≈ 50-80k subset). The 10-region dev fire emits LD matrices for both cohorts; the validation memo's §9 includes a "sensitivity-check correlation" table.

### D-M3-08: Validation-memo external review — OSF deposit as substitute (locked to spec default)

**Decision:** Per AOU-LD-PIPELINE.md §15 Q8 and the project's solo-author constraint per `PROJECT.md`: M3 ships the 4-check validation memo as `.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION.md` with a public OSF posting to the existing osf.io/az52u amendment record (the same record used for M1's amendment per DEC-2026-04-25-02). The OSF posting carries the full memo + tabular check outputs + reproducibility manifest; this serves as the external-reviewer substitute.

**Why:** Spec recommendation; matches the project's pre-registration discipline; the existing osf.io/az52u amendment record is the canonical M3 amendment trail destination.

**How to apply:** M3 Wave 5 (close-out) emits `m3-VALIDATION.md` (the 4-check memo) + a paste-ready PDF for OSF. Carter manually posts to osf.io/az52u as a supplementary file (same convention as M1's posting at osf.io/az52u/files/k8w7n). The egress audit log entry references the OSF DOI.

### D-M3-09: Open Issue O1 ruling — region-width acceptance

**Decision:** Resolution 1 — accept wide regions; Path A.3 for > 10 Mb regions. (Carter ruling 2026-04-28 at Wave 0 Task 5 close; quick task 260428-stv.)

**Why:** Methodological rigor and reviewer-defensibility outweigh compute convenience. (1) M2's union region list is the canonical fine-mapping unit across M2 → M3 → M4 → M5; Resolution 2's tile re-derivation would force an asymmetry between milestones forever and require a translation table (tile ↔ M2 region) at every cross-milestone reasoning step. (2) Resolution 2's "split at lowest LD-density valleys" is an algorithmic heuristic with no biological basis; every cut point becomes a defensible-question for reviewers, whereas accepting M2 region boundaries inherits the defensibility already published with M2. (3) Resolution 2 explicitly drops cross-tile LD at fine-mapping; for the 8 xlarge regions (chr2 50.5 Mb, chr3 50.5 Mb, chr4 101.7 Mb, chr6 102.5 Mb MHC-spanning, chr7 58.0 Mb, chr9 73.1 Mb, chr12 88.8 Mb, chr15 65.1 Mb), credible variants near tile boundaries would lose true LD partners on the other side — a real statistical loss for a fine-mapping LD panel. (4) Path A.3 BlockMatrix-write produces the same LD matrix as `to_numpy()` — it is engineering plumbing (already coded in `src/python/aou_ld_panel.py`), not a statistical compromise. (5) Novelty-class definitions (REQ-NOVELTY-CLASS-2 AFR-specific) stay region-anchored under R1, traceable directly back to M2; under R2 they would require re-derivation and tile-anchored re-mapping. (6) Carter standing preference (memory `feedback_rigor_over_speed.md`, 2026-04-28; project-level `CLAUDE.md` "Timeline is not a binding constraint. Rigor and impact matter more than speed."): in any gray-area trade-off between rigor and time/compute saving, choose rigor. R2's only advantage was wall-clock (~3 wall days at AoU quota), which is not a binding constraint here.

**How to apply:** Wave 1+ honor the per-region radius from `config/ld_regions.tsv` (already emitted at Wave 0 Task 1, commit 4cf6295) where `radius_bp = min((end - start) + 500_000, 50_000_000)` per region. Wave 4 production fire honors three Path-A branches in `src/python/aou_ld_panel.py` per `region_class` column: A.1 (`small`, ≤ 5 Mb, n=45 regions, `to_numpy()` densify on driver, 0.5 cluster-h each); A.2 (`medium`, 5–25 Mb, n=80, `sparsify` + `to_numpy()`, 1.5 cluster-h each); A.3 (`large` 25–50 Mb n=28 + `xlarge` > 50 Mb n=8, BlockMatrix write-to-bucket, never densify on driver — 8 cluster-h each for `large`, 24 cluster-h each for `xlarge`). Total cost: 558.5 cluster-hours per ancestry; ~1,117 cluster-hours AFR + EUR; 5–7 wall days at AoU's 8–12 concurrent Dataproc quota (per `m3-region-class-projection.tsv`). **No tile-splitter task is added to Wave 0;** Wave 0 closes after this ruling commits. The 36 large + xlarge regions remain region-anchored throughout M3 + M4 + M5; novelty calls and downstream coloc/replication code consume `m2_region_*` IDs unchanged. The 102 Mb chr4 (m2_region_00120) and 102.5 Mb chr6 MHC-spanning (m2_region_00145) cells are the largest single-job loads; they fire as A.3 streaming-writes and should not OOM the driver.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents (researcher, planner, executor) MUST read these before planning or implementing.**

### M3 architectural source-of-truth
- `.planning/amendments/AOU-LD-PIPELINE.md` — full M3 pipeline spec (~570 lines): cohort definition (§3), variant QC (§4), Hail BlockMatrix pipeline (§5.1), PLINK fallback (§5.2), parallelism strategy (§5.3), region list format (§6), export protocol (§7), local integration (§8), 4-check validation protocol (§9), storage naming + .gitignore (§10), compute cost (§11), risks (§12), AoU publication policy (§13), timeline (§14), open questions (§15). **Every M3 plan task ties back to a section here.**
- `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md` §3 M3, §5 — pivot-era authoritative scope (AoU controlled-tier WGS as AFR LD source; ~150× sample-size upgrade over 1000G AFR n=661).

### Project decisions inherited
- `.planning/DECISIONS.md` 2026-04-22 entry **DEC-2026-04-22-04** — AoU controlled-tier WGS as AFR LD source with egress-aware summary-only pipeline (M3's primary architectural premise).
- `.planning/DECISIONS.md` 2026-04-24 entry **DEC-2026-04-24-01** — GRCh37 canonical analytic plane (M3 conversion step liftovers AoU's GRCh38 to b37).
- `.planning/DECISIONS.md` 2026-04-24 entry **DEC-2026-04-24-02** — AoU compute path scaffolding established at M1 for AFR-SBP fallback (M3 reuses workspace registration discipline; separate egress-audit entry).
- `.planning/DECISIONS.md` 2026-04-25 entry **DEC-2026-04-25-02** — OSF amendment posting form (M3 validation memo posts as a supplementary file on osf.io/az52u, not a new amendment record on osf.io/pvb5j).

### M2 hand-off artifacts
- `results/regions/union_region_list.bed` — 161 regions; M3 region manifest input. Reformatted by Wave 0 to `config/ld_regions.tsv` (322 rows, region × ancestry).
- `.planning/m2_post_m3_rerun_queue.tsv` — 8 M2-supersede obligations queued at M2 closeout. M3 close-out updates this file with status notes; the actual re-fires happen in the M2-supplementary phase per D-M3-05.
- `.planning/phases/m2-ldsc-mtag-cpassoc-discovery/m2-deferred-items.md` — full M3-deferred trait/cell list with resolution paths.

### Requirements
- `.planning/REQUIREMENTS.md` **REQ-AOU-LD-EGRESS** — AoU P&P + RPS + egress classification gates; summary-only export; local landing under `data/processed/ld_reference/AFR_aou/`.
- `.planning/REQUIREMENTS.md` **REQ-AOU-LD-VALIDATION** — 4-check protocol on 10-region dev subset before scale-up admission to production DAGs.
- `.planning/REQUIREMENTS.md` **REQ-PUBLIC-DATA-ONLY**, **REQ-SNAKEMAKE-CI**, **REQ-PATH-PARAMETERIZATION** — cross-milestone constraints carrying into M3.

### AoU workspace registration draft
- `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md` — 518-line paste-ready document (13 portal-section headers, 46 inline `[src: ...]` citations). Carter pastes section-by-section into the AoU portal at workspace-creation time. Track A is explicitly OMITTED from this workspace.

### Pre-pivot scaffolding to extend
- `src/snakemake/rules/ld_reference.smk` — existing LD-reference rules (`build_ld_rds_1kg_eur`, `download_ukbb_ld_tiles`); M3 adds `build_ld_rds_aou_afr` and `build_ld_rds_aou_eur` parallel to these.
- `src/snakemake/rules/finemap.smk` — fine-mapping rule that resolves the LD path; M3 adds `ld_panel:` resolver.
- `config/pipeline.yaml` lines 180-196 (`finemap:` block) — M3 adds `ld_panel: { EUR: 1kg or aou, AFR: aou, aou_fallback_to_1kg: false }` per AOU-LD-PIPELINE.md §8.4.
- `envs/ld_build.yml` — convention reference for new `envs/m3-aou-dev.yml` and `envs/m3-r-ld.yml`.

### Existing pipeline pattern references
- `src/snakemake/rules/m1_download.smk` lines 46-62 — flag-driven download rule pattern (M3 reuses for AoU export ingest).
- `src/python/build_region_union.py` — M2 region-union builder (M3's Wave 0 reformatter is a sibling at `src/python/build_ld_region_manifest.py`).

### Test fixtures
- `tests/toy_3locus/data/ld_ref/*.rds` — current EUR identity-placeholder LD; M3 Wave 5 extends with AFR identity-placeholder fixtures (no AoU data in CI).
</canonical_refs>

<code_context>
## Existing Code Insights (from scout 2026-04-27)

### Reusable Assets
- **`src/snakemake/rules/ld_reference.smk` (lines 274-334, 349-448):** existing `build_ld_rds_1kg_eur` and `download_ukbb_ld_tiles` rules. M3 adds two new rules `build_ld_rds_aou_afr` and `build_ld_rds_aou_eur` following identical I/O conventions (input: `data/interim/aou_ld_exports/{ANCESTRY}_aou/{region_id}.npz`; output: `data/processed/ld_reference/{ANCESTRY}_aou/{region_id}.rds`). One R script (`src/scripts/ld_npz_to_rds.R` per AOU-LD-PIPELINE.md §8.2) backs both.
- **`src/python/build_region_union.py`:** M2's region-union pattern. M3's Wave 0 reformatter (`src/python/build_ld_region_manifest.py`) reads `results/regions/union_region_list.bed`, expands the JSON provenance column, and emits `config/ld_regions.tsv` in the AOU-LD-PIPELINE.md §6 schema (322 rows = 161 regions × 2 ancestries).
- **`config/pipeline.yaml` lines 180-196 `finemap:` block:** existing config layout. M3 adds `ld_panel:` block per spec §8.4.
- **`envs/ld_build.yml`:** convention reference for M3's two new env yamls.
- **`src/snakemake/rules/m1_download.smk` lines 46-62:** flag-driven download rule pattern (`output: flag=os.path.join(_RAW_ROOT, ".download_complete.{tag}")`); M3's AoU `.npz` ingest rule reuses this convention.
- **`src/snakemake/rules/finemap.smk` line 56:** the rule that consumes per-region LD `.rds` and currently expects a fixed `{ancestry}/{region}.rds` path. M3 wraps the path resolution in a helper that reads the new `ld_panel:` config block.
- **`tools/hess/`, `tools/ldsc/`, `tools/magma_v1.10/`:** existing pre-pivot tools tree. M3 Workbench-side code does NOT live here (it lives inside the AoU workspace bucket); the NCSU-side helpers go to `src/python/aou_ld_*.py`.

### Established Patterns
- **Snakemake rule directory:** `src/snakemake/rules/`. M3's new rules: `m3_ingest_aou_ld.smk`, `m3_convert_npz_rds.smk`, `m3_validation.smk`. Snakefile entry point updated at top-level `Snakefile`.
- **Conda env reference:** absolute-path workaround `LD_BUILD_ENV = str(Path(workflow.basedir) / "envs" / "ld_build.yml")` at top of rule files. M3 follows same convention.
- **Config-driven path resolution:** `config["paths"]["ld_reference"]` per `pipeline.yaml`. M3 extends but doesn't override.
- **Atomic-commit convention per phase wave:** matches M1/M2 — one commit per task per wave with `(${padded_phase}-${wave_id}-${task_id})` token in the commit subject.
- **Validation memo pattern:** M2 used `m2-VALIDATION.md` (9.3 KB structured table); M3 emits `m3-VALIDATION.md` covering the AOU-LD-PIPELINE.md §9 four checks.
- **Python tooling location:** `src/python/` for orchestration scripts; `src/scripts/` for one-shot R post-processing helpers (per AOU-LD-PIPELINE.md §8.2 convention).

### Integration Points
- **M4 fine-mapping consumer:** `src/snakemake/rules/finemap.smk` resolves LD `.rds` path through the new `ld_panel:` config selector. M3's plan must verify M4-side path resolver works against both EUR_1kg and EUR_aou (and AFR_1kg fallback chain).
- **M5 Borzoi consumer:** Tier A credible sets from M4 feed into M5's Borzoi scoring. M3 doesn't touch this, but the `ld_panel:` selector design must not break the M4 → M5 hand-off.
- **OSF amendment trail:** M3 validation memo posts to osf.io/az52u (per DEC-2026-04-25-02 form); this is also where M1's amendment lives. The trail integrity check happens via `.planning/amendments/aou-egress-audit-log.md` cross-reference.
- **Egress audit log:** new file `.planning/amendments/aou-egress-audit-log.md` (referenced by both M1's AFR-SBP derivation per DEC-2026-04-24-02 and M3's LD panel build). M3's plan adds this file in Wave 0; M1-supplementary AFR-SBP entry will append later.
</code_context>

<artifacts>
## Expected Deliverable Artifacts (per ROADMAP M3 + AOU-LD-PIPELINE.md §§5-9)

| # | Path | Source | Class |
|---|------|--------|-------|
| 1 | `config/ld_regions.tsv` | Wave 0 reformatter `build_ld_region_manifest.py` (322 rows from M2 union BED × 2 ancestries) | input manifest |
| 2 | `config/ld_regions_dev.tsv` | Wave 0 dev-subset selector (10 rows: 3 EUR-Track-A + 5 AFR-known + 2 HLA-stress) | input manifest |
| 3 | `config/pipeline.yaml` `ld_panel:` block | Wave 0 config update | config |
| 4 | `envs/m3-aou-dev.yml` | Wave 0 conda env (hail + pyspark + google-cloud-storage) | env |
| 5 | `envs/m3-r-ld.yml` | Wave 0 conda env (R + reticulate + Matrix) | env |
| 6 | `src/python/aou_ld_panel.py` | Hail driver (cohort-define + per-region LD compute); runs inside AoU Workbench | code |
| 7 | `src/python/build_ld_region_manifest.py` | Wave 0 region-manifest reformatter | code |
| 8 | `src/scripts/ld_npz_to_rds.R` | Wave 3 `.npz → .rds` converter per AOU-LD-PIPELINE.md §8.2 | code |
| 9 | `src/snakemake/rules/m3_ingest_aou_ld.smk` | Wave 3 NCSU-side `.npz` ingest rules | rules |
| 10 | `src/snakemake/rules/m3_convert_npz_rds.smk` | Wave 3 conversion rules | rules |
| 11 | `src/snakemake/rules/m3_validation.smk` | Wave 4 4-check validation rules | rules |
| 12 | `data/interim/aou_ld_exports/AFR_aou/*.npz` | AoU export landing (gitignored; ephemeral, deleted after `.rds` conversion per §10.3) | intermediate |
| 13 | `data/interim/aou_ld_exports/EUR_aou/*.npz` | AoU export landing (gitignored; ephemeral) | intermediate |
| 14 | `data/processed/ld_reference/AFR_aou/{region_id}.rds` | 161 files | production |
| 15 | `data/processed/ld_reference/EUR_aou/{region_id}.rds` | 161 files | production |
| 16 | `.planning/phases/m3-aou-afr-ld-panel-build/validation/` | 4-check outputs (heatmaps, correlation tables, SuSiE convergence logs, A/B yield contrast) | governance |
| 17 | `.planning/phases/m3-aou-afr-ld-panel-build/m3-VALIDATION.md` | Wave 4 validation memo (4-check outcomes + Carter signoff) | governance |
| 18 | `.planning/amendments/aou-egress-audit-log.md` | Wave 5 egress audit log (44 per-chromosome export entries + classification ruling) | OSF |
| 19 | `.planning/m2_post_m3_rerun_queue.tsv` | Wave 5 status update (M3 complete; supplementary phase eligible) | hand-off |
| 20 | `.planning/phases/m3-aou-afr-ld-panel-build/m3-PHASE-CLOSEOUT.md` | Wave 5 verifier output | governance |
| 21 | `.planning/amendments/sha256_manifest_m3_frozen.tsv` | Wave 5 SHA-256 freeze of all AFR_aou + EUR_aou `.rds` files | OSF |
| 22 | `tests/m3/fixtures/synthetic_mt/` + `tests/m3/test_aou_ld_panel_local.py` | Wave 0 local dev test fixtures | test |
| 23 | `tests/toy_3locus/data/ld_ref/*.AFR.rds` (identity placeholder) | Wave 4 CI smoke extension | test |

## Test artifacts

| Path | Purpose |
|------|---------|
| `tests/m3/test_aou_ld_panel_local.py` | Hail driver unit tests against synthetic MT (no AoU access) |
| `tests/m3/test_build_ld_region_manifest.py` | M2 BED → config/ld_regions.tsv schema correctness |
| `tests/m3/test_ld_npz_to_rds.py` | `.npz → .rds` round-trip + symmetry recovery + dimnames preservation |
| `tests/m3/test_validation_check_1_known_locus.py` | Check 1 LD-pattern visualization invariants |
| `tests/m3/test_validation_check_2_aou_eur_vs_1kg.py` | Check 2 entry-wise correlation threshold logic |
| `tests/m3/test_validation_check_3_susie_convergence.py` | Check 3 SuSiE-RSS convergence + CS size gates |
| `tests/m3/test_validation_check_4_identity_ab.py` | Check 4 A/B yield-contrast tabulation |
| `tests/m3/test_ld_panel_resolver.py` | `config/pipeline.yaml` `ld_panel:` selector resolution against the M4 fine-mapping rule |
</artifacts>

<requirements_traceability>
## Requirement-ID Coverage

| REQ ID | M3 deliverable that closes it | Notes |
|--------|------------------------------|-------|
| REQ-AOU-LD-EGRESS | AoU P&P registration filed; RPS approved; egress classification in writing; per-region `.npz` files + AF metadata land on GPFS; conversion to `.rds` per §8.2 | Wave 0 + Wave 1 + Wave 5 |
| REQ-AOU-LD-VALIDATION | `m3-VALIDATION.md` 4-check memo on 10-region dev subset; `validation/` outputs committed before scale-up | Wave 4 |
| REQ-PUBLIC-DATA-ONLY | All M3 work uses AoU controlled-tier WGS (DUA-covered); no individual-level data leaves the workspace; OSF posting confirms public-summary-only artifacts | Carry-forward; closed by spec compliance |
| REQ-SNAKEMAKE-CI | M3 Snakemake rules (`m3_*.smk`) registered in main pipeline; toy_3locus extended with AFR identity-placeholder | Wave 4 + Wave 5 |
| REQ-PATH-PARAMETERIZATION | All AoU-side and NCSU-side path resolution goes through `config/pipeline.yaml` `ld_panel:` block | Wave 0 |
</requirements_traceability>

<deferred_ideas>
## Deferred Ideas (out of M3 scope; capture for backlog)

- **UKB EUR LD augmentation** (D-M3-01.1) — DUA-pending; merge into EUR_aou as composite ~480k EUR if UKB lands by M5/M6. Tracked as a future supplementary phase slot in ROADMAP backlog.
- **AoU-supervised supplementary EUR fine-mapping** — if Check 2 (AoU EUR vs 1000G EUR) reveals a material discrepancy, a supplementary phase may swap the M4 EUR fine-mapping panel from 1000G EUR to AoU EUR. Decision deferred to Check 2 outcome.
- **AoU AFR ld-score derivation for proper AFR-AFR LDSC** (M2-POST-M3-05) — derives AFR ld-scores from the AoU AFR WGS panel for the M2 LDSC matrix re-fire. Belongs in M2-supplementary phase consuming M3 output.
- **TRANS mtCOJO 1000G AFR sensitivity check** (M2-POST-M3-04) — D-M2-Q3 sensitivity column. Belongs in M2-supplementary phase.
- **AFR LDSC matrix re-fire under AoU AFR ld-scores** (M2-POST-M3-02) — high-priority M2-supersede obligation; belongs in M2-supplementary phase per D-M3-05.
- **AFR PLINK clumping re-fire under AoU AFR LD** (M2-POST-M3-01) — high-priority M2-supersede obligation; belongs in M2-supplementary phase per D-M3-05.
- **AFR mtCOJO re-fire under AoU AFR LD** (M2-POST-M3-03) — high-priority M2-supersede obligation; belongs in M2-supplementary phase per D-M3-05.
- **GWAS Catalog v_lock_M5 refresh + delta-diff** (M2-POST-M3-06) — deferred to M5 cross-reference date; not M3 scope.
- **MTAG `--fdr` LSF re-fire** (M2-POST-M3-07) — Wave 2 M2 D6 LSF long-queue re-fire; belongs in M2-supplementary phase or its own LSF batch.
- **mtCOJO production sensitivity LSF re-fire for 13 eligible targets** (M2-POST-M3-08) — Wave 4 M2 D4 LSF long-queue re-fire; belongs in M2-supplementary phase.
- **AoU v8 re-run policy** — if AoU v8 lands during M3 development, AOU-LD-PIPELINE.md §3.3 commits to a re-run on v8 before export. Not a backlog item per se, but a watch-item for the M3 Carter checkpoint.
- **Hispanic-ancestry (HIS) LD panel** — AoU has ~30k HIS cohort; building HIS LD would close the cross-ancestry coverage further but is not in the Amendment §3 9-trait × 2-ancestry inventory. Deferred.
- **AoU CAD AFR / eGFR AFR / SBP AFR sumstats** — referenced in `m2-deferred-items.md` as M3+ resolution paths for traits without an AFR-specific stratum in M2. Belongs in a separate M1-supplementary phase or is folded into M5 deferred-catalog closure.
</deferred_ideas>

<assumptions>
## Assumptions Carter has validated

1. **AoU v7 controlled-tier access is active.** Per `.planning/quick/260426-aow-aou-workbench-registration-track-b-m3/AOU-WORKBENCH-REGISTRATION.md` and DEC-2026-04-22-04, Carter has eRA Commons → AoU Researcher Workbench link.
2. **AoU Researcher Workbench supports Dataproc + Hail.** AOU-LD-PIPELINE.md §5 cites Hail v0.2.x as the standard image; AoU's published documentation confirms this.
3. **AoU egress for variant×variant LD matrices is feasible.** R1 risk acknowledged in AOU-LD-PIPELINE.md §12; the registration document framing argues these are "aggregate summary statistics" with all cells computed from n ≥ 60k participants (trivially clearing the ≥20-person suppression floor). Hard gate per Carter human action: written classification before any Dataproc spend.
4. **AoU credit balance covers ~160-260 cluster-hours.** Per AOU-LD-PIPELINE.md §11, with cost levers; staged single-fire after dev-10 caps initial exposure.
5. **GRCh37 ↔ GRCh38 liftover in conversion step is acceptable for LD matrices.** AoU emits GRCh38; the existing `data/external/liftover/hg38ToHg19.over.chain.gz` (DEC-2026-04-24-01 chain, SHA-256 verified) handles variant ID liftover. **Open**: whether per-region BED start/end coordinates need liftover before AoU `filter_intervals` call (suggested: query AoU in GRCh38 native, liftover variant IDs at conversion step). Resolution: Wave 0 plan task.
6. **The 4-check validation gate is the canonical promotion gate.** Per AOU-LD-PIPELINE.md §9: pass-before-scale-up; Carter signoff on the validation memo before any production fire. No "we'll fix it in production" override.
7. **Single-fire production after dev gate is acceptable risk.** D-M3-03 — given our 161-region count is small relative to the spec's 3000-region target, single-fire is the simplest plan; the 4-check dev gate de-risks systemic-bug surprises.
8. **PCA-primary ancestry (D-M3-07) is defensible to reviewers.** §10 of registration document positions this explicitly with admixed-population community-considerations framing; sensitivity-check protocol provides audit trail.
9. **M2 region union remains the canonical fine-mapping unit across milestones.** D-M3-09 — Resolution 1 ruled at Wave 0 close (2026-04-28; quick task 260428-stv): the 36 large + xlarge regions fire as Path A.3 BlockMatrix streaming-writes rather than being re-tiled to ≤ 10 Mb. Methodological consistency M2 → M3 → M4 → M5 preserved; novelty calls (REQ-NOVELTY-CLASS-2) remain region-anchored; no tile ↔ region translation table needed at any cross-milestone reasoning step. Cost: 558.5 cluster-h per ancestry (~1,117 ch AFR + EUR; 5–7 wall days at AoU's 8–12 concurrent Dataproc quota) — accepted under Carter's rigor-over-time-saving preference (CLAUDE.md "Timeline is not a binding constraint" + memory `feedback_rigor_over_speed.md`).
</assumptions>

<open_questions>
## Open Questions for Research / Planning Agents (NOT for Carter)

These are technical-implementation choices the research agent should answer when it scouts:

1. **Region BED coordinate system.** M2 union BED uses GRCh37 coordinates per DEC-2026-04-24-01. AoU MT is GRCh38 native. Research agent: confirm whether the Wave 0 reformatter should liftover region start/end coordinates to GRCh38 BEFORE feeding `config/ld_regions.tsv` to the AoU driver, OR whether the AoU-side driver should liftover on read. Default recommendation: liftover at reformat step (one-shot), keep AoU-side driver pure.
2. **Hail `hl.ld_matrix` `radius` parameter for our ~1-2 Mb regions.** AOU-LD-PIPELINE.md §5.1 sets `radius=2_500_000`; research agent: confirm this is appropriate for the 161 union regions (some may be wider per M2 D-M2-09 ±1 Mb default; check `union_region_list.bed` start/end span distribution).
3. **AoU bucket vs Workbench Jupyter export semantics.** AOU-LD-PIPELINE.md §7.1 notes "Or programmatic: `aou_workbench_client` export endpoint — needs verification this is available for non-notebook artifacts". Research agent: confirm the export pathway for `.npz` files in workspace bucket vs notebook outputs. Affects how the egress audit log entries are structured.
4. **Per-chromosome export bundle size.** AOU-LD-PIPELINE.md §7.2 recommends "lower-triangular float32 `.npz` with MAF ≥ 0.01, one export request per chromosome". For 161 regions concentrated on ~22 chromosomes, the per-chromosome bundle size varies widely. Research agent: estimate per-chromosome export bundle size against AoU's per-batch export size limits.
5. **Hail BlockMatrix `block_size` parameter for OOM avoidance on HLA + 8p23.** AOU-LD-PIPELINE.md §12 R12 risk row mentions Hail BlockMatrix OOM on dense regions. Research agent: investigate `block_size` tuning + `to_numpy()` driver-memory limits; recommend a fallback to writing BlockMatrix directly to bucket and densify only at export.
6. **Local synthetic MT fixture for `envs/m3-aou-dev.yml` testing.** D-M3-06 calls for a tiny synthetic MT. Research agent: minimum viable schema (~100 samples × ~1000 variants × 2 chromosomes) that still exercises `hl.sample_qc`, `hl.variant_qc`, `hl.split_multi_hts`, `hl.ld_matrix` paths.
7. **`config/pipeline.yaml` `ld_panel:` resolver implementation.** AOU-LD-PIPELINE.md §8.4 sketches the YAML structure; the actual Snakemake helper that consults this is undefined. Research agent: design the `resolve_ld_path(region_id, ancestry, config)` helper consumed by `finemap.smk`.
8. **AoU `ancestry_pred` field name verification.** AOU-LD-PIPELINE.md §3.1 flags this as "needs verification against current AoU documentation" (`ancestry_pred` vs `pca_ancestry_category`). Research agent: confirm against AoU v7 CDR documentation and pin the field name in the Hail driver.
9. **AoU `RELATED_SAMPLES_HT_PATH` env var.** §5.1 line 142 uses `os.environ["RELATED_SAMPLES_HT_PATH"]` with NEEDS VERIFICATION; research agent: confirm AoU v7 workspace env var name + path conventions.
10. **MAF lower bound for export vs internal — finalize threshold.** Spec §7.2 Recommendation: MAF ≥ 0.01 for export, MAF ≥ 0.005 internal. Research agent: confirm the variant-count drop is acceptable (~30% drop in AFR per spec) and that the larger MAF doesn't drop too many M2-novel SNPs that we want LD for.
11. **MTAG-novel exemplar dev region candidates.** D-M3-04 spec default reserves 5 AFR-known slots; research agent: identify candidate regions with both AFR-stratum lead from M2 + published AFR GWAS at ≥1 trait so the dev-10 fixture exercises both Check 1 (LD pattern) and Check 3 (SuSiE-RSS convergence).
12. **Per-chromosome egress audit log structure.** Wave 5 emits `.planning/amendments/aou-egress-audit-log.md`. Research agent: design the log entry schema (timestamp, chromosome, ancestry, file count, total compressed size, AoU export request ID, classification ruling reference, SHA-256s).
</open_questions>

<next_step>
## Next Step

Run `/gsd-plan-phase m3-aou-afr-ld-panel-build` to:
1. Spawn `gsd-phase-researcher` agent to investigate the 12 open_questions above + scout the AoU `ancestry_pred` / `RELATED_SAMPLES_HT_PATH` field names + verify Hail v0.2.x API for `hl.ld_matrix`, `hl.sample_qc`, `hl.variant_qc`, `hl.split_multi_hts` against current docs (use Context7 if available)
2. Spawn `gsd-planner` agent to break M3 into atomic plans + waves consistent with the locked decisions in this CONTEXT.md (suggested wave structure: Wave 0 — workspace + envs + region manifest; Wave 1 — AoU cohort definition pipeline; Wave 2 — 10-region dev fire + Check 1+2+3+4; Wave 3 — NCSU `.npz → .rds` ingest + Snakemake `ld_panel:` selector wiring; Wave 4 — production fire 322 cells + per-chromosome egress; Wave 5 — close-out artifacts + OSF posting + supplementary-phase setup)
3. Spawn `gsd-plan-checker` agent for goal-backward review

**Hard gates before any Dataproc spend (Carter human action):**
- [ ] AoU workspace created in portal (paste from `AOU-WORKBENCH-REGISTRATION.md`)
- [ ] DUS approved
- [ ] RPS approved
- [ ] Billing profile attached
- [ ] P&P draft registration filed
- [ ] AoU egress classification of variant×variant LD matrices in writing (Risk R1)

The OSF amendment §9.1 hard gate was RELEASED 2026-04-25 (commit d55c1d1) — M3 inherits the released gate.
</next_step>
