# Courier to Seth — revision reply: §2 fixed, §3 pre-empted, §4 companion ADOPTED, §6 homed

> Provenance: drafted in-repo 2026-08-20 against your banked attack. Status line for the record, your words:
> measurement banked; amendment drafted, not posted; code constant unchanged; fire HELD; an agent never posts and never fires
> No OSF contact has occurred; `_OCCLUSION_ANOMALY_FRACTION` is still 0.0005 in code.

**§2 — fixed (your blocking item).** 1.18x is now stated as a COUNT ratio (occluded rows /
occluded sites) that does NOT convert between the two percentages. Measured ratio of the two
medians: **1.12x** (0.1888% row / 0.1685% site), with `fraction ratio = count ratio x
(n_sites/n_rows)` and region 1's 102,421 / 96,708 = 1.059 shown. Both are ledger slots now,
carrying `FRACTION_RATIO_X == ROW_MEDIAN_PCT / SITE_MEDIAN_PCT`, so the stated ratio cannot
drift from its operands. Your `0.1685 x 1.18` demo is deliberately not reproduced.

**§3 — pre-empted.** In the document, row against row: the adopted ceiling (0.5664% row basis)
is more permissive than the rejected 10x-withdrawn candidate (0.5% of rows); the objection to
8x/10x is selection-for-clearing-the-sample, not magnitude.

**§4 — ADOPTED, not disclosed.** Measured inflation across the 21 regions: min **1.04x** /
median **1.14x** / max **1.79x** / robust sigma (1.4826 x MAD) **0.0890x**. Companion ceiling
= 3 x median = **3.42x**, same location-statistic rule as the main ceiling, margin **1.91x**
over the observed max. Clause (d) now defers on EITHER site fraction > 0.5056% (site basis) OR
occluded-site row/site inflation > 3.42x. Accounting stays on rows; site fraction, row count
and inflation reported per region; no new branch — both routes go to `BRANCH_AFR_OCC_DEFERRED`.
It is a ledger slot, not a literal. **Check this one:** the reported summary figure is the
sample MEAN 1.18x, the gate is anchored on the MEDIAN 1.14x, and the *Accounting* paragraph
says so explicitly.

**§6 — homed.** Substance inside the paste block's limitation paragraph; the exact path
`.planning/amendments/note-same-position-collinearity-2026-08-19.md` in the NOT-YET-APPENDED
deviations entry only. Kept out of the public text because a posted OSF record must be
self-contained and that note is an internal record.

**Guard.** Extended strictly additively, in its own commit: `git diff --numstat` = `64  0`,
i.e. zero deleted lines. Three new identities plus an inflation ordering check at a stated
x-ratio tolerance of 0.01; the pre-existing 0.02 ratio tolerance untouched. Each new identity
seen RED in isolation on a perturbed copy; your earlier controls re-run against the extended
guard and reproducing their signature strings. 2x2 matrix: old guard x old file GREEN, new
guard x old file RED, old guard x new file RED, new guard x new file GREEN.

**Anchors (after the revision commit).** `osf-amendment-occlusion-gate-recalibration-2026-08-20.md`:
**42213 B / e1b4a11d18ad2907af4f0a93fd5747d2** — was 31,685 B / b8f9a978c9bdbc7892f97b5d90cf9d27.
Pre-execute gate commit ADVANCED to `2689cae`, superseding `8638ed3`: that row's own standing
instruction is to re-read HEAD and update if the branch has advanced, and it has. Both
occurrences (SLOT_LEDGER line + pre-paste table row) moved together by construction — the
drift-apart risk you flagged for POSTING_DATE applies to that row too.

**Ask.** A final pass on ONLY the changed passages: basis-conventions, no-calibrate-to-pass,
*Ceiling* + *Companion condition*, the limitation paragraph, and the deviations-block
collinearity line. Not a re-read of the whole document.
