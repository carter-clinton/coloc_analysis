# Deferred items — discovered during m3-04b execution (2026-08-03)

Out of this plan's scope (the m3-07 modules are pinned at a 0-line git diff by
m3-04b's must_haves). Logged, NOT fixed.

## D-04b-01 — `int(POS)` under-drops on a FLOAT-formatted POS column

**Found:** running the real 9-file present-rate scan as an end-to-end check of the
new assembler (NC State, public GRCh37 data, read-only, $0).

`data/processed/sumstats_harmonized/bmi.AFR.PAGE.2019.GRCh37.tsv.bgz` stores the
position as `5982778.0` (a float string), e.g.

    1	5982778.0	rs182965575	A	G	0.00539024	0.03857649	0.8888744	0.006747238	49335

Both `occlusion_present_rate_scan._canonical_key` and
`drop_occluded_from_sumstats._canonical_key` do `int(pos)`, which raises
`ValueError` on `"5982778.0"`. Each caller catches it and SKIPS the row:

* the scan `continue`s -> the variant is scored ABSENT in that trait;
* the filter sets `key = None` -> the row is KEPT, i.e. the occluded variant is
  NOT dropped from that file. A silent under-drop, wearing a clean
  `n_dropped == 0`.

**Measured consequence.** The scan reports rs182965575 (GRCh37 `1:5982778`) present
in **6 of 9** AFR sumstats (`asthma, hdl, ldl, t2d, tc, tg`). The project record and
the m3-04b/m3-07c objectives state **7 of 9**. The one-file gap IS `bmi.AFR.PAGE`,
where the variant is genuinely present (confirmed by direct read) but unparseable
under `int()`. The historical 7/9 is correct; the scan under-counts by one.

**Blast radius on THIS plan: none.** `rule occlusion_filter_sumstats` constrains
`stem=r"[A-Za-z0-9_.\-]+\.AFR"`, so the only mirrored files are `asthma.AFR`,
`stroke.AFR` and `t2d.AFR` — all three verified to carry INTEGER positions. The
defect affects the present-rate k/n published in the catalog, not the drop applied
to any `run_finemap` input on today's tree.

**Fix when in scope:** a shared coordinate coercion that accepts an integral float
(`int(float(pos))` only when `float(pos).is_integer()`, never a silent truncation),
applied to BOTH modules with a failing-test-first regression — the
`extract_reusable_utilities` pattern. Both modules are frozen for m3-04b.

## D-04b-02 — 6 of 9 AFR `.tbi` indexes are STALE

`asthma.AFR`, `hdl`, `stroke.AFR`, `t2d.AFR`, `tc`, `tg` all have a `.tbi` OLDER
than the `.bgz` it indexes. `tabix` then emits only `[W::hts_idx_load3] The index
file is older than the data file` and returns NOTHING — a silent empty result that
reads exactly like "variant absent". This is what made a tabix-based cross-check of
D-04b-01 disagree with the streaming scan in both directions.

Pre-existing, unrelated to m3-04b, and NOT touched here. `rule
occlusion_filter_sumstats` rebuilds the `.tbi` for its own mirror
(`tabix -f -S 1 -s 1 -b 2 -e 2`), so the mirror's index is fresh by construction.

## D-04b-03 — the full-workflow `snakemake --dry-run --quiet` cannot pass on this tree

`data/processed/ld_reference/` does not exist (the AoU fire has banked 0/276 `.npz`),
so `resolve_ld_path` raises `FileNotFoundError: No LD panel found for FTO_16q12 AFR`
from `ld_panel.py:94`. Verified PRE-EXISTING: the identical error, from the identical
line of `ld_panel.py`, is produced by `git show HEAD:Snakefile` at the m3-04b entry
commit `3e7a01a`. m3-04b's plan lists a clean full-workflow dry run as an acceptance
criterion; that criterion is unsatisfiable independently of this plan's work, and is
m3-04c's (panel reachability) to discharge.

## LOW-1 DEFERRED — denominator redefinition (files vs distinct traits) needs Carter

**Logged:** 2026-08-04 (quick-260804-rtc, Task 3). **Status: DEFERRED, not fixed.**

The present-rate scan scope resolves **9 FILES but only 8 DISTINCT TRAITS**: both
`stroke.AFR.tsv.bgz` and `stroke.AFR.GIGASTROKE.2022.GRCh37.tsv.bgz` report the trait
`stroke`. Confirmed on the real corpus by
`.planning/quick/260804-rtc-.../measure_present_rate_kn.json`
(`stats.duplicate_traits == ["stroke"]`, `n_files_scanned == 9`,
`n_distinct_traits_scanned == 8`).

