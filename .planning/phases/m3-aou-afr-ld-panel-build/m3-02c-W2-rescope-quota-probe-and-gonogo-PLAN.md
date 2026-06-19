---
phase: m3-aou-afr-ld-panel-build
plan: 02c
type: execute
wave: 1
depends_on: ["02b"]
files_modified:
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md
  - src/python/redo_ld_cost_model.py
  - tests/m3/test_redo_ld_cost_model.py
autonomous: false
nyquist_compliant: true
requirements:
  - REQ-AOU-LD-EGRESS
  - REQ-AOU-LD-VALIDATION
  - REQ-PUBLIC-DATA-ONLY
  - REQ-PATH-PARAMETERIZATION

must_haves:
  truths:
    - "Carter files an AoU/Verily quota-increase ticket naming N2_CPUS >= 400, region us-central1 (24x n2-highmem-16 workers + 1 n2-highmem-16 master = 400 vCPU; ask 400-512 for headroom) — the LONGEST-LEAD item, surfaced FIRST; a record of the ticket lands at m3-W2-quota-ticket.md before the probe."
    - "cluster_size = min(granted N2 quota, 400 vCPU) is a TUNING knob, not a correctness gate; if only ~256 vCPU (16 workers) is granted, the probe still runs and the projection scales wall-clock — the split (m3-02b) is what makes xlarge tractable, not the cluster size."
    - "Before the probe, the AoU env panel is confirmed to show n2-highmem workers (NOT n1-highmem) + region us-central1; the Q-RS2 executor config (cores=2 / 24-28g / 8-12g overhead) from m3-02b is applied and validated (no spill at cores=2, else drop to cores=1) on the probe."
    - "The 3 prep landmines are re-applied on the fresh cluster: symlink ~/coloc_analysis -> synced repo; pin WORKSPACE_BUCKET=gs://rw-migration-aou-rw-476cdac2 (HARD os.environ override, not setdefault); os.chdir(~/coloc_analysis) before the per-region loop (per SKILL.md)."
    - "The cost probe fires TWO AFR cells on the sized cluster: one WHOLE medium region (m2_region_00006, 122,678 var, 17.7 Mb) + one xlarge SUB-REGION (m2_region_00040__sub00, ~10 Mb / ~69k var). An optional THIRD cell = one EUR sub-region of the same parent (measures the EUR/AFR factor vs the 3.01x sample-ratio assumption A7)."
    - "For each probe cell the metric set is captured to m3-W2-cost-probe.tsv: blocks_per_min, block_count, peak_executor_mem, any_spill, wall_clock_min, cluster_vcpu, cluster_hours, tagged by (ancestry, region_class). _SUCCESS is NOT evidence of data — each cell is verified at the data layer (gsutil du on the .npz/.bm + Hail count) per D-M3-10."
    - "redo_ld_cost_model.py extrapolates the measured blocks_per_min to ALL 322 post-split cells (small/medium/sub-region classes only — the xlarge=24h rows are gone), applies the measured-or-3.01x EUR factor, sums xlarge parents as Sigma over their N sub-regions, and writes the new PROJECTED cluster-hours + credit-$ to m3-W2-budget-redo.md."
    - "The go/no-go gate is encoded with the EXACT predicate: fire the full 322 iff PROJECTED x 1.3 <= BUDGET_CAP_CLUSTER_H (from GATE-1). Disposition is one of GREEN (fire full 322 in m3-04), YELLOW-narrow-radius (drop export band toward Pan-UKBB 10 Mb, re-probe), YELLOW-finer-split (lower --max-subregion-span-mb for the cost-driver class, re-probe), or RED (re-negotiate budget / phase the fire). The disposition is recorded in m3-W2-budget-redo.md with the computed PROJECTED, BUDGET_CAP_CLUSTER_H, and the 1.3x headroom check."
    - "The full 322-cell production fire is EXPLICITLY OUT of scope here — it stays in Wave 4 (m3-04). This plan ends at a GREEN/RED go/no-go decision + a defensible re-derived budget."
  artifacts:
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md"
      provides: "Record of the N2_CPUS>=400 us-central1 quota request (channel, date filed, granted ceiling)"
      contains: "N2_CPUS"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv"
      provides: "Per-probe-cell blocks_per_min + block_count + peak_mem + spill + cluster_hours tagged by (ancestry, region_class)"
      contains: "blocks_per_min"
    - path: "src/python/redo_ld_cost_model.py"
      provides: "Extrapolate measured blocks_per_min to 322 post-split cells + evaluate PROJECTED x 1.3 <= BUDGET_CAP gate"
      min_lines: 60
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md"
      provides: "New PROJECTED cluster-h + credit-$ + the GREEN/YELLOW/RED disposition with the exact 1.3x predicate evaluated"
      contains: "PROJECTED"
    - path: "tests/m3/test_redo_ld_cost_model.py"
      provides: "Unit tests for the extrapolation arithmetic + the 1.3x gate predicate (synthetic probe TSV; no cluster)"
  key_links:
    - from: "src/python/redo_ld_cost_model.py"
      to: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv"
      via: "reads measured blocks_per_min per (ancestry, region_class)"
      pattern: "blocks_per_min"
    - from: "src/python/redo_ld_cost_model.py"
      to: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md"
      via: "writes PROJECTED + the PROJECTED x 1.3 <= BUDGET_CAP disposition"
      pattern: "BUDGET_CAP"
