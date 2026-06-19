---
phase: m3-aou-afr-ld-panel-build
plan: 02c
type: execute
wave: 1
depends_on: ["02b"]
files_modified:
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-grant.md
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv
  - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md
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
    - "QUOTA GATE 1 (ticket FILED): Carter files an AoU/Verily quota-increase ticket naming N2_CPUS >= 400, region us-central1 (24x n2-highmem-16 workers + 1 master = 400 vCPU; ask 400-512); a record lands at m3-W2-quota-ticket.md. Completion of THIS gate = the request is submitted (channel, metric, region, amount, date, request ID) — it does NOT assert a grant."
    - "QUOTA GATE 2 (grant GRANTED): a SEPARATE blocking gate records the NUMERIC granted N2_CPUS ceiling at m3-W2-quota-grant.md; cluster_size = min(granted, 400). The probe (Task 3) depends_on the GRANTED ceiling, not the filing. If only ~256 vCPU (16 workers) is granted, the probe still runs and the projection scales wall-clock — the split (m3-02b) is what makes xlarge tractable, not the cluster size."
    - "Before the probe, the AoU env panel is confirmed to show n2-highmem workers (NOT n1-highmem) + region us-central1; the Q-RS2 executor config (cores=2 / 24-28g / 8-12g overhead) from m3-02b is applied and validated (no spill at cores=2, else drop to cores=1) on the probe."
    - "The 3 prep landmines are re-applied on the fresh cluster: symlink ~/coloc_analysis -> synced repo; pin WORKSPACE_BUCKET=gs://rw-migration-aou-rw-476cdac2 (HARD os.environ override, not setdefault); os.chdir(~/coloc_analysis) before the per-region loop (per SKILL.md)."
    - "PREFLIGHT COUNT PASS: a cheap in-perimeter count pass runs over EVERY post-split ancestry compute cell BEFORE the cost projection, recording actual n_var, the actual routed path (A.1/A.2/A.3 via the real _route_region_path on the compute WINDOW span), estimated block_count, and output-size estimate to m3-W2-preflight-counts.tsv. Any cell exceeding the <=75k-var / size threshold is auto-split (lower --max-subregion-span-mb) or FLAGGED. The cost model consumes these REAL per-cell numbers, not span-derived guesses."
    - "The cost probe fires >=3 cells on the sized cluster: (1) AFR WHOLE medium region m2_region_00006 (122,678 var, 17.7 Mb); (2) AFR xlarge SUB-REGION m2_region_00040__sub00 (compute window ~core+buffer); (3) MANDATORY EUR SUB-REGION (220k samples — the spill-risk + cost driver; the 3.01x multiplier is MEASURED not assumed). PLUS an HLA preflight: probe one region_00145 (HLA/6p21) sub-region OR a mandatory HLA count/size preflight cell."
    - "For each probe cell the metric set is captured to m3-W2-cost-probe.tsv: blocks_per_min, block_count, peak_executor_mem, any_spill, wall_clock_min, cluster_vcpu, cluster_hours tagged by (ancestry, region_class). _SUCCESS is NOT evidence of data — each cell is verified at the data layer (gsutil du on the .npz/.bm + Hail count) per D-M3-10."
    - "EXECUTABLE RUNAWAY-COST CONTROLS: the probe task encodes a max wall-time per cell, a max probe credit spend, spill/OOM kill criteria, a GUARANTEED cluster shutdown after the probe, and a shutdown-VERIFICATION artifact (m3-W2-cluster-shutdown.md with the gcloud/wb stop confirmation + a $0 billing check) — not just a prose 'cluster is stopped'."
    - "redo_ld_cost_model.py extrapolates the measured blocks_per_min to ALL post-split COMPUTE cells using the REAL preflight n_var/block_count (not span guesses), applies the MEASURED EUR factor (from the mandatory EUR cell) or 3.01x +/-20% as fallback, and keeps SEPARATE totals: (a) 322 logical PARENT panels, (b) the expanded ancestry-specific COMPUTE cells (necessarily > 322 post-split), (c) aggregate parent costs (xlarge parent = Sigma over its sub-region compute cells). Cluster-hours include the MASTER and end-to-end wall (filtering, count_rows, variant collection, checkpoint, writes, sidecars, retries, startup, idle), not just Stage-4 workers. A contingency factor from observed probe variance is applied. An egress bundle-size projection is produced before production."
    - "The go/no-go gate is encoded with the EXACT predicate: fire the full 322 iff PROJECTED x 1.3 <= BUDGET_CAP_CLUSTER_H (from GATE-1). Disposition is one of GREEN (fire full in m3-04), YELLOW-narrow-radius (drop the buffer_bp toward Pan-UKBB 10 Mb via the m3-02b --subregion-buffer-mb knob, re-probe), YELLOW-finer-split (lower --max-subregion-span-mb for the cost-driver class, re-probe), or RED (re-negotiate budget / phase the fire). Recorded in m3-W2-budget-redo.md with the computed PROJECTED (all three totals), BUDGET_CAP_CLUSTER_H, and the 1.3x headroom check."
    - "The full 322-cell production fire is EXPLICITLY OUT of scope here — it stays in Wave 4 (m3-04). This plan ends at a GREEN/RED go/no-go decision + a defensible re-derived budget."
  artifacts:
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md"
      provides: "Record of the N2_CPUS>=400 us-central1 quota REQUEST (channel, date filed, request ID) — the FILED gate"
      contains: "N2_CPUS"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-grant.md"
      provides: "The NUMERIC granted N2_CPUS ceiling + resulting cluster_size = min(granted, 400) — the GRANTED gate the probe depends on"
      contains: "granted"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv"
      provides: "Per-post-split-cell actual n_var + routed path (real _route_region_path on the window span) + est block_count + output-size estimate; auto-split/flag for cells over threshold"
      contains: "n_var"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv"
      provides: "Per-probe-cell blocks_per_min + block_count + peak_mem + spill + cluster_hours tagged by (ancestry, region_class); incl. the mandatory EUR cell + HLA preflight"
      contains: "blocks_per_min"
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md"
      provides: "Shutdown-verification artifact: the stop command output + a $0/idle billing confirmation after the probe"
      contains: "stop"
    - path: "src/python/redo_ld_cost_model.py"
      provides: "Extrapolate measured blocks_per_min over the REAL preflight cells; 3 separate totals (parent panels / compute cells / aggregate); master+end-to-end inclusive cluster-hours; contingency factor; egress bundle estimate; PROJECTED x 1.3 <= BUDGET_CAP gate"
      min_lines: 90
    - path: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md"
      provides: "New PROJECTED (3 totals) + credit-$ + the GREEN/YELLOW/RED disposition with the exact 1.3x predicate evaluated"
      contains: "PROJECTED"
    - path: "tests/m3/test_redo_ld_cost_model.py"
      provides: "Unit tests for the extrapolation arithmetic (real-count inputs), the 3-totals separation, master-inclusive accounting, and the 1.3x gate predicate (synthetic preflight + probe TSV; no cluster)"
  key_links:
    - from: "src/python/redo_ld_cost_model.py"
      to: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv"
      via: "reads REAL per-cell n_var + block_count + routed path"
      pattern: "n_var"
    - from: "src/python/redo_ld_cost_model.py"
      to: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv"
      via: "reads measured blocks_per_min per (ancestry, region_class) incl. measured EUR factor"
      pattern: "blocks_per_min"
    - from: "src/python/redo_ld_cost_model.py"
      to: ".planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md"
      via: "writes PROJECTED (3 totals) + the PROJECTED x 1.3 <= BUDGET_CAP disposition"
      pattern: "BUDGET_CAP"
