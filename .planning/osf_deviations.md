# OSF Pre-registration Deviations and Clarifications

This file tracks deviations from the OSF pre-registration (DOI 10.17605/OSF.IO/PVB5J)
and internal clarifications that do NOT require an OSF amendment.

## Clarifications (no OSF amendment required)

### B-2-resolution: D-05 NCP detection-probability framework is an original-research construction

**Date:** 2026-04-15
**RESEARCH verdict:** B-2 CONTESTED -> resolved as clarification
**Affected:** D-05a, D-05b, D-05c, D-05d

**Issue:** The Phase 4 CONTEXT.md originally attributed the NCP-based
detection-probability framework to "Hou et al. 2023 (PMC10403901 / Nat Genet)."
Research verdict B-2 found that PMC10403901 resolves to PMC11120833, which is the
*radmix* paper — a local-ancestry-aware admixture method that does NOT describe an
NCP-based detection-probability framework.

**Resolution:** D-05 is an **original analytic construction** by this study. The
OSF pre-registration section 12.1 line 320 does NOT cite Hou by name for the NCP
framework (it describes the framework in generic statistical terms), so this is an
internal clarification of CONTEXT.md attribution, not a deviation from the pre-
registered analysis plan.

The compute_detection_probability.py script header explicitly documents this as
"# ORIGINAL-RESEARCH CONSTRUCTION" with a regression test guarding against
reintroduction of the broken citation.

**Files affected:**
- `src/python/compute_detection_probability.py` (header comment)
- `tests/test_matched_n_detection.py` (regression tests: test_original_research_header,
  test_parametric_hou_not_used)
- `.planning/phases/04-matched-n-cross-ancestry-concordance/04-CONTEXT.md` (D-05
  heading updated from "Hou et al. 2023 null" to "empirical beta/SE null")

## Deviations (OSF amendment required)

### TA-R3 audit-v2-driven phase fired without OSF amendment posting (operator override 2026-05-05)

**Date:** 2026-05-05

**Affected:** D-TA-R3-OSF-COVERAGE (set to `OVERRIDDEN at 2026-05-05T13:49:10Z` instead of `COVERED`); all W1/W2/W3/W4/W5 LSF dispatch under the `ta-r3-audit-v2-driven-psd-and-r1-refire` phase.

**Issue:** The OSF amendment text for the audit-v2-driven re-analysis (PSD-regularized SH2B3 12q24 EUR re-fit + R1 trait-pair coloc.susie cache-invalidated re-fire + R2 canonical-pair parity at FTO/MC4R/APOL1/CXADR + HLA reconcile) was authored and committed locally on 2026-05-04 at `.planning/amendments/osf-amendment-r3-2026-05-04.md`. The corresponding OSF web-UI posting to `osf.io/az52u` was deferred (operator decision 2026-05-05). The TA-R3 W1 plan literal required `D-TA-R3-OSF-COVERAGE: COVERED at <timestamp>` to be present in `ta-r3-CONTEXT.md` before any LSF dispatch fired (pre-execute hard gate).

**Resolution:** The hard gate is bypassed under operator override. The CONTEXT.md token reads `OVERRIDDEN at 2026-05-05T13:49:10Z` (NOT `COVERED`). Amendment text is locally committed and reviewable. W5 closeout brief will flag this deviation explicitly to Cowork-side for v5 disclosure decision: either (a) post the amendment retroactively to `osf.io/az52u` before manuscript submission, or (b) fold the disclosure into the v5 *Genome Medicine* cover letter as a pre-registration limitation.

**Why override (not block):** Carter elected to keep HPC compute moving on 2026-05-05 (15 LSF jobs at ~30 min each, parallelizable across 15 slots → ~30 min wall) rather than serialize on the OSF web-UI posting workflow. The amendment text is unambiguous on disk; the only deferred step is the public posting. No analytical decision rules differ between the OVERRIDDEN and COVERED states — the same lambda sweep, same outcome-branch decision matrix, same convergence criteria apply. The deviation is in *registration timing*, not in *analysis content*.

