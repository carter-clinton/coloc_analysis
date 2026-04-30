# Phase ta-sh2b3-canonical-and-cache-refresh: Track A R2 (id-vs-ref-LD) — Context

**Gathered:** 2026-04-28
**Status:** Ready for planning
**Slug:** ta-sh2b3-canonical-and-cache-refresh
**Discuss round:** R1 (power-mode; Carter accepted all 13 recommended defaults 2026-04-28T22:42:00-04:00; see [ta-sh2b3-DISCUSSION-LOG.md](./ta-sh2b3-DISCUSSION-LOG.md) for option-by-option audit trail)
**Project handle:** Track A is nicknamed `id-vs-ref-LD` (locked 2026-04-28; memory `project_track_a_handle.md`). The publication is original hypothesis-driven research on identity-LD vs reference-LD colocalization at curated cardiometabolic pleiotropy loci. Target ladder: *Genome Medicine* → *AJHG* short-report → *Bioinformatics* Applications Note. Existing in-tree paths still contain pre-rename tokens — see D-TA-06.

<domain>
## Phase Boundary

Track A R2 phase closing two open *Genome Medicine* manuscript issues ahead of resubmission. The frozen submission bundle at commit `cacdbfe` (`quick-260427-vbq`, 4.19 MB / 53 entries) is the state being rebased on; no narrative writes happen until disk numbers are frozen at Wave 5.

**In scope:**
- **Issue 1 — SH2B3 EUR canonical-pair reference-LD coverage** — close audit-V2 §HQ#2(i) + HQ#2(ii) + HQ#2(iii):
  1. Re-fit non-converged SH2B3 EUR per-trait SuSiE-RSS at expanded L (L-sweep {15, 20, 30} pre-registered supplementary; **D-TA-02**) for BMI + hypertension + stroke; verify `n_CS << L` per Zou et al. 2022 §Discussion
  2. Run coloc.susie on **9 new SH2B3 EUR trait-pairs** (full lattice minus already-on-disk `asthma_vs_t2d`; **D-TA-03**) against converged fits
  3. `checkpoint:human-verify` (Wave 3) — Carter selects honest 3-branch outcome (collapse / partial / survive) from disk numbers BEFORE narrative writes; thresholds are standard manuscript Tier B/A (collapse <0.5 / partial 0.5–0.8 / survive ≥0.8; **D-TA-Wave3-thresholds**)
  4. Audit-V2 §HQ#2(ii) headline-numerator decision (51/96 vs 33/96 vs hybrid) deferred to **post-Wave-1 from observed convergence outcome** (**D-TA-Wave1-headline**)
- **Issue 2 — variant-ID matcher cache propagation refresh** — close audit-V2 §Eval 3.2:
  1. Wave 0 SuSiE-RSS variant-ID format diagnostic (read 3 SuSiE-RSS fit JSONs at `results/fine_mapping/susie/*.json`) drives cache-layer scope decision (**D-TA-04 diagnostic-driven**)
  2. QTL-coloc cache invalidation (`mv results/qtl_coloc results/qtl_coloc.preFix.bak`); Snakemake re-fire `--use-conda -j 50` (~10 hr at 50 cores). SuSiE-RSS layer re-fire conditional on Wave-0 diagnostic (~5 hr extra)
  3. Verification: `too_few_snps` count drops materially from 1,005 (PASS ≤ 200; FAIL ≈ 1,000 → SuSiE-RSS layer root-cause investigation triggered, do NOT proceed to Wave 6)
