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

## E-2 — ✅ DECIDED 2026-08-07 as option A (leave the code, DISCLOSE a MATERIAL exposure)

> **✅ DISPOSED — `DEC-2026-08-07-e2-orientation-disposition`.** Carter chose
> **A** on measured evidence: the code is **NOT** changed; the exposure is
> disclosed as a stated limitation. **B is not "wrong", it is PREMATURE** — it is
> inert without **E-4**, it moves Track A numbers mid-submission, and the only
> substrate available to validate it is an identity-LD stub tree.
>
> ⚠ **THE EXPOSURE IS MATERIAL IN 2 OF THE 5 TRACK-A COLOC REGIONS** —
> `APOL1_22q12` **18.41%** and `FTO_16q12` **23.80%**; `SH2B3_12q24` tile 3 is
> **20.33%** while its anchor tiles 1–2 are **0.00%**; `CXADR_F2RL1_6p21` and
> `MC4R_18q21` are clean at ~0.06%. **Do not quote the 5.29% pooled figure
> alone** — it is dragged down by the two clean large regions.
>
> ⚠ **CORRECTION TO THE RECORD:** an interim report gave SH2B3 tile 3 as
> "0.20%". It is **20.33%** (a ratio of `0.2033` misread as a percent) — a 100×
> error in the reassuring direction.
>
> **THREE OBLIGATIONS SURVIVE, none discharged:** (1) a manuscript limitation
> paragraph naming `APOL1_22q12` and `FTO_16q12` explicitly; (2) an OSF record
> entry; (3) ⚠ **an OPEN question above executor authority — is this a
> LIMITATION or a CORRECTION?** Two of five coloc regions at ~18–24% is large
> enough that a reviewer may read it as the latter.
>
> **▶ UPDATE 2026-08-11 — OBLIGATION (3) IS DISCHARGED.** Framing **B
> (CORRECTION)** is chosen — `DEC-2026-08-11-e2-framing-correction` — selecting
> the matched pair `ms-correction` + `osf-correction`. **(1) and (2) remain
> OPEN** and are **Carter's external actions**. ⚠ Framing B is **NOT**
> disposition option B: the code is still not changed. See the
> **▶ E-2 FRAMING DECIDED (2026-08-11)** section at the end of this E-2 material
> for the full record.
>
> **B becomes right** bundled with **E-4**, after the AoU panel exists, with a
> real-LD re-measurement + before/after + OSF disclosure. **E-2 and E-4 are
> COUPLED.**
>
> The original entry is preserved below unchanged.

**Logged:** 2026-08-06 (quick-260805-w7u). **Status: SUPERSEDED — DECIDED as A
on 2026-08-07; preserved verbatim for the record.**
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

### ▶ E-2 EVIDENCE UPDATE (2026-08-07) — measured on the real corpus, not a fixture

**Why this exists.** The entry above says Carter should "decide on evidence
rather than on argument" by reading `ld_allele_flipped / (exact + flipped)` off
the per-pair receipts. **Those receipts cannot exist yet** — the shipped counter
path is gated to AFR (`ld_read_path.ancestries`), AFR has **zero** QTL-coloc jobs
(E-4), and the AoU panel is 0/276. So the quoted **46/182 = 25.3%** is a
**synthetic acceptance fixture**, not a measurement of anything real.

**What was measured instead ($0, read-only, NC-State, nothing written to the
repo tree).** The catalog↔panel allele join was run directly over the **207 real
region variant catalogs** in
`data/processed/region_analysis/ld_reference/variants/` against the `variants`
frames of the panels in the sibling ancestry directories, using the **SHIPPED**
`ld_allele_join_indices()` from `src/snakemake/scripts/ld_allele_join.R` — never
a reimplementation (the `260805-w7u` body-walk rule).

| Statistic (per region, EUR arm) | Value |
|---|---|
| regions measured | **206** |
| regions with ≥1 transposed row | **195 / 206** |
| **median** flipped ratio | **17.82%** |
| mean | 12.49% |
| max (`RAD50_peak__tile1`) | **38.68%** |
| min | 0.00% |
| pooled across all rows | 4.18% (31,152 / 745,534) |

⚠ **The pooled 4.18% is MISLEADING and must not be quoted alone.** It is dragged
down by a few very large zero-flip regions (`SH2B3_12q24__tile1/2` contribute
10,521 exact rows with **zero** flips). **A fit is per-region, so the per-region
median (17.8%) is the decision-relevant number** — and it is *worse* than the
fixture's 25.3% suggested for the typical region only in the sense that it is
pervasive: 195 of 206 regions are affected.

**The transposition is real, not an artifact.** Example from
`RAD50_peak__tile1`, where 1,388 of 3,474 catalog rows bind swapped:

| side | CHR | POS | REF | ALT | SNP_ID |
|---|---|---|---|---|---|
| catalog | 5 | 131306363 | C | A | `5:131306363` |
| panel | 5 | 131306363 | **A** | **C** | `rs147814714` |

The catalog and the panel `variants` frame are **different vintages** (positional
IDs vs rsIDs) with opposite allele orientation at the same coordinate.

**★ THE TRACK-A-RELEVANT RESULT — measured 2026-08-07 over the FIVE regions
Track A's coloc numbers actually depend on** (parsed from the `pair_id` column of
`results/multitrait/coloc_summary.tsv`).

⚠⚠ **THIS TABLE CORRECTS AN EARLIER VERSION OF THIS ENTRY.** The first draft
reported only SH2B3 and gave its tile 3 as **"0.20%"**. That was a **100× error**
— a ratio of `0.2033` misread as a percentage — and it ran in the *reassuring*
direction, in the exact claim option A was first proposed on. It also generalised
from the anchor alone to "Track A", which the full five-region sweep does not
support.

| Track A region | exact | flipped | ratio |
|---|---|---|---|
| `CXADR_F2RL1_6p21` (5 tiles) | 28,415 | 18 | **0.06%** |
| `MC4R_18q21` (2 tiles) | 14,141 | 10 | **0.07%** |
| `SH2B3_12q24` (3 tiles) | 11,826 | 333 | **2.74%** |
| — `__tile1` / `__tile2` (the **anchor**) | 10,521 | **0** | **0.00%** |
| — `__tile3` | 1,305 | 333 | **20.33%** |
| `APOL1_22q12` (2 tiles) | 4,910 | 1,108 | **18.41%** |
| `FTO_16q12` (3 cells) | 7,188 | 2,245 | **23.80%** |
| **pooled over the Track A set** | 66,480 | 3,714 | **5.29%** |

