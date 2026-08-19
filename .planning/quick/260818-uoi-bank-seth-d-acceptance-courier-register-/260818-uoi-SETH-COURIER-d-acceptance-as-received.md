# Seth courier — D-01…D-13 ACCEPTED, three of his checks reproduced broken (as received)

> Provenance: received 2026-08-18 ~22:04 EDT, pasted by Carter into the NCSU session,
> in reply to our 260818-sml adjudication courier (22,420 B /
> `dcb8a9c2f81e4815543fea3744173184`). AS-RECEIVED transcription of a chat-rendered
> body — no byte anchors supplied. This closes the adjudication thread: all thirteen
> accepted, zero contested; he re-ran his own prototype against the shipped status
> strings and reproduced all three defects himself.

---

Seth — D-01…D-13 accepted. Three of my checks were BROKEN and I reproduced all three.

Every adjudication accepted. I did not take them on report: I reloaded my own prototype and re-ran the failures myself. Three of my nine checks were defective, and one of them (D-02) would have stopped a healthy fire. Your file:line discipline is what surfaced them — arguing with the line rather than the claim is the right protocol and I have nothing to argue with.

## Reproduced against my own code — all three confirmed

D-02, the consequential one. My classify_deferrals on the REAL shipped status strings:

    input : "deferred_infeasible_square: n_var=181004 > ceiling=120000"
            "deferred_occlusion_anomaly: 73 occluded of 140000 (ceiling 70)"
    result: FAIL / HARD_STOP -> "unrecognized status value(s) [...]"

Confirmed. I wrote s not in _EXPECTED_DEFERRALS against bare tokens while the producer emits detail-in-status by design (:831, :854). Every real deferral, ~29+ of them, would have HARD_STOPped a healthy $385–1,084 fire on the gates working — at every Stage-C check-in. Prefix-matching is correct.

D-02b, and you were right that this one is worse. My same function on the statuses that do not start with deferred:

    input : "skipped_idempotent", "verify_failed", "error: boom"
    result: PASS

All three passed silently, as if ok. skipped_idempotent is emitted for every resumed region (:774) — after any Spot recycle that is most of them — and verify_failed (:991) never uploads while error: (:1028) banked nothing. My prefix bug was loud; this hole was quiet, and a quiet hole in a gate is the worse defect. Your ok-class / deferral / failure / unknown partition fixes both at once.

D-09, my own false-positive. My estimate_markers on innocent CORRECT text:

    input : "...affected span estimated from Stage B then MEASURED at rollup: 412.7 Mb."
    result: FAIL, tripped on marker 'estimate'

A gate that goes red on correct text gets disabled — so this was worse than dead weight; it was a future reason to switch the check off. And you measured that two of my four markers (ESTIMATE, ~29) do not occur in the file at all: my check was passing on one live marker out of four. Measured sentinels plus the required MEASURED: provenance line is strictly better, and the vacuity-FAIL on a renamed heading closes the hole I did not think of — I would have shipped a check that a heading rename silently satisfies.

D-01. Accepted, and it is the deepest correction. I specified the wrong reader: read_square_bin reads the .ld.bin, which _reclaim_region_scratch deletes in gs:// mode — so my check would have run against an artifact that does not survive the region. And content_verify_npz returns (ok, reason) rather than raising, so my try/except shape would have read ok=False as a clean run: a fail-closed check that fails open on the real code path. Your four-step version — shipped verifier first, then the frozen blocked scanner only on the failing path to attribute cause — is right, and pinning the "ok entails NaN-free" implication with the two NaN fixtures converts my assumption into a measured fact. Distinguishing "NaN present" from "shipped reason carried verbatim, NOT claiming NaN" is the misattribution guard the frozen reader's own comment (plink_ld_to_npz.py:213-217) demands.

D-04 / D-05. Both accepted. verify_failed and error: passing my classifier is the same defect as D-02b. And D-05 is the sharper principle: my startswith("deferred") was narrower than the code it gates (:1161 raises on ANY non-ok under --fail-fast), and a check narrower than its subject gives false assurance. Exact-ok is correct.

D-06 / D-07 / D-08 / D-10. Agreed, and the shared lesson is one I got wrong four times: I re-declared shipped constants instead of importing them. 256, 0.0005, 120, 276 each happened to be right today, which is exactly what makes a copied constant dangerous — it is a silent divergence with no enforcer. Importing, plus the monkeypatch test proving the gate FOLLOWS the producer's module global, plus the repo-wide grep forbidding the literals, is the correct treatment. D-10 making n_total required is better than my default: the 322 = 161 x 2 staleness you cite is the precise failure mode a default invites.

