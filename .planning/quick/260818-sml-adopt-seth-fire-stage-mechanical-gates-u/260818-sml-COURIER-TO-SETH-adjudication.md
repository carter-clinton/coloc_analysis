# Courier to Seth — the mechanical gates are SHIPPED, and here is every place the shipped code won

> **From:** Carter K. Clinton (via the GSD session, `quick-260818-sml`)
> **Date:** 2026-08-18
> **Re:** your 2026-08-18 courier, "Baking the pre-fire checks into the workflow"
> **Status:** ADOPTED. Landed as `src/python/fire_verifier.py` +
> `tests/m3/test_fire_verifier.py`, wired into all three `260812-ox1` fire runbooks.
> **Nothing was fired. $0. No perimeter contact.**

---

## 0. First: your suite reproduced, firsthand, as received

Before adopting anything I ran your two attached files unmodified in the session
scratchpad (`PYTHONPATH=. python3 test_fire_verifier.py`):

```
29/29 passed  (18 of them are NEGATIVE CONTROLS proving a check can fail)
```

Your claim reproduces exactly. And I took your instruction literally — **the
checks, not the file.** The prototype is banked verbatim under its original names
alongside this note as a REFERENCE artifact; nothing from it was shipped
byte-for-byte.

You closed with: *"If any check disagrees with how the shipped code actually
behaves, the shipped code wins and the check is wrong — tell me and I'll correct
it rather than assume my prototype is the authority."* That is the entire content
of this note. **Thirteen adjudications, D-01 through D-13.** Every one was
MEASURED against the shipped source, not reasoned about; each carries the
`file:line` I measured it at. Five of them go your way and I say so.

The single most consequential one is **D-02**, and it is not a nitpick: as
written, `classify_deferrals` would have HARD_STOPped the fire **on the gates
working**, at every Stage-C check-in, from roughly region 29 onward.

---

## D-01 — Reader identity: `read_square_bin` is the WRONG reader for the banked artifact

**Your design:** `check_nan_falsification(npz, reader)` where `reader` is *"the
FROZEN `plink_ld_to_npz.read_square_bin`-equivalent: it RAISES on any NaN."*

**Measured.** `plink_ld_to_npz.read_square_bin` (`plink_ld_to_npz.py:198`) reads
the plink **`.ld.bin`** — the PRE-`.npz` artifact. In the fire's `gs://` mode that
file does not survive the region:
`_reclaim_region_scratch(compute_dir, region_id, keep_npz=not gs_mode)`
(`run_native_ld_panel.py:1037`, helper at `:691`) drops everything local on a
successful region because the bucket holds the verified `.npz`. **The artifact
that survives the fire is the `.npz`**, and the shipped re-read of a `.npz` is
`run_native_ld_panel.content_verify_npz` (`:343`), which:

- validates dtype `float32`, square shape, `np.allclose(np.diag(ld), 1.0, atol=1e-3)`
  and `pln._is_symmetric_blocked(ld, atol=1e-4)`;
- **returns `(ok, reason)` — it does NOT raise** (`:351-352`: *"Returns (False,
  reason) on any failure rather than raising, so the loop can record the status
  and continue"*). Your `try: reader(npz) / except:` shape would therefore never
  fire against the shipped verifier — it would read `ok=False` as a clean run;
