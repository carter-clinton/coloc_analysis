---
phase: quick/260806-sr4
plan: 01
subsystem: m3-source-freeze
tags: [freeze, provenance, test-infrastructure, m3, track-a, k-3]
baseline_rev: 1b5b8c6
commits:
  - 98e0ee9  # T1 -- the utility + its proof + the three Python gates
  - 656529a  # T2 -- K-3 closed, the R freeze rescoped bytes -> code
  - c04e672  # T3 -- DEC-2026-08-06-sr4-freeze-scope + K-3 closure + SR4-OPEN
  - 5f0520b  # follow-up -- stale constant count in one assertion message
requires: [bf04199, bf16289]
provides:
  - "tests/m3/source_freeze.py -- the reusable R+Python code-identity utility"
  - "tests/m3/test_source_freeze_pins.py -- the forward gate for every m3 source freeze"
  - "DEC-2026-08-06-sr4-freeze-scope -- the freeze convention, recorded for the first time"
affects:
  - "every future edit to run_susie_rss.R and the three pinned Python modules"
tech-stack:
  added: []
  patterns: ["length-preserving string mask + brace-walk-the-mask (R)", "ast canonicalisation (Python)", "keyword-only actual_text= control seam", "derived-not-transcribed symbol lists", "bucket-annotated revision constants"]
key-files:
  created:
    - tests/m3/source_freeze.py
    - tests/m3/test_source_freeze.py
    - tests/m3/test_source_freeze_pins.py
  modified:
    - src/legacy/region_analysis/scripts/run_susie_rss.R
    - tests/m3/test_finemap_receipt_early_exit.py
    - tests/m3/test_qtl_coloc_allele_join.py
    - .planning/DECISIONS.md
    - .planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md
    - "+9 tests/m3 modules, comment-only bucket annotations (see Deviations)"
decisions:
  - "The source freeze pins CODE, not bytes; comments/docstrings are deliberately free"
  - "The R code pin was NOT moved -- bf04199 remains valid across the K-3 comment fix"
  - "3 of 8 HANDOFF-declared-frozen files gated; 5 have MOVED and were deliberately not gated"
metrics:
  duration: "~3h"
  completed: 2026-08-06
  tests_m3: "902 passed / 31 skipped / 0 failed (baseline 822/31/0)"
  tests_phase2: "136 passed / 1 skipped / 0 failed"
  cost: "$0, NC State only, zero perimeter contact, AoU fire NOT triggered"
---

# quick/260806-sr4: Rescope the source freeze to a comment-insensitive code pin Summary

Replaced the whole-file **byte** freeze on `run_susie_rss.R` with a
string-literal-safe, comment-insensitive, symbol-scoped **CODE** pin built as one
reusable R+Python utility — and closed **K-3** in the same window as the proof
that the new mechanism permits it, **without moving the pin**.

---

## 1. THE ACCEPTANCE TABLE

| # | Clause | Verdict | Raw evidence |
|---|---|---|---|
| 1 | **K-3 landed** | ✅ **MET** | `run_susie_rss.R:1018-1019` now reads `1,909` / `1,900`. `grep -c "1,909\|1,900"` = **2**; `grep -c "1,944\|1,935"` = **0**. `Rscript -e 'parse(...)'` → `PARSE_OK`. Diff vs `bf04199` = **1 hunk, 2 `-`/`+` pairs, 4/4 lines comments, 0 non-comment lines** |
| 2 | **The comment edit was provably FREE** | ✅ **MET** | **NC-SR7's RED/GREEN pair on ONE tree** (§3). The pin **did not move**: `R_CODE_REF` is still `bf04199` |
| 3 | **A code change to a pinned symbol goes RED, naming the symbol** | ✅ **MET — OBSERVED** | NC-SR2 (5 symbols, permanent) + NC-SR8 raw output in §3 |
| 4 | **A change concealed behind `#` inside a string goes RED, and the naive stripper is blind to it** | ✅ **MET — OBSERVED BOTH WAYS, BOTH LANGUAGES** | NC-SR3, permanent and in-suite (§3) |
| 5 | **Both suites at baseline-or-better, skips 31 and 1** | ✅ **MET** | `tests/m3` **902 passed / 31 skipped / 0 failed**; `tests/phase2` **136 / 1 / 0** |
| 6 | **`DECISIONS.md` records the convention** | ✅ **MET** | `DEC-2026-08-06-sr4-freeze-scope`, append-only (0 deleted lines) |