D-03. The AST drift enforcer is better than anything I proposed. An allow-list with no staleness detector is a comment; walking the producer for every result["status"] assignment — with the non-vacuity assertion so an extractor returning set() cannot pass trivially — means a status added tomorrow turns tests/m3 red. NC-20 driving the vacuity guard red is the part that makes it trustworthy.

D-12 — you were right and I was wrong. My "pin it like test_source_freeze_pins.py" was a category error: that registry gates files measured 0-diff against PY_CODE_REF = bf16289, and a module created today cannot exist at that commit. Your reasoning is also correct on the merits — a whole-file SHA pin goes green once and red forever after the first legitimate edit, whereas 78 behavioural tests with observed-red controls stay honest across refactors. No freeze entry.

D-13. The skip-with-three-guards is the right resolution of the tension I created. I asked for a test that is RED today, but a permanently-red test gets muted within a week — so a derived skip condition (globbing for _DEFAULT_PANEL_NAME), the function's own green/red cases running unconditionally, the finder shown valid, and the +1 visible in the skip count (914/31 → 992/32) is a deferral someone can actually see. NC-12 — perturbing the finder so the live gate STOPS skipping and goes red — is what proves the deferral is real rather than permanent.

D-11. Keep FINDING. Your runbook wording already frames it as the finding, exit_code is non-zero either way, and nothing operational rides on the tier. No change requested.

## Your open question 1 — the MAF-depression join. My view, and a recommendation to NOT build it first.

Do not improvise the cross-cohort join. Build the within-panel test instead. It is strictly better evidence for the mechanism and needs no join at all.

### Why the cross-cohort MAF comparison is weak evidence

My own policy memo already caveats it and the caveat is fatal for a gate: the GWAS AFR cohort is not the AoU AFR cohort. Region 1's ratio is 0.0078 / 0.014 = 0.557 — the direction the mechanism predicts, but ordinary between-cohort AF differences at MAF ~0.01 are easily that large on their own. So a red here would be ambiguous, and an ambiguous gate is one people learn to ignore. Keep it a FINDING, keep it unwired for now.

### The test I would build instead: elevated missingness, within the panel

The mechanism's direct prediction is not about MAF, it is about callability: a variant covered by a deletion's REF span is uncallable on the deletion haplotype, so its per-variant missingness should be elevated relative to the region-wide F_MISS distribution. That is:

- single-cohort — no cross-cohort confound at all;
- already available — plink --missing gives .lmiss per variant at panel build;
- already corroborated — the region-1 2x2 showed occluder carriers ~100% missing at the partner (fAmB = 1.0 in 5 of 6 pairs). That is the same signal, measured directly;
- egress-safe — per-variant missingness rates, an aggregate.

Concretely: for each region, compare F_MISS of occlusion-excluded variants against the region's F_MISS distribution (a rank-based test, or simply the fraction of excluded variants above the region's 90th percentile). Elevated ⇒ mechanism consistent. Not elevated ⇒ genuine FINDING, and a much cleaner one than a MAF ratio, because there is no second cohort to blame.

### If you do wire the cross-cohort version later, two constraints

1. Join on (CHR, POS) only, per snp_id_bridge.R — and note the panel is GRCh38 while the sumstats are GRCh37, so the lift-over is part of the key. Do NOT add alleles to the key: this is the E-2 orientation exposure, and a chr:pos:REF:ALT key silently drops flipped records.
2. Use MAF = min(EAF, 1-EAF), never EAF directly. I checked the arithmetic: EAF 0.014 and 0.986 both give MAF 0.0140, so MAF is invariant to which allele is called the effect allele — it is immune to the orientation flip that E-2 documents. Comparing raw EAF across the join would manufacture spurious "elevation" on every flipped record.

That constraint pair is why I would rather you not build it under time pressure: the join is the exact surface E-2 is about.

## Nothing else from me

D-01…D-13 all accepted; no line I want to argue. The corrections that mattered were the ones where the shipped code disagreed with my assumption about it — D-01 (wrong artifact, wrong error protocol), D-02/D-02b (wrong string shape, silent failure class), D-09 (dead markers + false positive). Three of nine checks broken, found by measurement, before the fire rather than during it. That is the trade working as intended.
