# Roadmap: coloc_analysis

> **Pivot note** (2026-04-22): This program was reframed from a 50-region
> candidate-locus study into a two-track original research program covering
> genome-wide joint-signal discovery across 9 traits × 2 ancestries (Track B,
> milestones M0–M6) plus a pre-specified short-form methods validation paper
> leveraging the existing real-LD audit (Track A finalization). Pivot charter:
> `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`.
> The pre-pivot Phase 00–11 content is preserved below under "Pre-pivot
> spine"; its artifacts are reusable per Amendment §8 and form the Track A
> data plus the Track B candidate-locus validation subset.
>
> **2026-04-29 reconciliation note** (quick task `260429-l1e`): This file
> was reconciled to Amendment §12 spec on 2026-04-29 against the
> authoritative source at
> `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`,
> with **zero substantive drift** identified from the post-pivot rewrite.
> All three §12 ROADMAP requirements satisfied: (1) **T1 retirement
> language** lives in the "Pre-pivot spine" appendix header at line 470
> (Phases 0–11 framed as the pre-pivot spine, with the post-2026-04-22
> active program living in the M0–M6 sections above); (2) **full M0–M6
> milestone table** inserted per Amendment §3 at lines 33-276 (M0 pivot
> scaffolding through M6 manuscript + replication + submission);
> (3) **phase-history appendix preserved verbatim** per the
> "interpretable git-history" rationale stated at lines 478-479 — this is
> why the pre-pivot `[T1]`/`[T2]`/`[T3]` tier markers stay verbatim, as
> historical record rather than active scope. Beyond the §12 minimum, this
> file additionally documents the **Track A short-form sequence**
> (`Track-A-finalization` at lines 280-380, current short-form draft path;
> `Track-A-R2-SH2B3` at lines ~381-468, R2 SH2B3 reanalysis being planned
> in `.planning/phases/ta-sh2b3-*`). Pair this reconciliation with the
> 2026-04-28 `260428-pj4` pass on PROJECT.md + REQUIREMENTS.md (commits
> `70db503`, `56fd413`, `927b5eb`); together these close the M0
> documentation alignment for all four `.planning/` files Amendment §12
> names.

## Overview

Two-track original research program (adopted 2026-04-22 per Amendment §3).

Track B executes genome-wide joint-signal discovery across 9 traits × up to
2 ancestries under milestones **M0 → M1 → M2 → M3 → M4 → M5 → M6**. M2
(LDSC + MTAG + CPASSOC) is gated on (a) M1 harmonization completion and
(b) OSF amendment posting per Amendment §9. M3 (AoU AFR LD build) is
partially parallel with M2. M4 (scalable coloc + fine-mapping) is gated on
M3 LD panels + M2 region list. M5 (variant→gene prioritization + novelty
cross-reference) is gated on M4 Tier A. M6 (manuscript + replication +
submission) is gated on M5.

Track A (short-form methods paper on the real-LD audit of 50 curated
cardiometabolic regions) is scientifically independent of Track B. It ships
on pre-pivot spine outputs (Phases 0 / 1 / 2 / 5 / 9, reusable per
Amendment §8) and targets Genome Medicine primary / AJHG short report
fallback / Bioinformatics Applications Note final fallback in 2026-05 /
2026-06 per Amendment §11.

## Current milestone sequence (Track B M0–M6)

### M0: Pivot scaffolding
**Slug**: m0-pivot-scaffolding
**Goal**: Adopt pivot charter; rewrite .planning/ scaffold per Amendment §12;
lock 9-trait × 2-ancestry inventory; lock phenotype definitions; author
ID-VS-REF-LD-STRATEGY.md, SUMSTATS-UPGRADE.tsv/.md, AOU-LD-PIPELINE.md,
TRACK-A-FROZEN-NUMBERS.md companion docs (Amendment §3 M0).
**Requirements**: REQ-AMEND-SEC12, REQ-PUBLIC-DATA-ONLY, REQ-SNAKEMAKE-CI
(carried forward)
**Dependencies**: None (planning only)
**Success Criteria**:
  1. Amendment committed under `.planning/amendments/`
  2. PROJECT / ROADMAP / REQUIREMENTS / DECISIONS rewritten to M0–M6 framing
  3. 9-trait × 2-ancestry inventory locked per Amendment §4
  4. Track A and Track B companion documents committed
  5. STATE.md refreshed to M0 in-flight position
**Deliverable Artifacts**:
  - `.planning/amendments/PROJECT-AMENDMENT-2026-04-22-genome-wide-reframe.md`
  - Updated `.planning/PROJECT.md` / `ROADMAP.md` / `REQUIREMENTS.md` / `DECISIONS.md`
  - `ID-VS-REF-LD-STRATEGY.md`, `TRACK-A-FROZEN-NUMBERS.md`, `SUMSTATS-UPGRADE.{md,tsv}`, `AOU-LD-PIPELINE.md`, `SUMSTATS-MANUAL-FETCH.md`
**Gating condition for M1**: M0 scaffolding commits land (this quick-task
plan + subsequent STATE.md refresh session).
**Status**: in flight — amendment + companions complete; doc rewrites are
this quick-task plan.

### M1: Sumstats upgrade and harmonization
**Slug**: m1-sumstats-upgrade-and-harmonization
**Goal**: Download Yengo 2022 (or Loh 2022 — pending source decision per
PROJECT.md open human-action item b), DIAMANTE 2022, GIGASTROKE 2022, Giri
2019 MVP, GBMI asthma 2022, Aragam 2022 CAD, GLGC 2021 lipids, CKDGen 2019
eGFR, MAGIC 2021 HbA1c per `SUMSTATS-UPGRADE.tsv`. Harmonize to GRCh37 (per
DEC-2026-04-24-01 override of Amendment §3 M1 GRCh38 wording; two b38-native
sources — Loh 2022 BMI + GBMI 2022 asthma — lifted via pyliftover), filter
MAF ≥ 0.005, INFO ≥ 0.8, per-ancestry QC. Build HM3-munged `.sumstats.gz` for
LDSC/MTAG AND full-coverage `.tsv.bgz + .parquet` dual-emit for coloc /
fine-mapping / CPASSOC (D-09 / D-15). Build 45×45 LDSC bivariate-intercept
matrix via 44 star-pattern `ldsc.py --rg` calls + Python reducer (NOT
`--rg-cross` which does not exist in vendored abdenlab fork). Verify
ancestries and sample-overlap flags per trait (Amendment §3 M1, §4, §5).
**Requirements**: REQ-TRAIT-INVENTORY, REQ-SNAKEMAKE-CI,
REQ-PUBLIC-DATA-ONLY, REQ-PATH-PARAMETERIZATION
**Dependencies**: Download lead times (some DUAs in place; MVP phs001672
needs verification per PROJECT.md open human-action item c)
**Success Criteria**:
  1. Harmonized sumstats parquet per trait × ancestry in `data/processed/sumstats/`
  2. Per-trait QC report with ancestry and sample-overlap flags locked
  3. LDSC-munged files for all 9 traits × ancestry strata listed in Amendment §4
  4. SHA-256 checksums recorded for every source file (frozen for OSF amendment text)
  5. Trait inventory YAML (`config/trait_inventory.yaml`) enumerates 9 traits
**Deliverable Artifacts**:
  - Harmonized sumstats parquet per trait × ancestry
  - Per-trait QC report (one HTML per trait)
  - LDSC-munged `.sumstats.gz` per trait × ancestry
  - `config/trait_inventory.yaml` with locked phenotype definitions
  - SHA-256 manifest for source sumstats files
**Gating condition for M2**: M1 harmonization verified (all success criteria)
AND OSF amendment posted at osf.io/pvb5j per Amendment §9 (Carter web-UI
action per PROJECT.md open human-action item a). Both conditions must hold.
**Plans**: 6 plans

