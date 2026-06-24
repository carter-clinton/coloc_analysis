# m3-W2 Budget Redo — LD production go/no-go

Re-scoped around the MEASURED binding constraints (A.3 write throughput + per-cell egress GiB), extrapolated from the COMPLETING-cell re-probe rates over the REAL re-split preflight counts. The prior INTERRUPTED/NA probe row is EXCLUDED from the rate basis.

## Three totals (do not conflate)

- **(a) n_logical_parent_panels** = 322 (the M2 region x ancestry logical panels)
- **(b) n_compute_cells** = 552 (> 322 post-split: each xlarge parent expands into N sub-cells)
- **(c) aggregate parent** = Sigma over each parent's split_status==subregion rows; total_parent_h = 29745.0 cluster-h

## Extrapolation basis

- COMPLETING probe rates (blocks_per_min): {'AFR': 3.0173}
- measured EUR/AFR write factor = 3.010 (source: sample-ratio-assumed-A7 (+/-20%))
- end-to-end overhead_factor (e2e/stage4) = 1.031
- master-inclusive workers+1 = 25 (cluster_vcpu 384)

## Projection + contingency

- PROJECTED (raw, master-inclusive) = 29745.0 cluster-h
- contingency factor (from probe blocks_per_min CoV) = 1.150
- **PROJECTED (with contingency)** = 34206.7 cluster-h (~$34,207 at $1.00/worker-h, A8 rate — flag for confirmation)

## Per-chromosome egress projection

- total summary-LD+AF output = 8866.7 GiB across 150 per-chrom bundles (EGRESS_CAP_GB=50, a CONSERVATIVE project working ceiling per Q5/A2 — confirm the real number on first export)
- chromosomes split into _a/_b (> 50 GB): ['NA']
- bundles still over cap (indivisible single cells): 47

## Gate evaluation

- BUDGET_CAP_CLUSTER_H = 1117.0
- predicate: PROJECTED * 1.3 (44468.8) <= BUDGET_CAP (1117.0) -> headroom_ok = False
- **DISPOSITION: YELLOW-finer-split**

NOT GREEN: the next lever is the disposition above (YELLOW-narrow-radius = cut the buffer band; YELLOW-finer-split = lower --max-subregion-span-mb, the likelier post-Q3 lever since the buffer is already narrow; RED = no lever room). A re-probe is needed before m3-04.

## Scope

The full 322-cell production fire is EXPLICITLY OUT OF SCOPE here and stays in Wave 4 (m3-04). This plan ends at the go/no-go decision.

## Provenance & caveats (NCSU Task 5 run, 2026-06-23)

- **Rate basis** = the v2 AFR re-probe (`m2_region_00040__sub00`, A.3 ordering-B, **3.0173 blocks/min**, 0 spill, `.bm` data-layer verified ~18.5 GiB). This is the clean AFR completing rate the re-probe was blocked on.
- **Preflight denominator** = the **FULL 552-cell production** preflight (`m3-W2-preflight-counts-FULL.tsv`), recovered from v1 commit `210e66c`. It is geometry-identical to the v2 dev preflight: the probe cell's `n_var` (64176), `est_block_count` (96.789), and `est_output_gib` (6.2286) match exactly; only `routed_path` differs (A.2 pre-fix vs A.3 post-fix), which the cost model does not use. The committed `m3-W2-preflight-counts.tsv` (54 dev cells) is the cluster-faithful v2 STEP-A artifact but is NOT the production denominator — using it gives a dev-subset projection of only 4,683.5 cluster-h.
- **EUR/AFR factor = 3.01 (sample-ratio fallback), NOT the v1 measured rate.** The v1 EUR completing rate (4.85 blk/min, `m2_region_00040__sub01`, commit `210e66c`) counts **matmul** blocks (810); the v2 AFR rate counts **banded** blocks (168). Combining them yields a "measured" factor of ~0.62 (EUR cheaper than AFR), which is physically backwards (EUR has 220k samples vs AFR 73k). The conservative 220k/73k = 3.01 sample-ratio fallback governs.
- **Budget cap = 1117 is PROVISIONAL** (the superseded prior estimate, used only to render a disposition). The real cap = Carter's AoU credit ÷ ~$1/worker-h (A8 rate, flag for confirmation). The **YELLOW-finer-split** disposition holds for any cap below ~34k cluster-h, so it is robust to the actual cap.
- **Egress caveat:** the preflight carries no `chr` column, so all cells lump into one `chr=NA` bucket — the "150 bundles / 47 over cap" split is a **degenerate artifact**. The **8,866.7 GiB total output volume IS valid**; the per-chromosome bundling must be recomputed with `chr` present before the m3-04 egress.
- **Uniform-A.3-rate caveat:** the A.3 banded write rate is applied to all cells. Post-fix the expensive cells all route A.3 (density veto on dense-narrow + large regions), so this is a reasonable conservative basis.

## Bottom line

PROJECTED ≈ **34,207 cluster-h** (× 1.3 = **44,469**), ~**30×** the old 1,117-cluster-h estimate and far above any plausible AoU credit cap → **NOT GREEN**. The binding lever is **finer splitting** (lower `--max-subregion-span-mb`) to cut blocks-per-cell, of which the chr6/HLA `region_00145__sub19` finer-split (T-M3RS2-HLA-01) is the first instance. m3-04 production stays BLOCKED pending a re-scoped (finer-split) cost that clears the real cap.
