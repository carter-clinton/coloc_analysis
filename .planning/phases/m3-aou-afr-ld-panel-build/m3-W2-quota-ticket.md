# m3-02c Quota Gate 1 (FILED) — RESOLVED, no ticket required

**Date:** 2026-06-20
**Gate:** m3-02c Task 1 — QUOTA FILED (the longest-lead human action; the plan surfaced it first so a ticket could sit in a queue for days–weeks while other prep proceeds).
**Disposition:** ✅ **PRE-SATISFIED — NO TICKET FILED.** The controlled-tier workspace already carries an `N2_CPUS` ceiling that exceeds the probe's need by ~12×, so there is nothing to request. Both the FILED (Task 1) and GRANTED (Task 2) sub-gates are closed by this pre-existing grant.

## What the gate would have requested (for the record)

| Field | Value |
|---|---|
| Metric | **N2 CPUs** (`N2_CPUS`) |
| Region | **us-central1** |
| Amount that would have been requested | **≥ 400** (24× `n2-highmem-16` workers + 1× `n2-highmem-16` master = 25 × 16 = 400 N2 vCPU; ask band 400–512) |
| Channel | n/a — no request submitted |
| Date filed | n/a — not filed |
| Request / ticket ID | n/a — not filed |

## Why no filing is needed

The existing live ceiling is **`N2_CPUS` = 5,000 in us-central1** on the VM-host project `wb-perky-corn-6639` (read in-perimeter from Console → IAM & Admin → Quotas). 400 vCPU fits with ~4,600 vCPU of headroom. The original plan (m3-REVIEWS.md, Codex HIGH) split this gate into FILED → GRANTED because the research treated the grantable ceiling as unknown and likely ticket-gated; reality is the workspace was provisioned well above the probe's footprint.

The NUMERIC grant is recorded in the companion artifact **`m3-W2-quota-grant.md`** (Task 2), including `cluster_size = min(granted, 400)` and the belt-and-suspenders live re-check command to run from a running cluster's in-perimeter terminal **before** the 400-vCPU launch (the Console value can lag the authoritative number per a standing "values are being updated" banner).

## Cross-reference

- Memory: `reference_aou_n2_quota_already_5000` — wb-perky-corn-6639 already has N2_CPUS=5000 in us-central1; **do NOT file a quota-increase ticket**.
- Task 2 (numeric grant): `m3-W2-quota-grant.md`.
- Belt-and-suspenders re-check is a Task 3 STEP-0 pre-flight item (see `m3-W2-AOU-FIRE-BRIEF.md`).
