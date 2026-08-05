# M3 egress + validation protocol addendum

**Status:** RECORDED 2026-08-05 by `m3-04c` Task 2 (NC State, `$0`, no
perimeter contact).
**Supersedes, in part:** `AOU-LD-PIPELINE.md` §7 (export protocol) and §9.2
(Check 2), and the `.planning/amendments/aou-egress-audit-log.md` header's
44-bundle scope statement.
**Does NOT supersede:** the 2026-04-28 egress-classification HARD GATE ruling
(RULED PASS). That ruling stands untouched and byte-intact; only the SCOPE it
applies to narrows.
**OSF cross-reference:** `osf.io/az52u` (project amendment record);
pre-registration `osf.io/pvb5j` (DOI 10.17605/OSF.IO/PVB5J).

## Why this document exists

Three pre-registered protocol items were written against a producer that no
longer exists. The m3-02e Wave-2 cost re-architecture replaced the symmetric
AoU Hail BlockMatrix build (AFR + EUR, 322 compute cells, ~34k cluster-hours)
with:

* **AFR** — `src/python/run_native_ld_panel.py`: native `plink1.9`, Hail-free,
  a single AoU Cloud Analysis VM looping the 276 windows in
  `config/ld_regions.tsv` (~263 VM-hours, ~$385–1,084).
* **EUR** — the **public UKBB 337k** panel (`EUR_ukbb_pub`), built on NC State
  for `$0` by `src/snakemake/rules/m3_public_eur_ld.smk`. **No EUR LD is
  computed inside the AoU perimeter, and none ever will be.**

Two of the three items are therefore not merely stale but **structurally
unrunnable as written**. The project rule is that a pre-registered item which
cannot be run is **redefined in the open, with its evidence** — never silently
dropped and never quietly reinterpreted. This file is that record.

---

## (a) Egress UNIT redefinition — from 44 bundle OBJECTS to at most 22 AFR request groups

**What the stale plan assumed.** `m3-04-W4-production-and-egress-PLAN.md` and
`AOU-LD-PIPELINE.md` §7.2 assumed a per-chromosome **bundle OBJECT** that could
be sized, split and exported: "one export request per chromosome", 44 bundles
total (22 chromosomes × 2 ancestries), each with a compressed size to check
against a cap.

**What the real producer does.** `run_native_ld_panel.py:922-938` uploads, per
region, exactly three objects — `{region_id}.npz`, `{region_id}.afreq`,
`{region_id}.occluded.excludelist` — **DIRECTLY** to
`gs://<bucket>/ld/AFR_aou/{region_id}.npz` and siblings, gated on
`content_verify_npz` passing (`:946-953`). The panel TSV
`m3-W2-native-plink-panel.tsv` sits alongside them. **At no stage does a
"chr1 AFR bundle" object exist.** There is nothing on the bucket side to size,
nothing to split, and nothing to `validate_bundle_sizes.py` against.

**The redefinition.** A *bundle* is a **REQUEST-LEVEL GROUPING OF OBJECT
URIs** — the set of per-region `.npz` (+ `.afreq` + `.excludelist`) URIs for
one chromosome, transferred as one `gsutil -m cp` and logged as one row in the
egress audit log. Grouping stays per-chromosome because that is what keeps the
number of human egress actions tractable (each carries a ~2–5 business-day
review SLA), not because an object boundary exists there.

**Scope change: 44 → at most 22.**

| | stale basis | corrected basis |
|---|---|---|
| ancestries egressed | AFR + EUR | **AFR only** (EUR is public, `$0`, on NC State) |
| unit | per-chromosome bundle OBJECT | per-chromosome **grouping of object URIs** |
| count | 44 (22 chr × 2 anc) | **at most 22**, plus within-chromosome size splits |
| region basis | 322 compute cells | **276** regions (`config/ld_regions.tsv`, 123 of them m3-02b `__sub` splits) |

"At most 22" is deliberate: a chromosome with no AFR region in the M2 union
contributes no request, and a chromosome over the working ceiling contributes
more than one (`chrN_a` / `chrN_b`).

