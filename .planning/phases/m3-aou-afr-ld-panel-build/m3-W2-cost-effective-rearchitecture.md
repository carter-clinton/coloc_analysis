# m3-W2 Cost-Effective Re-architecture — fit the LD panel in ~$3–4k without sacrificing rigor

**Date:** 2026-06-23 · **Trigger:** Carter — "find a more cost-effective way to get ALL of it done;
can part run off-AoU / on NCSU HPC? budget can stretch to $3–4k; not guessing." · **Method:** 5 parallel
web-research threads (cited below) + the AoU perimeter/egress constraints. **Bottom line: yes — a
re-architecture fits ~$3–4k with margin AND is *more* rigorous than the current plan, not less.** It
rests on three moves: (1) **don't compute EUR LD at all — use a public biobank-scale EUR reference**;
(2) **compute AFR LD in-house but with a native tool on a single VM, not Hail BlockMatrix**; (3) keep all
downstream on NCSU (already planned, egress-clean).

---

## The one hard constraint (anchors everything)
Individual-level AoU WGS genotypes **cannot leave the VPC-SC perimeter** (DUA). LD is computed *from*
genotypes, so the **AFR LD correlation compute must happen in-perimeter**. But **aggregate LD matrices
(variant×variant r, no participant rows) ARE permitted egress** — AoU policy explicitly allows summary-
statistics download (a GWAS sumstats file is their named example); the only granularity rule is the
"buckets of <20 individuals" floor, which cohort-wide LD (tens of thousands of haplotypes) does not trip.
Large downloads hit a throttle (chunk files / file the relaxation form), not a ban. So **compute LD
in-perimeter → analyze on NCSU** is policy-clean (already GATE-0 RULED PASS). [AoU Egress Alert Policy;
Data User Code of Conduct; Policy Questions]

