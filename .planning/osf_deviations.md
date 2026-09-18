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

### RESOLVED 2026-08-17 — the trsx5 body question is settled; pointer recorded here 2026-09-16

- **Why this pointer exists (and why it is only a pointer).** This section previously ended on
  "None of (1)-(6) has been actioned" (`:326` at `621701c`, re-derived 2026-09-16), and a search of
  THIS FILE for `08-17` / `gate-released` / `260817` returns **ZERO hits**
  (`grep -cE '08-17|gate-released|260817' .planning/osf_deviations.md` = `0`, re-measured
  2026-09-16), so a reader of the ledger alone could not learn the outcome. **Nothing above is
  re-adjudicated, edited or softened**: the 2026-08-13 / 2026-08-14 readings stay as the honest
  state of knowledge at their dates. This sub-entry adds the pointer, and nothing else.
- **The resolution.** The posted **9,695-B** body is a **byte-exact plain-text rendering of the
  COMPLETE 9,907-B lineage** — not a truncation, and not a third body. Seth published the 6-step
  transform first; we replicated it firsthand from the git object store at `3684413`
  (`git show 3684413:.planning/quick/260814-u9p-bank-seth-prefix-test-reply-third-body-e/260814-u9p-seth-lineage-9907.txt`,
  re-measured 2026-09-16 = **9,907 B** / `425d925a88ab474ec2396cbea25e665c`), implemented from his
  prose spec alone, run once, with no fitting. Output **9,695 B** /
  `c19be8b2ad7cd6a45fee1d668d8a9cf9` — which is also Carter's own firsthand 2026-08-16 OSF download
  measurement. The in-repo copy of the posted body is
  `.planning/quick/260817-vbu-release-trsx5-gate-bank-resolved-adjudic/260817-vbu-trsx5-posted-9695-reconstructed.txt`
  (re-measured 2026-09-16: **9,695 B** / `c19be8b2ad7cd6a45fee1d668d8a9cf9`).
- **Consequence for the pre-registration record.** All three bodies carry the same pre-registration
  prose; the 212-B and 149-B deltas are pure markup. The public record is substantively correct and
  complete. The **"unexplained third body" characterization is RETIRED** — by the person who coined
  it, and by our own replication — while the heading above that coined it stays exactly as written.
- **The gate.** **RELEASED BY CARTER ON SUBSTANCE, 2026-08-17 22:32 EDT**:
  `DEC-2026-08-17-trsx5-gate-released` in `.planning/DECISIONS.md` (at `:2030`, re-derived
  2026-09-16). **Re-post NOT taken**: optional legibility only, per Seth's withdrawn "re-post
  required". The recommendation list's "(1)-(6) not actioned" was TRUE when written, and is
  superseded by a resolution that reached the same question by a different route — characterize the
  posted body rather than re-post it.
- **Provenance.** Appended by `quick-260916-vqp` on 2026-09-16 after the blast-radius review
  (finding B8); the review is banked at
  `.planning/debug/260916-BLAST-RADIUS-c93e97b-to-621701c.md`. No OSF contact, no Seth contact, no
  agent posted anything. `$0`. Nothing fired. Appended, never rewritten: every pre-existing line of
  this section survives unchanged.

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

## 2026-08-22 — AFR native-panel occlusion anomaly-gate RECALIBRATION + factual correction to trsx5 (m3-07 OSF gate, second record)

- **Posted:** OSF file `mk7ze` on parent record az52u —
  `https://osf.io/mk7ze` — filename
  `osf-amendment-occlusion-gate-recalibration-2026-08-22.md` (append-only;
  M1/r3/tcujq/trsx5 pattern). Posted as a NEW supplementary file, NOT as a new version of
  trsx5.
- **APPEND-ONLY COMMITMENT:** verified at the OSF file pages after posting — `trsx5` still
  shows exactly 1 revision (2026-07-10 13:32, unmodified). Two distinct GUIDs, each
  single-version, so the corrected record was never altered and the correction is in
  CONTENT terms, not in OSF's version-tracking sense.
- **OSF timestamp (authoritative, UTC):** `2026-08-22T02:58:55Z` — the Recent Activity log
  entry "Carter Clinton added file
  osf-amendment-occlusion-gate-recalibration-2026-08-22.md to OSF Storage" (the widget
  renders that instant as "Aug 21, 2026 10:58 PM" ET). ⚠ **The prepared template predicted
  that this file page's "Date created" would show the PARENT RECORD's creation date
  (2026-04-10, osf.io/pvb5j) — as `trsx5`'s page does. That expectation was NOT borne out
  here.** The observed "Date created" read `2026-08-22T02:58:53Z`: this object's own
  creation, 2 s before the activity-log entry. The Recent Activity entry remains the
  authoritative stamp of record; the 2 s gap is upload-then-index, not a discrepancy, and
  it is written down here so a future reader is not surprised by it.
- **Project-side copy:** `.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md` (knowable now; the instantiation-dated basename does not move at posting).
- **Pre-execute gate commit:** `07df11e44f2d56536ef4ef0753c8d2f8fdb55ae8`. At OSF post time NO change to
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
  / robust sigma 0.0393%, 21/21 deferring at 0.0005, plus the site-basis re-measurement of
  the same 21 regions: site basis min 0.1345% / median 0.1685% / max 0.2698% / robust sigma
  0.0274% (site basis). The gate's own ceiling is 3x that site-basis median = 0.5056% (site
  basis), 1.87x the observed site-basis maximum. The gate ALSO gains a COMPANION condition
  on the occluded-site row/site inflation ratio, because a site-basis metric is
  multiplicity-invariant and therefore multiplicity-BLIND: measured across the same 21
  regions, inflation min 1.04x / median 1.14x / max
  1.79x / robust sigma 0.0890x; companion ceiling = 3x the
  median = 3.42x, leaving 1.91x margin over the observed
  maximum. A region deferring on EITHER condition routes to the same BRANCH_AFR_OCC_DEFERRED
  token — no fourth branch. Provenance of the withdrawn constant
  carried VERBATIM from the reviewer who derived it (calibrated on 6 NaN pairs at n=1,
  re-purposed to geometric exclusions without re-derivation; premise low by ~38x).
- **What it RETAINS unchanged:** clause (a) occlusion criterion; clause (b)
  exclude-in-lockstep (panel-only exclusion and NaN→0 still prohibited); clause (c)
  mandatory provenance manifest; the defer-not-exclude protocol; clause (e) present-rate
  reporting; BRANCH_AFR_OCC_{NONE,EXCLUDED,DEFERRED}; PSD regularization + λ (eigclip
  λ_floor=1e-6 primary, ridge λ∈{0.001,0.01,0.1} robustness); fully-NaN-row → drop;
  raw-panel NaN-raise contract.
- **Known limitation recorded alongside:** same-position collinearity caveat recorded at
  .planning/amendments/note-same-position-collinearity-2026-08-19.md; fine-mapping at
  multiallelic sites carries near-collinear predictors; known split-representation property,
  not a defect. That note is an INTERNAL RECORD — not part of any OSF amendment and not
  posted. Its SUBSTANCE is disclosed inside the posted text's limitation paragraph; only its
  repo PATH lives here, because a posted OSF record must be self-contained and a public
  reader cannot resolve a `.planning/` path.