**Where this is implemented.** `src/python/plan_ld_egress.py` — a thin CLI over
the already-shipped `src/python/ld_egress_bundle.py::plan_egress_bundles`
(`ade6066`, m3-02d). The stale plan's `src/python/validate_bundle_sizes.py` is
**deliberately not written**; its function shipped nine weeks earlier, and
writing it would have produced a second, divergent bin-packer.

**Downstream consequences already landed (m3-04c Task 2).**
`src/snakemake/rules/m3_ingest_aou_ld.smk` is AFR-only (aggregate `expand`
yields ≤22 flags, not 44) and `build_ld_rds_aou_eur` is retired from
`src/snakemake/rules/m3_convert_npz_rds.smk`. The per-chromosome ARRIVAL flag
is retained on purpose: egress lands over multiple weeks and partial arrival
must still let partial conversion proceed.

---

## (b) `EGRESS_CAP_GB` provenance correction — a working ceiling, not an AoU limit

**The correction.** The 50 GB per-request ceiling is a **CONSERVATIVE PROJECT
WORKING CEILING, NOT a documented hard AoU API limit.** The primary record is
`src/python/ld_egress_bundle.py:9-15`:

> `EGRESS_CAP_GB = 50` is a CONSERVATIVE PROJECT WORKING CEILING, NOT a
> documented hard AoU API limit. AoU's real egress mechanism is an ALERT
> THRESHOLD + MANUAL RELAXATION at egress-request time (the real number is
> confirmed on the first export).

**What was wrong.** The stale `m3-04` plan carried "50 GB cap per RESEARCH Q4"
as though it were an external hard constraint, which would make an oversize
request a *blocked* action rather than a *reviewed* one. It is neither
documented nor enforced by AoU as a hard cap; it is our own convention,
inherited from the audit-log per-bundle note "split chr1 into 1a + 1b due to
>50 GB".

**Operational consequence.** The real ceiling is **confirmed on the first
export**, not assumed. `plan_ld_egress.py --cap-gb` exists precisely so that
confirmation can be applied without a code change, and the emitted plan carries
`n_bundles_over_cap` so an indivisible oversize region is visible rather than
silently mis-planned. Do not report a >50 GB request as a protocol violation;
report it as a request needing manual relaxation.

---

## (c) REQ-AOU-LD-VALIDATION Check 2 redefinition — §9.2 is structurally unrunnable

