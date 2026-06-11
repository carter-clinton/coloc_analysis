# Wave 2 readiness review — what stands between "cohort recovered" and "LD compute firing"

**Status:** read-only review drafted 2026-06-10 while the AFR-sens recovery dry-run runs. Source: `WAVE-2-PLAN.md` (2026-06-04 audit) cross-checked against current cohort state. **No decisions made here** — this surfaces the open gates so there's no scramble the moment cohort 3/3 lands.

---

## Where the gate sequence actually stands (vs WAVE-2-PLAN §3)

| Gate | What it is | Status NOW | Owner |
|---|---|---|---|
| **GATE 1.5** | Genome-wide cohort rebuild (3 MTs) — prerequisite for ALL LD compute | **2/3 done + verified** (AFR-primary 73,122×20,767,864; EUR 220,098×11,375,140). **AFR-sens recovery in flight** (finalize-only dry-run). This is the *only* remaining cohort step. | finishing now |
| **GATE 0** 🔴 | AoU egress classification ruling for the variant×variant LD matrices, **in writing**, before ANY Dataproc LD spend | **UNVERIFIED / likely not in hand** (WAVE-2-PLAN §3 + §5.1: "Unverified whether this ruling exists yet"). HARD gate. | **Carter** |
| **GATE 1** 🟠 | Pre-fire readiness | Code work ✅ DONE. **2 Carter-only items open:** CDR pin (v8 stable, no mid-flight v8→v9), Cost/credit confirmation (~1,117 cluster-h → credit-$ + a cap) | **Carter** |
| **GATE 2** 🟡 | dev-10 LD fire + AOU-4 validation memo (the rigor gate; cheap) | not started — gated behind 1.5 + 1 | next compute step |
| **GATE 3** 🟢 | full 322-cell production fire + 44 egress requests | not started — gated behind 0 + 2 | later |

## The critical-path read

- **GATE 1.5 is nearly closed** — once AFR-sens is recovered + banked (3-row `cohort_summary_m3.tsv`), the cohort substrate for all LD compute exists genome-wide.
- **GATE 0 is the true long pole and it is NOT on the cohort path** — it gates LD-matrix *egress*, decoupled from the cohort build (GATE 1.5 is internal, "gated on GATE 1 but NOT on GATE 0", §3). **It should be filed/confirmed in parallel NOW** — it has an AoU SLA and blocks GATE 3 regardless of how fast compute runs. This is the single highest-leverage thing Carter can start that doesn't wait on the recovery.
- **GATE 2 (dev-10) can fire as soon as GATE 1.5 + GATE 1 clear** — it does **not** need GATE 0 (internal compute, no egress). So the moment the cohort lands and CDR/cost are confirmed, the dev-10 rigor fire is unblocked even while the GATE 0 ruling is pending.

## Open decisions for Carter (from WAVE-2-PLAN §5, still open)

1. **[HARD] GATE 0 egress classification ruling** — in hand? If not, **file before any LD spend**. The egress argument is framed (each LD entry computed from all n≥60k AFR / n≥130k EUR → clears the ≥20-person floor); the *written ruling* is the gate. **← start this in parallel with the recovery.**
2. **Cost ceiling / credit balance** — confirm ~1,117 cluster-h fits AoU credits + set a cap (spec R3).
3. **Cluster preset** — 256 vs 384 vCPU (Gate C ran 24×n2-standard-16 = 384; preset already decided "MAX to quota, no overthreading, executor.cores=1").
4. **Export MAF** — keep 0.005 (recommended, preserves AFR rare-allele signal) or revert to spec's 0.01.
5. **Self-ID escalation** — pre-bless the auto-escalate (dev-10 self-ID-vs-PCA LD r < 0.995 → full genome-wide self-ID fire) or require a manual checkpoint. **(Now directly relevant — the self-ID cohort is the one being recovered; D-M3-07 decides whether it stays sensitivity-only or escalates.)**
6. **CDR pin** — confirm v8 stable (the recovery is v8/R8-matched; keep it pinned).

## Code-readiness (all NCSU-side fixes already landed — no action)
- HIGH-1 `to_numpy()` driver-OOM span-veto routing — FIXED `c6c32b3` (would have crashed the *first* dev-10 region).
- HIGH-3 xlarge-radius → 50-Mb-banded LD — accepted + documented `c11949e` (downstream SuSiE-RSS must treat the 16 xlarge cells as banded).
- MED-4 `.bm` populated-validation / MED-5 sidecar-upload-raise / MED-6 idempotency-byte-floor — FIXED `c11949e`; A.2/A.3 coverage tests added.

## Sequencing recommendation (when recovery lands)
1. Promote AFR-sens → 3-row `cohort_summary_m3.tsv` (closes GATE 1.5). *(draft row staged — see `cohort_summary_m3.DRAFT-3row.tsv`)*
2. **In parallel, not after:** Carter confirms/files GATE 0 (egress ruling), confirms cost/credit + CDR pin (GATE 1). GATE 0 has the longest external SLA → start first.
3. dev-10 LD fire (GATE 2) as soon as 1.5 + 1 clear (does not wait on GATE 0).
4. Durable atomic-final-write fix via `/gsd-plan-phase --gaps` (design staged — `DURABLE-FIX-DESIGN-atomic-final-write.md`) — slot before GATE 3 production so the 322-cell fire writes under the hardened contract.

## Working-tree note (already tracked, not Wave-2-blocking)
WAVE-2-PLAN §6 already records the 54 tracked-file deletions: the 5 Wave-2-critical configs were restored; ~54 m1/m2 envs + pathway configs + legacy docs remain deleted, recoverable from HEAD. **Still undecided: intentional cleanup (commit) vs accidental (`git checkout -- envs docs config`).** Confirmed unchanged at this session's start — not a new event.
