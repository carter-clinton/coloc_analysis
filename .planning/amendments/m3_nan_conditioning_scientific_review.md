> Seth review, 2026-07-07. Gates m3-06 (d9ccb55) as landed-but-not-trusted pending the region-1 2×2 diagnostic. Companion: osf-amendment-afr-native-ld-nan-psd-2026-07-03.md.

# Scientific review — is NaN→0 + PSD the right treatment for the AFR panel NaNs?

**Reviewer stance:** the code (`condition_ld_matrix.py`, `psd_utils.R`,
`write_conditioned_ld_npz.py`, landed at `d9ccb55`) faithfully implements the posted
amendment, and the amendment is internally consistent. That is compliance. This memo
asks the prior question the amendment does NOT settle: **is conditioning these entries
by `NaN→0` the methodologically correct thing to do at all?** Conclusion: the mechanism
behind the NaNs is mis-identified, and under the correct mechanism `NaN→0` is a
directionally wrong fill applied exactly where LD fidelity matters most. The
conditioning should be gated behind a one-step in-perimeter diagnostic that has not yet
been run.

--------------------------------------------------------------------------------
## 1. The stated mechanism is arithmetically impossible

The diagnostic + amendment describe the 12 NaN cells (6 symmetric pairs) as
"pairwise-undefined `r` — `0/0` among clustered low-MAF variants," implying a benign
quasi-random degeneracy. A pairwise Pearson `r` is `0/0` **only if one variant is
monomorphic on the sample subset non-missing at BOTH variants.** Test that against the
reported aggregates (N = 73122; MAF 0.005–0.02; F_MISS ≤ 0.05):

- Minor-allele carriers per variant: ~730 (MAF 0.005) to ~2870 (MAF 0.02).
- Pairwise-complete intersection under independent missingness: ~66,000 people.
- For a variant to be monomorphic on that intersection, ALL its carriers must land in
  the ~3,656-person set missing the partner variant.
- Probability under independent missingness: `0.05^(#carriers)` ≈ **10⁻⁹⁴⁷ (MAF 0.005)
  to 10⁻³⁷²⁹ (MAF 0.02).**

This does not occur by chance. The "random pairwise `0/0`" story is refuted by the
project's own reported numbers.

## 2. The real mechanism: correlated missingness at co-located variants

The NaN can only arise if missingness at the two variants is **near-perfectly
correlated** — the same samples are missing at both, so the pairwise-complete subset
excludes exactly the carriers that would make `r` defined. Every reported feature is
consistent with this and NOT with chance:

- pairs are **index-adjacent** (10327/10328, 46713/46714/46715, …);
- within **8–52 bp** (five bp clusters; spans 52/13/8/14/28 bp, median 14 bp);
- one variant (46714) **chains two pairs** — a run of co-located records.

Index-adjacency is the strong signal here (consecutive `.bim` records); the bp spans are
tight but not uniformly base-pair-close (one is 52 bp). This is consistent with **the
same genomic event represented more than once** — a multiallelic site split into adjacent
bi-allelic records, or overlapping indel / MNP representations, where a caller emits
several records that genotype (and fail to genotype) together — i.e. a
**variant-representation artifact**, not an LD property. The 8–52 bp spread (rather than
strict adjacency in bp) means the mechanism is not *proven* by position alone; it is the
leading hypothesis, and step §4.1 is exactly what discriminates it from correlated
dropout at merely-nearby-but-distinct variants.

## 3. Why `NaN→0` is the wrong fill for THESE entries

`NaN→0` is not a neutral repair — it asserts a specific value: **`r = 0`, i.e. the two
variants are statistically independent.** Two variants tens of bp apart (8–52 bp here)
in a block tight enough to share a dropout pattern are expected to be in **substantial
LD** (often |r| large, up to near 1 for co-located records).
Zeroing their entry asserts independence exactly where independence is least physically
plausible, and PSD projection then propagates that false 0 across the submatrix.

Consequence for the actual science: if a fine-mapping credible set contains one of these
co-located pairs, asserting `r = 0` between two tightly-linked adjacent variants can
**split one true signal into two, or move the posterior-inclusion mass onto the wrong
variant** — the exact error fine-mapping exists to prevent. The amendment's
`BRANCH_AFR_COND_APPLIED` already requires PIP sensitivity for credible sets touching a
zeroed pair, which shows the local risk was sensed; but the diagnosis under-rates it by
treating the zeroed value as approximately-right-and-small rather than **directionally
wrong and located where LD fidelity is load-bearing.** `NaN→0` is convenient (it
guarantees the matrix is PSD-repairable) — convenient toward a known-wrong answer.

## 4. What should happen before any conditioning is trusted

1. **Confirm the mechanism (in-perimeter, egress-safe).** For each of the 6 pairs,
   compute the pairwise-complete 2×2 genotype contingency table on the analysis sample
   set; egress ONLY the 2×2 counts (aggregate, no genotypes). This distinguishes true
   intersection-monomorphism from a duplicate-record artifact from correlated dropout,
   and reveals the real LD being discarded.
2. **Fix upstream if it is representation (most likely).** If these are multiallelic-
   split or overlapping-indel records, the correct fix is variant normalization at the
   `.bim` / decomposition stage — drop or merge the redundant record — NOT a downstream
   LD-matrix patch. Conditioning the matrix launders an upstream data-model problem into
   the reference panel and hides it from every downstream consumer.
3. **If genuinely undefined, 0 is still the wrong value.** For adjacent variants a
   neighbor-informed estimate, or dropping the redundant co-located variant, is far more
   defensible than asserting independence. Reserve `NaN→0` for the case the 2×2 table
   shows is actually a sporadic, non-co-located degeneracy (which the current evidence
   says is NOT what region 1 has).

## 5. Bearing on the pipeline as landed

- The **raw panel `.npz` staying NaN-raising is correct and should stay** — it is the
  thing that surfaced this. Do not weaken it.
- `condition_ld_matrix.py` is well-built (memory-bounded, topology-branched, ceiling-
  gated). The objection is not to the code; it is that **its input assumption — that
  off-diagonal NaNs are sporadic pairwise degeneracies safely set to 0 — is not what the
  data show.** The topology branch handles fully-NaN rows (drop) vs the rest (zero); it
  needs a THIRD category: **co-located / correlated-missingness pairs → escalate to
  variant normalization, do not zero.**
- Nothing here requires re-posting the OSF amendment yet. It requires running the §4.1
  diagnostic and, depending on the 2×2 result, either (a) an upstream normalization fix
  with its own note, or (b) a narrow amendment-update recording that the 2×2 table
  confirmed sporadic degeneracy and `NaN→0` is warranted. Either way the diagnostic
  precedes trusting a single conditioned region.

## 6. Epistemic caveat

This analysis reasons from the reported aggregate statistics (MAF, F_MISS, positions,
NaN topology), not from re-derived genotype data — which lives in the AoU perimeter and
cannot leave. The §4.1 2×2 diagnostic is what would confirm it, and it is egress-safe.
But the ~900+ order-of-magnitude gap between "F_MISS ≤ 0.05" and "pairwise-monomorphic"
is large enough to shift the burden: the conditioning approach must **rule out the
co-located-artifact explanation before `NaN→0` is defensible**, and that has not been
done.
