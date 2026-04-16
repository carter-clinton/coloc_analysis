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

*None yet.*
