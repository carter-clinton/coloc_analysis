---
phase: ta-sh2b3-canonical-and-cache-refresh
plan: 4
slug: W4-cache-invalidation-and-refire
status: COMPLETE_HONEST_FINDING
mechanical_outcome: FAILED
strategic_disposition: HONEST_FINDING
created: 2026-05-01
updated: 2026-05-01
disposition_documents:
  - W4-DISPOSITION-REVISED.md (active narrative; refuted-hypothesis reasoning + 3-layer architecture)
  - ../DECISIONS.md::DEC-2026-05-01-02 (load-bearing decision anchor)
  - wave4_dispatch_tracker_v7.json (tracker; status=FAILED preserved + outcome_disposition=HONEST_FINDING)
materialized_via: quick task 260501-vxi (additive; no STATE.md writes; no push)
---

# Wave 4 — Variant-ID cache invalidation + Snakemake re-fire (Issue 2 closure)

## Outcome

**Mechanical PASS/FAIL gate:** **FAILED** — `too_few_snps = 1005 / 1274 = 78.9%` (≥ 800 cutoff).
**Strategic disposition:** **HONEST_FINDING** (re-dispositioned 2026-05-01 per [DEC-2026-05-01-02](../../DECISIONS.md)). The cache-staleness hypothesis embedded in tracker v6 was tested by the W4.5-A continuation (drain final 4 + aggregator 3rd-pass) and refuted (Δ = 0; pre-3rd-pass too_few_snps unchanged from V4-era count). The 78.9% is structural (LD-panel coverage + region-window choices), not artifactual.

**Adopted as canonical Layer-2 finding** parallel to Layer-1 51/96 = 53.1% SuSiE-RSS strict-gate convergence rate. **W4.5-B SuSiE-RSS rebuild explicitly skipped:** data identifies LD coverage as the constraint, not iteration budget; rebuild would risk TRACK-A-FROZEN md5 invariant break with low expected payoff.

See [W4-DISPOSITION-REVISED.md](W4-DISPOSITION-REVISED.md) for the full refuted-hypothesis reasoning + 3-layer contrast architecture (Layer-1 53.1% / Layer-2 21.1% feasibility ≡ 78.9% structural attrition / Layer-3 32/1274 = 2.5%).

## Dispatch chronology (V1 → W4.5-A continuation)

