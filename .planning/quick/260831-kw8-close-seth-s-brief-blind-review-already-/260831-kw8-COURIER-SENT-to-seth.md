# Courier to Seth — is the posted occlusion rule directionally complete?

**2026-08-29 · coloc_analysis / AoU AFR native-plink LD panel**

## What I am asking, and what I am deliberately withholding

I am asking you to adjudicate a **rule**, not a result. A measurement bearing on
this is running right now and has not landed. I am not telling you what our
earlier (contaminated) pass suggested, how many cases we think exist, or which
direction they fall in — because if I did, I would be handing you the conclusion
and calling your agreement independent.

**Before you read our numbers, I would like yours.** If you are willing: write
down what you expect — prevalence, directionality, whether you expect any cases
at all — and send that with your reply. Then we compare. If we converge, that
means something. If we diverge, that is worth more than agreement.

## The geometry

The panel is a plink1 `.bed` over AoU AFR WGS. Deletions are represented with a
REF span: a deletion at position `p` with REF length `L` covers `p+1 … p+L-1`.

For a pair of variants (X, Y), plink's `r` is computed over the samples where
**both** are called. `r` is **undefined** iff, within `called(X) ∩ called(Y)`,
X or Y is invariant. A deletion's span drives its neighbours' calls to missing,
which is how a neighbour ends up invariant on the surviving intersection.

## The posted rule

A variant `v` is excluded as occluded iff some deletion `d` satisfies:

```
d.index != v.index  and  d.pos < v.pos <= d.span_end
```

This is on OSF as a public amendment (`osf.io/mk7ze`, on `az52u`). Any change is
a **new OSF version**, never a silent edit — so the bar is a pre-registration
bar, not a code-review bar.

## The question

That predicate is **anchor-centric** (it asks only about the deletion currently
under consideration) and **strictly downstream** (`v.pos > d.pos`).

1. Is a strictly downstream, anchor-centric predicate **sufficient** to cover
   the cases where `r` is undefined for occlusion-related reasons? Or is there a
   class it cannot see by construction?

2. Consider a variant `w` that is rendered invariant-on-the-intersection by
   deletion **A**. Is `w` then problematic in a pair with a *different* deletion
   **B** whose span does not reach `w`? If so, does the posted rule handle that
   pair, and should it?

3. In indel-dense repeat sequence (STR/VNTR loci, poly-CA and poly-AT tracts)
   where several overlapping indel alleles are called at nearly the same
   coordinates — does the span-based predicate behave the way you would want?

4. If you think the rule has a blind spot: is the right response to **widen the
   predicate**, to **add a separate detector**, or to **leave the rule and
   characterise the residual**? A widened rule costs real variants; we have not
   priced that.

5. Is there a reason to prefer the current rule that we might be about to
   discard too quickly?

## What is not in scope here

Not asking about: the two-condition DEFER gate (occluded-SITE fraction 0.5056% /
inflation 3.42x) — that is posted and settled; the LD panel construction; or the
sweep's mechanics. Just the directionality and completeness of the exclusion
predicate above.

## One thing you should know about our track record here

The instrument that measures this was itself found defective twice in the last
week, both times by review rather than by our own green tests — once for a
premise we had asserted but never falsified, once for a manifest read that
silently doubled every count. So please attack the framing above, not only the
question inside it. If the geometry as I have described it is wrong, that is the
most valuable thing you could tell me.
