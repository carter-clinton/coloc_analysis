# Quick Task 260710-aa2 — SUMMARY

**Completed:** 2026-07-10 · **Branch:** m3-W2-aou-deltas · **Type:** docs-only (no code, no perimeter, no spend, no loop action)

## What was done

Landed the **region-1 NaN geometry VERDICT** (`m3_region1_nan_geometry_verdict.md`) — the 4th and final
amendment doc — byte-faithfully, clearing the standing **HOLD-THEN-PUSH-ALL-FOUR** order.

The verdict had blocked twice: the chat-paste route mangled its 6-row markdown table, so a reconstruction
could never byte-match its SHA-256 anchor (cf. [[reference_byte_faithful_artifact_transfer]]). Carter
delivered it this session as a `base64 -w0` blob.

### Byte-fidelity chain (all gates passed)

1. Wrote Carter's base64 to scratchpad; `base64 -d` → **5012 bytes**.
2. `sha256sum` of the raw decode == **`4543dcf4a61c3cf79061c8c55b71b316c38c4a938541cf0040c94212c8cdc06a`** (the anchor) — exact.
3. Built the final file = a 2-line self-locating header + blank line + the **verbatim 5012-byte body last**.
4. Re-verified **`tail -c 5012 | sha256sum` == anchor** (body preserved under the header). Final size 5361 B.
5. `cp`'d verbatim into `.planning/amendments/m3_region1_nan_geometry_verdict.md` (no re-typing) and
   re-verified `tail -c 5012` == anchor **in the repo location** before committing.

### Verdict content (for the record)

6/6 region-1 NaN pairs mechanistically resolved on hard coordinates: **5 direct `ref_span_overlap`**
(a deletion's REF interval physically covers the partner SNP's site → base absent on the deletion
haplotype → uncallable = the directional ~100%-missing 2×2 signature) + **1 second-order** (pair 4:
SNP@5922718 inside the upstream DEL@5922716 — same 3-record 5922716/5922718/5922724 tangle as pair 3).
**0 same-position/mergeable, 0 chance-degeneracy.** `bcftools norm -m +` fixes none; `norm -f` won't remove
a deletion spanning a neighbor. Handling = **exclude the occluded record / flag the locus limited-resolution
+ treat `r` as structurally undefined WITH provenance — never zero.** SYSTEMIC (region 1 alone has 7 distinct
deletions) → the fix belongs UPSTREAM at panel-build as an **overlapping-deletion span filter across all 276**.
This is the WHAT/mechanism that backs the already-resolved POLICY (`8f36fdf`).

## Result

- **HOLD-THEN-PUSH-ALL-FOUR CLEARED.** The amendment doc-set is complete and byte-faithful:
  - WHY — `m3_nan_conditioning_scientific_review.md` (`3516c18`)
  - JOIN-IMPACT — `m3_region1_occlusion_hinge_check.md` (`c4e0875`)
  - POLICY — `m3_panel_occlusion_policy_decision.md` (`8f36fdf`, byte-verified `42d70167…`)
  - WHAT/mechanism — `m3_region1_nan_geometry_verdict.md` (this commit, byte-verified `4543dcf4…`)
- The single `git push origin m3-W2-aou-deltas` (orchestrator step, immediately after this commit) takes all
  four to origin together → `origin==local` verified.

## Still open (unchanged by this task)

- Pre-register the scoped **OSF amendment-update** (exclusion+provenance) BEFORE any fix code lands.
- The **span-filter + provenance manifest + genome-wide present-rate-per-ancestry scan** = a future `/gsd-plan-phase`.
- **m3-06 stays HELD; `condition_ld_matrix.py` FROZEN; raw-panel NaN-raise intact.**
- AoU **loop-state UNRESOLVED** (in-perimeter check needed) — **do NOT re-fire** until the occlusion fix lands.