- detects NaN only **INDIRECTLY**: a NaN on the diagonal fails the diagonal check,
  and a NaN anywhere fails the blocked symmetry check (`np.allclose` defaults to
  `equal_nan=False`) — reported as `"not symmetric (atol 1e-4)"`. **It misreports
  the cause**, which is precisely what the frozen reader's own comment warns
  against (`plink_ld_to_npz.py:213-217`: *"NaN != NaN would otherwise trip the
  symmetry check below and MISREPORT the cause as an asymmetry … do NOT confuse
  this with an asymmetry"*).

**What shipped.** `check_nan_falsification(npz_path, *, verifier=content_verify_npz,
nan_scanner=_has_any_nan_blocked, ranker=nan_variant_indices,
min_bytes=_MIN_REGION_NPZ_BYTES, mode="square")`, in four steps:

1. missing file → FAIL closed; below the byte floor → FAIL closed;
2. call the **SHIPPED** verifier. `ok=True` → PASS, with the detail stating that
   the shipped pre-upload verification re-read the banked `.npz` and that `ok`
   therefore entails NaN-free;
3. `ok=False` → load the array **once more** and run the **FROZEN** blocked
   scanner. NaN present → HARD_STOP naming NaN and the ranked source rows with
   your verbatim sentence *"occlusion is NOT the sole NaN mechanism"*. NaN absent
   → HARD_STOP carrying the shipped `reason` verbatim and **explicitly not
   claiming NaN**;
4. any exception → FAIL closed, with no cause attributed.

Two things I want to flag because they were *your* points and they held:

- **The "ok entails NaN-free" implication is PINNED, not argued.**
  `test_shipped_verifier_rejects_both_nan_fixtures` calls the shipped
  `content_verify_npz` on a NaN-diagonal fixture and on a whole-row-NaN fixture
  and asserts `ok is False` for both — and asserts the second one's reason
  contains `"symmetric"`, i.e. it pins the MISREPORT as a measured fact.
- **Your `RED_reader_explodes_fails_closed` control survives as
  `test_RED_nan_falsification_corrupt_bytes_does_not_claim_nan`**, strengthened:
  it asserts the literal token `NaN` does **not** appear in the detail. A non-NaN
  failure reported as a NaN finding is the same misattribution one layer up.

Memory: at most one ~42 GB array is live, and the second load happens only on the
already-failing path. There is no `np.isnan(m)` / `np.allclose(m, m.T)` /
`np.triu(m)` over a full dense matrix anywhere in the module.

---

## D-02 — `classify_deferrals` is DEFEATED by the shipped producer (the big one)

**Your design:** `_EXPECTED_DEFERRALS = ("deferred_infeasible_square",
"deferred_occlusion_anomaly")` with the test
`if s.startswith("deferred") and s not in _EXPECTED_DEFERRALS: unknown.append(s)`.

**Measured.** The shipped statuses are **not bare tokens**. They carry a detail
suffix, by design (the *"detail-in-status"* precedent the producer's own comment
names at `run_native_ld_panel.py:827`):

```
run_native_ld_panel.py:831
    result["status"] = (f"deferred_infeasible_square: n_var={pre_window_n_var} "
                        f"> ceiling={max_n_var}")

run_native_ld_panel.py:854
    result["status"] = (
        f"deferred_occlusion_anomaly: {len(occluded_ids)} occluded of "
        f"{pre_window_n_var} (ceiling {int(_OCCLUSION_ANOMALY_FRACTION * pre_window_n_var)})")
```

So a REAL row reads
`deferred_infeasible_square: n_var=181004 > ceiling=120000`, which
`s not in _EXPECTED_DEFERRALS` evaluates **True** → `unknown` → **HARD_STOP**.
Every real deferral. You expect ~29+ of them. The gate would have fired
`"unrecognized status value(s)"` and stopped a healthy $385–1,084 fire on the
gates working, at every 2–3-day check-in.

**And there is a second hole in the same function, which I think is worse than
`"banana"`.** `skipped_idempotent` (`run_native_ld_panel.py:774`) is a REAL
shipped status — it is emitted for **every resumed region**, which after any
Spot-VM recycle or staged ramp is most of them. It does not start with
`"deferred"`, so your loop never inspects it: it lands in `counts` and passes
**silently, as if it were `ok`**. Same for `verify_failed` (`:991`) and
`error: …` (`:1028`) — see D-04. The prefix bug is loud; this one is quiet.

**What shipped.** `classify_deferrals` → `classify_statuses`, PREFIX-matched:

| class | members | disposition |
|---|---|---|
| ok-class (exact) | `ok`, `skipped_idempotent` | PASS |
| deferral (prefix) | `deferred_infeasible_square`, `deferred_occlusion_anomaly` | PASS — the gates working |
| failure | `verify_failed`, `error` (exact), `error:` (prefix) | **FAIL at FINDING** |
| anything else, or empty | — | **FAIL at HARD_STOP** |

Proven end to end on the shipped CLI, on a real detail-bearing row:

```
$ python3 src/python/fire_verifier.py stage-c --panel-tsv <fixture>
PASS  HARD_STOP  status_classification: 1 ok-class + 1 deferred row(s) of 2, ALL recognized
exit_code:  0
```

---

## D-03 — The measured status vocabulary (seven emission sites), and a NAMED drift enforcer

`grep -n 'result\["status"\]' src/python/run_native_ld_panel.py` plus
`grep -n '"status":'`:

| site | emitted |
|---|---|
| `:774` | `"skipped_idempotent"` (the dict entry — every resumed region) |
| `:785` | `"error"` (the initialiser) |
| `:831` | `f"deferred_infeasible_square: n_var={...} > ceiling={...}"` |
| `:854` | `f"deferred_occlusion_anomaly: {...} occluded of {...} (ceiling {...})"` |
| `:991` | `"ok" if ok else "verify_failed"` (an `IfExp` — two values, one site) |
| `:1028` | `f"error: {e}"` |

An allow-list is only as good as the thing that notices it went stale, so the
allow-list has an enforcer rather than a comment. A test walks the SHIPPED
producer with `ast` and extracts the constant prefix of every value assigned to
`result["status"]` or written as a `"status":` dict entry, handling `Constant`,
`JoinedStr` (leading `Constant` part) and `IfExp` (both branches). It asserts
(a) the extracted set is **non-empty** — an extractor that finds nothing would
pass trivially — and (b) every extracted prefix classifies. **A status added to
the producer tomorrow makes `tests/m3` red.**

Both halves were seen red before I trusted either
(`260818-sml-controls-transcript.txt`, NC-02 and NC-20): NC-20 perturbs the
extractor to return `set()` and the non-vacuity assertion fires; NC-02 makes
`_status_class` never return UNKNOWN and the coverage assertion stops flagging a
fixture producer carrying `result["status"] = "banana"`.

---

## D-04 — `verify_failed` / `error:` rows PASS under your classifier; ours fail them at FINDING

Under `classify_deferrals` neither starts with `"deferred"` and neither is empty,
so both pass. But a `verify_failed` region **never uploads** — the shipped upload
is inside `if ok:` (`run_native_ld_panel.py:996`) — and an `error:` region banked
nothing at all. That is not the gates working; it is a hole in the deliverable.

I did **not** make it a HARD_STOP, for the reason your own severity tier exists:
Stage C runs **without** `--fail-fast`, so the loop legitimately continues past
one, and an automatic abort would throw away the 200 regions still to come over a
single bad one. The correct response is report-to-Carter with the per-region
statuses. So: **FAIL at FINDING**, `exit_code` 1 either way.

---

## D-05 — `check_region1_not_deferred` → `check_region1_status`, widened

Your check fires on `status.strip().lower().startswith("deferred")`. But region 1
runs under `--fail-fast`, and the shipped gate there is:

```
run_native_ld_panel.py:1161-1162
    if fail_fast and str(res.get("status")) != "ok":
        raise RegionGateError(str(res.get("region_id")), str(res.get("status")))
```

**ANY** non-`ok` status is the gate condition — `verify_failed` and `error: …`
included. A check narrower than the code it is gating gives false assurance, so
ours passes only on exactly `ok`. Your `deferred` case is now one of three
negative controls; `verify_failed` is the widening pin.

---

## D-06 — `min_bytes=256` — you hit the shipped floor exactly

`aou_ld_panel._MIN_REGION_NPZ_BYTES = 256` (`aou_ld_panel.py:418`) is the MED-6
resume-guard byte floor: the guard treats a `.npz` below it as absent rather than
as banked, so a truncated object recomputes instead of being trusted. Your default
coincides **exactly**. We now `import` it rather than re-declare it — a copied
constant is a silent divergence with no enforcer, and the identity is asserted by
a test (`test_nan_falsification_min_bytes_default_is_the_shipped_floor`), driven
red by perturbing the accessor to return `255` (NC-16b).

---

## D-07 — `frac=0.0005` and the strict `>` — exactly right, including your boundary case

`_OCCLUSION_ANOMALY_FRACTION = 0.0005` (`run_native_ld_panel.py:133`) and the
shipped comparison is

```
run_native_ld_panel.py:853
    if len(occluded_ids) > _OCCLUSION_ANOMALY_FRACTION * pre_window_n_var:
```

— a FLOAT ceiling with a STRICT `>`, because clause (d) says *"exceeds"*. Your
`test_ceiling_boundary_equal_passes` (60 @ 120,000 passes, 61 fails) reproduces it
exactly and is kept verbatim in spirit.

Two hardenings. First, we **import** the constant instead of re-declaring it: it
is a MODULE GLOBAL read at evaluation time in the producer, deliberately NOT
CLI-tunable (*"a knob would invite silent deviation from the public commitment"*),
and our accessor reads it the same way. The test proves that by monkeypatching
`rnlp._OCCLUSION_ANOMALY_FRACTION` and asserting the gate FOLLOWS — a copy would
not. Second, a repo-wide assertion: `test_no_hardcoded_shipped_constants_in_the_module`
greps the shipped `fire_verifier.py` for a literal `0.0005`, `120000` or a
re-declared `= 256` and fails on any of them (seen red, NC-15).

---

## D-08 — `vm_gib=120` — CONFIRMED from the repo, not assumed

`.planning/debug/m3-producer-unbounded-dense-read.md:17` — *"every region must be
known to fit in the compute VM RAM (n1-standard-32, 120 GB)"*. `_VM_TOTAL_GIB =
120.0` is one of only two literals in the module, docstring-cited to that
`file:line`, and the runbook passes `--vm-gib 120` explicitly so the number is
visible at the call site too. Your 15% headroom → a 102.0 GiB bound.

---

## D-09 — Two of your four `estimate_markers` are DEAD, and one would false-positive

Your `estimate_markers = ("ESTIMATE", "estimate", "~29", "10.5%")`, measured
against the real text (`.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md`,
`## R4-COVERAGE` at line 1148 running to EOF at 1197):

- `ESTIMATE` (uppercase) — **does not occur.** `grep -n "ESTIMATE"` returns
  nothing (rc=1).
- `~29` — **does not occur.** The text reads `| regions deferring at the 120k cap
  | **29 / 276 = 10.5%** |`.
- `estimate` — matches only via the word *"estimates"* in *"These are Seth's
  estimates, not measurements"*, and would **false-positive** on innocent prose
  such as *"the affected span was estimated from Stage B and then MEASURED at
  rollup"*. A gate that goes red on correct text gets disabled.
- `10.5%` — real, and kept.

So two of four are dead weight and a third is a future false alarm; the check was
passing on one live marker out of four. Replaced with **measured sentinels**:
`"29 / 276 = 10.5%"`, `"Seth's estimates, not measurements"`, `"~247 regions"`,
`"48.5 Mb"`, `"~10.5%"` — plus two things your version could not do:

- a required `MEASURED:` provenance line naming the panel-TSV source, **so the
  obligation cannot be discharged by deleting the warning and shipping nothing**;
- a **vacuity FAIL**: the check extracts the `## R4-COVERAGE` block by heading, and
  a renamed heading yields an empty block that would satisfy every content
  assertion trivially. Short/empty block ⇒ FAIL, checked first. (That is the V0
  lesson from our `260817-vbu` enforcer, where a card gutted outright would have
  gone green.)

There is a dedicated false-positive control asserting that prose containing
*"estimated"* does **not** trip the check.

---

## D-10 — `n_total=276` is now a REQUIRED argument

`awk -F'\t' 'NR>1 && $7=="AFR"' config/ld_regions.tsv | wc -l` = **276**, so your
default is correct today. It is now required anyway, in the function signature and
on the CLI (`--n-total`), with a `pytest.raises(TypeError)` proving there is no
default. A default is exactly how a count goes silently stale — and this project
already ate that: the skill file still carried `322 = 161 × 2` for weeks after the
producer rescope made it 552 rows / 276 region-ids.

---

## D-11 — Region-1 severity: kept at FINDING, per your judgment call

I am taking your recommendation. It stays FINDING, for the reason you gave (the
correct response is diagnosis, and a hard abort invites a retry-without-
understanding) and because the runbook's own wording already frames it that way:
*"a deferral there would itself be the finding."*

Recorded in the module docstring and in the SUMMARY: flipping it is a
**one-constant change** (`_REGION1_SEVERITY`) reserved for Carter, and
`exit_code` is non-zero either way — nothing operational rides on the tier, only
the human's reading of it. **If you'd still rather it were HARD_STOP, say so and
it is one line.**

---

## D-12 — We did NOT add the module to the freeze registry, deliberately

You suggested pinning it *"the way `test_source_freeze_pins.py` pins the frozen
modules."* Measured: that registry gates only files **measured 0-diff against
`PY_CODE_REF = bf16289`** (`tests/m3/test_source_freeze_pins.py:52`), and its own
comment states that adding a file there *"requires a RECORDED DECISION that it is
frozen, not an inference"* (`:81-83`). A module created today **cannot exist at
`bf16289`**, so adding it would be a category error, and it would re-plant exactly
the nuisance-repin timebomb the SR4 rescope removed.

**DECISION: no freeze-registry entry.** `fire_verifier.py` is new, additive, and
expected to change as the fire teaches us things. Its enforcer is its own test
module — 78 tests, every check with at least one observed-red control. That is a
stronger pin than a whole-file SHA anyway: a SHA pin goes green once and red
forever after the first legitimate edit, whereas a behavioural test stays honest
across refactors. (We wrote that lesson down the hard way in August:
`[[feedback_a_fixed_sha_whole_file_pin_is_a_timebomb]]`.)

---

## D-13 — The R4-COVERAGE gate SKIPS pre-fire — with three anti-masking guards, and a visible baseline move

You wanted this one **in the suite, not the runbook** — *"a registered obligation
with no failing test is a promise with no enforcement."* Agreed, and it is. But it
cannot be RED in CI today for a boring reason: the measured numbers do not exist
yet, so a permanently-red test would be muted within a week.

So the pytest that runs the check against the LIVE repo file **skips while no
measured panel TSV exists in-repo**, and the skip condition is DERIVED, not
invented: it globs the repo for
`run_native_ld_panel._DEFAULT_PANEL_NAME` (`run_native_ld_panel.py:122`). Three
guards against the skip becoming a hiding place:

1. **The check function's own green + red cases run UNCONDITIONALLY** against
   fixture text — six of them, including empty-file, missing-file, renamed-heading
   and sentinels-removed-without-provenance. The function is proven able to fail
   whether or not the live gate runs.
2. **The finder itself is SHOWN VALID** by a test that hands it a tmp tree with
   and without the artifact. A skip-guard hides the bug unless the skipped check
   is shown valid — and I drove that one red too (NC-12: perturbing the finder to
   always report a hit makes the live gate STOP SKIPPING and go RED against the
   real file, which is the proof that the deferral is real and not permanent).
3. **The skip is VISIBLE in the baseline.** `tests/m3` moved from
   `914 passed, 31 skipped` to `992 passed, 32 skipped` — the +1 skip is this
   gate, registered in the SUMMARY and named in `260812-ox1-READY-TO-FIRE.md`
   item 10 as the enforcer of the obligation. A deferral in the skip count is a
   deferral someone can see.

Today, run directly, it is red exactly as you intended:

```
$ python3 src/python/fire_verifier.py disclosure --file .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
FAIL  HARD_STOP  publication_coverage_disclosure: the R4-COVERAGE disclosure still
carries pre-fire estimate sentinel(s): 29 / 276 = 10.5%; Seth's estimates, not
measurements; ~247 regions; 48.5 Mb; ~10.5% -> replace with MEASURED
deferred_infeasible_square counts + the affected span from the panel TSV …
exit_code:  1
```

---

## What we kept from you verbatim, because it was right

- **The three design rules.** Fail closed / measure the data layer never a marker /
  every check proven able to fail. They are the module docstring.
- **The two-tier severity**, and your reasoning for MAF-depression being a FINDING
  (the GWAS AFR cohort is not the AoU AFR cohort, so the machine should not be the
  one deciding).
- **`check_manifest_rows`' marker-content control.** It is now stronger, not
  weaker: the shipped writer emits a `region_id` column
  (`occlusion_manifest.STAGE_A_COLUMNS[0]`), and the runbook's own expectation is
  *"region_id m2_region_00001 on every record row"* — so the check asserts the
  VALUE, not just the arithmetic. Right count / wrong content is the $2,140 defect
  class, and a count is a weaker witness than a value.
- **`summarize()` as the stage gate's exit status**, wired to `argparse`
  subcommands `stage-a` / `stage-b` / `stage-c` / `disclosure` and into all three
  `260812-ox1` runbooks under a new hard rule **R8**: *run it, paste the full
  output, NEVER chain past a red — the gate makes the evidence mechanical, it
  never makes the decision.*
- **"Every check proven able to fail"** — taken literally. 22 perturbations
  (NC-01…NC-20 plus NC-04a/b and NC-16b), each applied to the **shipped** module,
  run, captured verbatim, reverted byte-exact, bytecode cache cleared, and re-run
  to prove the revert took. All of it in
  `260818-sml-controls-transcript.txt`. Two of those entries exist because I
  reconciled a component count instead of trusting the aggregate: NC-16 reported
  "5 selected, 4 failed", and the two stragglers turned out to be a control that
  never fired (CPython returns `"" + s` **unchanged**, so the "copy" I made was
  the same object) and a test that was never selected (its name carries
  `min_bytes`, not `min_npz_bytes`). Both were re-fired as NC-16b.

---

## Open, back to you

1. **MAF depression is implemented but NOT WIRED.** `check_maf_depression` and its
   three tests ship; no subcommand calls it. The `(panel_maf, sumstats_maf)` pairs
   need the per-region occlusion manifests JOINED to the harmonized sumstats, and
   that join does not exist. It is recorded as an explicit "do not improvise this"
   note in the Stage-B runbook block. **If you have a view on the right join key
   and the right MAF source on the sumstats side, that would save me a design
   pass.**
2. **Region-1 severity** — FINDING as you recommended (D-11). One constant if you
   want it flipped.
3. Anything in D-01…D-13 you think I read wrong. Every claim above has a
   `file:line`; argue with the line, not with me.

Thank you for this one. The prototype was 90% of the work and the negative
controls were the part worth copying verbatim — you were right that each one is a
defect class this project has actually hit.

— Carter