**Files affected:**
- `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` (D-TA-R3-OSF-COVERAGE token records `OVERRIDDEN` + override rationale)
- `.planning/DECISIONS.md` (DEC-2026-05-05-XX entry for the override decision)
- `.planning/amendments/osf-amendment-r3-2026-05-04.md` (amendment text; locally committed; OSF posting deferred)
- W5 closeout brief (will surface this deviation in the Cowork-side handoff package)

**Verification at override time:**
- `git log --oneline | grep -E '069b34f|7d54183|02c4404' | wc -l` returns 3 (commit ancestors preserved)
- Amendment text on disk at `.planning/amendments/osf-amendment-r3-2026-05-04.md` (committed locally)
- DECISIONS.md row landed for `DEC-2026-05-05-osf-r3-defer`

### TA-R3 W5 closeout — OSF override consolidated for Cowork-side disclosure decision (2026-05-06)

**Date:** 2026-05-06

**Affected:** TA-R3 phase closeout (`ta-r3-audit-v2-driven-psd-and-r1-refire`); D-TA-R3-OSF-COVERAGE override posture surfaced at W5 closeout.

**Issue:** Per the 2026-05-05 override entry above, the OSF amendment text at `.planning/amendments/osf-amendment-r3-2026-05-04.md` was authored and committed locally before any W1 LSF dispatch fired, but the OSF web-UI posting to `osf.io/az52u` was deferred under operator decision. The W5 closeout brief at `.planning/quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md` consolidates this for Cowork-side v5 disclosure routing per the OSF amendment "Note on outcome-branch verification follow-up" paragraph.

**Resolution at W5 closeout:** Two rigor-defensible paths surfaced for Cowork-side editorial decision:

- **(a) Retroactive OSF posting:** Post the amendment text + the realized W1/W2/W3/W4 outcome-branch follow-up update to osf.io/az52u BEFORE submitting the v5 *Genome Medicine* bundle. The OSF timestamp will postdate W1 LSF dispatch (2026-05-05T13:49:10Z), but the amendment text on disk predates dispatch. Disclose the timing in a v5 cover-letter footnote: "The amendment was authored 2026-05-04, applied to disk before any W1 compute fired, and retroactively posted to OSF on YYYY-MM-DD." This is the stricter route.

- **(b) v5 cover-letter pre-registration-timing limitation:** Skip retroactive OSF posting; disclose the OSF posting override in the v5 cover letter as a pre-registration-timing limitation, citing the in-tree audit trail (this file + DECISIONS.md `DEC-2026-05-05-osf-r3-defer` + `.planning/amendments/osf-amendment-r3-2026-05-04.md` + `ta-r3-VERIFICATION.md` D9 WARN dimension) as authoritative.

The decision is a Cowork-side editorial decision, not an HPC-side compute decision; the HPC-side W5 closeout job is to surface the override and provide the substrate for either path. Both paths preserve the audit-driven re-analysis framing intact.

**Realized W1/W2/W3/W4 outcome-branch realizations (per OSF amendment "Note on outcome-branch verification follow-up"; will be appended to whichever follow-up update fires):**

- W1: `BRANCH_PSD_FIRM` at primary lambda=0.01 (5/5 EUR traits converged; 3/3 canonical pair PP.H4 = 1.000000)
- W2: `BRANCH_R1_STRUCTURAL` (R1_non_empty_PP.H4 = 0 of 28; cache-staleness refuted)
- W3: `OUTCOME` fired (gated FIRES on W1=BRANCH_PSD_FIRM); 0 of 6 W3 canonical pairs surviving (Layer-2 attrition consistent with W2)
- W4: `DEFERRED_TO_FOOTNOTE` (option (i) of OSF amendment paragraph (g); on-disk tier_assignments.tsv UNTOUCHED)

**Files affected by W5 closeout consolidation:**
- `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-VERIFICATION.md` (D9 WARN dimension records the override; D1-D13 PASS/WARN/FAIL evidence overall)
- `.planning/quick/260506-epz-ta-r3-cowork-handoff/HPC_DELIVERABLE_2026-05-06.md` ("Disclosure" section enumerates the (a)/(b) decision paths for Cowork side)
- `.planning/phases/ta-sh2b3-canonical-and-cache-refresh/md5_baseline.tsv` (8 ta-r3 successor rows appended at commit `eebdc2f`; W7 baseline preserved per Pitfall 5)
- `.planning/STATE.md` (W5 phase closure recorded)
- `.planning/ROADMAP.md` (Track-A-R3 entry status updated to COMPLETE)
- `.planning/phases/ta-r3-audit-v2-driven-psd-and-r1-refire/ta-r3-CONTEXT.md` (D-TA-R3-W5-PHASE-CLOSURE recorded)