Plans:
- [x] m1-00-preflight-and-environment-PLAN.md — Wave 0: conda envs + pytest scaffolding + UCSC chain + LDSC LD staging + MAGIC FTP / Giri 2019 / LDSC benchmark probes + D-02/D-03/D-06 disposition + DEC-2026-04-24 decisions entry
- [x] m1-01-portal-fetches-and-aragam-route-PLAN.md — Wave 1: extend bin/download_sumstats_v2.sh for 17 portal rows + DIAMANTE cookie handling + Aragam ZIP unpack per D-03 + deterministic raw SHA-256 manifest freeze (OSF paste target)
- [x] m1-02a-harmonizers-continuous-traits-PLAN.md — Wave 2: harmonize_yengo + harmonize_glgc + harmonize_wuttke + harmonize_magic (BMI 4 cells + lipids 15 cells + eGFR 3 cells + HbA1c 6 cells = 28 leaf jobs) with Loh 2022 b38->b37 liftover, sumstats_utils.build_rsid_to_chrpos helper, m1_raw_glob.resolve_raw_for + DEFERRED_SENTINEL universal guard, and Snakemake DAG dry-run loaded clean
- [x] m1-02b-harmonizers-case-control-traits-PLAN.md — Wave 2: harmonize_diamante + harmonize_gigastroke + harmonize_aragam + extend harmonize_gbmi with --liftover-chain + verify_evangelou_sbp rename; freeze secondary harmonized SHA-256 manifest
- [x] m1-03-munge-and-ldsc-intercept-matrix-PLAN.md — Wave 3: munge 45 files to HM3 .sumstats.gz + 44 star-pattern ldsc.py --rg calls (NOT --rg-cross; RESEARCH Pitfall #1) + reducer -> 45x45 bivariate-intercept matrix at data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04.tsv
- [x] m1-04-qc-reports-inventory-manifest-PLAN.md — Wave 4: Quarto per-trait + cross-trait QC + config/trait_inventory.yaml build + Dimension-8 verify_m1_artifacts + OSF paste-prep + Carter OSF web-UI submission (M2 HARD GATE per Amendment §9.1)

**Status**: M1 closeout COMPLETE 2026-04-25; all 6 plans landed; phase verifier overall verdict PASS; OSF amendment paste-ready (Carter web-UI action remains as M2 hard gate per Amendment §9.1).

### M2: LDSC + MTAG + CPASSOC discovery
**Slug**: m2-ldsc-mtag-cpassoc-discovery
**Goal**: LDSC pairwise rg across all 9 traits × 2 ancestries; MTAG
(Turley 2018) with `--overlap` LDSC-intercept correction for UKB / MVP
cohort overlap; CPASSOC (Zhu 2015) orthogonal SHom / SHet joint-signal
test; `max_FDR` filter on MTAG; PLINK clump (p=5e-8, r²<0.01, 1Mb) per
trait × ancestry. Union of clumped regions + MTAG-novel + CPASSOC-novel
= discovery region list (~1,500–3,000 regions). **Novelty deliverable
Class 1**: joint-signal novel loci where MTAG or CPASSOC reaches
p < 5e-8 and no contributing single trait does, intersected with GWAS
Catalog v_lock for prior-art exclusion (Amendment §3 M2, §6, §7.1).
**Requirements**: REQ-MTAG-OVERLAP, REQ-CPASSOC-ORTHOGONAL,
REQ-NOVELTY-CLASS-1, REQ-OSF-PREREG, REQ-SNAKEMAKE-CI
**Dependencies**: M1 complete; OSF amendment posted BEFORE any MTAG /
CPASSOC run (Amendment §9)
**Success Criteria**:
  1. `rg_matrix.tsv` with LDSC pairwise rg + intercept block for all 9 × 2 pairs
  2. MTAG per-trait outputs with `max_FDR` column per Turley 2018
  3. CPASSOC per-locus SHom / SHet outputs
  4. Genome-wide union region BED (~1,500–3,000 regions)
  5. `joint_signal_novel.tsv` with MTAG ∩ CPASSOC high-confidence subset
  6. mtCOJO sensitivity table on top-N MTAG-novel loci
**Deliverable Artifacts**:
  - `results/ldsc/rg_matrix.tsv`
  - `results/mtag/` per-trait output tables
  - `results/cpassoc/` per-locus SHom/SHet tables
  - `results/regions/union_region_list.bed`
  - `results/novelty/joint_signal_novel.tsv` (Class 1)
**Gating condition for M3**: M2 region list frozen; per-region AoU LD
priority ordering handed to M3 Dataproc pipeline.
**Plans**: 6 plans

Plans:
- [x] m2-00-preflight-and-environment-PLAN.md — Wave 0: 13 pytest stubs + 6 conda envs (m2-mtag/cpassoc/clumping/mtcojo/regions/novelty) + MTAG vendoring at tools/mtag/ + 1000G AFR PLINK bfile build (Pitfall 3 BLOCKING) + GWAS Catalog v_lock_M2 snapshot + cpassoc.py SHom/SHet + m2_stratum_keys.py with _MIN_PER_STRATUM=3 (D-M2-Q6) + Carter sign-off checkpoint **COMPLETE 2026-04-26 (commits 740d8fc..99c7602; SUMMARY 3056622)**
- [x] m2-01-ldsc-matrix-refire-PLAN.md — Wave 1: archive M1 12x12 matrix + loosen m1_trait_keys defensive bound to 20-50 + refire m1_munge_all + m1_ldsc_rg_all_stars + m1_ldsc_rg_reduce against expanded ~26-trait inventory (D-M2-01) + OSF mirror (D-M2-Q2 EUR LD-scores cross-ancestry)
- [x] m2-02-mtag-3-strata-PLAN.md — Wave 2: build_mtag_residcov_slice.py (D-M2-10 corrected --residcov_path; bare-numeric K×K + sidecar trait_order.json) + m2_mtag.smk (residcov_slice + mtag_run + mtag_maxfdr_filter rules) + 3 strata production fire EUR/AFR/TRANS (D-M2-03) with --p_sig 5e-8 (D-M2-07) + post-hoc max_FDR<0.05 filter (D-M2-Q1)
- [x] m2-03-cpassoc-3-strata-PLAN.md — Wave 3: run_cpassoc.py orchestrator (Q7 PSD-preserving R slice via Wave 2 sidecar trait_order; D-M2-04) + m2_cpassoc.smk per-stratum + 3 strata production fire (chi-square p-values via scipy.stats.chi2.sf)
- [x] m2-04-clumping-mtcojo-regions-PLAN.md — Wave 4: m2_clumping.smk PLINK 1.9 --clump per (trait × ancestry × chr) at p1=5e-8/r²<0.01/kb=1000 (D-M2-09; Pitfall 5) using 1000G EUR/AFR (D-M2-02) + select_mtcojo_eligible_targets.py (gcov_int>0.1 D-M2-08 + D-M2-Q5) + m2_mtcojo.smk per (stratum, target_trait) (TRANS uses 1000G EUR primary D-M2-Q3) + build_region_union.py strict bedtools default merge (Q6 + Pitfall 9) emitting results/regions/union_region_list.bed with provenance JSON
- [ ] m2-05-class1-novelty-and-closeout-PLAN.md — Wave 5: call_class1_novelty.py applying OSF §7.1 Class 1 operational definition against v_lock_M2 (REQ-NOVELTY-CLASS-1) → results/novelty/joint_signal_novel.tsv with confidence_tier high/medium + .planning/m2_post_m3_rerun_queue.tsv (D-M2-02 supersede + Pitfall 11) + tests/toy_3locus/m2_smoke_targets.smk (REQ-SNAKEMAKE-CI extension) + verify_m2_artifacts.py Python-only verifier 9 dimensions (D-M2-Q4) + sha256_manifest_m2_frozen.tsv (Pattern E + DEC-2026-04-25-02 OSF follow-up) + Carter sign-off checkpoint advancing STATE.md to M2-complete

**Status**: m2-00 Wave 0 COMPLETE 2026-04-26 (nyquist_compliant: true; CR-checker WR-5 four-item attestation cleared); 1/6 plans complete; Wave 1 (m2-01-ldsc-matrix-refire) cleared to start.

### M3: AoU AFR LD panel build
**Slug**: m3-aou-afr-ld-panel-build
**Goal**: Inside the All of Us Researcher Workbench (Terra), build
per-region LD matrices per ancestry from controlled-tier WGS (~60–95k
AFR post-QC) per `AOU-LD-PIPELINE.md`. Export summary-only (LD matrix +
allele-frequency metadata) per AoU data-egress policy; verify AoU
classification of aggregate LD matrices as summary statistics (AoU R1
risk). Parallel: build EUR LD parity panel inside the AoU Workbench
against ancestry_pred=='eur' (D-M3-01); 1000G EUR Phase 3 plinkfiles
serve as the Check 2 entry-wise correlation comparator only. UKB EUR
augmentation deferred per D-M3-01.1 — UKB DUA timing not on the M3 to
M4 critical path.
**Requirements**: REQ-AOU-LD-EGRESS, REQ-AOU-LD-VALIDATION,
REQ-PUBLIC-DATA-ONLY, REQ-SNAKEMAKE-CI, REQ-PATH-PARAMETERIZATION
**Dependencies**: Region list from M2; AoU Workbench access
(controlled-tier confirmed for Carter); prerequisites P1–P7 in
`AOU-LD-PIPELINE.md` §2
**Success Criteria**:
  1. Per-region AoU AFR LD `.rds` files on GPFS under `data/processed/ld_reference/AFR_aou/`
  2. Per-region EUR LD parity panel built inside AoU against ancestry_pred=='eur' (D-M3-01)
  3. 10-region validation protocol passed per AOU-LD-PIPELINE.md §9 (4 checks)
  4. AoU data-egress audit log committed
  5. AoU P&P draft registration filed before scale-up compute
**Deliverable Artifacts**:
  - `data/processed/ld_reference/AFR_aou/*.rds` (per-region AFR LD)
  - `data/processed/ld_reference/EUR_aou/*.rds` (per-region EUR parity panel built inside AoU)
  - `.planning/phases/m3-aou-afr-ld-panel-build/validation/` (4-check memo)
  - `.planning/amendments/aou-egress-audit-log.md`
**Gating condition for M4**: Validation memo approved by Carter; per-region
LD files on GPFS; EUR parity panel available.
**Plans**: 10 plans (m3-00 through m3-05 + m3-02b/m3-02c/m3-02d/m3-02e Wave-2 re-scope; 10 waves)

**Plan list**:
- [x] m3-00-W0-foundations-PLAN.md — Wave 0: Region manifest reformatter (322 rows; per-region radius per RESEARCH Q2 structural finding) + dev-subset selector (D-M3-04 + Q11 overlap design) + ld_panel: resolver helper + config block (Q7) + envs/m3-aou-dev.yml + envs/m3-r-ld.yml + Hail driver with corrected ordering (split_multi_hts BEFORE variant_qc) + synthetic MT fixture (Q6) + 4 pytest scaffolds + egress audit log seed (Q12) + ROADMAP wording fix (D-M3-01) + .gitignore + Carter ruling on Open Issue O1 logged as D-M3-09
- [x] m3-01-W1-aou-cohort-and-hard-gates-PLAN.md — Wave 1: Carter 6-gate AoU portal action stack (P1 workspace + P2 DUS + P3 RPS + P4 billing + P6 P&P draft + R1 egress classification ruling — HARD GATE) + AUX path live verification + AOU-1 cohort definition notebook emitting 3 checkpointed MTs (mt_afr_qc.mt + mt_afr_pca_selfid.mt + mt_eur_qc.mt per D-M3-07 + D-M3-01)
- [~] m3-02-W2-dev-fire-and-validation-PLAN.md — Wave 2: AOU-2 dev fire on 10-region subset + 13 .npz egress + AOU-4 4-check validation harness (Checks 1+2+3+4 per RESEARCH Validation Architecture) + 5 pytest scaffolds + Carter signoff on m3-VALIDATION-MEMO.md + touch m3_dev_complete.flag (D-M3-03 dev to production gate). **STATUS 2026-05-21:** Tasks 1+2 DONE atomically (e3c29e7 AOU-2 design-delta cells m3-W2-T1; 6962607 RED + 001d8b1 GREEN AOU-4 Q2 signed-r contract m3-W2-T2); 23/23 pytest pass. Task 3 (Carter human-verify checkpoint) AWAITING: resume AoU env + fire AOU-2 + AOU-4 + write 9-section ≥100-line m3-VALIDATION-MEMO.md + touch m3_dev_complete.flag + commit with (m3-W2-T3) token. SUMMARY at m3-02-W2-dev-fire-and-validation-SUMMARY.md.
- [x] m3-02b-W2-rescope-split-stitch-code-PLAN.md — Wave 0 (re-scope; autonomous NCSU code) — **DONE 2026-06-19** (commits `a17a47a`/`0e3ec43`/`908de71`; SUMMARY landed). SPLIT the xlarge regions at manifest-build time into __sub{k:02d} **overlapping-window** rows (--max-subregion-span-mb default 10 + --split-classes xlarge + --subregion-buffer-mb; half-open cores tile the parent + core±buffer compute windows + parent_region_id/subregion_index/n_subregions/core+window_grch38/buffer_bp provenance + split_status projection) + dev tuple-resolve with capped __sub expansion + NEW stitch_subregions_to_rds.R (**BANDED, NOT block-diagonal** per m3-REVIEWS HIGH#1 — cross-core pairs within buffer_bp RETAINED at global (i,j), beyond zeroed; sparse dgCMatrix; allele-aware (CHR,POS,REF,ALT) ordering; core-ownership de-dup; emits obj$R + obj$variants for the REAL run_susie_rss.R loader) + ld_npz_to_rds.R whole-region payload reconciled + AF metadata in .npz/.rds + A6 real-loader verify (load_ld_matrix -> susie_rss) + sparse-parent benchmark (no whole-parent dense) + AOU-2 Q-RS2 executor cell (cores=2/24g/10g/24g) + 26 named test families (NO skip on the R families in the M3 env). Supersedes the dev-fire compute step of m3-02 (killed as intractable). **FLAG for m3-02c:** buffer_bp default = 50 Mb region radius makes the window span the whole parent → the --subregion-buffer-mb 10 (Pan-UKBB) lever is effectively mandatory; the probe must resolve the AFR/EUR LD-decay band + count region_00145 (chr6) density (set --max-subregion-span-mb 7 if >75k var). LOCKED: A.3 fix correct; ordering A kept; cohorts intact.
- [~] m3-02c-W2-rescope-quota-probe-and-gonogo-PLAN.md — Wave 1 (re-scope; autonomous:false, Carter fires in-perimeter): quota gate + real-cohort cost probe + redo_ld_cost_model.py + go/no-go. **FIRED 2026-06-22, partial → SUPERSEDED by m3-02d.** Quota Tasks 1-2 CLOSED (N2_CPUS=5000 pre-satisfied). STEP A preflight DONE (all 15 cells >75k var → split too coarse). STEP B minimal EUR probe: **0 spill on a 64GB cluster cores=1 → the n2-highmem premise was WRONG**; bottleneck = the A.3 WRITE; cell INTERRUPTED at 56min (no clean rate). Findings re-scoped the split granularity + cost model into m3-02d; redo_ld_cost_model.py was never built here (built in m3-02d).
- [ ] m3-02d-W2-rescope-write-egress-split-PLAN.md — Wave 2 (re-scope; autonomous:false for the re-probe, code tasks autonomous; plan-checker PASS 2026-06-22). Write+egress-bound redesign from the m3-02c probe: (1) per-ancestry buffer **AFR 3Mb / EUR 5Mb, core span 5Mb** in build_ld_region_manifest [code change — single-global knob today] + regen manifests; (2) ordering-B A.3 write [banded scratch ~7× smaller at radius≪span] + re-derive over_threshold around write-block-count+output-GiB (retire the 75k memory proxy) + per-chrom egress helper; (3) BUILD redo_ld_cost_model.py; (4) human-gate in-perimeter re-probe of COMPLETING AFR + EUR cells (ordering A vs B) on the existing 64GB HAIL cluster 20260604 cores=1 → clean blocks_per_min; (5) cost model + GREEN/RED go/no-go. Band width = Carter's locked scientific call (3-5× the LD-decay scale, under Pan-UKBB 10Mb). 322-cell production stays in m3-04. **SUPERSEDED by m3-02e: the Hail re-probe returned NOT-GREEN (~34k cluster-h) → cost re-architecture accepted.**
- [~] m3-02e-W2-native-ld-export-and-public-eur-PLAN.md — Wave 2 (COST RE-ARCHITECTURE; native-plink PILOT GREEN 2026-06-24). **Tasks 1-3 EXECUTED + SUMMARY 2026-06-24** (commits `fe83e8b`..`e17e77a`: `plink_ld_to_npz.py` + native helpers; `build_public_eur_manifest.py` + `m3_public_eur_ld.smk` public 337k EUR; `pipeline.yaml` EUR head=`EUR_ukbb_pub` + `estimate_s` guard + m3-04-superseded record; 38 tests pass). **T4 = the in-perimeter native-plink LD loop (autonomous:false) PENDING — Carter fires** per `m3-02e-AFR-NATIVE-FIRE-BRIEF.md` (production-VM re-measure is a BLOCKING stop-gate). Replaces the NOT-GREEN Hail BlockMatrix path (~34k cluster-h) per `m3-W2-cost-effective-rearchitecture.md` + `m3-W2-pilot-report.md`. **Three moves:** (1) **AFR LD in-house but NATIVE** — export the QC'd AFR cohort ONCE from the Hail MT to plink `.bed` (one-time count_cols scan amortized), then compute per-region banded/square LD on a single Spot VM looping the ~276 regions with `plink1.9 --r square bin4 --keep-allele-order` (pilot-validated: 25–56 min/region, ~$174–1,084 full panel, ~1–2 OOM cheaper than Hail); (2) **EUR LD = PUBLIC reference, $0** — ingest a biobank-scale public UKBB EUR LD panel (Weissbrod/PolyFun 337k `.npz` **or** Pan-UKBB 420k) on NCSU + hg19→hg38 liftover/coordinate adapter (Carter chose public; better-matched to external EUR GWAS than AoU 220k); (3) **downstream on NCSU** — coloc/SuSiE with `estimate_s`, consuming egress-clean AFR `.npz` + public EUR. **The one billable in-perimeter step (export-once + native LD loop on a Spot VM) is autonomous:false** — Carter fires it per a turnkey brief. PILOT CAVEATS to honor: re-measure the production-VM wall (pilot ran n2-standard-16, $rates labelled n2-highmem-64) before committing the budget; banded ~400M pairs estimated from size; per-region export ~33s. 322-cell production stays in m3-04.
- [x] m3-03-W3-ncsu-ingest-and-resolver-PLAN.md — Wave 3: src/scripts/ld_npz_to_rds.R (chr-prefix fix + GRCh38 to GRCh37 variant ID liftover per DEC-2026-04-24-01 + provenance JSON) + src/python/bm_to_npz.py (Path A.3 helper) + m3_ingest_aou_ld.smk + m3_convert_npz_rds.smk + finemap.smk resolver wiring (RESEARCH Q7) + converter pytest
- [ ] m3-04-W4-production-and-egress-PLAN.md — Wave 4: validate_bundle_sizes.py (50 GB cap per RESEARCH Q4) + m3_validation.smk (production-scale 30-region Check 4 sample gated on m3_dev_complete.flag) + AOU-2 production fire 322 cells (160-260 cluster-hours) + 44 per-chromosome egress requests + 322 .rds files land + 44 audit-log rows + 44 SHA-256 sub-manifests. **SUPERSEDED-PENDING-REPLAN (2026-06-24, by m3-02e):** the 322-cell **Hail BlockMatrix** LD production fire is RETIRED — m3-02e builds the AFR LD panel natively (plink on a Spot VM, ~276 windows) + the EUR LD from a public UKBB reference ($0). m3-04 must be re-planned to **CONSUME** m3-02e's AFR-native `.npz` + public EUR `.rds` (the egress/audit/validation scaffold stays), NOT rebuild LD via Hail. (322 = pre-m3-02d 161×2 basis; 276 = post-m3-02d per-ancestry AFR window count.)
- [ ] m3-05-W5-closeout-and-osf-PLAN.md — Wave 5: validation memo Wave 4 production addendum + PDF generation + 322-row monolith SHA-256 freeze + audit log close-out summary + toy 3-locus AFR identity-placeholder fixtures (REQ-SNAKEMAKE-CI) + m2_post_m3_rerun_queue status update (no closures per D-M3-05) + ROADMAP M2-supplementary phase entry (slug m2-supp-aou-afr-rerun) + STATE.md update + m3-PHASE-CLOSEOUT.md + OSF posting of validation memo PDF to osf.io/az52u (D-M3-08)
- [ ] m3-06-W6-ld-nan-psd-conditioning-PLAN.md — Wave 6 (999.1 §2-4 promotion; autonomous NCSU code, planned 2026-07-07): the AFR native-panel NaN conditioning MACHINERY under the posted OSF amendment (`tcujq`). **T1** — refactor the two r3 PSD fns (`psd_regularize_ridge`/`_eigclip`) into a shared `src/R/regularization/psd_utils.R`; `refit_sh2b3_psd_regularized.R` sources it; **byte-identity gate** (frozen golden + verbatim cross-check) guards the in-flight Track-A / r3 numerics. **T2** — `src/python/condition_ld_matrix.py`: pre-registered off-diagonal `NaN→0` (topology branch RAISE on fully-NaN/zero-variance rows; zero isolated pairs, diagonal untouched) + `n_zeroed_pairs ≤ 0.0005×n_var` ceiling RAISE (BRANCH_AFR_COND_DEFERRED) + provenance; **memory-bounded** block-wise (reuses the plink_ld_to_npz OOM discipline; `read_square_bin`/`content_verify_npz` stay FROZEN). **T3** — `src/python/write_conditioned_ld_npz.py`: bank a SEPARATE `{region}.conditioned.npz` with base + provenance keys (`psd_method`/`psd_lambda` placeholders filled at fit time/§5); raw `.npz` + `ld_npz_to_rds.R` UNCHANGED. TDD RED-first, 3 tasks, no perimeter access, no loop contact. **§5 (fit-time wiring) + §6 (in-perimeter region-1 verify) stay PARKED in 999.1 — loop-gated.** **⚠ NaN→0 SUPERSEDED 2026-07-10 by m3-07 (occlusion mechanism resolved — no `r` to zero); m3-06 STAYS HELD, `condition_ld_matrix.py` FROZEN, never fed to a fit.**
- [ ] m3-07-W7-overlapping-deletion-span-filter-and-provenance-PLAN.md — Wave 7 (planned 2026-07-10; **SUPERSEDES 999.1's dead NaN→0 approach**): the **upstream overlapping-deletion span-filter** at panel-build + a **load-bearing provenance manifest** + a **genome-wide present-rate-per-ancestry scan** + the **lockstep sumstats-side drop at m3-04**. **Mechanism RESOLVED** (geometry verdict `m3_region1_nan_geometry_verdict.md`, byte-verified `4543dcf4…`, landed `5fd58a5`): region-1 NaN = overlapping-deletion **occlusion** — a deletion's REF span physically covers a partner SNP's POS → the base is absent on the deletion haplotype → uncallable → structurally-undefined `r` (5 direct `ref_span_overlap` + 1 second-order, **0** same-position/mergeable → `bcftools norm` fixes none). **Policy RESOLVED** (`m3_panel_occlusion_policy_decision.md`, byte-verified `42d70167…`, `8f36fdf`): **exclude-in-lockstep across panel AND sumstats + a mandatory provenance manifest** (per dropped variant: ID + BOTH-build positions, occluding deletion + REF span, locus, traits-present, reason=reference-occlusion→undefined-LD; the manifest doubles as the Angle-1/3 occlusion catalog); **NaN→0 DEAD**; panel-only-exclude UNSAFE (orphans the sumstats-present `rs182965575` on the `(CHR,POS)` join). **Scope:** T1 detect occlusion (a deletion REF-interval covering a neighbor POS) across ALL 276 regions in the panel-build path (`run_native_ld_panel.py`/`aou_ld_panel.py`) → exclude the occluded record from the LD window BEFORE plink `--r`; T2 emit the per-region + aggregate provenance manifest; T3 genome-wide present-rate-per-ancestry scan (PRESENT vs ABSENT occluded variants); T4 wire the lockstep sumstats-side drop at m3-04. TDD RED-first, panel-build code (no perimeter access; **no loop re-fire until it lands**). **⚠ HARD GATE (BLOCKS all fix code):** pre-register the scoped OSF amendment-update (panel overlapping-variant policy = exclusion+provenance, never zeroing) BEFORE any fix code lands — mirrors the 999.1 OSF-gate discipline. Amendment doc-set (all on origin `5fd58a5`): WHY `3516c18` · JOIN-IMPACT `c4e0875` · POLICY `8f36fdf` · WHAT/mechanism `5fd58a5`. Context: `.planning/phases/m3-aou-afr-ld-panel-build/m3-07-CONTEXT.md`.

**Status**: planning complete 2026-04-28 (6 plans, 6 waves; nyquist_compliant=true on all plans; threat_models referenced; 5/5 REQ-IDs covered; 9/9 D-M3-XX decisions referenced); Wave 0 foundations + Wave 1+ Carter hard-gate stack pending fire. Wave 0 (NCSU-local foundations) executes autonomously; Waves 1+ block on Carter 6-gate AoU portal action stack.

**Live progress 2026-05-21:** m3-00 W0 + m3-01 W1 + m3-03 W3 COMPLETE; m3-02 W2 **PARTIAL — Tasks 1+2 done atomically; Task 3 awaiting Carter signoff on m3-VALIDATION-MEMO.md + m3_dev_complete.flag touch**. m3-04 W4 + m3-05 W5 blocked on m3_dev_complete.flag existing.

**Wave-2 RE-SCOPE 2026-06-18:** the dev-10 LD fire was KILLED as operationally intractable on the dev cluster (real cohorts 73k-220k samples make each correlation block ~36-110x heavier than the 2,000-sample synthetic repro measured; region_00006 crawled + master crashed at ~65 GiB dense scratch; 0 regions completed) — a CAPACITY wall, not a correctness bug. Re-scoped via m3-02b (xlarge split + sparse block-diagonal stitch + Q-RS2 executor config, NCSU code, autonomous) + m3-02c (N2 quota gate + real-cohort cost probe + PROJECTED x 1.3 <= BUDGET_CAP go/no-go). m3-04 322-cell fire now gates on the m3-02c GREEN disposition (replaces the stale ~1,117 cluster-h model). Per WAVE-2-RESCOPE-real-cohort-compute.md + m3-RESEARCH-W2-RESCOPE.md.

### M4: Scalable coloc + fine-mapping
**Slug**: m4-scalable-coloc-finemapping
**Goal**: Two-stage coloc — fast ABF-coloc (Giambartolomei 2014;
Wallace 2020) genome-wide first, then SuSiE-RSS (Zou 2022) only where
PP.H4 > 0.5 (cuts compute 10–20×). Region-level PP.H4 FDR correction.
HyPrColoc (Foley 2021) across ≥3 traits simultaneously. PolyFun
baselineLF2 functional priors (Weissbrod 2020) for rescue of underpowered
credible sets. AFR fine-mapping with AoU LD; EUR with 1000G + UKB LD.
**Novelty deliverables Classes 2 + 3**: AFR-specific lead variants and
secondary independent credible sets at known loci (Amendment §3 M4, §6, §7.1).
**Requirements**: REQ-TWO-STAGE-COLOC, REQ-HYPRCOLOC-MULTI,
REQ-POLYFUN-RESCUE, REQ-SUSIE-RSS-POLICY, REQ-NOVELTY-CLASS-2,
REQ-NOVELTY-CLASS-3, REQ-NEGATIVE-CONTROLS
**Dependencies**: M3 LD panels; M2 region list
**Success Criteria**:
  1. Per-region ABF PP.H4 table genome-wide (discovery region list)
  2. SuSiE-RSS outputs restricted to PP.H4 > 0.5 regions, with PolyFun-rescue column
  3. HyPrColoc regional_prob tables for ≥3-trait blocks
  4. Tier A / B / C classification with re-calibrated cutoffs
  5. `afr_specific_novel.tsv` (Class 2) + `secondary_signals.tsv` (Class 3)
  6. Negative-control regions (HLA, pigmentation, blood-group) null per REQ-NEGATIVE-CONTROLS
**Deliverable Artifacts**:
  - `results/coloc/abf_pph4_genome_wide.tsv`
  - `results/coloc/susie_rss_polyfun/` per-region credible-set tables
  - `results/coloc/hyprcoloc/` per-block regional_prob tables
  - `results/novelty/afr_specific_novel.tsv` (Class 2)
  - `results/novelty/secondary_signals.tsv` (Class 3)
  - Tier A / B / C classification tables per ancestry
**Gating condition for M5**: Tier A list frozen; cross-panel LD-sensitivity
parity check on Class 3 secondary signals complete.
**Status**: not planned; gated on M3 + M2.

### M5: Variant→gene prioritization + novelty cross-reference
**Slug**: m5-variant-to-gene-prioritization-plus-novelty-cross-reference
**Goal**: L2G (Open Targets Genetics; Mountjoy 2021) prior; eQTL / pQTL
coloc refreshed with upgraded sumstats; Borzoi variant-effect scoring
(Linder 2024) on Tier A credible-set variants; MAGMA gene-set re-run.
**Novelty deliverables Classes 4 + 5**: cross-reference colocalized loci
against locked versions of Pickrell 2016, Watanabe 2019 GWAS Atlas, and
Open Targets L2G to extract pleiotropy-class novel loci (Class 4);
annotate Tier A credible-set variants with Borzoi/Enformer effect scores
in tissue-specific tracks against ClinVar v_lock + GWAS Catalog v_lock +
primary-literature search to extract functional-mechanism novel variants
(Class 5, supplementary per §7.3). Catalog versions locked at M5
cross-reference date with SHA-256 checksums (Amendment §3 M5, §6, §7.1,
§7.2).
**Requirements**: REQ-L2G-GENE-PRIORITIZATION, REQ-BORZOI-VARIANT-EFFECT,
REQ-CATALOG-VERSION-LOCK, REQ-NOVELTY-CLASS-4, REQ-NOVELTY-CLASS-5
**Dependencies**: M4 Tier A list
**Success Criteria**:
  1. Per-Tier-A credible-set gene-prioritization table with L2G top-3
  2. Borzoi per-tissue score column for every Tier A credible-set variant
  3. `pleiotropy_novel.tsv` (Class 4) + `functional_novel.tsv` (Class 5 supplementary)
  4. `catalog_lock_manifest.tsv` with SHA-256 + URL per comparator catalog
  5. Consolidated novelty manifest with per-locus class assignments (one row per locus; multi-class allowed)
**Deliverable Artifacts**:
  - `results/gene_prioritization/l2g_table.tsv`
  - `results/borzoi/variant_effect_scores.tsv`
  - `results/novelty/pleiotropy_novel.tsv` (Class 4)
  - `results/novelty/functional_novel.tsv` (Class 5, supplementary)
  - `data/catalogs/catalog_lock_manifest.tsv` with SHA-256 checksums
  - Consolidated novelty manifest (5-class table)
**Gating condition for M6**: M5 deliverables frozen; comparator catalogs locked.
**Status**: not planned; gated on M4 Tier A.

### M6: Manuscript and replication
**Slug**: m6-manuscript-and-replication
**Goal**: Draft Track B manuscript; run hold-out replication on FinnGen
R13+ / Pan-UKBB / MVP release n+1 where available for Tier A claimed
loci and novel-variant Classes 1–4; generate figures; OSF deposit of
all post-registration outputs; submit to Nature Genetics (Amendment §3 M6).
**Requirements**: REQ-REPLICATION-HOLDOUT, REQ-EQUITY-FRAMING,
REQ-SNAKEMAKE-CI
**Dependencies**: M5 complete
**Success Criteria**:
  1. Per-class replication table with point estimate, 95% CI, sign agreement, post-hoc power
  2. Track B manuscript draft + figures under `manuscript/track_b/`
  3. OSF post-registration data deposit with all artifacts
  4. Zenodo DOI for reproducible pipeline release
  5. Nature Genetics submission confirmation + tracking number
**Deliverable Artifacts**:
  - `results/replication/per_class_replication_table.tsv`
  - `manuscript/track_b/` (draft + figures + supplementary)
  - OSF deposit record
  - Zenodo DOI for Snakemake pipeline release
  - Submitted manuscript + tracking number
**Gating condition**: Track B submission lands; Track A already ships
independently per Track-A-finalization row below.
**Status**: not planned; gated on M5.

## Current milestone sequence (Track A short-form)

### Track-A-finalization
**Slug**: track-a-finalization
**Goal**: Finalize Track A short-form methods paper framing the real-LD
audit of 50 curated cardiometabolic regions; submit bioRxiv preprint +
venue submission (Genome Medicine primary; AJHG short-report / Bioinformatics
Applications Note fallbacks) per ID-VS-REF-LD-STRATEGY.md and Amendment §8.
**Requirements**: REQ-PUBLIC-DATA-ONLY, REQ-SNAKEMAKE-CI,
REQ-SUSIE-RSS-POLICY, REQ-OSF-PREREG, REQ-PP.H4-THRESHOLD-SWEEP,
REQ-NEGATIVE-CONTROLS, REQ-PATH-PARAMETERIZATION
**Dependencies**: Pre-pivot spine (Phases 1, 2, 5, 9) outputs; independent
of Track B milestone sequence
**Sub-tasks**:
  - [x] Numeric reconciliation complete (2026-04-23, commit 05a701a):
    Stage 2 values locked in `TRACK-A-FROZEN-NUMBERS.md` (51/96 CS; 0
    Tier A; SH2B3 × asthma EUR identity-LD PP.H4=1.0 → real-LD
    n_cs_a=0; 224 negative-control rows all null)
  - [ ] Introduction rewrite (ID-VS-REF-LD-STRATEGY.md §4.5): 5-paragraph
    restructure; strip ML framing; demote evolutionary-medicine to
    Discussion
  - [ ] Discussion rewrite (ID-VS-REF-LD-STRATEGY.md §4.17): identity-LD
    inflation as dominant finding; drug-target-inference caution;
    Track B forward pointer
  - [ ] References additions: Wallace 2021, Zou 2022, Weissbrod 2020, Benner 2017
  - [ ] 3 figures: identity-LD vs real-LD CS yield, SH2B3 locus plot,
    pathway enrichment reconfiguration (build scripts under `src/R/figures/`)
  - [ ] bioRxiv preprint submission (Day 1 of draft-complete)
  - [ ] Genome Medicine Original Research submission (primary target)
**Success Criteria**:
  1. bioRxiv DOI minted and logged in `.planning/amendments/`
  2. Genome Medicine submission confirmation + tracking number
  3. All abstract numbers cite `TRACK-A-FROZEN-NUMBERS.md` verbatim
**Status**: numeric reconciliation done; remaining edit passes are Route A
of the resume plan. Independent of Track B M0–M6 progress.

### Track-A-R2-sh2b3-canonical-and-cache-refresh
**Slug**: ta-sh2b3-canonical-and-cache-refresh
**Goal**: Track A R2 phase closing two open Genome Medicine manuscript issues.
Issue 1 — SH2B3 canonical-pair reference-LD coverage gap: 3 of 5 SH2B3 EUR
per-trait SuSiE-RSS fits (BMI, hypertension, stroke) are non-converged at
L=10 / niter=100 (the SuSiE iteration-cap regime per Wang et al. 2020
§Discussion); identity-LD hypertension carries `L_saturated=TRUE` in the
per-fit JSON. Re-fit at expanded L (L=20 vs pre-registered L-sweep
{15, 20, 30}; choice gated on OSF check), verify `n_CS << L` per Zou et al.
2022 §Discussion, then run coloc.susie on the canonical SH2B3 EUR
trait-pairs (minimum BMI–HTN + HTN–stroke; recommended 9 new pairs to
symmetrize Table 3 with the FTO_16q12 row). The manuscript's canonical
claims (`PP.H4 = 1.00` at rs3184504, rs10774625, rs7137828, rs4766578 for
BMI–hypertension and hypertension–stroke) have never been tested under
reference-LD; Table 3 currently shows those rows as "not executed". Issue
2 — variant-ID matcher fix cache propagation refresh: code fixes ALREADY
committed in current branch (`069b34f` extended `run_qtl_coloc.R` to
tolerate chr:pos-formatted variant IDs; `7d54183` added LD-panel-rsid
override to `run_susie_rss.R`), but intermediate caches were generated
BEFORE those commits landed and weren't invalidated. 1,005 / 1,274
(78.9 %) QTL-coloc attempts returned `too_few_snps` owing to harmonized-TSV
vs SuSiE-fit variant-ID format mismatch (chr:pos vs rsid). Re-fire the
QTL-coloc layer (and conditionally the SuSiE-RSS layer per Wave-0
cache-layer diagnostic) and refresh all downstream aggregators + Fig S7 +
Table 1 + Tier assignments + Pathway disclosure + manuscript narrative
against post-refresh disk numbers.
**Requirements**: REQ-PUBLIC-DATA-ONLY, REQ-SUSIE-RSS-POLICY,
REQ-PP.H4-THRESHOLD-SWEEP, REQ-OSF-PREREG, REQ-SNAKEMAKE-CI,
REQ-PATH-PARAMETERIZATION
**Dependencies**: Submission bundle commit `cacdbfe` (`quick-260427-vbq`)
frozen checkpoint; Phase 1 SuSiE-RSS outputs (re-fits at expanded L);
Phase 2 Stage 2 real-LD coloc.susie outputs; Phase 2 QTL-coloc cache
(intermediate, slated for invalidation); honest-framing-lock chain at
`docs/manuscript/id-vs-ref-LD.md` (L148 + L295 + L220 + L90) +
R-script header + locked-scalar block + plot_annotation + 1vy SUMMARY
(must be preserved verbatim per `.planning/feedback_original_research_framing.md`)
**Open scope-decisions (Wave 0 — locked by `/gsd-discuss-phase` + Carter):**
  - **L value** for SH2B3 EUR per-trait SuSiE-RSS re-fits — L=20 vs
    pre-registered L-sweep {15, 20, 30} (check OSF pre-reg `osf.io/pvb5j`
    first; convergence verification per Zou 2022 §Discussion `n_CS << L`)
  - **Canonical-pair scope** — minimum BMI–HTN + HTN–stroke vs all 9 new
    SH2B3 EUR trait-pair combinations (`asthma–bmi`, `asthma–hypertension`,
    `asthma–stroke`, `bmi–hypertension`, `bmi–stroke`, `bmi–t2d`,
    `hypertension–stroke`, `hypertension–t2d`, `stroke–t2d`) to symmetrize
    Table 3 with the FTO_16q12 row
  - **Cache-layer scope** — QTL-coloc only (fast path) vs both
    SuSiE-RSS + QTL-coloc (conservative path); decided by Wave-0
    SuSiE-RSS variant-ID format diagnostic on
    `results/fine_mapping/susie/*.json` (chr:pos → both layers stale;
    rsid → QTL-coloc only)
  - **OSF amendment posting** before Wave 1 fires (`osf.io/pvb5j` or
    `osf.io/az52u`) for any L value, threshold (`PP.H4 ≥ 0.5` vs `≥ 0.8`),
    or scope choice not already pre-registered
**Suggested wave structure (final wave count + scope decided by
`/gsd-plan-phase`, NOT pre-locked here):**
  - **Wave 0**: source-repo path discovery on `login02.hpc.ncsu.edu` +
    verification that `069b34f` + `7d54183` reachable from HEAD
    (`git merge-base --is-ancestor`; cherry-pick if absent) + SuSiE-RSS
    cache-layer diagnostic + scope-decision questions to Carter
  - **Wave 1**: expanded-L SuSiE-RSS re-fits for SH2B3 EUR per-trait
    BMI + hypertension + stroke; convergence verification (`n_CS << L`
    per Zou 2022 §Discussion)
  - **Wave 2**: coloc.susie production fire on canonical SH2B3 EUR pairs
    (LSF; minimum BMI–HTN + HTN–stroke; recommended 9 pairs)
  - **Wave 3**: `checkpoint:human-verify` — Carter selects SH2B3 outcome
    branch from observed disk numbers BEFORE narrative writes:
      (a) BMI–HTN reference-LD `PP.H4 < 0.5` → identity-LD canonical
          claim does NOT survive matched-LD; flagship demonstrated
          collapse; strongest finding
      (b) `PP.H4 ∈ [0.5, 0.8)` → partial survival; calibration finding;
          manuscript pivots to "magnitude of inflation, not categorical"
      (c) `PP.H4 ≥ 0.8` → canonical claim holds up under matched-LD;
          SH2B3 anchor flips from "collapse" to "validated"; manuscript
          headline narrows but Fig S2 structural-inflation finding +
          FTO Tier-C disclosure still load-bearing
    Decision recorded as `D-TA-XX` in CONTEXT.md. Plan must NOT
    pre-commit to a branch.
  - **Wave 4**: variant-ID cache invalidation
    (`mv results/qtl_coloc results/qtl_coloc.preFix.bak`; SuSiE-RSS layer
    conditional on Wave-0 diagnostic) + Snakemake re-fire
    `--use-conda -j 50`. LSF compute envelope: ~1,274 QTL-coloc × ~30 sec
    ≈ ~10 hr at 50 cores; SuSiE-RSS re-fits if needed add ~5 hr
  - **Wave 5**: downstream aggregator refresh —
    `scripts/python/aggregate_qtl_coloc.py` + `scripts/R/aggregators/` +
    `fig_h3_ld_overlap_dose_response.R` (Fig S7 dose-response) + Table 1
    builder + Tier-assignment script + Pathway-disclosure aggregator.
    **PASS criterion**: `too_few_snps` count drops materially from 1,005
    (target ≤200; `success` + `no_qtl_cs` counts rise correspondingly).
    **FAIL criterion**: stays ~1,000 → SuSiE-RSS layer was the actual
    problem; root-cause investigation triggered, do NOT proceed to Wave 6
  - **Wave 6**: manuscript narrative atomic updates per Wave-3 branch +
    Wave-5 refreshed numbers — Methods §Harmonization-Pipeline
    Diagnostics, Limitations bullet 5, Discussion §Identity-LD Inflation,
    Discussion §SH2B3 anchor, Results §SH2B3 case study, Fig 3 caption,
    Fig S7 caption, Conclusion-1, Abstract, Table 3 SH2B3 rows, Table 4
    (`n_attempted` / `n_failed` columns), plus SH2B3-specific paragraphs
    in `docs/manuscript/id-vs-ref-LD.md`
  - **Wave 7**: phase closeout — SUMMARY.md per plan with deviations log
    + verification dimensions D1–DN PASS/WARN/FAIL JSON + new submission
    bundle build via `bin/build_id_vs_ref_ld_submission_bundle.sh` + SHA-256
    manifest update + OSF deviation log entry at `osf.io/az52u`
**Invariants the plan MUST honor (non-negotiable):**
  - NO `/gsd-quick` shortcuts. Atomic commits per task. SUMMARY.md per
    plan. Verification dimensions D1–DN with PASS/WARN/FAIL evidence.
  - Manuscript narrative writes ONLY in Wave 6 AFTER disk numbers are
    frozen at Wave 5. Never pre-write narrative against anticipated
    outcomes.
  - Honest-framing-lock chain preserved at every anchor point
    (`docs/manuscript/id-vs-ref-LD.md` L148 + L295 + L220 + L90 +
    R-script header + locked-scalar block + plot_annotation + 1vy
    SUMMARY). Original hypothesis-driven research framing only — never
    "revision" / "correction" / "cleanup" / "fix" (per
    `.planning/feedback_original_research_framing.md` memory).
  - DEC-2026-04-25-01 preserved: `results_identity_ld/` NOT committed;
    `.gitignore` + canonical CS-yield summary at
    `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` only.
  - Stage 2 md5 byte-identical preservation rule for files not
    intentionally rewritten by this phase (verify md5sum pre-vs-post
    each commit).
  - Pre-registration discipline: any L value, threshold, or scope choice
    not already pre-registered enters via OSF amendment posted BEFORE
    Wave 1 fires — not silent change.
**Success Criteria** (preliminary; `/gsd-plan-phase` will refine):
  1. SH2B3 EUR per-trait SuSiE-RSS fits converged at chosen L
     (`n_CS << L` verified) for BMI + hypertension + stroke
  2. coloc.susie executed on at minimum BMI–HTN + HTN–stroke canonical
     pairs against converged fits (preferably 9 new pairs to symmetrize
     Table 3 with FTO_16q12)
  3. Carter outcome-branch decision (a / b / c) recorded as `D-TA-XX`
     in CONTEXT.md before any narrative writes
  4. QTL-coloc cache invalidation + Snakemake re-fire complete;
     `too_few_snps` drops materially from 1,005 baseline (PASS ≤ 200;
     FAIL ≈ 1,000 → SuSiE-RSS layer root-cause investigation triggered)
  5. Downstream aggregators (Fig S7, Table 1, Tier assignments, Pathway
     disclosure, Table 4) refreshed against post-refresh disk numbers
  6. Manuscript narrative atomically updated per Wave-3 branch + Wave-5
     refreshed numbers (Methods, Results, Discussion, Limitations,
     Abstract, Conclusion-1, captions, tables) with honest-framing-lock
     chain preserved verbatim
  7. New submission bundle built via
     `bin/build_id_vs_ref_ld_submission_bundle.sh` + SHA-256 manifest update
     + OSF deviation log entry at `osf.io/az52u`
**Plans**: 8 plans (Wave 0 through Wave 7; one PLAN.md per wave)

Plans:
- [x] ta-sh2b3-W0-foundations-and-osf-gate-PLAN.md — Wave 0: source-repo path + code-fix ancestry + variant-ID format diagnostic + OSF pre-reg gate + per-L policy YAML + dispatch drivers + verification harness scaffolding
- [x] ta-sh2b3-W1-susie-rss-l-sweep-PLAN.md — Wave 1: SH2B3 EUR L-sweep SuSiE-RSS re-fits at L ∈ {15, 20, 30} for BMI + hypertension + stroke; convergence verification per Zou 2022
- [x] ta-sh2b3-W2-canonical-pair-coloc-susie-PLAN.md — Wave 2: 9 SH2B3 EUR canonical-pair coloc.susie production fire against Wave-1 PRIMARY_L fits (parallel namespace coloc_susie_R2/)
- [x] ta-sh2b3-W3-checkpoint-human-verify-PLAN.md — Wave 3: checkpoint:human-verify outcome-branch gate; Carter records D-TA-WAVE3-OUTCOME-{A_COLLAPSE|B_PARTIAL|C_SURVIVE} from Wave 2 disk numbers
- [x] ta-sh2b3-W4-cache-invalidation-and-refire-PLAN.md (closed via /gsd-quick 260501-r1q W4.5-A continuation drain + 260501-v9q CR-001 regression) — Wave 4: variant-ID cache invalidation + Snakemake re-fire with --use-conda -j 50; PASS = too_few_snps ≤ 200; FAIL = trigger Wave 4.5 SuSiE-RSS fallback
- [x] ta-sh2b3-W5-aggregator-and-figure-refresh-PLAN.md (closed via /gsd-quick 260501-wdn aggregator + figure refresh + frozen numbers) — Wave 5: downstream aggregator refresh + R2-canonical merge into coloc_summary.tsv (Pitfall 3 exemption) + TRACK-A-FROZEN-NUMBERS LIVE blocks updated + Fig S7 regenerated
- [x] ta-sh2b3-W6-rename-and-narrative-PLAN.md (closed via /gsd-quick 260502-lsk mechanical rename + 260502-1c1 cache-staleness refuted + 260502-tjn BRANCH_C SURVIVE substitution + 260503-1e1 PRESERVE-WITH-DISCLOSURE) — Wave 6: id-vs-ref-LD nickname rename (3 git mv + 17 reference fix-ups; ~50 historical quick files preserved) + manuscript narrative atomic updates per Wave-3 branch + Wave-5 frozen numbers
- [x] ta-sh2b3-W7-closeout-bundle-and-osf-deviation-PLAN.md (closed via /gsd-quick 260503-kfq bundle + osf_deviations + md5 invariant) — Wave 7: phase closeout — new submission bundle via renamed builder + SHA-256 manifest + Stage 2 md5 invariant whitelist + osf_deviations.md created + final C1-C15 sweep

**Status**: planned 2026-04-29 (8-wave structure mirrors CONTEXT.md `<wave_structure>` and RESEARCH.md wave-by-wave breakdown). Routed next to `/gsd-execute-phase ta-sh2b3-canonical-and-cache-refresh` starting at Wave 0. Independent of Track B M0–M6 progress (Track A short-form sequence). Concurrency note: stale `.claude/scheduled_tasks.lock` (Apr 22) confirmed dead at this entry's commit time; no live concurrent ROADMAP writer. If Terminal A reactivates before phase execute fires, stagger writes.

### Track-A-R3-audit-v2-driven-psd-and-r1-refire
**Slug**: ta-r3-audit-v2-driven-psd-and-r1-refire
**Goal**: Track A R3 phase to address v2 audit findings A1–A9 documented in
`HPC_HANDOFF_v5_2026-05-04.md` (Cowork-side authoritative scope source). HPC
lane (this phase) covers compute-side audit items: (a) SH2B3 12q24 EUR
PSD-regularized SuSiE re-fit + canonical-pair coloc.susie under λ ∈
{0.001, 0.01, 0.1} ridge sweep with eigenvalue-clip alternative
(W1; outcome branches BRANCH_PSD_{FIRM, PARTIAL, COLLAPSE, NON_CONVERGE});
(b) R1 trait-pair coloc.susie cache-invalidated re-fire post commits
`069b34f` + `7d54183` + `02c4404` (W2; outcome branches
BRANCH_R1_{BUG, STRUCTURAL}); (c) optional R2 canonical-pair parity re-fire
at FTO_16q12 / MC4R_18q21 / APOL1_22q12 / CXADR_F2RL1_6p21 EUR (W3); (d)
optional HLA_6p21 reclassification on `tier_assignments.tsv` (W4;
200-vs-224 reconciliation). Cowork-side scope (A1 / A2 / A3 / A6-stats /
A7 / A8 / A9 manuscript edits + v5 bundle ship) executes after HPC
artifacts land — explicitly OUT OF this phase's scope.
**Requirements**: REQ-PUBLIC-DATA-ONLY, REQ-SUSIE-RSS-POLICY,
REQ-PP.H4-THRESHOLD-SWEEP, REQ-OSF-PREREG, REQ-SNAKEMAKE-CI,
REQ-PATH-PARAMETERIZATION
**Dependencies**: Track-A-R2-sh2b3-canonical-and-cache-refresh closeout
(`/gsd-quick 260503-kfq` W7 + `/gsd-quick 260503-vcl` submission-readiness
wrap; bundle sha256 `a93d8f4952d1...` at
`.planning/quick/260427-vbq-assemble-track-a-genome-medicine-submiss/id_vs_ref_ld_genome_medicine_submission.zip`);
commits `069b34f` (variant-ID matcher in `run_qtl_coloc.R`), `7d54183`
(LD-panel-rsid override in `run_susie_rss.R`), `02c4404` (referenced in
HPC_HANDOFF_v5_2026-05-04.md); honest-framing-lock chain at
`docs/manuscript/id-vs-ref-LD.md` (must be preserved verbatim per
`.planning/feedback_original_research_framing.md` memory — frame as
"audit-driven re-analysis," NOT "fix" / "revision" / "cleanup");
HPC_HANDOFF_v5_2026-05-04.md (Cowork-side; canonical A1–A9 audit-finding
spec + λ ridge values + outcome-branch decision tables).
**Suggested wave structure (final wave count + per-wave PLAN.md decided
by `/gsd-plan-phase`, NOT pre-locked here):**
  - **W1** — SH2B3 12q24 EUR PSD-regularized SuSiE re-fit + canonical-pair
    coloc.susie under λ ∈ {0.001, 0.01, 0.1} ridge sweep (with
    eigenvalue-clip alternative if ridge fails to converge). Outcome
    branches recorded as `D-TA-R3-W1-BRANCH_PSD_{FIRM | PARTIAL | COLLAPSE
    | NON_CONVERGE}` per HPC_HANDOFF_v5 decision matrix.
  - **W2** — R1 trait-pair coloc.susie cache-invalidated re-fire against
    commits `069b34f` + `7d54183` + `02c4404` baseline. Outcome branches
    `D-TA-R3-W2-BRANCH_R1_{BUG | STRUCTURAL}` (BUG = cache invalidation
    cleared the failure mode; STRUCTURAL = remaining failures are real
    and demand methods-section disclosure).
  - **W3 (optional, gated on W1/W2 outcomes)** — R2 canonical-pair parity
    re-fire at FTO_16q12 / MC4R_18q21 / APOL1_22q12 / CXADR_F2RL1_6p21
    EUR to symmetrize Table 3 with the W1 SH2B3 PSD update.
  - **W4 (optional, gated on Cowork-side audit decision)** — HLA_6p21
    reclassification on `tier_assignments.tsv` (200-vs-224 row count
    reconciliation).
  - **W5 (closeout — implicit)** — atomic commits for downstream
    aggregator refresh + new freeze of `TRACK-A-FROZEN-NUMBERS.md`
    (md5 invariant WILL shift owing to PSD/R1 cache changes; new md5
    baseline locked here) + SUMMARY.md per wave + VERIFICATION.md
    dimensions D1–DN PASS / WARN / FAIL JSON. Cowork side then ships
    the v5 bundle outside this phase.
**Invariants the plan MUST honor (non-negotiable):**
  - Atomic commits per wave. SUMMARY.md per plan. Verification dimensions
    D1–DN with PASS / WARN / FAIL evidence.
  - Honest-original-research-framing lock preserved verbatim at every
    `docs/manuscript/id-vs-ref-LD.md` anchor (per
    `.planning/feedback_original_research_framing.md`). Frame this phase
    as "audit-driven re-analysis," NOT "fix" / "revision" / "cleanup" /
    "correction."
  - Stage 2 md5 invariant: `TRACK-A-FROZEN-NUMBERS.md` md5 WILL shift
    (PSD/R1 cache regeneration is the explicit driver). New md5 freeze
    locked in W5 closeout — must be added to the
    `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv`
    whitelist as a successor row, NOT silently overwritten.
  - DEC-2026-04-25-01 preserved: `results_identity_ld/` NOT committed.
  - Pre-registration discipline: λ ridge sweep + eigenvalue-clip
    alternative + outcome-branch decision tables enter via OSF amendment
    posted BEFORE W1 fires (osf.io/pvb5j or osf.io/az52u). No silent
    parameter changes.
  - Cowork-side scope (A1 / A2 / A3 / A6-stats / A7 / A8 / A9 manuscript
    edits + v5 bundle ship) MUST NOT be executed in this phase. HPC-side
    artifacts hand off to Cowork side via STATE.md + a quick-task
    handoff brief at `/gsd-quick 260504-XXX-ta-r3-cowork-handoff` (or
    equivalent) once W5 closes.
  - Multi-terminal staging: explicit `git add <path>` only; never
    `git add .` / `-A` per `.planning/feedback_multi_terminal_staging`.
**Plans**: 5 planned (W1 + W2 + W3 + W4 + W5; produced by `/gsd-plan-phase`
2026-05-04). 4 of 5 complete; 1 pending.

Plans:
- [x] ta-r3-W1-sh2b3-psd-regularized-refit-PLAN.md — Wave 1: SH2B3 12q24 EUR
  PSD-regularized SuSiE-RSS re-fit (Wen 2017 ridge + Hutchinson 2020 eigclip)
  across λ ∈ {0.001, 0.01, 0.1}; outcome `D-TA-R3-W1-BRANCH_PSD_FIRM` at
  primary λ=0.01 (5/5 per-trait fits converged; 3/3 canonical-pair PP.H4 =
  1.000000 — SH2B3 12q24 EUR Tier-A anchor empirically supported under
  PSD-regularized LD). W3 gate FIRES.
- [x] ta-r3-W2-r1-trait-pair-coloc-refire-PLAN.md — Wave 2: R1 trait-pair
  coloc.susie cache-invalidated re-fire against HEAD ancestors `069b34f` +
  `7d54183` + `02c4404`; outcome `D-TA-R3-W2-BRANCH_R1_STRUCTURAL` (R1
  non-empty PP.H4 = 0/28 post-refire — Δ=0 vs pre-W2 baseline; Layer-2-
  attrition framing empirically supported; cache-staleness alternative
  refuted).
- [x] ta-r3-W3-r2-canonical-pair-parity-PLAN.md — Wave 3: R2 canonical-pair
  parity re-fire at FTO_16q12 / MC4R_18q21 / APOL1_22q12 / CXADR_F2RL1_6p21
  EUR (gated on W1=BRANCH_PSD_FIRM); outcome `D-TA-R3-W3-OUTCOME` = 0 of 6
  W3 canonical pairs surviving PP.H4 ≥ 0.8 under matched-LD (Layer-2
  attrition consistent with W2 BRANCH_R1_STRUCTURAL — extends to canonical
  pairs at non-Tier-A regions; SH2B3 12q24 EUR remains the only surviving
  Tier-A signal across the 5 admissible regions × canonical-pair set).
- [x] ta-r3-W4-tier-assignments-hla-reconcile-PLAN.md — Wave 4: tier_assignments.tsv
  HLA_6p21 row-count reconciliation; outcome `D-TA-R3-W4-DEFERRED_TO_FOOTNOTE`
  per OSF amendment paragraph (g) option (i) (default path). Investigation TSV
  confirms HLA encoding is via `neg_ctrl_set == "hla_immune"` column flag (24
  rows; matches v5 narrative referent EXACTLY); HLA_6p21 region itself has
  empty `canonical_pairs` in `config/regions_curated.csv` so upstream pipeline
  correctly fires no positional rows. v5 narrative "224 - 24 = 200" was
  pre-W3-baseline-anchored; post-W3 audit-driven substrate is 233 rows
  (224 negative_control + 9 Tier C; 233 - 24 = 209 non-HLA). Cowork-side
  A9 footnote handles the reconciliation; on-disk file UNTOUCHED.
- [x] ta-r3-W5-closeout-and-handoff-PLAN.md — Wave 5: phase closeout +
  Cowork-side handoff brief. Appended 8 successor md5 rows to
  `md5_baseline.tsv` for W1-W3 file shifts (W7 baseline preserved per
  Pitfall 5; manuscript md5 UNCHANGED at `2a57c1a061f0c66988a55d1d6600efdf`
  through all 5 waves). VERIFICATION.md D1-D13 PASS/WARN/FAIL JSON evidence
  written (12/13 PASS + 1/13 WARN at D9 — OSF posting OVERRIDDEN per
  operator decision 2026-05-05; surfaced for Cowork-side disclosure
  routing). Cowork handoff brief at
  `.planning/quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md`
  enumerates wave outcomes + commit range (`bccd0d6..<W5 final>`) + LSF job
  IDs + md5 invariants + artifact paths + Cowork-side A1-A9 TODO list.

**Status**: COMPLETE — closed 2026-05-06; Wave outcomes: W1=BRANCH_PSD_FIRM,
W2=BRANCH_R1_STRUCTURAL, W3=OUTCOME 0/6 surviving, W4=DEFERRED_TO_FOOTNOTE;
Cowork-side handoff at `.planning/quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md`;
OSF amendment at `.planning/amendments/osf-amendment-r3-2026-05-04.md`
(committed locally; OSF web-UI posting OVERRIDDEN per operator decision
2026-05-05 — surfaced as D9 WARN dimension in `ta-r3-VERIFICATION.md` for
Cowork-side disclosure routing decision); honest-framing-lock manuscript
md5 (`2a57c1a061f0c66988a55d1d6600efdf`) unchanged through all 5 waves;
phase headline finding — the audit-V2 §HQ#2(i)/(ii)/(iii)/(g) reviewer
concerns are all addressed empirically and the Track A id-vs-ref-LD
manuscript narrative survives unchanged. Cowork-side scope (A1 / A2 / A3
/ A6-stats / A7 / A8 / A9 manuscript edits + v5 bundle ship + OSF
outcome-branch follow-up update) remains explicitly OUT OF this phase's
scope per the OSF amendment "What is not changing" paragraph.

## Pre-pivot spine (completed 2026-04-14; artifacts reusable per Amendment §8)

The Phase 00–11 content below executed between 2026-02 and 2026-04-14 under
the original candidate-locus framing. It closed as the pre-specified
methods-validation subset per Amendment §8. The Phase 0 reference data +
Phase 1 SuSiE-RSS outputs + Phase 2 Stage 2 real-LD coloc + Phase 5
partitioned heritability + Phase 9 replication scaffolding are reused as-is
downstream: they are Track A's primary data and Track B's candidate-locus
validation subset. Per-phase status markers (`[x]` and `[ ]`) are preserved
verbatim so per-phase git-history traces stay interpretable.

### Overview

Cross-ancestry colocalization revision from descriptive catalog to mechanistically resolved framework. Tiered execution: T1 spine (Phases 0, 1, 2, 5, 9) ships an honest AJHG submission. T2 (Phases 3, 4, 8) adds MR + matched-N + PRS for Nature Genetics ambition — gated on Checkpoint #1. T3 (Phases 6, 7, 10) adds selection scans + deep learning — gated on Checkpoint #2. Phase 11 (manuscript) runs in parallel from Phase 9 onward.

### Phases

**Phase Numbering:** Preserves Revision_Plan.md numbering. Phases are non-sequential because T2/T3 phases interleave.

**Tier Legend:** **T1** = must-ship spine. **T2** = gated on CP#1. **T3** = gated on CP#2. **M** = manuscript (parallel).

- [ ] **Phase 0: Data access + infrastructure** - DUAs, data ingest, Snakemake skeleton, CI smoke test [T1]
- [ ] **Phase 1: coloc.susie fine-mapping spine** - SuSiE-RSS + coloc.susie replaces coloc.abf [T1]
- [ ] **Phase 2: 3-way QTL colocalization** - eQTL/pQTL/sQTL coloc, gene-tissue matrix, threshold sweep [T1]
- [ ] **Phase 5: Pathway + partitioned heritability** - MAGMA, g:Profiler, LDSC-SEG, HESS [T1]
- [ ] **Phase 9: Replication in independent cohorts** - FinnGen, GBMI, MVP, AoU, BBJ [T1]
- [ ] **Phase 3: Mendelian randomization** - Bidirectional MR, weak-instrument mitigation [T2, gated on CP#1]
- [ ] **Phase 4: Matched-N cross-ancestry concordance** - Power-corrected Table 2 replacement [T2, gated on CP#1]
- [ ] **Phase 8: Cross-ancestry PRS** - PRS-CSx, calibration, clinical utility, equity trade-off [T2, gated on CP#1]
- [ ] **Phase 6: Selection scans + polygenic selection** - iHS/SDS/PBS, thrifty-gene tests [T3, gated on CP#2]
- [ ] **Phase 7: Single-cell + EpiMap + ABC** - Cell-type-resolved integration [T3, gated on CP#2]
- [ ] **Phase 10: Deep-learning variant effect + MPRA overlap** - Enformer/Borzoi/Sei/AlphaMissense [T3, gated on CP#2]
- [ ] **Phase 11: Manuscript + figures + submission** - Full manuscript assembly and submission [M, parallel from Phase 9]

### Phase Details

#### Phase 0: Data access + infrastructure
**Goal**: Establish all data sources, fix legacy issues, build reproducible Snakemake skeleton with CI smoke test. Two parallel sub-tracks: Track 0a (DUA applications, non-blocking) and Track 0b (infrastructure, blocks Phase 1).
**Depends on**: Nothing (first phase)
**Requirements**: REQ-1, REQ-9, REQ-12
**Tier**: T1
**Success Criteria** (what must be TRUE):
  1. All 7 open-access data sources downloaded or confirmed reachable
  2. All of Us institutional DURA status documented in .planning/data_access.md
  3. Corrupted supplementary tables (Table 1, 3, S4) fixed and DIAMANTE T2D dedup resolved
  4. Legacy hardcoded paths parameterized via config/pipeline.yaml (grep returns 0 matches)
  5. Conda envs pinned under envs/*.yml with exact versions
  6. Snakemake skeleton built with per-trait/ancestry schema validation
  7. Toy 3-locus CI smoke test completes in under 15 minutes
  8. OSF pre-registration submitted
**Plans**: 4 plans

Plans:
- [x] 00-01-PLAN.md — Config foundation: pipeline.yaml, datasets.yaml, cluster_lsf.yaml, schemas, conda envs, R config loader, data manifest
- [x] 00-02-PLAN.md — Data access checklist: verify connectivity, portal registrations, OSF pre-registration
- [x] 00-03-PLAN.md — Snakemake skeleton: refactor 8 legacy rules, top-level Snakefile, path parameterization, data fixes
- [x] 00-04-PLAN.md — Toy 3-locus CI smoke test: test scaffolding, config override, subsetting script

Track 0a detail (non-blocking DUAs):
- UKB-PPP (Synapse), deCODE pQTL, FinnGen, GTEx v8, Pan-UKBB, BBJ, MVP — all same-day registration/download
- All of Us Researcher Workbench — institutional DURA check first
- UK Biobank main DUA deferred (not-needed-unless status)

Track 0b detail (infrastructure, blocks Phase 1):
- Fix corrupted supplementary tables per Revision_Plan.md section 10
- Audit DIAMANTE T2D dedup (76/63%/26 denominator mismatch)
- Drop KCNJ11 asthma-HTN Tier-1 signal (n_SNPs=6 < 50 threshold)
- Ingest new ancestry GWAS: AFR BMI (Gurdasani 2019), AFR HTN (Hoffmann), AFR T2D, EAS (BBJ), Hispanic (PAGE/HCHS)
- Parameterize 174 hardcoded path references (REQ-12)
- Pin conda envs (REQ-9)
- Build Snakemake skeleton with schema validation
- Build toy 3-locus CI subset (REQ-9)
- OSF pre-registration

#### Phase 1: coloc.susie fine-mapping spine
**Goal**: Replace coloc.abf with coloc.susie across the entire pipeline. SuSiE-RSS fine-mapping per trait x ancestry with explicit complex-region policy and sensitivity sweeps.
**Depends on**: Phase 0 (Track 0b)
**Requirements**: REQ-2
**Tier**: T1
**Success Criteria** (what must be TRUE):
  1. SuSiE-RSS fine-mapping completes for all trait x ancestry combinations
  2. config/susie_policy.yaml exists with explicit rules for convergence failures, L cap, min_abs_corr
  3. min_abs_corr sensitivity sweep (3+ values) reported for complex regions as supplementary table
  4. coloc.susie replaces coloc.abf in the pipeline (no coloc.abf calls remain)
  5. Per-locus fine-mapping QC report generated
**Plans**: 6 plans

Plans:
- [x] 01-01-PLAN.md — Wave 1: policy YAML + schema + run_susie_rss.R in-place mod (fit persistence + retry ladder + policy loader + D1/D2/D3 diagnostics + sweep) + 4 G3_complex rows + cache-clear + A6 dispatch test with runsusie fallback + finemap.smk multi-output
- [x] 01-02-PLAN.md — Wave 2: UKBB-LD tiled EUR panel (Weissbrod 2020) via boto3 + per-region NPZ→.rds + HLA block-diagonal flag
- [x] 01-03-PLAN.md — Wave 3: HGDP+1kG AFR LD panel (gnomAD v3.1.2) via anonymous HTTPS + bcftools + plink2 (pilot-scope fallback). Serialized after 01-02 — shares ld_reference.smk + pipeline.yaml + test_ld_panels.py
- [x] 01-04-PLAN.md — Wave 4: coloc.smk + run_coloc_susie.R + rename run_coloc.R → run_coloc_abf_legacy.R + rewire multitrait.smk
- [x] 01-05-PLAN.md — Wave 5: Quarto QC dashboard D1+D2+D3+D4+D6 with HLA red-flag styling + standalone REQ-2 supplementary sweep table
- [ ] 01-06-PLAN.md — Wave 6: filter_finemap_summary.py update + first REAL CI smoke + methods_fragment.md + OSF amendment (DOI 10.17605/OSF.IO/PVB5J)

Seeds: src/legacy/region_analysis/scripts/run_susie_rss.R, src/legacy/genome_wide/scripts/run_coloc_genomewide.R

#### Phase 2: 3-way QTL colocalization
**Goal**: Build the causal gene x tissue x cell-type matrix through eQTL, pQTL, sQTL, and sc-eQTL colocalization with rigorous threshold sweep and negative controls. Highest-leverage T1 phase.
**Depends on**: Phase 1, Track 0a DUAs (for pQTL)
**Requirements**: REQ-3, REQ-7
**Tier**: T1
**Success Criteria** (what must be TRUE):
  1. GTEx v8 eQTL coloc completed per tissue, cross-referenced to Open Targets Locus2Gene
  2. sQTL coloc (GTEx) completed
  3. PP.H4 threshold sweep across {0.5, 0.7, 0.8, 0.9} reported with tier counts per ancestry
  4. Negative controls (HLA, cosmetic, blood group gene sets) all null — PP.H4 < threshold
  5. Causal gene x tissue x cell-type matrix assembled
  6. Tier A/B/C confidence assignment with reported threshold dependence
**Plans**: 5 plans

Plans:
- [x] 02-01-PLAN.md — Infrastructure: liftover + config (pph4_thresholds.yaml, negative_controls.yaml, qtl_sources.yaml) + conda env + LPA/KIV-2 policy update + QTL test fixtures
- [x] 02-02-PLAN.md — GTEx v8 eQTL coloc backbone: download rules + harmonize_eqtl.py + tissue-N lookup + run_qtl_coloc.R + qtl_coloc.smk manifest dispatch
- [x] 02-03-PLAN.md — GTEx v8 sQTL + UKB-PPP pQTL: harmonize_sqtl.py + harmonize_pqtl.py + sdY estimation + download_ukbppp.py + extended download rules
- [x] 02-04-PLAN.md — OneK1K sc-eQTL (14 immune cell types): download + harmonize + manifest extension (broad trigger on all loci)
- [x] 02-05-PLAN.md — Negative controls (3 curated + matched nulls) + PP.H4 threshold sweep + tier A/B/C assignment + L2G concordance + gene-tissue matrix + methods fragment

Architecture: harmonize-then-unify. Per-source harmonization produces common intermediate TSV (variant_id, beta, se, maf, position, N, sdY, gene_id, tissue). One unified run_qtl_coloc.R consumes all sources.

#### Phase 5: Pathway + partitioned heritability
**Goal**: Formal pathway enrichment with proper nulls and partitioned heritability analysis. Replaces the ad-hoc enrichment from the original manuscript.
**Depends on**: Phase 1
**Requirements**: REQ-7
**Tier**: T1
**Success Criteria** (what must be TRUE):
  1. MAGMA gene-based + gene-set enrichment completed
  2. g:Profiler run with discoverability-matched null (per-trait background)
  3. LDSC partitioned heritability reported per pathway per trait
  4. LDSC-SEG tissue-specific heritability completed
  5. Negative-control pathway set is null (enrichment q > 0.05)
  6. Permutation null for colocalization gene list computed
**Plans**: 5 plans

Plans:
- [x] 05-01-PLAN.md — Wave 1: Infrastructure — 4 conda envs, custom pathway GMT sets, negative control GMT, sumstats_utils.py, build_magma_geneset.py, build_ldsc_annot.py, munge_sumstats_ldsc.py, pathway.smk skeleton, test scaffolding
- [x] 05-02-PLAN.md — Wave 2: MAGMA 3-step enrichment (annotate, gene-analysis, gene-set) + g:Profiler with discoverability-matched 5-trait union background
- [x] 05-03-PLAN.md — Wave 3: LDSC partitioned heritability (baseline v2.2 + custom annotations) + LDSC-SEG tissue-specific enrichment (GTEx 53-tissue + Roadmap chromatin) + LDSC-SEG negative controls
- [x] 05-04-PLAN.md — Wave 4: HESS/rho-HESS local genetic covariance per trait pair x ancestry + HESS negative controls
- [x] 05-05-PLAN.md — Wave 5: Negative control validation (all 5 methods) + 1000 permutation null gene sets (matched for length, LD, MAF) + cross-method aggregation + methods fragment

#### Phase 9: Replication in independent cohorts
**Goal**: Validate T1 findings in independent cohorts to establish reproducibility for the submission.
**Depends on**: Phases 1, 2; Track 0a DUAs (for FinnGen, MVP, AoU, BBJ)
**Requirements**: (none directly; supports overall validity)
**Tier**: T1
**Success Criteria** (what must be TRUE):
  1. At least 2 independent cohort replications completed (from FinnGen, GBMI, MVP, AoU, BBJ)
  2. Replication-adjusted effect sizes calculated
  3. Hold-out replication tables generated for supplementary material
**Plans**: 5 plans

Plans:
- [x] 09-01-PLAN.md — Wave 1: Infrastructure — envs (GCTA, r_coloc extended), config/replication_cohorts.yaml (4 cohorts × 5 traits), MVP phs001672 FTP enumeration, replication.smk skeleton (20+ rules), tests/phase9/ scaffolding (9 files)
- [x] 09-02-PLAN.md — Wave 2: Ingest + harmonize 4 cohorts — FinnGen R12 + GBMI + MVP + BBJ harmonizers with canonical 10-column schema + GRCh38→37 liftover + palindromic SNP exclusion
- [x] 09-03-PLAN.md — Wave 3: Replication manifest (signal × cohort crossmap per D-02/D-05) + run_replication_susie.R (reuses Phase 1 susie_policy.yaml) + run_fiqt.R (winnerscurse::FDR_IQT)
- [x] 09-04-PLAN.md — Wave 4: coloc.susie re-estimation with PP.H4 sweep {0.5,0.7,0.8,0.9} + per-cohort Bonferroni effect-size test + same-direction + post-hoc power + IVW meta (metafor)
- [x] 09-05-PLAN.md — Wave 5: COJO sensitivity (1000G EUR/AFR with N<4000 caveat) + master_table.tsv + cross_ancestry_generalization_tier_ab.tsv (BBJ Tier A+B only, D-05c) + replication_holdout_supplementary.tsv + methods fragment

#### Checkpoint #1: End of T1 spine
**Type**: Decision gate (not a phase)
**Depends on**: Phases 0, 1, 2, 5, 9 all complete
**Requirements**: REQ-11
**Produces**: .planning/checkpoints/T1_review.md with:
- Tier A signals that survived PP.H4 sweep + replication
- Ancestry-level power retention under matched-N preview
- Go/no-go decision for T2 with explicit evidence
- Submission target: AJHG (T1 alone) vs. Nat Genet pivot (proceed to T2)

**No T2 phase is planned until this file exists with a "go" verdict.**

**Status 2026-04-15:** Interim CP#1 issued at `.planning/checkpoints/T1_review.md` — code-complete conditional-go. T2 research + planning authorized in parallel with T1 first-production LSF launch. CP#1-final pending on first-production completion.

#### Phase 3: Mendelian randomization
**Goal**: Establish causal direction between all 10 unique trait pairs via bidirectional MR (20 directed tests) with robust weak-instrument mitigation for non-EUR ancestries, plus 3 MVMR mediation triangles.
**Depends on**: CP#1 (go verdict)
**Requirements**: REQ-4
**Tier**: T2 (gated)
**Success Criteria** (what must be TRUE):
  1. IVW + MR-Egger + weighted median triangulation completed for all trait pairs
  2. MR-PRESSO + MR-CAUSE outlier robustness applied
  3. MR-RAPS implemented for AFR and EAS with explicit ancestry-specific vs. trans-ancestry choice
  4. Weak-instrument diagnostic table (F-stat, I-squared, Q-stat) produced per ancestry per trait pair
  5. Bidirectional causal graph assembled
**Plans**: 5 plans

Plans:
- [ ] 03-01-PLAN.md — Infrastructure: config expansion (20 bidirectional + 3 MVMR), envs/r_mr.yml, manifest builder update, test scaffolding
- [ ] 03-02-PLAN.md — Instrument extraction: SuSiE CS lead SNPs + FIQT merge + allele recovery + complex-region flags + F-stat/I^2/Q-stat diagnostics
- [ ] 03-03-PLAN.md — Bidirectional MR: 5 methods (IVW, Egger, median, PRESSO, RAPS) + CAUSE genome-wide + Steiger flagging + diagnostic plots
- [ ] 03-04-PLAN.md — MVMR triangles (3 mediation paths) + trans-ancestry meta-MR (metafor FE + TEMR sensitivity)
- [ ] 03-05-PLAN.md — Aggregation: majority rule (3+/5) + Bonferroni + evidence matrix + causal graph (Figure 5) + methods fragment

Seeds: src/legacy/region_analysis/scripts/create_mr_design.py, src/snakemake/rules/mr.smk

#### Phase 4: Matched-N cross-ancestry concordance
**Goal**: Replace broken Table 2 with power-corrected cross-ancestry concordance using matched-N bootstrap.
**Depends on**: CP#1 (go verdict)
**Requirements**: (none directly; fixes Table 2)
**Tier**: T2 (gated)
**Success Criteria** (what must be TRUE):
  1. EUR down-sampled to match AFR N with 100x bootstrap concordance
  2. Expected detection probability under Hou et al. 2023 null computed
  3. LDSC cross-ancestry r_g calculated as global benchmark
  4. New Table 2 generated, replacing old incomparable-trait-pair comparison
**Plans**: 5 plans (04-01 scaffold+config, 04-02 bootstrap engine, 04-03 concordance metrics, 04-04 LDSC rg + Hou null, 04-05 assembly+smoke gate)

Plans:
- [x] 04-01-PLAN.md — Scaffold, config, Wave 0 test stubs, bmi.AFR dependency surface
- [x] 04-02-PLAN.md — Bootstrap engine (SE-inflation + SuSiE refit + coloc.susie per bootstrap)
- [x] 04-03-PLAN.md — Concordance metrics (Tier A retention + Jaccard + sign agreement)
- [x] 04-04-PLAN.md — LDSC 30-test r_g matrix + Hou-null detection probability
- [x] 04-05-PLAN.md — Smoke-pilot gate + Table 2 assembly + violin figure + supplementary outputs

#### Phase 8: Cross-ancestry PRS
**Goal**: Build and evaluate cross-ancestry polygenic risk scores with full calibration and clinical utility metrics, quantifying the equity-vs-accuracy trade-off.
**Depends on**: CP#1 (go verdict)
**Requirements**: REQ-6, REQ-8
**Tier**: T2 (gated)
**Success Criteria** (what must be TRUE):
  1. PRS-CSx training in EUR and transfer to AFR/EAS/Hispanic completed
  2. Pathway-restricted vs. genome-wide PRS comparison reported
  3. Discrimination metrics (R-squared, AUC, incremental C-statistic) produced per ancestry
  4. Calibration metrics (Hosmer-Lemeshow, slope, intercept, obs-vs-expected plot) produced
  5. Clinical utility metrics (NRI, DCA, net benefit) produced
  6. Equity-vs-accuracy trade-off quantified with explicit numbers for AFR/EAS/Hispanic vs. EUR
**Plans**: TBD

Seeds: src/legacy/region_analysis/scripts/create_pgs_manifest.py, src/legacy/region_analysis/workflow/rules/pgs.smk

#### Checkpoint #2: End of T2
**Type**: Decision gate (not a phase)
**Depends on**: Phases 3, 4, 8 all complete
**Requirements**: REQ-11
**Produces**: .planning/checkpoints/T2_review.md with:
- Are T1+T2 results a Nature Genetics story or a Nature Metabolism story?
- Is T3 worth the schedule risk?
- Updated journal target decision

**No T3 phase is planned until this file exists.**

#### Phase 6: Selection scans + polygenic selection
**Goal**: Test evolutionary medicine hypotheses with formal selection scans and polygenic selection tests. Pre-specified fallback framing required before execution.
**Depends on**: CP#2 (go verdict)
**Requirements**: REQ-5
**Tier**: T3 (gated)
**Success Criteria** (what must be TRUE):
  1. iHS, SDS, PBS, XP-EHH scans completed across 1000G + HGDP
  2. Pathway-level enrichment of selection signatures computed
  3. Pre-specified fallback framing exists in PLAN.md before first execution run
  4. Thrifty-gene and antagonistic-pleiotropy hypothesis tests completed
**Plans**: TBD

#### Phase 7: Single-cell + EpiMap + ABC
**Goal**: Cell-type-resolved regulatory integration using single-cell eQTL, chromatin state, and enhancer-gene models.
**Depends on**: CP#2 (go verdict)
**Requirements**: (none directly; adds mechanistic depth)
**Tier**: T3 (gated)
**Success Criteria** (what must be TRUE):
  1. Cell-type-resolved eQTL integration completed
  2. Roadmap/EpiMap chromatin state overlap analysis done
  3. ABC enhancer-gene linking model applied to credible-set variants
  4. CELLECT/scDRS enrichment computed
**Plans**: TBD

#### Phase 10: Deep-learning variant effect + MPRA overlap
**Goal**: Computational variant effect prediction and validation against experimental MPRA data.
**Depends on**: CP#2 (go verdict)
**Requirements**: (none directly; adds functional evidence)
**Tier**: T3 (gated)
**Success Criteria** (what must be TRUE):
  1. Enformer + Borzoi inference completed per credible-set variant
  2. Sei regulatory activity scores computed
  3. AlphaMissense coding-variant scores retrieved
  4. Overlap with public MPRA datasets (Abell 2022, Tewhey 2016) quantified
  5. Composite functional-evidence score produced per variant
**Plans**: TBD

#### Phase 11: Manuscript + figures + submission
**Goal**: Assemble the full manuscript with regenerated figures, methods rewrite, equity framing, cover letters, and submission package.
**Depends on**: Phase 9 (runs in parallel from Phase 9 onward)
**Requirements**: REQ-8, REQ-10
**Tier**: M (parallel)
**Success Criteria** (what must be TRUE):
  1. Figures 1-6 regenerated from new analytical data
  2. New Table 2 (matched-N) + regenerated Tables 1, 3
  3. Methods section rewritten — one subsection per analytical phase
  4. Equity-as-trade-off framing reconciled across abstract/intro/discussion (REQ-8)
  5. Cover letters written per target journal (REQ-10)
  6. GitHub repo public release + Zenodo DOI minted
  7. OSF final registration updated
**Plans**: TBD

### Progress

**Execution Order:**
T1: 0 → 1 → 2 → 5 → 9 → CP#1
T2 (if go): 3, 4, 8 → CP#2
T3 (if go): 6, 7, 10
M: 11 (parallel from Phase 9)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 0. Data access + infrastructure | 0/4 | Planning complete | - |
| 1. coloc.susie fine-mapping | 0/TBD | Not started | - |
| 2. 3-way QTL colocalization | 0/5 | Planning complete | - |
| 5. Pathway + partitioned h2 | 0/TBD | Not started | - |
| 9. Replication | 0/TBD | Not started | - |
| 3. Mendelian randomization | 0/5 | Planning complete | - |
| 4. Matched-N concordance | - | Gated (T2) | - |
| 8. Cross-ancestry PRS | - | Gated (T2) | - |
| 6. Selection scans | - | Gated (T3) | - |
| 7. Single-cell + EpiMap | - | Gated (T3) | - |
| 10. DL variant effect | - | Gated (T3) | - |
| 11. Manuscript | - | Not started | - |

## Progress (current milestone sequence)

| Milestone | Plans Complete | Status | Target end-month |
|---|---|---|---|
| M0 pivot scaffolding | 0/1 (this plan) | in flight | 2026-05 |
| M1 sumstats upgrade + harmonization | 6/6 | closeout PASS 2026-04-25; OSF amendment paste-ready | 2026-06 / 2026-07 |
| M2 LDSC + MTAG + CPASSOC | 1/6 (m2-00 Wave 0 complete 2026-04-26) | in flight; Wave 1 cleared | 2026-08 / 2026-09 |
| M3 AoU AFR LD build | not planned | gated on M2 region list | 2026-09 / 2026-10 |
| M4 scalable coloc + fine-mapping | not planned | gated on M3 + M2 | 2026-12 / 2027-01 |
| M5 variant→gene prioritization + novelty | not planned | gated on M4 Tier A | 2027-02 |
| M6 manuscript + replication + submission | not planned | gated on M5 | 2027-04 / 2027-05 |
| Track-A-finalization | Route A in flight; audit-V2 sweep landed 2026-04-27 (`260427-azv` — 12 atomic commits, 15 V2-CLOSED tracker rows, Fig S2 + frozen scalars + 3 DEC entries) | in flight (independent of M0–M6) | 2026-05 / 2026-06 |
| Track-A-R2-sh2b3-canonical-and-cache-refresh | 3/8 (W0 + W1 + W2 complete; W1.5 LD-audit landed 2026-04-29 alongside W2; W3 next = checkpoint:human-verify) | in flight; W2 SUMMARY 2026-04-29 (3 SURVIVE_GE_0.8 + 2 COLLAPSE_BELOW_0.5; PP.H4 BMI-HTN=1.0); W1.5 LD-audit demonstrates panel pathology (50.4% rank deficiency; 23.46% negative eigenvalues) substantively justifying DISCLOSE-AS-COLUMN; Pitfall 3 + Invariant 2 preserved; closes SH2B3 reference-LD coverage gap (Issue 1) + variant-ID matcher cache propagation (Issue 2) ahead of Genome Medicine R2 submission | 2026-05 / 2026-06 |

## Backlog (parking lot — 999.x)

Ideas captured for later triage; not scheduled. Promote via `/gsd-review-backlog`.

### 999.1 — LD NaN policy: off-diagonal NaN→0 + PSD regularization (pre-SuSiE conditioning) — ⚠ SUPERSEDED 2026-07-10 by m3-07

> **⚠ SUPERSEDED 2026-07-10 by the new m3-07 wave.** The NaN mechanism is RESOLVED (geometry verdict `4543dcf4…`, landed `5fd58a5`): region-1 NaN = overlapping-deletion **occlusion**, so there is **no "true r" to zero** → **NaN→0 is DEAD** and the §2-4 conditioning code (`condition_ld_matrix.py`, `f147041`) stays FROZEN/HELD (never fed to a fit); §5-6 here are dead (they conditioned on NaN→0). The correct fix is an **upstream overlapping-deletion span-filter + provenance manifest + present-rate scan** = the **m3-07** wave (roadmap line under m3, above). Retained for history; the `psd_utils.R` refactor it produced is sound and reused elsewhere.

**Captured:** 2026-07-04 (Seth carry-forward from quick-260703-vk9) · **Milestone:** M3/M4, pre-m3-04 · **Status:** §2-4 code LANDED `f147041` (m3 wave `m3-06-W6`) but ⚠ **ON SCIENTIFIC HOLD** 2026-07-07 — Seth peer review (arithmetic verified) REFUTES the NaN→0 premise: the NaN is not "pairwise-undefined r" (impossible at F_MISS≤0.05/MAF 0.005-0.02, P~10^-949 to 10^-3767) but a co-located variant-REPRESENTATION artifact (correlated missingness); NaN→0 is directionally wrong for high-LD adjacent variants. **GATE before any conditioned region feeds a fit = the in-perimeter 2×2 diagnostic on the 6 pairs** (egress 2×2 counts + variant IDs/positions only). Likely fix = UPSTREAM variant normalization (disclosed deviation + amendment-update), not downstream NaN→0. m3-06 code FROZEN; raw-panel NaN-RAISE stays. Needs a THIRD topology category (co-located → normalize, don't zero). · §5-6 PARKED (loop-gated)

> **PROMOTED + §2-4 EXECUTED 2026-07-07:** step 1 (OSF gate) is CLOSED (amendment posted 2026-07-04 as OSF file `tcujq`, recorded + verified; tag `AFR-NANPSD-OSF-AMENDMENT-POSTED-2026-07-04` on `0f3c68b`). **Steps §2-4** (NC-State conditioning code: shared `psd_utils.R`, `condition_ld_matrix` util, conditioned-artifact writer) were promoted to the **m3 wave `m3-06-W6-ld-nan-psd-conditioning`** inside `m3-aou-afr-ld-panel-build` (planner→executor pattern, matching m3-02b/c/d/e) and **EXECUTED + independently verified 2026-07-07** (landed `f147041`; TDD RED→GREEN; full `tests/m3` 360 passed/30 skipped; Track-A byte-identity 16/16 `identical()=TRUE` so r3/EUR numerics unchanged; frozen contracts git-diff-clean). **Steps §5-6** (fit-time wiring against the real AFR panel + in-perimeter region-1 verification) REMAIN PARKED here — **loop-gated** (the 276-region AoU LD loop is still running; the panel does not exist yet), to be promoted as a follow-on wave when the panel lands. Design detail below is the spec source for the wave. **PLANNED 2026-07-07:** the wave plan is written at `.planning/phases/m3-aou-afr-ld-panel-build/m3-06-W6-ld-nan-psd-conditioning-PLAN.md` (3 TDD tasks = §2/§3/§4; wave file id `m3-06`). §5-6 remain parked here.

The native-plink AFR LD panel emits `NaN` for a handful of pairwise `r` where the
pair's complete-sample intersection is degenerate (`0/0` among clustered low-MAF
variants — region 1 = 12 NaN across 11 index-adjacent rows in 5 tight bp windows; a
**pairwise-undefined `r`**, NOT a "plink bug"). `read_square_bin` now RAISES on any NaN
(correct — diagnostic + resume-safe, quick-260703-o0m). It does **not** yet REPAIR.

**Scope of the design pass (must NOT be folded into any Defect fix):** the recommended
policy (browser agent + Seth) is **off-diagonal `NaN→0` + PSD projection, NOT a variant
drop** — a downstream step in the `.npz`/`.rds` build or a dedicated pre-SuSiE
conditioning stage. Open decisions with real fine-mapping consequences:

- Zeroing a pairwise `r` asserts an independence you have **not measured**.
- PSD projection (e.g. nearest-PD / eigenvalue clip) perturbs the **whole** matrix.
- Record `n_zeroed` + provenance per region; decide the PSD method and where in the
  pipeline it runs.

Until this lands, a loop re-fire still (correctly) raises on the NaN cells. This is the
**true region-1 substrate fix**; Defect 1 (the snplist race, quick-260703-vk9) is
orthogonal and already landed.

**Refs:** `quick/260703-vk9-.../260703-vk9-SUMMARY.md` · quick-260703-o0m · STATE.md
2026-07-04 block.

---

#### 999.1 design detail (Seth, 2026-07-04) — resolved OSF finding + work breakdown

**Reuse, do not reinvent — PSD machinery already exists.**
`src/R/regularization/refit_sh2b3_psd_regularized.R` already implements
`psd_regularize_ridge(R, λ)` (Wen 2017: `R + λI`, then row/col normalize) and
`psd_regularize_eigclip(R, λ_floor=1e-6)` (Hutchinson 2020: eigen-clip negatives,
reconstruct, normalize), applied at SuSiE-RSS fit time on the credible-set submatrix
`R_sub`. 999.1 must NOT add a third PSD implementation — factor these two into a shared
`src/R/regularization/psd_utils.R` that both the EUR refit and the AFR native panel
source.

**NaN topology locks the policy (region-1 in-perimeter diagnostic, aggregate egress).**
`n_var=102421`, 12 NaN cells, 11 rows, **0 fully-NaN rows** — isolated symmetric
off-diagonal pairs between index-adjacent low-MAF variants (MAF 0.005–0.02, F_MISS
≤0.05, no all-het), clustered in 5 tight bp windows. This is **pairwise-undefined `r`**
(`0/0` on that pair's complete-sample intersection), NOT a zero-variance source and NOT
a confirmed plink bug. Policy: **off-diagonal `NaN→0` + PSD conditioning, per-region
provenance — NOT a variant drop.** A DIFFERENT topology (a fully-NaN row →
`nan_variant_indices` non-empty) WOULD be a zero-variance source and SHOULD be dropped
by MAF/missingness QC; the conditioning util must branch on topology.

**Where in the pipeline.** `NaN→0` at an explicit, recorded conditioning stage (raw
panel `.npz` stays NaN-raising + auditable; conditioned artifact is separate). PSD stays
at fit time on the region submatrix — a full 102421² eigen needs ~195 GiB working set
(VM 120 GB) + ~8 h/region, infeasible. Order is fixed by correctness: `eigen()` returns
all-NaN on any NaN input, so **NaN→0 first, PSD (on the submatrix, later) second**;
zeroing off-diagonals can introduce mild indefiniteness that the downstream PSD then
repairs.

**OSF gate — RESOLVED: a NEW amendment is required.** `osf-amendment-r3-2026-05-04.md`
is **EUR-only** — it pre-registers PSD for the "1000 Genomes Phase 3 EUR LD matrix at
`data/processed/ld_reference/EUR/SH2B3_12q24.rds`" (ridge λ∈{0.001,0.01,0.1} + eigclip
λ_floor=1e-6), SH2B3 + 4 EUR regions, and its "what is not changing" clause pins the
substrate to the EUR reference panel. No AFR, no All-of-Us native panel, no NaN→0
step. The PSD methods are reusable; their pre-registration coverage is NOT. 999.1 needs
a **new OSF amendment** (or a scoped amendment-update citing r3's record at
`osf.io/az52u`) pre-specifying: AFR native-panel scope + ancestry, the NaN→0 policy +
`n_zeroed` ceiling, the PSD method + λ (pre-specified, not tuned), and — mirroring r3 —
the allowable outcome branches. Carter posts to OSF; the agent side only DRAFTS the
paste-ready text. This is the TRUE blocker on 999.1 promotion — the code is small; the
governance is the gate. Draft the amendment BEFORE writing conditioning code so the
pre-specified parameters lock before any fit can back-influence them.

**Fine-mapping caveats (must appear in the methods writeup, not buried):**
(1) Zeroing a pairwise `r` asserts an independence not measured — negligible in
aggregate for 12/102421², but if two zeroed variants fall in the SAME credible-set
region the local LD is misspecified there; flag those regions + report PIP sensitivity
with/without. (2) PSD renormalizes the WHOLE submatrix, not just zeroed cells — record
`max|R_reg−R|` + min-eigenvalue before/after per region. (3) λ/method is a researcher
degree of freedom — pre-specify in the amendment; default eigclip λ_floor=1e-6 (least
aggressive) unless a pre-registered sweep says otherwise.

**Work breakdown (for /gsd-plan-phase when promoted):**
1. **OSF gate (BLOCKS all below)** — draft the new AFR amendment (NaN→0 policy,
   `n_zeroed` ceiling, PSD method+λ pre-spec, AFR panel scope, outcome branches);
   Carter posts; record record-URL + timestamp in `.planning/osf_deviations.md`.
2. **Refactor PSD** — extract `psd_regularize_ridge`/`_eigclip` → `psd_utils.R`;
   regression-test byte-identical to current `refit_sh2b3_psd_regularized.R` output
   (pure refactor, no behavior change).
3. **NaN→0 conditioning util (Python)** — `condition_ld_matrix(m, policy, record)`:
   topology branch (RAISE→drop on fully-NaN rows; zero on isolated pairs), `n_zeroed`
   ceiling (RAISE if exceeded — large NaN fraction is a substrate problem, re-diagnose),
   provenance. Failing-first tests: isolated-pair zeros+records; fully-NaN-row RAISES;
   over-ceiling RAISES.
4. **Conditioned artifact** — write conditioned `.npz`/`.rds` with provenance keys
   (`n_zeroed`, `zeroed_pairs`, `nan_policy`, `psd_method`, `psd_lambda`); leave the raw
   panel `.npz` contract frozen (`ld_npz_to_rds.R` unchanged).
5. **Fit-time wiring + diagnostics** — AFR fit sources `psd_utils.R`; record
   `lambda_method`/`lambda`/`max|R_reg−R|`/min-eigenvalue per region + the credible-set-
   overlap flag & PIP sensitivity for regions containing a zeroed pair.
6. **Verification** — on region-1's real 12-NaN matrix (in-perimeter, aggregate egress):
   conditioned matrix finite + PSD (min-eig ≥ 0), `n_zeroed==6`, downstream SuSiE
   converges. Egress only aggregate diagnostics.

**Do-NOTs:** not folded into any Defect 1/3/4 fix (landed, orthogonal); no loop re-fire
until §1–6 land (`read_square_bin` correctly still raises); no full-panel PSD (O(n³));
no tuning λ/method to a fine-mapping result.

**Refs (design):** Seth ticket `ticket_999_1_nan_psd_design.md` (Science-side artifact,
2026-07-04) · `osf-amendment-r3-2026-05-04.md` (read in full, EUR-only) ·
`src/R/regularization/refit_sh2b3_psd_regularized.R`.