| Stamp | Version | Outcome | Tracker |
|-------|---------|---------|---------|
| 2026-04-30T00:30 EDT | V1 initial dispatch | HALTED 2026-04-30T00:35Z; DAG widened scope beyond D-TA-04=RSID intent (transitively re-fired 96 run_finemap SuSiE-RSS jobs because src/legacy/region_analysis/scripts/run_susie_rss.R was touched by W1 commit 02c4404 max_iter fix); 50 dispatched + bkill'd; 74 SuSiE-RSS files overwritten under post-7d54183 + post-02c4404 HEAD; cache restored from `results/qtl_coloc.preFix.bak.20260430_003141` (1,274 JSONs intact). | wave4_dispatch_tracker.json |
| 2026-04-30T08:12 EDT | V2 | LSF dispatch attempt; superseded by V3 | wave4_dispatch_tracker_v2.json |
| 2026-04-30T09:58 EDT | V3 | Attempted re-fire; HALT (commit 7676529) on 'Too few tasks' rejections; D-TA-WAVE4-V3-BSUB-TOO-FEW-TASKS-OUTCOME = Option E + max-cores audit | wave4_dispatch_tracker_v3.json |
| 2026-04-30T10:21 EDT | V4 | Option E launch (commit b3395d9 dispatch-healthy snapshot); supervisor PIDs 2224382/2224456/2224479; CONSERVATIVE_BOTH per D-TA-04-OVERRIDE-V2 | wave4_dispatch_tracker_v4.json |
| 2026-04-30T11:20 EDT | V4 addendum | Supervisor-orphan misdiagnosis + correction (supervisor lived on remote login node; HPC clusters share GPFS but not process trees across hosts) | wave4_dispatch_tracker_v4_addendum_supervisor_orphan.json |
| 2026-04-30T12:45 EDT | V4 PARTIAL_PASSED | SuSiE-RSS rebuilt at niter=1000 (96 .fit.rds; 3 SH2B3 anchor md5s captured: bmi=462ada6a / htn=8255c1ac / stk=a041eecc); qtl_coloc layer NOT rebuilt (DAG enumerated 0 run_qtl_coloc) | wave4_dispatch_tracker_v5.json |
| 2026-04-30T16:24 EDT | W4.5-A initial | HALTED 2026-04-30T16:35 EDT; DAG plan revealed scope creep to 1692 jobs (pipeline.yaml missing phase2_enabled_sources scope filter); 104 submitted + bkill'd 46 in-flight | (folded into v6) |
| 2026-04-30T16:48 EDT | scope correction | commit 986af29: pipeline.yaml gets `phase2_enabled_sources: [gtex_eqtl, gtex_sqtl]` top-level filter (T1 production scope per project_t1_production_status.md) | (folded into v6) |
| 2026-04-30T16:53 EDT | W4.5-A re-fire | DISPATCHED supervisor PID 2670648 on serial queue; DAG = 1275 jobs (1274 run_qtl_coloc + 1 all_qtl_coloc); aggregator rules NOT in DAG plan (snakemake planner saw V4-produced outputs as up-to-date at startup; 3rd-pass invocation flagged as needed in tracker v6) | wave4_dispatch_tracker_v6.json |
| 2026-04-30T18:04 EDT | W4.5-A supervisor exit | PID 2670648 last log activity at 99.6% (1270 of 1275 steps done); 4 run_qtl_coloc targets never dispatched / never picked up | (gap captured in tracker v7) |
| 2026-05-01T19:45 EDT | W4.5-A drain | Quick task 260501-r1q: bin/fire_w4_5_drain_final5.sh (NEW launcher, no `--forcerun`); 4 LSF jobs (82066–82069) dispatched + drained clean in ~4 min; JSON count 1270 → 1274 (commit f165e57) | wave4_dispatch_tracker_v7.json |
| 2026-05-01T20:06 EDT | W4.5-A aggregator 3rd-pass | Targeted aggregator output paths (after 3rd-pass v1 'Nothing to be done' + v2 forcerun-scope-creep recovery via SIGKILL + explicit-jobid bkill of 9 v2 jobs 82073–82081); 5/6 aggregator outputs refreshed at mtimes 1777680429–1777680509 (qtl_coloc_manifest.tsv correctly stays at V4 mtime per architectural design — built upstream from regions config not downstream from per-id JSONs) (commit bf2a18a) | wave4_dispatch_tracker_v7.json |
| 2026-05-01T~20:15 EDT | W4 disposition | DEC-2026-05-01-02 + W4-DISPOSITION-REVISED.md + tracker v7 outcome_disposition=HONEST_FINDING (commit ad48257) | wave4_dispatch_tracker_v7.json |

## Status distribution from the canonical 1274-JSON cache

| Status | Count | Fraction |
|---|---|---|
| `too_few_snps` | 1005 | **78.9%** ← canonical Layer-2 attrition |
| `no_qtl_cs` | 235 | 18.4% |
| `success` | 32 | **2.5%** ← Layer-3 substantive coloc hits |
| `qtl_susie_failed` | 2 | 0.2% |
| **Total** | **1274** | 100.0% |

## D-TA-WAVE4-OUTCOME