---

## 2. ⚠ THE PLAN-FACT CORRECTION — `HANDOFF.json` IS WRONG ABOUT 5 OF 8 FILES

**`.planning/HANDOFF.json:14` claims *"All 7 pinned files 0-line diff vs
`bf16289`"*. That is FALSE for five of eight.** Re-measured at `1b5b8c6`; the
plan's table reproduced **exactly**.

| File | `git diff --numstat bf16289 HEAD` | Last touched | Handled |
|---|---|---|---|
| `src/python/plink_ld_to_npz.py` | **0** | 2026-07-03 | ✅ **GATED** |
| `src/python/condition_ld_matrix.py` | **0** | 2026-07-07 | ✅ **GATED** |
| `src/python/occlusion_span_filter.py` | **0** | 2026-07-15 | ✅ **GATED** |
| `src/python/occlusion_manifest.py` | **+46 / −8** | 2026-08-04 (`bf963df`) | ⚠ **MOVED — NOT gated** |
| `src/python/occlusion_present_rate_scan.py` | **+154 / −21** | 2026-08-04 (`fac9a93`) | ⚠ **MOVED — NOT gated** |
| `src/python/drop_occluded_from_sumstats.py` | **+97 / −24** | 2026-08-04 (`bf963df`) | ⚠ **MOVED — NOT gated** |
| `src/scripts/ld_npz_to_rds.R` | **+313 / −62** | 2026-08-05 (`57b381f`) | ⚠ **MOVED — NOT gated** |
| `src/snakemake/schemas/pipeline.schema.yaml` | **+119 / −0** | 2026-08-06 (`2563451`) | ⚠ **MOVED — NOT gated** |

**It is worse than it looked:** `bf16289` appeared **nowhere** in `src/`,
`tests/`, `config/`, `Snakefile` or `scripts/`. There was **literally zero
enforcement** of any of these — the "freeze" was a per-task hand check, and that
ritual had been reporting a claim false for five of eight files.

**3 gated, 5 deliberately not.** `AUTH-SR4-EXTEND` covers only measured-0-diff
files. Gating a file that changed three times in three days would manufacture the
exact nuisance-repin timebomb the rescope removes, and **declaring a moving file
frozen is a DECISION, not an inference.**
`test_the_handoff_frozen_claim_is_recorded_as_partly_false` asserts the five are
**out** of the pinned set — *and* asserts each still has a non-empty numstat — so
a future sweep cannot re-add them silently, and the finding cannot silently rot.

---

## 3. NEGATIVE CONTROLS — EVERY ONE OBSERVED RED, QUOTED RAW

**Permanent and in-suite** (no revert, cannot decay into a claim): NC-SR1, SR2,
SR3, SR4, SR9, SR10. **Observed once out-of-band:** NC-SR5, SR6, SR7, SR8.

### NC-SR7 — ⭐ THE HEADLINE. The rescope is what made the edit free.

Both run on the **same tree**, after the K-3 edit:

```
$ git diff --exit-code bf04199 -- src/legacy/region_analysis/scripts/run_susie_rss.R
@@ -1015,8 +1015,8 @@ repeat {
-    # meaning: every legacy region JSON on this node carries it (1,944 measured
-    # 2026-08-06 -- 1,935 false, and the 9 true ones are all AFR Path-1 reverts
+    # meaning: every legacy region JSON on this node carries it (1,909 measured
+    # 2026-08-06 -- 1,900 false, and the 9 true ones are all AFR Path-1 reverts
OLD BYTE GATE rc=1  <-- RED

$ pytest tests/m3/test_source_freeze_pins.py -k k3 -q
..                                                    [100%]
2 passed, 37 deselected in 0.18s      <-- GREEN
```

