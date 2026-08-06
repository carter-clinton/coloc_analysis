---
phase: quick/260806-b77
verified: 2026-08-06T15:10:00Z
status: passed
score: 19/19 must-haves verified (8 truths + 7 artifacts + 4 key_links)
overrides_applied: 0
---

# Quick 260806-b77: Close the remaining blast-radius findings — Verification Report

**Task goal:** Close blast-radius findings **G, J, L, M** from `m3-04c-BLAST-RADIUS.md`, and
register **K** as a prepared deferral, clearing gate rows "Any TRANS fit" and "Growing the
curated region set" while leaving "Publishing the panel provenance" PARTIAL.

**Verified:** 2026-08-06, re-derived from the codebase — SUMMARY.md claims were treated as
hypotheses, not evidence. Every load-bearing number below was independently reproduced on
this node, not copied from the SUMMARY.

**Status:** passed
**Re-verification:** No — initial verification.

---

## Method

I did not trust the SUMMARY. For each of the ten items in the verification brief I re-derived
the claim from source, ran the actual code (including three live reverts of shipped source to
watch tests go RED, then restored), and ran both full suites myself. Total independent test
executions in this session: `tests/m3` full suite (807 passed/31 skipped/0 failed, 878s),
`tests/phase2` full suite (136 passed/1 skipped/0 failed), the three new modules + regression
targets (170 passed), plus three live source reverts (`NC-G1`, `NC-G2`, `NC-M1`) each producing
the exact RED failure counts the SUMMARY claims.

---

## 1. THE GATE-ROW LEDGER — verified against the blast-radius doc's own table

