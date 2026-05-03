# OSF Deviations Log — id-vs-ref-LD project (Track A)

**Project:** Identity-LD versus reference-LD colocalization at curated cardiometabolic pleiotropy loci
**OSF deposits:** osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J) — pre-registration; osf.io/az52u — closeout PDF + amendment chain
**Purpose:** Single canonical in-tree log of methodological deviations from the OSF pre-registration that accumulated during Phase ta-sh2b3-canonical-and-cache-refresh (Waves 0-7). Cache-hygiene fixes, infrastructure changes, narrative reframings, and other non-analytical adjustments are recorded here per project methodology (NOT as pre-registration amendments). Per D-TA-Cache-OSF: deviation-log-only entries; Carter optionally appends abstracts to osf.io/az52u closeout PDF (web-UI workflow).

**Phase scope:** Waves 0-7 of phase `ta-sh2b3-canonical-and-cache-refresh`; pre-phase frozen reference = commit `cacdbfe` (2026-04-27); post-phase HEAD ≈ `c211824` (2026-05-03 + W7 commits land on top).

**Cascade structure:** Entry 17 is the methodological ANCHOR (originally-anticipated cache-invalidation deviation per parent W7 PLAN). Entries 8-16 are chronological cascade entries that emerged during phase execution. Cross-references appear inline as "(see entry_N)".

---

## Entry 8 — V4 dispatch CONSERVATIVE_BOTH override (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 4)

**Discovery date:** 2026-04-29 (Wave 0 SuSiE-RSS variant-ID format diagnostic)

**Root cause:** Wave 0 diagnostic on `results/fine_mapping/susie/*.fit.rds` confirmed BOTH layers (SuSiE-RSS layer + QTL-coloc cache layer) carried pre-fix variant-ID format (chr:pos vs rsid mismatch). Per `D-TA-04-OVERRIDE-V2 = CONSERVATIVE_BOTH`: rebuild both layers (NOT QTL-coloc-only).

**Invalidation rationale:** Cache-hygiene rebuild against post-fix code (commits `069b34f` + `7d54183`); same data + same params; methodological deviation only.

**Execution:** V4 dispatch fired in two phases:
- SuSiE-RSS rebuild at `niter=1000` confirmed by 3 SH2B3 anchor md5 changes (BMI fit `462ada6a`, HTN fit `8255c1ac`, stroke fit `a041eecc`).
- QTL-coloc rebuild deferred to W4.5 wave (see entry_9) due to driver scope constraints.

**Commit pointers:** Wave 4 V4 atomic commits in phase ta-sh2b3-canonical-and-cache-refresh (per W4 SUMMARY `ta-sh2b3-W4-cache-invalidation-and-refire-SUMMARY.md`).

---

## Entry 9 — W4.5 wave creation: 2-pass QTL-coloc rebuild driver (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 4.5)

**Discovery date:** 2026-04-30 (W4 SuSiE-RSS layer landed, QTL-coloc cache rebuild needed driver outside W4 scope)

**Root cause:** `qtl_coloc.smk` 2-pass design (per Snakemake DAG semantics) requires re-firing without invoking the full pipeline driver. Created `bin/fire_w4_5_qtl_coloc_only.sh` to bypass driver per `D-TA-WAVE4-5-A-OUTCOME = W4.5-a`.

**Invalidation rationale:** Methodological — cache-hygiene re-fire of QTL-coloc layer only; SuSiE-RSS layer (entry_8) preserved at niter=1000.

**Commit pointers:** `b368e0e` (`bin/fire_w4_5_qtl_coloc_only.sh` driver added).

---

## Entry 10 — W4.5-A scope correction: T1 production lock recovery (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 4.5-A)

**Discovery date:** 2026-04-30 ~16:35 EDT (initial W4.5-a dispatch fired with broader phase2 source list; aborted at 1692-job mark)