- **Amends:** osf.io/pvb5j (DOI 10.17605/OSF.IO/PVB5J) via osf.io/az52u file trsx5. Sibling
  of osf-amendment-afr-occlusion-exclude-UPDATE-2026-07-10.md, which it corrects rather than
  withdraws.

### Recorded at posting (2026-08-22)

- **Posting-date disclosure.** The amendment carried a PROVISIONAL posting date of 2026-08-21.
  Carter had not uploaded when the UTC day rolled, so `POSTING_DATE` moved 2026-08-21 →
  2026-08-22 through the instantiation engine's Class-P pass (commit `c61d179`), never by hand.
  The body Seth's final pass cleared was 22,945 B / `422f1f28d6a3b76c7657fadec05a0237`; the body
  actually posted is 22,945 B / `13a49f543cabcc27ce9f1e589783c060`; the COMPLETE difference is
  the `**Date:**` line — `diff` reports exactly `4c4`, one line changed, nothing else. No
  scientific statement, number or commitment differs between the reviewed and the posted body.
- **Integrity.** The repo's paste block (the region between the two PASTE markers, exclusive of
  both) is 22,945 B / `13a49f543cabcc27ce9f1e589783c060`, equal to the md5 OSF Storage itself
  computed and stores for `mk7ze` version 1 (22,945 bytes) — so what OSF serves IS the repo body.
  ⚠ **Method caveat, recorded rather than smoothed over:** a scripted byte-for-byte re-download
  from inside the OSF page was REFUSED by OSF's file server (the project is private; the
  cross-origin authenticated fetch was rejected), so this hash was READ FROM THE FILE'S API
  RECORD after upload rather than recomputed from a downloaded byte stream. A local md5 of a
  manually re-downloaded copy was NOT performed; that belt-and-suspenders check is an OPTIONAL,
  NON-BLOCKING follow-up. The hash is OSF's own computation over the stored object — not a repo
  echo, and not a re-download.
- **Append-only.** `trsx5` still shows exactly **1 revision** — the Revisions panel lists a single
  entry "1. Jul 10, 2026 09:32 AM" (ET) and the API confirms one version created
  `2026-07-10T13:32:21Z`. Nothing was added to it as a new version. `mk7ze` is its own
  single-version file on the project's OSF Storage ROOT (breadcrumb Az52u / Files / Mk7ze), a
  SIBLING of `trsx5`, not a child of it; the stored filename is the exact lowercase
  `osf-amendment-occlusion-gate-recalibration-2026-08-22.md` (the OSF page heading title-cases it
  visually, but the file list, the API and the activity log all show the lowercase name). Two
  distinct GUIDs, each one version → no silent swap.
- **Precedence (Post-Paste checklist item 1) — SATISFIED, no deviation.** HEAD `c61d179` was
  committed `2026-08-22T02:48:03Z`, ten minutes BEFORE the OSF stamp `2026-08-22T02:58:55Z`.
  `src/python/run_native_ld_panel.py:133` still reads `_OCCLUSION_ANOMALY_FRACTION = 0.0005`,
  last changed in `d9fbc63` (2026-08-13, before this recalibration existed);
  `git diff --stat 2689cae HEAD -- src/ tests/ config/` is EMPTY; no recalibrated-gate output
  exists anywhere. The pre-registration precedes the analysis it governs.
- **Record.** Decision: `DEC-2026-08-22-occlusion-recalibration-posted` in
  `.planning/DECISIONS.md`. Git tag on the record commit:
  `AFR-OCCLUSION-GATE-RECALIBRATION-OSF-POSTED-2026-08-22` (July sibling:
  `AFR-OCCLUSION-EXCLUDE-OSF-UPDATE-POSTED-2026-07-10`). The seven supporting records the
  amendment's pre-paste checklist counts live in `.planning/debug/`: the four `260819-…`
  (SETH-VERDICT-adjudication-confirmed, SETH-C1C2C3-convergence, occ-measure-sweep-results,
  supplement-results), the two `260820-…` (site-basis-sweep-results,
  SETH-ATTACK-instantiated-amendment) and
  `260821-SETH-FINAL-PASS-no-blocking-objection-as-received.md`. Carter's posting procedure:
  `.planning/debug/260821-POSTING-CARD-for-carter.md`.

## 2026-09-03 — AFR native-panel DEFINED-ROW TAIL disclosure (measured characterisation; NO amendment, NO predicate change, NO carrier floor)

- **Status:** DRAFTED — NOT POSTED; placement and posting are Carter's. No agent has contacted
  OSF, no GUID has been reserved, and nothing below has been uploaded anywhere. This entry is the
  in-repo methods record only.
- ⚠ **CORRECTED 2026-09-04 (`260904-dgi`) after a 5-reviewer adversarial review** (Codex CLI plus
  four blind investigators), which found 5 blocker-level and 6 high-level false or overclaimed
  statements in the 2026-09-03 draft. The corrections are made INLINE rather than appended as
  errata, because this draft was never posted: there is nothing to retract, only a draft to fix
  before it becomes one.
- ⚠ **ADJUDICATED 2026-09-08 — NO OPEN OBJECTION.** The disclosure was reviewed across multiple
  rounds by the project's external reviewer, who then raised **two defects in the corrections
  themselves**. Both are disposed of below, and **no objection from any round remains open.**
  - **D8 — ACCEPTED.** The pair-4 citation asserted that neither of its members was covered by
    any deletion record. **FALSE:** its NaN-implicated SNP at 5922718 **IS** covered by a
    **THIRD** record, **DEL 5922716** (span 5922716-5922722), is therefore **EXCLUDED by the
    predicate**, and yields **ZERO residual** — a **DIFFERENT class** from the chr7 survivor,
    for which **no record covers EITHER member** and which **SURVIVES INTO THE PANEL**.
    Corrected in `260908-hv8`. ⚠ **The mechanism was BROADER than the instance reported, and
    that is the more important half:** the same phrasing occurred **THREE times** — false on
    pair 4, **TRUE** on the survivor and on one annotation — and that *shared phrasing* WAS the
    false equivalence, so correcting only pair 4 would have left it **RECONSTRUCTIBLE** from the
    surrounding text. All three were eliminated. ⚠ The phrase was also **invisible to a literal
    `grep`** — it was **line-wrapped AND bolded** — so a literal-scoped guard would have
    reported success while leaving the defect standing.
  - **D7 — RAISED, THEN RETRACTED BY THE REVIEWER AFTER HE MEASURED IT.** The charge was that
    our corrected mk7ze line numbers had been converted from stale references. Measurement
    showed otherwise: the cited sentences **SPAN MULTIPLE LINES** (the NaN sentence = posted
    **108-110**, repo draft 275-277; clause (a) = posted **300-302**, repo draft 467-469). We
    cited where each sentence **BEGINS**; he measured where the phrase he quoted **FALLS**.
    **Both are defensible referents**, and `275 - 167 = 108` is **correct arithmetic on a
    correct input**. This is recorded as **neither an error of ours nor a win**: the defect was
    the citation **FORM**, not the number — a single line number for a multi-line sentence is
    **AMBIGUOUS**, which is exactly why two parties measuring the same artifact produced
    different numbers. Fixed as **RANGES**, with the **verbatim quotation as the primary
    locator**, since a quote survives repagination and a line number does not.
