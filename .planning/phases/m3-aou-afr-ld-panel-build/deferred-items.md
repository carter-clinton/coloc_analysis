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
