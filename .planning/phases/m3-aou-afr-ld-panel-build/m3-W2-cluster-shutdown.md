# m3-W2 Cluster Shutdown — AoU LD cost RE-PROBE (m3-02d)

**Cluster:** HAIL 20260604 (JupyterLab_Spark_cluster_for_AoU_Spark_20260604) — n2-standard-16 x24, 64 GB master.
**Workspace:** aou-rw-476cdac2 / project wb-perky-corn-6639 / bucket gs://rw-migration-aou-rw-476cdac2 / region us-central1.
**Shutdown timestamp (UTC):** 2026-06-23T20:55:00Z
**Stop method:** AoU Workbench Apps panel -> Pause/Stop on the 20260604 cluster (UI control; not a billable compute action).
**Status:** STOPPED (compute paused; $0 idle compute confirmed — no running cluster after stop).

## Work completed this session (Task 4 = in-perimeter LD cost RE-PROBE)
- STEP A full preflight: count-only write_preflight_counts over the FULL config/ld_regions.tsv (552 compute cells, 276 AFR + 276 EUR). Wrote m3-W2-preflight-counts.tsv (552 data rows). Wall ~38.4 min. Count-only (filtered count_rows per cell) — NO matmul/LD-output writes.
- STEP B billable fires:
  - B.1 AFR m2_region_00040__sub00 (A.2): matmul completed (288 blocks) but driver collect in to_numpy() hung (dense 16.5 GB > 11 GiB driver heap). INTERRUPTED_a2_driver_collect; killed (SIGINT/TERM + yarn -kill). NOT a usable rate.
  - B.3 EUR m2_region_00040__sub01 (A.3, ordering B): COMPLETED. matmul 810 blocks (~13 min) then banded checkpoint 143 blocks; 0 spill throughout; peak exec heap ~1.85 GiB; end-to-end 180.6 min (exceeded 90-min brief cap — write-throughput-bound long tail). Data-layer verified: final .bm = 15.6 GiB (16,765,544,992 B), 143 parts, _SUCCESS + metadata.json, part-000 read-back OK. This is the CR-01 'banded write completes' proof + the A.3 ordering-B rate.
  - B.2 EUR A.2: deferred per user (low-density pass would not validate high-density A.2; A.2 rate needs a bigger driver). B.4 AFR A.3 factor: NOT fired per user.

## Path-bug note (resolved)
First full-preflight attempt crashed on read_final_cohort_mt: it used gs://.../ld/mt/mt_{anc}_qc.mt (erroneous /mt/ segment); the canonical path is gs://.../ld/mt_{anc}_qc.mt. The reader reads literally and refused the non-existent path (false 'empty-final' alarm). Verified after fix: AFR count_cols=73122, EUR count_cols=220098 (no refusal). NO re-finalize was performed; MTs were intact all along.

## Idle-cost sequencing
Artifacts committed + pushed BEFORE the cluster stop (prior session lesson: stopping the cluster kills the gateway/terminal mid-handback). Stop performed from the Apps panel AFTER push.
