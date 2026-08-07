---
phase: quick/260806-pd3
verified: 2026-08-06T00:00:00Z
status: gaps_found
score: 8/9 verifier claims verified (claim 6 FAILED); 7/7 plan must-have truths verified in scope
verifier: Claude (gsd-verifier)
commits_verified: [bf04199, 9538af0]
baseline_rev: 63453db
branch: m3-W2-aou-deltas
overrides_applied: 0
gaps:
  - truth: "The corrected artifact census (D-2) is accurate in the four shipped places that now carry it"
    status: failed
    reason: >-
      The shipped pair 1,944 / 1,935 is a REPO-WIDE count of every *.json carrying
      the key (minus .planning/HANDOFF.json), not a count of region JSONs. Scoped to
      results/legacy/region_analysis -- which is exactly what all four shipped
      sentences claim -- the correct values are 1,909 carrying the key, 1,900 false,
      9 true. The excess 35 files are 17 .planning/debug/stage2_narrow_validation/**
      fit JSONs plus 18 results_lsweep_*.bak/fine_mapping/susie/* backup JSONs, none
      of which is under results/legacy/region_analysis. The error is also INTERNALLY
      INCONSISTENT with the 687-of-2,596 figure shipped in the same paragraph in
      three of the four places: 2,596 - 687 = 1,909, not 1,944. The executor's D-2
      diagnosis (grep -r vs grep -R, the symlink) is CORRECT and its qualitative
      conclusions all hold; only the two headline integers are mis-scoped.
    artifacts:
      - path: "src/legacy/region_analysis/scripts/run_susie_rss.R"
        issue: ":1018-1019 -- '1,944 measured 2026-08-06 -- 1,935 false'. This is inside the FROZEN file, so correcting it needs a NEW unfreeze (AUTH-K1-UNFREEZE is SPENT) and another re-pin cascade."
      - path: "src/snakemake/rules/finemap.smk"
        issue: ":541 -- 'This is what 1,935 of the 1,944 legacy ...'; contradicts :538's correct '687 of the 2,596 region'."
      - path: "tests/m3/test_finemap_receipt_early_exit.py"
        issue: ":558 -- '1,935 of the 1,944 legacy JSONs that DO carry the key render this.' A COMMENT only -- no assertion depends on it; :553's 687/2,596 is correct."
      - path: ".planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md"
        issue: ":365-369 -- '**1,944** region JSONs carry variant_catalog_fallback -- **1,935 false** and **9 true**'; :369's 687-of-2,596 is correct and contradicts it."
    missing:
      - "Correct 1,944 -> 1,909 and 1,935 -> 1,900 in all four places, OR re-label the existing numbers as repo-wide *.json counts and state the region-scoped pair beside them."
      - "Reconcile against the 687-of-2,596 figure already shipped in the same paragraphs (2,596 - 687 = 1,909)."
      - "The R-source correction requires a NEW named unfreeze authorization plus a re-pin of FROZEN_R_REV / FREEZE_REF off bf04199 -- it cannot be done under AUTH-K1-UNFREEZE, which is SPENT."
deferred: []
human_verification: []
---

# quick/260806-pd3 Verification Report

**Task goal:** Close blast-radius finding K-1 — restore `variant_catalog_fallback` to its
legacy semantics by deleting the Path-2 overload from the frozen `run_susie_rss.R`,
strengthening the pre-existing test that mandated that line, fixing the decoder ring the
change breaks, and re-pinning the freeze cascade.

**Verified:** 2026-08-06 · **Status:** `gaps_found` · **Re-verification:** No — initial

**Headline.** The engineering goal is ACHIEVED and every mechanical claim holds under
independent re-derivation. One gap: the census numbers the executor corrected in D-2 are
themselves mis-scoped by +35 and are shipped in four places, one of which is the frozen R
source. This is a documentation-accuracy defect, not a behavioural one — no assertion, no
number, and no science path depends on it.

---

## Claim-by-claim evidence

| # | Claim under verification | Status | Evidence (independently re-derived, not relayed) |
|---|---|---|---|
| **1** | The one-line deletion is exactly one line; five MUST-NOT-MOVE sites byte-identical to `dc4bbd2` | ✓ **VERIFIED** | `git diff 63453db bf04199 -- run_susie_rss.R`: removed non-comment lines = **1**, and it is exactly `    variant_catalog_fallback <- TRUE` (`cat -A` confirms leading 4 spaces, no trailing whitespace). Added non-comment lines = **0**. I re-walked the file with my OWN brace walker (not the suite's) against `git show dc4bbd2:`: `init pair identical: True`, `path1 block identical: True (228 bytes)`, both early-exit emits still at line indices 935/967 in BOTH revisions, `success payload identical: True (3102 bytes)`. The deleted line came from inside the Path-2 `if (ld_overlap == 0 && used_variant_catalog && attempt == 1)` block — confirmed by extracting that block at both revisions. |
| **1b** | Success emit shift `:1208 → :1221` is positional only | ✓ **VERIFIED** | `grep -n` gives `1208` at `dc4bbd2` and `1221` at HEAD (+13, matching the comment reword 6→19 lines). Byte comparison of the whole success `list(...)` payload: **identical, 3,102 bytes**. Nothing pins the R file by line number in an executable assertion. |
| **2** | The strengthened `not in branch` assertion is not vacuous | ✓ **VERIFIED** | `_brace_block` (`test_ld_read_path.py:117-130`) opens with `assert idx != -1, f"anchor not found: {anchor!r}"` — I probed it with a bogus anchor and it **hard-failed**, so `branch` cannot be silently empty. The anchor occurs **exactly once** in the source; the live `branch` is **1,683 bytes**. Three POSITIVE assertions run over the SAME `branch` variable and all pass: `ld_overlap_zero_fallback <- TRUE`, `subset <- copy(subset_base)`, `attempt <- attempt + 1`. I re-derived NC-K3 myself through the suite's own walker on an in-memory splice: **RED**, message `Path 2 must NOT set the legacy variant_catalog_fallback key (K-1)`, and `working tree untouched: True`. |
| **3** | `CAUSE_TOKENS` is derived from live source, not hand-copied — and a rename turns it RED | ✓ **VERIFIED (demonstrated RED)** | `_recovered_cause_tokens()` slices `cause=(...)` out of `_receipt_program(FINEMAP_SMK.read_text())` and applies `re.findall(r"'([A-Za-z0-9_]+)'", ...)` — the class **admits `A-Z`**. The exactly-5 guard is present (`assert len(recovered) == 5`) and satisfied (5 recovered, equal to the literal). **Decisive in-memory perturbation A:** renaming `path2_ld_overlap_zero_RETRY` → `..._REDONE` in the `.smk` text ⇒ `RED (as required) -> literal != recovered`. **Perturbation B** (the plan's warning): a lowercase-only class recovers **3**, not 5 — the warning was real and was designed around. **Perturbation C:** dropping a token ⇒ exactly-5 guard fires `RED`. `working tree untouched: True`. |
| **4** | The decoder ring tells the truth after the change | ✓ **VERIFIED** | I extracted the live `cause=(...)` expression and `eval`'d it directly, bypassing the test entirely: `key absent → key_absent`, `false/false → none`, **`false/TRUE → path2_ld_overlap_zero_RETRY`** (not `none`), `true/true → path2_ld_overlap_zero_NO_NUMERIC_CAUSE`, `true/false → path1_variant_catalog_empty_subset`. The **pre-change** `63453db` expression on the same `(false, true)` input renders **`none`** — the incoherence is real and NC-K5 reproduces it permanently. The four pre-existing parametrise tokens at `63453db` are byte-identical at HEAD (only the case ORDER changed and the 5th was inserted). |
| **5** | The freeze cascade is fully re-pinned code-side | ✓ **VERIFIED** | `grep -rn "dc4bbd2" src tests config Snakefile scripts` returns **9 hits, 0 of them live FREEZE pins**: `finemap.smk:502`, `test_finemap_receipt_early_exit.py:15,:58`, `test_qtl_coloc_allele_join.py:58,:108` are re-pin *narratives* naming `bf04199` as the live pin; `test_qtl_coloc_allele_join.py:1300-1301` is the annotated HISTORICAL AUTH-b77-01 record; `test_variant_catalog_fallback_legacy_semantics.py:78,:82` is `PRE_K1_REF`, the DIFFERENTIAL SUBSTRATE. `FROZEN_R_REV = "bf04199"` and `FREEZE_REF = "bf04199"`. `git diff --exit-code bf04199 -- run_susie_rss.R` → **clean**. The forward gate consumes the new SHA at `test_finemap_receipt_early_exit.py:346`. All five `PRE_CHANGE_REF` substrates (`5ec33bd`, `0378ec8`, `6b427bc`, `7b1025d`) untouched; `PRE_K1_SMK_REF = "63453db"` annotated never-re-pin. |
| **6** | **THE CENSUS CORRECTION (D-2)** | ✗ **FAILED** | See the dedicated section below. The *method* correction (symlink, `grep -r` vs `-R`) is right; the two headline integers are mis-scoped by +35 and self-contradictory. |
| **7** | No number moves | ✓ **VERIFIED** | The Path-2 block's code-only lines at HEAD vs `dc4bbd2` differ by exactly `{variant_catalog_fallback <- TRUE}` removed, `{}` added — `subset <- copy(subset_base)`, `used_variant_catalog <- FALSE`, `ld_overlap_zero_fallback <- TRUE`, `attempt <- attempt + 1`, `next` all survive **in order**. The flag has exactly 5 sites in the R file (`:787` init, `:916` assign, `:936`/`:968`/`:1221` emit) — it is **never read in a conditional anywhere**, so no PIP / credible-set / `ld_overlap` / `ld_status` / `d3b_ld_z_consistency_s` path can depend on it. Its only other consumer is the `finemap.smk` receipt (reporting). All **16** `d.get('<key>')` literals preserved (0 lost, 0 gained vs `63453db`); `{PYTHON_BIN} -c` ×1; `--ld-allele-aware {params.ld_allele_aware}` ×1; `finemap.smk` non-comment changed lines = **2** (one `-`/`+` pair = the single receipt line). `Rscript parse` → `PARSE_OK`. `snakemake --list` on `config/pipeline.yaml` → `LIST_OK`. |
| **8** | Scope containment | ✓ **VERIFIED** | `git diff --name-only 63453db HEAD` = **exactly the 8 files** in the plan's `files_modified`, nothing else. No `STATE.md` / `HANDOFF.json` / `.continue-here.md` / `ROADMAP.md` touched. `results/` or `src/python/` files touched = **0**. AoU + m3-06 forbidden-token scan over the whole diff = **0**. The SUMMARY is written but **UNCOMMITTED** (the whole quick dir is `??` in `git status`; `git log 63453db..HEAD --name-only` contains no SUMMARY). |
| **8b** | AUTH-K1-TEST containment | ✓ **VERIFIED** | `grep -c "^def test_"` on `test_ld_read_path.py` = **8** at both `63453db` and HEAD. Diff hunk headers: `@@ -423,6 +423,24 @@` and `@@ -446,11 +464,11 @@`, **both** carrying the `def test_path2_ld_overlap_zero_fallback_is_observable_and_read` context marker. The `_brace_block(...)` anchor line is **byte-identical** (line 450 → 468, same text). *(Minor: the SUMMARY says "three diff hunks"; there are two. Immaterial.)* |
| **9** | Deferral integrity | ✓ **VERIFIED** | `grep -c "source(" src/legacy/region_analysis/scripts/run_susie_rss.R` = **0** — the extraction was NOT attempted. `deferred-items.md:529-585` registers **K-2 DEFERRED (STILL OPEN)** with all four findings, the verbatim sentence *"Freeze economy is NOT sufficient justification to accept fire-path risk."*, and the three conditions (fail-closed-and-loud / `identical()`-at-both-`allele_aware`-values / re-freeze re-pin at `bf04199`). Mirrored in `ld_allele_join.R` section (d). K-1 marked **CLOSED** at `:303` with the original surface preserved under `### THE ORIGINAL DEFERRAL, PRESERVED`. |

---

## Gap G-1 — the census correction is itself mis-scoped

The executor's D-2 diagnosis is **correct and valuable**: `results/legacy/region_analysis`
is a symlink to `/rs1/researchers/c/ckclinto/coloc_analysis/region_analysis/results`,
`grep -r` does not follow it, `grep -R` does, and the plan's "44, all false" was an artefact
of the wrong flag. Refusing to write "44/44" into frozen source was the right call.

But the replacement numbers are a repo-wide count, not a region-JSON count.

**My independent re-derivation (2026-08-06):**

| Measurement | Shipped | **Re-derived** |
|---|---|---|
| JSONs under `results/legacy/region_analysis` (`find -L`) | 2,596 | **2,596** ✓ |
| — carrying `variant_catalog_fallback` | **1,944** | **1,909** ✗ |
| — of which `false` | **1,935** | **1,900** ✗ |
| — of which `true` | 9 | **9** ✓ |
| — carrying `ld_overlap_zero_fallback` | 0 | **0** ✓ |
| — carrying the key not at all (`key_absent`) | 687 | **687** ✓ |

**Where the +35 comes from.** `grep -Rl` from the repo root over all `*.json` (excluding
`.git`) returns **1,945**. Of those, **1,909** are under `results/legacy/region_analysis`
and **36** are not: 18 under `.planning/` (17 × `.planning/debug/stage2_narrow_validation/
{identity,reald}_fits/*.json` plus `.planning/HANDOFF.json`, which is prose) and 18 under
`results_lsweep_L{15,20,30}.pre{Fix,Niter500}.bak.*/fine_mapping/susie/*.json`.
`1,945 − 1 = 1,944` and `1,900 + 35 = 1,935` reproduce the shipped pair exactly — the
executor subtracted only `HANDOFF.json` and kept the other 35 non-region files.

**The shipped text is self-contradictory.** Three of the four places carry the correct
`687 of the 2,596` alongside the wrong `1,944`. `2,596 − 687 = 1,909`, not 1,944. The two
numbers cannot both be right, and the one that is right is the one the executor did not
highlight.

**What is NOT affected.** Every qualitative conclusion survives intact and was
independently confirmed:

- The 9 `true` artifacts are `asthma.AFR.RAD50_peak__tile1` and eight
  `t2d.AFR.PYHIN1_1q23__tile{5..12}` — **all AFR**, and **all 9 carry zero occurrences of
  `ld_overlap_zero_fallback`**, i.e. genuine Path-1 reverts. K-1's premise (the overload
  would have collided with real `true` artifacts) is **strengthened**, exactly as claimed.
- **0** artifacts anywhere carry `ld_overlap_zero_fallback`, so no artifact was produced
  from an m3-04c-window tree and no before/after JSON diff was possible. The SUMMARY says
  this plainly and does not overclaim.
- The K-1 entry's original "1,957" is of the right order (1,909 region JSONs carry the key;
  2,596 exist).

**Cost of remediation.** `test_finemap_receipt_early_exit.py:558`, `finemap.smk:541` and
`deferred-items.md:365-366` are cheap comment/prose fixes. `run_susie_rss.R:1018-1019` is
**inside the re-frozen file**: correcting it needs a NEW named unfreeze (AUTH-K1-UNFREEZE is
SPENT) plus a fresh re-pin of `FROZEN_R_REV` and `FREEZE_REF` off `bf04199`. That is a
judgement call for the developer — the alternative is to leave the R comment as-is and
correct the three cheap sites, accepting a known-imprecise number in frozen source.

*Meta-note: the executor's own Lesson 2 is "when a number is going into a comment as
evidence, measure it twice by two methods." The number was measured twice by two methods
and still shipped at the wrong scope, because the second measurement changed the flag but
not the search root.*

---

## Behavioural spot-checks

| Behaviour | Command | Result | Status |
|---|---|---|---|
| Live decoder renders the post-K-1 Path-2 token | `eval` of the extracted `cause=(...)` on `(vcp=T, vcv=F, ozv=T)` | `path2_ld_overlap_zero_RETRY` | ✓ PASS |
| Pre-change decoder rendered the lie | same, over `git show 63453db:finemap.smk` | `none` | ✓ PASS |
| Renaming a token in `finemap.smk` turns the token test RED | in-memory rename + `_recovered_cause_tokens` | `RED` | ✓ PASS |
| Splicing the deleted line back turns the K-1 assertion RED | in-memory splice through the suite's own `_brace_block` | `RED` | ✓ PASS |
| `_brace_block` hard-fails on a missing anchor | bogus anchor | `AssertionError: anchor not found` | ✓ PASS |
| R file parses | `Rscript -e 'parse(...)'` | `PARSE_OK` | ✓ PASS |
| Snakemake DAG loads | `snakemake --list` on `config/pipeline.yaml` | `LIST_OK` | ✓ PASS |
| Forward freeze gate | `git diff --exit-code bf04199 -- run_susie_rss.R` | clean | ✓ PASS |
| Targeted modules | `pytest test_variant_catalog_fallback_legacy_semantics.py test_ld_read_path.py test_finemap_receipt_early_exit.py -q -rs` | **40 passed, 0 skipped** (11 + 8 + 21) | ✓ PASS |

Full `tests/m3` and `tests/phase2` runs were **deliberately not executed here** — the
orchestrator is running them independently in parallel, per the verification brief. The
SUMMARY's `822 / 31 / 0` and `136 / 1 / 0` are therefore **NOT** verified by this report;
the per-module collection counts I did measure (11 new + 21 receipt) are consistent with
the claimed `+15` reconciliation.

---

## Anti-patterns found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `run_susie_rss.R` | 1018-1019 | Mis-scoped factual claim in frozen source | ⚠️ Warning | Documentation only; requires a new unfreeze to correct |
| `finemap.smk` | 541 | Same number, contradicts `:538` in the same comment block | ⚠️ Warning | Documentation only |
| `test_finemap_receipt_early_exit.py` | 558 | Same number, in a comment | ℹ️ Info | No assertion depends on it |
| `deferred-items.md` | 365-366 | Same number, contradicts `:369` | ⚠️ Warning | Registry record |

No TODO / FIXME / placeholder / stub patterns found in the diff. No hardcoded empty returns.
No `console.log`-only or `return null` implementations. The three new/changed assertion
families each ship with a control that was demonstrated capable of failing.

---

## Gaps summary

The phase goal is achieved. `variant_catalog_fallback` has exactly one assignment site and
it is the Path-1 AFR empty-subset revert; the Path-2 branch's science is byte-unchanged; the
five MUST-NOT-MOVE regions are byte-identical; the strengthened assertion is demonstrably
capable of failing and is guarded against vacuity in three independent ways; the decoder
gained a truthful fifth outcome whose token set is recovered from live source and provably
RED on a rename; the freeze cascade is completely re-pinned at `bf04199` with every
surviving `dc4bbd2` correctly classified; scope is exactly the 8 planned files with no
orchestrator-owned doc written and the SUMMARY left uncommitted; and the `ld_allele_join.R`
extraction is deferred in writing with the fire-path-risk reasoning recorded verbatim.

The single gap is that the census correction — a claim the executor elevated to a material
deviation and then wrote into four shipped files including frozen R source — counts
repo-wide JSONs while calling them region JSONs. Correct region-scoped values are **1,909
carrying the key / 1,900 false / 9 true**, and those are what the co-shipped `687 of 2,596`
already implies. Every downstream conclusion drawn from the census is unaffected.

Also outstanding and correctly handed off by the executor (orchestrator-owned, not a gap in
this task): `.planning/STATE.md:55`, `.planning/HANDOFF.json:75/:111/:117`, and
`.planning/phases/m3-aou-afr-ld-panel-build/.continue-here.md:25` still assert `dc4bbd2` as
the live freeze and must move to `bf04199` in the docs commit.

---

_Verified: 2026-08-06_
_Verifier: Claude (gsd-verifier)_
