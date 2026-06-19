---
phase: m3
scope: Wave-2 RE-SCOPE (real-cohort LD compute)
reviewers: [codex]
reviewed_at: 2026-06-19T01:29:44Z
plans_reviewed:
  - m3-02b-W2-rescope-split-stitch-code-PLAN.md
  - m3-02c-W2-rescope-quota-probe-and-gonogo-PLAN.md
reviewer_runtime_notes: >
  Single external reviewer. Runtime = claude-vscode, so the Claude CLI is
  skipped for independence (it is this session's own model). Gemini, OpenCode,
  and CodeRabbit CLIs are not installed on the NCSU node. Codex CLI 0.141.0
  (ChatGPT-authed) was installed for this review and run via
  `codex exec --skip-git-repo-check --sandbox read-only`.
---

# Cross-AI Plan Review — Phase M3 Wave-2 RE-SCOPE

Reviews the two NEW re-scope plans (`m3-02b` code/Wave-0, `m3-02c` quota+probe+gonogo/Wave-1).
The original m3-00..m3-05 plans were out of scope for this review.

---

## Codex Review (gpt-5-codex, 0.141.0)

### Summary

The plans have strong operational discipline and correctly separate code work from live AoU
probing. However, as written they do not yet achieve a statistically defensible or operationally
complete re-scope. The critical flaw is that the stitch zeros all LD between adjacent 10 Mb
sub-regions, including variants immediately across an arbitrary boundary; the accepted decision
only justifies zeroing pairs more than 50 Mb apart. There are also downstream payload
incompatibilities, impractical stitched-RDS sizes, incomplete cost-model inputs, and a quota
dependency that can pass before quota is granted. These require plan revision before execution.

### Strengths

- Correctly identifies sample count as the matmul inner dimension and invalidates the synthetic cost estimate.
- Separates NCSU-local implementation from controlled-tier compute and egress.
- Places the quota request first and explicitly identifies the `N2_CPUS` versus generic-CPU trap.
- Preserves parent/sub-region provenance instead of relying only on filename parsing.
- Includes data-layer validation rather than trusting `_SUCCESS`.
- Keeps production outside the probe plan and defines an explicit budget predicate.
- Uses real-cohort measurements and records spill behavior.
- Includes restartability and the known Workbench preparation hazards.
- Recognizes that sparse-payload compatibility must be tested before production.

### Concerns

- **HIGH — The block-diagonal stitch changes the statistical model incorrectly.** Adjacent 10 Mb
  sub-regions share a boundary, so cross-block variants can be only base pairs apart. Setting all
  cross-block LD to zero is NOT equivalent to the accepted "LD beyond 50 Mb is zero" treatment.
  It can split loci, distort PIPs, create artificial independent signals, and produce credible
  sets determined by arbitrary window boundaries. HLA and inversion regions are especially vulnerable.

- **HIGH — The proposed parent `.rds` is likely operationally intractable.** `Matrix::bdiag` is
  sparse only between blocks; each 60–75k-variant correlation block is effectively dense.
  Converting blocks to R doubles and then `dgCMatrix` can still require hundreds of GB for a
  600k-variant parent, plus sparse-index overhead and expensive `xz` serialization. The downstream
  loader then calls `as.matrix(R)`, defeating the sparse representation.

- **HIGH — The existing fine-mapping loader does not accept the proposed payload schema.**
  `ld_npz_to_rds.R` and the proposed stitch emit `list(ld, snp_ids, provenance)`, while
  `run_susie_rss.R::load_ld_matrix()` expects `obj$R` and `obj$variants`. It also explicitly
  returns `as.matrix(R)`. A test that calls `susie_rss()` directly would pass while the actual
  project loader rejects the file.

- **HIGH — Variant-to-LD alignment checks are insufficient.** Ordering only by `subregion_index`
  and checking monotonic positions does not prove correspondence with the LD rows. Most selected
  identifiers may be rsids, for which the proposed position check is skipped. Duplicate rsids,
  multiallelic variants, liftover collisions, dropped variants, and allele swaps are not covered.

- **HIGH — Interval semantics can duplicate or omit boundary variants.** The plan defines half-open
  sub-windows, but `compute_region_ld()` constructs a Hail interval from `chr:start-end`, whose
  endpoint semantics are not explicitly reconciled with BED-style coordinates. Adjacent sub-regions
  may both include the boundary position or leave a gap.

- **HIGH — The cost model lacks the required population-wide inputs.** The projection currently has
  neither ancestry-specific `n_var` nor `block_count`. These cannot be estimated reliably from span
  alone, especially for HLA and ancestry-dependent MAF density. The plan alternates between
  "322 cells" and a post-split compute manifest that necessarily has more than 322 compute cells.

- **HIGH — The EUR probe should not be optional.** EUR is the largest sample panel and is the
  workload most likely to spill at `cores=2`. A linear 3.01 multiplier does not validate executor
  memory, shuffle, serialization, or scheduling behavior.

- **HIGH — Critical tests are allowed to skip while the plan declares success.** The stitch and
  sparse-loader tests may skip when R, Matrix, or susieR are unavailable. An `UNVERIFIED` sentinel
  does not satisfy the must-have that assumption A6 is confirmed.

- **MEDIUM — Quota task completion is internally inconsistent.** Task 1 is blocking on the quota
  grant, but its acceptance criteria only prove that a request was filed. Task 2 requires the
  granted ceiling. Filing and grant should be separate gates.

- **MEDIUM — Dev-selector expansion is underspecified and may not work as described.** Filtering for
  `m2_region_00040` after the parent has been removed produces no selected row to expand. Resolution
  must start from requested `(parent_id, ancestry)` tuples. Expanding every sub-region also turns
  the "dev-10" set into a substantially larger workload.

- **MEDIUM — The 10 Mb heuristic is not adequately gated.** A single `region_00040__sub00` probe
  cannot validate variant density for HLA or all xlarge regions. The target is ≤75k variants, but
  no complete count pass confirms that invariant.

- **MEDIUM — Cost accounting measures only Stage 4.** Filtering, `count_rows`, variant collection,
  checkpointing, output writes, sidecars, retries, cluster startup, master cost, scratch storage,
  and idle time are omitted. The proposed "cluster-hours" metric counts workers but not the master.

- **MEDIUM — No hard runaway-cost controls are executable.** The threat model says the cluster is
  stopped after the probe, but the task does not require a timeout, maximum probe spend, automatic
  stop, or a stop-confirmation artifact.

- **MEDIUM — Egress output requirements remain incomplete.** Current `.npz` output contains LD,
  variant IDs, and rsids but no allele-frequency metadata, despite the phase deliverable requiring
  LD plus AF metadata. The probe also does not project output and bundle sizes.

- **MEDIUM — Stitch input identity is ambiguous across ancestries.** The manifest contains AFR and
  EUR rows with the same sub-region IDs, but the stitch CLI has no ancestry parameter. It must
  reject mixed-ancestry, missing, duplicate, or extra child inputs.

- **MEDIUM — Path classification assertions are too weak.** Testing only that sub-regions are
  "not xlarge" does not prove they avoid A.3. The actual router demotes any span over 10 Mb to A.3
  regardless of manifest class.

- **LOW — Grep counts and minimum-line checks are weak acceptance criteria.** They prove text
  exists, not that contracts are correctly implemented.

### Suggestions

1. Replace the zeroed arbitrary-boundary stitch with one of: overlapping compute windows with
   non-overlapping core ownership and computed cross-boundary LD; biologically motivated boundaries
   plus overlap/buffer sensitivity analysis; or treating sub-regions as separate fine-mapping units
   rather than constructing a false parent matrix. At minimum, compute all pairs within the accepted
   50 Mb radius across neighboring sub-regions.
2. Add boundary validation: shift the 10 Mb grid by 5 Mb; require stable lead PIPs and credible
   sets; explicitly test loci within 1–2 Mb of every split boundary; prohibit a production split
   through a validated credible set or known long-range-LD locus.
3. Avoid a monolithic parent RDS. Keep an indexed, on-disk block collection and load only the
   variants required for each fine-mapping analysis. Benchmark peak RAM, disk size, read time, and
   downstream densification on a realistically sized fixture.
4. Make the actual `run_susie_rss.R::load_ld_matrix()` contract the A6 test target. Standardize the
   payload to `R` plus a variant table containing at least chromosome, position, ref, alt, and SNP
   ID. Test the complete resolver-to-SuSiE path.
5. Use GRCh38 `variant_ids` as the ordering key before liftover. Require exact uniqueness; exact
   child count and child-index coverage; no duplicate variants across windows; bijective row/column
   permutation after liftover filtering; allele-aware matching, not position-only matching.
6. Define interval semantics explicitly and test variants exactly at `start`, `end`, and neighboring
   boundaries through `compute_region_ld()`.
7. Add an inexpensive in-perimeter count/preflight pass over every post-split ancestry cell. Record
   actual `n_var`, actual path A.1/A.2/A.3, estimated block count, and output-size estimate.
   Automatically split any cell exceeding the threshold.
8. Make at least one EUR cell mandatory. Also include either an HLA sub-region probe or a mandatory
   HLA count/size preflight.
9. Price actual compute rows, not "322 post-split cells." Keep separate totals for: 322 logical
   parent panels; expanded ancestry-specific compute cells; aggregate parent costs.
10. Base rates on actual execution path and normalize them to cluster configuration. Include
    end-to-end wall time, worker and master cost, storage, output bytes, retries, and a contingency
    factor derived from observed variance.
11. Split the quota workflow into `ticket filed` and `quota granted` gates. Task 2 must depend on a
    recorded numeric grant.
12. Add probe safeguards: maximum wall time per cell, maximum probe credits, spill/OOM kill
    criteria, guaranteed cluster shutdown, and a shutdown-verification record.
13. Do not permit critical R tests to skip in the designated M3 conda environment. Missing
    R/Matrix/susieR should fail Plan 02b.
14. Add AF metadata to the output contract and project egress bundle sizes before production.

### Risk Assessment

**Overall risk: HIGH.** Operational controls are generally strong, but the current block-diagonal
design can produce statistically invalid fine-mapping while passing every proposed test. The
stitched payload is also incompatible with the current loader and may be too large to materialize
or serialize. Finally, the proposed probe cannot yet support a defensible full-panel cost
projection because EUR is optional and actual per-cell variant/block counts are absent. These are
goal-level failures, not minor implementation details.

---

## Consensus Summary

Single external reviewer (Codex), so "consensus" here is the orchestrator's triage of Codex's
findings against the locked re-scope spec and the in-pipeline `gsd-plan-checker` PASS. The
plan-checker verified *internal* plan quality (structure, REQ coverage, source-contract names,
sequencing) and passed; Codex attacked the *external* validity of the design and surfaced
goal-level risks the checker did not. Both are correct at their altitude — these are complementary,
not contradictory.

### Highest-priority concerns (recommend addressing before executing m3-02b/02c)

1. **Arbitrary-boundary zeroing ≠ the accepted 50 Mb banding** (Codex HIGH #1). The locked decision
   (WAVE-2 HIGH-3) zeroes LD beyond ~50 Mb, where it is genuinely ≈0. A 10 Mb hard split zeroes LD
   between variants that may be base-pairs apart across a window boundary — a different, stronger,
   and biologically false claim. This is the single most important finding: it can silently corrupt
   downstream SuSiE-RSS credible sets while every proposed test passes. **Fix direction:** overlapping
   compute windows that retain cross-boundary pairs within the 50 Mb radius (the research's own
   Q-RS3 contemplated contiguous windows; this makes them overlap-buffered), or treat sub-regions as
   independent fine-mapping units rather than fabricating a single parent matrix.

2. **Loader payload-schema mismatch** (Codex HIGH #3). The real consumer `run_susie_rss.R::load_ld_matrix()`
   expects `obj$R` + `obj$variants` and does `as.matrix(R)`. The plan emits `list(ld, snp_ids, provenance)`
   and targets a sparse payload. The A6 verify task must hit the *actual* loader contract, not
   `susie_rss()` directly. (The plan-checker flagged this exact path as an INFO observation; Codex
   independently escalates it to HIGH — concordant signal, raise its severity.)

3. **Stitched-parent `.rds` may be operationally intractable** (Codex HIGH #2). bdiag is sparse only
   between blocks; each block is dense; a 600k-variant parent can be hundreds of GB and the loader
   densifies anyway. Reconsider the monolithic-parent design vs an indexed on-disk block collection.

4. **EUR probe must be mandatory, not optional** (Codex HIGH #7). EUR (220k samples) is the spill-risk
   workload and the cost driver; the 3.01× sample-ratio multiplier is assumed, not measured. Promote
   the optional 3rd cell to required.

5. **Cost model needs real `n_var` / `block_count` per cell, including master + overhead** (Codex HIGH #6,
   MEDIUM cost-accounting). A defensible budget needs a cheap in-perimeter count/preflight over the
   post-split cells, not span-derived guesses; and cluster-hours must include the master.

6. **Tighten correctness gates that the plan lets pass weakly:** quota filed-vs-granted split (MEDIUM);
   no skip-allowed for R/Matrix/susieR tests in the M3 env (HIGH); allele-aware variant↔LD alignment
   (HIGH); explicit interval/boundary semantics (HIGH); executable runaway-cost stop + shutdown-verify
   artifact (MEDIUM); AF metadata in the egress contract (MEDIUM).

### Divergent / orchestrator note

Codex's framing of the 10 Mb split as "statistically invalid" is correct *only because the plan
pairs the split with hard zeroing at the window boundary*. The locked decision to split xlarge
regions is NOT itself in question — the defect is in the *stitch*, not the *split*. The cleanest
reconciliation (preserves the locked split + cluster sizing + cost-probe decisions, fixes the
finding) is **overlapping windows with cross-boundary LD retained inside the 50 Mb radius** + the
real-loader payload contract. That is a `/gsd-plan-phase m3 --reviews` revision of 02b's stitch
task + 02c's EUR/cost tasks, not a re-scope of the phase.

### Recommended next step

`/gsd-plan-phase m3 --reviews` to fold these findings into m3-02b (stitch redesign, real-loader A6
target, no-skip R tests, allele-aware alignment, interval semantics) and m3-02c (mandatory EUR cell,
preflight count pass, master-inclusive cost accounting, filed-vs-granted quota split, executable
cost stop). The locked decisions (A.3 fix correct, ordering A, cohorts intact, split-the-xlarge,
n2-highmem sizing, probe-before-fire) remain untouched.
