# M3-W2 AoU Hail RegionPool OOM Forensics — 2026-05-04

## Summary
AOU-1 cohort definition cell 3 (`load_qc_cohort(ancestry='afr')`) hung with ZERO completed Spark tasks across 2h25m+ of wall-clock execution on a 16-worker (4 vCPU / 15 GB) Dataproc cluster. Root cause: Hail RegionPool off-heap OOM in executor containers, exit code 56, infinite Spark task retry loop (attempt 38 observed at diagnostic time).

## Cluster Spec at Time of Failure
- Master: 16 vCPU, 104 GB RAM
- Workers: 16 standard, 0 preemptible
- Worker shape: 4 vCPU, 15 GB RAM, 150 GB disk (n2-standard-4 default)
- Cost: $5.00 / hr

## Key Forensic Numbers
- Spark App ID: application_1777860102738_0003
- Stage 8 numTasks: 290,384
- Stage 8 numCompleteTasks: 0
- Stage 8 numFailedTasks: 2,480 (at dump time)
- Running task attempt number: 38
- Executor IDs observed: 1248-1258 (max ID seen) — implies ~1240 executors launched and lost
- Failure reason: ExecutorLostFailure / Container exit code 56 / RegionPool memory exhaustion

## Critical Context — v7→v8 CDR Version Bump
The most recent commit on src/python/aou_ld_panel.py is `ac261f2` (v7→v8 CDR_VERSION bump). Prior 'successful' run reference of 1h57m was on v7 data. v8 hail.mt is shaped at 290,384 partitions; partition-explosion + RegionPool allocation per concurrent task is the structural failure mode.

## Remediation
Fix branch: m3/w2-oom-fix-naive-coalesce-and-cores-1
Decision ref: DEC-2026-05-04-01 (orchestrator-staged)
- Code change: insert `mt = mt.naive_coalesce(2048)` immediately after the ancestry filter in `load_qc_cohort()` (line ~204 of aou_ld_panel.py)
- Spark config change: pass `spark.executor.cores=1` via SparkSession.builder in cell 1 of AOU-1_cohort_definition.ipynb

## Files in this dump
- 01-10: Spark UI / YARN REST API JSON dumps
- 11-12: Hail driver logs (current 19:22 run + prior 05:52 run)
- 13-15: git forensics (commit history, v7-v8 diff stat, HEAD SHA)
- 16-18: process / port / top snapshot at dump time
- 19: hailctl config
