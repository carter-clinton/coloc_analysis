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

### ADJUDICATED 2026-08-14 — the posted trsx5 body is TRUNCATED (step 6b gate FIRED → STOP)

**STATUS: the posted body is the TRUNCATED lineage. The fire is HELD. Obligation-(2)
posting is HELD (same gate). This entry is no longer un-annotated toward either lineage.**

- **The measurement.** Carter downloaded https://osf.io/az52u/files/trsx5 — the **file**,
  not the page — from a logged-in OSF session on his own machine `cc-m4-mbp`, on
  2026-08-14 ~21:07 EDT:

  ```
  wc -c    ->  9695
  md5sum   ->  c19be8b2ad7cd6a45fee1d668d8a9cf9
  ```

- **The verdict, BY SIZE ALONE.** 9,695 is neither 9,758 nor 9,907, so the card's last row
  — *"any other size → STOP — the fire is HELD until a complete body is re-posted and
  recorded"* — fired on the byte count. **No hash comparison was required, none was used to
  adjudicate, and none could have overruled it.** Verdict: **STOP-truncated**. The gate is
  section **6b** of
  `.planning/quick/260812-ox1-m3-04c-task-3-fire-prep-pre-fire-1-per-r/260812-ox1-READY-TO-FIRE.md`
  and its two paste copies (`260812-ox1-AGENT-PROMPT.md` STEP 6b,
  `260812-ox1-BROWSER-PASTE.md` §6b), all three unedited by this entry.
- **Corroboration only.** The observed md5 equals Seth's API-read advisory value
  (`c19be8b2ad7cd6a45fee1d668d8a9cf9`) exactly. ⚠ That is corroboration and nothing more —
  the advisory value never adjudicates, and it did not here. The size did.
- **Seth's contest is CONFIRMED to the byte.** 9,907 - 9,695 = **212**, exactly his
  "212 bytes short" claim. His 2026-08-14 escalation was correct.
- **⚠ The prefix test is NEGATIVE — the posted body is NOT a truncation of OUR block.**
  Run in-repo by the orchestrator, `$0`, read-only, 2026-08-14 evening. The repo-canonical
  paste block was re-derived from
  `.planning/amendments/osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md` via the
  card's awk extraction (**exclusive of both marker lines**) = **9,758 B /
  `28ecdb3160833da80cfa25952f76415b`**, matching the card's anchor. Then:

  ```
  head -c 9695 <the 9,758-byte canonical block> | md5sum
    ->  6b75e660e52413e4cbec116f315590b6
  ```

  `6b75e660e52413e4cbec116f315590b6` ≠ `c19be8b2ad7cd6a45fee1d668d8a9cf9`. **Therefore the
  posted body is NOT a tail-truncation of the repo-canonical block.** *Reading — labelled a
  reading, not a finding:* the posted body most plausibly belongs to Seth's 9,907-byte
  lineage (whether it is a clean tail-truncation of HIS body is verifiable only by Seth),
  and the 2026-07-10 hand-paste source was evidently not byte-identical to the
  repo-canonical block.
- **The central open question.** The **149-byte** delta between the two "complete"
  lineages (9,907 vs 9,758) is **UNRECONCILED**.
- **Consequences in force.** The **fire is HELD**. **Obligation-(2) posting is HELD** (same
  gate). This ledger entry is no longer neutral: it is **ADJUDICATED — posted body =
  truncated lineage**. The 2026-07-10 / 2026-07-15 statements above were true when written
  and stand unaltered; this sub-entry is what makes the "un-annotated until adjudicated"
  standing position historical.
- **Remediation path — ⚠ RECOMMENDATION ONLY, NOT A DECISION. Carter has not decided.**
  Ordered: (1) reconcile the two lineages with Seth → (2) adjudicate the true complete body
  → (3) re-post it as a **NEW OSF version** — OSF file versioning preserves the truncated v1
  in history; **disclose, never silently replace** → (4) record URL / timestamp / bytes /
  md5 in this ledger → (5) only then does the fire unhold. None of (1)-(5) has been
  actioned.
