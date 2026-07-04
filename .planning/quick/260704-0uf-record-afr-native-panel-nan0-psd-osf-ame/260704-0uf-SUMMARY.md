# Quick Task 260704-0uf — SUMMARY

**Record the POSTED AFR native-panel NaN→0 + PSD OSF amendment (999.1 OSF gate)**

**Date:** 2026-07-04 · **Branch:** m3-W2-aou-deltas · **Mode:** quick (inline exec) · **Docs + tag**

## What & why

Seth reported the AFR native-panel NaN→0 + PSD OSF amendment is POSTED (OSF file `tcujq`
on parent record az52u). This task records it in-repo so the 999.1 W1 plan has a hard-gate
target. The amendment extends the r3 PSD methods (EUR-only) to the AFR native panel and
pre-registers the NaN→0 policy + `n_zeroed` ceiling + PSD method/λ + three outcome branches.

## Integrity — verifiable, not reconstructed (the crux)

The FILLED amendment is a Science-side artifact not in my repo, and the OSF file `tcujq` is
behind an auth wall (this node has no OSF creds). I **refused to fabricate** a pre-registration
artifact from a lossy chat paste (the pasted Pre-Paste table arrived markdown-mangled). Seth
supplied SHA-256 anchors; I reconstructed my best copy and let the anchors arbitrate:

| Anchor | Expected | Computed | Bytes |
|---|---|---|---|
| Full file (before header note) | `1a25a7ba…3bef56` | `1a25a7ba…3bef56` ✓ | 12672 == 12672 |
| Posted body (between PASTE markers) | `43248aff…5b7ac3f` | `43248aff…5b7ac3f` ✓ | 8332 == 8332 |

Both matched. The in-repo file is **byte-identical to what was posted to OSF.** Built by
concatenation (`header note + blank + verified content`) so the verified bytes are preserved
exactly; re-verified: content after the 2-line header note hashes to `1a25a7ba…` / 12672 B.

## Four deliverables (one atomic commit + tag)

1. **Amendment file** → `.planning/amendments/osf-amendment-afr-native-ld-nan-psd-2026-07-03.md`
   — byte-faithful FILLED content + self-locating header note
   `> POSTED 2026-07-04T04:14:46Z as https://osf.io/az52u/files/tcujq`.
2. **Deviations entry** → `.planning/osf_deviations.md` (dated 2026-07-04) — posted URL + OSF
   timestamp + the **disclosed minor deviation** (body `Date:` 2026-07-03 vs the immutable OSF
   post instant 2026-07-04 00:14 EDT, one calendar day later; OSF timestamp authoritative for
   precedence; NOT re-posted).
3. **Coverage flag** → STATE.md: `D-AFR-NANPSD-OSF-COVERAGE: COVERED at 2026-07-04T04:14:46Z
   (OSF file tcujq, https://osf.io/az52u/files/tcujq)` → 999.1 steps 2-6 unblocked.
4. **Tag** → `AFR-NANPSD-OSF-AMENDMENT-POSTED-2026-07-04` on `0f3c68b` (post date, not the
   in-file draft checklist's `-2026-07-03` — per Seth's operative instruction).

## Precedence (gate holds)

Gate `0f3c68b` committer-date `2026-07-04T03:45:29Z` (I verified); OSF post `04:14:46Z` is
+29 min after the gate and before any conditioning-output commit (none exist) →
pre-registration precedes the analysis it covers. **Coverage GREEN.**

## Boundaries honored

- 999.1 stays **parked** — COVERAGE recorded, not promotion. No conditioning code, no loop
  re-fire (read_square_bin correctly still raises until the NaN→0/PSD policy lands), no OSF
  re-post. Explicit-path staging only.
- Routing confirmed by Seth: `.planning/osf_deviations.md` (canonical PVB5J/az52u log, not the
  Track-A sibling); coverage flag in STATE.md (DECISIONS.md uses `DEC-DATE-NN`).