**What quick-260804-rtc DID do:** made it VISIBLE. `scan_present_rate` now records
`n_distinct_traits_scanned` / `duplicate_traits` in its `stats` out-param and emits one
loud STDERR note stating plainly that `n_traits_scanned` is a **FILE** rate and not a
trait rate.

**What it deliberately did NOT do:** change the denominator. The project record and
the pre-registration (osf.io/az52u, amendment-update POSTED 2026-07-10T13:32:22Z,
recorded `ac4c990`) publish *"rs182965575 is present in 7 of 9 AFR **sumstats**"* — a
FILE rate. Redefining it to distinct traits would move a PRE-REGISTERED number, and
that is **Carter's call, not an executor's**.

**The fork, stated neutrally:**

| Option | k/n for rs182965575 | Argument |
|---|---|---|
| **A — keep the FILE rate (shipped today)** | 7 of 9 | Matches what is already pre-registered and quoted in four module docstrings + `m3_occlusion_lockstep.smk`. No amendment needed. But `stroke` contributes twice to the denominator while contributing one trait's worth of evidence. |
| **B — switch to a DISTINCT-TRAIT rate** | would become 7 of 8 (`stroke` carries the variant in neither file) | Arguably the more honest scientific denominator — the claim is about how many TRAITS carry the variant. Requires an OSF amendment and a sweep of every quoted "7 of 9" in the repo. |

**Recommendation if asked:** B is the more defensible denominator, but it is a
pre-registration amendment, not a code change, and must be decided before the catalog
is published — not after.

**Not blocking:** nothing downstream depends on the choice today; the drop key is
unaffected (present-rate is reporting, never a filter).

---

# Deferred items — discovered during m3-04c Task 2 execution (2026-08-05)

Out of Task 2's scope (its `<action>` enumerates exactly three ROADMAP edits).
Logged, NOT fixed.

## D-04c-T2-01 — ROADMAP "Live progress 2026-05-21" line still cites the dead `m3_dev_complete.flag` gate

**Found:** applying Task 2 step 7's three ROADMAP edits (lines 200 / 211 / 212).

`.planning/ROADMAP.md:218` still reads:

> **Live progress 2026-05-21:** … m3-04 W4 + m3-05 W5 blocked on
> `m3_dev_complete.flag` existing.

That gate is one of the nine staleness axes the replanned line 211 now names as
UNREACHABLE — the dev-10 Hail fire it gated was killed as intractable
(Wave-2 re-scope) and never produced the flag. The line therefore advertises a
blocker that can never clear, next to a plan entry that says so.

**Why not fixed here:** Task 2 step 7 enumerates exactly three ROADMAP edits
(the `**Plans**` count line, the m3-04 entry, the m3-05 entry). Line 218 is a
phase-status narrative line owned by the STATE/HANDOFF surface, and the executor
instruction for this task is explicit that handoff-adjacent files are Carter's.

**Cost of leaving it:** documentation only. No rule, test or DAG reads it.

**Suggested fix:** fold it into the m3-05 replan, or into whichever quick task
next refreshes the M3 phase status block, replacing the flag clause with the
real gate (Task 3's in-perimeter fire + egress).

---

# Deferred items — discovered during quick-260805-w7u execution (2026-08-06)

Closing blast-radius finding **E** (`m3-04c-BLAST-RADIUS.md:141`, gate row
"Any GWAS×QTL colocalization"). Logged, NOT fixed.

## E-2 DEFERRED — the QTL-beta ↔ panel-ALT orientation needs Carter

**Logged:** 2026-08-06 (quick-260805-w7u). **Status: DEFERRED, not fixed.**
Named in the plan's `<explicitly_deferred>` so nobody discovers it by diffing.

`qtl_data$LD` is signed on the **panel's ALT** (plink `--keep-allele-order` is
hardcoded on every LD call, `aou_ld_panel.py:2905`; `plink --r` signs the
correlation on A1 == ALT). `qtl_data$beta` is signed on the **QTL's effect
allele**. When the two are transposed, the QTL SuSiE fit is mis-signed against
its own LD — finding **H**'s family, relocated to the QTL side.

**Why it is deferred rather than fixed:**

1. **It is PRE-EXISTING on the legacy 1kG/EUR path and unaddressed there today.**
   It is not created by 260805-w7u; closing finding E merely makes it reachable
   on a second panel.
2. **Fixing it would MOVE Track-A numbers.** Today's coloc successes are
   **32/32 EUR**, `1,957` legacy coloc JSONs exist, and Track A is **in
   submission**. A sign correction on the QTL beta changes PP.H4 for EUR pairs
   with no error and no flag — the same class of silent movement BLOCKER-B
   documented for the fine-map path.