`m3-04c-BLAST-RADIUS.md:133-144` (read directly, not from the plan's paraphrase):

| Gate row (blast-radius doc) | Blocked by | Autonomous? |
|---|---|---|
| Any TRANS fit | G, F | Yes, $0 |
| Publishing the panel provenance | I, J, K | Yes, $0 |
| Growing the curated region set | L, M | Yes, $0 |

SUMMARY's gate-binding table (`260806-b77-SUMMARY.md` §1):

| Gate row | Verdict | My independent check |
|---|---|---|
| Any TRANS fit | ✅ CLEARED (G here; F re-derived, not assumed) | **AGREE** — G is closed on fixtures/source (verified §2 below); F's closure was independently re-confirmed against live `finemap.smk`/`ld_read_path.py` (§2 below), not merely cited. |
| Publishing the panel provenance | 🟠 PARTIAL — NOT cleared (I closed by o7o, J closed here, K DEFERRED) | **AGREE.** K is genuinely not closed — both blockers I re-derived independently are real (§5). This is the one row where a full closure would have been the easy, wrong thing to report, and it was not reported that way. |
| Growing the curated region set | ✅ CLEARED (L, M) | **AGREE** — both L and M are engineering-complete (drift detection + allow-list), verified §7. |

**I agree with all three verdicts.** No partial closure is reported as a full one — this is
the exact failure class the brief warned about, and it did not recur here.

---

## 2. FINDING G — both directions, over the REAL shipped chains (re-derived myself)

I did **not** trust the plan's or SUMMARY's transcription of `config/pipeline.yaml`. I loaded
the real file with `yaml.safe_load` and ran `is_aou_source` against every entry myself:

```
$ /rs1/.../smoke_dev/bin/python -c "... enumerate ld_panel chains, apply is_aou_source ..."
EUR EUR_ukbb_pub False | EUR EUR_aou True | EUR EUR_ukbb False | EUR EUR_1kg False
AFR AFR_aou True | AFR AFR_hgdp False | AFR AFR_1kg False
TRANS TRANS_aou_eur True | TRANS EUR_1kg False
TRUE SET: ['AFR_aou', 'EUR_aou', 'TRANS_aou_eur']
FALSE SET: ['AFR_1kg', 'AFR_hgdp', 'EUR_1kg', 'EUR_ukbb', 'EUR_ukbb_pub']
OK — matches expected partition exactly
```

**Confirmed independently:** the True-set is exactly `{EUR_aou, AFR_aou, TRANS_aou_eur}` and
the False-set is the other five, matching the plan's exhaustive enumeration exactly.

**NC-G2 (the false-trip / over-fire direction) — reproduced live.** I stubbed
`is_aou_source` to `return True` and ran the new module:

```
12 failed, 20 passed in 1.25s
FAILED ...test_strict_mode_does_not_fire_on_a_chain_of_only_non_aou_sources
```
`test_strict_mode_does_not_fire_on_a_chain_of_only_non_aou_sources` is exactly the "guard must
not newly fire" assertion (behavior (d) in the plan). Restored to green (32 passed) afterward.
**This is the direction the P3/`quick-260715-vxz` lesson says gets missed, and it genuinely
fails here — a widened predicate would make the AoU fire unable to start**, confirmed live.

**NC-G1 (the finding itself) — reproduced live.** I reverted the body to
`endswith("_aou")` (byte length changed): **8 failed, 24 passed** — matching the SUMMARY's
claimed count exactly, including `test_inverted_control_strict_trans_differs_from_the_baseline`.
Restored to green (32 passed).

**TRANS_aou_eur is genuinely KEPT, not deleted.** `config/pipeline.yaml:222` still shows
`TRANS_aou_eur -> data/processed/ld_reference/EUR_aou/{region_id}.rds` as the TRANS chain head.
`pin.TRANS: null` (confirmed by direct read of `config/pipeline.yaml:259-262`) — `pin.TRANS` is
NOT used as a remedy. `EUR_aou` is confirmed present in the EUR chain
(`config/pipeline.yaml:213-216`), and `tests/m3/test_ld_panel_resolver.py:184`
(`eur_sources.index("EUR_aou")`) passes (47/47 in that file, run directly).

**Parsed-config equality, re-measured:**
```
$ python3 -c "a=yaml.safe_load(open('config/pipeline.yaml')); b=yaml.safe_load(git show 6b427bc:...); print(a==b)"
PARSED_CONFIG_IDENTICAL True
```
The config edit is comment-only, confirmed by structural equality, not by trusting the diff.

**FINDING F re-derived, not merely cited.** I read `ld_read_path.py` and `finemap.smk` myself:
`ld_matrix_region_id()` (`ld_read_path.py:97-111`) returns the legacy `region_safe_to_id[region]`
verbatim unless `ld_read_path_applies(ancestry, config)` is true, which requires `ancestry` to be
in `config["ld_read_path"]["ancestries"]`. The shipped config (`config/pipeline.yaml:369-373`)
has `ancestries: [AFR]` — EUR and TRANS are off the allow-list. `finemap.smk:351-352` routes
`ld_matrix` through this gated function, never through `CURATED_TO_M2` directly. **F is closed**,
confirmed by reading the live code, not by re-quoting the SUMMARY's excerpt.

**G's registry non-vacuity (artifact half).** I grepped the live tree independently:
```
$ grep -rn "ld_reference/EUR_aou" src/snakemake/rules/ Snakefile
src/snakemake/rules/m3_convert_npz_rds.smk:308:# data/processed/ld_reference/EUR_aou/{region_id}.rds.
```
One hit, and it is a `#`-commented line inside the retirement note — matches the claim exactly.

**Verdict: G closed, both directions proven, F genuinely re-derived, orphan genuinely kept
(not deleted), pin not used as a workaround. This item is FULLY VERIFIED.**

---

## 3. `TRANS_aou_eur` KEPT — the counter-intuitive choice, verified

Already covered in §2: the entry survives in the shipped config, `EUR_aou` was not removed
from the EUR chain (`test_ld_panel_resolver.py:184` passes, run directly: 47 passed), and
`pin.TRANS` is `null` in the shipped config (not set to a remedy value). `pin` short-circuits
ahead of `strict_aou_only` in `ld_panel.py:113-124` (`pin` filters the chain to a single entry
*before* the walk that checks `strict_aou_only`), confirmed by reading the resolver's control
flow directly — so `pin.TRANS` would indeed re-hide what the fix exposes, as claimed.

---

## 4. FINDING J — the receipt genuinely distinguishes early exit from regression

Read the live `finemap.smk:540` receipt line directly (not the plan's shape — the actual
shipped code): a single `{PYTHON_BIN} -c "..."` program with `EARLY=('no_variants',
'too_many_variants')` — a **tuple**, not a set literal (confirming Deviation 3: a `{...}` set
literal would collide with Snakemake's `shell:` placeholder syntax). It renders
`NA_EARLY_EXIT`/`early_exit:<status>` for the two early-exit statuses and
`ABSENT`/`ALARM_LD_FIELDS_MISSING` for a real regression (status present, `ld_matrix` absent).

Ran `tests/m3/test_finemap_receipt_early_exit.py` directly: **all pass**, including
`test_the_early_exit_token_and_the_alarm_token_are_not_equal` and the mutual-distinguishability
test across all three fixture classes.

**`finemap.smk`-only, confirmed by diff, not by claim:**
```
$ git diff 6b427bc HEAD -- src/snakemake/rules/finemap.smk | grep -c region_id   -> 0
$ grep -c "{PYTHON_BIN} -c" src/snakemake/rules/finemap.smk                      -> 1
$ grep -c -- "--ld-allele-aware {params.ld_allele_aware}" finemap.smk            -> 1
$ git diff --exit-code dc4bbd2 -- run_susie_rss.R                                -> clean (rc 0)
```
All four numbers match the plan's stated acceptance thresholds exactly. **J is genuinely closed
inside the non-frozen file, with `run_susie_rss.R` provably 0-diff.**

---

## 5. FINDING K — the deferral is genuinely FORCED, and the registry entry is actionable

**I independently re-derived both blockers, not just re-read them:**

1. **Frozen-file constraint.** `git diff --exit-code dc4bbd2 -- run_susie_rss.R` → clean.
   `grep -n "variant_catalog_fallback" run_susie_rss.R` (my own grep, not the plan's) returns
   exactly **six** lines: `:787` (init `FALSE`), `:916` (Path-1 mutation `TRUE`), `:936`/`:968`
   (the two early-exit JSON emits), `:1013` (Path-2 mutation `TRUE`), `:1208` (success emit).
   **The SUMMARY's Deviation 2 (corrected from the plan's three to six sites) is accurate** —
   I confirmed this independently by grepping the live source myself, not by trusting the
   correction. K-1's diff correctly deletes only `:1013` and explicitly states `:787`/`:916`/
   `:1208` do not move.
2. **Pre-existing test constraint.** Read `tests/m3/test_ld_read_path.py:451-453` directly:
   `assert "variant_catalog_fallback <- TRUE" in branch` inside the Path-2 brace block —
   confirmed via `git log -S` that this assertion predates this task
   (`f6c3c36`, `m3-04c-T1b`, well before baseline `6b427bc`), so it is genuinely pre-existing.

**I probed for a non-frozen remedy myself** (per the verification brief's instruction), and
concluded there genuinely isn't one within reasonable engineering bounds: the only alternative
would be a downstream script that rewrites the emitted JSON's `variant_catalog_fallback` field
post-hoc, duplicating the frozen file's Path-1/Path-2 branching logic outside it. That would
(a) not be a "receipt fix" — it mutates declared build outputs, a materially larger scope than
this task's `files_modified`; (b) require its own new module and test suite to keep the
duplicated logic from drifting from the frozen source over time; and (c) not actually restore
the field's meaning at the point of truth (a future consumer reading the JSON straight, without
going through the duplicated corrector, still sees the wrong value). The task's chosen `$0`
mitigation — a runtime `variant_catalog_fallback_cause` token added to the receipt, landed at
`finemap.smk:540` alongside the field itself — achieves the same reader-facing outcome without
this fragility. **The deferral is genuinely forced, not convenient.**

**K-1's registry entry, read directly from `deferred-items.md`:** contains (1) the exact
minimal one-line diff against `dc4bbd2` (deleting only `:1013`, explicitly stating `:916`/`:787`/
`:1208` do not move); (2) the blast radius (science unchanged, only the reporting flag moves,
`ld_overlap_zero_fallback` remains the Path-2 discriminator); (3) the re-freeze obligation
(single-use, with a note to bundle the `ld_allele_join.R` extraction into the same window);
(4) both authorizations named explicitly — (a) an unfreeze of `run_susie_rss.R` and (b) an
`AUTH`-style edit to `test_ld_read_path.py`'s Path-2 assertion, with the required strengthening
direction spelled out as a concrete diff. **All four required elements are present. This is a
prepared deferral a reader could execute from cold, not a rediscovery task.**

---

## 6. AUTH-b77-01 — the one authorized pre-existing test edit

Read `tests/m3/test_qtl_coloc_allele_join.py` directly. Confirmed:

- **First assertion survives verbatim:** `assert "region_id=lambda" not in text` (over
  `qtl_coloc.smk`) is unchanged.
- **Narrowed form is genuinely stronger on its stated subject:** the replacement
  (`assert "region_id" not in diff_text`) catches a `params.region_id` edit even inside a
  commit that legitimately changes something else — a case the whole-file pin could not
  distinguish. I re-ran the attribution table myself (not copied from the SUMMARY):
  ```
  6b427bc: 0 diff lines | 9b2d431: 0 diff lines | 9c0c67b: 0 diff lines | d8cfa53: 72 diff lines
  ```
  Matches the SUMMARY exactly — the finding-J receipt commit is what tripped the old pin.
- **Negative control is permanent, in-suite, and genuinely non-vacuous:** I ran
  `test_nc_auth_b77_01_the_narrowed_pin_still_catches_a_region_id_edit` directly — it passes,
  which means its internal `pytest.raises(AssertionError, match="touched region_id")` around
  the perturbed diff genuinely fired (the control constructs a real throwaway git repo, shadows
  `params.region_id`, and drives the real narrowed assertion against the resulting real `git
  diff`). The same test also asserts the REAL diff is non-empty and passes, and that the working
  tree's `finemap.smk` is byte-unchanged mid-control.
- **Primary guard rail untouched and green:** ran
  `tests/m3/test_occlusion_lockstep_wiring.py::test_params_region_id_is_untouched` directly —
  passes. `git diff 6b427bc HEAD -- finemap.smk | grep -c region_id` → `0`, confirming
  `params.region_id` is byte-unchanged in the actual diff, not just asserted to be.
- **Attribution confirmed pre-existing:** `git log -S"def test_params_region_id_is_not_declared_here"`
  → `1815bfd`, `260805-w7u-T2`, created before this task's baseline. Not authored by this task
  to dodge its own rule.

**Fully verified — the edit is a genuine strengthening with an observed-RED control, scoped to
exactly one assertion in one file.**

---

## 7. FINDINGS L AND M

**L — drift detection, read from the live code.** `crosswalk_missing_region_safes()` and
`crosswalk_covered_region_safes()` exist in `build_curated_m2_crosswalk.py:544-588`, and
`finemap.smk:160-197` (module scope only — confirmed no overlap with the `shell:` block T2
touched) computes `_CURATED_MISSING` from `config["paths"]["regions_curated"]` (not
`REGION_SAFE_TO_ID`, matching the stated availability concern) and WARNs by name when non-empty,
as an `else:` branch after the existing fully-empty-dict WARN — genuinely coverage-aware, not
only firing on total emptiness. `tests/m3/test_curated_m2_crosswalk_drift.py` is confirmed to be
the first module reading `COMMITTED_TSV` directly (`config/curated_to_m2_region_map.tsv`), and
`test_the_committed_crosswalk_is_byte_identical_to_a_fresh_rebuild` passes with no
`pytest.skip` guard on the chain file (confirmed present:
`data/external/liftover/hg38ToHg19.over.chain.gz`).

**M — allow-list, read from the live code.** `_LOADABLE_STATUSES = ("contained",)` at
`build_curated_m2_crosswalk.py:478`; `load_curated_to_m2` refuses any status not in this tuple
and prints a named WARN (`build_curated_m2_crosswalk.py:518-537`). **`"partial"` is confirmed
genuinely emitted** by `select_m2_candidate` (`build_curated_m2_crosswalk.py:257`,
`return _row(min(overlapping, key=_rank_partial), "partial", 0)`), not a hypothetical status —
I grepped this myself.

**NC-M1 reproduced live.** I changed `_LOADABLE_STATUSES` to `("contained", "partial")`
(byte length changed) and ran the drift module: **3 failed, 9 passed**, exactly matching the
SUMMARY's claimed count, including `test_the_allow_list_is_an_allow_list_not_a_deny_list`.
Restored to green (12 passed).

**Verdict: L and M are both engineering-complete, verified by direct execution and by a live
revert that reproduces the claimed failure signature exactly.**

---

## 8. The negative controls — existence and genuine failure capacity

| Control | Type | My verification |
|---|---|---|
| NC-G1 (revert to `endswith`) | one-off | **Reproduced live: 8 failed** (exact match) |
| NC-G2 (stub to `return True`) | one-off | **Reproduced live: 12 failed** (exact match) |
| NC-G3 (fourth unregistered entry) | permanent, in-suite | Read + ran — passes; asserts registry check names a synthetic `AFR_aou_v2` entry |
| NC-J1 (pre-change receipt ambiguity) | permanent, in-suite | Read + ran — passes; extracts `6b427bc`'s receipt via the same extractor, drives it over the same fixtures, asserts it cannot distinguish them |
| NC-J2 (program actually changed) | permanent, in-suite | Read + ran — passes; guards NC-J1 against a no-op edit |
| NC-L1 (byte perturbation of committed TSV) | permanent, in-suite | Read + ran — passes; perturbs a **copy**, never the committed file, asserts the byte comparison catches it |
| NC-L2 (dropped row reported by name) | permanent, in-suite | Read + ran — passes; drops a row from a copy, asserts `crosswalk_missing_region_safes` names it and stays `[]` on the unmodified file |
| NC-M1 (deny-list revert) | one-off | **Reproduced live: 3 failed** (exact match) |
| NC-AUTH-b77-01 (narrowed pin still catches a `region_id` edit) | permanent, in-suite | Read + ran — passes; builds a real throwaway git repo, perturbs a copy, drives the real assertion, asserts it raises |

**None of these controls appears structurally incapable of failing.** Every one carries an
explicit non-vacuity guard (byte-length checks on the perturbation, "real diff must be
non-empty" checks, anchor-occurs-exactly-once checks before a brace-walk). I directly
reproduced three of the one-off controls myself and got the exact failure counts claimed; the
six permanent-in-suite controls all pass with their internal `pytest.raises`/differential
assertions genuinely exercised (confirmed by reading the assertion logic, not merely the test
name).

---

## 9. Honesty about inertness — accurate and prominent, not buried

The SUMMARY states plainly, under a `⛔ READ THIS FIRST` heading immediately after the title
(not buried in a footnote), that: G's closure makes TRANS's failure **visible**, not working
(TRANS still resolves to `EUR_1kg`); `strict_aou_only: false` ships, so the strict half is
inert; L's WARN is inert today because the committed crosswalk is in sync (0 missing slugs,
confirmed by running `test_every_curated_region_has_a_crosswalk_row` directly); M's allow-list
is inert today because all 11 mapped rows are `contained` (confirmed:
`load_curated_to_m2(committed) == 6b427bc's loader`, `len == 11`, verified in the drift-test
run). The only behavioral change identified — the receipt's token substitution for J — is
correctly identified as the sole thing that changes on a currently-firing path
(`HLA_6p21`/`PYHIN1_1q23` are genuinely `too_many_variants` regions per the R source I read).
**I found nothing claimed as "working" that is actually inert; the disclosure is accurate.**

---

## 10. Scope and freeze — independently re-measured

```
$ git diff --exit-code dc4bbd2 -- run_susie_rss.R                                     -> clean
$ git diff --exit-code 6b427bc -- plink_ld_to_npz.py ld_npz_to_rds.R condition_ld_matrix.py -> clean
$ git diff --exit-code 6b427bc -- occlusion_catalog.py occlusion_lockstep_cli.py \
    drop_occluded_from_sumstats.py occlusion_span_filter.py m3_occlusion_lockstep.smk -> clean
$ git diff --exit-code 6b427bc -- pipeline.schema.yaml                                -> clean
$ git diff --name-only 6b427bc HEAD -- src config tests | sort
config/pipeline.yaml
src/python/build_curated_m2_crosswalk.py
src/python/ld_panel.py
src/snakemake/rules/finemap.smk
tests/m3/test_curated_m2_crosswalk_drift.py
tests/m3/test_finemap_receipt_early_exit.py
tests/m3/test_ld_panel_aou_orphan_and_strict.py
tests/m3/test_qtl_coloc_allele_join.py          <- the one authorized pre-existing test
$ git diff 6b427bc HEAD -- src config tests | grep -icE "condition_ld_matrix|nan_to_num|gsutil|gcloud|dataproc|hailctl" -> 0
$ git diff --stat HEAD -- .planning/ROADMAP.md .planning/STATE.md .planning/HANDOFF.json -> empty
```

`build_qtl_coloc_manifest.py::_ancestry_for_region` (E-4) still returns `"EUR"` unconditionally
(read directly, no diff to this file). No diff touches `run_qtl_coloc.R` or the allele-join
files that closed H/E. m3-06 stays HELD (`condition_ld_matrix`/`nan_to_num` grep = 0). No
perimeter-contact token anywhere in the diff.

---

## Both suites — measured myself, one run each

```
$ tests/m3 -q -rs
807 passed, 31 skipped, 4 warnings in 878.08s (0:14:38)
```
All 31 skips confirmed pre-existing (19× hail, 8× hg19ToHg38 chain absent, 1× M2 union BED,
1× hail not installed, 1× SKELETON gate, 1× AoU-perimeter gate) — none originate from the three
new modules.

```
$ tests/phase2 -q -rs
136 passed, 1 skipped in 1.30s
SKIPPED [1] tests/phase2/test_negative_controls.py:138: bedtools not available in test environment
```

Both exactly match the SUMMARY's claimed numbers and the plan's acceptance thresholds
(`tests/m3` ≥745/31/0 → measured 807/31/0; `tests/phase2` exactly 136/1/0 → measured 136/1/0).

`snakemake --list` rc 0 on all four configs (`pipeline.yaml` + three `lsweep` overlays),
re-run directly, not copied from the log.

`tests/m3/sparse_parent_benchmark.tsv`: my own test runs dirtied it (expected — the suite
rewrites it on every run); restored with `git checkout --` and confirmed clean, and confirmed
the executor's own diff (`git diff 6b427bc HEAD`) never touched it.

---

## Observable Truths (from PLAN must_haves)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | Strict-mode TRANS with head absent raises `FileNotFoundError` | ✓ VERIFIED | `test_strict_mode_raises_for_trans_when_the_orphaned_head_is_absent` passes; reproduced RED under NC-G1 |
| 2 | Shipped config (`strict_aou_only: false`) resolution byte-identical to `6b427bc` for all curated slugs × ancestries | ✓ VERIFIED | `test_shipped_config_resolution_is_identical_to_the_baseline` passes (4 trees × 23 pairs × 3 ancestries); inverted control confirms non-tautological |
| 3 | New AoU chain entry cannot be added without a producer or orphan-registry entry | ✓ VERIFIED | `test_the_registry_covers_exactly_the_shipped_aou_sources` + `test_nc_g3_...` both pass; reproduced RED under NC-G2/NC-G1 |
| 4 | Receipt distinguishes early-exit from regression via different tokens | ✓ VERIFIED | `NA_EARLY_EXIT != ABSENT`, verdicts differ; `test_the_early_exit_token_and_the_alarm_token_are_not_equal` passes |
| 5 | Drifted committed crosswalk fails the suite | ✓ VERIFIED | `test_the_committed_crosswalk_is_byte_identical_to_a_fresh_rebuild` passes; NC-L1 reproduces the fail on a perturbed copy |
| 6 | Missing-from-crosswalk curated region produces a named WARN at DAG-parse | ✓ VERIFIED | `finemap.smk:167-197` coverage-aware `else:` branch; `test_the_partial_coverage_warn_actually_fires_and_names_the_slugs` passes |
| 7 | `status=partial` row not handed to `resolve_ld_path`; old loader shown to hand it over | ✓ VERIFIED | `test_m_the_new_loader_refuses_a_partial_row_and_the_old_one_admits_it` passes (differential against `6b427bc`); reproduced RED under NC-M1 |
| 8 | K registered as prepared deferral with diff, blast radius, re-freeze obligation, both authorizations | ✓ VERIFIED | `deferred-items.md` K-1 entry read directly, all four elements present, six-site enumeration independently re-confirmed by grep |

**Score: 8/8 truths verified.**

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `src/python/ld_panel.py` | token-based `is_aou_source`; strict guard uses it | ✓ VERIFIED | `def is_aou_source` present, exported in `__all__`, guard at line 124 calls it |
| `src/snakemake/rules/finemap.smk` | status-aware receipt; coverage-aware WARN | ✓ VERIFIED | `d.get('ld_allele_catalog_join')` present (1 hit); coverage WARN at module scope |
| `src/python/build_curated_m2_crosswalk.py` | contained-only allow-list + drift/coverage readers | ✓ VERIFIED | `def load_curated_to_m2` present; `_LOADABLE_STATUSES = ("contained",)` |
| `tests/m3/test_ld_panel_aou_orphan_and_strict.py` | G — verdict table, orphan registry, strict-mode proof | ✓ VERIFIED | 32 tests, all pass |
| `tests/m3/test_finemap_receipt_early_exit.py` | J — differential receipt test | ✓ VERIFIED | passes as part of 170-test run |
| `tests/m3/test_curated_m2_crosswalk_drift.py` | L/M — drift, coverage, partial-rejection | ✓ VERIFIED | 12 tests, all pass |
| `.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md` | G-2 + K-1 | ✓ VERIFIED | Both entries present, K-1 contains all 4 required elements |

**Score: 7/7 artifacts verified (exists, substantive, wired — all confirmed by direct execution).**

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `ld_panel.py::resolve_ld_path` | `ld_panel.py::is_aou_source` | strict guard predicate | ✓ WIRED | `is_aou_source(entry["source"])` at line 124, confirmed live |
| `test_ld_panel_aou_orphan_and_strict.py` | `config/pipeline.yaml` `ld_panel` block | `yaml.safe_load` of REAL config | ✓ WIRED | `SHIPPED_CONFIG = PROJECT_ROOT / "config" / "pipeline.yaml"`, `yaml.safe_load` confirmed at line 173 |
| `test_finemap_receipt_early_exit.py` | `finemap.smk` shell block | extraction of live `PYTHON_BIN -c` line | ✓ WIRED | `_receipt_program(FINEMAP_SMK.read_text())` confirmed |
| `finemap.smk` module scope | `build_curated_m2_crosswalk.py` drift reader | import + named WARN | ✓ WIRED | `from build_curated_m2_crosswalk import crosswalk_missing_region_safes, load_curated_to_m2` at line 84-86 |

**Score: 4/4 key links verified.**

### Data-Flow Trace (Level 4)

Not applicable in the conventional UI-rendering sense (this is pipeline/CLI logic, not a
component tree). The equivalent trace was performed directly: `is_aou_source` was run against
the REAL loaded `config/pipeline.yaml` (not a mock), `load_curated_to_m2` was run against the
REAL committed `config/curated_to_m2_region_map.tsv`, and the receipt program was extracted from
the REAL live `finemap.smk` text and executed via `subprocess` against JSON fixtures — in every
case the "data source" is the actual shipped artifact, not a stand-in, and I independently
re-ran all of it.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Predicate partition matches shipped config exactly | direct `is_aou_source` enumeration over `yaml.safe_load(config/pipeline.yaml)` | True-set = `{EUR_aou, AFR_aou, TRANS_aou_eur}`, False-set = other 5 | ✓ PASS |
| NC-G1 revert produces claimed RED count | live revert + pytest | 8 failed (exact match) | ✓ PASS |
| NC-G2 revert produces claimed RED count | live revert + pytest | 12 failed (exact match) | ✓ PASS |
| NC-M1 revert produces claimed RED count | live revert + pytest | 3 failed (exact match) | ✓ PASS |
| Full `tests/m3` suite | `pytest tests/m3 -q -rs` | 807 passed / 31 skipped / 0 failed | ✓ PASS |
| Full `tests/phase2` suite | `pytest tests/phase2 -q -rs` | 136 passed / 1 skipped / 0 failed | ✓ PASS |
| `snakemake --list` on all 4 configs | `snakemake --list` | rc 0 × 4 | ✓ PASS |
| AUTH-b77-01 attribution table | `git diff 7b1025d <rev> -- finemap.smk \| wc -l` | 0, 0, 0, 72 (exact match) | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| BR-G | 260806-b77-PLAN | close finding G | ✓ SATISFIED | §2 above |
| BR-J | 260806-b77-PLAN | close finding J | ✓ SATISFIED | §4 above |
| BR-K | 260806-b77-PLAN | register K as prepared deferral (the plan's own must-have #8, not a closure) | ✓ SATISFIED (as a deferral, by design) | §5 above |
| BR-L | 260806-b77-PLAN | close finding L | ✓ SATISFIED | §7 above |
| BR-M | 260806-b77-PLAN | close finding M | ✓ SATISFIED | §7 above |

No orphaned requirements — `.planning/REQUIREMENTS.md` does not map BR-G/J/K/L/M (this is a
quick-task blast-radius closure, self-scoped by the finding IDs in the blast-radius doc, not
phase-level REQUIREMENTS.md entries).

### Anti-Patterns Found

None. Grepped all four touched source files for `TODO|FIXME|XXX|HACK|PLACEHOLDER`,
`placeholder|coming soon|not yet implemented`, and hardcoded-empty-return patterns — no hits
that aren't legitimate (`return {}` in `load_curated_to_m2` on a missing file, and `return
set()` in `crosswalk_covered_region_safes` on a missing file, are both explicit, tested,
fail-safe "fresh clone must still build" contracts, not stubs — each is covered by
`test_an_absent_crosswalk_reports_every_curated_slug_and_still_loads_empty`).

### Human Verification Required

None. Every claim in this task is a pure Python/R/YAML logic change verifiable by direct
execution — no UI, no external service, no real-time behavior, no visual component. I was able
to independently reproduce every load-bearing number (including three live source reverts) on
this node without needing human judgment calls.

### Gaps Summary

No gaps found. Every one of the ten items in the verification brief was independently
re-derived from the codebase (not accepted from the SUMMARY) and confirmed accurate, including
three live reverts that reproduced the exact claimed failure counts (NC-G1: 8, NC-G2: 12,
NC-M1: 3) and one exact-match numeric table (the AUTH-b77-01 attribution: 0/0/0/72). The two
scientifically-open items (G-2: is a TRANS fit on 1kG EUR reportable; K-1: restore
`variant_catalog_fallback`'s legacy meaning) are correctly registered as Carter's calls rather
than resolved silently, and the SUMMARY's "TWO cleared, ONE partial" framing matches the
blast-radius doc's own gate table exactly — no partial closure is reported as a full one.

---

_Verified: 2026-08-06_
_Verifier: Claude (gsd-verifier)_