- ⭐ **DISCHARGED 2026-09-08 — THE MEASUREMENT WAS FIRED, AND IT RETRACTS RATHER THAN CONFIRMS.**
  The one outstanding item — the **pairs-per-occluding-deletion DISTRIBUTION** in the tail — was
  fired by **Carter** on **2026-09-08** against `pcs_tail_verdicts.tsv` (**the emitted TSV only: no
  re-run, no genotypes, no scan re-execution**). It returned, and **its result RETRACTS Finding 2's
  establishment rather than confirming it.** With the clustering **measured**, the heterogeneity
  chi-square can be corrected for it directly, and under that correction **either treatment of the
  chr15 overlap carries AT MOST WEAK evidence** (p 0.0326 / p 0.0517; p 0.2171 dropping both).
  **Finding 2 — between-region heterogeneity in the POST-filter rate — is recorded below as
  NOT ESTABLISHED.** The within-window clustering is itself a **NEW REPORTABLE FINDING**, not
  merely a caveat. Both are in **§(10)**, with the measurement's provenance in **§(9)**.
  ⛔ **This discharges the last OPEN item. It is NOT authorization to post.** No open objection and
  no outstanding measurement now remain, and that changes **nothing** about posting: the decision is
  **Carter's alone**, and the status above stands unchanged — **DRAFTED — NOT POSTED.**
- ⚠ **CITATION CONVENTION (corrected 2026-09-04; REFINED 2026-09-08).** Every mk7ze citation below
  gives the **POSTED** line with the repo-draft line carried alongside — *"mk7ze lines 108-110 (repo
  draft lines 275-277)"* — so a reader can check either. ⚠ **Where a cited sentence SPANS MULTIPLE
  LINES the FULL RANGE is given, and the VERBATIM QUOTATION is the primary locator**, because a quote
  survives repagination and a line number does not. This refines, rather than corrects, an arithmetic
  error: the 2026-09-04 entry cited the single line on which each multi-line sentence **BEGINS**,
  which is a **defensible referent**, as is the line on which any later clause of the same sentence
  falls. **Both were right; neither was sufficient.** A single line number for a multi-line sentence
  is **AMBIGUOUS** — a reader quoting a later clause lands on a different number and cannot tell
  whether the citation or the arithmetic is at fault. The 2026-09-03 draft cited repo-draft line
  numbers of a 598-line working file
  while calling them mk7ze lines. **Posted = repo draft − 167**, and this is proven rather than
  asserted: repo lines 168-500 of
  `.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md` reproduce
  mk7ze's exact posted md5 `13a49f543cabcc27ce9f1e589783c060`, 22,945 B, **333 lines**. That repo
  file's line 1 reads `DRAFT — NOT POSTED`, its paste boundary is at repo line 501, and its lines
  502-598 are post-posting status material that was never part of the posted body.
- ⚠ **STATISTICAL CONVENTION (named, because it was the actual defect).** Every Spearman
  confidence interval in this entry is a **95% CI, Fisher z with the Bonett-Wright Spearman
  standard error 1.03/sqrt(n-3)**. It is named inline because an earlier draft mixed two
  conventions inside a single sentence — quoting a Pearson-form Fisher-z interval beside a
  Bonett-Wright bound — which is how a value outside its own stated interval survived review. A
  referee can now reproduce every interval here; against the earlier draft they could not.

### (1) DISPOSITION, and that it was adjudicated

- **DISCLOSE + ANNOTATE. No amendment.** Re-amending days after posting, for a measured
  characterisation that changes NO behaviour, would be poor pre-registration hygiene.
- **Two disclosure targets.** (i) methods disclosure (this log + manuscript); (ii) data-product
  annotation on the panel's own provenance manifest — which pairs carry a degraded
  informative-carrier count.
- **Why (ii) is not an amendment:** it is additive provenance under clause (c). It changes no
  exclusion, no criterion, no branch.
- **Why a carrier floor later WOULD be an amendment:** a floor changes the panel's contents.

### (2) WHAT WAS MEASURED

21 regions, all in scope, 3,094 defined tail rows at `max(carriers_lost_frac) >= 0.9`:

- **ROWS** 2560 PRE-filter / 534 POST-filter of 3094 — POST = **17.26%**
- **PAIRS** 2047 PRE-filter / 474 POST-filter of 2521 — POST = **18.80%**
- Regions with tail rows **21**; regions with ZERO POST-filter rows **0**.
- **Heterogeneity — MEASURED, but NOT ESTABLISHED.** ⚠ **§(10) supersedes the interpretation of
  this bullet; the numbers in it are retained because they are what was measured.** The
  **uncorrected** pair-level overdispersion is **1.99x (95% CI ~1.1-4.2; chi2 37.78, dof 19,
  p 6.3e-3)** after dropping the chr15 double-count; under the more conservative
  **drop-both-chr15-windows** treatment it is **1.52 (p 0.073)** — **not significant at alpha
  0.05**. ⚠ **Every one of those figures assumes INDEPENDENT pairs, and as of 2026-09-08 that
  assumption is MEASURED FALSE** (within-cluster **ICC 0.728930**, design effect **1.360272** —
  §(10)). **Under the measured design effect, either treatment of the chr15 overlap carries AT MOST
  WEAK evidence of heterogeneity beyond measured clustering (p 0.0326 / p 0.0517; p 0.2171 dropping
  both), so the between-region heterogeneity is NOT ESTABLISHED.** The **DIRECTION** remains
  positive under every treatment (**phi > 1.2 throughout**), but the **magnitude is unidentified**
  and the dispersion is **not robustly distinguishable from a clustering-only explanation**. A bare
  "1.99x" overstates what was identified; so does any claim of significance.
- **Permutation confirmation:** verified against a 40,000-resample Monte Carlo permutation test,
  **p = 0.0072** (asymptotic chi-square p 6.3e-3; the asymptotic value is mildly
  anti-conservative, conclusion unchanged). ⚠ The permutation test permutes PAIRS and therefore
  assumes exchangeable independent pairs — **it validates the asymptotics, NOT the independence
  assumption at issue in the clustering caveat** in §(7).
- **NO STRUCTURAL COVARIATE WAS FOUND to account for the heterogeneity** — rho **-0.199** (window
  rows), **-0.201** (occluded ids), **+0.004** (occlusion density). See §(7): at n=21 this is an
  **underpowered null**, not a demonstration that no covariate explains it. ~20% relative
  variation between parent regions.
- **Definitional axis:** rarer != min on **24.27%** of tail rows vs **0.52%** below tail = **46.5x**
  enrichment. **No association with the PRE/POST axis was DETECTED** — rho **+0.173**, 95% CI
  **[-0.292, +0.572]**, p **0.453**; the PRE-vs-POST 2x2 gives chi2 2.914, p **0.088**. **BOTH are
  underpowered at n=21 and NEITHER establishes independence.** The two axes are reported
  separately because no association was detected, not because none exists.
  ⚠ **Recorded against ourselves:** an earlier draft argued the rho carried the independence claim
  and that the 2x2 should deliberately not be used as support. That is inverted — the rho is the
  **WEAKER** of the two (**p 0.45** vs **p 0.088**). Steering from the stronger signal to the
  weaker one, in a passage about absence of evidence, was itself an absence-of-evidence error.

### (3) ⭐ THE SURVIVOR GEOMETRY — a HEADLINE, and what it does and does NOT establish

- `m2_region_00149`, deletion `chr7:89454077:GCGTA:G` (REF len 5, span 89454077..89454081) x
  partner `chr7:89454076:C:T`, offset **-1**, side upstream, `already_occluded` False, pair_key
  `9776035|9776036`.