**That pair is acceptance items 1 and 2.** The old mechanism forbids the
correction; the new one permits it; the pin never moved.

### NC-SR8 — the rewired JOB A gate can still fail (the exact call `_assert_r_freeze_clean` makes)

```
the CODE of src/legacy/region_analysis/scripts/run_susie_rss.R (whole file) has MOVED off its pin bf04199.
Comments, docstrings, blank lines and trailing whitespace are ignored by this comparison, so this is a REAL code change.
first difference at code-line index 14:
  -   R_reg <- R + diag(eps, nrow(R))
  +   R_reg <- R + diag(eps * 2, nrow(R))
(reference: 818 code lines / actual: 818 code lines)
Two hypotheses, both to be checked: either the code moved, or the extractor is reading the wrong region.
RE-PIN PROTOCOL: on an AUTHORIZED code change update EXACTLY ONE constant -- R_CODE_REF in tests/m3/test_source_freeze_pins.py -- to the landing commit's SHA, and nothing else. A comment or docstring change updates NOTHING. See DEC-2026-08-06-sr4-freeze-scope.

working tree untouched: True
```

### NC-SR5 / NC-SR6 — the paired shape: same file, same helper, same seam, one RED one GREEN

```
=== NC-SR5 -- a CODE edit to plink_ld_to_npz.py, in memory ===
the CODE of src/python/plink_ld_to_npz.py (whole file) has MOVED off its pin bf16289.
first difference at code-line index 33:
  - def _bim_snp_index(bim_path: Path) -> dict[str, int]:
  + def _bim_snp_index_sr4(bim_path: Path) -> dict[str, int]:
(reference: 149 code lines / actual: 149 code lines)
RE-PIN PROTOCOL: ... update EXACTLY ONE constant -- PY_CODE_REF ...

=== NC-SR6 -- a COMMENT edit to the SAME file, same helper, same seam ===
NO RAISE (correct). comment perturbed: '# AF sidecar (mirror bm_to_npz._load_af_sidecar: blank line -> NaN, ne'
perturbed text differs from original: True
```

That pairing is what makes comment-insensitivity a **property**, not an assertion.

### NC-SR3 — ⚠ THE LOAD-BEARING CONTROL: concealment behind `#` inside a string

Measured, both languages, both halves:

```
R  naive blind: True | R  utility detects: True
PY naive blind: True | PY utility detects: True
```

The naive `re.sub(r"#.*$", "", line)` stripper sees **no difference** between the
carrier and the concealed edit; `source_freeze` sees it. Without the first half
this control would prove nothing about the hazard being real. **No live file has
a `#` inside an executable string literal (measured 0/0/0/0), so the fixture MUST
be synthetic** — a latent hazard with no control is how a guard rots.

### NC-SR4 — the whole-file floor catches what all five symbol pins miss

First the **gap** is proved: the top-level main body (`option_list <- list(` at
`:659` through EOF, >600 lines) is inside **none** of the five symbol spans, and
all three `toJSON` emits (`:938`, `:970`, `:1357`) are in it. Then perturbing the
`:1357` emit (`pretty = TRUE` → `pretty = FALSE`) is **RED on the whole-file
floor** while **all five symbol pins stay GREEN**. Mechanical proof that
symbol-pins-only would have had a ~700-line silent hole.

### NC-SR1 / NC-SR2 — a code edit is detected; inside a symbol it NAMES the symbol

Permanent, parametrized over all four files and all five R symbols. NC-SR2 drives
`pytest.raises(AssertionError, match=<symbol>)` — the **only** shape that
exercises the message path — and re-asserts the working tree is unwritten after
each control.

### NC-SR9 — the rewired JOB B leak check can still fail