**Root cause:** Initial W4.5-a fire used the post-pivot expanded `phase2_enabled_sources` list (1692 jobs); per `D-TA-WAVE4-5-A-SCOPE-CORRECTION` and the original Phase 2 production lock, T1 scope is `[gtex_eqtl, gtex_sqtl]` only (1275 jobs).

**Invalidation rationale:** Scope-correction; did NOT change methodology — only restored the pre-registered T1 production source set.

**Execution:** Aborted 1692-job dispatch at 16:35 EDT 2026-04-30; re-fired with `pipeline.yaml::phase2_enabled_sources: [gtex_eqtl, gtex_sqtl]` at 1275 jobs (commit `986af29`).

**Commit pointers:** `986af29` (pipeline.yaml scope re-lock).

---

## Entry 11 — W4.5-A continuation re-fire outcome (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 4.5-A continuation)

**Discovery date:** 2026-05-01 (supervisor PID 2670648 exited at 99.6% complete, 1270/1275 done; 4 missing run_qtl_coloc + aggregator 3rd-pass)

**Root cause:** Supervisor exit before final 4 `run_qtl_coloc` jobs completed; aggregator never re-ran a 3rd pass against the updated cache.

**Invalidation rationale:** Methodological — completion of in-progress cache-hygiene rebuild started in entry_9 / entry_10. NO new analytical decisions.

**Execution:** Quick task `260501-r1q` drained the 4 missing `run_qtl_coloc` outputs and executed the aggregator 3rd pass. Cache-staleness hypothesis was tested AND refuted in this step (Δ status distribution = 0; see entry_12 for disposition).

**Numerics (post W4.5-A continuation, 1,274 attempts):**
| metric | pre-fix V1 cache | post-W4.5-A continuation | Δ |
|---|---|---|---|
| total_attempts | 1,274 | 1,274 | 0 |
| too_few_snps | 1,005 (78.9 %) | 1,005 (78.9 %) | 0 |
| success | 32 | 32 | 0 |
| no_qtl_cs | 235 | 235 | 0 |
| qtl_susie_failed | 2 | 2 | 0 |

**Commit pointers:** `260501-r1q` quick task atomic commits (see `.planning/quick/260501-r1q-*-SUMMARY.md`).

---

## Entry 12 — W4 disposition revision: mechanical FAILED → strategic HONEST_FINDING (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 4) — DEC-2026-05-01-02

**Discovery date:** 2026-05-01

**Root cause:** The Wave 4 mechanical PASS gate (`too_few_snps ≥ 800`) FAILED at the post-W4.5-A continuation distribution (1005/32/235/2 unchanged from V1). The cache-staleness hypothesis (that pre-fix code rejected ~78.9 % of attempts owing to chr:pos vs rsid mismatch) was tested in entry_11 AND refuted (Δ = 0). Continuing to W4.5-B (a SuSiE-RSS rebuild) was considered and rejected: LD coverage is the constraint, not iteration budget; rebuild risks breaking the TRACK-A-FROZEN md5 invariant on the 3 SH2B3 anchor `.fit.rds` files (`462ada6a` / `8255c1ac` / `a041eecc`).

**Invalidation rationale:** Methodological re-disposition. The 78.9 % rate is now adopted as the **canonical Layer-2 finding** parallel to the 53.1 % Layer-1 SuSiE convergence rate (Layer-1 finding from W6-260503-1e1; see entry_16). Both rates are real constraints of the curated-locus design under matched-LD, NOT artifacts of broken code.

**Disposition recorded:**
- tracker v7: `outcome_disposition: HONEST_FINDING` + historical_outcome block preserves mechanical FAILED label
- DECISIONS.md: `DEC-2026-05-01-02`
- W4-DISPOSITION-REVISED.md: canonical narrative + 3-layer architecture (Layer-1 SuSiE convergence; Layer-2 QTL-coloc rate; Layer-3 substantive Tier-A distribution)

**W4.5-B explicitly skipped:** SuSiE-RSS rebuild risks md5 break on canonical anchors with no expected change in Layer-2 outcome.

