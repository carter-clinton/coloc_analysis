> **DRAFT — NOT POSTED. Agent DRAFTS, Carter POSTS** (m3-07a discipline). Nothing in this
> file has been sent to OSF, and nothing in it authorizes a code change: the shipped constant
> `_OCCLUSION_ANOMALY_FRACTION` = 0.0005 stays exactly as it is until this amendment is POSTED.

> **The body below is UNINSTANTIATED.** Every quantity that the site-basis re-measurement
> (PENDING PASTE #3) must supply is a named double-brace slot sentinel, not a number. The
> enforcer `260819-u8d-placeholder-guard.sh` (section `all`) is the gate that must be GREEN
> before any paste; it is RED today by design, and its red is the guard working.

> **ENFORCER — exact invocation, run from the repo root** (recorded here so a future session
> finds the check from this artifact rather than from memory; the amendment argument follows
> this file when it is renamed at posting):
> `bash .planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-placeholder-guard.sh all .planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-XX.md`
> Its checks were seen red eight ways and green three, verbatim, in the sibling file
> `.planning/quick/260819-u8d-record-occlusion-recalibration-adoption-/260819-u8d-guard-controls-transcript.txt`.

# OSF Amendment-Update — Paste-Ready Text (AFR native-plink LD panel: factual correction to the 2026-07-10 record, and recalibration of the clause-(d) occlusion anomaly gate)

> **What this is.** A methods correction plus a gate recalibration against measurement. It
> corrects one false factual sentence in the posted 2026-07-10 record (az52u file `trsx5`,
> at that file's line 45) and re-derives that record's clause-(d) anomaly gate from a
> pre-committed 21-region measurement. The occlusion CRITERION, the exclude-in-lockstep rule,
> the provenance manifest, the defer-not-exclude protocol and the three outcome branches are
> UNCHANGED. This is a corrected empirical claim, not a threshold tweak.

---

## Pre-Paste Reference (do NOT paste this block)

| Field | Value |
|---|---|
| Target OSF project | `osf.io/az52u` — post as a **NEW supplementary file** on the existing parent amendment record (append-only; the same M1 / r3 / tcujq / trsx5 pattern). |
| Amendment kind | Methods correction (factual) + anomaly-gate recalibration. It does NOT withdraw a policy; it corrects a false factual sentence and re-derives one constant. |
| Prior record being corrected | `osf.io/az52u` file `trsx5` (AFR native-plink LD panel: withdraw NaN→0, adopt occlusion exclude-in-lockstep + provenance manifest), posted 2026-07-10T13:32:22Z. |
| Original pre-registration | `osf.io/pvb5j` (DOI `10.17605/OSF.IO/PVB5J`), posted 2026-04-10. |
| What changes | (1) the factual sentence at `trsx5`'s line 45 about region-1 deletion inventory; (2) the clause-(d) anomaly-gate metric (rows → sites) and its ceiling (0.0005 of rows → 3x the measured site-basis median). |
| What does NOT change | Clause (a) the occlusion criterion; clause (b) exclude-in-lockstep; clause (c) the mandatory provenance manifest; the defer-not-exclude protocol; clause (e) present-rate reporting; the three `BRANCH_AFR_OCC_*` outcome tokens; PSD regularization and λ; the fully-NaN-row drop rule; the raw-panel NaN-raise contract. |
| **NOT a re-version of `trsx5`** | This posts as a NEW dated file in the chain. After posting, `trsx5` must STILL show **exactly 1 revision** (2026-07-10 13:32) — the same append-only check that cleared the July record. "New OSF version, never a silent swap" means a new dated record, never an in-place edit of a posted body. |
| Posting gate | BEFORE the shipped `_OCCLUSION_ANOMALY_FRACTION` constant is changed in code, and before any recalibrated-gate output is banked. The pre-registered correction must precede the corrected execution. |
| Substrate | All of Us AFR WGS native-plink LD panel (`gs://…/ld/afr_native_panel/`, 276 regions). Controlled-tier: aggregate counts and coordinate geometry only; no raw genotypes, no LD matrices. |
| Pre-execute commit gate | `{{PRE_EXECUTE_COMMIT}}` — fill with the HEAD of `m3-W2-aou-deltas` at posting time, and confirm no gate-constant change has landed. |
| Expected posting date | `{{POSTING_DATE}}` |

**SLOT_LEDGER** — the machine-readable record of what was substituted. Post-instantiation
each line must carry a filled value; a slot that was DELETED rather than FILLED leaves a
ledger line matching no filled-value pattern, which is exactly how deletion is caught.

```
SLOT_LEDGER
  SITE_MIN_PCT = {{SITE_MIN_PCT}}
  SITE_MEDIAN_PCT = {{SITE_MEDIAN_PCT}}
  SITE_MAX_PCT = {{SITE_MAX_PCT}}
  SITE_ROBUST_SIGMA_PCT = {{SITE_ROBUST_SIGMA_PCT}}
  MEAN_ROW_SITE_INFLATION = {{MEAN_ROW_SITE_INFLATION}}
  MED_PLUS_3SIG_PCT = {{MED_PLUS_3SIG_PCT}}
  MED_PLUS_4SIG_PCT = {{MED_PLUS_4SIG_PCT}}
  TWO_X_MEDIAN_PCT = {{TWO_X_MEDIAN_PCT}}
  TWO_X_MAX_PCT = {{TWO_X_MAX_PCT}}
  CEILING_3X_MEDIAN_PCT = {{CEILING_3X_MEDIAN_PCT}}
  CEILING_MARGIN_X = {{CEILING_MARGIN_X}}
  POSTING_DATE = {{POSTING_DATE}}
  PRE_EXECUTE_COMMIT = {{PRE_EXECUTE_COMMIT}}
```

**Instantiation instructions (do NOT paste this block).**

1. Run PENDING PASTE #3 (`.planning/debug/260819-PENDING-PASTE-3-site-basis-sweep.md`) on the
   VM and paste its stdout verbatim. The harness cross-check must hold: region 1 must
   reproduce `n_occluded_rows == 231` exactly, or all results are discarded.
2. Read the eleven Class-M values off that stdout. Seven come directly from the printed
   `SITE-BASIS SUMMARY`, `CANDIDATE CEILING`, `margin over observed site-basis max` and
   `mean row/site inflation` lines; four are DERIVED by these formulas:

```
MED_PLUS_3SIG_PCT     = SITE_MEDIAN_PCT + 3 * SITE_ROBUST_SIGMA_PCT
MED_PLUS_4SIG_PCT     = SITE_MEDIAN_PCT + 4 * SITE_ROBUST_SIGMA_PCT
TWO_X_MEDIAN_PCT      = 2 * SITE_MEDIAN_PCT
TWO_X_MAX_PCT         = 2 * SITE_MAX_PCT
```

3. Substitute each Class-M slot **ONCE, everywhere it occurs**, including its SLOT_LEDGER
   line. Percentage slots render as `0.1234%`; the two ratio slots render as `1.23x`.
4. Fill the two Class-P slots at posting time: `POSTING_DATE` as `2026-08-21` shape,
   `PRE_EXECUTE_COMMIT` as the 7-40 hex-character HEAD.
5. Rename this file so its basename no longer contains the `XX` date placeholder — the guard
   FAILS while `XX` remains in the basename.
6. Run the guard's `paste-ready` and `arith` sections and require GREEN on both. Do not paste
   otherwise.

**Pre-paste checklist (top-to-bottom before submitting the OSF form):**

1. `paste-ready` GREEN, `arith` GREEN, `quote` GREEN, `draft` GREEN — i.e. section `all` exits 0.
2. Confirm no change to `_OCCLUSION_ANOMALY_FRACTION` (or to the occlusion criterion) has
   landed in code: `git log --oneline` since this draft shows docs-only.
3. Confirm the five supporting records are committed: the two Seth transcripts, the 21-region
   sweep, the §5/§4 supplement, and the site-basis sweep results.
4. Post as a NEW supplementary file on `osf.io/az52u`. Do NOT upload as a new version of
   `trsx5`.

--- PASTE INTO OSF FROM HERE ---

**Amendment-update to pre-registration osf.io/pvb5j (correcting and recalibrating osf.io/az52u file trsx5): AFR native-plink LD panel — factual correction to the region-1 deletion inventory, and recalibration of the clause-(d) occlusion anomaly gate onto occluded sites**

**Date:** {{POSTING_DATE}}

**Investigator:** Carter K. Clinton, NCSU ASHES Lab, ORCID 0000-0003-2669-8200.

**Purpose of amendment-update:** This update corrects a factual error in the 2026-07-10
record (osf.io/az52u, file trsx5) and recalibrates that record's clause-(d) anomaly gate
against measurement. The occlusion detection criterion, the exclude-in-lockstep policy, the
mandatory provenance manifest, the defer-not-exclude protocol, the genome-wide present-rate
reporting and the three pre-registered outcome branches are UNCHANGED. Nothing about how an
occluded variant is treated moves; what moves is the numerical gate that decides when a
region's occlusion count is anomalous, and one factual sentence that was wrong.

**Basis conventions (read this before any percentage below).** Two different denominators
appear in this document and they are not interchangeable. A quantity labelled **(row basis)**
is a fraction of the region's plink `.bim` variant ROWS. A quantity labelled **(site basis)**
is a fraction of the region's distinct genomic SITES (unique `(CHR, POS)` pairs). Because a
`.bim` row is biallelic by construction, one k-allelic site is rendered as k same-position
rows, so row-basis counts exceed site-basis counts by a representation-dependent factor —
measured here as {{MEAN_ROW_SITE_INFLATION}} on average across the sample. Every percentage
in this document carries its basis label explicitly. Mixing them is the single easiest way to
misread this amendment.

**(a) Factual correction to the 2026-07-10 record.**

The posted record states, in its mechanism-evidence bullet:

*"Region 1 alone contains 7 distinct overlapping deletions (60/29/7/31/31/17/29 bp)"*

That sentence is FALSE as written. It is the inventory of the deletions implicated in the six
observed NaN pairs — a statement about the NaN-implicated subset — written as if it were the
inventory of the region-1 window. The measured window inventory, obtained from the window's
own `.bim` records, is **7,951 multi-base-REF rows in 102,421 records (7.76%)**. That is the
ordinary WGS figure: gnomAD v3 reports indels at approximately 14.8% of variants with
deletions roughly half of indels, i.e. 7-8% of records. The asserted 7 in 102,421 is 0.0068%
— approximately 1,140x below the measured value and three orders of magnitude below any
published WGS callset. No real WGS window can contain 7 deletions.

The error was an unflagged scope promotion: a pair-indexed enumeration written as a
window-indexed one. It was falsifiable from published callset statistics alone, with no data
access, at any time after it was written; it was caught by a local known-answer test on first
contact with the real window.

The *same bullet's* other claim — *"Zero pairs are same-position multiallelic records"* — was
correctly scoped to the six NaN pairs and **STANDS**. What does not stand is any window-scale
reading of it: same-position rows are approximately 7-11% of rows in every region sampled,
with per-site multiplicities up to 21, and region 1's mean multiplicity is 3.16 (8,358
duplicate-position rows at 2,645 duplicate sites). The scope of the surviving claim is
therefore stated here explicitly, so it cannot be promoted again.

**(b) The corrected empirical claim.**

The honest statement of what changed: *we did not discover that our policy was wrong; we
discovered that our estimate of how often the policy applies was wrong by a factor of 38.*
Those are very different claims and only the second one is true.

The posted clause (d) carried an implicit factual assertion — that geometric occlusion is
rare enough for 0.05% of rows to be generous headroom. Measurement falsifies that assertion by
approximately 38x. Geometric occlusion at **0.1323% to 0.3527% of rows (row basis)** is a
population-scale property of this substrate, not an anomaly to be gated out. The exclusion
policy for an occluded variant is unaffected: its LD is structurally undefined, and lockstep
exclusion with a manifest entry remains the honest treatment. Only the calibration of the
anomaly detector changes.

**(c) The evidence.**

*Pre-committed sample.* A systematic-by-span sample of 21 of the 276 AFR regions (20 selected
by span stratum plus region 1 forced) was fixed BEFORE any result was seen, and measured with
the frozen `occlusion_span_filter` detector through its own `load_bim_rows` — the identical
code path as the gated test that failed. Read-only, coordinate-only, in-perimeter, with
aggregate counts as the only egress.

*Harness cross-check.* The sweep was pre-committed to discard ALL results unless region 1
reproduced exactly **231** occluded rows. It reproduced 231 exactly, so all 21 results are
trusted.

*The measured distribution (row basis).* min **0.1323%**, median **0.1888%**, max **0.3527%**,
robust sigma (1.4826 x MAD) **0.0393%**. **21/21** sampled regions DEFER at the pre-registered
0.0005 ceiling — as pre-registered, the panel build banks nothing. The distribution is flat
across small, medium and large regions with no size trend, which is what a substrate property
looks like rather than a per-region defect.

*Region 1, first real-data contact.* 231 occluded rows against a settled 5-member expectation
carried in the development fixtures. The 5 expected indices are a strict subset of the 231
observed at EXACT indices, with nothing missing and nothing displaced — the signature of a
correct detector against a too-small expectation, and a positive pass of the index-origin
validation that test existed to perform. An observable NaN requires complete-case zero
variance at that pair; geometric occlusion requires only coordinate span coverage, so every
NaN-implicated occlusion is a geometric occlusion but not conversely. The clause-(d) ceiling
for region 1 was 51.2 rows and was exceeded 4.5x.

*Representation composition.* Duplicate-position rows are approximately 7-11% of rows in all
21 regions, multiplicities reach 21, and 37 of 39 consecutive-index occluded runs in region 1
have a SINGLE occluder — one deletion span lying over a same-position stack, not a chain of
co-located deletions. A same-position stack has zero base-pair extent, so local variant
density is effectively unbounded exactly where occlusion happens.

*Mechanism conclusion.* A plink `.bim` row is biallelic by construction, so a correctly
normalized split-multiallelic callset NECESSARILY renders one k-allelic site as k
same-position rows. Same-position rows are therefore the obligatory representation for this
substrate, not evidence of un-normalized multiallelics; `bcftools norm -m +` would merge them
back into records plink cannot represent, which is the wrong direction. The correction is a
CALIBRATION of the gate, not an upstream normalization change.

**(d) The recalibrated clause (d), replacing the posted clause (d).**

*Purpose (stated first, because its absence caused the original error).* The gate exists to
detect a region whose occlusion count is qualitatively unlike the measured population — a
representation or LD-construction failure — and to do so with a low false-defer rate, because
every false defer discards a scientifically usable region. It does NOT exist to certify that
occlusion is rare. The withdrawn constant encoded exactly that belief into a detector meant to
catch anomalies, and the gate inherited the belief.

*Metric.* The gate counts occluded **SITES** as a fraction of the region's total distinct
sites. Site basis is representation-invariant: a row-basis gate fires differently on identical
biology depending on how the caller split multiallelics, counting 3 occluded records at
multiplicity 3 and 18 at multiplicity 18. A gate whose threshold moves with a representation
convention is not measuring the substrate.

*Accounting.* The exclusion ACCOUNTING remains on **ROWS**. Rows are what leave the panel; the
manifest records rows; the lockstep sumstats drop is row-keyed on `(CHR, POS)`. Reporting
exclusions in sites would understate what left the panel and would break the manifest's audit
purpose. **Both numbers are reported for every region**, together with the measured mean
row/site inflation of {{MEAN_ROW_SITE_INFLATION}} across the sample.

*Ceiling.* `n_occluded_sites <= {{CEILING_3X_MEDIAN_PCT}} x n_sites` — that is, **3x the
measured site-basis median** of {{SITE_MEDIAN_PCT}} (site basis) — giving
{{CEILING_MARGIN_X}} margin over the observed site-basis maximum of {{SITE_MAX_PCT}} (site
basis). The measured site-basis minimum is {{SITE_MIN_PCT}} (site basis) and the robust sigma
is {{SITE_ROBUST_SIGMA_PCT}} (site basis).

*Derivation, including what was rejected and why.*

| Candidate | Value (site basis) | Disposition |
|---|---|---|
| median + 3 sigma_rob | {{MED_PLUS_3SIG_PCT}} | REJECT — at or below the observed maximum; a normal region would defer. |
| median + 4 sigma_rob | {{MED_PLUS_4SIG_PCT}} | REJECT — still calibrated to the sample's spread, not to the purpose. |
| 2x median | {{TWO_X_MEDIAN_PCT}} | REJECT — too tight for n=21; leaves no room for an unmeasured upper tail. |
| 2x observed max | {{TWO_X_MAX_PCT}} | CANDIDATE — but anchored on where the sample happened to stop. |
| **3x median** | **{{CEILING_3X_MEDIAN_PCT}}** | **ADOPTED.** |

The reasoning: 3x median is anchored on a LOCATION statistic rather than on a sample edge, so
extending the sample moves the ceiling only if the population's centre moves; the resulting
margin over the observed maximum respects an upper tail that has not been measured; and it
still fires on anything at or above 3x typical, which is the regime where "a variant
representation problem beyond isolated occlusion" actually lives. For reconcilability, the
same derivation applied to the row-basis distribution gives 3 x 0.1888% = **0.5664% (row
basis)**; the site-basis figure above is the one the gate uses, and the row-basis figure is
reported only so a reader can move between the two conventions.

*No-calibrate-to-pass, on the public record.* The multiplier was NOT chosen because it clears
the sample. A ceiling at 8x or 10x the withdrawn constant also passes 21/21, and both are
REJECTED precisely because they would have been chosen for clearing the data — the original
error inverted. That 3x-median happens to pass 21/21 is a CONSEQUENCE of the derivation and
never its justification. If a future region legitimately sits above the ceiling, the gate
should fire and the region should be investigated, not the gate widened. Re-widening this
ceiling in response to a firing region is prohibited without a further amendment.

*Limitation, stated rather than buried.* n=21 of 276. The sample was pre-committed and
systematic-by-span and the distribution is flat across size classes, but the upper tail is
unmeasured. A full 276-region sweep is approximately 39 hours of virtual-machine time (8.6
minutes per region, measured) and is deliberately NOT spent ahead of this amendment. Every
region computes its own occlusion count during the production run, so the complete
distribution folds in at closeout and is reported there against this ceiling.

*Unchanged within clause (d).* Deferral remains NOT auto-exclusion. A region over the ceiling
is deferred for re-diagnosis and disclosed as a deviation, exactly as pre-registered. Nothing
about that protocol moves.

**(e) Provenance of the withdrawn constant.**

The 0.0005 constant was proposed by the project's external methodological reviewer. His own
account of its derivation is carried here verbatim, unedited, because the amendment's
rationale rests on it:

> Stated plainly for your provenance trace: 0.0005 was my figure. I derived it in July as "~10x headroom over the observed 6 NaN pairs at n_var 102,421" — i.e. calibrated against observed NaN count, on one region, for a policy that then got re-purposed to geometric exclusions. Every one of those three steps is a defect:

```
premise  : ~6 per 100,000  = 0.0059%
measured : 231 per 102,421 = 0.2255%    -> premise low by ~38x
```

> The re-purposing is the deepest error: the amendment says "the same fractional gate as the withdrawn ceiling, re-purposed to exclusions" — and I wrote that sentence without re-deriving the constant for the new, strictly larger quantity. A gate calibrated on NaN counts cannot be transplanted onto geometric-occlusion counts. That belongs in the amendment's rationale.

Both figures in that block are on the **(row basis)** convention. The re-purposing was
disclosed in the posted record's own parenthetical — "the same fractional gate as the
withdrawn ceiling, re-purposed to exclusions" — so this amendment completes a substitution the
pre-registration itself labelled as inherited, rather than correcting a hidden assumption.

**(f) Methods provenance.**

All counts in this amendment were produced by the frozen `occlusion_span_filter` detector
through its own `load_bim_rows` reader — the identical code path as the gated test that
failed, so no separate measurement implementation could have introduced a discrepancy. The
21-region sample was systematic-by-span and pre-committed before any result was seen. The
sweep carried a harness cross-check that discarded all results unless region 1 reproduced 231
occluded rows exactly. All probes were read-only and coordinate-only, executed inside the
controlled-tier perimeter with aggregate counts as the only egress — the same evidentiary
class the 2026-07-10 record cites for its own mechanism evidence. No genotypes were exported,
no LD matrix was computed, no panel output was banked, and no fine-mapping result was produced
or consulted.

**(g) What is UNCHANGED (enumerated, not gestured at).**

- **Clause (a), the occlusion criterion.** A variant record is flagged as an occluder when its
  reference-allele interval `[POS, POS + len(REF) - 1]` covers the position of a neighbouring
  variant. UNTOUCHED. The 2026-07-10 record fences *"choosing the occlusion criterion to
  obtain a particular fine-mapping result"*; the anomaly GATE is a different object from the
  CRITERION, and recalibrating the gate against a measured population is not that prohibited
  act. The criterion is not modified here in any way.
- **Clause (b), exclude-in-lockstep.** An occluded variant is excluded from the LD panel and,
  in lockstep, from the harmonized summary statistics. Panel-only exclusion and correlation
  fabrication (NaN→0) both remain prohibited.
- **Clause (c), the mandatory per-variant provenance manifest.** A lockstep exclusion without
  a manifest entry remains prohibited.
- **The defer-not-exclude protocol.** A region over the anomaly gate is deferred for
  re-diagnosis and disclosed as a deviation, never auto-excluded.
- **Clause (e), genome-wide present-rate reporting** per ancestry.
- **The three pre-registered outcome branches**, reproduced unchanged:
  BRANCH_AFR_OCC_NONE, BRANCH_AFR_OCC_EXCLUDED, BRANCH_AFR_OCC_DEFERRED.
- **PSD regularization and λ**: eigenvalue-clip with λ_floor = 1e-6 (primary) and the ridge
  sweep λ ∈ {0.001, 0.01, 0.1} (robustness companion).
- **The fully-NaN-row → drop rule** and **the raw-panel NaN-raise contract** (the raw
  per-region `.npz` reader continues to RAISE on any NaN rather than silently coercing it).
- **Pre-registration discipline and deviation logging** in `.planning/osf_deviations.md`, with
  disclosure in the manuscript.
- **All of Us controlled-tier handling**: aggregate summaries and coordinate geometry only; no
  raw genotypes and no full LD matrices leave the perimeter.

**Closing note for the record.** The pre-registered machinery worked. A gate calibrated on a
false premise fired at a free local known-answer test, on first contact with real data, before
a single byte of panel output was banked. The deferral it produced is the protective behaviour
operating as designed, and the correction is being made on the public record before the
corrected gate executes rather than after.

--- PASTE ENDS HERE ---

## Post-Paste Reference (do NOT paste this block)

**Verification checklist after OSF posting:**

1. Confirm the OSF timestamp PRECEDES any commit containing recalibrated-gate outputs or any
   change to `_OCCLUSION_ANOMALY_FRACTION`. If precedence is violated, log a deviation in
   `.planning/osf_deviations.md` immediately.
2. Capture the new file GUID and the authoritative UTC timestamp from the OSF Recent Activity
   entry (not the file page's "Date created", which is the parent record's creation date).
3. Confirm `trsx5` STILL shows exactly 1 revision (2026-07-10 13:32) — append-only honoured,
   no silent swap. If it shows 2, that is a posting deviation and must be disclosed.
4. Append the prepared entry below to `.planning/osf_deviations.md`.
5. Tag the record commit.
6. ONLY THEN may `_OCCLUSION_ANOMALY_FRACTION` be changed in code, and only to the
   site-basis metric and ceiling pre-registered above.

**Rollback:** Do not delete this file. OSF amendments are append-only; this file corrects
`trsx5` by superseding two of its statements in a new dated record, never by editing it.

## PREPARED `.planning/osf_deviations.md` ENTRY — ⚠ NOT-YET-APPENDED

**This block is TEXT ONLY. It appends to `.planning/osf_deviations.md` ONLY when Carter has
posted and the file URL, GUID and authoritative UTC timestamp are in hand. Until then
`.planning/osf_deviations.md` is byte-unchanged, and this entry does not exist anywhere but
here.** The `<TO BE FILLED AT POSTING>` markers are Carter-observed values; they are
deliberately NOT slot sentinels, because the slot ledger is a MEASUREMENT ledger and these are
not knowable from the site-basis sweep.

```
## <TO BE FILLED AT POSTING> — AFR native-panel occlusion anomaly-gate RECALIBRATION + factual correction to trsx5 (m3-07 OSF gate, second record)

- **Posted:** OSF file `<TO BE FILLED AT POSTING>` on parent record az52u —
  `<TO BE FILLED AT POSTING>` — filename
  `osf-amendment-occlusion-gate-recalibration-<TO BE FILLED AT POSTING>.md` (append-only;
  M1/r3/tcujq/trsx5 pattern). Posted as a NEW supplementary file, NOT as a new version of
  trsx5.
- **APPEND-ONLY COMMITMENT:** verified at the OSF file pages after posting — `trsx5` still
  shows exactly 1 revision (2026-07-10 13:32, unmodified). Two distinct GUIDs, each
  single-version, so the corrected record was never altered and the correction is in
  CONTENT terms, not in OSF's version-tracking sense.
- **OSF timestamp (authoritative, UTC):** `<TO BE FILLED AT POSTING>` (from the OSF Recent
  Activity entry). The file page's "Date created" is the PARENT RECORD's creation date
  (2026-04-10, osf.io/pvb5j), NOT this file's upload date.
- **Project-side copy:** `.planning/amendments/osf-amendment-occlusion-gate-recalibration-<TO BE FILLED AT POSTING>.md`.
- **Pre-execute gate commit:** `<TO BE FILLED AT POSTING>`. At OSF post time NO change to
  `_OCCLUSION_ANOMALY_FRACTION` and NO recalibrated-gate output had landed.
- **What it CORRECTS:** the factual sentence at trsx5's line 45 — "Region 1 alone contains 7
  distinct overlapping deletions (60/29/7/31/31/17/29 bp)" — which stated the NaN-pair
  deletion subset as the window inventory. Measured window inventory: 7,951 multi-base-REF
  rows in 102,421 records (7.76%), the ordinary WGS figure; the asserted 7 is 0.0068%,
  ~1,140x low. The same bullet's "Zero pairs are same-position multiallelic records" was
  correctly scoped to the six NaN pairs and STANDS; its window-scale reading does not
  (same-position rows are ~7-11% of rows).
- **What it RECALIBRATES:** clause (d), the per-region occlusion anomaly gate. Metric moves
  from occluded ROWS to occluded SITES (representation-invariant); accounting and manifest
  stay ROW-keyed and both numbers are reported; ceiling moves from 0.0005 x n_var (row
  basis) to 3x the measured site-basis median. Basis for the recalibration: a pre-committed
  systematic-by-span 21-region sample, row basis min 0.1323% / median 0.1888% / max 0.3527%
  / robust sigma 0.0393%, 21/21 deferring at 0.0005, with the site-basis re-measurement
  supplying the gate's own number. Provenance of the withdrawn constant carried VERBATIM
  from the reviewer who derived it (calibrated on 6 NaN pairs at n=1, re-purposed to
  geometric exclusions without re-derivation; premise low by ~38x).
- **What it RETAINS unchanged:** clause (a) occlusion criterion; clause (b)
  exclude-in-lockstep (panel-only exclusion and NaN→0 still prohibited); clause (c)
  mandatory provenance manifest; the defer-not-exclude protocol; clause (e) present-rate
  reporting; BRANCH_AFR_OCC_{NONE,EXCLUDED,DEFERRED}; PSD regularization + λ (eigclip
  λ_floor=1e-6 primary, ridge λ∈{0.001,0.01,0.1} robustness); fully-NaN-row → drop;
  raw-panel NaN-raise contract.
- **Amends:** osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J) via osf.io/az52u file trsx5. Sibling
  of osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md, which it corrects rather than
  withdraws.
```
