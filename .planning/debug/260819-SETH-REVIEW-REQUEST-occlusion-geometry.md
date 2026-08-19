# Review request — the fire STOPPED at STEP 7 on first real-data contact; attack our adjudication before we act on it

> Provenance: drafted in-repo 2026-08-19 (fire morning), $0, zero perimeter contact
> beyond the read-only probes quoted verbatim below (run in-perimeter by the
> Workbench-side agent under R3 stop discipline; VM now STOPPED). No OSF contact
> by any agent. Nothing fired; Stage A was never reached; nothing banked.
>
> This is a BRIEF-BLIND review request: everything below the evidence line is OUR
> reading, and the ask is that you attack it against the evidence, not confirm it.
> One provenance fact stated plainly because it bears on your review: the oracle
> under examination is the one YOUR July methodologist pass settled (the record
> tags it "Seth 5/5 vs the geometry verdict"). Last week you re-ran your own
> broken checks and reported them; same protocol, other direction.

## The event

STEP 7 (the gated real-`.bim` known-answer test — the detector's FIRST-ever
contact with real data; every prior run was synthetic or skipped) FAILED, and not
with the off-by-one signature the card licenses a one-line remedy for. The agent
stopped correctly, two read-only probes were authorized, and the fire is HELD
before Stage A. All human gates up to that point had passed (6b: the posted body
re-measured 9,695 / c19be8b2... at fire time — unchanged since the adjudication).

## The evidence (verbatim, in-perimeter, read-only)

Probe 2, structural, mirroring the test's own loading (osf.load_bim_rows +
detect_occluded_variants over data/aou/region1_window.bim):

    n_rows: 102421
    n_occluded: 231
    oracle_subset_of_observed: True
    oracle_missing_from_observed: []
    n_deletion_REF_rows: 7951
    max_span: 170
    clause_d_ceiling_this_window: 51.2105

Probe 1 (-vv full set diff) is banked on the VM at /home/jupyter/step7_vv.txt.
Structural features reported by the agent: the extra members often come in
consecutive-index runs (65340-65343, 71567-71573, 101915-101920), and the oracle
members appear unmarked in the diff (subset confirmed).

The settled oracle the test asserts (tests/m3/test_occlusion_span_filter.py:186,
:521-523): occluded row indices exactly {10328, 44784, 46714, 59097, 66730}
(0-based), AND the window's multi-base-REF inventory exactly 7 deletions with
spans 60/29/7/31/31/17/29 bp. The failure is therefore 226 extra detections plus
7,944 extra deletions relative to the oracle — no shift, no displacement, nothing
missing.

The pre-registered clause the counts collide with (the posted amendment, verbatim,
line 61 of the repo canonical):

    (d) Anomaly gate (per region). If the count of occlusion-excluded variants in
    a region exceeds 0.05 percent of the region's variant count (n_excluded ≤
    0.0005 × n_var; the same fractional gate as the withdrawn ceiling, re-purposed
    to exclusions), the region is treated as a substrate anomaly: it is NOT
    auto-excluded, it is deferred for re-diagnosis, and it is disclosed as a
    deviation. A large excluded fraction indicates an LD-construction or
    variant-representation problem beyond isolated occlusion.

Plus the pre-registered outcome branch: BRANCH_AFR_OCC_DEFERRED — "the region's
occlusion-exclusion count exceeds the anomaly gate; the region is deferred, not
auto-excluded, and disclosed as a deviation with its occlusion count."

## Our adjudication — the claim you are asked to attack

(1) The detector behaved exactly per its synthetic-pinned rule (22 fixture tests,
all green, unchanged). (2) The oracle was a FALSE EXTRAPOLATION: the July review
promoted "the 7 deletions implicated in June's observed NaN pairs" into "the
window's entire deletion inventory," and the 5 NaN-implicated partners into "the
full occluded set" — but observable-NaN is a strict subset of geometric
occlusion (NaN requires complete-case zero variance; span coverage does not).
(3) The 5-at-exact-indices subset result means STEP 7's actual purpose —
index-origin validation — PASSED. (4) 231 > 51.2 means region 1 defers by design
at Stage A, and if ~0.23% is typical of all 276 regions, bankable ≈ 0: the
ceiling's calibration premise (occlusion is ~5-per-100k rare) is measured false,
while the exclusion POLICY itself is scientifically unaffected (0.23% of variants
is negligible for a panel). (5) The pre-registration's own machinery — defer for
re-diagnosis, disclose, amend openly — is the sanctioned route; the constant is
never touched quietly.

Specific attack surfaces we want pressure on:
- Is there ANY credible detector-defect story consistent with 231-with-
  consecutive-runs? (Our reading: consecutive runs = multiallelic split records
  co-located under one deletion span — geometry, not defect. The detector's
  strict POS_D < POS_V co-location rule is pinned by its own fixture test.)
- Is 7,951 multi-base-REF rows in 102,421 (7.8%) plausible for AoU AFR WGS, or
  does that number itself indicate a representation problem (e.g., un-normalized
  multiallelics) — which is EXACTLY what clause (d)'s interpretation sentence
  contemplates? Note the oracle also asserted "same-position variants = 0
  (bcftools norm -m fixes none)" — reconcile that with the consecutive-run
  structure if you can; we could not, yet.
- Is excluding 231/102,421 actually negligible for downstream SuSiE/coloc, or is
  there a failure mode we are waving past (e.g., occluded variants clustering at
  exactly the loci that matter)?

## The decision space (do not pick for us; attack the premises of each)

A. Cheap Stage-A probe fire: let region 1 land BRANCH_AFR_OCC_DEFERRED as the
   empirical record of the pre-registered gate working, then amend with the
   measurement in hand.
B. Amend first: new OSF amendment recalibrating clause (d) with full disclosure
   (never a silent swap), then fire.
C. Measurement pass first: run the DETECTOR ONLY over all 276 per-region windows
   on the VM (no LD, no banking, minutes-cheap) to learn the occlusion-count
   distribution before recalibrating anything — then amend from data, then fire.

## What is held

The fire is HELD before Stage A. Nothing was banked; the deferral machinery was
never exercised; the VM is stopped; the failed test and both probe outputs are
preserved as the record. No test, no frozen file, and no pre-registered constant
has been edited. A full provenance trace (how 7/5 propagated into the test, the
runbook expectations, and the mechanical gate's expected_records=5) is being
assembled on the planning side and will follow — this note deliberately precedes
it so your first read is against the evidence, not our dossier.

Nothing further is needed from you beyond the attack. If your verdict is that our
adjudication is wrong — say so loudly; the last two weeks established which of us
finding the other's error is the trade working.