- **Downstream aggregator + figure refresh against post-refresh disk numbers** — `scripts/python/aggregate_qtl_coloc.py`, `scripts/R/aggregators/`, `fig_h3_ld_overlap_dose_response.R` (Fig S7 dose-response), Table 1 builder, Tier-assignment script, Pathway-disclosure aggregator
- **Wave 6 manuscript narrative atomic updates** per Wave-3 branch + Wave-5 refreshed numbers (Methods, Results, Discussion, Limitations, Abstract, Conclusion-1, captions, tables, plus SH2B3-specific paragraphs in `docs/manuscript/track_a_pivot.md` — pre-rename path)
- **id-vs-ref-LD nickname rename** bundled in Wave 6 (**D-TA-06 + D-TA-Wave-6-timing**):
  - `docs/manuscript/track_a_pivot.md` → `docs/manuscript/id-vs-ref-LD.md`
  - `.planning/amendments/TRACK-A-PIVOT.md` → `.planning/amendments/ID-VS-REF-LD-STRATEGY.md`
  - `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` — **NOT renamed** (TRACK-A- prefix preserved per Carter's flag; widely cross-referenced)
  - `bin/build_track_a_submission_bundle.sh` → `bin/build_id_vs_ref_ld_submission_bundle.sh` (lowercase snake_case matches rest of `bin/`)
  - Plus all intra-doc references in R figure-builders, aggregators, locked-scalar block headers, R-script headers, plot_annotation, Track-A SUMMARY, README pointers, OSF cross-references, STATE.md / DECISIONS.md forward references, test fixtures
- **Wave 7 phase closeout** — SUMMARY.md per plan + verification dimensions D1–DN PASS/WARN/FAIL JSON + new submission bundle build via `bin/build_id_vs_ref_ld_submission_bundle.sh` (post-rename) + SHA-256 manifest update + OSF deviation log entry at `osf.io/az52u`

**Out of scope (deferred to other phases):**
- MAXIMUM cross-region replication (FTO_16q12 EUR + MC4R_18q21 EUR + APOE_19q13 + CXADR_F2RL1_6p21 against post-L=20 fits) — would be its own phase
- Threshold-lowering to 0.3 to surface FTO Tier-C 0.3099 (rejected during quick-260427-e8n; would require OSF amendment + manuscript-wide threshold rewrite)
- M2-POST-M3-08 mtCOJO re-fire (~6.5 hr long-queue) — Terminal A capacity, file-disjoint
- Sumstats Route C manual-fetch refresh — Terminal A capacity, file-disjoint
- UKB EUR augmentation, M3 AoU AFR LD pipeline, M2 LDSC + MTAG + CPASSOC — Track B M-series milestones, scientifically independent

**Gating in:**
- Submission bundle commit `cacdbfe` frozen checkpoint (already on disk)
- Code fixes already committed in current branch: `069b34f` (run_qtl_coloc.R chr:pos tolerance) + `7d54183` (run_susie_rss.R LD-panel-rsid override) — Wave 0 verifies both reachable from HEAD via `git merge-base --is-ancestor`
- OSF pre-registration coverage verified (Wave 0 task; **D-TA-05**)

**Gating out:**
- Wave 7 closeout produces a new submission bundle (post-rename builder; post-cache-refresh numerics; post-canonical-pair coloc.susie; post-Wave-3 narrative branch). Carter takes the new bundle to *Genome Medicine* journal portal for resubmission.

</domain>

<inputs>
## Inputs Available from Prior Work

**Frozen submission bundle (commit `cacdbfe`, `quick-260427-vbq`, 2026-04-28):**
- 4.19 MB / 53 entries; `unzip -t` clean; `track_a_genome_medicine_submission.zip` + `build_log.txt` (96 KB `set -x` trace + EXIT_CODE=0 footer)
- 4 root metadata files (README + LICENSE-CODE MIT + LICENSE-MANUSCRIPT-AND-DATA CC-BY-4.0 + CITATION.cff with `orcid: TODO`)
- 3 manuscript files (`track_a_pivot.md` source + `track_a_pivot.html` rendered + `minimal.css`)
- 14 figure files (Figs 1A/1B/2/3/5 + S7 + S2)
- 10 supplementary (9 TSVs from `results/track_a_aggregations/` + `TRACK-A-FROZEN-NUMBERS.md`)
- 13 scripts (3 R aggregators + 7 R figs + 3 Python aggregators)
- This bundle is **not modified during Issues 1+2 work**; a new bundle is built at Wave 7 from post-refresh artifacts

**Code fixes already committed in current branch (Issue 2 substrate):**
- `069b34f` — `run_qtl_coloc.R` extended to tolerate chr:pos-formatted variant IDs
- `7d54183` — `run_susie_rss.R` LD-panel-rsid override
- Wave 0 task: `git merge-base --is-ancestor 069b34f HEAD && git merge-base --is-ancestor 7d54183 HEAD` — both must return 0 (ancestor) before Wave 4 fires; cherry-pick if not on current branch

**Phase 1 SuSiE-RSS outputs (Issue 1 substrate):**
- `results/fine_mapping/susie/*.json` per-fit JSONs + `results/fine_mapping/susie/*.rds` per-fit binaries
- `results/fine_mapping/finemap_summary.tsv` md5-locked Stage 2 manifest (51 / 96 non-empty real-LD CS)
- 3 of 5 SH2B3 EUR per-trait fits non-converged at L=10 / niter=100: BMI, hypertension, stroke; identity-LD hypertension carries `L_saturated=TRUE` per `IDENTITY-LD-K2D-FIT-SUMMARY.tsv`
- Wave 1 re-fits BMI + hypertension + stroke at L-sweep {15, 20, 30}; verify `n_CS << L` per Zou et al. 2022 §Discussion

**Phase 2 Stage 2 real-LD coloc.susie outputs (Issue 1 substrate):**
- `results/multitrait/coloc_summary.tsv` md5 `5fa3c4004970c5da711d05947cb1f7d2` (28 attempted trait-pair rows, all PP.H4 columns empty under real-LD)
- Already on disk at SH2B3 EUR: `SH2B3_12q24__EUR__asthma_vs_t2d` only
- Wave 2 fires coloc.susie on the 9 new SH2B3 EUR pairs against Wave-1 converged fits

**Phase 2 QTL-coloc cache (Issue 2 invalidation target):**
- `results/qtl_coloc/` — 1,274 attempts; status distribution 1,005 `too_few_snps` + 32 `success` + 235 `no_qtl_cs` + 2 `qtl_susie_failed`
- Wave 4 backs up to `results/qtl_coloc.preFix.bak` and re-fires Snakemake under `--use-conda -j 50`

**Honest-framing-lock chain (must be preserved verbatim across all anchor points; see memory `feedback_original_research_framing.md`):**
- `docs/manuscript/track_a_pivot.md` L148 (§3.4 SH2B3 case-study reframe)
- `docs/manuscript/track_a_pivot.md` L295 (Figure 2 caption SUPERSEDED block)
- `docs/manuscript/track_a_pivot.md` L220 (Discussion §Identity-LD Inflation)
- `docs/manuscript/track_a_pivot.md` L90 (Methods §Harmonization-Pipeline Diagnostics)
- R-script headers (e.g., `src/R/figures/fig2_cs_yield.R` L10-17 SUPERSEDED attribution)
- Locked-scalar block (per quick-260427-e8n LIVE block in `TRACK-A-FROZEN-NUMBERS.md`)
- `plot_annotation` calls in figure scripts (e.g., `fig3_sh2b3_eur_collapse_forest.R`)
- `quick/260425-1vy-track-a-figures-1a-3/260425-1vy-SUMMARY.md`

**Numerics source-of-truth (read-only during Waves 1–4; updated at Wave 5):**
- `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` — single source of truth for manuscript abstract/results/tables/OSF amendment; any Stage 2 re-run that changes these numbers updates this file FIRST then propagates downstream
- `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` — canonical CS-yield summary (96 rows; never rewritten; per DEC-2026-04-25-01)

**Reusable LSF infrastructure:**
- `bin/fire_phase2_stage2_refit.sh` — Stage 2 production fire driver (proven 2026-04-22; produced the 51/96 numerator)
- `scripts/fire_identity_ld_rerun.sh` — k2d 2026-04-24 identity-LD re-fire driver (committed `08beb4c`)
- `bin/bsub_wrapper.sh` — LSF queue dispatcher (memory `feedback_lsf_queues.md`: serial=5760 min wall, long=14400, standard=2880; `LSF_UNIT_FOR_LIMITS=GB`)
- LSF env constraint: `serial` queue + `la_multitrait_r` conda env at `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/` for SuSiE-RSS + coloc.susie work; SuSiE-RSS re-fits estimated ~2–4 hr wall time per AUDIT-RESPONSE 2026-04-26 line 260
- Python invocation discipline: NEVER use miniconda3 base (Python 3.13); use `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` (Snakemake 7.32.4 + Python 3.11) or `--use-conda` flag (memory `project_python_311_pin.md`)

**Audit closure record:**
- `.planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md` — single-document catalogue of all 27 audit items with status + commit pointers
- HQ#2(i) + HQ#2(iii) currently DEFERRED-COMPUTE (this phase fires them)
- HQ#2(ii) currently DEFERRED-DESIGN (Wave 3 / Wave 6 narrative decisions)
- Eval 3.2 (78.9 % QTL-coloc failure) PARTIALLY-CLOSED via prose anchors at L90 + L220 + L244 (commits `06b817b`, `21900ba`, `09c68e5`); structural cache invalidation deferred to this phase

</inputs>

<decisions>
## Locked Decisions (Carter accepted all 13 recommended defaults 2026-04-28)

### D-TA-01: Source repo absolute path on cluster

**Decision:** All Wave 0 + Wave 1 + Wave 2 + Wave 4 LSF compute uses `/rs1/researchers/c/ckclinto/coloc_analysis/` as the canonical repo path. The GPFS interactive mount `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/` is the same physical filesystem and may be used for pre-fire git work, but every `bsub` / Snakemake invocation passes the `/rs1/...` path explicitly.

**Alternatives considered:** (b) `/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/` — GPFS mount path; functionally equivalent same filesystem; less established at LSF dispatch. (c) `/share/clintonlab/ckclinto/coloc_analysis/` — only if a /share/ mirror exists for login02.

**Why:** Consistent with all prior LSF fires per `.planning/STATE.md` L175 (Phase 0 smoke_dev at `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/`) + L588 (deCODE pQTL ingest at `/rs1/researchers/c/ckclinto/coloc_analysis/data/raw/decode_pqtl/`) + the submission-bundle build script's hard-coded conda-pandoc path `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/bin/pandoc`. 4+ prior fires all on `/rs1/...`. Build host `login02.hpc.ncsu.edu` is one of several login nodes (login03 used for prior Stage 1d narrow-validation tests per `.planning/debug/stage2_narrow_validation/SH2B3_12q24_test.log`); the actual repo path is independent of which login node the user is on.

**How to apply:**
- Wave 0 verification task: `[ -d /rs1/researchers/c/ckclinto/coloc_analysis/.git ] && cd /rs1/researchers/c/ckclinto/coloc_analysis && git rev-parse HEAD` should return the same commit SHA visible from the GPFS interactive shell.
- All `bsub` invocations in Waves 1–4 use absolute `/rs1/...` paths in `--cwd`, `-o`, `-e`, and any in-script path references.
- Snakemake `--directory` flag (if used) gets the `/rs1/...` path.
- README pointers and `.planning/intel/` entries documenting the build host should mention both paths (interactive GPFS mount + canonical LSF `/rs1/...` path).

### D-TA-02: L value for SH2B3 EUR per-trait SuSiE-RSS re-fits

**Decision:** L-sweep {15, 20, 30} as the Wave 1 pre-registered supplementary fire. Re-fit BMI + hypertension + stroke at all three L values; report `n_CS` per fit for each L; verify `n_CS << L` at the chosen primary-result L (most likely L=20 if no saturation observed at L=15). The L-sweep delivers explicit sensitivity evidence for the Supplementary Methods table per Zou et al. 2022 §Discussion.

**Alternatives considered:** (a) L=20 single-shot — simplest; ~3× compute; risk of an L=20 saturation requiring a separate Wave-1.5 re-fire. (c) L=20 with conditional-extension to L=30 if any fit returns `n_CS = L` — adaptive; ~3× to ~6× compute; less defensible at peer review than a pre-registered sweep.

**Why:** Already pre-registered as a follow-on supplementary analysis in `docs/manuscript/track_a_pivot.md` Methods §Fine-Mapping Configuration. The audit-V2 reviewer's specific recommendation (HQ#2 §(i)) was "report whether `n_CS << L`" — a sweep explicitly tests this. Compute cost (~9× over L=10 baseline; ~12-15 hr LSF total on `serial` queue with `la_multitrait_r` env per AUDIT-RESPONSE line 260 estimate) is acceptable given the rigor mandate (Carter command-args: "no cutting corners; rigorous options over time-saving options"). OSF pre-reg coverage to be verified in Wave 0 per **D-TA-05**.

**How to apply:**
- Wave 1 task: re-fit BMI + hypertension + stroke at L=15, L=20, L=30 (3 traits × 3 L values = 9 fits). Reuse existing `bin/fire_phase2_stage2_refit.sh` driver pattern; LSF dispatch at `serial` queue with `la_multitrait_r` env.
- Convergence verification: per-fit JSON must report `n_CS < L` at each L value (i.e., n_CS ≤ 14 at L=15, ≤ 19 at L=20, ≤ 29 at L=30). If any L=20 fit returns n_CS = 20 (saturation), the L=30 sweep value is the primary-result L.
- Output the sweep as a Supplementary Methods table at Wave 6: rows = trait (BMI/HTN/stroke); columns = L=15 / L=20 / L=30 with `n_CS` + `convergence_status` per cell.
- Wave 6 narrative: cite Zou et al. 2022 §Discussion `n_CS << L` non-saturation criterion verbatim.

### D-TA-Wave1-headline (audit-V2 §HQ#2(ii) DEFERRED-DESIGN closure)

**Decision:** The 51/96 yield headline numerator decision is **deferred to post-Wave-1 from observed convergence outcome**. After Wave 1's L-sweep produces convergence-status results for the 3 SH2B3 EUR non-converged traits, the empirical outcome dictates Wave 6 prose:
- If all 3 SH2B3 EUR traits converge at the chosen L → recompute headline numerator from `(51 + Wave-1 newly converged - Wave-1 newly empty)/96`
- If some still don't converge → surface non-convergence as a separate disclosure column (analogous to Fig 3 disclosure sub-table); keep 51/96 with explicit caveat
- Plan must NOT pre-commit to a numerator value before Wave 1 fires.

**Alternatives considered:** (b) Keep 51/96 with caveat regardless of L=20 outcome — lowest manuscript-edit footprint; least responsive to new evidence. (c) Drop non-converged from numerator regardless — most rigorous but commits Wave 6 to 33/96 baseline before evidence lands.

**Why:** Matches the honest-framing-lock principle of disk-then-narrative. Audit-V2 Eval 2(a) flagged "non-convergence treated as data" as the issue — the right response is to first determine whether non-convergence is solved at L=20+ and then report the empirical outcome, not pre-commit to a framing. AUDIT-RESPONSE 2026-04-26 line 280 confirms this is "a framing choice that materially shifts the Abstract / Headline Result / Fig 2 / TRACK-A-FROZEN-NUMBERS.md LIVE block — not a routine prose edit".

**How to apply:**
- Wave 1 SUMMARY.md must report per-trait convergence-status outcomes at chosen L explicitly; do NOT update headline numerator in Wave 1.
- Wave 6 task: based on Wave 1 + Wave 2 outcomes, EITHER recompute 51/96 → updated value (then update Abstract + §Headline + Fig 2 caption + TRACK-A-FROZEN-NUMBERS.md LIVE block + Conclusion-1) OR add non-convergence disclosure column (then update Limitations bullet + Methods §Fine-Mapping Configuration without touching the 51/96 headline).
- Decision recorded as `D-TA-WAVE1-HEADLINE-XX` in CONTEXT.md addendum after Wave 1 completes.

### D-TA-03: Canonical-pair coloc.susie scope

**Decision:** Wave 2 fires coloc.susie on **9 new SH2B3 EUR trait-pairs** (full SH2B3 EUR trait-pair lattice minus already-on-disk `asthma_vs_t2d`):
- `asthma_vs_bmi`
- `asthma_vs_hypertension`
- `asthma_vs_stroke`
- `bmi_vs_hypertension` (canonical literature claim)
- `bmi_vs_stroke`
- `bmi_vs_t2d`
- `hypertension_vs_stroke` (canonical literature claim)
- `hypertension_vs_t2d`
- `stroke_vs_t2d`

This symmetrizes the Table 3 SH2B3 row with FTO_16q12 (which has all 10 pairs in the Stage 2 manifest). Both BMI–HTN and HTN–stroke (the two canonical literature pairs at PP.H4 = 1.00 under Stage 1d identity-LD) are included.

**Alternatives considered:** (a) MINIMUM — BMI–HTN + HTN–stroke only (2 new pairs) — half the LSF compute but Table 3 SH2B3 row remains asymmetric vs FTO_16q12; reviewer-bait. (c) MAXIMUM — also re-fire FTO_16q12 EUR + MC4R_18q21 EUR + APOE_19q13 + CXADR_F2RL1_6p21 against post-L=20 fits — over-scopes the manuscript ask; pushes total compute to ~25× single-pair; would itself become a separate phase.

**Why:** Symmetric Table 3 row across SH2B3 and FTO_16q12 is methodologically cleaner. Manuscript already discusses pleiotropic-hub framing across 8 published-literature hubs (KCNJ11/ABCC8, NEGR1, APOE, FTO, MC4R, SH2B3, PPARG, SEC16B); presenting only 2 pairs at SH2B3 vs 10 at FTO is internally inconsistent. Wave 2 LSF compute scales linearly with pair count (~2 hr per pair on `serial` queue with `la_multitrait_r` env, conservatively ~18 hr for 9 pairs).

**How to apply:**
- Wave 2 PLAN.md task list: 9 explicit `bsub` jobs (one per trait-pair × L=primary-result-from-Wave-1).
- Reuse existing `bin/fire_phase2_stage2_refit.sh` pattern for the dispatch driver.
- Output: `results/multitrait/coloc_summary.tsv` gets 9 new rows appended (or a parallel `results/multitrait/coloc_summary_R2.tsv` if Stage 2 md5 byte-identical preservation rule prohibits in-place edit; planner decides at Wave 2).
- Per-pair JSON outputs at `results/multitrait/SH2B3_12q24__EUR__{trait1}_vs_{trait2}.json` for downstream Wave 3 reading.

### D-TA-Wave3-thresholds: PP.H4 outcome-branch threshold for human-verify gate

**Decision:** Wave 3 `checkpoint:human-verify` uses standard manuscript Tier B / Tier A thresholds verbatim:
- **(a) Collapse**: BMI–HTN reference-LD `PP.H4 < 0.5`
- **(b) Partial**: `PP.H4 ∈ [0.5, 0.8)`
- **(c) Survive**: `PP.H4 ≥ 0.8`

The decision is recorded as `D-TA-WAVE3-OUTCOME-XX` in CONTEXT.md addendum after Wave 2 completes (Carter selects the branch from observed disk numbers BEFORE narrative writes in Wave 6).

**Alternatives considered:** Lower bar (collapse <0.3 / partial 0.3–0.7 / survive ≥0.7) — would surface FTO Tier-C 0.3099 signal as "partial"; requires OSF amendment; changes manuscript-wide threshold framing. Higher bar (collapse <0.5 / partial 0.5–0.95 / survive ≥0.95) — matches PP.H4 = 1.00 identity-LD claim more strictly; tests near-perfect colocalization under matched-LD.

**Why:** Manuscript currently uses Tier B = 0.5 / Tier A = 0.8 throughout; quick-260427-e8n explicitly rejected threshold-lowering as out of scope. Standard thresholds preserve Wave 6 narrative consistency without requiring a separate manuscript-wide threshold rewrite or OSF amendment. AUDIT-RESPONSE TRACK-A-FROZEN-NUMBERS L143 "Threshold preservation" anchors this principle.

**How to apply:**
- Wave 3 PLAN.md task: present BMI–HTN PP.H4 + HTN–stroke PP.H4 + the 7 other new pairs' PP.H4 values from Wave 2 outputs to Carter; Carter selects branch (a/b/c) for the BMI–HTN canonical pair specifically.
- Plan must NOT pre-commit to a branch outcome.
- Wave 6 narrative branches (per **D-TA-Wave3-thresholds**):
  - (a) Collapse: §SH2B3 case-study reframe at L148 anchors on "canonical claim does NOT survive matched-LD"; flagship demonstrated collapse. Strongest finding; Discussion §Identity-LD Inflation is load-bearing
  - (b) Partial: pivot to "magnitude of inflation, not categorical"; calibration finding. Both Discussion §Identity-LD Inflation and §SH2B3 case-study get rewrites of comparable weight
  - (c) Survive: SH2B3 anchor flips from "collapse" to "validated"; manuscript headline narrows but Fig S2 structural-inflation finding + FTO Tier-C disclosure still load-bearing as fallback narratives

### D-TA-04: Cache-layer scope for Issue 2 re-fire

**Decision:** **Diagnostic-driven** — Wave 0 reads 3 SuSiE-RSS fit JSONs at `results/fine_mapping/susie/*.json` (sample across regions to avoid single-locus bias) and inspects the `variant_ids` field:
- If **rsid format** (e.g., `rs3184504`) → SuSiE-RSS layer is post-`7d54183`; re-fire **QTL-coloc only** (~10 hr at 50 cores)
- If **chr:pos format** (e.g., `12:111884608`) → SuSiE-RSS layer is pre-`7d54183`; re-fire **both layers** (~15 hr total: ~5 hr SuSiE-RSS + ~10 hr QTL-coloc)
- If **mixed format across the 3 sampled JSONs** → escalate to CONSERVATIVE-BOTH (re-fire both layers regardless)

**Alternatives considered:** (b) CONSERVATIVE-BOTH — re-fire both layers regardless to eliminate cache-staleness as a confounder (~5 hr extra LSF unconditionally). (c) FAST-QTL-ONLY — re-fire only QTL-coloc; if Wave 4 PASS criterion fails, fallback to a Wave 4.5 SuSiE-RSS re-fire (round-trip overhead).

**Why:** Most efficient — only does work that's needed. Wave 0 SuSiE-RSS variant-ID format diagnostic is cheap (~5 min reading 3 JSONs) and unambiguously dictates the right scope. Mixed-format escalation to CONSERVATIVE-BOTH covers the edge case (some pre-fix + some post-fix fits) without requiring a Wave 4.5 round-trip.

**How to apply:**
- Wave 0 task `Diagnostic-SuSiE-RSS-format`: read `results/fine_mapping/susie/SH2B3_12q24__EUR__bmi.json`, `results/fine_mapping/susie/FTO_16q12__EUR__bmi.json`, `results/fine_mapping/susie/SH2B3_12q24__EUR__hypertension.json` — inspect `variant_ids[0]` per fit; record outcome in CONTEXT.md addendum as `D-TA-04-DIAGNOSTIC-XX`.
- PLAN.md must include both code paths (rsid → QTL-coloc only; chr:pos → both layers; mixed → CONSERVATIVE-BOTH) and an explicit Wave-0 diagnostic gate that picks the right path before Wave 4 fires.
- Wave 4 PASS criterion: `too_few_snps` count drops materially from 1,005 baseline (target ≤ 200; `success` + `no_qtl_cs` counts rise correspondingly).
- Wave 4 FAIL criterion: `too_few_snps` stays ~ 1,000 → SuSiE-RSS layer was the actual problem; root-cause investigation triggered, **do NOT proceed to Wave 5/6**. Wave 4.5 fallback fires SuSiE-RSS layer re-fire if Wave-0 diagnostic concluded rsid-only and the Wave 4 verification fails.
- Cache backup convention: `mv results/qtl_coloc results/qtl_coloc.preFix.bak`; `mv results/fine_mapping/susie results/fine_mapping/susie.preFix.bak` (if SuSiE-RSS layer is in scope).
- Snakemake re-fire command: `snakemake --snakefile workflow/Snakefile --use-conda -j 50 results/qtl_coloc` (and `results/fine_mapping` if SuSiE-RSS in scope). Substitute real Snakemake rule names by reading `workflow/Snakefile` at Wave-0 time.

### D-TA-05: OSF pre-registration coverage check

**Decision:** **Wave 0 verifies** OSF pre-reg coverage of D-TA-02 (L-sweep wording) + D-TA-03 (canonical-pair scope) against `osf.io/pvb5j` (DOI 10.17605/OSF.IO/PVB5J) Methods + closeout PDF at `osf.io/az52u`:
- (i) L-sweep wording — verify the Methods §Fine-Mapping Configuration phrase "an L-sweep re-fit at L ∈ {15, 20, 30} is pre-registered as a follow-on supplementary analysis" is present in the OSF-deposited Methods text or amendment, NOT only in the in-tree `track_a_pivot.md` draft
- (ii) Canonical-pair scope — verify HQ#2(iii) re-fire pre-registration is present in OSF deposit (AUDIT-RESPONSE 2026-04-26 line 269 says "pre-registered in TRACK-A-FROZEN-NUMBERS.md" — needs OSF-portal verification)
- (iii) Cache invalidation re-fire — covered separately by **D-TA-Cache-OSF** below

If any of (i)-(ii) is uncovered, **post OSF amendment BEFORE Wave 1 fires** (Carter web-UI, ~30 min on the OSF portal; rides on the existing `osf.io/az52u` closeout PDF as an addendum). Wave 1 is HARD-GATED on this verification.

**Alternatives considered:** (b) Post OSF amendment NOW pre-emptively (covers worst case; ~30 min Carter web-UI even if pre-reg already covers). (c) Defer the OSF check entirely until Wave 1 has produced results (risky — retroactive amendment).

**Why:** Saves a round-trip if pre-reg is sufficient (audit-response indicates it likely is). Eliminates pre-reg risk in either branch (verify-then-fire or amend-then-fire). Maintains the Carter-mandated pre-registration discipline invariant (any L value, threshold, or scope choice not pre-registered enters via OSF amendment posted BEFORE Wave 1 — not silent change).

**How to apply:**
- Wave 0 task `OSF-Pre-Reg-Verify`: Carter opens `osf.io/pvb5j` Methods + `osf.io/az52u` closeout PDF in browser; greps for "L-sweep" + "{15, 20, 30}" + "L = 20" + "canonical pair" + "BMI-HTN" + "HTN-stroke"; records the outcome as `D-TA-OSF-COVERAGE-XX` in CONTEXT.md addendum.
- If covered: Wave 1 cleared to fire.
- If uncovered: Carter posts amendment on OSF portal (~30 min web-UI); Wave 1 blocked until amendment confirmed live. The amendment text rides on the existing `osf.io/az52u` closeout PDF as an addendum (single combined R2 amendment is fine).
- Plan PLAN.md must include the OSF-Pre-Reg-Verify task as a Wave-0 hard gate with explicit `checkpoint:human-verify` annotation.

### D-TA-Cache-OSF: OSF treatment of Issue 2 cache invalidation re-fire

**Decision:** **Deviation-log entry only** — append to `.planning/amendments/osf_deviations.md` (or `osf.io/az52u` closeout addendum if Carter prefers a single OSF surface). The cache invalidation re-fire uses the **same code** (`069b34f` + `7d54183`) + **same data** + **same params** — only the cache state changes. This is a methodological cache-hygiene fix, not a new analysis.

**Alternatives considered:** (b) Pre-reg amendment via `osf.io/pvb5j` (treat as new analysis) — over-rigorous; cache hygiene fixes don't typically require pre-reg amendments. (c) Both — deviation-log + brief pre-reg amendment note — maximum traceability but extra OSF round-trip.

**Why:** Methodologically correct: this is not a new analysis, it's a cache hygiene fix that produces the analysis the pre-registration already covers. The 78.9 % `too_few_snps` rate was already disclosed in the manuscript (Methods L90 + Discussion L220 + Limitations bullet 5); the re-fire produces the analysis the manuscript pre-registered, not a new one. Per Carter's command-args explicitly: "should be a deviation-log entry, NOT a pre-reg amendment".

**How to apply:**
- Wave 7 closeout task: append `osf_deviations.md` entry with: discovery date (2026-04-28), root cause (intermediate caches generated before commits `069b34f` + `7d54183` landed), invalidation rationale (variant-ID format mismatch chr:pos vs rsid), before/after numerics (1,005 / 1,274 = 78.9% → post-refresh number), commit pointers for the cache invalidation + re-fire commits, and OSF deposit cross-reference.
- The deviation-log entry is the single OSF artifact for Issue 2 cache hygiene; no `osf.io/pvb5j` amendment needed.

### D-TA-06: id-vs-ref-LD nickname rename

**Decision:** Wave 6 bundles the id-vs-ref-LD rename with manuscript narrative updates. Per-path renames:

| Pre-rename path | Post-rename path | Rename? |
|---|---|---|
| `docs/manuscript/track_a_pivot.md` | `docs/manuscript/id-vs-ref-LD.md` | **YES** |
| `.planning/amendments/TRACK-A-PIVOT.md` | `.planning/amendments/ID-VS-REF-LD-STRATEGY.md` | **YES** |
| `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` | (keep as-is) | **NO** (Carter-flagged optional; widely cross-referenced; saves a round-trip) |
| `bin/build_track_a_submission_bundle.sh` | `bin/build_id_vs_ref_ld_submission_bundle.sh` | **YES** (lowercase snake_case matches rest of `bin/`) |

Plus all intra-doc references in: R figure-builder scripts (`source()` / `fs::path()` / `readLines()` pointers in `scripts/R/figures/` and `scripts/R/aggregators/`), the renamed submission-bundle build script's heredoc-generated README + CITATION.cff content, README pointers, OSF pre-reg / closeout PDF cross-references, `.planning/STATE.md` forward references, `.planning/DECISIONS.md` forward references, any test fixtures pointing at these paths.

**Alternatives considered:** Q-09: NO keep `track_a_pivot.md` (path is internal git history; only prose framing matters) — argues path naming doesn't reach public artifacts. Q-10: NO keep `TRACK-A-PIVOT.md` (memory rule allows "pivot" for the strategic event itself). Q-12: keep mixed-case `bin/build_id_vs_ref_LD_submission_bundle.sh` to preserve LD acronym capitalization; or NO keep current name (build tool, not publication artifact).

**Why:** Aligns the file paths with the locked manuscript title "Identity-LD versus reference-LD colocalization at curated cardiometabolic pleiotropy loci" and the `project_track_a_handle.md` memory. `TRACK-A-FROZEN-NUMBERS.md` retention saves an extra reference-fix-up round-trip across manuscript + R scripts + OSF amendment + Track A SUMMARY (4+ citation sites); the file's role as numerics source-of-truth is independent of the publication's nickname. `bin/build_id_vs_ref_ld_submission_bundle.sh` lowercase snake_case matches every other script in `bin/` (shell convention).

**How to apply:**
- Wave 6 task list (per renamed file): `git mv` + reference fix-up across all citation sites + verify `md5sum` byte-identical for content (only paths change, not bytes) + atomic commit per file.
- Honest-framing-lock chain enumerated explicitly in the Wave 6 PLAN.md task; each anchor point survives the rename byte-identical at new line numbers (post-rename verify: `grep -n "anchor_phrase" docs/manuscript/id-vs-ref-LD.md` returns the same content at L148, L295, L220, L90).
- Pivot-free language audit (separate Wave 6 task; record in CONTEXT.md addendum):
  - ALL future-facing prose, R-script headers, plot annotations, locked-scalar block headers, README, submission-bundle README (heredoc), and CITATION.cff drop "pivot" / "Track A pivot" framing in favor of "id-vs-ref-LD" or descriptive prose ("identity-LD vs reference-LD colocalization comparison" / "head-to-head identity-LD vs reference-LD evaluation")
  - Internal planning docs (`STATE.md`, `DECISIONS.md`, `.planning/amendments/`, `.planning/session_summaries/`) keep "pivot" for the 2026-04-22 strategic event itself, but NOT for the publication
  - Do NOT rewrite git history (commit messages predating 2026-04-28 keep their `track_a_pivot` / "Track A pivot" tokens — historical record)
- Bundle build script's heredoc-generated `CITATION.cff` and `README.md` content also updated to use post-rename branding.

### D-TA-Wave-6-timing: Rename timing

**Decision:** Wave 6. Bundle the rename with manuscript narrative updates. Wave 6 already touches every file in scope (Methods + Results + Discussion + Limitations + Abstract + Conclusion-1 + captions + tables + R-script headers + locked-scalar blocks). One atomic git mv + reference fix-up + commits-per-file series; zero extra waves.

**Alternatives considered:** Wave 0.5 dedicated rename wave inserted before Wave 1 (cleanest context for rest of phase to operate against new paths; +1 wave; question of whether to touch git history). Wave 6.5 dedicated post-narrative wave (cleanest commit boundaries; +1 wave; Wave-6 prose written against soon-to-be-stale paths).

**Why:** Wave 6 already touches every file in scope; bundling rename costs zero extra waves. Simplest mental model. Wave 0.5 alternative would fragment the rename across two waves (since manuscript prose updates only happen at Wave 6 anyway). Wave 6.5 alternative writes Wave-6 prose against soon-to-be-stale paths — adds mechanical churn.

**How to apply:**
- Wave 6 PLAN.md structure: ordered task list with rename + reference-fix-up tasks first (mechanical, zero-narrative), then narrative atomic-update tasks (per-file commit). Each task has its own atomic commit.
- Per-task commit-message convention: `docs(ta-sh2b3, W6-rename): git mv docs/manuscript/track_a_pivot.md → docs/manuscript/id-vs-ref-LD.md + 14 reference fix-ups` (rename tasks); `docs(ta-sh2b3, W6-narrative): update Methods §Harmonization-Pipeline Diagnostics for post-Wave-5 numbers` (narrative tasks).

### D-TA-Wave-0-foundations: Path + ancestry + rule-name verification (Wave 0 outcome)

**Recorded:** 2026-04-30T00:15:30Z (Wave 0 Task 1)

**D-TA-01 path:** **INVESTIGATE** — `/rs1/researchers/c/ckclinto/coloc_analysis/` exists on this GPFS node but is **NOT a git repo** (no `.git` subdirectory). The directory contains historical artifacts:
  - `coloc_analysis_reproducibility_pkg.zip` (252 KB; Feb 2026)
  - `coloc-attempt1-backup.tar.gz` (77 GB; Feb 2026 historical backup)
  - `create_reproducibility_package.sh` (Feb 2026)
  - Subdirectories: `data/`, `genome_wide/`, `ml/`, `region_analysis/` (the pre-pivot region_analysis tree, Feb 2026)

  This is the Pitfall 1 finding pre-flagged in RESEARCH.md L349 ("VERIFIED finding 2026-04-29: /rs1/researchers/c/ckclinto/coloc_analysis/.git was not found on the current GPFS node"). The path is a NAMESPACE COLLISION with historical pre-pivot artifacts; cloning the GPFS git repo to that path would either (a) overwrite the 77 GB backup tar.gz, or (b) require a sub-path like `/rs1/researchers/c/ckclinto/coloc_analysis_git/`. **Carter-mediated escalation required** before Wave 1/2/4 LSF dispatches that depend on D-TA-01 canonical `/rs1/...` cwd. Mitigation paths (in priority order):
  1. **Redirect Wave 1/2/4 LSF jobs to GPFS path** (`/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis`) — same physical filesystem per D-TA-01 §"Why" L121; only the dispatch convention changes. RECOMMENDED for this phase to unblock Wave 1.
  2. **Clone the repo to a sibling path** like `/rs1/researchers/c/ckclinto/coloc_analysis_git/` — preserves D-TA-01 LSF dispatch path semantics but creates a new convention for downstream phases.
  3. **Carter manually relocates the historical artifacts** off `/rs1/.../coloc_analysis/` (e.g., to `/rs1/.../coloc_analysis_legacy/`) and clones the current GPFS repo to the freed path — most rigorous but requires manual file ops on a 77 GB tar.gz.

  **Wave 1 driver (`bin/fire_susie_lsweep.sh`) defaults to `cd /rs1/researchers/c/ckclinto/coloc_analysis` per the plan task spec.** If at Wave 1 fire time the path is still not a git repo, the driver will exit on `set -euo pipefail` at the `cd` (path exists, but Snakemake will fail). Carter MUST resolve this before Wave 1 (post-OSF gate) — the driver scripts can be patched to point at GPFS path 1.0× line of code.

  GPFS HEAD = `3adde9ecefbcddc60ef7d164f8d8841b253d08c2` (current HEAD, captured at Wave 0 Task 1 time).

**Code-fix ancestry (C2):** `069b34f` = ancestor (PASS); `7d54183` = ancestor (PASS). Both code fixes (run_qtl_coloc.R chr:pos tolerance + run_susie_rss.R LD-rsid override) are reachable from HEAD on the current branch — no cherry-pick required.

**Snakefile rule-name surface** (drives Wave 4 dispatch + Wave 1/2 target convention):
- **Top-level (`Snakefile`):** `rule all` (L196), `rule all_qtl_coloc` (L209) — Wave 4 dispatch target
- **`src/snakemake/rules/finemap.smk`:** `rule build_finemap_manifest` (L21), `rule run_finemap` (L45 — SuSiE-RSS rule; `policy="config/susie_policy.yaml"` hardcoded at L62), `rule summarize_finemap_results` (L105), `rule filter_finemap_summary` (L119)
- **`src/snakemake/rules/qtl_coloc.smk`:** `rule build_qtl_coloc_manifest` (L241), `rule run_qtl_coloc` (L282), `rule aggregate_qtl_coloc` (L329), `rule assign_tiers` (L380), `rule build_gene_tissue_matrix` (L465)
- **`src/snakemake/rules/coloc.smk`:** `rule run_coloc_susie` (L88) — Wave 2 canonical-pair fire rule
- **`src/snakemake/rules/multitrait.smk`:** `rule build_multitrait_manifest` (L56), `rule build_coloc_manifest` (L76), `rule run_multitrait_placeholder` (L98), `rule stroke_afr_coloc_sweep` (L135), `rule summarize_coloc_results` (L151 — Pitfall 3 mitigation target; rebuilds `coloc_summary.tsv` from per-pair JSONs), `rule build_hyprcoloc_manifest` (L170), `rule run_hyprcoloc_group` (L192), `rule summarize_hyprcoloc` (L211), `rule augment_coloc_summary` (L234), `rule build_coloc_clean_sets` (L256), `rule build_coloc_top_hits_table` (L300)

**Wave 4 dispatch target:** `all_qtl_coloc` (top-level Snakefile L209). Confirmed.
**Wave 1 SuSiE rule:** `run_finemap` (finemap.smk L45). Wave 1 dispatch targets the per-trait JSON outputs of this rule under the per-L overlay's `finemap.output_dir`.
**Wave 2 coloc.susie rule:** `run_coloc_susie` (coloc.smk L88). Wave 2 dispatch targets `{MULTITRAIT_DIR}/coloc_susie/{pair_id}.json` per the multitrait.smk convention; Pitfall 3 mitigation requires writing to a parallel `coloc_susie_R2/` namespace via overlay.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents (researcher, planner, executor) MUST read these before acting.**

### Phase entry + scope
- `.planning/ROADMAP.md` §"### Track-A-R2-sh2b3-canonical-and-cache-refresh" (lines 314–462; entry committed `d2affb2`)
- This file: `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-CONTEXT.md` — locked decisions
- `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-DISCUSSION-LOG.md` — option-by-option audit trail
- `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/ta-sh2b3-QUESTIONS.json` — 13 finalized answers (all recommendations accepted)

### Project naming + framing constraints
- `/home/ckclinto/.claude/projects/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/memory/project_track_a_handle.md` — Track A nickname id-vs-ref-LD locked
- `/home/ckclinto/.claude/projects/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/memory/feedback_original_research_framing.md` — never frame Track A as revision/audit/cleanup
- `/home/ckclinto/.claude/projects/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/memory/feedback_lsf_queues.md` — bsub_wrapper.sh queue rules + LSF_UNIT_FOR_LIMITS=GB
- `/home/ckclinto/.claude/projects/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/memory/project_python_311_pin.md` — Snakemake 7.32.4 + Python 3.11; never invoke from miniconda3 base (Python 3.13)

### Manuscript + numerics source-of-truth
- `docs/manuscript/track_a_pivot.md` (pre-rename path; manuscript body)
- `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` — single source of truth for manuscript abstract/results/tables/OSF amendment
- `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` — canonical CS-yield summary; NEVER rewritten (DEC-2026-04-25-01)
- `.planning/amendments/TRACK-A-PIVOT.md` (pre-rename path; Track A strategy doc)

### Audit closure record + decision pointers
- `.planning/amendments/TRACK-A-AUDIT-RESPONSE-2026-04-26.md` — 27-item audit closure catalogue; HQ#2(i) + HQ#2(iii) DEFERRED-COMPUTE → fired by this phase; HQ#2(ii) DEFERRED-DESIGN → resolved by D-TA-Wave1-headline; Eval 3.2 PARTIAL-CLOSED → cache invalidation closes
- `.planning/amendments/AUDIT-REVIEW-V2-2026-04-26.md` — audit-V2 reviewer document
- `.planning/amendments/AUDIT-REVIEW-2026-04-25.md` — original audit document (HQ#2 + Eval 3.2 sources)
- `.planning/DECISIONS.md` — DEC-2026-04-25-01 (`results_identity_ld/` gitignored); DEC-2026-04-24-01 (GRCh37 canonical analytic plane); DEC-2026-04-24-02 (AFR-SBP M1 fallback)

### Code substrate (Issue 2)
- `069b34f` — `run_qtl_coloc.R` chr:pos tolerance (already committed to current branch)
- `7d54183` — `run_susie_rss.R` LD-panel-rsid override (already committed to current branch)

### LSF + dispatch infrastructure
- `bin/fire_phase2_stage2_refit.sh` — Stage 2 production-fire driver (proven 2026-04-22)
- `scripts/fire_identity_ld_rerun.sh` — k2d 2026-04-24 identity-LD re-fire driver (commit `08beb4c`)
- `bin/bsub_wrapper.sh` — LSF queue dispatcher
- `/rs1/researchers/c/ckclinto/conda_envs/la_multitrait_r/` — primary conda env for SuSiE-RSS + coloc.susie + R figures
- `/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake` — Snakemake 7.32.4 + Python 3.11 (memory pin)

### OSF deposits
- `osf.io/pvb5j` (DOI 10.17605/OSF.IO/PVB5J) — Track A pre-registration
- `osf.io/az52u` — Track A closeout PDF (M1 amendment posted 2026-04-25)
- `.planning/amendments/osf_deviations.md` — deviation-log target for D-TA-Cache-OSF

### Submission bundle (frozen checkpoint)
- Submission bundle commit `cacdbfe` (`quick-260427-vbq`) — frozen rebase substrate
- `bin/build_track_a_submission_bundle.sh` (pre-rename path; 488-line bash builder; 5-engine PDF fallback chain; MIT + CC-BY-4.0 dual license; ORCID-as-TODO)

</canonical_refs>

<invariants>
## Non-Negotiable Invariants

(Re-stated from `/gsd-add-phase` brief + `/gsd-discuss-phase` command-args; downstream agents MUST honor.)

1. **NO `/gsd-quick` shortcuts.** Atomic commits per task. SUMMARY.md per plan. Verification dimensions D1–DN with PASS/WARN/FAIL evidence. (Carter mandate: "no cutting corners; rigor over speed".)
2. **Manuscript narrative writes happen ONLY at Wave 6, AFTER disk numbers are frozen at Wave 5.** NEVER pre-write narrative against anticipated outcomes. Wave-3 `checkpoint:human-verify` gate is mandatory before Wave 6.
3. **Honest-framing-lock chain preserved at all anchor points** (`docs/manuscript/track_a_pivot.md` L148 + L295 + L220 + L90 + R-script header + locked-scalar block + plot_annotation + 1vy SUMMARY). Original hypothesis-driven research framing only — never "revision" / "correction" / "cleanup" / "fix" (per `feedback_original_research_framing.md` memory).
4. **DEC-2026-04-25-01 preserved**: `results_identity_ld/` NOT committed; `.gitignore` + canonical CS-yield summary at `.planning/amendments/IDENTITY-LD-K2D-FIT-SUMMARY.tsv` only.
5. **Stage 2 md5 byte-identical preservation rule** for files not intentionally rewritten by this phase (verify `md5sum` pre-vs-post each commit).
6. **Pre-registration discipline**: any L value, threshold, or scope choice not already pre-registered enters via OSF amendment posted BEFORE Wave 1 fires — not silent change. (Hard-gated by **D-TA-05**.)
7. **id-vs-ref-LD nickname is for FUTURE artifacts only**; do NOT rewrite git history (commit messages predating 2026-04-28 keep their `track_a_pivot` tokens — historical record).

</invariants>

<wave_structure>
## Suggested wave structure

Final wave count + scope decided by `/gsd-plan-phase` and not pre-locked here, but the outline below carries the locked-decision constraints:

- **Wave 0 — Foundations + Diagnostics + OSF gate**
  - Source-repo path verification (D-TA-01): `[ -d /rs1/researchers/c/ckclinto/coloc_analysis/.git ] && cd /rs1/... && git rev-parse HEAD` matches GPFS HEAD
  - Code-fix verification: `git merge-base --is-ancestor 069b34f HEAD && git merge-base --is-ancestor 7d54183 HEAD` (cherry-pick if absent)
  - SuSiE-RSS variant-ID format diagnostic (D-TA-04): read 3 sample fit JSONs; record format in CONTEXT.md addendum as `D-TA-04-DIAGNOSTIC-XX`
  - OSF pre-reg coverage verification (D-TA-05): Carter web-UI; record outcome as `D-TA-OSF-COVERAGE-XX`; if uncovered → post amendment + Wave 1 hard-blocked
  - Snakefile rule-name surface: read `workflow/Snakefile` for the actual rule names of `run_qtl_coloc` + `run_susie_rss` so Wave 4 can dispatch correctly

- **Wave 1 — SH2B3 EUR L-sweep re-fits**
  - LSF dispatch on `serial` queue with `la_multitrait_r` env: 3 traits (BMI, hypertension, stroke) × 3 L values (15, 20, 30) = 9 fits
  - Convergence verification per fit (`n_CS << L`)
  - **D-TA-Wave1-headline** decision recorded post-fire (does L=20 / L=30 converge the 3 non-converged?)

- **Wave 2 — Canonical SH2B3 EUR coloc.susie production fire**
  - LSF dispatch: 9 new SH2B3 EUR trait-pairs × primary-result-L from Wave 1 = 9 jobs
  - Output: per-pair JSONs at `results/multitrait/SH2B3_12q24__EUR__{trait1}_vs_{trait2}.json`

- **Wave 3 — `checkpoint:human-verify` outcome gate**
  - Carter selects branch (a/b/c) for canonical BMI–HTN PP.H4 from Wave 2 disk numbers
  - Decision recorded as `D-TA-WAVE3-OUTCOME-XX` in CONTEXT.md addendum
  - Plan must NOT pre-commit; Wave 6 narrative branches per outcome

- **Wave 4 — Variant-ID cache invalidation + Snakemake re-fire**
  - Cache backup: `mv results/qtl_coloc results/qtl_coloc.preFix.bak` (always); `mv results/fine_mapping/susie results/fine_mapping/susie.preFix.bak` (conditional on Wave-0 diagnostic per D-TA-04)
  - Snakemake re-fire `--use-conda -j 50` (~10 hr QTL-coloc; ~5 hr extra if SuSiE-RSS layer in scope)
  - Verification: `too_few_snps` count drops materially from 1,005 (PASS ≤ 200; FAIL ≈ 1,000 → root-cause investigation)

- **Wave 5 — Downstream aggregator + figure refresh**
  - Re-run `scripts/python/aggregate_qtl_coloc.py` → `results/track_a_aggregations/qtl_coloc_status_distribution.tsv`
  - Re-run `scripts/R/aggregators/*.R` (Table 1 builder, Tier-assignment script, Pathway-disclosure aggregator)
  - Re-run `src/R/figures/fig_h3_ld_overlap_dose_response.R` (Fig S7)
  - Update `TRACK-A-FROZEN-NUMBERS.md` LIVE block with Wave-5 numbers (this is the disk-then-narrative gate before Wave 6)

- **Wave 6 — Manuscript narrative atomic updates + id-vs-ref-LD rename**
  - Rename + reference-fix-up tasks (mechanical, zero-narrative): `git mv docs/manuscript/track_a_pivot.md → docs/manuscript/id-vs-ref-LD.md`; `.planning/amendments/TRACK-A-PIVOT.md → ID-VS-REF-LD-STRATEGY.md`; `bin/build_track_a_submission_bundle.sh → bin/build_id_vs_ref_ld_submission_bundle.sh`
  - Pivot-free language audit task: drop "pivot" from future-facing prose; preserve "pivot" in internal planning docs for the 2026-04-22 strategic event
  - Narrative atomic-update tasks per-file (Methods, Results, Discussion, Limitations, Abstract, Conclusion-1, captions, tables) per Wave-3 outcome branch + Wave-5 refreshed numbers; preserve honest-framing-lock chain at L148 / L295 / L220 / L90 byte-identical

- **Wave 7 — Phase closeout**
  - SUMMARY.md per plan with deviations log
  - Verification dimensions D1–DN PASS/WARN/FAIL JSON
  - New submission bundle build via `bin/build_id_vs_ref_ld_submission_bundle.sh` (post-rename)
  - SHA-256 manifest update
  - OSF deviation log entry at `osf.io/az52u` for cache invalidation re-fire (per D-TA-Cache-OSF)

**Wave count:** 8 waves (0 through 7). Final scope decided by `/gsd-plan-phase`.

</wave_structure>

<deferred>
## Deferred Ideas (out of phase scope; preserved for future phases)

- **MAXIMUM cross-region replication** — re-fire FTO_16q12 EUR + MC4R_18q21 EUR + APOE_19q13 + CXADR_F2RL1_6p21 against post-L=20 fits for cross-region consistency. Q-04 alternative (c). Would itself become a separate phase. Not chartered here.
- **Threshold-lowering to 0.3** — surface FTO_16q12 EUR Tier-C 0.3099 signal as "partial". Q-05 alternative (b). Rejected during quick-260427-e8n; would require OSF amendment + manuscript-wide threshold rewrite.
- **Pre-emptive OSF amendment for all Issue 1+2 sub-decisions** — Q-07 alternative (b). Recommendation chose Wave-0 verify-then-amend instead.
- **Cache invalidation pre-reg amendment** — Q-08 alternative (b)/(c). Recommendation chose deviation-log only (cache hygiene fix, not new analysis).
- **Track A FROZEN-NUMBERS rename** — Q-11 alternative (b). Carter explicitly flagged optional; widely cross-referenced; rename declined to preserve stability.
- **bin/build_id_vs_ref_LD_submission_bundle.sh mixed-case** — Q-12 alternative (b). Recommendation chose lowercase snake_case to match rest of `bin/`.
- **Wave 0.5 / Wave 6.5 dedicated rename waves** — Q-13 alternatives (b)/(c). Recommendation chose Wave 6 bundled rename (zero extra waves).
- **M2-POST-M3-08 mtCOJO re-fire (~6.5 hr long-queue)** — Terminal A capacity, file-disjoint from this phase. Carter can stack on Terminal A while this phase fires.
- **Sumstats Route C manual-fetch refresh** — Terminal A capacity, file-disjoint. Carter can stack on Terminal A while this phase fires.

</deferred>

<concurrency>
## Concurrency

**Terminal A is FREE** post-`5dd9548` (D-M3-09 closed). M3 Wave 1 is gated on AoU portal P1–P6 + R1 egress hard gate (Carter web-UI, separate flow). Terminal A capacity available for **M2-POST-M3-08 mtCOJO re-fire** (~6.5 hr long-queue) or **sumstats Route C manual-fetch refresh** — both file-disjoint from this phase.

Stale `.claude/scheduled_tasks.lock` from 2026-04-22 confirmed dead at `/gsd-add-phase` commit time (`ps -p 3995760` empty). No live concurrent ROADMAP writer. If Terminal A reactivates before `/gsd-plan-phase` fires, stagger writes (Track A R2 phase work writes only `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/` + ROADMAP table-row updates + STATE.md frontmatter; Terminal A M-series work writes only `.planning/phases/m{1,2,3}-*` + ROADMAP M-series rows + STATE.md frontmatter — disjoint paths but same STATE.md frontmatter requires sequential commits).

</concurrency>

---

*Phase: ta-sh2b3-canonical-and-cache-refresh*
*Context gathered: 2026-04-28T22:42:00-04:00*
*Mode: power-mode discuss-phase; Carter accepted all 13 recommendations*
*Next: `/gsd-plan-phase ta-sh2b3-canonical-and-cache-refresh`*
