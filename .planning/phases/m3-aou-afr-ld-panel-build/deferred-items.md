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
