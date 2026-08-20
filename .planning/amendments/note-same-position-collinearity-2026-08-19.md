# Note — same-position (split-multiallelic) rows and near-collinearity in the AFR native-plink LD panel

> **Status: INTERNAL RECORD. NOT part of any OSF amendment and NOT posted.** If this note is
> ever promoted to the public record, that is a separate, dated decision with its own entry in
> `.planning/DECISIONS.md`. Nothing here changes a pre-registered commitment.

**Provenance.** Surfaced by the §5 same-position measurement executed on the region-1 window
and the 21-region sample on 2026-08-19 (`.planning/debug/260819-supplement-results-as-received.md`),
and raised as a new issue in `§6` of
`.planning/debug/260819-SETH-C1C2C3-convergence-as-received.md` by the project's external
methodological reviewer. Recorded here rather than folded into the occlusion-gate
recalibration amendment, at his own explicit preference: *"If you think it belongs in a
separate note rather than this amendment, I agree — I would rather it be recorded somewhere
than folded in awkwardly."*

## The observation

Same-position rows in a plink `.bim` are alternate ALT alleles at ONE genomic site. A person
cannot carry two different ALTs of the same site on the same haplotype. The dosages of two
such rows are therefore **structurally anti-correlated**: their sample correlation `r` is
partly determined by the representation convention, not purely by population linkage
disequilibrium.

At the measured scale, the panel therefore contains a substantial population of
near-deterministic off-diagonal relationships.

## The measured scale

| Quantity | Value |
|---|---|
| Duplicate-position rows, all 21 sampled regions | ~7-11% of `n_rows`, stable across small / medium / large |
| Maximum per-site multiplicity observed | 21 (`m2_region_00111__sub07`, `m2_region_00060__sub12`) |
| Region 1 (`m2_region_00001`) | 8,358 duplicate rows at 2,645 duplicate sites; mean multiplicity 3.16; max 18 |
| Top region-1 sites | `chr1:10700080` (18), `chr1:10111044` (17), `chr1:5249031` (15) |

## What this is NOT

- **It is NOT fabrication.** The dosages really are anti-correlated. The LD is real as
  computed; no value is invented, imputed or coerced.
- **It is NOT the occlusion problem**, and it changes no conclusion in the clause-(d)
  recalibration. Occlusion is a coordinate-geometry property (a deletion's reference span
  covering a neighbour's position); this is a representation property of one site's alternate
  alleles. They co-occur in the same loci because both concentrate at complex indel sites, but
  they are different objects.
- **It is NOT a defect introduced by this pipeline.** A `.bim` row is biallelic by
  construction, so a correctly normalized split-multiallelic callset necessarily renders one
  k-allelic site as k same-position rows. This is a known property of split-multiallelic
  representation.

## What it IS — a fine-mapping consideration

SuSiE run on a region submatrix containing several same-position rows sees **near-collinear
predictors**. That is precisely the regime in which credible sets inflate (many members, low
per-variant posterior inclusion probability) or split across representation partners of one
underlying site. The same caution applies to any downstream method that assumes the LD matrix
is full-rank or well-conditioned on the analysed variant set.

The practical consequence for interpretation: a credible set whose members share a `(CHR,POS)`
should be read as ONE site with unresolved allele identity, not as several independent
candidate variants.

## Disposition

- Same-position rows are **RETAINED** in the panel. Merging them back into multiallelic
  records is not representable in plink, and `bcftools norm -m +` would move in the wrong
  direction (see the C1 adjudication in `DEC-2026-08-19-occlusion-recalibration-adopted`).
- No pre-registered commitment changes. No code changes.
- The **manuscript carries the caveat** for fine-mapping at multiallelic sites, stated in the
  methods/limitations rather than discovered by a reviewer.
- At panel closeout, the per-credible-set count of same-position members is worth reporting
  alongside the clause-(e) present-rate figure; both speak to the same question — what the
  representation does to the loci that matter, as opposed to the genome-wide aggregate.

Recorded now because an unrecorded observation becomes an unanswerable reviewer question
later.

**Cross-refs:** `.planning/debug/260819-SETH-C1C2C3-convergence-as-received.md` (§6);
`.planning/debug/260819-supplement-results-as-received.md` (PART 1a / PART 1b);
`.planning/DECISIONS.md` → `DEC-2026-08-19-occlusion-recalibration-adopted`;
`.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-XX.md`.