- **Provenance.** Banked by `quick-260814-tgf` on 2026-08-14. The measurement is Carter's
  (authenticated OSF session, his own machine); the prefix test is the orchestrator's
  (`$0`, read-only, in-repo). **No agent contacted OSF.** Zero perimeter contact — the AoU
  browser agent stood down at the Step 3 GATE and the VM was never started. Appended, never
  rewritten: every pre-existing line of this section survives unchanged.

### RECHARACTERIZED 2026-08-14 — the posted trsx5 body is an UNEXPLAINED THIRD BODY (both lineages falsified)

**STATUS: the STOP verdict of the ADJUDICATED sub-entry above stands UNCHANGED.** That
verdict was reached **by size alone** — 9,695 is in neither {9,758, 9,907} — and nothing
recorded below disturbs it. What changes here is the **characterization** of the posted
body, not the verdict on it. **The fire remains HELD. Obligation-(2) posting remains HELD**
(same gate). This sub-entry is an append: it deletes, softens and rewords nothing above it.

- **F-1 — Seth's ask-#1 answer is NO.** The 2026-08-14 courier addendum asked whether the
  posted body is a clean tail-truncation of Seth's 9,907-byte lineage. He ran the test
  against his own file, re-verifying that file's own md5 first:

  ```
  <Seth's complete 9,907-byte body>   md5sum
    ->  425d925a88ab474ec2396cbea25e665c

  head -c 9695 <that 9,907-byte body> | md5sum
    ->  a81c22d95e7b83488c015357445f3482

  posted body (9,695 B)               md5sum
    ->  c19be8b2ad7cd6a45fee1d668d8a9cf9        NOT EQUAL
  ```

  `a81c22d95e7b83488c015357445f3482` ≠ `c19be8b2ad7cd6a45fee1d668d8a9cf9`. **The posted body
  is NOT a tail-truncation of Seth's lineage either.**
- **F-2 — both prefix tests are now negative.** Ours, recorded above against the
  repo-canonical 9,758-byte block (`28ecdb3160833da80cfa25952f76415b`):
  `6b75e660e52413e4cbec116f315590b6` ≠ `c19be8b2ad7cd6a45fee1d668d8a9cf9`. His:
  `a81c22d95e7b83488c015357445f3482` ≠ `c19be8b2ad7cd6a45fee1d668d8a9cf9`. **Neither lineage
  yields the posted body by tail-truncation.**
- **F-3 — Seth's exhaustive derivation sweep against his own lineage, every result
  negative.** He established "a third body" rather than assuming it. Tested and refuted:
  - byte-prefix at **every** length from **9,600** through **9,919** — no match at any
    length (this rules out a size mis-report combined with truncation);
  - line-prefix at all **51** line boundaries — no match;
  - whitespace normalizations at full length — CRLF conversion, trailing-whitespace strip,
    blank-run collapse, trailing-newline add/remove — no match;
  - single-line deletion, i.e. a paste that dropped one line — no match;
  - contiguous block deletion of **1-25** lines at every offset — **not one such candidate
    even produces a 9,695-byte body**, let alone matches the hash;
  - his earlier draft version (the **9,912**-byte paste region) and its placeholder-fill
    variants across three plausible gate/date combinations (**5fd58a5** / **0f3c68b** ×
    **2026-07-10** / **2026-07-04**) — no match.

  **Finding — stated as a finding, not a reading: the posted body is an UNEXPLAINED THIRD
  BODY.** It is not derivable from either lineage by truncation, line loss, whitespace
  normalization, or placeholder substitution. The **212**-byte delta (9,907 − 9,695) is
  therefore **unexplained, not mislocated**.
- **⚠ FALSIFICATION, explicit and dated 2026-08-14.** The reading recorded in the
  ADJUDICATED sub-entry above — *"the posted body most plausibly belongs to Seth's
  9,907-byte lineage"* — is **FALSIFIED as of 2026-08-14**, by Seth, against his own side,
  which is the honest direction for a falsification to travel. **The original wording is
  preserved unaltered** in the ADJUDICATED sub-entry (landed at `50dc51d`); this entry does
  not edit, soften or remove it. It was explicitly labelled *a reading, not a finding* when
  it was written — the label held, and this is precisely what that label is for.
