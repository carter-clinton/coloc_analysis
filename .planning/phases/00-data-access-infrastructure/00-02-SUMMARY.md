---
phase: 00-data-access-infrastructure
plan: 02
subsystem: data-access
tags: [curl, connectivity, synapse, decode, gtex, finngen, pan-ukbb, bbj, mvp, gbmi, osf]

# Dependency graph
requires:
  - phase: none
    provides: "No prior phase dependencies"
provides:
  - "HPC connectivity verification for all 8 open-access data sources"
  - "Updated data_access.md with verification annotations and checked Day-1 items"
affects: [01-coloc-susie, 02-qtl-coloc, 03-mr-analysis, 09-replication]

# Tech tracking
tech-stack:
  added: [curl]
  patterns: [HEAD-request connectivity verification, data access tracker annotations]

key-files:
  created: []
  modified: [.planning/data_access.md]

key-decisions:
  - "GTEx v8 GCS path correction: bulk-qtl/v8/ not bulk-gex/v8/"
  - "FinnGen R13/R14 bucket names differ from R10 convention; exact URLs TBD after registration"
  - "GBMI reclassified from registration-required to open-access (no registration gate found)"

patterns-established:
  - "HPC connectivity annotation: each data source section gets an '**HPC connectivity:**' line with date, command, and HTTP result"

requirements-completed: []

# Metrics
duration: 7min
completed: 2026-04-10
status: checkpoint-pending
---

# Phase 00 Plan 02: Data Source Connectivity and Portal Registration Summary

**HPC connectivity verified for all 8 open-access data sources (Synapse, deCODE, GTEx, FinnGen, Pan-UKBB, BBJ, MVP, GBMI); checkpoint pending for user portal registrations and OSF pre-registration**

## Status: CHECKPOINT PENDING

This plan paused at Task 2 (checkpoint:human-verify). Task 1 is complete; Task 2 requires user action for portal registrations, browser verification (deCODE), and OSF pre-registration submission.

## Performance

- **Duration:** 7 min (Task 1 only)
- **Started:** 2026-04-10T18:54:01Z
- **Paused at:** 2026-04-10T19:01:00Z
- **Tasks:** 1 of 2 complete
- **Files modified:** 1

## Accomplishments
- All 8 open-access data sources confirmed reachable from NCSU HPC via curl HEAD requests
- Updated data_access.md with per-source HPC connectivity annotations including dates, HTTP status codes, and exact commands used
- Updated Day-1 action checklist: 7 items checked off (up from 2)
- Discovered and documented GTEx v8 GCS path correction (bulk-qtl/v8/ not bulk-gex/v8/)
- Identified FinnGen R13/R14 URL pattern discrepancy (R10 accessible; R13/R14 bucket names TBD)

## Task Commits

Each task was committed atomically:

1. **Task 1: Verify data source connectivity and prepare download scripts** - `12abd06` (feat)

## Files Created/Modified
- `.planning/data_access.md` - Updated with HPC connectivity verification for all 8 sources, checked off 5 additional Day-1 checklist items

## Decisions Made
- GTEx v8 correct GCS path is `bulk-qtl/v8/single-tissue-cis-qtl/`, not `bulk-gex/v8/single-tissue-cis-qtl/` -- this matters for Snakemake download rules in Phase 1+
- FinnGen R10 public bucket confirmed accessible; R13/R14 exact URLs unknown until after registration (different naming convention or distribution mechanism)
- GBMI resources page is fully open (no registration required) -- reclassified from "register with GBMI" to checked off

## Deviations from Plan

None - plan executed exactly as written for Task 1.

## Issues Encountered
- GTEx v8 URL in plan (`https://storage.googleapis.com/adult-gtex/bulk-gex/v8/single-tissue-cis-qtl/GTEx_Analysis_v8_eQTL.tar`) returned 404. Investigated and found correct path uses `bulk-qtl/` prefix instead of `bulk-gex/`. Verified correct file at `bulk-qtl/v8/single-tissue-cis-qtl/GTEx_Analysis_v8_eQTL.tar` (HTTP 200, 1.56 GB). Documented correction in data_access.md.

## Pending: Task 2 (Checkpoint)

Task 2 is a `checkpoint:human-verify` requiring user action for:
1. Synapse certified-user registration (UKB-PPP access)
2. FinnGen registration (click-wrap form)
3. deCODE portal manual browser verification
4. OSF pre-registration submission with DOI
5. AoU DURA status check with NC State Signing Official

## Next Phase Readiness
- Connectivity confirmed for all sources; download Snakemake rules can proceed once Phase 1 begins
- Portal registrations (Synapse, FinnGen) must be completed before Phase 2 (QTL coloc)
- OSF pre-registration must be submitted before results generation (per D-26)

---
*Phase: 00-data-access-infrastructure*
*Paused at checkpoint: 2026-04-10*
