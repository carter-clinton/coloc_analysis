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