- **What is now open.** The **149**-byte delta between the two "complete" lineages (9,907
  vs 9,758) remains **UNRECONCILED**, and it is no longer the only open question. A body
  that **neither party holds** was posted to the public record, and **no mechanism explains
  it**. We are recording that as *unexplained* rather than offering a mechanism that neither
  side can support.
- **The decisive artifact.** Carter's downloaded **9,695**-byte posted body. Seth holds both
  lineages and can diff it against both — which neither of us can do alone — and we
  replicate independently once the 9,695-byte body **and** a re-sent copy of the 9,907-byte
  body are both in-repo. **Size-first on arrival:** 9,695 first,
  `c19be8b2ad7cd6a45fee1d668d8a9cf9` only afterwards, and only to confirm which known body
  it is.
- **Next step — ⚠ RECOMMENDATION ONLY, NOT A DECISION. Carter has not decided.** Ordered:
  (1) **read the posted body first** → (2) both sides characterize it **independently**, so
  the two characterizations are a real cross-check rather than one opinion echoed twice →
  (3) adjudicate the true complete body → (4) re-post it as a **NEW OSF VERSION**, never a
  silent swap — OSF file versioning preserves the currently-posted body in history and the
  deviation is disclosed → (5) record URL / timestamp / bytes / md5 in this ledger → (6)
  only then does the fire unhold. None of (1)-(6) has been actioned. This **supersedes** the
  ADJUDICATED sub-entry's step (1) ("reconcile the two lineages with Seth") as the *first*
  move: reconciling before reading the posted body would mean choosing a body without
  knowing what was publicly claimed.
- **Vocabulary correction.** **"The truncated post" is RETIRED** as a description of the
  posted body — it presumed a truncation the evidence no longer supports. The phrasing from
  here is **"unexplained third body"**, mirroring Seth's own correction of his earlier
  framing. The ADJUDICATED heading above retains the word "TRUNCATED" as it was written; it
  is historical, and it stays.
- **Provenance.** Banked by `quick-260814-u9p` on 2026-08-14 from Seth's couriered reply
  (verbatim courier-in record at
  `.planning/quick/260814-u9p-bank-seth-prefix-test-reply-third-body-e/260814-u9p-SETH-REPLY-VERBATIM.md`).
  **Seth's measurements are HIS, and are unreproduced by us** — we do not hold his
  9,907-byte body, so F-1 and F-3 stand on his report rather than on our replication, and
  are recorded that way deliberately. **No agent contacted OSF.** Zero perimeter contact.
  `$0`. Nothing fired. Appended, never rewritten: every pre-existing line of this section
  survives unchanged.

---

### REQ-AOU-LD-VALIDATION Check 2 redefined without prior OSF amendment posting (operator override 2026-08-03)

**Date:** 2026-08-03

**Affected:** `AOU-LD-PIPELINE.md` §9.2 (Check 2 of the four-check validation protocol) and
REQ-AOU-LD-VALIDATION. Gate location: `m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md`
Task 3 STEP F ("OSF AMENDMENT-UPDATE FOR THE CHECK-2 REDEFINITION").

**Issue:** §9.2 as pre-registered reads *"Compute AoU EUR LD at the same 10 regions; compute
entry-wise Pearson correlation against 1000G EUR. Pass threshold: mean entry-wise r ≥ 0.97 for
variants with MAF ≥ 0.05 in both; ≥ 0.90 for MAF 0.01–0.05."* This is **structurally
unrunnable**: the m3-02e cost re-architecture retired the AoU EUR panel entirely (EUR LD is now
the public UKBB 337k reference, built on NCSU at $0 and never crossing an AoU boundary), so the
`AoU EUR` operand of the comparison will never exist. §9 declares the four checks *"a hard gate
for promoting the pipeline from dev to production."* All four `validation/` check directories
are currently EMPTY — the protocol has never been run.

**Resolution:** The posting gate is **bypassed under operator override** (Carter, 2026-08-03).
Check 2 is redefined in-repo, dated, with its evidence, and the redefinition is recorded here
rather than silently absorbed. The redefinition is three parts:
- **2a** — code-path equivalence of `run_native_ld_panel` against a direct `plink --r square`
  on public 1000G. $0, can genuinely fail, and exercises the exact estimator + IO path
  including the `lower_triangular` flag contract.