3. **It is not named by finding E.** E is "the colocalization would mix LD
   panels". Orientation is a separate defect that happens to live next door.
4. **It needs a GRCh38↔GRCh37 allele reconciliation that is its own task.** The
   QTL side is GRCh38 (`variant_id = chr12_110962202_G_A`); the panel and the
   region variant catalog are GRCh37. There is therefore no position join
   available on the QTL side at all — the panel↔catalog join this task landed
   works precisely because BOTH of its sides are GRCh37. Reconciling the QTL
   side requires a lift plus an allele-compatibility decision (and the lift
   carries `ld_npz_to_rds.R:348-361`'s non-complementing REF/ALT hazard, which
   is why palindromes are dropped rather than kept).

**What quick-260805-w7u DID do — and this is the part that makes E-2
actionable rather than rhetorical.** The panel↔catalog join emits
`ld_allele_flipped` (and the five sibling counters) into **every per-pair JSON
and a per-pair log receipt**. `ld_allele_flipped` is the count of rows whose
REF/ALT are transposed between the catalog and the panel at the same position —
i.e. **the population in which an orientation error can occur at all**. So E-2's
magnitude is now **MEASURABLE per region** instead of invisible. Carter can
decide on evidence rather than on argument: run the gated path, read
`ld_allele_flipped / (ld_allele_exact + ld_allele_flipped)` off the receipts,
and see whether the exposed fraction is 0.1% or 40%.

It also closed the **row-binding half**, which is independent of sign: a
multiallelic site binding to an arbitrary ALT's LD **ROW** is a wrong-row error
whether or not the sign is right, and that is fixed for the gated path.

**The fork, stated neutrally:**

| Option | Effect | Argument |
|---|---|---|
| **A — leave it (shipped today)** | EUR/Track-A numbers frozen; AFR coloc carries the same pre-existing orientation exposure the EUR path already carries | Nothing in submission moves. The exposure is now COUNTED, so it is disclosable rather than unknown. Reviewer-visible as a stated limitation. |
| **B — correct the QTL beta orientation** | PP.H4 moves for any pair with transposed variants, **including EUR** | Scientifically the right sign convention. Requires: a GRCh38↔GRCh37 reconciliation for the QTL side; an ancestry gate if Track A must not move; a before/after comparison; and a disclosure in the manuscript/OSF record. |

**Recommendation if asked:** B is correct, but it is a Track-A-moving change on
a manuscript in submission, so it must be scoped as its own task with its own
`identical()`-style containment proof — exactly as `260805-23d` scoped BLOCKER-B
— and **not** as a rider on finding E. Decide it before any AFR coloc figure is
published, using the counters this task emits.

**Not blocking:** the counters are reporting, never a filter. Nothing downstream
reads them today except the per-pair receipt.

## E-3 (minor) — two stale schema comments assert a measured-false claim

`src/snakemake/schemas/pipeline.schema.yaml` carries two comments (on the
`ld_read_path` block itself and on `allele_aware`) stating that without their
entry "EVERY Snakemake invocation fails at `validate()`". That was **measured
FALSE** in 260805-o7o Deviation 1: `additionalProperties: false` is TOP LEVEL
only, so `ld_read_path` sub-keys are permitted by JSON-Schema's default with or
without a declaration (re-measured here: rc 0 without the entry).

**Why not fixed here:** pre-existing, and editing prose in two unrelated comment
blocks is outside this task's scope boundary. The NEW `coloc` entry's comment
states the correction explicitly and points at this entry, so a reader is not
left with only the false version.

**Cost of leaving it:** documentation only; no rule, test or DAG reads it.

## E-4 — `build_qtl_coloc_manifest.py::_ancestry_for_region` is hardcoded to `"EUR"`

`src/python/build_qtl_coloc_manifest.py:245` returns `"EUR"` unconditionally,
ignoring the region entirely. Consequence, **measured** and pinned by
`tests/m3/test_qtl_coloc_ld_resolution.py::test_ancestry_for_region_is_hardcoded_eur_today`:
with the shipped allow-list (`AFR`) **no manifest row takes the new
`RESOLVED_BY_LD_PANEL_RESOLVER` sentinel branch**, and no manifest row reaches
`_qtl_coloc_ld_input`'s resolver branch either. The manifest half of finding E's
remedy is wired and correct but **INERT today**.

**Why not fixed here:** teaching `_ancestry_for_region` about AFR CHANGES THE
MANIFEST — new rows, new `qtl_coloc_id`s, a different DAG — for a pipeline whose
current coloc outputs are 32/32 EUR and feed Track A. That is a scope and
analysis decision, not a plumbing fix.