**⚠ TWO OF THE FIVE ARE MATERIALLY EXPOSED** (`APOL1_22q12`, `FTO_16q12`), and a
third has one exposed tile. **Do NOT quote the 5.29% pooled figure alone** — it
is dragged down by the two clean large regions (`CXADR`, `MC4R`) and hides that
two regions sit near 20%. The md5-pinned **anchor** tiles are genuinely 0.00%,
which is real but is **not** a statement about Track A as a whole.

**The worst-exposed regions corpus-wide** are `RAD50_peak__tile1` (38.7%),
`FTO_16q12` (34.1% on its untiled cell), `IRS1_2q36__tile1` (28.1%). Note
`RAD50_peak__tile1` is also one of the nine `variant_catalog_fallback: true`
Path-1 artifacts found by K-1, and `FTO` is both a BLOCKER-D large region **and**
a Track A coloc region.

⚠⚠ **THE CAVEAT THAT BOUNDS ALL OF THE ABOVE.** Every panel in that tree is an
**identity-LD stub**: `use_identity = TRUE`, `R` is **NULL**,
`status = "variants_exceed_threshold"`, and the `EUR/`, `AFR/` and `TRANS/`
directories are **byte-identical** (md5-verified on two regions). The allele
question does not depend on `R`, so the transposition counts are meaningful **for
the variant bookkeeping** — but it is **NOT verified** that a real (non-identity)
panel carries these same `variants` frames. Do not report these as the real-LD
exposure; report them as the catalog↔panel-frame transposition rate.

**What this changes for the decision.** Track A's anchor is at ~0% exposure, so
option **B gated to AFR** would leave Track A numerically untouched *and* lose
almost nothing at SH2B3 — but it would be **INERT today** because of E-4
(`_ancestry_for_region` returns `"EUR"` unconditionally, so no AFR QTL-coloc job
exists to exercise it). **E-2 and E-4 are therefore coupled: fixing E-2 alone
buys a correct-but-unexercised path, the same shape as findings E and G.**

### ▶ E-2 FRAMING DECIDED (2026-08-11) — B (CORRECTION)

**Obligation (3) of `DEC-2026-08-07-e2-orientation-disposition` is DISCHARGED**,
recorded as `DEC-2026-08-11-e2-framing-correction`. Carter delegated the choice
to the standing recommendation on the `260811-oku` decision surface:

> "Based on your recommendation, choose the pair for E-2, and for SR4-OPEN,
> correct the handoff language"

**The selected pair.** `ms-correction` → the Track A (`id-vs-ref-LD`)
manuscript, as a methods correction-and-disclosure note. `osf-correction` → a
**new supplementary file** on `osf.io/az52u`. Both are paste-ready, and
byte-identical to their oku sources, at
`.planning/quick/260811-tf3-record-carter-decisions-e-2-framing-b-co/260811-tf3-SELECTED-PAIR-correction.md`.
The unselected `ms-limitation` / `osf-limitation` halves stay in the oku
directory as the record of what was considered and are **not** to be posted.

**Why B, compressed.** A limitation is something the data cannot do; this is
something the pipeline **did wrongly** — coordinate matching that ignored the
alleles — so filing it under Limitations describes it inaccurately, and
inaccuracy in the reassuring direction is the class of error this arc has
already committed twice. The magnitude claim is bounded identically by both
bodies (same identity-LD-stub caveat, same "population, not realised errors"
sentence), so B corrects the convention without over-claiming the size. B's
extra obligation — real-LD re-measurement, before/after, a further OSF update —
is one the **E-4** bundle already carries. And the asymmetry favours B:
over-correcting costs a paragraph, while under-calling a measured 18–24%
exposure that a real panel later confirms costs the record showing the softer
word was chosen **after** measuring 18.41% and 23.80%.

**⚠ PRE-PLACEMENT CHECK — Carter's, before placement.** The target journal's
policy is the one input to this decision that is not in this repository. If the
journal reads a "correction" framing on an **in-submission** manuscript as a
formal post-publication correction notice, keep **B's CONTENT** and use **A's
PLACEMENT** (the Limitations section). Placement only: it reopens no framing,
changes no number, and changes no sentence of either body.

**⚠ THE AXIS GUARD.** Framing B is **NOT** disposition option B. E-2 remains
disposed as **option A** — the code is still not changed — and only the framing
axis moved here.

| Obligation | Status |
|---|---|
| **(3)** LIMITATION vs CORRECTION | ✅ **DISCHARGED** 2026-08-11 (`DEC-2026-08-11-e2-framing-correction`) |
| **(1)** manuscript paragraph | ⛔ **OPEN** — Carter places `ms-correction` in the Track A manuscript |
| **(2)** OSF record entry | ⛔ **OPEN** — Carter posts `osf-correction` as a NEW supplementary file on `osf.io/az52u` **and** records its URL + timestamp in `.planning/osf_deviations.md` |

> ⚠ **ANNOTATED 2026-08-12 EVENING (quick-260812-thz; rows above preserved, not
> rewritten).** Two updates the table predates: **(a)** the body names are now the
> **v2** pair (`260812-09a-SELECTED-PAIR-correction-v2.md`) — the `ms-correction` /
> `osf-correction` v1 names above are superseded history and must not be placed or
> posted (`DEC-2026-08-12-adversarial-review-remediation`); the placement-ready
> surface for (1) is the ot2 SPEC
> (`.planning/quick/260812-ot2-e-2-obligation-1-placement-draft-and-jou/260812-ot2-placement-draft-ms-correction-v2.md`).
> **(b)** Obligation **(2) is SKIPPED BY CARTER'S DIRECTION = DEFERRED, NOT
> DISCHARGED** (`DEC-2026-08-12-e2-obligation1-venue-and-obligation2-skip`); its
> discharge condition is unchanged, and if placement uses the P-1 (byte-intact)
> closing sentence it must be revisited before submission.

⛔ **No agent posts to OSF, edits a manuscript file, or edits the body of a
posted amendment.** OSF bodies are append-only, and (1) and (2) discharge only
by Carter's external actions.

⚠ **Posting makes a currently-internal commitment PUBLIC.** The `osf-correction`
body closes by committing to an allele-aware join, a real-panel re-measurement,
and affected African-ancestry results **regenerated and re-reported** with a
before-and-after comparison, posted as a further update whether or not the
reported conclusions change. That is an internal **E-4** obligation today; on
posting it must be registered as a tracked obligation of the E-4 work so it
cannot be lost.

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

## ✅ K-1 CLOSED — `variant_catalog_fallback`'s legacy semantics are RESTORED