---

<objective>
Resolve the two live-only items the m3-02b code re-scope cannot: (1) the AoU N2 vCPU quota grant (the longest-lead human action — file FIRST), and (2) the real-cohort cost probe that re-derives the known-stale ~1,117 cluster-h budget. The probe fires the minimal defensible pair — one WHOLE medium region (region_00006) + one xlarge SUB-REGION (m2_region_00040__sub00) — on the sized n2-highmem-16 cluster, measures blocks_per_min, extrapolates to all 322 post-split cells, and evaluates the go/no-go gate `PROJECTED × 1.3 ≤ BUDGET_CAP_CLUSTER_H`.

Purpose: The dev-10 fire was sized off a 2,000-sample synthetic repro (36-110x too cheap). Before any production spend, the budget must be rebuilt bottom-up from measured real-cohort throughput, and the full fire must be gated on it. This plan ends at a GREEN/RED decision; the full 322-cell fire stays in Wave 4 (m3-04).

Output: the quota-ticket record, the cost-probe TSV, the cost-model redo script + tests, and the budget-redo memo with the disposition.

LOCKED (do NOT relitigate): A.3 fix correct; ordering A kept; cohorts intact; the split (m3-02b) is the structural fix. Cluster size is a tuning knob, not a correctness gate.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/STATE.md
@.planning/phases/m3-aou-afr-ld-panel-build/WAVE-2-RESCOPE-real-cohort-compute.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
@.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md
@.claude/skills/aou-ld-pipeline/SKILL.md

<interfaces>
<!-- Inputs from m3-02b (Wave 0) + the live coordinates the probe needs. -->

From m3-02b (must exist before this plan runs):
- config/ld_regions.tsv now contains m2_region_00040__sub00 .. __subNN compute rows (xlarge split)
- config/ld_regions_dev.tsv expanded to include m2_region_00040 sub-rows
- AOU-2 notebook carries the Q-RS2 executor config (cores=2 / 24g / 10g / 24g) before pyspark import
- A6 verdict at tests/m3/A6_sparse_payload_verdict.txt

Live coordinates (SKILL.md):
- Workspace aou-rw-476cdac2 · project wb-perky-corn-6639 · bucket gs://rw-migration-aou-rw-476cdac2
- Run branch m3-W2-aou-deltas (NOT main — clone-from-main wedges deterministically)
- Cohorts (intact): AFR_pca 73,122 x 20,767,864 ; EUR_pca 220,098 x 11,375,140