**Commit pointers:** Tracker v7 + W4-DISPOSITION-REVISED.md atomic commits in phase ta-sh2b3-canonical-and-cache-refresh; DEC-2026-05-01-02 entry in `.planning/DECISIONS.md`.

---

## Entry 13 — W6 narrative narrowing: cache-staleness reframe (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 6) — quick task 260502-1c1

**Discovery date:** 2026-05-02

**Root cause:** Following entry_12 (DEC-2026-05-01-02), 6 sites in the manuscript draft `docs/manuscript/id-vs-ref-LD.md` framed cache-staleness as a hypothesis-of-fact (i.e., "78.9 % failure rate was caused by code-data mismatch"). Post-refutation, those framings are factually inconsistent with the disposition.

**Invalidation rationale:** Documentation-only narrative correction. NO numerical change. The substantive Layer-3 distribution (Tier-A = 0) is now made explicit at all 6 manuscript reframe sites.

**Execution:** 6 manuscript sites reframed: cache-staleness-as-fact → cache-staleness-tested-and-refuted. Tier-A = 0 substantive Layer-3 distribution explicit. Manuscript size 95,614 → 100,529 bytes.

**Commit pointers:** Quick task `260502-1c1` atomic commits (see `.planning/quick/260502-1c1-*-SUMMARY.md`).

---

## Entry 14 — W6 mechanical rename: track_a_pivot → id-vs-ref-LD (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 6) — quick task 260502-lsk

**Discovery date:** 2026-05-02

**Root cause:** "Track A pivot" framing was historical scaffolding from the 2026-04-22 strategic split; for resubmission to *Genome Medicine*, the project needs a non-pivot, non-revision public handle. Per memory `feedback_original_research_framing.md` and Carter's directive: rename to `id-vs-ref-LD` (factual, scientific).

**Invalidation rationale:** Mechanical rename — no content change at byte level for the renamed manuscript at the new path (md5 22f412f6 byte-identical pre/post rename); 17 forward-ref fix-ups across R scripts + .planning/ files updated reference paths only.

**Execution:** 3 `git mv` at R100 (rename detection threshold):
- `track_a_pivot.md` → `docs/manuscript/id-vs-ref-LD.md`
- `TRACK-A-PIVOT.md` → `.planning/amendments/ID-VS-REF-LD-STRATEGY.md`
- `build_track_a_submission_bundle.sh` → `bin/build_id_vs_ref_ld_submission_bundle.sh`

Plus 17 forward-reference fix-ups + STATE.md ref-fixups per Carter Option B.