**Logged:** 2026-08-06 (quick-260806-b77). **CLOSED:** 2026-08-06
(`quick-260806-pd3`), applied in commit **`bf04199`**. Carter authorized
**option B** on 2026-08-06.

**What landed.** ONE line — `variant_catalog_fallback <- TRUE` — deleted from
the Path-2 (`ld_overlap == 0`) brace block of
`src/legacy/region_analysis/scripts/run_susie_rss.R`, plus the comment above it
reworded. The key is now assigned at **exactly one site**, the Path-1 AFR
variant-catalog empty-subset revert, which is its original and only meaning.
Science behaviour is unchanged: the branch still reverts to `subset_base`, still
retries exactly once, and still records itself via `ld_overlap_zero_fallback`,
which is still emitted in the success JSON and still read by the `finemap.smk`
receipt. **Nothing became invisible.**

**Both authorizations: GRANTED and SPENT.**

* **AUTH-K1-UNFREEZE** — single-use unfreeze of `run_susie_rss.R` off `dc4bbd2`,
  scoped to that one deleted line plus the comment reword. **SPENT.**
* **AUTH-K1-TEST** — edit of the pre-existing
  `tests/m3/test_ld_read_path.py::test_path2_ld_overlap_zero_fallback_is_observable_and_read`
  parity assertion, in the STRENGTHENING direction. The assertion was
  **INVERTED, not deleted**, so the semantics are pinned in both directions.
  **SPENT.**

**The new freeze pin is `bf04199`.** The forward gate is

```
git diff --exit-code bf04199 -- src/legacy/region_analysis/scripts/run_susie_rss.R
```

⚠ **SUPERSEDED 2026-08-06 by `quick-260806-sr4`** (`AUTH-SR4-RESCOPE`): the forward gate is now `pytest tests/m3/test_source_freeze_pins.py` — a **CODE** pin, not a byte pin — and the constants are `FROZEN_R_CODE_REV` / `FREEZE_CODE_REF`, both **import aliases** of the single `R_CODE_REF` in `tests/m3/test_source_freeze_pins.py`. The historical sentences around this note are left exactly as written. See `DEC-2026-08-06-sr4-freeze-scope`.

Re-pinned code-side in commit 2 of `quick-260806-pd3`:
`tests/m3/test_finemap_receipt_early_exit.py::FROZEN_R_REV`,
`tests/m3/test_qtl_coloc_allele_join.py::FREEZE_REF`,
`src/snakemake/scripts/ld_allele_join.R:33` and `:58`, and the live prose in
`src/snakemake/rules/finemap.smk`. ⚠ **`PRE_K1_REF` (`dc4bbd2`) in
`tests/m3/test_variant_catalog_fallback_legacy_semantics.py`, `PRE_K1_SMK_REF`
(`63453db`), and both `PRE_CHANGE_REF` constants are DIFFERENTIAL SUBSTRATES,
not pins — they must NEVER be re-pinned.** `test_qtl_coloc_allele_join.py:1296`
keeps `dc4bbd2` because it is a HISTORICAL record of the pin in force when
AUTH-b77-01 was granted; it was annotated, not rewritten.

**Gate row effect.** `m3-04c-BLAST-RADIUS.md:133-144` row **"Publishing the
panel provenance" (I, J, K) moves PARTIAL → CLEARED.** This is the only gate row
affected. No PIP, credible set, `ld_overlap`, `ld_status` or
`d3b_ld_z_consistency_s` moves, and that is asserted mechanically rather than
assumed. Track A is untouched.

**What was proven, and what was NOT.** The closure is proven on **source text
and receipt fixtures** by
`tests/m3/test_variant_catalog_fallback_legacy_semantics.py` (11 tests, 0 skips:
one-assignment-site, whole-block containment, five byte-identical
MUST-NOT-MOVE regions, a symbol-scoped diff shape, plus permanent negative
controls NC-K1/NC-K2). **NO before/after region-JSON diff was performed**, and
none was possible: **0** JSONs on this node carry `ld_overlap_zero_fallback`, so
no artifact here was ever produced from an m3-04c-window tree. The change is
INERT on today's artifacts.

⚠ **CENSUS CORRECTION.** The "1,957" figure below was never reproducible as
written, and a planning-time re-count of "44" was also wrong — it used a
`grep -r`, which does **not** follow the `results/legacy/region_analysis`
symlink. A first `grep -R` re-count of "1,944" was ALSO wrong — it swept the
whole repo, picking up 35 non-region files (17 under
`.planning/debug/stage2_narrow_validation/`, 18 under `results_lsweep_*.bak/`)
plus `.planning/HANDOFF.json`. **Measured 2026-08-06, scoped to the region tree:
1,909** region JSONs carry `variant_catalog_fallback` — **1,900 `false`** and
**9 `true`**. This reconciles: `1,909 + 687 key-absent = 2,596` total region
JSONs, and `1,909 + 35 + 1 = 1,945` for the unscoped sweep. All 9 `true`
ones are AFR (`RAD50_peak__tile1` and eight `PYHIN1_1q23` tiles) and **none**
carries `ld_overlap_zero_fallback`, i.e. every one of them is a genuine
**Path-1** revert. A further **687** of the 2,596 JSONs under
`results/legacy/region_analysis` carry the key not at all. So `true` already
meant Path-1 on real artifacts, which is precisely why the Path-2 overload had
to go.

**Decoder-ring coherence, fixed in the same closure.** After K-1 a real Path-2
revert emits `variant_catalog_fallback: false` + `ld_overlap_zero_fallback:
true`, which the four-outcome `variant_catalog_fallback_cause` decoder rendered
as `none` — false, because Path 2 *did* fire. The decoder gained a **fifth**
token, `path2_ld_overlap_zero_RETRY`;
`path2_ld_overlap_zero_NO_NUMERIC_CAUSE` is retained as a **forensic marker**
for the m3-04c window and is unreachable from any tree at or after `bf04199`.

---

### THE ORIGINAL DEFERRAL, PRESERVED

The surfaced-then-authorized record is kept below in full, deliberately: the
STOP was correct, and the record of WHY two authorizations were needed is the
durable part.

**Logged:** 2026-08-06 (quick-260806-b77). **Status at the time: DEFERRED —
PREPARED, not executed.** Not blocking. This entry carries the exact diff, the
blast radius, the re-freeze obligation and both authorizations, so the work is
ready to run the moment it is authorized.

**The finding (`m3-04c-BLAST-RADIUS.md` row K).** `variant_catalog_fallback` is
a **pre-existing** key. All **1,957** legacy region JSONs carry
`variant_catalog_fallback: false` and **no** `ld_overlap_zero_fallback` key at
all. m3-04c's Path-2 parity change made the `ld_overlap == 0` retry set
`variant_catalog_fallback <- TRUE` **with no numeric cause**, so a before/after
diff of those 1,957 JSONs shows a `false -> true` flip that a reader will chase.
(`ld_overlap_zero_fallback` **is** genuinely additive and is fine.)