**Honest-framing-lock invariant verified at W5 closeout:** `docs/manuscript/id-vs-ref-LD.md` md5 = `2a57c1a061f0c66988a55d1d6600efdf` at phase entry AND exit (byte-identical through all 5 waves; lock holds end-to-end).

## 2026-07-04 — AFR native-panel LD NaN→0 + PSD conditioning amendment (999.1 OSF gate)

- **Posted:** OSF file `tcujq` on parent record az52u —
  https://osf.io/az52u/files/tcujq (append-only supplementary file; M1/r3 pattern).
- **OSF-side display filename:** `Prereg_Phase1_amendment3.md` (Carter-reported
  2026-07-15; not independently verifiable from the NC-State node — OSF is a browser
  action). Recorded so the file page is findable by NAME as well as GUID. Note the
  project-side copy is named `osf-amendment-afr-native-ld-nan-psd-2026-07-03.md`; the
  OSF-side and repo-side names differ, which is expected and not a deviation.
- **OSF timestamp (authoritative, UTC):** 2026-07-04T04:14:46.635031Z
  (Jul 4 2026 00:14 EDT).
- **⚠ DO NOT confuse `tcujq` with the 2026-07-10 occlusion-exclude UPDATE.** `tcujq` is
  THIS (2026-07-04) NaN→0 amendment — the one the 2026-07-10 update WITHDRAWS. The
  occlusion-exclude UPDATE is a SEPARATE file with its own GUID **`trsx5`**
  (https://osf.io/az52u/files/trsx5; posted 2026-07-10T13:32:22Z, recorded `ac4c990`, tag
  `AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10`) — see the 2026-07-10 entry below.
  Filling `tcujq` in as the update's GUID would point the withdrawing document at the
  document it withdraws and corrupt the pre-registration chain. (Flagged 2026-07-15 after
  `tcujq` was offered for that slot; the correct GUID `trsx5` was captured the same day.)
- **`tcujq` was never re-versioned.** Verified at the OSF file page 2026-07-15: exactly 1
  revision (2026-07-04 04:14). The 2026-07-10 update superseded it in POLICY, not by
  altering this record — the append-only commitment holds.
- **Pre-execute gate commit:** 0f3c68b (committer-date 2026-07-04T03:45:29Z). OSF post
  is +29 min after the gate and before any conditioning-output commit → pre-registration
  precedes the analysis it covers. Gate holds.
- **DISCLOSED DEVIATION (minor, date-field vs post-instant):** the amendment body's
  `Date:` field reads 2026-07-03, but the immutable OSF post instant is 2026-07-04
  00:14 EDT — one calendar day later. The OSF-assigned timestamp is authoritative for
  precedence; the text date was set before the exact post time was known. Recorded here
  for honesty; the amendment was NOT re-posted (append-only record; re-posting would
  duplicate, not correct).
- **Scope covered:** AFR All-of-Us native-plink LD panel — off-diagonal NaN→0 policy,
  n_zeroed ceiling (0.05% of n_var), PSD via reused r3 methods (eigclip λ_floor=1e-6
  primary; ridge λ∈{0.001,0.01,0.1} robustness), three outcome branches
  (CLEAN/APPLIED/DEFERRED). Extends r3 (EUR-only) to AFR; r3 not retracted.
- **Amends:** osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J). Sibling of
  osf-amendment-r3-2026-05-04.md.

## 2026-07-10 — AFR native-panel occlusion exclude-in-lockstep amendment-update (WITHDRAWS the 2026-07-04 NaN→0 policy; m3-07 OSF gate)

- **Posted:** OSF file `trsx5` on parent record az52u —
  https://osf.io/az52u/files/trsx5 — filename
  `osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` (append-only; M1/r3/tcujq
  pattern). **GUID CAPTURED 2026-07-15** from the OSF file page, closing the last open
  follow-up on this record.