**Cost of leaving it:** finding E's remedy cannot be exercised end-to-end in
production until AFR rows exist. It is proven on fixtures, and it goes live the
moment this function learns about AFR — which is the same moment the AFR coloc
work would begin anyway.

---

# Deferred items — discovered during quick-260806-b77 execution (2026-08-06)

Closing blast-radius findings **G, J, L, M** (`m3-04c-BLAST-RADIUS.md:133-144`,
gate rows "Any TRANS fit" and "Growing the curated region set") and registering
**K** as a prepared deferral. Logged, NOT fixed.

## G-2 — TRANS has no AoU panel and never will; is a TRANS fit on a 1kG EUR panel reportable?

**Logged:** 2026-08-06 (quick-260806-b77). **Status: DEFERRED — Carter's
scientific call, not an executor's.** Not blocking.

Finding **G** is CLOSED in the engineering sense: `strict_aou_only` can now see
the orphaned TRANS chain head. That closure makes the situation **VISIBLE**. It
does not make TRANS **WORK**, and the difference is the whole of this entry.

**The measured facts.**

1. `config/pipeline.yaml`'s TRANS chain HEAD is
   `TRANS_aou_eur -> data/processed/ld_reference/EUR_aou/{region_id}.rds`.
2. **Nothing produces that artifact.** `build_ld_rds_aou_eur` was retired
   2026-08-05 (`src/snakemake/rules/m3_convert_npz_rds.smk` retirement note)
   because m3-02e Move 2 made the PUBLIC UKBB 337k panel the EUR chain head, and
   **no EUR LD is computed inside the AoU perimeter at all** — so
   `data/interim/aou_ld_exports/EUR_aou/` is never populated, before OR after the
   ~11-day fire. Pinned in-suite:
   `test_no_non_comment_line_declares_the_eur_aou_artifact_path`.
3. **Therefore every TRANS resolution lands on `EUR_1kg`** — the legacy 1kG EUR
   panel — on every run today and after the fire. A TRANS fit is fitted on 1kG
   EUR LD.
4. `strict_aou_only` (shipped `false`) is now the lever that converts that
   silence into a `FileNotFoundError`. Before quick-260806-b77 the guard tested
   `source.endswith("_aou")`, which is `False` for `TRANS_aou_eur`, so strict
   mode was **provably blind** and TRANS walked to 1kG *even with strict mode
   ON*.
5. ⛔ **`pin.TRANS` is NOT a remedy.** `pin` short-circuits the chain **ahead of**
   strict mode (`src/python/ld_panel.py::resolve_ld_path`), so pinning TRANS to
   `EUR_1kg` would RE-HIDE exactly what the fix exposes.
6. ⛔ **Deleting the orphan is NOT a remedy either.** Removing `TRANS_aou_eur`
   leaves TRANS with no AoU entry at all, making `strict_aou_only` structurally
   unable to ever flag TRANS again — deletion DEEPENS the silence. Pinned by
   `test_the_trans_orphan_is_still_in_the_shipped_chain`.

**The question this leaves open, which is scientific and not mechanical:** the
project's TRANS ancestry exists to describe a trans-ancestry meta-analysis. Its
LD is, and will remain, a **European** reference. Is a TRANS fine-mapping result
on a EUR LD panel reportable at all, and under what disclosure?

**The fork, stated neutrally:**

| Option | Effect | Argument |
|---|---|---|
| **A — report TRANS fits on the 1kG EUR panel, disclosed** | Nothing moves. TRANS results keep flowing exactly as today. | It is what every TRANS number in the repo already rests on, so A is the *status quo made honest* rather than a change. Requires an explicit manuscript/OSF sentence: "trans-ancestry fine-mapping used a European (1000G EUR) LD reference; LD mis-specification is expected and is a stated limitation." |
| **B — stop producing TRANS fine-mapping results until a trans-ancestry LD reference exists** | TRANS rows disappear from the fine-map outputs; `strict_aou_only: true` (or an ancestry gate) enforces it. | LD mis-specification is precisely the miscalibration M3 exists to correct; using EUR LD for a trans-ancestry statistic is the same class of error, one ancestry over. Costs every TRANS result and needs a decision about what replaces them (an AFR+EUR meta of per-ancestry fits, or nothing). |

**Recommendation if asked:** decide it **before** any TRANS figure or table is
published, and record the decision in the OSF amendment either way. A is
defensible with disclosure; B is defensible on rigor; silently shipping A
*without* the disclosure is the only option that is not.

**Not blocking.** `strict_aou_only` ships `false`, so the guard is INERT today
and nothing in the DAG changes. The closure of G is what makes this decision
possible to take on evidence instead of by accident.
