# Seth courier — baking the pre-fire checks into the workflow (as received)

> Provenance: received 2026-08-18 ~20:18 EDT, pasted by Carter into the NCSU session,
> in reply to our 260817-vbu replication-confirmation courier. AS-RECEIVED transcription
> of a chat-rendered body — no byte anchors were supplied. The two code files he attached
> are banked alongside this file under their ORIGINAL names (`fire_verifier.py`,
> `test_fire_verifier.py`) so the prototype stays runnable; they are REFERENCE ONLY and
> are NEVER to be shipped verbatim (his own instruction: "Take the checks, not the file:
> re-implement inside your test suite / runbook wiring under GSD TDD").
>
> FIRSTHAND VERIFICATION 2026-08-18 ~20:40 EDT: his suite was run as received in the
> session scratchpad (`PYTHONPATH=. python3 test_fire_verifier.py`):
> **29/29 passed (18 of them negative controls)** — his claim reproduces exactly.

---

## Baking the pre-fire checks into the workflow — mechanical gates, not human vigilance

The problem with my last message: it was a checklist a human has to remember. That works at region 1 with full attention and fails at region 180 at 3am. Every item on it except the go/no-go decision itself can be made mechanical. Here is the verifier, with all checks proven able to fail.

Reference prototype (NOT a commit — GSD-route the real thing): fire_verifier.py + test_fire_verifier.py, 29/29 green, 18 of them negative controls.

## Three design rules, because a bad gate is worse than none

1. FAIL CLOSED. Missing file, unreadable input, unparseable content, or an internal exception => FAIL. A verifier that cannot measure must never pass. This is the _SUCCESS-marker lesson expressed in code: absence of evidence is FAIL, not PASS.
2. MEASURE THE DATA LAYER, NEVER A MARKER. Row counts come from reading rows; panel validity comes from re-reading the panel. A status string saying "ok" is corroboration, never the measurement.
3. EVERY CHECK PROVEN ABLE TO FAIL. 18 of the 29 tests are negative controls. A green that has never been observed red is not a result — your own words this week, and the reason your widened hex-run invariant was credible.

## Checklist item -> mechanical gate

| my checklist item | function | severity if red |
|---|---|---|
| filtered region-1 panel must raise nothing | check_nan_falsification(npz, reader) | HARD_STOP |
| manifest shows 6 lines (header + 5 records) | check_manifest_rows(path, expected_records=5) | HARD_STOP |
| 5 occluded vs 51 ceiling, 10x headroom | check_occlusion_ceiling(n_occluded, n_var, 0.0005) | HARD_STOP |
| a deferral at region 1 is itself the finding | check_region1_not_deferred(status) | FINDING |
| watch peak RAM on the 20.8 Mb region | check_peak_ram(peak_gib, vm_gib=120) | HARD_STOP |
| MAF-depression direction check | check_maf_depression(pairs) | FINDING |
| cost per BANKABLE region, not per 276 | check_cost_denominator(used, bankable) | HARD_STOP |
| deferred_* rows are the gates working | classify_deferrals(status_rows) | HARD_STOP only if status UNRECOGNIZED |
| coverage gap: real numbers before publication | check_coverage_disclosure_resolved(text) | HARD_STOP |

summarize(checks) returns exit_code 0/1 plus hard_stops / findings and a per-check report of what was measured. Wire it as the stage gate's exit status.

## The four that do real work (the rest are hygiene)

1. check_nan_falsification — it calls the reader ITSELF. It does not read a status field; it re-reads the banked panel through the frozen NaN-raising reader and treats a raise as a HARD_STOP with the reason spelled out ("occlusion is NOT the sole NaN mechanism"). You told me the fire path already does this by construction — good — but by construction is a property of the current code path, and this makes it an assertion that survives refactoring. Note the negative control test_nan_falsification_RED_reader_explodes_fails_closed: a reader failing for a NON-NaN reason (disk error) also FAILS rather than being mistaken for a clean run.

2. check_manifest_rows catches the _SUCCESS-marker class explicitly. Negative control test_manifest_RED_marker_content_not_records: a file with the right line count whose rows are _SUCCESS placeholders FAILS on field-parseability. Right count, wrong content is the exact defect that cost this project $2,140 once.

3. check_coverage_disclosure_resolved is the one I most want in the SUITE, not the runbook. It FAILS while my estimates (~29, 10.5%, ESTIMATE) are still in the disclosure text, and only passes once measured deferred_infeasible_square counts replace them. That way the R4 disclosure obligation cannot lapse quietly in the weeks between the fire and submission — it stays RED in CI until someone does the work. A registered obligation with no failing test is a promise with no enforcement.

4. classify_deferrals inverts the default. Recognized deferrals PASS (they are the gates working — don't "fix" them mid-fire). An unrecognized or empty status FAILS, because an unknown status silently treated as ok is how a new failure mode enters unnoticed.

## Severity is deliberately two-tier

- HARD_STOP — firing further would bank defective or unexplained output. Non-negotiable.
- FINDING — scientifically meaningful, needs a human decision, not an automatic abort. check_maf_depression is a FINDING not a HARD_STOP precisely because the GWAS AFR cohort is not the AoU AFR cohort: absent depression weakens the mechanism attribution but the confounding means the machine should not be the one deciding.

I want to flag the judgment call: I made region-1 deferral a FINDING rather than a HARD_STOP. Argument for HARD_STOP is that region 1 is the known-answer region and a deferral there means gate-or-substrate disagrees with ground truth. Argument for FINDING is that the correct response is diagnosis, and a hard abort invites a retry-without-understanding. Your call — if you prefer HARD_STOP, change one constant.

## What is NOT mechanizable, and shouldn't be

The go/no-go itself. An agent never fires it; each stage waits on Carter's explicit go. These gates make the evidence for that decision mechanical and fail-closed — they do not make the decision. Also not mechanized: the interpretation of a FINDING. That's the point of the tier.

## Adoption

Take the checks, not the file: re-implement inside your test suite / runbook wiring under GSD TDD so they are pinned the way test_source_freeze_pins.py pins the frozen modules. The negative controls are the part worth copying verbatim — each one is a defect class this project has actually hit (marker-not-data, unmeasured-treated-as-ok, wrong denominator, unknown-status-as-ok, estimate-shipped-as-measurement).

If any check disagrees with how the shipped code actually behaves, the shipped code wins and the check is wrong — tell me and I'll correct it rather than assume my prototype is the authority.