Permanent in `test_source_freeze.py` (so no assertion count moved in a
pre-existing module). Both a leaked **code** line and a leaked **comment** raise;
the comment case is exactly why JOB B was **not** made comment-insensitive.

### NC-SR10 — the ACTUAL side is the working tree, not a committed read

Module-scope, evaluated with the plan's own stripper (a raw substring check would
be RED at birth, since the utility's docstring quotes the forbidden call). If the
actual side became a committed read, the mid-test leak gates at
`test_finemap_receipt_early_exit.py:341`/`:357` and NC-2g would go **blind with
nothing turning red**.

### The seam guard's own non-vacuity — a grep would not have worked

```
actual_text = forged (spaces)    grep('actual_text=') hit=False  AST walk offenders=['actual_text']
**{"actual_text": ...}           grep('actual_text=') hit=False  AST walk offenders=[None]
```

Both evasions verified; the AST walk catches both. The test additionally asserts
the walk resolved **≥1 real call**, so "no offenders" cannot pass for free.

### Two REDs observed during execution, both real, both fixed

- **The bucket gate fired RED on first run**, correctly naming all 13
  un-annotated revision constants. That is the gate proving it can fail.
- **The K-3 containment test fired RED on a genuine bug of mine**: `ln[:1] in "-+"`
  counts the trailing blank from `split("\n")`, because `"" in "-+"` is `True`.
  Fixed to `ln[:1] and ln[0] in "-+"`, with the trap noted in a comment.

---

## 4. THE MASK INVARIANTS — pinned SYNTHETICALLY, because no live file exercises either

| Variant | `code_lines` of `q <- "line1\nline2 trailing   \nend"` |
|---|---|
| production (`filler="_"`, `keep_newlines=True`) | `['q <- "line1', 'line2 trailing', 'end"']` |
| **(4a) violated** (`keep_newlines=False`) | `['q <- "line1']` — **two lines silently vanish** |
| **(4b) violated** (`filler=" "`) | `['q <- "', 'end"']` — trailing content lost to `rstrip()` |

Every value reproduces the plan's measurement exactly. ⚠ **`len(masked) == len(text)`
holds under BOTH variants** — the length invariant is **blind** to 4a, which is
precisely why the synthetic pin exists. On the real file both `keep_newlines`
settings give **818** code lines, so this bug is invisible on today's inputs.

**Two independent implementations agree, twice:** the hand-written Python scanner
vs `ast` (all three modules), and `source_freeze`'s R mask vs the pre-existing
`r_code_only` (four R inputs, including both NC-SR3 fixtures).

---

## 5. THE FREEZE PARAGRAPH

`src/legacy/region_analysis/scripts/run_susie_rss.R` is **CODE-frozen at
`bf04199`**. **The pin did NOT move.** `AUTH-SR4-RESCOPE` and `AUTH-SR4-K3` are
both **SPENT**. The forward gate is **`pytest tests/m3/test_source_freeze_pins.py`**.
Zero bare `FROZEN_R_REV` / `FREEZE_REF` survive; zero `git diff --exit-code` gates
on that file survive anywhere in `tests/`. The R code pin is spelled **exactly
once** (`R_CODE_REF`), imported by both consumers as `FROZEN_R_CODE_REV` and
`FREEZE_CODE_REF`.

### The SHA bucket classification — 16 constants, now enforced permanently

| Bucket | Count | Constants |
|---|---|---|
| **CODE PIN** (may move on an authorized code change) | 2 | `PY_CODE_REF` `bf16289`, `R_CODE_REF` `bf04199` |
| **DIFFERENTIAL SUBSTRATE** (never moves) | 14 | `K3_PRE_FIX_REF` `bf04199`; `PRE_K1_REF` `dc4bbd2`; `PRE_K1_SMK_REF` `63453db`; 8× `PRE_CHANGE_REF` (`6b427bc`×2, `0378ec8`×2, `5ec33bd`×2, `7b1025d`×2); `BASE_COMMIT` `5ec33bd`; `BASELINE_REV` `6b427bc`, `3f431ab` |
| **HISTORICAL NARRATIVE** | 0 | — (`dc4bbd2`/`7b1025d` narrative in prose, not bound to constants) |

