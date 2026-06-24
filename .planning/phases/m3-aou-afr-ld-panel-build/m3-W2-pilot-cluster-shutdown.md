# m3-W2 PILOT — cluster shutdown record (native-plink pilot)

> Distinct from `m3-W2-cluster-shutdown.md` (that one records the prior Task-4 AFR
> re-probe v2). This file records the **native-plink PILOT** shutdown.

- **Cluster: HAIL Spark `20260604` — STOPPED** at handback (Apps-panel Stop; UI Pause,
  not a billable compute action). Stopped badge + Start button confirmed → **$0 idle**.
- The other three clusters (`20260605`, `20260617`, `20260620`) were left Stopped and
  untouched.
- **Worker resize abandoned as friction:** both graceful and forced
  (`--graceful-decommission-timeout 0s`) resize-to-2-workers stalled in UPDATING. Per the
  brief's fallback ("if resizing is friction, just run it as-is and stop promptly"), the
  pilot ran on the full 24-worker cluster. plink ran **single-node on the master**
  `n2-standard-16` (16 vCPU / 64 GB), so worker count did not affect the measurements.

## Handback (token-free)
- The AoU Workbench clone has **no git push token**; nothing was pushed from the
  Workbench. The agent `cat`'d the artifacts to the terminal and pinged "pilot-recorded".
- The terminal websocket dropped as the cluster began stopping, so the on-disk
  `m3-W2-pilot-plink-native.tsv` / `m3-W2-pilot-report.md` / `*_time.txt` could **not** be
  cat'd verbatim. NCSU reconstructed the TSV (verbatim row) + report (from the handback
  numbers) and pushed from the credentialed NCSU node. See provenance note in
  `m3-W2-pilot-report.md`. [[feedback_push_ncsu_before_aou_clone_fire]]

## Verdict carried forward
GREEN — native plink lands the full AFR panel well under $3–4k (banded ~$174–490 /
square ~$385–1,084). The Hail 34k-cluster-h path is NOT taken. Next = re-plan **m3-02e**.
