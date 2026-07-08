> Policy decision — committed byte-verified 2026-07-08 (quick-260707-x8e). The body below
> (from "# Panel occlusion policy" onward) is Seth's authoritative record, SHA-256
> 42d701677ac8bc85d3b03f390413c4406ba65f3b11ab085350e560738ab209ef (5247 B); this header is
> excluded from the hash. Companions: m3_nan_conditioning_scientific_review.md (WHY NaN→0 is
> wrong), m3_region1_nan_geometry_verdict.md (WHAT the mechanism is — its open "exclude-vs-flag"
> policy-call section is CLOSED by this doc; still pending byte-faithful transfer),
> m3_region1_occlusion_hinge_check.md (the (CHR,POS) join-impact evidence, quick-260707-w78 / c4e0875).

# Panel occlusion policy — decision (exclude-in-lockstep + provenance)

**Decision:** for occluded variants (a real, sumstats-present variant whose LD is
structurally undefined because an overlapping deletion makes it uncallable in the AoU AFR
reference), **exclude in lockstep across BOTH the LD panel and the harmonized sumstats,
with an auditable provenance manifest.** Not NaN→0, not panel-only exclude, not flag.

## What the hinge check settled (HPC agent, read-only, no spend)
- Panel join to sumstats is **(CHR, POS)-only** (`snp_id_bridge.R`), so position presence
  decides membership.
- The 3-record tangle GRCh38 5922716/5922718/5922724 → GRCh37 5982776/5982778/5982784.
- Occluding **deletion 5982776: ABSENT** from sumstats. Occluded **SNP rs182965575
  (5982778, MAF ~0.014): PRESENT** in 7/9 traits with genuine effect estimates
  (e.g. t2d β=0.057, SE=0.041). Second occluded SNP 5982784: absent.
- → the "present" case is real: a testable GWAS variant is uncallable in the LD reference.

## Why each alternative is rejected
- **NaN→0 (dead).** Concrete harm now, not hypothetical: zeroing tells SuSiE that
  rs182965575 has r=0 with its common same-locus neighbors rs11120783 (MAF 0.21) and
  rs10864245 (MAF 0.34). That is a fabricated LD value for a variant whose true LD is
  undefined; SuSiE's credible-set placement would act on the fabrication.
- **Panel-only exclude (unsafe).** Orphans rs182965575 — present in sumstats, gone from
  panel → the (CHR,POS) join drops it or the fine-mapper errors on the missing LD row.
  The earlier "exclude = join-safest" lean was under-specified; it is only safe when the
  occluded variant is ALSO absent from the sumstats (which is not this case).
- **Flag (correct but heavier).** Flag and lockstep-exclude **converge on the same
  statistical outcome** — an undefined LD row cannot enter the SuSiE fit submatrix either
  way, so the variant is not fine-mappable at this locus regardless. Flag pays for that
  identical outcome with `.npz`→`.rds`→fit flag-propagation machinery and the "a flag
  nothing reads is worse than useless" failure mode. Lockstep-exclude is the simpler,
  honest realization of the same result — PROVIDED the provenance manifest does the
  bookkeeping the flag would have.

## The provenance manifest is load-bearing, not optional
Per dropped variant, log: variant ID + position (both builds), the occluding deletion +
its REF span, the locus, the traits in which the variant was present, and the reason
(reference-occlusion, undefined LD). This (a) keeps the dropped variant auditable and
recoverable for any non-LD analysis that legitimately could use it, (b) is the honest
record that a **real testable variant was lost to a reference artifact** — which is the
subject matter of the Angle-1/3 papers, so the manifest IS the genome-wide catalog seed,
and (c) satisfies the reviewer/pre-registration standard (nothing silently disappears).

## Independent corroboration (my check, stated with its caveat)
The occluded SNP's panel MAF on the pairwise-complete subset was ~0.0078 (pairs 3/4),
vs ~0.014 in the sumstats — the reference observes the minor allele at roughly HALF the
GWAS frequency, the direction the occlusion mechanism predicts (minor-allele carriers on
the deletion haplotype are missing → observed MAF depressed). Caveat: the GWAS AFR cohort
is not necessarily the AoU AFR cohort, so cohort differences confound the exact ratio;
this is directionally consistent, not a clean quantitative match.

## Scope of the fix (systemic, upstream)
The occluded SNP is a generic dbSNP variant appearing across many GWAS; the occlusion
comes from the AoU AFR `.bim` geometry. So the fix is:
1. **Upstream panel-build span-filter for all 276 regions** — detect deletion-spans-
   neighbor occlusion at panel build, not per-region patching.
2. **Lockstep sumstats-side drop at the m3-04 harmonization step** — the same variant set,
   dropped consistently, driven by the provenance manifest.
3. **OSF amendment-update describes exclusion + provenance, never zeroing.**

## Honest limitations (carried from the hinge check)
- Partial: only the 3-record tangle positions were in the committed record; the 5 direct
  pairs live in `m3_region1_nan_geometry_verdict.md`, which the HPC agent could not read
  (uncommitted — needs transfer). One present occluded variant already rejects the clean
  "absent" branch and mandates lockstep; the full list only ADDS cases, not changes policy.
- Matched on position (the join key); allele orientation not verified — irrelevant to the
  exclude decision, relevant only to effect-sign in any later use.

## Open (for Carter / next step)
- **Genome-wide present-rate is unknown and matters.** If most occluded variants are
  ABSENT from sumstats, lockstep-exclude rarely fires (small loss). If many are PRESENT
  like rs182965575, the pipeline is losing many real testable variants to a reference
  artifact — a larger effect that directly strengthens the Angle-1/3 quantification. The
  genome-wide scan should report this rate explicitly.
- Unblock the HPC agent: transfer/commit `m3_region1_nan_geometry_verdict.md` so it has
  the full 6-pair (11-variant) set for the manifest.