**Rule-1 deviation acknowledged:** Per `feedback_original_research_framing.md` Rule-1, "track_a" tokens are forbidden in framing prose; factual filename references (e.g., the OLD `track_a_pivot.md` filename appearing in a `git mv` command in this entry's Execution block) are exempt as historical-record-preserving references.

**Commit pointers:** Quick task `260502-lsk` atomic commits.

---

## Entry 15 — W6 BRANCH_C SURVIVE: Wave-3 outcome materialization (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 6) — quick task 260502-tjn

**Discovery date:** 2026-05-02

**Root cause:** Wave 3 of the original phase plan was conditional on Wave 2 R2 canonical-pair coloc.susie outcomes. Wave 2 R2 fire (commit `b3395d9`) produced PP.H4 = 1.0 for BMI-HTN, HTN-stroke, HTN-T2D at rs3184504 under matched-LD. Per `D-TA-WAVE3-OUTCOME = BRANCH_C_SURVIVE`: SH2B3 anchor flips from "collapse / not executed" to "validated under matched-LD."

**Invalidation rationale:** Materialization of pre-registered branch outcome. NO methodological deviation; the outcome WAS pre-registered as a possible W3 branch.

**Execution:** 11 manuscript sites reframed; new "## Wave-3 outcome (BRANCH_C SURVIVE) — LIVE" block appended at `TRACK-A-FROZEN-NUMBERS.md` lines 338-369.

**Commit pointers:** Quick task `260502-tjn` atomic commits + Wave 2 fire commit `b3395d9`.

---

## Entry 16 — W6 Wave-1 L-sweep PRESERVE-WITH-DISCLOSURE (Phase ta-sh2b3-canonical-and-cache-refresh, Wave 6) — quick task 260503-1e1

**Discovery date:** 2026-05-03

**Root cause:** Wave 1 L-sweep at L ∈ {15, 20, 30} with niter=1000 returned NONE_CONVERGED at strict gate for all 9 (3 traits × 3 L-values) configurations. The 51/96 = 53.1 % headline value (Layer-1 SuSiE convergence rate at the original niter=500 run) was at risk of being undermined or replaced. Per `D-TA-Wave1-headline = PRESERVE-WITH-DISCLOSURE`: preserve the 51/96 numerator as the canonical Layer-1 rate AND disclose the L-sweep null-convergence outcome at strict gate.

**Invalidation rationale:** Methodological disclosure. Per Zou 2022 §Discussion (n_CS << L behavior), strict-gate FAIL at L ∈ {15, 20, 30} niter=1000 is consistent with structural sparsity, not pipeline failure. NO numerator change.

**Execution:**
- 4 manuscript narrative sites updated (preserve 51/96; disclose L-sweep null-convergence; cite Zou 2022)
- 1 Supplementary Methods Table SX added (per-trait per-L convergence details)
- Concurrent L216 residual-staleness fix (orthogonal site that still framed cache-staleness as fact)
- 4 honest-framing-lock anchors preserved at section-header level
- Forbidden-token count ≤ baseline 35 (per `feedback_original_research_framing.md` constraint)
- 3 SH2B3 anchor `.fit.rds` md5s preserved exactly (`462ada6a` / `8255c1ac` / `a041eecc`)
- L-sweep disclosure column added to canonical results table
- New "## Wave-1 L-sweep convergence outcomes (PRESERVE-WITH-DISCLOSURE) — LIVE" block at `TRACK-A-FROZEN-NUMBERS.md` lines 370-398
- No STATE.md Track-B-encoded mutations
- No push

**Commit pointers:** Quick task `260503-1e1` atomic commits (HEAD ≈ `c211824` pre-W7).

---

## Entry 17 — Cache-invalidation deviation (ANCHOR; D-TA-Cache-OSF) (Phase ta-sh2b3-canonical-and-cache-refresh, Waves 0-4 + W4.5)

**Anchor topic:** Cache invalidation across the QTL-coloc + SuSiE-RSS layers — methodological cache-hygiene fix paired with a falsifiable cache-staleness hypothesis test. This entry is the originally-anticipated W7 deviation (D-TA-Cache-OSF locked decision).

**Discovery date:** 2026-04-28 (audit-V2 §Eval 3.2 review)

**Root cause:** The intermediate QTL-coloc cache at `results/qtl_coloc/` (1,274 per-attempt JSONs; 1,005 / 1,274 = 78.9 % `too_few_snps` failure rate at V1 cache mtime 2026-04-30T00:30) was generated BEFORE the variant-ID matcher fixes landed in HEAD:
- Commit `069b34f` (2026-04-21): `run_qtl_coloc.R` extended to tolerate chr:pos-formatted variant IDs (added candidate-based best-overlap match: rsid / chrpos / variant_id).
- Commit `7d54183` (2026-04-21): `run_susie_rss.R` LD-panel-rsid override added when LD has rsids and sumstats has chr:pos.

**Two-fold methodological treatment:**
1. **Cache-hygiene fix:** rebuild cache against post-fix code; same data + same params + post-fix code = the analysis the OSF pre-registration already covers.
2. **Cache-staleness hypothesis test:** the 78.9 % rate predicted to drop substantially if pre-fix code was rejecting attempts owing to format mismatch.

**Invalidation rationale:** Methodological **cache hygiene fix + falsifiable hypothesis test**, NOT a new analysis. Per D-TA-Cache-OSF (locked decision in CONTEXT.md): treat as **deviation-log entry only** — NOT a pre-registration amendment.

**Test outcome:** The cache-staleness hypothesis was REFUTED. Δ status distribution = 0 across all 4 status categories at the post-W4.5-A continuation distribution (see entry_11). The 78.9 % rate is a real constraint of the harmonized-locus design, NOT a software artifact. See entry_12 for the full disposition (HONEST_FINDING, Layer-2 canonical adoption, W4.5-B skip).

**Cache backup preservation:** Pre-fix cache moved (NOT deleted) to `results/qtl_coloc.preFix.bak.${TS}` (timestamped per RESEARCH.md Pitfall 5); rollback path preserved on disk. Identical convention applied to `results/fine_mapping/susie/` (SuSiE-RSS layer in scope per `D-TA-04-OVERRIDE-V2 = CONSERVATIVE_BOTH`; see entry_8).

**Commit pointers:**
- Code fixes (already in HEAD, NOT this phase): `069b34f`, `7d54183`
- V4 dispatch (entry_8): Wave 4 atomic commits
- W4.5-a driver (entry_9): `b368e0e`
- W4.5-A scope correction (entry_10): `986af29`
- W4.5-A continuation (entry_11): quick task `260501-r1q` commits
- Disposition revision (entry_12): tracker v7 + W4-DISPOSITION-REVISED.md commits + DEC-2026-05-01-02

**OSF cross-reference:** Linked to `osf.io/az52u` closeout PDF amendment chain. This deviation entry is the canonical in-tree source. Carter optionally appends a brief abstract of this entry (or the entire 10-entry log) to the osf.io/az52u closeout PDF (web-UI workflow; OUT OF SCOPE for this task).

**Manuscript disclosure:** The methodological description of this cache invalidation, the cache-staleness hypothesis test, and its refutation, are integrated at:
- `docs/manuscript/id-vs-ref-LD.md` Methods §Harmonization-Pipeline Diagnostics (per W6-260502-1c1; see entry_13)
- `docs/manuscript/id-vs-ref-LD.md` Discussion §Identity-LD Inflation (per W6-260502-tjn BRANCH_C reframe; see entry_15)
- `docs/manuscript/id-vs-ref-LD.md` Limitations bullets (per W6-260502-1c1 + 260503-1e1; see entries 13, 16)

---

## Phase summary block

| Entry | Wave | Decision token | Disposition |
|---|---|---|---|
| 8 | W4 | D-TA-04-OVERRIDE-V2 = CONSERVATIVE_BOTH | applied; 3 SH2B3 anchor md5s changed |
| 9 | W4.5 | D-TA-WAVE4-5-A-OUTCOME = W4.5-a | driver landed (b368e0e) |
| 10 | W4.5-A | D-TA-WAVE4-5-A-SCOPE-CORRECTION | scope re-locked (986af29) |
| 11 | W4.5-A | continuation outcome | 1270/1275 + 4 drained; 3rd-pass aggregator |
| 12 | W4 | DEC-2026-05-01-02 (disposition revision) | mechanical FAILED → HONEST_FINDING |
| 13 | W6 | 260502-1c1 narrative narrowing | 6 sites reframed |
| 14 | W6 | 260502-lsk mechanical rename | 3 git mv at R100 |
| 15 | W6 | D-TA-WAVE3-OUTCOME = BRANCH_C_SURVIVE (260502-tjn) | 11 sites reframed |
| 16 | W6 | D-TA-Wave1-headline = PRESERVE-WITH-DISCLOSURE (260503-1e1) | 5 sites + Sup Table SX |
| 17 | W7 | D-TA-Cache-OSF (anchor) | this log file created |

**Total atomic commits across phase Waves 0-7 (estimated):** 32+ (per HEAD-vs-cacdbfe ahead-count).

**End of consolidated deviation log.**