- **2b** — AoU-AFR vs 1000G-AFR entry-wise r, **REPORTED, NOT THRESHOLDED**.
- **2c** — `EUR_ukbb_pub` vs 1000G EUR sanity comparison, threshold **retained at r ≥ 0.90**.

**⚠ HOW THIS DIFFERS FROM THE 2026-05-05 PRECEDENT — read before citing that precedent here.**
The TA-R3 override above was defensible primarily because *"the deviation is in registration
timing, not in analysis content — the same lambda sweep, same outcome-branch decision matrix,
same convergence criteria apply."* **That defense does NOT fully transfer to this override.**
Part 2b **removes a pass/fail threshold**, which changes a decision rule, not merely the timing
of its disclosure. This is therefore a *content* deviation and must be disclosed as one. Do not
describe it as timing-only.

**Why the 2b threshold removal is nonetheless scientifically correct (state this, don't hide
it):** the original 0.97 floor was written for an **AoU EUR vs 1000G EUR** comparison — two EUR
panels, where near-identity is the legitimate expectation. Applying that floor to an **AFR**
comparison inverts its meaning: a *low* AoU-AFR vs 1000G-AFR correlation is the **expected and
desired** finding, because 1000G AFR (n=661) is precisely the inadequate reference whose
replacement is the entire scientific rationale for building an AoU AFR panel (M1a). A 0.97 pass
threshold on 2b would fail the panel for succeeding. The honest instrument is to report the
divergence as the headline result, which is what 2b does — and Check 4 (identity-placeholder
A/B) already carries the yield comparison. Note that 2c **retains** a real threshold and 2a is
a genuine pass/fail gate, so the redefined protocol is not threshold-free.

**Disclosure obligations created by this override (NOT discharged by this entry):**
1. Draft + post an OSF amendment-update to `osf.io/az52u` recording the Check-2 redefinition,
   under the m3-07a discipline (agent DRAFTS, Carter POSTS, file GUID recorded in-repo).
2. **Until that posting exists, no redefined Check 2 result may be cited as "passed"** — in the
   manuscript, in the Sci Data descriptor, or in any closeout artifact. Report it as
   `OVERRIDDEN — redefined pending amendment` wherever a status is required.
3. If the panel reaches publication before the posting lands, fold the deviation into the
   manuscript's pre-registration-limitations statement, mirroring resolution (b) of the
   2026-05-05 override.

**Related, still open (separate item, not covered by this override):** the per-region occlusion
provenance manifest currently has **no path out of the AoU perimeter** —
`run_native_ld_panel.py:822` writes `{compute_dir}/occlusion_manifest.tsv` into local scratch
(`:733`) and the upload set (`:922-938`) is only `.npz` + `.afreq` + `.occluded.excludelist`.
The drop KEY is reconstructable from the uploaded excludelists via GRCh38 varid + liftover, but
the occluder attribution, REF spans and reason/order labels are NOT — and those are precisely
what the `trsx5` amendment-update commits to publishing. Tracked as PRE-FIRE 1 in the m3-04c
gate; a compliance gap, not a mechanics blocker.

**Files affected:**
- `.planning/osf_deviations.md` (this entry)
- `.planning/phases/m3-aou-afr-ld-panel-build/m3-04c-W4-panel-reachability-egress-and-fire-PLAN.md`
  (Task 3 STEP F — the posting gate being overridden; Task 2 step 7 — the in-repo redefinition addendum)
- `.planning/amendments/AOU-LD-PIPELINE.md` §9.2 (the pre-registered text being deviated from; NOT edited)

**Verification at override time:**
- `AOU-LD-PIPELINE.md` §9.2 present and unmodified (the pre-registered text is preserved verbatim).
- All four `.planning/phases/m3-aou-afr-ld-panel-build/validation/check_*/` directories EMPTY
  (0 files each) — no check has been run or cited under either the original or redefined form.
- No OSF file GUID exists for a Check-2 amendment-update as of this entry.