Every one is classified **from its own existing wording**, none guessed. The
count was 17 pre-rescope; it is 16 now (`FROZEN_R_REV` and `FREEZE_REF` became
import aliases, `K3_PRE_FIX_REF` was added).

**The acceptance test survives a future re-pin**: clause (i) reads the live
`R_CODE_REF`; clauses (ii)/(iii) read `K3_PRE_FIX_REF`. The split is proven real
**today** by a control that hands the historical clauses the live text —
precisely what `git show <new-ref>` returns after a re-pin — and observes RED.
Without it the split would be fixed in prose and not in fact.

---

## 6. TRACK A DID NOT MOVE — ASSERTED, NOT ASSUMED

| Check | Result |
|---|---|
| `results/`, `src/python/`, `.planning/amendments/` paths in the diff | **0** |
| `TRACK-A-FROZEN-NUMBERS.md` vs `1b5b8c6` | **CLEAN** |
| `DECISIONS.md` deleted lines | **0** — strictly **APPEND-ONLY** |
| aggregator md5 `558fca45` count | **2** — unchanged from pre-edit |
| SH2B3 `.fit.rds` md5s `462ada6a` / `8255c1ac` / `a041eecc` | **2 / 2 / 2** — unchanged |
| the ten must-be-0-diff files | **all 0** |
| forbidden tokens (`gsutil\|gcloud\|bq\|dataproc\|hailctl\|nan_to_num\|wb`) | **0** |
| m3-06 HELD (`condition_ld_matrix.*=\|nan_to_num`) | **empty** |
| `sparse_parent_benchmark.tsv` | restored, **not committed** |

---

## 7. WHAT THIS DOES **NOT** COVER — limits, not coverage

- **No fit was run. No `.rds`, `.npz` or region JSON was produced or compared.
  No numeric behaviour was executed.** The pins are over **source text**. They
  detect *that code moved*, **never *whether a number moved***. The only oracle
  for the latter is the AoU perimeter and the ~11-day billed fire — which is the
  whole reason a source guard exists.
- **YAML support was deliberately NOT built.** `pipeline.schema.yaml` has moved
  since `bf16289` (+119), so there was nothing to gate; building the parser
  anyway would be coverage theatre.
- **5 of 8 HANDOFF-declared-frozen files are NOT gated** — registered as an open
  question for Carter, **not silently resolved either way**.
- **Three prose sites still narrate a byte freeze** — `finemap.smk:502`,
  `ld_allele_join.R:33`/`:99` — deliberately deferred on fire-path risk.
- **This re-aimed a *source* guard.** It did **not** verify any AFR number, did
  **not** close E-2, and did **not** touch the fire gate.

---

## 8. DEVIATIONS FROM THE PLAN — named, not absorbed

### D1 (SIGNIFICANT) — ⚠ THE PLAN'S "NO EXPECTED-RED WINDOW" CLAIM IS FALSE. There is exactly one, and the plan created it.

The plan and the orchestrator brief both state there is **no** expected-RED
window anywhere. **There is one**, produced by two plan mandates interacting:

- **T2 STEP 1** lands the K-3 edit **in the working tree**.
- **T2 STEP 4** adds a capture guard asserting `real == git_show("HEAD", SUSIE_R_REL)`.

Between those two and commit 2, the working tree necessarily differs from `HEAD`,
so **both capture guards fire**. Observed: **4 failed / 182 passed** on the
eight-module regression set, and the plan's own `<verify>` block runs that set
inside this window.

**Diagnosis was made exact before proceeding, not assumed:** 3 `ALTERATIONS` + 1
= exactly 4 NC-2g tests, exactly 4 failures; and the **only** working-tree-vs-`HEAD`
delta on that file was the two K-3 comment lines. After commit 2 the same command
returned **186 passed, 0 failed** — the 4 failures were entirely the artifact.

