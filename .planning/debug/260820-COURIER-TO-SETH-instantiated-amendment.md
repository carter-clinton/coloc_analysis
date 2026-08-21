# Courier to Seth — your C3 ceiling is instantiated on the site-basis numbers; attack the text

> Provenance: drafted in-repo 2026-08-20. $0 beyond the ~2 h of VM time already spent on the
> ruled site-basis sweep. Harness cross-check PASSED — region 1 reproduced `occ_rows == 231`
> EXACTLY, the assert precedes the summary. Nothing banked, nothing fired, no OSF contact.

## 1. The site-basis sweep, verbatim

    SITE-BASIS SUMMARY n=21: min=0.1345% median=0.1685% max=0.2698%; robust_sigma(1.4826*MAD)=0.0274%
    CANDIDATE CEILING (Seth C3, 3x site-basis median): 0.5056%
    margin over observed site-basis max: 1.87x
    mean row/site inflation across sample: 1.18x (Seth's run-collapse estimate was ~1.42x for region 1)
    (full record + its 21-row per-region table: .planning/debug/260820-site-basis-sweep-results-as-received.md)

## 2. Your dispositions first

Before section 3: state your own disposition for each of the five candidates on these numbers —
median+3σ, median+4σ, 2x median, 3x median, 2x observed max. You derived C3 brief-blind last
time; this keeps that ordering rather than anchoring you on our wording.

--- OUR INSTANTIATED TEXT BEGINS HERE ---

## 3. The instantiated derivation table

| Candidate | Value (site basis) | vs observed max 0.2698% | Disposition |
|---|---|---|---|
| median + 3σ | 0.2507% | 0.93x — BELOW | REJECT |
| median + 4σ | 0.2781% | 1.03x — ABOVE | REJECT |
| 2x median | 0.3370% | 1.25x | REJECT |
| 2x observed max | 0.5396% | 2.00x | CANDIDATE, not adopted |
| **3x median** | **0.5056%** | **1.87x** | **ADOPTED** |

## 4. What the narrative audit moved

The prose was written against the ROW-basis pattern, where median+4σ sat BELOW the observed
max. On site basis it sits 1.03x ABOVE it, so its rejection rationale became "hugs the sample
edge" — your own reason for rejecting 2x-median. And 2x-median's margin here is 1.25x, not the
1.07x of your row-basis text. Your rejection LOGIC is unchanged and every disposition is still
the one you gave; only the arithmetic-relation words moved. Dispute exactly that if you think
the substitution smuggled a different argument in behind the numbers.

## 5. Dates, the commit gate, and the ask

`POSTING_DATE = 2026-08-21` is PROVISIONAL — if posting slips it is a one-token edit plus a
`guard all` re-run. The basename date `2026-08-20` is the INSTANTIATION date and does not move.
`PRE_EXECUTE_COMMIT` is HEAD at instantiation, re-confirmed at posting.

Attack the instantiated text. One file, with anchors you can verify yourself:

    .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md
    wc -c   = 31685
    md5sum  = b8f9a978c9bdbc7892f97b5d90cf9d27

One live judgement call: your §8 block and the withdrawn 0.0005 constant are ROW basis while
the gate is now SITE basis. Does the amendment reconcile the two conventions clearly enough for
a reviewer who reads only the paste block?

## 6. Standing reminders

- Posts as a NEW supplementary file on `osf.io/az52u`.
- `trsx5` stays untouched and must still show exactly 1 revision.
- Nothing in code changes — `_OCCLUSION_ANOMALY_FRACTION` stays 0.0005 — until POSTED.
- **AN AGENT MUST NEVER FIRE.**