- The posted predicate is `d.pos < v.pos`: `89454077 < 89454076` = **FALSE**. The single survivor is
  **INVISIBLE TO THE PREDICATE BY CONSTRUCTION**. Across the 21-region scan, **no positive-offset
  undefined survivor was observed**, and the only measured surviving pair was upstream at offset
  **-1**. Offset histogram `{-14:1, -9:1, -6:1, -3:1, -1:1, 0:10}`.
- **Stated at the strength the evidence supports:** that observation supports a **prospective
  positive-offset falsification check**; it is **NOT proof of predicate completeness**. The
  scanner's own docstring (`pairwise_completeness_scan.py:40-45`) states the reason directly —
  n = 1 supplies neither prevalence, boundary width, nor one-sidedness. An earlier draft promoted
  this to a completeness claim for the downstream direction; **that promotion is withdrawn as
  overclaimed from n=1.**
- ⛔ **NO PREDICATE CHANGE.** Extending to offset -1 would cost only ~0.12% of the panel, and that
  cheapness is an argument AGAINST, not for: it is calibrate-to-pass at n=1.
- **PROSPECTIVE PRODUCTION PREDICTION** — *"Within the 21-region pre-committed sample, residual
  undefined-r was observed ONLY at negative offsets. A positive-offset survivor WITHIN that sample
  would falsify downstream predicate completeness for it."*
  ⚠ **THIS IS EXPLICITLY SAMPLE-SCOPED.** A positive-offset case is **ALREADY KNOWN
  out-of-sample** — `m2_region_00057`'s **+1**: `chr15:20394741:AT:A` (ref_len 2, span_end
  20394742) x `chr15:20394743:T:C`, **one base past the span end, downstream, un-occluded**,
  measured 2026-08-24
  (`.planning/debug/260824-STAGE-B-HALT-region57-boundary-adjacent-pairwise-NaN.md:62-70`), and the
  pre-committed 21-region sample does not contain it. Our own `.planning/STATE.md:287` had already
  concluded that the residual class **sits immediately adjacent to the REF span on EITHER side**
  and that this sweep could observe only one side. **Production tests the rate on BOTH sides.**
  ⚠ The 2026-09-03 draft stated this prediction without the sample scope, which made it **false
  against data we already held**. That is corrected here.
- ⚠ **THIS IS NOT A PRE-REGISTRATION TODAY.** It is a prospective production prediction, **to be
  pre-registered IF AND WHEN this disclosure is posted, and posted BEFORE production testing**. It
  is **post hoc relative to the 21-region scan**. The 2026-09-03 draft's parenthetical "(recorded
  as pre-registered here)" could not be true of an entry marked DRAFTED — NOT POSTED, and is
  withdrawn. Change the predicate only if the RATE warrants it against data.

### (4) ⭐ SCOPE OF mk7ze LINES 108-110 (repo draft lines 275-277) — stated explicitly, as a RECORDED COMMITMENT

- **mk7ze lines 108-110 (repo draft lines 275-277)** read: *"An observable NaN requires
  complete-case zero variance at that pair; geometric occlusion requires only coordinate span
  coverage, so every NaN-implicated occlusion is a geometric occlusion but not conversely."*
- **RECORDED SCOPE:** it is a statement about OCCLUSIONS and their relation to NaN-implication. It
  does not address NaNs arising WITHOUT an occlusion. Its argumentative work is carried by *"but
  not conversely"* (not every geometric occlusion is NaN-implicated), which is substantive, true,
  and untouched by the survivor.
- **"Occlusion" is GEOMETRIC throughout mk7ze** — clause (a) at **mk7ze lines 300-302 (repo draft
  lines 467-469)**: *"A variant record is flagged as an occluder when its reference-allele interval
  [POS, POS + len(REF) - 1] covers the position of a neighbouring variant."*
- The survivor is a NaN with **no covering record for EITHER member**, hence **OUTSIDE the
  sentence's domain, not a counterexample within it**.
- ⚠ **THE SENTENCE'S OWN DRAFTING RECORD, carried verbatim rather than withheld.** The claim
  descends from `.planning/debug/fire-morning-occlusion-oracle-vs-geometry.md:227-233`, whose
  conclusion was stated **BROADLY**: *"Every NaN-producing pair is geometrically occluded."*
  That is stated plainly here because claiming a narrow scope for a sentence while withholding its
  own drafting record is the weakest available position, and because **mk7ze §(e) set the house
  standard of carrying provenance verbatim.** The narrow reading is defended below on what the
  expectation set was actually built on, not on the drafting record being favourable.
- ⚠ **THE NARROW READING IS NOT MERELY GRAMMATICALLY AVAILABLE — IT IS WHAT THE EXPECTATION SET WAS
  BUILT ON.** `.planning/amendments/m3_region1_nan_geometry_verdict.md:19-20` and `:30-37` record
  region-1 pair 4 — a NaN pair whose two members are **not in a coverage relation** (geometry
  **`disjoint`**; the NaN-implicated SNP at 5922718 is covered by a **THIRD** record, **DEL 5922716**
  spanning 5922716-5922722, and is therefore **EXCLUDED by the predicate**, with **NO residual**) —
  documented **BEFORE posting** and **DELIBERATELY EXCLUDED** from the 5-member expectation set.
  **mk7ze line 104 (repo draft line 271)** speaks of *"a settled 5-member expectation"*
  against **SIX** observed NaN pairs. The sixth is that disjoint pair. The posted expectation set
  was therefore constructed on the narrow reading at the time of writing.
- ⛔ **PAIR 4 IS A DIFFERENT CLASS FROM THE SURVIVOR AND MUST NOT BE READ AS THE SAME ONE.** The
  2026-09-04 entry glossed pair 4 as though **no record covered either of its members**, and used
  that same gloss for the chr7 survivor. **For pair 4 that gloss was FALSE.** Its NaN-implicated SNP
  **IS** covered — by a third record, **DEL 5922716** (span 5922716-5922722) — and the verdict
  annotates the pair *"2nd-order: SNP already occluded by DEL@5922716"*. Because one phrase served
  both cases, they read as a single class, from which a reader would conclude that **the survivor's
  class was documented before posting. IT WAS NOT.** The distinction, stated so it cannot be
  collapsed again: **pair 4 = known, handled, ZERO residual** — a covering record exists, so the
  predicate excludes it and nothing reaches the panel; **the chr7 survivor = unhandled, IN-PANEL
  residual** — **NO covering record exists for EITHER member**, so it **SURVIVES INTO THE PANEL**.
  ⚠ The citation above remains **sound for its own purpose** — pair 4's two members not being in a
  coverage relation is exactly what shows the narrow reading is what the expectation set was built
  on — but it establishes **NOTHING** about the survivor's class, which was **NOT** documented
  before posting.
- ⚠ **WHY THIS IS WRITTEN DOWN RATHER THAN LEFT AS AN INTERPRETATION:** mk7ze §(a) corrected a scope
  promotion and closed with *"The scope of the surviving claim is therefore stated here explicitly,
  so it cannot be promoted again."* §(a)'s remedy was EXPLICIT SCOPING IN THE RECORD, not narrow
  reading in correspondence. Recording the scope here converts the narrow reading from a defence
  available on challenge into a **COMMITMENT**.

### (5) ⭐ RECORDING THE SILENCE (not merely the survivor)