Recorded as **D-TA-WAVE4-OUTCOME = FAILED_HONEST_FINDING** per CONTEXT.md addendum chain:
- D-TA-WAVE4-V3-BSUB-TOO-FEW-TASKS-OUTCOME = Option E (commit ed8dc51)
- D-TA-04-OVERRIDE-V2 = CONSERVATIVE_BOTH executed in two phases (V4 SuSiE-RSS rebuild + W4.5-a QTL-coloc layer rebuild)
- D-TA-WAVE4-5-A-OUTCOME = Option W4.5-a 2-pass qtl_coloc rebuild (commit 33f61be)
- D-TA-WAVE4-5-A-SCOPE-CORRECTION = T1 production lock recovery via phase2_enabled_sources scope filter (commit e40f058)
- **D-TA-WAVE4-OUTCOME = FAILED_HONEST_FINDING** = mechanical FAILED on too_few_snps ≥ 800 gate; strategically re-dispositioned to HONEST_FINDING per [DEC-2026-05-01-02](../../DECISIONS.md); 78.9% qtl_coloc rate adopted as canonical Layer-2 finding (commit ad48257)

## must_haves traceability (PLAN.md frontmatter)

| must_have | Disposition |
|-----------|-------------|
| Pre-Wave-4 baseline status distribution captured (1,005 too_few_snps + 32 success + 235 no_qtl_cs + 2 qtl_susie_failed expected) | ✓ Captured V1 baseline at `results/qtl_coloc.preFix.bak.20260430_003141` (1,274 JSONs); status counts confirmed in tracker v7 `outcome_summary.status_distribution_from_1274_perid_jsons` (matches the expected baseline EXACTLY — refutes the cache-staleness hypothesis) |
| `results/qtl_coloc/` moved to timestamped backup `results/qtl_coloc.preFix.bak.${TS}` | ✓ Five backups across V1–V4: `.bak.20260430_003141` (V1), `.bak.20260430_081210` (V2 baseline; LOAD-BEARING for V3+V4 cp -R restores), `.bak.20260430_085556` (V2 driver), `.bak.20260430_095819` (V3 driver), `.bak.20260430_102053` (V4 driver). All 5 contain 1,274 JSONs (forensic record per tracker v6) |
| If D-TA-04-DIAGNOSTIC == BOTH_LAYERS or CONSERVATIVE_BOTH: `results/fine_mapping/susie/` also moved to timestamped backup | ✓ V2 / V3 / V4 SuSiE-RSS backups at `results/fine_mapping/susie.preFix.bak.20260430_081210` (87 fit.rds + 87 json), `.bak.20260430_095819`, `.bak.20260430_102053` (per tracker v6 `preserved_backups_at_w4_5_a_refire_kickoff`); V4 rebuilt SuSiE-RSS at niter=1000 (96 .fit.rds) |
| Snakemake re-fire of `all_qtl_coloc` target completes via `/rs1/.../coloc_analysis` with --use-conda -j 50 on long queue (~10 hr; +5 hr if SuSiE-RSS layer in scope) | ✓ V4 (Option E launch 2026-04-30T10:20:53; CONSERVATIVE_BOTH 14h envelope) completed 2026-04-30T12:45:51 EDT (V4 PARTIAL_PASSED — SuSiE-RSS rebuilt; qtl_coloc DAG enumerated 0 run_qtl_coloc → required W4.5-a 2-pass design); W4.5-a re-fire 2026-04-30T16:53:15 EDT on serial queue (1274 of 1275 dispatched; 1270 finished before supervisor exited at 99.6%); W4.5-A continuation drain 2026-05-01T19:45 (final 4 + aggregator 3rd-pass) closed the layer cleanly at 1274 fresh JSONs |
| Post-refresh too_few_snps count drops materially from 1,005 baseline: PASS ≤ 200 → continue to Wave 5; FAIL ~1,000 → halt + Wave 4.5 SuSiE-RSS layer fallback fires | ✗ **Mechanically FAILED** — post-refresh too_few_snps = 1005 (Δ = 0 vs baseline). The cache-staleness hypothesis predicted Δ ≠ 0; observed Δ = 0 refutes it. Strategically re-dispositioned to HONEST_FINDING per DEC-2026-05-01-02; W4.5-B SuSiE-RSS fallback explicitly skipped (LD coverage is the constraint, not iteration budget). |
| PASS/FAIL outcome recorded in CONTEXT.md as D-TA-WAVE4-OUTCOME-{PASS\|FAIL_TO_W4.5} | ✓ Recorded as `D-TA-WAVE4-OUTCOME = FAILED_HONEST_FINDING`; the canonical decision lives in `.planning/DECISIONS.md::DEC-2026-05-01-02`. Per the disposition, **the FAIL_TO_W4.5 path was not taken** — W4.5-B explicitly skipped (rebuild would risk TRACK-A-FROZEN md5 invariant break). |
| LSF dispatch uses long queue with -W=14400 min via bsub_wrapper.sh | ✓ V4 (Option E) used long queue with -W=14400 (per commit dbededf cluster_config.yaml run_finemap threads 1→2 long-queue n≥2 enforcement); W4.5-a re-fire used serial queue (run_qtl_coloc inherits __default__ serial 1-slot policy; W4 PLAN n=1 jobs not subject to long-queue policy). |
| Wave 4.5 fallback is a MANUAL ESCALATION (per checker iter 1 NIT 4) | ✓ Honored. **Wave 4.5-A** (qtl_coloc layer rebuild) was manually escalated by Carter in response to the V4 PARTIAL_PASSED state (D-TA-WAVE4-5-A-OUTCOME = Option W4.5-a; commit 33f61be). **Wave 4.5-B** (SuSiE-RSS layer rebuild on too_few_snps regions) was the documented next-escalation path; explicitly NOT taken per DEC-2026-05-01-02 (rigor-correct reasoning per `feedback_rigor_over_speed.md`: data identifies LD coverage not iteration budget as constraint; rebuild risks TRACK-A-FROZEN md5 break with low expected payoff). |