- **APPEND-ONLY COMMITMENT VERIFIED — no posting deviation.** The amendment pre-registered
  itself as "a NEW supplementary file (append-only)" rather than a re-version of the file
  it withdraws. Confirmed at the OSF file pages 2026-07-15: `trsx5` has exactly **1
  revision** (2026-07-10 13:32) and `tcujq` still has exactly **1 revision** (2026-07-04
  04:14, **unmodified**). Two distinct GUIDs, each single-version → the withdrawn record
  was never altered, and the supersession is in CONTENT/POLICY terms, not in OSF's
  version-tracking sense. Had it been posted as a new version of `tcujq`, that would have
  been a disclosed deviation; it was not, so there is none.
- **⚠ GUID DISAMBIGUATION (a near-miss worth recording):** `trsx5` = THIS update.
  `tcujq` (`Prereg_Phase1_amendment3.md`) = the 2026-07-04 NaN→0 amendment this one
  WITHDRAWS. On 2026-07-15 `tcujq` was initially offered to fill this slot; it was
  refused. Writing `tcujq` here would have pointed the withdrawing document at the
  document it withdraws — a plausible-looking value that silently corrupts the
  pre-registration chain in the one artifact whose job is establishing what was on the
  record and when.
- **OSF timestamp (authoritative, UTC):** 2026-07-10T13:32:22.212989Z (from the OSF
  Recent Activity entry "Carter Clinton added file …"). The file page renders this as
  "Jul 10, 2026, 09:32 AM" local/EDT = 13:32 UTC — consistent. NOTE the file page's
  "Date created: April 10, 2026" is the PARENT RECORD's creation date (the original
  pre-registration osf.io/pvb5j was posted 2026-04-10), NOT this file's upload date.
- **Project-side copy:** `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md`.
- **Pre-execute gate commit:** 5fd58a5 (the four supporting amendment docs — scientific
  review 3516c18, hinge check c4e0875, policy 8f36fdf, geometry verdict 5fd58a5 — all on
  origin). At OSF post time NO occlusion exclude / span-filter / lockstep-drop code had
  landed (m3-07 code is 07b/07c, gated on this record). Withdrawal + replacement policy is
  on the OSF record BEFORE the replacement executes → pre-registration precedes analysis.
- **What it WITHDRAWS:** the off-diagonal NaN→0 conditioning of isolated pairwise-undefined
  entries (2026-07-04 tcujq items (a)-isolated-pair-branch + (b) zeroing ceiling) and its
  three BRANCH_AFR_COND_* outcomes. Rationale: the AFR panel NaN is overlapping-deletion
  **occlusion** (structurally undefined LD, mechanism resolved 6/6 in region 1), so 0 is a
  fabricated correlation asserting independence between high-LD co-located variants.
- **What it PRE-REGISTERS (replacement):** occlusion detection (coordinate-only,
  `[POS, POS+len(REF)−1]` covers a neighbor POS) → **exclude-in-lockstep** across panel AND
  harmonized sumstats + a **mandatory provenance manifest** (per excluded variant: ID +
  both-build positions, occluding deletion + REF span, locus, traits-present,
  reason=reference-occlusion→undefined-LD) + per-region anomaly gate
  (n_excluded ≤ 0.0005×n_var → DEFERRED) + genome-wide present-rate-per-ancestry reporting.
  New outcome branches BRANCH_AFR_OCC_{NONE,EXCLUDED,DEFERRED}. Panel-only-exclude prohibited
  (orphans the sumstats-present occluded SNP on the (CHR,POS) join, e.g. rs182965575 in 7/9
  AFR traits); NaN→0 prohibited.
- **What it RETAINS unchanged:** the r3 PSD-regularization methods + λ (eigclip λ_floor=1e-6
  primary; ridge λ∈{0.001,0.01,0.1} robustness); fully-NaN-row → drop; raw-panel NaN-raise
  contract.
- **Supersedes-pointer added** to the top of the project-side tcujq body
  (`osf-amendment-afr-native-ld-nan-psd-2026-07-03.md`) per the append-only withdrawal
  convention (the prior file is NOT deleted).
- **Git tag:** `AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10` on the record commit.
- **Amends:** osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J) via osf.io/az52u file tcujq. Sibling
  of osf-amendment-afr-native-ld-nan-psd-2026-07-03.md.