- **mk7ze does not claim that undefined or degraded r is EXHAUSTED by the occlusion predicate, and
  it does not discuss the measured degraded defined-row class.** ⚠ That is a bounded statement, and
  it replaces the 2026-09-03 draft's blanket assertion that mk7ze says nothing at all on the
  subject — which was too broad, because mk7ze **DOES** retain a raw-panel NaN-raise contract at
  **mk7ze lines 321-322 (repo draft lines 488-489)**: the raw per-region `.npz` reader continues to
  **RAISE** on any NaN rather than silently coercing it.
- **Sweep of the 333-line posted body:** ZERO hits for "defined row", "finite r", "degraded",
  "precision", "SE(". ⚠ The 2026-09-03 draft described this as a sweep of a 598-line body and
  called that body the posted one. 598 is the **repo draft working file**, not what was posted.
  The sweep's **CONCLUSION is unaffected**, since zero hits over the superset implies zero over
  the subset, **but the sentence stated a false fact about what was posted** and is corrected.
- ⚠ **THE SWEEP MISSED THE WORD THAT MATTERS, AND IT IS ADDED HERE: `undefined`.** It occurs
  **EXACTLY ONCE** in the posted body, at **mk7ze line 82 (repo draft line 249)**: *"The exclusion
  policy for an occluded variant is unaffected: its LD is structurally undefined"*. That is a
  **DIRECTIONAL** claim — its implication runs **occluded ⇒ undefined**, **NOT** undefined ⇒
  occluded — so it runs the **OTHER way** from the tail finding, **makes no completeness claim over
  undefined r**, and there is **nothing there for the tail finding to falsify**. It is disclosed here
  as swept and considered rather than silently omitted, and recorded because **a sweep that omits the
  one relevant term is not a sweep**.
- **That is a SILENCE, not a false statement. Nothing in the posted record is falsified.**
- But the silence covers a real, measured class, and a reader of §(c) meets in sequence a correct
  detector, a too-small expectation, a passed index-origin validation, and NaN-implicated ⊆
  geometric — from which the natural inference is that geometry brackets the undefined-r cases.
  **THAT INFERENCE IS NOT LICENSED BY THE TEXT.**
- So, in substance: *"mk7ze characterises the relationship between NaN-implicated occlusions and
  geometric occlusions; it does not claim that undefined or degraded r is exhausted by the
  occlusion predicate, and it does not discuss the degraded defined-row class. Such cases exist and
  are quantified here: one undefined pair with no covering record for EITHER member (upstream,
  offset -1), and 474
  pairs across 21 regions with a defined but degraded informative-carrier count. Neither class is
  claimed against in the posted record; both are reported here so the posted record's silence is
  not read as coverage."*

### (6) NO CARRIER FLOOR — and the definition PINNED before one exists

- **NO carrier floor is proposed and none is requested.** The informative-carrier DISTRIBUTION is
  reported so that a floor, if ever warranted, is chosen against data rather than against a
  hoped-for pass rate.
- 📌 **PINNED NOW:** ANY carrier floor MUST be defined on
  **min-on-the-pairwise-complete-INTERSECTION**, **NEVER** on rarer-by-overall-MAF. The two disagree
  on ~24% of exactly the rows a floor exists to catch, so a floor written against the wrong quantity
  would be **SILENTLY BLIND on a quarter of its target class**.
- **Mechanism:** occlusion strips ~99.4-99.9% of the deletion's carriers on the intersection, so the
  variant that is rarer by overall MAF stops being the one with fewer carriers on the intersection —
  asymmetric carrier loss **INVERTS THE RANK**. This is why the definitional disagreement is a
  signature of the first finding, not a third phenomenon.

### (7) THE COVARIATE SCAN — AN UNDERPOWERED NULL, NOT A NEGATIVE RESULT

- Three structural correlates were measured (95% CI, Fisher z with the Bonett-Wright Spearman
  standard error 1.03/sqrt(n-3)):
  rho **-0.199** [-0.590, +0.267], rho **-0.201** [-0.591, +0.266], rho **+0.004**
  [-0.440, +0.446].
- **At n=21 the design has 80% power only for |rho| >~ 0.61, and 24% power at rho 0.30.** These
  therefore exclude only **STRONG** correlates and remain consistent with moderate ones — for the
  cleanest of them, **|rho| up to 0.446 is inside the interval**. **This is an UNDERPOWERED NULL,
  not a negative result**, and the 2026-09-03 draft's instruction to record it as the latter is
  withdrawn.
- ⚠ The rho **+0.886** comparison does **not** calibrate the power of those three: it is a **COUNT
  against its own EXPOSURE** (both scale with window size, so a large rho there is near-mechanical),
  while the nulls are **SIZE-NORMALIZED PROPORTIONS** against size. Different tests.
- ⚠ **THE TWO ARTIFACT EXPLANATIONS WERE NOT BOTH ELIMINATED.** The 2026-09-03 draft claimed the
  heterogeneity was better established than an unexamined null on that basis. One was eliminated;
  the more plausible one was never tested:
  - **BETWEEN-window duplication cannot create dispersion** (simulated **0.98** under equal parent
    rates). **It does NOT follow that non-independence cannot: WITHIN-window clustering can and
    does.** Pairs sharing an occluding deletion do not flip independently, because carrier loss is
    a property of the deletion. An average of **two co-moving pairs per occluding deletion
    reproduces the observed 1.99 EXACTLY with zero parent-rate heterogeneity.**
    ⚠ **MEASURED 2026-09-08 — that hypothetical is NOT what the tail contains.** The size-weighted
    mean is **`c_eff` 1.494248** at **ICC 0.728930**, giving **deff 1.360272**, **BELOW** the ~2
    this sentence posits. The sentence stands as arithmetic about what **c ~ 2 WOULD** do; it is
    **not a description of the panel**. See **§(10)**.
  - ⚠ **REVIEWER ACCOUNTING, recorded 2026-09-08 — his framing adopted over ours because it is
    sharper.** His **SPECIFIC** mechanism (sub-window replication) **does** remain unable to
    create dispersion and **stays dead**. But the **GENERAL PRINCIPLE** he used to kill it —
    that non-independence can only **AMPLIFY** dispersion and never **GENERATE** it — was
    **FALSE**, and **a false general principle silently forecloses hypotheses nobody tested.**
    That is why **within-window clustering went untested while both parties believed the
    question settled.** It cost more than the specific error did.
  - ⚠ **PROVENANCE, CORRECTED 2026-09-17 at the reviewer's own request (§(10e)).** Stated as he
    stated it, and checked against the record before it was written: **(i)** the **BETWEEN-window**
    hypothesis (same-parent sub-window replication) was **his, and it was wrong** — the bullet above;
    **(ii)** the **WITHIN-window** mechanism and the **c=2 simulation** were **ours**, in
    `260904-dgi`'s `CONTENT-SPEC.md:45-56`: *"The operative dependence is WITHIN-window: pairs sharing
    an occluding deletion do not flip independently"* and *"c=2, ICC 1.0 -> mean phi 2.032"*;
    **(iii)** the measurement **confirmed that within-window clustering EXISTS** (ICC 0.73, §(10a))
    **without showing that it accounts for the dispersion** (§(10b)); **(iv)** the **Rao-Scott test
    was proposed by NEITHER party** (§(10c)). Our courier of the §(10) result credited him with
    pointing at within-window structure; **he declined that credit, the record agrees with him, and
    the credit never entered this entry.**
  - ⭐ **THE pairs-per-deletion DISTRIBUTION HAS NOW BEEN MEASURED (2026-09-08) — see §(10).**
    Until then the observed dispersion was **NOT attributable** to parent-region heterogeneity
    rather than to a cluster design effect, and the only operative structure on record was that
    **22.9%** of tail pairs are deletion-deletion neighbours (**564 of 2461**, panel-wide dedup
    basis; §(10) reports **573 of 2521 = 22.73%** on the per-region SUM basis and reconciles the
    two). ⚠ **That neighbour percentage was never a measurement of `c`**, and the measurement it
    was standing in for did **not** resolve Finding 2's magnitude as anticipated here — **it
    removed Finding 2's establishment instead.** The design effect is **1.360272** against an
    observed **1.99**: **clustering alone is not shown to reproduce the dispersion**, and the
    magnitude remains **unidentified**.
  - **The leave-one-out does not rule out an influential unit.** Leave-one-**WINDOW**-out gives
    **1.99-2.48** (worst-case p **0.0063**), but the two chr15 windows **shield each other**, so it
    cannot remove parent `00060` at all, and its minimum **is the headline itself**.
    Leave-one-**PARENT**-out over the **19 distinct parent regions** ranges **1.52-2.49** with
    worst-case **p 0.073**: parent region `00060` is influential enough that **its removal renders
    the heterogeneity non-significant at alpha 0.05.**
