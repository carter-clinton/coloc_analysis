# m3-W2 Re-scope Lever Analysis — can the AFR+EUR LD panel hit a ~$1k cap?

**Date:** 2026-06-23 · **Trigger:** Carter set the production cap at **~$1k ≈ 1,000 cluster-h** and
authorized a pure-NCSU re-scope investigation (no spend). **Inputs:** the v2 measured AFR A.3 rate
(3.0173 blk/min) + the FULL 552-cell preflight + the `redo_ld_cost_model.py` formulas. **TL;DR: at
genome-wide AFR+EUR scope and a defensible LD band, ~$1k is not reachable by tuning — the realistic
gap is 2–8×. This is a scope/budget/method decision, not a parameter tweak.**

## 1. Official gate at the real cap
PROJECTED = **34,207 cluster-h** (×1.3 = **44,469**) vs **cap 1,000** → **RED** (~44× over).

## 2. Where the cost lives (so we know what a lever must move)
- **AFR 47.9% / EUR 52.1%** (EUR's 3.01 sample-ratio scaling ≈ offsets its smaller block counts).
- **By class: large 53.7% (56 cells) · medium 45.4% (406 cells) · small 0.9%.**
- **Broadly distributed** — the top single parent region is only ~4%. There is **no "drop a few
  regions" win**; the cost is spread across hundreds of cells.

## 3. The levers, quantified

### (a) Finer-split — NOT a total-cost lever (corrects the model's "YELLOW-finer-split" label)
The block formula is `est_block_count = (ceil(n_var/4096))²/2 × band_frac`, `band_frac = min(2·buffer/span, 1)`.
With ~uniform density, banded blocks per cell ≈ `ρ²·B·(span+2B)/4096²`, so a region of total span S split
into k banded cells totals `≈ ρ²·B/4096²·(S + 2B·k)` — **rising in k**. Each split **replicates the
2·buffer band overlap**, so splitting an already-banded cell *increases* total cost. Splitting is a
**per-cell tractability requirement** (keep each cell ≤150 blocks / ≤10 GiB so it runs in one wall window —
e.g. the HLA `region_00145__sub19` at 158 blocks **must** split to run), **not** a way to lower the total.
The one place splitting helps is converting an un-split **full-band** large region (band_frac≈1, dense)
down to banded sub-cells — but that is a one-time dense→banded step, after which further splitting hurts.

### (b) Band width (buffer) — real, ~linear, but bounded by the science
Total cost ≈ ∝ buffer. Even an aggressive narrowing **destroys the panel's purpose** before it reaches the cap:
| buffer AFR/EUR (Mb) | cluster-h | ×1.3 |
|---|---|---|
| 3 / 5 (locked) | 34,197 | 44,456 |
| 2 / 3 | 21,858 | 28,416 |
| 1.5 / 2.5 | 17,351 | 22,556 |
| 1 / 1.5 | 11,008 | 14,311 |
| 0.5 / 1 (sub-LD-decay; not defensible) | 6,430 | 8,359 |

Band width alone cannot reach 1,000 without dropping below the LD-decay scale the panel exists to capture.

### (c) Cluster size / utilization (npm) — the biggest *arithmetic* lever, but validity is unconfirmed
The model bills `npm = workers+1 = 25` nodes × wall-time **per cell** (the measured per-cell cost was
**24 cluster-h = 57 min × 25 nodes**, empirical). If a cell truly needs fewer nodes, the real cost scales down:
| npm (nodes/cell) | cluster-h | ×1.3 |
|---|---|---|
| 25 (probe size) | 34,197 | 44,456 |
| 9 | 12,311 | 16,004 |
| 5 | 6,839 | 8,891 |
| 3 (master + 2) | 4,104 | 5,335 |

**But this only pays off if the A.3 stage is NOT compute-distributed.** The probe evidence cuts the
other way: Stage 6 "held at 0/168 **with CPU active**, then committed in a burst" — i.e. most of the 57
min was the **distributed `row_correlation` matmul across the workers**, with a short final write. If the
workers are genuinely doing the compute, shrinking the cluster ~proportionally slows each cell and
**node-hours stay ~constant** → npm is largely *not* a free lever.

## 4. Stacked best case still misses ~$1k
Even the optimistic stack (npm=3 **and** buffer 1.5/2.5 Mb) ≈ **2,348 cluster-h (×1.3 = 3,052)** — still
~3× over. The lever product is bounded: npm 25→3 (~8×) × band 5/3→2.5/1.5 (~2×) ≈ 16×; 34k/16 ≈ 2.1k.
Reaching 1,000 needs ~34×, so **levers alone cannot get there** — a **scope cut is required**:
- **AFR-only** (defer/drop EUR) ≈ −52% → ~16k baseline; stacked with the optimistic sizing+band → ~$1.5k (borderline).
- **Candidate/GWAS-hit regions** instead of genome-wide → linear in #regions retained.
- **A cheaper LD method** than Hail A.3 BlockMatrix, or the documented 1000G reference fallback (smoke-net only today).

## 5. The one cheap measurement that bounds the answer
The whole 2× vs 8× spread hinges on **how many workers an A.3 cell actually utilizes**. Resolve it with a
**~$3–5 confirmatory probe** (no scope risk): re-run the *already-verified* cell `m2_region_00040__sub00`
on a **minimal cluster (master + 2–4 workers)** and measure whether `blocks_per_min` **holds (~3, write-
bound → npm small → scope-reduced panel ≈ affordable)** or **collapses ∝ workers (compute-distributed →
npm~24 → genome-wide at $1k infeasible)**. Pair it (free, NCSU) with regenerating the production manifest
so all over-threshold large regions are split into tractable banded sub-cells (needed for m3-04 regardless).

## 6. Recommendation
1. **Carter decides scope/budget** — the genome-wide AFR+EUR panel at a real LD band is a **~$15–35k compute
   item**, not ~$1k. The honest options: raise the cap, cut scope (AFR-only / candidate regions), narrow the
   band (scientific cost), or change method/reference.
2. **Then the ~$5 sizing probe** to confirm whether a small cluster holds the rate — it sets the production
   cluster design and tells us if a scope-reduced panel lands near the cap.
3. m3-04 stays BLOCKED on this plus the correctness preconditions (P1 densify, P2 resume guard, HLA split).