**The pre-registered text** (`AOU-LD-PIPELINE.md` §9.2, "Check 2 — AoU EUR vs
1000G EUR"): *compute AoU EUR LD at the same 10 regions; compute entry-wise
Pearson correlation against 1000G EUR. Pass threshold: mean entry-wise r ≥ 0.97
for variants with MAF ≥ 0.05 in both; ≥ 0.90 for MAF 0.01–0.05.*

**Why it cannot be run.** It requires an **AoU EUR LD panel**. After m3-02e
Move 2 there will not be one, at any point, for any region: EUR LD comes from
the public UKBB 337k reference on NC State. The check is **STRUCTURALLY
UNRUNNABLE** — not "expensive", not "deferred", not "failed". Its input does
not and will not exist.

**Why it is not simply dropped.** §9 is a **pre-registered hard gate**
(`AOU-LD-PIPELINE.md:423`: the four checks are "a hard gate for promoting the
pipeline from dev to production"). Dropping a pre-registered gate silently is
exactly the failure mode pre-registration exists to prevent. It is redefined
into three parts that together preserve a check **that can actually FAIL**.

### 2a — HARD GATE (replaces §9.2): code-path equivalence on a public substrate

Run `run_native_ld_panel.process_region` over the **public 1000G plink files
already on disk** (the LDSC `1000G_EUR_Phase3_plink` set) for 2–3
curated-overlapping windows, and compare the resulting `.npz` LD against an
independent `plink1.9 --r square bin4 --keep-allele-order` computed directly on
the same window.

* **PASS:** identical variant ordering **and** entry-wise `max |delta| ≤ 1e-6`.
* **What it validates:** the EXACT estimator plus IO path that produces the AFR
  panel — the same `--keep-allele-order`, the same `.ld.bin` reader, the same
  `.npz` writer, and the same `lower_triangular` flag (the flag contract that
  has already caused two real defects: CR-01 doubling and BR-01 A.3 halving).
* **Cost:** `$0`, NC State, no perimeter.
* **It can fail for a real code reason** — that is the point of keeping it a
  hard gate.
* **HONEST LIMITATION, to be stated in the memo:** it validates the CODE, not
  the AoU substrate and not the cohort QC. Nothing in the redefined 2a
  substitutes for the substrate assurance the original §9.2 was reaching for;
  2b and 2c are what remain of that, and neither is a gate.

### 2b — REPORTED, explicitly NOT thresholded: AoU AFR vs 1000G AFR

Entry-wise Pearson r between the AoU AFR panel and 1000G AFR on shared variants
at the validation regions, stratified by MAF.

**A threshold here would be scientifically wrong.** 1000G AFR (n=661,
continental African) and AoU AFR (n≈73k, admixed African-American) differ in
both population and sample size, and **that divergence is the entire rationale
for M1a** (`AOU-LD-PIPELINE.md` §1). A LOW r is the expected and desired
finding. **Reporting the number IS the deliverable**; there is no pass mark, and
none may be introduced after the fact.

### 2c — SANITY, not a hard gate: `EUR_ukbb_pub` vs 1000G EUR

Entry-wise r between the shipped `EUR_ukbb_pub` chain head and 1000G EUR at the
same regions, MAF ≥ 0.05, **expected r ≥ 0.90**. This confirms the EUR chain
head that actually shipped is sane. The original 0.97 bar is inappropriate: both
panels are external and differ ~670-fold in n (337k vs 503), so 0.97 would fail
for a correct panel.

### The pre-registration consequence — ROUTED, NOT ABSORBED

§9 is a **PRE-REGISTERED hard gate**, so this redefinition requires an
**OSF amendment-update** posting BEFORE any redefined check is cited as passed.
This mirrors the m3-07a gate discipline: the amendment is **drafted by the
agent**, **POSTED by Carter**, and the resulting file GUID recorded here and in
`.planning/DECISIONS.md`.

⛔ **UNTIL THAT POSTING EXISTS, Check 2 is reported as
`OVERRIDDEN — redefined pending amendment`, never as "passed".** That applies
to 2a as well as to 2b/2c, and to any summary, memo, ROADMAP row or manuscript
sentence that would otherwise claim the §9 four-check gate is cleared.

Routing: `m3-04c` Task 3 gate, **STEP F**.

| item | status | posted amendment GUID |
|---|---|---|
| Check 2 redefinition (2a / 2b / 2c) | DRAFTED — awaiting Carter's OSF posting | _(pending)_ |

---

## Evidence index

| claim | primary evidence |
|---|---|
| per-region `.npz` written directly; no bundle object | `src/python/run_native_ld_panel.py:922-938`, `:946-953` |
| 50 GB is a working ceiling, not an AoU limit | `src/python/ld_egress_bundle.py:9-15` |
| the bundler already shipped | `ld_egress_bundle.plan_egress_bundles`, commit `ade6066` (m3-02d) |
| EUR head is `EUR_ukbb_pub`, `$0`, NC State | `config/pipeline.yaml` `ld_panel.EUR`; `src/snakemake/rules/m3_public_eur_ld.smk`; m3-02e Move 2 |
| 276 regions, 123 of them `__sub` splits | `config/ld_regions.tsv` (552 data rows = 276 unique ids × 2 ancestries) |
| §9 is a pre-registered hard gate | `.planning/amendments/AOU-LD-PIPELINE.md:423`; §9.2 at `:407-409` |
| the 2026-04-28 egress ruling is unchanged | `.planning/amendments/aou-egress-audit-log.md` (append-only; ruling text byte-intact) |