- ⛔ **Do NOT pre-register a dispersion FIGURE.**

### (8) EPISTEMIC STATUS — do not soften

- ⭐ **FINDING 2 IS NOT ESTABLISHED (recorded 2026-09-08).** Corrected for the **measured**
  within-window design effect, the between-region heterogeneity in POST-filter rate carries **at most
  weak evidence** under either **defensible** treatment of the chr15 window overlap (**p 0.0326** /
  **p 0.0517**, the same evidence; **p 0.2171** dropping both windows), is **not robustly
  distinguishable from a clustering-only explanation**, and its **magnitude is unidentified**.
  ⭐ **FINDING 1 IS UNCHANGED** and **Finding 3's status is unchanged.** Full statement, caveats and
  the measurement behind it: **§(10)**.

- **MEASURED, NOT PRE-REGISTERED.** The governing document
  `.planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-and-carrier-distribution.md:211-216`
  deliberately declined to state an expected value: *"an expectation written down now would be a
  number picked from what we hope passes."* That refusal is why these findings cannot have been
  shaped by an expectation.
- **The genuine pre-registration** is
  `.planning/debug/260826-PCS-ancestry-blind-manifest-read-8x-duplication-and-the-prereg-prediction.md`
  §(e), answered by RUN 1, confirmed 5/5 + histogram with ZERO adjustments on 2026-09-01.
- **The three values 3094/0/0 are a COMPLETION CHECK, NOT a pre-registration.**
- The run finished during a VM reboot: stdout and `$?` are **UNRECOVERABLE and were never seen**.
  Completion rests on the runtime reconciliation against the scanner's own independent measurement
  across all 21 regions (writes nothing on disagreement) plus the artifacts. **No pre-reboot hash
  exists, so the md5s anchor FORWARD, not backward.**

### (9) PROVENANCE

- `pcs_tail_verdicts.tsv` md5 `960f283734aea3b2c56c9249cf4fe94b`, 1031086 B
- `pcs_tail_summary.json` md5 `bd74c0d502d15ac4e2fb5e1bdafc72b1`, 38548 B
- both written 2026-09-02T21:07:03Z; launched 18:26:17Z; 2h40m46s wall.
- `bim_sha256` `9cc378b701277d57b54e8c1399ff5ceaeab7ae592783fce41271e7554feeeb99` (20,767,864 lines)
- `pairs_tsv_sha256` `eb2de2fd3d1af6e9fd39d1aada7e790dc03268a4a9f8afee3c809d4589123583` (353,090 lines)
- `regions_tsv_sha256` `e3c25ea083490017ffe7461fbcc1df5d3788e23f9c4130602c8bc9d040ce4d6a` — VERIFIED equal
  to `sha256sum config/ld_regions.tsv` at HEAD.
- `region_ids_selected = 276` is the ancestry-resolved MANIFEST size, **NOT** the 21 regions carrying
  rows. Stated explicitly so it is never read as a region count for this measurement.

- ⚠ **SECOND READ, 2026-09-08 (the clustering measurement of §(10)).** The same
  `pcs_tail_verdicts.tsv` was re-read VM-side at `/home/jupyter/occ_measure/pcs_tail_verdicts.tsv`.
  **All four banked anchors were matched BEFORE anything was computed** — md5
  `960f283734aea3b2c56c9249cf4fe94b`, **1,031,086 B**, **3,110 lines**, **32 columns** — and the
  file was **byte-identical after a six-day gap and a VM stop/start** (mtime 2026-09-02 21:07).
  The provenance above therefore holds against **this exact artifact**. **No re-run, no genotypes,
  no scan re-execution. Exit 0; all reconciliations passed.**

### (10) ⭐ THE CLUSTERING MEASUREMENT (2026-09-08) — A NEW FINDING, AND THE RETRACTION OF FINDING 2's ESTABLISHMENT

The measurement left outstanding in the status block above was fired by **Carter** on
**2026-09-08**. It is reported here in full, **including the parts that run against the conclusion
drawn from it**. Its provenance is the **SECOND READ** bullet in §(9).

#### (10a) NEW FINDING — WITHIN-WINDOW CLUSTERING IS REAL, MEASURED, AND STRONG

This did not exist before 2026-09-08 and is **reportable in its own right**, independently of what
it does to Finding 2. Pairs that share an occluding deletion are **STRONGLY correlated in PRE/POST
status**: carrier loss is a property of the **deletion**, so such pairs do **not** flip
independently. That is a **structural property of the tail** which anyone doing inference on this
panel downstream must carry.

- **n_pairs 2521**; **n_pairs_POST 474**; **POST-conflicts within a pair: 0** — the outcome is
  therefore a **well-defined property of the pair**, and the pair-level analysis is **not void**.
- **n_pairs_dual_anchored 573 = 22.73%** — deletion-deletion neighbours, two anchors each.
- **n_clusters 2105**; cluster-size distribution
  `{1: 1802, 2: 239, 3: 40, 4: 12, 5: 4, 6: 5, 7: 1, 8: 2}`; **c_max 8** at del_vid
  `chr15:91246748:CT:C`; **52 clusters span more than one region**.
- **Pairs in clusters of size >= 2: 719 of 2521 = 28.52%**, in **303** clusters; the other **1,802 of
  2521 (71.48%)** are **singletons**. ⚠ **This is NOT the 22.73% above, and the two must not be
  conflated:** 22.73% counts pairs anchored by **two** deletions (dual-anchored); 28.52% counts pairs
  whose anchoring deletion anchors **at least one other pair**. Reading 22.73% as the clustered
  fraction would understate it. Both are on the **per-region SUM** basis (SCOPE CAVEAT (1)).
- **c_mean 1.1976** — but the quantity a design effect actually depends on is the **SIZE-WEIGHTED**
  mean: **`c_eff` = sum(c^2)/sum(c) = 3767/2521 = 1.494248**.
