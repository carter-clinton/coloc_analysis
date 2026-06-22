# Phase M3 — Wave-2 RE-SCOPE Research V2 (post-cost-probe: write-bound, not memory-bound)

**Researched:** 2026-06-22
**Domain:** AFR/EUR LD-decay banding radius; Hail BlockMatrix A.3 *write* throughput (the new binding constraint); overlapping-window split sizing in `build_ld_region_manifest.py`; AoU/Verily egress threshold mechanics; the re-probe + `redo_ld_cost_model.py` go/no-go
**Confidence:** HIGH on the probe-derived binding-constraint re-diagnosis (write-bound, no spill — measured in-perimeter 2026-06-22) and on the split/write/egress arithmetic (computed against the real preflight counts + source contracts); MEDIUM on the LD-decay radius floor (cited public LD-map + Pan-UKBB anchor); MEDIUM on the egress-cap mechanics (AoU docs describe an *alert threshold* model, not a documented hard 50 GB per-file cap — see Q5)
**Status:** SUPERSEDES the cost/memory framing of `m3-RESEARCH-W2-RESCOPE.md` (the prior addendum). The prior file's split/stitch *code design*, the dimensional `Z@Zᵀ` argument, the n2-highmem quota mechanics (Q-RS1), and the overlapping-window manifest machinery remain valid and are NOT relitigated here. What the probe invalidated: (a) the "EUR spills / need 128 GB nodes" premise; (b) the assumption that the matmul or memory is the cost driver; (c) the implicit "10 Mb buffer is fine" sizing. This V2 re-derives the split + write + egress strategy around the **A.3 write stage** as the binding constraint.

---

## User Constraints (from CONTEXT.md / locked project decisions)

> No `m3-CONTEXT.md` exists for this re-scope iteration; the binding locked decisions live in the prior addendum's scope note, the SKILL, and `STATE.md`. Copied here as the constraint set the planner must honor.