Q-RS1 quota (verbatim):
- Blocking dimension = regional N2_CPUS in us-central1 (separate from generic CPUS / N1)
- Request must name N2 family + us-central1 explicitly; channel is likely an AoU/Verily ticket (VPC-SC-gated, not self-serve Console) — A1
- Grantable ceiling unknown (A2); cluster_size = min(granted N2 quota, 400 vCPU)

Q-RS5 probe + gate (verbatim):
- Two AFR cells: WHOLE region_00006 (122,678 var) + xlarge SUB-REGION m2_region_00040__sub00 (~69k var); optional 3rd = EUR sub-region
- Metric per cell: blocks_per_min = Stage-4 blocks / Stage-4 wall-minutes ; block_count ; peak exec mem + spill ; cluster-hours = wall_h x n_workers ; tag (ancestry, region_class)
- Extrapolation: per-region cluster-h = block_count / blocks_per_min / 60 x factor; AFR->EUR x measured-or-3.01x (A7); xlarge parent = Sigma over N sub-regions
- n2-highmem-16 price ~$0.95-1.10/hr/worker (A8 — confirm); 24 workers ~= $23-26/hr
- GATE: fire iff PROJECTED x 1.3 <= BUDGET_CAP_CLUSTER_H ; dispositions GREEN / YELLOW-narrow-radius / YELLOW-finer-split / RED

GATE-1 budget (STATE.md): cost/credit CLEARED 2026-06-12 by Carter; BUDGET_CAP_CLUSTER_H is Carter's approved credit cap — capture the numeric value into m3-W2-budget-redo.md at gate time. The old ~1,117 cluster-h was the basis for that approval; the redo replaces the PROJECTED, the CAP is Carter's standing approval (re-confirm the number with Carter at the gate).

D-M3-10: every MT/.npz/.bm write is contents-validated, not _SUCCESS-only (gsutil du + Hail count). The probe cells inherit this.
</interfaces>
</context>