- **ICC_hat = 0.728930** — ANOVA over the **k=303** clusters of size >= 2 (**N=719**,
  c0=2.371745). ⚠ **SCOPE: this ICC describes those 719 pairs (28.52% of 2521) ONLY** — among pairs
  sharing an anchoring deletion, PRE/POST status is highly correlated. It does **not** describe the
  **1,802 singletons (71.48%)**, and it must not be quoted as a tail-wide ICC without that denominator.
- **deff_hat = 1 + (`c_eff` - 1) * ICC = 1.360272**.

⚠ **CAVEATS THAT MUST TRAVEL WITH THIS FINDING:**

- **THREE regions return ICC exactly 1.000000** (`00027`, `00040__sub10`, `00161__sub13`). That is
  **the estimator AT ITS BOUNDARY** — zero within-cluster variance — and **NOT a fitted estimate.**
  It must never be quoted as one.
- **FIVE regions return NA** (too few clusters of size >= 2): `00017`, `00033`, `00053`, `00064`,
  `00088__sub01`.
- **The unit choice does not matter.** The row-level computation agrees closely: **ICC 0.7467,
  deff 1.3408 over 2601 clusters**. **No material unit disagreement.**
- ⭐ **THE CHAINING DIAGNOSTIC IS CLEAN — and this is the check that could have gone the other
  way.** Assigning each pair to a **single** anchoring deletion would **understate** clustering if
  pairs chained across deletions. They do not: **2051 connected components, largest 8 pairs
  (0.32%)**, with a distribution tracking the single-anchor clusters (**2051 vs 2105**). **The one
  way this measurement could have been biased toward its own conclusion is ruled out.**
- ⚠ **BASIS NOTE, so the two neighbour figures are not misread as a disagreement.** The
  **573 / 2521 = 22.73%** here is on the **per-region SUM** basis (SCOPE CAVEAT (1): a pair
  appearing in two regions is counted twice). The **564 / 2461 = 22.9%** quoted in §(7) is on the
  **panel-wide DEDUP** basis. **Different denominators, same structure**; the 60-pair gap between
  the bases is exactly the double-counting SCOPE CAVEAT (1) describes. ⚠ **Neither percentage is a
  measurement of `c`** — `c_eff` above is.

#### (10b) FINDING 2 IS **NOT ESTABLISHED**

Because the clustering is now **MEASURED**, the heterogeneity chi-square can be **CORRECTED for it
directly** instead of argued about: a **Rao-Scott** correction dividing each region's contribution
by **that region's own measured design effect**. In every row the **pooled POST rate is estimated
from the regions UNDER TEST in that row**, because the null being tested is that *those* regions
share a common rate (see the correction note below). Computed in-session, 2026-09-08:

| chr15 overlap treatment              | uncorrected phi | p       | DESIGN-CORRECTED phi | p          |
| ------------------------------------ | --------------- | ------- | -------------------- | ---------- |
| all 21 windows                       | 2.362           | 5.4e-4  | 1.931                | 0.0074     |
| drop `00060__sub13` (the HEADLINE)   | 1.988           | 0.0063  | **1.675**            | **0.0326** |
| drop `00060__sub12` (the MIRROR)     | 1.992           | 0.0062  | **1.579**            | **0.0517** |
| drop BOTH chr15 windows              | 1.518           | 0.0732  | 1.241                | 0.2171     |

⭐ **REPORT THE EVIDENCE, NOT WHICH SIDE OF A THRESHOLD IT FELL ON.** Dropping `sub13` and dropping
`sub12` are interchangeable **only as equally defensible handling choices made in advance**: both
were on record before either design-corrected p-value existed (the drop-`sub13` headline since
2026-09-02, the drop-`sub12` mirror in `260904-dgi`'s sensitivity table), the two windows overlap by
**6,000,001 bp** (SCOPE CAVEAT (3)) and **neither is privileged**. They are **NOT statistically
equivalent**: sub12 and sub13 carry **different measured design effects (1.096 vs 1.359)**, which is
why the two analyses separate **ONLY after the correction** (**p 0.0326** dropping `sub13`,
**p 0.0517** dropping `sub12`; **uncorrected they are indistinguishable (1.988 vs 1.992)**). In
evidence units they are **the same evidence**: -log10 p **1.49** vs **1.29**. ⛔ **Both are reported
and NEITHER is selected:** choosing either window now that both p-values are known, by ICC precision
or any other criterion, would be **post-hoc selection**. The evidence is also **AT MOST weak**: the
**five NA regions carry deff 1.0**, i.e. no correction (CONSERVATISM DISCLOSURE below), so a fuller
correction would lower phi.

**THE CONCLUSION, and it is not to be softened:**

> The between-region heterogeneity in POST-filter rate is **NOT ESTABLISHED**. Under either
> treatment of the chr15 window overlap, the design-corrected dispersion carries **at most weak
> evidence** of between-region heterogeneity beyond measured clustering: **p = 0.0326** dropping
> `00060__sub13` and **p = 0.0517** dropping `00060__sub12` (-log10 p **1.49** and **1.29**, the same
> evidence), and **p = 0.2171** with both chr15 windows dropped. The **magnitude is unidentified**,
> and the dispersion is **not robustly distinguishable from a clustering-only explanation**. The
> **DIRECTION** is positive under every treatment (**phi > 1.2 throughout**).

⚠ **CORRECTED 2026-09-08 (`260908-uer`) — THE ESTIMATOR WAS WRONG; THE CONCLUSION IS NOT.**
An earlier draft of this table estimated the pooled rate once from all 21 regions and reused that
one fixed value for every subset. **That is not the homogeneity test being reported:** the null is
that the regions **UNDER TEST** share a common rate, so the rate is estimated **from them**. The
table above is recomputed correctly. The correction **moved every subset figure slightly and did
NOT change the conclusion** — the p-value straddle that makes Finding 2 non-robust became
**TIGHTER** (**0.0326** vs **0.0517**, previously 0.0366 vs 0.0556). ⛔ This was an **error in the
analysis script, not a transcription fault**, and it is recorded as such. The three restatements of
the straddle elsewhere in this entry (the discharge bullet above, §(7) and §(8)) were aligned to the
corrected figures in the same edit; **no clustering figure moved**, because `c_eff`, ICC and
`deff` are computed from the measurement and involve **no pooled-rate choice** at all.

⭐ **A DISCREPANCY STANDING IN THE RECORD IS CLOSED BY THIS CORRECTION — AND THE OTHER SIDE WAS THE
RIGHT ONE.** Task `260908-u5k` deferred item **D1** flagged that this table gave **1.969** for the
drop-`sub13` uncorrected phi where the 2026-09-02 courier body gives **1.99**, and correctly
declined to adjudicate it. Under the subset estimator the value is **1.988**: **the courier's 1.99
was right and this table's 1.969 was the artifact** of the fixed-rate error. ⚠ **The corrected
column is also what §(7) already reported independently, which is why this is a reconciliation and
not a new disagreement:** §(7)'s leave-one-**WINDOW**-out worst case is **1.99 at p 0.0063** (its
minimum is the headline itself) and its leave-one-**PARENT**-out worst case is **p 0.073** — against
**1.988 / 0.0063** and **1.518 / 0.0732** in the corrected table. The **superseded** fixed-rate
column matched **neither**.