**The guard is correct and was NOT relaxed.** Relaxing it would be precisely the
coverage reduction hard rule 6 forbids. The resolution is **ordering**: commit 2
must land before that regression set is meaningful. Any executor following this
plan hits this; it should be written into the plan, not rediscovered.

### D2 — `files_modified` under-enumerates by 9 files, and the plan contradicts itself

T2 STEP 5 mandates a **repo-wide** `test_every_pin_constant_declares_its_bucket`
and explicitly authorizes the annotations ("comment-only — no assertion changes —
so it is inside AUTH-SR4-RESCOPE's re-pin-prose scope"), naming 11 constants
across 11 files. But the frontmatter `files_modified` lists only 8 paths, and T3
STEP 4 asserts the scope diff **equals it exactly**. Both cannot hold.

**Resolved toward the mandated gate** (it is explicitly authorized and mitigates
T-sr4-10; the frontmatter is bookkeeping the planner simply did not update).
**9 pre-existing modules gained comment-only annotations**; every one measured
**0 deleted lines and 0 non-comment lines added**. Actual scope = 17 files.
I also found **`PRE_K1_REF`**, which the plan's enumeration missed — 12 constants
needed annotation, not 11.

### D3 — the plan's `558fca45` instructions are mutually unsatisfiable

T3 STEP 1 says the entry must state it does not touch "the aggregator md5
`558fca45`"; T3 STEP 4 says `grep -c 558fca45` must be **unchanged**. Writing the
literal takes the count 2 → 3. **Resolved without weakening either**: the entry
names the lock by decision ID (`DEC-2026-05-03-vcl-Item2`) and explains that the
md5 literals are deliberately not restated, since a copy in a third entry is a
second source of truth waiting to drift. Count stays **2**; append-only stays **0**.

### D4 — `R_CODE_REF` had to be declared in T1, not T2

T1 STEP 3 says the pins module carries "only the Python pins", but T1 STEP 2's
NC-SR2/SR4/SR10 all call `assert_code_frozen(..., R_CODE_REF, ...)`. Declaring it
in T1 (with its **gates** landing in T2) is the only resolution preserving B5's
"declared exactly once". No constant was ever duplicated.

### D5 — clause (iii)'s wording is not literally satisfiable

"the raw diff mentions `1,909`/`1,900` **and not** `1,944`/`1,935`" cannot hold:
a diff shows both sides. Implemented as the strongest satisfiable reading — the
**live file** contains `1,909`/`1,900` and not `1,944`/`1,935`, and the
**substrate** the converse — which is unambiguous and a genuine historical fact.

### D6 — the mask-vs-`ast` cross-check needed a lookbehind

Bare `[A-Za-z_]\w*` tokenises the `e` of `1e-4` as an identifier while
`ast.unparse` normalises the literal to `0.0001`, producing a **2-token false
disagreement** in `plink_ld_to_npz.py` — a number-formatting artifact
masquerading as a stripper bug. Closed with `(?<![A-Za-z_0-9])`. All three
modules then agree. The comparison currency (non-keyword identifier multiset with
string literals collapsed) is documented, including what it does and does not
cover.

### D7 — a 4th commit

`5f0520b` corrects a stale constant count (17 → 16) in one assertion **message**.
Message-only; the `>= 15` floor and every assertion unchanged.

### D8 — `deferred-items.md`: 3 sites annotated, not 4

The plan's 4th site (`:633`) lives **inside** the K-3 entry that STEP 2 requires
be "preserved in full". Annotating in place would alter the preserved record.
The closure header directly supersedes that exact sentence instead
("the remedy... now requires NEITHER").

### D9 — TDD structure

T1/T2 are `tdd="true"`, but the plan mandates exactly 3 commits with named
subjects. Kept the 3-commit structure; the substantive TDD requirement (hard rule
1 — every assertion ships with an observed-RED control) is fully met, including
two genuine unplanned REDs (§3).

---

## 9. THINGS THE PLAN DID NOT ANTICIPATE

1. **D1 — the capture guard makes the working tree red for the duration of an
   uncommitted comment fix.** The strongest lesson here: *a guard that compares
   the working tree to `HEAD` is in tension with any workflow that edits before
   committing.* It is the right guard; the plan's task ordering just has to
   respect it.
2. **`""` is a substring of every string.** `ln[:1] in "-+"` silently counted a
   blank line and broke a containment assertion. Caught only because the
   assertion was written to fail loudly on a count mismatch.
3. **`PRE_K1_REF` was already correctly annotated but wrapped across two `#:`
   lines**, so a naive block scan missed it. The scan normalises whitespace
   before matching — otherwise a *correctly*-annotated constant is flagged, and
   the fix would have been to damage the annotation.
4. **The five R symbols are the *complete* set of top-level R functions** in
   `run_susie_rss.R` (measured). Nothing is outside a symbol *except* the
   ~700-line main body — which makes the floor even more load-bearing than the
   plan argued.
5. **`ast.unparse` normalises numeric literals**, which can fake a stripper
   disagreement (D6).

---

## 10. HANDOFF FOR THE ORCHESTRATOR — the executor wrote NONE of these

Per hard rule 12, `.planning/STATE.md`, `.planning/HANDOFF.json`,
`.continue-here.md` and `ROADMAP.md` were **not written**. Outstanding:

1. **`HANDOFF.json:14` carries the FALSE "All 7 pinned files 0-line diff vs
   bf16289" claim** — false for 5 of 8 (§2). It should be corrected.
2. **`HANDOFF.json:118`'s `freeze_state` describes a BYTE gate that no longer
   exists.** The forward gate is `pytest tests/m3/test_source_freeze_pins.py`.
3. **`HANDOFF.json:76` says K-3 is "REGISTERED BUT NOT A LICENCE"** — K-3 is now
   **CLOSED** (`656529a`).
4. **Three deferred prose sites still narrate a byte freeze**:
   `src/snakemake/rules/finemap.smk:502`,
   `src/snakemake/scripts/ld_allele_join.R:33` and `:99`. Deliberately not edited
   (live fire-path files; `DEC-2026-08-06-sr4-freeze-scope` is the canonical
   record and is cross-referenced from both rewired test modules).
   ⚠ `test_finemap_receipt_early_exit.py:568` and `finemap.smk:547`
   ("unreachable from any tree at or after `bf04199`") are **correct historical
   claims about the K-1 window** and were deliberately **left alone**.
5. **`.planning/STATE.md`** needs the quick-task row.

### THE OPEN QUESTION FOR CARTER (verbatim from `deferred-items.md`)

> For each of the five: were they **frozen and have since drifted** (in which
> case something was changed that should not have been, and the drift needs
> review), or were they **never actually frozen** (in which case
> `HANDOFF.json:14` should be corrected and they should stop being described as
> pinned)? These are different problems with different remedies, and choosing
> between them is a call about intent that no agent can make from the diff alone.

**Nothing is blocked on the answer.** The three real gates are live either way.

---

## 11. COST

**$0. NC State node only. Zero perimeter contact. The AoU fire was NOT
triggered** — no `gsutil` / `gcloud` / `bq` / `dataproc` / `hailctl` / `wb`
anywhere in the session or the diff (grep-verified over the full
`1b5b8c6..HEAD` diff).

---

## Self-Check: PASSED

- `tests/m3/source_freeze.py`, `tests/m3/test_source_freeze.py`,
  `tests/m3/test_source_freeze_pins.py` — all present.
- Commits `98e0ee9`, `656529a`, `c04e672`, `5f0520b` — all present in
  `git log --oneline`.
- `tests/m3` **902 / 31 / 0**, `tests/phase2` **136 / 1 / 0**, `snakemake --list`
  rc 0 on all four configs — all measured **after** the final commit.
- Working tree clean; `sparse_parent_benchmark.tsv` restored and uncommitted.