**WHY IT COULD NOT BE CLOSED BY `quick-260806-b77` — two independent blockers,
both re-derived at HEAD during execution:**

1. **Every assignment site is inside a FROZEN file.** All six
   `variant_catalog_fallback` sites live in
   `src/legacy/region_analysis/scripts/run_susie_rss.R`:
   `:787` (init `FALSE`), `:916` (the **Path-1** AFR empty-subset revert, `TRUE`),
   `:936` / `:968` (the `no_variants` / `too_many_variants` early-exit emits),
   `:1013` (the **Path-2** mutation, `TRUE`), `:1208` (the success-JSON emit).
   That file is **RE-FROZEN at `dc4bbd2`** and the `260805-o7o` unfreeze is
   **SPENT**.
2. **A PRE-EXISTING test MANDATES the exact line the fix deletes.**
   `tests/m3/test_ld_read_path.py:451-453`, inside
   `test_path2_ld_overlap_zero_fallback_is_observable_and_read`, asserts
   `"variant_catalog_fallback <- TRUE" in branch` for the Path-2 brace block.
   Deleting the line makes that test RED, and no pre-existing test may be
   edited without a named authorization (`AUTH-o7o-01` was **not** inherited).

So K needs **two** authorizations, not one. Landing the edit anyway would have
violated two freezes at once.

### 1. The exact minimal diff (against `dc4bbd2`)

```diff
--- a/src/legacy/region_analysis/scripts/run_susie_rss.R
+++ b/src/legacy/region_analysis/scripts/run_susie_rss.R
@@ -1005,10 +1005,9 @@
     subset <- copy(subset_base)
     used_variant_catalog <- FALSE
     # m3-04c Task 1b / HIGH-2: this revert used to leave NO distinguishing
     # signal -- used_variant_catalog went FALSE exactly as it does on the Path-1
     # (AFR empty-filtered-subset) revert, and variant_catalog_fallback was never
     # set. Both flags are now recorded and both are read by the per-region
     # estimate_s log. Science behaviour is UNCHANGED: still one retry against
     # subset_base. Only observability changes.
-    variant_catalog_fallback <- TRUE
     ld_overlap_zero_fallback <- TRUE
     attempt <- attempt + 1
     next
```

**ONE line deleted.** `:787` (init), `:916` (the Path-1 mutation), `:936` /
`:968` (the early-exit emits) and `:1208` (the success emit) **do not move**.
`ld_overlap_zero_fallback <- TRUE` at `:1014` stays, as do
`subset <- copy(subset_base)` and `attempt <- attempt + 1`. The comment above
the deleted line should be reworded in the same edit (it currently narrates the
parity that is being withdrawn).

### 2. The blast radius of applying it

* **Science is UNCHANGED.** The Path-2 branch still reverts to `subset_base` and
  still retries exactly once. Only a **reporting flag** moves.
* `variant_catalog_fallback` recovers its **legacy meaning** — "the AFR
  variant-catalog empty-subset revert (Path 1) fired" — so a before/after diff
  of the 1,957 legacy JSONs no longer shows a causeless `false -> true` flip.
* **Nothing becomes invisible.** `ld_overlap_zero_fallback` remains the Path-2
  discriminator, is emitted in the success JSON (`:1209`), and is read by the
  per-region receipt in `finemap.smk`. The pair still distinguishes the two
  reverts; only the *legacy* half of the pair stops being overloaded.
* **No number moves.** No PIP, credible set, `ld_overlap`, `ld_status` or
  `d3b_ld_z_consistency_s` depends on this flag. Track A is untouched.

### 3. What re-freezing means afterward

The unfreeze is **single-use**. After the edit, re-pin `run_susie_rss.R` at the
new SHA and the forward gate becomes

```
git diff --exit-code <new-sha> -- src/legacy/region_analysis/scripts/run_susie_rss.R
```

⚠ **SUPERSEDED 2026-08-06 by `quick-260806-sr4`** (`AUTH-SR4-RESCOPE`): the forward gate is now `pytest tests/m3/test_source_freeze_pins.py` — a **CODE** pin, not a byte pin — and the constants are `FROZEN_R_CODE_REV` / `FREEZE_CODE_REF`, both **import aliases** of the single `R_CODE_REF` in `tests/m3/test_source_freeze_pins.py`. The historical sentences around this note are left exactly as written. See `DEC-2026-08-06-sr4-freeze-scope`.

replacing the current `dc4bbd2` gate everywhere it is asserted (the task plans,
`tests/m3/test_finemap_receipt_early_exit.py::FROZEN_R_REV`, and the standing
verification checklist).

⚠ **Spend the window once.** The still-outstanding `ld_allele_join.R` extraction
follow-up recorded in `260805-w7u-SUMMARY.md` — replacing
`run_susie_rss.R:220-323` with
`source("src/snakemake/scripts/ld_allele_join.R")` — should be considered for
the **same** unfreeze window rather than spending a second one. That follow-up
carries its own containment requirement (an `identical()`-on-the-whole-
`load_ld_matrix`-result proof at `allele_aware` TRUE **and** FALSE), so pairing
them means one unfreeze, one re-pin, two containment proofs.

### 4. The two authorizations, named

**(a) An unfreeze of `src/legacy/region_analysis/scripts/run_susie_rss.R`** off
`dc4bbd2`, scoped to the single-line deletion above (plus the comment reword),
with a re-pin obligation at the new SHA.

**(b) An `AUTH`-style authorization to edit the pre-existing test**
`tests/m3/test_ld_read_path.py::test_path2_ld_overlap_zero_fallback_is_observable_and_read`,
whose `:451-453` parity assertion **mandates the very line being deleted**.

The authorization must require that the edit **STRENGTHENS** rather than
weakens the assertion — mirroring the two-part shape of `AUTH-o7o-01`. Concretely,
inside the Path-2 brace block:

```python
assert "ld_overlap_zero_fallback <- TRUE" in branch          # unchanged
assert "variant_catalog_fallback <- TRUE" not in branch, (   # NEW, replaces :451-453
    "Path 2 must NOT set the legacy variant_catalog_fallback key (K-1): it is a "
    "pre-existing key whose meaning is the Path-1 AFR empty-subset revert"
)
```