⚠ **CONSERVATISM DISCLOSURE, in our own disfavour, recorded before the conclusion is leaned on.**
The **five NA regions were assigned deff = 1.0 — that is, NO correction at all.** A fuller
correction would push phi **LOWER still**. The conservative choice therefore ran **AGAINST** the
conclusion now being drawn, which is part of why it is drawn.

⛔ **WHAT WAS NOT SHOWN, and the boundary is strict.** The measured design effect **1.360272** is
**BELOW** the observed dispersion **1.99**; on its own it **does not reproduce** that dispersion.
It **does** sit **INSIDE** the observed 95% CI **[1.1, 4.2]**, so clustering alone remains
statistically **CONSISTENT WITH** the entire effect — **but that is a FAILURE TO EXCLUDE, NOT a
demonstration.** ⛔ **Nothing in §(10a) is an explanation of Finding 2 and it must never be
reported as one.** The retraction rests on **the design-corrected evidence being at most weak under
either treatment of the overlap**, not on the design effect's point value.

#### (10c) THE DECISION RULE DID NOT FIRE, AND THE TEST THAT SETTLED IT WAS PROPOSED BY NEITHER PARTY

The rule set **before** the measurement (status block above, and §(7)) was: **c ~ 2 at high ICC**
reproduces the observed **1.99** from a homogeneous panel, whereas **c ~ 1** leaves the dispersion
open and parent-region heterogeneity live. **MEASURED: `c_eff` 1.494248 at ICC 0.728930 ->
deff 1.360272 — BETWEEN the two branches. NEITHER fired.** The comparison of point estimates was
therefore **not the decisive test at all**. What settled it was the **Rao-Scott correction**, and
**NEITHER party proposed it** — it was constructible only once the clustering had been measured.
**Recorded plainly, because a decision rule that fails to fire is a fact about the rule, not a
licence to pick whichever branch one prefers.**

#### (10d) WHAT IS UNCHANGED — stated explicitly, so the retraction is not over-read

- ⭐ **FINDING 1 IS UNTOUCHED BY ALL OF THIS.** Rows **2560 PRE / 534 POST of 3094 (17.26%)**;
  pairs **2047 PRE / 474 POST of 2521 (18.80%)**; **21/21** regions carry tail rows; **0** regions
  have zero POST. It is **COUNTING, NOT INFERENCE** — **no independence assumption enters it**, so
  a design effect cannot touch it. It has now survived **five reviewers, two adjudication rounds,
  and this measurement.**
- ⚠ **SCOPE OF FINDING 1 — the reviewer's own formulation, accepted 2026-09-17 (§(10e)).** In **all
  21 regions scanned** — **21 of the 276**-region ancestry-resolved manifest (§(9)), **7.6%** of the
  panel — a post-filter residual of **defined-but-degraded `r`** survives the **posted** predicate
  and is **invisible to the retained NaN-raise by construction**, because those rows are defined and
  so never produce a NaN. ⛔ **Stated at that scope deliberately: this says nothing about the 255
  regions NOT scanned, and nothing about any predicate other than the posted one.**
- **Finding 3's status is unchanged:** **no association DETECTED** on the definitional axis, and
  **both tests remain underpowered**.
- **The panel's contents are unchanged.** Nothing here changes an exclusion, a criterion or a
  branch; **no carrier floor** is introduced (§(6)); this remains a **DISCLOSURE, not an
  amendment** (§(1)).
- ⛔ **The status is unchanged: DRAFTED — NOT POSTED.** **Discharging the last open item is NOT
  authorization to post.** The posting decision is **Carter's alone**.

#### (10e) REVIEWER RESPONSE 2026-09-17 — framing corrected, provenance corrected, scope stated

The project's external reviewer answered the §(10) result on **2026-09-17**. His reply is banked as
received (pasted into the session; **not byte-verified** against the original) at
`.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md`.
He **accepted the disposition as stated**, objected to the sentence that carried it, and declined a
credit. **The disposition does not change: Finding 2 is NOT ESTABLISHED.** Every site that carried
the old framing was aligned in this edit (the discharge bullet in the status block, §(2), §(8) and
§(10b)), following the precedent of the `260908-uer` correction note above.

- ⚠ **FRAMING — the "straddle" is withdrawn as a reading of the evidence.** This entry had said that
  two interchangeable overlap treatments "straddle p = 0.05", that "a coin-flip between two equally
  defensible analyses" moves the result across the threshold, and that the significance "is an
  artifact of analytic choice". The two design-corrected p-values, **0.0326** and **0.0517**, are
  **1.49** and **1.29** in -log10 p: **the same evidence**. That they fall on opposite sides of a
  threshold is a property of the **threshold**, not of the data, and reporting which side each fell
  on is the calibrate-to-a-threshold error run in reverse. The aligned sites now report the evidence:
  **at most weak** under either treatment, **p 0.2171** with both chr15 windows dropped, magnitude
  unidentified, and not robustly distinguishable from a clustering-only explanation. **"At most"**
  because the five NA regions carry deff 1.0, so a fuller correction lowers phi. ⚠ The `260908-uer`
  correction note keeps its original wording and numbers: it records what that edit did. ⚠ Its
  parenthetical names the three restatements it then aligned as the discharge bullet, §(7) and §(8);
  the third was in fact **§(2)** — §(7) carried the design effect, never the straddle. The note is
  left exactly as written because it is the historical record; this clause is the correction.
- ⚠ **"INTERCHANGEABLE" — scoped, and NO window is selected.** The reviewer also argued that, given
  their different design effects (**1.096** vs **1.359**), the better-corrected window is determinable
  from the data. **Declined:** both p-values are now known, so choosing either window, by ICC
  precision or any other criterion, would be **post-hoc selection**. "Interchangeable" now means
  **equally defensible handling choices made in advance**, **not statistically equivalent**, and both
  analyses stay reported. ⭐ **He ACCEPTED this scoping on 2026-09-17**, in a closure banked as
  received (**not byte-verified**) at
  `.planning/quick/260917-pff-bank-the-reviewer-closure-on-finding-2-r/260917-pff-SETH-CLOSURE-finding2-review-as-received.md`.
  He accepted **all seven points** of our reply and **WITHDREW BOTH of his objections** — the pooled
  design-effect share, and this post-hoc window selector, which he named as his own threshold
  objection applied to the selector. **He closed with no open objection**, and nothing further is
  expected from him until there is a new measurement or a posting decision.
- ⚠ **SCOPE — two quantities separated, and the ICC's denominator attached (§(10a)).** **22.73%**
  (573 of 2521) of pairs are dual-anchored; **28.52%** (719 of 2521, in 303 clusters) are in clusters
  of size >= 2; the other **1,802 (71.48%)** are singletons, which the ICC does not describe.
- ⚠ **PROVENANCE — corrected in §(7)'s reviewer accounting.** Our courier of the §(10) result
  credited the reviewer with pointing at within-window structure. **He declined the credit, and the
  record agrees with him:** the within-window mechanism and its simulation were ours.
- **Finding 1's counts and its claim are unchanged.** ⚠ On the same date, a **scope sentence** in
  the reviewer's own accepted formulation was added beside it in §(10d) (quick `260917-pff`): it
  states the scope of what was measured — 21 of 21 scanned regions, the **posted** predicate, and the
  retained **NaN-raise** — and changes none of the counts.
- ⛔ **The status is unchanged: DRAFTED — NOT POSTED.** A reviewer response is **NOT authorization to
  post.** The posting decision is **Carter's alone**.
