# Gate G0 disposition — proceed with RW 2.0 migration WITHOUT Abby's reply

**Date:** 2026-05-29
**Decision:** Proceed to Phase 2 MIGRATE (RW 2.0 Steps 1–4) without waiting for a Zendesk #57144 reply from Abby Doyle / AoU engineering.

## Why this is the correct G0 disposition (not a bypass)

Gate G0's *purpose* was to protect the Track 1 credit-recovery evidence + Abby's
engineering team's ability to assess the claim. That purpose is satisfied by the
**preserve-first plan**, not by waiting for a reply:

1. **The clean immutable record already exists.** Forensic mirror committed to NCSU at `c81ac4d` (bundle + MANIFEST with the `_SUCCESS` mtimes) + pre-migration inventory + env-panel snapshot at `5a9b752`. Tech support has a complete record whenever they engage.
2. **The workspace bucket survives migration.** The catastrophe MTs (`ld/mt_*_qc.mt/`) + the full `forensics/` dir (hail.log.*, jstack/pyspy/yarn captures, AOU-1 backups, the mirror bundle) persist across the Legacy→RW 2.0 migration. Migrating does not erase the evidence.
3. **Legacy is being decommissioned** — the forced 2026-06-30 migration *is* the Legacy retirement. The Legacy-reproduction window closes at 6/30 regardless of when we migrate, so waiting buys no reproduction capability.
4. **Abby's reply timeline is unknown** and cannot be allowed to run past the hard deadline. Carter directive 2026-05-29: the preservation was done precisely so migration need not wait on tech support.

## Residual risk accepted

Cannot re-run on the *exact* Legacy env instance post-migration — but Legacy retires by 6/30 anyway, the env was already a throwaway recreate, and all diagnostic captures are preserved on NCSU + in the bucket. Accepted.

## Audit-trail note

This is the documented "proceed without reply" decision the playbook G0 table anticipates. Reflect in the OSF deviation trail (`.planning/amendments/osf_deviations.md`) at the next manuscript/OSF pass: "Wave-1 LD-panel rebuild migrated AoU workspace Legacy→RW 2.0 on/after 2026-05-29 with catastrophe forensics preserved on NCSU; AoU engineering credit-recovery dialogue (Zendesk #57144) was still open at migration time; migration was platform-mandated (Legacy decommission, hard deadline 2026-06-30)."