<tasks>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 1: Carter files the N2_CPUS >= 400 us-central1 quota-increase ticket (LONGEST-LEAD — surfaced first)</name>
  <files>.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS1" (lines 16-40) — quota mechanics + the N1-vs-N2 trap + request path + A1/A2 flags
    - .claude/skills/aou-ld-pipeline/SKILL.md "Coordinates" + "RW2.0 is a MIRROR ... VPC-SC perimeter" (the request path is perimeter-gated)
    - memory reference_wb_cli_hpc_setup (control-plane vs data-plane boundary)
  </read_first>
  <action>See the human_gate block. Carter human action; no agent compute. The agent verifies acceptance_criteria after Carter records the ticket.</action>
  <human_gate>
    <gate>AoU N2 vCPU quota grant for the sized re-fire cluster</gate>
    <description>
      File the quota-increase request that unblocks the sized cluster. This is the LONGEST-LEAD item (days to ~2 weeks per Q-RS1 A1) and it GATES the cost probe — file it before anything else in this plan.

      The request MUST name, EXPLICITLY:
      - Quota metric: N2_CPUS (NOT generic CPUS / N1 — raising CPUS will NOT unblock an all-N2 cluster; this is the Q-RS1 N1-vs-N2 trap).
      - Region: us-central1 (reconfirm in the AoU env panel before filing — A1).
      - Amount: >= 400 vCPU (24x n2-highmem-16 workers + 1 n2-highmem-16 master = 25 x 16 = 400); ask 400-512 to leave headroom.

      Channel (Q-RS1 A1): the AoU RW2.0 / Verily billing project is org-managed and the Console quota page is likely VPC-SC-restricted — the realistic path is an AoU support / Verily request ticket, not a self-serve Console edit. If the Console quota page IS reachable from inside the perimeter (IAM and Admin -> Quotas -> filter "N2 CPUs" / region us-central1 -> Edit Quotas), use it; otherwise file via AoU support.

      Record the request at .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md with: the channel used, the metric/region/amount requested, the date filed, the ticket/request ID, and (when it comes back) the GRANTED ceiling. If the grant is &lt; 400, set cluster_size = min(granted, 400) and note it — the probe still runs, the projection just scales wall-clock (cluster size is a tuning knob, not a correctness gate).
    </description>
    <unblocks>Task 2 (the cost probe — needs the sized cluster) and ultimately Wave 4 (m3-04) full fire</unblocks>
    <how-to-resolve>
      1. Reconfirm workspace region == us-central1 in the AoU env panel.
      2. File the N2_CPUS >= 400 (ask 400-512) us-central1 request via AoU support ticket (or Console if reachable).
      3. Write m3-W2-quota-ticket.md with channel + metric=N2_CPUS + region=us-central1 + amount + date + request ID.
      4. When granted, append the GRANTED ceiling and set cluster_size = min(granted, 400).
      5. Type "filed" to record the gate.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md &amp;&amp; grep -c "N2_CPUS" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md` exits 0.
    - `grep -c "N2_CPUS" m3-W2-quota-ticket.md` (in the phase dir) returns >= 1.
    - `grep -c "us-central1" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md` returns >= 1.
    - `grep -cE "40[0-9]|4[0-9][0-9]|5[0-9][0-9]" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md` returns >= 1 (the >=400 amount).
    - `grep -ci "filed\|request id\|ticket" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md` returns >= 1.
  </acceptance_criteria>
  <done>
    The N2_CPUS >= 400 us-central1 quota request is filed (correct family + region named) and recorded with its channel, amount, date, and request ID. cluster_size = min(granted, 400) noted once the grant returns.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: Fire the 2-3 cell cost probe on the sized n2-highmem-16 cluster + record m3-W2-cost-probe.tsv</name>
  <files>.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS5" (lines 159-204) — probe design + exact metric set + extrapolation
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS2" (lines 43-83) — executor config to validate on the probe
    - .claude/skills/aou-ld-pipeline/SKILL.md "Fresh-clone re-run checklist" + "LD compute (AOU-2) — specifics" + "The invariants" (the 3 prep landmines + data-layer verify)
    - .planning/notebooks/AOU-2_per_region_ld.ipynb (the Q-RS2 executor cell + the per-region loop; from m3-02b)
    - config/ld_regions_dev.tsv (expanded by m3-02b to include m2_region_00040 sub-rows)
  </read_first>
  <action>See the human_gate block. Carter fires the probe inside the AoU perimeter; the agent prepares the probe manifest hint + verifies the recorded TSV afterward. The agent's only pre-fire action: confirm config/ld_regions_dev.tsv (or a 2-3 row probe manifest) contains exactly the probe cells m2_region_00006 (AFR, whole) + m2_region_00040__sub00 (AFR, sub-region) [+ optional m2_region_00040__sub00 EUR].</action>
  <human_gate>
    <gate>Real-cohort cost probe on the sized cluster (2-3 cells)</gate>
    <description>
      Fire the minimal defensible probe to measure real-cohort throughput. Pre-flight (SKILL.md fresh-clone checklist), then fire 2-3 cells, then record the metric set.

      PRE-FLIGHT (re-apply on the fresh sized cluster):
      - Start the cluster on the granted N2 quota: workers n2-highmem-16 (128 GB — stops the spill), master n2-highmem-16, vCPU = cluster_size = min(granted N2 quota, 400). Confirm in the env panel that workers are n2-highmem (NOT n1-highmem) and region == us-central1.
      - git checkout m3-W2-aou-deltas (NOT main) -> git pull -> git checkout -f (the Workbench filter re-dirties notebooks).
      - The 3 prep landmines: symlink ~/coloc_analysis -> synced repo; pin WORKSPACE_BUCKET=gs://rw-migration-aou-rw-476cdac2 via a HARD os.environ override (not setdefault); os.chdir(~/coloc_analysis) before the per-region loop.
      - The AOU-2 Q-RS2 executor cell (cores=2 / 24g / 10g overhead / 24g driver) runs BEFORE the pyspark/hail import. Confirm it bound (print PYSPARK_SUBMIT_ARGS).

      FIRE 2-3 CELLS (AFR primary; use the expanded dev/probe manifest):
      1. WHOLE medium region: m2_region_00006 (AFR, 122,678 var, 17.7 Mb) — the best-characterized region from dev-10; direct before/after comparability.
      2. xlarge SUB-REGION: m2_region_00040__sub00 (AFR, ~10 Mb / ~69k var) — proves the split makes the worst region tractable.
      3. OPTIONAL EUR sub-region: m2_region_00040__sub00 (EUR, 220k samples) — measures the EUR/AFR factor empirically (A7) instead of assuming exactly 3.01x. Skip if credits are tight and use 3.01x +/- 20%.

      VALIDATE THE EXECUTOR CONFIG ON THE PROBE: watch for executor spill at cores=2. If EUR spills, note it and drop to cores=1 for the production config (record which cores value the projection assumes).

      DATA-LAYER VERIFY (D-M3-10 — _SUCCESS is NOT evidence): for each cell, gsutil du -s the produced .npz/.bm under gs://rw-migration-aou-rw-476cdac2/ld/{AFR_aou,EUR_aou}/ (must be >> 0) AND a Hail/np read-back count, before recording the cell as complete.

      RECORD m3-W2-cost-probe.tsv (one row per cell) with the EXACT columns:
      `region_id  ancestry  region_class  n_var  block_count  stage4_wall_min  blocks_per_min  peak_executor_mem_gib  any_spill  cluster_vcpu  n_workers  cluster_hours`
      where blocks_per_min = block_count / stage4_wall_min and cluster_hours = (stage4_wall_min / 60) * n_workers. Tag each row by (ancestry, region_class). Capture peak_executor_mem + any_spill from the Spark UI.
    </description>
    <unblocks>Task 3 (cost-model redo + go/no-go gate)</unblocks>
    <how-to-resolve>
      1. Pre-flight per SKILL.md (sized cluster, 3 landmines, Q-RS2 cell bound).
      2. Fire region_00006 (AFR) + m2_region_00040__sub00 (AFR) [+ EUR optional].
      3. Data-layer-verify each cell (gsutil du + count).
      4. Write the 12-column m3-W2-cost-probe.tsv (header + 2-3 rows).
      5. Type "probe-recorded" to resume; Task 3 reads the TSV.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv &amp;&amp; head -1 .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv | grep -q "blocks_per_min" &amp;&amp; test $(tail -n +2 .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv | grep -c .) -ge 2 &amp;&amp; echo OK</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` exits 0.
    - `head -1 .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` contains all of: region_id, ancestry, region_class, block_count, blocks_per_min, cluster_hours (grep -c each >= 1).
    - `grep -c "m2_region_00006" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` returns >= 1 (whole-region cell).
    - `grep -c "m2_region_00040__sub00" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` returns >= 1 (sub-region cell).
    - `tail -n +2 .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv | grep -c .` returns >= 2 (>= 2 measured cells).
    - `grep -ci "spill" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` returns >= 1 (the any_spill column header / value present).
  </acceptance_criteria>
  <done>
    The 2-3 probe cells fire on the sized n2-highmem-16 cluster; the Q-RS2 executor config is validated (spill behavior recorded); each cell is data-layer-verified per D-M3-10; m3-W2-cost-probe.tsv carries the full metric set tagged by (ancestry, region_class).
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: redo_ld_cost_model.py extrapolation + the PROJECTED x 1.3 <= BUDGET_CAP go/no-go gate + budget-redo memo</name>
  <files>src/python/redo_ld_cost_model.py, tests/m3/test_redo_ld_cost_model.py, .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS5 Extrapolation" + "Go / no-go threshold structure" (lines 182-198) — the exact arithmetic + the PROJECTED x 1.3 <= BUDGET_CAP predicate + the 4 dispositions
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv (Task 2 output — the measured blocks_per_min input)
    - src/python/build_ld_region_manifest.py (est_cluster_hours table lines 346-357 — the STALE model this REPLACES; the projection TSV the extrapolation iterates over, now with split_status + n_subregions from m3-02b)
    - config/ld_regions.tsv + m3-region-class-projection.tsv (the 322 post-split cells to extrapolate over)
  </read_first>
  <behavior>
    - test_blocks_per_min_extrapolation: given a synthetic probe TSV (AFR-medium blocks_per_min=R1, AFR-subregion blocks_per_min=R2) and a synthetic 322-cell projection, assert per-region cluster-h = block_count / blocks_per_min / 60 is applied per matching (ancestry, region_class); EUR cells get blocks_per_min / EUR_factor (measured-or-3.01x).
    - test_xlarge_parent_sums_subregions: an xlarge parent's aggregate cost == sum over its N sub-region rows (no single 24h figure; the stale xlarge=24.0 row is absent from the post-split projection).
    - test_eur_factor_default_3_01: with no measured EUR cell, the model applies EUR_factor = 3.01 with a +/- 20% band recorded; with a measured EUR cell it uses the measured ratio.
    - test_gate_predicate_green: PROJECTED such that PROJECTED * 1.3 <= BUDGET_CAP -> disposition == "GREEN".
    - test_gate_predicate_red: PROJECTED such that PROJECTED * 1.3 > BUDGET_CAP at all levers -> disposition in {"YELLOW-narrow-radius","YELLOW-finer-split","RED"} per the decision tree (the function returns the predicate result + the recommended next lever; assert RED when PROJECTED * 1.3 > BUDGET_CAP and no lever room flag is set).
  </behavior>
  <action>
    1. Write `src/python/redo_ld_cost_model.py`:
       - `load_probe_rates(probe_tsv) -> dict[(ancestry, region_class) -> blocks_per_min]` reading m3-W2-cost-probe.tsv.
       - `eur_factor(probe_rates) -> (factor, source)`: if both an AFR and EUR rate exist for the same class, factor = afr_blocks_per_min / eur_blocks_per_min (EUR is slower => factor > 1); else (3.01, "sample-ratio-assumed-A7") with a +/- 20% band.
       - `project_cell_hours(projection_df, probe_rates, eur_factor) -> DataFrame`: per cell, region_block_count is read from the projection (or computed from n_var + radius band + block_size 4096); per-region cluster-h = block_count / matched_blocks_per_min / 60; EUR cells divide the AFR rate by eur_factor (heavier => more hours). xlarge parents are NOT priced directly — they are the sum over their split_status=="subregion" rows (group by parent_region_id).
       - `total_projected(projected_df) -> float` (PROJECTED cluster-h over all 322 post-split cells).
       - `evaluate_gate(projected, budget_cap_cluster_h, *, lever_room=None) -> dict` returning `{projected, budget_cap, headroom_ok: projected * 1.3 <= budget_cap, disposition}` where disposition is "GREEN" if headroom_ok else the recommended lever ("YELLOW-narrow-radius" if any cell radius > sub_span i.e. there is band to cut; "YELLOW-finer-split" if a specific (ancestry, region_class) dominates and can be split finer; else "RED"). Encode the EXACT predicate `projected * 1.3 <= budget_cap` verbatim.
       - `main()` CLI: `--probe-tsv --projection --budget-cap-cluster-h --out-budget-md`; writes m3-W2-budget-redo.md with PROJECTED, BUDGET_CAP_CLUSTER_H, the `PROJECTED * 1.3 <= BUDGET_CAP` evaluation, the credit-$ at the n2-highmem-16 rate (A8 ~$0.95-1.10/hr/worker; flag for confirmation), and the disposition.
       - REQ-PATH-PARAMETERIZATION: no hardcoded /share/clintonlab|/rs1/researchers|/gpfs_common paths.

    2. Write `tests/m3/test_redo_ld_cost_model.py` with the 5 behavior tests above using synthetic in-memory probe TSV + projection DataFrames (no cluster, no AoU). Assert the exact gate predicate (projected * 1.3 <= budget_cap) on both the GREEN and RED sides.

    3. Run redo_ld_cost_model.py against the real m3-W2-cost-probe.tsv + the post-split projection + the BUDGET_CAP_CLUSTER_H (confirm the numeric value with Carter; the old ~1,117 cluster-h was the basis for the GATE-1 cost approval — capture the actual approved cap). Write m3-W2-budget-redo.md. The memo MUST state: the new PROJECTED, the BUDGET_CAP_CLUSTER_H, the evaluated `PROJECTED x 1.3 <= BUDGET_CAP` result, the disposition (GREEN/YELLOW-narrow-radius/YELLOW-finer-split/RED), and — explicitly — that the full 322-cell production fire is OUT of scope here and stays in Wave 4 (m3-04). If disposition is GREEN, the memo states m3-04 is unblocked; if RED/YELLOW, it states the next lever + that a re-probe is needed before m3-04.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_redo_ld_cost_model.py -v --tb=short &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md &amp;&amp; grep -c "PROJECTED" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "projected \* 1.3 <= budget_cap\|projected\*1.3<=budget_cap\|PROJECTED.*1.3.*BUDGET_CAP" src/python/redo_ld_cost_model.py` returns >= 1 (the exact predicate encoded).
    - `grep -c "def evaluate_gate\|def project_cell_hours\|def eur_factor" src/python/redo_ld_cost_model.py` returns >= 3.
    - `grep -c "GREEN\|YELLOW-narrow-radius\|YELLOW-finer-split\|RED" src/python/redo_ld_cost_model.py` returns >= 4 (all dispositions present).
    - `grep -c "parent_region_id\|subregion" src/python/redo_ld_cost_model.py` returns >= 1 (xlarge parent = sum over sub-regions).
    - `pytest tests/m3/test_redo_ld_cost_model.py -v` reports >= 5 passed, 0 failed.
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` exits 0.
    - `grep -c "PROJECTED" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1.
    - `grep -c "BUDGET_CAP" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1.
    - `grep -cE "GREEN|YELLOW|RED" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1 (the disposition).
    - `grep -ci "out of scope\|Wave 4\|m3-04" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1 (322-cell fire stays in m3-04).
    - `grep -rn "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/redo_ld_cost_model.py` returns 0 matches (REQ-PATH-PARAMETERIZATION).
  </acceptance_criteria>
  <done>
    redo_ld_cost_model.py extrapolates the measured blocks_per_min to all 322 post-split cells (xlarge parents summed over sub-regions, EUR via measured-or-3.01x factor), evaluates the exact `PROJECTED x 1.3 <= BUDGET_CAP` gate, and writes m3-W2-budget-redo.md with PROJECTED + cap + disposition (GREEN/YELLOW/RED) + the explicit note that the full 322-cell fire stays in m3-04. 5 unit tests pass.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| AoU perimeter -> NCSU | The probe produces summary LD .npz/.bm in the AoU bucket; nothing crosses to NCSU in this plan except the cost metrics (blocks_per_min etc.) hand-recorded into the TSV. No individual-level genotypes leave the perimeter. |
