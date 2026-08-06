---
phase: quick/260805-w7u
verified: 2026-08-06T05:39:08Z
status: passed
score: 8/8 must-haves verified
overrides_applied: 0
---

# Quick 260805-w7u: Close blast-radius finding E — Verification Report

**Task goal:** Close blast-radius finding **E** (`m3-04c-BLAST-RADIUS.md:141`, gate row
"Any GWAS×QTL colocalization") — `qtl_coloc.smk` had zero crosswalk/resolver references and
would colocalize an AFR GWAS fit (produced on the AoU panel) against a legacy 1kG LD matrix —
together with the coupled coloc-side key defect and matrix-class defect that closing E alone
would activate.

**Verified:** 2026-08-06T05:39:08Z
**Status:** passed
**Method:** Independent re-derivation. Read every changed file end-to-end, re-ran both new
test modules and the full `tests/m3` / `tests/phase2` suites live, reproduced NC-1c by hand
against the real Snakefile/schema/config, traced the R control flow line-by-line for the
loud-failure and bounded-coercion claims, and independently verified scope/freeze diffs with
raw `git diff`/`git show`. SUMMARY claims were treated as hypotheses to re-derive, not facts.

## Goal Achievement

### Observable Truths (from PLAN frontmatter `must_haves.truths`, 1:1 with roadmap gate row E)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | For an allow-listed ancestry the LD `.rds` reaching `coloc::runsusie` is the SAME artifact `resolve_ld_path` hands `run_finemap` | ✓ VERIFIED | `qtl_coloc.smk:311-326` calls `resolve_ld_path(region_id=ld_matrix_region_id(...))` with `CURATED_TO_M2`/`REGION_SAFE_TO_ID` **reused** from `finemap.smk`'s module scope (`grep -c "load_curated_to_m2" qtl_coloc.smk` = 0, confirmed live). `test_gate_on_equals_finemap_smk_ld_matrix_lambda` evaluates `finemap.smk`'s REAL `ld_matrix=` lambda (extracted from source text, not retyped) and asserts equality — passed independently. |
| 2 | The manifest can no longer supply a competing LD path for a gated ancestry; it emits a value provably not a path | ✓ VERIFIED | `build_qtl_coloc_manifest.py:122` `LD_PATH_RESOLVER_SENTINEL = "RESOLVED_BY_LD_PANEL_RESOLVER"`; `:349-350` writes it for gated ancestries. `test_gate_on_ignores_a_competing_existing_manifest_path` proves the resolver's answer wins even when the manifest names a **different, existing** file — passed independently. |
| 3 | A panel row binds to the GWAS-fit variant whose REF/ALT it actually matches, never an arbitrary ALT at the same position | ✓ VERIFIED | `ld_allele_join.R:125-230` — two `match()` calls on 4-keys, ambiguity guard nulls duplicated panel 4-keys out of the match table before matching. Read the full function; matches the multiallelic/transposed/palindromic/mismatch/ambiguous/unusable spec exactly. Differential agreement against the shipped matcher (see truth 8) confirms semantic equivalence. |
| 4 | Gate ON + unbridgeable/sub-threshold ⇒ EXITS NON-ZERO, named reason, no status JSON written | ✓ VERIFIED | `run_qtl_coloc.R:206-220` `ld_join_stop()` calls `stop(sprintf(...))` — R `stop()` at top level is a non-zero exit that halts before any `write_status_json`. `test_unbridgeable_catalog_exits_non_zero_with_a_named_reason` asserts `returncode != 0`, `not out.exists()`, and every named field present in stderr — **ran independently, passed.** Snakemake's `shell:` blocks run under implicit strict-mode, so a non-zero `Rscript` exit fails the rule (the receipt line, guarded `|| true`, only runs after a successful `Rscript` call and cannot mask this). |
| 5 | LD handed to `coloc::runsusie` is a base matrix, produced WITHOUT densifying the full panel | ✓ VERIFIED | `run_qtl_coloc.R:550-551`: `idx <- as.integer(ld_row_index[overlap_snps]); ld_matrix_subset <- as.matrix(ld_full[idx, idx, drop = FALSE])` — subset by integer index **first**, coerce the subset only. `test_the_full_panel_is_never_densified` asserts `"as.matrix(ld_full)"` and `"as.matrix(ld_obj$R)"` are absent from source; `test_subset_then_coerce_is_bounded_on_a_panel_much_larger_than_the_subset` drives a ~3.9 GB dense-equivalent sparse fixture through the real subset-then-coerce shape — both passed independently. |
| 6 | Every disposition class and the opened panel path reach the per-pair JSON and a per-pair log receipt | ✓ VERIFIED | `run_qtl_coloc.R:176-198` `ld_provenance()` builds the 10-field block; `qtl_coloc.smk:497-509` emits a `log.ld_receipt` reading every field from the output JSON. `test_the_per_pair_receipt_reads_every_counter` and `test_every_disposition_class_reaches_the_json` — passed independently. |
| 7 | For EUR (off allow-list) emitted JSON is BYTE-IDENTICAL to `7b1025d`'s, proven with an inverted control observed non-identical | ✓ VERIFIED | Structural: off `LD_ALLELE_JOIN`, every conditional branch reduces to `7b1025d`'s exact code (`ld_provenance()` returns `list()` off-gate — R's `list(k=NULL)` trap correctly avoided). `test_eur_json_is_byte_identical_to_7b1025d` (both flag-absent and flag-`false` forms, with a non-vacuity guard requiring `status=="success"` on the pre-change side) and `test_inverted_control_afr_with_the_gate_on_is_not_identical` (asserts non-identical bytes AND `status` differs: `success` vs `too_few_snps`) — **both ran independently, passed.** |
| 8 | The new matcher agrees with the SHIPPED `run_susie_rss.R` matcher, differentially, against a body-walk extraction (never hand-copied), with controls observing RED for a perturbed new matcher AND a perturbed extraction source | ✓ VERIFIED | `extract_nested()` (`tests/m3/test_qtl_coloc_allele_join.py:189-232`) walks `body(load_ld_matrix)` for the `<-` assignment and `eval()`s the RHS — read in full; genuinely reads real source text via `_loader_functions_only`, never retypes logic. `test_the_shipped_matcher_is_not_reachable_without_the_body_walk` proves the necessity (`match_indices_allele_aware` absent at top level after sourcing the prefix alone). NC-2f (perturb `ld_allele_join.R`) and NC-2g (4 tests: 3 parametrized source alterations + 1 assignment-deletion) both alter **in-memory copies**, assert disagreement, and re-assert `git diff --exit-code dc4bbd2 -- run_susie_rss.R` mid-control — all ran independently, all passed. |

**Score:** 8/8 truths verified.

### ★ Item 1 — E-4, answered directly

**`build_qtl_coloc_manifest.py::_ancestry_for_region` (line 250) returns `"EUR"`
unconditionally** — confirmed by direct read, and confirmed **pre-existing and unchanged**:
`git show 7b1025d:src/python/build_qtl_coloc_manifest.py` carries the identical function at
line 220. This is not a regression introduced by this task; it is a pre-existing condition
this task discovered and disclosed (docstring at `build_qtl_coloc_manifest.py:276-281`,
SUMMARY §2 "Nothing moves today", `deferred-items.md` E-4 entry).

**Consequence, independently confirmed:** with the shipped allow-list (`ancestries: [AFR]`)
and every manifest row's ancestry hardcoded to `"EUR"`, `ld_coloc_applies("EUR", config)` is
`False` for every row the builder can currently produce — the sentinel branch and the
resolver branch are both **unreachable in production today**, not merely untested.

**Direct answer to "does the gate row actually become safe, or is it merely
no-longer-wrong-in-principle?"**

Both, in a way that matters to state precisely:

- **Trivially safe today**, but not *because of* this fix: zero AFR QTL-coloc jobs exist in
  the manifest at `7b1025d` OR at HEAD (same hardcoded-EUR condition, unchanged by this task).
  Finding E's specific scenario — an AFR GWAS fit colocalized against a 1kG LD matrix — cannot
  occur today with or without this patch, because no AFR coloc job is ever generated.
- **What this task actually bought:** the WIRING is now correct and machine-verified against
  fixtures (104 new tests, all independently re-run and passing; differential agreement
  against the real frozen matcher; byte-identical EUR containment with an inverted control).
  That is "no longer wrong in principle" in the strongest sense available without a real
  panel — but it has **not been exercised end-to-end against a single real AFR coloc job**,
  because none can exist until `_ancestry_for_region` is taught about AFR (a separate,
  correctly-out-of-scope decision per Deviation 1, since it would change the manifest's row
  set and `qtl_coloc_id` space for a pipeline that currently feeds Track A).
- The gate row "Any GWAS×QTL colocalization" in the phase's blast-radius table is fairly
  marked DISCHARGED **as a code-level defect** — the mixing-LD-panels defect no longer exists
  in the code path that would be taken once AFR rows appear. It should **not** be read as "AFR
  colocalization is now safe to run" in a production sense, because no AFR colocalization can
  run at all yet. This distinction is not hidden by the executor (SUMMARY §2 states it in bold,
  `deferred-items.md` E-4 registers it explicitly) — but it is worth restating plainly here per
  the verification brief: **the fix is currently inert, and its safety claim is conditional on
  wiring correctness, not on production exercise.**

This is not scored as a gap: none of the plan's 8 must-have truths claim production exercise
was possible (the plan's own `<precondition_stated_honestly>` block states "THE PANEL DOES NOT
EXIST. THIS IS WIRING THAT GOES LIVE AFTER THE FIRE" and forbids any acceptance criterion that
depends on a real panel). The disclosure obligation is met, not evaded.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `src/python/ld_read_path.py` | `ld_coloc_applies` — single gate | ✓ VERIFIED | Function present (`:158-198`), `is True` (not truthiness), exported in `__all__`; `ld_coloc_join`/`ld_coloc_ancestries` also present and correctly derived from the single predicate. |
| `src/snakemake/rules/qtl_coloc.smk` | resolver-routed input, threading, receipt | ✓ VERIFIED | `_qtl_coloc_ld_input` (`:295-327`) routes through `resolve_ld_path`; `--ld-allele-join {params.ld_allele_join}` count = 1; `--variant-list` token unconstructible off-allow-list (`variant_list_flag` param, verified by direct read + `test_the_variant_list_token_is_unconstructible_off_the_allow_list`); per-pair receipt present (`:497-509`). |
| `src/python/build_qtl_coloc_manifest.py` | `--resolver-ancestries`, sentinel | ✓ VERIFIED | `LD_PATH_RESOLVER_SENTINEL` present, threaded through `build_manifest`, default `None` reproduces `7b1025d` byte-for-byte (independently re-run, passed). |
| `src/snakemake/scripts/ld_allele_join.R` | shared join, `source()`-able | ✓ VERIFIED | `ld_allele_join_indices(subset_dt, variants_dt)` present and exported; no top-level execution; header discloses the deliberate-duplication rationale. |
| `src/snakemake/scripts/run_qtl_coloc.R` | bridge, hard `stop()`, bounded coercion, provenance | ✓ VERIFIED | All four confirmed by direct code trace (see truths 4-7 above). |
| `tests/m3/test_qtl_coloc_ld_resolution.py` | resolution + containment + no-second-crosswalk control | ✓ VERIFIED | 45 tests, independently re-run: all pass. |
| `tests/m3/test_qtl_coloc_allele_join.py` | join acceptance, differential agreement, byte-identity + inverted control | ✓ VERIFIED | 59 tests including `extract_nested`, independently re-run: all pass. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `qtl_coloc.smk::_qtl_coloc_ld_input` | `ld_panel.py::resolve_ld_path` | `ld_matrix_region_id(CURATED_TO_M2, REGION_SAFE_TO_ID)` | ✓ WIRED | Direct call at `qtl_coloc.smk:312-320`; equality with `finemap.smk`'s real lambda proven by extraction-and-execution, not retyping. |
| `config/pipeline.yaml ld_read_path.coloc` | `ld_read_path.py::ld_coloc_applies` | same allow-list, second lever | ✓ WIRED | `coloc: true` present in shipped config; `_ld_read_path_block(config).get("coloc") is True` reads it. |
| `qtl_coloc.smk params.ld_allele_join` | `run_qtl_coloc.R --ld-allele-join` | rendered shell arg | ✓ WIRED | `grep -c -- '--ld-allele-join {params.ld_allele_join}' qtl_coloc.smk` = 1 (independently re-run). |
| `run_qtl_coloc.R` | `ld_allele_join.R` | `source()` | ✓ WIRED | `source(LD_ALLELE_JOIN_R)` at `run_qtl_coloc.R:164`, gated so a missing file cannot change the ungated return code. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| New test modules pass in isolation | `pytest tests/m3/test_qtl_coloc_ld_resolution.py tests/m3/test_qtl_coloc_allele_join.py -q` | `104 passed in 68.24s` | ✓ PASS |
| `tests/m3` full suite | `pytest tests/m3 -q -rs` | `745 passed, 31 skipped, 0 failed in 806.55s` — exact match to SUMMARY's claim, same 31 skip origins (hail imports, chain files, M2 union BED, perimeter gate, one skeleton) | ✓ PASS |
| `tests/phase2` full suite | `pytest tests/phase2 -q -rs` | `136 passed, 1 skipped (bedtools)` — exact match | ✓ PASS |
| `--list` on real config + 3 lsweep overlays | `snakemake --list` × 4 configs | `OK` on all four | ✓ PASS |
| NC-1c reproduced by hand | schema WITH `coloc` entry + `coloc: "not-a-boolean"` in config | `ValidationError: 'not-a-boolean' is not of type 'boolean'`, rc=1 | ✓ PASS |
| NC-1c inverse reproduced by hand | schema WITHOUT `coloc` entry (temp-swapped, restored clean after) + same bad value | rc=0, 0 `ValidationError` occurrences | ✓ PASS |
| Scope diff | `git diff --name-only 7b1025d HEAD -- src config tests` | Exactly the 9 files in `files_modified` | ✓ PASS |
| Freeze | `git diff --exit-code dc4bbd2 -- run_susie_rss.R` | clean | ✓ PASS |
| Frozen contracts / out-of-scope files | `git diff --exit-code 7b1025d -- finemap.smk aggregate_qtl_coloc.py ld_panel.py plink_ld_to_npz.py ld_npz_to_rds.R condition_ld_matrix.py` + m3-07 modules | all clean | ✓ PASS |
| Perimeter strings | `git diff 7b1025d HEAD | grep -iE "gsutil\|gcloud\|bq\|dataproc\|hailctl\| wb "` | 0 matches | ✓ PASS |
| STATE/HANDOFF/ROADMAP | `git diff --name-only 7b1025d HEAD` filtered | 0 matches | ✓ PASS |
| E-2 arithmetic | `46 / (136 + 46)` | `0.25275` ≈ 25.3% as claimed | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| `E` | 260805-w7u-PLAN | Close gate row "Any GWAS×QTL colocalization" | ✓ SATISFIED (as a code-level fix; see E-4 caveat above) | Resolver routing, sentinel, allele join, loud failure, bounded coercion, byte-identical EUR — all independently verified. |
| `E-coupled-key` | 260805-w7u-PLAN | Allele-blind coloc join defect | ✓ SATISFIED | `ld_allele_join.R` + differential agreement, independently re-run and passing. |
| `E-coupled-class` | 260805-w7u-PLAN | Sparse-matrix-to-`coloc::runsusie` defect | ✓ SATISFIED | Subset-then-coerce, gated, measured cost-free on the legacy path (`plink_ld_to_rds.R:72` confirmed `R <- as.matrix(ld_dt)`, a base matrix). |

### Anti-Patterns Found

None. No TODO/FIXME/placeholder markers in the changed files; no empty handlers; no
hardcoded-empty stub returns on any live path. The one `write_status_json` + `quit(status=0)`
pattern that remains (the pre-LD-intersection `n_snps_overlap < 50` gate at `:340`) is
correctly scoped as F3-out-of-family (fires before any LD is loaded — a data-availability
fact, not a verification-impossibility) and is explicitly justified in SUMMARY Deviation 7.

### Scope Discipline (item 8)

All confirmed by direct `git diff`, not by claim:
- `git diff --name-only 7b1025d HEAD -- src config tests` = exactly the plan's 9
  `files_modified`, nothing else.
- Findings G, J, K, L, M and BLOCKER-D's MC4R/FTO/HLA classes: no functional touch (the one
  `FTO_16q12` string hit in the diff is a synthetic two-region test fixture in the new test
  file, unrelated to BLOCKER-D's large-region handling).
- H and I: not re-opened (full `tests/m3` suite, including their modules, passed 0 failed).
- `run_susie_rss.R` 0-diff vs `dc4bbd2`; `finemap.smk`, `aggregate_qtl_coloc.py`, `ld_panel.py`,
  `plink_ld_to_npz.py`, `ld_npz_to_rds.R`, `condition_ld_matrix.py`, and all four m3-07
  occlusion modules 0-diff vs `7b1025d`.
- `params.region_id` byte-unchanged (0 `region_id` hits in the `finemap.smk` diff, which is
  itself 0-diff).
- m3-06 held: 0 `condition_ld_matrix|nan_to_num` hits anywhere in the diff.
- No `gsutil`/`gcloud`/`bq`/`dataproc`/`hailctl`/` wb ` string anywhere in the diff.
- `.planning/STATE.md`, `.planning/HANDOFF.json`, `.planning/ROADMAP.md`: untouched.

### Human Verification Required

None. Every claim in the verification brief was either re-derived from source code directly,
confirmed by an independent live test run, or reproduced by hand against the real repository
state (NC-1c). No visual, real-time, or external-service behavior is involved in this task.

### Gaps Summary

No gaps. All 8 must-have truths, all 7 required artifacts, and all 4 key links verified
independently against the live codebase, not from the SUMMARY's prose. The full `tests/m3`
(745 passed / 31 skipped / 0 failed) and `tests/phase2` (136 passed / 1 skipped) suites were
re-run live and match the SUMMARY's reported numbers exactly, including the origin of every
skip. Scope and freeze diffs were confirmed directly via `git diff`/`git show`, not accepted
from the SUMMARY's assertions.

**One finding requires prominent restatement, not remediation:** E-4 (`_ancestry_for_region`
hardcoded to `"EUR"`, pre-existing and unchanged by this task) means the wiring this task
built is currently **inert** — no AFR QTL-coloc job can exist to exercise it. The executor
disclosed this thoroughly and accurately (SUMMARY §2, Deviation 1, `deferred-items.md` E-4);
this report restates it because the verification brief specifically asked for a direct answer
on whether the gate row is "actually safe" versus "no-longer-wrong-in-principle" — the honest
answer is the latter, with the safety of today's (zero-AFR) production state owed to a
pre-existing, unrelated condition rather than to this fix. This does not change the pass/fail
determination: the plan never claimed production exercise, and the precondition was stated
honestly in the plan itself before execution began.

---

*Verified: 2026-08-06T05:39:08Z*
*Verifier: Claude (gsd-verifier)*
