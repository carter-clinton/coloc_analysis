> Byte-faithful transfer of the region-1 NaN geometry verdict (authored Science-side). Body SHA-256 `4543dcf4a61c3cf79061c8c55b71b316c38c4a938541cf0040c94212c8cdc06a` / 5012 B; moved via base64 because the chat paste mangled its 6-row table. Everything below this header is the verbatim 5012-byte body — `tail -c 5012 | sha256sum` == the anchor.

# Region-1 NaN — final mechanism verdict + per-locus fix decision (on hard coordinates)

**Egress audit:** both returned tables are pure variant-metadata / coordinate geometry
(chr, pos, id, full REF/ALT, REF spans, coverage booleans). No genotypes, no per-person
counts this round. Boundary honored.

**Independent re-derivation:** I recomputed every REF span and coverage test from the raw
`bp`/`len(REF)` values — result is byte-for-byte the browser agent's geometry (5
`ref_span_overlap`, 1 `disjoint`). Not taking the summary's booleans on trust; they hold.

## The verdict (6/6 now mechanistically resolved)

| pair | A → B | gap | geometry | mechanism |
|---|---|---|---|---|
| 1 | DEL 1980423 (60bp) → SNP 1980475 | 52 | `ref_span_overlap` | deletion spans SNP site |
| 2 | DEL 5733474 (29bp) → SNP 5733487 | 13 | `ref_span_overlap` | deletion spans SNP site |
| 3 | DEL 5922716 (7bp) → SNP 5922718 | 2 | `ref_span_overlap` | deletion spans SNP site |
| 4 | SNP 5922718 → DEL 5922724 (31bp) | 6 | **`disjoint`** | **2nd-order: SNP already occluded by DEL@5922716** |
| 5 | DEL 7492679 (31bp) → DEL 7492693 (17bp) | 14 | `ref_span_overlap` | co-terminating deletions (both end 7492709) |
| 6 | DEL 8375794 (29bp) → SNP 8375822 | 28 | `ref_span_overlap` | deletion spans SNP site |

**5 of 6 confirmed on hard coordinates:** the deletion's REF interval physically covers
the partner's position, so on the deletion haplotype the partner base does not exist and
its genotype is uncallable — the exact directional 100%-missing signature the 2×2 showed.
The overlapping-deletion mechanism is now **coordinate-proven**, not just inferred from
missingness asymmetry.

**Pair 4 (`disjoint`) — the self-check fired and resolved cleanly.** The SNP@5922718 does
NOT sit inside DEL@5922724 (that deletion starts 6 bp downstream). But SNP@5922718 DOES
sit inside DEL@**5922716** (span 5922716–5922722) — it is the *occluded partner of pair
3*. So its minor-allele carriers are already depleted by the upstream deletion, and its
NaN against the downstream DEL@5922724 is a **second-order consequence of the same 3-record
tangle** (5922716 DEL / 5922718 SNP / 5922724 DEL), not an independent A–B span overlap.
Same root cause (overlapping deletions at a complex locus), different graph edge. The
`disjoint` verdict correctly refused to force pair 4 into the direct-coverage box.

## Fix decision, per locus (hard-coordinate basis)

- **`bcftools norm -m +` is the wrong tool for all six** — there are **zero same-position
  cases**, so allele-merging touches nothing. This kills the "just normalize/merge" reflex
  outright.
- **`bcftools norm -f REF` (left-align)** is still worth running as standard hygiene, but
  it will not resolve these — left-alignment does not remove a deletion that legitimately
  spans a neighbor.
- **The 5 `ref_span_overlap` pairs are distinct overlapping events, not mergeable.** The
  defensible panel-level handling is **flag the locus as limited-resolution and exclude the
  occluded record from the LD window** (or retain both but mark the pair's `r` as
  structurally undefined with provenance — NOT zero). The missingness is real biology (the
  base is absent on the deletion haplotype), so there is no "true r" to recover.
- **The 5922716–5922724 tangle (pairs 3 + 4) must be handled as one 3-record locus,** not
  two independent pairs — exclude/flag decisions there interact.

## What stays a Carter policy call (not auto-executed)

Excluding or flagging records in the LD panel changes which variants the panel carries,
which couples to the **sumstats↔panel join key** (`chr:pos:REF:ALT`). Dropping an occluded
record is only safe if that variant is absent from (or independently handled in) the
harmonized sumstats. So the sequence:
1. **coordinate mechanism: settled** (this doc) — 5 direct overlaps + 1 second-order, 0
   mergeable, 0 chance-degeneracy.
2. **policy: Carter chooses** exclude-occluded vs flag-locus-limited-resolution, checked
   against the sumstats harmonization key, and whether an overlapping-deletion span filter
   belongs upstream at panel-build for ALL 276 regions (region 1 is unlikely to be unique).
3. **lands as a gated step** with a narrow amendment-update recording the panel
   overlapping-variant policy; the m3-06 third topology category (co-located → escalate,
   don't zero) routes these there.

m3-06 stays held landed-but-not-trusted; raw-panel NaN-raise stays.

## Generalization flag (worth raising now)
Region 1 alone has **7 distinct deletions** (60/29/7/31/31/17/29 bp): a 7-bp, four
~30-bp (29/31/31/29 at pairs 2, 4, 5, 6), a 17-bp co-terminating with the pair-5 31-bp
deletion, and a 60-bp — each occluding or overlapping a neighbor. Across 276 regions of
AFR WGS this pattern will recur — the fix
should almost certainly be a **panel-build-stage overlapping-deletion span filter**, not a
per-region patch. That is the scalable version of the fix and belongs in the policy
decision.