## Preserved invariants

All four pinned invariants intact post-wave (verified in tracker v7 `outcome_summary.preserved_invariants`):

| Invariant | Pinned md5 | Post-wave md5 | Status |
|-----------|------------|----------------|--------|
| `bmi.EUR.SH2B3_12q24.fit.rds` (anchor) | `462ada6ab64fdf8571fb5ed7dd6c6ea2` | `462ada6ab64fdf8571fb5ed7dd6c6ea2` | ✓ |
| `hypertension.EUR.SH2B3_12q24.fit.rds` (anchor) | `8255c1acf50add5f68dfb551af977b53` | `8255c1acf50add5f68dfb551af977b53` | ✓ |
| `stroke.EUR.SH2B3_12q24.fit.rds` (anchor) | `a041eecc27f3086190069783eeb45ffe` | `a041eecc27f3086190069783eeb45ffe` | ✓ |
| `.planning/amendments/TRACK-A-FROZEN-NUMBERS.md` | `9d0405a4db95655b1be7401883d22165` | `9d0405a4db95655b1be7401883d22165` | ✓ |

## Other-terminal protection

**PID 830751** (results_identity_ld pipeline; canonical k2d identity-LD comparator per DEC-2026-04-25-01) preserved alive throughout V1 → V2 → V3 → V4 → V4-addendum → W4.5-A-initial → W4.5-A-refire → W4.5-A-continuation transitions. `bkill 0` was NEVER used. All bkills targeted explicit jobid lists scoped to W4 dispatches:
- W4.5-A initial bkill: 46 in-flight jobs from the scope-creep dispatch (2026-04-30T16:35)
- W4.5-A continuation v2 bkill: 9 v2-aggregator jobs 82073–82081 from the `--forcerun aggregate_qtl_coloc all_qtl_coloc` scope-creep recovery (2026-05-01T~19:55)

