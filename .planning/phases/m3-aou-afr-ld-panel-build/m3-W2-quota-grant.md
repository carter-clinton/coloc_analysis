# m3-02c Quota Gate — RESOLVED (no filing required)

**Date:** 2026-06-18
**Gate:** m3-02c Task 1 (quota FILED) + Task 2 (quota GRANTED, numeric) — the longest-lead human-action gate for the Wave-1 cost probe.
**Disposition:** ✅ **PRE-SATISFIED.** No quota increase filed, no support ticket needed. The existing ceiling already exceeds the target by ~12×.

## Audit record (read from Console → IAM & Admin → Quotas, in-perimeter)

| Field | Value |
|---|---|
| Project (Dataproc VM-host) | `wb-perky-corn-6639` |
| Workspace | `aou-rw-476cdac2` |
| Metric | **N2 CPUs** (`N2_CPUS`) |
| Region | **us-central1** |
| **Current limit** | **5,000** |
| Current usage | 0 (0%) |
| Adjustable | No |

**Target need:** 24× `n2-highmem-16` workers + 1× `n2-highmem-16` master = 25 × 16 = **400 N2 vCPU**. Fits under the 5,000 ceiling with ~4,600 vCPU headroom.

## Assumptions closed by this read

- **Region == us-central1** — confirmed (Quotas region filter + stopped cluster `20260617` config: master `n2-standard-16`, 16× `n2-standard-4`, all N2 family → `N2_CPUS` is the correct metric). Closes research Q-RS1 assumption A1 (region) + A2 (ceiling).
- **Project scope** — confirmed `wb-perky-corn-6639` is the VM-host project (the `N2 CPUs / us-central1` row exists on it). No billing-vs-host project disagreement.
- **"Adjustable: No"** is irrelevant — no adjustment is required.

## Why the original m3-02c gate design is now moot

The plan (Codex review finding #11) split the gate into FILED → GRANTED because the research treated the grantable ceiling as unknown and likely ticket-gated (days–weeks lead). Reality: the controlled-tier workspace already carries a 5,000 N2_CPUS ceiling, so both sub-gates are satisfied by this pre-existing grant. The executor of m3-02c should mark Task 1 + Task 2 **done (pre-satisfied)** and proceed to the preflight/probe (Task 3) once the Wave-0 code lands and a cluster is launched.

## Caveat + belt-and-suspenders re-check

A standing Console banner reads: *"Values for quotas are being updated. This may take 2-3 weeks to complete"* + a *"server was only able to partially fulfill your request"* warning. Our specific `N2_CPUS / us-central1` row rendered cleanly at 5,000, but the Console value can lag the authoritative number. **Before the actual 400-vCPU cluster launch** (m3-02c Task 3 preflight), re-confirm the live ceiling from the in-perimeter terminal of a running cluster:

```bash
PROJECT=$(gcloud config get-value project 2>/dev/null)   # expect wb-perky-corn-6639
gcloud compute regions describe us-central1 \
  --project="$PROJECT" \
  --flatten="quotas" \
  --filter="quotas.metric=N2_CPUS" \
  --format="table(quotas.metric, quotas.limit, quotas.usage)"
```

This reads the authoritative quota directly rather than the possibly-stale Console cache. If it still shows ≥ 400, launch proceeds; if it has somehow dropped below 400 (not expected), revisit before sizing the cluster.