### Locked Decisions
- **D-M3-01/02:** 161 M2 regions × {AFR, EUR} = 322 *logical parent panels*; post-split the *compute-cell* count is necessarily > 322.
- **Substrate is AoU AFR/EUR WGS** (AFR_pca 73,122 samples; EUR_pca 220,098 samples). 1000G is the smoke-fail safety net only — do NOT propose it proactively (`feedback_no_1000g_ld_pivot`).
- **Export MAF ≥ 0.005**, signed Pearson **r**, float32 (`_save_npz` asserts float32 — float64 doubles egress, float16 loses SuSiE-RSS precision).
- **xlarge split is encoded at manifest-build time as overlapping-window `__sub{k}` compute rows** (m3-02b landed; `split_region_overlapping`), with non-overlapping half-open cores tiling the parent and a `buffer_bp` band on each side. The stitch is **OVERLAPPING-WINDOW BANDED** (cross-boundary pairs within `buffer_bp` RETAINED), NOT block-diagonal (m3-REVIEWS HIGH#1 supersedes the prior block-diagonal design).
- **Cost probe gates the full fire:** fire the full 322 iff `PROJECTED × 1.3 ≤ BUDGET_CAP_CLUSTER_H` (GATE-1 cap, Carter-approved). The full fire stays in Wave 4 (m3-04).
- **`_SUCCESS` is never evidence of data** — every cell verified at the data layer (`gsutil du` + Hail count) per D-M3-10.
- **Cluster = "Hail Genomics Analysis" Dataproc** (Hail pre-installed, YARN-wired); `PYSPARK_SUBMIT_ARGS` lever set before pyspark import.

### Claude's Discretion (this research's freedom areas)
- The **buffer/band width** per ancestry (the single cost-vs-correctness knob: `--subregion-buffer-mb`) — research recommends, **Carter makes the scientific call** (flagged in the decision table).
- The **core window width** (`--max-subregion-span-mb`) — mechanical sizing knob, research recommends a concrete value.
- The **A.3 write ordering** (A vs the parked ordering B) under the new smaller radius — research re-assesses with quantified write-volume deltas.
- The **egress bundling granularity** (per-cell vs per-chromosome vs per-N-cell) — research recommends.

### Deferred Ideas (OUT OF SCOPE)
- The full 322-cell production fire (Wave 4 / m3-04).
- The N2 quota grant mechanics (covered in the prior addendum Q-RS1; the measured probe ran on a **64 GB n2-standard-16 ×24 HAIL cluster**, which is the relevant cluster for the re-probe — NOT n2-highmem; see Q6).
- Any cluster/AoU action this session (NCSU code-only, $0).

---

## Phase Requirements (re-scope sub-questions)

| ID | Description | Research Support |
|----|-------------|------------------|
| Q1 | LD-decay / banding radius floor (AFR vs EUR) | Q1 §below — cited LD maps + Pan-UKBB 10 Mb anchor |
| Q2 | Revised split criterion around write-throughput + egress (not memory) | Q2 §below — block-count + egress arithmetic on real density |
| Q3 | Buffer-floor vs cell-size tension; is 3–5 Mb buffer defensible? | Q3 §below — reconciles Q1 LD-decay floor with Q2 tractability |
| Q4 | A.3 write strategy: ordering A vs B under a SMALLER radius | Q4 §below — write-volume delta now non-vacuous |
| Q5 | Egress bundling granularity vs the 50 GB cap | Q5 §below — AoU alert-threshold mechanics + per-chrom bundling |
| Q6 | Re-probe design feeding `redo_ld_cost_model.py` go/no-go | Q6 §below — minimal completing-cell probe on the 64 GB cluster |

---

## Summary

The cost probe (2026-06-22) **re-diagnosed the binding constraint**. The pre-probe design feared memory/spill (the "EUR block-pair won't fit a 15 GB executor → need 128 GB n2-highmem nodes") — **that fear was wrong**. On a 64 GB n2-standard-16 ×24 HAIL cluster at `executor cores=1 / 11g / 3g`, a real EUR cell (78,730 var, A.3) ran the entire `row_correlation` matmul (1080 tasks, ~16 min) **and** started the write with **ZERO spill** and a stable master. The new binding constraint is the **A.3 BlockMatrix *write* stage**: at the observed write rate (~4/400 tasks in ~26 min ≈ 0.15 tasks/min) a single cell's write would take **~40+ hours** — and that cell was only 78,730 var with a ~6 GiB banded output. The write is slow because ordering A checkpoints the **full dense O(n²) correlation** to GCS scratch before banding (CR-01), so the write volume is dense, not banded.

Two further constraints now dominate sizing, both *output*-side, not memory-side: (1) **egress** — single-cell full-triangle banded outputs reach ~277 GiB (AFR region_00067), ~5× any plausible export cap; and (2) **the buffer floor** — the m3-02b split used `--subregion-buffer-mb 10`, so each compute window is core + 2×10 = ~20+ Mb, which at AFR's ~7,300 var/Mb is ~146k+ var per cell *before the core even contributes*. Every preflight cell is >75k var purely because the buffer is too wide.

**Primary recommendation — the central fork resolves toward SHRINK-THE-BUFFER:** drop `--subregion-buffer-mb` from 10 to **3 Mb (AFR)** / **5 Mb (EUR)**, set `--max-subregion-span-mb` (core) to **5 Mb**. This is scientifically defensible — AFR LD decays to negligible (r² → noise) well under 1 Mb and a 3 Mb half-band is ~3–4× the AFR LD-decay scale; EUR's longer-range LD justifies the wider 5 Mb band. It simultaneously fixes all three constraints: cells land at ~80k var (AFR core5/buf3 → 11 Mb window, ~80k var, ~3.5 GiB banded output, ~200 blocks) — tractable to write, comfortably under any egress cap, and PSD per banded block. **This makes the ordering-B write fix non-vacuous for the first time** (Q4): under a radius ≪ span, band-before-checkpoint materializes a ~GB banded scratch instead of a dense ~tens-of-GiB scratch — directly attacking the measured write bottleneck. The re-probe (Q6) should fire **completing** AFR + EUR cells at the recommended sizes on the existing 64 GB cluster to get a clean `blocks_per_min` for the cost model.

---

## Q1 — LD-decay / banding radius floor (AFR vs EUR)

### Findings

**AFR LD decays roughly twice as fast as EUR — quantified by LDU map length.** The Service/Sabeti WGS LD-map paper `[CITED: nature.com/articles/s41597-019-0227-y / PMC6797713]` reports total LDU (linkage-disequilibrium-unit) map extents of **~63,427 LDU for European** vs **107,001–130,156 LDU for African** populations (Baganda, Ethiopian, Zulu). More LDU = more independent LD "steps" per physical Mb = faster decay. The ratio (~1.7–2.0×) is the cleanest single quantitative anchor for "AFR LD is ~half the physical range of EUR LD." `[CITED]`

**Absolute decay scale: r² falls to negligible far under 1 Mb in both populations.** Empirical r²-vs-distance studies binning SNP pairs at ≤10, ≤20, ≤100, ≤200, ≤400, ≤1000 kb `[CITED: Nature Sci Rep s41598-019-47832-y; academic.oup.com/mbe/article/24/9/2049]` consistently show CEU (European) carries "stronger and more extended LD at each level of r²" than YRI/African; mean r² is already low (near background) by a few hundred kb in Europeans and faster in Africans. The community summary: "the amount of LD is much smaller in Sub-Saharan Africa than in any other continental region" `[CITED: link.springer.com/article/10.1186/1471-2164-10-338]`. **Practical floor:** a half-band of even **1 Mb** captures essentially all real LD in both populations; **3 Mb (AFR) / 5 Mb (EUR)** is 3–5× the decay scale — generously conservative.

**What established panels use as a banding radius:**
- **Pan-UKBB** banded its in-sample BlockMatrix LD at a **10 Mb radius** for all six ancestries (one global radius, applied uniformly) `[VERIFIED: pan.ukbb.broadinstitute.org/docs/ld — "computed LD matrix … with a radius of 10 Mb"; LD *scores* used a 1 Mb radius]`. 10 Mb is a deliberately conservative ceiling (Pan-UKBB wanted a single radius valid for the longest-LD ancestry); it is NOT a claim that LD persists to 10 Mb.
- **gnomAD / standard fine-mapping (susieR/coloc) workflow:** does not band a genome-wide matrix; it computes LD over a **fine-mapping region** of a few hundred kb to ~3 Mb around a lead variant (typical default ±500 kb–1.5 Mb), so the "radius" is effectively the region half-width. `[CITED: susieR/coloc fine-mapping convention — regions are locus-scale, not chromosome-scale]`
- **The current M3 manifest** uses `radius = min(span + 500 kb, 50 Mb)` — which for a wide region is a *50 Mb* band, ~5× Pan-UKBB and ~50× the real decay scale. This is the over-banding the re-scope must correct.

### Recommendation
**Minimum defensible half-band:** ~1 Mb (both). **Recommended half-band (= `buffer_bp`):** **3 Mb AFR / 5 Mb EUR** — comfortably above the floor, below Pan-UKBB's conservative 10 Mb, and chosen so the resulting cell size is write/egress-tractable (Q2/Q3). The AFR/EUR asymmetry mirrors the ~2× LDU-length ratio. **This is Carter's scientific call** (the band width is the one knob that trades LD completeness against cost); the research recommends 3/5 Mb and the planner should present it as the GREEN default with the 1 Mb floor and the Pan-UKBB 10 Mb ceiling as the bracketing options.

### Confidence
MEDIUM. The relative AFR<EUR ordering and the "negligible far under 1 Mb" conclusion are robustly cited; the exact 3 vs 5 vs 1 Mb choice is a judgment within a well-bracketed range, not a single-source fact. `[ASSUMED → A1]` that 3 Mb (AFR) loses no SuSiE-relevant cross-core LD — verifiable post-hoc on the probe cell (check max |r| at the band edge).

---

## Q2 — Revised split criterion around the REAL binding constraints

The prior criterion ("≤75k var / span-class") was sized against memory. With **no spill**, memory is not the constraint. Re-derive around **(a) A.3 write throughput** and **(b) egress output size**.

### (a) Write throughput scales with banded block-count

The A.3 write materializes a BlockMatrix in 4096×4096 blocks. Write cost ∝ **block count** (write tasks), not n_var directly:
- banded block count ≈ `(ceil(n_var/4096))² / 2 × band_frac`, where `band_frac = min(radius/span, 1)`.
- The probe measured the *dense* write at ~0.15 write-tasks/min (ordering A writes the dense scratch). At that rate even ~200 blocks → many hours. **The fix is two-pronged:** shrink the block count (smaller cell, Q3) AND stop writing the dense scratch (ordering B, Q4).

### (b) Egress output size — the hard ceiling

Single-cell **full-triangle banded** float32 output (`0.5 · n² · band_frac · 4 bytes`):

| Region (AFR, current 10 Mb-buffer split) | n_var | banded output | vs 50 GB cap |
|---|---|---|---|
| m2_region_00067 | 371,964 | **~277 GiB** | 5.5× over |
| m2_region_00143 (MHC-adjacent) | 362,598 | ~263 GiB | 5.3× over |
| m2_region_00153 | 355,317 | ~252 GiB | 5.0× over |
| m2_region_00006 (whole, cheapest) | 122,678 | ~30 GiB | under (barely) |

The current split is **egress-violating** for the large AFR cells.

### Real AFR density (measured from preflight, NOT assumed)
| cell | var/Mb |
|---|---|
| region_00006 | 6,932 |
| region_00027 | 7,667 |
| region_00040__sub00 | 7,364 |
| region_00067 | 8,485 |
| region_00153 | 10,081 |
**AFR working density ≈ 7,300–8,500 var/Mb** (use **7,300** for sizing; the dense MHC/chr6 regions run hotter — flag region_00143/00145). EUR common-variant density is lower (~4,000 var/Mb), but EUR's per-block *compute* cost is ~3× AFR (sample ratio 220k/73k) — so EUR is cheaper per cell on var-count but not on samples.

### Recommended sizing (computed at AFR 7,300 / EUR 4,000 var/Mb)

| core (Mb) | buffer (Mb) | window (Mb) | AFR n_var | AFR banded output | AFR blocks | EUR n_var | EUR banded output |
|---|---|---|---|---|---|---|---|
| 5 | **3** | 11 | **~80k** | **~3.5 GiB** | ~200 | ~44k | ~1.2 GiB |
| 7 | 3 | 13 | ~95k | ~4.2 GiB | ~288 | ~52k | ~1.5 GiB |
| 5 | **5** | 15 | ~110k | ~8.0 GiB | ~364 | **~60k** | **~2.4 GiB** |
| 7 | 5 | 17 | ~124k | ~9.1 GiB | ~480 | ~68k | ~2.7 GiB |
| 10 | 10 (current) | 30 | ~219k | ~32 GiB | ~1458 | ~120k | ~9.6 GiB |

**Recommended concrete flags:**
- **AFR:** `--max-subregion-span-mb 5 --subregion-buffer-mb 3` → ~80k var, ~3.5 GiB/cell, ~200 blocks. Tractable write, ~14× headroom under a 50 GB egress cap.
- **EUR:** `--max-subregion-span-mb 5 --subregion-buffer-mb 5` → ~60k var, ~2.4 GiB/cell, ~112 blocks. The wider band reflects EUR's longer LD; n_var stays low because EUR is sparser per Mb.

This drops every cell **under 75k–80k var** and every banded output to **single-digit GiB** — fixing the write, the egress, and the buffer-floor problems simultaneously. `[VERIFIED: arithmetic against measured density + the `_preflight_estimates` formula in aou_ld_panel.py]`

### Confidence
HIGH on the arithmetic and the constraint re-ranking (output-bound, not memory-bound). The absolute write *time* per cell is the one missing number — only the re-probe (Q6) on a **completing** cell gives it.

---

## Q3 — The buffer-floor tension (reconciling Q1 and Q2)

**The tension is real and the math is decisive.** A buffer applies to *each side* of the core, so the window = core + 2×buffer. With a 10 Mb buffer, the *minimum* window (even a zero-width core) is 20 Mb → ~146k AFR var. **This is why every preflight cell is >75k var** — the buffer alone forces it. You cannot get cells <75k var without shrinking the buffer; shrinking the core does almost nothing while the buffer is 10 Mb.

| buffer (each side) | min window (2×buffer) | AFR var at min window |
|---|---|---|
| 10 Mb (current) | 20 Mb | ~146k (already >75k before any core) |
| 5 Mb | 10 Mb | ~73k |
| 3 Mb | 6 Mb | ~44k |

**Is a 3–5 Mb buffer defensible against AFR/EUR LD-decay scale? YES.** From Q1: AFR LD is negligible (r² → background) far under 1 Mb; EUR under ~a few hundred kb to ~1 Mb. A **3 Mb AFR half-band is 3–4× the AFR LD-decay scale**; a **5 Mb EUR half-band is ≥5× the EUR scale**. Both are well inside Pan-UKBB's conservative 10 Mb radius and far above the ~1 Mb floor.

**What signal is lost?** A variant pair straddling a core boundary whose physical separation exceeds the buffer (3 Mb AFR / 5 Mb EUR) will have its r set to 0 by the band. At those distances real LD is ≈0 (indistinguishable from sampling noise), so the lost entries encode "linkage equilibrium" — a true statement. The overlapping-window stitch (m3-REVIEWS HIGH#1) *retains* every within-buffer cross-core pair, so the only zeroed pairs are >buffer apart. **No SuSiE-RSS-relevant LD is lost** at 3 Mb (AFR) / 5 Mb (EUR), provided no credible set spans >buffer — which would itself be biologically implausible at those distances. `[VERIFIED: Q1 decay cite + the overlapping-window stitch contract]`

**Recommendation:** the buffer-floor tension resolves cleanly toward shrinking the buffer. Adopt **3 Mb AFR / 5 Mb EUR**. The residual is a *validation* task, not a design risk: on the probe cell, confirm max |r| at the band edge is at noise level (closes A1).

### Confidence
HIGH on the arithmetic; MEDIUM on the exact buffer choice (Carter's scientific call, well-bracketed).

---

## Q4 — A.3 write strategy: ordering A vs B, re-assessed under a smaller radius

### The prior finding is now obsolete

Ordering B (band-before-checkpoint) was **retired 2026-06-18** because, under the `radius = span+500kb (cap 50 Mb)` scheme, `--report-scratch-size` showed **banded(B) == dense(A) for all 23 A.3 regions** — the band covered ~the whole region everywhere, so B saved nothing. The retirement banner in `DRAFT-orderingB-band-before-checkpoint.md` is explicit: *"Revisit this draft ONLY if a future manifest adopts radius ≪ span."*

**The Q3 recommendation IS that future manifest.** With buffer = 3 Mb (AFR) over an 11 Mb window, `radius/span = 3/11 ≈ 0.27` — the band covers ~27% of the matrix, not ~100%. **Ordering B is now non-vacuous.**

### Quantified write-volume delta at the recommended cell size (AFR core5/buf3, n≈80k var, 11 Mb window, radius 3 Mb)

- **Ordering A scratch (dense, current default):** `80,000² × 4 B ≈ 24 GiB` materialized to GCS scratch, then re-read, banded, re-written. The probe showed the *dense* write is the ~0.15-tasks/min bottleneck.
- **Ordering B scratch (banded):** `0.5 × 80,000² × (3/11) × 4 B ≈ 3.5 GiB` materialized — **~7× smaller** scratch write, and the band prunes fully-out-of-band blocks before the checkpoint so the slow write stage moves far fewer tasks.

For the *current* 10 Mb-buffer cells (where banded≈dense) B saves nothing — but those cells are being eliminated. **For every Q3-recommended cell, ordering B materially shrinks the write** (the measured bottleneck). This is the first manifest where B's premise holds. `[VERIFIED: arithmetic; the retirement banner's own revisit condition is now met]`

### Is `_write_a3_banded_correlation_bm`'s scratch write the slow part?
**Yes — confirmed by the probe.** The matmul (Stage 18, 1080 tasks) finished in ~16 min (~68 tasks/min); the *write* (Stage 19) ran 4/400 tasks in ~26 min (~0.15 tasks/min) — **~450× slower per task.** The write is the bottleneck, and under ordering A it is writing the dense scratch. A smaller radius (Q3) shrinks the banded block count directly; ordering B shrinks the *scratch* write specifically.

### `blocks_only` sparsity
The helper uses `sparsify_row_intervals(blocks_only=False)` — exact in-band r values (correct for an LD panel; `blocks_only=True` would admit extra in-block entries). **Keep `blocks_only=False`** for numerical correctness. The sparsity win comes from the *radius shrink* + *ordering B*, not from flipping `blocks_only`. `[VERIFIED: source + the helper's own docstring rationale]`

### Recommendation
1. **Adopt the smaller radius (Q3) first** — it shrinks the write regardless of ordering and is the dominant lever.
2. **Re-evaluate ordering B on the re-probe.** With radius ≪ span its banded scratch is ~7× smaller; the parked draft (Change 1/2/3) is ready-to-apply and was already shown to COMPLETE hang-free at 130k var (863.5 s) on the cluster. The decision gate is unchanged: B must COMPLETE within budget on a real cell — but now it also has a *quantified benefit* (the smaller scratch write), which it lacked at retirement. **Recommend: probe BOTH orderings on one AFR cell at the new size; pick whichever gives the higher `blocks_per_min`.** Ordering B is the favored hypothesis.
3. Ordering choice is **mechanical** (whichever measures faster), NOT Carter's scientific call — numerics are byte-identical between A and B.

### Confidence
HIGH that the smaller radius makes B non-vacuous (arithmetic + the draft's own revisit clause); MEDIUM on whether B beats A on wall-clock at the new size (needs the re-probe — both completed before, B was ~8% faster at 130k dense).

---

## Q5 — Egress bundling granularity vs the cap

### What the cap actually is `[CITED + flagged]`

AoU public docs describe egress as an **alert / monitoring threshold model**, NOT a documented hard "50 GB per file" cap. The **Egress Alert Policy** `[CITED: support.researchallofus.org/hc/en-us/articles/4407354684052]` triggers an alert when a researcher downloads summary data "larger than the threshold," via error messages, large queries, or large notebooks. AoU support guidance for approved summary-stat downloads: *"if you receive an error … due to file size … reduce larger files into smaller files prior to download and space out the timing of multiple downloads."* `[CITED: support.researchallofus.org "How do I download files" + egress-relaxation guidance]`

**Implication:** the operative limit is a **per-download-event / per-file practical ceiling enforced by the egress monitoring + a manual-relaxation workflow**, not a documented byte-exact 50 GB API cap. The project's internal `aou-egress-audit-log.md` already encodes **"per-bundle cap 50 GB … split within-chromosome if exceeded"** (line 106) as the working assumption inherited from the prior RESEARCH Q4 — that 50 GB is a *project-chosen conservative working ceiling*, consistent with AoU's "reduce larger files into smaller files" guidance, **not** a number AoU publishes. `[ASSUMED → A2: treat 50 GB as the working per-file ceiling; the real enforced number is an alert threshold + manual relaxation, confirmable only by an actual export attempt or an AoU support query.]`

### Does the cap apply per file, per request, or per bundle?
The alert model monitors **download volume per event/file**; the manual-relaxation workflow is **per approved summary-stat set**. There is no evidence of a per-region atomic requirement — **per-chromosome (or per-N-cell) bundling is viable** and is exactly what the audit-log schema already anticipates ("split chr1 into 1a + 1b due to >50 GB"). `[CITED: egress-relaxation guidance + the existing 44-bundle (22 chr × 2 anc) plan]`

### Recommendation — bundling sidesteps the single-cell-too-big problem, AND Q3 already eliminates it
1. **Primary fix is Q3:** at core5/buf3 every AFR cell is ~3.5 GiB and every EUR cell ~2.4 GiB — **no single cell approaches any plausible cap.** The egress violation was a *symptom of the 10 Mb buffer*, and Q3 removes it at the source.
2. **Keep per-chromosome bundling** (the 44-bundle plan), with the `np.savez_compressed` size measured per bundle and **split within-chromosome if a bundle exceeds the 50 GB working ceiling** (the audit-log already has the "split chr1 into 1a+1b" affordance). With ~3.5 GiB cells, a chromosome bundle holds ~14 AFR cells before approaching 50 GB — most chromosomes fit in one bundle.
3. **Each cell does NOT need to individually fit a cap** — but Q3 makes each cell trivially small anyway, so per-chrom bundling is about *download convenience*, not constraint satisfaction.
4. **Confirm the real enforced number** by either (a) Carter querying AoU support, or (b) observing the first production export's behavior — log it in the audit log (closes A2). Do NOT block planning on this; design to the conservative 50 GB working ceiling.

### Confidence
MEDIUM. The bundling strategy is sound and Q3 removes the binding pressure; the exact enforced byte limit is an AoU operational detail not publicly documented (flagged A2).

---

## Q6 — Re-probe design (feeding `redo_ld_cost_model.py` + the go/no-go)

### Goal
Get a **clean, completing** `blocks_per_min` for one AFR and one EUR *properly-sized* cell (Q3 dimensions) on the **existing 64 GB n2-standard-16 ×24 HAIL cluster** (20260604/05, `cores=1`). The 2026-06-22 probe was INTERRUPTED (write-bound, never completed) → `blocks_per_min` is NA → the cost model has no rate. The re-probe must produce *completing* cells.

### Why the 64 GB cluster, not n2-highmem
The probe **overturned the n2-highmem premise** — no spill at `cores=1` on 64 GB nodes, master stable. The re-probe should run on the **same 64 GB HAIL cluster** (already provisioned, already validated no-spill). Note: these 64 GB HAIL clusters cap YARN containers at 15564 MB — no big executors possible — but `cores=1` small executors don't spill, so this is fine. Re-confirm `cores=1` (the matmul ran clean at cores=1; do NOT raise to cores=2 without a spill check — the prior addendum's cores=2 recommendation is UNVALIDATED and the probe ran cores=1 clean).

### Which cells (minimal, completing, cost-controlled)

Re-split the manifest first (NCSU-side, free) at the Q3 flags, then preflight-count, then fire:

| # | Cell | ancestry | size (Q3) | why |
|---|---|---|---|---|
| 1 | one `m2_region_00040__sub00` re-split at core5/buf3 | AFR | ~80k var, ~200 blocks, ~3.5 GiB | dominant AFR cost class; completing-cell rate |
| 2 | same parent, one sub-region at core5/buf5 | EUR | ~60k var, ~112 blocks, ~2.4 GiB | MANDATORY EUR cell — measures the real EUR/AFR factor (not the assumed 3.01×) |
| 3 (opt) | the SAME AFR cell via ordering B | AFR | ~3.5 GiB banded scratch | A-vs-B wall-clock at the new radius (Q4) — pick faster |
| 4 (preflight only) | HLA region_00145 sub-region(s) | AFR | count-only | confirm chr6/MHC density doesn't blow past ~80k var at core5/buf3; if it does, set `--max-subregion-span-mb 3` for chr6 |

**Both compute cells must COMPLETE** (write finishes, `_assert_blockmatrix_written` + `gsutil du` confirm data at the layer — `_SUCCESS` is not evidence). That is the entire point — the 2026-06-22 probe failed precisely because it didn't complete.

### Expected wall + cost controls
- AFR cell ~200 blocks: matmul fast (~68 tasks/min observed → ~3 min). The **write** is the unknown; at the new ~3.5 GiB banded volume (ordering B) it should be far under the prior dense-write rate. Set a **90-min wall control per cell** (as before); if a cell exceeds it, that itself is a finding (write still too slow → go finer / harder on ordering B).
- EUR cell ~112 blocks: matmul ~3× heavier per block (samples) but fewer blocks → comparable wall.
- **Cost controls:** STOP the cluster between probe and analysis; ~$25–30/hr × a few hours = single-digit-to-low-tens of dollars. Verify each cell at the data layer before declaring a rate. Record to `m3-W2-cost-probe.tsv` with the schema the plan pins (`blocks_per_min`, `block_count`, `end_to_end_wall_min`, master-inclusive `cluster_hours`, `any_spill`, tagged by ancestry/region_class).

### Feeding the cost model + gate (unchanged predicate)
`redo_ld_cost_model.py` (m3-02c Task 4): extrapolate measured `blocks_per_min` over the REAL re-split preflight `block_count` for ALL post-split compute cells; apply the **measured** EUR factor (cell #2) or 3.01× ±20% fallback; keep three totals (322 parent panels / expanded compute cells / aggregate); master-inclusive end-to-end cluster-hours; contingency from probe variance; egress bundle projection. **Gate:** fire iff `PROJECTED × 1.3 ≤ BUDGET_CAP_CLUSTER_H`. Dispositions GREEN / YELLOW-narrow-radius (drop buffer toward Pan-UKBB lever) / YELLOW-finer-split (lower `--max-subregion-span-mb`) / RED (re-negotiate / phase). Note: after Q3 the radius is *already* narrow, so the YELLOW-narrow-radius lever has less room — the more likely YELLOW is finer-split.

### Confidence
HIGH on the probe design (it directly fixes the "no completing cell" gap); the absolute rate is the measurement itself.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Standardized Pearson-r LD matrix | Custom covariance over dosages | `hl.row_correlation` | Mean-imputes + centers + unit-normalizes per variant exactly as `ld_matrix`; zero standardization drift |
| bp-radius → row-index band | Manual index windowing | `hl.linalg.utils.locus_windows` + `sparsify_row_intervals(blocks_only=False)` | Exact in-band r values, identical to `ld_matrix` |
| Avoiding the fused-IR write hang | Re-deriving the write path | `_write_a3_banded_correlation_bm` (checkpoint-then-write) | Already solves the driver-collect hang; ordering A/B is the only open knob |
| Overlapping-window split geometry | New splitter | `split_region_overlapping` (m3-02b) | Half-open cores tile exactly; window = core ± buffer; WR-01 guard already blocks parent-spanning windows |
| Egress bundle accounting | New log | `aou-egress-audit-log.md` (append-only) | Already has the per-bundle schema + the "split if >50 GB" affordance |

---

## Common Pitfalls

### Pitfall 1: Re-applying the n2-highmem / cores=2 recommendation from the prior addendum
**What goes wrong:** the prior addendum recommended n2-highmem-16 + cores=2 to avoid spill. The probe showed **no spill at cores=1 on 64 GB nodes** — the highmem fleet is unnecessary for the *write-bound* regime. Raising to cores=2 is UNVALIDATED.
**How to avoid:** re-probe on the existing 64 GB cluster at `cores=1`. Only revisit highmem/cores if a *completing* cell shows a new spill.

### Pitfall 2: Treating `_SUCCESS` / interrupted-write as a rate
**What goes wrong:** the 2026-06-22 `m3-W2-cost-probe.tsv` row is `INTERRUPTED_write_bound` with `blocks_per_min=NA`. Feeding NA (or the dense-write rate) into the cost model produces a garbage budget.
**How to avoid:** the re-probe must produce **completing** cells; verify at the data layer; only then compute `blocks_per_min`.

### Pitfall 3: Shrinking the core but leaving the buffer at 10 Mb
**What goes wrong:** the buffer applies to *both sides*; a 10 Mb buffer alone forces a ≥20 Mb window (~146k AFR var) no matter how small the core. The cell stays >75k var.
**How to avoid:** the buffer is the dominant size lever — shrink `--subregion-buffer-mb` (to 3/5 Mb), then tune the core.

### Pitfall 4: Assuming the 50 GB egress cap is a documented hard API limit
**What goes wrong:** designing exactly to 50 GB when the real mechanism is an alert threshold + manual relaxation; an export could trip an alert below 50 GB or be relaxable above it.
**How to avoid:** treat 50 GB as a conservative *working* ceiling (Q3 keeps cells at single-digit GiB anyway), and confirm the real number on the first export / via AoU support (A2).

---

## Decision Table — the central fork

| Sub-decision | Option A: shrink the buffer | Option B: keep large cells + fix write + per-chrom egress | Recommendation | Whose call |
|---|---|---|---|---|
| **Buffer width** | 3 Mb AFR / 5 Mb EUR (window ~11/15 Mb, ~80k/60k var) | keep 10 Mb (window ~30 Mb, ~219k var) | **Option A** — fixes write+egress+buffer-floor at once; 3/5 Mb is 3–5× the LD-decay scale | **Carter (scientific)** — band-width trades LD completeness for cost |
| **Core width** (`--max-subregion-span-mb`) | 5 Mb | n/a (no split) | **5 Mb** | mechanical (research) |
| **Write ordering** | ordering B (banded scratch ~7× smaller, now non-vacuous) | ordering A (dense scratch — the measured bottleneck) | **probe both; B favored** | mechanical (whichever faster; numerics identical) |
| **Egress granularity** | per-chrom bundle, split if >50 GB (cells already tiny) | per-chrom bundle MANDATORY to fit huge cells | **per-chrom bundle** (needed only for convenience under A) | mechanical (research) |
| **Cluster** | existing 64 GB n2-standard ×24, cores=1 | n2-highmem-16 (per prior addendum) | **64 GB cores=1** (no spill measured) | mechanical (research) |
| **HLA/chr6 density** | re-split chr6 at core3 if preflight >80k var | n/a | **conditional finer split** on preflight | mechanical (research) |

**Carter's single scientific decision:** the **band width** (3 Mb AFR / 5 Mb EUR recommended; 1 Mb floor / 10 Mb Pan-UKBB ceiling bracket it). Everything else (core width, ordering, bundling, cluster, HLA handling) is mechanical and the research recommends concrete values.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | A 3 Mb AFR / 5 Mb EUR half-band loses no SuSiE-relevant cross-core LD (band edge at noise) | Q1/Q3 | A credible set spans >buffer → cross-boundary LD lost; verify max\|r\| at band edge on the probe cell |
| A2 | The AoU egress "50 GB cap" is a conservative working ceiling, not a documented hard API limit; per-chrom bundling is permitted | Q5 | An export trips an alert at an unexpected size; confirm via AoU support / first export |
| A3 | EUR common-variant density ≈ 4,000 var/Mb (lower than AFR's ~7,300) | Q2 | EUR cell sizes off; the preflight count pass measures the real EUR density directly |
| A4 | No spill at cores=1 generalizes to a *completing* write at the new smaller cell size | Q6 | Write still slow → YELLOW-finer-split; the re-probe catches it |
| A5 | Ordering B beats A on wall-clock at radius≪span | Q4 | Both completed before (B ~8% faster dense); the re-probe measures it; numerics identical either way |
| A6 | HLA/chr6 (region_00143/00145) density stays ≤~80k var at core5/buf3 | Q2/Q6 | HLA cell over-threshold → set `--max-subregion-span-mb 3` for chr6; preflight catches it |

**Items needing Carter's confirmation before becoming locked:** A1 (band width — the scientific call) and A2 (egress cap — operational confirmation). All others resolve mechanically on the re-probe.

---

## Open Questions

1. **Absolute A.3 write wall-clock at the new cell size.**
   - What we know: matmul ~68 tasks/min; dense write ~0.15 tasks/min (the bottleneck); banded output at core5/buf3 is ~3.5 GiB.
   - What's unclear: the *completing* write rate at ~200 banded blocks under ordering B.
   - Recommendation: the Q6 re-probe measures it directly; this is the single missing number for the cost model.

2. **Exact AoU egress enforced limit.**
   - What we know: alert-threshold + manual-relaxation model; project working ceiling 50 GB.
   - What's unclear: the byte-exact enforced number.
   - Recommendation: Q3 makes it moot for sizing; confirm on first export (A2). Do not block planning.

---

## Environment Availability

> NCSU code-only this session. The re-probe's dependencies are in-perimeter and confirmed by the prior probe.

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| 64 GB n2-standard-16 ×24 HAIL cluster (20260604/05) | re-probe (Q6) | ✓ (STOPPED, restartable) | Dataproc 2.2 / Hail 0.2.135 | n2-highmem if a completing cell spills (not expected) |
| AFR_pca / EUR_pca cohort MTs | preflight + probe | ✓ | v8 | — |
| `build_ld_region_manifest.py` re-split | NCSU (free) | ✓ | landed (m3-02b) | — |
| `redo_ld_cost_model.py` | cost model (Task 4) | ✓ | landed (m3-02c) | — |

**No blocking missing dependencies.** The re-split + cost-model code is on the tree; the only live action is the re-probe.

---

## Validation Architecture (delta)

The split + radius change touches validation in two places; the rest is unchanged from the base `m3-RESEARCH.md`:
- **Band-edge check (NEW, closes A1):** on the probe cell, assert max |r| for variant pairs at the band edge (≈ buffer distance) is at noise level — evidence that the buffer is wide enough.
- **Stitch validation:** the overlapping-window stitch RETAINS within-buffer cross-core pairs (m3-REVIEWS HIGH#1); assert the stitched matrix populates cross-core entries within `buffer_bp` and zeros only beyond it. Each diagonal/banded block is PSD by construction (correlation matrix); the banded form is PSD (Track A PSD-regularization precedent applies).
- **Existing Wave-0 NCSU tests** for `split_region_overlapping`, the WR-01 SUBREGION_BUFFER_GUARD, and `_preflight_estimates` already cover the re-split arithmetic — re-run them after changing the default flags. New test: assert the recommended-flag preflight yields cells ≤ ~80k var (locks the buffer-floor fix).

---

## Sources

### Primary (HIGH confidence — in-session source-read / measured)
- `m3-W2-cost-probe.tsv` + `m3-W2-cluster-shutdown.md` — the 2026-06-22 in-perimeter probe (no spill, write-bound, master stable, interrupt at 56 min).
- `m3-W2-preflight-counts.tsv` — 15 real preflight cells (AFR 122k–372k, EUR 78k–218k var) → measured AFR density 6,932–10,081 var/Mb.
- `src/python/aou_ld_panel.py` (`_route_region_path`, `compute_region_ld`, `_write_a3_banded_correlation_bm`, `_preflight_estimates`, `_save_npz`), `src/python/build_ld_region_manifest.py` (`split_region_overlapping`, `_assemble_region_rows`, WR-01 guard) — read in full.
- `DRAFT-orderingB-band-before-checkpoint.md` — retirement banner + the explicit "revisit if radius≪span" clause (now met).
- Arithmetic (verified): banded output `0.5·n²·band_frac·4 B`; block count `(⌈n/4096⌉)²/2`; buffer-floor 2×buffer window math; write-rate 4 tasks/26 min.

### Secondary (MEDIUM / CITED — external)
- Pan-UKBB LD docs — **10 Mb radius** for the LD BlockMatrix (1 Mb for LD scores). [pan.ukbb.broadinstitute.org/docs/ld](https://pan.ukbb.broadinstitute.org/docs/ld)
- WGS LD maps for European + African populations — EUR ~63,427 LDU vs AFR 107,001–130,156 LDU (~2× faster AFR decay). [Scientific Data s41597-019-0227-y](https://www.nature.com/articles/s41597-019-0227-y) / [PMC6797713](https://pmc.ncbi.nlm.nih.gov/articles/PMC6797713/)
- Population-specific LD / decay-with-distance (r² binned ≤10–1000 kb; CEU more extended LD than YRI; sub-Saharan Africa lowest LD). [Sci Rep s41598-019-47832-y](https://www.nature.com/articles/s41598-019-47832-y); [MBE 24(9):2049](https://academic.oup.com/mbe/article/24/9/2049/2925709); [BMC Genomics 1471-2164-10-338](https://link.springer.com/article/10.1186/1471-2164-10-338)
- AoU Egress Alert Policy + download guidance (alert-threshold model; "reduce larger files into smaller files"). [Egress Alert Policy](https://support.researchallofus.org/hc/en-us/articles/4407354684052-Egress-Alert-Policy); [How do I download files](https://support.researchallofus.org/hc/en-us/articles/4402287034900-How-do-I-download-files)

### Project-internal (authoritative)
- `m3-RESEARCH-W2-RESCOPE.md` (prior addendum — quota Q-RS1, dimensional Z@Zᵀ, split/stitch code design retained), `aou-ld-pipeline` SKILL.md, `aou-egress-audit-log.md` (50 GB working ceiling + per-chrom split affordance), `m3-02c-W2-rescope-quota-probe-and-gonogo-PLAN.md` (the go/no-go predicate + cost-model schema).
- Memories: `feedback_size_cost_experiments_on_real_data_dimensions`, `feedback_aou_success_marker_not_evidence_of_data`, `feedback_aou_cluster_sizing_for_ld_panel`, `feedback_npz_triangle_flag_contract`, `feedback_no_1000g_ld_pivot`.

### Live-only (NOT confirmable from NCSU)
- The *completing* A.3 write `blocks_per_min` at the new cell size (the re-probe).
- The byte-exact AoU egress enforced limit (first export / AoU support).

---

## Metadata

**Confidence breakdown:**
- Binding-constraint re-diagnosis (write-bound, no spill): HIGH — measured in-perimeter 2026-06-22.
- Split/write/egress arithmetic: HIGH — computed against real preflight density + source formulas.
- LD-decay radius floor: MEDIUM — cited public LD maps + Pan-UKBB; exact 3/5 Mb is a bracketed judgment (Carter's call).
- Egress cap mechanics: MEDIUM — AoU describes an alert threshold, not a documented hard cap (A2).
- Ordering B benefit: HIGH that it's now non-vacuous; MEDIUM that it beats A on wall-clock (re-probe).

**Research date:** 2026-06-22
**Valid until:** ~30 days (stable); the re-probe measurement supersedes the open absolute-write-rate question whenever it runs.

## RESEARCH COMPLETE