| Cluster spend -> credit balance | The probe spends real AoU credits; the go/no-go gate exists precisely to cap the much larger production spend. |
| VPC-SC perimeter | The sized cluster + quota request live entirely inside the Verily perimeter; the request path itself is perimeter-gated (Q-RS1 A1). |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M3RS-EGRESS-02 | Information disclosure | controlled-tier AoU genotypes during the probe | mitigate | The probe emits only summary LD matrices + AF metadata to the in-perimeter bucket (REQ-AOU-LD-EGRESS); each cell over n>=60k AFR / n>=130k EUR trivially clears the n>=20 suppression floor; NOTHING individual-level crosses to NCSU (only the hand-recorded cost metrics). No egress request is filed in this plan — the 44 per-bundle reviews stay in m3-04. |
| T-M3RS-VPCSC-01 | Cross-perimeter leakage | the sized cluster + bucket | mitigate | All compute + writes stay in-perimeter (gs://rw-migration-aou-rw-476cdac2); no cross-perimeter transfer (regenerate-in-perimeter per SKILL.md RW2.0-mirror facts); the quota request names the in-perimeter project + us-central1. |
| T-M3RS-COST-02 | DoS / cost-overrun / runaway cluster billing | the production 322-cell fire | mitigate | The ENTIRE purpose of the probe + the PROJECTED x 1.3 <= BUDGET_CAP gate: the full fire is fired iff the measured-and-extrapolated projection clears the cap with 30% headroom; the cluster is STOPPED after the probe ($0); cluster_size capped at min(granted, 400). |
| T-M3RS-STITCH-03 | Tampering / Integrity | mis-ordered stitch corrupting variant<->LD alignment to SuSiE-RSS | mitigate (in m3-02b) | The probe verifies a sub-region cell at the data layer; the stitch ordering assertion (monotonic snp position, sort by subregion_index column) is enforced + tested in m3-02b (T-M3RS-STITCH-01). This plan validates the sub-region produces real data (D-M3-10 count), feeding the m3-02b stitch. |
| T-M3RS-PROBE-01 | Integrity / false-completion | _SUCCESS over empty .npz/.bm masking a failed probe cell | mitigate | D-M3-10 contents-validation: each probe cell is gsutil-du + Hail/np count verified before being recorded in the TSV; _SUCCESS alone is NEVER accepted (baked by the m3-W1 empty-MT catastrophe). |
</threat_model>

<verification>
**Plan-level checks:**

1. m3-W2-quota-ticket.md exists naming N2_CPUS + us-central1 + >=400 (Task 1 acceptance).
2. m3-W2-cost-probe.tsv exists with the 12-column header + >= 2 measured cells incl. region_00006 + m2_region_00040__sub00 (Task 2 acceptance).
3. `pytest tests/m3/test_redo_ld_cost_model.py -v` >= 5 passed (Task 3).
4. m3-W2-budget-redo.md states PROJECTED + BUDGET_CAP + the `PROJECTED x 1.3 <= BUDGET_CAP` evaluation + disposition + the explicit "322-cell fire stays in m3-04" note.
5. REQ-PATH-PARAMETERIZATION: `grep -rn "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/redo_ld_cost_model.py` returns 0.
6. The exact gate predicate `projected * 1.3 <= budget_cap` is encoded in redo_ld_cost_model.py (Task 3 acceptance).
</verification>

<success_criteria>
- The N2_CPUS >= 400 us-central1 quota request is filed (correct family + region) and recorded — the longest-lead item, surfaced first.
- The 2-3 cell cost probe fires on the sized n2-highmem-16 cluster; the Q-RS2 executor config is validated (spill recorded); each cell is data-layer-verified per D-M3-10.
- m3-W2-cost-probe.tsv carries blocks_per_min + the full metric set tagged by (ancestry, region_class).
- redo_ld_cost_model.py re-derives the 322-cell PROJECTED budget (xlarge parents summed over sub-regions; EUR via measured-or-3.01x) and evaluates the exact `PROJECTED x 1.3 <= BUDGET_CAP` gate.
- m3-W2-budget-redo.md records PROJECTED + cap + disposition (GREEN/YELLOW/RED) + the explicit out-of-scope note for the 322-cell fire.
- The full 322-cell production fire stays in Wave 4 (m3-04) — this plan ends at the go/no-go decision.
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-02c-W2-rescope-quota-probe-and-gonogo-SUMMARY.md` recording:
- The quota channel used + the GRANTED N2 ceiling + the resulting cluster_size
- The probe cells' measured blocks_per_min (AFR-medium, AFR-subregion, EUR if fired) + spill behavior + the cores value the projection assumes
- The new PROJECTED cluster-h vs the stale ~1,117 + the credit-$ at the confirmed n2-highmem-16 rate
- The BUDGET_CAP_CLUSTER_H value + the disposition (GREEN/YELLOW/RED) + the next step (m3-04 unblocked, or which lever + re-probe)
- Any region (e.g. HLA/6p21 region_00145) flagged for finer split if its sub-region overshot 75k var on the probe
</output>