---

<objective>
Resolve the two live-only items the m3-02b code re-scope cannot: (1) the AoU N2 vCPU quota grant (the longest-lead human action — file FIRST), and (2) the real-cohort cost probe that re-derives the known-stale ~1,117 cluster-h budget. The probe fires a defensible >=3-cell set — one WHOLE medium region (region_00006) + one xlarge SUB-REGION (m2_region_00040__sub00) + one MANDATORY EUR sub-region (the spill-risk + cost driver) + an HLA preflight — on the sized n2-highmem-16 cluster, AFTER a cheap in-perimeter PREFLIGHT COUNT PASS over every post-split compute cell. It measures blocks_per_min, extrapolates over the REAL preflight counts (not span guesses), keeps three separate totals (322 parent panels / expanded compute cells / aggregate), accounts for the MASTER + end-to-end wall, and evaluates the go/no-go gate `PROJECTED x 1.3 <= BUDGET_CAP_CLUSTER_H`.

REVISION (m3-REVIEWS.md, Codex HIGH #6/7 + MEDIUMs): split the quota gate into FILED vs GRANTED (the probe depends on a numeric grant, not the filing); make the EUR cell MANDATORY (it is the spill-risk + cost driver; the 3.01x multiplier must be measured); add an HLA preflight; add an in-perimeter preflight count pass feeding REAL n_var/block_count into the cost model; make cluster-hours master-inclusive + end-to-end with three separate totals + a contingency factor + an egress bundle-size projection; and add EXECUTABLE runaway-cost controls (max wall/credit, spill/OOM kill, guaranteed shutdown + a shutdown-verification artifact).

Purpose: The dev-10 fire was sized off a 2,000-sample synthetic repro (36-110x too cheap). Before any production spend, the budget must be rebuilt bottom-up from measured real-cohort throughput AND real per-cell counts, and the full fire gated on it. This plan ends at a GREEN/RED decision; the full 322-cell fire stays in Wave 4 (m3-04).

Output: the FILED + GRANTED quota records, the preflight-counts TSV, the cost-probe TSV, the shutdown-verification artifact, the cost-model redo script + tests, and the budget-redo memo with the disposition.

LOCKED (do NOT relitigate): A.3 fix correct; ordering A kept; cohorts intact; the split (m3-02b) is the structural fix; probe-before-fire. Cluster size is a tuning knob, not a correctness gate.
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
@.planning/phases/m3-aou-afr-ld-panel-build/m3-REVIEWS.md
@.planning/phases/m3-aou-afr-ld-panel-build/m3-CONTEXT.md
@.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md
@.claude/skills/aou-ld-pipeline/SKILL.md

<interfaces>
<!-- Inputs from m3-02b (Wave 0) + the live coordinates the probe needs. -->

From m3-02b (must exist before this plan runs):
- config/ld_regions.tsv now contains m2_region_00040__sub00 .. __subNN COMPUTE rows (overlapping-window split:
  start_grch38/end_grch38 = the WINDOW = core +/- buffer_bp; buffer_bp + core_start/core_end columns present)
- config/ld_regions_dev.tsv expanded (capped) to include m2_region_00040 sub-rows
- AOU-2 notebook carries the Q-RS2 executor config (cores=2 / 24g / 10g / 24g) before pyspark import
- The .npz payload carries allele_freq; the stitch emits a BANDED sparse obj$R + obj$variants for the real loader
- _route_region_path(region_class, window_span_mb): PATH_A2_MAX_MB=10 -> a >10 Mb compute window is A.3

Live coordinates (SKILL.md):
- Workspace aou-rw-476cdac2 . project wb-perky-corn-6639 . bucket gs://rw-migration-aou-rw-476cdac2
- Run branch m3-W2-aou-deltas (NOT main - clone-from-main wedges deterministically)
- Cohorts (intact): AFR_pca 73,122 x 20,767,864 ; EUR_pca 220,098 x 11,375,140

Q-RS1 quota (verbatim):
- Blocking dimension = regional N2_CPUS in us-central1 (separate from generic CPUS / N1)
- Request must name N2 family + us-central1 explicitly; channel likely an AoU/Verily ticket (VPC-SC-gated) - A1
- Grantable ceiling unknown (A2); cluster_size = min(granted N2 quota, 400 vCPU)

Q-RS5 probe + gate (verbatim, REVISED to mandatory-EUR + HLA + preflight):
- Cells: WHOLE region_00006 (122,678 var) + xlarge SUB-REGION m2_region_00040__sub00 + MANDATORY EUR sub-region + HLA preflight
- Metric per cell: blocks_per_min = Stage-4 blocks / Stage-4 wall-minutes ; block_count ; peak exec mem + spill ;
  cluster-hours = MASTER-INCLUSIVE end-to-end wall_h x (n_workers + 1 master) ; tag (ancestry, region_class)
- Extrapolation: per-cell cluster-h from REAL preflight block_count / measured blocks_per_min ; AFR->EUR x MEASURED
  factor (mandatory EUR cell) ; xlarge parent = Sigma over its sub-region compute cells
- n2-highmem-16 price ~$0.95-1.10/hr/worker (A8 - confirm); 24 workers + master ~= $24-27/hr
- GATE: fire iff PROJECTED x 1.3 <= BUDGET_CAP_CLUSTER_H ; dispositions GREEN / YELLOW-narrow-radius / YELLOW-finer-split / RED

GATE-1 budget (STATE.md): cost/credit CLEARED 2026-06-12 by Carter; BUDGET_CAP_CLUSTER_H is Carter's approved credit cap
- capture the numeric value into m3-W2-budget-redo.md at gate time (re-confirm the number with Carter at the gate).

D-M3-10: every MT/.npz/.bm write is contents-validated, not _SUCCESS-only (gsutil du + Hail count). The probe cells inherit this.
</interfaces>
</context>

<tasks>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 1: QUOTA GATE 1 (FILED) — Carter files the N2_CPUS >= 400 us-central1 quota-increase ticket (LONGEST-LEAD — surfaced first)</name>
  <files>.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS1" (lines 16-40) — quota mechanics + the N1-vs-N2 trap + request path + A1/A2 flags
    - .claude/skills/aou-ld-pipeline/SKILL.md "Coordinates" + "RW2.0 is a MIRROR ... VPC-SC perimeter" (the request path is perimeter-gated)
    - memory reference_wb_cli_hpc_setup (control-plane vs data-plane boundary)
  </read_first>
  <action>See the human_gate block. Carter human action; no agent compute. The agent verifies acceptance_criteria after Carter records the FILED ticket. This gate is FILING ONLY — the numeric grant is Task 2.</action>
  <human_gate>
    <gate>AoU N2 vCPU quota REQUEST filed for the sized re-fire cluster</gate>
    <description>
      File the quota-increase request that unblocks the sized cluster. This is the LONGEST-LEAD item (days to ~2 weeks per Q-RS1 A1) and it gates the cost probe — file it before anything else.

      The request MUST name, EXPLICITLY:
      - Quota metric: N2_CPUS (NOT generic CPUS / N1 — raising CPUS will NOT unblock an all-N2 cluster; the Q-RS1 N1-vs-N2 trap).
      - Region: us-central1 (reconfirm in the AoU env panel before filing — A1).
      - Amount: >= 400 vCPU (24x n2-highmem-16 workers + 1 master = 25 x 16 = 400); ask 400-512 for headroom.

      Channel (Q-RS1 A1): the AoU RW2.0 / Verily billing project is org-managed and the Console quota page is likely VPC-SC-restricted — the realistic path is an AoU support / Verily request ticket. If the Console quota page IS reachable from inside the perimeter (IAM and Admin -> Quotas -> filter "N2 CPUs" / region us-central1 -> Edit Quotas), use it; otherwise file via AoU support.

      Record the REQUEST at m3-W2-quota-ticket.md with: channel used, metric=N2_CPUS, region=us-central1, amount, date filed, ticket/request ID. THIS GATE COMPLETES WHEN THE REQUEST IS SUBMITTED — it does NOT assert a grant (the numeric grant is recorded separately in Task 2).
    </description>
    <unblocks>Task 2 (the GRANTED gate) -> Task 3 (the cost probe)</unblocks>
    <how-to-resolve>
      1. Reconfirm workspace region == us-central1 in the AoU env panel.
      2. File the N2_CPUS >= 400 (ask 400-512) us-central1 request via AoU support ticket (or Console if reachable).
      3. Write m3-W2-quota-ticket.md with channel + metric=N2_CPUS + region=us-central1 + amount + date + request ID.
      4. Type "filed" to record the gate. Do NOT wait for the grant here — that is Task 2.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md &amp;&amp; grep -c "N2_CPUS" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md` exits 0.
    - `grep -c "N2_CPUS" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md` returns >= 1.
    - `grep -c "us-central1" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md` returns >= 1.
    - `grep -cE "40[0-9]|4[0-9][0-9]|5[0-9][0-9]" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md` returns >= 1 (the >=400 amount).
    - `grep -ci "filed\|request id\|ticket" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md` returns >= 1.
    - This gate does NOT require a grant value — it asserts the REQUEST was submitted. The grant is Task 2.
  </acceptance_criteria>
  <done>
    The N2_CPUS >= 400 us-central1 quota request is FILED (correct family + region named) and recorded with its channel, amount, date, and request ID. No grant is asserted here — Task 2 records the numeric grant.
  </done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 2: QUOTA GATE 2 (GRANTED) — record the NUMERIC granted N2_CPUS ceiling; the probe depends on the grant, not the filing</name>
  <files>.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-grant.md</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-ticket.md (Task 1 output — the filed request this gate awaits a grant for)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS1" A2 (grantable ceiling unknown; cluster_size = min(granted, 400))
  </read_first>
  <action>See the human_gate block. Carter human action; no agent compute. The agent verifies acceptance_criteria after Carter records the NUMERIC grant. This is a SEPARATE blocking gate from the filing (Codex MEDIUM: filing != grant). Task 3 depends_on THIS task, not Task 1.</action>
  <human_gate>
    <gate>AoU N2 vCPU quota GRANTED — the numeric ceiling is recorded</gate>
    <description>
      The filing (Task 1) only proves a request was submitted; it can sit in a queue for days to ~2 weeks (Q-RS1 A1). This gate records the ACTUAL grant so the probe sizes the cluster against a real number, not an assumed one.

      When the quota request returns:
      - Record the NUMERIC granted N2_CPUS ceiling (e.g. "granted: 400 vCPU" or "granted: 256 vCPU") at m3-W2-quota-grant.md, with the date granted + the channel that confirmed it.
      - Compute cluster_size = min(granted, 400) and write it explicitly (e.g. granted 400 -> cluster_size 400 -> 24 workers + 1 master; granted 256 -> cluster_size 256 -> 15 workers + 1 master).
      - If the grant is BELOW the 400 ask, note it: the probe STILL runs and the projection scales wall-clock — the split (m3-02b) is what makes xlarge tractable, the cluster size is only a wall-clock tuning knob (NOT a correctness gate).

      Do NOT proceed to Task 3 (the probe) until a NUMERIC grant is recorded here. A pending/queued ticket is NOT a grant.
    </description>
    <unblocks>Task 3 (the cost probe — needs the sized cluster from the GRANTED ceiling)</unblocks>
    <how-to-resolve>
      1. Wait for the quota request (Task 1) to be approved.
      2. Record the numeric granted N2_CPUS ceiling + date + channel at m3-W2-quota-grant.md.
      3. Write cluster_size = min(granted, 400) and the resulting worker/master count.
      4. Type "granted" to record the gate. If still pending, this gate stays blocked.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-grant.md &amp;&amp; grep -ci "granted" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-grant.md &amp;&amp; grep -cE "[0-9]{2,4}" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-grant.md</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-grant.md` exits 0.
    - `grep -ci "granted" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-grant.md` returns >= 1.
    - `grep -cE "[0-9]{2,4}" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-grant.md` returns >= 1 (a NUMERIC ceiling is recorded — not just "approved").
    - `grep -ci "cluster_size\|cluster size" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-quota-grant.md` returns >= 1 (cluster_size = min(granted, 400) computed).
  </acceptance_criteria>
  <done>
    A NUMERIC granted N2_CPUS ceiling is recorded at m3-W2-quota-grant.md with cluster_size = min(granted, 400). Task 3 (the probe) is unblocked by THIS gate, not by the Task 1 filing. A pending ticket does NOT satisfy this gate.
  </done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 3: PREFLIGHT count pass over every post-split cell + fire the >=3-cell cost probe (mandatory EUR + HLA) with EXECUTABLE runaway-cost controls + a GUARANTEED shutdown-verify artifact</name>
  <files>.planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv, .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv, .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS5" (probe design + exact metric set + extrapolation) + "Q-RS2" (executor config to validate)
    - .claude/skills/aou-ld-pipeline/SKILL.md "Fresh-clone re-run checklist" + "LD compute (AOU-2) — specifics" + "The invariants" (the 3 prep landmines + data-layer verify + the websocket-drop orphan-kernel kill)
    - .planning/notebooks/AOU-2_per_region_ld.ipynb (the Q-RS2 executor cell + the per-region loop; from m3-02b)
    - config/ld_regions.tsv (m3-02b post-split: m2_region_00040__sub* + region_00145 HLA rows) + config/ld_regions_dev.tsv (capped expansion)
    - src/python/aou_ld_panel.py _route_region_path (the real router the preflight tags the window span against) + the count/n_var pass in compute_region_ld
  </read_first>
  <action>See the human_gate block. Carter fires the preflight + probe inside the AoU perimeter; the agent prepares the probe-cell manifest hint + the preflight column spec + verifies the recorded TSVs + the shutdown artifact afterward. The agent's only pre-fire action: confirm config/ld_regions_dev.tsv (or a probe manifest) contains the probe cells m2_region_00006 (AFR, whole), m2_region_00040__sub00 (AFR, sub), m2_region_00040__sub00 (EUR, sub — MANDATORY), and an HLA region_00145 sub-region (for the HLA preflight/probe). The agent does NOT cross the perimeter.</action>
  <human_gate>
    <gate>Preflight count pass + real-cohort cost probe (mandatory EUR + HLA) with executable cost controls + verified shutdown</gate>
    <description>
      Two sub-steps in the perimeter: a CHEAP preflight count pass over every post-split cell, then a >=3-cell throughput probe with hard cost controls and a verified shutdown.

      PRE-FLIGHT (re-apply on the fresh sized cluster):
      - Start the cluster on the GRANTED N2 quota (Task 2): workers n2-highmem-16 (128 GB — stops the spill), master n2-highmem-16, vCPU = cluster_size = min(granted, 400). Confirm in the env panel: workers are n2-highmem (NOT n1-highmem) and region == us-central1.
      - git checkout m3-W2-aou-deltas (NOT main) -> git pull -> git checkout -f (the Workbench filter re-dirties notebooks).
      - The 3 prep landmines: symlink ~/coloc_analysis -> synced repo; pin WORKSPACE_BUCKET=gs://rw-migration-aou-rw-476cdac2 via a HARD os.environ override (not setdefault); os.chdir(~/coloc_analysis) before the per-region loop.
      - The AOU-2 Q-RS2 executor cell (cores=2 / 24g / 10g overhead / 24g driver) runs BEFORE the pyspark/hail import. Confirm it bound (print PYSPARK_SUBMIT_ARGS).

      STEP A — PREFLIGHT COUNT PASS (cheap, in-perimeter, BEFORE the cost projection):
      Run a count-only pass (filter the cohort MT to each post-split compute WINDOW + Hail count_rows; NO correlation compute) over EVERY post-split ancestry compute cell. For each cell record to m3-W2-preflight-counts.tsv with columns:
      `region_id  ancestry  region_class  window_span_mb  n_var  routed_path  est_block_count  est_output_gib  over_threshold`
      where routed_path = the REAL _route_region_path(region_class, window_span_mb) (A.1/A.2/A.3 on the WINDOW span, not the core span), est_block_count = ceil(n_var/4096)^2 / 2 (banded -> the in-band block count), est_output_gib = banded nnz * 4 bytes / 1e9, and over_threshold = (n_var > 75000). MANDATORY: include the HLA region_00145 sub-region(s) — HLA/6p21 density may exceed the 10 Mb -> ~69k-var assumption (A4); if any cell has over_threshold == True, AUTO-SPLIT it (re-run m3-02b build_ld_region_manifest with a lower --max-subregion-span-mb, e.g. 7, for that chromosome) or FLAG it for finer split before the cost model consumes it. The cost model (Task 4) reads these REAL n_var/block_count, NOT span-derived guesses.

      STEP B — FIRE >=3 PROBE CELLS (with EXECUTABLE cost controls):
      Encode these hard controls in the probe loop BEFORE firing (not prose):
      - MAX_WALL_MIN_PER_CELL (e.g. 90 min): if a cell exceeds it, KILL the job (cancel the Spark stage / interrupt the cell) and record any_spill/timeout.
      - MAX_PROBE_CREDIT_USD (e.g. $60): track elapsed cluster-hours x rate; if the running probe spend exceeds the cap, STOP firing further cells and shut down.
      - SPILL/OOM KILL: if executor spill bytes > 0 at cores=2 OR an OOM is observed, record it, drop to cores=1 for the production projection, and (if OOM) kill + re-fire that cell once at cores=1.
      Fire the cells:
      1. WHOLE medium region: m2_region_00006 (AFR, 122,678 var, 17.7 Mb) — direct before/after comparability with dev-10.
      2. xlarge SUB-REGION: m2_region_00040__sub00 (AFR, compute window ~core+buffer) — proves the split makes the worst region tractable.
      3. MANDATORY EUR SUB-REGION: m2_region_00040__sub00 (EUR, 220,098 samples) — the spill-risk + cost driver; the EUR/AFR factor is MEASURED here, NOT assumed 3.01x. Do NOT skip this cell — it is the load-bearing cost input.
      4. HLA: probe one region_00145 (HLA/6p21) sub-region OR (if STEP A's HLA preflight already gave n_var + est_block_count) accept the preflight count as the HLA input and note it.

      VALIDATE THE EXECUTOR CONFIG ON THE PROBE: watch for executor spill at cores=2 (especially on EUR). If EUR spills, record it and set the production config to cores=1 (record which cores value the projection assumes).

      DATA-LAYER VERIFY (D-M3-10 — _SUCCESS is NOT evidence): for each fired cell, gsutil du -s the produced .npz/.bm under gs://rw-migration-aou-rw-476cdac2/ld/{AFR_aou,EUR_aou}/ (must be >> 0) AND a Hail/np read-back count, before recording the cell as complete.

      RECORD m3-W2-cost-probe.tsv (one row per fired cell) with the EXACT columns:
      `region_id  ancestry  region_class  n_var  block_count  stage4_wall_min  end_to_end_wall_min  blocks_per_min  peak_executor_mem_gib  any_spill  cluster_vcpu  n_workers  cluster_hours`
      where blocks_per_min = block_count / stage4_wall_min, end_to_end_wall_min = the FULL cell wall incl. filtering/count_rows/variant-collection/checkpoint/writes/sidecars/retries (NOT just Stage-4), and cluster_hours = (end_to_end_wall_min / 60) * (n_workers + 1)  [MASTER-INCLUSIVE]. Tag each row by (ancestry, region_class). Capture peak_executor_mem + any_spill from the Spark UI.

      STEP C — GUARANTEED SHUTDOWN + VERIFICATION ARTIFACT:
      After the probe (or on any cost-control trip), STOP the cluster (gcloud dataproc clusters stop / wb cluster stop / the AoU env Delete-Cluster control) and WRITE m3-W2-cluster-shutdown.md with: the stop command + its output, the timestamp, the cluster state == STOPPED/DELETED confirmation, and a $0/idle billing check (env panel shows no running cluster). A prose "I stopped it" does NOT satisfy this — the artifact must carry the stop confirmation + the idle-billing check.
    </description>
    <unblocks>Task 4 (cost-model redo + go/no-go gate)</unblocks>
    <how-to-resolve>
      1. Pre-flight per SKILL.md (sized cluster on the GRANTED quota, 3 landmines, Q-RS2 cell bound).
      2. STEP A: run the cheap count pass over every post-split cell -> m3-W2-preflight-counts.tsv (incl. HLA region_00145); auto-split/flag any over_threshold cell.
      3. STEP B: encode the hard cost controls, fire region_00006 (AFR) + m2_region_00040__sub00 (AFR) + m2_region_00040__sub00 (EUR, MANDATORY) + HLA; data-layer-verify each cell.
      4. Write the master-inclusive m3-W2-cost-probe.tsv (header + >= 3 rows).
      5. STEP C: STOP the cluster, write m3-W2-cluster-shutdown.md with the stop output + $0 idle check.
      6. Type "probe-recorded" to resume; Task 4 reads the two TSVs.
    </how-to-resolve>
  </human_gate>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv &amp;&amp; head -1 .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv | grep -q "routed_path" &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv &amp;&amp; head -1 .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv | grep -q "blocks_per_min" &amp;&amp; test $(tail -n +2 .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv | grep -c .) -ge 3 &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md &amp;&amp; echo OK</automated>
  </verify>
  <acceptance_criteria>
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv` exits 0; `head -1` contains all of: n_var, routed_path, est_block_count, over_threshold (grep -c each >= 1).
    - `grep -c "region_00145\|HLA\|6p21" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv` returns >= 1 (HLA included in the preflight).
    - `tail -n +2 .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv | grep -c .` returns >= 4 (every post-split probe-relevant cell counted).
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` exits 0; `head -1` contains: region_id, ancestry, region_class, block_count, blocks_per_min, end_to_end_wall_min, cluster_hours (grep -c each >= 1).
    - `grep -c "m2_region_00006" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` returns >= 1 (whole-region cell).
    - `grep -c "m2_region_00040__sub00" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` returns >= 1 (sub-region cell).
    - `grep -c "EUR" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` returns >= 1 (the MANDATORY EUR cell was fired — not skipped).
    - `tail -n +2 .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv | grep -c .` returns >= 3 (>= 3 measured cells incl. EUR).
    - `grep -ci "spill" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv` returns >= 1 (any_spill column present).
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md` exits 0; `grep -ci "stop\|stopped\|deleted" m3-W2-cluster-shutdown.md` (phase dir) returns >= 1 AND `grep -ci "\\$0\|idle\|no running\|billing" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cluster-shutdown.md` returns >= 1 (shutdown + idle-billing verification, not just prose).
  </acceptance_criteria>
  <done>
    A cheap preflight count pass records REAL n_var + real routed path + est block/output size for EVERY post-split cell (incl. HLA region_00145) to m3-W2-preflight-counts.tsv, auto-splitting/flagging any >75k-var cell; the >=3-cell probe fires WITH the mandatory EUR cell on the sized cluster under executable cost controls (max wall/credit, spill/OOM kill); each cell is data-layer-verified (D-M3-10); m3-W2-cost-probe.tsv carries the master-inclusive end-to-end metric set; and the cluster is shut down with a verified shutdown artifact (stop output + $0 idle check).
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 4: redo_ld_cost_model.py — real-count extrapolation, 3 separate totals, master-inclusive end-to-end cluster-hours, contingency + egress projection, and the PROJECTED x 1.3 <= BUDGET_CAP go/no-go gate + budget-redo memo</name>
  <files>src/python/redo_ld_cost_model.py, tests/m3/test_redo_ld_cost_model.py, .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md</files>
  <read_first>
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-RESEARCH-W2-RESCOPE.md "Q-RS5 Extrapolation" + "Go / no-go threshold structure" — the exact arithmetic + the PROJECTED x 1.3 <= BUDGET_CAP predicate + the 4 dispositions
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-preflight-counts.tsv (Task 3 STEP A — the REAL per-cell n_var/block_count/routed_path the model consumes)
    - .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-cost-probe.tsv (Task 3 STEP B — the measured blocks_per_min + the measured EUR factor + master-inclusive cluster_hours)
    - src/python/build_ld_region_manifest.py (the post-split projection TSV with split_status in {whole,parent,subregion} + parent_region_id + n_subregions from m3-02b; the STALE est_cluster_hours table this REPLACES)
    - config/ld_regions.tsv + the m3-region-class-projection.tsv (the logical 322 parents + the expanded compute cells)
  </read_first>
  <behavior>
    - test_three_separate_totals: the model returns THREE distinct totals — (a) n_logical_parent_panels == 322, (b) n_compute_cells > 322 (post-split: each xlarge parent expands into N sub-region compute cells), (c) aggregate parent cost where an xlarge parent cost == sum over its split_status=="subregion" rows (grouped by parent_region_id). Assert total_compute_cells > 322 and the per-parent aggregate equals the sub-row sum.
    - test_real_count_extrapolation_not_span: per-cell cluster-h is computed from the PREFLIGHT n_var/block_count (read from m3-W2-preflight-counts.tsv), NOT from span; feed a preflight row whose n_var implies a different block_count than its span would, and assert the model uses the preflight block_count.
    - test_master_inclusive_end_to_end_hours: cluster_hours per cell = (end_to_end_wall_min / 60) * (n_workers + 1) — the +1 is the MASTER; assert a cell's hours include the master (n_workers+1, not n_workers) and use end_to_end wall (not stage4-only).
    - test_eur_factor_measured_then_fallback: with a measured EUR cell in the probe TSV, EUR_factor = measured afr_rate/eur_rate; with no EUR cell, factor = 3.01 with a +/-20% band recorded as the source.
    - test_contingency_factor_from_variance: a contingency factor derived from the observed probe blocks_per_min variance is applied to PROJECTED (assert PROJECTED_with_contingency >= PROJECTED_raw and the factor is recorded).
    - test_egress_bundle_projection: the model projects an egress bundle-size total (sum of est_output_gib over compute cells, plus per-chrom + monolith bundle estimates) and flags it against the 50 GB egress cap.
    - test_gate_predicate_green: PROJECTED such that PROJECTED * 1.3 <= BUDGET_CAP -> disposition == "GREEN".
    - test_gate_predicate_red_and_levers: PROJECTED * 1.3 > BUDGET_CAP -> disposition in {"YELLOW-narrow-radius","YELLOW-finer-split","RED"} per the decision tree; assert YELLOW-narrow-radius is recommended when there is buffer_bp band to cut (radius > Pan-UKBB 10 Mb), and RED when no lever room is flagged.
  </behavior>
  <action>
    1. Write `src/python/redo_ld_cost_model.py`:
       - `load_probe_rates(probe_tsv) -> dict[(ancestry, region_class) -> blocks_per_min]` reading m3-W2-cost-probe.tsv; also load the per-cell measured cluster_hours + variance.
       - `load_preflight_counts(preflight_tsv) -> DataFrame` reading m3-W2-preflight-counts.tsv (REAL n_var, est_block_count, routed_path, est_output_gib per cell). The cost model consumes THIS, not span guesses.
       - `eur_factor(probe_rates) -> (factor, source)`: if both an AFR and EUR rate exist for the same class, factor = afr_blocks_per_min / eur_blocks_per_min (EUR slower => factor > 1, source="measured"); else (3.01, "sample-ratio-assumed-A7") with a +/-20% band.
       - `n_workers_plus_master(cluster_vcpu) -> int`: workers = cluster_vcpu/16; returns workers + 1 (the MASTER). All cluster_hours use (n_workers + 1).
       - `project_cell_hours(preflight_df, probe_rates, eur_factor) -> DataFrame`: per compute cell, cluster-h = preflight_block_count / matched_blocks_per_min / 60 * (n_workers + 1); EUR cells multiply the AFR rate's hours by eur_factor; uses end_to_end (master-inclusive) accounting calibrated from the probe's measured end_to_end_wall_min vs stage4_wall_min ratio (overhead_factor) so filtering/count_rows/writes/retries/startup/idle are included, not just Stage-4.
       - `three_totals(projected_df) -> dict`: returns {n_logical_parents: 322, n_compute_cells: len(compute rows), parent_aggregate: groupby(parent_region_id).sum(), total_compute_h, total_parent_h}. xlarge parents are NEVER priced directly — only as Sigma over their split_status=="subregion" rows.
       - `apply_contingency(total_h, probe_rate_variance) -> (total_with_contingency, contingency_factor)`: factor = 1 + k * coefficient_of_variation of the probe blocks_per_min (k stated, e.g. 0.5; min floor 1.15); PROJECTED uses the contingency-adjusted total.
       - `project_egress_bundles(preflight_df) -> dict`: total est_output_gib (sum over compute cells), per-chrom bundle sizes, monolith size; flag each against EGRESS_CAP_GB = 50.
       - `evaluate_gate(projected, budget_cap_cluster_h, *, lever_room=None) -> dict` returning `{projected, budget_cap, headroom_ok: projected * 1.3 <= budget_cap, disposition}`; disposition == "GREEN" if headroom_ok else the recommended lever ("YELLOW-narrow-radius" if buffer_bp band > Pan-UKBB 10 Mb i.e. there is band to cut; "YELLOW-finer-split" if a specific (ancestry, region_class) dominates and can be split finer; else "RED"). Encode the EXACT predicate `projected * 1.3 <= budget_cap` verbatim.
       - `main()` CLI: `--probe-tsv --preflight-tsv --projection --budget-cap-cluster-h --out-budget-md`; writes m3-W2-budget-redo.md with the THREE totals, the contingency factor, the egress bundle projection, BUDGET_CAP_CLUSTER_H, the `PROJECTED * 1.3 <= BUDGET_CAP` evaluation, the credit-$ at the n2-highmem-16 rate (A8 ~$0.95-1.10/hr/worker; flag for confirmation), and the disposition.
       - REQ-PATH-PARAMETERIZATION: no hardcoded /share/clintonlab|/rs1/researchers|/gpfs_common paths.

    2. Write `tests/m3/test_redo_ld_cost_model.py` with the 8 behavior tests above using synthetic in-memory preflight + probe TSVs + projection DataFrames (no cluster, no AoU). Assert the exact gate predicate (projected * 1.3 <= budget_cap) on both the GREEN and RED sides; assert the three-totals separation and the master-inclusive (n_workers+1) accounting explicitly.

    3. Run redo_ld_cost_model.py against the real m3-W2-preflight-counts.tsv + m3-W2-cost-probe.tsv + the post-split projection + the BUDGET_CAP_CLUSTER_H (confirm the numeric value with Carter at the gate; the old ~1,117 cluster-h was the basis for the GATE-1 cost approval — capture the actual approved cap). Write m3-W2-budget-redo.md. The memo MUST state: the THREE totals (322 logical parents / expanded compute cells / aggregate parent costs), the contingency factor, the egress bundle projection vs the 50 GB cap, the BUDGET_CAP_CLUSTER_H, the evaluated `PROJECTED x 1.3 <= BUDGET_CAP` result, the disposition (GREEN/YELLOW-narrow-radius/YELLOW-finer-split/RED) — where YELLOW-narrow-radius ties to the m3-02b --subregion-buffer-mb knob — and explicitly that the full 322-cell production fire is OUT of scope here and stays in Wave 4 (m3-04). If GREEN, the memo states m3-04 is unblocked; if RED/YELLOW, it states the next lever + that a re-probe is needed before m3-04.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis &amp;&amp; PATH=/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin:$PATH pytest tests/m3/test_redo_ld_cost_model.py -v --tb=short &amp;&amp; test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md &amp;&amp; grep -c "PROJECTED" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c "projected \* 1.3 <= budget_cap\|projected\*1.3<=budget_cap\|PROJECTED.*1.3.*BUDGET_CAP" src/python/redo_ld_cost_model.py` returns >= 1 (the exact predicate encoded).
    - `grep -c "def evaluate_gate\|def project_cell_hours\|def eur_factor\|def three_totals\|def apply_contingency\|def project_egress_bundles\|def load_preflight_counts" src/python/redo_ld_cost_model.py` returns >= 6.
    - `grep -c "GREEN\|YELLOW-narrow-radius\|YELLOW-finer-split\|RED" src/python/redo_ld_cost_model.py` returns >= 4 (all dispositions present).
    - `grep -c "n_workers + 1\|n_workers+1\|+ 1.*master\|master" src/python/redo_ld_cost_model.py` returns >= 1 (MASTER-inclusive cluster-hours).
    - `grep -c "parent_region_id\|subregion\|three_totals\|n_logical_parent" src/python/redo_ld_cost_model.py` returns >= 2 (3-totals + xlarge parent = sum over sub-regions).
    - `grep -c "contingency\|EGRESS_CAP\|est_output_gib" src/python/redo_ld_cost_model.py` returns >= 2 (contingency factor + egress bundle projection).
    - `pytest tests/m3/test_redo_ld_cost_model.py -v` reports >= 8 passed, 0 failed.
    - `test -f .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` exits 0.
    - `grep -c "PROJECTED" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1.
    - `grep -c "BUDGET_CAP" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1.
    - `grep -cE "GREEN|YELLOW|RED" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1 (the disposition).
    - `grep -ci "logical parent\|compute cell\|aggregate" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1 (the 3 totals stated).
    - `grep -ci "out of scope\|Wave 4\|m3-04" .planning/phases/m3-aou-afr-ld-panel-build/m3-W2-budget-redo.md` returns >= 1 (322-cell fire stays in m3-04).
    - `grep -rn "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/redo_ld_cost_model.py` returns 0 matches (REQ-PATH-PARAMETERIZATION).
  </acceptance_criteria>
  <done>
    redo_ld_cost_model.py extrapolates the measured blocks_per_min over the REAL preflight n_var/block_count (not span guesses), keeps THREE separate totals (322 logical parents / expanded compute cells / aggregate parent costs with xlarge = Sigma over sub-regions), computes MASTER-inclusive end-to-end cluster-hours, applies a contingency factor from probe variance, projects egress bundle sizes vs the 50 GB cap, evaluates the exact `PROJECTED x 1.3 <= BUDGET_CAP` gate, and writes m3-W2-budget-redo.md with all three totals + cap + disposition (GREEN/YELLOW/RED) + the explicit note that the full 322-cell fire stays in m3-04. >= 8 unit tests pass.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| AoU perimeter -> NCSU | The preflight + probe produce summary LD .npz/.bm + count metrics in the AoU bucket; nothing crosses to NCSU in this plan except the cost metrics (blocks_per_min, n_var, cluster_hours) hand-recorded into the TSVs. No individual-level genotypes leave the perimeter. |
| Quota filing -> quota grant | A FILED ticket is not a GRANT; sizing the cluster off an assumed grant risks a wedge or a wrong projection. Two separate gates (Task 1 filed, Task 2 granted) close this. |
| Cluster spend -> credit balance | The probe spends real AoU credits; the executable cost controls (max wall/credit, spill/OOM kill, guaranteed shutdown) cap the probe spend, and the go/no-go gate caps the much larger production spend. |
| VPC-SC perimeter | The sized cluster + quota request live entirely inside the Verily perimeter; the request path itself is perimeter-gated (Q-RS1 A1). |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-M3RS-EGRESS-02 | Information disclosure | controlled-tier AoU genotypes during preflight + probe | mitigate | The probe emits only summary LD matrices + AF metadata to the in-perimeter bucket (REQ-AOU-LD-EGRESS); each cell over n>=60k AFR / n>=130k EUR trivially clears the n>=20 suppression floor; NOTHING individual-level crosses to NCSU (only the hand-recorded cost/count metrics). No egress request is filed in this plan — the per-bundle reviews stay in m3-04. The egress bundle-size projection (Task 4) sizes the future egress vs the 50 GB cap. |
| T-M3RS-VPCSC-01 | Cross-perimeter leakage | the sized cluster + bucket | mitigate | All compute + writes stay in-perimeter (gs://rw-migration-aou-rw-476cdac2); no cross-perimeter transfer (regenerate-in-perimeter per SKILL.md RW2.0-mirror facts); the quota request names the in-perimeter project + us-central1. |
| T-M3RS-COST-02 | DoS / cost-overrun / runaway cluster billing | the probe AND the production 322-cell fire | mitigate | EXECUTABLE controls on the probe: MAX_WALL_MIN_PER_CELL, MAX_PROBE_CREDIT_USD, spill/OOM kill, a GUARANTEED post-probe shutdown, and a shutdown-VERIFICATION artifact (m3-W2-cluster-shutdown.md with the stop output + $0 idle check) — not prose. The production fire is gated by PROJECTED x 1.3 <= BUDGET_CAP with 30% headroom; cluster_size capped at min(granted, 400). |
| T-M3RS-COST-03 | Integrity / under-estimation | a too-cheap projection re-greenlighting an intractable fire (the dev-10 trap) | mitigate | The cost model consumes REAL preflight n_var/block_count (not span guesses), uses the MEASURED EUR factor (the mandatory EUR cell), MASTER-inclusive end-to-end cluster-hours, a contingency factor from observed probe variance, and three separate totals — closing the 36-110x under-estimate that killed dev-10. |
| T-M3RS-QUOTA-01 | Availability / false-readiness | a queued ticket mistaken for a grant -> the probe sizes off an assumed cluster | mitigate | Task 2 (GRANTED) is a SEPARATE blocking gate requiring a NUMERIC ceiling; Task 3 depends_on Task 2, not the Task 1 filing. A pending ticket cannot pass Task 2. |
| T-M3RS-PROBE-01 | Integrity / false-completion | _SUCCESS over empty .npz/.bm masking a failed probe/preflight cell | mitigate | D-M3-10 contents-validation: each fired cell is gsutil-du + Hail/np count verified before being recorded; _SUCCESS alone is NEVER accepted (baked by the m3-W1 empty-MT catastrophe). |
| T-M3RS-HLA-01 | Integrity | HLA/6p21 (region_00145) density exceeding the 10 Mb -> ~69k-var assumption (A4) | mitigate | The preflight count pass MANDATORILY includes HLA region_00145; any over_threshold (>75k var) cell is auto-split (lower --max-subregion-span-mb) or flagged before the cost model consumes it. |
</threat_model>

<verification>
**Plan-level checks:**

1. m3-W2-quota-ticket.md exists naming N2_CPUS + us-central1 + >=400 (Task 1) AND m3-W2-quota-grant.md records a NUMERIC granted ceiling + cluster_size (Task 2) — the filed-vs-granted split.
2. m3-W2-preflight-counts.tsv exists with n_var + routed_path + est_block_count + over_threshold columns + an HLA region_00145 row, >= 4 cells (Task 3 STEP A).
3. m3-W2-cost-probe.tsv exists with the master-inclusive end-to-end metric set + >= 3 measured cells incl. the MANDATORY EUR cell + region_00006 + m2_region_00040__sub00 (Task 3 STEP B).
4. m3-W2-cluster-shutdown.md exists with the stop confirmation + a $0/idle billing check (Task 3 STEP C — executable shutdown, not prose).
5. `pytest tests/m3/test_redo_ld_cost_model.py -v` >= 8 passed (Task 4).
6. m3-W2-budget-redo.md states the THREE totals + contingency + egress projection + BUDGET_CAP + the `PROJECTED x 1.3 <= BUDGET_CAP` evaluation + disposition + the explicit "322-cell fire stays in m3-04" note.
7. The exact gate predicate `projected * 1.3 <= budget_cap` + MASTER-inclusive (n_workers+1) accounting are encoded in redo_ld_cost_model.py (Task 4 acceptance).
8. REQ-PATH-PARAMETERIZATION: `grep -rn "/share/clintonlab\|/rs1/researchers\|/gpfs_common" src/python/redo_ld_cost_model.py` returns 0.
</verification>

<success_criteria>
- The quota gate is split: the N2_CPUS >= 400 us-central1 request is FILED (Task 1) and a SEPARATE gate records the NUMERIC grant + cluster_size (Task 2); the probe depends on the grant, not the filing.
- A cheap preflight count pass records REAL n_var + real routed path + est block/output size for every post-split cell (incl. HLA region_00145), auto-splitting/flagging any >75k-var cell.
- The >=3-cell cost probe fires WITH the mandatory EUR cell on the sized n2-highmem-16 cluster under EXECUTABLE cost controls (max wall/credit, spill/OOM kill); the Q-RS2 executor config is validated (spill recorded); each cell is data-layer-verified per D-M3-10.
- The cluster is shut down with a VERIFIED shutdown artifact (stop output + $0 idle check), not prose.
- redo_ld_cost_model.py re-derives the budget from REAL preflight counts, keeps THREE separate totals (322 logical parents / expanded compute cells / aggregate), computes MASTER-inclusive end-to-end cluster-hours with a contingency factor, projects egress bundle sizes vs the 50 GB cap, and evaluates the exact `PROJECTED x 1.3 <= BUDGET_CAP` gate.
- m3-W2-budget-redo.md records the three totals + cap + disposition (GREEN/YELLOW/RED) + the explicit out-of-scope note for the 322-cell fire.
- The full 322-cell production fire stays in Wave 4 (m3-04) — this plan ends at the go/no-go decision.
</success_criteria>

<output>
After completion, create `.planning/phases/m3-aou-afr-ld-panel-build/m3-02c-W2-rescope-quota-probe-and-gonogo-SUMMARY.md` recording:
- The quota channel used + the FILED date + the GRANTED N2 ceiling + the resulting cluster_size (the filed-vs-granted split)
- The preflight count pass results: any cell that overshot 75k var (esp. HLA region_00145) + whether it was auto-split or flagged
- The probe cells' measured blocks_per_min (AFR-medium, AFR-subregion, the MANDATORY EUR cell) + spill behavior + the cores value the projection assumes + the master-inclusive end-to-end vs Stage-4 overhead factor
- The executable cost controls that fired (any wall/credit/spill trip) + the shutdown-verification result ($0 idle confirmed)
- The new PROJECTED (all THREE totals) vs the stale ~1,117 + the contingency factor + the credit-$ at the confirmed n2-highmem-16 rate + the egress bundle projection vs the 50 GB cap
- The BUDGET_CAP_CLUSTER_H value + the disposition (GREEN/YELLOW/RED) + the next step (m3-04 unblocked, or which lever + re-probe) — where YELLOW-narrow-radius ties to the m3-02b --subregion-buffer-mb knob
</output>