Lock-file edits across all dispatch versions were surgical (cp lock to lock.bak.${TS} before any mutation; surgical sed/grep filter to drop only qtl_coloc/finemap lines; preserve any results_identity_ld lines). Per memory `feedback_multi_terminal_staging.md` baked 2026-04-28: explicit-paths-only `git add` rule honored for every commit.

## Self-Check

- [x] **PASS/FAIL gate evaluated** — too_few_snps = 1005 / 1274 = 78.9% ≥ 800 → mechanically FAILED.
- [x] **Disposition recorded** — DEC-2026-05-01-02 + W4-DISPOSITION-REVISED.md + tracker v7 outcome_disposition=HONEST_FINDING.
- [x] **Refuted-hypothesis reasoning documented** — cache-staleness hypothesis from tracker v6 tested by W4.5-A continuation; Δ = 0 refutes it; LD-panel coverage + region-window choices identified as the actual constraint.
- [x] **3-layer contrast architecture established** — Layer-1 (51/96 = 53.1%) / Layer-2 (269/1274 = 21.1% feasibility ≡ 78.9% structural attrition) / Layer-3 (32/1274 = 2.5% substantive hits).
- [x] **W4.5-B SuSiE-RSS rebuild explicitly skipped** — rationale: data identifies LD coverage not iteration budget as constraint; rebuild risks TRACK-A-FROZEN md5 invariant break with low payoff. Per `feedback_rigor_over_speed.md` rigor-correct.
- [x] **All 4 pinned invariants intact** — 3 SH2B3 anchor md5s + TRACK-A-FROZEN-NUMBERS.md md5 unchanged across V1 → W4.5-A continuation.
- [x] **Other-terminal PID 830751 preserved** — `bkill 0` never used; surgical lock-file edits; explicit-jobid bkills only.
- [x] **Atomic commits landed** — V1–V4 dispatch trail + W4.5-a launcher (b368e0e) + scope-correction (986af29 + e40f058) + V6 dispatch (f33262f) + drain (f165e57) + aggregator 3rd-pass (bf2a18a) + W4 disposition (ad48257).
- [x] **No `data/processed/region_analysis/SH2B3_12q24/*` mutations** — manuscript Methods L90 + Discussion L220 + Limitations bullet 5 disclosure was DESIGNED to read "78.9% known cache-staleness issue"; the disposition revision flips that framing to "78.9% structural Layer-2 attrition" but does NOT touch frozen anchors. Wave 6 narrative captures the framing flip.

## Wave 5 readiness

**BLOCKED on Carter's stated precondition** (per session 2026-05-01 closing message): *"Wave 5 will fire from the orchestrator after the m3 AOU-1 dev fire returns and STATE.md frontmatter refreshes both tracks atomically."*

Current state of the precondition (verified 2026-05-01):

| Half | Status |
|------|--------|
| m3 AOU-1 dev fire returns | NOT MET — `m3-02-W2-dev-fire-and-validation` plan has no SUMMARY.md; m3-W3 ingest+resolver landed (recent commits 6d2e753…270fccc + v7→v8 CDR bump ac261f2) but the AOU-1 cohort dev-cell fire has not produced its summary or any dev10/dev100 markers under `data/processed/m3/` or `results/m3*` |
| STATE.md frontmatter refreshes both tracks atomically | NOT MET — `last_updated: 2026-04-30T16:25:08.057Z` predates today's W4.5-A continuation + W4 disposition + W3 code-review-fix work; `Current focus` and `Current Position` are Track B (m3) only; running `gsd-tools state begin-phase` for Track A would clobber Track B mid-flight |

