---
phase: m3-aou-afr-ld-panel-build
plan: 07c
subsystem: occlusion / present-rate + lockstep sumstats filter
tags: [ld, occlusion, present-rate, lockstep, sumstats, aou, afr, tdd]
requires: ["07a (the RED suites)", "07b (occlusion_manifest producer + span filter)"]
provides:
  - "occlusion_present_rate_scan.scan_present_rate — per-variant PRESENT-vs-ABSENT k/n over the public GRCh37 AFR sumstats; directly feedable to enrich_occlusion_manifest(present_rate=...)"
  - "drop_occluded_from_sumstats.drop_occluded_from_sumstats — reusable manifest-driven (CHR,POS) drop-only lockstep sumstats filter, idempotent on its own output"
affects:
  - "m3-04 consume replan (the wiring seam this plan deliberately did NOT wire)"
  - "Angle-1/3 occlusion catalog (present-rate is the catalog payload)"
tech-stack:
  added: []
  patterns:
    - "FILE-IN / FILE-OUT module.function, mirroring plink_ld_to_npz.plink_ld_to_npz"
    - "canonical (chr, pos) key normalization mirroring occlusion_manifest._present_rate_key"
    - "BY-NAME header column location (hinge-check awk prototype), never positional"
key-files:
  created:
    - src/python/occlusion_present_rate_scan.py
    - src/python/drop_occluded_from_sumstats.py
  modified: []
decisions:
  - "T3 canonicalizes the returned key ('chr1'/'1' -> 1) rather than echoing the caller's tuple — load-bearing: the real producer emits chr as the STRING '1', and echoing it back would make the consumer match zero liftable rows and RAISE"
  - "T3 resolves the trait label from the harmonized TRAIT column (filename fallback) — the RED does not discriminate; TRAIT survives a renamed file"
  - "T4 fails closed on a Stage-A manifest (no pos_grch37) rather than reporting a clean n_dropped == 0 that would orphan every occluded variant"
  - "T4 skips an unlifted manifest row with an explicit STDERR warning rather than raising or guessing a coordinate"
  - "T3 and T4 each carry a private header locator rather than sharing one — the two commits must stay independently revertible"
metrics:
  duration: "~35 min"
  tasks: 2
  files: 2
  completed: 2026-07-16
---

# Phase m3 Plan 07c: Present-Rate + Lockstep Summary

Two modules landed TDD-GREEN against the 07a REDs: the present-rate scan that
quantifies the *scientific cost* of the pre-registered exclusion policy, and the
reusable lockstep filter that stops a panel-excluded variant from being orphaned in
the sumstats.

**Full tests/m3: 0 failed / 420 passed / 31 skipped** — exactly the predicted final
state (405 baseline + the 15 now-green REDs). No test outside those 15 changed state.

## Commits

| Task | Commit | Suite | Result |
|------|--------|-------|--------|
| T3 — `occlusion_present_rate_scan.py` | `c475da7` | `test_occlusion_present_rate_scan.py` | 6 RED → **6 passed** |
| T4 — `drop_occluded_from_sumstats.py` | `ed3e122` | `test_occlusion_lockstep_drop.py` | 9 RED → **9 passed** |

Plan-scoped slice (`-k "present_rate or lockstep or occlusion"`): **48 passed, 1
skipped** (the skip is pre-existing and unrelated; total skips unchanged at 31).

## T3 — the present-rate scan

`scan_present_rate(variants_grch37, sumstats_paths) -> {(chr, pos): {...}}`, keyed on
the canonical GRCh37 `(chr:int, pos:int)` tuple, values `{n_traits_present,
n_traits_scanned, present_rate, traits_present}` — `STAGE_B_TRAIT_COLUMNS` + the rate.

- **CHR/POS located BY NAME** (CHR else col 1; POS else BP else col 2 — the
  hinge-check awk prototype). The RED's reordered-columns fixture passes.
- Absent variant → a **record** with rate `0.0`, never a missing key or a divide error.
- A multi-allelic collision counts **once** toward k (`snp_id_bridge.R` first-wins) —
  counting hits instead of files would let `present_rate` exceed 1.0.
- stdlib-only, streamed line-wise (a genome-wide sumstats is never materialized);
  handles `.tsv` and `.tsv.bgz` (BGZF is gzip-compatible).

### The seam claim was verified, not assumed

The plan asserts T3's return is "directly feedable to
`enrich_occlusion_manifest(present_rate=...)` — write NO adapter." **No test covers
that end-to-end**, so I proved it out-of-band against the real producer + real
hg38ToHg19 chain before committing (scratch only, not committed):

- the producer hands over `chr` as the **string `'1'`** (`build_region_records` does
  `"chr": str(raw[0])`), while the RED keys on the **int `1`**;
- canonicalizing both sides to `1` is what makes the join land. snpC GRCh38 5922718 →
  GRCh37 5982778 (the settled known-answer anchor) enriched cleanly to
  `traits_present=['bmi','ldl'], n_traits_present=2, n_traits_scanned=3`.

Had I preserved the caller's tuple verbatim — the other defensible reading of the RED,
which passes all 6 tests — the consumer would have matched **zero liftable rows and
raised ValueError** in integration. The RED alone does not pin this; the seam does.

## T4 — the lockstep drop filter

`drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> {n_in,
n_dropped, n_out}`. **FILE-IN / FILE-OUT** (mirroring `plink_ld_to_npz`), not
DataFrame-in/tuple-out.

- Drops exactly the manifest's GRCh37 `(chr, pos_grch37)`; **CHR-aware** (a POS-only
  key would silently delete unrelated variants genome-wide).