## Move 1 — EUR LD: use a public reference, don't compute it (removes ~52% of cost AND improves rigor)
The EUR arm colocalizes **external EUR GWAS/pQTL (UKB-PPP, deCODE, FinnGen…)**, not AoU. The rigor rule is
that **LD must match the GWAS sample's ancestry, and in-sample/large-matched is preferred** (Benner 2017
AJHG; Weissbrod 2020 NatGenet; Zou 2022 SuSiE-RSS; Kanai 2022 Cell Genomics). For a UKB-based EUR GWAS,
a **public UKBB LD reference is closer to in-sample than AoU's 220k EUR would be** — so computing AoU EUR
LD is not just expensive, it may be the *wrong* reference. Two free, biobank-scale public EUR panels exist:
- **Weissbrod/PolyFun UKBB LD** — N=337,491 British, **2,763 × 3 Mb regions, `.npz` + `.gz`** (matches our
  pipeline's `.npz` contract incl. the triangle flag), `s3://broad-alkesgroup-ukbb-ld/` (CC-BY, no-sign-request). **hg19.**
- **Pan-UKBB EUR LD** — in-sample **N=420,531**, Hail `.bm`, upper-triangular sparsified (maps to our
  `lower_triangular` flag concern), `s3://pan-ukb-us-east-1/ld_release/`.
**→ EUR LD compute cost = $0.** Integration cost (NCSU, free): adapt the external format + reconcile build
(refs are **hg19**, our pipeline is **hg38** → liftover/coordinate match). This is standard practice —
SuSiEx/MultiSuSiE use a *different* matched LD source per ancestry within one study. [Weissbrod 2020;
Pan-UKBB LD release 2020; SuSiEx NatGenet 2024; MultiSuSiE NatGenet 2025]

## Move 2 — AFR LD: compute in-house (it's the contribution), but cheaply
**No adequate public AFR LD reference exists** — the best public AFR panels are ~50–75× smaller than the
EUR one (gnomAD ~4.4k, Pan-UKBB AFR 6,636, TOP-LD 1,335 query-only, 1000G 661) and small/mismatched LD
**produces false-positive credible sets** — so AFR LD from the 73k AoU cohort is both **necessary and the
scientific contribution**. The published **MultiSuSiE (NatGenet 2025)** is the direct precedent: in-sample
per-ancestry LD from AoU WGS (47k AFR / 116k EUR), "in-sample LD to minimize computational costs," and AFR
fine-mapping was *more* powerful than EUR at matched N. **But compute it natively, not in Hail:**
- **Export the QC'd AFR cohort ONCE** from the Hail MT (`hl.export_plink` / `hl.export_bgen`) — one-time.
- **Run per-region banded LD on a single Spot VM** (n2-highmem-64), looping regions, checkpointed:
  - **plink 1.9 `--r square --keep-allele-order`** (lowest-risk SuSiE workhorse; the allele-order flag is
    mandatory or signs mismatch z — a known susieR failure). *(plink2 `--r2` is not yet implemented.)*
  - or **LDstore2** (FinnGen/FINEMAP in-sample standard, BGEN input) / **emeraLD** (fastest — 128× plink,
    250× LDstore at UKB N — but needs output-format verification + VCF conversion).
- **Why this is ~1–2 orders of magnitude cheaper than Hail BlockMatrix:** (a) compute shape — a single
  n2-highmem-64 is **~$4.19/hr on-demand / ~$1.49/hr Spot vs ~$23.4/hr for the 24-node Dataproc cluster**
  (~5.6× / ~16×); (b) native C avoids the JVM/Spark/shuffle/block-replication + driver-mediated BlockMatrix
  write that make Hail slow. [emeraLD Quick 2019; FinnGen LDstore2 pipeline; GCP pricing; Pan-UKBB used 500
  workers × 16h ≈ 64k CPU-h for genome-wide Hail LD — the cost we're avoiding]

## Move 3 — Downstream off-perimeter (already the plan)
coloc / SuSiE / MR run on **NC State HPC** consuming the egressed AFR LD `.npz` + the public EUR LD. No AoU
compute. Validate every region with the **SuSiE-RSS `estimate_s` / `kriging_rss` z-vs-LD diagnostic** to
guard allele-flip/encoding errors. [Zou 2022]

---

## Cost envelope (vs the ~$44k / 34k-cluster-h current plan)
| Component | Current (Hail, both ancestries) | Re-architected |
|---|---|---|
| EUR LD | ~half of 34k cluster-h | **$0** (public download) |
| AFR LD | ~half of 34k cluster-h on a 24-node cluster | native tool on 1 Spot VM — **est. $400–2,300** (per-region time TBD by pilot) |
| Downstream | NCSU (free) | NCSU (free) |
| **Total** | **~$15–44k** | **well within $3–4k**, likely < $2.5k |

At $1.49/hr Spot, $3–4k buys **~2,000–2,700 VM-hours** of native LD compute — far more than AFR-only needs.

## Two things to verify before committing (honest flags — this is where "not guessing" matters)
1. **One-region native pilot ($5–20):** no public benchmark exists at our exact 73k-sample × 3–5 Mb-band
   config. Run plink1.9 (or LDstore2) on **one real AFR region**, measure wall/RAM/output-size/cost →
   confirms the per-region cost and the Hail-vs-native multiplier on real dimensions (Carter's own rule:
   [[feedback_size_cost_experiments_on_real_data_dimensions]]). This *replaces* the earlier "$5 sizing probe."
2. **EUR-reference pipeline integration (NCSU, free but real):** adapt the public `.npz`/`.bm` format +
   triangle convention into our loader, and **liftover hg19→hg38** (or match variants by rsID/position).
   Confirm the EUR GWAS sources are UKB-ancestry-compatible (Carter's science input).

## What this does NOT change (rigor preserved/improved)
- AoU AFR WGS stays the committed AFR substrate ([[feedback_no_1000g_ld_pivot]]); we only swap the *tool*.
- EUR gains a **larger, better-matched** LD reference (337–420k vs AoU 220k, and matched to the EUR GWAS).
- Ancestry-matched, in-sample(-grade) per-ancestry LD — the MultiSuSiE/SuSiEx standard. Reviewer-defensible.

## Recommended next steps
1. **Carter confirms the EUR GWAS sources** (UKB-PPP / deCODE / FinnGen …) so we pick the matched public EUR
   panel (UKBB Weissbrod vs Pan-UKBB) — or decides he wants AoU in-sample EUR after all (still cheap natively).
2. **Run the one-region AFR native pilot** (plink1.9 first) to lock the real cost + tool choice.
3. **Re-plan** as a new phase (`m3-02e` / re-scoped m3-03/04): export-once → native per-region AFR LD on a
   Spot VM → egress → NCSU ingest of AFR(`.npz`) + public EUR + liftover adapter → coloc/SuSiE with the
   `estimate_s` diagnostic. m3-04's correctness preconditions (P1 densify, P2 resume, HLA split) fold in or
   are mooted by the native-tool path (e.g. plink writes the matrix directly — no `bm_to_npz` densify step).

### Sources (decision-grade, cross-verified)
Egress/pricing: AoU Egress Alert Policy, Data User Code of Conduct; GCP/Dataproc pricing. EUR refs:
Weissbrod 2020 NatGenet (PolyFun UKBB LD); Pan-UKBB LD release 2020. AFR scarcity: gnomAD v2.1.1 LD,
Pan-UKBB AFR (6,636), TOP-LD, 1000G. Tools: emeraLD (Quick 2019), LDstore2/FinnGen, plink1.9 docs.
Rigor: Benner 2017 AJHG, Zou 2022 SuSiE-RSS (PLoS Genet), Kanai 2022 Cell Genomics, Li & Zhou 2025 NRG,
SuSiEx 2024 / MultiSuSiE 2025 NatGenet (per-ancestry in-sample LD incl. AoU AFR — direct precedent).