**Wave 5 dispatch path when precondition is met:**
- W5 PLAN consumes the canonical 1274-JSON cache + the 5/6 fresh aggregator outputs (qtl_coloc_summary.tsv, tier_assignments.tsv, gene_tissue_matrix.tsv, gene_tissue_long.tsv, pph4_threshold_sweep.tsv); qtl_coloc_manifest.tsv stays at V4 mtime by architectural design.
- The 3-layer contrast architecture from W4-DISPOSITION-REVISED.md flows into W5 figures + aggregator manuscripts panels (Wave 6 narrative materializes the 78.9% Layer-2 framing transparently).
- D-TA-Wave1-headline (51/96 = 53.1% Layer-1 yield) decision is locked at PRESERVE-WITH-DISCLOSURE per W1 SUMMARY (NONE_CONVERGED at L ∈ {15, 20, 30}); Wave 6 carries the disclosure column.

## Open framing questions (carried into Wave 5/6)

1. **Layer-2 transparency framing in manuscript Methods + Limitations** — the 78.9% structural attrition needs explicit reviewer-defensible framing per `feedback_original_research_framing.md`. Suggested phrasing: "Per-region × per-(QTL source × tissue) coloc-feasibility yield is bounded by the GWAS×QTL panel SNP intersection at current LD-panel coverage and region-window choices; in this study, 269 of 1,274 = 21.1% of region/QTL/tissue tuples produced sufficient SNP overlap to attempt colocalization." NOT "78.9% failed".
2. **Sensitivity check on whether the 32 successes are concentrated in specific tissue × region classes** — useful for reviewer-defensibility but not blocking; W5 figure roster can show this as a stratified bar chart.
3. **OSF deviation log entry W7-pipeline #11** — pending W7 closeout: "W4.5-a re-fire outcome (PASSED/FAILED) + 3rd-pass aggregator refresh — tracker v7 will record"; now resolves as "FAILED on mechanical gate; HONEST_FINDING on strategic disposition; cache-staleness hypothesis refuted; 78.9% qtl_coloc rate adopted as canonical Layer-2 finding".
4. **Whether to surface the 235 `no_qtl_cs` disposition (Layer-2-feasible-but-no-credible-set) as a separate stratum** in Methods or to fold into the 78.9% bucket — design-expected outcome; default is to keep distinct in tracker v7 but pool into "non-success" in the headline reporting.

## Cross-references

- Predecessor disposition: `wave4_dispatch_tracker_v6.json` (DISPATCHED, supervisor PID 2670648 exited at 99.6%)
- Mechanical outcome: [`wave4_dispatch_tracker_v7.json`](wave4_dispatch_tracker_v7.json) (status=FAILED + outcome_disposition=HONEST_FINDING + historical_outcome block)
- Active narrative: [`W4-DISPOSITION-REVISED.md`](W4-DISPOSITION-REVISED.md) (refuted-hypothesis reasoning + 3-layer architecture)
- Decision anchor: [`../../DECISIONS.md`](../../DECISIONS.md) `## 2026-05-01 — DEC-2026-05-01-02`
- W4.5-A continuation quick task: [`../../quick/260501-r1q-w4-5-a-continuation-drain-final-5-and-ag/`](../../quick/260501-r1q-w4-5-a-continuation-drain-final-5-and-ag/)
- Layer-1 provenance: [`ta-sh2b3-W1-susie-rss-l-sweep-SUMMARY.md`](ta-sh2b3-W1-susie-rss-l-sweep-SUMMARY.md) (D-TA-Wave1-headline; 51/96 = 53.1%)
- W5 dependency root: [`ta-sh2b3-W5-aggregator-and-figure-refresh-PLAN.md`](ta-sh2b3-W5-aggregator-and-figure-refresh-PLAN.md)
- Wave 6 narrative branch root: [`ta-sh2b3-W6-rename-and-narrative-PLAN.md`](ta-sh2b3-W6-rename-and-narrative-PLAN.md) — D-TA-WAVE3-OUTCOME=BRANCH_C_SURVIVE flows here; W4 disposition flows here as the Layer-2 framing flip
- Materialization quick task: `260501-vxi` (this SUMMARY produced via `/gsd-quick materialize-w4-summary-from-disposition-doc-additive-no-state-writes-no-push`; additive only; no STATE.md writes; no push)