- **Drop-only, no re-key**: `SNP_ID` untouched, survivors byte-identical and in order.
  Implemented by streaming **binary** so surviving bytes are never decoded/re-encoded
  or newline-translated on the way out.
- **Idempotent on its own output**: re-reads what it writes, `n_dropped == 0`,
  byte-identical.
- Every drop **logged to STDERR** with manifest provenance (`print(..., file=sys.stderr)`
  — deliberately not `logging`, whose handler would bind a stale `sys.stderr` and escape
  `capsys`).
- `n_in - n_dropped == n_out`, and `n_out` == body rows actually written.
- The **producer→consumer seam test runs the real 07b manifest end-to-end** through
  pyliftover + the chain, and **does not skip** (9 passed, 0 skipped).

## Deviations from Plan

### Auto-fixed / auto-added

**1. [Rule 2 — missing critical functionality] T4 fails closed on a Stage-A manifest**
- **Found during:** Task 2. Neither the RED nor the plan covers a manifest lacking
  `pos_grch37` (Stage A carries `pos_grch38` only).
- **Issue:** the natural implementation reports a clean `n_dropped == 0` — a green
  result that silently orphans **every** occluded variant, i.e. exactly the failure
  the module exists to prevent, wearing a passing badge.
- **Fix:** raise `ValueError` naming `add_grch37_positions` / `enrich_occlusion_manifest`.
- **Commit:** `ed3e122`

**2. [Rule 2 — provenance] T4 warns on an unlifted manifest row instead of silently skipping**
- **Found during:** Task 2. A row with `pos_grch37` NA has no GRCh37 coordinate and
  cannot be located in GRCh37 sumstats at all.
- **Fix:** skip + explicit STDERR warning. *Not* a raise — `enrich_occlusion_manifest`'s
  documented boundary treats a liftover/assembly-gap variant as "rare but plausible", and
  hard-aborting a whole trait over one would be wrong. *Not* a guessed coordinate — a
  plausible-but-wrong one drops the WRONG row. The warning is the honest record that
  lockstep could not be enforced there.
- **Commit:** `ed3e122`

### Rejected simplification

An early-exit optimization in T3's scan loop (stop once all targets are found) was
written and then **removed**: for a handful of occluded variants scattered genome-wide
the scan reads to EOF anyway, so it bought nothing measurable while complicating a
scientific scanner. Per `feedback_verify_assumption_before_shipping`, an unmeasured
cost claim does not ship.

## Where the RED and the plan still disagree

**Nothing contradictory — the 8d4087a reconciliation is accurate.** Every spec claim I
checked against the assertions held: signatures, key type, the four value names,
FILE-IN/FILE-OUT, the counts dict, the STDERR mechanism, idempotence-on-own-output, the
absence of a `build=` kwarg. Both suites went green with a **0-line diff to `tests/`**.

Three places where the plan is **silent** rather than wrong (unpinned degrees of freedom
the executor had to choose; flagged so the choices are auditable):

1. **T3 `traits_present` label source is not pinned.** The RED's two fixtures agree
   (`bmi.AFR.tsv` carries `TRAIT=bmi`), so filename-derived and TRAIT-column-derived
   labels are indistinguishable. The reordered-columns fixture *would* discriminate
   (`reo.AFR.tsv` carries `TRAIT=ldl`) but asserts only the rate. **Chose the TRAIT
   column** (authoritative; survives a renamed file), filename as fallback.
2. **T3's key canonicalization is not pinned** — see the seam verification above. The
   RED passes either way; only the real producer reveals which is correct.
3. **T4's unlifted / Stage-A manifest handling is not pinned** — see the two Rule-2 items.

## Observations for the Angle-1/3 catalog (out of scope, not actioned)

- `enrich_occlusion_manifest` pulls only `STAGE_B_TRAIT_COLUMNS` from the present_rate
  dict, so **`present_rate` itself is not persisted as a manifest column** — it is
  derivable as `n_traits_present / n_traits_scanned`. Behaviour of the shipped consumer
  (63bdb59), consistent with the plan; noting it so the catalog step doesn't hunt for it.
- `traits_present` serializes to the TSV as a **stringified Python list** (`['bmi', 'ldl']`),
  so a future catalog reader gets a `str`, not a `list`. Pre-existing 63bdb59 consumer
  behaviour, unchanged here; worth a parse/serialization decision when the catalog lands.

## Gates

| Gate | Result |
|------|--------|
| Full `tests/m3` | **420 passed / 31 skipped / 0 failed** (6m32s) |
| REDs unedited (`git diff --stat 55eae23..HEAD -- tests/`) | **EMPTY** |
| Frozen contracts (`plink_ld_to_npz.py`, `ld_npz_to_rds.R`, `condition_ld_matrix.py`) | **EMPTY diff** |
| `finemap.smk` (m3-04 disclosed deferral) | **UNTOUCHED** |
| Files changed vs baseline | exactly the 2 new modules (+423 lines, 0 deletions) |
| `grep -c present_rate` T3 | 11 (≥1) |
| `grep -c "SUPERSEDED-PENDING-REPLAN\|m3-04"` T4 | 6 (≥1) |
| Perimeter / loop / spend | **NONE** — no gsutil/gcloud/Hail/network; $0 |
| m3-06 `condition_ld_matrix` | not imported, not referenced; NaN→0 stays dead |
| REQ-PUBLIC-DATA-ONLY | synthetic fixtures + public GRCh37 sumstats semantics only |

The real 9-file genome-wide present-rate scan remains a **GATED integration step** — not
run here, per the plan and the execution gate.

## Self-Check: PASSED

- `src/python/occlusion_present_rate_scan.py` — FOUND
- `src/python/drop_occluded_from_sumstats.py` — FOUND
- commit `c475da7` — FOUND
- commit `ed3e122` — FOUND