so the NEW semantics are pinned in **both** directions — Path 2 still records
itself, and it no longer overloads the legacy key. The `:449-450` docstring and
the Path-1 half of the test (`:419-420`, `:916`) stay as they are, because Path
1 legitimately sets both.

### The fork, stated neutrally

| Option | Effect | Argument |
|---|---|---|
| **A — leave it (shipped today), documented** | The `false -> true` flip stays. It is explained by the decoder ring landed in `finemap.smk`'s receipt comment AND emitted at runtime as `variant_catalog_fallback_cause` (`path2_ld_overlap_zero_NO_NUMERIC_CAUSE` vs `path1_variant_catalog_empty_subset` vs `key_absent`). | Zero freeze spend, zero risk, and the phantom is now **self-explaining at the place a reader diffing JSONs actually looks**. Costs: the key remains overloaded, so any future automated before/after comparison must special-case it. |
| **B — restore the legacy semantics** | One line deleted; the key means what all 1,957 legacy JSONs mean by it. | Correct. A pre-existing key should not silently change meaning. Costs: an unfreeze **and** a pre-existing-test authorization, and the re-pin obligation above. |

**Recommendation if asked:** **B**, bundled with the `ld_allele_join.R`
extraction into one unfreeze window, so the freeze is opened once rather than
twice. Until then A is honest — the decoder ring is landed and tested
(`tests/m3/test_finemap_receipt_early_exit.py::test_the_variant_catalog_fallback_cause_token_explains_the_phantom`,
4 parametrised cases) — but it is a **mitigation of K, not its closure**.

**This needs one decision from Carter and is otherwise ready to execute.**

## K-2 DEFERRED (STILL OPEN) — the `ld_allele_join.R` extraction was evaluated against an OPEN freeze window and declined

**Logged:** 2026-08-06 (`quick-260806-pd3`). **Status: DEFERRED — evaluated on
the merits, not deferred by default.** Not blocking.

**The proposal.** Replace the nested closure `match_indices_allele_aware`
(`run_susie_rss.R:220-323`) with
`source("src/snakemake/scripts/ld_allele_join.R")`, eliminating a deliberate
second implementation of the allele-aware join. It was recorded in
`260805-w7u-SUMMARY.md` and in `ld_allele_join.R` section (d) as something to
bundle into "the next time the freeze is opened for an independent reason", on
**freeze-economy** grounds.

**That trigger fired on 2026-08-06** — `quick-260806-pd3` opened a window on
`run_susie_rss.R` for K-1 — **and the rider was declined.** Four findings, all
measured during planning and re-verified at execution:

1. **VERIFIED, and decisive.** `run_susie_rss.R` contains **ZERO `source()`
   calls today** (`grep -c "source(" → 0`). The extraction would introduce a
   **first-of-its-kind runtime file dependency** on the exact code path the
   ~11-day / $385–1,084 AoU fire exercises. A failed `source()` at fire time is
   a catastrophic, expensive failure mode **that does not exist today**.
2. **VERIFIED.** The duplication is **already** drift-guarded on **every suite
   run** by `tests/m3/test_qtl_coloc_allele_join.py`'s differential agreement
   test plus NC-2f / NC-2g, which body-walk the SHIPPED closure out of the real
   source. **The benefit is style, not safety.**
3. **VERIFIED — and the original brief's premise was WRONG.** The brief stated
   that `run_qtl_coloc.R:164` solves path resolution "with a `--ld-allele-join`
   CLI arg threaded from `qtl_coloc.smk`". It does not. `--ld-allele-join`
   (`run_qtl_coloc.R:62`) is a **boolean flag**; the PATH is resolved
   **script-relatively** at `run_qtl_coloc.R:153`
   (`file.path(.script_dir(), "ld_allele_join.R")`). `run_susie_rss.R` lives in
   `src/legacy/region_analysis/scripts/`, so `.script_dir()` would **not** find
   the shared file — a genuinely **new** path mechanism (a new CLI argument
   threaded from `finemap.smk`, or a repo-root walk) would be required. **That
   is wider than the brief assumed, not narrower.**
4. **ANSWERED.** `.up`, `.usable`, `.allele_counts0`
   (`run_susie_rss.R:210-218`) are referenced ONLY at `:223` and `:237-249`, all
   inside the closure's own body, whose sole call site is `:332`. **Nothing else
   in `load_ld_matrix` uses them**, so removal is technically feasible. This
   removes an objection but supplies no justification.

**Verdict: DEFER.** Point 4 clears an obstacle; points 1 and 3 stand.
**Freeze economy is NOT sufficient justification to accept fire-path risk.**

**Any future attempt must satisfy all three conditions:**

* **(i) a FAIL-CLOSED-AND-LOUD design.** A missing or unsourceable shared file
  must STOP with a named error and must **never** degrade to a position-only
  match — that degradation **IS finding H**.
* **(ii) an `identical()`-on-the-whole-`load_ld_matrix`-result proof** at
  `allele_aware` **TRUE and FALSE** against the then-current pin (`bf04199` as
  of 2026-08-06).
* **(iii) a re-freeze re-pin** at the new SHA, after which
  `git diff --exit-code <new-sha> -- run_susie_rss.R` becomes the forward gate.

⚠ **SUPERSEDED 2026-08-06 by `quick-260806-sr4`** (`AUTH-SR4-RESCOPE`): the forward gate is now `pytest tests/m3/test_source_freeze_pins.py` — a **CODE** pin, not a byte pin — and the constants are `FROZEN_R_CODE_REV` / `FREEZE_CODE_REF`, both **import aliases** of the single `R_CODE_REF` in `tests/m3/test_source_freeze_pins.py`. The historical sentences around this note are left exactly as written. See `DEC-2026-08-06-sr4-freeze-scope`.

## ✅ K-3 CLOSED — the wrong census number is CORRECTED; the comment fix cost NO re-pin

**Closed:** 2026-08-06 by `quick-260806-sr4`, commit `656529a`.
**Status: ✅ CLOSED. `AUTH-SR4-K3` GRANTED (Carter, 2026-08-06) and SPENT.**

`src/legacy/region_analysis/scripts/run_susie_rss.R:1018-1019` now reads
**`1,909`** and **`1,900`** in place of `1,944` and `1,935`. The diff vs
`bf04199` is **one hunk, two `-`/`+` pairs, all four lines comments**, differing
only in those digits; `Rscript -e 'parse(...)'` returns `PARSE_OK`. Containment
is re-asserted permanently in-suite by
`tests/m3/test_source_freeze_pins.py::test_the_k3_edit_touched_only_two_comment_lines`,
so a widened unfreeze could not be discovered only by reading a summary.

