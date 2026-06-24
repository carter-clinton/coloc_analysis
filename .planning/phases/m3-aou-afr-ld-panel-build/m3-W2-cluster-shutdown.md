# m3-W2 Cluster Shutdown (Task 4 AFR re-probe v2)

- Cluster: HAIL Spark 20260604 (reused from v1; not 20260605/20260617/20260620)
- Action: STOPPED at handback via Apps panel (UI Pause/Stop; not a billable compute action).
- UTC timestamp: 2026-06-24T01:18:25Z
- Status: STOPPED (idle cost while stopped = $0/hr). Apps panel shows the Stopped badge + Start button.

## STEP B result (recorded in m3-W2-cost-probe.tsv)
- AFR m2_region_00040__sub00, routed A.3 (density veto: n_var 64176 > 24301), ordering B, status COMPLETED.
- n_var=64176, block_count=168, stage4_wall_min=55.679, end_to_end_wall_min=57.421, blocks_per_min=3.0173, any_spill=False.
- peak_executor_mem_gib = na (no per-executor peak emitted in the run logs; recorded as na, not a number).
- Data-layer verify (D-M3-10): .bm du=19917095023 bytes (~18.5 GiB) >> 0; _SUCCESS + metadata.json present; part-000 = 134534698 bytes (read-back OK).
- Output: gs://rw-migration-aou-rw-476cdac2/ld/cost_probe_m3d/bm/m2_region_00040__sub00.bm

## Artifact handback (token-free path)
- The AoU Workbench clone has NO git push token (the brief's STEP C assumed one). Rather than place a PAT in a browser terminal, the three artifacts were `cat` to the terminal and the AoU local commit (07f43dc) was DISCARDED when the cluster stopped.
- Source of truth = the verified .bm in GCS + the cat output; NCSU reconstructs the three artifacts and pushes them from the credentialed NCSU node. The discarded AoU commit SHA is immaterial (the rate/wall numbers and .bm are preserved).

## Notes
- Ordering A was not run: the A.3 write path at HEAD is hard-locked to ordering B (band-before-checkpoint); the un-materialized matmul ordering A was deliberately removed (hang-prone). Fired ordering B only.
- HLA forward note: region_00145__sub19 AFR is over-threshold in preflight (95997 var, est 158.8 blk, 10.16 GiB) -> chr6 finer-split (--max-subregion-span-mb 3) needed before m3-04 (plan T-M3RS2-HLA-01).
- EUR re-confirm was skipped (optional per brief v2.1). The v1 EUR-B completing rate (m2_region_00040__sub01, 4.85 blocks/min, commit 210e66c) is on a different block basis (810 matmul blocks) than this AFR cell (168 banded blocks) and is NOT combined into a measured AFR/EUR factor; Task 5 uses the conservative 3.01 sample-ratio fallback.