⚠ **THE ONE LINE THAT MATTERS.** The remedy below says this "requires: a named
unfreeze, the standing re-pin obligation". **It now requires NEITHER.**
`quick-260806-sr4` rescoped the `run_susie_rss.R` freeze from **bytes** to
**CODE** under `AUTH-SR4-RESCOPE`, so **the freeze no longer covers comments at
all**. The pin **was not moved** — `bf04199` remains valid *across* the
correction, and keeps its stronger meaning ("no CODE has moved since the K-1
closure") rather than degrading to "nothing has moved since yesterday's typo
fix". Observed on one tree: the OLD gate
`git diff --exit-code bf04199 -- run_susie_rss.R` is **RED**, the NEW gate
`pytest tests/m3/test_source_freeze_pins.py -k k3` is **GREEN**.

**The deferral's own reasoning was the bug, not the excuse.** K-3 exists because
a byte-scoped freeze made shipping a **known falsehood** cheaper than correcting
a comment. That is now recorded as `DEC-2026-08-06-sr4-freeze-scope`, with the
byte pin rejected by name.

**Nothing about the underlying science moved.** Every qualitative conclusion in
the preserved entry below stands unchanged; only the two census digits changed.

### THE ORIGINAL DEFERRAL, PRESERVED

## K-3 DEFERRED (STILL OPEN) — a WRONG CENSUS NUMBER is shipped inside the re-frozen `run_susie_rss.R` comment

**Logged:** 2026-08-06 (quick-260806-pd3, found by the verifier AFTER commit 2 had
landed and the file was already re-frozen at `bf04199`). **Status: DEFERRED —
disclosed, NOT fixed. Cosmetic; no behaviour and no number depends on it.**

**The defect.** `src/legacy/region_analysis/scripts/run_susie_rss.R:1018-1019`
states the legacy census as **"1,944 measured 2026-08-06 -- 1,935 false"**. That
count is **35 too high**: it came from an unscoped `grep -R` over the whole repo,
which also swept 17 fit JSONs under `.planning/debug/stage2_narrow_validation/`
and 18 under `results_lsweep_*.bak/`, plus `.planning/HANDOFF.json`.

**The correct figures**, scoped to the region tree and reconciled three ways:

| Quantity | Correct | Shipped in the R comment |
|---|---|---|
| region JSONs carrying `variant_catalog_fallback` | **1,909** | 1,944 ✗ |
| — of which `false` | **1,900** | 1,935 ✗ |
| — of which `true` | **9** | 9 ✓ |
| region JSONs with the key absent | **687** | 687 ✓ (elsewhere) |
| total region JSONs | **2,596** | 2,596 ✓ (elsewhere) |
| carrying `ld_overlap_zero_fallback` | **0** | 0 ✓ |

Reconciliation: `1,909 + 687 = 2,596`; `1,909 + 35 + 1 = 1,945` (the unscoped
sweep). The R comment is additionally **self-inconsistent** with the `2,596` and
`687` it cites in the same breath, since `2,596 − 687 = 1,909`, not 1,944.

**Every qualitative conclusion is UNAFFECTED.** All 9 `true` artifacts are still
AFR (`RAD50_peak__tile1` + eight `PYHIN1_1q23` tiles), still carry **zero**
`ld_overlap_zero_fallback`, and are therefore still genuine **Path-1** reverts —
which is the entire argument for why the Path-2 overload had to go. The K-1
closure stands.

**THE THREE NON-FROZEN SITES WERE CORRECTED IN THE SAME SESSION** (the docs
commit): `src/snakemake/rules/finemap.smk:541`,
`tests/m3/test_finemap_receipt_early_exit.py:558`, and the census paragraph in
this file. **Only the frozen R comment still carries the wrong figure**, so the
repository is now internally inconsistent at exactly one place, deliberately and
on the record rather than silently.

**Why it was not fixed.** `run_susie_rss.R` was RE-FROZEN at `bf04199` by commit
2 and **AUTH-K1-UNFREEZE is SPENT**. Correcting a comment is not a licence to
re-open a freeze; doing so would also force a second re-pin cascade across
`FROZEN_R_REV`, `FREEZE_REF`, `ld_allele_join.R`, `finemap.smk` and this file for
a cosmetic gain.

**The remedy, when a freeze window next opens for an independent reason** (bundle
it with [[K-2]] and any future K-1-class work — one window, one re-pin):
change `1,944` → `1,909` and `1,935` → `1,900` at `:1018-1019`. Two numbers, one
line each, no logic. Requires: a named unfreeze, the standing re-pin obligation,
and nothing else — there is no containment proof to construct because no
executable assertion reads these digits.

## ✅ AUTH-b77-01 GRANTED AND APPLIED — a PRE-EXISTING test pinned `finemap.smk` at `7b1025d` FOREVER

**Logged:** 2026-08-06 (quick-260806-b77). **Status: ✅ GRANTED 2026-08-06 by
the coordinator under Carter's standing "proceed autonomously" instruction, and
APPLIED in commit `13b82ef`.** The surfaced-then-authorized sequence is preserved
below in full, deliberately: the STOP was correct and the record of WHY the
authorization was needed is the durable part.

⚠ **SCOPE OF THE GRANT: ONE assertion in ONE file.** It does NOT reopen the
no-pre-existing-test-edits rule for anything else, it does NOT unfreeze
`run_susie_rss.R`, and it does NOT authorize editing
`tests/m3/test_ld_read_path.py:451` (K-1's second authorization, still
OUTSTANDING). Any other pre-existing test going red remains a STOP-and-surface.

**Verified before the grant** (independently re-run by both the coordinator and
the executor):

```
git diff 7b1025d HEAD -- src/snakemake/rules/finemap.smk | grep -c region_id   -> 0
git diff 7b1025d HEAD -- src/snakemake/rules/finemap.smk | wc -l              -> 128
git diff 6b427bc HEAD -- finemap.smk | grep -c "region_id=lambda"             -> 0
pytest tests/m3/test_occlusion_lockstep_wiring.py -q                          -> 16 passed
```

i.e. the 128-line diff mentions `region_id` nowhere, `params.region_id` is
byte-unchanged, and the **PRIMARY guard rail is intact and green**:
`test_occlusion_lockstep_wiring.py::test_params_region_id_is_untouched`, which
asserts `region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],`
character-for-character. The assertion that was edited is a redundant SECONDARY
pin.

---

### THE ORIGINAL SURFACE, PRESERVED

At the time of surfacing: no pre-existing test had been edited, and `tests/m3`
was **805 passed / 1 failed / 31 skipped** on this tree, the one failure being
this.

**The failing test:**
`tests/m3/test_qtl_coloc_allele_join.py::test_params_region_id_is_not_declared_here`
(`:1280-1290`), created by `260805-w7u` Task 2 (commit `1815bfd`) — i.e. **before**
this task's baseline `6b427bc`.

```python
def test_params_region_id_is_not_declared_here():
    """``finemap.smk:349-350`` is out of scope and must not be shadowed."""
    text = QTL_COLOC_SMK.read_text()
    assert "region_id=lambda" not in text
    diff = subprocess.run(
        ["git", "diff", PRE_CHANGE_REF, "HEAD", "--",
         "src/snakemake/rules/finemap.smk"],
        cwd=PROJECT_ROOT, capture_output=True, text=True,
    )
    assert diff.stdout.strip() == ""        # <-- PRE_CHANGE_REF == "7b1025d"
```

**What it actually asserts vs what it means to assert.** Its docstring and its
name say the subject is `finemap.smk`'s `params.region_id` — that
`260805-w7u`'s *coloc* work must not shadow it. Its **implementation** asserts
that `src/snakemake/rules/finemap.smk` is **byte-identical to `7b1025d`
forever**, for every future task. That is a TASK-SCOPE guard baked into the
permanent suite: exactly the "a coverage assertion can be a false invariant"
shape this arc keeps catching, one level up.

**Attribution, measured — `git diff 7b1025d <rev> -- src/snakemake/rules/finemap.smk`:**

| rev | diff lines | this test |
|---|---|---|
| `6b427bc` (b77 baseline) | 0 | GREEN |
| `9b2d431` (b77 plan doc) | 0 | GREEN |
| `9c0c67b` (b77 T1 — did not touch `finemap.smk`) | 0 | GREEN |
| `d8cfa53` (b77 T2 — the FINDING J receipt edit) | 72 | **RED** |

**Why this is unavoidable for findings J and L.** Finding **J** lives in the
pair (frozen `run_susie_rss.R` early-exit writers) x (the `finemap.smk`
receipt). The R half is RE-FROZEN at `dc4bbd2` with its unfreeze SPENT, so **J
can only be closed by editing `finemap.smk`** — which is precisely what the
`quick-260806-b77` plan mandates and lists in its `files_modified`. Finding
**L**'s coverage WARN lives at `finemap.smk` module scope for the same reason.
**Reverting would not avoid this test; it would only discard J and L and leave
the same authorization needed to ever close them.**

**⛔ NOT FIXED HERE.** `AUTH-o7o-01` was not inherited and no pre-existing test
may be edited without a named authorization. The plan's `<verified_anchors>`
enumerated four pre-existing tests that constrain these fixes and **did not name
this one** — recorded as a plan-fact gap in `260806-b77-SUMMARY.md`, not worked
around.

### The authorization requested, and the exact minimal STRENGTHENING edit

**AUTH-b77-01:** authorize editing
`tests/m3/test_qtl_coloc_allele_join.py::test_params_region_id_is_not_declared_here`
so its assertion matches its own stated subject. The edit must **STRENGTHEN**,
not weaken — mirroring the two-part shape of `AUTH-o7o-01`:

```diff
     diff = subprocess.run(
         ["git", "diff", PRE_CHANGE_REF, "HEAD", "--",
          "src/snakemake/rules/finemap.smk"],
         cwd=PROJECT_ROOT, capture_output=True, text=True,
     )
-    assert diff.stdout.strip() == ""
+    # The SUBJECT is params.region_id, not the whole file. A whole-file pin was
+    # a TASK-SCOPE guard for 260805-w7u and made every later finemap.smk change
+    # -- including the FINDING J receipt fix, which CANNOT live anywhere else
+    # because run_susie_rss.R is frozen -- unlandable. Pin the thing named.
+    assert "region_id" not in diff.stdout, (
+        "a finemap.smk change touched params.region_id, which is out of scope "
+        f"for every task since {PRE_CHANGE_REF}:\n{diff.stdout}"
+    )
```

**Why the replacement is STRICTLY STRONGER on its own subject.** The whole-file
pin could only ever say "something changed"; the replacement says **which**
change is forbidden and would fail on a `params.region_id` edit *even in a
commit that also legitimately changed the receipt* — a case the old assertion
could not distinguish. It is also the exact check the `quick-260806-b77` plan
already specifies as an acceptance criterion
(`git diff 6b427bc HEAD -- src/snakemake/rules/finemap.smk | grep -c region_id`
must be `0`; **measured `0` on this tree**), so the two agree by construction.

The first assertion (`"region_id=lambda" not in qtl_coloc.smk`) and the whole of
`test_run_susie_rss_is_zero_diff_vs_the_freeze` are **untouched**.

**Until AUTH-b77-01 is granted, `tests/m3` does not reach `0 failed`, and the
full-suite gate for `quick-260806-b77` is reported as NOT MET.** Nothing else in
either suite is red: `tests/phase2` is `136 passed / 1 skipped / 0 failed`, and
the 31 `tests/m3` skips are unchanged and pre-existing.

### WHAT WAS ACTUALLY APPLIED (2026-08-06, `13b82ef`)

Exactly the authorized change, in `tests/m3/test_qtl_coloc_allele_join.py`, and
nothing else in that file:

* **KEPT verbatim:** `assert "region_id=lambda" not in text` (over `qtl_coloc.smk`)
  — this test's original subject.
* **REPLACED:** `assert diff.stdout.strip() == ""` →
  `_assert_finemap_diff_leaves_region_id_alone(diff.stdout)`, whose body is
  `assert "region_id" not in diff_text` with a message naming the guard, the
  reason `params.region_id` is out of scope, and the offending diff.
* **DOCSTRING UPDATED** to state what the assertion now enforces, to record
  `AUTH-b77-01` and its one-line reason (a fixed-SHA whole-file pin cannot
  distinguish a regression from a legitimate edit, so it was narrowed to the
  stated subject and thereby made STRONGER on it), and to point at the PRIMARY
  guard rail in `test_occlusion_lockstep_wiring.py`.
* **ADDED:** `FINEMAP_SMK` (read-only) and the permanent in-suite negative
  control `test_nc_auth_b77_01_the_narrowed_pin_still_catches_a_region_id_edit`.

**THE NEGATIVE CONTROL — OBSERVED RED. This was the price of the edit.** The
control builds a throwaway git repo from a COPY of `finemap.smk`, shadows the
directive (`REGION_SAFE_TO_ID[wildcards.region]` → `wildcards.region`), and
drives the narrowed assertion with the resulting real `git diff`. With
`pytest.raises` temporarily removed so the failure surfaces raw:

```
E  AssertionError: a finemap.smk change touched region_id.
   run_finemap.params.region_id has been out of scope for every task since
   7b1025d ... Offending diff:
E    @@ -387,7 +387,7 @@ rule run_finemap:
E    -        region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],
E    +        region_id=lambda wildcards: wildcards.region,
E  assert 'region_id' not in 'diff --git ...rd default\n'
```

The control additionally asserts, in the same run, that the REAL diff still
passes AND is **non-empty** (so that half is not vacuous), and that
`src/snakemake/rules/finemap.smk` in the working tree is byte-unchanged
MID-CONTROL — the same discipline `260805-w7u`'s NC-2g used against the frozen R
source. Verified after: `git status --short -- src/snakemake/rules/finemap.smk`
empty; `test_occlusion_lockstep_wiring.py` 16 passed.

**Both suites after the edit:** `tests/m3` **806 passed / 0 failed / 31 skipped**;
`tests/phase2` **136 passed / 1 skipped / 0 failed**. Gate MET.

⚠ **This is the SEVENTH assertion in this arc found structurally incapable of
doing its stated job — and unlike the other six, WE WROTE IT, one task ago
(`260805-w7u`, `1815bfd`, 2026-08-05).** The lesson generalises past this file: a
scope assertion must name its SUBJECT, not its blast radius. `diff == ""` against
a fixed SHA is never a contract about correctness; it is a countdown to the next
legitimate edit.

## ⚠ SR4-OPEN — FIVE files `HANDOFF.json` calls "frozen at `bf16289`" have MOVED. A QUESTION FOR CARTER, deliberately NOT answered.

> **✅ DISPOSED 2026-08-11 — NEVER ACTUALLY FROZEN.**
> `DEC-2026-08-11-sr4-disposition`. Carter's call: the handoff's
> "frozen/pinned at `bf16289`" language for the five files was **wrong** and is
> **corrected, not defended**. **No drift review is required.**
>
> ⚠ **The `Status: OPEN` line immediately below is SUPERSEDED**, as is
> *"THE QUESTION FOR CARTER — not answered here"*. Both are **preserved
> verbatim for the record**, along with the rest of this entry.
>
> **Evidence:** `.planning/quick/260811-pmv-sr4-open-evidence-dossier-were-the-five-/260811-pmv-DOSSIER.md`
> (`f78bbc1`, `399c50f`, `2b13dce`) — `bf16289` is a `docs(handoff)`
> session-close commit that touched **none** of the eight, so it was a bookmark
> rather than an act of freezing; there are zero register declarations for any
> of the five and zero `bf16289` enforcement at **every one** of the 8 drift
> commits; all 8 drift commits are traceable to a reviewed task SUMMARY; and the
> label was COLLECTIVE — a **status report**, not a prohibition.
>
> ⚠ **Both contrary facts stand, stated rather than smoothed.** For **F1–F4**
> that collective label (`2bda675`, 2026-08-03) **did predate** the drift —
> genuine contrary evidence, bounded by three things: it is a status report and
> not a freeze instruction, it lives in a handoff narrative and not in the
> decision register, and it was enforced by measured zero at each drift commit.
> **F5** (`pipeline.schema.yaml`) was **never in the "7 pinned files" roster**
> and its only label postdates all of its drift, so there is nothing to review.
>
> **Consequences:** no drift review; the three genuinely 0-diff files stay gated
> by `tests/m3/source_freeze.py`; and **NO NEW PIN** is created — none of the
> five is added to `PY_FROZEN_RELS`. ⚠ The residual live sites
> `.planning/STATE.md:15` and `.planning/ROADMAP.md:1077` are a registered
> follow-up, out of the write scope of the task that landed this banner; the
> dated historical `>` blocks are **NOT** correction sites.

**Logged:** 2026-08-06 (`quick-260806-sr4`). **Status: OPEN — registered, NOT
resolved either way.**

`.planning/HANDOFF.json:14` states *"All 7 pinned files 0-line diff vs
`bf16289`"*. **That claim is FALSE for 5 of 8 files.** MEASURED at `1b5b8c6`
with `git diff --numstat bf16289 HEAD`:

| File | Diff vs `bf16289` | Last touched | Handled |
|---|---|---|---|
| `src/python/plink_ld_to_npz.py` | **0** | 2026-07-03 | ✅ **GATED** |
| `src/python/condition_ld_matrix.py` | **0** | 2026-07-07 | ✅ **GATED** |
| `src/python/occlusion_span_filter.py` | **0** | 2026-07-15 | ✅ **GATED** |
| `src/python/occlusion_manifest.py` | +46 / −8 | 2026-08-04 (`bf963df`) | ⚠ **MOVED — not gated** |
| `src/python/occlusion_present_rate_scan.py` | +154 / −21 | 2026-08-04 (`fac9a93`) | ⚠ **MOVED — not gated** |
| `src/python/drop_occluded_from_sumstats.py` | +97 / −24 | 2026-08-04 (`bf963df`) | ⚠ **MOVED — not gated** |
| `src/scripts/ld_npz_to_rds.R` | +313 / −62 | 2026-08-05 (`57b381f`) | ⚠ **MOVED — not gated** |
| `src/snakemake/schemas/pipeline.schema.yaml` | +119 / −0 | 2026-08-06 (`2563451`) | ⚠ **MOVED — not gated** |

**It is worse than it looks.** `bf16289` appears **nowhere** in `src/`, `tests/`,
`config/`, `Snakefile` or `scripts/` — until `quick-260806-sr4` there was
**literally zero enforcement** of any of these. The "freeze" was a per-task hand
check, and that ritual had been **reporting a claim that is false for five of
eight files**.

**Why three were gated and five were not.** `AUTH-SR4-EXTEND` covers only files
that are **measured 0-diff** against the pin. Gating a file that changed three
times in the last three days would manufacture exactly the nuisance-repin
timebomb the rescope exists to remove, and **declaring a moving file frozen is a
DECISION, not an inference.** So the three genuinely-unmoved modules became real
gates and the other five were deliberately left alone. A permanent test
(`test_the_handoff_frozen_claim_is_recorded_as_partly_false`) asserts the five
are **out** of the pinned set, so a future sweep cannot "helpfully" add them back
without a decision.

**THE QUESTION FOR CARTER — not answered here.** For each of the five: were they
**frozen and have since drifted** (in which case something was changed that
should not have been, and the drift needs review), or were they **never actually
frozen** (in which case `HANDOFF.json:14` should be corrected and they should
stop being described as pinned)? These are different problems with different
remedies, and choosing between them is a call about intent that no agent can
make from the diff alone.

**Nothing is blocked on the answer.** The three real gates are live either way.
